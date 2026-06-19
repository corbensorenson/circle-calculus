#!/usr/bin/env python3
"""Validate the copyable downstream CI acceptance example output.

The example script intentionally uses only the Python standard library. This
checker is repository-side: it can depend on jsonschema and verifies that the
copyable script still emits reports and receipts matching the generated public
schema sidecars.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLE = ROOT / "examples" / "downstream_ci_accept_circle_ai_contracts.py"
DEFAULT_PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_POLICY = ROOT / "examples" / "circle_ai_contract_acceptance_policy.json"
DEFAULT_REPORT_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_acceptance_policy_report.schema.json"
)
DEFAULT_RECEIPT_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_contract_acceptance_receipt.schema.json"
)
DEFAULT_REJECTION_REPORT_SCHEMA = (
    ROOT
    / "site"
    / "data"
    / "generated"
    / "circle_ai_downstream_rejection_report.schema.json"
)


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_example(
    *,
    example: Path,
    pack: Path,
    policy: Path,
    extra_args: Iterable[str] = (),
) -> dict:
    command = [
        sys.executable,
        str(example),
        "--pack",
        str(pack),
        "--policy",
        str(policy),
        "--format",
        "json",
        *extra_args,
    ]
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise TypeError("downstream CI example must emit a JSON object")
    return payload


def _run_example_failure(
    *,
    example: Path,
    pack: Path,
    policy: Path,
    extra_args: Iterable[str] = (),
) -> dict:
    command = [
        sys.executable,
        str(example),
        "--pack",
        str(pack),
        "--policy",
        str(policy),
        "--format",
        "json",
        *extra_args,
    ]
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        raise ValueError("downstream CI example unexpectedly accepted failure case")
    payload = json.loads(result.stderr)
    if not isinstance(payload, dict):
        raise TypeError("downstream CI failure report must emit a JSON object")
    return payload


def _validate_report(
    payload: dict,
    *,
    report_schema: dict,
    receipt_schema: dict,
) -> None:
    jsonschema.validate(payload, report_schema)
    receipts = payload.get("receipts")
    accepted_contracts = payload.get("accepted_contracts")
    if receipts != accepted_contracts:
        raise ValueError("accepted_contracts must match canonical receipts")
    if not isinstance(receipts, list):
        raise TypeError("receipts must be a list")
    for receipt in receipts:
        jsonschema.validate(receipt, receipt_schema)
    policy_summary = payload.get("policy_summary")
    if not isinstance(policy_summary, dict):
        raise TypeError("policy_summary must be an object")
    accepted_kinds = [receipt.get("kind") for receipt in receipts]
    if policy_summary.get("accepted_contract_kinds") != accepted_kinds:
        raise ValueError("policy_summary accepted_contract_kinds drifted")
    if policy_summary.get("accepted_contract_count") != len(receipts):
        raise ValueError("policy_summary accepted_contract_count drifted")
    if policy_summary.get("required_recommendation_count") != sum(
        len(receipt.get("required_recommendation_ids", []))
        for receipt in receipts
    ):
        raise ValueError("policy_summary required_recommendation_count drifted")
    if policy_summary.get("contract_summaries") is None:
        raise ValueError("policy_summary contract_summaries missing")
    planner_summary = payload.get("planner_summary")
    if not isinstance(planner_summary, dict):
        raise TypeError("planner_summary must be an object")
    action_plan = payload.get("action_plan")
    if not isinstance(action_plan, list):
        raise TypeError("action_plan must be a list")
    selected_ids = [action.get("recommendation_id") for action in action_plan]
    if planner_summary.get("selected_recommendation_ids") != selected_ids:
        raise ValueError("planner_summary selected_recommendation_ids drifted")
    if planner_summary.get("selected_recommendation_count") != len(action_plan):
        raise ValueError("planner_summary selected_recommendation_count drifted")


def _validate_failure_report(
    payload: dict,
    *,
    rejection_report_schema: dict,
) -> None:
    jsonschema.validate(payload, rejection_report_schema)
    failures = payload.get("failures")
    if not isinstance(failures, list) or not failures:
        raise TypeError("failure report must include a non-empty failures list")
    if payload.get("failure_count") != len(failures):
        raise ValueError("failure_count must match failures length")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--example",
        default=str(DEFAULT_EXAMPLE),
        help="Path to examples/downstream_ci_accept_circle_ai_contracts.py.",
    )
    parser.add_argument(
        "--pack",
        default=str(DEFAULT_PACK),
        help="Path to circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY),
        help="Path to the pinned acceptance-policy lockfile.",
    )
    parser.add_argument(
        "--report-schema",
        default=str(DEFAULT_REPORT_SCHEMA),
        help="Path to circle_ai_contract_acceptance_policy_report.schema.json.",
    )
    parser.add_argument(
        "--receipt-schema",
        default=str(DEFAULT_RECEIPT_SCHEMA),
        help="Path to circle_ai_contract_acceptance_receipt.schema.json.",
    )
    parser.add_argument(
        "--rejection-report-schema",
        default=str(DEFAULT_REJECTION_REPORT_SCHEMA),
        help="Path to circle_ai_downstream_rejection_report.schema.json.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact success summary.",
    )
    args = parser.parse_args()

    example = _resolve(args.example)
    pack = _resolve(args.pack)
    policy = _resolve(args.policy)
    report_schema = _load_json(_resolve(args.report_schema))
    receipt_schema = _load_json(_resolve(args.receipt_schema))
    rejection_report_schema = _load_json(_resolve(args.rejection_report_schema))
    if (
        not isinstance(report_schema, dict)
        or not isinstance(receipt_schema, dict)
        or not isinstance(rejection_report_schema, dict)
    ):
        raise TypeError("schema sidecars must contain JSON objects")
    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.Draft202012Validator.check_schema(rejection_report_schema)

    scenarios = [
        (),
        ("--include-values",),
        (
            "--planner-recommendation",
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "--include-values",
        ),
        (
            "--planner-recommendation",
            "ROPE-USE-D19-MARGIN-FRONTIER",
            "--include-values",
        ),
    ]
    reports = [
        _run_example(
            example=example,
            pack=pack,
            policy=policy,
            extra_args=scenario,
        )
        for scenario in scenarios
    ]
    for report in reports:
        _validate_report(
            report,
            report_schema=report_schema,
            receipt_schema=receipt_schema,
        )
    failure_reports = [
        _run_example_failure(
            example=example,
            pack=pack,
            policy=policy,
            extra_args=(
                "--planner-recommendation",
                "NOT-A-RECOMMENDATION",
            ),
        ),
    ]
    for failure_report in failure_reports:
        _validate_failure_report(
            failure_report,
            rejection_report_schema=rejection_report_schema,
        )

    if args.summary:
        selected_counts = [
            str(report.get("planner_recommendation_count")) for report in reports
        ]
        print(
            "circle AI downstream CI example schema ok: "
            f"scenarios={len(reports)} "
            f"failure_scenarios={len(failure_reports)} "
            f"planner_counts={','.join(selected_counts)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
