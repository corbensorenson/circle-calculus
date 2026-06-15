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
  constructor
  · exact
      ropeTurnRatioFiniteMargin_mono_context
        (turnRatio := ropeStandardChannel0TurnRatio)
        (margin := ropeStandardChannel0D19SeedMargin)
        hcontext_max
        ropeStandardChannel0D19Seed_turnRatioFiniteMargin
  · intro margin hmargin
    exact
      not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993
        (context := context) (margin := margin) hcontext_min hmargin

end Circle.Applications
