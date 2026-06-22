"""Parameterized Circle AI contract receipts.

The generated contract pack is the fixture/audit artifact. This module is the
runtime-facing layer: a downstream project supplies parameters, and receives a
small theorem-linked receipt with explicit proof boundaries.
"""

from __future__ import annotations

import hashlib
import json
import shlex
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import jsonschema

from .circle_ai import (
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_batch,
    certify_kv_cache_live_window,
    certify_kv_cache_live_window_request,
    certify_kv_cache_sink_window,
    certify_kv_cache_window,
    certify_stride_family_coverage,
)
from .circle_ai_contract_consumer import (
    FINGERPRINT_ALGORITHM,
    contract_recommendations,
    find_contract,
    readiness_summary,
    require_ready_contract,
    validate_consumer_pack,
)
from .circle_ai_contracts import (
    SCHEMA_ID as CONTRACT_PACK_SCHEMA_ID,
    build_circulant_block_cyclic_mixer_contract,
    build_contract_pack,
    build_cyclic_memory_contract,
    build_multicoil_phase_feature_contract,
    build_recurrence_schedule_contract,
    build_seed_rule_contract,
    build_strided_candidate_fanout_contract,
)
from .rope_certifier import (
    RoPEConfig,
    certify_rope_positions,
    certify_standard_channel0_d19_bank_request,
    certify_standard_channel0_d19_range_request_margin_bracket,
)


REQUEST_SCHEMA_ID = "circle_calculus.ai_contract_request.v0"
RECEIPT_SCHEMA_ID = "circle_calculus.ai_contract_receipt.v0"
COMPACT_RECEIPT_SCHEMA_ID = "circle_calculus.ai_contract_compact_receipt.v0"
REQUEST_VALIDATION_SCHEMA_ID = "circle_calculus.ai_contract_request_validation.v0"
ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID = (
    "circle_calculus.rope_model_config_import.v0"
)
ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID = (
    "circle_calculus.ai_architecture_config_import.v0"
)
RUNNER_CHECK_SCHEMA_ID = "circle_calculus.ai_contract_runner_check.v0"
RECEIPT_FILE_CHECK_SCHEMA_ID = "circle_calculus.ai_contract_receipt_file_check.v0"
RECEIPT_REPLAY_CHECK_SCHEMA_ID = (
    "circle_calculus.ai_contract_receipt_replay_check.v0"
)
CERTIFICATION_BUNDLE_SCHEMA_ID = (
    "circle_calculus.ai_contract_certification_bundle.v0"
)
CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID = (
    "circle_calculus.ai_contract_certification_bundle_file_check.v0"
)
ARTIFACT_MANIFEST_SCHEMA_ID = (
    "circle_calculus.ai_contract_artifact_manifest.v0"
)
ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_ID = (
    "circle_calculus.ai_contract_artifact_manifest_file_check.v0"
)
REQUEST_SCHEMA_PATH = "site/data/generated/circle_ai_contract_request.schema.json"
REQUEST_VALIDATION_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_request_validation.schema.json"
)
ROPE_MODEL_CONFIG_IMPORT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_rope_model_config_import.schema.json"
)
ARCHITECTURE_CONFIG_IMPORT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_architecture_config_import.schema.json"
)
RECEIPT_SCHEMA_PATH = "site/data/generated/circle_ai_contract_receipt.schema.json"
COMPACT_RECEIPT_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_compact_receipt.schema.json"
)
RUNNER_CHECK_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_runner_check.schema.json"
)
RECEIPT_FILE_CHECK_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_receipt_file_check.schema.json"
)
RECEIPT_REPLAY_CHECK_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_receipt_replay_check.schema.json"
)
CERTIFICATION_BUNDLE_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_certification_bundle.schema.json"
)
CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_PATH = (
    "site/data/generated/"
    "circle_ai_contract_certification_bundle_file_check.schema.json"
)
ARTIFACT_MANIFEST_SCHEMA_PATH = (
    "site/data/generated/circle_ai_contract_artifact_manifest.schema.json"
)
ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_PATH = (
    "site/data/generated/"
    "circle_ai_contract_artifact_manifest_file_check.schema.json"
)

SUPPORTED_CONTRACT_KINDS = (
    "rope_position_distinguishability",
    "kv_cache_ring_buffer",
    "sparse_attention_coverage",
    "recurrence_schedule",
    "strided_candidate_fanout",
    "cyclic_memory_residue_winding",
    "multicoil_phase_feature",
    "circulant_block_cyclic_mixer",
    "seed_rule_exact_regeneration",
)
KIND_ALIASES = {
    "rope": "rope_position_distinguishability",
    "rope_position_distinguishability": "rope_position_distinguishability",
    "kv": "kv_cache_ring_buffer",
    "kv-cache": "kv_cache_ring_buffer",
    "kv_cache": "kv_cache_ring_buffer",
    "kv_cache_ring_buffer": "kv_cache_ring_buffer",
    "sparse": "sparse_attention_coverage",
    "sparse-attention": "sparse_attention_coverage",
    "sparse_attention": "sparse_attention_coverage",
    "sparse_attention_coverage": "sparse_attention_coverage",
    "recurrence": "recurrence_schedule",
    "recurrence-schedule": "recurrence_schedule",
    "recurrence_schedule": "recurrence_schedule",
    "fanout": "strided_candidate_fanout",
    "strided-fanout": "strided_candidate_fanout",
    "strided_candidate_fanout": "strided_candidate_fanout",
    "memory": "cyclic_memory_residue_winding",
    "cyclic-memory": "cyclic_memory_residue_winding",
    "cyclic_memory": "cyclic_memory_residue_winding",
    "cyclic_memory_residue_winding": "cyclic_memory_residue_winding",
    "phase-feature": "multicoil_phase_feature",
    "multicoil-phase": "multicoil_phase_feature",
    "multicoil_phase_feature": "multicoil_phase_feature",
    "mixer": "circulant_block_cyclic_mixer",
    "cyclic-mixer": "circulant_block_cyclic_mixer",
    "circulant-mixer": "circulant_block_cyclic_mixer",
    "circulant_block_cyclic_mixer": "circulant_block_cyclic_mixer",
    "seed-rule": "seed_rule_exact_regeneration",
    "seed_rule": "seed_rule_exact_regeneration",
    "seed_rule_exact_regeneration": "seed_rule_exact_regeneration",
}
CONTRACT_KIND_CLI_SUBCOMMANDS = {
    "rope_position_distinguishability": "rope",
    "kv_cache_ring_buffer": "kv-cache",
    "sparse_attention_coverage": "sparse-attention",
    "recurrence_schedule": "recurrence",
    "strided_candidate_fanout": "strided-fanout",
    "cyclic_memory_residue_winding": "cyclic-memory",
    "multicoil_phase_feature": "multicoil-phase",
    "circulant_block_cyclic_mixer": "cyclic-mixer",
    "seed_rule_exact_regeneration": "seed-rule",
}
STATUS_VALUES = (
    "proved",
    "impossible",
    "undecided",
    "numerical_only",
    "outside_scope",
)
PROOF_LAYER_BUCKETS = (
    "proved_fields",
    "computed_fields",
    "numerical_only_fields",
    "unsupported_fields",
)
PROOF_LAYER_LABEL_BY_BUCKET = {
    "proved_fields": "proved",
    "computed_fields": "computed",
    "numerical_only_fields": "numerical_only",
    "unsupported_fields": "unsupported",
}
COMPACT_EVIDENCE_PROOF_LAYER_LABELS = (
    "proved",
    "computed",
    "numerical_only",
    "unsupported",
    "mixed",
    "unclassified",
)
DECISION_VERDICTS = (
    "passed",
    "failed",
    "undecided",
    "numerical_only",
    "outside_scope",
)
DECISION_ASSURANCE_LEVELS = (
    "theorem_backed",
    "mixed_theorem_and_computation",
    "numerical_only",
    "unsupported",
    "undecided",
)
RECEIPT_TOP_LEVEL_KEYS = {
    "schema_id",
    "request_schema_id",
    "contract_pack_schema_id",
    "kind",
    "contract_id",
    "status",
    "request_passed",
    "decision",
    "request",
    "request_content_fingerprint",
    "normalized_request",
    "normalized_request_fingerprint",
    "evidence",
    "proof_status",
    "proof_layers",
    "recommendations",
    "validation_commands",
    "support",
    "not_claimed",
    "content_fingerprint_algorithm",
    "receipt_content_fingerprint",
}
COMPACT_RECEIPT_EVIDENCE_PATHS_BY_KIND = {
    "rope_position_distinguishability": (
        "exact_discrete_pass",
        "exact_total_bank_collision_pair_count",
        "exact_common_collision_gap",
        "real_phase_numerical_pass_margin",
        "real_phase_numerical_worst_gap",
        "real_phase_numerical_worst_margin_radians",
        "standard_channel0_d19_request_classifier.request_status",
        "standard_channel0_d19_request_classifier.theorem_backed_classification",
        "standard_channel0_d19_request_classifier.requested_margin",
        "standard_channel0_d19_request_classifier.requested_context",
        "standard_channel0_d19_bank_bridge.applies",
        "standard_channel0_d19_bank_bridge.request_status",
        "standard_channel0_d19_bank_bridge.theorem_backed",
        "standard_channel0_d19_bank_bridge.bank_shape",
        "real_phase_dirichlet_guardrail.applies",
        "real_phase_dirichlet_guardrail.requested_margin_relation_to_ceiling",
        "real_phase_dirichlet_guardrail.requested_margin_exceeds_ceiling",
    ),
    "kv_cache_ring_buffer": (
        "window_certificate.retained",
        "window_certificate.slot",
        "window_certificate.lag",
        "window_certificate.next_overwrite_token",
        "adapter_request_trace_certificate.pass_certificate",
        "adapter_request_trace_certificate.stale_requested_count",
        "adapter_request_trace_certificate.first_stale_token",
        "live_window_certificate.full_coverage_contract",
        "live_window_certificate.start",
        "live_window_certificate.length",
        "sink_window_certificate.token_count",
        "sink_window_certificate.token_count_bound",
    ),
    "sparse_attention_coverage": (
        "coverage_complete",
        "covered_lag_count",
        "uncovered_lag_count",
        "first_uncovered_lag",
        "complete_repair_window",
        "complete_repair_window_covers_context",
        "complete_repair_window_minimal_for_declared_stride_family",
        "uncovered_lag_interval_count",
        "largest_uncovered_interval_length",
        "theorem_side_lag_candidates_no_collision",
        "theorem_side_lag_candidate_dedup_loss",
        "theorem_side_lag_candidate_collision_pair_count",
        "lag_collision_pair_count_bounds_dedup_loss",
        "lag_dedup_loss_accounting_matches_raw",
        "theorem_side_query_candidates_no_collision",
        "theorem_side_query_candidate_dedup_loss",
        "theorem_side_query_candidate_collision_pair_count",
        "query_collision_pair_count_bounds_dedup_loss",
        "query_dedup_loss_accounting_matches_raw",
    ),
    "recurrence_schedule": (
        "fields.loop_period",
        "fields.sample_index",
        "fields.exit_step",
        "fields.total_active_token_work",
        "fields.total_inactive_token_work",
        "fields.scheduled_work_saving",
        "fields.post_period_multi_extension_horizon_steps",
    ),
    "strided_candidate_fanout": (
        "fields.context_length",
        "fields.stride",
        "fields.gcd",
        "fields.predicted_reach",
        "fields.full_coverage",
        "fields.candidate_budget",
        "fields.effective_candidate_budget",
        "fields.duplicate_count",
        "fields.candidate_budget_shortfall",
    ),
    "cyclic_memory_residue_winding": (
        "fields.bank_size",
        "fields.event_index",
        "fields.residue_slot",
        "fields.winding",
        "fields.same_residue_events",
        "fields.same_residue_windings",
        "fields.max_alias_load",
    ),
    "multicoil_phase_feature": (
        "fields.periods",
        "fields.position",
        "fields.phase_tuple",
        "fields.joint_repeat_horizon",
        "fields.query_position",
        "fields.key_position",
        "fields.relative_period",
        "fields.relative_phase",
        "fields.shifted_relative_phase",
    ),
    "circulant_block_cyclic_mixer": (
        "fields.period",
        "fields.channel_count",
        "fields.block_size",
        "fields.max_abs_dense_delta",
        "fields.circulant_parameters",
        "fields.dense_parameters",
        "fields.block_cyclic_parameters",
        "fields.block_to_dense_ratio",
    ),
    "seed_rule_exact_regeneration": (
        "fields.artifact_id",
        "fields.fixture_n",
        "fields.exact_regeneration",
        "fields.generator_shorter",
        "fields.explicit_length",
        "fields.generator_length",
        "fields.storage_saving",
        "fields.storage_saving_positive",
    ),
}
ROPE_DIRICHLET_GUARDRAIL_THEOREM_IDS = (
    "AIRA-T0239",
    "AIRA-T0240",
    "AIRA-T0241",
)
ROPE_MODEL_BASE_KEYS = (
    "rope_theta",
    "rope_base",
    "rotary_emb_base",
    "rotary_base",
    "rotary_theta",
)
ROPE_MODEL_CONTEXT_KEYS = (
    "max_position_embeddings",
    "max_seq_len",
    "max_seq_length",
    "max_sequence_length",
    "model_max_length",
    "seq_len",
    "context_length",
    "seq_length",
    "n_positions",
)
ROPE_MODEL_HEAD_DIM_KEYS = ("head_dim", "attention_head_dim")
ROPE_MODEL_ROTARY_DIM_KEYS = (
    "rotary_dim",
    "rotary_emb_dim",
    "rotary_ndims",
    "qk_rope_head_dim",
    "rope_head_dim",
)
ROPE_MODEL_ROTARY_FRACTION_KEYS = ("partial_rotary_factor", "rotary_pct")
ARCHITECTURE_CONFIG_SUPPORTED_KINDS = (
    "kv_cache_ring_buffer",
    "sparse_attention_coverage",
    "recurrence_schedule",
)
ARCHITECTURE_CONFIG_SECTION_KEYS = {
    "kv_cache_ring_buffer": (
        "kv_cache",
        "kv-cache",
        "kv_cache_ring_buffer",
        "cache",
        "attention_cache",
    ),
    "sparse_attention_coverage": (
        "sparse_attention",
        "sparse-attention",
        "sparse_attention_coverage",
        "attention",
        "sparse",
    ),
    "recurrence_schedule": (
        "recurrence",
        "recurrence_schedule",
        "looped_recurrence",
        "recursive_transformer",
        "loop",
    ),
}
ARCHITECTURE_CONFIG_PARAMETER_ALIASES = {
    "kv_cache_ring_buffer": {
        "cache_size": (
            "cache_size",
            "kv_cache_size",
            "kv_cache_length",
            "window_size",
            "sliding_window",
        ),
        "current": (
            "current",
            "current_token",
            "current_position",
            "sequence_position",
            "position",
        ),
        "token": (
            "token",
            "requested_token",
            "read_token",
            "token_index",
        ),
        "batch_tokens": (
            "batch_tokens",
            "requested_tokens",
            "tokens",
            "read_tokens",
        ),
        "sink_size": (
            "sink_size",
            "num_sink_tokens",
            "attention_sink_size",
            "sink_tokens",
        ),
        "request_id": ("request_id", "id", "name"),
    },
    "sparse_attention_coverage": {
        "context": (
            "context",
            "context_length",
            "sequence_length",
            "seq_len",
            "max_position_embeddings",
        ),
        "strides": (
            "strides",
            "attention_strides",
            "sparse_attention_strides",
            "dilation_strides",
        ),
        "path_length": (
            "path_length",
            "attention_path_length",
            "sparse_path_length",
            "max_hops",
        ),
        "local_window": (
            "local_window",
            "window",
            "window_size",
            "sliding_window",
        ),
    },
    "recurrence_schedule": {
        "loop_period": (
            "loop_period",
            "recurrence_period",
            "ponder_period",
            "period",
        ),
        "sample_index": (
            "sample_index",
            "sample_step",
            "position",
            "token_index",
        ),
        "max_loops": (
            "max_loops",
            "max_recurrence_steps",
            "recurrence_steps",
            "num_iterations",
            "iterations",
        ),
        "token_count": (
            "token_count",
            "sequence_length",
            "context_length",
            "seq_len",
        ),
        "selected_block_start": (
            "selected_block_start",
            "block_start",
            "middle_block_start",
        ),
        "selected_block_width": (
            "selected_block_width",
            "block_width",
            "middle_block_width",
        ),
        "shift_passes": (
            "shift_passes",
            "periodic_shift_passes",
            "shift_periods",
        ),
    },
}
ARCHITECTURE_CONFIG_OPTIONAL_PARAMETERS = {
    "kv_cache_ring_buffer": {"batch_tokens", "sink_size", "request_id"},
    "sparse_attention_coverage": set(),
    "recurrence_schedule": {
        "loop_period",
        "sample_index",
        "max_loops",
        "token_count",
        "selected_block_start",
        "selected_block_width",
        "shift_passes",
    },
}
ARCHITECTURE_CONFIG_PARAMETER_DEFAULTS: dict[str, dict[str, Any]] = {
    "kv_cache_ring_buffer": {
        "batch_tokens": [],
        "sink_size": 0,
        "request_id": "read_request",
    },
    "sparse_attention_coverage": {},
    "recurrence_schedule": {
        "loop_period": 5,
        "sample_index": 8,
        "max_loops": 7,
        "token_count": 8,
        "selected_block_start": 2,
        "selected_block_width": 3,
        "shift_passes": 3,
    },
}
_ARCHITECTURE_CONFIG_DEFAULT_MISSING = object()


def canonical_contract_kind(kind: str) -> str:
    """Return the canonical contract kind, accepting CLI-friendly aliases."""

    canonical = KIND_ALIASES.get(kind)
    if canonical is None:
        supported = ", ".join(sorted(KIND_ALIASES))
        raise ValueError(f"unsupported contract kind {kind!r}; expected one of {supported}")
    return canonical


def parse_fraction(value: str | Fraction | None) -> Fraction | None:
    """Parse a human margin like ``1/328459`` or ``0.001`` into a Fraction."""

    if value is None or isinstance(value, Fraction):
        return value
    text = str(value).strip()
    if not text:
        raise ValueError("fraction value must be non-empty")
    return Fraction(text)


def _model_config_value(config: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in config:
            return config[key]
    return None


def _model_config_key(config: Mapping[str, Any], keys: Sequence[str]) -> str | None:
    for key in keys:
        if key in config:
            return key
    return None


def _positive_int_value(value: Any, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"model config {field} must be a positive integer")
    return value


def _even_rope_head_dim_value(value: Any, *, field: str) -> int:
    head_dim = _positive_int_value(value, field=field)
    if head_dim % 2 != 0:
        raise ValueError(
            f"model config {field} must be even because RoPE uses dimension pairs"
        )
    return head_dim


def _positive_float_value(value: Any, *, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"model config {field} must be a positive number")
    return float(value)


def _nonnegative_float_value(value: Any, *, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ValueError(f"model config {field} must be a nonnegative number")
    return float(value)


def _optional_rotary_fraction(config: Mapping[str, Any]) -> Fraction | None:
    value = _model_config_value(config, ROPE_MODEL_ROTARY_FRACTION_KEYS)
    if value is None:
        return None
    if not isinstance(value, (int, float, str)) or isinstance(value, bool):
        raise ValueError("model config rotary fraction must be a positive number")
    try:
        fraction = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(
            "model config rotary fraction must parse as a positive number"
        ) from exc
    if fraction <= 0:
        raise ValueError("model config rotary fraction must be positive")
    return fraction


def _ensure_standard_rope_scaling(config: Mapping[str, Any]) -> None:
    rope_scaling = config.get("rope_scaling")
    if rope_scaling in (None, False):
        return
    if isinstance(rope_scaling, Mapping):
        rope_type = rope_scaling.get("rope_type", rope_scaling.get("type"))
        if rope_type in (None, "default", "none"):
            return
    raise ValueError(
        "model config rope_scaling is outside the standard-RoPE importer; "
        "use an explicit Circle request only for the simplified parameters "
        "you intend to certify"
    )


def _infer_rope_head_dim(config: Mapping[str, Any]) -> int:
    direct_rope_dim = _model_config_value(config, ROPE_MODEL_ROTARY_DIM_KEYS)
    if direct_rope_dim is not None:
        return _even_rope_head_dim_value(direct_rope_dim, field="rotary_dim")

    direct = _model_config_value(config, ROPE_MODEL_HEAD_DIM_KEYS)
    if direct is not None:
        head_dim = _even_rope_head_dim_value(direct, field="head_dim")
    else:
        hidden_size = _positive_int_value(
            config.get("hidden_size"),
            field="hidden_size",
        )
        num_heads = _positive_int_value(
            config.get("num_attention_heads"),
            field="num_attention_heads",
        )
        if hidden_size % num_heads != 0:
            raise ValueError(
                "model config hidden_size must be divisible by num_attention_heads"
            )
        head_dim = hidden_size // num_heads

    fraction = _optional_rotary_fraction(config)
    if fraction is None:
        return _even_rope_head_dim_value(head_dim, field="head_dim")
    numerator = head_dim * fraction.numerator
    if numerator % fraction.denominator != 0:
        raise ValueError(
            "model config rotary fraction must produce an integer RoPE head_dim"
        )
    rotary_dim = numerator // fraction.denominator
    if rotary_dim <= 0:
        raise ValueError("model config rotary fraction produced a nonpositive head_dim")
    if rotary_dim % 2 != 0:
        raise ValueError(
            "model config rotary fraction must produce an even RoPE head_dim"
        )
    return rotary_dim


def build_rope_request_parameters_from_model_config(
    config: Mapping[str, Any],
    *,
    head_dim: int | None = None,
    base: float | None = None,
    context: int | None = None,
    tolerance: float | None = None,
    discretization: str | None = None,
    requested_margin: str | Fraction | None = None,
) -> dict[str, Any]:
    """Build standard-RoPE runner parameters from a model config object.

    The importer covers the common standard-RoPE fields used by model
    ``config.json`` files. Non-default ``rope_scaling`` metadata is rejected
    because the current runner receipts do not prove scaled-RoPE semantics.
    """

    if not isinstance(config, Mapping):
        raise ValueError("model config must be a JSON object")
    _ensure_standard_rope_scaling(config)

    resolved_head_dim = (
        _even_rope_head_dim_value(head_dim, field="head_dim")
        if head_dim is not None
        else _infer_rope_head_dim(config)
    )
    base_value = (
        base if base is not None else _model_config_value(config, ROPE_MODEL_BASE_KEYS)
    )
    resolved_base = 10000.0 if base_value is None else _positive_float_value(
        base_value,
        field="base",
    )
    context_value = (
        context
        if context is not None
        else _model_config_value(config, ROPE_MODEL_CONTEXT_KEYS)
    )
    resolved_context = _positive_int_value(context_value, field="context")
    resolved_tolerance = 1e-6 if tolerance is None else _nonnegative_float_value(
        tolerance,
        field="tolerance",
    )
    resolved_discretization = "round" if discretization is None else discretization

    parameters: dict[str, Any] = {
        "head_dim": resolved_head_dim,
        "base": resolved_base,
        "context": resolved_context,
        "tolerance": resolved_tolerance,
        "discretization": resolved_discretization,
        "requested_margin": None,
    }
    if requested_margin is not None:
        parameters["requested_margin"] = str(requested_margin)
    return parameters


def _rope_model_config_parameter_sources(
    config: Mapping[str, Any],
    *,
    head_dim: int | None,
    base: float | None,
    context: int | None,
    tolerance: float | None,
    discretization: str | None,
    requested_margin: str | Fraction | None,
) -> dict[str, dict[str, Any]]:
    """Describe where each standard-RoPE request parameter came from."""

    head_dim_key = _model_config_key(config, ROPE_MODEL_HEAD_DIM_KEYS)
    rotary_dim_key = _model_config_key(config, ROPE_MODEL_ROTARY_DIM_KEYS)
    rotary_fraction_key = _model_config_key(config, ROPE_MODEL_ROTARY_FRACTION_KEYS)
    base_key = _model_config_key(config, ROPE_MODEL_BASE_KEYS)
    context_key = _model_config_key(config, ROPE_MODEL_CONTEXT_KEYS)

    if head_dim is not None:
        head_dim_source = {
            "source": "override",
            "field": "head_dim",
        }
    elif rotary_dim_key is not None:
        note = "explicit RoPE rotary dimension"
        if rotary_fraction_key is not None:
            note = (
                "explicit RoPE rotary dimension; rotary fraction was not "
                "reapplied"
            )
        head_dim_source = {
            "source": "config_field",
            "field": rotary_dim_key,
            "note": note,
        }
    elif head_dim_key is not None:
        if rotary_fraction_key is None:
            head_dim_source = {
                "source": "config_field",
                "field": head_dim_key,
            }
        else:
            head_dim_source = {
                "source": "derived_config_fields",
                "fields": [head_dim_key, rotary_fraction_key],
                "note": "head_dim adjusted by rotary fraction",
            }
    else:
        fields = ["hidden_size", "num_attention_heads"]
        if rotary_fraction_key is not None:
            fields.append(rotary_fraction_key)
        head_dim_source = {
            "source": "derived_config_fields",
            "fields": fields,
            "note": "hidden_size / num_attention_heads, adjusted by rotary fraction when present",
        }

    return {
        "head_dim": head_dim_source,
        "base": (
            {"source": "override", "field": "base"}
            if base is not None
            else (
                {"source": "config_field", "field": base_key}
                if base_key is not None
                else {"source": "default", "note": "10000.0"}
            )
        ),
        "context": (
            {"source": "override", "field": "context"}
            if context is not None
            else (
                {"source": "config_field", "field": context_key}
                if context_key is not None
                else {"source": "missing"}
            )
        ),
        "tolerance": (
            {"source": "override", "field": "tolerance"}
            if tolerance is not None
            else {"source": "default", "note": "1e-6"}
        ),
        "discretization": (
            {"source": "override", "field": "discretization"}
            if discretization is not None
            else {"source": "default", "note": "round"}
        ),
        "requested_margin": (
            {"source": "override", "field": "requested_margin"}
            if requested_margin is not None
            else {"source": "omitted"}
        ),
    }


def _strip_fingerprint_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_fingerprint_fields(child)
            for key, child in value.items()
            if key != "receipt_content_fingerprint"
        }
    if isinstance(value, list):
        return [_strip_fingerprint_fields(child) for child in value]
    if isinstance(value, tuple):
        return [_strip_fingerprint_fields(child) for child in value]
    return value


def _json_ready_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _json_ready_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready_value(child) for child in value]
    return value


