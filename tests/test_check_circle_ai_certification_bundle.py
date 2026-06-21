from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

from circle_math.applications import (
    build_contract_certification_bundle,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_request,
    build_rope_model_config_import_report,
    load_contract_pack,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_circle_ai_certification_bundle.py"
PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
STANDARD_ROPE_MODEL_CONFIG = (
    ROOT / "examples" / "circle_ai_model_configs" / "standard_rope_config.json"
)


def _write_bundle(path: Path, bundle: dict) -> None:
    path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n")


def test_check_circle_ai_certification_bundle_accepts_model_config_bundle(
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "rope_certification_bundle.json"
    report_path = tmp_path / "bundle_check_report.json"
    pack = load_contract_pack(PACK)
    import_report = build_rope_model_config_import_report(
        json.loads(STANDARD_ROPE_MODEL_CONFIG.read_text(encoding="utf-8")),
        requested_margin="1/328459",
    )
    bundle = build_contract_certification_bundle(
        import_report["request"],
        pack=pack,
        model_config_import_report=import_report,
        required_statuses=("proved",),
        required_decision_verdicts=("passed",),
        required_assurance_levels=("mixed_theorem_and_computation",),
        require_passed=True,
    )
    _write_bundle(bundle_path, bundle)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(bundle_path),
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
    jsonschema.validate(
        payload,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    assert payload["schema_id"] == (
        "circle_calculus.ai_contract_certification_bundle_file_check.v0"
    )
    assert payload["ok"] is True
    assert payload["bundle_count"] == 1
    assert payload["failure_count"] == 0
    assert payload["gate_policy"] == {
        "allowed_statuses": ["proved"],
        "allowed_decision_verdicts": ["passed"],
        "allowed_assurance_levels": ["mixed_theorem_and_computation"],
        "require_passed": True,
    }
    summary = payload["summaries"][0]
    assert summary["path"] == str(bundle_path)
    assert summary["kind"] == "rope_position_distinguishability"
    assert summary["has_model_config_import_report"] is True
    assert summary["model_config_fingerprint"] == import_report[
        "model_config_fingerprint"
    ]
    assert summary["bundle_request_content_fingerprint"] == bundle[
        "request_content_fingerprint"
    ]
    assert summary["receipt_content_fingerprint"] == bundle[
        "receipt_content_fingerprint"
    ]
    assert json.loads(report_path.read_text()) == payload


def test_check_circle_ai_certification_bundle_rejects_status_gate(
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "rope_impossible_certification_bundle.json"
    pack = load_contract_pack(PACK)
    request = build_contract_request(
        "rope",
        {
            "context": 131072,
            "requested_margin": "1/328458",
        },
    )
    bundle = build_contract_certification_bundle(request, pack=pack)
    _write_bundle(bundle_path, bundle)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(bundle_path),
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
    jsonschema.validate(
        payload,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    assert result.returncode == 1
    assert payload["ok"] is False
    assert payload["failure_count"] == 1
    assert "did not match required status set" in payload["failures"][0]


def test_check_circle_ai_certification_bundle_rejects_tampered_fingerprint(
    tmp_path: Path,
) -> None:
    bundle_path = tmp_path / "tampered_certification_bundle.json"
    pack = load_contract_pack(PACK)
    request = build_contract_request(
        "rope",
        {
            "context": 131072,
            "requested_margin": "1/328459",
        },
    )
    bundle = build_contract_certification_bundle(request, pack=pack)
    bundle["receipt_content_fingerprint"] = "0" * 64
    _write_bundle(bundle_path, bundle)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(bundle_path),
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    jsonschema.validate(
        payload,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    assert result.returncode == 1
    assert payload["ok"] is False
    assert any(
        "receipt_content_fingerprint does not match bundle" in failure
        for failure in payload["failures"]
    )
