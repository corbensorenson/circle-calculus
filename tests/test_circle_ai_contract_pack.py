from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml

from circle_math.applications.circle_ai_contracts import (
    build_acceptance_policy_report_json_schema,
    build_acceptance_policy_json_schema,
    build_acceptance_receipt_json_schema,
    build_contract_pack,
    build_contract_pack_json_schema,
    build_downstream_rejection_report_json_schema,
)
from circle_math.applications.circle_ai_contract_runner import (
    build_contract_artifact_manifest_file_check_json_schema,
    build_contract_artifact_manifest_json_schema,
    build_contract_certification_bundle_json_schema,
    build_compact_contract_receipt_json_schema,
    build_contract_receipt_file_check_json_schema,
    build_contract_runner_check_json_schema,
)
from circle_math.applications.circle_ai_contract_consumer import (
    contract_acceptance_policy_report,
)
from scripts.check_circle_ai_contract_pack import EXPECTED_LIVING_BOOK_PAGE_BY_KIND


ROOT = Path(__file__).resolve().parents[1]

SPARSE_STRICT_RECEIPT_COMMAND = (
    "python scripts/circle_ai_contract_ready.py --kind "
    "sparse_attention_coverage --receipt --format json "
    "--field first_uncovered_lag "
    "--field first_uncovered_interval_start "
    "--field complete_repair_window "
    "--field complete_repair_window_covers_context "
    "--field complete_repair_window_minimal_for_declared_stride_family "
    "--field complete_repair_window_minimal_witness_lag "
    "--require-theorem AIT-T0104 --require-theorem AIT-T0172 "
    "--require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
    "--require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK "
    "--require-recommendation-evidence-field "
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start "
    "--require-recommendation-evidence-field "
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
    "local_window_complete_threshold_is_exact_local_minimum "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
    "complete_repair_window_minimal_for_declared_stride_family "
    "--require-recommendation-evidence-field "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag "
    "--require-recommendation-theorem "
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169 "
    "--require-recommendation-theorem "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170 "
    "--require-recommendation-action-parameter "
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
    "--require-recommendation-action-parameter "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
    "--require-recommendation-action-parameter "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots "
    "--require-recommendation-action-parameter-path "
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
    "--require-recommendation-action-parameter-path "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
    "--require-recommendation-action-parameter-path "
    "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots"
)


