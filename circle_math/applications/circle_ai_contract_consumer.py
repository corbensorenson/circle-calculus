"""Consumer helpers for the generated Circle AI contract pack.

This module is intentionally lightweight. It validates the public JSON shape a
downstream project needs, but it does not require Lean, manifests, or repository
validation scripts to be present.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


EXPECTED_SCHEMA_ID = "circle_calculus.ai_contract_pack.v0"
DEFAULT_PACK = Path("site/data/generated/circle_ai_contract_pack.json")
EXPECTED_RECOMMENDATION_KEYS = {
    "id",
    "action_kind",
    "status",
    "coverage_scope",
    "evidence_fields",
    "theorem_ids",
    "not_claimed",
}


class ContractConsumerError(ValueError):
    """Base error for consumer-facing contract-pack failures."""


class ContractPackSchemaError(ContractConsumerError):
    """Raised when the pack is malformed or internally inconsistent."""


class ContractNotReadyError(ContractConsumerError):
    """Raised when a requested contract kind is present but not ready."""


@dataclass(frozen=True)
class ContractReadinessSummary:
    """Compact readiness view for one contract kind."""

    schema_id: str
    contract_id: str
    kind: str
    ready_for_downstream_fixture_use: bool
    contract_passed: bool
    required_fields_present: bool
    all_theorem_ids_resolved: bool
    all_theorem_ids_proved: bool
    theorem_count: int
    missing_minimum_fields: tuple[str, ...]
    unresolved_theorem_ids: tuple[str, ...]
    unproved_theorem_ids: tuple[str, ...]
    quickstart_docs: tuple[str, ...]
    living_book_pages: tuple[str, ...]
    entrypoints: tuple[str, ...]
    validation_commands: tuple[str, ...]
    planner_recommendation_count: int
    planner_recommendation_ids: tuple[str, ...]
    theorem_ids: tuple[str, ...]
    dictionary_ids: tuple[str, ...]
    minimum_fields: tuple[str, ...]
    source_paper: str | None
    not_claimed: str

    @property
    def ready(self) -> bool:
        return self.ready_for_downstream_fixture_use

    def failure_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        if not self.contract_passed:
            reasons.append("contract_passed is false")
        if not self.required_fields_present:
            reasons.append(
                "missing minimum fields: " + ",".join(self.missing_minimum_fields)
            )
        if not self.all_theorem_ids_resolved:
            reasons.append(
                "unresolved theorem ids: " + ",".join(self.unresolved_theorem_ids)
            )
        if not self.all_theorem_ids_proved:
            reasons.append("unproved theorem ids: " + ",".join(self.unproved_theorem_ids))
        return tuple(reasons)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "id": self.contract_id,
            "kind": self.kind,
            "ready_for_downstream_fixture_use": (
                self.ready_for_downstream_fixture_use
            ),
            "contract_passed": self.contract_passed,
            "required_fields_present": self.required_fields_present,
            "all_theorem_ids_resolved": self.all_theorem_ids_resolved,
            "all_theorem_ids_proved": self.all_theorem_ids_proved,
            "theorem_count": self.theorem_count,
            "missing_minimum_fields": list(self.missing_minimum_fields),
            "unresolved_theorem_ids": list(self.unresolved_theorem_ids),
            "unproved_theorem_ids": list(self.unproved_theorem_ids),
            "quickstart_docs": list(self.quickstart_docs),
            "living_book_pages": list(self.living_book_pages),
            "entrypoints": list(self.entrypoints),
            "validation_commands": list(self.validation_commands),
            "planner_recommendation_count": self.planner_recommendation_count,
            "planner_recommendation_ids": list(self.planner_recommendation_ids),
            "theorem_ids": list(self.theorem_ids),
            "dictionary_ids": list(self.dictionary_ids),
            "minimum_fields": list(self.minimum_fields),
            "source_paper": self.source_paper,
            "not_claimed": self.not_claimed,
            "failure_reasons": list(self.failure_reasons()),
        }


def load_contract_pack(path: str | Path = DEFAULT_PACK) -> dict[str, Any]:
    """Load a generated contract pack from JSON."""

    return json.loads(Path(path).read_text())


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _json_value_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


def find_contract(pack: dict[str, Any], kind: str) -> dict[str, Any] | None:
    """Return the contract record for ``kind`` if it exists."""

    contracts = pack.get("contracts")
    if not isinstance(contracts, list):
        return None
    for contract in contracts:
        if isinstance(contract, dict) and contract.get("kind") == kind:
            return contract
    return None


def contract_kinds(pack: dict[str, Any]) -> tuple[str, ...]:
    """Return available contract kinds in stable sorted order."""

    contracts = pack.get("contracts")
    if not isinstance(contracts, list):
        return ()
    kinds = [
        contract.get("kind")
        for contract in contracts
        if isinstance(contract, dict) and isinstance(contract.get("kind"), str)
    ]
    return tuple(sorted(kinds))


def validate_consumer_pack(pack: dict[str, Any]) -> list[str]:
    """Validate the JSON invariants a downstream consumer relies on."""

    failures: list[str] = []
    if pack.get("schema_id") != EXPECTED_SCHEMA_ID:
        failures.append(f"expected schema_id {EXPECTED_SCHEMA_ID!r}")

    contracts = pack.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        failures.append("contracts must be a non-empty list")
        return failures

    readiness_index = pack.get("contract_readiness_index")
    if not isinstance(readiness_index, dict) or not readiness_index:
        failures.append("contract_readiness_index must be a non-empty object")
        readiness_index = {}
    recommendation_index = pack.get("planner_recommendation_index")
    if not isinstance(recommendation_index, dict) or not recommendation_index:
        failures.append("planner_recommendation_index must be a non-empty object")
        recommendation_index = {}

    schema = pack.get("contract_schema")
    if not isinstance(schema, dict):
        failures.append("contract_schema must be an object")
        schema = {}
    minimum_fields_by_kind = schema.get("minimum_fields_by_kind")
    if not isinstance(minimum_fields_by_kind, dict):
        failures.append("contract_schema.minimum_fields_by_kind must be an object")
        minimum_fields_by_kind = {}
    minimum_field_catalog_by_kind = schema.get("minimum_field_catalog_by_kind")
    if not isinstance(minimum_field_catalog_by_kind, dict):
        failures.append(
            "contract_schema.minimum_field_catalog_by_kind must be an object"
        )
        minimum_field_catalog_by_kind = {}

    contract_kinds_seen: set[str] = set()
    expected_recommendation_index: dict[str, dict[str, Any]] = {}
    for contract in contracts:
        if not isinstance(contract, dict):
            failures.append("contract entry must be an object")
            continue
        kind = contract.get("kind")
        contract_id = contract.get("id", "<missing id>")
        if not isinstance(kind, str):
            failures.append(f"{contract_id}: kind must be a string")
            continue
        contract_kinds_seen.add(kind)

        fields = contract.get("fields")
        if not isinstance(fields, dict):
            failures.append(f"{contract_id}: fields must be an object")
            fields = {}
        minimum_fields = minimum_fields_by_kind.get(kind, [])
        if not isinstance(minimum_fields, list):
            failures.append(f"{contract_id}: minimum field list is missing")
            minimum_fields = []
        field_catalog = minimum_field_catalog_by_kind.get(kind)
        if not isinstance(field_catalog, dict):
            failures.append(f"{contract_id}: minimum field catalog is missing")
            field_catalog = {}
        missing_fields = [
            field for field in minimum_fields
            if isinstance(field, str) and field not in fields
        ]
        missing_catalog_fields = [
            field for field in minimum_fields
            if isinstance(field, str) and field not in field_catalog
        ]
        if missing_catalog_fields:
            failures.append(
                f"{contract_id}: minimum field catalog missing fields "
                f"{missing_catalog_fields}"
            )
        for field in minimum_fields:
            if not isinstance(field, str):
                continue
            catalog_entry = field_catalog.get(field)
            if not isinstance(catalog_entry, dict):
                continue
            for entry_key in ("description", "value_kind", "proof_role"):
                value = catalog_entry.get(entry_key)
                if not isinstance(value, str) or not value.strip():
                    failures.append(
                        f"{contract_id}: catalog entry {field}.{entry_key} "
                        "must be a non-empty string"
                    )
            if field in fields and catalog_entry.get("value_kind") != _json_value_kind(
                fields[field]
            ):
                failures.append(
                    f"{contract_id}: catalog entry {field}.value_kind drifted from "
                    "field value"
                )

        consumer_check = contract.get("consumer_check")
        if not isinstance(consumer_check, dict):
            failures.append(f"{contract_id}: consumer_check must be an object")
            consumer_check = {}
        proof_status = contract.get("proof_status")
        if not isinstance(proof_status, dict):
            failures.append(f"{contract_id}: proof_status must be an object")
            proof_status = {}

        expected_ready = (
            bool(contract.get("contract_passed"))
            and not missing_fields
            and consumer_check.get("all_theorem_ids_resolved") is True
            and consumer_check.get("all_theorem_ids_proved") is True
        )
        if consumer_check.get("missing_minimum_fields", []) != missing_fields:
            failures.append(f"{contract_id}: missing field list drifted")
        if consumer_check.get("required_fields_present") != (not missing_fields):
            failures.append(f"{contract_id}: required_fields_present drifted")
        if (
            consumer_check.get("ready_for_downstream_fixture_use")
            != expected_ready
        ):
            failures.append(f"{contract_id}: consumer ready flag drifted")
        if (
            consumer_check.get("all_theorem_ids_resolved")
            != proof_status.get("all_theorem_ids_resolved")
        ):
            failures.append(f"{contract_id}: resolved proof flag drifted")
        if (
            consumer_check.get("all_theorem_ids_proved")
            != proof_status.get("all_theorem_ids_proved")
        ):
            failures.append(f"{contract_id}: proved proof flag drifted")
        if "not" not in str(contract.get("not_claimed", "")).lower():
            failures.append(f"{contract_id}: not_claimed boundary is missing")

        recommendations = contract.get("planner_recommendations", [])
        if recommendations is not None and not isinstance(recommendations, list):
            failures.append(f"{contract_id}: planner_recommendations must be a list")
            recommendations = []
        theorem_ids = set(_as_str_tuple(contract.get("theorem_ids", [])))
        for index, recommendation in enumerate(recommendations):
            if not isinstance(recommendation, dict):
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] must be an object"
                )
                continue
            missing_recommendation_keys = sorted(
                EXPECTED_RECOMMENDATION_KEYS - set(recommendation)
            )
            if missing_recommendation_keys:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] missing "
                    f"keys {missing_recommendation_keys}"
                )
            evidence_fields = _as_str_tuple(recommendation.get("evidence_fields", []))
            unknown_evidence_fields = [
                field for field in evidence_fields if field not in fields
            ]
            if unknown_evidence_fields:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] "
                    f"unknown evidence fields {unknown_evidence_fields}"
                )
            recommendation_theorems = _as_str_tuple(
                recommendation.get("theorem_ids", [])
            )
            unknown_recommendation_theorems = [
                theorem_id
                for theorem_id in recommendation_theorems
                if theorem_id not in theorem_ids
            ]
            if unknown_recommendation_theorems:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}] "
                    f"unknown theorem ids {unknown_recommendation_theorems}"
                )
            recommendation_id = recommendation.get("id")
            if isinstance(recommendation_id, str):
                expected_recommendation_index[recommendation_id] = {
                    "id": recommendation_id,
                    "kind": kind,
                    "contract_id": contract_id,
                    "ready_for_downstream_fixture_use": (
                        consumer_check.get("ready_for_downstream_fixture_use") is True
                    ),
                    "action_kind": recommendation.get("action_kind"),
                    "status": recommendation.get("status"),
                    "coverage_scope": recommendation.get("coverage_scope"),
                    "evidence_fields": list(evidence_fields),
                    "theorem_ids": list(recommendation_theorems),
                    "quickstart_docs": list(contract.get("quickstart_docs", [])),
                    "living_book_pages": list(contract.get("living_book_pages", [])),
                    "validation_commands": list(
                        contract.get("validation_commands", [])
                    ),
                    "source_paper": contract.get("source_paper"),
                    "not_claimed": recommendation.get("not_claimed"),
                }

        readiness = readiness_index.get(kind)
        if not isinstance(readiness, dict):
            failures.append(f"{contract_id}: readiness index entry is missing")
            continue
        expected_pairs = {
            "id": contract_id,
            "kind": kind,
            "ready_for_downstream_fixture_use": (
                consumer_check.get("ready_for_downstream_fixture_use") is True
            ),
            "contract_passed": bool(contract.get("contract_passed")),
            "required_fields_present": (
                consumer_check.get("required_fields_present") is True
            ),
            "missing_minimum_field_count": len(missing_fields),
            "missing_minimum_fields": missing_fields,
            "all_theorem_ids_resolved": (
                consumer_check.get("all_theorem_ids_resolved") is True
            ),
            "all_theorem_ids_proved": (
                consumer_check.get("all_theorem_ids_proved") is True
            ),
            "unresolved_theorem_count": len(
                consumer_check.get("unresolved_theorem_ids", [])
            ),
            "unproved_theorem_count": len(
                consumer_check.get("unproved_theorem_ids", [])
            ),
            "theorem_count": proof_status.get("theorem_count"),
            "planner_recommendation_count": len(recommendations),
            "planner_recommendation_ids": [
                recommendation["id"]
                for recommendation in recommendations
                if isinstance(recommendation, dict)
                and isinstance(recommendation.get("id"), str)
            ],
        }
        for key, expected in expected_pairs.items():
            if readiness.get(key) != expected:
                failures.append(f"{contract_id}: readiness index {key} drifted")

    if set(readiness_index) != contract_kinds_seen:
        failures.append("contract_readiness_index keys drifted from contract kinds")
    if set(recommendation_index) != set(expected_recommendation_index):
        failures.append("planner_recommendation_index keys drifted from contracts")
    for recommendation_id, expected in expected_recommendation_index.items():
        indexed = recommendation_index.get(recommendation_id)
        if not isinstance(indexed, dict):
            failures.append(
                f"planner_recommendation_index.{recommendation_id} must be an object"
            )
            continue
        for key, expected_value in expected.items():
            if indexed.get(key) != expected_value:
                failures.append(
                    f"planner_recommendation_index.{recommendation_id}.{key} drifted"
                )
    return failures


def _assert_consumer_pack(pack: dict[str, Any]) -> None:
    failures = validate_consumer_pack(pack)
    if failures:
        raise ContractPackSchemaError(
            "invalid Circle AI contract pack: " + "; ".join(failures)
        )


def readiness_summary(pack: dict[str, Any], kind: str) -> ContractReadinessSummary:
    """Return a compact readiness summary for one contract kind."""

    _assert_consumer_pack(pack)
    contract = find_contract(pack, kind)
    if contract is None:
        raise ContractPackSchemaError(f"unknown contract kind: {kind}")
    readiness = pack["contract_readiness_index"][kind]
    consumer_check = contract["consumer_check"]
    return ContractReadinessSummary(
        schema_id=str(pack.get("schema_id")),
        contract_id=str(contract.get("id")),
        kind=kind,
        ready_for_downstream_fixture_use=(
            readiness.get("ready_for_downstream_fixture_use") is True
        ),
        contract_passed=readiness.get("contract_passed") is True,
        required_fields_present=readiness.get("required_fields_present") is True,
        all_theorem_ids_resolved=(
            readiness.get("all_theorem_ids_resolved") is True
        ),
        all_theorem_ids_proved=readiness.get("all_theorem_ids_proved") is True,
        theorem_count=int(readiness.get("theorem_count", 0)),
        missing_minimum_fields=_as_str_tuple(
            consumer_check.get("missing_minimum_fields", [])
        ),
        unresolved_theorem_ids=_as_str_tuple(
            consumer_check.get("unresolved_theorem_ids", [])
        ),
        unproved_theorem_ids=_as_str_tuple(
            consumer_check.get("unproved_theorem_ids", [])
        ),
        quickstart_docs=_as_str_tuple(contract.get("quickstart_docs", [])),
        living_book_pages=_as_str_tuple(contract.get("living_book_pages", [])),
        entrypoints=_as_str_tuple(contract.get("entrypoints", [])),
        validation_commands=_as_str_tuple(contract.get("validation_commands", [])),
        planner_recommendation_count=int(
            readiness.get("planner_recommendation_count", 0),
        ),
        planner_recommendation_ids=_as_str_tuple(
            readiness.get("planner_recommendation_ids", []),
        ),
        theorem_ids=_as_str_tuple(contract.get("theorem_ids", [])),
        dictionary_ids=_as_str_tuple(contract.get("dictionary_ids", [])),
        minimum_fields=_as_str_tuple(consumer_check.get("minimum_fields", [])),
        source_paper=(
            str(contract["source_paper"])
            if isinstance(contract.get("source_paper"), str)
            else None
        ),
        not_claimed=str(contract.get("not_claimed", "")),
    )


def require_ready_contract(pack: dict[str, Any], kind: str) -> dict[str, Any]:
    """Return a contract record, or raise if it is not downstream-ready."""

    summary = readiness_summary(pack, kind)
    if not summary.ready:
        reasons = summary.failure_reasons() or ("readiness flag is false",)
        raise ContractNotReadyError(f"{kind} is not ready: {'; '.join(reasons)}")
    contract = find_contract(pack, kind)
    if contract is None:
        raise ContractPackSchemaError(f"unknown contract kind: {kind}")
    return contract


def contract_digest(
    pack: dict[str, Any],
    kind: str,
    *,
    fields: Iterable[str] | None = None,
    include_field_metadata: bool = False,
    include_recommendations: bool = False,
) -> dict[str, Any]:
    """Return a compact, copy-safe contract digest for downstream reports."""

    contract = require_ready_contract(pack, kind)
    summary = readiness_summary(pack, kind)
    contract_fields = contract.get("fields", {})
    if fields is None:
        requested_fields = list(summary.minimum_fields)
    else:
        requested_fields = list(fields)
    evidence_fields = {
        field: contract_fields[field]
        for field in requested_fields
        if isinstance(contract_fields, dict) and field in contract_fields
    }
    digest = {
        "schema_id": summary.schema_id,
        "contract_id": summary.contract_id,
        "kind": summary.kind,
        "ready_for_downstream_fixture_use": summary.ready,
        "theorem_count": summary.theorem_count,
        "theorem_ids": list(summary.theorem_ids),
        "dictionary_ids": list(summary.dictionary_ids),
        "evidence_fields": evidence_fields,
        "missing_requested_fields": [
            field for field in requested_fields if field not in evidence_fields
        ],
        "quickstart_docs": list(summary.quickstart_docs),
        "living_book_pages": list(summary.living_book_pages),
        "entrypoints": list(summary.entrypoints),
        "validation_commands": list(summary.validation_commands),
        "source_paper": summary.source_paper,
        "not_claimed": summary.not_claimed,
    }
    if include_field_metadata:
        schema = pack.get("contract_schema", {})
        catalog_by_kind = (
            schema.get("minimum_field_catalog_by_kind", {})
            if isinstance(schema, dict)
            else {}
        )
        field_catalog = (
            catalog_by_kind.get(kind, {})
            if isinstance(catalog_by_kind, dict)
            else {}
        )
        digest["field_catalog"] = {
            field: field_catalog[field]
            for field in evidence_fields
            if isinstance(field_catalog, dict) and field in field_catalog
        }
    if include_recommendations:
        digest["planner_recommendations"] = [
            dict(recommendation)
            for recommendation in contract_recommendations(pack, kind)
        ]
    return digest


def contract_recommendations(
    pack: dict[str, Any],
    kind: str,
) -> tuple[dict[str, Any], ...]:
    """Return structured planner recommendations for a ready contract."""

    contract = require_ready_contract(pack, kind)
    recommendations = contract.get("planner_recommendations", [])
    if not isinstance(recommendations, list):
        return ()
    return tuple(
        dict(recommendation)
        for recommendation in recommendations
        if isinstance(recommendation, dict)
    )


def planner_recommendation_index(pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the top-level recommendation index after consumer validation."""

    _assert_consumer_pack(pack)
    index = pack.get("planner_recommendation_index", {})
    if not isinstance(index, dict):
        return {}
    return {
        recommendation_id: dict(record)
        for recommendation_id, record in index.items()
        if isinstance(recommendation_id, str) and isinstance(record, dict)
    }


