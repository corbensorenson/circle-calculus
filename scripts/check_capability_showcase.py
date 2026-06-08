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
SHOWCASE_MATRIX_WIDGET_ID = "capability_portfolio_matrix"
SHOWCASE_MATRIX_SCRIPT = "widgets/showcase/capability_portfolio_matrix.js"
PROVED_STATUSES = {"proved", "lean_proved"}
ALLOWED_PORTFOLIO_ROLES = {
    "standard_math_parity",
    "circle_native_value",
    "application_guardrail",
}
ALLOWED_PROOF_PROVENANCE_KINDS = {
    "mathlib_bridge",
    "project_native",
    "mixed",
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
    "proof_provenance",
    "not_claimed",
]
PAGE_CLAIM_FIELDS = [
    "standard_math_anchor",
    "circle_math_expression",
    "circle_native_value",
    "advertised_claim",
    "proof_scope",
    "proof_provenance",
    "not_claimed",
]
CAPABILITY_ATTR_RE = re.compile(
    r'<div[^>]*class="capability-anchor"[^>]*data-capability-id="([^"]+)"'
)
ROLE_ATTR_RE = re.compile(
    r'data-capability-id="([^"]+)"[^>]*data-portfolio-role="([^"]+)"'
)
CLAIM_FIELD_RE = re.compile(
    r'<span class="claim-field-evidence"([^>]*)></span>(.*)$'
)
EXECUTABLE_ATTR_RE = re.compile(
    r'data-capability-id="([^"]+)"[^>]*data-executable-ref="([^"]+)"'
)
DICTIONARY_ATTR_RE = re.compile(
    r'data-capability-id="([^"]+)"[^>]*data-dictionary-id="([^"]+)"'
)
LIVING_BOOK_PAGE_REF_RE = re.compile(
    r'<span class="living-book-evidence"([^>]*)></span>'
)
LIVING_BOOK_WIDGET_REF_RE = re.compile(
    r'<span class="living-book-widget-evidence"([^>]*)></span>'
)
WIDGET_PANEL_RE = re.compile(r'data-widget="([^"]+)"')
THEOREM_ATTR_RE = re.compile(r'data-theorem-id="([^"]+)"')
SHOWCASE_REF_RE = re.compile(r'data-showcase-ref="([^"]+)"')
THEOREM_BOX_RE = re.compile(r'<div class="theorem-box"([^>]*)>')
PAPER_REF_RE = re.compile(r'<p([^>]*data-paper-ref="[^"]+"[^>]*)>')
SECTION_RE = re.compile(r"^##\s+", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(.+)$")


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


def source_trail_section(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text()
    marker = "## Source Trail"
    start = text.find(marker)
    if start == -1:
        return ""
    next_section = SECTION_RE.search(text, start + len(marker))
    if next_section is None:
        return text[start:]
    return text[start : next_section.start()]


def module_name_for_path(path: Path) -> str:
    return ".".join(path.with_suffix("").parts)


def module_name_for_ref(ref: str) -> str:
    return module_name_for_path(Path(ref))


def lean_modules_by_name() -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for path in sorted(ROOT.glob("**/*.lean")):
        if ".lake" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        modules[module_name_for_path(relative)] = path
    return modules


def imported_modules(path: Path) -> set[str]:
    imports: set[str] = set()
    if not path.exists():
        return imports
    for line in path.read_text().splitlines():
        match = IMPORT_RE.match(line)
        if not match:
            continue
        imports.update(part for part in match.group(1).split() if part)
    return imports


def paper_lean_sidecars(paper: dict) -> list[Path]:
    sidecar = paper.get("sidecar")
    if not sidecar:
        return []
    lean_dir = ROOT / sidecar / "lean"
    if not lean_dir.exists():
        return []
    return sorted(lean_dir.glob("*.lean"))


def transitive_local_imports(start_paths: list[Path], modules: dict[str, Path]) -> set[str]:
    seen: set[str] = set()
    stack: list[str] = []
    for path in start_paths:
        stack.extend(imported_modules(path))
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        local_path = modules.get(module)
        if local_path is not None:
            stack.extend(imported_modules(local_path) - seen)
    return seen


def paper_source_ref_backed(ref: str, paper_ids: list[str], papers: dict[str, dict], modules: dict[str, Path]) -> bool:
    source_sections: list[str] = []
    sidecar_paths: list[Path] = []
    for paper_id in paper_ids:
        paper = papers.get(paper_id)
        if paper is None:
            continue
        paper_path = path_for_paper_id(paper_id)
        if paper_path is not None:
            source_sections.append(source_trail_section(paper_path))
        sidecar_paths.extend(paper_lean_sidecars(paper))

    if any(ref in section for section in source_sections):
        return True
    local_ref = Path(ref)
    if local_ref.parts[:1] == ("Circle",) and local_ref.suffix == ".lean":
        module_name = module_name_for_ref(ref)
        return module_name in transitive_local_imports(sidecar_paths, modules)
    return False


def page_capability_ids() -> list[str]:
    if not SHOWCASE_PAGE.exists():
        return []
    return CAPABILITY_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_executable_pairs() -> list[tuple[str, str]]:
    if not SHOWCASE_PAGE.exists():
        return []
    return EXECUTABLE_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_role_pairs() -> list[tuple[str, str]]:
    if not SHOWCASE_PAGE.exists():
        return []
    return ROLE_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_claim_field_entries() -> tuple[list[tuple[str, str]], list[str], list[tuple[str, str, str]]]:
    if not SHOWCASE_PAGE.exists():
        return [], [], []
    pairs: list[tuple[str, str]] = []
    missing_attrs: list[str] = []
    values: list[tuple[str, str, str]] = []
    for line in SHOWCASE_PAGE.read_text().splitlines():
        if "claim-field-evidence" not in line:
            continue
        match = CLAIM_FIELD_RE.search(line)
        if match is None:
            failures_token = line.strip()[:120]
            missing_attrs.append(failures_token)
            continue
        attrs, value = match.groups()
        capability_id = html_attr(attrs, "data-capability-id")
        claim_field = html_attr(attrs, "data-claim-field")
        if capability_id and claim_field:
            pairs.append((capability_id, claim_field))
            values.append((capability_id, claim_field, value.strip()))
        else:
            missing_attrs.append(line.strip()[:120])
    return pairs, missing_attrs, values


def page_dictionary_pairs() -> list[tuple[str, str]]:
    if not SHOWCASE_PAGE.exists():
        return []
    return DICTIONARY_ATTR_RE.findall(SHOWCASE_PAGE.read_text())


def page_living_book_entries() -> tuple[
    list[tuple[str, str]],
    list[str],
    list[tuple[str, str]],
]:
    if not SHOWCASE_PAGE.exists():
        return [], [], []
    page_refs: list[tuple[str, str]] = []
    missing_attrs: list[str] = []
    widget_refs: list[tuple[str, str]] = []
    text = SHOWCASE_PAGE.read_text()
    for attrs in LIVING_BOOK_PAGE_REF_RE.findall(text):
        capability_id = html_attr(attrs, "data-capability-id")
        page_ref = html_attr(attrs, "data-page-ref")
        if capability_id and page_ref:
            page_refs.append((capability_id, page_ref))
        else:
            missing_attrs.append(attrs.strip()[:120])
    for attrs in LIVING_BOOK_WIDGET_REF_RE.findall(text):
        capability_id = html_attr(attrs, "data-capability-id")
        widget_id = html_attr(attrs, "data-widget-id")
        if capability_id and widget_id:
            widget_refs.append((capability_id, widget_id))
        else:
            missing_attrs.append(attrs.strip()[:120])
    return page_refs, missing_attrs, widget_refs


def living_book_refs(item: dict) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    capability_id = item.get("id")
    page_refs: set[tuple[str, str]] = set()
    widget_refs: set[tuple[str, str]] = set()
    if not capability_id:
        return page_refs, widget_refs
    for entry in item.get("living_book_refs", []):
        if not isinstance(entry, dict):
            continue
        page_ref = entry.get("page")
        if not page_ref:
            continue
        page_refs.add((capability_id, page_ref))
        for widget_id in entry.get("widget_ids", []) or []:
            widget_refs.add((capability_id, widget_id))
    return page_refs, widget_refs


def widgets_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(WIDGET_PANEL_RE.findall(path.read_text()))


def widget_paths() -> dict[str, Path]:
    return {
        path.stem: path
        for path in sorted((ROOT / "site" / "widgets").glob("**/*.js"))
    }


def theorem_ids_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(THEOREM_ATTR_RE.findall(path.read_text()))


def showcase_refs_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(SHOWCASE_REF_RE.findall(path.read_text()))


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


def page_paper_entries() -> tuple[list[tuple[str, str]], list[str], list[tuple[str, str, str]]]:
    if not SHOWCASE_PAGE.exists():
        return [], [], []
    pairs: list[tuple[str, str]] = []
    missing_attrs: list[str] = []
    paths: list[tuple[str, str, str]] = []
    for attrs in PAPER_REF_RE.findall(SHOWCASE_PAGE.read_text()):
        paper_ref = html_attr(attrs, "data-paper-ref")
        paper_id = html_attr(attrs, "data-paper-id")
        capability_id = html_attr(attrs, "data-capability-id")
        if paper_ref and paper_id and capability_id:
            pairs.append((capability_id, paper_id))
            paths.append((capability_id, paper_id, paper_ref))
        elif paper_ref:
            missing_attrs.append(paper_ref)
    return pairs, missing_attrs, paths


def main() -> int:
    data = load_yaml(SHOWCASE)
    capabilities = data.get("capabilities", [])
    statuses = theorem_statuses()
    papers = paper_index()
    known_dictionary_ids = dictionary_ids()
    known_widgets = widget_paths()
    local_lean_modules = lean_modules_by_name()
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
        page_text = SHOWCASE_PAGE.read_text()
        if f'data-widget="{SHOWCASE_MATRIX_WIDGET_ID}"' not in page_text:
            failures.append(
                f"showcase page must mount {SHOWCASE_MATRIX_WIDGET_ID}"
            )
        if SHOWCASE_MATRIX_SCRIPT not in page_text:
            failures.append(
                f"showcase page must import {SHOWCASE_MATRIX_SCRIPT}"
            )
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
        page_roles = page_role_pairs()
        role_duplicates = sorted(
            {pair for pair in page_roles if page_roles.count(pair) > 1}
        )
        if role_duplicates:
            failures.append(f"duplicate page portfolio roles: {role_duplicates}")
        expected_roles = {
            (item.get("id"), role)
            for item in capabilities
            if item.get("id") and isinstance(item.get("portfolio_roles", []), list)
            for role in item.get("portfolio_roles", [])
        }
        page_role_set = set(page_roles)
        missing_roles = sorted(expected_roles - page_role_set)
        unknown_roles_on_page = sorted(page_role_set - expected_roles)
        if missing_roles:
            failures.append(f"portfolio roles missing from page: {missing_roles}")
        if unknown_roles_on_page:
            failures.append(
                f"unknown page portfolio roles: {unknown_roles_on_page}"
            )
        page_claims, claim_refs_without_attrs, page_claim_values = page_claim_field_entries()
        if claim_refs_without_attrs:
            failures.append(
                "page claim refs missing data-capability-id or data-claim-field: "
                f"{sorted(claim_refs_without_attrs)}"
            )
        claim_duplicates = sorted(
            {pair for pair in page_claims if page_claims.count(pair) > 1}
        )
        if claim_duplicates:
            failures.append(f"duplicate page claim refs: {claim_duplicates}")
        expected_claims = {
            (item.get("id"), field)
            for item in capabilities
            if item.get("id")
            for field in PAGE_CLAIM_FIELDS
        }
        page_claim_set = set(page_claims)
        missing_claims = sorted(expected_claims - page_claim_set)
        unknown_claims = sorted(page_claim_set - expected_claims)
        if missing_claims:
            failures.append(f"claim fields missing from page: {missing_claims}")
        if unknown_claims:
            failures.append(f"unknown page claim fields: {unknown_claims}")
        manifest_by_id = {
            item.get("id"): item
            for item in capabilities
            if item.get("id")
        }
        for capability_id, field, page_value in page_claim_values:
            expected_value = str(manifest_by_id.get(capability_id, {}).get(field, ""))
            if page_value != expected_value:
                failures.append(
                    f"{capability_id}: page {field} text {page_value!r} "
                    f"does not match manifest {expected_value!r}"
                )
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
        page_dictionaries = page_dictionary_pairs()
        dictionary_duplicates = sorted(
            {pair for pair in page_dictionaries if page_dictionaries.count(pair) > 1}
        )
        if dictionary_duplicates:
            failures.append(
                f"duplicate page dictionary refs: {dictionary_duplicates}"
            )
        expected_dictionaries = {
            (item.get("id"), dictionary_id)
            for item in capabilities
            if item.get("id") and isinstance(item.get("dictionary_ids", []), list)
            for dictionary_id in item.get("dictionary_ids", [])
        }
        page_dictionary_set = set(page_dictionaries)
        missing_dictionaries = sorted(expected_dictionaries - page_dictionary_set)
        unknown_dictionaries = sorted(page_dictionary_set - expected_dictionaries)
        if missing_dictionaries:
            failures.append(
                f"dictionary refs missing from page: {missing_dictionaries}"
            )
        if unknown_dictionaries:
            failures.append(
                f"unknown page dictionary refs: {unknown_dictionaries}"
            )
        page_living_refs, living_refs_without_attrs, page_living_widgets = page_living_book_entries()
        if living_refs_without_attrs:
            failures.append(
                "page Living Book refs missing data-capability-id or "
                f"data-page-ref/data-widget-id: {sorted(living_refs_without_attrs)}"
            )
        expected_living_refs: set[tuple[str, str]] = set()
        expected_living_widgets: set[tuple[str, str]] = set()
        for item in capabilities:
            item_pages, item_widgets = living_book_refs(item)
            expected_living_refs.update(item_pages)
            expected_living_widgets.update(item_widgets)
        page_living_set = set(page_living_refs)
        missing_living_refs = sorted(expected_living_refs - page_living_set)
        unknown_living_refs = sorted(page_living_set - expected_living_refs)
        if missing_living_refs:
            failures.append(
                f"Living Book refs missing from page: {missing_living_refs}"
            )
        if unknown_living_refs:
            failures.append(
                f"unknown page Living Book refs: {unknown_living_refs}"
            )
        living_widget_duplicates = sorted(
            {pair for pair in page_living_widgets if page_living_widgets.count(pair) > 1}
        )
        if living_widget_duplicates:
            failures.append(
                f"duplicate page Living Book widget refs: {living_widget_duplicates}"
            )
        page_living_widget_set = set(page_living_widgets)
        missing_living_widgets = sorted(expected_living_widgets - page_living_widget_set)
        unknown_living_widgets = sorted(page_living_widget_set - expected_living_widgets)
        if missing_living_widgets:
            failures.append(
                f"Living Book widget refs missing from page: {missing_living_widgets}"
            )
        if unknown_living_widgets:
            failures.append(
                f"unknown page Living Book widget refs: {unknown_living_widgets}"
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
        page_papers, paper_refs_without_attrs, page_paper_paths = page_paper_entries()
        if paper_refs_without_attrs:
            failures.append(
                "page paper refs missing data-capability-id or data-paper-id: "
                f"{sorted(paper_refs_without_attrs)}"
            )
        paper_duplicates = sorted(
            {pair for pair in page_papers if page_papers.count(pair) > 1}
        )
        if paper_duplicates:
            failures.append(f"duplicate page paper refs: {paper_duplicates}")
        expected_papers = {
            (item.get("id"), paper_id)
            for item in capabilities
            if item.get("id") and isinstance(item.get("paper_ids", []), list)
            for paper_id in item.get("paper_ids", [])
        }
        page_paper_set = set(page_papers)
        missing_papers = sorted(expected_papers - page_paper_set)
        unknown_papers = sorted(page_paper_set - expected_papers)
        if missing_papers:
            failures.append(f"paper refs missing from page: {missing_papers}")
        if unknown_papers:
            failures.append(f"unknown page paper refs: {unknown_papers}")
        for capability_id, paper_id, paper_ref in page_paper_paths:
            paper_path = path_for_paper_id(paper_id)
            if paper_path is None:
                continue
            expected_ref = str(paper_path.relative_to(ROOT))
            if paper_ref != expected_ref:
                failures.append(
                    f"{capability_id}: paper {paper_id} page ref {paper_ref} "
                    f"does not match {expected_ref}"
                )

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
        living_refs = item.get("living_book_refs", [])
        roles = item.get("portfolio_roles", [])
        proof_provenance_kind = item.get("proof_provenance_kind")

        if not theorem_ids:
            failures.append(f"{capability_id}: must advertise at least one theorem id")
        if not paper_ids:
            failures.append(f"{capability_id}: must cite at least one paper id")
        if not refs:
            failures.append(f"{capability_id}: must cite at least one source ref")
        if not isinstance(executable_refs, list) or not executable_refs:
            failures.append(f"{capability_id}: must cite at least one executable ref")
            executable_refs = []
        if not isinstance(living_refs, list) or not living_refs:
            failures.append(f"{capability_id}: must cite at least one Living Book ref")
            living_refs = []
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
        if not isinstance(proof_provenance_kind, str) or not proof_provenance_kind:
            failures.append(f"{capability_id}: must declare proof_provenance_kind")
        elif proof_provenance_kind not in ALLOWED_PROOF_PROVENANCE_KINDS:
            failures.append(
                f"{capability_id}: unknown proof_provenance_kind {proof_provenance_kind}"
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

        seen_living_pages: list[str] = []
        for living_ref in living_refs:
            if not isinstance(living_ref, dict):
                failures.append(f"{capability_id}: Living Book ref must be a mapping")
                continue
            page_ref = living_ref.get("page")
            if not isinstance(page_ref, str) or not page_ref:
                failures.append(f"{capability_id}: Living Book ref missing page")
                continue
            seen_living_pages.append(page_ref)
            local_page = Path(page_ref)
            page_path = ROOT / local_page
            if local_page.is_absolute() or ".." in local_page.parts:
                failures.append(f"{capability_id}: unsafe Living Book ref {page_ref}")
                continue
            if local_page.parts[0] != "site":
                failures.append(
                    f"{capability_id}: Living Book ref {page_ref} must live under site/"
                )
            if page_path.suffix != ".qmd":
                failures.append(
                    f"{capability_id}: Living Book page ref {page_ref} must be a .qmd file"
                )
            if not page_path.exists():
                failures.append(f"{capability_id}: missing Living Book ref {page_ref}")
                continue
            if capability_id not in showcase_refs_on_page(page_path):
                failures.append(
                    f"{capability_id}: Living Book page {page_ref} must carry data-showcase-ref=\"{capability_id}\""
                )
            widget_ids = living_ref.get("widget_ids", []) or []
            if not isinstance(widget_ids, list):
                failures.append(f"{capability_id}: widget_ids for {page_ref} must be a list")
                widget_ids = []
            duplicate_widgets = sorted(
                {widget_id for widget_id in widget_ids if widget_ids.count(widget_id) > 1}
            )
            if duplicate_widgets:
                failures.append(
                    f"{capability_id}: duplicate Living Book widgets for {page_ref}: {duplicate_widgets}"
                )
            page_widgets = widgets_on_page(page_path)
            for widget_id in widget_ids:
                if not isinstance(widget_id, str) or not widget_id:
                    failures.append(f"{capability_id}: empty Living Book widget id for {page_ref}")
                elif widget_id not in known_widgets:
                    failures.append(
                        f"{capability_id}: unknown Living Book widget id {widget_id}"
                    )
                elif widget_id not in page_widgets:
                    failures.append(
                        f"{capability_id}: Living Book page {page_ref} does not mount widget {widget_id}"
                    )
            if not widget_ids and set(theorem_ids).isdisjoint(theorem_ids_on_page(page_path)):
                failures.append(
                    f"{capability_id}: Living Book page {page_ref} must carry at least one advertised theorem id or a widget"
                )
        duplicate_living_pages = sorted(
            {page_ref for page_ref in seen_living_pages if seen_living_pages.count(page_ref) > 1}
        )
        if duplicate_living_pages:
            failures.append(
                f"{capability_id}: duplicate Living Book page refs {duplicate_living_pages}"
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
            elif not paper_source_ref_backed(ref, paper_ids, papers, local_lean_modules):
                failures.append(
                    f"{capability_id}: source ref {ref} is not backed by cited "
                    "paper source trails or Lean sidecar imports"
                )

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
