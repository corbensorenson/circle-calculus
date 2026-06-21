"""Finite phase-loop, vortex-charge, and phase-locking helpers.

This module gives executable counterparts for the Lean finite phase-loop
contracts. It treats loop charge, vortex charge, and closed-loop holonomy as
modular sums. Kuramoto-style helpers are limited to phase-locking and order
parameter diagnostics; they do not model oscillator dynamics or stability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import tau
from typing import Any, Iterable

from .circular_statistics import mean_resultant_length
from .winding import LiftedNode, lift


PHASE_LOOP_SCHEMA_ID = "circle_calculus.phase_loop_report.v0"

PHASE_LOOP_THEOREM_IDS: tuple[str, ...] = (
    "CC-T0161",
    "CC-T0162",
    "CC-T0163",
    "CC-T0164",
    "CC-T0165",
    "CC-T0166",
    "CC-T0167",
    "CC-T0168",
    "CC-T0169",
    "CC-T0170",
    "CC-T0171",
    "CC-T0172",
)

PHASE_LOOP_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.phaseLoopCharge_nil",
    "Circle.Applications.phaseLoopCharge_singleton",
    "Circle.Applications.phaseLoopCharge_append",
    "Circle.Applications.phaseLoopCharge_reverse",
    "Circle.Applications.vortexCharge_eq_phaseLoopCharge",
    "Circle.Applications.vortexCharge_reverse",
    "Circle.Applications.loopGaugeShiftedCharge_eq_phaseLoopCharge",
    "Circle.Applications.finitePhaseLocked_iff_gap_dvd",
    "Circle.Applications.finitePhaseLocked_refl",
    "Circle.Applications.finitePhaseLocked_symm",
    "Circle.Applications.finitePhaseLocked_trans",
    "Circle.Applications.windingResidueReconstruct_eq_value",
)

PHASE_LOOP_CLAIM_BOUNDARY = (
    "The proved claim is finite modular phase-loop bookkeeping: loop-charge "
    "sums, reversal negation, closed-loop endpoint-gauge cancellation, "
    "same-phase locking, and winding/residue reconstruction. This does not "
    "prove continuum vortices, Kuramoto dynamics, synchronization thresholds, "
    "physical stability, quantum holonomy, or model quality."
)


@dataclass(frozen=True)
class PhaseLoopReport:
    """Theorem-linked finite phase-loop diagnostic report."""

    schema_id: str
    period: int
    increments: tuple[int, ...]
    charge: int
    reverse_increments: tuple[int, ...]
    reverse_charge: int
    charge_plus_reverse: int
    closed_loop_gauge_shifted_charge: int
    closed_loop_gauge_invariant: bool
    charge_lift: LiftedNode
    charge_is_zero: bool
    theorem_ids: tuple[str, ...] = PHASE_LOOP_THEOREM_IDS
    lean_declarations: tuple[str, ...] = PHASE_LOOP_LEAN_DECLARATIONS
    claim_boundary: str = PHASE_LOOP_CLAIM_BOUNDARY
    references: tuple[str, ...] = (
        "https://aipp.silverchair-cdn.com/article-minimal/384529",
        "https://link.aps.org/doi/10.1103/PhysRevE.109.064203",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseLockReport:
    """Finite phase-locking and Kuramoto-style order-parameter diagnostic."""

    schema_id: str
    period: int
    phases: tuple[int, ...]
    locked_to_first: tuple[bool, ...]
    all_locked: bool
    order_parameter: float
    theorem_ids: tuple[str, ...] = PHASE_LOOP_THEOREM_IDS
    lean_declarations: tuple[str, ...] = PHASE_LOOP_LEAN_DECLARATIONS
    claim_boundary: str = PHASE_LOOP_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_positive_period(period: int) -> int:
    if not isinstance(period, int) or period <= 0:
        raise ValueError("period must be a positive integer")
    return period


def _require_int(name: str, value: int) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    return value


def _residue(period: int, value: int) -> int:
    return _require_int("value", value) % period


def normalize_phase_increments(
    period: int,
    increments: Iterable[int],
) -> tuple[int, ...]:
    """Return increments reduced modulo ``period``."""

    period = _require_positive_period(period)
    return tuple(_residue(period, increment) for increment in increments)


def phase_loop_charge(period: int, increments: Iterable[int]) -> int:
    """Return total finite loop charge as a modular sum."""

    period = _require_positive_period(period)
    return sum(normalize_phase_increments(period, increments)) % period


def vortex_charge(period: int, increments: Iterable[int]) -> int:
    """Alias for finite phase-loop charge with vortex vocabulary."""

    return phase_loop_charge(period, increments)


def reverse_phase_increments(
    period: int,
    increments: Iterable[int],
) -> tuple[int, ...]:
    """Reverse a finite phase path and negate each increment modulo period."""

    period = _require_positive_period(period)
    normalized = normalize_phase_increments(period, increments)
    return tuple((-increment) % period for increment in reversed(normalized))


def loop_gauge_shifted_charge(
    period: int,
    increments: Iterable[int],
    *,
    base_gauge: int = 0,
) -> int:
    """Return closed-loop endpoint-gauge-shifted charge.

    The same base gauge appears at the source and target, so the finite theorem
    says this equals ``phase_loop_charge``.
    """

    period = _require_positive_period(period)
    charge = phase_loop_charge(period, increments)
    gauge = _residue(period, base_gauge)
    return (charge + gauge - gauge) % period


def finite_phase_locked(period: int, left: int, right: int) -> bool:
    """Return whether two natural phase samples are equal modulo period."""

    period = _require_positive_period(period)
    if left < 0 or right < 0:
        raise ValueError("finite phase-locking samples must be nonnegative")
    return left % period == right % period


def finite_phase_gap(period: int, left: int, right: int) -> int:
    """Return the forward modular gap from ``left`` to ``right``."""

    period = _require_positive_period(period)
    if left < 0 or right < 0:
        raise ValueError("finite phase gap samples must be nonnegative")
    return (right - left) % period


def winding_residue_reconstruct(modulus: int, winding: int, residue: int) -> int:
    """Reconstruct a natural position from winding and residue."""

    if modulus <= 0:
        raise ValueError("modulus must be positive")
    if winding < 0:
        raise ValueError("winding must be nonnegative")
    if not 0 <= residue < modulus:
        raise ValueError("residue must satisfy 0 <= residue < modulus")
    return winding * modulus + residue


def loop_winding_lift(period: int, total_increment: int) -> LiftedNode:
    """Lift a nonnegative total increment into winding plus residue."""

    period = _require_positive_period(period)
    if total_increment < 0:
        raise ValueError("total_increment must be nonnegative")
    return lift(period, total_increment)


def phase_loop_report(
    period: int,
    increments: Iterable[int],
    *,
    base_gauge: int = 0,
) -> PhaseLoopReport:
    """Return a theorem-linked finite loop-charge report."""

    period = _require_positive_period(period)
    normalized = normalize_phase_increments(period, increments)
    charge = phase_loop_charge(period, normalized)
    reversed_increments = reverse_phase_increments(period, normalized)
    reverse_charge = phase_loop_charge(period, reversed_increments)
    total_increment = sum(normalized)
    return PhaseLoopReport(
        schema_id=PHASE_LOOP_SCHEMA_ID,
        period=period,
        increments=normalized,
        charge=charge,
        reverse_increments=reversed_increments,
        reverse_charge=reverse_charge,
        charge_plus_reverse=(charge + reverse_charge) % period,
        closed_loop_gauge_shifted_charge=loop_gauge_shifted_charge(
            period,
            normalized,
            base_gauge=base_gauge,
        ),
        closed_loop_gauge_invariant=loop_gauge_shifted_charge(
            period,
            normalized,
            base_gauge=base_gauge,
        )
        == charge,
        charge_lift=loop_winding_lift(period, total_increment),
        charge_is_zero=charge == 0,
    )


def phase_lock_report(period: int, phases: Iterable[int]) -> PhaseLockReport:
    """Return finite phase-lock and order-parameter diagnostics."""

    period = _require_positive_period(period)
    normalized = normalize_phase_increments(period, phases)
    if not normalized:
        raise ValueError("at least one phase is required")
    first = normalized[0]
    locked = tuple(finite_phase_locked(period, first, phase) for phase in normalized)
    order = mean_resultant_length(
        (phase / period * tau for phase in normalized),
        period=tau,
    )
    return PhaseLockReport(
        schema_id=PHASE_LOOP_SCHEMA_ID,
        period=period,
        phases=normalized,
        locked_to_first=locked,
        all_locked=all(locked),
        order_parameter=order,
    )


__all__ = [
    "PHASE_LOOP_CLAIM_BOUNDARY",
    "PHASE_LOOP_LEAN_DECLARATIONS",
    "PHASE_LOOP_SCHEMA_ID",
    "PHASE_LOOP_THEOREM_IDS",
    "PhaseLockReport",
    "PhaseLoopReport",
    "finite_phase_gap",
    "finite_phase_locked",
    "loop_gauge_shifted_charge",
    "loop_winding_lift",
    "normalize_phase_increments",
    "phase_lock_report",
    "phase_loop_charge",
    "phase_loop_report",
    "reverse_phase_increments",
    "vortex_charge",
    "winding_residue_reconstruct",
]
