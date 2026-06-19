from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_contract_ready_cli_accepts_ready_kind_text() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract readiness ok: sparse_attention_coverage" in result.stdout
    assert "ready=True" in result.stdout
    assert "proof_proved=True" in result.stdout
    assert "unresolved=0" in result.stdout
    assert "unproved=0" in result.stdout
    assert "recommendations=4" in result.stdout
    assert (
        "planner_recommendations=SPARSE-LOCAL-FIRST-INTERVAL-REPAIR,"
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL,"
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK,SPARSE-INTERVAL-REPAIR-PATH"
    ) in result.stdout
    assert (
        "validation_commands=python scripts/stride_family_certify.py --context 120 "
        "--strides 7,13 --path-length 3 --local-window 4 --format json"
    ) in result.stdout
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in result.stdout
    )


def test_contract_ready_cli_accepts_ready_kind_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "seed_rule_exact_regeneration"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["readiness"]["theorem_count"] == 32
    assert payload["readiness"]["all_theorem_ids_proved"] is True
    assert payload["contract"]["id"] == "CC-AI-CONTRACT-SEED-RULE-001"
    assert "GEN-T0050" in payload["contract"]["theorem_ids"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration"
        in payload["contract"]["validation_commands"]
    )


def test_contract_ready_cli_emits_text_digest_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "kv_cache_ring_buffer",
            "--digest",
            "--field",
            "stale_probe_first_stale_token",
            "--field",
            "stale_probe_stale_requested_count",
            "--include-field-metadata",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract digest ok: kv_cache_ring_buffer" in result.stdout
    assert "fields=2" in result.stdout
    assert "missing=0" in result.stdout
    assert "evidence.stale_probe_first_stale_token=12" in result.stdout
    assert "evidence.stale_probe_stale_requested_count=1" in result.stdout
    assert "field.stale_probe_first_stale_token.value_kind=integer" in result.stdout
    assert "proof_role=fixture_parameter_or_observation" in result.stdout
    assert (
        "validation_commands=python scripts/kv_cache_certify.py --cache-size 16"
        in result.stdout
    )


def test_contract_ready_cli_emits_json_digest_fields() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--digest",
            "--format",
            "json",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--field",
            "d19_undecided_request_status",
            "--field",
            "d19_proved_first_channel_bank_transfer",
            "--field",
            "d19_proved_first_channel_bank_shape",
            "--field",
            "d19_proved_first_channel_bank_tolerance_rule",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["ready_for_downstream_fixture_use"] is True
    assert payload["evidence_fields"] == {
        "d19_proved_request_status": "proved",
        "d19_impossible_request_status": "impossible",
        "d19_undecided_request_status": "undecided_margin_gap",
        "d19_proved_first_channel_bank_transfer": True,
        "d19_proved_first_channel_bank_shape": "standard_channel0_first",
        "d19_proved_first_channel_bank_tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
    }
    assert "AIRA-T0216" in payload["theorem_ids"]
    assert "AIRA-T0214" in payload["theorem_ids"]
    assert "AIRA-T0231" in payload["theorem_ids"]
    assert "AIRA-T0234" in payload["theorem_ids"]


def test_contract_ready_cli_emits_rope_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--digest",
            "--format",
            "json",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--field",
            "d19_undecided_request_status",
            "--field",
            "d19_proved_first_channel_bank_transfer",
            "--field",
            "d19_proved_first_channel_bank_shape",
            "--field",
            "d19_proved_first_channel_bank_tolerance_rule",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "d19_proved_request_status": "proved",
        "d19_impossible_request_status": "impossible",
        "d19_undecided_request_status": "undecided_margin_gap",
        "d19_proved_first_channel_bank_transfer": True,
        "d19_proved_first_channel_bank_shape": "standard_channel0_first",
        "d19_proved_first_channel_bank_tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert payload["planner_recommendations"][0]["exact_discrete_pass"] is True
    assert payload["planner_recommendations"][0]["collision_pair_count"] == 0
    assert payload["planner_recommendations"][1]["proved_margin"] == "1/328459"
    assert (
        payload["planner_recommendations"][1]["impossible_margin_floor"]
        == "1/328458"
    )
    assert payload["planner_recommendations"][1]["undecided_margin"] == "2/656917"
    assert (
        payload["planner_recommendations"][1]["undecided_status"]
        == "undecided_margin_gap"
    )


def test_contract_ready_cli_emits_json_digest_field_metadata() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "strided_candidate_fanout",
            "--digest",
            "--format",
            "json",
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


def test_contract_ready_cli_emits_json_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--digest",
            "--format",
            "json",
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
    assert payload["planner_recommendations"][1]["target_interval_stop"] == 119


