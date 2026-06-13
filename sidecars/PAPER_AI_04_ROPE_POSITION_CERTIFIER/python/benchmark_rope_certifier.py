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
    certificate_summary_lines,
    certify_phase_bank_positions,
    certify_rational_preset_4099,
    certify_rope_positions,
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


def compact_phase_bank_certificate(certificate: Any) -> dict[str, Any]:
    return {
        "schema_id": certificate.schema_id,
        "config": asdict(certificate.config),
        "exact_discrete_summary": compact_exact_discrete(certificate.exact_discrete),
        "theorem_ids": certificate.theorem_ids,
        "claim_boundary": certificate.claim_boundary,
    }


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
    return {
        "schema_id": "circle_calculus.rope_certifier_preset_results.v0",
        "claim_boundary": (
            "These are proof-carrying position-contract reports for declared "
            "integer-period phase banks plus numerical real-phase margin scans. "
            "They are not model-quality, context-length, speed, memory, "
            "perplexity, or deployment claims."
        ),
        "rational_margin_certificate": certify_rational_preset_4099().to_dict(),
        "standard_interval_certificate": certify_standard_channel0_interval_seed().to_dict(),
        "standard_interval_candidate_plans": (
            plan_standard_channel0_interval_bands(
                pi_bound_preset="d4",
                margin=Fraction(1, 512),
                max_context_length=4096,
            ).to_dict(),
            plan_standard_channel0_interval_bands(
                pi_bound_preset="d6",
                margin=Fraction(1, 1024),
                max_context_length=4096,
            ).to_dict(),
            plan_standard_channel0_interval_bands(
                pi_bound_preset="d20",
                margin=Fraction(1, 131072),
                max_context_length=4096,
            ).to_dict(),
        ),
        "presets": certificates,
        "phase_bank_diagnostics": phase_bank_diagnostics,
    }


def markdown_results(payload: dict[str, Any]) -> str:
    rational = payload["rational_margin_certificate"]
    standard_interval = payload["standard_interval_certificate"]
    standard_plans = payload["standard_interval_candidate_plans"]
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
            "| Name | Ratio | Context | Certified margin | Status | Theorem ids |",
            "| --- | --- | ---: | ---: | --- | --- |",
            "| {name} | {numerator}/{denominator} | {context} | {margin:.12g} | {status} | {theorems} |".format(
                name=rational["name"],
                numerator=rational["numerator"],
                denominator=rational["denominator"],
                context=rational["context_length"],
                margin=rational["certified_margin"],
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
            "## Standard RoPE Candidate Interval Plans",
            "",
            "These exact-rational plans are generated source data for Lean interval certificates. The d4 context-333, d6 context-710, and d20 context-4096 plans are now matched by compiled Lean declarations; candidate-only rows remain unproved until matching declarations and manifest ids exist.",
            "",
            *plan_rows,
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
                print(f"theorem_ids={','.join(rational['theorem_ids'])}")
                print()
                print(f"standard_interval_certificate={standard_interval['name']}")
                print(f"pass_certificate={standard_interval['pass_certificate']}")
                print(f"certified_margin={standard_interval['certified_margin']}")
                print(f"theorem_ids={','.join(standard_interval['theorem_ids'])}")
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
