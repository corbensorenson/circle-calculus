from __future__ import annotations

from scripts.compare_prime_external_controls import (
    ExternalComparison,
    ExternalSpeedupRow,
    compare_speedup_rows,
    comparison_failures,
    render_comparison_table,
)


def speedup_row(
    *,
    name: str = "circle_prime_parallel_default_count_8t",
    low: int = 0,
    high: int = 10_000_000,
    segment_size: int = 65_536,
    result: int = 664_579,
    threads: int = 8,
    requested_threads: int = 8,
    baseline: str = "external_primesieve_count",
    best_speedup: float = 0.900,
    median_speedup: float = 0.950,
    count_mode: str = "segmented",
    sample_stability: str = "stable",
) -> ExternalSpeedupRow:
    return ExternalSpeedupRow(
        name=name,
        low=low,
        high=high,
        segment_size=segment_size,
        result=result,
        threads=threads,
        requested_threads=requested_threads,
        baseline=baseline,
        best_speedup=best_speedup,
        median_speedup=median_speedup,
        count_mode=count_mode,
        sample_stability=sample_stability,
    )


def test_compare_speedup_rows_matches_candidate_subset() -> None:
    baseline_row = speedup_row(best_speedup=0.900, median_speedup=0.950)
    candidate_row = speedup_row(best_speedup=0.930, median_speedup=0.970)
    ignored_row = speedup_row(
        baseline="external_primecount_pi_diff",
        best_speedup=1.200,
        median_speedup=1.300,
    )

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row, ignored_row.key: ignored_row},
        candidate_rows={candidate_row.key: candidate_row},
        baselines={"external_primesieve_count"},
    )

    assert len(comparisons) == 1
    assert comparisons[0].median_speedup_ratio == 0.970 / 0.950
    assert comparisons[0].baseline_count_mode == "segmented"
    assert comparisons[0].candidate_count_mode == "segmented"
    assert comparisons[0].candidate_sample_stability == "stable"
    assert not comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
    )


def test_compare_speedup_rows_requires_selected_baseline_coverage() -> None:
    first = speedup_row(high=10_000_000, segment_size=65_536)
    second = speedup_row(high=100_000_000, segment_size=196_608, result=5_761_455)
    candidate = speedup_row(high=10_000_000, segment_size=65_536, best_speedup=0.920)

    try:
        compare_speedup_rows(
            baseline_rows={first.key: first, second.key: second},
            candidate_rows={candidate.key: candidate},
            baselines={"external_primesieve_count"},
        )
    except ValueError as exc:
        assert "candidate CSV is missing selected baseline speedup row(s)" in str(exc)
        assert "range=[0,100000000)" in str(exc)
    else:
        raise AssertionError("expected missing selected baseline speedup row to fail")


def test_compare_speedup_rows_can_allow_candidate_subset() -> None:
    first = speedup_row(high=10_000_000, segment_size=65_536)
    second = speedup_row(high=100_000_000, segment_size=196_608, result=5_761_455)
    candidate = speedup_row(high=10_000_000, segment_size=65_536, best_speedup=0.920)

    comparisons = compare_speedup_rows(
        baseline_rows={first.key: first, second.key: second},
        candidate_rows={candidate.key: candidate},
        baselines={"external_primesieve_count"},
        require_baseline_coverage=False,
    )

    assert len(comparisons) == 1
    assert comparisons[0].key == first.key


def test_compare_speedup_rows_can_filter_by_range() -> None:
    baseline_primary = speedup_row(
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        name="circle_prime_server_parallel_default_count_8t",
        baseline="external_primesieve_count_server",
        best_speedup=1.200,
        median_speedup=1.100,
    )
    candidate_primary = speedup_row(
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        name="circle_prime_server_parallel_default_count_8t",
        baseline="external_primesieve_count_server",
        best_speedup=1.250,
        median_speedup=1.150,
    )
    ignored_baseline = speedup_row(
        low=1_500_000_000_000,
        high=1_500_010_000_000,
        name="circle_prime_server_parallel_default_count_8t",
        baseline="external_primesieve_count_server",
        best_speedup=1.010,
        median_speedup=0.990,
    )

    comparisons = compare_speedup_rows(
        baseline_rows={
            baseline_primary.key: baseline_primary,
            ignored_baseline.key: ignored_baseline,
        },
        candidate_rows={candidate_primary.key: candidate_primary},
        names={"circle_prime_server_default_count"},
        baselines={"external_primesieve_count_server"},
        ranges={(1_000_000_000_000, 1_000_010_000_000)},
    )

    assert len(comparisons) == 1
    assert comparisons[0].key[1:3] == (1_000_000_000_000, 1_000_010_000_000)


