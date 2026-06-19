"""Consumer helpers for the generated Circle AI contract pack.

This module is intentionally lightweight. It validates the public JSON shape a
downstream project needs, but it does not require Lean, manifests, or repository
validation scripts to be present.
"""

from __future__ import annotations

import copy
import json
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


EXPECTED_SCHEMA_ID = "circle_calculus.ai_contract_pack.v0"
DEFAULT_PACK = Path("site/data/generated/circle_ai_contract_pack.json")
FINGERPRINT_ALGORITHM = "sha256-json-v1"
FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_RECOMMENDATION_KEYS = {
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


class ContractConsumerError(ValueError):
    """Base error for consumer-facing contract-pack failures."""


class ContractPackSchemaError(ContractConsumerError):
    """Raised when the pack is malformed or internally inconsistent."""


class ContractNotReadyError(ContractConsumerError):
    """Raised when a requested contract kind is present but not ready."""


class ContractFingerprintMismatchError(ContractConsumerError):
    """Raised when a pinned pack or contract fingerprint does not match."""


class ContractAcceptanceError(ContractConsumerError):
    """Raised when a strict downstream acceptance receipt cannot be issued."""


class ContractAcceptancePolicyError(ContractAcceptanceError):
    """Raised when a downstream acceptance policy cannot be satisfied."""


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
    payload = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
    if pack.get("content_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        failures.append(
            "content_fingerprint_algorithm must be "
            f"{FINGERPRINT_ALGORITHM!r}"
        )
    pack_fingerprint = pack.get("pack_content_fingerprint")
    if not isinstance(pack_fingerprint, str) or not SHA256_HEX_RE.fullmatch(
        pack_fingerprint
    ):
        failures.append("pack_content_fingerprint must be a lowercase sha256 hex string")
    elif pack_fingerprint != _json_fingerprint(pack):
        failures.append("pack_content_fingerprint drifted from pack content")

    contracts = pack.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        failures.append("contracts must be a non-empty list")
        return failures

    fingerprint_index = pack.get("contract_fingerprint_index")
    if not isinstance(fingerprint_index, dict) or not fingerprint_index:
        failures.append("contract_fingerprint_index must be a non-empty object")
        fingerprint_index = {}

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
    seen_recommendation_ids: dict[str, str] = {}
    expected_fingerprint_index: dict[str, dict[str, str]] = {}
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

        if contract.get("content_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
            failures.append(
                f"{contract_id}: content_fingerprint_algorithm must be "
                f"{FINGERPRINT_ALGORITHM!r}"
            )
        content_fingerprint = contract.get("content_fingerprint")
        if not isinstance(content_fingerprint, str) or not SHA256_HEX_RE.fullmatch(
            content_fingerprint
        ):
            failures.append(
                f"{contract_id}: content_fingerprint must be a lowercase "
                "sha256 hex string"
            )
        elif content_fingerprint != _json_fingerprint(contract):
            failures.append(f"{contract_id}: content_fingerprint drifted")
        if isinstance(content_fingerprint, str):
            expected_fingerprint_index[kind] = {
                "id": str(contract_id),
                "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
                "content_fingerprint": content_fingerprint,
            }

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
            if not isinstance(recommendation_id, str) or not recommendation_id:
                failures.append(
                    f"{contract_id}: planner_recommendations[{index}].id "
                    "must be a non-empty string"
                )
            else:
                previous_contract_id = seen_recommendation_ids.get(
                    recommendation_id
                )
                if previous_contract_id is not None:
                    failures.append(
                        f"{contract_id}: duplicate planner recommendation id "
                        f"{recommendation_id} already used by "
                        f"{previous_contract_id}"
                    )
                else:
                    seen_recommendation_ids[recommendation_id] = str(contract_id)
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
    if set(fingerprint_index) != set(expected_fingerprint_index):
        failures.append("contract_fingerprint_index keys drifted from contracts")
    for kind, expected in expected_fingerprint_index.items():
        indexed = fingerprint_index.get(kind)
        if not isinstance(indexed, dict):
            failures.append(f"contract_fingerprint_index.{kind} must be an object")
            continue
        for key, expected_value in expected.items():
            if indexed.get(key) != expected_value:
                failures.append(f"contract_fingerprint_index.{kind}.{key} drifted")
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


def readiness_report(
    pack: dict[str, Any],
    kinds: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a machine-readable readiness report for selected contract kinds."""

    selected_kinds = list(kinds) if kinds is not None else list(contract_kinds(pack))
    summaries = [
        readiness_summary(pack, kind).to_dict()
        for kind in selected_kinds
    ]
    ready_count = sum(
        1
        for summary in summaries
        if summary["ready_for_downstream_fixture_use"] is True
    )
    return {
        "schema_id": pack.get("schema_id"),
        "readiness_schema": "circle_calculus.ai_contract_readiness.v0",
        "selected_kinds": selected_kinds,
        "contract_count": len(summaries),
        "ready_contract_count": ready_count,
        "all_ready": ready_count == len(summaries),
        "summaries": summaries,
    }


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


def contract_fingerprint_summary(pack: dict[str, Any]) -> dict[str, Any]:
    """Return pack and per-contract fingerprints after consumer validation."""

    _assert_consumer_pack(pack)
    return {
        "schema_id": pack.get("schema_id"),
        "content_fingerprint_algorithm": pack.get("content_fingerprint_algorithm"),
        "pack_content_fingerprint": pack.get("pack_content_fingerprint"),
        "contract_fingerprint_index": {
            kind: dict(record)
            for kind, record in pack.get("contract_fingerprint_index", {}).items()
            if isinstance(kind, str) and isinstance(record, dict)
        },
    }


def verify_fingerprint_expectations(
    pack: dict[str, Any],
    *,
    expected_pack_fingerprint: str | None = None,
    expected_contract_fingerprints: dict[str, str] | None = None,
) -> tuple[str, ...]:
    """Return fingerprint expectation failures for a downstream pin set."""

    _assert_consumer_pack(pack)
    failures: list[str] = []
    summary = contract_fingerprint_summary(pack)
    if expected_pack_fingerprint is not None:
        if not SHA256_HEX_RE.fullmatch(expected_pack_fingerprint):
            failures.append(
                "expected pack fingerprint is not a lowercase sha256 hex string"
            )
        elif (
            summary["pack_content_fingerprint"]
            != expected_pack_fingerprint
        ):
            failures.append(
                "pack fingerprint mismatch: expected "
                f"{expected_pack_fingerprint}, got "
                f"{summary['pack_content_fingerprint']}"
            )

    index = summary["contract_fingerprint_index"]
    for kind, expected in (expected_contract_fingerprints or {}).items():
        if not SHA256_HEX_RE.fullmatch(expected):
            failures.append(
                f"expected contract fingerprint for {kind} is not a lowercase "
                "sha256 hex string"
            )
            continue
        record = index.get(kind)
        if record is None:
            failures.append(f"unknown contract kind for fingerprint expectation: {kind}")
            continue
        actual = record.get("content_fingerprint")
        if actual != expected:
            failures.append(
                f"{kind} fingerprint mismatch: expected {expected}, got {actual}"
            )
    return tuple(failures)


def require_fingerprint_expectations(
    pack: dict[str, Any],
    *,
    expected_pack_fingerprint: str | None = None,
    expected_contract_fingerprints: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return fingerprint summary, or raise when pinned fingerprints drift."""

    failures = verify_fingerprint_expectations(
        pack,
        expected_pack_fingerprint=expected_pack_fingerprint,
        expected_contract_fingerprints=expected_contract_fingerprints,
    )
    if failures:
        raise ContractFingerprintMismatchError(
            "Circle AI contract fingerprint expectation failed: "
            + "; ".join(failures)
        )
    return contract_fingerprint_summary(pack)


def refresh_acceptance_policy_fingerprints(
    pack: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Return ``policy`` with pack and selected-contract fingerprints refreshed.

    The function deliberately preserves every required field, theorem id,
    recommendation id, recommendation evidence-field pin, recommendation
    theorem-id pin, recommendation action-parameter pin, and recommendation
    action-parameter path pin. Use it to update an acceptance-policy lockfile
    after the generated contract pack changes, without silently weakening the
    acceptance requirements.
    """

    policy_schema = "circle_calculus.ai_contract_acceptance_policy.v0"
    if not isinstance(policy, dict):
        raise ContractAcceptancePolicyError("acceptance policy must be an object")
    fingerprints = contract_fingerprint_summary(pack)
    contract_fingerprints = fingerprints.get("contract_fingerprint_index", {})
    if not isinstance(contract_fingerprints, dict):
        raise ContractAcceptancePolicyError(
            "Circle AI contract pack is missing contract_fingerprint_index"
        )

    failures: list[str] = []
    if policy.get("schema_id") != policy_schema:
        failures.append(f"policy.schema_id must be {policy_schema!r}")
    raw_contracts = policy.get("contracts")
    if not isinstance(raw_contracts, list) or not raw_contracts:
        failures.append("policy.contracts must be a non-empty list")
        raw_contracts = []

    refreshed = copy.deepcopy(policy)
    refreshed["expected_pack_fingerprint"] = fingerprints["pack_content_fingerprint"]
    refreshed_contracts = refreshed.get("contracts")
    if not isinstance(refreshed_contracts, list):
        refreshed_contracts = []

    seen_kinds: set[str] = set()
    for index, raw_spec in enumerate(raw_contracts):
        context = f"policy.contracts[{index}]"
        if not isinstance(raw_spec, dict):
            failures.append(f"{context} must be an object")
            continue
        kind = raw_spec.get("kind")
        if not isinstance(kind, str) or not kind.strip():
            failures.append(f"{context}.kind must be a non-empty string")
            continue
        if kind in seen_kinds:
            failures.append(f"{context}.kind repeats contract kind {kind!r}")
            continue
        seen_kinds.add(kind)
        indexed = contract_fingerprints.get(kind)
        if not isinstance(indexed, dict):
            failures.append(f"{context}.kind is not in contract_fingerprint_index")
            continue
        content_fingerprint = indexed.get("content_fingerprint")
        if not isinstance(content_fingerprint, str):
            failures.append(
                f"contract_fingerprint_index.{kind}.content_fingerprint must be a string"
            )
            continue
        refreshed_spec = refreshed_contracts[index]
        if isinstance(refreshed_spec, dict):
            refreshed_spec["expected_contract_fingerprint"] = content_fingerprint

    if failures:
        raise ContractAcceptancePolicyError(
            "Circle AI contract acceptance policy refresh failed: "
            + "; ".join(failures)
        )
    return refreshed


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


def _strict_receipt_string_tuple(
    value: Iterable[str] | None,
    *,
    context: str,
    default: Iterable[str] = (),
) -> tuple[str, ...]:
    if value is None:
        items = tuple(default)
    elif isinstance(value, (str, bytes)):
        raise ContractAcceptanceError(
            f"{context} must be an iterable of non-empty strings, not a string"
        )
    else:
        items = tuple(value)
    if any(not isinstance(item, str) or not item for item in items):
        raise ContractAcceptanceError(
            f"{context} must contain only non-empty strings"
        )
    if len(set(items)) != len(items):
        raise ContractAcceptanceError(
            f"{context} must not contain duplicate strings"
        )
    return items


def _strict_receipt_requirement_map(
    value: dict[str, Iterable[str]] | None,
    *,
    context: str,
) -> dict[str, tuple[str, ...]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ContractAcceptanceError(f"{context} must be an object")
    normalized: dict[str, tuple[str, ...]] = {}
    for recommendation_id, requirements in value.items():
        if not isinstance(recommendation_id, str) or not recommendation_id:
            raise ContractAcceptanceError(
                f"{context} keys must be non-empty strings"
            )
        normalized[recommendation_id] = _strict_receipt_string_tuple(
            requirements,
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
    if not isinstance(item, dict):
        return False
    if "=" not in selector:
        return False
    key, expected = selector.split("=", 1)
    return isinstance(key, str) and item.get(key) == expected


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
        matches = [
            item
            for item in current
            if _path_selector_matches(item, selector)
        ]
        if not matches:
            return False
        current = matches[0]
    return True


def contract_acceptance_receipt(
    pack: dict[str, Any],
    kind: str,
    *,
    required_fields: Iterable[str] | None = None,
    required_theorem_ids: Iterable[str] | None = None,
    required_recommendation_ids: Iterable[str] | None = None,
    required_recommendation_evidence_fields: dict[str, Iterable[str]] | None = None,
    required_recommendation_theorem_ids: dict[str, Iterable[str]] | None = None,
    required_recommendation_action_parameters: dict[str, Iterable[str]] | None = None,
    required_recommendation_action_parameter_paths: (
        dict[str, Iterable[str]] | None
    ) = None,
    include_field_metadata: bool = False,
) -> dict[str, Any]:
    """Return a strict CI-friendly receipt for a ready contract.

    Unlike ``contract_digest``, this function fails when a requested evidence
    field, theorem id, or planner recommendation is missing. Use it when a
    downstream project wants a hard accept/reject gate rather than an
    exploratory report.
    """

    summary = readiness_summary(pack, kind)
    field_names = _strict_receipt_string_tuple(
        required_fields,
        context="required_fields",
        default=summary.minimum_fields,
    )
    theorem_requirements = _strict_receipt_string_tuple(
        required_theorem_ids,
        context="required_theorem_ids",
    )
    recommendation_field_requirements = _strict_receipt_requirement_map(
        required_recommendation_evidence_fields,
        context="required_recommendation_evidence_fields",
    )
    recommendation_theorem_requirements = _strict_receipt_requirement_map(
        required_recommendation_theorem_ids,
        context="required_recommendation_theorem_ids",
    )
    recommendation_action_parameter_requirements = _strict_receipt_requirement_map(
        required_recommendation_action_parameters,
        context="required_recommendation_action_parameters",
    )
    recommendation_action_parameter_path_requirements = (
        _strict_receipt_requirement_map(
            required_recommendation_action_parameter_paths,
            context="required_recommendation_action_parameter_paths",
        )
    )
    explicit_recommendation_ids = _strict_receipt_string_tuple(
        required_recommendation_ids,
        context="required_recommendation_ids",
    )
    recommendation_ids = tuple(
        dict.fromkeys(
            explicit_recommendation_ids
            + tuple(recommendation_field_requirements)
            + tuple(recommendation_theorem_requirements)
            + tuple(recommendation_action_parameter_requirements)
            + tuple(recommendation_action_parameter_path_requirements)
        )
    )
    digest = contract_digest(
        pack,
        kind,
        fields=field_names,
        include_field_metadata=include_field_metadata,
    )
    failures: list[str] = []
    missing_fields = tuple(digest["missing_requested_fields"])
    if missing_fields:
        failures.append(
            "missing requested evidence fields: " + ",".join(missing_fields)
        )
    theorem_id_set = set(summary.theorem_ids)
    missing_theorem_ids = tuple(
        theorem_id for theorem_id in theorem_requirements
        if theorem_id not in theorem_id_set
    )
    if missing_theorem_ids:
        failures.append(
            "missing requested theorem ids: " + ",".join(missing_theorem_ids)
        )

    available_recommendations = {
        recommendation["id"]: recommendation
        for recommendation in contract_recommendations(pack, kind)
        if isinstance(recommendation.get("id"), str)
    }
    missing_recommendations = tuple(
        recommendation_id
        for recommendation_id in recommendation_ids
        if recommendation_id not in available_recommendations
    )
    if missing_recommendations:
        failures.append(
            "missing requested planner recommendations: "
            + ",".join(missing_recommendations)
        )
    for recommendation_id, fields in recommendation_field_requirements.items():
        recommendation = available_recommendations.get(recommendation_id)
        if recommendation is None:
            continue
        evidence_fields = set(_as_str_tuple(recommendation.get("evidence_fields", [])))
        missing_evidence_fields = tuple(
            field for field in fields if field not in evidence_fields
        )
        if missing_evidence_fields:
            failures.append(
                f"{recommendation_id} missing required recommendation evidence "
                "fields: " + ",".join(missing_evidence_fields)
            )
    for recommendation_id, theorem_ids in recommendation_theorem_requirements.items():
        recommendation = available_recommendations.get(recommendation_id)
        if recommendation is None:
            continue
        recommendation_theorem_ids = set(
            _as_str_tuple(recommendation.get("theorem_ids", []))
        )
        missing_recommendation_theorems = tuple(
            theorem_id for theorem_id in theorem_ids
            if theorem_id not in recommendation_theorem_ids
        )
        if missing_recommendation_theorems:
            failures.append(
                f"{recommendation_id} missing required recommendation theorem "
                "ids: " + ",".join(missing_recommendation_theorems)
            )
    for recommendation_id, parameter_keys in (
        recommendation_action_parameter_requirements.items()
    ):
        recommendation = available_recommendations.get(recommendation_id)
        if recommendation is None:
            continue
        action_parameter_keys = set(recommendation) - EXPECTED_RECOMMENDATION_KEYS
        missing_action_parameters = tuple(
            parameter_key
            for parameter_key in parameter_keys
            if parameter_key not in action_parameter_keys
        )
        if missing_action_parameters:
            failures.append(
                f"{recommendation_id} missing required recommendation action "
                "parameters: " + ",".join(missing_action_parameters)
            )
    for recommendation_id, paths in recommendation_action_parameter_path_requirements.items():
        recommendation = available_recommendations.get(recommendation_id)
        if recommendation is None:
            continue
        action_parameter_keys = set(recommendation) - EXPECTED_RECOMMENDATION_KEYS
        invalid_action_parameter_paths = tuple(
            path
            for path in paths
            if (
                _action_parameter_path_head(path) is None
                or _action_parameter_path_head(path) not in action_parameter_keys
            )
        )
        if invalid_action_parameter_paths:
            failures.append(
                f"{recommendation_id} has invalid recommendation action-parameter "
                "paths: " + ",".join(invalid_action_parameter_paths)
            )
            continue
        missing_action_parameter_paths = tuple(
            path for path in paths if not _json_path_exists(recommendation, path)
        )
        if missing_action_parameter_paths:
            failures.append(
                f"{recommendation_id} missing required recommendation "
                "action-parameter paths: "
                + ",".join(missing_action_parameter_paths)
            )
    if failures:
        raise ContractAcceptanceError(
            f"{kind} contract acceptance failed: " + "; ".join(failures)
        )

    fingerprints = contract_fingerprint_summary(pack)
    contract_fingerprint = fingerprints["contract_fingerprint_index"][kind]
    receipt = {
        "schema_id": summary.schema_id,
        "receipt_schema": "circle_calculus.ai_contract_acceptance_receipt.v0",
        "accepted": True,
        "kind": summary.kind,
        "contract_id": summary.contract_id,
        "content_fingerprint_algorithm": fingerprints[
            "content_fingerprint_algorithm"
        ],
        "pack_content_fingerprint": fingerprints["pack_content_fingerprint"],
        "contract_content_fingerprint": contract_fingerprint[
            "content_fingerprint"
        ],
        "required_fields": list(field_names),
        "required_theorem_ids": list(theorem_requirements),
        "evidence_fields": digest["evidence_fields"],
        "required_recommendation_ids": list(recommendation_ids),
        "required_recommendation_evidence_fields": {
            recommendation_id: list(fields)
            for recommendation_id, fields in recommendation_field_requirements.items()
        },
        "required_recommendation_theorem_ids": {
            recommendation_id: list(theorem_ids)
            for recommendation_id, theorem_ids
            in recommendation_theorem_requirements.items()
        },
        "required_recommendation_action_parameters": {
            recommendation_id: list(parameter_keys)
            for recommendation_id, parameter_keys
            in recommendation_action_parameter_requirements.items()
        },
        "required_recommendation_action_parameter_paths": {
            recommendation_id: list(paths)
            for recommendation_id, paths
            in recommendation_action_parameter_path_requirements.items()
        },
        "planner_recommendations": [
            dict(available_recommendations[recommendation_id])
            for recommendation_id in recommendation_ids
        ],
        "theorem_ids": list(summary.theorem_ids),
        "dictionary_ids": list(summary.dictionary_ids),
        "quickstart_docs": list(summary.quickstart_docs),
        "living_book_pages": list(summary.living_book_pages),
        "validation_commands": list(summary.validation_commands),
        "source_paper": summary.source_paper,
        "not_claimed": summary.not_claimed,
    }
    if include_field_metadata and "field_catalog" in digest:
        receipt["field_catalog"] = digest["field_catalog"]
    return receipt


def _policy_string_list(
    spec: dict[str, Any],
    key: str,
    *,
    context: str,
    failures: list[str],
) -> tuple[str, ...]:
    value = spec.get(key, [])
    if not isinstance(value, list):
        failures.append(f"{context}.{key} must be a list of strings")
        return ()
    non_strings = [item for item in value if not isinstance(item, str)]
    if non_strings:
        failures.append(f"{context}.{key} must contain only strings")
        return ()
    empty_items = [item for item in value if not item]
    if empty_items:
        failures.append(f"{context}.{key} must not contain empty strings")
    if len(set(value)) != len(value):
        failures.append(f"{context}.{key} must not contain duplicate strings")
    return tuple(value)


def _policy_recommendation_field_requirements(
    spec: dict[str, Any],
    key: str,
    *,
    context: str,
    failures: list[str],
) -> dict[str, tuple[str, ...]]:
    value = spec.get(key, {})
    if not isinstance(value, dict):
        failures.append(f"{context}.{key} must be an object of string lists")
        return {}
    requirements: dict[str, tuple[str, ...]] = {}
    for recommendation_id, fields in value.items():
        if not isinstance(recommendation_id, str) or not recommendation_id:
            failures.append(f"{context}.{key} keys must be non-empty strings")
            continue
        if not isinstance(fields, list):
            failures.append(f"{context}.{key}.{recommendation_id} must be a list")
            continue
        non_strings = [field for field in fields if not isinstance(field, str)]
        if non_strings:
            failures.append(
                f"{context}.{key}.{recommendation_id} must contain only strings"
            )
            continue
        empty_fields = [field for field in fields if not field]
        if empty_fields:
            failures.append(
                f"{context}.{key}.{recommendation_id} must not contain empty strings"
            )
        if len(set(fields)) != len(fields):
            failures.append(
                f"{context}.{key}.{recommendation_id} must not contain duplicate strings"
            )
        requirements[recommendation_id] = tuple(fields)
    return requirements


def contract_acceptance_policy_report(
    pack: dict[str, Any],
    policy: dict[str, Any],
    *,
    include_field_metadata: bool = False,
) -> dict[str, Any]:
    """Validate a pinned downstream acceptance policy and emit receipts.

    A policy is stricter than a digest: it pins the pack fingerprint, pins every
    selected contract fingerprint, requires declared evidence fields and
    theorem ids, and can require planner recommendation ids with specific
    evidence fields, theorem ids, value-mode action-parameter keys, or nested
    action-parameter paths. This is the shape a downstream CI job can use to
    reject stale or weakened Circle AI contracts before consuming their
    certificate fields.
    """

    policy_schema = "circle_calculus.ai_contract_acceptance_policy.v0"
    if not isinstance(policy, dict):
        raise ContractAcceptancePolicyError("acceptance policy must be an object")

    failures: list[str] = []
    if policy.get("schema_id") != policy_schema:
        failures.append(f"policy.schema_id must be {policy_schema!r}")
    expected_pack_fingerprint = policy.get("expected_pack_fingerprint")
    if not isinstance(expected_pack_fingerprint, str):
        failures.append("policy.expected_pack_fingerprint must be a string")
        expected_pack_fingerprint = None

    raw_contracts = policy.get("contracts")
    if not isinstance(raw_contracts, list) or not raw_contracts:
        failures.append("policy.contracts must be a non-empty list")
        raw_contracts = []

    contract_expectations: dict[str, str] = {}
    normalized_specs: list[dict[str, Any]] = []
    seen_kinds: set[str] = set()
    for index, raw_spec in enumerate(raw_contracts):
        context = f"policy.contracts[{index}]"
        if not isinstance(raw_spec, dict):
            failures.append(f"{context} must be an object")
            continue
        kind = raw_spec.get("kind")
        if not isinstance(kind, str) or not kind.strip():
            failures.append(f"{context}.kind must be a non-empty string")
            continue
        if kind in seen_kinds:
            failures.append(f"{context}.kind repeats contract kind {kind!r}")
            continue
        seen_kinds.add(kind)
        expected_contract_fingerprint = raw_spec.get(
            "expected_contract_fingerprint"
        )
        if not isinstance(expected_contract_fingerprint, str):
            failures.append(
                f"{context}.expected_contract_fingerprint must be a string"
            )
        else:
            contract_expectations[kind] = expected_contract_fingerprint

        required_fields = _policy_string_list(
            raw_spec,
            "required_fields",
            context=context,
            failures=failures,
        )
        required_theorem_ids = _policy_string_list(
            raw_spec,
            "required_theorem_ids",
            context=context,
            failures=failures,
        )
        required_recommendation_ids = _policy_string_list(
            raw_spec,
            "required_recommendation_ids",
            context=context,
            failures=failures,
        )
        required_recommendation_evidence_fields = (
            _policy_recommendation_field_requirements(
                raw_spec,
                "required_recommendation_evidence_fields",
                context=context,
                failures=failures,
            )
        )
        required_recommendation_theorem_ids = (
            _policy_recommendation_field_requirements(
                raw_spec,
                "required_recommendation_theorem_ids",
                context=context,
                failures=failures,
            )
        )
        required_recommendation_action_parameters = (
            _policy_recommendation_field_requirements(
                raw_spec,
                "required_recommendation_action_parameters",
                context=context,
                failures=failures,
            )
        )
        required_recommendation_action_parameter_paths = (
            _policy_recommendation_field_requirements(
                raw_spec,
                "required_recommendation_action_parameter_paths",
                context=context,
                failures=failures,
            )
        )
        all_required_recommendation_ids = tuple(
            dict.fromkeys(
                required_recommendation_ids
                + tuple(required_recommendation_evidence_fields)
                + tuple(required_recommendation_theorem_ids)
                + tuple(required_recommendation_action_parameters)
                + tuple(required_recommendation_action_parameter_paths)
            )
        )
        normalized_specs.append({
            "kind": kind,
            "required_fields": required_fields,
            "required_theorem_ids": required_theorem_ids,
            "required_recommendation_ids": all_required_recommendation_ids,
            "required_recommendation_evidence_fields": (
                required_recommendation_evidence_fields
            ),
            "required_recommendation_theorem_ids": (
                required_recommendation_theorem_ids
            ),
            "required_recommendation_action_parameters": (
                required_recommendation_action_parameters
            ),
            "required_recommendation_action_parameter_paths": (
                required_recommendation_action_parameter_paths
            ),
            "include_field_metadata": bool(
                raw_spec.get("include_field_metadata", include_field_metadata)
            ),
        })

    if expected_pack_fingerprint is not None:
        failures.extend(
            verify_fingerprint_expectations(
                pack,
                expected_pack_fingerprint=expected_pack_fingerprint,
                expected_contract_fingerprints=contract_expectations,
            )
        )
    if failures:
        raise ContractAcceptancePolicyError(
            "Circle AI contract acceptance policy failed: " + "; ".join(failures)
        )

    receipts: list[dict[str, Any]] = []
    for spec in normalized_specs:
        try:
            receipts.append(
                contract_acceptance_receipt(
                    pack,
                    spec["kind"],
                    required_fields=spec["required_fields"],
                    required_theorem_ids=spec["required_theorem_ids"],
                    required_recommendation_ids=spec[
                        "required_recommendation_ids"
                    ],
                    required_recommendation_evidence_fields=spec[
                        "required_recommendation_evidence_fields"
                    ],
                    required_recommendation_theorem_ids=spec[
                        "required_recommendation_theorem_ids"
                    ],
                    required_recommendation_action_parameters=spec[
                        "required_recommendation_action_parameters"
                    ],
                    required_recommendation_action_parameter_paths=spec[
                        "required_recommendation_action_parameter_paths"
                    ],
                    include_field_metadata=spec["include_field_metadata"],
                )
            )
        except ContractConsumerError as exc:
            failures.append(str(exc))
    if failures:
        raise ContractAcceptancePolicyError(
            "Circle AI contract acceptance policy failed: " + "; ".join(failures)
        )

    fingerprints = contract_fingerprint_summary(pack)
    return {
        "schema_id": pack.get("schema_id"),
        "acceptance_policy_report_schema": (
            "circle_calculus.ai_contract_acceptance_policy_report.v0"
        ),
        "policy_schema": policy_schema,
        "policy_id": policy.get("policy_id"),
        "policy_name": policy.get("policy_name"),
        "accepted": True,
        "content_fingerprint_algorithm": fingerprints[
            "content_fingerprint_algorithm"
        ],
        "pack_content_fingerprint": fingerprints["pack_content_fingerprint"],
        "expected_pack_fingerprint": expected_pack_fingerprint,
        "contract_count": len(normalized_specs),
        "receipt_count": len(receipts),
        "receipts": receipts,
        "not_claimed": (
            "Acceptance means the selected theorem-linked contract fixtures "
            "match the pinned policy. It is not a claim of model quality, "
            "reasoning ability, speed, memory scaling, deployment safety, "
            "transfer, or ASI."
        ),
    }


def planner_action_plan(
    pack: dict[str, Any],
    kinds: Iterable[str] | None = None,
    *,
    include_values: bool = False,
    recommendation_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a copy-safe theorem-linked planner action plan.

    The default form keeps evidence field names rather than values. Pass
    ``include_values=True`` when a downstream planner needs the concrete
    theorem-backed field values and recommendation-specific parameters.
    """

    selected_kinds = list(kinds) if kinds is not None else list(contract_kinds(pack))
    selected_recommendation_ids = list(dict.fromkeys(recommendation_ids or ()))
    selected_recommendation_id_set = set(selected_recommendation_ids)
    actions: list[dict[str, Any]] = []
    emitted_recommendation_ids: set[str] = set()
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
            recommendation_id = recommendation["id"]
            if (
                selected_recommendation_id_set
                and recommendation_id not in selected_recommendation_id_set
            ):
                continue
            action: dict[str, Any] = {
                "recommendation_id": recommendation_id,
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
            emitted_recommendation_ids.add(str(recommendation_id))
    missing_recommendation_ids = [
        recommendation_id
        for recommendation_id in selected_recommendation_ids
        if recommendation_id not in emitted_recommendation_ids
    ]
    if missing_recommendation_ids:
        raise ContractConsumerError(
            "missing requested planner recommendations in selected scope: "
            + ",".join(missing_recommendation_ids)
        )
    return {
        "schema_id": pack.get("schema_id"),
        "planner_schema": "circle_calculus.ai_contract_planner.v0",
        "planner_includes_values": include_values,
        "selected_kinds": selected_kinds,
        "selected_recommendation_ids": selected_recommendation_ids,
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
