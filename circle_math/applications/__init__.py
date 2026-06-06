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
from .circle_ai import (
    PhaseChannelBenchmarkResult,
    accuracy,
    adapter_block,
    default_positive_phases,
    fit_phase_lookup,
    memory_slot,
    mlx_available,
    periodic_phase_label,
    phase_channel,
    predict_phase_lookup,
    run_phase_channel_benchmark,
    synthetic_phase_dataset,
)

__all__ = [
    "PeriodBenchmarkResult",
    "PhaseChannelBenchmarkResult",
    "accuracy",
    "adapter_block",
    "autocorrelation_score",
    "benchmark_known_period",
    "coil_closure_error",
    "default_positive_phases",
    "fit_phase_lookup",
    "memory_slot",
    "mlx_available",
    "periodic_phase_label",
    "phase_coordinate",
    "phase_channel",
    "predict_phase_lookup",
    "rank_periods_by_autocorrelation",
    "rank_periods_by_coil_closure",
    "run_phase_channel_benchmark",
    "synthetic_phase_dataset",
    "synthetic_periodic_signal",
]
