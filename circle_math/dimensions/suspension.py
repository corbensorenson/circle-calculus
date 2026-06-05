from __future__ import annotations

from collections.abc import Sequence

from .common import euler_characteristic, suspension_counts


def suspension_euler_characteristic(counts: Sequence[int]) -> int:
    """Return chi(Susp K) for a finite cell-count list."""
    return euler_characteristic(suspension_counts(counts))

