from __future__ import annotations

from scripts.compare_prime_engine_benchmarks import (
    Comparison,
    TimingRow,
    compare_timing_rows,
    comparison_failures,
    render_comparison_table,
)


def test_compare_timing_rows_matches_candidate_subset() -> None:
    baseline = {
        ("scalar_u64_batch", 200000, 0): TimingRow(
            "scalar_u64_batch", 200000, 0, 9135, 160.0
        ),
        ("parallel_segmented_range_count_8t", 10000000, 131072): TimingRow(
            "parallel_segmented_range_count_8t", 10000000, 131072, 664579, 0.320
        ),
    }
    candidate = {
        ("scalar_u64_batch", 200000, 0): TimingRow(
            "scalar_u64_batch", 200000, 0, 9135, 158.0
        )
    }

    comparisons = compare_timing_rows(
        baseline_rows=baseline,
        candidate_rows=candidate,
        names={"scalar_u64_batch"},
    )

    assert len(comparisons) == 1
    assert comparisons[0].ratio == 158.0 / 160.0
    assert not comparison_failures(comparisons, max_regression_ratio=1.05)


def test_compare_timing_rows_requires_selected_baseline_coverage() -> None:
    baseline = {
        ("parallel_segmented_range_count_8t", 10000000, 131072): TimingRow(
            "parallel_segmented_range_count_8t", 10000000, 131072, 664579, 0.320
        ),
        ("parallel_segmented_range_count_8t", 100000000, 196608): TimingRow(
            "parallel_segmented_range_count_8t", 100000000, 196608, 5761455, 2.900
        ),
    }
    candidate = {
        ("parallel_segmented_range_count_8t", 10000000, 131072): TimingRow(
            "parallel_segmented_range_count_8t", 10000000, 131072, 664579, 0.310
        )
    }

    try:
        compare_timing_rows(
            baseline_rows=baseline,
            candidate_rows=candidate,
            names={"parallel_segmented_range_count_8t"},
        )
    except ValueError as exc:
        assert "candidate CSV is missing selected baseline row(s)" in str(exc)
        assert "workload=100000000" in str(exc)
    else:
        raise AssertionError("expected missing selected baseline row to fail")


def test_compare_timing_rows_can_allow_candidate_subset() -> None:
    baseline = {
        ("parallel_segmented_range_count_8t", 10000000, 131072): TimingRow(
            "parallel_segmented_range_count_8t", 10000000, 131072, 664579, 0.320
        ),
        ("parallel_segmented_range_count_8t", 100000000, 196608): TimingRow(
            "parallel_segmented_range_count_8t", 100000000, 196608, 5761455, 2.900
        ),
    }
    candidate = {
        ("parallel_segmented_range_count_8t", 10000000, 131072): TimingRow(
            "parallel_segmented_range_count_8t", 10000000, 131072, 664579, 0.310
        )
    }

    comparisons = compare_timing_rows(
        baseline_rows=baseline,
        candidate_rows=candidate,
        names={"parallel_segmented_range_count_8t"},
        require_baseline_coverage=False,
    )

    assert len(comparisons) == 1
    assert comparisons[0].key == ("parallel_segmented_range_count_8t", 10000000, 131072)


def test_comparison_failures_detects_regression_and_result_mismatch() -> None:
    comparisons = [
        Comparison(
            key=("scalar_u64_batch", 200000, 0),
            baseline_result=9135,
            candidate_result=9135,
            baseline_best_ms=160.0,
            candidate_best_ms=180.0,
        ),
        Comparison(
            key=("parallel_segmented_range_count_8t", 10000000, 131072),
            baseline_result=664579,
            candidate_result=664580,
            baseline_best_ms=0.320,
            candidate_best_ms=0.310,
        ),
    ]

    failures = comparison_failures(comparisons, max_regression_ratio=1.05)

    assert any("regressed" in failure for failure in failures)
    assert any("result changed" in failure for failure in failures)


def test_comparison_failures_can_require_improvement() -> None:
    comparisons = [
        Comparison(
            key=("scalar_u64_batch", 200000, 0),
            baseline_result=9135,
            candidate_result=9135,
            baseline_best_ms=160.0,
            candidate_best_ms=160.0,
        )
    ]

    failures = comparison_failures(
        comparisons,
        max_regression_ratio=1.05,
        require_improvement_ratio=0.99,
    )

    assert failures == ["no compared row met required improvement ratio 0.990"]


def test_comparison_failures_reports_zero_baseline_without_crashing() -> None:
    comparisons = [
        Comparison(
            key=("base_prime_generation", 10000, 0),
            baseline_result=1229,
            candidate_result=1229,
            baseline_best_ms=0.0,
            candidate_best_ms=0.0,
        )
    ]

    failures = comparison_failures(comparisons, max_regression_ratio=1.05)
    rendered = render_comparison_table(comparisons)

    assert comparisons[0].ratio is None
    assert any("cannot compare timing ratio" in failure for failure in failures)
    assert "base_prime_generation,10000,0,0.000,0.000,n/a,match" in rendered


def test_render_comparison_table_marks_result_status() -> None:
    rendered = render_comparison_table(
        [
            Comparison(
                key=("scalar_u64_batch", 200000, 0),
                baseline_result=9135,
                candidate_result=9135,
                baseline_best_ms=160.0,
                candidate_best_ms=158.0,
            )
        ]
    )

    assert "scalar_u64_batch,200000,0,160.000,158.000,0.988,match" in rendered
