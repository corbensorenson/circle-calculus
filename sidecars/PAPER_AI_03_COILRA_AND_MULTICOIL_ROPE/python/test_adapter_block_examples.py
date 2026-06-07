from circle_math.applications.circle_ai import (
    adapter_block,
    adapter_block_collision_count,
    adapter_block_loads,
    fit_adapter_block_lookup,
    predict_adapter_block_lookup,
    run_adapter_block_benchmark,
    synthetic_adapter_block_dataset,
)


def test_adapter_block_is_bounded() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            assert 0 <= adapter_block(block_size, channel) < block_size


def test_adapter_block_closes_after_block_size() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            assert adapter_block(block_size, channel + block_size) == adapter_block(block_size, channel)


def test_adapter_block_closes_after_multiple_block_passes() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 128):
            for passes in range(0, 9):
                assert adapter_block(block_size, channel + passes * block_size) == adapter_block(block_size, channel)


def test_adapter_block_is_idempotent() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            normalized = adapter_block(block_size, channel)
            assert adapter_block(block_size, normalized) == normalized


def test_adapter_block_zero() -> None:
    for block_size in range(1, 65):
        assert adapter_block(block_size, 0) == 0


def test_adapter_block_lookup_recovers_periodic_fixture() -> None:
    block_size = 8
    train_channels, train_labels = synthetic_adapter_block_dataset(block_size, 64)
    test_channels, test_labels = synthetic_adapter_block_dataset(block_size, 32, start=64)

    lookup = fit_adapter_block_lookup(block_size, train_channels, train_labels)
    predictions = predict_adapter_block_lookup(block_size, lookup, test_channels)

    assert predictions == test_labels


def test_adapter_block_collision_diagnostics_are_deterministic() -> None:
    block_size = 8
    channels = tuple(range(64))

    assert adapter_block_loads(block_size, channels) == (8, 8, 8, 8, 8, 8, 8, 8)
    assert adapter_block_collision_count(block_size, channels) == 56


def test_adapter_block_benchmark_has_baseline_and_negative_control() -> None:
    result = run_adapter_block_benchmark(block_size=8, train_channels=64, test_channels=32)

    assert result.adapter_block_accuracy == 1.0
    assert result.constant_accuracy < result.adapter_block_accuracy
    assert result.scalar_channel_threshold_accuracy < result.adapter_block_accuracy
    assert result.nonperiodic_scalar_threshold_accuracy == 1.0
    assert result.nonperiodic_adapter_block_accuracy < result.nonperiodic_scalar_threshold_accuracy
    assert result.train_collision_count == 56
    assert result.max_train_block_load == 8
