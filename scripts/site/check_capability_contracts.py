from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

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
    "claim_language_guardrail",
    "value_proposition",
    "proof_trail",
    "review_packet",
    "parity_value_comparison",
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

REQUIRED_ROUTE_FIELDS = [
    "id",
    "title",
    "audience",
    "route_claim",
    "not_claimed",
]

CLAIM_LANGUAGE_PATTERNS = [
    ("open_problem_solution", re.compile(r"\bsolv(?:e|es|ed|ing)\b", re.IGNORECASE)),
    ("new_proof", re.compile(r"\bnew proof\b", re.IGNORECASE)),
    ("open_problem_progress", re.compile(r"\bprogress on (?:an? )?open\b", re.IGNORECASE)),
    ("improved_bounds", re.compile(r"\bimprov(?:e|es|ed|ing|ement)\s+bounds?\b", re.IGNORECASE)),
    ("universal_compression", re.compile(r"\buniversal compression\b", re.IGNORECASE)),
    ("model_quality_improvement", re.compile(r"\bmodel-quality improvement\b", re.IGNORECASE)),
    ("context_length_improvement", re.compile(r"\bcontext-length improvement\b", re.IGNORECASE)),
    ("speedup_claim", re.compile(r"\bspeedup\b|\bfaster\b", re.IGNORECASE)),
    ("physics_discovery", re.compile(r"\bphysics discovery\b", re.IGNORECASE)),
    ("continuum_physics", re.compile(r"\bcontinuum (?:gauge|physics)\b", re.IGNORECASE)),
    ("lattice_qcd_correctness", re.compile(r"\blattice-QCD correctness\b", re.IGNORECASE)),
    ("full_smooth_hopf", re.compile(r"\bfull smooth Hopf\b", re.IGNORECASE)),
    ("complete_so3", re.compile(r"\bcomplete SO\(3\)\b", re.IGNORECASE)),
]

CLAIM_BOUNDARY_MARKERS = [
    "no ",
    "not ",
    "does not",
    "without",
    "examples only",
    "future",
    "boundary",
]

CAPABILITY_CLAIM_LANGUAGE_FIELDS = [
    "audience_interest",
    "standard_math_anchor",
    "circle_math_expression",
    "circle_native_value",
    "advertised_claim",
    "proof_scope",
    "proof_provenance",
]

ROUTE_CLAIM_LANGUAGE_FIELDS = [
    "title",
    "audience",
    "route_claim",
]


def claim_language_contract(item: dict, checked_fields: list[str]) -> dict:
    flagged_phrases = []
    for field in checked_fields:
        value = str(item.get(field, "") or "")
        for pattern_id, pattern in CLAIM_LANGUAGE_PATTERNS:
            for match in pattern.finditer(value):
                flagged_phrases.append(
                    {
                        "field": field,
                        "pattern": pattern_id,
                        "phrase": match.group(0),
                    }
                )
    boundary_text = str(item.get("not_claimed", "") or "")
    boundary_lower = boundary_text.lower()
    explicit_boundary = any(marker in boundary_lower for marker in CLAIM_BOUNDARY_MARKERS)
    return {
        "ready_to_advertise": not flagged_phrases and explicit_boundary,
        "checked_fields": checked_fields,
        "flagged_phrases": flagged_phrases,
        "boundary_field": "not_claimed",
        "explicit_boundary": explicit_boundary,
    }


def value_proposition_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
) -> dict:
    roles = set(item.get("portfolio_roles", []) or [])
    executable_ready = bool(item.get("executable_refs", []) or [])
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    checks = {
        "standard_math_parity": {
            "required": "standard_math_parity" in roles,
            "ready": (
                "standard_math_parity" not in roles
                or (
                    bool(str(item.get("standard_math_anchor", "")).strip())
                    and bool(str(item.get("circle_math_expression", "")).strip())
                    and theorem_ready
                )
            ),
            "evidence": (
                f"theorems "
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)}"
            ),
        },
        "circle_native_value": {
            "required": "circle_native_value" in roles,
            "ready": (
                "circle_native_value" not in roles
                or (
                    bool(str(item.get("circle_native_value", "")).strip())
                    and bool(str(item.get("circle_math_expression", "")).strip())
                    and source_ready
                    and living_ready
                    and executable_ready
                )
            ),
            "evidence": (
                f"sources {source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)}; "
                f"Living Book pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}"
            ),
        },
        "application_guardrail": {
            "required": "application_guardrail" in roles,
            "ready": (
                "application_guardrail" not in roles
                or (
                    bool(str(item.get("not_claimed", "")).strip())
                    and claim_language_contract.get("ready_to_advertise", False)
                    and source_ready
                    and executable_ready
                )
            ),
            "evidence": (
                "language "
                + (
                    "clean"
                    if claim_language_contract.get("ready_to_advertise", False)
                    else "incomplete"
                )
            ),
        },
    }
    return {
        "ready_to_advertise": all(
            check["ready"] for check in checks.values() if check["required"]
        ),
        "role_checks": checks,
    }


