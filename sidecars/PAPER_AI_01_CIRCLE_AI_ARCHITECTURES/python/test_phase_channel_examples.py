def phase_channel(period: int, position: int) -> int:
    assert period > 0
    return position % period


def test_phase_channel_is_bounded() -> None:
    for period in range(1, 65):
        for position in range(0, 512):
            assert 0 <= phase_channel(period, position) < period


def test_phase_channel_closes_after_period() -> None:
    for period in range(1, 65):
        for position in range(0, 512):
            assert phase_channel(period, position + period) == phase_channel(period, position)
