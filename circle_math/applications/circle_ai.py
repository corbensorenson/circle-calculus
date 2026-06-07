"""Executable reference models for Circle AI application seeds.

These functions support examples, smoke tests, and tiny benchmark fixtures.
They are not formal proofs and they are not model-quality claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, lcm, sin, tau
from typing import Optional, Sequence


def _require_positive(value: int, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def phase_channel(period: int, position: int) -> int:
    """Return the phase-channel index ``position mod period``."""
    _require_positive(period, "period")
    return position % period


def memory_slot(bank_size: int, token: int) -> int:
    """Return the cyclic memory-bank slot ``token mod bank_size``."""
    _require_positive(bank_size, "bank_size")
    return token % bank_size


def adapter_block(block_size: int, channel: int) -> int:
    """Return the adapter block index ``channel mod block_size``."""
    _require_positive(block_size, "block_size")
    return channel % block_size


def normalize_multicoil_periods(periods: Sequence[int]) -> tuple[int, ...]:
    """Validate a nonempty tuple of positive MultiCoil periods."""
    normalized = tuple(periods)
    if not normalized:
        raise ValueError("periods must be nonempty")
    for period in normalized:
        _require_positive(period, "period")
    return normalized


def multicoil_phase(periods: Sequence[int], position: int) -> tuple[int, ...]:
    """Return the tuple of residues for a MultiCoil/RoPE-style position."""
    normalized = normalize_multicoil_periods(periods)
    return tuple(position % period for period in normalized)


def multicoil_cycle_length(periods: Sequence[int]) -> int:
    """Return the least common repeat horizon for a set of periods."""
    normalized = normalize_multicoil_periods(periods)
    cycle = 1
    for period in normalized:
        cycle = lcm(cycle, period)
    return cycle


def multicoil_phase_label(periods: Sequence[int], position: int) -> int:
    """Return a deterministic binary label controlled by combined phases."""
    phase = multicoil_phase(periods, position)
    score = sum((index + 1) * residue for index, residue in enumerate(phase))
    return 1 if score % 4 == 1 else 0


def default_positive_phases(period: int) -> tuple[int, ...]:
    """Choose a deterministic nontrivial phase-label pattern for fixtures."""
    _require_positive(period, "period")
    return tuple(phase for phase in range(period) if phase % 3 == 1)


def normalize_positive_phases(period: int, positive_phases: Optional[Sequence[int]]) -> tuple[int, ...]:
    """Validate and normalize a phase-label set."""
    _require_positive(period, "period")
    phases = default_positive_phases(period) if positive_phases is None else tuple(positive_phases)
    normalized = tuple(sorted({phase % period for phase in phases}))
    if not normalized:
        raise ValueError("positive_phases must contain at least one phase")
    if len(normalized) == period:
        raise ValueError("positive_phases must not contain every phase")
    return normalized


def periodic_phase_label(period: int, position: int, positive_phases: Optional[Sequence[int]] = None) -> int:
    """Return a deterministic binary label controlled only by the phase."""
    phases = normalize_positive_phases(period, positive_phases)
    return 1 if phase_channel(period, position) in phases else 0


def synthetic_phase_dataset(
    period: int,
    length: int,
    *,
    start: int = 0,
    positive_phases: Optional[Sequence[int]] = None,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return positions and binary labels for a known-period synthetic task."""
    _require_positive(period, "period")
    if length <= 0:
        raise ValueError("length must be positive")
    phases = normalize_positive_phases(period, positive_phases)
    positions = tuple(range(start, start + length))
    labels = tuple(periodic_phase_label(period, position, phases) for position in positions)
    return positions, labels


def majority_label(labels: Sequence[int]) -> int:
    """Return the deterministic majority label, using 1 as the tie breaker."""
    if not labels:
        raise ValueError("labels must be nonempty")
    positives = sum(1 for label in labels if label == 1)
    negatives = len(labels) - positives
    return 1 if positives >= negatives else 0


