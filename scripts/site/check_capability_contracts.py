from __future__ import annotations

import sys

from site_lib import GENERATED, load_json


REQUIRED_GATE_IDS = {
    "role_contract",
    "standard_anchor",
    "circle_expression",
    "circle_native_value",
    "advertised_claim",
    "proof_scope",
    "proof_provenance_kind",
    "proof_provenance",
    "paper_backing",
    "proved_theorem_ids",
    "dictionary_backing",
    "source_trail",
    "executable_reference",
    "living_book_presentation",
    "claim_boundary",
}


def main() -> int:
    failures: list[str] = []
    data = load_json(GENERATED / "capability_showcase.json")
    capabilities = data.get("capabilities", [])
    summary = data.get("portfolio_summary", {}).get("claim_contract_summary", {})

    ready_count = 0
    gate_failure_counts: dict[str, int] = {}
    for capability in capabilities:
        capability_id = capability.get("id", "<missing id>")
        contract = capability.get("claim_contract")
        if not isinstance(contract, dict):
            failures.append(f"{capability_id}: missing claim_contract")
            continue

        gates = contract.get("gates", [])
        if not isinstance(gates, list) or not gates:
            failures.append(f"{capability_id}: claim_contract has no gates")
            continue
        gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
        duplicate_gate_ids = sorted(
            {gate_id for gate_id in gate_ids if gate_id and gate_ids.count(gate_id) > 1}
        )
        if duplicate_gate_ids:
            failures.append(
                f"{capability_id}: duplicate claim-contract gates {duplicate_gate_ids}"
            )
        missing_gate_ids = sorted(REQUIRED_GATE_IDS - set(gate_ids))
        unknown_gate_ids = sorted(set(gate_ids) - REQUIRED_GATE_IDS)
        if missing_gate_ids:
            failures.append(f"{capability_id}: missing claim-contract gates {missing_gate_ids}")
        if unknown_gate_ids:
            failures.append(f"{capability_id}: unknown claim-contract gates {unknown_gate_ids}")

        passed_count = 0
        for gate in gates:
            if not isinstance(gate, dict):
                failures.append(f"{capability_id}: claim-contract gate must be a mapping")
                continue
            gate_id = gate.get("id", "<missing gate id>")
            if not gate.get("label"):
                failures.append(f"{capability_id}: gate {gate_id} missing label")
            if "passed" not in gate:
                failures.append(f"{capability_id}: gate {gate_id} missing passed flag")
            elif gate["passed"]:
                passed_count += 1
            else:
                gate_failure_counts[gate_id] = gate_failure_counts.get(gate_id, 0) + 1
            if "evidence" not in gate:
                failures.append(f"{capability_id}: gate {gate_id} missing evidence")

        expected_ready = passed_count == len(gates)
        if contract.get("passed_gate_count") != passed_count:
            failures.append(
                f"{capability_id}: passed_gate_count {contract.get('passed_gate_count')} "
                f"does not match {passed_count}"
            )
        if contract.get("total_gate_count") != len(gates):
            failures.append(
                f"{capability_id}: total_gate_count {contract.get('total_gate_count')} "
                f"does not match {len(gates)}"
            )
        if bool(contract.get("ready_to_advertise")) != expected_ready:
            failures.append(f"{capability_id}: ready_to_advertise does not match gates")
        expected_status = "ready" if expected_ready else "incomplete"
        if contract.get("status") != expected_status:
            failures.append(
                f"{capability_id}: contract status {contract.get('status')} "
                f"does not match {expected_status}"
            )
        if not expected_ready:
            failures.append(f"{capability_id}: claim contract is incomplete")
        else:
            ready_count += 1

    expected_incomplete = len(capabilities) - ready_count
    if summary.get("ready_count") != ready_count:
        failures.append(
            f"claim contract summary ready_count {summary.get('ready_count')} "
            f"does not match {ready_count}"
        )
    if summary.get("incomplete_count") != expected_incomplete:
        failures.append(
            "claim contract summary incomplete_count "
            f"{summary.get('incomplete_count')} does not match {expected_incomplete}"
        )
    if summary.get("gate_failure_counts", {}) != dict(sorted(gate_failure_counts.items())):
        failures.append("claim contract summary gate_failure_counts do not match gates")

    if failures:
        print("capability contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"capability contracts ok: {len(capabilities)} ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
