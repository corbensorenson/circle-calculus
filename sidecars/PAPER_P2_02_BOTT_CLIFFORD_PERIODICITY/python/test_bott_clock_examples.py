def bott_clock_index(dimension: int) -> int:
    assert dimension >= 0
    return dimension % 8


def test_bott_clock_index_is_bounded() -> None:
    for dimension in range(0, 256):
        assert 0 <= bott_clock_index(dimension) < 8


def test_bott_clock_closes_after_eight_dimensions() -> None:
    for dimension in range(0, 256):
        assert bott_clock_index(dimension + 8) == bott_clock_index(dimension)


def test_bott_clock_zero() -> None:
    assert bott_clock_index(0) == 0
