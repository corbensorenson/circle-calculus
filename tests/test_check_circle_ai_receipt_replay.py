from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

from circle_math.applications import (
    build_contract_receipt_replay_check_json_schema,
    build_rope_receipt,
    load_contract_pack,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_circle_ai_receipt_replay.py"
PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"


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

    payload = json.dumps(
        strip(receipt),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _write_receipt(path: Path, receipt: dict) -> None:
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")


def test_check_circle_ai_receipt_replay_accepts_saved_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "rope_receipt.json"
    report_path = tmp_path / "rope_replay_report.json"
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=load_contract_pack(PACK),
    )
    _write_receipt(receipt_path, receipt)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(receipt_path),
            "--report-out",
            str(report_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, build_contract_receipt_replay_check_json_schema())
    assert payload["ok"] is True
    assert payload["replay_command"] == receipt["validation_commands"][0]
    assert payload["replay_command_matches_request"] is True
    assert payload["package_replay_command"] == receipt["validation_commands"][1]
    assert payload["package_replay_command_matches_request"] is True
    assert payload["comparison"]["all_replay_fields_match"] is True
    assert payload["original"]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )
    assert payload["replayed"]["receipt_content_fingerprint"] == (
        receipt["receipt_content_fingerprint"]
    )
    assert json.loads(report_path.read_text()) == payload


def test_check_circle_ai_receipt_replay_rejects_stale_saved_receipt(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "stale_rope_receipt.json"
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=load_contract_pack(PACK),
    )
    receipt["evidence"]["exact_common_collision_gap"] = -1
    receipt["receipt_content_fingerprint"] = _receipt_fingerprint(receipt)
    _write_receipt(receipt_path, receipt)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(receipt_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, build_contract_receipt_replay_check_json_schema())
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["comparison"]["receipt_content_fingerprint_matches"] is False
    assert any(
        "receipt replay mismatch: receipt_content_fingerprint" in failure
        for failure in payload["failures"]
    )
