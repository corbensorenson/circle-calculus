#!/usr/bin/env python
"""Validate public Circle AI contract-runner examples and receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications import (  # noqa: E402
    build_contract_certification_bundle,
    build_contract_certification_bundle_json_schema,
    build_contract_request_validation_report,
    build_contract_runner_check_json_schema,
    build_rope_model_config_import_report,
    build_validated_contract_receipt_from_request,
    load_contract_pack,
    validate_contract_request,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    DECISION_ASSURANCE_LEVELS,
    DECISION_VERDICTS,
    RUNNER_CHECK_SCHEMA_ID,
    STATUS_VALUES,
)


DEFAULT_EXAMPLE_DIR = ROOT / "examples" / "circle_ai_requests"
DEFAULT_MODEL_CONFIG_DIR = ROOT / "examples" / "circle_ai_model_configs"
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_REQUEST_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_request.schema.json"
)
DEFAULT_REQUEST_VALIDATION_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_request_validation.schema.json"
)
DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_rope_model_config_import.schema.json"
)
DEFAULT_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
)
DEFAULT_RUNNER_CHECK_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_runner_check.schema.json"
)
DEFAULT_CERTIFICATION_BUNDLE_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_certification_bundle.schema.json"
)


def _json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _request_paths(example_dir: Path) -> list[Path]:
    paths = sorted(example_dir.glob("*_request.json"))
    if not paths:
        raise ValueError(f"no *_request.json files found under {example_dir}")
    return paths


def _model_config_paths(model_config_dir: Path | None) -> list[Path]:
    if model_config_dir is None:
        return []
    if not model_config_dir.exists():
        return []
    return sorted(model_config_dir.glob("*.json"))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _json_fingerprint(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _summary_from_receipt(
    *,
    source_type: str,
    source_path: Path,
    source: dict[str, Any],
    request_path: Path | None,
    model_config_import_report_path: Path | None,
    model_config_parameter_sources: dict[str, Any] | None,
    request_validation_report_path: Path | None,
    certification_bundle_path: Path | None,
    receipt_path: Path | None,
    receipt: dict[str, Any],
) -> dict[str, Any]:
    decision = receipt["decision"]
    return {
        "source_type": source_type,
        "source_path": _display_path(source_path),
        "source_content_fingerprint": _json_fingerprint(source),
        "request_path": None if request_path is None else _display_path(request_path),
        "model_config_import_report_path": (
            None
            if model_config_import_report_path is None
            else _display_path(model_config_import_report_path)
        ),
        "model_config_parameter_sources": model_config_parameter_sources,
        "request_validation_report_path": (
            None
            if request_validation_report_path is None
            else _display_path(request_validation_report_path)
        ),
        "certification_bundle_path": (
            None
            if certification_bundle_path is None
            else _display_path(certification_bundle_path)
        ),
        "receipt_path": None if receipt_path is None else _display_path(receipt_path),
        "kind": receipt["kind"],
        "status": receipt["status"],
        "request_passed": receipt["request_passed"],
        "decision_verdict": decision["verdict"],
        "decision_assurance": decision["assurance"],
        "theorem_count": receipt["proof_status"]["theorem_count"],
        "recommendation_count": len(receipt["recommendations"]),
        "validation_command_count": len(receipt["validation_commands"]),
        "normalized_request": receipt["normalized_request"],
        "request_content_fingerprint": receipt["request_content_fingerprint"],
        "normalized_request_fingerprint": receipt["normalized_request_fingerprint"],
        "receipt_content_fingerprint": receipt["receipt_content_fingerprint"],
    }


def _append_gate_failures(
    *,
    path: Path,
    summary: dict[str, Any],
    failures: list[str],
    required_statuses: tuple[str, ...],
    required_decision_verdicts: tuple[str, ...],
    required_assurance_levels: tuple[str, ...],
    require_passed: bool,
) -> None:
    if required_statuses and summary["status"] not in required_statuses:
        failures.append(
            f"{path}: receipt status {summary['status']!r} did not match "
            "required status set: " + ", ".join(required_statuses)
        )
    if (
        required_decision_verdicts
        and summary["decision_verdict"] not in required_decision_verdicts
    ):
        failures.append(
            f"{path}: receipt decision verdict {summary['decision_verdict']!r} "
            "did not match required decision set: "
            + ", ".join(required_decision_verdicts)
        )
    if (
        required_assurance_levels
        and summary["decision_assurance"] not in required_assurance_levels
    ):
        failures.append(
            f"{path}: receipt assurance {summary['decision_assurance']!r} "
            "did not match required assurance set: "
            + ", ".join(required_assurance_levels)
        )
    if require_passed and summary["request_passed"] is not True:
        failures.append(
            f"{path}: receipt request_passed was not true "
            f"(got {summary['request_passed']!r})"
        )


def check_runner_examples(
    *,
    example_dir: Path = DEFAULT_EXAMPLE_DIR,
    model_config_dir: Path | None = DEFAULT_MODEL_CONFIG_DIR,
    model_config_requested_margin: str | None = "1/328459",
    pack_path: Path = DEFAULT_PACK_PATH,
    request_schema_path: Path = DEFAULT_REQUEST_SCHEMA,
    request_validation_schema_path: Path = DEFAULT_REQUEST_VALIDATION_SCHEMA,
    model_config_import_schema_path: Path = DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA,
    receipt_schema_path: Path = DEFAULT_RECEIPT_SCHEMA,
    runner_check_schema_path: Path = DEFAULT_RUNNER_CHECK_SCHEMA,
    certification_bundle_schema_path: Path = DEFAULT_CERTIFICATION_BUNDLE_SCHEMA,
    receipt_out_dir: Path | None = None,
    model_config_import_report_out_dir: Path | None = None,
    request_validation_report_out_dir: Path | None = None,
    certification_bundle_out_dir: Path | None = None,
    required_statuses: tuple[str, ...] = (),
    required_decision_verdicts: tuple[str, ...] = (),
    required_assurance_levels: tuple[str, ...] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    request_schema = _json(request_schema_path)
    request_validation_schema = _json(request_validation_schema_path)
    model_config_import_schema = _json(model_config_import_schema_path)
    receipt_schema = _json(receipt_schema_path)
    runner_check_schema = _json(runner_check_schema_path)
    certification_bundle_schema = _json(certification_bundle_schema_path)
    jsonschema.Draft202012Validator.check_schema(request_schema)
    jsonschema.Draft202012Validator.check_schema(request_validation_schema)
    jsonschema.Draft202012Validator.check_schema(model_config_import_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.Draft202012Validator.check_schema(runner_check_schema)
    jsonschema.Draft202012Validator.check_schema(certification_bundle_schema)
    if certification_bundle_schema != build_contract_certification_bundle_json_schema():
        raise jsonschema.SchemaError(
            "certification-bundle schema drifted from application builder"
        )
    pack = load_contract_pack(pack_path)
    summaries: list[dict[str, Any]] = []
    failures: list[str] = []

    for path in _request_paths(example_dir):
        try:
            request = _json(path)
            jsonschema.validate(request, request_schema)
            validation_report = build_contract_request_validation_report(request)
            jsonschema.validate(validation_report, request_validation_schema)
            validation_report_path = None
            if request_validation_report_out_dir is not None:
                validation_report_path = (
                    request_validation_report_out_dir
                    / f"{path.stem.removesuffix('_request')}_request_validation.json"
                )
                _write_json(validation_report_path, validation_report)
            request_failures = validate_contract_request(request)
            if request_failures:
                failures.append(f"{path}: " + "; ".join(request_failures))
                continue
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
            jsonschema.validate(receipt, receipt_schema)
            receipt_path = None
            if receipt_out_dir is not None:
                receipt_path = receipt_out_dir / f"{path.stem.removesuffix('_request')}_receipt.json"
                _write_json(receipt_path, receipt)
            certification_bundle_path = None
            if certification_bundle_out_dir is not None:
                certification_bundle_path = (
                    certification_bundle_out_dir
                    / f"{path.stem.removesuffix('_request')}_certification_bundle.json"
                )
                bundle = build_contract_certification_bundle(
                    request,
                    pack=pack,
                    receipt_path=(
                        _display_path(receipt_path)
                        if receipt_path is not None
                        else "<in-memory-receipt>"
                    ),
                    required_statuses=required_statuses,
                    required_decision_verdicts=required_decision_verdicts,
                    required_assurance_levels=required_assurance_levels,
                    require_passed=require_passed,
                )
                jsonschema.validate(bundle, certification_bundle_schema)
                _write_json(certification_bundle_path, bundle)
            summary = _summary_from_receipt(
                source_type="request",
                source_path=path,
                source=request,
                request_path=path,
                model_config_import_report_path=None,
                model_config_parameter_sources=None,
                request_validation_report_path=validation_report_path,
                certification_bundle_path=certification_bundle_path,
                receipt_path=receipt_path,
                receipt=receipt,
            )
            summaries.append(summary)
            _append_gate_failures(
                path=path,
                summary=summary,
                failures=failures,
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
        except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{path}: {exc}")

    for path in _model_config_paths(model_config_dir):
        try:
            config = _json(path)
            import_report = build_rope_model_config_import_report(
                config,
                requested_margin=model_config_requested_margin,
            )
            jsonschema.validate(import_report, model_config_import_schema)
            import_report_path = None
            if model_config_import_report_out_dir is not None:
                import_report_path = (
                    model_config_import_report_out_dir / f"{path.stem}_import.json"
                )
                _write_json(import_report_path, import_report)
            if not import_report["ok"]:
                failures.append(f"{path}: " + "; ".join(import_report["failures"]))
                continue
            request = import_report["request"]
            if not isinstance(request, dict):
                failures.append(f"{path}: model config import report did not emit a request")
                continue
            jsonschema.validate(request, request_schema)
            validation_report = build_contract_request_validation_report(request)
            jsonschema.validate(validation_report, request_validation_schema)
            validation_report_path = None
            if request_validation_report_out_dir is not None:
                validation_report_path = (
                    request_validation_report_out_dir
                    / f"{path.stem}_request_validation.json"
                )
                _write_json(validation_report_path, validation_report)
            request_failures = validate_contract_request(request)
            if request_failures:
                failures.append(f"{path}: " + "; ".join(request_failures))
                continue
            receipt = build_validated_contract_receipt_from_request(request, pack=pack)
            jsonschema.validate(receipt, receipt_schema)
            request_path = None
            receipt_path = None
            if receipt_out_dir is not None:
                request_path = receipt_out_dir / f"{path.stem}_request.json"
                receipt_path = receipt_out_dir / f"{path.stem}_receipt.json"
                _write_json(request_path, request)
                _write_json(receipt_path, receipt)
            certification_bundle_path = None
            if certification_bundle_out_dir is not None:
                certification_bundle_path = (
                    certification_bundle_out_dir
                    / f"{path.stem}_certification_bundle.json"
                )
                bundle = build_contract_certification_bundle(
                    request,
                    pack=pack,
                    model_config_import_report=import_report,
                    receipt_path=(
                        _display_path(receipt_path)
                        if receipt_path is not None
                        else "<in-memory-receipt>"
                    ),
                    required_statuses=required_statuses,
                    required_decision_verdicts=required_decision_verdicts,
                    required_assurance_levels=required_assurance_levels,
                    require_passed=require_passed,
                )
                jsonschema.validate(bundle, certification_bundle_schema)
                _write_json(certification_bundle_path, bundle)
            summary = _summary_from_receipt(
                source_type="model_config",
                source_path=path,
                source=config,
                request_path=request_path,
                model_config_import_report_path=import_report_path,
                model_config_parameter_sources=import_report["parameter_sources"],
                request_validation_report_path=validation_report_path,
                certification_bundle_path=certification_bundle_path,
                receipt_path=receipt_path,
                receipt=receipt,
            )
            summaries.append(summary)
            _append_gate_failures(
                path=path,
                summary=summary,
                failures=failures,
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
        except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{path}: {exc}")

    report = {
        "schema_id": RUNNER_CHECK_SCHEMA_ID,
        "ok": not failures,
        "example_count": len(summaries),
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
    jsonschema.validate(report, runner_check_schema)
    generated_schema = build_contract_runner_check_json_schema()
    if runner_check_schema != generated_schema:
        raise jsonschema.SchemaError(
            "contract-runner check schema drifted from application builder"
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Circle AI contract-runner request/model-config examples.",
    )
    parser.add_argument("--example-dir", type=Path, default=DEFAULT_EXAMPLE_DIR)
    parser.add_argument(
        "--model-config-dir",
        type=Path,
        default=DEFAULT_MODEL_CONFIG_DIR,
        help="Optional directory of standard RoPE model config JSON examples.",
    )
    parser.add_argument(
        "--model-config-requested-margin",
        default="1/328459",
        help=(
            "Requested real-phase margin to attach to model-config examples. "
            "Use an empty string to omit the margin."
        ),
    )
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH)
    parser.add_argument(
        "--request-schema",
        type=Path,
        default=DEFAULT_REQUEST_SCHEMA,
    )
    parser.add_argument(
        "--receipt-schema",
        type=Path,
        default=DEFAULT_RECEIPT_SCHEMA,
    )
    parser.add_argument(
        "--request-validation-schema",
        type=Path,
        default=DEFAULT_REQUEST_VALIDATION_SCHEMA,
    )
    parser.add_argument(
        "--model-config-import-schema",
        type=Path,
        default=DEFAULT_MODEL_CONFIG_IMPORT_SCHEMA,
        help="Generated JSON Schema used to validate standard-RoPE model-config import reports.",
    )
    parser.add_argument(
        "--runner-check-schema",
        type=Path,
        default=DEFAULT_RUNNER_CHECK_SCHEMA,
    )
    parser.add_argument(
        "--certification-bundle-schema",
        type=Path,
        default=DEFAULT_CERTIFICATION_BUNDLE_SCHEMA,
        help=(
            "Generated JSON Schema used to validate certification bundles "
            "written by --certification-bundle-out-dir."
        ),
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--receipt-out-dir",
        type=Path,
        help="Optional directory where validated receipt JSON files are written.",
    )
    parser.add_argument(
        "--model-config-import-report-out-dir",
        type=Path,
        help=(
            "Optional directory where schema-validated standard-RoPE "
            "model-config import reports are written."
        ),
    )
    parser.add_argument(
        "--request-validation-report-out-dir",
        type=Path,
        help=(
            "Optional directory where schema-validated request preflight "
            "reports are written for every checked request."
        ),
    )
    parser.add_argument(
        "--certification-bundle-out-dir",
        type=Path,
        help=(
            "Optional directory where schema-validated certification bundles "
            "are written for every checked request/model config."
        ),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        help="Optional path where the schema-validated batch check report is written.",
    )
    parser.add_argument(
        "--require-status",
        action="append",
        choices=STATUS_VALUES,
        default=[],
        help=(
            "Require every emitted receipt status to match this value. May be "
            "passed more than once."
        ),
    )
    parser.add_argument(
        "--require-decision",
        action="append",
        choices=DECISION_VERDICTS,
        default=[],
        help=(
            "Require every emitted receipt decision.verdict to match this value. "
            "May be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-assurance",
        action="append",
        choices=DECISION_ASSURANCE_LEVELS,
        default=[],
        help=(
            "Require every emitted receipt decision.assurance to match this value. "
            "May be passed more than once."
        ),
    )
    parser.add_argument(
        "--require-passed",
        action="store_true",
        help="Exit nonzero unless every emitted receipt has request_passed=true.",
    )
    args = parser.parse_args()

    report = check_runner_examples(
        example_dir=args.example_dir,
        model_config_dir=args.model_config_dir,
        model_config_requested_margin=(
            args.model_config_requested_margin
            if args.model_config_requested_margin
            else None
        ),
        pack_path=args.pack,
        request_schema_path=args.request_schema,
        request_validation_schema_path=args.request_validation_schema,
        model_config_import_schema_path=args.model_config_import_schema,
        receipt_schema_path=args.receipt_schema,
        runner_check_schema_path=args.runner_check_schema,
        certification_bundle_schema_path=args.certification_bundle_schema,
        receipt_out_dir=args.receipt_out_dir,
        model_config_import_report_out_dir=args.model_config_import_report_out_dir,
        request_validation_report_out_dir=args.request_validation_report_out_dir,
        certification_bundle_out_dir=args.certification_bundle_out_dir,
        required_statuses=tuple(args.require_status),
        required_decision_verdicts=tuple(args.require_decision),
        required_assurance_levels=tuple(args.require_assurance),
        require_passed=args.require_passed,
    )
    if args.report_out is not None:
        _write_json(args.report_out, report)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "circle AI runner examples "
            f"ok={report['ok']} examples={report['example_count']} "
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
                "source="
                f"{summary['source_path']} type={summary['source_type']} "
                f"request={summary['request_path']} kind={summary['kind']} "
                f"import_report={summary['model_config_import_report_path']} "
                f"request_validation={summary['request_validation_report_path']} "
                f"bundle={summary['certification_bundle_path']} "
                f"status={summary['status']} "
                f"passed={summary['request_passed']} "
                f"decision={summary['decision_verdict']} "
                f"assurance={summary['decision_assurance']} "
                f"theorems={summary['theorem_count']} "
                f"recommendations={summary['recommendation_count']} "
                f"receipt={summary['receipt_path']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
