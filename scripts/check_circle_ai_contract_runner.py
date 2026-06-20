#!/usr/bin/env python
"""Validate public Circle AI contract-runner request examples and receipts."""

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
    build_contract_request_validation_report,
    build_contract_receipt_from_request,
    load_contract_pack,
    validate_contract_receipt,
    validate_contract_request,
)


DEFAULT_EXAMPLE_DIR = ROOT / "examples" / "circle_ai_requests"
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
DEFAULT_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
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


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def check_runner_examples(
    *,
    example_dir: Path = DEFAULT_EXAMPLE_DIR,
    pack_path: Path = DEFAULT_PACK_PATH,
    request_schema_path: Path = DEFAULT_REQUEST_SCHEMA,
    request_validation_schema_path: Path = DEFAULT_REQUEST_VALIDATION_SCHEMA,
    receipt_schema_path: Path = DEFAULT_RECEIPT_SCHEMA,
    receipt_out_dir: Path | None = None,
) -> dict[str, Any]:
    request_schema = _json(request_schema_path)
    request_validation_schema = _json(request_validation_schema_path)
    receipt_schema = _json(receipt_schema_path)
    jsonschema.Draft202012Validator.check_schema(request_schema)
    jsonschema.Draft202012Validator.check_schema(request_validation_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    pack = load_contract_pack(pack_path)
    summaries: list[dict[str, Any]] = []
    failures: list[str] = []

    for path in _request_paths(example_dir):
        try:
            request = _json(path)
            jsonschema.validate(request, request_schema)
            validation_report = build_contract_request_validation_report(request)
            jsonschema.validate(validation_report, request_validation_schema)
            request_failures = validate_contract_request(request)
            if request_failures:
                failures.append(f"{path}: " + "; ".join(request_failures))
                continue
            receipt = build_contract_receipt_from_request(request, pack=pack)
            receipt_failures = validate_contract_receipt(receipt)
            if receipt_failures:
                failures.append(f"{path}: " + "; ".join(receipt_failures))
                continue
            jsonschema.validate(receipt, receipt_schema)
            receipt_path = None
            if receipt_out_dir is not None:
                receipt_path = receipt_out_dir / f"{path.stem.removesuffix('_request')}_receipt.json"
                _write_json(receipt_path, receipt)
            summaries.append(
                {
                    "request_path": _display_path(path),
                    "receipt_path": (
                        None if receipt_path is None else _display_path(receipt_path)
                    ),
                    "kind": receipt["kind"],
                    "status": receipt["status"],
                    "request_passed": receipt["request_passed"],
                    "theorem_count": receipt["proof_status"]["theorem_count"],
                    "recommendation_count": len(receipt["recommendations"]),
                    "validation_command_count": len(receipt["validation_commands"]),
                    "request_content_fingerprint": receipt[
                        "request_content_fingerprint"
                    ],
                    "normalized_request_fingerprint": receipt[
                        "normalized_request_fingerprint"
                    ],
                    "receipt_content_fingerprint": receipt[
                        "receipt_content_fingerprint"
                    ],
                }
            )
        except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{path}: {exc}")

    return {
        "schema_id": "circle_calculus.ai_contract_runner_check.v0",
        "ok": not failures,
        "example_count": len(summaries),
        "failure_count": len(failures),
        "failures": failures,
        "summaries": summaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Circle AI contract-runner request examples.",
    )
    parser.add_argument("--example-dir", type=Path, default=DEFAULT_EXAMPLE_DIR)
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
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--receipt-out-dir",
        type=Path,
        help="Optional directory where validated receipt JSON files are written.",
    )
    args = parser.parse_args()

    report = check_runner_examples(
        example_dir=args.example_dir,
        pack_path=args.pack,
        request_schema_path=args.request_schema,
        request_validation_schema_path=args.request_validation_schema,
        receipt_schema_path=args.receipt_schema,
        receipt_out_dir=args.receipt_out_dir,
    )
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            "circle AI runner examples "
            f"ok={report['ok']} examples={report['example_count']} "
            f"failures={report['failure_count']}"
        )
        for summary in report["summaries"]:
            print(
                "request="
                f"{summary['request_path']} kind={summary['kind']} "
                f"status={summary['status']} "
                f"passed={summary['request_passed']} "
                f"theorems={summary['theorem_count']} "
                f"recommendations={summary['recommendation_count']} "
                f"receipt={summary['receipt_path']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
