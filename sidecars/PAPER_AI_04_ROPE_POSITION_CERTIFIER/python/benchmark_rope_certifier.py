"""Run the public RoPE position distinguishability certifier presets.

This sidecar is a paper-local convenience wrapper around ``scripts/rope_certify.py``.
It emits compact text summaries for the named model-like and diagnostic
configurations used by the paper. The certificates are structural
position-contract reports, not model quality or long-context benchmark claims.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import (
    ROPE_CERTIFIER_PRESETS,
    certificate_summary_lines,
    certify_rope_positions,
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


def run_presets(presets: tuple[str, ...]) -> dict[str, Any]:
    certificates = []
    for preset in presets:
        certificate = certify_rope_positions(ROPE_CERTIFIER_PRESETS[preset])
        certificates.append(
            {
                "preset": preset,
                "summary_lines": certificate_summary_lines(certificate),
                "certificate": certificate.to_dict(),
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
        "presets": certificates,
    }


def markdown_results(payload: dict[str, Any]) -> str:
    rows = [
        "| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Common-gap pairs | Total bank pairs | Real margin | Worst gap | Theorem ids |",
        "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for item in payload["presets"]:
        cert = item["certificate"]
        config = cert["config"]
        exact = cert["exact_discrete"]
        margin = cert["real_phase_margin"]
        exact_label = "PASS" if exact["pass_exact"] else "FAIL"
        margin_label = "PASS" if margin["pass_margin"] else "WARN"
        common_gap = (
            ">= context"
            if exact["common_collision_gap"] is None
            else str(exact["common_collision_gap"])
        )
        worst_gap = "none" if margin["worst_gap"] is None else str(margin["worst_gap"])
        theorem_ids = ", ".join(cert["theorem_ids"])
        rows.append(
            "| {preset} | {head_dim} | {base:g} | {context} | {exact_label} | "
            "{common_gap} | {pair_count} | {total_count} | {margin_label} ({worst_margin:.6g} rad) | {worst_gap} | {theorem_ids} |".format(
                preset=item["preset"],
                head_dim=config["head_dim"],
                base=config["base"],
                context=config["context_length"],
                exact_label=exact_label,
                common_gap=common_gap,
                pair_count=exact["guaranteed_common_gap_collision_pair_count"],
                total_count=exact["total_bank_collision_pair_count"],
                margin_label=margin_label,
                worst_margin=margin["worst_margin_radians"],
                worst_gap=worst_gap,
                theorem_ids=theorem_ids,
            )
        )
    return "\n".join(
        [
            "# RoPE Certifier Preset Results",
            "",
            payload["claim_boundary"],
            "",
            *rows,
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
            if index:
                print()
            print(f"preset={item['preset']}")
            for line in item["summary_lines"]:
                print(line)


if __name__ == "__main__":
    main()
