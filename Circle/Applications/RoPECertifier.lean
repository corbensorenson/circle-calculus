import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Int.GCD
import Mathlib.Data.Int.Cast.Basic
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Analysis.Real.Pi.Bounds
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Finset.Range
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.IntervalCases
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

/-- Total ordered pair count over all positive in-context multiples of a common
collision gap.

For a period-bank LCM `g`, this is the exact all-channel integer-bank collision
pair count: the LCM theorem says exactly the positive multiples of `g` collide,
and this sum counts the starts available at each such positive gap. -/
def ropeCollisionPairCountAtGapMultiples (context commonGap : Nat) : Nat :=
  ∑ multiple ∈ (Finset.range context).filter (fun multiple => 0 < multiple),
    ropeCollisionPairCountAtGap context (multiple * commonGap)

/-- The number of positive common-gap multiples that can still fit inside the
inspected context.

For a common collision gap `g`, the contributing positive multiples are exactly
`1, 2, ..., (context - 1) / g`. The accompanying theorem makes that executable
quotient a checked bound rather than an informal loop limit. -/
def ropeCollisionPairCountFittingMultipleCount (context commonGap : Nat) : Nat :=
  (context - 1) / commonGap

/-- The same positive-multiple collision count, restricted to the exact
quotient-bounded range of fitting positive multiples. -/
def ropeCollisionPairCountAtGapMultiplesFittingRange (context commonGap : Nat) : Nat :=
  ∑ multiple ∈
      (Finset.range (ropeCollisionPairCountFittingMultipleCount context commonGap + 1)).filter
        (fun multiple => 0 < multiple),
    ropeCollisionPairCountAtGap context (multiple * commonGap)

/-- The least common multiple of a finite integer-period RoPE bank.

For the empty bank this is `1`, matching the vacuous all-channel collision
predicate: every positive gap is a collision when no periods are declared. -/
def ropePeriodBankLCM : List Nat → Nat
  | [] => 1
  | period :: rest => Nat.lcm period (ropePeriodBankLCM rest)

/-- A declared positive-period bank has a positive least common multiple.

The Python certifier rejects zero periods. This theorem is the Lean-side guard
that turns that input validation into the positive-LCM precondition required by
the exact collision-witness and collision-count theorems. -/
theorem ropePeriodBankLCM_pos_of_forall_mem_pos
    {periods : List Nat} (hperiods : ∀ period, period ∈ periods → 0 < period) :
    0 < ropePeriodBankLCM periods := by
  induction periods with
  | nil =>
      simp [ropePeriodBankLCM]
  | cons period rest ih =>
      apply Nat.lcm_pos
      · exact hperiods period (by simp)
      · exact ih (by
          intro p hp
          exact hperiods p (by simp [hp]))

/-- There is at least one ordered pair separated by `gap` inside a context iff
the gap is strictly smaller than the context. -/
theorem ropeCollisionPairCountAtGap_pos_iff {context gap : Nat} :
    0 < ropeCollisionPairCountAtGap context gap ↔ gap < context := by
  unfold ropeCollisionPairCountAtGap
  exact Nat.sub_pos_iff_lt

/-- The positive-multiple collision count is positive exactly when the common
gap itself fits inside the inspected context.

This is the count-level bridge used by the certifier's
`total_bank_collision_pair_count`: if the least common collision gap reaches
the context, no positive multiple can contribute; if it is inside the context,
the first multiple already contributes a positive family. -/
theorem ropeCollisionPairCountAtGapMultiples_pos_iff
    {context commonGap : Nat} (hgap_pos : 0 < commonGap) :
    0 < ropeCollisionPairCountAtGapMultiples context commonGap ↔ commonGap < context := by
  constructor
  · intro hsum_pos
    by_contra hnot
    have hcontext_le_gap : context ≤ commonGap := le_of_not_gt hnot
    have hsum_zero : ropeCollisionPairCountAtGapMultiples context commonGap = 0 := by
      unfold ropeCollisionPairCountAtGapMultiples
      rw [Finset.sum_eq_zero_iff_of_nonneg]
      · intro multiple hmem
        rw [Finset.mem_filter] at hmem
        have hmultiple_pos : 0 < multiple := hmem.2
        have hgap_le_multiple : commonGap ≤ multiple * commonGap := by
          simpa [Nat.mul_comm] using Nat.le_mul_of_pos_left commonGap hmultiple_pos
        exact Nat.sub_eq_zero_iff_le.mpr (le_trans hcontext_le_gap hgap_le_multiple)
      · intro multiple _hmem
        exact Nat.zero_le _
    exact (Nat.ne_of_gt hsum_pos) hsum_zero
  · intro hgap_lt_context
    unfold ropeCollisionPairCountAtGapMultiples
    refine Finset.sum_pos' (fun multiple _hmem => Nat.zero_le _) ?_
    refine ⟨1, ?_, ?_⟩
    · rw [Finset.mem_filter]
      constructor
      · rw [Finset.mem_range]
        exact lt_of_le_of_lt (Nat.succ_le_of_lt hgap_pos) hgap_lt_context
      · exact Nat.zero_lt_one
    · simpa [Nat.one_mul] using
        (ropeCollisionPairCountAtGap_pos_iff
          (context := context) (gap := commonGap)).2 hgap_lt_context

/-- The quotient `(context - 1) / commonGap` is exactly the upper bound for the
positive common-gap multiples that fit inside the inspected context.

This is the theorem-backed loop bound used by the public certifier when it
reports how many positive LCM multiples contribute to the exact integer-bank
collision count. -/
theorem ropeCollisionPairCountFittingMultipleCount_spec
    {context commonGap multiple : Nat}
    (hgap_pos : 0 < commonGap) (hmultiple_pos : 0 < multiple) :
    multiple ≤ ropeCollisionPairCountFittingMultipleCount context commonGap ↔
      multiple * commonGap < context := by
  unfold ropeCollisionPairCountFittingMultipleCount
  constructor
  · intro hle
    have hmul_le :
        multiple * commonGap ≤ ((context - 1) / commonGap) * commonGap :=
      Nat.mul_le_mul_right commonGap hle
    have hdiv_mul_le :
        ((context - 1) / commonGap) * commonGap ≤ context - 1 :=
      Nat.div_mul_le_self (context - 1) commonGap
    have hprod_le_pred : multiple * commonGap ≤ context - 1 :=
      le_trans hmul_le hdiv_mul_le
    have hprod_pos : 0 < multiple * commonGap :=
      Nat.mul_pos hmultiple_pos hgap_pos
    omega
  · intro hlt
    have hprod_le_pred : multiple * commonGap ≤ context - 1 := by
      omega
    exact (Nat.le_div_iff_mul_le hgap_pos).2 hprod_le_pred

/-- The positive-multiple collision count can be computed by summing only over
the exact quotient-bounded fitting range.

The original definition ranges over all positive multiples below `context`;
this theorem proves that every multiple beyond `(context - 1) / commonGap`
contributes zero, and every multiple up to that bound is already in the
original range. -/
theorem ropeCollisionPairCountAtGapMultiples_eq_fittingRange
    {context commonGap : Nat} (hgap_pos : 0 < commonGap) :
    ropeCollisionPairCountAtGapMultiples context commonGap =
      ropeCollisionPairCountAtGapMultiplesFittingRange context commonGap := by
  unfold ropeCollisionPairCountAtGapMultiples
    ropeCollisionPairCountAtGapMultiplesFittingRange
  let q := ropeCollisionPairCountFittingMultipleCount context commonGap
  let small : Finset Nat := (Finset.range (q + 1)).filter (fun multiple => 0 < multiple)
  let big : Finset Nat := (Finset.range context).filter (fun multiple => 0 < multiple)
  have hsubset : small ⊆ big := by
    intro multiple hmem
    rw [Finset.mem_filter] at hmem ⊢
    rcases hmem with ⟨hmultiple_range, hmultiple_pos⟩
    rw [Finset.mem_range] at hmultiple_range
    have hmultiple_le_q : multiple ≤ q := Nat.lt_succ_iff.mp hmultiple_range
    have hmultiple_gap_lt_context : multiple * commonGap < context :=
      (ropeCollisionPairCountFittingMultipleCount_spec
        (context := context) (commonGap := commonGap) (multiple := multiple)
        hgap_pos hmultiple_pos).1 hmultiple_le_q
    have hmultiple_le_gap : multiple ≤ multiple * commonGap := by
      simpa [Nat.mul_comm] using Nat.le_mul_of_pos_left multiple hgap_pos
    exact ⟨by
      rw [Finset.mem_range]
      exact lt_of_le_of_lt hmultiple_le_gap hmultiple_gap_lt_context, hmultiple_pos⟩
  have hsmall_eq_big :
      (∑ multiple ∈ small, ropeCollisionPairCountAtGap context (multiple * commonGap)) =
        ∑ multiple ∈ big, ropeCollisionPairCountAtGap context (multiple * commonGap) := by
    refine Finset.sum_subset hsubset ?_
    intro multiple hmem_big hmem_not_small
    rw [Finset.mem_filter] at hmem_big
    have hmultiple_pos : 0 < multiple := hmem_big.2
    have hnot_le_q : ¬ multiple ≤ q := by
      intro hle
      apply hmem_not_small
      rw [Finset.mem_filter]
      exact ⟨by
        rw [Finset.mem_range]
        exact Nat.lt_succ_iff.mpr hle, hmultiple_pos⟩
    have hnot_gap_lt_context : ¬ multiple * commonGap < context := by
      intro hlt
      exact hnot_le_q
        ((ropeCollisionPairCountFittingMultipleCount_spec
          (context := context) (commonGap := commonGap) (multiple := multiple)
          hgap_pos hmultiple_pos).2 hlt)
    unfold ropeCollisionPairCountAtGap
    exact Nat.sub_eq_zero_iff_le.mpr (le_of_not_gt hnot_gap_lt_context)
  exact hsmall_eq_big.symm

/-- A closed-form doubled sum for positive multiples that all fit.

