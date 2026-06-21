import Mathlib.Data.Nat.ModEq
import Mathlib.Data.List.Count

/-!
# Finite circular statistics contracts

This module gives the exact finite residue layer behind circular statistics:
same-phase predicates, wrapped finite-circle distances, residue sample lists,
and residue histograms. Real-valued trigonometric statistics such as circular
means and resultant vectors are executable Python reference models; the proved
claims here are the integer modular facts they can cite.
-/

namespace Circle.Applications

/-! ### Same-phase and wrapped-distance predicates -/

/-- Two natural samples have the same finite circular phase when their residues
modulo the declared period are equal. -/
def circularSamePhase (period left right : Nat) : Prop :=
  left % period = right % period

/-- Forward wrapped distance from `left` to `right` on a finite circle. -/
def circularForwardDistance (period left right : Nat) : Nat :=
  (right + period - left) % period

/-- Backward wrapped distance from `left` to `right` on a finite circle. -/
def circularBackwardDistance (period left right : Nat) : Nat :=
  (left + period - right) % period

/-- The shorter of the forward and backward wrapped distances. -/
def wrappedCircularDistance (period left right : Nat) : Nat :=
  min (circularForwardDistance period left right)
    (circularBackwardDistance period left right)

/-- Ordered same-phase samples are exactly those whose gap is divisible by the
declared period. -/
theorem circularSamePhase_iff_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    circularSamePhase period left right ↔ period ∣ right - left := by
  unfold circularSamePhase
  exact Nat.modEq_iff_dvd' hleft

/-- Same-phase is reflexive. -/
theorem circularSamePhase_refl (period sample : Nat) :
    circularSamePhase period sample sample := by
  rfl

/-- Same-phase is symmetric. -/
theorem circularSamePhase_symm
    {period left right : Nat} :
    circularSamePhase period left right →
      circularSamePhase period right left := by
  intro hsame
  exact hsame.symm

/-- Same-phase is transitive. -/
theorem circularSamePhase_trans
    {period left middle right : Nat} :
    circularSamePhase period left middle →
      circularSamePhase period middle right →
        circularSamePhase period left right := by
  intro hleft hright
  exact Eq.trans hleft hright

/-- Wrapped circular distance is symmetric. -/
theorem wrappedCircularDistance_comm
    (period left right : Nat) :
    wrappedCircularDistance period left right =
      wrappedCircularDistance period right left := by
  unfold wrappedCircularDistance circularForwardDistance circularBackwardDistance
  exact Nat.min_comm _ _

/-- Wrapped circular distance is bounded by the forward distance. -/
theorem wrappedCircularDistance_le_forward
    (period left right : Nat) :
    wrappedCircularDistance period left right ≤
      circularForwardDistance period left right := by
  unfold wrappedCircularDistance
  exact Nat.min_le_left _ _

/-- Wrapped circular distance is bounded by the backward distance. -/
theorem wrappedCircularDistance_le_backward
    (period left right : Nat) :
    wrappedCircularDistance period left right ≤
      circularBackwardDistance period left right := by
  unfold wrappedCircularDistance
  exact Nat.min_le_right _ _

/-! ### Finite residue samples and histograms -/

/-- Map natural samples to their residues modulo a declared finite period. -/
def circularSampleResidues (period : Nat) (samples : List Nat) : List Nat :=
  samples.map (fun sample => sample % period)

/-- Count how many samples land in a declared residue. -/
def circularHistogram (period : Nat) (samples : List Nat) (residue : Nat) : Nat :=
  (circularSampleResidues period samples).count residue

/-- Every listed residue produced with a positive period is below the period. -/
theorem mem_circularSampleResidues_lt_period
    {period sample : Nat} {samples : List Nat}
    (hperiod : 0 < period)
    (hmem : sample ∈ circularSampleResidues period samples) :
    sample < period := by
  unfold circularSampleResidues at hmem
  rw [List.mem_map] at hmem
  rcases hmem with ⟨raw, _hraw, hsample⟩
  rw [← hsample]
  exact Nat.mod_lt raw hperiod

/-- A residue histogram count is bounded by the sample length. -/
theorem circularHistogram_le_length
    (period : Nat) (samples : List Nat) (residue : Nat) :
    circularHistogram period samples residue ≤ samples.length := by
  unfold circularHistogram circularSampleResidues
  simpa using
    (List.count_le_length :
      (samples.map (fun sample => sample % period)).count residue ≤
        (samples.map (fun sample => sample % period)).length)

/-- Residues outside a positive period have zero histogram count. -/
theorem circularHistogram_zero_of_period_le_residue
    {period residue : Nat} {samples : List Nat}
    (hperiod : 0 < period) (hresidue : period ≤ residue) :
    circularHistogram period samples residue = 0 := by
  unfold circularHistogram
  rw [List.count_eq_zero]
  intro hmem
  have hlt := mem_circularSampleResidues_lt_period (period := period) hperiod hmem
  exact not_lt_of_ge hresidue hlt

end Circle.Applications
