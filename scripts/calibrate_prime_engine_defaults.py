from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
DEFAULT_EXTERNAL_SEGMENT_SWEEP = (
    RESULTS_DIR / "prime_engine_external_segment_sweep_latest.csv"
)
DEFAULT_EXTERNAL_SEGMENT_SWEEP_METADATA = (
    RESULTS_DIR / "prime_engine_external_segment_sweep_latest.json"
)
DEFAULT_EXTERNAL_MODE_SWEEP = RESULTS_DIR / "prime_engine_external_mode_sweep_latest.csv"
DEFAULT_EXTERNAL_MODE_SWEEP_METADATA = (
    RESULTS_DIR / "prime_engine_external_mode_sweep_latest.json"
)
DEFAULT_EXTERNAL_MODE_CONFIRMATION = (
    RESULTS_DIR / "prime_engine_external_mode_confirmation_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_QUICK = (
    RESULTS_DIR / "prime_engine_high_offset_quick_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_QUICK_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_quick_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_TIGHT = (
    RESULTS_DIR / "prime_engine_high_offset_tight_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_TIGHT_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_tight_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_CONFIRMATION = (
    RESULTS_DIR / "prime_engine_high_offset_confirmation_latest.json"
)
DEFAULT_TUNING = RESULTS_DIR / "prime_engine_tuning_latest.json"
DEFAULT_OUTPUT_JSON = RESULTS_DIR / "prime_engine_default_calibration_latest.json"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "prime_engine_default_calibration_latest.md"
DEFAULT_BASELINE_PRIORITY = (
    "external_primesieve_count_server,external_primesieve_count,external_primecount_pi_diff"
)
SAMPLE_NOISY_MAX_OVER_MEDIAN = 1.5
SAMPLE_ROBUST_NOISE_MIN_COUNT = 5
DEFAULT_MIN_ACTIONABLE_MEDIAN_DELTA_MS = 0.001


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Select measured Circle prime-engine default recommendations from "
            "external segment sweeps and tuner artifacts."
        )
    )
    parser.add_argument(
        "--external-segment-sweep",
        type=Path,
        default=DEFAULT_EXTERNAL_SEGMENT_SWEEP,
    )
    parser.add_argument(
        "--external-segment-sweep-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_SEGMENT_SWEEP_METADATA,
    )
    parser.add_argument(
        "--external-mode-sweep",
        type=Path,
        default=DEFAULT_EXTERNAL_MODE_SWEEP,
    )
    parser.add_argument(
        "--external-mode-sweep-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_MODE_SWEEP_METADATA,
    )
    parser.add_argument(
        "--external-mode-confirmation",
        type=Path,
        default=DEFAULT_EXTERNAL_MODE_CONFIRMATION,
    )
    parser.add_argument(
        "--external-high-offset-quick",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_QUICK,
    )
    parser.add_argument(
        "--external-high-offset-quick-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_QUICK_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-tight",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_TIGHT,
    )
    parser.add_argument(
        "--external-high-offset-tight-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_TIGHT_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-confirmation",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_CONFIRMATION,
    )
    parser.add_argument("--tuning", type=Path, default=DEFAULT_TUNING)
    parser.add_argument(
        "--circle-prime",
        type=Path,
        default=ROOT / "target" / "release" / "circle-prime",
        help="Release circle-prime CLI used to read current adaptive defaults.",
    )
    parser.add_argument(
        "--baseline-priority",
        default=DEFAULT_BASELINE_PRIORITY,
        help=(
            "Comma-separated external baselines to trust, in order, when "
            "multiple sweep baselines are present."
        ),
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.05,
        help="Allowed default median slowdown over the selected row.",
    )
    parser.add_argument(
        "--min-actionable-median-delta-ms",
        type=float,
        default=DEFAULT_MIN_ACTIONABLE_MEDIAN_DELTA_MS,
        help=(
            "Ignore ratio drift when the absolute median delta is this many "
            "milliseconds or less."
        ),
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit nonzero when current defaults are slower than tolerance or lack evidence.",
    )
    args = parser.parse_args()

    if args.tolerance < 0:
        parser.error("--tolerance must be nonnegative")
    if args.min_actionable_median_delta_ms < 0:
        parser.error("--min-actionable-median-delta-ms must be nonnegative")
    baseline_priority = split_csv(args.baseline_priority)
    if not baseline_priority:
        parser.error("--baseline-priority must include at least one baseline")

    external_rows = read_csv_optional(args.external_segment_sweep)
    external_metadata = read_json_optional(args.external_segment_sweep_metadata)
    external_sample_rows = read_sample_rows_from_metadata(external_metadata)
    external_mode_rows = read_csv_optional(args.external_mode_sweep)
    external_mode_metadata = read_json_optional(args.external_mode_sweep_metadata)
    external_mode_sample_rows = read_sample_rows_from_metadata(external_mode_metadata)
    external_mode_confirmation = read_json_optional(args.external_mode_confirmation)
    confirmation_rows, confirmation_sample_rows = read_external_mode_confirmation_input_rows(
        external_mode_confirmation
    )
    external_mode_rows.extend(confirmation_rows)
    external_mode_sample_rows.extend(confirmation_sample_rows)
    external_high_offset_rows = read_csv_optional(args.external_high_offset_quick)
    external_high_offset_metadata = read_json_optional(
        args.external_high_offset_quick_metadata
    )
    external_high_offset_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_metadata
    )
    external_high_offset_tight_rows = read_csv_optional(args.external_high_offset_tight)
    external_high_offset_tight_metadata = read_json_optional(
        args.external_high_offset_tight_metadata
    )
    external_high_offset_tight_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_tight_metadata
    )
    external_high_offset_confirmation = read_json_optional(
        args.external_high_offset_confirmation
    )
    (
        external_high_offset_confirmation_rows,
        external_high_offset_confirmation_sample_rows,
    ) = read_external_mode_confirmation_input_rows(external_high_offset_confirmation)
    tuning_summary = read_json_optional(args.tuning)
    tuning_sample_rows = read_tuning_sample_rows(args.tuning, tuning_summary)
    recommendations = select_recommendations(
        external_rows=external_rows,
        external_sample_rows=external_sample_rows,
        external_mode_rows=external_mode_rows,
        external_mode_sample_rows=external_mode_sample_rows,
        external_mode_confirmation=external_mode_confirmation,
        external_high_offset_rows=external_high_offset_rows,
        external_high_offset_sample_rows=external_high_offset_sample_rows,
        external_high_offset_tight_rows=external_high_offset_tight_rows,
        external_high_offset_tight_sample_rows=external_high_offset_tight_sample_rows,
        external_high_offset_confirmation_rows=external_high_offset_confirmation_rows,
        external_high_offset_confirmation_sample_rows=external_high_offset_confirmation_sample_rows,
        external_high_offset_confirmation=external_high_offset_confirmation,
        tuning_summary=tuning_summary,
        tuning_sample_rows=tuning_sample_rows,
        baseline_priority=baseline_priority,
    )
    current_defaults = read_current_defaults(args.circle_prime, recommendations)
    calibration = build_calibration(
        recommendations=recommendations,
        current_defaults=current_defaults,
        external_metadata=external_metadata,
        external_mode_metadata=external_mode_metadata,
        external_mode_confirmation=external_mode_confirmation,
        external_high_offset_metadata=external_high_offset_metadata,
        external_high_offset_tight_metadata=external_high_offset_tight_metadata,
        external_high_offset_confirmation=external_high_offset_confirmation,
        tuning_summary=tuning_summary,
        baseline_priority=baseline_priority,
        tolerance=args.tolerance,
        min_actionable_median_delta_ms=args.min_actionable_median_delta_ms,
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        inputs={
            "external_segment_sweep": str(args.external_segment_sweep),
            "external_segment_sweep_metadata": str(args.external_segment_sweep_metadata),
            "external_mode_sweep": str(args.external_mode_sweep),
            "external_mode_sweep_metadata": str(args.external_mode_sweep_metadata),
            "external_mode_confirmation": str(args.external_mode_confirmation),
            "external_high_offset_quick": str(args.external_high_offset_quick),
            "external_high_offset_quick_metadata": str(
                args.external_high_offset_quick_metadata
            ),
            "external_high_offset_tight": str(args.external_high_offset_tight),
            "external_high_offset_tight_metadata": str(
                args.external_high_offset_tight_metadata
            ),
            "external_high_offset_confirmation": str(
                args.external_high_offset_confirmation
            ),
            "tuning": str(args.tuning),
            "circle_prime": str(args.circle_prime),
        },
    )

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(calibration, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(calibration))
    print(f"wrote prime-engine default calibration JSON: {args.output_json}")
    print(f"wrote prime-engine default calibration report: {args.output_md}")

    if args.fail_on_drift and calibration["failing_recommendation_count"] > 0:
        return 1
    return 0


