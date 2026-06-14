#!/usr/bin/env python
"""Run the finite stride-family sparse-attention coverage certifier."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from circle_math.applications import certify_stride_family_coverage


def parse_strides(raw: str) -> tuple[int, ...]:
    parts = [part.strip() for part in raw.replace(";", ",").split(",")]
    strides = tuple(int(part) for part in parts if part)
    if not strides:
        raise argparse.ArgumentTypeError("strides must contain at least one integer")
    for stride in strides:
        if stride <= 0:
            raise argparse.ArgumentTypeError("strides must be positive")
    return strides


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite lag coverage and candidate-budget accounting for a "
            "declared local-window plus stride-family sparse-attention plan."
        ),
    )
    parser.add_argument("--context", required=True, type=int, help="Finite context length.")
    parser.add_argument(
        "--strides",
        required=True,
        type=parse_strides,
        help="Comma-separated positive strides, for example 7,13.",
    )
    parser.add_argument("--path-length", required=True, type=int, help="Steps admitted per stride.")
    parser.add_argument("--local-window", required=True, type=int, help="Local lag window width.")
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable certificate JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full certificate JSON to stdout.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=12,
        help="Maximum covered/uncovered lags to show in text output.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sample(values: tuple[int, ...], limit: int) -> tuple[int, ...]:
    if limit < 0:
        raise ValueError("sample limit must be nonnegative")
    return values[:limit]


def summary_lines(payload: dict[str, Any], sample_limit: int) -> list[str]:
    coverage_status = "PASS" if payload["coverage_complete"] else "GAPS"
    lag_budget_status = (
        "exact-raw-budget"
        if payload["theorem_side_lag_candidates_no_collision"]
        else "deduplicated-below-raw"
    )
    query_budget_status = (
        "exact-raw-budget"
        if payload["theorem_side_query_candidates_no_collision"]
        else "deduplicated-below-raw"
    )
    return [
        (
            "stride_family_contract="
            f"{coverage_status} context={payload['sequence_length']} "
            f"strides={tuple(payload['strides'])} path_length={payload['path_length']} "
            f"local_window={payload['local_window']}"
        ),
        (
            f"covered_lags={payload['covered_lag_count']} "
            f"uncovered_lags={payload['uncovered_lag_count']} "
            f"uncovered_intervals={payload['uncovered_lag_interval_count']} "
            f"coverage_ratio={payload['coverage_ratio']:.6f}"
        ),
        (
            "lag_partition="
            f"covered_plus_uncovered={payload['covered_uncovered_count_sum']} "
            f"positive_lags={payload['positive_lag_count']} "
            f"partition_complete={payload['covered_uncovered_count_partition']} "
            "theorem=AIT-T0094"
        ),
        (
            "covered_count_complete="
            f"{payload['covered_count_certifies_complete']} "
            "theorem=AIT-T0095"
        ),
        (
            "candidate_budget_per_query="
            f"{payload['candidate_budget_per_query']} "
            f"raw_upper_bound={payload['raw_candidate_budget_upper_bound']} "
            f"deduplicated_bound={payload['deduplicated_candidate_budget_upper_bound']} "
            f"full_attention_budget={payload['full_attention_budget']}"
        ),
        (
            "lag_budget_status="
            f"{lag_budget_status} unique_lag_candidates="
            f"{payload['theorem_side_unique_lag_candidate_count']} "
            f"lag_no_collision={payload['theorem_side_lag_candidates_no_collision']}"
        ),
        (
            "query_budget_status="
            f"{query_budget_status} unique_query_candidates="
            f"{payload['theorem_side_unique_query_candidate_count']} "
            f"query_no_collision={payload['theorem_side_query_candidates_no_collision']}"
        ),
        (
            "structural_checks="
            f"coil_residues_no_collision={payload['theorem_side_coil_residues_no_collision']} "
            f"local_coil_disjoint={payload['theorem_side_local_coil_disjoint']} "
            "predecessor_injective="
            f"{payload['theorem_side_predecessor_injective_on_lag_candidates']} "
            "window_lt_context="
            f"{payload['theorem_side_predecessor_injective_window_context_condition']}"
        ),
        f"fixture_theorem_ids={tuple(payload['fixture_theorem_ids'])}",
        f"covered_lag_sample={sample(tuple(payload['covered_lags']), sample_limit)}",
        f"uncovered_lag_sample={sample(tuple(payload['uncovered_lags']), sample_limit)}",
        f"uncovered_lag_intervals={sample(tuple(tuple(interval) for interval in payload['uncovered_lag_intervals']), sample_limit)}",
        f"theorem_ids={tuple(payload['theorem_ids'])}",
        f"boundary={payload['note']}",
    ]


def main() -> None:
    args = parse_args()
    certificate = certify_stride_family_coverage(
        sequence_length=args.context,
        strides=args.strides,
        path_length=args.path_length,
        local_window=args.local_window,
    )
    payload = asdict(certificate)
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload, args.sample_limit):
            print(line)


if __name__ == "__main__":
    main()
