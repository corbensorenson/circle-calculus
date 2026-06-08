from __future__ import annotations

import shlex
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
    "verification_recipe",
    "living_book_presentation",
    "claim_boundary",
}

EVIDENCE_COUNT_KEYS = [
    "paper_count",
    "theorem_count",
    "dictionary_count",
    "executable_count",
    "source_count",
    "living_book_page_count",
    "living_book_widget_count",
]


def capability_living_book_sets(capability: dict) -> tuple[set[str], set[str]]:
    pages: set[str] = set()
    widgets: set[str] = set()
    for ref in capability.get("living_book_refs", []) or []:
        if not isinstance(ref, dict):
            continue
        page = ref.get("page", "")
        if page:
            pages.add(page)
        for widget_id in ref.get("widget_ids", []) or []:
            if widget_id:
                widgets.add(widget_id)
    return pages, widgets


def expected_evidence_counts(capability: dict) -> dict[str, int]:
    living_pages, living_widgets = capability_living_book_sets(capability)
    return {
        "paper_count": len(capability.get("paper_ids", []) or []),
        "theorem_count": len(capability.get("theorem_ids", []) or []),
        "dictionary_count": len(capability.get("dictionary_ids", []) or []),
        "executable_count": len(capability.get("executable_refs", []) or []),
        "source_count": len(capability.get("source_refs", []) or []),
        "living_book_page_count": len(living_pages),
        "living_book_widget_count": len(living_widgets),
    }


def portfolio_backing_contract_summary(capabilities: list[dict]) -> dict:
    theorem_refs = {
        "proved_and_paper_backed_count": 0,
        "total_count": 0,
        "unproved_or_unbacked_refs": [],
    }
    source_refs = {
        "backed_count": 0,
        "total_count": 0,
        "unbacked_refs": [],
    }
    living_book_refs = {
        "backed_page_count": 0,
        "total_page_count": 0,
        "backed_widget_count": 0,
        "total_widget_count": 0,
        "unbacked_pages": [],
        "unbacked_widgets": [],
    }
    for capability in capabilities:
        capability_id = capability.get("id", "<missing id>")
        theorem_contract = capability.get("theorem_ref_contract", {}) or {}
        source_contract = capability.get("source_ref_contract", {}) or {}
        living_contract = capability.get("living_book_ref_contract", {}) or {}

        theorem_refs["proved_and_paper_backed_count"] += theorem_contract.get(
            "proved_and_paper_backed_count", 0
        )
        theorem_refs["total_count"] += theorem_contract.get("total_count", 0)
        theorem_refs["unproved_or_unbacked_refs"].extend(
            f"{capability_id}#{theorem_id}"
            for theorem_id in theorem_contract.get("unproved_or_unbacked_ids", []) or []
        )

        source_refs["backed_count"] += source_contract.get("backed_count", 0)
        source_refs["total_count"] += source_contract.get("total_count", 0)
        source_refs["unbacked_refs"].extend(
            f"{capability_id}#{ref}"
            for ref in source_contract.get("unbacked_refs", []) or []
        )

        living_book_refs["backed_page_count"] += living_contract.get(
            "backed_page_count", 0
        )
        living_book_refs["total_page_count"] += living_contract.get(
            "total_page_count", 0
        )
        living_book_refs["backed_widget_count"] += living_contract.get(
            "backed_widget_count", 0
        )
        living_book_refs["total_widget_count"] += living_contract.get(
            "total_widget_count", 0
        )
        living_book_refs["unbacked_pages"].extend(
            f"{capability_id}#{page}"
            for page in living_contract.get("unbacked_pages", []) or []
        )
        living_book_refs["unbacked_widgets"].extend(
            f"{capability_id}#{widget}"
            for widget in living_contract.get("unbacked_widgets", []) or []
        )

    theorem_ready = (
        theorem_refs["proved_and_paper_backed_count"] == theorem_refs["total_count"]
        and not theorem_refs["unproved_or_unbacked_refs"]
    )
    source_ready = (
        source_refs["backed_count"] == source_refs["total_count"]
        and not source_refs["unbacked_refs"]
    )
    living_ready = (
        living_book_refs["backed_page_count"] == living_book_refs["total_page_count"]
        and living_book_refs["backed_widget_count"] == living_book_refs["total_widget_count"]
        and not living_book_refs["unbacked_pages"]
        and not living_book_refs["unbacked_widgets"]
    )
    return {
        "ready_to_advertise": theorem_ready and source_ready and living_ready,
        "theorem_refs": theorem_refs,
        "source_refs": source_refs,
        "living_book_refs": living_book_refs,
    }


