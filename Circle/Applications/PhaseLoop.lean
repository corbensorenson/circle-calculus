import Circle.Applications.CircularStatistics
import Circle.Core.Winding
import Circle.Physics.LatticeGauge

/-!
# Finite phase-loop, vortex-charge, and locking contracts

This module packages finite modular phase bookkeeping for winding, loop
holonomy, vortex-charge-style sums, and Kuramoto-style phase locking. The proved
claims are exact `ZMod`/`Nat` identities only. They do not assert a continuum
field theory, physical vortex dynamics, oscillator stability, or synchronization
threshold.
-/

namespace Circle.Applications

/-- Total modular phase around a finite loop. -/
def phaseLoopCharge (increments : List (ZMod n)) : ZMod n :=
  Circle.Physics.pathHolonomy increments

/-- Vortex-charge vocabulary for the same finite modular loop sum. -/
def vortexCharge (increments : List (ZMod n)) : ZMod n :=
  phaseLoopCharge increments

/-- Closed-loop endpoint gauge shift: source and target gauges are the same. -/
def loopGaugeShiftedCharge
    (increments : List (ZMod n)) (baseGauge : ZMod n) : ZMod n :=
  Circle.Physics.gaugeTransformHolonomy
    { phases := increments, sourceGauge := baseGauge, targetGauge := baseGauge }

/-- Empty loops have zero finite phase-loop charge. -/
theorem phaseLoopCharge_nil :
    phaseLoopCharge ([] : List (ZMod n)) = 0 := by
  simp [phaseLoopCharge, Circle.Physics.pathHolonomy]

/-- A one-edge loop charge is the edge phase itself. -/
theorem phaseLoopCharge_singleton (phase : ZMod n) :
    phaseLoopCharge [phase] = phase := by
  simp [phaseLoopCharge, Circle.Physics.pathHolonomy]

/-- Finite phase-loop charge is additive under path concatenation. -/
theorem phaseLoopCharge_append
    (left right : List (ZMod n)) :
    phaseLoopCharge (left ++ right) =
      phaseLoopCharge left + phaseLoopCharge right := by
  exact Circle.Physics.pathHolonomy_concat left right

/-- Reversing a finite phase loop negates its loop charge. -/
theorem phaseLoopCharge_reverse (increments : List (ZMod n)) :
    phaseLoopCharge (Circle.Physics.reversePhases increments) =
      - phaseLoopCharge increments := by
  exact Circle.Physics.pathHolonomy_reverse increments

/-- Vortex charge is exactly the finite phase-loop charge in this module. -/
theorem vortexCharge_eq_phaseLoopCharge
    (increments : List (ZMod n)) :
    vortexCharge increments = phaseLoopCharge increments := by
  rfl

/-- Reversing a finite vortex loop negates its charge. -/
theorem vortexCharge_reverse (increments : List (ZMod n)) :
    vortexCharge (Circle.Physics.reversePhases increments) =
      - vortexCharge increments := by
  exact phaseLoopCharge_reverse increments

/-- A closed endpoint gauge shift leaves finite loop charge unchanged. -/
theorem loopGaugeShiftedCharge_eq_phaseLoopCharge
    (increments : List (ZMod n)) (baseGauge : ZMod n) :
    loopGaugeShiftedCharge increments baseGauge =
      phaseLoopCharge increments := by
  simp [loopGaugeShiftedCharge, phaseLoopCharge,
    Circle.Physics.gaugeTransformHolonomy]

/-- Finite phase locking is same-phase equality modulo a declared period. -/
def finitePhaseLocked (period left right : Nat) : Prop :=
  circularSamePhase period left right

/-- Ordered finite phase locking is equivalent to period divisibility of the
phase gap. -/
theorem finitePhaseLocked_iff_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    finitePhaseLocked period left right ↔ period ∣ right - left := by
  exact circularSamePhase_iff_gap_dvd hleft

/-- Finite phase locking is reflexive. -/
theorem finitePhaseLocked_refl (period sample : Nat) :
    finitePhaseLocked period sample sample := by
  exact circularSamePhase_refl period sample

/-- Finite phase locking is symmetric. -/
theorem finitePhaseLocked_symm
    {period left right : Nat} :
    finitePhaseLocked period left right →
      finitePhaseLocked period right left := by
  exact circularSamePhase_symm

/-- Finite phase locking is transitive. -/
theorem finitePhaseLocked_trans
    {period left middle right : Nat} :
    finitePhaseLocked period left middle →
      finitePhaseLocked period middle right →
        finitePhaseLocked period left right := by
  exact circularSamePhase_trans

/-- Reconstruct a natural phase position from winding and residue. -/
def windingResidueReconstruct
    (modulus winding residue : Nat) : Nat :=
  winding * modulus + residue

/-- A `LiftedNode` reconstructs exactly by winding times modulus plus residue. -/
theorem windingResidueReconstruct_eq_value
    (node : Circle.LiftedNode) :
    windingResidueReconstruct node.modulus node.winding node.residue =
      node.value := by
  rfl

end Circle.Applications
