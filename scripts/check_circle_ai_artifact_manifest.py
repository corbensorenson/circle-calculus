#!/usr/bin/env python
"""Validate saved Circle AI contract artifact manifest JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications import (  # noqa: E402
    CIRCLE_AI_CONTRACT_ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_ID,
    build_contract_artifact_manifest_file_check_json_schema,
    build_contract_artifact_manifest_file_check_report,
    build_contract_artifact_manifest_json_schema,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_PATH,
    ARTIFACT_MANIFEST_SCHEMA_PATH,
)


CHECK_SCHEMA_ID = CIRCLE_AI_CONTRACT_ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_ID
DEFAULT_MANIFEST_SCHEMA = ROOT / ARTIFACT_MANIFEST_SCHEMA_PATH
DEFAULT_REPORT_SCHEMA = ROOT / ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_PATH


def _json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _validate_schema_file(
    path: Path,
    generated_schema: dict[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    schema = _json_object(path)
    jsonschema.Draft202012Validator.check_schema(schema)
    if schema != generated_schema:
        raise jsonschema.SchemaError(f"{label} schema drifted from application builder")
    return schema


def _pin_failures(
    summaries: list[dict[str, Any]],
    *,
    required_kinds: tuple[str, ...],
    required_theorem_ids: tuple[str, ...],
    required_evidence_fields: tuple[str, ...],
    required_recommendation_ids: tuple[str, ...],
) -> list[str]:
    failures: list[str] = []
    observed_kinds = {
        summary["kind"] for summary in summaries if isinstance(summary.get("kind"), str)
    }
    observed_theorem_ids = {
        theorem_id
        for summary in summaries
        for theorem_id in summary.get("theorem_ids", [])
        if isinstance(theorem_id, str)
    }
    observed_evidence_fields = {
        field
        for summary in summaries
        for field in summary.get("evidence_fields", [])
        if isinstance(field, str)
    }
    observed_recommendation_ids = {
        recommendation_id
        for summary in summaries
        for recommendation_id in summary.get("recommendation_ids", [])
        if isinstance(recommendation_id, str)
    }

    for kind in required_kinds:
        if kind not in observed_kinds:
            failures.append(f"required contract kind is missing: {kind}")
    for theorem_id in required_theorem_ids:
        if theorem_id not in observed_theorem_ids:
            failures.append(f"required receipt theorem id is missing: {theorem_id}")
    for field in required_evidence_fields:
        if field not in observed_evidence_fields:
            failures.append(f"required receipt evidence field is missing: {field}")
    for recommendation_id in required_recommendation_ids:
        if recommendation_id not in observed_recommendation_ids:
            failures.append(
                f"required receipt recommendation id is missing: {recommendation_id}"
            )
    return failures


def check_artifact_manifest_files(
    *,
    manifest_paths: tuple[Path, ...],
    manifest_schema_path: Path = DEFAULT_MANIFEST_SCHEMA,
    report_schema_path: Path = DEFAULT_REPORT_SCHEMA,
    required_kinds: tuple[str, ...] = (),
    required_theorem_ids: tuple[str, ...] = (),
    required_evidence_fields: tuple[str, ...] = (),
    required_recommendation_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    manifest_schema = _validate_schema_file(
        manifest_schema_path,
        build_contract_artifact_manifest_json_schema(),
        label="artifact manifest",
    )
    report_schema = _validate_schema_file(
        report_schema_path,
        build_contract_artifact_manifest_file_check_json_schema(),
        label="artifact-manifest file-check report",
    )

    summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in manifest_paths:
        try:
            manifest = _json_object(path)
            jsonschema.validate(manifest, manifest_schema)
            manifest_report = build_contract_artifact_manifest_file_check_report(
                manifest,
                manifest_path=path,
            )
            failures.extend(manifest_report["failures"])
            summaries.extend(manifest_report["summaries"])
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
            jsonschema.ValidationError,
            jsonschema.SchemaError,
        ) as exc:
            failures.append(f"{path}: {exc}")

    failures.extend(
        _pin_failures(
            summaries,
            required_kinds=required_kinds,
            required_theorem_ids=required_theorem_ids,
            required_evidence_fields=required_evidence_fields,
            required_recommendation_ids=required_recommendation_ids,
        )
    )
    report = {
        "schema_id": CHECK_SCHEMA_ID,
        "ok": not failures,
        "manifest_count": len(manifest_paths),
        "failure_count": len(failures),
        "failures": failures,
        "summaries": summaries,
    }
    jsonschema.validate(report, report_schema)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate saved Circle AI artifact manifests, including referenced "
            "file existence, SHA-256 fingerprints, declared schema ids, and "
            "receipt summary consistency."
        ),
    )
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument(
        "--manifest-schema",
        type=Path,
        default=DEFAULT_MANIFEST_SCHEMA,
    )
    parser.add_argument(
        "--report-schema",
        type=Path,
        default=DEFAULT_REPORT_SCHEMA,
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--report-out",
        type=Path,
        help="Optional path where the artifact-manifest validation report is written.",
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
        help="Require at least one saved receipt artifact to cite this theorem id.",
    )
    parser.add_argument(
        "--require-evidence-field",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this top-level "
            "evidence field."
        ),
    )
    parser.add_argument(
        "--require-recommendation-id",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this planner "
            "recommendation id."
        ),
    )
    args = parser.parse_args()

    report = check_artifact_manifest_files(
        manifest_paths=tuple(args.manifests),
        manifest_schema_path=args.manifest_schema,
        report_schema_path=args.report_schema,
        required_kinds=tuple(args.require_kind),
        required_theorem_ids=tuple(args.require_theorem_id),
        required_evidence_fields=tuple(args.require_evidence_field),
        required_recommendation_ids=tuple(args.require_recommendation_id),
    )
    if args.report_out is not None:
        _write_json(args.report_out, report)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "circle AI artifact manifests "
            f"ok={report['ok']} manifests={report['manifest_count']} "
            f"failures={report['failure_count']}"
        )
        for summary in report["summaries"]:
            print(
                "artifact_manifest="
                f"{summary['path']} kind={summary['kind']} "
                f"status={summary['status']} "
                f"passed={summary['request_passed']} "
                f"decision={summary['decision_verdict']} "
                f"assurance={summary['decision_assurance']} "
                f"artifacts={summary['artifact_count']} "
                f"missing={summary['missing_artifact_count']} "
                f"fingerprint_mismatches={summary['fingerprint_mismatch_count']} "
                f"schema_mismatches={summary['schema_mismatch_count']} "
                f"failures={summary['failure_count']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
