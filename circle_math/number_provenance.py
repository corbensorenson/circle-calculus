"""Number provenance fixtures for finite-circle explanations.

This module treats a number as a small construction/index object for S1
examples. It is an interface experiment, not new arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd


@dataclass(frozen=True)
class StrideProvenance:
    size: int
    stride: int
    divisor: int
    cofactor: int
    period: int
    orbit_count: int
    theorem_ids: tuple[str, ...]


@dataclass(frozen=True)
class NumberProvenance:
    value: int
    divisors: tuple[int, ...]
    factor_pairs: tuple[tuple[int, int], ...]
    default_theorem_ids: tuple[str, ...]


def divisors(value: int) -> tuple[int, ...]:
    if value <= 0:
        raise ValueError("value must be positive")
    return tuple(divisor for divisor in range(1, value + 1) if value % divisor == 0)


def factor_pairs(value: int) -> tuple[tuple[int, int], ...]:
    return tuple((divisor, value // divisor) for divisor in divisors(value) if divisor <= value // divisor)


def theorem_ids_for_stride(size: int, stride: int) -> tuple[str, ...]:
    divisor = gcd(size, stride)
    theorem_ids = ["CC-T0005", "CC-T0006", "CC-T0042", "CC-T0044"]
    theorem_ids.append("CC-T0054" if divisor == 1 else "CC-T0030")
    return tuple(theorem_ids)


def number_provenance(value: int) -> NumberProvenance:
    return NumberProvenance(
        value=value,
        divisors=divisors(value),
        factor_pairs=factor_pairs(value),
        default_theorem_ids=("CC-T0005", "CC-T0006", "CC-T0054"),
    )


def stride_provenance(size: int, stride: int) -> StrideProvenance:
    if size <= 0:
        raise ValueError("size must be positive")
    divisor = gcd(size, stride)
    return StrideProvenance(
        size=size,
        stride=stride,
        divisor=divisor,
        cofactor=size // divisor,
        period=size // divisor,
        orbit_count=divisor,
        theorem_ids=theorem_ids_for_stride(size, stride),
    )


def value_only_summary(value: int) -> dict[str, object]:
    if value <= 0:
        raise ValueError("value must be positive")
    return {"value": value}


def provenance_summary(value: int, strides: tuple[int, ...]) -> dict[str, object]:
    provenance = number_provenance(value)
    stride_views = tuple(stride_provenance(value, stride) for stride in strides)
    theorem_ids = tuple(sorted({theorem_id for view in stride_views for theorem_id in view.theorem_ids}))
    return {
        "value": provenance.value,
        "divisors": provenance.divisors,
        "factor_pairs": provenance.factor_pairs,
        "stride_views": stride_views,
        "theorem_ids": theorem_ids,
    }
