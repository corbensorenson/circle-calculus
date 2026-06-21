#!/usr/bin/env python
"""Validate saved Circle AI contract certification bundle JSON files."""

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
    CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
    build_contract_certification_bundle_file_check_report,
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_json_schema,
    build_contract_request_validation_json_schema,
    build_rope_model_config_import_json_schema,
    load_contract_pack,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH,
    CERTIFICATION_BUNDLE_SCHEMA_PATH,
    DECISION_ASSURANCE_LEVELS,
    DECISION_VERDICTS,
    REQUEST_VALIDATION_SCHEMA_PATH,
    ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH,
    STATUS_VALUES,
)


CHECK_SCHEMA_ID = CIRCLE_AI_CONTRACT_CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_BUNDLE_SCHEMA = ROOT / CERTIFICATION_BUNDLE_SCHEMA_PATH
DEFAULT_REPORT_SCHEMA = ROOT / CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH
DEFAULT_REQUEST_VALIDATION_SCHEMA = ROOT / REQUEST_VALIDATION_SCHEMA_PATH
DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA = ROOT / ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH


def _json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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


def _pin_failures(
    summaries: list[dict[str, Any]],
    *,
    required_theorem_ids: tuple[str, ...],
    required_evidence_fields: tuple[str, ...],
    required_recommendation_ids: tuple[str, ...],
    required_validation_commands: tuple[str, ...],
    required_model_config_fingerprints: tuple[str, ...],
    required_normalized_params: tuple[tuple[str, Any], ...],
) -> list[str]:
    failures: list[str] = []
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
    observed_validation_commands = {
        command
        for summary in summaries
        for command in summary.get("validation_commands", [])
        if isinstance(command, str)
    }
    observed_model_config_fingerprints = {
        fingerprint
        for summary in summaries
        for fingerprint in (summary.get("model_config_fingerprint"),)
        if isinstance(fingerprint, str)
    }

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
    for command in required_validation_commands:
        if command not in observed_validation_commands:
            failures.append(f"required receipt validation command is missing: {command}")
    for fingerprint in required_model_config_fingerprints:
        if fingerprint not in observed_model_config_fingerprints:
            failures.append(
                f"required model config fingerprint is missing: {fingerprint}"
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
    return failures


def check_certification_bundle_files(
    *,
    bundle_paths: tuple[Path, ...],
    pack_path: Path = DEFAULT_PACK_PATH,
    bundle_schema_path: Path = DEFAULT_BUNDLE_SCHEMA,
    report_schema_path: Path = DEFAULT_REPORT_SCHEMA,
    request_validation_schema_path: Path = DEFAULT_REQUEST_VALIDATION_SCHEMA,
    model_config_import_schema_path: Path = DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA,
    required_statuses: tuple[str, ...] = (),
    required_decision_verdicts: tuple[str, ...] = (),
    required_assurance_levels: tuple[str, ...] = (),
    require_passed: bool = False,
    required_theorem_ids: tuple[str, ...] = (),
    required_evidence_fields: tuple[str, ...] = (),
    required_recommendation_ids: tuple[str, ...] = (),
    required_validation_commands: tuple[str, ...] = (),
    required_model_config_fingerprints: tuple[str, ...] = (),
    required_normalized_params: tuple[tuple[str, Any], ...] = (),
) -> dict[str, Any]:
    _validate_schema_file(
        bundle_schema_path,
        build_contract_certification_bundle_json_schema(),
        label="certification-bundle",
    )
    report_schema = _validate_schema_file(
        report_schema_path,
        build_contract_certification_bundle_file_check_json_schema(),
        label="certification-bundle file-check report",
    )
    _validate_schema_file(
        request_validation_schema_path,
        build_contract_request_validation_json_schema(),
        label="request validation",
    )
    _validate_schema_file(
        model_config_import_schema_path,
        build_rope_model_config_import_json_schema(),
        label="RoPE model config import",
    )
    pack = load_contract_pack(pack_path)

    summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in bundle_paths:
        try:
            bundle = _json_object(path)
            bundle_report = build_contract_certification_bundle_file_check_report(
                bundle=bundle,
                pack=pack,
                bundle_path=_display_path(path),
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
            failures.extend(bundle_report["failures"])
            summaries.extend(bundle_report["summaries"])
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
            required_theorem_ids=required_theorem_ids,
            required_evidence_fields=required_evidence_fields,
            required_recommendation_ids=required_recommendation_ids,
            required_validation_commands=required_validation_commands,
            required_model_config_fingerprints=required_model_config_fingerprints,
            required_normalized_params=required_normalized_params,
        )
    )
    report = {
        "schema_id": CHECK_SCHEMA_ID,
        "ok": not failures,
        "bundle_count": len(bundle_paths),
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": {
            "allowed_statuses": list(required_statuses),
            "allowed_decision_verdicts": list(required_decision_verdicts),
            "allowed_assurance_levels": list(required_assurance_levels),
            "require_passed": require_passed,
        },
        "summaries": summaries,
    }
    jsonschema.validate(report, report_schema)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate saved Circle AI certification bundle JSON against the "
            "public bundle schema, embedded receipt, loaded contract pack, "
            "model-config provenance, and optional CI gate requirements."
        ),
    )
    parser.add_argument("bundles", nargs="+", type=Path)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH)
    parser.add_argument("--bundle-schema", type=Path, default=DEFAULT_BUNDLE_SCHEMA)
    parser.add_argument("--report-schema", type=Path, default=DEFAULT_REPORT_SCHEMA)
    parser.add_argument(
        "--request-validation-schema",
        type=Path,
        default=DEFAULT_REQUEST_VALIDATION_SCHEMA,
    )
    parser.add_argument(
        "--model-config-import-schema",
        type=Path,
        default=DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA,
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--report-out",
        type=Path,
        help=(
            "Optional path where the certification-bundle validation report "
            "is written."
        ),
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=STATUS_VALUES,
        default=[],
        help=(
            "Require every embedded receipt status to match this value. May "
            "be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=DECISION_VERDICTS,
        default=[],
        help=(
            "Require every embedded receipt decision.verdict to match this "
            "value. May be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=DECISION_ASSURANCE_LEVELS,
        default=[],
        help=(
            "Require every embedded receipt decision.assurance to match this "
            "value. May be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Exit nonzero unless every embedded receipt has request_passed=true.",
    )
    parser.add_argument(
        "--require-theorem-id",
        action="append",
        default=[],
        help="Require at least one embedded receipt to cite this theorem id.",
    )
    parser.add_argument(
        "--require-evidence-field",
        action="append",
        default=[],
        help=(
            "Require at least one embedded receipt to expose this top-level "
            "evidence field."
        ),
    )
    parser.add_argument(
        "--require-recommendation-id",
        action="append",
        default=[],
        help=(
            "Require at least one embedded receipt to expose this planner "
            "recommendation id."
        ),
    )
    parser.add_argument(
        "--require-validation-command",
        action="append",
        default=[],
        help="Require at least one embedded receipt to expose this exact command.",
    )
    parser.add_argument(
        "--require-model-config-fingerprint",
        action="append",
        default=[],
        help=(
            "Require at least one embedded RoPE model-config import report to "
            "expose this source config SHA-256 fingerprint."
        ),
    )
    parser.add_argument(
        "--require-normalized-param",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help=(
            "Require at least one embedded receipt to have this top-level "
            "normalized_request parameter value."
        ),
    )
    args = parser.parse_args()
    try:
        required_normalized_params = tuple(
            _parse_normalized_param_pin(raw)
            for raw in args.require_normalized_param
        )
    except ValueError as exc:
        print(f"circle AI certification bundles failed: {exc}", file=sys.stderr)
        return 2

    report = check_certification_bundle_files(
        bundle_paths=tuple(args.bundles),
        pack_path=args.pack,
        bundle_schema_path=args.bundle_schema,
        report_schema_path=args.report_schema,
        request_validation_schema_path=args.request_validation_schema,
        model_config_import_schema_path=args.model_config_import_schema,
        required_statuses=tuple(args.require_status),
        required_decision_verdicts=tuple(args.require_decision),
        required_assurance_levels=tuple(args.require_assurance),
        require_passed=args.require_passed,
        required_theorem_ids=tuple(args.require_theorem_id),
        required_evidence_fields=tuple(args.require_evidence_field),
        required_recommendation_ids=tuple(args.require_recommendation_id),
        required_validation_commands=tuple(args.require_validation_command),
        required_model_config_fingerprints=tuple(
            args.require_model_config_fingerprint
        ),
        required_normalized_params=required_normalized_params,
    )
    if args.report_out is not None:
        _write_json(args.report_out, report)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "circle AI certification bundles "
            f"ok={report['ok']} bundles={report['bundle_count']} "
            f"failures={report['failure_count']} "
            f"required_statuses={report['gate_policy']['allowed_statuses']} "
            "required_decisions="
            f"{report['gate_policy']['allowed_decision_verdicts']} "
            "required_assurances="
            f"{report['gate_policy']['allowed_assurance_levels']} "
            f"require_passed={report['gate_policy']['require_passed']}"
        )
        for summary in report["summaries"]:
            print(
                "bundle="
                f"{summary['path']} kind={summary['kind']} "
                f"contract_id={summary['contract_id']} "
                f"status={summary['status']} "
                f"passed={summary['request_passed']} "
                f"decision={summary['decision_verdict']} "
                f"assurance={summary['decision_assurance']} "
                f"model_config={summary['has_model_config_import_report']} "
                f"pack={summary['contract_pack_fingerprint'][:12]} "
                f"receipt_fingerprint={summary['receipt_content_fingerprint'][:12]} "
                f"failures={summary['failure_count']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
