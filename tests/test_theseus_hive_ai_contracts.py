from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.theseus_hive_contracts import build_contract_pack


def test_contract_pack_has_public_safe_boundary_and_core_contracts() -> None:
    pack = build_contract_pack()
    assert pack["schema_id"] == "circle_calculus.theseus_hive_ai_contracts.v0"
    assert "ASI" in pack["claim_boundary"]
    contracts = {contract["kind"]: contract for contract in pack["contracts"]}

    assert {
        "recurrence_schedule",
        "strided_candidate_fanout",
        "cyclic_memory_residue_winding",
        "multicoil_phase_feature",
        "circulant_block_cyclic_mixer",
        "seed_rule_exact_regeneration",
    } <= set(contracts)

    for contract in contracts.values():
        assert contract["status"] == "fixture"
        assert contract["contract_passed"] is True
        assert contract["ordinary_baselines"]
        assert contract["theorem_ids"]
        assert "not" in contract["not_claimed"].lower()


def test_recurrence_contract_records_exit_and_token_budgets() -> None:
    contract = {
        item["kind"]: item for item in build_contract_pack()["contracts"]
    }["recurrence_schedule"]
    fields = contract["fields"]
    assert fields["required_steps"] == fields["exit_step"]
    assert 1 <= fields["required_steps"] <= fields["loop_period"]
    assert fields["middle_block_budget"] == fields["required_steps"]
    assert fields["active_step_one_tokens"] == list(range(len(fields["tokens"])))
    assert fields["active_step_one_is_full_range"] is True
    assert fields["first_step_active_token_count"] == len(fields["tokens"])
    assert fields["first_step_inactive_token_count"] == 0
    assert fields["first_step_inactive_count_zero"] is True
    assert fields["work_count_step"] == 2
    assert fields["work_step_active_token_count"] + fields["work_step_inactive_token_count"] == len(fields["tokens"])
    assert fields["work_step_active_inactive_count_eq_token_count"] is True
    assert fields["post_period_step"] == fields["loop_period"] + 1
    assert fields["post_period_active_tokens"] == []
    assert fields["post_period_active_empty"] is True
    assert fields["post_period_active_token_count"] == 0
    assert fields["post_period_inactive_token_count"] == len(fields["tokens"])
    assert fields["post_period_inactive_count_eq_token_count"] is True
    assert fields["active_token_sets_descend"] is True
    assert fields["active_token_lists_nodup"] is True
    assert fields["active_token_counts_bounded"] is True
    assert fields["active_token_counts_descend"] is True
    assert fields["inactive_token_counts_ascend"] is True
    assert fields["active_monotonicity_checked_steps"] == fields["loop_period"] + 1
    assert fields["total_work_horizon_steps"] == fields["loop_period"]
    assert fields["total_active_token_work"] == 21
    assert fields["total_inactive_token_work"] == 19
    assert fields["full_loop_token_work"] == 40
    assert fields["scheduled_work_saving"] == 19
    assert fields["scheduled_work_saving_accounting"] is True
    assert fields["active_inactive_work_accounting"] is True
    assert fields["scheduled_work_saving_matches_inactive_work"] is True
    assert fields["scheduled_work_saving_positive"] is True
    assert fields["active_work_below_full_loop_work"] is True
    assert fields["scheduled_work_saving_positive_iff_active_work_shortfall"] is True
    assert fields["scheduled_work_saving_zero"] is False
    assert fields["active_work_equals_full_loop_work"] is False
    assert fields["scheduled_work_saving_zero_iff_no_active_work_shortfall"] is True
    assert fields["public_fixture_4_8_2_active_token_count"] == 6
    assert fields["public_fixture_4_8_2_inactive_token_count"] == 2
    assert fields["public_fixture_4_8_2_accounting_eq_token_count"] is True
    assert fields["public_fixture_4_8_4_total_active_token_work"] == 20
    assert fields["public_fixture_4_8_4_total_inactive_token_work"] == 12
    assert fields["public_fixture_8_4_full_loop_token_work"] == 32
    assert fields["public_fixture_4_8_4_scheduled_work_saving"] == 12
    assert fields["public_fixture_4_8_4_work_saving_accounting"] is True
    assert fields["public_fixture_4_8_4_active_inactive_work_accounting"] is True
    assert fields["public_fixture_4_8_4_work_saving_matches_inactive_work"] is True
    assert fields["public_fixture_4_8_4_scheduled_work_saving_positive"] is True
    assert fields["public_fixture_4_8_4_active_work_below_full_loop_work"] is True
    assert fields["public_fixture_4_8_4_positive_saving_iff_active_work_shortfall"] is True
    assert fields["public_fixture_4_8_4_scheduled_work_saving_zero"] is False
    assert fields["public_fixture_4_8_4_active_work_equals_full_loop_work"] is False
    assert fields["public_fixture_4_8_4_zero_saving_iff_no_active_work_shortfall"] is True
    assert fields["default_fixture_5_8_5_total_active_token_work"] == 21
    assert fields["default_fixture_5_8_5_total_inactive_token_work"] == 19
    assert fields["default_fixture_8_5_full_loop_token_work"] == 40
    assert fields["default_fixture_5_8_5_scheduled_work_saving"] == 19
    assert fields["default_fixture_5_8_5_work_saving_accounting"] is True
    assert fields["default_fixture_5_8_5_active_inactive_work_accounting"] is True
    assert fields["default_fixture_5_8_5_work_saving_matches_inactive_work"] is True
    assert fields["post_period_extension_horizon_steps"] == 6
    assert fields["post_period_extension_total_active_token_work"] == 21
    assert fields["post_period_extension_total_inactive_token_work"] == 27
    assert fields["post_period_extension_full_loop_token_work"] == 48
    assert fields["post_period_extension_scheduled_work_saving"] == 27
    assert fields["post_period_extension_active_work_unchanged"] is True
    assert fields["post_period_extension_inactive_work_added_token_count"] is True
    assert fields["post_period_extension_saving_added_token_count"] is True
    assert fields["default_fixture_5_8_6_total_active_token_work"] == 21
    assert fields["default_fixture_5_8_6_scheduled_work_saving"] == 27
    assert fields["default_fixture_5_8_6_active_work_unchanged"] is True
    assert fields["default_fixture_5_8_6_saving_added_token_count"] is True
    assert fields["post_period_extra_steps"] == 3
    assert fields["post_period_multi_extension_horizon_steps"] == 8
    assert fields["post_period_multi_extension_total_active_token_work"] == 21
    assert fields["post_period_multi_extension_total_inactive_token_work"] == 43
    assert fields["post_period_multi_extension_full_loop_token_work"] == 64
    assert fields["post_period_multi_extension_scheduled_work_saving"] == 43
    assert fields["post_period_multi_extension_active_work_unchanged"] is True
    assert fields["post_period_multi_extension_inactive_work_added_extra_token_count"] is True
    assert fields["post_period_multi_extension_saving_added_extra_token_count"] is True
    assert fields["default_fixture_5_8_8_total_active_token_work"] == 21
    assert fields["default_fixture_5_8_8_scheduled_work_saving"] == 43
    assert fields["default_fixture_5_8_8_active_work_unchanged"] is True
    assert fields["default_fixture_5_8_8_saving_added_extra_token_count"] is True
    assert fields["periodic_shift_base_token"] == 7
    assert fields["periodic_shift_passes"] == 3
    assert fields["periodic_shift_amount"] == 15
    assert fields["periodic_shifted_token"] == 22
    assert fields["periodic_shift_required_steps_invariant"] is True
    assert fields["periodic_shift_recurrence_budget_invariant"] is True
    assert fields["periodic_shift_training_free_budget_invariant"] is True
    assert fields["periodic_shift_exit_step_invariant"] is True
    assert fields["periodic_shift_overthinking_boundary_invariant"] is True
    assert fields["periodic_shift_active_step"] == 2
    assert fields["periodic_shift_active_at_step_invariant"] is True
    assert len(fields["tokens"]) == 8
    assert all(1 <= token["budget"] <= fields["loop_period"] for token in fields["tokens"])
    assert "AIM-T0026" in contract["theorem_ids"]
    assert "AIM-T0027" in contract["theorem_ids"]
    assert "AIM-T0028" in contract["theorem_ids"]
    assert "AIM-T0029" in contract["theorem_ids"]
    assert "AIM-T0030" in contract["theorem_ids"]
    assert "AIM-T0033" in contract["theorem_ids"]
    assert "AIM-T0034" in contract["theorem_ids"]
    assert "AIM-T0035" in contract["theorem_ids"]
    assert "AIM-T0111" in contract["theorem_ids"]
    assert "AIM-T0112" in contract["theorem_ids"]
    assert "AIM-T0113" in contract["theorem_ids"]
    assert "AIM-T0114" in contract["theorem_ids"]
    assert "AIM-T0115" in contract["theorem_ids"]
    assert "AIM-T0116" in contract["theorem_ids"]
    assert "AIM-T0120" in contract["theorem_ids"]
    assert "AIM-T0128" in contract["theorem_ids"]
    assert "AIM-T0123" in contract["theorem_ids"]
    assert "AIM-T0129" in contract["theorem_ids"]
    assert "AIM-T0127" in contract["theorem_ids"]
    assert "AIM-T0130" in contract["theorem_ids"]
    assert "AIM-T0131" in contract["theorem_ids"]
    assert "AIM-T0144" in contract["theorem_ids"]
    assert "AIM-T0145" in contract["theorem_ids"]
    assert "AIM-T0132" in contract["theorem_ids"]
    assert "AIM-T0133" in contract["theorem_ids"]
    assert "AIM-T0134" in contract["theorem_ids"]
    assert "AIM-T0146" in contract["theorem_ids"]
    assert "AIM-T0135" in contract["theorem_ids"]
    assert "AIM-T0138" in contract["theorem_ids"]
    assert "AIM-T0139" in contract["theorem_ids"]
    assert "AIM-T0140" in contract["theorem_ids"]
    assert "AIM-T0141" in contract["theorem_ids"]
    assert "AIM-T0142" in contract["theorem_ids"]
    assert "AIM-T0147" in contract["theorem_ids"]
    assert "AIM-T0143" in contract["theorem_ids"]
    assert "AIM-T0150" in contract["theorem_ids"]
    assert "AIM-T0151" in contract["theorem_ids"]
    assert "AIM-T0152" in contract["theorem_ids"]
    assert "AIM-T0153" in contract["theorem_ids"]
    assert "AIM-T0154" in contract["theorem_ids"]
    assert "AIM-T0155" in contract["theorem_ids"]
    assert "AIM-T0156" in contract["theorem_ids"]
    assert "AIM-T0157" in contract["theorem_ids"]
    assert "AIM-T0158" in contract["theorem_ids"]
    assert "AIM-T0159" in contract["theorem_ids"]


