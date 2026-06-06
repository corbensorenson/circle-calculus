from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean


def phase_coordinate(period: int, step: int) -> int:
    if period <= 0:
        raise ValueError("period must be positive")
    return step % period


def synthetic_periodic_signal(period: int, length: int, *, harmonic_weight: float = 0.25) -> tuple[float, ...]:
    """Return a deterministic synthetic signal with a known period."""
    if period <= 0:
        raise ValueError("period must be positive")
    if length <= 0:
        raise ValueError("length must be positive")
    values: list[float] = []
    for step in range(length):
        phase = 2.0 * math.pi * phase_coordinate(period, step) / period
        values.append(math.sin(phase) + harmonic_weight * math.cos(2.0 * phase))
    return tuple(values)


def coil_closure_error(values: tuple[float, ...], period: int) -> float:
    """Mean squared difference after shifting by a candidate period; lower is better."""
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) <= period:
        raise ValueError("values must contain at least one full candidate shift")
    return mean((values[index] - values[index - period]) ** 2 for index in range(period, len(values)))


def autocorrelation_score(values: tuple[float, ...], lag: int) -> float:
    """Normalized autocorrelation at a candidate lag; higher is better."""
    if lag <= 0:
        raise ValueError("lag must be positive")
    if len(values) <= lag:
        raise ValueError("values must contain at least one full candidate lag")
    left = values[lag:]
    right = values[:-lag]
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_energy = sum((a - left_mean) ** 2 for a in left)
    right_energy = sum((b - right_mean) ** 2 for b in right)
    if left_energy == 0.0 or right_energy == 0.0:
        return 0.0
    return numerator / math.sqrt(left_energy * right_energy)


def rank_periods_by_coil_closure(values: tuple[float, ...], candidates: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(candidates, key=lambda period: (coil_closure_error(values, period), period)))


def rank_periods_by_autocorrelation(values: tuple[float, ...], candidates: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(candidates, key=lambda period: (-autocorrelation_score(values, period), period)))


@dataclass(frozen=True)
class PeriodBenchmarkResult:
    true_period: int
    coil_best_period: int
    autocorrelation_best_period: int
    candidates: tuple[int, ...]


def benchmark_known_period(
    true_period: int,
    *,
    length: int = 240,
    candidates: tuple[int, ...] | None = None,
) -> PeriodBenchmarkResult:
    if candidates is None:
        candidates = tuple(range(max(1, true_period - 6), true_period + 7))
    values = synthetic_periodic_signal(true_period, length)
    return PeriodBenchmarkResult(
        true_period=true_period,
        coil_best_period=rank_periods_by_coil_closure(values, candidates)[0],
        autocorrelation_best_period=rank_periods_by_autocorrelation(values, candidates)[0],
        candidates=candidates,
    )
