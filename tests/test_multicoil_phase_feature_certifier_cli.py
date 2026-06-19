from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "multicoil_phase_feature_certify.py"


def test_multicoil_phase_feature_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "multicoil_phase_feature_contract.json"
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
        "multicoil_phase_feature_contract=READY periods=(5, 7) position=37 "
        "phase_tuple=(2, 2) joint_repeat_horizon=35"
    ) in result.stdout
    assert (
        "joint_shift=shifted_position=72 shifted_phase_tuple=(2, 2) "
        "phase_invariant=True theorems=AIA-T0001,AIA-T0002,AIA-T0004"
    ) in result.stdout
    assert (
        "relative_phase=query_position=41 key_position=18 relative_period=5 "
        "relative_phase=3 shifted_relative_phase=3 relative_phase_invariant=True "
        "theorems=AIT-T0004,AIT-T0005"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-PHASE-FEATURE-001"
    assert payload["kind"] == "multicoil_phase_feature"
    assert payload["contract_passed"] is True
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert (
        "docs/MULTICOIL_PHASE_FEATURE_CERTIFIER_QUICKSTART.md"
        in payload["quickstart_docs"]
    )
    assert "python scripts/multicoil_phase_feature_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["periods"] == [5, 7]
    assert fields["position"] == 37
    assert fields["phase_tuple"] == [2, 2]
    assert fields["joint_repeat_horizon"] == 35
    assert fields["shifted_position"] == 72
    assert fields["shifted_phase_tuple"] == [2, 2]
    assert fields["relative_period"] == 5
    assert fields["relative_phase"] == 3
    assert fields["shifted_relative_phase"] == 3
    assert {"AIA-T0001", "AIA-T0002", "AIA-T0004", "AIT-T0004", "AIT-T0005"} <= set(
        payload["theorem_ids"]
    )


def test_multicoil_phase_feature_certifier_cli_json_custom_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--periods",
            "4,6",
            "--position",
            "10",
            "--query-position",
            "17",
            "--key-position",
            "5",
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
    assert fields["periods"] == [4, 6]
    assert fields["position"] == 10
    assert fields["phase_tuple"] == [2, 4]
    assert fields["joint_repeat_horizon"] == 12
    assert fields["shifted_position"] == 22
    assert fields["shifted_phase_tuple"] == [2, 4]
    assert fields["relative_period"] == 4
    assert fields["relative_phase"] == 0
    assert fields["shifted_relative_phase"] == 0


def test_multicoil_phase_feature_certifier_rejects_nonpositive_period() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--periods",
            "5,0",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "all periods must be positive" in result.stderr
