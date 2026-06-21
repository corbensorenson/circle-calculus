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


def check_receipt_files(
    *,
    receipt_paths: tuple[Path, ...],
    pack_path: Path = DEFAULT_PACK_PATH,
    receipt_schema_path: Path = DEFAULT_RECEIPT_SCHEMA,
    required_statuses: tuple[str, ...] = (),
    require_passed: bool = False,
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

    return {
        "schema_id": CHECK_SCHEMA_ID,
        "ok": not failures,
        "receipt_count": len(receipt_paths),
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": {
            "allowed_statuses": list(required_statuses),
            "require_passed": require_passed,
        },
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
        "--require-passed",
        action="store_true",
        help="Exit nonzero unless every receipt has request_passed=true.",
    )
    args = parser.parse_args()

    report = check_receipt_files(
        receipt_paths=tuple(args.receipts),
        pack_path=args.pack,
        receipt_schema_path=args.receipt_schema,
        required_statuses=tuple(args.require_status),
        require_passed=args.require_passed,
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
                f"theorems={summary['theorem_count']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
