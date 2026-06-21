# Phase Loop, Winding, Vortex, And Locking Contracts

Claim boundary: this page proves finite modular phase-loop bookkeeping:
loop-charge sums, reversal negation, closed-loop endpoint-gauge cancellation,
same-phase locking, and winding/residue reconstruction. It does not prove
continuum vortices, Kuramoto dynamics, synchronization thresholds, physical
stability, quantum holonomy, or model quality.

## Motivation

Loop phases are one of the places where circle language becomes genuinely
useful: a path accumulates phase, a closed loop has holonomy, a winding count
records full turns, and a vortex-charge or loop-current diagnostic is a modular
sum around a cycle. In Kuramoto-style oscillator networks, the literature
connects phase-locked states with topological winding numbers and loop currents;
see Delabays, Coletta, and Jacquod on
[phase-locking and topological winding numbers](https://arxiv.org/abs/1512.04266)
and the journal version in
[Journal of Mathematical Physics](https://pubs.aip.org/aip/jmp/article/57/3/032701/384529/Multistability-of-phase-locking-and-topological).
Recent twisted-state work also studies Kuramoto oscillators arranged on a
circle, for example
[Physical Review E 109, 064203](https://link.aps.org/doi/10.1103/PhysRevE.109.064203).

Circle Calculus formalizes only the finite, reusable bookkeeping layer:

```text
loop_charge = sum(increments) mod period
reverse_loop_charge = -loop_charge
closed endpoint gauge shift = loop_charge + g(base) - g(base)
phase_locked(left, right) = left mod period = right mod period
position = winding * period + residue
```

## Lean Surface

The reusable proof source is:

```lean
import Circle.Applications.PhaseLoop
```

Stable public import:

```lean
import Circle.Applications.Public
```

Primary declarations:

- `Circle.Applications.phaseLoopCharge_nil`
- `Circle.Applications.phaseLoopCharge_singleton`
- `Circle.Applications.phaseLoopCharge_append`
- `Circle.Applications.phaseLoopCharge_reverse`
- `Circle.Applications.vortexCharge_eq_phaseLoopCharge`
- `Circle.Applications.vortexCharge_reverse`
- `Circle.Applications.loopGaugeShiftedCharge_eq_phaseLoopCharge`
- `Circle.Applications.finitePhaseLocked_iff_gap_dvd`
- `Circle.Applications.finitePhaseLocked_refl`
- `Circle.Applications.finitePhaseLocked_symm`
- `Circle.Applications.finitePhaseLocked_trans`
- `Circle.Applications.windingResidueReconstruct_eq_value`

The theorem ids are `CC-T0161` through `CC-T0172`.

## Python: Loop Charge

```python
from circle_math.core import phase_loop_report

report = phase_loop_report(12, [3, 4, 7], base_gauge=5)

print(report.charge)
print(report.reverse_increments)
print(report.reverse_charge)
print(report.charge_plus_reverse)
print(report.closed_loop_gauge_invariant)
print(report.charge_lift)
```

Expected shape:

```text
2
(5, 8, 9)
10
0
True
LiftedNode(modulus=12, winding=1, residue=2)
```

The report is useful for finite vortex-charge, loop-current, and holonomy
fixtures. The theorem-backed statement is only the modular arithmetic.

## Python: Phase Locking

```python
from circle_math.core import phase_lock_report

locked = phase_lock_report(12, [1, 13, 25])
opposite = phase_lock_report(12, [0, 6])

print(locked.all_locked)
print(locked.order_parameter)
print(opposite.all_locked)
print(opposite.order_parameter)
```

The `all_locked` field is theorem-facing finite same-phase equality. The
`order_parameter` field is an executable circular-statistics diagnostic; it is
not a theorem about Kuramoto dynamics.

## What To Reuse

Use this module when a concept is a finite phase loop:

1. Encode increments as integer residues modulo a declared period.
2. Use `phase_loop_report` for loop charge, reverse charge, and closed-loop
   gauge-shift cancellation.
3. Use `phase_lock_report` for finite same-phase and order-parameter fixtures.
4. Cite `CC-T0161` through `CC-T0172` only for the finite modular claims.
5. Keep dynamics, stability, continuum topology, quantum phase, and physical
   interpretation outside the proof boundary until separate models exist.
