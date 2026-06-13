import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Int.Cast.Basic
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Analysis.Real.Pi.Bounds
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
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

/-- The least common multiple of a finite integer-period RoPE bank.

For the empty bank this is `1`, matching the vacuous all-channel collision
predicate: every positive gap is a collision when no periods are declared. -/
def ropePeriodBankLCM : List Nat → Nat
  | [] => 1
  | period :: rest => Nat.lcm period (ropePeriodBankLCM rest)

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

/-- Every declared period divides the period-bank LCM. -/
theorem ropePeriodBankLCM_dvd_of_mem
    {periods : List Nat} {period : Nat} (hmem : period ∈ periods) :
    period ∣ ropePeriodBankLCM periods := by
  induction periods with
  | nil =>
      simp at hmem
  | cons head rest ih =>
      simp [List.mem_cons] at hmem
      rcases hmem with hhead | hrest
      · subst period
        exact Nat.dvd_lcm_left head (ropePeriodBankLCM rest)
      · exact Nat.dvd_trans (ih hrest) (Nat.dvd_lcm_right head (ropePeriodBankLCM rest))

/-- If every declared period divides a gap, then the period-bank LCM divides
that gap. -/
theorem ropePeriodBankLCM_dvd_of_forall_dvd
    {periods : List Nat} {gap : Nat}
    (hdivides : ∀ period, period ∈ periods → period ∣ gap) :
    ropePeriodBankLCM periods ∣ gap := by
  induction periods with
  | nil =>
      simp [ropePeriodBankLCM]
  | cons head rest ih =>
      simpa [ropePeriodBankLCM] using Nat.lcm_dvd
        (hdivides head (by simp))
        (ih (by
          intro period hmem
          exact hdivides period (by simp [hmem])))

/-- Exact finite-bank collision criterion compressed to one LCM divisibility
test. This is the theorem that upgrades common-gap counting into total
integer-period bank collision counting: after sorting pairs by positive gap,
only positive multiples of `ropePeriodBankLCM periods` can collide in every
declared channel, and every such multiple does collide. -/
theorem ropePhaseBankCollision_iff_lcm_dvd_gap
    {periods : List Nat} {left right : Nat} (hleft : left ≤ right) :
    ropePhaseBankCollision periods left right ↔
      ropePeriodBankLCM periods ∣ right - left := by
  rw [ropePhaseBankCollision_iff_forall_gap_dvd (periods := periods) hleft]
  constructor
  · intro hdivides
    exact ropePeriodBankLCM_dvd_of_forall_dvd hdivides
  · intro hlcm period hmem
    exact Nat.dvd_trans (ropePeriodBankLCM_dvd_of_mem hmem) hlcm

/-- Every in-context start paired with the period-bank LCM gap is an
all-channel collision.

This is the exact fail-side companion to the LCM pass condition: when the LCM
is below the requested context, the certifier can cite this theorem for the
reported collision family rather than treating the family as a brute-force
observation. -/
theorem ropePhaseBankCollision_at_lcm_gap
    {periods : List Nat} {context start : Nat}
    (hstart : start < ropeCollisionPairCountAtGap context (ropePeriodBankLCM periods)) :
    ropePhaseBankCollision periods start (start + ropePeriodBankLCM periods) ∧
      start + ropePeriodBankLCM periods < context := by
  exact ropePhaseBankCollision_at_gap_of_forall_dvd
    (periods := periods) (context := context) (gap := ropePeriodBankLCM periods)
    (start := start) (fun period hmem => ropePeriodBankLCM_dvd_of_mem hmem) hstart

/-- If the period-bank LCM is positive and smaller than the inspected context,
then the integer-period bank has an explicit unequal all-channel collision
witness inside the context.

Together with `not_ropePhaseBankCollision_of_lcm_ge_context`, this gives the
certifier a two-sided exact LCM contract: reaching the context proves no
unequal in-context all-channel collisions; falling short produces a checked
collision witness. -/
theorem ropePhaseBankCollision_exists_of_lcm_pos_lt_context
    {periods : List Nat} {context : Nat}
    (hlcm_pos : 0 < ropePeriodBankLCM periods)
    (hlcm_lt_context : ropePeriodBankLCM periods < context) :
    ∃ left right,
      left < right ∧ right < context ∧ ropePhaseBankCollision periods left right := by
  have hstart : 0 < ropeCollisionPairCountAtGap context (ropePeriodBankLCM periods) :=
    ropeCollisionPairCountAtGap_pos_iff.mpr hlcm_lt_context
  have hfamily :=
    ropePhaseBankCollision_at_lcm_gap (periods := periods) (context := context)
      (start := 0) hstart
  refine ⟨0, ropePeriodBankLCM periods, ?_, ?_, ?_⟩
  · simpa using hlcm_pos
  · simpa using hfamily.2
  · simpa using hfamily.1

/-- If the period-bank LCM reaches the inspected context, no unequal ordered
in-context pair can collide in every declared channel.

This is the exact finite-bank pass condition used by the certifier: once the
least common collision gap is at least the context length, every positive
in-context position gap is too small to be divisible by that bank LCM. -/
theorem not_ropePhaseBankCollision_of_lcm_ge_context
    {periods : List Nat} {context left right : Nat}
    (hlcm_context : context ≤ ropePeriodBankLCM periods)
    (hleft : left < right) (hright : right < context) :
    ¬ ropePhaseBankCollision periods left right := by
  intro hcollision
  have hle : left ≤ right := Nat.le_of_lt hleft
  have hdvd : ropePeriodBankLCM periods ∣ right - left :=
    (ropePhaseBankCollision_iff_lcm_dvd_gap (periods := periods) hle).1 hcollision
  have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
  have hlcm_le_gap : ropePeriodBankLCM periods ≤ right - left :=
    Nat.le_of_dvd hgap_pos hdvd
  have hgap_lt_context : right - left < context :=
    lt_of_le_of_lt (Nat.sub_le right left) hright
  exact (not_lt_of_ge (le_trans hlcm_context hlcm_le_gap)) hgap_lt_context

/-- If a prefix subbank already has LCM at least the inspected context, then
adding more channels cannot create an unequal all-channel collision.

This is the formal bridge used by prefix collision reports: a small declared
prefix that distinguishes the context is enough to certify the larger bank,
because every collision in the larger bank restricts to a collision in the
prefix. -/
theorem not_ropePhaseBankCollision_of_prefix_lcm_ge_context
    {pref suffix : List Nat} {context left right : Nat}
    (hlcm_context : context ≤ ropePeriodBankLCM pref)
    (hleft : left < right) (hright : right < context) :
    ¬ ropePhaseBankCollision (pref ++ suffix) left right := by
  intro hcollision
  have hpref : ropePhaseBankCollision pref left right := by
    intro period hmem
    exact hcollision period (by simp [List.mem_append, hmem])
  exact not_ropePhaseBankCollision_of_lcm_ge_context
    (periods := pref) (context := context) (left := left) (right := right)
    hlcm_context hleft hright hpref

/-- If any selected subbank has LCM at least the inspected context, then a
larger bank containing that subbank cannot have an unequal all-channel
collision.

