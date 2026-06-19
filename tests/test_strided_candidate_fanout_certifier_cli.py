from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "strided_candidate_fanout_certify.py"


def test_strided_candidate_fanout_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "fanout_contract.json"
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
        "strided_candidate_fanout_contract=READY context_length=12 "
        "start_index=0 stride=5 gcd=1 predicted_reach=12 full_coverage=True"
    ) in result.stdout
    assert (
        "orbit=nodes=(0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7) "
        "orbit_unique=True predicted_reach_matches_orbit_length=True "
        "theorems=AIT-T0001,AIT-T0002,AIT-T0003"
    ) in result.stdout
    assert (
        "candidate_path=nodes=(7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0) "
        "candidate_budget=12 unique_candidate_count=12 "
        "effective_candidate_budget=12 duplicate_count=0 path_unique=True "
        "candidate_budget_accounting=True candidate_budget_shortfall=0 "
        "effective_budget_reaches_predicted_reach=True budget_theorems=AIT-T0173"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-FANOUT-001"
    assert payload["kind"] == "strided_candidate_fanout"
    assert payload["contract_passed"] is True
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert "docs/STRIDED_CANDIDATE_FANOUT_CERTIFIER_QUICKSTART.md" in payload["quickstart_docs"]
    assert "python scripts/strided_candidate_fanout_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["context_length"] == 12
    assert fields["stride"] == 5
    assert fields["start_index"] == 0
    assert fields["gcd"] == 1
    assert fields["predicted_reach"] == 12
    assert fields["full_coverage"] is True
    assert fields["orbit"] == [0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7]
    assert fields["candidate_path"] == [7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0]
    assert fields["candidate_budget"] == 12
    assert fields["unique_candidate_count"] == 12
    assert fields["effective_candidate_budget"] == 12
    assert fields["duplicate_count"] == 0
    assert fields["candidate_budget_accounting"] is True
    assert fields["effective_budget_matches_unique_candidates"] is True
    assert fields["candidate_budget_shortfall"] == 0
    assert fields["effective_budget_reaches_predicted_reach"] is True
    assert {"AIT-T0001", "AIT-T0002", "AIT-T0003", "AIT-T0173"} <= set(
        payload["theorem_ids"]
    )


def test_strided_candidate_fanout_certifier_cli_json_custom_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context-length",
            "10",
            "--stride",
            "4",
            "--start-index",
            "1",
            "--path-length",
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
    assert payload["contract_passed"] is True
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert fields["context_length"] == 10
    assert fields["stride"] == 4
    assert fields["start_index"] == 1
    assert fields["gcd"] == 2
    assert fields["predicted_reach"] == 5
    assert fields["full_coverage"] is False
    assert fields["orbit"] == [1, 5, 9, 3, 7]
    assert fields["candidate_path"] == [7, 3, 9, 5, 1, 7, 3, 9]
    assert fields["candidate_budget"] == 8
    assert fields["unique_candidate_count"] == 5
    assert fields["effective_candidate_budget"] == 5
    assert fields["duplicate_count"] == 3
    assert fields["candidate_budget_accounting"] is True
    assert fields["effective_budget_matches_unique_candidates"] is True
    assert fields["candidate_budget_shortfall"] == 0
    assert fields["effective_budget_reaches_predicted_reach"] is True


def test_strided_candidate_fanout_certifier_rejects_negative_stride() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--stride",
            "-1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--stride must be nonnegative" in result.stderr
