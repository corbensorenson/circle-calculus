from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import List


@dataclass(frozen=True)
class Circle:
    """Finite v0 circle as a cyclic address space with n > 0 nodes."""

    n: int

    def __post_init__(self) -> None:
        if self.n <= 0:
            raise ValueError("v0 finite circles require n > 0")

    def node(self, i: int) -> int:
        return i % self.n

    def rot(self, i: int, k: int) -> int:
        return (i + k) % self.n

    def orbit(self, start: int, stride: int) -> List[int]:
        out: List[int] = []
        seen: set[int] = set()
        x = self.node(start)
        while x not in seen:
            seen.add(x)
            out.append(x)
            x = self.rot(x, stride)
        return out

    def period(self, stride: int) -> int:
        return self.n // gcd(self.n, stride)

    def is_full_coil(self, stride: int) -> bool:
        return gcd(self.n, stride) == 1

    def orbit_decomposition(self, stride: int) -> List[List[int]]:
        remaining = set(range(self.n))
        orbits: List[List[int]] = []
        while remaining:
            start = min(remaining)
            orbit = self.orbit(start, stride)
            orbits.append(orbit)
            remaining.difference_update(orbit)
        return orbits

    def scale(self, i: int, k: int) -> int:
        return (k * i) % self.n

    def scale_image(self, k: int) -> List[int]:
        return [self.scale(i, k) for i in range(self.n)]

    def scale_is_permutation(self, k: int) -> bool:
        return len(set(self.scale_image(k))) == self.n