def fit_phase_lookup(period: int, positions: Sequence[int], labels: Sequence[int]) -> tuple[int, ...]:
    """Fit a phase-index lookup table by majority label for each phase."""
    _require_positive(period, "period")
    if len(positions) != len(labels):
        raise ValueError("positions and labels must have the same length")
    if not positions:
        raise ValueError("positions must be nonempty")
    fallback = majority_label(labels)
    counts = [[0, 0] for _ in range(period)]
    for position, label in zip(positions, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        counts[phase_channel(period, position)][label] += 1
    return tuple(
        fallback if zero_count + one_count == 0 else (1 if one_count >= zero_count else 0)
        for zero_count, one_count in counts
    )


def predict_phase_lookup(period: int, lookup: Sequence[int], positions: Sequence[int]) -> tuple[int, ...]:
    """Predict labels from a fitted phase lookup table."""
    _require_positive(period, "period")
    if len(lookup) != period:
        raise ValueError("lookup length must equal period")
    return tuple(lookup[phase_channel(period, position)] for position in positions)


def accuracy(predictions: Sequence[int], labels: Sequence[int]) -> float:
    """Return exact classification accuracy for deterministic fixtures."""
    if len(predictions) != len(labels):
        raise ValueError("predictions and labels must have the same length")
    if not labels:
        raise ValueError("labels must be nonempty")
    correct = sum(1 for prediction, label in zip(predictions, labels) if prediction == label)
    return correct / len(labels)


def mlx_available() -> bool:
    """Return whether the optional MLX backend can be imported."""
    try:
        import mlx.core  # type: ignore[import-not-found]  # noqa: F401
    except Exception:
        return False
    return True


def _mlx_accuracy(predictions: Sequence[int], labels: Sequence[int]) -> float:
    try:
        import mlx.core as mx  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on optional local backend
        raise RuntimeError("MLX is not available in this Python environment") from exc
    pred_array = mx.array(tuple(predictions), dtype=mx.int32)
    label_array = mx.array(tuple(labels), dtype=mx.int32)
    score = mx.mean((pred_array == label_array).astype(mx.float32))
    mx.eval(score)
    return float(score.item())


@dataclass(frozen=True)
class PhaseChannelBenchmarkResult:
    period: int
    train_length: int
    test_length: int
    positive_phases: tuple[int, ...]
    phase_channel_accuracy: float
    constant_accuracy: float
    backend: str
    note: str = "Synthetic phase fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedPhaseBenchmarkResult:
    period: int
    train_length: int
    test_length: int
    periodic_phase_accuracy: float
    periodic_dense_accuracy: float
    nonperiodic_phase_accuracy: float
    nonperiodic_dense_accuracy: float
    note: str = "Tiny learned-baseline fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedFeatureBaselineResult:
    period: int
    wrong_period: int
    train_length: int
    test_length: int
    periodic_cyclic_feature_accuracy: float
    periodic_dense_scalar_accuracy: float
    periodic_learned_position_accuracy: float
    periodic_wrong_period_accuracy: float
    nonperiodic_cyclic_feature_accuracy: float
    nonperiodic_dense_scalar_accuracy: float
    nonperiodic_learned_position_accuracy: float
    note: str = "Tiny learned-feature baseline fixture only; not a model-quality claim."


@dataclass(frozen=True)
class HarmonicFeatureBaselineResult:
    period: int
    wrong_period: int
    train_length: int
    test_length: int
    observed_feature_count: int
    cyclic_phase_accuracy: float
    harmonic_feature_accuracy: float
    wrong_harmonic_accuracy: float
    scalar_threshold_accuracy: float
    learned_position_accuracy: float
    nonperiodic_harmonic_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    note: str = "Tiny harmonic-feature baseline fixture only; not a model-quality claim."


@dataclass(frozen=True)
class AIBackendParityResult:
    fixture_count: int
    cpu_scores: tuple[tuple[str, float], ...]
    mlx_available: bool
    mlx_scores: tuple[tuple[str, float], ...]
    max_abs_delta: Optional[float]
    note: str = "AI backend parity fixture only; not a model-quality claim."


@dataclass(frozen=True)
class MemorySlotBenchmarkResult:
    bank_size: int
    train_length: int
    test_length: int
    slot_values: tuple[int, ...]
    cyclic_memory_accuracy: float
    scalar_threshold_accuracy: float
    constant_accuracy: float
    nonperiodic_cyclic_memory_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    train_collision_count: int
    max_train_slot_load: int
    note: str = "Synthetic cyclic-memory fixture only; not a model-quality claim."


@dataclass(frozen=True)
class CoilRetrievalBenchmarkResult:
    sequence_length: int
    query_count: int
    target_lag: int
    stride: int
    path_length: int
    local_window: int
    coil_path_accuracy: float
    local_window_accuracy: float
    wrong_stride_accuracy: float
    full_attention_accuracy: float
    near_control_lag: int
    near_control_coil_path_accuracy: float
    near_control_local_window_accuracy: float
    near_control_full_attention_accuracy: float
    note: str = "Synthetic coil-retrieval reachability fixture only; not a model-quality claim."


@dataclass(frozen=True)
class ContentGatedRetrievalBenchmarkResult:
    sequence_length: int
    query_count: int
    long_target_lag: int
    near_target_lag: int
    stride: int
    path_length: int
    local_window: int
    content_gated_accuracy: float
    static_coil_accuracy: float
    static_local_accuracy: float
    union_candidate_accuracy: float
    wrong_gate_accuracy: float
    full_attention_accuracy: float
    average_gated_candidate_count: float
    average_union_candidate_count: float
    average_full_candidate_count: float
    note: str = "Synthetic content-gated retrieval fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedContentGateRetrievalBenchmarkResult:
    sequence_length: int
    train_length: int
    test_length: int
    route_period: int
    wrong_route_period: int
    long_target_lag: int
    near_target_lag: int
    stride: int
    path_length: int
    local_window: int
    learned_route_lookup: tuple[int, ...]
    wrong_period_route_lookup: tuple[int, ...]
    required_route_sample: tuple[int, ...]
    learned_route_sample: tuple[int, ...]
    learned_route_accuracy: float
    wrong_period_route_accuracy: float
    learned_gate_accuracy: float
    static_coil_accuracy: float
    static_local_accuracy: float
    wrong_period_gate_accuracy: float
    flipped_gate_accuracy: float
    union_candidate_accuracy: float
    full_attention_accuracy: float
    average_learned_candidate_count: float
    average_union_candidate_count: float
    average_full_candidate_count: float
    note: str = "Synthetic learned content-gate retrieval fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LoopedRecurrenceBenchmarkResult:
    loop_period: int
    train_length: int
    test_length: int
    fixed_loop_budget: int
    over_loop_budget: int
    overthink_tolerance: int
    sparse_phase_router_steps: tuple[int, ...]
    observed_exit_steps: tuple[int, ...]
    single_pass_accuracy: float
    fixed_loop_accuracy: float
    adaptive_exit_accuracy: float
    recurrent_memory_accuracy: float
    sparse_phase_router_accuracy: float
    over_looped_accuracy: float
    nonperiodic_loop_phase_accuracy: float
    nonperiodic_dense_threshold_accuracy: float
    note: str = "Synthetic looped-recurrence schedule fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LoopExitCertificateResult:
    loop_period: int
    sample_index: int
    max_loops: int
    overthink_tolerance: int
    required_steps: int
    overthinking_boundary: int
    score_trace: tuple[int, ...]
    exit_step: Optional[int]
    exit_available: bool
    within_budget: bool
    within_guardrail: bool
    note: str = "Synthetic loop-exit certificate fixture only; not a model-quality claim."


@dataclass(frozen=True)
class TokenLevelRecurrenceBenchmarkResult:
    loop_period: int
    token_count: int
    max_budget: int
    fixed_global_budget: int
    over_loop_budget: int
    wrong_budget_shift: int
    overthink_tolerance: int
    selected_loop_block: tuple[int, int]
    resolution_levels: tuple[str, ...]
    token_budgets: tuple[int, ...]
    active_token_counts: tuple[int, ...]
    token_level_accuracy: float
    fixed_global_budget_accuracy: float
    wrong_budget_accuracy: float
    over_looped_accuracy: float
    nonperiodic_token_level_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    average_active_tokens: float
    note: str = "Synthetic token-level recurrence routing fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedTokenLevelRecurrenceBenchmarkResult:
    loop_period: int
    wrong_period: int
    train_token_count: int
    test_token_count: int
    max_budget: int
    fixed_global_budget: int
    over_loop_budget: int
    wrong_budget_shift: int
    overthink_tolerance: int
    learned_budget_lookup: tuple[int, ...]
    wrong_period_budget_lookup: tuple[int, ...]
    required_budget_sample: tuple[int, ...]
    learned_budget_sample: tuple[int, ...]
    wrong_shift_budget_sample: tuple[int, ...]
    active_token_counts: tuple[int, ...]
    learned_token_router_accuracy: float
    fixed_global_budget_accuracy: float
    wrong_period_router_accuracy: float
    wrong_shift_accuracy: float
    over_looped_accuracy: float
    nonperiodic_phase_lookup_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    average_active_tokens: float
    note: str = "Synthetic learned token-level recurrence fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedMiddleBlockRecurrenceBenchmarkResult:
    block_count: int
    train_length: int
    test_length: int
    loop_period: int
    block_period: int
    wrong_block_period: int
    wrong_budget_period: int
    selected_loop_block: tuple[int, int]
    wrong_loop_block: tuple[int, int]
    selected_block_indices: tuple[int, ...]
    max_budget: int
    fixed_loop_budget: int
    over_loop_budget: int
    overthink_tolerance: int
    learned_block_lookup: tuple[int, ...]
    learned_budget_lookup: tuple[int, ...]
    wrong_block_period_lookup: tuple[int, ...]
    wrong_budget_period_lookup: tuple[int, ...]
    required_block_sample: tuple[int, ...]
    learned_block_sample: tuple[int, ...]
    wrong_block_sample: tuple[int, ...]
    required_budget_sample: tuple[int, ...]
    learned_budget_sample: tuple[int, ...]
    wrong_budget_sample: tuple[int, ...]
    active_sample_counts: tuple[int, ...]
    learned_middle_block_router_accuracy: float
    selected_band_phase_budget_accuracy: float
    full_block_phase_budget_accuracy: float
    fixed_loop_budget_accuracy: float
    wrong_block_period_accuracy: float
    wrong_budget_period_accuracy: float
    wrong_loop_block_accuracy: float
    over_looped_accuracy: float
    average_learned_block_passes: float
    average_selected_band_passes: float
    average_full_block_passes: float
    note: str = "Synthetic learned middle-block recurrence fixture only; not a model-quality claim."


@dataclass(frozen=True)
class MiddleBlockRecurrenceBenchmarkResult:
    block_count: int
    sample_count: int
    loop_period: int
    selected_loop_block: tuple[int, int]
    wrong_loop_block: tuple[int, int]
    max_budget: int
    fixed_loop_budget: int
    over_loop_budget: int
    overthink_tolerance: int
    selected_block_indices: tuple[int, ...]
    required_block_sample: tuple[int, ...]
    required_budget_sample: tuple[int, ...]
    selected_middle_block_accuracy: float
    full_block_phase_budget_accuracy: float
    fixed_loop_budget_accuracy: float
    wrong_block_accuracy: float
    over_looped_accuracy: float
    average_selected_block_passes: float
    average_full_block_passes: float
    note: str = "Synthetic middle-block recurrence fixture only; not a model-quality claim."


@dataclass(frozen=True)
class MultiResolutionRecurrenceBenchmarkResult:
    loop_period: int
    sample_count: int
    max_budget: int
    fixed_loop_budget: int
    wrong_resolution_shift: int
    over_loop_budget: int
    overthink_tolerance: int
    resolution_levels: tuple[str, ...]
    required_budget_sample: tuple[int, ...]
    required_resolution_sample: tuple[str, ...]
    active_sample_counts: tuple[int, ...]
    multi_resolution_accuracy: float
    single_resolution_coarse_accuracy: float
    single_resolution_fine_accuracy: float
    fixed_budget_accuracy: float
    wrong_resolution_accuracy: float
    over_looped_accuracy: float
    average_active_samples: float
    note: str = "Synthetic multi-resolution recurrence fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedMultiResolutionRecurrenceBenchmarkResult:
    loop_period: int
    wrong_budget_period: int
    wrong_resolution_period: int
    train_length: int
    test_length: int
    max_budget: int
    fixed_loop_budget: int
    over_loop_budget: int
    overthink_tolerance: int
    resolution_levels: tuple[str, ...]
    learned_budget_lookup: tuple[int, ...]
    learned_resolution_lookup: tuple[str, ...]
    wrong_budget_period_lookup: tuple[int, ...]
    wrong_resolution_period_lookup: tuple[str, ...]
    required_budget_sample: tuple[int, ...]
    learned_budget_sample: tuple[int, ...]
    wrong_budget_sample: tuple[int, ...]
    required_resolution_sample: tuple[str, ...]
    learned_resolution_sample: tuple[str, ...]
    wrong_resolution_sample: tuple[str, ...]
    active_sample_counts: tuple[int, ...]
    learned_multi_resolution_router_accuracy: float
    single_resolution_coarse_accuracy: float
    single_resolution_fine_accuracy: float
    fixed_budget_accuracy: float
    wrong_budget_period_accuracy: float
    wrong_resolution_period_accuracy: float
    over_looped_accuracy: float
    average_active_samples: float
    note: str = "Synthetic learned multi-resolution recurrence fixture only; not a model-quality claim."


@dataclass(frozen=True)
class LearnedRecurrenceScheduleBenchmarkResult:
    loop_period: int
    wrong_period: int
    train_length: int
    test_length: int
    fixed_loop_budget: int
    over_loop_budget: int
    overthink_tolerance: int
    learned_budget_lookup: tuple[int, ...]
    wrong_period_budget_lookup: tuple[int, ...]
    required_budget_sample: tuple[int, ...]
    learned_budget_sample: tuple[int, ...]
    learned_phase_router_accuracy: float
    fixed_loop_budget_accuracy: float
    wrong_period_router_accuracy: float
    over_looped_accuracy: float
    note: str = "Synthetic learned recurrence-schedule fixture only; not a model-quality claim."


@dataclass(frozen=True)
class TrainingFreeLoopWrapperBenchmarkResult:
    loop_period: int
    sample_count: int
    max_loops: int
    fixed_loop_budget: int
    wrong_loop_period: int
    over_loop_budget: int
    overthink_tolerance: int
    backend: str
    phase_budgets: tuple[int, ...]
    active_sample_counts: tuple[int, ...]
    budget_histogram: tuple[tuple[int, int], ...]
    average_phase_budget: float
    single_pass_accuracy: float
    fixed_loop_accuracy: float
    training_free_phase_budget_accuracy: float
    wrong_period_budget_accuracy: float
    over_loop_no_exit_accuracy: float
    nonperiodic_phase_budget_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    note: str = "Synthetic training-free loop-wrapper fixture only; not a model-quality claim."


@dataclass(frozen=True)
class AdapterBlockBenchmarkResult:
    block_size: int
    train_channels: int
    test_channels: int
    block_values: tuple[int, ...]
    adapter_block_accuracy: float
    scalar_channel_threshold_accuracy: float
    constant_accuracy: float
    nonperiodic_adapter_block_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    train_collision_count: int
    max_train_block_load: int
    note: str = "Synthetic adapter-block fixture only; not a model-quality claim."


@dataclass(frozen=True)
class AdapterParameterBudgetResult:
    channel_count: int
    block_size: int
    rank: int
    parameters_per_channel: int
    dense_adapter_parameters: int
    lora_parameters: int
    block_cyclic_parameters: int
    lora_to_dense_ratio: float
    block_to_dense_ratio: float
    channel_collision_count: int
    max_block_load: int
    note: str = "Synthetic adapter parameter-budget fixture only; not a model-quality claim."


@dataclass(frozen=True)
class CirculantMixerBenchmarkResult:
    period: int
    dense_parameters: int
    circulant_parameters: int
    parameter_ratio: float
    input_values: tuple[int, ...]
    kernel_values: tuple[int, ...]
    circulant_output: tuple[int, ...]
    dense_output: tuple[int, ...]
    wrong_shift_output: tuple[int, ...]
    max_abs_dense_delta: int
    wrong_shift_mismatch_count: int
    note: str = "Synthetic circulant mixer fixture only; not a model-quality claim."


@dataclass(frozen=True)
class MultiCoilRoPEBenchmarkResult:
    periods: tuple[int, ...]
    train_length: int
    test_length: int
    cycle_length: int
    observed_phase_count: int
    multicoil_phase_accuracy: float
    single_period_phase_accuracy: float
    scalar_threshold_accuracy: float
    constant_accuracy: float
    nonperiodic_multicoil_phase_accuracy: float
    nonperiodic_scalar_threshold_accuracy: float
    note: str = "Synthetic MultiCoil/RoPE-style phase fixture only; not a model-quality claim."


@dataclass(frozen=True)
class RoPERelativePhaseBenchmarkResult:
    period: int
    wrong_period: int
    train_length: int
    test_length: int
    positive_lags: tuple[int, ...]
    observed_relative_feature_count: int
    rope_relative_accuracy: float
    wrong_period_rope_accuracy: float
    query_position_accuracy: float
    scalar_query_threshold_accuracy: float
    nonperiodic_rope_relative_accuracy: float
    nonperiodic_scalar_query_threshold_accuracy: float
    note: str = "Synthetic RoPE-style relative phase fixture only; not a model-quality claim."


def run_phase_channel_benchmark(
    *,
    period: int = 8,
    train_length: int = 64,
    test_length: int = 32,
    positive_phases: Optional[Sequence[int]] = None,
    backend: str = "cpu",
) -> PhaseChannelBenchmarkResult:
    """Run a tiny deterministic phase-channel benchmark fixture.

    The fixture compares a phase-index lookup against a constant majority
    baseline on data whose label is known to be periodic. It is a harness
    sanity check, not evidence that phase channels improve real models.
    """
    _require_positive(period, "period")
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")
    phases = normalize_positive_phases(period, positive_phases)
    train_positions, train_labels = synthetic_phase_dataset(
        period,
        train_length,
        positive_phases=phases,
    )
    test_positions, test_labels = synthetic_phase_dataset(
        period,
        test_length,
        start=train_length,
        positive_phases=phases,
    )

    lookup = fit_phase_lookup(period, train_positions, train_labels)
    phase_predictions = predict_phase_lookup(period, lookup, test_positions)
    constant = majority_label(train_labels)
    constant_predictions = tuple(constant for _ in test_positions)

    if backend == "cpu":
        phase_accuracy = accuracy(phase_predictions, test_labels)
        constant_accuracy = accuracy(constant_predictions, test_labels)
    elif backend == "mlx":
        phase_accuracy = _mlx_accuracy(phase_predictions, test_labels)
        constant_accuracy = _mlx_accuracy(constant_predictions, test_labels)
    else:
        raise ValueError("backend must be 'cpu' or 'mlx'")

    return PhaseChannelBenchmarkResult(
        period=period,
        train_length=train_length,
        test_length=test_length,
        positive_phases=phases,
        phase_channel_accuracy=phase_accuracy,
        constant_accuracy=constant_accuracy,
        backend=backend,
    )


def nonperiodic_threshold_label(position: int, threshold: int) -> int:
    """Return a simple nonperiodic control label."""
    return 1 if position >= threshold else 0


def fit_threshold_classifier(positions: Sequence[int], labels: Sequence[int]) -> tuple[int, int]:
    """Fit a deterministic scalar threshold classifier.

    Returns ``(threshold, polarity)`` where polarity 1 predicts ``position >=
    threshold`` and polarity -1 predicts the opposite. This is a tiny dense
    scalar baseline, not a neural model.
    """
    if len(positions) != len(labels):
        raise ValueError("positions and labels must have the same length")
    if not positions:
        raise ValueError("positions must be nonempty")
    candidates = tuple(range(min(positions), max(positions) + 2))
    best = (0.0, candidates[0], 1)
    for threshold in candidates:
        for polarity in (1, -1):
            predictions = tuple(
                1 if (position >= threshold) == (polarity == 1) else 0
                for position in positions
            )
            score = accuracy(predictions, labels)
            if score > best[0]:
                best = (score, threshold, polarity)
    return best[1], best[2]


def predict_threshold_classifier(positions: Sequence[int], threshold: int, polarity: int) -> tuple[int, ...]:
    if polarity not in (1, -1):
        raise ValueError("polarity must be 1 or -1")
    return tuple(1 if (position >= threshold) == (polarity == 1) else 0 for position in positions)


def _fit_position_lookup(positions: Sequence[int], labels: Sequence[int]) -> tuple[int, tuple[tuple[int, int], ...]]:
    if len(positions) != len(labels):
        raise ValueError("positions and labels must have the same length")
    if not positions:
        raise ValueError("positions must be nonempty")
    fallback = majority_label(labels)
    counts: dict[int, list[int]] = {}
    for position, label in zip(positions, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        if position not in counts:
            counts[position] = [0, 0]
        counts[position][label] += 1
    entries = tuple(
        (position, 1 if one_count >= zero_count else 0)
        for position, (zero_count, one_count) in sorted(counts.items())
    )
    return fallback, entries


def _predict_position_lookup(
    lookup: tuple[int, tuple[tuple[int, int], ...]],
    positions: Sequence[int],
) -> tuple[int, ...]:
    fallback, entries = lookup
    lookup_map = dict(entries)
    return tuple(lookup_map.get(position, fallback) for position in positions)


def harmonic_feature(period: int, position: int, *, harmonic: int = 1) -> tuple[float, float]:
    """Return a rounded sine/cosine feature for a circular position.

    This is a tiny Fourier/RoPE-style feature, not a learned embedding. Values
    are rounded so deterministic lookup tables can use them as dictionary keys.
    """
    _require_positive(period, "period")
    _require_positive(harmonic, "harmonic")
    angle = tau * harmonic * phase_channel(period, position) / period
    return (round(cos(angle), 12), round(sin(angle), 12))


def fit_harmonic_feature_lookup(
    period: int,
    positions: Sequence[int],
    labels: Sequence[int],
    *,
    harmonic: int = 1,
) -> tuple[tuple[tuple[float, float], int], ...]:
    """Fit a deterministic lookup table over sine/cosine phase features."""
    _require_positive(period, "period")
    _require_positive(harmonic, "harmonic")
    if len(positions) != len(labels):
        raise ValueError("positions and labels must have the same length")
    if not positions:
        raise ValueError("positions must be nonempty")
    counts: dict[tuple[float, float], list[int]] = {}
    for position, label in zip(positions, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        feature = harmonic_feature(period, position, harmonic=harmonic)
        if feature not in counts:
            counts[feature] = [0, 0]
        counts[feature][label] += 1
    entries = []
    for feature, (zero_count, one_count) in counts.items():
        entries.append((feature, 1 if one_count >= zero_count else 0))
    return tuple(sorted(entries))


def predict_harmonic_feature_lookup(
    period: int,
    lookup: Sequence[tuple[tuple[float, float], int]],
    positions: Sequence[int],
    *,
    harmonic: int = 1,
) -> tuple[int, ...]:
    """Predict labels from a fitted sine/cosine phase-feature table."""
    _require_positive(period, "period")
    _require_positive(harmonic, "harmonic")
    lookup_map = {feature: label for feature, label in lookup}
    if not lookup_map:
        raise ValueError("lookup must be nonempty")
    fallback = majority_label(tuple(lookup_map.values()))
    return tuple(
        lookup_map.get(harmonic_feature(period, position, harmonic=harmonic), fallback)
        for position in positions
    )


def run_learned_phase_baseline_benchmark(
    *,
    period: int = 8,
    train_length: int = 64,
    test_length: int = 32,
) -> LearnedPhaseBenchmarkResult:
    """Compare phase lookup against a learned scalar threshold baseline."""
    train_positions, periodic_train_labels = synthetic_phase_dataset(period, train_length)
    test_positions, periodic_test_labels = synthetic_phase_dataset(period, test_length, start=train_length)

    phase_lookup = fit_phase_lookup(period, train_positions, periodic_train_labels)
    periodic_phase_predictions = predict_phase_lookup(period, phase_lookup, test_positions)
    threshold, polarity = fit_threshold_classifier(train_positions, periodic_train_labels)
    periodic_dense_predictions = predict_threshold_classifier(test_positions, threshold, polarity)

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in train_positions)
    control_test_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in test_positions)
    control_phase_lookup = fit_phase_lookup(period, train_positions, control_train_labels)
    control_phase_predictions = predict_phase_lookup(period, control_phase_lookup, test_positions)
    control_threshold_fit, control_polarity = fit_threshold_classifier(train_positions, control_train_labels)
    control_dense_predictions = predict_threshold_classifier(test_positions, control_threshold_fit, control_polarity)

    return LearnedPhaseBenchmarkResult(
        period=period,
        train_length=train_length,
        test_length=test_length,
        periodic_phase_accuracy=accuracy(periodic_phase_predictions, periodic_test_labels),
        periodic_dense_accuracy=accuracy(periodic_dense_predictions, periodic_test_labels),
        nonperiodic_phase_accuracy=accuracy(control_phase_predictions, control_test_labels),
        nonperiodic_dense_accuracy=accuracy(control_dense_predictions, control_test_labels),
    )


def run_learned_feature_baseline_benchmark(
    *,
    period: int = 8,
    wrong_period: int = 7,
    train_length: int = 64,
    test_length: int = 32,
) -> LearnedFeatureBaselineResult:
    """Compare cyclic features with small ordinary learned baselines.

    This fixture is still synthetic and tiny. It checks whether a correct
    cyclic phase feature solves a known-period task while dense scalar,
    absolute-position lookup, and wrong-period phase baselines stay weaker;
    the nonperiodic control checks that the scalar baseline wins when the
    target is not cyclic.
    """
    _require_positive(period, "period")
    _require_positive(wrong_period, "wrong_period")
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")

    train_positions, periodic_train_labels = synthetic_phase_dataset(period, train_length)
    test_positions, periodic_test_labels = synthetic_phase_dataset(period, test_length, start=train_length)

    cyclic_lookup = fit_phase_lookup(period, train_positions, periodic_train_labels)
    periodic_cyclic_predictions = predict_phase_lookup(period, cyclic_lookup, test_positions)
    dense_threshold, dense_polarity = fit_threshold_classifier(train_positions, periodic_train_labels)
    periodic_dense_predictions = predict_threshold_classifier(test_positions, dense_threshold, dense_polarity)
    position_lookup = _fit_position_lookup(train_positions, periodic_train_labels)
    periodic_position_predictions = _predict_position_lookup(position_lookup, test_positions)
    wrong_lookup = fit_phase_lookup(wrong_period, train_positions, periodic_train_labels)
    periodic_wrong_predictions = predict_phase_lookup(wrong_period, wrong_lookup, test_positions)

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in train_positions)
    control_test_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in test_positions)
    control_cyclic_lookup = fit_phase_lookup(period, train_positions, control_train_labels)
    control_cyclic_predictions = predict_phase_lookup(period, control_cyclic_lookup, test_positions)
    control_dense_threshold, control_dense_polarity = fit_threshold_classifier(
        train_positions,
        control_train_labels,
    )
    control_dense_predictions = predict_threshold_classifier(
        test_positions,
        control_dense_threshold,
        control_dense_polarity,
    )
    control_position_lookup = _fit_position_lookup(train_positions, control_train_labels)
    control_position_predictions = _predict_position_lookup(control_position_lookup, test_positions)

    return LearnedFeatureBaselineResult(
        period=period,
        wrong_period=wrong_period,
        train_length=train_length,
        test_length=test_length,
        periodic_cyclic_feature_accuracy=accuracy(periodic_cyclic_predictions, periodic_test_labels),
        periodic_dense_scalar_accuracy=accuracy(periodic_dense_predictions, periodic_test_labels),
        periodic_learned_position_accuracy=accuracy(periodic_position_predictions, periodic_test_labels),
        periodic_wrong_period_accuracy=accuracy(periodic_wrong_predictions, periodic_test_labels),
        nonperiodic_cyclic_feature_accuracy=accuracy(control_cyclic_predictions, control_test_labels),
        nonperiodic_dense_scalar_accuracy=accuracy(control_dense_predictions, control_test_labels),
        nonperiodic_learned_position_accuracy=accuracy(control_position_predictions, control_test_labels),
    )


def run_harmonic_feature_baseline_benchmark(
    *,
    period: int = 8,
    wrong_period: int = 7,
    train_length: int = 64,
    test_length: int = 32,
) -> HarmonicFeatureBaselineResult:
    """Compare cyclic phase lookup with Fourier/RoPE-style feature baselines.

    The positive task is generated from the true period. A correct harmonic
    feature lookup and a phase lookup should both solve it; wrong-period,
    scalar-threshold, and absolute-position lookup baselines should not be
    confused with real evidence. The nonperiodic control must still favor the
    scalar baseline. This is not a neural-network or RoPE quality benchmark.
    """
    _require_positive(period, "period")
    _require_positive(wrong_period, "wrong_period")
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")

    train_positions, periodic_train_labels = synthetic_phase_dataset(period, train_length)
    test_positions, periodic_test_labels = synthetic_phase_dataset(period, test_length, start=train_length)

    phase_lookup = fit_phase_lookup(period, train_positions, periodic_train_labels)
    phase_predictions = predict_phase_lookup(period, phase_lookup, test_positions)
    harmonic_lookup = fit_harmonic_feature_lookup(period, train_positions, periodic_train_labels)
    harmonic_predictions = predict_harmonic_feature_lookup(period, harmonic_lookup, test_positions)
    wrong_harmonic_lookup = fit_harmonic_feature_lookup(wrong_period, train_positions, periodic_train_labels)
    wrong_harmonic_predictions = predict_harmonic_feature_lookup(
        wrong_period,
        wrong_harmonic_lookup,
        test_positions,
    )
    threshold, polarity = fit_threshold_classifier(train_positions, periodic_train_labels)
    threshold_predictions = predict_threshold_classifier(test_positions, threshold, polarity)
    position_lookup = _fit_position_lookup(train_positions, periodic_train_labels)
    position_predictions = _predict_position_lookup(position_lookup, test_positions)

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in train_positions)
    control_test_labels = tuple(nonperiodic_threshold_label(position, control_threshold) for position in test_positions)
    control_harmonic_lookup = fit_harmonic_feature_lookup(period, train_positions, control_train_labels)
    control_harmonic_predictions = predict_harmonic_feature_lookup(
        period,
        control_harmonic_lookup,
        test_positions,
    )
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_positions,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_positions,
        control_threshold_fit,
        control_polarity,
    )

    return HarmonicFeatureBaselineResult(
        period=period,
        wrong_period=wrong_period,
        train_length=train_length,
        test_length=test_length,
        observed_feature_count=len(harmonic_lookup),
        cyclic_phase_accuracy=accuracy(phase_predictions, periodic_test_labels),
        harmonic_feature_accuracy=accuracy(harmonic_predictions, periodic_test_labels),
        wrong_harmonic_accuracy=accuracy(wrong_harmonic_predictions, periodic_test_labels),
        scalar_threshold_accuracy=accuracy(threshold_predictions, periodic_test_labels),
        learned_position_accuracy=accuracy(position_predictions, periodic_test_labels),
        nonperiodic_harmonic_accuracy=accuracy(control_harmonic_predictions, control_test_labels),
        nonperiodic_scalar_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
    )


