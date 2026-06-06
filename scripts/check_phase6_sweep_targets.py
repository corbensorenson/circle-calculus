from __future__ import annotations

import sys

import yaml

from repo_paths import ROOT


TARGETS = ROOT / "manifests" / "phase6_sweep_targets.yaml"
ALLOWED_STATUSES = {"planned", "active", "completed", "blocked", "deferred"}
ALLOWED_SWEEP_TYPES = {
    "application_guardrails",
    "dictionary_usage",
    "living_book",
    "paper_quality",
    "proof_status",
    "repo_hygiene",
    "repo_onboarding",
    "sidecar_parity",
}
REQUIRED_FIELDS = {
    "id",
    "area",
    "priority",
    "status",
    "sweep_type",
    "objective",
    "acceptance_criteria",
    "artifact_refs",
    "checks",
    "next_action",
    "guardrail",
}


def main() -> int:
    data = yaml.safe_load(TARGETS.read_text()) or {}
    targets = data.get("targets", [])
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
        if not str(target_id).startswith("P6-SWEEP-"):
            failures.append(f"{target_id}: Phase VI sweep target id must start with P6-SWEEP-")
        if target["status"] not in ALLOWED_STATUSES:
            failures.append(f"{target_id}: invalid status {target['status']}")
        if target["sweep_type"] not in ALLOWED_SWEEP_TYPES:
            failures.append(f"{target_id}: invalid sweep_type {target['sweep_type']}")
        if target["status"] == "blocked" and not target.get("blocker"):
            failures.append(f"{target_id}: blocked target needs blocker text")
        if target["status"] == "completed" and not target.get("evidence_refs"):
            failures.append(f"{target_id}: completed target needs evidence_refs")
        if not target.get("acceptance_criteria"):
            failures.append(f"{target_id}: needs acceptance criteria")
        if not target.get("checks"):
            failures.append(f"{target_id}: needs checks")
        for ref in target.get("artifact_refs", []):
            path = ROOT / ref.split("#", 1)[0]
            if not path.exists():
                failures.append(f"{target_id}: missing artifact ref {ref}")

    if failures:
        print("phase6 sweep target failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"phase6 sweep targets ok: {len(targets)} targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
