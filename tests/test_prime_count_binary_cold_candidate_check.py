from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.check_prime_count_binary_cold_candidate_readout import (
    ColdCountBinaryRow,
    apply_confirmation_holds,
    check_cold_count_binary_candidates,
    cold_count_binary_candidate_rows,
    main,
)


def test_cold_candidate_check_passes_when_gain_is_too_small() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.999),
        cold_row(
            "circle_prime_count_binary_parallel_presieve17_count_8t",
            1.011,
            mode="presieve17",
        ),
    ]

    result = check_cold_count_binary_candidates(rows, min_gain=1.03)

    assert result["ok"] is True
    assert result["trial_rows"] == []
    assert "best gain 1.012x" in result["message"]


def test_cold_candidate_check_fails_for_material_stable_candidate() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 1.00),
        cold_row(
            "circle_prime_count_binary_parallel_presieve17_count_8t",
            1.08,
            mode="presieve17",
        ),
    ]

    result = check_cold_count_binary_candidates(rows, min_gain=1.03)

    assert result["ok"] is False
    assert len(result["trial_rows"]) == 1
    assert result["trial_rows"][0]["best"]["count_mode"] == "presieve17"


def test_cold_candidate_check_ignores_noisy_candidates_by_default() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 1.00),
        cold_row(
            "circle_prime_count_binary_parallel_presieve17_count_8t",
            1.10,
            mode="presieve17",
            stability="noisy",
        ),
    ]

    result = check_cold_count_binary_candidates(rows, min_gain=1.03)

    assert result["ok"] is True
    assert result["trial_rows"] == []


def test_cold_candidate_check_passes_when_all_comparable_rows_are_noisy() -> None:
    rows = [
        cold_row(
            "circle_prime_count_binary_parallel_default_count_8t",
            1.00,
            stability="noisy",
        ),
        cold_row(
            "circle_prime_count_binary_parallel_presieve17_count_8t",
            1.10,
            mode="presieve17",
            stability="noisy",
        ),
    ]

    result = check_cold_count_binary_candidates(rows, min_gain=1.03)

    assert result["ok"] is True
    assert result["trial_rows"] == []
    assert "no comparable stable row groups" in result["message"]
    assert "noisy fallback best gain 1.100x" in result["message"]
    assert "best action trial_cold_count_binary_candidate" in result["message"]


def test_cold_candidate_check_still_fails_when_no_cold_rows_exist() -> None:
    result = check_cold_count_binary_candidates([], min_gain=1.03)

    assert result["ok"] is False
    assert "no comparable cold count-binary default/candidate rows" in result["message"]


def test_cold_candidate_rows_require_candidate_to_beat_primesieve() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.80),
        cold_row(
            "circle_prime_count_binary_parallel_presieve17_count_8t",
            0.90,
            mode="presieve17",
        ),
    ]

    summaries = cold_count_binary_candidate_rows(
        rows,
        min_gain=1.03,
        min_candidate_median_speedup=1.0,
        min_candidate_best_speedup=1.0,
        require_stable_samples=True,
    )

    assert summaries[0]["action"] == "hold_small_gain_candidate"
    assert summaries[0]["median_gain_over_default"] > 1.03


def test_cold_candidate_rows_require_candidate_best_to_beat_primesieve() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.92),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_6t",
            1.02,
            best_speedup=0.98,
            mode="presieve13",
            segment_size=1_835_008,
            threads=6,
            requested_threads=6,
        ),
    ]

    summaries = cold_count_binary_candidate_rows(
        rows,
        min_gain=1.03,
        min_candidate_median_speedup=1.0,
        min_candidate_best_speedup=1.0,
        require_stable_samples=True,
    )

    assert summaries[0]["action"] == "hold_best_speedup_below_floor"
    assert summaries[0]["best"]["circle_threads"] == 6


def test_cold_candidate_check_compares_reduced_thread_candidates_to_default() -> None:
    rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.92),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_6t",
            1.02,
            best_speedup=1.01,
            mode="presieve13",
            segment_size=1_835_008,
            threads=6,
            requested_threads=6,
        ),
    ]

    result = check_cold_count_binary_candidates(rows, min_gain=1.03)

    assert result["ok"] is False
    assert result["trial_rows"][0]["best"]["circle_threads"] == 6
    assert result["trial_rows"][0]["median_gain_over_default"] == pytest.approx(
        1.02 / 0.92
    )


def test_confirmation_holds_trial_ready_sweep_candidate() -> None:
    sweep_rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.96),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_7t",
            1.05,
            best_speedup=1.04,
            segment_size=1_507_328,
            threads=7,
            requested_threads=8,
        ),
    ]
    confirmation_rows = [
        cold_row(
            "circle_prime_count_binary_parallel_default_count_8t",
            0.87,
            stability="noisy",
        ),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_7t",
            0.95,
            best_speedup=0.85,
            segment_size=1_507_328,
            threads=7,
            requested_threads=8,
            stability="noisy",
        ),
    ]
    sweep_result = check_cold_count_binary_candidates(sweep_rows, min_gain=1.03)

    result = apply_confirmation_holds(
        sweep_result,
        confirmation_rows,
        min_gain=1.03,
        min_candidate_median_speedup=1.0,
        min_candidate_best_speedup=1.0,
    )

    assert result["ok"] is True
    assert result["trial_rows"] == []
    assert "held by focused confirmation" in result["message"]
    assert "presieve13:1507328:7" in result["message"]


