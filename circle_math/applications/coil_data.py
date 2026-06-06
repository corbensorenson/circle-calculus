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


def deterministic_noise(step: int) -> float:
    """Small deterministic pseudo-noise in [-1, 1]."""
    return (((step * 37 + 11) % 101) - 50) / 50.0


def synthetic_noisy_periodic_signal(
    period: int,
    length: int,
    *,
    noise_weight: float = 0.15,
) -> tuple[float, ...]:
    base = synthetic_periodic_signal(period, length)
    return tuple(value + noise_weight * deterministic_noise(step) for step, value in enumerate(base))


def synthetic_aliased_signal(
    primary_period: int,
    alias_period: int,
    length: int,
    *,
    alias_weight: float = 0.45,
) -> tuple[float, ...]:
    primary = synthetic_periodic_signal(primary_period, length)
    alias = synthetic_periodic_signal(alias_period, length, harmonic_weight=0.0)
    return tuple(a + alias_weight * b for a, b in zip(primary, alias))


def synthetic_multi_period_signal(
    periods: tuple[int, ...],
    length: int,
    *,
    weights: tuple[float, ...] | None = None,
) -> tuple[float, ...]:
    if not periods:
        raise ValueError("periods must be nonempty")
    if weights is None:
        weights = tuple(1.0 / (index + 1) for index in range(len(periods)))
    if len(weights) != len(periods):
        raise ValueError("weights and periods must have the same length")
    components = [synthetic_periodic_signal(period, length) for period in periods]
    return tuple(
        sum(weight * component[step] for weight, component in zip(weights, components))
        for step in range(length)
    )


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


def periodogram_score(values: tuple[float, ...], period: int) -> float:
    """Naive single-frequency periodogram-style score; higher is better."""
    if period <= 0:
        raise ValueError("period must be positive")
    if not values:
        raise ValueError("values must be nonempty")
    real = 0.0
    imag = 0.0
    for step, value in enumerate(values):
        angle = 2.0 * math.pi * step / period
        real += value * math.cos(angle)
        imag -= value * math.sin(angle)
    return math.sqrt(real * real + imag * imag) / len(values)


def rank_periods_by_coil_closure(values: tuple[float, ...], candidates: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(candidates, key=lambda period: (coil_closure_error(values, period), period)))


def rank_periods_by_autocorrelation(values: tuple[float, ...], candidates: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(candidates, key=lambda period: (-autocorrelation_score(values, period), period)))


def rank_periods_by_periodogram(values: tuple[float, ...], candidates: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted(candidates, key=lambda period: (-periodogram_score(values, period), period)))


@dataclass(frozen=True)
class PeriodBenchmarkResult:
    true_period: int
    coil_best_period: int
    autocorrelation_best_period: int
    candidates: tuple[int, ...]


@dataclass(frozen=True)
class PeriodFixtureCaseResult:
    name: str
    expected_periods: tuple[int, ...]
    coil_best_period: int
    autocorrelation_best_period: int
    periodogram_best_period: int
    candidates: tuple[int, ...]
    note: str


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


def benchmark_period_fixture_suite() -> tuple[PeriodFixtureCaseResult, ...]:
    """Run deterministic periodic-data fixtures without upgrading usefulness claims."""
    cases = [
        (
            "clean",
            (12,),
            synthetic_periodic_signal(12, 240),
            tuple(range(5, 21)),
            "Clean known-period sanity check.",
        ),
        (
            "noisy",
            (12,),
            synthetic_noisy_periodic_signal(12, 240),
            tuple(range(5, 21)),
            "Deterministic noise checks robustness, not real-data usefulness.",
        ),
        (
            "aliased",
            (6, 12),
            synthetic_aliased_signal(12, 6, 240),
            tuple(range(4, 17)),
            "Aliased fixture accepts either visible component as an ambiguity.",
        ),
        (
            "multi_period",
            (12, 20),
            synthetic_multi_period_signal((12, 20), 240),
            tuple(range(6, 25)),
            "Multi-period fixture records which component each baseline prefers.",
        ),
    ]
    results: list[PeriodFixtureCaseResult] = []
    for name, expected_periods, values, candidates, note in cases:
        results.append(
            PeriodFixtureCaseResult(
                name=name,
                expected_periods=expected_periods,
                coil_best_period=rank_periods_by_coil_closure(values, candidates)[0],
                autocorrelation_best_period=rank_periods_by_autocorrelation(values, candidates)[0],
                periodogram_best_period=rank_periods_by_periodogram(values, candidates)[0],
                candidates=candidates,
                note=note,
            )
        )
    return tuple(results)