def default_memory_slot_values(bank_size: int) -> tuple[int, ...]:
    """Choose a deterministic nontrivial binary value for each memory slot."""
    _require_positive(bank_size, "bank_size")
    values = tuple(1 if slot % 3 == 1 else 0 for slot in range(bank_size))
    if not any(values) or all(values):
        raise ValueError("bank_size must produce both positive and negative slot values")
    return values


def normalize_memory_slot_values(
    bank_size: int,
    slot_values: Optional[Sequence[int]],
) -> tuple[int, ...]:
    """Validate or create a binary value table indexed by memory slot."""
    _require_positive(bank_size, "bank_size")
    values = default_memory_slot_values(bank_size) if slot_values is None else tuple(slot_values)
    if len(values) != bank_size:
        raise ValueError("slot_values length must equal bank_size")
    if any(value not in (0, 1) for value in values):
        raise ValueError("slot_values must be binary")
    if not any(values):
        raise ValueError("slot_values must contain at least one positive slot")
    if all(values):
        raise ValueError("slot_values must contain at least one negative slot")
    return values


def synthetic_memory_slot_dataset(
    bank_size: int,
    length: int,
    *,
    start: int = 0,
    slot_values: Optional[Sequence[int]] = None,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return tokens and binary labels controlled only by cyclic memory slot."""
    if length <= 0:
        raise ValueError("length must be positive")
    values = normalize_memory_slot_values(bank_size, slot_values)
    tokens = tuple(range(start, start + length))
    labels = tuple(values[memory_slot(bank_size, token)] for token in tokens)
    return tokens, labels


def fit_memory_slot_lookup(bank_size: int, tokens: Sequence[int], labels: Sequence[int]) -> tuple[int, ...]:
    """Fit a slot-index lookup table by majority label for each memory slot."""
    _require_positive(bank_size, "bank_size")
    if len(tokens) != len(labels):
        raise ValueError("tokens and labels must have the same length")
    if not tokens:
        raise ValueError("tokens must be nonempty")
    fallback = majority_label(labels)
    counts = [[0, 0] for _ in range(bank_size)]
    for token, label in zip(tokens, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        counts[memory_slot(bank_size, token)][label] += 1
    return tuple(
        fallback if zero_count + one_count == 0 else (1 if one_count >= zero_count else 0)
        for zero_count, one_count in counts
    )


def predict_memory_slot_lookup(
    bank_size: int,
    lookup: Sequence[int],
    tokens: Sequence[int],
) -> tuple[int, ...]:
    """Predict labels from a fitted memory-slot lookup table."""
    _require_positive(bank_size, "bank_size")
    if len(lookup) != bank_size:
        raise ValueError("lookup length must equal bank_size")
    return tuple(lookup[memory_slot(bank_size, token)] for token in tokens)


def memory_slot_loads(bank_size: int, tokens: Sequence[int]) -> tuple[int, ...]:
    """Return how many tokens land in each cyclic memory slot."""
    _require_positive(bank_size, "bank_size")
    loads = [0 for _ in range(bank_size)]
    for token in tokens:
        loads[memory_slot(bank_size, token)] += 1
    return tuple(loads)


def memory_slot_collision_count(bank_size: int, tokens: Sequence[int]) -> int:
    """Count extra tokens beyond the first occupant of each used slot."""
    loads = memory_slot_loads(bank_size, tokens)
    return sum(max(0, load - 1) for load in loads)


def run_memory_slot_benchmark(
    *,
    bank_size: int = 8,
    train_length: int = 64,
    test_length: int = 32,
    slot_values: Optional[Sequence[int]] = None,
) -> MemorySlotBenchmarkResult:
    """Run a deterministic cyclic-memory fixture with baselines and a control.

    The positive fixture labels tokens by their memory slot. The negative
    control labels tokens by a scalar threshold, where circular slot lookup
    should not be the winning representation. This is a benchmark harness
    sanity check, not evidence that cyclic memory improves neural networks.
    """
    values = normalize_memory_slot_values(bank_size, slot_values)
    train_tokens, train_labels = synthetic_memory_slot_dataset(
        bank_size,
        train_length,
        slot_values=values,
    )
    test_tokens, test_labels = synthetic_memory_slot_dataset(
        bank_size,
        test_length,
        start=train_length,
        slot_values=values,
    )

    lookup = fit_memory_slot_lookup(bank_size, train_tokens, train_labels)
    memory_predictions = predict_memory_slot_lookup(bank_size, lookup, test_tokens)
    threshold, polarity = fit_threshold_classifier(train_tokens, train_labels)
    threshold_predictions = predict_threshold_classifier(test_tokens, threshold, polarity)
    constant = majority_label(train_labels)
    constant_predictions = tuple(constant for _ in test_tokens)

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(token, control_threshold)
        for token in train_tokens
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(token, control_threshold)
        for token in test_tokens
    )
    control_lookup = fit_memory_slot_lookup(bank_size, train_tokens, control_train_labels)
    control_memory_predictions = predict_memory_slot_lookup(bank_size, control_lookup, test_tokens)
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_tokens,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_tokens,
        control_threshold_fit,
        control_polarity,
    )
    train_loads = memory_slot_loads(bank_size, train_tokens)

    return MemorySlotBenchmarkResult(
        bank_size=bank_size,
        train_length=train_length,
        test_length=test_length,
        slot_values=values,
        cyclic_memory_accuracy=accuracy(memory_predictions, test_labels),
        scalar_threshold_accuracy=accuracy(threshold_predictions, test_labels),
        constant_accuracy=accuracy(constant_predictions, test_labels),
        nonperiodic_cyclic_memory_accuracy=accuracy(control_memory_predictions, control_test_labels),
        nonperiodic_scalar_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
        train_collision_count=memory_slot_collision_count(bank_size, train_tokens),
        max_train_slot_load=max(train_loads),
    )


def coil_attention_path(
    sequence_length: int,
    query_index: int,
    stride: int,
    path_length: int,
) -> tuple[int, ...]:
    """Return fixed-stride predecessor indices for a coil attention path."""
    _require_positive(sequence_length, "sequence_length")
    _require_positive(path_length, "path_length")
    if stride < 0:
        raise ValueError("stride must be nonnegative")
    return tuple((query_index - step * stride) % sequence_length for step in range(1, path_length + 1))


def local_window_indices(sequence_length: int, query_index: int, window: int) -> tuple[int, ...]:
    """Return predecessor indices in a local attention window."""
    _require_positive(sequence_length, "sequence_length")
    _require_positive(window, "window")
    return tuple((query_index - step) % sequence_length for step in range(1, window + 1))


def retrieval_target_index(sequence_length: int, query_index: int, target_lag: int) -> int:
    """Return the known dependency index for a synthetic retrieval target."""
    _require_positive(sequence_length, "sequence_length")
    if target_lag < 0:
        raise ValueError("target_lag must be nonnegative")
    return (query_index - target_lag) % sequence_length


def retrieval_hit_rate(
    sequence_length: int,
    query_indices: Sequence[int],
    target_lag: int,
    candidate_sets: Sequence[Sequence[int]],
) -> float:
    """Return how often a candidate attention set contains the target index."""
    if len(query_indices) != len(candidate_sets):
        raise ValueError("query_indices and candidate_sets must have the same length")
    if not query_indices:
        raise ValueError("query_indices must be nonempty")
    hits = 0
    for query_index, candidates in zip(query_indices, candidate_sets):
        target = retrieval_target_index(sequence_length, query_index, target_lag)
        if target in set(candidates):
            hits += 1
    return hits / len(query_indices)


def mixed_retrieval_target_lags(
    query_indices: Sequence[int],
    *,
    long_target_lag: int,
    near_target_lag: int,
) -> tuple[int, ...]:
    """Return alternating long/near target lags for gated retrieval fixtures."""
    if long_target_lag < 0:
        raise ValueError("long_target_lag must be nonnegative")
    if near_target_lag < 0:
        raise ValueError("near_target_lag must be nonnegative")
    if not query_indices:
        raise ValueError("query_indices must be nonempty")
    return tuple(long_target_lag if query_index % 2 == 0 else near_target_lag for query_index in query_indices)


def retrieval_hit_rate_by_lag(
    sequence_length: int,
    query_indices: Sequence[int],
    target_lags: Sequence[int],
    candidate_sets: Sequence[Sequence[int]],
) -> float:
    """Return hit rate when each query has its own target lag."""
    _require_positive(sequence_length, "sequence_length")
    if len(query_indices) != len(target_lags):
        raise ValueError("query_indices and target_lags must have the same length")
    if len(query_indices) != len(candidate_sets):
        raise ValueError("query_indices and candidate_sets must have the same length")
    if not query_indices:
        raise ValueError("query_indices must be nonempty")
    hits = 0
    for query_index, target_lag, candidates in zip(query_indices, target_lags, candidate_sets):
        target = retrieval_target_index(sequence_length, query_index, target_lag)
        if target in set(candidates):
            hits += 1
    return hits / len(query_indices)


def average_candidate_count(candidate_sets: Sequence[Sequence[int]]) -> float:
    """Return the average unique candidate count in a retrieval fixture."""
    if not candidate_sets:
        raise ValueError("candidate_sets must be nonempty")
    return sum(len(set(candidates)) for candidates in candidate_sets) / len(candidate_sets)


def run_coil_retrieval_benchmark(
    *,
    sequence_length: int = 64,
    query_count: int = 64,
    target_lag: int = 21,
    stride: int = 7,
    path_length: int = 3,
    local_window: int = 8,
    wrong_stride: int = 5,
    near_control_lag: int = 3,
) -> CoilRetrievalBenchmarkResult:
    """Run a deterministic coil-retrieval reachability fixture.

    The positive fixture asks whether a fixed coil path can reach a known
    dependency lag that local attention misses. The near-lag control asks the
    opposite: local attention should reach the dependency while the selected
    coil path should not. This measures reachability of candidate index sets,
    not neural attention quality.
    """
    _require_positive(sequence_length, "sequence_length")
    _require_positive(query_count, "query_count")
    _require_positive(path_length, "path_length")
    _require_positive(local_window, "local_window")
    if target_lag < 0:
        raise ValueError("target_lag must be nonnegative")
    if wrong_stride < 0:
        raise ValueError("wrong_stride must be nonnegative")
    if near_control_lag < 0:
        raise ValueError("near_control_lag must be nonnegative")

    query_indices = tuple(range(query_count))
    coil_candidates = tuple(
        coil_attention_path(sequence_length, query_index, stride, path_length)
        for query_index in query_indices
    )
    local_candidates = tuple(
        local_window_indices(sequence_length, query_index, local_window)
        for query_index in query_indices
    )
    wrong_stride_candidates = tuple(
        coil_attention_path(sequence_length, query_index, wrong_stride, path_length)
        for query_index in query_indices
    )
    full_candidates = tuple(tuple(range(sequence_length)) for _ in query_indices)

    return CoilRetrievalBenchmarkResult(
        sequence_length=sequence_length,
        query_count=query_count,
        target_lag=target_lag,
        stride=stride,
        path_length=path_length,
        local_window=local_window,
        coil_path_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            coil_candidates,
        ),
        local_window_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            local_candidates,
        ),
        wrong_stride_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            wrong_stride_candidates,
        ),
        full_attention_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            full_candidates,
        ),
        near_control_lag=near_control_lag,
        near_control_coil_path_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            near_control_lag,
            coil_candidates,
        ),
        near_control_local_window_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            near_control_lag,
            local_candidates,
        ),
        near_control_full_attention_accuracy=retrieval_hit_rate(
            sequence_length,
            query_indices,
            near_control_lag,
            full_candidates,
        ),
    )


def run_content_gated_retrieval_benchmark(
    *,
    sequence_length: int = 64,
    query_count: int = 64,
    long_target_lag: int = 21,
    near_target_lag: int = 3,
    stride: int = 7,
    path_length: int = 3,
    local_window: int = 8,
) -> ContentGatedRetrievalBenchmarkResult:
    """Run a deterministic content-gated coil/local retrieval fixture.

    Even-indexed queries require a long dependency that the selected coil path
    can reach; odd-indexed queries require a near dependency that the local
    window can reach. The content-gated route chooses between those candidate
    sets. This checks reachability and candidate budgets only, not neural
    attention quality.
    """
    _require_positive(sequence_length, "sequence_length")
    _require_positive(query_count, "query_count")
    _require_positive(path_length, "path_length")
    _require_positive(local_window, "local_window")
    if long_target_lag < 0:
        raise ValueError("long_target_lag must be nonnegative")
    if near_target_lag < 0:
        raise ValueError("near_target_lag must be nonnegative")
    if stride < 0:
        raise ValueError("stride must be nonnegative")

    query_indices = tuple(range(query_count))
    target_lags = mixed_retrieval_target_lags(
        query_indices,
        long_target_lag=long_target_lag,
        near_target_lag=near_target_lag,
    )
    coil_candidates = tuple(
        coil_attention_path(sequence_length, query_index, stride, path_length)
        for query_index in query_indices
    )
    local_candidates = tuple(
        local_window_indices(sequence_length, query_index, local_window)
        for query_index in query_indices
    )
    gated_candidates = tuple(
        coil if query_index % 2 == 0 else local
        for query_index, coil, local in zip(query_indices, coil_candidates, local_candidates)
    )
    wrong_gate_candidates = tuple(
        local if query_index % 2 == 0 else coil
        for query_index, coil, local in zip(query_indices, coil_candidates, local_candidates)
    )
    union_candidates = tuple(
        tuple(sorted(set(coil) | set(local)))
        for coil, local in zip(coil_candidates, local_candidates)
    )
    full_candidates = tuple(tuple(range(sequence_length)) for _ in query_indices)

    return ContentGatedRetrievalBenchmarkResult(
        sequence_length=sequence_length,
        query_count=query_count,
        long_target_lag=long_target_lag,
        near_target_lag=near_target_lag,
        stride=stride,
        path_length=path_length,
        local_window=local_window,
        content_gated_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            gated_candidates,
        ),
        static_coil_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            coil_candidates,
        ),
        static_local_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            local_candidates,
        ),
        union_candidate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            union_candidates,
        ),
        wrong_gate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            wrong_gate_candidates,
        ),
        full_attention_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            target_lags,
            full_candidates,
        ),
        average_gated_candidate_count=average_candidate_count(gated_candidates),
        average_union_candidate_count=average_candidate_count(union_candidates),
        average_full_candidate_count=average_candidate_count(full_candidates),
    )


def content_route_label(query_index: int) -> int:
    """Return the deterministic coil/local route label for mixed retrieval.

    ``1`` means use the selected coil path for a long dependency. ``0`` means
    use the local window for a near dependency.
    """
    return 1 if query_index % 2 == 0 else 0


def fit_content_route_lookup(
    route_period: int,
    query_indices: Sequence[int],
    route_labels: Sequence[int],
) -> tuple[int, ...]:
    """Fit a deterministic phase-to-route table by majority vote."""
    _require_positive(route_period, "route_period")
    query_tuple = tuple(query_indices)
    route_tuple = tuple(route_labels)
    if len(query_tuple) != len(route_tuple):
        raise ValueError("query_indices and route_labels must have the same length")
    if not query_tuple:
        raise ValueError("query_indices must be nonempty")
    for route in route_tuple:
        if route not in (0, 1):
            raise ValueError("route_labels must be binary")
    fallback = _majority_int(route_tuple)
    buckets: list[list[int]] = [[] for _ in range(route_period)]
    for query_index, route in zip(query_tuple, route_tuple):
        buckets[phase_channel(route_period, query_index)].append(route)
    return tuple(fallback if not bucket else _majority_int(bucket) for bucket in buckets)


def predict_content_route_lookup(
    route_period: int,
    lookup: Sequence[int],
    query_indices: Sequence[int],
) -> tuple[int, ...]:
    """Predict coil/local route labels from a fitted phase-to-route table."""
    _require_positive(route_period, "route_period")
    lookup_tuple = tuple(lookup)
    if len(lookup_tuple) != route_period:
        raise ValueError("lookup length must equal route_period")
    for route in lookup_tuple:
        if route not in (0, 1):
            raise ValueError("lookup values must be binary routes")
    return tuple(lookup_tuple[phase_channel(route_period, query_index)] for query_index in query_indices)


def _candidate_sets_for_routes(
    routes: Sequence[int],
    coil_candidates: Sequence[Sequence[int]],
    local_candidates: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    route_tuple = tuple(routes)
    if len(route_tuple) != len(coil_candidates):
        raise ValueError("routes and coil_candidates must have the same length")
    if len(route_tuple) != len(local_candidates):
        raise ValueError("routes and local_candidates must have the same length")
    candidates: list[tuple[int, ...]] = []
    for route, coil, local in zip(route_tuple, coil_candidates, local_candidates):
        if route == 1:
            candidates.append(tuple(coil))
        elif route == 0:
            candidates.append(tuple(local))
        else:
            raise ValueError("routes must be binary")
    return tuple(candidates)


def run_learned_content_gate_retrieval_benchmark(
    *,
    sequence_length: int = 64,
    train_length: int = 64,
    test_length: int = 32,
    route_period: int = 2,
    wrong_route_period: int = 3,
    long_target_lag: int = 21,
    near_target_lag: int = 3,
    stride: int = 7,
    path_length: int = 3,
    local_window: int = 8,
) -> LearnedContentGateRetrievalBenchmarkResult:
    """Run a learned phase-route fixture for coil/local retrieval.

    The route table is fit from examples whose target type is known: even
    query indices require the long coil path and odd query indices require the
    local window. This checks whether a tiny learned phase gate can recover the
    fixture route and candidate budget. It is not an attention-quality claim.
    """
    _require_positive(sequence_length, "sequence_length")
    _require_positive(train_length, "train_length")
    _require_positive(test_length, "test_length")
    _require_positive(route_period, "route_period")
    _require_positive(wrong_route_period, "wrong_route_period")
    _require_positive(path_length, "path_length")
    _require_positive(local_window, "local_window")
    if long_target_lag < 0:
        raise ValueError("long_target_lag must be nonnegative")
    if near_target_lag < 0:
        raise ValueError("near_target_lag must be nonnegative")
    if stride < 0:
        raise ValueError("stride must be nonnegative")

    train_queries = tuple(range(train_length))
    train_routes = tuple(content_route_label(query_index) for query_index in train_queries)
    test_queries = tuple(range(train_length, train_length + test_length))
    required_routes = tuple(content_route_label(query_index) for query_index in test_queries)
    target_lags = mixed_retrieval_target_lags(
        test_queries,
        long_target_lag=long_target_lag,
        near_target_lag=near_target_lag,
    )

    learned_lookup = fit_content_route_lookup(route_period, train_queries, train_routes)
    wrong_lookup = fit_content_route_lookup(wrong_route_period, train_queries, train_routes)
    learned_routes = predict_content_route_lookup(route_period, learned_lookup, test_queries)
    wrong_period_routes = predict_content_route_lookup(wrong_route_period, wrong_lookup, test_queries)
    flipped_routes = tuple(1 - route for route in required_routes)

    coil_candidates = tuple(
        coil_attention_path(sequence_length, query_index, stride, path_length)
        for query_index in test_queries
    )
    local_candidates = tuple(
        local_window_indices(sequence_length, query_index, local_window)
        for query_index in test_queries
    )
    learned_candidates = _candidate_sets_for_routes(learned_routes, coil_candidates, local_candidates)
    wrong_period_candidates = _candidate_sets_for_routes(
        wrong_period_routes,
        coil_candidates,
        local_candidates,
    )
    flipped_candidates = _candidate_sets_for_routes(flipped_routes, coil_candidates, local_candidates)
    union_candidates = tuple(
        tuple(sorted(set(coil) | set(local)))
        for coil, local in zip(coil_candidates, local_candidates)
    )
    full_candidates = tuple(tuple(range(sequence_length)) for _ in test_queries)

    return LearnedContentGateRetrievalBenchmarkResult(
        sequence_length=sequence_length,
        train_length=train_length,
        test_length=test_length,
        route_period=route_period,
        wrong_route_period=wrong_route_period,
        long_target_lag=long_target_lag,
        near_target_lag=near_target_lag,
        stride=stride,
        path_length=path_length,
        local_window=local_window,
        learned_route_lookup=learned_lookup,
        wrong_period_route_lookup=wrong_lookup,
        required_route_sample=required_routes[:12],
        learned_route_sample=learned_routes[:12],
        learned_route_accuracy=accuracy(learned_routes, required_routes),
        wrong_period_route_accuracy=accuracy(wrong_period_routes, required_routes),
        learned_gate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            learned_candidates,
        ),
        static_coil_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            coil_candidates,
        ),
        static_local_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            local_candidates,
        ),
        wrong_period_gate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            wrong_period_candidates,
        ),
        flipped_gate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            flipped_candidates,
        ),
        union_candidate_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            union_candidates,
        ),
        full_attention_accuracy=retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            target_lags,
            full_candidates,
        ),
        average_learned_candidate_count=average_candidate_count(learned_candidates),
        average_union_candidate_count=average_candidate_count(union_candidates),
        average_full_candidate_count=average_candidate_count(full_candidates),
    )


def loop_required_steps(loop_period: int, sample_index: int) -> int:
    """Return the synthetic recurrence depth required by a sample."""
    _require_positive(loop_period, "loop_period")
    return phase_channel(loop_period, sample_index) + 1


def loop_score_trace(required_steps: int, max_loops: int, *, overthink_tolerance: int = 1) -> tuple[int, ...]:
    """Return a binary success trace over recurrence steps.

    A sample becomes solvable at its required loop step. It remains valid for
    ``overthink_tolerance`` extra steps, then degrades. This models the
    overthinking guardrail as a fixture condition, not as a theorem about
    real models.
    """
    _require_positive(required_steps, "required_steps")
    _require_positive(max_loops, "max_loops")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    return tuple(
        1 if required_steps <= step <= required_steps + overthink_tolerance else 0
        for step in range(1, max_loops + 1)
    )


def loop_exit_step(required_steps: int, max_loops: int, *, overthink_tolerance: int = 1) -> Optional[int]:
    """Return the first successful loop step, if one exists."""
    trace = loop_score_trace(required_steps, max_loops, overthink_tolerance=overthink_tolerance)
    for index, score in enumerate(trace, start=1):
        if score == 1:
            return index
    return None


def loop_exit_certificate(
    loop_period: int,
    sample_index: int,
    max_loops: int,
    *,
    overthink_tolerance: int = 1,
) -> LoopExitCertificateResult:
    """Return a deterministic loop-exit certificate for one synthetic sample."""
    _require_positive(loop_period, "loop_period")
    _require_positive(max_loops, "max_loops")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    required = loop_required_steps(loop_period, sample_index)
    boundary = required + overthink_tolerance
    trace = loop_score_trace(required, max_loops, overthink_tolerance=overthink_tolerance)
    exit_step = loop_exit_step(required, max_loops, overthink_tolerance=overthink_tolerance)
    return LoopExitCertificateResult(
        loop_period=loop_period,
        sample_index=sample_index,
        max_loops=max_loops,
        overthink_tolerance=overthink_tolerance,
        required_steps=required,
        overthinking_boundary=boundary,
        score_trace=trace,
        exit_step=exit_step,
        exit_available=exit_step is not None,
        within_budget=exit_step is not None and exit_step <= max_loops,
        within_guardrail=exit_step is not None and exit_step <= boundary,
    )


def _loop_fixed_budget_predictions(
    loop_period: int,
    sample_indices: Sequence[int],
    budget: int,
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    _require_positive(budget, "budget")
    return tuple(
        loop_score_trace(
            loop_required_steps(loop_period, sample_index),
            budget,
            overthink_tolerance=overthink_tolerance,
        )[-1]
        for sample_index in sample_indices
    )


def _loop_adaptive_exit_predictions(
    loop_period: int,
    sample_indices: Sequence[int],
    budget: int,
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    _require_positive(budget, "budget")
    return tuple(
        1
        if loop_exit_step(
            loop_required_steps(loop_period, sample_index),
            budget,
            overthink_tolerance=overthink_tolerance,
        )
        is not None
        else 0
        for sample_index in sample_indices
    )


def _loop_sparse_router_predictions(
    loop_period: int,
    sample_indices: Sequence[int],
    routed_steps: Sequence[int],
) -> tuple[int, ...]:
    normalized_steps = tuple(sorted(set(routed_steps)))
    if not normalized_steps:
        raise ValueError("routed_steps must be nonempty")
    for step in normalized_steps:
        _require_positive(step, "routed step")
    return tuple(
        1 if loop_required_steps(loop_period, sample_index) in normalized_steps else 0
        for sample_index in sample_indices
    )


def _observed_loop_exit_steps(
    loop_period: int,
    sample_indices: Sequence[int],
    budget: int,
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    exits = {
        step
        for sample_index in sample_indices
        for step in [
            loop_exit_step(
                loop_required_steps(loop_period, sample_index),
                budget,
                overthink_tolerance=overthink_tolerance,
            )
        ]
        if step is not None
    }
    return tuple(sorted(exits))


def run_looped_recurrence_benchmark(
    *,
    loop_period: int = 4,
    train_length: int = 64,
    test_length: int = 32,
    fixed_loop_budget: int = 4,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 1,
    sparse_phase_router_steps: Optional[Sequence[int]] = None,
) -> LoopedRecurrenceBenchmarkResult:
    """Run a deterministic looped/recursive transformer schedule fixture.

    The positive fixture gives each sample a required recurrence depth. It
    compares a single pass, a fixed loop budget, adaptive exit, recurrent
    memory that keeps any successful intermediate state, a sparse phase-router
    baseline, and an over-looped control. The nonperiodic control compares a
    loop-phase lookup against a dense scalar threshold baseline.
    """
    _require_positive(loop_period, "loop_period")
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    routed_steps = tuple(sparse_phase_router_steps) if sparse_phase_router_steps is not None else (1, 3)

    train_indices = tuple(range(train_length))
    test_indices = tuple(range(train_length, train_length + test_length))
    positive_labels = tuple(1 for _ in test_indices)

    single_pass_predictions = _loop_fixed_budget_predictions(
        loop_period,
        test_indices,
        1,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_loop_predictions = _loop_fixed_budget_predictions(
        loop_period,
        test_indices,
        fixed_loop_budget,
        overthink_tolerance=overthink_tolerance,
    )
    adaptive_predictions = _loop_adaptive_exit_predictions(
        loop_period,
        test_indices,
        fixed_loop_budget,
        overthink_tolerance=overthink_tolerance,
    )
    recurrent_memory_predictions = tuple(
        1 if value else 0
        for value in adaptive_predictions
    )
    sparse_router_predictions = _loop_sparse_router_predictions(loop_period, test_indices, routed_steps)
    over_looped_predictions = _loop_fixed_budget_predictions(
        loop_period,
        test_indices,
        over_loop_budget,
        overthink_tolerance=overthink_tolerance,
    )

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(sample_index, control_threshold)
        for sample_index in train_indices
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(sample_index, control_threshold)
        for sample_index in test_indices
    )
    control_loop_lookup = fit_phase_lookup(loop_period, train_indices, control_train_labels)
    control_loop_predictions = predict_phase_lookup(loop_period, control_loop_lookup, test_indices)
    control_threshold_fit, control_polarity = fit_threshold_classifier(train_indices, control_train_labels)
    control_threshold_predictions = predict_threshold_classifier(
        test_indices,
        control_threshold_fit,
        control_polarity,
    )

    return LoopedRecurrenceBenchmarkResult(
        loop_period=loop_period,
        train_length=train_length,
        test_length=test_length,
        fixed_loop_budget=fixed_loop_budget,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        sparse_phase_router_steps=tuple(sorted(set(routed_steps))),
        observed_exit_steps=_observed_loop_exit_steps(
            loop_period,
            test_indices,
            fixed_loop_budget,
            overthink_tolerance=overthink_tolerance,
        ),
        single_pass_accuracy=accuracy(single_pass_predictions, positive_labels),
        fixed_loop_accuracy=accuracy(fixed_loop_predictions, positive_labels),
        adaptive_exit_accuracy=accuracy(adaptive_predictions, positive_labels),
        recurrent_memory_accuracy=accuracy(recurrent_memory_predictions, positive_labels),
        sparse_phase_router_accuracy=accuracy(sparse_router_predictions, positive_labels),
        over_looped_accuracy=accuracy(over_looped_predictions, positive_labels),
        nonperiodic_loop_phase_accuracy=accuracy(control_loop_predictions, control_test_labels),
        nonperiodic_dense_threshold_accuracy=accuracy(control_threshold_predictions, control_test_labels),
    )


def token_recurrence_budget(loop_period: int, token_index: int) -> int:
    """Return the routed recurrence budget for a token-level fixture."""
    return loop_required_steps(loop_period, token_index)


def token_recurrence_budgets(loop_period: int, token_indices: Sequence[int]) -> tuple[int, ...]:
    """Return per-token recurrence budgets for token-level routing fixtures."""
    return tuple(token_recurrence_budget(loop_period, token_index) for token_index in token_indices)


def normalize_selected_loop_block(selected_loop_block: Optional[Sequence[int]]) -> tuple[int, int]:
    """Validate the selected middle-block range recorded by the fixture."""
    block = (2, 5) if selected_loop_block is None else tuple(selected_loop_block)
    if len(block) != 2:
        raise ValueError("selected_loop_block must contain start and stop indices")
    start, stop = int(block[0]), int(block[1])
    if start < 0:
        raise ValueError("selected_loop_block start must be nonnegative")
    if stop <= start:
        raise ValueError("selected_loop_block stop must be greater than start")
    return start, stop


def recurrence_resolution_levels(max_budget: int) -> tuple[str, ...]:
    """Return a deterministic coarse/fine resolution label for each loop step."""
    _require_positive(max_budget, "max_budget")
    return tuple("coarse" if step % 2 == 1 else "fine" for step in range(1, max_budget + 1))


def multi_resolution_required_resolutions(
    max_budget: int,
    required_budgets: Sequence[int],
) -> tuple[str, ...]:
    """Return the required coarse/fine label for each recurrence budget."""
    levels = recurrence_resolution_levels(max_budget)
    budgets = tuple(required_budgets)
    if not budgets:
        raise ValueError("required_budgets must be nonempty")
    for budget in budgets:
        _require_positive(budget, "required budget")
        if budget > max_budget:
            raise ValueError("required budget must be within max_budget")
    return tuple(levels[budget - 1] for budget in budgets)


def shifted_recurrence_resolutions(
    max_budget: int,
    required_budgets: Sequence[int],
    shift: int,
) -> tuple[str, ...]:
    """Return a deterministic wrong-resolution control by rotating labels."""
    if shift == 0:
        raise ValueError("shift must be nonzero")
    levels = recurrence_resolution_levels(max_budget)
    budgets = tuple(required_budgets)
    if not budgets:
        raise ValueError("required_budgets must be nonempty")
    for budget in budgets:
        _require_positive(budget, "required budget")
        if budget > max_budget:
            raise ValueError("required budget must be within max_budget")
    return tuple(levels[(budget - 1 + shift) % max_budget] for budget in budgets)


def active_token_counts_by_budget(token_budgets: Sequence[int], max_budget: int) -> tuple[int, ...]:
    """Count how many tokens are still active at each loop step."""
    _require_positive(max_budget, "max_budget")
    budgets = tuple(token_budgets)
    if not budgets:
        raise ValueError("token_budgets must be nonempty")
    for budget in budgets:
        _require_positive(budget, "token budget")
    return tuple(sum(1 for budget in budgets if budget >= step) for step in range(1, max_budget + 1))


def loop_block_indices(block_count: int, selected_loop_block: Optional[Sequence[int]] = None) -> tuple[int, ...]:
    """Return the model-block indices selected for a middle-block recurrence fixture."""
    _require_positive(block_count, "block_count")
    start, stop = normalize_selected_loop_block(selected_loop_block)
    if stop > block_count:
        raise ValueError("selected_loop_block stop must be within block_count")
    return tuple(range(start, stop))


def middle_block_required_blocks(
    block_count: int,
    selected_loop_block: Optional[Sequence[int]],
    sample_indices: Sequence[int],
) -> tuple[int, ...]:
    """Assign each sample a required block inside the selected recurrence range."""
    samples = tuple(sample_indices)
    if not samples:
        raise ValueError("sample_indices must be nonempty")
    selected = loop_block_indices(block_count, selected_loop_block)
    return tuple(selected[phase_channel(len(selected), sample)] for sample in samples)


def _recurrence_budget_predictions(
    required_budgets: Sequence[int],
    planned_budgets: Sequence[int],
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    required = tuple(required_budgets)
    planned = tuple(planned_budgets)
    if len(required) != len(planned):
        raise ValueError("required_budgets and planned_budgets must have the same length")
    if not required:
        raise ValueError("required_budgets must be nonempty")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    return tuple(
        loop_score_trace(required_budget, planned_budget, overthink_tolerance=overthink_tolerance)[-1]
        for required_budget, planned_budget in zip(required, planned)
    )


def _majority_int(values: Sequence[int]) -> int:
    value_tuple = tuple(values)
    if not value_tuple:
        raise ValueError("values must be nonempty")
    counts: dict[int, int] = {}
    for value in value_tuple:
        counts[value] = counts.get(value, 0) + 1
    return min(counts, key=lambda value: (-counts[value], value))


def _majority_str(values: Sequence[str]) -> str:
    value_tuple = tuple(values)
    if not value_tuple:
        raise ValueError("values must be nonempty")
    counts: dict[str, int] = {}
    for value in value_tuple:
        if not value:
            raise ValueError("values must be nonempty strings")
        counts[value] = counts.get(value, 0) + 1
    return min(counts, key=lambda value: (-counts[value], value))


def fit_loop_budget_lookup(
    period: int,
    positions: Sequence[int],
    budgets: Sequence[int],
) -> tuple[int, ...]:
    """Fit a deterministic phase-to-loop-budget table by majority vote."""
    _require_positive(period, "period")
    position_tuple = tuple(positions)
    budget_tuple = tuple(budgets)
    if len(position_tuple) != len(budget_tuple):
        raise ValueError("positions and budgets must have the same length")
    if not position_tuple:
        raise ValueError("positions must be nonempty")
    fallback = _majority_int(budget_tuple)
    buckets: list[list[int]] = [[] for _ in range(period)]
    for position, budget in zip(position_tuple, budget_tuple):
        _require_positive(budget, "budget")
        buckets[phase_channel(period, position)].append(budget)
    return tuple(fallback if not bucket else _majority_int(bucket) for bucket in buckets)


def fit_recurrence_resolution_lookup(
    period: int,
    positions: Sequence[int],
    resolutions: Sequence[str],
) -> tuple[str, ...]:
    """Fit a deterministic phase-to-resolution table by majority vote."""
    _require_positive(period, "period")
    position_tuple = tuple(positions)
    resolution_tuple = tuple(resolutions)
    if len(position_tuple) != len(resolution_tuple):
        raise ValueError("positions and resolutions must have the same length")
    if not position_tuple:
        raise ValueError("positions must be nonempty")
    fallback = _majority_str(resolution_tuple)
    buckets: list[list[str]] = [[] for _ in range(period)]
    for position, resolution in zip(position_tuple, resolution_tuple):
        if not resolution:
            raise ValueError("resolutions must be nonempty strings")
        buckets[phase_channel(period, position)].append(resolution)
    return tuple(fallback if not bucket else _majority_str(bucket) for bucket in buckets)


def fit_loop_block_lookup(
    period: int,
    positions: Sequence[int],
    blocks: Sequence[int],
) -> tuple[int, ...]:
    """Fit a deterministic phase-to-block table by majority vote."""
    _require_positive(period, "period")
    position_tuple = tuple(positions)
    block_tuple = tuple(blocks)
    if len(position_tuple) != len(block_tuple):
        raise ValueError("positions and blocks must have the same length")
    if not position_tuple:
        raise ValueError("positions must be nonempty")
    fallback = _majority_int(block_tuple)
    buckets: list[list[int]] = [[] for _ in range(period)]
    for position, block in zip(position_tuple, block_tuple):
        if block < 0:
            raise ValueError("blocks must be nonnegative")
        buckets[phase_channel(period, position)].append(block)
    return tuple(fallback if not bucket else _majority_int(bucket) for bucket in buckets)


def predict_loop_budget_lookup(
    period: int,
    lookup: Sequence[int],
    positions: Sequence[int],
) -> tuple[int, ...]:
    """Predict loop budgets from a fitted phase-to-budget lookup table."""
    _require_positive(period, "period")
    lookup_tuple = tuple(lookup)
    if len(lookup_tuple) != period:
        raise ValueError("lookup length must equal period")
    return tuple(lookup_tuple[phase_channel(period, position)] for position in positions)


def predict_recurrence_resolution_lookup(
    period: int,
    lookup: Sequence[str],
    positions: Sequence[int],
) -> tuple[str, ...]:
    """Predict resolution labels from a fitted phase-to-resolution table."""
    _require_positive(period, "period")
    lookup_tuple = tuple(lookup)
    if len(lookup_tuple) != period:
        raise ValueError("lookup length must equal period")
    for resolution in lookup_tuple:
        if not resolution:
            raise ValueError("lookup resolutions must be nonempty strings")
    return tuple(lookup_tuple[phase_channel(period, position)] for position in positions)


def predict_loop_block_lookup(
    period: int,
    lookup: Sequence[int],
    positions: Sequence[int],
) -> tuple[int, ...]:
    """Predict loop blocks from a fitted phase-to-block lookup table."""
    _require_positive(period, "period")
    lookup_tuple = tuple(lookup)
    if len(lookup_tuple) != period:
        raise ValueError("lookup length must equal period")
    for block in lookup_tuple:
        if block < 0:
            raise ValueError("lookup blocks must be nonnegative")
    return tuple(lookup_tuple[phase_channel(period, position)] for position in positions)


def _middle_block_predictions(
    required_blocks: Sequence[int],
    required_budgets: Sequence[int],
    candidate_blocks: Sequence[int],
    planned_budgets: Sequence[int],
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    required_block_tuple = tuple(required_blocks)
    required_budget_tuple = tuple(required_budgets)
    planned_budget_tuple = tuple(planned_budgets)
    if len(required_block_tuple) != len(required_budget_tuple):
        raise ValueError("required_blocks and required_budgets must have the same length")
    if len(required_block_tuple) != len(planned_budget_tuple):
        raise ValueError("required_blocks and planned_budgets must have the same length")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    candidates = set(candidate_blocks)
    if not candidates:
        raise ValueError("candidate_blocks must be nonempty")
    return tuple(
        1
        if required_block in candidates
        and required_budget <= planned_budget <= required_budget + overthink_tolerance
        else 0
        for required_block, required_budget, planned_budget in zip(
            required_block_tuple,
            required_budget_tuple,
            planned_budget_tuple,
        )
    )


def _sampled_middle_block_predictions(
    required_blocks: Sequence[int],
    required_budgets: Sequence[int],
    planned_blocks: Sequence[int],
    planned_budgets: Sequence[int],
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    required_block_tuple = tuple(required_blocks)
    required_budget_tuple = tuple(required_budgets)
    planned_block_tuple = tuple(planned_blocks)
    planned_budget_tuple = tuple(planned_budgets)
    if len(required_block_tuple) != len(required_budget_tuple):
        raise ValueError("required_blocks and required_budgets must have the same length")
    if len(required_block_tuple) != len(planned_block_tuple):
        raise ValueError("required_blocks and planned_blocks must have the same length")
    if len(required_block_tuple) != len(planned_budget_tuple):
        raise ValueError("required_blocks and planned_budgets must have the same length")
    if not required_block_tuple:
        raise ValueError("required_blocks must be nonempty")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    return tuple(
        1
        if required_block == planned_block
        and required_budget <= planned_budget <= required_budget + overthink_tolerance
        else 0
        for required_block, required_budget, planned_block, planned_budget in zip(
            required_block_tuple,
            required_budget_tuple,
            planned_block_tuple,
            planned_budget_tuple,
        )
    )


def _multi_resolution_predictions(
    required_budgets: Sequence[int],
    required_resolutions: Sequence[str],
    planned_budgets: Sequence[int],
    planned_resolutions: Sequence[str],
    *,
    overthink_tolerance: int,
) -> tuple[int, ...]:
    required_budget_tuple = tuple(required_budgets)
    required_resolution_tuple = tuple(required_resolutions)
    planned_budget_tuple = tuple(planned_budgets)
    planned_resolution_tuple = tuple(planned_resolutions)
    if len(required_budget_tuple) != len(required_resolution_tuple):
        raise ValueError("required_budgets and required_resolutions must have the same length")
    if len(required_budget_tuple) != len(planned_budget_tuple):
        raise ValueError("required_budgets and planned_budgets must have the same length")
    if len(required_budget_tuple) != len(planned_resolution_tuple):
        raise ValueError("required_budgets and planned_resolutions must have the same length")
    if not required_budget_tuple:
        raise ValueError("required_budgets must be nonempty")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")
    return tuple(
        1
        if required_resolution == planned_resolution
        and required_budget <= planned_budget <= required_budget + overthink_tolerance
        else 0
        for required_budget, required_resolution, planned_budget, planned_resolution in zip(
            required_budget_tuple,
            required_resolution_tuple,
            planned_budget_tuple,
            planned_resolution_tuple,
        )
    )


def run_token_level_recurrence_benchmark(
    *,
    loop_period: int = 4,
    token_count: int = 32,
    max_budget: int = 4,
    fixed_global_budget: int = 4,
    over_loop_budget: int = 8,
    wrong_budget_shift: int = 1,
    overthink_tolerance: int = 0,
    selected_loop_block: Optional[Sequence[int]] = None,
) -> TokenLevelRecurrenceBenchmarkResult:
    """Run a deterministic token-level recurrence routing fixture.

    This fixture records per-token recurrence budgets, active-token counts by
    loop step, a selected middle-block range, alternating coarse/fine
    resolution labels, and fixed/wrong/over-loop controls. It is schedule
    bookkeeping only, not evidence about learned recursive model quality.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(token_count, "token_count")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_global_budget, "fixed_global_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if wrong_budget_shift == 0:
        raise ValueError("wrong_budget_shift must be nonzero")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    tokens = tuple(range(token_count))
    token_budgets = token_recurrence_budgets(loop_period, tokens)
    positive_labels = tuple(1 for _ in tokens)
    routed_budgets = tuple(min(budget, max_budget) for budget in token_budgets)
    fixed_budgets = tuple(fixed_global_budget for _ in tokens)
    wrong_budgets = tuple(
        ((budget - 1 + wrong_budget_shift) % max_budget) + 1
        for budget in token_budgets
    )
    over_budgets = tuple(over_loop_budget for _ in tokens)

    token_level_predictions = _recurrence_budget_predictions(
        token_budgets,
        routed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _recurrence_budget_predictions(
        token_budgets,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_predictions = _recurrence_budget_predictions(
        token_budgets,
        wrong_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _recurrence_budget_predictions(
        token_budgets,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )

    control_threshold = (3 * token_count) // 4
    control_labels = tuple(nonperiodic_threshold_label(token, control_threshold) for token in tokens)
    control_loop_lookup = fit_phase_lookup(loop_period, tokens, control_labels)
    control_loop_predictions = predict_phase_lookup(loop_period, control_loop_lookup, tokens)
    control_threshold_fit, control_polarity = fit_threshold_classifier(tokens, control_labels)
    control_threshold_predictions = predict_threshold_classifier(
        tokens,
        control_threshold_fit,
        control_polarity,
    )
    active_counts = active_token_counts_by_budget(token_budgets, max_budget)

    return TokenLevelRecurrenceBenchmarkResult(
        loop_period=loop_period,
        token_count=token_count,
        max_budget=max_budget,
        fixed_global_budget=fixed_global_budget,
        over_loop_budget=over_loop_budget,
        wrong_budget_shift=wrong_budget_shift,
        overthink_tolerance=overthink_tolerance,
        selected_loop_block=normalize_selected_loop_block(selected_loop_block),
        resolution_levels=recurrence_resolution_levels(max_budget),
        token_budgets=token_budgets,
        active_token_counts=active_counts,
        token_level_accuracy=accuracy(token_level_predictions, positive_labels),
        fixed_global_budget_accuracy=accuracy(fixed_predictions, positive_labels),
        wrong_budget_accuracy=accuracy(wrong_predictions, positive_labels),
        over_looped_accuracy=accuracy(over_predictions, positive_labels),
        nonperiodic_token_level_accuracy=accuracy(control_loop_predictions, control_labels),
        nonperiodic_scalar_threshold_accuracy=accuracy(control_threshold_predictions, control_labels),
        average_active_tokens=sum(active_counts) / len(active_counts),
    )


def run_learned_token_level_recurrence_benchmark(
    *,
    loop_period: int = 4,
    wrong_period: int = 3,
    train_token_count: int = 64,
    test_token_count: int = 32,
    max_budget: int = 4,
    fixed_global_budget: int = 4,
    over_loop_budget: int = 8,
    wrong_budget_shift: int = 1,
    overthink_tolerance: int = 0,
) -> LearnedTokenLevelRecurrenceBenchmarkResult:
    """Run a learned token-level recurrence routing fixture.

    The fixture fits a phase-to-budget table on training tokens, applies that
    table to held-out tokens, and compares it with fixed, wrong-period,
    shifted-budget, over-loop, and nonperiodic scalar controls. It is routing
    bookkeeping only, not evidence about learned recursive transformer quality.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(wrong_period, "wrong_period")
    _require_positive(train_token_count, "train_token_count")
    _require_positive(test_token_count, "test_token_count")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_global_budget, "fixed_global_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if loop_period > max_budget:
        raise ValueError("loop_period must be no larger than max_budget")
    if wrong_period == loop_period:
        raise ValueError("wrong_period must differ from loop_period")
    if wrong_budget_shift == 0:
        raise ValueError("wrong_budget_shift must be nonzero")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    train_tokens = tuple(range(train_token_count))
    train_budgets = token_recurrence_budgets(loop_period, train_tokens)
    test_tokens = tuple(range(train_token_count, train_token_count + test_token_count))
    required_budgets = token_recurrence_budgets(loop_period, test_tokens)
    labels = tuple(1 for _ in test_tokens)

    learned_lookup = fit_loop_budget_lookup(loop_period, train_tokens, train_budgets)
    learned_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(loop_period, learned_lookup, test_tokens)
    )
    wrong_lookup = fit_loop_budget_lookup(wrong_period, train_tokens, train_budgets)
    wrong_period_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(wrong_period, wrong_lookup, test_tokens)
    )
    fixed_budgets = tuple(fixed_global_budget for _ in test_tokens)
    wrong_shift_budgets = tuple(
        ((budget - 1 + wrong_budget_shift) % max_budget) + 1
        for budget in required_budgets
    )
    over_budgets = tuple(over_loop_budget for _ in test_tokens)

    learned_predictions = _recurrence_budget_predictions(
        required_budgets,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _recurrence_budget_predictions(
        required_budgets,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_period_predictions = _recurrence_budget_predictions(
        required_budgets,
        wrong_period_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_shift_predictions = _recurrence_budget_predictions(
        required_budgets,
        wrong_shift_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _recurrence_budget_predictions(
        required_budgets,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )

    control_threshold = (3 * train_token_count) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(token, control_threshold)
        for token in train_tokens
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(token, control_threshold)
        for token in test_tokens
    )
    control_phase_lookup = fit_phase_lookup(loop_period, train_tokens, control_train_labels)
    control_phase_predictions = predict_phase_lookup(loop_period, control_phase_lookup, test_tokens)
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_tokens,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_tokens,
        control_threshold_fit,
        control_polarity,
    )
    active_counts = active_token_counts_by_budget(learned_budgets, max_budget)

    return LearnedTokenLevelRecurrenceBenchmarkResult(
        loop_period=loop_period,
        wrong_period=wrong_period,
        train_token_count=train_token_count,
        test_token_count=test_token_count,
        max_budget=max_budget,
        fixed_global_budget=fixed_global_budget,
        over_loop_budget=over_loop_budget,
        wrong_budget_shift=wrong_budget_shift,
        overthink_tolerance=overthink_tolerance,
        learned_budget_lookup=learned_lookup,
        wrong_period_budget_lookup=wrong_lookup,
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        learned_budget_sample=learned_budgets[: min(12, len(learned_budgets))],
        wrong_shift_budget_sample=wrong_shift_budgets[: min(12, len(wrong_shift_budgets))],
        active_token_counts=active_counts,
        learned_token_router_accuracy=accuracy(learned_predictions, labels),
        fixed_global_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_period_router_accuracy=accuracy(wrong_period_predictions, labels),
        wrong_shift_accuracy=accuracy(wrong_shift_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
        nonperiodic_phase_lookup_accuracy=accuracy(control_phase_predictions, control_test_labels),
        nonperiodic_scalar_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
        average_active_tokens=sum(active_counts) / len(active_counts),
    )


def run_middle_block_recurrence_benchmark(
    *,
    block_count: int = 8,
    sample_count: int = 32,
    loop_period: int = 4,
    selected_loop_block: Optional[Sequence[int]] = None,
    wrong_loop_block: Optional[Sequence[int]] = (0, 2),
    max_budget: int = 4,
    fixed_loop_budget: int = 4,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
) -> MiddleBlockRecurrenceBenchmarkResult:
    """Run a deterministic middle-block recurrence scheduling fixture.

    The positive fixture assigns every sample a required loop depth and a
    required model block inside the selected middle-block range. The selected
    route and a full-block route can both satisfy the constructed schedule;
    fixed-budget, wrong-block, and over-loop controls keep the claim bounded.
    This is recurrence bookkeeping only, not evidence about learned model
    quality or efficiency.
    """
    _require_positive(block_count, "block_count")
    _require_positive(sample_count, "sample_count")
    _require_positive(loop_period, "loop_period")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    selected_block = normalize_selected_loop_block(selected_loop_block)
    wrong_block = normalize_selected_loop_block(wrong_loop_block)
    selected_blocks = loop_block_indices(block_count, selected_block)
    wrong_blocks = loop_block_indices(block_count, wrong_block)
    full_blocks = tuple(range(block_count))
    samples = tuple(range(sample_count))
    required_blocks = middle_block_required_blocks(block_count, selected_block, samples)
    required_budgets = token_recurrence_budgets(loop_period, samples)
    phase_budgets = tuple(min(budget, max_budget) for budget in required_budgets)
    fixed_budgets = tuple(fixed_loop_budget for _ in samples)
    over_budgets = tuple(over_loop_budget for _ in samples)
    labels = tuple(1 for _ in samples)

    selected_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        selected_blocks,
        phase_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    full_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        full_blocks,
        phase_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        selected_blocks,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        wrong_blocks,
        phase_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        selected_blocks,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )

    average_phase_budget = sum(phase_budgets) / len(phase_budgets)
    return MiddleBlockRecurrenceBenchmarkResult(
        block_count=block_count,
        sample_count=sample_count,
        loop_period=loop_period,
        selected_loop_block=selected_block,
        wrong_loop_block=wrong_block,
        max_budget=max_budget,
        fixed_loop_budget=fixed_loop_budget,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        selected_block_indices=selected_blocks,
        required_block_sample=required_blocks[: min(12, len(required_blocks))],
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        selected_middle_block_accuracy=accuracy(selected_predictions, labels),
        full_block_phase_budget_accuracy=accuracy(full_predictions, labels),
        fixed_loop_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_block_accuracy=accuracy(wrong_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
        average_selected_block_passes=average_phase_budget * len(selected_blocks),
        average_full_block_passes=average_phase_budget * len(full_blocks),
    )


def run_learned_middle_block_recurrence_benchmark(
    *,
    block_count: int = 8,
    train_length: int = 64,
    test_length: int = 32,
    loop_period: int = 4,
    wrong_block_period: int = 2,
    wrong_budget_period: int = 3,
    selected_loop_block: Optional[Sequence[int]] = None,
    wrong_loop_block: Optional[Sequence[int]] = (0, 2),
    max_budget: int = 4,
    fixed_loop_budget: int = 4,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
) -> LearnedMiddleBlockRecurrenceBenchmarkResult:
    """Run a learned middle-block recurrence routing fixture.

    The fixture fits one phase table for the required loop block and another
    phase table for the required recurrence budget, then evaluates held-out
    samples against block-period, budget-period, fixed-budget, wrong-band,
    selected-band, full-block, and over-loop controls. It is routing
    bookkeeping only, not evidence about learned recursive transformer quality.
    """
    _require_positive(block_count, "block_count")
    _require_positive(train_length, "train_length")
    _require_positive(test_length, "test_length")
    _require_positive(loop_period, "loop_period")
    _require_positive(wrong_block_period, "wrong_block_period")
    _require_positive(wrong_budget_period, "wrong_budget_period")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if loop_period > max_budget:
        raise ValueError("loop_period must be no larger than max_budget")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    selected_block = normalize_selected_loop_block(selected_loop_block)
    wrong_block = normalize_selected_loop_block(wrong_loop_block)
    selected_blocks = loop_block_indices(block_count, selected_block)
    wrong_blocks = loop_block_indices(block_count, wrong_block)
    block_period = len(selected_blocks)
    if wrong_block_period == block_period:
        raise ValueError("wrong_block_period must differ from the selected block period")
    if wrong_budget_period == loop_period:
        raise ValueError("wrong_budget_period must differ from loop_period")

    train_samples = tuple(range(train_length))
    train_required_blocks = middle_block_required_blocks(block_count, selected_block, train_samples)
    train_required_budgets = token_recurrence_budgets(loop_period, train_samples)
    test_samples = tuple(range(train_length, train_length + test_length))
    required_blocks = middle_block_required_blocks(block_count, selected_block, test_samples)
    required_budgets = token_recurrence_budgets(loop_period, test_samples)
    labels = tuple(1 for _ in test_samples)

    learned_block_lookup = fit_loop_block_lookup(block_period, train_samples, train_required_blocks)
    learned_blocks = predict_loop_block_lookup(block_period, learned_block_lookup, test_samples)
    learned_budget_lookup = fit_loop_budget_lookup(loop_period, train_samples, train_required_budgets)
    learned_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(loop_period, learned_budget_lookup, test_samples)
    )
    wrong_block_lookup = fit_loop_block_lookup(wrong_block_period, train_samples, train_required_blocks)
    wrong_period_blocks = predict_loop_block_lookup(wrong_block_period, wrong_block_lookup, test_samples)
    wrong_budget_lookup = fit_loop_budget_lookup(wrong_budget_period, train_samples, train_required_budgets)
    wrong_period_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(wrong_budget_period, wrong_budget_lookup, test_samples)
    )
    fixed_budgets = tuple(fixed_loop_budget for _ in test_samples)
    over_budgets = tuple(over_loop_budget for _ in test_samples)
    full_blocks = tuple(range(block_count))

    learned_predictions = _sampled_middle_block_predictions(
        required_blocks,
        required_budgets,
        learned_blocks,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    selected_band_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        selected_blocks,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    full_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        full_blocks,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _sampled_middle_block_predictions(
        required_blocks,
        required_budgets,
        learned_blocks,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_block_period_predictions = _sampled_middle_block_predictions(
        required_blocks,
        required_budgets,
        wrong_period_blocks,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_budget_period_predictions = _sampled_middle_block_predictions(
        required_blocks,
        required_budgets,
        learned_blocks,
        wrong_period_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_loop_block_predictions = _middle_block_predictions(
        required_blocks,
        required_budgets,
        wrong_blocks,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _sampled_middle_block_predictions(
        required_blocks,
        required_budgets,
        learned_blocks,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    active_counts = active_token_counts_by_budget(learned_budgets, max_budget)
    average_budget = sum(learned_budgets) / len(learned_budgets)

    return LearnedMiddleBlockRecurrenceBenchmarkResult(
        block_count=block_count,
        train_length=train_length,
        test_length=test_length,
        loop_period=loop_period,
        block_period=block_period,
        wrong_block_period=wrong_block_period,
        wrong_budget_period=wrong_budget_period,
        selected_loop_block=selected_block,
        wrong_loop_block=wrong_block,
        selected_block_indices=selected_blocks,
        max_budget=max_budget,
        fixed_loop_budget=fixed_loop_budget,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        learned_block_lookup=learned_block_lookup,
        learned_budget_lookup=learned_budget_lookup,
        wrong_block_period_lookup=wrong_block_lookup,
        wrong_budget_period_lookup=wrong_budget_lookup,
        required_block_sample=required_blocks[: min(12, len(required_blocks))],
        learned_block_sample=learned_blocks[: min(12, len(learned_blocks))],
        wrong_block_sample=wrong_period_blocks[: min(12, len(wrong_period_blocks))],
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        learned_budget_sample=learned_budgets[: min(12, len(learned_budgets))],
        wrong_budget_sample=wrong_period_budgets[: min(12, len(wrong_period_budgets))],
        active_sample_counts=active_counts,
        learned_middle_block_router_accuracy=accuracy(learned_predictions, labels),
        selected_band_phase_budget_accuracy=accuracy(selected_band_predictions, labels),
        full_block_phase_budget_accuracy=accuracy(full_predictions, labels),
        fixed_loop_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_block_period_accuracy=accuracy(wrong_block_period_predictions, labels),
        wrong_budget_period_accuracy=accuracy(wrong_budget_period_predictions, labels),
        wrong_loop_block_accuracy=accuracy(wrong_loop_block_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
        average_learned_block_passes=average_budget,
        average_selected_band_passes=average_budget * len(selected_blocks),
        average_full_block_passes=average_budget * len(full_blocks),
    )


def run_multi_resolution_recurrence_benchmark(
    *,
    loop_period: int = 4,
    sample_count: int = 32,
    max_budget: int = 4,
    fixed_loop_budget: int = 4,
    wrong_resolution_shift: int = 1,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
) -> MultiResolutionRecurrenceBenchmarkResult:
    """Run a deterministic multi-resolution recurrence routing fixture.

    The positive route chooses the required loop budget and the required
    coarse/fine resolution label for each sample. Single-resolution,
    fixed-budget, wrong-resolution, and over-loop controls keep the result as
    schedule bookkeeping only, not evidence about learned model quality.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(sample_count, "sample_count")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if loop_period > max_budget:
        raise ValueError("loop_period must be no larger than max_budget")
    if wrong_resolution_shift == 0:
        raise ValueError("wrong_resolution_shift must be nonzero")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    samples = tuple(range(sample_count))
    required_budgets = token_recurrence_budgets(loop_period, samples)
    required_resolutions = multi_resolution_required_resolutions(max_budget, required_budgets)
    labels = tuple(1 for _ in samples)
    routed_budgets = tuple(min(budget, max_budget) for budget in required_budgets)
    fixed_budgets = tuple(fixed_loop_budget for _ in samples)
    over_budgets = tuple(over_loop_budget for _ in samples)
    coarse_resolutions = tuple("coarse" for _ in samples)
    fine_resolutions = tuple("fine" for _ in samples)
    wrong_resolutions = shifted_recurrence_resolutions(
        max_budget,
        required_budgets,
        wrong_resolution_shift,
    )

    multi_resolution_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        routed_budgets,
        required_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    coarse_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        routed_budgets,
        coarse_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    fine_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        routed_budgets,
        fine_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        fixed_budgets,
        required_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        routed_budgets,
        wrong_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        over_budgets,
        required_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    active_counts = active_token_counts_by_budget(required_budgets, max_budget)

    return MultiResolutionRecurrenceBenchmarkResult(
        loop_period=loop_period,
        sample_count=sample_count,
        max_budget=max_budget,
        fixed_loop_budget=fixed_loop_budget,
        wrong_resolution_shift=wrong_resolution_shift,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        resolution_levels=recurrence_resolution_levels(max_budget),
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        required_resolution_sample=required_resolutions[: min(12, len(required_resolutions))],
        active_sample_counts=active_counts,
        multi_resolution_accuracy=accuracy(multi_resolution_predictions, labels),
        single_resolution_coarse_accuracy=accuracy(coarse_predictions, labels),
        single_resolution_fine_accuracy=accuracy(fine_predictions, labels),
        fixed_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_resolution_accuracy=accuracy(wrong_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
        average_active_samples=sum(active_counts) / len(active_counts),
    )


def run_learned_multi_resolution_recurrence_benchmark(
    *,
    loop_period: int = 4,
    wrong_budget_period: int = 3,
    wrong_resolution_period: int = 3,
    train_length: int = 64,
    test_length: int = 32,
    max_budget: int = 4,
    fixed_loop_budget: int = 4,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
) -> LearnedMultiResolutionRecurrenceBenchmarkResult:
    """Run a learned multi-resolution recurrence routing fixture.

    The fixture fits one phase table for loop budget and one phase table for
    coarse/fine resolution labels, applies both to held-out samples, and
    compares the learned route with single-resolution, fixed-budget,
    wrong-period, and over-loop controls. It is schedule bookkeeping only, not
    evidence about learned recursive transformer quality.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(wrong_budget_period, "wrong_budget_period")
    _require_positive(wrong_resolution_period, "wrong_resolution_period")
    _require_positive(train_length, "train_length")
    _require_positive(test_length, "test_length")
    _require_positive(max_budget, "max_budget")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if loop_period > max_budget:
        raise ValueError("loop_period must be no larger than max_budget")
    if wrong_budget_period == loop_period:
        raise ValueError("wrong_budget_period must differ from loop_period")
    if wrong_resolution_period == loop_period:
        raise ValueError("wrong_resolution_period must differ from loop_period")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    train_samples = tuple(range(train_length))
    train_budgets = token_recurrence_budgets(loop_period, train_samples)
    train_resolutions = multi_resolution_required_resolutions(max_budget, train_budgets)
    test_samples = tuple(range(train_length, train_length + test_length))
    required_budgets = token_recurrence_budgets(loop_period, test_samples)
    required_resolutions = multi_resolution_required_resolutions(max_budget, required_budgets)
    labels = tuple(1 for _ in test_samples)

    learned_budget_lookup = fit_loop_budget_lookup(loop_period, train_samples, train_budgets)
    learned_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(loop_period, learned_budget_lookup, test_samples)
    )
    learned_resolution_lookup = fit_recurrence_resolution_lookup(
        loop_period,
        train_samples,
        train_resolutions,
    )
    learned_resolutions = predict_recurrence_resolution_lookup(
        loop_period,
        learned_resolution_lookup,
        test_samples,
    )
    wrong_budget_lookup = fit_loop_budget_lookup(wrong_budget_period, train_samples, train_budgets)
    wrong_budgets = tuple(
        min(budget, max_budget)
        for budget in predict_loop_budget_lookup(wrong_budget_period, wrong_budget_lookup, test_samples)
    )
    wrong_resolution_lookup = fit_recurrence_resolution_lookup(
        wrong_resolution_period,
        train_samples,
        train_resolutions,
    )
    wrong_resolutions = predict_recurrence_resolution_lookup(
        wrong_resolution_period,
        wrong_resolution_lookup,
        test_samples,
    )
    fixed_budgets = tuple(fixed_loop_budget for _ in test_samples)
    over_budgets = tuple(over_loop_budget for _ in test_samples)
    coarse_resolutions = tuple("coarse" for _ in test_samples)
    fine_resolutions = tuple("fine" for _ in test_samples)

    learned_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        learned_budgets,
        learned_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    coarse_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        learned_budgets,
        coarse_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    fine_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        learned_budgets,
        fine_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        fixed_budgets,
        learned_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_budget_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        wrong_budgets,
        learned_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_resolution_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        learned_budgets,
        wrong_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _multi_resolution_predictions(
        required_budgets,
        required_resolutions,
        over_budgets,
        learned_resolutions,
        overthink_tolerance=overthink_tolerance,
    )
    active_counts = active_token_counts_by_budget(learned_budgets, max_budget)

    return LearnedMultiResolutionRecurrenceBenchmarkResult(
        loop_period=loop_period,
        wrong_budget_period=wrong_budget_period,
        wrong_resolution_period=wrong_resolution_period,
        train_length=train_length,
        test_length=test_length,
        max_budget=max_budget,
        fixed_loop_budget=fixed_loop_budget,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        resolution_levels=recurrence_resolution_levels(max_budget),
        learned_budget_lookup=learned_budget_lookup,
        learned_resolution_lookup=learned_resolution_lookup,
        wrong_budget_period_lookup=wrong_budget_lookup,
        wrong_resolution_period_lookup=wrong_resolution_lookup,
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        learned_budget_sample=learned_budgets[: min(12, len(learned_budgets))],
        wrong_budget_sample=wrong_budgets[: min(12, len(wrong_budgets))],
        required_resolution_sample=required_resolutions[: min(12, len(required_resolutions))],
        learned_resolution_sample=learned_resolutions[: min(12, len(learned_resolutions))],
        wrong_resolution_sample=wrong_resolutions[: min(12, len(wrong_resolutions))],
        active_sample_counts=active_counts,
        learned_multi_resolution_router_accuracy=accuracy(learned_predictions, labels),
        single_resolution_coarse_accuracy=accuracy(coarse_predictions, labels),
        single_resolution_fine_accuracy=accuracy(fine_predictions, labels),
        fixed_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_budget_period_accuracy=accuracy(wrong_budget_predictions, labels),
        wrong_resolution_period_accuracy=accuracy(wrong_resolution_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
        average_active_samples=sum(active_counts) / len(active_counts),
    )


def run_learned_recurrence_schedule_benchmark(
    *,
    loop_period: int = 4,
    wrong_period: int = 3,
    train_length: int = 64,
    test_length: int = 32,
    fixed_loop_budget: int = 4,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
) -> LearnedRecurrenceScheduleBenchmarkResult:
    """Run a deterministic learned phase-to-recurrence-budget fixture.

    The positive fixture fits a tiny phase lookup table from training examples
    whose labels are required loop depths. Wrong-period, fixed-budget, and
    over-loop controls keep this as schedule-learning bookkeeping only.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(wrong_period, "wrong_period")
    _require_positive(train_length, "train_length")
    _require_positive(test_length, "test_length")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(over_loop_budget, "over_loop_budget")
    if wrong_period == loop_period:
        raise ValueError("wrong_period must differ from loop_period")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    train_positions = tuple(range(train_length))
    train_budgets = token_recurrence_budgets(loop_period, train_positions)
    test_positions = tuple(range(train_length, train_length + test_length))
    required_budgets = token_recurrence_budgets(loop_period, test_positions)
    labels = tuple(1 for _ in test_positions)

    learned_lookup = fit_loop_budget_lookup(loop_period, train_positions, train_budgets)
    learned_budgets = predict_loop_budget_lookup(loop_period, learned_lookup, test_positions)
    wrong_lookup = fit_loop_budget_lookup(wrong_period, train_positions, train_budgets)
    wrong_budgets = predict_loop_budget_lookup(wrong_period, wrong_lookup, test_positions)
    fixed_budgets = tuple(fixed_loop_budget for _ in test_positions)
    over_budgets = tuple(over_loop_budget for _ in test_positions)

    learned_predictions = _recurrence_budget_predictions(
        required_budgets,
        learned_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _recurrence_budget_predictions(
        required_budgets,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_predictions = _recurrence_budget_predictions(
        required_budgets,
        wrong_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _recurrence_budget_predictions(
        required_budgets,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )

    return LearnedRecurrenceScheduleBenchmarkResult(
        loop_period=loop_period,
        wrong_period=wrong_period,
        train_length=train_length,
        test_length=test_length,
        fixed_loop_budget=fixed_loop_budget,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        learned_budget_lookup=learned_lookup,
        wrong_period_budget_lookup=wrong_lookup,
        required_budget_sample=required_budgets[: min(12, len(required_budgets))],
        learned_budget_sample=learned_budgets[: min(12, len(learned_budgets))],
        learned_phase_router_accuracy=accuracy(learned_predictions, labels),
        fixed_loop_budget_accuracy=accuracy(fixed_predictions, labels),
        wrong_period_router_accuracy=accuracy(wrong_predictions, labels),
        over_looped_accuracy=accuracy(over_predictions, labels),
    )


def training_free_loop_budget(loop_period: int, sample_index: int, max_loops: int) -> int:
    """Return a phase-prior loop budget for a training-free wrapper fixture."""
    _require_positive(max_loops, "max_loops")
    return min(loop_required_steps(loop_period, sample_index), max_loops)


def training_free_loop_budgets(
    loop_period: int,
    sample_indices: Sequence[int],
    max_loops: int,
) -> tuple[int, ...]:
    """Return phase-prior budgets for a batch of samples."""
    samples = tuple(sample_indices)
    if not samples:
        raise ValueError("sample_indices must be nonempty")
    return tuple(training_free_loop_budget(loop_period, sample, max_loops) for sample in samples)


def _backend_accuracy(predictions: Sequence[int], labels: Sequence[int], backend: str) -> float:
    if backend == "cpu":
        return accuracy(predictions, labels)
    if backend == "mlx":
        return _mlx_accuracy(predictions, labels)
    raise ValueError("backend must be 'cpu' or 'mlx'")


def _budget_is_full_depth_predictions(
    planned_budgets: Sequence[int],
    max_loops: int,
) -> tuple[int, ...]:
    _require_positive(max_loops, "max_loops")
    return tuple(1 if budget >= max_loops else 0 for budget in planned_budgets)


def _budget_histogram(planned_budgets: Sequence[int]) -> tuple[tuple[int, int], ...]:
    budgets = tuple(planned_budgets)
    if not budgets:
        raise ValueError("planned_budgets must be nonempty")
    return tuple((budget, budgets.count(budget)) for budget in sorted(set(budgets)))


def run_training_free_loop_wrapper_benchmark(
    *,
    loop_period: int = 4,
    sample_count: int = 32,
    max_loops: int = 4,
    fixed_loop_budget: int = 2,
    wrong_loop_period: int = 3,
    over_loop_budget: int = 8,
    overthink_tolerance: int = 0,
    backend: str = "cpu",
) -> TrainingFreeLoopWrapperBenchmarkResult:
    """Run a deterministic training-free loop-wrapper fixture.

    The wrapper uses the known circular phase as a fixed prior for how many
    loop passes to run. It compares single-pass, fixed-budget, wrong-period,
    and over-loop controls, plus a nonperiodic scalar-threshold control. This
    is schedule bookkeeping only, not evidence about learned model quality.
    """
    _require_positive(loop_period, "loop_period")
    _require_positive(sample_count, "sample_count")
    _require_positive(max_loops, "max_loops")
    _require_positive(fixed_loop_budget, "fixed_loop_budget")
    _require_positive(wrong_loop_period, "wrong_loop_period")
    _require_positive(over_loop_budget, "over_loop_budget")
    if wrong_loop_period == loop_period:
        raise ValueError("wrong_loop_period must differ from loop_period")
    if overthink_tolerance < 0:
        raise ValueError("overthink_tolerance must be nonnegative")

    samples = tuple(range(sample_count))
    required_budgets = token_recurrence_budgets(loop_period, samples)
    positive_labels = tuple(1 for _ in samples)
    phase_budgets = training_free_loop_budgets(loop_period, samples, max_loops)
    single_pass_budgets = tuple(1 for _ in samples)
    fixed_budgets = tuple(fixed_loop_budget for _ in samples)
    wrong_period_budgets = training_free_loop_budgets(wrong_loop_period, samples, max_loops)
    over_budgets = tuple(over_loop_budget for _ in samples)

    single_pass_predictions = _recurrence_budget_predictions(
        required_budgets,
        single_pass_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    fixed_predictions = _recurrence_budget_predictions(
        required_budgets,
        fixed_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    phase_predictions = _recurrence_budget_predictions(
        required_budgets,
        phase_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    wrong_predictions = _recurrence_budget_predictions(
        required_budgets,
        wrong_period_budgets,
        overthink_tolerance=overthink_tolerance,
    )
    over_predictions = _recurrence_budget_predictions(
        required_budgets,
        over_budgets,
        overthink_tolerance=overthink_tolerance,
    )

    control_threshold = (3 * sample_count) // 4
    control_labels = tuple(nonperiodic_threshold_label(sample, control_threshold) for sample in samples)
    control_phase_predictions = _budget_is_full_depth_predictions(phase_budgets, max_loops)
    threshold_fit, threshold_polarity = fit_threshold_classifier(samples, control_labels)
    control_threshold_predictions = predict_threshold_classifier(
        samples,
        threshold_fit,
        threshold_polarity,
    )
    active_counts = active_token_counts_by_budget(phase_budgets, max_loops)

    return TrainingFreeLoopWrapperBenchmarkResult(
        loop_period=loop_period,
        sample_count=sample_count,
        max_loops=max_loops,
        fixed_loop_budget=fixed_loop_budget,
        wrong_loop_period=wrong_loop_period,
        over_loop_budget=over_loop_budget,
        overthink_tolerance=overthink_tolerance,
        backend=backend,
        phase_budgets=phase_budgets,
        active_sample_counts=active_counts,
        budget_histogram=_budget_histogram(phase_budgets),
        average_phase_budget=sum(phase_budgets) / len(phase_budgets),
        single_pass_accuracy=_backend_accuracy(single_pass_predictions, positive_labels, backend),
        fixed_loop_accuracy=_backend_accuracy(fixed_predictions, positive_labels, backend),
        training_free_phase_budget_accuracy=_backend_accuracy(phase_predictions, positive_labels, backend),
        wrong_period_budget_accuracy=_backend_accuracy(wrong_predictions, positive_labels, backend),
        over_loop_no_exit_accuracy=_backend_accuracy(over_predictions, positive_labels, backend),
        nonperiodic_phase_budget_accuracy=_backend_accuracy(control_phase_predictions, control_labels, backend),
        nonperiodic_scalar_threshold_accuracy=_backend_accuracy(
            control_threshold_predictions,
            control_labels,
            backend,
        ),
    )


def default_adapter_block_values(block_size: int) -> tuple[int, ...]:
    """Choose a deterministic nontrivial binary value for each adapter block."""
    _require_positive(block_size, "block_size")
    values = tuple(1 if block % 3 == 1 else 0 for block in range(block_size))
    if not any(values) or all(values):
        raise ValueError("block_size must produce both positive and negative block values")
    return values


def normalize_adapter_block_values(
    block_size: int,
    block_values: Optional[Sequence[int]],
) -> tuple[int, ...]:
    """Validate or create a binary value table indexed by adapter block."""
    _require_positive(block_size, "block_size")
    values = default_adapter_block_values(block_size) if block_values is None else tuple(block_values)
    if len(values) != block_size:
        raise ValueError("block_values length must equal block_size")
    if any(value not in (0, 1) for value in values):
        raise ValueError("block_values must be binary")
    if not any(values):
        raise ValueError("block_values must contain at least one positive block")
    if all(values):
        raise ValueError("block_values must contain at least one negative block")
    return values


def synthetic_adapter_block_dataset(
    block_size: int,
    length: int,
    *,
    start: int = 0,
    block_values: Optional[Sequence[int]] = None,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return channels and binary labels controlled only by adapter block."""
    if length <= 0:
        raise ValueError("length must be positive")
    values = normalize_adapter_block_values(block_size, block_values)
    channels = tuple(range(start, start + length))
    labels = tuple(values[adapter_block(block_size, channel)] for channel in channels)
    return channels, labels


def fit_adapter_block_lookup(
    block_size: int,
    channels: Sequence[int],
    labels: Sequence[int],
) -> tuple[int, ...]:
    """Fit an adapter-block lookup table by majority label for each block."""
    _require_positive(block_size, "block_size")
    if len(channels) != len(labels):
        raise ValueError("channels and labels must have the same length")
    if not channels:
        raise ValueError("channels must be nonempty")
    fallback = majority_label(labels)
    counts = [[0, 0] for _ in range(block_size)]
    for channel, label in zip(channels, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        counts[adapter_block(block_size, channel)][label] += 1
    return tuple(
        fallback if zero_count + one_count == 0 else (1 if one_count >= zero_count else 0)
        for zero_count, one_count in counts
    )


def predict_adapter_block_lookup(
    block_size: int,
    lookup: Sequence[int],
    channels: Sequence[int],
) -> tuple[int, ...]:
    """Predict labels from a fitted adapter-block lookup table."""
    _require_positive(block_size, "block_size")
    if len(lookup) != block_size:
        raise ValueError("lookup length must equal block_size")
    return tuple(lookup[adapter_block(block_size, channel)] for channel in channels)


def adapter_block_loads(block_size: int, channels: Sequence[int]) -> tuple[int, ...]:
    """Return how many channels land in each adapter block."""
    _require_positive(block_size, "block_size")
    loads = [0 for _ in range(block_size)]
    for channel in channels:
        loads[adapter_block(block_size, channel)] += 1
    return tuple(loads)


def adapter_block_collision_count(block_size: int, channels: Sequence[int]) -> int:
    """Count extra channels beyond the first occupant of each used block."""
    loads = adapter_block_loads(block_size, channels)
    return sum(max(0, load - 1) for load in loads)


def run_adapter_block_benchmark(
    *,
    block_size: int = 8,
    train_channels: int = 64,
    test_channels: int = 32,
    block_values: Optional[Sequence[int]] = None,
) -> AdapterBlockBenchmarkResult:
    """Run a deterministic adapter-block fixture with baselines and a control.

    The positive fixture labels channels by their adapter block. The negative
    control labels channels by a scalar threshold, where block lookup should
    not be the winning representation. This is a benchmark harness sanity
    check, not evidence that CoilRA improves neural networks.
    """
    values = normalize_adapter_block_values(block_size, block_values)
    train_channel_ids, train_labels = synthetic_adapter_block_dataset(
        block_size,
        train_channels,
        block_values=values,
    )
    test_channel_ids, test_labels = synthetic_adapter_block_dataset(
        block_size,
        test_channels,
        start=train_channels,
        block_values=values,
    )

    lookup = fit_adapter_block_lookup(block_size, train_channel_ids, train_labels)
    adapter_predictions = predict_adapter_block_lookup(block_size, lookup, test_channel_ids)
    threshold, polarity = fit_threshold_classifier(train_channel_ids, train_labels)
    threshold_predictions = predict_threshold_classifier(test_channel_ids, threshold, polarity)
    constant = majority_label(train_labels)
    constant_predictions = tuple(constant for _ in test_channel_ids)

    control_threshold = (3 * train_channels) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(channel, control_threshold)
        for channel in train_channel_ids
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(channel, control_threshold)
        for channel in test_channel_ids
    )
    control_lookup = fit_adapter_block_lookup(block_size, train_channel_ids, control_train_labels)
    control_adapter_predictions = predict_adapter_block_lookup(
        block_size,
        control_lookup,
        test_channel_ids,
    )
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_channel_ids,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_channel_ids,
        control_threshold_fit,
        control_polarity,
    )
    train_loads = adapter_block_loads(block_size, train_channel_ids)

    return AdapterBlockBenchmarkResult(
        block_size=block_size,
        train_channels=train_channels,
        test_channels=test_channels,
        block_values=values,
        adapter_block_accuracy=accuracy(adapter_predictions, test_labels),
        scalar_channel_threshold_accuracy=accuracy(threshold_predictions, test_labels),
        constant_accuracy=accuracy(constant_predictions, test_labels),
        nonperiodic_adapter_block_accuracy=accuracy(control_adapter_predictions, control_test_labels),
        nonperiodic_scalar_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
        train_collision_count=adapter_block_collision_count(block_size, train_channel_ids),
        max_train_block_load=max(train_loads),
    )


def dense_adapter_parameter_count(channel_count: int, parameters_per_channel: int) -> int:
    """Return a dense per-channel adapter parameter count."""
    _require_positive(channel_count, "channel_count")
    _require_positive(parameters_per_channel, "parameters_per_channel")
    return channel_count * parameters_per_channel


def lora_adapter_parameter_count(channel_count: int, parameters_per_channel: int, rank: int) -> int:
    """Return a LoRA-style low-rank adapter parameter count."""
    _require_positive(channel_count, "channel_count")
    _require_positive(parameters_per_channel, "parameters_per_channel")
    _require_positive(rank, "rank")
    return rank * (channel_count + parameters_per_channel)


def block_cyclic_adapter_parameter_count(block_size: int, parameters_per_block: int) -> int:
    """Return a block-cyclic shared-table parameter count."""
    _require_positive(block_size, "block_size")
    _require_positive(parameters_per_block, "parameters_per_block")
    return block_size * parameters_per_block


def run_adapter_parameter_budget_benchmark(
    *,
    channel_count: int = 128,
    block_size: int = 8,
    rank: int = 4,
    parameters_per_channel: int = 16,
) -> AdapterParameterBudgetResult:
    """Compare adapter parameter budgets against ordinary baselines.

    This fixture counts parameters only. It compares a dense per-channel
    adapter, a LoRA-style low-rank baseline, and a block-cyclic table shared
    by ``channel mod block_size``. It does not measure model quality, runtime,
    training stability, or hardware efficiency.
    """
    _require_positive(channel_count, "channel_count")
    _require_positive(block_size, "block_size")
    _require_positive(rank, "rank")
    _require_positive(parameters_per_channel, "parameters_per_channel")

    channels = tuple(range(channel_count))
    dense_count = dense_adapter_parameter_count(channel_count, parameters_per_channel)
    lora_count = lora_adapter_parameter_count(channel_count, parameters_per_channel, rank)
    block_count = block_cyclic_adapter_parameter_count(block_size, parameters_per_channel)
    block_loads = adapter_block_loads(block_size, channels)

    return AdapterParameterBudgetResult(
        channel_count=channel_count,
        block_size=block_size,
        rank=rank,
        parameters_per_channel=parameters_per_channel,
        dense_adapter_parameters=dense_count,
        lora_parameters=lora_count,
        block_cyclic_parameters=block_count,
        lora_to_dense_ratio=lora_count / dense_count,
        block_to_dense_ratio=block_count / dense_count,
        channel_collision_count=adapter_block_collision_count(block_size, channels),
        max_block_load=max(block_loads),
    )


def default_circulant_input(period: int) -> tuple[int, ...]:
    """Return a deterministic input vector for circulant mixer fixtures."""
    _require_positive(period, "period")
    return tuple(((index * index + 3 * index + 1) % 7) - 3 for index in range(period))


def default_circulant_kernel(period: int) -> tuple[int, ...]:
    """Return a deterministic sparse kernel for circular convolution."""
    _require_positive(period, "period")
    kernel = [0 for _ in range(period)]
    kernel[0] = 2
    if period > 1:
        kernel[1] = -1
    if period > 2:
        kernel[2] = 1
    if period > 4:
        kernel[4] = -2
    return tuple(kernel)


def normalize_circulant_vector(values: Optional[Sequence[int]], period: int, name: str) -> tuple[int, ...]:
    """Validate or create an integer vector of length ``period``."""
    _require_positive(period, "period")
    vector = default_circulant_input(period) if values is None and name == "input_values" else values
    if vector is None:
        vector = default_circulant_kernel(period)
    normalized = tuple(int(value) for value in vector)
    if len(normalized) != period:
        raise ValueError(f"{name} length must equal period")
    return normalized


def circulant_mixer_output(input_values: Sequence[int], kernel_values: Sequence[int]) -> tuple[int, ...]:
    """Apply a circular convolution mixer to an input vector."""
    values = tuple(input_values)
    kernel = tuple(kernel_values)
    if len(values) != len(kernel):
        raise ValueError("input_values and kernel_values must have the same length")
    period = len(values)
    _require_positive(period, "period")
    return tuple(
        sum(kernel[offset] * values[(index - offset) % period] for offset in range(period))
        for index in range(period)
    )


def dense_circulant_matrix(kernel_values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Return the dense matrix equivalent of a circular convolution kernel."""
    kernel = tuple(kernel_values)
    period = len(kernel)
    _require_positive(period, "period")
    return tuple(
        tuple(kernel[(row - column) % period] for column in range(period))
        for row in range(period)
    )


def dense_matrix_vector_product(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> tuple[int, ...]:
    """Apply an integer dense matrix to an integer vector."""
    rows = tuple(tuple(row) for row in matrix)
    values = tuple(vector)
    if not rows:
        raise ValueError("matrix must be nonempty")
    if any(len(row) != len(values) for row in rows):
        raise ValueError("each matrix row length must equal vector length")
    return tuple(sum(entry * value for entry, value in zip(row, values)) for row in rows)


def rotate_kernel(kernel_values: Sequence[int], shift: int) -> tuple[int, ...]:
    """Rotate a circulant kernel by a fixed offset."""
    kernel = tuple(kernel_values)
    period = len(kernel)
    _require_positive(period, "period")
    return tuple(kernel[(index - shift) % period] for index in range(period))


def run_circulant_mixer_benchmark(
    *,
    period: int = 8,
    input_values: Optional[Sequence[int]] = None,
    kernel_values: Optional[Sequence[int]] = None,
    wrong_shift: int = 1,
) -> CirculantMixerBenchmarkResult:
    """Validate a circulant mixer against its dense matrix baseline.

    This fixture checks exact output parity and parameter counts for a circular
    convolution mixer. It also reports a wrong-shift control. It is not a
    neural layer quality, runtime, memory, or hardware-efficiency benchmark.
    """
    _require_positive(period, "period")
    values = normalize_circulant_vector(input_values, period, "input_values")
    kernel = normalize_circulant_vector(kernel_values, period, "kernel_values")
    circulant_output = circulant_mixer_output(values, kernel)
    dense_output = dense_matrix_vector_product(dense_circulant_matrix(kernel), values)
    wrong_output = circulant_mixer_output(values, rotate_kernel(kernel, wrong_shift))
    deltas = tuple(abs(left - right) for left, right in zip(circulant_output, dense_output))

    dense_parameters = period * period
    circulant_parameters = period
    return CirculantMixerBenchmarkResult(
        period=period,
        dense_parameters=dense_parameters,
        circulant_parameters=circulant_parameters,
        parameter_ratio=circulant_parameters / dense_parameters,
        input_values=values,
        kernel_values=kernel,
        circulant_output=circulant_output,
        dense_output=dense_output,
        wrong_shift_output=wrong_output,
        max_abs_dense_delta=max(deltas) if deltas else 0,
        wrong_shift_mismatch_count=sum(
            1 for correct, wrong in zip(circulant_output, wrong_output) if correct != wrong
        ),
    )


def synthetic_multicoil_phase_dataset(
    periods: Sequence[int],
    length: int,
    *,
    start: int = 0,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return positions and binary labels controlled by combined phases."""
    normalize_multicoil_periods(periods)
    if length <= 0:
        raise ValueError("length must be positive")
    positions = tuple(range(start, start + length))
    labels = tuple(multicoil_phase_label(periods, position) for position in positions)
    return positions, labels


def default_positive_lags(period: int) -> tuple[int, ...]:
    """Choose a deterministic nontrivial relative-lag pattern."""
    _require_positive(period, "period")
    lags = tuple(lag for lag in range(period) if lag % 3 == 1)
    if not lags or len(lags) == period:
        raise ValueError("period must produce a nontrivial lag pattern")
    return lags


def normalize_positive_lags(period: int, positive_lags: Optional[Sequence[int]]) -> tuple[int, ...]:
    _require_positive(period, "period")
    lags = default_positive_lags(period) if positive_lags is None else tuple(positive_lags)
    normalized = tuple(sorted({lag % period for lag in lags}))
    if not normalized:
        raise ValueError("positive_lags must contain at least one lag")
    if len(normalized) == period:
        raise ValueError("positive_lags must not contain every lag")
    return normalized


def rope_relative_feature(period: int, query_position: int, key_position: int) -> tuple[float, float]:
    """Return a rounded sine/cosine feature for a relative RoPE-style phase."""
    _require_positive(period, "period")
    lag = (query_position - key_position) % period
    angle = tau * lag / period
    return (round(cos(angle), 12), round(sin(angle), 12))


def synthetic_rope_relative_dataset(
    period: int,
    length: int,
    *,
    start: int = 0,
    positive_lags: Optional[Sequence[int]] = None,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    """Return query/key pairs and labels controlled by relative phase."""
    _require_positive(period, "period")
    if length <= 0:
        raise ValueError("length must be positive")
    lags = normalize_positive_lags(period, positive_lags)
    pairs = []
    labels = []
    for sample_index in range(start, start + length):
        query_position = sample_index // period
        lag = sample_index % period
        key_position = query_position - lag
        pairs.append((query_position, key_position))
        labels.append(1 if lag in lags else 0)
    return tuple(pairs), tuple(labels)


def fit_rope_relative_lookup(
    period: int,
    pairs: Sequence[tuple[int, int]],
    labels: Sequence[int],
) -> tuple[tuple[tuple[float, float], int], ...]:
    """Fit a lookup table over relative sine/cosine phase features."""
    _require_positive(period, "period")
    if len(pairs) != len(labels):
        raise ValueError("pairs and labels must have the same length")
    if not pairs:
        raise ValueError("pairs must be nonempty")
    counts: dict[tuple[float, float], list[int]] = {}
    for (query_position, key_position), label in zip(pairs, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        feature = rope_relative_feature(period, query_position, key_position)
        if feature not in counts:
            counts[feature] = [0, 0]
        counts[feature][label] += 1
    entries = []
    for feature, (zero_count, one_count) in counts.items():
        entries.append((feature, 1 if one_count >= zero_count else 0))
    return tuple(sorted(entries))


def predict_rope_relative_lookup(
    period: int,
    lookup: Sequence[tuple[tuple[float, float], int]],
    pairs: Sequence[tuple[int, int]],
) -> tuple[int, ...]:
    """Predict labels from a fitted relative phase lookup table."""
    _require_positive(period, "period")
    lookup_map = {feature: label for feature, label in lookup}
    if not lookup_map:
        raise ValueError("lookup must be nonempty")
    fallback = majority_label(tuple(lookup_map.values()))
    return tuple(
        lookup_map.get(rope_relative_feature(period, query_position, key_position), fallback)
        for query_position, key_position in pairs
    )


def _query_positions_from_pairs(pairs: Sequence[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(query_position for query_position, _ in pairs)


def fit_multicoil_phase_lookup(
    periods: Sequence[int],
    positions: Sequence[int],
    labels: Sequence[int],
) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Fit a combined-phase lookup table by majority label."""
    normalized = normalize_multicoil_periods(periods)
    if len(positions) != len(labels):
        raise ValueError("positions and labels must have the same length")
    if not positions:
        raise ValueError("positions must be nonempty")
    counts: dict[tuple[int, ...], list[int]] = {}
    for position, label in zip(positions, labels):
        if label not in (0, 1):
            raise ValueError("labels must be binary")
        phase = multicoil_phase(normalized, position)
        if phase not in counts:
            counts[phase] = [0, 0]
        counts[phase][label] += 1
    entries = []
    for phase, (zero_count, one_count) in counts.items():
        entries.append((phase, 1 if one_count >= zero_count else 0))
    return tuple(sorted(entries))


def predict_multicoil_phase_lookup(
    periods: Sequence[int],
    lookup: Sequence[tuple[tuple[int, ...], int]],
    positions: Sequence[int],
) -> tuple[int, ...]:
    """Predict labels from a fitted combined-phase lookup table."""
    normalized = normalize_multicoil_periods(periods)
    lookup_map = {phase: label for phase, label in lookup}
    if not lookup_map:
        raise ValueError("lookup must be nonempty")
    fallback = majority_label(tuple(lookup_map.values()))
    return tuple(lookup_map.get(multicoil_phase(normalized, position), fallback) for position in positions)


def run_multicoil_rope_benchmark(
    *,
    periods: Sequence[int] = (5, 7),
    train_length: int = 140,
    test_length: int = 70,
) -> MultiCoilRoPEBenchmarkResult:
    """Run a deterministic MultiCoil/RoPE-style fixture with baselines.

    The positive fixture labels positions by a combined phase tuple. A
    multi-period lookup should recover that synthetic pattern, while a
    single-period lookup and scalar threshold baseline should be weaker. The
    nonperiodic control labels positions by a scalar threshold, where circular
    phase lookup should not win. This is not a RoPE quality claim.
    """
    normalized = normalize_multicoil_periods(periods)
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")

    train_positions, train_labels = synthetic_multicoil_phase_dataset(normalized, train_length)
    test_positions, test_labels = synthetic_multicoil_phase_dataset(
        normalized,
        test_length,
        start=train_length,
    )

    multicoil_lookup = fit_multicoil_phase_lookup(normalized, train_positions, train_labels)
    multicoil_predictions = predict_multicoil_phase_lookup(normalized, multicoil_lookup, test_positions)
    single_period = normalized[0]
    single_lookup = fit_phase_lookup(single_period, train_positions, train_labels)
    single_predictions = predict_phase_lookup(single_period, single_lookup, test_positions)
    threshold, polarity = fit_threshold_classifier(train_positions, train_labels)
    threshold_predictions = predict_threshold_classifier(test_positions, threshold, polarity)
    constant = majority_label(train_labels)
    constant_predictions = tuple(constant for _ in test_positions)

    control_threshold = (3 * train_length) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(position, control_threshold)
        for position in train_positions
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(position, control_threshold)
        for position in test_positions
    )
    control_multicoil_lookup = fit_multicoil_phase_lookup(
        normalized,
        train_positions,
        control_train_labels,
    )
    control_multicoil_predictions = predict_multicoil_phase_lookup(
        normalized,
        control_multicoil_lookup,
        test_positions,
    )
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_positions,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_positions,
        control_threshold_fit,
        control_polarity,
    )

    return MultiCoilRoPEBenchmarkResult(
        periods=normalized,
        train_length=train_length,
        test_length=test_length,
        cycle_length=multicoil_cycle_length(normalized),
        observed_phase_count=len(multicoil_lookup),
        multicoil_phase_accuracy=accuracy(multicoil_predictions, test_labels),
        single_period_phase_accuracy=accuracy(single_predictions, test_labels),
        scalar_threshold_accuracy=accuracy(threshold_predictions, test_labels),
        constant_accuracy=accuracy(constant_predictions, test_labels),
        nonperiodic_multicoil_phase_accuracy=accuracy(
            control_multicoil_predictions,
            control_test_labels,
        ),
        nonperiodic_scalar_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
    )


def run_rope_relative_phase_benchmark(
    *,
    period: int = 8,
    wrong_period: int = 7,
    train_length: int = 64,
    test_length: int = 32,
    positive_lags: Optional[Sequence[int]] = None,
) -> RoPERelativePhaseBenchmarkResult:
    """Run a deterministic RoPE-style relative phase fixture.

    The positive task labels query/key pairs by their relative lag modulo the
    true period. A correct relative phase lookup should solve the task, while
    a wrong-period relative lookup, query-only lookup, and scalar threshold
    baseline should stay weaker. The nonperiodic control labels pairs by the
    query index so the scalar threshold should win. This is not a RoPE quality
    or language-model benchmark.
    """
    _require_positive(period, "period")
    _require_positive(wrong_period, "wrong_period")
    if train_length <= 0:
        raise ValueError("train_length must be positive")
    if test_length <= 0:
        raise ValueError("test_length must be positive")
    lags = normalize_positive_lags(period, positive_lags)

    train_pairs, train_labels = synthetic_rope_relative_dataset(
        period,
        train_length,
        positive_lags=lags,
    )
    test_pairs, test_labels = synthetic_rope_relative_dataset(
        period,
        test_length,
        start=train_length,
        positive_lags=lags,
    )

    rope_lookup = fit_rope_relative_lookup(period, train_pairs, train_labels)
    rope_predictions = predict_rope_relative_lookup(period, rope_lookup, test_pairs)
    wrong_lookup = fit_rope_relative_lookup(wrong_period, train_pairs, train_labels)
    wrong_predictions = predict_rope_relative_lookup(wrong_period, wrong_lookup, test_pairs)
    train_queries = _query_positions_from_pairs(train_pairs)
    test_queries = _query_positions_from_pairs(test_pairs)
    query_lookup = _fit_position_lookup(train_queries, train_labels)
    query_predictions = _predict_position_lookup(query_lookup, test_queries)
    threshold, polarity = fit_threshold_classifier(train_queries, train_labels)
    threshold_predictions = predict_threshold_classifier(test_queries, threshold, polarity)

    control_threshold = (3 * (train_length // period)) // 4
    control_train_labels = tuple(
        nonperiodic_threshold_label(query_position, control_threshold)
        for query_position in train_queries
    )
    control_test_labels = tuple(
        nonperiodic_threshold_label(query_position, control_threshold)
        for query_position in test_queries
    )
    control_rope_lookup = fit_rope_relative_lookup(period, train_pairs, control_train_labels)
    control_rope_predictions = predict_rope_relative_lookup(period, control_rope_lookup, test_pairs)
    control_threshold_fit, control_polarity = fit_threshold_classifier(
        train_queries,
        control_train_labels,
    )
    control_threshold_predictions = predict_threshold_classifier(
        test_queries,
        control_threshold_fit,
        control_polarity,
    )

    return RoPERelativePhaseBenchmarkResult(
        period=period,
        wrong_period=wrong_period,
        train_length=train_length,
        test_length=test_length,
        positive_lags=lags,
        observed_relative_feature_count=len(rope_lookup),
        rope_relative_accuracy=accuracy(rope_predictions, test_labels),
        wrong_period_rope_accuracy=accuracy(wrong_predictions, test_labels),
        query_position_accuracy=accuracy(query_predictions, test_labels),
        scalar_query_threshold_accuracy=accuracy(threshold_predictions, test_labels),
        nonperiodic_rope_relative_accuracy=accuracy(
            control_rope_predictions,
            control_test_labels,
        ),
        nonperiodic_scalar_query_threshold_accuracy=accuracy(
            control_threshold_predictions,
            control_test_labels,
        ),
    )


def _retrieval_hit_indicators(
    sequence_length: int,
    query_indices: Sequence[int],
    target_lag: int,
    candidate_sets: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    if len(query_indices) != len(candidate_sets):
        raise ValueError("query_indices and candidate_sets must have the same length")
    return tuple(
        1 if retrieval_target_index(sequence_length, query_index, target_lag) in set(candidates) else 0
        for query_index, candidates in zip(query_indices, candidate_sets)
    )


def ai_backend_parity_cases() -> tuple[tuple[str, tuple[int, ...], tuple[int, ...]], ...]:
    """Return deterministic binary scoring cases shared by CPU and MLX."""
    phase_train_positions, phase_train_labels = synthetic_phase_dataset(8, 64)
    phase_test_positions, phase_test_labels = synthetic_phase_dataset(8, 32, start=64)
    phase_lookup = fit_phase_lookup(8, phase_train_positions, phase_train_labels)
    phase_predictions = predict_phase_lookup(8, phase_lookup, phase_test_positions)
    phase_constant = majority_label(phase_train_labels)

    memory_train_tokens, memory_train_labels = synthetic_memory_slot_dataset(8, 64)
    memory_test_tokens, memory_test_labels = synthetic_memory_slot_dataset(8, 32, start=64)
    memory_lookup = fit_memory_slot_lookup(8, memory_train_tokens, memory_train_labels)
    memory_predictions = predict_memory_slot_lookup(8, memory_lookup, memory_test_tokens)

    adapter_train_channels, adapter_train_labels = synthetic_adapter_block_dataset(8, 64)
    adapter_test_channels, adapter_test_labels = synthetic_adapter_block_dataset(8, 32, start=64)
    adapter_lookup = fit_adapter_block_lookup(8, adapter_train_channels, adapter_train_labels)
    adapter_predictions = predict_adapter_block_lookup(8, adapter_lookup, adapter_test_channels)

    multicoil_train_positions, multicoil_train_labels = synthetic_multicoil_phase_dataset((5, 7), 140)
    multicoil_test_positions, multicoil_test_labels = synthetic_multicoil_phase_dataset((5, 7), 70, start=140)
    multicoil_lookup = fit_multicoil_phase_lookup((5, 7), multicoil_train_positions, multicoil_train_labels)
    multicoil_predictions = predict_multicoil_phase_lookup((5, 7), multicoil_lookup, multicoil_test_positions)

    retrieval_queries = tuple(range(64))
    retrieval_candidates = tuple(
        coil_attention_path(64, query_index, stride=7, path_length=3)
        for query_index in retrieval_queries
    )
    retrieval_predictions = _retrieval_hit_indicators(64, retrieval_queries, 21, retrieval_candidates)
    retrieval_labels = tuple(1 for _ in retrieval_queries)

    learned_train_positions, learned_train_labels = synthetic_phase_dataset(8, 64)
    learned_test_positions, learned_test_labels = synthetic_phase_dataset(8, 32, start=64)
    learned_lookup = fit_phase_lookup(8, learned_train_positions, learned_train_labels)
    learned_predictions = predict_phase_lookup(8, learned_lookup, learned_test_positions)
    learned_control_threshold = (3 * 64) // 4
    learned_control_train_labels = tuple(
        nonperiodic_threshold_label(position, learned_control_threshold)
        for position in learned_train_positions
    )
    learned_control_test_labels = tuple(
        nonperiodic_threshold_label(position, learned_control_threshold)
        for position in learned_test_positions
    )
    learned_control_threshold_fit, learned_control_polarity = fit_threshold_classifier(
        learned_train_positions,
        learned_control_train_labels,
    )
    learned_control_predictions = predict_threshold_classifier(
        learned_test_positions,
        learned_control_threshold_fit,
        learned_control_polarity,
    )

    harmonic_train_positions, harmonic_train_labels = synthetic_phase_dataset(8, 64)
    harmonic_test_positions, harmonic_test_labels = synthetic_phase_dataset(8, 32, start=64)
    harmonic_lookup = fit_harmonic_feature_lookup(8, harmonic_train_positions, harmonic_train_labels)
    harmonic_predictions = predict_harmonic_feature_lookup(8, harmonic_lookup, harmonic_test_positions)

    rope_train_pairs, rope_train_labels = synthetic_rope_relative_dataset(8, 64)
    rope_test_pairs, rope_test_labels = synthetic_rope_relative_dataset(8, 32, start=64)
    rope_lookup = fit_rope_relative_lookup(8, rope_train_pairs, rope_train_labels)
    rope_predictions = predict_rope_relative_lookup(8, rope_lookup, rope_test_pairs)

    near_local_candidates = tuple(
        local_window_indices(64, query_index, window=8)
        for query_index in retrieval_queries
    )
    near_local_predictions = _retrieval_hit_indicators(64, retrieval_queries, 3, near_local_candidates)
    near_local_labels = tuple(1 for _ in retrieval_queries)

    gated_target_lags = mixed_retrieval_target_lags(
        retrieval_queries,
        long_target_lag=21,
        near_target_lag=3,
    )
    gated_coil_candidates = tuple(
        coil_attention_path(64, query_index, stride=7, path_length=3)
        for query_index in retrieval_queries
    )
    gated_local_candidates = tuple(
        local_window_indices(64, query_index, window=8)
        for query_index in retrieval_queries
    )
    gated_candidates = tuple(
        coil if query_index % 2 == 0 else local
        for query_index, coil, local in zip(retrieval_queries, gated_coil_candidates, gated_local_candidates)
    )
    gated_predictions = tuple(
        1 if retrieval_target_index(64, query_index, target_lag) in set(candidates) else 0
        for query_index, target_lag, candidates in zip(retrieval_queries, gated_target_lags, gated_candidates)
    )
    gated_labels = tuple(1 for _ in retrieval_queries)

    looped_test_indices = tuple(range(64, 96))
    looped_predictions = _loop_adaptive_exit_predictions(
        4,
        looped_test_indices,
        4,
        overthink_tolerance=1,
    )
    looped_labels = tuple(1 for _ in looped_test_indices)

    return (
        ("phase_lookup", phase_predictions, phase_test_labels),
        (
            "phase_constant_baseline",
            tuple(phase_constant for _ in phase_test_positions),
            phase_test_labels,
        ),
        ("memory_lookup", memory_predictions, memory_test_labels),
        ("adapter_lookup", adapter_predictions, adapter_test_labels),
        ("multicoil_lookup", multicoil_predictions, multicoil_test_labels),
        ("retrieval_coil_path", retrieval_predictions, retrieval_labels),
        ("retrieval_near_local_window", near_local_predictions, near_local_labels),
        ("retrieval_content_gated", gated_predictions, gated_labels),
        ("learned_feature_cyclic", learned_predictions, learned_test_labels),
        ("harmonic_feature_lookup", harmonic_predictions, harmonic_test_labels),
        ("rope_relative_phase", rope_predictions, rope_test_labels),
        ("looped_recurrence_adaptive_exit", looped_predictions, looped_labels),
        (
            "learned_feature_nonperiodic_dense_scalar",
            learned_control_predictions,
            learned_control_test_labels,
        ),
    )


def run_ai_backend_parity_check() -> AIBackendParityResult:
    """Compare CPU scoring with optional MLX scoring on deterministic cases."""
    cases = ai_backend_parity_cases()
    cpu_scores = tuple((name, accuracy(predictions, labels)) for name, predictions, labels in cases)
    if not mlx_available():
        return AIBackendParityResult(
            fixture_count=len(cases),
            cpu_scores=cpu_scores,
            mlx_available=False,
            mlx_scores=(),
            max_abs_delta=None,
        )

    mlx_scores = tuple((name, _mlx_accuracy(predictions, labels)) for name, predictions, labels in cases)
    deltas = tuple(abs(cpu_score - mlx_score) for (_, cpu_score), (_, mlx_score) in zip(cpu_scores, mlx_scores))
    return AIBackendParityResult(
        fixture_count=len(cases),
        cpu_scores=cpu_scores,
        mlx_available=True,
        mlx_scores=mlx_scores,
        max_abs_delta=max(deltas) if deltas else 0.0,
    )
