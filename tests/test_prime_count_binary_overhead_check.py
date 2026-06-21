from __future__ import annotations

import pytest

from scripts.check_prime_count_binary_overhead_readout import (
    SpeedupRow,
    check_count_binary_overhead,
    summarize_count_binary_overhead,
)


def speedup_row(
    *,
    name: str,
    baseline: str,
    median_ms: float,
    median_speedup: float,
) -> SpeedupRow:
    return SpeedupRow(
        name=name,
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        baseline=baseline,
        median_ms=median_ms,
        best_ms=median_ms * 0.9,
        median_speedup=median_speedup,
        best_speedup=median_speedup * 0.95,
        sample_stability="stable",
    )


def startup_bound_rows() -> list[SpeedupRow]:
    return [
        speedup_row(
            name="circle_prime_count_binary_parallel_default_count_8t",
            baseline="external_primesieve_count",
            median_ms=5.0,
            median_speedup=0.95,
        ),
        speedup_row(
            name="circle_prime_count_binary_server_parallel_default_count_8t",
            baseline="external_primesieve_count_server",
            median_ms=2.0,
            median_speedup=1.20,
        ),
    ]


def test_count_binary_overhead_classifies_startup_bound_lane() -> None:
    overhead = summarize_count_binary_overhead(startup_bound_rows())

    assert overhead.diagnosis == "cold_process_or_startup_bound"
    assert overhead.circle_cold_over_hot == pytest.approx(2.5)
    assert overhead.circle_cold_extra_ms == pytest.approx(3.0)
    assert overhead.primesieve_cli_median_ms == pytest.approx(4.75)
    assert overhead.libprimesieve_median_ms == pytest.approx(2.4)


def test_count_binary_overhead_passes_when_hot_lane_still_wins() -> None:
    result = check_count_binary_overhead(startup_bound_rows())

    assert result["ok"] is True
    assert result["overhead"].diagnosis == "cold_process_or_startup_bound"


def test_count_binary_overhead_fails_when_hot_lane_loses() -> None:
    rows = [
        speedup_row(
            name="circle_prime_count_binary_parallel_default_count_8t",
            baseline="external_primesieve_count",
            median_ms=5.0,
            median_speedup=0.95,
        ),
        speedup_row(
            name="circle_prime_count_binary_server_parallel_default_count_8t",
            baseline="external_primesieve_count_server",
            median_ms=2.0,
            median_speedup=0.97,
        ),
    ]

    result = check_count_binary_overhead(rows)

    assert result["ok"] is False
    assert "hot count-binary server speedup 0.970x" in result["message"]
    assert result["overhead"].diagnosis == "hot_algorithm_gap"


def test_count_binary_overhead_requires_comparable_rows() -> None:
    result = check_count_binary_overhead([])

    assert result["ok"] is False
    assert "missing speedup row" in result["message"]