The right side is the triangular-number numerator for the collision-pair
count over the positive multiples `1, ..., q`. The factor `2 *` avoids
introducing a divisibility side condition into the core arithmetic theorem. -/
theorem ropePositiveRangeCollisionPairCount_twice_eq_closedForm
    {context commonGap q : Nat} (hfit : q * commonGap < context) :
    2 * (∑ multiple ∈ (Finset.range (q + 1)).filter (fun multiple => 0 < multiple),
      (context - multiple * commonGap)) =
    q * (2 * context - commonGap * (q + 1)) := by
  induction q with
  | zero =>
      simp
  | succ q ih =>
      have hq_fit : q * commonGap < context := by
        exact lt_of_le_of_lt (Nat.mul_le_mul_right commonGap (Nat.le_succ q)) hfit
      have ih' := ih hq_fit
      rw [show Nat.succ q + 1 = q + 1 + 1 by omega]
      rw [Finset.range_add_one]
      rw [Finset.filter_insert]
      simp only [Nat.succ_pos, ↓reduceIte]
      rw [Finset.sum_insert]
      · rw [mul_add, ih']
        have hlast_le : (q + 1) * commonGap ≤ context := le_of_lt hfit
        have hg_le_context : commonGap ≤ context := by
          have hle_mul : commonGap ≤ (q + 1) * commonGap := by
            simpa [Nat.mul_comm] using Nat.le_mul_of_pos_left commonGap (Nat.succ_pos q)
          exact le_trans hle_mul hlast_le
        have hprev_inner_le : commonGap * (q + 1) ≤ 2 * context := by
          rw [Nat.mul_add]
          rw [Nat.mul_one]
          rw [Nat.mul_comm commonGap q]
          omega
        have hnext_inner_le : commonGap * (q + 1 + 1) ≤ 2 * context := by
          rw [Nat.mul_add]
          rw [Nat.mul_one]
          rw [Nat.mul_comm commonGap (q + 1)]
          omega
        apply Int.ofNat.inj
        norm_num [Nat.cast_sub hlast_le, Nat.cast_sub hprev_inner_le, Nat.cast_sub hnext_inner_le]
        ring
      · exact by
          rw [Finset.mem_filter]
          exact fun h => Finset.notMem_range_self h.1

/-- The quotient-bounded fitting-range collision count has a checked doubled
closed form.

For `q = (context - 1) / commonGap`, the executable loop over positive
contributing multiples satisfies
`2 * count = q * (2 * context - commonGap * (q + 1))`. -/
theorem ropeCollisionPairCountAtGapMultiplesFittingRange_twice_eq_closedForm
    {context commonGap : Nat} (hgap_pos : 0 < commonGap) :
    2 * ropeCollisionPairCountAtGapMultiplesFittingRange context commonGap =
      let q := ropeCollisionPairCountFittingMultipleCount context commonGap
      q * (2 * context - commonGap * (q + 1)) := by
  unfold ropeCollisionPairCountAtGapMultiplesFittingRange
  let q := ropeCollisionPairCountFittingMultipleCount context commonGap
  by_cases hq_pos : 0 < q
  · have hfit : q * commonGap < context :=
      (ropeCollisionPairCountFittingMultipleCount_spec
        (context := context) (commonGap := commonGap) (multiple := q)
        hgap_pos hq_pos).1 le_rfl
    simpa [q, ropeCollisionPairCountAtGap] using
      (ropePositiveRangeCollisionPairCount_twice_eq_closedForm
        (context := context) (commonGap := commonGap) (q := q) hfit)
  · have hq_zero : q = 0 := Nat.eq_zero_of_not_pos hq_pos
    simp [q, hq_zero, ropeCollisionPairCountAtGap]

/-- The full positive-multiple collision count has the same checked doubled
closed form, because the full count reduces to the exact fitting range. -/
theorem ropeCollisionPairCountAtGapMultiples_twice_eq_closedForm
    {context commonGap : Nat} (hgap_pos : 0 < commonGap) :
    2 * ropeCollisionPairCountAtGapMultiples context commonGap =
      let q := ropeCollisionPairCountFittingMultipleCount context commonGap
      q * (2 * context - commonGap * (q + 1)) := by
  rw [ropeCollisionPairCountAtGapMultiples_eq_fittingRange hgap_pos]
  exact ropeCollisionPairCountAtGapMultiplesFittingRange_twice_eq_closedForm
    (context := context) (commonGap := commonGap) hgap_pos

/-- Exact closed form for the positive-multiple collision count.

This divides the checked doubled numerator by two. The previous theorem proves
that the numerator is exactly twice the count, so this statement is the direct
formula used by the executable certifier. -/
theorem ropeCollisionPairCountAtGapMultiples_eq_closedForm
    {context commonGap : Nat} (hgap_pos : 0 < commonGap) :
    ropeCollisionPairCountAtGapMultiples context commonGap =
      (let q := ropeCollisionPairCountFittingMultipleCount context commonGap;
        q * (2 * context - commonGap * (q + 1))) / 2 := by
  exact Nat.eq_div_of_mul_eq_right (by decide)
    (ropeCollisionPairCountAtGapMultiples_twice_eq_closedForm
      (context := context) (commonGap := commonGap) hgap_pos)

/-- When exactly the first positive multiple of a common collision gap can fit
inside the inspected context, the total positive-multiple collision-pair count
collapses to the single-gap count `context - commonGap`.

This is the closed-form boundary used by the public certifier for rows just
past the first repeat: there are no contributions from `2 * commonGap`,
`3 * commonGap`, and so on. -/
theorem ropeCollisionPairCountAtGapMultiples_eq_single_gap_count
    {context commonGap : Nat} (hgap_pos : 0 < commonGap)
    (hgap_lt_context : commonGap < context) (hcontext_le_two_gap : context ≤ 2 * commonGap) :
    ropeCollisionPairCountAtGapMultiples context commonGap = context - commonGap := by
  unfold ropeCollisionPairCountAtGapMultiples
  let singleton : Finset Nat := {1}
  have hsubset : singleton ⊆ (Finset.range context).filter (fun multiple => 0 < multiple) := by
    intro multiple hmem
    simp [singleton] at hmem
    subst multiple
    rw [Finset.mem_filter]
    constructor
    · rw [Finset.mem_range]
      exact lt_of_le_of_lt (Nat.succ_le_of_lt hgap_pos) hgap_lt_context
    · exact Nat.zero_lt_one
  have hsum_singleton :
      (∑ multiple ∈ singleton, ropeCollisionPairCountAtGap context (multiple * commonGap)) =
        context - commonGap := by
    simp [singleton, ropeCollisionPairCountAtGap]
  have hbig_eq_singleton :
      (∑ multiple ∈ singleton, ropeCollisionPairCountAtGap context (multiple * commonGap)) =
      ∑ multiple ∈ (Finset.range context).filter (fun multiple => 0 < multiple),
        ropeCollisionPairCountAtGap context (multiple * commonGap) := by
    refine Finset.sum_subset hsubset ?_
    intro multiple hmem_big hmem_not_singleton
    rw [Finset.mem_filter] at hmem_big
    have hmultiple_pos : 0 < multiple := hmem_big.2
    have hmultiple_ne_one : multiple ≠ 1 := by
      intro h
      apply hmem_not_singleton
      simp [singleton, h]
    have htwo_le_multiple : 2 ≤ multiple := by omega
    have htwo_gap_le : 2 * commonGap ≤ multiple * commonGap :=
      Nat.mul_le_mul_right commonGap htwo_le_multiple
    unfold ropeCollisionPairCountAtGap
    exact Nat.sub_eq_zero_iff_le.mpr (le_trans hcontext_le_two_gap htwo_gap_le)
  exact hbig_eq_singleton ▸ hsum_singleton

/-- At the first-repeat boundary `context = commonGap + 1`, the
positive-multiple collision-pair count is exactly one.

This is the named theorem behind boundary diagnostics such as a period-`960`
channel inspected at context `961`: the only colliding pair is separated by the
period itself. -/
theorem ropeCollisionPairCountAtGapMultiples_period_succ_eq_one
    {commonGap : Nat} (hgap_pos : 0 < commonGap) :
    ropeCollisionPairCountAtGapMultiples (commonGap + 1) commonGap = 1 := by
  rw [ropeCollisionPairCountAtGapMultiples_eq_single_gap_count
    (context := commonGap + 1) (commonGap := commonGap)
    hgap_pos (Nat.lt_succ_self commonGap) (by omega)]
  omega

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

/-- The exact positive-multiple LCM collision count is zero iff the period-bank
LCM reaches the inspected context.

The Python certifier's `total_bank_collision_pair_count` uses the same
positive-multiple sum for the declared integer-period bank. This theorem is the
count-level pass/fail companion to the LCM collision iff: under a positive LCM,
the total all-channel integer-bank collision count is zero exactly when the
least common collision gap is outside the context. -/
theorem ropeLCMCollisionPairCountMultiples_eq_zero_iff
    {periods : List Nat} {context : Nat}
    (hlcm_pos : 0 < ropePeriodBankLCM periods) :
    ropeCollisionPairCountAtGapMultiples context (ropePeriodBankLCM periods) = 0 ↔
      context ≤ ropePeriodBankLCM periods := by
  constructor
  · intro hzero
    by_contra hnot
    have hlcm_lt_context : ropePeriodBankLCM periods < context := lt_of_not_ge hnot
    have hpos : 0 < ropeCollisionPairCountAtGapMultiples context (ropePeriodBankLCM periods) :=
      (ropeCollisionPairCountAtGapMultiples_pos_iff
        (context := context) (commonGap := ropePeriodBankLCM periods) hlcm_pos).2
        hlcm_lt_context
    rw [hzero] at hpos
    exact Nat.lt_irrefl 0 hpos
  · intro hcontext_le_lcm
    by_contra hne
    have hpos : 0 < ropeCollisionPairCountAtGapMultiples context (ropePeriodBankLCM periods) :=
      Nat.pos_of_ne_zero hne
    have hlcm_lt_context : ropePeriodBankLCM periods < context :=
      (ropeCollisionPairCountAtGapMultiples_pos_iff
        (context := context) (commonGap := ropePeriodBankLCM periods) hlcm_pos).1 hpos
    exact (not_lt_of_ge hcontext_le_lcm) hlcm_lt_context

/-- The exact positive-multiple LCM collision count is positive iff an unequal
all-channel collision witness exists inside the inspected context.

This gives the public certificate count a direct semantic interpretation: for
a positive period-bank LCM, a nonzero `total_bank_collision_pair_count` is
equivalent to an actual pair of distinct in-context positions colliding in
every declared integer-period channel. -/
theorem ropeLCMCollisionPairCountMultiples_pos_iff_exists_collision
    {periods : List Nat} {context : Nat}
    (hlcm_pos : 0 < ropePeriodBankLCM periods) :
    0 < ropeCollisionPairCountAtGapMultiples context (ropePeriodBankLCM periods) ↔
      ∃ left right,
        left < right ∧ right < context ∧ ropePhaseBankCollision periods left right := by
  constructor
  · intro hcount_pos
    have hlcm_lt_context : ropePeriodBankLCM periods < context :=
      (ropeCollisionPairCountAtGapMultiples_pos_iff
        (context := context) (commonGap := ropePeriodBankLCM periods) hlcm_pos).1
        hcount_pos
    exact ropePhaseBankCollision_exists_of_lcm_pos_lt_context hlcm_pos hlcm_lt_context
  · intro hwitness
    rcases hwitness with ⟨left, right, hleft, hright, hcollision⟩
    have hle : left ≤ right := Nat.le_of_lt hleft
    have hdvd : ropePeriodBankLCM periods ∣ right - left :=
      (ropePhaseBankCollision_iff_lcm_dvd_gap (periods := periods) hle).1 hcollision
    have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
    have hlcm_le_gap : ropePeriodBankLCM periods ≤ right - left :=
      Nat.le_of_dvd hgap_pos hdvd
    have hgap_lt_context : right - left < context :=
      lt_of_le_of_lt (Nat.sub_le right left) hright
    have hlcm_lt_context : ropePeriodBankLCM periods < context :=
      lt_of_le_of_lt hlcm_le_gap hgap_lt_context
    exact (ropeCollisionPairCountAtGapMultiples_pos_iff
      (context := context) (commonGap := ropePeriodBankLCM periods) hlcm_pos).2
      hlcm_lt_context

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

/-- For a positive-period phase bank, exact context distinguishability is
equivalent to the period-bank LCM reaching the context.

This is the end-to-end exact discrete pass/fail contract behind
`exact_discrete_contract`: if the LCM reaches the context, every unequal
in-context pair is separated by at least one declared period; if the LCM falls
inside the context, the LCM itself supplies an unequal all-channel collision
witness. -/
theorem ropePhaseBankNoCollisionOnContext_iff_lcm_ge_context_of_forall_mem_pos
    {periods : List Nat} {context : Nat}
    (hperiods : ∀ period, period ∈ periods → 0 < period) :
    (∀ left right,
        left < right → right < context → ¬ ropePhaseBankCollision periods left right) ↔
      context ≤ ropePeriodBankLCM periods := by
  constructor
  · intro hnoCollision
    by_contra hnot
    have hlcm_lt_context : ropePeriodBankLCM periods < context := lt_of_not_ge hnot
    have hlcm_pos : 0 < ropePeriodBankLCM periods :=
      ropePeriodBankLCM_pos_of_forall_mem_pos hperiods
    rcases ropePhaseBankCollision_exists_of_lcm_pos_lt_context
        (periods := periods) (context := context) hlcm_pos hlcm_lt_context with
      ⟨left, right, hleft, hright, hcollision⟩
    exact hnoCollision left right hleft hright hcollision
  · intro hlcm_context left right hleft hright
    exact not_ropePhaseBankCollision_of_lcm_ge_context
      (periods := periods) (context := context) (left := left) (right := right)
      hlcm_context hleft hright

/-- For a positive-period phase bank, exact no-collision over a finite context
is equivalent to the reported total integer-bank collision count being zero.

This is the direct public-certificate bridge between the boolean
`exact_discrete_contract` field and the numeric `total_bank_collision_pair_count`
field: both are just two views of the same LCM criterion. -/
theorem ropePhaseBankNoCollisionOnContext_iff_lcmCollisionPairCount_eq_zero_of_forall_mem_pos
    {periods : List Nat} {context : Nat}
    (hperiods : ∀ period, period ∈ periods → 0 < period) :
    (∀ left right,
        left < right → right < context → ¬ ropePhaseBankCollision periods left right) ↔
      ropeCollisionPairCountAtGapMultiples context (ropePeriodBankLCM periods) = 0 := by
  rw [ropePhaseBankNoCollisionOnContext_iff_lcm_ge_context_of_forall_mem_pos
    (periods := periods) (context := context) hperiods]
  rw [ropeLCMCollisionPairCountMultiples_eq_zero_iff
    (periods := periods) (context := context)
    (ropePeriodBankLCM_pos_of_forall_mem_pos hperiods)]

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

/-- A prefix length is a passing integer-period RoPE prefix when it is a
nonempty prefix of the declared bank and its LCM reaches the inspected
context. -/
def ropePrefixPassesContext
    (context : Nat) (periods : List Nat) (prefixLength : Nat) : Prop :=
  0 < prefixLength ∧
    prefixLength ≤ periods.length ∧
      context ≤ ropePeriodBankLCM (periods.take prefixLength)

/-- A prefix length is the first passing prefix when it passes and every
shorter nonempty prefix has LCM below the inspected context. -/
def ropeFirstPrefixPassesContext
    (context : Nat) (periods : List Nat) (prefixLength : Nat) : Prop :=
  ropePrefixPassesContext context periods prefixLength ∧
    ∀ shorter,
      0 < shorter → shorter < prefixLength →
        ropePeriodBankLCM (periods.take shorter) < context

/-- The first passing prefix length, when certified, is unique.

This is the theorem-side contract behind the public
`first_exact_pass_prefix_length` field: two prefix lengths cannot both be the
first prefix whose LCM reaches the inspected context. -/
theorem ropeFirstPrefixPassesContext_unique
    {context : Nat} {periods : List Nat} {leftPrefix rightPrefix : Nat}
    (hleft : ropeFirstPrefixPassesContext context periods leftPrefix)
    (hright : ropeFirstPrefixPassesContext context periods rightPrefix) :
    leftPrefix = rightPrefix := by
  by_cases hlt : leftPrefix < rightPrefix
  · have hfail := hright.2 leftPrefix hleft.1.1 hlt
    exact False.elim ((not_le_of_gt hfail) hleft.1.2.2)
  · by_cases hgt : rightPrefix < leftPrefix
    · have hfail := hleft.2 rightPrefix hright.1.1 hgt
      exact False.elim ((not_le_of_gt hfail) hright.1.2.2)
    · omega

/-- A certified first passing prefix forbids unequal all-channel collisions in
the full declared bank.

This packages the prefix report into the same no-collision contract as the
full-bank LCM theorem: once the first passing prefix has LCM reaching the
context, adding the remaining suffix channels cannot create a new unequal
all-channel collision. -/
theorem not_ropePhaseBankCollision_of_firstPrefixPassesContext
    {periods : List Nat} {context prefixLength left right : Nat}
    (hfirst : ropeFirstPrefixPassesContext context periods prefixLength)
    (hleft : left < right) (hright : right < context) :
    ¬ ropePhaseBankCollision periods left right := by
  have hprefix_no_collision :
      ¬ ropePhaseBankCollision
        (periods.take prefixLength ++ periods.drop prefixLength) left right :=
    not_ropePhaseBankCollision_of_prefix_lcm_ge_context
      (pref := periods.take prefixLength) (suffix := periods.drop prefixLength)
      (context := context) (left := left) (right := right)
      hfirst.1.2.2 hleft hright
  simpa [List.take_append_drop] using hprefix_no_collision

/-- A selected subfamily passes an integer-period RoPE context when it is
contained in the declared bank and its LCM reaches the inspected context. -/
def ropeSubfamilyPassesContext
    (context : Nat) (bank subbank : List Nat) : Prop :=
  (∀ period, period ∈ subbank → period ∈ bank) ∧
    context ≤ ropePeriodBankLCM subbank

/-- A selected subfamily has smallest passing size when it passes and every
strictly smaller contained subfamily has LCM below the inspected context. -/
def ropeSmallestSubfamilyPassesContext
    (context : Nat) (bank subbank : List Nat) : Prop :=
  ropeSubfamilyPassesContext context bank subbank ∧
    ∀ smaller,
      (∀ period, period ∈ smaller → period ∈ bank) →
        smaller.length < subbank.length →
          ropePeriodBankLCM smaller < context

/-- The size of a smallest passing subfamily, when certified, is unique.

The actual subfamily need not be unique: several different selected channel
sets can have the same minimal size. The report field
`smallest_pass_subfamily_size` is therefore the stable theorem-backed object,
not a claim that Python found the only sufficient subfamily. -/
theorem ropeSmallestSubfamilyPassesContext_size_unique
    {context : Nat} {bank leftSubbank rightSubbank : List Nat}
    (hleft : ropeSmallestSubfamilyPassesContext context bank leftSubbank)
    (hright : ropeSmallestSubfamilyPassesContext context bank rightSubbank) :
    leftSubbank.length = rightSubbank.length := by
  by_cases hlt : leftSubbank.length < rightSubbank.length
  · have hfail := hright.2 leftSubbank hleft.1.1 hlt
    exact False.elim ((not_le_of_gt hfail) hleft.1.2)
  · by_cases hgt : rightSubbank.length < leftSubbank.length
    · have hfail := hleft.2 rightSubbank hright.1.1 hgt
      exact False.elim ((not_le_of_gt hfail) hright.1.2)
    · omega

/-- A smallest passing subfamily certificate forbids unequal all-channel
collisions in the full declared bank.

This packages a minimal-size subfamily report into the same no-collision
contract as the unordered subbank bridge. The minimality part is not needed for
no-collision, but it ties the public `smallest_pass_subfamily_size` field to a
semantic guarantee about the full bank. -/
theorem not_ropePhaseBankCollision_of_smallestSubfamilyPassesContext
    {bank subbank : List Nat} {context left right : Nat}
    (hsmallest : ropeSmallestSubfamilyPassesContext context bank subbank)
    (hleft : left < right) (hright : right < context) :
    ¬ ropePhaseBankCollision bank left right :=
  not_ropePhaseBankCollision_of_subbank_lcm_ge_context
    (subbank := subbank) (bank := bank) (context := context)
    (left := left) (right := right)
    hsmallest.1.1 hsmallest.1.2 hleft hright

/-- The diagnostic prefix preset `[6, 9, 13, 18]` first reaches context `128`
at prefix length `3`.

This theorem backs the public `first_exact_pass_prefix_length = 3` report for
the bounded diagnostic prefix fixture. It is a concrete finite certificate, not
a general theorem about all RoPE period banks. -/
theorem ropeDiagnosticPrefixPass_context128_firstPrefix_length_three :
    ropePeriodBankLCM [6] < 128 ∧
      ropePeriodBankLCM [6, 9] < 128 ∧
        128 ≤ ropePeriodBankLCM [6, 9, 13] := by
  native_decide

/-- The diagnostic prefix preset satisfies the generic first-prefix contract at
length `3`.

This connects the public diagnostic report to the reusable
`ropeFirstPrefixPassesContext` predicate rather than only to a hand-written
triple of LCM inequalities. -/
theorem ropeDiagnosticPrefixPass_context128_firstPrefixPasses_three :
    ropeFirstPrefixPassesContext 128 [6, 9, 13, 18] 3 := by
  refine ⟨⟨by native_decide, by native_decide, by native_decide⟩, ?_⟩
  intro shorter hpos hlt
  interval_cases shorter <;> native_decide

/-- The diagnostic prefix preset `[6, 9, 13, 18]` has no singleton subbank
whose LCM reaches context `128`, while the subbank `[13, 18]` does.

This theorem backs the public `smallest_pass_subfamily_size = 2` report for
the bounded diagnostic prefix fixture. The bounded Python report still records
which subfamily was found; this Lean fact certifies the size boundary for the
named finite case. -/
theorem ropeDiagnosticPrefixPass_context128_smallestSubfamily_size_two :
    (∀ period, period ∈ ([6, 9, 13, 18] : List Nat) →
      ropePeriodBankLCM [period] < 128) ∧
      128 ≤ ropePeriodBankLCM [13, 18] := by
  native_decide

/-- The diagnostic prefix preset satisfies the generic smallest-subfamily
contract for the selected subfamily `[13, 18]`.

This upgrades the public `smallest_pass_subfamily_size = 2` diagnostic field
from a pair of concrete LCM facts to the reusable minimal-size predicate. -/
theorem ropeDiagnosticPrefixPass_context128_smallestSubfamilyPasses_13_18 :
    ropeSmallestSubfamilyPassesContext 128 [6, 9, 13, 18] [13, 18] := by
  refine ⟨⟨by native_decide, by native_decide⟩, ?_⟩
  intro smaller hsubset hlt
  cases smaller with
  | nil =>
      native_decide
  | cons period rest =>
      cases rest with
      | nil =>
          exact (ropeDiagnosticPrefixPass_context128_smallestSubfamily_size_two).1
            period (hsubset period (by simp))
      | cons _ tail =>
          simp at hlt

/-! ### Named finite diagnostic count certificates -/

/-- The public diagnostic shared-factor RoPE row has exact integer-bank
collision count `10`.

The rounded diagnostic periods are `[6, 18, 54]`, their period-bank LCM is
`54`, and the only positive in-context LCM multiple inside context `64` is
gap `54`, giving starts `0` through `9`. -/
theorem ropeDiagnosticSharedFactor_context64_totalCollisionPairCount :
    ropeCollisionPairCountAtGapMultiples 64
      (ropePeriodBankLCM [6, 18, 54]) = 10 := by
  native_decide

/-- The public quantized shared-factor phase-bank row has exact integer-bank
collision count `224`.

For periods `[32, 48, 96]` and context `256`, the LCM is `96`; the positive
in-context multiples are gaps `96` and `192`, contributing `160 + 64`
ordered starts. -/
theorem ropeQuantizedSharedFactor_context256_totalCollisionPairCount :
    ropeCollisionPairCountAtGapMultiples 256
      (ropePeriodBankLCM [32, 48, 96]) = 224 := by
  native_decide

/-- The public quantized boundary-fail phase-bank row has exact integer-bank
collision count `1`.

For periods `[15, 16]` and context `241`, the LCM gap is `240`, so exactly one
ordered start, `0`, has a paired position at `240` inside the context. -/
theorem ropeQuantizedBoundary_context241_totalCollisionPairCount :
    ropeCollisionPairCountAtGapMultiples 241
      (ropePeriodBankLCM [15, 16]) = 1 := by
  native_decide

/-- The public scaled-period boundary-pass phase-bank row has exact
integer-bank collision count `0`.

For periods `[60, 64]` and context `960`, the LCM is exactly the context
length, so no positive LCM-multiple gap has a positive number of starts. -/
theorem ropeInterpolatedX4_context960_totalCollisionPairCount :
    ropeCollisionPairCountAtGapMultiples 960
      (ropePeriodBankLCM [60, 64]) = 0 := by
  native_decide

/-- The public scaled-period one-token-past-boundary phase-bank row has exact
integer-bank collision count `1`.

For periods `[60, 64]` and context `961`, the LCM gap is `960`, so exactly one
ordered start, `0`, has a paired position at `960` inside the context. -/
theorem ropeInterpolatedX4_context961_totalCollisionPairCount :
    ropeCollisionPairCountAtGapMultiples 961
      (ropePeriodBankLCM [60, 64]) = 1 := by
  native_decide

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

/-- A single positive integer-period channel has no unequal in-context
collisions exactly when its period reaches the inspected context.

This is the engineer-facing single-channel threshold: a channel with period
`period` can distinguish all positions in `[0, context)` precisely up to the
point where the context length exceeds that period. -/
theorem ropeDiscreteNoCollisionOnContext_iff_context_le_period
    {period context : Nat} (hperiod : 0 < period) :
    (∀ left right,
        left < right → right < context → ¬ ropeDiscreteCollision period left right) ↔
      context ≤ period := by
  constructor
  · intro hno_collision
    by_contra hnot
    have hperiod_lt_context : period < context := lt_of_not_ge hnot
    have hcollision : ropeDiscreteCollision period 0 period :=
      (ropeDiscreteCollision_iff_gap_dvd
        (period := period) (left := 0) (right := period)
        (Nat.zero_le period)).2
        (dvd_refl period)
    exact hno_collision 0 period hperiod hperiod_lt_context hcollision
  · intro hcontext_le left right hleft hright hcollision
    have hleft_context : left < context := lt_trans hleft hright
    have heq : left = right :=
      (ropeDiscreteCollision_iff_eq_on_context
        (period := period) (context := context) hcontext_le
        hleft_context hright).1
        hcollision
    exact (ne_of_lt hleft) heq

/-- A single positive integer-period channel has a positive collision-pair count
exactly when there is an unequal in-context collision witness.

This is the fail-side companion to the zero-count theorem: a nonzero
`single_period_collision_pair_counts` entry is not just a diagnostic number; it
means there exists a concrete ordered position pair that collides in that
channel. -/
theorem ropeDiscreteCollisionPairCount_pos_iff_exists_collision
    {period context : Nat} (hperiod : 0 < period) :
    0 < ropeCollisionPairCountAtGapMultiples context period ↔
      ∃ left right,
        left < right ∧ right < context ∧ ropeDiscreteCollision period left right := by
  constructor
  · intro hcount_pos
    have hperiod_lt_context : period < context :=
      (ropeCollisionPairCountAtGapMultiples_pos_iff
        (context := context) (commonGap := period) hperiod).1
        hcount_pos
    have hcollision : ropeDiscreteCollision period 0 period :=
      (ropeDiscreteCollision_iff_gap_dvd
        (period := period) (left := 0) (right := period)
        (Nat.zero_le period)).2
        (dvd_refl period)
    exact ⟨0, period, hperiod, hperiod_lt_context, hcollision⟩
  · intro hwitness
    rcases hwitness with ⟨left, right, hleft, hright, hcollision⟩
    have hle : left ≤ right := Nat.le_of_lt hleft
    have hdvd : period ∣ right - left :=
      (ropeDiscreteCollision_iff_gap_dvd (period := period) hle).1 hcollision
    have hgap_pos : 0 < right - left := Nat.sub_pos_of_lt hleft
    have hperiod_le_gap : period ≤ right - left :=
      Nat.le_of_dvd hgap_pos hdvd
    have hgap_lt_context : right - left < context :=
      lt_of_le_of_lt (Nat.sub_le right left) hright
    have hperiod_lt_context : period < context :=
      lt_of_le_of_lt hperiod_le_gap hgap_lt_context
    exact (ropeCollisionPairCountAtGapMultiples_pos_iff
      (context := context) (commonGap := period) hperiod).2
      hperiod_lt_context

/-- For a single positive integer-period channel, the per-channel positive
multiple collision count is zero exactly when that channel has no unequal
in-context collision.

This is the theorem-backed interpretation of the Python certifier's
`single_period_collision_pair_counts` field: the count is not just a diagnostic
number. Zero is equivalent to a semantic no-collision contract for that one
declared period. -/
theorem ropeDiscreteNoCollisionOnContext_iff_collisionPairCount_eq_zero
    {period context : Nat} (hperiod : 0 < period) :
    (∀ left right,
        left < right → right < context → ¬ ropeDiscreteCollision period left right) ↔
      ropeCollisionPairCountAtGapMultiples context period = 0 := by
  have hcount_zero_iff_context_le :
      ropeCollisionPairCountAtGapMultiples context period = 0 ↔
        context ≤ period := by
    constructor
    · intro hzero
      by_contra hnot
      have hperiod_lt_context : period < context := lt_of_not_ge hnot
      have hpos : 0 < ropeCollisionPairCountAtGapMultiples context period :=
        (ropeCollisionPairCountAtGapMultiples_pos_iff
          (context := context) (commonGap := period) hperiod).2
          hperiod_lt_context
      rw [hzero] at hpos
      exact (Nat.lt_irrefl 0) hpos
    · intro hcontext_le
      by_contra hne
      have hpos : 0 < ropeCollisionPairCountAtGapMultiples context period :=
        Nat.pos_of_ne_zero hne
      have hperiod_lt_context : period < context :=
        (ropeCollisionPairCountAtGapMultiples_pos_iff
          (context := context) (commonGap := period) hperiod).1 hpos
      exact (not_lt_of_ge hcontext_le) hperiod_lt_context
  rw [ropeDiscreteNoCollisionOnContext_iff_context_le_period hperiod,
    hcount_zero_iff_context_le]

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

/-- One near-integer witness obstructs a finite-context turn-ratio margin.

This is the generic proof shape behind the standard channel-0 gap-`710`
negative certificates: if one inspected positive gap is already closer to an
integer turn than the advertised margin, then the whole finite-context margin
predicate cannot hold for any context containing that gap. -/
theorem not_ropeTurnRatioFiniteMargin_of_error_lt_margin
    {turnRatio margin : ℝ} {context gap : Nat} {turns : Int}
    (hgap_pos : 0 < gap) (hgap_context : gap < context)
    (herror : ropeTurnRatioError turnRatio gap turns < margin) :
    ¬ ropeTurnRatioFiniteMargin turnRatio margin context := by
  intro hmargin
  have hcertifies_gap := hmargin gap hgap_pos hgap_context turns
  linarith

/-- Failing a finite-context turn-ratio margin is exactly the existence of one
positive in-context gap and integer-turn witness whose error is below the
advertised margin.

This is the bidirectional negative-certificate contract behind obstruction
reports: an executable witness is not merely suggestive, and every failure of
the abstract finite-margin predicate has such a witness. -/
theorem not_ropeTurnRatioFiniteMargin_iff_exists_error_lt_margin
    {turnRatio margin : ℝ} {context : Nat} :
    ¬ ropeTurnRatioFiniteMargin turnRatio margin context ↔
      ∃ gap : Nat, 0 < gap ∧ gap < context ∧
        ∃ turns : Int, ropeTurnRatioError turnRatio gap turns < margin := by
  rw [ropeTurnRatioFiniteMargin]
  push Not
  rfl

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

/-- The scalar nearest-integer margin for one turn-ratio gap.

This is the quantitative version of the floor/ceiling witness pair: it is the
smaller of the two endpoint errors that determine the distance from
`gap * turnRatio` to the nearest integer. -/
noncomputable def ropeTurnRatioGapNearestIntegerMargin
    (turnRatio : ℝ) (gap : Nat) : ℝ :=
  min
    |(gap : ℝ) * turnRatio - ((⌊(gap : ℝ) * turnRatio⌋ : ℤ) : ℝ)|
    |(gap : ℝ) * turnRatio - ((⌈(gap : ℝ) * turnRatio⌉ : ℤ) : ℝ)|

/-- Bounding the scalar nearest-integer margin for one gap is equivalent to
bounding both floor and ceiling endpoint errors.

This is the formal bridge behind certifier fields that report a single
`nearest_gap_margin` number while still citing the two-witness Lean proof
shape. -/
theorem ropeTurnRatioGapNearestIntegerMargin_ge_iff_floor_ceil
    {turnRatio margin : ℝ} {gap : Nat} :
    margin ≤ ropeTurnRatioGapNearestIntegerMargin turnRatio gap ↔
      margin ≤ |(gap : ℝ) * turnRatio - ((⌊(gap : ℝ) * turnRatio⌋ : ℤ) : ℝ)| ∧
        margin ≤ |(gap : ℝ) * turnRatio - ((⌈(gap : ℝ) * turnRatio⌉ : ℤ) : ℝ)| := by
  unfold ropeTurnRatioGapNearestIntegerMargin
  exact le_min_iff

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

/-- Finite-context turn-ratio margins are equivalent to lower-bounding the
scalar nearest-integer margin for every generated positive gap.

This packages the floor/ceiling witness bridge as a quantitative contract: a
certifier may report the weakest gap margin as a single scalar, and this
theorem states exactly how that scalar condition relates to the abstract
finite-context margin predicate. -/
theorem ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
    {turnRatio margin : ℝ} {context : Nat} :
    ropeTurnRatioFiniteMargin turnRatio margin context ↔
      ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
        margin ≤ ropeTurnRatioGapNearestIntegerMargin turnRatio gap := by
  rw [ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses]
  constructor
  · intro hwitnesses gap hgap_range hgap_pos
    exact
      (ropeTurnRatioGapNearestIntegerMargin_ge_iff_floor_ceil
        (turnRatio := turnRatio) (margin := margin) (gap := gap)).2
        (hwitnesses gap hgap_range hgap_pos)
  · intro hmargin gap hgap_range hgap_pos
    exact
      (ropeTurnRatioGapNearestIntegerMargin_ge_iff_floor_ceil
        (turnRatio := turnRatio) (margin := margin) (gap := gap)).1
        (hmargin gap hgap_range hgap_pos)

/-- A report-facing exact weakest-gap margin certificate.

It says that `witnessGap` is an inspected positive gap, that its scalar
nearest-integer margin is exactly the reported `margin`, and that no inspected
positive gap has a smaller scalar nearest-integer margin. This is the generic
Lean contract behind executable fields such as `exact_nearest_gap_margin` and
`exact_nearest_gap`. -/
def ropeTurnRatioExactWeakestGapMargin
    (turnRatio margin : ℝ) (context witnessGap : Nat) : Prop :=
  witnessGap ∈ List.range context ∧
    0 < witnessGap ∧
      ropeTurnRatioGapNearestIntegerMargin turnRatio witnessGap = margin ∧
        ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
          margin ≤ ropeTurnRatioGapNearestIntegerMargin turnRatio gap

/-- An exact weakest-gap certificate is equivalent to a finite-margin
certificate whose lower bound is attained at the reported witness gap.

The forward direction turns the report's global lower-bound claim into the
abstract finite-margin predicate. The reverse direction is how generated
certifiers can prove exact weakest-gap fields: prove the finite lower bound and
then prove the reported witness realizes it. -/
theorem ropeTurnRatioExactWeakestGapMargin_iff_finiteMargin_and_realized
    {turnRatio margin : ℝ} {context witnessGap : Nat} :
    ropeTurnRatioExactWeakestGapMargin turnRatio margin context witnessGap ↔
      witnessGap ∈ List.range context ∧
        0 < witnessGap ∧
          ropeTurnRatioGapNearestIntegerMargin turnRatio witnessGap = margin ∧
            ropeTurnRatioFiniteMargin turnRatio margin context := by
  constructor
  · intro hcert
    rcases hcert with ⟨hmem, hpos, hrealized, hlower⟩
    exact
      ⟨hmem, hpos, hrealized,
        (ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
          (turnRatio := turnRatio) (margin := margin) (context := context)).2
          hlower⟩
  · intro hcert
    rcases hcert with ⟨hmem, hpos, hrealized, hfinite⟩
    exact
      ⟨hmem, hpos, hrealized,
        (ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
          (turnRatio := turnRatio) (margin := margin) (context := context)).1
          hfinite⟩

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

/-- The finite nearest-integer certificate object is equivalent to the abstract
finite-context turn-ratio margin contract.

The forward direction is `RopeTurnRatioFiniteMarginCertificate.certifies`; the
reverse direction packages the nearest-integer witnesses supplied by
`ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses`. This gives Python and
Living Book certificate objects a bidirectional Lean statement to cite instead
of treating the named certificate as only a one-way proof payload. -/
theorem ropeTurnRatioFiniteMarginCertificate_iff_finiteMargin
    {turnRatio margin : ℝ} {context : Nat} :
    RopeTurnRatioFiniteMarginCertificate turnRatio margin context ↔
      ropeTurnRatioFiniteMargin turnRatio margin context := by
  constructor
  · intro certificate
    exact certificate.certifies
  · intro hmargin
    exact
      ⟨(ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses
        (turnRatio := turnRatio) (margin := margin) (context := context)).1
        hmargin⟩

/-- A positive finite-margin certificate rules out exact integer-turn hits.

This is the generic semantic bridge behind `zero_margin_witness = none` fields:
if a turn-ratio margin is strictly positive over a finite context, then no
positive generated gap in that context can have zero error against any integer
turn count. -/
theorem ropeTurnRatioFiniteMargin_pos_no_zero_error
    {turnRatio margin : ℝ} {context : Nat}
    (hmargin_pos : 0 < margin)
    (hfinite : ropeTurnRatioFiniteMargin turnRatio margin context) :
    ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
      ∀ turns : Int, ropeTurnRatioError turnRatio gap turns ≠ 0 := by
  intro gap hgap_range hgap_pos turns hzero
  have hbound : margin ≤ ropeTurnRatioError turnRatio gap turns :=
    hfinite gap hgap_pos (List.mem_range.mp hgap_range) turns
  rw [hzero] at hbound
  linarith

/-- One rational interval witness for a turn-ratio gap.

The rational interval `[lower, upper]` encloses `gap * turnRatio` and sits
inside a single integer cell `[cell + margin, cell + 1 - margin]`. This is the
exact-arithmetic shape needed by generated interval certificates: the
certificate never asks Lean to trust a floating-point scan. -/
def ropeTurnRatioIntervalWitness
    (turnRatio margin : ℝ) (gap : Nat) (lower upper : ℚ) (cell : Int) : Prop :=
  (lower : ℝ) ≤ (gap : ℝ) * turnRatio ∧
    (gap : ℝ) * turnRatio ≤ (upper : ℝ) ∧
      (cell : ℝ) + margin ≤ (lower : ℝ) ∧
        (upper : ℝ) ≤ (cell : ℝ) + 1 - margin

/-- Endpoint bounds for a whole gap band produce one interval witness inside
that band.

This is the reusable compression rule for generated interval certificates: a
generator may group consecutive gaps into a band with one integer cell,
then prove only the lower endpoint and upper endpoint inequalities for that
band. Monotonicity fills in every intermediate gap. -/
theorem ropeTurnRatioIntervalWitness_of_band_bounds
    {turnRatio margin lowerBound upperBound : ℝ}
    {gap start stop : Nat} {lower upper : ℚ} {cell : Int}
    (hlower_eval : (lower : ℝ) = (gap : ℝ) * lowerBound)
    (hupper_eval : (upper : ℝ) = (gap : ℝ) * upperBound)
    (hlower_turn : lowerBound ≤ turnRatio)
    (hupper_turn : turnRatio ≤ upperBound)
    (hlower_nonneg : 0 ≤ lowerBound)
    (hupper_nonneg : 0 ≤ upperBound)
    (hstart : start ≤ gap) (hstop : gap ≤ stop)
    (hcell_lower : (cell : ℝ) + margin ≤ (start : ℝ) * lowerBound)
    (hcell_upper : (stop : ℝ) * upperBound ≤ (cell : ℝ) + 1 - margin) :
    ropeTurnRatioIntervalWitness turnRatio margin gap lower upper cell := by
  have hgap_nonneg : 0 ≤ (gap : ℝ) := by positivity
  have hstart_le_gap_real : (start : ℝ) ≤ gap := by exact_mod_cast hstart
  have hgap_le_stop_real : (gap : ℝ) ≤ stop := by exact_mod_cast hstop
  constructor
  · rw [hlower_eval]
    exact mul_le_mul_of_nonneg_left hlower_turn hgap_nonneg
  constructor
  · rw [hupper_eval]
    exact mul_le_mul_of_nonneg_left hupper_turn hgap_nonneg
  constructor
  · rw [hlower_eval]
    exact
      le_trans hcell_lower
        (mul_le_mul_of_nonneg_right hstart_le_gap_real hlower_nonneg)
  · rw [hupper_eval]
    exact
      le_trans
        (mul_le_mul_of_nonneg_right hgap_le_stop_real hupper_nonneg)
        hcell_upper

/-- A first-class rational interval band for generated turn-ratio certificates.

The band stores a range of natural gaps, one integer cell, and rational lower
and upper bounds for the turn ratio. Generated certificates can emit a list of
these bands rather than expanding every gap as a separate Lean case. -/
structure RopeTurnRatioRationalIntervalBand where
  startGap : Nat
  endGap : Nat
  cell : Int
  lowerBound : ℚ
  upperBound : ℚ
  deriving DecidableEq

/-- A compact generated interval band when every band in a certificate shares
the same rational turn-ratio enclosure.

Large standard-channel certificates use one global lower/upper bound for
`1/(2*pi)` and many integer-cell gap bands. Keeping only the gap range and cell
in each generated row avoids repeating the same large rational constants in
every table entry; `toRationalIntervalBand` restores the ordinary band object
used by the proof bridge. -/
structure RopeTurnRatioUniformRationalIntervalBand where
  startGap : Nat
  endGap : Nat
  cell : Int
  deriving DecidableEq

/-- Restore a compact uniform band to the ordinary rational interval-band
record by attaching the shared lower and upper turn-ratio bounds. -/
def RopeTurnRatioUniformRationalIntervalBand.toRationalIntervalBand
    (lowerBound upperBound : ℚ)
    (band : RopeTurnRatioUniformRationalIntervalBand) :
    RopeTurnRatioRationalIntervalBand :=
  { startGap := band.startGap
    endGap := band.endGap
    cell := band.cell
    lowerBound := lowerBound
    upperBound := upperBound }

/-- Expand a compact uniform-band list into the ordinary band list consumed by
the rational-band interval-certificate theorem. -/
def ropeTurnRatioUniformRationalIntervalBands
    (lowerBound upperBound : ℚ)
    (bands : List RopeTurnRatioUniformRationalIntervalBand) :
    List RopeTurnRatioRationalIntervalBand :=
  bands.map (fun band => band.toRationalIntervalBand lowerBound upperBound)

/-- The compact endpoint-validity predicate for a uniform rational band.

The shared lower and upper turn-ratio bounds are parameters instead of fields
on every generated row. The global nonnegativity checks for those bounds are
handled once by the reflection bridge below. -/
def RopeTurnRatioUniformRationalIntervalBand.RatEndpointValid
    (band : RopeTurnRatioUniformRationalIntervalBand)
    (lowerBound upperBound margin : ℚ) : Prop :=
  (band.cell : ℚ) + margin ≤
    (band.startGap : ℚ) * lowerBound ∧
    (band.endGap : ℚ) * upperBound ≤
      (band.cell : ℚ) + 1 - margin

/-- A rational interval band covers a gap when the gap lies between its
declared endpoints. -/
def RopeTurnRatioRationalIntervalBand.CoversGap
    (band : RopeTurnRatioRationalIntervalBand) (gap : Nat) : Prop :=
  band.startGap ≤ gap ∧ gap ≤ band.endGap

/-- A rational interval band is valid for a turn ratio and margin when its
global rational bounds enclose the turn ratio and its endpoint inequalities
place the whole covered band inside the declared integer cell with that
margin. -/
def RopeTurnRatioRationalIntervalBand.Valid
    (band : RopeTurnRatioRationalIntervalBand) (turnRatio margin : ℝ) : Prop :=
  (band.lowerBound : ℝ) ≤ turnRatio ∧
    turnRatio ≤ (band.upperBound : ℝ) ∧
      0 ≤ (band.lowerBound : ℝ) ∧
        0 ≤ (band.upperBound : ℝ) ∧
          (band.cell : ℝ) + margin ≤ (band.startGap : ℝ) * (band.lowerBound : ℝ) ∧
            (band.endGap : ℝ) * (band.upperBound : ℝ) ≤
              (band.cell : ℝ) + 1 - margin

/-- The purely rational endpoint-validity predicate for a generated interval
band.

This is the executable side of the generated-band proof route: Python can
check these rational inequalities exactly, and the reflection theorem below
casts them into the real-valued `Valid` predicate used by the Lean interval
certificate bridge. -/
def RopeTurnRatioRationalIntervalBand.RatEndpointValid
    (band : RopeTurnRatioRationalIntervalBand) (margin : ℚ) : Prop :=
  0 ≤ band.lowerBound ∧
    0 ≤ band.upperBound ∧
      (band.cell : ℚ) + margin ≤
        (band.startGap : ℚ) * band.lowerBound ∧
        (band.endGap : ℚ) * band.upperBound ≤
          (band.cell : ℚ) + 1 - margin

/-- Rational endpoint-validity reflects into the real-valued band-validity
predicate.

Generated certificates can keep endpoint checks over `ℚ`; after supplying the
global real turn-ratio enclosure, this theorem produces the `Valid` hypothesis
required by the rational-band compression bridge. -/
theorem ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid
    {turnRatio : ℝ} {margin : ℚ}
    {band : RopeTurnRatioRationalIntervalBand}
    (hlower_turn : (band.lowerBound : ℝ) ≤ turnRatio)
    (hupper_turn : turnRatio ≤ (band.upperBound : ℝ))
    (hvalid : band.RatEndpointValid margin) :
    band.Valid turnRatio (margin : ℝ) := by
  rcases hvalid with
    ⟨hlower_nonneg, hupper_nonneg, hcell_lower, hcell_upper⟩
  refine ⟨hlower_turn, hupper_turn, ?_, ?_, ?_, ?_⟩
  · exact_mod_cast hlower_nonneg
  · exact_mod_cast hupper_nonneg
  · exact_mod_cast hcell_lower
  · exact_mod_cast hcell_upper

/-- Compact uniform endpoint checks reflect to ordinary rational-band endpoint
checks after attaching the shared lower and upper turn-ratio bounds. -/
theorem RopeTurnRatioUniformRationalIntervalBand.ratEndpointValid_toRationalIntervalBand
    {lowerBound upperBound margin : ℚ}
    {band : RopeTurnRatioUniformRationalIntervalBand}
    (hlower_nonneg : 0 ≤ lowerBound)
    (hupper_nonneg : 0 ≤ upperBound)
    (hvalid : band.RatEndpointValid lowerBound upperBound margin) :
    (band.toRationalIntervalBand lowerBound upperBound).RatEndpointValid margin := by
  rcases hvalid with ⟨hcell_lower, hcell_upper⟩
  exact ⟨hlower_nonneg, hupper_nonneg, hcell_lower, hcell_upper⟩

/-- A compact uniform-band endpoint audit proves endpoint validity for the
expanded rational bands consumed by the interval-certificate bridge. -/
theorem ropeTurnRatioUniformRationalIntervalBands_ratEndpointValid
    {lowerBound upperBound margin : ℚ}
    {compactBands : List RopeTurnRatioUniformRationalIntervalBand}
    (hlower_nonneg : 0 ≤ lowerBound)
    (hupper_nonneg : 0 ≤ upperBound)
    (hvalid :
      ∀ band, band ∈ compactBands →
        band.RatEndpointValid lowerBound upperBound margin) :
    ∀ band, band ∈
      ropeTurnRatioUniformRationalIntervalBands lowerBound upperBound compactBands →
      band.RatEndpointValid margin := by
  intro band hmem
  rcases List.mem_map.mp hmem with ⟨compactBand, hcompact_mem, hband_eq⟩
  rw [← hband_eq]
  exact
    RopeTurnRatioUniformRationalIntervalBand.ratEndpointValid_toRationalIntervalBand
      hlower_nonneg hupper_nonneg (hvalid compactBand hcompact_mem)

/-- A compact uniform-band endpoint audit proves real-valued validity for the
expanded rational bands after attaching a shared turn-ratio enclosure. -/
theorem ropeTurnRatioUniformRationalIntervalBands_valid_of_ratEndpointValid
    {turnRatio : ℝ} {lowerBound upperBound margin : ℚ}
    {compactBands : List RopeTurnRatioUniformRationalIntervalBand}
    (hlower_turn : (lowerBound : ℝ) ≤ turnRatio)
    (hupper_turn : turnRatio ≤ (upperBound : ℝ))
    (hlower_nonneg : 0 ≤ lowerBound)
    (hupper_nonneg : 0 ≤ upperBound)
    (hvalid :
      ∀ band, band ∈ compactBands →
        band.RatEndpointValid lowerBound upperBound margin) :
    ∀ band, band ∈
      ropeTurnRatioUniformRationalIntervalBands lowerBound upperBound compactBands →
      band.Valid turnRatio (margin : ℝ) := by
  intro band hmem
  rcases List.mem_map.mp hmem with ⟨compactBand, hcompact_mem, hband_eq⟩
  rw [← hband_eq]
  exact
    ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid
      hlower_turn
      hupper_turn
      (RopeTurnRatioUniformRationalIntervalBand.ratEndpointValid_toRationalIntervalBand
        hlower_nonneg hupper_nonneg (hvalid compactBand hcompact_mem))

/-- One valid rational interval band produces an interval witness for every
gap it covers.

This packages the endpoint monotonicity bridge in the exact shape needed by
generated RoPE interval plans: the lower and upper witnesses for a covered gap
are just `gap * lowerBound` and `gap * upperBound` in rational arithmetic. -/
theorem ropeTurnRatioIntervalWitness_of_rationalIntervalBand
    {turnRatio margin : ℝ} {gap : Nat}
    {band : RopeTurnRatioRationalIntervalBand}
    (hvalid : band.Valid turnRatio margin)
    (hcover : band.CoversGap gap) :
    ropeTurnRatioIntervalWitness turnRatio margin gap
      ((gap : ℚ) * band.lowerBound) ((gap : ℚ) * band.upperBound) band.cell := by
  rcases hvalid with
    ⟨hlower_turn, hupper_turn, hlower_nonneg, hupper_nonneg, hcell_lower,
      hcell_upper⟩
  rcases hcover with ⟨hstart, hstop⟩
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := turnRatio)
      (margin := margin)
      (lowerBound := (band.lowerBound : ℝ))
      (upperBound := (band.upperBound : ℝ))
      (gap := gap) (start := band.startGap) (stop := band.endGap)
      (lower := (gap : ℚ) * band.lowerBound)
      (upper := (gap : ℚ) * band.upperBound)
      (cell := band.cell)
      (by norm_num)
      (by norm_num)
      hlower_turn
      hupper_turn
      hlower_nonneg
      hupper_nonneg
      hstart
      hstop
      hcell_lower
      hcell_upper

