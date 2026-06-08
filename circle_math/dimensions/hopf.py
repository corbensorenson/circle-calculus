from __future__ import annotations

import cmath
import math


Point3 = tuple[float, float, float]
DEFAULT_HOPF_TOLERANCE = 1e-12


def pair_norm_sq(z0: complex, z1: complex) -> float:
    """Return |z0|^2 + |z1|^2 for complex-pair S3 coordinates."""
    return abs(z0) ** 2 + abs(z1) ** 2


def normalize_pair(z0: complex, z1: complex) -> tuple[complex, complex]:
    """Scale a nonzero complex pair onto the unit S3 in C^2."""
    norm_sq = pair_norm_sq(z0, z1)
    if norm_sq == 0.0:
        raise ValueError("cannot normalize the zero complex pair")
    scale = math.sqrt(norm_sq)
    return (z0 / scale, z1 / scale)


def hopf_map(z0: complex, z1: complex) -> Point3:
    """Return the standard complex-pair Hopf map coordinates."""
    product = z0 * z1.conjugate()
    return (2.0 * product.real, 2.0 * product.imag, abs(z0) ** 2 - abs(z1) ** 2)


def sphere_norm_sq(point: Point3) -> float:
    """Return x^2+y^2+z^2 for an S2 candidate."""
    x, y, z = point
    return x * x + y * y + z * z


def unit_phase(theta: float) -> complex:
    """Return exp(i theta), a unit complex phase."""
    return cmath.exp(1j * theta)


def phase_rotate(z0: complex, z1: complex, theta: float) -> tuple[complex, complex]:
    """Apply the same S1 phase to both complex coordinates."""
    phase = unit_phase(theta)
    return (phase * z0, phase * z1)


def hopf_fiber_point(z0: complex, z1: complex, theta: float) -> tuple[complex, complex]:
    """Return the point in the Hopf phase orbit at angle theta."""
    return phase_rotate(z0, z1, theta)


def point_close(left: Point3, right: Point3, *, tol: float = DEFAULT_HOPF_TOLERANCE) -> bool:
    """Compare two executable Hopf base records coordinatewise."""
    return all(abs(left_coord - right_coord) <= tol for left_coord, right_coord in zip(left, right))


def complex_pair_coordinates(pair: tuple[complex, complex]) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return explicit real/imaginary coordinates for a complex pair."""
    left, right = pair
    return ((left.real, left.imag), (right.real, right.imag))


def hopf_phase_record(z0: complex, z1: complex, theta: float) -> dict[str, object]:
    """Return the bounded hidden-phase invariance record used by the S3 Hopf note."""
    normalized = normalize_pair(z0, z1)
    rotated = phase_rotate(*normalized, theta)
    base = hopf_map(*normalized)
    rotated_base = hopf_map(*rotated)
    return {
        "normalized_pair": complex_pair_coordinates(normalized),
        "rotated_pair": complex_pair_coordinates(rotated),
        "base_point": base,
        "rotated_base_point": rotated_base,
        "pair_norm_sq": pair_norm_sq(*normalized),
        "rotated_pair_norm_sq": pair_norm_sq(*rotated),
        "base_norm_sq": sphere_norm_sq(base),
        "rotated_base_norm_sq": sphere_norm_sq(rotated_base),
        "base_points_match": point_close(base, rotated_base),
    }
