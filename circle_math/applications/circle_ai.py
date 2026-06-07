"""Executable reference models for Circle AI application seeds.

These functions support examples, smoke tests, and tiny benchmark fixtures.
They are not formal proofs and they are not model-quality claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import lcm
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

    near_local_candidates = tuple(
        local_window_indices(64, query_index, window=8)
        for query_index in retrieval_queries
    )
    near_local_predictions = _retrieval_hit_indicators(64, retrieval_queries, 3, near_local_candidates)
    near_local_labels = tuple(1 for _ in retrieval_queries)

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
        ("learned_feature_cyclic", learned_predictions, learned_test_labels),
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