def test_fanout_memory_phase_and_mixer_contracts_have_controls() -> None:
    contracts = {item["kind"]: item for item in build_contract_pack()["contracts"]}

    fanout_contract = contracts["strided_candidate_fanout"]
    assert "AIT-T0173" in fanout_contract["theorem_ids"]
    fanout = contracts["strided_candidate_fanout"]["fields"]
    assert fanout["gcd"] == 1
    assert fanout["full_coverage"] is True
    assert fanout["predicted_reach"] == fanout["context_length"]
    assert len(set(fanout["orbit"])) == fanout["predicted_reach"]
    assert fanout["unique_candidate_count"] == fanout["effective_candidate_budget"]
    assert fanout["effective_candidate_budget"] + fanout["duplicate_count"] == fanout["candidate_budget"]
    assert fanout["candidate_budget_accounting"] is True
    assert fanout["effective_budget_matches_unique_candidates"] is True
    assert fanout["candidate_budget_shortfall"] == 0
    assert fanout["effective_budget_reaches_predicted_reach"] is True

    memory = contracts["cyclic_memory_residue_winding"]["fields"]
    assert memory["event_index"] == memory["winding"] * memory["bank_size"] + memory["residue_slot"]
    assert len(memory["same_residue_events"]) == memory["max_alias_load"]

    phase = contracts["multicoil_phase_feature"]["fields"]
    assert phase["phase_tuple"] == phase["shifted_phase_tuple"]
    assert phase["relative_phase"] == phase["shifted_relative_phase"]

    mixer = contracts["circulant_block_cyclic_mixer"]["fields"]
    assert mixer["circulant_output"] == mixer["dense_output"]
    assert mixer["circulant_parameters"] < mixer["dense_parameters"]
    assert "dense_mixer" in contracts["circulant_block_cyclic_mixer"]["ordinary_baselines"]


