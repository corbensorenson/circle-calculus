from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from repo_paths import ROOT


APPLICATION_MANIFESTS = ROOT / "manifests" / "applications"
APPLICATION_PAPERS = ROOT / "papers" / "applications"
APPLICATION_CONTEXT = ROOT / "docs" / "PHASE2_AND_APPLICATIONS.md"

REQUIRED_PAPER_HEADINGS = {
    "## Source Trail",
    "## Theorem Spine",
    "## Proved Core",
    "## Guardrail",
}

BASELINE_WORDS = {
    "autocorrelation",
    "baseline",
    "baselines",
    "constant",
    "dense",
    "direct",
    "domain-test",
    "fft",
    "gcd-cycle",
    "natural",
    "ntt",
    "ordinary",
    "periodogram",
    "standard",
    "threshold",
}

BENCHMARK_WORDS = {
    "benchmark",
    "benchmarks",
    "domain-test",
    "external",
    "fixture",
    "measure",
    "measurements",
    "negative",
    "synthetic",
}

CUDA_ALLOWED_CONTEXT = {
    "baseline",
    "baselines",
    "external",
    "future",
    "portability",
}

NEGATION_WORDS = {
    "do not",
    "does not",
    "not",
    "no claim",
    "no real-data",
    "not evidence",
}

OVERCLAIM_PATTERNS = [
    re.compile(r"\bcircles improve all\b", re.IGNORECASE),
    re.compile(r"\balways faster\b", re.IGNORECASE),
    re.compile(r"\balways better\b", re.IGNORECASE),
    re.compile(r"\breplaces? all attention\b", re.IGNORECASE),
    re.compile(r"\bproof that .*improves?\b", re.IGNORECASE),
]


def path_part(ref: str) -> str:
    return ref.split("::", 1)[0].split("#", 1)[0].split(" ", 1)[0]


def existing_path(ref: str) -> Path:
    return ROOT / path_part(ref)


def contains_any(text: str, words: set[str]) -> bool:
    lower = text.lower()
    return any(word in lower for word in words)


def sentence_for_line(text: str, line: str) -> str:
    start = text.find(line)
    if start == -1:
        return line
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_dot = text.find(".", start + len(line))
    right_newline = text.find("\n", start + len(line))
    right_candidates = [item for item in [right_dot, right_newline] if item != -1]
    right = min(right_candidates) if right_candidates else start + len(line)
    return text[left + 1 : right + 1]


def manifest_paths() -> list[Path]:
    return sorted(APPLICATION_MANIFESTS.glob("*.yaml"))


def application_paper_paths() -> list[Path]:
    return sorted(APPLICATION_PAPERS.glob("*.md"))


def check_manifest(path: Path, failures: list[str]) -> None:
    rel_path = path.relative_to(ROOT)
    data = yaml.safe_load(path.read_text()) or {}
    manifest_id = data.get("id", rel_path)
    combined_next = " ".join(data.get("next_targets", []))
    guardrail = data.get("guardrail", "")

    if not guardrail:
        failures.append(f"{rel_path}: {manifest_id} missing guardrail")

    for ref in data.get("papers", []):
        if not existing_path(ref).exists():
            failures.append(f"{rel_path}: {manifest_id} missing paper {ref}")

    for benchmark in data.get("benchmarks", []):
        benchmark_id = benchmark.get("id", "<missing benchmark id>")
        description = benchmark.get("description", "")
        if benchmark.get("status") != "exploratory_python":
            failures.append(f"{rel_path}: {benchmark_id} benchmark must be exploratory_python")
        if not contains_any(description, BASELINE_WORDS):
            failures.append(f"{rel_path}: {benchmark_id} description must name an ordinary baseline")
        if benchmark.get("path") and not existing_path(benchmark["path"]).exists():
            failures.append(f"{rel_path}: {benchmark_id} missing benchmark path {benchmark['path']}")
        if benchmark.get("script") and not existing_path(benchmark["script"]).exists():
            failures.append(f"{rel_path}: {benchmark_id} missing benchmark script {benchmark['script']}")

    if "benchmark" in combined_next.lower() and not contains_any(combined_next, BASELINE_WORDS):
        failures.append(f"{rel_path}: {manifest_id} benchmark next_targets must name a baseline family")

    if not contains_any(" ".join([combined_next, guardrail]), BENCHMARK_WORDS | BASELINE_WORDS):
        failures.append(f"{rel_path}: {manifest_id} needs benchmark/baseline guardrail language")


def check_application_paper(path: Path, failures: list[str]) -> None:
    rel_path = path.relative_to(ROOT)
    text = path.read_text()
    lower = text.lower()

    for heading in REQUIRED_PAPER_HEADINGS:
        if heading not in text:
            failures.append(f"{rel_path}: missing {heading}")

    if "lean declarations determine proof status" not in lower:
        failures.append(f"{rel_path}: missing Lean proof-status source sentence")

    if "benchmark" in lower and not contains_any(text, BASELINE_WORDS):
        failures.append(f"{rel_path}: benchmark discussion does not name ordinary baselines")

    if "benchmark" in lower and not any(phrase in lower for phrase in ["not evidence", "not a theorem", "not a proof", "do not prove", "lean declarations determine proof status"]):
        failures.append(f"{rel_path}: benchmark discussion lacks proof-status separation")

    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.search(r"\b(CUDA|cuFFT|NVIDIA)\b", line):
            sentence = sentence_for_line(text, line)
            if not contains_any(sentence, CUDA_ALLOWED_CONTEXT):
                failures.append(f"{rel_path}:{line_number}: CUDA/cuFFT wording must be external, future, portability, or baseline context")

        for pattern in OVERCLAIM_PATTERNS:
            if pattern.search(line):
                sentence = sentence_for_line(text, line).lower()
                if not any(word in sentence for word in NEGATION_WORDS):
                    failures.append(f"{rel_path}:{line_number}: possible unguarded application overclaim: {line.strip()}")

    if ("mlx" in lower or "mac-compatible" in lower) and "cuda" in lower:
        for line_number, line in enumerate(text.splitlines(), start=1):
            if "cuda" in line.lower() and not contains_any(line, CUDA_ALLOWED_CONTEXT):
                failures.append(f"{rel_path}:{line_number}: CUDA mention must not read as the local backend")


def check_context_doc(failures: list[str]) -> None:
    text = APPLICATION_CONTEXT.read_text()
    rel_path = APPLICATION_CONTEXT.relative_to(ROOT)
    if "Python and MLX executable models" not in text:
        failures.append(f"{rel_path}: missing MLX executable-model context")
    if "CUDA references remain external baselines or future portability notes" not in text:
        failures.append(f"{rel_path}: missing CUDA external-baseline/portability guardrail")
    if "claim is proved only when it has a compiled Lean declaration" not in text:
        failures.append(f"{rel_path}: missing proof-status guardrail")


def main() -> int:
    failures: list[str] = []
    for path in manifest_paths():
        check_manifest(path, failures)
    for path in application_paper_paths():
        check_application_paper(path, failures)
    check_context_doc(failures)

    if failures:
        print("application guardrail failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(
        f"application guardrails ok: {len(manifest_paths())} manifests, "
        f"{len(application_paper_paths())} papers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
