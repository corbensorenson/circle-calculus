from __future__ import annotations

import re
from pathlib import Path

from site_lib import GENERATED, ROOT, load_yaml, repo_relative, write_json


DECL_RE = re.compile(r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive)\s+([A-Za-z0-9_'.]+)")

STATUS_MAP = {
    "proved": "proved",
    "lean_proved": "proved",
    "exploratory_python": "exploratory",
    "stated": "planned",
    "lean_stated": "planned",
    "planned": "planned",
    "paper_draft": "draft",
    "paper_complete": "draft",
    "blocked": "blocked",
    "deferred": "deferred",
}


def canonical_status(status: str) -> str:
    return STATUS_MAP.get(status, "planned")


def theorem_manifest_paths() -> list[Path]:
    candidates = sorted((ROOT / "manifests").glob("**/*.yaml"))
    return [path for path in candidates if path.name not in {"paper_manifest.yaml", "dimension_index.yaml"}]


def lean_declaration_sources() -> dict[str, dict[str, object]]:
    sources: dict[str, dict[str, object]] = {}
    for path in sorted((ROOT / "Circle").glob("**/*.lean")):
        namespace_stack: list[str] = []
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("namespace "):
                namespace_stack.append(stripped.split(None, 1)[1])
                continue
            if stripped == "end" or stripped.startswith("end "):
                if namespace_stack:
                    namespace_stack.pop()
                continue
            match = DECL_RE.match(line)
            if match:
                local = match.group(1)
                full = ".".join(namespace_stack + [local]) if namespace_stack else local
                sources[full] = {
                    "path": repo_relative(path),
                    "line": line_number,
                }
    return sources


def export_theorems() -> dict:
    theorems: list[dict] = []
    seen: set[str] = set()
    lean_sources = lean_declaration_sources()
    for path in theorem_manifest_paths():
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if not theorem_id or theorem_id in seen:
                continue
            seen.add(theorem_id)
            item = dict(theorem)
            item["source_manifest"] = repo_relative(path)
            item["original_status"] = item.get("status", "")
            item["canonical_status"] = canonical_status(item.get("status", "planned"))
            lean_source = lean_sources.get(item.get("lean_name", ""))
            if lean_source:
                item["lean_source"] = lean_source["path"]
                item["lean_source_line"] = lean_source["line"]
            theorems.append(item)
    return {"theorems": sorted(theorems, key=lambda item: item["id"])}


def dictionary_paths() -> list[Path]:
    paths = [ROOT / "dictionary" / "circle_dictionary.yaml"]
    paths.extend(sorted((ROOT / "dictionary" / "dimensions").glob("*.yaml")))
    return [path for path in paths if path.exists()]


def export_dictionary() -> dict:
    entries: list[dict] = []
    seen: set[str] = set()
    for path in dictionary_paths():
        data = load_yaml(path)
        for entry in data.get("entries", []):
            entry_id = entry.get("id")
            if not entry_id or entry_id in seen:
                continue
            seen.add(entry_id)
            item = dict(entry)
            item["source_dictionary"] = repo_relative(path)
            entries.append(item)
    return {"entries": sorted(entries, key=lambda item: item["id"])}


def export_dimensions() -> dict:
    path = ROOT / "manifests" / "dimensions" / "dimension_index.yaml"
    if not path.exists():
        return {"dimensions": []}
    data = load_yaml(path)
    return {"dimensions": data.get("dimensions", [])}


def paper_path_for_id(paper_id: str) -> str:
    for path in sorted((ROOT / "papers").glob("**/*.md")):
        if path.stem == paper_id:
            return repo_relative(path)
    return ""


def export_papers() -> dict:
    path = ROOT / "manifests" / "paper_manifest.yaml"
    if not path.exists():
        return {"papers": []}
    data = load_yaml(path)
    papers: list[dict] = []
    for paper in data.get("papers", []):
        item = dict(paper)
        item["path"] = paper_path_for_id(item.get("id", ""))
        papers.append(item)
    return {"papers": papers}


def export_widget_index() -> dict:
    widgets = [
        {
            "id": "finite_circle_rotator",
            "path": "site/widgets/S1/finite_circle_rotator.js",
            "theorem_ids": [],
            "dictionary_ids": ["CC-0001", "CC-0002"],
            "python_reference": "circle_math.finite.Circle.node",
        },
        {
            "id": "rotation_composition",
            "path": "site/widgets/S1/rotation_composition.js",
            "theorem_ids": ["CC-T0002"],
            "dictionary_ids": ["CC-0101"],
            "python_reference": "circle_math.finite.Circle.rot",
        },
        {
            "id": "coil_orbit_explorer",
            "path": "site/widgets/S1/coil_orbit_explorer.js",
            "theorem_ids": ["CC-T0005"],
            "dictionary_ids": ["CC-0201", "CC-0202", "CC-0205"],
            "python_reference": "circle_math.finite.Circle.orbit",
        },
        {
            "id": "period_gcd_visualizer",
            "path": "site/widgets/S1/period_gcd_visualizer.js",
            "theorem_ids": ["CC-T0006"],
            "dictionary_ids": ["CC-0205", "CC-0207", "CC-0208"],
            "python_reference": "circle_math.finite.Circle.orbit_decomposition",
        },
        {
            "id": "prime_full_coil_explorer",
            "path": "site/widgets/S1/prime_full_coil_explorer.js",
            "theorem_ids": ["CC-T0007"],
            "dictionary_ids": ["CC-0206"],
            "python_reference": "circle_math.finite.Circle.is_full_coil",
        },
        {
            "id": "winding_lift_explorer",
            "path": "site/widgets/S1/winding_lift_explorer.js",
            "theorem_ids": ["CC-T0009"],
            "dictionary_ids": ["CC-0301"],
            "python_reference": "circle_math.winding.lift",
        },
    ]
    return {"widgets": widgets}


def export_phase4_targets() -> dict:
    path = ROOT / "manifests" / "phase4_theorem_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_phase5_targets() -> dict:
    path = ROOT / "manifests" / "phase5_edge_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_all() -> None:
    write_json(GENERATED / "theorem_manifest.json", export_theorems())
    write_json(GENERATED / "dictionary.json", export_dictionary())
    write_json(GENERATED / "dimensions.json", export_dimensions())
    write_json(GENERATED / "paper_index.json", export_papers())
    write_json(GENERATED / "widget_index.json", export_widget_index())
    write_json(GENERATED / "phase4_targets.json", export_phase4_targets())
    write_json(GENERATED / "phase5_targets.json", export_phase5_targets())


def main() -> int:
    export_all()
    print("site data exported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
