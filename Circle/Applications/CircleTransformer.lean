import Circle.Core.Period
import Circle.Core.Rotation
import Mathlib.Tactic.Ring

/-!
# Proved structural guarantees for a circle-structured transformer

This file states the **structural** facts a finite-circle transformer can rely on, as
Lean theorems. These are guarantees about *architecture* (which positions a sparse head
can reach, how relative position behaves), not claims about model quality — those require
experiments and are deliberately out of scope here.

Two components are covered:

## Strided ("coil") sparse attention — coverage

A strided attention head with stride `k` on a context of length `n` lets a token attend to
positions `i, i±k, i±2k, …` — exactly a coil orbit on `C n`. The reachability of such a
head is therefore governed by the finite-circle period/orbit theory:

* `attentionReach_eq_div_gcd` — one strided head reaches exactly `n / gcd(n,k)` distinct
  positions;
* `stridedHead_fullCoverage_iff_coprime` — it reaches **every** position iff `gcd(n,k)=1`.

This is a real design rule (the kind practitioners reason about for sparse/dilated
attention), and it is a genuine, non-trivial consequence of the orbit spine
(`Circle.period_eq_n_div_gcd`), not relabeled modular arithmetic.

## Rotary position encoding (RoPE) — relative position

RoPE encodes position `p` as a rotation by `p` (here, in `C n`). The defining property of
RoPE — that the interaction between a query at position `m` and a key at position `k`
depends only on the relative position `m − k` — is the rotation/translation law:

* `rope_relative_shift_invariant` — shifting both positions by any `d` leaves the relative
  phase unchanged;
* `rope_compose` — rotations compose additively (RoPE phase additivity), reusing
  `Circle.rot_comp`.

Out of scope (empirical, not claimed here): that any of this improves accuracy, efficiency,
or extrapolation. Those are experiments, not theorems.
-/

namespace Circle.Applications

open Circle

/-! ### Strided "coil" attention coverage -/

/-- The number of distinct positions a stride-`k` attention head reaches on a length-`n`
context: the size of its coil orbit, i.e. the finite-circle period. -/
noncomputable def attentionReach (n k : Nat) : Nat := Circle.period n k

/-- A stride-`k` head reaches exactly `n / gcd(n,k)` distinct positions. -/
theorem attentionReach_eq_div_gcd {n k : Nat} (hn : n ≠ 0) :
    attentionReach n k = n / Nat.gcd n k :=
  Circle.period_eq_n_div_gcd hn

/-- A stride-`k` head achieves *full coverage* when it reaches all `n` positions. -/
def stridedHeadFullCoverage (n k : Nat) : Prop := attentionReach n k = n

/-- **Coverage rule.** A single strided attention head reaches every position of a
length-`n` context iff its stride is coprime to `n`. -/
theorem stridedHead_fullCoverage_iff_coprime {n k : Nat} (hn : n ≠ 0) :
    stridedHeadFullCoverage n k ↔ Nat.gcd n k = 1 := by
  unfold stridedHeadFullCoverage
  rw [attentionReach_eq_div_gcd hn, Nat.div_eq_self]
  simp [hn]

/-- A coprime stride guarantees full coverage. -/
theorem stridedHead_fullCoverage_of_coprime {n k : Nat} (hn : n ≠ 0)
    (hk : Nat.gcd n k = 1) : stridedHeadFullCoverage n k :=
  (stridedHead_fullCoverage_iff_coprime hn).2 hk

/-! ### RoPE relative position -/

/-- The RoPE phase of a token at position `pos`: rotation by `pos` from the base node. -/
def ropePhase (n pos : Nat) : C n := Circle.rot n pos 0

@[simp] theorem ropePhase_eq (n pos : Nat) : ropePhase n pos = (pos : C n) := by
  simp [ropePhase, Circle.rot]

/-- The relative RoPE phase between a query at position `query` and a key at position
`key`. -/
def ropeRelative (n query key : Nat) : C n := ropePhase n query - ropePhase n key

/-- **Relative-position property.** Shifting both the query and key positions by the same
amount `d` leaves the relative RoPE phase unchanged: RoPE interaction depends only on the
relative position `query − key`. -/
theorem rope_relative_shift_invariant (n query key d : Nat) :
    ropeRelative n (query + d) (key + d) = ropeRelative n query key := by
  unfold ropeRelative
  simp only [ropePhase_eq]
  push_cast
  ring

/-- **RoPE phase additivity.** Rotations compose by adding strides — the algebraic basis
of RoPE's relative-position behaviour. (Reuses `Circle.rot_comp`.) -/
theorem rope_compose (n a b : Nat) (x : C n) :
    Circle.rot n a (Circle.rot n b x) = Circle.rot n (a + b) x :=
  Circle.rot_comp n a b x

end Circle.Applications