def test_contract_ready_cli_emits_json_acceptance_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--format",
            "json",
            "--field",
            "first_uncovered_lag",
            "--field",
            "first_uncovered_interval_start",
            "--field",
            "complete_repair_window",
            "--field",
            "complete_repair_window_covers_context",
            "--field",
            "complete_repair_window_minimal_for_declared_stride_family",
            "--field",
            "complete_repair_window_minimal_witness_lag",
            "--require-theorem",
            "AIT-T0104",
            "--require-theorem",
            "AIT-T0172",
            "--require-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--require-recommendation",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=local_window_complete_threshold_is_exact_local_minimum",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_for_declared_stride_family",
            "--require-recommendation-evidence-field",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169",
            "--require-recommendation-theorem",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
            "--require-recommendation-action-parameter",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window",
            "--require-recommendation-action-parameter",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots",
            "--require-recommendation-action-parameter-path",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
            "--require-recommendation-action-parameter-path",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window",
            "--require-recommendation-action-parameter-path",
            "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots",
            "--include-field-metadata",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["receipt_schema"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    assert payload["accepted"] is True
    assert payload["kind"] == "sparse_attention_coverage"
    assert payload["contract_id"] == "CC-AI-CONTRACT-SPARSE-001"
    assert len(payload["pack_content_fingerprint"]) == 64
    assert len(payload["contract_content_fingerprint"]) == 64
    assert payload["required_fields"] == [
        "first_uncovered_lag",
        "first_uncovered_interval_start",
        "complete_repair_window",
        "complete_repair_window_covers_context",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
    ]
    assert payload["required_theorem_ids"] == ["AIT-T0104", "AIT-T0172"]
    assert payload["evidence_fields"] == {
        "first_uncovered_lag": 5,
        "first_uncovered_interval_start": 5,
        "complete_repair_window": 119,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
    }
    assert payload["required_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
    ]
    assert payload["required_recommendation_evidence_fields"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "first_uncovered_interval_start",
            "first_uncovered_interval_stop",
        ],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "complete_repair_window",
            "complete_repair_window_covers_context",
            "complete_repair_window_uses_dense_threshold",
            "local_window_complete_threshold_is_exact_local_minimum",
            "complete_repair_window_minimal_for_declared_stride_family",
            "complete_repair_window_minimal_witness_lag",
        ],
    }
    assert payload["required_recommendation_theorem_ids"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["AIT-T0104"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "AIT-T0023",
            "AIT-T0034",
            "AIT-T0172",
            "AIT-T0168",
            "AIT-T0169",
            "AIT-T0170",
        ],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert payload["planner_recommendations"][0]["id"] == (
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    )
    assert payload["planner_recommendations"][1]["id"] == (
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    )
    assert payload["planner_recommendations"][1]["proposed_local_window"] == 119
    assert payload["field_catalog"]["first_uncovered_lag"]["value_kind"] == (
        "integer"
    )


def test_contract_ready_cli_emits_rope_bank_transfer_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--receipt",
            "--format",
            "json",
            "--field",
            "d19_proved_request_status",
            "--field",
            "d19_impossible_request_status",
            "--field",
            "d19_undecided_request_status",
            "--field",
            "d19_proved_first_channel_bank_transfer",
            "--field",
            "d19_proved_first_channel_bank_shape",
            "--field",
            "d19_proved_first_channel_bank_tolerance_rule",
            "--require-theorem",
            "AIRA-T0171",
            "--require-theorem",
            "AIRA-T0172",
            "--require-theorem",
            "AIRA-T0234",
            "--require-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--require-recommendation-evidence-field",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_bank_transfer"
            ),
            "--require-recommendation-theorem",
            "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234",
            "--require-recommendation-action-parameter",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer",
            "--require-recommendation-action-parameter-path",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies",
            "--require-recommendation-action-parameter-path",
            "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["required_theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
    ]
    assert payload["evidence_fields"] == {
        "d19_proved_request_status": "proved",
        "d19_impossible_request_status": "impossible",
        "d19_undecided_request_status": "undecided_margin_gap",
        "d19_proved_first_channel_bank_transfer": True,
        "d19_proved_first_channel_bank_shape": "standard_channel0_first",
        "d19_proved_first_channel_bank_tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
    }
    assert payload["required_recommendation_ids"] == [
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ]
    assert payload["required_recommendation_evidence_fields"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "d19_proved_first_channel_bank_transfer"
        ],
    }
    assert payload["required_recommendation_theorem_ids"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": ["AIRA-T0234"],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": ["proved_branch_bank_transfer"],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "ROPE-USE-D19-MARGIN-FRONTIER": [
            "proved_branch_bank_transfer.applies",
            "proved_branch_bank_transfer.theorem_ids",
        ],
    }
    recommendation = payload["planner_recommendations"][0]
    assert recommendation["proved_branch_bank_transfer"] == {
        "applies": True,
        "bank_shape": "standard_channel0_first",
        "tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
        "theorem_ids": ["AIRA-T0171", "AIRA-T0172", "AIRA-T0234"],
    }


