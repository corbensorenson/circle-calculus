from circle_math.applications.circle_ai import (
    mlx_available,
    harmonic_feature,
    phase_channel,
    run_ai_backend_parity_check,
    run_harmonic_feature_baseline_benchmark,
    run_learned_feature_baseline_benchmark,
    run_learned_phase_baseline_benchmark,
    run_phase_channel_benchmark,
)


def test_phase_channel_is_bounded() -> None:
    for period in range(1, 65):
        for position in range(0, 512):
            assert 0 <= phase_channel(period, position) < period


def test_phase_channel_closes_after_period() -> None:
    for period in range(1, 65):
        for position in range(0, 512):
            assert phase_channel(period, position + period) == phase_channel(period, position)


def test_phase_channel_closes_after_multiple_periods() -> None:
    for period in range(1, 65):
        for position in range(0, 128):
            for passes in range(0, 9):
                assert phase_channel(period, position + passes * period) == phase_channel(period, position)


def test_phase_channel_is_idempotent() -> None:
    for period in range(1, 65):
        for position in range(0, 512):
            normalized = phase_channel(period, position)
            assert phase_channel(period, normalized) == normalized


def test_phase_channel_zero() -> None:
    for period in range(1, 65):
        assert phase_channel(period, 0) == 0


def test_harmonic_feature_closes_after_period() -> None:
    for period in range(1, 65):
        for position in range(0, 128):
            assert harmonic_feature(period, position + period) == harmonic_feature(period, position)


def test_phase_channel_benchmark_fixture_is_deterministic() -> None:
    first = run_phase_channel_benchmark(period=8, train_length=64, test_length=32)
    second = run_phase_channel_benchmark(period=8, train_length=64, test_length=32)
    assert first == second
    assert first.backend == "cpu"
    assert first.phase_channel_accuracy == 1.0
    assert first.constant_accuracy < first.phase_channel_accuracy
    assert first.note.endswith("not a model-quality claim.")


def test_mlx_phase_channel_backend_matches_cpu_when_available() -> None:
    if not mlx_available():
        return
    cpu = run_phase_channel_benchmark(period=8, train_length=64, test_length=32)
    mlx = run_phase_channel_benchmark(period=8, train_length=64, test_length=32, backend="mlx")
    assert mlx.phase_channel_accuracy == cpu.phase_channel_accuracy
    assert mlx.constant_accuracy == cpu.constant_accuracy


def test_learned_phase_baseline_fixture_has_positive_and_negative_controls() -> None:
    result = run_learned_phase_baseline_benchmark(period=8, train_length=64, test_length=32)
    assert result.periodic_phase_accuracy > result.periodic_dense_accuracy
    assert result.nonperiodic_dense_accuracy > result.nonperiodic_phase_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_learned_feature_baseline_fixture_has_baselines_and_controls() -> None:
    result = run_learned_feature_baseline_benchmark(
        period=8,
        wrong_period=7,
        train_length=64,
        test_length=32,
    )
    assert result.periodic_cyclic_feature_accuracy == 1.0
    assert result.periodic_cyclic_feature_accuracy > result.periodic_dense_scalar_accuracy
    assert result.periodic_cyclic_feature_accuracy > result.periodic_learned_position_accuracy
    assert result.periodic_cyclic_feature_accuracy > result.periodic_wrong_period_accuracy
    assert result.nonperiodic_dense_scalar_accuracy == 1.0
    assert result.nonperiodic_dense_scalar_accuracy > result.nonperiodic_cyclic_feature_accuracy
    assert result.nonperiodic_dense_scalar_accuracy > result.nonperiodic_learned_position_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_harmonic_feature_baseline_fixture_has_frequency_controls() -> None:
    result = run_harmonic_feature_baseline_benchmark(
        period=8,
        wrong_period=7,
        train_length=64,
        test_length=32,
    )
    assert result.observed_feature_count == result.period
    assert result.cyclic_phase_accuracy == 1.0
    assert result.harmonic_feature_accuracy == result.cyclic_phase_accuracy
    assert result.wrong_harmonic_accuracy < result.harmonic_feature_accuracy
    assert result.scalar_threshold_accuracy < result.harmonic_feature_accuracy
    assert result.learned_position_accuracy < result.harmonic_feature_accuracy
    assert result.nonperiodic_scalar_threshold_accuracy == 1.0
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_harmonic_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_ai_backend_parity_fixture_is_deterministic() -> None:
    first = run_ai_backend_parity_check()
    second = run_ai_backend_parity_check()
    assert first == second
    assert first.fixture_count >= 10
    assert dict(first.cpu_scores)["phase_lookup"] == 1.0
    assert dict(first.cpu_scores)["learned_feature_cyclic"] == 1.0
    assert dict(first.cpu_scores)["harmonic_feature_lookup"] == 1.0
    assert dict(first.cpu_scores)["learned_feature_nonperiodic_dense_scalar"] == 1.0
    assert dict(first.cpu_scores)["memory_lookup"] == 1.0
    assert dict(first.cpu_scores)["adapter_lookup"] == 1.0
    assert dict(first.cpu_scores)["multicoil_lookup"] == 1.0
    assert dict(first.cpu_scores)["retrieval_coil_path"] == 1.0
    if first.mlx_available:
        assert first.mlx_scores
        assert first.max_abs_delta is not None
        assert first.max_abs_delta < 1e-6
    else:
        assert first.mlx_scores == ()
        assert first.max_abs_delta is None
