from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import ROOT


THEOREM_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-T\d{4}\b")
THEOREM_RANGE_RE = re.compile(
    r"\b(?P<prefix>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-T)"
    r"(?P<start>\d{4})\s+through\s+"
    r"(?:(?P=prefix))?(?P<end>\d{4})\b"
)
PROVED_CONTEXT_RE = re.compile(r"\b(Lean-proved|proved|proven|established)\b", re.IGNORECASE)
NEGATED_CONTEXT_RE = re.compile(
    r"\b(not proved|not yet proved|not claimed as proved|unless .* proved|future work)\b",
    re.IGNORECASE,
)


def theorem_manifest_paths() -> list[Path]:
    return sorted((ROOT / "manifests").glob("**/*.yaml"))


def load_theorem_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in theorem_manifest_paths():
        data = yaml.safe_load(path.read_text()) or {}
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                statuses[theorem_id] = theorem.get("status", "planned")
    return statuses


def reader_facing_paths() -> list[Path]:
    roots = [ROOT / "README.md", ROOT / "docs", ROOT / "papers", ROOT / "site"]
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
            continue
        for path in sorted(root.glob("**/*")):
            if "site/_site" in path.as_posix():
                continue
            if path.suffix in {".md", ".qmd"}:
                paths.append(path)
    return paths


def theorem_ids_in_line(line: str) -> set[str]:
    ids = set(THEOREM_ID_RE.findall(line))
    for match in THEOREM_RANGE_RE.finditer(line):
        prefix = match.group("prefix")
        start = int(match.group("start"))
        end = int(match.group("end"))
        if start <= end and end - start <= 200:
            ids.update(f"{prefix}{value:04d}" for value in range(start, end + 1))
    return ids


def main() -> int:
    statuses = load_theorem_statuses()
    failures: list[str] = []

    for path in reader_facing_paths():
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            if not PROVED_CONTEXT_RE.search(line):
                continue
            if NEGATED_CONTEXT_RE.search(line):
                continue
            ids = theorem_ids_in_line(line)
            for theorem_id in sorted(ids):
                status = statuses.get(theorem_id)
                if status is None:
                    failures.append(f"{path.relative_to(ROOT)}:{line_no}: unknown theorem id {theorem_id}")
                elif status not in {"proved", "lean_proved"}:
                    failures.append(
                        f"{path.relative_to(ROOT)}:{line_no}: {theorem_id} appears near proved language but status is {status}"
                    )

    if failures:
        print("claim-language failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("claim language ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
