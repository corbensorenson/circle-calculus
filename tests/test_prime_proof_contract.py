from __future__ import annotations

import pytest

from scripts.check_prime_proof_contract import (
    EXPECTED_LEAN_MODULE,
    EXPECTED_RUST_DOMAIN,
    EXPECTED_THEOREM_IDS,
    check_contract_against_manifest,
    compare_contracts,
)


def contract() -> dict:
    return {
        "name": "prime_horizon_sqrt_containment",
        "lean_module": EXPECTED_LEAN_MODULE,
        "theorem_ids": EXPECTED_THEOREM_IDS,
        "lean_names": [
            "Circle.primitiveHorizonContained_iff_dvd",
            "Circle.primeHorizon_iff_no_smaller_contained",
            "Circle.primeHorizon_iff_no_sqrt_contained",
            "Circle.primeHorizon_of_no_sqrt_contained",
            "Circle.not_primeHorizon_has_sqrt_contained",
        ],
        "rust_domain": EXPECTED_RUST_DOMAIN,
        "scope": "Lean proves the contract; Rust supplies exact arithmetic.",
    }


def manifest_by_id() -> dict:
    return {
        theorem_id: {"id": theorem_id, "status": "proved", "lean_name": lean_name}
        for theorem_id, lean_name in zip(
            EXPECTED_THEOREM_IDS,
            contract()["lean_names"],
        )
    }


def test_contract_matches_manifest() -> None:
    check_contract_against_manifest(contract(), manifest_by_id(), "test")


def test_contract_rejects_manifest_lean_name_drift() -> None:
    manifest = manifest_by_id()
    manifest["CC-T0075"] = {
        **manifest["CC-T0075"],
        "lean_name": "Circle.wrong_name",
    }

    with pytest.raises(AssertionError, match="lean_name mismatch"):
        check_contract_against_manifest(contract(), manifest, "test")


def test_contract_rejects_unproved_manifest_entry() -> None:
    manifest = manifest_by_id()
    manifest["CC-T0076"] = {**manifest["CC-T0076"], "status": "planned"}

    with pytest.raises(AssertionError, match="is not proved"):
        check_contract_against_manifest(contract(), manifest, "test")


def test_compare_contracts_rejects_per_command_drift() -> None:
    actual = {**contract(), "lean_module": "Circle.Core.Prime"}

    with pytest.raises(AssertionError, match="differs from reference"):
        compare_contracts(contract(), actual, "range_count")
