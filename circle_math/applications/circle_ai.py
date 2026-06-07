"""Executable reference models for Circle AI application seeds.

These functions support examples, smoke tests, and tiny benchmark fixtures.
They are not formal proofs and they are not model-quality claims.
"""

from __future__ import annotations

from dataclasses import dataclass
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
