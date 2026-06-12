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
* `hybridLagReach_of_local` / `hybridLagReach_of_coil` — a local+coil sparse head reaches
  a dependency lag whenever either the local window or the coil path reaches it.

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

/-! ### Local+coil hybrid sparse attention -/

/-- A local sliding-window head reaches a positive dependency lag if the lag is inside
the window width. -/
def localLagReach (window lag : Nat) : Prop := 1 ≤ lag ∧ lag ≤ window

/-- The local window covers every positive dependency lag inside a length-`n`
context. -/
def localWindowCoversContext (n window : Nat) : Prop :=
  ∀ lag, 1 ≤ lag → lag < n → localLagReach window lag

/-- A finite coil path reaches a dependency lag when some nonzero step within the path
has the same cyclic lag modulo the context length. -/
def coilLagReach (n stride pathLength lag : Nat) : Prop :=
  ∃ step, 1 ≤ step ∧ step ≤ pathLength ∧ (step * stride) % n = lag % n

/-- A hybrid local+coil sparse head reaches a lag if either the local window or the coil
path reaches it. -/
def hybridLagReach (n window stride pathLength lag : Nat) : Prop :=
  localLagReach window lag ∨ coilLagReach n stride pathLength lag

/-- A finite family of coil strides reaches a dependency lag when one admitted stride
reaches that lag within the shared path length. This is the proof-side model of a
multi-head sparse attention plan where each head owns one stride. -/
def coilStrideFamilyLagReach (n pathLength lag : Nat) (strides : List Nat) : Prop :=
  ∃ stride, stride ∈ strides ∧ coilLagReach n stride pathLength lag

/-- A local-window plus finite stride-family sparse plan reaches a lag when either the
local window reaches it or one admitted coil stride reaches it. -/
def hybridFamilyLagReach (n window pathLength lag : Nat) (strides : List Nat) : Prop :=
  localLagReach window lag ∨ coilStrideFamilyLagReach n pathLength lag strides

/-- The local reachability predicate is exactly the positive in-window lag condition. -/
theorem localLagReach_of_le {window lag : Nat} (hpos : 1 ≤ lag) (hwindow : lag ≤ window) :
    localLagReach window lag :=
  ⟨hpos, hwindow⟩

/-- A coil path reaches the exact lag generated by any admitted step. -/
theorem coilLagReach_of_step {n stride pathLength step : Nat}
    (hpos : 1 ≤ step) (hstep : step ≤ pathLength) :
    coilLagReach n stride pathLength (step * stride) := by
  unfold coilLagReach
  exact ⟨step, hpos, hstep, rfl⟩

/-- Coil lag reachability is invariant under adding one full context length to the target
lag. This is the cyclic-alias bookkeeping a sparse attention harness must expose. -/
theorem coilLagReach_add_context {n stride pathLength lag : Nat}
    (hreach : coilLagReach n stride pathLength lag) :
    coilLagReach n stride pathLength (lag + n) := by
  rcases hreach with ⟨step, hpos, hstep, hmod⟩
  unfold coilLagReach
  refine ⟨step, hpos, hstep, ?_⟩
  rw [Nat.add_mod, Nat.mod_self, Nat.add_zero, Nat.mod_mod]
  exact hmod

/-- A stride family reaches every exact lag generated by an admitted stride and step. -/
theorem coilStrideFamilyLagReach_of_member_step
    {n pathLength stride step : Nat} {strides : List Nat}
    (hmem : stride ∈ strides) (hpos : 1 ≤ step) (hstep : step ≤ pathLength) :
    coilStrideFamilyLagReach n pathLength (step * stride) strides := by
  unfold coilStrideFamilyLagReach
  exact ⟨stride, hmem, coilLagReach_of_step hpos hstep⟩

/-- Stride-family lag reachability is invariant under adding one full context length to
the target lag, inheriting the cyclic alias law from each admitted coil path. -/
theorem coilStrideFamilyLagReach_add_context
    {n pathLength lag : Nat} {strides : List Nat}
    (hreach : coilStrideFamilyLagReach n pathLength lag strides) :
    coilStrideFamilyLagReach n pathLength (lag + n) strides := by
  rcases hreach with ⟨stride, hmem, hcoil⟩
  unfold coilStrideFamilyLagReach
  exact ⟨stride, hmem, coilLagReach_add_context hcoil⟩

/-- A hybrid sparse head reaches every lag already reached by its local window. -/
theorem hybridLagReach_of_local {n window stride pathLength lag : Nat}
    (hlocal : localLagReach window lag) :
    hybridLagReach n window stride pathLength lag :=
  Or.inl hlocal

/-- A hybrid sparse head reaches every lag already reached by its coil path. -/
theorem hybridLagReach_of_coil {n window stride pathLength lag : Nat}
    (hcoil : coilLagReach n stride pathLength lag) :
    hybridLagReach n window stride pathLength lag :=
  Or.inr hcoil

