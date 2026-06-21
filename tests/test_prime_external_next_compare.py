from __future__ import annotations

from scripts.compare_prime_external_next import (
    NextComparison,
    NextSpeedupRow,
    compare_speedup_rows,
    comparison_failures,
    render_comparison_table,
)


def speedup_row(
    *,
    name: str = "circle_prime_next_prime",
    start: int = 1_000_000_000_000,
    batch_size: int = 1,
    result: int = 1_000_000_000_039,
    candidate_count: int = 12,
    threads: int = 1,
    requested_threads: int = 1,
    baseline: str = "external_primesieve_next_prime",
    best_speedup: float = 1.2,
    median_speedup: float = 1.1,
    sample_stability: str = "stable",
) -> NextSpeedupRow:
    return NextSpeedupRow(
        name=name,
        start=start,
        batch_size=batch_size,
        result=result,
        candidate_count=candidate_count,
        threads=threads,
        requested_threads=requested_threads,
        baseline=baseline,
        best_speedup=best_speedup,
        median_speedup=median_speedup,
        sample_stability=sample_stability,
    )


def test_compare_next_speedup_rows_matches_selected_starts() -> None:
    baseline_row = speedup_row(best_speedup=1.2, median_speedup=1.1)
    candidate_row = speedup_row(best_speedup=1.25, median_speedup=1.15)
    ignored_row = speedup_row(start=90, result=97, candidate_count=2)

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row, ignored_row.key: ignored_row},
        candidate_rows={candidate_row.key: candidate_row},
        starts={1_000_000_000_000},
    )

    assert len(comparisons) == 1
    assert comparisons[0].median_speedup_ratio == 1.15 / 1.1
    assert comparisons[0].candidate_sample_stability == "stable"
    assert not comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
    )


def test_compare_next_speedup_rows_requires_selected_baseline_coverage() -> None:
    first = speedup_row(start=4_294_967_000, result=4_294_967_029, candidate_count=8)
    second = speedup_row(start=1_000_000_000_000)
    candidate = speedup_row(
        start=4_294_967_000,
        result=4_294_967_029,
        candidate_count=8,
        best_speedup=1.1,
    )

    try:
        compare_speedup_rows(
            baseline_rows={first.key: first, second.key: second},
            candidate_rows={candidate.key: candidate},
            starts={4_294_967_000, 1_000_000_000_000},
        )
    except ValueError as exc:
        assert "candidate CSV is missing selected baseline next-prime speedup row(s)" in str(exc)
        assert "start=1000000000000" in str(exc)
    else:
        raise AssertionError("expected missing selected baseline speedup row to fail")


def test_compare_next_speedup_rows_can_allow_candidate_subset() -> None:
    first = speedup_row(start=4_294_967_000, result=4_294_967_029, candidate_count=8)
    second = speedup_row(start=1_000_000_000_000)
    candidate = speedup_row(
        start=4_294_967_000,
        result=4_294_967_029,
        candidate_count=8,
        best_speedup=1.1,
    )

    comparisons = compare_speedup_rows(
        baseline_rows={first.key: first, second.key: second},
        candidate_rows={candidate.key: candidate},
        starts={4_294_967_000, 1_000_000_000_000},
        require_baseline_coverage=False,
    )

    assert len(comparisons) == 1
    assert comparisons[0].key == first.key


def test_next_comparison_failures_detect_regressions_and_result_mismatch() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row().key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_061,
            baseline_candidate_count=12,
            candidate_candidate_count=19,
            baseline_best_speedup=1.2,
            candidate_best_speedup=0.8,
            baseline_median_speedup=1.1,
            candidate_median_speedup=0.7,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
    )

    assert any("result changed" in failure for failure in failures)
    assert any("median speedup regressed" in failure for failure in failures)
    assert any("best speedup regressed" in failure for failure in failures)


def test_next_median_regression_can_be_tolerated_when_best_speedup_stays_close() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row().key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=1.2,
            candidate_best_speedup=1.1,
            baseline_median_speedup=1.1,
            candidate_median_speedup=0.8,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        median_regression_best_speedup_ratio_floor=0.90,
    )

    assert failures == []


def test_next_best_regression_can_be_tolerated_when_median_speedup_stays_close() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row().key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=1.2,
            candidate_best_speedup=0.9,
            baseline_median_speedup=1.1,
            candidate_median_speedup=1.05,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        best_regression_median_speedup_ratio_floor=0.90,
    )

    assert failures == []


def test_next_dominant_speedup_rows_use_lower_ratio_floor() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(
                name="circle_prime_server_next_prime",
                start=18_446_744_073_709_551_500,
            ).key,
            baseline_result=18_446_744_073_709_551_521,
            candidate_result=18_446_744_073_709_551_521,
            baseline_candidate_count=5,
            candidate_candidate_count=5,
            baseline_best_speedup=28_000.0,
            candidate_best_speedup=24_600.0,
            baseline_median_speedup=23_100.0,
            candidate_median_speedup=18_800.0,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        dominant_speedup_floor=1000.0,
        dominant_min_speedup_ratio=0.75,
    )

    assert failures == []