This is the unordered-subfamily version of the prefix bridge. It supports
certificates that search for a small sufficient subset of channels instead of
only checking initial prefixes. -/
theorem not_ropePhaseBankCollision_of_subbank_lcm_ge_context
    {subbank bank : List Nat} {context left right : Nat}
    (hsubset : ∀ period, period ∈ subbank → period ∈ bank)
    (hlcm_context : context ≤ ropePeriodBankLCM subbank)
    (hleft : left < right) (hright : right < context) :
    ¬ ropePhaseBankCollision bank left right := by
  intro hcollision
  have hsubbank : ropePhaseBankCollision subbank left right := by
    intro period hmem
    exact hcollision period (hsubset period hmem)
  exact not_ropePhaseBankCollision_of_lcm_ge_context
    (periods := subbank) (context := context) (left := left) (right := right)
    hlcm_context hleft hright hsubbank

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

/-- A real one-channel phase gap is near a full turn when some signed full-turn
multiple is within the declared tolerance.

This predicate is still one-channel and real-valued. It does not by itself
prove anything about a whole RoPE bank or about learned model quality. -/
def ropeRealPhaseNearTurn
    (frequency fullTurn tolerance : ℝ) (left right : Nat) : Prop :=
  ∃ turns : Int, ropeRealPhaseIntTurnError frequency fullTurn left right turns ≤ tolerance

/-- A real one-channel phase gap is separated from every signed full-turn
multiple by at least a declared margin. -/
def ropeRealPhaseTurnSeparated
    (frequency fullTurn margin : ℝ) (left right : Nat) : Prop :=
  ∀ turns : Int, margin ≤ ropeRealPhaseIntTurnError frequency fullTurn left right turns

/-- A finite real-phase bank is near a full-turn collision when every declared
channel is individually near some signed full-turn multiple.

This is the real-valued analogue of an all-channel collision warning. It is
still conditional real arithmetic, not a Diophantine theorem for standard RoPE
frequencies. -/
def ropeRealPhaseBankNearTurn
    (frequencies : List ℝ) (fullTurn tolerance : ℝ) (left right : Nat) : Prop :=
  ∀ frequency, frequency ∈ frequencies →
    ropeRealPhaseNearTurn frequency fullTurn tolerance left right

/-- A finite real-phase bank has a separating channel when at least one
declared channel is separated from every signed full-turn multiple by the
given margin. -/
def ropeRealPhaseBankTurnSeparated
    (frequencies : List ℝ) (fullTurn margin : ℝ) (left right : Nat) : Prop :=
  ∃ frequency, frequency ∈ frequencies ∧
    ropeRealPhaseTurnSeparated frequency fullTurn margin left right

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

/-- One-turn-window separation from every signed full-turn multiple.

