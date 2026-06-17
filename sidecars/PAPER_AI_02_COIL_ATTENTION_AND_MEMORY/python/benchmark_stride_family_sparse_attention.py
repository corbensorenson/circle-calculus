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
from typing import Any, Sequence

from circle_math.applications.circle_ai import (
    certify_stride_family_coverage,
    run_stride_family_sparse_attention_benchmark,
)

CLAIM_BOUNDARY = (
    "This is a proof-carrying finite sparse-attention candidate-set certificate "
    "for a declared local-window plus stride-family plan. It reports covered "
    "lags, uncovered gap witnesses, no-collision budget predicates, and "
    "structured controls. It is not a neural attention-quality, long-context, "
    "throughput, runtime, memory-use, or model-quality claim."
)

CORE_COVERAGE_THEOREM_IDS = (
    "AIT-T0080",
    "AIT-T0081",
    "AIT-T0082",
    "AIT-T0083",
    "AIT-T0090",
    "AIT-T0092",
    "AIT-T0093",
    "AIT-T0094",
    "AIT-T0095",
    "AIT-T0096",
    "AIT-T0097",
    "AIT-T0098",
    "AIT-T0099",
    "AIT-T0100",
    "AIT-T0101",
    "AIT-T0103",
    "AIT-T0110",
    "AIT-T0111",
    "AIT-T0112",
    "AIT-T0113",
    "AIT-T0114",
    "AIT-T0115",
    "AIT-T0116",
    "AIT-T0117",
    "AIT-T0118",
    "AIT-T0119",
    "AIT-T0120",
    "AIT-T0121",
    "AIT-T0122",
    "AIT-T0123",
    "AIT-T0124",
    "AIT-T0125",
    "AIT-T0126",
    "AIT-T0127",
    "AIT-T0128",
    "AIT-T0129",
    "AIT-T0130",
    "AIT-T0131",
    "AIT-T0132",
    "AIT-T0133",
    "AIT-T0134",
    "AIT-T0135",
    "AIT-T0136",
)

PLANNER_STYLE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "plan_id": "default_gap_fixture_120",
        "description": "Small public gappy fixture used by the theorem-side gap witnesses.",
        "sequence_length": 120,
        "strides": (7, 13),
        "path_length": 3,
        "local_window": 4,
    },
    {
        "plan_id": "complete_toy_fixture_9",
        "description": "Compact complete-coverage fixture with an empty uncovered-lag list.",
        "sequence_length": 9,
        "strides": (3, 4, 7),
        "path_length": 2,
        "local_window": 2,
    },
    {
        "plan_id": "singleton_period_probe_12",
        "description": (
            "Single-stride probe where path length stops before the finite coil "
            "period, so the no-zero residue check is certified by the period threshold."
        ),
        "sequence_length": 12,
        "strides": (4,),
        "path_length": 2,
        "local_window": 1,
    },
    {
        "plan_id": "long_context_no_wrap_probe_4096",
        "description": (
            "4096-token probe with separated strides; useful for inspecting exact "
            "raw-budget preservation without implying broad coverage."
        ),
        "sequence_length": 4096,
        "strides": (33, 160, 800),
        "path_length": 4,
        "local_window": 32,
    },
    {
        "plan_id": "long_context_coprime_probe_8192",
        "description": (
            "8192-token probe with coprime-style separated long strides; useful "
            "for budget and gap inspection on a larger declared context."
        ),
        "sequence_length": 8192,
        "strides": (127, 509, 1021, 2039),
        "path_length": 8,
        "local_window": 64,
    },
)


def _sample(values: Sequence[Any], limit: int) -> tuple[Any, ...]:
    return tuple(values[:limit])


