from __future__ import annotations

import sys

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, ROOT


TARGETS = ROOT / "manifests" / "phase8_depth_validation.yaml"
ALLOWED_STATUSES = {"planned", "active", "blocked", "deferred", "completed"}
ALLOWED_TARGET_TYPES = {
    "communication",
    "external_review",
    "proof_contract",
    "proof_program",
    "results_note",
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
        if not str(target_id).startswith(("P8-DEPTH-", "P8-VALID-", "P8-CONTRACT-", "P8-ENG-", "P8-COMM-")):
            failures.append(f"{target_id}: Phase VIII target id has an unknown prefix")
        if target["status"] not in ALLOWED_STATUSES:
            failures.append(f"{target_id}: invalid status {target['status']}")
        if target["target_type"] not in ALLOWED_TARGET_TYPES:
            failures.append(f"{target_id}: invalid target_type {target['target_type']}")
        if target["status"] == "blocked" and not target.get("blocker"):
            failures.append(f"{target_id}: blocked target needs blocker text")
        if target["status"] == "completed" and not target.get("evidence_refs"):
            failures.append(f"{target_id}: completed target needs evidence_refs")
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
        print("phase8 target failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"phase8 targets ok: {len(targets)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