This packages `ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window` as the
formal real-phase margin predicate used by the certifier roadmap. It is still
conditional on the one-turn window hypotheses. -/
theorem ropeRealPhaseTurnSeparated_of_one_turn_window
    {frequency fullTurn margin : ℝ} {left right : Nat}
    (hfull_nonneg : 0 ≤ fullTurn)
    (hphase_le_full : ropeRealPhaseGapAbs frequency left right ≤ fullTurn)
    (hleft_margin : margin ≤ ropeRealPhaseGapAbs frequency left right)
    (hright_margin : margin ≤ fullTurn - ropeRealPhaseGapAbs frequency left right) :
    ropeRealPhaseTurnSeparated frequency fullTurn margin left right := by
  intro turns
  exact ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window
    (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
    (left := left) (right := right) (turns := turns)
    hfull_nonneg hphase_le_full hleft_margin hright_margin

/-- Separation by `margin` rules out any near-turn collision at a smaller
`tolerance`.

This is the first formal bridge from a lower-bound margin statement to the
Boolean warning condition used by a numerical certifier. The theorem does not
prove the margin hypotheses for arbitrary RoPE frequencies. -/
theorem not_ropeRealPhaseNearTurn_of_turnSeparated_lt
    {frequency fullTurn margin tolerance : ℝ} {left right : Nat}
    (hseparated : ropeRealPhaseTurnSeparated frequency fullTurn margin left right)
    (htolerance : tolerance < margin) :
    ¬ ropeRealPhaseNearTurn frequency fullTurn tolerance left right := by
  rintro ⟨turns, hnear⟩
  have hmargin := hseparated turns
  linarith

/-- Scale real RoPE full-turn error into the standard Diophantine form.

For ordered positions and a nonnegative channel frequency, the signed
full-turn error is the declared full turn times the nearest-integer style
quantity `|gap * (frequency / fullTurn) - turns|`. This is the bridge needed
before applying continued-fraction or Diophantine approximation theorems to
the real-phase margin program. -/
theorem ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError
    {frequency fullTurn : ℝ} {left right : Nat} {turns : Int}
    (hleft : left ≤ right) (hfrequency_nonneg : 0 ≤ frequency)
    (hfull_pos : 0 < fullTurn) :
    ropeRealPhaseIntTurnError frequency fullTurn left right turns =
      fullTurn * |((right - left : Nat) : ℝ) * (frequency / fullTurn) - (turns : ℝ)| := by
  unfold ropeRealPhaseIntTurnError
  rw [ropeRealPhaseGapAbs_eq_natGap_mul_abs (frequency := frequency) hleft,
    abs_of_nonneg hfrequency_nonneg]
  have hscale :
      ((right - left : Nat) : ℝ) * frequency - (turns : ℝ) * fullTurn =
        fullTurn * (((right - left : Nat) : ℝ) * (frequency / fullTurn) - (turns : ℝ)) := by
    field_simp [hfull_pos.ne']
  rw [hscale, abs_mul, abs_of_pos hfull_pos]

/-- Nearest-integer turn-ratio error for a natural position gap.

After the normalization theorem
`ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError`, this is the
dimensionless Diophantine error object for the turn ratio
`frequency / fullTurn`. -/
def ropeTurnRatioError (turnRatio : ℝ) (gap : Nat) (turns : Int) : ℝ :=
  |(gap : ℝ) * turnRatio - (turns : ℝ)|

/-- A finite-context lower-bound certificate for a turn ratio.

It says that every positive gap smaller than `context` is at least `margin`
away from every integer multiple of a full turn after normalization. This is
the finite-context object that a continued-fraction or bounded-search proof can
target later. -/
def ropeTurnRatioFiniteMargin (turnRatio margin : ℝ) (context : Nat) : Prop :=
  ∀ gap : Nat, 0 < gap → gap < context → ∀ turns : Int,
    margin ≤ ropeTurnRatioError turnRatio gap turns

/-- The finite-context margin predicate is exactly the same as checking every
positive gap in the generated context range.

This is the first formal finite-search bridge for the real RoPE margin
program. It does not reduce the remaining integer-turn quantifier; it only
connects the abstract predicate to the concrete list of gaps a certifier or a
future bounded proof artifact must cover. -/
theorem ropeTurnRatioFiniteMargin_iff_range_gap_bounds
    {turnRatio margin : ℝ} {context : Nat} :
    ropeTurnRatioFiniteMargin turnRatio margin context ↔
      ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
        ∀ turns : Int, margin ≤ ropeTurnRatioError turnRatio gap turns := by
  constructor
  · intro hmargin gap hgap_range hgap_pos turns
    exact hmargin gap hgap_pos (List.mem_range.mp hgap_range) turns
  · intro hbounds gap hgap_pos hgap_context turns
    exact hbounds gap (List.mem_range.mpr hgap_context) hgap_pos turns

/-- Finite floor/ceiling witnesses for a turn-ratio margin.

For each positive generated gap, this asks only for the two nearest-integer
boundary checks: the integer floor and the integer ceiling of
`gap * turnRatio`. The theorem below proves that these two checks are
equivalent to the full `∀ turns : Int` obligation in
`ropeTurnRatioFiniteMargin`. -/
def ropeTurnRatioNearestIntegerWitnesses
    (turnRatio margin : ℝ) (context : Nat) : Prop :=
  ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
    margin ≤ |(gap : ℝ) * turnRatio - ((⌊(gap : ℝ) * turnRatio⌋ : ℤ) : ℝ)| ∧
      margin ≤ |(gap : ℝ) * turnRatio - ((⌈(gap : ℝ) * turnRatio⌉ : ℤ) : ℝ)|

/-- Checking a lower bound against the floor and ceiling of a real value is
equivalent to checking the same lower bound against every integer.

This is the finite nearest-integer bridge behind the RoPE real-phase theorem
program: for a fixed real value, all integer-turn obligations collapse to two
auditable witnesses. -/
theorem ropeNearestIntegerWitnesses_iff_forall_int {x margin : ℝ} :
    (margin ≤ |x - ((⌊x⌋ : ℤ) : ℝ)| ∧ margin ≤ |x - ((⌈x⌉ : ℤ) : ℝ)|) ↔
      ∀ turns : Int, margin ≤ |x - (turns : ℝ)| := by
  constructor
  · intro h turns
    rcases h with ⟨hfloor, hceil⟩
    by_cases hturns_le_floor : turns ≤ ⌊x⌋
    · have hturns_le_floor_real : (turns : ℝ) ≤ ((⌊x⌋ : ℤ) : ℝ) := by
        exact_mod_cast hturns_le_floor
      have hfloor_le_x : ((⌊x⌋ : ℤ) : ℝ) ≤ x := Int.floor_le x
      have hfloor_dist : |x - ((⌊x⌋ : ℤ) : ℝ)| ≤ |x - (turns : ℝ)| := by
        rw [abs_of_nonneg (sub_nonneg.mpr hfloor_le_x)]
        rw [abs_of_nonneg (sub_nonneg.mpr (le_trans hturns_le_floor_real hfloor_le_x))]
        linarith
      exact le_trans hfloor hfloor_dist
    · have hfloor_lt_turns : ⌊x⌋ < turns := lt_of_not_ge hturns_le_floor
      have hfloor_add_le_turns : ⌊x⌋ + 1 ≤ turns :=
        Int.add_one_le_iff.mpr hfloor_lt_turns
      have hx_lt_floor_add : x < (((⌊x⌋ : ℤ) + 1 : ℤ) : ℝ) := by
        simp [Int.cast_add, Int.cast_one, Int.lt_floor_add_one x]
      have hfloor_add_le_turns_real :
          (((⌊x⌋ : ℤ) + 1 : ℤ) : ℝ) ≤ (turns : ℝ) := by
        exact_mod_cast hfloor_add_le_turns
      have hx_le_turns : x ≤ (turns : ℝ) :=
        le_of_lt (lt_of_lt_of_le hx_lt_floor_add hfloor_add_le_turns_real)
      have hceil_le_turns : ⌈x⌉ ≤ turns := Int.ceil_le.mpr hx_le_turns
      have hceil_le_turns_real : ((⌈x⌉ : ℤ) : ℝ) ≤ (turns : ℝ) := by
        exact_mod_cast hceil_le_turns
      have hx_le_ceil : x ≤ ((⌈x⌉ : ℤ) : ℝ) := Int.le_ceil x
      have hceil_dist : |x - ((⌈x⌉ : ℤ) : ℝ)| ≤ |x - (turns : ℝ)| := by
        rw [abs_of_nonpos (sub_nonpos.mpr hx_le_ceil)]
        rw [abs_of_nonpos (sub_nonpos.mpr hx_le_turns)]
        linarith
      exact le_trans hceil hceil_dist
  · intro h
    exact ⟨h ⌊x⌋, h ⌈x⌉⟩

/-- Finite-context turn-ratio margins are equivalent to checking the floor and
ceiling nearest-integer witnesses for every positive generated gap.

This upgrades the generated-gap bridge by removing the infinite integer-turn
quantifier. It is still not a continued-fraction lower-bound theorem: the
remaining mathematical work is to prove or independently certify the two
witness inequalities for the concrete turn ratios under study. -/
theorem ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses
    {turnRatio margin : ℝ} {context : Nat} :
    ropeTurnRatioFiniteMargin turnRatio margin context ↔
      ropeTurnRatioNearestIntegerWitnesses turnRatio margin context := by
  rw [ropeTurnRatioFiniteMargin_iff_range_gap_bounds]
  constructor
  · intro hbounds gap hgap_range hgap_pos
    exact
      ⟨hbounds gap hgap_range hgap_pos ⌊(gap : ℝ) * turnRatio⌋,
        hbounds gap hgap_range hgap_pos ⌈(gap : ℝ) * turnRatio⌉⟩
  · intro hwitness gap hgap_range hgap_pos turns
    exact
      (ropeNearestIntegerWitnesses_iff_forall_int
        (x := (gap : ℝ) * turnRatio) (margin := margin)).1
        (hwitness gap hgap_range hgap_pos) turns

/-- A proof-carrying finite turn-ratio margin certificate.

The payload is the finite floor/ceiling nearest-integer witness predicate from
`ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses`. Keeping this as a
named certificate object gives downstream tools a stable declaration to cite:
the finite witnesses are the proof payload, and the theorem below turns that
payload into the abstract `ropeTurnRatioFiniteMargin` contract. -/
structure RopeTurnRatioFiniteMarginCertificate
    (turnRatio margin : ℝ) (context : Nat) : Prop where
  nearestIntegerWitnesses : ropeTurnRatioNearestIntegerWitnesses turnRatio margin context

/-- A finite nearest-integer witness certificate proves the corresponding
finite-context turn-ratio margin. -/
theorem RopeTurnRatioFiniteMarginCertificate.certifies
    {turnRatio margin : ℝ} {context : Nat}
    (certificate :
      RopeTurnRatioFiniteMarginCertificate turnRatio margin context) :
    ropeTurnRatioFiniteMargin turnRatio margin context :=
  (ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses
    (turnRatio := turnRatio) (margin := margin) (context := context)).2
    certificate.nearestIntegerWitnesses

/-- One rational interval witness for a turn-ratio gap.

The rational interval `[lower, upper]` encloses `gap * turnRatio` and sits
inside a single integer cell `[cell + margin, cell + 1 - margin]`. This is the
exact-arithmetic shape needed by future generated interval certificates: the
certificate never asks Lean to trust a floating-point scan. -/
def ropeTurnRatioIntervalWitness
    (turnRatio margin : ℝ) (gap : Nat) (lower upper : ℚ) (cell : Int) : Prop :=
  (lower : ℝ) ≤ (gap : ℝ) * turnRatio ∧
    (gap : ℝ) * turnRatio ≤ (upper : ℝ) ∧
      (cell : ℝ) + margin ≤ (lower : ℝ) ∧
        (upper : ℝ) ≤ (cell : ℝ) + 1 - margin

/-- A rational interval witness proves the nearest-integer lower bound for
all integer turns at one generated gap. -/
theorem ropeTurnRatioIntervalWitness_forall_int
    {turnRatio margin : ℝ} {gap : Nat} {lower upper : ℚ} {cell : Int}
    (hmargin_nonneg : 0 ≤ margin)
    (hwitness :
      ropeTurnRatioIntervalWitness turnRatio margin gap lower upper cell) :
    ∀ turns : Int, margin ≤ ropeTurnRatioError turnRatio gap turns := by
  intro turns
  unfold ropeTurnRatioIntervalWitness at hwitness
  rcases hwitness with ⟨hlower, hupper, hleft, hright⟩
  let x : ℝ := (gap : ℝ) * turnRatio
  have hcell_margin_le_x : (cell : ℝ) + margin ≤ x := le_trans hleft hlower
  have hx_le_cell_succ_sub : x ≤ (cell : ℝ) + 1 - margin := le_trans hupper hright
  by_cases hturns_le_cell : turns ≤ cell
  · have hturns_le_cell_real : (turns : ℝ) ≤ (cell : ℝ) := by
      exact_mod_cast hturns_le_cell
    have hmargin_le_sub : margin ≤ x - (turns : ℝ) := by
      linarith
    have hsub_nonneg : 0 ≤ x - (turns : ℝ) := by
      linarith
    unfold ropeTurnRatioError
    have : margin ≤ |x - (turns : ℝ)| := by
      rwa [abs_of_nonneg hsub_nonneg]
    simpa [x] using this
  · have hcell_lt_turns : cell < turns := lt_of_not_ge hturns_le_cell
    have hcell_succ_le_turns : cell + 1 ≤ turns :=
      Int.add_one_le_iff.mpr hcell_lt_turns
    have hcell_succ_le_turns_real :
        (((cell : Int) + 1 : Int) : ℝ) ≤ (turns : ℝ) := by
      exact_mod_cast hcell_succ_le_turns
    have hcell_succ_le_turns_real' : (cell : ℝ) + 1 ≤ (turns : ℝ) := by
      simpa [Int.cast_add, Int.cast_one] using hcell_succ_le_turns_real
    have hmargin_le_sub : margin ≤ (turns : ℝ) - x := by
      linarith
    have hsub_nonpos : x - (turns : ℝ) ≤ 0 := by
      linarith
    unfold ropeTurnRatioError
    have : margin ≤ |x - (turns : ℝ)| := by
      rw [abs_of_nonpos hsub_nonpos]
      linarith
    simpa [x] using this

/-- A finite rational interval certificate for a turn-ratio margin.

For every positive generated gap below the context, the certificate supplies a
rational enclosure of `gap * turnRatio` and an integer cell showing that the
whole enclosure stays at least `margin` away from both cell endpoints. -/
def ropeTurnRatioIntervalCertificate
    (turnRatio margin : ℝ) (context : Nat) : Prop :=
  0 ≤ margin ∧
    ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
      ∃ lower upper : ℚ, ∃ cell : Int,
        ropeTurnRatioIntervalWitness turnRatio margin gap lower upper cell

/-- A finite rational interval certificate proves the finite-context
turn-ratio margin. -/
theorem ropeTurnRatioFiniteMargin_of_intervalCertificate
    {turnRatio margin : ℝ} {context : Nat}
    (certificate :
      ropeTurnRatioIntervalCertificate turnRatio margin context) :
    ropeTurnRatioFiniteMargin turnRatio margin context := by
  rw [ropeTurnRatioFiniteMargin_iff_range_gap_bounds]
  intro gap hgap_range hgap_pos turns
  rcases certificate with ⟨hmargin_nonneg, hwitnesses⟩
  rcases hwitnesses gap hgap_range hgap_pos with ⟨lower, upper, cell, hwitness⟩
  exact
    ropeTurnRatioIntervalWitness_forall_int
      (turnRatio := turnRatio) (margin := margin) (gap := gap)
      (lower := lower) (upper := upper) (cell := cell)
      hmargin_nonneg hwitness turns

/-- Integer turn ratios have no positive finite-context margin once the
context contains the unit gap.

This is a guardrail theorem for the real RoPE program: if a channel advances by
an integer number of full turns per position, then adjacent positions can land
exactly on a full-turn multiple. Such a channel can only certify nonpositive
nearest-integer margins for any context with `1 < context`. -/
theorem ropeTurnRatioFiniteMargin_int_iff_nonpos_of_one_lt_context
    {turnRatio margin : ℝ} {turns : Int} {context : Nat}
    (hturnRatio : turnRatio = (turns : ℝ)) (hcontext : 1 < context) :
    ropeTurnRatioFiniteMargin turnRatio margin context ↔ margin ≤ 0 := by
  constructor
  · intro hmargin
    have hbound := hmargin 1 (by decide) hcontext turns
    unfold ropeTurnRatioError at hbound
    rw [hturnRatio] at hbound
    simpa using hbound
  · intro hnonpos gap _hgap_pos _hgap_context z
    unfold ropeTurnRatioError
    exact le_trans hnonpos (abs_nonneg _)

/-- Rational turn ratios have no positive finite-context margin once the
context contains the denominator gap.

This extends the integer-ratio guardrail to discretized or rationalized RoPE
channels: if `turnRatio = numerator / denominator`, then the denominator-sized
gap lands exactly on an integer number of full turns. Such a channel cannot
certify positive nearest-integer separation for any context with
`denominator < context`. -/
theorem ropeTurnRatioFiniteMargin_natRatio_iff_nonpos_of_den_lt_context
    {numerator denominator : Nat} {margin : ℝ} {context : Nat}
    (hdenominator : 0 < denominator) (hcontext : denominator < context) :
    ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ)) margin context ↔
      margin ≤ 0 := by
  constructor
  · intro hmargin
    have hbound := hmargin denominator hdenominator hcontext (Int.ofNat numerator)
    unfold ropeTurnRatioError at hbound
    have hden_ne : (denominator : ℝ) ≠ 0 := by exact_mod_cast hdenominator.ne'
    have hzero :
        (denominator : ℝ) * ((numerator : ℝ) / (denominator : ℝ)) -
            ((Int.ofNat numerator : Int) : ℝ) = 0 := by
      field_simp [hden_ne]
      norm_num
    rwa [hzero, abs_zero] at hbound
  · intro hnonpos gap _hgap_pos _hgap_context turns
    unfold ropeTurnRatioError
    exact le_trans hnonpos (abs_nonneg _)

