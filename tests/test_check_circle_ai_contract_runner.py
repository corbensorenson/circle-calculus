from __future__ import annotations

import json
import subprocess
import sys


def test_check_circle_ai_contract_runner_accepts_examples() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_circle_ai_contract_runner.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "circle AI runner examples ok=True examples=4 failures=0" in result.stdout
    assert "kind=rope_position_distinguishability" in result.stdout
    assert "kind=kv_cache_ring_buffer" in result.stdout
    assert "kind=sparse_attention_coverage" in result.stdout
    assert "kind=recurrence_schedule" in result.stdout


def test_check_circle_ai_contract_runner_emits_json_report() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_circle_ai_contract_runner.py",
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.ai_contract_runner_check.v0"
    assert payload["ok"] is True
    assert payload["example_count"] == 4
    assert payload["failure_count"] == 0
    assert payload["failures"] == []
    assert all(
        len(summary["request_content_fingerprint"]) == 64
        for summary in payload["summaries"]
    )
