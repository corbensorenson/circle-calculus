from __future__ import annotations

import sys
from pathlib import Path

import yaml

from repo_paths import DICTIONARY, DIMENSION_DICTIONARIES, DIMENSION_MANIFESTS, ROOT, THEOREM_MANIFEST


MANIFEST_ROOTS = [ROOT / "manifests" / "applications", ROOT / "manifests" / "theories"]
ALLOWED_STATUSES = {"active", "planned", "deferred", "blocked"}
ALLOWED_THEOREM_STATUSES = {"lean_proved", "lean_stated", "planned", "exploratory_python", "blocked", "deferred"}
REQUIRED_FIELDS = {"id", "status", "papers", "sidecars", "theorems", "next_targets", "guardrail"}


def load_dictionary_ids() -> set[str]:
    ids = {entry["id"] for entry in yaml.safe_load(DICTIONARY.read_text()).get("entries", [])}
    for path in sorted(DIMENSION_DICTIONARIES.glob("*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        ids.update(entry["id"] for entry in data.get("entries", []))
    return ids


def load_theorems() -> dict[str, dict]:
    theorems: dict[str, dict] = {}
    for path in [THEOREM_MANIFEST, *sorted(DIMENSION_MANIFESTS.glob("*.yaml"))]:
        data = yaml.safe_load(path.read_text()) or {}
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                theorems[theorem_id] = theorem
    return theorems


def manifest_paths() -> list[Path]:
    paths: list[Path] = []
    for root in MANIFEST_ROOTS:
        paths.extend(sorted(root.glob("*.yaml")))
    return paths


def path_part(ref: str) -> str:
    return ref.split("::", 1)[0].split("#", 1)[0].split(" ", 1)[0]


def check_path(ref: str, label: str, failures: list[str]) -> None:
    path = ROOT / path_part(ref)
    if not path.exists():
        failures.append(f"{label}: missing path {ref}")


def main() -> int:
    dictionary_ids = load_dictionary_ids()
    theorem_by_id = load_theorems()
    failures: list[str] = []
    seen_ids: list[str] = []

    for path in manifest_paths():
        rel_path = path.relative_to(ROOT)
        data = yaml.safe_load(path.read_text()) or {}
        manifest_id = data.get("id", "<missing id>")
        seen_ids.append(manifest_id)

        missing = sorted(REQUIRED_FIELDS - set(data))
        if missing:
            failures.append(f"{rel_path}: {manifest_id} missing fields {missing}")
            continue

        if data["status"] not in ALLOWED_STATUSES:
            failures.append(f"{rel_path}: {manifest_id} invalid status {data['status']}")

        for ref in data.get("papers", []):
            check_path(ref, f"{rel_path}: {manifest_id} paper", failures)

        for ref in data.get("sidecars", []):
            check_path(ref, f"{rel_path}: {manifest_id} sidecar", failures)

        for ref in data.get("python_reference", []):
            check_path(ref, f"{rel_path}: {manifest_id} python_reference", failures)

        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id", "<missing theorem id>")
            if theorem.get("status") not in ALLOWED_THEOREM_STATUSES:
                failures.append(f"{rel_path}: {theorem_id} invalid theorem status {theorem.get('status')}")

            registered = theorem_by_id.get(theorem_id)
            if registered is None:
                failures.append(f"{rel_path}: unknown theorem id {theorem_id}")
            elif theorem.get("lean_name") != registered.get("lean_name"):
                failures.append(
                    f"{rel_path}: {theorem_id} lean_name mismatch: "
                    f"{theorem.get('lean_name')} != {registered.get('lean_name')}"
                )

            for dep in theorem.get("dictionary_dependencies", []):
                if dep not in dictionary_ids:
                    failures.append(f"{rel_path}: {theorem_id} unknown dictionary dependency {dep}")

        for benchmark in data.get("benchmarks", []):
            benchmark_id = benchmark.get("id", "<missing benchmark id>")
            if benchmark.get("status") != "exploratory_python":
                failures.append(f"{rel_path}: {benchmark_id} benchmark status should be exploratory_python")
            if not benchmark.get("description"):
                failures.append(f"{rel_path}: {benchmark_id} missing description")
            if benchmark.get("path"):
                check_path(benchmark["path"], f"{rel_path}: {benchmark_id} benchmark path", failures)
            else:
                failures.append(f"{rel_path}: {benchmark_id} missing benchmark path")
            if benchmark.get("script"):
                check_path(benchmark["script"], f"{rel_path}: {benchmark_id} benchmark script", failures)

        if not data.get("next_targets"):
            failures.append(f"{rel_path}: {manifest_id} missing next_targets")
        if not data.get("guardrail"):
            failures.append(f"{rel_path}: {manifest_id} missing guardrail")

    duplicates = sorted({item for item in seen_ids if seen_ids.count(item) > 1})
    if duplicates:
        failures.append(f"duplicate research manifest ids: {duplicates}")

    if failures:
        print("research manifest failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"research manifests ok: {len(manifest_paths())} manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
