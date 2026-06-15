import Circle.Core.Period
import Circle.Core.Rotation
import Mathlib.Data.Finset.Card
import Mathlib.Data.List.Dedup
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

/-- A local-window plus finite stride-family sparse plan covers every positive
dependency lag inside a length-`n` context. -/
def hybridFamilyCoversContext
    (n window pathLength : Nat) (strides : List Nat) : Prop :=
  ∀ lag, 1 ≤ lag → lag < n → hybridFamilyLagReach n window pathLength lag strides

/-- Raw per-query candidate budget for a local-window plus stride-family plan,
before boundary clipping and duplicate removal.

The executable sparse-attention certificate reports this as an upper bound
beside the exact deduplicated candidate count. -/
def hybridFamilyRawCandidateBudget
    (window pathLength : Nat) (strides : List Nat) : Nat :=
  window + pathLength * strides.length

/-- A theorem-side upper bound for deduplicated per-query candidate count.

The raw budget counts every local and stride-family candidate before duplicate
removal; a deduplicated candidate set also cannot exceed the finite context
size. This bound records the useful minimum of those two caps without modeling
the executable list generator. -/
def hybridFamilyDedupCandidateBudgetBound
    (n window pathLength : Nat) (strides : List Nat) : Nat :=
  Nat.min n (hybridFamilyRawCandidateBudget window pathLength strides)

/-- Local lag candidates generated by the local-window component: `1, ..., window`. -/
def localLagCandidateList (window : Nat) : List Nat :=
  List.range' 1 window

