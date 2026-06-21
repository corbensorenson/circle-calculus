from __future__ import annotations

from circle_math.core import (
    CYCLIC_EQUIVARIANCE_THEOREM_IDS,
    check_cyclic_equivariance,
    circulant_equivariance_report,
    circulant_layer,
    cyclic_orbit,
    cyclic_shift,
    cyclic_sum,
    cyclic_sum_invariance_report,
    dihedral_orbit,
    dihedral_transform,
    reflect_signal,
)


def test_cyclic_shift_and_reflection_match_finite_index_conventions() -> None:
    assert cyclic_shift([1, 2, 3, 4], 1) == (4, 1, 2, 3)
    assert cyclic_shift([1, 2, 3, 4], -1) == (2, 3, 4, 1)
    assert reflect_signal([10, 20, 30, 40]) == (10, 40, 30, 20)
    assert dihedral_transform([10, 20, 30, 40], shift=1, reflected=True) == (
        20,
        10,
        40,
        30,
    )


def test_cyclic_and_dihedral_orbits_have_expected_size() -> None:
    signal = [1, 2, 3]
    assert len(cyclic_orbit(signal)) == 3
    assert len(dihedral_orbit(signal)) == 6


def test_cyclic_sum_invariance_report() -> None:
    report = cyclic_sum_invariance_report([[1, 2, 3, 4], [2, -1, 0, 5]])
    assert report.schema_id == "circle_calculus.cyclic_equivariance_report.v0"
    assert report.theorem_ids == CYCLIC_EQUIVARIANCE_THEOREM_IDS
    assert report.transform_family == "cyclic_sum_invariance"
    assert report.passed is True
    assert report.max_abs_delta == 0.0
    assert cyclic_sum(cyclic_shift([1, 2, 3, 4], 2)) == 10


def test_circulant_layer_cyclic_equivariance_report() -> None:
    report = circulant_equivariance_report(
        [2, 0, 1, 0],
        [[1, 2, 0, -1], [0, 3, 1, 2]],
    )
    assert report.transform_family == "cyclic_shift"
    assert report.passed is True
    assert report.max_abs_delta < 1e-9


def test_generic_cyclic_equivariance_checker_accepts_identity_layer() -> None:
    report = check_cyclic_equivariance(lambda signal: signal, [[1, 2, 3]])
    assert report.passed is True
    assert report.failures == ()


def test_circulant_layer_matches_existing_circular_convolution_shape() -> None:
    assert circulant_layer([2, 0, 1, 0], [1, 2, 0, -1]) == (
        2 + 0j,
        3 + 0j,
        1 + 0j,
        0 + 0j,
    )
