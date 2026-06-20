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
    load_contract_pack,
    validate_contract_receipt,
)
from circle_math.applications.circle_ai_contract_consumer import (  # noqa: E402
    find_contract,
)
from circle_math.applications.circle_ai_contract_runner import (  # noqa: E402
    STATUS_VALUES,
)


CHECK_SCHEMA_ID = "circle_calculus.ai_contract_receipt_file_check.v0"
DEFAULT_PACK_PATH = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_RECEIPT_SCHEMA = (
    ROOT / "site" / "data" / "generated" / "circle_ai_contract_receipt.schema.json"
)


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


def _as_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _receipt_pack_failures(
    *,
    receipt: dict[str, Any],
    pack: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    support = receipt.get("support")
    if not isinstance(support, dict):
        return ["support must be an object before pack checks can run"]

    pack_fingerprint = pack.get("pack_content_fingerprint")
    if support.get("contract_pack_fingerprint") != pack_fingerprint:
        failures.append(
            "support.contract_pack_fingerprint does not match loaded contract pack"
        )

    kind = receipt.get("kind")
    contract = find_contract(pack, str(kind)) if isinstance(kind, str) else None
    if contract is None:
        failures.append("receipt kind is not present in the loaded contract pack")
        return failures

    contract_id = contract.get("id")
    if receipt.get("contract_id") != contract_id:
        failures.append("contract_id does not match loaded contract record")
    if support.get("contract_id") != contract_id:
        failures.append("support.contract_id does not match loaded contract record")

    contract_fingerprint = contract.get("content_fingerprint")
    if support.get("contract_content_fingerprint") != contract_fingerprint:
        failures.append(
            "support.contract_content_fingerprint does not match loaded contract"
        )

    fingerprint_index = pack.get("contract_fingerprint_index")
    index_entry = (
        fingerprint_index.get(kind)
        if isinstance(fingerprint_index, dict) and isinstance(kind, str)
        else None
    )
    if not isinstance(index_entry, dict):
        failures.append("loaded contract pack is missing a fingerprint-index entry")
    else:
        if index_entry.get("id") != contract_id:
            failures.append("contract fingerprint index id disagrees with contract")
        if index_entry.get("content_fingerprint") != contract_fingerprint:
            failures.append(
                "contract fingerprint index content hash disagrees with contract"
            )

    proof_status = receipt.get("proof_status")
    receipt_theorem_ids = (
        _as_string_set(proof_status.get("theorem_ids"))
        if isinstance(proof_status, dict)
        else set()
    )
    contract_theorem_ids = _as_string_set(contract.get("theorem_ids"))
    missing_from_contract = sorted(receipt_theorem_ids - contract_theorem_ids)
    if missing_from_contract:
        failures.append(
            "receipt theorem ids are not in loaded contract: "
            + ",".join(missing_from_contract)
        )

    contract_proof_status = contract.get("proof_status")
    contract_all_proved = (
        isinstance(contract_proof_status, dict)
        and contract_proof_status.get("all_theorem_ids_resolved") is True
        and contract_proof_status.get("all_theorem_ids_proved") is True
    )
    if receipt.get("status") in {"proved", "impossible"} and not contract_all_proved:
        failures.append("proved/impossible receipt requires proved contract theorems")

    return failures


def _gate_failures(
    *,
    receipt: dict[str, Any],
    required_statuses: tuple[str, ...],
    require_passed: bool,
) -> list[str]:
    failures: list[str] = []
    status = receipt.get("status")
    if required_statuses and status not in required_statuses:
        failures.append(
            f"receipt status {status!r} did not match required status set: "
            + ", ".join(required_statuses)
        )
    if require_passed and receipt.get("request_passed") is not True:
        failures.append(
            "receipt request_passed was not true "
            f"(got {receipt.get('request_passed')!r})"
        )
    return failures


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
            path_failures.extend(validate_contract_receipt(receipt))
            path_failures.extend(_receipt_pack_failures(receipt=receipt, pack=pack))
            path_failures.extend(
                _gate_failures(
                    receipt=receipt,
                    required_statuses=required_statuses,
                    require_passed=require_passed,
                )
            )
            summaries.append(
                {
                    "path": _display_path(path),
                    "kind": receipt.get("kind"),
                    "contract_id": receipt.get("contract_id"),
                    "status": receipt.get("status"),
                    "request_passed": receipt.get("request_passed"),
                    "theorem_count": (
                        receipt.get("proof_status", {}).get("theorem_count")
                        if isinstance(receipt.get("proof_status"), dict)
                        else None
                    ),
                    "receipt_content_fingerprint": receipt.get(
                        "receipt_content_fingerprint"
                    ),
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
    parser.add_argument("--format", choices=("text", "json"), default="text")
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
                f"theorems={summary['theorem_count']}"
            )
        for failure in report["failures"]:
            print(f"failure={failure}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
