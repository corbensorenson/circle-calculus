#!/usr/bin/env python3
"""Generate a manifest-backed theorem evidence graph.

The manifests do not encode formal proof dependencies between Lean theorems.
This graph is therefore a blueprint/evidence graph: theorem ids connect to Lean
declarations, dictionary terms, paper references, and paper reading-order edges.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "site" / "data" / "generated" / "theorem_blueprint_graph.json"
MD_OUT = ROOT / "docs" / "generated" / "THEOREM_BLUEPRINT_GRAPH.md"

DECL_RE = re.compile(r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive)\s+([A-Za-z0-9_'.]+)")


def repo_relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


def theorem_manifest_paths() -> list[Path]:
    skip = {
        "paper_manifest.yaml",
        "dimension_index.yaml",
        "capability_showcase.yaml",
        "theorem_manifest.schema.json",
    }
    return [
        path
        for path in sorted((ROOT / "manifests").glob("**/*.yaml"))
        if path.name not in skip
    ]


def lean_sources() -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "Circle").glob("**/*.lean")):
        namespace_stack: list[str] = []
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("namespace "):
                namespace_stack.append(stripped.split(None, 1)[1])
                continue
            if stripped == "end" or stripped.startswith("end "):
                if namespace_stack:
                    namespace_stack.pop()
                continue
            match = DECL_RE.match(line)
            if not match:
                continue
            local = match.group(1)
            full = ".".join(namespace_stack + [local]) if namespace_stack else local
            sources[full] = {"path": repo_relative(path), "line": line_no}
    return sources


def paper_manifest() -> dict[str, Any]:
    path = ROOT / "manifests" / "paper_manifest.yaml"
    return load_yaml(path) if path.exists() else {"papers": []}


def paper_id_from_ref(ref: str) -> str:
    return ref.split(".", 1)[0]


def add_node(nodes: dict[str, dict[str, Any]], node_id: str, kind: str, **fields: Any) -> None:
    nodes.setdefault(node_id, {"id": node_id, "kind": kind}).update(fields)


def main() -> int:
    lean = lean_sources()
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    theorem_by_id: dict[str, dict[str, Any]] = {}

    for path in theorem_manifest_paths():
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if not theorem_id:
                continue
            theorem_by_id[theorem_id] = theorem
            add_node(
                nodes,
                theorem_id,
                "theorem",
                name=theorem.get("name", ""),
                status=theorem.get("status", ""),
                lean_name=theorem.get("lean_name", ""),
                source_manifest=repo_relative(path),
            )
            lean_name = theorem.get("lean_name", "")
            if lean_name:
                source = lean.get(lean_name, {})
                add_node(
                    nodes,
                    f"lean:{lean_name}",
                    "lean_declaration",
                    lean_name=lean_name,
                    source=source.get("path", ""),
                    line=source.get("line", 0),
                )
                edges.append(
                    {"source": theorem_id, "target": f"lean:{lean_name}", "kind": "declares"}
                )
            for dictionary_id in theorem.get("dictionary_dependencies", []):
                add_node(nodes, f"dict:{dictionary_id}", "dictionary", dictionary_id=dictionary_id)
                edges.append(
                    {
                        "source": theorem_id,
                        "target": f"dict:{dictionary_id}",
                        "kind": "uses_dictionary",
                    }
                )
            for paper_ref in theorem.get("paper_refs", []):
                paper_id = paper_id_from_ref(str(paper_ref))
                add_node(nodes, f"paper:{paper_id}", "paper", paper_id=paper_id)
                edges.append(
                    {"source": theorem_id, "target": f"paper:{paper_id}", "kind": "cited_by_paper"}
                )

    paper_edges = 0
    paper_theorem_counts: dict[str, int] = {}
    for paper in paper_manifest().get("papers", []):
        paper_id = paper.get("id")
        theorem_ids = [tid for tid in paper.get("theorem_ids", []) if tid in theorem_by_id]
        if not paper_id:
            continue
        add_node(nodes, f"paper:{paper_id}", "paper", paper_id=paper_id, title=paper.get("title", ""))
        paper_theorem_counts[paper_id] = len(theorem_ids)
        for theorem_id in theorem_ids:
            edges.append(
                {"source": f"paper:{paper_id}", "target": theorem_id, "kind": "contains_theorem"}
            )
        for left, right in zip(theorem_ids, theorem_ids[1:]):
            edges.append(
                {
                    "source": left,
                    "target": right,
                    "kind": "paper_reading_order",
                }
            )
            paper_edges += 1

    status_counts: dict[str, int] = defaultdict(int)
    for theorem in theorem_by_id.values():
        status_counts[str(theorem.get("status", ""))] += 1

    graph = {
        "schema_id": "circle_calculus.theorem_blueprint_graph.v0",
        "kind": "manifest_evidence_graph",
        "not_claimed": (
            "Edges are manifest evidence and paper reading-order links, not formal "
            "Lean proof-dependency edges unless a future manifest field says so."
        ),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "theorem_count": len(theorem_by_id),
        "status_counts": dict(sorted(status_counts.items())),
        "paper_theorem_counts": dict(sorted(paper_theorem_counts.items())),
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "edges": sorted(edges, key=lambda item: (item["source"], item["kind"], item["target"])),
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")

    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Generated Theorem Blueprint Graph",
        "",
        "Generated by `scripts/generate_theorem_blueprint_graph.py`.",
        "",
        graph["not_claimed"],
        "",
        "## Summary",
        "",
        f"- Theorems: `{graph['theorem_count']}`",
        f"- Nodes: `{graph['node_count']}`",
        f"- Edges: `{graph['edge_count']}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in graph["status_counts"].items():
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Largest Paper Theorem Spines", ""])
    for paper_id, count in sorted(paper_theorem_counts.items(), key=lambda item: (-item[1], item[0]))[:20]:
        lines.append(f"- `{paper_id}`: `{count}` theorem ids")
    lines.extend(["", "## Data Artifact", "", "- `site/data/generated/theorem_blueprint_graph.json`"])
    MD_OUT.write_text("\n".join(lines).rstrip() + "\n")

    print(f"wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
