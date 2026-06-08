from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import (
    DICTIONARY,
    DIMENSION_DICTIONARIES,
    PAPER_MANIFEST,
    ROOT,
)


SHOWCASE = ROOT / "manifests" / "capability_showcase.yaml"
SHOWCASE_PAGE = ROOT / "site" / "showcase.qmd"
PROVED_STATUSES = {"proved", "lean_proved"}
ALLOWED_PORTFOLIO_ROLES = {
    "standard_math_parity",
    "circle_native_value",
    "application_guardrail",
}
REQUIRED_TEXT_FIELDS = [
    "title",
    "area",
    "audience_interest",
    "standard_math_anchor",
    "circle_math_expression",
    "circle_native_value",
    "advertised_claim",
    "proof_scope",
    "not_claimed",
]
CAPABILITY_ATTR_RE = re.compile(
    r'<div class="capability-anchor"[^>]*data-capability-id="([^"]+)"'
)
EXECUTABLE_ATTR_RE = re.compile(
    r'data-capability-id="([^"]+)"[^>]*data-executable-ref="([^"]+)"'
)
THEOREM_BOX_RE = re.compile(r'<div class="theorem-box"([^>]*)>')


def html_attr(attrs: str, name: str) -> str | None:
    match = re.search(rf'{re.escape(name)}="([^"]+)"', attrs)
    if match:
        return match.group(1)
    return None


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def theorem_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in sorted((ROOT / "manifests").glob("**/*.yaml")):
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                statuses[theorem_id] = theorem.get("status", "")
    return statuses


def paper_index() -> dict[str, dict]:
    data = load_yaml(PAPER_MANIFEST)
    return {paper["id"]: paper for paper in data.get("papers", []) if paper.get("id")}


def dictionary_ids() -> set[str]:
    ids = {
        entry["id"]
        for entry in load_yaml(DICTIONARY).get("entries", [])
        if entry.get("id")
    }
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        ids.update(
            entry["id"]
            for entry in load_yaml(path).get("entries", [])
            if entry.get("id")
        )
    return ids


def path_for_paper_id(paper_id: str) -> Path | None:
    for path in sorted((ROOT / "papers").glob("**/*.md")):
        if path.stem == paper_id:
            return path
    return None


def page_capability_ids() -> list[str]:
    if not SHOWCASE_PAGE.exists():
        return []
    return CAPABILITY_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_executable_pairs() -> list[tuple[str, str]]:
    if not SHOWCASE_PAGE.exists():
        return []
    return EXECUTABLE_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_theorem_pairs() -> tuple[list[tuple[str, str]], list[str]]:
    if not SHOWCASE_PAGE.exists():
        return [], []
    pairs: list[tuple[str, str]] = []
    missing_capabilities: list[str] = []
    for attrs in THEOREM_BOX_RE.findall(SHOWCASE_PAGE.read_text()):
        theorem_id = html_attr(attrs, "data-theorem-id")
        capability_id = html_attr(attrs, "data-capability-id")
        if theorem_id and capability_id:
            pairs.append((capability_id, theorem_id))
        elif theorem_id:
            missing_capabilities.append(theorem_id)
    return pairs, missing_capabilities


