from enum import Enum


class Sign(Enum):
    NEG = -1
    POS = 1


def antipode(sign: Sign) -> Sign:
    return Sign.POS if sign is Sign.NEG else Sign.NEG


def test_s0_has_two_points() -> None:
    assert len(Sign) == 2


def test_s0_antipode_is_involutive() -> None:
    for sign in Sign:
        assert antipode(antipode(sign)) is sign


def test_s0_antipode_has_no_fixed_point() -> None:
    for sign in Sign:
        assert antipode(sign) is not sign


def test_s0_antipode_swaps_named_signs() -> None:
    assert antipode(Sign.NEG) is Sign.POS
    assert antipode(Sign.POS) is Sign.NEG


def test_c1_is_not_s0() -> None:
    c1_nodes = (0,)
    assert len(c1_nodes) != len(Sign)