def test_contract_ready_cli_emits_text_acceptance_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--field",
            "first_uncovered_lag",
            "--require-theorem",
            "AIT-T0104",
            "--require-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
            "--require-recommendation-action-parameter-path",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract receipt ok: sparse_attention_coverage" in result.stdout
    assert "accepted=True" in result.stdout
    assert "fields=1" in result.stdout
    assert "recommendations=1" in result.stdout
    assert "recommendation_evidence_fields=1" in result.stdout
    assert "recommendation_theorems=1" in result.stdout
    assert "recommendation_action_parameters=1" in result.stdout
    assert "recommendation_action_parameter_paths=1" in result.stdout
    assert "fingerprint_algorithm=sha256-json-v1" in result.stdout
    assert "evidence.first_uncovered_lag=5" in result.stdout
    assert (
        "recommendation.SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
        "action=increase_local_window"
    ) in result.stdout
    assert (
        "required_recommendation_evidence_fields."
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start"
    ) in result.stdout
    assert (
        "required_recommendation_theorem_ids."
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104"
    ) in result.stdout
    assert (
        "required_recommendation_action_parameters."
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window"
    ) in result.stdout
    assert (
        "required_recommendation_action_parameter_paths."
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window"
    ) in result.stdout


def test_contract_ready_cli_receipt_rejects_missing_field() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--field",
            "not_a_field",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing requested evidence fields: not_a_field" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_recommendation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation",
            "NOT-A-REC",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing requested planner recommendations: NOT-A-REC" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_theorem() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-theorem",
            "NOT-A-THEOREM",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing requested theorem ids: NOT-A-THEOREM" in result.stderr


def test_contract_ready_cli_receipt_rejects_duplicate_requirement_pin() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--field",
            "first_uncovered_lag",
            "--field",
            "first_uncovered_lag",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "required_fields must not contain duplicate strings" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_recommendation_evidence_field() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=not_recommendation_evidence",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "not_recommendation_evidence" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_recommendation_theorem() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=NOT-A-REC-THEOREM",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing required recommendation theorem ids" in result.stderr
    assert "NOT-A-REC-THEOREM" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_recommendation_action_parameter() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--receipt",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=not_an_action_parameter",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing required recommendation action parameters" in result.stderr
    assert "not_an_action_parameter" in result.stderr


