from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from circle_math.applications.circle_ai_contract_consumer import (
    ContractAcceptancePolicyError,
    contract_acceptance_policy_report,
    refresh_acceptance_policy_fingerprints,
    _json_fingerprint,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


ROOT = Path(__file__).resolve().parents[1]


def _policy_for(pack: dict) -> dict:
    return {
        "schema_id": "circle_calculus.ai_contract_acceptance_policy.v0",
        "policy_id": "test_flagship_policy",
        "policy_name": "Test flagship policy",
        "expected_pack_fingerprint": pack["pack_content_fingerprint"],
        "contracts": [
            {
                "kind": "sparse_attention_coverage",
                "expected_contract_fingerprint": pack[
                    "contract_fingerprint_index"
                ]["sparse_attention_coverage"]["content_fingerprint"],
                "required_fields": [
                    "first_uncovered_lag",
                    "first_uncovered_interval_start",
                    "complete_repair_window",
                    "complete_repair_window_covers_context",
                    "complete_repair_window_minimal_for_declared_stride_family",
                    "complete_repair_window_minimal_witness_lag",
                ],
                "required_theorem_ids": [
                    "AIT-T0104",
                    "AIT-T0172",
                ],
                "required_recommendation_ids": [
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
                    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
                ],
                "required_recommendation_evidence_fields": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "first_uncovered_interval_start",
                        "first_uncovered_interval_stop",
                    ],
                    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
                        "complete_repair_window",
                        "complete_repair_window_covers_context",
                        "complete_repair_window_uses_dense_threshold",
                        "local_window_complete_threshold_is_exact_local_minimum",
                        (
                            "complete_repair_window_minimal_for_declared_"
                            "stride_family"
                        ),
                        "complete_repair_window_minimal_witness_lag",
                    ],
                },
                "required_recommendation_theorem_ids": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "AIT-T0104",
                    ],
                    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
                        "AIT-T0023",
                        "AIT-T0034",
                        "AIT-T0172",
                        "AIT-T0168",
                        "AIT-T0169",
                        "AIT-T0170",
                    ],
                },
                "required_recommendation_action_parameters": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "proposed_local_window",
                    ],
                    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
                        "proposed_local_window",
                        "additional_local_slots",
                    ],
                },
                "required_recommendation_action_parameter_paths": {
                    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
                        "proposed_local_window",
                    ],
                    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
                        "proposed_local_window",
                        "additional_local_slots",
                    ],
                },
                "include_field_metadata": True,
            },
            {
                "kind": "kv_cache_ring_buffer",
                "expected_contract_fingerprint": pack[
                    "contract_fingerprint_index"
                ]["kv_cache_ring_buffer"]["content_fingerprint"],
                "required_fields": [
                    "stale_probe_first_stale_token",
                    "sink_tokens_retained_by_policy",
                    "sink_window_exact_policy",
                    "sink_window_tokens_distinct",
                    "sink_prefix_disjoint_from_live_window",
                    "sink_tokens_outside_ordinary_rolling_window",
                ],
                "required_theorem_ids": [
                    "AIM-T0103",
                    "AIM-T0149",
                ],
                "required_recommendation_ids": [
                    "KV-DROP-STALE-REQUEST-TOKEN",
                    "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
                ],
                "required_recommendation_evidence_fields": {
                    "KV-DROP-STALE-REQUEST-TOKEN": [
                        "stale_probe_first_stale_token",
                        "stale_probe_stale_requested_count",
                    ],
                    "KV-USE-SINK-ROLLING-WINDOW-REQUEST": [
                        "sink_window_exact_policy",
                        "sink_window_tokens_distinct",
                        "sink_prefix_disjoint_from_live_window",
                        "sink_rolling_tokens_retained",
                        "sink_tokens_non_future",
                        "sink_tokens_retained_by_policy",
                        "sink_tokens_outside_ordinary_rolling_window",
                    ],
                },
                "required_recommendation_theorem_ids": {
                    "KV-DROP-STALE-REQUEST-TOKEN": [
                        "AIM-T0103",
                    ],
                    "KV-USE-SINK-ROLLING-WINDOW-REQUEST": [
                        "AIM-T0104",
                        "AIM-T0110",
                        "AIM-T0117",
                        "AIM-T0136",
                        "AIM-T0137",
                        "AIM-T0148",
                        "AIM-T0149",
                    ],
                },
                "required_recommendation_action_parameters": {
                    "KV-DROP-STALE-REQUEST-TOKEN": [
                        "target_token",
                        "next_same_slot_overwrite_token",
                    ],
                    "KV-USE-SINK-ROLLING-WINDOW-REQUEST": [
                        "sink_size",
                        "request_token_count",
                        "request_token_count_bound",
                        "cache_size",
                        "current",
                    ],
                },
                "required_recommendation_action_parameter_paths": {
                    "KV-DROP-STALE-REQUEST-TOKEN": [
                        "target_token",
                    ],
                    "KV-USE-SINK-ROLLING-WINDOW-REQUEST": [
                        "sink_size",
                        "request_token_count",
                        "request_token_count_bound",
                        "cache_size",
                        "current",
                    ],
                },
            },
        ],
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def test_acceptance_policy_report_emits_receipts_for_selected_contracts() -> None:
    pack = build_contract_pack()
    report = contract_acceptance_policy_report(pack, _policy_for(pack))

    assert report["acceptance_policy_report_schema"] == (
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
    )
    assert report["accepted"] is True
    assert report["policy_id"] == "test_flagship_policy"
    assert report["contract_count"] == 2
    assert report["receipt_count"] == 2
    assert report["pack_content_fingerprint"] == pack["pack_content_fingerprint"]
    assert [receipt["kind"] for receipt in report["receipts"]] == [
        "sparse_attention_coverage",
        "kv_cache_ring_buffer",
    ]
    sparse_receipt = report["receipts"][0]
    assert sparse_receipt["evidence_fields"] == {
        "complete_repair_window": 119,
        "complete_repair_window_covers_context": True,
        "complete_repair_window_minimal_for_declared_stride_family": True,
        "complete_repair_window_minimal_witness_lag": 119,
        "first_uncovered_lag": 5,
        "first_uncovered_interval_start": 5,
    }
    assert [
        recommendation["id"]
        for recommendation in sparse_receipt["planner_recommendations"]
    ] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
    ]
    assert sparse_receipt["required_recommendation_evidence_fields"] == {
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
    assert sparse_receipt["required_theorem_ids"] == ["AIT-T0104", "AIT-T0172"]
    assert sparse_receipt["required_recommendation_theorem_ids"] == {
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
    assert sparse_receipt["required_recommendation_action_parameters"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert sparse_receipt["required_recommendation_action_parameter_paths"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert sparse_receipt["field_catalog"]["first_uncovered_lag"][
        "value_kind"
    ] == "integer"
    assert "not a claim of model quality" in report["not_claimed"]


def test_acceptance_policy_rejects_stale_fingerprints() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["expected_pack_fingerprint"] = "0" * 64
    policy["contracts"][0]["expected_contract_fingerprint"] = "1" * 64

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="pack fingerprint mismatch",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "sparse_attention_coverage fingerprint mismatch" in str(exc_info.value)


def test_acceptance_policy_refreshes_only_fingerprints() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["expected_pack_fingerprint"] = "0" * 64
    policy["contracts"][0]["expected_contract_fingerprint"] = "1" * 64

    refreshed = refresh_acceptance_policy_fingerprints(pack, policy)
    report = contract_acceptance_policy_report(pack, refreshed)

    assert refreshed["expected_pack_fingerprint"] == pack["pack_content_fingerprint"]
    assert refreshed["contracts"][0]["expected_contract_fingerprint"] == (
        pack["contract_fingerprint_index"]["sparse_attention_coverage"][
            "content_fingerprint"
        ]
    )
    assert refreshed["contracts"][0]["required_theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0172",
    ]
    assert refreshed["contracts"][0]["required_recommendation_theorem_ids"] == {
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
    assert refreshed["contracts"][0]["required_recommendation_action_parameters"] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert refreshed["contracts"][0][
        "required_recommendation_action_parameter_paths"
    ] == {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["proposed_local_window"],
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK": [
            "proposed_local_window",
            "additional_local_slots",
        ],
    }
    assert report["accepted"] is True


def test_acceptance_policy_refresh_rejects_unknown_kind() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["kind"] = "not_a_contract_kind"

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="not in contract_fingerprint_index",
    ):
        refresh_acceptance_policy_fingerprints(pack, policy)


def test_acceptance_policy_rejects_missing_fields_and_recommendations() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_fields"] = ["not_a_field"]
    policy["contracts"][0]["required_recommendation_ids"] = ["NOT-A-REC"]

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="missing requested evidence fields: not_a_field",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "missing requested planner recommendations: NOT-A-REC" in str(
        exc_info.value
    )


def test_acceptance_policy_rejects_missing_recommendation_evidence_fields() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_evidence_fields"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["not_recommendation_evidence"],
    }

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="missing required recommendation evidence fields",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR" in str(exc_info.value)
    assert "not_recommendation_evidence" in str(exc_info.value)


def test_acceptance_policy_rejects_missing_theorem_pins() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_theorem_ids"] = ["NOT-A-THEOREM"]
    policy["contracts"][0]["required_recommendation_theorem_ids"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["NOT-A-REC-THEOREM"],
    }

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="missing requested theorem ids: NOT-A-THEOREM",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "missing required recommendation theorem ids" in str(exc_info.value)
    assert "NOT-A-REC-THEOREM" in str(exc_info.value)


def test_acceptance_policy_rejects_missing_action_parameter_pins() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_action_parameters"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": ["not_an_action_parameter"],
    }

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="missing required recommendation action parameters",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR" in str(exc_info.value)
    assert "not_an_action_parameter" in str(exc_info.value)


def test_acceptance_policy_rejects_missing_action_parameter_path_pins() -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["contracts"][0]["required_recommendation_action_parameter_paths"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "not_an_action_parameter.path",
        ],
    }

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="invalid recommendation action-parameter paths",
    ) as exc_info:
        contract_acceptance_policy_report(pack, policy)

    assert "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR" in str(exc_info.value)
    assert "not_an_action_parameter.path" in str(exc_info.value)


