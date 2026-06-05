from __future__ import annotations

import cmath
import math


Point3 = tuple[float, float, float]


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
