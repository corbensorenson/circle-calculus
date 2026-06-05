from __future__ import annotations

from dataclasses import dataclass

from .quaternion import Quaternion


Coordinate8 = tuple[float, float, float, float, float, float, float, float]


@dataclass(frozen=True)
class Octonion:
    """Small exploratory octonion record using the Cayley-Dickson product."""

    coordinates: Coordinate8

    @staticmethod
    def from_pair(left: Quaternion, right: Quaternion) -> Octonion:
        return Octonion((*left.coordinates(), *right.coordinates()))

    def as_pair(self) -> tuple[Quaternion, Quaternion]:
        c = self.coordinates
        return (Quaternion(c[0], c[1], c[2], c[3]), Quaternion(c[4], c[5], c[6], c[7]))

    def __add__(self, other: Octonion) -> Octonion:
        return Octonion(tuple(a + b for a, b in zip(self.coordinates, other.coordinates)))  # type: ignore[arg-type]

    def __neg__(self) -> Octonion:
        return Octonion(tuple(-value for value in self.coordinates))  # type: ignore[arg-type]

    def __sub__(self, other: Octonion) -> Octonion:
        return self + (-other)

    def __mul__(self, other: Octonion) -> Octonion:
        left_a, right_a = self.as_pair()
        left_b, right_b = other.as_pair()
        left = left_a * left_b - right_b.conjugate() * right_a
        right = right_b * left_a + right_a * left_b.conjugate()
        return Octonion.from_pair(left, right)

    def scale(self, factor: float) -> Octonion:
        return Octonion(tuple(factor * value for value in self.coordinates))  # type: ignore[arg-type]

    def conjugate(self) -> Octonion:
        left, right = self.as_pair()
        return Octonion.from_pair(left.conjugate(), -right)

    def squared_norm(self) -> float:
        return sum(value * value for value in self.coordinates)


def octonion_basis() -> tuple[Octonion, ...]:
    """Return e0 through e7 for the coordinate octonion model."""
    return tuple(
        Octonion(tuple(1.0 if index == basis_index else 0.0 for index in range(8)))  # type: ignore[arg-type]
        for basis_index in range(8)
    )


def normalize(octonion: Octonion) -> Octonion:
    """Scale a nonzero octonion to squared norm one."""
    norm_sq = octonion.squared_norm()
    if norm_sq == 0.0:
        raise ValueError("cannot normalize the zero octonion")
    return octonion.scale(norm_sq ** -0.5)


def real_part(octonion: Octonion) -> float:
    return octonion.coordinates[0]