def test_comparison_failures_detects_regressions_and_result_mismatch() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_580,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.700,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.800,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
    )

    assert any("result changed" in failure for failure in failures)
    assert any("median speedup regressed" in failure for failure in failures)
    assert any("best speedup regressed" in failure for failure in failures)


def test_noisy_baseline_median_regression_can_be_allowed_at_parity_floor() -> None:
    row = ExternalComparison(
        key=speedup_row().key,
        baseline_result=664_579,
        candidate_result=664_579,
        baseline_best_speedup=1.400,
        candidate_best_speedup=1.300,
        baseline_median_speedup=1.300,
        candidate_median_speedup=1.010,
        baseline_sample_stability="noisy",
        candidate_sample_stability="stable",
    )

    assert not comparison_failures(
        [row],
        min_median_speedup_ratio=0.90,
        min_best_speedup_ratio=0.85,
        allow_noisy_baseline_median_regression_when_candidate_speedup_at_least=1.0,
    )


def test_noisy_baseline_median_regression_bypass_requires_stable_candidate() -> None:
    row = ExternalComparison(
        key=speedup_row().key,
        baseline_result=664_579,
        candidate_result=664_579,
        baseline_best_speedup=1.400,
        candidate_best_speedup=1.300,
        baseline_median_speedup=1.300,
        candidate_median_speedup=1.010,
        baseline_sample_stability="noisy",
        candidate_sample_stability="noisy",
    )

    failures = comparison_failures(
        [row],
        min_median_speedup_ratio=0.90,
        min_best_speedup_ratio=0.85,
        allow_noisy_baseline_median_regression_when_candidate_speedup_at_least=1.0,
    )

    assert any("median speedup regressed" in failure for failure in failures)


def test_count_mode_change_is_reported_without_default_failure() -> None:
    baseline_row = speedup_row(count_mode="segmented")
    candidate_row = speedup_row(
        best_speedup=0.930,
        median_speedup=0.970,
        count_mode="balanced",
    )

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row},
        candidate_rows={candidate_row.key: candidate_row},
        baselines={"external_primesieve_count"},
    )

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
    )
    rendered = render_comparison_table(comparisons)

    assert failures == []
    assert comparisons[0].baseline_count_mode == "segmented"
    assert comparisons[0].candidate_count_mode == "balanced"
    assert ",segmented,balanced,yes," in rendered


def test_adaptive_default_rows_compare_across_effective_thread_changes() -> None:
    baseline_row = speedup_row(
        name="circle_prime_parallel_default_count_8t",
        threads=8,
        requested_threads=8,
        count_mode="dynamic",
    )
    candidate_row = speedup_row(
        name="circle_prime_default_count",
        threads=1,
        requested_threads=8,
        count_mode="prefix-pi",
        best_speedup=1.200,
        median_speedup=1.300,
    )

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row},
        candidate_rows={candidate_row.key: candidate_row},
        baselines={"external_primesieve_count"},
    )

    assert len(comparisons) == 1
    assert comparisons[0].key == (
        "circle_prime_default_count",
        0,
        10_000_000,
        0,
        8,
        8,
        "external_primesieve_count",
    )
    assert comparisons[0].baseline_count_mode == "dynamic"
    assert comparisons[0].candidate_count_mode == "prefix-pi"
    assert comparisons[0].median_speedup_ratio == 1.300 / 0.950


