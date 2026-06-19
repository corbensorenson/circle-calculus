from __future__ import annotations

import json
import subprocess
import sys

from scripts.check_circle_ai_contract_docs import STRICT_RECEIPT_TOKENS_BY_KIND
from scripts.targeted_check import plan_for_files, plan_payload


def commands_for(files: list[str], *, full: bool = False) -> list[tuple[str, ...]]:
    return [check.command for check in plan_for_files(files, full=full)]


def contains_command(commands: list[tuple[str, ...]], *parts: str) -> bool:
    joined = [" ".join(command) for command in commands]
    return any(all(part in command for part in parts) for command in joined)


def assert_kind_contract_checks(commands: list[tuple[str, ...]], kind: str) -> None:
    assert contains_command(commands, "scripts/export_circle_ai_contracts.py")
    assert contains_command(commands, "scripts/check_circle_ai_contract_pack.py")
    assert contains_command(commands, "scripts/check_circle_ai_contract_docs.py")
    assert contains_command(
        commands,
        "scripts/circle_ai_contract_ready.py",
        "--kind",
        kind,
    )
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def strict_receipt_command(commands: list[tuple[str, ...]], kind: str) -> str | None:
    for command in commands:
        joined = " ".join(command)
        if (
            "scripts/circle_ai_contract_ready.py" in joined
            and f"--kind {kind}" in joined
            and "--receipt" in joined
        ):
            return joined
    return None


def assert_strict_receipt_check(commands: list[tuple[str, ...]], kind: str) -> None:
    joined = strict_receipt_command(commands, kind)
    assert joined is not None
    assert "--format json" in joined
    for token in STRICT_RECEIPT_TOKENS_BY_KIND[kind]:
        assert token in joined


def test_plan_payload_is_machine_readable() -> None:
    files = ["scripts/targeted_check.py"]
    checks = plan_for_files(files)
    payload = plan_payload(checks, files)

    assert payload["changed_files"] == files
    assert payload["changed_file_count"] == 1
    assert payload["check_count"] == len(checks)
    assert payload["validation_scope"] == "targeted_edit_loop"
    assert payload["release_gate_required"] is True
    assert payload["release_gate_commands"] == ["make check", "make living-book-check"]
    assert payload["ai_contract_validation_scope"] == "all_contracts"
    assert "sparse_attention_coverage" in payload["impacted_ai_contract_kinds"]
    assert {
        "kv_cache_ring_buffer",
        "recurrence_schedule",
        "rope_position_distinguishability",
        "sparse_attention_coverage",
    }.issubset(set(payload["strict_receipt_kinds"]))
    assert isinstance(payload["checks"], list)
    assert payload["checks"]
    first_check = payload["checks"][0]
    assert set(first_check) == {"label", "command", "reason"}
    assert isinstance(first_check["command"], list)


def test_targeted_check_cli_emits_json_plan() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/targeted_check.py",
            "--files",
            "scripts/targeted_check.py",
            "--list",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["changed_files"] == ["scripts/targeted_check.py"]
    assert payload["validation_scope"] == "targeted_edit_loop"
    assert payload["release_gate_required"] is True
    assert payload["ai_contract_validation_scope"] == "all_contracts"
    assert "rope_position_distinguishability" in payload["strict_receipt_kinds"]
    assert any(
        "tests/test_targeted_check.py" in " ".join(check["command"])
        for check in payload["checks"]
    )


def test_targeted_check_cli_emits_full_json_plan_metadata() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/targeted_check.py",
            "--full",
            "--list",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["validation_scope"] == "full_release"
    assert payload["release_gate_required"] is False
    assert payload["release_gate_commands"] == []
    assert payload["ai_contract_validation_scope"] == "full_release"
    assert "rope_position_distinguishability" in payload["impacted_ai_contract_kinds"]
    assert any(
        "make check" in " ".join(check["command"])
        for check in payload["checks"]
    )


def test_targeted_check_text_plan_labels_release_gate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/targeted_check.py",
            "--files",
            "scripts/targeted_check.py",
            "--list",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "targeted-check validation scope: targeted edit-loop" in result.stdout
    assert (
        "targeted-check release gate required before publication: yes"
        in result.stdout
    )
    assert (
        "targeted-check AI contract validation scope: all_contracts"
        in result.stdout
    )
    assert (
        "targeted-check strict receipt kinds: "
        in result.stdout
    )


def test_plan_payload_reports_kind_specific_ai_contract_scope() -> None:
    files = ["scripts/seed_rule_certify.py"]
    checks = plan_for_files(files)
    payload = plan_payload(checks, files)

    assert payload["ai_contract_validation_scope"] == "kind_specific"
    assert payload["impacted_ai_contract_kinds"] == ["seed_rule_exact_regeneration"]
    assert payload["strict_receipt_kinds"] == []


