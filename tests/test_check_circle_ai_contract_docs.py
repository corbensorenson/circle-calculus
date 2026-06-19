from __future__ import annotations

from pathlib import Path

from circle_math.applications.circle_ai_contracts import build_contract_pack
from circle_math.applications.theseus_hive_contracts import (
    build_contract_pack as build_theseus_contract_pack,
)
from scripts.check_circle_ai_contract_docs import (
    DEFAULT_DOCS,
    DEFAULT_FAMILY_DOCS,
    DEFAULT_SUMMARY_DOCS,
    validate_contract_family_summaries,
    validate_doc_tables,
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
