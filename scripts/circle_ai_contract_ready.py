#!/usr/bin/env python3
"""Read the public Circle AI contract pack as a downstream consumer."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from check_circle_ai_contract_pack import DEFAULT_PACK, find_contract, validate_pack
from circle_math.applications.circle_ai_contract_consumer import (
    ContractConsumerError,
    contract_digest,
    planner_action_plan,
    planner_recommendation_index,
)


ROOT = Path(__file__).resolve().parents[1]
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _load_pack(path: Path) -> dict[str, Any]:
    if not path.is_absolute():
        path = ROOT / path
    return json.loads(path.read_text())


def _readiness_for(pack: dict[str, Any], kind: str) -> dict[str, Any] | None:
    readiness_index = pack.get("contract_readiness_index", {})
    if not isinstance(readiness_index, dict):
        return None
    readiness = readiness_index.get(kind)
    return readiness if isinstance(readiness, dict) else None


def _json_payload(pack: dict[str, Any], kind: str, readiness: dict[str, Any]) -> dict[str, Any]:
    contract = find_contract(pack, kind) or {}
    return {
        "schema_id": pack.get("schema_id"),
        "kind": kind,
        "ready_for_downstream_fixture_use": readiness.get(
            "ready_for_downstream_fixture_use"
        ),
        "readiness": readiness,
        "contract": {
            "id": contract.get("id"),
            "source_paper": contract.get("source_paper"),
            "quickstart_docs": contract.get("quickstart_docs", []),
            "living_book_pages": contract.get("living_book_pages", []),
            "entrypoints": contract.get("entrypoints", []),
            "validation_commands": contract.get("validation_commands", []),
            "theorem_ids": contract.get("theorem_ids", []),
            "dictionary_ids": contract.get("dictionary_ids", []),
            "not_claimed": contract.get("not_claimed"),
        },
    }


def _print_text(kind: str, readiness: dict[str, Any], pack: dict[str, Any]) -> None:
    contract = find_contract(pack, kind) or {}
    ready = readiness.get("ready_for_downstream_fixture_use") is True
    status = "ok" if ready else "not-ready"
    print(f"circle AI contract readiness {status}: {kind}")
    print(
        " ".join(
            [
                f"id={readiness.get('id')}",
                f"ready={ready}",
                f"contract_passed={readiness.get('contract_passed')}",
                f"fields_present={readiness.get('required_fields_present')}",
                f"proof_resolved={readiness.get('all_theorem_ids_resolved')}",
                f"proof_proved={readiness.get('all_theorem_ids_proved')}",
                f"missing_fields={readiness.get('missing_minimum_field_count')}",
                f"unresolved={readiness.get('unresolved_theorem_count')}",
                f"unproved={readiness.get('unproved_theorem_count')}",
                f"theorems={readiness.get('theorem_count')}",
                f"recommendations={readiness.get('planner_recommendation_count', 0)}",
            ]
        )
    )
    quickstart_docs = contract.get("quickstart_docs", [])
    living_book_pages = contract.get("living_book_pages", [])
    entrypoints = contract.get("entrypoints", [])
    validation_commands = contract.get("validation_commands", [])
    if quickstart_docs:
        print("quickstart_docs=" + ",".join(quickstart_docs))
    if living_book_pages:
        print("living_book_pages=" + ",".join(living_book_pages))
    if entrypoints:
        print("entrypoints=" + " | ".join(entrypoints))
    if validation_commands:
        print("validation_commands=" + " | ".join(validation_commands))
    recommendation_ids = readiness.get("planner_recommendation_ids", [])
    if isinstance(recommendation_ids, list) and recommendation_ids:
        print(
            "planner_recommendations="
            + ",".join(str(item) for item in recommendation_ids)
        )


def _print_kind_list(pack: dict[str, Any], output_format: str) -> None:
    readiness_index = pack.get("contract_readiness_index", {})
    if not isinstance(readiness_index, dict):
        readiness_index = {}
    if output_format == "json":
        print(json.dumps(readiness_index, indent=2, sort_keys=True))
        return
    for kind in sorted(readiness_index):
        readiness = readiness_index[kind]
        print(
            " ".join(
                [
                    f"kind={kind}",
                    f"id={readiness.get('id')}",
                    f"ready={readiness.get('ready_for_downstream_fixture_use') is True}",
                    f"proof_proved={readiness.get('all_theorem_ids_proved') is True}",
                    f"missing_fields={readiness.get('missing_minimum_field_count')}",
                    f"unresolved={readiness.get('unresolved_theorem_count')}",
                    f"unproved={readiness.get('unproved_theorem_count')}",
                    f"recommendations={readiness.get('planner_recommendation_count', 0)}",
                ]
            )
        )


def _print_recommendation_list(pack: dict[str, Any], output_format: str) -> None:
    index = planner_recommendation_index(pack)
    if output_format == "json":
        print(json.dumps(index, indent=2, sort_keys=True))
        return
    for recommendation_id in sorted(index):
        record = index[recommendation_id]
        theorem_ids = record.get("theorem_ids", [])
        if not isinstance(theorem_ids, list):
            theorem_ids = []
        print(
            " ".join(
                [
                    f"recommendation={recommendation_id}",
                    f"kind={record.get('kind')}",
                    f"contract={record.get('contract_id')}",
                    f"ready={record.get('ready_for_downstream_fixture_use') is True}",
                    f"action={record.get('action_kind')}",
                    f"scope={record.get('coverage_scope')}",
                    f"status={record.get('status')}",
                    f"theorems={len(theorem_ids)}",
                ]
            )
        )


def _fingerprint_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": pack.get("schema_id"),
        "content_fingerprint_algorithm": pack.get("content_fingerprint_algorithm"),
        "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
        "contract_fingerprint_index": pack.get("contract_fingerprint_index", {}),
    }


def _print_fingerprints(pack: dict[str, Any], output_format: str) -> None:
    payload = _fingerprint_payload(pack)
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        " ".join(
            [
                "circle AI contract fingerprints ok:",
                f"algorithm={payload.get('content_fingerprint_algorithm')}",
                f"pack={payload.get('pack_content_fingerprint')}",
            ]
        )
    )
    index = payload.get("contract_fingerprint_index", {})
    if not isinstance(index, dict):
        return
    for kind in sorted(index):
        record = index[kind]
        if not isinstance(record, dict):
            continue
        print(
            " ".join(
                [
                    f"fingerprint.{kind}",
                    f"id={record.get('id')}",
                    f"algorithm={record.get('content_fingerprint_algorithm')}",
                    f"content={record.get('content_fingerprint')}",
                ]
            )
        )


def _parse_contract_fingerprint_expectations(
    values: list[str],
) -> tuple[dict[str, str], list[str]]:
    expectations: dict[str, str] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--expect-contract-fingerprint must have the form kind=sha256"
            )
            continue
        kind, fingerprint = raw.split("=", 1)
        kind = kind.strip()
        fingerprint = fingerprint.strip()
        if not kind:
            failures.append("--expect-contract-fingerprint kind is empty")
            continue
        if not SHA256_HEX_RE.fullmatch(fingerprint):
            failures.append(
                f"--expect-contract-fingerprint for {kind} is not a lowercase "
                "sha256 hex string"
            )
            continue
        if kind in expectations:
            failures.append(
                f"--expect-contract-fingerprint repeats contract kind: {kind}"
            )
            continue
        expectations[kind] = fingerprint
    return expectations, failures


def _verify_fingerprint_expectations(
    pack: dict[str, Any],
    *,
    expected_pack_fingerprint: str | None,
    expected_contract_fingerprints: dict[str, str],
) -> list[str]:
    failures: list[str] = []
    if expected_pack_fingerprint is not None:
        if not SHA256_HEX_RE.fullmatch(expected_pack_fingerprint):
            failures.append(
                "--expect-pack-fingerprint is not a lowercase sha256 hex string"
            )
        elif pack.get("pack_content_fingerprint") != expected_pack_fingerprint:
            failures.append(
                "pack fingerprint mismatch: expected "
                f"{expected_pack_fingerprint}, got {pack.get('pack_content_fingerprint')}"
            )

    index = pack.get("contract_fingerprint_index", {})
    if not isinstance(index, dict):
        index = {}
    for kind, expected in expected_contract_fingerprints.items():
        record = index.get(kind)
        if not isinstance(record, dict):
            failures.append(f"unknown contract kind for fingerprint expectation: {kind}")
            continue
        actual = record.get("content_fingerprint")
        if actual != expected:
            failures.append(
                f"{kind} fingerprint mismatch: expected {expected}, got {actual}"
            )
    return failures


def _print_action_plan_text(plan: dict[str, Any]) -> None:
    selected_kinds = plan.get("selected_kinds", [])
    actions = plan.get("action_plan", [])
    print(
        "circle AI action plan ok: "
        f"kinds={','.join(str(kind) for kind in selected_kinds)} "
        f"actions={plan.get('planner_recommendation_count')} "
        f"ready_actions={plan.get('ready_recommendation_count')} "
        f"includes_values={plan.get('planner_includes_values') is True}"
    )
    if not isinstance(actions, list):
        return
    for action in actions:
        if not isinstance(action, dict):
            continue
        theorem_ids = action.get("theorem_ids", [])
        if not isinstance(theorem_ids, list):
            theorem_ids = []
        parts = [
            f"action.{action.get('recommendation_id')}",
            f"kind={action.get('kind')}",
            f"contract={action.get('contract_id')}",
            f"ready={action.get('ready_for_downstream_fixture_use') is True}",
            f"action_kind={action.get('action_kind')}",
            f"scope={action.get('coverage_scope')}",
            f"status={action.get('status')}",
            "theorems=" + ",".join(str(item) for item in theorem_ids),
        ]
        evidence_values = action.get("evidence_values")
        if isinstance(evidence_values, dict):
            parts.append("evidence_values=" + json.dumps(evidence_values, sort_keys=True))
        action_parameters = action.get("action_parameters")
        if isinstance(action_parameters, dict):
            parts.append("action_parameters=" + json.dumps(action_parameters, sort_keys=True))
        print(" ".join(parts))


def _print_digest_text(digest: dict[str, Any]) -> None:
    evidence = digest.get("evidence_fields", {})
    field_catalog = digest.get("field_catalog", {})
    recommendations = digest.get("planner_recommendations", [])
    missing = digest.get("missing_requested_fields", [])
    print(f"circle AI contract digest ok: {digest.get('kind')}")
    print(
        " ".join(
            [
                f"id={digest.get('contract_id')}",
                f"ready={digest.get('ready_for_downstream_fixture_use')}",
                f"fields={len(evidence) if isinstance(evidence, dict) else 0}",
                f"missing={len(missing) if isinstance(missing, list) else 0}",
                f"theorems={len(digest.get('theorem_ids', []))}",
            ]
        )
    )
    if isinstance(evidence, dict):
        for key in sorted(evidence):
            print(f"evidence.{key}={json.dumps(evidence[key], sort_keys=True)}")
    if isinstance(field_catalog, dict):
        for key in sorted(field_catalog):
            entry = field_catalog[key]
            if not isinstance(entry, dict):
                continue
            print(
                " ".join(
                    [
                        f"field.{key}.value_kind={entry.get('value_kind')}",
                        f"proof_role={entry.get('proof_role')}",
                    ]
                )
            )
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            if not isinstance(recommendation, dict):
                continue
            theorem_ids = recommendation.get("theorem_ids", [])
            if not isinstance(theorem_ids, list):
                theorem_ids = []
            print(
                " ".join(
                    [
                        f"recommendation.{recommendation.get('id')}",
                        f"action={recommendation.get('action_kind')}",
                        f"scope={recommendation.get('coverage_scope')}",
                        f"status={recommendation.get('status')}",
                        "theorems=" + ",".join(str(item) for item in theorem_ids),
                    ]
                )
            )
    validation_commands = digest.get("validation_commands", [])
    if isinstance(validation_commands, list) and validation_commands:
        print(
            "validation_commands="
            + " | ".join(str(command) for command in validation_commands)
        )
    if missing:
        print("missing_requested_fields=" + ",".join(str(field) for field in missing))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check one Circle AI contract readiness entry as an external "
            "consumer without reading Lean or manifest YAML."
        )
    )
    parser.add_argument(
        "--path",
        default=str(DEFAULT_PACK),
        help="Path to circle_ai_contract_pack.json.",
    )
    parser.add_argument("--kind", help="Contract kind to require as downstream-ready.")
    parser.add_argument(
        "--list-kinds",
        action="store_true",
        help="List available contract kinds and readiness flags.",
    )
    parser.add_argument(
        "--list-recommendations",
        action="store_true",
        help="List all indexed planner recommendations across ready contracts.",
    )
    parser.add_argument(
        "--fingerprints",
        action="store_true",
        help=(
            "Print the pack fingerprint and per-contract content fingerprints "
            "for downstream audit logs."
        ),
    )
    parser.add_argument(
        "--expect-pack-fingerprint",
        help=(
            "Require the exported pack fingerprint to match this lowercase "
            "sha256 hex string."
        ),
    )
    parser.add_argument(
        "--expect-contract-fingerprint",
        action="append",
        default=[],
        metavar="KIND=SHA256",
        help=(
            "Require one contract content fingerprint to match. Repeat for "
            "multiple contract kinds."
        ),
    )
    parser.add_argument(
        "--action-plan",
        action="store_true",
        help=(
            "Emit a theorem-linked planner action plan. With --kind, emit "
            "actions for that one contract; without --kind, emit all ready "
            "contract actions."
        ),
    )
    parser.add_argument(
        "--include-values",
        action="store_true",
        help=(
            "Include concrete evidence values and recommendation parameters in "
            "--action-plan output."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the selected kind or kind list.",
    )
    parser.add_argument(
        "--digest",
        action="store_true",
        help=(
            "Emit a compact copy-safe contract digest instead of readiness "
            "metadata for the selected kind."
        ),
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help=(
            "Evidence field to include in --digest output. Repeat to request "
            "multiple fields. Defaults to the contract kind's minimum fields."
        ),
    )
    parser.add_argument(
        "--include-field-metadata",
        action="store_true",
        help=(
            "Include field descriptions, JSON value kinds, and proof roles in "
            "--digest output."
        ),
    )
    parser.add_argument(
        "--include-recommendations",
        action="store_true",
        help=(
            "Include optional planner recommendation records in --digest output."
        ),
    )
    args = parser.parse_args()

    pack = _load_pack(Path(args.path))
    failures = validate_pack(pack)
    if failures:
        print("circle AI contract pack is not valid:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    expected_contracts, parse_failures = _parse_contract_fingerprint_expectations(
        args.expect_contract_fingerprint,
    )
    fingerprint_failures = parse_failures + _verify_fingerprint_expectations(
        pack,
        expected_pack_fingerprint=args.expect_pack_fingerprint,
        expected_contract_fingerprints=expected_contracts,
    )
    if fingerprint_failures:
        print("circle AI contract fingerprint expectation failed:", file=sys.stderr)
        for failure in fingerprint_failures:
            print(f"  - {failure}", file=sys.stderr)
        return 3

    if args.list_kinds:
        if (
            args.digest
            or args.list_recommendations
            or args.action_plan
            or args.fingerprints
        ):
            parser.error(
                "--list-kinds cannot be combined with --digest or "
                "--list-recommendations or --action-plan or --fingerprints"
            )
        _print_kind_list(pack, args.format)
        return 0

    if args.list_recommendations:
        if args.digest or args.action_plan or args.fingerprints:
            parser.error(
                "--list-recommendations cannot be used with --digest or "
                "--action-plan or --fingerprints"
            )
        _print_recommendation_list(pack, args.format)
        return 0

    if args.fingerprints:
        if args.digest or args.action_plan:
            parser.error("--fingerprints cannot be used with --digest or --action-plan")
        _print_fingerprints(pack, args.format)
        return 0

    if args.action_plan:
        if args.digest:
            parser.error("--digest cannot be used with --action-plan")
        selected_kinds = (args.kind,) if args.kind else None
        try:
            plan = planner_action_plan(
                pack,
                selected_kinds,
                include_values=args.include_values,
            )
        except ContractConsumerError as exc:
            print(f"contract action plan failed: {exc}", file=sys.stderr)
            return 2
        if args.format == "json":
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            _print_action_plan_text(plan)
        return 0

    if not args.kind:
        parser.error(
            "--kind is required unless --list-kinds or --list-recommendations "
            "is passed"
        )

    readiness = _readiness_for(pack, args.kind)
    if readiness is None:
        print(f"unknown contract kind: {args.kind}", file=sys.stderr)
        return 1

    if args.digest:
        try:
            digest = contract_digest(
                pack,
                args.kind,
                fields=tuple(args.field) if args.field else None,
                include_field_metadata=args.include_field_metadata,
                include_recommendations=args.include_recommendations,
            )
        except ContractConsumerError as exc:
            print(f"contract digest failed: {exc}", file=sys.stderr)
            return 2
        if args.format == "json":
            print(json.dumps(digest, indent=2, sort_keys=True))
        else:
            _print_digest_text(digest)
        return 0

    if args.format == "json":
        print(json.dumps(_json_payload(pack, args.kind, readiness), indent=2, sort_keys=True))
    else:
        _print_text(args.kind, readiness, pack)

    return 0 if readiness.get("ready_for_downstream_fixture_use") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