def test_plan_payload_reports_no_ai_contract_scope_for_core_math() -> None:
    files = ["circle_math/core.py"]
    checks = plan_for_files(files)
    payload = plan_payload(checks, files)

    assert payload["ai_contract_validation_scope"] == "none"
    assert payload["impacted_ai_contract_kinds"] == []
    assert payload["strict_receipt_kinds"] == []


def test_rope_python_change_runs_rope_tests_without_full_suite() -> None:
    commands = commands_for(["circle_math/applications/rope_certifier.py"])

    assert contains_command(commands, "pytest", "tests/test_rope_certifier.py")
    assert ("make", "check") not in commands
    assert ("make", "sourcecheck") not in commands


def test_application_lean_change_runs_local_lean_and_guardrails() -> None:
    commands = commands_for(["Circle/Applications/RoPECertifier.lean"])

    assert ("lake", "env", "lean", "Circle/Applications/RoPECertifier.lean") not in commands
    assert ("lake", "build", "Circle.Applications.RoPECertifier") in commands
    assert contains_command(commands, "scripts/check_manifest_lean_names.py")
    assert contains_command(commands, "scripts/check_application_guardrails.py")
    assert contains_command(commands, "scripts/check_proof_depth_audit.py", "--fail-on-review-required")
    assert_kind_contract_checks(commands, "rope_position_distinguishability")


def test_rope_frontier_lean_change_runs_rope_contract_checks() -> None:
    commands = commands_for(["Circle/Applications/RoPEFrontier.lean"])

    assert ("lake", "build", "Circle.Applications.RoPEFrontier") in commands
    assert contains_command(commands, "scripts/check_application_guardrails.py")
    assert_kind_contract_checks(commands, "rope_position_distinguishability")
    assert contains_command(
        commands,
        "scripts/circle_ai_contract_ready.py",
        "--digest",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_bank_tolerance_rule",
    )
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_transformer_lean_change_runs_sparse_contract_checks() -> None:
    commands = commands_for(["Circle/Applications/CircleTransformer.lean"])

    assert ("lake", "build", "Circle.Applications.CircleTransformer") in commands
    assert contains_command(commands, "scripts/check_application_guardrails.py")
    assert_kind_contract_checks(commands, "sparse_attention_coverage")
    assert contains_command(
        commands,
        "scripts/circle_ai_contract_ready.py",
        "--digest",
        "complete_repair_window",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
    )
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_flagship_kind_specific_changes_run_strict_receipt_checks() -> None:
    path_kinds = {
        "docs/ROPE_CERTIFIER_QUICKSTART.md": "rope_position_distinguishability",
        "docs/KV_CACHE_CERTIFIER_QUICKSTART.md": "kv_cache_ring_buffer",
        "site/chapters/applications/sparse_attention_contract.qmd": (
            "sparse_attention_coverage"
        ),
        "scripts/recurrence_schedule_certify.py": "recurrence_schedule",
    }

    for path, kind in path_kinds.items():
        commands = commands_for([path])

        assert_kind_contract_checks(commands, kind)
        assert_strict_receipt_check(commands, kind)
        assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_secondary_kind_specific_changes_do_not_run_flagship_receipts() -> None:
    commands = commands_for(["scripts/seed_rule_certify.py"])

    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert strict_receipt_command(commands, "seed_rule_exact_regeneration") is None


def test_site_widget_change_runs_widget_checks() -> None:
    commands = commands_for(["site/widgets/S1/coil_orbit_explorer.js"])

    assert contains_command(commands, "scripts/site/export_site_data.py")
    assert contains_command(commands, "scripts/site/check_site_widget_contracts.py")
    assert contains_command(commands, "scripts/site/check_widget_python_parity.py")
    assert contains_command(commands, "pytest", "tests/site/test_site_widget_contracts.py")


def test_generated_site_data_change_runs_site_checks() -> None:
    commands = commands_for(["site/data/generated/theorem_manifest.json"])

    assert contains_command(commands, "scripts/site/export_site_data.py")
    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "scripts/site/check_site_theorem_status.py")
    assert contains_command(commands, "scripts/site/check_site_data_backlinks.py")


def test_manifest_phase8_change_runs_phase8_and_site_checks() -> None:
    commands = commands_for(["manifests/phase8_depth_validation.yaml"])

    assert contains_command(commands, "scripts/check_phase8_targets.py")
    assert contains_command(commands, "scripts/check_manifest.py")
    assert contains_command(commands, "scripts/site/export_site_data.py")
    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")