def compact_planner_certificate(spec: dict[str, Any]) -> dict[str, Any]:
    """Return a compact report row for a declared sparse-attention plan.

    The full exact certificate for any row can be reproduced through
    ``scripts/stride_family_certify.py`` using the same fields. The compact row
    is kept short enough for committed sidecar results and the Living Book.
    """
    certificate = certify_stride_family_coverage(
        sequence_length=spec["sequence_length"],
        strides=spec["strides"],
        path_length=spec["path_length"],
        local_window=spec["local_window"],
    )
    return {
        "plan_id": spec["plan_id"],
        "description": spec["description"],
        "sequence_length": certificate.sequence_length,
        "strides": certificate.strides,
        "path_length": certificate.path_length,
        "local_window": certificate.local_window,
        "coverage_complete": certificate.coverage_complete,
        "coverage_ratio": certificate.coverage_ratio,
        "covered_lag_count": certificate.covered_lag_count,
        "uncovered_lag_count": certificate.uncovered_lag_count,
        "uncovered_count_positive": certificate.uncovered_count_positive,
        "first_uncovered_lag": certificate.first_uncovered_lag,
        "uncovered_count_positive_matches_gap_witness": (
            certificate.uncovered_count_positive_matches_gap_witness
        ),
        "first_uncovered_lag_matches_uncovered_list_head": (
            certificate.first_uncovered_lag_matches_uncovered_list_head
        ),
        "no_first_uncovered_lag_matches_coverage_complete": (
            certificate.no_first_uncovered_lag_matches_coverage_complete
        ),
        "first_uncovered_lag_gap_witness": certificate.first_uncovered_lag_gap_witness,
        "positive_lag_count": certificate.positive_lag_count,
        "covered_uncovered_count_sum": certificate.covered_uncovered_count_sum,
        "covered_uncovered_count_partition": certificate.covered_uncovered_count_partition,
        "covered_count_certifies_complete": certificate.covered_count_certifies_complete,
        "covered_count_shortfall": certificate.covered_count_shortfall,
        "covered_count_shortfall_matches_gap_witness": (
            certificate.covered_count_shortfall_matches_gap_witness
        ),
        "uncovered_lag_interval_count": certificate.uncovered_lag_interval_count,
        "candidate_budget_per_query": certificate.candidate_budget_per_query,
        "raw_candidate_budget_upper_bound": certificate.raw_candidate_budget_upper_bound,
        "raw_budget_shortfall_certifies_incomplete": (
            certificate.raw_budget_shortfall_certifies_incomplete
        ),
        "deduplicated_candidate_budget_upper_bound": (
            certificate.deduplicated_candidate_budget_upper_bound
        ),
        "theorem_side_unique_lag_candidate_count": (
            certificate.theorem_side_unique_lag_candidate_count
        ),
        "theorem_side_lag_candidates_positive_in_context": (
            certificate.theorem_side_lag_candidates_positive_in_context
        ),
        "no_wrap_separated_candidate_range_sufficient_condition": (
            certificate.no_wrap_separated_candidate_range_sufficient_condition
        ),
        "no_zero_residue_candidate_range_sufficient_condition": (
            certificate.no_zero_residue_candidate_range_sufficient_condition
        ),
        "singleton_stride_period": certificate.singleton_stride_period,
        "singleton_no_zero_period_threshold": (
            certificate.singleton_no_zero_period_threshold
        ),
        "singleton_no_zero_period_threshold_matches_condition": (
            certificate.singleton_no_zero_period_threshold_matches_condition
        ),
        "stride_family_periods": certificate.stride_family_periods,
        "no_zero_period_thresholds": certificate.no_zero_period_thresholds,
        "stride_family_zero_residue_step_counts": (
            certificate.stride_family_zero_residue_step_counts
        ),
        "zero_residue_step_counts_match_period_formula": (
            certificate.zero_residue_step_counts_match_period_formula
        ),
        "no_zero_period_threshold_candidate_range_sufficient_condition": (
            certificate.no_zero_period_threshold_candidate_range_sufficient_condition
        ),
        "no_zero_period_threshold_matches_condition": (
            certificate.no_zero_period_threshold_matches_condition
        ),
        "no_zero_period_violation_witness_stride": (
            certificate.no_zero_period_violation_witness_stride
        ),
        "no_zero_period_violation_witness_period": (
            certificate.no_zero_period_violation_witness_period
        ),
        "no_zero_period_violation_witness_step": (
            certificate.no_zero_period_violation_witness_step
        ),
        "no_zero_period_violation_witness_residue": (
            certificate.no_zero_period_violation_witness_residue
        ),
        "zero_residue_witness_matches_period_threshold": (
            certificate.zero_residue_witness_matches_period_threshold
        ),
        "zero_residue_witness_matches_no_zero_failure": (
            certificate.zero_residue_witness_matches_no_zero_failure
        ),
        "period_threshold_violation_matches_no_zero_failure": (
            certificate.period_threshold_violation_matches_no_zero_failure
        ),
        "no_zero_period_violation_witness_is_first_zero": (
            certificate.no_zero_period_violation_witness_is_first_zero
        ),
        "no_zero_period_violation_witness_step_positive": (
            certificate.no_zero_period_violation_witness_step_positive
        ),
        "unique_lag_count_shortfall_certifies_incomplete": (
            certificate.unique_lag_count_shortfall_certifies_incomplete
        ),
        "unique_lag_count_shortfall_matches_gap_witness_under_candidate_range": (
            certificate.unique_lag_count_shortfall_matches_gap_witness_under_candidate_range
        ),
        "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold": (
            certificate.unique_lag_count_shortfall_matches_gap_witness_under_period_threshold
        ),
        "unique_lag_count_matches_complete_under_candidate_range": (
            certificate.unique_lag_count_matches_complete_under_candidate_range
        ),
        "covered_count_matches_unique_lag_count_under_candidate_range": (
            certificate.covered_count_matches_unique_lag_count_under_candidate_range
        ),
        "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range": (
            certificate.uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range
        ),
        "full_attention_budget": certificate.full_attention_budget,
        "candidate_budget_ratio": (
            certificate.candidate_budget_per_query / certificate.full_attention_budget
        ),
        "raw_budget_survives_lag_dedup": (
            certificate.theorem_side_lag_candidates_no_collision
            and certificate.theorem_side_unique_lag_candidate_count
            == certificate.raw_candidate_budget_upper_bound
        ),
        "raw_budget_survives_query_dedup": (
            certificate.theorem_side_query_candidates_no_collision
            and certificate.theorem_side_unique_query_candidate_count
            == certificate.raw_candidate_budget_upper_bound
        ),
        "coil_residues_no_collision": certificate.theorem_side_coil_residues_no_collision,
        "local_coil_disjoint": certificate.theorem_side_local_coil_disjoint,
        "covered_lag_sample": _sample(certificate.covered_lags, 24),
        "uncovered_lag_sample": _sample(certificate.uncovered_lags, 24),
        "uncovered_lag_interval_sample": _sample(certificate.uncovered_lag_intervals, 12),
        "fixture_theorem_ids": certificate.fixture_theorem_ids,
        "core_coverage_theorem_ids": CORE_COVERAGE_THEOREM_IDS,
        "reproduce_command": (
            "python scripts/stride_family_certify.py "
            f"--context {certificate.sequence_length} "
            f"--strides {','.join(str(stride) for stride in certificate.strides)} "
            f"--path-length {certificate.path_length} "
            f"--local-window {certificate.local_window}"
        ),
        "note": (
            "Compact planner row only; rerun the reproduce_command for the full "
            "finite covered/uncovered-lag certificate. This is not an attention-quality, "
            "runtime, memory-use, or long-context performance claim."
        ),
    }


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
        "complete_fixture_certificate": asdict(
            certify_stride_family_coverage(
                sequence_length=9,
                strides=(3, 4, 7),
                path_length=2,
                local_window=2,
            )
        ),
        "planner_style_certificates": tuple(
            compact_planner_certificate(spec) for spec in PLANNER_STYLE_SPECS
        ),
    }


