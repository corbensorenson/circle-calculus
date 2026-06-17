import json
import subprocess
import sys
from pathlib import Path

from circle_math.applications.circle_ai import (
    active_token_counts_by_budget,
    average_candidate_count,
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_batch,
    certify_kv_cache_live_window,
    certify_kv_cache_live_window_request,
    certify_kv_cache_window,
    certify_stride_family_coverage,
    consecutive_integer_intervals,
    coil_attention_path,
    content_route_label,
    fit_loop_budget_lookup,
    fit_loop_block_lookup,
    fit_content_route_lookup,
    fit_memory_slot_lookup,
    fit_recurrence_resolution_lookup,
    hybrid_attention_candidates,
    kv_cache_adapter_request_trace_pass_compact,
    kv_cache_batch_trace_fresh_iff_next_overwrite_boundary,
    kv_cache_distinct_retained_slots_distinct,
    kv_cache_live_window_length,
    kv_cache_ordered_live_window_subrequest,
    kv_cache_live_window_slot_range_covered,
    kv_cache_live_window_slots_distinct,
    kv_cache_live_window_start,
    kv_cache_live_window_tokens,
    kv_cache_next_overwrite_after_current,
    kv_cache_next_overwrite_token,
    kv_cache_no_same_slot_overwrite_before_current,
    kv_cache_batch_retained_iff_no_same_slot_overwrite_trace,
    kv_cache_retained_batch_slots_distinct,
    kv_cache_retained_iff_no_same_slot_overwrite_trace,
    kv_cache_retained_slots_distinct,
    kv_cache_same_slot_overwrite_witness_when_stale,
    kv_cache_slot,
    kv_cache_slots_collide,
    kv_cache_stale_by_next_overwrite_boundary,
    kv_cache_stale_iff_same_slot_overwrite_trace,
    kv_cache_trace_fresh_batch_slots_distinct,
    kv_cache_trace_fresh_iff_next_overwrite_boundary,
    kv_cache_window_contains,
    local_window_indices,
    loop_exit_certificate,
    loop_exit_step,
    loop_block_indices,
    loop_required_steps,
    loop_score_active,
    loop_score_trace,
    looped_recurrent_state,
    looped_recurrent_states,
    memory_slot,
    middle_block_required_blocks,
    middle_block_route,
    memory_slot_collision_count,
    memory_slot_loads,
    middle_block_budget_route,
    mixed_retrieval_target_lags,
    multi_resolution_required_resolutions,
    nonstructured_hybrid_control_lags,
    predict_loop_budget_lookup,
    predict_loop_block_lookup,
    predict_content_route_lookup,
    predict_memory_slot_lookup,
    predict_recurrence_resolution_lookup,
    retrieval_hit_rate_by_lag,
    retrieval_target_index,
    recurrence_resolution_levels,
    run_coil_retrieval_benchmark,
    run_content_gated_retrieval_benchmark,
    run_hybrid_sparse_attention_benchmark,
    run_learned_content_gate_retrieval_benchmark,
    run_learned_middle_block_recurrence_benchmark,
    run_learned_multi_resolution_recurrence_benchmark,
    run_learned_token_level_recurrence_benchmark,
    run_tiny_looped_recurrent_prototype,
    run_looped_recurrence_benchmark,
    run_learned_recurrence_schedule_benchmark,
    run_memory_slot_benchmark,
    run_middle_block_recurrence_benchmark,
    run_multi_resolution_recurrence_benchmark,
    run_stride_family_sparse_attention_benchmark,
    run_training_free_loop_wrapper_benchmark,
    run_token_level_recurrence_benchmark,
    shifted_recurrence_resolutions,
    stride_family_attention_candidates,
    stride_family_covered_lags,
    stride_family_coil_residue_list,
    stride_family_coil_residues_no_collision,
    stride_family_deduplicated_candidate_budget_bound,
    stride_family_head_coil_residues_disjoint_from_tail,
    stride_family_head_tail_no_wrap_separation_sufficient_condition,
    stride_family_lag_candidates_no_collision,
    stride_family_lag_candidate_list,
    stride_family_local_coil_candidates_disjoint,
    stride_family_no_wrap_separated_lag_no_collision_sufficient_condition,
    stride_family_no_wrap_separated_local_disjoint_sufficient_condition,
    stride_family_no_wrap_separated_query_no_collision_sufficient_condition,
    stride_family_no_wrap_separated_query_raw_budget_exact_sufficient_condition,
    stride_family_no_wrap_separated_sufficient_condition,
    stride_family_predecessor_injective_window_context_sufficient_condition,
    stride_family_predecessor_injective_on_lag_candidates,
    stride_family_query_candidates_no_collision,
    stride_family_query_candidate_list,
    stride_family_raw_candidate_budget,
    stride_family_single_stride_no_wrap_sufficient_condition,
    stride_family_unique_lag_candidate_count,
    stride_family_unique_query_candidate_count,
    structured_stride_family_target_lags,
    structured_hybrid_target_lags,
    token_active_at_step,
    synthetic_memory_slot_dataset,
    token_recurrence_budget,
    token_recurrence_budgets,
    training_free_loop_budget,
    training_free_loop_budgets,
)


def test_memory_slot_is_bounded() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            assert 0 <= memory_slot(bank_size, token) < bank_size


def test_kv_cache_ring_buffer_certificate_has_no_overwrite_before_read() -> None:
    certificate = certify_kv_cache_window(cache_size=16, current=31, token=20)
    assert certificate.slot == kv_cache_slot(16, 20) == 4
    assert certificate.current_slot == kv_cache_slot(16, 31) == 15
    assert certificate.lag == 11
    assert certificate.retained
    assert kv_cache_window_contains(16, 31, 20)
    assert not certificate.collision_with_current
    assert certificate.retained_noncurrent_slot_distinct_from_current
    assert certificate.next_overwrite_token == kv_cache_next_overwrite_token(16, 20) == 36
    assert certificate.next_overwrite_after_current
    assert kv_cache_next_overwrite_after_current(16, 31, 20)
    assert not certificate.stale_by_next_overwrite_boundary
    assert not kv_cache_stale_by_next_overwrite_boundary(16, 31, 20)
    assert certificate.no_same_slot_overwrite_before_current
    assert kv_cache_no_same_slot_overwrite_before_current(16, 31, 20)
    assert not certificate.same_slot_overwrite_witness_when_stale
    assert not kv_cache_same_slot_overwrite_witness_when_stale(16, 31, 20)
    assert certificate.stale_iff_same_slot_overwrite_trace
    assert kv_cache_stale_iff_same_slot_overwrite_trace(16, 31, 20)
    assert certificate.retained_iff_no_same_slot_overwrite_trace
    assert kv_cache_retained_iff_no_same_slot_overwrite_trace(16, 31, 20)
    assert certificate.trace_fresh_iff_next_overwrite_boundary
    assert kv_cache_trace_fresh_iff_next_overwrite_boundary(16, 31, 20)
    assert certificate.collision_with_next_overwrite
    assert kv_cache_slots_collide(16, 20, 36)
    assert not kv_cache_slots_collide(16, 20, 31)
    assert "AIM-T0063" in certificate.theorem_ids
    assert "AIM-T0064" in certificate.theorem_ids
    assert "AIM-T0065" in certificate.theorem_ids
    assert "AIM-T0066" in certificate.theorem_ids
    assert "AIM-T0069" in certificate.theorem_ids
    assert "AIM-T0070" in certificate.theorem_ids
    assert "AIM-T0075" in certificate.theorem_ids
    assert "AIM-T0076" in certificate.theorem_ids
    assert "AIM-T0091" in certificate.theorem_ids
    assert "AIM-T0099" in certificate.theorem_ids
    assert certificate.note.endswith("deployment safety.")


def test_kv_cache_retained_tokens_are_pairwise_slot_distinct() -> None:
    assert kv_cache_window_contains(16, 31, 20)
    assert kv_cache_window_contains(16, 31, 29)
    assert kv_cache_retained_slots_distinct(16, 31, 20, 29)
    assert kv_cache_distinct_retained_slots_distinct(16, 31, 20, 29)
    assert kv_cache_distinct_retained_slots_distinct(16, 31, 29, 20)
    assert kv_cache_slot(16, 20) != kv_cache_slot(16, 29)
    assert not kv_cache_retained_slots_distinct(16, 31, 29, 20)
    assert not kv_cache_distinct_retained_slots_distinct(16, 31, 20, 20)
    assert not kv_cache_retained_slots_distinct(16, 40, 20, 29)
    assert not kv_cache_distinct_retained_slots_distinct(16, 40, 20, 29)


def test_kv_cache_retained_batch_slots_are_distinct() -> None:
    certificate = certify_kv_cache_batch(cache_size=16, current=31, tokens=(20, 24, 29, 31))
    assert certificate.slots == (4, 8, 13, 15)
    assert certificate.all_retained
    assert certificate.tokens_distinct
    assert certificate.slots_distinct
    assert certificate.retained_iff_no_same_slot_overwrite_trace
    assert certificate.next_overwrites_after_current
    assert certificate.trace_fresh_iff_next_overwrite_boundary
    assert certificate.trace_fresh_slots_distinct
    assert kv_cache_retained_batch_slots_distinct(16, 31, (20, 24, 29, 31))
    assert kv_cache_batch_retained_iff_no_same_slot_overwrite_trace(
        16,
        31,
        (20, 24, 29, 31),
    )
    assert kv_cache_batch_trace_fresh_iff_next_overwrite_boundary(
        16,
        31,
        (20, 24, 29, 31),
    )
    assert kv_cache_trace_fresh_batch_slots_distinct(16, 31, (20, 24, 29, 31))
    assert not kv_cache_retained_batch_slots_distinct(16, 31, (20, 20, 29))
    assert not kv_cache_retained_batch_slots_distinct(16, 40, (20, 24, 29))
    assert "AIM-T0067" in certificate.theorem_ids
    assert "AIM-T0068" in certificate.theorem_ids
    assert "AIM-T0078" in certificate.theorem_ids
    assert "AIM-T0079" in certificate.theorem_ids
    assert "AIM-T0091" in certificate.theorem_ids
    assert "AIM-T0092" in certificate.theorem_ids
    assert "retained-batch slot certificate only" in certificate.note

    stale_batch = certify_kv_cache_batch(cache_size=16, current=40, tokens=(20, 24, 29))
    assert not stale_batch.all_retained
    assert stale_batch.retained_iff_no_same_slot_overwrite_trace
    assert not stale_batch.next_overwrites_after_current
    assert stale_batch.trace_fresh_iff_next_overwrite_boundary
    assert not stale_batch.trace_fresh_slots_distinct
    assert kv_cache_batch_retained_iff_no_same_slot_overwrite_trace(16, 40, (20, 24, 29))
    assert kv_cache_batch_trace_fresh_iff_next_overwrite_boundary(16, 40, (20, 24, 29))
    assert not kv_cache_trace_fresh_batch_slots_distinct(16, 40, (20, 24, 29))


def test_kv_cache_adapter_request_trace_packages_batch_contract() -> None:
    certificate = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(20, 24, 29, 31),
        request_id="prefill_read",
    )
    assert certificate.request_id == "prefill_read"
    assert certificate.requested_tokens == (20, 24, 29, 31)
    assert certificate.requested_slots == (4, 8, 13, 15)
    assert certificate.request_token_count == 4
    assert certificate.all_non_future
    assert certificate.all_retained
    assert certificate.tokens_distinct
    assert certificate.slots_distinct
    assert certificate.first_stale_token is None
    assert certificate.first_stale_next_overwrite_token is None
    assert not certificate.stale_member_blocks_pass
    assert certificate.retained_iff_no_same_slot_overwrite_trace
    assert certificate.next_overwrites_after_current
    assert certificate.trace_fresh_iff_next_overwrite_boundary
    assert certificate.trace_fresh_slots_distinct
    assert certificate.ordered_live_window_subrequest
    assert certificate.duplicate_free_live_window_subrequest
    assert certificate.live_window_subrequest_pass_contract
    assert certificate.pass_certificate
    assert certificate.pass_iff_next_overwrite_boundary
    assert certificate.pass_iff_no_stale_member_under_nonfuture_nodup
    assert certificate.fail_iff_stale_member_under_nonfuture_nodup
    assert kv_cache_adapter_request_trace_pass_compact(16, 31, (20, 24, 29, 31))
    assert kv_cache_ordered_live_window_subrequest(16, 31, (20, 24, 29, 31))
    assert "AIM-T0078" in certificate.theorem_ids
    assert "AIM-T0079" in certificate.theorem_ids
    assert "AIM-T0086" in certificate.theorem_ids
    assert "AIM-T0091" in certificate.theorem_ids
    assert "AIM-T0092" in certificate.theorem_ids
    assert "AIM-T0093" in certificate.theorem_ids
    assert "AIM-T0094" in certificate.theorem_ids
    assert "AIM-T0095" in certificate.theorem_ids
    assert "AIM-T0096" in certificate.theorem_ids
    assert "AIM-T0097" in certificate.theorem_ids
    assert "AIM-T0098" in certificate.theorem_ids
    assert "AIM-T0100" in certificate.theorem_ids
    assert (
        "Circle.Applications.kvCacheLiveWindowSubrequest_adapterRequestTracePass"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheAdapterRequestBoundary_allRetained"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheAdapterRequestBoundary_slotMap_nodup"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_kvCacheAdapterRequestTracePass_of_stale_member"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheAdapterRequestTracePass_iff_no_stale_member_of_nonFuture_nodup"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_kvCacheAdapterRequestTracePass_iff_exists_stale_member_of_nonFuture_nodup"
        in certificate.lean_declarations
    )
    assert "Modeled adapter request-trace certificate only" in certificate.note

    future_request = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(20, 32),
    )
    assert not future_request.all_non_future
    assert not future_request.all_retained
    assert future_request.next_overwrites_after_current
    assert not future_request.trace_fresh_iff_next_overwrite_boundary
    assert not future_request.ordered_live_window_subrequest
    assert not future_request.duplicate_free_live_window_subrequest
    assert not future_request.live_window_subrequest_pass_contract
    assert not future_request.pass_certificate
    assert future_request.pass_iff_next_overwrite_boundary
    assert not future_request.pass_iff_no_stale_member_under_nonfuture_nodup
    assert not future_request.fail_iff_stale_member_under_nonfuture_nodup
    assert future_request.first_stale_token is None
    assert future_request.first_stale_next_overwrite_token is None
    assert not future_request.stale_member_blocks_pass
    assert not kv_cache_adapter_request_trace_pass_compact(16, 31, (20, 32))

    stale_request = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(12, 20),
        request_id="stale_read",
    )
    assert stale_request.request_id == "stale_read"
    assert stale_request.all_non_future
    assert not stale_request.all_retained
    assert stale_request.tokens_distinct
    assert not stale_request.slots_distinct
    assert stale_request.first_stale_token == 12
    assert stale_request.first_stale_next_overwrite_token == 28
    assert stale_request.stale_member_blocks_pass
    assert not stale_request.next_overwrites_after_current
    assert stale_request.trace_fresh_iff_next_overwrite_boundary
    assert not stale_request.trace_fresh_slots_distinct
    assert not stale_request.ordered_live_window_subrequest
    assert not stale_request.duplicate_free_live_window_subrequest
    assert not stale_request.live_window_subrequest_pass_contract
    assert not stale_request.pass_certificate
    assert stale_request.pass_iff_next_overwrite_boundary
    assert stale_request.pass_iff_no_stale_member_under_nonfuture_nodup
    assert stale_request.fail_iff_stale_member_under_nonfuture_nodup
    assert not kv_cache_adapter_request_trace_pass_compact(16, 31, (12, 20))

    duplicate_request = certify_kv_cache_adapter_request_trace(
        cache_size=16,
        current=31,
        requested_tokens=(20, 20),
    )
    assert duplicate_request.all_non_future
    assert duplicate_request.all_retained
    assert not duplicate_request.tokens_distinct
    assert not duplicate_request.slots_distinct
    assert duplicate_request.next_overwrites_after_current
    assert duplicate_request.trace_fresh_iff_next_overwrite_boundary
    assert not duplicate_request.ordered_live_window_subrequest
    assert not duplicate_request.duplicate_free_live_window_subrequest
    assert not duplicate_request.live_window_subrequest_pass_contract
    assert not duplicate_request.pass_certificate
    assert duplicate_request.pass_iff_next_overwrite_boundary
    assert not duplicate_request.pass_iff_no_stale_member_under_nonfuture_nodup
    assert not duplicate_request.fail_iff_stale_member_under_nonfuture_nodup
    assert duplicate_request.first_stale_token is None
    assert duplicate_request.first_stale_next_overwrite_token is None
    assert not duplicate_request.stale_member_blocks_pass
    assert not kv_cache_adapter_request_trace_pass_compact(16, 31, (20, 20))