def select_recommendations(
    *,
    external_rows: list[dict[str, str]],
    external_sample_rows: list[dict[str, str]] | None = None,
    external_mode_rows: list[dict[str, str]] | None = None,
    external_mode_sample_rows: list[dict[str, str]] | None = None,
    external_mode_confirmation: dict[str, Any] | None = None,
    external_high_offset_rows: list[dict[str, str]] | None = None,
    external_high_offset_sample_rows: list[dict[str, str]] | None = None,
    external_high_offset_tight_rows: list[dict[str, str]] | None = None,
    external_high_offset_tight_sample_rows: list[dict[str, str]] | None = None,
    external_high_offset_confirmation_rows: list[dict[str, str]] | None = None,
    external_high_offset_confirmation_sample_rows: list[dict[str, str]] | None = None,
    external_high_offset_confirmation: dict[str, Any] | None = None,
    tuning_summary: dict[str, Any] | None,
    tuning_sample_rows: list[dict[str, str]] | None = None,
    baseline_priority: list[str],
) -> list[dict[str, Any]]:
    high_offset_confirmation_recommendations = apply_mode_confirmation(
        select_external_recommendations(
            [
                (
                    "external_high_offset_confirmation",
                    external_high_offset_confirmation_rows or [],
                    external_high_offset_confirmation_sample_rows or [],
                )
            ],
            baseline_priority,
        ),
        external_high_offset_confirmation,
        selected_by="confirmed_external_high_offset",
    )
    confirmed_high_offset_confirmation_recommendations = [
        row
        for row in high_offset_confirmation_recommendations
        if row.get("mode_confirmation_status") == "confirmed"
    ]
    confirmed_high_offset_confirmation_ranges = {
        (row["low"], row["high"], row["baseline"])
        for row in confirmed_high_offset_confirmation_recommendations
    }
    high_offset_tight_recommendations = select_external_recommendations(
        [
            (
                "external_high_offset_tight",
                external_high_offset_tight_rows or [],
                external_high_offset_tight_sample_rows or [],
            )
        ],
        baseline_priority,
    )
    tight_ranges = {
        (row["low"], row["high"], row["baseline"])
        for row in high_offset_tight_recommendations
    }
    high_offset_quick_recommendations = select_external_recommendations(
        [
            (
                "external_high_offset_quick",
                external_high_offset_rows or [],
                external_high_offset_sample_rows or [],
            )
        ],
        baseline_priority,
    )
    high_offset_recommendations = apply_mode_confirmation(
        confirmed_high_offset_confirmation_recommendations
        + [
            row
            for row in high_offset_tight_recommendations
            if (row["low"], row["high"], row["baseline"])
            not in confirmed_high_offset_confirmation_ranges
        ]
        + [
            row
            for row in high_offset_quick_recommendations
            if (row["low"], row["high"], row["baseline"])
            not in confirmed_high_offset_confirmation_ranges
            and (row["low"], row["high"], row["baseline"]) not in tight_ranges
        ],
        external_high_offset_confirmation,
        selected_by="confirmed_external_high_offset",
    )
    mode_recommendations = apply_mode_confirmation(
        select_external_recommendations(
            [("external_mode_sweep", external_mode_rows or [], external_mode_sample_rows or [])],
            baseline_priority,
        ),
        external_mode_confirmation,
    )
    high_offset_ranges = {(row["low"], row["high"]) for row in high_offset_recommendations}
    segment_recommendations = select_external_recommendations(
        [("external_segment_sweep", external_rows, external_sample_rows or [])],
        baseline_priority,
    )
    recommendations = high_offset_recommendations + [
        row
        for row in mode_recommendations
        if (row["low"], row["high"]) not in high_offset_ranges
    ]
    covered_external_ranges = {(row["low"], row["high"]) for row in recommendations}
    recommendations.extend(
        [
            row
            for row in segment_recommendations
            if (row["low"], row["high"]) not in covered_external_ranges
        ]
    )
    covered_ranges = {(row["low"], row["high"]) for row in recommendations}
    for row in select_tuning_recommendations(tuning_summary, tuning_sample_rows):
        if (row["low"], row["high"]) not in covered_ranges:
            recommendations.append(row)
    return sorted(recommendations, key=lambda row: (row["low"], row["high"]))