def test_name_filter_matches_adaptive_default_comparison_name() -> None:
    baseline_row = speedup_row(
        name="circle_prime_default_count",
        threads=1,
        requested_threads=8,
        count_mode="prefix-pi",
    )
    candidate_row = speedup_row(
        name="circle_prime_parallel_default_count_2t",
        threads=2,
        requested_threads=8,
        best_speedup=1.100,
        median_speedup=1.200,
        count_mode="prefix-pi",
    )

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row},
        candidate_rows={candidate_row.key: candidate_row},
        names={"circle_prime_default_count"},
        baselines={"external_primesieve_count"},
    )

    assert len(comparisons) == 1
    assert comparisons[0].key == (
        "circle_prime_default_count",
        0,
        10_000_000,
        0,
        8,
        8,
        "external_primesieve_count",
    )
    assert comparisons[0].candidate_median_speedup == 1.200


def test_count_binary_default_keeps_separate_comparison_key() -> None:
    full_cli = speedup_row(
        name="circle_prime_parallel_default_count_8t",
        segment_size=1_310_720,
        best_speedup=0.900,
        median_speedup=0.910,
        count_mode="presieve13",
    )
    count_binary = speedup_row(
        name="circle_prime_count_binary_parallel_default_count_8t",
        segment_size=1_310_720,
        best_speedup=0.930,
        median_speedup=0.940,
        count_mode="presieve13",
    )

    rows = {full_cli.key: full_cli, count_binary.key: count_binary}

    assert len(rows) == 2
    comparisons = compare_speedup_rows(
        baseline_rows=rows,
        candidate_rows=rows,
        names={"circle_prime_count_binary_default_count"},
        baselines={"external_primesieve_count"},
    )

    assert len(comparisons) == 1
    assert comparisons[0].key[0] == "circle_prime_count_binary_default_count"
    assert comparisons[0].candidate_median_speedup == 0.940


def test_count_binary_server_default_keeps_separate_comparison_key() -> None:
    count_binary = speedup_row(
        name="circle_prime_count_binary_parallel_default_count_8t",
        segment_size=1_310_720,
        best_speedup=0.930,
        median_speedup=0.940,
        count_mode="presieve13",
    )
    count_binary_server = speedup_row(
        name="circle_prime_count_binary_server_parallel_default_count_8t",
        segment_size=1_310_720,
        best_speedup=3.100,
        median_speedup=3.200,
        count_mode="presieve13",
    )

    rows = {count_binary.key: count_binary, count_binary_server.key: count_binary_server}

    assert len(rows) == 2
    count_binary_comparisons = compare_speedup_rows(
        baseline_rows=rows,
        candidate_rows=rows,
        names={"circle_prime_count_binary_default_count"},
        baselines={"external_primesieve_count"},
    )
    server_comparisons = compare_speedup_rows(
        baseline_rows=rows,
        candidate_rows=rows,
        names={"circle_prime_count_binary_server_parallel_default_count_8t"},
        baselines={"external_primesieve_count"},
    )

    assert len(count_binary_comparisons) == 1
    assert count_binary_comparisons[0].key[0] == "circle_prime_count_binary_default_count"
    assert count_binary_comparisons[0].candidate_median_speedup == 0.940
    assert len(server_comparisons) == 1
    assert server_comparisons[0].key[0] == "circle_prime_count_binary_server_default_count"
    assert server_comparisons[0].candidate_median_speedup == 3.200


def test_adaptive_server_default_rows_keep_separate_comparison_key() -> None:
    cold_baseline = speedup_row(
        name="circle_prime_parallel_default_count_7t",
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        segment_size=1_507_328,
        result=361_726,
        threads=7,
        requested_threads=8,
        best_speedup=0.980,
        median_speedup=1.010,
        count_mode="presieve17",
    )
    server_baseline = speedup_row(
        name="circle_prime_server_parallel_default_count_7t",
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        segment_size=1_507_328,
        result=361_726,
        threads=7,
        requested_threads=8,
        best_speedup=2.400,
        median_speedup=2.500,
        count_mode="presieve17",
    )
    cold_candidate = speedup_row(
        name="circle_prime_parallel_default_count_4t",
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        segment_size=3_145_728,
        result=361_726,
        threads=4,
        requested_threads=8,
        best_speedup=1.020,
        median_speedup=1.030,
        count_mode="presieve13",
    )
    server_candidate = speedup_row(
        name="circle_prime_server_parallel_default_count_4t",
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        segment_size=3_145_728,
        result=361_726,
        threads=4,
        requested_threads=8,
        best_speedup=2.700,
        median_speedup=2.800,
        count_mode="presieve13",
    )

    comparisons = compare_speedup_rows(
        baseline_rows={
            cold_baseline.key: cold_baseline,
            server_baseline.key: server_baseline,
        },
        candidate_rows={
            cold_candidate.key: cold_candidate,
            server_candidate.key: server_candidate,
        },
        baselines={"external_primesieve_count"},
    )

    assert [comparison.key[0] for comparison in comparisons] == [
        "circle_prime_default_count",
        "circle_prime_server_default_count",
    ]
    assert comparisons[0].baseline_median_speedup == 1.010
    assert comparisons[1].baseline_median_speedup == 2.500
    assert comparisons[1].candidate_median_speedup == 2.800