private theorem one_le_abs_intCast_of_ne_zero {z : ℤ} (hz : z ≠ 0) :
    (1 : ℝ) ≤ |(z : ℝ)| := by
  have hnat : 1 ≤ z.natAbs := Nat.succ_le_of_lt (Int.natAbs_pos.mpr hz)
  have hint : (1 : ℤ) ≤ |z| := by
    rw [Int.abs_eq_natAbs]
    exact_mod_cast hnat
  exact_mod_cast hint

private theorem ropeTurnRatioError_natRatio_eq_abs_int_num_sub_turn_mul_den_div_den
    {numerator denominator gap : Nat} {turns : Int}
    (hdenominator : 0 < denominator) :
    let z : Int := ((gap * numerator : Nat) : Int) - turns * (denominator : Int)
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap turns =
      |(z : ℝ)| / (denominator : ℝ) := by
  intro z
  unfold ropeTurnRatioError
  have hden_ne : (denominator : ℝ) ≠ 0 := by exact_mod_cast (ne_of_gt hdenominator)
  have hcast :
      (z : ℝ) = (gap : ℝ) * (numerator : ℝ) - (turns : ℝ) * (denominator : ℝ) := by
    dsimp [z]
    norm_num [Nat.cast_mul]
  have hden_pos_real : (0 : ℝ) < denominator := by exact_mod_cast hdenominator
  have hquot :
      (gap : ℝ) * ((numerator : ℝ) / (denominator : ℝ)) - (turns : ℝ) =
        ((gap : ℝ) * (numerator : ℝ) - (turns : ℝ) * (denominator : ℝ)) /
          (denominator : ℝ) := by
    field_simp [hden_ne]
  calc
    |(gap : ℝ) * ((numerator : ℝ) / (denominator : ℝ)) - (turns : ℝ)|
        = |((gap : ℝ) * (numerator : ℝ) - (turns : ℝ) * (denominator : ℝ)) /
            (denominator : ℝ)| := by rw [hquot]
    _ = |((gap : ℝ) * (numerator : ℝ) - (turns : ℝ) * (denominator : ℝ))| /
            (denominator : ℝ) := by rw [abs_div, abs_of_pos hden_pos_real]
    _ = |(z : ℝ)| / (denominator : ℝ) := by rw [hcast]

