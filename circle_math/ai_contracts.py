"""Stable public API for building Circle AI contract fixtures.

The records produced here are finite structural contracts. They cite Lean
theorem ids and carry explicit non-claim boundaries; they are not benchmark or
model-quality results.
"""

from __future__ import annotations

from .applications.circle_ai_contract_runner import (
    SUPPORTED_CONTRACT_KINDS,
    build_contract_receipt,
    build_contract_request,
    build_kv_cache_receipt,
    build_recurrence_receipt,
    build_rope_contract_request_from_model_config,
    build_rope_model_config_import_report,
    build_rope_request_parameters_from_model_config,
    build_rope_receipt,
    build_sparse_attention_receipt,
    build_validated_contract_receipt,
    build_validated_rope_receipt_from_model_config,
    canonical_contract_kind,
    receipt_summary_lines,
)
from .applications.circle_ai_contracts import (
    SCHEMA_ID as CONTRACT_PACK_SCHEMA_ID,
    build_circulant_block_cyclic_mixer_contract,
    build_contract_pack,
    build_cyclic_memory_contract,
    build_multicoil_phase_feature_contract,
    build_recurrence_schedule_contract,
    build_seed_rule_contract,
    build_strided_candidate_fanout_contract,
)


__all__ = [
    "CONTRACT_PACK_SCHEMA_ID",
    "SUPPORTED_CONTRACT_KINDS",
    "build_circulant_block_cyclic_mixer_contract",
    "build_contract_pack",
    "build_contract_receipt",
    "build_contract_request",
    "build_cyclic_memory_contract",
    "build_kv_cache_receipt",
    "build_multicoil_phase_feature_contract",
    "build_recurrence_receipt",
    "build_recurrence_schedule_contract",
    "build_rope_contract_request_from_model_config",
    "build_rope_model_config_import_report",
    "build_rope_request_parameters_from_model_config",
    "build_rope_receipt",
    "build_seed_rule_contract",
    "build_sparse_attention_receipt",
    "build_strided_candidate_fanout_contract",
    "build_validated_contract_receipt",
    "build_validated_rope_receipt_from_model_config",
    "canonical_contract_kind",
    "receipt_summary_lines",
]