def proof_trail_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
) -> dict:
    executable_refs = item.get("executable_refs", []) or []
    source_refs = set(item.get("source_refs", []) or [])
    executable_ready = (
        bool(executable_refs)
        and all(ref in source_refs for ref in executable_refs)
        and all(
            Path(ref).name.startswith("test_") and Path(ref).suffix == ".py"
            for ref in executable_refs
        )
    )
    steps = [
        {
            "id": "paper_backing",
            "label": "cited paper backing",
            "ready": bool(item.get("paper_ids", []) or []),
            "evidence": f"{len(item.get('paper_ids', []) or [])} paper ids",
        },
        {
            "id": "theorem_refs",
            "label": "proved paper-carried theorem refs",
            "ready": (
                theorem_ref_contract.get("total_count", 0) > 0
                and theorem_ref_contract.get("proved_and_paper_backed_count")
                == theorem_ref_contract.get("total_count")
                and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
            ),
            "evidence": (
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)} theorem refs"
            ),
        },
        {
            "id": "source_refs",
            "label": "paper-backed source refs",
            "ready": (
                source_ref_contract.get("total_count", 0) > 0
                and source_ref_contract.get("backed_count")
                == source_ref_contract.get("total_count")
                and not source_ref_contract.get("unbacked_refs", [])
            ),
            "evidence": (
                f"{source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)} source refs"
            ),
        },
        {
            "id": "executable_refs",
            "label": "pytest executable refs",
            "ready": executable_ready,
            "evidence": f"{len(executable_refs)} executable refs",
        },
        {
            "id": "living_book_refs",
            "label": "backed Living Book presentation",
            "ready": (
                living_book_ref_contract.get("total_page_count", 0) > 0
                and living_book_ref_contract.get("backed_page_count")
                == living_book_ref_contract.get("total_page_count")
                and living_book_ref_contract.get("backed_widget_count")
                == living_book_ref_contract.get("total_widget_count")
                and not living_book_ref_contract.get("unbacked_pages", [])
                and not living_book_ref_contract.get("unbacked_widgets", [])
            ),
            "evidence": (
                f"pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}; "
                f"widgets {living_book_ref_contract.get('backed_widget_count', 0)}/"
                f"{living_book_ref_contract.get('total_widget_count', 0)}"
            ),
        },
        {
            "id": "role_value",
            "label": "role-backed value proposition",
            "ready": value_proposition_contract.get("ready_to_advertise", False),
            "evidence": (
                "role checks ready"
                if value_proposition_contract.get("ready_to_advertise", False)
                else "role checks incomplete"
            ),
        },
        {
            "id": "claim_language",
            "label": "advertising-language boundary",
            "ready": claim_language_contract.get("ready_to_advertise", False),
            "evidence": "clean" if claim_language_contract.get("ready_to_advertise", False) else "incomplete",
        },
    ]
    return {
        "ready_to_advertise": all(step["ready"] for step in steps),
        "passed_step_count": sum(1 for step in steps if step["ready"]),
        "total_step_count": len(steps),
        "steps": steps,
    }


def review_packet_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
    proof_trail_contract: dict,
) -> dict:
    executable_refs = item.get("executable_refs", []) or []
    expected_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
    verification_recipe = {
        "lean_command": "lake build",
        "pytest_command": expected_pytest_command,
        "capability_contract_command": (
            "python scripts/check_capability_showcase.py && "
            "python scripts/site/check_capability_contracts.py"
        ),
        "site_command": "make sitecheck",
    }
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    claim_ready = (
        bool(str(item.get("advertised_claim", "")).strip())
        and bool(str(item.get("proof_scope", "")).strip())
        and bool(str(item.get("not_claimed", "")).strip())
        and claim_language_contract.get("ready_to_advertise", False)
    )
    command_ready = (
        bool(executable_refs)
        and verification_recipe.get("pytest_command") == expected_pytest_command
        and verification_recipe.get("lean_command") == "lake build"
        and verification_recipe.get("site_command") == "make sitecheck"
    )
    local_gate_ready = (
        proof_trail_contract.get("ready_to_advertise", False)
        and value_proposition_contract.get("ready_to_advertise", False)
        and claim_language_contract.get("ready_to_advertise", False)
    )
    sections = [
        {
            "id": "claim_scope_boundary",
            "label": "claim, proof scope, and boundary",
            "ready": claim_ready,
            "evidence": (
                "claim/scope/boundary present"
                if claim_ready
                else "missing claim, proof scope, clean language, or boundary"
            ),
            "refs": [],
        },
        {
            "id": "paper_trail",
            "label": "paper trail",
            "ready": bool(item.get("paper_ids", []) or []),
            "evidence": f"{len(item.get('paper_ids', []) or [])} paper ids",
            "refs": item.get("paper_ids", []) or [],
        },
        {
            "id": "theorem_trail",
            "label": "proved theorem trail",
            "ready": theorem_ready,
            "evidence": (
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)} theorem refs"
            ),
            "refs": item.get("theorem_ids", []) or [],
        },
        {
            "id": "source_trail",
            "label": "paper-backed source trail",
            "ready": source_ready,
            "evidence": (
                f"{source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)} source refs"
            ),
            "refs": item.get("source_refs", []) or [],
        },
        {
            "id": "example_command",
            "label": "executable example command",
            "ready": command_ready,
            "evidence": verification_recipe.get("pytest_command", ""),
            "refs": executable_refs,
            "command": verification_recipe.get("pytest_command", ""),
        },
        {
            "id": "living_book_route",
            "label": "Living Book route",
            "ready": living_ready,
            "evidence": (
                f"pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}; "
                f"widgets {living_book_ref_contract.get('backed_widget_count', 0)}/"
                f"{living_book_ref_contract.get('total_widget_count', 0)}"
            ),
            "refs": item.get("living_book_refs", []) or [],
        },
        {
            "id": "local_verification_gates",
            "label": "local verification gates",
            "ready": local_gate_ready,
            "evidence": (
                f"proof trail {proof_trail_contract.get('passed_step_count', 0)}/"
                f"{proof_trail_contract.get('total_step_count', 0)}; "
                "role/value/language gates ready"
            ),
            "refs": [],
            "commands": [
                verification_recipe.get("lean_command", ""),
                verification_recipe.get("capability_contract_command", ""),
                verification_recipe.get("site_command", ""),
            ],
        },
    ]
    ready = all(section["ready"] for section in sections)
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "sections": sections,
    }


