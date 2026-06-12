import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Int.Cast.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith

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

/-- If every declared period divides a common gap, then every positive multiple
of that common gap also gives a certified all-channel collision family while
the paired endpoint remains inside the inspected context.

This extends the common-gap count from one gap to every in-context multiple of
the common gap. It is still a guaranteed-family theorem, not a total collision
count over all possible gaps. -/
theorem ropePhaseBankCollision_at_commonGap_mul_of_forall_dvd
    {periods : List Nat} {context commonGap multiple start : Nat}
    (hdivides : ∀ period, period ∈ periods → period ∣ commonGap)
    (_hmultiple : 0 < multiple)
    (hstart : start < ropeCollisionPairCountAtGap context (multiple * commonGap)) :
    ropePhaseBankCollision periods start (start + multiple * commonGap) ∧
      start + multiple * commonGap < context := by
  refine ropePhaseBankCollision_at_gap_of_forall_dvd
    (periods := periods) (context := context) (gap := multiple * commonGap)
    (start := start) ?_ hstart
  intro period hmem
  simpa [Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc] using
    dvd_mul_of_dvd_right (hdivides period hmem) multiple

/-- In a single positive-period channel, every in-context collision between
unequal ordered positions has a positive period-multiple gap.

This is the converse direction needed by exact single-period collision counts:
the only gaps that can contribute are `period`, `2 * period`, `3 * period`,
and so on while the paired endpoint remains inside the context. -/
theorem ropeDiscreteCollision_exists_positive_multiple_gap
    {period context left right : Nat}
    (_hperiod : 0 < period) (hleft : left < right) (hright : right < context)
    (hcollision : ropeDiscreteCollision period left right) :
    ∃ multiple, 0 < multiple ∧ right = left + multiple * period ∧
      multiple * period < context := by
  have hle : left ≤ right := Nat.le_of_lt hleft
  have hdvd : period ∣ right - left :=
    (ropeDiscreteCollision_iff_gap_dvd (period := period) hle).1 hcollision
  rcases hdvd with ⟨multiple, hgap_raw⟩
  have hgap : right - left = multiple * period := by
    simpa [Nat.mul_comm] using hgap_raw
  have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
  have hmultiple_pos : 0 < multiple := by
    by_contra hnot
    have hzero : multiple = 0 := Nat.eq_zero_of_not_pos hnot
    have hgap_zero : right - left = 0 := by
      simpa [hzero] using hgap
    exact (Nat.ne_of_gt hgap_pos) hgap_zero
  have hright_eq' : right = multiple * period + left :=
    Nat.eq_add_of_sub_eq hle hgap
  have hright_eq : right = left + multiple * period := by
    simpa [Nat.add_comm, Nat.add_left_comm, Nat.add_assoc] using hright_eq'
  refine ⟨multiple, hmultiple_pos, hright_eq, ?_⟩
  have hgap_le_right : multiple * period ≤ right := by
    rw [hright_eq]
    exact Nat.le_add_left (multiple * period) left
  exact lt_of_le_of_lt hgap_le_right hright

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

/-- Error between the nonnegative unwrapped phase magnitude and a chosen
nonnegative full-turn multiple.

This is still not a completed circular-distance theorem. It is a reusable
object for reducing one-turn phase-window claims to ordinary real inequalities.
-/
def ropeRealPhaseNatTurnError
    (frequency fullTurn : ℝ) (left right turns : Nat) : ℝ :=
  |ropeRealPhaseGapAbs frequency left right - (turns : ℝ) * fullTurn|

/-- Error between the nonnegative unwrapped phase magnitude and a signed
full-turn multiple.

This is the real-valued object needed before stating a nearest-integer
circular-margin theorem. -/
def ropeRealPhaseIntTurnError
    (frequency fullTurn : ℝ) (left right : Nat) (turns : Int) : ℝ :=
  |ropeRealPhaseGapAbs frequency left right - (turns : ℝ) * fullTurn|

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

/-- One-turn-window endpoint lower-bound transfer.

If the unwrapped phase magnitude lies inside one declared turn and stays at
least `margin` away from both endpoints of that turn, then it is at least
`margin` away from the zero-turn and one-turn endpoints. This is still a
generic real-inequality precursor, not a Diophantine theorem and not a
formal certification of the numerical RoPE scan. -/
theorem ropeRealPhaseNatTurnEndpointErrors_ge_margin_of_one_turn_window
    {frequency fullTurn margin : ℝ} {left right : Nat}
    (hphase_le_full : ropeRealPhaseGapAbs frequency left right ≤ fullTurn)
    (hleft_margin : margin ≤ ropeRealPhaseGapAbs frequency left right)
    (hright_margin : margin ≤ fullTurn - ropeRealPhaseGapAbs frequency left right) :
    margin ≤ ropeRealPhaseNatTurnError frequency fullTurn left right 0 ∧
      margin ≤ ropeRealPhaseNatTurnError frequency fullTurn left right 1 := by
  unfold ropeRealPhaseNatTurnError
  constructor
  · rw [Nat.cast_zero, zero_mul, sub_zero, abs_of_nonneg]
    exact hleft_margin
    unfold ropeRealPhaseGapAbs
    exact abs_nonneg _
  · rw [Nat.cast_one, one_mul, abs_of_nonpos (sub_nonpos.mpr hphase_le_full), neg_sub]
    exact hright_margin

