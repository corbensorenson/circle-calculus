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
    ContractAcceptanceError,
    ContractAcceptancePolicyError,
    ContractConsumerError,
    contract_acceptance_policy_report,
    contract_acceptance_receipt,
    contract_digest,
    planner_action_plan,
    planner_recommendation_index,
    refresh_acceptance_policy_fingerprints,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "examples" / "circle_ai_contract_acceptance_policy.json"
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


def _acceptance_policy_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": pack.get("schema_id"),
        "content_fingerprint_algorithm": pack.get("content_fingerprint_algorithm"),
        "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
        "acceptance_policy": pack.get("acceptance_policy", {}),
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_absolute():
        path = ROOT / path
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _print_acceptance_policy(pack: dict[str, Any], output_format: str) -> None:
    payload = _acceptance_policy_payload(pack)
    policy = payload.get("acceptance_policy", {})
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if not isinstance(policy, dict):
        policy = {}
    print(
        " ".join(
            [
                "circle AI acceptance policy ok:",
                f"schema={policy.get('schema_id')}",
                f"report_schema={policy.get('report_schema_id')}",
                f"policy={policy.get('default_policy_path')}",
                f"checker={policy.get('checker')}",
                f"standalone={policy.get('standalone_checker')}",
                f"pack={payload.get('pack_content_fingerprint')}",
            ]
        )
    )
    refresh_command = policy.get("fingerprint_refresh_command")
    if isinstance(refresh_command, str) and refresh_command:
        print(f"fingerprint_refresh_command={refresh_command}")
    pinned_keys = policy.get("pinned_requirement_keys", [])
    if isinstance(pinned_keys, list) and pinned_keys:
        print("pinned_requirement_keys=" + ",".join(str(key) for key in pinned_keys))
    validation_commands = policy.get("validation_commands", [])
    if isinstance(validation_commands, list) and validation_commands:
        print(
            "validation_commands="
            + " | ".join(str(command) for command in validation_commands)
        )


def _print_acceptance_policy_report_text(report: dict[str, Any]) -> None:
    print(
        "circle AI acceptance policy report ok: "
        f"id={report.get('policy_id')} "
        f"contracts={report.get('contract_count')} "
        f"receipts={report.get('receipt_count')} "
        f"accepted={report.get('accepted') is True}"
    )
    print(
        " ".join(
            [
                f"schema={report.get('acceptance_policy_report_schema')}",
                f"policy_schema={report.get('policy_schema')}",
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
        required_fields = receipt.get("required_fields", [])
        required_theorem_ids = receipt.get("required_theorem_ids", [])
        required_recommendation_ids = receipt.get("required_recommendation_ids", [])
        print(
            " ".join(
                [
                    f"receipt.{receipt.get('kind')}",
                    f"contract={receipt.get('contract_id')}",
                    f"accepted={receipt.get('accepted') is True}",
                    f"fields={len(required_fields) if isinstance(required_fields, list) else 0}",
                    (
                        "theorems="
                        f"{len(required_theorem_ids) if isinstance(required_theorem_ids, list) else 0}"
                    ),
                    (
                        "recommendations="
                        f"{len(required_recommendation_ids) if isinstance(required_recommendation_ids, list) else 0}"
                    ),
                    f"fingerprint={receipt.get('contract_content_fingerprint')}",
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


def _parse_recommendation_evidence_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-evidence-field must have the form "
                "RECOMMENDATION_ID=field_name"
            )
            continue
        recommendation_id, field = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        field = field.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-evidence-field recommendation id is empty"
            )
            continue
        if not field:
            failures.append(
                "--require-recommendation-evidence-field field name is empty"
            )
            continue
        fields = requirements.setdefault(recommendation_id, [])
        if field in fields:
            failures.append(
                "--require-recommendation-evidence-field repeats "
                f"{recommendation_id}={field}"
            )
            continue
        fields.append(field)
    return {
        recommendation_id: tuple(fields)
        for recommendation_id, fields in requirements.items()
    }, failures


def _parse_recommendation_theorem_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-theorem must have the form "
                "RECOMMENDATION_ID=THEOREM_ID"
            )
            continue
        recommendation_id, theorem_id = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        theorem_id = theorem_id.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-theorem recommendation id is empty"
            )
            continue
        if not theorem_id:
            failures.append("--require-recommendation-theorem theorem id is empty")
            continue
        theorem_ids = requirements.setdefault(recommendation_id, [])
        if theorem_id in theorem_ids:
            failures.append(
                "--require-recommendation-theorem repeats "
                f"{recommendation_id}={theorem_id}"
            )
            continue
        theorem_ids.append(theorem_id)
    return {
        recommendation_id: tuple(theorem_ids)
        for recommendation_id, theorem_ids in requirements.items()
    }, failures


def _parse_recommendation_action_parameter_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-action-parameter must have the form "
                "RECOMMENDATION_ID=parameter_key"
            )
            continue
        recommendation_id, parameter_key = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        parameter_key = parameter_key.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-action-parameter recommendation id is empty"
            )
            continue
        if not parameter_key:
            failures.append(
                "--require-recommendation-action-parameter parameter key is empty"
            )
            continue
        parameter_keys = requirements.setdefault(recommendation_id, [])
        if parameter_key in parameter_keys:
            failures.append(
                "--require-recommendation-action-parameter repeats "
                f"{recommendation_id}={parameter_key}"
            )
            continue
        parameter_keys.append(parameter_key)
    return {
        recommendation_id: tuple(parameter_keys)
        for recommendation_id, parameter_keys in requirements.items()
    }, failures


