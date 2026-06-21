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
    build_contract_certification_bundle_file_check_json_schema,
    build_contract_certification_bundle_json_schema,
    build_contract_receipt_file_check_report,
    build_contract_receipt_file_check_json_schema,
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


def _append_bundle_consistency_failures(
    *,
    bundle: dict[str, Any],
    embedded_gate_schema: dict[str, Any],
    request_validation_schema: dict[str, Any],
    model_config_import_schema: dict[str, Any],
    path_failures: list[str],
) -> None:
    if bundle.get("failure_count") != len(bundle.get("failures", [])):
        path_failures.append("bundle failure_count does not match failures length")
    if bundle.get("ok") is not True:
        details = "; ".join(str(failure) for failure in bundle.get("failures", ()))
        path_failures.append(
            "bundle ok was not true" + (f": {details}" if details else "")
        )

    request_validation = bundle.get("request_validation_report")
    if isinstance(request_validation, dict):
        jsonschema.validate(request_validation, request_validation_schema)
        if request_validation.get("request_content_fingerprint") != bundle.get(
            "request_content_fingerprint"
        ):
            path_failures.append(
                "request validation fingerprint does not match bundle request"
            )
        if request_validation.get("ok") is not True:
            path_failures.append("request validation report ok was not true")

    receipt = bundle.get("receipt")
    if isinstance(receipt, dict):
        if receipt.get("normalized_request_fingerprint") != bundle.get(
            "normalized_request_fingerprint"
        ):
            path_failures.append(
                "receipt normalized_request_fingerprint does not match bundle"
            )
        if receipt.get("receipt_content_fingerprint") != bundle.get(
            "receipt_content_fingerprint"
        ):
            path_failures.append("receipt_content_fingerprint does not match bundle")
    else:
        path_failures.append("bundle receipt was null")

    gate_report = bundle.get("gate_report")
    if isinstance(gate_report, dict):
        jsonschema.validate(gate_report, embedded_gate_schema)
        if gate_report.get("gate_policy") != bundle.get("gate_policy"):
            path_failures.append("embedded gate_report policy does not match bundle")
        if gate_report.get("failure_count") != len(gate_report.get("failures", [])):
            path_failures.append(
                "embedded gate_report failure_count does not match failures length"
            )
        if gate_report.get("ok") != (gate_report.get("failure_count") == 0):
            path_failures.append("embedded gate_report ok disagrees with failure_count")
        summaries = gate_report.get("summaries")
        if isinstance(receipt, dict) and isinstance(summaries, list):
            if len(summaries) != 1:
                path_failures.append("embedded gate_report must have one summary")
            elif summaries[0].get("receipt_content_fingerprint") != receipt.get(
                "receipt_content_fingerprint"
            ):
                path_failures.append(
                    "embedded gate_report receipt fingerprint does not match receipt"
                )
    else:
        path_failures.append("bundle gate_report was null")

    import_report = bundle.get("model_config_import_report")
    if import_report is None:
        return
    if isinstance(import_report, dict):
        jsonschema.validate(import_report, model_config_import_schema)
        if import_report.get("request_content_fingerprint") != bundle.get(
            "request_content_fingerprint"
        ):
            path_failures.append(
                "model config import request fingerprint does not match bundle"
            )
        if isinstance(receipt, dict) and import_report.get("request") != receipt.get(
            "request"
        ):
            path_failures.append("model config import request does not match receipt")
        if import_report.get("ok") is not True:
            path_failures.append("model config import report ok was not true")
    else:
        path_failures.append("model_config_import_report was not an object or null")


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
) -> dict[str, Any]:
    bundle_schema = _validate_schema_file(
        bundle_schema_path,
        build_contract_certification_bundle_json_schema(),
        label="certification-bundle",
    )
    report_schema = _validate_schema_file(
        report_schema_path,
        build_contract_certification_bundle_file_check_json_schema(),
        label="certification-bundle file-check report",
    )
    request_validation_schema = _validate_schema_file(
        request_validation_schema_path,
        build_contract_request_validation_json_schema(),
        label="request validation",
    )
    model_config_import_schema = _validate_schema_file(
        model_config_import_schema_path,
        build_rope_model_config_import_json_schema(),
        label="RoPE model config import",
    )
    embedded_gate_schema = build_contract_receipt_file_check_json_schema()
    pack = load_contract_pack(pack_path)

    summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in bundle_paths:
        path_failures: list[str] = []
        try:
            bundle = _json_object(path)
            jsonschema.validate(bundle, bundle_schema)
            receipt = bundle.get("receipt")
            if not isinstance(receipt, dict):
                receipt_report = {"summaries": [], "failures": []}
            else:
                receipt_report = build_contract_receipt_file_check_report(
                    receipt,
                    pack,
                    receipt_path=f"{_display_path(path)}::receipt",
                    required_statuses=required_statuses,
                    required_decision_verdicts=required_decision_verdicts,
                    required_assurance_levels=required_assurance_levels,
                    require_passed=require_passed,
                )
                path_failures.extend(receipt_report["failures"])
            _append_bundle_consistency_failures(
                bundle=bundle,
                embedded_gate_schema=embedded_gate_schema,
                request_validation_schema=request_validation_schema,
                model_config_import_schema=model_config_import_schema,
                path_failures=path_failures,
            )

            if receipt_report["summaries"]:
                receipt_summary = dict(receipt_report["summaries"][0])
                import_report = bundle.get("model_config_import_report")
                has_import_report = isinstance(import_report, dict)
                summaries.append(
                    {
                        "path": _display_path(path),
                        "bundle_ok": bool(bundle.get("ok")),
                        "bundle_failure_count": int(bundle.get("failure_count", 0)),
                        "request_validation_ok": bool(
                            bundle["request_validation_report"].get("ok")
                        ),
                        "gate_report_ok": (
                            bundle["gate_report"].get("ok")
                            if isinstance(bundle.get("gate_report"), dict)
                            else None
                        ),
                        "has_model_config_import_report": has_import_report,
                        "model_config_fingerprint": (
                            import_report.get("model_config_fingerprint")
                            if has_import_report
                            else None
                        ),
                        "model_config_request_content_fingerprint": (
                            import_report.get("request_content_fingerprint")
                            if has_import_report
                            else None
                        ),
                        "kind": receipt_summary["kind"],
                        "contract_id": receipt_summary["contract_id"],
                        "content_fingerprint_algorithm": receipt_summary[
                            "content_fingerprint_algorithm"
                        ],
                        "contract_pack_fingerprint": receipt_summary[
                            "contract_pack_fingerprint"
                        ],
                        "contract_content_fingerprint": receipt_summary[
                            "contract_content_fingerprint"
                        ],
                        "status": receipt_summary["status"],
                        "request_passed": receipt_summary["request_passed"],
                        "decision_verdict": receipt_summary["decision_verdict"],
                        "decision_assurance": receipt_summary["decision_assurance"],
                        "theorem_count": receipt_summary["theorem_count"],
                        "normalized_request": receipt_summary["normalized_request"],
                        "bundle_request_content_fingerprint": bundle[
                            "request_content_fingerprint"
                        ],
                        "receipt_request_content_fingerprint": receipt_summary[
                            "request_content_fingerprint"
                        ],
                        "normalized_request_fingerprint": receipt_summary[
                            "normalized_request_fingerprint"
                        ],
                        "receipt_content_fingerprint": receipt_summary[
                            "receipt_content_fingerprint"
                        ],
                        "failure_count": len(path_failures),
                    }
                )
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
            jsonschema.ValidationError,
            jsonschema.SchemaError,
        ) as exc:
            path_failures.append(str(exc))

        failures.extend(f"{path}: {failure}" for failure in path_failures)

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
    args = parser.parse_args()

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
