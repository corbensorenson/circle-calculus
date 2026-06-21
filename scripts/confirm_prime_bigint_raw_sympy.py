from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import sympy

try:
    from check_prime_bigint_controls import (
        PRIME_CASES,
        PRIME_LIKE_CASES,
        BigIntRow,
        parse_case_list,
        read_rows,
    )
    from benchmark_prime_bigint_controls import LineServer, prime_cases, timed
except ModuleNotFoundError:
    from scripts.check_prime_bigint_controls import (
        PRIME_CASES,
        PRIME_LIKE_CASES,
        BigIntRow,
        parse_case_list,
        read_rows,
    )
    from scripts.benchmark_prime_bigint_controls import LineServer, prime_cases, timed


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
            "Repeat the BigUint raw-primality benchmark and require the raw BPSW "
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
    rows = benchmark_raw_prime_rows(args=args, cases=cases)
    write_rows(csv_path, rows)
    write_metadata(metadata_path, args=args, rows=rows, cases=cases)
    parsed_rows = read_rows(csv_path)
    failures = validate_raw_prime_rows(
        parsed_rows,
        cases=cases,
        minimum=args.min_bpsw_prime_vs_sympy,
    )
    return RunSummary(
        run=run_index,
        csv=csv_path,
        metadata=metadata_path,
        failures=failures,
        speedups=bpsw_prime_speedups_by_case(parsed_rows, cases),
    )


def benchmark_raw_prime_rows(
    *,
    args: argparse.Namespace,
    cases: set[str],
) -> list[dict[str, object]]:
    selected_cases = [case for case in prime_cases() if case.name in cases]
    rows: list[dict[str, object]] = []
    with LineServer(
        [
            str(args.circle_prime_bin),
            "big-test-server",
            "--profile",
            "bpsw",
        ]
    ) as circle_bpsw_server:
        for case in selected_cases:
            expected = case.expected_prime
            circle = timed(
                lambda case=case: circle_big_bpsw_test_server(
                    circle_bpsw_server,
                    case.n,
                    args.server_batch_size,
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            sympy_sample = timed(
                lambda case=case: bool(sympy.isprime(case.n)),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            append_row(
                rows,
                case=case.name,
                bits=case.n.bit_length(),
                engine="circle_big_bpsw_test_server",
                result=bool(circle.result),
                expected=expected,
                agreed=bool(circle.result) == expected,
                mr_rounds=args.mr_rounds,
                samples_ms=circle.samples_ms,
            )
            append_row(
                rows,
                case=case.name,
                bits=case.n.bit_length(),
                engine="sympy_isprime",
                result=bool(sympy_sample.result),
                expected=expected,
                agreed=bool(sympy_sample.result) == expected,
                mr_rounds=args.mr_rounds,
                samples_ms=sympy_sample.samples_ms,
            )
    return rows


def circle_big_bpsw_test_server(server: LineServer, n: int, batch_size: int) -> bool:
    lines = server.request(n, batch_size)
    if any(line != lines[0] for line in lines):
        raise RuntimeError(f"big-test-server returned inconsistent batch: {lines}")
    if lines[0] in {"prime", "probable_prime"}:
        return True
    if lines[0] == "composite":
        return False
    raise RuntimeError(f"could not parse big-test-server response: {lines[0]!r}")


def append_row(
    rows: list[dict[str, object]],
    *,
    case: str,
    bits: int,
    engine: str,
    result: bool,
    expected: bool,
    agreed: bool,
    mr_rounds: int,
    samples_ms: list[float],
) -> None:
    rows.append(
        {
            "operation": "prime_test",
            "case": case,
            "bits": bits,
            "engine": engine,
            "result": str(result),
            "expected": str(expected),
            "agreed": str(agreed),
            "mr_rounds": mr_rounds,
            "rounds": len(samples_ms),
            "median_ms": f"{median(samples_ms):.6f}",
            "min_ms": f"{min(samples_ms):.6f}",
            "max_ms": f"{max(samples_ms):.6f}",
        }
    )


def median(values: list[float]) -> float:
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "operation",
                "case",
                "bits",
                "engine",
                "result",
                "expected",
                "agreed",
                "mr_rounds",
                "rounds",
                "median_ms",
                "min_ms",
                "max_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(
    path: Path,
    *,
    args: argparse.Namespace,
    rows: list[dict[str, object]],
    cases: set[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema": "circle_calculus.prime_bigint_raw_sympy_run.v0",
        "row_count": len(rows),
        "bench_rounds": args.bench_rounds,
        "warmup_rounds": args.warmup_rounds,
        "mr_rounds": args.mr_rounds,
        "server_batch_size": args.server_batch_size,
        "cases": sorted(cases),
        "circle_prime": {
            "path": str(args.circle_prime_bin),
            "exists": args.circle_prime_bin.exists(),
        },
        "tools": {
            "sympy": sympy.__version__,
        },
    }
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def validate_raw_prime_rows(
    rows: list[BigIntRow],
    *,
    cases: set[str],
    minimum: float,
) -> list[str]:
    failures = []
    row_by_key = {row.key: row for row in rows}
    for case in sorted(cases):
        for engine in ["circle_big_bpsw_test_server", "sympy_isprime"]:
            row = row_by_key.get(("prime_test", case, engine))
            if row is None:
                failures.append(f"missing prime_test row: case={case}, engine={engine}")
                continue
            if not row.agreed:
                failures.append(
                    f"prime_test {case} {engine} disagreed: "
                    f"result={row.result}, expected={row.expected}"
                )
            if row.rounds <= 0:
                failures.append(f"prime_test {case} {engine} has no samples")
            if row.median_ms <= 0.0 or row.min_ms <= 0.0 or row.max_ms <= 0.0:
                failures.append(f"prime_test {case} {engine} has nonpositive timing")
            if row.min_ms > row.median_ms or row.median_ms > row.max_ms:
                failures.append(f"prime_test {case} {engine} timing order is invalid")
        bpsw = row_by_key.get(("prime_test", case, "circle_big_bpsw_test_server"))
        sympy_row = row_by_key.get(("prime_test", case, "sympy_isprime"))
        if bpsw is not None and sympy_row is not None and minimum > 0.0:
            speedup = sympy_row.median_ms / bpsw.median_ms
            if speedup < minimum:
                failures.append(
                    f"prime_test {case} circle_big_bpsw_test_server median speedup over "
                    f"sympy_isprime is {speedup:.3f}, below required {minimum:.3f}"
                )
    return failures


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