def _walk_ids(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        identifier = value.get("id")
        if isinstance(identifier, str):
            found.add(identifier)
        for child in value.values():
            found.update(_walk_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_walk_ids(child))
    return found


def _manifest_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted((ROOT / "manifests").glob("**/*.yaml")):
        ids.update(_walk_ids(yaml.safe_load(path.read_text()) or {}))
    return ids


def _dictionary_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted((ROOT / "dictionary").glob("**/*.yaml")):
        ids.update(_walk_ids(yaml.safe_load(path.read_text()) or {}))
    return ids


def test_generic_contract_pack_is_standalone_with_compatibility_aliases() -> None:
    pack = build_contract_pack()
    assert pack["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert "model quality" in pack["claim_boundary"]
    assert "theseus_hive" in pack["downstream_compatibility"]
    assert "contract_schema" in pack
    assert "required_contract_keys" in pack["contract_schema"]
    assert "minimum_fields_by_kind" in pack["contract_schema"]
    assert "minimum_field_catalog_by_kind" in pack["contract_schema"]
    assert "consumer_check_keys" in pack["contract_schema"]
    assert "planner_recommendation_keys" in pack["contract_schema"]
    assert "contract_readiness_index" in pack
    assert "planner_recommendation_index" in pack
    assert "contract_fingerprint_index" in pack
    assert pack["acceptance_policy"]["schema_id"] == (
        "circle_calculus.ai_contract_acceptance_policy.v0"
    )
    assert pack["acceptance_policy"]["report_schema_id"] == (
        "circle_calculus.ai_contract_acceptance_policy_report.v0"
    )
    assert pack["acceptance_policy"]["receipt_schema_id"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    assert pack["acceptance_policy"]["rejection_report_schema_id"] == (
        "circle_calculus.downstream_ci_rejection_report.v0"
    )
    assert pack["acceptance_policy"]["policy_schema_path"] == (
        "site/data/generated/circle_ai_contract_acceptance_policy.schema.json"
    )
    assert pack["acceptance_policy"]["report_schema_path"] == (
        "site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json"
    )
    assert pack["acceptance_policy"]["receipt_schema_path"] == (
        "site/data/generated/circle_ai_contract_acceptance_receipt.schema.json"
    )
    assert pack["acceptance_policy"]["rejection_report_schema_path"] == (
        "site/data/generated/circle_ai_downstream_rejection_report.schema.json"
    )
    assert pack["acceptance_policy"]["default_policy_path"] == (
        "examples/circle_ai_contract_acceptance_policy.json"
    )
    assert pack["acceptance_policy"]["checker"] == (
        "scripts/check_circle_ai_contract_acceptance_policy.py"
    )
    assert pack["acceptance_policy"]["standalone_checker"] == (
        "examples/downstream_ci_accept_circle_ai_contracts.py"
    )
    assert pack["acceptance_policy"]["standalone_schema_checker"] == (
        "scripts/check_downstream_ci_acceptance_example.py"
    )
    assert "required_theorem_ids" in pack["acceptance_policy"][
        "pinned_requirement_keys"
    ]
    assert "required_recommendation_theorem_ids" in pack["acceptance_policy"][
        "pinned_requirement_keys"
    ]
    assert "required_recommendation_action_parameters" in pack["acceptance_policy"][
        "pinned_requirement_keys"
    ]
    assert "required_recommendation_action_parameter_paths" in pack[
        "acceptance_policy"
    ]["pinned_requirement_keys"]
    assert "preserve" in pack["acceptance_policy"]["rule"].lower()
    assert pack["content_fingerprint_algorithm"] == "sha256-json-v1"
    assert len(pack["pack_content_fingerprint"]) == 64
    assert set(pack["pack_content_fingerprint"]) <= set("0123456789abcdef")
    assert pack["proof_indexes"]["theorem_index"] == "site/data/generated/theorem_manifest.json"
    assert pack["proof_indexes"]["dictionary_index"] == "site/data/generated/dictionary.json"
    assert "python scripts/check_circle_ai_contract_pack.py" in pack["validation_commands"]
    assert (
        "python scripts/check_circle_ai_contract_acceptance_policy.py"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/check_circle_ai_contract_acceptance_policy.py --format json"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/check_downstream_ci_acceptance_example.py --summary"
        in pack["validation_commands"]
    )
    assert (
        "python examples/downstream_ci_accept_circle_ai_contracts.py --format json"
        in pack["validation_commands"]
    )
    assert (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values"
        in pack["validation_commands"]
    )
    assert (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "ROPE-USE-D19-MARGIN-FRONTIER --include-values"
        in pack["validation_commands"]
    )
    assert (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values"
        in pack["acceptance_policy"]["validation_commands"]
    )
    assert (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "ROPE-USE-D19-MARGIN-FRONTIER --include-values"
        in pack["acceptance_policy"]["validation_commands"]
    )
    assert (
        "python scripts/check_downstream_ci_acceptance_example.py --summary"
        in pack["acceptance_policy"]["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --action-plan "
        "--recommendation ROPE-USE-D19-MARGIN-FRONTIER --include-values --format json"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/example_consume_circle_ai_contract_pack.py "
        "--planner --planner-kind rope_position_distinguishability "
        "--planner-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
        "--planner-include-values"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --acceptance-policy"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --acceptance-policy --format json"
        in pack["validation_commands"]
    )
    assert set(pack["acceptance_policy"]["validation_commands"]) <= set(
        pack["validation_commands"]
    )
    assert pack["acceptance_policy"]["fingerprint_refresh_command"] == (
        "python scripts/circle_ai_contract_ready.py --print-refreshed-policy"
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --list-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --fingerprints"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --action-plan"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration "
        "--action-plan --include-values --format json"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability "
        "--digest --format json --field d19_proved_request_status "
        "--field d19_impossible_request_status "
        "--field d19_undecided_request_status "
        "--field d19_proved_first_channel_bank_transfer "
        "--field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope "
        "--field d19_proved_first_channel_context_wide_contract "
        "--field d19_proved_first_channel_radian_bank_form "
        "--field d19_proved_first_channel_bank_tolerance_rule "
        "--field d19_undecided_probe_margin_in_open_gap "
        "--field real_phase_dirichlet_witness_guardrail "
        "--field real_phase_margin_ceiling_guardrail "
        "--field real_phase_exact_weakest_margin_ceiling_guardrail "
        "--include-field-metadata --include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "rope_position_distinguishability --receipt --format json "
        "--field d19_proved_request_status "
        "--field d19_impossible_request_status "
        "--field d19_undecided_request_status "
        "--field d19_proved_first_channel_bank_transfer "
        "--field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope "
        "--field d19_proved_first_channel_context_wide_contract "
        "--field d19_proved_first_channel_radian_bank_form "
        "--field d19_proved_first_channel_bank_tolerance_rule "
        "--field d19_undecided_probe_margin_in_open_gap "
        "--field real_phase_dirichlet_witness_guardrail "
        "--field real_phase_margin_ceiling_guardrail "
        "--field real_phase_exact_weakest_margin_ceiling_guardrail "
        "--require-theorem AIRA-T0171 --require-theorem AIRA-T0172 "
        "--require-theorem AIRA-T0234 --require-theorem AIRA-T0235 "
        "--require-theorem AIRA-T0236 --require-theorem AIRA-T0237 "
        "--require-theorem AIRA-T0238 --require-theorem AIRA-T0239 "
        "--require-theorem AIRA-T0240 --require-theorem AIRA-T0241 "
        "--require-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_bank_transfer "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "d19_proved_first_channel_context_wide_contract "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_radian_bank_form "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_undecided_probe_margin_in_open_gap "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=real_phase_dirichlet_witness_guardrail "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=real_phase_margin_ceiling_guardrail "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "real_phase_exact_weakest_margin_ceiling_guardrail "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0238 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0239 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0240 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0241 "
        "--require-recommendation-action-parameter "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.context_wide_contract "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.radian_bank_form "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer "
        "--digest --field stale_probe_first_stale_token --include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "kv_cache_ring_buffer --receipt --format json "
        "--field stale_probe_first_stale_token "
        "--field sink_tokens_retained_by_policy "
        "--field sink_window_exact_policy "
        "--field sink_window_tokens_distinct "
        "--field sink_prefix_disjoint_from_live_window "
        "--field sink_tokens_outside_ordinary_rolling_window "
        "--require-theorem AIM-T0103 --require-theorem AIM-T0104 "
        "--require-theorem AIM-T0149 "
        "--require-recommendation KV-DROP-STALE-REQUEST-TOKEN "
        "--require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST "
        "--require-recommendation-evidence-field "
        "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_retained_by_policy "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
        "sink_tokens_outside_ordinary_rolling_window "
        "--require-recommendation-theorem "
        "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103 "
        "--require-recommendation-theorem "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149 "
        "--require-recommendation-action-parameter "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage "
        "--digest --field first_uncovered_lag --include-recommendations"
        in pack["validation_commands"]
    )
    assert SPARSE_STRICT_RECEIPT_COMMAND in pack["validation_commands"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind recurrence_schedule "
        "--digest --field scheduled_work_saving "
        "--field post_period_multi_extension_scheduled_work_saving "
        "--include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "recurrence_schedule --receipt --format json "
        "--field periodic_shift_required_steps_invariant "
        "--field periodic_shift_active_at_step_invariant "
        "--field total_active_token_work "
        "--field scheduled_work_saving "
        "--field scheduled_work_saving_accounting "
        "--field active_inactive_work_accounting "
        "--field scheduled_work_saving_positive "
        "--field post_period_multi_extension_scheduled_work_saving "
        "--require-theorem AIM-T0026 --require-theorem AIM-T0130 "
        "--require-theorem AIM-T0159 "
        "--require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE "
        "--require-recommendation RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=total_active_token_work "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_required_steps_invariant "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_active_at_step_invariant "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 "
        "--require-recommendation-theorem "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-action-parameter "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding "
        "--digest --field max_alias_load --include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout "
        "--digest --field full_coverage --field effective_candidate_budget "
        "--field duplicate_count --include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature "
        "--digest --field joint_repeat_horizon --field relative_phase "
        "--include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer "
        "--digest --field max_abs_dense_delta --field block_to_dense_ratio "
        "--include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration "
        "--digest --field storage_saving --include-recommendations"
        in pack["validation_commands"]
    )
    assert (
        "python -m pytest tests/test_circle_ai_contract_consumer.py -q"
        in pack["validation_commands"]
    )
    assert "make circle-ai-contracts-ready" in pack["validation_commands"]

    contracts = {contract["kind"]: contract for contract in pack["contracts"]}
    assert {
        "rope_position_distinguishability",
        "kv_cache_ring_buffer",
        "sparse_attention_coverage",
        "recurrence_schedule",
        "strided_candidate_fanout",
        "cyclic_memory_residue_winding",
        "multicoil_phase_feature",
        "circulant_block_cyclic_mixer",
        "seed_rule_exact_regeneration",
    } <= set(contracts)
    assert set(pack["contract_readiness_index"]) == set(contracts)
    assert set(pack["contract_fingerprint_index"]) == set(contracts)

    for contract in contracts.values():
        for key in pack["contract_schema"]["required_contract_keys"]:
            assert key in contract
        assert contract["content_fingerprint_algorithm"] == "sha256-json-v1"
        assert len(contract["content_fingerprint"]) == 64
        assert set(contract["content_fingerprint"]) <= set("0123456789abcdef")
        fingerprint_entry = pack["contract_fingerprint_index"][contract["kind"]]
        assert fingerprint_entry == {
            "id": contract["id"],
            "content_fingerprint_algorithm": "sha256-json-v1",
            "content_fingerprint": contract["content_fingerprint"],
        }
        assert contract["id"].startswith("CC-AI-CONTRACT-")
        assert contract["status"] == "fixture"
        assert contract["contract_passed"] is True
        assert contract["integration_use"]
        assert isinstance(contract["compatibility_ids"], list)
        if contract.get("downstream_compatibility"):
            assert contract["compatibility_ids"][0].startswith("TH-AI-CONTRACT-")
        assert "theseus_hive_use" not in contract
        assert "not" in contract["not_claimed"].lower()
        assert contract["theorem_ids"]
        assert contract["dictionary_ids"]
        assert contract["quickstart_docs"]
        assert contract["living_book_pages"]
        assert contract["entrypoints"]
        assert contract["validation_commands"]
        proof_status = contract["proof_status"]
        assert proof_status["theorem_count"] == len(contract["theorem_ids"])
        assert proof_status["all_theorem_ids_resolved"] is True
        assert proof_status["all_theorem_ids_proved"] is True
        assert proof_status["unresolved_theorem_ids"] == []
        assert proof_status["unproved_theorem_ids"] == []
        assert {record["id"] for record in proof_status["theorems"]} == set(
            contract["theorem_ids"]
        )
        assert all(record["resolved"] is True for record in proof_status["theorems"])
        assert all(record["proved"] is True for record in proof_status["theorems"])
        assert all(record["lean_name"] for record in proof_status["theorems"])
        consumer_check = contract["consumer_check"]
        assert consumer_check["missing_minimum_fields"] == []
        assert consumer_check["required_fields_present"] is True
        assert consumer_check["all_theorem_ids_resolved"] is True
        assert consumer_check["all_theorem_ids_proved"] is True
        assert consumer_check["unresolved_theorem_ids"] == []
        assert consumer_check["unproved_theorem_ids"] == []
        assert consumer_check["ready_for_downstream_fixture_use"] is True
        assert consumer_check["minimum_fields"] == pack["contract_schema"][
            "minimum_fields_by_kind"
        ][contract["kind"]]
        assert set(consumer_check["minimum_fields"]) <= set(contract["fields"])
        field_catalog = pack["contract_schema"]["minimum_field_catalog_by_kind"][
            contract["kind"]
        ]
        assert set(field_catalog) == set(consumer_check["minimum_fields"])
        for field in consumer_check["minimum_fields"]:
            catalog_entry = field_catalog[field]
            assert catalog_entry["description"]
            assert catalog_entry["value_kind"]
            assert catalog_entry["proof_role"]
        readiness = pack["contract_readiness_index"][contract["kind"]]
        assert readiness["id"] == contract["id"]
        assert readiness["kind"] == contract["kind"]
        assert readiness["ready_for_downstream_fixture_use"] is True
        assert readiness["contract_passed"] is True
        assert readiness["required_fields_present"] is True
        assert readiness["missing_minimum_field_count"] == 0
        assert readiness["missing_minimum_fields"] == []
        assert readiness["all_theorem_ids_resolved"] is True
        assert readiness["all_theorem_ids_proved"] is True
        assert readiness["unresolved_theorem_count"] == 0
        assert readiness["unresolved_theorem_ids"] == []
        assert readiness["unproved_theorem_count"] == 0
        assert readiness["unproved_theorem_ids"] == []
        assert readiness["theorem_count"] == len(contract["theorem_ids"])
        assert readiness["entrypoint_count"] == len(contract["entrypoints"])
        assert readiness["quickstart_docs"] == contract["quickstart_docs"]
        assert readiness["living_book_pages"] == contract["living_book_pages"]
        recommendations = contract.get("planner_recommendations", [])
        assert readiness["planner_recommendation_count"] == len(recommendations)
        assert readiness["planner_recommendation_ids"] == [
            recommendation["id"] for recommendation in recommendations
        ]
        for recommendation in recommendations:
            indexed = pack["planner_recommendation_index"][recommendation["id"]]
            assert indexed["id"] == recommendation["id"]
            assert indexed["kind"] == contract["kind"]
            assert indexed["contract_id"] == contract["id"]
            assert indexed["ready_for_downstream_fixture_use"] is True
            assert indexed["action_kind"] == recommendation["action_kind"]
            assert indexed["status"] == recommendation["status"]
            assert indexed["coverage_scope"] == recommendation["coverage_scope"]
            assert indexed["evidence_fields"] == recommendation["evidence_fields"]
            assert indexed["theorem_ids"] == recommendation["theorem_ids"]
            assert indexed["quickstart_docs"] == contract["quickstart_docs"]
            assert indexed["living_book_pages"] == contract["living_book_pages"]
            assert indexed["validation_commands"] == contract["validation_commands"]
            assert indexed["source_paper"] == contract.get("source_paper")
            assert indexed["not_claimed"] == recommendation["not_claimed"]

    assert len(pack["planner_recommendation_index"]) == sum(
        len(contract.get("planner_recommendations", []))
        for contract in contracts.values()
    )

    assert contracts["rope_position_distinguishability"]["fields"][
        "certificate_schema_id"
    ] == "circle_calculus.rope_position_distinguishability.v0"
    assert "docs/ROPE_CERTIFIER_RESULTS_NOTE.md" in contracts[
        "rope_position_distinguishability"
    ]["quickstart_docs"]
    field_catalog = pack["contract_schema"]["minimum_field_catalog_by_kind"]
    rope_catalog = field_catalog["rope_position_distinguishability"]
    assert rope_catalog["certificate_schema_id"]["value_kind"] == "string"
    assert "Versioned certificate schema" in rope_catalog["certificate_schema_id"][
        "description"
    ]
    assert rope_catalog["worst_margin_radians"]["value_kind"] == "number"
    assert (
        rope_catalog["d19_proved_request_theorem_backed_classification"]["proof_role"]
        == "theorem_backed_check"
    )
    assert contracts["rope_position_distinguishability"]["fields"][
        "exact_discrete_pass"
    ] is True
    rope_fields = contracts["rope_position_distinguishability"]["fields"]
    assert rope_fields["d19_request_context"] == 131072
    assert rope_fields["d19_context_range_min_exclusive"] == 103993
    assert rope_fields["d19_context_range_max_inclusive"] == 196608
    assert rope_fields["d19_proved_margin"] == "1/328459"
    assert rope_fields["d19_impossible_margin_floor"] == "1/328458"
    assert rope_fields["d19_proved_request_margin"] == "1/328459"
    assert rope_fields["d19_proved_request_status"] == "proved"
    assert rope_fields["d19_proved_request_relation"] == (
        "at_or_below_proved_threshold"
    )
    assert rope_fields["d19_proved_request_theorem_backed_classification"] is True
    assert rope_fields["d19_proved_request_margin_applies"] is True
    assert rope_fields["d19_impossible_request_margin"] == "1/328458"
    assert rope_fields["d19_impossible_request_status"] == "impossible"
    assert rope_fields["d19_impossible_request_relation"] == (
        "at_or_above_impossible_floor"
    )
    assert rope_fields["d19_impossible_request_theorem_backed_classification"] is True
    assert rope_fields["d19_impossible_request_margin_applies"] is True
    assert rope_fields["d19_undecided_request_margin"] == "2/656917"
    assert rope_fields["d19_undecided_request_status"] == "undecided_margin_gap"
    assert rope_fields["d19_undecided_request_relation"] == (
        "strictly_between_thresholds"
    )
    assert (
        rope_fields["d19_undecided_request_theorem_backed_classification"]
        is False
    )
    assert rope_fields["d19_undecided_margin_open_gap"] is True
    assert rope_fields["d19_undecided_probe_margin_in_open_gap"] is True
    assert rope_fields["real_phase_dirichlet_witness_guardrail"] is True
    assert rope_fields["real_phase_margin_ceiling_guardrail"] is True
    assert rope_fields["real_phase_exact_weakest_margin_ceiling_guardrail"] is True
    assert rope_fields["d19_undecided_margin_interval_lower_exclusive"] == (
        "1/328459"
    )
    assert rope_fields["d19_undecided_margin_interval_upper_exclusive"] == (
        "1/328458"
    )
    assert rope_fields["d19_undecided_margin_interval_width"] == (
        "1/107884986222"
    )
    assert rope_fields["d19_undecided_request_failure_reason"] == (
        "requested_margin_between_proved_and_impossible_thresholds"
    )
    assert rope_fields["d19_margin_thresholds_ordered"] is True
    assert rope_fields["d19_proved_impossible_branches_disjoint"] is True
    assert rope_fields["d19_margin_status_exhaustive"] is True
    assert rope_fields["d19_in_range_semantic_trichotomy"] is True
    assert rope_fields["d19_proved_first_channel_bank_transfer"] is True
    assert rope_fields["d19_proved_first_channel_bank_shape"] == (
        "standard_channel0_first"
    )
    assert rope_fields["d19_proved_first_channel_pair_scope"] == (
        "all ordered unequal pairs left < right < requested_context"
    )
    assert rope_fields["d19_proved_first_channel_context_wide_contract"] is True
    assert rope_fields["d19_proved_first_channel_bank_tolerance_rule"] == (
        "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
    )
    assert "AIRA-T0216" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0221" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0214" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0231" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0232" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0233" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0234" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0235" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0236" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0237" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0238" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0239" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0240" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert "AIRA-T0241" in contracts["rope_position_distinguishability"]["theorem_ids"]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "rope_position_distinguishability --receipt --format json "
        "--field d19_proved_request_status "
        "--field d19_impossible_request_status "
        "--field d19_undecided_request_status "
        "--field d19_proved_first_channel_bank_transfer "
        "--field d19_proved_first_channel_bank_shape --field d19_proved_first_channel_pair_scope "
        "--field d19_proved_first_channel_context_wide_contract "
        "--field d19_proved_first_channel_radian_bank_form "
        "--field d19_proved_first_channel_bank_tolerance_rule "
        "--field d19_undecided_probe_margin_in_open_gap "
        "--field real_phase_dirichlet_witness_guardrail "
        "--field real_phase_margin_ceiling_guardrail "
        "--field real_phase_exact_weakest_margin_ceiling_guardrail "
        "--require-theorem AIRA-T0171 --require-theorem AIRA-T0172 "
        "--require-theorem AIRA-T0234 --require-theorem AIRA-T0235 "
        "--require-theorem AIRA-T0236 --require-theorem AIRA-T0237 "
        "--require-theorem AIRA-T0238 --require-theorem AIRA-T0239 "
        "--require-theorem AIRA-T0240 --require-theorem AIRA-T0241 "
        "--require-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "d19_proved_first_channel_bank_transfer "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "d19_proved_first_channel_context_wide_contract "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_radian_bank_form "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_undecided_probe_margin_in_open_gap "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=real_phase_dirichlet_witness_guardrail "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=real_phase_margin_ceiling_guardrail "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "real_phase_exact_weakest_margin_ceiling_guardrail "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236 --require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0238 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0239 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0240 "
        "--require-recommendation-theorem ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0241 "
        "--require-recommendation-action-parameter "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.applies "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.context_wide_contract "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.radian_bank_form "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.theorem_ids"
        in contracts["rope_position_distinguishability"]["validation_commands"]
    )
    rope_recommendations = contracts["rope_position_distinguishability"][
        "planner_recommendations"
    ]
    assert [recommendation["id"] for recommendation in rope_recommendations] == [
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
        "ROPE-USE-D19-MARGIN-FRONTIER",
    ]
    assert rope_recommendations[0]["coverage_scope"] == (
        "declared_integer_period_phase_bank_fixture"
    )
    assert rope_recommendations[0]["preset"] == "llama_style_10000_4k"
    assert rope_recommendations[0]["context_length"] == 4096
    assert rope_recommendations[0]["exact_discrete_pass"] is True
    assert rope_recommendations[0]["collision_pair_count"] == 0
    assert rope_recommendations[0]["theorem_ids"] == [
        "AIRA-T0024",
        "AIRA-T0036",
        "AIRA-T0179",
        "AIRA-T0180",
        "AIRA-T0184",
    ]
    assert rope_recommendations[1]["coverage_scope"] == (
        "standard_channel0_d19_context_range_fixture"
    )
    assert "d19_context_range_min_exclusive" in rope_recommendations[1][
        "evidence_fields"
    ]
    assert "d19_context_range_max_inclusive" in rope_recommendations[1][
        "evidence_fields"
    ]
    assert "real_phase_dirichlet_witness_guardrail" in rope_recommendations[1][
        "evidence_fields"
    ]
    assert "real_phase_margin_ceiling_guardrail" in rope_recommendations[1][
        "evidence_fields"
    ]
    assert "real_phase_exact_weakest_margin_ceiling_guardrail" in rope_recommendations[1][
        "evidence_fields"
    ]
    assert rope_recommendations[1]["request_context"] == 131072
    assert rope_recommendations[1]["proved_margin"] == "1/328459"
    assert rope_recommendations[1]["impossible_margin_floor"] == "1/328458"
    assert rope_recommendations[1]["proved_status"] == "proved"
    assert rope_recommendations[1]["impossible_status"] == "impossible"
    assert rope_recommendations[1]["undecided_margin"] == "2/656917"
    assert rope_recommendations[1]["undecided_status"] == "undecided_margin_gap"
    assert rope_recommendations[1]["undecided_probe_margin_in_open_gap"] is True
    assert rope_recommendations[1]["undecided_interval"] == {
        "lower_exclusive": "1/328459",
        "upper_exclusive": "1/328458",
        "width": "1/107884986222",
    }
    assert rope_recommendations[1]["applicable_context_range"] == {
        "min_exclusive": 103993,
        "max_inclusive": 196608,
    }
    assert rope_recommendations[1]["proved_branch_bank_transfer"] == {
        "applies": True,
        "bank_shape": "standard_channel0_first",
        "pair_scope": "all ordered unequal pairs left < right < requested_context",
        "context_wide_contract": True,
        "radian_bank_form": True,
        "tolerance_rule": (
            "Lean conclusion applies when tolerance < fullTurn * requestedMargin."
        ),
        "theorem_ids": [
            "AIRA-T0171",
            "AIRA-T0172",
            "AIRA-T0234",
            "AIRA-T0235",
            "AIRA-T0236",
            "AIRA-T0237",
        ],
    }
    assert rope_recommendations[1]["classifier_regions"] == [
        {
            "region": "proved",
            "condition": "requested_margin <= 1/328459",
            "request_status": "proved",
            "theorem_backed_classification": True,
            "theorem_backed_region": True,
            "theorem_ids": ["AIRA-T0216", "AIRA-T0217", "AIRA-T0233"],
            "meaning": (
                "Inside 103993 < context <= 196608, the requested one-channel "
                "standard RoPE margin is certified. The proved branch also "
                "transfers to a conditional first-channel finite-bank "
                "no-near-turn guarantee."
            ),
        },
        {
            "region": "undecided_margin_gap",
            "condition": "1/328459 < requested_margin < 1/328458",
            "request_status": "undecided_margin_gap",
            "theorem_backed_classification": False,
            "theorem_backed_region": True,
            "theorem_ids": [
                "AIRA-T0220",
                "AIRA-T0221",
                "AIRA-T0232",
                "AIRA-T0233",
                "AIRA-T0238",
            ],
            "meaning": (
                "Lean identifies this as the open interval between the proved "
                "and impossible branches; the current contract deliberately "
                "does not certify or reject that margin."
            ),
        },
        {
            "region": "impossible",
            "condition": "1/328458 <= requested_margin",
            "request_status": "impossible",
            "theorem_backed_classification": True,
            "theorem_backed_region": True,
            "theorem_ids": ["AIRA-T0217", "AIRA-T0219", "AIRA-T0233"],
            "meaning": (
                "Inside 103993 < context <= 196608, gap 103993 obstructs any "
                "advertised margin at or above 1/328458."
            ),
        },
    ]
    assert rope_recommendations[1]["theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0216",
        "AIRA-T0217",
        "AIRA-T0218",
        "AIRA-T0219",
        "AIRA-T0220",
        "AIRA-T0221",
        "AIRA-T0232",
        "AIRA-T0233",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
        "AIRA-T0238",
        "AIRA-T0239",
        "AIRA-T0240",
        "AIRA-T0241",
        "AIRA-T0230",
        "AIRA-T0231",
    ]
    assert contracts["kv_cache_ring_buffer"]["fields"][
        "certificate_schema_id"
    ] == "circle_calculus.kv_cache_ring_buffer_certificate.v0"
    kv_fields = contracts["kv_cache_ring_buffer"]["fields"]
    kv_catalog = field_catalog["kv_cache_ring_buffer"]
    assert kv_catalog["stale_probe_first_stale_token"]["value_kind"] == "integer"
    assert "KV-cache" in kv_catalog["stale_probe_first_stale_token"]["description"]
    assert kv_fields["stale_requested_count"] == 0
    assert kv_fields["stale_probe_requested_tokens"] == [12, 20]
    assert kv_fields["stale_probe_requested_slots"] == [12, 4]
    assert kv_fields["stale_probe_all_non_future"] is True
    assert kv_fields["stale_probe_tokens_distinct"] is True
    assert kv_fields["stale_probe_pass"] is False
    assert kv_fields["stale_probe_first_stale_token"] == 12
    assert kv_fields["stale_probe_first_stale_next_overwrite_token"] == 28
    assert kv_fields["stale_probe_stale_requested_count"] == 1
    assert kv_fields["stale_probe_stale_count_zero_iff_no_stale_member"] is True
    assert kv_fields["stale_probe_stale_member_blocks_pass"] is True
    assert (
        kv_fields["stale_probe_pass_iff_stale_count_zero_under_nonfuture_nodup"]
        is True
    )
    assert (
        kv_fields["stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup"]
        is True
    )
    assert kv_fields["sink_window_token_count"] == 20
    assert kv_fields["sink_window_token_count_bound"] == 20
    assert kv_fields["sink_window_token_count_le_sink_plus_cache"] is True
    assert kv_fields["sink_window_live_window_start"] == 16
    assert kv_fields["sink_window_live_window_length"] == 16
    assert kv_fields["sink_window_disjoint_exact_token_count"] == 20
    assert (
        kv_fields["sink_window_token_count_eq_sink_plus_live_window_when_disjoint"]
        is True
    )
    assert kv_fields["sink_prefix_disjoint_from_live_window"] is True
    assert kv_fields["sink_window_tokens_distinct"] is True
    assert kv_fields["sink_window_rolling_tokens_match_filtered_live_window"] is True
    assert kv_fields["sink_tokens_are_seen_prefix"] is True
    assert kv_fields["sink_tokens_non_future"] is True
    assert kv_fields["sink_tokens_retained_by_policy"] is True
    assert kv_fields["sink_tokens_outside_ordinary_rolling_window"] is True
    assert "AIM-T0110" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0117" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0118" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0119" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0136" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0137" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0148" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    assert "AIM-T0149" in contracts["kv_cache_ring_buffer"]["theorem_ids"]
    kv_recommendations = contracts["kv_cache_ring_buffer"]["planner_recommendations"]
    assert [recommendation["id"] for recommendation in kv_recommendations] == [
        "KV-DROP-STALE-REQUEST-TOKEN",
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    ]
    assert kv_recommendations[0]["coverage_scope"] == (
        "modeled_adapter_request_stale_probe"
    )
    assert kv_recommendations[0]["target_token"] == 12
    assert kv_recommendations[0]["next_same_slot_overwrite_token"] == 28
    assert kv_recommendations[0]["stale_requested_count"] == 1
    assert kv_recommendations[0]["theorem_ids"] == ["AIM-T0097", "AIM-T0103"]
    assert kv_recommendations[1]["coverage_scope"] == (
        "pinned_seen_prefix_plus_rolling_live_window"
    )
    assert kv_recommendations[1]["sink_size"] == 4
    assert kv_recommendations[1]["cache_size"] == 16
    assert kv_recommendations[1]["current"] == 31
    assert kv_recommendations[1]["request_token_count"] == 20
    assert kv_recommendations[1]["request_token_count_bound"] == 20
    assert kv_recommendations[1]["theorem_ids"] == [
        "AIM-T0104",
        "AIM-T0110",
        "AIM-T0117",
        "AIM-T0136",
        "AIM-T0137",
        "AIM-T0148",
        "AIM-T0149",
    ]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "kv_cache_ring_buffer --receipt --format json "
        "--field stale_probe_first_stale_token "
        "--field sink_tokens_retained_by_policy "
        "--field sink_window_exact_policy "
        "--field sink_window_tokens_distinct "
        "--field sink_prefix_disjoint_from_live_window "
        "--field sink_tokens_outside_ordinary_rolling_window "
        "--require-theorem AIM-T0103 --require-theorem AIM-T0104 "
        "--require-theorem AIM-T0149 "
        "--require-recommendation KV-DROP-STALE-REQUEST-TOKEN "
        "--require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST "
        "--require-recommendation-evidence-field "
        "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
        "sink_tokens_retained_by_policy "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
        "sink_tokens_outside_ordinary_rolling_window "
        "--require-recommendation-theorem "
        "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103 "
        "--require-recommendation-theorem "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149 "
        "--require-recommendation-action-parameter "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current"
        in contracts["kv_cache_ring_buffer"]["validation_commands"]
    )
    assert contracts["sparse_attention_coverage"]["fields"][
        "certificate_schema_id"
    ] == "circle_calculus.stride_family_sparse_attention_certificate.v0"
    sparse_fields = contracts["sparse_attention_coverage"]["fields"]
    assert (
        SPARSE_STRICT_RECEIPT_COMMAND
        in contracts["sparse_attention_coverage"]["validation_commands"]
    )
    assert sparse_fields["first_uncovered_lag"] == 5
    assert sparse_fields["first_uncovered_interval_start"] == 5
    assert sparse_fields["first_uncovered_interval_stop"] == 6
    assert sparse_fields["first_uncovered_interval_length"] == 2
    assert sparse_fields["local_window_needed_to_cover_first_uncovered_interval"] == 6
    assert sparse_fields["first_uncovered_interval_additional_local_slots"] == 2
    assert sparse_fields["first_uncovered_interval_repair_reaches_interval"] is True
    assert sparse_fields["first_interval_repair_next_uncovered_lag"] == 8
    assert sparse_fields["first_interval_repair_still_has_gap"] is True
    assert sparse_fields["first_interval_repair_covers_context"] is False
    assert sparse_fields["first_gap_local_window_shortfall"] == 1
    assert sparse_fields["local_window_needed_to_cover_first_gap"] == 5
    assert sparse_fields["current_window_below_first_gap"] is True
    assert sparse_fields["first_gap_repair_window_reaches"] is True
    assert sparse_fields["first_gap_repair_window_covers_context"] is False
    assert sparse_fields["first_gap_repair_window_is_final_positive_lag"] is False
    assert sparse_fields["first_gap_repair_threshold_matches_final_lag"] is True
    assert sparse_fields["local_window_complete_coverage_threshold"] == 119
    assert sparse_fields["local_window_complete_coverage_shortfall"] == 115
    assert sparse_fields["local_window_reaches_complete_coverage_threshold"] is False
    assert sparse_fields["local_window_threshold_certifies_complete"] is False
    assert sparse_fields["local_window_complete_threshold_is_exact_local_minimum"] is True
    assert sparse_fields["complete_repair_window"] == 119
    assert sparse_fields["complete_repair_window_additional_local_slots"] == 115
    assert sparse_fields["complete_repair_window_covers_context"] is True
    assert sparse_fields["complete_repair_window_uses_dense_threshold"] is True
    assert (
        sparse_fields["complete_repair_window_minimal_for_declared_stride_family"]
        is True
    )
    assert sparse_fields["complete_repair_window_minimal_witness_lag"] == 119
    assert sparse_fields["uncovered_lag_intervals"] == [
        {"start": 5, "stop": 6},
        {"start": 8, "stop": 12},
        {"start": 15, "stop": 20},
        {"start": 22, "stop": 25},
        {"start": 27, "stop": 38},
        {"start": 40, "stop": 119},
    ]
    assert sparse_fields["interval_repair_plan"] == [
        {
            "target_interval_start": 5,
            "target_interval_stop": 6,
            "proposed_local_window": 6,
            "additional_local_slots": 2,
            "remaining_gap_count_after_repair": 107,
        },
        {
            "target_interval_start": 8,
            "target_interval_stop": 12,
            "proposed_local_window": 12,
            "additional_local_slots": 6,
            "remaining_gap_count_after_repair": 102,
        },
        {
            "target_interval_start": 15,
            "target_interval_stop": 20,
            "proposed_local_window": 20,
            "additional_local_slots": 8,
            "remaining_gap_count_after_repair": 96,
        },
        {
            "target_interval_start": 22,
            "target_interval_stop": 25,
            "proposed_local_window": 25,
            "additional_local_slots": 5,
            "remaining_gap_count_after_repair": 92,
        },
        {
            "target_interval_start": 27,
            "target_interval_stop": 38,
            "proposed_local_window": 38,
            "additional_local_slots": 13,
            "remaining_gap_count_after_repair": 80,
        },
        {
            "target_interval_start": 40,
            "target_interval_stop": 119,
            "proposed_local_window": 119,
            "additional_local_slots": 81,
            "remaining_gap_count_after_repair": 0,
        },
    ]
    assert sparse_fields["interval_repair_plan_step_count"] == 6
    assert sparse_fields["interval_repair_plan_final_window"] == 119
    assert sparse_fields["interval_repair_plan_covers_context"] is True
    assert sparse_fields["interval_repair_plan_strictly_progresses"] is True
    assert sparse_fields["first_gap_repair_window_reaches_complete_threshold"] is False
    assert sparse_fields["largest_uncovered_interval_start"] == 40
    assert sparse_fields["largest_uncovered_interval_stop"] == 119
    assert sparse_fields["largest_uncovered_interval_length"] == 80
    assert (
        sparse_fields["local_window_needed_to_cover_largest_uncovered_interval"]
        == 119
    )
    assert sparse_fields["largest_uncovered_interval_additional_local_slots"] == 115
    assert sparse_fields["largest_uncovered_interval_repair_reaches_interval"] is True
    assert sparse_fields["largest_interval_repair_next_uncovered_lag"] is None
    assert sparse_fields["largest_interval_repair_still_has_gap"] is False
    assert sparse_fields["largest_interval_repair_covers_context"] is True
    assert sparse_fields["largest_uncovered_interval_is_tail"] is True
    assert sparse_fields["lag_unique_plus_loss_eq_raw"] is True
    assert sparse_fields["query_unique_plus_loss_eq_raw"] is True
    assert sparse_fields["lag_collision_pair_count"] == 0
    assert sparse_fields["query_collision_pair_count"] == 0
    assert sparse_fields["lag_collision_pair_count_zero_iff_no_collision"] is True
    assert sparse_fields["lag_collision_pair_count_positive_iff_collision"] is True
    assert sparse_fields["lag_collision_pair_count_bounds_dedup_loss"] is True
    assert sparse_fields["lag_collision_pair_count_excess_over_dedup_loss"] == 0
    assert sparse_fields["query_collision_pair_count_zero_iff_no_collision"] is True
    assert sparse_fields["query_collision_pair_count_positive_iff_collision"] is True
    assert sparse_fields["query_collision_pair_count_bounds_dedup_loss"] is True
    assert sparse_fields["query_collision_pair_count_excess_over_dedup_loss"] == 0
    sparse_recommendations = contracts["sparse_attention_coverage"][
        "planner_recommendations"
    ]
    assert [recommendation["id"] for recommendation in sparse_recommendations] == [
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
        "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
        "SPARSE-INTERVAL-REPAIR-PATH",
    ]
    assert sparse_recommendations[0]["coverage_scope"] == (
        "first_uncovered_interval_only"
    )
    assert sparse_recommendations[0]["proposed_local_window"] == 6
    assert sparse_recommendations[0]["additional_local_slots"] == 2
    assert sparse_recommendations[0]["target_interval_start"] == 5
    assert sparse_recommendations[0]["target_interval_stop"] == 6
    assert sparse_recommendations[0]["next_uncovered_lag_after_repair"] == 8
    assert sparse_recommendations[0]["still_has_gap_after_repair"] is True
    assert sparse_recommendations[0]["theorem_ids"] == [
        "AIT-T0104",
        "AIT-T0171",
        "AIT-T0166",
        "AIT-T0167",
    ]
    assert sparse_recommendations[1]["coverage_scope"] == "largest_uncovered_interval"
    assert sparse_recommendations[1]["proposed_local_window"] == 119
    assert sparse_recommendations[1]["additional_local_slots"] == 115
    assert sparse_recommendations[1]["target_interval_start"] == 40
    assert sparse_recommendations[1]["target_interval_stop"] == 119
    assert sparse_recommendations[1]["target_interval_length"] == 80
    assert sparse_recommendations[1]["covers_context_after_repair"] is True
    assert sparse_recommendations[1]["largest_interval_is_tail"] is True
    assert sparse_recommendations[1]["theorem_ids"] == [
        "AIT-T0094",
        "AIT-T0104",
        "AIT-T0171",
    ]
    assert sparse_recommendations[2]["coverage_scope"] == "all_positive_lags"
    assert sparse_recommendations[2]["proposed_local_window"] == 119
    assert sparse_recommendations[2]["additional_local_slots"] == 115
    assert sparse_recommendations[2]["theorem_ids"] == [
        "AIT-T0023",
        "AIT-T0034",
        "AIT-T0172",
        "AIT-T0168",
        "AIT-T0169",
        "AIT-T0170",
    ]
    assert sparse_recommendations[3]["coverage_scope"] == (
        "successive_first_uncovered_intervals"
    )
    assert sparse_recommendations[3]["step_count"] == 6
    assert sparse_recommendations[3]["final_local_window"] == 119
    assert sparse_recommendations[3]["covers_context_after_final_step"] is True
    assert sparse_recommendations[3]["strictly_progresses"] is True
    assert sparse_recommendations[3]["theorem_ids"] == [
        "AIT-T0094",
        "AIT-T0104",
        "AIT-T0171",
    ]
    sparse_catalog = field_catalog["sparse_attention_coverage"]
    assert sparse_catalog["first_uncovered_interval_stop"]["value_kind"] == "integer"
    assert "Inclusive end" in sparse_catalog["first_uncovered_interval_stop"][
        "description"
    ]
    assert (
        sparse_catalog["local_window_needed_to_cover_first_uncovered_interval"][
            "proof_role"
        ]
        == "finite_quantity_or_bound"
    )
    assert "AIT-T0149" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0150" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0151" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0152" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0155" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0156" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0157" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0158" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0159" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0160" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0161" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0162" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0163" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0164" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0165" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0166" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0167" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0168" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0169" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0170" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0171" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert "AIT-T0172" in contracts["sparse_attention_coverage"]["theorem_ids"]
    assert (
        pack["contract_schema"]["planner_recommendation_keys"]
        == [
            "id",
            "action_kind",
            "status",
            "coverage_scope",
            "evidence_fields",
            "theorem_ids",
            "not_claimed",
        ]
    )

    fanout = contracts["strided_candidate_fanout"]
    fanout_fields = fanout["fields"]
    fanout_catalog = field_catalog["strided_candidate_fanout"]
    assert fanout_catalog["effective_candidate_budget"]["value_kind"] == "integer"
    assert "Duplicate-collapsed" in fanout_catalog["effective_candidate_budget"][
        "description"
    ]
    assert (
        fanout_catalog["candidate_budget_accounting"]["proof_role"]
        == "theorem_backed_check"
    )
    assert "docs/STRIDED_CANDIDATE_FANOUT_CERTIFIER_QUICKSTART.md" in fanout["quickstart_docs"]
    assert "python scripts/strided_candidate_fanout_certify.py" in fanout["entrypoints"]
    assert fanout_fields["context_length"] == 12
    assert fanout_fields["stride"] == 5
    assert fanout_fields["start_index"] == 0
    assert fanout_fields["gcd"] == 1
    assert fanout_fields["predicted_reach"] == 12
    assert fanout_fields["full_coverage"] is True
    assert fanout_fields["orbit"] == [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
    assert fanout_fields["candidate_path"] == [7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0]
    assert fanout_fields["candidate_budget"] == 12
    assert fanout_fields["unique_candidate_count"] == 12
    assert fanout_fields["effective_candidate_budget"] == 12
    assert fanout_fields["duplicate_count"] == 0
    assert fanout_fields["candidate_budget_accounting"] is True
    assert fanout_fields["effective_budget_matches_unique_candidates"] is True
    assert fanout_fields["candidate_budget_shortfall"] == 0
    assert fanout_fields["effective_budget_reaches_predicted_reach"] is True
    assert "AIT-T0001" in fanout["theorem_ids"]
    assert "AIT-T0002" in fanout["theorem_ids"]
    assert "AIT-T0003" in fanout["theorem_ids"]
    assert "AIT-T0173" in fanout["theorem_ids"]
    fanout_recommendations = fanout["planner_recommendations"]
    assert [recommendation["id"] for recommendation in fanout_recommendations] == [
        "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE",
        "FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET",
    ]
    assert fanout_recommendations[0]["coverage_scope"] == (
        "finite_coprime_stride_orbit_fixture"
    )
    assert fanout_recommendations[0]["context_length"] == 12
    assert fanout_recommendations[0]["stride"] == 5
    assert fanout_recommendations[0]["gcd"] == 1
    assert fanout_recommendations[0]["predicted_reach"] == 12
    assert fanout_recommendations[0]["full_coverage"] is True
    assert fanout_recommendations[0]["theorem_ids"] == [
        "AIT-T0001",
        "AIT-T0002",
        "AIT-T0003",
    ]
    assert fanout_recommendations[1]["coverage_scope"] == (
        "declared_fixed_budget_candidate_path"
    )
    assert fanout_recommendations[1]["candidate_budget"] == 12
    assert fanout_recommendations[1]["unique_candidate_count"] == 12
    assert fanout_recommendations[1]["effective_candidate_budget"] == 12
    assert fanout_recommendations[1]["duplicate_count"] == 0
    assert fanout_recommendations[1]["candidate_budget_shortfall"] == 0
    assert fanout_recommendations[1]["theorem_ids"] == [
        "AIT-T0001",
        "AIT-T0002",
        "AIT-T0173",
    ]

    recurrence = contracts["recurrence_schedule"]
    recurrence_fields = recurrence["fields"]
    assert "docs/RECURRENCE_SCHEDULE_CERTIFIER_QUICKSTART.md" in recurrence["quickstart_docs"]
    assert "python scripts/recurrence_schedule_certify.py" in recurrence["entrypoints"]
    assert recurrence_fields["active_step_one_is_full_range"] is True
    assert recurrence_fields["first_step_active_token_count"] == len(recurrence_fields["tokens"])
    assert recurrence_fields["first_step_inactive_token_count"] == 0
    assert recurrence_fields["first_step_inactive_count_zero"] is True
    assert recurrence_fields["work_count_step"] == 2
    assert (
        recurrence_fields["work_step_active_token_count"]
        + recurrence_fields["work_step_inactive_token_count"]
        == len(recurrence_fields["tokens"])
    )
    assert recurrence_fields["work_step_active_inactive_count_eq_token_count"] is True
    assert recurrence_fields["post_period_active_empty"] is True
    assert recurrence_fields["post_period_active_token_count"] == 0
    assert recurrence_fields["post_period_inactive_token_count"] == len(recurrence_fields["tokens"])
    assert recurrence_fields["post_period_inactive_count_eq_token_count"] is True
    assert recurrence_fields["active_token_sets_descend"] is True
    assert recurrence_fields["active_token_lists_nodup"] is True
    assert recurrence_fields["active_token_counts_bounded"] is True
    assert recurrence_fields["active_token_counts_descend"] is True
    assert recurrence_fields["inactive_token_counts_ascend"] is True
    assert recurrence_fields["active_monotonicity_checked_steps"] == recurrence_fields["loop_period"] + 1
    assert recurrence_fields["total_work_horizon_steps"] == recurrence_fields["loop_period"]
    assert recurrence_fields["total_active_token_work"] == 21
    assert recurrence_fields["total_inactive_token_work"] == 19
    assert recurrence_fields["full_loop_token_work"] == 40
    assert recurrence_fields["scheduled_work_saving"] == 19
    assert recurrence_fields["scheduled_work_saving_accounting"] is True
    assert recurrence_fields["active_inactive_work_accounting"] is True
    assert recurrence_fields["scheduled_work_saving_matches_inactive_work"] is True
    assert recurrence_fields["scheduled_work_saving_positive"] is True
    assert recurrence_fields["active_work_below_full_loop_work"] is True
    assert recurrence_fields["scheduled_work_saving_positive_iff_active_work_shortfall"] is True
    assert recurrence_fields["scheduled_work_saving_zero"] is False
    assert recurrence_fields["active_work_equals_full_loop_work"] is False
    assert recurrence_fields["scheduled_work_saving_zero_iff_no_active_work_shortfall"] is True
    assert recurrence_fields["public_fixture_4_8_2_active_token_count"] == 6
    assert recurrence_fields["public_fixture_4_8_2_inactive_token_count"] == 2
    assert recurrence_fields["public_fixture_4_8_2_accounting_eq_token_count"] is True
    assert recurrence_fields["public_fixture_4_8_4_total_active_token_work"] == 20
    assert recurrence_fields["public_fixture_4_8_4_total_inactive_token_work"] == 12
    assert recurrence_fields["public_fixture_8_4_full_loop_token_work"] == 32
    assert recurrence_fields["public_fixture_4_8_4_scheduled_work_saving"] == 12
    assert recurrence_fields["public_fixture_4_8_4_work_saving_accounting"] is True
    assert recurrence_fields["public_fixture_4_8_4_active_inactive_work_accounting"] is True
    assert recurrence_fields["public_fixture_4_8_4_work_saving_matches_inactive_work"] is True
    assert recurrence_fields["public_fixture_4_8_4_scheduled_work_saving_positive"] is True
    assert recurrence_fields["public_fixture_4_8_4_active_work_below_full_loop_work"] is True
    assert (
        recurrence_fields["public_fixture_4_8_4_positive_saving_iff_active_work_shortfall"]
        is True
    )
    assert recurrence_fields["public_fixture_4_8_4_scheduled_work_saving_zero"] is False
    assert recurrence_fields["public_fixture_4_8_4_active_work_equals_full_loop_work"] is False
    assert (
        recurrence_fields["public_fixture_4_8_4_zero_saving_iff_no_active_work_shortfall"]
        is True
    )
    assert recurrence_fields["default_fixture_5_8_5_total_active_token_work"] == 21
    assert recurrence_fields["default_fixture_5_8_5_total_inactive_token_work"] == 19
    assert recurrence_fields["default_fixture_8_5_full_loop_token_work"] == 40
    assert recurrence_fields["default_fixture_5_8_5_scheduled_work_saving"] == 19
    assert recurrence_fields["default_fixture_5_8_5_work_saving_accounting"] is True
    assert recurrence_fields["default_fixture_5_8_5_active_inactive_work_accounting"] is True
    assert recurrence_fields["default_fixture_5_8_5_work_saving_matches_inactive_work"] is True
    assert recurrence_fields["post_period_extension_horizon_steps"] == 6
    assert recurrence_fields["post_period_extension_total_active_token_work"] == 21
    assert recurrence_fields["post_period_extension_total_inactive_token_work"] == 27
    assert recurrence_fields["post_period_extension_full_loop_token_work"] == 48
    assert recurrence_fields["post_period_extension_scheduled_work_saving"] == 27
    assert recurrence_fields["post_period_extension_active_work_unchanged"] is True
    assert recurrence_fields["post_period_extension_inactive_work_added_token_count"] is True
    assert recurrence_fields["post_period_extension_saving_added_token_count"] is True
    assert recurrence_fields["default_fixture_5_8_6_total_active_token_work"] == 21
    assert recurrence_fields["default_fixture_5_8_6_scheduled_work_saving"] == 27
    assert recurrence_fields["default_fixture_5_8_6_active_work_unchanged"] is True
    assert recurrence_fields["default_fixture_5_8_6_saving_added_token_count"] is True
    assert recurrence_fields["post_period_extra_steps"] == 3
    assert recurrence_fields["post_period_multi_extension_horizon_steps"] == 8
    assert recurrence_fields["post_period_multi_extension_total_active_token_work"] == 21
    assert recurrence_fields["post_period_multi_extension_total_inactive_token_work"] == 43
    assert recurrence_fields["post_period_multi_extension_full_loop_token_work"] == 64
    assert recurrence_fields["post_period_multi_extension_scheduled_work_saving"] == 43
    assert recurrence_fields["post_period_multi_extension_active_work_unchanged"] is True
    assert (
        recurrence_fields["post_period_multi_extension_inactive_work_added_extra_token_count"]
        is True
    )
    assert (
        recurrence_fields["post_period_multi_extension_saving_added_extra_token_count"]
        is True
    )
    assert recurrence_fields["default_fixture_5_8_8_total_active_token_work"] == 21
    assert recurrence_fields["default_fixture_5_8_8_scheduled_work_saving"] == 43
    assert recurrence_fields["default_fixture_5_8_8_active_work_unchanged"] is True
    assert (
        recurrence_fields["default_fixture_5_8_8_saving_added_extra_token_count"]
        is True
    )
    assert recurrence_fields["active_token_count_trace"] == [8, 6, 4, 2, 1]
    assert recurrence_fields["inactive_token_count_trace"] == [0, 2, 4, 6, 7]
    assert recurrence_fields["active_token_count_trace_sum"] == 21
    assert recurrence_fields["inactive_token_count_trace_sum"] == 19
    assert recurrence_fields["active_token_count_trace_sum_matches_total"] is True
    assert recurrence_fields["inactive_token_count_trace_sum_matches_total"] is True
    assert recurrence_fields["first_inactive_steps"] == [
        {"token_index": 0, "active_budget": 1, "first_inactive_step": 2},
        {"token_index": 1, "active_budget": 2, "first_inactive_step": 3},
        {"token_index": 2, "active_budget": 3, "first_inactive_step": 4},
        {"token_index": 3, "active_budget": 4, "first_inactive_step": 5},
        {"token_index": 4, "active_budget": 5, "first_inactive_step": 6},
        {"token_index": 5, "active_budget": 1, "first_inactive_step": 2},
        {"token_index": 6, "active_budget": 2, "first_inactive_step": 3},
        {"token_index": 7, "active_budget": 3, "first_inactive_step": 4},
    ]
    assert recurrence_fields["first_inactive_steps_match_budget_successor"] is True
    assert recurrence_fields["periodic_shift_base_token"] == 7
    assert recurrence_fields["periodic_shift_passes"] == 3
    assert recurrence_fields["periodic_shift_amount"] == 15
    assert recurrence_fields["periodic_shifted_token"] == 22
    assert recurrence_fields["periodic_shift_base_required_steps"] == 3
    assert recurrence_fields["periodic_shift_shifted_required_steps"] == 3
    assert recurrence_fields["periodic_shift_required_steps_invariant"] is True
    assert recurrence_fields["periodic_shift_base_recurrence_budget"] == 3
    assert recurrence_fields["periodic_shift_shifted_recurrence_budget"] == 3
    assert recurrence_fields["periodic_shift_recurrence_budget_invariant"] is True
    assert recurrence_fields["periodic_shift_base_training_free_budget"] == 3
    assert recurrence_fields["periodic_shift_shifted_training_free_budget"] == 3
    assert recurrence_fields["periodic_shift_training_free_budget_invariant"] is True
    assert recurrence_fields["periodic_shift_base_exit_step"] == 3
    assert recurrence_fields["periodic_shift_shifted_exit_step"] == 3
    assert recurrence_fields["periodic_shift_exit_step_invariant"] is True
    assert recurrence_fields["periodic_shift_base_overthinking_boundary"] == 4
    assert recurrence_fields["periodic_shift_shifted_overthinking_boundary"] == 4
    assert recurrence_fields["periodic_shift_overthinking_boundary_invariant"] is True
    assert recurrence_fields["periodic_shift_active_step"] == 2
    assert recurrence_fields["periodic_shift_base_active_at_step"] is True
    assert recurrence_fields["periodic_shift_shifted_active_at_step"] is True
    assert recurrence_fields["periodic_shift_active_at_step_invariant"] is True
    assert "AIM-T0026" in recurrence["theorem_ids"]
    assert "AIM-T0027" in recurrence["theorem_ids"]
    assert "AIM-T0028" in recurrence["theorem_ids"]
    assert "AIM-T0029" in recurrence["theorem_ids"]
    assert "AIM-T0030" in recurrence["theorem_ids"]
    assert "AIM-T0033" in recurrence["theorem_ids"]
    assert "AIM-T0034" in recurrence["theorem_ids"]
    assert "AIM-T0138" in recurrence["theorem_ids"]
    assert "AIM-T0139" in recurrence["theorem_ids"]
    assert "AIM-T0144" in recurrence["theorem_ids"]
    assert "AIM-T0145" in recurrence["theorem_ids"]
    assert "AIM-T0146" in recurrence["theorem_ids"]
    assert "AIM-T0147" in recurrence["theorem_ids"]
    assert "AIM-T0140" in recurrence["theorem_ids"]
    assert "AIM-T0141" in recurrence["theorem_ids"]
    assert "AIM-T0142" in recurrence["theorem_ids"]
    assert "AIM-T0143" in recurrence["theorem_ids"]
    assert "AIM-T0150" in recurrence["theorem_ids"]
    assert "AIM-T0151" in recurrence["theorem_ids"]
    assert "AIM-T0152" in recurrence["theorem_ids"]
    assert "AIM-T0153" in recurrence["theorem_ids"]
    assert "AIM-T0154" in recurrence["theorem_ids"]
    assert "AIM-T0155" in recurrence["theorem_ids"]
    assert "AIM-T0156" in recurrence["theorem_ids"]
    assert "AIM-T0157" in recurrence["theorem_ids"]
    assert "AIM-T0158" in recurrence["theorem_ids"]
    assert "AIM-T0159" in recurrence["theorem_ids"]
    assert "AIM-T0111" in recurrence["theorem_ids"]
    assert "AIM-T0112" in recurrence["theorem_ids"]
    assert "AIM-T0113" in recurrence["theorem_ids"]
    assert "AIM-T0114" in recurrence["theorem_ids"]
    assert "AIM-T0115" in recurrence["theorem_ids"]
    assert "AIM-T0116" in recurrence["theorem_ids"]
    assert "AIM-T0120" in recurrence["theorem_ids"]
    assert "AIM-T0128" in recurrence["theorem_ids"]
    assert "AIM-T0121" in recurrence["theorem_ids"]
    assert "AIM-T0122" in recurrence["theorem_ids"]
    assert "AIM-T0123" in recurrence["theorem_ids"]
    assert "AIM-T0129" in recurrence["theorem_ids"]
    assert "AIM-T0124" in recurrence["theorem_ids"]
    assert "AIM-T0125" in recurrence["theorem_ids"]
    assert "AIM-T0126" in recurrence["theorem_ids"]
    assert "AIM-T0127" in recurrence["theorem_ids"]
    assert "AIM-T0130" in recurrence["theorem_ids"]
    assert "AIM-T0131" in recurrence["theorem_ids"]
    assert "AIM-T0132" in recurrence["theorem_ids"]
    assert "AIM-T0133" in recurrence["theorem_ids"]
    assert "AIM-T0134" in recurrence["theorem_ids"]
    assert "AIM-T0135" in recurrence["theorem_ids"]
    recurrence_recommendations = recurrence["planner_recommendations"]
    assert [
        recommendation["id"] for recommendation in recurrence_recommendations
    ] == [
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    ]
    work_schedule = recurrence_recommendations[0]
    assert work_schedule["coverage_scope"] == "finite_default_loop_schedule_fixture"
    assert work_schedule["loop_period"] == 5
    assert work_schedule["token_count"] == 8
    assert work_schedule["horizon_steps"] == 5
    assert work_schedule["active_token_count_trace"] == [8, 6, 4, 2, 1]
    assert work_schedule["inactive_token_count_trace"] == [0, 2, 4, 6, 7]
    assert work_schedule["active_token_work"] == 21
    assert work_schedule["inactive_token_work"] == 19
    assert work_schedule["full_loop_token_work"] == 40
    assert work_schedule["scheduled_work_saving"] == 19
    assert work_schedule["post_period_extension_horizon_steps"] == 6
    assert work_schedule["post_period_extension_scheduled_work_saving"] == 27
    assert work_schedule["post_period_extra_steps"] == 3
    assert work_schedule["post_period_multi_extension_horizon_steps"] == 8
    assert work_schedule["post_period_multi_extension_scheduled_work_saving"] == 43
    assert work_schedule["theorem_ids"] == [
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
    shift_reuse = recurrence_recommendations[1]
    assert shift_reuse["coverage_scope"] == "whole_loop_period_token_shift_fixture"
    assert shift_reuse["base_token"] == 7
    assert shift_reuse["shift_passes"] == 3
    assert shift_reuse["shift_amount"] == 15
    assert shift_reuse["shifted_token"] == 22
    assert shift_reuse["active_step"] == 2
    assert shift_reuse["theorem_ids"] == [
        "AIM-T0026",
        "AIM-T0027",
        "AIM-T0028",
        "AIM-T0029",
        "AIM-T0030",
        "AIM-T0033",
        "AIM-T0034",
        "AIM-T0036",
    ]
    assert (
        "python scripts/circle_ai_contract_ready.py --kind "
        "recurrence_schedule --receipt --format json "
        "--field periodic_shift_required_steps_invariant "
        "--field periodic_shift_active_at_step_invariant "
        "--field total_active_token_work "
        "--field scheduled_work_saving "
        "--field scheduled_work_saving_accounting "
        "--field active_inactive_work_accounting "
        "--field scheduled_work_saving_positive "
        "--field post_period_multi_extension_scheduled_work_saving "
        "--require-theorem AIM-T0026 --require-theorem AIM-T0130 "
        "--require-theorem AIM-T0159 "
        "--require-recommendation "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE "
        "--require-recommendation "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "total_active_token_work "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_required_steps_invariant "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_active_at_step_invariant "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 "
        "--require-recommendation-theorem "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "scheduled_work_saving "
        "--require-recommendation-action-parameter "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount"
        in recurrence["validation_commands"]
    )

    memory = contracts["cyclic_memory_residue_winding"]
    memory_fields = memory["fields"]
    assert "docs/CYCLIC_MEMORY_CERTIFIER_QUICKSTART.md" in memory["quickstart_docs"]
    assert "python scripts/cyclic_memory_certify.py" in memory["entrypoints"]
    assert memory_fields["bank_size"] == 8
    assert memory_fields["event_index"] == 23
    assert memory_fields["event_count"] == 32
    assert memory_fields["residue_slot"] == 7
    assert memory_fields["winding"] == 2
    assert memory_fields["same_residue_events"] == [7, 15, 23, 31]
    assert memory_fields["same_residue_windings"] == [0, 1, 2, 3]
    assert memory_fields["max_alias_load"] == 4
    assert "AIM-T0001" in memory["theorem_ids"]
    assert "AIM-T0002" in memory["theorem_ids"]
    assert "AIM-T0004" in memory["theorem_ids"]
    assert "AIM-T0005" in memory["theorem_ids"]
    memory_recommendations = memory["planner_recommendations"]
    assert [recommendation["id"] for recommendation in memory_recommendations] == [
        "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE",
        "MEMORY-AUDIT-FINITE-ALIAS-LOAD",
    ]
    alias_provenance = memory_recommendations[0]
    assert alias_provenance["coverage_scope"] == (
        "finite_same_residue_alias_class_fixture"
    )
    assert alias_provenance["bank_size"] == 8
    assert alias_provenance["event_index"] == 23
    assert alias_provenance["residue_slot"] == 7
    assert alias_provenance["winding"] == 2
    assert alias_provenance["alias_count"] == 4
    assert alias_provenance["theorem_ids"] == [
        "AIM-T0001",
        "AIM-T0002",
        "AIM-T0004",
    ]
    alias_load = memory_recommendations[1]
    assert alias_load["coverage_scope"] == "declared_finite_trace_slot_loads"
    assert alias_load["bank_size"] == 8
    assert alias_load["event_count"] == 32
    assert alias_load["max_alias_load"] == 4
    assert alias_load["slot_loads"] == [4, 4, 4, 4, 4, 4, 4, 4]
    assert alias_load["theorem_ids"] == [
        "AIM-T0001",
        "AIM-T0005",
    ]

    phase = contracts["multicoil_phase_feature"]
    phase_fields = phase["fields"]
    assert "docs/MULTICOIL_PHASE_FEATURE_CERTIFIER_QUICKSTART.md" in phase["quickstart_docs"]
    assert "python scripts/multicoil_phase_feature_certify.py" in phase["entrypoints"]
    assert phase_fields["periods"] == [5, 7]
    assert phase_fields["position"] == 37
    assert phase_fields["phase_tuple"] == [2, 2]
    assert phase_fields["joint_repeat_horizon"] == 35
    assert phase_fields["shifted_position"] == 72
    assert phase_fields["shifted_phase_tuple"] == [2, 2]
    assert phase_fields["relative_period"] == 5
    assert phase_fields["relative_phase"] == 3
    assert phase_fields["shifted_relative_phase"] == 3
    assert "AIA-T0001" in phase["theorem_ids"]
    assert "AIA-T0002" in phase["theorem_ids"]
    assert "AIA-T0004" in phase["theorem_ids"]
    assert "AIT-T0004" in phase["theorem_ids"]
    assert "AIT-T0005" in phase["theorem_ids"]
    phase_recommendations = phase["planner_recommendations"]
    assert [recommendation["id"] for recommendation in phase_recommendations] == [
        "PHASE-USE-JOINT-REPEAT-HORIZON",
        "PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT",
    ]
    assert phase_recommendations[0]["coverage_scope"] == (
        "declared_finite_period_bank_fixture"
    )
    assert phase_recommendations[0]["periods"] == [5, 7]
    assert phase_recommendations[0]["position"] == 37
    assert phase_recommendations[0]["phase_tuple"] == [2, 2]
    assert phase_recommendations[0]["joint_repeat_horizon"] == 35
    assert phase_recommendations[0]["shifted_position"] == 72
    assert phase_recommendations[0]["shifted_phase_tuple"] == [2, 2]
    assert phase_recommendations[0]["theorem_ids"] == [
        "AIA-T0001",
        "AIA-T0002",
        "AIA-T0004",
    ]
    assert phase_recommendations[1]["coverage_scope"] == (
        "declared_query_key_relative_phase_fixture"
    )
    assert phase_recommendations[1]["query_position"] == 41
    assert phase_recommendations[1]["key_position"] == 18
    assert phase_recommendations[1]["relative_period"] == 5
    assert phase_recommendations[1]["relative_phase"] == 3
    assert phase_recommendations[1]["shifted_relative_phase"] == 3
    assert phase_recommendations[1]["theorem_ids"] == [
        "AIT-T0004",
        "AIT-T0005",
    ]

    mixer = contracts["circulant_block_cyclic_mixer"]
    mixer_fields = mixer["fields"]
    assert (
        "docs/CIRCULANT_BLOCK_CYCLIC_MIXER_CERTIFIER_QUICKSTART.md"
        in mixer["quickstart_docs"]
    )
    assert "python scripts/circulant_block_cyclic_mixer_certify.py" in mixer["entrypoints"]
    assert mixer_fields["period"] == 8
    assert mixer_fields["channel_count"] == 128
    assert mixer_fields["block_size"] == 8
    assert mixer_fields["circulant_output"] == mixer_fields["dense_output"]
    assert mixer_fields["max_abs_dense_delta"] == 0
    assert mixer_fields["circulant_parameters"] == 8
    assert mixer_fields["dense_parameters"] == 64
    assert mixer_fields["circulant_parameter_ratio"] == 0.125
    assert mixer_fields["dense_adapter_parameters"] == 2048
    assert mixer_fields["lora_parameters"] == 576
    assert mixer_fields["block_cyclic_parameters"] == 128
    assert mixer_fields["block_to_dense_ratio"] == 0.0625
    assert mixer_fields["block_loads"] == [16, 16, 16, 16, 16, 16, 16, 16]
    assert "AIT-T0006" in mixer["theorem_ids"]
    assert "AIT-T0007" in mixer["theorem_ids"]
    assert "AIT-T0008" in mixer["theorem_ids"]
    assert "AIT-T0009" in mixer["theorem_ids"]
    assert "AIRA-T0001" in mixer["theorem_ids"]
    assert "AIRA-T0002" in mixer["theorem_ids"]
    assert "AIRA-T0004" in mixer["theorem_ids"]
    mixer_recommendations = mixer["planner_recommendations"]
    assert [recommendation["id"] for recommendation in mixer_recommendations] == [
        "MIXER-AUDIT-CIRCULANT-DENSE-PARITY",
        "MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET",
    ]
    assert mixer_recommendations[0]["coverage_scope"] == (
        "deterministic_circulant_fixture"
    )
    assert mixer_recommendations[0]["period"] == 8
    assert mixer_recommendations[0]["max_abs_dense_delta"] == 0
    assert mixer_recommendations[0]["circulant_parameters"] == 8
    assert mixer_recommendations[0]["dense_parameters"] == 64
    assert mixer_recommendations[0]["circulant_parameter_ratio"] == 0.125
    assert mixer_recommendations[0]["theorem_ids"] == [
        "AIT-T0006",
        "AIT-T0007",
        "AIT-T0008",
        "AIT-T0009",
    ]
    assert mixer_recommendations[1]["coverage_scope"] == (
        "declared_block_cyclic_adapter_fixture"
    )
    assert mixer_recommendations[1]["channel_count"] == 128
    assert mixer_recommendations[1]["block_size"] == 8
    assert mixer_recommendations[1]["dense_adapter_parameters"] == 2048
    assert mixer_recommendations[1]["lora_parameters"] == 576
    assert mixer_recommendations[1]["block_cyclic_parameters"] == 128
    assert mixer_recommendations[1]["block_to_dense_ratio"] == 0.0625
    assert mixer_recommendations[1]["theorem_ids"] == [
        "AIRA-T0001",
        "AIRA-T0002",
        "AIRA-T0004",
    ]

    seed_rule = contracts["seed_rule_exact_regeneration"]
    seed_fields = seed_rule["fields"]
    seed_catalog = field_catalog["seed_rule_exact_regeneration"]
    assert seed_catalog["closure_condition"]["value_kind"] == "string"
    assert "exact regeneration" in seed_catalog["closure_condition"][
        "description"
    ]
    assert seed_catalog["rules"]["value_kind"] == "array"
    assert "docs/SEED_RULE_CERTIFIER_QUICKSTART.md" in seed_rule["quickstart_docs"]
    assert "python scripts/seed_rule_certify.py" in seed_rule["entrypoints"]
    assert seed_fields["artifact_id"] == "finite_circle"
    assert seed_fields["fixture_n"] == 128
    assert seed_fields["exact_regeneration"] is True
    assert seed_fields["generator_shorter"] is True
    assert seed_fields["storage_saving_positive"] is True
    assert (
        seed_fields["storage_saving"] + seed_fields["generator_length"]
        == seed_fields["explicit_length"]
    )
    assert seed_fields["generator_shorter_iff_positive_saving"] is True
    assert seed_fields["storage_saving_add_generator_length_eq_explicit_length"] is True
    assert seed_fields["bounded_search_id"] == "public_seed_rule_finite_circle_search"
    assert seed_fields["bounded_search_finite_search_space"] is True
    assert seed_fields["bounded_search_candidate_count"] == 3
    assert seed_fields["bounded_search_exact_candidate_count"] == 2
    assert seed_fields["bounded_search_exact_candidate_count_le_candidate_count"] is True
    assert seed_fields["bounded_search_has_best_exact"] is True
    assert (
        seed_fields["bounded_search_best_exact_exists_iff_exact_count_positive"]
        is True
    )
    assert seed_fields["bounded_search_best_exact_implies_candidate_count_positive"] is True
    assert seed_fields["bounded_search_best_exact_artifact_id"] == "finite_circle"
    assert seed_fields["bounded_search_best_exact_candidate_id"] == (
        "finite_circle_unit_fixture"
    )
    assert seed_fields["bounded_search_best_exact_regenerates"] is True
    assert seed_fields["bounded_search_has_best_shorter"] is True
    assert seed_fields["bounded_search_best_shorter_artifact_id"] == "finite_circle"
    assert seed_fields["bounded_search_best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert seed_fields["bounded_search_best_shorter_generator_shorter"] is True
    assert seed_fields["bounded_search_candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
        "finite_circle_public_fixture",
    ]
    assert seed_fields["bounded_search_exact_candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_public_fixture",
    ]
    assert seed_fields["bounded_search_shorter_candidate_ids_by_generator_length"] == [
        "finite_circle_public_fixture"
    ]
    seed_candidates = seed_fields["bounded_search_candidates"]
    assert [candidate["candidate_id"] for candidate in seed_candidates] == [
        "finite_circle_public_fixture",
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
    ]
    assert seed_candidates[0]["exact_regeneration"] is True
    assert seed_candidates[0]["rank_by_generator_length"] == 3
    assert seed_candidates[0]["generator_shorter"] is True
    assert seed_candidates[0]["storage_saving"] == 71
    assert seed_candidates[2]["exact_regeneration"] is False
    assert seed_fields["bounded_search_note"].endswith("not an optimality theorem.")
    assert "GEN-T0037" in seed_rule["theorem_ids"]
    assert "GEN-T0044" in seed_rule["theorem_ids"]
    assert "GEN-T0045" in seed_rule["theorem_ids"]
    assert "GEN-T0046" in seed_rule["theorem_ids"]
    assert "GEN-T0050" in seed_rule["theorem_ids"]
    seed_recommendations = seed_rule["planner_recommendations"]
    assert [recommendation["id"] for recommendation in seed_recommendations] == [
        "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
        "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
    ]
    exact_recipe = seed_recommendations[0]
    assert exact_recipe["coverage_scope"] == "public_finite_circle_fixture"
    assert exact_recipe["artifact_id"] == "finite_circle"
    assert exact_recipe["fixture_n"] == 128
    assert exact_recipe["rule_ids"] == ["enumerate_nodes"]
    assert exact_recipe["generated_object_length"] == 128
    assert exact_recipe["theorem_ids"] == [
        "GEN-T0040",
        "GEN-T0041",
        "GEN-T0043",
    ]
    shorter_candidate = seed_recommendations[1]
    assert shorter_candidate["coverage_scope"] == "declared_finite_candidate_search"
    assert shorter_candidate["search_id"] == "public_seed_rule_finite_circle_search"
    assert shorter_candidate["candidate_count"] == 3
    assert shorter_candidate["exact_candidate_count"] == 2
    assert shorter_candidate["best_shorter_artifact_id"] == "finite_circle"
    assert shorter_candidate["best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert shorter_candidate["candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
        "finite_circle_public_fixture",
    ]
    assert shorter_candidate["explicit_length"] == 454
    assert shorter_candidate["generator_length"] == 383
    assert shorter_candidate["storage_saving"] == 71
    assert shorter_candidate["theorem_ids"] == [
        "GEN-T0037",
        "GEN-T0044",
        "GEN-T0045",
        "GEN-T0046",
        "GEN-T0047",
        "GEN-T0048",
        "GEN-T0049",
        "GEN-T0050",
    ]


def test_generic_contract_pack_json_schema_validates_pack() -> None:
    pack = build_contract_pack()
    schema = build_contract_pack_json_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_id"]["const"] == pack["schema_id"]
    assert "contracts" in schema["required"]
    acceptance_policy_schema = schema["properties"]["acceptance_policy"]
    assert "standalone_schema_checker" in acceptance_policy_schema["required"]
    assert "rejection_report_schema_id" in acceptance_policy_schema["required"]
    assert "rejection_report_schema_path" in acceptance_policy_schema["required"]
    assert acceptance_policy_schema["properties"]["standalone_schema_checker"][
        "minLength"
    ] == 1
    assert acceptance_policy_schema["properties"]["rejection_report_schema_id"][
        "const"
    ] == "circle_calculus.downstream_ci_rejection_report.v0"
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(pack, schema)

    contract_schema = schema["properties"]["contract_schema"]
    assert "minimum_field_catalog_by_kind" in contract_schema["required"]
    fanout_contract_item = schema["properties"]["contracts"]["items"]
    fanout_requirement = next(
        item
        for item in fanout_contract_item["allOf"]
        if item["if"]["properties"]["kind"]["const"] == "strided_candidate_fanout"
    )
    assert "effective_candidate_budget" in fanout_requirement["then"][
        "properties"
    ]["fields"]["required"]
    contract_item = schema["properties"]["contracts"]["items"]
    assert "source_paper" in contract_item["required"]
    assert contract_item["properties"]["source_paper"]["minLength"] == 1
    assert contract_item["properties"]["quickstart_docs"]["minItems"] == 1
    assert contract_item["properties"]["living_book_pages"]["minItems"] == 1
    assert contract_item["properties"]["entrypoints"]["minItems"] == 1
    assert contract_item["properties"]["validation_commands"]["minItems"] == 1
    planner_index_item = schema["properties"]["planner_recommendation_index"][
        "additionalProperties"
    ]
    assert "source_paper" in planner_index_item["required"]
    assert "quickstart_docs" in planner_index_item["required"]
    assert "living_book_pages" in planner_index_item["required"]
    assert planner_index_item["properties"]["quickstart_docs"]["minItems"] == 1
    assert planner_index_item["properties"]["living_book_pages"]["minItems"] == 1


def test_generic_contract_pack_json_schema_rejects_weak_source_trails() -> None:
    schema = build_contract_pack_json_schema()

    missing_source_paper = build_contract_pack()
    del missing_source_paper["contracts"][0]["source_paper"]
    with pytest.raises(jsonschema.ValidationError, match="source_paper"):
        jsonschema.validate(missing_source_paper, schema)

    empty_quickstart_docs = build_contract_pack()
    empty_quickstart_docs["contracts"][0]["quickstart_docs"] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(empty_quickstart_docs, schema)

    empty_recommendation_evidence = build_contract_pack()
    empty_recommendation_evidence["contracts"][0]["planner_recommendations"][0][
        "evidence_fields"
    ] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(empty_recommendation_evidence, schema)

    missing_index_source_paper = build_contract_pack()
    recommendation_id = missing_index_source_paper["contracts"][0][
        "planner_recommendations"
    ][0]["id"]
    del missing_index_source_paper["planner_recommendation_index"][
        recommendation_id
    ]["source_paper"]
    with pytest.raises(jsonschema.ValidationError, match="source_paper"):
        jsonschema.validate(missing_index_source_paper, schema)

    empty_index_living_book_pages = build_contract_pack()
    empty_index_living_book_pages["planner_recommendation_index"][
        recommendation_id
    ]["living_book_pages"] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(empty_index_living_book_pages, schema)


def test_acceptance_policy_json_schema_validates_example_policy() -> None:
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    schema = build_acceptance_policy_json_schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_id"]["const"] == (
        "circle_calculus.ai_contract_acceptance_policy.v0"
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(policy, schema)


def test_acceptance_report_and_receipt_json_schemas_validate_default_policy() -> None:
    pack = build_contract_pack()
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["expected_pack_fingerprint"] = pack["pack_content_fingerprint"]
    for spec in policy["contracts"]:
        spec["expected_contract_fingerprint"] = pack["contract_fingerprint_index"][
            spec["kind"]
        ]["content_fingerprint"]

    report = contract_acceptance_policy_report(pack, policy)
    report_schema = build_acceptance_policy_report_json_schema()
    receipt_schema = build_acceptance_receipt_json_schema()

    assert report_schema["properties"]["acceptance_policy_report_schema"][
        "const"
    ] == "circle_calculus.ai_contract_acceptance_policy_report.v0"
    assert receipt_schema["properties"]["receipt_schema"]["const"] == (
        "circle_calculus.ai_contract_acceptance_receipt.v0"
    )
    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(report, report_schema)
    for receipt in report["receipts"]:
        jsonschema.validate(receipt, receipt_schema)


def test_downstream_rejection_report_json_schema_validates_failure_report(
    tmp_path: Path,
) -> None:
    pack = build_contract_pack()
    pack_path = tmp_path / "circle_ai_contract_pack.json"
    policy_path = tmp_path / "policy.json"
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["expected_pack_fingerprint"] = pack["pack_content_fingerprint"]
    for spec in policy["contracts"]:
        spec["expected_contract_fingerprint"] = pack["contract_fingerprint_index"][
            spec["kind"]
        ]["content_fingerprint"]
    pack_path.write_text(json.dumps(pack))
    policy_path.write_text(json.dumps(policy))

    result = subprocess.run(
        [
            sys.executable,
            "examples/downstream_ci_accept_circle_ai_contracts.py",
            "--pack",
            str(pack_path),
            "--policy",
            str(policy_path),
            "--format",
            "json",
            "--planner-recommendation",
            "NOT-A-RECOMMENDATION",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 4
    payload = json.loads(result.stderr)
    schema = build_downstream_rejection_report_json_schema()
    assert schema["properties"]["schema_id"]["const"] == (
        "circle_calculus.downstream_ci_rejection_report.v0"
    )
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(payload, schema)
    assert payload["failure_count"] == len(payload["failures"])


def test_acceptance_policy_json_schema_rejects_empty_requirement_pins() -> None:
    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    schema = build_acceptance_policy_json_schema()

    policy["contracts"][0]["required_fields"] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(policy, schema)

    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["required_recommendation_theorem_ids"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(policy, schema)

    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["required_recommendation_action_parameters"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(policy, schema)

    policy = json.loads(
        (ROOT / "examples/circle_ai_contract_acceptance_policy.json").read_text()
    )
    policy["contracts"][0]["required_recommendation_action_parameter_paths"][
        "ROPE-USE-D19-MARGIN-FRONTIER"
    ] = []
    with pytest.raises(jsonschema.ValidationError, match="non-empty"):
        jsonschema.validate(policy, schema)


def test_generic_contract_pack_references_resolve() -> None:
    pack = build_contract_pack()
    manifest_ids = _manifest_ids()
    dictionary_ids = _dictionary_ids()

    for source_doc in pack["source_docs"]:
        assert (ROOT / source_doc).exists(), source_doc
    for command in pack["validation_commands"]:
        assert command.startswith(("python ", "make ")), command

    for contract in pack["contracts"]:
        assert set(contract["theorem_ids"]) <= manifest_ids
        assert set(contract["dictionary_ids"]) <= dictionary_ids
        assert (ROOT / contract["source_paper"]).exists(), contract["source_paper"]
        for doc in contract["quickstart_docs"]:
            assert (ROOT / doc).exists(), doc
        for page in contract["living_book_pages"]:
            assert (ROOT / page).exists(), page
        for command in contract["entrypoints"]:
            if command.startswith("python "):
                script = command.split()[1]
                assert (ROOT / script).exists(), command
        for command in contract["validation_commands"]:
            assert command.startswith(("python ", "make ")), command
            if command.startswith("python "):
                parts = command.split()
                if len(parts) > 1 and parts[1] != "-m":
                    assert (ROOT / parts[1]).exists(), command


def test_generic_contract_pack_uses_focused_living_book_lessons() -> None:
    contracts = {contract["kind"]: contract for contract in build_contract_pack()["contracts"]}

    for kind, expected_page in EXPECTED_LIVING_BOOK_PAGE_BY_KIND.items():
        assert expected_page in contracts[kind]["living_book_pages"]


def test_generic_export_script_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "circle_contracts.json"
    schema_out = tmp_path / "circle_contracts.schema.json"
    policy_schema_out = tmp_path / "circle_policy.schema.json"
    policy_report_schema_out = tmp_path / "circle_policy_report.schema.json"
    receipt_schema_out = tmp_path / "circle_receipt.schema.json"
    runner_request_schema_out = tmp_path / "circle_runner_request.schema.json"
    runner_request_validation_schema_out = (
        tmp_path / "circle_runner_request_validation.schema.json"
    )
    runner_receipt_schema_out = tmp_path / "circle_runner_receipt.schema.json"
    runner_compact_receipt_schema_out = (
        tmp_path / "circle_runner_compact_receipt.schema.json"
    )
    runner_check_schema_out = tmp_path / "circle_runner_check.schema.json"
    receipt_file_check_schema_out = tmp_path / "circle_receipt_file_check.schema.json"
    certification_bundle_schema_out = (
        tmp_path / "circle_certification_bundle.schema.json"
    )
    artifact_manifest_schema_out = tmp_path / "circle_artifact_manifest.schema.json"
    artifact_manifest_file_check_schema_out = (
        tmp_path / "circle_artifact_manifest_file_check.schema.json"
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/export_circle_ai_contracts.py",
            "--out",
            str(out),
            "--acceptance-policy-schema-out",
            str(policy_schema_out),
            "--acceptance-policy-report-schema-out",
            str(policy_report_schema_out),
            "--acceptance-receipt-schema-out",
            str(receipt_schema_out),
            "--contract-runner-request-schema-out",
            str(runner_request_schema_out),
            "--contract-runner-request-validation-schema-out",
            str(runner_request_validation_schema_out),
            "--contract-runner-receipt-schema-out",
            str(runner_receipt_schema_out),
            "--contract-runner-compact-receipt-schema-out",
            str(runner_compact_receipt_schema_out),
            "--contract-runner-check-schema-out",
            str(runner_check_schema_out),
            "--contract-receipt-file-check-schema-out",
            str(receipt_file_check_schema_out),
            "--contract-certification-bundle-schema-out",
            str(certification_bundle_schema_out),
            "--contract-artifact-manifest-schema-out",
            str(artifact_manifest_schema_out),
            "--contract-artifact-manifest-file-check-schema-out",
            str(artifact_manifest_file_check_schema_out),
        ],
        check=True,
    )
    data = json.loads(out.read_text())
    schema = json.loads(schema_out.read_text())
    policy_schema = json.loads(policy_schema_out.read_text())
    policy_report_schema = json.loads(policy_report_schema_out.read_text())
    receipt_schema = json.loads(receipt_schema_out.read_text())
    runner_request_schema = json.loads(runner_request_schema_out.read_text())
    runner_request_validation_schema = json.loads(
        runner_request_validation_schema_out.read_text()
    )
    runner_receipt_schema = json.loads(runner_receipt_schema_out.read_text())
    runner_compact_receipt_schema = json.loads(
        runner_compact_receipt_schema_out.read_text()
    )
    runner_check_schema = json.loads(runner_check_schema_out.read_text())
    receipt_file_check_schema = json.loads(receipt_file_check_schema_out.read_text())
    certification_bundle_schema = json.loads(
        certification_bundle_schema_out.read_text()
    )
    artifact_manifest_schema = json.loads(artifact_manifest_schema_out.read_text())
    artifact_manifest_file_check_schema = json.loads(
        artifact_manifest_file_check_schema_out.read_text()
    )
    assert data["schema_id"] == "circle_calculus.ai_contract_pack.v0"
    assert len(data["contracts"]) == 9
    jsonschema.validate(data, schema)
    jsonschema.Draft202012Validator.check_schema(policy_schema)
    jsonschema.Draft202012Validator.check_schema(policy_report_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.Draft202012Validator.check_schema(runner_request_schema)
    jsonschema.Draft202012Validator.check_schema(runner_request_validation_schema)
    jsonschema.Draft202012Validator.check_schema(runner_receipt_schema)
    jsonschema.Draft202012Validator.check_schema(runner_compact_receipt_schema)
    jsonschema.Draft202012Validator.check_schema(runner_check_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_file_check_schema)
    jsonschema.Draft202012Validator.check_schema(certification_bundle_schema)
    jsonschema.Draft202012Validator.check_schema(artifact_manifest_schema)
    jsonschema.Draft202012Validator.check_schema(artifact_manifest_file_check_schema)
    assert runner_check_schema == build_contract_runner_check_json_schema()
    assert (
        runner_compact_receipt_schema
        == build_compact_contract_receipt_json_schema()
    )
    assert receipt_file_check_schema == build_contract_receipt_file_check_json_schema()
    assert (
        certification_bundle_schema
        == build_contract_certification_bundle_json_schema()
    )
    assert artifact_manifest_schema == build_contract_artifact_manifest_json_schema()
    assert (
        artifact_manifest_file_check_schema
        == build_contract_artifact_manifest_file_check_json_schema()
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        check=True,
    )


def test_generic_pack_validator_summary_and_required_kind(tmp_path: Path) -> None:
    out = tmp_path / "circle_contracts.json"
    out.write_text(json.dumps(build_contract_pack(), indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
            "--summary",
            "--require-kind",
            "sparse_attention_coverage",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract pack ok:" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "ready=True" in result.stdout
    assert "proof_resolved=True" in result.stdout
    assert "proof_proved=True" in result.stdout
    assert "unresolved=0" in result.stdout
    assert "unproved=0" in result.stdout


def test_generic_pack_validator_rejects_missing_required_kind(tmp_path: Path) -> None:
    out = tmp_path / "circle_contracts.json"
    out.write_text(json.dumps(build_contract_pack(), indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
            "--require-kind",
            "not_a_contract_kind",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "required contract kind is missing: not_a_contract_kind" in result.stderr


def test_generic_pack_validator_rejects_missing_minimum_field(tmp_path: Path) -> None:
    data = build_contract_pack()
    for contract in data["contracts"]:
        if contract["kind"] == "kv_cache_ring_buffer":
            del contract["fields"]["stale_requested_count"]
            break
    out = tmp_path / "bad_circle_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "stale_requested_count" in result.stderr


def test_generic_pack_validator_rejects_stale_proof_status(tmp_path: Path) -> None:
    data = build_contract_pack()
    contract = data["contracts"][0]
    contract["proof_status"]["all_theorem_ids_proved"] = False
    contract["consumer_check"]["all_theorem_ids_proved"] = False
    contract["consumer_check"]["ready_for_downstream_fixture_use"] = False
    out = tmp_path / "bad_proof_status_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "proof_status proved flag drifted" in result.stderr


def test_generic_pack_validator_rejects_readiness_index_drift(tmp_path: Path) -> None:
    data = build_contract_pack()
    data["contract_readiness_index"]["sparse_attention_coverage"][
        "ready_for_downstream_fixture_use"
    ] = False
    out = tmp_path / "bad_readiness_index_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "readiness index ready_for_downstream_fixture_use drifted" in result.stderr


def test_generic_pack_validator_rejects_missing_catalog_entry(tmp_path: Path) -> None:
    data = build_contract_pack()
    del data["contract_schema"]["minimum_field_catalog_by_kind"][
        "kv_cache_ring_buffer"
    ]["stale_requested_count"]
    out = tmp_path / "bad_catalog_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "minimum_field_catalog_by_kind.kv_cache_ring_buffer missing fields" in (
        result.stderr
    )
    assert "stale_requested_count" in result.stderr


def test_generic_pack_validator_rejects_catalog_value_kind_drift(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["contract_schema"]["minimum_field_catalog_by_kind"][
        "strided_candidate_fanout"
    ]["effective_candidate_budget"]["value_kind"] = "string"
    out = tmp_path / "bad_catalog_value_kind_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "catalog value_kind for effective_candidate_budget drifted" in result.stderr


def test_generic_pack_validator_rejects_recommendation_evidence_drift(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    for contract in data["contracts"]:
        if contract["kind"] == "sparse_attention_coverage":
            contract["planner_recommendations"][0]["evidence_fields"].append(
                "not_a_field"
            )
            break
    out = tmp_path / "bad_recommendation_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "planner_recommendations[0] unknown evidence fields" in result.stderr
    assert "not_a_field" in result.stderr


def test_generic_pack_validator_rejects_recommendation_index_drift(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["contract_readiness_index"]["sparse_attention_coverage"][
        "planner_recommendation_ids"
    ] = []
    out = tmp_path / "bad_recommendation_index_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "readiness index planner_recommendation_ids drifted" in result.stderr


def test_generic_pack_validator_rejects_duplicate_recommendation_ids(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    duplicate_id = data["contracts"][0]["planner_recommendations"][0]["id"]
    for contract in data["contracts"]:
        if contract["kind"] == "sparse_attention_coverage":
            contract["planner_recommendations"][0]["id"] = duplicate_id
            break
    out = tmp_path / "bad_duplicate_recommendation_id_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "duplicate planner recommendation id" in result.stderr
    assert duplicate_id in result.stderr


def test_generic_pack_validator_rejects_recommendation_index_evidence_drift(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    recommendation_id = "ROPE-USE-D19-MARGIN-FRONTIER"
    data["planner_recommendation_index"][recommendation_id][
        "evidence_fields"
    ] = [
        field
        for field in data["planner_recommendation_index"][recommendation_id][
            "evidence_fields"
        ]
        if field != "d19_context_range_max_inclusive"
    ]
    out = tmp_path / "bad_recommendation_index_evidence_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert (
        f"planner_recommendation_index.{recommendation_id}.evidence_fields drifted"
    ) in result.stderr


def test_generic_pack_validator_rejects_missing_validation_script(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["validation_commands"].append("python scripts/not_a_real_contract_check.py")
    out = tmp_path / "bad_validation_script_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "validation script is missing: scripts/not_a_real_contract_check.py" in (
        result.stderr
    )


def test_generic_pack_validator_rejects_missing_contract_pytest_path(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["contracts"][0]["validation_commands"].append(
        "python -m pytest tests/not_a_real_contract_test.py -q"
    )
    out = tmp_path / "bad_validation_pytest_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "pytest validation path is missing: tests/not_a_real_contract_test.py" in (
        result.stderr
    )


def test_generic_pack_validator_rejects_missing_validation_make_target(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["validation_commands"].append("make not-a-real-contract-target")
    out = tmp_path / "bad_validation_make_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "make target is missing: not-a-real-contract-target" in result.stderr


def test_generic_pack_validator_rejects_recommendation_validation_command_drift(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    recommendation = next(iter(data["planner_recommendation_index"].values()))
    recommendation["validation_commands"] = []
    out = tmp_path / "bad_recommendation_validation_commands_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "planner_recommendation_index." in result.stderr
    assert ".validation_commands drifted" in result.stderr


def test_generic_pack_validator_rejects_unknown_validation_kind(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["validation_commands"].append(
        "python scripts/circle_ai_contract_ready.py --kind not_a_contract_kind"
    )
    out = tmp_path / "bad_validation_kind_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "unknown contract kind in command: not_a_contract_kind" in result.stderr


def test_contract_ready_default_invocation_prints_readiness_summary() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI contract readiness summary ok:" in result.stdout
    assert "ready=" in result.stdout
    assert "not_ready=0" in result.stdout
    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=kv_cache_ring_buffer" in result.stdout
    assert "proof_proved=True" in result.stdout


def test_contract_ready_default_invocation_json_summary() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["all_ready_for_downstream_fixture_use"] is True
    assert payload["not_ready_contract_count"] == 0
    assert payload["ready_contract_count"] == payload["contract_count"]
    assert {
        record["kind"] for record in payload["contracts"]
    } >= {
        "rope_position_distinguishability",
        "kv_cache_ring_buffer",
        "sparse_attention_coverage",
        "recurrence_schedule",
    }


def test_contract_ready_digest_without_kind_still_fails() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/circle_ai_contract_ready.py",
            "--digest",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--kind is required for digest" in result.stderr


def test_generic_pack_validator_rejects_unknown_validation_field(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    data["validation_commands"].append(
        "python scripts/circle_ai_contract_ready.py "
        "--kind sparse_attention_coverage --field not_a_contract_field"
    )
    out = tmp_path / "bad_validation_field_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert (
        "unknown field for sparse_attention_coverage in command: "
        "not_a_contract_field"
    ) in result.stderr


def test_generic_pack_validator_rejects_missing_source_paper(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    del data["contracts"][0]["source_paper"]
    out = tmp_path / "bad_missing_source_paper_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "source_paper must be a non-empty path" in result.stderr


def test_generic_pack_validator_rejects_missing_contract_ready_validation(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    contract = data["contracts"][0]
    contract["validation_commands"] = [
        command
        for command in contract["validation_commands"]
        if "scripts/circle_ai_contract_ready.py" not in command
    ]
    out = tmp_path / "bad_missing_ready_command_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "validation_commands must include circle_ai_contract_ready.py --kind" in (
        result.stderr
    )


def test_generic_pack_validator_rejects_missing_contract_pytest_validation(
    tmp_path: Path,
) -> None:
    data = build_contract_pack()
    contract = data["contracts"][0]
    contract["validation_commands"] = [
        command
        for command in contract["validation_commands"]
        if "python -m pytest" not in command
    ]
    out = tmp_path / "bad_missing_pytest_command_contracts.json"
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_pack.py",
            "--path",
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "validation_commands must include pytest" in result.stderr
