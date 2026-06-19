from __future__ import annotations

from pathlib import Path

from circle_math.applications.circle_ai_contracts import build_contract_pack
from circle_math.applications.theseus_hive_contracts import (
    build_contract_pack as build_theseus_contract_pack,
)
from scripts.check_circle_ai_contract_docs import (
    DEFAULT_ACCEPTANCE_POLICY_DOCS,
    DEFAULT_DOCS,
    DEFAULT_FAMILY_DOCS,
    DEFAULT_GUIDED_SUITE_DOCS,
    DEFAULT_STRICT_RECEIPT_DOCS,
    DEFAULT_SUMMARY_DOCS,
    validate_acceptance_policy_docs,
    validate_contract_family_summaries,
    validate_contract_source_trails,
    validate_doc_tables,
    validate_guided_suite_docs,
    validate_strict_flagship_receipt_docs,
    validate_strict_flagship_receipt_pack,
    validate_strict_sparse_receipt_docs,
)


def test_ai_contract_docs_cover_generated_minimum_fields() -> None:
    failures = validate_doc_tables(build_contract_pack(), DEFAULT_DOCS)

    assert failures == []


def test_ai_contract_docs_cover_public_families_and_compatibility_count() -> None:
    failures = validate_contract_family_summaries(
        build_contract_pack(),
        family_doc_paths=DEFAULT_FAMILY_DOCS,
        summary_doc_paths=DEFAULT_SUMMARY_DOCS,
        compatibility_pack=build_theseus_contract_pack(),
    )

    assert failures == []


def test_ai_contract_docs_cover_acceptance_policy_surface() -> None:
    failures = validate_acceptance_policy_docs(
        build_contract_pack(),
        doc_paths=DEFAULT_ACCEPTANCE_POLICY_DOCS,
    )

    assert failures == []


def test_ai_contract_guided_suite_docs_do_not_use_stale_version_label() -> None:
    failures = validate_guided_suite_docs(DEFAULT_GUIDED_SUITE_DOCS)

    assert failures == []


def test_ai_contract_docs_use_strict_flagship_receipts() -> None:
    failures = validate_strict_flagship_receipt_docs(DEFAULT_STRICT_RECEIPT_DOCS)

    assert failures == []


def test_ai_contract_docs_use_strict_sparse_receipts_alias() -> None:
    failures = validate_strict_sparse_receipt_docs(DEFAULT_STRICT_RECEIPT_DOCS)

    assert failures == []


def test_ai_contract_pack_uses_strict_flagship_receipts() -> None:
    failures = validate_strict_flagship_receipt_pack(build_contract_pack())

    assert failures == []


def test_ai_contract_source_trails_resolve_generated_paths() -> None:
    failures = validate_contract_source_trails(build_contract_pack())

    assert failures == []


