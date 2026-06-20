from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema


RUNNER_CHECK_SCHEMA = (
    Path("site")
    / "data"
    / "generated"
    / "circle_ai_contract_runner_check.schema.json"
)


def _runner_check_schema() -> dict:
    return json.loads(RUNNER_CHECK_SCHEMA.read_text())


def test_check_circle_ai_contract_runner_accepts_examples() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_circle_ai_contract_runner.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI runner examples ok=True examples=4 failures=0" in result.stdout
    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=kv_cache_ring_buffer" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "kind=recurrence_schedule" in result.stdout


def test_check_circle_ai_contract_runner_emits_json_report() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, _runner_check_schema())
    assert payload["schema_id"] == "circle_calculus.ai_contract_runner_check.v0"
    assert payload["ok"] is True
    assert payload["example_count"] == 4
    assert payload["failure_count"] == 0
    assert payload["failures"] == []
    assert all(
        len(summary["request_content_fingerprint"]) == 64
        for summary in payload["summaries"]
    )


def test_check_circle_ai_contract_runner_writes_receipts(tmp_path: Path) -> None:
    out_dir = tmp_path / "receipts"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--receipt-out-dir",
            str(out_dir),
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, _runner_check_schema())
    receipt_paths = [Path(summary["receipt_path"]) for summary in payload["summaries"]]
    assert len(receipt_paths) == 4
    assert all(path.exists() for path in receipt_paths)
    for path in receipt_paths:
        receipt = json.loads(path.read_text())
        assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
        assert len(receipt["receipt_content_fingerprint"]) == 64
        assert receipt["proof_status"]["all_theorem_ids_proved"] is True
