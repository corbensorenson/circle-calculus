from __future__ import annotations

import sys

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, ROOT


TARGETS = ROOT / "manifests" / "phase7_physics_generators.yaml"
ALLOWED_STATUSES = {"planned", "active", "exploratory_python", "blocked", "deferred"}
ALLOWED_TARGET_TYPES = {
    "benchmark",
    "living_book",
    "paper_program",
    "proof_program",
    "tooling",
}
REQUIRED_FIELDS = {
    "id",
    "area",
    "priority",
    "status",
    "target_type",
    "title",
    "question",
    "ordinary_baseline",
    "acceptance_criteria",
    "artifact_refs",
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


def main() -> int:
    data = yaml.safe_load(TARGETS.read_text()) or {}
    targets = data.get("targets", [])
    dictionary_ids = load_dictionary_ids()
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
        if not str(target_id).startswith(("P7-PHYS-", "P7-GEN-")):
            failures.append(f"{target_id}: Phase VII target id must start with P7-PHYS- or P7-GEN-")
        if target["status"] not in ALLOWED_STATUSES:
            failures.append(f"{target_id}: invalid status {target['status']}")
        if target["target_type"] not in ALLOWED_TARGET_TYPES:
            failures.append(f"{target_id}: invalid target_type {target['target_type']}")
        if target["status"] == "blocked" and not target.get("blocker"):
            failures.append(f"{target_id}: blocked target needs blocker text")
        if not target.get("ordinary_baseline"):
            failures.append(f"{target_id}: needs an ordinary baseline")
        if not target.get("acceptance_criteria"):
            failures.append(f"{target_id}: needs acceptance criteria")
        for ref in target.get("artifact_refs", []):
            path = ROOT / ref.split("#", 1)[0]
            if not path.exists():
                failures.append(f"{target_id}: missing artifact ref {ref}")
        for dep in target.get("dictionary_dependencies", []):
            if dep not in dictionary_ids:
                failures.append(f"{target_id}: unknown dictionary dependency {dep}")

    if failures:
        print("phase7 target failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"phase7 targets ok: {len(targets)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
