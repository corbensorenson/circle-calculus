from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from circle_math.applications import (
    build_contract_artifact_manifest_file_check_json_schema,
    build_contract_artifact_manifest_file_check_report,
    build_contract_artifact_manifest_json_schema,
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_json_schema,
    build_contract_receipt,
    build_contract_receipt_file_check_json_schema,
    build_contract_receipt_file_check_report,
    build_contract_receipt_gate_report,
    build_contract_receipt_json_schema,
    build_contract_receipt_replay_check_json_schema,
    build_contract_receipt_replay_check_report,
    build_contract_receipt_from_request,
    build_contract_request,
    build_contract_runner_check_json_schema,
    build_contract_request_json_schema,
    build_contract_request_validation_report,
    build_contract_request_validation_json_schema,
    build_compact_contract_receipt,
    build_compact_contract_receipt_json_schema,
    build_circulant_block_cyclic_mixer_receipt,
    build_cyclic_memory_receipt,
    build_kv_cache_receipt,
    build_multicoil_phase_feature_receipt,
    build_recurrence_receipt,
    build_rope_contract_request_from_model_config,
    build_rope_model_config_import_json_schema,
    build_rope_model_config_import_report,
    build_rope_request_parameters_from_model_config,
    build_rope_receipt,
    build_seed_rule_receipt,
    build_sparse_attention_receipt,
    build_strided_candidate_fanout_receipt,
    build_validated_contract_receipt,
    build_validated_contract_receipt_from_request,
    build_validated_rope_receipt_from_model_config,
    receipt_summary_lines,
    require_contract_receipt_gate,
    validate_contract_request,
    validate_contract_receipt,
    validate_contract_receipt_against_pack,
)
from circle_math.applications.circle_ai_contracts import build_contract_pack


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "circle_ai_certify.py"
ARTIFACT_MANIFEST_CHECK_SCRIPT = (
    ROOT / "scripts" / "check_circle_ai_artifact_manifest.py"
)
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)
PUBLIC_CONTRACT_PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
PACK_FINGERPRINT_ALGORITHM = "sha256-json-v1"
PACK_FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}
PROOF_LAYER_BUCKETS = (
    "proved_fields",
    "computed_fields",
    "numerical_only_fields",
    "unsupported_fields",
)


def _json_fingerprint(value: dict) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _receipt_fingerprint(receipt: dict) -> str:
    def strip(value):
        if isinstance(value, dict):
            return {
                key: strip(child)
                for key, child in value.items()
                if key != "receipt_content_fingerprint"
            }
        if isinstance(value, list):
            return [strip(child) for child in value]
        return value

    return _json_fingerprint(strip(receipt))


def _strip_pack_fingerprint_fields(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: _strip_pack_fingerprint_fields(child)
            for key, child in sorted(value.items())
            if key not in PACK_FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_strip_pack_fingerprint_fields(child) for child in value]
    return value


