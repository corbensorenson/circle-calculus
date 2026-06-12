import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Real.Basic

/-!
# Proof-carrying RoPE position distinguishability contracts

This file is the formal spine for the public RoPE certifier. It deliberately
models the exact/discretized contract first: each rotary channel is represented
by a finite period, and a position is visible through its residue modulo that
period.

Real RoPE uses real-valued phases. Exact equality of real phases is therefore
not the right first claim for an engineering certifier. The checked theorem
here is the exact finite contract that a discretized/rational phase policy can
cite: two positions collide in every declared phase channel exactly when every
declared period divides their position gap.
-/

namespace Circle.Applications

/-! ### Single discrete RoPE channel -/

/-- The exact finite phase seen by one discretized RoPE channel. -/
def ropeDiscretePhase (period position : Nat) : Nat :=
  position % period

/-- Two positions collide in one discretized RoPE channel when they have the
same residue modulo that channel's period. -/
def ropeDiscreteCollision (period left right : Nat) : Prop :=
  ropeDiscretePhase period left = ropeDiscretePhase period right

/-- A single discretized RoPE channel distinguishes two positions when they do
not collide in that channel. -/
def ropeDiscreteDistinguishable (period left right : Nat) : Prop :=
  ¬ ropeDiscreteCollision period left right

/-- Exact single-channel collision criterion: for ordered positions, equality
of residues modulo the channel period is equivalent to the period dividing the
position gap. -/
theorem ropeDiscreteCollision_iff_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    ropeDiscreteCollision period left right ↔ period ∣ right - left := by
  unfold ropeDiscreteCollision ropeDiscretePhase
  exact Nat.modEq_iff_dvd' hleft

/-- Exact single-channel distinguishability criterion. -/
theorem ropeDiscreteDistinguishable_iff_not_gap_dvd
    {period left right : Nat} (hleft : left ≤ right) :
    ropeDiscreteDistinguishable period left right ↔ ¬ period ∣ right - left := by
  unfold ropeDiscreteDistinguishable
  rw [ropeDiscreteCollision_iff_gap_dvd hleft]

/-- If the inspected context fits inside one period, that channel is injective
on the context range: residue collision is exactly position equality. -/
theorem ropeDiscreteCollision_iff_eq_on_context
    {period context left right : Nat}
    (hcontext : context ≤ period) (hleft : left < context) (hright : right < context) :
    ropeDiscreteCollision period left right ↔ left = right := by
  unfold ropeDiscreteCollision ropeDiscretePhase
  have hleft_period : left < period := lt_of_lt_of_le hleft hcontext
  have hright_period : right < period := lt_of_lt_of_le hright hcontext
  rw [Nat.mod_eq_of_lt hleft_period, Nat.mod_eq_of_lt hright_period]

/-! ### Finite phase-bank contract -/

/-- A finite discretized RoPE bank collides when every declared channel period
collides. -/
def ropePhaseBankCollision (periods : List Nat) (left right : Nat) : Prop :=
  ∀ period, period ∈ periods → ropeDiscreteCollision period left right

/-- A finite discretized RoPE bank distinguishes two positions when at least
one declared channel period distinguishes them. -/
def ropePhaseBankDistinguishable (periods : List Nat) (left right : Nat) : Prop :=
  ∃ period, period ∈ periods ∧ ropeDiscreteDistinguishable period left right

/-- Exact finite-bank collision criterion: an ordered pair collides in every
declared channel iff every declared period divides the position gap. -/
theorem ropePhaseBankCollision_iff_forall_gap_dvd
    {periods : List Nat} {left right : Nat} (hleft : left ≤ right) :
    ropePhaseBankCollision periods left right ↔
      ∀ period, period ∈ periods → period ∣ right - left := by
  constructor
  · intro hcollision period hmem
    exact (ropeDiscreteCollision_iff_gap_dvd (period := period) hleft).1
      (hcollision period hmem)
  · intro hdivides period hmem
    exact (ropeDiscreteCollision_iff_gap_dvd (period := period) hleft).2
      (hdivides period hmem)

/-- Exact finite-bank distinguishability criterion: an ordered pair is
distinguished by the phase bank iff some declared period does not divide the
position gap. -/
theorem ropePhaseBankDistinguishable_iff_exists_not_gap_dvd
    {periods : List Nat} {left right : Nat} (hleft : left ≤ right) :
    ropePhaseBankDistinguishable periods left right ↔
      ∃ period, period ∈ periods ∧ ¬ period ∣ right - left := by
  unfold ropePhaseBankDistinguishable ropeDiscreteDistinguishable
  constructor
  · rintro ⟨period, hmem, hdistinguish⟩
    exact ⟨period, hmem,
      mt (ropeDiscreteCollision_iff_gap_dvd (period := period) hleft).2 hdistinguish⟩
  · rintro ⟨period, hmem, hnotdvd⟩
    exact ⟨period, hmem,
      mt (ropeDiscreteCollision_iff_gap_dvd (period := period) hleft).1 hnotdvd⟩

