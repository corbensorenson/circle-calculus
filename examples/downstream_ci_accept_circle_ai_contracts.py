#!/usr/bin/env python3
"""Standalone downstream CI gate for Circle AI contract packs.

This example intentionally uses only the Python standard library. A downstream
project can copy it, vendor a generated ``circle_ai_contract_pack.json`` plus a
pinned acceptance policy, and fail CI when Circle's theorem-linked contract
surface drifts or weakens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_ID = "circle_calculus.ai_contract_pack.v0"
EXPECTED_POLICY_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_policy.v0"
EXPECTED_REPORT_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_policy_report.v0"
EXPECTED_RECEIPT_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_receipt.v0"
EXAMPLE_SCHEMA_ID = "circle_calculus.downstream_ci_acceptance_example.v0"
FAILURE_SCHEMA_ID = "circle_calculus.downstream_ci_rejection_report.v0"
FINGERPRINT_ALGORITHM = "sha256-json-v1"
FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}
BASE_RECOMMENDATION_KEYS = {
    "id",
    "action_kind",
    "status",
    "coverage_scope",
    "evidence_fields",
    "theorem_ids",
    "not_claimed",
}
ACTION_PARAMETER_PATH_SEGMENT_RE = re.compile(
    r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?:\[(?P<selector>[^\]]+)\])?$"
)
RECOMMENDATION_INDEX_KEYS = (
    "id",
    "kind",
    "contract_id",
    "ready_for_downstream_fixture_use",
    "action_kind",
    "status",
    "coverage_scope",
    "evidence_fields",
    "theorem_ids",
    "quickstart_docs",
    "living_book_pages",
    "validation_commands",
    "source_paper",
    "not_claimed",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _strip_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in value.items()
            if key not in FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_fingerprint(value: Any) -> str:
    normalized = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _string_list(value: Any, *, context: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise ValueError(f"{context} must be a list of non-empty strings")
    seen: set[str] = set()
    for item in value:
        if item in seen:
            raise ValueError(f"{context} repeats string {item!r}")
        seen.add(item)
    return list(value)


def _recommendation_field_requirements(
    value: Any,
    *,
    context: str,
) -> dict[str, list[str]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be an object")
    normalized: dict[str, list[str]] = {}
    for recommendation_id, fields in value.items():
        if not isinstance(recommendation_id, str) or not recommendation_id:
            raise ValueError(f"{context} keys must be non-empty strings")
        normalized[recommendation_id] = _string_list(
            fields,
            context=f"{context}.{recommendation_id}",
        )
    return normalized


def _action_parameter_path_head(path: str) -> str | None:
    segment = path.split(".", 1)[0]
    match = ACTION_PARAMETER_PATH_SEGMENT_RE.fullmatch(segment)
    if match is None:
        return None
    return match.group("key")


def _path_selector_matches(item: Any, selector: str) -> bool:
    if not isinstance(item, dict) or "=" not in selector:
        return False
    key, expected = selector.split("=", 1)
    return item.get(key) == expected


def _json_path_exists(value: Any, path: str) -> bool:
    current = value
    for raw_segment in path.split("."):
        if not raw_segment:
            return False
        match = ACTION_PARAMETER_PATH_SEGMENT_RE.fullmatch(raw_segment)
        if match is None:
            return False
        key = match.group("key")
        selector = match.group("selector")
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
        if selector is None:
            continue
        if selector.isdecimal():
            if not isinstance(current, list):
                return False
            index = int(selector)
            if index >= len(current):
                return False
            current = current[index]
            continue
        if not isinstance(current, list):
            return False
        matches = [item for item in current if _path_selector_matches(item, selector)]
        if not matches:
            return False
        current = matches[0]
    return True


def _contract_by_kind(pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contracts = pack.get("contracts")
    if not isinstance(contracts, list):
        raise ValueError("pack.contracts must be a list")
    by_kind: dict[str, dict[str, Any]] = {}
    for contract in contracts:
        if not isinstance(contract, dict):
            raise ValueError("pack.contracts entries must be objects")
        kind = contract.get("kind")
        if not isinstance(kind, str) or not kind:
            raise ValueError("contract.kind must be a non-empty string")
        if kind in by_kind:
            raise ValueError(f"contract kind repeats: {kind}")
        by_kind[kind] = contract
    return by_kind


def _field_map(contract: dict[str, Any]) -> dict[str, Any]:
    fields = contract.get("fields")
    if not isinstance(fields, dict):
        raise ValueError(f"{contract.get('kind')}: fields must be an object")
    return fields


def _recommendations_by_id(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    recommendations = contract.get("planner_recommendations", [])
    if not isinstance(recommendations, list):
        raise ValueError(
            f"{contract.get('kind')}: planner_recommendations must be a list"
        )
    by_id: dict[str, dict[str, Any]] = {}
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            raise ValueError(
                f"{contract.get('kind')}: planner recommendations must be objects"
            )
        recommendation_id = recommendation.get("id")
        if not isinstance(recommendation_id, str) or not recommendation_id:
            raise ValueError(
                f"{contract.get('kind')}: recommendation id must be a string"
            )
        if recommendation_id in by_id:
            raise ValueError(
                f"{contract.get('kind')}: duplicate recommendation id "
                f"{recommendation_id}"
            )
        by_id[recommendation_id] = recommendation
    return by_id


def _expected_indexed_recommendation(
    contract: dict[str, Any],
    recommendation: dict[str, Any],
) -> dict[str, Any]:
    consumer_check = contract.get("consumer_check", {})
    ready = (
        isinstance(consumer_check, dict)
        and consumer_check.get("ready_for_downstream_fixture_use") is True
    )
    return {
        "id": recommendation.get("id"),
        "kind": contract.get("kind"),
        "contract_id": contract.get("id"),
        "ready_for_downstream_fixture_use": ready,
        "action_kind": recommendation.get("action_kind"),
        "status": recommendation.get("status"),
        "coverage_scope": recommendation.get("coverage_scope"),
        "evidence_fields": list(recommendation.get("evidence_fields", [])),
        "theorem_ids": list(recommendation.get("theorem_ids", [])),
        "quickstart_docs": list(contract.get("quickstart_docs", [])),
        "living_book_pages": list(contract.get("living_book_pages", [])),
        "validation_commands": list(contract.get("validation_commands", [])),
        "source_paper": contract.get("source_paper"),
        "not_claimed": recommendation.get("not_claimed"),
    }


def _require_contract_ready(contract: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    kind = contract.get("kind", "<unknown>")
    consumer_check = contract.get("consumer_check", {})
    proof_status = contract.get("proof_status", {})
    if not isinstance(consumer_check, dict):
        return [f"{kind}: consumer_check must be an object"]
    if not isinstance(proof_status, dict):
        return [f"{kind}: proof_status must be an object"]
    if contract.get("contract_passed") is not True:
        failures.append(f"{kind}: contract_passed is not true")
    if consumer_check.get("ready_for_downstream_fixture_use") is not True:
        failures.append(f"{kind}: consumer readiness is not true")
    if consumer_check.get("missing_minimum_fields") not in ([], None):
        failures.append(f"{kind}: minimum fields are missing")
    if consumer_check.get("unresolved_theorem_ids") not in ([], None):
        failures.append(f"{kind}: theorem ids are unresolved")
    if consumer_check.get("unproved_theorem_ids") not in ([], None):
        failures.append(f"{kind}: theorem ids are unproved")
    if proof_status.get("all_theorem_ids_resolved") is not True:
        failures.append(f"{kind}: proof status has unresolved theorem ids")
    if proof_status.get("all_theorem_ids_proved") is not True:
        failures.append(f"{kind}: proof status has unproved theorem ids")
    if "not_claimed" not in contract:
        failures.append(f"{kind}: non-claim boundary is missing")
    return failures


def accept_policy(
    pack: dict[str, Any],
    policy: dict[str, Any],
    *,
    include_values: bool = False,
    planner_recommendation_ids: list[str] | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    requested_recommendation_ids = list(dict.fromkeys(planner_recommendation_ids or []))
    if pack.get("schema_id") != EXPECTED_SCHEMA_ID:
        failures.append(f"pack.schema_id must be {EXPECTED_SCHEMA_ID!r}")
    if pack.get("content_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        failures.append(
            f"pack.content_fingerprint_algorithm must be {FINGERPRINT_ALGORITHM!r}"
        )
    computed_pack_fingerprint = _json_fingerprint(pack)
    if pack.get("pack_content_fingerprint") != computed_pack_fingerprint:
        failures.append("pack_content_fingerprint drifted from pack content")
    if policy.get("schema_id") != EXPECTED_POLICY_SCHEMA_ID:
        failures.append(f"policy.schema_id must be {EXPECTED_POLICY_SCHEMA_ID!r}")
    expected_pack_fingerprint = policy.get("expected_pack_fingerprint")
    if expected_pack_fingerprint != pack.get("pack_content_fingerprint"):
        failures.append("policy expected pack fingerprint does not match pack")

    contracts_by_kind = _contract_by_kind(pack)
    recommendation_index = pack.get("planner_recommendation_index")
    if not isinstance(recommendation_index, dict):
        failures.append("pack.planner_recommendation_index must be an object")
        recommendation_index = {}
    raw_specs = policy.get("contracts")
    if not isinstance(raw_specs, list) or not raw_specs:
        failures.append("policy.contracts must be a non-empty list")
        raw_specs = []

    receipts: list[dict[str, Any]] = []
    selected_recommendation_owners: dict[str, str] = {}
    selected_policy_kinds: set[str] = set()
    for index, raw_spec in enumerate(raw_specs):
        context = f"policy.contracts[{index}]"
        if not isinstance(raw_spec, dict):
            failures.append(f"{context} must be an object")
            continue
        kind = raw_spec.get("kind")
        if not isinstance(kind, str) or not kind:
            failures.append(f"{context}.kind must be a non-empty string")
            continue
        if kind in selected_policy_kinds:
            failures.append(f"{kind}: policy selects contract kind more than once")
            continue
        selected_policy_kinds.add(kind)
        contract = contracts_by_kind.get(kind)
        if contract is None:
            failures.append(f"{kind}: selected contract is missing")
            continue
        fields = _field_map(contract)
        recommendations = _recommendations_by_id(contract)
        for recommendation_id, recommendation in recommendations.items():
            previous_kind = selected_recommendation_owners.get(recommendation_id)
            if previous_kind is not None:
                failures.append(
                    f"{kind}: duplicate selected recommendation id "
                    f"{recommendation_id} already used by {previous_kind}"
                )
                continue
            selected_recommendation_owners[recommendation_id] = kind
            indexed = recommendation_index.get(recommendation_id)
            if not isinstance(indexed, dict):
                failures.append(f"{kind}: {recommendation_id} is missing from index")
                continue
            expected_indexed = _expected_indexed_recommendation(
                contract,
                recommendation,
            )
            for key in RECOMMENDATION_INDEX_KEYS:
                if indexed.get(key) != expected_indexed[key]:
                    failures.append(
                        f"{kind}: {recommendation_id} index {key} drifted"
                    )
        required_fields = _string_list(
            raw_spec.get("required_fields", []),
            context=f"{context}.required_fields",
        )
        required_theorems = _string_list(
            raw_spec.get("required_theorem_ids", []),
            context=f"{context}.required_theorem_ids",
        )
        required_recommendations = _string_list(
            raw_spec.get("required_recommendation_ids", []),
            context=f"{context}.required_recommendation_ids",
        )
        required_recommendation_fields = _recommendation_field_requirements(
            raw_spec.get("required_recommendation_evidence_fields", {}),
            context=f"{context}.required_recommendation_evidence_fields",
        )
        required_recommendation_theorems = _recommendation_field_requirements(
            raw_spec.get("required_recommendation_theorem_ids", {}),
            context=f"{context}.required_recommendation_theorem_ids",
        )
        required_recommendation_action_parameters = (
            _recommendation_field_requirements(
                raw_spec.get("required_recommendation_action_parameters", {}),
                context=f"{context}.required_recommendation_action_parameters",
            )
        )
        required_recommendation_action_parameter_paths = (
            _recommendation_field_requirements(
                raw_spec.get("required_recommendation_action_parameter_paths", {}),
                context=f"{context}.required_recommendation_action_parameter_paths",
            )
        )
        all_required_recommendation_ids = sorted(
            set(required_recommendations)
            | set(required_recommendation_fields)
            | set(required_recommendation_theorems)
            | set(required_recommendation_action_parameters)
            | set(required_recommendation_action_parameter_paths)
        )
        expected_contract_fingerprint = raw_spec.get(
            "expected_contract_fingerprint"
        )
        computed_contract_fingerprint = _json_fingerprint(contract)
        if contract.get("content_fingerprint") != computed_contract_fingerprint:
            failures.append(f"{kind}: content_fingerprint drifted")
        if expected_contract_fingerprint != contract.get("content_fingerprint"):
            failures.append(f"{kind}: policy expected fingerprint does not match")
        failures.extend(_require_contract_ready(contract))

        missing_fields = [field for field in required_fields if field not in fields]
        if missing_fields:
            failures.append(f"{kind}: missing required fields {missing_fields}")
        contract_theorem_ids = contract.get("theorem_ids", [])
        if not isinstance(contract_theorem_ids, list):
            contract_theorem_ids = []
        missing_theorems = [
            theorem_id
            for theorem_id in required_theorems
            if theorem_id not in contract_theorem_ids
        ]
        if missing_theorems:
            failures.append(f"{kind}: missing required theorem ids {missing_theorems}")
        missing_recommendations = [
            recommendation_id
            for recommendation_id in all_required_recommendation_ids
            if recommendation_id not in recommendations
        ]
        if missing_recommendations:
            failures.append(
                f"{kind}: missing planner recommendations {missing_recommendations}"
            )
        for recommendation_id in all_required_recommendation_ids:
            indexed = recommendation_index.get(recommendation_id)
            if not isinstance(indexed, dict):
                failures.append(f"{kind}: {recommendation_id} is missing from index")
                continue
            if indexed.get("kind") != kind:
                failures.append(f"{kind}: {recommendation_id} index kind drifted")
            if indexed.get("contract_id") != contract.get("id"):
                failures.append(
                    f"{kind}: {recommendation_id} index contract id drifted"
                )
            if indexed.get("ready_for_downstream_fixture_use") is not True:
                failures.append(f"{kind}: {recommendation_id} index is not ready")
        missing_recommendation_fields: dict[str, list[str]] = {}
        for recommendation_id, required in required_recommendation_fields.items():
            recommendation = recommendations.get(recommendation_id)
            if recommendation is None:
                missing_recommendation_fields[recommendation_id] = list(required)
                continue
            evidence_fields = recommendation.get("evidence_fields", [])
            if not isinstance(evidence_fields, list):
                evidence_fields = []
            missing = [field for field in required if field not in evidence_fields]
            if missing:
                missing_recommendation_fields[recommendation_id] = missing
            indexed = recommendation_index.get(recommendation_id)
            if isinstance(indexed, dict):
                indexed_evidence_fields = indexed.get("evidence_fields", [])
                if not isinstance(indexed_evidence_fields, list):
                    indexed_evidence_fields = []
                missing_index_fields = [
                    field
                    for field in required
                    if field not in indexed_evidence_fields
                ]
                if missing_index_fields:
                    failures.append(
                        f"{kind}: {recommendation_id} index missing required "
                        f"evidence fields {missing_index_fields}"
                    )
        missing_recommendation_theorems: dict[str, list[str]] = {}
        for recommendation_id, required in required_recommendation_theorems.items():
            recommendation = recommendations.get(recommendation_id)
            if recommendation is None:
                missing_recommendation_theorems[recommendation_id] = list(required)
                continue
            recommendation_theorem_ids = recommendation.get("theorem_ids", [])
            if not isinstance(recommendation_theorem_ids, list):
                recommendation_theorem_ids = []
            missing = [
                theorem_id
                for theorem_id in required
                if theorem_id not in recommendation_theorem_ids
            ]
            if missing:
                missing_recommendation_theorems[recommendation_id] = missing
            indexed = recommendation_index.get(recommendation_id)
            if isinstance(indexed, dict):
                indexed_theorem_ids = indexed.get("theorem_ids", [])
                if not isinstance(indexed_theorem_ids, list):
                    indexed_theorem_ids = []
                missing_index_theorems = [
                    theorem_id
                    for theorem_id in required
                    if theorem_id not in indexed_theorem_ids
                ]
                if missing_index_theorems:
                    failures.append(
                        f"{kind}: {recommendation_id} index missing required "
                        f"theorem ids {missing_index_theorems}"
                    )
        if missing_recommendation_fields:
            failures.append(
                f"{kind}: missing recommendation evidence fields "
                f"{missing_recommendation_fields}"
            )
        if missing_recommendation_theorems:
            failures.append(
                f"{kind}: missing recommendation theorem ids "
                f"{missing_recommendation_theorems}"
            )
        missing_recommendation_action_parameters: dict[str, list[str]] = {}
        for recommendation_id, required in (
            required_recommendation_action_parameters.items()
        ):
            recommendation = recommendations.get(recommendation_id)
            if recommendation is None:
                missing_recommendation_action_parameters[recommendation_id] = (
                    list(required)
                )
                continue
            action_parameter_keys = set(recommendation) - BASE_RECOMMENDATION_KEYS
            missing = [
                parameter_key
                for parameter_key in required
                if parameter_key not in action_parameter_keys
            ]
            if missing:
                missing_recommendation_action_parameters[recommendation_id] = missing
        if missing_recommendation_action_parameters:
            failures.append(
                f"{kind}: missing recommendation action parameters "
                f"{missing_recommendation_action_parameters}"
            )
        missing_recommendation_action_parameter_paths: dict[str, list[str]] = {}
        invalid_recommendation_action_parameter_paths: dict[str, list[str]] = {}
        for recommendation_id, required in (
            required_recommendation_action_parameter_paths.items()
        ):
            recommendation = recommendations.get(recommendation_id)
            if recommendation is None:
                missing_recommendation_action_parameter_paths[
                    recommendation_id
                ] = list(required)
                continue
            action_parameter_keys = set(recommendation) - BASE_RECOMMENDATION_KEYS
            invalid = [
                path
                for path in required
                if (
                    _action_parameter_path_head(path) is None
                    or _action_parameter_path_head(path)
                    not in action_parameter_keys
                )
            ]
            if invalid:
                invalid_recommendation_action_parameter_paths[
                    recommendation_id
                ] = invalid
                continue
            missing = [
                path
                for path in required
                if not _json_path_exists(recommendation, path)
            ]
            if missing:
                missing_recommendation_action_parameter_paths[
                    recommendation_id
                ] = missing
        if invalid_recommendation_action_parameter_paths:
            failures.append(
                f"{kind}: invalid recommendation action-parameter paths "
                f"{invalid_recommendation_action_parameter_paths}"
            )
        if missing_recommendation_action_parameter_paths:
            failures.append(
                f"{kind}: missing recommendation action-parameter paths "
                f"{missing_recommendation_action_parameter_paths}"
            )

        receipts.append({
            "schema_id": pack.get("schema_id"),
            "receipt_schema": EXPECTED_RECEIPT_SCHEMA_ID,
            "accepted": True,
            "kind": kind,
            "contract_id": contract.get("id"),
            "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
            "contract_content_fingerprint": contract.get("content_fingerprint"),
            "required_fields": required_fields,
            "required_theorem_ids": required_theorems,
            "evidence_fields": {
                field: fields[field]
                for field in required_fields
                if field in fields
            },
            "required_recommendation_ids": all_required_recommendation_ids,
            "required_recommendation_evidence_fields": (
                required_recommendation_fields
            ),
            "required_recommendation_theorem_ids": (
                required_recommendation_theorems
            ),
            "required_recommendation_action_parameters": (
                required_recommendation_action_parameters
            ),
            "required_recommendation_action_parameter_paths": (
                required_recommendation_action_parameter_paths
            ),
            "planner_recommendations": [
                recommendations[recommendation_id]
                for recommendation_id in all_required_recommendation_ids
                if recommendation_id in recommendations
            ],
            "theorem_ids": list(contract.get("theorem_ids", [])),
            "dictionary_ids": list(contract.get("dictionary_ids", [])),
            "planner_recommendation_count": len(recommendations),
            "theorem_count": len(contract.get("theorem_ids", [])),
            "quickstart_docs": contract.get("quickstart_docs", []),
            "living_book_pages": contract.get("living_book_pages", []),
            "validation_commands": contract.get("validation_commands", []),
            "source_paper": contract.get("source_paper"),
            "not_claimed": contract.get("not_claimed"),
        })

    if failures:
        raise ValueError("; ".join(failures))

    action_plan = []
    selected_action_ids: list[str] = []
    selected_action_id_set: set[str] = set()
    selected_kinds = [receipt["kind"] for receipt in receipts]
    for kind in selected_kinds:
        contract = contracts_by_kind[kind]
        fields = _field_map(contract)
        for recommendation in _recommendations_by_id(contract).values():
            recommendation_id = recommendation["id"]
            if (
                requested_recommendation_ids
                and recommendation_id not in requested_recommendation_ids
            ):
                continue
            indexed = recommendation_index.get(recommendation_id)
            if not isinstance(indexed, dict):
                indexed = recommendation
            evidence_fields = [
                field
                for field in indexed.get("evidence_fields", [])
                if isinstance(field, str)
            ]
            action = {
                "recommendation_id": recommendation_id,
                "kind": kind,
                "contract_id": indexed.get("contract_id", contract.get("id")),
                "action_kind": indexed.get("action_kind"),
                "status": indexed.get("status"),
                "coverage_scope": indexed.get("coverage_scope"),
                "ready_for_downstream_fixture_use": indexed.get(
                    "ready_for_downstream_fixture_use"
                ),
                "evidence_fields": evidence_fields,
                "theorem_ids": indexed.get("theorem_ids", []),
                "quickstart_docs": indexed.get("quickstart_docs", []),
                "living_book_pages": indexed.get("living_book_pages", []),
                "validation_commands": indexed.get("validation_commands", []),
                "source_paper": indexed.get("source_paper"),
                "not_claimed": indexed.get("not_claimed"),
            }
            if include_values:
                action["evidence_values"] = {
                    field: fields[field]
                    for field in evidence_fields
                    if field in fields
                }
                action["missing_evidence_fields"] = [
                    field for field in evidence_fields if field not in fields
                ]
                action["action_parameters"] = {
                    key: value
                    for key, value in recommendation.items()
                    if key not in BASE_RECOMMENDATION_KEYS
                }
            action_plan.append(action)
            selected_action_ids.append(recommendation_id)
            selected_action_id_set.add(recommendation_id)

    missing_requested_recommendations = [
        recommendation_id
        for recommendation_id in requested_recommendation_ids
        if recommendation_id not in selected_action_id_set
    ]
    if missing_requested_recommendations:
        raise ValueError(
            "requested planner recommendations were not selected by the "
            f"accepted policy: {missing_requested_recommendations}"
        )

    contract_summaries = []
    for receipt in receipts:
        recommendation_theorems = receipt.get(
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
        contract_summaries.append({
            "kind": receipt["kind"],
            "contract_id": receipt["contract_id"],
            "required_field_count": len(receipt["required_fields"]),
            "required_theorem_count": len(receipt["required_theorem_ids"]),
            "required_recommendation_ids": list(
                receipt["required_recommendation_ids"]
            ),
            "required_recommendation_count": len(
                receipt["required_recommendation_ids"]
            ),
            "required_recommendation_theorem_count": (
                sum(len(value) for value in recommendation_theorems.values())
                if isinstance(recommendation_theorems, dict)
                else 0
            ),
            "required_recommendation_action_parameter_count": (
                sum(
                    len(value)
                    for value in recommendation_action_parameters.values()
                )
                if isinstance(recommendation_action_parameters, dict)
                else 0
            ),
            "required_recommendation_action_parameter_path_count": (
                sum(
                    len(value)
                    for value in recommendation_action_parameter_paths.values()
                )
                if isinstance(recommendation_action_parameter_paths, dict)
                else 0
            ),
            "content_fingerprint": receipt["contract_content_fingerprint"],
        })
    total_required_recommendation_theorems = sum(
        summary["required_recommendation_theorem_count"]
        for summary in contract_summaries
    )
    selected_recommendations_by_kind: dict[str, list[str]] = {}
    for action in action_plan:
        kind = action["kind"]
        selected_recommendations_by_kind.setdefault(kind, []).append(
            action["recommendation_id"]
        )

    return {
        "schema_id": pack.get("schema_id"),
        "example_schema_id": EXAMPLE_SCHEMA_ID,
        "acceptance_policy_report_schema": EXPECTED_REPORT_SCHEMA_ID,
        "policy_schema": EXPECTED_POLICY_SCHEMA_ID,
        "accepted": True,
        "policy_id": policy.get("policy_id"),
        "policy_name": policy.get("policy_name"),
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
        "expected_pack_fingerprint": expected_pack_fingerprint,
        "contract_count": len(receipts),
        "receipt_count": len(receipts),
        "receipts": receipts,
        "accepted_contracts": receipts,
        "policy_summary": {
            "schema_id": "circle_calculus.downstream_ci_policy_summary.v0",
            "policy_id": policy.get("policy_id"),
            "accepted_contract_kinds": [receipt["kind"] for receipt in receipts],
            "accepted_contract_count": len(receipts),
            "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
            "expected_pack_fingerprint": expected_pack_fingerprint,
            "required_field_count": sum(
                summary["required_field_count"] for summary in contract_summaries
            ),
            "required_theorem_count": sum(
                summary["required_theorem_count"] for summary in contract_summaries
            ),
            "required_recommendation_count": sum(
                summary["required_recommendation_count"]
                for summary in contract_summaries
            ),
            "required_recommendation_theorem_count": (
                total_required_recommendation_theorems
            ),
            "contract_summaries": contract_summaries,
        },
        "planner_schema": "circle_calculus.ai_contract_planner.v0",
        "planner_includes_values": include_values,
        "planner_requested_recommendation_ids": requested_recommendation_ids,
        "planner_selected_recommendation_ids": selected_action_ids,
        "planner_recommendation_count": len(action_plan),
        "planner_summary": {
            "schema_id": "circle_calculus.downstream_ci_planner_summary.v0",
            "selected_recommendation_count": len(action_plan),
            "selected_recommendation_ids": selected_action_ids,
            "selected_recommendations_by_kind": selected_recommendations_by_kind,
            "requested_recommendation_ids": requested_recommendation_ids,
            "includes_values": include_values,
        },
        "action_plan": action_plan,
        "not_claimed": (
            "This example accepts pinned theorem-linked fixture contracts only. "
            "It does not prove model quality, speed, memory scaling, deployment "
            "safety, transfer, or ASI."
        ),
    }


def _print_text(report: dict[str, Any]) -> None:
    planner_summary = report.get("planner_summary", {})
    selected_recommendation_ids = planner_summary.get(
        "selected_recommendation_ids",
        report.get("planner_selected_recommendation_ids", []),
    )
    print(
        "circle AI downstream CI acceptance ok: "
        f"policy={report['policy_id']} contracts={report['contract_count']} "
        f"actions={report['planner_recommendation_count']}"
    )
    print(
        " ".join(
            [
                f"fingerprint_algorithm={report['content_fingerprint_algorithm']}",
                f"pack={report['pack_content_fingerprint']}",
            ]
        )
    )
    if selected_recommendation_ids:
        print("planner.selected=" + ",".join(selected_recommendation_ids))
    for receipt in report["accepted_contracts"]:
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
        recommendation_theorem_count = (
            sum(len(value) for value in recommendation_theorem_ids.values())
            if isinstance(recommendation_theorem_ids, dict)
            else 0
        )
        recommendation_action_parameter_count = (
            sum(len(value) for value in recommendation_action_parameters.values())
            if isinstance(recommendation_action_parameters, dict)
            else 0
        )
        recommendation_action_parameter_path_count = (
            sum(len(value) for value in recommendation_action_parameter_paths.values())
            if isinstance(recommendation_action_parameter_paths, dict)
            else 0
        )
        print(
            " ".join(
                [
                    f"accepted.{receipt['kind']}",
                    f"contract={receipt['contract_id']}",
                    f"fields={len(receipt['required_fields'])}",
                    f"theorems={len(receipt.get('required_theorem_ids', []))}",
                    (
                        "recommendations="
                        f"{len(receipt['required_recommendation_ids'])}"
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
                    f"fingerprint={receipt['contract_content_fingerprint']}",
                ]
            )
        )


def _failure_items(message: str) -> list[str]:
    items = [item.strip() for item in message.split("; ") if item.strip()]
    return items or [message]


def _failure_report(
    *,
    exc: BaseException,
    pack_path: str,
    policy_path: str,
    planner_recommendation_ids: list[str],
) -> dict[str, Any]:
    message = str(exc)
    failures = _failure_items(message)
    return {
        "schema_id": FAILURE_SCHEMA_ID,
        "example_schema_id": EXAMPLE_SCHEMA_ID,
        "accepted": False,
        "error": message,
        "failure_count": len(failures),
        "failures": failures,
        "pack_path": str(_resolve(pack_path)),
        "policy_path": str(_resolve(policy_path)),
        "planner_requested_recommendation_ids": list(planner_recommendation_ids),
        "not_claimed": (
            "This is a machine-readable rejection report for a pinned "
            "artifact-consumption gate. It is not a mathematical proof, model "
            "quality result, deployment-safety claim, or ASI claim."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Standalone downstream CI example for accepting a pinned Circle AI "
            "contract pack and planner surface."
        ),
    )
    parser.add_argument(
        "--pack",
        default="site/data/generated/circle_ai_contract_pack.json",
        help="Path to generated circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--policy",
        default="examples/circle_ai_contract_acceptance_policy.json",
        help="Path to a pinned Circle AI acceptance policy JSON file.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--include-values",
        action="store_true",
        help="Include resolved evidence values in planner action records.",
    )
    parser.add_argument(
        "--planner-recommendation",
        action="append",
        default=[],
        metavar="RECOMMENDATION_ID",
        help=(
            "Emit only the named planner recommendation. May be repeated. "
            "The command fails if an id is not selected by the accepted policy."
        ),
    )
    args = parser.parse_args()

    try:
        pack = _load_json_object(_resolve(args.pack))
        policy = _load_json_object(_resolve(args.policy))
        report = accept_policy(
            pack,
            policy,
            include_values=args.include_values,
            planner_recommendation_ids=args.planner_recommendation,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if args.format == "json":
            print(
                json.dumps(
                    _failure_report(
                        exc=exc,
                        pack_path=args.pack,
                        policy_path=args.policy,
                        planner_recommendation_ids=args.planner_recommendation,
                    ),
                    indent=2,
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
        else:
            print(
                f"circle AI downstream CI acceptance failed: {exc}",
                file=sys.stderr,
            )
        return 4

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
