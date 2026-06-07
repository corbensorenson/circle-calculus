from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Optional, Tuple

from .finite import Circle


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 2
    return True


def _finite_set(circle: Circle, values: Iterable[int]) -> Tuple[int, ...]:
    return tuple(sorted({circle.node(value) for value in values}))


def circle_sumset(modulus: int, left: Iterable[int], right: Iterable[int]) -> Tuple[int, ...]:
    """Return the finite-circle set sum `left + right` in `C_modulus`."""

    circle = Circle(modulus)
    left_set = _finite_set(circle, left)
    right_set = _finite_set(circle, right)
    return tuple(sorted({circle.node(a + b) for a in left_set for b in right_set}))


def circle_pair_sum_counts(
    modulus: int, left: Iterable[int], right: Iterable[int]
) -> dict[int, int]:
    """Count ordered set-pair representations of residues in `left + right`."""

    circle = Circle(modulus)
    left_set = _finite_set(circle, left)
    right_set = _finite_set(circle, right)
    counts: Counter[int] = Counter()
    for a in left_set:
        for b in right_set:
            counts[circle.node(a + b)] += 1
    return dict(sorted(counts.items()))


@dataclass(frozen=True)
class CauchyDavenportExample:
    """Executable certificate for a concrete Cauchy-Davenport instance."""

    modulus: int
    left: Tuple[int, ...]
    right: Tuple[int, ...]
    sumset: Tuple[int, ...]
    lower_bound: int

    @property
    def theorem_id(self) -> str:
        return "CC-T0063"

    @property
    def passes_bound(self) -> bool:
        return self.lower_bound <= len(self.sumset)


def cauchy_davenport_example(
    prime_modulus: int, left: Iterable[int], right: Iterable[int]
) -> CauchyDavenportExample:
    """Build a concrete Cauchy-Davenport example over a prime-size circle."""

    if not _is_prime(prime_modulus):
        raise ValueError("Cauchy-Davenport examples require a prime modulus")

    circle = Circle(prime_modulus)
    left_set = _finite_set(circle, left)
    right_set = _finite_set(circle, right)
    if not left_set or not right_set:
        raise ValueError("Cauchy-Davenport examples require nonempty sets")

    sumset = circle_sumset(prime_modulus, left_set, right_set)
    lower_bound = min(prime_modulus, len(left_set) + len(right_set) - 1)
    return CauchyDavenportExample(
        modulus=prime_modulus,
        left=left_set,
        right=right_set,
        sumset=sumset,
        lower_bound=lower_bound,
    )


def egz_sharpness_family(modulus: int) -> Tuple[int, ...]:
    """Return the standard `n - 1` zeros and `n - 1` ones EGZ sharpness family."""

    if modulus < 2:
        raise ValueError("EGZ sharpness examples require modulus at least 2")
    return (0,) * (modulus - 1) + (1,) * (modulus - 1)


def zero_sum_subsequence_witnesses(
    modulus: int,
    family: Iterable[int],
    length: int,
    *,
    limit: Optional[int] = None,
) -> Tuple[Tuple[int, ...], ...]:
    """Find index-tuples whose selected residues sum to zero in `C_modulus`."""

    circle = Circle(modulus)
    values = tuple(circle.node(value) for value in family)
    if length < 0:
        raise ValueError("subsequence length must be nonnegative")
    if length > len(values):
        return ()

    witnesses: list[Tuple[int, ...]] = []
    for indexes in combinations(range(len(values)), length):
        if circle.node(sum(values[index] for index in indexes)) == 0:
            witnesses.append(indexes)
            if limit is not None and len(witnesses) >= limit:
                break
    return tuple(witnesses)


def has_zero_sum_subsequence(modulus: int, family: Iterable[int], length: int) -> bool:
    return bool(zero_sum_subsequence_witnesses(modulus, family, length, limit=1))
