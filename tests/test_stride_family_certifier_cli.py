from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "stride_family_certify.py"


def test_stride_family_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "stride_family_certificate.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "120",
            "--strides",
            "7,13",
            "--path-length",
            "3",
            "--local-window",
            "4",
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "stride_family_contract=GAPS context=120 strides=(7, 13)" in result.stdout
    assert "covered_lags=10 uncovered_lags=109 uncovered_intervals=6" in result.stdout
    assert (
        "lag_partition=covered_plus_uncovered=119 positive_lags=119 "
        "partition_complete=True theorem=AIT-T0094"
    ) in result.stdout
    assert "covered_count_complete=False theorem=AIT-T0095" in result.stdout
    assert (
        "first_uncovered_lag_bridge=list_head=True none_iff_complete=True "
        "semantic_miss=True theorems=AIT-T0098,AIT-T0099,AIT-T0100,AIT-T0101"
        in result.stdout
    )
    assert (
        "uncovered_count_witness=True positive=True first_gap=5 "
        "theorems=AIT-T0096,AIT-T0103"
        in result.stdout
    )
    assert (
        "first_uncovered_interval=start=5 stop=6 length=2 "
        "repair_window=6 additional_local_slots=2 "
        "target_interval_reached=True theorems=AIT-T0104,AIT-T0171"
        in result.stdout
    )
    assert (
        "first_interval_repair_next_gap=8 still_has_gap=True "
        "covers_context=False fixture_theorems=AIT-T0166,AIT-T0167"
        in result.stdout
    )
    assert (
        "largest_uncovered_interval=start=40 stop=119 length=80 "
        "repair_window=119 additional_local_slots=115 "
        "target_interval_reached=True next_gap_after_repair=None "
        "covers_context=True is_tail=True source=largest_certificate_gap_interval"
        in result.stdout
    )
    assert (
        "covered_count_shortfall=True gap_witness_equiv=True theorem=AIT-T0097"
        in result.stdout
    )
    assert (
        "uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), "
        "(22, 25), (27, 38), (40, 119))"
    ) in result.stdout
    assert "lag_budget_status=exact-raw-budget" in result.stdout
    assert "lag_dedup_loss=0 lag_no_collision=True" in result.stdout
    assert "query_budget_status=exact-raw-budget" in result.stdout
    assert "query_dedup_loss=0 query_no_collision=True" in result.stdout
    assert (
        "dedup_loss_collision=lag_positive=False lag_matches_collision=True "
        "query_positive=False query_matches_collision=True theorems=AIT-T0147,AIT-T0148"
        in result.stdout
    )
    assert (
        "dedup_loss_accounting=lag_unique_plus_loss_eq_raw=True "
        "query_unique_plus_loss_eq_raw=True theorems=AIT-T0149,AIT-T0150"
        in result.stdout
    )
    assert (
        "collision_pair_counts=lag=0 query=0 "
        "lag_zero_matches_no_collision=True lag_positive_matches_collision=True "
        "query_zero_matches_no_collision=True query_positive_matches_collision=True "
        "theorems=AIT-T0155,AIT-T0156,AIT-T0157,AIT-T0158 "
        "fixture_theorems=see_fixture_theorem_ids"
    ) in result.stdout
    assert (
        "collision_pair_severity=lag_bounds_dedup_loss=True "
        "lag_excess_over_dedup_loss=0 query_bounds_dedup_loss=True "
        "query_excess_over_dedup_loss=0 theorems=AIT-T0159,AIT-T0160"
    ) in result.stdout
    assert (
        "first_gap_local_repair=shortfall=1 needed_window=5 "
        "current_window_below_first_gap=True "
        "repair_window_reaches_first_gap=True "
        "repair_window_covers_context=False "
        "repair_window_is_final_positive_lag=False "
        "repair_threshold_matches_final_lag=True "
        "theorems=AIT-T0161,AIT-T0162,AIT-T0164,AIT-T0165 "
        "fixture_theorems=AIT-T0163"
    ) in result.stdout
    assert (
        "local_window_complete_threshold=threshold=119 shortfall=115 "
        "reaches_threshold=False threshold_certifies_complete=False "
        "exact_local_minimum=True "
        "first_gap_repair_reaches_threshold=False theorems=AIT-T0023,AIT-T0034"
    ) in result.stdout
    assert (
        "complete_local_repair=window=119 additional_slots=115 "
        "covers_context=True uses_dense_threshold=True exact_local_minimum=True "
        "minimal_for_declared_family=True minimal_witness_lag=119 "
        "theorems=AIT-T0023,AIT-T0034 "
        "fixture_theorems=AIT-T0168,AIT-T0169,AIT-T0170"
    ) in result.stdout
    assert (
        "interval_repair_plan=steps=6 final_window=119 "
        "covers_context=True strictly_progresses=True first_step=(5, 6, 6, 2, 107) "
        "last_step=(40, 119, 119, 81, 0) "
        "source=successive_first_uncovered_intervals"
    ) in result.stdout
    assert "AIT-T0076" in result.stdout
    assert "AIT-T0077" in result.stdout
    assert "AIT-T0090" in result.stdout
    assert "AIT-T0091" in result.stdout
    assert "AIT-T0106" in result.stdout
    assert "AIT-T0107" in result.stdout
    assert "AIT-T0151" in result.stdout
    assert "AIT-T0152" in result.stdout
    assert "AIT-T0155" in result.stdout
    assert "AIT-T0158" in result.stdout
    assert "query_le_unique_lag=True theorem=AIT-T0108" in result.stdout
    assert "query_matches_unique_lag=True when_injective_theorem=AIT-T0109" in result.stdout
    assert (
        "unique_query_shortfall=True "
        "gap_witness_equiv_under_candidate_range_and_injective=True "
        "no_wrap_structural_equiv=True no_zero_structural_equiv=True "
        "period_threshold_equiv=True theorems=AIT-T0123,AIT-T0124,AIT-T0125,AIT-T0130"
    ) in result.stdout
    assert "raw_budget_shortfall=True certifies_incomplete=True theorem=AIT-T0110" in result.stdout
    assert (
        "unique_lag_shortfall=True certifies_incomplete=True "
        "gap_witness_equiv_under_candidate_range=True "
        "period_threshold_equiv=True "
        "theorems=AIT-T0111,AIT-T0120,AIT-T0121,AIT-T0122,AIT-T0129"
    ) in result.stdout
    assert (
        "candidate_range=True no_wrap_separated_sufficient=False "
        "no_zero_residue_sufficient=True unique_count_complete_iff=True "
        "theorems=AIT-T0112,AIT-T0115,AIT-T0116,AIT-T0117,AIT-T0118,AIT-T0119"
    ) in result.stdout
    assert (
        "singleton_no_zero_period_threshold=None period=None "
        "matches_no_zero_residue_condition=True theorems=AIT-T0126,AIT-T0127"
    ) in result.stdout
    assert (
        "family_no_zero_period_thresholds=(True, True) periods=(120, 120) "
        "zero_residue_counts=(0, 0) "
        "counts_match_period_formula=True "
        "zero_residue_total_count=0 "
        "total_count_matches_sum_formula=True "
        "total_count_zero_matches_no_zero_condition=True "
        "period_threshold_sufficient=True matches_no_zero_residue_condition=True "
        "violation_witness=(None, None, None, None) "
        "witness_matches_period_threshold=True "
        "witness_matches_no_zero_failure=True "
        "period_violation_matches_no_zero_failure=True "
        "witness_is_first_zero=True "
        "witness_step_positive=True "
        "theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133,AIT-T0134,AIT-T0135,AIT-T0136,AIT-T0137,AIT-T0138"
    ) in result.stdout
    assert (
        "candidate_range_counts=covered_eq_unique=True "
        "uncovered_eq_context_minus_unique=True theorems=AIT-T0113,AIT-T0114"
    ) in result.stdout
    assert "not model-quality evidence" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["schema_id"] == "circle_calculus.stride_family_sparse_attention_certificate.v0"
    assert payload["coverage_complete"] is False
    assert payload["covered_lags"] == [1, 2, 3, 4, 7, 14, 21, 13, 26, 39]
    assert payload["positive_lag_count"] == 119
    assert payload["uncovered_count_positive"] is True
    assert payload["first_uncovered_lag"] == 5
    assert payload["first_uncovered_lag_interval_start"] == 5
    assert payload["first_uncovered_lag_interval_stop"] == 6
    assert payload["first_uncovered_lag_interval_length"] == 2
    assert payload["first_uncovered_lag_interval_repair_window"] == 6
    assert payload["first_uncovered_lag_interval_additional_local_slots"] == 2
    assert payload["first_uncovered_interval_repair_reaches_interval"] is True
    assert payload["first_interval_repair_next_uncovered_lag"] == 8
    assert payload["first_interval_repair_still_has_gap"] is True
    assert payload["first_interval_repair_covers_context"] is False
    assert payload["largest_uncovered_interval_start"] == 40
    assert payload["largest_uncovered_interval_stop"] == 119
    assert payload["largest_uncovered_interval_length"] == 80
    assert payload["largest_uncovered_interval_repair_window"] == 119
    assert payload["largest_uncovered_interval_additional_local_slots"] == 115
    assert payload["largest_uncovered_interval_repair_reaches_interval"] is True
    assert payload["largest_interval_repair_next_uncovered_lag"] is None
    assert payload["largest_interval_repair_still_has_gap"] is False
    assert payload["largest_interval_repair_covers_context"] is True
    assert payload["largest_uncovered_interval_is_tail"] is True
    assert payload["first_uncovered_lag_matches_uncovered_list_head"] is True
    assert payload["no_first_uncovered_lag_matches_coverage_complete"] is True
    assert payload["first_uncovered_lag_gap_witness"] is True
    assert payload["first_uncovered_lag_local_window_shortfall"] == 1
    assert payload["first_uncovered_lag_repair_window"] == 5
    assert payload["first_uncovered_lag_exceeds_local_window"] is True
    assert payload["first_uncovered_lag_repair_window_reaches"] is True
    assert payload["first_uncovered_lag_repair_window_covers_context"] is False
    assert payload["first_gap_repair_window_is_final_positive_lag"] is False
    assert payload["first_gap_repair_threshold_matches_final_lag"] is True
    assert payload["local_window_complete_coverage_threshold"] == 119
    assert payload["local_window_complete_coverage_shortfall"] == 115
    assert payload["local_window_reaches_complete_coverage_threshold"] is False
    assert payload["local_window_threshold_certifies_complete"] is False
    assert payload["local_window_complete_threshold_is_exact_local_minimum"] is True
    assert payload["complete_repair_window"] == 119
    assert payload["complete_repair_window_additional_local_slots"] == 115
    assert payload["complete_repair_window_covers_context"] is True
    assert payload["complete_repair_window_uses_dense_threshold"] is True
    assert payload["complete_repair_window_minimal_for_declared_stride_family"] is True
    assert payload["complete_repair_window_minimal_witness_lag"] == 119
    assert payload["interval_repair_plan"] == [
        [5, 6, 6, 2, 107],
        [8, 12, 12, 6, 102],
        [15, 20, 20, 8, 96],
        [22, 25, 25, 5, 92],
        [27, 38, 38, 13, 80],
        [40, 119, 119, 81, 0],
    ]
    assert payload["interval_repair_plan_step_count"] == 6
    assert payload["interval_repair_plan_final_window"] == 119
    assert payload["interval_repair_plan_covers_context"] is True
    assert payload["interval_repair_plan_strictly_progresses"] is True
    assert payload["first_gap_repair_window_reaches_complete_threshold"] is False
    assert payload["uncovered_count_positive_matches_gap_witness"] is True
    assert payload["covered_uncovered_count_sum"] == 119
    assert payload["covered_uncovered_count_partition"] is True
    assert payload["covered_count_certifies_complete"] is False
    assert payload["covered_count_shortfall"] is True
    assert payload["covered_count_shortfall_matches_gap_witness"] is True
    assert payload["uncovered_lags"][:5] == [5, 6, 8, 9, 10]
    assert payload["uncovered_lag_intervals"] == [
        [5, 6],
        [8, 12],
        [15, 20],
        [22, 25],
        [27, 38],
        [40, 119],
    ]
    assert payload["uncovered_lag_interval_count"] == 6
    assert payload["theorem_side_lag_candidates_no_collision"] is True
    assert payload["theorem_side_query_candidates_no_collision"] is True
    assert "AIT-T0076" in payload["theorem_ids"]
    assert "AIT-T0077" in payload["theorem_ids"]
    assert "AIT-T0090" in payload["theorem_ids"]
    assert "AIT-T0092" in payload["theorem_ids"]
    assert "AIT-T0093" in payload["theorem_ids"]
    assert "AIT-T0094" in payload["theorem_ids"]
    assert "AIT-T0095" in payload["theorem_ids"]
    assert "AIT-T0096" in payload["theorem_ids"]
    assert "AIT-T0097" in payload["theorem_ids"]
    assert "AIT-T0098" in payload["theorem_ids"]
    assert "AIT-T0099" in payload["theorem_ids"]
    assert "AIT-T0100" in payload["theorem_ids"]
    assert "AIT-T0101" in payload["theorem_ids"]
    assert "AIT-T0102" in payload["theorem_ids"]
    assert "AIT-T0103" in payload["theorem_ids"]
    assert "AIT-T0104" in payload["theorem_ids"]
    assert "AIT-T0105" in payload["theorem_ids"]
    assert "AIT-T0106" in payload["theorem_ids"]
    assert "AIT-T0107" in payload["theorem_ids"]
    assert "AIT-T0108" in payload["theorem_ids"]
    assert "AIT-T0109" in payload["theorem_ids"]
    assert "AIT-T0147" in payload["theorem_ids"]
    assert "AIT-T0148" in payload["theorem_ids"]
    assert "AIT-T0149" in payload["theorem_ids"]
    assert "AIT-T0150" in payload["theorem_ids"]
    assert "AIT-T0155" in payload["theorem_ids"]
    assert "AIT-T0156" in payload["theorem_ids"]
    assert "AIT-T0157" in payload["theorem_ids"]
    assert "AIT-T0158" in payload["theorem_ids"]
    assert "AIT-T0159" in payload["theorem_ids"]
    assert "AIT-T0160" in payload["theorem_ids"]
    assert "AIT-T0161" in payload["theorem_ids"]
    assert "AIT-T0162" in payload["theorem_ids"]
    assert "AIT-T0163" in payload["fixture_theorem_ids"]
    assert payload["theorem_side_query_count_le_unique_lag_count"] is True
    assert payload["theorem_side_query_count_matches_unique_lag_count"] is True
    assert payload["theorem_side_lag_candidate_dedup_loss"] == 0
    assert payload["theorem_side_lag_candidate_collision_pair_count"] == 0
    assert payload["lag_collision_pair_count_zero_matches_no_collision"] is True
    assert payload["lag_collision_pair_count_positive_matches_collision"] is True
    assert payload["lag_collision_pair_count_bounds_dedup_loss"] is True
    assert payload["lag_collision_pair_count_excess_over_dedup_loss"] == 0
    assert payload["theorem_side_lag_candidate_dedup_loss_positive"] is False
    assert payload["lag_dedup_loss_positive_matches_collision"] is True
    assert payload["lag_dedup_loss_accounting_matches_raw"] is True
    assert payload["theorem_side_query_candidate_dedup_loss"] == 0
    assert payload["theorem_side_query_candidate_collision_pair_count"] == 0
    assert payload["query_collision_pair_count_zero_matches_no_collision"] is True
    assert payload["query_collision_pair_count_positive_matches_collision"] is True
    assert payload["query_collision_pair_count_bounds_dedup_loss"] is True
    assert payload["query_collision_pair_count_excess_over_dedup_loss"] == 0
    assert payload["theorem_side_query_candidate_dedup_loss_positive"] is False
    assert payload["query_dedup_loss_positive_matches_collision"] is True
    assert payload["query_dedup_loss_accounting_matches_raw"] is True
    assert payload["raw_budget_shortfall_certifies_incomplete"] is True
    assert payload["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert (
        payload[
            "unique_lag_count_shortfall_matches_gap_witness_under_candidate_range"
        ]
        is True
    )