/-- If a phase bank contains a period at least as large as the inspected
context, then that bank distinguishes every unequal pair inside the context. -/
theorem ropePhaseBankDistinguishable_of_period_ge_context
    {periods : List Nat} {period context left right : Nat}
    (hmem : period ∈ periods) (hcontext : context ≤ period)
    (hleft : left < context) (hright : right < context) (hne : left ≠ right) :
    ropePhaseBankDistinguishable periods left right := by
  refine ⟨period, hmem, ?_⟩
  unfold ropeDiscreteDistinguishable
  intro hcollision
  exact hne ((ropeDiscreteCollision_iff_eq_on_context hcontext hleft hright).1 hcollision)

/-! ### Collision-counting seed -/

/-- The number of ordered start positions whose paired position is exactly
`gap` steps ahead inside a context. When `gap < context`, these are the pairs
`(0,gap)`, `(1,1+gap)`, ..., `(context-gap-1, context-1)`. -/
def ropeCollisionPairCountAtGap (context gap : Nat) : Nat :=
  context - gap

/-- There is at least one ordered pair separated by `gap` inside a context iff
the gap is strictly smaller than the context. -/
theorem ropeCollisionPairCountAtGap_pos_iff {context gap : Nat} :
    0 < ropeCollisionPairCountAtGap context gap ↔ gap < context := by
  unfold ropeCollisionPairCountAtGap
  exact Nat.sub_pos_iff_lt

/-- If every declared period divides a gap, then every start counted by
`ropeCollisionPairCountAtGap context gap` gives a colliding pair in the phase
bank. This is a theorem-backed collision-counting seed: the count is not yet
the total number of all colliding pairs, but it is a certified family of that
many all-channel collisions at the declared common gap. -/
theorem ropePhaseBankCollision_at_gap_of_forall_dvd
    {periods : List Nat} {context gap start : Nat}
    (hdivides : ∀ period, period ∈ periods → period ∣ gap)
    (hstart : start < ropeCollisionPairCountAtGap context gap) :
    ropePhaseBankCollision periods start (start + gap) ∧ start + gap < context := by
  have hleft : start ≤ start + gap := Nat.le_add_right start gap
  have hgap : start + gap - start = gap := Nat.add_sub_cancel_left start gap
  refine ⟨?_, Nat.add_lt_of_lt_sub hstart⟩
  exact (ropePhaseBankCollision_iff_forall_gap_dvd (periods := periods) hleft).2
    (by
      intro period hmem
      simpa [hgap] using hdivides period hmem)

/-! ### Real phase-margin precursor -/

/-- The unwrapped real-valued phase gap for one RoPE channel frequency.

This is not yet the circular distance modulo a full turn. It is the first
formal real-valued object needed before a Diophantine/circular-margin theorem
can replace the current numerical scan. -/
def ropeRealPhaseGap (frequency : ℝ) (left right : Nat) : ℝ :=
  ((right : ℝ) - (left : ℝ)) * frequency

/-- Absolute unwrapped real-valued phase gap for one channel frequency. -/
def ropeRealPhaseGapAbs (frequency : ℝ) (left right : Nat) : ℝ :=
  |ropeRealPhaseGap frequency left right|

/-- For ordered positions, the absolute unwrapped real phase gap is exactly
the natural position gap times the absolute frequency. -/
theorem ropeRealPhaseGapAbs_eq_natGap_mul_abs
    {frequency : ℝ} {left right : Nat} (hleft : left ≤ right) :
    ropeRealPhaseGapAbs frequency left right =
      ((right - left : Nat) : ℝ) * |frequency| := by
  unfold ropeRealPhaseGapAbs ropeRealPhaseGap
  rw [← Nat.cast_sub hleft, abs_mul, abs_of_nonneg (Nat.cast_nonneg _)]

/-- A simple quantitative precursor: if the inspected position gap is at least
`minGap` and the channel frequency has absolute value at least `lower`, then
the unwrapped absolute phase gap is at least `minGap * lower`.

This is an unwrapped lower bound only. It is not a circular modulo-full-turn
margin theorem and should not be cited as one. -/
theorem ropeRealPhaseGapAbs_ge_minGap_mul_lower
    {frequency lower : ℝ} {left right minGap : Nat}
    (hleft : left ≤ right) (hgap : minGap ≤ right - left)
    (hlower_nonneg : 0 ≤ lower) (hlower : lower ≤ |frequency|) :
    (minGap : ℝ) * lower ≤ ropeRealPhaseGapAbs frequency left right := by
  rw [ropeRealPhaseGapAbs_eq_natGap_mul_abs (frequency := frequency) hleft]
  have hgap_real : (minGap : ℝ) ≤ ((right - left : Nat) : ℝ) := by
    exact Nat.cast_le.mpr hgap
  exact mul_le_mul hgap_real hlower hlower_nonneg (Nat.cast_nonneg _)

end Circle.Applications
