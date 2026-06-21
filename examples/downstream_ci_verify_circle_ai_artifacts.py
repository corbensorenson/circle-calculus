#!/usr/bin/env python3
"""Standalone downstream CI gate for Circle AI runner artifact manifests.

This example intentionally uses only the Python standard library. A downstream
project can copy it next to emitted ``*_artifact_manifest.json`` files and fail
CI when a receipt artifact is missing, stale, schema-mismatched, or outside the
consumer's accepted proof-status policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_ID = "circle_calculus.ai_contract_artifact_manifest.v0"
MANIFEST_CHECK_SCHEMA_ID = (
    "circle_calculus.ai_contract_artifact_manifest_file_check.v0"
)
EXAMPLE_SCHEMA_ID = "circle_calculus.downstream_ci_artifact_acceptance.v0"
FAILURE_SCHEMA_ID = "circle_calculus.downstream_ci_artifact_rejection.v0"
FINGERPRINT_ALGORITHM = "sha256-file-v1"
SUPPORTED_STATUSES = {
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
}
SUPPORTED_DECISIONS = {
    "passed",
    "failed",
    "undecided",
    "numerical_only",
    "outside_scope",
}
SUPPORTED_ASSURANCES = {
    "theorem_backed",
    "mixed_theorem_and_computation",
    "numerical_only",
    "unsupported",
    "undecided",
}
EXPECTED_SCHEMA_BY_LABEL = {
    "request_json": "circle_calculus.ai_contract_request.v0",
    "request_validation_report": "circle_calculus.ai_contract_request_validation.v0",
    "model_config_import_report": "circle_calculus.rope_model_config_import.v0",
    "receipt_json": "circle_calculus.ai_contract_receipt.v0",
    "receipt_check": "circle_calculus.ai_contract_receipt_file_check.v0",
    "gate_report": "circle_calculus.ai_contract_receipt_file_check.v0",
    "certification_bundle": "circle_calculus.ai_contract_certification_bundle.v0",
    "certification_bundle_check": (
        "circle_calculus.ai_contract_certification_bundle_file_check.v0"
    ),
}


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _short(value: object) -> str | None:
    return value[:12] if isinstance(value, str) else None


def _resolve_candidates(
    raw_path: str,
    *,
    manifest_path: Path,
    base_dir: Path | None,
) -> list[Path]:
    path = Path(raw_path)
    candidates = [path]
    if not path.is_absolute():
        candidates.extend([Path.cwd() / path, manifest_path.parent / path])
        if base_dir is not None:
            candidates.append(base_dir / path)
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def _resolve_existing_artifact(
    raw_path: str,
    *,
    manifest_path: Path,
    base_dir: Path | None,
) -> Path | None:
    for candidate in _resolve_candidates(
        raw_path,
        manifest_path=manifest_path,
        base_dir=base_dir,
    ):
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _load_schema_id(path: Path) -> str | None:
    try:
        payload = _load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    schema_id = payload.get("schema_id")
    return schema_id if isinstance(schema_id, str) else None


def _manifest_check_path(manifest_path: Path) -> Path:
    name = manifest_path.name
    if name.endswith("_artifact_manifest.json"):
        return manifest_path.with_name(
            name.removesuffix("_artifact_manifest.json")
            + "_artifact_manifest_check.json"
        )
    return manifest_path.with_name(manifest_path.stem + "_check.json")


def _check_policy_values(
    *,
    statuses: list[str],
    decisions: list[str],
    assurances: list[str],
) -> None:
    unknown_statuses = sorted(set(statuses) - SUPPORTED_STATUSES)
    unknown_decisions = sorted(set(decisions) - SUPPORTED_DECISIONS)
    unknown_assurances = sorted(set(assurances) - SUPPORTED_ASSURANCES)
    if unknown_statuses:
        raise ValueError(f"unsupported required statuses: {unknown_statuses}")
    if unknown_decisions:
        raise ValueError(f"unsupported required decisions: {unknown_decisions}")
    if unknown_assurances:
        raise ValueError(f"unsupported required assurances: {unknown_assurances}")


def _parse_normalized_param_pin(raw: str) -> tuple[str, Any]:
    if "=" not in raw:
        raise ValueError(
            "--require-normalized-param must be KEY=JSON_VALUE, for example "
            "head_dim=128"
        )
    key, raw_value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError("--require-normalized-param key must be non-empty")
    raw_value = raw_value.strip()
    if not raw_value:
        raise ValueError("--require-normalized-param value must be non-empty")
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        value = raw_value
    return key, value


def _artifact_report(
    artifact: dict[str, Any],
    *,
    manifest_path: Path,
    base_dir: Path | None,
) -> dict[str, Any]:
    failures: list[str] = []
    label = artifact.get("label")
    raw_path = artifact.get("path")
    declared_sha256 = artifact.get("sha256")
    declared_exists = artifact.get("exists")
    declared_schema = artifact.get("content_schema_id")
    expected_schema = EXPECTED_SCHEMA_BY_LABEL.get(label)
    resolved_path: Path | None = None
    actual_sha256: str | None = None
    actual_schema: str | None = None

    if not isinstance(label, str) or not label:
        failures.append("artifact label must be a non-empty string")
    if not isinstance(raw_path, str) or not raw_path:
        failures.append("artifact path must be a non-empty string")
    else:
        resolved_path = _resolve_existing_artifact(
            raw_path,
            manifest_path=manifest_path,
            base_dir=base_dir,
        )
        if resolved_path is None:
            failures.append(f"artifact file is missing: {raw_path}")
        else:
            actual_sha256 = _file_sha256(resolved_path)
            actual_schema = _load_schema_id(resolved_path)

    if declared_exists is not True:
        failures.append(f"artifact declared exists={declared_exists!r}, expected true")
    if not isinstance(declared_sha256, str) or len(declared_sha256) != 64:
        failures.append("artifact sha256 must be a lowercase 64-character hex string")
    elif actual_sha256 is not None and declared_sha256 != actual_sha256:
        failures.append(
            f"artifact sha256 mismatch: {declared_sha256!r} != {actual_sha256!r}"
        )
    if expected_schema is not None and declared_schema != expected_schema:
        failures.append(
            f"artifact declared schema mismatch: {declared_schema!r} != {expected_schema!r}"
        )
    if declared_schema is not None and actual_schema != declared_schema:
        failures.append(
            f"artifact content schema mismatch: {actual_schema!r} != {declared_schema!r}"
        )

    return {
        "label": label,
        "path": raw_path,
        "resolved_path": None if resolved_path is None else str(resolved_path),
        "declared_sha256": declared_sha256,
        "actual_sha256": actual_sha256,
        "declared_schema_id": declared_schema,
        "actual_schema_id": actual_schema,
        "ok": not failures,
        "failures": failures,
    }


def _receipt_consistency_failures(
    *,
    manifest: dict[str, Any],
    artifacts_by_label: dict[str, dict[str, Any]],
    manifest_path: Path,
    base_dir: Path | None,
) -> list[str]:
    receipt_artifact = artifacts_by_label.get("receipt_json")
    if receipt_artifact is None:
        return []
    raw_path = receipt_artifact.get("path")
    if not isinstance(raw_path, str):
        return []
    receipt_path = _resolve_existing_artifact(
        raw_path,
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    if receipt_path is None:
        return []
    receipt = _load_json_object(receipt_path)
    if receipt.get("schema_id") != EXPECTED_SCHEMA_BY_LABEL["receipt_json"]:
        return ["receipt_json has an unexpected schema_id"]
    decision = receipt.get("decision")
    decision_obj = decision if isinstance(decision, dict) else {}
    comparisons = (
        ("kind", manifest.get("kind"), receipt.get("kind")),
        ("status", manifest.get("status"), receipt.get("status")),
        (
            "request_passed",
            manifest.get("request_passed"),
            receipt.get("request_passed"),
        ),
        (
            "decision_verdict",
            manifest.get("decision_verdict"),
            decision_obj.get("verdict"),
        ),
        (
            "decision_assurance",
            manifest.get("decision_assurance"),
            decision_obj.get("assurance"),
        ),
        (
            "request_content_fingerprint",
            manifest.get("request_content_fingerprint"),
            receipt.get("request_content_fingerprint"),
        ),
        (
            "normalized_request_fingerprint",
            manifest.get("normalized_request_fingerprint"),
            receipt.get("normalized_request_fingerprint"),
        ),
        (
            "receipt_content_fingerprint",
            manifest.get("receipt_content_fingerprint"),
            receipt.get("receipt_content_fingerprint"),
        ),
    )
    failures: list[str] = []
    for field, manifest_value, receipt_value in comparisons:
        if manifest_value != receipt_value:
            failures.append(
                f"manifest {field} does not match receipt_json: "
                f"{manifest_value!r} != {receipt_value!r}"
            )
    return failures


def _load_receipt_artifact(
    *,
    artifacts_by_label: dict[str, dict[str, Any]],
    manifest_path: Path,
    base_dir: Path | None,
) -> dict[str, Any] | None:
    receipt_artifact = artifacts_by_label.get("receipt_json")
    if receipt_artifact is None:
        return None
    raw_path = receipt_artifact.get("path")
    if not isinstance(raw_path, str):
        return None
    receipt_path = _resolve_existing_artifact(
        raw_path,
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    if receipt_path is None:
        return None
    try:
        return _load_json_object(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _receipt_theorem_ids(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    proof_status = receipt.get("proof_status")
    if not isinstance(proof_status, dict):
        return []
    theorem_ids = proof_status.get("theorem_ids")
    if not isinstance(theorem_ids, list):
        return []
    return [theorem_id for theorem_id in theorem_ids if isinstance(theorem_id, str)]


def _receipt_evidence_fields(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict):
        return []
    return sorted(key for key in evidence if isinstance(key, str))


def _receipt_recommendation_ids(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    recommendations = receipt.get("recommendations")
    if not isinstance(recommendations, list):
        return []
    ids: list[str] = []
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            continue
        recommendation_id = recommendation.get("id")
        if isinstance(recommendation_id, str):
            ids.append(recommendation_id)
    return ids


def _receipt_validation_commands(receipt: dict[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    commands = receipt.get("validation_commands")
    if not isinstance(commands, list):
        return []
    return [command for command in commands if isinstance(command, str)]


def _manifest_check_report(
    *,
    manifest_path: Path,
    require_manifest_check: bool,
) -> tuple[dict[str, Any] | None, list[str]]:
    path = _manifest_check_path(manifest_path)
    if not path.exists():
        if require_manifest_check:
            return None, [f"manifest-check report is missing: {path}"]
        return None, []
    try:
        report = _load_json_object(path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, [f"manifest-check report is unreadable: {exc}"]
    failures: list[str] = []
    if report.get("schema_id") != MANIFEST_CHECK_SCHEMA_ID:
        failures.append("manifest-check report schema_id is unexpected")
    if report.get("ok") is not True:
        failures.append("manifest-check report ok was not true")
    if report.get("failure_count") != 0:
        failures.append("manifest-check report failure_count was not zero")
    return report, failures


def verify_manifest(
    path: Path,
    *,
    base_dir: Path | None,
    required_statuses: list[str],
    required_decisions: list[str],
    required_assurances: list[str],
    require_passed: bool,
    required_labels: list[str],
    require_manifest_check: bool,
) -> dict[str, Any]:
    manifest = _load_json_object(path)
    failures: list[str] = []
    if manifest.get("schema_id") != MANIFEST_SCHEMA_ID:
        failures.append("manifest schema_id is unexpected")
    if manifest.get("artifact_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        failures.append("manifest artifact_fingerprint_algorithm is unexpected")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        artifacts = []
        failures.append("manifest artifacts must be a list")
    declared_count = manifest.get("artifact_count")
    if declared_count != len(artifacts):
        failures.append(
            f"manifest artifact_count mismatch: {declared_count!r} != {len(artifacts)!r}"
        )

    artifact_reports: list[dict[str, Any]] = []
    labels: list[str] = []
    artifacts_by_label: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            failures.append("artifact entry is not an object")
            continue
        report = _artifact_report(
            artifact,
            manifest_path=path,
            base_dir=base_dir,
        )
        artifact_reports.append(report)
        label = report.get("label")
        if isinstance(label, str):
            if label in artifacts_by_label:
                failures.append(f"duplicate artifact label: {label}")
            artifacts_by_label[label] = artifact
            labels.append(label)
        failures.extend(f"{label}: {failure}" for failure in report["failures"])

    for label in required_labels:
        if label not in artifacts_by_label:
            failures.append(f"required artifact label is missing: {label}")

    failures.extend(
        _receipt_consistency_failures(
            manifest=manifest,
            artifacts_by_label=artifacts_by_label,
            manifest_path=path,
            base_dir=base_dir,
        )
    )
    receipt = _load_receipt_artifact(
        artifacts_by_label=artifacts_by_label,
        manifest_path=path,
        base_dir=base_dir,
    )
    receipt_theorem_ids = _receipt_theorem_ids(receipt)
    receipt_evidence_fields = _receipt_evidence_fields(receipt)
    receipt_recommendation_ids = _receipt_recommendation_ids(receipt)
    receipt_validation_commands = _receipt_validation_commands(receipt)
    normalized_request = (
        receipt.get("normalized_request") if isinstance(receipt, dict) else None
    )

    status = manifest.get("status")
    decision = manifest.get("decision_verdict")
    assurance = manifest.get("decision_assurance")
    if required_statuses and status not in set(required_statuses):
        failures.append(f"manifest status {status!r} not in {required_statuses!r}")
    if required_decisions and decision not in set(required_decisions):
        failures.append(
            f"manifest decision_verdict {decision!r} not in {required_decisions!r}"
        )
    if required_assurances and assurance not in set(required_assurances):
        failures.append(
            "manifest decision_assurance "
            f"{assurance!r} not in {required_assurances!r}"
        )
    if require_passed and manifest.get("request_passed") is not True:
        failures.append("manifest request_passed was not true")

    manifest_check, manifest_check_failures = _manifest_check_report(
        manifest_path=path,
        require_manifest_check=require_manifest_check,
    )
    failures.extend(manifest_check_failures)

    return {
        "path": str(path),
        "accepted": not failures,
        "kind": manifest.get("kind"),
        "status": status,
        "request_passed": manifest.get("request_passed"),
        "decision_verdict": decision,
        "decision_assurance": assurance,
        "artifact_count": len(artifact_reports),
        "declared_artifact_count": declared_count,
        "artifact_labels": labels,
        "artifact_reports": artifact_reports,
        "theorem_count": len(receipt_theorem_ids),
        "theorem_ids": receipt_theorem_ids,
        "evidence_field_count": len(receipt_evidence_fields),
        "evidence_fields": receipt_evidence_fields,
        "recommendation_ids": receipt_recommendation_ids,
        "validation_command_count": len(receipt_validation_commands),
        "validation_commands": receipt_validation_commands,
        "normalized_request": (
            dict(normalized_request)
            if isinstance(normalized_request, dict)
            else None
        ),
        "request_content_fingerprint": manifest.get("request_content_fingerprint"),
        "normalized_request_fingerprint": manifest.get(
            "normalized_request_fingerprint"
        ),
        "receipt_content_fingerprint": manifest.get("receipt_content_fingerprint"),
        "request_content_fingerprint_short": _short(
            manifest.get("request_content_fingerprint")
        ),
        "normalized_request_fingerprint_short": _short(
            manifest.get("normalized_request_fingerprint")
        ),
        "receipt_content_fingerprint_short": _short(
            manifest.get("receipt_content_fingerprint")
        ),
        "manifest_check_path": str(_manifest_check_path(path)),
        "manifest_check_present": manifest_check is not None,
        "manifest_check_ok": (
            None if manifest_check is None else manifest_check.get("ok") is True
        ),
        "failure_count": len(failures),
        "failures": failures,
    }


def verify_manifests(
    paths: list[Path],
    *,
    base_dir: Path | None,
    required_kinds: list[str],
    required_theorem_ids: list[str],
    required_evidence_fields: list[str],
    required_recommendation_ids: list[str],
    required_validation_commands: list[str],
    required_normalized_params: list[tuple[str, Any]],
    required_statuses: list[str],
    required_decisions: list[str],
    required_assurances: list[str],
    require_passed: bool,
    required_labels: list[str],
    require_manifest_check: bool,
) -> dict[str, Any]:
    _check_policy_values(
        statuses=required_statuses,
        decisions=required_decisions,
        assurances=required_assurances,
    )
    summaries = [
        verify_manifest(
            path,
            base_dir=base_dir,
            required_statuses=required_statuses,
            required_decisions=required_decisions,
            required_assurances=required_assurances,
            require_passed=require_passed,
            required_labels=required_labels,
            require_manifest_check=require_manifest_check,
        )
        for path in paths
    ]
    failures = [
        f"{summary['path']}: {failure}"
        for summary in summaries
        for failure in summary["failures"]
    ]
    observed_kinds = [
        summary["kind"] for summary in summaries if isinstance(summary.get("kind"), str)
    ]
    kind_counts = {
        kind: observed_kinds.count(kind) for kind in sorted(set(observed_kinds))
    }
    for kind in required_kinds:
        if kind not in kind_counts:
            failures.append(f"required contract kind is missing: {kind}")
    observed_theorem_ids = sorted(
        {
            theorem_id
            for summary in summaries
            for theorem_id in summary.get("theorem_ids", [])
            if isinstance(theorem_id, str)
        }
    )
    observed_theorem_id_set = set(observed_theorem_ids)
    for theorem_id in required_theorem_ids:
        if theorem_id not in observed_theorem_id_set:
            failures.append(f"required receipt theorem id is missing: {theorem_id}")
    observed_evidence_fields = sorted(
        {
            field
            for summary in summaries
            for field in summary.get("evidence_fields", [])
            if isinstance(field, str)
        }
    )
    observed_evidence_field_set = set(observed_evidence_fields)
    for field in required_evidence_fields:
        if field not in observed_evidence_field_set:
            failures.append(f"required receipt evidence field is missing: {field}")
    observed_recommendation_ids = sorted(
        {
            recommendation_id
            for summary in summaries
            for recommendation_id in summary.get("recommendation_ids", [])
            if isinstance(recommendation_id, str)
        }
    )
    observed_recommendation_id_set = set(observed_recommendation_ids)
    for recommendation_id in required_recommendation_ids:
        if recommendation_id not in observed_recommendation_id_set:
            failures.append(
                f"required receipt recommendation id is missing: {recommendation_id}"
            )
    observed_validation_commands = sorted(
        {
            command
            for summary in summaries
            for command in summary.get("validation_commands", [])
            if isinstance(command, str)
        }
    )
    observed_validation_command_set = set(observed_validation_commands)
    for command in required_validation_commands:
        if command not in observed_validation_command_set:
            failures.append(
                f"required receipt validation command is missing: {command}"
            )
    for key, value in required_normalized_params:
        if not any(
            isinstance(summary.get("normalized_request"), dict)
            and summary["normalized_request"].get(key) == value
            for summary in summaries
        ):
            failures.append(
                f"required normalized request parameter is missing: {key}={value!r}"
            )
    return {
        "schema_id": EXAMPLE_SCHEMA_ID,
        "accepted": not failures,
        "manifest_count": len(paths),
        "failure_count": len(failures),
        "failures": failures,
        "required_kinds": required_kinds,
        "observed_kinds": sorted(set(observed_kinds)),
        "kind_counts": kind_counts,
        "required_theorem_ids": required_theorem_ids,
        "observed_theorem_id_count": len(observed_theorem_ids),
        "required_evidence_fields": required_evidence_fields,
        "observed_evidence_field_count": len(observed_evidence_fields),
        "required_recommendation_ids": required_recommendation_ids,
        "observed_recommendation_id_count": len(observed_recommendation_ids),
        "required_validation_commands": required_validation_commands,
        "observed_validation_command_count": len(observed_validation_commands),
        "required_normalized_params": [
            {"key": key, "value": value} for key, value in required_normalized_params
        ],
        "required_statuses": required_statuses,
        "required_decisions": required_decisions,
        "required_assurances": required_assurances,
        "require_passed": require_passed,
        "required_labels": required_labels,
        "require_manifest_check": require_manifest_check,
        "manifests": summaries,
        "not_claimed": (
            "This is a downstream artifact-integrity gate. It is not a "
            "mathematical proof, Lean verification run, model-quality result, "
            "deployment-safety claim, or ASI claim."
        ),
    }


def _failure_report(exc: BaseException, manifests: list[str]) -> dict[str, Any]:
    message = str(exc)
    return {
        "schema_id": FAILURE_SCHEMA_ID,
        "example_schema_id": EXAMPLE_SCHEMA_ID,
        "accepted": False,
        "error": message,
        "failure_count": 1,
        "failures": [message],
        "manifest_paths": manifests,
        "not_claimed": (
            "This is a machine-readable rejection report for an artifact "
            "integrity gate. It is not a mathematical proof, model-quality "
            "result, deployment-safety claim, or ASI claim."
        ),
    }


def _print_text(report: dict[str, Any]) -> None:
    print(
        "circle AI downstream artifact verification "
        f"accepted={report['accepted']} manifests={report['manifest_count']} "
        f"failures={report['failure_count']}"
    )
    for summary in report["manifests"]:
        print(
            "artifact_manifest "
            f"path={summary['path']} kind={summary['kind']} "
            f"status={summary['status']} passed={summary['request_passed']} "
            f"decision={summary['decision_verdict']} "
            f"assurance={summary['decision_assurance']} "
            f"artifacts={summary['artifact_count']} "
            f"manifest_check={summary['manifest_check_present']} "
            f"failures={summary['failure_count']}"
        )
        for failure in summary["failures"]:
            print(f"failure={summary['path']}: {failure}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Standalone downstream CI verifier for Circle AI runner "
            "artifact manifests."
        ),
    )
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Optional base directory for resolving relative artifact paths.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        default=[],
        help="Require every manifest status to match this value.",
    )
    parser.add_argument(
        "--require-kind",
        action="append",
        default=[],
        help="Require at least one artifact manifest for this contract kind.",
    )
    parser.add_argument(
        "--require-theorem-id",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to cite this theorem id. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--require-evidence-field",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this top-level "
            "evidence field. May be repeated."
        ),
    )
    parser.add_argument(
        "--require-recommendation-id",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this planner "
            "recommendation id. May be repeated."
        ),
    )
    parser.add_argument(
        "--require-validation-command",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this exact "
            "validation command. May be repeated."
        ),
    )
    parser.add_argument(
        "--require-normalized-param",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help=(
            "Require at least one saved receipt artifact to have this top-level "
            "normalized_request parameter value. May be repeated."
        ),
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        default=[],
        help="Require every manifest decision_verdict to match this value.",
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        default=[],
        help="Require every manifest decision_assurance to match this value.",
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Fail unless every manifest has request_passed=true.",
    )
    parser.add_argument(
        "--require-label",
        action="append",
        default=[],
        help="Require an artifact label to be present. May be repeated.",
    )
    parser.add_argument(
        "--require-manifest-check",
        action="store_true",
        help="Require the sibling *_artifact_manifest_check.json report to pass.",
    )
    args = parser.parse_args()

    try:
        required_normalized_params = [
            _parse_normalized_param_pin(raw)
            for raw in args.require_normalized_param
        ]
        report = verify_manifests(
            args.manifests,
            base_dir=args.base_dir,
            required_kinds=args.require_kind,
            required_theorem_ids=args.require_theorem_id,
            required_evidence_fields=args.require_evidence_field,
            required_recommendation_ids=args.require_recommendation_id,
            required_validation_commands=args.require_validation_command,
            required_normalized_params=required_normalized_params,
            required_statuses=args.require_status,
            required_decisions=args.require_decision,
            required_assurances=args.require_assurance,
            require_passed=args.require_passed,
            required_labels=args.require_label,
            require_manifest_check=args.require_manifest_check,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        failure = _failure_report(exc, [str(path) for path in args.manifests])
        if args.format == "json":
            print(json.dumps(failure, indent=2, sort_keys=True), file=sys.stderr)
        else:
            print(f"circle AI downstream artifact verification failed: {exc}", file=sys.stderr)
        return 4

    if args.format == "json":
        output = sys.stdout if report["accepted"] else sys.stderr
        print(json.dumps(report, indent=2, sort_keys=True), file=output)
    else:
        _print_text(report)
    return 0 if report["accepted"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