/-- One-turn-window lower-bound transfer for all nonnegative full-turn
multiples.

If the unwrapped phase magnitude lies inside one declared turn and stays at
least `margin` away from both endpoints of that turn, then it is at least
`margin` away from every nonnegative full-turn multiple. This is a generic
real-inequality precursor; it still does not prove the nearest-integer or
Diophantine theorem needed for a full real RoPE circular-margin certificate. -/
theorem ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window
    {frequency fullTurn margin : ℝ} {left right turns : Nat}
    (hfull_nonneg : 0 ≤ fullTurn)
    (hphase_le_full : ropeRealPhaseGapAbs frequency left right ≤ fullTurn)
    (hleft_margin : margin ≤ ropeRealPhaseGapAbs frequency left right)
    (hright_margin : margin ≤ fullTurn - ropeRealPhaseGapAbs frequency left right) :
    margin ≤ ropeRealPhaseNatTurnError frequency fullTurn left right turns := by
  unfold ropeRealPhaseNatTurnError
  cases turns with
  | zero =>
      rw [Nat.cast_zero, zero_mul, sub_zero, abs_of_nonneg]
      exact hleft_margin
      unfold ropeRealPhaseGapAbs
      exact abs_nonneg _
  | succ turnTail =>
      cases turnTail with
      | zero =>
          rw [Nat.cast_one, one_mul, abs_of_nonpos (sub_nonpos.mpr hphase_le_full), neg_sub]
          exact hright_margin
      | succ turnTail =>
          have hcoef : (1 : ℝ) ≤ (Nat.succ (Nat.succ turnTail) : ℝ) := by
            simpa using (Nat.cast_le (α := ℝ)).mpr
              (Nat.succ_le_succ (Nat.zero_le (Nat.succ turnTail)))
          have hfull_le_turn :
              fullTurn ≤ (Nat.succ (Nat.succ turnTail) : ℝ) * fullTurn := by
            calc
              fullTurn = (1 : ℝ) * fullTurn := by rw [one_mul]
              _ ≤ (Nat.succ (Nat.succ turnTail) : ℝ) * fullTurn :=
                mul_le_mul_of_nonneg_right hcoef hfull_nonneg
          rw [abs_of_nonpos]
          · linarith
          · linarith

/-- One-turn-window lower-bound transfer for all signed full-turn multiples.

If the unwrapped phase magnitude lies inside one declared turn and stays at
least `margin` away from both endpoints of that turn, then it is at least
`margin` away from every signed full-turn multiple. Negative full-turn multiples
are handled by the zero-turn endpoint bound; nonnegative multiples are handled
by `ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window`.

This is still a local one-turn-window theorem. It does not yet provide the
Diophantine/continued-fraction lower bound needed to prove that arbitrary RoPE
gaps actually satisfy the window hypotheses. -/
theorem ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window
    {frequency fullTurn margin : ℝ} {left right : Nat} {turns : Int}
    (hfull_nonneg : 0 ≤ fullTurn)
    (hphase_le_full : ropeRealPhaseGapAbs frequency left right ≤ fullTurn)
    (hleft_margin : margin ≤ ropeRealPhaseGapAbs frequency left right)
    (hright_margin : margin ≤ fullTurn - ropeRealPhaseGapAbs frequency left right) :
    margin ≤ ropeRealPhaseIntTurnError frequency fullTurn left right turns := by
  unfold ropeRealPhaseIntTurnError
  cases turns with
  | ofNat turnsNat =>
      simpa [ropeRealPhaseNatTurnError] using
        (ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window
          (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
          (left := left) (right := right) (turns := turnsNat)
          hfull_nonneg hphase_le_full hleft_margin hright_margin)
  | negSucc turnsNat =>
      have hphase_nonneg : 0 ≤ ropeRealPhaseGapAbs frequency left right := by
        unfold ropeRealPhaseGapAbs
        exact abs_nonneg _
      have hcoef_nonpos : ((Int.negSucc turnsNat : Int) : ℝ) ≤ 0 := by
        rw [Int.cast_negSucc]
        exact neg_nonpos.mpr (Nat.cast_nonneg _)
      have hturn_mul_nonpos :
          ((Int.negSucc turnsNat : Int) : ℝ) * fullTurn ≤ 0 :=
        mul_nonpos_of_nonpos_of_nonneg hcoef_nonpos hfull_nonneg
      rw [abs_of_nonneg]
      · linarith
      · linarith

end Circle.Applications
