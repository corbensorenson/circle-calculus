from __future__ import annotations

import sys

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, DIMENSION_MANIFESTS, ROOT, THEOREM_MANIFEST


TARGETS = ROOT / "manifests" / "phase4_theorem_targets.yaml"
ALLOWED_STATUSES = {"planned", "deferred", "blocked", "exploratory_python", "promoted"}
ALLOWED_CLAIM_TYPES = {"theorem", "experiment", "paper_improvement", "proof_improvement"}
REQUIRED_FIELDS = {
    "id",
    "layer",
    "priority",
    "status",
    "claim_type",
    "title",
    "target_statement",
    "candidate_formalization",
    "paper_refs",
    "dictionary_dependencies",
    "next_action",
    "guardrail",
}


def load_dictionary_ids() -> set[str]:
    ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        ids.update(entry["id"] for entry in data.get("entries", []))
    return ids


def load_theorem_ids() -> set[str]:
    ids: set[str] = set()
    for path in [THEOREM_MANIFEST, *sorted(DIMENSION_MANIFESTS.glob("*.yaml"))]:
        data = yaml.safe_load(path.read_text()) or {}
        ids.update(theorem["id"] for theorem in data.get("theorems", []))
    return ids


def main() -> int:
    data = yaml.safe_load(TARGETS.read_text()) or {}
    targets = data.get("targets", [])
    dictionary_ids = load_dictionary_ids()
    theorem_ids = load_theorem_ids()
    failures: list[str] = []

    ids = [target.get("id") for target in targets]
    duplicates = sorted({target_id for target_id in ids if ids.count(target_id) > 1})
    if duplicates:
        failures.append(f"duplicate target ids: {duplicates}")

    for target in targets:
        target_id = target.get("id", "<missing id>")
        missing = sorted(REQUIRED_FIELDS - set(target))
        if missing:
            failures.append(f"{target_id}: missing fields {missing}")
            continue
        if target["status"] not in ALLOWED_STATUSES:
            failures.append(f"{target_id}: invalid status {target['status']}")
        if target["claim_type"] not in ALLOWED_CLAIM_TYPES:
            failures.append(f"{target_id}: invalid claim_type {target['claim_type']}")
        if target["status"] == "blocked" and not target.get("blocker"):
            failures.append(f"{target_id}: blocked target needs blocker text")
        if target["status"] == "promoted":
            promoted_theorem_id = target.get("promoted_theorem_id")
            if not promoted_theorem_id:
                failures.append(f"{target_id}: promoted target needs promoted_theorem_id")
            elif promoted_theorem_id not in theorem_ids:
                failures.append(f"{target_id}: promoted theorem id does not exist: {promoted_theorem_id}")
        for ref in target.get("paper_refs", []):
            path = ROOT / ref.split("#", 1)[0]
            if not path.exists():
                failures.append(f"{target_id}: missing paper ref {ref}")
        for dep in target.get("dictionary_dependencies", []):
            if dep not in dictionary_ids:
                failures.append(f"{target_id}: unknown dictionary dependency {dep}")

    if failures:
        print("phase4 target failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"phase4 targets ok: {len(targets)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