def test_validation_script_change_runs_matching_test_when_present() -> None:
    commands = commands_for(["scripts/targeted_check.py"])

    assert contains_command(commands, "pytest", "tests/test_targeted_check.py")


def test_prime_calibration_script_change_runs_calibration_tests() -> None:
    commands = commands_for(["scripts/calibrate_prime_engine_defaults.py"])

    assert contains_command(
        commands,
        "pytest",
        "tests/test_prime_engine_default_calibration.py",
    )
    assert ("make", "check") not in commands


def test_prime_engine_result_artifacts_run_matching_local_tests() -> None:
    paths_and_tests = {
        "sidecars/PRIME_ENGINE/results/prime_engine_default_calibration_latest.md": (
            "tests/test_prime_engine_default_calibration.py"
        ),
        "sidecars/PRIME_ENGINE/results/prime_engine_high_offset_confirmation_latest.md": (
            "tests/test_prime_external_mode_confirm.py"
        ),
        "sidecars/PRIME_ENGINE/results/prime_engine_report_latest.md": (
            "tests/test_prime_engine_report.py"
        ),
    }

    for path, test_path in paths_and_tests.items():
        commands = commands_for([path])

        assert contains_command(commands, "pytest", test_path)
        assert ("make", "check") not in commands


def test_rust_prime_engine_change_runs_cargo_and_cli_tests() -> None:
    commands = commands_for(["rust/circle-prime/src/segmented.rs"])

    assert ("cargo", "test", "-p", "circle-prime") in commands
    assert contains_command(commands, "pytest", "tests/test_rust_prime_cli.py")
    assert ("make", "check") not in commands


def test_makefile_change_uses_targeted_smoke_without_sourcecheck() -> None:
    commands = commands_for(["Makefile"])

    assert contains_command(commands, "make", "targeted-check-list")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert ("make", "sourcecheck") not in commands
    assert ("make", "check") not in commands


def test_pyproject_change_still_uses_full_sourcecheck() -> None:
    commands = commands_for(["pyproject.toml"])

    assert ("make", "sourcecheck") in commands


def test_generic_contract_pack_change_runs_pack_tests() -> None:
    commands = commands_for(["circle_math/applications/circle_ai_contracts.py"])

    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_circle_ai_contract_acceptance_policy.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_example_consume_circle_ai_contract_pack.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_downstream_ci_accept_circle_ai_contracts.py",
    )
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert not contains_command(commands, "pytest", "tests/test_stride_family_certifier_cli.py")
    assert ("make", "check") not in commands


