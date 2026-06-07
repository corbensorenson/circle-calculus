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
        {
            "id": "sphere_grid_placeholder",
            "path": "site/widgets/S2/sphere_grid_placeholder.js",
            "theorem_ids": [],
            "dictionary_ids": ["S2-0001", "S2-0002"],
            "python_reference": "",
        },
        {
            "id": "hopf_placeholder",
            "path": "site/widgets/S3/hopf_placeholder.js",
            "theorem_ids": [],
            "dictionary_ids": ["S3H-0001", "S3H-0002"],
            "python_reference": "",
        },
        {
            "id": "seed_rule_diagram_generator",
            "path": "site/widgets/generative/seed_rule_diagram_generator.js",
            "theorem_ids": [
                "CC-T0001",
                "CC-T0002",
                "PHYS-T0005",
                "PHYS-T0012",
                "GEN-T0017",
                "GEN-T0019",
            ],
            "dictionary_ids": [
                "CC-0001",
                "CC-0002",
                "COMMON-0060",
                "COMMON-0061",
                "COMMON-0062",
                "COMMON-0063",
                "COMMON-0064",
                "COMMON-0066",
            ],
            "python_reference": "circle_math.generative.finite_circle_diagram_generator; circle_math.generative.physics_loop_diagram_generator",
        },
    ]
    return {"widgets": widgets}


def add_dictionary_backlinks(
    dictionary: dict,
    theorem_manifest: dict,
    paper_index: dict,
    widget_index: dict,
    glyph_index: dict,
) -> dict:
    entries = [dict(entry) for entry in dictionary.get("entries", [])]
    by_id = {entry["id"]: entry for entry in entries}
    backlink_fields = [
        "used_by_theorems",
        "used_by_papers",
        "used_by_widgets",
        "used_by_glyphs",
    ]
    for entry in entries:
        for field in backlink_fields:
            entry[field] = []

    def add(entry_id: str, field: str, value: dict) -> None:
        entry = by_id.get(entry_id)
        if entry is not None:
            entry[field].append(value)

    for theorem in theorem_manifest.get("theorems", []):
        for entry_id in theorem.get("dictionary_dependencies", []):
            add(
                entry_id,
                "used_by_theorems",
                {
                    "id": theorem.get("id", ""),
                    "name": theorem.get("name", theorem.get("lean_name", "")),
                    "status": theorem.get("canonical_status", theorem.get("status", "")),
                    "lean_name": theorem.get("lean_name", ""),
                },
            )

    for paper in paper_index.get("papers", []):
        for entry_id in paper.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_papers",
                {
                    "id": paper.get("id", ""),
                    "title": paper.get("title", ""),
                    "status": paper.get("status", ""),
                    "path": paper.get("path", ""),
                },
            )

    for widget in widget_index.get("widgets", []):
        for entry_id in widget.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_widgets",
                {
                    "id": widget.get("id", ""),
                    "path": widget.get("path", ""),
                    "python_reference": widget.get("python_reference", ""),
                },
            )

    for glyph in glyph_index.get("glyphs", []):
        for entry_id in glyph.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_glyphs",
                {
                    "id": glyph.get("id", ""),
                    "theorem_id": glyph.get("theorem_id", ""),
                    "status": glyph.get("canonical_status", ""),
                    "status_label": glyph.get("status_label", ""),
                },
            )

    for entry in entries:
        for field in backlink_fields:
            entry[field] = sorted(entry[field], key=lambda item: item.get("id", ""))

    return {"entries": sorted(entries, key=lambda item: item["id"])}


def add_theorem_backlinks(theorem_manifest: dict, paper_index: dict) -> dict:
    theorems = [dict(theorem) for theorem in theorem_manifest.get("theorems", [])]
    by_id = {theorem["id"]: theorem for theorem in theorems}
    for theorem in theorems:
        theorem["used_by_papers"] = []

    for paper in paper_index.get("papers", []):
        for theorem_id in paper.get("theorem_ids", []):
            theorem = by_id.get(theorem_id)
            if theorem is None:
                continue
            theorem["used_by_papers"].append(
                {
                    "id": paper.get("id", ""),
                    "title": paper.get("title", ""),
                    "status": paper.get("status", ""),
                    "path": paper.get("path", ""),
                },
            )

    for theorem in theorems:
        theorem["used_by_papers"] = sorted(
            theorem["used_by_papers"],
            key=lambda item: item.get("id", ""),
        )

    return {"theorems": sorted(theorems, key=lambda item: item["id"])}


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


