def direction_bin(bin_count: int, sample: int) -> int:
    assert bin_count > 0
    return sample % bin_count


def test_direction_bin_is_bounded() -> None:
    for bin_count in range(1, 65):
        for sample in range(0, 512):
            assert 0 <= direction_bin(bin_count, sample) < bin_count


def test_direction_bin_closes_after_bin_count() -> None:
    for bin_count in range(1, 65):
        for sample in range(0, 512):
            assert direction_bin(bin_count, sample + bin_count) == direction_bin(bin_count, sample)