def select_external_recommendations(
    inputs: list[tuple[str, list[dict[str, str]], list[dict[str, str]]]],
    baseline_priority: list[str],
) -> list[dict[str, Any]]:
    speedups = []
    for source, rows, sample_rows in inputs:
        timing_rows = [row for row in rows if row.get("kind") == "timing"]
        sample_stats = summarize_sample_rows(sample_rows)
        speedups.extend(
            external_speedup_summary(row, timing_rows, sample_stats, source)
            for row in rows
            if row.get("kind") == "speedup"
        )
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in speedups:
        grouped.setdefault((row["low"], row["high"], row["baseline"]), []).append(row)

    ranges = sorted({(row["low"], row["high"]) for row in speedups})
    recommendations = []
    for low, high in ranges:
        chosen_baseline = next(
            (
                baseline
                for baseline in baseline_priority
                if (low, high, baseline) in grouped
            ),
            None,
        )
        if chosen_baseline is None:
            continue
        candidates = sorted(
            grouped[(low, high, chosen_baseline)],
            key=lambda row: (
                row["median_ms"],
                row["best_ms"],
                row["segment_size"],
                row["threads"],
                row["count_mode"],
                row["source"],
            ),
        )
        selected = dict(candidates[0])
        selected.update(
            {
                "candidate_count": len(candidates),
                "candidates": candidates,
                "selected_by": "median_ms",
            }
        )
        recommendations.append(selected)
    return recommendations


def apply_mode_confirmation(
    recommendations: list[dict[str, Any]],
    confirmation: dict[str, Any] | None,
    *,
    selected_by: str = "confirmed_external_mode",
) -> list[dict[str, Any]]:
    if confirmation is None:
        return recommendations

    winners = {
        (int(row["low"]), int(row["high"]), str(row["baseline"])): row
        for row in confirmation.get("winners", [])
    }
    adjusted = []
    for recommendation in recommendations:
        winner = winners.get(
            (
                int(recommendation["low"]),
                int(recommendation["high"]),
                str(recommendation.get("baseline")),
            )
        )
        if winner is None:
            selected = dict(recommendation)
            selected.update(mode_confirmation_fields(None, confirmation))
            adjusted.append(selected)
            continue

        confirmed_candidate = None
        if winner.get("status") == "confirmed":
            confirmed_candidate = find_matching_mode_candidate(
                recommendation.get("candidates", []),
                winner,
            )
        if confirmed_candidate is not None:
            selected = dict(confirmed_candidate)
            selected.update(
                {
                    "candidate_count": int(recommendation.get("candidate_count", 0)),
                    "candidates": recommendation.get("candidates", []),
                    "selected_by": selected_by,
                }
            )
            selected.update(mode_confirmation_fields(winner, confirmation))
            adjusted.append(selected)
            continue

        selected = dict(recommendation)
        selected.update(mode_confirmation_fields(winner, confirmation))
        adjusted.append(selected)
    return adjusted