def test_contract_ready_cli_receipt_rejects_missing_recommendation_action_parameter_path() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "rope_position_distinguishability",
            "--receipt",
            "--require-recommendation-action-parameter-path",
            (
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "classifier_regions[region=not_a_region].theorem_ids"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "contract receipt failed" in result.stderr
    assert "missing required recommendation action-parameter paths" in result.stderr
    assert "classifier_regions[region=not_a_region].theorem_ids" in result.stderr


def test_contract_ready_cli_recommendation_evidence_field_requires_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-evidence-field",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--require-recommendation-evidence-field requires --receipt" in (
        result.stderr
    )


def test_contract_ready_cli_theorem_pins_require_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--require-theorem",
            "AIT-T0104",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--require-theorem requires --receipt" in result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-theorem",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--require-recommendation-theorem requires --receipt" in result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-action-parameter",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--require-recommendation-action-parameter requires --receipt" in (
        result.stderr
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--require-recommendation-action-parameter-path",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--require-recommendation-action-parameter-path requires --receipt" in (
        result.stderr
    )


def test_contract_ready_cli_emits_text_fingerprints() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract fingerprints ok:" in result.stdout
    assert "algorithm=sha256-json-v1" in result.stdout
    assert "fingerprint.sparse_attention_coverage" in result.stdout
    assert "fingerprint.seed_rule_exact_regeneration" in result.stdout


def test_contract_ready_cli_emits_json_fingerprints() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(payload["pack_content_fingerprint"]) == 64
    assert "sparse_attention_coverage" in payload["contract_fingerprint_index"]
    sparse = payload["contract_fingerprint_index"]["sparse_attention_coverage"]
    assert sparse["id"] == "CC-AI-CONTRACT-SPARSE-001"
    assert len(sparse["content_fingerprint"]) == 64


def test_contract_ready_cli_emits_text_acceptance_policy() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--acceptance-policy",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI acceptance policy ok:" in result.stdout
    assert "schema=circle_calculus.ai_contract_acceptance_policy.v0" in result.stdout
    assert (
        "policy=examples/circle_ai_contract_acceptance_policy.json"
        in result.stdout
    )
    assert "checker=scripts/check_circle_ai_contract_acceptance_policy.py" in result.stdout
    assert (
        "standalone=examples/downstream_ci_accept_circle_ai_contracts.py"
        in result.stdout
    )
    assert "pinned_requirement_keys=required_fields" in result.stdout
    assert "required_recommendation_theorem_ids" in result.stdout
    assert (
        "fingerprint_refresh_command=python scripts/circle_ai_contract_ready.py "
        "--print-refreshed-policy"
    ) in result.stdout


def test_contract_ready_cli_emits_json_acceptance_policy() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--acceptance-policy",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert payload["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(payload["pack_content_fingerprint"]) == 64
    policy = payload["acceptance_policy"]
    assert policy["schema_id"] == "circle_calculus.ai_contract_acceptance_policy.v0"
    assert policy["report_schema_id"] == (
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
    )
    assert policy["default_policy_path"] == (
        "examples/circle_ai_contract_acceptance_policy.json"
    )
    assert policy["checker"] == "scripts/check_circle_ai_contract_acceptance_policy.py"
    assert policy["standalone_checker"] == (
        "examples/downstream_ci_accept_circle_ai_contracts.py"
    )
    assert policy["fingerprint_refresh_command"] == (
        "python scripts/circle_ai_contract_ready.py --print-refreshed-policy"
    )
    assert "required_theorem_ids" in policy["pinned_requirement_keys"]
    assert "required_recommendation_theorem_ids" in policy["pinned_requirement_keys"]


def test_contract_ready_cli_prints_refreshed_policy_preserving_pins(
    tmp_path,
) -> None:
    original_policy = json.loads(
        Path("examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    stale_policy = json.loads(json.dumps(original_policy))
    stale_policy["expected_pack_fingerprint"] = "0" * 64
    stale_policy["contracts"][0]["expected_contract_fingerprint"] = "1" * 64
    policy_path = tmp_path / "stale_policy.json"
    policy_path.write_text(json.dumps(stale_policy))

    fingerprint_result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    fingerprints = json.loads(fingerprint_result.stdout)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--policy",
            str(policy_path),
            "--print-refreshed-policy",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    refreshed = json.loads(result.stdout)
    assert refreshed["expected_pack_fingerprint"] == (
        fingerprints["pack_content_fingerprint"]
    )
    contract_fingerprints = fingerprints["contract_fingerprint_index"]
    for contract in refreshed["contracts"]:
        kind = contract["kind"]
        assert contract["expected_contract_fingerprint"] == (
            contract_fingerprints[kind]["content_fingerprint"]
        )

    assert refreshed["contracts"][0]["required_fields"] == (
        stale_policy["contracts"][0]["required_fields"]
    )
    assert refreshed["contracts"][0]["required_theorem_ids"] == (
        stale_policy["contracts"][0]["required_theorem_ids"]
    )
    assert refreshed["contracts"][0]["required_recommendation_ids"] == (
        stale_policy["contracts"][0]["required_recommendation_ids"]
    )
    assert refreshed["contracts"][0]["required_recommendation_theorem_ids"] == (
        stale_policy["contracts"][0]["required_recommendation_theorem_ids"]
    )


def test_contract_ready_cli_print_refreshed_policy_rejects_kind_mode() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--print-refreshed-policy",
            "--kind",
            "rope_position_distinguishability",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--print-refreshed-policy cannot be used with --kind" in result.stderr


def test_contract_ready_cli_emits_text_acceptance_policy_report() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--acceptance-policy-report",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI acceptance policy report ok:" in result.stdout
    assert "schema=circle_calculus.ai_contract_acceptance_policy_report.v0" in (
        result.stdout
    )
    assert "receipt.rope_position_distinguishability" in result.stdout
    assert "receipt.kv_cache_ring_buffer" in result.stdout
    assert "receipt.sparse_attention_coverage" in result.stdout
    assert "receipt.recurrence_schedule" in result.stdout


def test_contract_ready_cli_emits_json_acceptance_policy_report() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--acceptance-policy-report",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["acceptance_policy_report_schema"] == (
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
    )
    assert payload["accepted"] is True
    assert payload["receipt_count"] == 4
    assert [receipt["kind"] for receipt in payload["receipts"]] == [
        "rope_position_distinguishability",
        "kv_cache_ring_buffer",
        "sparse_attention_coverage",
        "recurrence_schedule",
    ]
    assert payload["receipts"][0]["required_recommendation_ids"] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]


def test_contract_ready_cli_acceptance_policy_report_rejects_kind_mode() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--acceptance-policy-report",
            "--kind",
            "rope_position_distinguishability",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--acceptance-policy-report cannot be used with --kind" in result.stderr


def test_contract_ready_cli_accepts_matching_fingerprint_expectations() -> None:
    fingerprint_result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    fingerprints = json.loads(fingerprint_result.stdout)
    sparse = fingerprints["contract_fingerprint_index"]["sparse_attention_coverage"]

    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--expect-pack-fingerprint",
            fingerprints["pack_content_fingerprint"],
            "--expect-contract-fingerprint",
            f"sparse_attention_coverage={sparse['content_fingerprint']}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract fingerprints ok:" in result.stdout


def test_contract_ready_cli_rejects_mismatched_fingerprint_expectation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--fingerprints",
            "--expect-pack-fingerprint",
            "0" * 64,
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3
    assert "fingerprint expectation failed" in result.stderr
    assert "pack fingerprint mismatch" in result.stderr


def test_contract_ready_cli_emits_kv_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "kv_cache_ring_buffer",
            "--digest",
            "--format",
            "json",
            "--field",
            "stale_probe_first_stale_token",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"stale_probe_first_stale_token": 12}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "KV-DROP-STALE-REQUEST-TOKEN",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    ]
    assert payload["planner_recommendations"][0]["target_token"] == 12
    assert (
        payload["planner_recommendations"][0]["next_same_slot_overwrite_token"]
        == 28
    )
    assert payload["planner_recommendations"][1]["request_token_count"] == 20