def planner_recommendations_for_kind(
    pack: dict[str, Any],
    kind: str,
) -> tuple[dict[str, Any], ...]:
    """Return indexed recommendation summaries for one contract kind."""

    contract = require_ready_contract(pack, kind)
    recommendations = contract.get("planner_recommendations", [])
    if not isinstance(recommendations, list):
        return ()
    index = planner_recommendation_index(pack)
    return tuple(
        dict(index[recommendation["id"]])
        for recommendation in recommendations
        if isinstance(recommendation, dict)
        and isinstance(recommendation.get("id"), str)
        and recommendation["id"] in index
    )


def planner_action_plan(
    pack: dict[str, Any],
    kinds: Iterable[str] | None = None,
    *,
    include_values: bool = False,
) -> dict[str, Any]:
    """Return a copy-safe theorem-linked planner action plan.

    The default form keeps evidence field names rather than values. Pass
    ``include_values=True`` when a downstream planner needs the concrete
    theorem-backed field values and recommendation-specific parameters.
    """

    selected_kinds = list(kinds) if kinds is not None else list(contract_kinds(pack))
    actions: list[dict[str, Any]] = []
    for kind in selected_kinds:
        contract = require_ready_contract(pack, kind)
        contract_fields = contract.get("fields", {})
        fields = contract_fields if isinstance(contract_fields, dict) else {}
        raw_recommendations = {
            recommendation["id"]: recommendation
            for recommendation in contract_recommendations(pack, kind)
            if isinstance(recommendation.get("id"), str)
        }
        for recommendation in planner_recommendations_for_kind(pack, kind):
            action: dict[str, Any] = {
                "recommendation_id": recommendation["id"],
                "kind": recommendation["kind"],
                "contract_id": recommendation["contract_id"],
                "ready_for_downstream_fixture_use": recommendation[
                    "ready_for_downstream_fixture_use"
                ],
                "action_kind": recommendation["action_kind"],
                "status": recommendation["status"],
                "coverage_scope": recommendation["coverage_scope"],
                "evidence_fields": recommendation["evidence_fields"],
                "theorem_ids": recommendation["theorem_ids"],
                "quickstart_docs": recommendation["quickstart_docs"],
                "living_book_pages": recommendation["living_book_pages"],
                "validation_commands": recommendation["validation_commands"],
                "source_paper": recommendation["source_paper"],
                "not_claimed": recommendation["not_claimed"],
            }
            if include_values:
                evidence_fields = [
                    field
                    for field in recommendation["evidence_fields"]
                    if isinstance(field, str)
                ]
                raw = raw_recommendations.get(recommendation["id"], {})
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
                    for key, value in raw.items()
                    if key not in EXPECTED_RECOMMENDATION_KEYS
                }
            actions.append(action)
    return {
        "schema_id": pack.get("schema_id"),
        "planner_schema": "circle_calculus.ai_contract_planner.v0",
        "planner_includes_values": include_values,
        "selected_kinds": selected_kinds,
        "planner_recommendation_count": len(actions),
        "ready_recommendation_count": sum(
            1
            for action in actions
            if action["ready_for_downstream_fixture_use"] is True
        ),
        "action_plan": actions,
    }


def find_planner_recommendation(
    pack: dict[str, Any],
    recommendation_id: str,
) -> dict[str, Any] | None:
    """Return one indexed recommendation summary by id."""

    return planner_recommendation_index(pack).get(recommendation_id)
