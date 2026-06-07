from circle_math.applications.circle_ai import (
    fit_memory_slot_lookup,
    memory_slot,
    memory_slot_collision_count,
    memory_slot_loads,
    predict_memory_slot_lookup,
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
