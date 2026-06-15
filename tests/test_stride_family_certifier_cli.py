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
        "covered_count_shortfall=True gap_witness_equiv=True theorem=AIT-T0097"
        in result.stdout
    )
    assert (
        "uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), "
        "(22, 25), (27, 38), (40, 119))"
    ) in result.stdout
    assert "lag_budget_status=exact-raw-budget" in result.stdout
    assert "query_budget_status=exact-raw-budget" in result.stdout
    assert "AIT-T0076" in result.stdout
    assert "AIT-T0077" in result.stdout
    assert "AIT-T0090" in result.stdout
    assert "AIT-T0091" in result.stdout
    assert "AIT-T0106" in result.stdout
    assert "AIT-T0107" in result.stdout
    assert "query_le_unique_lag=True theorem=AIT-T0108" in result.stdout
    assert "query_matches_unique_lag=True when_injective_theorem=AIT-T0109" in result.stdout
    assert "raw_budget_shortfall=True certifies_incomplete=True theorem=AIT-T0110" in result.stdout
    assert "unique_lag_shortfall=True certifies_incomplete=True theorem=AIT-T0111" in result.stdout
    assert (
        "candidate_range=True no_wrap_separated_sufficient=False "
        "unique_count_complete_iff=True theorems=AIT-T0112,AIT-T0115,AIT-T0116"
    ) in result.stdout
    assert (
        "candidate_range_counts=covered_eq_unique=True "
        "uncovered_eq_context_minus_unique=True theorems=AIT-T0113,AIT-T0114"
    ) in result.stdout
    assert "not model-quality evidence" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["coverage_complete"] is False
    assert payload["covered_lags"] == [1, 2, 3, 4, 7, 14, 21, 13, 26, 39]
    assert payload["positive_lag_count"] == 119
    assert payload["uncovered_count_positive"] is True
    assert payload["first_uncovered_lag"] == 5
    assert payload["first_uncovered_lag_matches_uncovered_list_head"] is True
    assert payload["no_first_uncovered_lag_matches_coverage_complete"] is True
    assert payload["first_uncovered_lag_gap_witness"] is True
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
    assert payload["theorem_side_query_count_le_unique_lag_count"] is True
    assert payload["theorem_side_query_count_matches_unique_lag_count"] is True
    assert payload["raw_budget_shortfall_certifies_incomplete"] is True
    assert payload["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert payload["theorem_side_lag_candidates_positive_in_context"] is True
    assert payload["no_wrap_separated_candidate_range_sufficient_condition"] is False
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
    assert payload["fixture_theorem_ids"] == [
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0091",
        "AIT-T0102",
        "AIT-T0104",
    ]
