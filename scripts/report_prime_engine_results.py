from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
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
DEFAULT_EXTERNAL_NEXT_SERVER = RESULTS_DIR / "prime_engine_external_next_server_latest.csv"
DEFAULT_EXTERNAL_NEXT_SERVER_METADATA = (
    RESULTS_DIR / "prime_engine_external_next_server_latest.json"
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
DEFAULT_EXTERNAL_HIGH_OFFSET_HOT_SERVER = (
    RESULTS_DIR / "prime_engine_high_offset_hot_server_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_HOT_SERVER_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_hot_server_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_probe_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_probe_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_SWEEP = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_segment_sweep_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_SWEEP_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_segment_sweep_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_CANDIDATE_CONFIRM = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_candidate_confirm_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_CANDIDATE_CONFIRM_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_count_binary_candidate_confirm_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_HOT_SERVER = (
    RESULTS_DIR / "prime_engine_high_offset_shifted_hot_server_top_confirm_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_HOT_SERVER_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_shifted_hot_server_top_confirm_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_COUNT_BINARY = (
    RESULTS_DIR / "prime_engine_high_offset_shifted_count_binary_probe_latest.csv"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_COUNT_BINARY_METADATA = (
    RESULTS_DIR / "prime_engine_high_offset_shifted_count_binary_probe_latest.json"
)
DEFAULT_EXTERNAL_COMPETITIVE_SMOKE = (
    RESULTS_DIR / "prime_engine_competitive_smoke_latest.csv"
)
DEFAULT_EXTERNAL_COMPETITIVE_SMOKE_METADATA = (
    RESULTS_DIR / "prime_engine_competitive_smoke_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_CONFIRMATION = (
    RESULTS_DIR / "prime_engine_high_offset_confirmation_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_CANDIDATE_CONFIRMATION = (
    RESULTS_DIR / "prime_engine_high_offset_candidate_confirmation_latest.json"
)
DEFAULT_EXTERNAL_HIGH_OFFSET_PROMOTION_FOCUS = (
    RESULTS_DIR / "prime_engine_high_offset_promotion_focus_latest.json"
)
DEFAULT_HIGH_OFFSET_HOT_COLD_BENCHMARK = (
    RESULTS_DIR / "prime_engine_high_offset_hot_cold_latest.csv"
)
DEFAULT_TUNING = RESULTS_DIR / "prime_engine_tuning_latest.json"
DEFAULT_DEFAULT_CALIBRATION = RESULTS_DIR / "prime_engine_default_calibration_latest.json"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "prime_engine_report_latest.md"
DEFAULT_OUTPUT_JSON = RESULTS_DIR / "prime_engine_report_latest.json"
SAMPLE_NOISY_MAX_OVER_MEDIAN = 1.5
SAMPLE_ROBUST_NOISE_MIN_COUNT = 5
HIGH_OFFSET_PROMOTION_MIN_GAIN_RATIO = 1.05
HIGH_OFFSET_SHIFTED_CANDIDATE_MIN_GAIN_RATIO = 1.05
EXTERNAL_CONTROL_PROVENANCE_TOOLS = (
    "primesieve",
    "primecount",
    "primesieve_count_server",
    "primecount_pi_server",
    "primesieve_library_server",
    "primesieve_iterator_server",
    "primecount_library_server",
)


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
    "cold_count_binary_high_offset_default_plan_8t",
    "cold_count_binary_high_offset_noop",
    "cold_count_binary_parallel_high_offset_default_range_count_8t",
    "cold_process_high_offset_default_plan_8t",
    "cold_process_high_offset_noop_worker",
    "cold_process_segmented_range_count",
    "cold_process_parallel_segmented_range_count_8t",
    "cold_process_parallel_high_offset_default_range_count_1t",
    "cold_process_parallel_high_offset_segmented_range_count_8t",
    "cold_process_parallel_high_offset_default_range_count_8t",
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
        "--external-next-server",
        type=Path,
        default=DEFAULT_EXTERNAL_NEXT_SERVER,
    )
    parser.add_argument(
        "--external-next-server-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_NEXT_SERVER_METADATA,
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
        "--external-high-offset-hot-server",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_HOT_SERVER,
    )
    parser.add_argument(
        "--external-high-offset-hot-server-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_HOT_SERVER_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-count-binary",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY,
    )
    parser.add_argument(
        "--external-high-offset-count-binary-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-count-binary-sweep",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_SWEEP,
    )
    parser.add_argument(
        "--external-high-offset-count-binary-sweep-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_SWEEP_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-count-binary-candidate-confirm",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_CANDIDATE_CONFIRM,
    )
    parser.add_argument(
        "--external-high-offset-count-binary-candidate-confirm-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_COUNT_BINARY_CANDIDATE_CONFIRM_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-shifted-hot-server",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_HOT_SERVER,
    )
    parser.add_argument(
        "--external-high-offset-shifted-hot-server-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_HOT_SERVER_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-shifted-count-binary",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_COUNT_BINARY,
    )
    parser.add_argument(
        "--external-high-offset-shifted-count-binary-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_SHIFTED_COUNT_BINARY_METADATA,
    )
    parser.add_argument(
        "--external-competitive-smoke",
        type=Path,
        default=DEFAULT_EXTERNAL_COMPETITIVE_SMOKE,
    )
    parser.add_argument(
        "--external-competitive-smoke-metadata",
        type=Path,
        default=DEFAULT_EXTERNAL_COMPETITIVE_SMOKE_METADATA,
    )
    parser.add_argument(
        "--external-high-offset-confirmation",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_CONFIRMATION,
    )
    parser.add_argument(
        "--external-high-offset-candidate-confirmation",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_CANDIDATE_CONFIRMATION,
    )
    parser.add_argument(
        "--external-high-offset-promotion-focus",
        type=Path,
        default=DEFAULT_EXTERNAL_HIGH_OFFSET_PROMOTION_FOCUS,
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
        external_next_server_path=args.external_next_server,
        external_next_server_metadata_path=args.external_next_server_metadata,
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
        external_high_offset_hot_server_path=args.external_high_offset_hot_server,
        external_high_offset_hot_server_metadata_path=(
            args.external_high_offset_hot_server_metadata
        ),
        external_high_offset_count_binary_path=args.external_high_offset_count_binary,
        external_high_offset_count_binary_metadata_path=(
            args.external_high_offset_count_binary_metadata
        ),
        external_high_offset_count_binary_sweep_path=(
            args.external_high_offset_count_binary_sweep
        ),
        external_high_offset_count_binary_sweep_metadata_path=(
            args.external_high_offset_count_binary_sweep_metadata
        ),
        external_high_offset_count_binary_candidate_confirm_path=(
            args.external_high_offset_count_binary_candidate_confirm
        ),
        external_high_offset_count_binary_candidate_confirm_metadata_path=(
            args.external_high_offset_count_binary_candidate_confirm_metadata
        ),
        external_high_offset_shifted_hot_server_path=(
            args.external_high_offset_shifted_hot_server
        ),
        external_high_offset_shifted_hot_server_metadata_path=(
            args.external_high_offset_shifted_hot_server_metadata
        ),
        external_high_offset_shifted_count_binary_path=(
            args.external_high_offset_shifted_count_binary
        ),
        external_high_offset_shifted_count_binary_metadata_path=(
            args.external_high_offset_shifted_count_binary_metadata
        ),
        external_competitive_smoke_path=args.external_competitive_smoke,
        external_competitive_smoke_metadata_path=(
            args.external_competitive_smoke_metadata
        ),
        external_high_offset_confirmation_path=args.external_high_offset_confirmation,
        external_high_offset_candidate_confirmation_path=(
            args.external_high_offset_candidate_confirmation
        ),
        external_high_offset_promotion_focus_path=(
            args.external_high_offset_promotion_focus
        ),
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
    external_next_server_path: Path | None = None,
    external_next_server_metadata_path: Path | None = None,
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
    external_high_offset_hot_server_path: Path | None = None,
    external_high_offset_hot_server_metadata_path: Path | None = None,
    external_high_offset_count_binary_path: Path | None = None,
    external_high_offset_count_binary_metadata_path: Path | None = None,
    external_high_offset_count_binary_sweep_path: Path | None = None,
    external_high_offset_count_binary_sweep_metadata_path: Path | None = None,
    external_high_offset_count_binary_candidate_confirm_path: Path | None = None,
    external_high_offset_count_binary_candidate_confirm_metadata_path: Path | None = None,
    external_high_offset_shifted_hot_server_path: Path | None = None,
    external_high_offset_shifted_hot_server_metadata_path: Path | None = None,
    external_high_offset_shifted_count_binary_path: Path | None = None,
    external_high_offset_shifted_count_binary_metadata_path: Path | None = None,
    external_competitive_smoke_path: Path | None = None,
    external_competitive_smoke_metadata_path: Path | None = None,
    external_high_offset_confirmation_path: Path | None = None,
    external_high_offset_candidate_confirmation_path: Path | None = None,
    external_high_offset_promotion_focus_path: Path | None = None,
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
    external_next_server_rows = read_csv_optional(external_next_server_path)
    external_next_server_metadata = read_json_optional(external_next_server_metadata_path)
    external_next_server_sample_rows = read_sample_rows_from_metadata(
        external_next_server_metadata
    )
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
    external_high_offset_hot_server_rows = read_csv_optional(
        external_high_offset_hot_server_path
    )
    external_high_offset_hot_server_metadata = read_json_optional(
        external_high_offset_hot_server_metadata_path
    )
    external_high_offset_hot_server_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_hot_server_metadata
    )
    external_high_offset_count_binary_rows = (
        read_csv_if_present(external_high_offset_count_binary_path, missing_inputs)
        if external_high_offset_count_binary_path is not None
        else []
    )
    external_high_offset_count_binary_metadata = read_json_optional(
        external_high_offset_count_binary_metadata_path
    )
    external_high_offset_count_binary_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_count_binary_metadata
    )
    external_high_offset_count_binary_sweep_rows = read_csv_optional(
        external_high_offset_count_binary_sweep_path
    )
    external_high_offset_count_binary_sweep_metadata = read_json_optional(
        external_high_offset_count_binary_sweep_metadata_path
    )
    external_high_offset_count_binary_sweep_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_count_binary_sweep_metadata
    )
    external_high_offset_count_binary_candidate_confirm_rows = read_csv_optional(
        external_high_offset_count_binary_candidate_confirm_path
    )
    external_high_offset_count_binary_candidate_confirm_metadata = read_json_optional(
        external_high_offset_count_binary_candidate_confirm_metadata_path
    )
    external_high_offset_count_binary_candidate_confirm_sample_rows = (
        read_sample_rows_from_metadata(
            external_high_offset_count_binary_candidate_confirm_metadata
        )
    )
    external_high_offset_shifted_hot_server_rows = read_csv_optional(
        external_high_offset_shifted_hot_server_path
    )
    external_high_offset_shifted_hot_server_metadata = read_json_optional(
        external_high_offset_shifted_hot_server_metadata_path
    )
    external_high_offset_shifted_hot_server_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_shifted_hot_server_metadata
    )
    external_high_offset_shifted_count_binary_rows = read_csv_optional(
        external_high_offset_shifted_count_binary_path
    )
    external_high_offset_shifted_count_binary_metadata = read_json_optional(
        external_high_offset_shifted_count_binary_metadata_path
    )
    external_high_offset_shifted_count_binary_sample_rows = read_sample_rows_from_metadata(
        external_high_offset_shifted_count_binary_metadata
    )
    external_competitive_smoke_rows = read_csv_optional(external_competitive_smoke_path)
    external_competitive_smoke_metadata = read_json_optional(
        external_competitive_smoke_metadata_path
    )
    external_competitive_smoke_sample_rows = read_sample_rows_from_metadata(
        external_competitive_smoke_metadata
    )
    external_high_offset_confirmation = read_json_optional(
        external_high_offset_confirmation_path
    )
    external_high_offset_candidate_confirmation = read_json_optional(
        external_high_offset_candidate_confirmation_path
    )
    external_high_offset_promotion_focus = read_json_optional(
        external_high_offset_promotion_focus_path
    )
    high_offset_hot_cold_benchmark_rows = read_csv_optional(
        high_offset_hot_cold_benchmark_path
    )
    tuning_summary = read_json_if_present(tuning_path, missing_inputs)
    default_calibration = read_json_optional(default_calibration_path)

    default_calibration_summary = summarize_default_calibration(default_calibration)
    benchmark_summary = summarize_benchmark(
        benchmark_rows,
        high_offset_hot_cold_benchmark_rows,
    )
    external_summary = summarize_external(
        external_rows,
        external_metadata,
        external_sample_rows,
    )
    benchmark_summary["high_offset_server_external"] = (
        summarize_high_offset_server_external(benchmark_summary, external_summary)
    )
    external_high_offset_hot_server_summary = summarize_external_segment_sweep(
        external_high_offset_hot_server_rows,
        external_high_offset_hot_server_metadata,
        external_high_offset_hot_server_sample_rows,
    )
    external_high_offset_count_binary_summary = summarize_high_offset_count_binary(
        external_high_offset_count_binary_rows,
        external_high_offset_count_binary_metadata,
        external_high_offset_count_binary_sample_rows,
    )
    external_high_offset_count_binary_sweep_summary = (
        summarize_high_offset_count_binary_segment_sweep(
            external_high_offset_count_binary_sweep_rows,
            external_high_offset_count_binary_sweep_metadata,
            external_high_offset_count_binary_sweep_sample_rows,
        )
    )
    external_high_offset_count_binary_candidate_confirm_summary = (
        summarize_high_offset_count_binary_segment_sweep(
            external_high_offset_count_binary_candidate_confirm_rows,
            external_high_offset_count_binary_candidate_confirm_metadata,
            external_high_offset_count_binary_candidate_confirm_sample_rows,
            readout_require_stable_samples=False,
        )
    )
    external_high_offset_count_binary_sweep_summary = (
        apply_count_binary_cold_confirmation_readout(
            external_high_offset_count_binary_sweep_summary,
            external_high_offset_count_binary_candidate_confirm_summary,
        )
    )
    external_high_offset_confirmation_summary = summarize_external_mode_confirmation(
        external_high_offset_confirmation
    )
    external_high_offset_candidate_confirmation_summary = (
        summarize_external_mode_confirmation(external_high_offset_candidate_confirmation)
    )
    external_high_offset_promotion_focus_summary = (
        summarize_external_mode_confirmation(external_high_offset_promotion_focus)
    )
    external_high_offset_promotion_readout = summarize_high_offset_promotion_readout(
        external_high_offset_hot_server_summary,
        external_high_offset_confirmation_summary,
        external_high_offset_candidate_confirmation_summary,
        external_high_offset_promotion_focus_summary,
    )
    external_high_offset_shifted_hot_server_summary = summarize_external_segment_sweep(
        external_high_offset_shifted_hot_server_rows,
        external_high_offset_shifted_hot_server_metadata,
        external_high_offset_shifted_hot_server_sample_rows,
    )
    external_high_offset_shifted_count_binary_summary = summarize_external_segment_sweep(
        external_high_offset_shifted_count_binary_rows,
        external_high_offset_shifted_count_binary_metadata,
        external_high_offset_shifted_count_binary_sample_rows,
    )
    external_competitive_smoke_summary = summarize_external_segment_sweep(
        external_competitive_smoke_rows,
        external_competitive_smoke_metadata,
        external_competitive_smoke_sample_rows,
    )
    external_control_provenance = summarize_external_control_provenance(
        [
            ("external_controls", external_metadata),
            ("competitive_smoke", external_competitive_smoke_metadata),
            ("high_offset_count_binary", external_high_offset_count_binary_metadata),
            ("high_offset_hot_server", external_high_offset_hot_server_metadata),
            (
                "high_offset_shifted_count_binary",
                external_high_offset_shifted_count_binary_metadata,
            ),
            ("external_next_server", external_next_server_metadata),
        ]
    )
    external_high_offset_shifted_candidate_readout = (
        summarize_high_offset_shifted_candidate_readout(
            external_high_offset_shifted_hot_server_summary
        )
    )
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
            "external_next_server": (
                str(external_next_server_path)
                if external_next_server_path is not None
                else None
            ),
            "external_next_server_metadata": (
                str(external_next_server_metadata_path)
                if external_next_server_metadata_path is not None
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
            "external_high_offset_hot_server": (
                str(external_high_offset_hot_server_path)
                if external_high_offset_hot_server_path is not None
                else None
            ),
            "external_high_offset_hot_server_metadata": (
                str(external_high_offset_hot_server_metadata_path)
                if external_high_offset_hot_server_metadata_path is not None
                else None
            ),
            "external_high_offset_count_binary": (
                str(external_high_offset_count_binary_path)
                if external_high_offset_count_binary_path is not None
                else None
            ),
            "external_high_offset_count_binary_metadata": (
                str(external_high_offset_count_binary_metadata_path)
                if external_high_offset_count_binary_metadata_path is not None
                else None
            ),
            "external_high_offset_count_binary_sweep": (
                str(external_high_offset_count_binary_sweep_path)
                if external_high_offset_count_binary_sweep_path is not None
                else None
            ),
            "external_high_offset_count_binary_sweep_metadata": (
                str(external_high_offset_count_binary_sweep_metadata_path)
                if external_high_offset_count_binary_sweep_metadata_path is not None
                else None
            ),
            "external_high_offset_count_binary_candidate_confirm": (
                str(external_high_offset_count_binary_candidate_confirm_path)
                if external_high_offset_count_binary_candidate_confirm_path is not None
                else None
            ),
            "external_high_offset_count_binary_candidate_confirm_metadata": (
                str(external_high_offset_count_binary_candidate_confirm_metadata_path)
                if external_high_offset_count_binary_candidate_confirm_metadata_path
                is not None
                else None
            ),
            "external_high_offset_shifted_hot_server": (
                str(external_high_offset_shifted_hot_server_path)
                if external_high_offset_shifted_hot_server_path is not None
                else None
            ),
            "external_high_offset_shifted_hot_server_metadata": (
                str(external_high_offset_shifted_hot_server_metadata_path)
                if external_high_offset_shifted_hot_server_metadata_path is not None
                else None
            ),
            "external_high_offset_shifted_count_binary": (
                str(external_high_offset_shifted_count_binary_path)
                if external_high_offset_shifted_count_binary_path is not None
                else None
            ),
            "external_high_offset_shifted_count_binary_metadata": (
                str(external_high_offset_shifted_count_binary_metadata_path)
                if external_high_offset_shifted_count_binary_metadata_path is not None
                else None
            ),
            "external_competitive_smoke": (
                str(external_competitive_smoke_path)
                if external_competitive_smoke_path is not None
                else None
            ),
            "external_competitive_smoke_metadata": (
                str(external_competitive_smoke_metadata_path)
                if external_competitive_smoke_metadata_path is not None
                else None
            ),
            "external_high_offset_confirmation": (
                str(external_high_offset_confirmation_path)
                if external_high_offset_confirmation_path is not None
                else None
            ),
            "external_high_offset_candidate_confirmation": (
                str(external_high_offset_candidate_confirmation_path)
                if external_high_offset_candidate_confirmation_path is not None
                else None
            ),
            "external_high_offset_promotion_focus": (
                str(external_high_offset_promotion_focus_path)
                if external_high_offset_promotion_focus_path is not None
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
        "external_control_provenance": external_control_provenance,
        "benchmark": benchmark_summary,
        "external_correctness": summarize_external_correctness(external_correctness),
        "external": external_summary,
        "external_next": summarize_external_next(
            external_next_rows,
            external_next_metadata,
            external_next_sample_rows,
        ),
        "external_next_server": summarize_external_next(
            external_next_server_rows,
            external_next_server_metadata,
            external_next_server_sample_rows,
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
        "external_high_offset_hot_server": external_high_offset_hot_server_summary,
        "external_high_offset_count_binary": external_high_offset_count_binary_summary,
        "external_high_offset_count_binary_sweep": (
            external_high_offset_count_binary_sweep_summary
        ),
        "external_high_offset_count_binary_candidate_confirm": (
            external_high_offset_count_binary_candidate_confirm_summary
        ),
        "external_high_offset_shifted_hot_server": (
            external_high_offset_shifted_hot_server_summary
        ),
        "external_high_offset_shifted_count_binary": (
            external_high_offset_shifted_count_binary_summary
        ),
        "external_competitive_smoke": external_competitive_smoke_summary,
        "external_high_offset_shifted_candidate_readout": (
            external_high_offset_shifted_candidate_readout
        ),
        "external_high_offset_promotion_readout": external_high_offset_promotion_readout,
        "external_high_offset_confirmation": external_high_offset_confirmation_summary,
        "external_high_offset_candidate_confirmation": (
            external_high_offset_candidate_confirmation_summary
        ),
        "external_high_offset_promotion_focus": (
            external_high_offset_promotion_focus_summary
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
    hot_candidates = [
        row
        for row in rows_by_name.values()
        if row["name"].startswith("parallel_high_offset_")
        and row["name"].endswith("_range_count_8t")
    ]
    hot = min(
        hot_candidates,
        key=lambda row: float(row["best_ms"]),
        default=None,
    )
    hot_server_candidates = [
        row
        for row in rows_by_name.values()
        if row["name"].startswith("hot_cli_count_server_parallel_high_offset_")
    ]
    hot_server = min(
        hot_server_candidates,
        key=lambda row: float(row["best_ms"]),
        default=None,
    )
    cold_cli = rows_by_name.get("cold_cli_parallel_high_offset_default_range_count_8t")
    cold_count_binary = rows_by_name.get(
        "cold_count_binary_parallel_high_offset_default_range_count_8t"
    )
    cold_count_binary_noop = rows_by_name.get("cold_count_binary_high_offset_noop")
    cold_count_binary_plan = rows_by_name.get(
        "cold_count_binary_high_offset_default_plan_8t"
    )
    cold_noop = rows_by_name.get("cold_process_high_offset_noop_worker")
    cold_plan = rows_by_name.get("cold_process_high_offset_default_plan_8t")
    cold_serial_default = rows_by_name.get(
        "cold_process_parallel_high_offset_default_range_count_1t"
    )
    cold_process = rows_by_name.get("cold_process_parallel_high_offset_segmented_range_count_8t")
    cold_process_default = rows_by_name.get(
        "cold_process_parallel_high_offset_default_range_count_8t"
    )
    cold_external_primesieve = rows_by_name.get(
        "cold_external_primesieve_high_offset_count_8t"
    )
    if hot is None or (
        hot_server is None
        and cold_cli is None
        and cold_count_binary is None
        and cold_process is None
        and cold_process_default is None
    ):
        return []

    hot_ms = float(hot["best_ms"])
    hot_server_ms = float(hot_server["best_ms"]) if hot_server else None
    cold_count_binary_ms = float(cold_count_binary["best_ms"]) if cold_count_binary else None
    cold_count_binary_noop_ms = (
        float(cold_count_binary_noop["best_ms"]) if cold_count_binary_noop else None
    )
    cold_count_binary_server_extra_ms = (
        cold_count_binary_ms - hot_server_ms
        if cold_count_binary_ms is not None and hot_server_ms is not None
        else None
    )
    cold_count_binary_noop_share_of_server_extra = (
        cold_count_binary_noop_ms / cold_count_binary_server_extra_ms
        if cold_count_binary_noop_ms is not None
        and cold_count_binary_server_extra_ms is not None
        and cold_count_binary_server_extra_ms > 0
        else None
    )
    cold_count_binary_residual_after_binary_noop_ms = (
        max(0.0, cold_count_binary_server_extra_ms - cold_count_binary_noop_ms)
        if cold_count_binary_server_extra_ms is not None
        and cold_count_binary_noop_ms is not None
        else None
    )
    summary = {
        "workload": hot["workload"],
        "result": hot["result"],
        "hot_name": hot["name"],
        "hot_segment_size": hot["segment_size"],
        "hot_best_ms": hot_ms,
        "hot_server_name": hot_server["name"] if hot_server else None,
        "hot_server_segment_size": hot_server["segment_size"] if hot_server else None,
        "hot_server_best_ms": hot_server_ms,
        "hot_server_over_hot": (
            float(hot_server["best_ms"]) / hot_ms if hot_server and hot_ms > 0 else None
        ),
        "hot_server_over_cold_cli": (
            float(hot_server["best_ms"]) / float(cold_cli["best_ms"])
            if hot_server and cold_cli and float(cold_cli["best_ms"]) > 0
            else None
        ),
        "hot_server_over_cold_count_binary": (
            float(hot_server["best_ms"]) / float(cold_count_binary["best_ms"])
            if hot_server and cold_count_binary and float(cold_count_binary["best_ms"]) > 0
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
        "cold_count_binary_name": cold_count_binary["name"] if cold_count_binary else None,
        "cold_count_binary_segment_size": (
            cold_count_binary["segment_size"] if cold_count_binary else None
        ),
        "cold_count_binary_best_ms": cold_count_binary_ms,
        "cold_count_binary_over_hot": (
            float(cold_count_binary["best_ms"]) / hot_ms
            if cold_count_binary and hot_ms > 0
            else None
        ),
        "cold_count_binary_extra_ms": (
            float(cold_count_binary["best_ms"]) - hot_ms
            if cold_count_binary is not None
            else None
        ),
        "cold_count_binary_noop_name": (
            cold_count_binary_noop["name"] if cold_count_binary_noop else None
        ),
        "cold_count_binary_noop_best_ms": cold_count_binary_noop_ms,
        "cold_count_binary_plan_name": (
            cold_count_binary_plan["name"] if cold_count_binary_plan else None
        ),
        "cold_count_binary_plan_best_ms": (
            float(cold_count_binary_plan["best_ms"]) if cold_count_binary_plan else None
        ),
        "cold_count_binary_minus_noop_ms": (
            float(cold_count_binary["best_ms"]) - float(cold_noop["best_ms"])
            if cold_count_binary is not None and cold_noop is not None
            else None
        ),
        "cold_count_binary_minus_binary_noop_ms": (
            float(cold_count_binary["best_ms"]) - float(cold_count_binary_noop["best_ms"])
            if cold_count_binary is not None and cold_count_binary_noop is not None
            else None
        ),
        "cold_count_binary_server_extra_ms": cold_count_binary_server_extra_ms,
        "cold_count_binary_noop_share_of_server_extra": (
            cold_count_binary_noop_share_of_server_extra
        ),
        "cold_count_binary_residual_after_binary_noop_ms": (
            cold_count_binary_residual_after_binary_noop_ms
        ),
        "cold_count_binary_next_action": classify_cold_count_binary_next_action(
            cold_count_binary_noop_share_of_server_extra,
            cold_count_binary_residual_after_binary_noop_ms,
        ),
        "cold_process_noop_name": cold_noop["name"] if cold_noop else None,
        "cold_process_noop_best_ms": float(cold_noop["best_ms"]) if cold_noop else None,
        "cold_process_plan_name": cold_plan["name"] if cold_plan else None,
        "cold_process_plan_best_ms": float(cold_plan["best_ms"]) if cold_plan else None,
        "cold_process_serial_default_name": (
            cold_serial_default["name"] if cold_serial_default else None
        ),
        "cold_process_serial_default_best_ms": (
            float(cold_serial_default["best_ms"]) if cold_serial_default else None
        ),
        "cold_external_primesieve_name": (
            cold_external_primesieve["name"] if cold_external_primesieve else None
        ),
        "cold_external_primesieve_best_ms": (
            float(cold_external_primesieve["best_ms"])
            if cold_external_primesieve
            else None
        ),
        "cold_count_binary_over_external_primesieve": (
            float(cold_count_binary["best_ms"]) / float(cold_external_primesieve["best_ms"])
            if cold_count_binary
            and cold_external_primesieve
            and float(cold_external_primesieve["best_ms"]) > 0
            else None
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
        "cold_process_default_name": (
            cold_process_default["name"] if cold_process_default else None
        ),
        "cold_process_default_segment_size": (
            cold_process_default["segment_size"] if cold_process_default else None
        ),
        "cold_process_default_best_ms": (
            float(cold_process_default["best_ms"]) if cold_process_default else None
        ),
        "cold_process_default_over_hot": (
            float(cold_process_default["best_ms"]) / hot_ms
            if cold_process_default and hot_ms > 0
            else None
        ),
        "cold_process_default_extra_ms": (
            float(cold_process_default["best_ms"]) - hot_ms
            if cold_process_default is not None
            else None
        ),
    }
    return [summary]


def classify_cold_count_binary_next_action(
    noop_share_of_server_extra: float | None,
    residual_after_noop_ms: float | None,
) -> str | None:
    if noop_share_of_server_extra is None or residual_after_noop_ms is None:
        return None
    if noop_share_of_server_extra >= 0.50:
        return "launch_amortization_required"
    if residual_after_noop_ms >= 0.50:
        return "thread_first_touch_reduction_required"
    return "cold_core_rebenchmark_required"


def summarize_high_offset_server_external(
    benchmark_summary: dict[str, Any],
    external_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    overhead_rows = benchmark_summary.get("high_offset_cold_hot_overhead") or []
    if not overhead_rows:
        return []
    server = overhead_rows[0]
    server_ms = server.get("hot_server_best_ms")
    if server_ms is None or server_ms <= 0:
        return []

    rows = []
    for speedup in external_summary.get("speedups", []):
        if speedup.get("span") != server["workload"]:
            continue
        if speedup.get("result") != server["result"]:
            continue
        if speedup.get("low", 0) == 0:
            continue
        baseline_best_ms = speedup.get("baseline_best_ms")
        if baseline_best_ms is None:
            continue
        rows.append(
            {
                "workload": server["workload"],
                "result": server["result"],
                "server_name": server["hot_server_name"],
                "server_segment_size": server["hot_server_segment_size"],
                "server_best_ms": server_ms,
                "baseline": speedup["baseline"],
                "baseline_best_ms": baseline_best_ms,
                "baseline_median_ms": speedup.get("baseline_median_ms"),
                "server_best_speedup": baseline_best_ms / server_ms,
                "cold_cli_name": speedup["name"],
                "cold_cli_best_ms": speedup["best_ms"],
                "cold_cli_best_speedup": speedup["circle_speedup"],
            }
        )
    return sorted(rows, key=lambda row: row["baseline"])


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
    all_summary = external_win_counts(speedups)
    cold_cli_summary = external_win_counts(
        [
            row
            for row in speedups
            if not is_circle_server_row(row) and not is_external_count_server_baseline(row)
        ]
    )
    server_summary = external_win_counts(
        [
            row
            for row in speedups
            if is_circle_server_row(row) and not is_external_count_server_baseline(row)
        ]
    )
    external_server_summary = external_win_counts(
        [row for row in speedups if is_external_count_server_baseline(row)]
    )
    return {
        "speedups": speedups,
        **all_summary,
        "cold_cli": cold_cli_summary,
        "server": server_summary,
        "external_server": external_server_summary,
        "metadata": summarize_external_metadata(metadata),
    }


COUNT_BINARY_FOCUS_ORDER = {
    "cold_count_binary_vs_primesieve_cli": 0,
    "cold_count_binary_vs_primecount_cli": 1,
    "slim_server_vs_primesieve_cli": 2,
    "slim_server_vs_primecount_cli": 3,
    "slim_server_vs_libprimesieve": 4,
    "slim_server_vs_libprimecount": 5,
    "hot_server_vs_libprimesieve": 6,
    "hot_server_vs_libprimecount": 7,
}


def summarize_high_offset_count_binary(
    rows: list[dict[str, str]],
    metadata: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    summary = summarize_external_segment_sweep(rows, metadata, sample_rows)
    focus_rows = []
    for row in summary.get("speedups", []):
        role = high_offset_count_binary_role(row)
        if role is None:
            continue
        focus_rows.append(
            {
                **row,
                "role": role,
                "role_label": high_offset_count_binary_role_label(role),
            }
        )
    focus_rows.sort(
        key=lambda row: (
            row["low"],
            row["high"],
            COUNT_BINARY_FOCUS_ORDER.get(row["role"], 99),
            row["baseline"],
            row["name"],
        )
    )
    return {
        **summary,
        "focus_rows": focus_rows,
        "focus_rows_count": len(focus_rows),
        "focus_median_wins": sum(
            1 for row in focus_rows if row["median_circle_speedup"] >= 1.0
        ),
        "focus_best_wins": sum(1 for row in focus_rows if row["circle_speedup"] >= 1.0),
        "cold_hot_overhead": summarize_count_binary_cold_hot_overhead(focus_rows),
    }


def summarize_high_offset_count_binary_segment_sweep(
    rows: list[dict[str, str]],
    metadata: dict[str, Any] | None,
    sample_rows: list[dict[str, str]] | None = None,
    *,
    readout_require_stable_samples: bool = True,
) -> dict[str, Any]:
    summary = summarize_external_segment_sweep(
        [row for row in rows if is_count_binary_sweep_row(row)],
        metadata,
        [row for row in sample_rows or [] if is_count_binary_sweep_row(row)],
    )
    return {
        **summary,
        "cold_candidate_readout": summarize_count_binary_cold_candidate_readout(
            summary.get("speedups", []),
            require_stable_samples=readout_require_stable_samples,
        ),
    }


def is_count_binary_sweep_row(row: dict[str, str]) -> bool:
    name = str(row.get("name", ""))
    return name.startswith("circle_prime_count_binary_") or name.startswith("external_")


def summarize_count_binary_cold_candidate_readout(
    speedups: list[dict[str, Any]],
    *,
    min_gain: float = 1.03,
    min_candidate_median_speedup: float = 1.0,
    min_candidate_best_speedup: float = 1.0,
    require_stable_samples: bool = True,
) -> list[dict[str, Any]]:
    cold_rows = [
        row
        for row in speedups
        if str(row.get("name", "")).startswith("circle_prime_count_binary_")
        and "_server_" not in str(row.get("name", ""))
        and row.get("baseline") == "external_primesieve_count"
    ]
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for row in cold_rows:
        grouped.setdefault((row["low"], row["high"], row["baseline"]), []).append(row)

    readout = []
    for (low, high, baseline), rows in sorted(grouped.items()):
        decision_rows = (
            [row for row in rows if row.get("sample_stability") == "stable"]
            if require_stable_samples
            else rows
        )
        if not decision_rows:
            continue
        default = best_count_binary_cold_row(
            [row for row in decision_rows if is_adaptive_default_row(str(row["name"]))]
        )
        best = best_count_binary_cold_row(
            [
                row
                for row in decision_rows
                if not is_adaptive_default_row(str(row["name"]))
            ]
        )
        if default is None:
            continue
        if best is None:
            best = default
        gain = safe_ratio(best["median_circle_speedup"], default["median_circle_speedup"])
        action = count_binary_cold_candidate_action(
            default,
            best,
            gain,
            min_gain=min_gain,
            min_candidate_median_speedup=min_candidate_median_speedup,
            min_candidate_best_speedup=min_candidate_best_speedup,
        )
        readout.append(
            {
                "low": low,
                "high": high,
                "baseline": baseline,
                "default": default,
                "best": best,
                "median_gain_over_default": gain,
                "action": action,
                "min_gain": min_gain,
                "min_candidate_median_speedup": min_candidate_median_speedup,
                "min_candidate_best_speedup": min_candidate_best_speedup,
                "sample_scope": "stable" if require_stable_samples else "all",
            }
        )
    return readout


def best_count_binary_cold_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return max(
        rows,
        key=lambda row: (
            row["median_circle_speedup"],
            row["circle_speedup"],
            -row["median_ms"],
            -row["best_ms"],
            str(row["name"]),
        ),
    )


def count_binary_cold_candidate_action(
    default: dict[str, Any],
    best: dict[str, Any],
    gain: float | None,
    *,
    min_gain: float,
    min_candidate_median_speedup: float,
    min_candidate_best_speedup: float,
) -> str:
    if external_candidate_identity(default) == external_candidate_identity(best):
        return "keep_default"
    if gain is None or best["median_circle_speedup"] <= default["median_circle_speedup"]:
        return "keep_default"
    if gain < min_gain or best["median_circle_speedup"] < min_candidate_median_speedup:
        return "hold_small_gain_candidate"
    if best["circle_speedup"] < min_candidate_best_speedup:
        return "hold_best_speedup_below_floor"
    return "trial_cold_count_binary_candidate"


def apply_count_binary_cold_confirmation_readout(
    sweep_summary: dict[str, Any],
    confirmation_summary: dict[str, Any],
) -> dict[str, Any]:
    readout = sweep_summary.get("cold_candidate_readout") or []
    confirmation_readout = confirmation_summary.get("cold_candidate_readout") or []
    if not readout or not confirmation_readout:
        return sweep_summary

    annotated = []
    for row in readout:
        confirmation = matching_count_binary_cold_confirmation(row, confirmation_readout)
        if confirmation is None:
            annotated.append(
                {
                    **row,
                    "final_action": row.get("action"),
                    "confirmation_status": "missing",
                }
            )
            continue

        confirmation_action = confirmation.get("action")
        action = row.get("action")
        final_action = action
        if action == "trial_cold_count_binary_candidate":
            if confirmation_action == "trial_cold_count_binary_candidate":
                final_action = "trial_confirmed_by_focused_confirmation"
            else:
                final_action = "held_by_focused_confirmation"
        annotated.append(
            {
                **row,
                "confirmation": confirmation,
                "confirmation_status": "matched",
                "confirmation_action": confirmation_action,
                "confirmation_sample_scope": confirmation.get("sample_scope", "unknown"),
                "final_action": final_action,
            }
        )

    return {**sweep_summary, "cold_candidate_readout": annotated}


def matching_count_binary_cold_confirmation(
    row: dict[str, Any],
    confirmation_rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    row_best = external_candidate_identity(row.get("best", {}))
    for confirmation in confirmation_rows:
        if (
            confirmation.get("low") == row.get("low")
            and confirmation.get("high") == row.get("high")
            and confirmation.get("baseline") == row.get("baseline")
            and external_candidate_identity(confirmation.get("best", {})) == row_best
        ):
            return confirmation
    return None


def summarize_count_binary_cold_hot_overhead(
    focus_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int, int], dict[str, dict[str, Any]]] = {}
    for row in focus_rows:
        key = (int(row["low"]), int(row["high"]), int(row["result"]))
        grouped.setdefault(key, {})[row["role"]] = row

    summaries = []
    for key in sorted(grouped):
        rows = grouped[key]
        cold = rows.get("cold_count_binary_vs_primesieve_cli")
        hot = rows.get("slim_server_vs_libprimesieve")
        if cold is None or hot is None:
            continue
        cold_median_ms = float(cold["median_ms"])
        hot_median_ms = float(hot["median_ms"])
        if cold_median_ms <= 0.0 or hot_median_ms <= 0.0:
            continue
        primesieve_cli_median_ms = cold.get("baseline_median_ms")
        libprimesieve_median_ms = hot.get("baseline_median_ms")
        summaries.append(
            {
                "low": key[0],
                "high": key[1],
                "result": key[2],
                "cold_count_binary_name": cold["name"],
                "hot_count_binary_server_name": hot["name"],
                "hot_server_name": hot["name"],
                "cold_count_binary_median_ms": cold_median_ms,
                "hot_count_binary_server_median_ms": hot_median_ms,
                "hot_server_median_ms": hot_median_ms,
                "circle_cold_over_hot_median": cold_median_ms / hot_median_ms,
                "circle_cold_extra_ms": cold_median_ms - hot_median_ms,
                "cold_count_binary_vs_primesieve_median_speedup": cold[
                    "median_circle_speedup"
                ],
                "hot_count_binary_server_vs_libprimesieve_median_speedup": hot[
                    "median_circle_speedup"
                ],
                "hot_server_vs_libprimesieve_median_speedup": hot[
                    "median_circle_speedup"
                ],
                "primesieve_cli_median_ms": primesieve_cli_median_ms,
                "libprimesieve_median_ms": libprimesieve_median_ms,
                "primesieve_cli_over_lib_median": (
                    primesieve_cli_median_ms / libprimesieve_median_ms
                    if primesieve_cli_median_ms is not None
                    and libprimesieve_median_ms is not None
                    and libprimesieve_median_ms > 0.0
                    else None
                ),
                "primesieve_cli_extra_ms": (
                    primesieve_cli_median_ms - libprimesieve_median_ms
                    if primesieve_cli_median_ms is not None
                    and libprimesieve_median_ms is not None
                    else None
                ),
            }
        )
    return summaries


def high_offset_count_binary_role(row: dict[str, Any]) -> str | None:
    name = str(row.get("name", ""))
    baseline = str(row.get("baseline", ""))
    if not is_adaptive_default_row(name):
        return None
    if name.startswith("circle_prime_count_binary_server_"):
        if baseline == "external_primesieve_count":
            return "slim_server_vs_primesieve_cli"
        if baseline == "external_primecount_pi_diff":
            return "slim_server_vs_primecount_cli"
        if baseline == "external_primesieve_count_server":
            return "slim_server_vs_libprimesieve"
        if baseline == "external_primecount_pi_diff_server":
            return "slim_server_vs_libprimecount"
        return None
    if name.startswith("circle_prime_count_binary_"):
        if baseline == "external_primesieve_count":
            return "cold_count_binary_vs_primesieve_cli"
        if baseline == "external_primecount_pi_diff":
            return "cold_count_binary_vs_primecount_cli"
    if name.startswith("circle_prime_server_"):
        if baseline == "external_primesieve_count_server":
            return "hot_server_vs_libprimesieve"
        if baseline == "external_primecount_pi_diff_server":
            return "hot_server_vs_libprimecount"
    return None


def high_offset_count_binary_role_label(role: str) -> str:
    labels = {
        "cold_count_binary_vs_primesieve_cli": "cold count binary vs primesieve CLI",
        "cold_count_binary_vs_primecount_cli": "cold count binary vs primecount CLI",
        "slim_server_vs_primesieve_cli": "slim count binary server vs primesieve CLI",
        "slim_server_vs_primecount_cli": "slim count binary server vs primecount CLI",
        "slim_server_vs_libprimesieve": "slim count binary server vs libprimesieve",
        "slim_server_vs_libprimecount": "slim count binary server vs libprimecount",
        "hot_server_vs_libprimesieve": "hot server vs libprimesieve",
        "hot_server_vs_libprimecount": "hot server vs libprimecount",
    }
    return labels.get(role, role)


def external_win_counts(speedups: list[dict[str, Any]]) -> dict[str, int]:
    primesieve = [row for row in speedups if row["baseline"] == "external_primesieve_count"]
    primesieve_count_server = [
        row for row in speedups if row["baseline"] == "external_primesieve_count_server"
    ]
    primecount_pi_server = [
        row for row in speedups if row["baseline"] == "external_primecount_pi_diff_server"
    ]
    primecount = [row for row in speedups if row["baseline"] == "external_primecount_pi_diff"]
    return {
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
        "primecount_pi_server_wins": sum(
            1 for row in primecount_pi_server if row["circle_speedup"] >= 1.0
        ),
        "primecount_pi_server_median_wins": sum(
            1 for row in primecount_pi_server if row["median_circle_speedup"] >= 1.0
        ),
        "primecount_pi_server_rows": len(primecount_pi_server),
        "primesieve_count_server_wins": sum(
            1 for row in primesieve_count_server if row["circle_speedup"] >= 1.0
        ),
        "primesieve_count_server_median_wins": sum(
            1 for row in primesieve_count_server if row["median_circle_speedup"] >= 1.0
        ),
        "primesieve_count_server_rows": len(primesieve_count_server),
    }


def is_circle_server_row(row: dict[str, Any]) -> bool:
    return str(row.get("name", "")).startswith("circle_prime_server_")


def is_primesieve_count_server_baseline(row: dict[str, Any]) -> bool:
    return row.get("baseline") == "external_primesieve_count_server"


def is_external_count_server_baseline(row: dict[str, Any]) -> bool:
    return row.get("baseline") in {
        "external_primesieve_count_server",
        "external_primecount_pi_diff_server",
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
    cold_cli_speedups = [
        row for row in speedups if not is_external_next_server_row(row)
    ]
    server_speedups = [row for row in speedups if is_external_next_server_row(row)]
    counts = external_next_win_counts(speedups)
    return {
        "available": bool(rows),
        "speedups": speedups,
        "baseline_rows": counts["baseline_rows"],
        "baseline_wins": counts["baseline_wins"],
        "baseline_median_wins": counts["baseline_median_wins"],
        "by_baseline": counts["by_baseline"],
        "primesieve_rows": counts["primesieve_rows"],
        "primesieve_wins": counts["primesieve_wins"],
        "primesieve_median_wins": counts["primesieve_median_wins"],
        "cold_cli": external_next_win_counts(cold_cli_speedups),
        "server": external_next_win_counts(server_speedups),
        "metadata": summarize_external_next_metadata(metadata),
    }


def external_next_win_counts(speedups: list[dict[str, Any]]) -> dict[str, Any]:
    by_baseline: dict[str, dict[str, int]] = {}
    for row in speedups:
        baseline = row["baseline"]
        counts = by_baseline.setdefault(
            baseline,
            {
                "rows": 0,
                "wins": 0,
                "median_wins": 0,
            },
        )
        counts["rows"] += 1
        counts["wins"] += int(row["circle_speedup"] >= 1.0)
        counts["median_wins"] += int(row["median_circle_speedup"] >= 1.0)
    primesieve = by_baseline.get(
        "external_primesieve_next_prime",
        {"rows": 0, "wins": 0, "median_wins": 0},
    )
    return {
        "baseline_rows": len(speedups),
        "baseline_wins": sum(1 for row in speedups if row["circle_speedup"] >= 1.0),
        "baseline_median_wins": sum(
            1 for row in speedups if row["median_circle_speedup"] >= 1.0
        ),
        "by_baseline": by_baseline,
        "primesieve_rows": primesieve["rows"],
        "primesieve_wins": primesieve["wins"],
        "primesieve_median_wins": primesieve["median_wins"],
    }


def is_external_next_server_row(row: dict[str, Any]) -> bool:
    return str(row.get("name", "")).startswith("circle_prime_server_")


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
    if sample_stability == "unknown":
        sample_stability = row.get("sample_stability") or sample_stability
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


def fingerprint_summary(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    return {
        "available": value.get("available"),
        "path": value.get("path"),
        "size_bytes": value.get("size_bytes"),
        "modified_at_utc": value.get("modified_at_utc"),
        "sha256": value.get("sha256"),
        "error": value.get("error"),
    }


def summarize_external_next_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    if metadata is None:
        return {
            "available": False,
            "tools": {},
            "thread_policy": {},
            "starts": [],
            "batch_size": None,
            "warmup_rounds": 0,
            "server_only": False,
            "include_primecount": False,
            "primecount_max_start": None,
            "include_primecount_library_server": False,
            "primecount_library_max_start": None,
            "include_primesieve_library_server": False,
            "include_primesieve_iterator_server": False,
            "primesieve_library_max_start": None,
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
        "warmup_rounds": int(metadata.get("warmup_rounds") or 0),
        "server_only": bool(metadata.get("server_only")),
        "include_circle_server": bool(metadata.get("include_circle_server")),
        "include_primecount": bool(metadata.get("include_primecount")),
        "primecount_max_start": metadata.get("primecount_max_start"),
        "include_primecount_library_server": bool(
            metadata.get("include_primecount_library_server")
        ),
        "primecount_library_max_start": metadata.get("primecount_library_max_start"),
        "include_primesieve_library_server": bool(
            metadata.get("include_primesieve_library_server")
        ),
        "include_primesieve_iterator_server": bool(
            metadata.get("include_primesieve_iterator_server")
        ),
        "primesieve_library_max_start": metadata.get("primesieve_library_max_start"),
        "sample_output": metadata.get("sample_output"),
        "circle_prime_defaults": fingerprint_summary(
            metadata.get("circle_prime_defaults")
        ),
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
                "source": tool.get("source"),
                "method": tool.get("method"),
                "error": tool.get("error"),
                "binary": fingerprint_summary(tool.get("binary")),
                "defaults": fingerprint_summary(tool.get("defaults")),
                "small_prefix_pi_cache_limit": tool.get(
                    "small_prefix_pi_cache_limit"
                ),
                "small_prefix_pi_cache_default_limit": tool.get(
                    "small_prefix_pi_cache_default_limit"
                ),
                "small_prefix_pi_cache_max_limit": tool.get(
                    "small_prefix_pi_cache_max_limit"
                ),
                "small_prefix_pi_cache_limit_env": tool.get(
                    "small_prefix_pi_cache_limit_env"
                ),
                "small_prefix_pi_cache_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_estimated_bytes"
                ),
                "small_prefix_pi_cache_default_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_default_estimated_bytes"
                ),
                "small_prefix_pi_cache_max_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_max_estimated_bytes"
                ),
                "small_prefix_pi_cache_warmup_profiles": tool.get(
                    "small_prefix_pi_cache_warmup_profiles", []
                ),
                "small_prefix_pi_cache_scope": tool.get(
                    "small_prefix_pi_cache_scope"
                ),
                "small_prefix_pi_cache_warmup": tool.get(
                    "small_prefix_pi_cache_warmup"
                ),
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
    default_by_range_baseline = []
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
        default_candidates = [
            row for row in ordered if is_adaptive_default_row(str(row["name"]))
        ]
        if default_candidates:
            default_by_range_baseline.append(default_candidates[0])
        candidate_spread.append(
            {
                "low": low,
                "high": high,
                "span": best["span"],
                "baseline": baseline,
                "candidates": ordered,
            }
        )
    prefix_pi_thread_comparisons = summarize_prefix_pi_thread_comparisons(grouped)

    return {
        "available": bool(rows),
        "speedups": speedups,
        "best_by_range_baseline": best_by_range_baseline,
        "default_by_range_baseline": default_by_range_baseline,
        "prefix_pi_thread_comparisons": prefix_pi_thread_comparisons,
        "candidate_spread": candidate_spread,
        "metadata": summarize_external_sweep_metadata(metadata),
    }


def summarize_high_offset_promotion_readout(
    hot_server_summary: dict[str, Any],
    default_confirmation: dict[str, Any],
    candidate_confirmation: dict[str, Any],
    promotion_focus_confirmation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not hot_server_summary.get("available"):
        return {"available": False, "rows": []}

    default_rows = {
        range_baseline_key(row): row
        for row in hot_server_summary.get("default_by_range_baseline", [])
    }
    hot_server_finished_at = hot_server_summary.get("metadata", {}).get("finished_at_utc")
    candidate_confirmation_generated_at = candidate_confirmation.get("generated_at_utc")
    candidate_confirmation_freshness = confirmation_freshness(
        candidate_confirmation_generated_at,
        hot_server_finished_at,
    )
    promotion_focus_confirmation = promotion_focus_confirmation or {}
    promotion_focus_generated_at = promotion_focus_confirmation.get("generated_at_utc")
    promotion_focus_freshness = confirmation_freshness(
        promotion_focus_generated_at,
        hot_server_finished_at,
    )
    default_confirmations = confirmation_rows_by_range_and_identity(default_confirmation)
    candidate_confirmations = confirmation_winner_rows_by_range_and_identity(
        candidate_confirmation
    )
    promotion_focus_confirmations = confirmation_winner_rows_by_range_and_identity(
        promotion_focus_confirmation
    )
    rows = []
    for best in hot_server_summary.get("best_by_range_baseline", []):
        key = range_baseline_key(best)
        default = default_rows.get(key)
        if default is None:
            continue

        best_confirmation_identity = hot_server_row_identity(best)
        default_confirmation_identity = hot_server_row_identity(default)
        best_execution_identity = hot_server_execution_identity(best)
        default_execution_identity = hot_server_execution_identity(default)
        best_is_default = best_execution_identity == default_execution_identity
        candidate_confirmation_row = candidate_confirmations.get(
            (key, best_confirmation_identity)
        )
        candidate_confirmation_source = "candidate_confirmation"
        action_confirmation_freshness = candidate_confirmation_freshness
        focus_confirmation_row = promotion_focus_confirmations.get(
            (key, best_confirmation_identity)
        )
        if focus_confirmation_row is not None and promotion_focus_freshness == "fresh":
            candidate_confirmation_row = focus_confirmation_row
            candidate_confirmation_source = "promotion_focus"
            action_confirmation_freshness = promotion_focus_freshness
        elif candidate_confirmation_row is None:
            candidate_confirmation_source = "missing"
            action_confirmation_freshness = "missing"
        default_confirmation_row = default_confirmations.get(
            (key, default_confirmation_identity)
        )
        candidate_status = confirmation_status(candidate_confirmation_row)
        default_status = confirmation_status(default_confirmation_row)
        default_median_speedup = default.get("median_circle_speedup")
        best_median_speedup = best.get("median_circle_speedup")
        median_gain = ratio_or_none_any(best_median_speedup, default_median_speedup)
        action = high_offset_promotion_action(
            best_is_default=best_is_default,
            best_median_speedup=best_median_speedup,
            median_gain_over_default=median_gain,
            candidate_status=candidate_status,
            candidate_confirmation_freshness=action_confirmation_freshness,
        )
        rows.append(
            {
                "low": best["low"],
                "high": best["high"],
                "baseline": best["baseline"],
                "default": default,
                "best": best,
                "best_is_default": best_is_default,
                "median_gain_over_default": median_gain,
                "default_confirmation_status": default_status,
                "candidate_confirmation_status": candidate_status,
                "candidate_confirmation_source": candidate_confirmation_source,
                "candidate_confirmation_freshness": action_confirmation_freshness,
                "action": action,
            }
        )

    return {
        "available": bool(rows),
        "candidate_confirmation_generated_at_utc": candidate_confirmation_generated_at,
        "promotion_focus_confirmation_generated_at_utc": promotion_focus_generated_at,
        "hot_server_finished_at_utc": hot_server_finished_at,
        "candidate_confirmation_freshness": candidate_confirmation_freshness,
        "promotion_focus_confirmation_freshness": promotion_focus_freshness,
        "rows": rows,
    }


def summarize_high_offset_shifted_candidate_readout(
    shifted_summary: dict[str, Any],
) -> dict[str, Any]:
    if not shifted_summary.get("available"):
        return {"available": False, "rows": []}

    default_rows = {
        range_baseline_key(row): row
        for row in shifted_summary.get("default_by_range_baseline", [])
    }
    rows = []
    for best in shifted_summary.get("best_by_range_baseline", []):
        key = range_baseline_key(best)
        default = default_rows.get(key)
        if default is None:
            continue

        best_execution_identity = hot_server_execution_identity(best)
        default_execution_identity = hot_server_execution_identity(default)
        best_is_default = best_execution_identity == default_execution_identity
        default_median_speedup = default.get("median_circle_speedup")
        best_median_speedup = best.get("median_circle_speedup")
        median_gain = ratio_or_none_any(best_median_speedup, default_median_speedup)
        action = high_offset_shifted_candidate_action(
            best_is_default=best_is_default,
            best_median_speedup=best_median_speedup,
            median_gain_over_default=median_gain,
        )
        rows.append(
            {
                "low": best["low"],
                "high": best["high"],
                "baseline": best["baseline"],
                "default": default,
                "best": best,
                "best_is_default": best_is_default,
                "median_gain_over_default": median_gain,
                "action": action,
            }
        )

    metadata = shifted_summary.get("metadata", {})
    return {
        "available": bool(rows),
        "min_gain_ratio": HIGH_OFFSET_SHIFTED_CANDIDATE_MIN_GAIN_RATIO,
        "batch_request_profile": metadata.get("batch_request_profile"),
        "batch_size": metadata.get("batch_size"),
        "batch_shift": metadata.get("batch_shift"),
        "rounds": metadata.get("rounds"),
        "warmup_rounds": metadata.get("warmup_rounds"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rows": rows,
    }


def range_baseline_key(row: dict[str, Any]) -> tuple[int, int, str]:
    return (int(row["low"]), int(row["high"]), str(row["baseline"]))


def hot_server_row_identity(row: dict[str, Any]) -> tuple[str, int, int | None, int | None]:
    return (
        str(row.get("count_mode") or ""),
        int(row.get("segment_size") or 0),
        parse_identity_int(row.get("circle_threads")),
        parse_identity_int(row.get("circle_requested_threads")),
    )


def hot_server_execution_identity(row: dict[str, Any]) -> tuple[str, int, int | None]:
    effective_threads = first_identity_int(
        row.get("circle_threads"),
        row.get("threads"),
        row.get("circle_requested_threads"),
        row.get("requested_threads"),
    )
    return (
        str(row.get("count_mode") or ""),
        int(row.get("segment_size") or 0),
        effective_threads,
    )


def confirmation_row_identity(row: dict[str, Any]) -> tuple[str, int, int | None, int | None]:
    return (
        str(row.get("count_mode") or ""),
        int(row.get("segment_size") or 0),
        parse_identity_int(row.get("threads")),
        parse_identity_int(row.get("requested_threads")),
    )


def parse_identity_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def first_identity_int(*values: Any) -> int | None:
    for value in values:
        parsed = parse_identity_int(value)
        if parsed is not None:
            return parsed
    return None


def confirmation_rows_by_range_and_identity(
    summary: dict[str, Any],
) -> dict[tuple[tuple[int, int, str], tuple[str, int, int | None, int | None]], dict[str, Any]]:
    rows = {}
    if not summary.get("available"):
        return rows
    source_rows = summary.get("identity_summaries") or summary.get("winners", [])
    for row in source_rows:
        key = (int(row["low"]), int(row["high"]), str(row["baseline"]))
        rows[(key, confirmation_row_identity(row))] = row
    return rows


def confirmation_winner_rows_by_range_and_identity(
    summary: dict[str, Any],
) -> dict[tuple[tuple[int, int, str], tuple[str, int, int | None, int | None]], dict[str, Any]]:
    rows = {}
    if not summary.get("available"):
        return rows
    for row in summary.get("winners", []):
        key = (int(row["low"]), int(row["high"]), str(row["baseline"]))
        rows[(key, confirmation_row_identity(row))] = row
    return rows


def confirmation_status(row: dict[str, Any] | None) -> str:
    if row is None:
        return "missing"
    return str(row.get("status") or "missing")


def confirmation_freshness(
    confirmation_generated_at: Any,
    benchmark_finished_at: Any,
) -> str:
    confirmation_time = parse_utc_timestamp(confirmation_generated_at)
    benchmark_time = parse_utc_timestamp(benchmark_finished_at)
    if confirmation_time is None or benchmark_time is None:
        return "unknown"
    if confirmation_time < benchmark_time:
        return "stale"
    return "fresh"


def parse_utc_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y%m%dT%H%M%SZ"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def ratio_or_none_any(numerator: Any, denominator: Any) -> float | None:
    if numerator is None or denominator is None:
        return None
    denominator = float(denominator)
    if denominator == 0.0:
        return None
    return float(numerator) / denominator


def high_offset_promotion_action(
    *,
    best_is_default: bool,
    best_median_speedup: Any,
    median_gain_over_default: float | None,
    candidate_status: str,
    candidate_confirmation_freshness: str,
) -> str:
    if best_is_default:
        return "keep_default"
    if best_median_speedup is None or float(best_median_speedup) < 1.0:
        return "reject_candidate"
    if candidate_status != "confirmed":
        return "hold_unconfirmed_candidate"
    if candidate_confirmation_freshness == "stale":
        return "hold_stale_candidate_confirmation"
    if candidate_confirmation_freshness != "fresh":
        return "hold_unfresh_candidate_confirmation"
    if (
        median_gain_over_default is None
        or median_gain_over_default < HIGH_OFFSET_PROMOTION_MIN_GAIN_RATIO
    ):
        return "hold_small_gain_candidate"
    return "trial_candidate_default"


def high_offset_shifted_candidate_action(
    *,
    best_is_default: bool,
    best_median_speedup: Any,
    median_gain_over_default: float | None,
) -> str:
    if best_is_default:
        return "keep_default"
    if best_median_speedup is None or float(best_median_speedup) < 1.0:
        return "reject_candidate"
    if (
        median_gain_over_default is None
        or median_gain_over_default < HIGH_OFFSET_SHIFTED_CANDIDATE_MIN_GAIN_RATIO
    ):
        return "hold_small_gain_candidate"
    return "trial_shifted_candidate"


def summarize_prefix_pi_thread_comparisons(
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    comparisons = []
    for (low, high, baseline), candidates in sorted(grouped.items()):
        serial_candidates = [
            row
            for row in candidates
            if row.get("count_mode") == "prefix-pi"
            and row.get("circle_threads") == 1
            and not is_adaptive_default_row(str(row["name"]))
        ]
        has_prefix_pi_serial = bool(serial_candidates)
        default_candidates = [
            row
            for row in candidates
            if is_adaptive_default_row(str(row["name"]))
            and (row.get("circle_threads") or 0) > 1
            and (
                row.get("count_mode") == "prefix-pi"
                or (row.get("count_mode") is None and has_prefix_pi_serial)
            )
        ]
        if not serial_candidates or not default_candidates:
            continue

        serial = min(serial_candidates, key=lambda row: (row["median_ms"], row["name"]))
        default = min(default_candidates, key=lambda row: (row["median_ms"], row["name"]))
        thread_speedup = (
            serial["median_ms"] / default["median_ms"]
            if default["median_ms"] > 0.0
            else None
        )
        comparisons.append(
            {
                "low": low,
                "high": high,
                "baseline": baseline,
                "serial": serial,
                "default": default,
                "thread_speedup": thread_speedup,
                "verdict": (
                    "default_faster"
                    if thread_speedup is not None and thread_speedup >= 1.0
                    else "serial_faster"
                ),
            }
        )
    return comparisons


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
            "include_primesieve_count_server": False,
            "include_primecount_pi_server": False,
            "include_circle_count_binary": False,
            "include_circle_count_binary_server": False,
            "required_external_tools": [],
            "warmup_rounds": 0,
            "batch_size": 1,
            "batch_request_profile": "identical",
            "batch_shift": 0,
        }
    tools = metadata.get("tools", {})
    return {
        "available": True,
        "started_at_utc": metadata.get("started_at_utc"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rounds": metadata.get("rounds"),
        "batch_size": int(metadata.get("batch_size") or 1),
        "batch_request_profile": metadata.get("batch_request_profile", "identical"),
        "batch_shift": int(metadata.get("batch_shift") or 0),
        "warmup_rounds": int(metadata.get("warmup_rounds") or 0),
        "row_count": metadata.get("row_count"),
        "interleaved": bool(metadata.get("interleaved")),
        "include_circle_count_binary": bool(
            metadata.get("include_circle_count_binary")
        ),
        "include_circle_count_binary_server": bool(
            metadata.get("include_circle_count_binary_server")
        ),
        "include_circle_server": bool(metadata.get("include_circle_server")),
        "include_primesieve_count_server": bool(
            metadata.get("include_primesieve_count_server")
        ),
        "include_primecount_pi_server": bool(
            metadata.get("include_primecount_pi_server")
        ),
        "sample_output": metadata.get("sample_output"),
        "circle_prime_defaults": fingerprint_summary(
            metadata.get("circle_prime_defaults")
        ),
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
                "source": tool.get("source"),
                "method": tool.get("method"),
                "error": tool.get("error"),
                "binary": fingerprint_summary(tool.get("binary")),
                "defaults": fingerprint_summary(tool.get("defaults")),
                "small_prefix_pi_cache_limit": tool.get(
                    "small_prefix_pi_cache_limit"
                ),
                "small_prefix_pi_cache_default_limit": tool.get(
                    "small_prefix_pi_cache_default_limit"
                ),
                "small_prefix_pi_cache_max_limit": tool.get(
                    "small_prefix_pi_cache_max_limit"
                ),
                "small_prefix_pi_cache_limit_env": tool.get(
                    "small_prefix_pi_cache_limit_env"
                ),
                "small_prefix_pi_cache_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_estimated_bytes"
                ),
                "small_prefix_pi_cache_default_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_default_estimated_bytes"
                ),
                "small_prefix_pi_cache_max_estimated_bytes": tool.get(
                    "small_prefix_pi_cache_max_estimated_bytes"
                ),
                "small_prefix_pi_cache_warmup_profiles": tool.get(
                    "small_prefix_pi_cache_warmup_profiles", []
                ),
                "small_prefix_pi_cache_scope": tool.get(
                    "small_prefix_pi_cache_scope"
                ),
                "small_prefix_pi_cache_warmup": tool.get(
                    "small_prefix_pi_cache_warmup"
                ),
            }
            for name, tool in tools.items()
        },
    }


def summarize_external_control_provenance(
    artifacts: list[tuple[str, dict[str, Any] | None]],
) -> dict[str, Any]:
    rows = []
    for artifact, metadata in artifacts:
        if metadata is None:
            continue
        tools = metadata.get("tools", {})
        if not isinstance(tools, dict):
            continue
        for name in EXTERNAL_CONTROL_PROVENANCE_TOOLS:
            tool = tools.get(name)
            if not isinstance(tool, dict):
                continue
            if not tool_has_provenance(tool):
                continue
            rows.append(external_control_provenance_row(artifact, metadata, name, tool))
    return {
        "available": bool(rows),
        "rows": rows,
    }


def tool_has_provenance(tool: dict[str, Any]) -> bool:
    return any(
        tool.get(key)
        for key in [
            "available",
            "path",
            "version",
            "error",
        ]
    )


def external_control_provenance_row(
    artifact: str,
    metadata: dict[str, Any],
    name: str,
    tool: dict[str, Any],
) -> dict[str, Any]:
    binary = fingerprint_summary(tool.get("binary")) or {}
    source = fingerprint_summary(tool.get("source_fingerprint")) or {}
    return {
        "artifact": artifact,
        "tool": name,
        "available": bool(tool.get("available")),
        "version": first_nonempty_line(tool.get("version")),
        "path": tool.get("path") or binary.get("path"),
        "method": tool.get("method"),
        "error": tool.get("error"),
        "binary_sha256": binary.get("sha256"),
        "binary_size_bytes": binary.get("size_bytes"),
        "source_sha256": source.get("sha256"),
        "source_path": source.get("path") or tool.get("source"),
        "started_at_utc": metadata.get("started_at_utc"),
        "finished_at_utc": metadata.get("finished_at_utc"),
        "rounds": metadata.get("rounds"),
        "batch_size": metadata.get("batch_size"),
        "batch_request_profile": metadata.get("batch_request_profile", "identical"),
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
            "primecount_next_max_start": None,
            "next_external_check_count": 0,
        }
    failures = [
        check
        for check in summary.get("checks", [])
        if not bool(check.get("passes"))
    ]
    count_server_failures = [
        check
        for check in summary.get("count_server_checks", [])
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
        "count_server_check_count": int(
            summary.get("count_server_check_count")
            or len(summary.get("count_server_checks", []))
        ),
        "enumeration_check_count": int(
            summary.get("enumeration_check_count")
            or len(summary.get("enumeration_checks", []))
        ),
        "next_check_count": int(
            summary.get("next_check_count") or len(summary.get("next_checks", []))
        ),
        "next_external_check_count": int(
            summary.get("next_external_check_count")
            or sum(
                len(check.get("external_primes", {}))
                or int(check.get("external_prime") is not None)
                for check in summary.get("next_checks", [])
            )
        ),
        "failure_count": int(
            summary.get("failure_count")
            or len(failures)
            + len(count_server_failures)
            + len(enumeration_failures)
            + len(next_failures)
        ),
        "count_failure_count": int(summary.get("count_failure_count") or len(failures)),
        "count_server_failure_count": int(
            summary.get("count_server_failure_count") or len(count_server_failures)
        ),
        "enumeration_failure_count": int(
            summary.get("enumeration_failure_count") or len(enumeration_failures)
        ),
        "next_failure_count": int(summary.get("next_failure_count") or len(next_failures)),
        "ranges": summary.get("ranges", []),
        "enumeration_ranges": summary.get("enumeration_ranges", []),
        "next_starts": summary.get("next_starts", []),
        "primecount_next_max_start": summary.get("primecount_next_max_start"),
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
        "count_server_failures": count_server_failures,
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
        "count_mode": infer_count_mode(row.get("name", ""), row.get("count_mode")),
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


def safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0.0:
        return None
    return numerator / denominator


def format_optional_code(value: str | None) -> str:
    return "n/a" if value is None else f"`{value}`"


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
        return {"available": False, "winners": [], "identity_summaries": []}
    return {
        "available": True,
        "generated_at_utc": summary.get("generated_at_utc"),
        "min_confirmations": summary.get("min_confirmations"),
        "require_stable_samples": summary.get("require_stable_samples"),
        "batch_size": summary.get("batch_size"),
        "observed_group_count": summary.get("observed_group_count", 0),
        "confirmed_count": summary.get("confirmed_count", 0),
        "unconfirmed_count": summary.get("unconfirmed_count", 0),
        "winners": [
            confirmation_row_summary(row) for row in summary.get("winners", [])
        ],
        "identity_summaries": [
            confirmation_row_summary(row)
            for row in summary.get("identity_summaries", [])
        ],
        "input_metadata": summarize_confirmation_input_metadata(summary),
    }


def summarize_confirmation_input_metadata(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in summary.get("input_metadata", []):
        circle_prime = row.get("circle_prime") or {}
        binary = circle_prime.get("binary") or {}
        defaults = row.get("circle_prime_defaults") or circle_prime.get("defaults") or {}
        rows.append(
            {
                "input": row.get("input"),
                "metadata": row.get("metadata"),
                "metadata_available": row.get("metadata_available"),
                "started_at_utc": row.get("started_at_utc"),
                "finished_at_utc": row.get("finished_at_utc"),
                "rounds": row.get("rounds"),
                "batch_size": row.get("batch_size"),
                "warmup_rounds": row.get("warmup_rounds"),
                "circle_binary_sha256": binary.get("sha256"),
                "circle_binary_modified_at_utc": binary.get("modified_at_utc"),
                "defaults_sha256": defaults.get("sha256"),
                "defaults_modified_at_utc": defaults.get("modified_at_utc"),
            }
        )
    return rows


def confirmation_row_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
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
        "median_ms_values": [float(value) for value in row.get("median_ms_values", [])],
        "median_speedup_values": [
            float(value) for value in row.get("median_speedup_values", [])
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

    lines.extend(
        render_external_control_provenance_markdown(
            report["external_control_provenance"]
        )
    )
    lines.extend(render_external_correctness_markdown(report["external_correctness"]))
    lines.extend(render_external_markdown(report["external"]))
    lines.extend(render_external_next_markdown(report["external_next"]))
    lines.extend(
        render_external_next_markdown(
            report["external_next_server"],
            title="External Next-Prime Server-Only Search",
            missing_message="No server-only next-prime benchmark artifact was available.",
        )
    )
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
        render_external_segment_sweep_markdown(
            report["external_high_offset_hot_server"],
            title="High-Offset Hot-Server Scorecard",
            missing_message="No high-offset hot-server scorecard artifact was available.",
            default_label="Adaptive default hot-server scorecard:",
            best_label="Best hot-server candidate scorecard:",
            spread_label="High-offset hot-server candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_high_offset_count_binary_markdown(
            report["external_high_offset_count_binary"]
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_count_binary_sweep"],
            title="High-Offset Count-Binary Mode/Segment Sweep",
            missing_message=(
                "No high-offset count-binary mode/segment sweep artifact was available."
            ),
            default_label="Adaptive count-binary mode/segment scorecard:",
            best_label="Best count-binary mode/segment candidate scorecard:",
            spread_label="High-offset count-binary mode/segment candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_count_binary_candidate_confirm"],
            title="High-Offset Count-Binary Candidate Confirmation",
            missing_message=(
                "No high-offset count-binary candidate confirmation artifact was "
                "available."
            ),
            default_label="Focused cold default scorecard:",
            best_label="Focused cold candidate scorecard:",
            spread_label="Focused cold candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_shifted_hot_server"],
            title="High-Offset Shifted Hot-Server Scorecard",
            missing_message=(
                "No high-offset shifted hot-server scorecard artifact was available."
            ),
            default_label="Adaptive default shifted scorecard:",
            best_label="Best shifted candidate scorecard:",
            spread_label="High-offset shifted candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_high_offset_shifted_count_binary"],
            title="High-Offset Shifted Count-Binary Scorecard",
            missing_message=(
                "No high-offset shifted count-binary scorecard artifact was available."
            ),
            default_label="Adaptive shifted count-binary scorecard:",
            best_label="Best shifted count-binary candidate scorecard:",
            spread_label="High-offset shifted count-binary candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_external_segment_sweep_markdown(
            report["external_competitive_smoke"],
            title="Competitive Smoke Scorecard",
            missing_message="No competitive smoke scorecard artifact was available.",
            default_label="Fresh shifted count-binary smoke scorecard:",
            best_label="Best competitive smoke candidate scorecard:",
            spread_label="Competitive smoke candidate spread:",
            include_circle_row=True,
        )
    )
    lines.extend(
        render_high_offset_shifted_candidate_readout_markdown(
            report["external_high_offset_shifted_candidate_readout"]
        )
    )
    lines.extend(
        render_high_offset_promotion_readout_markdown(
            report["external_high_offset_promotion_readout"]
        )
    )
    lines.extend(
        render_external_mode_confirmation_markdown(
            report["external_high_offset_promotion_focus"],
            title="High-Offset Promotion Focus Confirmation",
            missing_message=(
                "No focused high-offset promotion confirmation artifact was "
                "available."
            ),
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
        render_external_mode_confirmation_markdown(
            report["external_high_offset_candidate_confirmation"],
            title="High-Offset Candidate Confirmation",
            missing_message=(
                "No repeated high-offset candidate confirmation artifact was "
                "available."
            ),
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
            default_label="Adaptive default scorecard:",
            best_label="Best candidate scorecard:",
            thread_comparison_label="Prefix-pi thread comparison:",
            spread_label="Throughput segment candidate spread:",
            include_circle_row=True,
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
        or summary.get("count_server_check_count")
        or summary.get("enumeration_check_count")
        or summary.get("next_check_count")
    ):
        lines.append(
            f"Count checks: `{summary.get('count_check_count', 0)}`; "
            f"count-server checks: `{summary.get('count_server_check_count', 0)}`; "
            f"enumeration checks: `{summary.get('enumeration_check_count', 0)}`; "
            f"next-prime checks: `{summary.get('next_check_count', 0)}`."
        )
    if summary.get("next_external_check_count"):
        lines.append(
            "Next-prime external oracle comparisons: "
            f"`{summary.get('next_external_check_count', 0)}`."
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
    if summary.get("primecount_next_max_start") is not None:
        lines.append(
            "Primecount next-prime checks capped at start "
            f"`{summary['primecount_next_max_start']}`."
        )
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
    ]
    cold_summary = summary.get("cold_cli", summary)
    server_summary = summary.get("server", {})
    external_server_summary = summary.get("external_server", {})
    lines.append(external_lane_summary_line("primesieve", "cold CLI", cold_summary))
    if server_summary.get("primesieve_rows", 0):
        lines.append(external_lane_summary_line("primesieve", "server", server_summary))
    if external_server_summary.get("primesieve_count_server_rows", 0):
        lines.append(
            external_lane_summary_line(
                "libprimesieve count server",
                "external server",
                external_server_summary,
            )
        )
    lines.append(external_lane_summary_line("primecount", "cold CLI", cold_summary))
    if server_summary.get("primecount_rows", 0):
        lines.append(external_lane_summary_line("primecount", "server", server_summary))
    if external_server_summary.get("primecount_pi_server_rows", 0):
        lines.append(
            external_lane_summary_line(
                "libprimecount pi server",
                "external server",
                external_server_summary,
            )
        )
    lines.append("")
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


def render_external_control_provenance_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## External Control Provenance", ""]
    rows = summary.get("rows", [])
    if not rows:
        lines.append("No external-control provenance metadata was available.")
        lines.append("")
        return lines

    lines.extend(
        [
            "| Artifact | Tool | Status | Version / Method | Path | Hashes |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        status = "available" if row.get("available") else "unavailable"
        version_or_method = row.get("version") or row.get("method") or row.get("error") or ""
        path = row.get("path") or ""
        hashes = external_control_hash_text(row)
        lines.append(
            f"| `{row.get('artifact', '')}` | `{row.get('tool', '')}` | "
            f"`{status}` | {markdown_cell(version_or_method)} | "
            f"{markdown_cell(path)} | {markdown_cell(hashes)} |"
        )
    lines.append("")
    return lines


def external_control_hash_text(row: dict[str, Any]) -> str:
    parts = []
    binary_sha = row.get("binary_sha256")
    source_sha = row.get("source_sha256")
    if binary_sha:
        parts.append(f"bin {str(binary_sha)[:12]}")
    if source_sha:
        parts.append(f"src {str(source_sha)[:12]}")
    return ", ".join(parts)


def markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("|", "\\|")
    return f"`{text}`" if text else ""


def render_high_offset_count_binary_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## High-Offset Count Binary", ""]
    if not summary["available"]:
        lines.append("No high-offset count-binary probe artifact was available.")
        lines.append("")
        return lines

    focus_rows = summary.get("focus_rows", [])
    lines.append(
        f"Focused rows: `{len(focus_rows)}`; median wins: "
        f"`{summary.get('focus_median_wins', 0)}/{len(focus_rows)}`; "
        f"best-time wins: `{summary.get('focus_best_wins', 0)}/{len(focus_rows)}`."
    )
    metadata = summary.get("metadata", {})
    if metadata.get("available"):
        rounds = metadata.get("rounds")
        batch_size = metadata.get("batch_size")
        warmup_rounds = metadata.get("warmup_rounds")
        if rounds is not None:
            lines.append(
                f"Probe shape: rounds `{rounds}`, batch `{batch_size}`, "
                f"warmup `{warmup_rounds}`."
            )
        count_tool = metadata.get("tools", {}).get("circle_prime_count", {})
        if count_tool:
            lines.append(render_tool_binary_bullet("circle-prime-count", count_tool))
        if metadata.get("include_circle_count_binary"):
            lines.append("- standalone `circle-prime-count` rows included.")
        if metadata.get("include_circle_count_binary_server"):
            lines.append("- slim `circle-prime-count count-server` rows included.")
        if metadata.get("include_primesieve_count_server"):
            lines.append("- libprimesieve count-server rows included.")
        if metadata.get("include_primecount_pi_server"):
            lines.append("- libprimecount pi-server rows included.")
    lines.append("")

    if focus_rows:
        lines.extend(
            [
                "| Lane | Range | Circle Row | Baseline | Circle Median ms | Baseline Median ms | Best Speedup | Median Speedup | Samples | Verdict |",
                "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in focus_rows:
            lines.append(
                f"| {row['role_label']} | [{row['low']}, {row['high']}) | "
                f"{circle_row_label(row)} | "
                f"`{external_count_baseline_label(row['baseline'])}` | "
                f"{row['median_ms']:.3f} | "
                f"{format_optional_ms(row['baseline_median_ms'])} | "
                f"{row['circle_speedup']:.3f} | "
                f"{row['median_circle_speedup']:.3f} | "
                f"{sample_stability_text(row)} | {row['verdict']} |"
            )
        lines.append("")

    overhead_rows = summary.get("cold_hot_overhead", [])
    if overhead_rows:
        lines.extend(
            [
                "Cold-binary overhead diagnosis:",
                "",
                "| Range | Cold Count Binary Median ms | Hot Count Binary Server Median ms | Circle Cold/Hot | Circle Extra ms | primesieve CLI/lib | Cold vs primesieve | Hot count binary vs libprimesieve |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in overhead_rows:
            lines.append(
                f"| [{row['low']}, {row['high']}) | "
                f"{row['cold_count_binary_median_ms']:.3f} | "
                f"{row['hot_count_binary_server_median_ms']:.3f} | "
                f"{format_optional_ratio(row['circle_cold_over_hot_median'])} | "
                f"{format_optional_ms(row['circle_cold_extra_ms'])} | "
                f"{format_optional_ratio(row['primesieve_cli_over_lib_median'])} | "
                f"{row['cold_count_binary_vs_primesieve_median_speedup']:.3f} | "
                f"{row['hot_count_binary_server_vs_libprimesieve_median_speedup']:.3f} |"
            )
        lines.append("")
    return lines


def external_lane_summary_line(
    baseline_label: str,
    lane_label: str,
    summary: dict[str, Any],
) -> str:
    prefix_by_label = {
        "primesieve": "primesieve",
        "primecount": "primecount",
        "libprimesieve count server": "primesieve_count_server",
        "libprimecount pi server": "primecount_pi_server",
    }
    prefix = prefix_by_label[baseline_label]
    wins = summary.get(f"{prefix}_wins", 0)
    rows = summary.get(f"{prefix}_rows", 0)
    median_wins = summary.get(f"{prefix}_median_wins", wins)
    return (
        f"- `{baseline_label}` {lane_label}: Circle faster on {wins}/{rows} "
        f"rows by best time; median faster on {median_wins}/{rows} rows."
    )


def external_count_baseline_label(baseline: str) -> str:
    labels = {
        "external_primesieve_count": "primesieve CLI count",
        "external_primecount_pi_diff": "primecount CLI pi diff",
        "external_primesieve_count_server": "libprimesieve count server",
        "external_primecount_pi_diff_server": "libprimecount pi server",
    }
    return labels.get(baseline, baseline)


def render_tool_binary_bullet(label: str, tool: dict[str, Any]) -> str:
    path = tool.get("path") or "path unavailable"
    version = tool.get("version") or "version unavailable"
    binary = tool.get("binary") or {}
    sha = binary.get("sha256")
    size = binary.get("size_bytes")
    fingerprint_parts = []
    if sha:
        fingerprint_parts.append(f"sha `{str(sha)[:12]}`")
    if size is not None:
        fingerprint_parts.append(f"size `{size}` bytes")
    fingerprint = ""
    if fingerprint_parts:
        fingerprint = "; " + ", ".join(fingerprint_parts)
    return f"- `{label}`: {version} (`{path}`{fingerprint})."


def render_external_metadata_markdown(metadata: dict[str, Any]) -> list[str]:
    lines = ["Tool metadata:"]
    for name in ["circle_prime", "primesieve", "primecount"]:
        tool = metadata.get("tools", {}).get(name, {})
        available = tool.get("available")
        version = tool.get("version") or "version unavailable"
        path = tool.get("path") or "path unavailable"
        status = version if available else "not installed"
        lines.append(f"- `{name}`: {status} (`{path}`)")
    circle_count_server = metadata.get("tools", {}).get("circle_count_server", {})
    if circle_count_server:
        path = circle_count_server.get("path") or "path unavailable"
        method = circle_count_server.get("method") or "method unavailable"
        if circle_count_server.get("available"):
            lines.append(
                "- `circle_count_server`: available "
                f"(`{path}`); method `{method}`."
            )
            cache_limit = circle_count_server.get("small_prefix_pi_cache_limit")
            cache_default_limit = circle_count_server.get(
                "small_prefix_pi_cache_default_limit"
            )
            cache_max_limit = circle_count_server.get("small_prefix_pi_cache_max_limit")
            cache_limit_env = circle_count_server.get("small_prefix_pi_cache_limit_env")
            cache_estimated_bytes = circle_count_server.get(
                "small_prefix_pi_cache_estimated_bytes"
            )
            cache_default_estimated_bytes = circle_count_server.get(
                "small_prefix_pi_cache_default_estimated_bytes"
            )
            cache_max_estimated_bytes = circle_count_server.get(
                "small_prefix_pi_cache_max_estimated_bytes"
            )
            cache_warmup_profiles = circle_count_server.get(
                "small_prefix_pi_cache_warmup_profiles"
            ) or []
            cache_scope = circle_count_server.get("small_prefix_pi_cache_scope")
            cache_warmup = circle_count_server.get("small_prefix_pi_cache_warmup")
            if cache_limit is not None:
                detail = f"limit `{cache_limit}`"
                if cache_default_limit is not None:
                    detail += f"; default `{cache_default_limit}`"
                if cache_max_limit is not None:
                    detail += f"; max `{cache_max_limit}`"
                if cache_limit_env:
                    detail += f"; env `{cache_limit_env}`"
                detail += f"; scope {cache_scope}"
                lines.append(
                    "- `circle_count_server` small-prefix `pi` cache: "
                    f"{detail}."
                )
            if cache_estimated_bytes is not None:
                detail = f"estimated bytes `{cache_estimated_bytes}`"
                if cache_default_estimated_bytes is not None:
                    detail += f"; default bytes `{cache_default_estimated_bytes}`"
                if cache_max_estimated_bytes is not None:
                    detail += f"; max bytes `{cache_max_estimated_bytes}`"
                lines.append(
                    "- `circle_count_server` small-prefix `pi` cache memory: "
                    f"{detail}."
                )
            if cache_warmup_profiles:
                warmup_ms = [
                    profile.get("startup_warmup_ms")
                    for profile in cache_warmup_profiles
                    if profile.get("startup_warmup_ms") is not None
                ]
                if warmup_ms:
                    lines.append(
                        "- `circle_count_server` small-prefix `pi` cache startup "
                        f"warmup: min `{min(warmup_ms):.3f} ms`; "
                        f"median `{median(warmup_ms):.3f} ms`; "
                        f"max `{max(warmup_ms):.3f} ms`; "
                        f"samples `{len(warmup_ms)}`."
                    )
            if cache_warmup:
                lines.append(
                    "- `circle_count_server` small-prefix `pi` cache warmup: "
                    f"{cache_warmup}."
                )
        else:
            lines.append(f"- `circle_count_server`: not included (`{path}`)")
    primesieve_count_server = metadata.get("tools", {}).get("primesieve_count_server", {})
    if primesieve_count_server:
        path = primesieve_count_server.get("path") or "path unavailable"
        method = primesieve_count_server.get("method") or "method unavailable"
        if primesieve_count_server.get("available"):
            lines.append(
                "- `primesieve_count_server`: available "
                f"(`{path}`); method `{method}`."
            )
        else:
            status = primesieve_count_server.get("error") or "not built"
            lines.append(f"- `primesieve_count_server`: {status} (`{path}`)")
    primecount_pi_server = metadata.get("tools", {}).get("primecount_pi_server", {})
    if primecount_pi_server:
        path = primecount_pi_server.get("path") or "path unavailable"
        method = primecount_pi_server.get("method") or "method unavailable"
        if primecount_pi_server.get("available"):
            lines.append(
                "- `primecount_pi_server`: available "
                f"(`{path}`); method `{method}`."
            )
        else:
            status = primecount_pi_server.get("error") or "not built"
            lines.append(f"- `primecount_pi_server`: {status} (`{path}`)")
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
    warmup_rounds = int(metadata.get("warmup_rounds") or 0)
    if warmup_rounds:
        lines.append(f"- warmup: `{warmup_rounds}` unrecorded interleaved pass(es).")
    batch_size = int(metadata.get("batch_size") or 1)
    if batch_size > 1:
        lines.append(
            f"- repeated count requests per timed sample: `{batch_size}` "
            "(reported timings are per-request averages)."
        )
    batch_request_profile = metadata.get("batch_request_profile", "identical")
    if batch_request_profile != "identical":
        batch_shift = int(metadata.get("batch_shift") or 0)
        lines.append(
            f"- batch request profile: `{batch_request_profile}` "
            f"with shift `{batch_shift}`."
        )
    if metadata.get("include_circle_server"):
        lines.append("- Circle server rows: persistent `count-server` requests included.")
    if metadata.get("include_primesieve_count_server"):
        lines.append("- libprimesieve count-server rows included.")
    if metadata.get("include_primecount_pi_server"):
        lines.append("- libprimecount pi-server rows included.")
    if metadata.get("sample_output"):
        lines.append(f"- per-round samples: `{metadata['sample_output']}`.")
    lines.append("")
    return lines


def render_external_next_markdown(
    summary: dict[str, Any],
    *,
    title: str = "External Next-Prime Search",
    missing_message: str = "No external next-prime benchmark artifact was available.",
) -> list[str]:
    lines = [
        f"## {title}",
        "",
    ]
    if not summary["available"]:
        lines.append(missing_message)
        lines.append("")
        return lines

    cold_summary = summary.get("cold_cli", summary)
    server_summary = summary.get("server", {})
    lines.extend(external_next_lane_summary_lines("cold CLI", cold_summary))
    if server_summary.get("baseline_rows", 0):
        lines.extend(external_next_lane_summary_lines("server", server_summary))
    lines.append("")
    metadata = summary.get("metadata", {})
    if metadata.get("available"):
        lines.extend(render_external_next_metadata_markdown(metadata))
    if summary["speedups"]:
        lines.extend(
            [
                "| Start | Baseline | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |",
                "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in summary["speedups"]:
            baseline_ms = (
                "n/a"
                if row["baseline_best_ms"] is None
                else f"{row['baseline_best_ms']:.3f}"
            )
            lines.append(
                f"| {row['start']} | `{external_next_baseline_label(row['baseline'])}` | "
                f"{row['result']} | {row['candidate_count']} | "
                f"{row['batch_size']} | {row['best_ms']:.3f} | {baseline_ms} | "
                f"{row['circle_speedup']:.3f} | {row['median_circle_speedup']:.3f} | "
                f"{sample_stability_text(row)} | {row['verdict']} |"
            )
        lines.append("")
    return lines


def external_next_lane_summary_lines(
    lane_label: str,
    summary: dict[str, Any],
) -> list[str]:
    by_baseline = summary.get("by_baseline") or {}
    if not by_baseline:
        return []
    lines = []
    for baseline in sorted(by_baseline, key=external_next_baseline_sort_key):
        counts = by_baseline[baseline]
        rows = counts.get("rows", 0)
        lines.append(
            f"- `{external_next_baseline_label(baseline)}` {lane_label}: "
            f"Circle faster on {counts.get('wins', 0)}/{rows} rows by best time; "
            f"median faster on {counts.get('median_wins', 0)}/{rows} rows."
        )
    return lines


def external_next_baseline_sort_key(baseline: str) -> tuple[int, str]:
    order = {
        "external_primesieve_generate_next_server": 0,
        "external_primesieve_iterator_next_server": 1,
        "external_primesieve_next_prime": 2,
        "external_primecount_next_prime": 3,
        "external_primecount_next_server": 4,
    }
    return (order.get(baseline, 99), baseline)


def external_next_baseline_label(baseline: str) -> str:
    labels = {
        "external_primesieve_generate_next_server": "libprimesieve generate_n_primes server",
        "external_primesieve_iterator_next_server": "libprimesieve iterator server",
        "external_primesieve_next_prime": "primesieve --nth-prime",
        "external_primecount_next_prime": "primecount pi+nth-prime",
        "external_primecount_next_server": "libprimecount pi+nth-prime server",
    }
    return labels.get(baseline, baseline)


def render_external_next_metadata_markdown(metadata: dict[str, Any]) -> list[str]:
    lines = ["Tool metadata:"]
    tool_names = ["circle_prime"]
    if not metadata.get("server_only"):
        tool_names.append("primesieve")
    if metadata.get("include_primecount"):
        tool_names.append("primecount")
    for name in tool_names:
        tool = metadata.get("tools", {}).get(name, {})
        available = tool.get("available")
        version = tool.get("version") or "version unavailable"
        path = tool.get("path") or "path unavailable"
        status = version if available else "not installed"
        lines.append(f"- `{name}`: {status} (`{path}`)")
    library_tool = metadata.get("tools", {}).get("primesieve_library_server", {})
    if library_tool:
        path = library_tool.get("path") or "path unavailable"
        method = library_tool.get("method") or "method unavailable"
        if library_tool.get("available"):
            lines.append(
                "- `primesieve_library_server`: available "
                f"(`{path}`); method `{method}`."
            )
        else:
            status = library_tool.get("error") or "not built"
            lines.append(f"- `primesieve_library_server`: {status} (`{path}`)")
    iterator_tool = metadata.get("tools", {}).get("primesieve_iterator_server", {})
    if iterator_tool:
        path = iterator_tool.get("path") or "path unavailable"
        method = iterator_tool.get("method") or "method unavailable"
        if iterator_tool.get("available"):
            lines.append(
                "- `primesieve_iterator_server`: available "
                f"(`{path}`); method `{method}`."
            )
        else:
            status = iterator_tool.get("error") or "not built"
            lines.append(f"- `primesieve_iterator_server`: {status} (`{path}`)")
    primecount_library_tool = metadata.get("tools", {}).get(
        "primecount_library_server",
        {},
    )
    if primecount_library_tool:
        path = primecount_library_tool.get("path") or "path unavailable"
        method = primecount_library_tool.get("method") or "method unavailable"
        if primecount_library_tool.get("available"):
            lines.append(
                "- `primecount_library_server`: available "
                f"(`{path}`); method `{method}`."
            )
        else:
            status = primecount_library_tool.get("error") or "not built"
            lines.append(f"- `primecount_library_server`: {status} (`{path}`)")
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
    if metadata.get("server_only"):
        lines.append(
            "- server-only mode: cold CLI rows skipped; persistent Circle "
            "`next-server` is compared directly with persistent `libprimesieve`."
        )
    if metadata.get("include_circle_server"):
        lines.append("- Circle server rows: persistent `next-server` requests included.")
    if metadata.get("include_primecount"):
        cap = metadata.get("primecount_max_start")
        if cap is None:
            lines.append("- `primecount` next-prime rows included where available.")
        else:
            lines.append(
                "- `primecount` next-prime rows included for starts at or below "
                f"`{cap}`."
            )
    if metadata.get("include_primesieve_library_server"):
        cap = metadata.get("primesieve_library_max_start")
        if cap is None:
            lines.append("- libprimesieve next-prime helper rows included where available.")
        else:
            lines.append(
                "- libprimesieve next-prime helper rows included for starts at or below "
                f"`{cap}`."
            )
    if metadata.get("include_primesieve_iterator_server"):
        cap = metadata.get("primesieve_library_max_start")
        if cap is None:
            lines.append("- libprimesieve iterator helper rows included where available.")
        else:
            lines.append(
                "- libprimesieve iterator helper rows included for starts at or below "
                f"`{cap}`."
            )
    if metadata.get("include_primecount_library_server"):
        cap = metadata.get("primecount_library_max_start")
        if cap is None:
            lines.append("- libprimecount next-prime helper rows included where available.")
        else:
            lines.append(
                "- libprimecount next-prime helper rows included for starts at or below "
                f"`{cap}`."
            )
    required_tools = metadata.get("required_external_tools") or []
    if required_tools:
        formatted = ", ".join(f"`{tool}`" for tool in required_tools)
        lines.append(f"- required external controls: {formatted}.")
    if metadata.get("sample_output"):
        lines.append(f"- per-round samples: `{metadata['sample_output']}`.")
    lines.append("")
    return lines


def infer_count_mode(name: str, explicit: str | None) -> str | None:
    explicit_mode = (explicit or "").strip()
    if explicit_mode:
        return explicit_mode

    if "prefix_pi" in name:
        return "prefix-pi"
    return None


def circle_row_label(row: dict[str, Any]) -> str:
    label = f"`{row['name']}`"
    count_mode = row.get("count_mode")
    if count_mode:
        label += f"<br>mode: `{count_mode}`"
    return label


def external_candidate_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("low"),
        row.get("high"),
        row.get("baseline"),
        row.get("name"),
        row.get("segment_size"),
        row.get("circle_threads"),
        row.get("circle_requested_threads"),
        row.get("count_mode"),
    )


def is_adaptive_default_row(name: str) -> bool:
    return "_default_count" in name


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
    if summary.get("batch_size"):
        lines.append(
            "Fresh-run count requests per timed sample: "
            f"`{summary['batch_size']}`."
        )
    lines.append("")
    if summary["winners"]:
        lines.extend(
            [
                "| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
            ]
        )
        for row in summary["winners"]:
            medians = ", ".join(f"{value:.3f}" for value in row["median_ms_values"])
            speedups = ", ".join(
                f"{value:.3f}" for value in row.get("median_speedup_values", [])
            )
            speedups = speedups or "-"
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                f"`{row['count_mode']}` | {row['segment_size']} | "
                f"{thread_text(row.get('threads'), row.get('requested_threads'))} | "
                f"{row['confirmation_count']}/{summary['min_confirmations']} | "
                f"{row['stable_observed_count']}/{row['observed_count']} | "
                f"{medians} | {speedups} | `{row['status']}` |"
            )
        lines.append("")
    return lines


def render_high_offset_promotion_readout_markdown(summary: dict[str, Any]) -> list[str]:
    lines = ["## High-Offset Promotion Readout", ""]
    if not summary.get("available"):
        lines.append("No high-offset promotion readout was available.")
        lines.append("")
        return lines

    lines.append(
        "Confirmed non-default candidates require at least "
        f"`{HIGH_OFFSET_PROMOTION_MIN_GAIN_RATIO:.3f}x` median gain over the "
        "current adaptive default and fresh candidate-confirmation evidence "
        "before this readout marks them as trial-ready."
    )
    lines.append("")

    lines.extend(
        [
            "| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Default Confirm | Candidate Confirm | Candidate Freshness | Action |",
            "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in summary["rows"]:
        default = row["default"]
        best = row["best"]
        gain = row.get("median_gain_over_default")
        gain_text = "-" if gain is None else f"{gain:.3f}x"
        lines.append(
            f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
            + f"{mode_segment_thread_text(default)} | "
            + f"{default['median_circle_speedup']:.3f} | "
            + f"{mode_segment_thread_text(best)} | "
            + f"{best['median_circle_speedup']:.3f} | "
            + f"{gain_text} | "
            + f"`{row['default_confirmation_status']}` | "
            + f"`{row['candidate_confirmation_status']}` | "
            + f"`{row['candidate_confirmation_freshness']}` | "
            + f"`{row['action']}` |"
        )
    lines.append("")
    return lines


def render_high_offset_shifted_candidate_readout_markdown(
    summary: dict[str, Any],
) -> list[str]:
    lines = ["## High-Offset Shifted Candidate Readout", ""]
    if not summary.get("available"):
        lines.append("No high-offset shifted candidate readout was available.")
        lines.append("")
        return lines

    lines.append(
        "Shifted candidates require at least "
        f"`{HIGH_OFFSET_SHIFTED_CANDIDATE_MIN_GAIN_RATIO:.3f}x` median gain "
        "over the adaptive default before this readout marks them as "
        "trial-ready for fresh-interval optimization."
    )
    profile = summary.get("batch_request_profile")
    batch_size = summary.get("batch_size")
    batch_shift = summary.get("batch_shift")
    rounds = summary.get("rounds")
    if profile is not None:
        lines.append(
            "Artifact profile: "
            f"`{profile}`, batch `{batch_size}`, shift `{batch_shift}`, "
            f"rounds `{rounds}`."
        )
    lines.append("")

    lines.extend(
        [
            "| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Action |",
            "| --- | --- | --- | ---: | --- | ---: | ---: | --- |",
        ]
    )
    for row in summary["rows"]:
        default = row["default"]
        best = row["best"]
        gain = row.get("median_gain_over_default")
        gain_text = "-" if gain is None else f"{gain:.3f}x"
        lines.append(
            f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
            + f"{mode_segment_thread_text(default)} | "
            + f"{default['median_circle_speedup']:.3f} | "
            + f"{mode_segment_thread_text(best)} | "
            + f"{best['median_circle_speedup']:.3f} | "
            + f"{gain_text} | "
            + f"`{row['action']}` |"
        )
    lines.append("")
    return lines


def mode_segment_thread_text(row: dict[str, Any]) -> str:
    return (
        f"`{row.get('count_mode') or 'segmented'}` "
        f"{row['segment_size']} "
        f"({thread_text(row.get('circle_threads'), row.get('circle_requested_threads'))})"
    )


def render_count_binary_cold_candidate_readout_markdown(
    rows: list[dict[str, Any]],
) -> list[str]:
    if not rows:
        return []
    first = rows[0]
    include_confirmation = any(row.get("confirmation") for row in rows)
    lines = [
        "Cold one-shot count-binary candidate readout:",
        "",
        (
            "Trial requires median gain over default at least "
            f"`{first.get('min_gain', 1.03):.3f}x`, candidate median speedup "
            f"at least `{first.get('min_candidate_median_speedup', 1.0):.3f}x`, "
            "and candidate best-time speedup at least "
            f"`{first.get('min_candidate_best_speedup', 1.0):.3f}x` versus "
            "cold `primesieve`."
        ),
        "",
    ]
    if include_confirmation:
        lines.extend(
            [
                "| Range | Default | Default Median/Best | Best Candidate | Candidate Median/Best | Median Gain | Sweep Action | Confirmation | Final Action |",
                "| --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |",
            ]
        )
    else:
        lines.extend(
            [
                "| Range | Default | Default Median/Best | Best Candidate | Candidate Median/Best | Median Gain | Action |",
                "| --- | --- | ---: | --- | ---: | ---: | --- |",
            ]
        )
    for row in rows:
        default = row["default"]
        best = row["best"]
        base = (
            f"| [{row['low']}, {row['high']}) | "
            f"{cold_count_binary_candidate_label(default)} | "
            f"{default['median_circle_speedup']:.3f}x / "
            f"{default['circle_speedup']:.3f}x | "
            f"{cold_count_binary_candidate_label(best)} | "
            f"{best['median_circle_speedup']:.3f}x / "
            f"{best['circle_speedup']:.3f}x | "
            f"{format_optional_ratio(row.get('median_gain_over_default'))} | "
            f"`{row['action']}` |"
        )
        if include_confirmation:
            lines.append(
                base
                + f" {count_binary_confirmation_text(row)} | "
                + f"`{row.get('final_action', row['action'])}` |"
            )
        else:
            lines.append(base)
    lines.append("")
    return lines


def count_binary_confirmation_text(row: dict[str, Any]) -> str:
    confirmation = row.get("confirmation")
    if not isinstance(confirmation, dict):
        return "`missing`"
    best = confirmation["best"]
    return (
        f"`{row.get('confirmation_sample_scope', confirmation.get('sample_scope', 'unknown'))}` "
        f"`{confirmation.get('action', 'unknown')}`<br>"
        f"{best['median_circle_speedup']:.3f}x / {best['circle_speedup']:.3f}x, "
        f"gain {format_optional_ratio(confirmation.get('median_gain_over_default'))}"
    )


def cold_count_binary_candidate_label(row: dict[str, Any]) -> str:
    return (
        f"{circle_row_label(row)}<br>segment: `{row['segment_size']}`, "
        "threads: "
        f"`{thread_text(row.get('circle_threads'), row.get('circle_requested_threads'))}`"
    )


def render_external_segment_sweep_markdown(
    summary: dict[str, Any],
    *,
    title: str = "External Segment Sweep",
    missing_message: str = "No external segment sweep artifact was available.",
    spread_label: str = "Segment candidate spread:",
    include_circle_row: bool = False,
    default_label: str | None = None,
    best_label: str | None = None,
    thread_comparison_label: str | None = None,
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

    if summary.get("cold_candidate_readout"):
        lines.extend(
            render_count_binary_cold_candidate_readout_markdown(
                summary["cold_candidate_readout"]
            )
        )

    if default_label and summary.get("default_by_range_baseline"):
        lines.extend([default_label, ""])
        lines.extend(
            [
                "| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in summary["default_by_range_baseline"]:
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                + f"{circle_row_label(row)} | {row['segment_size']} | "
                + f"{thread_text(row.get('circle_threads'), row.get('circle_requested_threads'))} | "
                + f"{row['best_ms']:.3f} | {row['median_ms']:.3f} | "
                + f"{row['circle_speedup']:.3f} | {row['median_circle_speedup']:.3f} | "
                + f"{sample_stability_text(row)} | "
                + f"{row['verdict']} |"
        )
        lines.append("")

    if thread_comparison_label and summary.get("prefix_pi_thread_comparisons"):
        lines.extend([thread_comparison_label, ""])
        lines.extend(
            [
                "| Range | Baseline | Serial Row | Default Row | Serial ms | Default ms | Median Ratio | Verdict |",
                "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
            ]
        )
        for row in summary["prefix_pi_thread_comparisons"]:
            serial = row["serial"]
            default = row["default"]
            ratio = row.get("thread_speedup")
            ratio_text = "n/a" if ratio is None else f"{ratio:.3f}"
            lines.append(
                f"| [{row['low']}, {row['high']}) | `{row['baseline']}` | "
                + f"{circle_row_label(serial)} ({thread_text(serial.get('circle_threads'), serial.get('circle_requested_threads'))}) | "
                + f"{circle_row_label(default)} ({thread_text(default.get('circle_threads'), default.get('circle_requested_threads'))}) | "
                + f"{serial['median_ms']:.3f} | {default['median_ms']:.3f} | "
                + f"{ratio_text} | `{row['verdict']}` |"
            )
        lines.append("")

    best_rows = summary["best_by_range_baseline"]
    if default_label and summary.get("default_by_range_baseline"):
        default_identities = {
            external_candidate_identity(row)
            for row in summary["default_by_range_baseline"]
        }
        best_identities = {external_candidate_identity(row) for row in best_rows}
        if default_identities == best_identities:
            best_rows = []

    if best_rows:
        if best_label:
            lines.extend([best_label, ""])
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
        for row in best_rows:
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
    noise_ratio = stats.get("noise_over_median")
    count = stats.get("sample_count")
    if ratio is None:
        return f"n={count}"
    if stats.get("ignored_single_high_outlier") and noise_ratio is not None:
        return f"n={count}, robust/med={noise_ratio:.2f}, max/med={ratio:.2f}"
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
                "| Workload | Hot Row | Hot ms | Server Row | Count Server ms | Server / Hot | Server / Cold Count Binary | Cold Count Binary ms | Count Binary / Hot | Full CLI ms | Minimal Default Process ms | Segmented Process ms |",
                "| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["high_offset_cold_hot_overhead"]:
            lines.append(
                f"| {row['workload']} | `{row['hot_name']}` | "
                f"{row['hot_best_ms']:.3f} | "
                f"{format_optional_code(row['hot_server_name'])} | "
                f"{format_optional_ms(row['hot_server_best_ms'])} | "
                f"{format_optional_ratio(row['hot_server_over_hot'])} | "
                f"{format_optional_ratio(row['hot_server_over_cold_count_binary'])} | "
                f"{format_optional_ms(row['cold_count_binary_best_ms'])} | "
                f"{format_optional_ratio(row['cold_count_binary_over_hot'])} | "
                f"{format_optional_ms(row['cold_cli_best_ms'])} | "
                f"{format_optional_ms(row['cold_process_default_best_ms'])} | "
                f"{format_optional_ms(row['cold_process_best_ms'])} |"
            )
        lines.append("")
        diagnostic_rows = [
            row
            for row in summary["high_offset_cold_hot_overhead"]
            if any(
                row.get(field) is not None
                for field in (
                    "cold_process_noop_best_ms",
                    "cold_process_plan_best_ms",
                    "cold_count_binary_noop_best_ms",
                    "cold_count_binary_plan_best_ms",
                    "cold_process_serial_default_best_ms",
                    "cold_count_binary_minus_noop_ms",
                    "cold_count_binary_minus_binary_noop_ms",
                    "cold_external_primesieve_best_ms",
                )
            )
        ]
        if diagnostic_rows:
            lines.extend(
                [
                    "High-offset cold diagnostics:",
                    "",
                    "| Workload | Bench Noop ms | Bench Plan ms | Count Binary Noop ms | Count Binary Plan ms | Serial Default ms | Count Binary ms | Count Binary - Server ms | Noop Share | Residual After Noop ms | Next Action | primesieve Cold ms | Count Binary / primesieve |",
                    "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
                ]
            )
            for row in diagnostic_rows:
                lines.append(
                    f"| {row['workload']} | "
                    f"{format_optional_ms(row['cold_process_noop_best_ms'])} | "
                    f"{format_optional_ms(row['cold_process_plan_best_ms'])} | "
                    f"{format_optional_ms(row['cold_count_binary_noop_best_ms'])} | "
                    f"{format_optional_ms(row['cold_count_binary_plan_best_ms'])} | "
                    f"{format_optional_ms(row['cold_process_serial_default_best_ms'])} | "
                    f"{format_optional_ms(row['cold_count_binary_best_ms'])} | "
                    f"{format_optional_ms(row['cold_count_binary_server_extra_ms'])} | "
                    f"{format_optional_ratio(row['cold_count_binary_noop_share_of_server_extra'])} | "
                    f"{format_optional_ms(row['cold_count_binary_residual_after_binary_noop_ms'])} | "
                    f"{format_optional_code(row['cold_count_binary_next_action'])} | "
                    f"{format_optional_ms(row['cold_external_primesieve_best_ms'])} | "
                    f"{format_optional_ratio(row['cold_count_binary_over_external_primesieve'])} |"
                )
            lines.append("")
    if summary.get("high_offset_server_external"):
        lines.extend(
            [
                "High-offset server/external best-time comparison:",
                "",
                "| Workload | Server Row | Server ms | Baseline | Baseline Best ms | Server Speedup | Cold CLI ms | Cold CLI Speedup |",
                "| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["high_offset_server_external"]:
            lines.append(
                f"| {row['workload']} | {format_optional_code(row['server_name'])} | "
                f"{row['server_best_ms']:.3f} | `{row['baseline']}` | "
                f"{row['baseline_best_ms']:.3f} | "
                f"{row['server_best_speedup']:.3f} | "
                f"{row['cold_cli_best_ms']:.3f} | "
                f"{row['cold_cli_best_speedup']:.3f} |"
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