def test_count_mode_change_can_be_a_strict_failure() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.930,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.970,
            baseline_count_mode="segmented",
            candidate_count_mode="balanced",
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        fail_on_count_mode_change=True,
    )

    assert failures == [
        "circle_prime_default_count range=[0,10000000) "
        "segment=0 threads=8 requested_threads=8 "
        "baseline=external_primesieve_count count_mode changed: "
        "baseline=segmented, candidate=balanced"
    ]


def test_default_segment_size_change_is_reported_without_default_failure() -> None:
    baseline_row = speedup_row(segment_size=196_608)
    candidate_row = speedup_row(
        segment_size=131_072,
        best_speedup=0.930,
        median_speedup=0.970,
    )

    comparisons = compare_speedup_rows(
        baseline_rows={baseline_row.key: baseline_row},
        candidate_rows={candidate_row.key: candidate_row},
        baselines={"external_primesieve_count"},
    )

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
    )
    rendered = render_comparison_table(comparisons)

    assert failures == []
    assert comparisons[0].key[3] == 0
    assert comparisons[0].baseline_segment_size == 196_608
    assert comparisons[0].candidate_segment_size == 131_072
    assert ",0,196608,131072,yes," in rendered


def test_default_segment_size_change_can_be_a_strict_failure() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.930,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.970,
            baseline_segment_size=196_608,
            candidate_segment_size=131_072,
            baseline_count_mode="segmented",
            candidate_count_mode="segmented",
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        fail_on_segment_size_change=True,
    )

    assert failures == [
        "circle_prime_default_count range=[0,10000000) "
        "segment=0 threads=8 requested_threads=8 "
        "baseline=external_primesieve_count segment_size changed: "
        "baseline=196608, candidate=131072"
    ]


def test_explicit_segment_rows_still_compare_by_segment_size() -> None:
    baseline_row = speedup_row(
        name="circle_prime_parallel_segmented_count_8t",
        segment_size=196_608,
    )
    candidate_row = speedup_row(
        name="circle_prime_parallel_segmented_count_8t",
        segment_size=131_072,
        best_speedup=0.930,
        median_speedup=0.970,
    )

    try:
        compare_speedup_rows(
            baseline_rows={baseline_row.key: baseline_row},
            candidate_rows={candidate_row.key: candidate_row},
            baselines={"external_primesieve_count"},
        )
    except ValueError as exc:
        assert "candidate CSV is missing selected baseline speedup row(s)" in str(exc)
        assert "segment_size=196608" in str(exc)
    else:
        raise AssertionError("expected explicit segment change to miss baseline row")


def test_comparison_failures_can_require_a_serious_control_win() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.910,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.990,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        require_any_median_speedup_at_least=1.0,
    )

    assert failures == ["no compared row met required candidate median speedup 1.000"]


def test_comparison_failures_can_require_each_selected_row_to_win() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.910,
            baseline_median_speedup=0.950,
            candidate_median_speedup=1.010,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        require_each_median_speedup_at_least=1.0,
    )

    assert failures == []


def test_comparison_failures_rejects_selected_row_below_required_win_floor() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.910,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.990,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        require_each_median_speedup_at_least=1.0,
    )

    assert failures == [
        "circle_prime_default_count range=[0,10000000) segment=0 "
        "threads=8 requested_threads=8 baseline=external_primesieve_count "
        "median speedup below required floor: 0.990 < 1.000"
    ]


