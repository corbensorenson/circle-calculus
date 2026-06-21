from __future__ import annotations

from math import exp, isclose, pi, tau

from circle_math.core import (
    CIRCULAR_STATISTICS_THEOREM_IDS,
    angular_difference,
    circular_mean,
    circular_mean_report,
    circular_variance,
    finite_residue_histogram,
    finite_residue_samples,
    finite_same_phase,
    finite_wrapped_distance,
    mean_resultant_length,
    normalize_angle,
    resultant_vector,
    von_mises_weight,
    wrapped_angular_error,
)


def test_finite_same_phase_and_wrapped_distance_match_modular_contract() -> None:
    assert finite_same_phase(12, 1, 25) is True
    assert finite_same_phase(12, 1, 26) is False
    assert finite_wrapped_distance(12, 1, 11) == 2
    assert finite_wrapped_distance(12, 11, 1) == 2


def test_finite_residue_samples_and_histogram() -> None:
    assert finite_residue_samples(5, [0, 5, 7, 12]) == (0, 0, 2, 2)
    assert finite_residue_histogram(5, [0, 5, 7, 12]) == {0: 2, 2: 2}
    assert finite_residue_histogram(
        5,
        [0, 5, 7, 12],
        include_zero_counts=True,
    ) == {0: 2, 1: 0, 2: 2, 3: 0, 4: 0}


def test_normalize_and_wrapped_angular_error() -> None:
    assert isclose(normalize_angle(-pi), pi)
    assert isclose(angular_difference(0.0, 3.0 * pi / 2.0), -pi / 2.0)
    assert isclose(wrapped_angular_error(0.0, 3.0 * pi / 2.0), pi / 2.0)


def test_circular_mean_and_resultant_report() -> None:
    assert isclose(circular_mean([0.0, tau / 4.0]) or 0.0, tau / 8.0)

    report = circular_mean_report([0.0, tau / 4.0])
    assert report.schema_id == "circle_calculus.circular_statistics_report.v0"
    assert report.theorem_ids == CIRCULAR_STATISTICS_THEOREM_IDS
    assert report.undefined_mean is False
    assert isclose(report.mean_angle or 0.0, tau / 8.0)
    assert isclose(report.mean_resultant_length, 2**0.5 / 2.0)
    assert isclose(report.circular_variance, 1.0 - 2**0.5 / 2.0)


def test_antipodal_samples_have_undefined_mean_under_tolerance() -> None:
    report = circular_mean_report([0.0, pi])
    assert report.undefined_mean is True
    assert report.mean_angle is None
    assert report.mean_resultant_length < 1e-12


def test_resultant_variance_and_von_mises_weight() -> None:
    x, y = resultant_vector([0.0, tau / 4.0])
    assert isclose(x, 1.0)
    assert isclose(y, 1.0)
    assert isclose(mean_resultant_length([0.0, tau / 4.0]), 2**0.5 / 2.0)
    assert isclose(circular_variance([0.0, tau / 4.0]), 1.0 - 2**0.5 / 2.0)
    assert isclose(von_mises_weight(0.0, mean=0.0, kappa=2.0), exp(2.0))