/-- A finite rational band list covers a generated context when every positive
gap in `List.range context` lies in one of the listed bands. -/
def ropeTurnRatioRationalIntervalBandsCover
    (bands : List RopeTurnRatioRationalIntervalBand) (context : Nat) : Prop :=
  ∀ gap : Nat, gap ∈ List.range context → 0 < gap →
    ∃ band, band ∈ bands ∧ band.CoversGap gap

/-- A generated rational-band list is contiguous over the half-open gap range
`[next, stop)` when every row starts exactly where the previous row ended and
the final row reaches `stop - 1`.

This is a compact proof-build certificate for generated RoPE interval tables.
It avoids checking coverage by searching every gap against every band. -/
def ropeTurnRatioRationalIntervalBandsContiguousCover :
    List RopeTurnRatioRationalIntervalBand → Nat → Nat → Prop
  | [], next, stop => stop ≤ next
  | band :: tail, next, stop =>
      band.startGap = next ∧
        next ≤ band.endGap ∧
          band.endGap < stop ∧
            ropeTurnRatioRationalIntervalBandsContiguousCover
              tail (band.endGap + 1) stop

instance ropeTurnRatioRationalIntervalBandsContiguousCover_decidable
    (bands : List RopeTurnRatioRationalIntervalBand) (next stop : Nat) :
    Decidable (ropeTurnRatioRationalIntervalBandsContiguousCover bands next stop) := by
  induction bands generalizing next stop with
  | nil =>
      dsimp [ropeTurnRatioRationalIntervalBandsContiguousCover]
      infer_instance
  | cons _band _tail _ih =>
      dsimp [ropeTurnRatioRationalIntervalBandsContiguousCover]
      infer_instance

private theorem ropeTurnRatioRationalIntervalBandsCover_of_contiguous_aux
    {bands : List RopeTurnRatioRationalIntervalBand} {start stop gap : Nat}
    (hchain :
      ropeTurnRatioRationalIntervalBandsContiguousCover bands start stop)
    (hstart : start ≤ gap) (hgap_stop : gap < stop) :
    ∃ band, band ∈ bands ∧ band.CoversGap gap := by
  induction bands generalizing start stop gap with
  | nil =>
      dsimp [ropeTurnRatioRationalIntervalBandsContiguousCover] at hchain
      have hstop_le_gap : stop ≤ gap := le_trans hchain hstart
      exact False.elim ((Nat.not_lt_of_ge hstop_le_gap) hgap_stop)
  | cons band tail ih =>
      dsimp [ropeTurnRatioRationalIntervalBandsContiguousCover] at hchain
      rcases hchain with ⟨hband_start, _hstart_end, _hend_stop, htail⟩
      by_cases hgap_le_end : gap ≤ band.endGap
      · refine ⟨band, by simp, ?_⟩
        dsimp [RopeTurnRatioRationalIntervalBand.CoversGap]
        exact ⟨by simpa [hband_start] using hstart, hgap_le_end⟩
      · have hend_lt_gap : band.endGap < gap := Nat.lt_of_not_ge hgap_le_end
        rcases ih (start := band.endGap + 1) htail
            (Nat.succ_le_of_lt hend_lt_gap) hgap_stop with
          ⟨coveredBand, hmem, hcover⟩
        exact ⟨coveredBand, by simp [hmem], hcover⟩

/-- A contiguous generated band list covers every positive gap in
`List.range context`.