def test_confirmation_keeps_failing_when_candidate_confirms() -> None:
    sweep_rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.96),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_7t",
            1.05,
            best_speedup=1.04,
            segment_size=1_507_328,
            threads=7,
            requested_threads=8,
        ),
    ]
    confirmation_rows = [
        cold_row("circle_prime_count_binary_parallel_default_count_8t", 0.97),
        cold_row(
            "circle_prime_count_binary_parallel_presieve13_count_7t",
            1.06,
            best_speedup=1.03,
            segment_size=1_507_328,
            threads=7,
            requested_threads=8,
        ),
    ]
    sweep_result = check_cold_count_binary_candidates(sweep_rows, min_gain=1.03)

    result = apply_confirmation_holds(
        sweep_result,
        confirmation_rows,
        min_gain=1.03,
        min_candidate_median_speedup=1.0,
        min_candidate_best_speedup=1.0,
    )

    assert result["ok"] is False
    assert len(result["trial_rows"]) == 1
    assert "after focused confirmation" in result["message"]


def test_main_reports_trial_ready_cold_candidate(
    tmp_path: Path, capsys
) -> None:
    csv_path = tmp_path / "sweep.csv"
    write_sweep_csv(
        csv_path,
        [
            cold_csv_row("circle_prime_count_binary_parallel_default_count_8t", 1.00),
            cold_csv_row(
                "circle_prime_count_binary_parallel_presieve17_count_8t",
                1.08,
                mode="presieve17",
            ),
        ],
    )

    status = main_with_args(csv_path)

    captured = capsys.readouterr()
    assert status == 1
    assert "[1000000000000, 1000010000000)" in captured.err
    assert "candidate=presieve17:1310720:8" in captured.err


def test_main_passes_when_no_trial_ready_cold_candidate(
    tmp_path: Path, capsys
) -> None:
    csv_path = tmp_path / "sweep.csv"
    write_sweep_csv(
        csv_path,
        [
            cold_csv_row("circle_prime_count_binary_parallel_default_count_8t", 1.00),
            cold_csv_row(
                "circle_prime_count_binary_parallel_presieve17_count_8t",
                1.01,
                mode="presieve17",
            ),
        ],
    )

    status = main_with_args(csv_path)

    captured = capsys.readouterr()
    assert status == 0
    assert "OK: no trial-ready" in captured.out


def cold_row(
    name: str,
    median_speedup: float,
    *,
    best_speedup: float | None = None,
    mode: str = "presieve13",
    segment_size: int = 1_310_720,
    threads: int = 8,
    requested_threads: int = 8,
    stability: str = "stable",
) -> ColdCountBinaryRow:
    return ColdCountBinaryRow(
        name=name,
        low=1_000_000_000_000,
        high=1_000_010_000_000,
        baseline="external_primesieve_count",
        median_speedup=median_speedup,
        best_speedup=median_speedup if best_speedup is None else best_speedup,
        count_mode=mode,
        segment_size=segment_size,
        threads=threads,
        requested_threads=requested_threads,
        sample_stability=stability,
    )


def cold_csv_row(
    name: str,
    median_speedup: float,
    *,
    mode: str = "presieve13",
    stability: str = "stable",
) -> dict[str, str]:
    return {
        "kind": "speedup",
        "name": name,
        "low": "1000000000000",
        "high": "1000010000000",
        "span": "10000000",
        "segment_size": "1310720",
        "result": "361726",
        "rounds": "9",
        "best_ms": "5.0",
        "median_ms": "5.0",
        "rate_per_second": "0",
        "median_rate_per_second": "0",
        "threads": "8",
        "requested_threads": "8",
        "baseline": "external_primesieve_count",
        "best_speedup": f"{median_speedup:.3f}",
        "median_speedup": f"{median_speedup:.3f}",
        "count_mode": mode,
        "sample_count": "9",
        "sample_noise_ms": "5.1",
        "sample_max_ms": "5.1",
        "sample_noise_over_median": "1.02",
        "sample_max_over_median": "1.02",
        "sample_ignored_single_high_outlier": "false",
        "sample_stability": stability,
    }


def write_sweep_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main_with_args(csv_path: Path) -> int:
    import sys

    old_argv = sys.argv
    try:
        sys.argv = [
            "check_prime_count_binary_cold_candidate_readout.py",
            "--csv",
            str(csv_path),
            "--skip-provenance",
        ]
        return main()
    finally:
        sys.argv = old_argv