/-- Residue lags generated by one stride over the admitted path steps. -/
def coilLagResidueList (n stride pathLength : Nat) : List Nat :=
  (List.range' 1 pathLength).map fun step => (step * stride) % n

/-- Residue lags generated by every stride in a finite stride family. -/
def coilStrideFamilyLagResidueList
    (n pathLength : Nat) : List Nat → List Nat
  | [] => []
  | stride :: strides =>
      coilLagResidueList n stride pathLength ++
        coilStrideFamilyLagResidueList n pathLength strides

/-- The exact theorem-side lag candidate list for a local+stride-family plan.

This list is the finite object whose deduplicated length is compared against
raw candidate budgets. It intentionally records lag/residue bookkeeping only;
query-indexed attention positions remain in the executable Python layer. -/
def hybridFamilyLagCandidateList
    (n window pathLength : Nat) (strides : List Nat) : List Nat :=
  localLagCandidateList window ++
    coilStrideFamilyLagResidueList n pathLength strides

/-- Finite list of positive in-context lags missing from a local+stride-family
sparse-attention plan.

This is the theorem-side object mirrored by executable sparse-attention
coverage certificates: a nonempty list is a concrete gap report, while an
empty list is complete context coverage. -/
def hybridFamilyUncoveredLagList
    (n window pathLength : Nat) (strides : List Nat) : List Nat :=
  (List.range' 1 (n - 1)).filter fun lag =>
    lag ∉ hybridFamilyLagCandidateList n window pathLength strides

/-- Extend a reversed list of consecutive lag intervals with one new lag.

The interval list is stored newest-first so `List.foldl` can update the current
run without traversing the accumulated prefix. -/
def extendConsecutiveLagIntervals :
    List (Nat × Nat) → Nat → List (Nat × Nat)
  | [], lag => [(lag, lag)]
  | (start, stop) :: rest, lag =>
      if lag = stop + 1 then (start, lag) :: rest
      else (lag, lag) :: (start, stop) :: rest

/-- Compress an ascending finite lag list into inclusive consecutive intervals. -/
def consecutiveLagIntervals (lags : List Nat) : List (Nat × Nat) :=
  (lags.foldl extendConsecutiveLagIntervals []).reverse

/-- Consecutive interval summary for the theorem-side uncovered-lag list.

This mirrors the compact interval field exposed by the executable sparse
attention certifier. The underlying semantic object remains
`hybridFamilyUncoveredLagList`; intervals are a readability layer over that
checked finite gap list. -/
def hybridFamilyUncoveredLagIntervalList
    (n window pathLength : Nat) (strides : List Nat) : List (Nat × Nat) :=
  consecutiveLagIntervals
    (hybridFamilyUncoveredLagList n window pathLength strides)

/-- First positive in-context lag missed by a local+stride-family sparse plan,
when the finite uncovered-lag list is nonempty.

Executable certifiers expose this as a compact witness field; the theorem-side
definition keeps that field tied to the checked uncovered-list object. -/
def hybridFamilyFirstUncoveredLag
    (n window pathLength : Nat) (strides : List Nat) : Option Nat :=
  (hybridFamilyUncoveredLagList n window pathLength strides).head?

/-- Finite list of positive in-context lags covered by a local+stride-family
sparse-attention plan.

This is the positive counterpart to `hybridFamilyUncoveredLagList`: executable
certifiers can report both covered and uncovered lags against theorem-side list
objects instead of treating the covered count as merely a Python filter. -/
def hybridFamilyCoveredLagList
    (n window pathLength : Nat) (strides : List Nat) : List Nat :=
  (List.range' 1 (n - 1)).filter fun lag =>
    lag ∈ hybridFamilyLagCandidateList n window pathLength strides

/-- Exact deduplicated lag-candidate count for the theorem-side candidate list. -/
def hybridFamilyUniqueLagCandidateCount
    (n window pathLength : Nat) (strides : List Nat) : Nat :=
  (hybridFamilyLagCandidateList n window pathLength strides).dedup.length

/-- Query-indexed predecessor position for a declared cyclic lag. -/
def predecessorIndex (n query lag : Nat) : Nat :=
  (query + n - (lag % n)) % n

/-- The query predecessor map is injective on in-context lag values.

If two lags are both strict representatives below the context length, then
equal query-indexed predecessor positions force the lags themselves to be
equal. -/
theorem predecessorIndex_injective_of_lag_lt_context
    {n query left right : Nat}
    (hleft : left < n)
    (hright : right < n)
    (heq : predecessorIndex n query left = predecessorIndex n query right) :
    left = right := by
  unfold predecessorIndex at heq
  have hmod :
      query + n - (left % n) ≡ query + n - (right % n) [MOD n] := by
    have hleftMod :
        query + n - (left % n) ≡
          (query + n - (left % n)) % n [MOD n] :=
      (Nat.mod_modEq (query + n - (left % n)) n).symm
    have hmiddle :
        (query + n - (left % n)) % n ≡
          (query + n - (right % n)) % n [MOD n] := by
      rw [heq]
    have hrightMod :
        (query + n - (right % n)) % n ≡
          query + n - (right % n) [MOD n] :=
      Nat.mod_modEq (query + n - (right % n)) n
    exact hleftMod.trans (hmiddle.trans hrightMod)
  have hmod' : query + n - left ≡ query + n - right [MOD n] := by
    simpa [Nat.mod_eq_of_lt hleft, Nat.mod_eq_of_lt hright] using hmod
  have hleftle : left ≤ query + n :=
    le_trans (Nat.le_of_lt hleft) (Nat.le_add_left n query)
  have hrightle : right ≤ query + n :=
    le_trans (Nat.le_of_lt hright) (Nat.le_add_left n query)
  have hsub := Nat.ModEq.sub_left
    (Nat.sub_le (query + n) left)
    (Nat.sub_le (query + n) right)
    hmod'
  have hlagMod : left ≡ right [MOD n] := by
    simpa [Nat.sub_sub_self hleftle, Nat.sub_sub_self hrightle] using hsub
  exact Nat.ModEq.eq_of_lt_of_lt hlagMod hleft hright

/-- Query-indexed raw predecessor candidates generated from the theorem-side
lag-candidate list. -/
def hybridFamilyQueryCandidateList
    (n query window pathLength : Nat) (strides : List Nat) : List Nat :=
  (hybridFamilyLagCandidateList n window pathLength strides).map
    (predecessorIndex n query)

/-- Exact deduplicated query-indexed candidate count for the theorem-side
candidate generator. -/
def hybridFamilyUniqueQueryCandidateCount
    (n query window pathLength : Nat) (strides : List Nat) : Nat :=
  (hybridFamilyQueryCandidateList n query window pathLength strides).dedup.length

/-- No-collision predicate for the theorem-side lag-candidate list. -/
def hybridFamilyLagCandidatesNoCollision
    (n window pathLength : Nat) (strides : List Nat) : Prop :=
  (hybridFamilyLagCandidateList n window pathLength strides).Nodup

/-- No-collision predicate for the theorem-side query-indexed candidate list. -/
def hybridFamilyQueryCandidatesNoCollision
    (n query window pathLength : Nat) (strides : List Nat) : Prop :=
  (hybridFamilyQueryCandidateList n query window pathLength strides).Nodup

/-- No-collision predicate for the stride-family residue block alone. -/
def coilStrideFamilyLagResiduesNoCollision
    (n pathLength : Nat) (strides : List Nat) : Prop :=
  (coilStrideFamilyLagResidueList n pathLength strides).Nodup

/-- Disjointness between raw local-window lags and stride-family residue lags. -/
def localCoilLagCandidatesDisjoint
    (n window pathLength : Nat) (strides : List Nat) : Prop :=
  (localLagCandidateList window).Disjoint
    (coilStrideFamilyLagResidueList n pathLength strides)

/-- Disjointness between one stride's residue block and the rest of a stride family. -/
def coilLagResiduesDisjointFromFamily
    (n stride pathLength : Nat) (strides : List Nat) : Prop :=
  (coilLagResidueList n stride pathLength).Disjoint
    (coilStrideFamilyLagResidueList n pathLength strides)

/-- A finite stride family is no-wrap separated when each head block stays
below the context length, every tail block does the same, and the head block's
largest possible value is below every tail stride. This is an ordered sufficient
condition for duplicate-free stride-family residue blocks. -/
def coilStrideFamilyNoWrapSeparated
    (n pathLength : Nat) : List Nat → Prop
  | [] => True
  | stride :: strides =>
      0 < stride ∧
        pathLength * stride < n ∧
        (∀ tailStride ∈ strides,
          0 < tailStride ∧
            pathLength * tailStride < n ∧
            pathLength * stride < tailStride) ∧
        coilStrideFamilyNoWrapSeparated n pathLength strides

/-- The query-predecessor map is injective on the generated lag candidates. -/
def hybridFamilyPredecessorInjectiveOnLagCandidates
    (n query window pathLength : Nat) (strides : List Nat) : Prop :=
  ∀ left, left ∈ hybridFamilyLagCandidateList n window pathLength strides →
    ∀ right, right ∈ hybridFamilyLagCandidateList n window pathLength strides →
      predecessorIndex n query left = predecessorIndex n query right → left = right

/-- The local reachability predicate is exactly the positive in-window lag condition. -/
theorem localLagReach_of_le {window lag : Nat} (hpos : 1 ≤ lag) (hwindow : lag ≤ window) :
    localLagReach window lag :=
  ⟨hpos, hwindow⟩

/-- For a positive lag, missing the local window is exactly being beyond the
window width. -/
theorem not_localLagReach_iff_window_lt_of_pos
    {window lag : Nat} (hpos : 1 ≤ lag) :
    ¬ localLagReach window lag ↔ window < lag := by
  constructor
  · intro hmiss
    exact Nat.lt_of_not_ge (fun hwindow => hmiss ⟨hpos, hwindow⟩)
  · intro habove hlocal
    exact (not_le_of_gt habove) hlocal.2

/-- Increasing the local window cannot remove a locally reachable lag. -/
theorem localLagReach_mono_window
    {smallWindow largeWindow lag : Nat}
    (hwindow : smallWindow ≤ largeWindow)
    (hreach : localLagReach smallWindow lag) :
    localLagReach largeWindow lag :=
  ⟨hreach.1, le_trans hreach.2 hwindow⟩

/-- A coil path reaches the exact lag generated by any admitted step. -/
theorem coilLagReach_of_step {n stride pathLength step : Nat}
    (hpos : 1 ≤ step) (hstep : step ≤ pathLength) :
    coilLagReach n stride pathLength (step * stride) := by
  unfold coilLagReach
  exact ⟨step, hpos, hstep, rfl⟩

/-- Increasing the admitted coil path length cannot remove a reachable lag. -/
theorem coilLagReach_mono_pathLength
    {n stride smallPath largePath lag : Nat}
    (hpath : smallPath ≤ largePath)
    (hreach : coilLagReach n stride smallPath lag) :
    coilLagReach n stride largePath lag := by
  rcases hreach with ⟨step, hpos, hstep, hmod⟩
  exact ⟨step, hpos, le_trans hstep hpath, hmod⟩

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

/-- Increasing the shared path length of a stride family cannot remove a
reachable lag. -/
theorem coilStrideFamilyLagReach_mono_pathLength
    {n smallPath largePath lag : Nat} {strides : List Nat}
    (hpath : smallPath ≤ largePath)
    (hreach : coilStrideFamilyLagReach n smallPath lag strides) :
    coilStrideFamilyLagReach n largePath lag strides := by
  rcases hreach with ⟨stride, hmem, hcoil⟩
  exact ⟨stride, hmem, coilLagReach_mono_pathLength hpath hcoil⟩

/-- Exact decomposition for adding one stride to a finite stride family. -/
theorem coilStrideFamilyLagReach_cons_iff
    {n pathLength lag stride : Nat} {strides : List Nat} :
    coilStrideFamilyLagReach n pathLength lag (stride :: strides) ↔
      coilLagReach n stride pathLength lag ∨
        coilStrideFamilyLagReach n pathLength lag strides := by
  unfold coilStrideFamilyLagReach
  constructor
  · rintro ⟨candidate, hmem, hreach⟩
    simp at hmem
    rcases hmem with hhead | htail
    · subst candidate
      exact Or.inl hreach
    · exact Or.inr ⟨candidate, htail, hreach⟩
  · intro hreach
    rcases hreach with hhead | htail
    · exact ⟨stride, by simp, hhead⟩
    · rcases htail with ⟨candidate, hmem, hcandidate⟩
      exact ⟨candidate, by simp [hmem], hcandidate⟩

/-- An empty stride family reaches no coil lags. -/
theorem not_coilStrideFamilyLagReach_nil
    {n pathLength lag : Nat} :
    ¬ coilStrideFamilyLagReach n pathLength lag [] := by
  rintro ⟨_stride, hmem, _hreach⟩
  cases hmem

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

/-- Increasing both sparse-attention budgets cannot remove a lag already
covered by a local-window plus stride-family plan. -/
theorem hybridFamilyLagReach_mono_window_pathLength
    {n smallWindow largeWindow smallPath largePath lag : Nat} {strides : List Nat}
    (hwindow : smallWindow ≤ largeWindow)
    (hpath : smallPath ≤ largePath)
    (hreach : hybridFamilyLagReach n smallWindow smallPath lag strides) :
    hybridFamilyLagReach n largeWindow largePath lag strides := by
  rcases hreach with hlocal | hfamily
  · exact Or.inl (localLagReach_mono_window hwindow hlocal)
  · exact Or.inr (coilStrideFamilyLagReach_mono_pathLength hpath hfamily)

/-- Exact decomposition for a local+stride-family plan when one stride is
added to the family. -/
theorem hybridFamilyLagReach_cons_iff
    {n window pathLength lag stride : Nat} {strides : List Nat} :
    hybridFamilyLagReach n window pathLength lag (stride :: strides) ↔
      hybridFamilyLagReach n window pathLength lag strides ∨
        coilLagReach n stride pathLength lag := by
  unfold hybridFamilyLagReach
  rw [coilStrideFamilyLagReach_cons_iff]
  constructor
  · intro hreach
    rcases hreach with hlocal | hfamily
    · exact Or.inl (Or.inl hlocal)
    · rcases hfamily with hhead | htail
      · exact Or.inr hhead
      · exact Or.inl (Or.inr htail)
  · intro hreach
    rcases hreach with hrest | hhead
    · rcases hrest with hlocal | htail
      · exact Or.inl hlocal
      · exact Or.inr (Or.inr htail)
    · exact Or.inr (Or.inl hhead)

/-- With no admitted coil strides, a local+stride-family plan reaches exactly
the local-window lags. -/
theorem hybridFamilyLagReach_nil_iff_local
    {n window pathLength lag : Nat} :
    hybridFamilyLagReach n window pathLength lag [] ↔ localLagReach window lag := by
  unfold hybridFamilyLagReach
  constructor
  · intro hreach
    rcases hreach with hlocal | hfamily
    · exact hlocal
    · exact False.elim (not_coilStrideFamilyLagReach_nil hfamily)
  · intro hlocal
    exact Or.inl hlocal

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

/-- A stride-family plan covers the context exactly when there is no positive
in-context lag carrying a gap certificate. -/
theorem hybridFamilyCoversContext_iff_no_uncovered_lag
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      ¬ ∃ lag, 1 ≤ lag ∧ lag < n ∧
        ¬ hybridFamilyLagReach n window pathLength lag strides := by
  constructor
  · intro hcover
    rintro ⟨lag, hpos, hcontext, hgap⟩
    exact hgap (hcover lag hpos hcontext)
  · intro hnogap lag hpos hcontext
    by_contra hgap
    exact hnogap ⟨lag, hpos, hcontext, hgap⟩

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

/-- Dense local-window coverage lifts to the named complete-coverage predicate
for any declared stride family. -/
theorem hybridFamilyCoversContext_of_localWindow_ge_context_sub_one
    {n window pathLength : Nat} {strides : List Nat}
    (hwindow : n - 1 ≤ window) :
    hybridFamilyCoversContext n window pathLength strides := by
  intro lag hpos hcontext
  exact hybridFamilyLagReach_of_localWindow_ge_context_sub_one hpos hcontext hwindow

/-- Increasing both sparse-attention budgets preserves complete context
coverage for a local-window plus stride-family plan. -/
theorem hybridFamilyCoversContext_mono_window_pathLength
    {n smallWindow largeWindow smallPath largePath : Nat} {strides : List Nat}
    (hwindow : smallWindow ≤ largeWindow)
    (hpath : smallPath ≤ largePath)
    (hcover : hybridFamilyCoversContext n smallWindow smallPath strides) :
    hybridFamilyCoversContext n largeWindow largePath strides := by
  intro lag hpos hcontext
  exact hybridFamilyLagReach_mono_window_pathLength hwindow hpath
    (hcover lag hpos hcontext)

/-- The raw candidate budget always contains the local-window budget. -/
theorem hybridFamilyRawCandidateBudget_ge_window
    {window pathLength : Nat} {strides : List Nat} :
    window ≤ hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyRawCandidateBudget
  exact Nat.le_add_right window (pathLength * strides.length)

/-- Adding one stride contributes one additional path-length block to the raw
candidate budget. -/
theorem hybridFamilyRawCandidateBudget_cons
    {window pathLength stride : Nat} {strides : List Nat} :
    hybridFamilyRawCandidateBudget window pathLength (stride :: strides) =
      hybridFamilyRawCandidateBudget window pathLength strides + pathLength := by
  unfold hybridFamilyRawCandidateBudget
  simp [Nat.mul_succ, Nat.add_comm, Nat.add_left_comm]

/-- Increasing the local-window or path-length budget cannot reduce the raw
candidate-budget upper bound for a fixed stride family. -/
theorem hybridFamilyRawCandidateBudget_mono_window_pathLength
    {smallWindow largeWindow smallPath largePath : Nat} {strides : List Nat}
    (hwindow : smallWindow ≤ largeWindow)
    (hpath : smallPath ≤ largePath) :
    hybridFamilyRawCandidateBudget smallWindow smallPath strides ≤
      hybridFamilyRawCandidateBudget largeWindow largePath strides := by
  unfold hybridFamilyRawCandidateBudget
  exact Nat.add_le_add hwindow (Nat.mul_le_mul_right strides.length hpath)

/-- The deduplicated candidate-count bound never exceeds the raw candidate
budget. -/
theorem hybridFamilyDedupCandidateBudgetBound_le_raw
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyDedupCandidateBudgetBound n window pathLength strides ≤
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyDedupCandidateBudgetBound
  exact Nat.min_le_right n (hybridFamilyRawCandidateBudget window pathLength strides)

/-- The deduplicated candidate-count bound never exceeds the finite context
size. -/
theorem hybridFamilyDedupCandidateBudgetBound_le_context
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyDedupCandidateBudgetBound n window pathLength strides ≤ n := by
  unfold hybridFamilyDedupCandidateBudgetBound
  exact Nat.min_le_left n (hybridFamilyRawCandidateBudget window pathLength strides)

/-- If the raw budget fits inside the context, the deduplicated candidate bound
is the raw budget. -/
theorem hybridFamilyDedupCandidateBudgetBound_eq_raw_of_raw_le_context
    {n window pathLength : Nat} {strides : List Nat}
    (hraw : hybridFamilyRawCandidateBudget window pathLength strides ≤ n) :
    hybridFamilyDedupCandidateBudgetBound n window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyDedupCandidateBudgetBound
  exact Nat.min_eq_right hraw

/-- If the context is no larger than the raw budget, the deduplicated candidate
bound is the context size. -/
theorem hybridFamilyDedupCandidateBudgetBound_eq_context_of_context_le_raw
    {n window pathLength : Nat} {strides : List Nat}
    (hcontext : n ≤ hybridFamilyRawCandidateBudget window pathLength strides) :
    hybridFamilyDedupCandidateBudgetBound n window pathLength strides = n := by
  unfold hybridFamilyDedupCandidateBudgetBound
  exact Nat.min_eq_left hcontext

/-- The local lag-candidate list has exactly `window` raw entries. -/
theorem localLagCandidateList_length (window : Nat) :
    (localLagCandidateList window).length = window := by
  unfold localLagCandidateList
  exact List.length_range'

/-- One stride contributes exactly `pathLength` raw residue candidates. -/
theorem coilLagResidueList_length (n stride pathLength : Nat) :
    (coilLagResidueList n stride pathLength).length = pathLength := by
  unfold coilLagResidueList
  simp

/-- A finite stride family contributes `pathLength * strides.length` raw residue
candidates before deduplication. -/
theorem coilStrideFamilyLagResidueList_length
    (n pathLength : Nat) (strides : List Nat) :
    (coilStrideFamilyLagResidueList n pathLength strides).length =
      pathLength * strides.length := by
  induction strides with
  | nil => simp [coilStrideFamilyLagResidueList]
  | cons stride strides ih =>
      simp [coilStrideFamilyLagResidueList, coilLagResidueList_length, ih,
        Nat.mul_succ, Nat.add_comm]

/-- The theorem-side lag-candidate list has exactly the raw sparse-attention
candidate budget before deduplication. -/
theorem hybridFamilyLagCandidateList_length
    (n window pathLength : Nat) (strides : List Nat) :
    (hybridFamilyLagCandidateList n window pathLength strides).length =
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyLagCandidateList hybridFamilyRawCandidateBudget
  simp [localLagCandidateList_length,
    coilStrideFamilyLagResidueList_length]

/-- The exact deduplicated lag-candidate count is never larger than the raw
candidate budget. -/
theorem hybridFamilyUniqueLagCandidateCount_le_raw
    (n window pathLength : Nat) (strides : List Nat) :
    hybridFamilyUniqueLagCandidateCount n window pathLength strides ≤
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyUniqueLagCandidateCount
  rw [← hybridFamilyLagCandidateList_length n window pathLength strides]
  exact List.Sublist.length_le (List.dedup_sublist _)

/-- Membership in the local candidate list is exactly local-window reachability. -/
theorem mem_localLagCandidateList_iff
    {window lag : Nat} :
    lag ∈ localLagCandidateList window ↔ localLagReach window lag := by
  unfold localLagCandidateList localLagReach
  rw [List.mem_range']
  constructor
  · rintro ⟨i, hi, hlag⟩
    constructor <;> omega
  · rintro ⟨hpos, hwindow⟩
    refine ⟨lag - 1, ?_, ?_⟩ <;> omega

/-- For an in-context lag, membership in one stride's residue-candidate list is
exactly the stride-path reachability predicate. -/
theorem mem_coilLagResidueList_iff
    {n stride pathLength lag : Nat} (hcontext : lag < n) :
    lag ∈ coilLagResidueList n stride pathLength ↔
      coilLagReach n stride pathLength lag := by
  unfold coilLagResidueList coilLagReach
  rw [List.mem_map]
  constructor
  · rintro ⟨step, hstepmem, hlag⟩
    rw [List.mem_range'] at hstepmem
    rcases hstepmem with ⟨i, hi, hstep⟩
    subst step
    refine ⟨1 + i, ?_, ?_, ?_⟩
    · omega
    · omega
    · rw [Nat.mod_eq_of_lt hcontext]
      simpa using hlag
  · rintro ⟨step, hpos, hstep, hmod⟩
    refine ⟨step, ?_, ?_⟩
    · rw [List.mem_range']
      refine ⟨step - 1, ?_, ?_⟩ <;> omega
    · rw [Nat.mod_eq_of_lt hcontext] at hmod
      exact hmod

/-- Every one-stride residue candidate is an in-context lag representative when
the context length is positive. -/
theorem mem_coilLagResidueList_lt_context
    {n stride pathLength lag : Nat}
    (hn : 0 < n)
    (hmem : lag ∈ coilLagResidueList n stride pathLength) :
    lag < n := by
  unfold coilLagResidueList at hmem
  rw [List.mem_map] at hmem
  rcases hmem with ⟨step, _hstep, hlag⟩
  rw [← hlag]
  exact Nat.mod_lt _ hn

/-- For an in-context lag, membership in the finite stride-family residue list
is exactly stride-family reachability. -/
theorem mem_coilStrideFamilyLagResidueList_iff
    {n pathLength lag : Nat} {strides : List Nat} (hcontext : lag < n) :
    lag ∈ coilStrideFamilyLagResidueList n pathLength strides ↔
      coilStrideFamilyLagReach n pathLength lag strides := by
  induction strides with
  | nil =>
      simp [coilStrideFamilyLagResidueList, not_coilStrideFamilyLagReach_nil]
  | cons stride strides ih =>
      simp [coilStrideFamilyLagResidueList, List.mem_append,
        mem_coilLagResidueList_iff hcontext, ih, coilStrideFamilyLagReach_cons_iff]

/-- Every finite stride-family residue candidate is an in-context lag
representative when the context length is positive. -/
theorem mem_coilStrideFamilyLagResidueList_lt_context
    {n pathLength lag : Nat} {strides : List Nat}
    (hn : 0 < n)
    (hmem : lag ∈ coilStrideFamilyLagResidueList n pathLength strides) :
    lag < n := by
  induction strides with
  | nil =>
      unfold coilStrideFamilyLagResidueList at hmem
      cases hmem
  | cons stride strides ih =>
      unfold coilStrideFamilyLagResidueList at hmem
      rw [List.mem_append] at hmem
      rcases hmem with hhead | htail
      · exact mem_coilLagResidueList_lt_context hn hhead
      · exact ih htail

/-- For an in-context lag, membership in the theorem-side hybrid candidate list
is exactly local+stride-family reachability. -/
theorem mem_hybridFamilyLagCandidateList_iff
    {n window pathLength lag : Nat} {strides : List Nat}
    (hcontext : lag < n) :
    lag ∈ hybridFamilyLagCandidateList n window pathLength strides ↔
      hybridFamilyLagReach n window pathLength lag strides := by
  unfold hybridFamilyLagCandidateList hybridFamilyLagReach
  rw [List.mem_append]
  rw [mem_localLagCandidateList_iff]
  rw [mem_coilStrideFamilyLagResidueList_iff hcontext]

/-- Complete context coverage is exactly finite coverage of the generated
positive-lag range by the theorem-side candidate list.

This is the list-level bridge used by executable sparse-attention certificates:
checking the finite range `1, ..., n - 1` against the candidate list is
equivalent to the quantified `hybridFamilyCoversContext` predicate. -/
theorem hybridFamilyCoversContext_iff_range_lags_mem_candidate_list
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      ∀ lag, lag ∈ List.range' 1 (n - 1) →
        lag ∈ hybridFamilyLagCandidateList n window pathLength strides := by
  constructor
  · intro hcover lag hmem
    rw [List.mem_range'] at hmem
    rcases hmem with ⟨i, hi, hlag⟩
    subst lag
    have hpos : 1 ≤ 1 + i := by omega
    have hcontext : 1 + i < n := by omega
    simpa [Nat.one_mul] using
      (mem_hybridFamilyLagCandidateList_iff hcontext).2
        (hcover (1 + i) hpos hcontext)
  · intro hmem lag hpos hcontext
    have hlag_mem : lag ∈ List.range' 1 (n - 1) := by
      rw [List.mem_range']
      refine ⟨lag - 1, ?_, ?_⟩ <;> omega
    exact (mem_hybridFamilyLagCandidateList_iff hcontext).1
      (hmem lag hlag_mem)

/-- Complete coverage requires at least as many raw sparse candidates as there
are positive in-context lags.

This is a planner-facing impossibility guard: before considering learning
quality or runtime, any local-window plus stride-family plan whose raw generator
budget is smaller than `n - 1` cannot cover every positive lag in a length-`n`
context. -/
theorem hybridFamilyRawCandidateBudget_ge_context_sub_one_of_covers
    {n window pathLength : Nat} {strides : List Nat}
    (hcover : hybridFamilyCoversContext n window pathLength strides) :
    n - 1 ≤ hybridFamilyRawCandidateBudget window pathLength strides := by
  let positiveLags := List.range' 1 (n - 1)
  let candidates := hybridFamilyLagCandidateList n window pathLength strides
  have hmem :
      ∀ lag, lag ∈ positiveLags → lag ∈ candidates := by
    intro lag hlag
    exact
      (hybridFamilyCoversContext_iff_range_lags_mem_candidate_list
        (n := n) (window := window) (pathLength := pathLength)
        (strides := strides)).1 hcover lag hlag
  have hsubset : positiveLags.toFinset ⊆ candidates.toFinset := by
    intro lag hlag
    rw [List.mem_toFinset] at hlag ⊢
    exact hmem lag hlag
  have hcard_subset :
      positiveLags.toFinset.card ≤ candidates.toFinset.card :=
    Finset.card_le_card hsubset
  have hpositive_card : positiveLags.toFinset.card = n - 1 := by
    have hnodup : positiveLags.Nodup := by
      simp [positiveLags, List.nodup_range']
    rw [List.card_toFinset, List.Nodup.dedup hnodup]
    simp [positiveLags, List.length_range']
  have hcandidates_card :
      candidates.toFinset.card =
        hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
    simp [candidates, hybridFamilyUniqueLagCandidateCount, List.card_toFinset]
  have hunique_le_raw :
      hybridFamilyUniqueLagCandidateCount n window pathLength strides ≤
        hybridFamilyRawCandidateBudget window pathLength strides :=
    hybridFamilyUniqueLagCandidateCount_le_raw n window pathLength strides
  exact hpositive_card ▸
    le_trans (hcandidates_card ▸ hcard_subset) hunique_le_raw

/-- Complete coverage requires at least as many unique theorem-side lag
candidates as there are positive in-context lags.

This is the deduplicated counterpart to the raw-budget lower bound: even if the
declared raw generator budget is large, duplicate lag candidates cannot cover
every positive lag unless the unique lag-candidate count reaches `n - 1`. -/
theorem hybridFamilyUniqueLagCandidateCount_ge_context_sub_one_of_covers
    {n window pathLength : Nat} {strides : List Nat}
    (hcover : hybridFamilyCoversContext n window pathLength strides) :
    n - 1 ≤ hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
  let positiveLags := List.range' 1 (n - 1)
  let candidates := hybridFamilyLagCandidateList n window pathLength strides
  have hmem :
      ∀ lag, lag ∈ positiveLags → lag ∈ candidates := by
    intro lag hlag
    exact
      (hybridFamilyCoversContext_iff_range_lags_mem_candidate_list
        (n := n) (window := window) (pathLength := pathLength)
        (strides := strides)).1 hcover lag hlag
  have hsubset : positiveLags.toFinset ⊆ candidates.toFinset := by
    intro lag hlag
    rw [List.mem_toFinset] at hlag ⊢
    exact hmem lag hlag
  have hcard_subset :
      positiveLags.toFinset.card ≤ candidates.toFinset.card :=
    Finset.card_le_card hsubset
  have hpositive_card : positiveLags.toFinset.card = n - 1 := by
    have hnodup : positiveLags.Nodup := by
      simp [positiveLags, List.nodup_range']
    rw [List.card_toFinset, List.Nodup.dedup hnodup]
    simp [positiveLags, List.length_range']
  have hcandidates_card :
      candidates.toFinset.card =
        hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
    simp [candidates, hybridFamilyUniqueLagCandidateCount, List.card_toFinset]
  exact hpositive_card ▸ (hcandidates_card ▸ hcard_subset)

/-- If every generated lag candidate is already a positive in-context lag,
complete coverage is equivalent to the deduplicated lag-candidate count reaching
the full positive-lag count `n - 1`.

This turns the one-sided unique-count lower bound into an iff when the candidate
generator cannot waste entries on zero or out-of-context residues. -/
theorem hybridFamilyCoversContext_iff_uniqueLagCandidateCount_eq_context_sub_one_of_candidate_range
    {n window pathLength : Nat} {strides : List Nat}
    (hcandidate_range :
      ∀ lag, lag ∈ hybridFamilyLagCandidateList n window pathLength strides →
        1 ≤ lag ∧ lag < n) :
    hybridFamilyCoversContext n window pathLength strides ↔
      hybridFamilyUniqueLagCandidateCount n window pathLength strides = n - 1 := by
  let positiveLags := List.range' 1 (n - 1)
  let candidates := hybridFamilyLagCandidateList n window pathLength strides
  have hpositive_card : positiveLags.toFinset.card = n - 1 := by
    have hnodup : positiveLags.Nodup := by
      simp [positiveLags, List.nodup_range']
    rw [List.card_toFinset, List.Nodup.dedup hnodup]
    simp [positiveLags, List.length_range']
  have hcandidates_card :
      candidates.toFinset.card =
        hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
    simp [candidates, hybridFamilyUniqueLagCandidateCount, List.card_toFinset]
  have hcandidate_subset_positive : candidates.toFinset ⊆ positiveLags.toFinset := by
    intro lag hlag
    rw [List.mem_toFinset] at hlag ⊢
    have hrange := hcandidate_range lag hlag
    rw [List.mem_range']
    refine ⟨lag - 1, ?_, ?_⟩ <;> omega
  constructor
  · intro hcover
    have hpositive_subset_candidates : positiveLags.toFinset ⊆ candidates.toFinset := by
      intro lag hlag
      rw [List.mem_toFinset] at hlag ⊢
      exact
        (hybridFamilyCoversContext_iff_range_lags_mem_candidate_list
          (n := n) (window := window) (pathLength := pathLength)
          (strides := strides)).1 hcover lag hlag
    have hle :
        candidates.toFinset.card ≤ positiveLags.toFinset.card :=
      Finset.card_le_card hcandidate_subset_positive
    have hge :
        positiveLags.toFinset.card ≤ candidates.toFinset.card :=
      Finset.card_le_card hpositive_subset_candidates
    omega
  · intro hcount
    rw [hybridFamilyCoversContext_iff_range_lags_mem_candidate_list]
    intro lag hlag
    have hcard_ge :
        positiveLags.toFinset.card ≤ candidates.toFinset.card := by
      rw [hcandidates_card, hcount, hpositive_card]
    have hset_eq : candidates.toFinset = positiveLags.toFinset :=
      Finset.eq_of_subset_of_card_le hcandidate_subset_positive hcard_ge
    have hlag_fin : lag ∈ positiveLags.toFinset := by
      rw [List.mem_toFinset]
      exact hlag
    have hcandidate_fin : lag ∈ candidates.toFinset := by
      rw [hset_eq]
      exact hlag_fin
    rw [List.mem_toFinset] at hcandidate_fin
    exact hcandidate_fin

/-- If every generated lag candidate is already a positive in-context lag, the
covered-lag report count equals the exact deduplicated lag-candidate count. -/
theorem hybridFamilyCoveredLagList_length_eq_uniqueLagCandidateCount_of_candidate_range
    {n window pathLength : Nat} {strides : List Nat}
    (hcandidate_range :
      ∀ lag, lag ∈ hybridFamilyLagCandidateList n window pathLength strides →
        1 ≤ lag ∧ lag < n) :
    (hybridFamilyCoveredLagList n window pathLength strides).length =
      hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
  let positiveLags := List.range' 1 (n - 1)
  let candidates := hybridFamilyLagCandidateList n window pathLength strides
  let covered := hybridFamilyCoveredLagList n window pathLength strides
  have hpositive_nodup : positiveLags.Nodup := by
    simp [positiveLags, List.nodup_range']
  have hcovered_nodup : covered.Nodup := by
    unfold covered hybridFamilyCoveredLagList
    exact hpositive_nodup.filter _
  have hcovered_card : covered.toFinset.card = covered.length := by
    rw [List.card_toFinset, List.Nodup.dedup hcovered_nodup]
  have hcovered_toFinset : covered.toFinset = candidates.toFinset := by
    ext lag
    rw [List.mem_toFinset, List.mem_toFinset]
    unfold covered hybridFamilyCoveredLagList
    simp only [List.mem_filter, decide_eq_true_eq]
    constructor
    · intro hcovered_mem
      exact hcovered_mem.2
    · intro hcandidate_mem
      have hrange := hcandidate_range lag hcandidate_mem
      constructor
      · rw [List.mem_range']
        refine ⟨lag - 1, ?_, ?_⟩ <;> omega
      · exact hcandidate_mem
  rw [← hcovered_card, hcovered_toFinset]
  simp [candidates, hybridFamilyUniqueLagCandidateCount, List.card_toFinset]

/-- Membership in the finite covered-lag list is exactly positive in-context
semantic reachability.

This is the positive side of the sparse-attention certifier contract: every
listed covered lag is really reachable by the local+stride-family plan, and
every reachable positive in-context lag appears in the list. -/
theorem mem_hybridFamilyCoveredLagList_iff
    {n window pathLength lag : Nat} {strides : List Nat} :
    lag ∈ hybridFamilyCoveredLagList n window pathLength strides ↔
      1 ≤ lag ∧ lag < n ∧
        hybridFamilyLagReach n window pathLength lag strides := by
  unfold hybridFamilyCoveredLagList
  simp only [List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨hrange, hmem⟩
    rw [List.mem_range'] at hrange
    rcases hrange with ⟨i, hi, hlag⟩
    subst lag
    have hpos : 1 ≤ 1 + 1 * i := by omega
    have hcontext : 1 + 1 * i < n := by omega
    exact ⟨hpos, hcontext, (mem_hybridFamilyLagCandidateList_iff hcontext).1 hmem⟩
  · rintro ⟨hpos, hcontext, hreach⟩
    constructor
    · rw [List.mem_range']
      refine ⟨lag - 1, ?_, ?_⟩ <;> omega
    · exact (mem_hybridFamilyLagCandidateList_iff hcontext).2 hreach

/-- Membership in the finite uncovered-lag list is exactly a positive
in-context semantic gap.

This is the proof-carrying sparse-attention contract form an executable
certifier can cite: every listed lag is really uncovered, and every real
uncovered positive in-context lag appears in the finite list. -/
theorem mem_hybridFamilyUncoveredLagList_iff
    {n window pathLength lag : Nat} {strides : List Nat} :
    lag ∈ hybridFamilyUncoveredLagList n window pathLength strides ↔
      1 ≤ lag ∧ lag < n ∧
        ¬ hybridFamilyLagReach n window pathLength lag strides := by
  unfold hybridFamilyUncoveredLagList
  simp only [List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨hrange, hnotmem⟩
    rw [List.mem_range'] at hrange
    rcases hrange with ⟨i, hi, hlag⟩
    subst lag
    have hpos : 1 ≤ 1 + 1 * i := by omega
    have hcontext : 1 + 1 * i < n := by omega
    refine ⟨hpos, hcontext, ?_⟩
    intro hreach
    exact hnotmem ((mem_hybridFamilyLagCandidateList_iff hcontext).2 hreach)
  · rintro ⟨hpos, hcontext, hgap⟩
    constructor
    · rw [List.mem_range']
      refine ⟨lag - 1, ?_, ?_⟩ <;> omega
    · intro hmem
      exact hgap ((mem_hybridFamilyLagCandidateList_iff hcontext).1 hmem)

/-- Covered and uncovered finite lag lists are disjoint.

This is the partition-safety side of the sparse-attention report: a positive
in-context lag cannot be simultaneously listed as a semantic hit and a
semantic gap for the same declared sparse plan. -/
theorem hybridFamilyCoveredLagList_disjoint_uncoveredLagList
    {n window pathLength : Nat} {strides : List Nat} :
    (hybridFamilyCoveredLagList n window pathLength strides).Disjoint
      (hybridFamilyUncoveredLagList n window pathLength strides) := by
  rw [List.disjoint_left]
  intro lag hcovered huncovered
  have hhit := (mem_hybridFamilyCoveredLagList_iff).1 hcovered
  have hgap := (mem_hybridFamilyUncoveredLagList_iff).1 huncovered
  exact hgap.2.2 hhit.2.2

/-- Every positive in-context lag appears in either the covered or uncovered
finite lag list.

Together with `hybridFamilyCoveredLagList_disjoint_uncoveredLagList`, this says
the two theorem-side lists form an exact finite partition of the positive lag
range for the declared sparse-attention plan. -/
theorem mem_hybridFamilyCoveredLagList_or_mem_hybridFamilyUncoveredLagList_of_pos_lt_context
    {n window pathLength lag : Nat} {strides : List Nat}
    (hpos : 1 ≤ lag) (hcontext : lag < n) :
    lag ∈ hybridFamilyCoveredLagList n window pathLength strides ∨
      lag ∈ hybridFamilyUncoveredLagList n window pathLength strides := by
  by_cases hreach : hybridFamilyLagReach n window pathLength lag strides
  · exact Or.inl ((mem_hybridFamilyCoveredLagList_iff).2
      ⟨hpos, hcontext, hreach⟩)
  · exact Or.inr ((mem_hybridFamilyUncoveredLagList_iff).2
      ⟨hpos, hcontext, hreach⟩)

/-- The covered and uncovered finite lag-list lengths add up to the number of
positive in-context lags.

This is the count side of the sparse-attention partition certificate: every
positive lag below the context contributes to exactly one of the reported
finite lists, so the two report counts add to `n - 1`. -/
theorem hybridFamilyCoveredUncoveredLagList_length_add
    {n window pathLength : Nat} {strides : List Nat} :
    (hybridFamilyCoveredLagList n window pathLength strides).length +
      (hybridFamilyUncoveredLagList n window pathLength strides).length = n - 1 := by
  unfold hybridFamilyCoveredLagList hybridFamilyUncoveredLagList
  simpa [List.length_range'] using
    (List.length_eq_length_filter_add
      (l := List.range' 1 (n - 1))
      (f := fun lag =>
        decide (lag ∈ hybridFamilyLagCandidateList n window pathLength strides))).symm

/-- Under the positive in-context candidate-range hypothesis, the uncovered-gap
count is exactly the positive-lag count minus the unique lag-candidate count. -/
theorem hybridFamilyUncoveredLagList_length_eq_context_sub_one_sub_uniqueLagCandidateCount_of_candidate_range
    {n window pathLength : Nat} {strides : List Nat}
    (hcandidate_range :
      ∀ lag, lag ∈ hybridFamilyLagCandidateList n window pathLength strides →
        1 ≤ lag ∧ lag < n) :
    (hybridFamilyUncoveredLagList n window pathLength strides).length =
      n - 1 - hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
  have hcovered :=
    hybridFamilyCoveredLagList_length_eq_uniqueLagCandidateCount_of_candidate_range
      (n := n) (window := window) (pathLength := pathLength) (strides := strides)
      hcandidate_range
  have hpartition :=
    hybridFamilyCoveredUncoveredLagList_length_add
      (n := n) (window := window) (pathLength := pathLength) (strides := strides)
  omega

/-- Complete sparse-attention coverage is equivalent to an empty finite
uncovered-lag list. -/
theorem hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      hybridFamilyUncoveredLagList n window pathLength strides = [] := by
  constructor
  · intro hcover
    apply List.eq_nil_iff_forall_not_mem.2
    intro lag hmem
    have hgap := (mem_hybridFamilyUncoveredLagList_iff).1 hmem
    exact hgap.2.2 (hcover lag hgap.1 hgap.2.1)
  · intro hempty
    exact (hybridFamilyCoversContext_iff_no_uncovered_lag).2 (by
      rintro ⟨lag, hpos, hcontext, hgap⟩
      have hmem : lag ∈ hybridFamilyUncoveredLagList n window pathLength strides :=
        (mem_hybridFamilyUncoveredLagList_iff).2 ⟨hpos, hcontext, hgap⟩
      rw [hempty] at hmem
      exact List.not_mem_nil hmem)

/-- The first-uncovered-lag field is empty exactly when the finite uncovered
lag list is empty. -/
theorem hybridFamilyFirstUncoveredLag_eq_none_iff_uncoveredLagList_eq_nil
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyFirstUncoveredLag n window pathLength strides = none ↔
      hybridFamilyUncoveredLagList n window pathLength strides = [] := by
  unfold hybridFamilyFirstUncoveredLag
  generalize hlist :
    hybridFamilyUncoveredLagList n window pathLength strides = xs
  cases xs with
  | nil =>
      simp
  | cons head tail =>
      simp

/-- Complete sparse-attention coverage is equivalent to having no first
uncovered lag.

This is the proof-carrying status bit behind certifier fields such as
`coverage_complete` and `first_uncovered_lag`: a missing first gap is not a
Python convention, but the theorem-side empty uncovered-list criterion. -/
theorem hybridFamilyCoversContext_iff_firstUncoveredLag_eq_none
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      hybridFamilyFirstUncoveredLag n window pathLength strides = none := by
  rw [hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil,
    hybridFamilyFirstUncoveredLag_eq_none_iff_uncoveredLagList_eq_nil]

/-- Reporting a first uncovered lag is exactly reporting the head of the
finite uncovered-lag list. -/
theorem hybridFamilyFirstUncoveredLag_eq_some_iff_uncoveredLagList_eq_cons
    {n window pathLength lag : Nat} {strides : List Nat} :
    hybridFamilyFirstUncoveredLag n window pathLength strides = some lag ↔
      ∃ tail,
        hybridFamilyUncoveredLagList n window pathLength strides = lag :: tail := by
  unfold hybridFamilyFirstUncoveredLag
  generalize hlist :
    hybridFamilyUncoveredLagList n window pathLength strides = xs
  cases xs with
  | nil =>
      simp
  | cons head tail =>
      constructor
      · intro hfirst
        simp at hfirst
        subst lag
        exact ⟨tail, rfl⟩
      · rintro ⟨tail', htail'⟩
        cases htail'
        simp

/-- Any reported first uncovered lag is a genuine positive in-context
semantic miss for the declared sparse-attention plan. -/
theorem hybridFamilyFirstUncoveredLag_eq_some_gap
    {n window pathLength lag : Nat} {strides : List Nat}
    (hfirst :
      hybridFamilyFirstUncoveredLag n window pathLength strides = some lag) :
    1 ≤ lag ∧ lag < n ∧
      ¬ hybridFamilyLagReach n window pathLength lag strides := by
  rcases
    (hybridFamilyFirstUncoveredLag_eq_some_iff_uncoveredLagList_eq_cons).1
      hfirst with
    ⟨tail, hlist⟩
  exact (mem_hybridFamilyUncoveredLagList_iff).1 (by rw [hlist]; simp)

/-- Complete sparse-attention coverage is equivalent to zero uncovered lags. -/
theorem hybridFamilyCoversContext_iff_uncoveredLagList_length_eq_zero
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      (hybridFamilyUncoveredLagList n window pathLength strides).length = 0 := by
  rw [hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil,
    List.length_eq_zero_iff]

/-- A positive uncovered-lag count is equivalent to the existence of a semantic
uncovered positive in-context lag.

This is the witness side of the sparse-attention gap-count certificate: a
nonzero uncovered count is not just a reporting artifact; it exists exactly
when there is a concrete positive lag below the context length that the
declared local-window plus stride-family plan cannot reach. -/
theorem hybridFamilyUncoveredLagList_length_pos_iff_exists_uncovered_lag
    {n window pathLength : Nat} {strides : List Nat} :
    0 < (hybridFamilyUncoveredLagList n window pathLength strides).length ↔
      ∃ lag, 1 ≤ lag ∧ lag < n ∧
        ¬ hybridFamilyLagReach n window pathLength lag strides := by
  rw [List.length_pos_iff_exists_mem]
  constructor
  · rintro ⟨lag, hmem⟩
    exact ⟨lag, (mem_hybridFamilyUncoveredLagList_iff).1 hmem⟩
  · rintro ⟨lag, hgap⟩
    exact ⟨lag, (mem_hybridFamilyUncoveredLagList_iff).2 hgap⟩

/-- A positive uncovered-lag count is equivalent to the first-uncovered-lag
field being populated.

This bridges two executable sparse-attention report fields: the numeric
`uncovered_lag_count > 0` status and the optional first-gap witness carry the
same theorem-side information. -/
theorem hybridFamilyUncoveredLagList_length_pos_iff_firstUncoveredLag_ne_none
    {n window pathLength : Nat} {strides : List Nat} :
    0 < (hybridFamilyUncoveredLagList n window pathLength strides).length ↔
      hybridFamilyFirstUncoveredLag n window pathLength strides ≠ none := by
  unfold hybridFamilyFirstUncoveredLag
  generalize hlist :
    hybridFamilyUncoveredLagList n window pathLength strides = xs
  cases xs with
  | nil =>
      simp
  | cons head tail =>
      simp

/-- The covered-lag count falls short of the full positive-lag range exactly
when there is a semantic uncovered positive in-context lag.

This packages the failure side of the sparse-attention count certificate:
reporting fewer than `n - 1` covered lags is equivalent to having a concrete
gap witness, not merely a smaller numeric count. -/
theorem hybridFamilyCoveredLagList_length_lt_context_sub_one_iff_exists_uncovered_lag
    {n window pathLength : Nat} {strides : List Nat} :
    (hybridFamilyCoveredLagList n window pathLength strides).length < n - 1 ↔
      ∃ lag, 1 ≤ lag ∧ lag < n ∧
        ¬ hybridFamilyLagReach n window pathLength lag strides := by
  constructor
  · intro hshort
    have hpartition :=
      hybridFamilyCoveredUncoveredLagList_length_add
        (n := n) (window := window) (pathLength := pathLength) (strides := strides)
    have huncovered_pos :
        0 < (hybridFamilyUncoveredLagList n window pathLength strides).length := by
      omega
    exact (hybridFamilyUncoveredLagList_length_pos_iff_exists_uncovered_lag).1
      huncovered_pos
  · intro hgap
    have huncovered_pos :
        0 < (hybridFamilyUncoveredLagList n window pathLength strides).length :=
      (hybridFamilyUncoveredLagList_length_pos_iff_exists_uncovered_lag).2 hgap
    have hpartition :=
      hybridFamilyCoveredUncoveredLagList_length_add
        (n := n) (window := window) (pathLength := pathLength) (strides := strides)
    omega

/-- Complete sparse-attention coverage is equivalent to the finite covered-lag
count reaching the full positive-lag count `n - 1`.

This is the quantitative counterpart to the empty-uncovered-list criterion: the
covered and uncovered lag lists partition the positive in-context lags, so
covering all positive lags is exactly the same as reporting `n - 1` covered
lags. -/
theorem hybridFamilyCoversContext_iff_coveredLagList_length_eq_context_sub_one
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyCoversContext n window pathLength strides ↔
      (hybridFamilyCoveredLagList n window pathLength strides).length = n - 1 := by
  constructor
  · intro hcover
    have huncovered :
        (hybridFamilyUncoveredLagList n window pathLength strides).length = 0 :=
      (hybridFamilyCoversContext_iff_uncoveredLagList_length_eq_zero).1 hcover
    have hpartition :=
      hybridFamilyCoveredUncoveredLagList_length_add
        (n := n) (window := window) (pathLength := pathLength) (strides := strides)
    omega
  · intro hcovered
    rw [hybridFamilyCoversContext_iff_uncoveredLagList_length_eq_zero]
    have hpartition :=
      hybridFamilyCoveredUncoveredLagList_length_add
        (n := n) (window := window) (pathLength := pathLength) (strides := strides)
    omega

/-- If the local window is below the context length, then every theorem-side
lag candidate is a strict in-context representative. -/
theorem mem_hybridFamilyLagCandidateList_lt_context_of_window_lt_context
    {n window pathLength lag : Nat} {strides : List Nat}
    (hwindow : window < n)
    (hmem : lag ∈ hybridFamilyLagCandidateList n window pathLength strides) :
    lag < n := by
  have hn : 0 < n := lt_of_le_of_lt (Nat.zero_le window) hwindow
  unfold hybridFamilyLagCandidateList at hmem
  rw [List.mem_append] at hmem
  rcases hmem with hlocal | hcoil
  · have hreach : localLagReach window lag := by
      exact (mem_localLagCandidateList_iff).1 hlocal
    exact lt_of_le_of_lt hreach.2 hwindow
  · exact mem_coilStrideFamilyLagResidueList_lt_context hn hcoil

/-- The query-indexed candidate list has the same raw length as the theorem-side
lag candidate list, hence the same raw candidate budget. -/
theorem hybridFamilyQueryCandidateList_length
    (n query window pathLength : Nat) (strides : List Nat) :
    (hybridFamilyQueryCandidateList n query window pathLength strides).length =
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyQueryCandidateList
  rw [List.length_map, hybridFamilyLagCandidateList_length]

/-- The exact deduplicated query-indexed candidate count is never larger than
the raw sparse-attention candidate budget. -/
theorem hybridFamilyUniqueQueryCandidateCount_le_raw
    (n query window pathLength : Nat) (strides : List Nat) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides ≤
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyUniqueQueryCandidateCount
  rw [← hybridFamilyQueryCandidateList_length n query window pathLength strides]
  exact List.Sublist.length_le (List.dedup_sublist _)

/-- The exact deduplicated query-indexed candidate count is never larger than
the finite context when the context is nonempty.

Every theorem-side query candidate is produced by reducing a predecessor index
modulo `n`, so deduplicating those candidates can never yield more than the
`n` available residue addresses. -/
theorem hybridFamilyUniqueQueryCandidateCount_le_context_of_pos
    {n query window pathLength : Nat} {strides : List Nat}
    (hn : 0 < n) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides ≤ n := by
  let candidates :=
    hybridFamilyQueryCandidateList n query window pathLength strides
  have hsubset : candidates.toFinset ⊆ Finset.range n := by
    intro candidate hcandidate
    rw [List.mem_toFinset] at hcandidate
    unfold candidates hybridFamilyQueryCandidateList at hcandidate
    rw [List.mem_map] at hcandidate
    rcases hcandidate with ⟨lag, _hlag, rfl⟩
    unfold predecessorIndex
    exact Finset.mem_range.2 (Nat.mod_lt _ hn)
  have hcard := Finset.card_le_card hsubset
  simpa [hybridFamilyUniqueQueryCandidateCount, candidates, List.card_toFinset] using hcard

/-- The exact deduplicated query-indexed candidate count is bounded by the
context-clipped sparse-attention budget `min(context, raw_budget)`.

This packages the two independent facts engineers need from the report: the
deduplicated query candidates cannot exceed either the raw generator budget or
the finite context size. -/
theorem hybridFamilyUniqueQueryCandidateCount_le_dedup_bound_of_context_pos
    {n query window pathLength : Nat} {strides : List Nat}
    (hn : 0 < n) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides ≤
      hybridFamilyDedupCandidateBudgetBound n window pathLength strides := by
  unfold hybridFamilyDedupCandidateBudgetBound
  exact le_min
    (hybridFamilyUniqueQueryCandidateCount_le_context_of_pos
      (query := query) (window := window) (pathLength := pathLength)
      (strides := strides) hn)
    (hybridFamilyUniqueQueryCandidateCount_le_raw
      n query window pathLength strides)

/-- Mapping lag candidates to query-indexed predecessor addresses cannot create
more distinct candidates than the lag-side generator already had.

The query list is the image of the lag list under `predecessorIndex`; finite
images can identify values but cannot increase cardinality. This lets the
executable report treat lag-side deduplication as a theorem-backed upper bound
for the exact query-indexed deduplicated count. -/
theorem hybridFamilyUniqueQueryCandidateCount_le_uniqueLagCandidateCount
    (n query window pathLength : Nat) (strides : List Nat) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides ≤
      hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
  unfold hybridFamilyUniqueQueryCandidateCount
    hybridFamilyQueryCandidateList hybridFamilyUniqueLagCandidateCount
  let xs := hybridFamilyLagCandidateList n window pathLength strides
  let f := predecessorIndex n query
  have hsubset : (xs.map f).toFinset ⊆ Finset.image f xs.toFinset := by
    intro candidate hcandidate
    rw [List.mem_toFinset] at hcandidate
    rw [List.mem_map] at hcandidate
    rcases hcandidate with ⟨lag, hlag, rfl⟩
    rw [Finset.mem_image]
    exact ⟨lag, by rw [List.mem_toFinset]; exact hlag, rfl⟩
  have hcardSubset :
      (xs.map f).toFinset.card ≤ (Finset.image f xs.toFinset).card :=
    Finset.card_le_card hsubset
  have hcardImage :
      (Finset.image f xs.toFinset).card ≤ xs.toFinset.card :=
    Finset.card_image_le
  have hcard : (xs.map f).toFinset.card ≤ xs.toFinset.card :=
    le_trans hcardSubset hcardImage
  simpa [xs, f, List.card_toFinset] using hcard

/-- If query predecessor indexing is injective on the generated lag candidates,
then mapping lags to query-indexed predecessor addresses preserves the exact
deduplicated candidate count.

Together with `hybridFamilyUniqueQueryCandidateCount_le_uniqueLagCandidateCount`,
this separates the general image-count cap from the no-merge regime: query
addressing can only reduce the unique count, and it preserves that count exactly
when the generated lags are not identified by the predecessor map. -/
theorem hybridFamilyUniqueQueryCandidateCount_eq_uniqueLagCandidateCount_of_predecessor_injective
    {n query window pathLength : Nat} {strides : List Nat}
    (hinjective :
      hybridFamilyPredecessorInjectiveOnLagCandidates n query window pathLength strides) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides =
      hybridFamilyUniqueLagCandidateCount n window pathLength strides := by
  unfold hybridFamilyUniqueQueryCandidateCount
    hybridFamilyQueryCandidateList hybridFamilyUniqueLagCandidateCount
  unfold hybridFamilyPredecessorInjectiveOnLagCandidates at hinjective
  let xs := hybridFamilyLagCandidateList n window pathLength strides
  let f := predecessorIndex n query
  have hquery_le_lag :
      (xs.map f).toFinset.card ≤ xs.toFinset.card := by
    have hsubset : (xs.map f).toFinset ⊆ Finset.image f xs.toFinset := by
      intro candidate hcandidate
      rw [List.mem_toFinset] at hcandidate
      rw [List.mem_map] at hcandidate
      rcases hcandidate with ⟨lag, hlag, rfl⟩
      rw [Finset.mem_image]
      exact ⟨lag, by rw [List.mem_toFinset]; exact hlag, rfl⟩
    have hcardSubset :
        (xs.map f).toFinset.card ≤ (Finset.image f xs.toFinset).card :=
      Finset.card_le_card hsubset
    have hcardImage :
        (Finset.image f xs.toFinset).card ≤ xs.toFinset.card :=
      Finset.card_image_le
    exact le_trans hcardSubset hcardImage
  have hmaps : Set.MapsTo f ↑xs.toFinset ↑(xs.map f).toFinset := by
    intro lag hlag
    have hlagList : lag ∈ xs := by
      simpa using hlag
    simpa using (List.mem_map.2 ⟨lag, hlagList, rfl⟩ : f lag ∈ xs.map f)
  have hinj : Set.InjOn f ↑xs.toFinset := by
    intro left hleft right hright heq
    have hleftList : left ∈ xs := by
      simpa using hleft
    have hrightList : right ∈ xs := by
      simpa using hright
    exact hinjective left hleftList right hrightList heq
  have hlag_le_query : xs.toFinset.card ≤ (xs.map f).toFinset.card :=
    Finset.card_le_card_of_injOn f hmaps hinj
  have hcard : (xs.map f).toFinset.card = xs.toFinset.card :=
    le_antisymm hquery_le_lag hlag_le_query
  simpa [xs, f, List.card_toFinset] using hcard

/-- A no-wrap single stride generates duplicate-free residues.

If all admitted multiples `step * stride`, `1 ≤ step ≤ pathLength`, remain
strictly below the context length, then reducing them modulo the context does
not identify two different steps. -/
theorem coilLagResidueList_nodup_of_path_mul_stride_lt_context
    {n stride pathLength : Nat}
    (hstride : 0 < stride)
    (hbound : pathLength * stride < n) :
    (coilLagResidueList n stride pathLength).Nodup := by
  unfold coilLagResidueList
  refine (List.nodup_range' (s := 1) (n := pathLength)).map_on ?_
  intro left hleft right hright heq
  have hleft_le : left ≤ pathLength := by
    rw [List.mem_range'] at hleft
    rcases hleft with ⟨i, hi, hleft⟩
    subst left
    omega
  have hright_le : right ≤ pathLength := by
    rw [List.mem_range'] at hright
    rcases hright with ⟨i, hi, hright⟩
    subst right
    omega
  have hleft_bound : left * stride < n :=
    lt_of_le_of_lt (Nat.mul_le_mul_right stride hleft_le) hbound
  have hright_bound : right * stride < n :=
    lt_of_le_of_lt (Nat.mul_le_mul_right stride hright_le) hbound
  rw [Nat.mod_eq_of_lt hleft_bound, Nat.mod_eq_of_lt hright_bound] at heq
  exact Nat.mul_right_cancel hstride heq

/-- A one-stride family inherits the no-wrap duplicate-free residue condition. -/
theorem coilStrideFamilyLagResiduesNoCollision_singleton_of_path_mul_stride_lt_context
    {n stride pathLength : Nat}
    (hstride : 0 < stride)
    (hbound : pathLength * stride < n) :
    coilStrideFamilyLagResiduesNoCollision n pathLength [stride] := by
  unfold coilStrideFamilyLagResiduesNoCollision coilStrideFamilyLagResidueList
  exact (coilLagResidueList_nodup_of_path_mul_stride_lt_context
    (n := n) (stride := stride) (pathLength := pathLength) hstride hbound).append
      (by
        change ([].Nodup)
        exact List.nodup_nil)
      (by
        rw [List.disjoint_left]
        intro _ _ hmem
        cases hmem)

/-- Appending one stride preserves residue no-collision when the head stride
block, the tail family, and the boundary between them are all duplicate-free. -/
theorem coilStrideFamilyLagResiduesNoCollision_cons_of_head_tail_disjoint
    {n stride pathLength : Nat} {strides : List Nat}
    (hhead : (coilLagResidueList n stride pathLength).Nodup)
    (htail : coilStrideFamilyLagResiduesNoCollision n pathLength strides)
    (hdisjoint : coilLagResiduesDisjointFromFamily n stride pathLength strides) :
    coilStrideFamilyLagResiduesNoCollision n pathLength (stride :: strides) := by
  unfold coilStrideFamilyLagResiduesNoCollision coilStrideFamilyLagResidueList
  unfold coilStrideFamilyLagResiduesNoCollision at htail
  unfold coilLagResiduesDisjointFromFamily at hdisjoint
  exact hhead.append htail hdisjoint

/-- A numeric sufficient condition for the head stride block to be disjoint
from a tail family.

If the head block and every tail block remain below the context length before
modulo reduction, and the largest possible head value is still below every
tail stride, then no head residue can equal a tail-family residue. -/
theorem coilLagResiduesDisjointFromFamily_of_path_mul_head_lt_tail_strides
    {n stride pathLength : Nat} {strides : List Nat}
    (hheadBound : pathLength * stride < n)
    (htailBound : ∀ tailStride ∈ strides, pathLength * tailStride < n)
    (hseparated : ∀ tailStride ∈ strides, pathLength * stride < tailStride) :
    coilLagResiduesDisjointFromFamily n stride pathLength strides := by
  unfold coilLagResiduesDisjointFromFamily
  rw [List.disjoint_left]
  intro lag hhead htail
  unfold coilLagResidueList at hhead
  rw [List.mem_map] at hhead
  rcases hhead with ⟨headStep, hheadStepMem, hheadLag⟩
  have hheadStepLe : headStep ≤ pathLength := by
    rw [List.mem_range'] at hheadStepMem
    rcases hheadStepMem with ⟨i, hi, hstep⟩
    subst headStep
    omega
  have hheadStepBound : headStep * stride < n :=
    lt_of_le_of_lt (Nat.mul_le_mul_right stride hheadStepLe) hheadBound
  have hlag_eq_head : lag = headStep * stride := by
    symm
    simpa [Nat.mod_eq_of_lt hheadStepBound] using hheadLag
  have hcontext : lag < n := by
    rw [hlag_eq_head]
    exact hheadStepBound
  rw [mem_coilStrideFamilyLagResidueList_iff hcontext] at htail
  rcases htail with ⟨tailStride, htailStrideMem, tailStep, htailStepPos,
    htailStepLe, htailLag⟩
  have htailStepBound : tailStep * tailStride < n :=
    lt_of_le_of_lt (Nat.mul_le_mul_right tailStride htailStepLe)
      (htailBound tailStride htailStrideMem)
  have htail_eq_lag : tailStep * tailStride = lag := by
    simpa [Nat.mod_eq_of_lt htailStepBound, Nat.mod_eq_of_lt hcontext] using htailLag
  have hhead_le : headStep * stride ≤ pathLength * stride :=
    Nat.mul_le_mul_right stride hheadStepLe
  have htail_stride_le : tailStride ≤ tailStep * tailStride := by
    calc
      tailStride = 1 * tailStride := by rw [Nat.one_mul]
      _ ≤ tailStep * tailStride := Nat.mul_le_mul_right tailStride htailStepPos
  have hlt : lag < tailStep * tailStride := by
    rw [hlag_eq_head]
    exact lt_of_le_of_lt hhead_le
      (lt_of_lt_of_le (hseparated tailStride htailStrideMem) htail_stride_le)
  rw [htail_eq_lag] at hlt
  exact (Nat.lt_irrefl lag) hlt

/-- Ordered no-wrap separation is a finite-family sufficient condition for
duplicate-free stride-family residues. -/
theorem coilStrideFamilyLagResiduesNoCollision_of_noWrapSeparated
    {n pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides) :
    coilStrideFamilyLagResiduesNoCollision n pathLength strides := by
  induction strides with
  | nil =>
      unfold coilStrideFamilyLagResiduesNoCollision coilStrideFamilyLagResidueList
      exact List.nodup_nil
  | cons stride strides ih =>
      simp [coilStrideFamilyNoWrapSeparated] at hseparated
      rcases hseparated with ⟨hstride, hheadBound, htailInfo, htailSeparated⟩
      exact coilStrideFamilyLagResiduesNoCollision_cons_of_head_tail_disjoint
        (coilLagResidueList_nodup_of_path_mul_stride_lt_context hstride hheadBound)
        (ih htailSeparated)
        (coilLagResiduesDisjointFromFamily_of_path_mul_head_lt_tail_strides
          hheadBound
          (by
            intro tailStride hmem
            exact (htailInfo tailStride hmem).2.1)
          (by
            intro tailStride hmem
            exact (htailInfo tailStride hmem).2.2))

/-- If every ordered no-wrap-separated stride starts beyond the local window,
then local-window lags are disjoint from the full stride-family residue block. -/
theorem localCoilLagCandidatesDisjoint_of_noWrapSeparated_of_window_lt_all_strides
    {n window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride) :
    localCoilLagCandidatesDisjoint n window pathLength strides := by
  induction strides with
  | nil =>
      unfold localCoilLagCandidatesDisjoint coilStrideFamilyLagResidueList
      rw [List.disjoint_left]
      intro _ _ hcoil
      cases hcoil
  | cons stride strides ih =>
      simp [coilStrideFamilyNoWrapSeparated] at hseparated
      rcases hseparated with ⟨_hstride, hheadBound, _htailInfo, htailSeparated⟩
      unfold localCoilLagCandidatesDisjoint
      rw [List.disjoint_left]
      intro lag hlocalMem hcoil
      have hlocal : localLagReach window lag := by
        rwa [mem_localLagCandidateList_iff] at hlocalMem
      change lag ∈ coilLagResidueList n stride pathLength ++
        coilStrideFamilyLagResidueList n pathLength strides at hcoil
      rw [List.mem_append] at hcoil
      rcases hcoil with hhead | htail
      · unfold coilLagResidueList at hhead
        rw [List.mem_map] at hhead
        rcases hhead with ⟨step, hstepMem, hlag⟩
        have hstepPos : 1 ≤ step := by
          rw [List.mem_range'] at hstepMem
          rcases hstepMem with ⟨i, _hi, hstep⟩
          subst step
          omega
        have hstepLe : step ≤ pathLength := by
          rw [List.mem_range'] at hstepMem
          rcases hstepMem with ⟨i, hi, hstep⟩
          subst step
          omega
        have hstepBound : step * stride < n :=
          lt_of_le_of_lt (Nat.mul_le_mul_right stride hstepLe) hheadBound
        have hlag_eq : lag = step * stride := by
          symm
          simpa [Nat.mod_eq_of_lt hstepBound] using hlag
        have hstride_le : stride ≤ step * stride := by
          calc
            stride = 1 * stride := by rw [Nat.one_mul]
            _ ≤ step * stride := Nat.mul_le_mul_right stride hstepPos
        have hlag_gt : window < lag := by
          rw [hlag_eq]
          exact lt_of_lt_of_le (hwindow stride (by simp)) hstride_le
        exact (not_le_of_gt hlag_gt) hlocal.2
      · have htailDisjoint :
            localCoilLagCandidatesDisjoint n window pathLength strides :=
          ih htailSeparated (by
            intro tailStride hmem
            exact hwindow tailStride (by simp [hmem]))
        unfold localCoilLagCandidatesDisjoint at htailDisjoint
        rw [List.disjoint_left] at htailDisjoint
        exact htailDisjoint hlocalMem htail

/-- A no-wrap single stride above the local window is disjoint from local lags. -/
theorem localCoilLagCandidatesDisjoint_singleton_of_window_lt_stride_of_path_mul_stride_lt_context
    {n window stride pathLength : Nat}
    (hwindow : window < stride)
    (hbound : pathLength * stride < n) :
    localCoilLagCandidatesDisjoint n window pathLength [stride] := by
  unfold localCoilLagCandidatesDisjoint coilStrideFamilyLagResidueList
  rw [List.disjoint_left]
  intro lag hlocal hcoil
  rw [mem_localLagCandidateList_iff] at hlocal
  simp [coilStrideFamilyLagResidueList] at hcoil
  unfold coilLagResidueList at hcoil
  rw [List.mem_map] at hcoil
  rcases hcoil with ⟨step, hstepmem, hlag⟩
  have hstep_pos : 1 ≤ step := by
    rw [List.mem_range'] at hstepmem
    rcases hstepmem with ⟨i, _hi, hstep⟩
    subst step
    omega
  have hstep_le : step ≤ pathLength := by
    rw [List.mem_range'] at hstepmem
    rcases hstepmem with ⟨i, hi, hstep⟩
    subst step
    omega
  have hstep_bound : step * stride < n :=
    lt_of_le_of_lt (Nat.mul_le_mul_right stride hstep_le) hbound
  have hlag_eq : lag = step * stride := by
    symm
    simpa [Nat.mod_eq_of_lt hstep_bound] using hlag
  have hstride_le : stride ≤ step * stride := by
    calc
      stride = 1 * stride := by rw [Nat.one_mul]
      _ ≤ step * stride := Nat.mul_le_mul_right stride hstep_pos
  have hlag_gt : window < lag := by
    rw [hlag_eq]
    exact lt_of_lt_of_le hwindow hstride_le
  exact (not_le_of_gt hlag_gt) hlocal.2

/-- A constructive lag no-collision certificate.

If the stride-family residue block has no duplicates and the local-window lags
are disjoint from those residues, then the full theorem-side lag-candidate list
has no duplicates. -/
theorem hybridFamilyLagCandidatesNoCollision_of_coil_noCollision_of_local_coil_disjoint
    {n window pathLength : Nat} {strides : List Nat}
    (hcoil :
      coilStrideFamilyLagResiduesNoCollision n pathLength strides)
    (hdisjoint :
      localCoilLagCandidatesDisjoint n window pathLength strides) :
    hybridFamilyLagCandidatesNoCollision n window pathLength strides := by
  unfold hybridFamilyLagCandidatesNoCollision hybridFamilyLagCandidateList
  unfold coilStrideFamilyLagResiduesNoCollision at hcoil
  unfold localCoilLagCandidatesDisjoint at hdisjoint
  exact (List.nodup_range' (s := 1) (n := window)).append hcoil hdisjoint

/-- Ordered no-wrap separation plus a local-window lower bound gives full
duplicate-free theorem-side lag candidates. -/
theorem hybridFamilyLagCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides
    {n window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride) :
    hybridFamilyLagCandidatesNoCollision n window pathLength strides :=
  hybridFamilyLagCandidatesNoCollision_of_coil_noCollision_of_local_coil_disjoint
    (coilStrideFamilyLagResiduesNoCollision_of_noWrapSeparated hseparated)
    (localCoilLagCandidatesDisjoint_of_noWrapSeparated_of_window_lt_all_strides
      hseparated hwindow)

/-- Concrete no-wrap single-stride sufficient condition for lag no-collision. -/
theorem hybridFamilyLagCandidatesNoCollision_singleton_of_window_lt_stride_of_path_mul_stride_lt_context
    {n window stride pathLength : Nat}
    (hwindow : window < stride)
    (hbound : pathLength * stride < n) :
    hybridFamilyLagCandidatesNoCollision n window pathLength [stride] := by
  exact hybridFamilyLagCandidatesNoCollision_of_coil_noCollision_of_local_coil_disjoint
    (coilStrideFamilyLagResiduesNoCollision_singleton_of_path_mul_stride_lt_context
      (n := n) (stride := stride) (pathLength := pathLength)
      (Nat.lt_of_le_of_lt (Nat.zero_le window) hwindow) hbound)
    (localCoilLagCandidatesDisjoint_singleton_of_window_lt_stride_of_path_mul_stride_lt_context
      (n := n) (window := window) (stride := stride) (pathLength := pathLength)
      hwindow hbound)

/-- A constructive query no-collision certificate.

If lag candidates are duplicate-free and query predecessor indexing is
injective on those generated lags, then the query-indexed candidate list is
also duplicate-free. -/
theorem hybridFamilyQueryCandidatesNoCollision_of_lag_noCollision_of_predecessor_injective
    {n query window pathLength : Nat} {strides : List Nat}
    (hnoCollision :
      hybridFamilyLagCandidatesNoCollision n window pathLength strides)
    (hinjective :
      hybridFamilyPredecessorInjectiveOnLagCandidates n query window pathLength strides) :
    hybridFamilyQueryCandidatesNoCollision n query window pathLength strides := by
  unfold hybridFamilyQueryCandidatesNoCollision hybridFamilyQueryCandidateList
  unfold hybridFamilyLagCandidatesNoCollision at hnoCollision
  unfold hybridFamilyPredecessorInjectiveOnLagCandidates at hinjective
  exact hnoCollision.map_on hinjective

/-- Ordered no-wrap separation plus predecessor injectivity gives
duplicate-free query-indexed candidates. -/
theorem hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective
    {n query window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride)
    (hinjective :
      hybridFamilyPredecessorInjectiveOnLagCandidates n query window pathLength strides) :
    hybridFamilyQueryCandidatesNoCollision n query window pathLength strides :=
  hybridFamilyQueryCandidatesNoCollision_of_lag_noCollision_of_predecessor_injective
    (hybridFamilyLagCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides
      hseparated hwindow)
    hinjective

/-- A local window below the context length is enough to make predecessor
indexing injective on all theorem-side lag candidates. -/
theorem hybridFamilyPredecessorInjectiveOnLagCandidates_of_window_lt_context
    {n query window pathLength : Nat} {strides : List Nat}
    (hcontext : window < n) :
    hybridFamilyPredecessorInjectiveOnLagCandidates n query window pathLength strides := by
  unfold hybridFamilyPredecessorInjectiveOnLagCandidates
  intro left hleft right hright heq
  exact predecessorIndex_injective_of_lag_lt_context
    (mem_hybridFamilyLagCandidateList_lt_context_of_window_lt_context hcontext hleft)
    (mem_hybridFamilyLagCandidateList_lt_context_of_window_lt_context hcontext hright)
    heq

/-- Ordered no-wrap separation plus an in-context local window gives
duplicate-free query-indexed candidates without an abstract injectivity
assumption. -/
theorem hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_window_lt_context
    {n query window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride)
    (hcontext : window < n) :
    hybridFamilyQueryCandidatesNoCollision n query window pathLength strides :=
  hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective
    hseparated hwindow
    (hybridFamilyPredecessorInjectiveOnLagCandidates_of_window_lt_context hcontext)

/-- If the theorem-side lag-candidate list has no duplicate lag candidates, its
exact deduplicated count equals the raw candidate budget. -/
theorem hybridFamilyUniqueLagCandidateCount_eq_raw_of_noCollision
    {n window pathLength : Nat} {strides : List Nat}
    (hnoCollision :
      hybridFamilyLagCandidatesNoCollision n window pathLength strides) :
    hybridFamilyUniqueLagCandidateCount n window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyUniqueLagCandidateCount hybridFamilyLagCandidatesNoCollision at *
  rw [List.Nodup.dedup hnoCollision]
  exact hybridFamilyLagCandidateList_length n window pathLength strides

/-- Exact raw-budget survival criterion for theorem-side lag candidates.

The deduplicated lag-candidate count equals the raw local+stride-family budget
if and only if the theorem-side lag-candidate list has no duplicates. This is
the necessary-and-sufficient endpoint behind sparse-plan budget certificates:
any budget loss is exactly a duplicate lag candidate. -/
theorem hybridFamilyUniqueLagCandidateCount_eq_raw_iff_noCollision
    {n window pathLength : Nat} {strides : List Nat} :
    hybridFamilyUniqueLagCandidateCount n window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides ↔
      hybridFamilyLagCandidatesNoCollision n window pathLength strides := by
  unfold hybridFamilyUniqueLagCandidateCount hybridFamilyLagCandidatesNoCollision
  rw [← hybridFamilyLagCandidateList_length n window pathLength strides]
  constructor
  · intro hlen
    have hsub :=
      List.dedup_sublist (hybridFamilyLagCandidateList n window pathLength strides)
    have heq :
        (hybridFamilyLagCandidateList n window pathLength strides).dedup =
          hybridFamilyLagCandidateList n window pathLength strides :=
      hsub.eq_of_length hlen
    exact (List.dedup_eq_self).1 heq
  · intro hnodup
    rw [List.Nodup.dedup hnodup]

/-- Ordered no-wrap separation plus a local-window lower bound makes the exact
lag-candidate count equal the raw sparse-attention budget. -/
theorem hybridFamilyUniqueLagCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides
    {n window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride) :
    hybridFamilyUniqueLagCandidateCount n window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides :=
  hybridFamilyUniqueLagCandidateCount_eq_raw_of_noCollision
    (hybridFamilyLagCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides
      hseparated hwindow)

/-- If the theorem-side query-indexed candidate list has no duplicate
predecessor candidates, its exact deduplicated count equals the raw candidate
budget. -/
theorem hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noCollision
    {n query window pathLength : Nat} {strides : List Nat}
    (hnoCollision :
      hybridFamilyQueryCandidatesNoCollision n query window pathLength strides) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides := by
  unfold hybridFamilyUniqueQueryCandidateCount hybridFamilyQueryCandidatesNoCollision at *
  rw [List.Nodup.dedup hnoCollision]
  exact hybridFamilyQueryCandidateList_length n query window pathLength strides

/-- Exact raw-budget survival criterion for query-indexed candidates.

The deduplicated query-candidate count equals the raw local+stride-family
budget if and only if the theorem-side query-indexed candidate list has no
duplicates. This is the query-level version of the sparse-plan budget contract. -/
theorem hybridFamilyUniqueQueryCandidateCount_eq_raw_iff_noCollision
    {n query window pathLength : Nat} {strides : List Nat} :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides ↔
      hybridFamilyQueryCandidatesNoCollision n query window pathLength strides := by
  unfold hybridFamilyUniqueQueryCandidateCount hybridFamilyQueryCandidatesNoCollision
  rw [← hybridFamilyQueryCandidateList_length n query window pathLength strides]
  constructor
  · intro hlen
    have hsub :=
      List.dedup_sublist (hybridFamilyQueryCandidateList n query window pathLength strides)
    have heq :
        (hybridFamilyQueryCandidateList n query window pathLength strides).dedup =
          hybridFamilyQueryCandidateList n query window pathLength strides :=
      hsub.eq_of_length hlen
    exact (List.dedup_eq_self).1 heq
  · intro hnodup
    rw [List.Nodup.dedup hnodup]

/-- Ordered no-wrap separation plus predecessor injectivity makes the exact
query-candidate count equal the raw sparse-attention budget. -/
theorem hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective
    {n query window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride)
    (hinjective :
      hybridFamilyPredecessorInjectiveOnLagCandidates n query window pathLength strides) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides :=
  hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noCollision
    (hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective
      hseparated hwindow hinjective)

/-- Ordered no-wrap separation plus an in-context local window makes the exact
query-candidate count equal the raw sparse-attention budget. -/
theorem hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides_of_window_lt_context
    {n query window pathLength : Nat} {strides : List Nat}
    (hseparated : coilStrideFamilyNoWrapSeparated n pathLength strides)
    (hwindow : ∀ stride ∈ strides, window < stride)
    (hcontext : window < n) :
    hybridFamilyUniqueQueryCandidateCount n query window pathLength strides =
      hybridFamilyRawCandidateBudget window pathLength strides :=
  hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noCollision
    (hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_window_lt_context
      hseparated hwindow hcontext)

/-- Query-candidate membership is exactly membership after mapping some
generated lag through the predecessor-index map. -/
theorem mem_hybridFamilyQueryCandidateList_iff_exists_lag
    {n query window pathLength candidate : Nat} {strides : List Nat} :
    candidate ∈ hybridFamilyQueryCandidateList n query window pathLength strides ↔
      ∃ lag, lag ∈ hybridFamilyLagCandidateList n window pathLength strides ∧
        predecessorIndex n query lag = candidate := by
  unfold hybridFamilyQueryCandidateList
  rw [List.mem_map]

/-- Any in-context lag reached by the local+stride-family plan maps to a
query-indexed predecessor candidate. -/
theorem predecessorIndex_mem_hybridFamilyQueryCandidateList_of_reach
    {n query window pathLength lag : Nat} {strides : List Nat}
    (hcontext : lag < n)
    (hreach : hybridFamilyLagReach n window pathLength lag strides) :
    predecessorIndex n query lag ∈
      hybridFamilyQueryCandidateList n query window pathLength strides := by
  rw [mem_hybridFamilyQueryCandidateList_iff_exists_lag]
  exact ⟨lag, (mem_hybridFamilyLagCandidateList_iff hcontext).2 hreach, rfl⟩

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

/-- Concrete default sparse-plan gap certificate used by the executable
stride-family sidecar.

For the default plan `C_120`, local window `4`, path length `3`, and strides
`[7,13]`, lag `5` is beyond the local window and is not equal to any admitted
stride step modulo `120`. -/
theorem hybridFamilyLagGap_default_120_4_3_7_13_lag5 :
    ¬ hybridFamilyLagReach 120 4 3 5 [7, 13] := by
  apply hybridFamilyLagGap_of_above_window_and_forall_stride_step_ne
  · omega
  · intro stride hmem step hpos hstep
    simp at hmem
    rcases hmem with hstride | hstride <;> subst stride
    · have hstep_cases : step = 1 ∨ step = 2 ∨ step = 3 := by omega
      rcases hstep_cases with rfl | rfl | rfl <;> omega
    · have hstep_cases : step = 1 ∨ step = 2 ∨ step = 3 := by omega
      rcases hstep_cases with rfl | rfl | rfl <;> omega

/-- The default `C_120`, local-window `4`, path-length `3`, strides `[7,13]`
sparse plan is not complete coverage because lag `5` is a concrete uncovered
positive in-context witness. -/
theorem not_hybridFamilyCoversContext_default_120_4_3_7_13 :
    ¬ hybridFamilyCoversContext 120 4 3 [7, 13] := by
  intro hcover
  exact hybridFamilyLagGap_default_120_4_3_7_13_lag5
    (hcover 5 (by omega) (by omega))

/-- The default sparse-attention plan's finite uncovered-lag list contains the
same concrete gap witness, lag `5`. -/
theorem mem_hybridFamilyUncoveredLagList_default_120_4_3_7_13_lag5 :
    5 ∈ hybridFamilyUncoveredLagList 120 4 3 [7, 13] := by
  exact (mem_hybridFamilyUncoveredLagList_iff).2
    ⟨by omega, by omega, hybridFamilyLagGap_default_120_4_3_7_13_lag5⟩

/-- The default sparse-attention plan's first uncovered lag is exactly `5`. -/
theorem hybridFamilyFirstUncoveredLag_default_120_4_3_7_13_eq_some5 :
    hybridFamilyFirstUncoveredLag 120 4 3 [7, 13] = some 5 := by
  native_decide

/-- The default sparse-attention plan has exactly `109` positive in-context
uncovered lags. This is the finite count reported by the executable sidecar. -/
theorem hybridFamilyUncoveredLagList_default_120_4_3_7_13_length :
    (hybridFamilyUncoveredLagList 120 4 3 [7, 13]).length = 109 := by
  native_decide

/-- The default sparse-attention plan's uncovered-lag interval summary has the
six exact ranges reported by the executable sidecar. -/
theorem hybridFamilyUncoveredLagIntervalList_default_120_4_3_7_13 :
    hybridFamilyUncoveredLagIntervalList 120 4 3 [7, 13] =
      [(5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119)] := by
  native_decide

/-- The default `C_120`, local-window `4`, path-length `3`, strides `[7,13]`
sparse plan has exactly ten theorem-side covered positive lags. -/
theorem hybridFamilyCoveredLagList_default_120_4_3_7_13_length :
    (hybridFamilyCoveredLagList 120 4 3 [7, 13]).length = 10 := by
  native_decide

/-- A compact complete sparse-family fixture has no uncovered positive lags.

For `C_9`, local window `2`, path length `2`, and strides `[3,4,7]`,
the generated lag candidates are exactly `1,2,3,6,4,8,7,5`, covering every
positive in-context lag once. -/
theorem hybridFamilyUncoveredLagList_complete_9_2_2_3_4_7_eq_nil :
    hybridFamilyUncoveredLagList 9 2 2 [3, 4, 7] = [] := by
  native_decide

/-- The compact `C_9` sparse-family fixture is a positive complete-coverage
certificate. -/
theorem hybridFamilyCoversContext_complete_9_2_2_3_4_7 :
    hybridFamilyCoversContext 9 2 2 [3, 4, 7] := by
  exact (hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil).2
    hybridFamilyUncoveredLagList_complete_9_2_2_3_4_7_eq_nil

/-- The compact complete sparse-family fixture has an empty uncovered-interval
summary, matching its empty uncovered-lag list. -/
theorem hybridFamilyUncoveredLagIntervalList_complete_9_2_2_3_4_7_eq_nil :
    hybridFamilyUncoveredLagIntervalList 9 2 2 [3, 4, 7] = [] := by
  native_decide

/-- The compact `C_9` sparse-family fixture preserves the raw lag-candidate
budget after deduplication. -/
theorem hybridFamilyUniqueLagCandidateCount_complete_9_2_2_3_4_7_eq_raw :
    hybridFamilyUniqueLagCandidateCount 9 2 2 [3, 4, 7] =
      hybridFamilyRawCandidateBudget 2 2 [3, 4, 7] := by
  native_decide

/-- The compact `C_9` sparse-family fixture preserves the raw query-candidate
budget after deduplication. -/
theorem hybridFamilyUniqueQueryCandidateCount_complete_9_2_2_3_4_7_eq_raw :
    hybridFamilyUniqueQueryCandidateCount 9 0 2 2 [3, 4, 7] =
      hybridFamilyRawCandidateBudget 2 2 [3, 4, 7] := by
  native_decide

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
