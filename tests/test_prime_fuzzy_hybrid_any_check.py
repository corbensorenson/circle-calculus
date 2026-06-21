from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.check_prime_fuzzy_hybrid_any import validate_artifact


TIMING_NAMES = [
    "circle_fuzzy_hybrid_python_any_prime",
    "circle_fuzzy_hybrid_rust_server_any_prime",
    "deterministic_python_mr64_any_prime",
    "circle_prime_server_next_prime",
    "external_primesieve_generate_next_server",
    "external_primesieve_iterator_next_server",
    "external_primecount_next_server",
]


def write_artifacts(
    tmp_path: Path,
    *,
    bad_prime: bool = False,
) -> tuple[Path, Path]:
    csv_path = tmp_path / "fuzzy_any.csv"
    metadata_path = tmp_path / "fuzzy_any.json"
    fieldnames = [
        "kind",
        "name",
        "start",
        "batch_size",
        "result",
        "candidate_count",
        "rounds",
        "best_ms",
        "median_ms",
        "searches_per_second",
        "median_searches_per_second",
        "threads",
        "requested_threads",
        "baseline",
        "best_speedup",
        "median_speedup",
        "sample_count",
        "sample_noise_ms",
        "sample_max_ms",
        "sample_noise_over_median",
        "sample_max_over_median",
        "sample_ignored_single_high_outlier",
        "sample_stability",
    ]
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, name in enumerate(TIMING_NAMES):
            writer.writerow(
                {
                    "kind": "timing",
                    "name": name,
                    "start": "1000000",
                    "batch_size": "8",
                    "result": "1000004" if bad_prime and index == 0 else "1000003",
                    "candidate_count": "2",
                    "rounds": "3",
                    "best_ms": "0.1",
                    "median_ms": "0.2",
                    "searches_per_second": "80",
                    "median_searches_per_second": "40",
                    "threads": "1",
                    "requested_threads": "1",
                    "baseline": "",
                    "best_speedup": "",
                    "median_speedup": "",
                }
            )
        for baseline in TIMING_NAMES:
            if baseline == "circle_fuzzy_hybrid_rust_server_any_prime":
                continue
            writer.writerow(
                {
                    "kind": "speedup",
                    "name": "circle_fuzzy_hybrid_rust_server_any_prime",
                    "start": "1000000",
                    "batch_size": "8",
                    "result": "1000003",
                    "candidate_count": "2",
                    "rounds": "3",
                    "best_ms": "0.1",
                    "median_ms": "0.2",
                    "searches_per_second": "80",
                    "median_searches_per_second": "40",
                    "threads": "1",
                    "requested_threads": "1",
                    "baseline": baseline,
                    "best_speedup": "2.0",
                    "median_speedup": "1.5",
                }
            )
    metadata_path.write_text(
        json.dumps(
            {
                "schema_id": "circle_calculus.prime_fuzzy_hybrid_any_benchmark.v0",
                "starts": [1000000],
                "rounds": 3,
                "batch_size": 8,
                "warmup_rounds": 1,
                "top_k": 8,
                "score_limit": 64,
                "search_window": 512,
                "search_mode": "any-prime",
                "rust_model_fingerprint": {"available": True},
                "hybrid_proof_contract": {
                    "name": "prime_fuzzy_hybrid_verified_prime_search_v0",
                    "neural_role": "candidate_ordering_only",
                    "deterministic_prefilter": "deterministic wheel prefilter",
                    "acceptance_rule": "requires deterministic verification",
                },
                "not_claimed": ["any-prime rows do not claim next prime"],
                "tools": {
                    "circle_prime": {"available": True},
                    "primesieve": {"available": True},
                    "primecount": {"available": True},
                    "primesieve_library_server": {"available": True},
                    "primesieve_iterator_server": {"available": True},
                    "primecount_library_server": {"available": True},
                },
            }
        )
    )
    return csv_path, metadata_path


def test_fuzzy_hybrid_any_check_accepts_complete_artifact(tmp_path: Path) -> None:
    csv_path, metadata_path = write_artifacts(tmp_path)

    assert validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        expect_starts={1000000},
        expect_rounds=3,
        expect_batch_size=8,
        expect_warmup_rounds=1,
        expect_search_window=512,
        expect_top_k=8,
        expect_score_limit=64,
        min_rust_median_speedups={"deterministic_python_mr64_any_prime": 1.0},
    ) == []


def test_fuzzy_hybrid_any_check_rejects_non_prime_result(tmp_path: Path) -> None:
    csv_path, metadata_path = write_artifacts(tmp_path, bad_prime=True)

    failures = validate_artifact(csv_path=csv_path, metadata_path=metadata_path)

    assert any("is not prime" in failure for failure in failures)


def test_fuzzy_hybrid_any_check_rejects_competitor_floor_miss(
    tmp_path: Path,
) -> None:
    csv_path, metadata_path = write_artifacts(tmp_path)

    failures = validate_artifact(
        csv_path=csv_path,
        metadata_path=metadata_path,
        min_rust_median_speedups={"external_primesieve_generate_next_server": 2.0},
    )

    assert any("external_primesieve_generate_next_server" in failure for failure in failures)
    assert any("below required" in failure for failure in failures)
