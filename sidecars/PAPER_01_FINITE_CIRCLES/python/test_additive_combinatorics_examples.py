import pytest

from circle_math.additive import (
    cauchy_davenport_example,
    circle_pair_sum_counts,
    circle_sumset,
    egz_sharpness_family,
    has_zero_sum_subsequence,
    zero_sum_subsequence_witnesses,
)


def test_circle_sumset_normalizes_inputs_as_finite_sets() -> None:
    assert circle_sumset(5, [0, 5, 1], [2, 7]) == (2, 3)


def test_pair_sum_counts_records_ordered_set_representations() -> None:
    assert circle_pair_sum_counts(5, [0, 1, 1], [0, 2]) == {
        0: 1,
        1: 1,
        2: 1,
        3: 1,
    }


def test_cauchy_davenport_examples_meet_lower_bound() -> None:
    example = cauchy_davenport_example(7, [0, 1, 3], [0, 2, 4])
    assert example.theorem_id == "CC-T0063"
    assert example.lower_bound == 5
    assert len(example.sumset) >= example.lower_bound
    assert example.passes_bound


def test_cauchy_davenport_examples_require_prime_nonempty_inputs() -> None:
    with pytest.raises(ValueError):
        cauchy_davenport_example(8, [0, 1], [0, 2])
    with pytest.raises(ValueError):
        cauchy_davenport_example(7, [], [0, 2])


def test_egz_sharpness_family_has_no_length_n_zero_sum() -> None:
    for modulus in range(2, 9):
        family = egz_sharpness_family(modulus)
        assert len(family) == 2 * modulus - 2
        assert not has_zero_sum_subsequence(modulus, family, modulus)


def test_egz_threshold_plus_one_has_zero_sum_witness() -> None:
    modulus = 5
    family = egz_sharpness_family(modulus) + (1,)
    witnesses = zero_sum_subsequence_witnesses(modulus, family, modulus, limit=1)
    assert witnesses
    assert sum(family[index] for index in witnesses[0]) % modulus == 0
