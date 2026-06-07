from circle_math.applications.circle_ai import (
    coil_attention_path,
    fit_memory_slot_lookup,
    local_window_indices,
    memory_slot,
    memory_slot_collision_count,
    memory_slot_loads,
    predict_memory_slot_lookup,
    retrieval_target_index,
    run_coil_retrieval_benchmark,
    run_memory_slot_benchmark,
    synthetic_memory_slot_dataset,
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