def test_contract_ready_cli_emits_kv_sink_window_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "kv_cache_ring_buffer",
            "--receipt",
            "--format",
            "json",
            "--field",
            "stale_probe_first_stale_token",
            "--field",
            "sink_tokens_retained_by_policy",
            "--field",
            "sink_window_exact_policy",
            "--field",
            "sink_window_tokens_distinct",
            "--field",
            "sink_prefix_disjoint_from_live_window",
            "--field",
            "sink_tokens_outside_ordinary_rolling_window",
            "--require-theorem",
            "AIM-T0103",
            "--require-theorem",
            "AIM-T0104",
            "--require-theorem",
            "AIM-T0149",
            "--require-recommendation",
            "KV-DROP-STALE-REQUEST-TOKEN",
            "--require-recommendation",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
            "--require-recommendation-evidence-field",
            "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token",
            "--require-recommendation-evidence-field",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_retained_by_policy",
            "--require-recommendation-evidence-field",
            (
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
                "sink_tokens_outside_ordinary_rolling_window"
            ),
            "--require-recommendation-theorem",
            "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103",
            "--require-recommendation-theorem",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149",
            "--require-recommendation-action-parameter",
            "KV-DROP-STALE-REQUEST-TOKEN=target_token",
            "--require-recommendation-action-parameter",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size",
            "--require-recommendation-action-parameter-path",
            "KV-DROP-STALE-REQUEST-TOKEN=target_token",
            "--require-recommendation-action-parameter-path",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size",
            "--require-recommendation-action-parameter-path",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count",
            "--require-recommendation-action-parameter-path",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound",
            "--require-recommendation-action-parameter-path",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size",
            "--require-recommendation-action-parameter-path",
            "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["kind"] == "kv_cache_ring_buffer"
    assert payload["required_theorem_ids"] == [
        "AIM-T0103",
        "AIM-T0104",
        "AIM-T0149",
    ]
    assert payload["evidence_fields"] == {
        "stale_probe_first_stale_token": 12,
        "sink_tokens_retained_by_policy": True,
        "sink_window_exact_policy": True,
        "sink_window_tokens_distinct": True,
        "sink_prefix_disjoint_from_live_window": True,
        "sink_tokens_outside_ordinary_rolling_window": True,
    }
    assert payload["required_recommendation_ids"] == [
        "KV-DROP-STALE-REQUEST-TOKEN",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    ]
    assert payload["required_recommendation_theorem_ids"] == {
        "KV-DROP-STALE-REQUEST-TOKEN": ["AIM-T0103"],
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST": ["AIM-T0149"],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "KV-DROP-STALE-REQUEST-TOKEN": ["target_token"],
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST": ["sink_size"],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "KV-DROP-STALE-REQUEST-TOKEN": ["target_token"],
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST": [
            "sink_size",
            "request_token_count",
            "request_token_count_bound",
            "cache_size",
            "current",
        ],
    }
    stale_action, sink_action = payload["planner_recommendations"]
    assert stale_action["target_token"] == 12
    assert sink_action["sink_size"] == 4
    assert sink_action["request_token_count"] == 20
    assert sink_action["request_token_count_bound"] == 20


def test_contract_ready_cli_emits_recurrence_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "recurrence_schedule",
            "--digest",
            "--format",
            "json",
            "--field",
            "scheduled_work_saving",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"scheduled_work_saving": 19}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    assert payload["planner_recommendations"][0]["active_token_work"] == 21
    assert payload["planner_recommendations"][0]["scheduled_work_saving"] == 19
    assert (
        payload["planner_recommendations"][0]["post_period_extension_scheduled_work_saving"]
        == 27
    )
    assert payload["planner_recommendations"][0]["post_period_extra_steps"] == 3
    assert (
        payload["planner_recommendations"][0][
            "post_period_multi_extension_scheduled_work_saving"
        ]
        == 43
    )
    assert payload["planner_recommendations"][1]["shifted_token"] == 22
    assert payload["planner_recommendations"][1]["active_step"] == 2