/-- A local+stride-family sparse plan reaches every lag already reached by its local
window. -/
theorem hybridFamilyLagReach_of_local
    {n window pathLength lag : Nat} {strides : List Nat}
    (hlocal : localLagReach window lag) :
    hybridFamilyLagReach n window pathLength lag strides :=
  Or.inl hlocal

/-- A local+stride-family sparse plan reaches every lag already reached by one admitted
coil stride. -/
theorem hybridFamilyLagReach_of_family
    {n window pathLength lag : Nat} {strides : List Nat}
    (hfamily : coilStrideFamilyLagReach n pathLength lag strides) :
    hybridFamilyLagReach n window pathLength lag strides :=
  Or.inr hfamily

/-- If a stride belongs to the sparse-head family, then every admitted step along that
stride is reachable by the local+family plan. -/
theorem hybridFamilyLagReach_of_member_step
    {n window pathLength stride step : Nat} {strides : List Nat}
    (hmem : stride ∈ strides) (hpos : 1 ≤ step) (hstep : step ≤ pathLength) :
    hybridFamilyLagReach n window pathLength (step * stride) strides :=
  hybridFamilyLagReach_of_family
    (coilStrideFamilyLagReach_of_member_step hmem hpos hstep)

/-- A local+stride-family sparse plan misses a lag exactly when neither the
local window nor any admitted stride-family coil path reaches it. This is the
gap-certificate form of the sparse-attention reachability contract. -/
theorem hybridFamilyLagGap_iff_not_local_and_not_family
    {n window pathLength lag : Nat} {strides : List Nat} :
    ¬ hybridFamilyLagReach n window pathLength lag strides ↔
      ¬ localLagReach window lag ∧
        ¬ coilStrideFamilyLagReach n pathLength lag strides := by
  unfold hybridFamilyLagReach
  constructor
  · intro hgap
    exact ⟨fun hlocal => hgap (Or.inl hlocal),
      fun hfamily => hgap (Or.inr hfamily)⟩
  · rintro ⟨hnotlocal, hnotfamily⟩ hreach
    cases hreach with
    | inl hlocal => exact hnotlocal hlocal
    | inr hfamily => exact hnotfamily hfamily

/-- Concrete stride-family gap certificate.

If a lag is beyond the local window and every admitted stride/step pair has a
different cyclic lag, then the local+stride-family plan misses that lag. This
is the form emitted by executable sparse-attention coverage certificates:
uncovered lags are not merely absent from a Python list; they satisfy a
checkable local-window and stride-step exclusion condition. -/
theorem hybridFamilyLagGap_of_above_window_and_forall_stride_step_ne
    {n window pathLength lag : Nat} {strides : List Nat}
    (habove : window < lag)
    (hnoStride :
      ∀ stride, stride ∈ strides → ∀ step, 1 ≤ step → step ≤ pathLength →
        (step * stride) % n ≠ lag % n) :
    ¬ hybridFamilyLagReach n window pathLength lag strides := by
  rw [hybridFamilyLagGap_iff_not_local_and_not_family]
  constructor
  · intro hlocal
    exact (not_le_of_gt habove) hlocal.2
  · intro hfamily
    rcases hfamily with ⟨stride, hmem, step, hpos, hstep, hmod⟩
    exact hnoStride stride hmem step hpos hstep hmod

/-- Local-window full-coverage sufficient condition.

If the local window is at least `n - 1`, then every positive lag inside a
length-`n` context is reached by the local part of any local+stride-family
plan. This is the simple complete-coverage certificate for the dense-local
limit of the sparse-attention model. -/
theorem hybridFamilyLagReach_of_localWindow_ge_context_sub_one
    {n window pathLength lag : Nat} {strides : List Nat}
    (hpos : 1 ≤ lag) (hcontext : lag < n) (hwindow : n - 1 ≤ window) :
    hybridFamilyLagReach n window pathLength lag strides :=
  hybridFamilyLagReach_of_local
    (localLagReach_of_le hpos (le_trans (Nat.le_sub_one_of_lt hcontext) hwindow))

/-- Exact local-window coverage criterion.

The local window covers every positive lag inside a length-`n` context iff it
reaches the largest possible positive lag, `n - 1`. This is the converse side
of the dense-local sparse-attention certificate. -/
theorem localWindowCoversContext_iff_context_sub_one_le
    {n window : Nat} :
    localWindowCoversContext n window ↔ n - 1 ≤ window := by
  constructor
  · intro hcover
    cases n with
    | zero =>
        exact Nat.zero_le window
    | succ m =>
        by_cases hm : m = 0
        · simp [hm]
        · have hpos : 1 ≤ m := Nat.succ_le_of_lt (Nat.pos_of_ne_zero hm)
          exact (hcover m hpos (Nat.lt_succ_self m)).2
  · intro hwindow lag hpos hcontext
    exact localLagReach_of_le hpos (le_trans (Nat.le_sub_one_of_lt hcontext) hwindow)

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
