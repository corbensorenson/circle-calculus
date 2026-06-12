"""Tiny stride-family sparse-attention reachability sidecar.

This script reports candidate-set reachability only. It is not a neural
attention-quality, runtime, memory, or sparse-attention replacement benchmark.

Run:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from circle_math.applications.circle_ai import run_stride_family_sparse_attention_benchmark

CLAIM_BOUNDARY = (
    "This is a proof-carrying finite sparse-attention candidate-set certificate "
    "for a declared local-window plus stride-family plan. It reports covered "
    "lags, uncovered gap witnesses, no-collision budget predicates, and "
    "structured controls. It is not a neural attention-quality, long-context, "
    "throughput, runtime, memory-use, or model-quality claim."
)


def build_payload(
    *,
    sequence_length: int,
    query_count: int,
    strides: tuple[int, ...],
    wrong_strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> dict[str, Any]:
    result = run_stride_family_sparse_attention_benchmark(
        sequence_length=sequence_length,
        query_count=query_count,
        strides=strides,
        wrong_strides=wrong_strides,
        path_length=path_length,
        local_window=local_window,
    )
    return {
        "schema_id": "circle_calculus.stride_family_sparse_attention_certificate.v0",
        "claim_boundary": CLAIM_BOUNDARY,
        "benchmark_result": asdict(result),
    }


def text_results(payload: dict[str, Any]) -> str:
    result = payload["benchmark_result"]
    certificate = result["coverage_certificate"]
    return (
        "stride_family_sparse_attention "
        f"sequence_length={result['sequence_length']} "
        f"query_count={result['query_count']} "
        f"strides={result['strides']} "
        f"wrong_strides={result['wrong_strides']} "
        f"path_length={result['path_length']} "
        f"local_window={result['local_window']} "
        f"family_accuracy={result['family_accuracy']:.3f} "
        f"single_stride_accuracy={result['single_stride_accuracy']:.3f} "
        f"local_window_accuracy={result['local_window_accuracy']:.3f} "
        f"wrong_family_accuracy={result['wrong_family_accuracy']:.3f} "
        f"full_attention_accuracy={result['full_attention_accuracy']:.3f} "
        f"nonstructured_family_accuracy={result['nonstructured_family_accuracy']:.3f} "
        "nonstructured_full_attention_accuracy="
        f"{result['nonstructured_full_attention_accuracy']:.3f} "
        f"avg_family_candidates={result['average_family_candidate_count']:.3f} "
        "avg_single_stride_candidates="
        f"{result['average_single_stride_candidate_count']:.3f} "
        f"avg_local_candidates={result['average_local_candidate_count']:.3f} "
        f"avg_full_candidates={result['average_full_candidate_count']:.3f} "
        f"covered_lag_count={certificate['covered_lag_count']} "
        f"uncovered_lag_count={certificate['uncovered_lag_count']} "
        f"covered_lag_sample={certificate['covered_lags'][:12]} "
        f"uncovered_lag_sample={certificate['uncovered_lags'][:12]} "
        f"dedup_candidate_budget={certificate['candidate_budget_per_query']} "
        "theorem_side_unique_lag_candidate_count="
        f"{certificate['theorem_side_unique_lag_candidate_count']} "
        "theorem_side_unique_query_candidate_count="
        f"{certificate['theorem_side_unique_query_candidate_count']} "
        "coil_residues_no_collision="
        f"{certificate['theorem_side_coil_residues_no_collision']} "
        f"local_coil_disjoint={certificate['theorem_side_local_coil_disjoint']} "
        "lag_candidates_no_collision="
        f"{certificate['theorem_side_lag_candidates_no_collision']} "
        "predecessor_injective_on_lag_candidates="
        f"{certificate['theorem_side_predecessor_injective_on_lag_candidates']} "
        "query_candidates_no_collision="
        f"{certificate['theorem_side_query_candidates_no_collision']} "
        "dedup_candidate_budget_upper_bound="
        f"{certificate['deduplicated_candidate_budget_upper_bound']} "
        f"raw_candidate_budget_upper_bound={certificate['raw_candidate_budget_upper_bound']} "
        f"coverage_complete={certificate['coverage_complete']} "
        f"coverage_ratio={certificate['coverage_ratio']:.3f} "
        f"theorem_ids={','.join(certificate['theorem_ids'])}\n"
        f"{payload['claim_boundary']}\n"
    )


def markdown_results(payload: dict[str, Any]) -> str:
    result = payload["benchmark_result"]
    certificate = result["coverage_certificate"]
    return "\n".join(
        [
            "# Stride-Family Sparse-Attention Certificate Results",
            "",
            payload["claim_boundary"],
            "",
            "| Context | Query count | Local window | Path length | Strides | Wrong strides | Coverage complete | Coverage ratio |",
            "| ---: | ---: | ---: | ---: | --- | --- | --- | ---: |",
            (
                f"| {result['sequence_length']} | {result['query_count']} | "
                f"{result['local_window']} | {result['path_length']} | "
                f"{', '.join(str(stride) for stride in result['strides'])} | "
                f"{', '.join(str(stride) for stride in result['wrong_strides'])} | "
                f"{certificate['coverage_complete']} | {certificate['coverage_ratio']:.3f} |"
            ),
            "",
            "| Structured family | Single stride | Local only | Wrong family | Full attention | Nonstructured family | Nonstructured full |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {result['family_accuracy']:.3f} | "
                f"{result['single_stride_accuracy']:.3f} | "
                f"{result['local_window_accuracy']:.3f} | "
                f"{result['wrong_family_accuracy']:.3f} | "
                f"{result['full_attention_accuracy']:.3f} | "
                f"{result['nonstructured_family_accuracy']:.3f} | "
                f"{result['nonstructured_full_attention_accuracy']:.3f} |"
            ),
            "",
            "| Average family candidates | Average single-stride candidates | Average local candidates | Average full candidates |",
            "| ---: | ---: | ---: | ---: |",
            (
                f"| {result['average_family_candidate_count']:.3f} | "
                f"{result['average_single_stride_candidate_count']:.3f} | "
                f"{result['average_local_candidate_count']:.3f} | "
                f"{result['average_full_candidate_count']:.3f} |"
            ),
            "",
            "| Covered lag count | Uncovered lag count | Candidate budget | Raw budget bound | Deduplicated bound | Full-attention budget |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {certificate['covered_lag_count']} | "
                f"{certificate['uncovered_lag_count']} | "
                f"{certificate['candidate_budget_per_query']} | "
                f"{certificate['raw_candidate_budget_upper_bound']} | "
                f"{certificate['deduplicated_candidate_budget_upper_bound']} | "
                f"{certificate['full_attention_budget']} |"
            ),
            "",
            "| Coil residues no collision | Local/coil disjoint | Lag candidates no collision | Predecessor injective | Query candidates no collision |",
            "| --- | --- | --- | --- | --- |",
            (
                f"| {certificate['theorem_side_coil_residues_no_collision']} | "
                f"{certificate['theorem_side_local_coil_disjoint']} | "
                f"{certificate['theorem_side_lag_candidates_no_collision']} | "
                f"{certificate['theorem_side_predecessor_injective_on_lag_candidates']} | "
                f"{certificate['theorem_side_query_candidates_no_collision']} |"
            ),
            "",
            "Covered lags:",
            "",
            "```text",
            ", ".join(str(lag) for lag in certificate["covered_lags"]),
            "```",
            "",
            "First uncovered lags:",
            "",
            "```text",
            ", ".join(str(lag) for lag in certificate["uncovered_lags"][:24]),
            "```",
            "",
            "Theorem ids:",
            "",
            "```text",
            ", ".join(certificate["theorem_ids"]),
            "```",
            "",
            "Reproduce with:",
            "",
            "```bash",
            "python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py --format markdown",
            "```",
            "",
        ]
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence-length", type=int, default=120)
    parser.add_argument("--query-count", type=int, default=120)
    parser.add_argument("--strides", type=int, nargs="+", default=[7, 13])
    parser.add_argument("--wrong-strides", type=int, nargs="+", default=[5, 9])
    parser.add_argument("--path-length", type=int, default=3)
    parser.add_argument("--local-window", type=int, default=4)
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format for stdout.",
    )
    parser.add_argument("--json-out", type=Path, help="Optional JSON result file.")
    parser.add_argument("--markdown-out", type=Path, help="Optional Markdown result file.")
    args = parser.parse_args()

    payload = build_payload(
        sequence_length=args.sequence_length,
        query_count=args.query_count,
        strides=tuple(args.strides),
        wrong_strides=tuple(args.wrong_strides),
        path_length=args.path_length,
        local_window=args.local_window,
    )
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
        print(text_results(payload), end="")


if __name__ == "__main__":
    main()
