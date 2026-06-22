#!/usr/bin/env python
"""Validate saved Circle AI contract receipt JSON files."""

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
    CIRCLE_AI_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_ID,
    build_contract_receipt_file_check_report,
    build_contract_receipt_file_check_json_schema,
    load_contract_pack,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    DECISION_ASSURANCE_LEVELS,
    DECISION_VERDICTS,
    RECEIPT_FILE_CHECK_SCHEMA_PATH,
    STATUS_VALUES,
)


CHECK_SCHEMA_ID = CIRCLE_AI_CONTRACT_RECEIPT_FILE_CHECK_SCHEMA_ID
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
)
DEFAULT_REPORT_SCHEMA = ROOT / RECEIPT_FILE_CHECK_SCHEMA_PATH


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


def _validate_report_schema(report: dict[str, Any], schema_path: Path) -> None:
    schema = _json_object(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(report, schema)
    generated_schema = build_contract_receipt_file_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "receipt-file check schema drifted from application builder"
        )


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


def _receipt_policy_values(policy: dict[str, Any]) -> dict[str, Any]:
    model_config_fingerprints = _policy_string_tuple(
        policy,
        "required_model_config_fingerprints",
    )
    if model_config_fingerprints:
        raise ValueError(
            "receipt pin policies cannot require model config fingerprints; "
            "use the certification bundle or artifact manifest checker"
        )
    architecture_config_fingerprints = _policy_string_tuple(
        policy,
        "required_architecture_config_fingerprints",
    )
    if architecture_config_fingerprints:
        raise ValueError(
            "receipt pin policies cannot require architecture config "
            "fingerprints; use the certification bundle or artifact manifest "
            "checker"
        )
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
    required_normalized_params: tuple[tuple[str, Any], ...],
) -> dict[str, Any]:
    return {
        "required_kinds": list(required_kinds),
        "required_theorem_ids": list(required_theorem_ids),
        "required_evidence_fields": list(required_evidence_fields),
        "required_recommendation_ids": list(required_recommendation_ids),
        "required_validation_commands": list(required_validation_commands),
        "required_model_config_fingerprints": [],
        "required_architecture_config_fingerprints": [],
        "required_normalized_params": [
            {"key": key, "value": value} for key, value in required_normalized_params
        ],
    }