Generated RoPE certificates can now prove this linear contiguity predicate
instead of running a nested existential coverage search. -/
theorem ropeTurnRatioRationalIntervalBandsCover_of_contiguous
    {bands : List RopeTurnRatioRationalIntervalBand} {context : Nat}
    (hchain :
      ropeTurnRatioRationalIntervalBandsContiguousCover bands 1 context) :
    ropeTurnRatioRationalIntervalBandsCover bands context := by
  intro gap hgap_range hgap_pos
  exact
    ropeTurnRatioRationalIntervalBandsCover_of_contiguous_aux hchain
      (Nat.succ_le_of_lt hgap_pos) (List.mem_range.mp hgap_range)

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

/-- A valid rational band list covering the generated gap range gives a finite
interval certificate.

This is the compressed proof route for larger standard-RoPE channel-0 planner
frontiers: Lean only needs to check band validity and range coverage, then this
theorem expands the contract to the original per-gap interval-certificate
predicate. -/
theorem ropeTurnRatioIntervalCertificate_of_rationalIntervalBands
    {turnRatio margin : ℝ} {context : Nat}
    {bands : List RopeTurnRatioRationalIntervalBand}
    (hmargin_nonneg : 0 ≤ margin)
    (hvalid : ∀ band, band ∈ bands → band.Valid turnRatio margin)
    (hcover : ropeTurnRatioRationalIntervalBandsCover bands context) :
    ropeTurnRatioIntervalCertificate turnRatio margin context := by
  refine ⟨hmargin_nonneg, ?_⟩
  intro gap hgap_range hgap_pos
  rcases hcover gap hgap_range hgap_pos with ⟨band, hmem, hband_cover⟩
  exact
    ⟨(gap : ℚ) * band.lowerBound, (gap : ℚ) * band.upperBound, band.cell,
      ropeTurnRatioIntervalWitness_of_rationalIntervalBand
        (turnRatio := turnRatio) (margin := margin) (gap := gap)
        (band := band) (hvalid band hmem) hband_cover⟩

/-- A rational interval witness remains valid when the advertised margin is
decreased. -/
theorem ropeTurnRatioIntervalWitness_mono_margin
    {turnRatio smallMargin largeMargin : ℝ} {gap : Nat}
    {lower upper : ℚ} {cell : Int}
    (hmargin_le : smallMargin ≤ largeMargin)
    (hwitness :
      ropeTurnRatioIntervalWitness turnRatio largeMargin gap lower upper cell) :
    ropeTurnRatioIntervalWitness turnRatio smallMargin gap lower upper cell := by
  rcases hwitness with ⟨hlower, hupper, hleft, hright⟩
  exact ⟨hlower, hupper, by linarith, by linarith⟩

/-- A rational interval certificate remains valid when the advertised margin is
decreased to a nonnegative value. -/
theorem ropeTurnRatioIntervalCertificate_mono_margin
    {turnRatio smallMargin largeMargin : ℝ} {context : Nat}
    (hsmall_nonneg : 0 ≤ smallMargin)
    (hmargin_le : smallMargin ≤ largeMargin)
    (certificate :
      ropeTurnRatioIntervalCertificate turnRatio largeMargin context) :
    ropeTurnRatioIntervalCertificate turnRatio smallMargin context := by
  rcases certificate with ⟨_hlarge_nonneg, hwitnesses⟩
  refine ⟨hsmall_nonneg, ?_⟩
  intro gap hgap_range hgap_pos
  rcases hwitnesses gap hgap_range hgap_pos with ⟨lower, upper, cell, hwitness⟩
  exact
    ⟨lower, upper, cell,
      ropeTurnRatioIntervalWitness_mono_margin
        (turnRatio := turnRatio) (smallMargin := smallMargin)
        (largeMargin := largeMargin) (gap := gap)
        (lower := lower) (upper := upper) (cell := cell)
        hmargin_le hwitness⟩

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

/-- The scalar nearest-integer margin for one gap is no larger than the error
against any chosen integer-turn witness.

This is the generic upper-bound half needed by report contracts: once a
certifier supplies a concrete integer turn whose error is exactly the claimed
margin, the scalar nearest-gap margin cannot be larger than that report value.
-/
theorem ropeTurnRatioGapNearestIntegerMargin_le_error
    {turnRatio : ℝ} {gap : Nat} {turns : Int} :
    ropeTurnRatioGapNearestIntegerMargin turnRatio gap ≤
      ropeTurnRatioError turnRatio gap turns := by
  have hfloor_ceil :
      ropeTurnRatioGapNearestIntegerMargin turnRatio gap ≤
          |(gap : ℝ) * turnRatio - ((⌊(gap : ℝ) * turnRatio⌋ : ℤ) : ℝ)| ∧
        ropeTurnRatioGapNearestIntegerMargin turnRatio gap ≤
          |(gap : ℝ) * turnRatio - ((⌈(gap : ℝ) * turnRatio⌉ : ℤ) : ℝ)| := by
    unfold ropeTurnRatioGapNearestIntegerMargin
    exact ⟨min_le_left _ _, min_le_right _ _⟩
  exact
    (ropeNearestIntegerWitnesses_iff_forall_int
      (x := (gap : ℝ) * turnRatio)
      (margin := ropeTurnRatioGapNearestIntegerMargin turnRatio gap)).1
      hfloor_ceil turns

/- A natural-rational turn-ratio gap has exact error `1 / denominator` when
its numerator product is one more than an integer number of denominators.

This is the exact modular-inverse witness form for reduced rational reports:
Python may find a gap whose residue is `1`, and Lean turns that witness into a
nearest-integer error equality. -/
private theorem ropeTurnRatioError_natRatio_eq_one_over_den_of_num_eq_turn_mul_den_add_one
    {numerator denominator gap turns : Nat} (hdenominator : 0 < denominator)
    (hproduct : gap * numerator = turns * denominator + 1) :
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap
      (Int.ofNat turns) = 1 / (denominator : ℝ) := by
  let z : Int := ((gap * numerator : Nat) : Int) -
    (Int.ofNat turns) * (denominator : Int)
  have herror :=
    ropeTurnRatioError_natRatio_eq_abs_int_num_sub_turn_mul_den_div_den
      (numerator := numerator) (denominator := denominator) (gap := gap)
      (turns := Int.ofNat turns) hdenominator
  have hz : z = 1 := by
    dsimp [z]
    have hproduct_int :
        (gap : Int) * (numerator : Int) =
          (turns : Int) * (denominator : Int) + 1 := by
      exact_mod_cast hproduct
    linarith
  calc
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap
        (Int.ofNat turns) = |(z : ℝ)| / (denominator : ℝ) := by
      simpa [z] using herror
    _ = 1 / (denominator : ℝ) := by
      rw [hz]
      norm_num

/- A natural-rational turn-ratio gap has exact error `1 / denominator` when
its numerator product is one less than an integer number of denominators.

This is the companion residue-`-1` modular-inverse witness form. -/
private theorem ropeTurnRatioError_natRatio_eq_one_over_den_of_num_add_one_eq_turn_mul_den
    {numerator denominator gap turns : Nat} (hdenominator : 0 < denominator)
    (hproduct : gap * numerator + 1 = turns * denominator) :
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap
      (Int.ofNat turns) = 1 / (denominator : ℝ) := by
  let z : Int := ((gap * numerator : Nat) : Int) -
    (Int.ofNat turns) * (denominator : Int)
  have herror :=
    ropeTurnRatioError_natRatio_eq_abs_int_num_sub_turn_mul_den_div_den
      (numerator := numerator) (denominator := denominator) (gap := gap)
      (turns := Int.ofNat turns) hdenominator
  have hz : z = -1 := by
    dsimp [z]
    have hproduct_int :
        (gap : Int) * (numerator : Int) + 1 =
          (turns : Int) * (denominator : Int) := by
      exact_mod_cast hproduct
    linarith
  calc
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap
        (Int.ofNat turns) = |(z : ℝ)| / (denominator : ℝ) := by
      simpa [z] using herror
    _ = 1 / (denominator : ℝ) := by
      rw [hz]
      norm_num

/-- A natural-rational turn-ratio gap has exact error `1 / denominator` when
its numerator product is one away from an integer number of denominators.

This is the modular-inverse witness equality for reduced rational reports:
the supplied gap may realize residue `+1` or residue `-1` modulo the
denominator. -/
theorem ropeTurnRatioError_natRatio_eq_one_over_den_of_modular_inverse_witness
    {numerator denominator gap turns : Nat} (hdenominator : 0 < denominator)
    (hwitness :
      gap * numerator = turns * denominator + 1 ∨
        gap * numerator + 1 = turns * denominator) :
    ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) gap
      (Int.ofNat turns) = 1 / (denominator : ℝ) := by
  rcases hwitness with hplus | hminus
  · exact
      ropeTurnRatioError_natRatio_eq_one_over_den_of_num_eq_turn_mul_den_add_one
        (numerator := numerator) (denominator := denominator) (gap := gap)
        (turns := turns) hdenominator hplus
  · exact
      ropeTurnRatioError_natRatio_eq_one_over_den_of_num_add_one_eq_turn_mul_den
        (numerator := numerator) (denominator := denominator) (gap := gap)
        (turns := turns) hdenominator hminus

/-- A supplied modular-inverse witness makes the exact weakest-gap report
contract generic for reduced natural rational turn ratios.

If `numerator/denominator` is reduced, the inspected context stays before the
denominator return gap, and the reported `witnessGap` is one residue away from
an integer number of denominators, then the exact weakest scalar
nearest-integer margin is `1 / denominator` and it is realized at
`witnessGap`. This generalizes the special `1 / denominator` report theorem
without claiming anything about irrational standard RoPE channels. -/
theorem ropeTurnRatioNatRatio_exactWeakestGapMargin_report_of_modular_inverse_witness
    {numerator denominator context witnessGap turns : Nat}
    (hdenominator : 0 < denominator)
    (hcoprime : Nat.Coprime numerator denominator)
    (hcontext : context ≤ denominator)
    (hgap_pos : 0 < witnessGap)
    (hgap_context : witnessGap < context)
    (hwitness :
      witnessGap * numerator = turns * denominator + 1 ∨
        witnessGap * numerator + 1 = turns * denominator) :
    ropeTurnRatioExactWeakestGapMargin
      ((numerator : ℝ) / (denominator : ℝ))
      (1 / (denominator : ℝ)) context witnessGap := by
  have hfinite :
      ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ))
        (1 / (denominator : ℝ)) context :=
    ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
      (numerator := numerator) (denominator := denominator)
      hdenominator hcoprime hcontext
  have hmem : witnessGap ∈ List.range context := List.mem_range.mpr hgap_context
  have hlower :
      (1 / (denominator : ℝ)) ≤
        ropeTurnRatioGapNearestIntegerMargin
          ((numerator : ℝ) / (denominator : ℝ)) witnessGap :=
    (ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
      (turnRatio := ((numerator : ℝ) / (denominator : ℝ)))
      (margin := 1 / (denominator : ℝ)) (context := context)).1
      hfinite witnessGap hmem hgap_pos
  have hupper :
      ropeTurnRatioGapNearestIntegerMargin
          ((numerator : ℝ) / (denominator : ℝ)) witnessGap ≤
        1 / (denominator : ℝ) := by
    have hle_error :
        ropeTurnRatioGapNearestIntegerMargin
            ((numerator : ℝ) / (denominator : ℝ)) witnessGap ≤
          ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ))
            witnessGap (Int.ofNat turns) :=
      ropeTurnRatioGapNearestIntegerMargin_le_error
        (turnRatio := ((numerator : ℝ) / (denominator : ℝ)))
        (gap := witnessGap) (turns := Int.ofNat turns)
    have herror_eq :
        ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ))
          witnessGap (Int.ofNat turns) = 1 / (denominator : ℝ) :=
      ropeTurnRatioError_natRatio_eq_one_over_den_of_modular_inverse_witness
        (numerator := numerator) (denominator := denominator)
        (gap := witnessGap) (turns := turns) hdenominator hwitness
    exact le_trans hle_error (le_of_eq herror_eq)
  refine
    (ropeTurnRatioExactWeakestGapMargin_iff_finiteMargin_and_realized
      (turnRatio := ((numerator : ℝ) / (denominator : ℝ)))
      (margin := 1 / (denominator : ℝ))
      (context := context)
      (witnessGap := witnessGap)).2 ?_
  exact ⟨hmem, hgap_pos, le_antisymm hupper hlower, hfinite⟩

/-- Every reduced natural-rational turn ratio has some modular-inverse gap
realizing exact weakest margin `1 / denominator` over the full denominator
context.

This removes the need for a caller to supply the inverse witness manually in
the full-period rational/discretized case: coprimality gives a positive gap
strictly below the denominator whose numerator product is one residue away from
an integer number of denominators, and the generic witness theorem turns that
gap into an exact weakest-gap report. -/
theorem ropeTurnRatioNatRatio_exists_exactWeakestGapMargin_report_of_coprime
    {numerator denominator : Nat}
    (hdenominator : 1 < denominator)
    (hcoprime : Nat.Coprime numerator denominator) :
    ∃ witnessGap, 0 < witnessGap ∧ witnessGap < denominator ∧
      ropeTurnRatioExactWeakestGapMargin
        ((numerator : ℝ) / (denominator : ℝ))
        (1 / (denominator : ℝ)) denominator witnessGap := by
  obtain ⟨witnessGap, hgap_lt, hmod⟩ :=
    Nat.exists_mul_mod_eq_one_of_coprime
      (k := denominator) (n := numerator) hcoprime hdenominator
  have hgap_pos : 0 < witnessGap := by
    by_contra hnot
    have hzero : witnessGap = 0 := Nat.eq_zero_of_not_pos hnot
    subst witnessGap
    norm_num at hmod
  let turns := (witnessGap * numerator) / denominator
  have hmod_comm :
      witnessGap * numerator % denominator = 1 := by
    simpa [Nat.mul_comm] using hmod
  have hwitness :
      witnessGap * numerator = turns * denominator + 1 ∨
        witnessGap * numerator + 1 = turns * denominator := by
    left
    have hdivmod :
        witnessGap * numerator =
          denominator * ((witnessGap * numerator) / denominator) +
            (witnessGap * numerator) % denominator :=
      (Nat.div_add_mod (witnessGap * numerator) denominator).symm
    have hdivmod' :
        witnessGap * numerator =
          ((witnessGap * numerator) / denominator) * denominator +
            (witnessGap * numerator) % denominator := by
      simpa [Nat.mul_comm denominator ((witnessGap * numerator) / denominator)] using hdivmod
    simpa [turns, hmod_comm] using hdivmod'
  exact
    ⟨witnessGap, hgap_pos, hgap_lt,
      ropeTurnRatioNatRatio_exactWeakestGapMargin_report_of_modular_inverse_witness
        (numerator := numerator) (denominator := denominator)
        (context := denominator) (witnessGap := witnessGap) (turns := turns)
        (Nat.zero_lt_of_lt hdenominator) hcoprime (le_refl denominator)
        hgap_pos hgap_lt hwitness⟩

/-- At the full denominator context, a reduced natural-rational turn ratio has
exact finite-margin threshold `1 / denominator`.

This is the report-facing pass/fail boundary for rational/discretized RoPE
channels: below or at `1 / denominator` the finite margin predicate holds, and
above it the exact weakest-gap witness rules it out. It is still a rational
turn-ratio theorem, not an irrational standard RoPE channel theorem. -/
theorem ropeTurnRatioFiniteMargin_natRatio_full_denominator_iff_margin_le_one_over_den
    {numerator denominator : Nat} {margin : ℝ}
    (hdenominator : 1 < denominator)
    (hcoprime : Nat.Coprime numerator denominator) :
    ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ))
      margin denominator ↔ margin ≤ 1 / (denominator : ℝ) := by
  constructor
  · intro hfinite
    obtain ⟨witnessGap, _hgap_pos, _hgap_lt, hexact⟩ :=
      ropeTurnRatioNatRatio_exists_exactWeakestGapMargin_report_of_coprime
        (numerator := numerator) (denominator := denominator)
        hdenominator hcoprime
    rcases
      (ropeTurnRatioExactWeakestGapMargin_iff_finiteMargin_and_realized
        (turnRatio := ((numerator : ℝ) / (denominator : ℝ)))
        (margin := 1 / (denominator : ℝ))
        (context := denominator)
        (witnessGap := witnessGap)).1 hexact with
      ⟨hmem, hgap_pos, hnearest_eq, _hthreshold_finite⟩
    have hgap_bound :
        margin ≤ ropeTurnRatioGapNearestIntegerMargin
          ((numerator : ℝ) / (denominator : ℝ)) witnessGap :=
      (ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
        (turnRatio := ((numerator : ℝ) / (denominator : ℝ)))
        (margin := margin) (context := denominator)).1
        hfinite witnessGap hmem hgap_pos
    rwa [hnearest_eq] at hgap_bound
  · intro hmargin
    have hthreshold :
        ropeTurnRatioFiniteMargin ((numerator : ℝ) / (denominator : ℝ))
          (1 / (denominator : ℝ)) denominator :=
      ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
        (numerator := numerator) (denominator := denominator)
        (Nat.zero_lt_of_lt hdenominator) hcoprime (le_refl denominator)
    intro gap hgap_pos hgap_context turns
    exact le_trans hmargin (hthreshold gap hgap_pos hgap_context turns)

/-- If a requested margin is above the exact full-denominator rational
threshold, a concrete below-margin nearest-integer obstruction exists.

This is the report-facing failure witness behind rational/discretized RoPE
requests: for a reduced `numerator / denominator` turn ratio, any advertised
margin larger than `1 / denominator` is refuted by some positive gap below the
denominator and an integer turn whose error is already below the advertised
margin. -/
theorem ropeTurnRatioNatRatio_full_denominator_obstruction_of_one_over_den_lt_margin
    {numerator denominator : Nat} {margin : ℝ}
    (hdenominator : 1 < denominator)
    (hcoprime : Nat.Coprime numerator denominator)
    (hmargin : 1 / (denominator : ℝ) < margin) :
    ∃ witnessGap turns, 0 < witnessGap ∧ witnessGap < denominator ∧
      ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) witnessGap
        (Int.ofNat turns) < margin := by
  obtain ⟨witnessGap, hgap_lt, hmod⟩ :=
    Nat.exists_mul_mod_eq_one_of_coprime
      (k := denominator) (n := numerator) hcoprime hdenominator
  have hgap_pos : 0 < witnessGap := by
    by_contra hnot
    have hzero : witnessGap = 0 := Nat.eq_zero_of_not_pos hnot
    subst witnessGap
    norm_num at hmod
  let turns := (witnessGap * numerator) / denominator
  have hmod_comm :
      witnessGap * numerator % denominator = 1 := by
    simpa [Nat.mul_comm] using hmod
  have hwitness :
      witnessGap * numerator = turns * denominator + 1 ∨
        witnessGap * numerator + 1 = turns * denominator := by
    left
    have hdivmod :
        witnessGap * numerator =
          denominator * ((witnessGap * numerator) / denominator) +
            (witnessGap * numerator) % denominator :=
      (Nat.div_add_mod (witnessGap * numerator) denominator).symm
    have hdivmod' :
        witnessGap * numerator =
          ((witnessGap * numerator) / denominator) * denominator +
            (witnessGap * numerator) % denominator := by
      simpa [Nat.mul_comm denominator ((witnessGap * numerator) / denominator)] using hdivmod
    simpa [turns, hmod_comm] using hdivmod'
  have herror_eq :
      ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) witnessGap
          (Int.ofNat turns) =
        1 / (denominator : ℝ) :=
    ropeTurnRatioError_natRatio_eq_one_over_den_of_modular_inverse_witness
      (numerator := numerator) (denominator := denominator)
      (gap := witnessGap) (turns := turns)
      (Nat.zero_lt_of_lt hdenominator) hwitness
  have hobstruction :
      ropeTurnRatioError ((numerator : ℝ) / (denominator : ℝ)) witnessGap
          (Int.ofNat turns) < margin := by
    rw [herror_eq]
    exact hmargin
  exact ⟨witnessGap, turns, hgap_pos, hgap_lt, hobstruction⟩

private theorem ropeTurnRatio_one_over_nat_floor_eq_zero
    {denominator : Nat} (hdenominator : 1 < denominator) :
    ⌊((1 : ℝ) / (denominator : ℝ))⌋ = (0 : ℤ) := by
  rw [Int.floor_eq_iff]
  constructor
  · norm_num
  · norm_num
    have hden_real : (1 : ℝ) < denominator := by exact_mod_cast hdenominator
    simpa [one_div] using inv_lt_one_of_one_lt₀ hden_real

private theorem ropeTurnRatio_one_over_nat_ceil_eq_one
    {denominator : Nat} (hdenominator : 1 < denominator) :
    ⌈((1 : ℝ) / (denominator : ℝ))⌉ = (1 : ℤ) := by
  rw [Int.ceil_eq_iff]
  constructor
  · norm_num
    exact Nat.zero_lt_of_lt hdenominator
  · norm_num
    have hden_real : (1 : ℝ) < denominator := by exact_mod_cast hdenominator
    exact le_of_lt (by simpa [one_div] using inv_lt_one_of_one_lt₀ hden_real)

/-- The first gap of a `1 / denominator` rational turn ratio has scalar
nearest-integer margin exactly `1 / denominator`.