def test_contract_ready_cli_emits_recurrence_schedule_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "recurrence_schedule",
            "--receipt",
            "--format",
            "json",
            "--field",
            "periodic_shift_required_steps_invariant",
            "--field",
            "periodic_shift_active_at_step_invariant",
            "--field",
            "total_active_token_work",
            "--field",
            "scheduled_work_saving",
            "--field",
            "scheduled_work_saving_accounting",
            "--field",
            "active_inactive_work_accounting",
            "--field",
            "scheduled_work_saving_positive",
            "--field",
            "post_period_multi_extension_scheduled_work_saving",
            "--require-theorem",
            "AIM-T0026",
            "--require-theorem",
            "AIM-T0130",
            "--require-theorem",
            "AIM-T0159",
            "--require-recommendation",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
            "--require-recommendation",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
            "--require-recommendation-evidence-field",
            (
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "total_active_token_work"
            ),
            "--require-recommendation-evidence-field",
            (
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "scheduled_work_saving"
            ),
            "--require-recommendation-evidence-field",
            (
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "post_period_multi_extension_scheduled_work_saving"
            ),
            "--require-recommendation-evidence-field",
            (
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
                "periodic_shift_required_steps_invariant"
            ),
            "--require-recommendation-evidence-field",
            (
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
                "periodic_shift_active_at_step_invariant"
            ),
            "--require-recommendation-theorem",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130",
            "--require-recommendation-theorem",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159",
            "--require-recommendation-theorem",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026",
            "--require-recommendation-action-parameter",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period",
            "--require-recommendation-action-parameter",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving",
            "--require-recommendation-action-parameter",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving",
            "--require-recommendation-action-parameter-path",
            (
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "post_period_multi_extension_scheduled_work_saving"
            ),
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token",
            "--require-recommendation-action-parameter-path",
            "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["kind"] == "recurrence_schedule"
    assert payload["required_theorem_ids"] == [
        "AIM-T0026",
        "AIM-T0130",
        "AIM-T0159",
    ]
    assert payload["evidence_fields"] == {
        "periodic_shift_required_steps_invariant": True,
        "periodic_shift_active_at_step_invariant": True,
        "total_active_token_work": 21,
        "scheduled_work_saving": 19,
        "scheduled_work_saving_accounting": True,
        "active_inactive_work_accounting": True,
        "scheduled_work_saving_positive": True,
        "post_period_multi_extension_scheduled_work_saving": 43,
    }
    assert payload["required_recommendation_ids"] == [
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    assert payload["required_recommendation_theorem_ids"] == {
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE": [
            "AIM-T0130",
            "AIM-T0159",
        ],
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT": ["AIM-T0026"],
    }
    assert payload["required_recommendation_action_parameters"] == {
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE": [
            "loop_period",
            "scheduled_work_saving",
        ],
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT": ["base_token"],
    }
    assert payload["required_recommendation_action_parameter_paths"] == {
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE": [
            "loop_period",
            "token_count",
            "horizon_steps",
            "scheduled_work_saving",
            "post_period_multi_extension_scheduled_work_saving",
        ],
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT": [
            "base_token",
            "shifted_token",
            "shift_amount",
        ],
    }
    work_action, shift_action = payload["planner_recommendations"]
    assert work_action["loop_period"] == 5
    assert work_action["token_count"] == 8
    assert work_action["horizon_steps"] == 5
    assert work_action["scheduled_work_saving"] == 19
    assert work_action["post_period_multi_extension_scheduled_work_saving"] == 43
    assert shift_action["base_token"] == 7
    assert shift_action["shifted_token"] == 22
    assert shift_action["shift_amount"] == 15


def test_contract_ready_cli_emits_seed_rule_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--digest",
            "--format",
            "json",
            "--field",
            "storage_saving",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"storage_saving": 71}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
    ]
    assert payload["planner_recommendations"][0]["generated_object_length"] == 128
    assert payload["planner_recommendations"][1]["candidate_count"] == 3
    assert payload["planner_recommendations"][1]["storage_saving"] == 71


def test_contract_ready_cli_emits_cyclic_memory_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "cyclic_memory_residue_winding",
            "--digest",
            "--format",
            "json",
            "--field",
            "max_alias_load",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {"max_alias_load": 4}
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE",
        "MEMORY-AUDIT-FINITE-ALIAS-LOAD",
    ]
    assert payload["planner_recommendations"][0]["alias_count"] == 4
    assert payload["planner_recommendations"][0]["residue_slot"] == 7
    assert payload["planner_recommendations"][1]["slot_loads"] == [
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
    ]


