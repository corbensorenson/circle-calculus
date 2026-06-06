from __future__ import annotations

import sys

from site_lib import GENERATED, load_json


def ids_from(items: list[dict] | list[str] | str | None) -> set[str]:
    if not items:
        return set()
    if isinstance(items, str):
        return {items}
    ids: set[str] = set()
    for item in items:
        if isinstance(item, dict):
            item_id = item.get("id", "")
        else:
            item_id = str(item)
        if item_id:
            ids.add(item_id)
    return ids


def load_indexes() -> tuple[dict, dict, dict, dict, dict]:
    theorem_manifest = load_json(GENERATED / "theorem_manifest.json")
    dictionary = load_json(GENERATED / "dictionary.json")
    paper_index = load_json(GENERATED / "paper_index.json")
    widget_index = load_json(GENERATED / "widget_index.json")
    glyph_index = load_json(GENERATED / "glyph_index.json")
    return theorem_manifest, dictionary, paper_index, widget_index, glyph_index


def main() -> int:
    failures: list[str] = []
    theorem_manifest, dictionary, paper_index, widget_index, glyph_index = load_indexes()

    theorems = {item["id"]: item for item in theorem_manifest.get("theorems", [])}
    entries = {item["id"]: item for item in dictionary.get("entries", [])}
    papers = {item["id"]: item for item in paper_index.get("papers", [])}
    widgets = {item["id"]: item for item in widget_index.get("widgets", [])}
    glyphs = {item["id"]: item for item in glyph_index.get("glyphs", [])}

    for theorem in theorems.values():
        theorem_id = theorem["id"]
        for entry_id in theorem.get("dictionary_dependencies", []):
            entry = entries.get(entry_id)
            if entry is None:
                failures.append(f"theorem {theorem_id}: unknown dictionary dependency {entry_id}")
                continue
            if theorem_id not in ids_from(entry.get("used_by_theorems")):
                failures.append(f"theorem {theorem_id}: missing dictionary backlink from {entry_id}")
        for paper_ref in theorem.get("used_by_papers", []):
            paper_id = paper_ref.get("id", "")
            paper = papers.get(paper_id)
            if paper is None:
                failures.append(f"theorem {theorem_id}: backlink to unknown paper {paper_id}")
                continue
            if theorem_id not in paper.get("theorem_ids", []):
                failures.append(f"theorem {theorem_id}: paper backlink {paper_id} is not reciprocal")
            if paper_ref.get("path", "") != paper.get("path", ""):
                failures.append(f"theorem {theorem_id}: paper backlink {paper_id} path drift")

    for paper in papers.values():
        paper_id = paper["id"]
        for theorem_id in paper.get("theorem_ids", []):
            theorem = theorems.get(theorem_id)
            if theorem is None:
                failures.append(f"paper {paper_id}: unknown theorem id {theorem_id}")
                continue
            if paper_id not in ids_from(theorem.get("used_by_papers")):
                failures.append(f"paper {paper_id}: missing theorem backlink from {theorem_id}")
        for entry_id in paper.get("dictionary_ids", []):
            entry = entries.get(entry_id)
            if entry is None:
                failures.append(f"paper {paper_id}: unknown dictionary id {entry_id}")
                continue
            if paper_id not in ids_from(entry.get("used_by_papers")):
                failures.append(f"paper {paper_id}: missing dictionary backlink from {entry_id}")

    for entry in entries.values():
        entry_id = entry["id"]
        for theorem_ref in entry.get("used_by_theorems", []):
            theorem_id = theorem_ref.get("id", "")
            theorem = theorems.get(theorem_id)
            if theorem is None:
                failures.append(f"dictionary {entry_id}: backlink to unknown theorem {theorem_id}")
                continue
            if entry_id not in theorem.get("dictionary_dependencies", []):
                failures.append(f"dictionary {entry_id}: theorem backlink {theorem_id} is not reciprocal")
            if theorem_ref.get("status", "") != theorem.get("canonical_status", theorem.get("status", "")):
                failures.append(f"dictionary {entry_id}: theorem backlink {theorem_id} status drift")
            if theorem_ref.get("lean_name", "") != theorem.get("lean_name", ""):
                failures.append(f"dictionary {entry_id}: theorem backlink {theorem_id} Lean-name drift")

        for paper_ref in entry.get("used_by_papers", []):
            paper_id = paper_ref.get("id", "")
            paper = papers.get(paper_id)
            if paper is None:
                failures.append(f"dictionary {entry_id}: backlink to unknown paper {paper_id}")
                continue
            if entry_id not in paper.get("dictionary_ids", []):
                failures.append(f"dictionary {entry_id}: paper backlink {paper_id} is not reciprocal")
            if paper_ref.get("path", "") != paper.get("path", ""):
                failures.append(f"dictionary {entry_id}: paper backlink {paper_id} path drift")

        for widget_ref in entry.get("used_by_widgets", []):
            widget_id = widget_ref.get("id", "")
            widget = widgets.get(widget_id)
            if widget is None:
                failures.append(f"dictionary {entry_id}: backlink to unknown widget {widget_id}")
                continue
            if entry_id not in widget.get("dictionary_ids", []):
                failures.append(f"dictionary {entry_id}: widget backlink {widget_id} is not reciprocal")
            if widget_ref.get("path", "") != widget.get("path", ""):
                failures.append(f"dictionary {entry_id}: widget backlink {widget_id} path drift")

        for glyph_ref in entry.get("used_by_glyphs", []):
            glyph_id = glyph_ref.get("id", "")
            glyph = glyphs.get(glyph_id)
            if glyph is None:
                failures.append(f"dictionary {entry_id}: backlink to unknown glyph {glyph_id}")
                continue
            if entry_id not in glyph.get("dictionary_ids", []):
                failures.append(f"dictionary {entry_id}: glyph backlink {glyph_id} is not reciprocal")
            if glyph_ref.get("theorem_id", "") != glyph.get("theorem_id", ""):
                failures.append(f"dictionary {entry_id}: glyph backlink {glyph_id} theorem drift")
            if glyph_ref.get("status", "") != glyph.get("canonical_status", ""):
                failures.append(f"dictionary {entry_id}: glyph backlink {glyph_id} status drift")

    for widget in widgets.values():
        widget_id = widget["id"]
        for entry_id in widget.get("dictionary_ids", []):
            entry = entries.get(entry_id)
            if entry is None:
                failures.append(f"widget {widget_id}: unknown dictionary id {entry_id}")
                continue
            if widget_id not in ids_from(entry.get("used_by_widgets")):
                failures.append(f"widget {widget_id}: missing dictionary backlink from {entry_id}")

    for glyph in glyphs.values():
        glyph_id = glyph["id"]
        theorem_id = glyph.get("theorem_id", "")
        theorem = theorems.get(theorem_id)
        if theorem is None:
            failures.append(f"glyph {glyph_id}: unknown theorem id {theorem_id}")
        else:
            if glyph.get("lean_name", "") != theorem.get("lean_name", ""):
                failures.append(f"glyph {glyph_id}: Lean name does not match theorem {theorem_id}")
            if glyph.get("canonical_status", "") != theorem.get("canonical_status", ""):
                failures.append(f"glyph {glyph_id}: status does not match theorem {theorem_id}")
        for entry_id in glyph.get("dictionary_ids", []):
            entry = entries.get(entry_id)
            if entry is None:
                failures.append(f"glyph {glyph_id}: unknown dictionary id {entry_id}")
                continue
            if glyph_id not in ids_from(entry.get("used_by_glyphs")):
                failures.append(f"glyph {glyph_id}: missing dictionary backlink from {entry_id}")

    if failures:
        print("site data backlink failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site data backlinks ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