def _parse_recommendation_action_parameter_path_requirements(
    values: list[str],
) -> tuple[dict[str, tuple[str, ...]], list[str]]:
    requirements: dict[str, list[str]] = {}
    failures: list[str] = []
    for raw in values:
        if "=" not in raw:
            failures.append(
                "--require-recommendation-action-parameter-path must have the "
                "form RECOMMENDATION_ID=PARAMETER_PATH"
            )
            continue
        recommendation_id, parameter_path = raw.split("=", 1)
        recommendation_id = recommendation_id.strip()
        parameter_path = parameter_path.strip()
        if not recommendation_id:
            failures.append(
                "--require-recommendation-action-parameter-path "
                "recommendation id is empty"
            )
            continue
        if not parameter_path:
            failures.append(
                "--require-recommendation-action-parameter-path path is empty"
            )
            continue
        parameter_paths = requirements.setdefault(recommendation_id, [])
        if parameter_path in parameter_paths:
            failures.append(
                "--require-recommendation-action-parameter-path repeats "
                f"{recommendation_id}={parameter_path}"
            )
            continue
        parameter_paths.append(parameter_path)
    return {
        recommendation_id: tuple(parameter_paths)
        for recommendation_id, parameter_paths in requirements.items()
    }, failures


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


def _print_receipt_text(receipt: dict[str, Any]) -> None:
    evidence = receipt.get("evidence_fields", {})
    recommendations = receipt.get("planner_recommendations", [])
    recommendation_evidence_fields = receipt.get(
        "required_recommendation_evidence_fields",
        {},
    )
    required_recommendation_theorem_ids = receipt.get(
        "required_recommendation_theorem_ids",
        {},
    )
    required_recommendation_action_parameters = receipt.get(
        "required_recommendation_action_parameters",
        {},
    )
    required_recommendation_action_parameter_paths = receipt.get(
        "required_recommendation_action_parameter_paths",
        {},
    )
    theorem_ids = receipt.get("theorem_ids", [])
    recommendation_evidence_field_count = (
        sum(len(fields) for fields in recommendation_evidence_fields.values())
        if isinstance(recommendation_evidence_fields, dict)
        else 0
    )
    recommendation_theorem_count = (
        sum(len(theorem_ids) for theorem_ids in required_recommendation_theorem_ids.values())
        if isinstance(required_recommendation_theorem_ids, dict)
        else 0
    )
    recommendation_action_parameter_count = (
        sum(
            len(parameter_keys)
            for parameter_keys in required_recommendation_action_parameters.values()
        )
        if isinstance(required_recommendation_action_parameters, dict)
        else 0
    )
    recommendation_action_parameter_path_count = (
        sum(
            len(parameter_paths)
            for parameter_paths in (
                required_recommendation_action_parameter_paths.values()
            )
        )
        if isinstance(required_recommendation_action_parameter_paths, dict)
        else 0
    )
    print(f"circle AI contract receipt ok: {receipt.get('kind')}")
    print(
        " ".join(
            [
                f"id={receipt.get('contract_id')}",
                f"accepted={receipt.get('accepted') is True}",
                f"fields={len(evidence) if isinstance(evidence, dict) else 0}",
                (
                    "recommendations="
                    f"{len(recommendations) if isinstance(recommendations, list) else 0}"
                ),
                f"recommendation_evidence_fields={recommendation_evidence_field_count}",
                f"recommendation_theorems={recommendation_theorem_count}",
                (
                    "recommendation_action_parameters="
                    f"{recommendation_action_parameter_count}"
                ),
                (
                    "recommendation_action_parameter_paths="
                    f"{recommendation_action_parameter_path_count}"
                ),
                f"theorems={len(theorem_ids) if isinstance(theorem_ids, list) else 0}",
            ]
        )
    )
    print(
        " ".join(
            [
                f"fingerprint_algorithm={receipt.get('content_fingerprint_algorithm')}",
                f"pack={receipt.get('pack_content_fingerprint')}",
                f"contract={receipt.get('contract_content_fingerprint')}",
            ]
        )
    )
    if isinstance(evidence, dict):
        for key in sorted(evidence):
            print(f"evidence.{key}={json.dumps(evidence[key], sort_keys=True)}")
    if isinstance(recommendations, list):
        for recommendation in recommendations:
            if not isinstance(recommendation, dict):
                continue
            rec_theorem_ids = recommendation.get("theorem_ids", [])
            if not isinstance(rec_theorem_ids, list):
                rec_theorem_ids = []
            print(
                " ".join(
                    [
                        f"recommendation.{recommendation.get('id')}",
                        f"action={recommendation.get('action_kind')}",
                        f"scope={recommendation.get('coverage_scope')}",
                        f"status={recommendation.get('status')}",
                        "theorems=" + ",".join(str(item) for item in rec_theorem_ids),
                    ]
                )
            )
    if isinstance(recommendation_evidence_fields, dict):
        for recommendation_id in sorted(recommendation_evidence_fields):
            fields = recommendation_evidence_fields[recommendation_id]
            if not isinstance(fields, list):
                continue
            print(
                "required_recommendation_evidence_fields."
                f"{recommendation_id}="
                + ",".join(str(field) for field in fields)
            )
    if isinstance(required_recommendation_theorem_ids, dict):
        for recommendation_id in sorted(required_recommendation_theorem_ids):
            theorem_ids = required_recommendation_theorem_ids[recommendation_id]
            if not isinstance(theorem_ids, list):
                continue
            print(
                "required_recommendation_theorem_ids."
                f"{recommendation_id}="
                + ",".join(str(theorem_id) for theorem_id in theorem_ids)
            )
    if isinstance(required_recommendation_action_parameters, dict):
        for recommendation_id in sorted(required_recommendation_action_parameters):
            parameter_keys = required_recommendation_action_parameters[
                recommendation_id
            ]
            if not isinstance(parameter_keys, list):
                continue
            print(
                "required_recommendation_action_parameters."
                f"{recommendation_id}="
                + ",".join(str(parameter_key) for parameter_key in parameter_keys)
            )
    if isinstance(required_recommendation_action_parameter_paths, dict):
        for recommendation_id in sorted(required_recommendation_action_parameter_paths):
            parameter_paths = required_recommendation_action_parameter_paths[
                recommendation_id
            ]
            if not isinstance(parameter_paths, list):
                continue
            print(
                "required_recommendation_action_parameter_paths."
                f"{recommendation_id}="
                + ",".join(str(parameter_path) for parameter_path in parameter_paths)
            )
    validation_commands = receipt.get("validation_commands", [])
    if isinstance(validation_commands, list) and validation_commands:
        print(
            "validation_commands="
            + " | ".join(str(command) for command in validation_commands)
        )


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
        "--acceptance-policy",
        action="store_true",
        help=(
            "Print the generated acceptance-policy metadata: default policy "
            "path, checker scripts, refresh command, and pinned requirement keys."
        ),
    )
    parser.add_argument(
        "--acceptance-policy-report",
        action="store_true",
        help=(
            "Validate the selected downstream acceptance policy and emit the "
            "bundled strict receipt report for its pinned contracts."
        ),
    )
    parser.add_argument(
        "--print-refreshed-policy",
        action="store_true",
        help=(
            "Print the selected acceptance policy with only expected pack and "
            "contract fingerprints refreshed from --path. Requirement pins "
            "are preserved."
        ),
    )
    parser.add_argument(
        "--policy",
        default=str(DEFAULT_POLICY),
        help=(
            "Path to a circle_calculus.ai_contract_acceptance_policy.v0 JSON "
            "file for --acceptance-policy-report or --print-refreshed-policy."
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
        "--recommendation",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID",
        help=(
            "In --action-plan output, emit only this planner recommendation id. "
            "Repeat for multiple ids. Missing ids fail instead of being ignored."
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
        "--receipt",
        action="store_true",
        help=(
            "Emit a strict acceptance receipt for the selected kind. This "
            "fails if any requested --field or --require-recommendation is "
            "missing."
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
        "--require-theorem",
        action="append",
        default=[],
        metavar="THEOREM_ID",
        help=(
            "In --receipt output, require a theorem id to appear in the "
            "selected contract theorem spine. Repeat for multiple theorems."
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
    parser.add_argument(
        "--require-recommendation",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID",
        help=(
            "In --receipt output, require a planner recommendation id to exist "
            "for the selected kind. Repeat for multiple recommendations."
        ),
    )
    parser.add_argument(
        "--require-recommendation-evidence-field",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=FIELD",
        help=(
            "In --receipt output, require a planner recommendation to cite a "
            "specific evidence field. Repeat for multiple fields. This also "
            "requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-theorem",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=THEOREM_ID",
        help=(
            "In --receipt output, require a planner recommendation to cite a "
            "specific theorem id. Repeat for multiple theorem ids. This also "
            "requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-action-parameter",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=PARAMETER_KEY",
        help=(
            "In --receipt output, require a planner recommendation to expose a "
            "specific value-mode action parameter key. Repeat for multiple "
            "keys. This also requires the recommendation id itself."
        ),
    )
    parser.add_argument(
        "--require-recommendation-action-parameter-path",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID=PARAMETER_PATH",
        help=(
            "In --receipt output, require a planner recommendation to expose a "
            "nested value-mode action parameter path, for example "
            "classifier_regions[region=proved].theorem_ids. Repeat for "
            "multiple paths. This also requires the recommendation id itself."
        ),
    )
    args = parser.parse_args()

    recommendation_evidence_requirements, evidence_parse_failures = (
        _parse_recommendation_evidence_requirements(
            args.require_recommendation_evidence_field,
        )
    )
    recommendation_theorem_requirements, theorem_parse_failures = (
        _parse_recommendation_theorem_requirements(
            args.require_recommendation_theorem,
        )
    )
    recommendation_action_parameter_requirements, action_parse_failures = (
        _parse_recommendation_action_parameter_requirements(
            args.require_recommendation_action_parameter,
        )
    )
    recommendation_action_parameter_path_requirements, path_parse_failures = (
        _parse_recommendation_action_parameter_path_requirements(
            args.require_recommendation_action_parameter_path,
        )
    )
    parse_failures = (
        evidence_parse_failures
        + theorem_parse_failures
        + action_parse_failures
        + path_parse_failures
    )
    if parse_failures:
        parser.error("; ".join(parse_failures))
    if args.require_recommendation_evidence_field and not args.receipt:
        parser.error("--require-recommendation-evidence-field requires --receipt")
    if args.require_recommendation_theorem and not args.receipt:
        parser.error("--require-recommendation-theorem requires --receipt")
    if args.require_recommendation_action_parameter and not args.receipt:
        parser.error("--require-recommendation-action-parameter requires --receipt")
    if args.require_recommendation_action_parameter_path and not args.receipt:
        parser.error(
            "--require-recommendation-action-parameter-path requires --receipt"
        )
    if args.require_theorem and not args.receipt:
        parser.error("--require-theorem requires --receipt")
    if args.recommendation and not args.action_plan:
        parser.error("--recommendation requires --action-plan")
    if args.print_refreshed_policy:
        if (
            args.kind
            or args.list_kinds
            or args.list_recommendations
            or args.fingerprints
            or args.acceptance_policy
            or args.acceptance_policy_report
            or args.digest
            or args.receipt
            or args.action_plan
            or args.expect_pack_fingerprint
            or args.expect_contract_fingerprint
        ):
            parser.error(
                "--print-refreshed-policy cannot be used with --kind or "
                "--list-kinds or --list-recommendations or --fingerprints or "
                "--acceptance-policy or --acceptance-policy-report or --digest or "
                "--receipt or --action-plan or fingerprint expectations"
            )

    pack = _load_pack(Path(args.path))
    if args.print_refreshed_policy:
        try:
            policy = _load_json_object(Path(args.policy))
            refreshed_policy = refresh_acceptance_policy_fingerprints(pack, policy)
        except (
            ContractAcceptancePolicyError,
            OSError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            print(f"acceptance policy refresh failed: {exc}", file=sys.stderr)
            return 4
        print(json.dumps(refreshed_policy, indent=2, sort_keys=True))
        return 0

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
            or args.receipt
            or args.list_recommendations
            or args.action_plan
            or args.fingerprints
            or args.acceptance_policy
            or args.acceptance_policy_report
            or args.print_refreshed_policy
        ):
            parser.error(
                "--list-kinds cannot be combined with --digest or --receipt or "
                "--list-recommendations or --action-plan or --fingerprints or "
                "--acceptance-policy or --acceptance-policy-report or "
                "--print-refreshed-policy"
            )
        _print_kind_list(pack, args.format)
        return 0

    if args.list_recommendations:
        if (
            args.digest
            or args.receipt
            or args.action_plan
            or args.fingerprints
            or args.acceptance_policy
            or args.acceptance_policy_report
            or args.print_refreshed_policy
        ):
            parser.error(
                "--list-recommendations cannot be used with --digest or --receipt "
                "or --action-plan or --fingerprints or --acceptance-policy or "
                "--acceptance-policy-report or --print-refreshed-policy"
            )
        _print_recommendation_list(pack, args.format)
        return 0

    if args.fingerprints:
        if (
            args.digest
            or args.receipt
            or args.action_plan
            or args.acceptance_policy
            or args.acceptance_policy_report
            or args.print_refreshed_policy
        ):
            parser.error(
                "--fingerprints cannot be used with --digest or --receipt or "
                "--action-plan or --acceptance-policy or --acceptance-policy-report "
                "or --print-refreshed-policy"
            )
        _print_fingerprints(pack, args.format)
        return 0

    if args.acceptance_policy:
        if (
            args.kind
            or args.digest
            or args.receipt
            or args.action_plan
            or args.acceptance_policy_report
            or args.print_refreshed_policy
        ):
            parser.error(
                "--acceptance-policy cannot be used with --kind or --digest or "
                "--receipt or --action-plan or --acceptance-policy-report or "
                "--print-refreshed-policy"
            )
        _print_acceptance_policy(pack, args.format)
        return 0

    if args.acceptance_policy_report:
        if (
            args.kind
            or args.digest
            or args.receipt
            or args.action_plan
            or args.print_refreshed_policy
        ):
            parser.error(
                "--acceptance-policy-report cannot be used with --kind or "
                "--digest or --receipt or --action-plan or --print-refreshed-policy"
            )
        try:
            policy = _load_json_object(Path(args.policy))
            report = contract_acceptance_policy_report(
                pack,
                policy,
                include_field_metadata=args.include_field_metadata,
            )
        except (
            ContractAcceptancePolicyError,
            OSError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            print(f"acceptance policy report failed: {exc}", file=sys.stderr)
            return 4
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            _print_acceptance_policy_report_text(report)
        return 0

    if args.action_plan:
        if args.digest or args.receipt:
            parser.error("--digest and --receipt cannot be used with --action-plan")
        selected_kinds = (args.kind,) if args.kind else None
        try:
            plan = planner_action_plan(
                pack,
                selected_kinds,
                include_values=args.include_values,
                recommendation_ids=args.recommendation or None,
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
            "or --fingerprints or --acceptance-policy is passed"
        )

    readiness = _readiness_for(pack, args.kind)
    if readiness is None:
        print(f"unknown contract kind: {args.kind}", file=sys.stderr)
        return 1

    if args.digest and args.receipt:
        parser.error("--digest cannot be used with --receipt")

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

    if args.receipt:
        try:
            receipt = contract_acceptance_receipt(
                pack,
                args.kind,
                required_fields=tuple(args.field) if args.field else None,
                required_theorem_ids=(
                    tuple(args.require_theorem) if args.require_theorem else None
                ),
                required_recommendation_ids=(
                    tuple(args.require_recommendation)
                    if args.require_recommendation
                    else None
                ),
                required_recommendation_evidence_fields=(
                    recommendation_evidence_requirements or None
                ),
                required_recommendation_theorem_ids=(
                    recommendation_theorem_requirements or None
                ),
                required_recommendation_action_parameters=(
                    recommendation_action_parameter_requirements or None
                ),
                required_recommendation_action_parameter_paths=(
                    recommendation_action_parameter_path_requirements or None
                ),
                include_field_metadata=args.include_field_metadata,
            )
        except (ContractAcceptanceError, ContractConsumerError) as exc:
            print(f"contract receipt failed: {exc}", file=sys.stderr)
            return 4
        if args.format == "json":
            print(json.dumps(receipt, indent=2, sort_keys=True))
        else:
            _print_receipt_text(receipt)
        return 0

    if args.format == "json":
        print(json.dumps(_json_payload(pack, args.kind, readiness), indent=2, sort_keys=True))
    else:
        _print_text(args.kind, readiness, pack)

    return 0 if readiness.get("ready_for_downstream_fixture_use") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
