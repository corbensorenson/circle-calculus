from circle_math.applications.coil_data import (
    autocorrelation_score,
    benchmark_known_period,
    coil_closure_error,
    phase_coordinate,
    rank_periods_by_autocorrelation,
    rank_periods_by_coil_closure,
    synthetic_periodic_signal,
)


def test_phase_coordinate_is_bounded() -> None:
    for period in range(1, 25):
        for step in range(0, 200):
            assert 0 <= phase_coordinate(period, step) < period


def test_phase_coordinate_closes_after_period() -> None:
    for period in range(1, 25):
        for step in range(0, 200):
            assert phase_coordinate(period, step + period) == phase_coordinate(period, step)


def test_phase_coordinate_zero() -> None:
    for period in range(1, 25):
        assert phase_coordinate(period, 0) == 0


def test_synthetic_periodic_signal_is_deterministic() -> None:
    assert synthetic_periodic_signal(12, 48) == synthetic_periodic_signal(12, 48)


def test_coil_closure_error_prefers_true_period_on_synthetic_signal() -> None:
    signal = synthetic_periodic_signal(12, 240)
    candidates = tuple(range(5, 20))

    assert rank_periods_by_coil_closure(signal, candidates)[0] == 12
    assert coil_closure_error(signal, 12) < coil_closure_error(signal, 11)


def test_autocorrelation_baseline_prefers_true_period_on_synthetic_signal() -> None:
    signal = synthetic_periodic_signal(12, 240)
    candidates = tuple(range(5, 20))

    assert rank_periods_by_autocorrelation(signal, candidates)[0] == 12
    assert autocorrelation_score(signal, 12) > autocorrelation_score(signal, 11)


def test_known_period_benchmark_fixture_reports_both_methods() -> None:
    result = benchmark_known_period(12, candidates=tuple(range(5, 20)))

    assert result.true_period == 12
    assert result.coil_best_period == 12
    assert result.autocorrelation_best_period == 12