def expected_portfolio_summary(
    capabilities: list[dict],
    ready_count: int,
    gate_failure_counts: dict[str, int],
) -> dict:
    role_counts: dict[str, int] = {}
    proof_provenance_counts: dict[str, int] = {}
    evidence_totals = {key: 0 for key in EVIDENCE_COUNT_KEYS}
    unique_papers: set[str] = set()
    unique_theorems: set[str] = set()
    unique_dictionary_ids: set[str] = set()
    unique_executables: set[str] = set()
    unique_sources: set[str] = set()
    unique_living_pages: set[str] = set()
    unique_living_widgets: set[str] = set()

    for capability in capabilities:
        for role in capability.get("portfolio_roles", []) or []:
            role_counts[role] = role_counts.get(role, 0) + 1
        proof_provenance_kind = capability.get("proof_provenance_kind", "")
        if proof_provenance_kind:
            proof_provenance_counts[proof_provenance_kind] = (
                proof_provenance_counts.get(proof_provenance_kind, 0) + 1
            )

        counts = expected_evidence_counts(capability)
        for key, value in counts.items():
            evidence_totals[key] += value
        living_pages, living_widgets = capability_living_book_sets(capability)
        unique_papers.update(capability.get("paper_ids", []) or [])
        unique_theorems.update(capability.get("theorem_ids", []) or [])
        unique_dictionary_ids.update(capability.get("dictionary_ids", []) or [])
        unique_executables.update(capability.get("executable_refs", []) or [])
        unique_sources.update(capability.get("source_refs", []) or [])
        unique_living_pages.update(living_pages)
        unique_living_widgets.update(living_widgets)

    return {
        "capability_count": len(capabilities),
        "role_counts": dict(sorted(role_counts.items())),
        "proof_provenance_counts": dict(sorted(proof_provenance_counts.items())),
        "evidence_totals": evidence_totals,
        "unique_evidence_counts": {
            "paper_count": len(unique_papers),
            "theorem_count": len(unique_theorems),
            "dictionary_count": len(unique_dictionary_ids),
            "executable_count": len(unique_executables),
            "source_count": len(unique_sources),
            "living_book_page_count": len(unique_living_pages),
            "living_book_widget_count": len(unique_living_widgets),
        },
        "unique_living_book_pages": sorted(unique_living_pages),
        "claim_contract_summary": {
            "ready_count": ready_count,
            "incomplete_count": len(capabilities) - ready_count,
            "gate_failure_counts": dict(sorted(gate_failure_counts.items())),
        },
        "backing_contract_summary": portfolio_backing_contract_summary(capabilities),
    }


