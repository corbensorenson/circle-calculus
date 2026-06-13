from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "kv_cache_certify.py"


def test_kv_cache_certifier_cli_text_and_json_out(tmp_path: Path) -> None:
    json_out = tmp_path / "kv_cache_certificate.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--cache-size",
            "16",
            "--current",
            "31",
            "--token",
            "20",
            "--batch-tokens",
            "20,24,29,31",
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "kv_cache_contract=LIVE cache_size=16 current=31 token=20 slot=4" in result.stdout
    assert "overwrite_boundary=next_overwrite=36 after_current=True" in result.stdout
    assert "batch_contract=tokens=(20, 24, 29, 31) slots=(4, 8, 13, 15)" in result.stdout
    assert "live_window_contract=FULL start=16 length=16" in result.stdout
    assert "full_coverage_contract=True" in result.stdout
    assert "AIM-T0074" in result.stdout
    assert "not a paging-policy" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["schema_id"] == "circle_calculus.kv_cache_ring_buffer_certificate.v0"
    assert payload["window_certificate"]["retained"] is True
    assert payload["batch_certificate"]["slots_distinct"] is True
    assert payload["live_window_certificate"]["full_coverage_contract"] is True
    assert "AIM-T0074" in payload["live_window_certificate"]["theorem_ids"]


def test_kv_cache_certifier_cli_json_stdout_prefix_window() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--cache-size",
            "16",
            "--current",
            "5",
            "--token",
            "2",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["window_certificate"]["retained"] is True
    assert payload["batch_certificate"]["tokens"] == [2]
    assert payload["live_window_certificate"]["start"] == 0
    assert payload["live_window_certificate"]["length"] == 6
    assert payload["live_window_certificate"]["full_window"] is False
    assert payload["live_window_certificate"]["slot_count_matches_cache_size"] is False
    assert payload["live_window_certificate"]["full_coverage_contract"] is False
