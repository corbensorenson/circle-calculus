from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import PAPER_MANIFEST, PAPERS, ROOT


SECTION_RE = re.compile(r"^##\s+", re.MULTILINE)


def paper_paths_by_id() -> dict[str, Path]:
    return {
        path.stem: path
        for path in PAPERS.glob("**/PAPER*.md")
        if path.name != "template.md"
    }


def source_trail_section(text: str) -> str | None:
    marker = "## Source Trail"
    start = text.find(marker)
    if start == -1:
        return None
    next_section = SECTION_RE.search(text, start + len(marker))
    if next_section is None:
        return text[start:]
    return text[start : next_section.start()]


def has_theorem_section(text: str) -> bool:
    return any(
        marker in text
        for marker in [
            "## Theorem Spine",
            "## 4. Main Theorems",
            "## Main Theorems",
        ]
    )


def main() -> int:
    data = yaml.safe_load(PAPER_MANIFEST.read_text()) or {}
    entries = data.get("papers", [])
    paths = paper_paths_by_id()
    failures: list[str] = []

    for entry in entries:
        paper_id = entry.get("id")
        if not paper_id:
            failures.append("paper manifest entry missing id")
            continue

        path = paths.get(paper_id)
        if path is None:
            failures.append(f"{paper_id}: no paper file found")
            continue

        text = path.read_text()
        relative = path.relative_to(ROOT)
        section = source_trail_section(text)
        if section is None:
            failures.append(f"{relative}: missing ## Source Trail")
        else:
            sidecar = entry.get("sidecar")
            if sidecar and sidecar not in section:
                failures.append(f"{relative}: source trail does not mention manifest sidecar {sidecar}")
            if "Lean" not in section:
                failures.append(f"{relative}: source trail does not mention Lean")
            if "Python" not in section:
                failures.append(f"{relative}: source trail does not mention Python")
            if "proof status" not in section and "proof source" not in section:
                failures.append(f"{relative}: source trail does not state proof-status boundary")

        if "## Target Spine" in text:
            failures.append(f"{relative}: uses obsolete ## Target Spine heading")

        if entry.get("theorem_ids") and not has_theorem_section(text):
            failures.append(f"{relative}: theorem-bearing paper missing theorem section")

    if failures:
        print("paper source trail failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"paper source trails ok: {len(entries)} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
