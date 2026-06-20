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

/-- Inside the D19 context range, the request classifier has exactly one
semantic branch.

Margins in the proved branch come with a finite-margin proof; margins in the
impossible branch come with a finite-margin refutation; margins in the open gap
are explicitly the undecided region and are disjoint from the two theorem-backed
branches. -/
theorem ropeStandardChannel0D19_contextRange_request_margin_semantic_trichotomy
    {context : Nat} {requestedMargin : ℝ}
    (hcontext_min : 103993 < context)
    (hcontext_max : context ≤ ropeStandardChannel0D19SeedContext) :
    (requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
      ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
        requestedMargin context ∧
      ¬ (1 : ℝ) / 328458 ≤ requestedMargin ∧
      ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
        requestedMargin < (1 : ℝ) / 328458)) ∨
      ((1 : ℝ) / 328458 ≤ requestedMargin ∧
        ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
          requestedMargin context ∧
        ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
        ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
          requestedMargin < (1 : ℝ) / 328458)) ∨
      ((ropeStandardChannel0D19SeedMargin < requestedMargin ∧
        requestedMargin < (1 : ℝ) / 328458) ∧
        ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
        ¬ (1 : ℝ) / 328458 ≤ requestedMargin) := by
  have hbracket :=
    ropeStandardChannel0D19_contextRange_request_margin_bracket
      (context := context) (requestedMargin := requestedMargin)
      hcontext_min hcontext_max
  rcases
      ropeStandardChannel0D19_request_margin_trichotomy requestedMargin with
    hproved | himpossible_or_gap
  · have hfinite := hbracket.1 hproved
    have hnot_impossible : ¬ (1 : ℝ) / 328458 ≤ requestedMargin := by
      intro himpossible
      exact
        ropeStandardChannel0D19_request_margin_branches_disjoint
          ⟨hproved, himpossible⟩
    have hnot_gap :
        ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
          requestedMargin < (1 : ℝ) / 328458) := by
      intro hgap
      exact (not_le_of_gt hgap.1) hproved
    exact Or.inl ⟨hproved, hfinite, hnot_impossible, hnot_gap⟩
  · rcases himpossible_or_gap with himpossible | hgap
    · have hnot_finite := hbracket.2 himpossible
      have hnot_proved : ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin := by
        intro hproved
        exact
          ropeStandardChannel0D19_request_margin_branches_disjoint
            ⟨hproved, himpossible⟩
      have hnot_gap :
          ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
            requestedMargin < (1 : ℝ) / 328458) := by
        intro hgap
        exact (not_le_of_gt hgap.2) himpossible
      exact Or.inr (Or.inl ⟨himpossible, hnot_finite, hnot_proved, hnot_gap⟩)
    · have hnot_proved :
          ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin :=
        not_le_of_gt hgap.1
      have hnot_impossible : ¬ (1 : ℝ) / 328458 ≤ requestedMargin :=
        not_le_of_gt hgap.2
      exact Or.inr (Or.inr ⟨hgap, hnot_proved, hnot_impossible⟩)

/-- The D19 proved request branch transfers to a first-channel finite bank.

If a real-phase bank has standard channel 0 as its first channel, then every
request at or below the D19 proved margin and inside the D19 certified horizon
inherits a no-near-turn bank conclusion. This is the useful proved-branch bank
contract. It intentionally has no impossible-branch converse: a one-channel
obstruction does not prove that a whole bank has an all-channel collision. -/
theorem ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext left right : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D19SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D19SeedMargin)
    (hleft : left < right) (hright : right < requestedContext)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ¬ ropeRealPhaseBankNearTurn
      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
      fullTurn tolerance left right :=
  not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed_cons
    hcontext hmargin_le hleft hright hfull_pos htolerance

/-- The D19 proved request branch gives a context-wide first-channel bank
guarantee.

This is the user-facing form of the bank bridge: after the context, margin,
full-turn, and tolerance preconditions are fixed, every ordered unequal pair
inside the requested context is ruled out as a near-turn collision. It is still
only a one-separating-channel guarantee based on standard channel 0. -/
theorem ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn_onContext
    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}
    {requestedContext : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D19SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D19SeedMargin)
    (hfull_pos : 0 < fullTurn)
    (htolerance : tolerance < fullTurn * requestedMargin) :
    ∀ {left right : Nat}, left < right → right < requestedContext →
      ¬ ropeRealPhaseBankNearTurn
        ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)
        fullTurn tolerance left right := by
  intro left right hleft hright
  exact
    ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn
      hcontext hmargin_le hleft hright hfull_pos htolerance

/-- Standard channel 0 has radian frequency `1` when the full turn is `2π`.

This algebra bridge lets downstream contracts cite the ordinary RoPE radian
bank shape `(1 :: extraFrequencies)` instead of the normalized expression
`(1 / (2π)) * (2π) :: extraFrequencies`. -/
theorem ropeStandardChannel0TurnRatio_mul_two_pi :
    ropeStandardChannel0TurnRatio * (2 * Real.pi) = 1 := by
  have htwo_pi_ne : (2 * Real.pi : ℝ) ≠ 0 := ne_of_gt Real.two_pi_pos
  rw [ropeStandardChannel0TurnRatio]
  field_simp [htwo_pi_ne]