This is the reusable version of the public `1/4099` preset's realized-gap
calculation. It is still a rational/discretized theorem, not a standard
irrational RoPE channel-0 result. -/
theorem ropeTurnRatioOneOverNat_gapOneNearestIntegerMargin
    {denominator : Nat} (hdenominator : 1 < denominator) :
    ropeTurnRatioGapNearestIntegerMargin
      (((1 : Nat) : ℝ) / (denominator : ℝ)) 1 =
        1 / (denominator : ℝ) := by
  unfold ropeTurnRatioGapNearestIntegerMargin
  simp only [Nat.cast_one, one_mul]
  rw [ropeTurnRatio_one_over_nat_floor_eq_zero hdenominator,
    ropeTurnRatio_one_over_nat_ceil_eq_one hdenominator]
  have hden_pos : (0 : ℝ) < denominator := by
    exact_mod_cast (Nat.zero_lt_of_lt hdenominator)
  have hden_real_gt_one : (1 : ℝ) < denominator := by exact_mod_cast hdenominator
  have hle_one : (1 : ℝ) / (denominator : ℝ) ≤ 1 := by
    exact le_of_lt (by simpa [one_div] using inv_lt_one_of_one_lt₀ hden_real_gt_one)
  have htwo_le_den : (2 : ℝ) ≤ denominator := by exact_mod_cast hdenominator
  have htwo_div_le_one : (2 : ℝ) / (denominator : ℝ) ≤ 1 := by
    rw [div_le_iff₀ hden_pos]
    simpa [one_mul] using htwo_le_den
  have hhalf_pre :
      (1 : ℝ) / (denominator : ℝ) ≤
        1 - (1 : ℝ) / (denominator : ℝ) := by
    rw [le_sub_iff_add_le]
    calc
      (1 : ℝ) / (denominator : ℝ) + (1 : ℝ) / (denominator : ℝ)
          = (2 : ℝ) / (denominator : ℝ) := by ring
      _ ≤ 1 := htwo_div_le_one
  have hhalf :
      (1 : ℝ) / (denominator : ℝ) ≤
        |(1 : ℝ) / (denominator : ℝ) - 1| := by
    rw [abs_of_nonpos (sub_nonpos.mpr hle_one)]
    simpa [sub_eq_add_neg] using hhalf_pre
  have hleft :
      |(1 : ℝ) / (denominator : ℝ) - 0| =
        1 / (denominator : ℝ) := by
    rw [sub_zero, abs_of_nonneg]
    exact le_of_lt (one_div_pos.mpr hden_pos)
  simpa [hleft] using min_eq_left hhalf

/-- For the rational turn ratio `1 / denominator`, the exact weakest
finite-context nearest-integer margin is `1 / denominator`, realized at gap
`1`, throughout every nontrivial context that stays before the denominator
return gap.

This turns the one-off rational preset report into a family-level contract:
when `1 < context ≤ denominator`, the public fields
`exact_nearest_gap_margin = 1/denominator` and `exact_nearest_gap = 1` are
Lean-backed for the declared rational/discretized ratio. -/
theorem ropeTurnRatioOneOverNat_exactWeakestGapMargin_report
    {denominator context : Nat}
    (hcontext_min : 1 < context) (hcontext_den : context ≤ denominator) :
    ropeTurnRatioExactWeakestGapMargin
      (((1 : Nat) : ℝ) / (denominator : ℝ))
      (1 / (denominator : ℝ)) context 1 := by
  have hdenominator : 1 < denominator := lt_of_lt_of_le hcontext_min hcontext_den
  refine
    (ropeTurnRatioExactWeakestGapMargin_iff_finiteMargin_and_realized
      (turnRatio := (((1 : Nat) : ℝ) / (denominator : ℝ)))
      (margin := 1 / (denominator : ℝ))
      (context := context)
      (witnessGap := 1)).2 ?_
  exact
    ⟨List.mem_range.mpr hcontext_min,
      by norm_num,
      ropeTurnRatioOneOverNat_gapOneNearestIntegerMargin hdenominator,
      ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den
        (numerator := 1) (denominator := denominator)
        (context := context)
        (Nat.zero_lt_of_lt hdenominator)
        (by norm_num)
        hcontext_den⟩

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

/-- The named rational/discretized preset's public weakest-gap report is exact.

Gap `1` realizes scalar nearest-integer margin `1 / 4099`, and every positive
generated gap in the inspected context has scalar nearest-integer margin at
least that value. This is the Lean bridge behind the Python fields
`exact_nearest_gap_margin = "1/4099"` and `exact_nearest_gap = 1`. -/
theorem ropeRationalPreset4099_exactWeakestGapMargin :
    ropeTurnRatioGapNearestIntegerMargin ropeRationalPreset4099TurnRatio 1 =
        ropeRationalPreset4099Margin ∧
      ∀ gap : Nat, gap ∈ List.range ropeRationalPreset4099Context → 0 < gap →
        ropeRationalPreset4099Margin ≤
          ropeTurnRatioGapNearestIntegerMargin ropeRationalPreset4099TurnRatio gap := by
  constructor
  · dsimp [ropeTurnRatioGapNearestIntegerMargin, ropeRationalPreset4099TurnRatio,
      ropeRationalPreset4099Margin]
    norm_num
  · intro gap hgap_range hgap_pos
    exact
      (ropeTurnRatioFiniteMargin_iff_gapNearestIntegerMargin
        (turnRatio := ropeRationalPreset4099TurnRatio)
        (margin := ropeRationalPreset4099Margin)
        (context := ropeRationalPreset4099Context)).1
        ropeRationalPreset4099_turnRatioFiniteMargin gap hgap_range hgap_pos

/-- The named rational/discretized preset satisfies the generic exact
weakest-gap report contract.

This packages the public `exact_nearest_gap_margin = "1/4099"` and
`exact_nearest_gap = 1` fields using the reusable report-facing predicate
instead of a bespoke conjunction. -/
theorem ropeRationalPreset4099_exactWeakestGapMargin_report :
    ropeTurnRatioExactWeakestGapMargin ropeRationalPreset4099TurnRatio
      ropeRationalPreset4099Margin ropeRationalPreset4099Context 1 := by
  refine
    (ropeTurnRatioExactWeakestGapMargin_iff_finiteMargin_and_realized
      (turnRatio := ropeRationalPreset4099TurnRatio)
      (margin := ropeRationalPreset4099Margin)
      (context := ropeRationalPreset4099Context)
      (witnessGap := 1)).2 ?_
  exact
    ⟨by
      dsimp [ropeRationalPreset4099Context]
      norm_num,
    by norm_num,
    ropeRationalPreset4099_exactWeakestGapMargin.1,
    ropeRationalPreset4099_turnRatioFiniteMargin⟩

/-- The named rational/discretized preset has no zero-margin witness inside
the inspected context.

The Python certifier reports `zero_margin_witness = none` for the `1/4099`,
context-4096 preset. This theorem gives that field its Lean meaning: every
positive generated gap below `4096` has nonzero error against every integer
turn count. -/
theorem ropeRationalPreset4099_noZeroTurnRatioError :
    ∀ gap : Nat, gap ∈ List.range ropeRationalPreset4099Context → 0 < gap →
      ∀ turns : Int,
        ropeTurnRatioError ropeRationalPreset4099TurnRatio gap turns ≠ 0 := by
  exact
    ropeTurnRatioFiniteMargin_pos_no_zero_error
      (turnRatio := ropeRationalPreset4099TurnRatio)
      (margin := ropeRationalPreset4099Margin)
      (context := ropeRationalPreset4099Context)
      (by
        dsimp [ropeRationalPreset4099Margin]
        norm_num)
      ropeRationalPreset4099_turnRatioFiniteMargin

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

/-- A third tiny inspected context for the standard-RoPE interval certificate.
This includes the first positive gap whose turn ratio has crossed one full
turn, so the interval witness must use integer cell `1` rather than `0`. -/
def ropeStandardChannel0D3SeedContext : Nat := 8

/-- The advertised margin for the third standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D3SeedMargin : ℝ := 1 / 32

/-- A larger tiny inspected context for the standard-RoPE interval certificate.
This carries the same `1/32` margin through all positive gaps below `19` by
placing intervals in integer cells `0`, `1`, and `2`. -/
def ropeStandardChannel0D4SeedContext : Nat := 19

/-- The advertised margin for the fourth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D4SeedMargin : ℝ := 1 / 32

/-- A fifth tiny inspected context for the standard-RoPE interval certificate.
This lowers the advertised margin to `1/64` and carries the same elementary
pi-bounds through all positive gaps below `44`. -/
def ropeStandardChannel0D5SeedContext : Nat := 44

/-- The advertised margin for the fifth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D5SeedMargin : ℝ := 1 / 64

/-- A sixth tiny inspected context for the standard-RoPE interval certificate.
This crosses the first near-integer obstruction after gap `43` by switching to
the four-decimal mathlib bounds on `π`. -/
def ropeStandardChannel0D6SeedContext : Nat := 57

/-- The advertised margin for the sixth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D6SeedMargin : ℝ := 1 / 512

/-- A seventh inspected context for the standard-RoPE interval certificate.
This extends the four-decimal interval route through all positive gaps below
`333`. Gap `333` is the first obstruction for this d4 bound table. -/
def ropeStandardChannel0D7SeedContext : Nat := 333

/-- The advertised margin for the seventh standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D7SeedMargin : ℝ := 1 / 512

private def ropeStandardChannel0D7Cell (gap : Nat) : Int :=
  if gap ≤ 6 then 0
  else if gap ≤ 12 then 1
  else if gap ≤ 18 then 2
  else if gap ≤ 25 then 3
  else if gap ≤ 31 then 4
  else if gap ≤ 37 then 5
  else if gap ≤ 43 then 6
  else if gap ≤ 50 then 7
  else if gap ≤ 56 then 8
  else if gap ≤ 62 then 9
  else if gap ≤ 69 then 10
  else if gap ≤ 75 then 11
  else if gap ≤ 81 then 12
  else if gap ≤ 87 then 13
  else if gap ≤ 94 then 14
  else if gap ≤ 100 then 15
  else if gap ≤ 106 then 16
  else if gap ≤ 113 then 17
  else if gap ≤ 119 then 18
  else if gap ≤ 125 then 19
  else if gap ≤ 131 then 20
  else if gap ≤ 138 then 21
  else if gap ≤ 144 then 22
  else if gap ≤ 150 then 23
  else if gap ≤ 157 then 24
  else if gap ≤ 163 then 25
  else if gap ≤ 169 then 26
  else if gap ≤ 175 then 27
  else if gap ≤ 182 then 28
  else if gap ≤ 188 then 29
  else if gap ≤ 194 then 30
  else if gap ≤ 201 then 31
  else if gap ≤ 207 then 32
  else if gap ≤ 213 then 33
  else if gap ≤ 219 then 34
  else if gap ≤ 226 then 35
  else if gap ≤ 232 then 36
  else if gap ≤ 238 then 37
  else if gap ≤ 245 then 38
  else if gap ≤ 251 then 39
  else if gap ≤ 257 then 40
  else if gap ≤ 263 then 41
  else if gap ≤ 270 then 42
  else if gap ≤ 276 then 43
  else if gap ≤ 282 then 44
  else if gap ≤ 289 then 45
  else if gap ≤ 295 then 46
  else if gap ≤ 301 then 47
  else if gap ≤ 307 then 48
  else if gap ≤ 314 then 49
  else if gap ≤ 320 then 50
  else if gap ≤ 326 then 51
  else if gap ≤ 332 then 52
  else 0

/-- An eighth inspected context for the standard-RoPE interval certificate.
This is the next generated target from six-decimal `π` bounds. -/
def ropeStandardChannel0D8SeedContext : Nat := 710

/-- The advertised margin for the eighth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D8SeedMargin : ℝ := 1 / 1024

private def ropeStandardChannel0D8Cell (gap : Nat) : Int :=
  Int.ofNat ((500000 * gap) / 3141593)

/-- A ninth inspected context for the standard-RoPE interval certificate.
This names a model-scale 4k seed from 20-decimal `π` bounds. -/
def ropeStandardChannel0D9SeedContext : Nat := 4096

/-- The advertised margin for the ninth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D9SeedMargin : ℝ := 1 / 131072

private def ropeStandardChannel0D9Cell (gap : Nat) : Int :=
  Int.ofNat ((100000000000000000000 * gap) / 628318530717958647694)

/-- A tenth inspected context for the standard-RoPE interval certificate.
This keeps the 4k horizon and tightens the channel-0 margin with the same
20-decimal `π` bounds. -/
def ropeStandardChannel0D10SeedContext : Nat := 4096

/-- The advertised margin for the tenth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D10SeedMargin : ℝ := 1 / 105000

/-- An eleventh inspected context for the standard-RoPE interval certificate.
This keeps the 4k horizon and tightens the channel-0 margin to the exact
threshold found by the deterministic d20 interval planner. -/
def ropeStandardChannel0D11SeedContext : Nat := 4096

/-- The advertised margin for the eleventh standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D11SeedMargin : ℝ := 1 / 104219

/-- A twelfth inspected context for the standard-RoPE interval certificate.
This extends the genuine channel-0 seed to an 8k context by lowering the
advertised margin just below the D11 bracket. -/
def ropeStandardChannel0D12SeedContext : Nat := 8192

/-- The advertised margin for the twelfth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D12SeedMargin : ℝ := 1 / 104220

/-- A thirteenth inspected context for the standard-RoPE interval certificate.
This keeps the 8k horizon and restores the D11 margin using the same
20-decimal generated interval bands. -/
def ropeStandardChannel0D13SeedContext : Nat := 8192

/-- The advertised margin for the thirteenth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D13SeedMargin : ℝ := 1 / 104219

/-- A fourteenth inspected context for the standard-RoPE interval certificate.
This extends the D13 channel-0 margin to a 16k context using the same
20-decimal generated interval bands. -/
def ropeStandardChannel0D14SeedContext : Nat := 16384

/-- The advertised margin for the fourteenth standard channel-0 interval seed. -/
noncomputable def ropeStandardChannel0D14SeedMargin : ℝ := 1 / 104219

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

private theorem ropeStandardChannel0_d3_base_lower :
    (10 : ℝ) / 63 ≤ ropeStandardChannel0TurnRatio := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have htwo_pi_lt : 2 * Real.pi < (63 : ℝ) / 10 := by
    nlinarith [Real.pi_lt_d2]
  have hrecip : ((63 : ℝ) / 10)⁻¹ = (10 : ℝ) / 63 := by norm_num
  have hlower : ((63 : ℝ) / 10)⁻¹ < (2 * Real.pi)⁻¹ :=
    (inv_lt_inv₀ (by norm_num : (0 : ℝ) < (63 : ℝ) / 10) htwo_pi_pos).2
      htwo_pi_lt
  have hlower_le : (10 : ℝ) / 63 ≤ (2 * Real.pi)⁻¹ := by
    rw [← hrecip]
    exact le_of_lt hlower
  simpa [ropeStandardChannel0TurnRatio, one_div] using hlower_le

/-- Four-decimal lower rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD4_base_lower :
    (5000 : ℝ) / 31416 ≤ ropeStandardChannel0TurnRatio := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have htwo_pi_lt : 2 * Real.pi < (31416 : ℝ) / 5000 := by
    nlinarith [Real.pi_lt_d4]
  have hrecip : ((31416 : ℝ) / 5000)⁻¹ = (5000 : ℝ) / 31416 := by norm_num
  have hlower : ((31416 : ℝ) / 5000)⁻¹ < (2 * Real.pi)⁻¹ :=
    (inv_lt_inv₀ (by norm_num : (0 : ℝ) < (31416 : ℝ) / 5000) htwo_pi_pos).2
      htwo_pi_lt
  have hlower_le : (5000 : ℝ) / 31416 ≤ (2 * Real.pi)⁻¹ := by
    rw [← hrecip]
    exact le_of_lt hlower
  simpa [ropeStandardChannel0TurnRatio, one_div] using hlower_le

/-- Four-decimal upper rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD4_base_upper :
    ropeStandardChannel0TurnRatio ≤ (5000 : ℝ) / 31415 := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have hlower : (31415 : ℝ) / 5000 < 2 * Real.pi := by
    nlinarith [Real.pi_gt_d4]
  have hrecip : ((31415 : ℝ) / 5000)⁻¹ = (5000 : ℝ) / 31415 := by norm_num
  have hupper : (2 * Real.pi)⁻¹ < ((31415 : ℝ) / 5000)⁻¹ :=
    (inv_lt_inv₀ htwo_pi_pos (by norm_num : (0 : ℝ) < (31415 : ℝ) / 5000)).2
      hlower
  have hupper_le : (2 * Real.pi)⁻¹ ≤ (5000 : ℝ) / 31415 := by
    rw [← hrecip]
    exact le_of_lt hupper
  simpa [ropeStandardChannel0TurnRatio, one_div] using hupper_le

/-- Six-decimal lower rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD6_base_lower :
    (500000 : ℝ) / 3141593 ≤ ropeStandardChannel0TurnRatio := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have htwo_pi_lt : 2 * Real.pi < (3141593 : ℝ) / 500000 := by
    nlinarith [Real.pi_lt_d6]
  have hrecip : ((3141593 : ℝ) / 500000)⁻¹ = (500000 : ℝ) / 3141593 := by
    norm_num
  have hlower : ((3141593 : ℝ) / 500000)⁻¹ < (2 * Real.pi)⁻¹ :=
    (inv_lt_inv₀ (by norm_num : (0 : ℝ) < (3141593 : ℝ) / 500000) htwo_pi_pos).2
      htwo_pi_lt
  have hlower_le : (500000 : ℝ) / 3141593 ≤ (2 * Real.pi)⁻¹ := by
    rw [← hrecip]
    exact le_of_lt hlower
  simpa [ropeStandardChannel0TurnRatio, one_div] using hlower_le

/-- Six-decimal upper rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD6_base_upper :
    ropeStandardChannel0TurnRatio ≤ (500000 : ℝ) / 3141592 := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have hlower : (3141592 : ℝ) / 500000 < 2 * Real.pi := by
    nlinarith [Real.pi_gt_d6]
  have hrecip : ((3141592 : ℝ) / 500000)⁻¹ = (500000 : ℝ) / 3141592 := by
    norm_num
  have hupper : (2 * Real.pi)⁻¹ < ((3141592 : ℝ) / 500000)⁻¹ :=
    (inv_lt_inv₀ htwo_pi_pos (by norm_num : (0 : ℝ) < (3141592 : ℝ) / 500000)).2
      hlower
  have hupper_le : (2 * Real.pi)⁻¹ ≤ (500000 : ℝ) / 3141592 := by
    rw [← hrecip]
    exact le_of_lt hupper
  simpa [ropeStandardChannel0TurnRatio, one_div] using hupper_le

/-- Twenty-decimal lower rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD20_base_lower :
    (100000000000000000000 : ℝ) / 628318530717958647694 ≤
      ropeStandardChannel0TurnRatio := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have htwo_pi_lt :
      2 * Real.pi < (628318530717958647694 : ℝ) /
        100000000000000000000 := by
    nlinarith [Real.pi_lt_d20]
  have hrecip :
      ((628318530717958647694 : ℝ) / 100000000000000000000)⁻¹ =
        (100000000000000000000 : ℝ) / 628318530717958647694 := by
    norm_num
  have hlower :
      ((628318530717958647694 : ℝ) / 100000000000000000000)⁻¹ <
        (2 * Real.pi)⁻¹ :=
    (inv_lt_inv₀
      (by norm_num : (0 : ℝ) <
        (628318530717958647694 : ℝ) / 100000000000000000000)
      htwo_pi_pos).2 htwo_pi_lt
  have hlower_le :
      (100000000000000000000 : ℝ) / 628318530717958647694 ≤
        (2 * Real.pi)⁻¹ := by
    rw [← hrecip]
    exact le_of_lt hlower
  simpa [ropeStandardChannel0TurnRatio, one_div] using hlower_le

/-- Twenty-decimal upper rational enclosure for the standard channel-0 turn
ratio `1 / (2π)`. -/
theorem ropeStandardChannel0_piD20_base_upper :
    ropeStandardChannel0TurnRatio ≤
      (100000000000000000000 : ℝ) / 628318530717958647692 := by
  have htwo_pi_pos : 0 < 2 * Real.pi := Real.two_pi_pos
  have hlower :
      (628318530717958647692 : ℝ) / 100000000000000000000 <
        2 * Real.pi := by
    nlinarith [Real.pi_gt_d20]
  have hrecip :
      ((628318530717958647692 : ℝ) / 100000000000000000000)⁻¹ =
        (100000000000000000000 : ℝ) / 628318530717958647692 := by
    norm_num
  have hupper :
      (2 * Real.pi)⁻¹ <
        ((628318530717958647692 : ℝ) / 100000000000000000000)⁻¹ :=
    (inv_lt_inv₀ htwo_pi_pos
      (by norm_num : (0 : ℝ) <
        (628318530717958647692 : ℝ) / 100000000000000000000)).2 hlower
  have hupper_le :
      (2 * Real.pi)⁻¹ ≤
        (100000000000000000000 : ℝ) / 628318530717958647692 := by
    rw [← hrecip]
    exact le_of_lt hupper
  simpa [ropeStandardChannel0TurnRatio, one_div] using hupper_le

private theorem ropeStandardChannel0_intervalWitness_of_gap_le_five
    {gap : Nat} (hgap_pos : 0 < gap) (hgap_le_five : gap ≤ 5) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0SeedMargin gap ((gap : ℚ) / 8) ((gap : ℚ) / 6) 0 := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0SeedMargin)
      (lowerBound := (1 : ℝ) / 8)
      (upperBound := (1 : ℝ) / 6)
      (gap := gap) (start := 1) (stop := 5)
      (lower := (gap : ℚ) / 8) (upper := (gap : ℚ) / 6) (cell := 0)
      (by norm_num [div_eq_mul_inv])
      (by norm_num [div_eq_mul_inv])
      ropeStandardChannel0_base_lower
      ropeStandardChannel0_base_upper
      (by norm_num)
      (by norm_num)
      (Nat.succ_le_of_lt hgap_pos)
      hgap_le_five
      (by norm_num [ropeStandardChannel0SeedMargin])
      (by norm_num [ropeStandardChannel0SeedMargin])

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
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D2SeedMargin)
      (lowerBound := (1 : ℝ) / 8)
      (upperBound := (25 : ℝ) / 157)
      (gap := gap) (start := 1) (stop := 6)
      (lower := (gap : ℚ) / 8)
      (upper := (((25 * gap : Nat) : ℚ) / 157)) (cell := 0)
      (by norm_num [div_eq_mul_inv])
      (by
        norm_num [Nat.cast_mul, div_eq_mul_inv]
        ring)
      ropeStandardChannel0_base_lower
      ropeStandardChannel0_d2_base_upper
      (by norm_num)
      (by norm_num)
      (Nat.succ_le_of_lt hgap_pos)
      hgap_le_six
      (by norm_num [ropeStandardChannel0D2SeedMargin])
      (by norm_num [ropeStandardChannel0D2SeedMargin])

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

