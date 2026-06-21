from __future__ import annotations

import hashlib
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
CONTRACT_PACK = Path("site") / "data" / "generated" / "circle_ai_contract_pack.json"
FINGERPRINT_ALGORITHM = "sha256-json-v1"
FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}


def _runner_check_schema() -> dict:
    return json.loads(RUNNER_CHECK_SCHEMA.read_text())


def _strip_fingerprint_fields(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in sorted(value.items())
            if key not in FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_fingerprint(value: object) -> str:
    normalized = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _refresh_pack_fingerprints(pack: dict) -> None:
    for contract in pack["contracts"]:
        contract["content_fingerprint_algorithm"] = FINGERPRINT_ALGORITHM
        contract["content_fingerprint"] = _json_fingerprint(contract)
    pack["contract_fingerprint_index"] = {
        contract["kind"]: {
            "id": contract["id"],
            "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "content_fingerprint": contract["content_fingerprint"],
        }
        for contract in pack["contracts"]
    }
    pack["content_fingerprint_algorithm"] = FINGERPRINT_ALGORITHM
    pack["pack_content_fingerprint"] = _json_fingerprint(pack)


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


def test_check_circle_ai_contract_runner_rejects_pack_missing_receipt_theorem(
    tmp_path: Path,
) -> None:
    pack = json.loads(CONTRACT_PACK.read_text())
    kv_contract = next(
        contract
        for contract in pack["contracts"]
        if contract["kind"] == "kv_cache_ring_buffer"
    )
    theorem_ids = kv_contract["theorem_ids"]
    assert "AIM-T0060" in theorem_ids
    kv_contract["theorem_ids"] = [
        theorem_id for theorem_id in theorem_ids if theorem_id != "AIM-T0060"
    ]
    _refresh_pack_fingerprints(pack)
    stale_pack = tmp_path / "kv_missing_theorem_pack.json"
    stale_pack.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--pack",
            str(stale_pack),
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
    assert any(
        "receipt theorem ids are not in loaded contract: AIM-T0060" in failure
        for failure in payload["failures"]
    )