def _json_fingerprint(value: Any) -> str:
    payload = json.dumps(
        _strip_fingerprint_fields(value),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _architecture_config_sections(
    canonical: str,
    config: Mapping[str, Any],
) -> tuple[tuple[str | None, Mapping[str, Any]], ...]:
    sections: list[tuple[str | None, Mapping[str, Any]]] = []
    for key in ARCHITECTURE_CONFIG_SECTION_KEYS.get(canonical, ()):
        value = config.get(key)
        if isinstance(value, Mapping):
            sections.append((key, value))
    sections.append((None, config))
    return tuple(sections)


def _architecture_config_lookup(
    canonical: str,
    config: Mapping[str, Any],
    parameter: str,
) -> tuple[Any, str] | None:
    aliases = ARCHITECTURE_CONFIG_PARAMETER_ALIASES[canonical][parameter]
    for section_key, section in _architecture_config_sections(canonical, config):
        for alias in aliases:
            if alias in section:
                field = alias if section_key is None else f"{section_key}.{alias}"
                return section[alias], field
    return None


def _architecture_parameter_source(
    *,
    source: str,
    field: str | None = None,
    value: Any = None,
    note: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"source": source}
    if field is not None:
        payload["field"] = field
    if source != "missing":
        payload["value"] = _json_ready_value(value)
    if note is not None:
        payload["note"] = note
    return payload


def _unique_strings(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def _cli_value(value: Any) -> str:
    return shlex.quote(str(value))


def _cli_csv(values: Sequence[Any]) -> str:
    return ",".join(str(value) for value in values)


def _runner_validation_command_for_request(request: Mapping[str, Any]) -> str:
    kind = canonical_contract_kind(str(request["kind"]))
    parameters = request["parameters"]
    if not isinstance(parameters, Mapping):
        raise ValueError("request.parameters must be an object")
    parts = [
        "python",
        "scripts/circle_ai_certify.py",
        CONTRACT_KIND_CLI_SUBCOMMANDS[kind],
    ]
    if kind == "rope_position_distinguishability":
        for flag, key in (
            ("--head-dim", "head_dim"),
            ("--base", "base"),
            ("--context", "context"),
            ("--tolerance", "tolerance"),
            ("--discretization", "discretization"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
        if parameters.get("requested_margin") is not None:
            parts.extend(
                ["--requested-margin", _cli_value(parameters["requested_margin"])]
            )
    elif kind == "kv_cache_ring_buffer":
        for flag, key in (
            ("--cache-size", "cache_size"),
            ("--current", "current"),
            ("--token", "token"),
        ):
            parts.extend([flag, _cli_value(parameters[key])])
        batch_tokens = parameters.get("batch_tokens", [])
        if batch_tokens:
            parts.extend(["--batch-tokens", _cli_value(_cli_csv(batch_tokens))])
        if "sink_size" in parameters:
            parts.extend(["--sink-size", _cli_value(parameters["sink_size"])])
        if parameters.get("request_id") != "read_request":
            parts.extend(["--request-id", _cli_value(parameters["request_id"])])
    elif kind == "sparse_attention_coverage":
        parts.extend(["--context", _cli_value(parameters["context"])])
        parts.extend(["--strides", _cli_value(_cli_csv(parameters["strides"]))])
        parts.extend(["--path-length", _cli_value(parameters["path_length"])])
        parts.extend(["--local-window", _cli_value(parameters["local_window"])])
    elif kind == "recurrence_schedule":
        for flag, key in (
            ("--loop-period", "loop_period"),
            ("--sample-index", "sample_index"),
            ("--max-loops", "max_loops"),
            ("--token-count", "token_count"),
            ("--selected-block-start", "selected_block_start"),
            ("--selected-block-width", "selected_block_width"),
            ("--shift-passes", "shift_passes"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
    elif kind == "strided_candidate_fanout":
        for flag, key in (
            ("--context-length", "context_length"),
            ("--stride", "stride"),
            ("--start-index", "start_index"),
            ("--path-length", "path_length"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
    elif kind == "cyclic_memory_residue_winding":
        for flag, key in (
            ("--bank-size", "bank_size"),
            ("--event-index", "event_index"),
            ("--event-count", "event_count"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
    elif kind == "multicoil_phase_feature":
        if "periods" in parameters:
            parts.extend(["--periods", _cli_value(_cli_csv(parameters["periods"]))])
        for flag, key in (
            ("--position", "position"),
            ("--query-position", "query_position"),
            ("--key-position", "key_position"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
    elif kind == "circulant_block_cyclic_mixer":
        for flag, key in (
            ("--period", "period"),
            ("--channel-count", "channel_count"),
            ("--block-size", "block_size"),
        ):
            if key in parameters:
                parts.extend([flag, _cli_value(parameters[key])])
    elif kind == "seed_rule_exact_regeneration":
        if "n" in parameters:
            parts.extend(["--n", _cli_value(parameters["n"])])
    parts.extend(["--format", "json"])
    return " ".join(parts)


def _as_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _duplicate_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    duplicates_seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        if value in seen and value not in duplicates_seen:
            duplicates.append(value)
            duplicates_seen.add(value)
        seen.add(value)
    return duplicates


def build_contract_request(kind: str, parameters: Mapping[str, Any]) -> dict[str, Any]:
    """Build and validate a versioned public runner request object."""

    canonical = canonical_contract_kind(kind)
    request = {
        "schema_id": REQUEST_SCHEMA_ID,
        "kind": canonical,
        "parameters": _json_ready_value(dict(parameters)),
    }
    failures = validate_contract_request(request)
    if failures:
        raise ValueError("invalid Circle AI contract request: " + "; ".join(failures))
    return request


def build_rope_contract_request_from_model_config(
    config: Mapping[str, Any],
    *,
    head_dim: int | None = None,
    base: float | None = None,
    context: int | None = None,
    tolerance: float | None = None,
    discretization: str | None = None,
    requested_margin: str | Fraction | None = None,
) -> dict[str, Any]:
    """Build a versioned standard-RoPE request from a model config object."""

    parameters = build_rope_request_parameters_from_model_config(
        config,
        head_dim=head_dim,
        base=base,
        context=context,
        tolerance=tolerance,
        discretization=discretization,
        requested_margin=requested_margin,
    )
    return build_contract_request("rope", parameters)


def _unsupported_rope_model_config_fields(config: Any) -> list[str]:
    if not isinstance(config, Mapping):
        return []
    fields: list[str] = []
    rope_scaling = config.get("rope_scaling")
    if rope_scaling not in (None, False):
        if isinstance(rope_scaling, Mapping):
            rope_type = rope_scaling.get("rope_type", rope_scaling.get("type"))
            if rope_type in (None, "default", "none"):
                return fields
        fields.append("rope_scaling")
    return fields


def build_rope_model_config_import_report(
    config: Mapping[str, Any],
    *,
    head_dim: int | None = None,
    base: float | None = None,
    context: int | None = None,
    tolerance: float | None = None,
    discretization: str | None = None,
    requested_margin: str | Fraction | None = None,
) -> dict[str, Any]:
    """Return a machine-readable standard-RoPE import report for a config."""

    request: dict[str, Any] | None = None
    failures: list[str] = []
    try:
        request = build_rope_contract_request_from_model_config(
            config,
            head_dim=head_dim,
            base=base,
            context=context,
            tolerance=tolerance,
            discretization=discretization,
            requested_margin=requested_margin,
        )
    except ValueError as exc:
        failures.append(str(exc))
    request_fingerprint = _json_fingerprint(request) if request is not None else None
    return {
        "schema_id": ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "model_config_fingerprint": _json_fingerprint(_json_ready_value(config)),
        "request_content_fingerprint": request_fingerprint,
        "kind": "rope_position_distinguishability",
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "unsupported_model_config_fields": _unsupported_rope_model_config_fields(
            config
        ),
        "parameter_sources": _rope_model_config_parameter_sources(
            config,
            head_dim=head_dim,
            base=base,
            context=context,
            tolerance=tolerance,
            discretization=discretization,
            requested_margin=requested_margin,
        ),
        "request": request,
        "notes": [
            "This report only covers conversion to Circle's standard-RoPE request frontier.",
            "A successful import is not a proof; the emitted request still needs a receipt.",
            "Unsupported model-config features must not be silently certified as standard RoPE.",
        ],
    }


def build_contract_request_from_architecture_config(
    kind: str,
    config: Mapping[str, Any],
    *,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a versioned request from a small AI architecture config object.

    This adapter covers the finite structural contracts that have explicit
    parameter aliases: KV-cache, sparse-attention coverage, and recurrence
    schedules. RoPE keeps its more specific model-config importer because real
    rotary configs need separate proof-boundary checks.
    """

    report = build_architecture_config_import_report(
        kind,
        config,
        overrides=overrides,
    )
    if not report["ok"]:
        raise ValueError(
            "invalid Circle AI architecture config import: "
            + "; ".join(report["failures"])
        )
    request = report["request"]
    assert isinstance(request, dict)
    return request


def build_architecture_config_import_report(
    kind: str,
    config: Mapping[str, Any],
    *,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a source-tracked config import report for non-RoPE AI contracts."""

    failures: list[str] = []
    request: dict[str, Any] | None = None
    parameters: dict[str, Any] = {}
    parameter_sources: dict[str, Any] = {}
    try:
        canonical = canonical_contract_kind(kind)
    except ValueError as exc:
        canonical = None
        failures.append(str(exc))

    if canonical is not None and canonical not in ARCHITECTURE_CONFIG_SUPPORTED_KINDS:
        failures.append(
            "architecture config import currently supports "
            + ", ".join(ARCHITECTURE_CONFIG_SUPPORTED_KINDS)
        )

    normalized_overrides = {
        key: value
        for key, value in (dict(overrides or {})).items()
        if value is not None
    }

    if canonical in ARCHITECTURE_CONFIG_SUPPORTED_KINDS:
        aliases = ARCHITECTURE_CONFIG_PARAMETER_ALIASES[canonical]
        optional = ARCHITECTURE_CONFIG_OPTIONAL_PARAMETERS[canonical]
        defaults = ARCHITECTURE_CONFIG_PARAMETER_DEFAULTS[canonical]
        unsupported_overrides = sorted(
            key for key in normalized_overrides if key not in aliases
        )
        if unsupported_overrides:
            failures.append(
                "overrides contains unsupported keys: "
                + ", ".join(unsupported_overrides)
            )
        for parameter in aliases:
            if parameter in normalized_overrides:
                value = normalized_overrides[parameter]
                parameters[parameter] = value
                parameter_sources[parameter] = _architecture_parameter_source(
                    source="explicit_override",
                    field=parameter,
                    value=value,
                )
                continue
            found = _architecture_config_lookup(canonical, config, parameter)
            if found is not None:
                value, field = found
                parameters[parameter] = value
                parameter_sources[parameter] = _architecture_parameter_source(
                    source="architecture_config_field",
                    field=field,
                    value=value,
                )
            elif parameter in optional:
                default = defaults.get(
                    parameter,
                    _ARCHITECTURE_CONFIG_DEFAULT_MISSING,
                )
                if default is not _ARCHITECTURE_CONFIG_DEFAULT_MISSING:
                    parameters[parameter] = default
                    parameter_sources[parameter] = _architecture_parameter_source(
                        source="default",
                        value=default,
                        note="receipt builder default applied by importer",
                    )
                else:
                    parameter_sources[parameter] = _architecture_parameter_source(
                        source="missing",
                        note="optional; receipt builder default applies if omitted",
                    )
            else:
                parameter_sources[parameter] = _architecture_parameter_source(
                    source="missing",
                    note="required for this contract kind",
                )
        if not failures:
            try:
                request = build_contract_request(canonical, parameters)
            except ValueError as exc:
                failures.append(str(exc))

    return {
        "schema_id": ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "architecture_config_fingerprint": _json_fingerprint(
            _json_ready_value(config)
        ),
        "request_content_fingerprint": (
            _json_fingerprint(request) if request is not None else None
        ),
        "kind": canonical,
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "parameters": _json_ready_value(parameters),
        "parameter_sources": parameter_sources,
        "request": request,
        "notes": [
            "This report only records deterministic translation from an AI architecture config into a Circle request.",
            "A successful import is not a proof; the emitted request still needs a theorem-linked receipt.",
            "Unsupported architecture behavior must not be silently certified by alias matching.",
        ],
    }


def build_validated_contract_receipt_from_architecture_config(
    kind: str,
    config: Mapping[str, Any],
    *,
    overrides: Mapping[str, Any] | None = None,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a pack-validated receipt from a non-RoPE AI architecture config."""

    request = build_contract_request_from_architecture_config(
        kind,
        config,
        overrides=overrides,
    )
    return build_validated_contract_receipt_from_request(request, pack=pack)


def _default_pack(pack: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(pack) if pack is not None else build_contract_pack()


def _support_block(pack: dict[str, Any], kind: str) -> dict[str, Any]:
    failures = validate_consumer_pack(pack)
    if failures:
        raise ValueError("invalid Circle AI contract pack: " + "; ".join(failures))
    contract = require_ready_contract(pack, kind)
    summary = readiness_summary(pack, kind)
    fingerprint_index = pack.get("contract_fingerprint_index", {})
    contract_fingerprint = {}
    if isinstance(fingerprint_index, dict):
        value = fingerprint_index.get(kind, {})
        if isinstance(value, dict):
            contract_fingerprint = value
    manifest_info = _manifest_proved_theorem_ids(pack)
    return {
        "schema_id": pack.get("schema_id"),
        "contract_id": summary.contract_id,
        "kind": kind,
        "fixture_status": contract.get("status"),
        "ready_for_downstream_fixture_use": summary.ready,
        "contract_pack_fingerprint": pack.get("pack_content_fingerprint"),
        "contract_content_fingerprint": contract_fingerprint.get(
            "content_fingerprint"
        ),
        "content_fingerprint_algorithm": pack.get("content_fingerprint_algorithm"),
        "quickstart_docs": list(summary.quickstart_docs),
        "living_book_pages": list(summary.living_book_pages),
        "entrypoints": list(summary.entrypoints),
        "validation_commands": list(summary.validation_commands),
        "source_paper": summary.source_paper,
        "planner_recommendations": [
            {
                "id": recommendation.get("id"),
                "action_kind": recommendation.get("action_kind"),
                "status": recommendation.get("status"),
                "coverage_scope": recommendation.get("coverage_scope"),
                "theorem_ids": list(recommendation.get("theorem_ids", [])),
            }
            for recommendation in contract_recommendations(pack, kind)
        ],
        "not_claimed": summary.not_claimed,
        "contract_theorem_count": summary.theorem_count,
        "contract_theorem_ids": list(summary.theorem_ids),
        "contract_dictionary_ids": list(summary.dictionary_ids),
        "theorem_index_path": manifest_info["path"],
        "theorem_index_available": manifest_info["available"],
        "theorem_index_proved_count": len(manifest_info["proved_ids"]),
    }


def _manifest_proved_theorem_ids(pack: Mapping[str, Any]) -> dict[str, Any]:
    proof_indexes = pack.get("proof_indexes", {})
    theorem_index = None
    if isinstance(proof_indexes, Mapping):
        value = proof_indexes.get("theorem_index")
        if isinstance(value, str):
            theorem_index = value
    if theorem_index is None:
        return {"path": None, "available": False, "proved_ids": set()}
    candidates = [Path(theorem_index)]
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / theorem_index)
    for candidate in candidates:
        if not candidate.exists():
            continue
        data = json.loads(candidate.read_text(encoding="utf-8"))
        records = data.get("theorems", []) if isinstance(data, dict) else []
        proved_ids = {
            record["id"]
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("id"), str)
            and record.get("canonical_status", record.get("status"))
            in {"proved", "lean_proved"}
        }
        return {
            "path": theorem_index,
            "available": True,
            "proved_ids": proved_ids,
        }
    return {"path": theorem_index, "available": False, "proved_ids": set()}


def _proof_status(
    *,
    theorem_ids: Sequence[str],
    support: Mapping[str, Any],
    pack: Mapping[str, Any],
) -> dict[str, Any]:
    ordered_ids = _unique_strings(theorem_ids)
    contract_ids = set(support.get("contract_theorem_ids", []))
    manifest_info = _manifest_proved_theorem_ids(pack)
    manifest_proved_ids = set(manifest_info["proved_ids"])
    proved_ids = set(contract_ids)
    if support.get("ready_for_downstream_fixture_use"):
        proved_ids |= contract_ids
    proved_ids |= manifest_proved_ids
    resolved_ids = contract_ids | manifest_proved_ids
    unresolved = tuple(
        theorem_id for theorem_id in ordered_ids if theorem_id not in resolved_ids
    )
    unproved = tuple(
        theorem_id
        for theorem_id in ordered_ids
        if theorem_id in resolved_ids and theorem_id not in proved_ids
    )
    all_resolved = not unresolved
    all_proved = all_resolved and not unproved
    return {
        "theorem_ids": list(ordered_ids),
        "theorem_count": len(ordered_ids),
        "all_theorem_ids_resolved": all_resolved,
        "all_theorem_ids_proved": all_proved,
        "unresolved_theorem_ids": list(unresolved),
        "unproved_theorem_ids": list(unproved),
        "theorem_index_path": manifest_info["path"],
        "theorem_index_available": manifest_info["available"],
        "proof_source": (
            "The generated contract pack resolves theorem ids to proved "
            "manifest entries and compiled Lean declarations. For custom "
            "parameter receipts, the generated theorem manifest is also used "
            "when available. This receipt does not re-run Lean."
        ),
    }


def _decision_verdict(*, status: str, request_passed: bool | None) -> str:
    if request_passed is True:
        return "passed"
    if request_passed is False:
        return "failed"
    if status == "numerical_only":
        return "numerical_only"
    if status == "outside_scope":
        return "outside_scope"
    return "undecided"


def _decision_assurance(
    *,
    status: str,
    proof_status: Mapping[str, Any],
    proof_layers: Mapping[str, Any],
) -> str:
    if status == "numerical_only":
        return "numerical_only"
    if status == "outside_scope":
        return "unsupported"
    if status == "undecided":
        return "undecided"
    if proof_status.get("all_theorem_ids_proved") is not True:
        return "undecided"
    if proof_layers.get("computed_fields") or proof_layers.get("numerical_only_fields"):
        return "mixed_theorem_and_computation"
    return "theorem_backed"


def _decision_summary(*, kind: str, status: str, request_passed: bool | None) -> str:
    if request_passed is True:
        return f"{kind} request passed with receipt status {status}."
    if request_passed is False:
        return f"{kind} request failed with receipt status {status}."
    return f"{kind} request is not decided by the current receipt frontier."


def _decision_next_action(*, status: str, request_passed: bool | None) -> str:
    if request_passed is True and status == "proved":
        return "Use the receipt as a theorem-linked structural certificate."
    if request_passed is False and status in {"proved", "impossible"}:
        return "Treat the requested property as rejected by the cited theorem layer."
    if status == "outside_scope":
        return "Narrow the request to the proved contract range or add a new theorem."
    if status == "numerical_only":
        return (
            "Do not gate on this result as a formal proof; add a theorem or "
            "acceptance policy."
        )
    return "Inspect unsupported and numerical-only fields before using this as a gate."


def _receipt_decision(
    *,
    kind: str,
    status: str,
    request_passed: bool | None,
    proof_status: Mapping[str, Any],
    proof_layers: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_id": "circle_calculus.ai_contract_decision.v0",
        "verdict": _decision_verdict(
            status=status,
            request_passed=request_passed,
        ),
        "assurance": _decision_assurance(
            status=status,
            proof_status=proof_status,
            proof_layers=proof_layers,
        ),
        "claim_status": status,
        "request_passed": request_passed,
        "theorem_count": proof_status.get("theorem_count"),
        "all_theorem_ids_proved": proof_status.get("all_theorem_ids_proved"),
        "proof_layer_counts": {
            bucket: len(proof_layers.get(bucket, []))
            for bucket in PROOF_LAYER_BUCKETS
        },
        "summary": _decision_summary(
            kind=kind,
            status=status,
            request_passed=request_passed,
        ),
        "next_action": _decision_next_action(
            status=status,
            request_passed=request_passed,
        ),
    }


def _base_receipt(
    *,
    kind: str,
    request_parameters: Mapping[str, Any],
    normalized_parameters: Mapping[str, Any],
    status: str,
    request_passed: bool | None,
    evidence: Mapping[str, Any],
    theorem_ids: Sequence[str],
    proof_layers: Mapping[str, Any],
    not_claimed: Sequence[str],
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    canonical = canonical_contract_kind(kind)
    if status not in STATUS_VALUES:
        raise ValueError(f"unsupported receipt status {status!r}")
    pack_dict = _default_pack(pack)
    request_object = build_contract_request(canonical, request_parameters)
    support = _support_block(pack_dict, canonical)
    support = dict(support)
    support["validation_commands"] = list(
        _unique_strings(
            (
                _runner_validation_command_for_request(request_object),
                *support["validation_commands"],
            )
        )
    )
    proof_status = _proof_status(
        theorem_ids=theorem_ids,
        support=support,
        pack=pack_dict,
    )
    proof_layers_object = dict(proof_layers)
    decision = _receipt_decision(
        kind=canonical,
        status=status,
        request_passed=request_passed,
        proof_status=proof_status,
        proof_layers=proof_layers_object,
    )
    normalized_object = dict(normalized_parameters)
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "contract_pack_schema_id": support["schema_id"],
        "kind": canonical,
        "contract_id": support["contract_id"],
        "status": status,
        "request_passed": request_passed,
        "decision": decision,
        "request": request_object,
        "request_content_fingerprint": _json_fingerprint(request_object),
        "normalized_request": normalized_object,
        "normalized_request_fingerprint": _json_fingerprint(normalized_object),
        "evidence": dict(evidence),
        "proof_status": proof_status,
        "proof_layers": proof_layers_object,
        "recommendations": list(support["planner_recommendations"]),
        "validation_commands": list(support["validation_commands"]),
        "support": support,
        "not_claimed": list(_unique_strings(not_claimed)),
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "receipt_content_fingerprint": "",
    }
    receipt["receipt_content_fingerprint"] = _json_fingerprint(receipt)
    failures = validate_contract_receipt(receipt)
    if failures:
        raise ValueError("invalid Circle AI contract receipt: " + "; ".join(failures))
    return receipt


def _d19_status_to_receipt_status(status: str) -> str:
    if status == "proved":
        return "proved"
    if status == "impossible":
        return "impossible"
    if status == "undecided_margin_gap":
        return "undecided"
    if status == "outside_range":
        return "outside_scope"
    return "numerical_only"


def _margin_relation_to_inv_context(
    *,
    margin: Fraction | None,
    inv_context_margin: Fraction,
) -> str | None:
    if margin is None:
        return None
    if margin < inv_context_margin:
        return "below_dirichlet_ceiling"
    if margin == inv_context_margin:
        return "at_dirichlet_ceiling"
    return "above_dirichlet_ceiling"


def _rope_dirichlet_guardrail(
    *,
    context: int,
    requested_margin: Fraction | None,
) -> dict[str, Any]:
    """Return the theorem-backed finite-context ``1/context`` ceiling guardrail."""

    if context <= 1:
        return {
            "applies": False,
            "context": context,
            "inv_context_margin": None,
            "requested_margin": (
                str(requested_margin) if requested_margin is not None else None
            ),
            "requested_margin_relation_to_ceiling": None,
            "requested_margin_exceeds_ceiling": None,
            "requested_margin_at_or_below_ceiling": None,
            "theorem_backed": False,
            "theorem_ids": [],
            "claim": (
                "The Dirichlet finite-context guardrail applies only when "
                "context > 1."
            ),
            "non_claim": (
                "This does not classify a nontrivial real-phase margin request."
            ),
        }

    inv_context_margin = Fraction(1, context)
    relation = _margin_relation_to_inv_context(
        margin=requested_margin,
        inv_context_margin=inv_context_margin,
    )
    return {
        "applies": True,
        "context": context,
        "inv_context_margin": str(inv_context_margin),
        "requested_margin": (
            str(requested_margin) if requested_margin is not None else None
        ),
        "requested_margin_relation_to_ceiling": relation,
        "requested_margin_exceeds_ceiling": (
            None if requested_margin is None else requested_margin > inv_context_margin
        ),
        "requested_margin_at_or_below_ceiling": (
            None if requested_margin is None else requested_margin <= inv_context_margin
        ),
        "theorem_backed": True,
        "theorem_ids": list(ROPE_DIRICHLET_GUARDRAIL_THEOREM_IDS),
        "claim": (
            "For any turn ratio and context > 1, there is an in-context "
            "nearest-integer witness with error at most 1/context; therefore "
            "any advertised finite-context margin strictly larger than "
            "1/context is impossible."
        ),
        "non_claim": (
            "This does not prove that a requested margin at or below 1/context "
            "holds; it is an upper-bound guardrail."
        ),
    }


def _rope_standard_channel0_d19_bank_bridge(
    *,
    context: int,
    requested_margin: Fraction,
) -> dict[str, Any]:
    """Return the conditional D19 first-channel bank bridge receipt payload."""

    certificate = certify_standard_channel0_d19_bank_request(
        requested_context=context,
        requested_margin=requested_margin,
    ).to_dict()
    applies = bool(certificate["pass_certificate"])
    theorem_ids = (
        list(certificate["theorem_ids"])
        if applies
        else []
    )
    return {
        "schema_id": certificate["schema_id"],
        "applies": applies,
        "request_status": (
            "proved_conditional_bank_no_near_turn"
            if applies
            else "outside_bank_bridge_scope"
        ),
        "theorem_backed": applies,
        "requested_context": certificate["requested_context"],
        "requested_margin": certificate["requested_margin"],
        "certified_context": certificate["certified_context"],
        "certified_margin": certificate["certified_margin"],
        "failure_reason": certificate["failure_reason"],
        "bank_shape": certificate["bank_shape"],
        "pair_scope": certificate["context_wide_pair_scope"],
        "context_wide_first_channel_contract": certificate[
            "context_wide_first_channel_contract"
        ],
        "radian_bank_form": (
            applies
            and certificate["bank_shape"] == "standard_channel0_first"
            and "AIRA-T0236" in certificate["theorem_ids"]
        ),
        "assumptions": list(certificate["assumptions"]),
        "tolerance_rule": certificate["tolerance_rule"],
        "theorem_ids": theorem_ids,
        "available_theorem_ids": list(certificate["theorem_ids"]),
        "lean_declarations": (
            list(certificate["lean_declarations"])
            if applies
            else []
        ),
        "available_lean_declarations": list(certificate["lean_declarations"]),
        "claim": certificate["explanation"],
        "non_claim": certificate["claim_boundary"],
    }


def build_rope_receipt(
    *,
    head_dim: int = 128,
    base: float = 10000.0,
    context: int = 32768,
    tolerance: float = 1e-6,
    discretization: str = "round",
    requested_margin: str | Fraction | None = None,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one RoPE configuration."""

    margin = parse_fraction(requested_margin)
    config = RoPEConfig(
        head_dim=head_dim,
        base=base,
        context_length=context,
        tolerance=tolerance,
        discretization=discretization,
    )
    certificate = certify_rope_positions(config).to_dict()
    theorem_ids = list(certificate["theorem_ids"])
    evidence: dict[str, Any] = {
        "exact_discrete_pass": certificate["exact_discrete"]["pass_exact"],
        "exact_discretized_periods": certificate["exact_discrete"][
            "discretized_periods"
        ],
        "exact_total_bank_collision_pair_count": certificate["exact_discrete"][
            "total_bank_collision_pair_count"
        ],
        "exact_common_collision_gap": certificate["exact_discrete"][
            "common_collision_gap"
        ],
        "exact_common_collision_gap_reaches_context": certificate[
            "exact_discrete"
        ]["common_collision_gap_reaches_context"],
        "exact_sample_collision_pairs": certificate["exact_discrete"][
            "sample_collision_pairs"
        ],
        "real_phase_numerical_pass_margin": certificate["real_phase_margin"][
            "pass_margin"
        ],
        "real_phase_numerical_worst_margin_radians": certificate[
            "real_phase_margin"
        ]["worst_margin_radians"],
        "real_phase_numerical_worst_gap": certificate["real_phase_margin"][
            "worst_gap"
        ],
        "real_phase_numerical_worst_channel_index": certificate[
            "real_phase_margin"
        ]["worst_channel_index"],
        "real_phase_numerical_near_collision_gaps": certificate[
            "real_phase_margin"
        ]["near_collision_gaps"],
        "proof_layer_summaries": [
            {
                "layer": layer["layer"],
                "status": layer["status"],
                "theorem_backed": layer["theorem_backed"],
                "theorem_ids": layer["theorem_ids"],
            }
            for layer in certificate["proof_layers"]
        ],
    }
    dirichlet_guardrail = _rope_dirichlet_guardrail(
        context=context,
        requested_margin=margin,
    )
    evidence["real_phase_dirichlet_guardrail"] = dirichlet_guardrail
    if dirichlet_guardrail["applies"]:
        theorem_ids.extend(dirichlet_guardrail["theorem_ids"])
    status = "proved"
    request_passed: bool | None = bool(certificate["exact_discrete"]["pass_exact"])
    d19_receipt_status: str | None = None
    if margin is not None:
        d19 = certify_standard_channel0_d19_range_request_margin_bracket(
            requested_context=context,
            requested_margin=margin,
        ).to_dict()
        evidence["standard_channel0_d19_request_classifier"] = d19
        theorem_ids.extend(d19["theorem_ids"])
        d19_receipt_status = _d19_status_to_receipt_status(d19["request_status"])
        status = d19_receipt_status
        if status == "proved":
            request_passed = True
        elif status == "impossible":
            request_passed = False
        elif status in {"undecided", "outside_scope"}:
            request_passed = None
        bank_bridge = _rope_standard_channel0_d19_bank_bridge(
            context=context,
            requested_margin=margin,
        )
        evidence["standard_channel0_d19_bank_bridge"] = bank_bridge
        theorem_ids.extend(bank_bridge["theorem_ids"])
        if bank_bridge["applies"]:
            if status in {"outside_scope", "proved"}:
                status = "proved"
                request_passed = True
    if dirichlet_guardrail["requested_margin_exceeds_ceiling"] is True:
        status = "impossible"
        request_passed = False
    proof_layers = {
        "proved_fields": [
            "exact_discrete_pass",
            "exact_total_bank_collision_pair_count",
            "exact_common_collision_gap",
        ],
        "computed_fields": [
            "exact_discretized_periods",
            "exact_sample_collision_pairs",
        ],
        "numerical_only_fields": [
            "real_phase_numerical_pass_margin",
            "real_phase_numerical_worst_margin_radians",
            "real_phase_numerical_worst_gap",
            "real_phase_numerical_near_collision_gaps",
        ],
        "unsupported_fields": [
            "full all-channel real-valued RoPE separation theorem",
            "model quality or useful context-length improvement",
        ],
    }
    if dirichlet_guardrail["applies"]:
        proof_layers["proved_fields"].append("real_phase_dirichlet_guardrail")
    else:
        proof_layers["unsupported_fields"].append(
            "real_phase_dirichlet_guardrail requires context > 1"
        )
    if d19_receipt_status in {"proved", "impossible", "undecided"}:
        proof_layers["proved_fields"].append(
            "standard_channel0_d19_request_classifier"
        )
    elif d19_receipt_status == "outside_scope":
        proof_layers["unsupported_fields"].append(
            "standard_channel0_d19_request_classifier outside its proved context range"
        )
    if margin is not None:
        bank_bridge = evidence["standard_channel0_d19_bank_bridge"]
        if bank_bridge["applies"]:
            proof_layers["proved_fields"].append(
                "standard_channel0_d19_bank_bridge"
            )
        else:
            proof_layers["unsupported_fields"].append(
                "standard_channel0_d19_bank_bridge outside its certified "
                "margin/context scope"
            )
    return _base_receipt(
        kind="rope_position_distinguishability",
        request_parameters={
            "head_dim": head_dim,
            "base": base,
            "context": context,
            "tolerance": tolerance,
            "discretization": discretization,
            "requested_margin": str(margin) if margin is not None else None,
        },
        normalized_parameters={
            "head_dim": config.head_dim,
            "base": config.base,
            "context_length": config.context_length,
            "tolerance": config.tolerance,
            "discretization": config.discretization,
            "requested_margin": str(margin) if margin is not None else None,
        },
        status=status,
        request_passed=request_passed,
        evidence=evidence,
        theorem_ids=theorem_ids,
        proof_layers=proof_layers,
        not_claimed=[
            certificate["claim_boundary"],
            "The numerical real-phase scan is executable support, not a proof.",
        ],
        pack=pack,
    )


def build_kv_cache_receipt(
    *,
    cache_size: int,
    current: int,
    token: int,
    batch_tokens: Sequence[int] = (),
    sink_size: int = 0,
    request_id: str = "read_request",
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one KV-cache ring-buffer request."""

    requested_tokens = tuple(batch_tokens) or (token,)
    window = asdict(
        certify_kv_cache_window(
            cache_size=cache_size,
            current=current,
            token=token,
        )
    )
    batch = asdict(
        certify_kv_cache_batch(
            cache_size=cache_size,
            current=current,
            tokens=requested_tokens,
        )
    )
    adapter_request = asdict(
        certify_kv_cache_adapter_request_trace(
            cache_size=cache_size,
            current=current,
            requested_tokens=requested_tokens,
            request_id=request_id,
        )
    )
    live_window = asdict(
        certify_kv_cache_live_window(
            cache_size=cache_size,
            current=current,
        )
    )
    live_window_request = asdict(
        certify_kv_cache_live_window_request(
            cache_size=cache_size,
            current=current,
            request_id=f"{request_id}_generated_live_window",
        )
    )
    evidence: dict[str, Any] = {
        "window_certificate": window,
        "batch_certificate": batch,
        "adapter_request_trace_certificate": adapter_request,
        "live_window_certificate": live_window,
        "live_window_request_certificate": live_window_request,
    }
    theorem_ids = list(window["theorem_ids"])
    theorem_ids.extend(batch["theorem_ids"])
    theorem_ids.extend(adapter_request["theorem_ids"])
    theorem_ids.extend(live_window["theorem_ids"])
    theorem_ids.extend(live_window_request["theorem_ids"])
    theorem_ids.extend(live_window_request["fixture_theorem_ids"])
    proved_fields = [
        "window_certificate",
        "batch_certificate",
        "adapter_request_trace_certificate",
        "live_window_certificate",
        "live_window_request_certificate",
    ]
    unsupported_fields = [
        "paging policy",
        "throughput",
        "memory saving",
        "retrieval quality",
        "implementation correctness",
    ]
    if sink_size:
        sink_window = asdict(
            certify_kv_cache_sink_window(
                sink_size=sink_size,
                cache_size=cache_size,
                current=current,
            )
        )
        evidence["sink_window_certificate"] = sink_window
        theorem_ids.extend(sink_window["theorem_ids"])
        theorem_ids.extend(sink_window["fixture_theorem_ids"])
        proved_fields.append("sink_window_certificate")
    else:
        unsupported_fields.append(
            "sink_window_certificate requires positive sink_size"
        )
    return _base_receipt(
        kind="kv_cache_ring_buffer",
        request_parameters={
            "cache_size": cache_size,
            "current": current,
            "token": token,
            "batch_tokens": list(batch_tokens),
            "sink_size": sink_size,
            "request_id": request_id,
        },
        normalized_parameters={
            "cache_size": cache_size,
            "current": current,
            "token": token,
            "requested_tokens": list(requested_tokens),
            "sink_size": sink_size,
            "request_id": request_id,
        },
        status="proved",
        request_passed=bool(adapter_request["pass_certificate"]),
        evidence=evidence,
        theorem_ids=theorem_ids,
        proof_layers={
            "proved_fields": proved_fields,
            "computed_fields": [],
            "numerical_only_fields": [],
            "unsupported_fields": unsupported_fields,
        },
        not_claimed=[
            "This is a proof-carrying finite ring-buffer indexing, retained-window, "
            "and modeled adapter request-trace certificate. It is not a paging-policy, "
            "throughput, memory-saving, retrieval-quality, implementation-correctness, "
            "deployment-safety, or model-quality claim."
        ],
        pack=pack,
    )


def build_sparse_attention_receipt(
    *,
    context: int,
    strides: Sequence[int],
    path_length: int,
    local_window: int,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one sparse-attention plan."""

    certificate = asdict(
        certify_stride_family_coverage(
            sequence_length=context,
            strides=tuple(strides),
            path_length=path_length,
            local_window=local_window,
        )
    )
    return _base_receipt(
        kind="sparse_attention_coverage",
        request_parameters={
            "context": context,
            "strides": list(strides),
            "path_length": path_length,
            "local_window": local_window,
        },
        normalized_parameters={
            "sequence_length": certificate["sequence_length"],
            "strides": list(certificate["strides"]),
            "path_length": certificate["path_length"],
            "local_window": certificate["local_window"],
        },
        status="proved",
        request_passed=bool(certificate["coverage_complete"]),
        evidence=certificate,
        theorem_ids=certificate["theorem_ids"],
        proof_layers={
            "proved_fields": [
                "coverage_complete",
                "covered_lags",
                "covered_lag_count",
                "uncovered_lags",
                "uncovered_lag_count",
                "first_uncovered_lag",
                "uncovered_lag_intervals",
                "uncovered_lag_interval_count",
                "first_uncovered_lag_interval_start",
                "first_uncovered_lag_interval_stop",
                "first_uncovered_lag_interval_length",
                "first_uncovered_lag_interval_repair_window",
                "first_uncovered_lag_interval_additional_local_slots",
                "first_uncovered_interval_repair_reaches_interval",
                "first_interval_repair_next_uncovered_lag",
                "first_interval_repair_still_has_gap",
                "first_interval_repair_covers_context",
                "largest_uncovered_interval_start",
                "largest_uncovered_interval_stop",
                "largest_uncovered_interval_length",
                "largest_uncovered_interval_repair_window",
                "largest_uncovered_interval_additional_local_slots",
                "largest_uncovered_interval_repair_reaches_interval",
                "largest_interval_repair_next_uncovered_lag",
                "largest_interval_repair_still_has_gap",
                "largest_interval_repair_covers_context",
                "largest_uncovered_interval_is_tail",
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
                "candidate_budget_per_query",
                "raw_candidate_budget_upper_bound",
                "deduplicated_candidate_budget_upper_bound",
                "raw_budget_shortfall_certifies_incomplete",
                "theorem_side_lag_candidates",
                "theorem_side_unique_lag_candidate_count",
                "theorem_side_lag_candidates_no_collision",
                "theorem_side_lag_candidate_dedup_loss",
                "theorem_side_lag_candidate_collision_pair_count",
                "lag_collision_pair_count_zero_matches_no_collision",
                "lag_collision_pair_count_positive_matches_collision",
                "lag_collision_pair_count_bounds_dedup_loss",
                "lag_dedup_loss_accounting_matches_raw",
                "theorem_side_query_candidates",
                "theorem_side_unique_query_candidate_count",
                "theorem_side_query_candidates_no_collision",
                "theorem_side_query_candidate_dedup_loss",
                "theorem_side_query_candidate_collision_pair_count",
                "query_collision_pair_count_zero_matches_no_collision",
                "query_collision_pair_count_positive_matches_collision",
                "query_collision_pair_count_bounds_dedup_loss",
                "query_dedup_loss_accounting_matches_raw",
                "stride_family_periods",
                "no_zero_period_thresholds",
                "stride_family_zero_residue_step_counts",
                "stride_family_zero_residue_total_step_count",
                "zero_residue_step_counts_match_period_formula",
                "zero_residue_total_count_matches_sum_formula",
                "zero_residue_total_count_zero_matches_no_zero_condition",
                "no_zero_period_threshold_matches_condition",
            ],
            "computed_fields": [],
            "numerical_only_fields": [],
            "unsupported_fields": [
                "attention quality",
                "runtime speed",
                "optimal sparse-layout design",
                "model accuracy",
            ],
        },
        not_claimed=[
            "This is a proof-carrying finite sparse-plan coverage and budget "
            "certificate. It is not an attention-quality, runtime, memory, "
            "optimal-layout, training, or model-quality claim."
        ],
        pack=pack,
    )


def build_recurrence_receipt(
    *,
    loop_period: int = 5,
    sample_index: int = 8,
    max_loops: int = 7,
    token_count: int = 8,
    selected_block_start: int = 2,
    selected_block_width: int = 3,
    shift_passes: int = 3,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for one finite recurrence schedule."""

    payload = build_recurrence_schedule_contract(
        loop_period=loop_period,
        sample_index=sample_index,
        max_loops=max_loops,
        token_indices=tuple(range(token_count)),
        selected_block_start=selected_block_start,
        selected_block_width=selected_block_width,
        periodic_shift_passes=shift_passes,
    )
    fields = payload["fields"]
    return _base_receipt(
        kind="recurrence_schedule",
        request_parameters={
            "loop_period": loop_period,
            "sample_index": sample_index,
            "max_loops": max_loops,
            "token_count": token_count,
            "selected_block_start": selected_block_start,
            "selected_block_width": selected_block_width,
            "shift_passes": shift_passes,
        },
        normalized_parameters={
            "loop_period": fields["loop_period"],
            "sample_index": fields["sample_index"],
            "max_loops": fields["max_loops"],
            "token_count": len(fields["tokens"]),
            "selected_block_start": selected_block_start,
            "selected_block_width": selected_block_width,
            "periodic_shift_passes": fields["periodic_shift_passes"],
        },
        status="proved",
        request_passed=bool(payload["contract_passed"]),
        evidence=payload,
        theorem_ids=payload["theorem_ids"],
        proof_layers={
            "proved_fields": [
                "fields.required_steps",
                "fields.exit_step",
                "fields.active_token_count_trace",
                "fields.total_active_token_work",
                "fields.scheduled_work_saving",
                "fields.scheduled_work_saving_accounting",
                "fields.active_inactive_work_accounting",
                "fields.scheduled_work_saving_positive",
                "fields.post_period_multi_extension_scheduled_work_saving",
                "fields.post_period_multi_extension_active_work_unchanged",
                "fields.periodic_shift_required_steps_invariant",
                "fields.periodic_shift_recurrence_budget_invariant",
                "fields.periodic_shift_training_free_budget_invariant",
                "fields.periodic_shift_exit_step_invariant",
                "fields.periodic_shift_overthinking_boundary_invariant",
                "fields.periodic_shift_active_at_step_invariant",
            ],
            "computed_fields": [
                "fields.loop_period",
                "fields.sample_index",
                "fields.total_inactive_token_work",
                "fields.post_period_multi_extension_horizon_steps",
            ],
            "numerical_only_fields": [],
            "unsupported_fields": [
                "reasoning quality",
                "training benefit",
                "recursive-transformer model quality",
            ],
        },
        not_claimed=[payload["not_claimed"]],
        pack=pack,
    )


def _generic_ready_contract_receipt(
    *,
    kind: str,
    request_parameters: Mapping[str, Any],
    normalized_parameters: Mapping[str, Any],
    payload: Mapping[str, Any],
    unsupported_fields: Sequence[str],
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    fields = payload.get("fields")
    if not isinstance(fields, Mapping):
        raise ValueError("generic Circle AI contract payload must contain fields")
    consumer_check = payload.get("consumer_check")
    if not isinstance(consumer_check, Mapping):
        raise ValueError("generic Circle AI contract payload must contain consumer_check")
    minimum_fields = {
        field
        for field in consumer_check.get("minimum_fields", [])
        if isinstance(field, str)
    }
    proved_fields = [
        "contract_passed",
        "consumer_check.ready_for_downstream_fixture_use",
        *[
            f"fields.{field}"
            for field in fields
            if isinstance(field, str) and field in minimum_fields
        ],
    ]
    computed_fields = [
        f"fields.{field}"
        for field in fields
        if isinstance(field, str) and field not in minimum_fields
    ]
    not_claimed = payload.get("not_claimed")
    theorem_ids = payload.get("theorem_ids")
    if not isinstance(not_claimed, str):
        raise ValueError("generic Circle AI contract payload must contain not_claimed")
    if not isinstance(theorem_ids, Sequence) or isinstance(theorem_ids, (str, bytes)):
        raise ValueError("generic Circle AI contract payload must contain theorem_ids")
    return _base_receipt(
        kind=kind,
        request_parameters=request_parameters,
        normalized_parameters=normalized_parameters,
        status="proved",
        request_passed=bool(payload.get("contract_passed")),
        evidence=payload,
        theorem_ids=[str(theorem_id) for theorem_id in theorem_ids],
        proof_layers={
            "proved_fields": proved_fields,
            "computed_fields": computed_fields,
            "numerical_only_fields": [],
            "unsupported_fields": list(unsupported_fields),
        },
        not_claimed=[not_claimed],
        pack=pack,
    )


def build_strided_candidate_fanout_receipt(
    *,
    context_length: int = 12,
    stride: int = 5,
    start_index: int = 0,
    path_length: int = 12,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for finite strided candidate fanout."""

    payload = build_strided_candidate_fanout_contract(
        context_length=context_length,
        stride=stride,
        start_index=start_index,
        path_length=path_length,
    )
    fields = payload["fields"]
    return _generic_ready_contract_receipt(
        kind="strided_candidate_fanout",
        request_parameters={
            "context_length": context_length,
            "stride": stride,
            "start_index": start_index,
            "path_length": path_length,
        },
        normalized_parameters={
            "context_length": fields["context_length"],
            "stride": fields["stride"],
            "start_index": fields["start_index"],
            "path_length": path_length,
        },
        payload=payload,
        unsupported_fields=[
            "model-quality improvement",
            "search-quality improvement",
            "throughput or latency",
            "optimal candidate schedule",
        ],
        pack=pack,
    )


def build_cyclic_memory_receipt(
    *,
    bank_size: int = 8,
    event_index: int = 23,
    event_count: int = 32,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for cyclic memory residue/winding facts."""

    payload = build_cyclic_memory_contract(
        bank_size=bank_size,
        event_index=event_index,
        event_count=event_count,
    )
    fields = payload["fields"]
    return _generic_ready_contract_receipt(
        kind="cyclic_memory_residue_winding",
        request_parameters={
            "bank_size": bank_size,
            "event_index": event_index,
            "event_count": event_count,
        },
        normalized_parameters={
            "bank_size": fields["bank_size"],
            "event_index": fields["event_index"],
            "event_count": fields["event_count"],
            "residue_slot": fields["residue_slot"],
            "winding": fields["winding"],
        },
        payload=payload,
        unsupported_fields=[
            "retrieval quality",
            "memory compression ratio for a real model",
            "implementation-level cache safety",
            "model-quality improvement",
        ],
        pack=pack,
    )


def build_multicoil_phase_feature_receipt(
    *,
    periods: Sequence[int] = (5, 7),
    position: int = 37,
    query_position: int = 41,
    key_position: int = 18,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for finite MultiCoil phase features."""

    payload = build_multicoil_phase_feature_contract(
        periods=tuple(periods),
        position=position,
        query_position=query_position,
        key_position=key_position,
    )
    fields = payload["fields"]
    return _generic_ready_contract_receipt(
        kind="multicoil_phase_feature",
        request_parameters={
            "periods": list(periods),
            "position": position,
            "query_position": query_position,
            "key_position": key_position,
        },
        normalized_parameters={
            "periods": list(fields["periods"]),
            "position": fields["position"],
            "query_position": fields["query_position"],
            "key_position": fields["key_position"],
            "joint_repeat_horizon": fields["joint_repeat_horizon"],
        },
        payload=payload,
        unsupported_fields=[
            "feature usefulness in a trained model",
            "attention-quality improvement",
            "training stability",
            "all-real-phase RoPE separation",
        ],
        pack=pack,
    )


def build_circulant_block_cyclic_mixer_receipt(
    *,
    period: int = 8,
    channel_count: int = 128,
    block_size: int = 8,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for finite circulant/block-cyclic mixers."""

    payload = build_circulant_block_cyclic_mixer_contract(
        period=period,
        channel_count=channel_count,
        block_size=block_size,
    )
    fields = payload["fields"]
    return _generic_ready_contract_receipt(
        kind="circulant_block_cyclic_mixer",
        request_parameters={
            "period": period,
            "channel_count": channel_count,
            "block_size": block_size,
        },
        normalized_parameters={
            "period": fields["period"],
            "channel_count": fields["channel_count"],
            "block_size": fields["block_size"],
            "circulant_parameters": fields["circulant_parameters"],
            "block_cyclic_parameters": fields["block_cyclic_parameters"],
        },
        payload=payload,
        unsupported_fields=[
            "accuracy improvement over dense layers",
            "training speed",
            "hardware efficiency",
            "optimal mixer architecture",
        ],
        pack=pack,
    )


def build_seed_rule_receipt(
    *,
    n: int = 128,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a theorem-linked receipt for finite seed/rule regeneration."""

    payload = build_seed_rule_contract(n=n)
    fields = payload["fields"]
    return _generic_ready_contract_receipt(
        kind="seed_rule_exact_regeneration",
        request_parameters={"n": n},
        normalized_parameters={
            "n": n,
            "artifact_id": fields["artifact_id"],
            "fixture_n": fields["fixture_n"],
            "exact_regeneration": fields["exact_regeneration"],
            "storage_saving": fields["storage_saving"],
        },
        payload=payload,
        unsupported_fields=[
            "global compression optimality",
            "Kolmogorov complexity",
            "learned generator discovery",
            "model-quality improvement",
        ],
        pack=pack,
    )


def build_contract_receipt(
    kind: str,
    parameters: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch to the receipt builder for ``kind``."""

    canonical = canonical_contract_kind(kind)
    params = dict(parameters)
    if canonical == "rope_position_distinguishability":
        return build_rope_receipt(pack=pack, **params)
    if canonical == "kv_cache_ring_buffer":
        return build_kv_cache_receipt(pack=pack, **params)
    if canonical == "sparse_attention_coverage":
        return build_sparse_attention_receipt(pack=pack, **params)
    if canonical == "recurrence_schedule":
        return build_recurrence_receipt(pack=pack, **params)
    if canonical == "strided_candidate_fanout":
        return build_strided_candidate_fanout_receipt(pack=pack, **params)
    if canonical == "cyclic_memory_residue_winding":
        return build_cyclic_memory_receipt(pack=pack, **params)
    if canonical == "multicoil_phase_feature":
        return build_multicoil_phase_feature_receipt(pack=pack, **params)
    if canonical == "circulant_block_cyclic_mixer":
        return build_circulant_block_cyclic_mixer_receipt(pack=pack, **params)
    if canonical == "seed_rule_exact_regeneration":
        return build_seed_rule_receipt(pack=pack, **params)
    raise ValueError(f"unsupported contract kind: {kind}")


def build_validated_contract_receipt(
    kind: str,
    parameters: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a receipt and validate it against the loaded contract pack."""

    pack_dict = _default_pack(pack)
    receipt = build_contract_receipt(kind, parameters, pack=pack_dict)
    failures = validate_contract_receipt_against_pack(receipt, pack_dict)
    if failures:
        raise ValueError(
            "invalid Circle AI contract receipt for loaded pack: "
            + "; ".join(failures)
        )
    return receipt


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_allowed_keys(
    parameters: Mapping[str, Any],
    *,
    allowed: set[str],
    failures: list[str],
) -> None:
    extra = sorted(str(key) for key in parameters if key not in allowed)
    if extra:
        failures.append("parameters contains unsupported keys: " + ", ".join(extra))


def _require_keys(
    parameters: Mapping[str, Any],
    *,
    required: set[str],
    failures: list[str],
) -> None:
    missing = sorted(key for key in required if key not in parameters)
    if missing:
        failures.append("parameters is missing required keys: " + ", ".join(missing))


def _require_positive_int(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
) -> None:
    if key in parameters and (not _is_int(parameters[key]) or parameters[key] <= 0):
        failures.append(f"parameters.{key} must be a positive integer")


def _require_even_int(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
    *,
    reason: str,
) -> None:
    if key in parameters and _is_int(parameters[key]) and parameters[key] % 2 != 0:
        failures.append(f"parameters.{key} must be even {reason}")


def _require_nonnegative_int(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
) -> None:
    if key in parameters and (not _is_int(parameters[key]) or parameters[key] < 0):
        failures.append(f"parameters.{key} must be a nonnegative integer")


def _require_positive_number(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
) -> None:
    if key in parameters and (not _is_number(parameters[key]) or parameters[key] <= 0):
        failures.append(f"parameters.{key} must be a positive number")


def _require_nonnegative_number(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
) -> None:
    if key in parameters and (not _is_number(parameters[key]) or parameters[key] < 0):
        failures.append(f"parameters.{key} must be a nonnegative number")


def _require_int_sequence(
    parameters: Mapping[str, Any],
    key: str,
    failures: list[str],
    *,
    positive: bool = False,
    nonempty: bool = False,
) -> None:
    if key not in parameters:
        return
    value = parameters[key]
    if (
        isinstance(value, (str, bytes))
        or not isinstance(value, Sequence)
        or any(not _is_int(item) for item in value)
    ):
        failures.append(f"parameters.{key} must be an integer array")
        return
    if nonempty and not value:
        failures.append(f"parameters.{key} must be non-empty")
    if positive and any(item <= 0 for item in value):
        failures.append(f"parameters.{key} must contain positive integers")


def _validate_request_parameters(
    *,
    canonical: str,
    parameters: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    if canonical == "rope_position_distinguishability":
        allowed = {
            "head_dim",
            "base",
            "context",
            "tolerance",
            "discretization",
            "requested_margin",
        }
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "head_dim", failures)
        _require_even_int(
            parameters,
            "head_dim",
            failures,
            reason="because RoPE uses dimension pairs",
        )
        _require_positive_number(parameters, "base", failures)
        _require_positive_int(parameters, "context", failures)
        _require_nonnegative_number(parameters, "tolerance", failures)
        if "discretization" in parameters and parameters["discretization"] not in {
            "round",
            "floor",
            "ceil",
        }:
            failures.append("parameters.discretization must be round, floor, or ceil")
        margin = parameters.get("requested_margin")
        if margin is not None:
            if not isinstance(margin, (str, Fraction)):
                failures.append("parameters.requested_margin must be a string or null")
            else:
                try:
                    parse_fraction(margin)
                except (ValueError, ZeroDivisionError):
                    failures.append("parameters.requested_margin must parse as a Fraction")
    elif canonical == "kv_cache_ring_buffer":
        allowed = {
            "cache_size",
            "current",
            "token",
            "batch_tokens",
            "sink_size",
            "request_id",
        }
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_keys(
            parameters,
            required={"cache_size", "current", "token"},
            failures=failures,
        )
        _require_positive_int(parameters, "cache_size", failures)
        _require_nonnegative_int(parameters, "current", failures)
        _require_nonnegative_int(parameters, "token", failures)
        _require_int_sequence(parameters, "batch_tokens", failures)
        _require_nonnegative_int(parameters, "sink_size", failures)
        if "request_id" in parameters and (
            not isinstance(parameters["request_id"], str) or not parameters["request_id"]
        ):
            failures.append("parameters.request_id must be a non-empty string")
    elif canonical == "sparse_attention_coverage":
        allowed = {"context", "strides", "path_length", "local_window"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_keys(
            parameters,
            required={"context", "strides", "path_length", "local_window"},
            failures=failures,
        )
        _require_positive_int(parameters, "context", failures)
        _require_int_sequence(
            parameters,
            "strides",
            failures,
            positive=True,
            nonempty=True,
        )
        _require_nonnegative_int(parameters, "path_length", failures)
        _require_nonnegative_int(parameters, "local_window", failures)
    elif canonical == "recurrence_schedule":
        allowed = {
            "loop_period",
            "sample_index",
            "max_loops",
            "token_count",
            "selected_block_start",
            "selected_block_width",
            "shift_passes",
        }
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "loop_period", failures)
        _require_nonnegative_int(parameters, "sample_index", failures)
        _require_positive_int(parameters, "max_loops", failures)
        _require_positive_int(parameters, "token_count", failures)
        _require_nonnegative_int(parameters, "selected_block_start", failures)
        _require_positive_int(parameters, "selected_block_width", failures)
        _require_nonnegative_int(parameters, "shift_passes", failures)
    elif canonical == "strided_candidate_fanout":
        allowed = {"context_length", "stride", "start_index", "path_length"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "context_length", failures)
        _require_nonnegative_int(parameters, "stride", failures)
        _require_nonnegative_int(parameters, "start_index", failures)
        _require_positive_int(parameters, "path_length", failures)
    elif canonical == "cyclic_memory_residue_winding":
        allowed = {"bank_size", "event_index", "event_count"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "bank_size", failures)
        _require_nonnegative_int(parameters, "event_index", failures)
        _require_positive_int(parameters, "event_count", failures)
        if (
            _is_int(parameters.get("event_index"))
            and _is_int(parameters.get("event_count"))
            and parameters["event_index"] >= parameters["event_count"]
        ):
            failures.append("parameters.event_index must be less than event_count")
    elif canonical == "multicoil_phase_feature":
        allowed = {"periods", "position", "query_position", "key_position"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_int_sequence(
            parameters,
            "periods",
            failures,
            positive=True,
            nonempty=True,
        )
        _require_nonnegative_int(parameters, "position", failures)
        _require_nonnegative_int(parameters, "query_position", failures)
        _require_nonnegative_int(parameters, "key_position", failures)
    elif canonical == "circulant_block_cyclic_mixer":
        allowed = {"period", "channel_count", "block_size"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "period", failures)
        _require_positive_int(parameters, "channel_count", failures)
        _require_positive_int(parameters, "block_size", failures)
        if (
            _is_int(parameters.get("block_size"))
            and _is_int(parameters.get("channel_count"))
            and parameters["block_size"] > parameters["channel_count"]
        ):
            failures.append(
                "parameters.block_size must be less than or equal to channel_count"
            )
    elif canonical == "seed_rule_exact_regeneration":
        allowed = {"n"}
        _require_allowed_keys(parameters, allowed=allowed, failures=failures)
        _require_positive_int(parameters, "n", failures)
    return failures


def validate_contract_request(request: Mapping[str, Any]) -> list[str]:
    """Return request-shape failures for the public runner request object."""

    failures: list[str] = []
    extra_keys = sorted(
        str(key)
        for key in request
        if key not in {"schema_id", "kind", "parameters"}
    )
    if extra_keys:
        failures.append(
            "request contains unsupported keys: " + ", ".join(extra_keys)
        )
    if request.get("schema_id") != REQUEST_SCHEMA_ID:
        failures.append(f"schema_id must be {REQUEST_SCHEMA_ID!r}")
    kind = request.get("kind")
    canonical: str | None = None
    if not isinstance(kind, str) or not kind:
        failures.append("kind must be a non-empty string")
    elif kind not in KIND_ALIASES:
        failures.append("kind must be a supported Circle AI contract kind or alias")
    else:
        canonical = KIND_ALIASES[kind]
    parameters = request.get("parameters")
    if not isinstance(parameters, Mapping):
        failures.append("parameters must be an object")
    elif canonical is not None:
        failures.extend(
            _validate_request_parameters(canonical=canonical, parameters=parameters)
        )
    return failures


def build_contract_request_validation_report(request: Mapping[str, Any]) -> dict[str, Any]:
    """Return a stable validation report for a versioned public request object."""

    failures = validate_contract_request(request)
    raw_kind = request.get("kind")
    kind = raw_kind if isinstance(raw_kind, str) else None
    canonical_kind = None
    if kind is not None:
        try:
            canonical_kind = canonical_contract_kind(kind)
        except ValueError:
            canonical_kind = None
    return {
        "schema_id": REQUEST_VALIDATION_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "request_content_fingerprint": _json_fingerprint(_json_ready_value(request)),
        "ok": not failures,
        "kind": kind,
        "canonical_kind": canonical_kind,
        "failure_count": len(failures),
        "failures": failures,
    }


def build_contract_receipt_from_request(
    request: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a receipt from a versioned public runner request object."""

    failures = validate_contract_request(request)
    if failures:
        raise ValueError("invalid Circle AI contract request: " + "; ".join(failures))
    kind = str(request["kind"])
    parameters = request["parameters"]
    assert isinstance(parameters, Mapping)
    try:
        return build_contract_receipt(kind, parameters, pack=pack)
    except TypeError as exc:
        raise ValueError(
            "invalid Circle AI contract request parameters: " + str(exc)
        ) from exc
    except ValueError as exc:
        message = str(exc)
        if message.startswith(
            ("invalid Circle AI contract pack", "invalid Circle AI contract receipt")
        ):
            raise
        raise ValueError(
            "invalid Circle AI contract request parameters: " + message
        ) from exc


def build_validated_contract_receipt_from_request(
    request: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a request receipt and validate it against the loaded pack."""

    pack_dict = _default_pack(pack)
    receipt = build_contract_receipt_from_request(request, pack=pack_dict)
    failures = validate_contract_receipt_against_pack(receipt, pack_dict)
    if failures:
        raise ValueError(
            "invalid Circle AI contract receipt for loaded pack: "
            + "; ".join(failures)
        )
    return receipt


def build_validated_rope_receipt_from_model_config(
    config: Mapping[str, Any],
    *,
    head_dim: int | None = None,
    base: float | None = None,
    context: int | None = None,
    tolerance: float | None = None,
    discretization: str | None = None,
    requested_margin: str | Fraction | None = None,
    pack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a pack-validated standard-RoPE receipt from a model config object."""

    request = build_rope_contract_request_from_model_config(
        config,
        head_dim=head_dim,
        base=base,
        context=context,
        tolerance=tolerance,
        discretization=discretization,
        requested_margin=requested_margin,
    )
    return build_validated_contract_receipt_from_request(request, pack=pack)


def _validate_decision_block(
    *,
    decision: Any,
    receipt: Mapping[str, Any],
    proof_status: Any,
    proof_layers: Any,
    failures: list[str],
) -> None:
    if not isinstance(decision, dict):
        failures.append("decision must be an object")
        return
    if decision.get("schema_id") != "circle_calculus.ai_contract_decision.v0":
        failures.append(
            "decision.schema_id must be circle_calculus.ai_contract_decision.v0"
        )
    if decision.get("verdict") not in DECISION_VERDICTS:
        failures.append("decision.verdict must be a supported decision verdict")
    if decision.get("assurance") not in DECISION_ASSURANCE_LEVELS:
        failures.append("decision.assurance must be a supported assurance level")
    if decision.get("claim_status") != receipt.get("status"):
        failures.append("decision.claim_status must match receipt status")
    if decision.get("request_passed") != receipt.get("request_passed"):
        failures.append("decision.request_passed must match receipt request_passed")
    if not isinstance(proof_status, dict):
        return
    if decision.get("theorem_count") != proof_status.get("theorem_count"):
        failures.append("decision.theorem_count must match proof_status.theorem_count")
    if decision.get("all_theorem_ids_proved") != proof_status.get(
        "all_theorem_ids_proved"
    ):
        failures.append("decision.all_theorem_ids_proved must match proof_status")
    counts = decision.get("proof_layer_counts")
    if not isinstance(counts, dict):
        failures.append("decision.proof_layer_counts must be an object")
    elif isinstance(proof_layers, dict):
        for bucket in PROOF_LAYER_BUCKETS:
            fields = proof_layers.get(bucket)
            expected = len(fields) if isinstance(fields, list) else None
            if counts.get(bucket) != expected:
                failures.append(
                    f"decision.proof_layer_counts.{bucket} must match proof_layers"
                )
    if not isinstance(decision.get("summary"), str) or not decision.get("summary"):
        failures.append("decision.summary must be a non-empty string")
    if not isinstance(decision.get("next_action"), str) or not decision.get(
        "next_action"
    ):
        failures.append("decision.next_action must be a non-empty string")


def validate_contract_receipt(receipt: Mapping[str, Any]) -> list[str]:
    """Return receipt-shape failures. This is a JSON-level check, not Lean."""

    failures: list[str] = []
    extra_keys = sorted(str(key) for key in receipt if key not in RECEIPT_TOP_LEVEL_KEYS)
    if extra_keys:
        failures.append(
            "receipt contains unsupported keys: " + ", ".join(extra_keys)
        )
    if receipt.get("schema_id") != RECEIPT_SCHEMA_ID:
        failures.append(f"schema_id must be {RECEIPT_SCHEMA_ID!r}")
    if receipt.get("request_schema_id") != REQUEST_SCHEMA_ID:
        failures.append(f"request_schema_id must be {REQUEST_SCHEMA_ID!r}")
    if receipt.get("contract_pack_schema_id") != CONTRACT_PACK_SCHEMA_ID:
        failures.append(f"contract_pack_schema_id must be {CONTRACT_PACK_SCHEMA_ID!r}")
    kind = receipt.get("kind")
    if kind not in SUPPORTED_CONTRACT_KINDS:
        failures.append("kind must be a supported Circle AI contract kind")
    status = receipt.get("status")
    if status not in STATUS_VALUES:
        failures.append("status must be one of " + ", ".join(STATUS_VALUES))
    request_passed = receipt.get("request_passed")
    if (
        request_passed is not True
        and request_passed is not False
        and request_passed is not None
    ):
        failures.append("request_passed must be true, false, or null")
    if receipt.get("content_fingerprint_algorithm") != FINGERPRINT_ALGORITHM:
        failures.append(
            f"content_fingerprint_algorithm must be {FINGERPRINT_ALGORITHM!r}"
        )
    fingerprint = receipt.get("receipt_content_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        failures.append("receipt_content_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in fingerprint):
        failures.append("receipt_content_fingerprint must be lowercase hex")
    elif fingerprint != _json_fingerprint(dict(receipt)):
        failures.append("receipt_content_fingerprint drifted from receipt content")
    request = receipt.get("request")
    if not isinstance(request, dict):
        failures.append("request must be an object")
    else:
        for failure in validate_contract_request(request):
            failures.append("request: " + failure)
        request_kind = request.get("kind")
        if isinstance(kind, str) and isinstance(request_kind, str):
            try:
                request_canonical = canonical_contract_kind(request_kind)
            except ValueError:
                request_canonical = None
            if request_canonical is not None and request_canonical != kind:
                failures.append("request.kind must match receipt kind")
    request_fingerprint = receipt.get("request_content_fingerprint")
    if not isinstance(request_fingerprint, str) or len(request_fingerprint) != 64:
        failures.append("request_content_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in request_fingerprint):
        failures.append("request_content_fingerprint must be lowercase hex")
    elif isinstance(request, dict) and request_fingerprint != _json_fingerprint(request):
        failures.append("request_content_fingerprint drifted from request content")
    normalized = receipt.get("normalized_request")
    if not isinstance(normalized, dict) or not normalized:
        failures.append("normalized_request must be a non-empty object")
    normalized_fingerprint = receipt.get("normalized_request_fingerprint")
    if not isinstance(normalized_fingerprint, str) or len(normalized_fingerprint) != 64:
        failures.append("normalized_request_fingerprint must be a sha256 hex string")
    elif any(char not in "0123456789abcdef" for char in normalized_fingerprint):
        failures.append("normalized_request_fingerprint must be lowercase hex")
    elif isinstance(normalized, dict) and normalized_fingerprint != _json_fingerprint(
        normalized
    ):
        failures.append(
            "normalized_request_fingerprint drifted from normalized_request content"
        )
    evidence = receipt.get("evidence")
    if not isinstance(evidence, dict) or not evidence:
        failures.append("evidence must be a non-empty object")
    proof_layers = receipt.get("proof_layers")
    if not isinstance(proof_layers, dict):
        failures.append("proof_layers must be an object")
    else:
        field_buckets: dict[str, list[str]] = {}
        for bucket in PROOF_LAYER_BUCKETS:
            fields = proof_layers.get(bucket)
            if not isinstance(fields, list):
                failures.append(f"proof_layers.{bucket} must be a list")
            elif not all(isinstance(field, str) and field for field in fields):
                failures.append(
                    f"proof_layers.{bucket} must contain non-empty strings"
                )
            else:
                duplicate_fields = _duplicate_strings(fields)
                if duplicate_fields:
                    failures.append(
                        f"proof_layers.{bucket} must not contain duplicates: "
                        + ", ".join(duplicate_fields)
                    )
                for field in fields:
                    field_buckets.setdefault(field, []).append(bucket)
        for field, buckets in sorted(field_buckets.items()):
            if len(buckets) > 1:
                failures.append(
                    "proof layer field appears in multiple buckets: "
                    f"{field} in {', '.join(buckets)}"
                )
    proof_status = receipt.get("proof_status")
    if not isinstance(proof_status, dict):
        failures.append("proof_status must be an object")
    else:
        theorem_ids = proof_status.get("theorem_ids")
        if not isinstance(theorem_ids, list) or not theorem_ids:
            failures.append("proof_status.theorem_ids must be a non-empty list")
        elif _duplicate_strings(theorem_ids):
            failures.append(
                "proof_status.theorem_ids must not contain duplicates: "
                + ", ".join(_duplicate_strings(theorem_ids))
            )
        theorem_count = proof_status.get("theorem_count")
        if not isinstance(theorem_count, int):
            failures.append("proof_status.theorem_count must be an integer")
        elif isinstance(theorem_ids, list) and theorem_count != len(theorem_ids):
            failures.append(
                "proof_status.theorem_count must equal len(theorem_ids)"
            )
        if proof_status.get("all_theorem_ids_resolved") is not True:
            failures.append("all receipt theorem ids must resolve in the contract pack")
        for key in ("unresolved_theorem_ids", "unproved_theorem_ids"):
            value = proof_status.get(key)
            if isinstance(value, list) and _duplicate_strings(value):
                failures.append(
                    f"proof_status.{key} must not contain duplicates: "
                    + ", ".join(_duplicate_strings(value))
                )
        if status in {"proved", "impossible"} and proof_status.get(
            "all_theorem_ids_proved"
        ) is not True:
            failures.append("proved/impossible receipts require proved theorem ids")
    _validate_decision_block(
        decision=receipt.get("decision"),
        receipt=receipt,
        proof_status=proof_status,
        proof_layers=proof_layers,
        failures=failures,
    )
    support = receipt.get("support")
    if not isinstance(support, dict):
        failures.append("support must be an object")
    else:
        if not support.get("contract_id"):
            failures.append("support.contract_id must be present")
        elif receipt.get("contract_id") != support.get("contract_id"):
            failures.append("support.contract_id must match receipt contract_id")
        if support.get("ready_for_downstream_fixture_use") is not True:
            failures.append("support.ready_for_downstream_fixture_use must be true")
        if not support.get("contract_pack_fingerprint"):
            failures.append("support.contract_pack_fingerprint must be present")
        if not support.get("contract_content_fingerprint"):
            failures.append("support.contract_content_fingerprint must be present")
        contract_theorem_ids = support.get("contract_theorem_ids")
        contract_theorem_count = support.get("contract_theorem_count")
        if (
            isinstance(contract_theorem_ids, list)
            and isinstance(contract_theorem_count, int)
            and contract_theorem_count != len(contract_theorem_ids)
        ):
            failures.append(
                "support.contract_theorem_count must equal "
                "len(contract_theorem_ids)"
            )
        if isinstance(contract_theorem_ids, list) and _duplicate_strings(
            contract_theorem_ids
        ):
            failures.append(
                "support.contract_theorem_ids must not contain duplicates: "
                + ", ".join(_duplicate_strings(contract_theorem_ids))
            )
    recommendations = receipt.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        failures.append("recommendations must be a non-empty list")
    elif not all(isinstance(recommendation, dict) for recommendation in recommendations):
        failures.append("recommendations must contain objects")
    elif (
        isinstance(support, dict)
        and isinstance(support.get("planner_recommendations"), list)
        and recommendations != support["planner_recommendations"]
    ):
        failures.append("recommendations must match support.planner_recommendations")
    validation_commands = receipt.get("validation_commands")
    if not isinstance(validation_commands, list) or not validation_commands:
        failures.append("validation_commands must be a non-empty list")
    elif not all(isinstance(command, str) and command for command in validation_commands):
        failures.append("validation_commands must contain non-empty strings")
    elif _duplicate_strings(validation_commands):
        failures.append(
            "validation_commands must not contain duplicates: "
            + ", ".join(_duplicate_strings(validation_commands))
        )
    elif (
        isinstance(support, dict)
        and isinstance(support.get("validation_commands"), list)
        and validation_commands != support["validation_commands"]
    ):
        failures.append("validation_commands must match support.validation_commands")
    elif isinstance(request, dict):
        try:
            expected_replay_command = _runner_validation_command_for_request(request)
        except (KeyError, TypeError, ValueError):
            expected_replay_command = None
        if (
            expected_replay_command is not None
            and validation_commands[0] != expected_replay_command
        ):
            failures.append(
                "validation_commands[0] must replay the embedded request"
            )
    if not isinstance(receipt.get("not_claimed"), list) or not receipt.get(
        "not_claimed"
    ):
        failures.append("not_claimed must be a non-empty list")
    else:
        not_claimed = receipt["not_claimed"]
        if not all(isinstance(claim, str) and claim for claim in not_claimed):
            failures.append("not_claimed must contain non-empty strings")
        elif _duplicate_strings(not_claimed):
            failures.append(
                "not_claimed must not contain duplicates: "
                + ", ".join(_duplicate_strings(not_claimed))
            )
    return failures


def validate_contract_receipt_against_pack(
    receipt: Mapping[str, Any],
    pack: Mapping[str, Any],
) -> list[str]:
    """Validate a saved receipt against the contract pack it claims to use.

    This does not run Lean. It checks the receipt's JSON-level invariants, then
    compares its support fingerprints, contract id, contract theorem ids, and
    proved/impossible proof-status expectations against the loaded contract
    pack.
    """

    failures = validate_contract_receipt(receipt)
    pack_failures = validate_consumer_pack(dict(pack))
    failures.extend(f"contract pack: {failure}" for failure in pack_failures)

    support = receipt.get("support")
    if not isinstance(support, dict):
        failures.append("support must be an object before pack checks can run")
        return failures

    pack_fingerprint = pack.get("pack_content_fingerprint")
    if support.get("contract_pack_fingerprint") != pack_fingerprint:
        failures.append(
            "support.contract_pack_fingerprint does not match loaded contract pack"
        )

    kind = receipt.get("kind")
    contract = find_contract(dict(pack), str(kind)) if isinstance(kind, str) else None
    if contract is None:
        failures.append("receipt kind is not present in the loaded contract pack")
        return failures

    contract_id = contract.get("id")
    if receipt.get("contract_id") != contract_id:
        failures.append("contract_id does not match loaded contract record")
    if support.get("contract_id") != contract_id:
        failures.append("support.contract_id does not match loaded contract record")

    contract_fingerprint = contract.get("content_fingerprint")
    if support.get("contract_content_fingerprint") != contract_fingerprint:
        failures.append(
            "support.contract_content_fingerprint does not match loaded contract"
        )

    fingerprint_index = pack.get("contract_fingerprint_index")
    index_entry = (
        fingerprint_index.get(kind)
        if isinstance(fingerprint_index, dict) and isinstance(kind, str)
        else None
    )
    if not isinstance(index_entry, dict):
        failures.append("loaded contract pack is missing a fingerprint-index entry")
    else:
        if index_entry.get("id") != contract_id:
            failures.append("contract fingerprint index id disagrees with contract")
        if index_entry.get("content_fingerprint") != contract_fingerprint:
            failures.append(
                "contract fingerprint index content hash disagrees with contract"
            )

    proof_status = receipt.get("proof_status")
    receipt_theorem_ids = (
        _as_string_set(proof_status.get("theorem_ids"))
        if isinstance(proof_status, dict)
        else set()
    )
    contract_theorem_ids = _as_string_set(contract.get("theorem_ids"))
    missing_from_contract = sorted(receipt_theorem_ids - contract_theorem_ids)
    if missing_from_contract:
        failures.append(
            "receipt theorem ids are not in loaded contract: "
            + ",".join(missing_from_contract)
        )

    contract_proof_status = contract.get("proof_status")
    contract_all_proved = (
        isinstance(contract_proof_status, dict)
        and contract_proof_status.get("all_theorem_ids_resolved") is True
        and contract_proof_status.get("all_theorem_ids_proved") is True
    )
    if receipt.get("status") in {"proved", "impossible"} and not contract_all_proved:
        failures.append("proved/impossible receipt requires proved contract theorems")

    return failures


def _validate_receipt_gate_policy(
    *,
    required_statuses: Sequence[str],
    required_decision_verdicts: Sequence[str],
    required_assurance_levels: Sequence[str],
) -> None:
    unsupported_statuses = [
        status for status in required_statuses if status not in STATUS_VALUES
    ]
    if unsupported_statuses:
        raise ValueError(
            "required_statuses contains unsupported statuses: "
            + ", ".join(str(status) for status in unsupported_statuses)
        )
    unsupported_verdicts = [
        verdict
        for verdict in required_decision_verdicts
        if verdict not in DECISION_VERDICTS
    ]
    if unsupported_verdicts:
        raise ValueError(
            "required_decision_verdicts contains unsupported verdicts: "
            + ", ".join(str(verdict) for verdict in unsupported_verdicts)
        )
    unsupported_assurance_levels = [
        level
        for level in required_assurance_levels
        if level not in DECISION_ASSURANCE_LEVELS
    ]
    if unsupported_assurance_levels:
        raise ValueError(
            "required_assurance_levels contains unsupported assurance levels: "
            + ", ".join(str(level) for level in unsupported_assurance_levels)
        )


def _receipt_gate_policy(
    *,
    required_statuses: Sequence[str],
    required_decision_verdicts: Sequence[str],
    required_assurance_levels: Sequence[str],
    require_passed: bool,
) -> dict[str, Any]:
    return {
        "allowed_statuses": list(required_statuses),
        "allowed_decision_verdicts": list(required_decision_verdicts),
        "allowed_assurance_levels": list(required_assurance_levels),
        "require_passed": require_passed,
    }


def _dependency_pin_policy_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    normalized_param_pin = {
        "type": "object",
        "required": ["key", "value"],
        "properties": {
            "key": {"type": "string", "minLength": 1},
            "value": {},
        },
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "required": [
            "required_kinds",
            "required_theorem_ids",
            "required_evidence_fields",
            "required_recommendation_ids",
            "required_validation_commands",
            "required_model_config_fingerprints",
            "required_architecture_config_fingerprints",
            "required_normalized_params",
        ],
        "properties": {
            "required_kinds": string_list,
            "required_theorem_ids": string_list,
            "required_evidence_fields": string_list,
            "required_recommendation_ids": string_list,
            "required_validation_commands": string_list,
            "required_model_config_fingerprints": string_list,
            "required_architecture_config_fingerprints": string_list,
            "required_normalized_params": {
                "type": "array",
                "items": normalized_param_pin,
            },
        },
        "additionalProperties": False,
    }


def _dependency_pin_policy(
    *,
    required_kinds: Sequence[str] = (),
    required_theorem_ids: Sequence[str] = (),
    required_evidence_fields: Sequence[str] = (),
    required_recommendation_ids: Sequence[str] = (),
    required_validation_commands: Sequence[str] = (),
    required_model_config_fingerprints: Sequence[str] = (),
    required_architecture_config_fingerprints: Sequence[str] = (),
    required_normalized_params: Sequence[tuple[str, Any]] = (),
) -> dict[str, Any]:
    return {
        "required_kinds": list(required_kinds),
        "required_theorem_ids": list(required_theorem_ids),
        "required_evidence_fields": list(required_evidence_fields),
        "required_recommendation_ids": list(required_recommendation_ids),
        "required_validation_commands": list(required_validation_commands),
        "required_model_config_fingerprints": list(
            required_model_config_fingerprints
        ),
        "required_architecture_config_fingerprints": list(
            required_architecture_config_fingerprints
        ),
        "required_normalized_params": [
            {"key": key, "value": value} for key, value in required_normalized_params
        ],
    }


def _contract_runner_check_source_path(
    source_paths: Sequence[str],
    index: int,
    fallback_prefix: str,
) -> str:
    if index < len(source_paths):
        value = str(source_paths[index])
        if value:
            return value
    return f"<{fallback_prefix}:{index + 1}>"


def _contract_runner_check_summary_from_receipt(
    *,
    source_type: str,
    source_path: str,
    source: Mapping[str, Any],
    receipt: Mapping[str, Any],
    model_config_parameter_sources: Mapping[str, Any] | None = None,
    architecture_config_parameter_sources: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    compact_receipt = build_compact_contract_receipt(receipt)
    decision = receipt["decision"]
    selected_evidence_layers = compact_receipt["selected_evidence_proof_layers"]
    return {
        "source_type": source_type,
        "source_path": source_path,
        "source_content_fingerprint": _json_fingerprint(_json_ready_value(source)),
        "request_path": None,
        "model_config_import_report_path": None,
        "model_config_parameter_sources": (
            None
            if model_config_parameter_sources is None
            else _json_ready_value(model_config_parameter_sources)
        ),
        "architecture_config_import_report_path": None,
        "architecture_config_parameter_sources": (
            None
            if architecture_config_parameter_sources is None
            else _json_ready_value(architecture_config_parameter_sources)
        ),
        "request_validation_report_path": None,
        "certification_bundle_path": None,
        "certification_bundle_check_path": None,
        "receipt_path": None,
        "compact_receipt_path": None,
        "kind": receipt["kind"],
        "status": receipt["status"],
        "request_passed": receipt["request_passed"],
        "decision_verdict": decision["verdict"],
        "decision_assurance": decision["assurance"],
        "theorem_count": receipt["proof_status"]["theorem_count"],
        "recommendation_count": len(receipt["recommendations"]),
        "validation_command_count": len(receipt["validation_commands"]),
        "normalized_request": receipt["normalized_request"],
        "request_content_fingerprint": receipt["request_content_fingerprint"],
        "normalized_request_fingerprint": receipt["normalized_request_fingerprint"],
        "receipt_content_fingerprint": receipt["receipt_content_fingerprint"],
        "compact_selected_evidence_count": len(compact_receipt["selected_evidence"]),
        "compact_selected_evidence_unclassified_count": sum(
            1
            for label in selected_evidence_layers.values()
            if label == "unclassified"
        ),
        "compact_selected_evidence_labels": sorted(
            set(selected_evidence_layers.values())
        ),
    }


def _append_contract_runner_check_gate_failures(
    *,
    source_path: str,
    receipt: Mapping[str, Any],
    failures: list[str],
    required_statuses: Sequence[str],
    required_decision_verdicts: Sequence[str],
    required_assurance_levels: Sequence[str],
    require_passed: bool,
) -> None:
    if required_statuses and receipt.get("status") not in set(required_statuses):
        failures.append(
            f"{source_path}: receipt status {receipt.get('status')!r} "
            f"is not in {tuple(required_statuses)!r}"
        )
    decision = receipt.get("decision")
    if not isinstance(decision, Mapping):
        decision = {}
    if (
        required_decision_verdicts
        and decision.get("verdict") not in set(required_decision_verdicts)
    ):
        failures.append(
            f"{source_path}: receipt decision.verdict "
            f"{decision.get('verdict')!r} is not in "
            f"{tuple(required_decision_verdicts)!r}"
        )
    if (
        required_assurance_levels
        and decision.get("assurance") not in set(required_assurance_levels)
    ):
        failures.append(
            f"{source_path}: receipt decision.assurance "
            f"{decision.get('assurance')!r} is not in "
            f"{tuple(required_assurance_levels)!r}"
        )
    if require_passed and receipt.get("request_passed") is not True:
        failures.append(f"{source_path}: receipt request_passed is not true")


def build_contract_runner_check_report(
    *,
    requests: Sequence[Mapping[str, Any]] = (),
    model_configs: Sequence[Mapping[str, Any]] = (),
    architecture_configs: Sequence[Mapping[str, Any]] = (),
    pack: Mapping[str, Any] | None = None,
    request_source_paths: Sequence[str] = (),
    model_config_source_paths: Sequence[str] = (),
    architecture_config_source_paths: Sequence[str] = (),
    architecture_config_kinds: Sequence[str] = (),
    head_dim: int | None = None,
    base: float | None = None,
    context: int | None = None,
    tolerance: float | None = None,
    discretization: str | None = None,
    requested_margin: str | None = None,
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Build a schema-valid batch runner report from in-memory inputs.

    This is the public Python API equivalent of the installed
    ``circle-ai-certify batch`` command for callers that already loaded request
    objects, standard-RoPE model configs, or non-RoPE architecture configs. It
    returns summaries and gate failures; it does not write receipts or sidecar
    files.
    """

    _validate_receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
    )
    pack_dict = build_contract_pack() if pack is None else pack
    summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    selected_kinds: set[str] = set()
    selected_architecture_kinds = tuple(
        architecture_config_kinds
        or ("kv-cache", "sparse-attention", "recurrence")
    )

    for index, request in enumerate(requests):
        source_path = _contract_runner_check_source_path(
            request_source_paths,
            index,
            "request",
        )
        try:
            receipt = build_validated_contract_receipt_from_request(
                request,
                pack=pack_dict,
            )
            selected_kinds.add(str(receipt["kind"]))
            summaries.append(
                _contract_runner_check_summary_from_receipt(
                    source_type="request",
                    source_path=source_path,
                    source=request,
                    receipt=receipt,
                )
            )
            _append_contract_runner_check_gate_failures(
                source_path=source_path,
                receipt=receipt,
                failures=failures,
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
        except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{source_path}: {exc}")

    for index, model_config in enumerate(model_configs):
        source_path = _contract_runner_check_source_path(
            model_config_source_paths,
            index,
            "model_config",
        )
        try:
            import_report = build_rope_model_config_import_report(
                model_config,
                head_dim=head_dim,
                base=base,
                context=context,
                tolerance=tolerance,
                discretization=discretization,
                requested_margin=requested_margin,
            )
            if not import_report["ok"]:
                failures.append(
                    f"{source_path}: " + "; ".join(import_report["failures"])
                )
                continue
            receipt = build_validated_rope_receipt_from_model_config(
                model_config,
                head_dim=head_dim,
                base=base,
                context=context,
                tolerance=tolerance,
                discretization=discretization,
                requested_margin=requested_margin,
                pack=pack_dict,
            )
            selected_kinds.add(str(receipt["kind"]))
            summaries.append(
                _contract_runner_check_summary_from_receipt(
                    source_type="model_config",
                    source_path=source_path,
                    source=model_config,
                    receipt=receipt,
                    model_config_parameter_sources=import_report[
                        "parameter_sources"
                    ],
                )
            )
            _append_contract_runner_check_gate_failures(
                source_path=source_path,
                receipt=receipt,
                failures=failures,
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
        except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{source_path}: {exc}")

    for index, architecture_config in enumerate(architecture_configs):
        source_path = _contract_runner_check_source_path(
            architecture_config_source_paths,
            index,
            "architecture_config",
        )
        for architecture_kind in selected_architecture_kinds:
            try:
                import_report = build_architecture_config_import_report(
                    architecture_kind,
                    architecture_config,
                )
                if not import_report["ok"]:
                    failures.append(
                        f"{source_path}:{architecture_kind}: "
                        + "; ".join(import_report["failures"])
                    )
                    continue
                request = import_report["request"]
                if not isinstance(request, Mapping):
                    failures.append(
                        f"{source_path}:{architecture_kind}: architecture "
                        "config import report did not emit a request"
                    )
                    continue
                receipt = build_validated_contract_receipt_from_request(
                    request,
                    pack=pack_dict,
                )
                selected_kinds.add(str(receipt["kind"]))
                summaries.append(
                    _contract_runner_check_summary_from_receipt(
                        source_type="architecture_config",
                        source_path=source_path,
                        source=architecture_config,
                        receipt=receipt,
                        architecture_config_parameter_sources=import_report[
                            "parameter_sources"
                        ],
                    )
                )
                _append_contract_runner_check_gate_failures(
                    source_path=f"{source_path}:{architecture_kind}",
                    receipt=receipt,
                    failures=failures,
                    required_statuses=required_statuses,
                    required_decision_verdicts=required_decision_verdicts,
                    required_assurance_levels=required_assurance_levels,
                    require_passed=require_passed,
                )
            except (
                ValueError,
                jsonschema.ValidationError,
                jsonschema.SchemaError,
            ) as exc:
                failures.append(f"{source_path}:{architecture_kind}: {exc}")

    report = {
        "schema_id": RUNNER_CHECK_SCHEMA_ID,
        "ok": not failures,
        "example_count": len(summaries),
        "failure_count": len(failures),
        "failures": failures,
        "selected_kinds": sorted(selected_kinds),
        "gate_policy": _receipt_gate_policy(
            required_statuses=required_statuses,
            required_decision_verdicts=required_decision_verdicts,
            required_assurance_levels=required_assurance_levels,
            require_passed=require_passed,
        ),
        "summaries": summaries,
    }
    jsonschema.validate(report, build_contract_runner_check_json_schema())
    return report


def build_contract_receipt_file_check_report(
    receipt: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    receipt_path: str,
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Build a saved-receipt validation report with the public report shape.

    This is the public API equivalent of ``scripts/check_circle_ai_receipt.py``
    for callers that already have a receipt object in memory.
    """

    if not isinstance(receipt_path, str) or not receipt_path:
        raise ValueError("receipt_path must be a non-empty string")
    _validate_receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
    )
    failures = validate_contract_receipt_against_pack(receipt, pack)
    status = receipt.get("status")
    if required_statuses and status not in set(required_statuses):
        failures.append(
            f"receipt status {status!r} did not match required status set: "
            + ", ".join(required_statuses)
        )
    decision = receipt.get("decision")
    decision_verdict = decision.get("verdict") if isinstance(decision, Mapping) else None
    decision_assurance = (
        decision.get("assurance") if isinstance(decision, Mapping) else None
    )
    if required_decision_verdicts and decision_verdict not in set(
        required_decision_verdicts
    ):
        failures.append(
            f"receipt decision verdict {decision_verdict!r} did not match "
            "required decision set: "
            + ", ".join(required_decision_verdicts)
        )
    if required_assurance_levels and decision_assurance not in set(
        required_assurance_levels
    ):
        failures.append(
            f"receipt assurance {decision_assurance!r} did not match "
            "required assurance set: "
            + ", ".join(required_assurance_levels)
        )
    if require_passed and receipt.get("request_passed") is not True:
        failures.append(
            "receipt request_passed was not true "
            f"(got {receipt.get('request_passed')!r})"
        )
    support = receipt.get("support")
    support_map = support if isinstance(support, Mapping) else {}
    receipt_theorem_ids = _receipt_artifact_theorem_ids(receipt)
    receipt_evidence_fields = _receipt_artifact_evidence_fields(receipt)
    receipt_recommendation_ids = _receipt_artifact_recommendation_ids(receipt)
    receipt_validation_commands = _receipt_artifact_validation_commands(receipt)
    report = {
        "schema_id": RECEIPT_FILE_CHECK_SCHEMA_ID,
        "ok": not failures,
        "receipt_count": 1,
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": _receipt_gate_policy(
            required_statuses=required_statuses,
            required_decision_verdicts=required_decision_verdicts,
            required_assurance_levels=required_assurance_levels,
            require_passed=require_passed,
        ),
        "pin_policy": _dependency_pin_policy(),
        "summaries": [
            {
                "path": receipt_path,
                "kind": receipt.get("kind"),
                "contract_id": receipt.get("contract_id"),
                "content_fingerprint_algorithm": receipt.get(
                    "content_fingerprint_algorithm"
                ),
                "contract_pack_fingerprint": support_map.get(
                    "contract_pack_fingerprint"
                ),
                "contract_content_fingerprint": support_map.get(
                    "contract_content_fingerprint"
                ),
                "status": status,
                "request_passed": receipt.get("request_passed"),
                "decision_verdict": (
                    decision.get("verdict") if isinstance(decision, Mapping) else None
                ),
                "decision_assurance": (
                    decision.get("assurance") if isinstance(decision, Mapping) else None
                ),
                "theorem_count": len(receipt_theorem_ids),
                "theorem_ids": receipt_theorem_ids,
                "evidence_field_count": len(receipt_evidence_fields),
                "evidence_fields": receipt_evidence_fields,
                "recommendation_ids": receipt_recommendation_ids,
                "validation_command_count": len(receipt_validation_commands),
                "validation_commands": receipt_validation_commands,
                "normalized_request": receipt.get("normalized_request"),
                "request_content_fingerprint": receipt.get(
                    "request_content_fingerprint"
                ),
                "normalized_request_fingerprint": receipt.get(
                    "normalized_request_fingerprint"
                ),
                "receipt_content_fingerprint": receipt.get(
                    "receipt_content_fingerprint"
                ),
                "failure_count": len(failures),
            }
        ],
    }
    return report


def _receipt_replay_summary(receipt: Mapping[str, Any]) -> dict[str, Any]:
    decision = receipt.get("decision")
    decision_map = decision if isinstance(decision, Mapping) else {}
    return {
        "kind": receipt.get("kind"),
        "contract_id": receipt.get("contract_id"),
        "status": receipt.get("status"),
        "request_passed": receipt.get("request_passed"),
        "decision_verdict": decision_map.get("verdict"),
        "decision_assurance": decision_map.get("assurance"),
        "request_content_fingerprint": receipt.get("request_content_fingerprint"),
        "normalized_request_fingerprint": receipt.get(
            "normalized_request_fingerprint"
        ),
        "receipt_content_fingerprint": receipt.get("receipt_content_fingerprint"),
    }


def build_contract_receipt_replay_check_report(
    receipt: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    receipt_path: str,
) -> dict[str, Any]:
    """Rebuild a receipt from its embedded request and compare fingerprints.

    This is a deterministic stale-receipt check. It does not execute the shell
    command stored in ``validation_commands``; it rebuilds through the public
    Python request API against the supplied contract pack.
    """

    if not isinstance(receipt_path, str) or not receipt_path:
        raise ValueError("receipt_path must be a non-empty string")
    failures = validate_contract_receipt_against_pack(receipt, pack)
    request = receipt.get("request")
    replayed: dict[str, Any] | None = None
    replay_command = None
    replay_command_matches_request = False
    comparison = {
        "kind_matches": False,
        "contract_id_matches": False,
        "status_matches": False,
        "request_passed_matches": False,
        "decision_verdict_matches": False,
        "decision_assurance_matches": False,
        "request_content_fingerprint_matches": False,
        "normalized_request_fingerprint_matches": False,
        "receipt_content_fingerprint_matches": False,
        "all_replay_fields_match": False,
    }
    if not isinstance(request, Mapping):
        failures.append("receipt request must be an object before replay")
    else:
        try:
            replay_command = _runner_validation_command_for_request(request)
        except (KeyError, TypeError, ValueError) as exc:
            failures.append(f"receipt replay command could not be derived: {exc}")
        receipt_commands = receipt.get("validation_commands")
        if isinstance(receipt_commands, list) and receipt_commands:
            replay_command_matches_request = receipt_commands[0] == replay_command
            if not replay_command_matches_request:
                failures.append(
                    "receipt validation_commands[0] does not match replay command"
                )
        try:
            replayed = build_validated_contract_receipt_from_request(
                request,
                pack=pack,
            )
        except ValueError as exc:
            failures.append(f"receipt replay failed: {exc}")
    if replayed is not None:
        original_summary = _receipt_replay_summary(receipt)
        replayed_summary = _receipt_replay_summary(replayed)
        for key in (
            "kind",
            "contract_id",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
        ):
            comparison_key = f"{key}_matches"
            comparison[comparison_key] = original_summary.get(key) == (
                replayed_summary.get(key)
            )
            if not comparison[comparison_key]:
                failures.append(f"receipt replay mismatch: {key}")
        comparison["all_replay_fields_match"] = all(
            value
            for key, value in comparison.items()
            if key != "all_replay_fields_match"
        )
    else:
        original_summary = _receipt_replay_summary(receipt)
        replayed_summary = None
    return {
        "schema_id": RECEIPT_REPLAY_CHECK_SCHEMA_ID,
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "path": receipt_path,
        "replay_command": replay_command,
        "replay_command_matches_request": replay_command_matches_request,
        "original": original_summary,
        "replayed": replayed_summary,
        "comparison": comparison,
    }


def build_contract_receipt_gate_report(
    receipt: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    receipt_path: str = "<in-memory-receipt>",
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Build the public pack-aware gate report for an in-memory receipt.

    This is the Python API counterpart to ``scripts/check_circle_ai_receipt.py``.
    Downstream callers that already have a receipt object should use this helper
    instead of shelling out or treating ``decision`` as a standalone proof.
    """

    return build_contract_receipt_file_check_report(
        receipt,
        pack,
        receipt_path=receipt_path,
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
        require_passed=require_passed,
    )


def require_contract_receipt_gate(
    receipt: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    receipt_path: str = "<in-memory-receipt>",
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Return a gate report or raise ``ValueError`` with its failures."""

    report = build_contract_receipt_gate_report(
        receipt,
        pack,
        receipt_path=receipt_path,
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
        require_passed=require_passed,
    )
    if report["ok"]:
        return report
    raise ValueError(
        "Circle AI contract receipt gate failed: " + "; ".join(report["failures"])
    )


def build_contract_certification_bundle(
    request: Mapping[str, Any],
    *,
    pack: Mapping[str, Any] | None = None,
    model_config_import_report: Mapping[str, Any] | None = None,
    architecture_config_import_report: Mapping[str, Any] | None = None,
    receipt_path: str = "<in-memory-receipt>",
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Return request validation, receipt, and gate report in one public shape.

    The bundle is the Python API counterpart to running
    ``circle_ai_certify.py`` with request preflight and a receipt gate. When the
    request came from a RoPE model config or non-RoPE architecture config,
    callers may include the matching import report so the bundle carries the
    config-to-request provenance too.
    Invalid requests return a failed bundle with ``receipt = None`` instead of
    forcing downstream callers to catch an exception just to see validation
    failures. Invalid gate-policy values still raise ``ValueError`` because
    that is a caller bug rather than a property of the request being certified.
    """

    _validate_receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
    )
    request_validation_report = build_contract_request_validation_report(request)
    gate_policy = _receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
        require_passed=require_passed,
    )
    failures = [
        f"request validation failed: {failure}"
        for failure in request_validation_report["failures"]
    ]
    receipt: dict[str, Any] | None = None
    gate_report: dict[str, Any] | None = None
    import_report = (
        None
        if model_config_import_report is None
        else dict(model_config_import_report)
    )
    architecture_import_report = (
        None
        if architecture_config_import_report is None
        else dict(architecture_config_import_report)
    )

    if import_report is not None:
        if import_report.get("schema_id") != ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID:
            failures.append(
                "model config import report schema_id must be "
                f"{ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID}"
            )
        if import_report.get("request_schema_id") != REQUEST_SCHEMA_ID:
            failures.append(
                "model config import report request_schema_id must be "
                f"{REQUEST_SCHEMA_ID}"
            )
        if import_report.get("kind") != "rope_position_distinguishability":
            failures.append(
                "model config import report kind must be "
                "rope_position_distinguishability"
            )
        if import_report.get("ok") is not True:
            report_failures = import_report.get("failures", ())
            if isinstance(report_failures, (list, tuple)):
                detail = "; ".join(str(failure) for failure in report_failures)
            else:
                detail = str(report_failures)
            failures.append(
                "model config import report failed"
                + (f": {detail}" if detail else "")
            )
        if (
            import_report.get("request_content_fingerprint")
            != request_validation_report["request_content_fingerprint"]
        ):
            failures.append(
                "model config import report request_content_fingerprint does "
                "not match the bundled request"
            )

    if architecture_import_report is not None:
        if (
            architecture_import_report.get("schema_id")
            != ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID
        ):
            failures.append(
                "architecture config import report schema_id must be "
                f"{ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID}"
            )
        if architecture_import_report.get("request_schema_id") != REQUEST_SCHEMA_ID:
            failures.append(
                "architecture config import report request_schema_id must be "
                f"{REQUEST_SCHEMA_ID}"
            )
        kind = architecture_import_report.get("kind")
        if kind not in ARCHITECTURE_CONFIG_SUPPORTED_KINDS:
            failures.append(
                "architecture config import report kind must be one of "
                f"{list(ARCHITECTURE_CONFIG_SUPPORTED_KINDS)!r}"
            )
        if architecture_import_report.get("ok") is not True:
            report_failures = architecture_import_report.get("failures", ())
            if isinstance(report_failures, (list, tuple)):
                detail = "; ".join(str(failure) for failure in report_failures)
            else:
                detail = str(report_failures)
            failures.append(
                "architecture config import report failed"
                + (f": {detail}" if detail else "")
            )
        if (
            architecture_import_report.get("request_content_fingerprint")
            != request_validation_report["request_content_fingerprint"]
        ):
            failures.append(
                "architecture config import report request_content_fingerprint "
                "does not match the bundled request"
            )

    if request_validation_report["ok"]:
        pack_dict = _default_pack(pack)
        try:
            receipt = build_validated_contract_receipt_from_request(
                request,
                pack=pack_dict,
            )
            gate_report = build_contract_receipt_gate_report(
                receipt,
                pack_dict,
                receipt_path=receipt_path,
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
            failures.extend(gate_report["failures"])
        except ValueError as exc:
            failures.append(str(exc))

    return {
        "schema_id": CERTIFICATION_BUNDLE_SCHEMA_ID,
        "request_schema_id": REQUEST_SCHEMA_ID,
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "gate_report_schema_id": RECEIPT_FILE_CHECK_SCHEMA_ID,
        "model_config_import_report_schema_id": ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID,
        "architecture_config_import_report_schema_id": (
            ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID
        ),
        "content_fingerprint_algorithm": FINGERPRINT_ALGORITHM,
        "ok": not failures,
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": gate_policy,
        "request_content_fingerprint": request_validation_report[
            "request_content_fingerprint"
        ],
        "normalized_request_fingerprint": (
            None if receipt is None else receipt["normalized_request_fingerprint"]
        ),
        "receipt_content_fingerprint": (
            None if receipt is None else receipt["receipt_content_fingerprint"]
        ),
        "request_validation_report": request_validation_report,
        "receipt": receipt,
        "gate_report": gate_report,
        "model_config_import_report": import_report,
        "architecture_config_import_report": architecture_import_report,
    }


def receipt_summary_lines(receipt: Mapping[str, Any]) -> list[str]:
    """Return a compact text summary for humans."""

    proof_status = receipt["proof_status"]
    support = receipt["support"]
    lines = [
        (
            "circle_ai_contract_receipt="
            f"{receipt['status']} kind={receipt['kind']} "
            f"contract_id={receipt['contract_id']} "
            f"request_passed={receipt['request_passed']}"
        ),
        (
            "proof_status="
            f"theorems={proof_status['theorem_count']} "
            f"resolved={proof_status['all_theorem_ids_resolved']} "
            f"proved={proof_status['all_theorem_ids_proved']} "
            f"unresolved={len(proof_status['unresolved_theorem_ids'])} "
            f"unproved={len(proof_status['unproved_theorem_ids'])}"
        ),
        (
            "support="
            f"ready={support['ready_for_downstream_fixture_use']} "
            f"pack_fingerprint={str(support['contract_pack_fingerprint'])[:12]} "
            f"contract_fingerprint={str(support['contract_content_fingerprint'])[:12]}"
        ),
        (
            "request_fingerprints="
            f"request={str(receipt['request_content_fingerprint'])[:12]} "
            f"normalized={str(receipt['normalized_request_fingerprint'])[:12]}"
        ),
        (
            "runner_metadata="
            f"recommendations={len(receipt['recommendations'])} "
            f"validation_commands={len(receipt['validation_commands'])}"
        ),
    ]
    proof_layers = receipt["proof_layers"]
    lines.append(
        "proof_layers="
        f"proved_fields={len(proof_layers['proved_fields'])} "
        f"computed_fields={len(proof_layers['computed_fields'])} "
        f"numerical_only_fields={len(proof_layers['numerical_only_fields'])} "
        f"unsupported_fields={len(proof_layers['unsupported_fields'])}"
    )
    decision = receipt["decision"]
    lines.append(
        "decision="
        f"verdict={decision['verdict']} "
        f"assurance={decision['assurance']} "
        f"claim_status={decision['claim_status']} "
        f"request_passed={decision['request_passed']}"
    )
    evidence = receipt["evidence"]
    kind = receipt["kind"]
    if kind == "rope_position_distinguishability":
        lines.append(
            "rope_exact_discrete="
            f"pass={evidence['exact_discrete_pass']} "
            f"collision_pairs={evidence['exact_total_bank_collision_pair_count']} "
            f"common_gap={evidence['exact_common_collision_gap']}"
        )
        lines.append(
            "rope_real_phase_scan="
            f"numerical_pass={evidence['real_phase_numerical_pass_margin']} "
            f"worst_gap={evidence['real_phase_numerical_worst_gap']} "
            f"worst_margin={evidence['real_phase_numerical_worst_margin_radians']}"
        )
        classifier = evidence.get("standard_channel0_d19_request_classifier")
        if isinstance(classifier, dict):
            lines.append(
                "rope_d19_request="
                f"status={classifier['request_status']} "
                f"theorem_backed={classifier['theorem_backed_classification']} "
                f"margin={classifier['requested_margin']} "
                f"context={classifier['requested_context']}"
            )
        bank_bridge = evidence.get("standard_channel0_d19_bank_bridge")
        if isinstance(bank_bridge, dict):
            lines.append(
                "rope_d19_bank_bridge="
                f"applies={bank_bridge['applies']} "
                f"theorem_backed={bank_bridge['theorem_backed']} "
                f"radian_bank_form={bank_bridge['radian_bank_form']} "
                f"bank_shape={bank_bridge['bank_shape']} "
                f"status={bank_bridge['request_status']}"
            )
        guardrail = evidence.get("real_phase_dirichlet_guardrail")
        if isinstance(guardrail, dict):
            lines.append(
                "rope_dirichlet_guardrail="
                f"applies={guardrail['applies']} "
                f"inv_context_margin={guardrail['inv_context_margin']} "
                "requested_relation="
                f"{guardrail['requested_margin_relation_to_ceiling']} "
                f"exceeds_ceiling={guardrail['requested_margin_exceeds_ceiling']}"
            )
    elif kind == "kv_cache_ring_buffer":
        window = evidence["window_certificate"]
        adapter = evidence["adapter_request_trace_certificate"]
        live = evidence["live_window_certificate"]
        lines.append(
            "kv_cache_window="
            f"retained={window['retained']} slot={window['slot']} "
            f"lag={window['lag']} next_overwrite={window['next_overwrite_token']}"
        )
        lines.append(
            "kv_cache_request="
            f"pass={adapter['pass_certificate']} "
            f"stale_count={adapter['stale_requested_count']} "
            f"first_stale_token={adapter['first_stale_token']}"
        )
        lines.append(
            "kv_cache_live_window="
            f"full_coverage={live['full_coverage_contract']} "
            f"start={live['start']} length={live['length']}"
        )
        sink = evidence.get("sink_window_certificate")
        if isinstance(sink, dict):
            lines.append(
                "kv_cache_sink_window="
                f"sink_size={sink['sink_size']} "
                f"token_count={sink['token_count']} "
                f"token_bound={sink['token_count_bound']} "
                f"exact_policy={sink['generated_tokens_exact_policy']} "
                f"tokens_distinct={sink['tokens_distinct']} "
                "sink_tokens_retained="
                f"{sink['sink_tokens_retained_by_policy']} "
                "sink_tokens_outside_rolling="
                f"{sink['sink_tokens_outside_ordinary_rolling_window']}"
            )
    elif kind == "sparse_attention_coverage":
        lines.append(
            "sparse_attention="
            f"coverage_complete={evidence['coverage_complete']} "
            f"covered={evidence['covered_lag_count']} "
            f"uncovered={evidence['uncovered_lag_count']} "
            f"first_gap={evidence['first_uncovered_lag']}"
        )
        lines.append(
            "sparse_repair="
            f"complete_repair_window={evidence['complete_repair_window']} "
            "complete_additional_slots="
            f"{evidence['complete_repair_window_additional_local_slots']} "
            "complete_covers_context="
            f"{evidence['complete_repair_window_covers_context']} "
            "complete_minimal="
            f"{evidence['complete_repair_window_minimal_for_declared_stride_family']} "
            "complete_witness_lag="
            f"{evidence['complete_repair_window_minimal_witness_lag']}"
        )
        lines.append(
            "sparse_intervals="
            f"interval_count={evidence['uncovered_lag_interval_count']} "
            "first="
            f"{evidence['first_uncovered_lag_interval_start']}-"
            f"{evidence['first_uncovered_lag_interval_stop']} "
            f"first_len={evidence['first_uncovered_lag_interval_length']} "
            "largest="
            f"{evidence['largest_uncovered_interval_start']}-"
            f"{evidence['largest_uncovered_interval_stop']} "
            f"largest_len={evidence['largest_uncovered_interval_length']} "
            f"largest_is_tail={evidence['largest_uncovered_interval_is_tail']}"
        )
        lines.append(
            "sparse_interval_repair="
            "first_window="
            f"{evidence['first_uncovered_lag_interval_repair_window']} "
            "first_reaches_interval="
            f"{evidence['first_uncovered_interval_repair_reaches_interval']} "
            "first_next_gap="
            f"{evidence['first_interval_repair_next_uncovered_lag']} "
            "largest_window="
            f"{evidence['largest_uncovered_interval_repair_window']} "
            "largest_covers_context="
            f"{evidence['largest_interval_repair_covers_context']}"
        )
        lines.append(
            "sparse_repair_plan="
            f"steps={evidence['interval_repair_plan_step_count']} "
            f"final_window={evidence['interval_repair_plan_final_window']} "
            f"covers_context={evidence['interval_repair_plan_covers_context']} "
            "strictly_progresses="
            f"{evidence['interval_repair_plan_strictly_progresses']}"
        )
        lines.append(
            "sparse_budget="
            f"raw={evidence['raw_candidate_budget_upper_bound']} "
            f"dedup_bound={evidence['deduplicated_candidate_budget_upper_bound']} "
            f"per_query={evidence['candidate_budget_per_query']} "
            f"lag_unique={evidence['theorem_side_unique_lag_candidate_count']} "
            f"lag_dedup_loss={evidence['theorem_side_lag_candidate_dedup_loss']} "
            "lag_collision_pairs="
            f"{evidence['theorem_side_lag_candidate_collision_pair_count']} "
            f"query_unique={evidence['theorem_side_unique_query_candidate_count']} "
            "query_collision_pairs="
            f"{evidence['theorem_side_query_candidate_collision_pair_count']}"
        )
        lines.append(
            "sparse_collision_accounting="
            f"lag_no_collision={evidence['theorem_side_lag_candidates_no_collision']} "
            f"lag_dedup_loss={evidence['theorem_side_lag_candidate_dedup_loss']} "
            "lag_pairs_bound_loss="
            f"{evidence['lag_collision_pair_count_bounds_dedup_loss']} "
            "lag_unique_plus_loss_eq_raw="
            f"{evidence['lag_dedup_loss_accounting_matches_raw']} "
            f"query_no_collision={evidence['theorem_side_query_candidates_no_collision']} "
            f"query_dedup_loss={evidence['theorem_side_query_candidate_dedup_loss']} "
            "query_pairs_bound_loss="
            f"{evidence['query_collision_pair_count_bounds_dedup_loss']} "
            "query_unique_plus_loss_eq_raw="
            f"{evidence['query_dedup_loss_accounting_matches_raw']}"
        )
        lines.append(
            "sparse_zero_residue="
            f"periods={evidence['stride_family_periods']} "
            f"period_thresholds={evidence['no_zero_period_thresholds']} "
            "zero_residue_steps="
            f"{evidence['stride_family_zero_residue_step_counts']} "
            f"total={evidence['stride_family_zero_residue_total_step_count']} "
            "threshold_matches_condition="
            f"{evidence['no_zero_period_threshold_matches_condition']}"
        )
    elif kind == "recurrence_schedule":
        fields = evidence["fields"]
        lines.append(
            "recurrence_schedule="
            f"loop_period={fields['loop_period']} "
            f"sample_index={fields['sample_index']} "
            f"token_count={len(fields['tokens'])} "
            f"exit_step={fields['exit_step']}"
        )
        lines.append(
            "recurrence_work="
            f"active={fields['total_active_token_work']} "
            f"inactive={fields['total_inactive_token_work']} "
            f"saving={fields['scheduled_work_saving']}"
        )
        lines.append(
            "recurrence_post_period="
            f"horizon={fields['post_period_multi_extension_horizon_steps']} "
            "extra_steps="
            f"{fields['post_period_extra_steps']} "
            "saving="
            f"{fields['post_period_multi_extension_scheduled_work_saving']} "
            "active_work_unchanged="
            f"{fields['post_period_multi_extension_active_work_unchanged']}"
        )
        lines.append(
            "recurrence_periodic_shift="
            f"base_token={fields['periodic_shift_base_token']} "
            f"passes={fields['periodic_shift_passes']} "
            f"shift={fields['periodic_shift_amount']} "
            f"shifted_token={fields['periodic_shifted_token']} "
            "required_steps_invariant="
            f"{fields['periodic_shift_required_steps_invariant']} "
            "active_at_step_invariant="
            f"{fields['periodic_shift_active_at_step_invariant']}"
        )
    elif kind == "strided_candidate_fanout":
        fields = evidence["fields"]
        lines.append(
            "strided_fanout="
            f"context_length={fields['context_length']} "
            f"stride={fields['stride']} gcd={fields['gcd']} "
            f"predicted_reach={fields['predicted_reach']} "
            f"full_coverage={fields['full_coverage']}"
        )
        lines.append(
            "strided_fanout_budget="
            f"candidate_budget={fields['candidate_budget']} "
            f"effective_budget={fields['effective_candidate_budget']} "
            f"duplicates={fields['duplicate_count']} "
            f"shortfall={fields['candidate_budget_shortfall']}"
        )
    elif kind == "cyclic_memory_residue_winding":
        fields = evidence["fields"]
        lines.append(
            "cyclic_memory="
            f"bank_size={fields['bank_size']} "
            f"event_index={fields['event_index']} "
            f"residue_slot={fields['residue_slot']} winding={fields['winding']}"
        )
        lines.append(
            "cyclic_memory_aliases="
            f"same_residue_events={fields['same_residue_events']} "
            f"same_residue_windings={fields['same_residue_windings']} "
            f"max_alias_load={fields['max_alias_load']}"
        )
    elif kind == "multicoil_phase_feature":
        fields = evidence["fields"]
        lines.append(
            "multicoil_phase="
            f"periods={fields['periods']} position={fields['position']} "
            f"phase_tuple={fields['phase_tuple']} "
            f"joint_repeat_horizon={fields['joint_repeat_horizon']}"
        )
        lines.append(
            "multicoil_relative_phase="
            f"query={fields['query_position']} key={fields['key_position']} "
            f"relative_period={fields['relative_period']} "
            f"relative_phase={fields['relative_phase']} "
            f"shifted_relative_phase={fields['shifted_relative_phase']}"
        )
    elif kind == "circulant_block_cyclic_mixer":
        fields = evidence["fields"]
        lines.append(
            "cyclic_mixer="
            f"period={fields['period']} "
            f"max_abs_dense_delta={fields['max_abs_dense_delta']} "
            f"circulant_parameters={fields['circulant_parameters']} "
            f"dense_parameters={fields['dense_parameters']}"
        )
        lines.append(
            "cyclic_mixer_block_accounting="
            f"channel_count={fields['channel_count']} "
            f"block_size={fields['block_size']} "
            f"block_cyclic_parameters={fields['block_cyclic_parameters']} "
            f"block_to_dense_ratio={fields['block_to_dense_ratio']}"
        )
    elif kind == "seed_rule_exact_regeneration":
        fields = evidence["fields"]
        lines.append(
            "seed_rule="
            f"artifact_id={fields['artifact_id']} fixture_n={fields['fixture_n']} "
            f"exact_regeneration={fields['exact_regeneration']} "
            f"generator_shorter={fields['generator_shorter']}"
        )
        lines.append(
            "seed_rule_storage="
            f"explicit_length={fields['explicit_length']} "
            f"generator_length={fields['generator_length']} "
            f"storage_saving={fields['storage_saving']} "
            f"storage_saving_positive={fields['storage_saving_positive']}"
        )
    lines.append(f"not_claimed={'; '.join(receipt['not_claimed'])}")
    return lines


_COMPACT_MISSING = object()


def _dot_path_value(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return _COMPACT_MISSING
        current = current[part]
    return current


def _compact_recommendation_ids(recommendations: Any) -> list[str]:
    if not isinstance(recommendations, Sequence) or isinstance(
        recommendations,
        (str, bytes),
    ):
        return []
    ids: list[str] = []
    for recommendation in recommendations:
        if not isinstance(recommendation, Mapping):
            continue
        value = recommendation.get("id")
        if isinstance(value, str) and value:
            ids.append(value)
    return list(_unique_strings(ids))


def _selected_evidence_proof_layer(
    path: str,
    proof_layers: Mapping[str, Any],
) -> str:
    labels: set[str] = set()
    path_prefix = f"{path}."
    for bucket, label in PROOF_LAYER_LABEL_BY_BUCKET.items():
        fields = proof_layers.get(bucket, [])
        if not isinstance(fields, Sequence) or isinstance(fields, (str, bytes)):
            continue
        for field in fields:
            if not isinstance(field, str):
                continue
            if (
                field == path
                or field.startswith(path_prefix)
                or path.startswith(f"{field}.")
            ):
                labels.add(label)
    if len(labels) == 1:
        return next(iter(labels))
    if len(labels) > 1:
        return "mixed"
    return "unclassified"


def build_compact_contract_receipt(
    receipt: Mapping[str, Any],
    *,
    evidence_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return a small downstream-consumer view of a validated full receipt.

    The compact receipt is not a replacement for the audit receipt. It exposes
    gate-friendly fields while pointing back to the full receipt fingerprint.
    """

    failures = validate_contract_receipt(receipt)
    if failures:
        raise ValueError(
            "invalid source Circle AI contract receipt: " + "; ".join(failures)
        )

    kind = str(receipt["kind"])
    proof_status = receipt["proof_status"]
    proof_layers = receipt["proof_layers"]
    evidence = receipt["evidence"]
    decision = receipt["decision"]
    support = receipt["support"]
    selected_paths = tuple(
        evidence_paths
        if evidence_paths is not None
        else COMPACT_RECEIPT_EVIDENCE_PATHS_BY_KIND.get(kind, ())
    )
    selected_evidence = {
        path: found
        for path in selected_paths
        if (found := _dot_path_value(evidence, path)) is not _COMPACT_MISSING
    }
    selected_evidence_proof_layers = {
        path: _selected_evidence_proof_layer(path, proof_layers)
        for path in selected_evidence
    }
    proof_layer_counts = {
        bucket: len(proof_layers.get(bucket, [])) for bucket in PROOF_LAYER_BUCKETS
    }
    compact = {
        "schema_id": COMPACT_RECEIPT_SCHEMA_ID,
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "kind": kind,
        "contract_id": receipt["contract_id"],
        "status": receipt["status"],
        "request_passed": receipt["request_passed"],
        "decision": {
            "schema_id": decision["schema_id"],
            "verdict": decision["verdict"],
            "assurance": decision["assurance"],
            "claim_status": decision["claim_status"],
            "request_passed": decision["request_passed"],
            "theorem_count": decision["theorem_count"],
            "all_theorem_ids_proved": decision["all_theorem_ids_proved"],
            "proof_layer_counts": dict(decision["proof_layer_counts"]),
            "summary": decision["summary"],
            "next_action": decision["next_action"],
        },
        "normalized_request": dict(receipt["normalized_request"]),
        "proof_status_summary": {
            "theorem_ids": list(proof_status["theorem_ids"]),
            "theorem_count": proof_status["theorem_count"],
            "all_theorem_ids_resolved": proof_status[
                "all_theorem_ids_resolved"
            ],
            "all_theorem_ids_proved": proof_status["all_theorem_ids_proved"],
            "unresolved_theorem_ids": list(
                proof_status["unresolved_theorem_ids"]
            ),
            "unproved_theorem_ids": list(proof_status["unproved_theorem_ids"]),
        },
        "proof_layer_counts": proof_layer_counts,
        "evidence_field_names": sorted(str(key) for key in evidence),
        "selected_evidence": selected_evidence,
        "selected_evidence_proof_layers": selected_evidence_proof_layers,
        "recommendation_ids": _compact_recommendation_ids(
            receipt["recommendations"]
        ),
        "validation_commands": list(receipt["validation_commands"]),
        "not_claimed": list(receipt["not_claimed"]),
        "fingerprints": {
            "content_fingerprint_algorithm": receipt[
                "content_fingerprint_algorithm"
            ],
            "request_content_fingerprint": receipt[
                "request_content_fingerprint"
            ],
            "normalized_request_fingerprint": receipt[
                "normalized_request_fingerprint"
            ],
            "receipt_content_fingerprint": receipt[
                "receipt_content_fingerprint"
            ],
            "contract_pack_fingerprint": support[
                "contract_pack_fingerprint"
            ],
            "contract_content_fingerprint": support[
                "contract_content_fingerprint"
            ],
        },
    }
    jsonschema.validate(compact, build_compact_contract_receipt_json_schema())
    return compact


def build_contract_request_json_schema() -> dict[str, Any]:
    rope_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "rope_position_distinguishability"
    ]
    kv_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "kv_cache_ring_buffer"
    ]
    sparse_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "sparse_attention_coverage"
    ]
    recurrence_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "recurrence_schedule"
    ]
    fanout_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "strided_candidate_fanout"
    ]
    memory_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "cyclic_memory_residue_winding"
    ]
    phase_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "multicoil_phase_feature"
    ]
    mixer_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "circulant_block_cyclic_mixer"
    ]
    seed_rule_aliases = [
        alias
        for alias, canonical in KIND_ALIASES.items()
        if canonical == "seed_rule_exact_regeneration"
    ]
    integer = {"type": "integer"}
    positive_integer = {"type": "integer", "minimum": 1}
    positive_even_integer = {"type": "integer", "minimum": 2, "multipleOf": 2}
    nonnegative_integer = {"type": "integer", "minimum": 0}
    integer_array = {
        "type": "array",
        "items": integer,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://circle-calculus.local/schemas/circle_ai_contract_request.schema.json",
        "title": "Circle AI Contract Request",
        "type": "object",
        "required": ["schema_id", "kind", "parameters"],
        "properties": {
            "schema_id": {"const": REQUEST_SCHEMA_ID},
            "kind": {"enum": sorted(KIND_ALIASES)},
            "parameters": {"type": "object", "minProperties": 0},
        },
        "oneOf": [
            {
                "properties": {
                    "kind": {"enum": sorted(rope_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "head_dim": positive_even_integer,
                            "base": {"type": "number", "exclusiveMinimum": 0},
                            "context": positive_integer,
                            "tolerance": {"type": "number", "minimum": 0},
                            "discretization": {"enum": ["round", "floor", "ceil"]},
                            "requested_margin": {"type": ["string", "null"]},
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(kv_aliases)},
                    "parameters": {
                        "type": "object",
                        "required": ["cache_size", "current", "token"],
                        "properties": {
                            "cache_size": positive_integer,
                            "current": nonnegative_integer,
                            "token": nonnegative_integer,
                            "batch_tokens": integer_array,
                            "sink_size": nonnegative_integer,
                            "request_id": {"type": "string", "minLength": 1},
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(sparse_aliases)},
                    "parameters": {
                        "type": "object",
                        "required": [
                            "context",
                            "strides",
                            "path_length",
                            "local_window",
                        ],
                        "properties": {
                            "context": positive_integer,
                            "strides": {
                                "type": "array",
                                "items": positive_integer,
                                "minItems": 1,
                            },
                            "path_length": nonnegative_integer,
                            "local_window": nonnegative_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(recurrence_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "loop_period": positive_integer,
                            "sample_index": nonnegative_integer,
                            "max_loops": positive_integer,
                            "token_count": positive_integer,
                            "selected_block_start": nonnegative_integer,
                            "selected_block_width": positive_integer,
                            "shift_passes": nonnegative_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(fanout_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "context_length": positive_integer,
                            "stride": nonnegative_integer,
                            "start_index": nonnegative_integer,
                            "path_length": positive_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(memory_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bank_size": positive_integer,
                            "event_index": nonnegative_integer,
                            "event_count": positive_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(phase_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "periods": {
                                "type": "array",
                                "items": positive_integer,
                                "minItems": 1,
                            },
                            "position": nonnegative_integer,
                            "query_position": nonnegative_integer,
                            "key_position": nonnegative_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(mixer_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "period": positive_integer,
                            "channel_count": positive_integer,
                            "block_size": positive_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
            {
                "properties": {
                    "kind": {"enum": sorted(seed_rule_aliases)},
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "n": positive_integer,
                        },
                        "additionalProperties": False,
                    },
                },
            },
        ],
        "additionalProperties": False,
    }


def build_contract_request_validation_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_request_validation.schema.json"
        ),
        "title": "Circle AI Contract Request Validation Report",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "content_fingerprint_algorithm",
            "request_content_fingerprint",
            "ok",
            "kind",
            "canonical_kind",
            "failure_count",
            "failures",
        ],
        "properties": {
            "schema_id": {"const": REQUEST_VALIDATION_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "request_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "ok": {"type": "boolean"},
            "kind": {"type": ["string", "null"]},
            "canonical_kind": {
                "type": ["string", "null"],
                "enum": [*SUPPORTED_CONTRACT_KINDS, None],
            },
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
        },
        "additionalProperties": False,
    }


def build_rope_model_config_import_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    parameter_source = {
        "type": "object",
        "required": ["source"],
        "properties": {
            "source": {
                "enum": [
                    "override",
                    "config_field",
                    "derived_config_fields",
                    "default",
                    "missing",
                    "omitted",
                ],
            },
            "field": {"type": "string", "minLength": 1},
            "fields": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "note": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_rope_model_config_import.schema.json"
        ),
        "title": "Circle AI RoPE Model Config Import Report",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "content_fingerprint_algorithm",
            "model_config_fingerprint",
            "request_content_fingerprint",
            "kind",
            "ok",
            "failure_count",
            "failures",
            "unsupported_model_config_fields",
            "parameter_sources",
            "request",
            "notes",
        ],
        "properties": {
            "schema_id": {"const": ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "model_config_fingerprint": fingerprint,
            "request_content_fingerprint": {
                "anyOf": [
                    fingerprint,
                    {"type": "null"},
                ],
            },
            "kind": {"const": "rope_position_distinguishability"},
            "ok": {"type": "boolean"},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "unsupported_model_config_fields": string_list,
            "parameter_sources": {
                "type": "object",
                "required": [
                    "head_dim",
                    "base",
                    "context",
                    "tolerance",
                    "discretization",
                    "requested_margin",
                ],
                "properties": {
                    "head_dim": parameter_source,
                    "base": parameter_source,
                    "context": parameter_source,
                    "tolerance": parameter_source,
                    "discretization": parameter_source,
                    "requested_margin": parameter_source,
                },
                "additionalProperties": False,
            },
            "request": {
                "anyOf": [
                    build_contract_request_json_schema(),
                    {"type": "null"},
                ],
            },
            "notes": string_list,
        },
        "additionalProperties": False,
    }


def build_architecture_config_import_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    parameter_source = {
        "type": "object",
        "required": ["source"],
        "properties": {
            "source": {
                "enum": [
                    "explicit_override",
                    "architecture_config_field",
                    "default",
                    "missing",
                ],
            },
            "field": {"type": "string", "minLength": 1},
            "value": {},
            "note": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_architecture_config_import.schema.json"
        ),
        "title": "Circle AI Architecture Config Import Report",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "content_fingerprint_algorithm",
            "architecture_config_fingerprint",
            "request_content_fingerprint",
            "kind",
            "ok",
            "failure_count",
            "failures",
            "parameters",
            "parameter_sources",
            "request",
            "notes",
        ],
        "properties": {
            "schema_id": {"const": ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "architecture_config_fingerprint": fingerprint,
            "request_content_fingerprint": {
                "anyOf": [
                    fingerprint,
                    {"type": "null"},
                ],
            },
            "kind": {
                "type": ["string", "null"],
                "enum": [*ARCHITECTURE_CONFIG_SUPPORTED_KINDS, None],
            },
            "ok": {"type": "boolean"},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "parameters": {"type": "object"},
            "parameter_sources": {
                "type": "object",
                "additionalProperties": parameter_source,
            },
            "request": {
                "anyOf": [
                    build_contract_request_json_schema(),
                    {"type": "null"},
                ],
            },
            "notes": string_list,
        },
        "additionalProperties": False,
    }


def build_contract_runner_check_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    parameter_source = {
        "type": "object",
        "required": ["source"],
        "properties": {
            "source": {
                "enum": [
                    "override",
                    "config_field",
                    "derived_config_fields",
                    "default",
                    "missing",
                    "omitted",
                ],
            },
            "field": {"type": "string", "minLength": 1},
            "fields": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
            },
            "note": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    model_config_parameter_sources = {
        "type": "object",
        "required": [
            "head_dim",
            "base",
            "context",
            "tolerance",
            "discretization",
            "requested_margin",
        ],
        "properties": {
            "head_dim": parameter_source,
            "base": parameter_source,
            "context": parameter_source,
            "tolerance": parameter_source,
            "discretization": parameter_source,
            "requested_margin": parameter_source,
        },
        "additionalProperties": False,
    }
    summary = {
        "type": "object",
        "required": [
            "source_type",
            "source_path",
            "source_content_fingerprint",
            "request_path",
            "model_config_import_report_path",
            "model_config_parameter_sources",
            "architecture_config_import_report_path",
            "architecture_config_parameter_sources",
            "request_validation_report_path",
            "certification_bundle_path",
            "certification_bundle_check_path",
            "receipt_path",
            "compact_receipt_path",
            "kind",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "theorem_count",
            "recommendation_count",
            "validation_command_count",
            "normalized_request",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "compact_selected_evidence_count",
            "compact_selected_evidence_unclassified_count",
            "compact_selected_evidence_labels",
        ],
        "properties": {
            "source_type": {"enum": ["request", "model_config", "architecture_config"]},
            "source_path": {"type": "string", "minLength": 1},
            "source_content_fingerprint": fingerprint,
            "request_path": {"type": ["string", "null"]},
            "model_config_import_report_path": {"type": ["string", "null"]},
            "model_config_parameter_sources": {
                "anyOf": [model_config_parameter_sources, {"type": "null"}],
            },
            "architecture_config_import_report_path": {
                "type": ["string", "null"]
            },
            "architecture_config_parameter_sources": {
                "anyOf": [{"type": "object"}, {"type": "null"}],
            },
            "request_validation_report_path": {"type": ["string", "null"]},
            "certification_bundle_path": {"type": ["string", "null"]},
            "certification_bundle_check_path": {"type": ["string", "null"]},
            "receipt_path": {"type": ["string", "null"]},
            "compact_receipt_path": {"type": ["string", "null"]},
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {"enum": list(DECISION_VERDICTS)},
            "decision_assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "theorem_count": {"type": "integer", "minimum": 0},
            "recommendation_count": {"type": "integer", "minimum": 0},
            "validation_command_count": {"type": "integer", "minimum": 0},
            "normalized_request": {"type": "object", "minProperties": 1},
            "request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "compact_selected_evidence_count": {"type": "integer", "minimum": 1},
            "compact_selected_evidence_unclassified_count": {
                "type": "integer",
                "minimum": 0,
            },
            "compact_selected_evidence_labels": {
                "type": "array",
                "items": {
                    "enum": list(COMPACT_EVIDENCE_PROOF_LAYER_LABELS),
                },
                "uniqueItems": True,
            },
        },
        "additionalProperties": False,
    }
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_runner_check.schema.json"
        ),
        "title": "Circle AI Contract Runner Check Report",
        "type": "object",
        "required": [
            "schema_id",
            "ok",
            "example_count",
            "failure_count",
            "failures",
            "selected_kinds",
            "gate_policy",
            "summaries",
        ],
        "properties": {
            "schema_id": {"const": RUNNER_CHECK_SCHEMA_ID},
            "ok": {"type": "boolean"},
            "example_count": {"type": "integer", "minimum": 0},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "selected_kinds": {
                "type": "array",
                "items": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            },
            "gate_policy": gate_policy,
            "summaries": {"type": "array", "items": summary},
        },
        "additionalProperties": False,
    }


def build_contract_artifact_manifest_json_schema() -> dict[str, Any]:
    fingerprint = {
        "anyOf": [
            {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            {"type": "null"},
        ]
    }
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    artifact = {
        "type": "object",
        "required": [
            "label",
            "path",
            "exists",
            "sha256",
            "content_schema_id",
        ],
        "properties": {
            "label": {"type": "string", "minLength": 1},
            "path": {"type": "string", "minLength": 1},
            "exists": {"type": "boolean"},
            "sha256": fingerprint,
            "content_schema_id": {"type": ["string", "null"]},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_artifact_manifest.schema.json"
        ),
        "title": "Circle AI Contract Artifact Manifest",
        "type": "object",
        "required": [
            "schema_id",
            "artifact_fingerprint_algorithm",
            "kind",
            "artifact_prefix",
            "artifact_dir",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "gate_policy",
            "artifact_count",
            "artifacts",
        ],
        "properties": {
            "schema_id": {"const": ARTIFACT_MANIFEST_SCHEMA_ID},
            "artifact_fingerprint_algorithm": {"const": "sha256-file-v1"},
            "kind": {
                "type": ["string", "null"],
                "enum": [*SUPPORTED_CONTRACT_KINDS, None],
            },
            "artifact_prefix": {"type": "string", "minLength": 1},
            "artifact_dir": {"type": ["string", "null"]},
            "status": {
                "type": ["string", "null"],
                "enum": [*STATUS_VALUES, None],
            },
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {
                "type": ["string", "null"],
                "enum": [*DECISION_VERDICTS, None],
            },
            "decision_assurance": {
                "type": ["string", "null"],
                "enum": [*DECISION_ASSURANCE_LEVELS, None],
            },
            "request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "gate_policy": gate_policy,
            "artifact_count": {"type": "integer", "minimum": 0},
            "artifacts": {"type": "array", "items": artifact},
        },
        "additionalProperties": False,
    }


def build_contract_artifact_manifest_file_check_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {
        "anyOf": [
            {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            {"type": "null"},
        ]
    }
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    artifact_summary = {
        "type": "object",
        "required": [
            "label",
            "path",
            "resolved_path",
            "exists",
            "declared_exists",
            "declared_sha256",
            "actual_sha256",
            "content_schema_id",
            "actual_schema_id",
            "ok",
            "failures",
        ],
        "properties": {
            "label": {"type": "string", "minLength": 1},
            "path": {"type": "string", "minLength": 1},
            "resolved_path": {"type": ["string", "null"]},
            "exists": {"type": "boolean"},
            "declared_exists": {"type": "boolean"},
            "declared_sha256": fingerprint,
            "actual_sha256": fingerprint,
            "content_schema_id": {"type": ["string", "null"]},
            "actual_schema_id": {"type": ["string", "null"]},
            "ok": {"type": "boolean"},
            "failures": string_list,
        },
        "additionalProperties": False,
    }
    summary = {
        "type": "object",
        "required": [
            "path",
            "kind",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "artifact_fingerprint_algorithm",
            "artifact_count",
            "declared_artifact_count",
            "missing_artifact_count",
            "fingerprint_mismatch_count",
            "schema_mismatch_count",
            "artifact_prefix",
            "artifact_dir",
            "gate_policy",
            "normalized_request",
            "model_config_fingerprint",
            "unsupported_model_config_fields",
            "architecture_config_fingerprint",
            "architecture_config_import_kind",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "receipt_replay_check_present",
            "receipt_replay_check_schema_id",
            "receipt_replay_check_ok",
            "receipt_replay_check_failure_count",
            "receipt_replay_check_replay_command_matches_request",
            "receipt_replay_check_all_replay_fields_match",
            "receipt_replay_check_original_receipt_fingerprint",
            "receipt_replay_check_replayed_receipt_fingerprint",
            "receipt_replay_check_fingerprints_match_receipt",
            "semantic_check_sidecar_count",
            "semantic_check_sidecar_labels",
            "semantic_check_sidecar_failure_count",
            "preflight_sidecar_count",
            "preflight_sidecar_labels",
            "preflight_sidecar_failure_count",
            "theorem_count",
            "theorem_ids",
            "evidence_field_count",
            "evidence_fields",
            "recommendation_ids",
            "validation_command_count",
            "validation_commands",
            "artifacts",
            "failure_count",
        ],
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "kind": {"type": ["string", "null"], "enum": [*SUPPORTED_CONTRACT_KINDS, None]},
            "status": {"type": ["string", "null"], "enum": [*STATUS_VALUES, None]},
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {
                "type": ["string", "null"],
                "enum": [*DECISION_VERDICTS, None],
            },
            "decision_assurance": {
                "type": ["string", "null"],
                "enum": [*DECISION_ASSURANCE_LEVELS, None],
            },
            "artifact_fingerprint_algorithm": {"const": "sha256-file-v1"},
            "artifact_count": {"type": "integer", "minimum": 0},
            "declared_artifact_count": {"type": "integer", "minimum": 0},
            "missing_artifact_count": {"type": "integer", "minimum": 0},
            "fingerprint_mismatch_count": {"type": "integer", "minimum": 0},
            "schema_mismatch_count": {"type": "integer", "minimum": 0},
            "artifact_prefix": {"type": "string", "minLength": 1},
            "artifact_dir": {"type": ["string", "null"]},
            "gate_policy": gate_policy,
            "normalized_request": {
                "anyOf": [{"type": "object"}, {"type": "null"}],
            },
            "model_config_fingerprint": fingerprint,
            "unsupported_model_config_fields": string_list,
            "architecture_config_fingerprint": fingerprint,
            "architecture_config_import_kind": {
                "type": ["string", "null"],
                "enum": [*SUPPORTED_CONTRACT_KINDS, None],
            },
            "request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "receipt_replay_check_present": {"type": "boolean"},
            "receipt_replay_check_schema_id": {"type": ["string", "null"]},
            "receipt_replay_check_ok": {"type": ["boolean", "null"]},
            "receipt_replay_check_failure_count": {
                "type": ["integer", "null"],
                "minimum": 0,
            },
            "receipt_replay_check_replay_command_matches_request": {
                "type": ["boolean", "null"]
            },
            "receipt_replay_check_all_replay_fields_match": {
                "type": ["boolean", "null"]
            },
            "receipt_replay_check_original_receipt_fingerprint": fingerprint,
            "receipt_replay_check_replayed_receipt_fingerprint": fingerprint,
            "receipt_replay_check_fingerprints_match_receipt": {
                "type": ["boolean", "null"]
            },
            "semantic_check_sidecar_count": {"type": "integer", "minimum": 0},
            "semantic_check_sidecar_labels": string_list,
            "semantic_check_sidecar_failure_count": {
                "type": "integer",
                "minimum": 0,
            },
            "preflight_sidecar_count": {"type": "integer", "minimum": 0},
            "preflight_sidecar_labels": string_list,
            "preflight_sidecar_failure_count": {
                "type": "integer",
                "minimum": 0,
            },
            "theorem_count": {"type": "integer", "minimum": 0},
            "theorem_ids": string_list,
            "evidence_field_count": {"type": "integer", "minimum": 0},
            "evidence_fields": string_list,
            "recommendation_ids": string_list,
            "validation_command_count": {"type": "integer", "minimum": 0},
            "validation_commands": string_list,
            "artifacts": {"type": "array", "items": artifact_summary},
            "failure_count": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_artifact_manifest_file_check.schema.json"
        ),
        "title": "Circle AI Contract Artifact Manifest File Check Report",
        "type": "object",
        "required": [
            "schema_id",
            "ok",
            "manifest_count",
            "failure_count",
            "failures",
            "pin_policy",
            "summaries",
        ],
        "properties": {
            "schema_id": {"const": ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_ID},
            "ok": {"type": "boolean"},
            "manifest_count": {"type": "integer", "minimum": 0},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "pin_policy": _dependency_pin_policy_schema(),
            "summaries": {"type": "array", "items": summary},
        },
        "additionalProperties": False,
    }


def _file_sha256_or_none(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_manifest_status_fields(
    *,
    receipt: Mapping[str, Any] | None,
    request_validation_report: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if receipt is not None:
        decision = receipt.get("decision")
        decision_dict = decision if isinstance(decision, Mapping) else {}
        return {
            "kind": receipt.get("kind"),
            "status": receipt.get("status"),
            "request_passed": receipt.get("request_passed"),
            "decision_verdict": decision_dict.get("verdict"),
            "decision_assurance": decision_dict.get("assurance"),
            "request_content_fingerprint": receipt.get("request_content_fingerprint"),
            "normalized_request_fingerprint": receipt.get(
                "normalized_request_fingerprint"
            ),
            "receipt_content_fingerprint": receipt.get("receipt_content_fingerprint"),
        }
    if request_validation_report is not None:
        return {
            "kind": request_validation_report.get("canonical_kind"),
            "status": None,
            "request_passed": None,
            "decision_verdict": None,
            "decision_assurance": None,
            "request_content_fingerprint": request_validation_report.get(
                "request_content_fingerprint"
            ),
            "normalized_request_fingerprint": None,
            "receipt_content_fingerprint": None,
        }
    return {
        "kind": None,
        "status": None,
        "request_passed": None,
        "decision_verdict": None,
        "decision_assurance": None,
        "request_content_fingerprint": None,
        "normalized_request_fingerprint": None,
        "receipt_content_fingerprint": None,
    }


def build_contract_artifact_manifest(
    artifact_paths: Sequence[tuple[str, str | Path, str | None]],
    *,
    artifact_prefix: str,
    artifact_dir: str | Path | None = None,
    receipt: Mapping[str, Any] | None = None,
    request_validation_report: Mapping[str, Any] | None = None,
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Build a schema-shaped artifact manifest for written contract sidecars.

    ``artifact_paths`` contains ``(label, path, content_schema_id)`` triples.
    The builder records file existence and SHA-256 fingerprints, then mirrors
    the receipt or request-preflight status fields needed by downstream CI.
    """

    if not isinstance(artifact_prefix, str) or not artifact_prefix:
        raise ValueError("artifact_prefix must be a non-empty string")
    _validate_receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
    )
    artifacts: list[dict[str, Any]] = []
    for label, raw_path, schema_id in artifact_paths:
        if not isinstance(label, str) or not label:
            raise ValueError("artifact labels must be non-empty strings")
        path = Path(raw_path)
        artifacts.append(
            {
                "label": label,
                "path": str(path),
                "exists": path.exists(),
                "sha256": _file_sha256_or_none(path),
                "content_schema_id": schema_id,
            }
        )
    status_fields = _artifact_manifest_status_fields(
        receipt=receipt,
        request_validation_report=request_validation_report,
    )
    return {
        "schema_id": ARTIFACT_MANIFEST_SCHEMA_ID,
        "artifact_fingerprint_algorithm": "sha256-file-v1",
        "artifact_prefix": artifact_prefix,
        "artifact_dir": None if artifact_dir is None else str(Path(artifact_dir)),
        "gate_policy": _receipt_gate_policy(
            required_statuses=required_statuses,
            required_decision_verdicts=required_decision_verdicts,
            required_assurance_levels=required_assurance_levels,
            require_passed=require_passed,
        ),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        **status_fields,
    }


def _display_manifest_check_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _artifact_resolution_candidates(raw_path: str, manifest_path: Path) -> list[Path]:
    path = Path(raw_path)
    candidates = [path]
    if not path.is_absolute():
        candidates.append(manifest_path.parent / path)
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def _load_artifact_schema_id(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(payload, Mapping):
        return None
    schema_id = payload.get("schema_id")
    return schema_id if isinstance(schema_id, str) else None


def _load_artifact_payload_by_label(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest_path: Path,
    label: str,
) -> Mapping[str, Any] | None:
    artifact = artifact_by_label.get(label)
    if not isinstance(artifact, Mapping):
        return None
    raw_path = artifact.get("path")
    if not isinstance(raw_path, str):
        return None
    artifact_path = next(
        (
            candidate
            for candidate in _artifact_resolution_candidates(raw_path, manifest_path)
            if candidate.exists()
        ),
        None,
    )
    if artifact_path is None:
        return None
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _receipt_consistency_failures(
    *,
    manifest: Mapping[str, Any],
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest_path: Path,
) -> list[str]:
    receipt_artifact = artifact_by_label.get("receipt_json")
    if not isinstance(receipt_artifact, Mapping):
        return []
    raw_path = receipt_artifact.get("path")
    if not isinstance(raw_path, str):
        return []
    receipt_path = next(
        (
            candidate
            for candidate in _artifact_resolution_candidates(raw_path, manifest_path)
            if candidate.exists()
        ),
        None,
    )
    if receipt_path is None:
        return []
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return [f"receipt_json artifact is not readable JSON: {raw_path}"]
    if not isinstance(receipt, Mapping):
        return [f"receipt_json artifact is not a JSON object: {raw_path}"]

    failures: list[str] = []
    decision = receipt.get("decision")
    decision_dict = decision if isinstance(decision, Mapping) else {}
    comparisons = (
        ("kind", manifest.get("kind"), receipt.get("kind")),
        ("status", manifest.get("status"), receipt.get("status")),
        (
            "request_passed",
            manifest.get("request_passed"),
            receipt.get("request_passed"),
        ),
        (
            "decision_verdict",
            manifest.get("decision_verdict"),
            decision_dict.get("verdict"),
        ),
        (
            "decision_assurance",
            manifest.get("decision_assurance"),
            decision_dict.get("assurance"),
        ),
        (
            "request_content_fingerprint",
            manifest.get("request_content_fingerprint"),
            receipt.get("request_content_fingerprint"),
        ),
        (
            "normalized_request_fingerprint",
            manifest.get("normalized_request_fingerprint"),
            receipt.get("normalized_request_fingerprint"),
        ),
        (
            "receipt_content_fingerprint",
            manifest.get("receipt_content_fingerprint"),
            receipt.get("receipt_content_fingerprint"),
        ),
    )
    for field, manifest_value, receipt_value in comparisons:
        if manifest_value != receipt_value:
            failures.append(
                f"manifest {field} does not match receipt_json: "
                f"{manifest_value!r} != {receipt_value!r}"
            )
    return failures


def _load_receipt_artifact_payload(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest_path: Path,
) -> Mapping[str, Any] | None:
    return _load_artifact_payload_by_label(
        artifact_by_label=artifact_by_label,
        manifest_path=manifest_path,
        label="receipt_json",
    )


def _receipt_artifact_theorem_ids(receipt: Mapping[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    proof_status = receipt.get("proof_status")
    if not isinstance(proof_status, Mapping):
        return []
    theorem_ids = proof_status.get("theorem_ids")
    if not isinstance(theorem_ids, list):
        return []
    return [theorem_id for theorem_id in theorem_ids if isinstance(theorem_id, str)]


def _receipt_artifact_evidence_fields(receipt: Mapping[str, Any] | None) -> list[str]:
    if receipt is None:
        return []
    evidence = receipt.get("evidence")
    if not isinstance(evidence, Mapping):
        return []
    return sorted(key for key in evidence if isinstance(key, str))


def _receipt_artifact_recommendation_ids(
    receipt: Mapping[str, Any] | None,
) -> list[str]:
    if receipt is None:
        return []
    recommendations = receipt.get("recommendations")
    if not isinstance(recommendations, list):
        return []
    ids: list[str] = []
    for recommendation in recommendations:
        if not isinstance(recommendation, Mapping):
            continue
        recommendation_id = recommendation.get("id")
        if isinstance(recommendation_id, str):
            ids.append(recommendation_id)
    return ids


def _receipt_artifact_validation_commands(
    receipt: Mapping[str, Any] | None,
) -> list[str]:
    if receipt is None:
        return []
    commands = receipt.get("validation_commands")
    if not isinstance(commands, list):
        return []
    return [command for command in commands if isinstance(command, str)]


def _load_model_config_import_artifact_payload(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest_path: Path,
) -> Mapping[str, Any] | None:
    return _load_artifact_payload_by_label(
        artifact_by_label=artifact_by_label,
        manifest_path=manifest_path,
        label="model_config_import_report",
    )


def _load_architecture_config_import_artifact_payload(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest_path: Path,
) -> Mapping[str, Any] | None:
    return _load_artifact_payload_by_label(
        artifact_by_label=artifact_by_label,
        manifest_path=manifest_path,
        label="architecture_config_import_report",
    )


def _receipt_replay_artifact_summary_and_failures(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    manifest_path: Path,
    receipt_payload: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    replay_artifact = artifact_by_label.get("receipt_replay_check")
    summary: dict[str, Any] = {
        "receipt_replay_check_present": isinstance(replay_artifact, Mapping),
        "receipt_replay_check_schema_id": None,
        "receipt_replay_check_ok": None,
        "receipt_replay_check_failure_count": None,
        "receipt_replay_check_replay_command_matches_request": None,
        "receipt_replay_check_all_replay_fields_match": None,
        "receipt_replay_check_original_receipt_fingerprint": None,
        "receipt_replay_check_replayed_receipt_fingerprint": None,
        "receipt_replay_check_fingerprints_match_receipt": None,
    }
    if not isinstance(replay_artifact, Mapping):
        return summary, []

    payload = _load_artifact_payload_by_label(
        artifact_by_label=artifact_by_label,
        manifest_path=manifest_path,
        label="receipt_replay_check",
    )
    if payload is None:
        return summary, ["receipt_replay_check artifact is not readable JSON"]

    schema_id = payload.get("schema_id")
    summary["receipt_replay_check_schema_id"] = (
        schema_id if isinstance(schema_id, str) else None
    )
    failures: list[str] = []
    try:
        jsonschema.validate(payload, build_contract_receipt_replay_check_json_schema())
    except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        failures.append(f"receipt_replay_check schema validation failed: {exc}")

    ok = payload.get("ok")
    failure_count = payload.get("failure_count")
    replay_command_matches = payload.get("replay_command_matches_request")
    comparison = payload.get("comparison")
    all_fields_match = (
        comparison.get("all_replay_fields_match")
        if isinstance(comparison, Mapping)
        else None
    )
    summary["receipt_replay_check_ok"] = ok if isinstance(ok, bool) else None
    summary["receipt_replay_check_failure_count"] = (
        failure_count if isinstance(failure_count, int) else None
    )
    summary["receipt_replay_check_replay_command_matches_request"] = (
        replay_command_matches if isinstance(replay_command_matches, bool) else None
    )
    summary["receipt_replay_check_all_replay_fields_match"] = (
        all_fields_match if isinstance(all_fields_match, bool) else None
    )

    expected_fingerprint = (
        receipt_payload.get("receipt_content_fingerprint")
        if isinstance(receipt_payload, Mapping)
        else manifest.get("receipt_content_fingerprint")
    )
    expected_fingerprint = (
        expected_fingerprint if isinstance(expected_fingerprint, str) else None
    )
    original = payload.get("original")
    replayed = payload.get("replayed")
    original_fingerprint = (
        original.get("receipt_content_fingerprint")
        if isinstance(original, Mapping)
        else None
    )
    replayed_fingerprint = (
        replayed.get("receipt_content_fingerprint")
        if isinstance(replayed, Mapping)
        else None
    )
    original_fingerprint = (
        original_fingerprint if isinstance(original_fingerprint, str) else None
    )
    replayed_fingerprint = (
        replayed_fingerprint if isinstance(replayed_fingerprint, str) else None
    )
    summary["receipt_replay_check_original_receipt_fingerprint"] = original_fingerprint
    summary["receipt_replay_check_replayed_receipt_fingerprint"] = replayed_fingerprint
    fingerprints_match_receipt = (
        None
        if expected_fingerprint is None
        else original_fingerprint == expected_fingerprint
        and replayed_fingerprint == expected_fingerprint
    )
    summary["receipt_replay_check_fingerprints_match_receipt"] = (
        fingerprints_match_receipt
    )

    if ok is not True:
        failures.append("receipt_replay_check report ok was not true")
    if replay_command_matches is not True:
        failures.append(
            "receipt_replay_check replay_command_matches_request was not true"
        )
    if all_fields_match is not True:
        failures.append(
            "receipt_replay_check comparison.all_replay_fields_match was not true"
        )
    if expected_fingerprint is not None and original_fingerprint != expected_fingerprint:
        failures.append(
            "receipt_replay_check original receipt_content_fingerprint does not "
            "match receipt_json"
        )
    if expected_fingerprint is not None and replayed_fingerprint != expected_fingerprint:
        failures.append(
            "receipt_replay_check replayed receipt_content_fingerprint does not "
            "match receipt_json"
        )
    return summary, failures


def _semantic_check_sidecar_summary_and_failures(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    manifest_path: Path,
    receipt_payload: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    expected_fingerprint = (
        receipt_payload.get("receipt_content_fingerprint")
        if isinstance(receipt_payload, Mapping)
        else manifest.get("receipt_content_fingerprint")
    )
    expected_fingerprint = (
        expected_fingerprint if isinstance(expected_fingerprint, str) else None
    )
    labels: list[str] = []
    failures: list[str] = []

    for label in ("receipt_check", "gate_report"):
        if label not in artifact_by_label:
            continue
        labels.append(label)
        payload = _load_artifact_payload_by_label(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
            label=label,
        )
        if payload is None:
            failures.append(f"{label} artifact is not readable JSON")
            continue
        try:
            jsonschema.validate(payload, build_contract_receipt_file_check_json_schema())
        except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{label} schema validation failed: {exc}")
        if payload.get("ok") is not True:
            failures.append(f"{label} report ok was not true")
        if payload.get("failure_count") != 0:
            failures.append(f"{label} failure_count was not zero")
        if payload.get("gate_policy") != manifest.get("gate_policy"):
            failures.append(f"{label} gate_policy does not match artifact manifest")
        summaries = payload.get("summaries")
        if not isinstance(summaries, list) or len(summaries) != 1:
            failures.append(f"{label} must have exactly one summary")
            continue
        summary = summaries[0]
        if not isinstance(summary, Mapping):
            failures.append(f"{label} summary was not an object")
            continue
        if (
            expected_fingerprint is not None
            and summary.get("receipt_content_fingerprint") != expected_fingerprint
        ):
            failures.append(
                f"{label} receipt_content_fingerprint does not match receipt_json"
            )

    label = "certification_bundle_check"
    if label in artifact_by_label:
        labels.append(label)
        payload = _load_artifact_payload_by_label(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
            label=label,
        )
        if payload is None:
            failures.append(f"{label} artifact is not readable JSON")
        else:
            try:
                jsonschema.validate(
                    payload,
                    build_contract_certification_bundle_file_check_json_schema(),
                )
            except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
                failures.append(f"{label} schema validation failed: {exc}")
            if payload.get("ok") is not True:
                failures.append(f"{label} report ok was not true")
            if payload.get("failure_count") != 0:
                failures.append(f"{label} failure_count was not zero")
            if payload.get("gate_policy") != manifest.get("gate_policy"):
                failures.append(
                    f"{label} gate_policy does not match artifact manifest"
                )
            summaries = payload.get("summaries")
            if not isinstance(summaries, list) or len(summaries) != 1:
                failures.append(f"{label} must have exactly one summary")
            else:
                summary = summaries[0]
                if not isinstance(summary, Mapping):
                    failures.append(f"{label} summary was not an object")
                elif (
                    expected_fingerprint is not None
                    and summary.get("receipt_content_fingerprint")
                    != expected_fingerprint
                ):
                    failures.append(
                        f"{label} receipt_content_fingerprint does not match "
                        "receipt_json"
                    )

    return (
        {
            "semantic_check_sidecar_count": len(labels),
            "semantic_check_sidecar_labels": labels,
            "semantic_check_sidecar_failure_count": len(failures),
        },
        failures,
    )


def _preflight_sidecar_summary_and_failures(
    *,
    artifact_by_label: Mapping[str, Mapping[str, Any]],
    manifest: Mapping[str, Any],
    manifest_path: Path,
) -> tuple[dict[str, Any], list[str]]:
    expected_request_fingerprint = manifest.get("request_content_fingerprint")
    expected_request_fingerprint = (
        expected_request_fingerprint
        if isinstance(expected_request_fingerprint, str)
        else None
    )
    labels: list[str] = []
    failures: list[str] = []

    preflight_schemas = {
        "request_validation_report": build_contract_request_validation_json_schema,
        "model_config_import_report": build_rope_model_config_import_json_schema,
        "architecture_config_import_report": (
            build_architecture_config_import_json_schema
        ),
    }
    for label, schema_builder in preflight_schemas.items():
        if label not in artifact_by_label:
            continue
        labels.append(label)
        payload = _load_artifact_payload_by_label(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
            label=label,
        )
        if payload is None:
            failures.append(f"{label} artifact is not readable JSON")
            continue
        try:
            jsonschema.validate(payload, schema_builder())
        except (jsonschema.ValidationError, jsonschema.SchemaError) as exc:
            failures.append(f"{label} schema validation failed: {exc}")
        if payload.get("ok") is not True:
            failures.append(f"{label} report ok was not true")
        if payload.get("failure_count") != 0:
            failures.append(f"{label} failure_count was not zero")
        if (
            expected_request_fingerprint is not None
            and payload.get("request_content_fingerprint")
            != expected_request_fingerprint
        ):
            failures.append(
                f"{label} request_content_fingerprint does not match artifact "
                "manifest"
            )

    return (
        {
            "preflight_sidecar_count": len(labels),
            "preflight_sidecar_labels": labels,
            "preflight_sidecar_failure_count": len(failures),
        },
        failures,
    )


def build_contract_artifact_manifest_file_check_report(
    manifest: Mapping[str, Any],
    *,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Validate a saved artifact manifest and the files it names.

    This is the consumer-facing counterpart to ``--artifact-dir``. It verifies
    the manifest schema, every referenced file's SHA-256, declared content
    schema ids, and the receipt summary fields mirrored into the manifest.
    """

    manifest_path = Path(manifest_path)
    path_failures: list[str] = []
    summaries: list[dict[str, Any]] = []
    try:
        jsonschema.validate(manifest, build_contract_artifact_manifest_json_schema())
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list):
            artifacts = []
        if manifest.get("artifact_count") != len(artifacts):
            path_failures.append(
                "artifact_count does not match artifacts length: "
                f"{manifest.get('artifact_count')!r} != {len(artifacts)!r}"
            )

        seen_labels: set[str] = set()
        artifact_summaries: list[dict[str, Any]] = []
        missing_count = 0
        fingerprint_mismatch_count = 0
        schema_mismatch_count = 0
        artifact_by_label: dict[str, Mapping[str, Any]] = {}
        for artifact in artifacts:
            artifact_failures: list[str] = []
            if not isinstance(artifact, Mapping):
                path_failures.append("artifact entry was not an object")
                continue
            label = artifact.get("label")
            raw_path = artifact.get("path")
            declared_sha256 = artifact.get("sha256")
            content_schema_id = artifact.get("content_schema_id")
            declared_exists = artifact.get("exists")
            if isinstance(label, str):
                if label in seen_labels:
                    artifact_failures.append(f"duplicate artifact label: {label}")
                seen_labels.add(label)
                artifact_by_label[label] = artifact
            resolved_path: Path | None = None
            actual_sha256: str | None = None
            actual_schema_id: str | None = None
            if not isinstance(raw_path, str):
                artifact_failures.append("artifact path was not a string")
            else:
                for candidate in _artifact_resolution_candidates(raw_path, manifest_path):
                    if candidate.exists():
                        resolved_path = candidate
                        break
                if resolved_path is None:
                    artifact_failures.append(f"artifact file is missing: {raw_path}")
                    missing_count += 1
                else:
                    actual_sha256 = _file_sha256_or_none(resolved_path)
                    actual_schema_id = _load_artifact_schema_id(resolved_path)
            if declared_exists is not True:
                artifact_failures.append(
                    f"artifact declared exists={declared_exists!r}, expected true"
                )
            if declared_sha256 != actual_sha256:
                artifact_failures.append(
                    f"artifact sha256 mismatch: {declared_sha256!r} != {actual_sha256!r}"
                )
                fingerprint_mismatch_count += 1
            if content_schema_id is not None and content_schema_id != actual_schema_id:
                artifact_failures.append(
                    "artifact schema_id mismatch: "
                    f"{content_schema_id!r} != {actual_schema_id!r}"
                )
                schema_mismatch_count += 1
            artifact_summaries.append(
                {
                    "label": str(label),
                    "path": str(raw_path),
                    "resolved_path": (
                        None
                        if resolved_path is None
                        else _display_manifest_check_path(resolved_path)
                    ),
                    "exists": resolved_path is not None,
                    "declared_exists": bool(declared_exists),
                    "declared_sha256": declared_sha256,
                    "actual_sha256": actual_sha256,
                    "content_schema_id": content_schema_id,
                    "actual_schema_id": actual_schema_id,
                    "ok": not artifact_failures,
                    "failures": artifact_failures,
                }
            )
            path_failures.extend(
                f"{label}: {failure}" for failure in artifact_failures
            )

        path_failures.extend(
            _receipt_consistency_failures(
                manifest=manifest,
                artifact_by_label=artifact_by_label,
                manifest_path=manifest_path,
            )
        )
        receipt_payload = _load_receipt_artifact_payload(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
        )
        receipt_theorem_ids = _receipt_artifact_theorem_ids(receipt_payload)
        receipt_evidence_fields = _receipt_artifact_evidence_fields(receipt_payload)
        receipt_recommendation_ids = _receipt_artifact_recommendation_ids(
            receipt_payload
        )
        receipt_validation_commands = _receipt_artifact_validation_commands(
            receipt_payload
        )
        normalized_request = (
            receipt_payload.get("normalized_request")
            if isinstance(receipt_payload, Mapping)
            else None
        )
        model_config_import = _load_model_config_import_artifact_payload(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
        )
        architecture_config_import = _load_architecture_config_import_artifact_payload(
            artifact_by_label=artifact_by_label,
            manifest_path=manifest_path,
        )
        unsupported_model_config_fields = (
            model_config_import.get("unsupported_model_config_fields")
            if isinstance(model_config_import, Mapping)
            else []
        )
        (
            receipt_replay_summary,
            receipt_replay_failures,
        ) = _receipt_replay_artifact_summary_and_failures(
            artifact_by_label=artifact_by_label,
            manifest=manifest,
            manifest_path=manifest_path,
            receipt_payload=receipt_payload,
        )
        path_failures.extend(receipt_replay_failures)
        (
            semantic_sidecar_summary,
            semantic_sidecar_failures,
        ) = _semantic_check_sidecar_summary_and_failures(
            artifact_by_label=artifact_by_label,
            manifest=manifest,
            manifest_path=manifest_path,
            receipt_payload=receipt_payload,
        )
        path_failures.extend(semantic_sidecar_failures)
        (
            preflight_sidecar_summary,
            preflight_sidecar_failures,
        ) = _preflight_sidecar_summary_and_failures(
            artifact_by_label=artifact_by_label,
            manifest=manifest,
            manifest_path=manifest_path,
        )
        path_failures.extend(preflight_sidecar_failures)
        summary = {
            "path": _display_manifest_check_path(manifest_path),
            "kind": manifest.get("kind"),
            "status": manifest.get("status"),
            "request_passed": manifest.get("request_passed"),
            "decision_verdict": manifest.get("decision_verdict"),
            "decision_assurance": manifest.get("decision_assurance"),
            "artifact_fingerprint_algorithm": manifest.get(
                "artifact_fingerprint_algorithm"
            ),
            "artifact_count": len(artifact_summaries),
            "declared_artifact_count": int(manifest.get("artifact_count", 0)),
            "missing_artifact_count": missing_count,
            "fingerprint_mismatch_count": fingerprint_mismatch_count,
            "schema_mismatch_count": schema_mismatch_count,
            "artifact_prefix": manifest.get("artifact_prefix"),
            "artifact_dir": manifest.get("artifact_dir"),
            "gate_policy": manifest.get("gate_policy"),
            "normalized_request": (
                dict(normalized_request)
                if isinstance(normalized_request, Mapping)
                else None
            ),
            "model_config_fingerprint": (
                model_config_import.get("model_config_fingerprint")
                if isinstance(model_config_import, Mapping)
                else None
            ),
            "unsupported_model_config_fields": (
                [
                    field
                    for field in unsupported_model_config_fields
                    if isinstance(field, str)
                ]
                if isinstance(unsupported_model_config_fields, list)
                else []
            ),
            "architecture_config_fingerprint": (
                architecture_config_import.get("architecture_config_fingerprint")
                if isinstance(architecture_config_import, Mapping)
                else None
            ),
            "architecture_config_import_kind": (
                architecture_config_import.get("kind")
                if isinstance(architecture_config_import, Mapping)
                else None
            ),
            "request_content_fingerprint": manifest.get(
                "request_content_fingerprint"
            ),
            "normalized_request_fingerprint": manifest.get(
                "normalized_request_fingerprint"
            ),
            "receipt_content_fingerprint": manifest.get(
                "receipt_content_fingerprint"
            ),
            **receipt_replay_summary,
            **semantic_sidecar_summary,
            **preflight_sidecar_summary,
            "theorem_count": len(receipt_theorem_ids),
            "theorem_ids": receipt_theorem_ids,
            "evidence_field_count": len(receipt_evidence_fields),
            "evidence_fields": receipt_evidence_fields,
            "recommendation_ids": receipt_recommendation_ids,
            "validation_command_count": len(receipt_validation_commands),
            "validation_commands": receipt_validation_commands,
            "artifacts": artifact_summaries,
            "failure_count": len(path_failures),
        }
        summaries.append(summary)
    except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        path_failures.append(str(exc))

    failures = [f"{_display_manifest_check_path(manifest_path)}: {failure}" for failure in path_failures]
    report = {
        "schema_id": ARTIFACT_MANIFEST_FILE_CHECK_SCHEMA_ID,
        "ok": not failures,
        "manifest_count": 1,
        "failure_count": len(failures),
        "failures": failures,
        "pin_policy": _dependency_pin_policy(),
        "summaries": summaries,
    }
    jsonschema.validate(
        report,
        build_contract_artifact_manifest_file_check_json_schema(),
    )
    return report


def build_contract_receipt_file_check_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    summary = {
        "type": "object",
        "required": [
            "path",
            "kind",
            "contract_id",
            "content_fingerprint_algorithm",
            "contract_pack_fingerprint",
            "contract_content_fingerprint",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "theorem_count",
            "theorem_ids",
            "evidence_field_count",
            "evidence_fields",
            "recommendation_ids",
            "validation_command_count",
            "validation_commands",
            "normalized_request",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "failure_count",
        ],
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "contract_pack_fingerprint": fingerprint,
            "contract_content_fingerprint": fingerprint,
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {"enum": list(DECISION_VERDICTS)},
            "decision_assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "theorem_count": {"type": "integer", "minimum": 0},
            "theorem_ids": string_list,
            "evidence_field_count": {"type": "integer", "minimum": 0},
            "evidence_fields": string_list,
            "recommendation_ids": string_list,
            "validation_command_count": {"type": "integer", "minimum": 0},
            "validation_commands": string_list,
            "normalized_request": {"type": "object", "minProperties": 1},
            "request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "failure_count": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_receipt_file_check.schema.json"
        ),
        "title": "Circle AI Contract Receipt File Check Report",
        "type": "object",
        "required": [
            "schema_id",
            "ok",
            "receipt_count",
            "failure_count",
            "failures",
            "gate_policy",
            "pin_policy",
            "summaries",
        ],
        "properties": {
            "schema_id": {"const": RECEIPT_FILE_CHECK_SCHEMA_ID},
            "ok": {"type": "boolean"},
            "receipt_count": {"type": "integer", "minimum": 0},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "gate_policy": gate_policy,
            "pin_policy": _dependency_pin_policy_schema(),
            "summaries": {"type": "array", "items": summary},
        },
        "additionalProperties": False,
    }


def build_contract_receipt_replay_check_json_schema() -> dict[str, Any]:
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    receipt_summary = {
        "type": "object",
        "required": [
            "kind",
            "contract_id",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
        ],
        "properties": {
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {"enum": list(DECISION_VERDICTS)},
            "decision_assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
        },
        "additionalProperties": False,
    }
    comparison = {
        "type": "object",
        "required": [
            "kind_matches",
            "contract_id_matches",
            "status_matches",
            "request_passed_matches",
            "decision_verdict_matches",
            "decision_assurance_matches",
            "request_content_fingerprint_matches",
            "normalized_request_fingerprint_matches",
            "receipt_content_fingerprint_matches",
            "all_replay_fields_match",
        ],
        "properties": {
            "kind_matches": {"type": "boolean"},
            "contract_id_matches": {"type": "boolean"},
            "status_matches": {"type": "boolean"},
            "request_passed_matches": {"type": "boolean"},
            "decision_verdict_matches": {"type": "boolean"},
            "decision_assurance_matches": {"type": "boolean"},
            "request_content_fingerprint_matches": {"type": "boolean"},
            "normalized_request_fingerprint_matches": {"type": "boolean"},
            "receipt_content_fingerprint_matches": {"type": "boolean"},
            "all_replay_fields_match": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_receipt_replay_check.schema.json"
        ),
        "title": "Circle AI Contract Receipt Replay Check Report",
        "type": "object",
        "required": [
            "schema_id",
            "receipt_schema_id",
            "request_schema_id",
            "content_fingerprint_algorithm",
            "ok",
            "failure_count",
            "failures",
            "path",
            "replay_command",
            "replay_command_matches_request",
            "original",
            "replayed",
            "comparison",
        ],
        "properties": {
            "schema_id": {"const": RECEIPT_REPLAY_CHECK_SCHEMA_ID},
            "receipt_schema_id": {"const": RECEIPT_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "ok": {"type": "boolean"},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": {"type": "array", "items": {"type": "string"}},
            "path": {"type": "string", "minLength": 1},
            "replay_command": {
                "type": ["string", "null"],
                "minLength": 1,
            },
            "replay_command_matches_request": {"type": "boolean"},
            "original": receipt_summary,
            "replayed": {
                "anyOf": [receipt_summary, {"type": "null"}],
            },
            "comparison": comparison,
        },
        "additionalProperties": False,
    }


def build_contract_certification_bundle_json_schema() -> dict[str, Any]:
    fingerprint = {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"}
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }

    def inline(schema: Mapping[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in schema.items()
            if key not in {"$schema", "$id", "title"}
        }

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_certification_bundle.schema.json"
        ),
        "title": "Circle AI Contract Certification Bundle",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "receipt_schema_id",
            "gate_report_schema_id",
            "model_config_import_report_schema_id",
            "architecture_config_import_report_schema_id",
            "content_fingerprint_algorithm",
            "ok",
            "failure_count",
            "failures",
            "gate_policy",
            "request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "request_validation_report",
            "receipt",
            "gate_report",
            "model_config_import_report",
            "architecture_config_import_report",
        ],
        "properties": {
            "schema_id": {"const": CERTIFICATION_BUNDLE_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "receipt_schema_id": {"const": RECEIPT_SCHEMA_ID},
            "gate_report_schema_id": {"const": RECEIPT_FILE_CHECK_SCHEMA_ID},
            "model_config_import_report_schema_id": {
                "const": ROPE_MODEL_CONFIG_IMPORT_SCHEMA_ID
            },
            "architecture_config_import_report_schema_id": {
                "const": ARCHITECTURE_CONFIG_IMPORT_SCHEMA_ID
            },
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "ok": {"type": "boolean"},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": {"type": "array", "items": {"type": "string"}},
            "gate_policy": gate_policy,
            "request_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "request_validation_report": inline(
                build_contract_request_validation_json_schema()
            ),
            "receipt": {
                "anyOf": [inline(build_contract_receipt_json_schema()), {"type": "null"}]
            },
            "gate_report": {
                "anyOf": [
                    inline(build_contract_receipt_file_check_json_schema()),
                    {"type": "null"},
                ],
            },
            "model_config_import_report": {
                "anyOf": [
                    inline(build_rope_model_config_import_json_schema()),
                    {"type": "null"},
                ],
            },
            "architecture_config_import_report": {
                "anyOf": [
                    inline(build_architecture_config_import_json_schema()),
                    {"type": "null"},
                ],
            },
        },
        "additionalProperties": False,
    }


def build_contract_certification_bundle_file_check_json_schema() -> dict[str, Any]:
    string_list = {"type": "array", "items": {"type": "string"}}
    fingerprint = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    nullable_fingerprint = {
        "anyOf": [
            fingerprint,
            {"type": "null"},
        ]
    }
    gate_policy = {
        "type": "object",
        "required": [
            "allowed_statuses",
            "allowed_decision_verdicts",
            "allowed_assurance_levels",
            "require_passed",
        ],
        "properties": {
            "allowed_statuses": {
                "type": "array",
                "items": {"enum": list(STATUS_VALUES)},
            },
            "allowed_decision_verdicts": {
                "type": "array",
                "items": {"enum": list(DECISION_VERDICTS)},
            },
            "allowed_assurance_levels": {
                "type": "array",
                "items": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            },
            "require_passed": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    summary = {
        "type": "object",
        "required": [
            "path",
            "bundle_ok",
            "bundle_failure_count",
            "request_validation_ok",
            "gate_report_ok",
            "has_model_config_import_report",
            "model_config_fingerprint",
            "model_config_request_content_fingerprint",
            "has_architecture_config_import_report",
            "architecture_config_fingerprint",
            "architecture_config_request_content_fingerprint",
            "kind",
            "contract_id",
            "content_fingerprint_algorithm",
            "contract_pack_fingerprint",
            "contract_content_fingerprint",
            "status",
            "request_passed",
            "decision_verdict",
            "decision_assurance",
            "theorem_count",
            "theorem_ids",
            "evidence_field_count",
            "evidence_fields",
            "recommendation_ids",
            "validation_command_count",
            "validation_commands",
            "normalized_request",
            "bundle_request_content_fingerprint",
            "receipt_request_content_fingerprint",
            "normalized_request_fingerprint",
            "receipt_content_fingerprint",
            "failure_count",
        ],
        "properties": {
            "path": {"type": "string", "minLength": 1},
            "bundle_ok": {"type": "boolean"},
            "bundle_failure_count": {"type": "integer", "minimum": 0},
            "request_validation_ok": {"type": "boolean"},
            "gate_report_ok": {"type": ["boolean", "null"]},
            "has_model_config_import_report": {"type": "boolean"},
            "model_config_fingerprint": nullable_fingerprint,
            "model_config_request_content_fingerprint": nullable_fingerprint,
            "has_architecture_config_import_report": {"type": "boolean"},
            "architecture_config_fingerprint": nullable_fingerprint,
            "architecture_config_request_content_fingerprint": nullable_fingerprint,
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "contract_pack_fingerprint": fingerprint,
            "contract_content_fingerprint": fingerprint,
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision_verdict": {"enum": list(DECISION_VERDICTS)},
            "decision_assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "theorem_count": {"type": "integer", "minimum": 0},
            "theorem_ids": string_list,
            "evidence_field_count": {"type": "integer", "minimum": 0},
            "evidence_fields": string_list,
            "recommendation_ids": string_list,
            "validation_command_count": {"type": "integer", "minimum": 0},
            "validation_commands": string_list,
            "normalized_request": {"type": "object", "minProperties": 1},
            "bundle_request_content_fingerprint": fingerprint,
            "receipt_request_content_fingerprint": fingerprint,
            "normalized_request_fingerprint": fingerprint,
            "receipt_content_fingerprint": fingerprint,
            "failure_count": {"type": "integer", "minimum": 0},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_certification_bundle_file_check.schema.json"
        ),
        "title": "Circle AI Contract Certification Bundle File Check Report",
        "type": "object",
        "required": [
            "schema_id",
            "ok",
            "bundle_count",
            "failure_count",
            "failures",
            "gate_policy",
            "pin_policy",
            "summaries",
        ],
        "properties": {
            "schema_id": {"const": CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID},
            "ok": {"type": "boolean"},
            "bundle_count": {"type": "integer", "minimum": 0},
            "failure_count": {"type": "integer", "minimum": 0},
            "failures": string_list,
            "gate_policy": gate_policy,
            "pin_policy": _dependency_pin_policy_schema(),
            "summaries": {"type": "array", "items": summary},
        },
        "additionalProperties": False,
    }


def _append_certification_bundle_consistency_failures(
    *,
    bundle: Mapping[str, Any],
    path_failures: list[str],
) -> None:
    if bundle.get("failure_count") != len(bundle.get("failures", [])):
        path_failures.append("bundle failure_count does not match failures length")
    if bundle.get("ok") is not True:
        details = "; ".join(str(failure) for failure in bundle.get("failures", ()))
        path_failures.append(
            "bundle ok was not true" + (f": {details}" if details else "")
        )

    request_validation = bundle.get("request_validation_report")
    if isinstance(request_validation, Mapping):
        jsonschema.validate(
            request_validation,
            build_contract_request_validation_json_schema(),
        )
        if request_validation.get("request_content_fingerprint") != bundle.get(
            "request_content_fingerprint"
        ):
            path_failures.append(
                "request validation fingerprint does not match bundle request"
            )
        if request_validation.get("ok") is not True:
            path_failures.append("request validation report ok was not true")

    receipt = bundle.get("receipt")
    if isinstance(receipt, Mapping):
        if receipt.get("normalized_request_fingerprint") != bundle.get(
            "normalized_request_fingerprint"
        ):
            path_failures.append(
                "receipt normalized_request_fingerprint does not match bundle"
            )
        if receipt.get("receipt_content_fingerprint") != bundle.get(
            "receipt_content_fingerprint"
        ):
            path_failures.append("receipt_content_fingerprint does not match bundle")
    else:
        path_failures.append("bundle receipt was null")

    gate_report = bundle.get("gate_report")
    if isinstance(gate_report, Mapping):
        jsonschema.validate(
            gate_report,
            build_contract_receipt_file_check_json_schema(),
        )
        if gate_report.get("gate_policy") != bundle.get("gate_policy"):
            path_failures.append("embedded gate_report policy does not match bundle")
        if gate_report.get("failure_count") != len(gate_report.get("failures", [])):
            path_failures.append(
                "embedded gate_report failure_count does not match failures length"
            )
        if gate_report.get("ok") != (gate_report.get("failure_count") == 0):
            path_failures.append("embedded gate_report ok disagrees with failure_count")
        summaries = gate_report.get("summaries")
        if isinstance(receipt, Mapping) and isinstance(summaries, list):
            if len(summaries) != 1:
                path_failures.append("embedded gate_report must have one summary")
            elif summaries[0].get("receipt_content_fingerprint") != receipt.get(
                "receipt_content_fingerprint"
            ):
                path_failures.append(
                    "embedded gate_report receipt fingerprint does not match receipt"
                )
    else:
        path_failures.append("bundle gate_report was null")

    policy = bundle.get("gate_policy")
    decision = receipt.get("decision") if isinstance(receipt, Mapping) else None
    if isinstance(policy, Mapping) and isinstance(receipt, Mapping):
        allowed_statuses = tuple(policy.get("allowed_statuses", ()))
        if allowed_statuses and receipt.get("status") not in allowed_statuses:
            path_failures.append(
                "embedded gate policy status check failed: "
                f"{receipt.get('status')!r} not in {list(allowed_statuses)!r}"
            )
        allowed_verdicts = tuple(policy.get("allowed_decision_verdicts", ()))
        decision_verdict = (
            decision.get("verdict") if isinstance(decision, Mapping) else None
        )
        if allowed_verdicts and decision_verdict not in allowed_verdicts:
            path_failures.append(
                "embedded gate policy decision check failed: "
                f"{decision_verdict!r} not in {list(allowed_verdicts)!r}"
            )
        allowed_assurances = tuple(policy.get("allowed_assurance_levels", ()))
        decision_assurance = (
            decision.get("assurance") if isinstance(decision, Mapping) else None
        )
        if allowed_assurances and decision_assurance not in allowed_assurances:
            path_failures.append(
                "embedded gate policy assurance check failed: "
                f"{decision_assurance!r} not in {list(allowed_assurances)!r}"
            )
        if (
            policy.get("require_passed") is True
            and receipt.get("request_passed") is not True
        ):
            path_failures.append(
                "embedded gate policy pass check failed: request_passed was not true"
            )

    import_report = bundle.get("model_config_import_report")
    if import_report is None:
        pass
    elif isinstance(import_report, Mapping):
        jsonschema.validate(import_report, build_rope_model_config_import_json_schema())
        if import_report.get("request_content_fingerprint") != bundle.get(
            "request_content_fingerprint"
        ):
            path_failures.append(
                "model config import request fingerprint does not match bundle"
            )
        if isinstance(receipt, Mapping) and import_report.get("request") != receipt.get(
            "request"
        ):
            path_failures.append("model config import request does not match receipt")
        if import_report.get("ok") is not True:
            path_failures.append("model config import report ok was not true")
    else:
        path_failures.append("model_config_import_report was not an object or null")

    architecture_import_report = bundle.get("architecture_config_import_report")
    if architecture_import_report is None:
        pass
    elif isinstance(architecture_import_report, Mapping):
        jsonschema.validate(
            architecture_import_report,
            build_architecture_config_import_json_schema(),
        )
        if architecture_import_report.get("request_content_fingerprint") != bundle.get(
            "request_content_fingerprint"
        ):
            path_failures.append(
                "architecture config import request fingerprint does not match bundle"
            )
        if (
            isinstance(receipt, Mapping)
            and architecture_import_report.get("request") != receipt.get("request")
        ):
            path_failures.append(
                "architecture config import request does not match receipt"
            )
        if architecture_import_report.get("ok") is not True:
            path_failures.append("architecture config import report ok was not true")
    else:
        path_failures.append(
            "architecture_config_import_report was not an object or null"
        )


def build_contract_certification_bundle_file_check_report(
    bundle: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    bundle_path: str,
    required_statuses: Sequence[str] = (),
    required_decision_verdicts: Sequence[str] = (),
    required_assurance_levels: Sequence[str] = (),
    require_passed: bool = False,
) -> dict[str, Any]:
    """Build a saved-certification-bundle validation report.

    This is the public API equivalent of
    ``scripts/check_circle_ai_certification_bundle.py`` for callers that
    already have a bundle object in memory.
    """

    if not isinstance(bundle_path, str) or not bundle_path:
        raise ValueError("bundle_path must be a non-empty string")
    _validate_receipt_gate_policy(
        required_statuses=required_statuses,
        required_decision_verdicts=required_decision_verdicts,
        required_assurance_levels=required_assurance_levels,
    )

    summaries: list[dict[str, Any]] = []
    path_failures: list[str] = []
    try:
        jsonschema.validate(bundle, build_contract_certification_bundle_json_schema())
        receipt = bundle.get("receipt")
        if isinstance(receipt, Mapping):
            receipt_report = build_contract_receipt_file_check_report(
                receipt,
                pack,
                receipt_path=f"{bundle_path}::receipt",
                required_statuses=required_statuses,
                required_decision_verdicts=required_decision_verdicts,
                required_assurance_levels=required_assurance_levels,
                require_passed=require_passed,
            )
            path_failures.extend(receipt_report["failures"])
        else:
            receipt_report = {"summaries": [], "failures": []}
        _append_certification_bundle_consistency_failures(
            bundle=bundle,
            path_failures=path_failures,
        )
        if receipt_report["summaries"]:
            receipt_summary = dict(receipt_report["summaries"][0])
            import_report = bundle.get("model_config_import_report")
            has_import_report = isinstance(import_report, Mapping)
            architecture_import_report = bundle.get(
                "architecture_config_import_report"
            )
            has_architecture_import_report = isinstance(
                architecture_import_report,
                Mapping,
            )
            receipt_payload = receipt if isinstance(receipt, Mapping) else None
            receipt_theorem_ids = _receipt_artifact_theorem_ids(receipt_payload)
            receipt_evidence_fields = _receipt_artifact_evidence_fields(
                receipt_payload
            )
            receipt_recommendation_ids = _receipt_artifact_recommendation_ids(
                receipt_payload
            )
            receipt_validation_commands = _receipt_artifact_validation_commands(
                receipt_payload
            )
            summaries.append(
                {
                    "path": bundle_path,
                    "bundle_ok": bool(bundle.get("ok")),
                    "bundle_failure_count": int(bundle.get("failure_count", 0)),
                    "request_validation_ok": bool(
                        bundle["request_validation_report"].get("ok")
                    ),
                    "gate_report_ok": (
                        bundle["gate_report"].get("ok")
                        if isinstance(bundle.get("gate_report"), Mapping)
                        else None
                    ),
                    "has_model_config_import_report": has_import_report,
                    "model_config_fingerprint": (
                        import_report.get("model_config_fingerprint")
                        if has_import_report
                        else None
                    ),
                    "model_config_request_content_fingerprint": (
                        import_report.get("request_content_fingerprint")
                        if has_import_report
                        else None
                    ),
                    "has_architecture_config_import_report": (
                        has_architecture_import_report
                    ),
                    "architecture_config_fingerprint": (
                        architecture_import_report.get(
                            "architecture_config_fingerprint"
                        )
                        if has_architecture_import_report
                        else None
                    ),
                    "architecture_config_request_content_fingerprint": (
                        architecture_import_report.get(
                            "request_content_fingerprint"
                        )
                        if has_architecture_import_report
                        else None
                    ),
                    "kind": receipt_summary["kind"],
                    "contract_id": receipt_summary["contract_id"],
                    "content_fingerprint_algorithm": receipt_summary[
                        "content_fingerprint_algorithm"
                    ],
                    "contract_pack_fingerprint": receipt_summary[
                        "contract_pack_fingerprint"
                    ],
                    "contract_content_fingerprint": receipt_summary[
                        "contract_content_fingerprint"
                    ],
                    "status": receipt_summary["status"],
                    "request_passed": receipt_summary["request_passed"],
                    "decision_verdict": receipt_summary["decision_verdict"],
                    "decision_assurance": receipt_summary["decision_assurance"],
                    "theorem_count": len(receipt_theorem_ids),
                    "theorem_ids": receipt_theorem_ids,
                    "evidence_field_count": len(receipt_evidence_fields),
                    "evidence_fields": receipt_evidence_fields,
                    "recommendation_ids": receipt_recommendation_ids,
                    "validation_command_count": len(receipt_validation_commands),
                    "validation_commands": receipt_validation_commands,
                    "normalized_request": receipt_summary["normalized_request"],
                    "bundle_request_content_fingerprint": bundle[
                        "request_content_fingerprint"
                    ],
                    "receipt_request_content_fingerprint": receipt_summary[
                        "request_content_fingerprint"
                    ],
                    "normalized_request_fingerprint": receipt_summary[
                        "normalized_request_fingerprint"
                    ],
                    "receipt_content_fingerprint": receipt_summary[
                        "receipt_content_fingerprint"
                    ],
                    "failure_count": len(path_failures),
                }
            )
    except (ValueError, jsonschema.ValidationError, jsonschema.SchemaError) as exc:
        path_failures.append(str(exc))

    failures = [f"{bundle_path}: {failure}" for failure in path_failures]
    report = {
        "schema_id": CERTIFICATION_BUNDLE_FILE_CHECK_SCHEMA_ID,
        "ok": not failures,
        "bundle_count": 1,
        "failure_count": len(failures),
        "failures": failures,
        "gate_policy": _receipt_gate_policy(
            required_statuses=required_statuses,
            required_decision_verdicts=required_decision_verdicts,
            required_assurance_levels=required_assurance_levels,
            require_passed=require_passed,
        ),
        "pin_policy": _dependency_pin_policy(),
        "summaries": summaries,
    }
    jsonschema.validate(
        report,
        build_contract_certification_bundle_file_check_json_schema(),
    )
    return report


def build_compact_contract_receipt_json_schema() -> dict[str, Any]:
    unique_string_list = {
        "type": "array",
        "items": {"type": "string"},
        "uniqueItems": True,
    }
    nonempty_unique_string_list = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "uniqueItems": True,
    }
    proof_layer_counts_schema = {
        "type": "object",
        "required": list(PROOF_LAYER_BUCKETS),
        "properties": {
            bucket: {"type": "integer", "minimum": 0}
            for bucket in PROOF_LAYER_BUCKETS
        },
        "additionalProperties": False,
    }
    decision_schema = {
        "type": "object",
        "required": [
            "schema_id",
            "verdict",
            "assurance",
            "claim_status",
            "request_passed",
            "theorem_count",
            "all_theorem_ids_proved",
            "proof_layer_counts",
            "summary",
            "next_action",
        ],
        "properties": {
            "schema_id": {"const": "circle_calculus.ai_contract_decision.v0"},
            "verdict": {"enum": list(DECISION_VERDICTS)},
            "assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "claim_status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "theorem_count": {"type": "integer", "minimum": 0},
            "all_theorem_ids_proved": {"type": "boolean"},
            "proof_layer_counts": proof_layer_counts_schema,
            "summary": {"type": "string", "minLength": 1},
            "next_action": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://circle-calculus.local/schemas/"
            "circle_ai_contract_compact_receipt.schema.json"
        ),
        "title": "Circle AI Contract Compact Receipt",
        "type": "object",
        "required": [
            "schema_id",
            "receipt_schema_id",
            "kind",
            "contract_id",
            "status",
            "request_passed",
            "decision",
            "normalized_request",
            "proof_status_summary",
            "proof_layer_counts",
            "evidence_field_names",
            "selected_evidence",
            "selected_evidence_proof_layers",
            "recommendation_ids",
            "validation_commands",
            "not_claimed",
            "fingerprints",
        ],
        "properties": {
            "schema_id": {"const": COMPACT_RECEIPT_SCHEMA_ID},
            "receipt_schema_id": {"const": RECEIPT_SCHEMA_ID},
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision": decision_schema,
            "normalized_request": {"type": "object"},
            "proof_status_summary": {
                "type": "object",
                "required": [
                    "theorem_ids",
                    "theorem_count",
                    "all_theorem_ids_resolved",
                    "all_theorem_ids_proved",
                    "unresolved_theorem_ids",
                    "unproved_theorem_ids",
                ],
                "properties": {
                    "theorem_ids": nonempty_unique_string_list,
                    "theorem_count": {"type": "integer", "minimum": 0},
                    "all_theorem_ids_resolved": {"type": "boolean"},
                    "all_theorem_ids_proved": {"type": "boolean"},
                    "unresolved_theorem_ids": unique_string_list,
                    "unproved_theorem_ids": unique_string_list,
                },
                "additionalProperties": False,
            },
            "proof_layer_counts": proof_layer_counts_schema,
            "evidence_field_names": nonempty_unique_string_list,
            "selected_evidence": {
                "type": "object",
                "additionalProperties": True,
            },
            "selected_evidence_proof_layers": {
                "type": "object",
                "additionalProperties": {
                    "enum": list(COMPACT_EVIDENCE_PROOF_LAYER_LABELS)
                },
            },
            "recommendation_ids": unique_string_list,
            "validation_commands": nonempty_unique_string_list,
            "not_claimed": nonempty_unique_string_list,
            "fingerprints": {
                "type": "object",
                "required": [
                    "content_fingerprint_algorithm",
                    "request_content_fingerprint",
                    "normalized_request_fingerprint",
                    "receipt_content_fingerprint",
                    "contract_pack_fingerprint",
                    "contract_content_fingerprint",
                ],
                "properties": {
                    "content_fingerprint_algorithm": {
                        "const": FINGERPRINT_ALGORITHM
                    },
                    "request_content_fingerprint": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                    "normalized_request_fingerprint": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                    "receipt_content_fingerprint": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                    "contract_pack_fingerprint": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                    "contract_content_fingerprint": {
                        "type": "string",
                        "pattern": "^[0-9a-f]{64}$",
                    },
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    }


def build_contract_receipt_json_schema() -> dict[str, Any]:
    unique_string_list = {
        "type": "array",
        "items": {"type": "string"},
        "uniqueItems": True,
    }
    nonempty_unique_string_list = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "uniqueItems": True,
    }
    proof_layer_bucket = {
        "type": "array",
        "items": {"type": "string", "minLength": 1},
        "uniqueItems": True,
    }
    request_schema = {
        key: value
        for key, value in build_contract_request_json_schema().items()
        if key not in {"$schema", "$id", "title"}
    }
    proof_layer_counts_schema = {
        "type": "object",
        "required": list(PROOF_LAYER_BUCKETS),
        "properties": {
            bucket: {"type": "integer", "minimum": 0}
            for bucket in PROOF_LAYER_BUCKETS
        },
        "additionalProperties": False,
    }
    decision_schema = {
        "type": "object",
        "required": [
            "schema_id",
            "verdict",
            "assurance",
            "claim_status",
            "request_passed",
            "theorem_count",
            "all_theorem_ids_proved",
            "proof_layer_counts",
            "summary",
            "next_action",
        ],
        "properties": {
            "schema_id": {"const": "circle_calculus.ai_contract_decision.v0"},
            "verdict": {"enum": list(DECISION_VERDICTS)},
            "assurance": {"enum": list(DECISION_ASSURANCE_LEVELS)},
            "claim_status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "theorem_count": {"type": "integer", "minimum": 0},
            "all_theorem_ids_proved": {"type": "boolean"},
            "proof_layer_counts": proof_layer_counts_schema,
            "summary": {"type": "string", "minLength": 1},
            "next_action": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://circle-calculus.local/schemas/circle_ai_contract_receipt.schema.json",
        "title": "Circle AI Contract Receipt",
        "type": "object",
        "required": [
            "schema_id",
            "request_schema_id",
            "contract_pack_schema_id",
            "kind",
            "contract_id",
            "status",
            "request_passed",
            "decision",
            "request",
            "request_content_fingerprint",
            "normalized_request",
            "normalized_request_fingerprint",
            "evidence",
            "proof_status",
            "proof_layers",
            "recommendations",
            "validation_commands",
            "support",
            "not_claimed",
            "content_fingerprint_algorithm",
            "receipt_content_fingerprint",
        ],
        "properties": {
            "schema_id": {"const": RECEIPT_SCHEMA_ID},
            "request_schema_id": {"const": REQUEST_SCHEMA_ID},
            "contract_pack_schema_id": {"const": CONTRACT_PACK_SCHEMA_ID},
            "kind": {"enum": list(SUPPORTED_CONTRACT_KINDS)},
            "contract_id": {"type": "string", "minLength": 1},
            "status": {"enum": list(STATUS_VALUES)},
            "request_passed": {"type": ["boolean", "null"]},
            "decision": decision_schema,
            "request": request_schema,
            "request_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "normalized_request": {"type": "object"},
            "normalized_request_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
            "evidence": {"type": "object"},
            "proof_status": {
                "type": "object",
                "required": [
                    "theorem_ids",
                    "theorem_count",
                    "all_theorem_ids_resolved",
                    "all_theorem_ids_proved",
                    "unresolved_theorem_ids",
                    "unproved_theorem_ids",
                ],
                "properties": {
                    "theorem_ids": nonempty_unique_string_list,
                    "theorem_count": {"type": "integer", "minimum": 0},
                    "all_theorem_ids_resolved": {"type": "boolean"},
                    "all_theorem_ids_proved": {"type": "boolean"},
                    "unresolved_theorem_ids": unique_string_list,
                    "unproved_theorem_ids": unique_string_list,
                },
                "additionalProperties": True,
            },
            "proof_layers": {
                "type": "object",
                "required": list(PROOF_LAYER_BUCKETS),
                "properties": {
                    bucket: proof_layer_bucket for bucket in PROOF_LAYER_BUCKETS
                },
                "additionalProperties": True,
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "object"},
                "minItems": 1,
                "uniqueItems": True,
            },
            "validation_commands": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
                "uniqueItems": True,
            },
            "support": {"type": "object"},
            "not_claimed": nonempty_unique_string_list,
            "content_fingerprint_algorithm": {"const": FINGERPRINT_ALGORITHM},
            "receipt_content_fingerprint": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            },
        },
        "additionalProperties": False,
    }
