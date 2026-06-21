from __future__ import annotations

import json
from pathlib import Path

from scripts.check_prime_engine_promotion_readout import (
    check_promotion_readout,
    main,
    trial_candidate_rows,
)


def test_promotion_check_passes_when_candidates_are_held() -> None:
    report = report_with_rows(
        [
            promotion_row("keep_default"),
            promotion_row("hold_unconfirmed_candidate"),
            promotion_row("hold_small_gain_candidate"),
        ]
    )

    result = check_promotion_readout(report)

    assert result["ok"] is True
    assert result["trial_rows"] == []
    assert "3 promotion row(s)" in result["message"]


def test_promotion_check_fails_when_readout_is_unavailable() -> None:
    result = check_promotion_readout(
        {"external_high_offset_promotion_readout": {"available": False, "rows": []}}
    )

    assert result["ok"] is False
    assert result["trial_rows"] == []
    assert "unavailable" in result["message"]


def test_trial_candidate_rows_select_only_trial_ready_actions() -> None:
    summary = {
        "available": True,
        "rows": [
            promotion_row("hold_small_gain_candidate"),
            promotion_row("trial_candidate_default", low=10, high=20),
            promotion_row("keep_default"),
        ],
    }

    rows = trial_candidate_rows(summary)

    assert len(rows) == 1
    assert rows[0]["low"] == 10
    assert rows[0]["high"] == 20


def test_promotion_check_fails_when_trial_candidate_is_ready() -> None:
    report = report_with_rows(
        [
            promotion_row("keep_default"),
            promotion_row("trial_candidate_default", low=100, high=200),
        ]
    )

    result = check_promotion_readout(report)

    assert result["ok"] is False
    assert len(result["trial_rows"]) == 1
    assert "trial-ready candidate default" in result["message"]


def test_main_reports_trial_ready_candidate(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(
            report_with_rows(
                [promotion_row("trial_candidate_default", low=1_000, high=2_000)]
            )
        )
    )

    status = main_with_args(report_path)

    captured = capsys.readouterr()
    assert status == 1
    assert "[1000, 2000)" in captured.err
    assert "candidate=presieve17:1310720:8" in captured.err


def test_main_passes_when_no_trial_candidate(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(report_with_rows([promotion_row("hold_small_gain_candidate")]))
    )

    status = main_with_args(report_path)

    captured = capsys.readouterr()
    assert status == 0
    assert "OK: no trial-ready" in captured.out


def report_with_rows(rows: list[dict]) -> dict:
    return {
        "external_high_offset_promotion_readout": {
            "available": True,
            "rows": rows,
        }
    }


def promotion_row(action: str, *, low: int = 1, high: int = 2) -> dict:
    return {
        "action": action,
        "low": low,
        "high": high,
        "baseline": "external_primesieve_count_server",
        "median_gain_over_default": 1.071,
        "default": {
            "count_mode": "presieve13",
            "segment_size": 1310720,
            "circle_threads": 8,
            "median_circle_speedup": 1.500,
        },
        "best": {
            "count_mode": "presieve17",
            "segment_size": 1310720,
            "circle_threads": 8,
            "median_circle_speedup": 1.607,
        },
    }


def main_with_args(report_path: Path) -> int:
    import sys

    old_argv = sys.argv
    try:
        sys.argv = [
            "check_prime_engine_promotion_readout.py",
            str(report_path),
        ]
        return main()
    finally:
        sys.argv = old_argv