def test_ai_contract_docs_validator_reports_missing_minimum_field(tmp_path: Path) -> None:
    pack = {
        "contract_schema": {
            "minimum_fields_by_kind": {
                "demo_contract": ["field_a", "field_b"],
            },
        },
    }
    doc = tmp_path / "demo.md"
    doc.write_text(
        "\n".join(
            [
                "| Contract kind | Minimum fields to read |",
                "| --- | --- |",
                "| `demo_contract` | `field_a` |",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_doc_tables(pack, (doc,))

    assert len(failures) == 1
    assert "demo_contract row omits minimum fields ['field_b']" in failures[0]


def test_ai_contract_docs_validator_reports_missing_public_family(tmp_path: Path) -> None:
    pack = {
        "contracts": [{"kind": "demo_a"}, {"kind": "demo_b"}],
        "contract_schema": {
            "minimum_fields_by_kind": {
                "demo_a": [],
                "demo_b": [],
            },
        },
    }
    family_doc = tmp_path / "family.md"
    family_doc.write_text("`demo_a`\n", encoding="utf-8")
    summary_doc = tmp_path / "summary.md"
    summary_doc.write_text("two contract families\n", encoding="utf-8")

    failures = validate_contract_family_summaries(
        pack,
        family_doc_paths=(family_doc,),
        summary_doc_paths=(summary_doc,),
    )

    assert len(failures) == 1
    assert "omits public contract family ids ['demo_b']" in failures[0]


def test_ai_contract_docs_validator_reports_stale_public_summary_phrase(
    tmp_path: Path,
) -> None:
    pack = {
        "contracts": [{"kind": "demo_a"}],
        "contract_schema": {"minimum_fields_by_kind": {"demo_a": []}},
    }
    family_doc = tmp_path / "family.md"
    family_doc.write_text("`demo_a`\n", encoding="utf-8")
    summary_doc = tmp_path / "summary.md"
    summary_doc.write_text(
        "public-safe generic fixture pack for recurrence, fanout, memory, "
        "phase-feature, mixer, and seed-rule experiments\n",
        encoding="utf-8",
    )

    failures = validate_contract_family_summaries(
        pack,
        family_doc_paths=(family_doc,),
        summary_doc_paths=(summary_doc,),
    )

    assert len(failures) == 1
    assert "stale contract-pack summary phrase" in failures[0]


def test_ai_contract_docs_validator_reports_missing_acceptance_policy_token(
    tmp_path: Path,
) -> None:
    pack = {
        "acceptance_policy": {
            "schema_id": "circle_calculus.ai_contract_acceptance_policy.v0",
            "report_schema_id": "circle_calculus.ai_contract_acceptance_policy_report.v0",
            "receipt_schema_id": "circle_calculus.ai_contract_acceptance_receipt.v0",
            "rejection_report_schema_id": (
                "circle_calculus.downstream_ci_rejection_report.v0"
            ),
            "policy_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_policy.schema.json"
            ),
            "report_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_policy_report.schema.json"
            ),
            "receipt_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_receipt.schema.json"
            ),
            "rejection_report_schema_path": (
                "site/data/generated/"
                "circle_ai_downstream_rejection_report.schema.json"
            ),
            "default_policy_path": "examples/circle_ai_contract_acceptance_policy.json",
            "checker": "scripts/check_circle_ai_contract_acceptance_policy.py",
            "standalone_checker": "examples/downstream_ci_accept_circle_ai_contracts.py",
            "fingerprint_refresh_command": (
                "python scripts/circle_ai_contract_ready.py --print-refreshed-policy"
            ),
            "pinned_requirement_keys": [
                "required_fields",
                "required_theorem_ids",
            ],
            "validation_commands": [
                "python scripts/check_circle_ai_contract_acceptance_policy.py --format json",
            ],
        },
    }
    doc = tmp_path / "policy.md"
    doc.write_text(
        "\n".join(
            [
                "acceptance_policy",
                "python scripts/circle_ai_contract_ready.py --acceptance-policy",
                "circle_calculus.ai_contract_acceptance_policy.v0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_acceptance_policy_docs(pack, doc_paths=(doc,))

    assert len(failures) == 1
    assert "acceptance-policy docs omit generated tokens" in failures[0]
    assert "circle_calculus.ai_contract_acceptance_policy_report.v0" in failures[0]


def test_ai_contract_guided_suite_validator_reports_stale_version_label(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "suite.md"
    doc.write_text(
        "Use the four v0.2 flagship contracts as a guided suite.\n",
        encoding="utf-8",
    )

    failures = validate_guided_suite_docs((doc,))

    assert len(failures) == 1
    assert "stale guided-suite label" in failures[0]
    assert "four v0.2 flagship contracts" in failures[0]


def test_ai_contract_docs_validator_reports_weak_sparse_receipt(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "suite.md"
    doc.write_text(
        "\n".join(
            [
                "```bash",
                "python scripts/circle_ai_contract_ready.py \\",
                "  --kind sparse_attention_coverage \\",
                "  --receipt \\",
                "  --field first_uncovered_lag \\",
                "  --field complete_repair_window \\",
                "  --require-theorem AIT-T0104 \\",
                "  --require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_strict_sparse_receipt_docs((doc,))

    assert len(failures) == 1
    assert "weak sparse_attention_coverage receipt command" in failures[0]
    assert "--field first_uncovered_interval_start" in failures[0]
    assert "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172" in failures[0]


def test_ai_contract_docs_validator_reports_weak_rope_receipt(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "suite.md"
    doc.write_text(
        "\n".join(
            [
                "```bash",
                "python scripts/circle_ai_contract_ready.py \\",
                "  --kind rope_position_distinguishability \\",
                "  --receipt \\",
                "  --field d19_proved_request_status \\",
                "  --require-theorem AIRA-T0171 \\",
                "  --require-recommendation ROPE-USE-D19-MARGIN-FRONTIER",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_strict_flagship_receipt_docs((doc,))

    assert len(failures) == 1
    assert "weak rope_position_distinguishability receipt command" in failures[0]
    assert "--field d19_undecided_request_status" in failures[0]
    assert "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234" in failures[0]


def test_ai_contract_docs_validator_reports_weak_kv_receipt(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "suite.md"
    doc.write_text(
        "\n".join(
            [
                "```bash",
                "python scripts/circle_ai_contract_ready.py \\",
                "  --kind kv_cache_ring_buffer \\",
                "  --receipt \\",
                "  --field stale_probe_first_stale_token \\",
                "  --require-theorem AIM-T0103 \\",
                "  --require-recommendation KV-DROP-STALE-REQUEST-TOKEN",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_strict_flagship_receipt_docs((doc,))

    assert len(failures) == 1
    assert "weak kv_cache_ring_buffer receipt command" in failures[0]
    assert "--field sink_tokens_retained_by_policy" in failures[0]
    assert "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149" in failures[0]


def test_ai_contract_docs_validator_reports_weak_recurrence_receipt(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "suite.md"
    doc.write_text(
        "\n".join(
            [
                "```bash",
                "python scripts/circle_ai_contract_ready.py \\",
                "  --kind recurrence_schedule \\",
                "  --receipt \\",
                "  --field total_active_token_work \\",
                "  --require-theorem AIM-T0130 \\",
                "  --require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_strict_flagship_receipt_docs((doc,))

    assert len(failures) == 1
    assert "weak recurrence_schedule receipt command" in failures[0]
    assert "--field periodic_shift_required_steps_invariant" in failures[0]
    assert "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026" in failures[0]


def test_ai_contract_docs_validator_reports_missing_pack_receipt() -> None:
    pack = build_contract_pack()
    contract = next(
        contract
        for contract in pack["contracts"]
        if contract["kind"] == "rope_position_distinguishability"
    )
    contract["validation_commands"] = [
        command
        for command in contract["validation_commands"]
        if "--receipt" not in command
    ]

    failures = validate_strict_flagship_receipt_pack(pack)

    assert len(failures) == 1
    assert (
        "rope_position_distinguishability: validation_commands must include "
        "a strict receipt command"
    ) in failures[0]


def test_ai_contract_docs_validator_reports_weak_pack_receipt() -> None:
    pack = build_contract_pack()
    contract = next(
        contract
        for contract in pack["contracts"]
        if contract["kind"] == "kv_cache_ring_buffer"
    )
    contract["validation_commands"] = [
        (
            "python scripts/circle_ai_contract_ready.py "
            "--kind kv_cache_ring_buffer --receipt "
            "--field stale_probe_first_stale_token "
            "--require-theorem AIM-T0103"
        )
    ]

    failures = validate_strict_flagship_receipt_pack(pack)

    assert len(failures) == 1
    assert "kv_cache_ring_buffer.validation_commands contains weak" in failures[0]
    assert "--field sink_tokens_retained_by_policy" in failures[0]


def test_ai_contract_docs_validator_reports_missing_standalone_selector(
    tmp_path: Path,
) -> None:
    pack = {
        "acceptance_policy": {
            "schema_id": "circle_calculus.ai_contract_acceptance_policy.v0",
            "report_schema_id": "circle_calculus.ai_contract_acceptance_policy_report.v0",
            "receipt_schema_id": "circle_calculus.ai_contract_acceptance_receipt.v0",
            "rejection_report_schema_id": (
                "circle_calculus.downstream_ci_rejection_report.v0"
            ),
            "policy_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_policy.schema.json"
            ),
            "report_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_policy_report.schema.json"
            ),
            "receipt_schema_path": (
                "site/data/generated/"
                "circle_ai_contract_acceptance_receipt.schema.json"
            ),
            "rejection_report_schema_path": (
                "site/data/generated/"
                "circle_ai_downstream_rejection_report.schema.json"
            ),
            "default_policy_path": "examples/circle_ai_contract_acceptance_policy.json",
            "checker": "scripts/check_circle_ai_contract_acceptance_policy.py",
            "standalone_checker": "examples/downstream_ci_accept_circle_ai_contracts.py",
            "fingerprint_refresh_command": (
                "python scripts/circle_ai_contract_ready.py --print-refreshed-policy"
            ),
            "pinned_requirement_keys": [
                "required_fields",
                "required_theorem_ids",
            ],
            "validation_commands": [
                "python scripts/check_circle_ai_contract_acceptance_policy.py --format json",
            ],
        },
    }
    doc = tmp_path / "policy.md"
    doc.write_text(
        "\n".join(
            [
                "acceptance_policy",
                "python scripts/circle_ai_contract_ready.py --acceptance-policy",
                "circle_calculus.ai_contract_acceptance_policy.v0",
                "circle_calculus.ai_contract_acceptance_policy_report.v0",
                "circle_calculus.ai_contract_acceptance_receipt.v0",
                "circle_calculus.downstream_ci_rejection_report.v0",
                "site/data/generated/circle_ai_contract_acceptance_policy.schema.json",
                "site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json",
                "site/data/generated/circle_ai_contract_acceptance_receipt.schema.json",
                "site/data/generated/circle_ai_downstream_rejection_report.schema.json",
                "examples/circle_ai_contract_acceptance_policy.json",
                "scripts/check_circle_ai_contract_acceptance_policy.py",
                "examples/downstream_ci_accept_circle_ai_contracts.py",
                (
                    "python scripts/check_circle_ai_contract_acceptance_policy.py "
                    "--print-refreshed-policy"
                ),
                "required_fields",
                "required_theorem_ids",
                "python scripts/check_circle_ai_contract_acceptance_policy.py --format json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    failures = validate_acceptance_policy_docs(pack, doc_paths=(doc,))

    assert len(failures) == 1
    assert "--planner-recommendation RECOMMENDATION_ID" in failures[0]
    assert "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR" in failures[0]
    assert "ROPE-USE-D19-MARGIN-FRONTIER" in failures[0]
    assert "classifier_regions" in failures[0]
    assert "undecided_margin_gap" in failures[0]


def test_ai_contract_docs_validator_reports_missing_source_trail_path() -> None:
    pack = build_contract_pack()
    pack["contracts"][0]["quickstart_docs"] = ["docs/DOES_NOT_EXIST.md"]

    failures = validate_contract_source_trails(pack)

    assert len(failures) == 1
    assert "quickstart_docs path does not exist" in failures[0]
    assert "docs/DOES_NOT_EXIST.md" in failures[0]


def test_ai_contract_docs_validator_reports_missing_command_reference() -> None:
    pack = build_contract_pack()
    pack["contracts"][0]["validation_commands"] = [
        "python scripts/does_not_exist.py --format json",
    ]

    failures = validate_contract_source_trails(pack)

    assert len(failures) == 1
    assert "validation_commands command references missing path" in failures[0]
    assert "scripts/does_not_exist.py" in failures[0]
