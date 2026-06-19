from __future__ import annotations

import json

from scripts.calibrate_prime_engine_defaults import (
    build_calibration,
    read_external_mode_confirmation_input_rows,
    render_markdown,
    select_recommendations,
)


def speedup_row(
    *,
    low: int = 0,
    high: int = 10_000_000,
    baseline: str = "external_primesieve_count",
    name: str | None = None,
    segment_size: int,
    threads: int = 8,
    requested_threads: int = 8,
    best_ms: str,
    median_ms: str,
    best_speedup: str = "0.900",
    median_speedup: str = "0.900",
) -> dict[str, str]:
    return {
        "kind": "speedup",
        "name": name or f"circle_prime_parallel_segmented_count_{threads}t",
        "low": str(low),
        "high": str(high),
        "span": str(high - low),
        "segment_size": str(segment_size),
        "result": "664579",
        "rounds": "5",
        "best_ms": best_ms,
        "median_ms": median_ms,
        "rate_per_second": "0",
        "median_rate_per_second": "0",
        "threads": str(threads),
        "requested_threads": str(requested_threads),
        "baseline": baseline,
        "best_speedup": best_speedup,
        "median_speedup": median_speedup,
    }


def test_select_recommendations_prefers_primesieve_median_row() -> None:
    rows = [
        speedup_row(segment_size=65536, best_ms="3.2", median_ms="3.0"),
        speedup_row(segment_size=196608, best_ms="2.9", median_ms="3.4"),
        speedup_row(
            baseline="external_primecount_pi_diff",
            segment_size=131072,
            best_ms="2.8",
            median_ms="2.9",
        ),
    ]

    selected = select_recommendations(
        external_rows=rows,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count", "external_primecount_pi_diff"],
    )

    assert len(selected) == 1
    assert selected[0]["baseline"] == "external_primesieve_count"
    assert selected[0]["count_mode"] == "segmented"
    assert selected[0]["segment_size"] == 65536
    assert selected[0]["selected_by"] == "median_ms"


