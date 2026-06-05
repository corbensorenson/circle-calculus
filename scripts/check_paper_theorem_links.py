from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import DICTIONARY, PAPERS, SIDECARS, THEOREM_MANIFEST


THEOREM_RE = re.compile(r"\bCC-T\d{4}\b")
DICT_RE = re.compile(r"\bCC-(?!T\d{4}\b)[A-Z0-9]+\b")
PROVED_WORD_RE = re.compile(r"\b(proved|proven|established)\b", re.IGNORECASE)


def main() -> int:
    manifest = yaml.safe_load(THEOREM_MANIFEST.read_text())
    theorem_by_id = {item["id"]: item for item in manifest["theorems"]}
    dictionary = yaml.safe_load(DICTIONARY.read_text())
    dictionary_ids = {entry["id"] for entry in dictionary["entries"]}

    failures: list[str] = []

    for paper in PAPERS.glob("PAPER_*.md"):
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
            if dict_id not in dictionary_ids:
                failures.append(f"{paper}: unknown dictionary id {dict_id}")

        for line_no, line in enumerate(text.splitlines(), start=1):
            if PROVED_WORD_RE.search(line):
                ids = THEOREM_RE.findall(line)
                for theorem_id in ids:
                    status = theorem_by_id.get(theorem_id, {}).get("status")
                    if status != "proved":
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

