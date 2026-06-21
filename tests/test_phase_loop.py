from __future__ import annotations

from math import isclose

from circle_math.core import (
    PHASE_LOOP_THEOREM_IDS,
    finite_phase_gap,
    finite_phase_locked,
    loop_gauge_shifted_charge,
    loop_winding_lift,
    phase_lock_report,
    phase_loop_charge,
    phase_loop_report,
    reverse_phase_increments,
    vortex_charge,
    winding_residue_reconstruct,
)


def test_phase_loop_charge_and_reverse_negation() -> None:
    increments = [3, 4, 7]
    assert phase_loop_charge(12, increments) == 2
    assert vortex_charge(12, increments) == 2
    assert reverse_phase_increments(12, increments) == (5, 8, 9)
    assert phase_loop_charge(12, reverse_phase_increments(12, increments)) == 10
    assert (phase_loop_charge(12, increments) + phase_loop_charge(12, reverse_phase_increments(12, increments))) % 12 == 0


def test_closed_loop_gauge_shifted_charge_matches_loop_charge() -> None:
    increments = [3, 4, 7]
    assert loop_gauge_shifted_charge(12, increments, base_gauge=5) == 2
    report = phase_loop_report(12, increments, base_gauge=5)
    assert report.schema_id == "circle_calculus.phase_loop_report.v0"
    assert report.theorem_ids == PHASE_LOOP_THEOREM_IDS
    assert report.charge == 2
    assert report.reverse_charge == 10
    assert report.charge_plus_reverse == 0
    assert report.closed_loop_gauge_shifted_charge == report.charge
    assert report.closed_loop_gauge_invariant is True
    assert report.charge_lift.winding == 1
    assert report.charge_lift.residue == 2


def test_finite_phase_locking_and_gap() -> None:
    assert finite_phase_locked(12, 1, 25) is True
    assert finite_phase_locked(12, 1, 26) is False
    assert finite_phase_gap(12, 1, 25) == 0
    assert finite_phase_gap(12, 1, 26) == 1


def test_winding_residue_reconstruction_and_lift() -> None:
    assert winding_residue_reconstruct(5, 3, 2) == 17
    lifted = loop_winding_lift(5, 17)
    assert lifted.winding == 3
    assert lifted.residue == 2
    assert winding_residue_reconstruct(lifted.modulus, lifted.winding, lifted.residue) == lifted.value


def test_phase_lock_report_order_parameter() -> None:
    locked = phase_lock_report(12, [1, 13, 25])
    assert locked.all_locked is True
    assert locked.locked_to_first == (True, True, True)
    assert isclose(locked.order_parameter, 1.0)

    opposite = phase_lock_report(12, [0, 6])
    assert opposite.all_locked is False
    assert opposite.order_parameter < 1e-12