def find_matching_mode_candidate(
    candidates: list[dict[str, Any]],
    winner: dict[str, Any],
) -> dict[str, Any] | None:
    for candidate in candidates:
        if (
            str(candidate.get("count_mode", "segmented")) == str(winner["count_mode"])
            and int(candidate["segment_size"]) == int(winner["segment_size"])
            and int(candidate["threads"]) == int(winner["threads"])
            and int(candidate["requested_threads"]) == int(winner["requested_threads"])
        ):
            return candidate
    return None


def mode_confirmation_fields(
    winner: dict[str, Any] | None,
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    fields = {
        "mode_confirmation_available": True,
        "mode_confirmation_min_confirmations": confirmation.get("min_confirmations"),
        "mode_confirmation_requires_stable_samples": confirmation.get(
            "require_stable_samples"
        ),
    }
    if winner is None:
        fields.update(
            {
                "mode_confirmation_status": "missing",
                "mode_confirmation_count": 0,
                "mode_confirmation_observed_count": 0,
                "mode_confirmation_stable_observed_count": 0,
            }
        )
        return fields
    fields.update(
        {
            "mode_confirmation_status": winner.get("status"),
            "mode_confirmation_count": int(winner.get("confirmation_count", 0)),
            "mode_confirmation_observed_count": int(winner.get("observed_count", 0)),
            "mode_confirmation_stable_observed_count": int(
                winner.get("stable_observed_count", 0)
            ),
            "mode_confirmation_count_mode": winner.get("count_mode"),
            "mode_confirmation_segment_size": winner.get("segment_size"),
            "mode_confirmation_threads": winner.get("threads"),
            "mode_confirmation_requested_threads": winner.get("requested_threads"),
        }
    )
    return fields


def select_tuning_recommendations(
    summary: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    if summary is None:
        return []
    recommendations = []
    candidates_by_range = tuning_candidates_by_range(sample_rows or [])
    for row in summary.get("best_by_range", []):
        best = row.get("best", {})
        low = int(row["low"])
        high = int(row["high"])
        candidates = candidates_by_range.get((low, high), [])
        recommendations.append(
            {
                "source": "tuning",
                "baseline": None,
                "low": low,
                "high": high,
                "span": int(row["span"]),
                "count_mode": str(best.get("count_mode", "segmented")),
                "segment_size": int(best["segment_size"]),
                "threads": int(best["threads"]),
                "requested_threads": int(best["requested_threads"]),
                "best_ms": float(best["best_ms"]),
                "median_ms": float(best.get("median_ms", best["best_ms"])),
                "circle_speedup": None,
                "median_circle_speedup": None,
                "candidate_count": len(candidates) or int(row.get("samples", 0)),
                "candidates": candidates,
                "selected_by": "median_ms",
            }
        )
    return recommendations


def tuning_candidates_by_range(
    rows: list[dict[str, str]],
) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("kind") != "tuning":
            continue
        low = int(row["low"])
        high = int(row["high"])
        candidate = {
            "low": low,
            "high": high,
            "span": int(row["span"]),
            "source": "tuning",
            "count_mode": row.get("count_mode") or "segmented",
            "segment_size": int(row["segment_size"]),
            "threads": int(row["threads"]),
            "requested_threads": int(row.get("requested_threads") or row["threads"]),
            "best_ms": float(row["best_ms"]),
            "median_ms": float(row.get("median_ms") or row["best_ms"]),
        }
        grouped.setdefault((low, high), []).append(candidate)
    for candidates in grouped.values():
        candidates.sort(
            key=lambda row: (
                row["median_ms"],
                row["best_ms"],
                row["segment_size"],
                row["threads"],
                row["requested_threads"],
                row["count_mode"],
            )
        )
    return grouped


def build_calibration(
    *,
    recommendations: list[dict[str, Any]],
    current_defaults: dict[tuple[int, int, int], dict[str, Any]],
    external_metadata: dict[str, Any] | None,
    tuning_summary: dict[str, Any] | None,
    baseline_priority: list[str],
    tolerance: float,
    min_actionable_median_delta_ms: float = DEFAULT_MIN_ACTIONABLE_MEDIAN_DELTA_MS,
    generated_at_utc: str,
    inputs: dict[str, str],
    external_mode_metadata: dict[str, Any] | None = None,
    external_mode_confirmation: dict[str, Any] | None = None,
    external_high_offset_metadata: dict[str, Any] | None = None,
    external_high_offset_tight_metadata: dict[str, Any] | None = None,
    external_high_offset_confirmation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    calibrated = []
    for recommendation in recommendations:
        calibrated.append(
            calibrate_recommendation(
                recommendation,
                current_defaults.get(
                    (
                        int(recommendation["low"]),
                        int(recommendation["high"]),
                        int(recommendation["requested_threads"]),
                    )
                ),
                tolerance,
                min_actionable_median_delta_ms,
            )
        )
    failing = [row for row in calibrated if not row["passes"]]
    return {
        "generated_at_utc": generated_at_utc,
        "inputs": inputs,
        "baseline_priority": baseline_priority,
        "tolerance": tolerance,
        "min_actionable_median_delta_ms": min_actionable_median_delta_ms,
        "external_sweep": summarize_external_sweep_metadata(external_metadata),
        "external_mode_sweep": summarize_external_sweep_metadata(external_mode_metadata),
        "external_mode_confirmation": summarize_external_mode_confirmation(
            external_mode_confirmation
        ),
        "external_high_offset_quick": summarize_external_sweep_metadata(
            external_high_offset_metadata
        ),
        "external_high_offset_tight": summarize_external_sweep_metadata(
            external_high_offset_tight_metadata
        ),
        "external_high_offset_confirmation": summarize_external_mode_confirmation(
            external_high_offset_confirmation
        ),
        "tuning": summarize_tuning_metadata(tuning_summary),
        "recommendations": calibrated,
        "recommendation_count": len(calibrated),
        "aligned_count": sum(1 for row in calibrated if row["status"] == "aligned"),
        "within_tolerance_count": sum(
            1 for row in calibrated if row["status"] == "within_tolerance"
        ),
        "drift_count": sum(1 for row in calibrated if row["status"] == "drift"),
        "noisy_drift_count": sum(
            1 for row in calibrated if row["status"] == "noisy_drift"
        ),
        "unconfirmed_mode_drift_count": sum(
            1 for row in calibrated if row["status"] == "unconfirmed_mode_drift"
        ),
        "missing_evidence_count": sum(
            1 for row in calibrated if row["status"] in {"missing_default_evidence", "no_current_default"}
        ),
        "failing_recommendation_count": len(failing),
    }


def calibrate_recommendation(
    recommendation: dict[str, Any],
    current_default: dict[str, Any] | None,
    tolerance: float,
    min_actionable_median_delta_ms: float = DEFAULT_MIN_ACTIONABLE_MEDIAN_DELTA_MS,
) -> dict[str, Any]:
    row = {
        "source": recommendation["source"],
        "baseline": recommendation.get("baseline"),
        "low": int(recommendation["low"]),
        "high": int(recommendation["high"]),
        "span": int(recommendation["span"]),
        "selected_segment_size": int(recommendation["segment_size"]),
        "selected_count_mode": str(recommendation.get("count_mode", "segmented")),
        "selected_threads": int(recommendation["threads"]),
        "selected_requested_threads": int(recommendation["requested_threads"]),
        "selected_best_ms": float(recommendation["best_ms"]),
        "selected_median_ms": float(recommendation["median_ms"]),
        "selected_best_speedup": recommendation.get("circle_speedup"),
        "selected_median_speedup": recommendation.get("median_circle_speedup"),
        "selected_sample_stability": recommendation.get("sample_stability"),
        "selected_circle_sample": recommendation.get("circle_sample"),
        "selected_baseline_sample": recommendation.get("baseline_sample"),
        "selected_mode_confirmation_status": recommendation.get(
            "mode_confirmation_status"
        ),
        "selected_mode_confirmation_count": recommendation.get(
            "mode_confirmation_count"
        ),
        "selected_mode_confirmation_min": recommendation.get(
            "mode_confirmation_min_confirmations"
        ),
        "selected_mode_confirmation_requires_stable_samples": recommendation.get(
            "mode_confirmation_requires_stable_samples"
        ),
        "selected_mode_confirmation_observed_count": recommendation.get(
            "mode_confirmation_observed_count"
        ),
        "selected_mode_confirmation_stable_observed_count": recommendation.get(
            "mode_confirmation_stable_observed_count"
        ),
        "selected_by": recommendation.get("selected_by", "median_ms"),
        "candidate_count": int(recommendation.get("candidate_count", 0)),
    }
    row["selected_effective_sample_stability"] = effective_sample_stability(row)
    if current_default is None:
        row.update(
            {
                "current_default_count_mode": None,
                "current_default_segment_size": None,
                "current_default_threads": None,
                "current_default_requested_threads": None,
                "default_best_ms": None,
                "default_median_ms": None,
                "default_over_selected": None,
                "count_mode_aligned": False,
                "segment_size_aligned": False,
                "threads_aligned": False,
                "status": "no_current_default",
                "passes": False,
            }
        )
        return row

    default_count_mode = str(current_default.get("count_mode", "segmented"))
    default_segment_size = int(current_default["segment_size"])
    default_threads = int(current_default["threads"])
    default_requested_threads = int(current_default["requested_threads"])
    default_candidate = find_default_candidate(
        recommendation.get("candidates", []),
        default_count_mode,
        default_segment_size,
        default_threads,
        default_requested_threads,
    )
    count_mode_aligned = default_count_mode == row["selected_count_mode"]
    segment_aligned = default_segment_size == row["selected_segment_size"]
    threads_aligned = default_threads == row["selected_threads"]
    row.update(
        {
            "current_default_count_mode": default_count_mode,
            "current_default_segment_size": default_segment_size,
            "current_default_threads": default_threads,
            "current_default_requested_threads": default_requested_threads,
            "count_mode_aligned": count_mode_aligned,
            "segment_size_aligned": segment_aligned,
            "threads_aligned": threads_aligned,
        }
    )
    if count_mode_aligned and segment_aligned and threads_aligned:
        row.update(
            {
                "default_best_ms": row["selected_best_ms"],
                "default_median_ms": row["selected_median_ms"],
                "default_over_selected": 1.0,
                "status": "aligned",
                "passes": True,
            }
        )
        return row
    if default_candidate is None:
        row.update(
            {
                "default_best_ms": None,
                "default_median_ms": None,
                "default_over_selected": None,
                "status": "missing_default_evidence",
                "passes": False,
            }
        )
        return row

    default_median = float(default_candidate["median_ms"])
    ratio = default_median / row["selected_median_ms"]
    median_delta_ms = default_median - row["selected_median_ms"]
    within_tolerance = (
        ratio <= 1.0 + tolerance
        or median_delta_ms <= min_actionable_median_delta_ms
    )
    noisy_external_drift = (
        not within_tolerance
        and str(row["source"]).startswith("external_")
        and row.get("selected_effective_sample_stability") == "noisy"
    )
    unconfirmed_mode_drift = (
        not within_tolerance
        and row["source"]
        in {
            "external_mode_sweep",
            "external_high_offset_quick",
            "external_high_offset_tight",
            "external_high_offset_confirmation",
        }
        and row.get("selected_mode_confirmation_status") not in (None, "confirmed")
    )
    row.update(
        {
            "default_best_ms": float(default_candidate["best_ms"]),
            "default_median_ms": default_median,
            "default_minus_selected_median_ms": median_delta_ms,
            "default_over_selected": ratio,
            "status": (
                "within_tolerance"
                if within_tolerance
                else "unconfirmed_mode_drift"
                if unconfirmed_mode_drift
                else "noisy_drift"
                if noisy_external_drift
                else "drift"
            ),
            "passes": within_tolerance or noisy_external_drift or unconfirmed_mode_drift,
        }
    )
    return row


def effective_sample_stability(row: dict[str, Any]) -> str | None:
    raw_stability = row.get("selected_sample_stability")
    if (
        raw_stability == "noisy"
        and row.get("selected_mode_confirmation_status") == "confirmed"
        and row.get("selected_mode_confirmation_requires_stable_samples") is True
        and row.get("selected_mode_confirmation_stable_observed_count") is not None
        and row.get("selected_mode_confirmation_min") is not None
        and int(row["selected_mode_confirmation_stable_observed_count"])
        >= int(row["selected_mode_confirmation_min"])
    ):
        return "stable"
    return raw_stability


def find_default_candidate(
    candidates: list[dict[str, Any]],
    count_mode: str,
    segment_size: int,
    threads: int,
    requested_threads: int | None = None,
) -> dict[str, Any] | None:
    for candidate in candidates:
        if (
            str(candidate.get("count_mode", "segmented")) == count_mode
            and int(candidate["segment_size"]) == segment_size
            and int(candidate["threads"]) == threads
            and (
                requested_threads is None
                or "requested_threads" not in candidate
                or int(candidate["requested_threads"]) == requested_threads
            )
        ):
            return candidate
    return None


def read_current_defaults(
    binary: Path,
    recommendations: list[dict[str, Any]],
) -> dict[tuple[int, int, int], dict[str, Any]]:
    if not recommendations:
        return {}
    if not binary.exists():
        raise FileNotFoundError(
            f"circle-prime CLI not found at {binary}; build it with "
            "`cargo build --release -p circle-prime --bin circle-prime`"
        )
    defaults = {}
    for row in recommendations:
        key = (int(row["low"]), int(row["high"]), int(row["requested_threads"]))
        if key not in defaults:
            defaults[key] = recommend_count_default(binary, *key)
    return defaults


def recommend_count_default(
    binary: Path,
    low: int,
    high: int,
    requested_threads: int,
) -> dict[str, Any]:
    completed = subprocess.run(
        [
            str(binary),
            "recommend",
            str(low),
            str(high),
            "--count",
            "--json",
            "--threads",
            str(requested_threads),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def external_speedup_summary(
    row: dict[str, str],
    timing_rows: list[dict[str, str]] | None = None,
    sample_stats: dict[tuple[int, int, str, int, int | None, int | None], dict[str, Any]] | None = None,
    source: str = "external_segment_sweep",
) -> dict[str, Any]:
    best_speedup = float(row["best_speedup"])
    median_speedup = float(row.get("median_speedup") or best_speedup)
    baseline_row = matching_timing_row(row, timing_rows or [], row["baseline"])
    circle_sample = sample_stats_for_speedup(row, sample_stats)
    baseline_sample = (
        sample_stats_for_timing(baseline_row, sample_stats)
        if baseline_row is not None
        else None
    )
    return {
        "low": int(row["low"]),
        "high": int(row["high"]),
        "span": int(row["span"]),
        "source": source,
        "baseline": row["baseline"],
        "count_mode": row.get("count_mode") or count_mode_from_circle_name(row["name"]),
        "segment_size": int(row["segment_size"]),
        "threads": int(row["threads"]),
        "requested_threads": int(row["requested_threads"]),
        "best_ms": float(row["best_ms"]),
        "median_ms": float(row.get("median_ms") or row["best_ms"]),
        "circle_speedup": best_speedup,
        "median_circle_speedup": median_speedup,
        "circle_sample": circle_sample,
        "baseline_sample": baseline_sample,
        "sample_stability": combined_sample_stability(circle_sample, baseline_sample),
    }


def count_mode_from_circle_name(name: str) -> str:
    if "prefix_pi" in name:
        return "prefix-pi"
    if "hybrid_wheel30_mark" in name:
        return "hybrid-wheel30-mark"
    if "wheel30_mark" in name:
        return "wheel30-mark"
    if "presieve13" in name:
        return "presieve13"
    if "presieve17" in name:
        return "presieve17"
    if "dynamic" in name:
        return "dynamic"
    if "balanced" in name:
        return "balanced"
    return "segmented"


def matching_timing_row(
    speedup_row: dict[str, str],
    timing_rows: list[dict[str, str]],
    name: str,
) -> dict[str, str] | None:
    for row in timing_rows:
        if (
            row.get("name") == name
            and row.get("low") == speedup_row.get("low")
            and row.get("high") == speedup_row.get("high")
            and row.get("result") == speedup_row.get("result")
        ):
            return row
    return None


def summarize_sample_rows(
    rows: list[dict[str, str]],
) -> dict[tuple[int, int, str, int, int | None, int | None], dict[str, Any]]:
    grouped: dict[tuple[int, int, str, int, int | None, int | None], list[float]] = {}
    for row in rows:
        if row.get("kind") != "sample":
            continue
        key = (
            int(row["low"]),
            int(row["high"]),
            row["name"],
            int(row["segment_size"]),
            parse_optional_int(row.get("threads")),
            parse_optional_int(row.get("requested_threads")),
        )
        grouped.setdefault(key, []).append(float(row["elapsed_ms"]))
    return {key: sample_stats(values) for key, values in grouped.items()}


def sample_stats(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    median_ms = median_float(ordered)
    min_ms = ordered[0]
    max_ms = ordered[-1]
    max_over_median = max_ms / median_ms if median_ms > 0 else None
    noise_ms = (
        ordered[-2]
        if len(ordered) >= SAMPLE_ROBUST_NOISE_MIN_COUNT
        else max_ms
    )
    noise_over_median = noise_ms / median_ms if median_ms > 0 else None
    return {
        "sample_count": len(ordered),
        "min_ms": min_ms,
        "median_ms": median_ms,
        "max_ms": max_ms,
        "max_over_median": max_over_median,
        "noise_ms": noise_ms,
        "noise_over_median": noise_over_median,
        "ignored_single_high_outlier": len(ordered) >= SAMPLE_ROBUST_NOISE_MIN_COUNT,
        "stability": (
            "noisy"
            if noise_over_median is not None
            and noise_over_median > SAMPLE_NOISY_MAX_OVER_MEDIAN
            else "stable"
        ),
    }


def median_float(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot compute median of empty values")
    middle = len(values) // 2
    if len(values) % 2 == 1:
        return values[middle]
    return (values[middle - 1] + values[middle]) / 2.0


def sample_stats_for_speedup(
    row: dict[str, str],
    stats: dict[tuple[int, int, str, int, int | None, int | None], dict[str, Any]] | None,
) -> dict[str, Any] | None:
    if stats is None:
        return None
    key = (
        int(row["low"]),
        int(row["high"]),
        row["name"],
        int(row["segment_size"]),
        parse_optional_int(row.get("threads")),
        parse_optional_int(row.get("requested_threads")),
    )
    return stats.get(key)


def sample_stats_for_timing(
    row: dict[str, str] | None,
    stats: dict[tuple[int, int, str, int, int | None, int | None], dict[str, Any]] | None,
) -> dict[str, Any] | None:
    if row is None or stats is None:
        return None
    key = (
        int(row["low"]),
        int(row["high"]),
        row["name"],
        int(row["segment_size"]),
        parse_optional_int(row.get("threads")),
        parse_optional_int(row.get("requested_threads")),
    )
    return stats.get(key)


def combined_sample_stability(
    circle_stats: dict[str, Any] | None,
    baseline_stats: dict[str, Any] | None,
) -> str:
    if circle_stats is None and baseline_stats is None:
        return "unknown"
    if (circle_stats and circle_stats.get("stability") == "noisy") or (
        baseline_stats and baseline_stats.get("stability") == "noisy"
    ):
        return "noisy"
    return "stable"


def parse_optional_int(raw: str | None) -> int | None:
    if raw in (None, ""):
        return None
    return int(raw)


def summarize_external_sweep_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if metadata is None:
        return {"available": False}
    return {
        "available": True,
        "started_at_utc": metadata.get("started_at_utc"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rounds": metadata.get("rounds"),
        "requested_segment_sizes": metadata.get("requested_segment_sizes", []),
        "sample_output": metadata.get("sample_output"),
        "thread_policy": metadata.get("thread_policy", {}),
    }


def summarize_external_mode_confirmation(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {"available": False}
    return {
        "available": True,
        "generated_at_utc": summary.get("generated_at_utc"),
        "min_confirmations": summary.get("min_confirmations"),
        "require_stable_samples": summary.get("require_stable_samples"),
        "observed_group_count": summary.get("observed_group_count", 0),
        "confirmed_count": summary.get("confirmed_count", 0),
        "unconfirmed_count": summary.get("unconfirmed_count", 0),
    }


def summarize_tuning_metadata(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {"available": False}
    return {
        "available": True,
        "started_at_utc": summary.get("started_at_utc"),
        "finished_at_utc": summary.get("finished_at_utc"),
        "rounds": summary.get("rounds"),
        "sample_output": summary.get("sample_output"),
        "sample_count": summary.get("sample_count"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "count_modes": summary.get("count_modes", ["segmented"]),
    }


def render_markdown(calibration: dict[str, Any]) -> str:
    lines = [
        "# Prime Engine Default Calibration",
        "",
        f"Generated: `{calibration['generated_at_utc']}`",
        f"Tolerance: `{calibration['tolerance']:.3f}` median slowdown over selected row.",
        "Minimum actionable median delta: "
        f"`{calibration.get('min_actionable_median_delta_ms', 0.0):.6f}` ms.",
        "",
        f"- recommendations: `{calibration['recommendation_count']}`",
        f"- aligned: `{calibration['aligned_count']}`",
        f"- within tolerance: `{calibration['within_tolerance_count']}`",
        f"- drift: `{calibration['drift_count']}`",
        f"- noisy drift: `{calibration.get('noisy_drift_count', 0)}`",
        f"- unconfirmed mode drift: `{calibration.get('unconfirmed_mode_drift_count', 0)}`",
        f"- missing evidence: `{calibration['missing_evidence_count']}`",
        "",
    ]
    if calibration["recommendations"]:
        lines.extend(
            [
                "| Range | Source | Baseline | Selected Mode | Current Mode | Selected Segment | Current Default | Threads | Selected Median ms | Samples | Default Ratio | Status |",
                "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in calibration["recommendations"]:
            baseline = row["baseline"] or "n/a"
            default_mode = row.get("current_default_count_mode")
            default_mode_text = "n/a" if default_mode is None else f"`{default_mode}`"
            default_segment = row["current_default_segment_size"]
            default_segment_text = "n/a" if default_segment is None else str(default_segment)
            ratio = row["default_over_selected"]
            ratio_text = "n/a" if ratio is None else f"{ratio:.3f}x"
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['source']}` | `{baseline}` | "
                f"`{row['selected_count_mode']}` | {default_mode_text} | "
                f"{row['selected_segment_size']} | {default_segment_text} | "
                f"{row['selected_threads']}/{row['selected_requested_threads']} -> "
                f"{row['current_default_threads']}/{row['current_default_requested_threads']} | "
                f"{row['selected_median_ms']:.3f} | "
                f"{sample_stability_text(row)} | {ratio_text} | `{row['status']}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def read_csv_optional(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.read_text().splitlines()))


def read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def read_sample_rows_from_metadata(metadata: dict[str, Any] | None) -> list[dict[str, str]]:
    if metadata is None:
        return []
    raw_path = metadata.get("sample_output")
    if not raw_path:
        return []
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return []
    return list(csv.DictReader(path.read_text().splitlines()))


def read_tuning_sample_rows(
    tuning_path: Path,
    metadata: dict[str, Any] | None,
) -> list[dict[str, str]]:
    if metadata is not None and metadata.get("sample_output"):
        return read_sample_rows_from_metadata(metadata)
    candidates = [tuning_path.with_suffix(".csv")]
    if tuning_path.name == "prime_engine_tuning_latest.json":
        candidates.append(tuning_path.with_name("prime_engine_tuning_latest.csv"))
    for path in candidates:
        if path.exists():
            return list(csv.DictReader(path.read_text().splitlines()))
    return []


def read_external_mode_confirmation_input_rows(
    confirmation: dict[str, Any] | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if confirmation is None:
        return [], []
    rows: list[dict[str, str]] = []
    sample_rows: list[dict[str, str]] = []
    for raw_path in confirmation.get("inputs", []):
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        rows.extend(read_csv_optional(path))
        metadata = read_json_optional(path.with_suffix(".json"))
        sample_rows.extend(read_sample_rows_from_metadata(metadata))
    return rows, sample_rows


def sample_stability_text(row: dict[str, Any]) -> str:
    stability = row.get("selected_sample_stability") or "unknown"
    effective_stability = row.get("selected_effective_sample_stability")
    circle = row.get("selected_circle_sample")
    baseline = row.get("selected_baseline_sample")
    parts = [stability]
    if effective_stability is not None and effective_stability != stability:
        parts.append(f"effective {effective_stability}")
    if circle is not None:
        parts.append(f"C {sample_spread_text(circle)}")
    if baseline is not None:
        parts.append(f"B {sample_spread_text(baseline)}")
    confirmation = row.get("selected_mode_confirmation_status")
    if confirmation:
        count = row.get("selected_mode_confirmation_count")
        minimum = row.get("selected_mode_confirmation_min")
        if count is not None and minimum is not None:
            parts.append(f"mode {confirmation} {count}/{minimum}")
        else:
            parts.append(f"mode {confirmation}")
    return "<br>".join(parts)


def sample_spread_text(stats: dict[str, Any]) -> str:
    ratio = stats.get("max_over_median")
    noise_ratio = stats.get("noise_over_median")
    count = stats.get("sample_count")
    if ratio is None:
        return f"n={count}"
    if stats.get("ignored_single_high_outlier") and noise_ratio is not None:
        return f"n={count}, robust/med={noise_ratio:.2f}, max/med={ratio:.2f}"
    return f"n={count}, max/med={ratio:.2f}"


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime engine default calibration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
