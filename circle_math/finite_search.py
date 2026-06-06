"""Finite-coil theorem signature helpers.

This is a bounded search fixture for S1 theorem navigation. It is not a
general theorem prover or a global theorem-discovery result.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable


@dataclass(frozen=True)
class FiniteCoilSignature:
    size: int
    stride: int
    gcd: int
    period: int
    orbit_count: int
    full_coil: bool


THEOREM_SIGNATURES: dict[str, tuple[str, ...]] = {
    "CC-T0005": ("period", "gcd", "finite-coil"),
    "CC-T0006": ("orbit-count", "gcd", "finite-coil"),
    "CC-T0007": ("full-coil", "prime", "coprime"),
    "CC-T0030": ("period", "divisibility", "scaling"),
    "CC-T0034": ("period", "normal-form", "scaling"),
    "CC-T0035": ("period", "congruence", "scaling"),
    "CC-T0042": ("kernel-cardinality", "gcd", "scaling"),
    "CC-T0044": ("fiber-cardinality", "gcd", "scaling"),
    "CC-T0049": ("image-times-kernel", "gcd", "scaling"),
    "CC-T0054": ("full-coil", "coprime", "finite-coil"),
    "CC-T0055": ("same-orbit", "orbit-quotient", "finite-coil"),
    "CC-T0059": ("same-orbit", "gcd-congruence", "finite-coil"),
    "CC-T0060": ("same-orbit", "gcd-congruence", "finite-coil"),
    "CC-T0061": ("same-orbit", "gcd-congruence", "finite-coil"),
}


def finite_coil_signature(size: int, stride: int) -> FiniteCoilSignature:
    """Return the gcd/period/orbit signature for a finite-circle stride."""
    if size <= 0:
        raise ValueError("size must be positive")
    divisor = gcd(size, stride)
    period = size // divisor
    return FiniteCoilSignature(
        size=size,
        stride=stride,
        gcd=divisor,
        period=period,
        orbit_count=divisor,
        full_coil=divisor == 1,
    )


def signature_tags(signature: FiniteCoilSignature) -> tuple[str, ...]:
    """Convert a finite-coil signature into searchable theorem tags."""
    tags = [
        "finite-coil",
        "period",
        "gcd",
        "orbit-count",
        "full-coil" if signature.full_coil else "partial-coil",
        "coprime" if signature.full_coil else "noncoprime",
    ]
    return tuple(tags)


def build_s1_signature_index(theorem_signatures: dict[str, tuple[str, ...]] = THEOREM_SIGNATURES) -> dict[str, tuple[str, ...]]:
    """Build a tag-to-theorem-id index for the bounded S1 fixture."""
    index: dict[str, set[str]] = {}
    for theorem_id, tags in theorem_signatures.items():
        for tag in tags:
            index.setdefault(tag, set()).add(theorem_id)
    return {tag: tuple(sorted(theorem_ids)) for tag, theorem_ids in sorted(index.items())}


def search_theorems_by_tags(tags: Iterable[str]) -> tuple[str, ...]:
    """Return theorem ids matching all requested tags."""
    index = build_s1_signature_index()
    requested = tuple(tags)
    if not requested:
        return tuple()
    matches = set(index.get(requested[0], ()))
    for tag in requested[1:]:
        matches.intersection_update(index.get(tag, ()))
    return tuple(sorted(matches))
