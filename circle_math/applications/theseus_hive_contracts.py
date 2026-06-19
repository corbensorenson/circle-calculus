"""Circle-to-Theseus-Hive AI contract fixtures.

These exports are public, deterministic fixtures that Theseus-Hive can consume
as experiment configuration. They are not model-quality claims and not ASI
claims. Lean theorem ids certify only finite index, schedule, coverage,
relative-phase, and equivariance facts where those ids are marked proved.
"""

from __future__ import annotations

from math import gcd
from typing import Any, Sequence

from circle_math.generative import (
    SeedRuleProvenance,
    bounded_generator_search,
    compare_generator_to_explicit,
    finite_circle_generator,
    regenerate,
)

from .circle_ai import (
    active_inactive_token_count_accounting,
    active_token_count_at_step,
    active_token_count_trace,
    adapter_block_loads,
    active_token_counts_bounded_by_token_count,
    active_token_counts_descending_by_step,
    active_tokens_at_step,
    active_tokens_descending_by_step,
    active_tokens_nodup_by_step,
    coil_attention_path,
    full_loop_token_work,
    inactive_token_count_at_step,
    inactive_token_count_trace,
    inactive_token_counts_ascending_by_step,
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
    scheduled_work_saving,
    token_active_at_step,
    token_first_inactive_step,
    token_recurrence_budget,
    total_active_token_work,
    total_inactive_token_work,
    training_free_loop_budget,
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


def _bounded_search_candidate_summary(
    candidates: Sequence[tuple[str, SeedRuleProvenance]],
) -> tuple[list[dict[str, Any]], list[str], list[str], list[str]]:
    """Return declared finite-search candidate rows and deterministic ranks."""

    rows: list[dict[str, Any]] = []
    for declared_index, (candidate_id, candidate) in enumerate(candidates):
        comparison = compare_generator_to_explicit(candidate)
        rows.append(
            {
                "candidate_id": candidate_id,
                "declared_index": declared_index,
                "artifact_id": comparison.artifact_id,
                "seed": _jsonable(candidate.seed),
                "exact_regeneration": comparison.exact_regeneration,
                "explicit_length": comparison.explicit_length,
                "generator_length": comparison.generator_length,
                "storage_saving": comparison.storage_saving,
                "storage_saving_positive": comparison.storage_saving_positive,
                "generator_shorter": comparison.generator_shorter,
            }
        )

    ranked = sorted(
        rows,
        key=lambda row: (
            row["generator_length"],
            row["explicit_length"],
            row["declared_index"],
            row["candidate_id"],
        ),
    )
    rank_by_candidate_id = {
        row["candidate_id"]: rank for rank, row in enumerate(ranked, start=1)
    }
    for row in rows:
        row["rank_by_generator_length"] = rank_by_candidate_id[row["candidate_id"]]

    ranked_candidate_ids = [row["candidate_id"] for row in ranked]
    ranked_exact_candidate_ids = [
        row["candidate_id"] for row in ranked if row["exact_regeneration"]
    ]
    ranked_shorter_candidate_ids = [
        row["candidate_id"] for row in ranked if row["generator_shorter"]
    ]
    return rows, ranked_candidate_ids, ranked_exact_candidate_ids, ranked_shorter_candidate_ids


def recurrence_contract(
    *,
    loop_period: int = 5,
    sample_index: int = 8,
    max_loops: int = 7,
    token_indices: Sequence[int] = (0, 1, 2, 3, 4, 5, 6, 7),
    selected_block_start: int = 2,
    selected_block_width: int = 3,
    periodic_shift_passes: int = 3,
) -> dict[str, Any]:
    """Return a loop/recurrence schedule contract for Theseus-Hive."""
    if periodic_shift_passes < 0:
        raise ValueError("periodic_shift_passes must be nonnegative")
    cert = loop_exit_certificate(loop_period, sample_index, max_loops)
    required = loop_required_steps(loop_period, sample_index)
    token_indices = tuple(token_indices)
    token_count = len(token_indices)
    work_count_step = 2 if loop_period >= 2 else 1
    active_step_one_tokens = active_tokens_at_step(loop_period, token_count, 1)
    active_work_step_tokens = active_tokens_at_step(loop_period, token_count, work_count_step)
    post_period_active_tokens = active_tokens_at_step(loop_period, token_count, loop_period + 1)
    active_work_count = active_token_count_at_step(loop_period, token_count, work_count_step)
    inactive_work_count = inactive_token_count_at_step(loop_period, token_count, work_count_step)
    first_step_active_count = active_token_count_at_step(loop_period, token_count, 1)
    first_step_inactive_count = inactive_token_count_at_step(loop_period, token_count, 1)
    post_period_active_count = active_token_count_at_step(loop_period, token_count, loop_period + 1)
    post_period_inactive_count = inactive_token_count_at_step(loop_period, token_count, loop_period + 1)
    active_inactive_accounting = active_inactive_token_count_accounting(
        loop_period,
        token_count,
        work_count_step,
    )
    public_fixture_active_count = active_token_count_at_step(4, 8, 2)
    public_fixture_inactive_count = inactive_token_count_at_step(4, 8, 2)
    public_fixture_accounting = active_inactive_token_count_accounting(4, 8, 2)
    active_token_sets_descend = active_tokens_descending_by_step(loop_period, token_count, loop_period + 1)
    active_token_lists_nodup = active_tokens_nodup_by_step(loop_period, token_count, loop_period + 1)
    active_token_counts_bounded = active_token_counts_bounded_by_token_count(loop_period, token_count, loop_period + 1)
    active_token_counts_descend = active_token_counts_descending_by_step(loop_period, token_count, loop_period + 1)
    inactive_token_counts_ascend = inactive_token_counts_ascending_by_step(loop_period, token_count, loop_period + 1)
    total_active_work = total_active_token_work(loop_period, token_count, loop_period)
    total_inactive_work = total_inactive_token_work(loop_period, token_count, loop_period)
    active_count_trace = active_token_count_trace(loop_period, token_count, loop_period)
    inactive_count_trace = inactive_token_count_trace(loop_period, token_count, loop_period)
    active_count_trace_sum_matches_total = sum(active_count_trace) == total_active_work
    inactive_count_trace_sum_matches_total = (
        sum(inactive_count_trace) == total_inactive_work
    )
    full_work = full_loop_token_work(token_count, loop_period)
    work_saving = scheduled_work_saving(loop_period, token_count, loop_period)
    work_saving_accounting = work_saving + total_active_work == full_work
    active_inactive_work_accounting = total_active_work + total_inactive_work == full_work
    work_saving_matches_inactive_work = work_saving == total_inactive_work
    work_saving_positive = work_saving > 0
    active_work_below_full = total_active_work < full_work
    work_saving_positive_matches_shortfall = work_saving_positive == active_work_below_full
    work_saving_zero = work_saving == 0
    active_work_equals_full = total_active_work == full_work
    work_saving_zero_matches_no_shortfall = work_saving_zero == active_work_equals_full
    public_fixture_total_active_work = total_active_token_work(4, 8, 4)
    public_fixture_total_inactive_work = total_inactive_token_work(4, 8, 4)
    public_fixture_full_work = full_loop_token_work(8, 4)
    public_fixture_work_saving = scheduled_work_saving(4, 8, 4)
    public_fixture_work_accounting = (
        public_fixture_work_saving + public_fixture_total_active_work
        == public_fixture_full_work
    )
    public_fixture_active_inactive_work_accounting = (
        public_fixture_total_active_work + public_fixture_total_inactive_work
        == public_fixture_full_work
    )
    public_fixture_work_saving_matches_inactive_work = (
        public_fixture_work_saving == public_fixture_total_inactive_work
    )
    public_fixture_work_saving_positive = public_fixture_work_saving > 0
    public_fixture_active_work_below_full = (
        public_fixture_total_active_work < public_fixture_full_work
    )
    public_fixture_positive_matches_shortfall = (
        public_fixture_work_saving_positive == public_fixture_active_work_below_full
    )
    public_fixture_work_saving_zero = public_fixture_work_saving == 0
    public_fixture_active_work_equals_full = (
        public_fixture_total_active_work == public_fixture_full_work
    )
    public_fixture_zero_matches_no_shortfall = (
        public_fixture_work_saving_zero == public_fixture_active_work_equals_full
    )
    default_fixture_total_active_work = total_active_token_work(5, 8, 5)
    default_fixture_total_inactive_work = total_inactive_token_work(5, 8, 5)
    default_fixture_full_work = full_loop_token_work(8, 5)
    default_fixture_work_saving = scheduled_work_saving(5, 8, 5)
    default_fixture_work_accounting = (
        default_fixture_work_saving + default_fixture_total_active_work
        == default_fixture_full_work
    )
    default_fixture_active_inactive_work_accounting = (
        default_fixture_total_active_work + default_fixture_total_inactive_work
        == default_fixture_full_work
    )
    default_fixture_work_saving_matches_inactive_work = (
        default_fixture_work_saving == default_fixture_total_inactive_work
    )
    post_period_extension_horizon_steps = loop_period + 1
    post_period_extension_total_active_work = total_active_token_work(
        loop_period,
        token_count,
        post_period_extension_horizon_steps,
    )
    post_period_extension_total_inactive_work = total_inactive_token_work(
        loop_period,
        token_count,
        post_period_extension_horizon_steps,
    )
    post_period_extension_full_work = full_loop_token_work(
        token_count,
        post_period_extension_horizon_steps,
    )
    post_period_extension_work_saving = scheduled_work_saving(
        loop_period,
        token_count,
        post_period_extension_horizon_steps,
    )
    post_period_extension_active_work_unchanged = (
        post_period_extension_total_active_work == total_active_work
    )
    post_period_extension_inactive_work_added_token_count = (
        post_period_extension_total_inactive_work == total_inactive_work + token_count
    )
    post_period_extension_saving_added_token_count = (
        post_period_extension_work_saving == work_saving + token_count
    )
    default_fixture_extension_total_active_work = total_active_token_work(5, 8, 6)
    default_fixture_extension_work_saving = scheduled_work_saving(5, 8, 6)
    default_fixture_extension_active_work_unchanged = (
        default_fixture_extension_total_active_work == default_fixture_total_active_work
    )
    default_fixture_extension_saving_added_token_count = (
        default_fixture_extension_work_saving == default_fixture_work_saving + 8
    )
    post_period_extra_steps = 3
    post_period_multi_extension_horizon_steps = loop_period + post_period_extra_steps
    post_period_multi_extension_total_active_work = total_active_token_work(
        loop_period,
        token_count,
        post_period_multi_extension_horizon_steps,
    )
    post_period_multi_extension_total_inactive_work = total_inactive_token_work(
        loop_period,
        token_count,
        post_period_multi_extension_horizon_steps,
    )
    post_period_multi_extension_full_work = full_loop_token_work(
        token_count,
        post_period_multi_extension_horizon_steps,
    )
    post_period_multi_extension_work_saving = scheduled_work_saving(
        loop_period,
        token_count,
        post_period_multi_extension_horizon_steps,
    )
    post_period_multi_extension_active_work_unchanged = (
        post_period_multi_extension_total_active_work == total_active_work
    )
    post_period_multi_extension_inactive_work_added_extra_token_count = (
        post_period_multi_extension_total_inactive_work
        == total_inactive_work + post_period_extra_steps * token_count
    )
    post_period_multi_extension_saving_added_extra_token_count = (
        post_period_multi_extension_work_saving
        == work_saving + post_period_extra_steps * token_count
    )
    default_fixture_multi_extension_total_active_work = total_active_token_work(5, 8, 8)
    default_fixture_multi_extension_work_saving = scheduled_work_saving(5, 8, 8)
    default_fixture_multi_extension_active_work_unchanged = (
        default_fixture_multi_extension_total_active_work == default_fixture_total_active_work
    )
    default_fixture_multi_extension_saving_added_extra_token_count = (
        default_fixture_multi_extension_work_saving
        == default_fixture_work_saving + post_period_extra_steps * 8
    )
    periodic_shift_base_token = token_indices[-1] if token_indices else sample_index
    periodic_shift_amount = periodic_shift_passes * loop_period
    periodic_shifted_token = periodic_shift_base_token + periodic_shift_amount
    periodic_shift_base_required_steps = loop_required_steps(loop_period, periodic_shift_base_token)
    periodic_shift_shifted_required_steps = loop_required_steps(loop_period, periodic_shifted_token)
    periodic_shift_required_steps_invariant = (
        periodic_shift_shifted_required_steps == periodic_shift_base_required_steps
    )
    periodic_shift_base_recurrence_budget = token_recurrence_budget(
        loop_period,
        periodic_shift_base_token,
    )
    periodic_shift_shifted_recurrence_budget = token_recurrence_budget(
        loop_period,
        periodic_shifted_token,
    )
    periodic_shift_recurrence_budget_invariant = (
        periodic_shift_shifted_recurrence_budget == periodic_shift_base_recurrence_budget
    )
    periodic_shift_base_training_free_budget = training_free_loop_budget(
        loop_period,
        periodic_shift_base_token,
        max_loops,
    )
    periodic_shift_shifted_training_free_budget = training_free_loop_budget(
        loop_period,
        periodic_shifted_token,
        max_loops,
    )
    periodic_shift_training_free_budget_invariant = (
        periodic_shift_shifted_training_free_budget == periodic_shift_base_training_free_budget
    )
    periodic_shift_base_certificate = loop_exit_certificate(
        loop_period,
        periodic_shift_base_token,
        max_loops,
    )
    periodic_shift_shifted_certificate = loop_exit_certificate(
        loop_period,
        periodic_shifted_token,
        max_loops,
    )
    periodic_shift_exit_step_invariant = (
        periodic_shift_shifted_certificate.exit_step == periodic_shift_base_certificate.exit_step
    )
    periodic_shift_overthinking_boundary_invariant = (
        periodic_shift_shifted_certificate.overthinking_boundary
        == periodic_shift_base_certificate.overthinking_boundary
    )
    periodic_shift_active_step = work_count_step
    periodic_shift_base_active_at_step = token_active_at_step(
        loop_period,
        periodic_shift_base_token,
        periodic_shift_active_step,
    )
    periodic_shift_shifted_active_at_step = token_active_at_step(
        loop_period,
        periodic_shifted_token,
        periodic_shift_active_step,
    )
    periodic_shift_active_at_step_invariant = (
        periodic_shift_shifted_active_at_step == periodic_shift_base_active_at_step
    )
    tokens = []
    first_inactive_steps = []
    for token_index in token_indices:
        budget = token_recurrence_budget(loop_period, token_index)
        first_inactive_step = token_first_inactive_step(loop_period, token_index)
        first_inactive_steps.append(
            {
                "token_index": token_index,
                "active_budget": budget,
                "first_inactive_step": first_inactive_step,
            }
        )
        tokens.append(
            {
                "token_index": token_index,
                "budget": budget,
                "first_inactive_step": first_inactive_step,
                "state_at_budget": looped_recurrent_state(loop_period, budget),
                "active_steps": [
                    step for step in range(1, max_loops + 1) if token_active_at_step(loop_period, token_index, step)
                ],
            }
        )
    first_inactive_steps_match_budget_successor = all(
        item["first_inactive_step"] == item["active_budget"] + 1
        for item in first_inactive_steps
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
        and active_step_one_tokens == tuple(range(token_count))
        and post_period_active_tokens == ()
        and first_step_active_count == token_count
        and first_step_inactive_count == 0
        and post_period_active_count == 0
        and post_period_inactive_count == token_count
        and active_inactive_accounting
        and public_fixture_active_count == 6
        and public_fixture_inactive_count == 2
        and public_fixture_accounting
        and active_token_sets_descend
        and active_token_lists_nodup
        and active_token_counts_bounded
        and active_token_counts_descend
        and inactive_token_counts_ascend
        and active_count_trace_sum_matches_total
        and inactive_count_trace_sum_matches_total
        and first_inactive_steps_match_budget_successor
        and total_active_work <= full_work
        and work_saving_accounting
        and active_inactive_work_accounting
        and work_saving_matches_inactive_work
        and work_saving_positive_matches_shortfall
        and work_saving_zero_matches_no_shortfall
        and public_fixture_total_active_work == 20
        and public_fixture_total_inactive_work == 12
        and public_fixture_full_work == 32
        and public_fixture_work_saving == 12
        and public_fixture_work_accounting
        and public_fixture_active_inactive_work_accounting
        and public_fixture_work_saving_matches_inactive_work
        and public_fixture_work_saving_positive
        and public_fixture_positive_matches_shortfall
        and public_fixture_zero_matches_no_shortfall
        and default_fixture_total_active_work == 21
        and default_fixture_total_inactive_work == 19
        and default_fixture_full_work == 40
        and default_fixture_work_saving == 19
        and default_fixture_work_accounting
        and default_fixture_active_inactive_work_accounting
        and default_fixture_work_saving_matches_inactive_work
        and post_period_extension_active_work_unchanged
        and post_period_extension_inactive_work_added_token_count
        and post_period_extension_saving_added_token_count
        and default_fixture_extension_total_active_work == 21
        and default_fixture_extension_work_saving == 27
        and default_fixture_extension_active_work_unchanged
        and default_fixture_extension_saving_added_token_count
        and post_period_multi_extension_active_work_unchanged
        and post_period_multi_extension_inactive_work_added_extra_token_count
        and post_period_multi_extension_saving_added_extra_token_count
        and default_fixture_multi_extension_total_active_work == 21
        and default_fixture_multi_extension_work_saving == 43
        and default_fixture_multi_extension_active_work_unchanged
        and default_fixture_multi_extension_saving_added_extra_token_count
        and periodic_shift_required_steps_invariant
        and periodic_shift_recurrence_budget_invariant
        and periodic_shift_training_free_budget_invariant
        and periodic_shift_exit_step_invariant
        and periodic_shift_overthinking_boundary_invariant
        and periodic_shift_active_at_step_invariant
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
            "AIM-T0026",
            "AIM-T0027",
            "AIM-T0028",
            "AIM-T0029",
            "AIM-T0030",
            "AIM-T0033",
            "AIM-T0034",
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
            "AIM-T0111",
            "AIM-T0112",
            "AIM-T0113",
            "AIM-T0114",
            "AIM-T0115",
            "AIM-T0116",
            "AIM-T0120",
            "AIM-T0128",
            "AIM-T0121",
            "AIM-T0122",
            "AIM-T0123",
            "AIM-T0129",
            "AIM-T0124",
            "AIM-T0125",
            "AIM-T0126",
            "AIM-T0127",
            "AIM-T0130",
            "AIM-T0131",
            "AIM-T0144",
            "AIM-T0145",
            "AIM-T0132",
            "AIM-T0133",
            "AIM-T0134",
            "AIM-T0146",
            "AIM-T0135",
            "AIM-T0138",
            "AIM-T0139",
            "AIM-T0140",
            "AIM-T0141",
            "AIM-T0142",
            "AIM-T0147",
            "AIM-T0143",
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
            "active_step_one_tokens": list(active_step_one_tokens),
            "active_step_one_is_full_range": active_step_one_tokens == tuple(range(token_count)),
            "first_step_active_token_count": first_step_active_count,
            "first_step_inactive_token_count": first_step_inactive_count,
            "first_step_inactive_count_zero": first_step_inactive_count == 0,
            "work_count_step": work_count_step,
            "work_step_active_tokens": list(active_work_step_tokens),
            "work_step_active_token_count": active_work_count,
            "work_step_inactive_token_count": inactive_work_count,
            "work_step_active_inactive_count_eq_token_count": active_inactive_accounting,
            "post_period_step": loop_period + 1,
            "post_period_active_tokens": list(post_period_active_tokens),
            "post_period_active_empty": post_period_active_tokens == (),
            "post_period_active_token_count": post_period_active_count,
            "post_period_inactive_token_count": post_period_inactive_count,
            "post_period_inactive_count_eq_token_count": post_period_inactive_count == token_count,
            "active_token_sets_descend": active_token_sets_descend,
            "active_token_lists_nodup": active_token_lists_nodup,
            "active_token_counts_bounded": active_token_counts_bounded,
            "active_token_counts_descend": active_token_counts_descend,
            "inactive_token_counts_ascend": inactive_token_counts_ascend,
            "active_monotonicity_checked_steps": loop_period + 1,
            "total_work_horizon_steps": loop_period,
            "active_token_count_trace": list(active_count_trace),
            "inactive_token_count_trace": list(inactive_count_trace),
            "active_token_count_trace_sum": sum(active_count_trace),
            "inactive_token_count_trace_sum": sum(inactive_count_trace),
            "active_token_count_trace_sum_matches_total": active_count_trace_sum_matches_total,
            "inactive_token_count_trace_sum_matches_total": inactive_count_trace_sum_matches_total,
            "first_inactive_steps": first_inactive_steps,
            "first_inactive_steps_match_budget_successor": first_inactive_steps_match_budget_successor,
            "total_active_token_work": total_active_work,
            "total_inactive_token_work": total_inactive_work,
            "full_loop_token_work": full_work,
            "scheduled_work_saving": work_saving,
            "scheduled_work_saving_accounting": work_saving_accounting,
            "active_inactive_work_accounting": active_inactive_work_accounting,
            "scheduled_work_saving_matches_inactive_work": work_saving_matches_inactive_work,
            "scheduled_work_saving_positive": work_saving_positive,
            "active_work_below_full_loop_work": active_work_below_full,
            "scheduled_work_saving_positive_iff_active_work_shortfall": work_saving_positive_matches_shortfall,
            "scheduled_work_saving_zero": work_saving_zero,
            "active_work_equals_full_loop_work": active_work_equals_full,
            "scheduled_work_saving_zero_iff_no_active_work_shortfall": work_saving_zero_matches_no_shortfall,
            "public_fixture_4_8_2_active_token_count": public_fixture_active_count,
            "public_fixture_4_8_2_inactive_token_count": public_fixture_inactive_count,
            "public_fixture_4_8_2_accounting_eq_token_count": public_fixture_accounting,
            "public_fixture_4_8_4_total_active_token_work": public_fixture_total_active_work,
            "public_fixture_4_8_4_total_inactive_token_work": public_fixture_total_inactive_work,
            "public_fixture_8_4_full_loop_token_work": public_fixture_full_work,
            "public_fixture_4_8_4_scheduled_work_saving": public_fixture_work_saving,
            "public_fixture_4_8_4_work_saving_accounting": public_fixture_work_accounting,
            "public_fixture_4_8_4_active_inactive_work_accounting": public_fixture_active_inactive_work_accounting,
            "public_fixture_4_8_4_work_saving_matches_inactive_work": public_fixture_work_saving_matches_inactive_work,
            "public_fixture_4_8_4_scheduled_work_saving_positive": public_fixture_work_saving_positive,
            "public_fixture_4_8_4_active_work_below_full_loop_work": public_fixture_active_work_below_full,
            "public_fixture_4_8_4_positive_saving_iff_active_work_shortfall": public_fixture_positive_matches_shortfall,
            "public_fixture_4_8_4_scheduled_work_saving_zero": public_fixture_work_saving_zero,
            "public_fixture_4_8_4_active_work_equals_full_loop_work": public_fixture_active_work_equals_full,
            "public_fixture_4_8_4_zero_saving_iff_no_active_work_shortfall": public_fixture_zero_matches_no_shortfall,
            "default_fixture_5_8_5_total_active_token_work": default_fixture_total_active_work,
            "default_fixture_5_8_5_total_inactive_token_work": default_fixture_total_inactive_work,
            "default_fixture_8_5_full_loop_token_work": default_fixture_full_work,
            "default_fixture_5_8_5_scheduled_work_saving": default_fixture_work_saving,
            "default_fixture_5_8_5_work_saving_accounting": default_fixture_work_accounting,
            "default_fixture_5_8_5_active_inactive_work_accounting": default_fixture_active_inactive_work_accounting,
            "default_fixture_5_8_5_work_saving_matches_inactive_work": default_fixture_work_saving_matches_inactive_work,
            "post_period_extension_horizon_steps": post_period_extension_horizon_steps,
            "post_period_extension_total_active_token_work": post_period_extension_total_active_work,
            "post_period_extension_total_inactive_token_work": post_period_extension_total_inactive_work,
            "post_period_extension_full_loop_token_work": post_period_extension_full_work,
            "post_period_extension_scheduled_work_saving": post_period_extension_work_saving,
            "post_period_extension_active_work_unchanged": post_period_extension_active_work_unchanged,
            "post_period_extension_inactive_work_added_token_count": post_period_extension_inactive_work_added_token_count,
            "post_period_extension_saving_added_token_count": post_period_extension_saving_added_token_count,
            "default_fixture_5_8_6_total_active_token_work": default_fixture_extension_total_active_work,
            "default_fixture_5_8_6_scheduled_work_saving": default_fixture_extension_work_saving,
            "default_fixture_5_8_6_active_work_unchanged": default_fixture_extension_active_work_unchanged,
            "default_fixture_5_8_6_saving_added_token_count": default_fixture_extension_saving_added_token_count,
            "post_period_extra_steps": post_period_extra_steps,
            "post_period_multi_extension_horizon_steps": post_period_multi_extension_horizon_steps,
            "post_period_multi_extension_total_active_token_work": post_period_multi_extension_total_active_work,
            "post_period_multi_extension_total_inactive_token_work": post_period_multi_extension_total_inactive_work,
            "post_period_multi_extension_full_loop_token_work": post_period_multi_extension_full_work,
            "post_period_multi_extension_scheduled_work_saving": post_period_multi_extension_work_saving,
            "post_period_multi_extension_active_work_unchanged": post_period_multi_extension_active_work_unchanged,
            "post_period_multi_extension_inactive_work_added_extra_token_count": post_period_multi_extension_inactive_work_added_extra_token_count,
            "post_period_multi_extension_saving_added_extra_token_count": post_period_multi_extension_saving_added_extra_token_count,
            "default_fixture_5_8_8_total_active_token_work": default_fixture_multi_extension_total_active_work,
            "default_fixture_5_8_8_scheduled_work_saving": default_fixture_multi_extension_work_saving,
            "default_fixture_5_8_8_active_work_unchanged": default_fixture_multi_extension_active_work_unchanged,
            "default_fixture_5_8_8_saving_added_extra_token_count": default_fixture_multi_extension_saving_added_extra_token_count,
            "periodic_shift_base_token": periodic_shift_base_token,
            "periodic_shift_passes": periodic_shift_passes,
            "periodic_shift_amount": periodic_shift_amount,
            "periodic_shifted_token": periodic_shifted_token,
            "periodic_shift_base_required_steps": periodic_shift_base_required_steps,
            "periodic_shift_shifted_required_steps": periodic_shift_shifted_required_steps,
            "periodic_shift_required_steps_invariant": periodic_shift_required_steps_invariant,
            "periodic_shift_base_recurrence_budget": periodic_shift_base_recurrence_budget,
            "periodic_shift_shifted_recurrence_budget": periodic_shift_shifted_recurrence_budget,
            "periodic_shift_recurrence_budget_invariant": periodic_shift_recurrence_budget_invariant,
            "periodic_shift_base_training_free_budget": periodic_shift_base_training_free_budget,
            "periodic_shift_shifted_training_free_budget": periodic_shift_shifted_training_free_budget,
            "periodic_shift_training_free_budget_invariant": periodic_shift_training_free_budget_invariant,
            "periodic_shift_base_exit_step": periodic_shift_base_certificate.exit_step,
            "periodic_shift_shifted_exit_step": periodic_shift_shifted_certificate.exit_step,
            "periodic_shift_exit_step_invariant": periodic_shift_exit_step_invariant,
            "periodic_shift_base_overthinking_boundary": periodic_shift_base_certificate.overthinking_boundary,
            "periodic_shift_shifted_overthinking_boundary": periodic_shift_shifted_certificate.overthinking_boundary,
            "periodic_shift_overthinking_boundary_invariant": periodic_shift_overthinking_boundary_invariant,
            "periodic_shift_active_step": periodic_shift_active_step,
            "periodic_shift_base_active_at_step": periodic_shift_base_active_at_step,
            "periodic_shift_shifted_active_at_step": periodic_shift_shifted_active_at_step,
            "periodic_shift_active_at_step_invariant": periodic_shift_active_at_step_invariant,
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
    unique_candidate_count = len(set(path))
    duplicate_count = len(path) - unique_candidate_count
    effective_candidate_budget = len(path) - duplicate_count
    candidate_budget_shortfall = max(0, predicted_reach - effective_candidate_budget)
    contract_passed = len(seen) == predicted_reach and (predicted_reach == context_length) == (g == 1)
    return {
        "id": "TH-AI-CONTRACT-FANOUT-001",
        "kind": "strided_candidate_fanout",
        "status": "fixture",
        "source_paper": "papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md",
        "theorem_ids": ["AIT-T0001", "AIT-T0002", "AIT-T0003", "AIT-T0173"],
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
            "unique_candidate_count": unique_candidate_count,
            "effective_candidate_budget": effective_candidate_budget,
            "duplicate_count": duplicate_count,
            "candidate_budget_accounting": effective_candidate_budget + duplicate_count == len(path),
            "effective_budget_matches_unique_candidates": effective_candidate_budget == unique_candidate_count,
            "candidate_budget_shortfall": candidate_budget_shortfall,
            "effective_budget_reaches_predicted_reach": effective_candidate_budget >= predicted_reach,
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


def seed_rule_contract(*, n: int = 128) -> dict[str, Any]:
    """Return a seed/rule exact-regeneration contract for CGS-style pressure."""
    record = finite_circle_generator(n)
    regenerated = regenerate(record)
    comparison = compare_generator_to_explicit(record)
    broken_record = SeedRuleProvenance(
        artifact_id=record.artifact_id,
        seed=record.seed,
        rules=record.rules,
        iteration_schedule=record.iteration_schedule,
        closure_condition=record.closure_condition,
        generated_object=(0, 1),
        theorem_ids=record.theorem_ids,
        dictionary_ids=record.dictionary_ids,
        note=record.note,
    )
    search_candidates = [
        ("finite_circle_public_fixture", record),
        ("finite_circle_unit_fixture", finite_circle_generator(1)),
        ("finite_circle_broken_fixture", broken_record),
    ]
    search = bounded_generator_search(
        [candidate for _, candidate in search_candidates],
        search_id="public_seed_rule_finite_circle_search",
    )
    (
        bounded_search_candidates,
        ranked_candidate_ids,
        ranked_exact_candidate_ids,
        ranked_shorter_candidate_ids,
    ) = _bounded_search_candidate_summary(search_candidates)
    best_exact_candidate_id = (
        ranked_exact_candidate_ids[0] if ranked_exact_candidate_ids else None
    )
    best_shorter_candidate_id = (
        ranked_shorter_candidate_ids[0] if ranked_shorter_candidate_ids else None
    )
    best_exact = search.best_exact
    best_shorter = search.best_shorter
    storage_accounting_ids = [
        "GEN-T0046",
        "GEN-T0047",
        "GEN-T0048",
        "GEN-T0049",
        "GEN-T0050",
    ]
    theorem_ids = list(record.theorem_ids) + list(search.theorem_ids) + storage_accounting_ids
    storage_saving_accounting = (
        comparison.storage_saving + comparison.generator_length
        == comparison.explicit_length
    )
    bounded_search_has_best_exact = best_exact is not None
    bounded_search_has_best_shorter = best_shorter is not None
    bounded_search_exact_count_positive = search.exact_candidate_count > 0
    bounded_search_candidate_count_positive = search.candidate_count > 0
    return {
        "id": "TH-AI-CONTRACT-SEED-RULE-001",
        "kind": "seed_rule_exact_regeneration",
        "status": "fixture",
        "source_paper": "papers/generative/PAPER_GEN_01_SEED_RULE_PROVENANCE.md",
        "theorem_ids": _jsonable(tuple(dict.fromkeys(theorem_ids))),
        "dictionary_ids": list(record.dictionary_ids),
        "fields": {
            "artifact_id": record.artifact_id,
            "fixture_n": n,
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
            "storage_saving": comparison.storage_saving,
            "storage_saving_positive": comparison.storage_saving_positive,
            "generator_shorter": comparison.generator_shorter,
            "generator_shorter_iff_positive_saving": (
                comparison.generator_shorter == comparison.storage_saving_positive
            ),
            "storage_saving_add_generator_length_eq_explicit_length": (
                storage_saving_accounting
            ),
            "bounded_search_id": search.search_id,
            "bounded_search_finite_search_space": search.finite_search_space,
            "bounded_search_candidate_count": search.candidate_count,
            "bounded_search_exact_candidate_count": search.exact_candidate_count,
            "bounded_search_exact_candidate_count_le_candidate_count": (
                search.exact_candidate_count <= search.candidate_count
            ),
            "bounded_search_has_best_exact": bounded_search_has_best_exact,
            "bounded_search_best_exact_exists_iff_exact_count_positive": (
                bounded_search_has_best_exact == bounded_search_exact_count_positive
            ),
            "bounded_search_best_exact_implies_candidate_count_positive": (
                (not bounded_search_has_best_exact)
                or bounded_search_candidate_count_positive
            ),
            "bounded_search_best_exact_artifact_id": (
                best_exact.artifact_id if best_exact is not None else None
            ),
            "bounded_search_best_exact_candidate_id": best_exact_candidate_id,
            "bounded_search_best_exact_regenerates": (
                best_exact.exact_regeneration if best_exact is not None else False
            ),
            "bounded_search_has_best_shorter": bounded_search_has_best_shorter,
            "bounded_search_best_shorter_artifact_id": (
                best_shorter.artifact_id if best_shorter is not None else None
            ),
            "bounded_search_best_shorter_candidate_id": best_shorter_candidate_id,
            "bounded_search_best_shorter_generator_shorter": (
                best_shorter.generator_shorter if best_shorter is not None else False
            ),
            "bounded_search_candidates": bounded_search_candidates,
            "bounded_search_candidate_ids_by_generator_length": ranked_candidate_ids,
            "bounded_search_exact_candidate_ids_by_generator_length": (
                ranked_exact_candidate_ids
            ),
            "bounded_search_shorter_candidate_ids_by_generator_length": (
                ranked_shorter_candidate_ids
            ),
            "bounded_search_note": search.note,
        },
        "contract_passed": (
            comparison.exact_regeneration
            and comparison.generator_shorter
            and comparison.storage_saving_positive
            and storage_saving_accounting
            and search.finite_search_space
            and search.exact_candidate_count <= search.candidate_count
            and bounded_search_has_best_exact
            and bounded_search_has_best_shorter
            and (bounded_search_has_best_exact == bounded_search_exact_count_positive)
            and ((not bounded_search_has_best_exact) or bounded_search_candidate_count_positive)
            and bool(best_exact and best_exact.exact_regeneration)
            and bool(best_shorter and best_shorter.generator_shorter)
        ),
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
