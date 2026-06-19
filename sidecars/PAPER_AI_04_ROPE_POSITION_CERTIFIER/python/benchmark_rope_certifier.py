"""Run the public RoPE position distinguishability certifier presets.

This sidecar is a paper-local convenience wrapper around ``scripts/rope_certify.py``.
It emits compact text summaries for the named model-like and diagnostic
configurations used by the paper. The certificates are structural
position-contract reports, not model quality or long-context benchmark claims.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

from circle_math.applications import (
    PHASE_BANK_CERTIFIER_PRESETS,
    ROPE_CERTIFIER_PRESETS,
    ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_LEAN_DECLARATIONS,
    ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS,
    audit_standard_channel0_rational_band_certificate,
    certificate_summary_lines,
    certify_phase_bank_positions,
    certify_rational_preset_4099,
    certify_rope_positions,
    certify_standard_channel0_d12_bank_request,
    certify_standard_channel0_d12_margin_bracket,
    certify_standard_channel0_d13_bank_request,
    certify_standard_channel0_d13_margin_bracket,
    certify_standard_channel0_d14_bank_request,
    certify_standard_channel0_d14_margin_bracket,
    certify_standard_channel0_d16_bank_request,
    certify_standard_channel0_d16_margin_bracket,
    certify_standard_channel0_d17_bank_request,
    certify_standard_channel0_d17_margin_bracket,
    certify_standard_channel0_d18_bank_request,
    certify_standard_channel0_d18_margin_bracket,
    certify_standard_channel0_d19_bank_request,
    certify_standard_channel0_d19_margin_bracket,
    certify_standard_channel0_d19_range_request_margin_bracket,
    certify_standard_channel0_interval_seed,
    plan_standard_channel0_interval_bands,
    phase_bank_certificate_summary_lines,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run named RoPE certifier presets.")
    parser.add_argument(
        "--preset",
        action="append",
        choices=sorted(ROPE_CERTIFIER_PRESETS),
        help="Preset to run. May be passed more than once. Defaults to all presets.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format for stdout.",
    )
    parser.add_argument("--json-out", type=Path, help="Optional JSON results file.")
    parser.add_argument("--markdown-out", type=Path, help="Optional Markdown results file.")
    return parser.parse_args()


def compact_exact_discrete(exact: Any) -> dict[str, Any]:
    return {
        "pass_exact": exact.pass_exact,
        "discretized_periods": exact.discretized_periods,
        "period_count": exact.period_count,
        "single_period_collision_pair_counts": exact.single_period_collision_pair_counts,
        "common_collision_gap": exact.common_collision_gap,
        "common_collision_gap_reaches_context": exact.common_collision_gap_reaches_context,
        "guaranteed_common_gap_collision_pair_count": exact.guaranteed_common_gap_collision_pair_count,
        "guaranteed_common_gap_multiple_pair_count": exact.guaranteed_common_gap_multiple_pair_count,
        "total_bank_collision_pair_count": exact.total_bank_collision_pair_count,
        "first_exact_pass_prefix_length": exact.first_exact_pass_prefix_length,
        "prefix_collision_reports": tuple(
            {
                "prefix_length": report.prefix_length,
                "periods": report.periods,
                "lcm_collision_gap": report.lcm_collision_gap,
                "lcm_reaches_context": report.lcm_reaches_context,
                "total_bank_collision_pair_count": report.total_bank_collision_pair_count,
            }
            for report in exact.prefix_collision_reports
        ),
        "smallest_pass_subfamily_size": exact.smallest_pass_subfamily_size,
        "subfamily_pass_reports": tuple(
            {
                "subfamily_indices": report.subfamily_indices,
                "periods": report.periods,
                "lcm_value": report.lcm_value,
            }
            for report in exact.subfamily_pass_reports
        ),
        "sample_collision_pairs": exact.sample_collision_pairs,
        "theorem_ids": exact.theorem_ids,
    }


def compact_rope_certificate(certificate: Any) -> dict[str, Any]:
    margin = certificate.real_phase_margin
    return {
        "schema_id": certificate.schema_id,
        "config": asdict(certificate.config),
        "exact_discrete_summary": compact_exact_discrete(certificate.exact_discrete),
        "real_phase_margin_summary": {
            "pass_margin": margin.pass_margin,
            "tolerance": margin.tolerance,
            "worst_margin_radians": margin.worst_margin_radians,
            "worst_gap": margin.worst_gap,
            "worst_channel_index": margin.worst_channel_index,
            "scanned_gap_count": margin.scanned_gap_count,
            "near_collision_gaps": margin.near_collision_gaps,
            "formal_precursor_theorem_ids": margin.formal_precursor_theorem_ids,
        },
        "proof_layers": tuple(
            {
                "layer": layer.layer,
                "status": layer.status,
                "theorem_backed": layer.theorem_backed,
                "theorem_ids": layer.theorem_ids,
            }
            for layer in certificate.proof_layers
        ),
        "theorem_ids": certificate.theorem_ids,
        "claim_boundary": certificate.claim_boundary,
    }


def compact_interval_certificate(certificate: Any) -> dict[str, Any]:
    witnesses = certificate.interval_witnesses
    return {
        "schema_id": certificate.schema_id,
        "name": certificate.name,
        "turn_ratio_expression": certificate.turn_ratio_expression,
        "context_length": certificate.context_length,
        "certified_margin": certificate.certified_margin,
        "pass_certificate": certificate.pass_certificate,
        "pi_bounds": certificate.pi_bounds,
        "witness_count": len(witnesses),
        "first_interval_witness": asdict(witnesses[0]) if witnesses else None,
        "last_interval_witness": asdict(witnesses[-1]) if witnesses else None,
        "theorem_ids": certificate.theorem_ids,
        "lean_declarations": certificate.lean_declarations,
        "explanation": certificate.explanation,
        "claim_boundary": certificate.claim_boundary,
    }


def compact_interval_plan(plan: Any) -> dict[str, Any]:
    bands = plan.bands
    return {
        "schema_id": plan.schema_id,
        "name": plan.name,
        "turn_ratio_expression": plan.turn_ratio_expression,
        "context_length": plan.context_length,
        "planned_margin": plan.planned_margin,
        "pi_bound_preset": plan.pi_bound_preset,
        "pi_bounds": plan.pi_bounds,
        "lower_turn_ratio_bound": plan.lower_turn_ratio_bound,
        "upper_turn_ratio_bound": plan.upper_turn_ratio_bound,
        "pass_plan": plan.pass_plan,
        "first_uncovered_gap": plan.first_uncovered_gap,
        "band_count": len(bands),
        "first_band": asdict(bands[0]) if bands else None,
        "last_band": asdict(bands[-1]) if bands else None,
        "theorem_status": plan.theorem_status,
        "explanation": plan.explanation,
        "claim_boundary": plan.claim_boundary,
    }


def compact_phase_bank_certificate(certificate: Any) -> dict[str, Any]:
    return {
        "schema_id": certificate.schema_id,
        "config": asdict(certificate.config),
        "exact_discrete_summary": compact_exact_discrete(certificate.exact_discrete),
        "theorem_ids": certificate.theorem_ids,
        "claim_boundary": certificate.claim_boundary,
    }


def standard_channel0_frontier_summary(standard_plans: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    proved_104219 = [
        plan
        for plan in standard_plans
        if plan["planned_margin"] == "1/104219"
        and plan["theorem_status"].startswith("lean_proved_interval_seed")
    ]
    failed_104219 = [
        plan
        for plan in standard_plans
        if plan["planned_margin"] == "1/104219"
        and plan["theorem_status"] == "candidate_plan_not_lean_proved"
    ]
    proved_lower_margin = [
        plan
        for plan in standard_plans
        if plan["planned_margin"] == "1/328459"
        and plan["theorem_status"].startswith("lean_proved_interval_seed")
    ]
    full_candidate_contexts = tuple(
        plan["context_length"]
        for plan in failed_104219
        if plan["first_uncovered_gap"] is None
    )
    frontier_gaps = tuple(
        plan["first_uncovered_gap"]
        for plan in failed_104219
        if plan["first_uncovered_gap"] is not None
    )
    proved_104219_context = max((plan["context_length"] for plan in proved_104219), default=0)
    proved_104219_plan = next(
        (plan for plan in proved_104219 if plan["context_length"] == proved_104219_context),
        None,
    )
    proved_lower_context = max(
        (plan["context_length"] for plan in proved_lower_margin),
        default=0,
    )
    proved_lower_plan = next(
        (
            plan
            for plan in proved_lower_margin
            if plan["context_length"] == proved_lower_context
        ),
        None,
    )
    return {
        "schema_id": "circle_calculus.standard_rope_channel0_frontier_summary.v0",
        "proved_margin": "1/328459",
        "proved_context": 0 if proved_lower_plan is None else proved_lower_plan["context_length"],
        "proved_theorem_status": (
            None if proved_lower_plan is None else proved_lower_plan["theorem_status"]
        ),
        "sharp_64k_margin": "1/104219",
        "sharp_64k_context": proved_104219_context,
        "sharp_64k_theorem_status": (
            None if proved_104219_plan is None else proved_104219_plan["theorem_status"]
        ),
        "too_strong_128k_margin": "1/104219",
        "candidate_full_contexts": full_candidate_contexts,
        "candidate_first_uncovered_gaps": frontier_gaps,
        "compression_bridge_theorem_ids": ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS,
        "compression_bridge_lean_declarations": (
            ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_LEAN_DECLARATIONS
        ),
        "frontier_status": (
            None if proved_lower_plan is None else proved_lower_plan["theorem_status"]
        ),
        "summary": (
            "Lean proves standard channel-0 margin 1/104219 through "
            f"context {proved_104219_context}, and a lower 1/328459 margin through "
            f"context {proved_lower_context}. The exact-rational planner first fails the stronger "
            f"128k margin-1/104219 request at gaps {frontier_gaps}; any remaining "
            f"full-context candidate rows are {full_candidate_contexts}. "
            "AIRA-T0139 through AIRA-T0141 are "
            "the proved rational-band compression and rational-endpoint "
            "reflection bridges used by the generated 32k/64k/128k/160k/192k certificates."
        ),
        "claim_boundary": (
            "This is a derived sidecar summary of proved and candidate interval "
            "plans. It does not upgrade candidate rows to theorem-backed status."
        ),
    }


def rational_band_audit_rows(audits: tuple[dict[str, Any], ...]) -> list[str]:
    rows = [
        "| Audit | Requested context | Certified context | Bands | Valid bands | Covered gaps | First uncovered gap | Coverage | Endpoint validity | Status | Bridge ids |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for audit in audits:
        first_uncovered = (
            "none"
            if audit["first_uncovered_gap"] is None
            else str(audit["first_uncovered_gap"])
        )
        rows.append(
            "| {name} | {requested} | {certified} | {bands} | {valid_bands} | "
            "{covered_gaps} | {first_uncovered} | {coverage} | {validity} | "
            "{status} | {theorems} |".format(
                name=audit["source_plan_name"],
                requested=audit["requested_context_length"],
                certified=audit["certified_context_length"],
                bands=audit["band_count"],
                valid_bands=audit["valid_band_count"],
                covered_gaps=audit["covered_gap_count"],
                first_uncovered=first_uncovered,
                coverage="PASS" if audit["coverage_pass"] else "FAIL",
                validity="PASS" if audit["endpoint_validity_pass"] else "FAIL",
                status=audit["theorem_status"],
                theorems=", ".join(audit["theorem_ids"]),
            )
        )
    return rows


def run_presets(presets: tuple[str, ...]) -> dict[str, Any]:
    certificates = []
    for preset in presets:
        certificate = certify_rope_positions(ROPE_CERTIFIER_PRESETS[preset])
        certificates.append(
            {
                "preset": preset,
                "summary_lines": certificate_summary_lines(certificate),
                "certificate": compact_rope_certificate(certificate),
            }
        )
    phase_bank_diagnostics = []
    for preset, config in PHASE_BANK_CERTIFIER_PRESETS.items():
        certificate = certify_phase_bank_positions(config)
        phase_bank_diagnostics.append(
            {
                "preset": preset,
                "summary_lines": phase_bank_certificate_summary_lines(certificate),
                "certificate": compact_phase_bank_certificate(certificate),
            }
        )
    standard_plan_specs = (
        ("d4", Fraction(1, 512), 4096, 333),
        ("d6", Fraction(1, 1024), 4096, 710),
        ("d20", Fraction(1, 104219), 4096, 4096),
        ("d20", Fraction(1, 104220), 8192, 8192),
        ("d20", Fraction(1, 104219), 8192, 8192),
        ("d20", Fraction(1, 104219), 16384, 16384),
        ("d20", Fraction(1, 104219), 32768, 32768),
        ("d20", Fraction(1, 104219), 65536, 65536),
        ("d20", Fraction(1, 104219), 131072, 131072),
        ("d20", Fraction(1, 328459), 131072, 131072),
        ("d20", Fraction(1, 328459), 163840, 163840),
        ("d20", Fraction(1, 328459), 196608, 196608),
    )
    standard_plan_objects = tuple(
        (
            requested_context,
            plan_standard_channel0_interval_bands(
                pi_bound_preset=pi_bound_preset,
                margin=margin,
                max_context_length=max_context_length,
            ),
        )
        for pi_bound_preset, margin, max_context_length, requested_context
        in standard_plan_specs
    )
    standard_plans = tuple(
        compact_interval_plan(plan) for _requested_context, plan in standard_plan_objects
    )
    standard_band_audits = tuple(
        audit_standard_channel0_rational_band_certificate(
            plan,
            requested_context_length=requested_context,
        ).to_dict()
        for requested_context, plan in standard_plan_objects
    )
    return {
        "schema_id": "circle_calculus.rope_certifier_preset_results.v0",
        "claim_boundary": (
            "These are proof-carrying position-contract reports for declared "
            "integer-period phase banks plus numerical real-phase margin scans. "
            "They are not model-quality, context-length, speed, memory, "
            "perplexity, or deployment claims."
        ),
        "rational_margin_certificate": certify_rational_preset_4099().to_dict(),
        "standard_interval_certificate": compact_interval_certificate(
            certify_standard_channel0_interval_seed()
        ),
        "standard_d12_bank_bridge_request": certify_standard_channel0_d12_bank_request(
            requested_context=8192,
            requested_margin=Fraction(1, 104220),
        ).to_dict(),
        "standard_d12_margin_bracket": certify_standard_channel0_d12_margin_bracket().to_dict(),
        "standard_d13_bank_bridge_request": certify_standard_channel0_d13_bank_request(
            requested_context=8192,
            requested_margin=Fraction(1, 104219),
        ).to_dict(),
        "standard_d13_margin_bracket": certify_standard_channel0_d13_margin_bracket().to_dict(),
        "standard_d14_bank_bridge_request": certify_standard_channel0_d14_bank_request(
            requested_context=16384,
            requested_margin=Fraction(1, 104219),
        ).to_dict(),
        "standard_d14_margin_bracket": certify_standard_channel0_d14_margin_bracket().to_dict(),
        "standard_d16_bank_bridge_request": certify_standard_channel0_d16_bank_request(
            requested_context=65536,
            requested_margin=Fraction(1, 104219),
        ).to_dict(),
        "standard_d16_margin_bracket": certify_standard_channel0_d16_margin_bracket().to_dict(),
        "standard_d17_bank_bridge_request": certify_standard_channel0_d17_bank_request(
            requested_context=131072,
            requested_margin=Fraction(1, 328459),
        ).to_dict(),
        "standard_d17_margin_bracket": certify_standard_channel0_d17_margin_bracket().to_dict(),
        "standard_d18_bank_bridge_request": certify_standard_channel0_d18_bank_request(
            requested_context=163840,
            requested_margin=Fraction(1, 328459),
        ).to_dict(),
        "standard_d18_margin_bracket": certify_standard_channel0_d18_margin_bracket().to_dict(),
        "standard_d19_bank_bridge_request": certify_standard_channel0_d19_bank_request(
            requested_context=196608,
            requested_margin=Fraction(1, 328459),
        ).to_dict(),
        "standard_d19_margin_bracket": certify_standard_channel0_d19_margin_bracket().to_dict(),
        "standard_d19_range_request_margin_bracket": (
            certify_standard_channel0_d19_range_request_margin_bracket(
                requested_context=131072,
                requested_margin=Fraction(1, 328458),
            ).to_dict()
        ),
        "standard_channel0_frontier_summary": standard_channel0_frontier_summary(standard_plans),
        "standard_band_certificate_audits": standard_band_audits,
        "standard_interval_candidate_plans": standard_plans,
        "presets": certificates,
        "phase_bank_diagnostics": phase_bank_diagnostics,
    }


def band_endpoint_audit_rows(standard_plans: tuple[dict[str, Any], ...]) -> list[str]:
    rows = [
        "| Plan | Band | Gap range | Cell | Start lower endpoint | End upper endpoint | Endpoint check | Bridge |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for plan in standard_plans:
        first_band = plan.get("first_band")
        last_band = plan.get("last_band")
        if first_band is None:
            rows.append(
                "| {name} | none | none | n/a | n/a | n/a | FAIL | n/a |".format(
                    name=plan["name"],
                )
            )
            continue
        selected_bands = (("first", first_band),)
        if last_band is not None and last_band != first_band:
            selected_bands = selected_bands + (("last", last_band),)
        for label, band in selected_bands:
            rows.append(
                "| {name} | {label} | {start}-{end} | {cell} | {lower} | {upper} | {status} | {bridge} |".format(
                    name=plan["name"],
                    label=label,
                    start=band["start_gap"],
                    end=band["end_gap"],
                    cell=band["cell"],
                    lower=band["start_lower_value"],
                    upper=band["end_upper_value"],
                    status="PASS" if band["endpoint_cell_margin_ok"] else "FAIL",
                    bridge=band["bridge_theorem_id"],
                )
            )
    return rows


def markdown_results(payload: dict[str, Any]) -> str:
    rational = payload["rational_margin_certificate"]
    standard_interval = payload["standard_interval_certificate"]
    standard_d12_bank = payload["standard_d12_bank_bridge_request"]
    standard_d12_bracket = payload["standard_d12_margin_bracket"]
    standard_d13_bank = payload["standard_d13_bank_bridge_request"]
    standard_d13_bracket = payload["standard_d13_margin_bracket"]
    standard_d14_bank = payload["standard_d14_bank_bridge_request"]
    standard_d14_bracket = payload["standard_d14_margin_bracket"]
    standard_d16_bank = payload["standard_d16_bank_bridge_request"]
    standard_d16_bracket = payload["standard_d16_margin_bracket"]
    standard_d17_bank = payload["standard_d17_bank_bridge_request"]
    standard_d17_bracket = payload["standard_d17_margin_bracket"]
    standard_d18_bank = payload["standard_d18_bank_bridge_request"]
    standard_d18_bracket = payload["standard_d18_margin_bracket"]
    standard_d19_bank = payload["standard_d19_bank_bridge_request"]
    standard_d19_bracket = payload["standard_d19_margin_bracket"]
    standard_d19_range_request = payload["standard_d19_range_request_margin_bracket"]
    frontier = payload["standard_channel0_frontier_summary"]
    standard_plans = payload["standard_interval_candidate_plans"]
    standard_band_audits = payload["standard_band_certificate_audits"]
    rows = [
        "| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Common-gap pairs | Total bank pairs | First pass prefix | Smallest pass subfamily | Real margin | Worst gap | Theorem ids |",
        "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for item in payload["presets"]:
        cert = item["certificate"]
        config = cert["config"]
        exact = cert["exact_discrete_summary"]
        margin = cert["real_phase_margin_summary"]
        exact_label = "PASS" if exact["pass_exact"] else "FAIL"
        margin_label = "PASS" if margin["pass_margin"] else "WARN"
        common_gap = (
            ">= context"
            if exact["common_collision_gap"] is None
            else str(exact["common_collision_gap"])
        )
        worst_gap = "none" if margin["worst_gap"] is None else str(margin["worst_gap"])
        first_prefix = (
            "none"
            if exact["first_exact_pass_prefix_length"] is None
            else str(exact["first_exact_pass_prefix_length"])
        )
        smallest_subfamily = (
            "none"
            if exact["smallest_pass_subfamily_size"] is None
            else str(exact["smallest_pass_subfamily_size"])
        )
        theorem_ids = ", ".join(cert["theorem_ids"])
        rows.append(
            "| {preset} | {head_dim} | {base:g} | {context} | {exact_label} | "
            "{common_gap} | {pair_count} | {total_count} | {first_prefix} | {smallest_subfamily} | {margin_label} ({worst_margin:.6g} rad) | {worst_gap} | {theorem_ids} |".format(
                preset=item["preset"],
                head_dim=config["head_dim"],
                base=config["base"],
                context=config["context_length"],
                exact_label=exact_label,
                common_gap=common_gap,
                pair_count=exact["guaranteed_common_gap_collision_pair_count"],
                total_count=exact["total_bank_collision_pair_count"],
                first_prefix=first_prefix,
                smallest_subfamily=smallest_subfamily,
                margin_label=margin_label,
                worst_margin=margin["worst_margin_radians"],
                worst_gap=worst_gap,
                theorem_ids=theorem_ids,
            )
        )
    phase_bank_rows = [
        "| Preset | Periods | Context | Exact discrete | Common collision gap | Total bank pairs | First pass prefix | Smallest pass subfamily | Theorem ids |",
        "| --- | --- | ---: | --- | --- | ---: | --- | --- | --- |",
    ]
    for item in payload["phase_bank_diagnostics"]:
        cert = item["certificate"]
        config = cert["config"]
        exact = cert["exact_discrete_summary"]
        exact_label = "PASS" if exact["pass_exact"] else "FAIL"
        common_gap = (
            ">= context"
            if exact["common_collision_gap"] is None
            else str(exact["common_collision_gap"])
        )
        first_prefix = (
            "none"
            if exact["first_exact_pass_prefix_length"] is None
            else str(exact["first_exact_pass_prefix_length"])
        )
        smallest_subfamily = (
            "none"
            if exact["smallest_pass_subfamily_size"] is None
            else str(exact["smallest_pass_subfamily_size"])
        )
        phase_bank_rows.append(
            "| {preset} | {periods} | {context} | {exact_label} | {common_gap} | "
            "{total_count} | {first_prefix} | {smallest_subfamily} | {theorems} |".format(
                preset=item["preset"],
                periods=",".join(str(period) for period in config["periods"]),
                context=config["context_length"],
                exact_label=exact_label,
                common_gap=common_gap,
                total_count=exact["total_bank_collision_pair_count"],
                first_prefix=first_prefix,
                smallest_subfamily=smallest_subfamily,
                theorems=", ".join(cert["theorem_ids"]),
            )
        )
    plan_rows = [
        "| Plan | Pi bounds | Planned margin | Covered context | First uncovered gap | Bands | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for plan in standard_plans:
        first_uncovered = (
            "none"
            if plan["first_uncovered_gap"] is None
            else str(plan["first_uncovered_gap"])
        )
        plan_rows.append(
            "| {name} | {pi_bounds} | {margin} | {context} | {first_uncovered} | "
            "{bands} | {status} |".format(
                name=plan["name"],
                pi_bounds=plan["pi_bounds"],
                margin=plan["planned_margin"],
                context=plan["context_length"],
                first_uncovered=first_uncovered,
                bands=plan["band_count"],
                status=plan["theorem_status"],
            )
        )
    return "\n".join(
        [
            "# RoPE Certifier Preset Results",
            "",
            payload["claim_boundary"],
            "",
            "## Named Rational Margin Certificate",
            "",
            "| Name | Ratio | Context | Certified margin | Exact weakest gap margin | Weakest gap | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {numerator}/{denominator} | {context} | {margin:.12g} | {exact_margin} | {exact_gap} | {status} | {theorems} |".format(
                name=rational["name"],
                numerator=rational["numerator"],
                denominator=rational["denominator"],
                context=rational["context_length"],
                margin=rational["certified_margin"],
                exact_margin=rational["exact_nearest_gap_margin"],
                exact_gap=rational["exact_nearest_gap"],
                status="PASS" if rational["pass_certificate"] else "FAIL",
                theorems=", ".join(rational["theorem_ids"]),
            ),
            "",
            rational["claim_boundary"],
            "",
            "## Named Standard RoPE Interval Seed",
            "",
            "| Name | Turn ratio | Context | Certified margin | Pi bounds | Status | Theorem ids |",
            "| --- | --- | ---: | --- | --- | --- | --- |",
            "| {name} | {ratio} | {context} | {margin} | {pi_bounds} | {status} | {theorems} |".format(
                name=standard_interval["name"],
                ratio=standard_interval["turn_ratio_expression"],
                context=standard_interval["context_length"],
                margin=standard_interval["certified_margin"],
                pi_bounds=standard_interval["pi_bounds"],
                status="PASS" if standard_interval["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_interval["theorem_ids"]),
            ),
            "",
            standard_interval["claim_boundary"],
            "",
            "## Standard RoPE D12 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d12_bank["name"],
                bank_shape=standard_d12_bank["bank_shape"],
                requested_context=standard_d12_bank["requested_context"],
                requested_margin=standard_d12_bank["requested_margin"],
                certified_context=standard_d12_bank["certified_context"],
                certified_margin=standard_d12_bank["certified_margin"],
                status="PASS" if standard_d12_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d12_bank["theorem_ids"]),
            ),
            "",
            standard_d12_bank["claim_boundary"],
            "",
            "## Standard RoPE D12 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d12_bracket["name"],
                context=standard_d12_bracket["context_length"],
                proved_margin=standard_d12_bracket["proved_margin"],
                impossible_margin_floor=standard_d12_bracket["impossible_margin_floor"],
                status="PASS" if standard_d12_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d12_bracket["theorem_ids"]),
            ),
            "",
            standard_d12_bracket["claim_boundary"],
            "",
            "## Standard RoPE D13 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d13_bank["name"],
                bank_shape=standard_d13_bank["bank_shape"],
                requested_context=standard_d13_bank["requested_context"],
                requested_margin=standard_d13_bank["requested_margin"],
                certified_context=standard_d13_bank["certified_context"],
                certified_margin=standard_d13_bank["certified_margin"],
                status="PASS" if standard_d13_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d13_bank["theorem_ids"]),
            ),
            "",
            standard_d13_bank["claim_boundary"],
            "",
            "## Standard RoPE D13 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d13_bracket["name"],
                context=standard_d13_bracket["context_length"],
                proved_margin=standard_d13_bracket["proved_margin"],
                impossible_margin_floor=standard_d13_bracket["impossible_margin_floor"],
                status="PASS" if standard_d13_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d13_bracket["theorem_ids"]),
            ),
            "",
            standard_d13_bracket["claim_boundary"],
            "",
            "## Standard RoPE D14 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d14_bank["name"],
                bank_shape=standard_d14_bank["bank_shape"],
                requested_context=standard_d14_bank["requested_context"],
                requested_margin=standard_d14_bank["requested_margin"],
                certified_context=standard_d14_bank["certified_context"],
                certified_margin=standard_d14_bank["certified_margin"],
                status="PASS" if standard_d14_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d14_bank["theorem_ids"]),
            ),
            "",
            standard_d14_bank["claim_boundary"],
            "",
            "## Standard RoPE D14 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d14_bracket["name"],
                context=standard_d14_bracket["context_length"],
                proved_margin=standard_d14_bracket["proved_margin"],
                impossible_margin_floor=standard_d14_bracket["impossible_margin_floor"],
                status="PASS" if standard_d14_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d14_bracket["theorem_ids"]),
            ),
            "",
            standard_d14_bracket["claim_boundary"],
            "",
            "## Standard RoPE D16 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d16_bank["name"],
                bank_shape=standard_d16_bank["bank_shape"],
                requested_context=standard_d16_bank["requested_context"],
                requested_margin=standard_d16_bank["requested_margin"],
                certified_context=standard_d16_bank["certified_context"],
                certified_margin=standard_d16_bank["certified_margin"],
                status="PASS" if standard_d16_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d16_bank["theorem_ids"]),
            ),
            "",
            standard_d16_bank["claim_boundary"],
            "",
            "## Standard RoPE D16 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d16_bracket["name"],
                context=standard_d16_bracket["context_length"],
                proved_margin=standard_d16_bracket["proved_margin"],
                impossible_margin_floor=standard_d16_bracket["impossible_margin_floor"],
                status="PASS" if standard_d16_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d16_bracket["theorem_ids"]),
            ),
            "",
            standard_d16_bracket["claim_boundary"],
            "",
            "## Standard RoPE D17 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d17_bank["name"],
                bank_shape=standard_d17_bank["bank_shape"],
                requested_context=standard_d17_bank["requested_context"],
                requested_margin=standard_d17_bank["requested_margin"],
                certified_context=standard_d17_bank["certified_context"],
                certified_margin=standard_d17_bank["certified_margin"],
                status="PASS" if standard_d17_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d17_bank["theorem_ids"]),
            ),
            "",
            standard_d17_bank["claim_boundary"],
            "",
            "## Standard RoPE D17 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d17_bracket["name"],
                context=standard_d17_bracket["context_length"],
                proved_margin=standard_d17_bracket["proved_margin"],
                impossible_margin_floor=standard_d17_bracket["impossible_margin_floor"],
                status="PASS" if standard_d17_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d17_bracket["theorem_ids"]),
            ),
            "",
            standard_d17_bracket["claim_boundary"],
            "",
            "## Standard RoPE D18 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d18_bank["name"],
                bank_shape=standard_d18_bank["bank_shape"],
                requested_context=standard_d18_bank["requested_context"],
                requested_margin=standard_d18_bank["requested_margin"],
                certified_context=standard_d18_bank["certified_context"],
                certified_margin=standard_d18_bank["certified_margin"],
                status="PASS" if standard_d18_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d18_bank["theorem_ids"]),
            ),
            "",
            standard_d18_bank["claim_boundary"],
            "",
            "## Standard RoPE D18 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d18_bracket["name"],
                context=standard_d18_bracket["context_length"],
                proved_margin=standard_d18_bracket["proved_margin"],
                impossible_margin_floor=standard_d18_bracket["impossible_margin_floor"],
                status="PASS" if standard_d18_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d18_bracket["theorem_ids"]),
            ),
            "",
            standard_d18_bracket["claim_boundary"],
            "",
            "## Standard RoPE D19 Bank Bridge Request",
            "",
            "| Name | Bank shape | Requested context | Requested margin | Certified context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
            "| {name} | {bank_shape} | {requested_context} | {requested_margin} | {certified_context} | {certified_margin} | {status} | {theorems} |".format(
                name=standard_d19_bank["name"],
                bank_shape=standard_d19_bank["bank_shape"],
                requested_context=standard_d19_bank["requested_context"],
                requested_margin=standard_d19_bank["requested_margin"],
                certified_context=standard_d19_bank["certified_context"],
                certified_margin=standard_d19_bank["certified_margin"],
                status="PASS" if standard_d19_bank["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d19_bank["theorem_ids"]),
            ),
            "",
            standard_d19_bank["claim_boundary"],
            "",
            "## Standard RoPE D19 Margin Bracket",
            "",
            "| Name | Context | Proved margin | Impossible margin floor | Status | Theorem ids |",
            "| --- | ---: | ---: | ---: | --- | --- |",
            "| {name} | {context} | {proved_margin} | {impossible_margin_floor} | {status} | {theorems} |".format(
                name=standard_d19_bracket["name"],
                context=standard_d19_bracket["context_length"],
                proved_margin=standard_d19_bracket["proved_margin"],
                impossible_margin_floor=standard_d19_bracket["impossible_margin_floor"],
                status="PASS" if standard_d19_bracket["pass_certificate"] else "FAIL",
                theorems=", ".join(standard_d19_bracket["theorem_ids"]),
            ),
            "",
            standard_d19_bracket["claim_boundary"],
            "",
            "## Standard RoPE D19 Range Request Classifier",
            "",
            "| Name | Requested context | Requested margin | Status | Theorem-backed | Proved applies | Impossible applies | Open gap | Exhaustive | Semantic trichotomy | Thresholds ordered | Branches disjoint | Theorem ids |",
            "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "| {name} | {requested_context} | {requested_margin} | {status} | {theorem_backed} | {proved} | {impossible} | {open_gap} | {exhaustive} | {semantic} | {ordered} | {disjoint} | {theorems} |".format(
                name=standard_d19_range_request["name"],
                requested_context=standard_d19_range_request["requested_context"],
                requested_margin=standard_d19_range_request["requested_margin"],
                status=standard_d19_range_request["request_status"],
                theorem_backed=standard_d19_range_request["theorem_backed_classification"],
                proved=standard_d19_range_request["proved_margin_applies"],
                impossible=standard_d19_range_request["impossible_margin_applies"],
                open_gap=standard_d19_range_request["undecided_margin_open_gap"],
                exhaustive=standard_d19_range_request["margin_status_exhaustive"],
                semantic=standard_d19_range_request["in_range_semantic_trichotomy"],
                ordered=standard_d19_range_request["margin_thresholds_ordered"],
                disjoint=standard_d19_range_request["proved_impossible_branches_disjoint"],
                theorems=", ".join(standard_d19_range_request["theorem_ids"]),
            ),
            "",
            standard_d19_range_request["claim_boundary"],
            "",
            "## Standard Channel-0 Frontier Summary",
            "",
        "| Proved margin | Proved context | Proved status | Candidate full contexts | Candidate first uncovered gaps | Compression bridge | Frontier status |",
        "| ---: | ---: | --- | --- | --- | --- | --- |",
        "| {proved_margin} | {proved_context} | {proved_status} | {candidate_contexts} | {frontier_gaps} | {compression} | {frontier_status} |".format(
            proved_margin=frontier["proved_margin"],
            proved_context=frontier["proved_context"],
            proved_status=frontier["proved_theorem_status"],
            candidate_contexts=", ".join(str(context) for context in frontier["candidate_full_contexts"]),
            frontier_gaps=", ".join(str(gap) for gap in frontier["candidate_first_uncovered_gaps"]),
            compression=", ".join(frontier["compression_bridge_theorem_ids"]),
            frontier_status=frontier["frontier_status"],
        ),
            "",
            frontier["claim_boundary"],
            "",
            "## Standard RoPE Candidate Interval Plans",
            "",
            "These exact-rational plans are generated source data for Lean interval certificates. The d4 context-333, d6 context-710, d20 context-4096, d20 context-8192, d20 context-16384, d20 context-32768, d20 context-65536, and d20 margin-1/328459 context-131072/context-163840/context-196608 plans listed here are now matched by compiled Lean declarations; the stronger 128k margin-1/104219 row remains a failed frontier comparison at gap 103993.",
            "",
            *plan_rows,
            "",
            "### Rational-Band Certificate Audits",
            "",
            "These executable audits check whether each generated band list has the finite shape needed by the generic compression bridge. They are source-data checks for the next Lean certificate route, not proof-status upgrades for candidate rows.",
            "",
            *rational_band_audit_rows(standard_band_audits),
            "",
            "### Band Endpoint Audit",
            "",
            "Each row shows the endpoint inequalities a generator must justify before the Lean bridge `AIRA-T0126` can fill in the intermediate gaps for that band. This table samples the first and last band for each generated plan; rerun the Python planner for the complete deterministic band list.",
            "",
            *band_endpoint_audit_rows(standard_plans),
            "",
            "## RoPE Preset Diagnostics",
            "",
            *rows,
            "",
            "## Exact Phase-Bank Diagnostics",
            "",
            "These exact-only presets exercise quantized/shared-factor and interpolation-style scaled-period boundary cases. They are declared integer-period phase-bank contracts, not real-valued RoPE claims.",
            "",
            *phase_bank_rows,
            "",
            "Reproduce with:",
            "",
            "```bash",
            "python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown",
            "```",
            "",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> None:
    args = parse_args()
    presets = tuple(args.preset) if args.preset else tuple(ROPE_CERTIFIER_PRESETS)
    payload = run_presets(presets)
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    markdown_text = markdown_results(payload)
    if args.json_out is not None:
        write_text(args.json_out, json_text)
    if args.markdown_out is not None:
        write_text(args.markdown_out, markdown_text)
    if args.format == "json":
        print(json_text, end="")
    elif args.format == "markdown":
        print(markdown_text, end="")
    else:
        for index, item in enumerate(payload["presets"]):
            if index == 0:
                rational = payload["rational_margin_certificate"]
                standard_interval = payload["standard_interval_certificate"]
                print(f"rational_margin_certificate={rational['name']}")
                print(f"pass_certificate={rational['pass_certificate']}")
                print(f"certified_margin={rational['certified_margin']}")
                print(f"exact_nearest_gap_margin={rational['exact_nearest_gap_margin']}")
                print(f"exact_nearest_gap={rational['exact_nearest_gap']}")
                print(f"theorem_ids={','.join(rational['theorem_ids'])}")
                print()
                print(f"standard_interval_certificate={standard_interval['name']}")
                print(f"pass_certificate={standard_interval['pass_certificate']}")
                print(f"certified_margin={standard_interval['certified_margin']}")
                print(f"theorem_ids={','.join(standard_interval['theorem_ids'])}")
                standard_d12_bank = payload["standard_d12_bank_bridge_request"]
                print()
                print(f"standard_d12_bank_bridge_request={standard_d12_bank['name']}")
                print(f"pass_certificate={standard_d12_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d12_bank["requested_context"],
                        requested_margin=standard_d12_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d12_bank['theorem_ids'])}")
                standard_d12_bracket = payload["standard_d12_margin_bracket"]
                print()
                print(f"standard_d12_margin_bracket={standard_d12_bracket['name']}")
                print(f"pass_certificate={standard_d12_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d12_bracket["context_length"],
                        proved_margin=standard_d12_bracket["proved_margin"],
                        impossible_margin_floor=standard_d12_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d12_bracket['theorem_ids'])}")
                standard_d13_bank = payload["standard_d13_bank_bridge_request"]
                print()
                print(f"standard_d13_bank_bridge_request={standard_d13_bank['name']}")
                print(f"pass_certificate={standard_d13_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d13_bank["requested_context"],
                        requested_margin=standard_d13_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d13_bank['theorem_ids'])}")
                standard_d13_bracket = payload["standard_d13_margin_bracket"]
                print()
                print(f"standard_d13_margin_bracket={standard_d13_bracket['name']}")
                print(f"pass_certificate={standard_d13_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d13_bracket["context_length"],
                        proved_margin=standard_d13_bracket["proved_margin"],
                        impossible_margin_floor=standard_d13_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d13_bracket['theorem_ids'])}")
                standard_d14_bank = payload["standard_d14_bank_bridge_request"]
                print()
                print(f"standard_d14_bank_bridge_request={standard_d14_bank['name']}")
                print(f"pass_certificate={standard_d14_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d14_bank["requested_context"],
                        requested_margin=standard_d14_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d14_bank['theorem_ids'])}")
                standard_d14_bracket = payload["standard_d14_margin_bracket"]
                print()
                print(f"standard_d14_margin_bracket={standard_d14_bracket['name']}")
                print(f"pass_certificate={standard_d14_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d14_bracket["context_length"],
                        proved_margin=standard_d14_bracket["proved_margin"],
                        impossible_margin_floor=standard_d14_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d14_bracket['theorem_ids'])}")
                standard_d16_bank = payload["standard_d16_bank_bridge_request"]
                print()
                print(f"standard_d16_bank_bridge_request={standard_d16_bank['name']}")
                print(f"pass_certificate={standard_d16_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d16_bank["requested_context"],
                        requested_margin=standard_d16_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d16_bank['theorem_ids'])}")
                standard_d16_bracket = payload["standard_d16_margin_bracket"]
                print()
                print(f"standard_d16_margin_bracket={standard_d16_bracket['name']}")
                print(f"pass_certificate={standard_d16_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d16_bracket["context_length"],
                        proved_margin=standard_d16_bracket["proved_margin"],
                        impossible_margin_floor=standard_d16_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d16_bracket['theorem_ids'])}")
                standard_d17_bank = payload["standard_d17_bank_bridge_request"]
                print()
                print(f"standard_d17_bank_bridge_request={standard_d17_bank['name']}")
                print(f"pass_certificate={standard_d17_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d17_bank["requested_context"],
                        requested_margin=standard_d17_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d17_bank['theorem_ids'])}")
                standard_d17_bracket = payload["standard_d17_margin_bracket"]
                print()
                print(f"standard_d17_margin_bracket={standard_d17_bracket['name']}")
                print(f"pass_certificate={standard_d17_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d17_bracket["context_length"],
                        proved_margin=standard_d17_bracket["proved_margin"],
                        impossible_margin_floor=standard_d17_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d17_bracket['theorem_ids'])}")
                standard_d18_bank = payload["standard_d18_bank_bridge_request"]
                print()
                print(f"standard_d18_bank_bridge_request={standard_d18_bank['name']}")
                print(f"pass_certificate={standard_d18_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d18_bank["requested_context"],
                        requested_margin=standard_d18_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d18_bank['theorem_ids'])}")
                standard_d18_bracket = payload["standard_d18_margin_bracket"]
                print()
                print(f"standard_d18_margin_bracket={standard_d18_bracket['name']}")
                print(f"pass_certificate={standard_d18_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d18_bracket["context_length"],
                        proved_margin=standard_d18_bracket["proved_margin"],
                        impossible_margin_floor=standard_d18_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d18_bracket['theorem_ids'])}")
                standard_d19_bank = payload["standard_d19_bank_bridge_request"]
                print()
                print(f"standard_d19_bank_bridge_request={standard_d19_bank['name']}")
                print(f"pass_certificate={standard_d19_bank['pass_certificate']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin}".format(
                        requested_context=standard_d19_bank["requested_context"],
                        requested_margin=standard_d19_bank["requested_margin"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d19_bank['theorem_ids'])}")
                standard_d19_bracket = payload["standard_d19_margin_bracket"]
                print()
                print(f"standard_d19_margin_bracket={standard_d19_bracket['name']}")
                print(f"pass_certificate={standard_d19_bracket['pass_certificate']}")
                print(
                    "context={context} proved_margin={proved_margin} "
                    "impossible_margin_floor={impossible_margin_floor}".format(
                        context=standard_d19_bracket["context_length"],
                        proved_margin=standard_d19_bracket["proved_margin"],
                        impossible_margin_floor=standard_d19_bracket["impossible_margin_floor"],
                    )
                )
                print(f"theorem_ids={','.join(standard_d19_bracket['theorem_ids'])}")
                standard_d19_range_request = payload["standard_d19_range_request_margin_bracket"]
                print()
                print(
                    "standard_d19_range_request_margin_bracket="
                    f"{standard_d19_range_request['name']}"
                )
                print(f"request_status={standard_d19_range_request['request_status']}")
                print(
                    "requested_context={requested_context} requested_margin={requested_margin} "
                    "theorem_backed={theorem_backed} open_gap={open_gap} "
                    "exhaustive={exhaustive} semantic_trichotomy={semantic}".format(
                        requested_context=standard_d19_range_request["requested_context"],
                        requested_margin=standard_d19_range_request["requested_margin"],
                        theorem_backed=standard_d19_range_request[
                            "theorem_backed_classification"
                        ],
                        open_gap=standard_d19_range_request["undecided_margin_open_gap"],
                        exhaustive=standard_d19_range_request["margin_status_exhaustive"],
                        semantic=standard_d19_range_request[
                            "in_range_semantic_trichotomy"
                        ],
                    )
                )
                print(f"theorem_ids={','.join(standard_d19_range_request['theorem_ids'])}")
                frontier = payload["standard_channel0_frontier_summary"]
                print()
                print("standard_channel0_frontier_summary")
                print(
                    "proved_margin={proved_margin} proved_context={proved_context} "
                    "candidate_full_contexts={candidate_contexts} "
                    "candidate_first_uncovered_gaps={frontier_gaps} "
                    "compression_bridge={compression_bridge} "
                    "status={status}".format(
                        proved_margin=frontier["proved_margin"],
                        proved_context=frontier["proved_context"],
                        candidate_contexts=tuple(frontier["candidate_full_contexts"]),
                        frontier_gaps=tuple(frontier["candidate_first_uncovered_gaps"]),
                        compression_bridge=tuple(frontier["compression_bridge_theorem_ids"]),
                        status=frontier["frontier_status"],
                    )
                )
                for plan in payload["standard_interval_candidate_plans"]:
                    print(
                        "candidate_interval_plan={name} context={context} "
                        "first_uncovered_gap={first_uncovered} bands={bands} "
                        "status={status}".format(
                            name=plan["name"],
                            context=plan["context_length"],
                            first_uncovered=plan["first_uncovered_gap"],
                            bands=plan["band_count"],
                            status=plan["theorem_status"],
                        )
                    )
                for audit in payload["standard_band_certificate_audits"]:
                    print(
                        "rational_band_audit={name} requested_context={requested} "
                        "certified_context={certified} bands={bands} "
                        "valid_bands={valid_bands} coverage={coverage} "
                        "endpoint_validity={validity} status={status}".format(
                            name=audit["source_plan_name"],
                            requested=audit["requested_context_length"],
                            certified=audit["certified_context_length"],
                            bands=audit["band_count"],
                            valid_bands=audit["valid_band_count"],
                            coverage=audit["coverage_pass"],
                            validity=audit["endpoint_validity_pass"],
                            status=audit["theorem_status"],
                        )
                    )
                print()
            if index:
                print()
            print(f"preset={item['preset']}")
            for line in item["summary_lines"]:
                print(line)
        for item in payload["phase_bank_diagnostics"]:
            print()
            print(f"phase_bank_preset={item['preset']}")
            for line in item["summary_lines"]:
                print(line)


if __name__ == "__main__":
    main()
