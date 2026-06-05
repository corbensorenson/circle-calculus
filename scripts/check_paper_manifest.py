from __future__ import annotations

import sys
from pathlib import Path

import yaml

from repo_paths import (
    DICTIONARY,
    DIMENSION_DICTIONARIES,
    DIMENSION_INDEX,
    PAPER_MANIFEST,
    PAPERS,
    ROOT,
    SIDECARS,
    THEOREM_MANIFEST,
)


ALLOWED_STATUSES = {
    "planned",
    "roadmap",
    "outline",
    "adapter",
    "draft",
    "complete",
}


def load_dimension_manifest_paths() -> list[Path]:
    data = yaml.safe_load(DIMENSION_INDEX.read_text())
    return [ROOT / dimension["theorem_manifest"] for dimension in data.get("dimensions", [])]


def load_theorem_ids() -> set[str]:
    ids = {item["id"] for item in yaml.safe_load(THEOREM_MANIFEST.read_text()).get("theorems", [])}
    for path in load_dimension_manifest_paths():
        data = yaml.safe_load(path.read_text())
        ids.update(item["id"] for item in data.get("theorems", []))
    return ids


def load_dictionary_ids() -> set[str]:
    ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        ids.update(entry["id"] for entry in data.get("entries", []))
    return ids


def manifest_path(text: str) -> Path:
    return ROOT / text


def main() -> int:
    data = yaml.safe_load(PAPER_MANIFEST.read_text())
    entries = data.get("papers", [])
    theorem_ids = load_theorem_ids()
    dictionary_ids = load_dictionary_ids()
    failures: list[str] = []

    paper_ids = [entry.get("id") for entry in entries]
    duplicate_papers = sorted({item for item in paper_ids if paper_ids.count(item) > 1})
    if duplicate_papers:
        failures.append(f"duplicate paper ids: {duplicate_papers}")

    registered_ids = set(paper_ids)
    existing_papers = {
        path.stem: path
        for path in PAPERS.glob("**/PAPER*.md")
        if path.name != "template.md"
    }

    missing_from_manifest = sorted(set(existing_papers) - registered_ids)
    if missing_from_manifest:
        failures.append(f"paper files missing from paper manifest: {missing_from_manifest}")

    for entry in entries:
        paper_id = entry.get("id")
        if not paper_id:
            failures.append("paper entry missing id")
            continue

        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            failures.append(f"{paper_id}: invalid status {status}")

        paper = existing_papers.get(paper_id)
        if paper is None:
            failures.append(f"{paper_id}: no paper file found under papers/")

        sidecar_text = entry.get("sidecar", "")
        theorem_refs = entry.get("theorem_ids", [])
        dictionary_refs = entry.get("dictionary_ids", [])

        duplicate_theorem_refs = sorted(
            {item for item in theorem_refs if theorem_refs.count(item) > 1}
        )
        if duplicate_theorem_refs:
            failures.append(f"{paper_id}: duplicate theorem refs {duplicate_theorem_refs}")

        duplicate_dictionary_refs = sorted(
            {item for item in dictionary_refs if dictionary_refs.count(item) > 1}
        )
        if duplicate_dictionary_refs:
            failures.append(f"{paper_id}: duplicate dictionary refs {duplicate_dictionary_refs}")

        for theorem_id in theorem_refs:
            if theorem_id not in theorem_ids:
                failures.append(f"{paper_id}: unknown theorem id {theorem_id}")

        for dictionary_id in dictionary_refs:
            if dictionary_id not in dictionary_ids:
                failures.append(f"{paper_id}: unknown dictionary id {dictionary_id}")

        if status != "planned" and not sidecar_text:
            failures.append(f"{paper_id}: non-planned paper has empty sidecar path")

        if sidecar_text:
            sidecar = manifest_path(sidecar_text)
            if not sidecar.exists():
                failures.append(f"{paper_id}: sidecar path does not exist: {sidecar_text}")
            elif not sidecar.is_dir():
                failures.append(f"{paper_id}: sidecar path is not a directory: {sidecar_text}")
            elif sidecar.name != paper_id:
                failures.append(f"{paper_id}: sidecar directory name does not match paper id")

            if theorem_refs:
                lean_dir = sidecar / "lean"
                if not lean_dir.exists():
                    failures.append(f"{paper_id}: theorem-bearing paper missing Lean sidecar dir")
                elif not list(lean_dir.glob("*.lean")):
                    failures.append(f"{paper_id}: theorem-bearing paper has no Lean sidecar files")

    sidecar_ids = {
        path.name
        for path in SIDECARS.iterdir()
        if path.is_dir() and path.name.startswith("PAPER")
    }
    orphan_sidecars = sorted(sidecar_ids - registered_ids)
    if orphan_sidecars:
        failures.append(f"sidecar directories missing from paper manifest: {orphan_sidecars}")

    if failures:
        print("paper manifest failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"paper manifest ok: {len(entries)} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