private theorem ropeStandardChannel0_d3IntervalWitness_gap_eq_seven
    {gap : Nat} (hgap_eq : gap = 7) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D3SeedMargin gap ((10 : ℚ) / 9) ((175 : ℚ) / 157) 1 := by
  subst gap
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D3SeedMargin)
      (lowerBound := (10 : ℝ) / 63)
      (upperBound := (25 : ℝ) / 157)
      (gap := 7) (start := 7) (stop := 7)
      (lower := (10 : ℚ) / 9) (upper := (175 : ℚ) / 157) (cell := 1)
      (by norm_num [div_eq_mul_inv])
      (by norm_num [div_eq_mul_inv])
      ropeStandardChannel0_d3_base_lower
      ropeStandardChannel0_d2_base_upper
      (by norm_num)
      (by norm_num)
      (by norm_num)
      (by norm_num)
      (by norm_num [ropeStandardChannel0D3SeedMargin])
      (by norm_num [ropeStandardChannel0D3SeedMargin])

/-- A third standard-RoPE interval seed: channel 0 has margin `1/32` over
the tiny context containing gaps `1` through `7`.

The new gap is the first one whose standard turn ratio lies between one and two
turns. The proof therefore combines the earlier cell-0 witnesses for gaps up
to `6` with a separate cell-1 witness for gap `7`, using the sharper
`π < 3.15` lower enclosure for `1 / (2π)`. -/
theorem ropeStandardChannel0D3Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D3SeedMargin ropeStandardChannel0D3SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D3SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_eight : gap < 8 := by
    simpa [ropeStandardChannel0D3SeedContext] using List.mem_range.mp hgap_range
  by_cases hgap_le_six : gap ≤ 6
  · exact
      ⟨(gap : ℚ) / 8, (((25 * gap : Nat) : ℚ) / 157), 0,
        by
          simpa [ropeStandardChannel0D3SeedMargin, ropeStandardChannel0D2SeedMargin]
            using ropeStandardChannel0_d2IntervalWitness_of_gap_le_six hgap_pos hgap_le_six⟩
  · have hgap_eq_seven : gap = 7 := by omega
    exact
      ⟨(10 : ℚ) / 9, (175 : ℚ) / 157, 1,
        ropeStandardChannel0_d3IntervalWitness_gap_eq_seven hgap_eq_seven⟩

/-- The third named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `8`. -/
theorem ropeStandardChannel0D3Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D3SeedMargin ropeStandardChannel0D3SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D3Seed_intervalCertificate

private theorem ropeStandardChannel0_d4IntervalWitness_of_gap_between_seven_twelve
    {gap : Nat} (hgap_min : 7 ≤ gap) (hgap_max : gap ≤ 12) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D4SeedMargin gap (((10 * gap : Nat) : ℚ) / 63)
      (((25 * gap : Nat) : ℚ) / 157) 1 := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D4SeedMargin)
      (lowerBound := (10 : ℝ) / 63)
      (upperBound := (25 : ℝ) / 157)
      (gap := gap) (start := 7) (stop := 12)
      (lower := ((10 * gap : Nat) : ℚ) / 63)
      (upper := ((25 * gap : Nat) : ℚ) / 157) (cell := 1)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_d3_base_lower
      ropeStandardChannel0_d2_base_upper
      (by norm_num)
      (by norm_num)
      hgap_min
      hgap_max
      (by norm_num [ropeStandardChannel0D4SeedMargin])
      (by norm_num [ropeStandardChannel0D4SeedMargin])

private theorem ropeStandardChannel0_d4IntervalWitness_of_gap_between_thirteen_eighteen
    {gap : Nat} (hgap_min : 13 ≤ gap) (hgap_max : gap ≤ 18) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D4SeedMargin gap (((10 * gap : Nat) : ℚ) / 63)
      (((25 * gap : Nat) : ℚ) / 157) 2 := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D4SeedMargin)
      (lowerBound := (10 : ℝ) / 63)
      (upperBound := (25 : ℝ) / 157)
      (gap := gap) (start := 13) (stop := 18)
      (lower := ((10 * gap : Nat) : ℚ) / 63)
      (upper := ((25 * gap : Nat) : ℚ) / 157) (cell := 2)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_d3_base_lower
      ropeStandardChannel0_d2_base_upper
      (by norm_num)
      (by norm_num)
      hgap_min
      hgap_max
      (by norm_num [ropeStandardChannel0D4SeedMargin])
      (by norm_num [ropeStandardChannel0D4SeedMargin])

/-- A fourth standard-RoPE interval seed: channel 0 has margin `1/32` over
the tiny context containing gaps `1` through `18`.

This uses the earlier cell-0 witnesses through gap `6`, then uses the same
rational upper enclosure with the sharper `π < 3.15` lower enclosure to place
gaps `7` through `12` in cell `1` and gaps `13` through `18` in cell `2`. -/
theorem ropeStandardChannel0D4Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D4SeedMargin ropeStandardChannel0D4SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D4SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_nineteen : gap < 19 := by
    simpa [ropeStandardChannel0D4SeedContext] using List.mem_range.mp hgap_range
  by_cases hgap_le_six : gap ≤ 6
  · exact
      ⟨(gap : ℚ) / 8, (((25 * gap : Nat) : ℚ) / 157), 0,
        by
          simpa [ropeStandardChannel0D4SeedMargin, ropeStandardChannel0D2SeedMargin]
            using ropeStandardChannel0_d2IntervalWitness_of_gap_le_six hgap_pos hgap_le_six⟩
  · by_cases hgap_le_twelve : gap ≤ 12
    · have hgap_min : 7 ≤ gap := by omega
      exact
        ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 1,
          ropeStandardChannel0_d4IntervalWitness_of_gap_between_seven_twelve
            hgap_min hgap_le_twelve⟩
    · have hgap_min : 13 ≤ gap := by omega
      have hgap_max : gap ≤ 18 := by omega
      exact
        ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 2,
          ropeStandardChannel0_d4IntervalWitness_of_gap_between_thirteen_eighteen
            hgap_min hgap_max⟩

/-- The fourth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `19`. -/
theorem ropeStandardChannel0D4Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D4SeedMargin ropeStandardChannel0D4SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D4Seed_intervalCertificate

private theorem ropeStandardChannel0_d5IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 64 ≤ (gap : ℝ) * ((10 : ℝ) / 63))
    (hcell_upper :
      (gap : ℝ) * ((25 : ℝ) / 157) ≤ (cell : ℝ) + 1 - (1 : ℝ) / 64) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D5SeedMargin gap (((10 * gap : Nat) : ℚ) / 63)
      (((25 * gap : Nat) : ℚ) / 157) cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D5SeedMargin)
      (lowerBound := (10 : ℝ) / 63)
      (upperBound := (25 : ℝ) / 157)
      (gap := gap) (start := gap) (stop := gap)
      (lower := ((10 * gap : Nat) : ℚ) / 63)
      (upper := ((25 * gap : Nat) : ℚ) / 157) (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_d3_base_lower
      ropeStandardChannel0_d2_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D5SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D5SeedMargin] using hcell_upper)

/-- A fifth standard-RoPE interval seed: channel 0 has margin `1/64` over
the tiny context containing gaps `1` through `43`.

The proof reuses the context-19, margin-`1/32` certificate for gaps through
`18`, then checks cell bands `3` through `6` for the remaining gaps using the
same rational enclosure `10*gap/63 <= gap/(2π) <= 25*gap/157`. -/
theorem ropeStandardChannel0D5Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D5SeedMargin ropeStandardChannel0D5SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D5SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_forty_four : gap < 44 := by
    simpa [ropeStandardChannel0D5SeedContext] using List.mem_range.mp hgap_range
  by_cases hgap_le_eighteen : gap ≤ 18
  · have hgap_range_d4 : gap ∈ List.range ropeStandardChannel0D4SeedContext := by
      apply List.mem_range.mpr
      simpa [ropeStandardChannel0D4SeedContext] using Nat.lt_succ_of_le hgap_le_eighteen
    have hsmall :
        ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
          ropeStandardChannel0D5SeedMargin ropeStandardChannel0D4SeedContext :=
      ropeTurnRatioIntervalCertificate_mono_margin
        (turnRatio := ropeStandardChannel0TurnRatio)
        (smallMargin := ropeStandardChannel0D5SeedMargin)
        (largeMargin := ropeStandardChannel0D4SeedMargin)
        (context := ropeStandardChannel0D4SeedContext)
        (by dsimp [ropeStandardChannel0D5SeedMargin]; norm_num)
        (by dsimp [ropeStandardChannel0D5SeedMargin, ropeStandardChannel0D4SeedMargin]; norm_num)
        ropeStandardChannel0D4Seed_intervalCertificate
    exact hsmall.2 gap hgap_range_d4 hgap_pos
  · by_cases hgap_le_twenty_five : gap ≤ 25
    · have hgap_min : 19 ≤ gap := by omega
      have hgap_min_real : (19 : ℝ) ≤ gap := by exact_mod_cast hgap_min
      have hgap_max_real : (gap : ℝ) ≤ 25 := by exact_mod_cast hgap_le_twenty_five
      have hcell_lower :
          (((3 : Int) : ℝ) + (1 : ℝ) / 64) ≤ (gap : ℝ) * ((10 : ℝ) / 63) := by
        nlinarith
      have hcell_upper :
          (gap : ℝ) * ((25 : ℝ) / 157) ≤ (((3 : Int) : ℝ) + 1 - (1 : ℝ) / 64) := by
        nlinarith
      exact
        ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 3,
          ropeStandardChannel0_d5IntervalWitness_of_scaled_bounds
            (gap := gap) (cell := 3) hcell_lower hcell_upper⟩
    · by_cases hgap_le_thirty_one : gap ≤ 31
      · have hgap_min : 26 ≤ gap := by omega
        have hgap_min_real : (26 : ℝ) ≤ gap := by exact_mod_cast hgap_min
        have hgap_max_real : (gap : ℝ) ≤ 31 := by exact_mod_cast hgap_le_thirty_one
        have hcell_lower :
            (((4 : Int) : ℝ) + (1 : ℝ) / 64) ≤ (gap : ℝ) * ((10 : ℝ) / 63) := by
          nlinarith
        have hcell_upper :
            (gap : ℝ) * ((25 : ℝ) / 157) ≤ (((4 : Int) : ℝ) + 1 - (1 : ℝ) / 64) := by
          nlinarith
        exact
          ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 4,
            ropeStandardChannel0_d5IntervalWitness_of_scaled_bounds
              (gap := gap) (cell := 4) hcell_lower hcell_upper⟩
      · by_cases hgap_le_thirty_seven : gap ≤ 37
        · have hgap_min : 32 ≤ gap := by omega
          have hgap_min_real : (32 : ℝ) ≤ gap := by exact_mod_cast hgap_min
          have hgap_max_real : (gap : ℝ) ≤ 37 := by exact_mod_cast hgap_le_thirty_seven
          have hcell_lower :
              (((5 : Int) : ℝ) + (1 : ℝ) / 64) ≤ (gap : ℝ) * ((10 : ℝ) / 63) := by
            nlinarith
          have hcell_upper :
              (gap : ℝ) * ((25 : ℝ) / 157) ≤ (((5 : Int) : ℝ) + 1 - (1 : ℝ) / 64) := by
            nlinarith
          exact
            ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 5,
              ropeStandardChannel0_d5IntervalWitness_of_scaled_bounds
                (gap := gap) (cell := 5) hcell_lower hcell_upper⟩
        · have hgap_min : 38 ≤ gap := by omega
          have hgap_max : gap ≤ 43 := by omega
          have hgap_min_real : (38 : ℝ) ≤ gap := by exact_mod_cast hgap_min
          have hgap_max_real : (gap : ℝ) ≤ 43 := by exact_mod_cast hgap_max
          have hcell_lower :
              (((6 : Int) : ℝ) + (1 : ℝ) / 64) ≤ (gap : ℝ) * ((10 : ℝ) / 63) := by
            nlinarith
          have hcell_upper :
              (gap : ℝ) * ((25 : ℝ) / 157) ≤ (((6 : Int) : ℝ) + 1 - (1 : ℝ) / 64) := by
            nlinarith
          exact
            ⟨((10 * gap : Nat) : ℚ) / 63, ((25 * gap : Nat) : ℚ) / 157, 6,
              ropeStandardChannel0_d5IntervalWitness_of_scaled_bounds
                (gap := gap) (cell := 6) hcell_lower hcell_upper⟩

/-- The fifth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `44`. -/
theorem ropeStandardChannel0D5Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D5SeedMargin ropeStandardChannel0D5SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D5Seed_intervalCertificate

private theorem ropeStandardChannel0_d6IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 512 ≤ (gap : ℝ) * ((5000 : ℝ) / 31416))
    (hcell_upper :
      (gap : ℝ) * ((5000 : ℝ) / 31415) ≤ (cell : ℝ) + 1 - (1 : ℝ) / 512) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D6SeedMargin gap (((5000 * gap : Nat) : ℚ) / 31416)
      (((5000 * gap : Nat) : ℚ) / 31415) cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D6SeedMargin)
      (lowerBound := (5000 : ℝ) / 31416)
      (upperBound := (5000 : ℝ) / 31415)
      (gap := gap) (start := gap) (stop := gap)
      (lower := ((5000 * gap : Nat) : ℚ) / 31416)
      (upper := ((5000 * gap : Nat) : ℚ) / 31415) (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD4_base_lower
      ropeStandardChannel0_piD4_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D6SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D6SeedMargin] using hcell_upper)

/-- A sixth standard-RoPE interval seed: channel 0 has margin `1/512` over
the tiny context containing gaps `1` through `56`.

The proof reuses the context-44 certificate after lowering the advertised
margin, then crosses the gap-44 near-integer obstruction with the sharper
four-decimal enclosure
`5000*gap/31416 <= gap/(2π) <= 5000*gap/31415`. -/
theorem ropeStandardChannel0D6Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D6SeedMargin ropeStandardChannel0D6SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D6SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt_fifty_seven : gap < 57 := by
    simpa [ropeStandardChannel0D6SeedContext] using List.mem_range.mp hgap_range
  by_cases hgap_le_forty_three : gap ≤ 43
  · have hgap_range_d5 : gap ∈ List.range ropeStandardChannel0D5SeedContext := by
      apply List.mem_range.mpr
      simpa [ropeStandardChannel0D5SeedContext] using Nat.lt_succ_of_le hgap_le_forty_three
    have hsmall :
        ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
          ropeStandardChannel0D6SeedMargin ropeStandardChannel0D5SeedContext :=
      ropeTurnRatioIntervalCertificate_mono_margin
        (turnRatio := ropeStandardChannel0TurnRatio)
        (smallMargin := ropeStandardChannel0D6SeedMargin)
        (largeMargin := ropeStandardChannel0D5SeedMargin)
        (context := ropeStandardChannel0D5SeedContext)
        (by dsimp [ropeStandardChannel0D6SeedMargin]; norm_num)
        (by dsimp [ropeStandardChannel0D6SeedMargin, ropeStandardChannel0D5SeedMargin]; norm_num)
        ropeStandardChannel0D5Seed_intervalCertificate
    exact hsmall.2 gap hgap_range_d5 hgap_pos
  · by_cases hgap_le_fifty : gap ≤ 50
    · have hgap_min : 44 ≤ gap := by omega
      have hgap_min_real : (44 : ℝ) ≤ gap := by exact_mod_cast hgap_min
      have hgap_max_real : (gap : ℝ) ≤ 50 := by exact_mod_cast hgap_le_fifty
      have hcell_lower :
          (((7 : Int) : ℝ) + (1 : ℝ) / 512) ≤
            (gap : ℝ) * ((5000 : ℝ) / 31416) := by
        nlinarith
      have hcell_upper :
          (gap : ℝ) * ((5000 : ℝ) / 31415) ≤
            (((7 : Int) : ℝ) + 1 - (1 : ℝ) / 512) := by
        nlinarith
      exact
        ⟨((5000 * gap : Nat) : ℚ) / 31416,
          ((5000 * gap : Nat) : ℚ) / 31415, 7,
          ropeStandardChannel0_d6IntervalWitness_of_scaled_bounds
            (gap := gap) (cell := 7) hcell_lower hcell_upper⟩
    · have hgap_min : 51 ≤ gap := by omega
      have hgap_max : gap ≤ 56 := by omega
      have hgap_min_real : (51 : ℝ) ≤ gap := by exact_mod_cast hgap_min
      have hgap_max_real : (gap : ℝ) ≤ 56 := by exact_mod_cast hgap_max
      have hcell_lower :
          (((8 : Int) : ℝ) + (1 : ℝ) / 512) ≤
            (gap : ℝ) * ((5000 : ℝ) / 31416) := by
        nlinarith
      have hcell_upper :
          (gap : ℝ) * ((5000 : ℝ) / 31415) ≤
            (((8 : Int) : ℝ) + 1 - (1 : ℝ) / 512) := by
        nlinarith
      exact
        ⟨((5000 * gap : Nat) : ℚ) / 31416,
          ((5000 * gap : Nat) : ℚ) / 31415, 8,
          ropeStandardChannel0_d6IntervalWitness_of_scaled_bounds
            (gap := gap) (cell := 8) hcell_lower hcell_upper⟩

/-- The sixth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `57`. -/
theorem ropeStandardChannel0D6Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D6SeedMargin ropeStandardChannel0D6SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D6Seed_intervalCertificate

private theorem ropeStandardChannel0_d7IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D7SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D7SeedMargin gap (((5000 * gap : Nat) : ℚ) / 31416)
      (((5000 * gap : Nat) : ℚ) / 31415) (ropeStandardChannel0D7Cell gap) := by
  unfold ropeStandardChannel0D7SeedContext at hgap_lt
  interval_cases hgap_value : gap <;> subst gap <;>
    dsimp [ropeStandardChannel0D7SeedMargin, ropeStandardChannel0D6SeedMargin,
      ropeStandardChannel0D7Cell]
  all_goals
    apply ropeStandardChannel0_d6IntervalWitness_of_scaled_bounds <;> norm_num

/-- A seventh standard-RoPE interval seed: channel 0 has margin `1/512` over
the context containing gaps `1` through `332`.

The proof uses a generated exact rational cell table for the same four-decimal
enclosure `5000*gap/31416 <= gap/(2π) <= 5000*gap/31415`. The next obstruction
for this table appears at gap `333`, so this certificate stops at context
`333`. -/
theorem ropeStandardChannel0D7Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D7SeedMargin ropeStandardChannel0D7SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D7SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D7SeedContext := by
    simpa [ropeStandardChannel0D7SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((5000 * gap : Nat) : ℚ) / 31416,
      ((5000 * gap : Nat) : ℚ) / 31415,
      ropeStandardChannel0D7Cell gap,
      ropeStandardChannel0_d7IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The seventh named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `333`. -/
theorem ropeStandardChannel0D7Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D7SeedMargin ropeStandardChannel0D7SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D7Seed_intervalCertificate

private theorem ropeStandardChannel0_d8IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 1024 ≤ (gap : ℝ) * ((500000 : ℝ) / 3141593))
    (hcell_upper :
      (gap : ℝ) * ((500000 : ℝ) / 3141592) ≤ (cell : ℝ) + 1 - (1 : ℝ) / 1024) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D8SeedMargin gap (((500000 * gap : Nat) : ℚ) / 3141593)
      (((500000 * gap : Nat) : ℚ) / 3141592) cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D8SeedMargin)
      (lowerBound := (500000 : ℝ) / 3141593)
      (upperBound := (500000 : ℝ) / 3141592)
      (gap := gap) (start := gap) (stop := gap)
      (lower := ((500000 * gap : Nat) : ℚ) / 3141593)
      (upper := ((500000 * gap : Nat) : ℚ) / 3141592) (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD6_base_lower
      ropeStandardChannel0_piD6_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D8SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D8SeedMargin] using hcell_upper)

private theorem ropeStandardChannel0_d8IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D8SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D8SeedMargin gap (((500000 * gap : Nat) : ℚ) / 3141593)
      (((500000 * gap : Nat) : ℚ) / 3141592) (ropeStandardChannel0D8Cell gap) := by
  unfold ropeStandardChannel0D8SeedContext at hgap_lt
  interval_cases hgap_value : gap <;> subst gap <;>
    dsimp [ropeStandardChannel0D8SeedMargin, ropeStandardChannel0D8Cell]
  all_goals
    apply ropeStandardChannel0_d8IntervalWitness_of_scaled_bounds <;> norm_num

/-- An eighth standard-RoPE interval seed: channel 0 has margin `1/1024`
over the context containing gaps `1` through `709`.

