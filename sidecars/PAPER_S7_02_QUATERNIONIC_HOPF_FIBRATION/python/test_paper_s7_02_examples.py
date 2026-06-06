import math

import pytest

from circle_math.dimensions.quaternion import (
    Quaternion,
    normalize_pair,
    pair_squared_norm,
    quaternionic_hopf_map,
    r5_norm_sq,
    right_phase_rotate,
    unit_i_phase,
)


TOL = 1e-12


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def assert_point_close(
    left: tuple[float, float, float, float, float],
    right: tuple[float, float, float, float, float],
    *,
    tol: float = TOL,
) -> None:
    for left_coord, right_coord in zip(left, right):
        assert_close(left_coord, right_coord, tol=tol)


def assert_quaternion_pair_close(
    left: tuple[Quaternion, Quaternion],
    right: tuple[Quaternion, Quaternion],
    *,
    tol: float = TOL,
) -> None:
    for left_quaternion, right_quaternion in zip(left, right):
        for left_coord, right_coord in zip(left_quaternion.coordinates(), right_quaternion.coordinates()):
            assert_close(left_coord, right_coord, tol=tol)


def test_quaternionic_hopf_map_lands_on_s4_for_normalized_pair() -> None:
    q0, q1 = normalize_pair(Quaternion(1.0, 0.5, -0.25, 0.75), Quaternion(-0.5, 1.25, 0.5, 0.0))

    assert_close(pair_squared_norm(q0, q1), 1.0)
    assert_close(r5_norm_sq(quaternionic_hopf_map(q0, q1)), 1.0)


@pytest.mark.parametrize("theta", [0.0, 0.25, math.pi / 4.0, math.pi, 2.0 * math.pi])
def test_quaternionic_hopf_right_phase_invariant(theta: float) -> None:
    q0, q1 = normalize_pair(Quaternion(0.25, -0.5, 1.0, 0.75), Quaternion(1.5, 0.0, -0.25, 0.5))
    phase = unit_i_phase(theta)
    rotated = right_phase_rotate(q0, q1, phase)

    assert_close(phase.squared_norm(), 1.0)
    assert_close(pair_squared_norm(*rotated), 1.0)
    assert_point_close(quaternionic_hopf_map(*rotated), quaternionic_hopf_map(q0, q1))


def test_quaternionic_right_phase_action_composes_and_preserves_base() -> None:
    q0, q1 = normalize_pair(Quaternion(0.25, -0.5, 1.0, 0.75), Quaternion(1.5, 0.0, -0.25, 0.5))
    base = quaternionic_hopf_map(q0, q1)

    for theta, phi in [(0.0, 0.5), (0.25, 1.0), (math.pi / 3.0, math.pi / 5.0)]:
        left_phase = unit_i_phase(theta)
        right_phase = unit_i_phase(phi)
        composed_phase = left_phase * right_phase

        stepwise = right_phase_rotate(*right_phase_rotate(q0, q1, left_phase), right_phase)
        combined = right_phase_rotate(q0, q1, composed_phase)

        assert_close(left_phase.squared_norm(), 1.0)
        assert_close(right_phase.squared_norm(), 1.0)
        assert_close(composed_phase.squared_norm(), 1.0)
        assert_quaternion_pair_close(stepwise, combined)
        assert_point_close(quaternionic_hopf_map(*combined), base)
