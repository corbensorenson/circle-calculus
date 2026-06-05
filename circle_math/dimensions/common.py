from __future__ import annotations

from collections.abc import Sequence


def euler_characteristic(counts: Sequence[int]) -> int:
    """Return the alternating sum of finite cell counts."""
    return sum(count if index % 2 == 0 else -count for index, count in enumerate(counts))


def suspension_counts(counts: Sequence[int]) -> tuple[int, ...]:
    """Return the finite cell-count transform for a suspension scaffold."""
    if not counts:
        return (2,)
    transformed = [counts[0] + 2]
    transformed.extend(counts[index] + 2 * counts[index - 1] for index in range(1, len(counts)))
    transformed.append(2 * counts[-1])
    return tuple(transformed)

