from __future__ import annotations

from scripts.tune_prime_engine import best_for_range, parse_count_modes, rust_row_to_sample


def tuning_row(**overrides: str) -> dict[str, str]:
    row = {
        "kind": "tuning",
        "timestamp_unix": "1780000000",
        "pass": "1",
        "count_mode": "segmented",
        "low": "0",
        "high": "100000000",
        "span": "100000000",
        "segment_size": "131072",
        "requested_threads": "8",
        "threads": "8",
        "rounds": "9",
        "count": "5761455",
        "best_ms": "5.000",
        "median_ms": "6.000",
        "rate_per_second": "20000000000",
        "median_rate_per_second": "16666666666",
    }
    row.update(overrides)
    return row


def test_rust_tuner_rows_parse_median_timing() -> None:
    sample = rust_row_to_sample(tuning_row(), "20260619T120000Z")

    assert sample.best_ms == 5.0
    assert sample.median_ms == 6.0
    assert sample.count_mode == "segmented"
    assert sample.rate_per_second == 20_000_000_000.0
    assert sample.median_rate_per_second == 16_666_666_666.0


def test_rust_tuner_rows_fall_back_for_older_csv_shape() -> None:
    row = tuning_row()
    del row["count_mode"]
    del row["median_ms"]
    del row["median_rate_per_second"]

    sample = rust_row_to_sample(row, "20260619T120000Z")

    assert sample.count_mode == "segmented"
    assert sample.median_ms == sample.best_ms
    assert sample.median_rate_per_second == sample.rate_per_second


def test_best_for_range_prefers_median_over_lucky_best() -> None:
    lucky_but_noisy = rust_row_to_sample(
        tuning_row(segment_size="131072", best_ms="4.000", median_ms="8.000"),
        "20260619T120000Z",
    )
    stable = rust_row_to_sample(
        tuning_row(segment_size="196608", best_ms="5.000", median_ms="6.000"),
        "20260619T120000Z",
    )

    assert best_for_range([lucky_but_noisy, stable], 0, 100000000) == stable


def test_best_for_range_can_select_faster_count_mode() -> None:
    segmented = rust_row_to_sample(
        tuning_row(count_mode="segmented", best_ms="5.000", median_ms="6.000"),
        "20260619T120000Z",
    )
    hybrid = rust_row_to_sample(
        tuning_row(
            count_mode="hybrid-wheel30-mark",
            best_ms="4.500",
            median_ms="5.500",
        ),
        "20260619T120000Z",
    )

    assert best_for_range([segmented, hybrid], 0, 100000000) == hybrid


def test_parse_count_modes_dedupes_in_stable_priority_order() -> None:
    assert parse_count_modes(
        "hybrid-wheel30-mark,dynamic,segmented,hybrid-wheel30-mark"
    ) == [
        "segmented",
        "dynamic",
        "hybrid-wheel30-mark",
    ]