def _pack_content_fingerprint(value: object) -> str:
    normalized = json.dumps(
        _strip_pack_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _refresh_pack_fingerprints(pack: dict) -> None:
    for contract in pack["contracts"]:
        theorem_ids = contract.get("theorem_ids")
        proof_status = contract.get("proof_status")
        if isinstance(theorem_ids, list) and isinstance(proof_status, dict):
            theorem_id_set = set(theorem_ids)
            theorems = proof_status.get("theorems")
            if isinstance(theorems, list):
                proof_status["theorems"] = [
                    theorem
                    for theorem in theorems
                    if isinstance(theorem, dict)
                    and theorem.get("id") in theorem_id_set
                ]
            proof_status["theorem_count"] = len(theorem_ids)
            readiness = pack.get("contract_readiness_index", {}).get(
                contract.get("kind")
            )
            if isinstance(readiness, dict):
                readiness["theorem_count"] = len(theorem_ids)
        contract["content_fingerprint_algorithm"] = PACK_FINGERPRINT_ALGORITHM
        contract["content_fingerprint"] = _pack_content_fingerprint(contract)
    pack["contract_fingerprint_index"] = {
        contract["kind"]: {
            "id": contract["id"],
            "content_fingerprint_algorithm": PACK_FINGERPRINT_ALGORITHM,
            "content_fingerprint": contract["content_fingerprint"],
        }
        for contract in pack["contracts"]
    }
    pack["content_fingerprint_algorithm"] = PACK_FINGERPRINT_ALGORITHM
    pack["pack_content_fingerprint"] = _pack_content_fingerprint(pack)


def _assert_decision_matches_receipt(
    receipt: dict,
    *,
    verdict: str | None = None,
    assurance: str | None = None,
) -> None:
    decision = receipt["decision"]
    assert decision["schema_id"] == "circle_calculus.ai_contract_decision.v0"
    assert decision["claim_status"] == receipt["status"]
    assert decision["request_passed"] == receipt["request_passed"]
    assert decision["theorem_count"] == receipt["proof_status"]["theorem_count"]
    assert decision["all_theorem_ids_proved"] == receipt["proof_status"][
        "all_theorem_ids_proved"
    ]
    assert decision["proof_layer_counts"] == {
        bucket: len(receipt["proof_layers"][bucket]) for bucket in PROOF_LAYER_BUCKETS
    }
    assert decision["summary"]
    assert decision["next_action"]
    if verdict is not None:
        assert decision["verdict"] == verdict
    if assurance is not None:
        assert decision["assurance"] == assurance


@pytest.fixture(scope="module")
def contract_pack() -> dict:
    return build_contract_pack()


def test_rope_receipt_classifies_d19_margin_request(contract_pack: dict) -> None:
    receipt = build_rope_receipt(
        head_dim=128,
        base=10000.0,
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    assert validate_contract_receipt(receipt) == []
    assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    _assert_decision_matches_receipt(
        receipt,
        verdict="passed",
        assurance="mixed_theorem_and_computation",
    )
    classifier = receipt["evidence"]["standard_channel0_d19_request_classifier"]
    assert classifier["request_status"] == "proved"
    assert classifier["theorem_backed_classification"] is True
    assert "AIRA-T0238" in receipt["proof_status"]["theorem_ids"]
    guardrail = receipt["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["applies"] is True
    assert guardrail["inv_context_margin"] == "1/131072"
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "below_dirichlet_ceiling"
    )
    assert guardrail["requested_margin_exceeds_ceiling"] is False
    assert "AIRA-T0240" in receipt["proof_status"]["theorem_ids"]
    assert "real_phase_dirichlet_guardrail" in receipt["proof_layers"][
        "proved_fields"
    ]
    bank_bridge = receipt["evidence"]["standard_channel0_d19_bank_bridge"]
    assert bank_bridge["applies"] is True
    assert bank_bridge["request_status"] == "proved_conditional_bank_no_near_turn"
    assert bank_bridge["bank_shape"] == "standard_channel0_first"
    assert bank_bridge["context_wide_first_channel_contract"] is True
    assert bank_bridge["radian_bank_form"] is True
    assert bank_bridge["pair_scope"] == (
        "all ordered unequal pairs left < right < requested_context"
    )
    assert bank_bridge["theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
    ]
    assert "AIRA-T0236" in receipt["proof_status"]["theorem_ids"]
    assert "standard_channel0_d19_bank_bridge" in receipt["proof_layers"][
        "proved_fields"
    ]
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    assert len(receipt["request_content_fingerprint"]) == 64
    assert len(receipt["normalized_request_fingerprint"]) == 64
    assert receipt["recommendations"]
    assert receipt["recommendations"] == receipt["support"]["planner_recommendations"]
    assert receipt["validation_commands"]
    assert receipt["validation_commands"] == receipt["support"]["validation_commands"]
    assert "real_phase_numerical_worst_gap" in receipt["proof_layers"][
        "numerical_only_fields"
    ]
    assert any(
        "full all-channel" in field
        for field in receipt["proof_layers"]["unsupported_fields"]
    )
    assert len(receipt["receipt_content_fingerprint"]) == 64


def test_compact_receipt_public_api_surfaces_downstream_fields(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(
        head_dim=128,
        base=10000.0,
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    compact = build_compact_contract_receipt(receipt)

    jsonschema.validate(compact, build_compact_contract_receipt_json_schema())
    assert compact["schema_id"] == "circle_calculus.ai_contract_compact_receipt.v0"
    assert compact["receipt_schema_id"] == receipt["schema_id"]
    assert compact["kind"] == receipt["kind"]
    assert compact["contract_id"] == receipt["contract_id"]
    assert compact["status"] == "proved"
    assert compact["request_passed"] is True
    assert compact["decision"]["verdict"] == receipt["decision"]["verdict"]
    assert compact["decision"]["assurance"] == receipt["decision"]["assurance"]
    assert compact["decision"]["proof_layer_counts"] == {
        bucket: len(receipt["proof_layers"][bucket]) for bucket in PROOF_LAYER_BUCKETS
    }
    assert compact["proof_status_summary"]["theorem_ids"] == receipt[
        "proof_status"
    ]["theorem_ids"]
    assert compact["proof_status_summary"]["all_theorem_ids_proved"] is True
    assert "AIRA-T0238" in compact["proof_status_summary"]["theorem_ids"]
    assert compact["normalized_request"] == receipt["normalized_request"]
    assert compact["proof_layer_counts"] == compact["decision"][
        "proof_layer_counts"
    ]
    assert "standard_channel0_d19_request_classifier.request_status" in compact[
        "selected_evidence"
    ]
    assert (
        compact["selected_evidence"][
            "standard_channel0_d19_request_classifier.request_status"
        ]
        == "proved"
    )
    assert "exact_total_bank_collision_pair_count" in compact["selected_evidence"]
    assert "standard_channel0_d19_request_classifier" in compact[
        "evidence_field_names"
    ]
    assert "evidence" not in compact
    assert compact["recommendation_ids"]
    assert compact["validation_commands"] == receipt["validation_commands"]
    assert compact["not_claimed"] == receipt["not_claimed"]
    assert compact["fingerprints"]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert compact["fingerprints"]["contract_pack_fingerprint"] == receipt[
        "support"
    ]["contract_pack_fingerprint"]
    assert compact["fingerprints"]["contract_content_fingerprint"] == receipt[
        "support"
    ]["contract_content_fingerprint"]


def test_rope_receipt_uses_d19_bank_bridge_for_smaller_context(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(
        head_dim=128,
        base=10000.0,
        context=4096,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    assert validate_contract_receipt(receipt) == []
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    _assert_decision_matches_receipt(
        receipt,
        verdict="passed",
        assurance="mixed_theorem_and_computation",
    )
    classifier = receipt["evidence"]["standard_channel0_d19_request_classifier"]
    assert classifier["request_status"] == "outside_range"
    bank_bridge = receipt["evidence"]["standard_channel0_d19_bank_bridge"]
    assert bank_bridge["applies"] is True
    assert bank_bridge["requested_context"] == 4096
    assert bank_bridge["requested_margin"] == "1/328459"
    assert bank_bridge["certified_context"] == 196608
    assert bank_bridge["certified_margin"] == "1/328459"
    assert bank_bridge["theorem_backed"] is True
    assert bank_bridge["radian_bank_form"] is True
    assert bank_bridge["failure_reason"] is None
    assert "standard_channel0_d19_bank_bridge" in receipt["proof_layers"][
        "proved_fields"
    ]
    assert any(
        "standard_channel0_d19_request_classifier outside" in field
        for field in receipt["proof_layers"]["unsupported_fields"]
    )
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_rope_receipt_distinguishes_impossible_and_undecided_margins(
    contract_pack: dict,
) -> None:
    impossible = build_rope_receipt(
        context=131072,
        requested_margin="1/328458",
        pack=contract_pack,
    )
    undecided = build_rope_receipt(
        context=131072,
        requested_margin="2/656917",
        pack=contract_pack,
    )

    assert impossible["status"] == "impossible"
    assert impossible["request_passed"] is False
    _assert_decision_matches_receipt(
        impossible,
        verdict="failed",
        assurance="mixed_theorem_and_computation",
    )
    assert impossible["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "impossible"
    assert impossible["proof_status"]["all_theorem_ids_proved"] is True
    assert undecided["status"] == "undecided"
    assert undecided["request_passed"] is None
    _assert_decision_matches_receipt(
        undecided,
        verdict="undecided",
        assurance="undecided",
    )
    assert undecided["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "undecided_margin_gap"
    assert validate_contract_receipt(undecided) == []

    above_ceiling = build_rope_receipt(
        context=1000,
        requested_margin="1/999",
        pack=contract_pack,
    )
    assert above_ceiling["status"] == "impossible"
    assert above_ceiling["request_passed"] is False
    _assert_decision_matches_receipt(
        above_ceiling,
        verdict="failed",
        assurance="mixed_theorem_and_computation",
    )
    guardrail = above_ceiling["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "above_dirichlet_ceiling"
    )
    assert guardrail["requested_margin_exceeds_ceiling"] is True
    assert "AIRA-T0240" in guardrail["theorem_ids"]
    assert above_ceiling["proof_status"]["all_theorem_ids_proved"] is True


def test_receipt_summary_lines_surface_proof_layer_counts(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(
        head_dim=128,
        base=10000.0,
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    lines = receipt_summary_lines(receipt)

    proof_layer_line = next(line for line in lines if line.startswith("proof_layers="))
    decision_line = next(line for line in lines if line.startswith("decision="))
    bank_bridge_line = next(
        line for line in lines if line.startswith("rope_d19_bank_bridge=")
    )
    proof_layers = receipt["proof_layers"]
    assert f"proved_fields={len(proof_layers['proved_fields'])}" in proof_layer_line
    assert f"computed_fields={len(proof_layers['computed_fields'])}" in proof_layer_line
    assert (
        f"numerical_only_fields={len(proof_layers['numerical_only_fields'])}"
        in proof_layer_line
    )
    assert (
        f"unsupported_fields={len(proof_layers['unsupported_fields'])}"
        in proof_layer_line
    )
    assert "verdict=passed" in decision_line
    assert "assurance=mixed_theorem_and_computation" in decision_line
    assert "applies=True" in bank_bridge_line
    assert "theorem_backed=True" in bank_bridge_line
    assert "radian_bank_form=True" in bank_bridge_line
    assert "bank_shape=standard_channel0_first" in bank_bridge_line


def test_kv_sparse_and_recurrence_receipts_preserve_family_semantics(
    contract_pack: dict,
) -> None:
    stale_kv = build_kv_cache_receipt(
        cache_size=16,
        current=31,
        token=20,
        batch_tokens=(12, 20),
        sink_size=4,
        request_id="stale_read",
        pack=contract_pack,
    )
    sparse = build_sparse_attention_receipt(
        context=120,
        strides=(7, 13),
        path_length=3,
        local_window=4,
        pack=contract_pack,
    )
    recurrence = build_recurrence_receipt(pack=contract_pack)

    assert stale_kv["status"] == "proved"
    assert stale_kv["request_passed"] is False
    _assert_decision_matches_receipt(
        stale_kv,
        verdict="failed",
        assurance="theorem_backed",
    )
    adapter = stale_kv["evidence"]["adapter_request_trace_certificate"]
    assert adapter["first_stale_token"] == 12
    assert adapter["stale_member_blocks_pass"] is True
    assert "sink_window_certificate" in stale_kv["proof_layers"]["proved_fields"]
    sink = stale_kv["evidence"]["sink_window_certificate"]
    assert sink["sink_size"] == 4
    assert sink["token_count"] == 20
    assert sink["generated_tokens_exact_policy"] is True
    assert sink["tokens_distinct"] is True
    assert sink["sink_tokens_retained_by_policy"] is True
    assert sink["sink_tokens_outside_ordinary_rolling_window"] is True
    stale_kv_lines = receipt_summary_lines(stale_kv)
    sink_line = next(
        line for line in stale_kv_lines if line.startswith("kv_cache_sink_window=")
    )
    assert "sink_size=4" in sink_line
    assert "exact_policy=True" in sink_line
    assert "sink_tokens_retained=True" in sink_line
    assert stale_kv["proof_status"]["all_theorem_ids_proved"] is True

    no_sink_kv = build_kv_cache_receipt(
        cache_size=16,
        current=31,
        token=20,
        batch_tokens=(12, 20),
        sink_size=0,
        request_id="stale_read_without_sink",
        pack=contract_pack,
    )
    assert "sink_window_certificate" not in no_sink_kv["evidence"]
    assert "sink_window_certificate" not in no_sink_kv["proof_layers"][
        "proved_fields"
    ]
    assert any(
        "sink_window_certificate requires positive sink_size" in field
        for field in no_sink_kv["proof_layers"]["unsupported_fields"]
    )
    assert not any(
        line.startswith("kv_cache_sink_window=")
        for line in receipt_summary_lines(no_sink_kv)
    )

    assert sparse["status"] == "proved"
    assert sparse["request_passed"] is False
    _assert_decision_matches_receipt(
        sparse,
        verdict="failed",
        assurance="theorem_backed",
    )
    assert sparse["evidence"]["coverage_complete"] is False
    assert sparse["evidence"]["first_uncovered_lag"] == 5
    assert "raw_candidate_budget_upper_bound" in sparse["proof_layers"][
        "proved_fields"
    ]
    assert "theorem_side_lag_candidate_collision_pair_count" in sparse[
        "proof_layers"
    ]["proved_fields"]
    assert "stride_family_zero_residue_total_step_count" in sparse["proof_layers"][
        "proved_fields"
    ]
    assert "first_uncovered_lag_interval_start" in sparse["proof_layers"][
        "proved_fields"
    ]
    assert "largest_uncovered_interval_repair_window" in sparse["proof_layers"][
        "proved_fields"
    ]
    assert "complete_repair_window_minimal_for_declared_stride_family" in sparse[
        "proof_layers"
    ]["proved_fields"]
    assert "interval_repair_plan_covers_context" in sparse["proof_layers"][
        "proved_fields"
    ]
    sparse_lines = receipt_summary_lines(sparse)
    repair_line = next(
        line for line in sparse_lines if line.startswith("sparse_repair=")
    )
    interval_line = next(
        line for line in sparse_lines if line.startswith("sparse_intervals=")
    )
    interval_repair_line = next(
        line for line in sparse_lines if line.startswith("sparse_interval_repair=")
    )
    repair_plan_line = next(
        line for line in sparse_lines if line.startswith("sparse_repair_plan=")
    )
    assert any(line.startswith("sparse_budget=") for line in sparse_lines)
    assert any(line.startswith("sparse_zero_residue=") for line in sparse_lines)
    assert "complete_repair_window=119" in repair_line
    assert "complete_minimal=True" in repair_line
    assert "complete_witness_lag=119" in repair_line
    assert "interval_count=6" in interval_line
    assert "first=5-6" in interval_line
    assert "largest=40-119" in interval_line
    assert "largest_is_tail=True" in interval_line
    assert "first_window=6" in interval_repair_line
    assert "first_next_gap=8" in interval_repair_line
    assert "largest_window=119" in interval_repair_line
    assert "largest_covers_context=True" in interval_repair_line
    assert "steps=6" in repair_plan_line
    assert "final_window=119" in repair_plan_line
    assert "covers_context=True" in repair_plan_line
    assert "strictly_progresses=True" in repair_plan_line
    assert sparse["proof_status"]["all_theorem_ids_proved"] is True

    assert recurrence["status"] == "proved"
    assert recurrence["request_passed"] is True
    _assert_decision_matches_receipt(
        recurrence,
        verdict="passed",
        assurance="theorem_backed",
    )
    fields = recurrence["evidence"]["fields"]
    assert fields["scheduled_work_saving"] > 0
    assert fields["periodic_shift_required_steps_invariant"] is True
    assert "fields.post_period_multi_extension_scheduled_work_saving" in recurrence[
        "proof_layers"
    ]["proved_fields"]
    assert "fields.periodic_shift_recurrence_budget_invariant" in recurrence[
        "proof_layers"
    ]["proved_fields"]
    recurrence_lines = receipt_summary_lines(recurrence)
    post_period_line = next(
        line
        for line in recurrence_lines
        if line.startswith("recurrence_post_period=")
    )
    periodic_shift_line = next(
        line
        for line in recurrence_lines
        if line.startswith("recurrence_periodic_shift=")
    )
    assert "horizon=8" in post_period_line
    assert "extra_steps=3" in post_period_line
    assert "saving=43" in post_period_line
    assert "active_work_unchanged=True" in post_period_line
    assert "base_token=7" in periodic_shift_line
    assert "shifted_token=22" in periodic_shift_line
    assert "required_steps_invariant=True" in periodic_shift_line
    assert "active_at_step_invariant=True" in periodic_shift_line
    assert recurrence["proof_status"]["all_theorem_ids_proved"] is True


def test_extended_ready_contract_receipts_preserve_family_semantics(
    contract_pack: dict,
) -> None:
    fanout = build_strided_candidate_fanout_receipt(pack=contract_pack)
    memory = build_cyclic_memory_receipt(pack=contract_pack)
    phase = build_multicoil_phase_feature_receipt(pack=contract_pack)
    mixer = build_circulant_block_cyclic_mixer_receipt(pack=contract_pack)
    seed_rule = build_seed_rule_receipt(pack=contract_pack)

    for receipt in (fanout, memory, phase, mixer, seed_rule):
        assert receipt["status"] == "proved"
        assert receipt["request_passed"] is True
        assert receipt["proof_status"]["all_theorem_ids_proved"] is True
        assert receipt["proof_layers"]["numerical_only_fields"] == []
        assert receipt["proof_layers"]["unsupported_fields"]
        _assert_decision_matches_receipt(receipt, verdict="passed")
        assert receipt["decision"]["assurance"] in {
            "theorem_backed",
            "mixed_theorem_and_computation",
        }
        assert validate_contract_receipt(receipt) == []

    assert fanout["kind"] == "strided_candidate_fanout"
    assert fanout["evidence"]["fields"]["full_coverage"] is True
    assert "fields.full_coverage" in fanout["proof_layers"]["proved_fields"]
    assert any(
        line.startswith("strided_fanout=") for line in receipt_summary_lines(fanout)
    )

    assert memory["kind"] == "cyclic_memory_residue_winding"
    assert memory["evidence"]["fields"]["residue_slot"] == 7
    assert "fields.same_residue_events" in memory["proof_layers"]["proved_fields"]
    assert any(
        line.startswith("cyclic_memory=") for line in receipt_summary_lines(memory)
    )

    assert phase["kind"] == "multicoil_phase_feature"
    assert phase["evidence"]["fields"]["joint_repeat_horizon"] == 35
    assert "fields.phase_tuple" in phase["proof_layers"]["proved_fields"]
    assert any(
        line.startswith("multicoil_phase=") for line in receipt_summary_lines(phase)
    )

    assert mixer["kind"] == "circulant_block_cyclic_mixer"
    assert mixer["evidence"]["fields"]["max_abs_dense_delta"] == 0
    assert "fields.max_abs_dense_delta" in mixer["proof_layers"]["proved_fields"]
    assert any(line.startswith("cyclic_mixer=") for line in receipt_summary_lines(mixer))

    assert seed_rule["kind"] == "seed_rule_exact_regeneration"
    assert seed_rule["evidence"]["fields"]["exact_regeneration"] is True
    assert "fields.storage_saving" in seed_rule["proof_layers"]["proved_fields"]
    assert any(line.startswith("seed_rule=") for line in receipt_summary_lines(seed_rule))


def test_dispatcher_aliases_and_fingerprint_validation(contract_pack: dict) -> None:
    receipt = build_contract_receipt(
        "sparse-attention",
        {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
        pack=contract_pack,
    )

    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["request_passed"] is True
    assert validate_contract_receipt(receipt) == []

    broken = dict(receipt)
    broken["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken)
    assert any("drifted" in failure for failure in failures)

    missing_metadata = dict(receipt)
    missing_metadata["recommendations"] = []
    missing_metadata["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(missing_metadata)
    assert any("recommendations must be a non-empty list" in failure for failure in failures)

    broken_request = dict(receipt)
    broken_request["request"] = {
        **receipt["request"],
        "parameters": {**receipt["request"]["parameters"], "context": 10},
    }
    broken_request["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken_request)
    assert any("request_content_fingerprint drifted" in failure for failure in failures)

    malformed_request = json.loads(json.dumps(receipt))
    malformed_request["request"]["paramaters"] = {}
    malformed_request["request_content_fingerprint"] = _json_fingerprint(
        malformed_request["request"]
    )
    malformed_request["receipt_content_fingerprint"] = _receipt_fingerprint(
        malformed_request
    )
    failures = validate_contract_receipt(malformed_request)
    assert any(
        "request: request contains unsupported keys: paramaters" in failure
        for failure in failures
    )

    wrong_request_kind = json.loads(json.dumps(receipt))
    wrong_request_kind["request"] = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {},
    }
    wrong_request_kind["request_content_fingerprint"] = _json_fingerprint(
        wrong_request_kind["request"]
    )
    wrong_request_kind["receipt_content_fingerprint"] = _receipt_fingerprint(
        wrong_request_kind
    )
    failures = validate_contract_receipt(wrong_request_kind)
    assert any("request.kind must match receipt kind" in failure for failure in failures)

    broken_normalized = dict(receipt)
    broken_normalized["normalized_request"] = {
        **receipt["normalized_request"],
        "sequence_length": 10,
    }
    broken_normalized["receipt_content_fingerprint"] = "0" * 64
    failures = validate_contract_receipt(broken_normalized)
    assert any(
        "normalized_request_fingerprint drifted" in failure
        for failure in failures
    )


def test_receipt_validator_requires_typed_proof_layer_buckets(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(pack=contract_pack)

    missing_bucket = json.loads(json.dumps(receipt))
    del missing_bucket["proof_layers"]["unsupported_fields"]
    missing_bucket["receipt_content_fingerprint"] = _receipt_fingerprint(
        missing_bucket
    )
    failures = validate_contract_receipt(missing_bucket)
    assert any(
        "proof_layers.unsupported_fields must be a list" in failure
        for failure in failures
    )

    bad_bucket_value = json.loads(json.dumps(receipt))
    bad_bucket_value["proof_layers"]["computed_fields"] = ["ok", ""]
    bad_bucket_value["receipt_content_fingerprint"] = _receipt_fingerprint(
        bad_bucket_value
    )
    failures = validate_contract_receipt(bad_bucket_value)
    assert any(
        "proof_layers.computed_fields must contain non-empty strings" in failure
        for failure in failures
    )

    duplicate_layer_field = json.loads(json.dumps(receipt))
    duplicate_layer_field["proof_layers"]["numerical_only_fields"].append(
        duplicate_layer_field["proof_layers"]["proved_fields"][0]
    )
    duplicate_layer_field["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_layer_field
    )
    failures = validate_contract_receipt(duplicate_layer_field)
    assert any(
        "proof layer field appears in multiple buckets" in failure
        and duplicate_layer_field["proof_layers"]["proved_fields"][0] in failure
        for failure in failures
    )

    duplicate_same_layer_field = json.loads(json.dumps(receipt))
    duplicate_same_layer_field["proof_layers"]["proved_fields"].append(
        duplicate_same_layer_field["proof_layers"]["proved_fields"][0]
    )
    duplicate_same_layer_field["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_same_layer_field
    )
    failures = validate_contract_receipt(duplicate_same_layer_field)
    assert any(
        "proof_layers.proved_fields must not contain duplicates" in failure
        for failure in failures
    )

    duplicate_theorem_id = json.loads(json.dumps(receipt))
    duplicate_theorem_id["proof_status"]["theorem_ids"].append(
        duplicate_theorem_id["proof_status"]["theorem_ids"][0]
    )
    duplicate_theorem_id["proof_status"]["theorem_count"] += 1
    duplicate_theorem_id["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_theorem_id
    )
    failures = validate_contract_receipt(duplicate_theorem_id)
    assert any(
        "proof_status.theorem_ids must not contain duplicates" in failure
        for failure in failures
    )

    wrong_theorem_count = json.loads(json.dumps(receipt))
    wrong_theorem_count["proof_status"]["theorem_count"] += 1
    wrong_theorem_count["receipt_content_fingerprint"] = _receipt_fingerprint(
        wrong_theorem_count
    )
    failures = validate_contract_receipt(wrong_theorem_count)
    assert any(
        "proof_status.theorem_count must equal len(theorem_ids)" in failure
        for failure in failures
    )

    mismatched_decision = json.loads(json.dumps(receipt))
    mismatched_decision["decision"]["claim_status"] = "impossible"
    mismatched_decision["receipt_content_fingerprint"] = _receipt_fingerprint(
        mismatched_decision
    )
    failures = validate_contract_receipt(mismatched_decision)
    assert any(
        "decision.claim_status must match receipt status" in failure
        for failure in failures
    )

    stale_decision_counts = json.loads(json.dumps(receipt))
    stale_decision_counts["decision"]["proof_layer_counts"]["proved_fields"] += 1
    stale_decision_counts["receipt_content_fingerprint"] = _receipt_fingerprint(
        stale_decision_counts
    )
    failures = validate_contract_receipt(stale_decision_counts)
    assert any(
        "decision.proof_layer_counts.proved_fields must match proof_layers"
        in failure
        for failure in failures
    )

    mismatched_recommendations = json.loads(json.dumps(receipt))
    mismatched_recommendations["recommendations"][0]["id"] = "WRONG"
    mismatched_recommendations["receipt_content_fingerprint"] = _receipt_fingerprint(
        mismatched_recommendations
    )
    failures = validate_contract_receipt(mismatched_recommendations)
    assert any(
        "recommendations must match support.planner_recommendations" in failure
        for failure in failures
    )

    mismatched_validation_commands = json.loads(json.dumps(receipt))
    mismatched_validation_commands["validation_commands"][0] = "python wrong.py"
    mismatched_validation_commands["receipt_content_fingerprint"] = (
        _receipt_fingerprint(mismatched_validation_commands)
    )
    failures = validate_contract_receipt(mismatched_validation_commands)
    assert any(
        "validation_commands must match support.validation_commands" in failure
        for failure in failures
    )

    wrong_replay_command = json.loads(json.dumps(receipt))
    wrong_replay_command["validation_commands"][0] = "python wrong.py"
    wrong_replay_command["support"]["validation_commands"][0] = "python wrong.py"
    wrong_replay_command["receipt_content_fingerprint"] = _receipt_fingerprint(
        wrong_replay_command
    )
    failures = validate_contract_receipt(wrong_replay_command)
    assert any(
        "validation_commands[0] must replay the embedded request" in failure
        for failure in failures
    )

    duplicate_validation_command = json.loads(json.dumps(receipt))
    duplicate_validation_command["validation_commands"].append(
        duplicate_validation_command["validation_commands"][0]
    )
    duplicate_validation_command["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_validation_command
    )
    failures = validate_contract_receipt(duplicate_validation_command)
    assert any(
        "validation_commands must not contain duplicates" in failure
        for failure in failures
    )

    mismatched_support_contract_id = json.loads(json.dumps(receipt))
    mismatched_support_contract_id["support"]["contract_id"] = "WRONG"
    mismatched_support_contract_id["receipt_content_fingerprint"] = (
        _receipt_fingerprint(mismatched_support_contract_id)
    )
    failures = validate_contract_receipt(mismatched_support_contract_id)
    assert any(
        "support.contract_id must match receipt contract_id" in failure
        for failure in failures
    )

    wrong_support_theorem_count = json.loads(json.dumps(receipt))
    wrong_support_theorem_count["support"]["contract_theorem_count"] += 1
    wrong_support_theorem_count["receipt_content_fingerprint"] = _receipt_fingerprint(
        wrong_support_theorem_count
    )
    failures = validate_contract_receipt(wrong_support_theorem_count)
    assert any(
        "support.contract_theorem_count must equal len(contract_theorem_ids)"
        in failure
        for failure in failures
    )

    duplicate_support_theorem_id = json.loads(json.dumps(receipt))
    duplicate_support_theorem_id["support"]["contract_theorem_ids"].append(
        duplicate_support_theorem_id["support"]["contract_theorem_ids"][0]
    )
    duplicate_support_theorem_id["support"]["contract_theorem_count"] += 1
    duplicate_support_theorem_id["receipt_content_fingerprint"] = (
        _receipt_fingerprint(duplicate_support_theorem_id)
    )
    failures = validate_contract_receipt(duplicate_support_theorem_id)
    assert any(
        "support.contract_theorem_ids must not contain duplicates" in failure
        for failure in failures
    )

    duplicate_non_claim = json.loads(json.dumps(receipt))
    duplicate_non_claim["not_claimed"].append(duplicate_non_claim["not_claimed"][0])
    duplicate_non_claim["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_non_claim
    )
    failures = validate_contract_receipt(duplicate_non_claim)
    assert any(
        "not_claimed must not contain duplicates" in failure
        for failure in failures
    )

    extra_key = json.loads(json.dumps(receipt))
    extra_key["proof_statuz"] = {}
    extra_key["receipt_content_fingerprint"] = _receipt_fingerprint(extra_key)
    failures = validate_contract_receipt(extra_key)
    assert any(
        "receipt contains unsupported keys: proof_statuz" in failure
        for failure in failures
    )

    wrong_pack_schema = json.loads(json.dumps(receipt))
    wrong_pack_schema["contract_pack_schema_id"] = "wrong"
    wrong_pack_schema["receipt_content_fingerprint"] = _receipt_fingerprint(
        wrong_pack_schema
    )
    failures = validate_contract_receipt(wrong_pack_schema)
    assert any("contract_pack_schema_id" in failure for failure in failures)


def test_receipt_pack_validator_rejects_stale_support_fingerprints(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    assert validate_contract_receipt_against_pack(receipt, contract_pack) == []

    stale = json.loads(json.dumps(receipt))
    stale["support"]["contract_pack_fingerprint"] = "0" * 64
    stale["receipt_content_fingerprint"] = _receipt_fingerprint(stale)
    failures = validate_contract_receipt_against_pack(stale, contract_pack)
    assert any(
        "support.contract_pack_fingerprint does not match loaded contract pack"
        in failure
        for failure in failures
    )


def test_receipt_file_check_report_public_api(contract_pack: dict) -> None:
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    report = build_contract_receipt_file_check_report(
        receipt,
        contract_pack,
        receipt_path="reports/rope_receipt.json",
        required_statuses=("proved",),
        require_passed=True,
    )

    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert report["ok"] is True
    assert report["receipt_count"] == 1
    assert report["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": [],
        "allowed_assurance_levels": [],
        "require_passed": True,
    }
    assert report["summaries"][0]["path"] == "reports/rope_receipt.json"
    assert report["summaries"][0]["content_fingerprint_algorithm"] == (
        receipt["content_fingerprint_algorithm"]
    )
    assert report["summaries"][0]["contract_pack_fingerprint"] == receipt["support"][
        "contract_pack_fingerprint"
    ]
    assert report["summaries"][0]["contract_content_fingerprint"] == receipt[
        "support"
    ]["contract_content_fingerprint"]
    assert report["summaries"][0]["decision_verdict"] == receipt["decision"][
        "verdict"
    ]
    assert report["summaries"][0]["decision_assurance"] == receipt["decision"][
        "assurance"
    ]
    assert report["summaries"][0]["normalized_request"] == receipt[
        "normalized_request"
    ]
    assert report["summaries"][0]["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    assert report["summaries"][0]["normalized_request_fingerprint"] == receipt[
        "normalized_request_fingerprint"
    ]
    assert report["summaries"][0]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]

    failed = build_contract_receipt_file_check_report(
        receipt,
        contract_pack,
        receipt_path="reports/rope_receipt.json",
        required_statuses=("impossible",),
        require_passed=True,
    )
    jsonschema.validate(failed, build_contract_receipt_file_check_json_schema())
    assert failed["ok"] is False
    assert failed["failure_count"] == 1
    assert "did not match required status set" in failed["failures"][0]

    decision_failed = build_contract_receipt_file_check_report(
        receipt,
        contract_pack,
        receipt_path="reports/rope_receipt.json",
        required_decision_verdicts=("failed",),
        required_assurance_levels=("theorem_backed",),
    )
    jsonschema.validate(decision_failed, build_contract_receipt_file_check_json_schema())
    assert decision_failed["ok"] is False
    assert decision_failed["failure_count"] == 2
    assert any(
        "did not match required decision set" in failure
        for failure in decision_failed["failures"]
    )
    assert any(
        "did not match required assurance set" in failure
        for failure in decision_failed["failures"]
    )


def test_receipt_replay_check_report_public_api(contract_pack: dict) -> None:
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )
    report = build_contract_receipt_replay_check_report(
        receipt,
        contract_pack,
        receipt_path="reports/rope_receipt.json",
    )

    jsonschema.validate(report, build_contract_receipt_replay_check_json_schema())
    assert report["ok"] is True
    assert report["replay_command"] == receipt["validation_commands"][0]
    assert report["replay_command_matches_request"] is True
    assert report["original"]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )
    assert report["replayed"]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )
    assert report["comparison"]["all_replay_fields_match"] is True

    stale = json.loads(json.dumps(receipt))
    stale["evidence"]["exact_common_collision_gap"] = -1
    stale["receipt_content_fingerprint"] = _receipt_fingerprint(stale)
    stale_report = build_contract_receipt_replay_check_report(
        stale,
        contract_pack,
        receipt_path="reports/stale_rope_receipt.json",
    )
    jsonschema.validate(
        stale_report,
        build_contract_receipt_replay_check_json_schema(),
    )
    assert stale_report["ok"] is False
    assert stale_report["comparison"]["receipt_content_fingerprint_matches"] is False
    assert any(
        "receipt replay mismatch: receipt_content_fingerprint" in failure
        for failure in stale_report["failures"]
    )


def test_receipt_gate_report_public_api(contract_pack: dict) -> None:
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    report = build_contract_receipt_gate_report(
        receipt,
        contract_pack,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("mixed_theorem_and_computation",),
        require_passed=True,
    )

    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert report["ok"] is True
    assert report["summaries"][0]["path"] == "<in-memory-receipt>"
    assert report["summaries"][0]["contract_pack_fingerprint"] == receipt["support"][
        "contract_pack_fingerprint"
    ]
    assert report["summaries"][0]["contract_content_fingerprint"] == receipt[
        "support"
    ]["contract_content_fingerprint"]
    assert report["summaries"][0]["normalized_request"] == receipt[
        "normalized_request"
    ]
    assert report["summaries"][0]["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    assert report["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    assert require_contract_receipt_gate(
        receipt,
        contract_pack,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("mixed_theorem_and_computation",),
        require_passed=True,
    )["ok"] is True

    with pytest.raises(ValueError, match="required decision set"):
        require_contract_receipt_gate(
            receipt,
            contract_pack,
            required_decision_verdicts=("failed",),
        )


def test_certification_bundle_public_api_accepts_valid_request(
    contract_pack: dict,
) -> None:
    request = build_contract_request(
        "rope",
        {
            "head_dim": 128,
            "base": 10000.0,
            "context": 131072,
            "requested_margin": "1/328459",
        },
    )

    bundle = build_contract_certification_bundle(
        request,
        pack=contract_pack,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("mixed_theorem_and_computation",),
        require_passed=True,
    )

    jsonschema.Draft202012Validator.check_schema(
        build_contract_certification_bundle_json_schema()
    )
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["schema_id"] == (
        "circle_calculus.ai_contract_certification_bundle.v0"
    )
    assert bundle["ok"] is True
    assert bundle["failure_count"] == 0
    assert bundle["request_validation_report"]["ok"] is True
    assert bundle["receipt"]["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert bundle["gate_report"]["ok"] is True
    assert bundle["request_content_fingerprint"] == bundle[
        "request_validation_report"
    ]["request_content_fingerprint"]
    assert bundle["receipt"]["request_content_fingerprint"]
    assert bundle["receipt_content_fingerprint"] == bundle["receipt"][
        "receipt_content_fingerprint"
    ]
    assert bundle["model_config_import_report_schema_id"] == (
        "circle_calculus.rope_model_config_import.v0"
    )
    assert bundle["model_config_import_report"] is None


def test_certification_bundle_public_api_embeds_model_config_import_report(
    contract_pack: dict,
) -> None:
    config = json.loads(STANDARD_ROPE_MODEL_CONFIG.read_text(encoding="utf-8"))
    import_report = build_rope_model_config_import_report(
        config,
        requested_margin="1/328459",
    )
    assert import_report["ok"] is True
    assert isinstance(import_report["request"], dict)

    bundle = build_contract_certification_bundle(
        import_report["request"],
        pack=contract_pack,
        model_config_import_report=import_report,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("mixed_theorem_and_computation",),
        require_passed=True,
    )

    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is True
    assert bundle["model_config_import_report"] == import_report
    assert bundle["model_config_import_report"]["request"] == (
        bundle["receipt"]["request"]
    )
    assert bundle["model_config_import_report"]["request_content_fingerprint"] == (
        bundle["request_content_fingerprint"]
    )
    assert bundle["model_config_import_report"]["parameter_sources"]["head_dim"][
        "source"
    ] == "derived_config_fields"


def test_certification_bundle_public_api_rejects_mismatched_model_config_import_report(
    contract_pack: dict,
) -> None:
    config = json.loads(STANDARD_ROPE_MODEL_CONFIG.read_text(encoding="utf-8"))
    import_report = build_rope_model_config_import_report(
        config,
        requested_margin="1/328459",
    )
    request = build_contract_request(
        "rope",
        {
            "head_dim": 128,
            "base": 10000.0,
            "context": 131072,
            "requested_margin": "1/328458",
        },
    )

    bundle = build_contract_certification_bundle(
        request,
        pack=contract_pack,
        model_config_import_report=import_report,
    )

    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is False
    assert any(
        "model config import report request_content_fingerprint" in failure
        for failure in bundle["failures"]
    )


def test_certification_bundle_public_api_reports_invalid_request(
    contract_pack: dict,
) -> None:
    request = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 32,
            "strides": [5, 0],
            "path_length": 16,
            "local_window": 9,
        },
    }

    bundle = build_contract_certification_bundle(request, pack=contract_pack)

    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is False
    assert bundle["request_validation_report"]["ok"] is False
    assert bundle["receipt"] is None
    assert bundle["gate_report"] is None
    assert bundle["normalized_request_fingerprint"] is None
    assert bundle["receipt_content_fingerprint"] is None
    assert bundle["failures"] == [
        "request validation failed: parameters.strides must contain positive integers"
    ]


def test_certification_bundle_public_api_reports_gate_failure(
    contract_pack: dict,
) -> None:
    request = build_contract_request(
        "rope",
        {
            "head_dim": 128,
            "base": 10000.0,
            "context": 131072,
            "requested_margin": "1/328458",
        },
    )

    bundle = build_contract_certification_bundle(
        request,
        pack=contract_pack,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        require_passed=True,
    )

    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is False
    assert bundle["request_validation_report"]["ok"] is True
    assert bundle["receipt"]["status"] == "impossible"
    assert bundle["gate_report"]["ok"] is False
    assert bundle["failure_count"] == 3
    assert any("receipt status" in failure for failure in bundle["failures"])
    assert any("decision verdict" in failure for failure in bundle["failures"])
    assert any(
        "request_passed was not true" in failure for failure in bundle["failures"]
    )


def test_receipt_file_check_report_rejects_invalid_api_inputs(
    contract_pack: dict,
) -> None:
    receipt = build_rope_receipt(pack=contract_pack)

    with pytest.raises(ValueError, match="receipt_path"):
        build_contract_receipt_file_check_report(
            receipt,
            contract_pack,
            receipt_path="",
        )

    with pytest.raises(ValueError, match="unsupported statuses"):
        build_contract_receipt_file_check_report(
            receipt,
            contract_pack,
            receipt_path="reports/rope_receipt.json",
            required_statuses=("green",),
        )

    with pytest.raises(ValueError, match="unsupported verdicts"):
        build_contract_receipt_file_check_report(
            receipt,
            contract_pack,
            receipt_path="reports/rope_receipt.json",
            required_decision_verdicts=("green",),
        )

    with pytest.raises(ValueError, match="unsupported assurance levels"):
        build_contract_receipt_file_check_report(
            receipt,
            contract_pack,
            receipt_path="reports/rope_receipt.json",
            required_assurance_levels=("green",),
        )


def test_request_api_validates_and_builds_receipts(contract_pack: dict) -> None:
    request = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
    }

    assert validate_contract_request(request) == []
    receipt = build_contract_receipt_from_request(request, pack=contract_pack)
    assert receipt["kind"] == "sparse_attention_coverage"
    assert receipt["request_passed"] is True
    assert validate_contract_receipt(receipt) == []


def _assert_request_replay_command(receipt: dict, expected: str) -> None:
    assert receipt["validation_commands"][0] == expected
    assert receipt["support"]["validation_commands"][0] == expected
    assert receipt["validation_commands"] == receipt["support"]["validation_commands"]
    assert validate_contract_receipt(receipt) == []


def test_receipts_include_request_specific_replay_commands(
    contract_pack: dict,
) -> None:
    rope = build_rope_receipt(
        head_dim=64,
        base=500000.0,
        context=8192,
        requested_margin="1/100000",
        pack=contract_pack,
    )
    _assert_request_replay_command(
        rope,
        "python scripts/circle_ai_certify.py rope --head-dim 64 "
        "--base 500000.0 --context 8192 --tolerance 1e-06 "
        "--discretization round --requested-margin 1/100000 --format json",
    )

    kv = build_kv_cache_receipt(
        cache_size=32,
        current=80,
        token=60,
        batch_tokens=(60, 64, 80),
        sink_size=2,
        pack=contract_pack,
    )
    _assert_request_replay_command(
        kv,
        "python scripts/circle_ai_certify.py kv-cache --cache-size 32 "
        "--current 80 --token 60 --batch-tokens 60,64,80 "
        "--sink-size 2 --format json",
    )

    sparse = build_sparse_attention_receipt(
        context=64,
        strides=(5, 9),
        path_length=2,
        local_window=3,
        pack=contract_pack,
    )
    _assert_request_replay_command(
        sparse,
        "python scripts/circle_ai_certify.py sparse-attention --context 64 "
        "--strides 5,9 --path-length 2 --local-window 3 --format json",
    )

    recurrence = build_recurrence_receipt(
        loop_period=6,
        sample_index=11,
        max_loops=9,
        token_count=10,
        selected_block_start=3,
        selected_block_width=4,
        shift_passes=5,
        pack=contract_pack,
    )
    _assert_request_replay_command(
        recurrence,
        "python scripts/circle_ai_certify.py recurrence --loop-period 6 "
        "--sample-index 11 --max-loops 9 --token-count 10 "
        "--selected-block-start 3 --selected-block-width 4 "
        "--shift-passes 5 --format json",
    )


def test_validated_receipt_api_builds_pack_checked_receipts(
    contract_pack: dict,
) -> None:
    direct_receipt = build_validated_contract_receipt(
        "sparse-attention",
        {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
        pack=contract_pack,
    )
    request = build_contract_request(
        "kv-cache",
        {
            "cache_size": 16,
            "current": 31,
            "token": 20,
            "batch_tokens": (20, 24, 29, 31),
            "sink_size": 4,
        },
    )
    request_receipt = build_validated_contract_receipt_from_request(
        request,
        pack=contract_pack,
    )

    assert direct_receipt["kind"] == "sparse_attention_coverage"
    assert request_receipt["kind"] == "kv_cache_ring_buffer"
    assert validate_contract_receipt_against_pack(direct_receipt, contract_pack) == []
    assert validate_contract_receipt_against_pack(request_receipt, contract_pack) == []


def test_validated_request_receipt_api_rejects_pack_missing_receipt_theorem() -> None:
    pack = json.loads(PUBLIC_CONTRACT_PACK.read_text())
    kv_contract = next(
        contract
        for contract in pack["contracts"]
        if contract["kind"] == "kv_cache_ring_buffer"
    )
    kv_contract["theorem_ids"] = [
        theorem_id
        for theorem_id in kv_contract["theorem_ids"]
        if theorem_id != "AIM-T0060"
    ]
    _refresh_pack_fingerprints(pack)
    request = build_contract_request(
        "kv-cache",
        {
            "cache_size": 16,
            "current": 31,
            "token": 20,
            "batch_tokens": (20, 24, 29, 31),
            "sink_size": 4,
        },
    )

    with pytest.raises(
        ValueError,
        match="receipt theorem ids are not in loaded contract: AIM-T0060",
    ):
        build_validated_contract_receipt_from_request(request, pack=pack)


def test_request_api_builds_canonical_json_safe_requests() -> None:
    request = build_contract_request(
        "sparse-attention",
        {
            "context": 9,
            "strides": (2, 5),
            "path_length": 4,
            "local_window": 8,
        },
    )

    assert request == {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse_attention_coverage",
        "parameters": {
            "context": 9,
            "strides": [2, 5],
            "path_length": 4,
            "local_window": 8,
        },
    }
    assert validate_contract_request(request) == []


def test_rope_model_config_import_builds_standard_request_parameters() -> None:
    parameters = build_rope_request_parameters_from_model_config(
        {
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "rope_theta": 500000.0,
            "max_position_embeddings": 131072,
        },
        requested_margin="1/328459",
    )

    assert parameters == {
        "head_dim": 128,
        "base": 500000.0,
        "context": 131072,
        "tolerance": 1e-6,
        "discretization": "round",
        "requested_margin": "1/328459",
    }
    assert validate_contract_request(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": parameters,
        }
    ) == []


def test_rope_model_config_public_api_builds_request_and_receipt(
    contract_pack: dict,
) -> None:
    config = {
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "rope_theta": 10000.0,
        "max_position_embeddings": 131072,
    }

    request = build_rope_contract_request_from_model_config(
        config,
        requested_margin="1/328459",
    )
    receipt = build_validated_rope_receipt_from_model_config(
        config,
        requested_margin="1/328459",
        pack=contract_pack,
    )

    assert request == {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope_position_distinguishability",
        "parameters": {
            "head_dim": 128,
            "base": 10000.0,
            "context": 131072,
            "tolerance": 1e-6,
            "discretization": "round",
            "requested_margin": "1/328459",
        },
    }
    assert validate_contract_request(request) == []
    assert receipt["kind"] == "rope_position_distinguishability"
    assert receipt["request"] == request
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    assert receipt["decision"]["verdict"] == "passed"
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    assert validate_contract_receipt_against_pack(receipt, contract_pack) == []


def test_rope_model_config_import_handles_partial_rotary_factor() -> None:
    parameters = build_rope_request_parameters_from_model_config(
        {
            "hidden_size": 1024,
            "num_attention_heads": 8,
            "max_position_embeddings": 2048,
            "partial_rotary_factor": 0.5,
        },
        base=10000.0,
        context=4096,
    )

    assert parameters["head_dim"] == 64
    assert parameters["base"] == 10000.0
    assert parameters["context"] == 4096


def test_rope_model_config_import_rejects_unproved_scaling_metadata() -> None:
    with pytest.raises(ValueError, match="rope_scaling"):
        build_rope_request_parameters_from_model_config(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 500000.0,
                "max_position_embeddings": 131072,
                "rope_scaling": {"rope_type": "llama3", "factor": 8.0},
            }
        )


def test_rope_model_config_import_report_schema_classifies_scaling() -> None:
    schema = build_rope_model_config_import_json_schema()
    standard = build_rope_model_config_import_report(
        {
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "rope_theta": 10000.0,
            "max_position_embeddings": 131072,
        },
        requested_margin="1/328459",
    )
    scaled = build_rope_model_config_import_report(
        {
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "rope_theta": 500000.0,
            "max_position_embeddings": 131072,
            "rope_scaling": {"rope_type": "llama3", "factor": 8.0},
        },
        requested_margin="1/328459",
    )

    jsonschema.validate(standard, schema)
    jsonschema.validate(scaled, schema)
    assert standard["ok"] is True
    assert standard["request"]["kind"] == "rope_position_distinguishability"
    assert standard["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(standard["model_config_fingerprint"]) == 64
    assert len(standard["request_content_fingerprint"]) == 64
    assert standard["parameter_sources"]["head_dim"] == {
        "source": "derived_config_fields",
        "fields": ["hidden_size", "num_attention_heads"],
        "note": "hidden_size / num_attention_heads, adjusted by rotary fraction when present",
    }
    assert standard["parameter_sources"]["base"] == {
        "source": "config_field",
        "field": "rope_theta",
    }
    assert standard["parameter_sources"]["context"] == {
        "source": "config_field",
        "field": "max_position_embeddings",
    }
    assert standard["parameter_sources"]["tolerance"] == {
        "source": "default",
        "note": "1e-6",
    }
    assert standard["parameter_sources"]["discretization"] == {
        "source": "default",
        "note": "round",
    }
    assert standard["parameter_sources"]["requested_margin"] == {
        "source": "override",
        "field": "requested_margin",
    }
    assert scaled["ok"] is False
    assert scaled["request"] is None
    assert len(scaled["model_config_fingerprint"]) == 64
    assert scaled["request_content_fingerprint"] is None
    assert scaled["unsupported_model_config_fields"] == ["rope_scaling"]
    assert scaled["parameter_sources"]["base"]["field"] == "rope_theta"
    assert "rope_scaling is outside" in scaled["failures"][0]


def test_rope_model_config_import_rejects_odd_head_dim() -> None:
    with pytest.raises(ValueError, match="must be even"):
        build_rope_request_parameters_from_model_config(
            {
                "hidden_size": 381,
                "num_attention_heads": 3,
                "max_position_embeddings": 2048,
            }
        )

    with pytest.raises(ValueError, match="must produce an even RoPE head_dim"):
        build_rope_request_parameters_from_model_config(
            {
                "hidden_size": 1008,
                "num_attention_heads": 8,
                "max_position_embeddings": 2048,
                "partial_rotary_factor": 0.5,
            }
        )


def test_request_api_reports_malformed_requests() -> None:
    missing_parameters = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
    }
    wrong_schema = {
        "schema_id": "wrong",
        "kind": "rope",
        "parameters": {},
    }
    unsupported = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "unknown",
        "parameters": {},
    }
    missing_kv_parameters = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "kv-cache",
        "parameters": {},
    }
    invalid_rope_margin = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {"requested_margin": "not-a-fraction"},
    }
    invalid_rope_head_dim = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {"head_dim": 127},
    }
    invalid_sparse_stride = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 32,
            "strides": [5, 0],
            "path_length": 16,
            "local_window": 9,
        },
    }
    invalid_recurrence_zero_loop_budget = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"max_loops": 0},
    }
    invalid_recurrence_empty_block = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"selected_block_width": 0},
    }
    typo_parameter = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"shift_presses": 3},
    }
    typo_top_level = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {},
        "paramaters": {},
    }

    assert "parameters must be an object" in validate_contract_request(
        missing_parameters
    )
    assert any("schema_id" in failure for failure in validate_contract_request(wrong_schema))
    assert any(
        "supported Circle AI contract kind" in failure
        for failure in validate_contract_request(unsupported)
    )
    assert any(
        "missing required keys" in failure
        for failure in validate_contract_request(missing_kv_parameters)
    )
    assert any(
        "parse as a Fraction" in failure
        for failure in validate_contract_request(invalid_rope_margin)
    )
    assert any(
        "parameters.head_dim must be even" in failure
        for failure in validate_contract_request(invalid_rope_head_dim)
    )
    assert any(
        "positive integers" in failure
        for failure in validate_contract_request(invalid_sparse_stride)
    )
    assert any(
        "parameters.max_loops must be a positive integer" in failure
        for failure in validate_contract_request(invalid_recurrence_zero_loop_budget)
    )
    assert any(
        "parameters.selected_block_width must be a positive integer" in failure
        for failure in validate_contract_request(invalid_recurrence_empty_block)
    )
    assert any(
        "unsupported keys" in failure
        for failure in validate_contract_request(typo_parameter)
    )
    assert any(
        "request contains unsupported keys: paramaters" in failure
        for failure in validate_contract_request(typo_top_level)
    )
    typo_parameter_report = build_contract_request_validation_report(typo_parameter)
    assert typo_parameter_report["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(typo_parameter_report["request_content_fingerprint"]) == 64
    assert {
        key: value
        for key, value in typo_parameter_report.items()
        if key
        not in {
            "content_fingerprint_algorithm",
            "request_content_fingerprint",
        }
    } == {
        "schema_id": "circle_calculus.ai_contract_request_validation.v0",
        "request_schema_id": "circle_calculus.ai_contract_request.v0",
        "ok": False,
        "kind": "recurrence",
        "canonical_kind": "recurrence_schedule",
        "failure_count": 1,
        "failures": ["parameters contains unsupported keys: shift_presses"],
    }
    non_string_kind_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": 12,
            "parameters": {},
        }
    )
    assert non_string_kind_report["kind"] is None
    assert non_string_kind_report["canonical_kind"] is None
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(unsupported)
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(missing_kv_parameters)
    with pytest.raises(ValueError, match="invalid Circle AI contract request"):
        build_contract_receipt_from_request(invalid_rope_margin)