def test_kv_cache_live_window_tokens_are_exact_and_slot_distinct() -> None:
    certificate = certify_kv_cache_live_window(cache_size=16, current=31)
    assert certificate.start == kv_cache_live_window_start(16, 31) == 16
    assert certificate.length == kv_cache_live_window_length(16, 31) == 16
    assert certificate.tokens == kv_cache_live_window_tokens(16, 31) == tuple(range(16, 32))
    assert certificate.slots == tuple(range(16))
    assert certificate.all_tokens_retained
    assert certificate.slots_distinct
    assert certificate.full_window
    assert certificate.slots_within_cache
    assert certificate.slot_count_matches_cache_size
    assert certificate.slot_count_matches_full_window
    assert certificate.slot_range_covered
    assert certificate.full_coverage_contract
    assert certificate.full_coverage_contract_matches_full_window
    assert kv_cache_live_window_slots_distinct(16, 31)
    assert kv_cache_live_window_slot_range_covered(16, 31)
    assert "AIM-T0071" in certificate.theorem_ids
    assert "AIM-T0072" in certificate.theorem_ids
    assert "AIM-T0073" in certificate.theorem_ids
    assert "AIM-T0074" in certificate.theorem_ids
    assert "AIM-T0080" in certificate.theorem_ids
    assert "AIM-T0081" in certificate.theorem_ids
    assert "AIM-T0082" in certificate.theorem_ids
    assert "AIM-T0083" in certificate.theorem_ids
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotMap_nodup"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotMap_fullCoverageContract"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotMap_length_eq_cacheSize_iff_full"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotMap_fullCoverageContract_iff_full"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotMap_mem_iff_lt_cacheSize_of_full"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_slotRangeCovered_iff_full"
        in certificate.lean_declarations
    )

    prefix = certify_kv_cache_live_window(cache_size=16, current=5)
    assert prefix.start == 0
    assert prefix.length == 6
    assert prefix.tokens == tuple(range(6))
    assert prefix.slots == tuple(range(6))
    assert prefix.all_tokens_retained
    assert prefix.slots_distinct
    assert not prefix.full_window
    assert prefix.slots_within_cache
    assert not prefix.slot_count_matches_cache_size
    assert prefix.slot_count_matches_full_window
    assert not prefix.slot_range_covered
    assert not prefix.full_coverage_contract
    assert prefix.full_coverage_contract_matches_full_window
    assert not kv_cache_live_window_slot_range_covered(16, 5)


def test_kv_cache_live_window_request_is_exact_and_passes() -> None:
    certificate = certify_kv_cache_live_window_request(cache_size=16, current=31)
    assert certificate.request_id == "generated_live_window_read"
    assert certificate.requested_tokens == tuple(range(16, 32))
    assert certificate.live_window_tokens == tuple(range(16, 32))
    assert certificate.requested_slots == tuple(range(16))
    assert certificate.exact_live_window_request
    assert certificate.request_token_count == 16
    assert certificate.all_non_future
    assert certificate.all_retained
    assert certificate.tokens_distinct
    assert certificate.slots_distinct
    assert certificate.pass_certificate
    assert certificate.live_window_request_contract
    assert "AIM-T0087" in certificate.theorem_ids
    assert "AIM-T0088" in certificate.theorem_ids
    assert "AIM-T0089" in certificate.fixture_theorem_ids
    assert (
        "Circle.Applications.kvCacheLiveWindowTokens_adapterRequestTracePass"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.kvCacheLiveWindowRequestTraceContract_iff_tokens_eq_liveWindow"
        in certificate.lean_declarations
    )

    prefix = certify_kv_cache_live_window_request(cache_size=16, current=5)
    assert prefix.requested_tokens == tuple(range(6))
    assert prefix.live_window_tokens == tuple(range(6))
    assert prefix.requested_slots == tuple(range(6))
    assert prefix.exact_live_window_request
    assert prefix.pass_certificate
    assert prefix.live_window_request_contract
    assert prefix.fixture_theorem_ids == ()


def test_kv_cache_ring_buffer_certificate_marks_stale_token() -> None:
    certificate = certify_kv_cache_window(cache_size=16, current=40, token=20)
    assert certificate.lag == 20
    assert not certificate.retained
    assert not kv_cache_window_contains(16, 40, 20)
    assert not certificate.next_overwrite_after_current
    assert not kv_cache_next_overwrite_after_current(16, 40, 20)
    assert certificate.stale_by_next_overwrite_boundary
    assert kv_cache_stale_by_next_overwrite_boundary(16, 40, 20)
    assert not certificate.no_same_slot_overwrite_before_current
    assert not kv_cache_no_same_slot_overwrite_before_current(16, 40, 20)
    assert certificate.same_slot_overwrite_witness_when_stale
    assert kv_cache_same_slot_overwrite_witness_when_stale(16, 40, 20)
    assert certificate.stale_iff_same_slot_overwrite_trace
    assert kv_cache_stale_iff_same_slot_overwrite_trace(16, 40, 20)
    assert certificate.retained_iff_no_same_slot_overwrite_trace
    assert kv_cache_retained_iff_no_same_slot_overwrite_trace(16, 40, 20)
    assert certificate.trace_fresh_iff_next_overwrite_boundary
    assert kv_cache_trace_fresh_iff_next_overwrite_boundary(16, 40, 20)
    assert certificate.next_overwrite_token == 36
    assert not certificate.retained_noncurrent_slot_distinct_from_current


def test_kv_cache_ring_buffer_certificate_marks_current_token_collision_as_self() -> None:
    certificate = certify_kv_cache_window(cache_size=16, current=31, token=31)
    assert certificate.retained
    assert certificate.lag == 0
    assert certificate.slot == certificate.current_slot
    assert certificate.collision_with_current
    assert not certificate.retained_noncurrent_slot_distinct_from_current