def parity_value_comparison_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
    proof_trail_contract: dict,
    review_packet_contract: dict,
) -> dict:
    roles = set(item.get("portfolio_roles", []) or [])
    evidence_counts = item.get("evidence_counts", {}) or {}
    executable_refs = item.get("executable_refs", []) or []
    standard_parity_claimed = "standard_math_parity" in roles
    circle_native_claimed = "circle_native_value" in roles
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    executable_ready = bool(executable_refs)
    standard_ready = (
        bool(str(item.get("audience_interest", "")).strip())
        and bool(str(item.get("standard_math_anchor", "")).strip())
        and theorem_ready
    )
    circle_form_ready = (
        bool(str(item.get("circle_math_expression", "")).strip())
        and bool(str(item.get("advertised_claim", "")).strip())
    )
    circle_value_ready = (
        circle_native_claimed
        and bool(str(item.get("circle_native_value", "")).strip())
        and value_proposition_contract.get("ready_to_advertise", False)
    )
    proof_backing_ready = (
        evidence_counts.get("paper_count", 0) > 0
        and theorem_ready
        and source_ready
        and living_ready
        and executable_ready
        and proof_trail_contract.get("ready_to_advertise", False)
    )
    review_ready = review_packet_contract.get("ready_to_review", False)
    boundary_ready = (
        bool(str(item.get("not_claimed", "")).strip())
        and claim_language_contract.get("ready_to_advertise", False)
    )
    sections = [
        {
            "id": "standard_reference",
            "label": "standard-math reference point",
            "ready": standard_ready,
            "evidence": item.get("standard_math_anchor", ""),
            "refs": item.get("theorem_ids", []) or [],
            "standard_parity_claimed": standard_parity_claimed,
        },
        {
            "id": "circle_expression",
            "label": "Circle expression of the same surface",
            "ready": circle_form_ready,
            "evidence": item.get("circle_math_expression", ""),
            "refs": item.get("source_refs", []) or [],
        },
        {
            "id": "circle_native_value",
            "label": "Circle-native value claim",
            "ready": circle_value_ready,
            "evidence": item.get("circle_native_value", ""),
            "refs": item.get("living_book_refs", []) or [],
            "circle_native_claimed": circle_native_claimed,
        },
        {
            "id": "proof_backing",
            "label": "paper, theorem, source, executable, and Living Book backing",
            "ready": proof_backing_ready,
            "evidence": (
                f"papers {evidence_counts.get('paper_count', 0)}; "
                f"theorem refs "
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)}; "
                f"sources {source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)}; "
                f"executables {evidence_counts.get('executable_count', 0)}; "
                f"Living Book pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}"
            ),
            "refs": [],
        },
        {
            "id": "review_entry",
            "label": "skeptical-reader review entry",
            "ready": review_ready,
            "evidence": (
                f"review packet {review_packet_contract.get('ready_section_count', 0)}/"
                f"{review_packet_contract.get('total_section_count', 0)} sections"
            ),
            "refs": [],
        },
        {
            "id": "advertising_boundary",
            "label": "advertising boundary",
            "ready": boundary_ready,
            "evidence": item.get("not_claimed", ""),
            "refs": [],
        },
    ]
    ready = all(section["ready"] for section in sections)
    summary_lines = [
        f"Standard reference: {item.get('standard_math_anchor', '')}",
        f"Circle expression: {item.get('circle_math_expression', '')}",
        f"Circle-native value: {item.get('circle_native_value', '')}",
        (
            f"Proof backing: {evidence_counts.get('paper_count', 0)} paper ids, "
            f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
            f"{theorem_ref_contract.get('total_count', 0)} theorem refs, "
            f"{source_ref_contract.get('backed_count', 0)}/"
            f"{source_ref_contract.get('total_count', 0)} source refs, "
            f"{evidence_counts.get('executable_count', 0)} executable refs, and "
            f"{living_book_ref_contract.get('backed_page_count', 0)}/"
            f"{living_book_ref_contract.get('total_page_count', 0)} Living Book page refs."
        ),
        f"Boundary: {item.get('not_claimed', '')}",
    ]
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "standard_parity_claimed": standard_parity_claimed,
        "circle_native_claimed": circle_native_claimed,
        "summary_lines": summary_lines,
        "sections": sections,
    }


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
    review_packets = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    parity_value_comparisons = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    for capability in capabilities:
        capability_id = capability.get("id", "<missing id>")
        theorem_contract = capability.get("theorem_ref_contract", {}) or {}
        source_contract = capability.get("source_ref_contract", {}) or {}
        living_contract = capability.get("living_book_ref_contract", {}) or {}
        review_contract = capability.get("review_packet_contract", {}) or {}

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
        review_packets["total_count"] += 1
        if review_contract.get("ready_to_review", False):
            review_packets["ready_count"] += 1
        else:
            review_packets["incomplete_capability_ids"].append(capability_id)
        comparison_contract = capability.get("parity_value_comparison_contract", {}) or {}
        parity_value_comparisons["total_count"] += 1
        if comparison_contract.get("ready_to_review", False):
            parity_value_comparisons["ready_count"] += 1
        else:
            parity_value_comparisons["incomplete_capability_ids"].append(capability_id)

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
    review_ready = (
        review_packets["ready_count"] == review_packets["total_count"]
        and not review_packets["incomplete_capability_ids"]
    )
    comparison_ready = (
        parity_value_comparisons["ready_count"] == parity_value_comparisons["total_count"]
        and not parity_value_comparisons["incomplete_capability_ids"]
    )
    return {
        "ready_to_advertise": (
            theorem_ready and source_ready and living_ready and review_ready and comparison_ready
        ),
        "theorem_refs": theorem_refs,
        "source_refs": source_refs,
        "living_book_refs": living_book_refs,
        "review_packets": review_packets,
        "parity_value_comparisons": parity_value_comparisons,
    }