def test_acceptance_policy_rejects_malformed_policy_shape() -> None:
    pack = build_contract_pack()

    with pytest.raises(
        ContractAcceptancePolicyError,
        match="policy.contracts must be a non-empty list",
    ):
        contract_acceptance_policy_report(
            pack,
            {
                "schema_id": "circle_calculus.ai_contract_acceptance_policy.v0",
                "expected_pack_fingerprint": pack["pack_content_fingerprint"],
                "contracts": [],
            },
        )

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_evidence_fields"] = [
        "not-an-object",
    ]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_recommendation_evidence_fields must be an object",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_theorem_ids"] = [
        "not-an-object",
    ]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_recommendation_theorem_ids must be an object",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_action_parameters"] = [
        "not-an-object",
    ]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_recommendation_action_parameters must be an object",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_action_parameter_paths"] = [
        "not-an-object",
    ]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_recommendation_action_parameter_paths must be an object",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_fields"] = [
        "first_uncovered_lag",
        "first_uncovered_lag",
    ]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_fields must not contain duplicate strings",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_theorem_ids"] = [""]
    with pytest.raises(
        ContractAcceptancePolicyError,
        match="required_theorem_ids must not contain empty strings",
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_evidence_fields"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "first_uncovered_interval_start",
            "first_uncovered_interval_start",
        ],
    }
    with pytest.raises(
        ContractAcceptancePolicyError,
        match=(
            "required_recommendation_evidence_fields"
            ".*must not contain duplicate strings"
        ),
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_theorem_ids"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [""],
    }
    with pytest.raises(
        ContractAcceptancePolicyError,
        match=(
            "required_recommendation_theorem_ids"
            ".*must not contain empty strings"
        ),
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_action_parameters"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "proposed_local_window",
            "proposed_local_window",
        ],
    }
    with pytest.raises(
        ContractAcceptancePolicyError,
        match=(
            "required_recommendation_action_parameters"
            ".*must not contain duplicate strings"
        ),
    ):
        contract_acceptance_policy_report(pack, malformed)

    malformed = _policy_for(pack)
    malformed["contracts"][0]["required_recommendation_action_parameter_paths"] = {
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR": [
            "proposed_local_window",
            "proposed_local_window",
        ],
    }
    with pytest.raises(
        ContractAcceptancePolicyError,
        match=(
            "required_recommendation_action_parameter_paths"
            ".*must not contain duplicate strings"
        ),
    ):
        contract_acceptance_policy_report(pack, malformed)


