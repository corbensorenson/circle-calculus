from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "stride_family_certify.py"


def test_stride_family_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "stride_family_certificate.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--context",
            "120",
            "--strides",
            "7,13",
            "--path-length",
            "3",
            "--local-window",
            "4",
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "stride_family_contract=GAPS context=120 strides=(7, 13)" in result.stdout
    assert "covered_lags=10 uncovered_lags=109 uncovered_intervals=6" in result.stdout
    assert "uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119))" in result.stdout
    assert "lag_budget_status=exact-raw-budget" in result.stdout
    assert "query_budget_status=exact-raw-budget" in result.stdout
    assert "AIT-T0076" in result.stdout
    assert "AIT-T0077" in result.stdout
    assert "AIT-T0090" in result.stdout
    assert "AIT-T0091" in result.stdout
    assert "not model-quality evidence" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["coverage_complete"] is False
    assert payload["covered_lags"] == [1, 2, 3, 4, 7, 14, 21, 13, 26, 39]
    assert payload["uncovered_lags"][:5] == [5, 6, 8, 9, 10]
    assert payload["uncovered_lag_intervals"] == [
        [5, 6],
        [8, 12],
        [15, 20],
        [22, 25],
        [27, 38],
        [40, 119],
    ]
    assert payload["uncovered_lag_interval_count"] == 6
    assert payload["theorem_side_lag_candidates_no_collision"] is True
    assert payload["theorem_side_query_candidates_no_collision"] is True
    assert "AIT-T0076" in payload["theorem_ids"]
    assert "AIT-T0077" in payload["theorem_ids"]
    assert "AIT-T0090" in payload["theorem_ids"]
    assert payload["fixture_theorem_ids"] == ["AIT-T0084", "AIT-T0085", "AIT-T0091"]
