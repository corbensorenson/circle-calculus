import math

import pytest

from circle_math.dimensions.hopf import (
    hopf_phase_record,
    hopf_fiber_point,
    hopf_map,
    normalize_pair,
    pair_norm_sq,
    phase_rotate,
    sphere_norm_sq,
)


TOL = 1e-12


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def assert_complex_pair_close(
    left: tuple[complex, complex], right: tuple[complex, complex], *, tol: float = TOL
) -> None:
    assert abs(left[0] - right[0]) <= tol
    assert abs(left[1] - right[1]) <= tol


def assert_point_close(
    left: tuple[float, float, float], right: tuple[float, float, float], *, tol: float = TOL
) -> None:
    for left_coord, right_coord in zip(left, right):
        assert_close(left_coord, right_coord, tol=tol)


def test_hopf_map_lands_on_unit_sphere_for_normalized_pair() -> None:
    z0, z1 = normalize_pair(1.0 + 2.0j, -0.5 + 0.25j)

    assert_close(pair_norm_sq(z0, z1), 1.0)
    assert_close(sphere_norm_sq(hopf_map(z0, z1)), 1.0)


@pytest.mark.parametrize("theta", [0.0, 0.25, 1.0, math.pi / 3.0, math.pi, 2.0 * math.pi])
def test_hopf_map_phase_invariant(theta: float) -> None:
    z0, z1 = normalize_pair(0.75 - 0.25j, 0.5 + 1.5j)
    rotated = phase_rotate(z0, z1, theta)

    assert_close(pair_norm_sq(*rotated), 1.0)
    assert_point_close(hopf_map(*rotated), hopf_map(z0, z1))


def test_phase_rotate_identity() -> None:
    z0, z1 = normalize_pair(0.75 - 0.25j, 0.5 + 1.5j)

    assert_complex_pair_close(phase_rotate(z0, z1, 0.0), (z0, z1))


def test_phase_rotate_composition() -> None:
    z0, z1 = normalize_pair(1.0 - 0.75j, 0.2 + 0.9j)

    for theta, phi in [(0.0, 0.5), (0.25, 1.0), (math.pi / 3.0, math.pi / 5.0)]:
        once = phase_rotate(z0, z1, theta)
        twice = phase_rotate(*once, phi)
        combined = phase_rotate(z0, z1, theta + phi)
        assert_complex_pair_close(twice, combined)


def test_hopf_phase_action_laws() -> None:
    z0, z1 = normalize_pair(1.0 - 0.75j, 0.2 + 0.9j)

    def act(phase: complex, pair: tuple[complex, complex]) -> tuple[complex, complex]:
        left, right = pair
        return (phase * left, phase * right)

    for theta, phi in [(0.0, 0.5), (0.25, 1.0), (math.pi / 3.0, math.pi / 5.0)]:
        left_phase = complex(math.cos(theta), math.sin(theta))
        right_phase = complex(math.cos(phi), math.sin(phi))
        assert_complex_pair_close(act(1.0 + 0.0j, (z0, z1)), (z0, z1))
        assert_complex_pair_close(
            act(left_phase, act(right_phase, (z0, z1))),
            act(left_phase * right_phase, (z0, z1)),
        )


def test_hopf_phase_multiplication_identity_and_associativity() -> None:
    phases = [
        complex(math.cos(theta), math.sin(theta))
        for theta in [0.0, 0.25, math.pi / 3.0, math.pi / 2.0]
    ]

    for phase in phases:
        assert_close(abs((1.0 + 0.0j) * phase - phase), 0.0)
        assert_close(abs(phase * (1.0 + 0.0j) - phase), 0.0)

    for left in phases:
        for middle in phases:
            for right in phases:
                assert_close(abs((left * middle) * right - left * (middle * right)), 0.0)


def test_hopf_fiber_phase_orbit_is_circle_like() -> None:
    z0, z1 = normalize_pair(1.0 - 0.75j, 0.2 + 0.9j)
    base = hopf_map(z0, z1)

    for theta in [0.0, 0.5, 1.0, 2.0, math.pi, 1.75 * math.pi]:
        fiber_point = hopf_fiber_point(z0, z1, theta)
        assert_close(pair_norm_sq(*fiber_point), 1.0)
        assert_point_close(hopf_map(*fiber_point), base)

    assert_complex_pair_close(
        hopf_fiber_point(z0, z1, 0.0),
        hopf_fiber_point(z0, z1, 2.0 * math.pi),
    )


def test_hopf_phase_record_exposes_hidden_phase_invariance() -> None:
    record = hopf_phase_record(1.0 - 0.75j, 0.2 + 0.9j, math.pi / 3.0)

    assert_close(record["pair_norm_sq"], 1.0)
    assert_close(record["rotated_pair_norm_sq"], 1.0)
    assert_close(record["base_norm_sq"], 1.0)
    assert_close(record["rotated_base_norm_sq"], 1.0)
    assert record["base_points_match"]
