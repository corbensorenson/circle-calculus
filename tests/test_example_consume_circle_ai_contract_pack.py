from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.circle_ai_contracts import build_contract_pack


def _write_pack(tmp_path: Path) -> Path:
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    pack_path.write_text(json.dumps(build_contract_pack()))
    return pack_path


def test_example_consumer_emits_selected_rope_digest(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "rope_position_distinguishability",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["evidence_fields"] == {
        "d19_impossible_request_status": "impossible",
        "d19_proved_request_status": "proved",
    }
    assert "AIRA-T0214" in payload["theorem_ids"]
    assert "AIRA-T0231" in payload["theorem_ids"]
    assert "model quality" in payload["not_claimed"]


def test_example_consumer_can_emit_field_metadata(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "strided_candidate_fanout",
            "--field",
            "effective_candidate_budget",
            "--include-field-metadata",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"effective_candidate_budget": 12}
    assert payload["field_catalog"]["effective_candidate_budget"]["value_kind"] == (
        "integer"
    )
    assert "Duplicate-collapsed" in payload["field_catalog"][
        "effective_candidate_budget"
    ]["description"]


def test_example_consumer_can_emit_sparse_recommendations(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--kind",
            "sparse_attention_coverage",
            "--field",
            "first_uncovered_lag",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"first_uncovered_lag": 5}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    ]
    assert payload["planner_recommendations"][0]["proposed_local_window"] == 6
    assert payload["planner_recommendations"][1]["proposed_local_window"] == 119
    assert payload["planner_recommendations"][1]["target_interval_start"] == 40


def test_example_consumer_can_emit_planner_action_plan(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-kind",
            "rope_position_distinguishability",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["planner_schema"] == "circle_calculus.ai_contract_planner.v0"
    assert payload["planner_includes_values"] is False
    assert payload["selected_kinds"] == [
        "sparse_attention_coverage",
        "rope_position_distinguishability",
    ]
    assert payload["planner_recommendation_count"] == 6
    assert payload["ready_recommendation_count"] == 6
    assert [action["recommendation_id"] for action in payload["action_plan"]] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert payload["action_plan"][0]["action_kind"] == "increase_local_window"
    assert payload["action_plan"][0]["evidence_fields"] == [
        "first_uncovered_interval_start",
        "first_uncovered_interval_stop",
        "first_uncovered_interval_length",
        "local_window_needed_to_cover_first_uncovered_interval",
        "first_uncovered_interval_additional_local_slots",
        "first_uncovered_interval_repair_reaches_interval",
        "first_interval_repair_next_uncovered_lag",
        "first_interval_repair_still_has_gap",
        "first_interval_repair_covers_context",
    ]
    assert payload["action_plan"][0]["theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0171",
        "AIT-T0166",
        "AIT-T0167",
    ]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in payload["action_plan"][0]["validation_commands"]
    )
    assert payload["action_plan"][1]["coverage_scope"] == "largest_uncovered_interval"
    assert "efficient" in payload["action_plan"][2]["not_claimed"]
    assert payload["action_plan"][3]["action_kind"] == "increase_local_window_sequence"
    assert "AIRA-T0216" in payload["action_plan"][5]["theorem_ids"]
    assert "evidence_values" not in payload["action_plan"][0]