def route_backing_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    unknown_capability_ids = [
        capability_id
        for capability_id in capability_ids
        if capability_id not in capability_by_id
    ]
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    incomplete_capability_ids = [
        capability.get("id", "<missing id>")
        for capability in route_capabilities
        if not (capability.get("claim_contract", {}) or {}).get("ready_to_advertise")
    ]
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
    review_packets = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    paper_ids: set[str] = set()
    theorem_ids: set[str] = set()
    dictionary_ids: set[str] = set()
    executable_refs: set[str] = set()
    source_ref_ids: set[str] = set()
    living_book_pages: set[str] = set()
    living_book_widgets: set[str] = set()
    roles: set[str] = set()
    provenance_kinds: set[str] = set()

    for capability in route_capabilities:
        capability_id = capability.get("id", "<missing id>")
        roles.update(capability.get("portfolio_roles", []) or [])
        provenance_kind = capability.get("proof_provenance_kind", "")
        if provenance_kind:
            provenance_kinds.add(provenance_kind)
        paper_ids.update(capability.get("paper_ids", []) or [])
        theorem_ids.update(capability.get("theorem_ids", []) or [])
        dictionary_ids.update(capability.get("dictionary_ids", []) or [])
        executable_refs.update(capability.get("executable_refs", []) or [])
        source_ref_ids.update(capability.get("source_refs", []) or [])
        for ref in capability.get("living_book_refs", []) or []:
            if not isinstance(ref, dict):
                continue
            page = ref.get("page", "")
            if page:
                living_book_pages.add(page)
            for widget_id in ref.get("widget_ids", []) or []:
                if widget_id:
                    living_book_widgets.add(widget_id)

        theorem_contract = capability.get("theorem_ref_contract", {}) or {}
        source_contract = capability.get("source_ref_contract", {}) or {}
        living_contract = capability.get("living_book_ref_contract", {}) or {}
        review_contract = capability.get("review_packet_contract", {}) or {}
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
        review_packets["total_count"] += 1
        if review_contract.get("ready_to_review", False):
            review_packets["ready_count"] += 1
        else:
            review_packets["incomplete_capability_ids"].append(capability_id)

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
    review_ready = (
        review_packets["ready_count"] == review_packets["total_count"]
        and not review_packets["incomplete_capability_ids"]
    )
    route_claim_language_contract = claim_language_contract(
        route,
        ROUTE_CLAIM_LANGUAGE_FIELDS,
    )
    return {
        "ready_to_advertise": (
            bool(capability_ids)
            and not unknown_capability_ids
            and not incomplete_capability_ids
            and theorem_ready
            and source_ready
            and living_ready
            and review_ready
            and route_claim_language_contract["ready_to_advertise"]
        ),
        "capability_count": len(capability_ids),
        "ready_capability_count": len(route_capabilities) - len(incomplete_capability_ids),
        "unknown_capability_ids": unknown_capability_ids,
        "incomplete_capability_ids": incomplete_capability_ids,
        "covered_roles": sorted(roles),
        "proof_provenance_kinds": sorted(provenance_kinds),
        "unique_evidence_counts": {
            "paper_count": len(paper_ids),
            "theorem_count": len(theorem_ids),
            "dictionary_count": len(dictionary_ids),
            "executable_count": len(executable_refs),
            "source_count": len(source_ref_ids),
            "living_book_page_count": len(living_book_pages),
            "living_book_widget_count": len(living_book_widgets),
        },
        "theorem_refs": theorem_refs,
        "source_refs": source_refs,
        "living_book_refs": living_book_refs,
        "review_packets": review_packets,
        "claim_language_contract": route_claim_language_contract,
    }


