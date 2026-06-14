#!/usr/bin/env python3
"""Generate compressed Lean certificates for large standard RoPE channel-0 plans."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from circle_math.applications.rope_certifier import plan_standard_channel0_interval_bands


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Circle" / "Applications" / "RoPEGeneratedCertificates.lean"


@dataclass(frozen=True)
class GeneratedPlan:
    level: str
    context: int
    margin_denominator: int
    impossible_margin_denominator: int
    obstruction_gap: int
    theorem_start: int
    description: str


PLANS = (
    GeneratedPlan(
        level="D15",
        context=32768,
        margin_denominator=104219,
        impossible_margin_denominator=104218,
        obstruction_gap=710,
        theorem_start=142,
        description="32k",
    ),
    GeneratedPlan(
        level="D16",
        context=65536,
        margin_denominator=104219,
        impossible_margin_denominator=104218,
        obstruction_gap=710,
        theorem_start=148,
        description="64k",
    ),
    GeneratedPlan(
        level="D17",
        context=131072,
        margin_denominator=328459,
        impossible_margin_denominator=328458,
        obstruction_gap=103993,
        theorem_start=156,
        description="128k",
    ),
    GeneratedPlan(
        level="D18",
        context=163840,
        margin_denominator=328459,
        impossible_margin_denominator=328458,
        obstruction_gap=103993,
        theorem_start=162,
        description="160k",
    ),
)


def theorem_id(number: int) -> str:
    return f"AIRA-T{number:04d}"


def render_plan(plan_spec: GeneratedPlan) -> str:
    plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, plan_spec.margin_denominator),
        max_context_length=plan_spec.context,
    )
    if plan.first_uncovered_gap is not None:
        raise RuntimeError(f"{plan_spec.level} plan failed at gap {plan.first_uncovered_gap}")

    lower = plan.lower_turn_ratio_bound
    upper = plan.upper_turn_ratio_bound
    level = plan_spec.level
    compact_name = f"ropeStandardChannel0{level}UniformBands"
    lower_name = f"ropeStandardChannel0{level}Bands"

    lines: list[str] = [
        f"/-- The generated standard channel-0 {plan_spec.description} context. -/",
        f"def ropeStandardChannel0{level}SeedContext : Nat := {plan_spec.context}",
        "",
        f"/-- The advertised margin for the generated standard channel-0 {plan_spec.description} seed. -/",
        f"noncomputable def ropeStandardChannel0{level}SeedMargin : ℝ := 1 / {plan_spec.margin_denominator}",
        "",
        f"/-- Generated d20 compact gap/cell bands for the standard channel-0 {plan_spec.description} seed. -/",
        f"private def {compact_name} : List RopeTurnRatioUniformRationalIntervalBand := [",
    ]
    for band in plan.bands:
        lines.append(
            "  "
            "{ "
            f"startGap := {band.start_gap}, "
            f"endGap := {band.end_gap}, "
            f"cell := {band.cell} "
            "},"
        )
    lines.extend(
        [
            "]",
            "",
            f"/-- Expanded rational bands for the standard channel-0 {plan_spec.description} seed. -/",
            f"private def {lower_name} : List RopeTurnRatioRationalIntervalBand :=",
            "  ropeTurnRatioUniformRationalIntervalBands",
            f"    ({lower} : ℚ)",
            f"    ({upper} : ℚ)",
            f"    {compact_name}",
            "",
            f"private theorem {compact_name}_lowerBound_nonneg :",
            f"    0 <= ({lower} : ℚ) := by",
            "  norm_num",
            "",
            f"private theorem {compact_name}_upperBound_nonneg :",
            f"    0 <= ({upper} : ℚ) := by",
            "  norm_num",
            "",
            f"private theorem {compact_name}_ratEndpointValid :",
            f"    ∀ band, band ∈ {compact_name} ->",
            f"      band.RatEndpointValid ({lower} : ℚ) ({upper} : ℚ)",
            f"        (1 / {plan_spec.margin_denominator} : ℚ) := by",
            "  unfold RopeTurnRatioUniformRationalIntervalBand.RatEndpointValid",
            "  native_decide",
            "",
            f"private theorem {lower_name}_contiguousCover :",
            f"    ropeTurnRatioRationalIntervalBandsContiguousCover {lower_name} 1",
            f"      ropeStandardChannel0{level}SeedContext := by",
            f"  unfold ropeStandardChannel0{level}SeedContext",
            f"  unfold {lower_name} ropeTurnRatioUniformRationalIntervalBands",
            "  unfold RopeTurnRatioUniformRationalIntervalBand.toRationalIntervalBand",
            "  native_decide",
            "",
            f"private theorem {lower_name}_cover :",
            f"    ropeTurnRatioRationalIntervalBandsCover {lower_name}",
            f"      ropeStandardChannel0{level}SeedContext :=",
            f"  ropeTurnRatioRationalIntervalBandsCover_of_contiguous {lower_name}_contiguousCover",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start)}: a generated compressed interval certificate for",
            f"standard channel 0 through context `{plan_spec.context}`",
            f"at margin `1/{plan_spec.margin_denominator}`. -/",
            f"theorem ropeStandardChannel0{level}Seed_intervalCertificate :",
            "    ropeTurnRatioIntervalCertificate ropeStandardChannel0TurnRatio",
            f"      ropeStandardChannel0{level}SeedMargin ropeStandardChannel0{level}SeedContext := by",
            f"  simpa [ropeStandardChannel0{level}SeedMargin, ropeStandardChannel0{level}SeedContext] using",
            "    ropeTurnRatioIntervalCertificate_of_rationalIntervalBands",
            "      (turnRatio := ropeStandardChannel0TurnRatio)",
            f"      (margin := ((1 / {plan_spec.margin_denominator} : ℚ) : ℝ))",
            f"      (context := {plan_spec.context})",
            f"      (bands := {lower_name})",
            "      (by norm_num)",
            "      (by",
            f"        simpa [{lower_name}] using",
            "          ropeTurnRatioUniformRationalIntervalBands_valid_of_ratEndpointValid",
            "            (turnRatio := ropeStandardChannel0TurnRatio)",
            f"            (lowerBound := ({lower} : ℚ))",
            f"            (upperBound := ({upper} : ℚ))",
            f"            (margin := (1 / {plan_spec.margin_denominator} : ℚ))",
            f"            (compactBands := {compact_name})",
            "            (by",
            "              convert ropeStandardChannel0_piD20_base_lower using 1",
            "              norm_num)",
            "            (by",
            "              convert ropeStandardChannel0_piD20_base_upper using 1",
            "              norm_num)",
            f"            {compact_name}_lowerBound_nonneg",
            f"            {compact_name}_upperBound_nonneg",
            f"            {compact_name}_ratEndpointValid)",
            f"      {lower_name}_cover",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start + 1)}: the generated {plan_spec.description}",
            "standard channel-0 seed has the advertised finite turn-ratio margin. -/",
            f"theorem ropeStandardChannel0{level}Seed_turnRatioFiniteMargin :",
            "    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio",
            f"      ropeStandardChannel0{level}SeedMargin ropeStandardChannel0{level}SeedContext :=",
            "  ropeTurnRatioFiniteMargin_of_intervalCertificate",
            f"    ropeStandardChannel0{level}Seed_intervalCertificate",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start + 2)}: the generated {plan_spec.description}",
            "seed rules out one-channel near-turn collisions below the certified margin. -/",
            f"theorem not_ropeStandardChannel0{level}Seed_nearTurn",
            "    {tolerance : ℝ} {left right : Nat}",
            f"    (hleft : left < right) (hright : right < ropeStandardChannel0{level}SeedContext)",
            f"    (htolerance : tolerance < ropeStandardChannel0{level}SeedMargin) :",
            "    ¬ ropeRealPhaseNearTurn ropeStandardChannel0TurnRatio 1 tolerance left right := by",
            "  exact",
            "    not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin",
            "      (frequency := ropeStandardChannel0TurnRatio) (fullTurn := 1)",
            f"      (margin := ropeStandardChannel0{level}SeedMargin) (tolerance := tolerance)",
            f"      (context := ropeStandardChannel0{level}SeedContext) (left := left) (right := right)",
            "      hleft hright",
            "      (by",
            "        dsimp [ropeStandardChannel0TurnRatio]",
            "        positivity)",
            "      (by norm_num)",
            f"      (by simpa using ropeStandardChannel0{level}Seed_turnRatioFiniteMargin)",
            f"      (by simpa [ropeStandardChannel0{level}SeedMargin] using htolerance)",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start + 3)}: the generated {plan_spec.description}",
            "seed transfers to a finite bank containing standard channel 0. -/",
            f"theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0{level}Seed",
            "    {frequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}",
            "    {requestedContext left right : Nat}",
            f"    (hcontext : requestedContext ≤ ropeStandardChannel0{level}SeedContext)",
            f"    (hmargin_le : requestedMargin ≤ ropeStandardChannel0{level}SeedMargin)",
            "    (hmem : ropeStandardChannel0TurnRatio * fullTurn ∈ frequencies)",
            "    (hleft : left < right) (hright : right < requestedContext)",
            "    (hfull_pos : 0 < fullTurn)",
            "    (htolerance : tolerance < fullTurn * requestedMargin) :",
            "    ¬ ropeRealPhaseBankNearTurn frequencies fullTurn tolerance left right := by",
            "  have hratio :",
            "      (ropeStandardChannel0TurnRatio * fullTurn) / fullTurn =",
            "        ropeStandardChannel0TurnRatio := by",
            "    field_simp [hfull_pos.ne']",
            "  have hfrequency_nonneg : 0 ≤ ropeStandardChannel0TurnRatio * fullTurn := by",
            "    dsimp [ropeStandardChannel0TurnRatio]",
            "    positivity",
            "  have hmargin :",
            "      ropeTurnRatioFiniteMargin",
            "        ((ropeStandardChannel0TurnRatio * fullTurn) / fullTurn)",
            f"        ropeStandardChannel0{level}SeedMargin ropeStandardChannel0{level}SeedContext := by",
            f"    simpa [hratio] using ropeStandardChannel0{level}Seed_turnRatioFiniteMargin",
            "  exact",
            "    not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin",
            "      (frequencies := frequencies)",
            "      (frequency := ropeStandardChannel0TurnRatio * fullTurn)",
            "      (fullTurn := fullTurn)",
            "      (requestedMargin := requestedMargin)",
            f"      (certifiedMargin := ropeStandardChannel0{level}SeedMargin)",
            "      (tolerance := tolerance)",
            "      (requestedContext := requestedContext)",
            f"      (certifiedContext := ropeStandardChannel0{level}SeedContext)",
            "      (left := left) (right := right)",
            "      hcontext hmargin_le hmem hleft hright hfrequency_nonneg hfull_pos hmargin",
            "      htolerance",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start + 4)}: a bank whose first channel is",
            f"standard channel 0 inherits the generated {plan_spec.description} certificate. -/",
            f"theorem not_ropeRealPhaseBankNearTurn_of_standardChannel0{level}Seed_cons",
            "    {extraFrequencies : List ℝ} {fullTurn requestedMargin tolerance : ℝ}",
            "    {requestedContext left right : Nat}",
            f"    (hcontext : requestedContext ≤ ropeStandardChannel0{level}SeedContext)",
            f"    (hmargin_le : requestedMargin ≤ ropeStandardChannel0{level}SeedMargin)",
            "    (hleft : left < right) (hright : right < requestedContext)",
            "    (hfull_pos : 0 < fullTurn)",
            "    (htolerance : tolerance < fullTurn * requestedMargin) :",
            "    ¬ ropeRealPhaseBankNearTurn",
            "      ((ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)",
            "      fullTurn tolerance left right := by",
            "  exact",
            f"    not_ropeRealPhaseBankNearTurn_of_standardChannel0{level}Seed",
            "      (frequencies := (ropeStandardChannel0TurnRatio * fullTurn) :: extraFrequencies)",
            "      (fullTurn := fullTurn)",
            "      (requestedMargin := requestedMargin)",
            "      (tolerance := tolerance)",
            "      (requestedContext := requestedContext)",
            "      (left := left) (right := right)",
            "      hcontext hmargin_le (by simp) hleft hright hfull_pos htolerance",
            "",
            f"/-- {theorem_id(plan_spec.theorem_start + 5)}: the generated",
            f"standard channel-0 {plan_spec.description} seed brackets the advertised margin. -/",
            f"theorem ropeStandardChannel0{level}_context{plan_spec.context}_margin_bracket :",
            "    ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio",
            f"      ((1 : ℝ) / {plan_spec.margin_denominator}) {plan_spec.context} ∧",
            f"    ∀ margin : ℝ, (1 : ℝ) / {plan_spec.impossible_margin_denominator} ≤ margin →",
            f"      ¬ ropeTurnRatioFiniteMargin ropeStandardChannel0TurnRatio margin {plan_spec.context} := by",
            "  constructor",
            f"  · simpa [ropeStandardChannel0{level}SeedMargin, ropeStandardChannel0{level}SeedContext]",
            f"      using ropeStandardChannel0{level}Seed_turnRatioFiniteMargin",
            "  · intro margin hmargin",
            "    exact",
            f"      not_ropeStandardChannel0_margin_ge_one_over_{plan_spec.impossible_margin_denominator}_of_context_gt_{plan_spec.obstruction_gap}",
            f"        (context := {plan_spec.context}) (margin := margin) (by norm_num) hmargin",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    header = """import Circle.Applications.RoPECertifier

/-!
# Generated standard RoPE channel-0 compressed certificates

This file is generated by `scripts/generate_rope_generated_certificates.py`.
It converts deterministic Python rational-band plans into Lean-checked
compressed interval certificates. The generated theorems remain one-channel
standard channel-0 statements plus conditional one-separating-channel bank
bridges; they are not full all-channel standard RoPE bank theorems.
-/

namespace Circle.Applications

set_option maxHeartbeats 40000000
set_option maxRecDepth 1200000
set_option linter.unnecessarySeqFocus false
"""
    body = "\n".join(render_plan(plan) for plan in PLANS)
    OUT.write_text(f"{header}\n{body}\nend Circle.Applications\n", encoding="utf-8")


if __name__ == "__main__":
    main()