/-- Coprime natural rational turn ratios have a theorem-backed positive finite
margin as long as the inspected context does not reach the denominator gap.

If `turnRatio = numerator / denominator`, `numerator` is coprime to
`denominator`, and every inspected positive gap is strictly below the
denominator, then every nearest-integer error is at least `1 / denominator`.
This is a positive rational finite-context certificate, not an irrational or
continued-fraction RoPE margin theorem. -/
theorem ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
    {numerator denominator : Nat} (hdenominator : 0 < denominator)
    (hcoprime : Nat.Coprime numerator denominator) {context : Nat}
    (hcontext : context ≤ denominator) :
    ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ))
      (1 / (denominator : ℝ)) context := by
  intro gap hgap_pos hgap_context turns
  let z : Int := ((gap * numerator : Nat) : Int) - turns * (denominator : Int)
  have herror :=
    ropeTurnRatioError_natRatio_eq_abs_int_num_sub_turn_mul_den_div_den
      (numerator := numerator) (denominator := denominator) (gap := gap)
      (turns := turns) hdenominator
  have hgap_lt_den : gap < denominator := lt_of_lt_of_le hgap_context hcontext
  have hz_ne : z ≠ 0 := by
    intro hz
    have hz0 : ((gap * numerator : Nat) : Int) - turns * (denominator : Int) = 0 := by
      simpa [z] using hz
    have heq : ((gap * numerator : Nat) : Int) = turns * (denominator : Int) := by
      linarith
    have hdiv_int : (denominator : Int) ∣ ((gap * numerator : Nat) : Int) := by
      refine ⟨turns, ?_⟩
      simpa [mul_comm] using heq
    have hdiv_nat : denominator ∣ gap * numerator :=
      Int.natCast_dvd_natCast.mp hdiv_int
    have hden_dvd_gap : denominator ∣ gap := by
      exact hcoprime.symm.dvd_of_dvd_mul_left (by simpa [mul_comm] using hdiv_nat)
    have hgap_zero : gap = 0 := Nat.eq_zero_of_dvd_of_lt hden_dvd_gap hgap_lt_den
    exact Nat.ne_of_gt hgap_pos hgap_zero
  have hone : (1 : ℝ) ≤ |(z : ℝ)| := one_le_abs_intCast_of_ne_zero hz_ne
  have hden_nonneg : (0 : ℝ) ≤ denominator := by exact_mod_cast (Nat.zero_le denominator)
  have hdiv : (1 : ℝ) / (denominator : ℝ) ≤ |(z : ℝ)| / (denominator : ℝ) :=
    div_le_div_of_nonneg_right hone hden_nonneg
  simpa [herror, z] using hdiv

/-- For a reduced natural rational turn ratio, the `1 / denominator` margin
has an exact finite-context boundary.

The positive certificate holds precisely while the inspected context does not
reach past the denominator gap. Once the denominator gap is included, that gap
lands exactly on an integer number of turns and no positive margin can remain.
This packages the rational positive and negative guardrails into one theorem
usable by certifiers. -/
theorem ropeTurnRatioFiniteMargin_natRatio_one_over_den_iff_context_le_den
    {numerator denominator context : Nat} (hdenominator : 0 < denominator)
    (hcoprime : Nat.Coprime numerator denominator) :
    ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ))
      (1 / (denominator : ℝ)) context ↔ context ≤ denominator := by
  constructor
  · intro hmargin
    by_contra hnot
    have hcontext : denominator < context := Nat.lt_of_not_ge hnot
    have hnonpos :
        (1 / (denominator : ℝ)) ≤ 0 :=
      (ropeTurnRatioFiniteMargin_natRatio_iff_nonpos_of_den_lt_context
        (numerator := numerator) (denominator := denominator)
        (margin := 1 / (denominator : ℝ)) (context := context)
        hdenominator hcontext).1 hmargin
    have hden_pos_real : (0 : ℝ) < denominator := by exact_mod_cast hdenominator
    have hpos : (0 : ℝ) < 1 / (denominator : ℝ) := one_div_pos.mpr hden_pos_real
    linarith
  · intro hcontext
    exact ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
      (numerator := numerator) (denominator := denominator)
      hdenominator hcoprime hcontext

/-! ### Named rational/discretized finite-margin preset -/

/-- A small theorem-backed rational turn-ratio preset used by the public
certifier as the first end-to-end finite-margin certificate example.

This is deliberately rational/discretized: it is not the irrational standard
RoPE `1 / (2π)` channel. Its purpose is to exercise the complete certificate
path over a real-shaped 4k context with no remaining hypotheses. -/
noncomputable def ropeRationalPreset4099TurnRatio : ℝ :=
  ((1 : Nat) : ℝ) / ((4099 : Nat) : ℝ)

/-- The advertised margin for `ropeRationalPreset4099TurnRatio`. -/
noncomputable def ropeRationalPreset4099Margin : ℝ :=
  1 / ((4099 : Nat) : ℝ)

/-- The inspected context length for the named rational/discretized preset. -/
def ropeRationalPreset4099Context : Nat := 4096

