from __future__ import annotations

import pytest

from scripts.prime_fuzzy_hybrid import (
    BuiltinMr64Labeler,
    SCHEMA_ID,
    TinyBitLogisticModel,
    bits_lsb,
    feature_vector,
    hybrid_contract,
    hybrid_next_prime_search,
    hybrid_prime_search,
    hybrid_prime_search_batch,
    is_prime_u64_mr,
    parse_args,
    run_experiment,
    sample_numbers,
)
from scripts.benchmark_prime_fuzzy_hybrid_next import deterministic_next_prime


def test_bits_lsb_uses_least_significant_bit_first_order() -> None:
    assert bits_lsb(0b10110, 6).tolist() == [0.0, 1.0, 1.0, 0.0, 1.0, 0.0]


def test_feature_vector_appends_bit_derived_residue_flags() -> None:
    assert feature_vector(15, 5, (3, 5, 7)).tolist() == [
        1.0,
        1.0,
        1.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ]


def test_tiny_model_exports_rust_text_format() -> None:
    model = TinyBitLogisticModel(
        bit_width=4,
        weights=(0.1, 0.2, 0.3, 0.4),
        bias=-0.5,
    )

    text = model.to_text()

    assert text.startswith("circle_fuzzy_model_v0\n")
    assert "bit_width 4\n" in text
    assert "residue_moduli none\n" in text
    assert "weights 0.10000000000000001" in text
    assert "bias -0.5\n" in text


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (0, False),
        (1, False),
        (2, True),
        (97, True),
        (561, False),
        (4_294_967_291, True),
        (4_294_967_295, False),
    ],
)
def test_builtin_mr64_reference_classifies_known_values(
    candidate: int,
    expected: bool,
) -> None:
    assert is_prime_u64_mr(candidate) is expected


def test_odd_only_sampling_stays_inside_range() -> None:
    samples = sample_numbers(low=4, high=9, count=64, seed=7, odd_only=True)

    assert set(samples) <= {5, 7}


def test_hybrid_experiment_reports_proof_bounded_contract() -> None:
    args = parse_args(
        [
            "--bit-width",
            "10",
            "--train-high",
            "512",
            "--eval-low",
            "512",
            "--eval-high",
            "768",
            "--train-samples",
            "96",
            "--eval-samples",
            "48",
            "--epochs",
            "6",
            "--learning-rate",
            "0.1",
            "--search-start",
            "100",
            "--search-window",
            "80",
            "--top-k",
            "4",
        ]
    )

    report = run_experiment(args)
    search = report["hybrid_search"]
    contract = report["hybrid_proof_contract"]

    assert report["schema_id"] == SCHEMA_ID
    assert report["model"]["parameter_count"] == 11
    assert report["evaluation"]["sample_count"] == 48
    assert isinstance(search, dict)
    assert search["deterministically_verified"] is True
    assert is_prime_u64_mr(search["reported_prime"])
    assert contract["neural_role"] == "candidate_ordering_only"
    assert "deterministic" in contract["deterministic_prefilter"]
    assert "deterministic verification" in contract["acceptance_rule"]
    assert any("silently discarded" in item for item in contract["not_claimed"])


def test_residue_feature_experiment_reports_tiny_residue_model() -> None:
    args = parse_args(
        [
            "--bit-width",
            "10",
            "--train-high",
            "512",
            "--eval-low",
            "512",
            "--eval-high",
            "768",
            "--train-samples",
            "96",
            "--eval-samples",
            "48",
            "--epochs",
            "6",
            "--learning-rate",
            "0.1",
            "--residue-moduli",
            "3,5,7",
        ]
    )

    report = run_experiment(args)

    assert report["model"]["kind"] == "tiny_bit_residue_logistic"
    assert report["model"]["feature_count"] == 13
    assert report["model"]["parameter_count"] == 14
    assert report["training"]["residue_moduli"] == [3, 5, 7]


def test_hybrid_search_falls_back_to_deterministic_scan_without_discarding() -> None:
    model = TinyBitLogisticModel(
        bit_width=8,
        weights=tuple(0.0 for _ in range(8)),
        bias=-100.0,
    )

    search = hybrid_prime_search(
        model,
        BuiltinMr64Labeler(),
        start=14,
        window=10,
        top_k=1,
    )

    assert search["reported_prime"] == 17
    assert search["baseline_first_prime"] == 17
    assert search["reported_prime_is_baseline_first_prime"] is True
    assert search["used_deterministic_fallback"] is True
    assert search["hybrid_deterministic_checks"] == 2


def test_exact_next_search_certifies_baseline_next_prime() -> None:
    model = TinyBitLogisticModel(
        bit_width=8,
        weights=tuple(0.0 for _ in range(8)),
        bias=0.0,
    )

    search = hybrid_next_prime_search(
        model,
        BuiltinMr64Labeler(),
        start=14,
        window=16,
        top_k=3,
    )

    assert search["search_kind"] == "exact_next_prime_in_window"
    assert search["reported_prime"] == 17
    assert search["exact_next_certified"] is True
    assert search["reported_prime_is_baseline_first_prime"] is True
    assert "earlier candidate" in search["certification_rule"]


def test_fuzzy_hybrid_benchmark_deterministic_next_helper() -> None:
    assert deterministic_next_prime(BuiltinMr64Labeler(), 100, 32) == (101, 1)
    assert deterministic_next_prime(BuiltinMr64Labeler(), 102, 32) == (103, 1)


def test_hybrid_search_batch_reports_all_windows() -> None:
    model = TinyBitLogisticModel(
        bit_width=8,
        weights=tuple(0.0 for _ in range(8)),
        bias=0.0,
    )

    searches = hybrid_prime_search_batch(
        model,
        BuiltinMr64Labeler(),
        search_mode="any-prime",
        start=90,
        window=32,
        top_k=2,
        runs=3,
        stride=32,
    )

    assert [search["start"] for search in searches] == [90, 122, 154]
    assert all(search["deterministically_verified"] for search in searches)


def test_experiment_rejects_search_range_that_exceeds_bit_width() -> None:
    args = parse_args(
        [
            "--bit-width",
            "8",
            "--search-start",
            "300",
            "--search-window",
            "10",
        ]
    )

    with pytest.raises(ValueError, match="increase --bit-width"):
        run_experiment(args)


def test_hybrid_contract_does_not_claim_neural_proof() -> None:
    contract = hybrid_contract()

    assert contract["rust_domain"] == "u64_exact_arithmetic"
    assert "model weights are not theorem proved" in contract["not_claimed"]