def text_results(payload: dict[str, Any]) -> str:
    result = payload["benchmark_result"]
    certificate = result["coverage_certificate"]
    complete = payload["complete_fixture_certificate"]
    planner = payload["planner_style_certificates"]
    planner_text = "\n".join(
        (
            "stride_family_sparse_attention_plan "
            f"plan_id={row['plan_id']} "
            f"context={row['sequence_length']} "
            f"local_window={row['local_window']} "
            f"path_length={row['path_length']} "
            f"strides={row['strides']} "
            f"coverage_complete={row['coverage_complete']} "
            f"coverage_ratio={row['coverage_ratio']:.6f} "
            f"candidate_budget={row['candidate_budget_per_query']} "
            f"full_attention_budget={row['full_attention_budget']} "
            f"budget_ratio={row['candidate_budget_ratio']:.6f} "
            f"uncovered_lag_count={row['uncovered_lag_count']} "
            f"first_uncovered_lag={row['first_uncovered_lag']} "
            "first_gap_is_list_head="
            f"{row['first_uncovered_lag_matches_uncovered_list_head']} "
            "no_first_gap_matches_complete="
            f"{row['no_first_uncovered_lag_matches_coverage_complete']} "
            "first_gap_semantic_miss="
            f"{row['first_uncovered_lag_gap_witness']} "
            "uncovered_count_witness="
            f"{row['uncovered_count_positive_matches_gap_witness']} "
            f"covered_count_shortfall={row['covered_count_shortfall']} "
            "shortfall_gap_witness="
            f"{row['covered_count_shortfall_matches_gap_witness']} "
            f"lag_partition={row['covered_uncovered_count_sum']}/"
            f"{row['positive_lag_count']} "
            f"partition_complete={row['covered_uncovered_count_partition']} "
            f"gap_interval_count={row['uncovered_lag_interval_count']} "
            "raw_budget_shortfall_certifies_incomplete="
            f"{row['raw_budget_shortfall_certifies_incomplete']} "
            "unique_lag_count_shortfall_certifies_incomplete="
            f"{row['unique_lag_count_shortfall_certifies_incomplete']} "
            "unique_lag_count_shortfall_matches_gap_witness="
            f"{row['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} "
            "unique_lag_period_threshold_equiv="
            f"{row['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} "
            "candidate_range="
            f"{row['theorem_side_lag_candidates_positive_in_context']} "
            "no_wrap_sufficient="
            f"{row['no_wrap_separated_candidate_range_sufficient_condition']} "
            "no_zero_sufficient="
            f"{row['no_zero_residue_candidate_range_sufficient_condition']} "
            "singleton_period="
            f"{row['singleton_stride_period']} "
            "singleton_period_threshold="
            f"{row['singleton_no_zero_period_threshold']} "
            "singleton_threshold_matches_no_zero="
            f"{row['singleton_no_zero_period_threshold_matches_condition']} "
            f"family_periods={row['stride_family_periods']} "
            f"family_period_thresholds={row['no_zero_period_thresholds']} "
            f"zero_residue_counts={row['stride_family_zero_residue_step_counts']} "
            "zero_residue_count_formula="
            f"{row['zero_residue_step_counts_match_period_formula']} "
            "family_period_threshold_sufficient="
            f"{row['no_zero_period_threshold_candidate_range_sufficient_condition']} "
            "family_threshold_matches_no_zero="
            f"{row['no_zero_period_threshold_matches_condition']} "
            "zero_witness_matches_no_zero_failure="
            f"{row['zero_residue_witness_matches_no_zero_failure']} "
            "period_violation_matches_no_zero_failure="
            f"{row['period_threshold_violation_matches_no_zero_failure']} "
            "witness_is_first_zero="
            f"{row['no_zero_period_violation_witness_is_first_zero']} "
            "witness_step_positive="
            f"{row['no_zero_period_violation_witness_step_positive']} "
            "unique_count_complete_iff="
            f"{row['unique_lag_count_matches_complete_under_candidate_range']} "
            "covered_eq_unique="
            f"{row['covered_count_matches_unique_lag_count_under_candidate_range']} "
            "uncovered_eq_context_minus_unique="
            f"{row['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} "
            f"raw_budget_survives_lag_dedup={row['raw_budget_survives_lag_dedup']} "
            f"raw_budget_survives_query_dedup={row['raw_budget_survives_query_dedup']} "
            f"fixture_theorem_ids={','.join(row['fixture_theorem_ids'])} "
            f"core_theorem_ids={','.join(row['core_coverage_theorem_ids'])}"
        )
        for row in planner
    )
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
        f"first_uncovered_lag={certificate['first_uncovered_lag']} "
        "first_gap_is_list_head="
        f"{certificate['first_uncovered_lag_matches_uncovered_list_head']} "
        "no_first_gap_matches_complete="
        f"{certificate['no_first_uncovered_lag_matches_coverage_complete']} "
        "first_gap_semantic_miss="
        f"{certificate['first_uncovered_lag_gap_witness']} "
        "uncovered_count_witness="
        f"{certificate['uncovered_count_positive_matches_gap_witness']} "
        f"covered_count_shortfall={certificate['covered_count_shortfall']} "
        "shortfall_gap_witness="
        f"{certificate['covered_count_shortfall_matches_gap_witness']} "
        "lag_partition="
        f"{certificate['covered_uncovered_count_sum']}/"
        f"{certificate['positive_lag_count']} "
        "partition_complete="
        f"{certificate['covered_uncovered_count_partition']} "
        f"uncovered_lag_interval_count={certificate['uncovered_lag_interval_count']} "
        f"uncovered_lag_intervals={certificate['uncovered_lag_intervals']} "
        f"covered_lag_sample={certificate['covered_lags'][:12]} "
        f"uncovered_lag_sample={certificate['uncovered_lags'][:12]} "
        f"dedup_candidate_budget={certificate['candidate_budget_per_query']} "
        "theorem_side_unique_lag_candidate_count="
        f"{certificate['theorem_side_unique_lag_candidate_count']} "
        "theorem_side_unique_query_candidate_count="
        f"{certificate['theorem_side_unique_query_candidate_count']} "
        "query_count_le_unique_lag_count="
        f"{certificate['theorem_side_query_count_le_unique_lag_count']} "
        "query_count_matches_unique_lag_count="
        f"{certificate['theorem_side_query_count_matches_unique_lag_count']} "
        "unique_query_shortfall_matches_gap_witness="
        f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective']} "
        "unique_query_no_wrap_equiv="
        f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated']} "
        "unique_query_no_zero_equiv="
        f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue']} "
        "unique_query_period_threshold_equiv="
        f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_period_threshold']} "
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
        "raw_budget_shortfall_certifies_incomplete="
        f"{certificate['raw_budget_shortfall_certifies_incomplete']} "
        "unique_lag_count_shortfall_certifies_incomplete="
        f"{certificate['unique_lag_count_shortfall_certifies_incomplete']} "
        "unique_lag_count_shortfall_matches_gap_witness="
        f"{certificate['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} "
        "unique_lag_period_threshold_equiv="
        f"{certificate['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} "
        "candidate_range="
        f"{certificate['theorem_side_lag_candidates_positive_in_context']} "
        "no_wrap_sufficient="
        f"{certificate['no_wrap_separated_candidate_range_sufficient_condition']} "
        "no_zero_sufficient="
        f"{certificate['no_zero_residue_candidate_range_sufficient_condition']} "
        "singleton_period="
        f"{certificate['singleton_stride_period']} "
        "singleton_period_threshold="
        f"{certificate['singleton_no_zero_period_threshold']} "
        "singleton_threshold_matches_no_zero="
        f"{certificate['singleton_no_zero_period_threshold_matches_condition']} "
        f"family_periods={certificate['stride_family_periods']} "
        f"family_period_thresholds={certificate['no_zero_period_thresholds']} "
        f"zero_residue_counts={certificate['stride_family_zero_residue_step_counts']} "
        "zero_residue_count_formula="
        f"{certificate['zero_residue_step_counts_match_period_formula']} "
        "family_period_threshold_sufficient="
        f"{certificate['no_zero_period_threshold_candidate_range_sufficient_condition']} "
        "family_threshold_matches_no_zero="
        f"{certificate['no_zero_period_threshold_matches_condition']} "
        "zero_witness_matches_no_zero_failure="
        f"{certificate['zero_residue_witness_matches_no_zero_failure']} "
        "period_violation_matches_no_zero_failure="
        f"{certificate['period_threshold_violation_matches_no_zero_failure']} "
        "witness_is_first_zero="
        f"{certificate['no_zero_period_violation_witness_is_first_zero']} "
        "witness_step_positive="
        f"{certificate['no_zero_period_violation_witness_step_positive']} "
        "unique_count_complete_iff="
        f"{certificate['unique_lag_count_matches_complete_under_candidate_range']} "
        "covered_eq_unique="
        f"{certificate['covered_count_matches_unique_lag_count_under_candidate_range']} "
        "uncovered_eq_context_minus_unique="
        f"{certificate['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} "
        f"coverage_complete={certificate['coverage_complete']} "
        f"coverage_ratio={certificate['coverage_ratio']:.3f} "
        f"fixture_theorem_ids={','.join(certificate['fixture_theorem_ids'])} "
        f"theorem_ids={','.join(certificate['theorem_ids'])}\n"
        "stride_family_sparse_attention_complete_fixture "
        f"sequence_length={complete['sequence_length']} "
        f"strides={complete['strides']} "
        f"path_length={complete['path_length']} "
        f"local_window={complete['local_window']} "
        f"covered_lags={complete['covered_lags']} "
        f"uncovered_lag_count={complete['uncovered_lag_count']} "
        f"first_uncovered_lag={complete['first_uncovered_lag']} "
        "first_gap_is_list_head="
        f"{complete['first_uncovered_lag_matches_uncovered_list_head']} "
        "no_first_gap_matches_complete="
        f"{complete['no_first_uncovered_lag_matches_coverage_complete']} "
        "first_gap_semantic_miss="
        f"{complete['first_uncovered_lag_gap_witness']} "
        "uncovered_count_witness="
        f"{complete['uncovered_count_positive_matches_gap_witness']} "
        f"covered_count_shortfall={complete['covered_count_shortfall']} "
        "shortfall_gap_witness="
        f"{complete['covered_count_shortfall_matches_gap_witness']} "
        f"coverage_complete={complete['coverage_complete']} "
        "theorem_side_unique_lag_candidate_count="
        f"{complete['theorem_side_unique_lag_candidate_count']} "
        "theorem_side_unique_query_candidate_count="
        f"{complete['theorem_side_unique_query_candidate_count']} "
        "query_count_le_unique_lag_count="
        f"{complete['theorem_side_query_count_le_unique_lag_count']} "
        "query_count_matches_unique_lag_count="
        f"{complete['theorem_side_query_count_matches_unique_lag_count']} "
        "unique_query_shortfall_matches_gap_witness="
        f"{complete['unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective']} "
        "unique_query_no_wrap_equiv="
        f"{complete['unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated']} "
        "unique_query_no_zero_equiv="
        f"{complete['unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue']} "
        "unique_query_period_threshold_equiv="
        f"{complete['unique_query_count_shortfall_matches_gap_witness_under_period_threshold']} "
        f"raw_candidate_budget_upper_bound={complete['raw_candidate_budget_upper_bound']} "
        "raw_budget_shortfall_certifies_incomplete="
        f"{complete['raw_budget_shortfall_certifies_incomplete']} "
        "unique_lag_count_shortfall_certifies_incomplete="
        f"{complete['unique_lag_count_shortfall_certifies_incomplete']} "
        "unique_lag_count_shortfall_matches_gap_witness="
        f"{complete['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} "
        "unique_lag_period_threshold_equiv="
        f"{complete['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} "
        "candidate_range="
        f"{complete['theorem_side_lag_candidates_positive_in_context']} "
        "no_wrap_sufficient="
        f"{complete['no_wrap_separated_candidate_range_sufficient_condition']} "
        "no_zero_sufficient="
        f"{complete['no_zero_residue_candidate_range_sufficient_condition']} "
        "singleton_period="
        f"{complete['singleton_stride_period']} "
        "singleton_period_threshold="
        f"{complete['singleton_no_zero_period_threshold']} "
        "singleton_threshold_matches_no_zero="
        f"{complete['singleton_no_zero_period_threshold_matches_condition']} "
        f"family_periods={complete['stride_family_periods']} "
        f"family_period_thresholds={complete['no_zero_period_thresholds']} "
        f"zero_residue_counts={complete['stride_family_zero_residue_step_counts']} "
        "zero_residue_count_formula="
        f"{complete['zero_residue_step_counts_match_period_formula']} "
        "family_period_threshold_sufficient="
        f"{complete['no_zero_period_threshold_candidate_range_sufficient_condition']} "
        "family_threshold_matches_no_zero="
        f"{complete['no_zero_period_threshold_matches_condition']} "
        "zero_witness_matches_no_zero_failure="
        f"{complete['zero_residue_witness_matches_no_zero_failure']} "
        "period_violation_matches_no_zero_failure="
        f"{complete['period_threshold_violation_matches_no_zero_failure']} "
        "witness_is_first_zero="
        f"{complete['no_zero_period_violation_witness_is_first_zero']} "
        "witness_step_positive="
        f"{complete['no_zero_period_violation_witness_step_positive']} "
        "unique_count_complete_iff="
        f"{complete['unique_lag_count_matches_complete_under_candidate_range']} "
        "covered_eq_unique="
        f"{complete['covered_count_matches_unique_lag_count_under_candidate_range']} "
        "uncovered_eq_context_minus_unique="
        f"{complete['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} "
        f"fixture_theorem_ids={','.join(complete['fixture_theorem_ids'])}\n"
        f"{planner_text}\n"
        f"{payload['claim_boundary']}\n"
    )