def route_review_dossier_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    route_contract = route_backing_contract(route, capability_by_id)
    executable_refs = sorted(
        {
            ref
            for capability in route_capabilities
            for ref in (capability.get("executable_refs", []) or [])
        }
    )
    route_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
    role_counts: dict[str, dict[str, int]] = {}
    for role in ("standard_math_parity", "circle_native_value", "application_guardrail"):
        required_capabilities = [
            capability
            for capability in route_capabilities
            if role in (capability.get("portfolio_roles", []) or [])
        ]
        ready_capabilities = [
            capability
            for capability in required_capabilities
            if (
                (
                    capability.get("value_proposition_contract", {})
                    or {}
                ).get("role_checks", {})
                or {}
            ).get(role, {}).get("ready", False)
        ]
        role_counts[role] = {
            "ready_count": len(ready_capabilities),
            "total_count": len(required_capabilities),
        }

    theorem_refs = route_contract.get("theorem_refs", {}) or {}
    source_refs = route_contract.get("source_refs", {}) or {}
    living_refs = route_contract.get("living_book_refs", {}) or {}
    review_packets = route_contract.get("review_packets", {}) or {}
    route_language = route_contract.get("claim_language_contract", {}) or {}
    capability_language_ready_count = sum(
        1
        for capability in route_capabilities
        if (capability.get("claim_language_contract", {}) or {}).get(
            "ready_to_advertise",
            False,
        )
    )
    proof_provenance_kinds = route_contract.get("proof_provenance_kinds", []) or []
    theorem_ready = (
        theorem_refs.get("total_count", 0) > 0
        and theorem_refs.get("proved_and_paper_backed_count")
        == theorem_refs.get("total_count")
        and not theorem_refs.get("unproved_or_unbacked_refs", [])
    )
    source_ready = (
        source_refs.get("total_count", 0) > 0
        and source_refs.get("backed_count") == source_refs.get("total_count")
        and not source_refs.get("unbacked_refs", [])
    )
    living_ready = (
        living_refs.get("total_page_count", 0) > 0
        and living_refs.get("backed_page_count") == living_refs.get("total_page_count")
        and living_refs.get("backed_widget_count") == living_refs.get("total_widget_count")
        and not living_refs.get("unbacked_pages", [])
        and not living_refs.get("unbacked_widgets", [])
    )
    standard_ready = (
        role_counts["standard_math_parity"]["total_count"] > 0
        and role_counts["standard_math_parity"]["ready_count"]
        == role_counts["standard_math_parity"]["total_count"]
    )
    circle_native_ready = (
        role_counts["circle_native_value"]["total_count"] > 0
        and role_counts["circle_native_value"]["ready_count"]
        == role_counts["circle_native_value"]["total_count"]
    )
    guardrail_ready = (
        route_language.get("ready_to_advertise", False)
        and capability_language_ready_count == len(route_capabilities)
        and all(bool(str(capability.get("not_claimed", "")).strip()) for capability in route_capabilities)
    )
    sections = [
        {
            "id": "route_scope_boundary",
            "label": "route claim, audience, and boundary",
            "ready": (
                bool(str(route.get("audience", "")).strip())
                and bool(str(route.get("route_claim", "")).strip())
                and bool(str(route.get("not_claimed", "")).strip())
                and route_language.get("ready_to_advertise", False)
            ),
            "evidence": (
                "route claim language clean"
                if route_language.get("ready_to_advertise", False)
                else "route claim language incomplete"
            ),
            "refs": [],
        },
        {
            "id": "capability_review_packets",
            "label": "capability review packets",
            "ready": (
                review_packets.get("total_count", 0) > 0
                and review_packets.get("ready_count") == review_packets.get("total_count")
                and not review_packets.get("incomplete_capability_ids", [])
                and not route_contract.get("unknown_capability_ids", [])
                and not route_contract.get("incomplete_capability_ids", [])
            ),
            "evidence": (
                f"{review_packets.get('ready_count', 0)}/"
                f"{review_packets.get('total_count', 0)} packets"
            ),
            "refs": capability_ids,
        },
        {
            "id": "standard_parity_surface",
            "label": "standard-math parity surface",
            "ready": standard_ready,
            "evidence": (
                f"{role_counts['standard_math_parity']['ready_count']}/"
                f"{role_counts['standard_math_parity']['total_count']} standard-parity lanes"
            ),
            "refs": [
                capability.get("id", "")
                for capability in route_capabilities
                if "standard_math_parity" in (capability.get("portfolio_roles", []) or [])
            ],
        },
        {
            "id": "circle_native_surface",
            "label": "Circle-native value surface",
            "ready": circle_native_ready,
            "evidence": (
                f"{role_counts['circle_native_value']['ready_count']}/"
                f"{role_counts['circle_native_value']['total_count']} Circle-native lanes"
            ),
            "refs": [
                capability.get("id", "")
                for capability in route_capabilities
                if "circle_native_value" in (capability.get("portfolio_roles", []) or [])
            ],
        },
        {
            "id": "proof_provenance_surface",
            "label": "proof provenance and backing surface",
            "ready": bool(proof_provenance_kinds) and theorem_ready and source_ready and living_ready,
            "evidence": (
                f"provenance {', '.join(proof_provenance_kinds) or 'none'}; "
                f"theorems {theorem_refs.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_refs.get('total_count', 0)}; "
                f"sources {source_refs.get('backed_count', 0)}/"
                f"{source_refs.get('total_count', 0)}"
            ),
            "refs": proof_provenance_kinds,
        },
        {
            "id": "route_reproduction_command",
            "label": "route-wide executable reproduction command",
            "ready": bool(executable_refs),
            "evidence": route_pytest_command,
            "refs": executable_refs,
            "command": route_pytest_command,
        },
        {
            "id": "advertising_guardrails",
            "label": "route and capability advertising guardrails",
            "ready": guardrail_ready,
            "evidence": (
                f"route language {'pass' if route_language.get('ready_to_advertise', False) else 'fail'}; "
                f"capability language {capability_language_ready_count}/{len(route_capabilities)}"
            ),
            "refs": capability_ids,
        },
    ]
    ready = all(section["ready"] for section in sections)
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "role_counts": role_counts,
        "sections": sections,
    }


