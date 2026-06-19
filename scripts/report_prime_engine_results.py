from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
DEFAULT_BENCHMARK = RESULTS_DIR / "prime_engine_benchmark_latest.csv"
DEFAULT_EXTERNAL = RESULTS_DIR / "prime_engine_external_controls_parallel_latest.csv"
DEFAULT_EXTERNAL_METADATA = RESULTS_DIR / "prime_engine_external_controls_parallel_latest.json"
DEFAULT_EXTERNAL_CORRECTNESS = (
    RESULTS_DIR / "prime_engine_external_correctness_latest.json"
)
DEFAULT_EXTERNAL_NEXT = RESULTS_DIR / "prime_engine_external_next_latest.csv"
DEFAULT_EXTERNAL_NEXT_METADATA = (
    RESULTS_DIR / "prime_engine_external_next_latest.json"
)
DEFAULT_EXTERNAL_THROUGHPUT = (
    RESULTS_DIR / "prime_engine_external_throughput_latest.csv"
)
DEFAULT_EXTERNAL_THROUGHPUT_METADATA = (
    RESULTS_DIR / "prime_engine_external_throughput_latest.json"
)
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
DEFAULT_HIGH_OFFSET_HOT_COLD_BENCHMARK = (
    RESULTS_DIR / "prime_engine_high_offset_hot_cold_latest.csv"
)
DEFAULT_TUNING = RESULTS_DIR / "prime_engine_tuning_latest.json"
DEFAULT_DEFAULT_CALIBRATION = RESULTS_DIR / "prime_engine_default_calibration_latest.json"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "prime_engine_report_latest.md"
DEFAULT_OUTPUT_JSON = RESULTS_DIR / "prime_engine_report_latest.json"
SAMPLE_NOISY_MAX_OVER_MEDIAN = 1.5


PRIMARY_COUNT_ROWS = {
    "segmented_range_count",
    "high_offset_segmented_range_count",
    "parallel_high_offset_default_range_count_8t",
    "parallel_high_offset_presieve13_range_count_8t",
    "parallel_high_offset_presieve17_range_count_8t",
    "parallel_high_offset_segmented_range_count_8t",
}
EXPERIMENTAL_COUNT_ROWS = {
    "bitpacked_range_count",
    "high_offset_bitpacked_range_count",
    "high_offset_presieve13_range_count",
    "high_offset_presieve17_range_count",
    "parallel_high_offset_balanced_segmented_range_count_8t",
    "high_offset_hybrid_wheel30_mark_range_count",
    "high_offset_tracked_byte_range_count",
    "high_offset_wheel30_range_count",
    "high_offset_wheel30_mark_range_count",
    "parallel_high_offset_hybrid_wheel30_mark_range_count_8t",
    "parallel_high_offset_wheel30_mark_range_count_8t",
    "hybrid_wheel30_mark_range_count",
    "presieve13_range_count",
    "presieve17_range_count",
    "tracked_byte_range_count",
    "wheel30_range_count",
    "wheel30_mark_range_count",
}
MATERIALIZED_GENERATION_ROWS = {
    "enumerate_range_primes",
}
NEXT_PRIME_SEARCH_ROWS = {
    "next_prime_search",
}
COLD_PROCESS_ROWS = {
    "cold_cli_parallel_default_range_count_8t",
    "cold_cli_parallel_high_offset_default_range_count_8t",
    "cold_process_segmented_range_count",
    "cold_process_parallel_segmented_range_count_8t",
    "cold_process_parallel_high_offset_segmented_range_count_8t",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize Circle prime-engine benchmark, tuning, and external-control artifacts."
    )
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--external", type=Path, default=DEFAULT_EXTERNAL)
    parser.add_argument("--external-metadata", type=Path, default=DEFAULT_EXTERNAL_METADATA)
    parser.add_argument(
        "--external-correctness",
        type=Path,
        default=DEFAULT_EXTERNAL_CORRECTNESS,
    )
    parser.add_argument(
        "--external-throughput",
        type=Path,
        default=DEFAULT_EXTERNAL_THROUGHPUT,
    )
    parser.add_argument(
        "--external-next",
        type=Path,
        default=DEFAULT_EXTERNAL_NEXT,
    )
    parser.add_argument(
        "--external-next-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_NEXT_METADATA,
    )
    parser.add_argument(
        "--external-throughput-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_THROUGHPUT_METADATA,
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
    parser.add_argument(
        "--high-offset-hot-cold-benchmark",
        type=Path,
        default=DEFAULT_HIGH_OFFSET_HOT_COLD_BENCHMARK,
    )
    parser.add_argument("--tuning", type=Path, default=DEFAULT_TUNING)
    parser.add_argument(
        "--default-calibration",
        type=Path,
        default=DEFAULT_DEFAULT_CALIBRATION,
    )
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument(
        "--require-inputs",
        action="store_true",
        help="Fail if any default input artifact is missing.",
    )
    args = parser.parse_args()

    report = build_report(
        benchmark_path=args.benchmark,
        external_path=args.external,
        external_metadata_path=args.external_metadata,
        external_correctness_path=args.external_correctness,
        external_next_path=args.external_next,
        external_next_metadata_path=args.external_next_metadata,
        external_throughput_path=args.external_throughput,
        external_throughput_metadata_path=args.external_throughput_metadata,
        external_segment_sweep_path=args.external_segment_sweep,
        external_segment_sweep_metadata_path=args.external_segment_sweep_metadata,
        external_mode_sweep_path=args.external_mode_sweep,
        external_mode_sweep_metadata_path=args.external_mode_sweep_metadata,
        external_mode_confirmation_path=args.external_mode_confirmation,
        external_high_offset_quick_path=args.external_high_offset_quick,
        external_high_offset_quick_metadata_path=args.external_high_offset_quick_metadata,
        external_high_offset_tight_path=args.external_high_offset_tight,
        external_high_offset_tight_metadata_path=args.external_high_offset_tight_metadata,
        external_high_offset_confirmation_path=args.external_high_offset_confirmation,
        high_offset_hot_cold_benchmark_path=args.high_offset_hot_cold_benchmark,
        tuning_path=args.tuning,
        default_calibration_path=args.default_calibration,
        generated_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    if args.require_inputs and report["missing_inputs"]:
        missing = ", ".join(report["missing_inputs"])
        raise FileNotFoundError(f"missing required prime-engine report inputs: {missing}")

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(report))
    print(f"wrote prime-engine report: {args.output_md}")
    print(f"wrote prime-engine report JSON: {args.output_json}")
    return 0


def build_report(
    *,
    benchmark_path: Path,
    external_path: Path,
    tuning_path: Path,
    external_metadata_path: Path | None = None,
    external_correctness_path: Path | None = None,
    external_next_path: Path | None = None,
    external_next_metadata_path: Path | None = None,
    external_throughput_path: Path | None = None,
    external_throughput_metadata_path: Path | None = None,
    external_segment_sweep_path: Path | None = None,
    external_segment_sweep_metadata_path: Path | None = None,
    external_mode_sweep_path: Path | None = None,
    external_mode_sweep_metadata_path: Path | None = None,
    external_mode_confirmation_path: Path | None = None,
    external_high_offset_quick_path: Path | None = None,
    external_high_offset_quick_metadata_path: Path | None = None,
    external_high_offset_tight_path: Path | None = None,
    external_high_offset_tight_metadata_path: Path | None = None,
    external_high_offset_confirmation_path: Path | None = None,
    high_offset_hot_cold_benchmark_path: Path | None = None,
    default_calibration_path: Path | None = None,
    generated_at_utc: str,
) -> dict[str, Any]:
    missing_inputs: list[str] = []
    benchmark_rows = read_csv_if_present(benchmark_path, missing_inputs)
    external_rows = read_csv_if_present(external_path, missing_inputs)
    external_metadata = read_json_optional(external_metadata_path)
    external_sample_rows = read_sample_rows_from_metadata(external_metadata)
    external_correctness = (
        read_json_if_present(external_correctness_path, missing_inputs)
        if external_correctness_path is not None
        else None
    )
    external_next_rows = read_csv_optional(external_next_path)
    external_next_metadata = read_json_optional(external_next_metadata_path)
    external_next_sample_rows = read_sample_rows_from_metadata(external_next_metadata)
    external_throughput_rows = read_csv_optional(external_throughput_path)
    external_throughput_metadata = read_json_optional(external_throughput_metadata_path)
    external_throughput_sample_rows = read_sample_rows_from_metadata(
        external_throughput_metadata
    )
    external_segment_sweep_rows = read_csv_optional(external_segment_sweep_path)
    external_segment_sweep_metadata = read_json_optional(
        external_segment_sweep_metadata_path
    )
    external_segment_sweep_sample_rows = read_sample_rows_from_metadata(
        external_segment_sweep_metadata
    )
    external_mode_sweep_rows = read_csv_optional(external_mode_sweep_path)
    external_mode_sweep_metadata = read_json_optional(external_mode_sweep_metadata_path)
    external_mode_sweep_sample_rows = read_sample_rows_from_metadata(
        external_mode_sweep_metadata
    )
    external_mode_confirmation = read_json_optional(external_mode_confirmation_path)
    external_high_offset_quick_rows = read_csv_optional(external_high_offset_quick_path)
    external_high_offset_quick_metadata = read_json_optional(
        external_high_offset_quick_metadata_path
    )
    external_high_offset_quick_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_quick_metadata
    )
    external_high_offset_tight_rows = read_csv_optional(external_high_offset_tight_path)
    external_high_offset_tight_metadata = read_json_optional(
        external_high_offset_tight_metadata_path
    )
    external_high_offset_tight_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_tight_metadata
    )
    external_high_offset_confirmation = read_json_optional(
        external_high_offset_confirmation_path
    )
    high_offset_hot_cold_benchmark_rows = read_csv_optional(
        high_offset_hot_cold_benchmark_path
    )
    tuning_summary = read_json_if_present(tuning_path, missing_inputs)
    default_calibration = read_json_optional(default_calibration_path)

    default_calibration_summary = summarize_default_calibration(default_calibration)
    return {
        "generated_at_utc": generated_at_utc,
        "inputs": {
            "benchmark": str(benchmark_path),
            "external": str(external_path),
            "external_metadata": (
                str(external_metadata_path) if external_metadata_path is not None else None
            ),
            "external_correctness": (
                str(external_correctness_path)
                if external_correctness_path is not None
                else None
            ),
            "external_throughput": (
                str(external_throughput_path)
                if external_throughput_path is not None
                else None
            ),
            "external_next": (
                str(external_next_path) if external_next_path is not None else None
            ),
            "external_next_metadata": (
                str(external_next_metadata_path)
                if external_next_metadata_path is not None
                else None
            ),
            "external_throughput_metadata": (
                str(external_throughput_metadata_path)
                if external_throughput_metadata_path is not None
                else None
            ),
            "external_segment_sweep": (
                str(external_segment_sweep_path)
                if external_segment_sweep_path is not None
                else None
            ),
            "external_segment_sweep_metadata": (
                str(external_segment_sweep_metadata_path)
                if external_segment_sweep_metadata_path is not None
                else None
            ),
            "external_mode_sweep": (
                str(external_mode_sweep_path)
                if external_mode_sweep_path is not None
                else None
            ),
            "external_mode_sweep_metadata": (
                str(external_mode_sweep_metadata_path)
                if external_mode_sweep_metadata_path is not None
                else None
            ),
            "external_mode_confirmation": (
                str(external_mode_confirmation_path)
                if external_mode_confirmation_path is not None
                else None
            ),
            "external_high_offset_quick": (
                str(external_high_offset_quick_path)
                if external_high_offset_quick_path is not None
                else None
            ),
            "external_high_offset_quick_metadata": (
                str(external_high_offset_quick_metadata_path)
                if external_high_offset_quick_metadata_path is not None
                else None
            ),
            "external_high_offset_tight": (
                str(external_high_offset_tight_path)
                if external_high_offset_tight_path is not None
                else None
            ),
            "external_high_offset_tight_metadata": (
                str(external_high_offset_tight_metadata_path)
                if external_high_offset_tight_metadata_path is not None
                else None
            ),
            "external_high_offset_confirmation": (
                str(external_high_offset_confirmation_path)
                if external_high_offset_confirmation_path is not None
                else None
            ),
            "high_offset_hot_cold_benchmark": (
                str(high_offset_hot_cold_benchmark_path)
                if high_offset_hot_cold_benchmark_path is not None
                else None
            ),
            "tuning": str(tuning_path),
            "default_calibration": (
                str(default_calibration_path) if default_calibration_path is not None else None
            ),
        },
        "missing_inputs": missing_inputs,
        "benchmark": summarize_benchmark(
            benchmark_rows,
            high_offset_hot_cold_benchmark_rows,
        ),
        "external_correctness": summarize_external_correctness(external_correctness),
        "external": summarize_external(
            external_rows,
            external_metadata,
            external_sample_rows,
        ),
        "external_next": summarize_external_next(
            external_next_rows,
            external_next_metadata,
            external_next_sample_rows,
        ),
        "external_throughput": summarize_external_segment_sweep(
            external_throughput_rows,
            external_throughput_metadata,
            external_throughput_sample_rows,
        ),
        "external_segment_sweep": summarize_external_segment_sweep(
            external_segment_sweep_rows,
            external_segment_sweep_metadata,
            external_segment_sweep_sample_rows,
        ),
        "external_mode_sweep": summarize_external_segment_sweep(
            external_mode_sweep_rows,
            external_mode_sweep_metadata,
            external_mode_sweep_sample_rows,
        ),
        "external_mode_confirmation": summarize_external_mode_confirmation(
            external_mode_confirmation
        ),
        "external_high_offset_quick": summarize_external_segment_sweep(
            external_high_offset_quick_rows,
            external_high_offset_quick_metadata,
            external_high_offset_quick_sample_rows,
        ),
        "external_high_offset_tight": summarize_external_segment_sweep(
            external_high_offset_tight_rows,
            external_high_offset_tight_metadata,
            external_high_offset_tight_sample_rows,
        ),
        "external_high_offset_confirmation": summarize_external_mode_confirmation(
            external_high_offset_confirmation
        ),
        "tuning": summarize_tuning(tuning_summary, default_calibration_summary),
        "default_calibration": default_calibration_summary,
    }


