"""Generic public Circle AI contract pack.

The pack in this module is the public, standalone view of the Circle AI
contracts. Downstream projects, including Theseus-Hive, can consume it as
configuration, but the schema is not Theseus-specific.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import yaml

from .circle_ai import (
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_live_window,
    certify_kv_cache_sink_window,
    certify_stride_family_coverage,
)
from .rope_certifier import (
    ROPE_CERTIFIER_PRESETS,
    certify_rope_positions,
    certify_standard_channel0_d19_bank_request,
    certify_standard_channel0_d19_range_request_margin_bracket,
)
from .theseus_hive_contracts import build_contract_pack as build_theseus_compat_pack
from .theseus_hive_contracts import fanout_contract as build_theseus_fanout_contract
from .theseus_hive_contracts import memory_contract as build_theseus_memory_contract
from .theseus_hive_contracts import mixer_contract as build_theseus_mixer_contract
from .theseus_hive_contracts import phase_feature_contract as build_theseus_phase_feature_contract
from .theseus_hive_contracts import recurrence_contract as build_theseus_recurrence_contract
from .theseus_hive_contracts import seed_rule_contract as build_theseus_seed_rule_contract

SCHEMA_ID = "circle_calculus.ai_contract_pack.v0"
ROOT = Path(__file__).resolve().parents[2]
PROVED_STATUSES = ("lean_proved", "proved")
FINGERPRINT_ALGORITHM = "sha256-json-v1"
FINGERPRINT_KEYS = {
    "content_fingerprint",
    "pack_content_fingerprint",
    "contract_fingerprint_index",
}
ACCEPTANCE_POLICY_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_policy.v0"
ACCEPTANCE_POLICY_REPORT_SCHEMA_ID = (
    "circle_calculus.ai_contract_acceptance_policy_report.v0"
)
ACCEPTANCE_RECEIPT_SCHEMA_ID = "circle_calculus.ai_contract_acceptance_receipt.v0"
DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID = (
    "circle_calculus.downstream_ci_rejection_report.v0"
)
ACCEPTANCE_POLICY_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_acceptance_policy.schema.json"
)
ACCEPTANCE_POLICY_REPORT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_acceptance_policy_report.schema.json"
)
ACCEPTANCE_RECEIPT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_acceptance_receipt.schema.json"
)
DOWNSTREAM_REJECTION_REPORT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_downstream_rejection_report.schema.json"
)

CLAIM_BOUNDARY = (
    "These contracts expose finite cyclic structure for external AI/math tools. "
    "They do not prove model quality, reasoning ability, context length, speed, "
    "memory scaling, deployment safety, transfer, or ASI."
)

ROPE_EXACT_RATIONAL_THRESHOLD_THEOREMS = (
    "AIRA-T0214",
    "AIRA-T0215",
    "AIRA-T0222",
    "AIRA-T0223",
    "AIRA-T0224",
    "AIRA-T0225",
    "AIRA-T0226",
    "AIRA-T0227",
    "AIRA-T0228",
    "AIRA-T0229",
    "AIRA-T0230",
    "AIRA-T0231",
)

GENERIC_IDS = {
    "rope_position_distinguishability": "CC-AI-CONTRACT-ROPE-001",
    "kv_cache_ring_buffer": "CC-AI-CONTRACT-KV-001",
    "sparse_attention_coverage": "CC-AI-CONTRACT-SPARSE-001",
    "recurrence_schedule": "CC-AI-CONTRACT-RECURRENCE-001",
    "strided_candidate_fanout": "CC-AI-CONTRACT-FANOUT-001",
    "cyclic_memory_residue_winding": "CC-AI-CONTRACT-MEMORY-001",
    "multicoil_phase_feature": "CC-AI-CONTRACT-PHASE-FEATURE-001",
    "circulant_block_cyclic_mixer": "CC-AI-CONTRACT-MIXER-001",
    "seed_rule_exact_regeneration": "CC-AI-CONTRACT-SEED-RULE-001",
}

GENERIC_USES = {
    "rope_position_distinguishability": (
        "RoPE position-contract auditing: exact integer-period phase-bank "
        "distinguishability, collision counts, and real-phase diagnostic margins."
    ),
    "kv_cache_ring_buffer": (
        "KV-cache request auditing: retained-window freshness, stale-request "
        "rejection, generated live-window coverage, and sink-window policy checks."
    ),
    "sparse_attention_coverage": (
        "Sparse-attention layout auditing: covered lags, explicit gap witnesses, "
        "candidate-budget shortfalls, duplicate-candidate loss fields, and "
        "collision-pair boundary fields."
    ),
    "recurrence_schedule": (
        "Looped or recursive schedule auditing: phase cycles, active-token "
        "budgets, exit steps, and overthinking-boundary diagnostics."
    ),
    "strided_candidate_fanout": (
        "Sparse candidate fanout auditing: finite reachability, coverage, "
        "duplicate-collapse, and gap diagnostics."
    ),
    "cyclic_memory_residue_winding": (
        "Cyclic memory auditing: slot aliases, winding/provenance separation, "
        "and residue-class load diagnostics."
    ),
    "multicoil_phase_feature": (
        "Phase-feature auditing: multi-period position tags and relative-phase "
        "features with explicit repeat horizons."
    ),
    "circulant_block_cyclic_mixer": (
        "Structured mixer/accounting checks: circulant equality fixtures, "
        "block-cyclic parameter counts, and dense-baseline comparison fields."
    ),
    "seed_rule_exact_regeneration": (
        "Generative provenance checks: seed/rule/object triples that can be "
        "regenerated exactly and compared against object-only storage."
    ),
}

CONTRACT_ARTIFACTS = {
    "rope_position_distinguishability": {
        "source_paper": "papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md",
        "quickstart_docs": ["docs/ROPE_CERTIFIER_QUICKSTART.md"],
        "living_book_pages": [
            "site/chapters/applications/rope_certifier.qmd",
            "site/chapters/applications/rope_certifier_audit.qmd",
        ],
        "entrypoints": [
            "python scripts/rope_certify.py --preset llama_style_10000_4k",
            "python scripts/rope_certify.py --preset llama_style_10000_4k --format json",
        ],
        "validation_commands": [
            "python scripts/rope_certify.py --preset llama_style_10000_4k --format json",
            "python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability",
            (
                "python scripts/circle_ai_contract_ready.py --kind "
                "rope_position_distinguishability --receipt --format json "
                "--field d19_proved_request_status "
                "--field d19_impossible_request_status "
                "--field d19_undecided_request_status "
                "--field d19_proved_first_channel_bank_transfer "
                "--field d19_proved_first_channel_bank_shape "
                "--field d19_proved_first_channel_pair_scope "
                "--field d19_proved_first_channel_context_wide_contract "
                "--field d19_proved_first_channel_radian_bank_form "
                "--field d19_proved_first_channel_bank_tolerance_rule "
                "--field d19_undecided_probe_margin_in_open_gap "
                "--require-theorem AIRA-T0171 --require-theorem AIRA-T0172 "
                "--require-theorem AIRA-T0234 --require-theorem AIRA-T0235 "
                "--require-theorem AIRA-T0236 --require-theorem AIRA-T0237 "
                "--require-theorem AIRA-T0238 "
                "--require-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
                "--require-recommendation-evidence-field "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_bank_transfer "
                "--require-recommendation-evidence-field "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_context_wide_contract "
                "--require-recommendation-evidence-field "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_proved_first_channel_radian_bank_form "
                "--require-recommendation-evidence-field "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "d19_undecided_probe_margin_in_open_gap "
                "--require-recommendation-theorem "
                "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 "
                "--require-recommendation-theorem "
                "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 "
                "--require-recommendation-theorem "
                "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236 "
                "--require-recommendation-theorem "
                "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237 "
                "--require-recommendation-theorem "
                "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0238 "
                "--require-recommendation-action-parameter "
                "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer "
                "--require-recommendation-action-parameter-path "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.applies "
                "--require-recommendation-action-parameter-path "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.context_wide_contract "
                "--require-recommendation-action-parameter-path "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.radian_bank_form "
                "--require-recommendation-action-parameter-path "
                "ROPE-USE-D19-MARGIN-FRONTIER="
                "proved_branch_bank_transfer.theorem_ids"
            ),
            "python -m pytest tests/test_rope_certifier.py -q",
        ],
    },
    "kv_cache_ring_buffer": {
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "quickstart_docs": ["docs/KV_CACHE_CERTIFIER_QUICKSTART.md"],
        "living_book_pages": [
            "site/chapters/applications/kv_cache_ring_buffer.qmd",
            "site/chapters/applications/kv_cache_ring_buffer_audit.qmd",
        ],
        "entrypoints": [
            "python scripts/kv_cache_certify.py --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4",
            "python scripts/kv_cache_certify.py --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --format json",
        ],
        "validation_commands": [
            "python scripts/kv_cache_certify.py --cache-size 16 --current 31 --token 20 --batch-tokens 20,24,29,31 --sink-size 4 --format json",
            "python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer",
            (
                "python scripts/circle_ai_contract_ready.py --kind "
                "kv_cache_ring_buffer --receipt --format json "
                "--field stale_probe_first_stale_token "
                "--field sink_tokens_retained_by_policy "
                "--field sink_window_exact_policy "
                "--field sink_window_tokens_distinct "
                "--field sink_prefix_disjoint_from_live_window "
                "--field sink_tokens_outside_ordinary_rolling_window "
                "--require-theorem AIM-T0103 --require-theorem AIM-T0104 "
                "--require-theorem AIM-T0149 "
                "--require-recommendation KV-DROP-STALE-REQUEST-TOKEN "
                "--require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST "
                "--require-recommendation-evidence-field "
                "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token "
                "--require-recommendation-evidence-field "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
                "sink_tokens_retained_by_policy "
                "--require-recommendation-evidence-field "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
                "sink_tokens_outside_ordinary_rolling_window "
                "--require-recommendation-theorem "
                "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103 "
                "--require-recommendation-theorem "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149 "
                "--require-recommendation-action-parameter "
                "KV-DROP-STALE-REQUEST-TOKEN=target_token "
                "--require-recommendation-action-parameter "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
                "--require-recommendation-action-parameter-path "
                "KV-DROP-STALE-REQUEST-TOKEN=target_token "
                "--require-recommendation-action-parameter-path "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
                "--require-recommendation-action-parameter-path "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count "
                "--require-recommendation-action-parameter-path "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound "
                "--require-recommendation-action-parameter-path "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size "
                "--require-recommendation-action-parameter-path "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current"
            ),
            "python -m pytest tests/test_kv_cache_certifier_cli.py -q",
        ],
    },
    "sparse_attention_coverage": {
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "quickstart_docs": ["docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md"],
        "living_book_pages": [
            "site/chapters/applications/sparse_attention_contract.qmd",
            "site/chapters/applications/sparse_attention_audit.qmd",
        ],
        "entrypoints": [
            "python scripts/stride_family_certify.py --context 120 --strides 7,13 --path-length 3 --local-window 4",
            "python scripts/stride_family_certify.py --context 120 --strides 7,13 --path-length 3 --local-window 4 --format json",
        ],
        "validation_commands": [
            "python scripts/stride_family_certify.py --context 120 --strides 7,13 --path-length 3 --local-window 4 --format json",
            "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage",
            (
                "python scripts/circle_ai_contract_ready.py --kind "
                "sparse_attention_coverage --receipt --format json "
                "--field first_uncovered_lag "
                "--field first_uncovered_interval_start "
                "--field complete_repair_window "
                "--field complete_repair_window_covers_context "
                "--field complete_repair_window_minimal_for_declared_stride_family "
                "--field complete_repair_window_minimal_witness_lag "
                "--require-theorem AIT-T0104 --require-theorem AIT-T0172 "
                "--require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
                "--require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK "
                "--require-recommendation-evidence-field "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start "
                "--require-recommendation-evidence-field "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
                "complete_repair_window_covers_context "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
                "complete_repair_window_uses_dense_threshold "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
                "local_window_complete_threshold_is_exact_local_minimum "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
                "complete_repair_window_minimal_for_declared_stride_family "
                "--require-recommendation-evidence-field "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
                "complete_repair_window_minimal_witness_lag "
                "--require-recommendation-theorem "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169 "
                "--require-recommendation-theorem "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170 "
                "--require-recommendation-action-parameter "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
                "--require-recommendation-action-parameter "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
                "--require-recommendation-action-parameter "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots "
                "--require-recommendation-action-parameter-path "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
                "--require-recommendation-action-parameter-path "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
                "--require-recommendation-action-parameter-path "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots"
            ),
            "python -m pytest tests/test_stride_family_certifier_cli.py tests/test_circle_transformer.py -q",
        ],
    },
    "recurrence_schedule": {
        "quickstart_docs": [
            "docs/RECURRENCE_SCHEDULE_CERTIFIER_QUICKSTART.md",
            "docs/AI_CONTRACT_SUITE.md",
        ],
        "living_book_pages": ["site/chapters/applications/looped_recurrence_contracts.qmd"],
        "entrypoints": [
            "python scripts/recurrence_schedule_certify.py",
            "python scripts/recurrence_schedule_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/recurrence_schedule_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind recurrence_schedule",
            (
                "python scripts/circle_ai_contract_ready.py --kind "
                "recurrence_schedule --receipt --format json "
                "--field periodic_shift_required_steps_invariant "
                "--field periodic_shift_active_at_step_invariant "
                "--field total_active_token_work "
                "--field scheduled_work_saving "
                "--field scheduled_work_saving_accounting "
                "--field active_inactive_work_accounting "
                "--field scheduled_work_saving_positive "
                "--field post_period_multi_extension_scheduled_work_saving "
                "--require-theorem AIM-T0026 --require-theorem AIM-T0130 "
                "--require-theorem AIM-T0159 "
                "--require-recommendation "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE "
                "--require-recommendation "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT "
                "--require-recommendation-evidence-field "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "total_active_token_work "
                "--require-recommendation-evidence-field "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "scheduled_work_saving "
                "--require-recommendation-evidence-field "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "post_period_multi_extension_scheduled_work_saving "
                "--require-recommendation-evidence-field "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
                "periodic_shift_required_steps_invariant "
                "--require-recommendation-evidence-field "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
                "periodic_shift_active_at_step_invariant "
                "--require-recommendation-theorem "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 "
                "--require-recommendation-theorem "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 "
                "--require-recommendation-theorem "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 "
                "--require-recommendation-action-parameter "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
                "--require-recommendation-action-parameter "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "scheduled_work_saving "
                "--require-recommendation-action-parameter "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "scheduled_work_saving "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
                "post_period_multi_extension_scheduled_work_saving "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token "
                "--require-recommendation-action-parameter-path "
                "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount"
            ),
            "python -m pytest tests/test_recurrence_schedule_certifier_cli.py -q",
        ],
    },
    "strided_candidate_fanout": {
        "quickstart_docs": [
            "docs/STRIDED_CANDIDATE_FANOUT_CERTIFIER_QUICKSTART.md",
            "docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md",
            "docs/AI_CONTRACT_SUITE.md",
        ],
        "living_book_pages": [
            "site/chapters/applications/strided_candidate_fanout.qmd"
        ],
        "entrypoints": [
            "python scripts/strided_candidate_fanout_certify.py",
            "python scripts/strided_candidate_fanout_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/strided_candidate_fanout_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout",
            "python -m pytest tests/test_strided_candidate_fanout_certifier_cli.py -q",
        ],
    },
    "cyclic_memory_residue_winding": {
        "quickstart_docs": [
            "docs/CYCLIC_MEMORY_CERTIFIER_QUICKSTART.md",
            "docs/AI_CONTRACT_SUITE.md",
        ],
        "living_book_pages": [
            "site/chapters/applications/cyclic_memory_residue_winding.qmd"
        ],
        "entrypoints": [
            "python scripts/cyclic_memory_certify.py",
            "python scripts/cyclic_memory_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/cyclic_memory_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding",
            "python -m pytest tests/test_cyclic_memory_certifier_cli.py -q",
        ],
    },
    "multicoil_phase_feature": {
        "quickstart_docs": [
            "docs/MULTICOIL_PHASE_FEATURE_CERTIFIER_QUICKSTART.md",
            "docs/AI_CONTRACT_SUITE.md",
        ],
        "living_book_pages": [
            "site/chapters/applications/multicoil_phase_feature.qmd"
        ],
        "entrypoints": [
            "python scripts/multicoil_phase_feature_certify.py",
            "python scripts/multicoil_phase_feature_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/multicoil_phase_feature_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature",
            "python -m pytest tests/test_multicoil_phase_feature_certifier_cli.py -q",
        ],
    },
    "circulant_block_cyclic_mixer": {
        "quickstart_docs": [
            "docs/CIRCULANT_BLOCK_CYCLIC_MIXER_CERTIFIER_QUICKSTART.md",
            "docs/AI_CONTRACT_SUITE.md",
        ],
        "living_book_pages": [
            "site/chapters/applications/circulant_block_cyclic_mixer.qmd"
        ],
        "entrypoints": [
            "python scripts/circulant_block_cyclic_mixer_certify.py",
            "python scripts/circulant_block_cyclic_mixer_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/circulant_block_cyclic_mixer_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer",
            "python -m pytest tests/test_circulant_block_cyclic_mixer_certifier_cli.py -q",
        ],
    },
    "seed_rule_exact_regeneration": {
        "quickstart_docs": [
            "docs/SEED_RULE_CERTIFIER_QUICKSTART.md",
            "docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md",
        ],
        "living_book_pages": ["site/chapters/applications/generative.qmd"],
        "entrypoints": [
            "python scripts/seed_rule_certify.py",
            "python scripts/seed_rule_certify.py --format json",
            "python scripts/export_circle_ai_contracts.py",
        ],
        "validation_commands": [
            "python scripts/seed_rule_certify.py --format json",
            "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration",
            "python -m pytest tests/test_seed_rule_certifier_cli.py -q",
        ],
    },
}

CONTRACT_REQUIRED_KEYS = (
    "id",
    "kind",
    "status",
    "content_fingerprint_algorithm",
    "content_fingerprint",
    "theorem_ids",
    "dictionary_ids",
    "fields",
    "proof_status",
    "contract_passed",
    "integration_use",
    "ordinary_baselines",
    "not_claimed",
    "source_paper",
    "quickstart_docs",
    "living_book_pages",
    "entrypoints",
    "validation_commands",
)

PLANNER_RECOMMENDATION_KEYS = (
    "id",
    "action_kind",
    "status",
    "coverage_scope",
    "evidence_fields",
    "theorem_ids",
    "not_claimed",
)

MINIMUM_FIELDS_BY_KIND = {
    "rope_position_distinguishability": (
        "certificate_schema_id",
        "exact_discrete_pass",
        "common_collision_gap",
        "total_bank_collision_pair_count",
        "real_phase_margin_pass",
        "worst_margin_radians",
        "d19_context_range_min_exclusive",
        "d19_context_range_max_inclusive",
        "d19_proved_request_status",
        "d19_proved_request_theorem_backed_classification",
        "d19_impossible_request_status",
        "d19_impossible_request_theorem_backed_classification",
        "d19_undecided_request_status",
        "d19_undecided_margin_open_gap",
        "d19_undecided_margin_interval_width",
        "d19_undecided_request_relation",
        "d19_margin_thresholds_ordered",
        "d19_proved_impossible_branches_disjoint",
        "d19_margin_status_exhaustive",
        "d19_in_range_semantic_trichotomy",
        "d19_proved_first_channel_bank_transfer",
        "d19_proved_first_channel_bank_shape",
        "d19_proved_first_channel_pair_scope",
        "d19_proved_first_channel_context_wide_contract",
        "d19_proved_first_channel_radian_bank_form",
        "d19_proved_first_channel_bank_tolerance_rule",
        "proof_layers",
    ),
    "kv_cache_ring_buffer": (
        "certificate_schema_id",
        "adapter_request_pass",
        "stale_requested_count",
        "pass_iff_stale_count_zero_under_nonfuture_nodup",
        "stale_probe_requested_tokens",
        "stale_probe_requested_slots",
        "stale_probe_pass",
        "stale_probe_first_stale_token",
        "stale_probe_first_stale_next_overwrite_token",
        "stale_probe_stale_requested_count",
        "stale_probe_stale_member_blocks_pass",
        "stale_probe_pass_iff_stale_count_zero_under_nonfuture_nodup",
        "stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup",
        "sink_window_exact_policy",
        "sink_window_tokens_distinct",
        "sink_window_token_count",
        "sink_window_token_count_bound",
        "sink_window_token_count_le_sink_plus_cache",
        "sink_window_disjoint_exact_token_count",
        "sink_window_token_count_eq_sink_plus_live_window_when_disjoint",
        "sink_prefix_disjoint_from_live_window",
        "sink_rolling_tokens_retained",
        "sink_tokens_are_seen_prefix",
        "sink_tokens_non_future",
        "sink_tokens_retained_by_policy",
        "sink_tokens_outside_ordinary_rolling_window",
    ),
    "sparse_attention_coverage": (
        "certificate_schema_id",
        "coverage_complete",
        "covered_lag_count",
        "uncovered_lag_count",
        "uncovered_lag_intervals",
        "first_uncovered_lag",
        "first_uncovered_interval_start",
        "first_uncovered_interval_stop",
        "first_uncovered_interval_length",
        "local_window_needed_to_cover_first_uncovered_interval",
        "first_uncovered_interval_additional_local_slots",
        "first_uncovered_interval_repair_reaches_interval",
        "first_interval_repair_next_uncovered_lag",
        "first_interval_repair_still_has_gap",
        "first_interval_repair_covers_context",
        "largest_uncovered_interval_start",
        "largest_uncovered_interval_stop",
        "largest_uncovered_interval_length",
        "local_window_needed_to_cover_largest_uncovered_interval",
        "largest_uncovered_interval_additional_local_slots",
        "largest_uncovered_interval_repair_reaches_interval",
        "largest_interval_repair_next_uncovered_lag",
        "largest_interval_repair_still_has_gap",
        "largest_interval_repair_covers_context",
        "largest_uncovered_interval_is_tail",
        "first_gap_local_window_shortfall",
        "local_window_needed_to_cover_first_gap",
        "current_window_below_first_gap",
        "first_gap_repair_window_reaches",
        "first_gap_repair_window_covers_context",
        "first_gap_repair_window_is_final_positive_lag",
        "first_gap_repair_threshold_matches_final_lag",
        "local_window_complete_coverage_threshold",
        "local_window_complete_coverage_shortfall",
        "local_window_reaches_complete_coverage_threshold",
        "local_window_threshold_certifies_complete",
        "local_window_complete_threshold_is_exact_local_minimum",
        "complete_repair_window",
        "complete_repair_window_additional_local_slots",
        "complete_repair_window_covers_context",
        "complete_repair_window_uses_dense_threshold",
        "complete_repair_window_minimal_for_declared_stride_family",
        "complete_repair_window_minimal_witness_lag",
        "interval_repair_plan",
        "interval_repair_plan_step_count",
        "interval_repair_plan_final_window",
        "interval_repair_plan_covers_context",
        "interval_repair_plan_strictly_progresses",
        "first_gap_repair_window_reaches_complete_threshold",
        "raw_budget_shortfall_certifies_incomplete",
        "lag_unique_plus_loss_eq_raw",
        "query_unique_plus_loss_eq_raw",
        "lag_collision_pair_count",
        "query_collision_pair_count",
        "lag_collision_pair_count_zero_iff_no_collision",
        "lag_collision_pair_count_positive_iff_collision",
        "lag_collision_pair_count_bounds_dedup_loss",
        "lag_collision_pair_count_excess_over_dedup_loss",
        "query_collision_pair_count_zero_iff_no_collision",
        "query_collision_pair_count_positive_iff_collision",
        "query_collision_pair_count_bounds_dedup_loss",
        "query_collision_pair_count_excess_over_dedup_loss",
    ),
    "recurrence_schedule": (
        "required_steps",
        "exit_step",
        "loop_period",
        "overthinking_boundary",
        "active_step_one_is_full_range",
        "first_step_active_token_count",
        "first_step_inactive_token_count",
        "first_step_inactive_count_zero",
        "work_count_step",
        "work_step_active_token_count",
        "work_step_inactive_token_count",
        "work_step_active_inactive_count_eq_token_count",
        "post_period_active_empty",
        "post_period_active_token_count",
        "post_period_inactive_token_count",
        "post_period_inactive_count_eq_token_count",
        "active_token_sets_descend",
        "active_token_lists_nodup",
        "active_token_counts_bounded",
        "active_token_counts_descend",
        "inactive_token_counts_ascend",
        "total_work_horizon_steps",
        "active_token_count_trace",
        "inactive_token_count_trace",
        "active_token_count_trace_sum",
        "inactive_token_count_trace_sum",
        "active_token_count_trace_sum_matches_total",
        "inactive_token_count_trace_sum_matches_total",
        "first_inactive_steps",
        "first_inactive_steps_match_budget_successor",
        "total_active_token_work",
        "total_inactive_token_work",
        "full_loop_token_work",
        "scheduled_work_saving",
        "scheduled_work_saving_accounting",
        "active_inactive_work_accounting",
        "scheduled_work_saving_matches_inactive_work",
        "scheduled_work_saving_positive",
        "active_work_below_full_loop_work",
        "scheduled_work_saving_positive_iff_active_work_shortfall",
        "scheduled_work_saving_zero",
        "active_work_equals_full_loop_work",
        "scheduled_work_saving_zero_iff_no_active_work_shortfall",
        "public_fixture_4_8_2_active_token_count",
        "public_fixture_4_8_2_inactive_token_count",
        "public_fixture_4_8_2_accounting_eq_token_count",
        "public_fixture_4_8_4_total_active_token_work",
        "public_fixture_4_8_4_total_inactive_token_work",
        "public_fixture_8_4_full_loop_token_work",
        "public_fixture_4_8_4_scheduled_work_saving",
        "public_fixture_4_8_4_work_saving_accounting",
        "public_fixture_4_8_4_active_inactive_work_accounting",
        "public_fixture_4_8_4_work_saving_matches_inactive_work",
        "public_fixture_4_8_4_scheduled_work_saving_positive",
        "public_fixture_4_8_4_active_work_below_full_loop_work",
        "public_fixture_4_8_4_positive_saving_iff_active_work_shortfall",
        "public_fixture_4_8_4_scheduled_work_saving_zero",
        "public_fixture_4_8_4_active_work_equals_full_loop_work",
        "public_fixture_4_8_4_zero_saving_iff_no_active_work_shortfall",
        "default_fixture_5_8_5_total_active_token_work",
        "default_fixture_5_8_5_total_inactive_token_work",
        "default_fixture_8_5_full_loop_token_work",
        "default_fixture_5_8_5_scheduled_work_saving",
        "default_fixture_5_8_5_work_saving_accounting",
        "default_fixture_5_8_5_active_inactive_work_accounting",
        "default_fixture_5_8_5_work_saving_matches_inactive_work",
        "post_period_extension_horizon_steps",
        "post_period_extension_total_active_token_work",
        "post_period_extension_total_inactive_token_work",
        "post_period_extension_full_loop_token_work",
        "post_period_extension_scheduled_work_saving",
        "post_period_extension_active_work_unchanged",
        "post_period_extension_inactive_work_added_token_count",
        "post_period_extension_saving_added_token_count",
        "default_fixture_5_8_6_total_active_token_work",
        "default_fixture_5_8_6_scheduled_work_saving",
        "default_fixture_5_8_6_active_work_unchanged",
        "default_fixture_5_8_6_saving_added_token_count",
        "post_period_extra_steps",
        "post_period_multi_extension_horizon_steps",
        "post_period_multi_extension_total_active_token_work",
        "post_period_multi_extension_total_inactive_token_work",
        "post_period_multi_extension_full_loop_token_work",
        "post_period_multi_extension_scheduled_work_saving",
        "post_period_multi_extension_active_work_unchanged",
        "post_period_multi_extension_inactive_work_added_extra_token_count",
        "post_period_multi_extension_saving_added_extra_token_count",
        "default_fixture_5_8_8_total_active_token_work",
        "default_fixture_5_8_8_scheduled_work_saving",
        "default_fixture_5_8_8_active_work_unchanged",
        "default_fixture_5_8_8_saving_added_extra_token_count",
        "periodic_shift_base_token",
        "periodic_shift_passes",
        "periodic_shift_amount",
        "periodic_shifted_token",
        "periodic_shift_required_steps_invariant",
        "periodic_shift_recurrence_budget_invariant",
        "periodic_shift_training_free_budget_invariant",
        "periodic_shift_exit_step_invariant",
        "periodic_shift_overthinking_boundary_invariant",
        "periodic_shift_active_step",
        "periodic_shift_active_at_step_invariant",
    ),
    "strided_candidate_fanout": (
        "context_length",
        "stride",
        "candidate_budget",
        "unique_candidate_count",
        "effective_candidate_budget",
        "duplicate_count",
        "candidate_budget_accounting",
        "effective_budget_matches_unique_candidates",
        "candidate_budget_shortfall",
        "effective_budget_reaches_predicted_reach",
        "full_coverage",
        "predicted_reach",
    ),
    "cyclic_memory_residue_winding": (
        "bank_size",
        "event_count",
        "residue_slot",
        "winding",
        "same_residue_events",
        "same_residue_windings",
        "max_alias_load",
    ),
    "multicoil_phase_feature": (
        "periods",
        "position",
        "phase_tuple",
        "shifted_position",
        "shifted_phase_tuple",
        "joint_repeat_horizon",
        "relative_period",
    ),
    "circulant_block_cyclic_mixer": (
        "period",
        "input_values",
        "kernel_values",
        "circulant_output",
        "dense_output",
        "max_abs_dense_delta",
        "dense_parameters",
        "circulant_parameters",
        "circulant_parameter_ratio",
    ),
    "seed_rule_exact_regeneration": (
        "artifact_id",
        "fixture_n",
        "seed",
        "rules",
        "generated_object",
        "regenerated_object",
        "exact_regeneration",
        "explicit_length",
        "generator_length",
        "storage_saving",
        "storage_saving_positive",
        "generator_shorter",
        "generator_shorter_iff_positive_saving",
        "storage_saving_add_generator_length_eq_explicit_length",
        "bounded_search_id",
        "bounded_search_finite_search_space",
        "bounded_search_candidate_count",
        "bounded_search_exact_candidate_count",
        "bounded_search_exact_candidate_count_le_candidate_count",
        "bounded_search_has_best_exact",
        "bounded_search_best_exact_exists_iff_exact_count_positive",
        "bounded_search_best_exact_implies_candidate_count_positive",
        "bounded_search_best_exact_artifact_id",
        "bounded_search_best_exact_candidate_id",
        "bounded_search_best_exact_regenerates",
        "bounded_search_has_best_shorter",
        "bounded_search_best_shorter_artifact_id",
        "bounded_search_best_shorter_candidate_id",
        "bounded_search_best_shorter_generator_shorter",
        "bounded_search_candidates",
        "bounded_search_candidate_ids_by_generator_length",
        "bounded_search_exact_candidate_ids_by_generator_length",
        "bounded_search_shorter_candidate_ids_by_generator_length",
        "closure_condition",
    ),
}

PACK_VALIDATION_COMMANDS = [
    "python scripts/export_circle_ai_contracts.py",
    "python scripts/check_circle_ai_contract_pack.py",
    "python scripts/example_validate_circle_ai_contract_pack_schema.py --summary",
    "make circle-ai-contracts-ready",
    "python scripts/check_circle_ai_contract_acceptance_policy.py",
    "python scripts/check_circle_ai_contract_acceptance_policy.py --format json",
    "python scripts/circle_ai_contract_ready.py --print-refreshed-policy",
    "python scripts/circle_ai_contract_ready.py --acceptance-policy-report",
    (
        "python scripts/circle_ai_contract_ready.py "
        "--acceptance-policy-report --format json"
    ),
    "python scripts/check_downstream_ci_acceptance_example.py --summary",
    "python examples/downstream_ci_accept_circle_ai_contracts.py --format json",
    "python examples/downstream_ci_accept_circle_ai_contracts.py --format text",
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK --include-values"
    ),
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values"
    ),
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --include-values"
    ),
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST --include-values"
    ),
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE --include-values"
    ),
    (
        "python examples/downstream_ci_accept_circle_ai_contracts.py "
        "--format json --planner-recommendation "
        "ROPE-USE-D19-MARGIN-FRONTIER --include-values"
    ),
    "python scripts/circle_ai_contract_ready.py --acceptance-policy",
    "python scripts/circle_ai_contract_ready.py --acceptance-policy --format json",
    "python scripts/circle_ai_contract_ready.py --list-recommendations",
    "python scripts/circle_ai_contract_ready.py --fingerprints",
    "python scripts/circle_ai_contract_ready.py --action-plan",
    (
        "python scripts/circle_ai_contract_ready.py --action-plan "
        "--recommendation ROPE-USE-D19-MARGIN-FRONTIER --include-values --format json"
    ),
    (
        "python scripts/example_consume_circle_ai_contract_pack.py "
        "--planner --planner-kind rope_position_distinguishability "
        "--planner-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
        "--planner-include-values"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration "
        "--action-plan --include-values --format json"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability "
        "--digest --format json --field d19_proved_request_status "
        "--field d19_impossible_request_status "
        "--field d19_undecided_request_status "
        "--field d19_proved_first_channel_bank_transfer "
        "--field d19_proved_first_channel_bank_shape "
        "--field d19_proved_first_channel_pair_scope "
        "--field d19_proved_first_channel_context_wide_contract "
        "--field d19_proved_first_channel_radian_bank_form "
        "--field d19_proved_first_channel_bank_tolerance_rule "
        "--field d19_undecided_probe_margin_in_open_gap "
        "--include-field-metadata --include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind "
        "rope_position_distinguishability --receipt --format json "
        "--field d19_proved_request_status "
        "--field d19_impossible_request_status "
        "--field d19_undecided_request_status "
        "--field d19_proved_first_channel_bank_transfer "
        "--field d19_proved_first_channel_bank_shape "
        "--field d19_proved_first_channel_pair_scope "
        "--field d19_proved_first_channel_context_wide_contract "
        "--field d19_proved_first_channel_radian_bank_form "
        "--field d19_proved_first_channel_bank_tolerance_rule "
        "--field d19_undecided_probe_margin_in_open_gap "
        "--require-theorem AIRA-T0171 --require-theorem AIRA-T0172 "
        "--require-theorem AIRA-T0234 --require-theorem AIRA-T0235 "
        "--require-theorem AIRA-T0236 --require-theorem AIRA-T0237 "
        "--require-theorem AIRA-T0238 "
        "--require-recommendation ROPE-USE-D19-MARGIN-FRONTIER "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_bank_transfer "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "d19_proved_first_channel_context_wide_contract "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_proved_first_channel_radian_bank_form "
        "--require-recommendation-evidence-field "
        "ROPE-USE-D19-MARGIN-FRONTIER=d19_undecided_probe_margin_in_open_gap "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0234 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0235 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0236 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0237 "
        "--require-recommendation-theorem "
        "ROPE-USE-D19-MARGIN-FRONTIER=AIRA-T0238 "
        "--require-recommendation-action-parameter "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.applies "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER="
        "proved_branch_bank_transfer.context_wide_contract "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.radian_bank_form "
        "--require-recommendation-action-parameter-path "
        "ROPE-USE-D19-MARGIN-FRONTIER=proved_branch_bank_transfer.theorem_ids"
    ),
    "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage",
    (
        "python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer "
        "--digest --field stale_probe_first_stale_token --include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind "
        "kv_cache_ring_buffer --receipt --format json "
        "--field stale_probe_first_stale_token "
        "--field sink_tokens_retained_by_policy "
        "--field sink_window_exact_policy "
        "--field sink_window_tokens_distinct "
        "--field sink_prefix_disjoint_from_live_window "
        "--field sink_tokens_outside_ordinary_rolling_window "
        "--require-theorem AIM-T0103 --require-theorem AIM-T0104 "
        "--require-theorem AIM-T0149 "
        "--require-recommendation KV-DROP-STALE-REQUEST-TOKEN "
        "--require-recommendation KV-USE-SINK-ROLLING-WINDOW-REQUEST "
        "--require-recommendation-evidence-field "
        "KV-DROP-STALE-REQUEST-TOKEN=stale_probe_first_stale_token "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_tokens_retained_by_policy "
        "--require-recommendation-evidence-field "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST="
        "sink_tokens_outside_ordinary_rolling_window "
        "--require-recommendation-theorem "
        "KV-DROP-STALE-REQUEST-TOKEN=AIM-T0103 "
        "--require-recommendation-theorem "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=AIM-T0149 "
        "--require-recommendation-action-parameter "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-DROP-STALE-REQUEST-TOKEN=target_token "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=sink_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=request_token_count_bound "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=cache_size "
        "--require-recommendation-action-parameter-path "
        "KV-USE-SINK-ROLLING-WINDOW-REQUEST=current"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage "
        "--digest --field first_uncovered_lag --include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind "
        "sparse_attention_coverage --receipt --format json "
        "--field first_uncovered_lag "
        "--field first_uncovered_interval_start "
        "--field complete_repair_window "
        "--field complete_repair_window_covers_context "
        "--field complete_repair_window_minimal_for_declared_stride_family "
        "--field complete_repair_window_minimal_witness_lag "
        "--require-theorem AIT-T0104 --require-theorem AIT-T0172 "
        "--require-recommendation SPARSE-LOCAL-FIRST-INTERVAL-REPAIR "
        "--require-recommendation SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK "
        "--require-recommendation-evidence-field "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_start "
        "--require-recommendation-evidence-field "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=first_uncovered_interval_stop "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_covers_context "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_uses_dense_threshold "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
        "local_window_complete_threshold_is_exact_local_minimum "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK="
        "complete_repair_window_minimal_for_declared_stride_family "
        "--require-recommendation-evidence-field "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=complete_repair_window_minimal_witness_lag "
        "--require-recommendation-theorem "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=AIT-T0104 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0023 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0034 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0172 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0168 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0169 "
        "--require-recommendation-theorem "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=AIT-T0170 "
        "--require-recommendation-action-parameter "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
        "--require-recommendation-action-parameter "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
        "--require-recommendation-action-parameter "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots "
        "--require-recommendation-action-parameter-path "
        "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR=proposed_local_window "
        "--require-recommendation-action-parameter-path "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=proposed_local_window "
        "--require-recommendation-action-parameter-path "
        "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK=additional_local_slots"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind recurrence_schedule "
        "--digest --field scheduled_work_saving "
        "--field post_period_multi_extension_scheduled_work_saving "
        "--include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind "
        "recurrence_schedule --receipt --format json "
        "--field periodic_shift_required_steps_invariant "
        "--field periodic_shift_active_at_step_invariant "
        "--field total_active_token_work "
        "--field scheduled_work_saving "
        "--field scheduled_work_saving_accounting "
        "--field active_inactive_work_accounting "
        "--field scheduled_work_saving_positive "
        "--field post_period_multi_extension_scheduled_work_saving "
        "--require-theorem AIM-T0026 --require-theorem AIM-T0130 "
        "--require-theorem AIM-T0159 "
        "--require-recommendation RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE "
        "--require-recommendation RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=total_active_token_work "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_required_steps_invariant "
        "--require-recommendation-evidence-field "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT="
        "periodic_shift_active_at_step_invariant "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0130 "
        "--require-recommendation-theorem "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=AIM-T0159 "
        "--require-recommendation-theorem "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=AIM-T0026 "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-action-parameter "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=loop_period "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=token_count "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=horizon_steps "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE=scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE="
        "post_period_multi_extension_scheduled_work_saving "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=base_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shifted_token "
        "--require-recommendation-action-parameter-path "
        "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT=shift_amount"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding "
        "--digest --field max_alias_load --include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout "
        "--digest --field full_coverage --field effective_candidate_budget "
        "--field duplicate_count --include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature "
        "--digest --field joint_repeat_horizon --field relative_phase "
        "--include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer "
        "--digest --field max_abs_dense_delta --field block_to_dense_ratio "
        "--include-recommendations"
    ),
    (
        "python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration "
        "--digest --field storage_saving --include-recommendations"
    ),
    "python -m pytest tests/test_circle_ai_contract_pack.py -q",
    "python -m pytest tests/test_circle_ai_contract_consumer.py -q",
    "python scripts/site/export_site_data.py",
    "python scripts/site/check_site_manifest_links.py",
    "python scripts/site/check_site_dictionary_links.py",
    "python scripts/site/check_site_theorem_status.py",
]


def _unique(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return tuple(ordered)


def _strip_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in sorted(value.items())
            if key not in FINGERPRINT_KEYS
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_fingerprint(value: Any) -> str:
    normalized = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _attach_contract_fingerprints(contracts: list[dict[str, Any]]) -> None:
    for contract in contracts:
        contract["content_fingerprint_algorithm"] = FINGERPRINT_ALGORITHM
        contract["content_fingerprint"] = _json_fingerprint(contract)


def _contract_fingerprint_index(
    contracts: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    return {
        contract["kind"]: {
            "id": contract["id"],
            "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
            "content_fingerprint": contract["content_fingerprint"],
        }
        for contract in contracts
    }


def _artifact_fields(kind: str) -> dict[str, Any]:
    artifacts = CONTRACT_ARTIFACTS.get(kind, {})
    return {
        "quickstart_docs": list(artifacts.get("quickstart_docs", ())),
        "living_book_pages": list(artifacts.get("living_book_pages", ())),
        "entrypoints": list(artifacts.get("entrypoints", ())),
        "validation_commands": list(artifacts.get("validation_commands", ())),
    }


def _proof_index_fields() -> dict[str, str]:
    return {
        "theorem_index": "site/data/generated/theorem_manifest.json",
        "dictionary_index": "site/data/generated/dictionary.json",
        "formal_source": "Lean declarations named by each theorem manifest entry",
    }


def _acceptance_policy_fields() -> dict[str, Any]:
    return {
        "schema_id": ACCEPTANCE_POLICY_SCHEMA_ID,
        "report_schema_id": ACCEPTANCE_POLICY_REPORT_SCHEMA_ID,
        "receipt_schema_id": ACCEPTANCE_RECEIPT_SCHEMA_ID,
        "rejection_report_schema_id": DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID,
        "policy_schema_path": ACCEPTANCE_POLICY_SCHEMA_PATH,
        "report_schema_path": ACCEPTANCE_POLICY_REPORT_SCHEMA_PATH,
        "receipt_schema_path": ACCEPTANCE_RECEIPT_SCHEMA_PATH,
        "rejection_report_schema_path": DOWNSTREAM_REJECTION_REPORT_SCHEMA_PATH,
        "default_policy_path": "examples/circle_ai_contract_acceptance_policy.json",
        "checker": "scripts/check_circle_ai_contract_acceptance_policy.py",
        "standalone_checker": "examples/downstream_ci_accept_circle_ai_contracts.py",
        "standalone_schema_checker": "scripts/check_downstream_ci_acceptance_example.py",
        "validation_commands": [
            "python scripts/check_circle_ai_contract_acceptance_policy.py",
            "python scripts/check_circle_ai_contract_acceptance_policy.py --format json",
            "python scripts/circle_ai_contract_ready.py --print-refreshed-policy",
            "python scripts/circle_ai_contract_ready.py --acceptance-policy-report",
            (
                "python scripts/circle_ai_contract_ready.py "
                "--acceptance-policy-report --format json"
            ),
            "python scripts/check_downstream_ci_acceptance_example.py --summary",
            "python examples/downstream_ci_accept_circle_ai_contracts.py --format json",
            "python examples/downstream_ci_accept_circle_ai_contracts.py --format text",
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK --include-values"
            ),
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR --include-values"
            ),
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK --include-values"
            ),
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "KV-USE-SINK-ROLLING-WINDOW-REQUEST --include-values"
            ),
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE --include-values"
            ),
            (
                "python examples/downstream_ci_accept_circle_ai_contracts.py "
                "--format json --planner-recommendation "
                "ROPE-USE-D19-MARGIN-FRONTIER --include-values"
            ),
        ],
        "fingerprint_refresh_command": (
            "python scripts/circle_ai_contract_ready.py --print-refreshed-policy"
        ),
        "pinned_requirement_keys": [
            "required_fields",
            "required_theorem_ids",
            "required_recommendation_ids",
            "required_recommendation_evidence_fields",
            "required_recommendation_theorem_ids",
            "required_recommendation_action_parameters",
            "required_recommendation_action_parameter_paths",
            "expected_pack_fingerprint",
            "expected_contract_fingerprint",
        ],
        "rule": (
            "Use the acceptance policy when a downstream project wants a locked "
            "receipt. Refreshing fingerprints must preserve required fields, "
            "theorem ids, recommendation ids, recommendation evidence fields, "
            "recommendation theorem ids, recommendation action-parameter pins, "
            "and recommendation action-parameter path pins."
        ),
    }


def _walk_manifest_entries(value: object) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            entries.append(value)
        for child in value.values():
            entries.extend(_walk_manifest_entries(child))
    elif isinstance(value, list):
        for child in value:
            entries.extend(_walk_manifest_entries(child))
    return entries


@lru_cache(maxsize=1)
def _manifest_entry_index() -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "manifests").glob("**/*.yaml")):
        data = yaml.safe_load(path.read_text()) or {}
        for entry in _walk_manifest_entries(data):
            entry_id = entry.get("id")
            if isinstance(entry_id, str) and entry_id not in entries:
                entries[entry_id] = entry
    return entries


def _proof_status_for(theorem_ids: list[str] | tuple[str, ...]) -> dict[str, Any]:
    index = _manifest_entry_index()
    theorem_records: list[dict[str, Any]] = []
    unresolved: list[str] = []
    unproved: list[str] = []
    for theorem_id in theorem_ids:
        entry = index.get(theorem_id)
        if entry is None:
            unresolved.append(theorem_id)
            unproved.append(theorem_id)
            theorem_records.append({
                "id": theorem_id,
                "resolved": False,
                "proved": False,
                "status": "missing",
                "lean_name": None,
            })
            continue
        status = str(entry.get("status", "")).strip()
        proved = status in PROVED_STATUSES
        if not proved:
            unproved.append(theorem_id)
        theorem_records.append({
            "id": theorem_id,
            "resolved": True,
            "proved": proved,
            "status": status,
            "lean_name": entry.get("lean_name"),
        })
    return {
        "source": "manifests/**/*.yaml",
        "proved_statuses": list(PROVED_STATUSES),
        "theorem_count": len(theorem_records),
        "all_theorem_ids_resolved": not unresolved,
        "all_theorem_ids_proved": not unresolved and not unproved,
        "unresolved_theorem_ids": unresolved,
        "unproved_theorem_ids": unproved,
        "theorems": theorem_records,
    }


def _consumer_check(
    kind: str,
    fields: dict[str, Any],
    contract_passed: bool,
    proof_status: dict[str, Any],
) -> dict[str, Any]:
    minimum_fields = list(MINIMUM_FIELDS_BY_KIND[kind])
    missing_fields = [field for field in minimum_fields if field not in fields]
    all_theorem_ids_resolved = bool(proof_status.get("all_theorem_ids_resolved"))
    all_theorem_ids_proved = bool(proof_status.get("all_theorem_ids_proved"))
    return {
        "minimum_fields": minimum_fields,
        "missing_minimum_fields": missing_fields,
        "required_fields_present": not missing_fields,
        "all_theorem_ids_resolved": all_theorem_ids_resolved,
        "all_theorem_ids_proved": all_theorem_ids_proved,
        "unresolved_theorem_ids": list(proof_status.get("unresolved_theorem_ids", [])),
        "unproved_theorem_ids": list(proof_status.get("unproved_theorem_ids", [])),
        "ready_for_downstream_fixture_use": (
            contract_passed
            and not missing_fields
            and all_theorem_ids_resolved
            and all_theorem_ids_proved
        ),
        "rule": (
            "A downstream project should require this block to be ready, preserve "
            "not_claimed, and keep theorem_ids attached to any derived report."
        ),
    }


def _with_consumer_check(item: dict[str, Any]) -> dict[str, Any]:
    item["proof_status"] = _proof_status_for(item.get("theorem_ids", []))
    item["consumer_check"] = _consumer_check(
        item["kind"],
        item["fields"],
        bool(item["contract_passed"]),
        item["proof_status"],
    )
    return item


def _readiness_entry(contract: dict[str, Any]) -> dict[str, Any]:
    consumer_check = contract["consumer_check"]
    proof_status = contract["proof_status"]
    planner_recommendations = contract.get("planner_recommendations", [])
    if not isinstance(planner_recommendations, list):
        planner_recommendations = []
    return {
        "id": contract["id"],
        "kind": contract["kind"],
        "ready_for_downstream_fixture_use": (
            consumer_check["ready_for_downstream_fixture_use"]
        ),
        "contract_passed": contract["contract_passed"],
        "required_fields_present": consumer_check["required_fields_present"],
        "missing_minimum_field_count": len(consumer_check["missing_minimum_fields"]),
        "missing_minimum_fields": list(consumer_check["missing_minimum_fields"]),
        "all_theorem_ids_resolved": consumer_check["all_theorem_ids_resolved"],
        "all_theorem_ids_proved": consumer_check["all_theorem_ids_proved"],
        "unresolved_theorem_count": len(consumer_check["unresolved_theorem_ids"]),
        "unresolved_theorem_ids": list(consumer_check["unresolved_theorem_ids"]),
        "unproved_theorem_count": len(consumer_check["unproved_theorem_ids"]),
        "unproved_theorem_ids": list(consumer_check["unproved_theorem_ids"]),
        "theorem_count": proof_status["theorem_count"],
        "entrypoint_count": len(contract["entrypoints"]),
        "quickstart_docs": list(contract["quickstart_docs"]),
        "living_book_pages": list(contract["living_book_pages"]),
        "planner_recommendation_count": len(planner_recommendations),
        "planner_recommendation_ids": [
            recommendation["id"]
            for recommendation in planner_recommendations
            if isinstance(recommendation, dict)
            and isinstance(recommendation.get("id"), str)
        ],
    }


def _readiness_index(contracts: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {contract["kind"]: _readiness_entry(contract) for contract in contracts}


def _planner_recommendation_index(
    contracts: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for contract in contracts:
        recommendations = contract.get("planner_recommendations", [])
        if not isinstance(recommendations, list):
            continue
        for recommendation in recommendations:
            if not isinstance(recommendation, dict):
                continue
            recommendation_id = recommendation.get("id")
            if not isinstance(recommendation_id, str):
                continue
            index[recommendation_id] = {
                "id": recommendation_id,
                "kind": contract["kind"],
                "contract_id": contract["id"],
                "ready_for_downstream_fixture_use": (
                    contract["consumer_check"]["ready_for_downstream_fixture_use"]
                    is True
                ),
                "action_kind": recommendation.get("action_kind"),
                "status": recommendation.get("status"),
                "coverage_scope": recommendation.get("coverage_scope"),
                "evidence_fields": list(recommendation.get("evidence_fields", [])),
                "theorem_ids": list(recommendation.get("theorem_ids", [])),
                "quickstart_docs": list(contract.get("quickstart_docs", [])),
                "living_book_pages": list(contract.get("living_book_pages", [])),
                "validation_commands": list(
                    contract.get("validation_commands", [])
                ),
                "source_paper": contract.get("source_paper"),
                "not_claimed": recommendation.get("not_claimed"),
            }
    return dict(sorted(index.items()))


FIELD_DESCRIPTION_OVERRIDES = {
    "certificate_schema_id": (
        "Versioned certificate schema identifier for this contract kind."
    ),
    "proof_layers": (
        "Names the exact, rational-threshold, and margin evidence layers exposed "
        "by the RoPE position-distinguishability contract."
    ),
    "common_collision_gap": (
        "Smallest positive position gap that collides across the exact discrete "
        "RoPE period bank in this fixture."
    ),
    "total_bank_collision_pair_count": (
        "Total number of colliding position pairs counted across the exact "
        "discrete RoPE period bank."
    ),
    "d19_proved_first_channel_bank_transfer": (
        "Boolean check that the proved D19 standard-channel request branch "
        "also transfers to a conditional first-channel finite-bank no-near-turn "
        "certificate."
    ),
    "d19_proved_first_channel_bank_tolerance_rule": (
        "Tolerance premise for applying the D19 first-channel finite-bank "
        "no-near-turn theorem."
    ),
    "d19_proved_first_channel_context_wide_contract": (
        "Boolean check that the D19 proved-branch first-channel bank transfer "
        "is packaged as a context-wide guarantee over every ordered unequal "
        "pair inside the requested context."
    ),
    "d19_proved_first_channel_radian_bank_form": (
        "Boolean check that the D19 context-wide first-channel guarantee is "
        "available in the ordinary radian bank form with first frequency 1 "
        "and full turn 2*pi."
    ),
    "d19_proved_first_channel_pair_scope": (
        "The ordered-pair scope covered by the D19 first-channel context-wide "
        "bank theorem."
    ),
    "first_uncovered_interval_start": (
        "Start of the first consecutive uncovered positive-lag interval in the "
        "sparse-attention coverage certificate."
    ),
    "first_uncovered_interval_stop": (
        "Inclusive end of the first consecutive uncovered positive-lag interval."
    ),
    "first_uncovered_interval_length": (
        "Number of consecutive missed positive lags in the first uncovered "
        "interval."
    ),
    "local_window_needed_to_cover_first_uncovered_interval": (
        "Local-window width that would cover the entire first uncovered interval "
        "locally."
    ),
    "first_uncovered_interval_additional_local_slots": (
        "Additional local-window slots needed to reach the end of the first "
        "uncovered interval."
    ),
    "first_uncovered_interval_repair_reaches_interval": (
        "Boolean theorem-backed check that the first-interval repair window "
        "reaches every lag in the reported first uncovered interval."
    ),
    "largest_uncovered_interval_start": (
        "Start of the longest consecutive uncovered positive-lag interval in "
        "the sparse-attention coverage certificate."
    ),
    "largest_uncovered_interval_stop": (
        "Inclusive end of the longest consecutive uncovered positive-lag interval."
    ),
    "largest_uncovered_interval_length": (
        "Number of consecutive missed positive lags in the longest uncovered "
        "interval."
    ),
    "local_window_needed_to_cover_largest_uncovered_interval": (
        "Local-window width that would cover the entire largest uncovered "
        "interval locally."
    ),
    "largest_uncovered_interval_additional_local_slots": (
        "Additional local-window slots needed to reach the end of the largest "
        "uncovered interval."
    ),
    "largest_uncovered_interval_repair_reaches_interval": (
        "Boolean computed check that the largest-interval repair window reaches "
        "every lag in the reported largest uncovered interval."
    ),
    "largest_uncovered_interval_is_tail": (
        "Boolean check that the largest uncovered interval reaches the final "
        "positive in-context lag."
    ),
    "local_window_complete_threshold_is_exact_local_minimum": (
        "Boolean theorem-backed check that the dense-local complete-coverage "
        "threshold is the exact local-only minimum, by AIT-T0023."
    ),
    "complete_repair_window_minimal_for_declared_stride_family": (
        "Boolean theorem-backed check that the complete repair window is "
        "minimal for the declared finite sparse-attention stride-family fixture."
    ),
    "complete_repair_window_minimal_witness_lag": (
        "Concrete positive lag that remains uncovered at the previous "
        "local-window width, witnessing minimality of the complete repair."
    ),
    "worst_margin_radians": (
        "Smallest observed real-phase separation margin, measured in radians, "
        "for the reported RoPE fixture."
    ),
    "d19_undecided_request_status": (
        "Request status for a D19 standard-channel-0 margin deliberately chosen "
        "inside the theorem-backed open interval between the proved and "
        "impossible thresholds."
    ),
    "d19_context_range_min_exclusive": (
        "Strict lower bound for the theorem-backed D19 standard-channel-0 "
        "request-classifier context range."
    ),
    "d19_context_range_max_inclusive": (
        "Inclusive upper bound for the theorem-backed D19 standard-channel-0 "
        "request-classifier context range."
    ),
    "d19_undecided_margin_open_gap": (
        "Boolean Lean-backed guard that the undecided D19 request margin lies "
        "strictly between the proved threshold and the impossible threshold."
    ),
    "d19_undecided_probe_margin_in_open_gap": (
        "Boolean Lean-backed guard that the public D19 undecided probe margin "
        "2/656917 lies strictly between the proved threshold and the "
        "impossible threshold."
    ),
    "d19_undecided_margin_interval_width": (
        "Exact rational width of the D19 open interval between the proved "
        "margin threshold and the impossible margin floor."
    ),
    "d19_undecided_request_relation": (
        "Stable request-relation label for the D19 undecided probe; it records "
        "that the requested margin is strictly between the two theorem-backed "
        "thresholds."
    ),
    "d19_in_range_semantic_trichotomy": (
        "Boolean Lean-backed guard that, inside the D19 context range, the "
        "requested margin is in exactly one semantic classifier branch: proved, "
        "impossible, or the deliberate undecided open gap."
    ),
    "stale_probe_first_stale_token": (
        "First requested token identified as stale by the KV-cache stale-read "
        "probe."
    ),
    "stale_probe_first_stale_next_overwrite_token": (
        "Next overwrite token for the first stale KV-cache probe miss."
    ),
    "sink_prefix_disjoint_from_live_window": (
        "Boolean check that the pinned sink prefix lies before the ordinary "
        "rolling live window in this KV-cache fixture."
    ),
    "sink_tokens_outside_ordinary_rolling_window": (
        "Boolean check that pinned sink-prefix tokens are not ordinary rolling "
        "live-window tokens and therefore need the sink-policy branch."
    ),
    "post_period_extension_active_work_unchanged": (
        "Boolean theorem-backed recurrence check that extending the schedule "
        "one step beyond the loop-period boundary adds no active-token work."
    ),
    "post_period_extension_inactive_work_added_token_count": (
        "Boolean theorem-backed recurrence check that the post-period extra "
        "step adds exactly one declared token count of inactive work."
    ),
    "post_period_extension_saving_added_token_count": (
        "Boolean theorem-backed recurrence check that scheduled-work saving "
        "increases by exactly one declared token count after the period boundary."
    ),
    "post_period_multi_extension_scheduled_work_saving": (
        "Scheduled-work saving after extending the recurrence horizon by a "
        "declared number of extra post-period steps."
    ),
    "post_period_multi_extension_active_work_unchanged": (
        "Boolean theorem-backed recurrence check that arbitrary post-period "
        "extension adds no active-token work."
    ),
    "post_period_multi_extension_saving_added_extra_token_count": (
        "Boolean theorem-backed recurrence check that arbitrary post-period "
        "extension increases scheduled-work saving by extra_steps * token_count."
    ),
    "effective_candidate_budget": (
        "Duplicate-collapsed candidate budget available after cyclic residue "
        "deduplication in the strided fanout contract."
    ),
    "candidate_budget_accounting": (
        "Boolean accounting check that raw candidate budget splits into unique "
        "candidates plus duplicates."
    ),
    "closure_condition": (
        "Human-readable stopping or closure rule used to certify exact "
        "regeneration from a seed and rule set."
    ),
    "bounded_search_candidates": (
        "Declared finite-search candidate comparison rows. Each row reports "
        "exact regeneration, description lengths, storage saving, and the "
        "rank within this declared search space only."
    ),
    "bounded_search_candidate_ids_by_generator_length": (
        "Stable declared candidate ids sorted by increasing generator "
        "description length within the bounded search fixture."
    ),
    "bounded_search_exact_candidate_ids_by_generator_length": (
        "Stable declared candidate ids for exact-regenerating candidates, "
        "sorted by increasing generator description length."
    ),
    "bounded_search_shorter_candidate_ids_by_generator_length": (
        "Stable declared candidate ids for exact candidates whose generator "
        "record is shorter than explicit object storage, sorted by increasing "
        "generator description length."
    ),
    "bounded_search_best_exact_candidate_id": (
        "Stable candidate id for the first exact-regenerating candidate under "
        "the bounded-search generator-length order."
    ),
    "bounded_search_best_shorter_candidate_id": (
        "Stable candidate id for the first exact shorter candidate under the "
        "bounded-search generator-length order."
    ),
}


def _json_value_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, (list, tuple)):
        return "array"
    if value is None:
        return "null"
    return type(value).__name__


def _field_description(kind: str, field: str) -> str:
    if field in FIELD_DESCRIPTION_OVERRIDES:
        return FIELD_DESCRIPTION_OVERRIDES[field]
    phrase = field.replace("_", " ")
    return (
        f"Required `{kind}` evidence field for `{phrase}`. Read it with the "
        "contract's theorem ids, proof_status block, and non-claim boundary."
    )


def _field_proof_role(field: str) -> str:
    if field == "certificate_schema_id":
        return "schema_identity"
    if (
        field.endswith("_pass")
        or "iff" in field
        or "invariant" in field
        or "accounting" in field
        or "matches" in field
        or "certifies" in field
        or "proved" in field
        or "impossible" in field
        or "open_gap" in field
        or "threshold" in field
        or "minimal" in field
        or field.startswith("exact_")
    ):
        return "theorem_backed_check"
    if any(
        token in field
        for token in (
            "count",
            "budget",
            "length",
            "period",
            "gap",
            "margin",
            "ratio",
            "saving",
            "window",
            "horizon",
        )
    ):
        return "finite_quantity_or_bound"
    return "fixture_parameter_or_observation"


def _minimum_field_catalog(
    contracts: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, str]]]:
    contracts_by_kind = {contract["kind"]: contract for contract in contracts}
    catalog: dict[str, dict[str, dict[str, str]]] = {}
    for kind, minimum_fields in sorted(MINIMUM_FIELDS_BY_KIND.items()):
        contract = contracts_by_kind.get(kind, {})
        fields = contract.get("fields", {})
        if not isinstance(fields, dict):
            fields = {}
        catalog[kind] = {
            field: {
                "description": _field_description(kind, field),
                "value_kind": (
                    _json_value_kind(fields[field])
                    if field in fields
                    else "missing"
                ),
                "proof_role": _field_proof_role(field),
            }
            for field in minimum_fields
        }
    return catalog


def _string_array_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "uniqueItems": True,
    }


def _nonempty_string_array_schema() -> dict[str, Any]:
    schema = _string_array_schema()
    schema["minItems"] = 1
    return schema


def _string_or_string_array_schema() -> dict[str, Any]:
    return {
        "oneOf": [
            {"type": "string"},
            _string_array_schema(),
        ],
    }


def build_contract_pack_json_schema() -> dict[str, Any]:
    """Return a JSON Schema for the public Circle AI contract pack."""

    kind_enum = sorted(MINIMUM_FIELDS_BY_KIND)
    minimum_field_requirements = [
        {
            "if": {
                "properties": {"kind": {"const": kind}},
                "required": ["kind"],
            },
            "then": {
                "properties": {
                    "fields": {
                        "type": "object",
                        "required": list(fields),
                    }
                }
            },
        }
        for kind, fields in sorted(MINIMUM_FIELDS_BY_KIND.items())
    ]
    field_catalog_entry_schema = {
        "type": "object",
        "required": ["description", "value_kind", "proof_role"],
        "properties": {
            "description": {"type": "string", "minLength": 1},
            "value_kind": {
                "type": "string",
                "enum": [
                    "array",
                    "boolean",
                    "integer",
                    "null",
                    "number",
                    "object",
                    "string",
                ],
            },
            "proof_role": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://circle-calculus.local/schemas/circle_ai_contract_pack.schema.json",
        "title": "Circle AI Contract Pack",
        "description": (
            "Public, standalone Circle Calculus AI contract pack. The schema "
            "checks JSON shape and required consumer fields; Lean/manifests "
            "remain the formal proof source."
        ),
        "type": "object",
        "required": [
            "schema_id",
            "status",
            "claim_boundary",
            "content_fingerprint_algorithm",
            "pack_content_fingerprint",
            "proof_indexes",
            "acceptance_policy",
            "contract_schema",
            "validation_commands",
            "source_docs",
            "downstream_compatibility",
            "contract_readiness_index",
            "planner_recommendation_index",
            "contract_fingerprint_index",
            "contracts",
        ],
        "properties": {
            "schema_id": {"const": SCHEMA_ID},
            "status": {"type": "string"},
            "claim_boundary": {"type": "string", "minLength": 1},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "pack_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "proof_indexes": {"type": "object"},
            "acceptance_policy": {
                "type": "object",
                "required": [
                    "schema_id",
                    "report_schema_id",
                    "receipt_schema_id",
                    "rejection_report_schema_id",
                    "policy_schema_path",
                    "report_schema_path",
                    "receipt_schema_path",
                    "rejection_report_schema_path",
                    "default_policy_path",
                    "checker",
                    "standalone_checker",
                    "standalone_schema_checker",
                    "validation_commands",
                    "fingerprint_refresh_command",
                    "pinned_requirement_keys",
                    "rule",
                ],
                "properties": {
                    "schema_id": {"const": ACCEPTANCE_POLICY_SCHEMA_ID},
                    "report_schema_id": {
                        "const": ACCEPTANCE_POLICY_REPORT_SCHEMA_ID
                    },
                    "receipt_schema_id": {"const": ACCEPTANCE_RECEIPT_SCHEMA_ID},
                    "rejection_report_schema_id": {
                        "const": DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID
                    },
                    "policy_schema_path": {"type": "string", "minLength": 1},
                    "report_schema_path": {"type": "string", "minLength": 1},
                    "receipt_schema_path": {"type": "string", "minLength": 1},
                    "rejection_report_schema_path": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "default_policy_path": {"type": "string", "minLength": 1},
                    "checker": {"type": "string", "minLength": 1},
                    "standalone_checker": {"type": "string", "minLength": 1},
                    "standalone_schema_checker": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "validation_commands": _nonempty_string_array_schema(),
                    "fingerprint_refresh_command": {
                        "type": "string",
                        "minLength": 1,
                    },
                    "pinned_requirement_keys": _nonempty_string_array_schema(),
                    "rule": {"type": "string", "minLength": 1},
                },
                "additionalProperties": False,
            },
            "validation_commands": _nonempty_string_array_schema(),
            "source_docs": _nonempty_string_array_schema(),
            "downstream_compatibility": {"type": "object"},
            "contract_readiness_index": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": [
                        "id",
                        "kind",
                        "ready_for_downstream_fixture_use",
                        "all_theorem_ids_resolved",
                        "all_theorem_ids_proved",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^CC-AI-CONTRACT-"},
                        "kind": {"type": "string", "enum": kind_enum},
                        "ready_for_downstream_fixture_use": {"type": "boolean"},
                        "all_theorem_ids_resolved": {"type": "boolean"},
                        "all_theorem_ids_proved": {"type": "boolean"},
                        "planner_recommendation_count": {
                            "type": "integer",
                            "minimum": 0,
                        },
                        "planner_recommendation_ids": _string_array_schema(),
                    },
                    "additionalProperties": True,
                },
            },
            "planner_recommendation_index": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": [
                        "id",
                        "kind",
                        "contract_id",
                        "ready_for_downstream_fixture_use",
                        "action_kind",
                        "status",
                        "coverage_scope",
                        "evidence_fields",
                        "theorem_ids",
                        "quickstart_docs",
                        "living_book_pages",
                        "validation_commands",
                        "source_paper",
                        "not_claimed",
                    ],
                    "properties": {
                        "id": {"type": "string", "minLength": 1},
                        "kind": {"type": "string", "enum": kind_enum},
                        "contract_id": {
                            "type": "string",
                            "pattern": "^CC-AI-CONTRACT-",
                        },
                        "ready_for_downstream_fixture_use": {"type": "boolean"},
                        "action_kind": {"type": "string", "minLength": 1},
                        "status": {"type": "string", "minLength": 1},
                        "coverage_scope": {"type": "string", "minLength": 1},
                        "evidence_fields": _nonempty_string_array_schema(),
                        "theorem_ids": _nonempty_string_array_schema(),
                        "quickstart_docs": _nonempty_string_array_schema(),
                        "living_book_pages": _nonempty_string_array_schema(),
                        "validation_commands": _nonempty_string_array_schema(),
                        "source_paper": {"type": "string", "minLength": 1},
                        "not_claimed": {"type": "string", "minLength": 1},
                    },
                    "additionalProperties": True,
                },
            },
            "contract_fingerprint_index": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": [
                        "id",
                        "content_fingerprint_algorithm",
                        "content_fingerprint",
                    ],
                    "properties": {
                        "id": {"type": "string", "pattern": "^CC-AI-CONTRACT-"},
                        "content_fingerprint_algorithm": {
                            "const": FINGERPRINT_ALGORITHM
                        },
                        "content_fingerprint": {
                            "type": "string",
                            "pattern": "^[0-9a-f]{64}$",
                        },
                    },
                    "additionalProperties": False,
                },
            },
            "contract_schema": {
                "type": "object",
                "required": [
                    "required_contract_keys",
                    "minimum_fields_by_kind",
                    "minimum_field_catalog_by_kind",
                    "consumer_check_keys",
                ],
                "properties": {
                    "required_contract_keys": _string_array_schema(),
                    "minimum_fields_by_kind": {
                        "type": "object",
                        "required": kind_enum,
                        "properties": {
                            kind: {
                                "type": "array",
                                "items": {"type": "string"},
                                "contains": {"const": fields[0]},
                            }
                            for kind, fields in sorted(MINIMUM_FIELDS_BY_KIND.items())
                        },
                        "additionalProperties": False,
                    },
                    "minimum_field_catalog_by_kind": {
                        "type": "object",
                        "required": kind_enum,
                        "properties": {
                            kind: {
                                "type": "object",
                                "required": list(fields),
                                "additionalProperties": field_catalog_entry_schema,
                            }
                            for kind, fields in sorted(MINIMUM_FIELDS_BY_KIND.items())
                        },
                        "additionalProperties": False,
                    },
                    "consumer_check_keys": _string_array_schema(),
                    "planner_recommendation_keys": _string_array_schema(),
                },
                "additionalProperties": True,
            },
            "contracts": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": list(CONTRACT_REQUIRED_KEYS),
                    "properties": {
                        "id": {"type": "string", "pattern": "^CC-AI-CONTRACT-"},
                        "kind": {"type": "string", "enum": kind_enum},
                        "status": {"type": "string"},
                        "content_fingerprint_algorithm": {
                            "const": FINGERPRINT_ALGORITHM
                        },
                        "content_fingerprint": {
                            "type": "string",
                            "pattern": "^[0-9a-f]{64}$",
                        },
                        "theorem_ids": _nonempty_string_array_schema(),
                        "dictionary_ids": _nonempty_string_array_schema(),
                        "fields": {"type": "object"},
                        "proof_status": {
                            "type": "object",
                            "required": [
                                "all_theorem_ids_resolved",
                                "all_theorem_ids_proved",
                            ],
                            "properties": {
                                "all_theorem_ids_resolved": {"type": "boolean"},
                                "all_theorem_ids_proved": {"type": "boolean"},
                            },
                            "additionalProperties": True,
                        },
                        "contract_passed": {"type": "boolean"},
                        "integration_use": {"type": "string"},
                        "ordinary_baselines": _string_or_string_array_schema(),
                        "not_claimed": {"type": "string"},
                        "source_paper": {"type": "string", "minLength": 1},
                        "quickstart_docs": _nonempty_string_array_schema(),
                        "living_book_pages": _nonempty_string_array_schema(),
                        "entrypoints": _nonempty_string_array_schema(),
                        "validation_commands": _nonempty_string_array_schema(),
                        "consumer_check": {
                            "type": "object",
                            "required": [
                                "minimum_fields",
                                "missing_minimum_fields",
                                "required_fields_present",
                                "ready_for_downstream_fixture_use",
                            ],
                            "properties": {
                                "minimum_fields": _string_array_schema(),
                                "missing_minimum_fields": _string_array_schema(),
                                "required_fields_present": {"type": "boolean"},
                                "ready_for_downstream_fixture_use": {
                                    "type": "boolean"
                                },
                            },
                            "additionalProperties": True,
                        },
                        "planner_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": list(PLANNER_RECOMMENDATION_KEYS),
                                "properties": {
                                    "id": {"type": "string", "minLength": 1},
                                    "action_kind": {"type": "string", "minLength": 1},
                                    "status": {"type": "string", "minLength": 1},
                                    "coverage_scope": {"type": "string", "minLength": 1},
                                    "evidence_fields": _nonempty_string_array_schema(),
                                    "theorem_ids": _nonempty_string_array_schema(),
                                    "not_claimed": {"type": "string", "minLength": 1},
                                },
                                "additionalProperties": True,
                            },
                        },
                    },
                    "allOf": minimum_field_requirements,
                    "additionalProperties": True,
                },
            },
        },
        "additionalProperties": True,
    }


def build_acceptance_policy_json_schema() -> dict[str, Any]:
    kind_enum = sorted(MINIMUM_FIELDS_BY_KIND)
    requirement_map_schema = {
        "type": "object",
        "additionalProperties": _nonempty_string_array_schema(),
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_acceptance_policy.schema.json"
        ),
        "title": "Circle AI Contract Acceptance Policy",
        "description": (
            "Shape schema for downstream lockfiles that pin Circle AI contract "
            "pack fingerprints, contract fingerprints, evidence fields, theorem "
            "ids, and planner recommendation requirements. The policy checker "
            "remains responsible for validating the pinned values against the "
            "generated pack."
        ),
        "type": "object",
        "required": [
            "schema_id",
            "policy_id",
            "expected_pack_fingerprint",
            "contracts",
        ],
        "properties": {
            "schema_id": {"const": ACCEPTANCE_POLICY_SCHEMA_ID},
            "policy_id": {"type": "string", "minLength": 1},
            "policy_name": {"type": "string", "minLength": 1},
            "expected_pack_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "contracts": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": [
                        "kind",
                        "expected_contract_fingerprint",
                    ],
                    "properties": {
                        "kind": {"type": "string", "enum": kind_enum},
                        "expected_contract_fingerprint": {
                            "type": "string",
                            "pattern": "^[0-9a-f]{64}$",
                        },
                        "required_fields": _nonempty_string_array_schema(),
                        "required_theorem_ids": _nonempty_string_array_schema(),
                        "required_recommendation_ids": (
                            _nonempty_string_array_schema()
                        ),
                        "required_recommendation_evidence_fields": (
                            requirement_map_schema
                        ),
                        "required_recommendation_theorem_ids": (
                            requirement_map_schema
                        ),
                        "required_recommendation_action_parameters": (
                            requirement_map_schema
                        ),
                        "required_recommendation_action_parameter_paths": (
                            requirement_map_schema
                        ),
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    }


def _sha256_schema() -> dict[str, Any]:
    return {"type": "string", "pattern": "^[0-9a-f]{64}$"}


def _requirement_map_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": _string_array_schema(),
    }


def _planner_recommendation_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": list(PLANNER_RECOMMENDATION_KEYS),
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "action_kind": {"type": "string", "minLength": 1},
            "status": {"type": "string", "minLength": 1},
            "coverage_scope": {"type": "string", "minLength": 1},
            "evidence_fields": _nonempty_string_array_schema(),
            "theorem_ids": _nonempty_string_array_schema(),
            "not_claimed": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def _acceptance_receipt_object_schema() -> dict[str, Any]:
    kind_enum = sorted(MINIMUM_FIELDS_BY_KIND)
    return {
        "type": "object",
        "required": [
            "schema_id",
            "receipt_schema",
            "accepted",
            "kind",
            "contract_id",
            "content_fingerprint_algorithm",
            "pack_content_fingerprint",
            "contract_content_fingerprint",
            "required_fields",
            "required_theorem_ids",
            "evidence_fields",
            "required_recommendation_ids",
            "required_recommendation_evidence_fields",
            "required_recommendation_theorem_ids",
            "required_recommendation_action_parameters",
            "required_recommendation_action_parameter_paths",
            "planner_recommendations",
            "theorem_ids",
            "dictionary_ids",
            "quickstart_docs",
            "living_book_pages",
            "validation_commands",
            "source_paper",
            "not_claimed",
        ],
        "properties": {
            "schema_id": {"const": SCHEMA_ID},
            "receipt_schema": {"const": ACCEPTANCE_RECEIPT_SCHEMA_ID},
            "accepted": {"const": True},
            "kind": {"type": "string", "enum": kind_enum},
            "contract_id": {"type": "string", "pattern": "^CC-AI-CONTRACT-"},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "pack_content_fingerprint": _sha256_schema(),
            "contract_content_fingerprint": _sha256_schema(),
            "required_fields": _string_array_schema(),
            "required_theorem_ids": _string_array_schema(),
            "evidence_fields": {"type": "object"},
            "required_recommendation_ids": _string_array_schema(),
            "required_recommendation_evidence_fields": _requirement_map_schema(),
            "required_recommendation_theorem_ids": _requirement_map_schema(),
            "required_recommendation_action_parameters": _requirement_map_schema(),
            "required_recommendation_action_parameter_paths": _requirement_map_schema(),
            "planner_recommendations": {
                "type": "array",
                "items": _planner_recommendation_schema(),
            },
            "theorem_ids": _nonempty_string_array_schema(),
            "dictionary_ids": _nonempty_string_array_schema(),
            "quickstart_docs": _nonempty_string_array_schema(),
            "living_book_pages": _nonempty_string_array_schema(),
            "validation_commands": _nonempty_string_array_schema(),
            "source_paper": {"type": "string", "minLength": 1},
            "not_claimed": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def build_acceptance_receipt_json_schema() -> dict[str, Any]:
    """Return a JSON Schema for strict downstream acceptance receipts."""

    schema = _acceptance_receipt_object_schema()
    schema.update({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_acceptance_receipt.schema.json"
        ),
        "title": "Circle AI Contract Acceptance Receipt",
        "description": (
            "Shape schema for strict downstream receipts emitted after a "
            "Circle AI contract satisfies pinned evidence, theorem, "
            "recommendation, and planner-payload requirements. The receipt "
            "schema validates the consumer artifact shape; Lean and manifest "
            "checks remain the formal proof source."
        ),
    })
    return schema


def build_acceptance_policy_report_json_schema() -> dict[str, Any]:
    """Return a JSON Schema for multi-contract acceptance-policy reports."""

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_acceptance_policy_report.schema.json"
        ),
        "title": "Circle AI Contract Acceptance Policy Report",
        "description": (
            "Shape schema for reports emitted after a pinned Circle AI "
            "acceptance policy validates selected contract receipts."
        ),
        "type": "object",
        "required": [
            "schema_id",
            "acceptance_policy_report_schema",
            "policy_schema",
            "accepted",
            "content_fingerprint_algorithm",
            "pack_content_fingerprint",
            "expected_pack_fingerprint",
            "contract_count",
            "receipt_count",
            "receipts",
            "not_claimed",
        ],
        "properties": {
            "schema_id": {"const": SCHEMA_ID},
            "acceptance_policy_report_schema": {
                "const": ACCEPTANCE_POLICY_REPORT_SCHEMA_ID
            },
            "policy_schema": {"const": ACCEPTANCE_POLICY_SCHEMA_ID},
            "policy_id": {"type": ["string", "null"]},
            "policy_name": {"type": ["string", "null"]},
            "accepted": {"const": True},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "pack_content_fingerprint": _sha256_schema(),
            "expected_pack_fingerprint": {"type": ["string", "null"]},
            "contract_count": {"type": "integer", "minimum": 0},
            "receipt_count": {"type": "integer", "minimum": 0},
            "receipts": {
                "type": "array",
                "items": _acceptance_receipt_object_schema(),
            },
            "not_claimed": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def build_downstream_rejection_report_json_schema() -> dict[str, Any]:
    """Return a JSON Schema for standalone downstream CI rejection reports."""

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_downstream_rejection_report.schema.json"
        ),
        "title": "Circle AI Downstream CI Rejection Report",
        "description": (
            "Shape schema for machine-readable rejection reports emitted by the "
            "standard-library-only downstream CI example when a pinned Circle AI "
            "contract pack or acceptance policy is rejected."
        ),
        "type": "object",
        "required": [
            "schema_id",
            "example_schema_id",
            "accepted",
            "error",
            "failure_count",
            "failures",
            "pack_path",
            "policy_path",
            "planner_requested_recommendation_ids",
            "not_claimed",
        ],
        "properties": {
            "schema_id": {"const": DOWNSTREAM_REJECTION_REPORT_SCHEMA_ID},
            "example_schema_id": {
                "const": "circle_calculus.downstream_ci_acceptance_example.v0"
            },
            "accepted": {"const": False},
            "error": {"type": "string", "minLength": 1},
            "failure_count": {"type": "integer", "minimum": 1},
            "failures": _nonempty_string_array_schema(),
            "pack_path": {"type": "string", "minLength": 1},
            "policy_path": {"type": "string", "minLength": 1},
            "planner_requested_recommendation_ids": _string_array_schema(),
            "not_claimed": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def _generic_contract(contract: dict[str, Any]) -> dict[str, Any]:
    kind = contract["kind"]
    item = dict(contract)
    compatibility_id = item["id"]
    item["id"] = GENERIC_IDS[kind]
    item["compatibility_ids"] = [compatibility_id]
    item["integration_use"] = GENERIC_USES[kind]
    item.update(_artifact_fields(kind))
    if "source_paper" not in item and "source_paper" in CONTRACT_ARTIFACTS.get(kind, {}):
        item["source_paper"] = CONTRACT_ARTIFACTS[kind]["source_paper"]
    item["downstream_compatibility"] = {
        "theseus_hive": {
            "contract_id": compatibility_id,
            "use": item.pop("theseus_hive_use", ""),
        }
    }
    item["not_claimed"] = CLAIM_BOUNDARY
    planner_recommendations = _generic_planner_recommendations(kind, item["fields"])
    if planner_recommendations:
        item["planner_recommendations"] = planner_recommendations
    return _with_consumer_check(item)


def _generic_planner_recommendations(
    kind: str,
    fields: dict[str, Any],
) -> list[dict[str, Any]]:
    if kind == "rope_position_distinguishability":
        return [
            {
                "id": "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK",
                "action_kind": "audit_exact_integer_phase_bank_collision_boundary",
                "status": "theorem_backed_exact_discrete_fixture",
                "coverage_scope": "declared_integer_period_phase_bank_fixture",
                "preset": fields["preset"],
                "context_length": fields["context_length"],
                "exact_discrete_pass": fields["exact_discrete_pass"],
                "common_collision_gap": fields["common_collision_gap"],
                "collision_pair_count": fields["total_bank_collision_pair_count"],
                "evidence_fields": [
                    "preset",
                    "context_length",
                    "exact_discrete_pass",
                    "common_collision_gap",
                    "total_bank_collision_pair_count",
                ],
                "theorem_ids": [
                    "AIRA-T0024",
                    "AIRA-T0036",
                    "AIRA-T0179",
                    "AIRA-T0180",
                    "AIRA-T0184",
                ],
                "not_claimed": (
                    "This recommendation audits the declared integer-period "
                    "phase-bank model only. It is not a proof of all-channel "
                    "real-valued RoPE distinguishability, model quality, long "
                    "context behavior, or training/deployment performance."
                ),
            },
            {
                "id": "ROPE-USE-D19-MARGIN-FRONTIER",
                "action_kind": "use_d19_theorem_backed_margin_frontier",
                "status": "theorem_backed_standard_channel0_request_classifier",
                "coverage_scope": "standard_channel0_d19_context_range_fixture",
                "request_context": fields["d19_request_context"],
                "proved_margin": fields["d19_proved_margin"],
                "impossible_margin_floor": fields["d19_impossible_margin_floor"],
                "proved_status": fields["d19_proved_request_status"],
                "impossible_status": fields["d19_impossible_request_status"],
                "undecided_margin": fields["d19_undecided_request_margin"],
                "undecided_status": fields["d19_undecided_request_status"],
                "undecided_probe_margin_in_open_gap": fields[
                    "d19_undecided_probe_margin_in_open_gap"
                ],
                "undecided_interval": {
                    "lower_exclusive": fields[
                        "d19_undecided_margin_interval_lower_exclusive"
                    ],
                    "upper_exclusive": fields[
                        "d19_undecided_margin_interval_upper_exclusive"
                    ],
                    "width": fields["d19_undecided_margin_interval_width"],
                },
                "applicable_context_range": {
                    "min_exclusive": fields["d19_context_range_min_exclusive"],
                    "max_inclusive": fields["d19_context_range_max_inclusive"],
                },
                "proved_branch_bank_transfer": {
                    "applies": fields["d19_proved_first_channel_bank_transfer"],
                    "bank_shape": fields["d19_proved_first_channel_bank_shape"],
                    "pair_scope": fields["d19_proved_first_channel_pair_scope"],
                    "context_wide_contract": fields[
                        "d19_proved_first_channel_context_wide_contract"
                    ],
                    "radian_bank_form": fields[
                        "d19_proved_first_channel_radian_bank_form"
                    ],
                    "tolerance_rule": fields[
                        "d19_proved_first_channel_bank_tolerance_rule"
                    ],
                    "theorem_ids": [
                        "AIRA-T0171",
                        "AIRA-T0172",
                        "AIRA-T0234",
                        "AIRA-T0235",
                        "AIRA-T0236",
                        "AIRA-T0237",
                    ],
                },
                "classifier_regions": [
                    {
                        "region": "proved",
                        "condition": "requested_margin <= 1/328459",
                        "request_status": fields["d19_proved_request_status"],
                        "theorem_backed_classification": fields[
                            "d19_proved_request_theorem_backed_classification"
                        ],
                        "theorem_backed_region": True,
                        "theorem_ids": ["AIRA-T0216", "AIRA-T0217", "AIRA-T0233"],
                        "meaning": (
                            "Inside 103993 < context <= 196608, the requested "
                            "one-channel standard RoPE margin is certified. "
                            "The proved branch also transfers to a conditional "
                            "first-channel finite-bank no-near-turn guarantee."
                        ),
                    },
                    {
                        "region": "undecided_margin_gap",
                        "condition": "1/328459 < requested_margin < 1/328458",
                        "request_status": fields["d19_undecided_request_status"],
                        "theorem_backed_classification": fields[
                            "d19_undecided_request_theorem_backed_classification"
                        ],
                        "theorem_backed_region": fields[
                            "d19_undecided_margin_open_gap"
                        ],
                        "theorem_ids": [
                            "AIRA-T0220",
                            "AIRA-T0221",
                            "AIRA-T0232",
                            "AIRA-T0233",
                            "AIRA-T0238",
                        ],
                        "meaning": (
                            "Lean identifies this as the open interval between "
                            "the proved and impossible branches; the current "
                            "contract deliberately does not certify or reject "
                            "that margin."
                        ),
                    },
                    {
                        "region": "impossible",
                        "condition": "1/328458 <= requested_margin",
                        "request_status": fields["d19_impossible_request_status"],
                        "theorem_backed_classification": fields[
                            "d19_impossible_request_theorem_backed_classification"
                        ],
                        "theorem_backed_region": True,
                        "theorem_ids": ["AIRA-T0217", "AIRA-T0219", "AIRA-T0233"],
                        "meaning": (
                            "Inside 103993 < context <= 196608, gap 103993 "
                            "obstructs any advertised margin at or above "
                            "1/328458."
                        ),
                    },
                ],
                "evidence_fields": [
                    "d19_context_range_min_exclusive",
                    "d19_context_range_max_inclusive",
                    "d19_request_context",
                    "d19_proved_margin",
                    "d19_impossible_margin_floor",
                    "d19_proved_request_status",
                    "d19_proved_request_theorem_backed_classification",
                    "d19_impossible_request_status",
                    "d19_impossible_request_theorem_backed_classification",
                    "d19_undecided_request_margin",
                    "d19_undecided_request_status",
                    "d19_undecided_margin_open_gap",
                    "d19_undecided_probe_margin_in_open_gap",
                    "d19_undecided_margin_interval_width",
                    "d19_undecided_request_relation",
                    "d19_margin_thresholds_ordered",
                    "d19_proved_impossible_branches_disjoint",
                    "d19_margin_status_exhaustive",
                    "d19_in_range_semantic_trichotomy",
                    "d19_proved_first_channel_bank_transfer",
                    "d19_proved_first_channel_bank_shape",
                    "d19_proved_first_channel_pair_scope",
                    "d19_proved_first_channel_context_wide_contract",
                    "d19_proved_first_channel_radian_bank_form",
                    "d19_proved_first_channel_bank_tolerance_rule",
                ],
                "theorem_ids": [
                    "AIRA-T0171",
                    "AIRA-T0172",
                    "AIRA-T0216",
                    "AIRA-T0217",
                    "AIRA-T0218",
                    "AIRA-T0219",
                    "AIRA-T0220",
                    "AIRA-T0221",
                    "AIRA-T0232",
                    "AIRA-T0233",
                    "AIRA-T0234",
                    "AIRA-T0235",
                    "AIRA-T0236",
                    "AIRA-T0237",
                    "AIRA-T0238",
                    "AIRA-T0230",
                    "AIRA-T0231",
                ],
                "not_claimed": (
                    "This recommendation exposes the D19 standard-channel-0 "
                    "margin frontier for request gating and a conditional "
                    "first-channel finite-bank transfer for the proved branch. "
                    "It does not transfer the impossible branch to a whole-bank "
                    "collision claim, is not a Diophantine theorem for arbitrary "
                    "RoPE frequencies, and is not a model-quality or "
                    "context-length extension claim."
                ),
            },
        ]
    if kind == "recurrence_schedule":
        token_count = len(fields.get("tokens", []))
        return [
            {
                "id": "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE",
                "action_kind": "use_active_token_work_schedule",
                "status": "theorem_backed_work_budget_fixture",
                "coverage_scope": "finite_default_loop_schedule_fixture",
                "loop_period": fields["loop_period"],
                "token_count": token_count,
                "horizon_steps": fields["total_work_horizon_steps"],
                "active_token_count_trace": fields["active_token_count_trace"],
                "inactive_token_count_trace": fields["inactive_token_count_trace"],
                "active_token_work": fields["total_active_token_work"],
                "inactive_token_work": fields["total_inactive_token_work"],
                "full_loop_token_work": fields["full_loop_token_work"],
                "scheduled_work_saving": fields["scheduled_work_saving"],
                "post_period_extension_horizon_steps": (
                    fields["post_period_extension_horizon_steps"]
                ),
                "post_period_extension_scheduled_work_saving": (
                    fields["post_period_extension_scheduled_work_saving"]
                ),
                "post_period_extra_steps": fields["post_period_extra_steps"],
                "post_period_multi_extension_horizon_steps": (
                    fields["post_period_multi_extension_horizon_steps"]
                ),
                "post_period_multi_extension_scheduled_work_saving": (
                    fields["post_period_multi_extension_scheduled_work_saving"]
                ),
                "evidence_fields": [
                    "total_work_horizon_steps",
                    "active_token_count_trace",
                    "inactive_token_count_trace",
                    "active_token_count_trace_sum",
                    "inactive_token_count_trace_sum",
                    "active_token_count_trace_sum_matches_total",
                    "inactive_token_count_trace_sum_matches_total",
                    "first_inactive_steps",
                    "first_inactive_steps_match_budget_successor",
                    "total_active_token_work",
                    "total_inactive_token_work",
                    "full_loop_token_work",
                    "scheduled_work_saving",
                    "scheduled_work_saving_accounting",
                    "active_inactive_work_accounting",
                    "scheduled_work_saving_matches_inactive_work",
                    "scheduled_work_saving_positive",
                    "active_work_below_full_loop_work",
                    "scheduled_work_saving_positive_iff_active_work_shortfall",
                    "post_period_extension_horizon_steps",
                    "post_period_extension_total_active_token_work",
                    "post_period_extension_total_inactive_token_work",
                    "post_period_extension_full_loop_token_work",
                    "post_period_extension_scheduled_work_saving",
                    "post_period_extension_active_work_unchanged",
                    "post_period_extension_inactive_work_added_token_count",
                    "post_period_extension_saving_added_token_count",
                    "post_period_extra_steps",
                    "post_period_multi_extension_horizon_steps",
                    "post_period_multi_extension_total_active_token_work",
                    "post_period_multi_extension_total_inactive_token_work",
                    "post_period_multi_extension_full_loop_token_work",
                    "post_period_multi_extension_scheduled_work_saving",
                    "post_period_multi_extension_active_work_unchanged",
                    "post_period_multi_extension_inactive_work_added_extra_token_count",
                    "post_period_multi_extension_saving_added_extra_token_count",
                ],
                "theorem_ids": [
                    "AIM-T0130",
                    "AIM-T0131",
                    "AIM-T0138",
                    "AIM-T0140",
                    "AIM-T0141",
                    "AIM-T0142",
                    "AIM-T0143",
                    "AIM-T0144",
                    "AIM-T0145",
                    "AIM-T0147",
                    "AIM-T0150",
                    "AIM-T0151",
                    "AIM-T0152",
                    "AIM-T0153",
                    "AIM-T0154",
                    "AIM-T0155",
                    "AIM-T0156",
                    "AIM-T0157",
                    "AIM-T0158",
                    "AIM-T0159",
                ],
                "not_claimed": (
                    "This recommendation exposes a finite active-token work "
                    "schedule and saved-work accounting fixture. It is not a "
                    "runtime, memory, reasoning-quality, convergence, or "
                    "model-quality proof."
                ),
            },
            {
                "id": "RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT",
                "action_kind": "reuse_whole_period_shifted_schedule_index",
                "status": "theorem_backed_index_reuse_fixture",
                "coverage_scope": "whole_loop_period_token_shift_fixture",
                "loop_period": fields["loop_period"],
                "base_token": fields["periodic_shift_base_token"],
                "shift_passes": fields["periodic_shift_passes"],
                "shift_amount": fields["periodic_shift_amount"],
                "shifted_token": fields["periodic_shifted_token"],
                "active_step": fields["periodic_shift_active_step"],
                "evidence_fields": [
                    "periodic_shift_base_token",
                    "periodic_shift_passes",
                    "periodic_shift_amount",
                    "periodic_shifted_token",
                    "periodic_shift_required_steps_invariant",
                    "periodic_shift_recurrence_budget_invariant",
                    "periodic_shift_training_free_budget_invariant",
                    "periodic_shift_exit_step_invariant",
                    "periodic_shift_overthinking_boundary_invariant",
                    "periodic_shift_active_step",
                    "periodic_shift_active_at_step_invariant",
                ],
                "theorem_ids": [
                    "AIM-T0026",
                    "AIM-T0027",
                    "AIM-T0028",
                    "AIM-T0029",
                    "AIM-T0030",
                    "AIM-T0033",
                    "AIM-T0034",
                    "AIM-T0036",
                ],
                "not_claimed": (
                    "This recommendation identifies a finite whole-period "
                    "index-reuse witness for schedule fields. It is not a proof "
                    "that a real looped transformer reasons better, halts "
                    "correctly, or can reuse implementation state safely without "
                    "a separate system contract."
                ),
            },
        ]
    if kind == "cyclic_memory_residue_winding":
        return [
            {
                "id": "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE",
                "action_kind": "attach_winding_to_same_slot_aliases",
                "status": "computed_from_theorem_backed_slot_fixture",
                "coverage_scope": "finite_same_residue_alias_class_fixture",
                "bank_size": fields["bank_size"],
                "event_index": fields["event_index"],
                "residue_slot": fields["residue_slot"],
                "winding": fields["winding"],
                "alias_count": len(fields["same_residue_events"]),
                "evidence_fields": [
                    "bank_size",
                    "event_index",
                    "event_count",
                    "residue_slot",
                    "winding",
                    "same_residue_events",
                    "same_residue_windings",
                ],
                "theorem_ids": [
                    "AIM-T0001",
                    "AIM-T0002",
                    "AIM-T0004",
                ],
                "not_claimed": (
                    "This recommendation exposes winding/provenance fields for "
                    "events that share a finite cyclic memory slot. It is not a "
                    "retrieval-quality, memory-scaling, cache-policy, semantic "
                    "identity, deployment, or model-quality proof."
                ),
            },
            {
                "id": "MEMORY-AUDIT-FINITE-ALIAS-LOAD",
                "action_kind": "audit_finite_slot_alias_load",
                "status": "computed_from_finite_trace_fixture_fields",
                "coverage_scope": "declared_finite_trace_slot_loads",
                "bank_size": fields["bank_size"],
                "event_count": fields["event_count"],
                "max_alias_load": fields["max_alias_load"],
                "slot_loads": list(fields["slot_loads"]),
                "evidence_fields": [
                    "bank_size",
                    "event_count",
                    "slot_loads",
                    "max_alias_load",
                ],
                "theorem_ids": [
                    "AIM-T0001",
                    "AIM-T0005",
                ],
                "not_claimed": (
                    "This recommendation reports finite slot-load pressure for "
                    "the declared trace only. It is not a throughput, memory "
                    "capacity, retrieval-quality, allocation-policy, or "
                    "model-quality theorem."
                ),
            },
        ]
    if kind == "strided_candidate_fanout":
        return [
            {
                "id": "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE",
                "action_kind": "use_full_coverage_stride_candidate_cycle",
                "status": "theorem_backed_gcd_full_coverage_fixture",
                "coverage_scope": "finite_coprime_stride_orbit_fixture",
                "context_length": fields["context_length"],
                "stride": fields["stride"],
                "gcd": fields["gcd"],
                "predicted_reach": fields["predicted_reach"],
                "full_coverage": fields["full_coverage"],
                "evidence_fields": [
                    "context_length",
                    "stride",
                    "gcd",
                    "predicted_reach",
                    "orbit",
                    "full_coverage",
                ],
                "theorem_ids": [
                    "AIT-T0001",
                    "AIT-T0002",
                    "AIT-T0003",
                ],
                "not_claimed": (
                    "This recommendation identifies a finite stride cycle that "
                    "covers the declared candidate context. It is not a search, "
                    "retrieval, routing-quality, runtime, or model-quality proof."
                ),
            },
            {
                "id": "FANOUT-AUDIT-DUPLICATE-COLLAPSED-BUDGET",
                "action_kind": "audit_duplicate_collapsed_candidate_budget",
                "status": "computed_from_finite_candidate_path_fixture_fields",
                "coverage_scope": "declared_fixed_budget_candidate_path",
                "candidate_budget": fields["candidate_budget"],
                "unique_candidate_count": fields["unique_candidate_count"],
                "effective_candidate_budget": fields["effective_candidate_budget"],
                "duplicate_count": fields["duplicate_count"],
                "candidate_budget_shortfall": fields["candidate_budget_shortfall"],
                "evidence_fields": [
                    "candidate_path",
                    "candidate_budget",
                    "unique_candidate_count",
                    "effective_candidate_budget",
                    "duplicate_count",
                    "candidate_budget_accounting",
                    "effective_budget_matches_unique_candidates",
                    "candidate_budget_shortfall",
                    "effective_budget_reaches_predicted_reach",
                ],
                "theorem_ids": [
                    "AIT-T0001",
                    "AIT-T0002",
                    "AIT-T0173",
                ],
                "not_claimed": (
                    "This recommendation exposes finite duplicate-collapse "
                    "accounting for the declared candidate path only. It is not "
                    "a ranking, recall, retrieval-quality, throughput, or "
                    "model-quality theorem."
                ),
            },
        ]
    if kind == "multicoil_phase_feature":
        return [
            {
                "id": "PHASE-USE-JOINT-REPEAT-HORIZON",
                "action_kind": "use_joint_repeat_horizon_phase_tags",
                "status": "theorem_backed_phase_tuple_shift_fixture",
                "coverage_scope": "declared_finite_period_bank_fixture",
                "periods": list(fields["periods"]),
                "position": fields["position"],
                "phase_tuple": list(fields["phase_tuple"]),
                "joint_repeat_horizon": fields["joint_repeat_horizon"],
                "shifted_position": fields["shifted_position"],
                "shifted_phase_tuple": list(fields["shifted_phase_tuple"]),
                "evidence_fields": [
                    "periods",
                    "position",
                    "phase_tuple",
                    "joint_repeat_horizon",
                    "shifted_position",
                    "shifted_phase_tuple",
                ],
                "theorem_ids": [
                    "AIA-T0001",
                    "AIA-T0002",
                    "AIA-T0004",
                ],
                "not_claimed": (
                    "This recommendation exposes finite phase tags and a joint "
                    "repeat horizon for the declared period bank. It is not a "
                    "learned-embedding, extrapolation, training-stability, "
                    "context-length, or model-quality proof."
                ),
            },
            {
                "id": "PHASE-AUDIT-RELATIVE-SHIFT-INVARIANT",
                "action_kind": "audit_relative_phase_common_shift_invariant",
                "status": "theorem_backed_relative_phase_fixture",
                "coverage_scope": "declared_query_key_relative_phase_fixture",
                "query_position": fields["query_position"],
                "key_position": fields["key_position"],
                "relative_period": fields["relative_period"],
                "relative_phase": fields["relative_phase"],
                "shifted_relative_phase": fields["shifted_relative_phase"],
                "evidence_fields": [
                    "query_position",
                    "key_position",
                    "relative_period",
                    "relative_phase",
                    "shifted_relative_phase",
                ],
                "theorem_ids": [
                    "AIT-T0004",
                    "AIT-T0005",
                ],
                "not_claimed": (
                    "This recommendation audits one finite query/key relative "
                    "phase fixture under a common shift. It is not an attention "
                    "quality, retrieval, equivariant-model, or model-quality "
                    "theorem."
                ),
            },
        ]
    if kind == "circulant_block_cyclic_mixer":
        return [
            {
                "id": "MIXER-AUDIT-CIRCULANT-DENSE-PARITY",
                "action_kind": "audit_circulant_dense_reference_parity",
                "status": "theorem_backed_circulant_fixture_parity",
                "coverage_scope": "deterministic_circulant_fixture",
                "period": fields["period"],
                "max_abs_dense_delta": fields["max_abs_dense_delta"],
                "circulant_parameters": fields["circulant_parameters"],
                "dense_parameters": fields["dense_parameters"],
                "circulant_parameter_ratio": fields["circulant_parameter_ratio"],
                "evidence_fields": [
                    "period",
                    "input_values",
                    "kernel_values",
                    "circulant_output",
                    "dense_output",
                    "max_abs_dense_delta",
                    "circulant_parameters",
                    "dense_parameters",
                    "circulant_parameter_ratio",
                ],
                "theorem_ids": [
                    "AIT-T0006",
                    "AIT-T0007",
                    "AIT-T0008",
                    "AIT-T0009",
                ],
                "not_claimed": (
                    "This recommendation audits exact dense-reference parity "
                    "for one deterministic circulant fixture. It is not a "
                    "speed, memory, hardware-efficiency, training-stability, "
                    "or model-quality proof."
                ),
            },
            {
                "id": "MIXER-AUDIT-BLOCK-CYCLIC-PARAMETER-BUDGET",
                "action_kind": "audit_block_cyclic_parameter_budget",
                "status": "theorem_backed_block_cyclic_accounting_fixture",
                "coverage_scope": "declared_block_cyclic_adapter_fixture",
                "channel_count": fields["channel_count"],
                "block_size": fields["block_size"],
                "dense_adapter_parameters": fields["dense_adapter_parameters"],
                "lora_parameters": fields["lora_parameters"],
                "block_cyclic_parameters": fields["block_cyclic_parameters"],
                "block_to_dense_ratio": fields["block_to_dense_ratio"],
                "evidence_fields": [
                    "channel_count",
                    "block_size",
                    "block_loads",
                    "dense_adapter_parameters",
                    "lora_parameters",
                    "block_cyclic_parameters",
                    "block_to_dense_ratio",
                ],
                "theorem_ids": [
                    "AIRA-T0001",
                    "AIRA-T0002",
                    "AIRA-T0004",
                ],
                "not_claimed": (
                    "This recommendation exposes finite block-cyclic adapter "
                    "parameter accounting for the declared fixture. It is not "
                    "a LoRA replacement theorem, memory-scaling proof, "
                    "hardware-efficiency proof, or model-quality claim."
                ),
            },
        ]
    if kind == "seed_rule_exact_regeneration":
        return [
            {
                "id": "SEED-RULE-USE-EXACT-REGENERATION-RECIPE",
                "action_kind": "use_seed_rule_exact_regeneration_recipe",
                "status": "theorem_backed_finite_generation_fixture",
                "coverage_scope": "public_finite_circle_fixture",
                "artifact_id": fields["artifact_id"],
                "fixture_n": fields["fixture_n"],
                "rule_ids": [rule["rule_id"] for rule in fields["rules"]],
                "generated_object_length": len(fields["generated_object"]),
                "evidence_fields": [
                    "artifact_id",
                    "fixture_n",
                    "seed",
                    "rules",
                    "generated_object",
                    "regenerated_object",
                    "exact_regeneration",
                    "closure_condition",
                ],
                "theorem_ids": [
                    "GEN-T0040",
                    "GEN-T0041",
                    "GEN-T0043",
                ],
                "not_claimed": (
                    "This recommendation exposes the public finite-circle "
                    "seed/rule recipe as an exact-regeneration fixture. It is "
                    "not a universal generator, compression, global-minimality, "
                    "program-synthesis, or model-quality proof."
                ),
            },
            {
                "id": "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE",
                "action_kind": "select_bounded_exact_shorter_candidate",
                "status": "theorem_backed_bounded_search_storage_fixture",
                "coverage_scope": "declared_finite_candidate_search",
                "search_id": fields["bounded_search_id"],
                "candidate_count": fields["bounded_search_candidate_count"],
                "exact_candidate_count": fields[
                    "bounded_search_exact_candidate_count"
                ],
                "best_shorter_artifact_id": fields[
                    "bounded_search_best_shorter_artifact_id"
                ],
                "best_shorter_candidate_id": fields[
                    "bounded_search_best_shorter_candidate_id"
                ],
                "explicit_length": fields["explicit_length"],
                "generator_length": fields["generator_length"],
                "storage_saving": fields["storage_saving"],
                "candidate_ids_by_generator_length": fields[
                    "bounded_search_candidate_ids_by_generator_length"
                ],
                "evidence_fields": [
                    "bounded_search_id",
                    "bounded_search_finite_search_space",
                    "bounded_search_candidate_count",
                    "bounded_search_exact_candidate_count",
                    "bounded_search_exact_candidate_count_le_candidate_count",
                    "bounded_search_has_best_exact",
                    "bounded_search_best_exact_exists_iff_exact_count_positive",
                    "bounded_search_best_exact_implies_candidate_count_positive",
                    "bounded_search_best_exact_artifact_id",
                    "bounded_search_best_exact_candidate_id",
                    "bounded_search_best_exact_regenerates",
                    "bounded_search_has_best_shorter",
                    "bounded_search_best_shorter_artifact_id",
                    "bounded_search_best_shorter_candidate_id",
                    "bounded_search_best_shorter_generator_shorter",
                    "bounded_search_candidates",
                    "bounded_search_candidate_ids_by_generator_length",
                    "bounded_search_exact_candidate_ids_by_generator_length",
                    "bounded_search_shorter_candidate_ids_by_generator_length",
                    "explicit_length",
                    "generator_length",
                    "storage_saving",
                    "storage_saving_positive",
                    "generator_shorter",
                    "generator_shorter_iff_positive_saving",
                    "storage_saving_add_generator_length_eq_explicit_length",
                    "bounded_search_note",
                ],
                "theorem_ids": [
                    "GEN-T0037",
                    "GEN-T0044",
                    "GEN-T0045",
                    "GEN-T0046",
                    "GEN-T0047",
                    "GEN-T0048",
                    "GEN-T0049",
                    "GEN-T0050",
                ],
                "not_claimed": (
                    "This recommendation selects the best shorter candidate "
                    "inside the declared finite search fixture only. It is not "
                    "a global optimality, Kolmogorov-complexity, compression, "
                    "semantic-equivalence, or model-quality theorem."
                ),
            },
        ]
    return []


def _rope_position_contract() -> dict[str, Any]:
    certificate = certify_rope_positions(ROPE_CERTIFIER_PRESETS["llama_style_10000_4k"])
    proved_request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(1, 328459),
    )
    impossible_request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(1, 328458),
    )
    undecided_request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(2, 656917),
    )
    first_channel_bank = certify_standard_channel0_d19_bank_request(
        requested_context=131072,
        requested_margin=Fraction(1, 328459),
        first_channel_shape=True,
    )
    config = certificate.config
    fields = {
        "certificate_schema_id": certificate.schema_id,
        "preset": "llama_style_10000_4k",
        "head_dim": config.head_dim,
        "base": config.base,
        "context_length": config.context_length,
        "tolerance": config.tolerance,
        "discretization": config.discretization,
        "exact_discrete_pass": certificate.exact_discrete.pass_exact,
        "common_collision_gap": certificate.exact_discrete.common_collision_gap,
        "total_bank_collision_pair_count": (
            certificate.exact_discrete.total_bank_collision_pair_count
        ),
        "real_phase_margin_pass": certificate.real_phase_margin.pass_margin,
        "worst_margin_radians": certificate.real_phase_margin.worst_margin_radians,
        "d19_request_context": proved_request.requested_context,
        "d19_context_range_min_exclusive": (
            proved_request.context_range_min_exclusive
        ),
        "d19_context_range_max_inclusive": (
            proved_request.context_range_max_inclusive
        ),
        "d19_proved_margin": proved_request.proved_margin,
        "d19_impossible_margin_floor": proved_request.impossible_margin_floor,
        "d19_proved_request_margin": proved_request.requested_margin,
        "d19_proved_request_status": proved_request.request_status,
        "d19_proved_request_theorem_backed_classification": (
            proved_request.theorem_backed_classification
        ),
        "d19_proved_request_margin_applies": proved_request.proved_margin_applies,
        "d19_impossible_request_margin": impossible_request.requested_margin,
        "d19_impossible_request_status": impossible_request.request_status,
        "d19_impossible_request_theorem_backed_classification": (
            impossible_request.theorem_backed_classification
        ),
        "d19_impossible_request_margin_applies": (
            impossible_request.impossible_margin_applies
        ),
        "d19_undecided_request_margin": undecided_request.requested_margin,
        "d19_undecided_request_status": undecided_request.request_status,
        "d19_undecided_request_theorem_backed_classification": (
            undecided_request.theorem_backed_classification
        ),
        "d19_undecided_margin_open_gap": (
            undecided_request.undecided_margin_open_gap
        ),
        "d19_undecided_probe_margin_in_open_gap": (
            undecided_request.requested_margin == "2/656917"
            and undecided_request.undecided_margin_open_gap
            and "AIRA-T0238" in undecided_request.theorem_ids
        ),
        "d19_undecided_margin_interval_lower_exclusive": (
            undecided_request.undecided_margin_interval_lower_exclusive
        ),
        "d19_undecided_margin_interval_upper_exclusive": (
            undecided_request.undecided_margin_interval_upper_exclusive
        ),
        "d19_undecided_margin_interval_width": (
            undecided_request.undecided_margin_interval_width
        ),
        "d19_proved_request_relation": proved_request.requested_margin_relation,
        "d19_impossible_request_relation": (
            impossible_request.requested_margin_relation
        ),
        "d19_undecided_request_relation": (
            undecided_request.requested_margin_relation
        ),
        "d19_undecided_request_failure_reason": (
            undecided_request.failure_reason
        ),
        "d19_margin_thresholds_ordered": proved_request.margin_thresholds_ordered,
        "d19_proved_impossible_branches_disjoint": (
            proved_request.proved_impossible_branches_disjoint
            and impossible_request.proved_impossible_branches_disjoint
            and undecided_request.proved_impossible_branches_disjoint
        ),
        "d19_margin_status_exhaustive": (
            proved_request.margin_status_exhaustive
            and impossible_request.margin_status_exhaustive
            and undecided_request.margin_status_exhaustive
        ),
        "d19_in_range_semantic_trichotomy": (
            proved_request.in_range_semantic_trichotomy
            and impossible_request.in_range_semantic_trichotomy
            and undecided_request.in_range_semantic_trichotomy
        ),
        "d19_proved_first_channel_bank_transfer": (
            first_channel_bank.pass_certificate
        ),
        "d19_proved_first_channel_bank_shape": first_channel_bank.bank_shape,
        "d19_proved_first_channel_pair_scope": (
            first_channel_bank.context_wide_pair_scope
        ),
        "d19_proved_first_channel_context_wide_contract": (
            first_channel_bank.context_wide_first_channel_contract
        ),
        "d19_proved_first_channel_radian_bank_form": (
            first_channel_bank.pass_certificate
            and first_channel_bank.bank_shape == "standard_channel0_first"
            and "AIRA-T0236" in first_channel_bank.theorem_ids
        ),
        "d19_proved_first_channel_bank_tolerance_rule": (
            first_channel_bank.tolerance_rule
        ),
        "proof_layers": [
            {
                "layer": layer.layer,
                "status": layer.status,
                "theorem_backed": layer.theorem_backed,
            }
            for layer in certificate.proof_layers
        ],
    }
    planner_recommendations = _generic_planner_recommendations(
        "rope_position_distinguishability",
        fields,
    )
    return _with_consumer_check({
        "id": GENERIC_IDS["rope_position_distinguishability"],
        "kind": "rope_position_distinguishability",
        "status": "fixture",
        "source_paper": CONTRACT_ARTIFACTS["rope_position_distinguishability"]["source_paper"],
        "theorem_ids": list(
            _unique(
                certificate.theorem_ids
                + proved_request.theorem_ids
                + undecided_request.theorem_ids
                + first_channel_bank.theorem_ids
                + ROPE_EXACT_RATIONAL_THRESHOLD_THEOREMS
            )
        ),
        "dictionary_ids": ["COMMON-0076", "COMMON-0077"],
        "fields": fields,
        "contract_passed": (
            certificate.exact_discrete.pass_exact
            and certificate.real_phase_margin.pass_margin
            and proved_request.request_status == "proved"
            and proved_request.theorem_backed_classification
            and impossible_request.request_status == "impossible"
            and impossible_request.theorem_backed_classification
            and undecided_request.request_status == "undecided_margin_gap"
            and not undecided_request.theorem_backed_classification
            and undecided_request.undecided_margin_open_gap
            and fields["d19_undecided_probe_margin_in_open_gap"]
            and proved_request.margin_thresholds_ordered
            and proved_request.proved_impossible_branches_disjoint
            and impossible_request.proved_impossible_branches_disjoint
            and undecided_request.proved_impossible_branches_disjoint
            and proved_request.margin_status_exhaustive
            and impossible_request.margin_status_exhaustive
            and undecided_request.margin_status_exhaustive
            and first_channel_bank.pass_certificate
        ),
        "integration_use": GENERIC_USES["rope_position_distinguishability"],
        "ordinary_baselines": [
            "standard_rope_config_audit",
            "uncertified_long_context_scaling",
            "raw_float_phase_scan",
        ],
        "not_claimed": CLAIM_BOUNDARY,
        "compatibility_ids": [],
        "planner_recommendations": planner_recommendations,
        **_artifact_fields("rope_position_distinguishability"),
    })


def _kv_cache_contract() -> dict[str, Any]:
    adapter = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(20, 24, 29, 31),
        request_id="public_pack_read_request",
    )
    stale_probe = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(12, 20),
        request_id="public_pack_stale_probe",
    )
    live_window = certify_kv_cache_live_window(cache_size=16, current=31)
    sink_window = certify_kv_cache_sink_window(sink_size=4, cache_size=16, current=31)
    theorem_ids = _unique(
        adapter.theorem_ids
        + stale_probe.theorem_ids
        + live_window.theorem_ids
        + sink_window.theorem_ids
        + getattr(adapter, "fixture_theorem_ids", ())
        + getattr(stale_probe, "fixture_theorem_ids", ())
        + getattr(live_window, "fixture_theorem_ids", ())
        + sink_window.fixture_theorem_ids
    )
    fields = {
        "certificate_schema_id": "circle_calculus.kv_cache_ring_buffer_certificate.v0",
        "cache_size": adapter.cache_size,
        "current": adapter.current,
        "requested_tokens": list(adapter.requested_tokens),
        "requested_slots": list(adapter.requested_slots),
        "adapter_request_pass": adapter.pass_certificate,
        "stale_requested_count": adapter.stale_requested_count,
        "stale_count_zero_iff_no_stale_member": (
            adapter.stale_requested_count_zero_iff_no_stale_member
        ),
        "pass_iff_stale_count_zero_under_nonfuture_nodup": (
            adapter.pass_iff_stale_count_zero_under_nonfuture_nodup
        ),
        "fail_iff_stale_count_positive_under_nonfuture_nodup": (
            adapter.fail_iff_stale_count_positive_under_nonfuture_nodup
        ),
        "stale_probe_request_id": stale_probe.request_id,
        "stale_probe_requested_tokens": list(stale_probe.requested_tokens),
        "stale_probe_requested_slots": list(stale_probe.requested_slots),
        "stale_probe_all_non_future": stale_probe.all_non_future,
        "stale_probe_tokens_distinct": stale_probe.tokens_distinct,
        "stale_probe_pass": stale_probe.pass_certificate,
        "stale_probe_first_stale_token": stale_probe.first_stale_token,
        "stale_probe_first_stale_next_overwrite_token": (
            stale_probe.first_stale_next_overwrite_token
        ),
        "stale_probe_stale_requested_count": stale_probe.stale_requested_count,
        "stale_probe_stale_count_zero_iff_no_stale_member": (
            stale_probe.stale_requested_count_zero_iff_no_stale_member
        ),
        "stale_probe_stale_member_blocks_pass": (
            stale_probe.stale_member_blocks_pass
        ),
        "stale_probe_pass_iff_stale_count_zero_under_nonfuture_nodup": (
            stale_probe.pass_iff_stale_count_zero_under_nonfuture_nodup
        ),
        "stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup": (
            stale_probe.fail_iff_stale_count_positive_under_nonfuture_nodup
        ),
        "live_window_full_coverage": live_window.full_coverage_contract,
        "live_window_slot_range_covered": live_window.slot_range_covered,
        "sink_size": sink_window.sink_size,
        "sink_window_tokens": list(sink_window.tokens),
        "sink_window_token_count": sink_window.token_count,
        "sink_window_token_count_bound": sink_window.token_count_bound,
        "sink_window_token_count_le_sink_plus_cache": (
            sink_window.token_count_le_sink_plus_cache
        ),
        "sink_window_live_window_start": sink_window.live_window_start,
        "sink_window_live_window_length": sink_window.live_window_length,
        "sink_window_disjoint_exact_token_count": (
            sink_window.disjoint_exact_token_count
        ),
        "sink_window_token_count_eq_sink_plus_live_window_when_disjoint": (
            sink_window.token_count_eq_sink_plus_live_window_when_disjoint
        ),
        "sink_prefix_disjoint_from_live_window": (
            sink_window.sink_prefix_disjoint_from_live_window
        ),
        "sink_window_tokens_distinct": sink_window.tokens_distinct,
        "sink_window_exact_policy": sink_window.generated_tokens_exact_policy,
        "sink_window_rolling_tokens_match_filtered_live_window": (
            sink_window.rolling_tokens_match_filtered_live_window
        ),
        "sink_rolling_tokens_retained": sink_window.rolling_tokens_retained,
        "sink_tokens_are_seen_prefix": sink_window.sink_tokens_are_seen_prefix,
        "sink_tokens_non_future": sink_window.sink_tokens_non_future,
        "sink_tokens_retained_by_policy": (
            sink_window.sink_tokens_retained_by_policy
        ),
        "sink_tokens_outside_ordinary_rolling_window": (
            sink_window.sink_tokens_outside_ordinary_rolling_window
        ),
    }
    planner_recommendations = [
        {
            "id": "KV-DROP-STALE-REQUEST-TOKEN",
            "action_kind": "reject_or_drop_stale_requested_token",
            "status": "theorem_backed_stale_probe",
            "coverage_scope": "modeled_adapter_request_stale_probe",
            "target_token": stale_probe.first_stale_token,
            "next_same_slot_overwrite_token": (
                stale_probe.first_stale_next_overwrite_token
            ),
            "stale_requested_count": stale_probe.stale_requested_count,
            "evidence_fields": [
                "stale_probe_first_stale_token",
                "stale_probe_first_stale_next_overwrite_token",
                "stale_probe_stale_requested_count",
                "stale_probe_stale_member_blocks_pass",
                "stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup",
            ],
            "theorem_ids": ["AIM-T0097", "AIM-T0103"],
            "not_claimed": (
                "This recommendation identifies a stale requested token in a "
                "finite modeled adapter request. It is not a kernel, paging, "
                "serving-stack, retrieval-quality, or model-quality proof."
            ),
        },
        {
            "id": "KV-USE-SINK-ROLLING-WINDOW-REQUEST",
            "action_kind": "use_generated_sink_window_request",
            "status": "theorem_backed_request_list_policy_fixture",
            "coverage_scope": "pinned_seen_prefix_plus_rolling_live_window",
            "sink_size": sink_window.sink_size,
            "cache_size": sink_window.cache_size,
            "current": sink_window.current,
            "request_token_count": sink_window.token_count,
            "request_token_count_bound": sink_window.token_count_bound,
            "evidence_fields": [
                "sink_size",
                "sink_window_token_count",
                "sink_window_token_count_bound",
                "sink_window_token_count_le_sink_plus_cache",
                "sink_window_exact_policy",
                "sink_window_tokens_distinct",
                "sink_prefix_disjoint_from_live_window",
                "sink_rolling_tokens_retained",
                "sink_tokens_non_future",
                "sink_tokens_retained_by_policy",
                "sink_tokens_outside_ordinary_rolling_window",
            ],
            "theorem_ids": [
                "AIM-T0104",
                "AIM-T0110",
                "AIM-T0117",
                "AIM-T0136",
                "AIM-T0137",
                "AIM-T0148",
                "AIM-T0149",
            ],
            "not_claimed": (
                "This recommendation exposes the generated pinned-prefix plus "
                "rolling-window request list as a finite policy fixture. It "
                "does not prove StreamingLLM quality, paging correctness, "
                "throughput, memory savings, or retrieval accuracy."
            ),
        },
    ]
    return _with_consumer_check({
        "id": GENERIC_IDS["kv_cache_ring_buffer"],
        "kind": "kv_cache_ring_buffer",
        "status": "fixture",
        "source_paper": CONTRACT_ARTIFACTS["kv_cache_ring_buffer"]["source_paper"],
        "theorem_ids": list(theorem_ids),
        "dictionary_ids": ["COMMON-0028", "COMMON-0081"],
        "fields": fields,
        "contract_passed": (
            adapter.pass_certificate
            and not stale_probe.pass_certificate
            and stale_probe.first_stale_token == 12
            and stale_probe.first_stale_next_overwrite_token == 28
            and stale_probe.stale_requested_count == 1
            and stale_probe.stale_member_blocks_pass
            and stale_probe.pass_iff_stale_count_zero_under_nonfuture_nodup
            and stale_probe.fail_iff_stale_count_positive_under_nonfuture_nodup
            and live_window.full_coverage_contract
            and sink_window.generated_tokens_exact_policy
            and sink_window.rolling_tokens_match_filtered_live_window
            and sink_window.rolling_tokens_retained
            and sink_window.sink_tokens_are_seen_prefix
            and sink_window.sink_tokens_non_future
            and sink_window.sink_tokens_retained_by_policy
            and sink_window.sink_prefix_disjoint_from_live_window
            and sink_window.sink_tokens_outside_ordinary_rolling_window
            and sink_window.token_count_le_sink_plus_cache
            and sink_window.token_count_eq_sink_plus_live_window_when_disjoint
            and sink_window.tokens_distinct
        ),
        "integration_use": GENERIC_USES["kv_cache_ring_buffer"],
        "ordinary_baselines": [
            "uncertified_ring_buffer_indexing",
            "rolling_window_only",
            "paged_cache_without_trace_certificate",
        ],
        "not_claimed": CLAIM_BOUNDARY,
        "compatibility_ids": [],
        "planner_recommendations": planner_recommendations,
        **_artifact_fields("kv_cache_ring_buffer"),
    })


def _sparse_attention_contract() -> dict[str, Any]:
    certificate = certify_stride_family_coverage(
        sequence_length=120,
        strides=(7, 13),
        path_length=3,
        local_window=4,
    )
    fields = {
        "certificate_schema_id": "circle_calculus.stride_family_sparse_attention_certificate.v0",
        "sequence_length": certificate.sequence_length,
        "strides": list(certificate.strides),
        "path_length": certificate.path_length,
        "local_window": certificate.local_window,
        "coverage_complete": certificate.coverage_complete,
        "covered_lag_count": certificate.covered_lag_count,
        "uncovered_lag_count": certificate.uncovered_lag_count,
        "uncovered_lag_intervals": [
            {"start": start, "stop": stop}
            for start, stop in certificate.uncovered_lag_intervals
        ],
        "first_uncovered_lag": certificate.first_uncovered_lag,
        "first_uncovered_interval_start": (
            certificate.first_uncovered_lag_interval_start
        ),
        "first_uncovered_interval_stop": (
            certificate.first_uncovered_lag_interval_stop
        ),
        "first_uncovered_interval_length": (
            certificate.first_uncovered_lag_interval_length
        ),
        "local_window_needed_to_cover_first_uncovered_interval": (
            certificate.first_uncovered_lag_interval_repair_window
        ),
        "first_uncovered_interval_additional_local_slots": (
            certificate.first_uncovered_lag_interval_additional_local_slots
        ),
        "first_uncovered_interval_repair_reaches_interval": (
            certificate.first_uncovered_interval_repair_reaches_interval
        ),
        "first_interval_repair_next_uncovered_lag": (
            certificate.first_interval_repair_next_uncovered_lag
        ),
        "first_interval_repair_still_has_gap": (
            certificate.first_interval_repair_still_has_gap
        ),
        "first_interval_repair_covers_context": (
            certificate.first_interval_repair_covers_context
        ),
        "largest_uncovered_interval_start": (
            certificate.largest_uncovered_interval_start
        ),
        "largest_uncovered_interval_stop": (
            certificate.largest_uncovered_interval_stop
        ),
        "largest_uncovered_interval_length": (
            certificate.largest_uncovered_interval_length
        ),
        "local_window_needed_to_cover_largest_uncovered_interval": (
            certificate.largest_uncovered_interval_repair_window
        ),
        "largest_uncovered_interval_additional_local_slots": (
            certificate.largest_uncovered_interval_additional_local_slots
        ),
        "largest_uncovered_interval_repair_reaches_interval": (
            certificate.largest_uncovered_interval_repair_reaches_interval
        ),
        "largest_interval_repair_next_uncovered_lag": (
            certificate.largest_interval_repair_next_uncovered_lag
        ),
        "largest_interval_repair_still_has_gap": (
            certificate.largest_interval_repair_still_has_gap
        ),
        "largest_interval_repair_covers_context": (
            certificate.largest_interval_repair_covers_context
        ),
        "largest_uncovered_interval_is_tail": (
            certificate.largest_uncovered_interval_is_tail
        ),
        "first_gap_is_semantic_miss": certificate.first_uncovered_lag_gap_witness,
        "first_gap_local_window_shortfall": (
            certificate.first_uncovered_lag_local_window_shortfall
        ),
        "local_window_needed_to_cover_first_gap": (
            certificate.first_uncovered_lag_repair_window
        ),
        "current_window_below_first_gap": (
            certificate.first_uncovered_lag_exceeds_local_window
        ),
        "first_gap_repair_window_reaches": (
            certificate.first_uncovered_lag_repair_window_reaches
        ),
        "first_gap_repair_window_covers_context": (
            certificate.first_uncovered_lag_repair_window_covers_context
        ),
        "first_gap_repair_window_is_final_positive_lag": (
            certificate.first_gap_repair_window_is_final_positive_lag
        ),
        "first_gap_repair_threshold_matches_final_lag": (
            certificate.first_gap_repair_threshold_matches_final_lag
        ),
        "local_window_complete_coverage_threshold": (
            certificate.local_window_complete_coverage_threshold
        ),
        "local_window_complete_coverage_shortfall": (
            certificate.local_window_complete_coverage_shortfall
        ),
        "local_window_reaches_complete_coverage_threshold": (
            certificate.local_window_reaches_complete_coverage_threshold
        ),
        "local_window_threshold_certifies_complete": (
            certificate.local_window_threshold_certifies_complete
        ),
        "local_window_complete_threshold_is_exact_local_minimum": (
            certificate.local_window_complete_threshold_is_exact_local_minimum
        ),
        "complete_repair_window": certificate.complete_repair_window,
        "complete_repair_window_additional_local_slots": (
            certificate.complete_repair_window_additional_local_slots
        ),
        "complete_repair_window_covers_context": (
            certificate.complete_repair_window_covers_context
        ),
        "complete_repair_window_uses_dense_threshold": (
            certificate.complete_repair_window_uses_dense_threshold
        ),
        "complete_repair_window_minimal_for_declared_stride_family": (
            certificate.complete_repair_window_minimal_for_declared_stride_family
        ),
        "complete_repair_window_minimal_witness_lag": (
            certificate.complete_repair_window_minimal_witness_lag
        ),
        "interval_repair_plan": [
            {
                "target_interval_start": start,
                "target_interval_stop": stop,
                "proposed_local_window": proposed_window,
                "additional_local_slots": additional_slots,
                "remaining_gap_count_after_repair": remaining_gap_count,
            }
            for (
                start,
                stop,
                proposed_window,
                additional_slots,
                remaining_gap_count,
            ) in certificate.interval_repair_plan
        ],
        "interval_repair_plan_step_count": (
            certificate.interval_repair_plan_step_count
        ),
        "interval_repair_plan_final_window": (
            certificate.interval_repair_plan_final_window
        ),
        "interval_repair_plan_covers_context": (
            certificate.interval_repair_plan_covers_context
        ),
        "interval_repair_plan_strictly_progresses": (
            certificate.interval_repair_plan_strictly_progresses
        ),
        "first_gap_repair_window_reaches_complete_threshold": (
            certificate.first_gap_repair_window_reaches_complete_threshold
        ),
        "raw_budget_shortfall_certifies_incomplete": (
            certificate.raw_budget_shortfall_certifies_incomplete
        ),
        "unique_lag_count_shortfall_certifies_incomplete": (
            certificate.unique_lag_count_shortfall_certifies_incomplete
        ),
        "lag_dedup_loss": certificate.theorem_side_lag_candidate_dedup_loss,
        "lag_collision_pair_count": (
            certificate.theorem_side_lag_candidate_collision_pair_count
        ),
        "lag_collision_pair_count_zero_iff_no_collision": (
            certificate.lag_collision_pair_count_zero_matches_no_collision
        ),
        "lag_collision_pair_count_positive_iff_collision": (
            certificate.lag_collision_pair_count_positive_matches_collision
        ),
        "lag_collision_pair_count_bounds_dedup_loss": (
            certificate.lag_collision_pair_count_bounds_dedup_loss
        ),
        "lag_collision_pair_count_excess_over_dedup_loss": (
            certificate.lag_collision_pair_count_excess_over_dedup_loss
        ),
        "lag_dedup_loss_zero_iff_no_collision": (
            certificate.lag_dedup_loss_zero_matches_no_collision
        ),
        "lag_dedup_loss_positive_iff_collision": (
            certificate.lag_dedup_loss_positive_matches_collision
        ),
        "lag_unique_plus_loss_eq_raw": (
            certificate.lag_dedup_loss_accounting_matches_raw
        ),
        "query_dedup_loss": certificate.theorem_side_query_candidate_dedup_loss,
        "query_collision_pair_count": (
            certificate.theorem_side_query_candidate_collision_pair_count
        ),
        "query_collision_pair_count_zero_iff_no_collision": (
            certificate.query_collision_pair_count_zero_matches_no_collision
        ),
        "query_collision_pair_count_positive_iff_collision": (
            certificate.query_collision_pair_count_positive_matches_collision
        ),
        "query_collision_pair_count_bounds_dedup_loss": (
            certificate.query_collision_pair_count_bounds_dedup_loss
        ),
        "query_collision_pair_count_excess_over_dedup_loss": (
            certificate.query_collision_pair_count_excess_over_dedup_loss
        ),
        "query_dedup_loss_zero_iff_no_collision": (
            certificate.query_dedup_loss_zero_matches_no_collision
        ),
        "query_dedup_loss_positive_iff_collision": (
            certificate.query_dedup_loss_positive_matches_collision
        ),
        "query_unique_plus_loss_eq_raw": (
            certificate.query_dedup_loss_accounting_matches_raw
        ),
    }
    planner_recommendations = [
        {
            "id": "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR",
            "action_kind": "increase_local_window",
            "status": "computed_from_theorem_backed_fixture_fields",
            "coverage_scope": "first_uncovered_interval_only",
            "proposed_local_window": (
                certificate.first_uncovered_lag_interval_repair_window
            ),
            "additional_local_slots": (
                certificate.first_uncovered_lag_interval_additional_local_slots
            ),
            "target_interval_start": certificate.first_uncovered_lag_interval_start,
            "target_interval_stop": certificate.first_uncovered_lag_interval_stop,
            "target_interval_length": certificate.first_uncovered_lag_interval_length,
            "next_uncovered_lag_after_repair": (
                certificate.first_interval_repair_next_uncovered_lag
            ),
            "still_has_gap_after_repair": (
                certificate.first_interval_repair_still_has_gap
            ),
            "evidence_fields": [
                "first_uncovered_interval_start",
                "first_uncovered_interval_stop",
                "first_uncovered_interval_length",
                "local_window_needed_to_cover_first_uncovered_interval",
                "first_uncovered_interval_additional_local_slots",
                "first_uncovered_interval_repair_reaches_interval",
                "first_interval_repair_next_uncovered_lag",
                "first_interval_repair_still_has_gap",
                "first_interval_repair_covers_context",
            ],
            "theorem_ids": ["AIT-T0104", "AIT-T0171", "AIT-T0166", "AIT-T0167"],
            "not_claimed": (
                "This repair target covers the first reported gap interval only; "
                "it is not a complete sparse-attention coverage theorem and not "
                "a performance recommendation."
            ),
        },
        {
            "id": "SPARSE-REPAIR-LARGEST-GAP-INTERVAL",
            "action_kind": "increase_local_window",
            "status": "computed_from_certificate_gap_fields",
            "coverage_scope": "largest_uncovered_interval",
            "proposed_local_window": (
                certificate.largest_uncovered_interval_repair_window
            ),
            "additional_local_slots": (
                certificate.largest_uncovered_interval_additional_local_slots
            ),
            "target_interval_start": certificate.largest_uncovered_interval_start,
            "target_interval_stop": certificate.largest_uncovered_interval_stop,
            "target_interval_length": certificate.largest_uncovered_interval_length,
            "next_uncovered_lag_after_repair": (
                certificate.largest_interval_repair_next_uncovered_lag
            ),
            "still_has_gap_after_repair": (
                certificate.largest_interval_repair_still_has_gap
            ),
            "covers_context_after_repair": (
                certificate.largest_interval_repair_covers_context
            ),
            "largest_interval_is_tail": (
                certificate.largest_uncovered_interval_is_tail
            ),
            "evidence_fields": [
                "largest_uncovered_interval_start",
                "largest_uncovered_interval_stop",
                "largest_uncovered_interval_length",
                "local_window_needed_to_cover_largest_uncovered_interval",
                "largest_uncovered_interval_additional_local_slots",
                "largest_uncovered_interval_repair_reaches_interval",
                "largest_interval_repair_next_uncovered_lag",
                "largest_interval_repair_still_has_gap",
                "largest_interval_repair_covers_context",
                "largest_uncovered_interval_is_tail",
                "uncovered_lag_intervals",
            ],
            "theorem_ids": ["AIT-T0094", "AIT-T0104", "AIT-T0171"],
            "not_claimed": (
                "This action highlights the largest reported gap interval and "
                "the local-window value that reaches it. It is not a proof of "
                "optimal sparse layout choice, not a learned-quality result, "
                "and not a recommendation to use dense local attention."
            ),
        },
        {
            "id": "SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK",
            "action_kind": "increase_local_window",
            "status": "theorem_backed_dense_local_fallback",
            "coverage_scope": "all_positive_lags",
            "proposed_local_window": certificate.complete_repair_window,
            "additional_local_slots": (
                certificate.complete_repair_window_additional_local_slots
            ),
            "evidence_fields": [
                "complete_repair_window",
                "complete_repair_window_additional_local_slots",
                "complete_repair_window_covers_context",
                "complete_repair_window_uses_dense_threshold",
                "local_window_complete_threshold_is_exact_local_minimum",
                "complete_repair_window_minimal_for_declared_stride_family",
                "complete_repair_window_minimal_witness_lag",
            ],
            "theorem_ids": [
                "AIT-T0023",
                "AIT-T0034",
                "AIT-T0172",
                "AIT-T0168",
                "AIT-T0169",
                "AIT-T0170",
            ],
            "not_claimed": (
                "This is the dense-local correctness fallback for complete "
                "positive-lag coverage. In the default fixture it is also the "
                "minimal local-window repair for the declared path and stride "
                "family, but it is not a claim that dense local attention is "
                "efficient or architecturally preferable."
            ),
        },
        {
            "id": "SPARSE-INTERVAL-REPAIR-PATH",
            "action_kind": "increase_local_window_sequence",
            "status": "computed_from_certificate_gap_fields",
            "coverage_scope": "successive_first_uncovered_intervals",
            "step_count": certificate.interval_repair_plan_step_count,
            "final_local_window": certificate.interval_repair_plan_final_window,
            "covers_context_after_final_step": (
                certificate.interval_repair_plan_covers_context
            ),
            "strictly_progresses": (
                certificate.interval_repair_plan_strictly_progresses
            ),
            "evidence_fields": [
                "interval_repair_plan",
                "interval_repair_plan_step_count",
                "interval_repair_plan_final_window",
                "interval_repair_plan_covers_context",
                "interval_repair_plan_strictly_progresses",
                "uncovered_lag_intervals",
            ],
            "theorem_ids": ["AIT-T0094", "AIT-T0104", "AIT-T0171"],
            "not_claimed": (
                "This is a deterministic remediation trace over the reported "
                "finite gap intervals. It is not a search over all sparse "
                "layouts, not a minimal sparse-attention architecture, and not "
                "a performance recommendation."
            ),
        },
    ]
    return _with_consumer_check({
        "id": GENERIC_IDS["sparse_attention_coverage"],
        "kind": "sparse_attention_coverage",
        "status": "fixture",
        "source_paper": CONTRACT_ARTIFACTS["sparse_attention_coverage"]["source_paper"],
        "theorem_ids": list(_unique(certificate.theorem_ids + certificate.fixture_theorem_ids)),
        "dictionary_ids": ["COMMON-0028", "COMMON-0029", "COMMON-0047", "COMMON-0075", "COMMON-0079"],
        "fields": fields,
        "contract_passed": (
            certificate.covered_uncovered_count_partition
            and certificate.first_uncovered_lag_gap_witness
            and certificate.first_uncovered_lag_exceeds_local_window
            and certificate.first_uncovered_interval_repair_reaches_interval is True
            and certificate.first_interval_repair_next_uncovered_lag == 8
            and certificate.first_interval_repair_still_has_gap is True
            and certificate.first_interval_repair_covers_context is False
            and certificate.largest_uncovered_interval_start == 40
            and certificate.largest_uncovered_interval_stop == 119
            and certificate.largest_uncovered_interval_length == 80
            and certificate.largest_uncovered_interval_repair_window == 119
            and certificate.largest_uncovered_interval_additional_local_slots == 115
            and certificate.largest_uncovered_interval_repair_reaches_interval is True
            and certificate.largest_interval_repair_next_uncovered_lag is None
            and certificate.largest_interval_repair_still_has_gap is False
            and certificate.largest_interval_repair_covers_context is True
            and certificate.largest_uncovered_interval_is_tail is True
            and certificate.first_uncovered_lag_repair_window_reaches
            and certificate.first_uncovered_lag_repair_window_covers_context is False
            and certificate.first_gap_repair_window_is_final_positive_lag is False
            and certificate.first_gap_repair_threshold_matches_final_lag is True
            and (
                not certificate.local_window_reaches_complete_coverage_threshold
                or certificate.coverage_complete
            )
            and certificate.local_window_complete_threshold_is_exact_local_minimum
            and certificate.complete_repair_window_covers_context
            and certificate.complete_repair_window_uses_dense_threshold
            and certificate.complete_repair_window_minimal_for_declared_stride_family
            and certificate.complete_repair_window_minimal_witness_lag == 119
            and certificate.interval_repair_plan_step_count == 6
            and certificate.interval_repair_plan_final_window == 119
            and certificate.interval_repair_plan_covers_context
            and certificate.interval_repair_plan_strictly_progresses
            and certificate.first_gap_repair_window_reaches_complete_threshold is False
            and certificate.uncovered_count_positive_matches_gap_witness
            and certificate.raw_budget_shortfall_certifies_incomplete
            and certificate.unique_lag_count_shortfall_certifies_incomplete
            and certificate.lag_dedup_loss_zero_matches_no_collision
            and certificate.query_dedup_loss_zero_matches_no_collision
            and certificate.lag_dedup_loss_positive_matches_collision
            and certificate.query_dedup_loss_positive_matches_collision
            and certificate.lag_collision_pair_count_zero_matches_no_collision
            and certificate.query_collision_pair_count_zero_matches_no_collision
            and certificate.lag_collision_pair_count_positive_matches_collision
            and certificate.query_collision_pair_count_positive_matches_collision
            and certificate.lag_dedup_loss_accounting_matches_raw
            and certificate.query_dedup_loss_accounting_matches_raw
        ),
        "integration_use": GENERIC_USES["sparse_attention_coverage"],
        "ordinary_baselines": [
            "dense_attention",
            "local_window_only",
            "random_sparse_pattern",
            "unverified_stride_layout",
        ],
        "not_claimed": CLAIM_BOUNDARY,
        "compatibility_ids": [],
        "planner_recommendations": planner_recommendations,
        **_artifact_fields("sparse_attention_coverage"),
    })


def build_recurrence_schedule_contract(
    *,
    loop_period: int = 5,
    sample_index: int = 8,
    max_loops: int = 7,
    token_indices: Sequence[int] = (0, 1, 2, 3, 4, 5, 6, 7),
    selected_block_start: int = 2,
    selected_block_width: int = 3,
    periodic_shift_passes: int = 3,
) -> dict[str, Any]:
    """Return one generic public recurrence-schedule contract."""
    return _generic_contract(
        build_theseus_recurrence_contract(
            loop_period=loop_period,
            sample_index=sample_index,
            max_loops=max_loops,
            token_indices=token_indices,
            selected_block_start=selected_block_start,
            selected_block_width=selected_block_width,
            periodic_shift_passes=periodic_shift_passes,
        )
    )


def build_strided_candidate_fanout_contract(
    *,
    context_length: int = 12,
    stride: int = 5,
    start_index: int = 0,
    path_length: int = 12,
) -> dict[str, Any]:
    """Return one generic public strided candidate-fanout contract."""
    return _generic_contract(
        build_theseus_fanout_contract(
            context_length=context_length,
            stride=stride,
            start_index=start_index,
            path_length=path_length,
        )
    )


def build_seed_rule_contract(*, n: int = 128) -> dict[str, Any]:
    """Return one generic public seed-rule exact-regeneration contract."""
    return _generic_contract(build_theseus_seed_rule_contract(n=n))


def build_cyclic_memory_contract(
    *,
    bank_size: int = 8,
    event_index: int = 23,
    event_count: int = 32,
) -> dict[str, Any]:
    """Return one generic public cyclic memory residue/winding contract."""
    return _generic_contract(
        build_theseus_memory_contract(
            bank_size=bank_size,
            event_index=event_index,
            event_count=event_count,
        )
    )


def build_multicoil_phase_feature_contract(
    *,
    periods: Sequence[int] = (5, 7),
    position: int = 37,
    query_position: int = 41,
    key_position: int = 18,
) -> dict[str, Any]:
    """Return one generic public multicoil phase-feature contract."""
    return _generic_contract(
        build_theseus_phase_feature_contract(
            periods=periods,
            position=position,
            query_position=query_position,
            key_position=key_position,
        )
    )


def build_circulant_block_cyclic_mixer_contract(
    *,
    period: int = 8,
    channel_count: int = 128,
    block_size: int = 8,
) -> dict[str, Any]:
    """Return one generic public structured mixer/accounting contract."""
    return _generic_contract(
        build_theseus_mixer_contract(
            period=period,
            channel_count=channel_count,
            block_size=block_size,
        )
    )


def build_contract_pack() -> dict[str, Any]:
    """Return the standalone Circle AI contract pack."""
    compat = build_theseus_compat_pack()
    contracts = [
        _rope_position_contract(),
        _kv_cache_contract(),
        _sparse_attention_contract(),
        *(_generic_contract(contract) for contract in compat["contracts"]),
    ]
    _attach_contract_fingerprints(contracts)
    pack = {
        "schema_id": SCHEMA_ID,
        "status": "public_safe_fixture",
        "claim_boundary": CLAIM_BOUNDARY,
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "proof_indexes": _proof_index_fields(),
        "acceptance_policy": _acceptance_policy_fields(),
        "contract_schema": {
            "required_contract_keys": list(CONTRACT_REQUIRED_KEYS),
            "minimum_fields_by_kind": {
                kind: list(fields)
                for kind, fields in sorted(MINIMUM_FIELDS_BY_KIND.items())
            },
            "minimum_field_catalog_by_kind": _minimum_field_catalog(contracts),
            "consumer_check_keys": [
                "minimum_fields",
                "missing_minimum_fields",
                "required_fields_present",
                "all_theorem_ids_resolved",
                "all_theorem_ids_proved",
                "unresolved_theorem_ids",
                "unproved_theorem_ids",
                "ready_for_downstream_fixture_use",
                "rule",
            ],
            "planner_recommendation_keys": list(PLANNER_RECOMMENDATION_KEYS),
        },
        "validation_commands": PACK_VALIDATION_COMMANDS,
        "source_docs": [
            "docs/AI_CONTRACT_SUITE.md",
            "docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md",
            "papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md",
            "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
            "papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md",
            "papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md",
            "papers/generative/PAPER_GEN_01_SEED_RULE_PROVENANCE.md",
        ],
        "downstream_compatibility": {
            "theseus_hive": {
                "schema_id": compat["schema_id"],
                "export_path": "site/data/generated/theseus_hive_ai_contracts.json",
                "policy": "compatibility alias only; Circle remains the public source of contract facts",
            }
        },
        "contract_readiness_index": _readiness_index(contracts),
        "planner_recommendation_index": _planner_recommendation_index(contracts),
        "contract_fingerprint_index": _contract_fingerprint_index(contracts),
        "contracts": contracts,
    }
    pack["pack_content_fingerprint"] = _json_fingerprint(pack)
    return pack
