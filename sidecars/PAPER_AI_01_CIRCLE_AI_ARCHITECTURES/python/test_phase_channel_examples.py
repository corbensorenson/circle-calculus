from circle_math.applications.circle_ai import (
    mlx_available,
    phase_channel,
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


def test_phase_channel_zero() -> None:
    for period in range(1, 65):
        assert phase_channel(period, 0) == 0


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
