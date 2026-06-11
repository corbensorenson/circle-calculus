"""Circle-to-Theseus-Hive AI contract fixtures.

These exports are public, deterministic fixtures that Theseus-Hive can consume
as experiment configuration. They are not model-quality claims and not ASI
claims. Lean theorem ids certify only finite index, schedule, coverage,
relative-phase, and equivariance facts where those ids are marked proved.
"""

from __future__ import annotations

from math import gcd
from typing import Any, Sequence

from circle_math.generative import coil_orbit_generator, compare_generator_to_explicit, regenerate

from .circle_ai import (
    adapter_block_loads,
    coil_attention_path,
    loop_exit_certificate,
    loop_required_steps,
    looped_recurrent_state,
    memory_slot,
    middle_block_budget_route,
    multicoil_cycle_length,
    multicoil_phase,
    phase_channel,
    run_adapter_parameter_budget_benchmark,
    run_circulant_mixer_benchmark,
    token_active_at_step,
    token_recurrence_budget,
)

SCHEMA_ID = "circle_calculus.theseus_hive_ai_contracts.v0"

CLAIM_BOUNDARY = (
    "These contracts expose finite structure for private experiments. They do not prove "
    "model quality, reasoning, transfer, context length, speed, memory scaling, or ASI."
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def recurrence_contract(
    *,
    loop_period: int = 5,
    sample_index: int = 8,
    max_loops: int = 7,
    token_indices: Sequence[int] = (0, 1, 2, 3, 4, 5, 6, 7),
    selected_block_start: int = 2,
    selected_block_width: int = 3,
) -> dict[str, Any]:
    """Return a loop/recurrence schedule contract for Theseus-Hive."""
    cert = loop_exit_certificate(loop_period, sample_index, max_loops)
    required = loop_required_steps(loop_period, sample_index)
    tokens = []
    for token_index in token_indices:
        budget = token_recurrence_budget(loop_period, token_index)
        tokens.append(
            {
                "token_index": token_index,
                "budget": budget,
                "state_at_budget": looped_recurrent_state(loop_period, budget),
                "active_steps": [
                    step for step in range(1, max_loops + 1) if token_active_at_step(loop_period, token_index, step)
                ],
            }
        )
    block, block_budget = middle_block_budget_route(
        selected_block_start,
        selected_block_width,
        loop_period,
        sample_index,
    )
    contract_passed = (
        1 <= required <= loop_period
        and cert.exit_step == required
        and cert.within_budget
        and cert.within_guardrail
        and all(1 <= item["budget"] <= loop_period for item in tokens)
    )
    return {
        "id": "TH-AI-CONTRACT-RECURRENCE-001",
        "kind": "recurrence_schedule",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "theorem_ids": [
            "AIM-T0006",
            "AIM-T0007",
            "AIM-T0008",
            "AIM-T0015",
            "AIM-T0035",
            "AIM-T0036",
            "AIM-T0037",
            "AIM-T0044",
            "AIM-T0045",
            "AIM-T0046",
            "AIM-T0047",
            "AIM-T0048",
            "AIM-T0049",
            "AIM-T0051",
            "AIM-T0052",
        ],
        "dictionary_ids": ["COMMON-0052", "COMMON-0053", "COMMON-0054", "COMMON-0059", "COMMON-0068"],
        "fields": {
            "loop_period": loop_period,
            "sample_index": sample_index,
            "max_loops": max_loops,
            "required_steps": required,
            "loop_phase": phase_channel(loop_period, sample_index),
            "score_trace": list(cert.score_trace),
            "exit_step": cert.exit_step,
            "overthinking_boundary": cert.overthinking_boundary,
            "middle_block": block,
            "middle_block_budget": block_budget,
            "tokens": tokens,
        },
        "contract_passed": contract_passed,
        "theseus_hive_use": "Private looped/recursive schedule, active-token, exit, and overthinking diagnostics.",
        "ordinary_baselines": ["fixed_depth", "dense_depth", "existing_work_budget", "no_recurrence"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def fanout_contract(
    *,
    context_length: int = 12,
    stride: int = 5,
    start_index: int = 0,
    path_length: int = 12,
) -> dict[str, Any]:
    """Return a strided candidate-fanout coverage contract."""
    g = gcd(context_length, stride)
    predicted_reach = context_length // g
    seen: list[int] = []
    current = start_index % context_length
    while current not in seen:
        seen.append(current)
        current = (current + stride) % context_length
    path = coil_attention_path(context_length, start_index, stride, path_length)
    duplicate_count = len(path) - len(set(path))
    contract_passed = len(seen) == predicted_reach and (predicted_reach == context_length) == (g == 1)
    return {
        "id": "TH-AI-CONTRACT-FANOUT-001",
        "kind": "strided_candidate_fanout",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "theorem_ids": ["AIT-T0001", "AIT-T0002", "AIT-T0003"],
        "dictionary_ids": ["COMMON-0047", "COMMON-0028"],
        "fields": {
            "context_length": context_length,
            "stride": stride,
            "start_index": start_index,
            "gcd": g,
            "predicted_reach": predicted_reach,
            "orbit": seen,
            "full_coverage": predicted_reach == context_length,
            "candidate_path": list(path),
            "candidate_budget": len(path),
            "duplicate_count": duplicate_count,
        },
        "contract_passed": contract_passed,
        "theseus_hive_use": "Private candidate fanout and STS branch-coverage diagnostics.",
        "ordinary_baselines": ["sequential_fanout", "random_fanout", "round_robin_fanout", "local_window"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def memory_contract(
    *,
    bank_size: int = 8,
    event_index: int = 23,
    event_count: int = 32,
) -> dict[str, Any]:
    """Return a cyclic memory slot plus winding/provenance contract."""
    events = list(range(event_count))
    loads = [0 for _ in range(bank_size)]
    for event in events:
        loads[memory_slot(bank_size, event)] += 1
    residue = memory_slot(bank_size, event_index)
    winding = event_index // bank_size
    same_residue_events = [event for event in events if memory_slot(bank_size, event) == residue]
    return {
        "id": "TH-AI-CONTRACT-MEMORY-001",
        "kind": "cyclic_memory_residue_winding",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "theorem_ids": ["AIM-T0001", "AIM-T0002", "AIM-T0004", "AIM-T0005"],
        "dictionary_ids": ["COMMON-0028", "COMMON-0029"],
        "fields": {
            "bank_size": bank_size,
            "event_index": event_index,
            "event_count": event_count,
            "residue_slot": residue,
            "winding": winding,
            "slot_loads": loads,
            "max_alias_load": max(loads),
            "same_residue_events": same_residue_events,
            "same_residue_windings": [event // bank_size for event in same_residue_events],
        },
        "contract_passed": 0 <= residue < bank_size and event_index == winding * bank_size + residue,
        "theseus_hive_use": "Context packet, routing-memory, and worker-state alias diagnostics.",
        "ordinary_baselines": ["fifo", "lru", "score_based_retention", "slot_only_memory"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def phase_feature_contract(
    *,
    periods: Sequence[int] = (5, 7),
    position: int = 37,
    query_position: int = 41,
    key_position: int = 18,
) -> dict[str, Any]:
    """Return a MultiCoil/relative-phase feature contract."""
    normalized_periods = tuple(periods)
    cycle = multicoil_cycle_length(normalized_periods)
    phase = multicoil_phase(normalized_periods, position)
    shifted_phase = multicoil_phase(normalized_periods, position + cycle)
    relative_period = normalized_periods[0]
    relative_phase = phase_channel(relative_period, query_position - key_position)
    shifted_relative = phase_channel(relative_period, query_position + cycle - (key_position + cycle))
    return {
        "id": "TH-AI-CONTRACT-PHASE-FEATURE-001",
        "kind": "multicoil_phase_feature",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md",
        "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIT-T0004", "AIT-T0005"],
        "dictionary_ids": ["COMMON-0026", "COMMON-0027", "COMMON-0046", "COMMON-0051"],
        "fields": {
            "periods": list(normalized_periods),
            "position": position,
            "phase_tuple": list(phase),
            "joint_repeat_horizon": cycle,
            "shifted_position": position + cycle,
            "shifted_phase_tuple": list(shifted_phase),
            "query_position": query_position,
            "key_position": key_position,
            "relative_period": relative_period,
            "relative_phase": relative_phase,
            "shifted_relative_phase": shifted_relative,
        },
        "contract_passed": phase == shifted_phase and relative_phase == shifted_relative,
        "theseus_hive_use": "Optional private Code LM state-sequence phase tags beside existing position buckets.",
        "ordinary_baselines": ["existing_position_bucket", "learned_position", "wrong_period", "no_phase_feature"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def mixer_contract(*, period: int = 8, channel_count: int = 128, block_size: int = 8) -> dict[str, Any]:
    """Return circulant and block-cyclic mixer/accounting contract."""
    mixer = run_circulant_mixer_benchmark(period=period)
    budget = run_adapter_parameter_budget_benchmark(channel_count=channel_count, block_size=block_size)
    loads = adapter_block_loads(block_size, tuple(range(channel_count)))
    return {
        "id": "TH-AI-CONTRACT-MIXER-001",
        "kind": "circulant_block_cyclic_mixer",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md",
        "theorem_ids": ["AIT-T0006", "AIT-T0007", "AIT-T0008", "AIT-T0009", "AIRA-T0001", "AIRA-T0002", "AIRA-T0004"],
        "dictionary_ids": ["COMMON-0056", "COMMON-0058", "COMMON-0030", "COMMON-0031"],
        "fields": {
            "period": period,
            "input_values": list(mixer.input_values),
            "kernel_values": list(mixer.kernel_values),
            "circulant_output": list(mixer.circulant_output),
            "dense_output": list(mixer.dense_output),
            "max_abs_dense_delta": mixer.max_abs_dense_delta,
            "dense_parameters": mixer.dense_parameters,
            "circulant_parameters": mixer.circulant_parameters,
            "circulant_parameter_ratio": mixer.parameter_ratio,
            "channel_count": channel_count,
            "block_size": block_size,
            "block_loads": list(loads),
            "dense_adapter_parameters": budget.dense_adapter_parameters,
            "lora_parameters": budget.lora_parameters,
            "block_cyclic_parameters": budget.block_cyclic_parameters,
            "block_to_dense_ratio": budget.block_to_dense_ratio,
        },
        "contract_passed": mixer.max_abs_dense_delta == 0 and max(loads) >= 1,
        "theseus_hive_use": "Private route-head, ranker, adapter, or feature-mixer baseline experiments.",
        "ordinary_baselines": ["dense_mixer", "low_rank_mixer", "lora_adapter", "no_mixer"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def seed_rule_contract(*, n: int = 12, stride: int = 8, start: int = 0) -> dict[str, Any]:
    """Return a seed/rule exact-regeneration contract for CGS-style pressure."""
    record = coil_orbit_generator(n, stride, start)
    regenerated = regenerate(record)
    comparison = compare_generator_to_explicit(record)
    return {
        "id": "TH-AI-CONTRACT-SEED-RULE-001",
        "kind": "seed_rule_exact_regeneration",
        "status": "fixture",
        "source_paper": "papers/generative/PAPER_GEN_01_SEED_RULE_PROVENANCE.md",
        "theorem_ids": list(record.theorem_ids),
        "dictionary_ids": list(record.dictionary_ids),
        "fields": {
            "artifact_id": record.artifact_id,
            "seed": _jsonable(record.seed),
            "rules": [
                {"rule_id": rule.rule_id, "parameters": _jsonable(rule.parameters)}
                for rule in record.rules
            ],
            "iteration_schedule": record.iteration_schedule,
            "closure_condition": record.closure_condition,
            "generated_object": _jsonable(record.generated_object),
            "regenerated_object": _jsonable(regenerated),
            "exact_regeneration": comparison.exact_regeneration,
            "explicit_length": comparison.explicit_length,
            "generator_length": comparison.generator_length,
            "generator_shorter": comparison.generator_shorter,
        },
        "contract_passed": comparison.exact_regeneration,
        "theseus_hive_use": "CGS accounting, loop-closure tool cards, and exact artifact regeneration checks.",
        "ordinary_baselines": ["object_only_storage", "unverified_template", "freeform_tool_memory"],
        "not_claimed": CLAIM_BOUNDARY,
    }


def build_contract_pack() -> dict[str, Any]:
    """Return the complete deterministic public contract pack."""
    contracts = [
        recurrence_contract(),
        fanout_contract(),
        memory_contract(),
        phase_feature_contract(),
        mixer_contract(),
        seed_rule_contract(),
    ]
    return {
        "schema_id": SCHEMA_ID,
        "status": "public_safe_fixture",
        "claim_boundary": CLAIM_BOUNDARY,
        "source_docs": [
            "docs/THESEUS_HIVE_AI_TRANSFER.md",
            "papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md",
            "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
            "papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md",
        ],
        "contracts": contracts,
    }