The proof uses a generated exact rational cell table expressed as a computed
floor cell for the six-decimal enclosure
`500000*gap/3141593 <= gap/(2π) <= 500000*gap/3141592`. The next obstruction
for this table appears at gap `710`, so this certificate stops at context
`710`. -/
theorem ropeStandardChannel0D8Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D8SeedMargin ropeStandardChannel0D8SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D8SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D8SeedContext := by
    simpa [ropeStandardChannel0D8SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((500000 * gap : Nat) : ℚ) / 3141593,
      ((500000 * gap : Nat) : ℚ) / 3141592,
      ropeStandardChannel0D8Cell gap,
      ropeStandardChannel0_d8IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The eighth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `710`. -/
theorem ropeStandardChannel0D8Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D8SeedMargin ropeStandardChannel0D8SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D8Seed_intervalCertificate

/-- The gap `710` is already within the advertised `1/1024` margin of integer
turn `113` for standard RoPE channel 0.

This explains why the context-`710` seed is a sharp stopping point for this
margin: the seed context contains gaps below `710`, while any larger context
would have to certify the obstructing gap `710`. -/
theorem ropeStandardChannel0D8_gap710_error_lt_margin :
    ropeTurnRatioError ropeStandardChannel0TurnRatio 710 113 <
      ropeStandardChannel0D8SeedMargin := by
  unfold ropeTurnRatioError ropeStandardChannel0D8SeedMargin
  have hlower :
      (710 : ℝ) * ((500000 : ℝ) / 3141593) ≤
        (710 : ℝ) * ropeStandardChannel0TurnRatio :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD6_base_lower (by norm_num)
  have hupper :
      (710 : ℝ) * ropeStandardChannel0TurnRatio ≤
        (710 : ℝ) * ((500000 : ℝ) / 3141592) :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD6_base_upper (by norm_num)
  rw [abs_lt]
  constructor
  · have hgap_lower :
        (113 : ℝ) - (1 : ℝ) / 1024 <
          (710 : ℝ) * ((500000 : ℝ) / 3141593) := by
      norm_num
    linarith
  · have hgap_upper :
        (710 : ℝ) * ((500000 : ℝ) / 3141592) <
          (113 : ℝ) + (1 : ℝ) / 1024 := by
      norm_num
    linarith

/-- The context-`710`, margin-`1/1024` standard-channel seed cannot be extended
to any strictly larger context at the same margin.

The obstruction is the concrete near-integer return at gap `710`, integer turn
`113`. -/
theorem not_ropeStandardChannel0D8SeedMargin_of_context_gt_seed
    {context : Nat} (hcontext : ropeStandardChannel0D8SeedContext < context) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D8SeedMargin context := by
  have hgap_lt : 710 < context := by
    simpa [ropeStandardChannel0D8SeedContext] using hcontext
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D8SeedMargin)
      (context := context) (gap := 710) (turns := 113)
      (by norm_num) hgap_lt ropeStandardChannel0D8_gap710_error_lt_margin

private theorem ropeStandardChannel0_d9IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 131072 ≤
        (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694))
    (hcell_upper :
      (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) ≤
        (cell : ℝ) + 1 - (1 : ℝ) / 131072) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D9SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D9SeedMargin)
      (lowerBound := (100000000000000000000 : ℝ) / 628318530717958647694)
      (upperBound := (100000000000000000000 : ℝ) / 628318530717958647692)
      (gap := gap) (start := gap) (stop := gap)
      (lower :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (upper :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD20_base_lower
      ropeStandardChannel0_piD20_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D9SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D9SeedMargin] using hcell_upper)

set_option maxHeartbeats 5000000 in
private theorem ropeStandardChannel0_d9IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D9SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D9SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  unfold ropeStandardChannel0D9SeedContext at hgap_lt
  interval_cases hgap_value : gap <;> subst gap <;>
    dsimp [ropeStandardChannel0D9SeedMargin, ropeStandardChannel0D9Cell]
  all_goals
    apply ropeStandardChannel0_d9IntervalWitness_of_scaled_bounds <;> norm_num

/-- A ninth standard-RoPE interval seed: channel 0 has margin `1/131072`
over the 4k context containing gaps `1` through `4095`.

The proof uses a generated exact rational cell table expressed as a computed
floor cell for the 20-decimal enclosure
`10^20*gap/628318530717958647694 <= gap/(2π) <=
10^20*gap/628318530717958647692`. -/
theorem ropeStandardChannel0D9Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D9SeedMargin ropeStandardChannel0D9SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D9SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D9SeedContext := by
    simpa [ropeStandardChannel0D9SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d9IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The ninth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin over context `4096`. -/
theorem ropeStandardChannel0D9Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D9SeedMargin ropeStandardChannel0D9SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D9Seed_intervalCertificate

private theorem ropeStandardChannel0_d10IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 105000 ≤
        (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694))
    (hcell_upper :
      (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) ≤
        (cell : ℝ) + 1 - (1 : ℝ) / 105000) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D10SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D10SeedMargin)
      (lowerBound := (100000000000000000000 : ℝ) / 628318530717958647694)
      (upperBound := (100000000000000000000 : ℝ) / 628318530717958647692)
      (gap := gap) (start := gap) (stop := gap)
      (lower :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (upper :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD20_base_lower
      ropeStandardChannel0_piD20_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D10SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D10SeedMargin] using hcell_upper)

set_option maxHeartbeats 5000000 in
private theorem ropeStandardChannel0_d10IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D10SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D10SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  unfold ropeStandardChannel0D10SeedContext at hgap_lt
  interval_cases hgap_value : gap <;> subst gap <;>
    dsimp [ropeStandardChannel0D10SeedMargin, ropeStandardChannel0D9Cell]
  all_goals
    apply ropeStandardChannel0_d10IntervalWitness_of_scaled_bounds <;> norm_num

/-- A tenth standard-RoPE interval seed: channel 0 has margin `1/105000`
over the same 4k context as the D9 seed.

This tightens the previous advertised `1/131072` margin using the same
20-decimal rational enclosure and generated integer-cell table. It is still a
finite one-channel certificate, not a full-bank or long-context theorem. -/
theorem ropeStandardChannel0D10Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D10SeedMargin ropeStandardChannel0D10SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D10SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D10SeedContext := by
    simpa [ropeStandardChannel0D10SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d10IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The tenth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin `1/105000` over context `4096`. -/
theorem ropeStandardChannel0D10Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D10SeedMargin ropeStandardChannel0D10SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D10Seed_intervalCertificate

private theorem ropeStandardChannel0_d11IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 104219 ≤
        (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694))
    (hcell_upper :
      (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) ≤
        (cell : ℝ) + 1 - (1 : ℝ) / 104219) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D11SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D11SeedMargin)
      (lowerBound := (100000000000000000000 : ℝ) / 628318530717958647694)
      (upperBound := (100000000000000000000 : ℝ) / 628318530717958647692)
      (gap := gap) (start := gap) (stop := gap)
      (lower :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (upper :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD20_base_lower
      ropeStandardChannel0_piD20_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D11SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D11SeedMargin] using hcell_upper)

set_option maxHeartbeats 5000000 in
private theorem ropeStandardChannel0_d11IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D11SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D11SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  unfold ropeStandardChannel0D11SeedContext at hgap_lt
  interval_cases hgap_value : gap <;> subst gap <;>
    dsimp [ropeStandardChannel0D11SeedMargin, ropeStandardChannel0D9Cell]
  all_goals
    apply ropeStandardChannel0_d11IntervalWitness_of_scaled_bounds <;> norm_num

/-- An eleventh standard-RoPE interval seed: channel 0 has margin `1/104219`
over the same 4k context as the D9 and D10 seeds.

The companion obstruction below shows that the adjacent larger margin
`1/104218` already fails at gap `710`, so this seed is the sharpest margin
found by the current 20-decimal interval planner for this certificate shape. -/
theorem ropeStandardChannel0D11Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D11SeedMargin ropeStandardChannel0D11SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D11SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D11SeedContext := by
    simpa [ropeStandardChannel0D11SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d11IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The eleventh named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin `1/104219` over context `4096`. -/
theorem ropeStandardChannel0D11Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D11SeedMargin ropeStandardChannel0D11SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D11Seed_intervalCertificate

private theorem ropeStandardChannel0_d12IntervalWitness_of_scaled_bounds
    {gap : Nat} {cell : Int}
    (hcell_lower :
      (cell : ℝ) + (1 : ℝ) / 104220 ≤
        (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694))
    (hcell_upper :
      (gap : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) ≤
        (cell : ℝ) + 1 - (1 : ℝ) / 104220) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D12SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      cell := by
  exact
    ropeTurnRatioIntervalWitness_of_band_bounds
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := ropeStandardChannel0D12SeedMargin)
      (lowerBound := (100000000000000000000 : ℝ) / 628318530717958647694)
      (upperBound := (100000000000000000000 : ℝ) / 628318530717958647692)
      (gap := gap) (start := gap) (stop := gap)
      (lower :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (upper :=
        ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (cell := cell)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      (by
        norm_num [Nat.cast_mul]
        ring_nf)
      ropeStandardChannel0_piD20_base_lower
      ropeStandardChannel0_piD20_base_upper
      (by norm_num)
      (by norm_num)
      le_rfl
      le_rfl
      (by simpa [ropeStandardChannel0D12SeedMargin] using hcell_lower)
      (by simpa [ropeStandardChannel0D12SeedMargin] using hcell_upper)

set_option maxHeartbeats 8000000 in
private theorem ropeStandardChannel0_d12IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D12SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D12SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  by_cases hgap_d11 : gap < ropeStandardChannel0D11SeedContext
  · apply ropeTurnRatioIntervalWitness_mono_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (smallMargin := ropeStandardChannel0D12SeedMargin)
      (largeMargin := ropeStandardChannel0D11SeedMargin)
      (gap := gap)
      (lower := ((100000000000000000000 * gap : Nat) : ℚ) /
        628318530717958647694)
      (upper := ((100000000000000000000 * gap : Nat) : ℚ) /
        628318530717958647692)
      (cell := ropeStandardChannel0D9Cell gap)
    · dsimp [ropeStandardChannel0D12SeedMargin, ropeStandardChannel0D11SeedMargin]
      norm_num
    · exact ropeStandardChannel0_d11IntervalWitness_of_gap_lt_context
        hgap_pos hgap_d11
  · have hgap_ge : ropeStandardChannel0D11SeedContext ≤ gap := le_of_not_gt hgap_d11
    unfold ropeStandardChannel0D11SeedContext at hgap_ge
    unfold ropeStandardChannel0D12SeedContext at hgap_lt
    interval_cases hgap_value : gap <;> subst gap <;>
      dsimp [ropeStandardChannel0D12SeedMargin, ropeStandardChannel0D9Cell]
    all_goals
      apply ropeStandardChannel0_d12IntervalWitness_of_scaled_bounds <;> norm_num

/-- A twelfth standard-RoPE interval seed: channel 0 has margin `1/104220`
over an 8k context using the same 20-decimal rational enclosure. -/
theorem ropeStandardChannel0D12Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D12SeedMargin ropeStandardChannel0D12SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D12SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D12SeedContext := by
    simpa [ropeStandardChannel0D12SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d12IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The twelfth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin `1/104220` over context `8192`. -/
theorem ropeStandardChannel0D12Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D12SeedMargin ropeStandardChannel0D12SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D12Seed_intervalCertificate

set_option maxHeartbeats 8000000 in
private theorem ropeStandardChannel0_d13IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D13SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D13SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  by_cases hgap_d11 : gap < ropeStandardChannel0D11SeedContext
  · simpa [ropeStandardChannel0D13SeedMargin, ropeStandardChannel0D11SeedMargin]
      using ropeStandardChannel0_d11IntervalWitness_of_gap_lt_context
        hgap_pos hgap_d11
  · have hgap_ge : ropeStandardChannel0D11SeedContext ≤ gap := le_of_not_gt hgap_d11
    unfold ropeStandardChannel0D11SeedContext at hgap_ge
    unfold ropeStandardChannel0D13SeedContext at hgap_lt
    interval_cases hgap_value : gap <;> subst gap <;>
      dsimp [ropeStandardChannel0D13SeedMargin, ropeStandardChannel0D11SeedMargin,
        ropeStandardChannel0D9Cell]
    all_goals
      apply ropeStandardChannel0_d11IntervalWitness_of_scaled_bounds <;> norm_num

/-- A thirteenth standard-RoPE interval seed: channel 0 has margin `1/104219`
over an 8k context using the same 20-decimal rational enclosure. -/
theorem ropeStandardChannel0D13Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D13SeedMargin ropeStandardChannel0D13SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D13SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D13SeedContext := by
    simpa [ropeStandardChannel0D13SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d13IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The thirteenth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin `1/104219` over context `8192`. -/
theorem ropeStandardChannel0D13Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D13SeedMargin ropeStandardChannel0D13SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D13Seed_intervalCertificate

set_option maxHeartbeats 12000000 in
private theorem ropeStandardChannel0_d14IntervalWitness_of_gap_lt_context
    {gap : Nat} (hgap_pos : 0 < gap)
    (hgap_lt : gap < ropeStandardChannel0D14SeedContext) :
    ropeTurnRatioIntervalWitness ropeStandardChannel0TurnRatio
      ropeStandardChannel0D14SeedMargin gap
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694)
      (((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692)
      (ropeStandardChannel0D9Cell gap) := by
  by_cases hgap_d13 : gap < ropeStandardChannel0D13SeedContext
  · simpa [ropeStandardChannel0D14SeedMargin, ropeStandardChannel0D13SeedMargin]
      using ropeStandardChannel0_d13IntervalWitness_of_gap_lt_context
        hgap_pos hgap_d13
  · have hgap_ge : ropeStandardChannel0D13SeedContext ≤ gap := le_of_not_gt hgap_d13
    unfold ropeStandardChannel0D13SeedContext at hgap_ge
    unfold ropeStandardChannel0D14SeedContext at hgap_lt
    interval_cases hgap_value : gap <;> subst gap <;>
      dsimp [ropeStandardChannel0D14SeedMargin, ropeStandardChannel0D11SeedMargin,
        ropeStandardChannel0D9Cell]
    all_goals
      apply ropeStandardChannel0_d11IntervalWitness_of_scaled_bounds <;> norm_num

/-- A fourteenth standard-RoPE interval seed: channel 0 has margin `1/104219`
over a 16k context using the same 20-decimal rational enclosure. -/
theorem ropeStandardChannel0D14Seed_intervalCertificate :
    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio
      ropeStandardChannel0D14SeedMargin ropeStandardChannel0D14SeedContext := by
  refine ⟨by dsimp [ropeStandardChannel0D14SeedMargin]; norm_num, ?_⟩
  intro gap hgap_range hgap_pos
  have hgap_lt : gap < ropeStandardChannel0D14SeedContext := by
    simpa [ropeStandardChannel0D14SeedContext] using List.mem_range.mp hgap_range
  exact
    ⟨((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647694,
      ((100000000000000000000 * gap : Nat) : ℚ) / 628318530717958647692,
      ropeStandardChannel0D9Cell gap,
      ropeStandardChannel0_d14IntervalWitness_of_gap_lt_context hgap_pos hgap_lt⟩

/-- The fourteenth named standard-RoPE channel-0 seed has a proved finite
turn-ratio margin `1/104219` over context `16384`. -/
theorem ropeStandardChannel0D14Seed_turnRatioFiniteMargin :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D14SeedMargin ropeStandardChannel0D14SeedContext :=
  ropeTurnRatioFiniteMargin_of_intervalCertificate
    ropeStandardChannel0D14Seed_intervalCertificate

/-- Gap `710` is already within margin `1/65536` of integer turn `113` for
the genuine standard channel-0 turn ratio.

This is a sharper obstruction than the earlier context-`710`,
margin-`1/1024` stop theorem. It explains why the 4k interval seed uses the
smaller advertised margin `1/131072`: any context containing gap `710` cannot
certify the doubled margin `1/65536` for this single channel. -/
theorem ropeStandardChannel0_gap710_error_lt_one_over_65536 :
    ropeTurnRatioError ropeStandardChannel0TurnRatio 710 (113 : Int) <
      (1 : ℝ) / 65536 := by
  unfold ropeTurnRatioError
  have hlower :
      (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694) ≤
        (710 : ℝ) * ropeStandardChannel0TurnRatio :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_lower (by norm_num)
  have hupper :
      (710 : ℝ) * ropeStandardChannel0TurnRatio ≤
        (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_upper (by norm_num)
  rw [abs_lt]
  constructor
  · have hgap_lower :
        (113 : ℝ) - (1 : ℝ) / 65536 <
          (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647694) := by
      norm_num
    linarith
  · have hgap_upper :
        (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647692) <
          (113 : ℝ) + (1 : ℝ) / 65536 := by
      norm_num
    linarith

/-- No standard channel-0 finite-context margin of `1/65536` is possible once
the inspected context contains gap `710`.

This is a useful negative certificate for the current 4k seed: the proved
margin `1/131072` is conservative, but the immediately doubled margin
`1/65536` is impossible for every context strictly larger than `710`. -/
theorem not_ropeStandardChannel0_margin_one_over_65536_of_context_gt_710
    {context : Nat} (hcontext : 710 < context) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 65536) context := by
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := (1 : ℝ) / 65536)
      (context := context) (gap := 710) (turns := 113)
      (by norm_num) hcontext
      ropeStandardChannel0_gap710_error_lt_one_over_65536

/-- Gap `710` is already within margin `1/104000` of integer turn `113` for
the genuine standard channel-0 turn ratio.

This brackets the tighter 4k D10 seed: Lean proves margin `1/105000` over the
4k context, while this concrete near-return prevents the nearby larger margin
`1/104000` for every context containing gap `710`. -/
theorem ropeStandardChannel0_gap710_error_lt_one_over_104000 :
    ropeTurnRatioError ropeStandardChannel0TurnRatio 710 (113 : Int) <
      (1 : ℝ) / 104000 := by
  unfold ropeTurnRatioError
  have hlower :
      (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694) ≤
        (710 : ℝ) * ropeStandardChannel0TurnRatio :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_lower (by norm_num)
  have hupper :
      (710 : ℝ) * ropeStandardChannel0TurnRatio ≤
        (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_upper (by norm_num)
  rw [abs_lt]
  constructor
  · have hgap_lower :
        (113 : ℝ) - (1 : ℝ) / 104000 <
          (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647694) := by
      norm_num
    linarith
  · have hgap_upper :
        (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647692) <
          (113 : ℝ) + (1 : ℝ) / 104000 := by
      norm_num
    linarith

/-- No standard channel-0 finite-context margin of `1/104000` is possible once
the inspected context contains gap `710`. -/
theorem not_ropeStandardChannel0_margin_one_over_104000_of_context_gt_710
    {context : Nat} (hcontext : 710 < context) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104000) context := by
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := (1 : ℝ) / 104000)
      (context := context) (gap := 710) (turns := 113)
      (by norm_num) hcontext
      ropeStandardChannel0_gap710_error_lt_one_over_104000

/-- Gap `710` is already within margin `1/104218` of integer turn `113` for
the genuine standard channel-0 turn ratio.

This is the adjacent obstruction for the D11 seed: the generated d20 interval
table proves margin `1/104219`, while this theorem proves that increasing the
margin to `1/104218` is impossible for any context containing gap `710`. -/
theorem ropeStandardChannel0_gap710_error_lt_one_over_104218 :
    ropeTurnRatioError ropeStandardChannel0TurnRatio 710 (113 : Int) <
      (1 : ℝ) / 104218 := by
  unfold ropeTurnRatioError
  have hlower :
      (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694) ≤
        (710 : ℝ) * ropeStandardChannel0TurnRatio :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_lower (by norm_num)
  have hupper :
      (710 : ℝ) * ropeStandardChannel0TurnRatio ≤
        (710 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_upper (by norm_num)
  rw [abs_lt]
  constructor
  · have hgap_lower :
        (113 : ℝ) - (1 : ℝ) / 104218 <
          (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647694) := by
      norm_num
    linarith
  · have hgap_upper :
        (710 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647692) <
          (113 : ℝ) + (1 : ℝ) / 104218 := by
      norm_num
    linarith

/-- No standard channel-0 finite-context margin of `1/104218` is possible once
the inspected context contains gap `710`. -/
theorem not_ropeStandardChannel0_margin_one_over_104218_of_context_gt_710
    {context : Nat} (hcontext : 710 < context) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104218) context := by
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := (1 : ℝ) / 104218)
      (context := context) (gap := 710) (turns := 113)
      (by norm_num) hcontext
      ropeStandardChannel0_gap710_error_lt_one_over_104218

/-- No standard channel-0 finite-context margin at or above `1/104218` is
possible once the inspected context contains gap `710`. -/
theorem not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710
    {context : Nat} {margin : ℝ} (hcontext : 710 < context)
    (hmargin : (1 : ℝ) / 104218 ≤ margin) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin context := by
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := margin)
      (context := context) (gap := 710) (turns := 113)
      (by norm_num) hcontext
      (lt_of_lt_of_le
        ropeStandardChannel0_gap710_error_lt_one_over_104218 hmargin)

/-- Gap `103993` is already within margin `1/328458` of integer turn `16551`
for the genuine standard channel-0 turn ratio.

This is the 128k frontier obstruction for the generated D17 seed: the D17
certificate proves margin `1/328459`, while this concrete near-return prevents
the adjacent larger margin `1/328458` for every context containing this gap. -/
theorem ropeStandardChannel0_gap103993_error_lt_one_over_328458 :
    ropeTurnRatioError ropeStandardChannel0TurnRatio 103993 (16551 : Int) <
      (1 : ℝ) / 328458 := by
  unfold ropeTurnRatioError
  have hlower :
      (103993 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647694) ≤
        (103993 : ℝ) * ropeStandardChannel0TurnRatio :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_lower (by norm_num)
  have hupper :
      (103993 : ℝ) * ropeStandardChannel0TurnRatio ≤
        (103993 : ℝ) * ((100000000000000000000 : ℝ) / 628318530717958647692) :=
    mul_le_mul_of_nonneg_left ropeStandardChannel0_piD20_base_upper (by norm_num)
  rw [abs_lt]
  constructor
  · have hgap_lower :
        (16551 : ℝ) - (1 : ℝ) / 328458 <
          (103993 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647694) := by
      norm_num
    linarith
  · have hgap_upper :
        (103993 : ℝ) *
            ((100000000000000000000 : ℝ) / 628318530717958647692) <
          (16551 : ℝ) + (1 : ℝ) / 328458 := by
      norm_num
    linarith

/-- No standard channel-0 finite-context margin at or above `1/328458` is
possible once the inspected context contains gap `103993`. -/
theorem not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993
    {context : Nat} {margin : ℝ} (hcontext : 103993 < context)
    (hmargin : (1 : ℝ) / 328458 ≤ margin) :
    ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin context := by
  exact
    not_ropeTurnRatioFiniteMargin_of_error_lt_margin
      (turnRatio := ropeStandardChannel0TurnRatio)
      (margin := margin)
      (context := context) (gap := 103993) (turns := 16551)
      (by norm_num) hcontext
      (lt_of_lt_of_le
        ropeStandardChannel0_gap103993_error_lt_one_over_328458 hmargin)

/-- The current standard channel-0 4k seed brackets the advertised finite margin:
`1/104219` is proved, while every margin at or above `1/104218` is impossible. -/
theorem ropeStandardChannel0D11_context4096_margin_bracket :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104219) 4096 ∧
    ∀ margin : ℝ, (1 : ℝ) / 104218 ≤ margin →
      ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin 4096 := by
  constructor
  · simpa [ropeStandardChannel0D11SeedMargin, ropeStandardChannel0D11SeedContext]
      using ropeStandardChannel0D11Seed_turnRatioFiniteMargin
  · intro margin hmargin
    exact
      not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710
        (context := 4096) (margin := margin) (by norm_num) hmargin

/-- The current standard channel-0 8k seed brackets the advertised finite margin:
`1/104220` is proved, while every margin at or above `1/104218` is impossible.

This keeps the longer D12 seed honest: it extends the context horizon by
lowering the advertised margin, and the same concrete gap-`710` obstruction
still prevents the nearby stronger margins for the longer context. -/
theorem ropeStandardChannel0D12_context8192_margin_bracket :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104220) 8192 ∧
    ∀ margin : ℝ, (1 : ℝ) / 104218 ≤ margin →
      ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin 8192 := by
  constructor
  · simpa [ropeStandardChannel0D12SeedMargin, ropeStandardChannel0D12SeedContext]
      using ropeStandardChannel0D12Seed_turnRatioFiniteMargin
  · intro margin hmargin
    exact
      not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710
        (context := 8192) (margin := margin) (by norm_num) hmargin

/-- The sharpened standard channel-0 8k seed brackets the advertised finite
margin: `1/104219` is proved, while every margin at or above `1/104218` is
impossible. -/
theorem ropeStandardChannel0D13_context8192_margin_bracket :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104219) 8192 ∧
    ∀ margin : ℝ, (1 : ℝ) / 104218 ≤ margin →
      ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin 8192 := by
  constructor
  · simpa [ropeStandardChannel0D13SeedMargin, ropeStandardChannel0D13SeedContext]
      using ropeStandardChannel0D13Seed_turnRatioFiniteMargin
  · intro margin hmargin
    exact
      not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710
        (context := 8192) (margin := margin) (by norm_num) hmargin