/-- The D19 proved request branch in ordinary radian RoPE bank form.

For a finite real-phase bank whose first frequency is the standard radian
channel-0 frequency `1`, with full turn `2π`, every requested context inside
the D19 horizon and every requested margin at or below `1/328459` inherits the
context-wide no-near-turn guarantee. This is still a one-separating-channel
contract, not an independent margin theorem for every channel. -/
theorem ropeStandardChannel0D19_proved_request_radianFirstChannel_bank_noNearTurn_onContext
    {extraFrequencies : List ℝ} {requestedMargin tolerance : ℝ}
    {requestedContext : Nat}
    (hcontext : requestedContext ≤ ropeStandardChannel0D19SeedContext)
    (hmargin_le : requestedMargin ≤ ropeStandardChannel0D19SeedMargin)
    (htolerance : tolerance < (2 * Real.pi) * requestedMargin) :
    ∀ {left right : Nat}, left < right → right < requestedContext →
      ¬ ropeRealPhaseBankNearTurn
        ((1 : ℝ) :: extraFrequencies) (2 * Real.pi) tolerance left right := by
  intro left right hleft hright
  simpa [ropeStandardChannel0TurnRatio_mul_two_pi] using
    (ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn
      (extraFrequencies := extraFrequencies)
      (fullTurn := 2 * Real.pi)
      (requestedMargin := requestedMargin)
      (tolerance := tolerance)
      (requestedContext := requestedContext)
      (left := left)
      (right := right)
      hcontext hmargin_le hleft hright Real.two_pi_pos htolerance)

/-- The D19 request classifier with the ordinary radian first-channel bank
consequence attached.

Inside the D19 context range, this theorem packages the three public request
branches in the form a downstream contract consumes: the proved branch carries a
context-wide no-near-turn guarantee for banks whose first radian frequency is
`1`; the impossible branch refutes only the one-channel finite-margin predicate;
and the open interval remains explicitly undecided. This is still not a
full-bank converse or an all-channel RoPE margin theorem. -/
theorem ropeStandardChannel0D19_contextRange_radianFirstChannel_request_semantic_trichotomy
    {extraFrequencies : List ℝ} {requestedContext : Nat}
    {requestedMargin tolerance : ℝ}
    (hcontext_min : 103993 < requestedContext)
    (hcontext_max : requestedContext ≤ ropeStandardChannel0D19SeedContext)
    (htolerance : tolerance < (2 * Real.pi) * requestedMargin) :
    (requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
      (∀ {left right : Nat}, left < right → right < requestedContext →
        ¬ ropeRealPhaseBankNearTurn
          ((1 : ℝ) :: extraFrequencies) (2 * Real.pi) tolerance left right) ∧
      ¬ (1 : ℝ) / 328458 ≤ requestedMargin ∧
      ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
        requestedMargin < (1 : ℝ) / 328458)) ∨
      ((1 : ℝ) / 328458 ≤ requestedMargin ∧
        ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio
          requestedMargin requestedContext ∧
        ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
        ¬ (ropeStandardChannel0D19SeedMargin < requestedMargin ∧
          requestedMargin < (1 : ℝ) / 328458)) ∨
      ((ropeStandardChannel0D19SeedMargin < requestedMargin ∧
        requestedMargin < (1 : ℝ) / 328458) ∧
        ¬ requestedMargin ≤ ropeStandardChannel0D19SeedMargin ∧
        ¬ (1 : ℝ) / 328458 ≤ requestedMargin) := by
  rcases
      ropeStandardChannel0D19_contextRange_request_margin_semantic_trichotomy
        (context := requestedContext) (requestedMargin := requestedMargin)
        hcontext_min hcontext_max with
    hproved | himpossible_or_gap
  · rcases hproved with
      ⟨hmargin_le, _hfinite, hnot_impossible, hnot_gap⟩
    have hbank :
        ∀ {left right : Nat}, left < right → right < requestedContext →
          ¬ ropeRealPhaseBankNearTurn
            ((1 : ℝ) :: extraFrequencies) (2 * Real.pi) tolerance left right :=
      ropeStandardChannel0D19_proved_request_radianFirstChannel_bank_noNearTurn_onContext
        (extraFrequencies := extraFrequencies)
        (requestedMargin := requestedMargin)
        (tolerance := tolerance)
        (requestedContext := requestedContext)
        hcontext_max hmargin_le htolerance
    exact Or.inl ⟨hmargin_le, hbank, hnot_impossible, hnot_gap⟩
  · rcases himpossible_or_gap with himpossible | hgap
    · exact Or.inr (Or.inl himpossible)
    · exact Or.inr (Or.inr hgap)

/-- The D19 classifier's undecided open margin interval has the exact rational
width reported by the public Python certificate.

This theorem ties the report field `undecided_margin_interval_width` to the
Lean frontier rather than leaving it as a Python-only arithmetic value. -/
theorem ropeStandardChannel0D19_request_margin_open_gap_width :
    (1 : ℝ) / 328458 - ropeStandardChannel0D19SeedMargin =
      (1 : ℝ) / 107884986222 := by
  norm_num [ropeStandardChannel0D19SeedMargin]

end Circle.Applications
