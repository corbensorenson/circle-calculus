#!/usr/bin/env python3
"""Copyable JSON Schema validation example for the Circle AI contract pack.

This script intentionally does not import Circle modules. It is a downstream
consumer pattern: read a generated pack and pinned acceptance policy, read their
JSON Schema sidecars, and validate JSON shape before doing project-specific
work.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        default="site/data/generated/circle_ai_contract_pack.json",
        help="Path to circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--schema",
        default="site/data/generated/circle_ai_contract_pack.schema.json",
        help="Path to circle_ai_contract_pack.schema.json.",
    )
    parser.add_argument(
        "--policy",
        default="examples/circle_ai_contract_acceptance_policy.json",
        help="Path to a pinned Circle AI acceptance-policy lockfile.",
    )
    parser.add_argument(
        "--policy-schema",
        default="site/data/generated/circle_ai_contract_acceptance_policy.schema.json",
        help="Path to circle_ai_contract_acceptance_policy.schema.json.",
    )
    parser.add_argument(
        "--policy-report",
        default=None,
        help=(
            "Optional path to a JSON report emitted by "
            "check_circle_ai_contract_acceptance_policy.py --format json."
        ),
    )
    parser.add_argument(
        "--policy-report-schema",
        default=(
            "site/data/generated/"
            "circle_ai_contract_acceptance_policy_report.schema.json"
        ),
        help="Path to circle_ai_contract_acceptance_policy_report.schema.json.",
    )
    parser.add_argument(
        "--receipt-schema",
        default="site/data/generated/circle_ai_contract_acceptance_receipt.schema.json",
        help="Path to circle_ai_contract_acceptance_receipt.schema.json.",
    )
    parser.add_argument(
        "--rejection-report",
        default=None,
        help=(
            "Optional path to a JSON rejection report emitted by "
            "downstream_ci_accept_circle_ai_contracts.py --format json."
        ),
    )
    parser.add_argument(
        "--rejection-report-schema",
        default="site/data/generated/circle_ai_downstream_rejection_report.schema.json",
        help="Path to circle_ai_downstream_rejection_report.schema.json.",
    )
    parser.add_argument(
        "--skip-policy",
        action="store_true",
        help="Validate only the contract pack and pack schema.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print schema id, contract count, and contract kinds after validation.",
    )
    args = parser.parse_args()

    pack_path = Path(args.pack)
    schema_path = Path(args.schema)
    pack = json.loads(pack_path.read_text())
    schema = json.loads(schema_path.read_text())

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(pack, schema)
    policy = None
    policy_report = None
    rejection_report = None
    if not args.skip_policy:
        policy_path = Path(args.policy)
        policy_schema_path = Path(args.policy_schema)
        policy = json.loads(policy_path.read_text())
        policy_schema = json.loads(policy_schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(policy_schema)
        jsonschema.validate(policy, policy_schema)
    if args.policy_report is not None:
        report_path = Path(args.policy_report)
        report_schema_path = Path(args.policy_report_schema)
        receipt_schema_path = Path(args.receipt_schema)
        policy_report = json.loads(report_path.read_text())
        report_schema = json.loads(report_schema_path.read_text())
        receipt_schema = json.loads(receipt_schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(report_schema)
        jsonschema.Draft202012Validator.check_schema(receipt_schema)
        jsonschema.validate(policy_report, report_schema)
        receipts = policy_report.get("receipts", [])
        if not isinstance(receipts, list):
            raise TypeError("policy report receipts must be a list")
        for receipt in receipts:
            jsonschema.validate(receipt, receipt_schema)
    if args.rejection_report is not None:
        rejection_report_path = Path(args.rejection_report)
        rejection_report_schema_path = Path(args.rejection_report_schema)
        rejection_report = json.loads(rejection_report_path.read_text())
        rejection_report_schema = json.loads(rejection_report_schema_path.read_text())
        jsonschema.Draft202012Validator.check_schema(rejection_report_schema)
        jsonschema.validate(rejection_report, rejection_report_schema)

    if args.summary:
        contracts = pack.get("contracts", [])
        kinds = [
            contract.get("kind")
            for contract in contracts
            if isinstance(contract, dict) and isinstance(contract.get("kind"), str)
        ]
        print(
            " ".join(
                [
                    "circle AI contract schema ok:",
                    f"schema_id={pack.get('schema_id')}",
                    f"contracts={len(contracts) if isinstance(contracts, list) else 0}",
                    f"policy_schema_id={policy.get('schema_id') if isinstance(policy, dict) else 'skipped'}",
                    "policy_report_schema_id="
                    + (
                        str(policy_report.get("acceptance_policy_report_schema"))
                        if isinstance(policy_report, dict)
                        else "skipped"
                    ),
                    "rejection_report_schema_id="
                    + (
                        str(rejection_report.get("schema_id"))
                        if isinstance(rejection_report, dict)
                        else "skipped"
                    ),
                    "kinds=" + ",".join(sorted(kinds)),
                ]
            )
        )
    else:
        print(f"circle AI contract schema ok: {pack_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
