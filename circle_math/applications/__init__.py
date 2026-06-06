"""Application-facing reference models for Circle Calculus."""

from .coil_data import (
    PeriodBenchmarkResult,
    autocorrelation_score,
    benchmark_known_period,
    coil_closure_error,
    phase_coordinate,
    rank_periods_by_autocorrelation,
    rank_periods_by_coil_closure,
    synthetic_periodic_signal,
)

__all__ = [
    "PeriodBenchmarkResult",
    "autocorrelation_score",
    "benchmark_known_period",
    "coil_closure_error",
    "phase_coordinate",
    "rank_periods_by_autocorrelation",
    "rank_periods_by_coil_closure",
    "synthetic_periodic_signal",
]