def test_kv_cache_ring_buffer_sidecar_emits_json_and_markdown() -> None:
    json_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(json_result.stdout)
    assert payload["schema_id"] == "circle_calculus.kv_cache_ring_buffer_certificate.v0"
    assert payload["window_certificate"]["slot"] == 4
    assert payload["window_certificate"]["next_overwrite_after_current"] is True
    assert payload["window_certificate"]["no_same_slot_overwrite_before_current"] is True
    assert payload["window_certificate"]["same_slot_overwrite_witness_when_stale"] is False
    assert payload["window_certificate"]["stale_iff_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert "AIM-T0069" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0075" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0076" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0077" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0099" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0091" in payload["window_certificate"]["theorem_ids"]
    assert payload["batch_certificate"]["slots_distinct"] is True
    assert payload["batch_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["batch_certificate"]["next_overwrites_after_current"] is True
    assert payload["batch_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["batch_certificate"]["trace_fresh_slots_distinct"] is True
    assert "AIM-T0068" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0078" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0079" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0091" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0092" in payload["batch_certificate"]["theorem_ids"]
    assert payload["adapter_request_trace_certificate"]["request_id"] == "default_read_request"
    assert payload["adapter_request_trace_certificate"]["requested_slots"] == [4, 8, 13, 15]
    assert payload["adapter_request_trace_certificate"]["pass_certificate"] is True
    assert payload["adapter_request_trace_certificate"]["next_overwrites_after_current"] is True
    assert payload["adapter_request_trace_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["adapter_request_trace_certificate"]["pass_iff_next_overwrite_boundary"] is True
    assert (
        payload["adapter_request_trace_certificate"][
            "pass_iff_no_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert (
        payload["adapter_request_trace_certificate"][
            "fail_iff_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert payload["adapter_request_trace_certificate"]["ordered_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["duplicate_free_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["live_window_subrequest_pass_contract"] is True
    assert "AIM-T0078" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0079" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0086" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0091" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0092" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0093" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0094" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0095" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0096" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0100" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert payload["live_window_certificate"]["start"] == 16
    assert payload["live_window_certificate"]["length"] == 16
    assert payload["live_window_certificate"]["slots_distinct"] is True
    assert payload["live_window_certificate"]["full_window"] is True
    assert payload["live_window_certificate"]["slot_count_matches_full_window"] is True
    assert payload["live_window_certificate"]["slot_range_covered"] is True
    assert payload["live_window_certificate"]["full_coverage_contract"] is True
    assert payload["live_window_certificate"]["full_coverage_contract_matches_full_window"] is True
    assert "AIM-T0073" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0074" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0080" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0081" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0082" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0083" in payload["live_window_certificate"]["theorem_ids"]
    assert payload["live_window_request_certificate"]["request_id"] == "generated_live_window_read"
    assert payload["live_window_request_certificate"]["requested_tokens"] == list(range(16, 32))
    assert payload["live_window_request_certificate"]["requested_slots"] == list(range(16))
    assert payload["live_window_request_certificate"]["exact_live_window_request"] is True
    assert payload["live_window_request_certificate"]["pass_certificate"] is True
    assert payload["live_window_request_certificate"]["live_window_request_contract"] is True
    assert "AIM-T0087" in payload["live_window_request_certificate"]["theorem_ids"]
    assert "AIM-T0088" in payload["live_window_request_certificate"]["theorem_ids"]
    assert "AIM-T0089" in payload["live_window_request_certificate"]["fixture_theorem_ids"]
    assert "not model-quality" in payload["claim_boundary"]

    markdown_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py",
            "--format",
            "markdown",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "KV-Cache Ring-Buffer Certificate Results" in markdown_result.stdout
    assert "| 16 | 31 | 20 | 4 | 15 | 11 | True | True | 36 | True | False | True | False | True | True |" in markdown_result.stdout
    assert "Batch tokens" in markdown_result.stdout
    assert "Request id" in markdown_result.stdout
    assert "default_read_request" in markdown_result.stdout
    assert "Pass certificate" in markdown_result.stdout
    assert "Stale iff later same-slot write" in markdown_result.stdout
    assert "Retained iff no later same-slot writes" in markdown_result.stdout
    assert "Trace iff boundary" in markdown_result.stdout
    assert "Next overwrites after current" in markdown_result.stdout
    assert "Pass iff boundary" in markdown_result.stdout
    assert "Trace-fresh slots distinct" in markdown_result.stdout
    assert "Ordered live-window subrequest" in markdown_result.stdout
    assert "Subrequest pass contract" in markdown_result.stdout
    assert "Live start" in markdown_result.stdout
    assert "Exact live-window request" in markdown_result.stdout
    assert "generated_live_window_read" in markdown_result.stdout
    assert "AIM-T0073" in markdown_result.stdout
    assert "AIM-T0074" in markdown_result.stdout
    assert "AIM-T0075" in markdown_result.stdout
    assert "AIM-T0076" in markdown_result.stdout
    assert "AIM-T0077" in markdown_result.stdout
    assert "AIM-T0078" in markdown_result.stdout
    assert "AIM-T0079" in markdown_result.stdout
    assert "AIM-T0087" in markdown_result.stdout
    assert "AIM-T0088" in markdown_result.stdout
    assert "AIM-T0089" in markdown_result.stdout
    assert "AIM-T0091" in markdown_result.stdout
    assert "AIM-T0092" in markdown_result.stdout
    assert "AIM-T0093" in markdown_result.stdout
    assert "AIM-T0094" in markdown_result.stdout
    assert "AIM-T0095" in markdown_result.stdout
    assert "AIM-T0096" in markdown_result.stdout


def test_committed_kv_cache_ring_buffer_results_match_generator(tmp_path: Path) -> None:
    generated_json = tmp_path / "kv_cache_ring_buffer.json"
    generated_markdown = tmp_path / "kv_cache_ring_buffer.md"
    subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py",
            "--json-out",
            str(generated_json),
            "--markdown-out",
            str(generated_markdown),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    committed_json = Path(
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/kv_cache_ring_buffer.json"
    )
    committed_markdown = Path(
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/kv_cache_ring_buffer.md"
    )
    assert json.loads(committed_json.read_text()) == json.loads(generated_json.read_text())
    assert committed_markdown.read_text() == generated_markdown.read_text()


def test_memory_slot_closes_after_bank_size() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            assert memory_slot(bank_size, token + bank_size) == memory_slot(bank_size, token)


def test_memory_slot_closes_after_multiple_bank_passes() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 128):
            for passes in range(0, 9):
                assert memory_slot(bank_size, token + passes * bank_size) == memory_slot(bank_size, token)


def test_memory_slot_is_idempotent() -> None:
    for bank_size in range(1, 65):
        for token in range(0, 512):
            normalized = memory_slot(bank_size, token)
            assert memory_slot(bank_size, normalized) == normalized


def test_memory_slot_zero() -> None:
    for bank_size in range(1, 65):
        assert memory_slot(bank_size, 0) == 0


def test_memory_slot_lookup_recovers_periodic_fixture() -> None:
    tokens, labels = synthetic_memory_slot_dataset(8, 64)
    lookup = fit_memory_slot_lookup(8, tokens, labels)
    test_tokens, test_labels = synthetic_memory_slot_dataset(8, 16, start=64)
    assert predict_memory_slot_lookup(8, lookup, test_tokens) == test_labels


def test_memory_slot_collision_diagnostics_are_deterministic() -> None:
    tokens = tuple(range(0, 20))
    assert memory_slot_loads(8, tokens) == (3, 3, 3, 3, 2, 2, 2, 2)
    assert memory_slot_collision_count(8, tokens) == 12


def test_memory_slot_benchmark_has_baseline_and_negative_control() -> None:
    result = run_memory_slot_benchmark(bank_size=8, train_length=64, test_length=32)
    assert result == run_memory_slot_benchmark(bank_size=8, train_length=64, test_length=32)
    assert result.cyclic_memory_accuracy == 1.0
    assert result.constant_accuracy < result.cyclic_memory_accuracy
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_cyclic_memory_accuracy
    assert result.train_collision_count == 56
    assert result.max_train_slot_load == 8
    assert result.note.endswith("not a model-quality claim.")


def test_coil_attention_path_indices_are_bounded() -> None:
    for query_index in range(0, 128):
        path = coil_attention_path(sequence_length=64, query_index=query_index, stride=7, path_length=3)
        assert len(path) == 3
        assert all(0 <= index < 64 for index in path)


def test_coil_attention_path_reaches_constructed_lag() -> None:
    sequence_length = 64
    query_index = 42
    target_lag = 21
    path = coil_attention_path(sequence_length, query_index, stride=7, path_length=3)
    local = local_window_indices(sequence_length, query_index, window=8)
    target = retrieval_target_index(sequence_length, query_index, target_lag)

    assert target in path
    assert target not in local


def test_coil_retrieval_benchmark_has_baselines_and_near_control() -> None:
    result = run_coil_retrieval_benchmark(
        sequence_length=64,
        query_count=64,
        target_lag=21,
        stride=7,
        path_length=3,
        local_window=8,
        wrong_stride=5,
        near_control_lag=3,
    )

    assert result.coil_path_accuracy == 1.0
    assert result.full_attention_accuracy == 1.0
    assert result.local_window_accuracy == 0.0
    assert result.wrong_stride_accuracy == 0.0
    assert result.near_control_local_window_accuracy == 1.0
    assert result.near_control_full_attention_accuracy == 1.0
    assert result.near_control_coil_path_accuracy == 0.0


def test_mixed_retrieval_target_lags_and_budget_helpers_are_deterministic() -> None:
    queries = tuple(range(6))
    target_lags = mixed_retrieval_target_lags(queries, long_target_lag=21, near_target_lag=3)
    candidate_sets = (
        (1, 2, 3),
        (4, 5),
        (7, 7, 8),
        (9,),
        (10, 11, 12),
        (13, 14),
    )

    assert target_lags == (21, 3, 21, 3, 21, 3)
    assert average_candidate_count(candidate_sets) == 13 / 6
    assert retrieval_hit_rate_by_lag(
        64,
        (24,),
        (21,),
        ((3, 17, 45),),
    ) == 1.0


def test_content_gated_retrieval_benchmark_has_route_and_budget_baselines() -> None:
    result = run_content_gated_retrieval_benchmark(
        sequence_length=64,
        query_count=64,
        long_target_lag=21,
        near_target_lag=3,
        stride=7,
        path_length=3,
        local_window=8,
    )

    assert result == run_content_gated_retrieval_benchmark(
        sequence_length=64,
        query_count=64,
        long_target_lag=21,
        near_target_lag=3,
        stride=7,
        path_length=3,
        local_window=8,
    )
    assert result.content_gated_accuracy == 1.0
    assert result.union_candidate_accuracy == 1.0
    assert result.full_attention_accuracy == 1.0
    assert result.static_coil_accuracy == 0.5
    assert result.static_local_accuracy == 0.5
    assert result.wrong_gate_accuracy == 0.0
    assert result.average_gated_candidate_count == 5.5
    assert result.average_union_candidate_count == 10.0
    assert result.average_full_candidate_count == 64.0
    assert result.note.endswith("not a model-quality claim.")


def test_hybrid_attention_candidates_union_local_and_coil_paths() -> None:
    candidates = hybrid_attention_candidates(
        sequence_length=96,
        query_index=50,
        stride=11,
        path_length=4,
        local_window=5,
    )

    assert candidates == (49, 48, 47, 46, 45, 39, 28, 17, 6)
    assert retrieval_target_index(96, 50, 3) in candidates
    assert retrieval_target_index(96, 50, 22) in candidates
    assert retrieval_target_index(96, 50, 44) in candidates


def test_hybrid_sparse_attention_benchmark_has_budget_and_negative_control() -> None:
    queries = tuple(range(6))
    assert structured_hybrid_target_lags(queries, stride=11, path_length=4, local_window=5) == (
        3,
        22,
        44,
        3,
        22,
        44,
    )
    assert nonstructured_hybrid_control_lags(queries, sequence_length=96) == (14, 21, 28, 35, 42, 49)

    result = run_hybrid_sparse_attention_benchmark(
        sequence_length=96,
        query_count=96,
        stride=11,
        path_length=4,
        local_window=5,
        wrong_stride=8,
    )

    assert result == run_hybrid_sparse_attention_benchmark(
        sequence_length=96,
        query_count=96,
        stride=11,
        path_length=4,
        local_window=5,
        wrong_stride=8,
    )
    assert result.hybrid_accuracy == 1.0
    assert result.full_attention_accuracy == 1.0
    assert result.local_window_accuracy == 1 / 3
    assert result.coil_path_accuracy == 2 / 3
    assert result.wrong_stride_hybrid_accuracy == 1 / 3
    assert result.average_hybrid_candidate_count == 9.0
    assert result.average_full_candidate_count == 96.0
    assert result.nonstructured_full_attention_accuracy == 1.0
    assert result.nonstructured_hybrid_accuracy < result.nonstructured_full_attention_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_stride_family_attention_candidates_union_multiple_coils() -> None:
    candidates = stride_family_attention_candidates(
        sequence_length=120,
        query_index=50,
        strides=(7, 13),
        path_length=3,
        local_window=4,
    )

    assert candidates == (49, 48, 47, 46, 43, 36, 29, 37, 24, 11)
    assert retrieval_target_index(120, 50, 3) in candidates
    assert retrieval_target_index(120, 50, 14) in candidates
    assert retrieval_target_index(120, 50, 26) in candidates
    assert retrieval_target_index(120, 50, 39) in candidates
    assert stride_family_covered_lags(120, (7, 13), 3, 4) == (1, 2, 3, 4, 7, 14, 21, 13, 26, 39)


def test_consecutive_integer_intervals_compress_gap_lists() -> None:
    assert consecutive_integer_intervals(()) == ()
    assert consecutive_integer_intervals((5, 6, 8, 9, 10, 12)) == ((5, 6), (8, 10), (12, 12))


def test_stride_family_sparse_attention_benchmark_has_budget_and_negative_control() -> None:
    queries = tuple(range(8))
    assert structured_stride_family_target_lags(
        queries,
        strides=(7, 13),
        path_length=3,
        local_window=4,
    ) == (3, 14, 26, 39, 3, 14, 26, 39)

    result = run_stride_family_sparse_attention_benchmark(
        sequence_length=120,
        query_count=120,
        strides=(7, 13),
        wrong_strides=(5, 9),
        path_length=3,
        local_window=4,
    )

    assert result == run_stride_family_sparse_attention_benchmark(
        sequence_length=120,
        query_count=120,
        strides=(7, 13),
        wrong_strides=(5, 9),
        path_length=3,
        local_window=4,
    )
    assert result.family_accuracy == 1.0
    assert result.full_attention_accuracy == 1.0
    assert result.local_window_accuracy == 0.25
    assert result.single_stride_accuracy == 0.5
    assert result.wrong_family_accuracy == 0.25
    assert result.average_family_candidate_count == 10.0
    assert result.average_single_stride_candidate_count == 7.0
    assert result.average_local_candidate_count == 4.0
    assert result.average_full_candidate_count == 120.0
    assert result.coverage_certificate == certify_stride_family_coverage(120, (7, 13), 3, 4)
    assert result.coverage_certificate.covered_lags == (1, 2, 3, 4, 7, 14, 21, 13, 26, 39)
    assert result.coverage_certificate.covered_lag_count == 10
    assert result.coverage_certificate.uncovered_lag_count == 109
    assert result.coverage_certificate.positive_lag_count == 119
    assert result.coverage_certificate.covered_uncovered_count_sum == 119
    assert result.coverage_certificate.covered_uncovered_count_partition
    assert not result.coverage_certificate.covered_count_certifies_complete
    assert result.coverage_certificate.uncovered_lags[:5] == (5, 6, 8, 9, 10)
    assert result.coverage_certificate.uncovered_lag_intervals == (
        (5, 6),
        (8, 12),
        (15, 20),
        (22, 25),
        (27, 38),
        (40, 119),
    )
    assert result.coverage_certificate.uncovered_lag_interval_count == 6
    assert not result.coverage_certificate.coverage_complete
    assert result.coverage_certificate.candidate_budget_per_query == 10
    assert result.coverage_certificate.raw_candidate_budget_upper_bound == 10
    assert result.coverage_certificate.raw_budget_shortfall_certifies_incomplete
    assert result.coverage_certificate.deduplicated_candidate_budget_upper_bound == 10
    assert result.coverage_certificate.theorem_side_unique_lag_candidate_count == 10
    assert result.coverage_certificate.theorem_side_lag_candidates_positive_in_context
    assert not (
        result.coverage_certificate.no_wrap_separated_candidate_range_sufficient_condition
    )
    assert result.coverage_certificate.no_zero_residue_candidate_range_sufficient_condition
    assert result.coverage_certificate.singleton_stride_period is None
    assert result.coverage_certificate.singleton_no_zero_period_threshold is None
    assert (
        result.coverage_certificate.singleton_no_zero_period_threshold_matches_condition
    )
    assert result.coverage_certificate.stride_family_periods == (120, 120)
    assert result.coverage_certificate.no_zero_period_thresholds == (True, True)
    assert result.coverage_certificate.stride_family_zero_residue_step_counts == (0, 0)
    assert result.coverage_certificate.zero_residue_step_counts_match_period_formula
    assert result.coverage_certificate.stride_family_zero_residue_total_step_count == 0
    assert result.coverage_certificate.zero_residue_total_count_matches_sum_formula
    assert (
        result.coverage_certificate
        .zero_residue_total_count_zero_matches_no_zero_condition
    )
    assert (
        result.coverage_certificate.no_zero_period_threshold_candidate_range_sufficient_condition
    )
    assert result.coverage_certificate.no_zero_period_threshold_matches_condition
    assert result.coverage_certificate.no_zero_period_violation_witness_stride is None
    assert result.coverage_certificate.no_zero_period_violation_witness_period is None
    assert result.coverage_certificate.no_zero_period_violation_witness_step is None
    assert result.coverage_certificate.no_zero_period_violation_witness_residue is None
    assert result.coverage_certificate.zero_residue_witness_matches_period_threshold
    assert result.coverage_certificate.zero_residue_witness_matches_no_zero_failure
    assert result.coverage_certificate.period_threshold_violation_matches_no_zero_failure
    assert result.coverage_certificate.no_zero_period_violation_witness_is_first_zero
    assert result.coverage_certificate.no_zero_period_violation_witness_step_positive
    assert result.coverage_certificate.unique_lag_count_shortfall_certifies_incomplete
    assert (
        result.coverage_certificate
        .unique_lag_count_shortfall_matches_gap_witness_under_period_threshold
    )
    assert result.coverage_certificate.unique_lag_count_matches_complete_under_candidate_range
    assert result.coverage_certificate.covered_count_matches_unique_lag_count_under_candidate_range
    assert (
        result.coverage_certificate.uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range
    )
    assert result.coverage_certificate.theorem_side_lag_candidates == (
        1,
        2,
        3,
        4,
        7,
        14,
        21,
        13,
        26,
        39,
    )
    assert result.coverage_certificate.theorem_side_lag_candidates == (
        stride_family_lag_candidate_list(120, (7, 13), 3, 4)
    )
    assert stride_family_coil_residue_list(120, (7, 13), 3) == (7, 14, 21, 13, 26, 39)
    assert result.coverage_certificate.theorem_side_coil_residues_no_collision
    assert result.coverage_certificate.theorem_side_coil_residues_no_collision == (
        stride_family_coil_residues_no_collision(120, (7, 13), 3)
    )
    assert result.coverage_certificate.theorem_side_local_coil_disjoint
    assert result.coverage_certificate.theorem_side_local_coil_disjoint == (
        stride_family_local_coil_candidates_disjoint(120, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_lag_candidate_count == 10
    assert result.coverage_certificate.theorem_side_unique_lag_candidate_count == (
        stride_family_unique_lag_candidate_count(120, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_lag_candidate_count <= (
        result.coverage_certificate.raw_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.theorem_side_lag_candidates_no_collision
    assert result.coverage_certificate.theorem_side_lag_candidates_no_collision == (
        stride_family_lag_candidates_no_collision(120, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_lag_candidate_count == (
        result.coverage_certificate.raw_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.theorem_side_query_candidates == (
        119,
        118,
        117,
        116,
        113,
        106,
        99,
        107,
        94,
        81,
    )
    assert result.coverage_certificate.theorem_side_query_candidates == (
        stride_family_query_candidate_list(120, 0, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_predecessor_injective_on_lag_candidates
    assert result.coverage_certificate.theorem_side_predecessor_injective_on_lag_candidates == (
        stride_family_predecessor_injective_on_lag_candidates(120, 0, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count == 10
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count == (
        stride_family_unique_query_candidate_count(120, 0, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count <= (
        result.coverage_certificate.raw_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count <= (
        result.coverage_certificate.deduplicated_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.theorem_side_query_count_le_unique_lag_count
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count <= (
        result.coverage_certificate.theorem_side_unique_lag_candidate_count
    )
    assert result.coverage_certificate.theorem_side_query_count_matches_unique_lag_count
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count == (
        result.coverage_certificate.theorem_side_unique_lag_candidate_count
    )
    assert (
        result.coverage_certificate
        .unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective
    )
    assert (
        result.coverage_certificate.unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated
    )
    assert (
        result.coverage_certificate.unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue
    )
    assert (
        result.coverage_certificate
        .unique_query_count_shortfall_matches_gap_witness_under_period_threshold
    )
    assert result.coverage_certificate.theorem_side_query_candidates_no_collision
    assert result.coverage_certificate.theorem_side_query_candidates_no_collision == (
        stride_family_query_candidates_no_collision(120, 0, (7, 13), 3, 4)
    )
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count == (
        result.coverage_certificate.raw_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.theorem_side_unique_query_candidate_count == (
        result.coverage_certificate.candidate_budget_per_query
    )
    assert result.coverage_certificate.deduplicated_candidate_budget_upper_bound == (
        stride_family_deduplicated_candidate_budget_bound(
            sequence_length=120,
            strides=(7, 13),
            path_length=3,
            local_window=4,
        )
    )
    assert result.coverage_certificate.candidate_budget_per_query <= (
        result.coverage_certificate.deduplicated_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.fixture_theorem_ids == (
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0091",
        "AIT-T0102",
        "AIT-T0104",
    )
    assert result.coverage_certificate.full_attention_budget == 120
    assert result.coverage_certificate.deduplicated_candidate_budget_upper_bound <= (
        result.coverage_certificate.raw_candidate_budget_upper_bound
    )
    assert result.coverage_certificate.deduplicated_candidate_budget_upper_bound <= (
        result.coverage_certificate.full_attention_budget
    )
    assert result.coverage_certificate.theorem_ids == (
        "AIT-T0016",
        "AIT-T0017",
        "AIT-T0020",
        "AIT-T0021",
        "AIT-T0022",
        "AIT-T0023",
        "AIT-T0024",
        "AIT-T0025",
        "AIT-T0028",
        "AIT-T0029",
        "AIT-T0030",
        "AIT-T0031",
        "AIT-T0032",
        "AIT-T0033",
        "AIT-T0034",
        "AIT-T0035",
        "AIT-T0036",
        "AIT-T0037",
        "AIT-T0038",
        "AIT-T0039",
        "AIT-T0040",
        "AIT-T0041",
        "AIT-T0042",
        "AIT-T0043",
        "AIT-T0044",
        "AIT-T0045",
        "AIT-T0046",
        "AIT-T0047",
        "AIT-T0048",
        "AIT-T0049",
        "AIT-T0050",
        "AIT-T0051",
        "AIT-T0052",
        "AIT-T0053",
        "AIT-T0054",
        "AIT-T0055",
        "AIT-T0056",
        "AIT-T0057",
        "AIT-T0058",
        "AIT-T0059",
        "AIT-T0060",
        "AIT-T0061",
        "AIT-T0062",
        "AIT-T0063",
        "AIT-T0064",
        "AIT-T0065",
        "AIT-T0066",
        "AIT-T0067",
        "AIT-T0068",
        "AIT-T0069",
        "AIT-T0070",
        "AIT-T0071",
        "AIT-T0072",
        "AIT-T0073",
        "AIT-T0074",
        "AIT-T0075",
        "AIT-T0076",
        "AIT-T0077",
        "AIT-T0078",
        "AIT-T0079",
        "AIT-T0080",
        "AIT-T0081",
        "AIT-T0082",
        "AIT-T0083",
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0090",
        "AIT-T0092",
        "AIT-T0093",
        "AIT-T0094",
        "AIT-T0095",
        "AIT-T0096",
        "AIT-T0097",
        "AIT-T0098",
        "AIT-T0099",
        "AIT-T0100",
        "AIT-T0101",
        "AIT-T0102",
        "AIT-T0103",
        "AIT-T0104",
        "AIT-T0105",
        "AIT-T0106",
        "AIT-T0107",
        "AIT-T0108",
        "AIT-T0109",
        "AIT-T0110",
        "AIT-T0111",
        "AIT-T0112",
        "AIT-T0113",
        "AIT-T0114",
        "AIT-T0115",
        "AIT-T0116",
        "AIT-T0117",
        "AIT-T0118",
        "AIT-T0119",
        "AIT-T0120",
        "AIT-T0121",
        "AIT-T0122",
        "AIT-T0123",
        "AIT-T0124",
        "AIT-T0125",
        "AIT-T0126",
        "AIT-T0127",
        "AIT-T0128",
        "AIT-T0129",
        "AIT-T0130",
        "AIT-T0131",
        "AIT-T0132",
        "AIT-T0133",
        "AIT-T0134",
        "AIT-T0135",
        "AIT-T0136",
        "AIT-T0137",
        "AIT-T0138",
    )
    assert result.nonstructured_full_attention_accuracy == 1.0
    assert result.nonstructured_family_accuracy < result.nonstructured_full_attention_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_stride_family_sparse_attention_sidecar_emits_json_and_markdown() -> None:
    json_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(json_result.stdout)
    assert payload["schema_id"] == (
        "circle_calculus.stride_family_sparse_attention_certificate.v0"
    )
    assert "not a neural attention-quality" in payload["claim_boundary"]
    result = payload["benchmark_result"]
    certificate = result["coverage_certificate"]
    assert result["family_accuracy"] == 1.0
    assert result["wrong_family_accuracy"] == 0.25
    assert certificate["covered_lag_count"] == 10
    assert certificate["uncovered_lag_count"] == 109
    assert certificate["uncovered_count_positive"] is True
    assert certificate["first_uncovered_lag"] == 5
    assert certificate["first_uncovered_lag_matches_uncovered_list_head"] is True
    assert certificate["no_first_uncovered_lag_matches_coverage_complete"] is True
    assert certificate["first_uncovered_lag_gap_witness"] is True
    assert certificate["uncovered_count_positive_matches_gap_witness"] is True
    assert certificate["positive_lag_count"] == 119
    assert certificate["covered_uncovered_count_sum"] == 119
    assert certificate["covered_uncovered_count_partition"] is True
    assert certificate["covered_count_certifies_complete"] is False
    assert certificate["covered_count_shortfall"] is True
    assert certificate["covered_count_shortfall_matches_gap_witness"] is True
    assert certificate["uncovered_lag_intervals"] == [
        [5, 6],
        [8, 12],
        [15, 20],
        [22, 25],
        [27, 38],
        [40, 119],
    ]
    assert certificate["uncovered_lag_interval_count"] == 6
    assert certificate["coverage_complete"] is False
    assert certificate["raw_budget_shortfall_certifies_incomplete"] is True
    assert certificate["theorem_side_unique_lag_candidate_count"] == 10
    assert certificate["theorem_side_lag_candidates_positive_in_context"] is True
    assert certificate["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert (
        certificate[
            "unique_lag_count_shortfall_matches_gap_witness_under_candidate_range"
        ]
        is True
    )
    assert certificate["unique_lag_count_matches_complete_under_candidate_range"] is True
    assert certificate["covered_count_matches_unique_lag_count_under_candidate_range"] is True
    assert (
        certificate[
            "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range"
        ]
        is True
    )
    assert certificate["fixture_theorem_ids"] == [
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0091",
        "AIT-T0102",
        "AIT-T0104",
    ]
    assert certificate["theorem_side_lag_candidates_no_collision"] is True
    assert "AIT-T0021" in certificate["theorem_ids"]
    assert "AIT-T0077" in certificate["theorem_ids"]
    assert "AIT-T0090" in certificate["theorem_ids"]
    assert "AIT-T0092" in certificate["theorem_ids"]
    assert "AIT-T0093" in certificate["theorem_ids"]
    assert "AIT-T0094" in certificate["theorem_ids"]
    assert "AIT-T0095" in certificate["theorem_ids"]
    assert "AIT-T0096" in certificate["theorem_ids"]
    assert "AIT-T0097" in certificate["theorem_ids"]
    assert "AIT-T0098" in certificate["theorem_ids"]
    assert "AIT-T0099" in certificate["theorem_ids"]
    assert "AIT-T0100" in certificate["theorem_ids"]
    assert "AIT-T0101" in certificate["theorem_ids"]
    assert "AIT-T0103" in certificate["theorem_ids"]
    assert "AIT-T0104" in certificate["theorem_ids"]
    assert "AIT-T0105" in certificate["theorem_ids"]
    assert "AIT-T0106" in certificate["theorem_ids"]
    assert "AIT-T0107" in certificate["theorem_ids"]
    assert "AIT-T0108" in certificate["theorem_ids"]
    assert "AIT-T0109" in certificate["theorem_ids"]
    assert "AIT-T0110" in certificate["theorem_ids"]
    assert "AIT-T0111" in certificate["theorem_ids"]
    assert "AIT-T0112" in certificate["theorem_ids"]
    assert "AIT-T0113" in certificate["theorem_ids"]
    assert "AIT-T0114" in certificate["theorem_ids"]
    assert "AIT-T0115" in certificate["theorem_ids"]
    assert "AIT-T0116" in certificate["theorem_ids"]
    assert "AIT-T0117" in certificate["theorem_ids"]
    assert "AIT-T0118" in certificate["theorem_ids"]
    assert "AIT-T0119" in certificate["theorem_ids"]
    assert "AIT-T0120" in certificate["theorem_ids"]
    assert "AIT-T0121" in certificate["theorem_ids"]
    assert "AIT-T0122" in certificate["theorem_ids"]
    assert "AIT-T0123" in certificate["theorem_ids"]
    assert "AIT-T0124" in certificate["theorem_ids"]
    assert "AIT-T0125" in certificate["theorem_ids"]
    assert "AIT-T0126" in certificate["theorem_ids"]
    assert "AIT-T0127" in certificate["theorem_ids"]
    assert "AIT-T0128" in certificate["theorem_ids"]
    assert "AIT-T0129" in certificate["theorem_ids"]
    assert "AIT-T0130" in certificate["theorem_ids"]
    assert "AIT-T0131" in certificate["theorem_ids"]
    assert "AIT-T0132" in certificate["theorem_ids"]
    assert "AIT-T0133" in certificate["theorem_ids"]
    assert "AIT-T0134" in certificate["theorem_ids"]
    assert "AIT-T0135" in certificate["theorem_ids"]
    assert "AIT-T0136" in certificate["theorem_ids"]
    assert "AIT-T0137" in certificate["theorem_ids"]
    assert "AIT-T0138" in certificate["theorem_ids"]
    assert certificate["no_wrap_separated_candidate_range_sufficient_condition"] is False
    assert certificate["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert certificate["singleton_stride_period"] is None
    assert certificate["singleton_no_zero_period_threshold"] is None
    assert certificate["singleton_no_zero_period_threshold_matches_condition"] is True
    assert certificate["stride_family_periods"] == [120, 120]
    assert certificate["no_zero_period_thresholds"] == [True, True]
    assert certificate["stride_family_zero_residue_step_counts"] == [0, 0]
    assert certificate["zero_residue_step_counts_match_period_formula"] is True
    assert certificate["stride_family_zero_residue_total_step_count"] == 0
    assert certificate["zero_residue_total_count_matches_sum_formula"] is True
    assert (
        certificate["zero_residue_total_count_zero_matches_no_zero_condition"]
        is True
    )
    assert (
        certificate["no_zero_period_threshold_candidate_range_sufficient_condition"]
        is True
    )
    assert certificate["no_zero_period_threshold_matches_condition"] is True
    assert certificate["no_zero_period_violation_witness_stride"] is None
    assert certificate["no_zero_period_violation_witness_period"] is None
    assert certificate["no_zero_period_violation_witness_step"] is None
    assert certificate["no_zero_period_violation_witness_residue"] is None
    assert certificate["zero_residue_witness_matches_period_threshold"] is True
    assert certificate["zero_residue_witness_matches_no_zero_failure"] is True
    assert certificate["period_threshold_violation_matches_no_zero_failure"] is True
    assert certificate["no_zero_period_violation_witness_is_first_zero"] is True
    assert certificate["no_zero_period_violation_witness_step_positive"] is True
    assert (
        certificate[
            "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert certificate["theorem_side_query_count_le_unique_lag_count"] is True
    assert certificate["theorem_side_query_count_matches_unique_lag_count"] is True
    assert (
        certificate[
            "unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective"
        ]
        is True
    )
    assert (
        certificate[
            "unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated"
        ]
        is True
    )
    assert (
        certificate[
            "unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue"
        ]
        is True
    )
    assert (
        certificate[
            "unique_query_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    complete = payload["complete_fixture_certificate"]
    assert complete["sequence_length"] == 9
    assert complete["strides"] == [3, 4, 7]
    assert complete["covered_lags"] == [1, 2, 3, 6, 4, 8, 7, 5]
    assert complete["uncovered_lags"] == []
    assert complete["uncovered_count_positive"] is False
    assert complete["first_uncovered_lag"] is None
    assert complete["first_uncovered_lag_matches_uncovered_list_head"] is True
    assert complete["no_first_uncovered_lag_matches_coverage_complete"] is True
    assert complete["first_uncovered_lag_gap_witness"] is True
    assert complete["uncovered_count_positive_matches_gap_witness"] is True
    assert complete["positive_lag_count"] == 8
    assert complete["covered_uncovered_count_sum"] == 8
    assert complete["covered_uncovered_count_partition"] is True
    assert complete["covered_count_certifies_complete"] is True
    assert complete["covered_count_shortfall"] is False
    assert complete["covered_count_shortfall_matches_gap_witness"] is True
    assert complete["uncovered_lag_intervals"] == []
    assert complete["uncovered_lag_interval_count"] == 0
    assert complete["coverage_complete"] is True
    assert complete["raw_candidate_budget_upper_bound"] == 8
    assert complete["raw_budget_shortfall_certifies_incomplete"] is True
    assert complete["theorem_side_unique_lag_candidate_count"] == 8
    assert complete["theorem_side_lag_candidates_positive_in_context"] is True
    assert complete["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert complete["singleton_stride_period"] is None
    assert complete["singleton_no_zero_period_threshold"] is None
    assert complete["singleton_no_zero_period_threshold_matches_condition"] is True
    assert complete["stride_family_periods"] == [3, 9, 9]
    assert complete["no_zero_period_thresholds"] == [True, True, True]
    assert complete["stride_family_zero_residue_step_counts"] == [0, 0, 0]
    assert complete["zero_residue_step_counts_match_period_formula"] is True
    assert complete["stride_family_zero_residue_total_step_count"] == 0
    assert complete["zero_residue_total_count_matches_sum_formula"] is True
    assert complete["zero_residue_total_count_zero_matches_no_zero_condition"] is True
    assert (
        complete["no_zero_period_threshold_candidate_range_sufficient_condition"]
        is True
    )
    assert complete["no_zero_period_threshold_matches_condition"] is True
    assert complete["no_zero_period_violation_witness_stride"] is None
    assert complete["no_zero_period_violation_witness_period"] is None
    assert complete["no_zero_period_violation_witness_step"] is None
    assert complete["no_zero_period_violation_witness_residue"] is None
    assert complete["zero_residue_witness_matches_period_threshold"] is True
    assert complete["zero_residue_witness_matches_no_zero_failure"] is True
    assert complete["period_threshold_violation_matches_no_zero_failure"] is True
    assert complete["no_zero_period_violation_witness_is_first_zero"] is True
    assert complete["no_zero_period_violation_witness_step_positive"] is True
    assert complete["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert (
        complete["unique_lag_count_shortfall_matches_gap_witness_under_candidate_range"]
        is True
    )
    assert (
        complete[
            "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert complete["unique_lag_count_matches_complete_under_candidate_range"] is True
    assert complete["covered_count_matches_unique_lag_count_under_candidate_range"] is True
    assert (
        complete[
            "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range"
        ]
        is True
    )
    assert complete["theorem_side_unique_query_candidate_count"] == 8
    assert complete["theorem_side_query_count_le_unique_lag_count"] is True
    assert complete["theorem_side_query_count_matches_unique_lag_count"] is True
    assert (
        complete[
            "unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective"
        ]
        is True
    )
    assert (
        complete["unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated"]
        is True
    )
    assert (
        complete["unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue"]
        is True
    )
    assert (
        complete[
            "unique_query_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert complete["fixture_theorem_ids"] == [
        "AIT-T0086",
        "AIT-T0087",
        "AIT-T0088",
        "AIT-T0089",
        "AIT-T0105",
    ]
    planner_rows = {
        row["plan_id"]: row for row in payload["planner_style_certificates"]
    }
    assert set(planner_rows) == {
        "default_gap_fixture_120",
        "complete_toy_fixture_9",
        "singleton_period_probe_12",
        "long_context_no_wrap_probe_4096",
        "long_context_coprime_probe_8192",
    }
    assert planner_rows["default_gap_fixture_120"]["fixture_theorem_ids"] == [
        "AIT-T0084",
        "AIT-T0085",
        "AIT-T0091",
        "AIT-T0102",
        "AIT-T0104",
    ]
    assert (
        planner_rows["default_gap_fixture_120"][
            "no_zero_residue_candidate_range_sufficient_condition"
        ]
        is True
    )
    assert planner_rows["complete_toy_fixture_9"]["coverage_complete"] is True
    assert planner_rows["complete_toy_fixture_9"]["uncovered_lag_count"] == 0
    assert planner_rows["complete_toy_fixture_9"]["covered_count_certifies_complete"] is True
    assert (
        planner_rows["complete_toy_fixture_9"][
            "no_zero_residue_candidate_range_sufficient_condition"
        ]
        is True
    )
    assert planner_rows["complete_toy_fixture_9"]["fixture_theorem_ids"] == [
        "AIT-T0086",
        "AIT-T0087",
        "AIT-T0088",
        "AIT-T0089",
        "AIT-T0105",
    ]
    singleton_probe = planner_rows["singleton_period_probe_12"]
    assert singleton_probe["sequence_length"] == 12
    assert singleton_probe["strides"] == [4]
    assert singleton_probe["path_length"] == 2
    assert singleton_probe["local_window"] == 1
    assert singleton_probe["singleton_stride_period"] == 3
    assert singleton_probe["singleton_no_zero_period_threshold"] is True
    assert singleton_probe["singleton_no_zero_period_threshold_matches_condition"] is True
    assert singleton_probe["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert singleton_probe["stride_family_periods"] == [3]
    assert singleton_probe["no_zero_period_thresholds"] == [True]
    assert singleton_probe["stride_family_zero_residue_step_counts"] == [0]
    assert singleton_probe["zero_residue_step_counts_match_period_formula"] is True
    assert singleton_probe["stride_family_zero_residue_total_step_count"] == 0
    assert singleton_probe["zero_residue_total_count_matches_sum_formula"] is True
    assert (
        singleton_probe["zero_residue_total_count_zero_matches_no_zero_condition"]
        is True
    )
    assert (
        singleton_probe["no_zero_period_threshold_candidate_range_sufficient_condition"]
        is True
    )
    assert singleton_probe["no_zero_period_threshold_matches_condition"] is True
    assert singleton_probe["no_zero_period_violation_witness_stride"] is None
    assert singleton_probe["no_zero_period_violation_witness_period"] is None
    assert singleton_probe["no_zero_period_violation_witness_step"] is None
    assert singleton_probe["no_zero_period_violation_witness_residue"] is None
    assert singleton_probe["zero_residue_witness_matches_period_threshold"] is True
    assert singleton_probe["zero_residue_witness_matches_no_zero_failure"] is True
    assert singleton_probe["period_threshold_violation_matches_no_zero_failure"] is True
    assert singleton_probe["no_zero_period_violation_witness_is_first_zero"] is True
    assert singleton_probe["no_zero_period_violation_witness_step_positive"] is True
    assert "AIT-T0126" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0127" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0128" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0131" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0132" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0133" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0134" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0135" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0136" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0137" in singleton_probe["core_coverage_theorem_ids"]
    assert "AIT-T0138" in singleton_probe["core_coverage_theorem_ids"]
    long_no_wrap = planner_rows["long_context_no_wrap_probe_4096"]
    assert long_no_wrap["sequence_length"] == 4096
    assert long_no_wrap["strides"] == [33, 160, 800]
    assert long_no_wrap["candidate_budget_per_query"] == 44
    assert long_no_wrap["covered_lag_count"] == 44
    assert long_no_wrap["uncovered_lag_count"] == 4051
    assert long_no_wrap["positive_lag_count"] == 4095
    assert long_no_wrap["covered_uncovered_count_sum"] == 4095
    assert long_no_wrap["covered_uncovered_count_partition"] is True
    assert long_no_wrap["covered_count_certifies_complete"] is False
    assert long_no_wrap["fixture_theorem_ids"] == ["AIT-T0139", "AIT-T0140"]
    assert long_no_wrap["uncovered_lag_interval_count"] == 12
    assert long_no_wrap["raw_budget_survives_lag_dedup"] is True
    assert long_no_wrap["raw_budget_survives_query_dedup"] is True
    assert long_no_wrap["raw_budget_shortfall_certifies_incomplete"] is True
    assert long_no_wrap["theorem_side_lag_candidates_positive_in_context"] is True
    assert long_no_wrap["no_wrap_separated_candidate_range_sufficient_condition"] is True
    assert long_no_wrap["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert long_no_wrap["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert (
        long_no_wrap[
            "unique_lag_count_shortfall_matches_gap_witness_under_candidate_range"
        ]
        is True
    )
    assert (
        long_no_wrap[
            "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert long_no_wrap["unique_lag_count_matches_complete_under_candidate_range"] is True
    assert long_no_wrap["covered_count_matches_unique_lag_count_under_candidate_range"] is True
    assert (
        long_no_wrap[
            "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range"
        ]
        is True
    )
    assert long_no_wrap["coverage_complete"] is False
    assert long_no_wrap["uncovered_lag_interval_sample"][:3] == [
        [34, 65],
        [67, 98],
        [100, 131],
    ]
    long_coprime = planner_rows["long_context_coprime_probe_8192"]
    assert long_coprime["sequence_length"] == 8192
    assert long_coprime["strides"] == [127, 509, 1021, 2039]
    assert long_coprime["candidate_budget_per_query"] == 96
    assert long_coprime["covered_lag_count"] == 96
    assert long_coprime["uncovered_lag_count"] == 8095
    assert long_coprime["uncovered_count_positive"] is True
    assert long_coprime["first_uncovered_lag"] == 65
    assert long_coprime["uncovered_count_positive_matches_gap_witness"] is True
    assert long_coprime["positive_lag_count"] == 8191
    assert long_coprime["covered_uncovered_count_sum"] == 8191
    assert long_coprime["covered_uncovered_count_partition"] is True
    assert long_coprime["covered_count_certifies_complete"] is False
    assert long_coprime["fixture_theorem_ids"] == ["AIT-T0141", "AIT-T0142"]
    assert long_coprime["covered_count_shortfall"] is True
    assert long_coprime["covered_count_shortfall_matches_gap_witness"] is True
    assert long_coprime["uncovered_lag_interval_count"] == 32
    assert long_coprime["raw_budget_survives_lag_dedup"] is True
    assert long_coprime["raw_budget_survives_query_dedup"] is True
    assert long_coprime["raw_budget_shortfall_certifies_incomplete"] is True
    assert long_coprime["theorem_side_lag_candidates_positive_in_context"] is True
    assert long_coprime["no_zero_residue_candidate_range_sufficient_condition"] is True
    assert long_coprime["unique_lag_count_shortfall_certifies_incomplete"] is True
    assert (
        long_coprime[
            "unique_lag_count_shortfall_matches_gap_witness_under_candidate_range"
        ]
        is True
    )
    assert (
        long_coprime[
            "unique_lag_count_shortfall_matches_gap_witness_under_period_threshold"
        ]
        is True
    )
    assert long_coprime["unique_lag_count_matches_complete_under_candidate_range"] is True
    assert long_coprime["covered_count_matches_unique_lag_count_under_candidate_range"] is True
    assert (
        long_coprime[
            "uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range"
        ]
        is True
    )
    assert "AIT-T0081" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0092" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0093" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0094" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0095" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0096" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0097" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0098" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0099" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0100" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0101" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0103" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0110" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0111" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0112" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0113" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0114" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0115" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0116" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0117" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0118" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0119" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0120" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0121" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0122" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0123" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0124" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0125" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0126" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0127" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0128" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0129" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0130" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0131" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0132" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0133" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0134" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0135" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0136" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0137" in long_coprime["core_coverage_theorem_ids"]
    assert "AIT-T0138" in long_coprime["core_coverage_theorem_ids"]
    assert long_coprime["no_wrap_separated_candidate_range_sufficient_condition"] is False
    assert "scripts/stride_family_certify.py --context 8192" in (
        long_coprime["reproduce_command"]
    )

    markdown_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py",
            "--format",
            "markdown",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "Stride-Family Sparse-Attention Certificate Results" in markdown_result.stdout
    assert "| 120 | 120 | 4 | 3 | 7, 13 | 5, 9 | False | 0.084 |" in markdown_result.stdout
    assert (
        "| 9 | 2 | 2 | 3, 4, 7 | True | 0 | None | True | True | True | "
        "True | False | True | 8 | True | 8 | True | False | True | None | "
        "None | True | True | True | True | True | True | True | 8 | True | True | "
        "True | True | True | True | "
        "AIT-T0086, AIT-T0087, AIT-T0088, AIT-T0089, AIT-T0105 |"
    ) in markdown_result.stdout
    assert "Planner-style declared plans" in markdown_result.stdout
    assert "Raw shortfall certifies incomplete" in markdown_result.stdout
    assert "Fixture theorem ids" in markdown_result.stdout
    assert "AIT-T0139, AIT-T0140" in markdown_result.stdout
    assert "AIT-T0141, AIT-T0142" in markdown_result.stdout
    assert (
        "| long_context_no_wrap_probe_4096 | 4096 | 32 | 4 | "
        "33, 160, 800 | False | 0.011 | 44 | 0.011 | 4095 | 4095 | 4051 | "
        "34 | True | True | True | True | True | True | 12 | True | True | True | True | "
        "None | None | True | True | True | True | True | True | True | lag=True, query=True |"
    ) in markdown_result.stdout
    assert (
        "| singleton_period_probe_12 | 12 | 1 | 2 | 4 | False | 0.273 | 3 | "
        "0.250 | 11 | 11 | 8 | 2 | True | True | True | True | True | True | "
        "3 | True | True | True | True | 3 | True | True | True | True | "
        "True | True | True | True | lag=True, query=True |"
    ) in markdown_result.stdout
    assert (
        "| long_context_coprime_probe_8192 | 8192 | 64 | 8 | "
        "127, 509, 1021, 2039 | False | 0.012 | 96 | 0.012 | 8191 | 8191 | "
        "8095 | 65 | True | True | True | True | True | True | 32 | True | True | False | True | "
        "None | None | True | True | True | True | True | True | True | lag=True, query=True | "
        "AIT-T0141, AIT-T0142 |"
    ) in markdown_result.stdout
    assert "AIT-T0091" in markdown_result.stdout
    assert "AIT-T0110" in markdown_result.stdout
    assert "AIT-T0111" in markdown_result.stdout
    assert "AIT-T0112" in markdown_result.stdout
    assert "AIT-T0113" in markdown_result.stdout
    assert "AIT-T0114" in markdown_result.stdout
    assert "AIT-T0115" in markdown_result.stdout
    assert "AIT-T0116" in markdown_result.stdout
    assert "AIT-T0117" in markdown_result.stdout
    assert "AIT-T0118" in markdown_result.stdout
    assert "AIT-T0119" in markdown_result.stdout
    assert "AIT-T0120" in markdown_result.stdout
    assert "AIT-T0121" in markdown_result.stdout
    assert "AIT-T0122" in markdown_result.stdout
    assert "AIT-T0126" in markdown_result.stdout
    assert "AIT-T0127" in markdown_result.stdout
    assert "AIT-T0128" in markdown_result.stdout
    assert "AIT-T0129" in markdown_result.stdout
    assert "AIT-T0130" in markdown_result.stdout
    assert "AIT-T0131" in markdown_result.stdout
    assert "AIT-T0132" in markdown_result.stdout
    assert "AIT-T0133" in markdown_result.stdout
    assert "AIT-T0134" in markdown_result.stdout
    assert "AIT-T0135" in markdown_result.stdout
    assert "AIT-T0136" in markdown_result.stdout
    assert "AIT-T0137" in markdown_result.stdout
    assert "AIT-T0138" in markdown_result.stdout
    assert "Family no-zero period threshold" in markdown_result.stdout
    assert (
        "| 120, 120 | True, True | 0, 0 | True | 0 | True | True | True | True | True | True | True | True |"
        in markdown_result.stdout
    )
    assert "Unique count iff complete" in markdown_result.stdout
    assert "Uncovered count formula" in markdown_result.stdout
    assert "Unique lag shortfall certifies incomplete" in markdown_result.stdout
    assert "Unique shortfall iff gap" in markdown_result.stdout
    assert "First uncovered lags" in markdown_result.stdout


def test_committed_stride_family_sparse_attention_results_match_generator(tmp_path: Path) -> None:
    generated_json = tmp_path / "stride_family_sparse_attention.json"
    generated_markdown = tmp_path / "stride_family_sparse_attention.md"
    subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py",
            "--json-out",
            str(generated_json),
            "--markdown-out",
            str(generated_markdown),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    committed_json = Path(
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/stride_family_sparse_attention.json"
    )
    committed_markdown = Path(
        "sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/stride_family_sparse_attention.md"
    )
    assert json.loads(committed_json.read_text()) == json.loads(generated_json.read_text())
    assert committed_markdown.read_text() == generated_markdown.read_text()


def test_stride_family_coverage_complete_when_local_window_covers_context() -> None:
    certificate = certify_stride_family_coverage(
        sequence_length=10,
        strides=(3,),
        path_length=2,
        local_window=9,
    )

    assert certificate.covered_lags == tuple(range(1, 10))
    assert certificate.uncovered_lags == ()
    assert certificate.coverage_complete
    assert certificate.positive_lag_count == 9
    assert certificate.covered_uncovered_count_sum == 9
    assert certificate.covered_uncovered_count_partition
    assert certificate.covered_count_certifies_complete
    assert certificate.coverage_ratio == 1.0
    assert certificate.raw_candidate_budget_upper_bound == stride_family_raw_candidate_budget(
        strides=(3,),
        path_length=2,
        local_window=9,
    )
    assert certificate.deduplicated_candidate_budget_upper_bound == 10
    assert certificate.deduplicated_candidate_budget_upper_bound == (
        stride_family_deduplicated_candidate_budget_bound(
            sequence_length=10,
            strides=(3,),
            path_length=2,
            local_window=9,
        )
    )
    assert certificate.theorem_side_lag_candidates == (
        stride_family_lag_candidate_list(10, (3,), 2, 9)
    )
    assert certificate.theorem_side_lag_candidates == (1, 2, 3, 4, 5, 6, 7, 8, 9, 3, 6)
    assert stride_family_coil_residue_list(10, (3,), 2) == (3, 6)
    assert certificate.theorem_side_coil_residues_no_collision
    assert certificate.theorem_side_coil_residues_no_collision == (
        stride_family_coil_residues_no_collision(10, (3,), 2)
    )
    assert not certificate.theorem_side_local_coil_disjoint
    assert certificate.theorem_side_local_coil_disjoint == (
        stride_family_local_coil_candidates_disjoint(10, (3,), 2, 9)
    )
    assert certificate.theorem_side_unique_lag_candidate_count == 9
    assert certificate.theorem_side_unique_lag_candidate_count == (
        stride_family_unique_lag_candidate_count(10, (3,), 2, 9)
    )
    assert certificate.theorem_side_unique_lag_candidate_count <= (
        certificate.raw_candidate_budget_upper_bound
    )
    assert not certificate.theorem_side_lag_candidates_no_collision
    assert certificate.theorem_side_lag_candidates_no_collision == (
        stride_family_lag_candidates_no_collision(10, (3,), 2, 9)
    )
    assert certificate.theorem_side_query_candidates == (
        stride_family_query_candidate_list(10, 0, (3,), 2, 9)
    )
    assert certificate.theorem_side_query_candidates == (9, 8, 7, 6, 5, 4, 3, 2, 1, 7, 4)
    assert certificate.theorem_side_predecessor_injective_on_lag_candidates
    assert certificate.theorem_side_predecessor_injective_on_lag_candidates == (
        stride_family_predecessor_injective_on_lag_candidates(10, 0, (3,), 2, 9)
    )
    assert certificate.theorem_side_predecessor_injective_window_context_condition
    assert certificate.theorem_side_predecessor_injective_window_context_condition == (
        stride_family_predecessor_injective_window_context_sufficient_condition(10, 9)
    )
    assert certificate.theorem_side_unique_query_candidate_count == 9
    assert certificate.theorem_side_unique_query_candidate_count == (
        stride_family_unique_query_candidate_count(10, 0, (3,), 2, 9)
    )
    assert certificate.theorem_side_unique_query_candidate_count <= (
        certificate.raw_candidate_budget_upper_bound
    )
    assert certificate.theorem_side_query_count_le_unique_lag_count
    assert certificate.theorem_side_unique_query_candidate_count <= (
        certificate.theorem_side_unique_lag_candidate_count
    )
    assert certificate.theorem_side_query_count_matches_unique_lag_count
    assert certificate.theorem_side_unique_query_candidate_count == (
        certificate.theorem_side_unique_lag_candidate_count
    )
    assert not certificate.theorem_side_query_candidates_no_collision
    assert certificate.theorem_side_query_candidates_no_collision == (
        stride_family_query_candidates_no_collision(10, 0, (3,), 2, 9)
    )
    assert certificate.theorem_side_unique_query_candidate_count == (
        certificate.candidate_budget_per_query
    )
    assert certificate.candidate_budget_per_query < certificate.raw_candidate_budget_upper_bound
    assert certificate.candidate_budget_per_query <= (
        certificate.deduplicated_candidate_budget_upper_bound
    )
    assert certificate.raw_budget_shortfall_certifies_incomplete
    assert certificate.theorem_side_lag_candidates_positive_in_context
    assert certificate.unique_lag_count_shortfall_certifies_incomplete
    assert certificate.unique_lag_count_shortfall_matches_gap_witness_under_candidate_range
    assert certificate.unique_lag_count_matches_complete_under_candidate_range
    assert certificate.covered_count_matches_unique_lag_count_under_candidate_range
    assert (
        certificate.uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range
    )
    assert "AIT-T0022" in certificate.theorem_ids
    assert "AIT-T0023" in certificate.theorem_ids
    assert "AIT-T0024" in certificate.theorem_ids
    assert "AIT-T0036" in certificate.theorem_ids
    assert "AIT-T0037" in certificate.theorem_ids
    assert "AIT-T0038" in certificate.theorem_ids
    assert "AIT-T0039" in certificate.theorem_ids
    assert "AIT-T0040" in certificate.theorem_ids
    assert "AIT-T0041" in certificate.theorem_ids
    assert "AIT-T0042" in certificate.theorem_ids
    assert "AIT-T0043" in certificate.theorem_ids
    assert "AIT-T0044" in certificate.theorem_ids
    assert "AIT-T0045" in certificate.theorem_ids
    assert "AIT-T0046" in certificate.theorem_ids
    assert "AIT-T0047" in certificate.theorem_ids
    assert "AIT-T0048" in certificate.theorem_ids
    assert "AIT-T0049" in certificate.theorem_ids
    assert "AIT-T0050" in certificate.theorem_ids
    assert "AIT-T0051" in certificate.theorem_ids
    assert "AIT-T0052" in certificate.theorem_ids
    assert "AIT-T0053" in certificate.theorem_ids
    assert "AIT-T0054" in certificate.theorem_ids
    assert "AIT-T0055" in certificate.theorem_ids
    assert "AIT-T0056" in certificate.theorem_ids
    assert "AIT-T0076" in certificate.theorem_ids
    assert "AIT-T0077" in certificate.theorem_ids
    assert "AIT-T0057" in certificate.theorem_ids
    assert "AIT-T0058" in certificate.theorem_ids
    assert "AIT-T0059" in certificate.theorem_ids
    assert "AIT-T0060" in certificate.theorem_ids
    assert "AIT-T0061" in certificate.theorem_ids
    assert "AIT-T0062" in certificate.theorem_ids
    assert "AIT-T0063" in certificate.theorem_ids
    assert "AIT-T0064" in certificate.theorem_ids
    assert "AIT-T0065" in certificate.theorem_ids
    assert "AIT-T0066" in certificate.theorem_ids
    assert "AIT-T0067" in certificate.theorem_ids
    assert "AIT-T0068" in certificate.theorem_ids
    assert "AIT-T0069" in certificate.theorem_ids
    assert "AIT-T0070" in certificate.theorem_ids
    assert "AIT-T0071" in certificate.theorem_ids
    assert "AIT-T0072" in certificate.theorem_ids
    assert "AIT-T0073" in certificate.theorem_ids
    assert "AIT-T0074" in certificate.theorem_ids
    assert "AIT-T0075" in certificate.theorem_ids
    assert "AIT-T0106" in certificate.theorem_ids
    assert "AIT-T0107" in certificate.theorem_ids
    assert "AIT-T0108" in certificate.theorem_ids
    assert "AIT-T0109" in certificate.theorem_ids
    assert "AIT-T0110" in certificate.theorem_ids
    assert "AIT-T0111" in certificate.theorem_ids
    assert "AIT-T0112" in certificate.theorem_ids
    assert "AIT-T0113" in certificate.theorem_ids
    assert "AIT-T0114" in certificate.theorem_ids
    assert "AIT-T0115" in certificate.theorem_ids
    assert "AIT-T0116" in certificate.theorem_ids
    assert "AIT-T0117" in certificate.theorem_ids
    assert "AIT-T0118" in certificate.theorem_ids
    assert "AIT-T0119" in certificate.theorem_ids
    assert "AIT-T0120" in certificate.theorem_ids
    assert "AIT-T0121" in certificate.theorem_ids
    assert "AIT-T0122" in certificate.theorem_ids
    assert "AIT-T0123" in certificate.theorem_ids
    assert "AIT-T0124" in certificate.theorem_ids
    assert "AIT-T0125" in certificate.theorem_ids
    assert "AIT-T0126" in certificate.theorem_ids
    assert "AIT-T0127" in certificate.theorem_ids
    assert "AIT-T0128" in certificate.theorem_ids
    assert "AIT-T0025" in certificate.theorem_ids


def test_singleton_stride_period_threshold_matches_no_zero_condition() -> None:
    below_period = certify_stride_family_coverage(
        sequence_length=12,
        strides=(4,),
        path_length=2,
        local_window=1,
    )
    at_period = certify_stride_family_coverage(
        sequence_length=12,
        strides=(4,),
        path_length=3,
        local_window=1,
    )

    assert below_period.singleton_stride_period == 3
    assert below_period.singleton_no_zero_period_threshold is True
    assert below_period.no_zero_residue_candidate_range_sufficient_condition is True
    assert below_period.singleton_no_zero_period_threshold_matches_condition is True
    assert below_period.stride_family_periods == (3,)
    assert below_period.no_zero_period_thresholds == (True,)
    assert below_period.stride_family_zero_residue_step_counts == (0,)
    assert below_period.zero_residue_step_counts_match_period_formula
    assert below_period.stride_family_zero_residue_total_step_count == 0
    assert below_period.zero_residue_total_count_matches_sum_formula
    assert below_period.zero_residue_total_count_zero_matches_no_zero_condition
    assert below_period.no_zero_period_threshold_candidate_range_sufficient_condition
    assert below_period.no_zero_period_threshold_matches_condition
    assert "AIT-T0126" in below_period.theorem_ids
    assert "AIT-T0127" in below_period.theorem_ids
    assert "AIT-T0128" in below_period.theorem_ids
    assert "AIT-T0131" in below_period.theorem_ids
    assert "AIT-T0132" in below_period.theorem_ids
    assert "AIT-T0133" in below_period.theorem_ids
    assert "AIT-T0134" in below_period.theorem_ids
    assert "AIT-T0135" in below_period.theorem_ids
    assert "AIT-T0136" in below_period.theorem_ids
    assert "AIT-T0137" in below_period.theorem_ids
    assert "AIT-T0138" in below_period.theorem_ids
    assert below_period.no_zero_period_violation_witness_stride is None
    assert below_period.no_zero_period_violation_witness_period is None
    assert below_period.no_zero_period_violation_witness_step is None
    assert below_period.no_zero_period_violation_witness_residue is None
    assert below_period.zero_residue_witness_matches_period_threshold
    assert below_period.zero_residue_witness_matches_no_zero_failure
    assert below_period.period_threshold_violation_matches_no_zero_failure
    assert below_period.no_zero_period_violation_witness_is_first_zero
    assert below_period.no_zero_period_violation_witness_step_positive

    assert at_period.singleton_stride_period == 3
    assert at_period.singleton_no_zero_period_threshold is False
    assert at_period.no_zero_residue_candidate_range_sufficient_condition is False
    assert at_period.singleton_no_zero_period_threshold_matches_condition is True
    assert at_period.stride_family_periods == (3,)
    assert at_period.no_zero_period_thresholds == (False,)
    assert at_period.stride_family_zero_residue_step_counts == (1,)
    assert at_period.zero_residue_step_counts_match_period_formula
    assert at_period.stride_family_zero_residue_total_step_count == 1
    assert at_period.zero_residue_total_count_matches_sum_formula
    assert at_period.zero_residue_total_count_zero_matches_no_zero_condition
    assert not at_period.no_zero_period_threshold_candidate_range_sufficient_condition
    assert at_period.no_zero_period_threshold_matches_condition
    assert at_period.no_zero_period_violation_witness_stride == 4
    assert at_period.no_zero_period_violation_witness_period == 3
    assert at_period.no_zero_period_violation_witness_step == 3
    assert at_period.no_zero_period_violation_witness_residue == 0
    assert at_period.zero_residue_witness_matches_period_threshold
    assert at_period.zero_residue_witness_matches_no_zero_failure
    assert at_period.period_threshold_violation_matches_no_zero_failure
    assert at_period.no_zero_period_violation_witness_is_first_zero
    assert at_period.no_zero_period_violation_witness_step_positive


def test_stride_family_complete_sparse_family_fixture_has_empty_gap_list() -> None:
    certificate = certify_stride_family_coverage(
        sequence_length=9,
        strides=(3, 4, 7),
        path_length=2,
        local_window=2,
    )

    assert certificate.covered_lags == (1, 2, 3, 6, 4, 8, 7, 5)
    assert certificate.uncovered_lags == ()
    assert certificate.covered_lag_count == 8
    assert certificate.uncovered_lag_count == 0
    assert certificate.positive_lag_count == 8
    assert certificate.covered_uncovered_count_sum == 8
    assert certificate.covered_uncovered_count_partition
    assert certificate.covered_count_certifies_complete
    assert certificate.coverage_complete
    assert certificate.coverage_ratio == 1.0
    assert certificate.candidate_budget_per_query == 8
    assert certificate.raw_candidate_budget_upper_bound == 8
    assert certificate.deduplicated_candidate_budget_upper_bound == 8
    assert certificate.theorem_side_lag_candidates == (1, 2, 3, 6, 4, 8, 7, 5)
    assert certificate.theorem_side_unique_lag_candidate_count == 8
    assert certificate.theorem_side_coil_residues_no_collision
    assert certificate.theorem_side_local_coil_disjoint
    assert certificate.theorem_side_lag_candidates_no_collision
    assert certificate.theorem_side_query_candidates == (8, 7, 6, 3, 5, 1, 2, 4)
    assert certificate.theorem_side_unique_query_candidate_count == 8
    assert certificate.theorem_side_lag_candidates_positive_in_context
    assert certificate.no_zero_residue_candidate_range_sufficient_condition
    assert certificate.unique_lag_count_shortfall_certifies_incomplete
    assert certificate.unique_lag_count_shortfall_matches_gap_witness_under_candidate_range
    assert certificate.unique_lag_count_matches_complete_under_candidate_range
    assert certificate.covered_count_matches_unique_lag_count_under_candidate_range
    assert (
        certificate.uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range
    )
    assert certificate.theorem_side_predecessor_injective_on_lag_candidates
    assert certificate.theorem_side_predecessor_injective_window_context_condition
    assert certificate.theorem_side_query_candidates_no_collision
    assert certificate.full_attention_budget == 9
    assert certificate.fixture_theorem_ids == (
        "AIT-T0086",
        "AIT-T0087",
        "AIT-T0088",
        "AIT-T0089",
        "AIT-T0105",
    )


def test_stride_family_single_stride_no_wrap_condition_certifies_no_collision() -> None:
    certificate = certify_stride_family_coverage(
        sequence_length=64,
        strides=(7,),
        path_length=3,
        local_window=4,
    )

    assert stride_family_single_stride_no_wrap_sufficient_condition(64, (7,), 3, 4)
    assert certificate.theorem_side_lag_candidates == (1, 2, 3, 4, 7, 14, 21)
    assert certificate.theorem_side_coil_residues_no_collision
    assert certificate.theorem_side_local_coil_disjoint
    assert certificate.theorem_side_lag_candidates_no_collision
    assert certificate.theorem_side_unique_lag_candidate_count == (
        certificate.raw_candidate_budget_upper_bound
    )
    assert not stride_family_single_stride_no_wrap_sufficient_condition(64, (7, 11), 3, 4)
    assert not stride_family_single_stride_no_wrap_sufficient_condition(20, (7,), 3, 4)
    assert not stride_family_single_stride_no_wrap_sufficient_condition(64, (7,), 3, 8)


def test_stride_family_head_tail_disjointness_detects_coil_block_overlap() -> None:
    assert stride_family_head_coil_residues_disjoint_from_tail(120, (7, 13), 3)
    assert not stride_family_head_coil_residues_disjoint_from_tail(120, (7, 14), 3)
    assert stride_family_head_coil_residues_disjoint_from_tail(120, (7,), 3)


def test_stride_family_head_tail_no_wrap_separation_is_sufficient_not_exact() -> None:
    assert stride_family_head_tail_no_wrap_separation_sufficient_condition(
        120, (7, 22), 3
    )
    assert stride_family_head_coil_residues_disjoint_from_tail(120, (7, 22), 3)
    assert not stride_family_head_tail_no_wrap_separation_sufficient_condition(
        120, (7, 20), 3
    )
    assert stride_family_head_coil_residues_disjoint_from_tail(120, (7, 20), 3)
    assert not stride_family_head_tail_no_wrap_separation_sufficient_condition(
        60, (7, 22), 3
    )


def test_stride_family_no_wrap_separated_condition_certifies_ordered_family() -> None:
    assert stride_family_no_wrap_separated_sufficient_condition(
        200, (5, 17, 61), 3
    )
    assert stride_family_coil_residues_no_collision(200, (5, 17, 61), 3)
    assert not stride_family_no_wrap_separated_sufficient_condition(
        200, (17, 5, 61), 3
    )
    assert stride_family_coil_residues_no_collision(200, (17, 5, 61), 3)
    assert not stride_family_no_wrap_separated_sufficient_condition(
        120, (7, 22, 50), 3
    )


def test_stride_family_no_wrap_separated_local_and_lag_no_collision_conditions() -> None:
    assert stride_family_no_wrap_separated_local_disjoint_sufficient_condition(
        200, (5, 17, 61), 3, 4
    )
    assert stride_family_no_wrap_separated_lag_no_collision_sufficient_condition(
        200, (5, 17, 61), 3, 4
    )
    assert stride_family_local_coil_candidates_disjoint(200, (5, 17, 61), 3, 4)
    assert stride_family_lag_candidates_no_collision(200, (5, 17, 61), 3, 4)
    assert not stride_family_no_wrap_separated_local_disjoint_sufficient_condition(
        200, (5, 17, 61), 3, 5
    )
    assert not stride_family_lag_candidates_no_collision(200, (5, 17, 61), 3, 5)
    assert not stride_family_no_wrap_separated_lag_no_collision_sufficient_condition(
        200, (17, 5, 61), 3, 4
    )
    assert stride_family_lag_candidates_no_collision(200, (17, 5, 61), 3, 4)


def test_stride_family_no_wrap_separated_query_raw_budget_endpoint() -> None:
    assert stride_family_predecessor_injective_window_context_sufficient_condition(
        200, 4
    )
    assert not stride_family_predecessor_injective_window_context_sufficient_condition(
        200, 200
    )
    assert stride_family_no_wrap_separated_query_no_collision_sufficient_condition(
        200, 37, (5, 17, 61), 3, 4
    )
    assert stride_family_no_wrap_separated_query_raw_budget_exact_sufficient_condition(
        200, 37, (5, 17, 61), 3, 4
    )
    assert stride_family_query_candidates_no_collision(200, 37, (5, 17, 61), 3, 4)
    assert stride_family_unique_lag_candidate_count(200, (5, 17, 61), 3, 4) == (
        stride_family_raw_candidate_budget(
            strides=(5, 17, 61),
            path_length=3,
            local_window=4,
        )
    )
    assert stride_family_unique_query_candidate_count(
        200, 37, (5, 17, 61), 3, 4
    ) == stride_family_raw_candidate_budget(
        strides=(5, 17, 61),
        path_length=3,
        local_window=4,
    )
    assert not stride_family_no_wrap_separated_query_no_collision_sufficient_condition(
        200, 37, (17, 5, 61), 3, 4
    )
    assert stride_family_query_candidates_no_collision(200, 37, (17, 5, 61), 3, 4)


def test_learned_content_gate_route_lookup_helpers_are_deterministic() -> None:
    queries = tuple(range(8))
    routes = tuple(content_route_label(query_index) for query_index in queries)
    lookup = fit_content_route_lookup(2, queries, routes)

    assert routes == (1, 0, 1, 0, 1, 0, 1, 0)
    assert lookup == (1, 0)
    assert predict_content_route_lookup(2, lookup, tuple(range(8, 16))) == routes


def test_learned_content_gate_retrieval_benchmark_has_baselines_and_controls() -> None:
    result = run_learned_content_gate_retrieval_benchmark(
        sequence_length=64,
        train_length=64,
        test_length=32,
        route_period=2,
        wrong_route_period=3,
        long_target_lag=21,
        near_target_lag=3,
        stride=7,
        path_length=3,
        local_window=8,
    )

    assert result == run_learned_content_gate_retrieval_benchmark(
        sequence_length=64,
        train_length=64,
        test_length=32,
        route_period=2,
        wrong_route_period=3,
        long_target_lag=21,
        near_target_lag=3,
        stride=7,
        path_length=3,
        local_window=8,
    )
    assert result.learned_route_lookup == (1, 0)
    assert result.required_route_sample == (1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)
    assert result.learned_route_sample == result.required_route_sample
    assert result.learned_route_accuracy == 1.0
    assert result.learned_gate_accuracy == 1.0
    assert result.static_coil_accuracy == 0.5
    assert result.static_local_accuracy == 0.5
    assert result.wrong_period_route_accuracy < result.learned_route_accuracy
    assert result.wrong_period_gate_accuracy < result.learned_gate_accuracy
    assert result.flipped_gate_accuracy == 0.0
    assert result.union_candidate_accuracy == 1.0
    assert result.full_attention_accuracy == 1.0
    assert result.average_learned_candidate_count == 5.5
    assert result.average_union_candidate_count == 10.0
    assert result.average_full_candidate_count == 64.0
    assert result.note.endswith("not a model-quality claim.")


def test_looped_recurrence_schedule_traces_overthinking_boundary() -> None:
    assert tuple(loop_required_steps(4, sample) for sample in range(8)) == (1, 2, 3, 4, 1, 2, 3, 4)
    assert loop_score_trace(3, 6, overthink_tolerance=1) == (0, 0, 1, 1, 0, 0)
    assert not loop_score_active(4, 6, 2, overthink_tolerance=1)
    assert loop_score_active(4, 6, 3, overthink_tolerance=1)
    assert loop_score_active(4, 6, 4, overthink_tolerance=1)
    assert not loop_score_active(4, 6, 5, overthink_tolerance=1)
    assert loop_exit_step(3, 6, overthink_tolerance=1) == 3
    assert loop_exit_step(7, 4, overthink_tolerance=1) is None


def test_loop_exit_certificate_records_budget_and_guardrail() -> None:
    certificate = loop_exit_certificate(4, sample_index=6, max_loops=4, overthink_tolerance=1)
    blocked = loop_exit_certificate(4, sample_index=3, max_loops=2, overthink_tolerance=1)

    assert certificate.required_steps == 3
    assert certificate.overthinking_boundary == 4
    assert certificate.score_trace == (0, 0, 1, 1)
    assert certificate.exit_step == 3
    assert certificate.first_active_step == 3
    assert certificate.first_active_step_matches_exit
    assert certificate.exit_available_iff_first_active_within_budget
    assert certificate.no_exit_iff_no_active_within_budget
    assert certificate.exit_step > 0
    assert certificate.exit_available
    assert training_free_loop_budget(
        certificate.loop_period,
        certificate.sample_index,
        certificate.max_loops,
    ) == certificate.exit_step
    shifted = loop_exit_certificate(4, sample_index=6 + 3 * 4, max_loops=4, overthink_tolerance=1)
    assert shifted.exit_step == certificate.exit_step
    assert shifted.overthinking_boundary == certificate.overthinking_boundary
    assert certificate.within_budget
    assert certificate.within_guardrail
    assert certificate.note.endswith("not a model-quality claim.")
    assert blocked.required_steps == 4
    assert blocked.score_trace == (0, 0)
    assert blocked.exit_step is None
    assert blocked.first_active_step is None
    assert blocked.first_active_step_matches_exit
    assert blocked.exit_available_iff_first_active_within_budget
    assert blocked.no_exit_iff_no_active_within_budget
    assert not blocked.exit_available
    assert not blocked.within_budget
    assert not blocked.within_guardrail
    assert "AIM-T0084" in certificate.theorem_ids
    assert "AIM-T0085" in certificate.theorem_ids
    assert "AIM-T0090" in certificate.theorem_ids


def test_loop_required_steps_are_positive_bounded_and_periodic() -> None:
    for loop_period in range(1, 17):
        assert token_recurrence_budget(loop_period, 0) == 1
        for sample in range(0, 128):
            required = loop_required_steps(loop_period, sample)
            assert 0 < required <= loop_period
            assert token_recurrence_budget(loop_period, sample) > 0
            assert loop_required_steps(loop_period, sample + loop_period) == required
            for passes in range(0, 8):
                shifted = sample + passes * loop_period
                shifted_certificate = loop_exit_certificate(
                    loop_period,
                    shifted,
                    loop_period,
                    overthink_tolerance=2,
                )
                base_certificate = loop_exit_certificate(
                    loop_period,
                    sample,
                    loop_period,
                    overthink_tolerance=2,
                )
                assert loop_required_steps(loop_period, shifted) == required
                assert token_recurrence_budget(loop_period, shifted) == token_recurrence_budget(
                    loop_period,
                    sample,
                )
                assert training_free_loop_budget(loop_period, shifted, loop_period) == training_free_loop_budget(
                    loop_period,
                    sample,
                    loop_period,
                )
                assert shifted_certificate.exit_available == base_certificate.exit_available
                assert shifted_certificate.exit_step == base_certificate.exit_step
                assert shifted_certificate.overthinking_boundary == base_certificate.overthinking_boundary
            if required <= loop_period:
                assert training_free_loop_budget(loop_period, sample, loop_period) > 0
            if required > 1:
                assert training_free_loop_budget(loop_period, sample, required - 1) == required - 1


def test_looped_recurrence_benchmark_has_baselines_and_overloop_control() -> None:
    result = run_looped_recurrence_benchmark(
        loop_period=4,
        train_length=64,
        test_length=32,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=1,
    )

    assert result == run_looped_recurrence_benchmark(
        loop_period=4,
        train_length=64,
        test_length=32,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=1,
    )
    assert result.observed_exit_steps == (1, 2, 3, 4)
    assert result.single_pass_accuracy == 0.25
    assert result.fixed_loop_accuracy == 0.5
    assert result.adaptive_exit_accuracy == 1.0
    assert result.recurrent_memory_accuracy == 1.0
    assert result.sparse_phase_router_accuracy == 0.5
    assert result.over_looped_accuracy == 0.0
    assert result.nonperiodic_dense_threshold_accuracy == 1.0
    assert result.nonperiodic_dense_threshold_accuracy > result.nonperiodic_loop_phase_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_token_level_recurrence_budget_helpers_are_deterministic() -> None:
    tokens = tuple(range(8))
    budgets = token_recurrence_budgets(4, tokens)

    assert budgets == (1, 2, 3, 4, 1, 2, 3, 4)
    assert tuple(token_recurrence_budget(4, token) for token in tokens) == budgets
    assert tuple(token_recurrence_budget(4, token + 4) for token in tokens) == budgets
    assert all(token_active_at_step(4, token, 1) for token in tokens)
    assert all(token_active_at_step(4, token + 3 * 4, 2) == token_active_at_step(4, token, 2) for token in tokens)
    assert all(not token_active_at_step(4, token, 5) for token in tokens)
    assert active_token_counts_by_budget(budgets, 4) == (8, 6, 4, 2)
    assert recurrence_resolution_levels(4) == ("coarse", "fine", "coarse", "fine")


def test_looped_recurrent_state_matches_certified_budget_phase() -> None:
    samples = tuple(range(8))
    budgets = token_recurrence_budgets(4, samples)
    states = looped_recurrent_states(4, budgets)

    assert budgets == (1, 2, 3, 4, 1, 2, 3, 4)
    assert states == (0, 1, 2, 3, 0, 1, 2, 3)
    assert looped_recurrent_state(4, 1) == 0
    assert all(
        looped_recurrent_state(4, token_recurrence_budget(4, sample)) == sample % 4
        for sample in range(32)
    )
    assert all(
        looped_recurrent_state(4, token_recurrence_budget(4, sample + 5 * 4))
        == looped_recurrent_state(4, token_recurrence_budget(4, sample))
        for sample in range(32)
    )
    assert all(
        looped_recurrent_state(4, budget + 4) == looped_recurrent_state(4, budget)
        for budget in range(1, 17)
    )
    assert all(
        looped_recurrent_state(4, budget + passes * 4) == looped_recurrent_state(4, budget)
        for budget in range(1, 17)
        for passes in range(6)
    )


def test_token_level_recurrence_benchmark_has_per_token_and_wrong_loop_controls() -> None:
    result = run_token_level_recurrence_benchmark(
        loop_period=4,
        token_count=32,
        max_budget=4,
        fixed_global_budget=4,
        over_loop_budget=8,
        wrong_budget_shift=1,
        overthink_tolerance=0,
    )

    assert result == run_token_level_recurrence_benchmark(
        loop_period=4,
        token_count=32,
        max_budget=4,
        fixed_global_budget=4,
        over_loop_budget=8,
        wrong_budget_shift=1,
        overthink_tolerance=0,
    )
    assert result.selected_loop_block == (2, 5)
    assert result.token_budgets[:8] == (1, 2, 3, 4, 1, 2, 3, 4)
    assert result.active_token_counts == (32, 24, 16, 8)
    assert result.resolution_levels == ("coarse", "fine", "coarse", "fine")
    assert result.average_active_tokens == 20.0
    assert result.token_level_accuracy == 1.0
    assert result.fixed_global_budget_accuracy == 0.25
    assert result.wrong_budget_accuracy == 0.0
    assert result.over_looped_accuracy == 0.0
    assert result.nonperiodic_scalar_threshold_accuracy == 1.0
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_token_level_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_tiny_looped_recurrent_prototype_has_baselines_and_controls() -> None:
    result = run_tiny_looped_recurrent_prototype(
        period=4,
        wrong_period=3,
        train_length=64,
        test_length=32,
    )

    assert result == run_tiny_looped_recurrent_prototype(
        period=4,
        wrong_period=3,
        train_length=64,
        test_length=32,
    )
    assert result.learned_state_lookup == (0, 1, 0, 0)
    assert result.wrong_period_state_lookup == (0, 0, 0)
    assert result.required_state_sample == (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)
    assert result.learned_state_sample == result.required_state_sample
    assert result.one_step_state_sample == (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert result.raw_budget_state_sample == (0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3)
    assert result.shifted_raw_budget_state_sample == result.raw_budget_state_sample
    assert result.looped_recurrent_accuracy == 1.0
    assert result.phase_lookup_accuracy == 1.0
    assert result.one_step_accuracy < result.looped_recurrent_accuracy
    assert result.scalar_threshold_accuracy < result.looped_recurrent_accuracy
    assert result.wrong_period_state_accuracy < result.looped_recurrent_accuracy
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_looped_recurrent_accuracy
    assert result.average_unroll_steps == 2.5
    assert result.note.endswith("not a model-quality claim.")


def test_middle_block_recurrence_helpers_are_deterministic() -> None:
    samples = tuple(range(8))

    assert middle_block_budget_route(2, 3, 4, 0) == (2, 1)
    assert tuple(middle_block_route(2, 3, sample) for sample in samples) == (2, 3, 4, 2, 3, 4, 2, 3)
    assert tuple(middle_block_budget_route(2, 3, 4, sample) for sample in samples) == (
        (2, 1),
        (3, 2),
        (4, 3),
        (2, 4),
        (3, 1),
        (4, 2),
        (2, 3),
        (3, 4),
    )
    for sample in range(24):
        routed = middle_block_route(2, 3, sample)
        routed_with_budget = middle_block_budget_route(2, 3, 4, sample)
        assert 2 <= routed < 5
        assert routed_with_budget[0] == routed
        assert 2 <= routed_with_budget[0] < 5
        assert 0 < routed_with_budget[1] <= 4
        assert middle_block_route(2, 3, sample + 3) == routed
        assert middle_block_route(2, 3, sample + 4 * 3) == routed
        assert middle_block_budget_route(2, 3, 4, sample + 3 * 4) == routed_with_budget
        assert all(
            middle_block_budget_route(2, 3, 4, sample + passes * (3 * 4)) == routed_with_budget
            for passes in range(6)
        )
    assert middle_block_route(2, 3, 0) == 2
    assert loop_block_indices(8, (2, 5)) == (2, 3, 4)
    assert middle_block_required_blocks(8, (2, 5), samples) == (2, 3, 4, 2, 3, 4, 2, 3)


def test_middle_block_recurrence_benchmark_has_block_and_budget_controls() -> None:
    result = run_middle_block_recurrence_benchmark(
        block_count=8,
        sample_count=32,
        loop_period=4,
        selected_loop_block=(2, 5),
        wrong_loop_block=(0, 2),
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_middle_block_recurrence_benchmark(
        block_count=8,
        sample_count=32,
        loop_period=4,
        selected_loop_block=(2, 5),
        wrong_loop_block=(0, 2),
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.selected_loop_block == (2, 5)
    assert result.selected_block_indices == (2, 3, 4)
    assert result.required_block_sample == (2, 3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4)
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.selected_middle_block_accuracy == 1.0
    assert result.full_block_phase_budget_accuracy == 1.0
    assert result.fixed_loop_budget_accuracy == 0.25
    assert result.wrong_block_accuracy == 0.0
    assert result.over_looped_accuracy == 0.0
    assert result.average_selected_block_passes == 7.5
    assert result.average_full_block_passes == 20.0
    assert result.note.endswith("not a model-quality claim.")


def test_multi_resolution_recurrence_helpers_are_deterministic() -> None:
    budgets = (1, 2, 3, 4, 1, 2, 3, 4)

    assert multi_resolution_required_resolutions(4, budgets) == (
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
    )
    assert shifted_recurrence_resolutions(4, budgets, 1) == (
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
    )


def test_multi_resolution_recurrence_benchmark_has_resolution_and_budget_controls() -> None:
    result = run_multi_resolution_recurrence_benchmark(
        loop_period=4,
        sample_count=32,
        max_budget=4,
        fixed_loop_budget=4,
        wrong_resolution_shift=1,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_multi_resolution_recurrence_benchmark(
        loop_period=4,
        sample_count=32,
        max_budget=4,
        fixed_loop_budget=4,
        wrong_resolution_shift=1,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.resolution_levels == ("coarse", "fine", "coarse", "fine")
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.required_resolution_sample == (
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
    )
    assert result.active_sample_counts == (32, 24, 16, 8)
    assert result.average_active_samples == 20.0
    assert result.multi_resolution_accuracy == 1.0
    assert result.single_resolution_coarse_accuracy == 0.5
    assert result.single_resolution_fine_accuracy == 0.5
    assert result.fixed_budget_accuracy == 0.25
    assert result.wrong_resolution_accuracy == 0.0
    assert result.over_looped_accuracy == 0.0
    assert result.note.endswith("not a model-quality claim.")


def test_learned_recurrence_schedule_lookup_helpers_are_deterministic() -> None:
    positions = tuple(range(16))
    budgets = tuple(loop_required_steps(4, position) for position in positions)
    lookup = fit_loop_budget_lookup(4, positions, budgets)

    assert lookup == (1, 2, 3, 4)
    assert predict_loop_budget_lookup(4, lookup, tuple(range(16, 24))) == (1, 2, 3, 4, 1, 2, 3, 4)


def test_learned_middle_block_lookup_helpers_are_deterministic() -> None:
    samples = tuple(range(12))
    blocks = middle_block_required_blocks(8, (2, 5), samples)
    lookup = fit_loop_block_lookup(3, samples, blocks)

    assert lookup == (2, 3, 4)
    assert predict_loop_block_lookup(3, lookup, tuple(range(12, 20))) == (2, 3, 4, 2, 3, 4, 2, 3)


def test_learned_resolution_lookup_helpers_are_deterministic() -> None:
    samples = tuple(range(16))
    budgets = token_recurrence_budgets(4, samples)
    resolutions = multi_resolution_required_resolutions(4, budgets)
    lookup = fit_recurrence_resolution_lookup(4, samples, resolutions)

    assert lookup == ("coarse", "fine", "coarse", "fine")
    assert predict_recurrence_resolution_lookup(4, lookup, tuple(range(16, 24))) == (
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
    )


def test_learned_recurrence_schedule_benchmark_has_baselines_and_controls() -> None:
    result = run_learned_recurrence_schedule_benchmark(
        loop_period=4,
        wrong_period=3,
        train_length=64,
        test_length=32,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_learned_recurrence_schedule_benchmark(
        loop_period=4,
        wrong_period=3,
        train_length=64,
        test_length=32,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.learned_budget_lookup == (1, 2, 3, 4)
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.learned_budget_sample == result.required_budget_sample
    assert result.learned_phase_router_accuracy == 1.0
    assert result.fixed_loop_budget_accuracy == 0.25
    assert result.wrong_period_router_accuracy < result.learned_phase_router_accuracy
    assert result.over_looped_accuracy == 0.0
    assert result.note.endswith("not a model-quality claim.")


def test_learned_multi_resolution_recurrence_benchmark_has_resolution_controls() -> None:
    result = run_learned_multi_resolution_recurrence_benchmark(
        loop_period=4,
        wrong_budget_period=3,
        wrong_resolution_period=3,
        train_length=64,
        test_length=32,
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_learned_multi_resolution_recurrence_benchmark(
        loop_period=4,
        wrong_budget_period=3,
        wrong_resolution_period=3,
        train_length=64,
        test_length=32,
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.learned_budget_lookup == (1, 2, 3, 4)
    assert result.learned_resolution_lookup == ("coarse", "fine", "coarse", "fine")
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.learned_budget_sample == result.required_budget_sample
    assert result.required_resolution_sample == (
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
        "coarse",
        "fine",
    )
    assert result.learned_resolution_sample == result.required_resolution_sample
    assert result.active_sample_counts == (32, 24, 16, 8)
    assert result.average_active_samples == 20.0
    assert result.learned_multi_resolution_router_accuracy == 1.0
    assert result.single_resolution_coarse_accuracy == 0.5
    assert result.single_resolution_fine_accuracy == 0.5
    assert result.fixed_budget_accuracy == 0.25
    assert result.wrong_budget_period_accuracy < result.learned_multi_resolution_router_accuracy
    assert result.wrong_resolution_period_accuracy < result.learned_multi_resolution_router_accuracy
    assert result.over_looped_accuracy == 0.0
    assert result.note.endswith("not a model-quality claim.")


def test_learned_middle_block_recurrence_benchmark_has_block_and_budget_controls() -> None:
    result = run_learned_middle_block_recurrence_benchmark(
        block_count=8,
        train_length=64,
        test_length=32,
        loop_period=4,
        wrong_block_period=2,
        wrong_budget_period=3,
        selected_loop_block=(2, 5),
        wrong_loop_block=(0, 2),
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_learned_middle_block_recurrence_benchmark(
        block_count=8,
        train_length=64,
        test_length=32,
        loop_period=4,
        wrong_block_period=2,
        wrong_budget_period=3,
        selected_loop_block=(2, 5),
        wrong_loop_block=(0, 2),
        max_budget=4,
        fixed_loop_budget=4,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.block_period == 3
    assert result.learned_block_lookup == (2, 3, 4)
    assert result.learned_budget_lookup == (1, 2, 3, 4)
    assert result.required_block_sample == (3, 4, 2, 3, 4, 2, 3, 4, 2, 3, 4, 2)
    assert result.learned_block_sample == result.required_block_sample
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.learned_budget_sample == result.required_budget_sample
    assert result.active_sample_counts == (32, 24, 16, 8)
    assert result.learned_middle_block_router_accuracy == 1.0
    assert result.selected_band_phase_budget_accuracy == 1.0
    assert result.full_block_phase_budget_accuracy == 1.0
    assert result.fixed_loop_budget_accuracy == 0.25
    assert result.wrong_block_period_accuracy < result.learned_middle_block_router_accuracy
    assert result.wrong_budget_period_accuracy < result.learned_middle_block_router_accuracy
    assert result.wrong_loop_block_accuracy == 0.0
    assert result.over_looped_accuracy == 0.0
    assert result.average_learned_block_passes == 2.5
    assert result.average_selected_band_passes == 7.5
    assert result.average_full_block_passes == 20.0
    assert result.note.endswith("not a model-quality claim.")


def test_learned_token_level_recurrence_benchmark_has_token_router_controls() -> None:
    result = run_learned_token_level_recurrence_benchmark(
        loop_period=4,
        wrong_period=3,
        train_token_count=64,
        test_token_count=32,
        max_budget=4,
        fixed_global_budget=4,
        over_loop_budget=8,
        wrong_budget_shift=1,
        overthink_tolerance=0,
    )

    assert result == run_learned_token_level_recurrence_benchmark(
        loop_period=4,
        wrong_period=3,
        train_token_count=64,
        test_token_count=32,
        max_budget=4,
        fixed_global_budget=4,
        over_loop_budget=8,
        wrong_budget_shift=1,
        overthink_tolerance=0,
    )
    assert result.learned_budget_lookup == (1, 2, 3, 4)
    assert result.required_budget_sample == (1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4)
    assert result.learned_budget_sample == result.required_budget_sample
    assert result.wrong_shift_budget_sample == (2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 1)
    assert result.active_token_counts == (32, 24, 16, 8)
    assert result.average_active_tokens == 20.0
    assert result.learned_token_router_accuracy == 1.0
    assert result.fixed_global_budget_accuracy == 0.25
    assert result.wrong_period_router_accuracy < result.learned_token_router_accuracy
    assert result.wrong_shift_accuracy == 0.0
    assert result.over_looped_accuracy == 0.0
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_phase_lookup_accuracy
    assert result.note.endswith("not a model-quality claim.")


def test_training_free_loop_wrapper_budget_helpers_are_deterministic() -> None:
    samples = tuple(range(8))
    budgets = training_free_loop_budgets(4, samples, 4)

    assert budgets == (1, 2, 3, 4, 1, 2, 3, 4)
    assert tuple(training_free_loop_budget(4, sample, 4) for sample in samples) == budgets
    capped = training_free_loop_budgets(4, samples, 2)
    assert capped == (1, 2, 2, 2, 1, 2, 2, 2)
    assert all(budget <= 2 for budget in capped)
    assert training_free_loop_budget(4, 3, 2) == 2


def test_training_free_loop_wrapper_benchmark_has_baselines_and_controls() -> None:
    result = run_training_free_loop_wrapper_benchmark(
        loop_period=4,
        sample_count=32,
        max_loops=4,
        fixed_loop_budget=2,
        wrong_loop_period=3,
        over_loop_budget=8,
        overthink_tolerance=0,
    )

    assert result == run_training_free_loop_wrapper_benchmark(
        loop_period=4,
        sample_count=32,
        max_loops=4,
        fixed_loop_budget=2,
        wrong_loop_period=3,
        over_loop_budget=8,
        overthink_tolerance=0,
    )
    assert result.backend == "cpu"
    assert result.phase_budgets[:8] == (1, 2, 3, 4, 1, 2, 3, 4)
    assert result.active_sample_counts == (32, 24, 16, 8)
    assert result.budget_histogram == ((1, 8), (2, 8), (3, 8), (4, 8))
    assert result.average_phase_budget == 2.5
    assert result.single_pass_accuracy == 0.25
    assert result.fixed_loop_accuracy == 0.25
    assert result.training_free_phase_budget_accuracy == 1.0
    assert result.wrong_period_budget_accuracy < result.training_free_phase_budget_accuracy
    assert result.over_loop_no_exit_accuracy == 0.0
    assert result.nonperiodic_scalar_threshold_accuracy == 1.0
    assert result.nonperiodic_scalar_threshold_accuracy > result.nonperiodic_phase_budget_accuracy
    assert result.note.endswith("not a model-quality claim.")
