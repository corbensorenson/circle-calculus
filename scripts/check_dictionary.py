from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml

from repo_paths import DICTIONARY, DICTIONARY_SCHEMA, DIMENSION_DICTIONARIES, ROOT


def dictionary_paths() -> list[Path]:
    return [DICTIONARY] + sorted(DIMENSION_DICTIONARIES.glob("*.yaml"))


def main() -> int:
    schema = json.loads(DICTIONARY_SCHEMA.read_text())
    path_entries: list[tuple[Path, dict]] = []
    failures: list[str] = []

    for path in dictionary_paths():
        data = yaml.safe_load(path.read_text()) or {}
        for entry in data.get("entries", []):
            path_entries.append((path, entry))

    ids = [entry.get("id") for _, entry in path_entries]
    duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
    if duplicates:
        failures.append(f"duplicate dictionary ids: {duplicates}")

    for path, entry in path_entries:
        try:
            jsonschema.validate(entry, schema)
        except jsonschema.ValidationError as error:
            rel_path = path.relative_to(ROOT)
            entry_id = entry.get("id", "<missing id>")
            failures.append(f"{rel_path}: {entry_id}: schema validation failed: {error.message}")

    known = set(ids)
    for path, entry in path_entries:
        for dep in entry.get("dependencies", []):
            if dep not in known:
                rel_path = path.relative_to(ROOT)
                failures.append(f"{rel_path}: {entry['id']} missing dictionary dependency {dep}")

    empty_forbidden = [
        f"{path.relative_to(ROOT)}:{entry['id']}"
        for path, entry in path_entries
        if not entry.get("forbidden_meanings")
    ]
    if empty_forbidden:
        failures.append(f"entries missing forbidden meanings: {empty_forbidden}")

    if failures:
        print("dictionary failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"dictionary ok: {len(path_entries)} entries across {len(dictionary_paths())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
