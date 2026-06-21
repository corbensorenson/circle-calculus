from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import sympy
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal CI envs.
    sympy = None

try:
    from check_prime_bigint_controls import BigIntRow, NEXT_CASES, read_rows
    from benchmark_prime_bigint_controls import (
        LineServer,
        circle_big_bpsw_next_server,
        circle_big_fuzzy_any_server,
        next_cases,
        sympy_next_prime_at_or_above,
        timed,
        write_big_fuzzy_model,
    )
except ModuleNotFoundError:
    from scripts.check_prime_bigint_controls import BigIntRow, NEXT_CASES, read_rows
    from scripts.benchmark_prime_bigint_controls import (
        LineServer,
        circle_big_bpsw_next_server,
        circle_big_fuzzy_any_server,
        next_cases,
        sympy_next_prime_at_or_above,
        timed,
        write_big_fuzzy_model,
    )


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "sidecars" / "PRIME_ENGINE" / "results"
SCHEMA_ID = "circle_calculus.prime_bigint_next_fuzzy_confirm.v0"


def require_sympy():
    if sympy is None:
        raise RuntimeError(
            "SymPy is required for BigUint next/fuzzy confirmation runs. "
            "Install sympy to run scripts/confirm_prime_bigint_next_fuzzy.py."
        )
    return sympy


@dataclass(frozen=True)
class RunSummary:
    run: int
    csv: Path
    metadata: Path
    failures: list[str]
    speedups: dict[str, dict[str, float]]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Repeat focused BigUint next-prime and fuzzy any-prime rows, with "
            "deterministic BPSW next-prime promotion separated from fuzzy readouts."
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
    parser.add_argument("--fuzzy-profile", choices=["mr", "bpsw"], default="bpsw")
    parser.add_argument("--server-batch-size", type=int, default=16)
    parser.add_argument("--min-bpsw-next-vs-sympy", type=float, default=1.1)
    parser.add_argument("--min-fuzzy-any-vs-sympy", type=float, default=0.0)
    parser.add_argument("--min-fuzzy-any-vs-bpsw-next", type=float, default=0.0)
    parser.add_argument(
        "--artifact-prefix",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_next_fuzzy_confirm",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=RESULTS_DIR / "prime_bigint_next_fuzzy_confirm_latest.json",
    )
    args = parser.parse_args()

    if args.runs <= 0:
        raise SystemExit("--runs must be positive")
    if args.bench_rounds <= 0:
        raise SystemExit("--bench-rounds must be positive")
    if args.warmup_rounds < 0:
        raise SystemExit("--warmup-rounds must be nonnegative")
    if args.server_batch_size <= 0:
        raise SystemExit("--server-batch-size must be positive")
    if not args.circle_prime_bin.exists():
        raise SystemExit(f"circle-prime binary is missing: {args.circle_prime_bin}")

    summaries = [
        run_confirmation_pass(args=args, run_index=run_index)
        for run_index in range(1, args.runs + 1)
    ]
    summary = build_summary(args=args, runs=summaries)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    for group, by_case in summary["min_speedup_by_group"].items():
        for case, speedup in by_case.items():
            print(f"{case}: min {group} speedup over {args.runs} run(s) = {speedup:.3f}x")
    print(f"wrote {args.summary_output}")

    failures = [
        f"run {run.run}: {failure}" for run in summaries for failure in run.failures
    ]
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    return 0


def run_confirmation_pass(*, args: argparse.Namespace, run_index: int) -> RunSummary:
    csv_path = args.artifact_prefix.with_name(
        f"{args.artifact_prefix.name}_run_{run_index:02d}.csv"
    )
    metadata_path = args.artifact_prefix.with_name(
        f"{args.artifact_prefix.name}_run_{run_index:02d}.json"
    )
    rows = benchmark_next_fuzzy_rows(args=args)
    write_rows(csv_path, rows)
    write_metadata(metadata_path, args=args, rows=rows)
    parsed_rows = read_rows(csv_path)
    failures = validate_next_fuzzy_rows(
        parsed_rows,
        min_bpsw_next_vs_sympy=args.min_bpsw_next_vs_sympy,
        min_fuzzy_any_vs_sympy=args.min_fuzzy_any_vs_sympy,
        min_fuzzy_any_vs_bpsw_next=args.min_fuzzy_any_vs_bpsw_next,
    )
    return RunSummary(
        run=run_index,
        csv=csv_path,
        metadata=metadata_path,
        failures=failures,
        speedups=next_fuzzy_speedups_by_case(parsed_rows),
    )