def test_build_calibration_marks_default_drift_over_tolerance() -> None:
    selected = select_recommendations(
        external_rows=[
            speedup_row(segment_size=65536, best_ms="3.2", median_ms="3.0"),
            speedup_row(segment_size=196608, best_ms="3.3", median_ms="3.4"),
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )
    current_defaults = {
        (0, 10_000_000, 8): {
            "segment_size": 196608,
            "threads": 8,
            "requested_threads": 8,
        }
    }

    calibration = build_calibration(
        recommendations=selected,
        current_defaults=current_defaults,
        external_metadata=None,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    assert calibration["drift_count"] == 1
    assert calibration["failing_recommendation_count"] == 1
    row = calibration["recommendations"][0]
    assert row["status"] == "drift"
    assert row["default_over_selected"] == 3.4 / 3.0
    assert "Default Calibration" in render_markdown(calibration)


def test_select_recommendations_uses_external_mode_sweep_candidates() -> None:
    selected = select_recommendations(
        external_rows=[
            speedup_row(segment_size=65_536, best_ms="3.0", median_ms="3.2"),
        ],
        external_mode_rows=[
            speedup_row(
                name="circle_prime_parallel_dynamic_count_8t",
                segment_size=65_536,
                best_ms="2.9",
                median_ms="3.0",
            )
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )

    assert len(selected) == 1
    assert selected[0]["source"] == "external_mode_sweep"
    assert selected[0]["count_mode"] == "dynamic"
    assert selected[0]["segment_size"] == 65_536
    assert selected[0]["candidate_count"] == 1


def test_external_mode_sweep_takes_precedence_over_segment_sweep() -> None:
    selected = select_recommendations(
        external_rows=[
            speedup_row(
                name="circle_prime_parallel_segmented_count_8t",
                segment_size=65_536,
                best_ms="2.0",
                median_ms="2.1",
            )
        ],
        external_mode_rows=[
            speedup_row(
                name="circle_prime_parallel_balanced_count_8t",
                segment_size=65_536,
                best_ms="2.5",
                median_ms="2.6",
            )
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )

    assert len(selected) == 1
    assert selected[0]["source"] == "external_mode_sweep"
    assert selected[0]["count_mode"] == "balanced"


def test_high_offset_quick_precedes_mode_and_segment_sweeps() -> None:
    low = 1_000_000_000_000
    high = 1_000_010_000_000

    selected = select_recommendations(
        external_rows=[
            speedup_row(
                low=low,
                high=high,
                name="circle_prime_parallel_segmented_count_8t",
                segment_size=3_145_728,
                best_ms="5.1",
                median_ms="5.2",
            )
        ],
        external_mode_rows=[
            speedup_row(
                low=low,
                high=high,
                name="circle_prime_parallel_balanced_count_8t",
                segment_size=1_441_792,
                best_ms="4.9",
                median_ms="5.0",
            )
        ],
        external_high_offset_rows=[
            speedup_row(
                low=low,
                high=high,
                name="circle_prime_parallel_presieve13_count_8t",
                segment_size=1_310_720,
                best_ms="4.8",
                median_ms="4.9",
            ),
            speedup_row(
                low=low,
                high=high,
                name="circle_prime_parallel_presieve13_count_8t",
                segment_size=1_376_256,
                best_ms="4.7",
                median_ms="4.8",
            ),
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )

    assert len(selected) == 1
    assert selected[0]["source"] == "external_high_offset_quick"
    assert selected[0]["count_mode"] == "presieve13"
    assert selected[0]["segment_size"] == 1_376_256
    assert selected[0]["candidate_count"] == 2


def test_confirmed_external_mode_overrides_latest_median_pick() -> None:
    selected = select_recommendations(
        external_rows=[],
        external_mode_rows=[
            speedup_row(
                name="circle_prime_parallel_dynamic_count_8t",
                segment_size=65_536,
                best_ms="2.5",
                median_ms="2.8",
            ),
            speedup_row(
                name="circle_prime_parallel_segmented_count_8t",
                segment_size=65_536,
                best_ms="2.6",
                median_ms="3.0",
            ),
        ],
        external_mode_confirmation={
            "min_confirmations": 2,
            "require_stable_samples": True,
            "winners": [
                {
                    "low": 0,
                    "high": 10_000_000,
                    "baseline": "external_primesieve_count",
                    "count_mode": "segmented",
                    "segment_size": 65_536,
                    "threads": 8,
                    "requested_threads": 8,
                    "confirmation_count": 2,
                    "observed_count": 3,
                    "stable_observed_count": 3,
                    "status": "confirmed",
                }
            ],
        },
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )

    assert selected[0]["count_mode"] == "segmented"
    assert selected[0]["selected_by"] == "confirmed_external_mode"
    assert selected[0]["mode_confirmation_status"] == "confirmed"


def test_unconfirmed_external_mode_drift_does_not_fail_calibration() -> None:
    selected = select_recommendations(
        external_rows=[],
        external_mode_rows=[
            speedup_row(
                name="circle_prime_parallel_dynamic_count_8t",
                segment_size=65_536,
                best_ms="2.5",
                median_ms="2.8",
            ),
            speedup_row(
                name="circle_prime_parallel_segmented_count_8t",
                segment_size=65_536,
                best_ms="3.0",
                median_ms="3.2",
            ),
        ],
        external_mode_confirmation={
            "min_confirmations": 2,
            "require_stable_samples": True,
            "winners": [
                {
                    "low": 0,
                    "high": 10_000_000,
                    "baseline": "external_primesieve_count",
                    "count_mode": "dynamic",
                    "segment_size": 65_536,
                    "threads": 8,
                    "requested_threads": 8,
                    "confirmation_count": 1,
                    "observed_count": 2,
                    "stable_observed_count": 1,
                    "status": "unconfirmed",
                }
            ],
        },
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )
    current_defaults = {
        (0, 10_000_000, 8): {
            "count_mode": "segmented",
            "segment_size": 65_536,
            "threads": 8,
            "requested_threads": 8,
        }
    }

    calibration = build_calibration(
        recommendations=selected,
        current_defaults=current_defaults,
        external_metadata=None,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    row = calibration["recommendations"][0]
    assert row["status"] == "unconfirmed_mode_drift"
    assert row["passes"] is True
    assert calibration["unconfirmed_mode_drift_count"] == 1
    assert calibration["failing_recommendation_count"] == 0
    assert "mode unconfirmed 1/2" in render_markdown(calibration)


def test_build_calibration_fails_when_default_mode_lacks_evidence() -> None:
    recommendations = [
        {
            "source": "tuning",
            "baseline": None,
            "low": 0,
            "high": 10_000_000,
            "span": 10_000_000,
            "count_mode": "hybrid-wheel30-mark",
            "segment_size": 65_536,
            "threads": 8,
            "requested_threads": 8,
            "best_ms": 2.0,
            "median_ms": 2.1,
            "circle_speedup": None,
            "median_circle_speedup": None,
            "candidate_count": 4,
            "candidates": [],
            "selected_by": "median_ms",
        }
    ]
    current_defaults = {
        (0, 10_000_000, 8): {
            "count_mode": "segmented",
            "segment_size": 65_536,
            "threads": 8,
            "requested_threads": 8,
        }
    }

    calibration = build_calibration(
        recommendations=recommendations,
        current_defaults=current_defaults,
        external_metadata=None,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    row = calibration["recommendations"][0]
    assert row["count_mode_aligned"] is False
    assert row["segment_size_aligned"] is True
    assert row["status"] == "missing_default_evidence"
    assert calibration["failing_recommendation_count"] == 1


def test_build_calibration_reports_noisy_drift_without_failing() -> None:
    selected = select_recommendations(
        external_rows=[
            speedup_row(segment_size=65536, best_ms="3.2", median_ms="3.0"),
            speedup_row(segment_size=196608, best_ms="3.3", median_ms="3.4"),
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )
    selected[0]["sample_stability"] = "noisy"
    current_defaults = {
        (0, 10_000_000, 8): {
            "segment_size": 196608,
            "threads": 8,
            "requested_threads": 8,
        }
    }

    calibration = build_calibration(
        recommendations=selected,
        current_defaults=current_defaults,
        external_metadata=None,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    assert calibration["drift_count"] == 0
    assert calibration["noisy_drift_count"] == 1
    assert calibration["failing_recommendation_count"] == 0
    assert calibration["recommendations"][0]["status"] == "noisy_drift"


def test_build_calibration_summarizes_high_offset_quick_metadata() -> None:
    selected = select_recommendations(
        external_rows=[],
        external_high_offset_rows=[
            speedup_row(
                low=1_000_000_000_000,
                high=1_000_010_000_000,
                name="circle_prime_parallel_presieve13_count_8t",
                segment_size=1_310_720,
                best_ms="5.3",
                median_ms="5.6",
            )
        ],
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )

    calibration = build_calibration(
        recommendations=selected,
        current_defaults={
            (1_000_000_000_000, 1_000_010_000_000, 8): {
                "count_mode": "presieve13",
                "segment_size": 1_310_720,
                "threads": 8,
                "requested_threads": 8,
            }
        },
        external_metadata=None,
        external_high_offset_metadata={
            "rounds": 13,
            "requested_segment_sizes": [1_310_720, 1_376_256],
            "thread_policy": {"circle_threads": 8, "external_threads": 8},
        },
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    assert calibration["external_high_offset_quick"]["available"] is True
    assert calibration["external_high_offset_quick"]["rounds"] == 13
    assert calibration["recommendations"][0]["source"] == "external_high_offset_quick"
    assert calibration["recommendations"][0]["status"] == "aligned"


def test_confirmed_stable_mode_turns_noisy_sample_into_actionable_drift() -> None:
    selected = select_recommendations(
        external_rows=[],
        external_mode_rows=[
            speedup_row(
                name="circle_prime_parallel_dynamic_count_8t",
                segment_size=65_536,
                best_ms="2.5",
                median_ms="2.8",
            ),
            speedup_row(
                name="circle_prime_parallel_segmented_count_8t",
                segment_size=65_536,
                best_ms="3.0",
                median_ms="3.2",
            ),
        ],
        external_mode_confirmation={
            "min_confirmations": 2,
            "require_stable_samples": True,
            "winners": [
                {
                    "low": 0,
                    "high": 10_000_000,
                    "baseline": "external_primesieve_count",
                    "count_mode": "dynamic",
                    "segment_size": 65_536,
                    "threads": 8,
                    "requested_threads": 8,
                    "confirmation_count": 2,
                    "observed_count": 3,
                    "stable_observed_count": 2,
                    "status": "confirmed",
                }
            ],
        },
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
    )
    selected[0]["sample_stability"] = "noisy"
    current_defaults = {
        (0, 10_000_000, 8): {
            "count_mode": "segmented",
            "segment_size": 65_536,
            "threads": 8,
            "requested_threads": 8,
        }
    }

    calibration = build_calibration(
        recommendations=selected,
        current_defaults=current_defaults,
        external_metadata=None,
        tuning_summary=None,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    row = calibration["recommendations"][0]
    assert row["selected_sample_stability"] == "noisy"
    assert row["selected_effective_sample_stability"] == "stable"
    assert row["status"] == "drift"
    assert row["passes"] is False
    assert calibration["drift_count"] == 1
    assert calibration["noisy_drift_count"] == 0


def test_select_recommendations_falls_back_to_tuning_for_missing_external_range() -> None:
    tuning_summary = {
        "best_by_range": [
            {
                "low": 0,
                "high": 1_000_000,
                "span": 1_000_000,
                "samples": 12,
                "best": {
                    "segment_size": 32768,
                    "requested_threads": 4,
                    "threads": 4,
                    "best_ms": 0.08,
                    "median_ms": 0.09,
                },
            }
        ]
    }

    selected = select_recommendations(
        external_rows=[],
        tuning_summary=tuning_summary,
        baseline_priority=["external_primesieve_count"],
    )

    assert selected[0]["source"] == "tuning"
    assert selected[0]["segment_size"] == 32768
    assert selected[0]["requested_threads"] == 4


def test_tuning_fallback_keeps_candidate_evidence_for_default_ratio() -> None:
    tuning_summary = {
        "best_by_range": [
            {
                "low": 0,
                "high": 1_000_000,
                "span": 1_000_000,
                "samples": 2,
                "best": {
                    "count_mode": "dynamic",
                    "segment_size": 262_144,
                    "requested_threads": 2,
                    "threads": 2,
                    "best_ms": 0.067,
                    "median_ms": 0.070,
                },
            }
        ]
    }
    tuning_sample_rows = [
        {
            "kind": "tuning",
            "count_mode": "segmented",
            "low": "0",
            "high": "1000000",
            "span": "1000000",
            "segment_size": "65536",
            "requested_threads": "2",
            "threads": "2",
            "best_ms": "0.073",
            "median_ms": "0.078",
        },
        {
            "kind": "tuning",
            "count_mode": "dynamic",
            "low": "0",
            "high": "1000000",
            "span": "1000000",
            "segment_size": "262144",
            "requested_threads": "2",
            "threads": "2",
            "best_ms": "0.067",
            "median_ms": "0.070",
        },
    ]

    selected = select_recommendations(
        external_rows=[],
        tuning_summary=tuning_summary,
        tuning_sample_rows=tuning_sample_rows,
        baseline_priority=["external_primesieve_count"],
    )
    calibration = build_calibration(
        recommendations=selected,
        current_defaults={
            (0, 1_000_000, 2): {
                "count_mode": "segmented",
                "segment_size": 65_536,
                "threads": 2,
                "requested_threads": 2,
            }
        },
        external_metadata=None,
        tuning_summary=tuning_summary,
        baseline_priority=["external_primesieve_count"],
        tolerance=0.05,
        generated_at_utc="2026-01-01T00:00:00Z",
        inputs={},
    )

    row = calibration["recommendations"][0]
    assert selected[0]["candidate_count"] == 2
    assert row["status"] == "drift"
    assert row["default_over_selected"] == 0.078 / 0.070
    assert calibration["missing_evidence_count"] == 0


def test_confirmation_input_rows_load_csv_and_samples(tmp_path) -> None:
    csv_path = tmp_path / "confirm.csv"
    sample_path = tmp_path / "confirm_samples.csv"
    metadata_path = tmp_path / "confirm.json"
    csv_path.write_text(
        "kind,name,low,high,span,segment_size,result,rounds,best_ms,median_ms,"
        "rate_per_second,median_rate_per_second,threads,requested_threads,"
        "baseline,best_speedup,median_speedup,count_mode\n"
        "speedup,circle_prime_parallel_dynamic_count_8t,0,10000000,10000000,"
        "98304,664579,5,2.9,3.0,0,0,8,8,external_primesieve_count,"
        "0.9,0.9,dynamic\n"
    )
    sample_path.write_text(
        "kind,name,low,high,span,segment_size,result,round_index,elapsed_ms,"
        "threads,requested_threads,count_mode\n"
        "sample,circle_prime_parallel_dynamic_count_8t,0,10000000,10000000,"
        "98304,664579,0,3.0,8,8,dynamic\n"
    )
    metadata_path.write_text(json.dumps({"sample_output": str(sample_path)}) + "\n")

    rows, samples = read_external_mode_confirmation_input_rows(
        {"inputs": [str(csv_path)]}
    )

    assert rows[0]["count_mode"] == "dynamic"
    assert rows[0]["segment_size"] == "98304"
    assert samples[0]["elapsed_ms"] == "3.0"