def test_request_schema_accepts_public_aliases() -> None:
    schema = build_contract_request_json_schema()

    assert schema["properties"]["schema_id"]["const"] == (
        "circle_calculus.ai_contract_request.v0"
    )
    assert "rope" in schema["properties"]["kind"]["enum"]
    assert "rope_position_distinguishability" in schema["properties"]["kind"]["enum"]
    assert "strided-fanout" in schema["properties"]["kind"]["enum"]
    assert "seed-rule" in schema["properties"]["kind"]["enum"]
    assert schema["properties"]["parameters"]["type"] == "object"


def test_request_schema_validates_public_parameter_shapes() -> None:
    schema = build_contract_request_json_schema()

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": {},
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "kv-cache",
            "parameters": {
                "cache_size": 16,
                "current": 31,
                "token": 20,
                "batch_tokens": [20, 24],
                "sink_size": 4,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "sparse-attention",
            "parameters": {
                "context": 32,
                "strides": [5, 11, 17],
                "path_length": 16,
                "local_window": 9,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "recurrence",
            "parameters": {},
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "strided-fanout",
            "parameters": {
                "context_length": 12,
                "stride": 5,
                "start_index": 0,
                "path_length": 12,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "cyclic-memory",
            "parameters": {"bank_size": 8, "event_index": 23, "event_count": 32},
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "multicoil-phase",
            "parameters": {
                "periods": [5, 7],
                "position": 37,
                "query_position": 41,
                "key_position": 18,
            },
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "cyclic-mixer",
            "parameters": {"period": 8, "channel_count": 128, "block_size": 8},
        },
        schema,
    )
    jsonschema.validate(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "seed-rule",
            "parameters": {"n": 128},
        },
        schema,
    )

    missing_sparse_field = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "sparse-attention",
        "parameters": {
            "context": 32,
            "strides": [5, 11, 17],
            "path_length": 16,
        },
    }
    typo_parameter = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"shift_presses": 3},
    }
    typo_top_level = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {},
        "paramaters": {},
    }
    odd_rope_head_dim = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "rope",
        "parameters": {"head_dim": 127},
    }
    zero_recurrence_loop_budget = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"max_loops": 0},
    }
    zero_recurrence_block_width = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "recurrence",
        "parameters": {"selected_block_width": 0},
    }
    empty_phase_periods = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "multicoil-phase",
        "parameters": {"periods": []},
    }
    zero_seed_rule_n = {
        "schema_id": "circle_calculus.ai_contract_request.v0",
        "kind": "seed-rule",
        "parameters": {"n": 0},
    }

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(missing_sparse_field, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(typo_parameter, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(typo_top_level, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(odd_rope_head_dim, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(zero_recurrence_loop_budget, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(zero_recurrence_block_width, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(empty_phase_periods, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(zero_seed_rule_n, schema)


def test_receipt_schema_exposes_runner_metadata() -> None:
    schema = build_contract_receipt_json_schema()

    assert "contract_pack_schema_id" in schema["properties"]
    assert schema["additionalProperties"] is False
    assert "recommendations" in schema["required"]
    assert "validation_commands" in schema["required"]
    assert "request_content_fingerprint" in schema["required"]
    assert "normalized_request_fingerprint" in schema["required"]
    assert "decision" in schema["required"]
    assert schema["properties"]["decision"]["additionalProperties"] is False
    assert schema["properties"]["decision"]["properties"]["verdict"]["enum"] == [
        "passed",
        "failed",
        "undecided",
        "numerical_only",
        "outside_scope",
    ]
    assert schema["properties"]["proof_layers"]["required"] == list(PROOF_LAYER_BUCKETS)
    assert (
        schema["properties"]["decision"]["properties"]["proof_layer_counts"][
            "required"
        ]
        == list(PROOF_LAYER_BUCKETS)
    )
    assert schema["properties"]["recommendations"]["minItems"] == 1
    assert schema["properties"]["recommendations"]["uniqueItems"] is True
    assert schema["properties"]["validation_commands"]["minItems"] == 1
    assert schema["properties"]["validation_commands"]["uniqueItems"] is True
    assert schema["properties"]["not_claimed"]["minItems"] == 1
    assert schema["properties"]["not_claimed"]["uniqueItems"] is True
    assert (
        schema["properties"]["proof_status"]["properties"]["theorem_ids"][
            "uniqueItems"
        ]
        is True
    )
    assert (
        schema["properties"]["proof_layers"]["properties"]["proved_fields"][
            "uniqueItems"
        ]
        is True
    )


def test_compact_receipt_schema_exposes_downstream_view() -> None:
    schema = build_compact_contract_receipt_json_schema()

    jsonschema.Draft202012Validator.check_schema(schema)
    assert schema["properties"]["schema_id"]["const"] == (
        "circle_calculus.ai_contract_compact_receipt.v0"
    )
    assert schema["additionalProperties"] is False
    assert "proof_status_summary" in schema["required"]
    assert "selected_evidence" in schema["required"]
    assert "fingerprints" in schema["required"]
    assert "evidence" not in schema["properties"]
    assert schema["properties"]["decision"]["additionalProperties"] is False
    assert (
        schema["properties"]["proof_layer_counts"]["required"]
        == list(PROOF_LAYER_BUCKETS)
    )
    assert (
        schema["properties"]["fingerprints"]["properties"][
            "receipt_content_fingerprint"
        ]["pattern"]
        == "^[0-9a-f]{64}$"
    )
    assert (
        schema["properties"]["proof_status_summary"]["properties"][
            "theorem_ids"
        ]["uniqueItems"]
        is True
    )
    assert schema["properties"]["validation_commands"]["minItems"] == 1
    assert schema["properties"]["not_claimed"]["minItems"] == 1


def test_receipt_schema_rejects_missing_proof_layer_bucket(
    contract_pack: dict,
) -> None:
    schema = build_contract_receipt_json_schema()
    receipt = build_rope_receipt(pack=contract_pack)
    del receipt["proof_layers"]["unsupported_fields"]
    receipt["receipt_content_fingerprint"] = _receipt_fingerprint(receipt)

    jsonschema.Draft202012Validator.check_schema(schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(receipt, schema)


def test_receipt_schema_rejects_duplicate_theorem_and_layer_fields(
    contract_pack: dict,
) -> None:
    schema = build_contract_receipt_json_schema()
    receipt = build_rope_receipt(pack=contract_pack)

    duplicate_theorem = json.loads(json.dumps(receipt))
    duplicate_theorem["proof_status"]["theorem_ids"].append(
        duplicate_theorem["proof_status"]["theorem_ids"][0]
    )
    duplicate_theorem["proof_status"]["theorem_count"] += 1
    duplicate_theorem["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_theorem
    )

    duplicate_layer = json.loads(json.dumps(receipt))
    duplicate_layer["proof_layers"]["proved_fields"].append(
        duplicate_layer["proof_layers"]["proved_fields"][0]
    )
    duplicate_layer["receipt_content_fingerprint"] = _receipt_fingerprint(
        duplicate_layer
    )

    jsonschema.Draft202012Validator.check_schema(schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(duplicate_theorem, schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(duplicate_layer, schema)

    receipt_with_extra_key = build_rope_receipt(pack=contract_pack)
    receipt_with_extra_key["proof_statuz"] = {}
    receipt_with_extra_key["receipt_content_fingerprint"] = _receipt_fingerprint(
        receipt_with_extra_key
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(receipt_with_extra_key, schema)

    receipt_with_bad_request = build_rope_receipt(pack=contract_pack)
    receipt_with_bad_request["request"]["paramaters"] = {}
    receipt_with_bad_request["request_content_fingerprint"] = _json_fingerprint(
        receipt_with_bad_request["request"]
    )
    receipt_with_bad_request["receipt_content_fingerprint"] = _receipt_fingerprint(
        receipt_with_bad_request
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(receipt_with_bad_request, schema)


def test_request_validation_report_schema_accepts_public_reports() -> None:
    schema = build_contract_request_validation_json_schema()
    good_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "rope",
            "parameters": {},
        }
    )
    bad_report = build_contract_request_validation_report(
        {
            "schema_id": "circle_calculus.ai_contract_request.v0",
            "kind": "sparse-attention",
            "parameters": {
                "context": 32,
                "strides": [5, 0],
                "path_length": 16,
                "local_window": 9,
            },
        }
    )

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(good_report, schema)
    jsonschema.validate(bad_report, schema)
    assert good_report["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(good_report["request_content_fingerprint"]) == 64
    assert len(bad_report["request_content_fingerprint"]) == 64
    assert good_report["ok"] is True
    assert bad_report["ok"] is False


def test_runner_check_report_schema_accepts_public_report() -> None:
    schema = build_contract_runner_check_json_schema()
    report = {
        "schema_id": "circle_calculus.ai_contract_runner_check.v0",
        "ok": True,
        "example_count": 1,
        "failure_count": 0,
        "failures": [],
        "selected_kinds": [],
        "gate_policy": {
            "allowed_statuses": ["proved"],
            "allowed_decision_verdicts": ["passed"],
            "allowed_assurance_levels": ["mixed_theorem_and_computation"],
            "require_passed": True,
        },
        "summaries": [
            {
                "source_type": "request",
                "source_path": "examples/circle_ai_requests/rope_request.json",
                "source_content_fingerprint": "3" * 64,
                "request_path": "examples/circle_ai_requests/rope_request.json",
                "model_config_import_report_path": None,
                "model_config_parameter_sources": None,
                "request_validation_report_path": None,
                "certification_bundle_path": None,
                "certification_bundle_check_path": None,
                "receipt_path": None,
                "kind": "rope_position_distinguishability",
                "status": "proved",
                "request_passed": True,
                "decision_verdict": "passed",
                "decision_assurance": "mixed_theorem_and_computation",
                "theorem_count": 43,
                "recommendation_count": 2,
                "validation_command_count": 2,
                "normalized_request": {
                    "head_dim": 128,
                    "base": 10000.0,
                    "context_length": 131072,
                },
                "request_content_fingerprint": "0" * 64,
                "normalized_request_fingerprint": "1" * 64,
                "receipt_content_fingerprint": "2" * 64,
            }
        ],
    }

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)


def test_circle_ai_certify_cli_emits_json_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--head-dim",
            "128",
            "--base",
            "10000",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert payload["status"] == "proved"
    assert payload["request_passed"] is True
    assert payload["decision"]["verdict"] == "passed"
    assert payload["decision"]["claim_status"] == payload["status"]
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    public_pack = json.loads(PUBLIC_CONTRACT_PACK.read_text())
    assert payload["support"]["contract_pack_fingerprint"] == public_pack[
        "pack_content_fingerprint"
    ]
    assert payload["evidence"]["standard_channel0_d19_request_classifier"][
        "request_status"
    ] == "proved"


def test_circle_ai_certify_cli_emits_compact_json_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--head-dim",
            "128",
            "--base",
            "10000",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "compact-json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, build_compact_contract_receipt_json_schema())
    assert payload["schema_id"] == "circle_calculus.ai_contract_compact_receipt.v0"
    assert payload["receipt_schema_id"] == "circle_calculus.ai_contract_receipt.v0"
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["status"] == "proved"
    assert payload["request_passed"] is True
    assert payload["decision"]["verdict"] == "passed"
    assert payload["proof_status_summary"]["all_theorem_ids_proved"] is True
    assert "AIRA-T0238" in payload["proof_status_summary"]["theorem_ids"]
    assert "evidence" not in payload
    assert (
        payload["selected_evidence"][
            "standard_channel0_d19_request_classifier.request_status"
        ]
        == "proved"
    )
    assert "receipt_content_fingerprint" in payload["fingerprints"]


def test_circle_ai_certify_cli_imports_standard_rope_model_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    request_path = tmp_path / "circle_request.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 10000.0,
                "max_position_embeddings": 131072,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(config_path),
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
            "--request-out",
            str(request_path),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["status"] == "proved"
    assert payload["normalized_request"]["head_dim"] == 128
    assert payload["normalized_request"]["base"] == 10000.0
    assert payload["normalized_request"]["context_length"] == 131072
    assert payload["request"]["parameters"]["requested_margin"] == "1/328459"
    saved_request = json.loads(request_path.read_text())
    assert saved_request == payload["request"]
    assert validate_contract_request(saved_request) == []


def test_circle_ai_certify_cli_imports_checked_in_model_config(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "request.json"
    receipt_path = tmp_path / "receipt.json"
    import_report_path = tmp_path / "rope_model_config_import.json"
    validation_report_path = tmp_path / "request_validation.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--request-out",
            str(request_path),
            "--json-out",
            str(receipt_path),
            "--model-config-import-report-out",
            str(import_report_path),
            "--request-validation-report-out",
            str(validation_report_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    saved_request = json.loads(request_path.read_text())
    saved_receipt = json.loads(receipt_path.read_text())
    import_report = json.loads(import_report_path.read_text())
    validation_report = json.loads(validation_report_path.read_text())
    assert payload == saved_receipt
    jsonschema.validate(import_report, build_rope_model_config_import_json_schema())
    jsonschema.validate(
        validation_report,
        build_contract_request_validation_json_schema(),
    )
    assert import_report["ok"] is True
    assert import_report["request"] == saved_request
    assert validation_report["ok"] is True
    assert validation_report["canonical_kind"] == "rope_position_distinguishability"
    assert validation_report["request_content_fingerprint"] == saved_receipt[
        "request_content_fingerprint"
    ]
    assert import_report["parameter_sources"]["head_dim"]["source"] == (
        "derived_config_fields"
    )
    assert import_report["parameter_sources"]["base"] == {
        "source": "config_field",
        "field": "rope_theta",
    }
    assert import_report["parameter_sources"]["context"] == {
        "source": "config_field",
        "field": "max_position_embeddings",
    }
    assert import_report["parameter_sources"]["discretization"] == {
        "source": "default",
        "note": "round",
    }
    assert saved_request == saved_receipt["request"]
    assert saved_receipt["normalized_request"]["head_dim"] == 128
    assert saved_receipt["normalized_request"]["base"] == 10000.0
    assert saved_receipt["normalized_request"]["context_length"] == 131072


def test_circle_ai_certify_cli_writes_receipt_check_report(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    report_path = tmp_path / "receipt_check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--json-out",
            str(receipt_path),
            "--receipt-check-out",
            str(report_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    receipt = json.loads(receipt_path.read_text())
    report = json.loads(report_path.read_text())
    assert json.loads(result.stdout) == receipt
    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert report["ok"] is True
    assert report["receipt_count"] == 1
    assert report["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    assert report["summaries"][0]["path"] == str(receipt_path)
    assert report["summaries"][0]["contract_pack_fingerprint"] == receipt["support"][
        "contract_pack_fingerprint"
    ]
    assert report["summaries"][0]["contract_content_fingerprint"] == receipt[
        "support"
    ]["contract_content_fingerprint"]
    assert report["summaries"][0]["normalized_request"] == receipt[
        "normalized_request"
    ]
    assert report["summaries"][0]["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    assert report["summaries"][0]["normalized_request_fingerprint"] == receipt[
        "normalized_request_fingerprint"
    ]
    assert report["summaries"][0]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]


def test_circle_ai_certify_cli_writes_certification_bundle(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    bundle_path = tmp_path / "certification_bundle.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--json-out",
            str(receipt_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    receipt = json.loads(receipt_path.read_text())
    bundle = json.loads(bundle_path.read_text())
    assert json.loads(result.stdout) == receipt
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is True
    assert bundle["request_validation_report"]["ok"] is True
    assert bundle["receipt"] == receipt
    assert bundle["gate_report"]["ok"] is True
    assert bundle["gate_report"]["summaries"][0]["path"] == str(receipt_path)
    assert bundle["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]


def test_circle_ai_certify_cli_writes_certification_bundle_check_report(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    bundle_path = tmp_path / "certification_bundle.json"
    bundle_check_path = tmp_path / "certification_bundle_check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--json-out",
            str(receipt_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--certification-bundle-check-out",
            str(bundle_check_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    receipt = json.loads(receipt_path.read_text())
    bundle = json.loads(bundle_path.read_text())
    bundle_check = json.loads(bundle_check_path.read_text())
    assert json.loads(result.stdout) == receipt
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    jsonschema.validate(
        bundle_check,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    assert bundle_check["ok"] is True
    assert bundle_check["bundle_count"] == 1
    assert bundle_check["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    assert bundle_check["summaries"][0]["path"] == str(bundle_path)
    assert bundle_check["summaries"][0]["bundle_request_content_fingerprint"] == (
        bundle["request_content_fingerprint"]
    )
    assert bundle_check["summaries"][0]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )


def test_circle_ai_certify_cli_text_output_lists_written_artifacts(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "request.json"
    request_validation_path = tmp_path / "request_validation.json"
    receipt_path = tmp_path / "receipt.json"
    receipt_check_path = tmp_path / "receipt_check.json"
    receipt_replay_check_path = tmp_path / "receipt_replay_check.json"
    gate_report_path = tmp_path / "gate_report.json"
    bundle_path = tmp_path / "certification_bundle.json"
    bundle_check_path = tmp_path / "certification_bundle_check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--request-out",
            str(request_path),
            "--request-validation-report-out",
            str(request_validation_path),
            "--json-out",
            str(receipt_path),
            "--receipt-check-out",
            str(receipt_check_path),
            "--receipt-replay-check-out",
            str(receipt_replay_check_path),
            "--gate-report-out",
            str(gate_report_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--certification-bundle-check-out",
            str(bundle_check_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "circle_ai_contract_receipt=proved" in result.stdout
    artifact_line = next(
        line for line in result.stdout.splitlines() if line.startswith("artifacts=")
    )
    assert f"request_json={request_path}" in artifact_line
    assert f"request_validation_report={request_validation_path}" in artifact_line
    assert f"receipt_json={receipt_path}" in artifact_line
    assert f"receipt_check={receipt_check_path}" in artifact_line
    assert f"receipt_replay_check={receipt_replay_check_path}" in artifact_line
    assert f"gate_report={gate_report_path}" in artifact_line
    assert f"certification_bundle={bundle_path}" in artifact_line
    assert f"certification_bundle_check={bundle_check_path}" in artifact_line
    for path in (
        request_path,
        request_validation_path,
        receipt_path,
        receipt_check_path,
        receipt_replay_check_path,
        gate_report_path,
        bundle_path,
        bundle_check_path,
    ):
        assert path.exists()


def test_circle_ai_certify_cli_artifact_dir_writes_standard_audit_set(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    prefix = "standard_rope_config"
    model_config = json.loads(STANDARD_ROPE_MODEL_CONFIG.read_text(encoding="utf-8"))
    model_config_fingerprint = build_rope_model_config_import_report(
        model_config,
        requested_margin="1/328459",
    )["model_config_fingerprint"]
    expected_paths = {
        "request_json": artifact_dir / f"{prefix}_request.json",
        "request_validation_report": artifact_dir
        / f"{prefix}_request_validation.json",
        "model_config_import_report": artifact_dir
        / f"{prefix}_model_config_import.json",
        "receipt_json": artifact_dir / f"{prefix}_receipt.json",
        "compact_receipt_json": artifact_dir / f"{prefix}_compact_receipt.json",
        "receipt_check": artifact_dir / f"{prefix}_receipt_check.json",
        "receipt_replay_check": artifact_dir / f"{prefix}_receipt_replay_check.json",
        "gate_report": artifact_dir / f"{prefix}_gate_report.json",
        "certification_bundle": artifact_dir / f"{prefix}_certification_bundle.json",
        "certification_bundle_check": artifact_dir
        / f"{prefix}_certification_bundle_check.json",
        "artifact_manifest": artifact_dir / f"{prefix}_artifact_manifest.json",
        "artifact_manifest_check": artifact_dir
        / f"{prefix}_artifact_manifest_check.json",
    }

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--require-kind",
            "rope_position_distinguishability",
            "--require-theorem-id",
            "AIRA-T0239",
            "--require-evidence-field",
            "real_phase_dirichlet_guardrail",
            "--require-recommendation-id",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--require-model-config-fingerprint",
            model_config_fingerprint,
            "--require-normalized-param",
            "head_dim=128",
            "--require-normalized-param",
            "context_length=131072",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    artifact_line = next(
        line for line in result.stdout.splitlines() if line.startswith("artifacts=")
    )
    for label, path in expected_paths.items():
        assert path.exists()
        assert f"{label}={path}" in artifact_line

    request_validation = json.loads(
        expected_paths["request_validation_report"].read_text()
    )
    model_config_import = json.loads(
        expected_paths["model_config_import_report"].read_text()
    )
    receipt = json.loads(expected_paths["receipt_json"].read_text())
    compact_receipt = json.loads(expected_paths["compact_receipt_json"].read_text())
    receipt_check = json.loads(expected_paths["receipt_check"].read_text())
    receipt_replay_check = json.loads(
        expected_paths["receipt_replay_check"].read_text()
    )
    gate_report = json.loads(expected_paths["gate_report"].read_text())
    bundle = json.loads(expected_paths["certification_bundle"].read_text())
    bundle_check = json.loads(expected_paths["certification_bundle_check"].read_text())
    artifact_manifest = json.loads(expected_paths["artifact_manifest"].read_text())
    artifact_manifest_check = json.loads(
        expected_paths["artifact_manifest_check"].read_text()
    )

    jsonschema.validate(
        request_validation,
        build_contract_request_validation_json_schema(),
    )
    jsonschema.validate(model_config_import, build_rope_model_config_import_json_schema())
    jsonschema.validate(receipt, build_contract_receipt_json_schema())
    jsonschema.validate(compact_receipt, build_compact_contract_receipt_json_schema())
    jsonschema.validate(receipt_check, build_contract_receipt_file_check_json_schema())
    jsonschema.validate(
        receipt_replay_check,
        build_contract_receipt_replay_check_json_schema(),
    )
    jsonschema.validate(gate_report, build_contract_receipt_file_check_json_schema())
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    jsonschema.validate(
        bundle_check,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    jsonschema.validate(
        artifact_manifest,
        build_contract_artifact_manifest_json_schema(),
    )
    jsonschema.validate(
        artifact_manifest_check,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert request_validation["ok"] is True
    assert model_config_import["ok"] is True
    assert receipt["status"] == "proved"
    assert compact_receipt["fingerprints"]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )
    assert receipt_check["ok"] is True
    assert receipt_replay_check["ok"] is True
    assert receipt_replay_check["comparison"]["all_replay_fields_match"] is True
    assert gate_report["ok"] is True
    assert bundle["ok"] is True
    assert bundle_check["ok"] is True
    assert artifact_manifest_check["ok"] is True
    assert bundle["model_config_import_report"] == model_config_import
    assert artifact_manifest["kind"] == "rope_position_distinguishability"
    assert artifact_manifest["status"] == "proved"
    assert artifact_manifest["request_passed"] is True
    assert artifact_manifest["decision_verdict"] == "passed"
    assert artifact_manifest["artifact_count"] == 10
    manifest_artifacts = {
        artifact["label"]: artifact for artifact in artifact_manifest["artifacts"]
    }
    assert set(manifest_artifacts) == {
        label
        for label in expected_paths
        if label not in {"artifact_manifest", "artifact_manifest_check"}
    }
    for label, artifact in manifest_artifacts.items():
        assert artifact["exists"] is True
        assert len(artifact["sha256"]) == 64
        assert artifact["path"] == str(expected_paths[label])

    artifact_manifest_report = build_contract_artifact_manifest_file_check_report(
        artifact_manifest,
        manifest_path=expected_paths["artifact_manifest"],
    )
    jsonschema.validate(
        artifact_manifest_report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert artifact_manifest_report["ok"] is True
    assert artifact_manifest_report["manifest_count"] == 1
    assert artifact_manifest_report["summaries"][0]["artifact_count"] == 10
    assert (
        artifact_manifest_report["summaries"][0]["fingerprint_mismatch_count"]
        == 0
    )
    assert artifact_manifest_report["summaries"][0]["schema_mismatch_count"] == 0
    assert artifact_manifest_report["summaries"][0]["theorem_count"] == (
        receipt["proof_status"]["theorem_count"]
    )
    assert "AIRA-T0239" in artifact_manifest_report["summaries"][0]["theorem_ids"]
    assert (
        "real_phase_dirichlet_guardrail"
        in artifact_manifest_report["summaries"][0]["evidence_fields"]
    )
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in (
        artifact_manifest_report["summaries"][0]["recommendation_ids"]
    )
    assert artifact_manifest_report["summaries"][0]["validation_command_count"] == (
        len(receipt["validation_commands"])
    )
    assert receipt["validation_commands"][0] in (
        artifact_manifest_report["summaries"][0]["validation_commands"]
    )
    assert artifact_manifest_report["summaries"][0]["normalized_request"] == (
        receipt["normalized_request"]
    )
    assert artifact_manifest_report["summaries"][0]["model_config_fingerprint"] == (
        model_config_import["model_config_fingerprint"]
    )
    assert artifact_manifest_report["summaries"][0][
        "unsupported_model_config_fields"
    ] == []
    assert artifact_manifest_report["summaries"][0][
        "receipt_replay_check_present"
    ] is True
    assert artifact_manifest_report["summaries"][0][
        "receipt_replay_check_ok"
    ] is True
    assert artifact_manifest_report["summaries"][0][
        "receipt_replay_check_replay_command_matches_request"
    ] is True
    assert artifact_manifest_report["summaries"][0][
        "receipt_replay_check_all_replay_fields_match"
    ] is True
    assert artifact_manifest_report["summaries"][0][
        "receipt_replay_check_fingerprints_match_receipt"
    ] is True
    assert artifact_manifest_report["summaries"][0][
        "semantic_check_sidecar_count"
    ] == 3
    assert artifact_manifest_report["summaries"][0][
        "semantic_check_sidecar_labels"
    ] == [
        "receipt_check",
        "gate_report",
        "certification_bundle_check",
    ]
    assert artifact_manifest_report["summaries"][0][
        "semantic_check_sidecar_failure_count"
    ] == 0
    assert artifact_manifest_report["summaries"][0]["preflight_sidecar_count"] == 2
    assert artifact_manifest_report["summaries"][0]["preflight_sidecar_labels"] == [
        "request_validation_report",
        "model_config_import_report",
    ]
    assert (
        artifact_manifest_report["summaries"][0]["preflight_sidecar_failure_count"]
        == 0
    )

    assert artifact_manifest_check["summaries"][0]["artifact_count"] == 10
    assert artifact_manifest_check["summaries"][0]["failure_count"] == 0
    assert artifact_manifest_check["pin_policy"] == {
        "required_kinds": ["rope_position_distinguishability"],
        "required_theorem_ids": ["AIRA-T0239"],
        "required_evidence_fields": ["real_phase_dirichlet_guardrail"],
        "required_recommendation_ids": ["ROPE-USE-D19-MARGIN-FRONTIER"],
        "required_validation_commands": [],
        "required_model_config_fingerprints": [model_config_fingerprint],
        "required_normalized_params": [
            {"key": "head_dim", "value": 128},
            {"key": "context_length", "value": 131072},
        ],
    }

    manifest_check_path = artifact_dir / f"{prefix}_artifact_manifest_recheck.json"
    manifest_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--report-out",
            str(manifest_check_path),
            "--require-kind",
            "rope_position_distinguishability",
            "--require-theorem-id",
            "AIRA-T0239",
            "--require-evidence-field",
            "real_phase_dirichlet_guardrail",
            "--require-recommendation-id",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--require-validation-command",
            receipt["validation_commands"][0],
            "--require-model-config-fingerprint",
            model_config_import["model_config_fingerprint"],
            "--require-normalized-param",
            "head_dim=128",
            "--require-normalized-param",
            "context_length=131072",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "circle AI artifact manifests ok=True manifests=1 failures=0" in (
        manifest_cli.stdout
    )
    manifest_cli_report = json.loads(manifest_check_path.read_text())
    jsonschema.validate(
        manifest_cli_report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert manifest_cli_report["ok"] is True
    assert manifest_cli_report["pin_policy"] == {
        "required_kinds": ["rope_position_distinguishability"],
        "required_theorem_ids": ["AIRA-T0239"],
        "required_evidence_fields": ["real_phase_dirichlet_guardrail"],
        "required_recommendation_ids": ["ROPE-USE-D19-MARGIN-FRONTIER"],
        "required_validation_commands": [receipt["validation_commands"][0]],
        "required_model_config_fingerprints": [
            model_config_import["model_config_fingerprint"]
        ],
        "required_normalized_params": [
            {"key": "head_dim", "value": 128},
            {"key": "context_length", "value": 131072},
        ],
    }
    assert "AIRA-T0239" in manifest_cli_report["summaries"][0]["theorem_ids"]

    manifest_policy_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--pin-policy",
            str(manifest_check_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    manifest_policy_report = json.loads(manifest_policy_cli.stdout)
    assert manifest_policy_report["ok"] is True
    assert manifest_policy_report["pin_policy"] == manifest_cli_report["pin_policy"]

    replay_artifact_dir = tmp_path / "replay_artifacts"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(replay_artifact_dir),
            "--pin-policy",
            str(expected_paths["artifact_manifest_check"]),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    replay_manifest_check = json.loads(
        (
            replay_artifact_dir
            / f"{prefix}_artifact_manifest_check.json"
        ).read_text()
    )
    assert replay_manifest_check["ok"] is True
    assert replay_manifest_check["pin_policy"] == artifact_manifest_check[
        "pin_policy"
    ]

    missing_pin_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--require-theorem-id",
            "NONEXISTENT-T0000",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert missing_pin_cli.returncode == 1
    assert "required receipt theorem id is missing" in missing_pin_cli.stderr

    missing_command_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--require-validation-command",
            "python nonexistent_validation.py",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert missing_command_cli.returncode == 1
    assert "required receipt validation command is missing" in (
        missing_command_cli.stderr
    )

    missing_model_config_fingerprint_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--require-model-config-fingerprint",
            "0" * 64,
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert missing_model_config_fingerprint_cli.returncode == 1
    assert "required model config fingerprint is missing" in (
        missing_model_config_fingerprint_cli.stderr
    )

    missing_normalized_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
            "--require-normalized-param",
            "head_dim=256",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert missing_normalized_cli.returncode == 1
    assert "required normalized request parameter is missing" in (
        missing_normalized_cli.stderr
    )

    expected_paths["request_json"].write_text(
        expected_paths["request_json"].read_text() + "\n",
        encoding="utf-8",
    )
    stale_cli = subprocess.run(
        [
            sys.executable,
            str(ARTIFACT_MANIFEST_CHECK_SCRIPT),
            str(expected_paths["artifact_manifest"]),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert stale_cli.returncode == 1
    assert "sha256 mismatch" in stale_cli.stderr


def test_artifact_manifest_check_rejects_stale_receipt_replay_sidecar(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    prefix = "standard_rope_config"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    manifest_path = artifact_dir / f"{prefix}_artifact_manifest.json"
    replay_path = artifact_dir / f"{prefix}_receipt_replay_check.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    replay_check = json.loads(replay_path.read_text(encoding="utf-8"))
    replay_check["original"]["receipt_content_fingerprint"] = "0" * 64
    replay_path.write_text(
        json.dumps(replay_check, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "receipt_replay_check":
            artifact["sha256"] = hashlib.sha256(replay_path.read_bytes()).hexdigest()

    report = build_contract_artifact_manifest_file_check_report(
        manifest,
        manifest_path=manifest_path,
    )
    jsonschema.validate(
        report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert report["ok"] is False
    assert report["summaries"][0]["receipt_replay_check_present"] is True
    assert report["summaries"][0]["receipt_replay_check_ok"] is True
    assert report["summaries"][0][
        "receipt_replay_check_fingerprints_match_receipt"
    ] is False
    assert "receipt_replay_check original receipt_content_fingerprint" in "\n".join(
        report["failures"]
    )


def test_artifact_manifest_check_rejects_stale_receipt_check_sidecar(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    prefix = "standard_rope_config"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    manifest_path = artifact_dir / f"{prefix}_artifact_manifest.json"
    receipt_check_path = artifact_dir / f"{prefix}_receipt_check.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt_check = json.loads(receipt_check_path.read_text(encoding="utf-8"))
    receipt_check["summaries"][0]["receipt_content_fingerprint"] = "0" * 64
    receipt_check_path.write_text(
        json.dumps(receipt_check, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "receipt_check":
            artifact["sha256"] = hashlib.sha256(
                receipt_check_path.read_bytes()
            ).hexdigest()

    report = build_contract_artifact_manifest_file_check_report(
        manifest,
        manifest_path=manifest_path,
    )
    jsonschema.validate(
        report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert report["ok"] is False
    assert report["summaries"][0]["semantic_check_sidecar_count"] == 3
    assert report["summaries"][0]["semantic_check_sidecar_failure_count"] == 1
    assert "receipt_check receipt_content_fingerprint" in "\n".join(
        report["failures"]
    )


def test_artifact_manifest_check_rejects_stale_request_validation_sidecar(
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifacts"
    prefix = "standard_rope_config"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--artifact-dir",
            str(artifact_dir),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    manifest_path = artifact_dir / f"{prefix}_artifact_manifest.json"
    request_validation_path = artifact_dir / f"{prefix}_request_validation.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    request_validation = json.loads(
        request_validation_path.read_text(encoding="utf-8")
    )
    request_validation["request_content_fingerprint"] = "0" * 64
    request_validation_path.write_text(
        json.dumps(request_validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for artifact in manifest["artifacts"]:
        if artifact["label"] == "request_validation_report":
            artifact["sha256"] = hashlib.sha256(
                request_validation_path.read_bytes()
            ).hexdigest()

    report = build_contract_artifact_manifest_file_check_report(
        manifest,
        manifest_path=manifest_path,
    )
    jsonschema.validate(
        report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    assert report["ok"] is False
    assert report["summaries"][0]["preflight_sidecar_count"] == 2
    assert report["summaries"][0]["preflight_sidecar_failure_count"] == 1
    assert "request_validation_report request_content_fingerprint" in "\n".join(
        report["failures"]
    )


def test_circle_ai_certify_cli_writes_model_config_certification_bundle(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "receipt.json"
    bundle_path = tmp_path / "certification_bundle.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(STANDARD_ROPE_MODEL_CONFIG),
            "--requested-margin",
            "1/328459",
            "--json-out",
            str(receipt_path),
            "--certification-bundle-out",
            str(bundle_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    receipt = json.loads(receipt_path.read_text())
    bundle = json.loads(bundle_path.read_text())
    assert json.loads(result.stdout) == receipt
    jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
    assert bundle["ok"] is True
    assert bundle["receipt"] == receipt
    assert bundle["model_config_import_report"]["ok"] is True
    assert bundle["model_config_import_report"]["request"] == receipt["request"]
    assert bundle["model_config_import_report"]["request_content_fingerprint"] == (
        bundle["request_content_fingerprint"]
    )
    assert bundle["model_config_import_report"]["parameter_sources"]["head_dim"][
        "source"
    ] == "derived_config_fields"


@pytest.mark.parametrize(
    ("subcommand_args", "expected_kind"),
    [
        (
            [
                "kv-cache",
                "--cache-size",
                "16",
                "--current",
                "31",
                "--token",
                "31",
                "--batch-tokens",
                "20,24,29,31",
                "--sink-size",
                "4",
            ],
            "kv_cache_ring_buffer",
        ),
        (
            [
                "sparse-attention",
                "--context",
                "32",
                "--strides",
                "5,11,17",
                "--path-length",
                "16",
                "--local-window",
                "9",
            ],
            "sparse_attention_coverage",
        ),
        (
            ["recurrence"],
            "recurrence_schedule",
        ),
        (
            ["strided-fanout"],
            "strided_candidate_fanout",
        ),
        (
            ["cyclic-memory"],
            "cyclic_memory_residue_winding",
        ),
        (
            ["multicoil-phase"],
            "multicoil_phase_feature",
        ),
        (
            ["cyclic-mixer"],
            "circulant_block_cyclic_mixer",
        ),
        (
            ["seed-rule"],
            "seed_rule_exact_regeneration",
        ),
    ],
)
def test_circle_ai_certify_cli_writes_receipt_checks_for_non_rope_families(
    tmp_path: Path,
    subcommand_args: list[str],
    expected_kind: str,
) -> None:
    receipt_path = tmp_path / f"{expected_kind}.receipt.json"
    report_path = tmp_path / f"{expected_kind}.check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            *subcommand_args,
            "--json-out",
            str(receipt_path),
            "--receipt-check-out",
            str(report_path),
            "--require-status",
            "proved",
            "--require-passed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    receipt = json.loads(receipt_path.read_text())
    report = json.loads(report_path.read_text())
    assert json.loads(result.stdout) == receipt
    assert receipt["kind"] == expected_kind
    assert receipt["status"] == "proved"
    assert receipt["request_passed"] is True
    assert receipt["proof_status"]["all_theorem_ids_proved"] is True
    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert report["ok"] is True
    assert report["summaries"][0]["kind"] == expected_kind
    assert report["summaries"][0]["contract_pack_fingerprint"] == receipt["support"][
        "contract_pack_fingerprint"
    ]
    assert report["summaries"][0]["contract_content_fingerprint"] == receipt[
        "support"
    ]["contract_content_fingerprint"]
    assert report["summaries"][0]["normalized_request"] == receipt[
        "normalized_request"
    ]
    assert report["summaries"][0]["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    assert report["summaries"][0]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]


def test_circle_ai_certify_cli_receipt_check_requires_saved_receipt(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "receipt_check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--receipt-check-out",
            str(report_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "--receipt-check-out requires --json-out" in result.stderr
    assert not report_path.exists()


def test_circle_ai_certify_cli_bundle_check_requires_saved_bundle(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "certification_bundle_check.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--certification-bundle-check-out",
            str(report_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert (
        "--certification-bundle-check-out requires --certification-bundle-out"
        in result.stderr
    )
    assert not report_path.exists()


def test_circle_ai_certify_cli_writes_in_memory_gate_report(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "gate_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--gate-report-out",
            str(report_path),
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    report = json.loads(report_path.read_text())
    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert "circle_ai_contract_receipt=proved" in result.stdout
    assert report["ok"] is True
    assert report["receipt_count"] == 1
    assert report["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    assert report["summaries"][0]["path"] == "<in-memory-receipt>"
    assert report["summaries"][0]["kind"] == "rope_position_distinguishability"
    assert report["summaries"][0]["decision_verdict"] == "passed"
    assert report["summaries"][0]["decision_assurance"] == (
        "mixed_theorem_and_computation"
    )


def test_circle_ai_certify_cli_rejects_scaled_rope_model_config(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    report_path = tmp_path / "rope_model_config_import.json"
    config_path.write_text(
        json.dumps(
            {
                "hidden_size": 4096,
                "num_attention_heads": 32,
                "rope_theta": 500000.0,
                "max_position_embeddings": 131072,
                "rope_scaling": {"rope_type": "llama3", "factor": 8.0},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--model-config",
            str(config_path),
            "--model-config-import-report-out",
            str(report_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "rope_scaling is outside" in result.stderr
    report = json.loads(report_path.read_text())
    jsonschema.validate(report, build_rope_model_config_import_json_schema())
    assert report["ok"] is False
    assert report["request"] is None
    assert len(report["model_config_fingerprint"]) == 64
    assert report["request_content_fingerprint"] is None
    assert report["unsupported_model_config_fields"] == ["rope_scaling"]


def test_circle_ai_certify_cli_accepts_request_json(tmp_path: Path) -> None:
    request_path = tmp_path / "rope_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "rope_position_distinguishability",
                "parameters": {
                    "head_dim": 128,
                    "base": 10000.0,
                    "context": 1000,
                    "requested_margin": "1/999",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "request",
            "--request-json",
            str(request_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["kind"] == "rope_position_distinguishability"
    assert payload["status"] == "impossible"
    assert payload["request_passed"] is False
    guardrail = payload["evidence"]["real_phase_dirichlet_guardrail"]
    assert guardrail["requested_margin_relation_to_ceiling"] == (
        "above_dirichlet_ceiling"
    )


def test_circle_ai_certify_cli_receipt_gate_accepts_passing_receipt() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["status"] == "proved"
    assert payload["request_passed"] is True
    assert payload["decision"]["verdict"] == "passed"
    assert result.stderr == ""


def test_circle_ai_certify_cli_rejects_pack_missing_receipt_theorem(
    tmp_path: Path,
) -> None:
    pack = json.loads(PUBLIC_CONTRACT_PACK.read_text())
    kv_contract = next(
        contract
        for contract in pack["contracts"]
        if contract["kind"] == "kv_cache_ring_buffer"
    )
    theorem_ids = kv_contract["theorem_ids"]
    assert "AIM-T0060" in theorem_ids
    kv_contract["theorem_ids"] = [
        theorem_id for theorem_id in theorem_ids if theorem_id != "AIM-T0060"
    ]
    _refresh_pack_fingerprints(pack)
    stale_pack_path = tmp_path / "kv_missing_theorem_pack.json"
    stale_pack_path.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "kv-cache",
            "--cache-size",
            "16",
            "--current",
            "31",
            "--token",
            "20",
            "--batch-tokens",
            "20,24,29,31",
            "--sink-size",
            "4",
            "--pack",
            str(stale_pack_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert "invalid Circle AI contract receipt for loaded pack" in result.stderr
    assert "receipt theorem ids are not in loaded contract: AIM-T0060" in result.stderr


def test_circle_ai_certify_cli_rejects_receipt_schema_drift(
    tmp_path: Path,
) -> None:
    schema_path = tmp_path / "bad_receipt_schema.json"
    schema = build_contract_receipt_json_schema()
    schema["properties"]["schema_id"]["const"] = "wrong"
    schema_path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--receipt-schema",
            str(schema_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "schema_id" in result.stderr


def test_circle_ai_certify_cli_receipt_gate_rejects_failed_request(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "failed_gate_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "1000",
            "--requested-margin",
            "1/999",
            "--format",
            "json",
            "--gate-report-out",
            str(report_path),
            "--require-status",
            "impossible",
            "--require-passed",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    report = json.loads(report_path.read_text())
    assert result.returncode == 1
    assert payload["status"] == "impossible"
    assert payload["request_passed"] is False
    jsonschema.validate(report, build_contract_receipt_file_check_json_schema())
    assert report["ok"] is False
    assert report["failure_count"] == 1
    assert report["summaries"][0]["status"] == "impossible"
    assert report["summaries"][0]["request_passed"] is False
    assert "receipt_gate_failure=" in result.stderr
    assert "request_passed was not true" in result.stderr


def test_circle_ai_certify_cli_rejects_mismatched_decision_gate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "rope",
            "--context",
            "131072",
            "--requested-margin",
            "1/328459",
            "--format",
            "json",
            "--require-decision",
            "failed",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["decision"]["verdict"] == "passed"
    assert "did not match required decision set" in result.stderr


def test_circle_ai_certify_cli_validates_request_without_receipt(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "sparse_request.json"
    report_path = tmp_path / "request_validation_report.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 11, 17],
                    "path_length": 16,
                    "local_window": 9,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "request",
            "--request-json",
            str(request_path),
            "--validate-only",
            "--format",
            "json",
            "--json-out",
            str(report_path),
            "--pack",
            str(tmp_path / "missing_contract_pack.json"),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert json.loads(report_path.read_text()) == payload
    assert payload["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(payload["request_content_fingerprint"]) == 64
    assert {
        key: value
        for key, value in payload.items()
        if key
        not in {
            "content_fingerprint_algorithm",
            "request_content_fingerprint",
        }
    } == {
        "schema_id": "circle_calculus.ai_contract_request_validation.v0",
        "request_schema_id": "circle_calculus.ai_contract_request.v0",
        "ok": True,
        "kind": "sparse-attention",
        "canonical_kind": "sparse_attention_coverage",
        "failure_count": 0,
        "failures": [],
    }


def test_circle_ai_certify_cli_validate_only_rejects_receipt_gate_options(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "sparse_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 11, 17],
                    "path_length": 16,
                    "local_window": 9,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "request",
            "--request-json",
            str(request_path),
            "--validate-only",
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "theorem_backed",
            "--gate-report-out",
            str(tmp_path / "gate_report.json"),
            "--certification-bundle-out",
            str(tmp_path / "certification_bundle.json"),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "require a receipt" in result.stderr


def test_circle_ai_certify_cli_validate_only_rejects_bad_request(
    tmp_path: Path,
) -> None:
    request_path = tmp_path / "bad_sparse_request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.ai_contract_request.v0",
                "kind": "sparse-attention",
                "parameters": {
                    "context": 32,
                    "strides": [5, 0],
                    "path_length": 16,
                    "local_window": 9,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "request",
            "--request-json",
            str(request_path),
            "--validate-only",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["canonical_kind"] == "sparse_attention_coverage"
    assert any("positive integers" in failure for failure in payload["failures"])
