from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from site_lib import GENERATED, ROOT, load_json


RUNTIME_LINK_GUARD_REQUIREMENTS = [
    ("repo path guard", "function looksLikeRepoPath(path)"),
    ("GitHub helper guard", "if (!looksLikeRepoPath(path)) return \"\";"),
    ("non-path refs stay text", "document.createTextNode(text)"),
]


def validate_repo_path(failures: list[str], owner: str, label: str, raw_path: str) -> None:
    if not raw_path:
        return
    if raw_path.startswith(("http://", "https://", "mailto:")):
        return
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        failures.append(f"{owner}: unsafe {label} path {raw_path}")
        return
    if not (ROOT / path).exists():
        failures.append(f"{owner}: missing {label} path {raw_path}")


def validate_many(
    failures: list[str],
    owner: str,
    label: str,
    values: Iterable[str],
) -> None:
    for value in values:
        validate_repo_path(failures, owner, label, value)


def validate_runtime_link_guard(failures: list[str]) -> None:
    path = ROOT / "site" / "widgets" / "shared" / "widget_base.js"
    text = path.read_text()
    for label, needle in RUNTIME_LINK_GUARD_REQUIREMENTS:
        if needle not in text:
            failures.append(f"site/widgets/shared/widget_base.js: missing {label}")


def main() -> int:
    failures: list[str] = []
    validate_runtime_link_guard(failures)

    theorem_manifest = load_json(GENERATED / "theorem_manifest.json")
    dictionary = load_json(GENERATED / "dictionary.json")
    paper_index = load_json(GENERATED / "paper_index.json")
    widget_index = load_json(GENERATED / "widget_index.json")
    glyph_index = load_json(GENERATED / "glyph_index.json")
    target_indexes = [
        load_json(GENERATED / "phase4_targets.json"),
        load_json(GENERATED / "phase5_targets.json"),
        load_json(GENERATED / "phase6_targets.json"),
    ]

    theorem_ids = {item["id"] for item in theorem_manifest.get("theorems", [])}
    dictionary_ids = {item["id"] for item in dictionary.get("entries", [])}
    paper_ids = {item["id"] for item in paper_index.get("papers", [])}
    widget_ids = {item["id"] for item in widget_index.get("widgets", [])}
    glyph_ids = {item["id"] for item in glyph_index.get("glyphs", [])}

    for theorem in theorem_manifest.get("theorems", []):
        owner = f"theorem {theorem['id']}"
        validate_repo_path(failures, owner, "source_manifest", theorem.get("source_manifest", ""))
        validate_repo_path(failures, owner, "lean_source", theorem.get("lean_source", ""))
        if theorem.get("canonical_status") == "proved" and theorem.get("lean_name") and not theorem.get("lean_source"):
            failures.append(f"{owner}: proved theorem with Lean name lacks lean_source")
        for entry_id in theorem.get("dictionary_dependencies", []):
            if entry_id not in dictionary_ids:
                failures.append(f"{owner}: unknown dictionary dependency {entry_id}")

    for entry in dictionary.get("entries", []):
        owner = f"dictionary {entry['id']}"
        validate_repo_path(failures, owner, "source_dictionary", entry.get("source_dictionary", ""))
        for item in entry.get("used_by_theorems", []):
            if item.get("id") not in theorem_ids:
                failures.append(f"{owner}: backlink to unknown theorem {item.get('id')}")
        for item in entry.get("used_by_papers", []):
            if item.get("id") not in paper_ids:
                failures.append(f"{owner}: backlink to unknown paper {item.get('id')}")
            validate_repo_path(failures, owner, "paper backlink", item.get("path", ""))
        for item in entry.get("used_by_widgets", []):
            if item.get("id") not in widget_ids:
                failures.append(f"{owner}: backlink to unknown widget {item.get('id')}")
            validate_repo_path(failures, owner, "widget backlink", item.get("path", ""))
        for item in entry.get("used_by_glyphs", []):
            if item.get("id") not in glyph_ids:
                failures.append(f"{owner}: backlink to unknown glyph {item.get('id')}")

    for paper in paper_index.get("papers", []):
        owner = f"paper {paper['id']}"
        validate_repo_path(failures, owner, "paper", paper.get("path", ""))
        validate_repo_path(failures, owner, "sidecar", paper.get("sidecar", ""))
        for theorem_id in paper.get("theorem_ids", []):
            if theorem_id not in theorem_ids:
                failures.append(f"{owner}: unknown theorem id {theorem_id}")
        for entry_id in paper.get("dictionary_ids", []):
            if entry_id not in dictionary_ids:
                failures.append(f"{owner}: unknown dictionary id {entry_id}")

    for widget in widget_index.get("widgets", []):
        owner = f"widget {widget['id']}"
        validate_repo_path(failures, owner, "widget", widget.get("path", ""))
        for theorem_id in widget.get("theorem_ids", []):
            if theorem_id not in theorem_ids:
                failures.append(f"{owner}: unknown theorem id {theorem_id}")
        for entry_id in widget.get("dictionary_ids", []):
            if entry_id not in dictionary_ids:
                failures.append(f"{owner}: unknown dictionary id {entry_id}")

    for glyph in glyph_index.get("glyphs", []):
        owner = f"glyph {glyph['id']}"
        validate_repo_path(failures, owner, "source_manifest", glyph.get("source_manifest", ""))
        validate_repo_path(failures, owner, "lean_source", glyph.get("lean_source", ""))
        validate_many(failures, owner, "paper_ref", glyph.get("paper_refs", []))
        if glyph.get("theorem_id") not in theorem_ids:
            failures.append(f"{owner}: unknown theorem id {glyph.get('theorem_id')}")
        for entry_id in glyph.get("dictionary_ids", []):
            if entry_id not in dictionary_ids:
                failures.append(f"{owner}: unknown dictionary id {entry_id}")

    for index in target_indexes:
        for target in index.get("targets", []):
            owner = f"target {target['id']}"
            validate_many(failures, owner, "paper_ref", target.get("paper_refs", []))
            validate_many(failures, owner, "artifact_ref", target.get("artifact_refs", []))
            promoted = target.get("promoted_theorem_id")
            if promoted and promoted not in theorem_ids:
                failures.append(f"{owner}: unknown promoted theorem id {promoted}")
            for entry_id in target.get("dictionary_dependencies", []):
                if entry_id not in dictionary_ids:
                    failures.append(f"{owner}: unknown dictionary id {entry_id}")

    if failures:
        print("site source link failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site source links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