def route_impact_summary_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    route_contract = route_backing_contract(route, capability_by_id)
    route_dossier = route_review_dossier_contract(route, capability_by_id)
    unique_counts = route_contract.get("unique_evidence_counts", {}) or {}
    route_language = route_contract.get("claim_language_contract", {}) or {}
    areas = sorted(
        {
            str(capability.get("area", "")).strip()
            for capability in route_capabilities
            if str(capability.get("area", "")).strip()
        }
    )
    standard_interest_refs = [
        {
            "capability_id": capability.get("id", ""),
            "area": capability.get("area", ""),
            "audience_interest": capability.get("audience_interest", ""),
            "standard_math_anchor": capability.get("standard_math_anchor", ""),
        }
        for capability in route_capabilities
    ]
    circle_native_value_refs = [
        {
            "capability_id": capability.get("id", ""),
            "circle_math_expression": capability.get("circle_math_expression", ""),
            "circle_native_value": capability.get("circle_native_value", ""),
        }
        for capability in route_capabilities
    ]
    capability_language_ready_count = sum(
        1
        for capability in route_capabilities
        if (capability.get("claim_language_contract", {}) or {}).get(
            "ready_to_advertise",
            False,
        )
    )
    audience_ready = (
        bool(str(route.get("title", "")).strip())
        and bool(str(route.get("audience", "")).strip())
        and bool(str(route.get("route_claim", "")).strip())
    )
    interest_ready = bool(standard_interest_refs) and all(
        str(ref.get("area", "")).strip()
        and str(ref.get("audience_interest", "")).strip()
        and str(ref.get("standard_math_anchor", "")).strip()
        for ref in standard_interest_refs
    )
    circle_value_ready = bool(circle_native_value_refs) and all(
        str(ref.get("circle_math_expression", "")).strip()
        and str(ref.get("circle_native_value", "")).strip()
        for ref in circle_native_value_refs
    )
    proof_backing_ready = (
        route_contract.get("ready_to_advertise", False)
        and unique_counts.get("paper_count", 0) > 0
        and unique_counts.get("theorem_count", 0) > 0
        and unique_counts.get("source_count", 0) > 0
        and unique_counts.get("executable_count", 0) > 0
        and unique_counts.get("living_book_page_count", 0) > 0
    )
    boundary_ready = (
        route_language.get("ready_to_advertise", False)
        and bool(str(route.get("not_claimed", "")).strip())
        and capability_language_ready_count == len(route_capabilities)
    )
    sections = [
        {
            "id": "audience_signal",
            "label": "audience and route signal",
            "ready": audience_ready,
            "evidence": route.get("audience", ""),
            "refs": [],
        },
        {
            "id": "standard_interest_surface",
            "label": "respected standard-math interest surface",
            "ready": interest_ready,
            "evidence": f"{len(standard_interest_refs)} capability interest anchors",
            "refs": [ref["capability_id"] for ref in standard_interest_refs],
        },
        {
            "id": "circle_native_value_surface",
            "label": "Circle-native value surface",
            "ready": circle_value_ready,
            "evidence": f"{len(circle_native_value_refs)} Circle-native value statements",
            "refs": [ref["capability_id"] for ref in circle_native_value_refs],
        },
        {
            "id": "proof_backing_counts",
            "label": "proof-backed evidence counts",
            "ready": proof_backing_ready,
            "evidence": (
                f"papers {unique_counts.get('paper_count', 0)}; "
                f"theorem refs {unique_counts.get('theorem_count', 0)}; "
                f"source refs {unique_counts.get('source_count', 0)}; "
                f"executables {unique_counts.get('executable_count', 0)}; "
                f"Living Book pages {unique_counts.get('living_book_page_count', 0)}"
            ),
            "refs": [],
        },
        {
            "id": "review_path",
            "label": "review path",
            "ready": route_dossier.get("ready_to_review", False),
            "evidence": (
                f"route dossier {route_dossier.get('ready_section_count', 0)}/"
                f"{route_dossier.get('total_section_count', 0)} sections"
            ),
            "refs": [],
        },
        {
            "id": "advertising_boundary",
            "label": "advertising boundary",
            "ready": boundary_ready,
            "evidence": route.get("not_claimed", ""),
            "refs": capability_ids,
        },
    ]
    ready = all(section["ready"] for section in sections)
    summary_lines = [
        f"Audience: {route.get('audience', '')}",
        (
            f"Capability surface: {len(route_capabilities)} route lanes"
            + (f" across {', '.join(areas)}." if areas else ".")
        ),
        (
            f"Proof backing: {unique_counts.get('theorem_count', 0)} proved theorem refs, "
            f"{unique_counts.get('paper_count', 0)} paper ids, "
            f"{unique_counts.get('source_count', 0)} source refs, "
            f"{unique_counts.get('executable_count', 0)} executable refs, "
            f"and {unique_counts.get('living_book_page_count', 0)} Living Book page refs."
        ),
        (
            f"Circle-native value: {len(circle_native_value_refs)} lanes state explicit "
            "Circle expression/value statements with role-backed checks."
        ),
        f"Boundary: {route.get('not_claimed', '')}",
    ]
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "areas": areas,
        "summary_lines": summary_lines,
        "standard_interest_refs": standard_interest_refs,
        "circle_native_value_refs": circle_native_value_refs,
        "sections": sections,
    }


