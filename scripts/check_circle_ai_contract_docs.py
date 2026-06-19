from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"
DEFAULT_DOCS = (
    ROOT / "docs" / "AI_CONTRACT_SUITE.md",
    ROOT / "docs" / "CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_pack_audit.qmd",
)
DEFAULT_COMPAT_PACK = ROOT / "site" / "data" / "generated" / "theseus_hive_ai_contracts.json"
DEFAULT_FAMILY_DOCS = (
    ROOT / "docs" / "AI_CONTRACT_SUITE.md",
    ROOT / "docs" / "CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_pack_audit.qmd",
)
DEFAULT_SUMMARY_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    ROOT / "docs" / "THESEUS_HIVE_AI_TRANSFER.md",
    ROOT / "docs" / "PHASE2_AND_APPLICATIONS.md",
)
CONTRACT_KIND_RE = re.compile(r"`([^`]+)`")
COUNT_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
}
FORBIDDEN_STALE_SUMMARY_PHRASES = (
    "Both exported packs currently contain six deterministic contract families",
    "public-safe generic fixture pack for recurrence, fanout, memory, phase-feature, mixer, and seed-rule experiments",
)


def _repo_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_pack(path: Path = DEFAULT_PACK) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _contract_field_rows(path: Path) -> dict[str, tuple[str, ...]]:
    rows: dict[str, tuple[str, ...]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        tokens = CONTRACT_KIND_RE.findall(cells[0] + " " + cells[1])
        if len(tokens) < 2:
            continue
        kind = tokens[0]
        rows[kind] = tuple(tokens[1:])
    return rows


def _contract_kinds(pack: dict[str, Any]) -> tuple[str, ...]:
    contracts = pack.get("contracts")
    if isinstance(contracts, list):
        kinds = [contract.get("kind") for contract in contracts if isinstance(contract, dict)]
        return tuple(kind for kind in kinds if isinstance(kind, str))
    schema = pack.get("contract_schema")
    if isinstance(schema, dict):
        minimum_fields = schema.get("minimum_fields_by_kind")
        if isinstance(minimum_fields, dict):
            return tuple(str(kind) for kind in minimum_fields)
    return ()


def _count_tokens(count: int) -> tuple[str, ...]:
    tokens = [str(count)]
    word = COUNT_WORDS.get(count)
    if word is not None:
        tokens.append(word)
    return tuple(tokens)


def validate_doc_tables(
    pack: dict[str, Any],
    doc_paths: Iterable[Path] = DEFAULT_DOCS,
) -> list[str]:
    failures: list[str] = []
    schema = pack.get("contract_schema")
    if not isinstance(schema, dict):
        return ["pack is missing contract_schema"]
    minimum_fields = schema.get("minimum_fields_by_kind")
    if not isinstance(minimum_fields, dict):
        return ["pack is missing contract_schema.minimum_fields_by_kind"]

    for path in doc_paths:
        if not path.exists():
            failures.append(f"missing contract docs file: {_repo_path(path)}")
            continue
        rows = _contract_field_rows(path)
        for kind, fields in sorted(minimum_fields.items()):
            if not isinstance(fields, list):
                failures.append(f"{kind}: minimum fields must be a list")
                continue
            if kind not in rows:
                failures.append(f"{_repo_path(path)}: missing contract field row for {kind}")
                continue
            documented = set(rows[kind])
            missing = [field for field in fields if field not in documented]
            if missing:
                failures.append(
                    f"{_repo_path(path)}: {kind} row omits minimum fields {missing}"
                )
    return failures


def validate_contract_family_summaries(
    pack: dict[str, Any],
    family_doc_paths: Iterable[Path] = DEFAULT_FAMILY_DOCS,
    summary_doc_paths: Iterable[Path] = DEFAULT_SUMMARY_DOCS,
    compatibility_pack: dict[str, Any] | None = None,
) -> list[str]:
    failures: list[str] = []
    public_kinds = _contract_kinds(pack)
    if not public_kinds:
        return ["pack has no contract families"]

    public_kind_set = set(public_kinds)
    schema = pack.get("contract_schema")
    if isinstance(schema, dict):
        minimum_fields = schema.get("minimum_fields_by_kind")
        if isinstance(minimum_fields, dict) and set(minimum_fields) != public_kind_set:
            failures.append(
                "pack contracts and contract_schema.minimum_fields_by_kind disagree: "
                f"contracts={sorted(public_kind_set)} "
                f"minimum_fields={sorted(minimum_fields)}"
            )

    summary_paths = tuple(summary_doc_paths)
    for path in summary_paths:
        if not path.exists():
            failures.append(f"missing contract summary docs file: {_repo_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_STALE_SUMMARY_PHRASES:
            if phrase in text:
                failures.append(
                    f"{_repo_path(path)} contains stale contract-pack summary phrase: "
                    f"{phrase!r}"
                )
        if path.name == "CIRCLE_AI_CONTRACTS_INTEGRATION.md":
            lower_text = text.lower()
            count_tokens = _count_tokens(len(public_kinds))
            if not any(f"{token} contract families" in lower_text for token in count_tokens):
                failures.append(
                    f"{_repo_path(path)} does not state the public "
                    f"contract-family count {len(public_kinds)}"
                )

    for path in family_doc_paths:
        if not path.exists():
            failures.append(f"missing contract family docs file: {_repo_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [kind for kind in public_kinds if f"`{kind}`" not in text]
        if missing:
            failures.append(
                f"{_repo_path(path)} omits public contract family ids {missing}"
            )

    if compatibility_pack is not None:
        compatibility_count = len(_contract_kinds(compatibility_pack))
        if compatibility_count:
            compatibility_tokens = _count_tokens(compatibility_count)
            compatibility_docs = (
                ROOT / "README.md",
                ROOT / "docs" / "THESEUS_HIVE_AI_TRANSFER.md",
                ROOT / "docs" / "PHASE2_AND_APPLICATIONS.md",
            )
            for path in compatibility_docs:
                if not path.exists():
                    failures.append(
                        f"missing compatibility summary docs file: {_repo_path(path)}"
                    )
                    continue
                text = path.read_text(encoding="utf-8").lower()
                has_count = any(
                    f"{token} downstream-transfer" in text
                    or f"{token} compatibility" in text
                    for token in compatibility_tokens
                )
                if not has_count:
                    failures.append(
                        f"{_repo_path(path)} does not distinguish the "
                        f"compatibility contract-family count {compatibility_count}"
                    )

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that AI contract docs and Living Book tables mention every "
            "generated minimum consumer field."
        )
    )
    parser.add_argument(
        "--pack",
        default=str(DEFAULT_PACK),
        help="Path to generated circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--compat-pack",
        default=str(DEFAULT_COMPAT_PACK),
        help=(
            "Optional compatibility pack used to verify public-vs-compatibility "
            "family-count wording."
        ),
    )
    parser.add_argument(
        "--doc",
        action="append",
        default=[],
        help="Contract docs file to check. Repeat to override the default docs set.",
    )
    args = parser.parse_args()

    pack_path = Path(args.pack)
    if not pack_path.is_absolute():
        pack_path = ROOT / pack_path
    doc_paths = tuple(Path(doc) if Path(doc).is_absolute() else ROOT / doc for doc in args.doc)
    if not doc_paths:
        doc_paths = DEFAULT_DOCS

    compatibility_pack = None
    compat_path = Path(args.compat_pack)
    if not compat_path.is_absolute():
        compat_path = ROOT / compat_path
    if compat_path.exists():
        compatibility_pack = load_pack(compat_path)

    pack = load_pack(pack_path)
    failures = [
        *validate_doc_tables(pack, doc_paths),
        *validate_contract_family_summaries(
            pack,
            compatibility_pack=compatibility_pack,
        ),
    ]
    if failures:
        for failure in failures:
            print(f"circle AI contract docs error: {failure}", file=sys.stderr)
        return 1
    print("circle AI contract docs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
