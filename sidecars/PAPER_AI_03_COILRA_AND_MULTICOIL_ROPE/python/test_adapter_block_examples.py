from circle_math.applications.circle_ai import (
    adapter_block,
    adapter_block_collision_count,
    adapter_block_loads,
    fit_adapter_block_lookup,
    fit_multicoil_phase_lookup,
    fit_rope_relative_lookup,
    multicoil_cycle_length,
    multicoil_phase,
    predict_adapter_block_lookup,
    predict_multicoil_phase_lookup,
    predict_rope_relative_lookup,
    rope_relative_feature,
    run_adapter_block_benchmark,
    run_multicoil_rope_benchmark,
    run_rope_relative_phase_benchmark,
    synthetic_adapter_block_dataset,
    synthetic_multicoil_phase_dataset,
    synthetic_rope_relative_dataset,
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


def test_multicoil_phase_components_are_bounded() -> None:
    periods = (5, 7)
    for position in range(0, 512):
        phase = multicoil_phase(periods, position)
        assert len(phase) == len(periods)
        assert all(0 <= residue < period for residue, period in zip(phase, periods))


def test_multicoil_phase_closes_after_joint_cycle() -> None:
    periods = (5, 7)
    cycle = multicoil_cycle_length(periods)
    assert cycle == 35
    for position in range(0, 512):
        assert multicoil_phase(periods, position + cycle) == multicoil_phase(periods, position)


def test_multicoil_lookup_recovers_combined_phase_fixture() -> None:
    periods = (5, 7)
    train_positions, train_labels = synthetic_multicoil_phase_dataset(periods, 140)
    test_positions, test_labels = synthetic_multicoil_phase_dataset(periods, 70, start=140)

    lookup = fit_multicoil_phase_lookup(periods, train_positions, train_labels)
    predictions = predict_multicoil_phase_lookup(periods, lookup, test_positions)

    assert len(lookup) == 35
    assert predictions == test_labels


def test_multicoil_rope_benchmark_has_baselines_and_negative_control() -> None:
    result = run_multicoil_rope_benchmark(periods=(5, 7), train_length=140, test_length=70)

    assert result.cycle_length == 35
    assert result.observed_phase_count == 35
    assert result.multicoil_phase_accuracy == 1.0
    assert result.single_period_phase_accuracy < result.multicoil_phase_accuracy
    assert result.scalar_threshold_accuracy < result.multicoil_phase_accuracy
    assert result.constant_accuracy < result.multicoil_phase_accuracy
    assert result.nonperiodic_scalar_threshold_accuracy == 1.0
    assert result.nonperiodic_multicoil_phase_accuracy < result.nonperiodic_scalar_threshold_accuracy


def test_rope_relative_feature_closes_after_period() -> None:
    period = 8
    for query_position in range(0, 64):
        for key_position in range(-8, 8):
            assert rope_relative_feature(period, query_position + period, key_position) == rope_relative_feature(
                period,
                query_position,
                key_position,
            )
            assert rope_relative_feature(period, query_position, key_position + period) == rope_relative_feature(
                period,
                query_position,
                key_position,
            )


def test_rope_relative_lookup_recovers_relative_phase_fixture() -> None:
    period = 8
    train_pairs, train_labels = synthetic_rope_relative_dataset(period, 64)
    test_pairs, test_labels = synthetic_rope_relative_dataset(period, 32, start=64)

    lookup = fit_rope_relative_lookup(period, train_pairs, train_labels)
    predictions = predict_rope_relative_lookup(period, lookup, test_pairs)

    assert len(lookup) == period
    assert predictions == test_labels


def test_rope_relative_phase_benchmark_has_baselines_and_negative_control() -> None:
    result = run_rope_relative_phase_benchmark(period=8, wrong_period=7, train_length=64, test_length=32)

    assert result.observed_relative_feature_count == result.period
    assert result.rope_relative_accuracy == 1.0
    assert result.wrong_period_rope_accuracy < result.rope_relative_accuracy
    assert result.query_position_accuracy < result.rope_relative_accuracy
    assert result.scalar_query_threshold_accuracy < result.rope_relative_accuracy
    assert result.nonperiodic_scalar_query_threshold_accuracy == 1.0
    assert result.nonperiodic_rope_relative_accuracy < result.nonperiodic_scalar_query_threshold_accuracy
    assert result.note.endswith("not a model-quality claim.")
