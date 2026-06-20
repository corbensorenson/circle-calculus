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

    assert "circle AI runner examples ok=True examples=5 failures=0" in result.stdout
    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=kv_cache_ring_buffer" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "kind=recurrence_schedule" in result.stdout
    assert "type=model_config" in result.stdout


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
    assert payload["example_count"] == 5
    assert payload["failure_count"] == 0
    assert payload["failures"] == []
    assert payload["gate_policy"] == {
        "allowed_statuses": [],
        "require_passed": False,
    }
    assert all(
        len(summary["request_content_fingerprint"]) == 64
        for summary in payload["summaries"]
    )
    assert {summary["source_type"] for summary in payload["summaries"]} == {
        "request",
        "model_config",
    }


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
    assert len(receipt_paths) == 5
    assert all(path.exists() for path in receipt_paths)
    for path in receipt_paths:
        receipt = json.loads(path.read_text())
        assert receipt["schema_id"] == "circle_calculus.ai_contract_receipt.v0"
        assert len(receipt["receipt_content_fingerprint"]) == 64
        assert receipt["proof_status"]["all_theorem_ids_proved"] is True


def test_check_circle_ai_contract_runner_writes_report_file(tmp_path: Path) -> None:
    report_path = tmp_path / "runner_check_report.json"
    receipt_dir = tmp_path / "receipts"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--receipt-out-dir",
            str(receipt_dir),
            "--report-out",
            str(report_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI runner examples ok=True examples=5 failures=0" in result.stdout
    payload = json.loads(report_path.read_text())
    jsonschema.validate(payload, _runner_check_schema())
    assert payload["ok"] is True
    assert len(payload["summaries"]) == 5
    assert all(summary["receipt_path"] for summary in payload["summaries"])
    model_config_summary = next(
        summary
        for summary in payload["summaries"]
        if summary["source_type"] == "model_config"
    )
    assert model_config_summary["request_path"]


def test_check_circle_ai_contract_runner_accepts_batch_gate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--require-status",
            "proved",
            "--require-passed",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, _runner_check_schema())
    assert payload["ok"] is True
    assert payload["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "require_passed": True,
    }
    assert payload["example_count"] == 5


def test_check_circle_ai_contract_runner_rejects_batch_gate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--require-status",
            "impossible",
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(payload, _runner_check_schema())
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["gate_policy"] == {
        "allowed_statuses": ["impossible"],
        "require_passed": False,
    }
    assert payload["failure_count"] == 5
    assert all("did not match required status set" in failure for failure in payload["failures"])
