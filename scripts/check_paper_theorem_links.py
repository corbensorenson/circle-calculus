from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import (
    DICTIONARY,
    DIMENSION_DICTIONARIES,
    PAPERS,
    ROOT,
    SIDECARS,
)


THEOREM_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-T\d{4}\b")
DICT_RE = re.compile(r"\bCC-(?!T\d{4}\b)[A-Z0-9]+\b")
PROVED_WORD_RE = re.compile(r"\b(proved|proven|established)\b", re.IGNORECASE)
PROVED_STATUSES = {"proved", "lean_proved"}


def theorem_manifest_paths() -> list[Path]:
    ignored = {
        "capability_showcase.yaml",
        "dimension_index.yaml",
        "paper_manifest.yaml",
    }
    return [
        path
        for path in sorted((ROOT / "manifests").glob("**/*.yaml"))
        if path.name not in ignored
    ]


def theorem_index() -> dict[str, dict]:
    theorem_by_id: dict[str, dict] = {}
    for path in theorem_manifest_paths():
        data = yaml.safe_load(path.read_text()) or {}
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                theorem_by_id[theorem_id] = theorem
    return theorem_by_id


def dictionary_ids() -> set[str]:
    ids = {
        entry["id"]
        for entry in (yaml.safe_load(DICTIONARY.read_text()) or {}).get("entries", [])
        if entry.get("id")
    }
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        ids.update(
            entry["id"]
            for entry in data.get("entries", [])
            if entry.get("id")
        )
    return ids


def paper_paths() -> list[Path]:
    return [
        path
        for path in sorted(PAPERS.glob("**/PAPER*.md"))
        if path.name != "template.md"
    ]


def main() -> int:
    theorem_by_id = theorem_index()
    known_dictionary_ids = dictionary_ids()

    failures: list[str] = []

    for paper in paper_paths():
        text = paper.read_text()
        paper_id = paper.stem
        sidecar = SIDECARS / paper_id
        if not sidecar.exists():
            failures.append(f"{paper}: missing sidecar folder {sidecar}")

        for theorem_id in sorted(set(THEOREM_RE.findall(text))):
            theorem = theorem_by_id.get(theorem_id)
            if theorem is None:
                failures.append(f"{paper}: unknown theorem id {theorem_id}")
                continue
            if theorem["lean_name"] not in text:
                failures.append(f"{paper}: {theorem_id} does not show Lean name {theorem['lean_name']}")

        for dict_id in sorted(set(DICT_RE.findall(text))):
            if dict_id not in known_dictionary_ids:
                failures.append(f"{paper}: unknown dictionary id {dict_id}")

        for line_no, line in enumerate(text.splitlines(), start=1):
            if PROVED_WORD_RE.search(line):
                ids = THEOREM_RE.findall(line)
                for theorem_id in ids:
                    status = theorem_by_id.get(theorem_id, {}).get("status")
                    if status not in PROVED_STATUSES:
                        failures.append(
                            f"{paper}:{line_no}: describes {theorem_id} as proved but status is {status}"
                        )

    if failures:
        print("paper link failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("paper theorem links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
