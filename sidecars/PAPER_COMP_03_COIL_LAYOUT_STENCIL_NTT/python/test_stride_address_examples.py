def stride_address(size: int, stride: int, step: int) -> int:
    assert size > 0
    return (step * stride) % size


def test_stride_address_is_bounded() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            for step in range(0, 128):
                assert 0 <= stride_address(size, stride, step) < size


def test_stride_address_closes_after_size_steps() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            for step in range(0, 128):
                assert stride_address(size, stride, step + size) == stride_address(size, stride, step)


def test_stride_address_zero_step() -> None:
    for size in range(1, 33):
        for stride in range(0, 33):
            assert stride_address(size, stride, 0) == 0


def test_stride_address_zero_stride() -> None:
    for size in range(1, 33):
        for step in range(0, 128):
            assert stride_address(size, 0, step) == 0
