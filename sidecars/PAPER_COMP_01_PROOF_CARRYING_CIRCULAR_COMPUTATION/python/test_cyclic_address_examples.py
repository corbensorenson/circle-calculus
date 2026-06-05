def cyclic_address(size: int, index: int) -> int:
    assert size > 0
    return index % size


def test_cyclic_address_is_bounded() -> None:
    for size in range(1, 33):
        for index in range(0, 256):
            assert 0 <= cyclic_address(size, index) < size


def test_cyclic_address_wraps_by_size() -> None:
    for size in range(1, 33):
        for index in range(0, 256):
            assert cyclic_address(size, index + size) == cyclic_address(size, index)
