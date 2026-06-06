"""Executable reference models for circular compute application seeds.

These helpers support benchmark fixtures and expected-output checks. They are
not formal proofs and they are not performance claims.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    size: int
    stride: int
    repeats: int
    seconds: float
    checksum: float


@dataclass(frozen=True)
class LayoutBenchmarkCase:
    size: int
    stride: int
    repeats: int = 1


@dataclass(frozen=True)
class LayoutValidationResult:
    case: LayoutBenchmarkCase
    natural_checksum: float
    gcd_cycle_checksum: float
    direct_checksum: float
    dense_checksum: float

    @property
    def all_match(self) -> bool:
        return (
            self.natural_checksum == self.gcd_cycle_checksum
            and self.natural_checksum == self.direct_checksum
            and self.natural_checksum == self.dense_checksum
        )


DEFAULT_LAYOUT_CASES: tuple[LayoutBenchmarkCase, ...] = (
    LayoutBenchmarkCase(size=8, stride=3, repeats=2),
    LayoutBenchmarkCase(size=12, stride=4, repeats=2),
    LayoutBenchmarkCase(size=15, stride=6, repeats=2),
    LayoutBenchmarkCase(size=16, stride=5, repeats=2),
)


def _require_positive(value: int, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def stride_address(size: int, stride: int, step: int) -> int:
    """Return ``step * stride mod size`` for a positive circular size."""
    _require_positive(size, "size")
    return (step * stride) % size


def gcd_cycle_order(size: int, stride: int) -> tuple[int, ...]:
    """Return each address once, grouped by cycles of ``i -> i + stride mod size``."""
    _require_positive(size, "size")
    stride %= size
    cycle_count = math.gcd(size, stride)
    period = size // cycle_count
    return tuple((start + step * stride) % size for start in range(cycle_count) for step in range(period))


def natural_order(size: int) -> tuple[int, ...]:
    _require_positive(size, "size")
    return tuple(range(size))


def reference_values(size: int) -> list[float]:
    _require_positive(size, "size")
    return [float((index * 17 + 3) % 257) for index in range(size)]


def circular_stride_checksum(values: Sequence[float], stride: int, order: Iterable[int], repeats: int) -> float:
    """Return a checksum for a simple circular nearest-stride stencil."""
    size = len(values)
    if size == 0:
        raise ValueError("values must be nonempty")
    _require_positive(repeats, "repeats")
    total = 0.0
    stride %= size
    order_tuple = tuple(order)
    for _ in range(repeats):
        for index in order_tuple:
            total += values[index] * 0.5 + values[(index + stride) % size] * 0.5
    return total


def direct_circular_checksum(values: Sequence[float], stride: int, repeats: int) -> float:
    """Return the direct natural-order checksum baseline."""
    return circular_stride_checksum(values, stride, natural_order(len(values)), repeats)


def dense_circular_checksum(values: Sequence[float], stride: int, repeats: int) -> float:
    """Return a tiny dense-matrix reference checksum for validation cases."""
    size = len(values)
    if size == 0:
        raise ValueError("values must be nonempty")
    if size > 256:
        raise ValueError("dense baseline is only intended for small validation fixtures")
    _require_positive(repeats, "repeats")
    stride %= size
    total = 0.0
    for _ in range(repeats):
        for row in range(size):
            for column, value in enumerate(values):
                weight = 0.0
                if column == row:
                    weight += 0.5
                if column == (row + stride) % size:
                    weight += 0.5
                total += value * weight
    return total


def validate_layout_case(case: LayoutBenchmarkCase) -> LayoutValidationResult:
    """Compare layout orders against direct and dense expected-output baselines."""
    values = reference_values(case.size)
    natural_checksum = circular_stride_checksum(values, case.stride, natural_order(case.size), case.repeats)
    gcd_checksum = circular_stride_checksum(values, case.stride, gcd_cycle_order(case.size, case.stride), case.repeats)
    direct_checksum = direct_circular_checksum(values, case.stride, case.repeats)
    dense_checksum = dense_circular_checksum(values, case.stride, case.repeats)
    return LayoutValidationResult(
        case=case,
        natural_checksum=natural_checksum,
        gcd_cycle_checksum=gcd_checksum,
        direct_checksum=direct_checksum,
        dense_checksum=dense_checksum,
    )


def validate_layout_grid(cases: Sequence[LayoutBenchmarkCase] = DEFAULT_LAYOUT_CASES) -> tuple[LayoutValidationResult, ...]:
    """Validate a deterministic parameter grid for layout benchmark fixtures."""
    return tuple(validate_layout_case(case) for case in cases)


def time_cpu_order(name: str, size: int, stride: int, repeats: int, order: tuple[int, ...]) -> BenchmarkResult:
    values = reference_values(size)
    start = time.perf_counter()
    checksum = circular_stride_checksum(values, stride, order, repeats)
    elapsed = time.perf_counter() - start
    return BenchmarkResult(name=name, size=size, stride=stride, repeats=repeats, seconds=elapsed, checksum=checksum)


def run_cpu(size: int, stride: int, repeats: int) -> list[BenchmarkResult]:
    return [
        time_cpu_order("cpu:natural", size, stride, repeats, natural_order(size)),
        time_cpu_order("cpu:gcd_cycle", size, stride, repeats, gcd_cycle_order(size, stride)),
    ]


def run_cpu_grid(cases: Sequence[LayoutBenchmarkCase] = DEFAULT_LAYOUT_CASES) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    for case in cases:
        results.extend(run_cpu(case.size, case.stride, case.repeats))
    return results


def run_mlx(size: int, stride: int, repeats: int) -> list[BenchmarkResult]:
    try:
        import mlx.core as mx  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on optional local backend
        raise RuntimeError("MLX is not available in this Python environment") from exc

    values = mx.array(reference_values(size), dtype=mx.float32)
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