def test_stride_family_certifier_cli_first_gap_repair_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "120",
            "--strides",
            "7,13",
            "--path-length",
            "3",
            "--local-window",
            "4",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["first_uncovered_lag"] == 5
    assert payload["first_uncovered_lag_interval_start"] == 5
    assert payload["first_uncovered_lag_interval_stop"] == 6
    assert payload["first_uncovered_lag_interval_length"] == 2
    assert payload["first_uncovered_lag_interval_repair_window"] == 6
    assert payload["first_uncovered_lag_interval_additional_local_slots"] == 2
    assert payload["first_interval_repair_next_uncovered_lag"] == 8
    assert payload["first_interval_repair_still_has_gap"] is True
    assert payload["first_interval_repair_covers_context"] is False
    assert payload["first_uncovered_lag_local_window_shortfall"] == 1
    assert payload["first_uncovered_lag_repair_window"] == 5
    assert payload["first_uncovered_lag_exceeds_local_window"] is True
    assert payload["first_uncovered_lag_repair_window_reaches"] is True
    assert payload["first_gap_repair_window_is_final_positive_lag"] is False
    assert payload["first_gap_repair_threshold_matches_final_lag"] is True
    assert payload["local_window_complete_coverage_threshold"] == 119
    assert payload["local_window_complete_coverage_shortfall"] == 115
    assert payload["local_window_reaches_complete_coverage_threshold"] is False
    assert payload["local_window_threshold_certifies_complete"] is False
    assert payload["local_window_complete_threshold_is_exact_local_minimum"] is True
    assert payload["complete_repair_window"] == 119
    assert payload["complete_repair_window_additional_local_slots"] == 115
    assert payload["complete_repair_window_covers_context"] is True
    assert payload["complete_repair_window_uses_dense_threshold"] is True
    assert payload["complete_repair_window_minimal_for_declared_stride_family"] is True
    assert payload["complete_repair_window_minimal_witness_lag"] == 119
    assert payload["first_gap_repair_window_reaches_complete_threshold"] is False
    assert "AIT-T0161" in payload["theorem_ids"]
    assert "AIT-T0162" in payload["theorem_ids"]
    assert "AIT-T0164" in payload["theorem_ids"]
    assert "AIT-T0165" in payload["theorem_ids"]
    assert "AIT-T0168" in payload["fixture_theorem_ids"]
    assert "AIT-T0169" in payload["fixture_theorem_ids"]
    assert "AIT-T0170" in payload["fixture_theorem_ids"]
    assert (
        payload[
            "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert payload["theorem_side_lag_candidates_positive_in_context"] is True
    assert payload["no_wrap_separated_candidate_range_sufficient_condition"] is False
    assert payload["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert payload["singleton_stride_period"] is None
    assert payload["singleton_no_zero_period_threshold"] is None
    assert payload["singleton_no_zero_period_threshold_matches_condition"] is True
    assert payload["stride_family_periods"] == [120, 120]
    assert payload["no_zero_period_thresholds"] == [True, True]
    assert payload["stride_family_zero_residue_step_counts"] == [0, 0]
    assert payload["zero_residue_step_counts_match_period_formula"] is True
    assert payload["stride_family_zero_residue_total_step_count"] == 0
    assert payload["zero_residue_total_count_matches_sum_formula"] is True
    assert payload["zero_residue_total_count_zero_matches_no_zero_condition"] is True
    assert payload["no_zero_period_threshold_candidate_range_sufficient_condition"] is True
    assert payload["no_zero_period_threshold_matches_condition"] is True
    assert payload["no_zero_period_violation_witness_stride"] is None
    assert payload["no_zero_period_violation_witness_period"] is None
    assert payload["no_zero_period_violation_witness_step"] is None
    assert payload["no_zero_period_violation_witness_residue"] is None
    assert payload["zero_residue_witness_matches_period_threshold"] is True
    assert payload["zero_residue_witness_matches_no_zero_failure"] is True
    assert payload["period_threshold_violation_matches_no_zero_failure"] is True
    assert payload["no_zero_period_violation_witness_is_first_zero"] is True
    assert payload["no_zero_period_violation_witness_step_positive"] is True
    assert payload["unique_lag_count_matches_complete_under_candidate_range"] is True
    assert payload["covered_count_matches_unique_lag_count_under_candidate_range"] is True
    assert (
        payload[
            "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range"
        ]
        is True
    )
    assert "AIT-T0110" in payload["theorem_ids"]
    assert "AIT-T0111" in payload["theorem_ids"]
    assert "AIT-T0112" in payload["theorem_ids"]
    assert "AIT-T0113" in payload["theorem_ids"]
    assert "AIT-T0114" in payload["theorem_ids"]
    assert "AIT-T0115" in payload["theorem_ids"]
    assert "AIT-T0116" in payload["theorem_ids"]
    assert "AIT-T0117" in payload["theorem_ids"]
    assert "AIT-T0118" in payload["theorem_ids"]
    assert "AIT-T0119" in payload["theorem_ids"]
    assert "AIT-T0120" in payload["theorem_ids"]
    assert "AIT-T0121" in payload["theorem_ids"]
    assert "AIT-T0122" in payload["theorem_ids"]
    assert "AIT-T0123" in payload["theorem_ids"]
    assert "AIT-T0124" in payload["theorem_ids"]
    assert "AIT-T0125" in payload["theorem_ids"]
    assert "AIT-T0126" in payload["theorem_ids"]
    assert "AIT-T0127" in payload["theorem_ids"]
    assert "AIT-T0128" in payload["theorem_ids"]
    assert "AIT-T0129" in payload["theorem_ids"]
    assert "AIT-T0130" in payload["theorem_ids"]
    assert "AIT-T0131" in payload["theorem_ids"]
    assert "AIT-T0132" in payload["theorem_ids"]
    assert "AIT-T0133" in payload["theorem_ids"]
    assert "AIT-T0134" in payload["theorem_ids"]
    assert "AIT-T0135" in payload["theorem_ids"]
    assert "AIT-T0136" in payload["theorem_ids"]
    assert "AIT-T0137" in payload["theorem_ids"]
    assert "AIT-T0138" in payload["theorem_ids"]
    assert (
        payload[
            "unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective"
        ]
        is True
    )
    assert (
        payload["unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated"]
        is True
    )
    assert (
        payload["unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue"]
        is True
    )
    assert (
        payload[
            "unique_query_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert payload["fixture_theorem_ids"] == [
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0091",
        "AIT-T0102",
        "AIT-T0104",
        "AIT-T0151",
        "AIT-T0152",
        "AIT-T0171",
        "AIT-T0163",
        "AIT-T0166",
        "AIT-T0167",
        "AIT-T0168",
        "AIT-T0169",
        "AIT-T0170",
    ]


def test_stride_family_certifier_cli_singleton_period_threshold() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "12",
            "--strides",
            "4",
            "--path-length",
            "2",
            "--local-window",
            "1",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert (
        "singleton_no_zero_period_threshold=True period=3 "
        "matches_no_zero_residue_condition=True theorems=AIT-T0126,AIT-T0127"
    ) in result.stdout
    assert (
        "family_no_zero_period_thresholds=(True,) periods=(3,) "
        "zero_residue_counts=(0,) "
        "counts_match_period_formula=True "
        "zero_residue_total_count=0 "
        "total_count_matches_sum_formula=True "
        "total_count_zero_matches_no_zero_condition=True "
        "period_threshold_sufficient=True matches_no_zero_residue_condition=True "
        "violation_witness=(None, None, None, None) "
        "witness_matches_period_threshold=True "
        "witness_matches_no_zero_failure=True "
        "period_violation_matches_no_zero_failure=True "
        "witness_is_first_zero=True "
        "witness_step_positive=True "
        "theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133,AIT-T0134,AIT-T0135,AIT-T0136,AIT-T0137,AIT-T0138"
    ) in result.stdout


def test_stride_family_certifier_cli_period_threshold_violation_witness() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "12",
            "--strides",
            "4",
            "--path-length",
            "3",
            "--local-window",
            "1",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert (
        "singleton_no_zero_period_threshold=False period=3 "
        "matches_no_zero_residue_condition=True theorems=AIT-T0126,AIT-T0127"
    ) in result.stdout
    assert (
        "family_no_zero_period_thresholds=(False,) periods=(3,) "
        "zero_residue_counts=(1,) "
        "counts_match_period_formula=True "
        "zero_residue_total_count=1 "
        "total_count_matches_sum_formula=True "
        "total_count_zero_matches_no_zero_condition=True "
        "period_threshold_sufficient=False matches_no_zero_residue_condition=True "
        "violation_witness=(4, 3, 3, 0) "
        "witness_matches_period_threshold=True "
        "witness_matches_no_zero_failure=True "
        "period_violation_matches_no_zero_failure=True "
        "witness_is_first_zero=True "
        "witness_step_positive=True "
        "theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133,AIT-T0134,AIT-T0135,AIT-T0136,AIT-T0137,AIT-T0138"
    ) in result.stdout


def test_stride_family_certifier_cli_dedup_loss_collision_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "16",
            "--strides",
            "4,8",
            "--path-length",
            "4",
            "--local-window",
            "2",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["theorem_side_lag_candidate_dedup_loss"] == 4
    assert payload["theorem_side_lag_candidate_collision_pair_count"] == 6
    assert payload["lag_collision_pair_count_zero_matches_no_collision"] is True
    assert payload["lag_collision_pair_count_positive_matches_collision"] is True
    assert payload["lag_collision_pair_count_bounds_dedup_loss"] is True
    assert payload["lag_collision_pair_count_excess_over_dedup_loss"] == 2
    assert payload["theorem_side_lag_candidate_dedup_loss_positive"] is True
    assert payload["theorem_side_lag_candidates_no_collision"] is False
    assert payload["lag_dedup_loss_positive_matches_collision"] is True
    assert payload["lag_dedup_loss_accounting_matches_raw"] is True
    assert payload["theorem_side_query_candidate_dedup_loss"] == 4
    assert payload["theorem_side_query_candidate_collision_pair_count"] == 6
    assert payload["query_collision_pair_count_zero_matches_no_collision"] is True
    assert payload["query_collision_pair_count_positive_matches_collision"] is True
    assert payload["query_collision_pair_count_bounds_dedup_loss"] is True
    assert payload["query_collision_pair_count_excess_over_dedup_loss"] == 2
    assert payload["theorem_side_query_candidate_dedup_loss_positive"] is True
    assert payload["theorem_side_query_candidates_no_collision"] is False
    assert payload["query_dedup_loss_positive_matches_collision"] is True
    assert payload["query_dedup_loss_accounting_matches_raw"] is True
    assert "AIT-T0155" in payload["theorem_ids"]
    assert "AIT-T0156" in payload["theorem_ids"]
    assert "AIT-T0157" in payload["theorem_ids"]
    assert "AIT-T0158" in payload["theorem_ids"]
    assert "AIT-T0159" in payload["theorem_ids"]
    assert "AIT-T0160" in payload["theorem_ids"]
    assert payload["fixture_theorem_ids"] == ["AIT-T0153", "AIT-T0154"]
