from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTRACT_NAME = "prime_horizon_sqrt_containment"
EXPECTED_LEAN_MODULE = "Circle.Core.Horizon"
EXPECTED_RUST_DOMAIN = "u64_exact_arithmetic"
EXPECTED_THEOREM_IDS = ["CC-T0073", "CC-T0074", "CC-T0075", "CC-T0076", "CC-T0077"]
EXPECTED_COUNT_CONTRACT_NAME = "prime_horizon_range_count_spec"
EXPECTED_COUNT_THEOREM_IDS = ["CC-T0078", "CC-T0079"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Circle prime-engine JSON proof_contract metadata."
    )
    parser.add_argument(
        "--binary",
        type=Path,
        default=ROOT / "target" / "debug" / binary_name("circle-prime"),
        help="Path to a built circle-prime binary.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "manifests" / "theorem_manifest.yaml",
    )
    args = parser.parse_args()

    if not args.binary.exists():
        raise FileNotFoundError(f"circle-prime binary not found: {args.binary}")
    manifest = load_theorem_manifest(args.manifest)
    contracts = collect_cli_contracts(args.binary)
    reference = contracts[0]
    for label, contract in contracts:
        compare_contracts(reference[1], contract, label)
        check_contract_against_manifest(contract, manifest, label)
    count_contracts = collect_count_contracts(args.binary)
    for label, contract in count_contracts:
        check_count_contract_against_manifest(contract, manifest, label)
    print(
        "prime proof contract ok: "
        + ", ".join(f"{label}={contract['name']}" for label, contract in contracts)
        + "; count proof contract ok: "
        + ", ".join(f"{label}={contract['name']}" for label, contract in count_contracts)
    )
    return 0


def binary_name(name: str) -> str:
    return f"{name}.exe" if sys.platform == "win32" else name


def load_theorem_manifest(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text()) or {}
    return {item["id"]: item for item in data.get("theorems", [])}


def collect_cli_contracts(binary: Path) -> list[tuple[str, dict[str, Any]]]:
    probes = [
        ("test", [str(binary), "test", "97", "--json"]),
        ("next", [str(binary), "next", "100", "--json"]),
        ("range_count", [str(binary), "range", "0", "1000", "--count", "--json"]),
        ("range_enum", [str(binary), "range", "0", "30", "--json"]),
        (
            "recommend_count",
            [str(binary), "recommend", "0", "1000", "--count", "--json", "--threads", "4"],
        ),
        ("inspect", [str(binary), "inspect", "16", "--json"]),
    ]
    return [(label, read_contract(command)) for label, command in probes]


def read_contract(command: list[str]) -> dict[str, Any]:
    return read_contract_field(command, "proof_contract")


def collect_count_contracts(binary: Path) -> list[tuple[str, dict[str, Any]]]:
    probes = [
        ("range_count", [str(binary), "range", "0", "1000", "--count", "--json"]),
        (
            "recommend_count",
            [str(binary), "recommend", "0", "1000", "--count", "--json", "--threads", "4"],
        ),
    ]
    return [(label, read_contract_field(command, "count_proof_contract")) for label, command in probes]


def read_contract_field(command: list[str], field: str) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(completed.stdout)
    contract = payload.get(field)
    if not isinstance(contract, dict):
        raise AssertionError(f"missing {field} in output from {' '.join(command)}")
    return contract


def compare_contracts(
    expected: dict[str, Any],
    actual: dict[str, Any],
    label: str,
) -> None:
    if actual != expected:
        raise AssertionError(
            f"{label} proof_contract differs from reference: "
            f"expected={expected}, actual={actual}"
        )


