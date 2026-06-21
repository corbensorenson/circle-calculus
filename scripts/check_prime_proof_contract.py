from __future__ import annotations

import argparse
import json
import re
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
EXPECTED_NEXT_CONTRACT_NAME = "prime_horizon_next_search_spec"
EXPECTED_NEXT_THEOREM_IDS = ["CC-T0080", "CC-T0081"]


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
        "--count-binary",
        type=Path,
        default=ROOT / "target" / "debug" / binary_name("circle-prime-count"),
        help="Path to a built circle-prime-count binary.",
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
    lean_sources = LeanSourceIndex(ROOT)
    contracts = collect_cli_contracts(args.binary)
    reference = contracts[0]
    for label, contract in contracts:
        compare_contracts(reference[1], contract, label)
        check_contract_against_manifest(contract, manifest, label, lean_sources)
    count_contracts = collect_count_contracts(args.binary)
    if args.count_binary.exists():
        count_contracts.extend(collect_count_binary_contracts(args.count_binary))
    for label, contract in count_contracts:
        check_count_contract_against_manifest(contract, manifest, label, lean_sources)
    next_contracts = collect_next_contracts(args.binary)
    for label, contract in next_contracts:
        check_next_contract_against_manifest(contract, manifest, label, lean_sources)
    print(
        "prime proof contract ok: "
        + ", ".join(f"{label}={contract['name']}" for label, contract in contracts)
        + "; count proof contract ok: "
        + ", ".join(f"{label}={contract['name']}" for label, contract in count_contracts)
        + "; next proof contract ok: "
        + ", ".join(f"{label}={contract['name']}" for label, contract in next_contracts)
    )
    return 0


def binary_name(name: str) -> str:
    return f"{name}.exe" if sys.platform == "win32" else name


def load_theorem_manifest(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text()) or {}
    return {item["id"]: item for item in data.get("theorems", [])}


class LeanSourceIndex:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._module_cache: dict[str, str] = {}

    def assert_declaration_exists(self, module: str, lean_name: str, label: str) -> None:
        source = self._source_for_module(module)
        declaration = lean_name.rsplit(".", 1)[-1]
        pattern = re.compile(
            rf"^\s*(?:noncomputable\s+)?(?:theorem|lemma|def|abbrev|instance)\s+"
            rf"{re.escape(declaration)}\b",
            re.MULTILINE,
        )
        if pattern.search(source) is None:
            path = self.module_path(module)
            raise AssertionError(
                f"{label} Lean declaration missing from {path}: {lean_name}"
            )

    def _source_for_module(self, module: str) -> str:
        if module not in self._module_cache:
            path = self.module_path(module)
            self._module_cache[module] = path.read_text()
        return self._module_cache[module]

    def module_path(self, module: str) -> Path:
        path = self.root / Path(*module.split(".")).with_suffix(".lean")
        if not path.exists():
            raise AssertionError(f"Lean module file missing for {module}: {path}")
        return path


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
    contracts = [(label, read_contract(command)) for label, command in probes]
    contracts.append(
        (
            "next_server",
            read_line_server_contract_field(
                [str(binary), "next-server", "--json"],
                "100\nquit\n",
                "proof_contract",
            ),
        )
    )
    contracts.append(
        (
            "count_server",
            read_line_server_contract_field(
                [
                    str(binary),
                    "count-server",
                    "--segment-size",
                    "65536",
                    "--threads",
                    "4",
                    "--count-mode",
                    "presieve13",
                    "--json",
                ],
                "0 1000\nquit\n",
                "proof_contract",
            ),
        )
    )
    return contracts


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
    contracts = [
        (label, read_contract_field(command, "count_proof_contract"))
        for label, command in probes
    ]
    contracts.append(
        (
            "count_server",
            read_line_server_contract_field(
                [
                    str(binary),
                    "count-server",
                    "--segment-size",
                    "65536",
                    "--threads",
                    "4",
                    "--count-mode",
                    "presieve13",
                    "--json",
                ],
                "0 1000\nquit\n",
                "count_proof_contract",
            ),
        )
    )
    return contracts


def collect_count_binary_contracts(binary: Path) -> list[tuple[str, dict[str, Any]]]:
    return [
        (
            "count_binary",
            read_contract_field(
                [str(binary), "0", "1000", "--json"],
                "count_proof_contract",
            ),
        ),
        (
            "count_binary_server",
            read_line_server_contract_field(
                [str(binary), "count-server", "--json"],
                "0 1000\nquit\n",
                "count_proof_contract",
            ),
        ),
        (
            "count_binary_shifted_server",
            read_line_server_consistent_contract_field(
                [str(binary), "count-server", "--json", "--threads", "8"],
                "shifted 2 10000000 1000000000000 1000010000000\nquit\n",
                "count_proof_contract",
            ),
        ),
    ]


