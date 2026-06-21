from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_prime_benchmark_provenance import benchmark_provenance_failures


DEFAULT_CSV = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_high_offset_count_binary_segment_sweep_latest.csv"
)
DEFAULT_METADATA = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_high_offset_count_binary_segment_sweep_latest.json"
)
DEFAULT_CIRCLE_PRIME = ROOT / "target" / "release" / "circle-prime"
DEFAULT_CIRCLE_PRIME_COUNT = ROOT / "target" / "release" / "circle-prime-count"
DEFAULT_DEFAULTS = ROOT / "rust" / "circle-prime" / "prime_engine_defaults.json"
TRIAL_ACTION = "trial_cold_count_binary_candidate"


@dataclass(frozen=True)
class ColdCountBinaryRow:
    name: str
    low: int
    high: int
    baseline: str
    median_speedup: float
    best_speedup: float
    count_mode: str
    segment_size: int
    threads: int
    requested_threads: int
    sample_stability: str

    @property
    def is_default(self) -> bool:
        return "_default_count" in self.name

    @property
    def identity(self) -> str:
        return f"{self.count_mode}:{self.segment_size}:{self.threads}"

    @property
    def group_key(self) -> tuple[int, int, str]:
        return (self.low, self.high, self.baseline)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when the high-offset count-binary sweep contains a stable, "
            "material cold one-shot variant that should be trialed as the "
            "count-binary default."
        )
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument(
        "--confirmation-csv",
        type=Path,
        help=(
            "Optional focused confirmation CSV. Trial-ready sweep rows are held "
            "when this artifact contains the same candidate and does not confirm it."
        ),
    )
    parser.add_argument(
        "--confirmation-metadata",
        type=Path,
        help="Optional focused confirmation metadata for current-binary provenance checks.",
    )
    parser.add_argument("--circle-prime", type=Path, default=DEFAULT_CIRCLE_PRIME)
    parser.add_argument(
        "--circle-prime-count",
        type=Path,
        default=DEFAULT_CIRCLE_PRIME_COUNT,
    )
    parser.add_argument("--defaults", type=Path, default=DEFAULT_DEFAULTS)
    parser.add_argument(
        "--min-gain",
        type=float,
        default=1.03,
        help="Minimum candidate/default median-speedup ratio required to fail.",
    )
    parser.add_argument(
        "--min-candidate-median-speedup",
        type=float,
        default=1.0,
        help="Minimum candidate median speedup versus cold primesieve required to fail.",
    )
    parser.add_argument(
        "--min-candidate-best-speedup",
        type=float,
        default=1.0,
        help="Minimum candidate best-time speedup versus cold primesieve required to fail.",
    )
    parser.add_argument(
        "--allow-noisy",
        action="store_true",
        help="Allow noisy candidate/default sample rows when deciding trial readiness.",
    )
    parser.add_argument(
        "--skip-provenance",
        action="store_true",
        help="Skip current-binary/defaults provenance checks. Intended for tests only.",
    )
    args = parser.parse_args()

    if args.min_gain < 0.0:
        parser.error("--min-gain must be nonnegative")
    if args.min_candidate_median_speedup < 0.0:
        parser.error("--min-candidate-median-speedup must be nonnegative")
    if args.min_candidate_best_speedup < 0.0:
        parser.error("--min-candidate-best-speedup must be nonnegative")

    try:
        rows = load_cold_count_binary_rows(args.csv)
        confirmation_rows = (
            load_cold_count_binary_rows(args.confirmation_csv)
            if args.confirmation_csv is not None and args.confirmation_csv.exists()
            else []
        )
        provenance_failures = []
        if not args.skip_provenance:
            provenance_failures = current_provenance_failures(
                args.metadata,
                circle_prime=args.circle_prime,
                circle_prime_count=args.circle_prime_count,
                defaults_path=args.defaults,
            )
            if args.confirmation_metadata is not None and args.confirmation_metadata.exists():
                provenance_failures.extend(
                    current_provenance_failures(
                        args.confirmation_metadata,
                        circle_prime=args.circle_prime,
                        circle_prime_count=args.circle_prime_count,
                        defaults_path=args.defaults,
                    )
                )
    except OSError as exc:
        print(f"ERROR: could not read cold count-binary evidence: {exc}", file=sys.stderr)
        return 1
    except (csv.Error, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not parse cold count-binary evidence: {exc}", file=sys.stderr)
        return 1

    if provenance_failures:
        for failure in provenance_failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1

    result = check_cold_count_binary_candidates(
        rows,
        min_gain=args.min_gain,
        min_candidate_median_speedup=args.min_candidate_median_speedup,
        min_candidate_best_speedup=args.min_candidate_best_speedup,
        require_stable_samples=not args.allow_noisy,
    )
    if confirmation_rows:
        result = apply_confirmation_holds(
            result,
            confirmation_rows,
            min_gain=args.min_gain,
            min_candidate_median_speedup=args.min_candidate_median_speedup,
            min_candidate_best_speedup=args.min_candidate_best_speedup,
        )
    if result["ok"]:
        print(result["message"])
        return 0

    print(result["message"], file=sys.stderr)
    for row in result["trial_rows"]:
        print(f"  - {format_trial_row(row)}", file=sys.stderr)
    return 1


def apply_confirmation_holds(
    result: dict[str, Any],
    confirmation_rows: list[ColdCountBinaryRow],
    *,
    min_gain: float,
    min_candidate_median_speedup: float,
    min_candidate_best_speedup: float,
) -> dict[str, Any]:
    trial_rows = result.get("trial_rows") or []
    if result.get("ok") or not trial_rows:
        return result

    stable_summaries = cold_count_binary_candidate_rows(
        confirmation_rows,
        min_gain=min_gain,
        min_candidate_median_speedup=min_candidate_median_speedup,
        min_candidate_best_speedup=min_candidate_best_speedup,
        require_stable_samples=True,
    )
    noisy_summaries = cold_count_binary_candidate_rows(
        confirmation_rows,
        min_gain=min_gain,
        min_candidate_median_speedup=min_candidate_median_speedup,
        min_candidate_best_speedup=min_candidate_best_speedup,
        require_stable_samples=False,
    )

    remaining = []
    held = []
    for trial in trial_rows:
        stable = matching_confirmation_summary(trial, stable_summaries)
        noisy = matching_confirmation_summary(trial, noisy_summaries)
        if stable is not None:
            if stable.get("action") == TRIAL_ACTION:
                remaining.append(trial)
            else:
                held.append((trial, stable, "stable"))
            continue
        if noisy is not None and noisy.get("action") != TRIAL_ACTION:
            held.append((trial, noisy, "noisy"))
            continue
        remaining.append(trial)

    if remaining:
        return {
            **result,
            "trial_rows": remaining,
            "message": (
                "ERROR: high-offset cold count-binary readout has "
                f"{len(remaining)} trial-ready candidate(s) after focused "
                "confirmation. Promote them intentionally or record why they "
                "are being held."
            ),
        }

    held_text = ", ".join(
        f"{identity_text(summary.get('best'))} {scope} action={summary.get('action')}"
        for _, summary, scope in held
    )
    return {
        "ok": True,
        "message": (
            "OK: no trial-ready high-offset cold count-binary candidates "
            f"({len(held)} sweep candidate(s) held by focused confirmation: "
            f"{held_text})."
        ),
        "trial_rows": [],
    }


def matching_confirmation_summary(
    trial: dict[str, Any],
    summaries: list[dict[str, Any]],
) -> dict[str, Any] | None:
    trial_best = row_identity_key(trial.get("best"))
    for summary in summaries:
        if (
            summary.get("low") == trial.get("low")
            and summary.get("high") == trial.get("high")
            and summary.get("baseline") == trial.get("baseline")
            and row_identity_key(summary.get("best")) == trial_best
        ):
            return summary
    return None


def row_identity_key(value: Any) -> tuple[Any, Any, Any, Any] | None:
    if not isinstance(value, dict):
        return None
    return (
        value.get("count_mode"),
        value.get("segment_size"),
        value.get("circle_threads"),
        value.get("circle_requested_threads"),
    )


def current_provenance_failures(
    metadata_path: Path,
    *,
    circle_prime: Path,
    circle_prime_count: Path,
    defaults_path: Path,
) -> list[str]:
    if not metadata_path.exists():
        return [f"benchmark metadata is missing: {metadata_path}"]
    metadata = json.loads(metadata_path.read_text())
    if not isinstance(metadata, dict):
        return [f"expected metadata object in {metadata_path}"]
    return benchmark_provenance_failures(
        metadata,
        circle_prime=circle_prime,
        circle_prime_count=circle_prime_count,
        defaults_path=defaults_path,
    )


def load_cold_count_binary_rows(path: Path) -> list[ColdCountBinaryRow]:
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            parsed = parse_cold_count_binary_row(row)
            if parsed is not None:
                rows.append(parsed)
    return rows


def parse_cold_count_binary_row(row: dict[str, str]) -> ColdCountBinaryRow | None:
    if row.get("kind") != "speedup":
        return None
    if row.get("baseline") != "external_primesieve_count":
        return None
    name = row.get("name", "")
    if not name.startswith("circle_prime_count_binary_"):
        return None
    if "_server_" in name:
        return None
    return ColdCountBinaryRow(
        name=name,
        low=int(row["low"]),
        high=int(row["high"]),
        baseline=row["baseline"],
        median_speedup=float(row["median_speedup"]),
        best_speedup=float(row["best_speedup"]),
        count_mode=row.get("count_mode", ""),
        segment_size=int(row.get("segment_size") or 0),
        threads=int(row.get("threads") or 0),
        requested_threads=int(row.get("requested_threads") or 0),
        sample_stability=row.get("sample_stability", ""),
    )


def check_cold_count_binary_candidates(
    rows: list[ColdCountBinaryRow],
    *,
    min_gain: float = 1.03,
    min_candidate_median_speedup: float = 1.0,
    min_candidate_best_speedup: float = 1.0,
    require_stable_samples: bool = True,
) -> dict[str, Any]:
    summary_rows = cold_count_binary_candidate_rows(
        rows,
        min_gain=min_gain,
        min_candidate_median_speedup=min_candidate_median_speedup,
        min_candidate_best_speedup=min_candidate_best_speedup,
        require_stable_samples=require_stable_samples,
    )
    if not summary_rows:
        if rows:
            stability_scope = "stable " if require_stable_samples else ""
            noisy_context = ""
            if require_stable_samples:
                noisy_summary_rows = cold_count_binary_candidate_rows(
                    rows,
                    min_gain=min_gain,
                    min_candidate_median_speedup=min_candidate_median_speedup,
                    min_candidate_best_speedup=min_candidate_best_speedup,
                    require_stable_samples=False,
                )
                if noisy_summary_rows:
                    noisy_context = (
                        f"; noisy fallback best gain {best_gain_text(noisy_summary_rows)}, "
                        f"best action {best_action_text(noisy_summary_rows)}"
                    )
            return {
                "ok": True,
                "message": (
                    "OK: no trial-ready high-offset cold count-binary candidates "
                    f"(no comparable {stability_scope}row groups among "
                    f"{len(rows)} parsed row(s){noisy_context})."
                ),
                "trial_rows": [],
            }
        return {
            "ok": False,
            "message": (
                "ERROR: no comparable cold count-binary default/candidate rows "
                "were found; rerun `make prime-engine-high-offset-count-binary-sweep`."
            ),
            "trial_rows": [],
        }
    trial_rows = [
        row for row in summary_rows if row.get("action") == TRIAL_ACTION
    ]
    if trial_rows:
        return {
            "ok": False,
            "message": (
                "ERROR: high-offset cold count-binary readout has "
                f"{len(trial_rows)} trial-ready candidate(s). Promote them "
                "intentionally or record why they are being held."
            ),
            "trial_rows": trial_rows,
        }
    return {
        "ok": True,
        "message": (
            "OK: no trial-ready high-offset cold count-binary candidates "
            f"({len(summary_rows)} row group(s) checked; best gain "
            f"{best_gain_text(summary_rows)})."
        ),
        "trial_rows": [],
    }


def cold_count_binary_candidate_rows(
    rows: list[ColdCountBinaryRow],
    *,
    min_gain: float,
    min_candidate_median_speedup: float,
    min_candidate_best_speedup: float,
    require_stable_samples: bool,
) -> list[dict[str, Any]]:
    groups: dict[tuple[int, int, str], list[ColdCountBinaryRow]] = {}
    for row in rows:
        groups.setdefault(row.group_key, []).append(row)

    summaries = []
    for key_rows in groups.values():
        default = best_row(
            [row for row in key_rows if row.is_default],
            require_stable_samples=require_stable_samples,
        )
        if default is None:
            continue
        candidates = [row for row in key_rows if not row.is_default]
        best = best_row(candidates, require_stable_samples=require_stable_samples)
        if best is None:
            summaries.append(summary_row("keep_default", default, default, 1.0))
            continue
        gain = safe_ratio(best.median_speedup, default.median_speedup)
        if gain is None or best.median_speedup <= default.median_speedup:
            action = "keep_default"
        elif gain >= min_gain and best.median_speedup >= min_candidate_median_speedup:
            if best.best_speedup >= min_candidate_best_speedup:
                action = TRIAL_ACTION
            else:
                action = "hold_best_speedup_below_floor"
        else:
            action = "hold_small_gain_candidate"
        summaries.append(summary_row(action, default, best, gain or 0.0))
    return summaries


def best_row(
    rows: list[ColdCountBinaryRow],
    *,
    require_stable_samples: bool,
) -> ColdCountBinaryRow | None:
    eligible = [
        row
        for row in rows
        if not require_stable_samples or row.sample_stability == "stable"
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda row: row.median_speedup)


def summary_row(
    action: str,
    default: ColdCountBinaryRow,
    best: ColdCountBinaryRow,
    gain: float,
) -> dict[str, Any]:
    return {
        "action": action,
        "low": default.low,
        "high": default.high,
        "baseline": default.baseline,
        "median_gain_over_default": gain,
        "default": row_identity(default),
        "best": row_identity(best),
    }


def row_identity(row: ColdCountBinaryRow) -> dict[str, Any]:
    return {
        "name": row.name,
        "count_mode": row.count_mode,
        "segment_size": row.segment_size,
        "circle_threads": row.threads,
        "circle_requested_threads": row.requested_threads,
        "median_circle_speedup": row.median_speedup,
        "best_circle_speedup": row.best_speedup,
        "sample_stability": row.sample_stability,
    }


def safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None
    return numerator / denominator


def best_gain_text(rows: list[dict[str, Any]]) -> str:
    gains = [
        float(row["median_gain_over_default"])
        for row in rows
        if row.get("median_gain_over_default") is not None
    ]
    if not gains:
        return "unknown"
    return f"{max(gains):.3f}x"


def best_action_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "unknown"
    best = max(
        rows,
        key=lambda row: (
            float(row.get("median_gain_over_default") or 0.0),
            str(row.get("action", "")),
        ),
    )
    return str(best.get("action", "unknown"))


def format_trial_row(row: dict[str, Any]) -> str:
    default = identity_text(row.get("default"))
    best = identity_text(row.get("best"))
    return (
        f"[{row.get('low', '?')}, {row.get('high', '?')}) "
        f"baseline={row.get('baseline', '?')} default={default} "
        f"candidate={best} gain={ratio_text(row.get('median_gain_over_default'))} "
        f"candidate_speedup={ratio_text(nested_get(row, 'best', 'median_circle_speedup'))}"
    )


def identity_text(value: Any) -> str:
    if not isinstance(value, dict):
        return "?"
    mode = value.get("count_mode", "?")
    segment_size = value.get("segment_size", "?")
    threads = value.get("circle_threads", value.get("circle_requested_threads", "?"))
    return f"{mode}:{segment_size}:{threads}"


def ratio_text(value: Any) -> str:
    if value is None:
        return "?"
    try:
        return f"{float(value):.3f}x"
    except (TypeError, ValueError):
        return str(value)


def nested_get(row: dict[str, Any], *keys: str) -> Any:
    value: Any = row
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
