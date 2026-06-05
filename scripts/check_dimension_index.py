from __future__ import annotations

import sys
from pathlib import Path

import yaml

from repo_paths import DIMENSION_INDEX, ROOT


REQUIRED_FIELDS = {
    "id",
    "display_name",
    "sphere_notation",
    "role",
    "status",
    "lean_namespace",
    "lean_root",
    "python_root",
    "paper_root",
    "theorem_manifest",
    "dictionary_file",
    "allowed_import_dimensions",
    "forbidden_import_dimensions",
}


def rel_exists(path_text: str) -> bool:
    return (ROOT / Path(path_text)).exists()


def main() -> int:
    data = yaml.safe_load(DIMENSION_INDEX.read_text())
    dimensions = data.get("dimensions", [])
    failures: list[str] = []

    ids = [dimension.get("id") for dimension in dimensions]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        failures.append(f"duplicate dimension ids: {duplicates}")

    known = set(ids)
    for dimension in dimensions:
        missing = sorted(REQUIRED_FIELDS - set(dimension))
        if missing:
            failures.append(f"{dimension.get('id', '<missing id>')}: missing fields {missing}")
            continue

        allowed = set(dimension["allowed_import_dimensions"])
        forbidden = set(dimension["forbidden_import_dimensions"])
        overlap = sorted(allowed & forbidden)
        if overlap:
            failures.append(f"{dimension['id']}: allowed/forbidden import overlap {overlap}")

        unknown_refs = sorted((allowed | forbidden) - known)
        if unknown_refs:
            failures.append(f"{dimension['id']}: unknown import dimension refs {unknown_refs}")

        if dimension["id"] in allowed or dimension["id"] in forbidden:
            failures.append(f"{dimension['id']}: import policy must not mention itself")

        for field in ["lean_root", "python_root", "paper_root", "theorem_manifest", "dictionary_file"]:
            if not rel_exists(dimension[field]):
                failures.append(f"{dimension['id']}: {field} does not exist: {dimension[field]}")

    if failures:
        print("dimension index failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"dimension index ok: {len(dimensions)} dimensions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

