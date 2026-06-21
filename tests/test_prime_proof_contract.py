from __future__ import annotations

import pytest

from scripts.check_prime_proof_contract import (
    EXPECTED_LEAN_MODULE,
    EXPECTED_NEXT_THEOREM_IDS,
    EXPECTED_RUST_DOMAIN,
    EXPECTED_THEOREM_IDS,
    LeanSourceIndex,
    check_contract_against_manifest,
    check_next_contract_against_manifest,
    compare_contracts,
    read_line_server_consistent_contract_field,
    read_line_server_contract_field,
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


def next_contract() -> dict:
    return {
        "name": "prime_horizon_next_search_spec",
        "lean_module": EXPECTED_LEAN_MODULE,
        "theorem_ids": EXPECTED_NEXT_THEOREM_IDS,
        "lean_names": [
            "Circle.nextPrimeHorizonResultUpTo_some_iff",
            "Circle.nextPrimeHorizonResultUpTo_none_iff",
        ],
        "rust_domain": EXPECTED_RUST_DOMAIN,
        "scope": "Lean proves the next-prime result spec; Rust supplies exact arithmetic.",
    }


def next_manifest_by_id() -> dict:
    return {
        theorem_id: {"id": theorem_id, "status": "proved", "lean_name": lean_name}
        for theorem_id, lean_name in zip(
            EXPECTED_NEXT_THEOREM_IDS,
            next_contract()["lean_names"],
        )
    }


def test_contract_matches_manifest() -> None:
    check_contract_against_manifest(contract(), manifest_by_id(), "test")


def test_next_contract_matches_manifest() -> None:
    check_next_contract_against_manifest(
        next_contract(),
        next_manifest_by_id(),
        "next",
    )


def test_contract_matches_manifest_and_lean_source(tmp_path) -> None:
    module_path = tmp_path / "Circle" / "Core" / "Horizon.lean"
    module_path.parent.mkdir(parents=True)
    module_path.write_text(
        "\n".join(
            [
                "namespace Circle",
                "theorem primitiveHorizonContained_iff_dvd := by trivial",
                "theorem primeHorizon_iff_no_smaller_contained := by trivial",
                "theorem primeHorizon_iff_no_sqrt_contained := by trivial",
                "theorem primeHorizon_of_no_sqrt_contained := by trivial",
                "theorem not_primeHorizon_has_sqrt_contained := by trivial",
                "theorem nextPrimeHorizonResultUpTo_some_iff := by trivial",
                "theorem nextPrimeHorizonResultUpTo_none_iff := by trivial",
                "end Circle",
                "",
            ]
        )
    )

    check_contract_against_manifest(
        contract(),
        manifest_by_id(),
        "test",
        LeanSourceIndex(tmp_path),
    )
    check_next_contract_against_manifest(
        next_contract(),
        next_manifest_by_id(),
        "next",
        LeanSourceIndex(tmp_path),
    )


def test_contract_rejects_missing_lean_declaration(tmp_path) -> None:
    module_path = tmp_path / "Circle" / "Core" / "Horizon.lean"
    module_path.parent.mkdir(parents=True)
    module_path.write_text(
        "\n".join(
            [
                "namespace Circle",
                "theorem primitiveHorizonContained_iff_dvd := by trivial",
                "theorem primeHorizon_iff_no_smaller_contained := by trivial",
                "theorem primeHorizon_iff_no_sqrt_contained := by trivial",
                "theorem primeHorizon_of_no_sqrt_contained := by trivial",
                "end Circle",
                "",
            ]
        )
    )

    with pytest.raises(AssertionError, match="Lean declaration missing"):
        check_contract_against_manifest(
            contract(),
            manifest_by_id(),
            "test",
            LeanSourceIndex(tmp_path),
        )


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


def test_read_line_server_contract_field_reads_first_json_response(monkeypatch) -> None:
    class Completed:
        stdout = (
            '{"count":168,"proof_contract":{"name":"prime_horizon_sqrt_containment"},'
            '"count_proof_contract":{"name":"prime_horizon_range_count_spec"}}\n'
        )

    def fake_run(command, **kwargs):
        assert command[-1] == "--json"
        assert kwargs["input"] == "0 1000\nquit\n"
        return Completed()

    monkeypatch.setattr("scripts.check_prime_proof_contract.subprocess.run", fake_run)

    assert read_line_server_contract_field(
        ["circle-prime", "count-server", "--json"],
        "0 1000\nquit\n",
        "count_proof_contract",
    ) == {
        "name": "prime_horizon_range_count_spec"
    }


def test_read_line_server_consistent_contract_field_checks_every_response(
    monkeypatch,
) -> None:
    class Completed:
        stdout = (
            '{"count":168,'
            '"count_proof_contract":{"name":"prime_horizon_range_count_spec"}}\n'
            '{"count":167,'
            '"count_proof_contract":{"name":"prime_horizon_range_count_spec"}}\n'
        )

    def fake_run(command, **kwargs):
        assert command[-1] == "--json"
        assert kwargs["input"].startswith("shifted 2")
        return Completed()

    monkeypatch.setattr("scripts.check_prime_proof_contract.subprocess.run", fake_run)

    assert read_line_server_consistent_contract_field(
        ["circle-prime-count", "count-server", "--json"],
        "shifted 2 100 1000000000000 1000000010000\nquit\n",
        "count_proof_contract",
    ) == {
        "name": "prime_horizon_range_count_spec"
    }


def test_read_line_server_consistent_contract_field_rejects_response_drift(
    monkeypatch,
) -> None:
    class Completed:
        stdout = (
            '{"count_proof_contract":{"name":"prime_horizon_range_count_spec"}}\n'
            '{"count_proof_contract":{"name":"wrong"}}\n'
        )

    def fake_run(command, **kwargs):
        return Completed()

    monkeypatch.setattr("scripts.check_prime_proof_contract.subprocess.run", fake_run)

    with pytest.raises(AssertionError, match="changed between line-server responses"):
        read_line_server_consistent_contract_field(
            ["circle-prime-count", "count-server", "--json"],
            "shifted 2 100 1000000000000 1000000010000\nquit\n",
            "count_proof_contract",
        )