def test_generic_contract_exporter_change_runs_pack_tests_not_sparse_tests() -> None:
    commands = commands_for(["scripts/export_circle_ai_contracts.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_circle_ai_contract_acceptance_policy.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_example_consume_circle_ai_contract_pack.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_downstream_ci_accept_circle_ai_contracts.py",
    )


def test_standalone_downstream_ci_example_change_runs_standalone_tests() -> None:
    commands = commands_for(["examples/downstream_ci_accept_circle_ai_contracts.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_downstream_ci_accept_circle_ai_contracts.py",
    )
    assert not contains_command(commands, "pytest", "tests/test_stride_family_certifier_cli.py")


def test_standalone_downstream_schema_checker_change_runs_standalone_tests() -> None:
    commands = commands_for(["scripts/check_downstream_ci_acceptance_example.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_downstream_ci_accept_circle_ai_contracts.py",
    )


def test_recurrence_certifier_change_runs_recurrence_and_pack_tests() -> None:
    commands = commands_for(["scripts/recurrence_schedule_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_recurrence_schedule_certifier_cli.py")
    assert_kind_contract_checks(commands, "recurrence_schedule")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_seed_rule_certifier_change_runs_seed_rule_and_pack_tests() -> None:
    commands = commands_for(["scripts/seed_rule_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_seed_rule_certifier_cli.py")
    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_cyclic_memory_certifier_change_runs_memory_and_pack_tests() -> None:
    commands = commands_for(["scripts/cyclic_memory_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_cyclic_memory_certifier_cli.py")
    assert_kind_contract_checks(commands, "cyclic_memory_residue_winding")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_strided_candidate_fanout_certifier_change_runs_fanout_and_pack_tests() -> None:
    commands = commands_for(["scripts/strided_candidate_fanout_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_strided_candidate_fanout_certifier_cli.py")
    assert_kind_contract_checks(commands, "strided_candidate_fanout")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_multicoil_phase_feature_certifier_change_runs_phase_and_pack_tests() -> None:
    commands = commands_for(["scripts/multicoil_phase_feature_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_multicoil_phase_feature_certifier_cli.py")
    assert_kind_contract_checks(commands, "multicoil_phase_feature")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_circulant_block_cyclic_mixer_certifier_change_runs_mixer_and_pack_tests() -> None:
    commands = commands_for(["scripts/circulant_block_cyclic_mixer_certify.py"])

    assert contains_command(commands, "pytest", "tests/test_circulant_block_cyclic_mixer_certifier_cli.py")
    assert_kind_contract_checks(commands, "circulant_block_cyclic_mixer")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_contract_ready_consumer_change_runs_cli_tests() -> None:
    commands = commands_for(["scripts/circle_ai_contract_ready.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_ready_cli.py")


def test_contract_docs_validator_change_runs_docs_check_and_tests() -> None:
    commands = commands_for(["scripts/check_circle_ai_contract_docs.py"])

    assert contains_command(commands, "scripts/check_circle_ai_contract_docs.py")
    assert contains_command(commands, "pytest", "tests/test_check_circle_ai_contract_docs.py")


def test_contract_docs_change_runs_contract_docs_check() -> None:
    commands = commands_for(["docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md"])

    assert contains_command(commands, "scripts/check_circle_ai_contract_docs.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")


def test_contract_quickstart_doc_change_runs_kind_check_not_all_contracts() -> None:
    commands = commands_for(["docs/SEED_RULE_CERTIFIER_QUICKSTART.md"])

    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert contains_command(commands, "scripts/site/check_site_static_source_links.py")
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_kv_quickstart_doc_change_digest_includes_sink_policy_fields() -> None:
    commands = commands_for(["docs/KV_CACHE_CERTIFIER_QUICKSTART.md"])

    assert_kind_contract_checks(commands, "kv_cache_ring_buffer")
    assert contains_command(
        commands,
        "scripts/circle_ai_contract_ready.py",
        "--digest",
        "sink_tokens_retained_by_policy",
        "sink_window_exact_policy",
        "sink_tokens_outside_ordinary_rolling_window",
    )
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_rope_review_packet_change_runs_rope_check_not_all_contracts() -> None:
    commands = commands_for(["docs/ROPE_CERTIFIER_REVIEW_PACKET.md"])

    assert_kind_contract_checks(commands, "rope_position_distinguishability")
    assert contains_command(commands, "scripts/site/check_site_static_source_links.py")
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")


def test_ai_contract_living_book_change_runs_contract_docs_check() -> None:
    commands = commands_for(["site/chapters/applications/ai_contract_pack_audit.qmd"])

    assert contains_command(commands, "scripts/check_circle_ai_contract_docs.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")


def test_ai_contract_suite_lesson_change_runs_contract_pack_checks() -> None:
    commands = commands_for(["site/chapters/applications/ai_contract_suite.qmd"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert not contains_command(commands, "scripts/check_circle_ai_contract_docs.py")


def test_ai_contract_ladder_pages_run_broad_contract_checks() -> None:
    for path in (
        "site/chapters/applications/ai_contract_ladder.qmd",
        "site/chapters/applications/ai_contract_ladder_audit.qmd",
    ):
        commands = commands_for([path])

        assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
        assert contains_command(commands, "make", "circle-ai-contracts-ready")
        assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
        assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_flagship_contract_lesson_change_runs_contract_pack_checks() -> None:
    commands = commands_for(["site/chapters/applications/sparse_attention_contract.qmd"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert_kind_contract_checks(commands, "sparse_attention_coverage")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_secondary_contract_lesson_changes_run_kind_specific_checks() -> None:
    page_kinds = {
        "site/chapters/applications/strided_candidate_fanout.qmd": (
            "strided_candidate_fanout"
        ),
        "site/chapters/applications/cyclic_memory_residue_winding.qmd": (
            "cyclic_memory_residue_winding"
        ),
        "site/chapters/applications/multicoil_phase_feature.qmd": (
            "multicoil_phase_feature"
        ),
        "site/chapters/applications/circulant_block_cyclic_mixer.qmd": (
            "circulant_block_cyclic_mixer"
        ),
    }

    for page, kind in page_kinds.items():
        commands = commands_for([page])

        assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
        assert_kind_contract_checks(commands, kind)
        assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
        assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_contract_consumer_adapter_change_runs_consumer_tests() -> None:
    commands = commands_for(["circle_math/applications/circle_ai_contract_consumer.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_circle_ai_contract_acceptance_policy.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_example_consume_circle_ai_contract_pack.py",
    )


def test_contract_acceptance_policy_change_runs_policy_gate_tests() -> None:
    commands = commands_for(["examples/circle_ai_contract_acceptance_policy.json"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(
        commands,
        "pytest",
        "tests/test_circle_ai_contract_acceptance_policy.py",
    )
    assert contains_command(
        commands,
        "pytest",
        "tests/test_example_consume_circle_ai_contract_pack.py",
    )


def test_theseus_compatibility_source_change_runs_public_and_compatibility_checks() -> None:
    commands = commands_for(["circle_math/applications/theseus_hive_contracts.py"])

    assert contains_command(commands, "make", "theseus-ai-contracts")
    assert contains_command(commands, "pytest", "tests/test_theseus_hive_ai_contracts.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")


def test_circle_ai_model_change_runs_contract_pack_check() -> None:
    commands = commands_for(["circle_math/applications/circle_ai.py"])

    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_stride_family_certifier_cli.py")
    assert ("make", "check") not in commands


def test_generative_python_change_runs_seed_rule_and_pack_checks() -> None:
    commands = commands_for(["circle_math/generative.py"])

    assert contains_command(commands, "pytest", "sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py")
    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert contains_command(commands, "scripts/site/check_widget_python_parity.py")
    assert not contains_command(commands, "pytest", "tests/test_rotation.py")
    assert ("make", "check") not in commands


def test_generative_lean_change_runs_seed_rule_pack_checks() -> None:
    commands = commands_for(["Circle/Generative/SeedRule.lean"])

    assert ("lake", "env", "lean", "Circle/Generative/SeedRule.lean") not in commands
    assert ("lake", "build", "Circle.Generative.SeedRule") in commands
    assert contains_command(commands, "pytest", "sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py")
    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_generative_sidecar_python_change_runs_local_sidecar_test_and_pack_checks() -> None:
    commands = commands_for([
        "sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py"
    ])

    assert contains_command(commands, "pytest", "sidecars/PAPER_GEN_01_SEED_RULE_PROVENANCE/python/test_seed_rule_provenance_examples.py")
    assert_kind_contract_checks(commands, "seed_rule_exact_regeneration")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert not contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")


def test_ai_sidecar_result_change_runs_sidecar_and_pack_checks() -> None:
    commands = commands_for([
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/stride_family_sparse_attention.json"
    ])

    assert contains_command(
        commands,
        "pytest",
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/test_memory_slot_examples.py",
    )
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_consumer.py")
    assert ("make", "check") not in commands


def test_non_ai_sidecar_result_change_runs_local_sidecar_tests_only() -> None:
    commands = commands_for([
        "sidecars/PAPER_01_FINITE_CIRCLES/results/example.json"
    ])

    assert contains_command(
        commands,
        "pytest",
        "sidecars/PAPER_01_FINITE_CIRCLES/python/test_paper_01_examples.py",
    )
    assert not contains_command(commands, "make", "circle-ai-contracts-ready")
    assert ("make", "check") not in commands


def test_contract_pack_json_change_runs_pack_validator() -> None:
    commands = commands_for(["site/data/generated/circle_ai_contract_pack.json"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")


def test_contract_pack_schema_json_change_runs_pack_validator() -> None:
    commands = commands_for(["site/data/generated/circle_ai_contract_pack.schema.json"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "make", "circle-ai-contracts-ready")
    assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")


def test_acceptance_policy_schema_json_change_runs_pack_validator() -> None:
    paths = [
        "site/data/generated/circle_ai_contract_acceptance_policy.schema.json",
        "site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json",
        "site/data/generated/circle_ai_contract_acceptance_receipt.schema.json",
        "site/data/generated/circle_ai_downstream_rejection_report.schema.json",
    ]

    for path in paths:
        commands = commands_for([path])

        assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
        assert contains_command(commands, "make", "circle-ai-contracts-ready")
        assert contains_command(commands, "pytest", "tests/test_circle_ai_contract_pack.py")


def test_theseus_contract_json_change_runs_compatibility_validator() -> None:
    commands = commands_for(["site/data/generated/theseus_hive_ai_contracts.json"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "pytest", "tests/test_theseus_hive_ai_contracts.py")
    assert contains_command(commands, "make", "theseus-ai-contracts")


def test_showcase_page_change_runs_capability_showcase_check() -> None:
    commands = commands_for(["site/showcase.qmd"])

    assert contains_command(commands, "scripts/site/check_site_manifest_links.py")
    assert contains_command(commands, "scripts/check_capability_showcase.py")


def test_full_mode_is_explicit_release_gate() -> None:
    commands = commands_for(["circle_math/applications/rope_certifier.py"], full=True)

    assert commands == [
        ("make", "check"),
        ("make", "site-render"),
        ("make", "site-render-check"),
    ]
