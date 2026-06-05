from __future__ import annotations

import sys
from pathlib import Path

import yaml

from check_manifest import lean_declarations
from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, DIMENSION_INDEX, DIMENSION_MANIFESTS, ROOT, THEOREM_MANIFEST


THEOREM_STATUSES = {
    "planned",
    "exploratory_python",
    "lean_stated",
    "lean_proved",
    "paper_draft",
    "paper_complete",
    "blocked",
    "deferred",
}

REQUIRED_THEOREM_FIELDS = {
    "id",
    "status",
    "lean_name",
    "informal_statement",
    "formal_statement",
    "dictionary_dependencies",
    "paper_refs",
    "imports_allowed",
    "verification",
    "blocker",
}

REQUIRED_WARNING_FIELDS = {
    "id",
    "status",
    "dictionary_dependencies",
    "paper_refs",
    "statement",
}


def load_dictionary_ids() -> set[str]:
    ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        ids.update(entry["id"] for entry in data.get("entries", []))
    return ids


def path_from_ref(ref: str) -> Path:
    return ROOT / ref.split("#", 1)[0]


def main() -> int:
    index = yaml.safe_load(DIMENSION_INDEX.read_text())
    expected_manifests = {
        Path(dimension["theorem_manifest"])
        for dimension in index.get("dimensions", [])
    }
    dictionary_ids = load_dictionary_ids()
    declarations = lean_declarations()
    failures: list[str] = []

    root_manifest = yaml.safe_load(THEOREM_MANIFEST.read_text())
    theorem_ids = [theorem["id"] for theorem in root_manifest.get("theorems", [])]
    warning_ids: list[str] = []

    for rel_path in sorted(expected_manifests):
        path = ROOT / rel_path
        data = yaml.safe_load(path.read_text())
        if "source_manifest" in data and not (ROOT / data["source_manifest"]).exists():
            failures.append(f"{rel_path}: source_manifest does not exist: {data['source_manifest']}")

        for theorem in data.get("theorems", []):
            missing = sorted(REQUIRED_THEOREM_FIELDS - set(theorem))
            if missing:
                failures.append(f"{rel_path}: {theorem.get('id', '<missing theorem id>')} missing {missing}")
                continue

            theorem_ids.append(theorem["id"])
            if theorem["status"] not in THEOREM_STATUSES:
                failures.append(f"{rel_path}: {theorem['id']} invalid status {theorem['status']}")

            if theorem["status"] == "blocked" and not theorem.get("blocker"):
                failures.append(f"{rel_path}: {theorem['id']} is blocked without blocker text")

            if theorem["status"] == "lean_proved" and theorem["lean_name"] not in declarations:
                failures.append(f"{rel_path}: {theorem['id']} lean_proved declaration not found: {theorem['lean_name']}")

            for dep in theorem.get("dictionary_dependencies", []):
                if dep not in dictionary_ids:
                    failures.append(f"{rel_path}: {theorem['id']} unknown dictionary dependency {dep}")

            for ref in theorem.get("paper_refs", []):
                if not path_from_ref(ref).exists():
                    failures.append(f"{rel_path}: {theorem['id']} missing paper ref {ref}")

        for warning in data.get("warnings", []):
            missing = sorted(REQUIRED_WARNING_FIELDS - set(warning))
            if missing:
                failures.append(f"{rel_path}: {warning.get('id', '<missing warning id>')} missing {missing}")
                continue

            warning_ids.append(warning["id"])
            for dep in warning.get("dictionary_dependencies", []):
                if dep not in dictionary_ids:
                    failures.append(f"{rel_path}: {warning['id']} unknown dictionary dependency {dep}")

            for ref in warning.get("paper_refs", []):
                if not path_from_ref(ref).exists():
                    failures.append(f"{rel_path}: {warning['id']} missing paper ref {ref}")

    duplicate_theorems = sorted({item for item in theorem_ids if theorem_ids.count(item) > 1})
    duplicate_warnings = sorted({item for item in warning_ids if warning_ids.count(item) > 1})
    if duplicate_theorems:
        failures.append(f"duplicate theorem ids: {duplicate_theorems}")
    if duplicate_warnings:
        failures.append(f"duplicate warning ids: {duplicate_warnings}")

    if failures:
        print("dimension manifest failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"dimension manifests ok: {len(theorem_ids)} theorem ids, {len(warning_ids)} warnings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

