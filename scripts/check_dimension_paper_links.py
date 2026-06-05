from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, DIMENSION_INDEX, PAPERS, ROOT, THEOREM_MANIFEST


TOKEN_RE = re.compile(r"\b(?:CC-T\d{4}|[A-Z][A-Z0-9]*-T\d{4}|[A-Z][A-Z0-9]*-W\d{4}|CC-[A-Z0-9]+|[A-Z][A-Z0-9]*-\d{4})\b")
PROVED_WORD_RE = re.compile(r"\b(proved|proven|established)\b", re.IGNORECASE)


def load_dimension_manifest_paths() -> list[Path]:
    data = yaml.safe_load(DIMENSION_INDEX.read_text())
    return [ROOT / dimension["theorem_manifest"] for dimension in data.get("dimensions", [])]


def main() -> int:
    theorem_by_id: dict[str, dict[str, str]] = {}
    warning_ids: set[str] = set()
    dictionary_ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}

    for theorem in yaml.safe_load(THEOREM_MANIFEST.read_text()).get("theorems", []):
        theorem_by_id[theorem["id"]] = {
            "status": theorem["status"],
            "lean_name": theorem["lean_name"],
        }

    for path in load_dimension_manifest_paths():
        data = yaml.safe_load(path.read_text())
        for theorem in data.get("theorems", []):
            theorem_by_id[theorem["id"]] = {
                "status": theorem["status"],
                "lean_name": theorem["lean_name"],
            }
        for warning in data.get("warnings", []):
            warning_ids.add(warning["id"])

    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        dictionary_ids.update(entry["id"] for entry in data.get("entries", []))

    failures: list[str] = []

    for paper in sorted(PAPERS.glob("**/*.md")):
        text = paper.read_text()
        for token in sorted(set(TOKEN_RE.findall(text))):
            if "-T" in token:
                theorem = theorem_by_id.get(token)
                if theorem is None:
                    failures.append(f"{paper.relative_to(ROOT)}: unknown theorem id {token}")
                    continue
                if theorem["status"] in {"proved", "lean_proved"} and theorem["lean_name"] not in text:
                    failures.append(f"{paper.relative_to(ROOT)}: {token} does not show Lean name {theorem['lean_name']}")
            elif "-W" in token:
                if token not in warning_ids and token not in dictionary_ids:
                    failures.append(f"{paper.relative_to(ROOT)}: unknown warning id {token}")
            elif token not in dictionary_ids:
                failures.append(f"{paper.relative_to(ROOT)}: unknown dictionary id {token}")

        for line_no, line in enumerate(text.splitlines(), start=1):
            if not PROVED_WORD_RE.search(line):
                continue
            for token in TOKEN_RE.findall(line):
                if "-T" not in token:
                    continue
                status = theorem_by_id.get(token, {}).get("status")
                if status not in {"proved", "lean_proved"}:
                    failures.append(
                        f"{paper.relative_to(ROOT)}:{line_no}: describes {token} as proved but status is {status}"
                    )

    if failures:
        print("dimension paper link failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("dimension paper links ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

