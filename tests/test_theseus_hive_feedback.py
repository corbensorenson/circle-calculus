from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from circle_math.applications.theseus_hive_feedback import import_feedback_summary, validate_feedback_summary


def feedback_payload() -> dict:
    return {
        "schema_id": "theseus_hive.circle_ai_feedback_summary.v0",
        "policy": "theseus_hive_circle_ai_feedback_summary_v0",
        "trigger_state": "GREEN",
        "ok": True,
        "claim_boundary": "aggregate feedback only",
        "public_calibration_used": False,
        "private_data_exported": False,
        "external_inference_calls": 0,
        "training_mutation": False,
        "promotion_evidence": False,
        "summary": {
            "expected_report_count": 6,
            "required_report_count": 5,
            "present_report_count": 5,
            "required_present_report_count": 5,
            "safe_to_import": True,
            "advantage_claim_ready": False,
            "learned_model_quality_metrics_present": False,
            "private_data_exported": False,
            "external_inference_calls": 0,
            "promotion_evidence": False,
        },
        "reports": [
            {
                "report_id": "contract_consumer",
                "path": "reports/circle_ai_contract_consumer.json",
                "exists": True,
                "data_gated": False,
                "content_exported": False,
                "trigger_state": "YELLOW",
                "ok": True,
                "safe_to_import": True,
                "external_inference_calls": 0,
                "private_data_exported": False,
                "promotion_evidence": False,
                "safe_summary": {
                    "contract_count": 6,
                    "implemented_families": ["recurrence_schedule", "multicoil_phase_feature"],
                    "learned_model_quality_metrics_present": False,
                },
            }
        ],
        "governance_gates": [
            {"gate": "private_data_export_absent", "passed": True},
            {"gate": "external_inference_calls_zero", "passed": True},
        ],
    }


def test_public_safe_feedback_import_keeps_claim_boundary() -> None:
    payload = feedback_payload()
    validate_feedback_summary(payload)
    imported = import_feedback_summary(payload, source_path="../Theseus-Hive/reports/circle_ai_feedback_summary.json")
    assert imported["schema_id"] == "circle_calculus.theseus_hive_ai_feedback_import.v0"
    assert imported["import_state"] == "imported"
    assert imported["private_data_exported"] is False
    assert imported["external_inference_calls"] == 0
    assert imported["promotion_evidence"] is False
    assert imported["advantage_claim_ready"] is False
    assert "not model-quality" in imported["claim_boundary"]
    assert imported["reports"][0]["safe_summary"]["contract_count"] == 6


def test_feedback_import_rejects_private_export_and_unsafe_summary_keys() -> None:
    payload = feedback_payload()
    payload["private_data_exported"] = True
    with pytest.raises(ValueError):
        validate_feedback_summary(payload)

    payload = feedback_payload()
    payload["reports"][0]["safe_summary"]["private_payload_text"] = 1
    with pytest.raises(ValueError):
        validate_feedback_summary(payload)


def test_feedback_import_script_writes_placeholder_for_missing_input(tmp_path: Path) -> None:
    out = tmp_path / "feedback.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/import_theseus_hive_ai_feedback.py",
            "--input",
            str(tmp_path / "missing.json"),
            "--out",
            str(out),
        ],
        check=True,
    )
    data = json.loads(out.read_text())
    assert data["import_state"] == "missing"
    assert data["private_data_exported"] is False
    assert data["advantage_claim_ready"] is False
