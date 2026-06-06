def round_robin_slot(slot_count: int, tick: int) -> int:
    assert slot_count > 0
    return tick % slot_count


def test_round_robin_slot_is_bounded() -> None:
    for slot_count in range(1, 65):
        for tick in range(0, 512):
            assert 0 <= round_robin_slot(slot_count, tick) < slot_count


def test_round_robin_slot_closes_after_slot_count() -> None:
    for slot_count in range(1, 65):
        for tick in range(0, 512):
            assert round_robin_slot(slot_count, tick + slot_count) == round_robin_slot(slot_count, tick)


def test_round_robin_slot_closes_after_multiple_passes() -> None:
    for slot_count in range(1, 65):
        for tick in range(0, 256):
            for passes in range(0, 16):
                assert (
                    round_robin_slot(slot_count, tick + passes * slot_count)
                    == round_robin_slot(slot_count, tick)
                )


def test_round_robin_slot_zero() -> None:
    for slot_count in range(1, 65):
        assert round_robin_slot(slot_count, 0) == 0