def test_next_dominant_speedup_floor_still_rejects_large_collapse() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(
                name="circle_prime_server_next_prime",
                start=18_446_744_073_709_551_500,
            ).key,
            baseline_result=18_446_744_073_709_551_521,
            candidate_result=18_446_744_073_709_551_521,
            baseline_candidate_count=5,
            candidate_candidate_count=5,
            baseline_best_speedup=28_000.0,
            candidate_best_speedup=1_100.0,
            baseline_median_speedup=23_100.0,
            candidate_median_speedup=1_100.0,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        dominant_speedup_floor=1000.0,
        dominant_min_speedup_ratio=0.75,
    )

    assert any("median speedup regressed" in failure for failure in failures)
    assert any("best speedup regressed" in failure for failure in failures)


def test_next_comparison_failures_can_require_serious_control_win() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row().key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=0.9,
            candidate_best_speedup=0.95,
            baseline_median_speedup=0.8,
            candidate_median_speedup=0.9,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        require_any_median_speedup_at_least=1.0,
    )

    assert failures == ["no compared row met required candidate median speedup 1.000"]


def test_next_comparison_failures_can_require_every_selected_row_to_win() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(
                name="circle_prime_server_next_prime",
                baseline="external_primesieve_generate_next_server",
                start=4_294_967_000,
            ).key,
            baseline_result=4_294_967_029,
            candidate_result=4_294_967_029,
            baseline_candidate_count=8,
            candidate_candidate_count=8,
            baseline_best_speedup=2.0,
            candidate_best_speedup=2.1,
            baseline_median_speedup=2.4,
            candidate_median_speedup=2.2,
        ),
        NextComparison(
            key=speedup_row(
                name="circle_prime_server_next_prime",
                baseline="external_primesieve_generate_next_server",
                start=1_000_000_000_000,
            ).key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=10.0,
            candidate_best_speedup=9.5,
            baseline_median_speedup=10.5,
            candidate_median_speedup=10.1,
        ),
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        require_each_median_speedup_at_least=1.0,
    )

    assert failures == []


def test_next_comparison_failures_rejects_selected_row_below_required_win_floor() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(
                name="circle_prime_server_next_prime",
                baseline="external_primesieve_generate_next_server",
                start=1_000_000,
            ).key,
            baseline_result=1_000_003,
            candidate_result=1_000_003,
            baseline_candidate_count=2,
            candidate_candidate_count=2,
            baseline_best_speedup=0.9,
            candidate_best_speedup=0.95,
            baseline_median_speedup=0.95,
            candidate_median_speedup=0.98,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        require_each_median_speedup_at_least=1.0,
    )

    assert failures == [
        "circle_prime_server_next_prime start=1000000 batch_size=1 threads=1 "
        "requested_threads=1 baseline=external_primesieve_generate_next_server "
        "median speedup below required floor: 0.980 < 1.000"
    ]


def test_next_comparison_failures_can_require_stable_samples() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(name="circle_prime_server_next_prime").key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=1.2,
            candidate_best_speedup=1.1,
            baseline_median_speedup=1.1,
            candidate_median_speedup=1.0,
            candidate_sample_stability="noisy",
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        require_stable_samples=True,
    )

    assert failures == [
        "circle_prime_server_next_prime start=1000000000000 batch_size=1 "
        "threads=1 requested_threads=1 baseline=external_primesieve_next_prime "
        "sample stability is not stable: noisy"
    ]


def test_next_comparison_failures_can_bypass_noisy_material_win() -> None:
    comparisons = [
        NextComparison(
            key=speedup_row(name="circle_prime_server_next_prime").key,
            baseline_result=1_000_000_000_039,
            candidate_result=1_000_000_000_039,
            baseline_candidate_count=12,
            candidate_candidate_count=12,
            baseline_best_speedup=1.6,
            candidate_best_speedup=1.7,
            baseline_median_speedup=1.6,
            candidate_median_speedup=1.8,
            candidate_sample_stability="noisy",
        )
    ]

    assert not comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.85,
        min_best_speedup_ratio=0.85,
        require_stable_samples=True,
        allow_noisy_when_median_speedup_at_least=1.5,
    )


def test_render_next_comparison_table_marks_result_status() -> None:
    rendered = render_comparison_table(
        [
            NextComparison(
                key=speedup_row().key,
                baseline_result=1_000_000_000_039,
                candidate_result=1_000_000_000_039,
                baseline_candidate_count=12,
                candidate_candidate_count=12,
                baseline_best_speedup=1.2,
                candidate_best_speedup=1.1,
                baseline_median_speedup=1.1,
                candidate_median_speedup=1.0,
            )
        ]
    )

    assert "circle_prime_next_prime,1000000000000,1,1,1,external_primesieve_next_prime" in rendered
    assert ",12,12,1.100,1.000,0.909,1.200,1.100,0.917,,match" in rendered
