from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Octonion:
    """Minimal exploratory octonion coordinate record for future S7 sidecars."""

    coordinates: tuple[float, float, float, float, float, float, float, float]

    def squared_norm(self) -> float:
        return sum(value * value for value in self.coordinates)

