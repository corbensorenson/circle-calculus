from circle_math.applications.circle_ai import adapter_block


def test_adapter_block_is_bounded() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            assert 0 <= adapter_block(block_size, channel) < block_size


def test_adapter_block_closes_after_block_size() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            assert adapter_block(block_size, channel + block_size) == adapter_block(block_size, channel)


def test_adapter_block_closes_after_multiple_block_passes() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 128):
            for passes in range(0, 9):
                assert adapter_block(block_size, channel + passes * block_size) == adapter_block(block_size, channel)


def test_adapter_block_is_idempotent() -> None:
    for block_size in range(1, 65):
        for channel in range(0, 512):
            normalized = adapter_block(block_size, channel)
            assert adapter_block(block_size, normalized) == normalized


def test_adapter_block_zero() -> None:
    for block_size in range(1, 65):
        assert adapter_block(block_size, 0) == 0