def test_default_flagship_policy_matches_generated_contract_pack() -> None:
    pack = json.loads(
        (ROOT / "site/data/generated/circle_ai_contract_pack.json").read_text()
    )
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )

    report = contract_acceptance_policy_report(pack, policy)

    assert report["policy_id"] == "circle_ai_flagship_contracts_acceptance_v0"
    assert report["contract_count"] == 4
    assert [receipt["kind"] for receipt in report["receipts"]] == [
        "rope_position_distinguishability",
        "kv_cache_ring_buffer",
        "sparse_attention_coverage",
        "recurrence_schedule",
    ]
    rope_receipt = report["receipts"][0]
    assert rope_receipt["required_fields"] == [
        "preset",
        "context_length",
        "exact_discrete_pass",
        "common_collision_gap",
        "total_bank_collision_pair_count",
        "d19_context_range_min_exclusive",
        "d19_context_range_max_inclusive",
        "d19_request_context",
        "d19_proved_request_status",
        "d19_impossible_request_status",
        "d19_impossible_obstruction_gap",
        "d19_impossible_obstruction_turns",
        "d19_undecided_request_status",
        "d19_undecided_margin_open_gap",
        "d19_undecided_probe_margin_in_open_gap",
        "d19_undecided_margin_interval_width",
        "d19_undecided_request_relation",
        "d19_margin_status_exhaustive",
        "d19_in_range_semantic_trichotomy",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_radian_bank_form",
        "d19_proved_first_channel_bank_tolerance_rule",
        "real_phase_nearest_integer_certificate_bridge",
        "real_phase_dirichlet_witness_guardrail",
        "real_phase_margin_ceiling_guardrail",
        "real_phase_exact_weakest_margin_ceiling_guardrail",
    ]
    assert rope_receipt["required_recommendation_ids"] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert rope_receipt["required_recommendation_evidence_fields"][
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
    ] == [
        "preset",
        "context_length",
        "exact_discrete_pass",
        "common_collision_gap",
        "total_bank_collision_pair_count",
    ]
    assert rope_receipt["required_recommendation_evidence_fields"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] == [
        "d19_context_range_min_exclusive",
        "d19_context_range_max_inclusive",
        "d19_request_context",
        "d19_proved_request_status",
        "d19_impossible_request_status",
        "d19_impossible_obstruction_gap",
        "d19_impossible_obstruction_turns",
        "d19_undecided_request_status",
        "d19_undecided_margin_open_gap",
        "d19_undecided_probe_margin_in_open_gap",
        "d19_undecided_margin_interval_width",
        "d19_undecided_request_relation",
        "d19_margin_status_exhaustive",
        "d19_in_range_semantic_trichotomy",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_radian_bank_form",
        "d19_proved_first_channel_bank_tolerance_rule",
        "real_phase_nearest_integer_certificate_bridge",
        "real_phase_dirichlet_witness_guardrail",
        "real_phase_margin_ceiling_guardrail",
        "real_phase_exact_weakest_margin_ceiling_guardrail",
    ]
    assert rope_receipt["required_theorem_ids"] == [
        "AIRA-T0058",
        "AIRA-T0059",
        "AIRA-T0177",
        "AIRA-T0178",
        "AIRA-T0182",
        "AIRA-T0183",
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0184",
        "AIRA-T0216",
        "AIRA-T0231",
        "AIRA-T0233",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
        "AIRA-T0238",
        "AIRA-T0239",
        "AIRA-T0240",
        "AIRA-T0241",
    ]
    assert rope_receipt["required_recommendation_theorem_ids"][
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
    ] == [
        "AIRA-T0024",
        "AIRA-T0036",
        "AIRA-T0179",
        "AIRA-T0180",
        "AIRA-T0184",
    ]
    assert rope_receipt["required_recommendation_theorem_ids"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] == [
        "AIRA-T0058",
        "AIRA-T0059",
        "AIRA-T0177",
        "AIRA-T0178",
        "AIRA-T0182",
        "AIRA-T0183",
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0216",
        "AIRA-T0231",
        "AIRA-T0233",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
        "AIRA-T0238",
        "AIRA-T0239",
        "AIRA-T0240",
        "AIRA-T0241",
    ]
    assert rope_receipt["required_recommendation_action_parameters"][
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
    ] == [
        "preset",
        "context_length",
        "exact_discrete_pass",
        "common_collision_gap",
        "collision_pair_count",
    ]
    assert rope_receipt["required_recommendation_action_parameters"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] == [
        "applicable_context_range",
        "classifier_regions",
        "impossible_obstruction_gap",
        "impossible_obstruction_turns",
        "undecided_interval",
        "proved_branch_bank_transfer",
    ]
    assert rope_receipt["required_recommendation_action_parameter_paths"][
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
    ] == [
        "preset",
        "context_length",
        "exact_discrete_pass",
        "common_collision_gap",
        "collision_pair_count",
    ]
    assert rope_receipt["required_recommendation_action_parameter_paths"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] == [
        "applicable_context_range.min_exclusive",
        "applicable_context_range.max_inclusive",
        "impossible_obstruction_gap",
        "impossible_obstruction_turns",
        "classifier_regions[region=proved].theorem_ids",
        "classifier_regions[region=undecided_margin_gap].condition",
        "classifier_regions[region=impossible].theorem_ids",
        "undecided_interval.width",
        "proved_branch_bank_transfer.applies",
        "proved_branch_bank_transfer.bank_shape",
        "proved_branch_bank_transfer.context_wide_contract",
        "proved_branch_bank_transfer.radian_bank_form",
        "proved_branch_bank_transfer.theorem_ids",
    ]
    kv_receipt = report["receipts"][1]
    assert kv_receipt["required_fields"] == [
        "stale_probe_first_stale_token",
        "sink_tokens_retained_by_policy",
        "sink_window_exact_policy",
        "sink_window_tokens_distinct",
        "sink_prefix_disjoint_from_live_window",
        "sink_tokens_outside_ordinary_rolling_window",
    ]
    assert kv_receipt["required_recommendation_ids"] == [
        "KV-DROP-STALE-REQUEST-TOKEN",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    ]
    assert kv_receipt["required_theorem_ids"] == [
        "AIM-T0103",
        "AIM-T0149",
    ]
    assert kv_receipt["required_recommendation_evidence_fields"][
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST"
    ] == [
        "sink_window_exact_policy",
        "sink_window_tokens_distinct",
        "sink_prefix_disjoint_from_live_window",
        "sink_rolling_tokens_retained",
        "sink_tokens_non_future",
        "sink_tokens_retained_by_policy",
        "sink_tokens_outside_ordinary_rolling_window",
    ]
    assert kv_receipt["required_recommendation_theorem_ids"][
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST"
    ] == [
        "AIM-T0104",
        "AIM-T0110",
        "AIM-T0117",
        "AIM-T0136",
        "AIM-T0137",
        "AIM-T0148",
        "AIM-T0149",
    ]
    sparse_receipt = report["receipts"][2]
    assert sparse_receipt["required_fields"] == [
        "first_uncovered_lag",
        "first_uncovered_interval_start",
        "complete_repair_window",
        "complete_repair_window_covers_context",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
    ]
    assert sparse_receipt["required_recommendation_ids"] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
    ]
    assert sparse_receipt["required_theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0172",
    ]
    assert sparse_receipt["required_recommendation_evidence_fields"][
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    ] == [
        "complete_repair_window",
        "complete_repair_window_covers_context",
        "complete_repair_window_uses_dense_threshold",
        "local_window_complete_threshold_is_exact_local_minimum",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
    ]
    assert sparse_receipt["required_recommendation_theorem_ids"][
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK"
    ] == [
        "AIT-T0023",
        "AIT-T0034",
        "AIT-T0172",
        "AIT-T0168",
        "AIT-T0169",
        "AIT-T0170",
    ]
    recurrence_receipt = report["receipts"][3]
    assert recurrence_receipt["required_fields"] == [
        "periodic_shift_required_steps_invariant",
        "periodic_shift_active_at_step_invariant",
        "total_active_token_work",
        "scheduled_work_saving",
        "scheduled_work_saving_accounting",
        "active_inactive_work_accounting",
        "scheduled_work_saving_positive",
        "post_period_multi_extension_scheduled_work_saving",
    ]
    assert recurrence_receipt["required_recommendation_ids"] == [
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    assert recurrence_receipt["required_theorem_ids"] == [
        "AIM-T0026",
        "AIM-T0130",
        "AIM-T0159",
    ]
    assert recurrence_receipt["required_recommendation_evidence_fields"][
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
    ] == [
        "total_active_token_work",
        "scheduled_work_saving",
        "scheduled_work_saving_accounting",
        "active_inactive_work_accounting",
        "scheduled_work_saving_positive",
        "post_period_multi_extension_scheduled_work_saving",
    ]
    assert recurrence_receipt["required_recommendation_theorem_ids"][
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
    ] == [
        "AIM-T0130",
        "AIM-T0131",
        "AIM-T0138",
        "AIM-T0140",
        "AIM-T0141",
        "AIM-T0142",
        "AIM-T0143",
        "AIM-T0144",
        "AIM-T0145",
        "AIM-T0147",
        "AIM-T0150",
        "AIM-T0151",
        "AIM-T0152",
        "AIM-T0153",
        "AIM-T0154",
        "AIM-T0155",
        "AIM-T0156",
        "AIM-T0157",
        "AIM-T0158",
        "AIM-T0159",
    ]


def test_acceptance_policy_cli_accepts_dynamic_policy(tmp_path: Path) -> None:
    pack = build_contract_pack()
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    _write_json(pack_path, pack)
    _write_json(policy_path, _policy_for(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_acceptance_policy.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    assert payload["receipt_count"] == 2
    assert payload["receipts"][0]["kind"] == "sparse_attention_coverage"


def test_acceptance_policy_cli_validates_report_schema_sidecars(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack["acceptance_policy"]["report_schema_path"] = (
        "site/data/generated/DOES_NOT_EXIST_REPORT.schema.json"
    )
    pack["pack_content_fingerprint"] = _json_fingerprint(pack)
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    _write_json(pack_path, pack)
    _write_json(policy_path, _policy_for(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_acceptance_policy.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance policy failed" in result.stderr
    assert "DOES_NOT_EXIST_REPORT.schema.json" in result.stderr


def test_acceptance_policy_cli_prints_refreshed_policy(tmp_path: Path) -> None:
    pack = build_contract_pack()
    stale_policy = _policy_for(pack)
    stale_policy["expected_pack_fingerprint"] = "0" * 64
    stale_policy["contracts"][0]["expected_contract_fingerprint"] = "1" * 64
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    _write_json(pack_path, pack)
    _write_json(policy_path, stale_policy)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_acceptance_policy.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--print-refreshed-policy",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    refreshed = json.loads(result.stdout)
    report = contract_acceptance_policy_report(pack, refreshed)
    assert refreshed["expected_pack_fingerprint"] == pack["pack_content_fingerprint"]
    assert refreshed["contracts"][0]["expected_contract_fingerprint"] == (
        pack["contract_fingerprint_index"]["sparse_attention_coverage"][
            "content_fingerprint"
        ]
    )
    assert refreshed["contracts"][0]["required_theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0172",
    ]
    assert report["accepted"] is True


def test_acceptance_policy_cli_text_reports_recommendation_evidence_fields(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    _write_json(pack_path, pack)
    _write_json(policy_path, _policy_for(pack))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_acceptance_policy.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "text",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract acceptance policy ok:" in result.stdout
    assert "receipt.sparse_attention_coverage" in result.stdout
    assert "recommendation_evidence_fields=8" in result.stdout
    assert "recommendation_theorems=7" in result.stdout
    assert "recommendation_action_parameter_paths=3" in result.stdout


def test_acceptance_policy_cli_rejects_stale_policy(tmp_path: Path) -> None:
    pack = build_contract_pack()
    policy = _policy_for(pack)
    policy["expected_pack_fingerprint"] = "0" * 64
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    _write_json(pack_path, pack)
    _write_json(policy_path, policy)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_acceptance_policy.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    assert "acceptance policy failed" in result.stderr
    assert "pack fingerprint mismatch" in result.stderr