/-- The named rational/discretized preset has a proved finite turn-ratio
margin over its 4k context. -/
theorem ropeRationalPreset4099_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeRationalPreset4099TurnRatio
      ropeRationalPreset4099Margin ropeRationalPreset4099Context := by
  dsimp [ropeRationalPreset4099TurnRatio, ropeRationalPreset4099Margin,
    ropeRationalPreset4099Context]
  exact
    ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
      (numerator := 1) (denominator := 4099) (context := 4096)
      (by norm_num) (by norm_num) (by norm_num)

/-- The named rational/discretized preset packaged as a proof-carrying
finite-margin certificate. -/
def ropeRationalPreset4099_certificate :
    RopeTurnRatioFiniteMarginCertificate ropeRationalPreset4099TurnRatio
      ropeRationalPreset4099Margin ropeRationalPreset4099Context :=
  ⟨(ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses
    (turnRatio := ropeRationalPreset4099TurnRatio)
    (margin := ropeRationalPreset4099Margin)
    (context := ropeRationalPreset4099Context)).1
    ropeRationalPreset4099_turnRatioFiniteMargin⟩

/-! ### Named standard-RoPE interval seeds -/

/-- The standard RoPE channel-0 turn ratio in turns per token:
`frequency / fullTurn = 1 / (2π)`. -/
noncomputable def ropeStandardChannel0TurnRatio : ℝ := 1 / (2 * Real.pi)

/-- A tiny inspected context for the first standard-RoPE interval certificate
seed. Larger contexts need generated rational interval data with sharper
`π` bounds. -/
def ropeStandardChannel0SeedContext : Nat := 6

/-- The advertised margin for the standard channel-0 seed certificate. -/
noncomputable def ropeStandardChannel0SeedMargin : ℝ := 1 / 8

/-- A slightly larger inspected context for the second standard-RoPE interval
certificate seed. This still covers only channel 0, but it uses a sharper
mathlib lower bound on `π` to include the sixth positive gap. -/
def ropeStandardChannel0D2SeedContext : Nat := 7

/-- The advertised margin for the second standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D2SeedMargin : ℝ := 1 / 32

private theorem ropeStandardChannel0_base_lower :
    (1 : ℝ) / 8 ≤ ropeStandardChannel0TurnRatio := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have htwo_pi_le_eight : 2 * Real.pi ≤ 8 := by
    nlinarith [Real.pi_le_four]
  rw [ropeStandardChannel0TurnRatio, one_div, one_div]
  exact
    (inv_le_inv₀ (by norm_num : (0 : ℝ) < 8) htwo_pi_pos).2
      htwo_pi_le_eight

private theorem ropeStandardChannel0_base_upper :
    ropeStandardChannel0TurnRatio ≤ (1 : ℝ) / 6 := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have hsix_le_two_pi : (6 : ℝ) ≤ 2 * Real.pi := by
    nlinarith [Real.pi_gt_three]
  rw [ropeStandardChannel0TurnRatio, one_div, one_div]
  exact
    (inv_le_inv₀ htwo_pi_pos (by norm_num : (0 : ℝ) < 6)).2
      hsix_le_two_pi

private theorem ropeStandardChannel0_d2_base_upper :
    ropeStandardChannel0TurnRatio ≤ (25 : ℝ) / 157 := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have hlower : (157 : ℝ) / 25 < 2 * Real.pi := by
    nlinarith [Real.pi_gt_d2]
  have hrecip : ((157 : ℝ) / 25)⁻¹ = (25 : ℝ) / 157 := by norm_num
  have hupper : (2 * Real.pi)⁻¹ < ((157 : ℝ) / 25)⁻¹ :=
    (inv_lt_inv₀ htwo_pi_pos (by norm_num : (0 : ℝ) < (157 : ℝ) / 25)).2 hlower
  have hupper_le : (2 * Real.pi)⁻¹ ≤ (25 : ℝ) / 157 := by
    rw [← hrecip]
    exact le_of_lt hupper
  simpa [ropeStandardChannel0TurnRatio, one_div] using hupper_le

private theorem ropeStandardChannel0_intervalWitness_of_gap_le_five
    {gap : Nat} (hgap_pos : 0 < gap) (hgap_le_five : gap ≤ 5) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0SeedMargin gap ((gap : ℚ) / 8) ((gap : ℚ) / 6) 0 := by
  unfold ropeTurnRatioIntervalWitness ropeStandardChannel0SeedMargin
  have hgap_nonneg : 0 ≤ (gap : ℝ) := by positivity
  have hgap_one_le : (1 : ℝ) ≤ gap := by exact_mod_cast hgap_pos
  have hgap_le_five_real : (gap : ℝ) ≤ 5 := by exact_mod_cast hgap_le_five
  constructor
  · calc
      (((gap : ℚ) / 8 : ℚ) : ℝ) = (gap : ℝ) * ((1 : ℝ) / 8) := by
        norm_num [div_eq_mul_inv]
      _ ≤ (gap : ℝ) * ropeStandardChannel0TurnRatio :=
        mul_le_mul_of_nonneg_left ropeStandardChannel0_base_lower hgap_nonneg
  constructor
  · calc
      (gap : ℝ) * ropeStandardChannel0TurnRatio ≤ (gap : ℝ) * ((1 : ℝ) / 6) :=
        mul_le_mul_of_nonneg_left ropeStandardChannel0_base_upper hgap_nonneg
      _ = (((gap : ℚ) / 6 : ℚ) : ℝ) := by
        norm_num [div_eq_mul_inv]
  constructor
  · calc
      ((0 : Int) : ℝ) + (1 : ℝ) / 8 = (1 : ℝ) / 8 := by norm_num
      _ ≤ (gap : ℝ) / 8 := by
        exact div_le_div_of_nonneg_right hgap_one_le (by norm_num : (0 : ℝ) ≤ 8)
      _ = (((gap : ℚ) / 8 : ℚ) : ℝ) := by
        norm_num
  · calc
      (((gap : ℚ) / 6 : ℚ) : ℝ) = (gap : ℝ) / 6 := by
        norm_num
      _ ≤ (5 : ℝ) / 6 := by
        exact div_le_div_of_nonneg_right hgap_le_five_real (by norm_num : (0 : ℝ) ≤ 6)
      _ ≤ (7 : ℝ) / 8 := by norm_num
      _ = ((0 : Int) : ℝ) + 1 - (1 : ℝ) / 8 := by norm_num

/-- The first standard-RoPE interval seed: channel 0 has margin `1/8` over
the tiny context containing gaps `1` through `5`.

This is intentionally small. It proves the end-to-end interval-certificate
shape for the genuine standard channel `1 / (2π)` using only mathlib's basic
`3 < π ≤ 4` bounds; larger contexts need generated rational intervals with
sharper `π` bounds. -/
theorem ropeStandardChannel0Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0SeedMargin ropeStandardChannel0SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_six : gap < 6 := by
    simpa [ropeStandardChannel0SeedContext] using List.mem_range.mp hgap_range
  have hgap_le_five : gap ≤ 5 := by
    simpa using Nat.lt_succ_iff.mp hgap_lt_six
  exact
    ⟨(gap : ℚ) / 8, (gap : ℚ) / 6, 0,
      ropeStandardChannel0_intervalWitness_of_gap_le_five hgap_pos hgap_le_five⟩

