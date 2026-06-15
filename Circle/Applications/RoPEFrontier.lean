import Circle.Applications.RoPEGeneratedCertificates

/-!
# Public RoPE frontier wrappers

This module packages generated standard-channel RoPE certificates into stable
frontier-facing theorem names. The generated file remains the source of the
large interval tables; this file only exposes smaller contracts that downstream
tools and prose can cite without depending on generated theorem naming patterns.
-/

namespace Circle.Applications

/-- The current generated standard channel-0 frontier gives a context-range
margin bracket.

For any requested context up to the D19 generated horizon, the D19 certified
margin `1/328459` holds by context monotonicity. Once the context contains the
obstruction gap `103993`, no advertised margin at or above `1/328458` can hold.
This is still a one-channel standard channel-0 theorem, not a full all-channel
standard RoPE bank theorem. -/
theorem ropeStandardChannel0D19_contextRange_margin_bracket
    {context : Nat}
    (hcontext_min : 103993 < context)
    (hcontext_max : context ≤ ropeStandardChannel0D19SeedContext) :
    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
      ropeStandardChannel0D19SeedMargin context ∧
      ∀ margin : ℝ, (1 : ℝ) / 328458 ≤ margin →
        ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin context := by
  exact
    ropeTurnRatioFiniteMargin_contextRange_bracket_of_obstruction
      (turnRatio := ropeStandardChannel0TurnRatio)
      (provedMargin := ropeStandardChannel0D19SeedMargin)
      (obstructionMargin := (1 : ℝ) / 328458)
      (certifiedContext := ropeStandardChannel0D19SeedContext)
      (obstructionGap := 103993)
      (obstructionTurns := 16551)
      ropeStandardChannel0D19Seed_turnRatioFiniteMargin
      (by norm_num)
      ropeStandardChannel0_gap103993_error_lt_one_over_328458
      hcontext_min hcontext_max

/-- The current generated standard channel-0 frontier answers request-level
margin brackets.

For any requested context in the D19 obstruction range, every requested margin
at or below the D19 proved margin `1/328459` holds by monotonicity, while every
advertised margin at or above `1/328458` is impossible. This is the
ML-facing request contract used by the Python certifier; it is still a
one-channel standard channel-0 theorem, not a full all-channel standard RoPE
bank theorem. -/
theorem ropeStandardChannel0D19_contextRange_request_margin_bracket
    {context : Nat} {requestedMargin : ℝ}
    (hcontext_min : 103993 < context)
    (hcontext_max : context ≤ ropeStandardChannel0D19SeedContext) :
    (requestedMargin ≤ ropeStandardChannel0D19SeedMargin →
      ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
        requestedMargin context) ∧
      ((1 : ℝ) / 328458 ≤ requestedMargin →
        ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
          requestedMargin context) := by
  exact
    ropeTurnRatioFiniteMargin_contextRange_request_bracket_of_obstruction
      (turnRatio := ropeStandardChannel0TurnRatio)
      (provedMargin := ropeStandardChannel0D19SeedMargin)
      (obstructionMargin := (1 : ℝ) / 328458)
      (requestedMargin := requestedMargin)
      (certifiedContext := ropeStandardChannel0D19SeedContext)
      (obstructionGap := 103993)
      (obstructionTurns := 16551)
      ropeStandardChannel0D19Seed_turnRatioFiniteMargin
      (by norm_num)
      ropeStandardChannel0_gap103993_error_lt_one_over_328458
      hcontext_min hcontext_max

/-- The D19 proved margin threshold is strictly below the D19 obstruction
threshold.

This theorem is intentionally small, but it is report-facing: the Python
request classifier can cite it when explaining that the proved branch
`requestedMargin ≤ 1/328459` is separated from the impossible branch
`1/328458 ≤ requestedMargin`. -/
theorem ropeStandardChannel0D19_request_margin_thresholds_ordered :
    ropeStandardChannel0D19SeedMargin < (1 : ℝ) / 328458 := by
  norm_num [ropeStandardChannel0D19SeedMargin]

/-- The D19 request classifier's proved and impossible margin branches are
disjoint.

This is the consistency guard for the ML-facing certificate: no requested
margin can be both at most the proved D19 threshold and at least the D19
obstruction threshold. -/
theorem ropeStandardChannel0D19_request_margin_branches_disjoint
    {requestedMargin : ℝ} :
    ¬ (requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
      (1 : ℝ) / 328458 ≤ requestedMargin) := by
  intro h
  exact
    (not_le_of_gt ropeStandardChannel0D19_request_margin_thresholds_ordered)
      (le_trans h.2 h.1)

/-- A requested margin is in the D19 classifier's undecided open interval exactly
when neither the proved branch nor the impossible branch applies.

This is a report-facing theorem for the `undecided_margin_gap` status: the gap is
not an arbitrary fallback, but precisely the interval between the proved D19
threshold and the obstruction threshold. -/
theorem ropeStandardChannel0D19_request_margin_open_gap_iff_unclassified
    {requestedMargin : ℝ} :
    (¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
      ¬ (1 : ℝ) / 328458 ≤ requestedMargin) ↔
      ropeStandardChannel0D19SeedMargin < requestedMargin ∧
        requestedMargin < (1 : ℝ) / 328458 := by
  constructor
  · intro h
    exact ⟨lt_of_not_ge h.1, lt_of_not_ge h.2⟩
  · intro h
    exact ⟨not_le_of_gt h.1, not_le_of_gt h.2⟩

/-- Every requested margin falls into exactly one of the D19 classifier regions:
proved threshold, impossible threshold, or the undecided open interval.

The disjointness theorem rules out overlap between the first two branches; this
theorem supplies the complementary exhaustiveness fact used by the public
request-status report. -/
theorem ropeStandardChannel0D19_request_margin_trichotomy
    (requestedMargin : ℝ) :
    requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∨
      (1 : ℝ) / 328458 ≤ requestedMargin ∨
        (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
          requestedMargin < (1 : ℝ) / 328458) := by
  by_cases hproved : requestedMargin ≤ ropeStandardChannel0D19SeedMargin
  · exact Or.inl hproved
  · by_cases himpossible : (1 : ℝ) / 328458 ≤ requestedMargin
    · exact Or.inr (Or.inl himpossible)
    · exact Or.inr (Or.inr
        ((ropeStandardChannel0D19_request_margin_open_gap_iff_unclassified).1
          ⟨hproved, himpossible⟩))

end Circle.Applications
