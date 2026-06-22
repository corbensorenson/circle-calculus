from __future__ import annotations

import pytest

from scripts.check_prime_count_binary_overhead_readout import (
    SpeedupRow,
    TimingRow,
    check_count_binary_overhead,
    summarize_count_binary_overhead,
    summarize_hot_cold_decomposition,
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


def hot_cold_rows() -> list[TimingRow]:
    return [
        TimingRow(
            name="cold_count_binary_high_offset_noop",
            workload=0,
            segment_size=0,
            result=0,
            rounds=17,
            best_ms=1.50,
        ),
        TimingRow(
            name="cold_count_binary_high_offset_default_plan_8t",
            workload=10_000_000,
            segment_size=1_507_328,
            result=7,
            rounds=17,
            best_ms=1.25,
        ),
        TimingRow(
            name="cold_count_binary_parallel_high_offset_default_range_count_8t",
            workload=10_000_000,
            segment_size=1_507_328,
            result=361_726,
            rounds=17,
            best_ms=4.05,
        ),
        TimingRow(
            name="hot_cli_count_server_parallel_high_offset_default_range_count_8t",
            workload=10_000_000,
            segment_size=1_507_328,
            result=361_726,
            rounds=17,
            best_ms=1.65,
        ),
    ]


def test_count_binary_overhead_classifies_startup_bound_lane() -> None:
    overhead = summarize_count_binary_overhead(startup_bound_rows())

    assert overhead.diagnosis == "cold_process_or_startup_bound"
    assert overhead.circle_cold_over_hot == pytest.approx(2.5)
    assert overhead.circle_cold_extra_ms == pytest.approx(3.0)
    assert overhead.primesieve_cli_median_ms == pytest.approx(4.75)
    assert overhead.libprimesieve_median_ms == pytest.approx(2.4)


def test_hot_cold_decomposition_quantifies_launch_and_thread_gap() -> None:
    decomposition = summarize_hot_cold_decomposition(hot_cold_rows())

    assert decomposition.diagnosis == "cold_launch_thread_first_touch_bound"
    assert decomposition.cold_over_hot_best == pytest.approx(4.05 / 1.65)
    assert decomposition.cold_extra_best_ms == pytest.approx(2.4)
    assert decomposition.noop_share_of_cold_extra == pytest.approx(1.5 / 2.4)
    assert decomposition.residual_after_noop_ms == pytest.approx(0.9)
    assert decomposition.next_action == "launch_amortization_required"


def test_hot_cold_decomposition_classifies_residual_thread_gap() -> None:
    rows = [
        row
        if row.name != "cold_count_binary_high_offset_noop"
        else TimingRow(
            name=row.name,
            workload=row.workload,
            segment_size=row.segment_size,
            result=row.result,
            rounds=row.rounds,
            best_ms=0.40,
        )
        for row in hot_cold_rows()
    ]

    decomposition = summarize_hot_cold_decomposition(rows)

    assert decomposition.noop_share_of_cold_extra == pytest.approx(0.40 / 2.4)
    assert decomposition.residual_after_noop_ms == pytest.approx(2.0)
    assert decomposition.next_action == "thread_first_touch_reduction_required"


def test_hot_cold_decomposition_uses_spawn_row_for_narrower_action() -> None:
    rows = [
        row
        if row.name != "cold_count_binary_high_offset_noop"
        else TimingRow(
            name=row.name,
            workload=row.workload,
            segment_size=row.segment_size,
            result=row.result,
            rounds=row.rounds,
            best_ms=0.40,
        )
        for row in hot_cold_rows()
    ]
    rows.append(
        TimingRow(
            name="cold_count_binary_high_offset_default_spawn_8t",
            workload=10_000_000,
            segment_size=1_507_328,
            result=7,
            rounds=17,
            best_ms=1.35,
        )
    )

    decomposition = summarize_hot_cold_decomposition(rows)

    assert decomposition.cold_spawn_best_ms == pytest.approx(1.35)
    assert decomposition.spawn_share_of_cold_extra == pytest.approx(1.35 / 2.4)
    assert decomposition.residual_after_spawn_ms == pytest.approx(1.05)
    assert decomposition.next_action == "scoped_thread_spawn_reduction_required"


def test_hot_cold_decomposition_identifies_post_spawn_residual() -> None:
    rows = [
        row
        if row.name != "cold_count_binary_high_offset_noop"
        else TimingRow(
            name=row.name,
            workload=row.workload,
            segment_size=row.segment_size,
            result=row.result,
            rounds=row.rounds,
            best_ms=0.40,
        )
        for row in hot_cold_rows()
    ]
    rows.append(
        TimingRow(
            name="cold_count_binary_high_offset_default_spawn_8t",
            workload=10_000_000,
            segment_size=1_507_328,
            result=7,
            rounds=17,
            best_ms=1.00,
        )
    )

    decomposition = summarize_hot_cold_decomposition(rows)

    assert decomposition.spawn_share_of_cold_extra == pytest.approx(1.00 / 2.4)
    assert decomposition.residual_after_spawn_ms == pytest.approx(1.4)
    assert decomposition.next_action == "scratch_or_marking_first_touch_required"


def test_count_binary_overhead_passes_when_hot_lane_still_wins() -> None:
    result = check_count_binary_overhead(startup_bound_rows())

    assert result["ok"] is True
    assert result["overhead"].diagnosis == "cold_process_or_startup_bound"


def test_count_binary_overhead_accepts_supporting_hot_cold_decomposition() -> None:
    result = check_count_binary_overhead(startup_bound_rows(), hot_cold_rows=hot_cold_rows())

    assert result["ok"] is True
    assert result["hot_cold"].cold_over_hot_best == pytest.approx(4.05 / 1.65)
    assert result["hot_cold"].next_action == "launch_amortization_required"


def test_count_binary_overhead_rejects_weak_hot_cold_gap() -> None:
    rows = [
        row
        if row.name != "cold_count_binary_parallel_high_offset_default_range_count_8t"
        else TimingRow(
            name=row.name,
            workload=row.workload,
            segment_size=row.segment_size,
            result=row.result,
            rounds=row.rounds,
            best_ms=2.0,
        )
        for row in hot_cold_rows()
    ]

    result = check_count_binary_overhead(startup_bound_rows(), hot_cold_rows=rows)

    assert result["ok"] is False
    assert "hot/cold best-time ratio" in result["message"]


def test_count_binary_overhead_rejects_weak_noop_share() -> None:
    rows = [
        row
        if row.name != "cold_count_binary_high_offset_noop"
        else TimingRow(
            name=row.name,
            workload=row.workload,
            segment_size=row.segment_size,
            result=row.result,
            rounds=row.rounds,
            best_ms=0.10,
        )
        for row in hot_cold_rows()
    ]

    result = check_count_binary_overhead(startup_bound_rows(), hot_cold_rows=rows)

    assert result["ok"] is False
    assert "fresh-process no-op share" in result["message"]


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