def markdown_results(payload: dict[str, Any]) -> str:
    result = payload["benchmark_result"]
    certificate = result["coverage_certificate"]
    complete = payload["complete_fixture_certificate"]
    planner = payload["planner_style_certificates"]
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
            "| Covered lag count | Uncovered lag count | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Positive lags | Partition complete | Uncovered intervals | Candidate budget | Raw budget bound | Raw shortfall certifies incomplete | Unique lag candidates | Candidate range | No-wrap sufficient | No-zero sufficient | Singleton period | Singleton period threshold | Singleton threshold matches no-zero | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Unique shortfall iff gap | Unique shortfall iff gap under period threshold | Deduplicated bound | Full-attention budget |",
            "| ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: |",
            (
                f"| {certificate['covered_lag_count']} | "
                f"{certificate['uncovered_lag_count']} | "
                f"{certificate['first_uncovered_lag']} | "
                f"{certificate['first_uncovered_lag_matches_uncovered_list_head']} | "
                f"{certificate['no_first_uncovered_lag_matches_coverage_complete']} | "
                f"{certificate['first_uncovered_lag_gap_witness']} | "
                f"{certificate['uncovered_count_positive_matches_gap_witness']} | "
                f"{certificate['covered_count_shortfall']} | "
                f"{certificate['covered_count_shortfall_matches_gap_witness']} | "
                f"{certificate['positive_lag_count']} | "
                f"{certificate['covered_uncovered_count_partition']} | "
                f"{certificate['uncovered_lag_interval_count']} | "
                f"{certificate['candidate_budget_per_query']} | "
                f"{certificate['raw_candidate_budget_upper_bound']} | "
                f"{certificate['raw_budget_shortfall_certifies_incomplete']} | "
                f"{certificate['theorem_side_unique_lag_candidate_count']} | "
                f"{certificate['theorem_side_lag_candidates_positive_in_context']} | "
                f"{certificate['no_wrap_separated_candidate_range_sufficient_condition']} | "
                f"{certificate['no_zero_residue_candidate_range_sufficient_condition']} | "
                f"{certificate['singleton_stride_period']} | "
                f"{certificate['singleton_no_zero_period_threshold']} | "
                f"{certificate['singleton_no_zero_period_threshold_matches_condition']} | "
                f"{certificate['unique_lag_count_matches_complete_under_candidate_range']} | "
                f"{certificate['covered_count_matches_unique_lag_count_under_candidate_range']} | "
                f"{certificate['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} | "
                f"{certificate['unique_lag_count_shortfall_certifies_incomplete']} | "
                f"{certificate['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} | "
                f"{certificate['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} | "
                f"{certificate['deduplicated_candidate_budget_upper_bound']} | "
                f"{certificate['full_attention_budget']} |"
            ),
            "",
            "| Coil residues no collision | Local/coil disjoint | Lag candidates no collision | Predecessor injective | Query candidates no collision | Query count <= unique lag count | Query count = unique lag count | Query shortfall iff gap under candidate-range+injective | Query shortfall iff gap under no-wrap | Query shortfall iff gap under no-zero | Query shortfall iff gap under period threshold |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {certificate['theorem_side_coil_residues_no_collision']} | "
                f"{certificate['theorem_side_local_coil_disjoint']} | "
                f"{certificate['theorem_side_lag_candidates_no_collision']} | "
                f"{certificate['theorem_side_predecessor_injective_on_lag_candidates']} | "
                f"{certificate['theorem_side_query_candidates_no_collision']} | "
                f"{certificate['theorem_side_query_count_le_unique_lag_count']} | "
                f"{certificate['theorem_side_query_count_matches_unique_lag_count']} | "
                f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective']} | "
                f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated']} | "
                f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue']} | "
                f"{certificate['unique_query_count_shortfall_matches_gap_witness_under_period_threshold']} |"
            ),
            "",
            "Family no-zero period threshold:",
            "",
            "| Periods | Thresholds | Zero-residue counts | Count formula | Period threshold sufficient | Matches no-zero residue scan | Zero witness iff no-zero failure | Period violation iff no-zero failure | Witness is first zero | Witness step positive |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {', '.join(str(period) for period in certificate['stride_family_periods'])} | "
                f"{', '.join(str(flag) for flag in certificate['no_zero_period_thresholds'])} | "
                f"{', '.join(str(count) for count in certificate['stride_family_zero_residue_step_counts'])} | "
                f"{certificate['zero_residue_step_counts_match_period_formula']} | "
                f"{certificate['no_zero_period_threshold_candidate_range_sufficient_condition']} | "
                f"{certificate['no_zero_period_threshold_matches_condition']} | "
                f"{certificate['zero_residue_witness_matches_no_zero_failure']} | "
                f"{certificate['period_threshold_violation_matches_no_zero_failure']} | "
                f"{certificate['no_zero_period_violation_witness_is_first_zero']} | "
                f"{certificate['no_zero_period_violation_witness_step_positive']} |"
            ),
            "",
            "Covered lags:",
            "",
            "```text",
            ", ".join(str(lag) for lag in certificate["covered_lags"]),
            "```",
            "",
            "Default fixture theorem ids:",
            "",
            "```text",
            ", ".join(certificate["fixture_theorem_ids"]),
            "```",
            "",
            "First uncovered lags:",
            "",
            "```text",
            ", ".join(str(lag) for lag in certificate["uncovered_lags"][:24]),
            "```",
            "",
            "Uncovered lag intervals:",
            "",
            "```text",
            ", ".join(
                f"{start}..{stop}" if start != stop else str(start)
                for start, stop in certificate["uncovered_lag_intervals"]
            ),
            "```",
            "",
            "Complete sparse-family fixture:",
            "",
            "| Context | Local window | Path length | Strides | Coverage complete | Uncovered lags | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Raw budget | Raw shortfall certifies incomplete | Unique lag candidates | Candidate range | No-wrap sufficient | No-zero sufficient | Singleton period | Singleton period threshold | Singleton threshold matches no-zero | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Unique shortfall iff gap | Unique shortfall iff gap under period threshold | Unique query candidates | Query <= unique lag | Query = unique lag | Query shortfall iff gap | Query no-wrap iff | Query no-zero iff | Query period-threshold iff | Fixture theorem ids |",
            "| ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
            (
                f"| {complete['sequence_length']} | {complete['local_window']} | "
                f"{complete['path_length']} | "
                f"{', '.join(str(stride) for stride in complete['strides'])} | "
                f"{complete['coverage_complete']} | "
                f"{complete['uncovered_lag_count']} | "
                f"{complete['first_uncovered_lag']} | "
                f"{complete['first_uncovered_lag_matches_uncovered_list_head']} | "
                f"{complete['no_first_uncovered_lag_matches_coverage_complete']} | "
                f"{complete['first_uncovered_lag_gap_witness']} | "
                f"{complete['uncovered_count_positive_matches_gap_witness']} | "
                f"{complete['covered_count_shortfall']} | "
                f"{complete['covered_count_shortfall_matches_gap_witness']} | "
                f"{complete['raw_candidate_budget_upper_bound']} | "
                f"{complete['raw_budget_shortfall_certifies_incomplete']} | "
                f"{complete['theorem_side_unique_lag_candidate_count']} | "
                f"{complete['theorem_side_lag_candidates_positive_in_context']} | "
                f"{complete['no_wrap_separated_candidate_range_sufficient_condition']} | "
                f"{complete['no_zero_residue_candidate_range_sufficient_condition']} | "
                f"{complete['singleton_stride_period']} | "
                f"{complete['singleton_no_zero_period_threshold']} | "
                f"{complete['singleton_no_zero_period_threshold_matches_condition']} | "
                f"{complete['unique_lag_count_matches_complete_under_candidate_range']} | "
                f"{complete['covered_count_matches_unique_lag_count_under_candidate_range']} | "
                f"{complete['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} | "
                f"{complete['unique_lag_count_shortfall_certifies_incomplete']} | "
                f"{complete['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} | "
                f"{complete['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} | "
                f"{complete['theorem_side_unique_query_candidate_count']} | "
                f"{complete['theorem_side_query_count_le_unique_lag_count']} | "
                f"{complete['theorem_side_query_count_matches_unique_lag_count']} | "
                f"{complete['unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective']} | "
                f"{complete['unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated']} | "
                f"{complete['unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue']} | "
                f"{complete['unique_query_count_shortfall_matches_gap_witness_under_period_threshold']} | "
                f"{', '.join(complete['fixture_theorem_ids'])} |"
            ),
            "",
            "Complete fixture covered lags:",
            "",
            "```text",
            ", ".join(str(lag) for lag in complete["covered_lags"]),
            "```",
            "",
            "Planner-style declared plans:",
            "",
            "| Plan | Context | Local window | Path length | Strides | Complete | Coverage | Candidate budget | Budget ratio | Covered+uncovered | Positive lags | Uncovered lags | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Gap intervals | Raw shortfall certifies incomplete | Candidate range | No-wrap sufficient | No-zero sufficient | Singleton period | Singleton period threshold | Singleton threshold matches no-zero | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Unique shortfall iff gap | Unique shortfall iff gap under period threshold | Raw budget survives dedup |",
            "| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *(
                (
                    f"| {row['plan_id']} | {row['sequence_length']} | "
                    f"{row['local_window']} | {row['path_length']} | "
                    f"{', '.join(str(stride) for stride in row['strides'])} | "
                    f"{row['coverage_complete']} | "
                    f"{row['coverage_ratio']:.3f} | "
                    f"{row['candidate_budget_per_query']} | "
                    f"{row['candidate_budget_ratio']:.3f} | "
                    f"{row['covered_uncovered_count_sum']} | "
                    f"{row['positive_lag_count']} | "
                    f"{row['uncovered_lag_count']} | "
                    f"{row['first_uncovered_lag']} | "
                    f"{row['first_uncovered_lag_matches_uncovered_list_head']} | "
                    f"{row['no_first_uncovered_lag_matches_coverage_complete']} | "
                    f"{row['first_uncovered_lag_gap_witness']} | "
                    f"{row['uncovered_count_positive_matches_gap_witness']} | "
                    f"{row['covered_count_shortfall']} | "
                    f"{row['covered_count_shortfall_matches_gap_witness']} | "
                    f"{row['uncovered_lag_interval_count']} | "
                    f"{row['raw_budget_shortfall_certifies_incomplete']} | "
                    f"{row['theorem_side_lag_candidates_positive_in_context']} | "
                    f"{row['no_wrap_separated_candidate_range_sufficient_condition']} | "
                    f"{row['no_zero_residue_candidate_range_sufficient_condition']} | "
                    f"{row['singleton_stride_period']} | "
                    f"{row['singleton_no_zero_period_threshold']} | "
                    f"{row['singleton_no_zero_period_threshold_matches_condition']} | "
                    f"{row['unique_lag_count_matches_complete_under_candidate_range']} | "
                    f"{row['covered_count_matches_unique_lag_count_under_candidate_range']} | "
                    f"{row['uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range']} | "
                    f"{row['unique_lag_count_shortfall_certifies_incomplete']} | "
                    f"{row['unique_lag_count_shortfall_matches_gap_witness_under_candidate_range']} | "
                    f"{row['unique_lag_count_shortfall_matches_gap_witness_under_period_threshold']} | "
                    f"lag={row['raw_budget_survives_lag_dedup']}, "
                    f"query={row['raw_budget_survives_query_dedup']} |"
                )
                for row in planner
            ),
            "",
            "Planner rows are compact reports over declared sparse layouts. Re-run the",
            "`reproduce_command` in the JSON for the full covered/uncovered-lag certificate.",
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
