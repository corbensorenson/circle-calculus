from __future__ import annotations

import json
import sys

import jsonschema
import yaml

from repo_paths import DICTIONARY, DICTIONARY_SCHEMA


def main() -> int:
    data = yaml.safe_load(DICTIONARY.read_text())
    schema = json.loads(DICTIONARY_SCHEMA.read_text())
    entries = data.get("entries", [])

    ids = [entry.get("id") for entry in entries]
    duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
    if duplicates:
        print(f"duplicate dictionary ids: {duplicates}", file=sys.stderr)
        return 1

    for entry in entries:
        jsonschema.validate(entry, schema)

    known = set(ids)
    missing = []
    for entry in entries:
        for dep in entry.get("dependencies", []):
            if dep not in known:
                missing.append((entry["id"], dep))

    if missing:
        print(f"missing dictionary dependencies: {missing}", file=sys.stderr)
        return 1

    empty_forbidden = [
        entry["id"] for entry in entries if not entry.get("forbidden_meanings")
    ]
    if empty_forbidden:
        print(f"entries missing forbidden meanings: {empty_forbidden}", file=sys.stderr)
        return 1

    print(f"dictionary ok: {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

