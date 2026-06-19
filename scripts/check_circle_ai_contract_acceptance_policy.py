#!/usr/bin/env python3
"""Check a pinned downstream Circle AI contract acceptance policy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

from circle_math.applications.circle_ai_contract_consumer import (
    ContractAcceptancePolicyError,
    contract_acceptance_policy_report,
    load_contract_pack,
    refresh_acceptance_policy_fingerprints,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_POLICY = ROOT / "examples" / "circle_ai_contract_acceptance_policy.json"


def _resolve(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _validate_report_schema(pack: dict[str, Any], report: dict[str, Any]) -> None:
    acceptance_policy = pack.get("acceptance_policy")
    if not isinstance(acceptance_policy, dict):
        raise ValueError("pack is missing acceptance_policy schema metadata")

    report_schema_ref = acceptance_policy.get("report_schema_path")
    receipt_schema_ref = acceptance_policy.get("receipt_schema_path")
    if not isinstance(report_schema_ref, str) or not report_schema_ref:
        raise ValueError("acceptance_policy.report_schema_path must be a path")
    if not isinstance(receipt_schema_ref, str) or not receipt_schema_ref:
        raise ValueError("acceptance_policy.receipt_schema_path must be a path")

    report_schema = _load_json(_resolve(report_schema_ref))
    receipt_schema = _load_json(_resolve(receipt_schema_ref))
    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(report, report_schema)
    receipts = report.get("receipts")
    if not isinstance(receipts, list):
        raise ValueError("acceptance report receipts must be a list")
    for receipt in receipts:
        jsonschema.validate(receipt, receipt_schema)


def _print_text(report: dict[str, Any]) -> None:
    print(
        "circle AI contract acceptance policy ok: "
        f"id={report.get('policy_id')} "
        f"contracts={report.get('contract_count')} "
        f"receipts={report.get('receipt_count')} "
        f"accepted={report.get('accepted') is True}"
    )
    print(
        " ".join(
            [
                f"fingerprint_algorithm={report.get('content_fingerprint_algorithm')}",
                f"pack={report.get('pack_content_fingerprint')}",
            ]
        )
    )
    receipts = report.get("receipts", [])
    if not isinstance(receipts, list):
        return
    for receipt in receipts:
        if not isinstance(receipt, dict):
            continue
        fields = receipt.get("required_fields", [])
        theorem_ids = receipt.get("required_theorem_ids", [])
        recommendations = receipt.get("required_recommendation_ids", [])
        recommendation_evidence_fields = receipt.get(
            "required_recommendation_evidence_fields",
            {},
        )
        recommendation_theorem_ids = receipt.get(
            "required_recommendation_theorem_ids",
            {},
        )
        recommendation_action_parameters = receipt.get(
            "required_recommendation_action_parameters",
            {},
        )
        recommendation_action_parameter_paths = receipt.get(
            "required_recommendation_action_parameter_paths",
            {},
        )
        recommendation_evidence_field_count = (
            sum(
                len(value)
                for value in recommendation_evidence_fields.values()
                if isinstance(value, list)
            )
            if isinstance(recommendation_evidence_fields, dict)
            else 0
        )
        recommendation_theorem_count = (
            sum(
                len(value)
                for value in recommendation_theorem_ids.values()
                if isinstance(value, list)
            )
            if isinstance(recommendation_theorem_ids, dict)
            else 0
        )
        recommendation_action_parameter_count = (
            sum(
                len(value)
                for value in recommendation_action_parameters.values()
                if isinstance(value, list)
            )
            if isinstance(recommendation_action_parameters, dict)
            else 0
        )
        recommendation_action_parameter_path_count = (
            sum(
                len(value)
                for value in recommendation_action_parameter_paths.values()
                if isinstance(value, list)
            )
            if isinstance(recommendation_action_parameter_paths, dict)
            else 0
        )
        print(
            " ".join(
                [
                    f"receipt.{receipt.get('kind')}",
                    f"contract={receipt.get('contract_id')}",
                    f"fields={len(fields) if isinstance(fields, list) else 0}",
                    (
                        "required_theorems="
                        f"{len(theorem_ids) if isinstance(theorem_ids, list) else 0}"
                    ),
                    (
                        "recommendations="
                        f"{len(recommendations) if isinstance(recommendations, list) else 0}"
                    ),
                    (
                        "recommendation_evidence_fields="
                        f"{recommendation_evidence_field_count}"
                    ),
                    f"recommendation_theorems={recommendation_theorem_count}",
                    (
                        "recommendation_action_parameters="
                        f"{recommendation_action_parameter_count}"
                    ),
                    (
                        "recommendation_action_parameter_paths="
                        f"{recommendation_action_parameter_path_count}"
                    ),
                    f"fingerprint={receipt.get('contract_content_fingerprint')}",
                ]
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a pinned Circle AI contract acceptance policy and emit "
            "strict receipts for the selected contracts."
        ),
    )
    parser.add_argument(
        "--pack",
        default=str(DEFAULT_PACK),
        help="Path to generated circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY),
        help="Path to circle_ai_contract_acceptance_policy.json.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format for the accepted policy report.",
    )
    parser.add_argument(
        "--include-field-metadata",
        action="store_true",
        help="Include field metadata for policy entries that do not override it.",
    )
    parser.add_argument(
        "--print-refreshed-policy",
        action="store_true",
        help=(
            "Print the selected policy with only the expected pack and "
            "contract fingerprints refreshed from --pack. Requirement pins are "
            "preserved."
        ),
    )
    args = parser.parse_args()

    try:
        pack = load_contract_pack(_resolve(args.pack))
        policy = _load_json(_resolve(args.policy))
        if args.print_refreshed_policy:
            refreshed_policy = refresh_acceptance_policy_fingerprints(pack, policy)
            print(json.dumps(refreshed_policy, indent=2, sort_keys=True))
            return 0
        report = contract_acceptance_policy_report(
            pack,
            policy,
            include_field_metadata=args.include_field_metadata,
        )
        _validate_report_schema(pack, report)
    except (
        ContractAcceptancePolicyError,
        OSError,
        ValueError,
        jsonschema.ValidationError,
        jsonschema.SchemaError,
        json.JSONDecodeError,
    ) as exc:
        print(f"circle AI contract acceptance policy failed: {exc}", file=sys.stderr)
        return 4

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
