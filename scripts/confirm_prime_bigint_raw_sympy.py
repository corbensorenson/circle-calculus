from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from check_prime_bigint_controls import (
        PRIME_CASES,
        PRIME_LIKE_CASES,
        BigIntRow,
        parse_case_list,
        read_rows,
        validate_artifact,
    )
except ModuleNotFoundError:
    from scripts.check_prime_bigint_controls import (
        PRIME_CASES,
        PRIME_LIKE_CASES,
        BigIntRow,
        parse_case_list,
        read_rows,
        validate_artifact,
    )


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
SCHEMA_ID = "circle_calculus.prime_bigint_raw_sympy_confirm.v0"


@dataclass(frozen=True)
class RunSummary:
    run: int
    csv: Path
    metadata: Path
    failures: list[str]
    speedups: dict[str, float]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Repeat the BigUint controls benchmark and require the raw BPSW "
            "primality promotion gate to pass on every run."
        )
    )
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument(
        "--circle-prime-bin",
        type=Path,
        default=ROOT / "target" / "release" / "circle-prime",
    )
    parser.add_argument("--bench-rounds", type=int, default=3)
    parser.add_argument("--warmup-rounds", type=int, default=1)
    parser.add_argument("--mr-rounds", type=int, default=16)
    parser.add_argument("--max-candidates", type=int, default=4096)
    parser.add_argument("--candidate-window", type=int, default=512)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--score-limit", type=int, default=128)
    parser.add_argument("--server-batch-size", type=int, default=16)
    parser.add_argument("--min-hot-test-vs-openssl", type=float, default=1.5)
    parser.add_argument("--min-bpsw-test-vs-openssl", type=float, default=1.5)
    parser.add_argument("--min-bpsw-next-vs-sympy", type=float, default=1.1)
    parser.add_argument("--min-bpsw-prime-vs-sympy", type=float, default=1.0)
    parser.add_argument(
        "--bpsw-prime-vs-sympy-cases",
        default=",".join(sorted(PRIME_LIKE_CASES)),
    )
    parser.add_argument(
        "--artifact-prefix",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_raw_sympy_confirm",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_raw_sympy_confirm_latest.json",
    )
    args = parser.parse_args()

    if args.runs <= 0:
        raise SystemExit("--runs must be positive")
    cases = parse_case_list(
        args.bpsw_prime_vs_sympy_cases,
        allowed_cases=PRIME_CASES,
        label="--bpsw-prime-vs-sympy-cases",
    )
    summaries = [
        run_confirmation_pass(args=args, run_index=run_index, cases=cases)
        for run_index in range(1, args.runs + 1)
    ]

    summary = build_summary(args=args, cases=cases, runs=summaries)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    for case, speedup in summary["min_speedup_by_case"].items():
        print(f"{case}: min BPSW/SymPy speedup over {args.runs} run(s) = {speedup:.3f}x")
    print(f"wrote {args.summary_output}")

    failures = [
        f"run {run.run}: {failure}" for run in summaries for failure in run.failures
    ]
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    return 0


def run_confirmation_pass(
    *,
    args: argparse.Namespace,
    run_index: int,
    cases: set[str],
) -> RunSummary:
    csv_path = args.artifact_prefix.with_name(
        f"{args.artifact_prefix.name}_run_{run_index:02d}.csv"
    )
    metadata_path = args.artifact_prefix.with_name(
        f"{args.artifact_prefix.name}_run_{run_index:02d}.json"
    )
    command = [
        sys.executable,
        str(ROOT / "scripts" / "benchmark_prime_bigint_controls.py"),
        "--circle-prime-bin",
        str(args.circle_prime_bin),
        "--bench-rounds",
        str(args.bench_rounds),
        "--warmup-rounds",
        str(args.warmup_rounds),
        "--mr-rounds",
        str(args.mr_rounds),
        "--max-candidates",
        str(args.max_candidates),
        "--candidate-window",
        str(args.candidate_window),
        "--top-k",
        str(args.top_k),
        "--score-limit",
        str(args.score_limit),
        "--server-batch-size",
        str(args.server_batch_size),
        "--output",
        str(csv_path),
        "--metadata-output",
        str(metadata_path),
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        expect_bench_rounds=args.bench_rounds,
        expect_warmup_rounds=args.warmup_rounds,
        expect_mr_rounds=args.mr_rounds,
        expect_server_batch_size=args.server_batch_size,
        min_hot_test_vs_openssl=args.min_hot_test_vs_openssl,
        min_bpsw_test_vs_openssl=args.min_bpsw_test_vs_openssl,
        min_bpsw_next_vs_sympy=args.min_bpsw_next_vs_sympy,
        min_bpsw_prime_vs_sympy=args.min_bpsw_prime_vs_sympy,
        bpsw_prime_vs_sympy_cases=cases,
        require_bpsw_profile=True,
        require_fuzzy_any=True,
    )
    return RunSummary(
        run=run_index,
        csv=csv_path,
        metadata=metadata_path,
        failures=failures,
        speedups=bpsw_prime_speedups_by_case(read_rows(csv_path), cases),
    )


def bpsw_prime_speedups_by_case(rows: list[BigIntRow], cases: set[str]) -> dict[str, float]:
    row_by_key = {row.key: row for row in rows}
    speedups = {}
    for case in sorted(cases):
        bpsw = row_by_key[("prime_test", case, "circle_big_bpsw_test_server")]
        sympy = row_by_key[("prime_test", case, "sympy_isprime")]
        speedups[case] = sympy.median_ms / bpsw.median_ms
    return speedups


def build_summary(
    *,
    args: argparse.Namespace,
    cases: set[str],
    runs: list[RunSummary],
) -> dict[str, object]:
    min_speedup_by_case = {
        case: min(run.speedups[case] for run in runs)
        for case in sorted(cases)
    }
    return {
        "schema": SCHEMA_ID,
        "runs": args.runs,
        "bench_rounds": args.bench_rounds,
        "warmup_rounds": args.warmup_rounds,
        "mr_rounds": args.mr_rounds,
        "server_batch_size": args.server_batch_size,
        "min_bpsw_prime_vs_sympy": args.min_bpsw_prime_vs_sympy,
        "cases": sorted(cases),
        "min_speedup_by_case": min_speedup_by_case,
        "all_runs_passed": all(not run.failures for run in runs),
        "run_artifacts": [
            {
                "run": run.run,
                "csv": str(run.csv),
                "metadata": str(run.metadata),
                "speedups": run.speedups,
                "failures": run.failures,
            }
            for run in runs
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
