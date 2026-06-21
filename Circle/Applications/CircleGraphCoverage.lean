import Circle.Applications.CircleTransformer

/-!
# Circle graph coverage wrappers

The sparse-attention certifier already proves the finite coverage facts in
`Circle.Applications.CircleTransformer`. This module gives the same theorem
spine graph-facing names: vertices are positions on `C_n`, local windows and
stride coils are directed lag generators, and coverage is reachability of every
positive dependency lag.

No model-quality, speed, memory, or long-context claim is made here.
-/

namespace Circle.Applications

/-- Graph-facing name for the number of vertices reached by one circular stride. -/
noncomputable abbrev circleGraphStrideReach (n stride : Nat) : Nat :=
  attentionReach n stride

/-- Graph-facing name for full coverage by one circular stride. -/
abbrev circleGraphStrideFullCoverage (n stride : Nat) : Prop :=
  stridedHeadFullCoverage n stride

/-- Graph-facing name for local-window lag reachability. -/
abbrev circleGraphLocalLagReach (window lag : Nat) : Prop :=
  localLagReach window lag

/-- Graph-facing name for one stride coil reaching a lag. -/
abbrev circleGraphStrideLagReach (n stride pathLength lag : Nat) : Prop :=
  coilLagReach n stride pathLength lag

/-- Graph-facing name for local-window plus stride-family lag reachability. -/
abbrev circleGraphFamilyLagReach
    (n window pathLength lag : Nat) (strides : List Nat) : Prop :=
  hybridFamilyLagReach n window pathLength lag strides

/-- Graph-facing name for complete positive-lag coverage. -/
abbrev circleGraphFamilyCovers
    (n window pathLength : Nat) (strides : List Nat) : Prop :=
  hybridFamilyCoversContext n window pathLength strides

/-- Graph-facing uncovered positive-lag list. -/
abbrev circleGraphUncoveredLagList
    (n window pathLength : Nat) (strides : List Nat) : List Nat :=
  hybridFamilyUncoveredLagList n window pathLength strides

/-- Graph-facing covered positive-lag list. -/
abbrev circleGraphCoveredLagList
    (n window pathLength : Nat) (strides : List Nat) : List Nat :=
  hybridFamilyCoveredLagList n window pathLength strides

/-- One circular stride reaches exactly `n / gcd n stride` vertices. -/
theorem circleGraphStrideReach_eq_div_gcd {n stride : Nat} (hn : n ≠ 0) :
    circleGraphStrideReach n stride = n / Nat.gcd n stride :=
  attentionReach_eq_div_gcd hn

/-- One circular stride covers the whole finite circle exactly when it is
coprime to the context length. -/
theorem circleGraphStrideFullCoverage_iff_coprime {n stride : Nat} (hn : n ≠ 0) :
    circleGraphStrideFullCoverage n stride ↔ Nat.gcd n stride = 1 :=
  stridedHead_fullCoverage_iff_coprime hn

/-- A local window covers every positive dependency lag exactly when it reaches
the final positive lag `n - 1`. -/
theorem circleGraphLocalWindowCovers_iff_context_sub_one_le
    {n window : Nat} :
    localWindowCoversContext n window ↔ n - 1 ≤ window :=
  localWindowCoversContext_iff_context_sub_one_le

/-- A circle graph sparse plan covers the context exactly when its uncovered
positive-lag list is empty. -/
theorem circleGraphFamilyCovers_iff_uncoveredLagList_eq_nil
    {n window pathLength : Nat} {strides : List Nat} :
    circleGraphFamilyCovers n window pathLength strides ↔
      circleGraphUncoveredLagList n window pathLength strides = [] :=
  hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil

/-- A circle graph sparse plan covers the context exactly when its covered
positive-lag list has length `n - 1`. -/
theorem circleGraphFamilyCovers_iff_coveredLagList_length_eq_context_sub_one
    {n window pathLength : Nat} {strides : List Nat} :
    circleGraphFamilyCovers n window pathLength strides ↔
      (circleGraphCoveredLagList n window pathLength strides).length = n - 1 :=
  hybridFamilyCoversContext_iff_coveredLagList_length_eq_context_sub_one

/-- The compact public sparse-attention fixture covers all positive lags. -/
theorem circleGraphCompleteFixture_9_2_2_3_4_7 :
    circleGraphFamilyCovers 9 2 2 [3, 4, 7] :=
  hybridFamilyCoversContext_complete_9_2_2_3_4_7

end Circle.Applications