def read_csv_if_present(path: Path, missing_inputs: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        missing_inputs.append(str(path))
        return []
    return list(csv.DictReader(path.read_text().splitlines()))


def read_csv_optional(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    return list(csv.DictReader(path.read_text().splitlines()))


def read_json_if_present(path: Path, missing_inputs: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        missing_inputs.append(str(path))
        return None
    return json.loads(path.read_text())


def read_json_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
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


def summarize_benchmark(
    rows: list[dict[str, str]],
    high_offset_hot_cold_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    timing_rows = [row for row in rows if row.get("kind") == "timing"]
    high_offset_hot_cold_timing_rows = [
        row
        for row in high_offset_hot_cold_rows or []
        if row.get("kind") == "timing"
    ]
    primary_counts = [row for row in timing_rows if is_primary_count_row(row.get("name", ""))]
    experimental_counts = [
        row
        for row in timing_rows
        if is_experimental_count_row(row.get("name", ""))
    ]
    fastest_by_workload: dict[str, dict[str, Any]] = {}
    candidates_by_workload: dict[str, list[dict[str, Any]]] = {}
    for row in primary_counts:
        key = benchmark_workload_key(row)
        candidate = benchmark_timing_summary(row)
        candidates_by_workload.setdefault(key, []).append(candidate)
        existing = fastest_by_workload.get(key)
        if existing is None or candidate["best_ms"] < existing["best_ms"]:
            fastest_by_workload[key] = candidate
    experimental_summaries = summarize_experimental_counts(
        experimental_counts,
        fastest_by_workload,
    )
    cold_process_counts = [
        benchmark_timing_summary(row)
        for row in timing_rows
        if row.get("name") in COLD_PROCESS_ROWS
    ]
    high_offset_rows = [
        benchmark_timing_summary(row)
        for row in timing_rows
        if "high_offset" in row.get("name", "")
    ]
    high_offset_hot_cold_summaries = [
        benchmark_timing_summary(row)
        for row in high_offset_hot_cold_timing_rows
        if "high_offset" in row.get("name", "")
        and row.get("name") not in COLD_PROCESS_ROWS
    ]
    high_offset_hot_cold_cold_counts = [
        benchmark_timing_summary(row)
        for row in high_offset_hot_cold_timing_rows
        if row.get("name") in COLD_PROCESS_ROWS
    ]
    if high_offset_hot_cold_summaries or high_offset_hot_cold_cold_counts:
        high_offset_overhead_source = "high_offset_hot_cold"
        high_offset_overhead_rows = high_offset_hot_cold_summaries
        high_offset_overhead_cold_counts = high_offset_hot_cold_cold_counts
    else:
        high_offset_overhead_source = "benchmark"
        high_offset_overhead_rows = high_offset_rows
        high_offset_overhead_cold_counts = cold_process_counts

    return {
        "timing_row_count": len(timing_rows),
        "base_prime_generation": [
            benchmark_timing_summary(row)
            for row in timing_rows
            if row.get("name") == "base_prime_generation"
        ],
        "materialized_generation": [
            benchmark_timing_summary(row)
            for row in timing_rows
            if row.get("name") in MATERIALIZED_GENERATION_ROWS
        ],
        "next_prime_searches": [
            benchmark_timing_summary(row)
            for row in timing_rows
            if row.get("name") in NEXT_PRIME_SEARCH_ROWS
        ],
        "cold_process_counts": cold_process_counts,
        "high_offset_rows": high_offset_rows,
        "high_offset_hot_cold_rows": high_offset_hot_cold_summaries,
        "high_offset_hot_cold_cold_counts": high_offset_hot_cold_cold_counts,
        "high_offset_cold_hot_overhead_source": high_offset_overhead_source,
        "high_offset_cold_hot_overhead": summarize_high_offset_cold_hot_overhead(
            high_offset_overhead_rows,
            high_offset_overhead_cold_counts,
        ),
        "fastest_primary_counts": [
            fastest_by_workload[key] for key in sorted(fastest_by_workload)
        ],
        "primary_candidate_spread": summarize_primary_candidate_spread(
            candidates_by_workload
        ),
        "experimental_counts": experimental_summaries,
    }


def summarize_high_offset_cold_hot_overhead(
    high_offset_rows: list[dict[str, Any]],
    cold_process_counts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows_by_name = {
        row["name"]: row
        for row in [*high_offset_rows, *cold_process_counts]
        if row.get("scope") == "high_offset"
    }
    hot = rows_by_name.get("parallel_high_offset_default_range_count_8t")
    hot_server = rows_by_name.get(
        "hot_cli_count_server_parallel_high_offset_default_range_count_8t"
    )
    cold_cli = rows_by_name.get("cold_cli_parallel_high_offset_default_range_count_8t")
    cold_process = rows_by_name.get("cold_process_parallel_high_offset_segmented_range_count_8t")
    if hot is None or (hot_server is None and cold_cli is None and cold_process is None):
        return []

    hot_ms = float(hot["best_ms"])
    summary = {
        "workload": hot["workload"],
        "result": hot["result"],
        "hot_name": hot["name"],
        "hot_segment_size": hot["segment_size"],
        "hot_best_ms": hot_ms,
        "hot_server_name": hot_server["name"] if hot_server else None,
        "hot_server_segment_size": hot_server["segment_size"] if hot_server else None,
        "hot_server_best_ms": float(hot_server["best_ms"]) if hot_server else None,
        "hot_server_over_hot": (
            float(hot_server["best_ms"]) / hot_ms if hot_server and hot_ms > 0 else None
        ),
        "hot_server_over_cold_cli": (
            float(hot_server["best_ms"]) / float(cold_cli["best_ms"])
            if hot_server and cold_cli and float(cold_cli["best_ms"]) > 0
            else None
        ),
        "cold_cli_name": cold_cli["name"] if cold_cli else None,
        "cold_cli_segment_size": cold_cli["segment_size"] if cold_cli else None,
        "cold_cli_best_ms": float(cold_cli["best_ms"]) if cold_cli else None,
        "cold_cli_over_hot": (
            float(cold_cli["best_ms"]) / hot_ms if cold_cli and hot_ms > 0 else None
        ),
        "cold_cli_extra_ms": (
            float(cold_cli["best_ms"]) - hot_ms if cold_cli is not None else None
        ),
        "cold_process_name": cold_process["name"] if cold_process else None,
        "cold_process_segment_size": cold_process["segment_size"] if cold_process else None,
        "cold_process_best_ms": float(cold_process["best_ms"]) if cold_process else None,
        "cold_process_over_hot": (
            float(cold_process["best_ms"]) / hot_ms if cold_process and hot_ms > 0 else None
        ),
        "cold_process_extra_ms": (
            float(cold_process["best_ms"]) - hot_ms if cold_process is not None else None
        ),
    }
    return [summary]


def is_primary_count_row(name: str) -> bool:
    return (
        name in PRIMARY_COUNT_ROWS
        or name.startswith("parallel_segmented_range_count_")
    )


def is_experimental_count_row(name: str) -> bool:
    return (
        name in EXPERIMENTAL_COUNT_ROWS
        or name.startswith("parallel_balanced_segmented_range_count_")
        or name.startswith("parallel_hybrid_wheel30_mark_range_count_")
        or name.startswith("parallel_wheel30_mark_range_count_")
    )


def benchmark_workload_key(row: dict[str, str]) -> str:
    name = row.get("name", "")
    workload = row.get("workload", "")
    result = row.get("result", "")
    if "high_offset" in name:
        return f"high_offset_span_{workload}_count_{result}"
    return f"prefix_span_{workload}_count_{result}"


def benchmark_timing_summary(row: dict[str, str]) -> dict[str, Any]:
    scope = "high_offset" if "high_offset" in row["name"] else "prefix"
    return {
        "name": row["name"],
        "scope": scope,
        "workload": int(row["workload"]),
        "segment_size": int(row["segment_size"]),
        "result": int(row["result"]),
        "rounds": int(row["rounds"]),
        "best_ms": float(row["best_ms"]),
        "rate_per_second": float(row["rate_per_second"]),
    }


def summarize_experimental_counts(
    rows: list[dict[str, str]],
    fastest_primary_by_workload: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries = []
    for row in rows:
        summary = benchmark_timing_summary(row)
        primary = fastest_primary_by_workload.get(benchmark_workload_key(row))
        if primary is not None:
            summary["primary_best_ms"] = primary["best_ms"]
            summary["slowdown_vs_primary"] = summary["best_ms"] / primary["best_ms"]
        else:
            summary["primary_best_ms"] = None
            summary["slowdown_vs_primary"] = None
        summaries.append(summary)
    return sorted(
        summaries,
        key=lambda row: (
            row["workload"],
            row["name"],
            row["segment_size"],
        ),
    )


def summarize_primary_candidate_spread(
    candidates_by_workload: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    spread = []
    for key in sorted(candidates_by_workload):
        candidates = sorted(
            candidates_by_workload[key],
            key=lambda row: (row["best_ms"], row["name"], row["segment_size"]),
        )
        fastest = candidates[0]
        spread.append(
            {
                "key": key,
                "scope": fastest["scope"],
                "workload": fastest["workload"],
                "result": fastest["result"],
                "candidates": [
                    {
                        **candidate,
                        "slowdown_vs_fastest": candidate["best_ms"] / fastest["best_ms"],
                    }
                    for candidate in candidates
                ],
            }
        )
    return spread


def summarize_external(
    rows: list[dict[str, str]],
    metadata: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    timing_rows = [row for row in rows if row.get("kind") == "timing"]
    sample_stats = summarize_sample_rows(sample_rows or [])
    speedups = [
        external_speedup_summary(row, timing_rows, sample_stats)
        for row in rows
        if row.get("kind") == "speedup"
    ]
    primesieve = [row for row in speedups if row["baseline"] == "external_primesieve_count"]
    primecount = [row for row in speedups if row["baseline"] == "external_primecount_pi_diff"]
    return {
        "speedups": speedups,
        "primesieve_wins": sum(1 for row in primesieve if row["circle_speedup"] >= 1.0),
        "primesieve_median_wins": sum(
            1 for row in primesieve if row["median_circle_speedup"] >= 1.0
        ),
        "primesieve_rows": len(primesieve),
        "primecount_wins": sum(1 for row in primecount if row["circle_speedup"] >= 1.0),
        "primecount_median_wins": sum(
            1 for row in primecount if row["median_circle_speedup"] >= 1.0
        ),
        "primecount_rows": len(primecount),
        "metadata": summarize_external_metadata(metadata),
    }


def summarize_external_next(
    rows: list[dict[str, str]],
    metadata: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    timing_rows = [row for row in rows if row.get("kind") == "timing"]
    sample_stats = summarize_external_next_sample_rows(sample_rows or [])
    speedups = [
        external_next_speedup_summary(row, timing_rows, sample_stats)
        for row in rows
        if row.get("kind") == "speedup"
    ]
    return {
        "available": bool(rows),
        "speedups": speedups,
        "primesieve_rows": len(speedups),
        "primesieve_wins": sum(
            1 for row in speedups if row["circle_speedup"] >= 1.0
        ),
        "primesieve_median_wins": sum(
            1 for row in speedups if row["median_circle_speedup"] >= 1.0
        ),
        "metadata": summarize_external_next_metadata(metadata),
    }


def external_next_speedup_summary(
    row: dict[str, str],
    timing_rows: list[dict[str, str]],
    sample_stats: dict[tuple[int, str, int, int | None, int | None], dict[str, Any]],
) -> dict[str, Any]:
    best_ms = float(row["best_ms"])
    median_ms = parse_optional_float(row.get("median_ms"), best_ms)
    baseline_row = matching_external_next_timing_row(row, timing_rows, row["baseline"])
    baseline_best_ms = (
        float(baseline_row["best_ms"]) if baseline_row is not None else None
    )
    baseline_median_ms = (
        parse_optional_float(baseline_row.get("median_ms"), baseline_best_ms)
        if baseline_row is not None and baseline_best_ms is not None
        else None
    )
    median_speedup = parse_optional_float(row.get("median_speedup"), None)
    if median_speedup is None:
        if baseline_median_ms is not None and median_ms > 0:
            median_speedup = baseline_median_ms / median_ms
        else:
            median_speedup = float(row["best_speedup"])
    circle_sample = sample_stats_for_external_next_speedup(row, sample_stats)
    baseline_sample = (
        sample_stats_for_external_next_timing(baseline_row, sample_stats)
        if baseline_row is not None
        else None
    )
    sample_stability = combined_sample_stability(circle_sample, baseline_sample)
    return {
        "start": int(row["start"]),
        "batch_size": int(row["batch_size"]),
        "name": row["name"],
        "result": int(row["result"]),
        "candidate_count": int(row.get("candidate_count") or 0),
        "rounds": int(row["rounds"]),
        "best_ms": best_ms,
        "median_ms": median_ms,
        "searches_per_second": float(row["searches_per_second"]),
        "median_searches_per_second": float(row["median_searches_per_second"]),
        "circle_threads": parse_optional_int(row.get("threads")),
        "circle_requested_threads": parse_optional_int(row.get("requested_threads")),
        "baseline": row["baseline"],
        "baseline_best_ms": baseline_best_ms,
        "baseline_median_ms": baseline_median_ms,
        "baseline_threads": parse_optional_int(
            baseline_row.get("threads") if baseline_row is not None else None
        ),
        "baseline_requested_threads": parse_optional_int(
            baseline_row.get("requested_threads") if baseline_row is not None else None
        ),
        "circle_speedup": float(row["best_speedup"]),
        "median_circle_speedup": median_speedup,
        "verdict": "circle_faster" if median_speedup >= 1.0 else "baseline_faster",
        "circle_sample": circle_sample,
        "baseline_sample": baseline_sample,
        "sample_stability": sample_stability,
    }


def matching_external_next_timing_row(
    speedup_row: dict[str, str],
    timing_rows: list[dict[str, str]],
    name: str,
) -> dict[str, str] | None:
    for row in timing_rows:
        if (
            row.get("name") == name
            and row.get("start") == speedup_row.get("start")
            and row.get("batch_size") == speedup_row.get("batch_size")
            and row.get("result") == speedup_row.get("result")
        ):
            return row
    return None


def summarize_external_next_sample_rows(
    rows: list[dict[str, str]],
) -> dict[tuple[int, str, int, int | None, int | None], dict[str, Any]]:
    grouped: dict[tuple[int, str, int, int | None, int | None], list[float]] = {}
    for row in rows:
        if row.get("kind") != "sample":
            continue
        key = (
            int(row["start"]),
            row["name"],
            int(row["batch_size"]),
            parse_optional_int(row.get("threads")),
            parse_optional_int(row.get("requested_threads")),
        )
        grouped.setdefault(key, []).append(float(row["elapsed_ms"]))
    return {key: sample_stats(values) for key, values in grouped.items()}


def sample_stats_for_external_next_speedup(
    row: dict[str, str],
    stats: dict[tuple[int, str, int, int | None, int | None], dict[str, Any]],
) -> dict[str, Any] | None:
    key = (
        int(row["start"]),
        row["name"],
        int(row["batch_size"]),
        parse_optional_int(row.get("threads")),
        parse_optional_int(row.get("requested_threads")),
    )
    return stats.get(key)


def sample_stats_for_external_next_timing(
    row: dict[str, str] | None,
    stats: dict[tuple[int, str, int, int | None, int | None], dict[str, Any]],
) -> dict[str, Any] | None:
    if row is None:
        return None
    key = (
        int(row["start"]),
        row["name"],
        int(row["batch_size"]),
        parse_optional_int(row.get("threads")),
        parse_optional_int(row.get("requested_threads")),
    )
    return stats.get(key)


def summarize_external_next_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if metadata is None:
        return {
            "available": False,
            "tools": {},
            "thread_policy": {},
            "starts": [],
            "batch_size": None,
            "required_external_tools": [],
        }
    tools = metadata.get("tools", {})
    return {
        "available": True,
        "started_at_utc": metadata.get("started_at_utc"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rounds": metadata.get("rounds"),
        "row_count": metadata.get("row_count"),
        "batch_size": metadata.get("batch_size"),
        "sample_output": metadata.get("sample_output"),
        "thread_policy": metadata.get("thread_policy", {}),
        "starts": metadata.get("starts", []),
        "required_external_tools": sorted(
            str(tool) for tool in metadata.get("required_external_tools", [])
        ),
        "tools": {
            name: {
                "available": bool(tool.get("available")),
                "path": tool.get("path"),
                "version": first_nonempty_line(tool.get("version")),
            }
            for name, tool in tools.items()
        },
    }


def summarize_external_segment_sweep(
    rows: list[dict[str, str]],
    metadata: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    timing_rows = [row for row in rows if row.get("kind") == "timing"]
    sample_stats = summarize_sample_rows(sample_rows or [])
    speedups = [
        external_speedup_summary(row, timing_rows, sample_stats)
        for row in rows
        if row.get("kind") == "speedup"
    ]
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in speedups:
        grouped.setdefault((row["low"], row["high"], row["baseline"]), []).append(row)

    best_by_range_baseline = []
    candidate_spread = []
    for (low, high, baseline), candidates in sorted(grouped.items()):
        ordered = sorted(
            candidates,
            key=lambda row: (
                -row["median_circle_speedup"],
                row["median_ms"],
                -row["circle_speedup"],
                row["best_ms"],
                row["name"],
                row["segment_size"],
                row["circle_threads"] or 0,
            ),
        )
        best = ordered[0]
        best_by_range_baseline.append(best)
        candidate_spread.append(
            {
                "low": low,
                "high": high,
                "span": best["span"],
                "baseline": baseline,
                "candidates": ordered,
            }
        )

    return {
        "available": bool(rows),
        "speedups": speedups,
        "best_by_range_baseline": best_by_range_baseline,
        "candidate_spread": candidate_spread,
        "metadata": summarize_external_sweep_metadata(metadata),
    }


def summarize_external_sweep_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    summary = summarize_external_metadata(metadata)
    if metadata is not None:
        summary["requested_segment_sizes"] = metadata.get("requested_segment_sizes", [])
    else:
        summary["requested_segment_sizes"] = []
    return summary


def summarize_external_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if metadata is None:
        return {
            "available": False,
            "tools": {},
            "thread_policy": {},
            "ranges": [],
            "circle_count_modes": [],
            "required_external_tools": [],
        }
    tools = metadata.get("tools", {})
    return {
        "available": True,
        "started_at_utc": metadata.get("started_at_utc"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rounds": metadata.get("rounds"),
        "row_count": metadata.get("row_count"),
        "interleaved": bool(metadata.get("interleaved")),
        "sample_output": metadata.get("sample_output"),
        "thread_policy": metadata.get("thread_policy", {}),
        "circle_count_modes": metadata.get("circle_count_modes", []),
        "ranges": metadata.get("ranges", []),
        "required_external_tools": sorted(
            str(tool) for tool in metadata.get("required_external_tools", [])
        ),
        "tools": {
            name: {
                "available": bool(tool.get("available")),
                "path": tool.get("path"),
                "version": first_nonempty_line(tool.get("version")),
            }
            for name, tool in tools.items()
        },
    }


def summarize_external_correctness(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {
            "available": False,
            "passes": False,
            "check_count": 0,
            "failure_count": 0,
            "ranges": [],
            "circle_count_modes": [],
            "required_external_tools": [],
            "missing_external_tools": [],
            "thread_policy": {},
            "tools": {},
            "failures": [],
            "max_checked_high": None,
        }
    failures = [
        check
        for check in summary.get("checks", [])
        if not bool(check.get("passes"))
    ]
    enumeration_failures = [
        check
        for check in summary.get("enumeration_checks", [])
        if not bool(check.get("passes"))
    ]
    next_failures = [
        check
        for check in summary.get("next_checks", [])
        if not bool(check.get("passes"))
    ]
    return {
        "available": True,
        "started_at_utc": summary.get("started_at_utc"),
        "finished_at_utc": summary.get("finished_at_utc"),
        "passes": bool(summary.get("passes")),
        "check_count": int(summary.get("check_count") or 0),
        "count_check_count": int(
            summary.get("count_check_count") or len(summary.get("checks", []))
        ),
        "enumeration_check_count": int(
            summary.get("enumeration_check_count")
            or len(summary.get("enumeration_checks", []))
        ),
        "next_check_count": int(
            summary.get("next_check_count") or len(summary.get("next_checks", []))
        ),
        "failure_count": int(
            summary.get("failure_count")
            or len(failures) + len(enumeration_failures) + len(next_failures)
        ),
        "count_failure_count": int(summary.get("count_failure_count") or len(failures)),
        "enumeration_failure_count": int(
            summary.get("enumeration_failure_count") or len(enumeration_failures)
        ),
        "next_failure_count": int(summary.get("next_failure_count") or len(next_failures)),
        "ranges": summary.get("ranges", []),
        "enumeration_ranges": summary.get("enumeration_ranges", []),
        "next_starts": summary.get("next_starts", []),
        "max_checked_high": max_checked_high(
            summary.get("ranges", []),
            summary.get("enumeration_ranges", []),
        ),
        "circle_count_modes": summary.get("circle_count_modes", []),
        "requested_segment_sizes": summary.get("requested_segment_sizes", []),
        "required_external_tools": sorted(
            str(tool) for tool in summary.get("required_external_tools", [])
        ),
        "missing_external_tools": sorted(
            str(tool) for tool in summary.get("missing_external_tools", [])
        ),
        "thread_policy": summary.get("thread_policy", {}),
        "tools": {
            name: {
                "available": bool(tool.get("available")),
                "path": tool.get("path"),
                "version": first_nonempty_line(tool.get("version")),
            }
            for name, tool in summary.get("tools", {}).items()
        },
        "failures": failures,
        "enumeration_failures": enumeration_failures,
    }


def max_checked_high(*range_groups: Any) -> int | None:
    highs = []
    for ranges in range_groups:
        if not isinstance(ranges, list):
            continue
        for row in ranges:
            if isinstance(row, dict) and isinstance(row.get("high"), int):
                highs.append(row["high"])
    return max(highs) if highs else None


def first_nonempty_line(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return None


def external_speedup_summary(
    row: dict[str, str],
    timing_rows: list[dict[str, str]],
    sample_stats: dict[tuple[int, int, str, int, int | None, int | None], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    speedup = float(row["best_speedup"])
    best_ms = float(row["best_ms"])
    median_ms = parse_optional_float(row.get("median_ms"), best_ms)
    baseline_row = matching_timing_row(row, timing_rows, row["baseline"])
    baseline_best_ms = (
        float(baseline_row["best_ms"]) if baseline_row is not None else None
    )
    baseline_median_ms = (
        parse_optional_float(baseline_row.get("median_ms"), baseline_best_ms)
        if baseline_row is not None and baseline_best_ms is not None
        else None
    )
    median_speedup = parse_optional_float(row.get("median_speedup"), None)
    if median_speedup is None:
        if baseline_median_ms is not None and median_ms > 0:
            median_speedup = baseline_median_ms / median_ms
        else:
            median_speedup = speedup
    circle_sample_stats = sample_stats_for_speedup(row, sample_stats)
    baseline_sample_stats = (
        sample_stats_for_timing(baseline_row, sample_stats)
        if baseline_row is not None
        else None
    )
    sample_stability = combined_sample_stability(
        circle_sample_stats,
        baseline_sample_stats,
    )
    return {
        "low": int(row["low"]),
        "high": int(row["high"]),
        "span": int(row["span"]),
        "name": row["name"],
        "count_mode": row.get("count_mode") or None,
        "segment_size": int(row["segment_size"]),
        "result": int(row["result"]),
        "rounds": int(row["rounds"]),
        "best_ms": best_ms,
        "median_ms": median_ms,
        "circle_threads": parse_optional_int(row.get("threads")),
        "circle_requested_threads": parse_optional_int(row.get("requested_threads")),
        "baseline": row["baseline"],
        "baseline_best_ms": baseline_best_ms,
        "baseline_median_ms": baseline_median_ms,
        "baseline_threads": parse_optional_int(
            baseline_row.get("threads") if baseline_row is not None else None
        ),
        "baseline_requested_threads": parse_optional_int(
            baseline_row.get("requested_threads") if baseline_row is not None else None
        ),
        "circle_speedup": speedup,
        "median_circle_speedup": median_speedup,
        "verdict": "circle_faster" if median_speedup >= 1.0 else "baseline_faster",
        "circle_sample": circle_sample_stats,
        "baseline_sample": baseline_sample_stats,
        "sample_stability": sample_stability,
    }


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
    return {
        "sample_count": len(ordered),
        "min_ms": min_ms,
        "median_ms": median_ms,
        "max_ms": max_ms,
        "max_over_median": max_over_median,
        "stability": (
            "noisy"
            if max_over_median is not None
            and max_over_median > SAMPLE_NOISY_MAX_OVER_MEDIAN
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


def parse_optional_int(raw: str | None) -> int | None:
    if raw in (None, ""):
        return None
    return int(raw)


def parse_optional_float(raw: str | None, fallback: float | None) -> float | None:
    if raw in (None, ""):
        return fallback
    return float(raw)


def format_optional_ms(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def format_optional_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}x"


def summarize_tuning(
    summary: dict[str, Any] | None,
    default_calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if summary is None:
        return {"available": False, "best_by_range": [], "default_alignment": []}
    best_by_range = []
    for row in summary.get("best_by_range", []):
        best = row["best"]
        best_by_range.append(
            {
                "low": int(row["low"]),
                "high": int(row["high"]),
                "span": int(row["span"]),
                "samples": int(row["samples"]),
                "count_mode": str(best.get("count_mode", "segmented")),
                "segment_size": int(best["segment_size"]),
                "requested_threads": int(best["requested_threads"]),
                "threads": int(best["threads"]),
                "best_ms": float(best["best_ms"]),
                "median_ms": float(best.get("median_ms", best["best_ms"])),
                "rate_per_second": float(best["rate_per_second"]),
                "median_rate_per_second": float(
                    best.get("median_rate_per_second", best["rate_per_second"])
                ),
                "count": int(best["count"]),
            }
        )
    return {
        "available": True,
        "started_at_utc": summary.get("started_at_utc"),
        "finished_at_utc": summary.get("finished_at_utc"),
        "elapsed_seconds": summary.get("elapsed_seconds"),
        "rounds": summary.get("rounds"),
        "sample_count": summary.get("sample_count"),
        "best_by_range": best_by_range,
        "default_alignment": summarize_default_alignment(
            summary.get("default_alignment", []),
            default_calibration,
        ),
    }


def summarize_default_alignment(
    rows: list[dict[str, Any]],
    default_calibration: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    current_defaults = current_default_recommendations_by_range(default_calibration)
    aligned_rows = []
    for row in rows:
        low = int(row["low"])
        high = int(row["high"])
        best_requested_threads = int(row["best_requested_threads"])
        artifact_default_count_mode = str(row.get("default_count_mode", "segmented"))
        artifact_default_segment_size = int(row["default_segment_size"])
        artifact_default_threads = int(row["default_threads"])
        artifact_default_requested_threads = int(row["default_requested_threads"])
        current_default = current_defaults.get((low, high, best_requested_threads))
        default_source = "tuning_artifact"
        default_count_mode = artifact_default_count_mode
        default_segment_size = artifact_default_segment_size
        default_threads = artifact_default_threads
        default_requested_threads = artifact_default_requested_threads
        if current_default is not None:
            default_source = "current_calibration"
            default_count_mode = current_default["count_mode"]
            default_segment_size = current_default["segment_size"]
            default_threads = current_default["threads"]
            default_requested_threads = current_default["requested_threads"]
        best_count_mode = str(row.get("best_count_mode", "segmented"))
        best_segment_size = int(row["best_segment_size"])
        best_threads = int(row["best_threads"])
        artifact_default_stale = (
            artifact_default_count_mode != default_count_mode
            or artifact_default_segment_size != default_segment_size
            or artifact_default_threads != default_threads
            or artifact_default_requested_threads != default_requested_threads
        )
        aligned_rows.append(
            {
                "low": low,
                "high": high,
                "span": int(row["span"]),
                "count": int(row["count"]),
                "best_count_mode": best_count_mode,
                "best_segment_size": best_segment_size,
                "best_threads": best_threads,
                "best_requested_threads": best_requested_threads,
                "best_ms": float(row["best_ms"]),
                "median_ms": float(row.get("median_ms", row["best_ms"])),
                "default_count_mode": default_count_mode,
                "default_segment_size": default_segment_size,
                "default_threads": default_threads,
                "default_requested_threads": default_requested_threads,
                "default_source": default_source,
                "artifact_default_count_mode": artifact_default_count_mode,
                "artifact_default_segment_size": artifact_default_segment_size,
                "artifact_default_threads": artifact_default_threads,
                "artifact_default_requested_threads": artifact_default_requested_threads,
                "artifact_default_stale": artifact_default_stale,
                "count_mode_aligned": best_count_mode == default_count_mode,
                "segment_size_aligned": best_segment_size == default_segment_size,
                "threads_aligned": best_threads == default_threads,
            }
        )
    return aligned_rows


def current_default_recommendations_by_range(
    default_calibration: dict[str, Any] | None,
) -> dict[tuple[int, int, int], dict[str, Any]]:
    if not default_calibration or not default_calibration.get("available"):
        return {}
    current_defaults = {}
    for row in default_calibration.get("recommendations", []):
        current_mode = row.get("current_default_count_mode")
        current_segment = row.get("current_default_segment_size")
        current_threads = row.get("current_default_threads")
        current_requested_threads = row.get("current_default_requested_threads")
        if (
            current_mode is None
            or current_segment is None
            or current_threads is None
            or current_requested_threads is None
        ):
            continue
        key = (int(row["low"]), int(row["high"]), int(current_requested_threads))
        current_defaults[key] = {
            "count_mode": str(current_mode),
            "segment_size": int(current_segment),
            "threads": int(current_threads),
            "requested_threads": int(current_requested_threads),
        }
    return current_defaults


def summarize_default_calibration(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {"available": False, "recommendations": []}
    return {
        "available": True,
        "generated_at_utc": summary.get("generated_at_utc"),
        "tolerance": summary.get("tolerance"),
        "recommendation_count": summary.get("recommendation_count", 0),
        "aligned_count": summary.get("aligned_count", 0),
        "within_tolerance_count": summary.get("within_tolerance_count", 0),
        "drift_count": summary.get("drift_count", 0),
        "noisy_drift_count": summary.get("noisy_drift_count", 0),
        "unconfirmed_mode_drift_count": summary.get("unconfirmed_mode_drift_count", 0),
        "missing_evidence_count": summary.get("missing_evidence_count", 0),
        "failing_recommendation_count": summary.get("failing_recommendation_count", 0),
        "recommendations": [
            {
                "source": row.get("source"),
                "baseline": row.get("baseline"),
                "low": int(row["low"]),
                "high": int(row["high"]),
                "span": int(row["span"]),
                "selected_count_mode": str(row.get("selected_count_mode", "segmented")),
                "selected_segment_size": int(row["selected_segment_size"]),
                "selected_threads": int(row["selected_threads"]),
                "selected_requested_threads": int(row["selected_requested_threads"]),
                "selected_median_ms": float(row["selected_median_ms"]),
                "selected_sample_stability": row.get("selected_sample_stability"),
                "selected_effective_sample_stability": row.get(
                    "selected_effective_sample_stability"
                ),
                "selected_circle_sample": row.get("selected_circle_sample"),
                "selected_baseline_sample": row.get("selected_baseline_sample"),
                "selected_mode_confirmation_status": row.get(
                    "selected_mode_confirmation_status"
                ),
                "selected_mode_confirmation_count": row.get(
                    "selected_mode_confirmation_count"
                ),
                "selected_mode_confirmation_min": row.get(
                    "selected_mode_confirmation_min"
                ),
                "current_default_count_mode": row.get("current_default_count_mode"),
                "current_default_segment_size": row.get("current_default_segment_size"),
                "current_default_threads": row.get("current_default_threads"),
                "current_default_requested_threads": row.get("current_default_requested_threads"),
                "default_over_selected": row.get("default_over_selected"),
                "status": row.get("status"),
                "passes": bool(row.get("passes")),
            }
            for row in summary.get("recommendations", [])
        ],
    }


def summarize_external_mode_confirmation(summary: dict[str, Any] | None) -> dict[str, Any]:
    if summary is None:
        return {"available": False, "winners": []}
    return {
        "available": True,
        "generated_at_utc": summary.get("generated_at_utc"),
        "min_confirmations": summary.get("min_confirmations"),
        "require_stable_samples": summary.get("require_stable_samples"),
        "observed_group_count": summary.get("observed_group_count", 0),
        "confirmed_count": summary.get("confirmed_count", 0),
        "unconfirmed_count": summary.get("unconfirmed_count", 0),
        "winners": [
            {
                "low": int(row["low"]),
                "high": int(row["high"]),
                "baseline": row.get("baseline"),
                "count_mode": row.get("count_mode"),
                "segment_size": int(row["segment_size"]),
                "threads": int(row["threads"]),
                "requested_threads": int(row["requested_threads"]),
                "confirmation_count": int(row["confirmation_count"]),
                "observed_count": int(row["observed_count"]),
                "stable_observed_count": int(row["stable_observed_count"]),
                "status": row.get("status"),
                "median_ms_values": [
                    float(value) for value in row.get("median_ms_values", [])
                ],
            }
            for row in summary.get("winners", [])
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Prime Engine Report",
        "",
        f"Generated: `{report['generated_at_utc']}`",
        "",
    ]
    if report["missing_inputs"]:
        lines.append("## Missing Inputs")
        lines.append("")
        for path in report["missing_inputs"]:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.extend(render_external_correctness_markdown(report["external_correctness"]))
    lines.extend(render_external_markdown(report["external"]))
    lines.extend(render_external_next_markdown(report["external_next"]))
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_quick"],
            title="High-Offset Quick Scorecard",
            missing_message="No high-offset quick scorecard artifact was available.",
            spread_label="High-offset quick candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_tight"],
            title="High-Offset Tight Scorecard",
            missing_message="No high-offset tight scorecard artifact was available.",
            spread_label="High-offset tight candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_mode_confirmation_markdown(
            report["external_high_offset_confirmation"],
            title="High-Offset Confirmation",
            missing_message="No repeated high-offset confirmation artifact was available.",
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_mode_sweep"],
            title="External Count Mode Sweep",
            missing_message="No external count-mode sweep artifact was available.",
            spread_label="Count mode candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(render_external_mode_confirmation_markdown(report["external_mode_confirmation"]))
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_throughput"],
            title="External Throughput",
            missing_message="No external throughput artifact was available.",
            spread_label="Throughput segment candidate spread:",
        )
    )
    lines.extend(render_external_segment_sweep_markdown(report["external_segment_sweep"]))
    lines.extend(render_default_calibration_markdown(report["default_calibration"]))
    lines.extend(render_benchmark_markdown(report["benchmark"]))
    lines.extend(render_tuning_markdown(report["tuning"]))
    return "\n".join(lines).rstrip() + "\n"


def render_external_correctness_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## External Correctness", ""]
    if not summary["available"]:
        lines.append("No external correctness artifact was available.")
        lines.append("")
        return lines

    verdict = "passed" if summary["passes"] else "failed"
    lines.append(
        f"Status: `{verdict}`; checks: `{summary['check_count']}`; "
        f"failures: `{summary['failure_count']}`."
    )
    if (
        summary.get("count_check_count")
        or summary.get("enumeration_check_count")
        or summary.get("next_check_count")
    ):
        lines.append(
            f"Count checks: `{summary.get('count_check_count', 0)}`; "
            f"enumeration checks: `{summary.get('enumeration_check_count', 0)}`; "
            f"next-prime checks: `{summary.get('next_check_count', 0)}`."
        )
    required_tools = summary.get("required_external_tools") or []
    if required_tools:
        formatted = ", ".join(f"`{tool}`" for tool in required_tools)
        lines.append(f"Required external controls: {formatted}.")
    missing_tools = summary.get("missing_external_tools") or []
    if missing_tools:
        formatted = ", ".join(f"`{tool}`" for tool in missing_tools)
        lines.append(f"Missing external controls: {formatted}.")
    count_modes = summary.get("circle_count_modes") or []
    if count_modes:
        formatted = ", ".join(f"`{mode}`" for mode in count_modes)
        lines.append(f"Circle count modes checked: {formatted}.")
    requested_sizes = summary.get("requested_segment_sizes") or []
    if requested_sizes:
        formatted = ", ".join(f"`{size}`" for size in requested_sizes)
        lines.append(f"Requested Circle segment sizes: {formatted}.")
    thread_policy = summary.get("thread_policy", {})
    circle_threads = thread_policy.get("circle_requested_threads")
    external_threads = thread_policy.get("external_requested_threads")
    if circle_threads is not None or external_threads is not None:
        lines.append(
            "Requested threads: "
            f"Circle `{circle_threads}`, external `{external_threads}`."
        )
    if summary.get("ranges"):
        lines.append(f"Count ranges checked: `{len(summary['ranges'])}`.")
    if summary.get("enumeration_ranges"):
        lines.append(
            f"Enumeration ranges checked: `{len(summary['enumeration_ranges'])}`."
        )
    if summary.get("max_checked_high") is not None:
        lines.append(f"Largest checked high: `{summary['max_checked_high']}`.")
    if summary.get("failures"):
        lines.append("")
        lines.append("Count failures:")
        lines.append("")
        lines.extend(
            [
                "| Range | Mode | Segment | Circle Count | External Counts |",
                "| --- | --- | ---: | ---: | --- |",
            ]
        )
        for row in summary["failures"]:
            external_counts = ", ".join(
                f"`{name}`={count}" for name, count in row.get("external_counts", {}).items()
            )
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['count_mode']}` | "
                f"{row['segment_size']} | {row['circle_count']} | {external_counts} |"
            )
    if summary.get("enumeration_failures"):
        lines.append("")
        lines.append("Enumeration failures:")
        lines.append("")
        lines.extend(
            [
                "| Range | Segment | Circle Count | External Count | First Mismatch |",
                "| --- | ---: | ---: | ---: | --- |",
            ]
        )
        for row in summary["enumeration_failures"]:
            mismatch = row.get("first_mismatch")
            mismatch_text = "n/a" if mismatch is None else json.dumps(mismatch, sort_keys=True)
            lines.append(
                f"| [{row['low']}, {row['high']}) | {row['segment_size']} | "
                f"{row['circle_count']} | {row['external_count']} | "
                f"`{mismatch_text}` |"
            )
    lines.append("")
    return lines


def render_external_markdown(summary: dict[str, Any]) -> list[str]:
    lines = [
        "## External Controls",
        "",
        (
            f"- `primesieve`: Circle faster on {summary['primesieve_wins']}/"
            f"{summary['primesieve_rows']} rows by best time; median faster on "
            f"{summary.get('primesieve_median_wins', summary['primesieve_wins'])}/"
            f"{summary['primesieve_rows']} rows."
        ),
        (
            f"- `primecount`: Circle faster on {summary['primecount_wins']}/"
            f"{summary['primecount_rows']} rows by best time; median faster on "
            f"{summary.get('primecount_median_wins', summary['primecount_wins'])}/"
            f"{summary['primecount_rows']} rows."
        ),
        "",
    ]
    metadata = summary.get("metadata", {})
    if metadata.get("available"):
        lines.extend(render_external_metadata_markdown(metadata))
    if summary["speedups"]:
        lines.extend(
            [
                "| Range | Circle Row | Baseline | Best Speedup | Median Speedup | Samples | Verdict |",
                "| --- | --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for row in summary["speedups"]:
            circle_thread_note = thread_note(
                row.get("circle_threads"),
                row.get("circle_requested_threads"),
            )
            baseline_thread_note = thread_note(
                row.get("baseline_threads"),
                row.get("baseline_requested_threads"),
            )
            lines.append(
                f"| [{row['low']}, {row['high']}) | {circle_row_label(row)}{circle_thread_note} | "
                f"`{row['baseline']}`{baseline_thread_note} | {row['circle_speedup']:.3f} | "
                f"{row['median_circle_speedup']:.3f} | "
                f"{sample_stability_text(row)} | "
                f"{row['verdict']} |"
            )
        lines.append("")
    return lines


def render_external_metadata_markdown(metadata: dict[str, Any]) -> list[str]:
    lines = ["Tool metadata:"]
    for name in ["circle_prime", "primesieve", "primecount"]:
        tool = metadata.get("tools", {}).get(name, {})
        available = tool.get("available")
        version = tool.get("version") or "version unavailable"
        path = tool.get("path") or "path unavailable"
        status = version if available else "not installed"
        lines.append(f"- `{name}`: {status} (`{path}`)")
    thread_policy = metadata.get("thread_policy", {})
    circle_threads = thread_policy.get("circle_requested_threads")
    external_threads = thread_policy.get("external_requested_threads")
    if circle_threads is not None or external_threads is not None:
        lines.append(
            "- requested threads: "
            f"Circle `{circle_threads}`, external `{external_threads}` "
            "(`0` means tool default/all cores)."
        )
    count_modes = metadata.get("circle_count_modes") or []
    if count_modes:
        formatted = ", ".join(f"`{mode}`" for mode in count_modes)
        lines.append(f"- Circle count modes: {formatted}.")
    required_tools = metadata.get("required_external_tools") or []
    if required_tools:
        formatted = ", ".join(f"`{tool}`" for tool in required_tools)
        lines.append(f"- required external controls: {formatted}.")
    if metadata.get("interleaved"):
        lines.append("- timing policy: interleaved round-robin samples.")
    if metadata.get("sample_output"):
        lines.append(f"- per-round samples: `{metadata['sample_output']}`.")
    lines.append("")
    return lines


def render_external_next_markdown(summary: dict[str, Any]) -> list[str]:
    lines = [
        "## External Next-Prime Search",
        "",
    ]
    if not summary["available"]:
        lines.append("No external next-prime benchmark artifact was available.")
        lines.append("")
        return lines

    lines.append(
        f"- `primesieve --nth-prime`: Circle faster on "
        f"{summary['primesieve_wins']}/{summary['primesieve_rows']} rows by best time; "
        f"median faster on {summary['primesieve_median_wins']}/"
        f"{summary['primesieve_rows']} rows."
    )
    lines.append("")
    metadata = summary.get("metadata", {})
    if metadata.get("available"):
        lines.extend(render_external_next_metadata_markdown(metadata))
    if summary["speedups"]:
        lines.extend(
            [
                "| Start | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in summary["speedups"]:
            baseline_ms = (
                "n/a"
                if row["baseline_best_ms"] is None
                else f"{row['baseline_best_ms']:.3f}"
            )
            lines.append(
                f"| {row['start']} | {row['result']} | {row['candidate_count']} | "
                f"{row['batch_size']} | {row['best_ms']:.3f} | {baseline_ms} | "
                f"{row['circle_speedup']:.3f} | {row['median_circle_speedup']:.3f} | "
                f"{sample_stability_text(row)} | {row['verdict']} |"
            )
        lines.append("")
    return lines


def render_external_next_metadata_markdown(metadata: dict[str, Any]) -> list[str]:
    lines = ["Tool metadata:"]
    for name in ["circle_prime", "primesieve"]:
        tool = metadata.get("tools", {}).get(name, {})
        available = tool.get("available")
        version = tool.get("version") or "version unavailable"
        path = tool.get("path") or "path unavailable"
        status = version if available else "not installed"
        lines.append(f"- `{name}`: {status} (`{path}`)")
    thread_policy = metadata.get("thread_policy", {})
    external_threads = thread_policy.get("external_requested_threads")
    if external_threads is not None:
        lines.append(
            "- requested threads: "
            f"Circle `1`, external `{external_threads}` "
            "(`0` means tool default/all cores)."
        )
    starts = metadata.get("starts") or []
    if starts:
        formatted = ", ".join(f"`{start}`" for start in starts)
        lines.append(f"- next-prime starts: {formatted}.")
    if metadata.get("batch_size") is not None:
        lines.append(f"- repeated searches per sample: `{metadata['batch_size']}`.")
    required_tools = metadata.get("required_external_tools") or []
    if required_tools:
        formatted = ", ".join(f"`{tool}`" for tool in required_tools)
        lines.append(f"- required external controls: {formatted}.")
    if metadata.get("sample_output"):
        lines.append(f"- per-round samples: `{metadata['sample_output']}`.")
    lines.append("")
    return lines


def circle_row_label(row: dict[str, Any]) -> str:
    label = f"`{row['name']}`"
    count_mode = row.get("count_mode")
    if count_mode:
        label += f"<br>mode: `{count_mode}`"
    return label


def render_external_mode_confirmation_markdown(
    summary: dict[str, Any],
    *,
    title: str = "External Mode Confirmation",
    missing_message: str = "No repeated external mode-confirmation artifact was available.",
) -> list[str]:
    lines = [f"## {title}", ""]
    if not summary["available"]:
        lines.append(missing_message)
        lines.append("")
        return lines

    lines.append(
        f"Observed groups: `{summary['observed_group_count']}`; "
        f"confirmed: `{summary['confirmed_count']}`; "
        f"unconfirmed: `{summary['unconfirmed_count']}`."
    )
    if summary.get("min_confirmations") is not None:
        lines.append(
            f"Minimum confirmations: `{summary['min_confirmations']}`; "
            f"requires stable samples: `{summary.get('require_stable_samples')}`."
        )
    lines.append("")
    if summary["winners"]:
        lines.extend(
            [
                "| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Status |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in summary["winners"]:
            medians = ", ".join(f"{value:.3f}" for value in row["median_ms_values"])
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                f"`{row['count_mode']}` | {row['segment_size']} | "
                f"{thread_text(row.get('threads'), row.get('requested_threads'))} | "
                f"{row['confirmation_count']}/{summary['min_confirmations']} | "
                f"{row['stable_observed_count']}/{row['observed_count']} | "
                f"{medians} | `{row['status']}` |"
            )
        lines.append("")
    return lines


def render_external_segment_sweep_markdown(
    summary: dict[str, Any],
    *,
    title: str = "External Segment Sweep",
    missing_message: str = "No external segment sweep artifact was available.",
    spread_label: str = "Segment candidate spread:",
    include_circle_row: bool = False,
) -> list[str]:
    lines = [f"## {title}", ""]
    if not summary["available"]:
        lines.append(missing_message)
        lines.append("")
        return lines

    metadata = summary.get("metadata", {})
    if metadata.get("available"):
        requested_sizes = metadata.get("requested_segment_sizes") or []
        if requested_sizes:
            lines.append(
                "Requested Circle segment sizes: "
                + ", ".join(f"`{size}`" for size in requested_sizes)
                + "."
            )
        count_modes = metadata.get("circle_count_modes") or []
        if count_modes:
            lines.append(
                "Circle count modes: "
                + ", ".join(f"`{mode}`" for mode in count_modes)
                + "."
            )
        if metadata.get("rounds") is not None:
            lines.append(f"Rounds per row: `{metadata['rounds']}`.")
        lines.append("")

    if summary["best_by_range_baseline"]:
        if include_circle_row:
            lines.extend(
                [
                    "| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |",
                    "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
                ]
            )
        else:
            lines.extend(
                [
                    "| Range | Baseline | Best Circle Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |",
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
                ]
            )
        for row in summary["best_by_range_baseline"]:
            prefix = f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
            if include_circle_row:
                prefix += f"{circle_row_label(row)} | {row['segment_size']} | "
            else:
                prefix += f"{row['segment_size']} | "
            lines.append(
                prefix
                + f"{thread_text(row.get('circle_threads'), row.get('circle_requested_threads'))} | "
                + f"{row['best_ms']:.3f} | {row['median_ms']:.3f} | "
                + f"{row['circle_speedup']:.3f} | {row['median_circle_speedup']:.3f} | "
                + f"{sample_stability_text(row)} | "
                + f"{row['verdict']} |"
            )
        lines.append("")

    if summary["candidate_spread"]:
        lines.extend([spread_label, ""])
        if include_circle_row:
            lines.extend(
                [
                    "| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |",
                    "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
                ]
            )
        else:
            lines.extend(
                [
                    "| Range | Baseline | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |",
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
                ]
            )
        for group in summary["candidate_spread"]:
            for row in group["candidates"][:5]:
                prefix = f"| [{group['low']}, {group['high']}) | `{group['baseline']}` | "
                if include_circle_row:
                    prefix += f"{circle_row_label(row)} | {row['segment_size']} | "
                else:
                    prefix += f"{row['segment_size']} | "
                lines.append(
                    prefix
                    + f"{thread_text(row.get('circle_threads'), row.get('circle_requested_threads'))} | "
                    + f"{row['best_ms']:.3f} | {row['median_ms']:.3f} | "
                    + f"{row['circle_speedup']:.3f} | {row['median_circle_speedup']:.3f} | "
                    + f"{sample_stability_text(row)} |"
                )
        lines.append("")
    return lines


def sample_stability_text(row: dict[str, Any]) -> str:
    stability = row.get("sample_stability") or "unknown"
    circle = row.get("circle_sample")
    baseline = row.get("baseline_sample")
    if circle is None and baseline is None:
        return stability
    parts = [stability]
    if circle is not None:
        parts.append(f"C {sample_spread_text(circle)}")
    if baseline is not None:
        parts.append(f"B {sample_spread_text(baseline)}")
    return "<br>".join(parts)


def sample_spread_text(stats: dict[str, Any]) -> str:
    ratio = stats.get("max_over_median")
    count = stats.get("sample_count")
    if ratio is None:
        return f"n={count}"
    return f"n={count}, max/med={ratio:.2f}"


def render_default_calibration_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## Default Calibration", ""]
    if not summary["available"]:
        lines.append("No default calibration artifact was available.")
        lines.append("")
        return lines

    lines.append(
        f"Recommendations: `{summary['recommendation_count']}`; "
        f"aligned: `{summary['aligned_count']}`; "
        f"within tolerance: `{summary['within_tolerance_count']}`; "
        f"drift: `{summary['drift_count']}`; "
        f"noisy drift: `{summary['noisy_drift_count']}`; "
        f"unconfirmed mode drift: `{summary.get('unconfirmed_mode_drift_count', 0)}`; "
        f"missing evidence: `{summary['missing_evidence_count']}`."
    )
    if summary.get("tolerance") is not None:
        lines.append(f"Tolerance: `{float(summary['tolerance']):.3f}` median slowdown.")
    lines.append("")
    if summary["recommendations"]:
        lines.extend(
            [
                "| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |",
                "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in summary["recommendations"]:
            baseline = row.get("baseline") or "n/a"
            default_mode = row.get("current_default_count_mode")
            default_mode_text = "n/a" if default_mode is None else f"`{default_mode}`"
            default_segment = row.get("current_default_segment_size")
            default_segment_text = "n/a" if default_segment is None else str(default_segment)
            ratio = row.get("default_over_selected")
            ratio_text = "n/a" if ratio is None else f"{float(ratio):.3f}x"
            default_threads = thread_text(
                row.get("current_default_threads"),
                row.get("current_default_requested_threads"),
            )
            selected_threads = thread_text(
                row.get("selected_threads"),
                row.get("selected_requested_threads"),
            )
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['source']}` | `{baseline}` | "
                f"`{row['selected_count_mode']}` | {default_mode_text} | "
                f"{row['selected_segment_size']} | {default_segment_text} | "
                f"{selected_threads} -> {default_threads} | "
                f"{row['selected_median_ms']:.3f} | "
                f"{calibration_sample_stability_text(row)} | {ratio_text} | "
                f"`{row['status']}` |"
            )
        lines.append("")
    return lines


def calibration_sample_stability_text(row: dict[str, Any]) -> str:
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


def thread_text(threads: int | None, requested_threads: int | None) -> str:
    if threads is None and requested_threads is None:
        return "n/a"
    if requested_threads in (None, 0):
        return "tool default"
    if threads is None or threads == requested_threads:
        return str(requested_threads)
    return f"{threads}/{requested_threads}"


def thread_note(threads: int | None, requested_threads: int | None) -> str:
    if threads is None and requested_threads is None:
        return ""
    if requested_threads in (None, 0):
        return " (threads: tool default)"
    if threads is None or threads == requested_threads:
        return f" (threads: {requested_threads})"
    return f" (threads: {threads}/{requested_threads})"


def render_benchmark_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## Release Benchmark", ""]
    if summary["fastest_primary_counts"]:
        lines.extend(
            [
                "| Scope | Workload | Row | Segment | Best ms | Count |",
                "| --- | ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["fastest_primary_counts"]:
            lines.append(
                f"| {row['scope']} | {row['workload']} | `{row['name']}` | "
                f"{row['segment_size']} | {row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["base_prime_generation"]:
        lines.append("Base-prime generation rows:")
        for row in summary["base_prime_generation"]:
            lines.append(f"- limit `{row['workload']}`: {row['best_ms']:.3f}ms")
        lines.append("")
    if summary["cold_process_counts"]:
        lines.extend(
            [
                "Cold process count rows:",
                "",
                "| Scope | Workload | Row | Segment | Best ms | Count |",
                "| --- | ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["cold_process_counts"]:
            lines.append(
                f"| {row['scope']} | {row['workload']} | `{row['name']}` | "
                f"{row['segment_size']} | {row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["high_offset_rows"]:
        lines.extend(
            [
                "High-offset benchmark rows:",
                "",
                "| Workload | Row | Segment | Best ms | Count |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["high_offset_rows"]:
            lines.append(
                f"| {row['workload']} | `{row['name']}` | {row['segment_size']} | "
                f"{row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["high_offset_hot_cold_rows"] or summary["high_offset_hot_cold_cold_counts"]:
        lines.extend(
            [
                "High-offset hot/cold rows:",
                "",
                "| Workload | Row | Segment | Best ms | Count |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in [
            *summary["high_offset_hot_cold_rows"],
            *summary["high_offset_hot_cold_cold_counts"],
        ]:
            lines.append(
                f"| {row['workload']} | `{row['name']}` | {row['segment_size']} | "
                f"{row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["high_offset_cold_hot_overhead"]:
        source_label = summary.get("high_offset_cold_hot_overhead_source", "benchmark")
        lines.extend(
            [
                f"High-offset cold/hot overhead (source: `{source_label}`):",
                "",
                "| Workload | Hot Row | Hot ms | Count Server ms | Server / Hot | Server / Cold CLI | Cold CLI ms | CLI / Hot | CLI Extra ms | Cold Process ms | Process / Hot |",
                "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["high_offset_cold_hot_overhead"]:
            lines.append(
                f"| {row['workload']} | `{row['hot_name']}` | "
                f"{row['hot_best_ms']:.3f} | "
                f"{format_optional_ms(row['hot_server_best_ms'])} | "
                f"{format_optional_ratio(row['hot_server_over_hot'])} | "
                f"{format_optional_ratio(row['hot_server_over_cold_cli'])} | "
                f"{format_optional_ms(row['cold_cli_best_ms'])} | "
                f"{format_optional_ratio(row['cold_cli_over_hot'])} | "
                f"{format_optional_ms(row['cold_cli_extra_ms'])} | "
                f"{format_optional_ms(row['cold_process_best_ms'])} | "
                f"{format_optional_ratio(row['cold_process_over_hot'])} |"
            )
        lines.append("")
    if summary["materialized_generation"]:
        lines.extend(
            [
                "Materialized generation rows:",
                "",
                "| Workload | Row | Segment | Best ms | Count |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["materialized_generation"]:
            lines.append(
                f"| {row['workload']} | `{row['name']}` | {row['segment_size']} | "
                f"{row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["next_prime_searches"]:
        lines.extend(
            [
                "Next-prime search rows:",
                "",
                "| Start | Row | Searches | Best ms | Prime |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["next_prime_searches"]:
            lines.append(
                f"| {row['workload']} | `{row['name']}` | "
                f"{row['segment_size']} | {row['best_ms']:.3f} | {row['result']} |"
            )
        lines.append("")
    if summary["primary_candidate_spread"]:
        lines.extend(
            [
                "Primary count candidate spread:",
                "",
                "| Scope | Workload | Row | Segment | Best ms | Slowdown vs fastest |",
                "| --- | ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for group in summary["primary_candidate_spread"]:
            for row in group["candidates"][:5]:
                lines.append(
                    f"| {group['scope']} | {group['workload']} | `{row['name']}` | "
                    f"{row['segment_size']} | {row['best_ms']:.3f} | "
                    f"{row['slowdown_vs_fastest']:.2f}x |"
                )
        lines.append("")
    if summary["experimental_counts"]:
        lines.extend(
            [
                "Experimental count lanes:",
                "",
                "| Workload | Row | Segment | Best ms | Slowdown vs primary |",
                "| ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for row in summary["experimental_counts"]:
            slowdown = row["slowdown_vs_primary"]
            slowdown_text = "n/a" if slowdown is None else f"{slowdown:.2f}x"
            lines.append(
                f"| {row['workload']} | `{row['name']}` | {row['segment_size']} | "
                f"{row['best_ms']:.3f} | {slowdown_text} |"
            )
        lines.append("")
    return lines


def render_tuning_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## Tuning", ""]
    if not summary["available"]:
        lines.append("No tuning summary was available.")
        lines.append("")
        return lines
    lines.append(
        f"Samples: `{summary['sample_count']}`; rounds: `{summary.get('rounds')}`; "
        f"elapsed seconds: `{summary['elapsed_seconds']}`."
    )
    lines.append("")
    if summary["best_by_range"]:
        lines.extend(
            [
                "| Range | Mode | Segment | Threads | Best ms | Median ms | Count |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["best_by_range"]:
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['count_mode']}` | "
                f"{row['segment_size']} | "
                f"{row['threads']}/{row['requested_threads']} | {row['best_ms']:.3f} | "
                f"{row['median_ms']:.3f} | {row['count']} |"
            )
        lines.append("")
    if summary["default_alignment"]:
        if any(row["default_source"] == "current_calibration" for row in summary["default_alignment"]):
            lines.append(
                "Default alignment uses current calibration defaults when available; "
                "`stale artifact` means the tuning JSON stored an older default."
            )
            lines.append("")
        lines.extend(
            [
                "Default alignment:",
                "",
                "| Range | Tuned mode | Default mode | Tuned segment | Default segment | Tuned threads | Default threads | Default source | Median ms | Aligned |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in summary["default_alignment"]:
            aligned = (
                row["count_mode_aligned"]
                and row["segment_size_aligned"]
                and row["threads_aligned"]
            )
            default_source = row["default_source"]
            if row["artifact_default_stale"]:
                default_source = f"{default_source}; stale artifact"
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['best_count_mode']}` | "
                f"`{row['default_count_mode']}` | "
                f"{row['best_segment_size']} | "
                f"{row['default_segment_size']} | "
                f"{row['best_threads']}/{row['best_requested_threads']} | "
                f"{row['default_threads']}/{row['default_requested_threads']} | "
                f"`{default_source}` | "
                f"{row['median_ms']:.3f} | "
                f"{'yes' if aligned else 'no'} |"
            )
        lines.append("")
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