def test_contract_ready_cli_emits_strided_fanout_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "strided_candidate_fanout",
            "--digest",
            "--format",
            "json",
            "--field",
            "full_coverage",
            "--field",
            "effective_candidate_budget",
            "--field",
            "duplicate_count",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "full_coverage": True,
        "effective_candidate_budget": 12,
        "duplicate_count": 0,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE",
        "FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET",
    ]
    assert payload["planner_recommendations"][0]["full_coverage"] is True
    assert payload["planner_recommendations"][0]["predicted_reach"] == 12
    assert payload["planner_recommendations"][1]["effective_candidate_budget"] == 12
    assert payload["planner_recommendations"][1]["duplicate_count"] == 0


def test_contract_ready_cli_emits_multicoil_phase_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "multicoil_phase_feature",
            "--digest",
            "--format",
            "json",
            "--field",
            "joint_repeat_horizon",
            "--field",
            "relative_phase",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "joint_repeat_horizon": 35,
        "relative_phase": 3,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "PHASE-USE-JOINT-REPEAT-HORIZON",
        "PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT",
    ]
    assert payload["planner_recommendations"][0]["phase_tuple"] == [2, 2]
    assert payload["planner_recommendations"][0]["joint_repeat_horizon"] == 35
    assert payload["planner_recommendations"][1]["relative_phase"] == 3
    assert payload["planner_recommendations"][1]["shifted_relative_phase"] == 3


def test_contract_ready_cli_emits_circulant_mixer_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "circulant_block_cyclic_mixer",
            "--digest",
            "--format",
            "json",
            "--field",
            "max_abs_dense_delta",
            "--field",
            "block_to_dense_ratio",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["evidence_fields"] == {
        "max_abs_dense_delta": 0,
        "block_to_dense_ratio": 0.0625,
    }
    assert [
        recommendation["id"]
        for recommendation in payload["planner_recommendations"]
    ] == [
        "MIXER-AUDIT-CIRCULANT-DENSE-PARITY",
        "MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET",
    ]
    assert payload["planner_recommendations"][0]["max_abs_dense_delta"] == 0
    assert payload["planner_recommendations"][0]["circulant_parameters"] == 8
    assert payload["planner_recommendations"][1]["block_cyclic_parameters"] == 128
    assert payload["planner_recommendations"][1]["block_to_dense_ratio"] == 0.0625


def test_contract_ready_cli_emits_text_digest_recommendations() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--digest",
            "--field",
            "first_uncovered_lag",
            "--include-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract digest ok: sparse_attention_coverage" in result.stdout
    assert (
        "recommendation.SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
        "action=increase_local_window scope=first_uncovered_interval_only"
    ) in result.stdout
    assert "recommendation.SPARSE-REPAIR-LARGEST-GAP-INTERVAL" in result.stdout
    assert "theorems=AIT-T0104" in result.stdout
    assert "recommendation.SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK" in result.stdout
    assert "theorems=AIT-T0023,AIT-T0034" in result.stdout


def test_contract_ready_cli_lists_kinds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-kinds",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "ready=True" in result.stdout
    assert "recommendations=2" in result.stdout


def test_contract_ready_cli_lists_recommendations_text() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-recommendations",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (
        "recommendation=ROPE-USE-D19-MARGIN-FRONTIER "
        "kind=rope_position_distinguishability"
    ) in result.stdout
    assert "contract=CC-AI-CONTRACT-ROPE-001" in result.stdout
    assert "recommendation=FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE" in result.stdout
    assert "recommendation=MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET" in result.stdout
    assert "ready=True" in result.stdout
    assert "theorems=" in result.stdout


def test_contract_ready_cli_lists_recommendations_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--list-recommendations",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert len(payload) == 20
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"]["kind"] == (
        "rope_position_distinguishability"
    )
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"]["contract_id"] == (
        "CC-AI-CONTRACT-ROPE-001"
    )
    assert payload["ROPE-USE-D19-MARGIN-FRONTIER"][
        "ready_for_downstream_fixture_use"
    ] is True
    assert "AIRA-T0216" in payload["ROPE-USE-D19-MARGIN-FRONTIER"]["theorem_ids"]
    assert payload["MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET"]["kind"] == (
        "circulant_block_cyclic_mixer"
    )