def check_contract_against_manifest(
    contract: dict[str, Any],
    manifest_by_id: dict[str, dict[str, Any]],
    label: str,
) -> None:
    if contract.get("name") != EXPECTED_CONTRACT_NAME:
        raise AssertionError(f"{label} proof_contract name changed: {contract.get('name')}")
    if contract.get("lean_module") != EXPECTED_LEAN_MODULE:
        raise AssertionError(
            f"{label} proof_contract lean_module changed: {contract.get('lean_module')}"
        )
    if contract.get("rust_domain") != EXPECTED_RUST_DOMAIN:
        raise AssertionError(
            f"{label} proof_contract rust_domain changed: {contract.get('rust_domain')}"
        )

    theorem_ids = contract.get("theorem_ids")
    if theorem_ids != EXPECTED_THEOREM_IDS:
        raise AssertionError(
            f"{label} proof_contract theorem_ids changed: {theorem_ids}; "
            f"expected {EXPECTED_THEOREM_IDS}"
        )

    lean_names = contract.get("lean_names")
    if not isinstance(lean_names, list):
        raise AssertionError(f"{label} proof_contract lean_names must be a list")
    if len(lean_names) != len(EXPECTED_THEOREM_IDS):
        raise AssertionError(
            f"{label} proof_contract lean_names length {len(lean_names)} does not "
            f"match theorem_ids length {len(EXPECTED_THEOREM_IDS)}"
        )

    for theorem_id, lean_name in zip(EXPECTED_THEOREM_IDS, lean_names):
        theorem = manifest_by_id.get(theorem_id)
        if theorem is None:
            raise AssertionError(f"{label} theorem id missing from manifest: {theorem_id}")
        if theorem.get("status") != "proved":
            raise AssertionError(
                f"{label} theorem {theorem_id} is not proved: {theorem.get('status')}"
            )
        if theorem.get("lean_name") != lean_name:
            raise AssertionError(
                f"{label} theorem {theorem_id} lean_name mismatch: "
                f"contract={lean_name}, manifest={theorem.get('lean_name')}"
            )


def check_count_contract_against_manifest(
    contract: dict[str, Any],
    manifest_by_id: dict[str, dict[str, Any]],
    label: str,
) -> None:
    if contract.get("name") != EXPECTED_COUNT_CONTRACT_NAME:
        raise AssertionError(
            f"{label} count_proof_contract name changed: {contract.get('name')}"
        )
    if contract.get("lean_module") != EXPECTED_LEAN_MODULE:
        raise AssertionError(
            f"{label} count_proof_contract lean_module changed: {contract.get('lean_module')}"
        )
    if contract.get("rust_domain") != EXPECTED_RUST_DOMAIN:
        raise AssertionError(
            f"{label} count_proof_contract rust_domain changed: {contract.get('rust_domain')}"
        )

    theorem_ids = contract.get("theorem_ids")
    if theorem_ids != EXPECTED_COUNT_THEOREM_IDS:
        raise AssertionError(
            f"{label} count_proof_contract theorem_ids changed: {theorem_ids}; "
            f"expected {EXPECTED_COUNT_THEOREM_IDS}"
        )

    lean_names = contract.get("lean_names")
    if not isinstance(lean_names, list):
        raise AssertionError(f"{label} count_proof_contract lean_names must be a list")
    if len(lean_names) != len(EXPECTED_COUNT_THEOREM_IDS):
        raise AssertionError(
            f"{label} count_proof_contract lean_names length {len(lean_names)} does not "
            f"match theorem_ids length {len(EXPECTED_COUNT_THEOREM_IDS)}"
        )

    for theorem_id, lean_name in zip(EXPECTED_COUNT_THEOREM_IDS, lean_names):
        theorem = manifest_by_id.get(theorem_id)
        if theorem is None:
            raise AssertionError(f"{label} theorem id missing from manifest: {theorem_id}")
        if theorem.get("status") != "proved":
            raise AssertionError(
                f"{label} theorem {theorem_id} is not proved: {theorem.get('status')}"
            )
        if theorem.get("lean_name") != lean_name:
            raise AssertionError(
                f"{label} theorem {theorem_id} lean_name mismatch: "
                f"contract={lean_name}, manifest={theorem.get('lean_name')}"
            )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime proof contract check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