/-- The named standard-RoPE channel-0 seed has a proved finite turn-ratio
margin over context `6`. -/
theorem ropeStandardChannel0Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0SeedMargin ropeStandardChannel0SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0Seed_intervalCertificate

private theorem ropeStandardChannel0_d2IntervalWitness_of_gap_le_six
    {gap : Nat} (hgap_pos : 0 < gap) (hgap_le_six : gap ≤ 6) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D2SeedMargin gap ((gap : ℚ) / 8)
      (((25 * gap : Nat) : ℚ) / 157) 0 := by
  unfold ropeTurnRatioIntervalWitness ropeStandardChannel0D2SeedMargin
  have hgap_nonneg : 0 ≤ (gap : ℝ) := by positivity
  have hgap_one_le : (1 : ℝ) ≤ gap := by exact_mod_cast hgap_pos
  have hgap_le_six_real : (gap : ℝ) ≤ 6 := by exact_mod_cast hgap_le_six
  constructor
  · calc
      (((gap : ℚ) / 8 : ℚ) : ℝ) = (gap : ℝ) * ((1 : ℝ) / 8) := by
        norm_num [div_eq_mul_inv]
      _ ≤ (gap : ℝ) * ropeStandardChannel0TurnRatio :=
        mul_le_mul_of_nonneg_left ropeStandardChannel0_base_lower hgap_nonneg
  constructor
  · calc
      (gap : ℝ) * ropeStandardChannel0TurnRatio ≤ (gap : ℝ) * ((25 : ℝ) / 157) :=
        mul_le_mul_of_nonneg_left ropeStandardChannel0_d2_base_upper hgap_nonneg
      _ = ((((25 * gap : Nat) : ℚ) / 157 : ℚ) : ℝ) := by
        norm_num [Nat.cast_mul, div_eq_mul_inv]
        ring
  constructor
  · calc
      ((0 : Int) : ℝ) + (1 : ℝ) / 32 = (1 : ℝ) / 32 := by norm_num
      _ ≤ (gap : ℝ) / 8 := by
        nlinarith [hgap_one_le]
      _ = (((gap : ℚ) / 8 : ℚ) : ℝ) := by
        norm_num
  · calc
      ((((25 * gap : Nat) : ℚ) / 157 : ℚ) : ℝ) = ((25 : ℝ) * gap) / 157 := by
        norm_num [Nat.cast_mul]
      _ ≤ ((25 : ℝ) * 6) / 157 := by
        exact div_le_div_of_nonneg_right
          (mul_le_mul_of_nonneg_left hgap_le_six_real (by norm_num : (0 : ℝ) ≤ 25))
          (by norm_num : (0 : ℝ) ≤ 157)
      _ ≤ (31 : ℝ) / 32 := by norm_num
      _ = ((0 : Int) : ℝ) + 1 - (1 : ℝ) / 32 := by norm_num

/-- A sharper standard-RoPE interval seed: channel 0 has margin `1/32` over
the tiny context containing gaps `1` through `6`.

This is still intentionally small, but it is a genuine strengthening of the
first seed: the sixth gap requires the sharper mathlib bound `3.14 < π`, giving
the rational upper enclosure `gap/(2π) ≤ 25*gap/157`. -/
theorem ropeStandardChannel0D2Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D2SeedMargin ropeStandardChannel0D2SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D2SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_seven : gap < 7 := by
    simpa [ropeStandardChannel0D2SeedContext] using List.mem_range.mp hgap_range
  have hgap_le_six : gap ≤ 6 := by
    simpa using Nat.lt_succ_iff.mp hgap_lt_seven
  exact
    ⟨(gap : ℚ) / 8, (((25 * gap : Nat) : ℚ) / 157), 0,
      ropeStandardChannel0_d2IntervalWitness_of_gap_le_six hgap_pos hgap_le_six⟩

/-- The sharper named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `7`. -/
theorem ropeStandardChannel0D2Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D2SeedMargin ropeStandardChannel0D2SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D2Seed_intervalCertificate

/-- Finite-context turn-ratio margins are monotone in the inspected context.

A margin certificate proved for a larger context automatically applies to any
smaller requested context, because the set of positive gaps to check only
shrinks. -/
theorem ropeTurnRatioFiniteMargin_mono_context
    {turnRatio margin : ℝ} {requestedContext certifiedContext : Nat}
    (hcontext : requestedContext ≤ certifiedContext)
    (hmargin : ropeTurnRatioFiniteMargin turnRatio margin certifiedContext) :
    ropeTurnRatioFiniteMargin turnRatio margin requestedContext := by
  intro gap hgap_pos hgap_context turns
  exact hmargin gap hgap_pos (lt_of_lt_of_le hgap_context hcontext) turns

/-- Finite-context turn-ratio margins are downward closed in the declared
margin value.

A certificate proving a larger lower bound also proves any smaller advertised
margin over the same finite context. -/
theorem ropeTurnRatioFiniteMargin_mono_margin
    {turnRatio smallMargin largeMargin : ℝ} {context : Nat}
    (hmargin_le : smallMargin ≤ largeMargin)
    (hmargin : ropeTurnRatioFiniteMargin turnRatio largeMargin context) :
    ropeTurnRatioFiniteMargin turnRatio smallMargin context := by
  intro gap hgap_pos hgap_context turns
  exact le_trans hmargin_le (hmargin gap hgap_pos hgap_context turns)

/-- A finite-context turn-ratio margin rules out one-channel real near-turn
collisions at any smaller scaled tolerance.

This is still conditional: it does not prove that a concrete RoPE turn ratio
has such a finite-context margin. It proves that once a margin certificate is
available, the certificate has the intended no-near-turn consequence inside
the inspected context. -/
theorem not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
    {frequency fullTurn margin tolerance : ℝ} {context left right : Nat}
    (hleft : left < right) (hright : right < context)
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn)
    (hmargin : ropeTurnRatioFiniteMargin (frequency / fullTurn) margin context)
    (htolerance : tolerance < fullTurn * margin) :
    ¬ ropeRealPhaseNearTurn frequency fullTurn tolerance left right := by
  intro hnear
  rcases hnear with ⟨turns, hturns⟩
  have hleft_le : left ≤ right := Nat.le_of_lt hleft
  have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
  have hgap_lt_context : right - left < context :=
    lt_of_le_of_lt (Nat.sub_le right left) hright
  have hratio :
      margin ≤ ropeTurnRatioError (frequency / fullTurn) (right - left) turns :=
    hmargin (right - left) hgap_pos hgap_lt_context turns
  have hscaled :
      fullTurn * margin ≤ ropeRealPhaseIntTurnError frequency fullTurn left right turns := by
    rw [ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError
      (frequency := frequency) (fullTurn := fullTurn) (left := left) (right := right)
      (turns := turns) hleft_le hfrequency_nonneg hfull_pos]
    exact mul_le_mul_of_nonneg_left hratio (le_of_lt hfull_pos)
  linarith

