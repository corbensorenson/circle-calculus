"""Small CoilLayout benchmark scaffold.

This script times natural circular-stride traversal against gcd-cycle coil
traversal. It is a benchmark harness, not a proof and not a performance claim.

Examples:
    python sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py
    python sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py --backend both
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    size: int
    stride: int
    repeats: int
    seconds: float
    checksum: float


def gcd_cycle_order(size: int, stride: int) -> tuple[int, ...]:
    """Return each address once, grouped by the cycles of i -> i + stride mod size."""
    if size <= 0:
        raise ValueError("size must be positive")
    stride %= size
    cycle_count = math.gcd(size, stride)
    period = size // cycle_count
    return tuple((start + step * stride) % size for start in range(cycle_count) for step in range(period))


def natural_order(size: int) -> tuple[int, ...]:
    if size <= 0:
        raise ValueError("size must be positive")
    return tuple(range(size))


def circular_stride_checksum(values: list[float], stride: int, order: Iterable[int], repeats: int) -> float:
    size = len(values)
    if size == 0:
        raise ValueError("values must be nonempty")
    total = 0.0
    stride %= size
    order_tuple = tuple(order)
    for _ in range(repeats):
        for index in order_tuple:
            total += values[index] * 0.5 + values[(index + stride) % size] * 0.5
    return total


def time_cpu_order(name: str, size: int, stride: int, repeats: int, order: tuple[int, ...]) -> BenchmarkResult:
    values = [float((index * 17 + 3) % 257) for index in range(size)]
    start = time.perf_counter()
    checksum = circular_stride_checksum(values, stride, order, repeats)
    elapsed = time.perf_counter() - start
    return BenchmarkResult(name=name, size=size, stride=stride, repeats=repeats, seconds=elapsed, checksum=checksum)


def run_cpu(size: int, stride: int, repeats: int) -> list[BenchmarkResult]:
    return [
        time_cpu_order("cpu:natural", size, stride, repeats, natural_order(size)),
        time_cpu_order("cpu:gcd_cycle", size, stride, repeats, gcd_cycle_order(size, stride)),
    ]


def run_mlx(size: int, stride: int, repeats: int) -> list[BenchmarkResult]:
    try:
        import mlx.core as mx  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on local optional backend
        raise RuntimeError("MLX is not available in this Python environment") from exc

    values = mx.array([(index * 17 + 3) % 257 for index in range(size)], dtype=mx.float32)
    natural = mx.array(natural_order(size), dtype=mx.int32)
    coil = mx.array(gcd_cycle_order(size, stride), dtype=mx.int32)
    stride %= size

    def time_mlx(name: str, order: object) -> BenchmarkResult:
        start = time.perf_counter()
        total = mx.array(0.0, dtype=mx.float32)
        for _ in range(repeats):
            total = total + mx.sum(values[order] * 0.5 + values[(order + stride) % size] * 0.5)
        mx.eval(total)
        elapsed = time.perf_counter() - start
        return BenchmarkResult(
            name=name,
            size=size,
            stride=stride,
            repeats=repeats,
            seconds=elapsed,
            checksum=float(total.item()),
        )

    return [time_mlx("mlx:natural", natural), time_mlx("mlx:gcd_cycle", coil)]


def print_results(results: Iterable[BenchmarkResult]) -> None:
    for result in results:
        print(
            f"{result.name:14s} size={result.size} stride={result.stride} "
            f"repeats={result.repeats} seconds={result.seconds:.6f} checksum={result.checksum:.1f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark natural vs gcd-cycle circular-stride traversal.")
    parser.add_argument("--size", type=int, default=32768)
    parser.add_argument("--stride", type=int, default=513)
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--backend", choices=("cpu", "mlx", "both"), default="cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runners: list[Callable[[int, int, int], list[BenchmarkResult]]] = []
    if args.backend in ("cpu", "both"):
        runners.append(run_cpu)
    if args.backend in ("mlx", "both"):
        runners.append(run_mlx)
    for runner in runners:
        print_results(runner(args.size, args.stride, args.repeats))


if __name__ == "__main__":
    main()
