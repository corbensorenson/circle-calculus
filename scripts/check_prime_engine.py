from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def require_cargo() -> str:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("cargo is required for the Rust prime engine checks")
    return cargo


def circle_prime_debug_binary() -> Path:
    suffix = ".exe" if sys.platform == "win32" else ""
    return ROOT / "target" / "debug" / f"circle-prime{suffix}"


def check_cli(binary: Path) -> None:
    prime = run(
        [
            str(binary),
            "test",
            "97",
            "--json",
        ],
        capture=True,
    ).stdout
    if '"status":"prime"' not in prime:
        raise AssertionError(f"expected 97 to be prime, got: {prime}")

    composite = run(
        [
            str(binary),
            "test",
            "561",
            "--json",
        ],
        capture=True,
    ).stdout
    if '"status":"composite"' not in composite:
        raise AssertionError(f"expected 561 to be composite, got: {composite}")

    count = run(
        [
            str(binary),
            "range",
            "0",
            "1000000",
            "--count",
        ],
        capture=True,
    ).stdout.strip()
    if count != "78498":
        raise AssertionError(f"expected pi(1_000_000)=78498, got: {count}")


def check_benchmark(
    cargo: str,
    rounds: int,
    min_primal_speedup: float,
    min_simple_speedup: float,
    min_trial_speedup: float,
    output_path: Path | None,
) -> None:
    completed = run(
        [
            cargo,
            "run",
            "--release",
            "-p",
            "circle-prime",
            "--bin",
            "circle-prime-bench",
            "--",
            "--rounds",
            str(rounds),
        ],
        capture=True,
    )
    print(completed.stdout, end="")
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(completed.stdout)
        print(f"wrote benchmark CSV to {output_path}")

    rows = list(csv.DictReader(completed.stdout.splitlines()))
    primal_speedups = best_speedups_by_workload(rows, "control_primal_sieve_count")
    simple_speedups = best_speedups_by_workload(rows, "control_simple_sieve_count")
    trial_speedups = best_speedups_by_workload(rows, "control_trial_division_count")
    cold_rows = [
        row
        for row in rows
        if row["kind"] == "timing" and row["name"] == "cold_process_segmented_range_count"
    ]
    base_prime_rows = [
        row
        for row in rows
        if row["kind"] == "timing" and row["name"] == "base_prime_generation"
    ]
    next_prime_rows = [
        row
        for row in rows
        if row["kind"] == "timing" and row["name"] == "next_prime_search"
    ]
    high_offset_rows = [
        row
        for row in rows
        if row["kind"] == "timing" and "high_offset" in row["name"]
    ]

    if not primal_speedups:
        raise AssertionError("benchmark did not report primal-sieve speedup rows")
    if not simple_speedups:
        raise AssertionError("benchmark did not report simple-sieve speedup rows")
    if not trial_speedups:
        raise AssertionError("benchmark did not report trial-division speedup rows")
    if not cold_rows:
        raise AssertionError("benchmark did not report cold-process segmented count rows")
    if not base_prime_rows:
        raise AssertionError("benchmark did not report base-prime generation rows")
    if not next_prime_rows:
        raise AssertionError("benchmark did not report next-prime search rows")
    if not high_offset_rows:
        raise AssertionError("benchmark did not report high-offset range count rows")
    if min_primal_speedup > 0:
        require_workload_speedups(
            primal_speedups, "primal-sieve", min_primal_speedup
        )
    require_workload_speedups(simple_speedups, "simple-sieve", min_simple_speedup)
    require_workload_speedups(trial_speedups, "trial-division", min_trial_speedup)


def best_speedups_by_workload(
    rows: list[dict[str, str]], baseline: str
) -> dict[str, float]:
    speedups: dict[str, float] = {}
    for row in rows:
        if row["kind"] != "speedup" or row["baseline"] != baseline:
            continue
        workload = row["workload"]
        speedup = float(row["best_speedup"])
        speedups[workload] = max(speedups.get(workload, 0.0), speedup)
    return speedups


def require_workload_speedups(
    speedups: dict[str, float], baseline_label: str, minimum: float
) -> None:
    failures = {
        workload: speedup for workload, speedup in speedups.items() if speedup < minimum
    }
    if failures:
        details = ", ".join(
            f"{workload}: {speedup:.3f}" for workload, speedup in sorted(failures.items())
        )
        raise AssertionError(
            f"Circle count engine did not beat {baseline_label} control enough "
            f"for every reported workload: {details}; required >= {minimum:.3f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Rust-backed Circle prime engine.")
    parser.add_argument("--benchmark", action="store_true", help="Run release benchmark controls.")
    parser.add_argument("--benchmark-rounds", type=int, default=3)
    parser.add_argument(
        "--benchmark-output",
        type=Path,
        help="Optional CSV path for benchmark output; only valid with --benchmark.",
    )
    parser.add_argument("--min-simple-speedup", type=float, default=1.05)
    parser.add_argument(
        "--min-primal-speedup",
        type=float,
        default=0.0,
        help="Optional gate against the optimized primal Rust sieve. Use 1.0 to require a win.",
    )
    parser.add_argument("--min-trial-speedup", type=float, default=5.0)
    args = parser.parse_args()

    if args.benchmark_rounds <= 0:
        parser.error("--benchmark-rounds must be positive")
    if args.min_primal_speedup < 0:
        parser.error("--min-primal-speedup must be nonnegative")
    if args.benchmark_output is not None and not args.benchmark:
        parser.error("--benchmark-output requires --benchmark")

    cargo = require_cargo()
    run([cargo, "fmt", "--all", "--check"])
    run([cargo, "test", "-p", "circle-prime"])
    run([cargo, "build", "--quiet", "-p", "circle-prime", "--bin", "circle-prime"])
    check_cli(circle_prime_debug_binary())
    run(
        [
            sys.executable,
            "scripts/check_prime_proof_contract.py",
            "--binary",
            str(circle_prime_debug_binary()),
        ]
    )
    if args.benchmark:
        check_benchmark(
            cargo,
            args.benchmark_rounds,
            args.min_primal_speedup,
            args.min_simple_speedup,
            args.min_trial_speedup,
            args.benchmark_output,
        )
    print("prime engine checks ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime engine check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
