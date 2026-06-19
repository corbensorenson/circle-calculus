from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "seed_rule_certify.py"


def test_seed_rule_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "seed_rule_contract.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert (
        "seed_rule_contract=READY artifact_id=finite_circle fixture_n=128 "
        "exact_regeneration=True generator_shorter=True"
    ) in result.stdout
    assert (
        "storage_accounting=explicit_length=454 generator_length=383 "
        "storage_saving=71 storage_saving_positive=True "
        "generator_shorter_iff_positive_saving=True "
        "saving_plus_generator_eq_explicit=True "
        "theorems=GEN-T0046,GEN-T0047,GEN-T0048,GEN-T0049,GEN-T0050"
    ) in result.stdout
    assert (
        "bounded_search=search_id=public_seed_rule_finite_circle_search "
        "candidate_count=3 exact_candidate_count=2 "
        "exact_count_le_candidate_count=True has_best_exact=True "
        "best_exact_regenerates=True has_best_shorter=True "
        "best_shorter_generator_shorter=True "
        "theorems=GEN-T0037,GEN-T0044,GEN-T0045"
    ) in result.stdout
    assert (
        "candidate_ranking=by_generator_length="
        "('finite_circle_unit_fixture', 'finite_circle_broken_fixture', "
        "'finite_circle_public_fixture') exact_by_generator_length="
        "('finite_circle_unit_fixture', 'finite_circle_public_fixture') "
        "shorter_by_generator_length=('finite_circle_public_fixture',) "
        "best_exact=finite_circle_unit_fixture "
        "best_shorter=finite_circle_public_fixture"
    ) in result.stdout
    assert (
        "generator_record=seed=(('n', 128),) rules=('enumerate_nodes',) "
        "closure_condition='stop before node n, since nodes are residues modulo n'"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "not an optimality theorem" in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-SEED-RULE-001"
    assert payload["kind"] == "seed_rule_exact_regeneration"
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert "docs/SEED_RULE_CERTIFIER_QUICKSTART.md" in payload["quickstart_docs"]
    assert "python scripts/seed_rule_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["fixture_n"] == 128
    assert fields["exact_regeneration"] is True
    assert fields["generator_shorter"] is True
    assert fields["storage_saving"] == 71
    assert fields["bounded_search_candidate_count"] == 3
    assert fields["bounded_search_exact_candidate_count"] == 2
    assert fields["bounded_search_best_exact_regenerates"] is True
    assert fields["bounded_search_best_shorter_generator_shorter"] is True
    assert fields["bounded_search_best_exact_candidate_id"] == (
        "finite_circle_unit_fixture"
    )
    assert fields["bounded_search_best_shorter_candidate_id"] == (
        "finite_circle_public_fixture"
    )
    assert fields["bounded_search_candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
        "finite_circle_public_fixture",
    ]
    assert fields["bounded_search_exact_candidate_ids_by_generator_length"] == [
        "finite_circle_unit_fixture",
        "finite_circle_public_fixture",
    ]
    assert fields["bounded_search_shorter_candidate_ids_by_generator_length"] == [
        "finite_circle_public_fixture"
    ]
    candidates = fields["bounded_search_candidates"]
    assert [candidate["candidate_id"] for candidate in candidates] == [
        "finite_circle_public_fixture",
        "finite_circle_unit_fixture",
        "finite_circle_broken_fixture",
    ]
    public_candidate = candidates[0]
    assert public_candidate["declared_index"] == 0
    assert public_candidate["rank_by_generator_length"] == 3
    assert public_candidate["exact_regeneration"] is True
    assert public_candidate["generator_shorter"] is True
    assert public_candidate["storage_saving"] == 71
    assert "GEN-T0037" in payload["theorem_ids"]
    assert "GEN-T0050" in payload["theorem_ids"]


def test_seed_rule_certifier_cli_json_small_circle_negative_case() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--n",
            "8",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    fields = payload["fields"]
    assert payload["contract_passed"] is False
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is False
    assert fields["fixture_n"] == 8
    assert fields["exact_regeneration"] is True
    assert fields["generator_shorter"] is False
    assert fields["storage_saving_positive"] is False
    assert fields["bounded_search_has_best_exact"] is True
    assert fields["bounded_search_has_best_shorter"] is False
    assert fields["bounded_search_best_exact_candidate_id"] == (
        "finite_circle_unit_fixture"
    )
    assert fields["bounded_search_best_shorter_candidate_id"] is None
    assert fields["bounded_search_shorter_candidate_ids_by_generator_length"] == []
