from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.calibrate_prime_engine_defaults import (  # noqa: E402
    DEFAULT_BASELINE_PRIORITY,
    RESULTS_DIR,
    read_sample_rows_from_metadata,
    select_external_recommendations,
)


DEFAULT_OUTPUT_JSON = RESULTS_DIR / "prime_engine_external_mode_confirmation_latest.json"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "prime_engine_external_mode_confirmation_latest.md"
DEFAULT_RANGES = "0:10000000,0:100000000,1000000000000:1000010000000"
DEFAULT_COUNT_MODES = (
    "segmented,balanced,dynamic,prefix-pi,presieve13,presieve17,wheel30-mark,hybrid-wheel30-mark"
)


@dataclass(frozen=True)
class ConfirmedWinner:
    low: int
    high: int
    baseline: str
    count_mode: str
    segment_size: int
    threads: int
    requested_threads: int
    confirmation_count: int
    observed_count: int
    stable_observed_count: int
    status: str
    median_ms_values: list[float]
    median_speedup_values: list[float]
    source_labels: list[str]


@dataclass(frozen=True)
class ConfirmedIdentity:
    low: int
    high: int
    baseline: str
    count_mode: str
    segment_size: int
    threads: int
    requested_threads: int
    confirmation_count: int
    observed_count: int
    stable_observed_count: int
    status: str
    median_ms_values: list[float]
    median_speedup_values: list[float]
    source_labels: list[str]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Confirm Circle prime-engine external count-mode recommendations "
            "across repeated mode sweeps."
        )
    )
    parser.add_argument(
        "--input",
        action="append",
        type=Path,
        default=[],
        help=(
            "Existing external mode-sweep CSV to include. Repeat for multiple "
            "runs. The metadata path defaults to the same stem with .json."
        ),
    )
    parser.add_argument(
        "--metadata-input",
        action="append",
        type=Path,
        default=[],
        help="Metadata JSON for the corresponding --input. Repeat in the same order.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=0,
        help="Run this many fresh external mode sweeps before confirmation.",
    )
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help=(
            "Forwarded to fresh benchmark runs: repeat each identical count "
            "request this many times inside one timed sample and use the "
            "per-request average."
        ),
    )
    parser.add_argument(
        "--warmup-rounds",
        type=int,
        default=0,
        help="Unrecorded warmup passes forwarded to fresh benchmark runs.",
    )
    parser.add_argument("--ranges", default=DEFAULT_RANGES)
    parser.add_argument("--circle-threads", type=int, default=8)
    parser.add_argument("--external-threads", type=int, default=8)
    parser.add_argument(
        "--external-baselines",
        help=(
            "Forwarded to fresh benchmark runs as --external-baselines. Use "
            "external_primesieve_count_server for focused hot-server confirmation."
        ),
    )
    parser.add_argument("--circle-count-modes", default=DEFAULT_COUNT_MODES)
    parser.add_argument(
        "--segment-sizes",
        default="0",
        help=(
            "Comma-separated Circle segment sizes to sweep in each fresh run. "
            "Use 0 to include the CLI adaptive default."
        ),
    )
    parser.add_argument(
        "--circle-variant",
        action="append",
        default=[],
        metavar="MODE:SEGMENT_SIZE[:THREADS]",
        help=(
            "Exact Circle variant to benchmark in each fresh run. Repeat or "
            "comma-separate values to avoid a noisy mode/segment cross product."
        ),
    )
    parser.add_argument(
        "--include-circle-server",
        action="store_true",
        help="Also benchmark persistent circle-prime count-server rows.",
    )
    parser.add_argument(
        "--circle-server-only",
        action="store_true",
        help=(
            "Forwarded to fresh benchmark runs: time only persistent Circle "
            "count-server rows and skip cold Circle subprocess rows."
        ),
    )
    parser.add_argument(
        "--include-primesieve-count-server",
        action="store_true",
        help="Also benchmark the persistent libprimesieve count helper.",
    )
    parser.add_argument(
        "--require-tool",
        choices=("primesieve", "primecount", "primesieve-library"),
        action="append",
        default=["primesieve", "primecount"],
    )
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument(
        "--run-prefix",
        help="Prefix for fresh sweep artifacts. Defaults to a UTC timestamp.",
    )
    parser.add_argument(
        "--baseline-priority",
        default=DEFAULT_BASELINE_PRIORITY,
        help="Comma-separated external baselines to trust, in order.",
    )
    parser.add_argument(
        "--min-confirmations",
        type=int,
        default=2,
        help="Minimum matching stable wins required to mark a range confirmed.",
    )
    parser.add_argument(
        "--allow-unstable",
        action="store_true",
        help="Count winners with noisy or missing sample stability as confirmations.",
    )
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--fail-on-unconfirmed",
        action="store_true",
        help="Exit nonzero if any observed range lacks a confirmed winner.",
    )
    args = parser.parse_args()

    if args.runs < 0:
        parser.error("--runs must be nonnegative")
    if args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.warmup_rounds < 0:
        parser.error("--warmup-rounds must be nonnegative")
    if args.circle_threads <= 0:
        parser.error("--circle-threads must be positive")
    if args.external_threads < 0:
        parser.error("--external-threads must be nonnegative")
    if args.min_confirmations <= 0:
        parser.error("--min-confirmations must be positive")
    if (
        args.include_circle_server or args.include_primesieve_count_server
    ) and args.rounds <= 0:
        parser.error("--rounds must be positive")
    if args.metadata_input and len(args.metadata_input) != len(args.input):
        parser.error("--metadata-input must be repeated once per --input")

    inputs = list(args.input)
    metadata_inputs = (
        list(args.metadata_input)
        if args.metadata_input
        else [infer_metadata_path(path) for path in inputs]
    )
    if args.runs:
        fresh_inputs, fresh_metadata = run_fresh_sweeps(args)
        inputs.extend(fresh_inputs)
        metadata_inputs.extend(fresh_metadata)
    if not inputs:
        parser.error("provide --input or --runs")

    baseline_priority = split_csv(args.baseline_priority)
    if not baseline_priority:
        parser.error("--baseline-priority must include at least one value")

    grouped = read_recommendations_by_source(
        inputs=inputs,
        metadata_inputs=metadata_inputs,
        baseline_priority=baseline_priority,
    )
    confirmation = build_confirmation(
        grouped,
        baseline_priority=baseline_priority,
        min_confirmations=args.min_confirmations,
        require_stable_samples=not args.allow_unstable,
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        inputs=[str(path) for path in inputs],
        batch_size=args.batch_size if args.runs else None,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(confirmation, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(confirmation))
    print(f"wrote external mode confirmation JSON: {args.output_json}")
    print(f"wrote external mode confirmation report: {args.output_md}")

    if args.fail_on_unconfirmed and confirmation["unconfirmed_count"] > 0:
        return 1
    return 0


def run_fresh_sweeps(args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prefix = args.run_prefix or f"prime_engine_external_mode_confirm_{stamp}"
    csv_paths: list[Path] = []
    metadata_paths: list[Path] = []
    for index in range(args.runs):
        run_label = f"{prefix}_{index + 1:02d}"
        csv_path = args.output_dir / f"{run_label}.csv"
        sample_path = args.output_dir / f"{run_label}_samples.csv"
        metadata_path = args.output_dir / f"{run_label}.json"
        command = fresh_sweep_command(args, csv_path, sample_path, metadata_path)
        print("+ " + " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)
        csv_paths.append(csv_path)
        metadata_paths.append(metadata_path)
    return csv_paths, metadata_paths


def fresh_sweep_command(
    args: argparse.Namespace,
    csv_path: Path,
    sample_path: Path,
    metadata_path: Path,
) -> list[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "benchmark_prime_external_controls.py"),
        "--ranges",
        args.ranges,
        "--rounds",
        str(args.rounds),
        "--batch-size",
        str(args.batch_size),
        "--warmup-rounds",
        str(args.warmup_rounds),
        "--interleaved",
        "--circle-threads",
        str(args.circle_threads),
        "--external-threads",
        str(args.external_threads),
    ]
    if getattr(args, "external_baselines", None):
        command.extend(["--external-baselines", args.external_baselines])
    command.extend(
        [
            "--circle-count-modes",
            args.circle_count_modes,
            "--segment-sizes",
            args.segment_sizes,
            "--output",
            str(csv_path),
            "--sample-output",
            str(sample_path),
            "--metadata-output",
            str(metadata_path),
        ]
    )
    for variant in getattr(args, "circle_variant", []) or []:
        command.extend(["--circle-variant", variant])
    if getattr(args, "include_circle_server", False):
        command.append("--include-circle-server")
    if getattr(args, "circle_server_only", False):
        command.append("--circle-server-only")
    if getattr(args, "include_primesieve_count_server", False):
        command.append("--include-primesieve-count-server")
    for tool in sorted(set(args.require_tool)):
        command.extend(["--require-tool", tool])
    return command


def read_recommendations_by_source(
    *,
    inputs: list[Path],
    metadata_inputs: list[Path],
    baseline_priority: list[str],
) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    for csv_path, metadata_path in zip(inputs, metadata_inputs):
        rows = read_csv(csv_path)
        metadata = read_json_optional(metadata_path)
        sample_rows = read_sample_rows_from_metadata(metadata)
        for row in select_external_recommendations(
            [(csv_path.stem, rows, sample_rows)],
            baseline_priority,
        ):
            row["source_path"] = str(csv_path)
            for candidate in row.get("candidates", []):
                candidate.setdefault("source_path", str(csv_path))
            recommendations.append(row)
    return recommendations


def build_confirmation(
    recommendations: list[dict[str, Any]],
    *,
    baseline_priority: list[str],
    min_confirmations: int,
    require_stable_samples: bool,
    generated_at_utc: str,
    inputs: list[str],
    batch_size: int | None = None,
) -> dict[str, Any]:
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in recommendations:
        grouped.setdefault((int(row["low"]), int(row["high"]), str(row["baseline"])), []).append(row)

    winners = []
    identity_summaries = []
    for key, rows in sorted(grouped.items()):
        winners.append(
            asdict(
                confirm_group(
                    key,
                    rows,
                    min_confirmations=min_confirmations,
                    require_stable_samples=require_stable_samples,
                )
            )
        )
        identity_summaries.extend(
            asdict(row)
            for row in confirm_identities(
                key,
                rows,
                min_confirmations=min_confirmations,
                require_stable_samples=require_stable_samples,
            )
        )
    confirmed_count = sum(1 for row in winners if row["status"] == "confirmed")
    return {
        "generated_at_utc": generated_at_utc,
        "inputs": inputs,
        "batch_size": batch_size,
        "baseline_priority": baseline_priority,
        "min_confirmations": min_confirmations,
        "require_stable_samples": require_stable_samples,
        "observed_group_count": len(winners),
        "confirmed_count": confirmed_count,
        "unconfirmed_count": len(winners) - confirmed_count,
        "winners": winners,
        "identity_summaries": identity_summaries,
    }


def confirm_group(
    key: tuple[int, int, str],
    rows: list[dict[str, Any]],
    *,
    min_confirmations: int,
    require_stable_samples: bool,
) -> ConfirmedWinner:
    low, high, baseline = key
    eligible = [
        row
        for row in rows
        if row_is_confirmation_eligible(
            row,
            require_stable_samples=require_stable_samples,
        )
    ]
    counter = Counter(winner_key(row) for row in eligible)
    if counter:
        selected_key, confirmation_count = counter.most_common(1)[0]
    else:
        selected_key = winner_key(min(rows, key=lambda row: float(row["median_ms"])))
        confirmation_count = 0

    selected_rows = [row for row in rows if winner_key(row) == selected_key]
    mode, segment_size, threads, requested_threads = selected_key
    stable_observed = sum(1 for row in rows if row.get("sample_stability") == "stable")
    status = "confirmed" if confirmation_count >= min_confirmations else "unconfirmed"
    return ConfirmedWinner(
        low=low,
        high=high,
        baseline=baseline,
        count_mode=mode,
        segment_size=segment_size,
        threads=threads,
        requested_threads=requested_threads,
        confirmation_count=confirmation_count,
        observed_count=len(rows),
        stable_observed_count=stable_observed,
        status=status,
        median_ms_values=[float(row["median_ms"]) for row in selected_rows],
        median_speedup_values=median_speedup_values(selected_rows),
        source_labels=[str(row.get("source_path") or row.get("source")) for row in selected_rows],
    )


def winner_key(row: dict[str, Any]) -> tuple[str, int, int, int]:
    return (
        str(row.get("count_mode", "segmented")),
        int(row["segment_size"]),
        int(row["threads"]),
        int(row["requested_threads"]),
    )


def confirm_identities(
    key: tuple[int, int, str],
    rows: list[dict[str, Any]],
    *,
    min_confirmations: int,
    require_stable_samples: bool,
) -> list[ConfirmedIdentity]:
    low, high, baseline = key
    grouped: dict[tuple[str, int, int, int], list[dict[str, Any]]] = {}
    for row in rows:
        candidates = row.get("candidates") or [row]
        for candidate in candidates:
            grouped.setdefault(winner_key(candidate), []).append(candidate)

    identities = []
    for identity, identity_rows in sorted(grouped.items()):
        eligible = [
            row
            for row in identity_rows
            if row_is_confirmation_eligible(
                row,
                require_stable_samples=require_stable_samples,
            )
        ]
        confirmation_count = len(eligible)
        mode, segment_size, threads, requested_threads = identity
        status = "confirmed" if confirmation_count >= min_confirmations else "unconfirmed"
        identities.append(
            ConfirmedIdentity(
                low=low,
                high=high,
                baseline=baseline,
                count_mode=mode,
                segment_size=segment_size,
                threads=threads,
                requested_threads=requested_threads,
                confirmation_count=confirmation_count,
                observed_count=len(identity_rows),
                stable_observed_count=sum(
                    1 for row in identity_rows if row.get("sample_stability") == "stable"
                ),
                status=status,
                median_ms_values=[float(row["median_ms"]) for row in identity_rows],
                median_speedup_values=median_speedup_values(identity_rows),
                source_labels=[
                    str(row.get("source_path") or row.get("source"))
                    for row in identity_rows
                ],
            )
        )
    return identities


def row_is_confirmation_eligible(
    row: dict[str, Any],
    *,
    require_stable_samples: bool,
) -> bool:
    if require_stable_samples and row.get("sample_stability") != "stable":
        return False
    return median_speedup_beats_baseline(row)


def median_speedup_beats_baseline(row: dict[str, Any]) -> bool:
    speedup = median_speedup_value(row)
    if speedup is None:
        return False
    return speedup > 1.0


def median_speedup_value(row: dict[str, Any]) -> float | None:
    raw = row.get("median_circle_speedup", row.get("median_speedup"))
    if raw is None or raw == "":
        return None
    return float(raw)


def median_speedup_values(rows: list[dict[str, Any]]) -> list[float]:
    values = []
    for row in rows:
        speedup = median_speedup_value(row)
        if speedup is not None:
            values.append(speedup)
    return values


def render_markdown(confirmation: dict[str, Any]) -> str:
    lines = [
        "# Prime Engine External Mode Confirmation",
        "",
        f"Generated: `{confirmation['generated_at_utc']}`",
        f"Minimum confirmations: `{confirmation['min_confirmations']}`",
        f"Require stable samples: `{confirmation['require_stable_samples']}`",
    ]
    if confirmation.get("batch_size"):
        lines.append(
            "Fresh-run count requests per timed sample: "
            f"`{confirmation['batch_size']}`"
        )
    lines.extend(
        [
            "",
            f"- observed groups: `{confirmation['observed_group_count']}`",
            f"- confirmed: `{confirmation['confirmed_count']}`",
            f"- unconfirmed: `{confirmation['unconfirmed_count']}`",
            "",
        ]
    )
    if confirmation["winners"]:
        lines.extend(
            [
                "| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in confirmation["winners"]:
            medians = ", ".join(f"{value:.3f}" for value in row["median_ms_values"])
            speedups = ", ".join(
                f"{value:.3f}" for value in row.get("median_speedup_values", [])
            )
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                f"`{row['count_mode']}` | {row['segment_size']} | "
                f"{row['threads']}/{row['requested_threads']} | "
                f"{row['confirmation_count']}/{confirmation['min_confirmations']} | "
                f"{row['stable_observed_count']}/{row['observed_count']} | "
                f"{medians} | {speedups} | `{row['status']}` |"
            )
        lines.append("")
    if confirmation.get("identity_summaries"):
        lines.extend(
            [
                "## Identity Evidence",
                "",
                "| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for row in confirmation["identity_summaries"]:
            speedups = ", ".join(
                f"{value:.3f}" for value in row.get("median_speedup_values", [])
            )
            speedups = speedups or "-"
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                f"`{row['count_mode']}` | {row['segment_size']} | "
                f"{row['threads']}/{row['requested_threads']} | "
                f"{row['confirmation_count']}/{confirmation['min_confirmations']} | "
                f"{row['stable_observed_count']}/{row['observed_count']} | "
                f"{speedups} | `{row['status']}` |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def infer_metadata_path(csv_path: Path) -> Path:
    return csv_path.with_suffix(".json")


def read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines()))


def read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"external mode confirmation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
