from fractions import Fraction

from circle_math.extremal import (
    is_three_ap_free,
    roth_interval_example,
    three_ap_witnesses,
)


def test_three_ap_witness_search() -> None:
    assert three_ap_witnesses([0, 2, 4], limit=1) == ((0, 2, 4),)
    assert is_three_ap_free([0, 1, 3, 7])


def test_roth_interval_example_records_density_and_witnesses() -> None:
    example = roth_interval_example(8, [0, 1, 2, 4, 7])
    assert example.theorem_id == "CC-T0066"
    assert example.density == Fraction(5, 8)
    assert (0, 1, 2) in example.witnesses
    assert example.has_progression