def test_example_consumer_planner_can_include_evidence_values(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
            "--planner-kind",
            "sparse_attention_coverage",
            "--planner-include-values",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_includes_values"] is True
    assert payload["planner_recommendation_count"] == 4

    first_interval = payload["action_plan"][0]
    assert first_interval["recommendation_id"] == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    )
    assert first_interval["evidence_values"] == {
        "first_uncovered_interval_start": 5,
        "first_uncovered_interval_stop": 6,
        "first_uncovered_interval_length": 2,
        "local_window_needed_to_cover_first_uncovered_interval": 6,
        "first_uncovered_interval_additional_local_slots": 2,
        "first_uncovered_interval_repair_reaches_interval": True,
        "first_interval_repair_next_uncovered_lag": 8,
        "first_interval_repair_still_has_gap": True,
        "first_interval_repair_covers_context": False,
    }
    assert first_interval["missing_evidence_fields"] == []
    assert first_interval["action_parameters"] == {
        "proposed_local_window": 6,
        "additional_local_slots": 2,
        "target_interval_start": 5,
        "target_interval_stop": 6,
        "target_interval_length": 2,
        "next_uncovered_lag_after_repair": 8,
        "still_has_gap_after_repair": True,
    }

    largest_gap = payload["action_plan"][1]
    assert largest_gap["recommendation_id"] == "SPARSE-REPAIR-LARGEST-GAP-INTERVAL"
    assert largest_gap["evidence_values"] == {
        "largest_uncovered_interval_start": 40,
        "largest_uncovered_interval_stop": 119,
        "largest_uncovered_interval_length": 80,
        "local_window_needed_to_cover_largest_uncovered_interval": 119,
        "largest_uncovered_interval_additional_local_slots": 115,
        "largest_uncovered_interval_repair_reaches_interval": True,
        "largest_interval_repair_next_uncovered_lag": None,
        "largest_interval_repair_still_has_gap": False,
        "largest_interval_repair_covers_context": True,
        "largest_uncovered_interval_is_tail": True,
        "uncovered_lag_intervals": [
            {"start": 5, "stop": 6},
            {"start": 8, "stop": 12},
            {"start": 15, "stop": 20},
            {"start": 22, "stop": 25},
            {"start": 27, "stop": 38},
            {"start": 40, "stop": 119},
        ],
    }
    assert largest_gap["action_parameters"] == {
        "proposed_local_window": 119,
        "additional_local_slots": 115,
        "target_interval_start": 40,
        "target_interval_stop": 119,
        "target_interval_length": 80,
        "next_uncovered_lag_after_repair": None,
        "still_has_gap_after_repair": False,
        "covers_context_after_repair": True,
        "largest_interval_is_tail": True,
    }

    complete_fallback = payload["action_plan"][2]
    assert complete_fallback["recommendation_id"] == (
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    )
    assert complete_fallback["evidence_values"] == {
        "complete_repair_window": 119,
        "complete_repair_window_additional_local_slots": 115,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_uses_dense_threshold": True,
        "local_window_complete_threshold_is_exact_local_minimum": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
    }
    assert complete_fallback["action_parameters"] == {
        "proposed_local_window": 119,
        "additional_local_slots": 115,
    }

    interval_path = payload["action_plan"][3]
    assert interval_path["recommendation_id"] == "SPARSE-INTERVAL-REPAIR-PATH"
    assert interval_path["evidence_values"]["interval_repair_plan_step_count"] == 6
    assert interval_path["evidence_values"]["interval_repair_plan_final_window"] == 119
    assert interval_path["evidence_values"]["interval_repair_plan_covers_context"] is True
    assert interval_path["evidence_values"]["interval_repair_plan_strictly_progresses"] is True
    assert interval_path["action_parameters"] == {
        "covers_context_after_final_step": True,
        "final_local_window": 119,
        "step_count": 6,
        "strictly_progresses": True,
    }


def test_example_consumer_planner_defaults_to_all_kinds(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--planner",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_recommendation_count"] == 20
    assert payload["ready_recommendation_count"] == 20
    assert "kv_cache_ring_buffer" in payload["selected_kinds"]
    assert "seed_rule_exact_regeneration" in payload["selected_kinds"]


def test_example_consumer_lists_contract_kinds(tmp_path: Path) -> None:
    pack_path = _write_pack(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/example_consume_circle_ai_contract_pack.py",
            "--pack",
            str(pack_path),
            "--list-kinds",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert "rope_position_distinguishability" in payload["kinds"]
    assert "kv_cache_ring_buffer" in payload["kinds"]
    assert "seed_rule_exact_regeneration" in payload["kinds"]
