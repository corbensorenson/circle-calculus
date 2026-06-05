from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Quaternion:
    """Small executable quaternion record for dimensional sidecars."""

    r: float
    i: float
    j: float
    k: float

    def __add__(self, other: Quaternion) -> Quaternion:
        return Quaternion(self.r + other.r, self.i + other.i, self.j + other.j, self.k + other.k)

    def __neg__(self) -> Quaternion:
        return Quaternion(-self.r, -self.i, -self.j, -self.k)

    def __sub__(self, other: Quaternion) -> Quaternion:
        return self + (-other)

    def __mul__(self, other: Quaternion) -> Quaternion:
        return Quaternion(
            self.r * other.r - self.i * other.i - self.j * other.j - self.k * other.k,
            self.r * other.i + self.i * other.r + self.j * other.k - self.k * other.j,
            self.r * other.j - self.i * other.k + self.j * other.r + self.k * other.i,
            self.r * other.k + self.i * other.j - self.j * other.i + self.k * other.r,
        )

    def scale(self, factor: float) -> Quaternion:
        return Quaternion(factor * self.r, factor * self.i, factor * self.j, factor * self.k)

    def conjugate(self) -> Quaternion:
        return Quaternion(self.r, -self.i, -self.j, -self.k)

    def squared_norm(self) -> float:
        return self.r * self.r + self.i * self.i + self.j * self.j + self.k * self.k

    def coordinates(self) -> tuple[float, float, float, float]:
        return (self.r, self.i, self.j, self.k)


def pair_squared_norm(q0: Quaternion, q1: Quaternion) -> float:
    """Return |q0|^2 + |q1|^2 for quaternion-pair S7 coordinates."""
    return q0.squared_norm() + q1.squared_norm()


def normalize_pair(q0: Quaternion, q1: Quaternion) -> tuple[Quaternion, Quaternion]:
    """Scale a nonzero quaternion pair onto the unit S7 in H^2."""
    norm_sq = pair_squared_norm(q0, q1)
    if norm_sq == 0.0:
        raise ValueError("cannot normalize the zero quaternion pair")
    scale = norm_sq ** -0.5
    return (q0.scale(scale), q1.scale(scale))


def unit_i_phase(theta: float) -> Quaternion:
    """Return cos(theta)+i sin(theta), a unit quaternion phase."""
    import math

    return Quaternion(math.cos(theta), math.sin(theta), 0.0, 0.0)


def right_phase_rotate(
    q0: Quaternion, q1: Quaternion, phase: Quaternion
) -> tuple[Quaternion, Quaternion]:
    """Apply the same right quaternionic phase to both coordinates."""
    return (q0 * phase, q1 * phase)


def quaternionic_hopf_map(q0: Quaternion, q1: Quaternion) -> tuple[float, float, float, float, float]:
    """Return the standard quaternionic Hopf map coordinates in R5."""
    product = (q0 * q1.conjugate()).scale(2.0)
    return (*product.coordinates(), q0.squared_norm() - q1.squared_norm())


def r5_norm_sq(point: tuple[float, float, float, float, float]) -> float:
    """Return the squared Euclidean norm of a five-coordinate S4 candidate."""
    return sum(value * value for value in point)
