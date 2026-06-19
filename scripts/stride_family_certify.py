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
            "first_uncovered_lag_bridge="
            f"list_head={payload['first_uncovered_lag_matches_uncovered_list_head']} "
            "none_iff_complete="
            f"{payload['no_first_uncovered_lag_matches_coverage_complete']} "
            "semantic_miss="
            f"{payload['first_uncovered_lag_gap_witness']} "
            "theorems=AIT-T0098,AIT-T0099,AIT-T0100,AIT-T0101"
        ),
        (
            "uncovered_count_witness="
            f"{payload['uncovered_count_positive_matches_gap_witness']} "
            f"positive={payload['uncovered_count_positive']} "
            f"first_gap={payload['first_uncovered_lag']} "
            "theorems=AIT-T0096,AIT-T0103"
        ),
        (
            "first_uncovered_interval="
            f"start={payload['first_uncovered_lag_interval_start']} "
            f"stop={payload['first_uncovered_lag_interval_stop']} "
            f"length={payload['first_uncovered_lag_interval_length']} "
            "repair_window="
            f"{payload['first_uncovered_lag_interval_repair_window']} "
            "additional_local_slots="
            f"{payload['first_uncovered_lag_interval_additional_local_slots']} "
            "target_interval_reached="
            f"{payload['first_uncovered_interval_repair_reaches_interval']} "
            "theorems=AIT-T0104,AIT-T0171"
        ),
        (
            "first_interval_repair_next_gap="
            f"{payload['first_interval_repair_next_uncovered_lag']} "
            "still_has_gap="
            f"{payload['first_interval_repair_still_has_gap']} "
            "covers_context="
            f"{payload['first_interval_repair_covers_context']} "
            "fixture_theorems=AIT-T0166,AIT-T0167"
        ),
        (
            "largest_uncovered_interval="
            f"start={payload['largest_uncovered_interval_start']} "
            f"stop={payload['largest_uncovered_interval_stop']} "
            f"length={payload['largest_uncovered_interval_length']} "
            "repair_window="
            f"{payload['largest_uncovered_interval_repair_window']} "
            "additional_local_slots="
            f"{payload['largest_uncovered_interval_additional_local_slots']} "
            "target_interval_reached="
            f"{payload['largest_uncovered_interval_repair_reaches_interval']} "
            "next_gap_after_repair="
            f"{payload['largest_interval_repair_next_uncovered_lag']} "
            "covers_context="
            f"{payload['largest_interval_repair_covers_context']} "
            "is_tail="
            f"{payload['largest_uncovered_interval_is_tail']} "
            "source=largest_certificate_gap_interval"
        ),
        (
            "covered_count_shortfall="
            f"{payload['covered_count_shortfall']} "
            "gap_witness_equiv="
            f"{payload['covered_count_shortfall_matches_gap_witness']} "
            "theorem=AIT-T0097"
        ),
        (
            "candidate_budget_per_query="
            f"{payload['candidate_budget_per_query']} "
            f"raw_upper_bound={payload['raw_candidate_budget_upper_bound']} "
            f"deduplicated_bound={payload['deduplicated_candidate_budget_upper_bound']} "
            f"full_attention_budget={payload['full_attention_budget']}"
        ),
        (
            "raw_budget_shortfall="
            f"{payload['raw_candidate_budget_upper_bound'] < payload['positive_lag_count']} "
            "certifies_incomplete="
            f"{payload['raw_budget_shortfall_certifies_incomplete']} "
            "theorem=AIT-T0110"
        ),
        (
            "unique_lag_shortfall="
            f"{payload['theorem_side_unique_lag_candidate_count'] < payload['positive_lag_count']} "
            "certifies_incomplete="
            f"{payload['unique_lag_count_shortfall_certifies_incomplete']} "
            "gap_witness_equiv_under_candidate_range="
            f"{payload['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} "
            "period_threshold_equiv="
            f"{payload['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} "
            "theorems=AIT-T0111,AIT-T0120,AIT-T0121,AIT-T0122,AIT-T0129"
        ),
        (
            "candidate_range="
            f"{payload['theorem_side_lag_candidates_positive_in_context']} "
            "no_wrap_separated_sufficient="
            f"{payload['no_wrap_separated_candidate_range_sufficient_condition']} "
            "no_zero_residue_sufficient="
            f"{payload['no_zero_residue_candidate_range_sufficient_condition']} "
            "unique_count_complete_iff="
            f"{payload['unique_lag_count_matches_complete_under_candidate_range']} "
            "theorems=AIT-T0112,AIT-T0115,AIT-T0116,AIT-T0117,AIT-T0118,AIT-T0119"
        ),
        (
            "singleton_no_zero_period_threshold="
            f"{payload['singleton_no_zero_period_threshold']} "
            f"period={payload['singleton_stride_period']} "
            "matches_no_zero_residue_condition="
            f"{payload['singleton_no_zero_period_threshold_matches_condition']} "
            "theorems=AIT-T0126,AIT-T0127"
        ),
        (
            "family_no_zero_period_thresholds="
            f"{tuple(payload['no_zero_period_thresholds'])} "
            f"periods={tuple(payload['stride_family_periods'])} "
            "zero_residue_counts="
            f"{tuple(payload['stride_family_zero_residue_step_counts'])} "
            "counts_match_period_formula="
            f"{payload['zero_residue_step_counts_match_period_formula']} "
            "zero_residue_total_count="
            f"{payload['stride_family_zero_residue_total_step_count']} "
            "total_count_matches_sum_formula="
            f"{payload['zero_residue_total_count_matches_sum_formula']} "
            "total_count_zero_matches_no_zero_condition="
            f"{payload['zero_residue_total_count_zero_matches_no_zero_condition']} "
            "period_threshold_sufficient="
            f"{payload['no_zero_period_threshold_candidate_range_sufficient_condition']} "
            "matches_no_zero_residue_condition="
            f"{payload['no_zero_period_threshold_matches_condition']} "
            "violation_witness="
            f"({payload['no_zero_period_violation_witness_stride']}, "
            f"{payload['no_zero_period_violation_witness_period']}, "
            f"{payload['no_zero_period_violation_witness_step']}, "
            f"{payload['no_zero_period_violation_witness_residue']}) "
            "witness_matches_period_threshold="
            f"{payload['zero_residue_witness_matches_period_threshold']} "
            "witness_matches_no_zero_failure="
            f"{payload['zero_residue_witness_matches_no_zero_failure']} "
            "period_violation_matches_no_zero_failure="
            f"{payload['period_threshold_violation_matches_no_zero_failure']} "
            "witness_is_first_zero="
            f"{payload['no_zero_period_violation_witness_is_first_zero']} "
            "witness_step_positive="
            f"{payload['no_zero_period_violation_witness_step_positive']} "
            "theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133,AIT-T0134,AIT-T0135,AIT-T0136,AIT-T0137,AIT-T0138"
        ),
        (
            "candidate_range_counts="
            "covered_eq_unique="
            f"{payload['covered_count_matches_unique_lag_count_under_candidate_range']} "
            "uncovered_eq_context_minus_unique="
            f"{payload['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} "
            "theorems=AIT-T0113,AIT-T0114"
        ),
        (
            "lag_budget_status="
            f"{lag_budget_status} unique_lag_candidates="
            f"{payload['theorem_side_unique_lag_candidate_count']} "
            f"lag_dedup_loss={payload['theorem_side_lag_candidate_dedup_loss']} "
            f"lag_no_collision={payload['theorem_side_lag_candidates_no_collision']}"
        ),
        (
            "query_budget_status="
            f"{query_budget_status} unique_query_candidates="
            f"{payload['theorem_side_unique_query_candidate_count']} "
            f"query_dedup_loss={payload['theorem_side_query_candidate_dedup_loss']} "
            f"query_no_collision={payload['theorem_side_query_candidates_no_collision']} "
            "query_le_unique_lag="
            f"{payload['theorem_side_query_count_le_unique_lag_count']} "
            "theorem=AIT-T0108 "
            "query_matches_unique_lag="
            f"{payload['theorem_side_query_count_matches_unique_lag_count']} "
            "when_injective_theorem=AIT-T0109"
        ),
        (
            "dedup_loss_collision="
            f"lag_positive={payload['theorem_side_lag_candidate_dedup_loss_positive']} "
            f"lag_matches_collision={payload['lag_dedup_loss_positive_matches_collision']} "
            f"query_positive={payload['theorem_side_query_candidate_dedup_loss_positive']} "
            f"query_matches_collision={payload['query_dedup_loss_positive_matches_collision']} "
            "theorems=AIT-T0147,AIT-T0148"
        ),
        (
            "dedup_loss_accounting="
            f"lag_unique_plus_loss_eq_raw={payload['lag_dedup_loss_accounting_matches_raw']} "
            f"query_unique_plus_loss_eq_raw={payload['query_dedup_loss_accounting_matches_raw']} "
            "theorems=AIT-T0149,AIT-T0150"
        ),
        (
            "collision_pair_counts="
            f"lag={payload['theorem_side_lag_candidate_collision_pair_count']} "
            f"query={payload['theorem_side_query_candidate_collision_pair_count']} "
            "lag_zero_matches_no_collision="
            f"{payload['lag_collision_pair_count_zero_matches_no_collision']} "
            "lag_positive_matches_collision="
            f"{payload['lag_collision_pair_count_positive_matches_collision']} "
            "query_zero_matches_no_collision="
            f"{payload['query_collision_pair_count_zero_matches_no_collision']} "
            "query_positive_matches_collision="
            f"{payload['query_collision_pair_count_positive_matches_collision']} "
            "theorems=AIT-T0155,AIT-T0156,AIT-T0157,AIT-T0158 "
            "fixture_theorems=see_fixture_theorem_ids"
        ),
        (
            "collision_pair_severity="
            "lag_bounds_dedup_loss="
            f"{payload['lag_collision_pair_count_bounds_dedup_loss']} "
            "lag_excess_over_dedup_loss="
            f"{payload['lag_collision_pair_count_excess_over_dedup_loss']} "
            "query_bounds_dedup_loss="
            f"{payload['query_collision_pair_count_bounds_dedup_loss']} "
            "query_excess_over_dedup_loss="
            f"{payload['query_collision_pair_count_excess_over_dedup_loss']} "
            "theorems=AIT-T0159,AIT-T0160"
        ),
        (
            "first_gap_local_repair="
            f"shortfall={payload['first_uncovered_lag_local_window_shortfall']} "
            f"needed_window={payload['first_uncovered_lag_repair_window']} "
            "current_window_below_first_gap="
            f"{payload['first_uncovered_lag_exceeds_local_window']} "
            "repair_window_reaches_first_gap="
            f"{payload['first_uncovered_lag_repair_window_reaches']} "
            "repair_window_covers_context="
            f"{payload['first_uncovered_lag_repair_window_covers_context']} "
            "repair_window_is_final_positive_lag="
            f"{payload['first_gap_repair_window_is_final_positive_lag']} "
            "repair_threshold_matches_final_lag="
            f"{payload['first_gap_repair_threshold_matches_final_lag']} "
            "theorems=AIT-T0161,AIT-T0162,AIT-T0164,AIT-T0165 "
            "fixture_theorems=AIT-T0163"
        ),
        (
            "local_window_complete_threshold="
            f"threshold={payload['local_window_complete_coverage_threshold']} "
            f"shortfall={payload['local_window_complete_coverage_shortfall']} "
            "reaches_threshold="
            f"{payload['local_window_reaches_complete_coverage_threshold']} "
            "threshold_certifies_complete="
            f"{payload['local_window_threshold_certifies_complete']} "
            "exact_local_minimum="
            f"{payload['local_window_complete_threshold_is_exact_local_minimum']} "
            "first_gap_repair_reaches_threshold="
            f"{payload['first_gap_repair_window_reaches_complete_threshold']} "
            "theorems=AIT-T0023,AIT-T0034"
        ),
        (
            "complete_local_repair="
            f"window={payload['complete_repair_window']} "
            "additional_slots="
            f"{payload['complete_repair_window_additional_local_slots']} "
            "covers_context="
            f"{payload['complete_repair_window_covers_context']} "
            "uses_dense_threshold="
            f"{payload['complete_repair_window_uses_dense_threshold']} "
            "exact_local_minimum="
            f"{payload['local_window_complete_threshold_is_exact_local_minimum']} "
            "minimal_for_declared_family="
            f"{payload['complete_repair_window_minimal_for_declared_stride_family']} "
            "minimal_witness_lag="
            f"{payload['complete_repair_window_minimal_witness_lag']} "
            "theorems=AIT-T0023,AIT-T0034 fixture_theorems=AIT-T0168,AIT-T0169,AIT-T0170"
        ),
        (
            "interval_repair_plan="
            f"steps={payload['interval_repair_plan_step_count']} "
            f"final_window={payload['interval_repair_plan_final_window']} "
            f"covers_context={payload['interval_repair_plan_covers_context']} "
            "strictly_progresses="
            f"{payload['interval_repair_plan_strictly_progresses']} "
            "first_step="
            f"{tuple(payload['interval_repair_plan'][0]) if payload['interval_repair_plan'] else None} "
            "last_step="
            f"{tuple(payload['interval_repair_plan'][-1]) if payload['interval_repair_plan'] else None} "
            "source=successive_first_uncovered_intervals"
        ),
        (
            "unique_query_shortfall="
            f"{payload['theorem_side_unique_query_candidate_count'] < payload['positive_lag_count']} "
            "gap_witness_equiv_under_candidate_range_and_injective="
            f"{payload['unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective']} "
            "no_wrap_structural_equiv="
            f"{payload['unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated']} "
            "no_zero_structural_equiv="
            f"{payload['unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue']} "
            "period_threshold_equiv="
            f"{payload['unique_query_count_shortfall_matches_gap_witness_under_period_threshold']} "
            "theorems=AIT-T0123,AIT-T0124,AIT-T0125,AIT-T0130"
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
    payload["schema_id"] = "circle_calculus.stride_family_sparse_attention_certificate.v0"
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload, args.sample_limit):
            print(line)


if __name__ == "__main__":
    main()
