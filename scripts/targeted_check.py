#!/usr/bin/env python3
"""Run change-aware validation for the Circle Calculus repository.

This script is intentionally conservative: it shortens the local edit loop, but
it does not replace `make check` or `make living-book-check` before release.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PYTHON = sys.executable

from scripts.check_circle_ai_contract_docs import STRICT_RECEIPT_TOKENS_BY_KIND


@dataclass(frozen=True)
class Check:
    label: str
    command: tuple[str, ...]
    reason: str


def rel(path: str | Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix().lstrip("./")


def run_git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def strict_receipt_kinds_from_checks(checks: Iterable[Check]) -> tuple[str, ...]:
    kinds: set[str] = set()
    for check in checks:
        command = check.command
        if command in {
            ("make", "check"),
            ("make", "sourcecheck"),
            ("make", "circle-ai-contracts-ready"),
        }:
            kinds.update(STRICT_RECEIPT_TOKENS_BY_KIND)
        if "--receipt" not in command or "--kind" not in command:
            continue
        kind_index = command.index("--kind") + 1
        if kind_index < len(command):
            kinds.add(command[kind_index])
    return tuple(kind for kind in ALL_AI_CONTRACT_KINDS if kind in kinds)


def detect_base() -> str | None:
    upstream = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
    if upstream:
        merge_base = run_git(["merge-base", "HEAD", upstream[0]])
        if merge_base:
            return merge_base[0]
    previous = run_git(["rev-parse", "HEAD~1"])
    return previous[0] if previous else None


def changed_files(base: str | None = None, explicit: Iterable[str] = ()) -> list[str]:
    if explicit:
        return sorted(dict.fromkeys(rel(path) for path in explicit))

    files: list[str] = []
    base = base or detect_base()
    if base:
        files.extend(run_git(["diff", "--name-only", f"{base}...HEAD"]))
    files.extend(run_git(["diff", "--name-only"]))
    files.extend(run_git(["diff", "--cached", "--name-only"]))
    files.extend(run_git(["ls-files", "--others", "--exclude-standard"]))
    return sorted(dict.fromkeys(rel(path) for path in files))


def add(checks: list[Check], seen: set[tuple[str, ...]], label: str, command: Iterable[str], reason: str) -> None:
    command_tuple = tuple(command)
    if command_tuple in seen:
        return
    seen.add(command_tuple)
    checks.append(Check(label=label, command=command_tuple, reason=reason))


def py(script: str, *args: str) -> tuple[str, ...]:
    return (PYTHON, script, *args)


def pytest(*paths: str) -> tuple[str, ...]:
    return (PYTHON, "-m", "pytest", *paths, "-q")


def path_matches(path: str, *needles: str) -> bool:
    lower = path.lower()
    return any(needle.lower() in lower for needle in needles)


MAKEFILE_AI_CONTRACT_MARKERS = (
    "ai_contract",
    "ai-contract",
    "circle-ai",
    "circle_ai",
    "contract-pack",
    "contract pack",
    "theseus-ai",
    "theseus_ai",
    "rope",
    "kv-cache",
    "kv_cache",
    "sparse-attention",
    "sparse_attention",
    "recurrence",
    "strided-candidate",
    "cyclic-memory",
    "multicoil",
    "circulant",
    "seed-rule",
)

MAKEFILE_PRIME_ENGINE_MARKERS = (
    "circle_prime",
    "circle-prime",
    "prime-engine",
    "prime_engine",
    "primesieve",
)

MAKEFILE_SITE_MARKERS = (
    "living-book",
    "living_book",
    "quarto",
    "site-",
    "site_",
    "sitecheck",
    "siterender",
)

MAKEFILE_TARGETED_MARKERS = (
    "targeted-check",
    "targeted_check",
    "targeted_",
)


def makefile_changed_lines() -> tuple[str, ...]:
    """Return changed Makefile content lines when git has enough context."""

    diff_args: list[list[str]] = [
        ["diff", "--unified=0", "--", "Makefile"],
        ["diff", "--cached", "--unified=0", "--", "Makefile"],
    ]
    base = detect_base()
    if base:
        diff_args.append(["diff", "--unified=0", f"{base}...HEAD", "--", "Makefile"])

    lines: list[str] = []
    for args in diff_args:
        for line in run_git(args):
            if not line.startswith(("+", "-")):
                continue
            if line.startswith(("+++", "---")):
                continue
            content = line[1:].strip()
            if content:
                lines.append(content)
    return tuple(dict.fromkeys(lines))


def makefile_changed_topics() -> tuple[str, ...]:
    lines = makefile_changed_lines()
    if not lines:
        return ("unknown",)

    topics: set[str] = set()
    for line in lines:
        lower = line.lower()
        matched = False
        if any(marker in lower for marker in MAKEFILE_AI_CONTRACT_MARKERS):
            topics.add("ai_contract")
            matched = True
        if any(marker in lower for marker in MAKEFILE_PRIME_ENGINE_MARKERS):
            topics.add("prime_engine")
            matched = True
        if any(marker in lower for marker in MAKEFILE_SITE_MARKERS):
            topics.add("site")
            matched = True
        if any(marker in lower for marker in MAKEFILE_TARGETED_MARKERS):
            topics.add("targeted")
            matched = True
        if not matched:
            topics.add("unknown")
    return tuple(sorted(topics))


def lean_module_name(path: str) -> str | None:
    if not path.startswith("Circle/") or not path.endswith(".lean"):
        return None
    return path.removesuffix(".lean").replace("/", ".")


def add_site_checks(checks: list[Check], seen: set[tuple[str, ...]], reason: str, *, widgets: bool = False) -> None:
    add(checks, seen, "site data export", py("scripts/site/export_site_data.py"), reason)
    add(checks, seen, "site structure", py("scripts/site/check_quarto_structure.py"), reason)
    add(checks, seen, "site manifest links", py("scripts/site/check_site_manifest_links.py"), reason)
    add(checks, seen, "site dictionary links", py("scripts/site/check_site_dictionary_links.py"), reason)
    add(checks, seen, "site theorem status", py("scripts/site/check_site_theorem_status.py"), reason)
    add(checks, seen, "site scaffold contract", py("scripts/site/check_site_scaffold_contract.py"), reason)
    add(checks, seen, "site source links", py("scripts/site/check_site_source_links.py"), reason)
    add(checks, seen, "site static source links", py("scripts/site/check_site_static_source_links.py"), reason)
    add(checks, seen, "site backlinks", py("scripts/site/check_site_data_backlinks.py"), reason)
    if widgets:
        add(checks, seen, "site widget contracts", py("scripts/site/check_site_widget_contracts.py"), reason)
        add(checks, seen, "site widget parity", py("scripts/site/check_widget_python_parity.py"), reason)
        add(checks, seen, "site widget runtime links", py("scripts/site/check_widget_runtime_links.py"), reason)


def add_circle_ai_contract_checks(checks: list[Check], seen: set[tuple[str, ...]], reason: str) -> None:
    add(checks, seen, "Circle AI contract readiness", ("make", "circle-ai-contracts-ready"), reason)
    add(checks, seen, "Circle AI contract pack tests", pytest("tests/test_circle_ai_contract_pack.py"), reason)
    add(checks, seen, "Circle AI consumer tests", pytest("tests/test_circle_ai_contract_consumer.py"), reason)
    add(
        checks,
        seen,
        "Circle AI acceptance policy tests",
        pytest("tests/test_circle_ai_contract_acceptance_policy.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI example consumer tests",
        pytest("tests/test_example_consume_circle_ai_contract_pack.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI standalone downstream CI tests",
        pytest("tests/test_downstream_ci_accept_circle_ai_contracts.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI standalone artifact verifier tests",
        pytest("tests/test_downstream_ci_verify_circle_ai_artifacts.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI contract runner tests",
        pytest("tests/test_circle_ai_contract_runner.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI receipt verifier tests",
        pytest("tests/test_check_circle_ai_receipt.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI receipt replay verifier tests",
        pytest("tests/test_check_circle_ai_receipt_replay.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI certification bundle verifier tests",
        pytest("tests/test_check_circle_ai_certification_bundle.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI contract runner example check",
        py("scripts/check_circle_ai_contract_runner.py"),
        reason,
    )
    add(
        checks,
        seen,
        "Circle AI request example tests",
        pytest("tests/test_circle_ai_contract_request_examples.py"),
        reason,
    )


def add_public_api_checks(checks: list[Check], seen: set[tuple[str, ...]], reason: str) -> None:
    add(checks, seen, "public API docs", py("scripts/generate_public_api_docs.py"), reason)
    add(checks, seen, "public API tests", pytest("tests/test_public_api.py"), reason)
    add_circle_ai_contract_checks(checks, seen, reason)


AI_CONTRACT_DIGEST_FIELDS = {
    "rope_position_distinguishability": (
        "d19_proved_request_status",
        "d19_impossible_request_status",
        "d19_undecided_request_status",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_radian_bank_form",
        "d19_proved_first_channel_bank_tolerance_rule",
    ),
    "kv_cache_ring_buffer": (
        "stale_probe_first_stale_token",
        "stale_probe_stale_requested_count",
        "sink_tokens_retained_by_policy",
        "sink_window_exact_policy",
        "sink_window_tokens_distinct",
        "sink_prefix_disjoint_from_live_window",
        "sink_tokens_outside_ordinary_rolling_window",
    ),
    "sparse_attention_coverage": (
        "first_uncovered_lag",
        "first_uncovered_interval_start",
        "complete_repair_window",
        "complete_repair_window_covers_context",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
    ),
    "recurrence_schedule": (
        "scheduled_work_saving",
        "post_period_multi_extension_scheduled_work_saving",
    ),
    "strided_candidate_fanout": (
        "gcd",
        "predicted_reach",
        "full_coverage",
        "effective_candidate_budget",
        "candidate_budget_accounting",
        "candidate_budget_shortfall",
        "duplicate_count",
    ),
    "cyclic_memory_residue_winding": (
        "same_residue_events",
        "same_residue_windings",
        "max_alias_load",
    ),
    "multicoil_phase_feature": (
        "phase_tuple",
        "joint_repeat_horizon",
        "shifted_phase_tuple",
        "relative_phase",
        "shifted_relative_phase",
    ),
    "circulant_block_cyclic_mixer": (
        "max_abs_dense_delta",
        "circulant_parameters",
        "dense_parameters",
        "block_cyclic_parameters",
        "block_to_dense_ratio",
    ),
    "seed_rule_exact_regeneration": (
        "storage_saving",
        "bounded_search_best_exact_candidate_id",
        "bounded_search_best_shorter_candidate_id",
    ),
}


def add_circle_ai_contract_core_checks(
    checks: list[Check],
    seen: set[tuple[str, ...]],
    reason: str,
) -> None:
    add(checks, seen, "Circle AI contract export", py("scripts/export_circle_ai_contracts.py"), reason)
    add(checks, seen, "Circle AI contract pack", py("scripts/check_circle_ai_contract_pack.py"), reason)
    add(checks, seen, "Circle AI contract docs", py("scripts/check_circle_ai_contract_docs.py"), reason)


def strict_receipt_args(kind: str) -> tuple[str, ...]:
    args: list[str] = []
    for token in STRICT_RECEIPT_TOKENS_BY_KIND.get(kind, ()):
        args.extend(shlex.split(token))
    return tuple(args)


def add_circle_ai_contract_kind_checks(
    checks: list[Check],
    seen: set[tuple[str, ...]],
    reason: str,
    kind: str,
) -> None:
    add_circle_ai_contract_core_checks(checks, seen, reason)
    add(
        checks,
        seen,
        f"Circle AI contract readiness: {kind}",
        py("scripts/circle_ai_contract_ready.py", "--kind", kind),
        reason,
    )
    digest_fields = AI_CONTRACT_DIGEST_FIELDS.get(kind, ())
    if digest_fields:
        digest_args: list[str] = ["--kind", kind, "--digest"]
        for field in digest_fields:
            digest_args.extend(["--field", field])
        digest_args.append("--include-recommendations")
        add(
            checks,
            seen,
            f"Circle AI contract digest: {kind}",
            py("scripts/circle_ai_contract_ready.py", *digest_args),
            reason,
        )
    receipt_args = strict_receipt_args(kind)
    if receipt_args:
        add(
            checks,
            seen,
            f"Circle AI strict receipt: {kind}",
            py(
                "scripts/circle_ai_contract_ready.py",
                "--kind",
                kind,
                "--receipt",
                "--format",
                "json",
                *receipt_args,
            ),
            reason,
        )


AI_CONTRACT_SITE_PAGE_KINDS = {
    "site/chapters/applications/rope_certifier.qmd": "rope_position_distinguishability",
    "site/chapters/applications/rope_certifier_audit.qmd": "rope_position_distinguishability",
    "site/chapters/applications/kv_cache_ring_buffer.qmd": "kv_cache_ring_buffer",
    "site/chapters/applications/kv_cache_ring_buffer_audit.qmd": "kv_cache_ring_buffer",
    "site/chapters/applications/sparse_attention_contract.qmd": "sparse_attention_coverage",
    "site/chapters/applications/sparse_attention_audit.qmd": "sparse_attention_coverage",
    "site/chapters/applications/strided_candidate_fanout.qmd": "strided_candidate_fanout",
    "site/chapters/applications/cyclic_memory_residue_winding.qmd": "cyclic_memory_residue_winding",
    "site/chapters/applications/multicoil_phase_feature.qmd": "multicoil_phase_feature",
    "site/chapters/applications/circulant_block_cyclic_mixer.qmd": (
        "circulant_block_cyclic_mixer"
    ),
    "site/chapters/applications/looped_recurrence_contracts.qmd": "recurrence_schedule",
    "site/chapters/applications/looped_recurrence_audit.qmd": "recurrence_schedule",
    "site/chapters/applications/generative.qmd": "seed_rule_exact_regeneration",
    "site/chapters/applications/generative_audit.qmd": "seed_rule_exact_regeneration",
}

AI_CONTRACT_SHARED_SITE_PAGES = {
    "site/chapters/applications/ai_contract_runner.qmd",
    "site/chapters/applications/ai_contract_suite.qmd",
    "site/chapters/applications/ai_contract_pack_audit.qmd",
    "site/chapters/applications/ai_contract_ladder.qmd",
    "site/chapters/applications/ai_contract_ladder_audit.qmd",
}

AI_CONTRACT_DOC_KINDS = {
    "docs/ROPE_CERTIFIER_QUICKSTART.md": "rope_position_distinguishability",
    "docs/ROPE_CERTIFIER_REVIEW_PACKET.md": "rope_position_distinguishability",
    "docs/ROPE_CERTIFIER_RESULTS_NOTE.md": "rope_position_distinguishability",
    "docs/KV_CACHE_CERTIFIER_QUICKSTART.md": "kv_cache_ring_buffer",
    "docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md": "sparse_attention_coverage",
    "docs/RECURRENCE_SCHEDULE_CERTIFIER_QUICKSTART.md": "recurrence_schedule",
    "docs/STRIDED_CANDIDATE_FANOUT_CERTIFIER_QUICKSTART.md": "strided_candidate_fanout",
    "docs/CYCLIC_MEMORY_CERTIFIER_QUICKSTART.md": "cyclic_memory_residue_winding",
    "docs/MULTICOIL_PHASE_FEATURE_CERTIFIER_QUICKSTART.md": "multicoil_phase_feature",
    "docs/CIRCULANT_BLOCK_CYCLIC_MIXER_CERTIFIER_QUICKSTART.md": "circulant_block_cyclic_mixer",
    "docs/SEED_RULE_CERTIFIER_QUICKSTART.md": "seed_rule_exact_regeneration",
}

ALL_AI_CONTRACT_KINDS = tuple(AI_CONTRACT_DIGEST_FIELDS)

AI_CONTRACT_CERTIFIER_PATH_KINDS = {
    "scripts/rope_certify.py": "rope_position_distinguishability",
    "scripts/kv_cache_certify.py": "kv_cache_ring_buffer",
    "scripts/stride_family_certify.py": "sparse_attention_coverage",
    "scripts/recurrence_schedule_certify.py": "recurrence_schedule",
    "scripts/strided_candidate_fanout_certify.py": "strided_candidate_fanout",
    "scripts/cyclic_memory_certify.py": "cyclic_memory_residue_winding",
    "scripts/multicoil_phase_feature_certify.py": "multicoil_phase_feature",
    "scripts/circulant_block_cyclic_mixer_certify.py": (
        "circulant_block_cyclic_mixer"
    ),
    "scripts/seed_rule_certify.py": "seed_rule_exact_regeneration",
}

AI_CONTRACT_LEAN_PATH_KINDS = {
    "Circle/Applications/RoPECertifier.lean": "rope_position_distinguishability",
    "Circle/Applications/RoPEFrontier.lean": "rope_position_distinguishability",
    "Circle/Applications/RoPEGeneratedCertificates.lean": (
        "rope_position_distinguishability"
    ),
    "Circle/Applications/CircleTransformer.lean": "sparse_attention_coverage",
    "Circle/Generative/SeedRule.lean": "seed_rule_exact_regeneration",
}

AI_CONTRACT_BROAD_SURFACE_PATHS = {
    "circle_math/ai_contracts.py",
    "circle_math/cli.py",
    "circle_math/applications/__init__.py",
    "circle_math/applications/circle_ai.py",
    "circle_math/applications/circle_ai_contracts.py",
    "circle_math/applications/circle_ai_contract_consumer.py",
    "circle_math/applications/circle_ai_contract_runner.py",
    "circle_math/applications/theseus_hive_contracts.py",
    "scripts/circle_ai_certify.py",
    "scripts/check_circle_ai_contract_docs.py",
    "scripts/check_circle_ai_contract_pack.py",
    "scripts/check_circle_ai_contract_acceptance_policy.py",
    "scripts/check_circle_ai_contract_runner.py",
    "scripts/check_circle_ai_certification_bundle.py",
    "scripts/check_circle_ai_receipt.py",
    "scripts/check_downstream_ci_acceptance_example.py",
    "scripts/circle_ai_contract_ready.py",
    "scripts/example_consume_circle_ai_contract_pack.py",
    "scripts/export_circle_ai_contracts.py",
    "scripts/generate_public_api_docs.py",
    "scripts/targeted_check.py",
    "docs/AI_CONTRACT_SUITE.md",
    "docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    "docs/CIRCLE_AI_CONTRACT_RUNNER.md",
    "docs/PUBLIC_API.md",
    "docs/USE_AS_LIBRARY.md",
    "docs/generated/PUBLIC_API_REFERENCE.md",
    "examples/circle_ai_contract_acceptance_policy.json",
    "examples/downstream_ci_accept_circle_ai_contracts.py",
    "examples/downstream_ci_verify_circle_ai_artifacts.py",
}

PUBLIC_API_SURFACE_PATHS = {
    "circle_math/ai_contracts.py",
    "circle_math/cli.py",
    "circle_math/applications/__init__.py",
    "scripts/generate_public_api_docs.py",
    "docs/PUBLIC_API.md",
    "docs/USE_AS_LIBRARY.md",
    "docs/generated/PUBLIC_API_REFERENCE.md",
}

AI_CONTRACT_GENERATED_PACK_ARTIFACTS = (
    "circle_ai_contract_pack.json",
    "circle_ai_contract_pack.schema.json",
    "circle_ai_contract_acceptance_policy.schema.json",
    "circle_ai_contract_acceptance_policy_report.schema.json",
    "circle_ai_contract_acceptance_receipt.schema.json",
    "circle_ai_downstream_rejection_report.schema.json",
    "circle_ai_contract_request.schema.json",
    "circle_ai_contract_request_validation.schema.json",
    "circle_ai_contract_receipt.schema.json",
    "circle_ai_contract_compact_receipt.schema.json",
    "circle_ai_contract_runner_check.schema.json",
    "circle_ai_contract_receipt_file_check.schema.json",
    "circle_ai_contract_receipt_replay_check.schema.json",
    "circle_ai_contract_certification_bundle.schema.json",
    "circle_ai_contract_certification_bundle_file_check.schema.json",
    "circle_ai_contract_artifact_manifest.schema.json",
    "circle_ai_contract_artifact_manifest_file_check.schema.json",
)


def ai_contract_impact(files: Iterable[str], *, full: bool = False) -> tuple[str, tuple[str, ...]]:
    if full:
        return "full_release", ALL_AI_CONTRACT_KINDS

    impacted: set[str] = set()
    all_contracts = False
    for raw_path in files:
        path = rel(raw_path)
        if (
            path in AI_CONTRACT_BROAD_SURFACE_PATHS
            or path in AI_CONTRACT_SHARED_SITE_PAGES
            or path.startswith("site/data/generated/circle_ai_contract_pack")
            or path.startswith("examples/circle_ai_requests/")
            or path.startswith("examples/circle_ai_model_configs/")
            or path.startswith("sidecars/PAPER_AI_")
            or "circle_ai_contract" in path
        ):
            all_contracts = True
            continue

        if path == "Makefile":
            makefile_topics = makefile_changed_topics()
            if "unknown" in makefile_topics or "ai_contract" in makefile_topics:
                all_contracts = True
            continue

        for mapping in (
            AI_CONTRACT_SITE_PAGE_KINDS,
            AI_CONTRACT_DOC_KINDS,
            AI_CONTRACT_CERTIFIER_PATH_KINDS,
            AI_CONTRACT_LEAN_PATH_KINDS,
        ):
            kind = mapping.get(path)
            if kind is not None:
                impacted.add(kind)

        if path.startswith("Circle/Applications/") and path.endswith(".lean"):
            if "RoPE" in path:
                impacted.add("rope_position_distinguishability")
            elif "Transformer" in path:
                impacted.add("sparse_attention_coverage")
        if path.startswith("Circle/Generative/") and path.endswith(".lean"):
            impacted.add("seed_rule_exact_regeneration")
        if path.startswith("sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/"):
            impacted.add("seed_rule_exact_regeneration")

    if all_contracts:
        return "all_contracts", ALL_AI_CONTRACT_KINDS
    if impacted:
        return "kind_specific", tuple(
            kind for kind in ALL_AI_CONTRACT_KINDS if kind in impacted
        )
    return "none", ()


def add_theseus_contract_checks(checks: list[Check], seen: set[tuple[str, ...]], reason: str) -> None:
    add(checks, seen, "Theseus transfer tests", pytest("tests/test_theseus_hive_ai_contracts.py", "tests/test_theseus_hive_feedback.py"), reason)
    add(checks, seen, "Theseus contract export", ("make", "theseus-ai-contracts"), reason)


PRIME_ENGINE_SCRIPT_TESTS = {
    "scripts/apply_prime_engine_defaults.py": ("tests/test_prime_engine_apply_defaults.py",),
    "scripts/benchmark_prime_external_controls.py": (
        "tests/test_external_prime_controls.py",
    ),
    "scripts/benchmark_prime_external_next.py": ("tests/test_external_prime_next.py",),
    "scripts/calibrate_prime_engine_defaults.py": (
        "tests/test_prime_engine_default_calibration.py",
    ),
    "scripts/check_prime_external_correctness.py": (
        "tests/test_prime_external_correctness.py",
    ),
    "scripts/check_prime_proof_contract.py": ("tests/test_prime_proof_contract.py",),
    "scripts/compare_prime_external_controls.py": (
        "tests/test_prime_external_control_compare.py",
    ),
    "scripts/compare_prime_external_next.py": (
        "tests/test_prime_external_next_compare.py",
    ),
    "scripts/compare_prime_engine_benchmarks.py": (
        "tests/test_prime_engine_benchmark_compare.py",
    ),
    "scripts/confirm_prime_external_modes.py": (
        "tests/test_prime_external_mode_confirm.py",
    ),
    "scripts/report_prime_engine_results.py": ("tests/test_prime_engine_report.py",),
    "scripts/tune_prime_engine.py": ("tests/test_prime_engine_tune.py",),
}

PRIME_ENGINE_RESULT_TESTS = {
    "prime_engine_default_calibration": (
        "tests/test_prime_engine_default_calibration.py",
    ),
    "prime_engine_external_mode_confirmation": (
        "tests/test_prime_external_mode_confirm.py",
    ),
    "prime_engine_high_offset_confirmation": (
        "tests/test_prime_external_mode_confirm.py",
    ),
    "prime_engine_report": ("tests/test_prime_engine_report.py",),
}


def add_prime_engine_tests(
    checks: list[Check],
    seen: set[tuple[str, ...]],
    tests: Iterable[str],
    reason: str,
) -> None:
    test_paths = tuple(dict.fromkeys(tests))
    if test_paths:
        add(checks, seen, "prime-engine targeted tests", pytest(*test_paths), reason)


def prime_engine_result_tests(path: str) -> tuple[str, ...]:
    if not path.startswith("sidecars/PRIME_ENGINE/results/"):
        return ()
    filename = Path(path).name
    tests: list[str] = []
    for stem, stem_tests in PRIME_ENGINE_RESULT_TESTS.items():
        if filename.startswith(stem):
            tests.extend(stem_tests)
    return tuple(dict.fromkeys(tests))


def add_rust_prime_checks(
    checks: list[Check],
    seen: set[tuple[str, ...]],
    reason: str,
) -> None:
    add(checks, seen, "Rust circle-prime tests", ("cargo", "test", "-p", "circle-prime"), reason)
    add(checks, seen, "Rust prime CLI tests", pytest("tests/test_rust_prime_cli.py"), reason)


def sidecar_python_tests(path: str) -> tuple[str, ...]:
    path_obj = ROOT / path
    if path_obj.name.startswith("test_") and path_obj.suffix == ".py":
        return (path,)
    if path_obj.parent.exists():
        tests = sorted(test_path for test_path in path_obj.parent.glob("test_*.py"))
        if tests:
            return tuple(rel(test_path) for test_path in tests)
    return ()


def sidecar_artifact_tests(path: str) -> tuple[str, ...]:
    parts = Path(path).parts
    if len(parts) < 3 or parts[0] != "sidecars":
        return ()
    sidecar_root = ROOT / parts[0] / parts[1]
    tests = sorted((sidecar_root / "python").glob("test_*.py"))
    return tuple(rel(test_path) for test_path in tests)


def plan_for_files(files: Iterable[str], *, full: bool = False) -> list[Check]:
    checks: list[Check] = []
    seen: set[tuple[str, ...]] = set()
    file_list = [rel(path) for path in files]

    if full:
        add(checks, seen, "full repository gate", ("make", "check"), "--full was requested")
        add(checks, seen, "render Living Book", ("make", "site-render"), "--full was requested")
        add(checks, seen, "validate rendered Living Book", ("make", "site-render-check"), "--full was requested")
        return checks

    if not file_list:
        add(checks, seen, "baseline manifest check", py("scripts/check_manifest.py"), "no changes detected")
        add(checks, seen, "baseline dictionary check", py("scripts/check_dictionary.py"), "no changes detected")
        return checks

    for path in file_list:
        suffix = Path(path).suffix

        if path == "examples/circle_ai_contract_acceptance_policy.json":
            add_circle_ai_contract_checks(
                checks,
                seen,
                f"{path} pins the downstream acceptance-policy gate",
            )

        if path == "Makefile":
            makefile_topics = makefile_changed_topics()
            add(
                checks,
                seen,
                "Makefile targeted-check smoke",
                ("make", "targeted-check-list", "TARGETED_FILES=scripts/targeted_check.py"),
                f"{path} changed",
            )
            if "targeted" in makefile_topics:
                add(
                    checks,
                    seen,
                    "targeted-check planner tests",
                    pytest("tests/test_targeted_check.py"),
                    f"{path} changed targeted-check wrapper targets",
                )
            if "prime_engine" in makefile_topics:
                add_prime_engine_tests(
                    checks,
                    seen,
                    (
                        "tests/test_prime_external_mode_confirm.py",
                        "tests/test_prime_engine_report.py",
                    ),
                    f"{path} changed prime-engine targets or defaults",
                )
            if "site" in makefile_topics:
                add_site_checks(checks, seen, f"{path} changed Living Book targets")
            if "unknown" in makefile_topics or "ai_contract" in makefile_topics:
                add(
                    checks,
                    seen,
                    "Circle AI contract readiness",
                    ("make", "circle-ai-contracts-ready"),
                    f"{path} changed AI-contract or unclassified validation targets",
                )

        if path in PUBLIC_API_SURFACE_PATHS:
            add_public_api_checks(checks, seen, f"{path} changed the packaged public API surface")

        if path in AI_CONTRACT_BROAD_SURFACE_PATHS:
            add_circle_ai_contract_checks(checks, seen, f"{path} changed public AI contract validation surface")

        if path.startswith("examples/circle_ai_requests/"):
            add_circle_ai_contract_checks(
                checks,
                seen,
                f"{path} changed a public AI contract request example",
            )

        if path.startswith("examples/circle_ai_model_configs/"):
            add_circle_ai_contract_checks(
                checks,
                seen,
                f"{path} changed a public AI model config example",
            )

        if path == "pyproject.toml" or path.startswith(".github/workflows/"):
            add(checks, seen, "full source checks", ("make", "sourcecheck"), f"{path} changes validation plumbing")

        if path in {"lakefile.lean", "lakefile.toml"}:
            add(checks, seen, "Lean build", ("lake", "build"), f"{path} changes Lean build configuration")

        if path.startswith("rust/circle-prime/"):
            add_rust_prime_checks(checks, seen, f"{path} changed executable prime-engine code")

        if path.startswith("Circle/") and suffix == ".lean":
            module = lean_module_name(path)
            if module is not None:
                add(checks, seen, f"Lean module build: {module}", ("lake", "build", module), f"{path} changed")
                if module != "Circle":
                    add(
                        checks,
                        seen,
                        "Lean aggregate build: Circle",
                        ("lake", "build", "Circle"),
                        (
                            f"{path} changed; manifest Lean-name checks import "
                            "the aggregate Circle module"
                        ),
                    )
            else:
                add(checks, seen, f"Lean file: {path}", ("lake", "env", "lean", path), f"{path} changed")
            add(checks, seen, "fake-proof guard", py("scripts/check_no_fake_proofs.py"), f"{path} changed")
            add(checks, seen, "manifest Lean names", py("scripts/check_manifest_lean_names.py"), f"{path} changed")
            if path.startswith("Circle/Generative/"):
                add(checks, seen, "generative sidecar tests", pytest("sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changes a contract-backed generative proof", "seed_rule_exact_regeneration")
            if path.startswith("Circle/Applications/"):
                add(checks, seen, "application guardrails", py("scripts/check_application_guardrails.py"), f"{path} is an application Lean file")
                add(checks, seen, "proof-depth audit", py("scripts/check_proof_depth_audit.py", "--fail-on-review-required"), f"{path} is an application Lean file")
                contract_kind = AI_CONTRACT_LEAN_PATH_KINDS.get(path)
                if contract_kind is None:
                    if "RoPE" in path:
                        contract_kind = "rope_position_distinguishability"
                    elif "Transformer" in path:
                        contract_kind = "sparse_attention_coverage"
                if contract_kind is not None:
                    if contract_kind == "rope_position_distinguishability":
                        add(
                            checks,
                            seen,
                            "RoPE certifier tests",
                            pytest("tests/test_rope_certifier.py"),
                            (
                                f"{path} changes RoPE proof metadata or theorem "
                                "trails used by generated preset result sidecars"
                            ),
                        )
                    add_circle_ai_contract_kind_checks(
                        checks,
                        seen,
                        f"{path} changes a contract-backed application proof",
                        contract_kind,
                    )

        if path.startswith("sidecars/") and suffix == ".lean":
            add(checks, seen, "Lean sidecars", py("scripts/check_lean_sidecars.py"), f"{path} changed")
            add(checks, seen, "fake-proof guard", py("scripts/check_no_fake_proofs.py"), f"{path} changed")

        if path.startswith("sidecars/") and suffix == ".py":
            sidecar_tests = sidecar_python_tests(path)
            if sidecar_tests:
                add(checks, seen, "sidecar Python tests", pytest(*sidecar_tests), f"{path} changed")
            else:
                add(checks, seen, "sidecar Python syntax", (PYTHON, "-m", "py_compile", path), f"{path} changed")
            if "PAPER_GEN_01_SEED_RULE_PROVENANCE" in path:
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} feeds the seed-rule contract fixture", "seed_rule_exact_regeneration")

        if path.startswith("sidecars/") and "/results/" in path and suffix in {".json", ".md"}:
            sidecar_tests = sidecar_artifact_tests(path)
            if sidecar_tests:
                add(checks, seen, "sidecar artifact tests", pytest(*sidecar_tests), f"{path} is a generated sidecar artifact")
            if "PAPER_AI_" in path or "PAPER_GEN_" in path:
                add_circle_ai_contract_checks(checks, seen, f"{path} feeds public AI contract fixtures")

        if path.startswith("tests/") and path.endswith(".py"):
            add(checks, seen, f"pytest: {path}", pytest(path), f"{path} changed")

        if suffix == ".py" and not path.startswith("tests/"):
            prime_tests = PRIME_ENGINE_SCRIPT_TESTS.get(path)
            if prime_tests is not None:
                add_prime_engine_tests(
                    checks,
                    seen,
                    prime_tests,
                    f"{path} changed prime-engine validation plumbing",
                )
            if path_matches(path, "rope", "phase_bank", "generate_rope"):
                add(checks, seen, "RoPE certifier tests", pytest("tests/test_rope_certifier.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "rope_position_distinguishability")
            if path_matches(path, "kv_cache"):
                add(checks, seen, "KV-cache certifier tests", pytest("tests/test_kv_cache_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "kv_cache_ring_buffer")
            if path_matches(path, "recurrence_schedule_certify"):
                add(checks, seen, "recurrence schedule certifier tests", pytest("tests/test_recurrence_schedule_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "recurrence_schedule")
            if path_matches(path, "strided_candidate_fanout_certify"):
                add(checks, seen, "strided candidate-fanout certifier tests", pytest("tests/test_strided_candidate_fanout_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "strided_candidate_fanout")
            if path_matches(path, "cyclic_memory_certify"):
                add(checks, seen, "cyclic memory certifier tests", pytest("tests/test_cyclic_memory_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "cyclic_memory_residue_winding")
            if path_matches(path, "multicoil_phase_feature_certify"):
                add(checks, seen, "multicoil phase-feature certifier tests", pytest("tests/test_multicoil_phase_feature_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "multicoil_phase_feature")
            if path_matches(path, "circulant_block_cyclic_mixer_certify"):
                add(checks, seen, "circulant/block-cyclic mixer certifier tests", pytest("tests/test_circulant_block_cyclic_mixer_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "circulant_block_cyclic_mixer")
            if path_matches(path, "seed_rule_certify"):
                add(checks, seen, "seed-rule certifier tests", pytest("tests/test_seed_rule_certifier_cli.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} changed", "seed_rule_exact_regeneration")
            if path == "circle_math/applications/circle_ai.py":
                add(checks, seen, "KV-cache certifier tests", pytest("tests/test_kv_cache_certifier_cli.py"), f"{path} changed")
            if path_matches(path, "stride_family", "circle_transformer") or path == "circle_math/applications/circle_ai.py":
                add(checks, seen, "sparse/AI contract tests", pytest("tests/test_stride_family_certifier_cli.py", "tests/test_circle_transformer.py"), f"{path} changed")
            if path_matches(path, "theseus_hive"):
                add_theseus_contract_checks(checks, seen, f"{path} changed")
                add_circle_ai_contract_checks(checks, seen, f"{path} changed")
            if path_matches(path, "circle_ai", "circle_ai_contract", "export_circle_ai_contracts"):
                add_circle_ai_contract_checks(checks, seen, f"{path} changed")
            if path_matches(path, "circle_ai_contract", "export_circle_ai_contracts"):
                add_circle_ai_contract_checks(checks, seen, f"{path} changed")
            if path_matches(path, "check_circle_ai_contract_docs"):
                add(checks, seen, "Circle AI contract docs", py("scripts/check_circle_ai_contract_docs.py"), f"{path} changed")
            if path == "circle_math/generative.py":
                add(checks, seen, "generative sidecar tests", pytest("sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py"), f"{path} changed")
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} feeds the seed-rule contract fixture", "seed_rule_exact_regeneration")
                add_site_checks(checks, seen, f"{path} feeds generated Living Book fixtures", widgets=True)
            if path.startswith("circle_math/dimensions/"):
                add(checks, seen, "dimension Python tests", pytest("tests/dimensions/test_dimensional_scaffolding.py"), f"{path} changed")
            if (
                path.startswith("circle_math/")
                and not path.startswith("circle_math/applications/")
                and path != "circle_math/generative.py"
                and path not in PUBLIC_API_SURFACE_PATHS
            ):
                add(checks, seen, "core Python tests", pytest("tests/test_rotation.py", "tests/test_orbit_period.py", "tests/test_winding.py", "tests/test_scaling.py", "tests/test_prime_coils.py"), f"{path} changed")
            if path.startswith("scripts/site/"):
                add_site_checks(checks, seen, f"{path} changed", widgets="widget" in path)
                test_path = "tests/site/test_" + Path(path).stem.removeprefix("check_") + ".py"
                if (ROOT / test_path).exists():
                    add(checks, seen, f"pytest: {test_path}", pytest(test_path), f"{path} changed")
            elif path.startswith("scripts/"):
                stem = Path(path).stem
                candidate_tests = [
                    f"tests/test_{stem}.py",
                    f"tests/test_{stem}_cli.py",
                    f"tests/test_{stem.removeprefix('check_')}.py",
                    f"tests/test_{stem.removeprefix('check_')}_cli.py",
                ]
                for test_path in dict.fromkeys(candidate_tests):
                    if (ROOT / test_path).exists():
                        add(checks, seen, f"pytest: {test_path}", pytest(test_path), f"{path} changed")

        if path.startswith("dictionary/") and suffix in {".yaml", ".yml", ".json"}:
            add(checks, seen, "dictionary", py("scripts/check_dictionary.py"), f"{path} changed")
            add(checks, seen, "paper theorem links", py("scripts/check_paper_theorem_links.py"), f"{path} changed")
            add_site_checks(checks, seen, f"{path} changed")

        if path.startswith("manifests/") and suffix in {".yaml", ".yml", ".json"}:
            add(checks, seen, "manifest", py("scripts/check_manifest.py"), f"{path} changed")
            add(checks, seen, "manifest Lean names", py("scripts/check_manifest_lean_names.py"), f"{path} changed")
            add(checks, seen, "paper manifest", py("scripts/check_paper_manifest.py"), f"{path} changed")
            add(checks, seen, "paper theorem links", py("scripts/check_paper_theorem_links.py"), f"{path} changed")
            add(checks, seen, "research manifests", py("scripts/check_research_manifests.py"), f"{path} changed")
            add(checks, seen, "capability showcase", py("scripts/check_capability_showcase.py"), f"{path} changed")
            if path_matches(path, "phase4"):
                add(checks, seen, "phase 4 targets", py("scripts/check_phase4_targets.py"), f"{path} changed")
            if path_matches(path, "phase5"):
                add(checks, seen, "phase 5 targets", py("scripts/check_phase5_targets.py"), f"{path} changed")
            if path_matches(path, "phase6"):
                add(checks, seen, "phase 6 targets", py("scripts/check_phase6_sweep_targets.py"), f"{path} changed")
            if path_matches(path, "phase7"):
                add(checks, seen, "phase 7 targets", py("scripts/check_phase7_targets.py"), f"{path} changed")
            if path_matches(path, "phase8"):
                add(checks, seen, "phase 8 targets", py("scripts/check_phase8_targets.py"), f"{path} changed")
            if path.startswith("manifests/dimensions/"):
                add(checks, seen, "dimension manifests", py("scripts/check_dimension_manifests.py"), f"{path} changed")
            add_site_checks(checks, seen, f"{path} changed")

        if path.startswith("papers/") and suffix == ".md":
            add(checks, seen, "paper manifest", py("scripts/check_paper_manifest.py"), f"{path} changed")
            add(checks, seen, "paper theorem links", py("scripts/check_paper_theorem_links.py"), f"{path} changed")
            add(checks, seen, "paper source trails", py("scripts/check_paper_source_trails.py"), f"{path} changed")
            add(checks, seen, "claim language", py("scripts/check_claim_language.py"), f"{path} changed")
            add_site_checks(checks, seen, f"{path} changed")

        if (path.startswith("docs/") and suffix == ".md") or path == "README.md":
            add(checks, seen, "claim language", py("scripts/check_claim_language.py"), f"{path} changed")
            add(checks, seen, "site static source links", py("scripts/site/check_site_static_source_links.py"), f"{path} changed")
            contract_doc_kind = AI_CONTRACT_DOC_KINDS.get(path)
            if contract_doc_kind is not None:
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} documents {contract_doc_kind}", contract_doc_kind)
            if path == "docs/ROPE_CERTIFIER_QUICKSTART.md":
                add(
                    checks,
                    seen,
                    "RoPE quickstart precursor drift test",
                    pytest(
                        "tests/test_rope_certifier.py::test_rope_quickstart_precursor_line_matches_certifier_constant"
                    ),
                    f"{path} includes generated theorem-id trails",
                )
            if path in {"docs/AI_CONTRACT_SUITE.md", "docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md"}:
                add(checks, seen, "Circle AI contract docs", py("scripts/check_circle_ai_contract_docs.py"), f"{path} documents the public contract pack")
                add_circle_ai_contract_checks(checks, seen, f"{path} documents the public contract pack")

        if path.startswith("site/") and suffix in {".qmd", ".html", ".js", ".css", ".yml", ".yaml"}:
            add_site_checks(checks, seen, f"{path} changed", widgets=path.startswith("site/widgets/"))
            contract_site_kind = AI_CONTRACT_SITE_PAGE_KINDS.get(path)
            if contract_site_kind is not None:
                add_circle_ai_contract_kind_checks(checks, seen, f"{path} documents {contract_site_kind}", contract_site_kind)
            if path in AI_CONTRACT_SHARED_SITE_PAGES:
                add_circle_ai_contract_checks(checks, seen, f"{path} documents the public AI contract pack")
            if path == "site/chapters/applications/ai_contract_pack_audit.qmd":
                add(checks, seen, "Circle AI contract docs", py("scripts/check_circle_ai_contract_docs.py"), f"{path} documents the public contract pack")
            if path == "site/showcase.qmd":
                add(checks, seen, "capability showcase", py("scripts/check_capability_showcase.py"), f"{path} mirrors capability manifest evidence")
            if path.startswith("site/widgets/"):
                add(checks, seen, "site widget pytest", pytest("tests/site/test_site_widget_contracts.py", "tests/site/test_widget_python_parity.py"), f"{path} changed")
            if suffix == ".qmd":
                add(checks, seen, "site source-link pytest", pytest("tests/site/test_site_source_links.py", "tests/site/test_site_static_source_links.py"), f"{path} changed")

        if path.startswith("site/data/generated/") and suffix == ".json":
            add_site_checks(checks, seen, f"{path} changed")
            if path.endswith(AI_CONTRACT_GENERATED_PACK_ARTIFACTS):
                add_circle_ai_contract_checks(checks, seen, f"{path} is the public contract pack artifact")
            if path.endswith("theseus_hive_ai_contracts.json"):
                add_theseus_contract_checks(checks, seen, f"{path} is the compatibility contract artifact")
            if path.endswith("capability_showcase.json"):
                add(checks, seen, "capability showcase", py("scripts/check_capability_showcase.py"), f"{path} mirrors capability manifest evidence")

        result_prime_tests = prime_engine_result_tests(path)
        if result_prime_tests:
            add_prime_engine_tests(
                checks,
                seen,
                result_prime_tests,
                f"{path} is a generated prime-engine result artifact",
            )

    if not checks:
        add(checks, seen, "manifest", py("scripts/check_manifest.py"), "fallback for unclassified changes")
        add(checks, seen, "dictionary", py("scripts/check_dictionary.py"), "fallback for unclassified changes")
    return checks


def print_plan(checks: list[Check], files: list[str], *, full: bool = False) -> None:
    ai_scope, ai_kinds = ai_contract_impact(files, full=full)
    strict_receipt_kinds = strict_receipt_kinds_from_checks(checks)
    print("targeted-check changed files:")
    if files:
        for path in files:
            print(f"  - {path}")
    else:
        print("  - <none>")
    if full:
        print("targeted-check validation scope: full release")
        print("targeted-check release gate required before publication: no")
    else:
        print("targeted-check validation scope: targeted edit-loop")
        print("targeted-check release gate required before publication: yes")
    print(f"targeted-check AI contract validation scope: {ai_scope}")
    print(
        "targeted-check impacted AI contract kinds: "
        + (", ".join(ai_kinds) if ai_kinds else "<none>")
    )
    print(
        "targeted-check strict receipt kinds: "
        + (", ".join(strict_receipt_kinds) if strict_receipt_kinds else "<none>")
    )
    print("targeted-check plan:")
    for index, check in enumerate(checks, start=1):
        print(f"  {index}. {check.label}: {' '.join(check.command)}")
        print(f"     reason: {check.reason}")


def plan_payload(
    checks: list[Check],
    files: list[str],
    *,
    full: bool = False,
) -> dict[str, object]:
    ai_scope, ai_kinds = ai_contract_impact(files, full=full)
    strict_receipt_kinds = strict_receipt_kinds_from_checks(checks)
    return {
        "changed_files": files,
        "changed_file_count": len(files),
        "check_count": len(checks),
        "validation_scope": "full_release" if full else "targeted_edit_loop",
        "release_gate_required": not full,
        "release_gate_commands": [] if full else ["make check", "make living-book-check"],
        "ai_contract_validation_scope": ai_scope,
        "impacted_ai_contract_kinds": list(ai_kinds),
        "strict_receipt_kinds": list(strict_receipt_kinds),
        "checks": [
            {
                "label": check.label,
                "command": list(check.command),
                "reason": check.reason,
            }
            for check in checks
        ],
    }


def run_checks(checks: list[Check]) -> int:
    for check in checks:
        print(f"\n==> {check.label}")
        print("+ " + " ".join(check.command))
        sys.stdout.flush()
        result = subprocess.run(check.command, cwd=ROOT)
        if result.returncode != 0:
            print(f"targeted-check failed at: {check.label}", file=sys.stderr)
            return result.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git base revision for committed-change detection.")
    parser.add_argument("--files", nargs="*", help="Explicit changed files; bypass git detection.")
    parser.add_argument("--list", action="store_true", help="Print the plan without running commands.")
    parser.add_argument("--full", action="store_true", help="Run the full repository and Living Book gates.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for --list plan output.",
    )
    args = parser.parse_args()

    if args.format == "json" and not args.list:
        parser.error("--format json is only supported with --list")

    files = changed_files(base=args.base, explicit=args.files or ())
    checks = plan_for_files(files, full=args.full)
    if args.list:
        if args.format == "json":
            print(json.dumps(plan_payload(checks, files, full=args.full), indent=2, sort_keys=True))
        else:
            print_plan(checks, files, full=args.full)
        return 0
    print_plan(checks, files, full=args.full)
    sys.stdout.flush()
    return run_checks(checks)


if __name__ == "__main__":
    raise SystemExit(main())