def collect_next_contracts(binary: Path) -> list[tuple[str, dict[str, Any]]]:
    contracts = [
        (
            "next_found",
            read_contract_field(
                [str(binary), "next", "100", "--json"],
                "next_proof_contract",
            ),
        ),
        (
            "next_not_found",
            read_contract_field(
                [str(binary), "next", "18446744073709551558", "--json"],
                "next_proof_contract",
            ),
        ),
    ]
    contracts.append(
        (
            "next_server",
            read_line_server_contract_field(
                [str(binary), "next-server", "--json"],
                "100\nquit\n",
                "next_proof_contract",
            ),
        )
    )
    return contracts


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


def read_line_server_contract_field(
    command: list[str],
    request: str,
    field: str,
) -> dict[str, Any]:
    return read_line_server_contract_fields(command, request, field)[0]


def read_line_server_consistent_contract_field(
    command: list[str],
    request: str,
    field: str,
) -> dict[str, Any]:
    contracts = read_line_server_contract_fields(command, request, field)
    reference = contracts[0]
    for index, contract in enumerate(contracts[1:], start=2):
        if contract != reference:
            raise AssertionError(
                f"{field} changed between line-server responses: "
                f"response 1={reference}, response {index}={contract}"
            )
    return reference


def read_line_server_contract_fields(
    command: list[str],
    request: str,
    field: str,
) -> list[dict[str, Any]]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        input=request,
        check=True,
        text=True,
        capture_output=True,
    )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise AssertionError(f"no JSON output from {' '.join(command)}")
    contracts = []
    for index, line in enumerate(lines, start=1):
        payload = json.loads(line)
        contract = payload.get(field)
        if not isinstance(contract, dict):
            raise AssertionError(
                f"missing {field} in output line {index} from {' '.join(command)}"
            )
        contracts.append(contract)
    return contracts


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
    lean_sources: LeanSourceIndex | None = None,
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
        if lean_sources is not None:
            lean_sources.assert_declaration_exists(
                contract["lean_module"],
                str(lean_name),
                label,
            )


def check_count_contract_against_manifest(
    contract: dict[str, Any],
    manifest_by_id: dict[str, dict[str, Any]],
    label: str,
    lean_sources: LeanSourceIndex | None = None,
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
        if lean_sources is not None:
            lean_sources.assert_declaration_exists(
                contract["lean_module"],
                str(lean_name),
                label,
            )


def check_next_contract_against_manifest(
    contract: dict[str, Any],
    manifest_by_id: dict[str, dict[str, Any]],
    label: str,
    lean_sources: LeanSourceIndex | None = None,
) -> None:
    if contract.get("name") != EXPECTED_NEXT_CONTRACT_NAME:
        raise AssertionError(
            f"{label} next_proof_contract name changed: {contract.get('name')}"
        )
    if contract.get("lean_module") != EXPECTED_LEAN_MODULE:
        raise AssertionError(
            f"{label} next_proof_contract lean_module changed: {contract.get('lean_module')}"
        )
    if contract.get("rust_domain") != EXPECTED_RUST_DOMAIN:
        raise AssertionError(
            f"{label} next_proof_contract rust_domain changed: {contract.get('rust_domain')}"
        )

    theorem_ids = contract.get("theorem_ids")
    if theorem_ids != EXPECTED_NEXT_THEOREM_IDS:
        raise AssertionError(
            f"{label} next_proof_contract theorem_ids changed: {theorem_ids}; "
            f"expected {EXPECTED_NEXT_THEOREM_IDS}"
        )

    lean_names = contract.get("lean_names")
    if not isinstance(lean_names, list):
        raise AssertionError(f"{label} next_proof_contract lean_names must be a list")
    if len(lean_names) != len(EXPECTED_NEXT_THEOREM_IDS):
        raise AssertionError(
            f"{label} next_proof_contract lean_names length {len(lean_names)} does not "
            f"match theorem_ids length {len(EXPECTED_NEXT_THEOREM_IDS)}"
        )

    for theorem_id, lean_name in zip(EXPECTED_NEXT_THEOREM_IDS, lean_names):
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
        if lean_sources is not None:
            lean_sources.assert_declaration_exists(
                contract["lean_module"],
                str(lean_name),
                label,
            )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime proof contract check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
