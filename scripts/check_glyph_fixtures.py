from __future__ import annotations

import sys

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, DIMENSION_MANIFESTS, ROOT, THEOREM_MANIFEST


GLYPH_MANIFESTS = ROOT / "manifests" / "glyphs"
REQUIRED_FIELDS = {"id", "theorem_id", "lean_name", "dictionary_ids", "paper_refs", "caption"}


def load_dictionary_ids() -> set[str]:
    ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        ids.update(entry["id"] for entry in data.get("entries", []))
    return ids


def load_theorems() -> dict[str, dict]:
    theorems: dict[str, dict] = {}
    for path in [THEOREM_MANIFEST, *sorted(DIMENSION_MANIFESTS.glob("*.yaml"))]:
        data = yaml.safe_load(path.read_text()) or {}
        for theorem in data.get("theorems", []):
            theorems[theorem["id"]] = theorem
    return theorems


def main() -> int:
    dictionary_ids = load_dictionary_ids()
    theorems = load_theorems()
    failures: list[str] = []
    glyph_ids: list[str] = []

    for path in sorted(GLYPH_MANIFESTS.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        for glyph in data.get("glyphs", []):
            glyph_id = glyph.get("id", "<missing id>")
            glyph_ids.append(glyph_id)
            missing = sorted(REQUIRED_FIELDS - set(glyph))
            if missing:
                failures.append(f"{path.relative_to(ROOT)}: {glyph_id} missing {missing}")
                continue
            theorem = theorems.get(glyph["theorem_id"])
            if theorem is None:
                failures.append(f"{path.relative_to(ROOT)}: {glyph_id} unknown theorem id {glyph['theorem_id']}")
            elif theorem.get("lean_name") != glyph["lean_name"]:
                failures.append(
                    f"{path.relative_to(ROOT)}: {glyph_id} Lean name mismatch "
                    f"{glyph['lean_name']} != {theorem.get('lean_name')}"
                )
            for dictionary_id in glyph.get("dictionary_ids", []):
                if dictionary_id not in dictionary_ids:
                    failures.append(f"{path.relative_to(ROOT)}: {glyph_id} unknown dictionary id {dictionary_id}")
            for ref in glyph.get("paper_refs", []):
                if not (ROOT / ref.split("#", 1)[0]).exists():
                    failures.append(f"{path.relative_to(ROOT)}: {glyph_id} missing paper ref {ref}")

    duplicates = sorted({glyph_id for glyph_id in glyph_ids if glyph_ids.count(glyph_id) > 1})
    if duplicates:
        failures.append(f"duplicate glyph ids: {duplicates}")

    if failures:
        print("glyph fixture failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"glyph fixtures ok: {len(glyph_ids)} glyphs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