def test_seed_rule_contract_is_exact_regeneration_not_compression_claim() -> None:
    contract = {
        item["kind"]: item for item in build_contract_pack()["contracts"]
    }["seed_rule_exact_regeneration"]
    fields = contract["fields"]
    assert fields["artifact_id"] == "finite_circle"
    assert fields["fixture_n"] == 128
    assert fields["generated_object"] == fields["regenerated_object"]
    assert fields["exact_regeneration"] is True
    assert fields["generator_shorter"] is True
    assert fields["storage_saving"] == fields["explicit_length"] - fields["generator_length"]
    assert fields["storage_saving_positive"] is True
    assert fields["generator_shorter_iff_positive_saving"] is True
    assert fields["storage_saving_add_generator_length_eq_explicit_length"] is True
    assert fields["bounded_search_id"] == "public_seed_rule_finite_circle_search"
    assert fields["bounded_search_finite_search_space"] is True
    assert fields["bounded_search_candidate_count"] == 3
    assert fields["bounded_search_exact_candidate_count"] == 2
    assert fields["bounded_search_exact_candidate_count_le_candidate_count"] is True
    assert fields["bounded_search_has_best_exact"] is True
    assert fields["bounded_search_best_exact_exists_iff_exact_count_positive"] is True
    assert fields["bounded_search_best_exact_implies_candidate_count_positive"] is True
    assert fields["bounded_search_best_exact_artifact_id"] == "finite_circle"
    assert fields["bounded_search_best_exact_regenerates"] is True
    assert fields["bounded_search_has_best_shorter"] is True
    assert fields["bounded_search_best_shorter_artifact_id"] == "finite_circle"
    assert fields["bounded_search_best_shorter_generator_shorter"] is True
    assert fields["bounded_search_note"].endswith("not an optimality theorem.")
    assert {
        "GEN-T0037",
        "GEN-T0044",
        "GEN-T0045",
        "GEN-T0046",
        "GEN-T0047",
        "GEN-T0048",
        "GEN-T0049",
        "GEN-T0050",
    } <= set(contract["theorem_ids"])
    assert "object_only_storage" in contract["ordinary_baselines"]
    assert "not" in contract["not_claimed"].lower()


def test_export_script_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "theseus_contracts.json"
    subprocess.run(
        [sys.executable, "scripts/export_theseus_hive_ai_contracts.py", "--out", str(out)],
        check=True,
    )
    data = json.loads(out.read_text())
    assert data["schema_id"] == "circle_calculus.theseus_hive_ai_contracts.v0"
    assert len(data["contracts"]) == 6
