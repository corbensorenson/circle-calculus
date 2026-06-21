"""Stable public API for consuming Circle proof-carrying contract packs.

Use this module when another project wants to load, validate, fingerprint, and
gate public Circle contract artifacts without importing the internal builder
implementation.
"""

from __future__ import annotations

from .applications.circle_ai_contract_consumer import (
    ContractAcceptanceError,
    ContractAcceptancePolicyError,
    ContractConsumerError,
    ContractFingerprintMismatchError,
    ContractNotReadyError,
    ContractPackSchemaError,
    ContractReadinessSummary,
    contract_acceptance_policy_report,
    contract_acceptance_receipt,
    contract_digest,
    contract_fingerprint_summary,
    contract_kinds,
    find_contract,
    load_contract_pack,
    planner_action_plan,
    planner_recommendation_index,
    readiness_report,
    readiness_summary,
    refresh_acceptance_policy_fingerprints,
    require_ready_contract,
    validate_consumer_pack,
    verify_fingerprint_expectations,
)
from .applications.circle_ai_contracts import SCHEMA_ID as CONTRACT_PACK_SCHEMA_ID


__all__ = [
    "CONTRACT_PACK_SCHEMA_ID",
    "ContractAcceptanceError",
    "ContractAcceptancePolicyError",
    "ContractConsumerError",
    "ContractFingerprintMismatchError",
    "ContractNotReadyError",
    "ContractPackSchemaError",
    "ContractReadinessSummary",
    "contract_acceptance_policy_report",
    "contract_acceptance_receipt",
    "contract_digest",
    "contract_fingerprint_summary",
    "contract_kinds",
    "find_contract",
    "load_contract_pack",
    "planner_action_plan",
    "planner_recommendation_index",
    "readiness_report",
    "readiness_summary",
    "refresh_acceptance_policy_fingerprints",
    "require_ready_contract",
    "validate_consumer_pack",
    "verify_fingerprint_expectations",
]
