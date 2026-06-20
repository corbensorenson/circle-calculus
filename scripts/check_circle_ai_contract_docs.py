from __future__ import annotations

import argparse
import json
import re
import shlex
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
DEFAULT_ACCEPTANCE_POLICY_DOCS = (
    ROOT / "docs" / "AI_CONTRACT_SUITE.md",
    ROOT / "docs" / "CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_pack_audit.qmd",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_suite.qmd",
)
DEFAULT_GUIDED_SUITE_DOCS = (
    ROOT / "docs" / "AI_CONTRACT_SUITE.md",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_suite.qmd",
)
DEFAULT_STRICT_RECEIPT_DOCS = (
    ROOT / "docs" / "AI_CONTRACT_SUITE.md",
    ROOT / "docs" / "CIRCLE_AI_CONTRACTS_INTEGRATION.md",
    ROOT / "site" / "chapters" / "applications" / "ai_contract_suite.qmd",
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
FORBIDDEN_STALE_GUIDED_SUITE_PHRASES = (
    "four v0.2 flagship contracts",
)
LOCAL_SOURCE_PREFIXES = (
    "Circle/",
    "circle_math/",
    "docs/",
    "examples/",
    "manifests/",
    "papers/",
    "scripts/",
    "sidecars/",
    "site/",
    "tests/",
)
STRICT_ROPE_RECEIPT_TOKENS = (
    "--field d19_proved_request_status",
    "--field d19_impossible_request_status",
    "--field d19_undecided_request_status",
    "--field d19_proved_first_channel_bank_transfer",
    "--field d19_proved_first_channel_bank_shape",
    "--field d19_proved_first_channel_pair_scope",
    "--field d19_proved_first_channel_context_wide_contract",
    "--field d19_proved_first_channel_radian_bank_form",
    "--field d19_proved_first_channel_bank_tolerance_rule",
    "--field d19_undecided_probe_margin_in_open_gap",
    "--require-theorem AIRA-T0171",
    "--require-theorem AIRA-T0172",
    "--require-theorem AIRA-T0234",
    "--require-theorem AIRA-T0235",
    "--require-theorem AIRA-T0236",
    "--require-theorem AIRA-T0237",
    "--require-theorem AIRA-T0238",
    "--require-recommendation ROPE-USE-D19-MARGIN-FRONTIER",
    (
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_bank_transfer"
    ),
    (
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_context_wide_contract"
    ),
    (
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_radian_bank_form"
    ),
    (
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_undecided_probe_margin_in_open_gap"
    ),
    (
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234"
    ),
    (
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235"
    ),
    (
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236"
    ),
    (
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237"
    ),
    (
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0238"
    ),
    (
        "--require-recommendation-action-parameter "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.context_wide_contract"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.radian_bank_form"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids"
    ),
)
STRICT_KV_RECEIPT_TOKENS = (
    "--field stale_probe_first_stale_token",
    "--field sink_tokens_retained_by_policy",
    "--field sink_window_exact_policy",
    "--field sink_window_tokens_distinct",
    "--field sink_prefix_disjoint_from_live_window",
    "--field sink_tokens_outside_ordinary_rolling_window",
    "--require-theorem AIM-T0103",
    "--require-theorem AIM-T0104",
    "--require-theorem AIM-T0149",
    "--require-recommendation KV-DROP-STALE-REQUEST-TOKEN",
    "--require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST",
    (
        "--require-recommendation-evidence-field "
        "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token"
    ),
    (
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_retained_by_policy"
    ),
    (
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_outside_ordinary_rolling_window"
    ),
    (
        "--require-recommendation-theorem "
        "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103"
    ),
    (
        "--require-recommendation-theorem "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149"
    ),
    (
        "--require-recommendation-action-parameter "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token"
    ),
    (
        "--require-recommendation-action-parameter "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current"
    ),
)
STRICT_SPARSE_RECEIPT_TOKENS = (
    "--field first_uncovered_lag",
    "--field first_uncovered_interval_start",
    "--field complete_repair_window",
    "--field complete_repair_window_covers_context",
    "--field complete_repair_window_minimal_for_declared_stride_family",
    "--field complete_repair_window_minimal_witness_lag",
    "--require-theorem AIT-T0104",
    "--require-theorem AIT-T0172",
    "--require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
    "--require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
    (
        "--require-recommendation-evidence-field "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=local_window_complete_threshold_is_exact_local_minimum"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_for_declared_stride_family"
    ),
    (
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169"
    ),
    (
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170"
    ),
    (
        "--require-recommendation-action-parameter "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window"
    ),
    (
        "--require-recommendation-action-parameter "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window"
    ),
    (
        "--require-recommendation-action-parameter "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots"
    ),
)
STRICT_RECURRENCE_RECEIPT_TOKENS = (
    "--field periodic_shift_required_steps_invariant",
    "--field periodic_shift_active_at_step_invariant",
    "--field total_active_token_work",
    "--field scheduled_work_saving",
    "--field scheduled_work_saving_accounting",
    "--field active_inactive_work_accounting",
    "--field scheduled_work_saving_positive",
    "--field post_period_multi_extension_scheduled_work_saving",
    "--require-theorem AIM-T0026",
    "--require-theorem AIM-T0130",
    "--require-theorem AIM-T0159",
    "--require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
    "--require-recommendation RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
    (
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=total_active_token_work"
    ),
    (
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving"
    ),
    (
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving"
    ),
    (
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_required_steps_invariant"
    ),
    (
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=periodic_shift_active_at_step_invariant"
    ),
    (
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130"
    ),
    (
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159"
    ),
    (
        "--require-recommendation-theorem "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026"
    ),
    (
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period"
    ),
    (
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving"
    ),
    (
        "--require-recommendation-action-parameter "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=post_period_multi_extension_scheduled_work_saving"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token"
    ),
    (
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount"
    ),
)
STRICT_RECEIPT_TOKENS_BY_KIND = {
    "rope_position_distinguishability": STRICT_ROPE_RECEIPT_TOKENS,
    "kv_cache_ring_buffer": STRICT_KV_RECEIPT_TOKENS,
    "sparse_attention_coverage": STRICT_SPARSE_RECEIPT_TOKENS,
    "recurrence_schedule": STRICT_RECURRENCE_RECEIPT_TOKENS,
}


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


def _repo_reference_exists(reference: str) -> bool:
    path = Path(reference)
    if path.is_absolute():
        return path.exists()
    return (ROOT / path).exists()


def _local_command_references(command: str) -> tuple[str, ...]:
    tokens = shlex.split(command)
    return tuple(
        token
        for token in tokens
        if token.startswith(LOCAL_SOURCE_PREFIXES)
    )


def _fenced_code_blocks(text: str) -> tuple[str, ...]:
    blocks: list[str] = []
    current: list[str] = []
    in_block = False
    for line in text.splitlines():
        if line.startswith("```"):
            if in_block:
                blocks.append("\n".join(current))
                current = []
            in_block = not in_block
            continue
        if in_block:
            current.append(line)
    return tuple(blocks)


def _shell_commands_from_block(block: str) -> tuple[str, ...]:
    commands: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                commands.append(" ".join(current))
                current = []
            continue
        starts_command = stripped.startswith(("python ", "make "))
        if starts_command and current and not current[-1].rstrip().endswith("\\"):
            commands.append(" ".join(current))
            current = []
        if starts_command or current:
            current.append(stripped.rstrip("\\").strip())
            if not stripped.endswith("\\"):
                commands.append(" ".join(current))
                current = []
    if current:
        commands.append(" ".join(current))
    return tuple(commands)


def _documented_shell_commands(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    commands: list[str] = []
    for block in _fenced_code_blocks(text):
        commands.extend(_shell_commands_from_block(block))
    return tuple(commands)


def _strict_receipt_command_failures(
    commands: Iterable[str],
    *,
    surface: str,
) -> list[str]:
    failures: list[str] = []
    for command in commands:
        if "--receipt" not in command:
            continue
        for kind, required_tokens in STRICT_RECEIPT_TOKENS_BY_KIND.items():
            if f"--kind {kind}" not in command:
                continue
            missing = [
                token
                for token in required_tokens
                if token not in command
            ]
            if missing:
                failures.append(
                    f"{surface} contains weak {kind} receipt command; "
                    f"missing {missing}"
                )
    return failures


def _required_string_list(
    contract: dict[str, Any],
    key: str,
    *,
    kind: str,
) -> tuple[list[str], list[str]]:
    value = contract.get(key)
    if not isinstance(value, list) or not value:
        return [], [f"{kind}: {key} must be a non-empty list"]
    strings = [item for item in value if isinstance(item, str) and item]
    if len(strings) != len(value):
        return strings, [f"{kind}: {key} must contain only non-empty strings"]
    return strings, []


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


def validate_acceptance_policy_docs(
    pack: dict[str, Any],
    doc_paths: Iterable[Path] = DEFAULT_ACCEPTANCE_POLICY_DOCS,
) -> list[str]:
    failures: list[str] = []
    policy = pack.get("acceptance_policy")
    if not isinstance(policy, dict):
        return ["pack is missing acceptance_policy"]

    docs: dict[Path, str] = {}
    for path in doc_paths:
        if not path.exists():
            failures.append(f"missing acceptance-policy docs file: {_repo_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        docs[path] = text
        if "acceptance_policy" not in text and "--acceptance-policy" not in text:
            failures.append(
                f"{_repo_path(path)} omits the generated acceptance-policy surface"
            )

    combined = "\n".join(docs.values())
    required_tokens = [
        "python scripts/circle_ai_contract_ready.py --acceptance-policy",
        (
            "python examples/downstream_ci_accept_circle_ai_contracts.py "
            "--format json --planner-recommendation "
            "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values"
        ),
        (
            "python examples/downstream_ci_accept_circle_ai_contracts.py "
            "--format json --planner-recommendation "
            "ROPE-USE-D19-MARGIN-FRONTIER --include-values"
        ),
        "classifier_regions",
        "undecided_margin_gap",
        "--planner-recommendation RECOMMENDATION_ID",
        str(policy.get("schema_id", "")),
        str(policy.get("report_schema_id", "")),
        str(policy.get("receipt_schema_id", "")),
        str(policy.get("rejection_report_schema_id", "")),
        str(policy.get("policy_schema_path", "")),
        str(policy.get("report_schema_path", "")),
        str(policy.get("receipt_schema_path", "")),
        str(policy.get("rejection_report_schema_path", "")),
        str(policy.get("default_policy_path", "")),
        str(policy.get("checker", "")),
        str(policy.get("standalone_checker", "")),
        str(policy.get("standalone_schema_checker", "")),
        str(policy.get("fingerprint_refresh_command", "")),
    ]
    pinned_keys = policy.get("pinned_requirement_keys", [])
    if isinstance(pinned_keys, list):
        required_tokens.extend(str(key) for key in pinned_keys if key)
    validation_commands = policy.get("validation_commands", [])
    if isinstance(validation_commands, list):
        required_tokens.extend(str(command) for command in validation_commands if command)

    missing_tokens = [
        token
        for token in required_tokens
        if token and token not in combined
    ]
    if missing_tokens:
        failures.append(
            "acceptance-policy docs omit generated tokens "
            f"{sorted(set(missing_tokens))}"
        )
    return failures


def validate_guided_suite_docs(
    doc_paths: Iterable[Path] = DEFAULT_GUIDED_SUITE_DOCS,
) -> list[str]:
    failures: list[str] = []
    for path in doc_paths:
        if not path.exists():
            failures.append(f"missing guided-suite docs file: {_repo_path(path)}")
            continue
        text = path.read_text(encoding="utf-8")
        stale_phrases = [
            phrase
            for phrase in FORBIDDEN_STALE_GUIDED_SUITE_PHRASES
            if phrase in text
        ]
        if stale_phrases:
            failures.append(
                f"{_repo_path(path)} uses stale guided-suite label(s): "
                f"{sorted(stale_phrases)}"
            )
    return failures


def validate_strict_flagship_receipt_docs(
    doc_paths: Iterable[Path] = DEFAULT_STRICT_RECEIPT_DOCS,
) -> list[str]:
    failures: list[str] = []
    for path in doc_paths:
        if not path.exists():
            failures.append(f"missing strict-receipt docs file: {_repo_path(path)}")
            continue
        failures.extend(
            _strict_receipt_command_failures(
                _documented_shell_commands(path),
                surface=_repo_path(path),
            )
        )
    return failures


def validate_strict_sparse_receipt_docs(
    doc_paths: Iterable[Path] = DEFAULT_STRICT_RECEIPT_DOCS,
) -> list[str]:
    return validate_strict_flagship_receipt_docs(doc_paths)


def validate_strict_flagship_receipt_pack(pack: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    contracts = pack.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        return ["pack.contracts must be a non-empty list"]

    by_kind = {
        contract.get("kind"): contract
        for contract in contracts
        if isinstance(contract, dict)
    }
    for kind in STRICT_RECEIPT_TOKENS_BY_KIND:
        contract = by_kind.get(kind)
        if not isinstance(contract, dict):
            failures.append(f"pack is missing flagship contract {kind}")
            continue
        raw_commands = contract.get("validation_commands")
        if not isinstance(raw_commands, list) or not raw_commands:
            failures.append(
                f"{kind}: validation_commands must be a non-empty list"
            )
            continue
        commands = [
            command
            for command in raw_commands
            if isinstance(command, str) and command
        ]
        if len(commands) != len(raw_commands):
            failures.append(
                f"{kind}: validation_commands must contain only non-empty strings"
            )
            continue
        receipt_commands = [
            command
            for command in commands
            if "--receipt" in command and f"--kind {kind}" in command
        ]
        if not receipt_commands:
            failures.append(
                f"{kind}: validation_commands must include a strict receipt command"
            )
            continue
        failures.extend(
            _strict_receipt_command_failures(
                receipt_commands,
                surface=f"{kind}.validation_commands",
            )
        )
    return failures


def validate_contract_source_trails(pack: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    contracts = pack.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        return ["pack.contracts must be a non-empty list"]

    for contract in contracts:
        if not isinstance(contract, dict):
            failures.append("pack.contracts entries must be objects")
            continue
        kind = contract.get("kind")
        if not isinstance(kind, str) or not kind:
            kind = str(contract.get("id", "<unknown contract>"))

        source_paper = contract.get("source_paper")
        if not isinstance(source_paper, str) or not source_paper:
            failures.append(f"{kind}: source_paper must be a non-empty string")
        elif not _repo_reference_exists(source_paper):
            failures.append(f"{kind}: source_paper path does not exist: {source_paper}")

        for key in ("quickstart_docs", "living_book_pages"):
            references, list_failures = _required_string_list(
                contract,
                key,
                kind=kind,
            )
            failures.extend(list_failures)
            for reference in references:
                if not _repo_reference_exists(reference):
                    failures.append(
                        f"{kind}: {key} path does not exist: {reference}"
                    )

        for key in ("entrypoints", "validation_commands"):
            commands, list_failures = _required_string_list(
                contract,
                key,
                kind=kind,
            )
            failures.extend(list_failures)
            for command in commands:
                try:
                    references = _local_command_references(command)
                except ValueError as exc:
                    failures.append(f"{kind}: {key} command is not parseable: {exc}")
                    continue
                for reference in references:
                    if not _repo_reference_exists(reference):
                        failures.append(
                            f"{kind}: {key} command references missing path "
                            f"{reference!r}: {command}"
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
        *validate_acceptance_policy_docs(pack),
        *validate_guided_suite_docs(),
        *validate_strict_flagship_receipt_pack(pack),
        *validate_strict_flagship_receipt_docs(),
        *validate_contract_source_trails(pack),
    ]
    if failures:
        for failure in failures:
            print(f"circle AI contract docs error: {failure}", file=sys.stderr)
        return 1
    print("circle AI contract docs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