def benchmark_next_fuzzy_rows(*, args: argparse.Namespace) -> list[dict[str, object]]:
    require_sympy()
    max_bits = max(case.start.bit_length() for case in next_cases())
    model_path = ROOT / "target" / "prime-controls" / "prime-big-fuzzy-model.txt"
    write_big_fuzzy_model(model_path, max_bits)
    rows: list[dict[str, object]] = []
    with LineServer(
        [
            str(args.circle_prime_bin),
            "big-next-server",
            "--profile",
            "bpsw",
            "--max-candidates",
            str(args.max_candidates),
        ]
    ) as bpsw_next_server, LineServer(
        [
            str(args.circle_prime_bin),
            "big-fuzzy-server",
            str(model_path),
            "--candidate-window",
            str(args.candidate_window),
            "--top-k",
            str(args.top_k),
            "--score-limit",
            str(args.score_limit),
            "--profile",
            args.fuzzy_profile,
            "--rounds",
            str(args.mr_rounds),
        ]
    ) as fuzzy_server:
        for case in next_cases():
            expected = sympy_next_prime_at_or_above(case.start)
            bpsw_next = timed(
                lambda case=case: circle_big_bpsw_next_server(
                    bpsw_next_server,
                    case.start,
                    args.server_batch_size,
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            fuzzy_any = timed(
                lambda case=case: circle_big_fuzzy_any_server(
                    fuzzy_server,
                    case.start,
                    args.server_batch_size,
                ),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
                sample_divisor=args.server_batch_size,
            )
            sympy_next = timed(
                lambda case=case: sympy_next_prime_at_or_above(case.start),
                warmup_rounds=args.warmup_rounds,
                bench_rounds=args.bench_rounds,
            )
            append_row(
                rows,
                operation="next_search",
                case=case.name,
                bits=case.start.bit_length(),
                engine="circle_big_bpsw_next_server",
                result=bpsw_next.result,
                expected=expected,
                agreed=bpsw_next.result == expected,
                mr_rounds=args.mr_rounds,
                samples_ms=bpsw_next.samples_ms,
            )
            append_row(
                rows,
                operation="next_search",
                case=case.name,
                bits=case.start.bit_length(),
                engine="sympy_nextprime",
                result=sympy_next.result,
                expected=expected,
                agreed=sympy_next.result == expected,
                mr_rounds=args.mr_rounds,
                samples_ms=sympy_next.samples_ms,
            )
            fuzzy_result = fuzzy_any.result
            append_row(
                rows,
                operation="fuzzy_any_search",
                case=case.name,
                bits=case.start.bit_length(),
                engine="circle_big_fuzzy_any_server",
                result=fuzzy_result,
                expected=expected,
                agreed=is_valid_fuzzy_result(fuzzy_result, start=case.start),
                mr_rounds=args.mr_rounds,
                samples_ms=fuzzy_any.samples_ms,
            )
    return rows


def is_valid_fuzzy_result(result: object, *, start: int) -> bool:
    if not isinstance(result, int):
        return False
    if result < start:
        return False
    return bool(require_sympy().isprime(result))


def append_row(
    rows: list[dict[str, object]],
    *,
    operation: str,
    case: str,
    bits: int,
    engine: str,
    result: object,
    expected: object,
    agreed: bool,
    mr_rounds: int,
    samples_ms: list[float],
) -> None:
    rows.append(
        {
            "operation": operation,
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
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema": "circle_calculus.prime_bigint_next_fuzzy_run.v0",
        "row_count": len(rows),
        "bench_rounds": args.bench_rounds,
        "warmup_rounds": args.warmup_rounds,
        "mr_rounds": args.mr_rounds,
        "max_candidates": args.max_candidates,
        "candidate_window": args.candidate_window,
        "top_k": args.top_k,
        "score_limit": args.score_limit,
        "fuzzy_profile": args.fuzzy_profile,
        "server_batch_size": args.server_batch_size,
        "cases": sorted(NEXT_CASES),
        "circle_prime": {
            "path": str(args.circle_prime_bin),
            "exists": args.circle_prime_bin.exists(),
        },
    }
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")


def validate_next_fuzzy_rows(
    rows: list[BigIntRow],
    *,
    min_bpsw_next_vs_sympy: float,
    min_fuzzy_any_vs_sympy: float,
    min_fuzzy_any_vs_bpsw_next: float,
) -> list[str]:
    failures: list[str] = []
    row_by_key = {row.key: row for row in rows}
    required = [
        ("next_search", "circle_big_bpsw_next_server"),
        ("next_search", "sympy_nextprime"),
        ("fuzzy_any_search", "circle_big_fuzzy_any_server"),
    ]
    for case in sorted(NEXT_CASES):
        for operation, engine in required:
            row = row_by_key.get((operation, case, engine))
            if row is None:
                failures.append(f"missing {operation} row: case={case}, engine={engine}")
                continue
            if not row.agreed:
                failures.append(
                    f"{operation} {case} {engine} disagreed: "
                    f"result={row.result}, expected={row.expected}"
                )
            if row.rounds <= 0:
                failures.append(f"{operation} {case} {engine} has no samples")
            if row.median_ms <= 0.0 or row.min_ms <= 0.0 or row.max_ms <= 0.0:
                failures.append(f"{operation} {case} {engine} has nonpositive timing")
            if row.min_ms > row.median_ms or row.median_ms > row.max_ms:
                failures.append(f"{operation} {case} {engine} timing order is invalid")
        failures.extend(
            validate_speed_floor(
                row_by_key,
                case=case,
                group="bpsw_next_vs_sympy",
                operation="next_search",
                candidate_engine="circle_big_bpsw_next_server",
                baseline_engine="sympy_nextprime",
                minimum=min_bpsw_next_vs_sympy,
            )
        )
        failures.extend(
            validate_speed_floor(
                row_by_key,
                case=case,
                group="fuzzy_any_vs_sympy",
                operation="fuzzy_any_search",
                candidate_engine="circle_big_fuzzy_any_server",
                baseline_engine="sympy_nextprime",
                baseline_operation="next_search",
                minimum=min_fuzzy_any_vs_sympy,
            )
        )
        failures.extend(
            validate_speed_floor(
                row_by_key,
                case=case,
                group="fuzzy_any_vs_bpsw_next",
                operation="fuzzy_any_search",
                candidate_engine="circle_big_fuzzy_any_server",
                baseline_engine="circle_big_bpsw_next_server",
                baseline_operation="next_search",
                minimum=min_fuzzy_any_vs_bpsw_next,
            )
        )
    return failures


def validate_speed_floor(
    row_by_key: dict[tuple[str, str, str], BigIntRow],
    *,
    case: str,
    group: str,
    operation: str,
    candidate_engine: str,
    baseline_engine: str,
    minimum: float,
    baseline_operation: str | None = None,
) -> list[str]:
    if minimum <= 0.0:
        return []
    candidate = row_by_key.get((operation, case, candidate_engine))
    baseline = row_by_key.get((baseline_operation or operation, case, baseline_engine))
    if candidate is None or baseline is None:
        return []
    speedup = baseline.median_ms / candidate.median_ms
    if speedup >= minimum:
        return []
    return [
        f"{case} {group} {candidate_engine} median speedup over "
        f"{baseline_engine} is {speedup:.3f}, below required {minimum:.3f}"
    ]


def next_fuzzy_speedups_by_case(rows: list[BigIntRow]) -> dict[str, dict[str, float]]:
    row_by_key = {row.key: row for row in rows}
    speedups: dict[str, dict[str, float]] = {
        "bpsw_next_vs_sympy": {},
        "fuzzy_any_vs_sympy": {},
        "fuzzy_any_vs_bpsw_next": {},
    }
    for case in sorted(NEXT_CASES):
        bpsw = row_by_key[("next_search", case, "circle_big_bpsw_next_server")]
        sympy = row_by_key[("next_search", case, "sympy_nextprime")]
        fuzzy = row_by_key[("fuzzy_any_search", case, "circle_big_fuzzy_any_server")]
        speedups["bpsw_next_vs_sympy"][case] = sympy.median_ms / bpsw.median_ms
        speedups["fuzzy_any_vs_sympy"][case] = sympy.median_ms / fuzzy.median_ms
        speedups["fuzzy_any_vs_bpsw_next"][case] = bpsw.median_ms / fuzzy.median_ms
    return speedups


def build_summary(*, args: argparse.Namespace, runs: list[RunSummary]) -> dict[str, object]:
    min_speedup_by_group: dict[str, dict[str, float]] = {}
    for group in ["bpsw_next_vs_sympy", "fuzzy_any_vs_sympy", "fuzzy_any_vs_bpsw_next"]:
        min_speedup_by_group[group] = {
            case: min(run.speedups[group][case] for run in runs)
            for case in sorted(NEXT_CASES)
        }
    return {
        "schema": SCHEMA_ID,
        "runs": args.runs,
        "bench_rounds": args.bench_rounds,
        "warmup_rounds": args.warmup_rounds,
        "mr_rounds": args.mr_rounds,
        "max_candidates": args.max_candidates,
        "candidate_window": args.candidate_window,
        "top_k": args.top_k,
        "score_limit": args.score_limit,
        "fuzzy_profile": args.fuzzy_profile,
        "server_batch_size": args.server_batch_size,
        "min_bpsw_next_vs_sympy": args.min_bpsw_next_vs_sympy,
        "min_fuzzy_any_vs_sympy": args.min_fuzzy_any_vs_sympy,
        "min_fuzzy_any_vs_bpsw_next": args.min_fuzzy_any_vs_bpsw_next,
        "cases": sorted(NEXT_CASES),
        "min_speedup_by_group": min_speedup_by_group,
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