/-- The named rational/discretized preset certificate rules out one-channel
near-turn collisions below its certified margin. -/
theorem not_ropeRationalPreset4099_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeRationalPreset4099Context)
    (htolerance : tolerance < ropeRationalPreset4099Margin) :
    ¬ ropeRealPhaseNearTurn ropeRationalPreset4099TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeRationalPreset4099TurnRatio) (fullTurn := 1)
      (margin := ropeRationalPreset4099Margin) (tolerance := tolerance)
      (context := ropeRationalPreset4099Context) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeRationalPreset4099TurnRatio]
        positivity)
      (by norm_num)
      (by
        simpa using
          RopeTurnRatioFiniteMarginCertificate.certifies
            ropeRationalPreset4099_certificate)
      (by simpa [ropeRationalPreset4099Margin] using htolerance)

/-- The standard-RoPE channel-0 interval seed rules out one-channel near-turn
collisions below its certified margin over the tiny seed context. -/
theorem not_ropeStandardChannel0Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0SeedContext)
    (htolerance : tolerance < ropeStandardChannel0SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0SeedMargin] using htolerance)

/-- The sharper standard-RoPE channel-0 interval seed rules out one-channel
near-turn collisions below its certified margin over context `7`. -/
theorem not_ropeStandardChannel0D2Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D2SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D2SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D2SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D2SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D2Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D2SeedMargin] using htolerance)

/-- A finite-context turn-ratio margin for one channel rules out all-channel
real near-turn collision in a finite bank.

This is the bank-level certificate shape for real RoPE margins: the bank is
safe against an all-channel near-turn collision at a tolerance once at least one
member channel has a proved finite-context turn-ratio margin whose scaled value
is larger than that tolerance. -/
theorem not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin
    {frequencies : List ℝ} {frequency fullTurn margin tolerance : ℝ}
    {context left right : Nat}
    (hmem : frequency ∈ frequencies)
    (hleft : left < right) (hright : right < context)
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn)
    (hmargin : ropeTurnRatioFiniteMargin (frequency / fullTurn) margin context)
    (htolerance : tolerance < fullTurn * margin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  intro hnear
  exact
    (not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
      (tolerance := tolerance) (context := context) (left := left) (right := right)
      hleft hright hfrequency_nonneg hfull_pos hmargin htolerance)
      (hnear frequency hmem)

/-- A finite-context turn-ratio margin certified for a larger context rules out
all-channel real near-turn collision in any smaller requested context.

This is the reusable certifier transfer law: once a channel margin has been
proved or independently certified up to `certifiedContext`, the same proof
covers every `requestedContext ≤ certifiedContext` without rerunning the
formal argument. -/
theorem not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context
    {frequencies : List ℝ} {frequency fullTurn margin tolerance : ℝ}
    {requestedContext certifiedContext left right : Nat}
    (hcontext : requestedContext ≤ certifiedContext)
    (hmem : frequency ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn)
    (hmargin : ropeTurnRatioFiniteMargin (frequency / fullTurn) margin certifiedContext)
    (htolerance : tolerance < fullTurn * margin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right :=
  not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin
    (frequencies := frequencies) (frequency := frequency) (fullTurn := fullTurn)
    (margin := margin) (tolerance := tolerance) (context := requestedContext)
    (left := left) (right := right) hmem hleft hright hfrequency_nonneg hfull_pos
    (ropeTurnRatioFiniteMargin_mono_context hcontext hmargin) htolerance

/-- A larger-context, larger-margin certificate can be reused for a smaller
requested context and a smaller advertised margin at the bank level.

This is the certifier-facing real-phase transfer theorem: a future
Diophantine proof or externally checked finite search can certify one channel
with a conservative horizon and lower bound, while downstream reports may ask
for a shorter context and a smaller published margin. -/
theorem not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
    {frequencies : List ℝ} {frequency fullTurn requestedMargin certifiedMargin tolerance : ℝ}
    {requestedContext certifiedContext left right : Nat}
    (hcontext : requestedContext ≤ certifiedContext)
    (hmargin_le : requestedMargin ≤ certifiedMargin)
    (hmem : frequency ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn)
    (hmargin : ropeTurnRatioFiniteMargin (frequency / fullTurn) certifiedMargin certifiedContext)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right :=
  not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin
    (frequencies := frequencies) (frequency := frequency) (fullTurn := fullTurn)
    (margin := requestedMargin) (tolerance := tolerance) (context := requestedContext)
    (left := left) (right := right) hmem hleft hright hfrequency_nonneg hfull_pos
    (ropeTurnRatioFiniteMargin_mono_context hcontext
      (ropeTurnRatioFiniteMargin_mono_margin hmargin_le hmargin))
    htolerance

/-- A single separating channel rules out an all-channel real-phase near-turn
collision at any smaller tolerance.

This is the bank-level bridge used by the certifier's numerical scan: if one
channel has a proved turn-separation margin, then the whole bank cannot be
simultaneously near a full-turn collision at a tighter tolerance. It still does
not prove that arbitrary RoPE frequencies have such a margin. -/
theorem not_ropeRealPhaseBankNearTurn_of_bankTurnSeparated_lt
    {frequencies : List ℝ} {fullTurn margin tolerance : ℝ} {left right : Nat}
    (hseparated :
      ropeRealPhaseBankTurnSeparated frequencies fullTurn margin left right)
    (htolerance : tolerance < margin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  rintro hnear
  rcases hseparated with ⟨frequency, hmem, hchannel⟩
  exact
    (not_ropeRealPhaseNearTurn_of_turnSeparated_lt
      (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
      (tolerance := tolerance) (left := left) (right := right)
      hchannel htolerance)
      (hnear frequency hmem)

/-- One one-turn-window channel is enough to rule out an all-channel near-turn
collision at a smaller tolerance.

This composes the one-channel endpoint theorem with the bank-level bridge. The
substantive future work is still to prove the window hypotheses for the actual
RoPE frequency schedule using Diophantine or continued-fraction bounds. -/
theorem not_ropeRealPhaseBankNearTurn_of_one_channel_one_turn_window
    {frequencies : List ℝ} {frequency fullTurn margin tolerance : ℝ}
    {left right : Nat}
    (hmem : frequency ∈ frequencies)
    (hfull_nonneg : 0 ≤ fullTurn)
    (hphase_le_full : ropeRealPhaseGapAbs frequency left right ≤ fullTurn)
    (hleft_margin : margin ≤ ropeRealPhaseGapAbs frequency left right)
    (hright_margin : margin ≤ fullTurn - ropeRealPhaseGapAbs frequency left right)
    (htolerance : tolerance < margin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  exact not_ropeRealPhaseBankNearTurn_of_bankTurnSeparated_lt
    (frequencies := frequencies) (fullTurn := fullTurn) (margin := margin)
    (tolerance := tolerance) (left := left) (right := right)
    ⟨frequency, hmem,
      ropeRealPhaseTurnSeparated_of_one_turn_window
        (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
        (left := left) (right := right)
        hfull_nonneg hphase_le_full hleft_margin hright_margin⟩
    htolerance

end Circle.Applications
