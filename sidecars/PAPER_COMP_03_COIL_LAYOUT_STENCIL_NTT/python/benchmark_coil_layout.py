"""Small CoilLayout benchmark scaffold.

This script times natural circular-stride traversal against gcd-cycle coil
traversal and can validate a deterministic parameter grid. It is a benchmark
harness, not a proof and not a performance claim.

Examples:
    python sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py
    python sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py --backend both
    python sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py --validate-grid
"""

from __future__ import annotations

import argparse
from typing import Callable, Iterable

from circle_math.applications.coil_compute import (
    BenchmarkResult,
    run_cpu,
    run_cpu_grid,
    run_mlx,
    validate_layout_grid,
    validate_stencil_grid,
)


def print_results(results: Iterable[BenchmarkResult]) -> None:
    for result in results:
        print(
            f"{result.name:14s} size={result.size} stride={result.stride} "
            f"repeats={result.repeats} seconds={result.seconds:.6f} checksum={result.checksum:.1f}"
        )


def print_grid_validation() -> None:
    mismatch = False
    for result in validate_layout_grid():
        status = "ok" if result.all_match else "mismatch"
        mismatch = mismatch or not result.all_match
        print(
            f"{status:8s} size={result.case.size} stride={result.case.stride} "
            f"repeats={result.case.repeats} checksum={result.natural_checksum:.1f}"
        )
    if mismatch:
        raise SystemExit(1)


def print_stencil_validation() -> None:
    mismatch = False
    for result in validate_stencil_grid():
        status = "ok" if result.all_match else "mismatch"
        mismatch = mismatch or not result.all_match
        print(
            f"{status:8s} stencil size={result.case.size} stride={result.case.stride} "
            f"repeats={result.case.repeats} checksum={sum(result.direct_output):.1f}"
        )
    if mismatch:
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark natural vs gcd-cycle circular-stride traversal.")
    parser.add_argument("--size", type=int, default=32768)
    parser.add_argument("--stride", type=int, default=513)
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--backend", choices=("cpu", "mlx", "both"), default="cpu")
    parser.add_argument("--grid", action="store_true", help="run the deterministic CPU parameter grid")
    parser.add_argument("--validate-grid", action="store_true", help="validate expected outputs for the grid")
    parser.add_argument("--validate-stencil", action="store_true", help="validate periodic-boundary stencil outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.validate_grid:
        print_grid_validation()
        return
    if args.validate_stencil:
        print_stencil_validation()
        return

    if args.grid:
        print_results(run_cpu_grid())
        return

    runners: list[Callable[[int, int, int], list[BenchmarkResult]]] = []
    if args.backend in ("cpu", "both"):
        runners.append(run_cpu)
    if args.backend in ("mlx", "both"):
        runners.append(run_mlx)
    for runner in runners:
        print_results(runner(args.size, args.stride, args.repeats))


if __name__ == "__main__":
    main()
