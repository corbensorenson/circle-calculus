from __future__ import annotations

import sys
from pathlib import Path

import yaml

from repo_paths import (
    DICTIONARY,
    DIMENSION_DICTIONARIES,
    PAPER_MANIFEST,
    ROOT,
)


SHOWCASE = ROOT / "manifests" / "capability_showcase.yaml"
PROVED_STATUSES = {"proved", "lean_proved"}
REQUIRED_TEXT_FIELDS = [
    "title",
    "area",
    "audience_interest",
    "advertised_claim",
    "proof_scope",
    "not_claimed",
]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def theorem_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for path in sorted((ROOT / "manifests").glob("**/*.yaml")):
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                statuses[theorem_id] = theorem.get("status", "")
    return statuses


def paper_index() -> dict[str, dict]:
    data = load_yaml(PAPER_MANIFEST)
    return {paper["id"]: paper for paper in data.get("papers", []) if paper.get("id")}


def dictionary_ids() -> set[str]:
    ids = {
        entry["id"]
        for entry in load_yaml(DICTIONARY).get("entries", [])
        if entry.get("id")
    }
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        ids.update(
            entry["id"]
            for entry in load_yaml(path).get("entries", [])
            if entry.get("id")
        )
    return ids


def path_for_paper_id(paper_id: str) -> Path | None:
    for path in sorted((ROOT / "papers").glob("**/*.md")):
        if path.stem == paper_id:
            return path
    return None


def main() -> int:
    data = load_yaml(SHOWCASE)
    capabilities = data.get("capabilities", [])
    statuses = theorem_statuses()
    papers = paper_index()
    known_dictionary_ids = dictionary_ids()
    failures: list[str] = []

    ids = [item.get("id") for item in capabilities]
    duplicates = sorted({item for item in ids if item and ids.count(item) > 1})
    if duplicates:
        failures.append(f"duplicate capability ids: {duplicates}")

    for item in capabilities:
        capability_id = item.get("id", "<missing id>")
        if not item.get("id"):
            failures.append("capability entry missing id")
        for field in REQUIRED_TEXT_FIELDS:
            if not item.get(field):
                failures.append(f"{capability_id}: missing {field}")

        theorem_ids = item.get("theorem_ids", [])
        paper_ids = item.get("paper_ids", [])
        refs = item.get("source_refs", [])

        if not theorem_ids:
            failures.append(f"{capability_id}: must advertise at least one theorem id")
        if not paper_ids:
            failures.append(f"{capability_id}: must cite at least one paper id")
        if not refs:
            failures.append(f"{capability_id}: must cite at least one source ref")

        duplicate_theorems = sorted({tid for tid in theorem_ids if theorem_ids.count(tid) > 1})
        if duplicate_theorems:
            failures.append(f"{capability_id}: duplicate theorem ids {duplicate_theorems}")

        duplicate_papers = sorted({pid for pid in paper_ids if paper_ids.count(pid) > 1})
        if duplicate_papers:
            failures.append(f"{capability_id}: duplicate paper ids {duplicate_papers}")

        paper_theorem_ids: set[str] = set()
        for paper_id in paper_ids:
            paper = papers.get(paper_id)
            if paper is None:
                failures.append(f"{capability_id}: unknown paper id {paper_id}")
                continue
            if path_for_paper_id(paper_id) is None:
                failures.append(f"{capability_id}: no paper file for {paper_id}")
            paper_theorem_ids.update(paper.get("theorem_ids", []))

        for theorem_id in theorem_ids:
            status = statuses.get(theorem_id)
            if status is None:
                failures.append(f"{capability_id}: unknown theorem id {theorem_id}")
            elif status not in PROVED_STATUSES:
                failures.append(f"{capability_id}: theorem {theorem_id} status is {status}")
            if theorem_id not in paper_theorem_ids:
                failures.append(
                    f"{capability_id}: theorem {theorem_id} is not carried by cited papers {paper_ids}"
                )

        for dictionary_id in item.get("dictionary_ids", []):
            if dictionary_id not in known_dictionary_ids:
                failures.append(f"{capability_id}: unknown dictionary id {dictionary_id}")

        for ref in refs:
            local_ref = Path(ref)
            ref_path = ROOT / local_ref
            if local_ref.is_absolute() or ".." in local_ref.parts:
                failures.append(f"{capability_id}: unsafe source ref {ref}")
            elif not ref_path.exists():
                failures.append(f"{capability_id}: missing source ref {ref}")

    if failures:
        print("capability showcase failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"capability showcase ok: {len(capabilities)} capabilities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
