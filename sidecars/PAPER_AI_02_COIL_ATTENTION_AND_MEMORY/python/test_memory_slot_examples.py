from circle_math.applications.circle_ai import (
    active_token_counts_by_budget,
    average_candidate_count,
    coil_attention_path,
    content_route_label,
    fit_loop_budget_lookup,
    fit_loop_block_lookup,
    fit_content_route_lookup,
    fit_memory_slot_lookup,
    fit_recurrence_resolution_lookup,
    local_window_indices,
    loop_exit_certificate,
    loop_exit_step,
    loop_block_indices,
    loop_required_steps,
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
    run_training_free_loop_wrapper_benchmark,
    run_token_level_recurrence_benchmark,
    shifted_recurrence_resolutions,
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
    assert loop_exit_step(3, 6, overthink_tolerance=1) == 3
    assert loop_exit_step(7, 4, overthink_tolerance=1) is None


def test_loop_exit_certificate_records_budget_and_guardrail() -> None:
    certificate = loop_exit_certificate(4, sample_index=6, max_loops=4, overthink_tolerance=1)
    blocked = loop_exit_certificate(4, sample_index=3, max_loops=2, overthink_tolerance=1)

    assert certificate.required_steps == 3
    assert certificate.overthinking_boundary == 4
    assert certificate.score_trace == (0, 0, 1, 1)
    assert certificate.exit_step == 3
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
    assert not blocked.exit_available
    assert not blocked.within_budget
    assert not blocked.within_guardrail


def test_loop_required_steps_are_positive_bounded_and_periodic() -> None:
    for loop_period in range(1, 17):
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