def test_comparison_failures_can_require_stable_samples() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.910,
            baseline_median_speedup=0.950,
            candidate_median_speedup=1.010,
            candidate_sample_stability="noisy",
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
        require_stable_samples=True,
    )

    assert failures == [
        "circle_prime_default_count range=[0,10000000) segment=0 "
        "threads=8 requested_threads=8 baseline=external_primesieve_count "
        "sample stability is not stable: noisy"
    ]


def test_noisy_samples_can_be_allowed_for_material_median_win() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=1.0,
            candidate_best_speedup=2.0,
            baseline_median_speedup=1.0,
            candidate_median_speedup=2.0,
            candidate_sample_stability="noisy",
        )
    ]

    assert (
        comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.95,
            min_best_speedup_ratio=0.90,
            require_stable_samples=True,
            allow_noisy_when_median_speedup_at_least=1.5,
        )
        == []
    )
    assert any(
        "sample stability is not stable" in failure
        for failure in comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.95,
            min_best_speedup_ratio=0.90,
            require_stable_samples=True,
            allow_noisy_when_median_speedup_at_least=2.5,
        )
    )


def test_best_speedup_regression_can_be_allowed_for_material_median_win() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=100.0,
            candidate_best_speedup=80.0,
            baseline_median_speedup=10.0,
            candidate_median_speedup=12.0,
        )
    ]

    assert (
        comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.90,
            min_best_speedup_ratio=0.85,
            allow_best_regression_when_median_speedup_at_least=5.0,
        )
        == []
    )
    assert any(
        "best speedup regressed" in failure
        for failure in comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.90,
            min_best_speedup_ratio=0.85,
            allow_best_regression_when_median_speedup_at_least=15.0,
        )
    )


def test_median_speedup_regression_can_be_allowed_for_material_median_win() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=100.0,
            candidate_best_speedup=80.0,
            baseline_median_speedup=10.0,
            candidate_median_speedup=8.0,
        )
    ]

    assert (
        comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.90,
            min_best_speedup_ratio=0.0,
            allow_median_regression_when_median_speedup_at_least=5.0,
        )
        == []
    )
    assert any(
        "median speedup regressed" in failure
        for failure in comparison_failures(
            comparisons,
            min_median_speedup_ratio=0.90,
            min_best_speedup_ratio=0.0,
            allow_median_regression_when_median_speedup_at_least=9.0,
        )
    )


def test_median_regression_can_be_tolerated_when_best_speedup_stays_close() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.870,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.820,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.90,
        min_best_speedup_ratio=0.85,
        median_regression_best_speedup_ratio_floor=0.95,
    )

    assert failures == []


def test_median_regression_still_fails_when_best_speedup_also_drifts() -> None:
    comparisons = [
        ExternalComparison(
            key=speedup_row().key,
            baseline_result=664_579,
            candidate_result=664_579,
            baseline_best_speedup=0.900,
            candidate_best_speedup=0.820,
            baseline_median_speedup=0.950,
            candidate_median_speedup=0.820,
        )
    ]

    failures = comparison_failures(
        comparisons,
        min_median_speedup_ratio=0.90,
        min_best_speedup_ratio=0.85,
        median_regression_best_speedup_ratio_floor=0.95,
    )

    assert any("median speedup regressed" in failure for failure in failures)


def test_zero_baseline_speedup_reports_na_without_crashing() -> None:
    comparison = ExternalComparison(
        key=speedup_row().key,
        baseline_result=664_579,
        candidate_result=664_579,
        baseline_best_speedup=0.0,
        candidate_best_speedup=0.1,
        baseline_median_speedup=0.0,
        candidate_median_speedup=0.1,
    )

    failures = comparison_failures(
        [comparison],
        min_median_speedup_ratio=0.95,
        min_best_speedup_ratio=0.90,
    )
    rendered = render_comparison_table([comparison])

    assert comparison.best_speedup_ratio is None
    assert comparison.median_speedup_ratio is None
    assert any("cannot compare median speedup ratio" in failure for failure in failures)
    assert any("cannot compare best speedup ratio" in failure for failure in failures)
    assert (
        ",0,0,0,no,8,8,external_primesieve_count,unknown,unknown,no,"
        "unknown,unknown,0.000,0.100,n/a,0.000,0.100,n/a,match"
    ) in rendered
