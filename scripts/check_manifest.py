from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

from repo_paths import DICTIONARY, THEOREM_MANIFEST, THEOREM_SCHEMA


DECL_RE = re.compile(r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive)\s+([A-Za-z0-9_'.]+)")


def lean_declarations() -> set[str]:
    names: set[str] = set()
    for path in Path(".").glob("Circle/**/*.lean"):
        namespace_stack: list[str] = []
        for line in path.read_text().splitlines():
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
                names.add(full)
    return names


def main() -> int:
    manifest = yaml.safe_load(THEOREM_MANIFEST.read_text())
    schema = json.loads(THEOREM_SCHEMA.read_text())
    jsonschema.validate(manifest, schema)

    theorem_ids = [item["id"] for item in manifest["theorems"]]
    lean_names = [item["lean_name"] for item in manifest["theorems"] if item["lean_name"]]

    duplicate_ids = sorted({item for item in theorem_ids if theorem_ids.count(item) > 1})
    duplicate_lean = sorted({item for item in lean_names if lean_names.count(item) > 1})
    if duplicate_ids or duplicate_lean:
        print(
            f"duplicate theorem ids={duplicate_ids}, lean names={duplicate_lean}",
            file=sys.stderr,
        )
        return 1

    dictionary = yaml.safe_load(DICTIONARY.read_text())
    dictionary_ids = {entry["id"] for entry in dictionary["entries"]}
    missing_deps = []
    for theorem in manifest["theorems"]:
        for dep in theorem.get("dictionary_dependencies", []):
            if dep not in dictionary_ids:
                missing_deps.append((theorem["id"], dep))
    if missing_deps:
        print(f"missing theorem dictionary dependencies: {missing_deps}", file=sys.stderr)
        return 1

    declarations = lean_declarations()
    missing_proved = [
        theorem["lean_name"]
        for theorem in manifest["theorems"]
        if theorem["status"] == "proved" and theorem["lean_name"] not in declarations
    ]
    if missing_proved:
        print(f"proved declarations not found in Lean source: {missing_proved}", file=sys.stderr)
        return 1

    print(f"manifest ok: {len(theorem_ids)} theorems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

