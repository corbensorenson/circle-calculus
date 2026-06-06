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


def iterated_suspension_counts(steps: int, counts: Sequence[int]) -> tuple[int, ...]:
    """Apply the finite suspension transform repeatedly."""
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    result = tuple(counts)
    for _ in range(steps):
        result = suspension_counts(result)
    return result


def alternating_suspension_euler(steps: int, chi: int) -> int:
    """Return the Euler characteristic after repeatedly applying chi -> 2 - chi."""
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    result = chi
    for _ in range(steps):
        result = 2 - result
    return result
