#!/usr/bin/env python
"""Rebuild saved Circle AI receipts from their embedded requests."""

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
    CIRCLE_AI_CONTRACT_RECEIPT_REPLAY_CHECK_SCHEMA_ID,
    build_contract_receipt_replay_check_json_schema,
    build_contract_receipt_replay_check_report,
    load_contract_pack,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    RECEIPT_REPLAY_CHECK_SCHEMA_PATH,
)


CHECK_SCHEMA_ID = CIRCLE_AI_CONTRACT_RECEIPT_REPLAY_CHECK_SCHEMA_ID
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
)
DEFAULT_REPORT_SCHEMA = ROOT / RECEIPT_REPLAY_CHECK_SCHEMA_PATH


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
    generated_schema = build_contract_receipt_replay_check_json_schema()
    if schema != generated_schema:
        raise jsonschema.SchemaError(
            "receipt-replay check schema drifted from application builder"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild a saved Circle AI receipt from its embedded request and "
            "compare the regenerated receipt fingerprints against the saved file."
        ),
    )
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK_PATH)
    parser.add_argument("--receipt-schema", type=Path, default=DEFAULT_RECEIPT_SCHEMA)
    parser.add_argument("--report-schema", type=Path, default=DEFAULT_REPORT_SCHEMA)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--report-out",
        type=Path,
        help="Optional path where the replay-check report is written.",
    )
    args = parser.parse_args()
    try:
        receipt_schema = _json_object(args.receipt_schema)
        jsonschema.Draft202012Validator.check_schema(receipt_schema)
        receipt = _json_object(args.receipt)
        jsonschema.validate(receipt, receipt_schema)
        report = build_contract_receipt_replay_check_report(
            receipt,
            load_contract_pack(args.pack),
            receipt_path=_display_path(args.receipt),
        )
        _validate_report_schema(report, args.report_schema)
        if args.report_out:
            _write_json(args.report_out, report)
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            original = report["original"]
            replayed = report["replayed"] or {}
            print(
                "circle AI receipt replay "
                f"ok={report['ok']} "
                f"path={report['path']} "
                f"failures={report['failure_count']} "
                f"kind={original.get('kind')} "
                f"status={original.get('status')}->{replayed.get('status')} "
                "receipt_fingerprint="
                f"{str(original.get('receipt_content_fingerprint'))[:12]}->"
                f"{str(replayed.get('receipt_content_fingerprint'))[:12]} "
                "replay_command_matches_request="
                f"{report['replay_command_matches_request']}"
            )
            for failure in report["failures"]:
                print(f"failure: {failure}")
        return 0 if report["ok"] else 1
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
    ) as exc:
        report = {
            "schema_id": CHECK_SCHEMA_ID,
            "receipt_schema_id": "circle_calculus.ai_contract_receipt.v0",
            "request_schema_id": "circle_calculus.ai_contract_request.v0",
            "content_fingerprint_algorithm": "sha256",
            "ok": False,
            "failure_count": 1,
            "failures": [str(exc)],
            "path": _display_path(args.receipt),
            "replay_command": None,
            "replay_command_matches_request": False,
            "original": {
                "kind": "rope_position_distinguishability",
                "contract_id": "unavailable",
                "status": "outside_scope",
                "request_passed": None,
                "decision_verdict": "outside_scope",
                "decision_assurance": "unsupported",
                "request_content_fingerprint": "0" * 64,
                "normalized_request_fingerprint": "0" * 64,
                "receipt_content_fingerprint": "0" * 64,
            },
            "replayed": None,
            "comparison": {
                "kind_matches": False,
                "contract_id_matches": False,
                "status_matches": False,
                "request_passed_matches": False,
                "decision_verdict_matches": False,
                "decision_assurance_matches": False,
                "request_content_fingerprint_matches": False,
                "normalized_request_fingerprint_matches": False,
                "receipt_content_fingerprint_matches": False,
                "all_replay_fields_match": False,
            },
        }
        if args.report_out:
            _write_json(args.report_out, report)
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"circle AI receipt replay ok=False failures=1 path={args.receipt}")
            print(f"failure: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
