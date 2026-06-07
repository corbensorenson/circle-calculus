from circle_math.additive import (
    cauchy_davenport_example,
    circle_pair_sum_counts,
    circle_sumset,
    egz_sharpness_family,
    has_zero_sum_subsequence,
    zero_sum_subsequence_witnesses,
)


def test_zero_sum_circle_sumset_examples() -> None:
    assert circle_sumset(5, [0, 5, 1], [2, 7]) == (2, 3)
    assert circle_pair_sum_counts(5, [0, 1, 1], [0, 2]) == {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
    }


def test_cauchy_davenport_circle_example() -> None:
    example = cauchy_davenport_example(7, [0, 1, 3], [0, 2, 4])
    assert example.theorem_id == "CC-T0063"
    assert example.lower_bound == 5
    assert len(example.sumset) >= example.lower_bound
    assert example.passes_bound


def test_egz_sharpness_circle_family() -> None:
    for modulus in range(2, 9):
        family = egz_sharpness_family(modulus)
        assert len(family) == 2 * modulus - 2
        assert not has_zero_sum_subsequence(modulus, family, modulus)


def test_egz_threshold_plus_one_has_witness() -> None:
    modulus = 5
    family = egz_sharpness_family(modulus) + (1,)
    witnesses = zero_sum_subsequence_witnesses(modulus, family, modulus, limit=1)
    assert witnesses
    assert sum(family[index] for index in witnesses[0]) % modulus == 0