def check_receipt_files(
    *,
    receipt_paths: tuple[Path, ...],
    pack_path: Path = DEFAULT_PACK_PATH,
    receipt_schema_path: Path = DEFAULT_RECEIPT_SCHEMA,
    required_statuses: tuple[str, ...] = (),
    required_decision_verdicts: tuple[str, ...] = (),
    required_assurance_levels: tuple[str, ...] = (),
    require_passed: bool = False,
    required_kinds: tuple[str, ...] = (),
    required_theorem_ids: tuple[str, ...] = (),
    required_evidence_fields: tuple[str, ...] = (),
    required_recommendation_ids: tuple[str, ...] = (),
    required_validation_commands: tuple[str, ...] = (),
    required_normalized_params: tuple[tuple[str, Any], ...] = (),
) -> dict[str, Any]:
    receipt_schema = _json_object(receipt_schema_path)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    pack = load_contract_pack(pack_path)

    summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in receipt_paths:
        path_failures: list[str] = []
        try:
            receipt = _json_object(path)
            jsonschema.validate(receipt, receipt_schema)
            receipt_report = build_contract_receipt_file_check_report(
                receipt,
                pack,
                receipt_path=_display_path(path),
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
            path_failures.extend(receipt_report["failures"])
            summaries.extend(receipt_report["summaries"])
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
            jsonschema.ValidationError,
            jsonschema.SchemaError,
        ) as exc:
            path_failures.append(str(exc))

        failures.extend(f"{path}: {failure}" for failure in path_failures)

    failures.extend(
        _pin_failures(
            summaries,
            required_kinds=required_kinds,
            required_theorem_ids=required_theorem_ids,
            required_evidence_fields=required_evidence_fields,
            required_recommendation_ids=required_recommendation_ids,
            required_validation_commands=required_validation_commands,
            required_normalized_params=required_normalized_params,
        )
    )
    return {
        "schema_id": CHECK_SCHEMA_ID,
        "ok": not failures,
        "receipt_count": len(receipt_paths),
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": {
            "allowed_statuses": list(required_statuses),
            "allowed_decision_verdicts": list(required_decision_verdicts),
            "allowed_assurance_levels": list(required_assurance_levels),
            "require_passed": require_passed,
        },
        "pin_policy": _pin_policy(
            required_kinds=required_kinds,
            required_theorem_ids=required_theorem_ids,
            required_evidence_fields=required_evidence_fields,
            required_recommendation_ids=required_recommendation_ids,
            required_validation_commands=required_validation_commands,
            required_normalized_params=required_normalized_params,
        ),
        "summaries": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate saved Circle AI receipt JSON against the public receipt "
            "schema, in-process validator, loaded contract pack fingerprints, "
            "and optional CI gate requirements."
        ),
    )
    parser.add_argument("receipts", nargs="+", type=Path)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH)
    parser.add_argument("--receipt-schema", type=Path, default=DEFAULT_RECEIPT_SCHEMA)
    parser.add_argument("--report-schema", type=Path, default=DEFAULT_REPORT_SCHEMA)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--report-out",
        type=Path,
        help="Optional path where the receipt-file validation report is written.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=STATUS_VALUES,
        default=[],
        help=(
            "Require every receipt status to match this value. May be passed "
            "more than once."
        ),
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=DECISION_VERDICTS,
        default=[],
        help=(
            "Require every receipt decision.verdict to match this value. May be "
            "passed more than once."
        ),
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=DECISION_ASSURANCE_LEVELS,
        default=[],
        help=(
            "Require every receipt decision.assurance to match this value. May "
            "be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Exit nonzero unless every receipt has request_passed=true.",
    )
    parser.add_argument(
        "--require-kind",
        action="append",
        default=[],
        help="Require at least one saved receipt for this contract kind.",
    )
    parser.add_argument(
        "--require-theorem-id",
        action="append",
        default=[],
        help="Require at least one saved receipt to cite this theorem id.",
    )
    parser.add_argument(
        "--require-evidence-field",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt to expose this top-level "
            "evidence field."
        ),
    )
    parser.add_argument(
        "--require-recommendation-id",
        action="append",
        default=[],
        help=(
            "Require at least one saved receipt to expose this planner "
            "recommendation id."
        ),
    )
    parser.add_argument(
        "--require-validation-command",
        action="append",
        default=[],
        help="Require at least one saved receipt to expose this exact command.",
    )
    parser.add_argument(
        "--require-normalized-param",
        action="append",
        default=[],
        metavar="KEY=JSON_VALUE",
        help=(
            "Require at least one saved receipt to have this top-level "
            "normalized_request parameter value."
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
        policy_values = _receipt_policy_values(_load_pin_policy(args.pin_policy))
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
        required_normalized_params = _merge_normalized_params(
            policy_values["required_normalized_params"],
            required_normalized_params,
        )
    except ValueError as exc:
        print(f"circle AI receipt files failed: {exc}", file=sys.stderr)
        return 2

    report = check_receipt_files(
        receipt_paths=tuple(args.receipts),
        pack_path=args.pack,
        receipt_schema_path=args.receipt_schema,
        required_statuses=tuple(args.require_status),
        required_decision_verdicts=tuple(args.require_decision),
        required_assurance_levels=tuple(args.require_assurance),
        require_passed=args.require_passed,
        required_kinds=required_kinds,
        required_theorem_ids=required_theorem_ids,
        required_evidence_fields=required_evidence_fields,
        required_recommendation_ids=required_recommendation_ids,
        required_validation_commands=required_validation_commands,
        required_normalized_params=required_normalized_params,
    )
    _validate_report_schema(report, args.report_schema)
    if args.report_out is not None:
        _write_json(args.report_out, report)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "circle AI receipt files "
            f"ok={report['ok']} receipts={report['receipt_count']} "
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
                "receipt="
                f"{summary['path']} kind={summary['kind']} "
                f"contract_id={summary['contract_id']} "
                f"status={summary['status']} "
                f"passed={summary['request_passed']} "
                f"decision={summary['decision_verdict']} "
                f"assurance={summary['decision_assurance']} "
                f"theorems={summary['theorem_count']} "
                f"pack={summary['contract_pack_fingerprint'][:12]} "
                f"contract={summary['contract_content_fingerprint'][:12]} "
                f"request={summary['request_content_fingerprint'][:12]} "
                f"receipt_fingerprint={summary['receipt_content_fingerprint'][:12]}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