def main() -> int:
    data = load_yaml(SHOWCASE)
    capabilities = data.get("capabilities", [])
    statuses = theorem_statuses()
    papers = paper_index()
    known_dictionary_ids = dictionary_ids()
    failures: list[str] = []

    ids = [item.get("id") for item in capabilities]
    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        failures.append(f"duplicate capability ids: {duplicates}")

    if not SHOWCASE_PAGE.exists():
        failures.append(
            f"missing showcase page {SHOWCASE_PAGE.relative_to(ROOT)}"
        )
        page_ids: list[str] = []
    else:
        page_ids = page_capability_ids()
        page_duplicates = sorted(
            {item for item in page_ids if page_ids.count(item) > 1}
        )
        if page_duplicates:
            failures.append(f"duplicate page capability ids: {page_duplicates}")
        manifest_ids = {item for item in ids if item}
        page_id_set = set(page_ids)
        missing_on_page = sorted(manifest_ids - page_id_set)
        unknown_on_page = sorted(page_id_set - manifest_ids)
        if missing_on_page:
            failures.append(f"capability ids missing from page: {missing_on_page}")
        if unknown_on_page:
            failures.append(f"unknown page capability ids: {unknown_on_page}")
        page_executables = page_executable_pairs()
        executable_duplicates = sorted(
            {pair for pair in page_executables if page_executables.count(pair) > 1}
        )
        if executable_duplicates:
            failures.append(
                f"duplicate page executable refs: {executable_duplicates}"
            )
        expected_executables = {
            (item.get("id"), ref)
            for item in capabilities
            if item.get("id") and isinstance(item.get("executable_refs", []), list)
            for ref in item.get("executable_refs", [])
        }
        page_executable_set = set(page_executables)
        missing_executables = sorted(expected_executables - page_executable_set)
        unknown_executables = sorted(page_executable_set - expected_executables)
        if missing_executables:
            failures.append(
                f"executable refs missing from page: {missing_executables}"
            )
        if unknown_executables:
            failures.append(
                f"unknown page executable refs: {unknown_executables}"
            )
        page_theorems, theorem_boxes_without_capability = page_theorem_pairs()
        if theorem_boxes_without_capability:
            failures.append(
                "page theorem boxes missing data-capability-id: "
                f"{sorted(theorem_boxes_without_capability)}"
            )
        theorem_duplicates = sorted(
            {pair for pair in page_theorems if page_theorems.count(pair) > 1}
        )
        if theorem_duplicates:
            failures.append(f"duplicate page theorem refs: {theorem_duplicates}")
        expected_theorems = {
            (item.get("id"), theorem_id)
            for item in capabilities
            if item.get("id") and isinstance(item.get("theorem_ids", []), list)
            for theorem_id in item.get("theorem_ids", [])
        }
        page_theorem_set = set(page_theorems)
        missing_theorems = sorted(expected_theorems - page_theorem_set)
        unknown_theorems = sorted(page_theorem_set - expected_theorems)
        if missing_theorems:
            failures.append(f"theorem refs missing from page: {missing_theorems}")
        if unknown_theorems:
            failures.append(f"unknown page theorem refs: {unknown_theorems}")

    for item in capabilities:
        capability_id = item.get("id", "<missing id>")
        if not item.get("id"):
            failures.append("capability entry missing id")
        for field in REQUIRED_TEXT_FIELDS:
            if not item.get(field):
                failures.append(f"{capability_id}: missing {field}")

        theorem_ids = item.get("theorem_ids", [])
        paper_ids = item.get("paper_ids", [])
        refs = item.get("source_refs", [])
        executable_refs = item.get("executable_refs", [])
        roles = item.get("portfolio_roles", [])

        if not theorem_ids:
            failures.append(f"{capability_id}: must advertise at least one theorem id")
        if not paper_ids:
            failures.append(f"{capability_id}: must cite at least one paper id")
        if not refs:
            failures.append(f"{capability_id}: must cite at least one source ref")
        if not isinstance(executable_refs, list) or not executable_refs:
            failures.append(f"{capability_id}: must cite at least one executable ref")
            executable_refs = []
        if not isinstance(roles, list) or not roles:
            failures.append(f"{capability_id}: must declare portfolio_roles")
            roles = []
        unknown_roles = sorted(set(roles) - ALLOWED_PORTFOLIO_ROLES)
        if unknown_roles:
            failures.append(f"{capability_id}: unknown portfolio roles {unknown_roles}")
        if "standard_math_parity" not in roles and "circle_native_value" not in roles:
            failures.append(
                f"{capability_id}: must advertise either standard_math_parity or circle_native_value"
            )

        duplicate_theorems = sorted({tid for tid in theorem_ids if theorem_ids.count(tid) > 1})
        if duplicate_theorems:
            failures.append(f"{capability_id}: duplicate theorem ids {duplicate_theorems}")

        duplicate_papers = sorted({pid for pid in paper_ids if paper_ids.count(pid) > 1})
        if duplicate_papers:
            failures.append(f"{capability_id}: duplicate paper ids {duplicate_papers}")

        duplicate_executables = sorted(
            {ref for ref in executable_refs if executable_refs.count(ref) > 1}
        )
        if duplicate_executables:
            failures.append(
                f"{capability_id}: duplicate executable refs {duplicate_executables}"
            )

        paper_theorem_ids: set[str] = set()
        for paper_id in paper_ids:
            paper = papers.get(paper_id)
            if paper is None:
                failures.append(f"{capability_id}: unknown paper id {paper_id}")
                continue
            if path_for_paper_id(paper_id) is None:
                failures.append(f"{capability_id}: no paper file for {paper_id}")
            paper_theorem_ids.update(paper.get("theorem_ids", []))

        for theorem_id in theorem_ids:
            status = statuses.get(theorem_id)
            if status is None:
                failures.append(f"{capability_id}: unknown theorem id {theorem_id}")
            elif status not in PROVED_STATUSES:
                failures.append(f"{capability_id}: theorem {theorem_id} status is {status}")
            if theorem_id not in paper_theorem_ids:
                failures.append(
                    f"{capability_id}: theorem {theorem_id} is not carried by cited papers {paper_ids}"
                )

        for dictionary_id in item.get("dictionary_ids", []):
            if dictionary_id not in known_dictionary_ids:
                failures.append(f"{capability_id}: unknown dictionary id {dictionary_id}")

        for ref in refs:
            local_ref = Path(ref)
            ref_path = ROOT / local_ref
            if local_ref.is_absolute() or ".." in local_ref.parts:
                failures.append(f"{capability_id}: unsafe source ref {ref}")
            elif not ref_path.exists():
                failures.append(f"{capability_id}: missing source ref {ref}")

        for ref in executable_refs:
            local_ref = Path(ref)
            ref_path = ROOT / local_ref
            if ref not in refs:
                failures.append(
                    f"{capability_id}: executable ref {ref} must also be listed in source_refs"
                )
            if local_ref.is_absolute() or ".." in local_ref.parts:
                failures.append(f"{capability_id}: unsafe executable ref {ref}")
            elif not ref_path.exists():
                failures.append(f"{capability_id}: missing executable ref {ref}")
            elif local_ref.parts[0] not in {"sidecars", "tests"}:
                failures.append(
                    f"{capability_id}: executable ref {ref} must live under sidecars/ or tests/"
                )
            elif ref_path.suffix != ".py" or not ref_path.name.startswith("test_"):
                failures.append(
                    f"{capability_id}: executable ref {ref} must be a pytest test_*.py file"
                )

    if failures:
        print("capability showcase failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"capability showcase ok: {len(capabilities)} capabilities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
