from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cyclic_memory_certify.py"


def test_cyclic_memory_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "cyclic_memory_contract.json"
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
        "cyclic_memory_contract=READY bank_size=8 event_index=23 "
        "event_count=32 residue_slot=7 winding=2"
    ) in result.stdout
    assert (
        "alias_class=same_residue_events=(7, 15, 23, 31) "
        "same_residue_windings=(0, 1, 2, 3) max_alias_load=4 "
        "theorems=AIM-T0001,AIM-T0002,AIM-T0004,AIM-T0005"
    ) in result.stdout
    assert (
        "reconstruction=event_index=23 winding_times_bank_plus_residue=23 "
        "exact=True"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-MEMORY-001"
    assert payload["kind"] == "cyclic_memory_residue_winding"
    assert payload["contract_passed"] is True
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert "docs/CYCLIC_MEMORY_CERTIFIER_QUICKSTART.md" in payload["quickstart_docs"]
    assert "python scripts/cyclic_memory_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["bank_size"] == 8
    assert fields["event_index"] == 23
    assert fields["event_count"] == 32
    assert fields["residue_slot"] == 7
    assert fields["winding"] == 2
    assert fields["same_residue_events"] == [7, 15, 23, 31]
    assert fields["same_residue_windings"] == [0, 1, 2, 3]
    assert fields["max_alias_load"] == 4
    assert {"AIM-T0001", "AIM-T0002", "AIM-T0004", "AIM-T0005"} <= set(
        payload["theorem_ids"]
    )


def test_cyclic_memory_certifier_cli_json_custom_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bank-size",
            "5",
            "--event-index",
            "12",
            "--event-count",
            "20",
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
    assert fields["bank_size"] == 5
    assert fields["event_index"] == 12
    assert fields["event_count"] == 20
    assert fields["residue_slot"] == 2
    assert fields["winding"] == 2
    assert fields["same_residue_events"] == [2, 7, 12, 17]
    assert fields["same_residue_windings"] == [0, 1, 2, 3]
    assert fields["max_alias_load"] == 4


def test_cyclic_memory_certifier_rejects_out_of_trace_event() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bank-size",
            "5",
            "--event-index",
            "20",
            "--event-count",
            "20",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--event-index must be less than --event-count" in result.stderr
