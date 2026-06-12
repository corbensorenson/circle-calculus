"""Public-safe Theseus-Hive feedback summary validation.

Theseus-Hive may emit aggregate Circle AI feedback reports from private local
runs. Circle Calculus can import only the sanitized summary, never raw private
reports, row bodies, labels, prompts, model weights, or promotion evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any


THESEUS_FEEDBACK_SCHEMA_ID = "theseus_hive.circle_ai_feedback_summary.v0"
CIRCLE_IMPORT_SCHEMA_ID = "circle_calculus.theseus_hive_ai_feedback_import.v0"
SAFE_STRING_LIST_VALUES = {
    "recurrence_schedule",
    "strided_candidate_fanout",
    "cyclic_memory_residue_winding",
    "multicoil_phase_feature",
    "circulant_block_cyclic_mixer",
    "seed_rule_exact_regeneration",
}
CLAIM_BOUNDARY = (
    "Imported Theseus-Hive feedback is aggregate report metadata only. It is not "
    "model-quality, reasoning, speed, context-length, transfer, promotion, or ASI evidence."
)


def import_feedback_summary(payload: dict[str, Any] | None, *, source_path: str = "") -> dict[str, Any]:
    """Return a Circle-side public-safe imported feedback summary.

    If ``payload`` is None, return a placeholder that records that no private-safe
    feedback handoff has been imported yet.
    """
    if payload is None:
        return placeholder_feedback_summary(source_path=source_path)
    validate_feedback_summary(payload)
    return {
        "schema_id": CIRCLE_IMPORT_SCHEMA_ID,
        "source_schema_id": payload.get("schema_id"),
        "source_policy": payload.get("policy", ""),
        "source_path": source_path,
        "import_state": "imported",
        "created_utc": str(payload.get("created_utc") or ""),
        "trigger_state": payload.get("trigger_state", "YELLOW"),
        "claim_boundary": CLAIM_BOUNDARY,
        "private_data_exported": False,
        "external_inference_calls": 0,
        "training_mutation": False,
        "promotion_evidence": False,
        "advantage_claim_ready": False,
        "summary": dict(payload.get("summary", {})),
        "reports": [public_report_row(row) for row in payload.get("reports", [])],
        "governance_gates": [
            {"gate": "source_feedback_schema_valid", "passed": True},
            {"gate": "private_data_export_absent", "passed": True},
            {"gate": "external_inference_calls_zero", "passed": True},
            {"gate": "promotion_evidence_absent", "passed": True},
            {"gate": "feedback_not_upgraded_to_claim", "passed": True},
        ],
    }


def placeholder_feedback_summary(*, source_path: str = "") -> dict[str, Any]:
    return {
        "schema_id": CIRCLE_IMPORT_SCHEMA_ID,
        "source_schema_id": THESEUS_FEEDBACK_SCHEMA_ID,
        "source_policy": "",
        "source_path": source_path,
        "import_state": "missing",
        "created_utc": "",
        "trigger_state": "YELLOW",
        "claim_boundary": CLAIM_BOUNDARY,
        "private_data_exported": False,
        "external_inference_calls": 0,
        "training_mutation": False,
        "promotion_evidence": False,
        "advantage_claim_ready": False,
        "summary": {
            "expected_report_count": 6,
            "required_report_count": 5,
            "present_report_count": 0,
            "required_present_report_count": 0,
            "safe_to_import": True,
            "advantage_claim_ready": False,
            "learned_model_quality_metrics_present": False,
            "private_data_exported": False,
            "external_inference_calls": 0,
            "promotion_evidence": False,
        },
        "reports": [],
        "governance_gates": [
            {"gate": "source_feedback_schema_valid", "passed": False},
            {"gate": "private_data_export_absent", "passed": True},
            {"gate": "external_inference_calls_zero", "passed": True},
            {"gate": "promotion_evidence_absent", "passed": True},
            {"gate": "feedback_not_upgraded_to_claim", "passed": True},
        ],
    }


def validate_feedback_summary(payload: dict[str, Any]) -> None:
    if payload.get("schema_id") != THESEUS_FEEDBACK_SCHEMA_ID:
        raise ValueError("unknown Theseus-Hive feedback schema")
    if payload.get("private_data_exported") is not False:
        raise ValueError("feedback summary reports private data export")
    if int_like(payload.get("external_inference_calls")) != 0:
        raise ValueError("feedback summary reports external inference")
    if payload.get("training_mutation") is not False:
        raise ValueError("feedback summary reports training mutation")
    if payload.get("promotion_evidence") is not False:
        raise ValueError("feedback summary reports promotion evidence")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("feedback summary missing summary object")
    if summary.get("private_data_exported") is not False:
        raise ValueError("summary reports private data export")
    if int_like(summary.get("external_inference_calls")) != 0:
        raise ValueError("summary reports external inference")
    if summary.get("promotion_evidence") is not False:
        raise ValueError("summary reports promotion evidence")
    if summary.get("advantage_claim_ready") is not False:
        raise ValueError("feedback cannot be imported as an advantage claim")
    reports = payload.get("reports")
    if not isinstance(reports, list):
        raise ValueError("feedback summary missing report list")
    for row in reports:
        validate_report_row(row)


def validate_report_row(row: Any) -> None:
    if not isinstance(row, dict):
        raise ValueError("report row is not an object")
    path = str(row.get("path") or "")
    if path and not safe_report_path(path):
        raise ValueError(f"unsafe report path: {path}")
    if row.get("content_exported") is not False:
        raise ValueError("report row exports content")
    if row.get("safe_to_import") is False:
        raise ValueError("report row is marked unsafe")
    if row.get("private_data_exported") not in {None, False}:
        raise ValueError("report row exports private data")
    if int_like(row.get("external_inference_calls")) != 0:
        raise ValueError("report row reports external inference")
    if row.get("promotion_evidence") not in {None, False}:
        raise ValueError("report row reports promotion evidence")
    safe_summary = row.get("safe_summary", {})
    if not isinstance(safe_summary, dict):
        raise ValueError("report row safe_summary is not an object")
    for key, value in safe_summary.items():
        if not safe_summary_key(key):
            raise ValueError(f"unsafe safe_summary key: {key}")
        if not safe_summary_value(value):
            raise ValueError(f"unsafe safe_summary value for {key}")


def public_report_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_id": str(row.get("report_id") or ""),
        "path": str(row.get("path") or ""),
        "exists": bool(row.get("exists")),
        "data_gated": bool(row.get("data_gated")),
        "trigger_state": str(row.get("trigger_state") or ""),
        "ok": row.get("ok") if isinstance(row.get("ok"), bool) else None,
        "safe_summary": dict(row.get("safe_summary", {})),
    }


def safe_report_path(path: str) -> bool:
    normalized = PurePosixPath(path.replace("\\", "/"))
    parts = normalized.parts
    return bool(parts) and parts[0] == "reports" and ".." not in parts


def safe_summary_key(key: Any) -> bool:
    text = str(key).lower()
    blocked = ["prompt", "body", "content", "label", "text", "packet", "payload", "candidate_code", "weight"]
    return not any(part in text for part in blocked)


def safe_summary_value(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return True
    if isinstance(value, int):
        return True
    if isinstance(value, float):
        return True
    if isinstance(value, list):
        return all(isinstance(item, str) and item in SAFE_STRING_LIST_VALUES for item in value)
    return False


def int_like(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
