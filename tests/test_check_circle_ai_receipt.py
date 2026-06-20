from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications import build_rope_receipt, load_contract_pack


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
    assert payload["schema_id"] == "circle_calculus.ai_contract_receipt_file_check.v0"
    assert payload["ok"] is True
    assert payload["receipt_count"] == 1
    assert payload["summaries"][0]["kind"] == "rope_position_distinguishability"
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
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["failure_count"] == 1
    assert "did not match required status set" in payload["failures"][0]


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
    assert result.returncode == 1
    assert payload["ok"] is False
    assert "does not match loaded contract pack" in payload["failures"][0]