def main() -> int:
    failures: list[str] = []
    data = load_json(GENERATED / "capability_showcase.json")
    capabilities = data.get("capabilities", [])
    portfolio_summary = data.get("portfolio_summary", {})
    summary = portfolio_summary.get("claim_contract_summary", {})

    ready_count = 0
    gate_failure_counts: dict[str, int] = {}
    for capability in capabilities:
        capability_id = capability.get("id", "<missing id>")
        executable_refs = capability.get("executable_refs", []) or []
        evidence_counts = capability.get("evidence_counts", {}) or {}
        expected_counts = expected_evidence_counts(capability)
        if evidence_counts != expected_counts:
            failures.append(
                f"{capability_id}: evidence_counts {evidence_counts} "
                f"do not match refs {expected_counts}"
            )
        expected_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
        recipe = capability.get("verification_recipe")
        if not isinstance(recipe, dict):
            failures.append(f"{capability_id}: missing verification_recipe")
        else:
            expected_recipe = {
                "lean_command": "lake build",
                "pytest_command": expected_pytest_command,
                "capability_contract_command": (
                    "python scripts/check_capability_showcase.py && "
                    "python scripts/site/check_capability_contracts.py"
                ),
                "site_command": "make sitecheck",
            }
            for key, expected_value in expected_recipe.items():
                if recipe.get(key) != expected_value:
                    failures.append(
                        f"{capability_id}: verification_recipe {key} "
                        f"{recipe.get(key)!r} does not match {expected_value!r}"
                    )
        theorem_ref_contract = capability.get("theorem_ref_contract")
        theorem_ids = capability.get("theorem_ids", []) or []
        if not isinstance(theorem_ref_contract, dict):
            failures.append(f"{capability_id}: missing theorem_ref_contract")
        else:
            theorem_refs = theorem_ref_contract.get("refs")
            if not isinstance(theorem_refs, list):
                failures.append(f"{capability_id}: theorem_ref_contract refs must be a list")
                theorem_refs = []
            contract_theorem_ids = [
                ref.get("id") for ref in theorem_refs if isinstance(ref, dict)
            ]
            if contract_theorem_ids != theorem_ids:
                failures.append(
                    f"{capability_id}: theorem_ref_contract refs do not match theorem_ids"
                )
            proved_and_paper_backed_count = sum(
                1
                for ref in theorem_refs
                if (
                    isinstance(ref, dict)
                    and ref.get("proved")
                    and ref.get("paper_backed")
                )
            )
            unproved_or_unbacked_ids = [
                ref.get("id", "")
                for ref in theorem_refs
                if not (
                    isinstance(ref, dict)
                    and ref.get("proved")
                    and ref.get("paper_backed")
                )
            ]
            if theorem_ref_contract.get("proved_and_paper_backed_count") != proved_and_paper_backed_count:
                failures.append(
                    f"{capability_id}: theorem_ref_contract "
                    "proved_and_paper_backed_count "
                    f"{theorem_ref_contract.get('proved_and_paper_backed_count')} "
                    f"does not match {proved_and_paper_backed_count}"
                )
            if theorem_ref_contract.get("total_count") != len(theorem_ids):
                failures.append(
                    f"{capability_id}: theorem_ref_contract total_count "
                    f"{theorem_ref_contract.get('total_count')} does not match {len(theorem_ids)}"
                )
            if theorem_ref_contract.get("unproved_or_unbacked_ids") != unproved_or_unbacked_ids:
                failures.append(
                    f"{capability_id}: theorem_ref_contract "
                    "unproved_or_unbacked_ids do not match refs"
                )
            for ref in theorem_refs:
                if not isinstance(ref, dict):
                    failures.append(
                        f"{capability_id}: theorem_ref_contract ref must be a mapping"
                    )
                    continue
                theorem_id = ref.get("id", "<missing theorem id>")
                if ref.get("canonical_status") != "proved":
                    failures.append(
                        f"{capability_id}: theorem {theorem_id} is not canonically proved"
                    )
                if not ref.get("lean_name"):
                    failures.append(
                        f"{capability_id}: theorem {theorem_id} missing Lean name"
                    )
                if not ref.get("carried_by_papers"):
                    failures.append(
                        f"{capability_id}: theorem {theorem_id} is not carried by cited papers"
                    )
            if unproved_or_unbacked_ids:
                failures.append(
                    f"{capability_id}: theorem ids are not proved and paper-backed: "
                    f"{unproved_or_unbacked_ids}"
                )
        source_ref_contract = capability.get("source_ref_contract")
        source_refs = capability.get("source_refs", []) or []
        if not isinstance(source_ref_contract, dict):
            failures.append(f"{capability_id}: missing source_ref_contract")
        else:
            refs = source_ref_contract.get("refs")
            if not isinstance(refs, list):
                failures.append(f"{capability_id}: source_ref_contract refs must be a list")
                refs = []
            contract_refs = [ref.get("ref") for ref in refs if isinstance(ref, dict)]
            if contract_refs != source_refs:
                failures.append(
                    f"{capability_id}: source_ref_contract refs do not match source_refs"
                )
            backed_count = sum(
                1
                for ref in refs
                if isinstance(ref, dict) and ref.get("backed")
            )
            unbacked_refs = [
                ref.get("ref", "")
                for ref in refs
                if isinstance(ref, dict) and not ref.get("backed")
            ]
            if source_ref_contract.get("backed_count") != backed_count:
                failures.append(
                    f"{capability_id}: source_ref_contract backed_count "
                    f"{source_ref_contract.get('backed_count')} does not match {backed_count}"
                )
            if source_ref_contract.get("total_count") != len(source_refs):
                failures.append(
                    f"{capability_id}: source_ref_contract total_count "
                    f"{source_ref_contract.get('total_count')} does not match {len(source_refs)}"
                )
            if source_ref_contract.get("unbacked_refs") != unbacked_refs:
                failures.append(
                    f"{capability_id}: source_ref_contract unbacked_refs do not match refs"
                )
            if unbacked_refs:
                failures.append(
                    f"{capability_id}: source refs are not paper-backed: {unbacked_refs}"
                )
        living_book_ref_contract = capability.get("living_book_ref_contract")
        living_book_refs = capability.get("living_book_refs", []) or []
        expected_pages = [
            ref.get("page", "")
            for ref in living_book_refs
            if isinstance(ref, dict)
        ]
        expected_widget_count = len(
            {
                widget_id
                for ref in living_book_refs
                if isinstance(ref, dict)
                for widget_id in (ref.get("widget_ids", []) or [])
            }
        )
        if not isinstance(living_book_ref_contract, dict):
            failures.append(f"{capability_id}: missing living_book_ref_contract")
        else:
            pages = living_book_ref_contract.get("pages")
            if not isinstance(pages, list):
                failures.append(
                    f"{capability_id}: living_book_ref_contract pages must be a list"
                )
                pages = []
            contract_pages = [
                page.get("page") for page in pages if isinstance(page, dict)
            ]
            if contract_pages != expected_pages:
                failures.append(
                    f"{capability_id}: living_book_ref_contract pages do not match living_book_refs"
                )
            backed_page_count = sum(
                1 for page in pages if isinstance(page, dict) and page.get("backed")
            )
            backed_widget_count = len(
                {
                    widget.get("id")
                    for page in pages
                    if isinstance(page, dict)
                    for widget in page.get("widgets", []) or []
                    if isinstance(widget, dict) and widget.get("backed")
                }
            )
            total_widget_count = len(
                {
                    widget.get("id")
                    for page in pages
                    if isinstance(page, dict)
                    for widget in page.get("widgets", []) or []
                    if isinstance(widget, dict)
                }
            )
            unbacked_pages = [
                page.get("page", "")
                for page in pages
                if isinstance(page, dict) and not page.get("backed")
            ]
            unbacked_widgets = [
                f"{page.get('page', '')}#{widget.get('id', '')}"
                for page in pages
                if isinstance(page, dict)
                for widget in page.get("widgets", []) or []
                if isinstance(widget, dict) and not widget.get("backed")
            ]
            if living_book_ref_contract.get("backed_page_count") != backed_page_count:
                failures.append(
                    f"{capability_id}: living_book_ref_contract backed_page_count "
                    f"{living_book_ref_contract.get('backed_page_count')} "
                    f"does not match {backed_page_count}"
                )
            if living_book_ref_contract.get("total_page_count") != len(expected_pages):
                failures.append(
                    f"{capability_id}: living_book_ref_contract total_page_count "
                    f"{living_book_ref_contract.get('total_page_count')} "
                    f"does not match {len(expected_pages)}"
                )
            if living_book_ref_contract.get("backed_widget_count") != backed_widget_count:
                failures.append(
                    f"{capability_id}: living_book_ref_contract backed_widget_count "
                    f"{living_book_ref_contract.get('backed_widget_count')} "
                    f"does not match {backed_widget_count}"
                )
            if total_widget_count != expected_widget_count:
                failures.append(
                    f"{capability_id}: living_book_ref_contract widget ids "
                    f"do not match living_book_refs"
                )
            if living_book_ref_contract.get("total_widget_count") != expected_widget_count:
                failures.append(
                    f"{capability_id}: living_book_ref_contract total_widget_count "
                    f"{living_book_ref_contract.get('total_widget_count')} "
                    f"does not match {expected_widget_count}"
                )
            if living_book_ref_contract.get("unbacked_pages") != unbacked_pages:
                failures.append(
                    f"{capability_id}: living_book_ref_contract unbacked_pages do not match pages"
                )
            if living_book_ref_contract.get("unbacked_widgets") != unbacked_widgets:
                failures.append(
                    f"{capability_id}: living_book_ref_contract unbacked_widgets do not match widgets"
                )
            if backed_page_count != evidence_counts.get("living_book_page_count"):
                failures.append(
                    f"{capability_id}: Living Book backed_page_count does not match evidence count"
                )
            if backed_widget_count != evidence_counts.get("living_book_widget_count"):
                failures.append(
                    f"{capability_id}: Living Book backed_widget_count does not match evidence count"
                )
            if unbacked_pages or unbacked_widgets:
                failures.append(
                    f"{capability_id}: Living Book refs are not backed: "
                    f"{unbacked_pages + unbacked_widgets}"
                )
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
    expected_summary = expected_portfolio_summary(
        capabilities,
        ready_count,
        gate_failure_counts,
    )
    for key, expected_value in expected_summary.items():
        if portfolio_summary.get(key) != expected_value:
            failures.append(f"portfolio_summary {key} does not match generated data")

    if failures:
        print("capability contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"capability contracts ok: {len(capabilities)} ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
