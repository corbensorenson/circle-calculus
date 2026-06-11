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
    assert len(fields["tokens"]) == 8
    assert all(1 <= token["budget"] <= fields["loop_period"] for token in fields["tokens"])
    assert "AIM-T0035" in contract["theorem_ids"]


def test_fanout_memory_phase_and_mixer_contracts_have_controls() -> None:
    contracts = {item["kind"]: item for item in build_contract_pack()["contracts"]}

    fanout = contracts["strided_candidate_fanout"]["fields"]
    assert fanout["gcd"] == 1
    assert fanout["full_coverage"] is True
    assert fanout["predicted_reach"] == fanout["context_length"]
    assert len(set(fanout["orbit"])) == fanout["predicted_reach"]

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
    assert fields["generated_object"] == fields["regenerated_object"]
    assert fields["exact_regeneration"] is True
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
