from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiftedNode:
    """Full windings plus a residue for a positive modulus."""

    modulus: int
    winding: int
    residue: int

    def __post_init__(self) -> None:
        if self.modulus <= 0:
            raise ValueError("lifted nodes require a positive modulus")
        if self.winding < 0:
            raise ValueError("v0 natural windings require winding >= 0")
        if not 0 <= self.residue < self.modulus:
            raise ValueError("residue must satisfy 0 <= residue < modulus")

    @property
    def value(self) -> int:
        return self.winding * self.modulus + self.residue


def lift(modulus: int, value: int) -> LiftedNode:
    if modulus <= 0:
        raise ValueError("lift requires a positive modulus")
    if value < 0:
        raise ValueError("v0 natural lift requires value >= 0")
    winding, residue = divmod(value, modulus)
    return LiftedNode(modulus=modulus, winding=winding, residue=residue)


def lift_successor(modulus: int, value: int) -> LiftedNode:
    current = lift(modulus, value)
    carry, residue = divmod(current.residue + 1, modulus)
    return LiftedNode(
        modulus=modulus,
        winding=current.winding + carry,
        residue=residue,
    )


def lift_add(modulus: int, left: int, right: int) -> LiftedNode:
    left_lift = lift(modulus, left)
    right_lift = lift(modulus, right)
    carry, residue = divmod(left_lift.residue + right_lift.residue, modulus)
    return LiftedNode(
        modulus=modulus,
        winding=left_lift.winding + right_lift.winding + carry,
        residue=residue,
    )


def lift_iter_successor(modulus: int, value: int, steps: int) -> LiftedNode:
    if steps < 0:
        raise ValueError("v0 natural iteration requires steps >= 0")
    state = lift(modulus, value)
    winding = state.winding
    residue = state.residue
    for _ in range(steps):
        carry, residue = divmod(residue + 1, modulus)
        winding += carry
    return LiftedNode(modulus=modulus, winding=winding, residue=residue)
