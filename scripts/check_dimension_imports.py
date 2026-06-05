from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import DIMENSION_INDEX, ROOT


IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)")

ORDER = {
    "Common": 0,
    "S0": 1,
    "S1": 2,
    "S2": 3,
    "S3": 4,
    "S4": 5,
    "S5": 6,
    "S6": 7,
    "S7": 8,
    "Future": 9,
}


def load_policy() -> dict[str, set[str]]:
    data = yaml.safe_load(DIMENSION_INDEX.read_text())
    return {
        dimension["id"]: set(dimension["forbidden_import_dimensions"])
        for dimension in data.get("dimensions", [])
    }


def file_dimension(path: Path) -> str | None:
    parts = path.parts
    if "Common" in parts:
        return "Common"
    if "S0" in parts:
        return "S0"
    if "S1" in parts or "Core" in parts or "Proof" in parts or "Meta" in parts:
        return "S1"
    for dim in ["S2", "S3", "S4", "S5", "S6", "S7"]:
        if dim in parts:
            return dim
    if "Future" in parts:
        return "Future"
    if path.name in {"Circle.lean", "Basic.lean"}:
        return "S1"
    return None


def import_dimension(module: str) -> str | None:
    if module.startswith("Circle.Future."):
        return "Future"
    if module.startswith("Circle.Common."):
        return "Common"
    for dim in ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"]:
        if module.startswith(f"Circle.{dim}."):
            return dim
    if module.startswith("Circle.Core.") or module.startswith("Circle.Proof.") or module.startswith("Circle.Meta."):
        return "S1"
    if module in {"Circle", "Circle.Basic"}:
        return "S1"
    return None


def main() -> int:
    forbidden = load_policy()
    failures: list[str] = []

    for path in sorted((ROOT / "Circle").glob("**/*.lean")):
        current = file_dimension(path.relative_to(ROOT))
        if current is None:
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            match = IMPORT_RE.match(line)
            if not match:
                continue
            imported = import_dimension(match.group(1))
            if imported is None:
                continue
            if imported in forbidden.get(current, set()):
                failures.append(f"{path.relative_to(ROOT)}:{lineno}: {current} imports forbidden {imported}")
            if ORDER[imported] > ORDER[current] and current != "Future":
                failures.append(f"{path.relative_to(ROOT)}:{lineno}: lower dimension {current} imports higher {imported}")

    if failures:
        print("dimension import failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("dimension imports ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

