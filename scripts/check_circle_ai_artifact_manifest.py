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


def _load_pin_policy(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = _json_object(path)
    if "pin_policy" in payload:
        policy = payload["pin_policy"]
        if not isinstance(policy, dict):
            raise ValueError(f"{path} pin_policy must be a JSON object")
        return policy
    return payload


def _policy_string_tuple(policy: dict[str, Any], key: str) -> tuple[str, ...]:
    values = policy.get(key, [])
    if not isinstance(values, list) or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError(f"pin policy {key} must be a list of strings")
    return tuple(values)


def _policy_normalized_params(
    policy: dict[str, Any],
) -> tuple[tuple[str, Any], ...]:
    values = policy.get("required_normalized_params", [])
    if not isinstance(values, list):
        raise ValueError(
            "pin policy required_normalized_params must be a list of objects"
        )
    pins: list[tuple[str, Any]] = []
    for item in values:
        if not isinstance(item, dict):
            raise ValueError(
                "pin policy required_normalized_params must be a list of objects"
            )
        key = item.get("key")
        if not isinstance(key, str) or not key:
            raise ValueError(
                "pin policy required_normalized_params entries need a string key"
            )
        if "value" not in item:
            raise ValueError(
                "pin policy required_normalized_params entries need a value"
            )
        pins.append((key, item["value"]))
    return tuple(pins)


def _merge_strings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                merged.append(value)
    return tuple(merged)


def _value_marker(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except TypeError:
        return repr(value)


def _merge_normalized_params(
    *groups: tuple[tuple[str, Any], ...],
) -> tuple[tuple[str, Any], ...]:
    merged: list[tuple[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for group in groups:
        for key, value in group:
            marker = (key, _value_marker(value))
            if marker not in seen:
                seen.add(marker)
                merged.append((key, value))
    return tuple(merged)


def _pin_policy_values(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_kinds": _policy_string_tuple(policy, "required_kinds"),
        "required_theorem_ids": _policy_string_tuple(
            policy,
            "required_theorem_ids",
        ),
        "required_evidence_fields": _policy_string_tuple(
            policy,
            "required_evidence_fields",
        ),
        "required_recommendation_ids": _policy_string_tuple(
            policy,
            "required_recommendation_ids",
        ),
        "required_validation_commands": _policy_string_tuple(
            policy,
            "required_validation_commands",
        ),
        "required_model_config_fingerprints": _policy_string_tuple(
            policy,
            "required_model_config_fingerprints",
        ),
        "required_architecture_config_fingerprints": _policy_string_tuple(
            policy,
            "required_architecture_config_fingerprints",
        ),
        "required_normalized_params": _policy_normalized_params(policy),
    }


def _pin_failures(
    summaries: list[dict[str, Any]],
    *,
    required_kinds: tuple[str, ...],
    required_theorem_ids: tuple[str, ...],
    required_evidence_fields: tuple[str, ...],
    required_recommendation_ids: tuple[str, ...],
    required_validation_commands: tuple[str, ...],
    required_model_config_fingerprints: tuple[str, ...],
    required_architecture_config_fingerprints: tuple[str, ...],
    required_normalized_params: tuple[tuple[str, Any], ...],
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
    observed_architecture_config_fingerprints = {
        fingerprint
        for summary in summaries
        for fingerprint in (summary.get("architecture_config_fingerprint"),)
        if isinstance(fingerprint, str)
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
    for command in required_validation_commands:
        if command not in observed_validation_commands:
            failures.append(f"required receipt validation command is missing: {command}")
    for fingerprint in required_model_config_fingerprints:
        if fingerprint not in observed_model_config_fingerprints:
            failures.append(
                f"required model config fingerprint is missing: {fingerprint}"
            )
    for fingerprint in required_architecture_config_fingerprints:
        if fingerprint not in observed_architecture_config_fingerprints:
            failures.append(
                "required architecture config fingerprint is missing: "
                f"{fingerprint}"
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


def _pin_policy(
    *,
    required_kinds: tuple[str, ...],
    required_theorem_ids: tuple[str, ...],
    required_evidence_fields: tuple[str, ...],
    required_recommendation_ids: tuple[str, ...],
    required_validation_commands: tuple[str, ...],
    required_model_config_fingerprints: tuple[str, ...],
    required_architecture_config_fingerprints: tuple[str, ...],
    required_normalized_params: tuple[tuple[str, Any], ...],
) -> dict[str, Any]:
    return {
        "required_kinds": list(required_kinds),
        "required_theorem_ids": list(required_theorem_ids),
        "required_evidence_fields": list(required_evidence_fields),
        "required_recommendation_ids": list(required_recommendation_ids),
        "required_validation_commands": list(required_validation_commands),
        "required_model_config_fingerprints": list(
            required_model_config_fingerprints
        ),
        "required_architecture_config_fingerprints": list(
            required_architecture_config_fingerprints
        ),
        "required_normalized_params": [
            {"key": key, "value": value} for key, value in required_normalized_params
        ],
    }


def check_artifact_manifest_files(
    *,
    manifest_paths: tuple[Path, ...],
    manifest_schema_path: Path = DEFAULT_MANIFEST_SCHEMA,
    report_schema_path: Path = DEFAULT_REPORT_SCHEMA,
    required_kinds: tuple[str, ...] = (),
    required_theorem_ids: tuple[str, ...] = (),
    required_evidence_fields: tuple[str, ...] = (),
    required_recommendation_ids: tuple[str, ...] = (),
    required_validation_commands: tuple[str, ...] = (),
    required_model_config_fingerprints: tuple[str, ...] = (),
    required_architecture_config_fingerprints: tuple[str, ...] = (),
    required_normalized_params: tuple[tuple[str, Any], ...] = (),
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
            required_validation_commands=required_validation_commands,
            required_model_config_fingerprints=required_model_config_fingerprints,
            required_architecture_config_fingerprints=(
                required_architecture_config_fingerprints
            ),
            required_normalized_params=required_normalized_params,
        )
    )
    report = {
        "schema_id": CHECK_SCHEMA_ID,
        "ok": not failures,
        "manifest_count": len(manifest_paths),
        "failure_count": len(failures),
        "failures": failures,
        "pin_policy": _pin_policy(
            required_kinds=required_kinds,
            required_theorem_ids=required_theorem_ids,
            required_evidence_fields=required_evidence_fields,
            required_recommendation_ids=required_recommendation_ids,
            required_validation_commands=required_validation_commands,
            required_model_config_fingerprints=required_model_config_fingerprints,
            required_architecture_config_fingerprints=(
                required_architecture_config_fingerprints
            ),
            required_normalized_params=required_normalized_params,
        ),
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
    parser.add_argument(
        "--require-validation-command",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt artifact to expose this exact "
            "validation command."
        ),
    )
    parser.add_argument(
        "--require-normalized-param",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help=(
            "Require at least one saved receipt artifact to have this top-level "
            "normalized_request parameter value."
        ),
    )
    parser.add_argument(
        "--require-model-config-fingerprint",
        action="append",
        default=[],
        help=(
            "Require at least one RoPE model-config import artifact to expose "
            "this source config SHA-256 fingerprint."
        ),
    )
    parser.add_argument(
        "--require-architecture-config-fingerprint",
        action="append",
        default=[],
        help=(
            "Require at least one architecture-config import artifact to expose "
            "this source config SHA-256 fingerprint."
        ),
    )
    parser.add_argument(
        "--pin-policy",
        type=Path,
        help=(
            "Load required dependency pins from a JSON object shaped like a "
            "check report pin_policy block. A whole prior check report is also "
            "accepted. Explicit --require-* flags are merged with loaded pins."
        ),
    )
    args = parser.parse_args()
    try:
        policy_values = _pin_policy_values(_load_pin_policy(args.pin_policy))
        required_normalized_params = tuple(
            _parse_normalized_param_pin(raw)
            for raw in args.require_normalized_param
        )
        required_kinds = _merge_strings(
            policy_values["required_kinds"],
            tuple(args.require_kind),
        )
        required_theorem_ids = _merge_strings(
            policy_values["required_theorem_ids"],
            tuple(args.require_theorem_id),
        )
        required_evidence_fields = _merge_strings(
            policy_values["required_evidence_fields"],
            tuple(args.require_evidence_field),
        )
        required_recommendation_ids = _merge_strings(
            policy_values["required_recommendation_ids"],
            tuple(args.require_recommendation_id),
        )
        required_validation_commands = _merge_strings(
            policy_values["required_validation_commands"],
            tuple(args.require_validation_command),
        )
        required_model_config_fingerprints = _merge_strings(
            policy_values["required_model_config_fingerprints"],
            tuple(args.require_model_config_fingerprint),
        )
        required_architecture_config_fingerprints = _merge_strings(
            policy_values["required_architecture_config_fingerprints"],
            tuple(args.require_architecture_config_fingerprint),
        )
        required_normalized_params = _merge_normalized_params(
            policy_values["required_normalized_params"],
            required_normalized_params,
        )
    except ValueError as exc:
        print(f"circle AI artifact manifests failed: {exc}", file=sys.stderr)
        return 2

    report = check_artifact_manifest_files(
        manifest_paths=tuple(args.manifests),
        manifest_schema_path=args.manifest_schema,
        report_schema_path=args.report_schema,
        required_kinds=required_kinds,
        required_theorem_ids=required_theorem_ids,
        required_evidence_fields=required_evidence_fields,
        required_recommendation_ids=required_recommendation_ids,
        required_validation_commands=required_validation_commands,
        required_model_config_fingerprints=required_model_config_fingerprints,
        required_architecture_config_fingerprints=(
            required_architecture_config_fingerprints
        ),
        required_normalized_params=required_normalized_params,
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
                f"model_config={summary.get('model_config_fingerprint') is not None} "
                "architecture_config="
                f"{summary.get('architecture_config_fingerprint') is not None} "
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