def portfolio_route_summary(routes: list[dict]) -> dict:
    ready_count = sum(
        1
        for route in routes
        if (route.get("route_contract", {}) or {}).get("ready_to_advertise")
    )
    return {
        "route_count": len(routes),
        "ready_count": ready_count,
        "incomplete_count": len(routes) - ready_count,
        "ready_dossier_count": sum(
            1
            for route in routes
            if (route.get("route_review_dossier_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "incomplete_dossier_ids": sorted(
            route.get("id", "")
            for route in routes
            if not (route.get("route_review_dossier_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "ready_impact_summary_count": sum(
            1
            for route in routes
            if (route.get("route_impact_summary_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "incomplete_impact_summary_ids": sorted(
            route.get("id", "")
            for route in routes
            if not (route.get("route_impact_summary_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "unknown_capability_ids": sorted(
            {
                capability_id
                for route in routes
                for capability_id in (
                    (route.get("route_contract", {}) or {}).get("unknown_capability_ids", [])
                    or []
                )
            }
        ),
    }


def expected_portfolio_summary(
    capabilities: list[dict],
    routes: list[dict],
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
        "route_summary": portfolio_route_summary(routes),
    }


def main() -> int:
    failures: list[str] = []
    data = load_json(GENERATED / "capability_showcase.json")
    capabilities = data.get("capabilities", [])
    routes = data.get("portfolio_routes", [])
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
        expected_claim_language_contract = claim_language_contract(
            capability,
            CAPABILITY_CLAIM_LANGUAGE_FIELDS,
        )
        if capability.get("claim_language_contract") != expected_claim_language_contract:
            failures.append(
                f"{capability_id}: claim_language_contract does not match claim text"
            )
        if not expected_claim_language_contract["ready_to_advertise"]:
            failures.append(
                f"{capability_id}: advertising language guardrail is incomplete"
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
        if (
            isinstance(theorem_ref_contract, dict)
            and isinstance(source_ref_contract, dict)
            and isinstance(living_book_ref_contract, dict)
        ):
            expected_value_contract = value_proposition_contract(
                capability,
                theorem_ref_contract,
                source_ref_contract,
                living_book_ref_contract,
                expected_claim_language_contract,
            )
            if capability.get("value_proposition_contract") != expected_value_contract:
                failures.append(
                    f"{capability_id}: value_proposition_contract does not match evidence"
                )
            if not expected_value_contract["ready_to_advertise"]:
                failures.append(
                    f"{capability_id}: role-backed value proposition is incomplete"
                )
            expected_proof_trail_contract = proof_trail_contract(
                capability,
                theorem_ref_contract,
                source_ref_contract,
                living_book_ref_contract,
                expected_claim_language_contract,
                expected_value_contract,
            )
            if capability.get("proof_trail_contract") != expected_proof_trail_contract:
                failures.append(
                    f"{capability_id}: proof_trail_contract does not match evidence"
                )
            if not expected_proof_trail_contract["ready_to_advertise"]:
                failures.append(f"{capability_id}: ordered proof trail is incomplete")
            expected_review_packet_contract = review_packet_contract(
                capability,
                theorem_ref_contract,
                source_ref_contract,
                living_book_ref_contract,
                expected_claim_language_contract,
                expected_value_contract,
                expected_proof_trail_contract,
            )
            if capability.get("review_packet_contract") != expected_review_packet_contract:
                failures.append(
                    f"{capability_id}: review_packet_contract does not match evidence"
                )
            if not expected_review_packet_contract["ready_to_review"]:
                failures.append(f"{capability_id}: review packet is incomplete")
            expected_comparison_contract = parity_value_comparison_contract(
                capability,
                theorem_ref_contract,
                source_ref_contract,
                living_book_ref_contract,
                expected_claim_language_contract,
                expected_value_contract,
                expected_proof_trail_contract,
                expected_review_packet_contract,
            )
            if (
                capability.get("parity_value_comparison_contract")
                != expected_comparison_contract
            ):
                failures.append(
                    f"{capability_id}: parity_value_comparison_contract does not match evidence"
                )
            if not expected_comparison_contract["ready_to_review"]:
                failures.append(
                    f"{capability_id}: parity/value comparison is incomplete"
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
    capability_by_id = {
        capability.get("id"): capability
        for capability in capabilities
        if capability.get("id")
    }
    route_ids = [route.get("id") for route in routes if isinstance(route, dict)]
    duplicate_route_ids = sorted(
        {route_id for route_id in route_ids if route_id and route_ids.count(route_id) > 1}
    )
    if duplicate_route_ids:
        failures.append(f"duplicate portfolio route ids: {duplicate_route_ids}")
    for route in routes:
        if not isinstance(route, dict):
            failures.append("portfolio route must be a mapping")
            continue
        route_id = route.get("id", "<missing route id>")
        for field in REQUIRED_ROUTE_FIELDS:
            if not str(route.get(field, "")).strip():
                failures.append(f"{route_id}: route {field} is required")
        capability_ids = route.get("capability_ids", [])
        if not isinstance(capability_ids, list) or not capability_ids:
            failures.append(f"{route_id}: route capability_ids must be a nonempty list")
            capability_ids = []
        duplicate_capability_ids = sorted(
            {
                capability_id
                for capability_id in capability_ids
                if capability_id and capability_ids.count(capability_id) > 1
            }
        )
        if duplicate_capability_ids:
            failures.append(
                f"{route_id}: duplicate route capability ids {duplicate_capability_ids}"
            )
        expected_contract = route_backing_contract(route, capability_by_id)
        if route.get("route_contract") != expected_contract:
            failures.append(f"{route_id}: route_contract does not match capabilities")
        if not expected_contract["ready_to_advertise"]:
            failures.append(f"{route_id}: route contract is incomplete")
        expected_dossier_contract = route_review_dossier_contract(route, capability_by_id)
        if route.get("route_review_dossier_contract") != expected_dossier_contract:
            failures.append(
                f"{route_id}: route_review_dossier_contract does not match capabilities"
            )
        if not expected_dossier_contract["ready_to_review"]:
            failures.append(f"{route_id}: route review dossier is incomplete")
        expected_impact_summary_contract = route_impact_summary_contract(
            route,
            capability_by_id,
        )
        if route.get("route_impact_summary_contract") != expected_impact_summary_contract:
            failures.append(
                f"{route_id}: route_impact_summary_contract does not match capabilities"
            )
        if not expected_impact_summary_contract["ready_to_review"]:
            failures.append(f"{route_id}: route impact summary is incomplete")
    expected_summary = expected_portfolio_summary(
        capabilities,
        routes,
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
