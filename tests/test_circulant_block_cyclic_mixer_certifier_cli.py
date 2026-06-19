from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "circulant_block_cyclic_mixer_certify.py"


def test_circulant_block_cyclic_mixer_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "mixer_contract.json"
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
        "circulant_block_cyclic_mixer_contract=READY period=8 "
        "channel_count=128 block_size=8"
    ) in result.stdout
    assert (
        "circulant_parity=output_parity=True max_abs_dense_delta=0 "
        "circulant_output=(5, -2, -8, 9, -1, 6, -1, -8) "
        "dense_output=(5, -2, -8, 9, -1, 6, -1, -8) "
        "theorems=AIT-T0006,AIT-T0007,AIT-T0008,AIT-T0009"
    ) in result.stdout
    assert (
        "circulant_parameters=circulant_parameters=8 dense_parameters=64 "
        "circulant_parameter_ratio=0.125"
    ) in result.stdout
    assert (
        "block_cyclic_accounting=dense_adapter_parameters=2048 "
        "lora_parameters=576 block_cyclic_parameters=128 "
        "block_to_dense_ratio=0.0625 block_loads=(16, 16, 16, 16, 16, 16, 16, 16) "
        "theorems=AIRA-T0001,AIRA-T0002,AIRA-T0004"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-MIXER-001"
    assert payload["kind"] == "circulant_block_cyclic_mixer"
    assert payload["contract_passed"] is True
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert (
        "docs/CIRCULANT_BLOCK_CYCLIC_MIXER_CERTIFIER_QUICKSTART.md"
        in payload["quickstart_docs"]
    )
    assert "python scripts/circulant_block_cyclic_mixer_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["period"] == 8
    assert fields["channel_count"] == 128
    assert fields["block_size"] == 8
    assert fields["circulant_output"] == fields["dense_output"]
    assert fields["max_abs_dense_delta"] == 0
    assert fields["circulant_parameters"] == 8
    assert fields["dense_parameters"] == 64
    assert fields["circulant_parameter_ratio"] == 0.125
    assert fields["dense_adapter_parameters"] == 2048
    assert fields["lora_parameters"] == 576
    assert fields["block_cyclic_parameters"] == 128
    assert fields["block_to_dense_ratio"] == 0.0625
    assert fields["block_loads"] == [16, 16, 16, 16, 16, 16, 16, 16]
    assert {"AIT-T0006", "AIT-T0007", "AIT-T0008", "AIT-T0009"} <= set(
        payload["theorem_ids"]
    )
    assert {"AIRA-T0001", "AIRA-T0002", "AIRA-T0004"} <= set(payload["theorem_ids"])


def test_circulant_block_cyclic_mixer_certifier_cli_json_custom_fixture() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--period",
            "4",
            "--channel-count",
            "16",
            "--block-size",
            "4",
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
    assert fields["period"] == 4
    assert fields["channel_count"] == 16
    assert fields["block_size"] == 4
    assert fields["circulant_output"] == [-5, 8, -2, 5]
    assert fields["dense_output"] == [-5, 8, -2, 5]
    assert fields["max_abs_dense_delta"] == 0
    assert fields["circulant_parameters"] == 4
    assert fields["dense_parameters"] == 16
    assert fields["circulant_parameter_ratio"] == 0.25
    assert fields["dense_adapter_parameters"] == 256
    assert fields["lora_parameters"] == 128
    assert fields["block_cyclic_parameters"] == 64
    assert fields["block_to_dense_ratio"] == 0.25
    assert fields["block_loads"] == [4, 4, 4, 4]


def test_circulant_block_cyclic_mixer_rejects_block_larger_than_channels() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--channel-count",
            "4",
            "--block-size",
            "8",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--block-size must be less than or equal to --channel-count" in result.stderr
