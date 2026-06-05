def phase_coordinate(period: int, step: int) -> int:
    assert period > 0
    return step % period


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
