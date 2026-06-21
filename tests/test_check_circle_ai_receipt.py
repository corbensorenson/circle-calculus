from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

from circle_math.applications import (
    build_contract_receipt_file_check_json_schema,
    build_rope_receipt,
    load_contract_pack,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_circle_ai_receipt.py"
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


def test_check_circle_ai_receipt_accepts_saved_receipt(tmp_path: Path) -> None:
    receipt_path = tmp_path / "rope_receipt.json"
    report_path = tmp_path / "receipt_check_report.json"
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
            "--require-status",
            "proved",
            "--require-decision",
            "passed",
            "--require-assurance",
            "mixed_theorem_and_computation",
            "--require-passed",
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
    schema = build_contract_receipt_file_check_json_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(payload, schema)
    assert payload["schema_id"] == "circle_calculus.ai_contract_receipt_file_check.v0"
    assert payload["ok"] is True
    assert payload["receipt_count"] == 1
    assert payload["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    assert payload["summaries"][0]["kind"] == "rope_position_distinguishability"
    assert payload["summaries"][0]["decision_verdict"] == receipt["decision"][
        "verdict"
    ]
    assert payload["summaries"][0]["decision_assurance"] == receipt["decision"][
        "assurance"
    ]
    assert payload["summaries"][0]["normalized_request"] == receipt[
        "normalized_request"
    ]
    assert payload["summaries"][0]["request_content_fingerprint"] == receipt[
        "request_content_fingerprint"
    ]
    assert payload["summaries"][0]["normalized_request_fingerprint"] == receipt[
        "normalized_request_fingerprint"
    ]
    assert payload["summaries"][0]["receipt_content_fingerprint"] == receipt[
        "receipt_content_fingerprint"
    ]
    assert json.loads(report_path.read_text()) == payload


def test_check_circle_ai_receipt_rejects_status_gate(tmp_path: Path) -> None:
    receipt_path = tmp_path / "rope_impossible_receipt.json"
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328458",
        pack=load_contract_pack(PACK),
    )
    _write_receipt(receipt_path, receipt)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(receipt_path),
            "--require-status",
            "proved",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, build_contract_receipt_file_check_json_schema())
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["failure_count"] == 1
    assert "did not match required status set" in payload["failures"][0]


def test_check_circle_ai_receipt_rejects_decision_gate(tmp_path: Path) -> None:
    receipt_path = tmp_path / "rope_receipt.json"
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
            "--require-decision",
            "failed",
            "--require-assurance",
            "theorem_backed",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, build_contract_receipt_file_check_json_schema())
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["failure_count"] == 2
    assert any(
        "did not match required decision set" in failure
        for failure in payload["failures"]
    )
    assert any(
        "did not match required assurance set" in failure
        for failure in payload["failures"]
    )


def test_check_circle_ai_receipt_rejects_stale_pack_fingerprint(
    tmp_path: Path,
) -> None:
    receipt_path = tmp_path / "stale_receipt.json"
    receipt = build_rope_receipt(
        context=131072,
        requested_margin="1/328459",
        pack=load_contract_pack(PACK),
    )
    receipt["support"]["contract_pack_fingerprint"] = "0" * 64
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
    jsonschema.validate(payload, build_contract_receipt_file_check_json_schema())
    assert result.returncode == 1
    assert payload["ok"] is False
    assert "does not match loaded contract pack" in payload["failures"][0]