/-- The standard channel-0 16k seed brackets the advertised finite margin:
`1/104219` is proved, while every margin at or above `1/104218` is impossible. -/
theorem ropeStandardChannel0D14_context16384_margin_bracket :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ((1 : ℝ) / 104219) 16384 ∧
    ∀ margin : ℝ, (1 : ℝ) / 104218 ≤ margin →
      ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin 16384 := by
  constructor
  · simpa [ropeStandardChannel0D14SeedMargin, ropeStandardChannel0D14SeedContext]
      using ropeStandardChannel0D14Seed_turnRatioFiniteMargin
  · intro margin hmargin
    exact
      not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710
        (context := 16384) (margin := margin) (by norm_num) hmargin

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

/-- A finite-context margin certificate plus one obstruction gap gives a
range bracket.

The pass side is context monotonicity: a proved margin at `certifiedContext`
holds for every smaller requested context. The fail side is the obstruction:
once a requested context contains a positive gap whose turn-ratio error is
below `obstructionMargin`, no advertised margin at or above that obstruction
margin can hold. This is the reusable theorem shape behind frontier reports
such as the standard channel-0 D19 range bracket. -/
theorem ropeTurnRatioFiniteMargin_contextRange_bracket_of_obstruction
    {turnRatio provedMargin obstructionMargin : ℝ}
    {certifiedContext obstructionGap : Nat} {obstructionTurns : Int}
    (hproved : ropeTurnRatioFiniteMargin turnRatio provedMargin certifiedContext)
    (hobstruction_gap_pos : 0 < obstructionGap)
    (hobstruction_error :
      ropeTurnRatioError turnRatio obstructionGap obstructionTurns < obstructionMargin) :
    ∀ {context : Nat}, obstructionGap < context → context ≤ certifiedContext →
      ropeTurnRatioFiniteMargin turnRatio provedMargin context ∧
        ∀ margin : ℝ, obstructionMargin ≤ margin →
          ¬ ropeTurnRatioFiniteMargin turnRatio margin context := by
  intro context hcontext_min hcontext_max
  constructor
  · exact ropeTurnRatioFiniteMargin_mono_context hcontext_max hproved
  · intro margin hmargin
    exact
      not_ropeTurnRatioFiniteMargin_of_error_lt_margin
        (turnRatio := turnRatio) (margin := margin) (context := context)
        (gap := obstructionGap) (turns := obstructionTurns)
        hobstruction_gap_pos hcontext_min
        (lt_of_lt_of_le hobstruction_error hmargin)

/-- A finite-context margin certificate plus one obstruction gap gives a
request-level range bracket.

This is the certifier-facing version of
`ropeTurnRatioFiniteMargin_contextRange_bracket_of_obstruction`: if the
requested context is inside the certified horizon and the requested margin is
no larger than the proved margin, the requested margin holds. If the requested
context also contains the obstruction gap, every advertised margin at or above
the obstruction threshold is impossible. -/
theorem ropeTurnRatioFiniteMargin_contextRange_request_bracket_of_obstruction
    {turnRatio provedMargin obstructionMargin requestedMargin : ℝ}
    {certifiedContext obstructionGap context : Nat} {obstructionTurns : Int}
    (hproved : ropeTurnRatioFiniteMargin turnRatio provedMargin certifiedContext)
    (hobstruction_gap_pos : 0 < obstructionGap)
    (hobstruction_error :
      ropeTurnRatioError turnRatio obstructionGap obstructionTurns < obstructionMargin)
    (hcontext_min : obstructionGap < context)
    (hcontext_max : context ≤ certifiedContext) :
    (requestedMargin ≤ provedMargin →
      ropeTurnRatioFiniteMargin turnRatio requestedMargin context) ∧
      (obstructionMargin ≤ requestedMargin →
        ¬ ropeTurnRatioFiniteMargin turnRatio requestedMargin context) := by
  have hbracket :=
    ropeTurnRatioFiniteMargin_contextRange_bracket_of_obstruction
      (turnRatio := turnRatio) (provedMargin := provedMargin)
      (obstructionMargin := obstructionMargin)
      (certifiedContext := certifiedContext)
      (obstructionGap := obstructionGap)
      (obstructionTurns := obstructionTurns)
      hproved hobstruction_gap_pos hobstruction_error hcontext_min hcontext_max
  constructor
  · intro hmargin_le
    exact ropeTurnRatioFiniteMargin_mono_margin hmargin_le hbracket.1
  · intro hmargin
    exact hbracket.2 requestedMargin hmargin

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

/-- A one-channel finite turn-ratio margin is equivalent to ruling out every
in-context real near-turn event below the corresponding scaled tolerance.

The forward direction is the certifier consequence theorem. The reverse
direction says the contract is not merely sufficient: if some positive
in-context gap is below the advertised turn-ratio margin, that same gap gives a
real near-turn witness at a tolerance strictly below `fullTurn * margin`. -/
theorem ropeTurnRatioFiniteMargin_iff_no_nearTurn_below_scaled_margin
    {frequency fullTurn margin : ℝ} {context : Nat}
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn) :
    ropeTurnRatioFiniteMargin (frequency / fullTurn) margin context ↔
      ∀ tolerance : ℝ, tolerance < fullTurn * margin →
        ∀ left right : Nat, left < right → right < context →
          ¬ ropeRealPhaseNearTurn frequency fullTurn tolerance left right := by
  constructor
  · intro hmargin tolerance htolerance left right hleft hright
    exact
      not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
        (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
        (tolerance := tolerance) (context := context) (left := left) (right := right)
        hleft hright hfrequency_nonneg hfull_pos hmargin htolerance
  · intro hnoNear
    by_contra hnotMargin
    rcases
        (not_ropeTurnRatioFiniteMargin_iff_exists_error_lt_margin
          (turnRatio := frequency / fullTurn) (margin := margin) (context := context)).1
          hnotMargin with
      ⟨gap, hgap_pos, hgap_context, turns, herror_lt_margin⟩
    let tolerance : ℝ := fullTurn * ropeTurnRatioError (frequency / fullTurn) gap turns
    have htolerance : tolerance < fullTurn * margin := by
      dsimp [tolerance]
      exact mul_lt_mul_of_pos_left herror_lt_margin hfull_pos
    have hscaled :
        ropeRealPhaseIntTurnError frequency fullTurn 0 gap turns =
          fullTurn * ropeTurnRatioError (frequency / fullTurn) gap turns := by
      simpa [ropeTurnRatioError] using
        (ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError
          (frequency := frequency) (fullTurn := fullTurn)
          (left := 0) (right := gap) (turns := turns)
          (Nat.zero_le gap) hfrequency_nonneg hfull_pos)
    have hnear :
        ropeRealPhaseNearTurn frequency fullTurn tolerance 0 gap := by
      refine ⟨turns, ?_⟩
      dsimp [tolerance]
      rw [hscaled]
    exact
      (hnoNear tolerance htolerance 0 gap hgap_pos hgap_context) hnear

/-- A finite nearest-integer certificate is equivalent to the one-channel
no-near-turn contract below the corresponding scaled margin.

This is the report-facing certificate bridge: a Python or Living Book report
can cite a finite nearest-integer certificate object, and this theorem states
exactly the real-phase no-near-turn property that the object certifies. -/
theorem ropeTurnRatioFiniteMarginCertificate_iff_no_nearTurn_below_scaled_margin
    {frequency fullTurn margin : ℝ} {context : Nat}
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn) :
    RopeTurnRatioFiniteMarginCertificate (frequency / fullTurn) margin context ↔
      ∀ tolerance : ℝ, tolerance < fullTurn * margin →
        ∀ left right : Nat, left < right → right < context →
          ¬ ropeRealPhaseNearTurn frequency fullTurn tolerance left right := by
  rw [ropeTurnRatioFiniteMarginCertificate_iff_finiteMargin]
  exact
    ropeTurnRatioFiniteMargin_iff_no_nearTurn_below_scaled_margin
      (frequency := frequency) (fullTurn := fullTurn) (margin := margin)
      (context := context) hfrequency_nonneg hfull_pos

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

/-- The next sharper standard-RoPE channel-0 interval seed rules out
one-channel near-turn collisions below its certified margin over context `8`. -/
theorem not_ropeStandardChannel0D3Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D3SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D3SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D3SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D3SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D3Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D3SeedMargin] using htolerance)

/-- The larger standard-RoPE channel-0 interval seed rules out one-channel
near-turn collisions below its certified margin over context `19`. -/
theorem not_ropeStandardChannel0D4Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D4SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D4SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D4SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D4SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D4Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D4SeedMargin] using htolerance)

/-- The smaller-margin standard-RoPE channel-0 interval seed rules out
one-channel near-turn collisions below margin `1/64` over context `44`. -/
theorem not_ropeStandardChannel0D5Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D5SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D5SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D5SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D5SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D5Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D5SeedMargin] using htolerance)

/-- The sharper standard-RoPE channel-0 interval seed rules out one-channel
near-turn collisions below margin `1/512` over context `57`. -/
theorem not_ropeStandardChannel0D6Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D6SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D6SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D6SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D6SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D6Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D6SeedMargin] using htolerance)

/-- The generated-band standard-RoPE channel-0 interval seed rules out
one-channel near-turn collisions below margin `1/512` over context `333`. -/
theorem not_ropeStandardChannel0D7Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D7SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D7SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D7SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D7SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D7Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D7SeedMargin] using htolerance)

/-- The six-decimal generated-band standard-RoPE channel-0 interval seed rules
out one-channel near-turn collisions below margin `1/1024` over context `710`. -/
theorem not_ropeStandardChannel0D8Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D8SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D8SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D8SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D8SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D8Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D8SeedMargin] using htolerance)

/-- The 20-decimal generated-band standard-RoPE channel-0 interval seed rules
out one-channel near-turn collisions below margin `1/131072` over context
`4096`. -/
theorem not_ropeStandardChannel0D9Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D9SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D9SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D9SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D9SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D9Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D9SeedMargin] using htolerance)

/-- The tighter 20-decimal generated-band standard-RoPE channel-0 interval seed
rules out one-channel near-turn collisions below margin `1/105000` over context
`4096`. -/
theorem not_ropeStandardChannel0D10Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D10SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D10SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D10SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D10SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D10Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D10SeedMargin] using htolerance)

/-- The sharpest current 20-decimal generated-band standard-RoPE channel-0
interval seed rules out one-channel near-turn collisions below margin
`1/104219` over context `4096`. -/
theorem not_ropeStandardChannel0D11Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D11SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D11SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D11SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D11SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D11Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D11SeedMargin] using htolerance)

/-- The 8k 20-decimal generated-band standard-RoPE channel-0 interval seed
rules out one-channel near-turn collisions below margin `1/104220` over context
`8192`. -/
theorem not_ropeStandardChannel0D12Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D12SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D12SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D12SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D12SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D12Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D12SeedMargin] using htolerance)

/-- The sharpened 8k 20-decimal generated-band standard-RoPE channel-0 interval
seed rules out one-channel near-turn collisions below margin `1/104219` over
context `8192`. -/
theorem not_ropeStandardChannel0D13Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D13SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D13SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D13SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D13SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D13Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D13SeedMargin] using htolerance)

/-- The 16k 20-decimal generated-band standard-RoPE channel-0 interval seed
rules out one-channel near-turn collisions below margin `1/104219`. -/
theorem not_ropeStandardChannel0D14Seed_nearTurn
    {tolerance : ℝ} {left right : Nat}
    (hleft : left < right) (hright : right < ropeStandardChannel0D14SeedContext)
    (htolerance : tolerance < ropeStandardChannel0D14SeedMargin) :
    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by
  exact
    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin
      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)
      (margin := ropeStandardChannel0D14SeedMargin) (tolerance := tolerance)
      (context := ropeStandardChannel0D14SeedContext) (left := left) (right := right)
      hleft hright
      (by
        dsimp [ropeStandardChannel0TurnRatio]
        positivity)
      (by norm_num)
      (by simpa using ropeStandardChannel0D14Seed_turnRatioFiniteMargin)
      (by simpa [ropeStandardChannel0D14SeedMargin] using htolerance)

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

/-- A finite nearest-integer certificate for one channel can be reused as a
bank-level no-near-turn certificate for any smaller requested context and
advertised margin.

This is the finite-certificate version of the one-separating-channel bank
bridge: if a frequency bank contains a channel with a proof-carrying
nearest-integer certificate, then an all-channel near-turn event is impossible
below the scaled requested margin. -/
theorem not_ropeRealPhaseBankNearTurn_of_one_channel_finiteMarginCertificate_le_context_margin
    {frequencies : List ℝ} {frequency fullTurn requestedMargin certifiedMargin tolerance : ℝ}
    {requestedContext certifiedContext left right : Nat}
    (hcontext : requestedContext ≤ certifiedContext)
    (hmargin_le : requestedMargin ≤ certifiedMargin)
    (hmem : frequency ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfrequency_nonneg : 0 ≤ frequency) (hfull_pos : 0 < fullTurn)
    (certificate :
      RopeTurnRatioFiniteMarginCertificate
        (frequency / fullTurn) certifiedMargin certifiedContext)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right :=
  not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
    (frequencies := frequencies) (frequency := frequency) (fullTurn := fullTurn)
    (requestedMargin := requestedMargin) (certifiedMargin := certifiedMargin)
    (tolerance := tolerance) (requestedContext := requestedContext)
    (certifiedContext := certifiedContext) (left := left) (right := right)
    hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos
    certificate.certifies htolerance

/-- The context-`4096` standard channel-0 interval seed can be used as a
bank-level no-near-turn certificate whenever that channel frequency is present.

This is not a full standard-RoPE bank theorem. It is the named certifier-facing
bridge from the one-channel D9 interval certificate to the existing bank
predicate: one separating channel is enough to rule out a simultaneous all-bank
near-turn event below any downgraded requested margin and context. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D9Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D9SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D9SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D9SeedMargin ropeStandardChannel0D9SeedContext := by
    simpa [hratio] using ropeStandardChannel0D9Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D9SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D9SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- The tighter context-`4096` standard channel-0 interval seed can be used as
a bank-level no-near-turn certificate whenever that channel frequency is
present.

This is the D10 version of the certifier-facing transfer: one separating
standard channel rules out a simultaneous all-bank near-turn event below any
downgraded requested margin and context. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D10Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D10SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D10SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D10SeedMargin ropeStandardChannel0D10SeedContext := by
    simpa [hratio] using ropeStandardChannel0D10Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D10SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D10SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- The sharpest current context-`4096` standard channel-0 interval seed can be
used as a bank-level no-near-turn certificate whenever that channel frequency
is present.

This is the D11 version of the certifier-facing transfer: it advertises the
tighter `1/104219` seed while preserving the same conservative one-channel
claim boundary as D9 and D10. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D11SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D11SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D11SeedMargin ropeStandardChannel0D11SeedContext := by
    simpa [hratio] using ropeStandardChannel0D11Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D11SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D11SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- Any finite real-phase bank whose first channel is the standard channel-0
frequency inherits the D11 no-near-turn certificate.

This removes the explicit membership premise from the certifier-facing D11
bridge for the common "standard channel plus additional channels" bank shape.
It is still a one-separating-channel certificate: the theorem uses channel 0
to rule out simultaneous all-bank near-turn events, and it does not prove
independent margins for every extra channel. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed_cons
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D11SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D11SeedMargin)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn
      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      fullTurn tolerance left right := by
  exact
    not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed
      (frequencies := (ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (left := left) (right := right)
      hcontext hmargin_le (by simp) hleft hright hfull_pos htolerance

/-- The context-`8192` standard channel-0 interval seed can be used as a
bank-level no-near-turn certificate whenever that channel frequency is
present.

This is the D12 version of the certifier-facing transfer. It lowers the
advertised margin to `1/104220` and extends the reusable one-separating-channel
bank contract to the longer `8192` seed context. It still does not prove
independent margins for the other standard RoPE channels. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D12SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D12SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D12SeedMargin ropeStandardChannel0D12SeedContext := by
    simpa [hratio] using ropeStandardChannel0D12Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D12SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D12SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- Any finite real-phase bank whose first channel is the standard channel-0
frequency inherits the D12 no-near-turn certificate.

This removes the explicit membership premise from the D12 bridge for the common
"standard channel plus additional channels" bank shape. It remains a
one-separating-channel certificate, not a full all-channel margin theorem. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D12SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D12SeedMargin)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn
      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      fullTurn tolerance left right := by
  exact
    not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed
      (frequencies := (ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (left := left) (right := right)
      hcontext hmargin_le (by simp) hleft hright hfull_pos htolerance

/-- The sharpened context-`8192` standard channel-0 interval seed can be used
as a bank-level no-near-turn certificate whenever that channel frequency is
present.

This is the D13 version of the certifier-facing transfer. It keeps the longer
`8192` seed context while raising the certified margin back to `1/104219`.
It remains a one-separating-channel certificate, not an all-channel margin
theorem. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D13SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D13SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D13SeedMargin ropeStandardChannel0D13SeedContext := by
    simpa [hratio] using ropeStandardChannel0D13Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D13SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D13SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- Any finite real-phase bank whose first channel is the standard channel-0
frequency inherits the sharpened D13 no-near-turn certificate. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D13SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D13SeedMargin)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn
      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      fullTurn tolerance left right := by
  exact
    not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed
      (frequencies := (ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (left := left) (right := right)
      hcontext hmargin_le (by simp) hleft hright hfull_pos htolerance

/-- The context-`16384` standard channel-0 interval seed can be used as a
bank-level no-near-turn certificate whenever that channel frequency is present.

This is the D14 version of the certifier-facing transfer. It extends the
certified context while keeping the D13 margin. It remains a
one-separating-channel certificate, not an all-channel margin theorem. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed
    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D14SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D14SeedMargin)
    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by
  have hratio :
      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =
        ropeStandardChannel0TurnRatio := by
    field_simp [hfull_pos.ne']
  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by
    dsimp [ropeStandardChannel0TurnRatio]
    positivity
  have hmargin :
      ropeTurnRatioFiniteMargin
        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)
        ropeStandardChannel0D14SeedMargin ropeStandardChannel0D14SeedContext := by
    simpa [hratio] using ropeStandardChannel0D14Seed_turnRatioFiniteMargin
  exact
    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin
      (frequencies := frequencies)
      (frequency := ropeStandardChannel0TurnRatio * fullTurn)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (certifiedMargin := ropeStandardChannel0D14SeedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (certifiedContext := ropeStandardChannel0D14SeedContext)
      (left := left) (right := right)
      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin
      htolerance

/-- Any finite real-phase bank whose first channel is the standard channel-0
frequency inherits the D14 no-near-turn certificate. -/
theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D14SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D14SeedMargin)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn
      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      fullTurn tolerance left right := by
  exact
    not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed
      (frequencies := (ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      (fullTurn := fullTurn)
      (requestedMargin := requestedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (left := left) (right := right)
      hcontext hmargin_le (by simp) hleft hright hfull_pos htolerance

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
