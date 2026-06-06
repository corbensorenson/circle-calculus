from circle_math.applications.coil_data import (
    autocorrelation_score,
    benchmark_known_period,
    benchmark_period_fixture_suite,
    coil_closure_error,
    phase_coordinate,
    periodogram_score,
    rank_periods_by_autocorrelation,
    rank_periods_by_coil_closure,
    rank_periods_by_periodogram,
    synthetic_aliased_signal,
    synthetic_multi_period_signal,
    synthetic_noisy_periodic_signal,
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


def test_phase_coordinate_closes_after_multiple_periods() -> None:
    for period in range(1, 25):
        for step in range(0, 80):
            for passes in range(0, 9):
                assert phase_coordinate(period, step + passes * period) == phase_coordinate(period, step)


def test_phase_coordinate_is_idempotent() -> None:
    for period in range(1, 25):
        for step in range(0, 200):
            normalized = phase_coordinate(period, step)
            assert phase_coordinate(period, normalized) == normalized


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


def test_periodogram_baseline_prefers_true_period_on_clean_signal() -> None:
    signal = synthetic_periodic_signal(12, 240)
    candidates = tuple(range(5, 20))

    assert rank_periods_by_periodogram(signal, candidates)[0] == 12
    assert periodogram_score(signal, 12) > periodogram_score(signal, 11)


def test_noisy_alias_and_multi_period_signals_are_deterministic() -> None:
    assert synthetic_noisy_periodic_signal(12, 48) == synthetic_noisy_periodic_signal(12, 48)
    assert synthetic_aliased_signal(12, 6, 48) == synthetic_aliased_signal(12, 6, 48)
    assert synthetic_multi_period_signal((12, 20), 48) == synthetic_multi_period_signal((12, 20), 48)


def test_period_fixture_suite_reports_all_baselines_without_overclaiming() -> None:
    results = benchmark_period_fixture_suite()
    names = {result.name for result in results}
    assert names == {"clean", "noisy", "aliased", "multi_period"}
    for result in results:
        assert result.coil_best_period in result.candidates
        assert result.autocorrelation_best_period in result.candidates
        assert result.periodogram_best_period in result.candidates
        assert result.note
