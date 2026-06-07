from circle_math.applications.circle_ai import memory_slot


def test_memory_slot_is_bounded() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            assert 0 <= memory_slot(bank_size, token) < bank_size


def test_memory_slot_closes_after_bank_size() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            assert memory_slot(bank_size, token + bank_size) == memory_slot(bank_size, token)


def test_memory_slot_closes_after_multiple_bank_passes() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 128):
            for passes in range(0, 9):
                assert memory_slot(bank_size, token + passes * bank_size) == memory_slot(bank_size, token)


def test_memory_slot_is_idempotent() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            normalized = memory_slot(bank_size, token)
            assert memory_slot(bank_size, normalized) == normalized


def test_memory_slot_zero() -> None:
    for bank_size in range(1, 65):
        assert memory_slot(bank_size, 0) == 0