def export_phase6_targets() -> dict:
    path = ROOT / "manifests" / "phase6_sweep_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_phase7_targets() -> dict:
    path = ROOT / "manifests" / "phase7_physics_generators.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def glyph_status_label(canonical_status: str) -> str:
    if canonical_status == "proved":
        return "Lean-proved"
    if canonical_status == "exploratory":
        return "Exploratory"
    if canonical_status == "blocked":
        return "Blocked"
    if canonical_status == "deferred":
        return "Deferred"
    if canonical_status == "draft":
        return "Draft"
    return "Planned theorem"


def glyph_manifest_paths() -> list[Path]:
    return sorted((ROOT / "manifests" / "glyphs").glob("*.yaml"))


def export_glyph_index(theorem_manifest: dict, dictionary: dict) -> dict:
    theorem_by_id = {item["id"]: item for item in theorem_manifest.get("theorems", [])}
    dictionary_ids = {item["id"] for item in dictionary.get("entries", [])}
    glyphs: list[dict] = []
    for path in glyph_manifest_paths():
        data = load_yaml(path)
        for glyph in data.get("glyphs", []):
            theorem = theorem_by_id.get(glyph.get("theorem_id", ""))
            if theorem is None:
                raise ValueError(f"{repo_relative(path)}: unknown theorem id {glyph.get('theorem_id')}")
            if glyph.get("lean_name") != theorem.get("lean_name"):
                raise ValueError(f"{repo_relative(path)}: Lean name mismatch for {glyph.get('id')}")
            unknown_dictionary_ids = [
                dictionary_id
                for dictionary_id in glyph.get("dictionary_ids", [])
                if dictionary_id not in dictionary_ids
            ]
            if unknown_dictionary_ids:
                raise ValueError(f"{repo_relative(path)}: unknown dictionary ids {unknown_dictionary_ids}")
            item = dict(glyph)
            item["source_manifest"] = repo_relative(path)
            item["original_status"] = theorem.get("original_status", theorem.get("status", "planned"))
            item["canonical_status"] = theorem.get("canonical_status", "planned")
            item["status_label"] = glyph_status_label(item["canonical_status"])
            item["lean_source"] = theorem.get("lean_source", "")
            item["lean_source_line"] = theorem.get("lean_source_line", "")
            glyphs.append(item)
    return {"glyphs": sorted(glyphs, key=lambda item: item["id"])}


def export_all() -> None:
    theorem_manifest = export_theorems()
    base_dictionary = export_dictionary()
    paper_index = export_papers()
    theorem_manifest = add_theorem_backlinks(theorem_manifest, paper_index)
    widget_index = export_widget_index()
    glyph_index = export_glyph_index(theorem_manifest, base_dictionary)
    dictionary = add_dictionary_backlinks(
        base_dictionary,
        theorem_manifest,
        paper_index,
        widget_index,
        glyph_index,
    )
    write_json(GENERATED / "theorem_manifest.json", theorem_manifest)
    write_json(GENERATED / "dictionary.json", dictionary)
    write_json(GENERATED / "dimensions.json", export_dimensions())
    write_json(GENERATED / "paper_index.json", paper_index)
    write_json(GENERATED / "widget_index.json", widget_index)
    write_json(GENERATED / "phase4_targets.json", export_phase4_targets())
    write_json(GENERATED / "phase5_targets.json", export_phase5_targets())
    write_json(GENERATED / "phase6_targets.json", export_phase6_targets())
    write_json(GENERATED / "phase7_targets.json", export_phase7_targets())
    write_json(GENERATED / "glyph_index.json", glyph_index)


def main() -> int:
    export_all()
    print("site data exported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
