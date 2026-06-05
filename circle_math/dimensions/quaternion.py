from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Quaternion:
    """Minimal exploratory quaternion record for future S3 sidecars."""

    r: float
    i: float
    j: float
    k: float

    def squared_norm(self) -> float:
        return self.r * self.r + self.i * self.i + self.j * self.j + self.k * self.k