def test_contract_ready_cli_emits_action_plan_json_with_values() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "seed_rule_exact_regeneration",
            "--action-plan",
            "--include-values",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["planner_schema"] == "circle_calculus.ai_contract_planner.v0"
    assert payload["planner_includes_values"] is True
    assert payload["selected_kinds"] == ["seed_rule_exact_regeneration"]
    assert payload["planner_recommendation_count"] == 2
    assert payload["ready_recommendation_count"] == 2
    actions = payload["action_plan"]
    assert [action["recommendation_id"] for action in actions] == [
        "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
    ]
    assert actions[0]["evidence_values"]["fixture_n"] == 128
    assert actions[0]["evidence_values"]["exact_regeneration"] is True
    assert actions[1]["evidence_values"]["bounded_search_best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert actions[1]["action_parameters"]["best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert "GEN-T0046" in actions[1]["theorem_ids"]
    assert actions[1]["missing_evidence_fields"] == []


def test_contract_ready_cli_filters_action_plan_by_recommendation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--action-plan",
            "--recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--include-values",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["selected_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert [action["recommendation_id"] for action in payload["action_plan"]] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
    ]
    assert payload["planner_recommendation_count"] == 1
    assert payload["action_plan"][0]["evidence_values"][
        "first_uncovered_interval_start"
    ] == 5


def test_contract_ready_cli_rejects_missing_action_plan_recommendation() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--action-plan",
            "--recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "contract action plan failed" in result.stderr
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in result.stderr


def test_contract_ready_cli_recommendation_requires_action_plan() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "sparse_attention_coverage",
            "--recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--recommendation requires --action-plan" in result.stderr


def test_contract_ready_cli_emits_action_plan_text_for_all_kinds() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--action-plan",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI action plan ok:" in result.stdout
    assert "actions=20" in result.stdout
    assert "ready_actions=20" in result.stdout
    assert "includes_values=False" in result.stdout
    assert "action.ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "action.SPARSE-INTERVAL-REPAIR-PATH" in result.stdout
    assert "action.SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE" in result.stdout


def test_contract_ready_cli_rejects_unknown_kind() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--kind",
            "not_a_contract",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "unknown contract kind: not_a_contract" in result.stderr


def test_contract_ready_make_target_checks_flagship_kinds() -> None:
    result = subprocess.run(
        ["make", "circle-ai-contracts-ready"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "kind=rope_position_distinguishability" in result.stdout
    assert "recommendation=ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "circle AI action plan ok:" in result.stdout
    assert "actions=20" in result.stdout
    assert "ready_actions=20" in result.stdout
    assert (
        "python scripts/example_validate_circle_ai_contract_pack_schema.py "
        "--summary >/dev/null"
    ) in result.stdout
    assert (
        "python scripts/circle_ai_contract_ready.py --action-plan --recommendation "
        "ROPE-USE-D19-MARGIN-FRONTIER --format json >/dev/null"
    ) in result.stdout
    assert (
        "python scripts/example_consume_circle_ai_contract_pack.py --planner "
        "--planner-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
        "--planner-include-values >/dev/null"
    ) in result.stdout
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "seed_rule_exact_regeneration --action-plan --include-values "
        "--format json >/dev/null"
    ) in result.stdout
    assert "circle AI contract readiness ok: rope_position_distinguishability" in result.stdout
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "rope_position_distinguishability --digest --format json --field "
        "d19_proved_request_status"
    ) in result.stdout
    assert "d19_proved_first_channel_bank_transfer" in result.stdout
    assert "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK" in result.stdout
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in result.stdout
    assert "circle AI contract readiness ok: kv_cache_ring_buffer" in result.stdout
    assert "circle AI contract digest ok: kv_cache_ring_buffer" in result.stdout
    assert "evidence.stale_probe_first_stale_token=12" in result.stdout
    assert "circle AI contract digest ok: strided_candidate_fanout" in result.stdout
    assert "recommendation.FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE" in result.stdout
    assert (
        "recommendation.FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET"
        in result.stdout
    )
    assert "circle AI contract digest ok: multicoil_phase_feature" in result.stdout
    assert "recommendation.PHASE-USE-JOINT-REPEAT-HORIZON" in result.stdout
    assert (
        "recommendation.PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT"
        in result.stdout
    )
    assert "circle AI contract digest ok: circulant_block_cyclic_mixer" in result.stdout
    assert "recommendation.MIXER-AUDIT-CIRCULANT-DENSE-PARITY" in result.stdout
    assert (
        "recommendation.MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET"
        in result.stdout
    )
    assert "circle AI contract digest ok: cyclic_memory_residue_winding" in result.stdout
    assert "evidence.max_alias_load=4" in result.stdout
    assert (
        "recommendation.MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE"
        in result.stdout
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "sparse_attention_coverage --receipt --format json"
    ) in result.stdout
    assert "circle AI contract readiness ok: recurrence_schedule" in result.stdout
    assert "circle AI contract digest ok: recurrence_schedule" in result.stdout
    assert "evidence.scheduled_work_saving=19" in result.stdout
    assert "evidence.post_period_multi_extension_scheduled_work_saving=43" in result.stdout
    assert (
        "recommendation.RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
        in result.stdout
    )
    assert "circle AI contract digest ok: seed_rule_exact_regeneration" in result.stdout
    assert "evidence.storage_saving=71" in result.stdout
    assert (
        "recommendation.SEED-RULE-USE-EXACT-REGENERATION-RECIPE"
        in result.stdout
    )
