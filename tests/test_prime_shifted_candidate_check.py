from __future__ import annotations

import json
from pathlib import Path

from scripts.check_prime_shifted_candidate_readout import (
    check_shifted_candidate_readout,
    main,
    trial_shifted_candidate_rows,
)


def test_shifted_candidate_check_passes_when_candidates_are_held() -> None:
    report = report_with_rows(
        [
            shifted_row("keep_default", gain=1.0),
            shifted_row("hold_small_gain_candidate", gain=1.024),
        ]
    )

    result = check_shifted_candidate_readout(report)

    assert result["ok"] is True
    assert result["trial_rows"] == []
    assert "2 shifted row(s)" in result["message"]
    assert "best gain 1.024x" in result["message"]


def test_shifted_candidate_check_fails_when_readout_is_unavailable() -> None:
    result = check_shifted_candidate_readout(
        {
            "external_high_offset_shifted_candidate_readout": {
                "available": False,
                "rows": [],
            }
        }
    )

    assert result["ok"] is False
    assert result["trial_rows"] == []
    assert "unavailable" in result["message"]


def test_trial_shifted_candidate_rows_select_only_trial_ready_actions() -> None:
    summary = {
        "available": True,
        "rows": [
            shifted_row("hold_small_gain_candidate", gain=1.024),
            shifted_row("trial_shifted_candidate", low=10, high=20, gain=1.08),
            shifted_row("keep_default", gain=1.0),
        ],
    }

    rows = trial_shifted_candidate_rows(summary)

    assert len(rows) == 1
    assert rows[0]["low"] == 10
    assert rows[0]["high"] == 20


def test_main_reports_trial_ready_shifted_candidate(
    tmp_path: Path, capsys
) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(
            report_with_rows(
                [shifted_row("trial_shifted_candidate", low=1_000, high=2_000)]
            )
        )
    )

    status = main_with_args(report_path)

    captured = capsys.readouterr()
    assert status == 1
    assert "[1000, 2000)" in captured.err
    assert "candidate=presieve13:1507328:7" in captured.err


def test_main_passes_when_no_trial_shifted_candidate(
    tmp_path: Path, capsys
) -> None:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(report_with_rows([shifted_row("hold_small_gain_candidate")]))
    )

    status = main_with_args(report_path)

    captured = capsys.readouterr()
    assert status == 0
    assert "OK: no trial-ready" in captured.out


def report_with_rows(rows: list[dict]) -> dict:
    return {
        "external_high_offset_shifted_candidate_readout": {
            "available": True,
            "rows": rows,
        }
    }


def shifted_row(
    action: str,
    *,
    low: int = 1,
    high: int = 2,
    gain: float = 1.08,
) -> dict:
    return {
        "action": action,
        "low": low,
        "high": high,
        "baseline": "external_primesieve_count_server",
        "median_gain_over_default": gain,
        "default": {
            "count_mode": "presieve13",
            "segment_size": 1310720,
            "circle_threads": 8,
            "median_circle_speedup": 1.195,
        },
        "best": {
            "count_mode": "presieve13",
            "segment_size": 1507328,
            "circle_threads": 7,
            "median_circle_speedup": 1.291,
        },
    }


def main_with_args(report_path: Path) -> int:
    import sys

    old_argv = sys.argv
    try:
        sys.argv = [
            "check_prime_shifted_candidate_readout.py",
            str(report_path),
        ]
        return main()
    finally:
        sys.argv = old_argv
