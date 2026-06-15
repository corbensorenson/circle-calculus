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
            "--request-id",
            "prefill_read",
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
    assert "no_same_slot_overwrite_before_current=True" in result.stdout
    assert "same_slot_overwrite_witness_when_stale=False" in result.stdout
    assert "stale_iff_same_slot_overwrite_trace=True" in result.stdout
    assert "retained_iff_no_same_slot_overwrite_trace=True" in result.stdout
    assert "trace_fresh_iff_next_overwrite_boundary=True" in result.stdout
    assert "batch_contract=tokens=(20, 24, 29, 31) slots=(4, 8, 13, 15)" in result.stdout
    assert "next_overwrites_after_current=True" in result.stdout
    assert "retained_iff_no_same_slot_overwrite_trace=True" in result.stdout
    assert "trace_fresh_slots_distinct=True" in result.stdout
    assert "adapter_request_trace=PASS request_id=prefill_read" in result.stdout
    assert "all_non_future=True all_retained=True tokens_distinct=True slots_distinct=True" in result.stdout
    assert "ordered_live_window_subrequest=True" in result.stdout
    assert "duplicate_free_live_window_subrequest=True" in result.stdout
    assert "live_window_subrequest_pass_contract=True" in result.stdout
    assert "adapter_request_boundary=pass_iff_next_overwrite_boundary=True" in result.stdout
    assert "fail_iff_stale_member_under_nonfuture_nodup=True" in result.stdout
    assert "live_window_contract=FULL start=16 length=16" in result.stdout
    assert "slot_count_matches_full_window=True" in result.stdout
    assert "slot_range_covered=True" in result.stdout
    assert "full_coverage_contract=True" in result.stdout
    assert "full_coverage_contract_matches_full_window=True" in result.stdout
    assert "live_window_request_trace=PASS request_id=prefill_read_generated_live_window" in result.stdout
    assert "exact_live_window_request=True" in result.stdout
    assert "live_window_request_contract=True" in result.stdout
    assert "AIM-T0074" in result.stdout
    assert "AIM-T0080" in result.stdout
    assert "AIM-T0081" in result.stdout
    assert "AIM-T0082" in result.stdout
    assert "AIM-T0083" in result.stdout
    assert "AIM-T0086" in result.stdout
    assert "AIM-T0087" in result.stdout
    assert "AIM-T0088" in result.stdout
    assert "AIM-T0089" in result.stdout
    assert "AIM-T0091" in result.stdout
    assert "AIM-T0092" in result.stdout
    assert "AIM-T0093" in result.stdout
    assert "AIM-T0094" in result.stdout
    assert "AIM-T0095" in result.stdout
    assert "AIM-T0096" in result.stdout
    assert "not a paging-policy" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["schema_id"] == "circle_calculus.kv_cache_ring_buffer_certificate.v0"
    assert payload["window_certificate"]["retained"] is True
    assert payload["window_certificate"]["no_same_slot_overwrite_before_current"] is True
    assert payload["window_certificate"]["same_slot_overwrite_witness_when_stale"] is False
    assert payload["window_certificate"]["stale_iff_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert "AIM-T0091" in payload["window_certificate"]["theorem_ids"]
    assert "AIM-T0099" in payload["window_certificate"]["theorem_ids"]
    assert payload["batch_certificate"]["slots_distinct"] is True
    assert payload["batch_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["batch_certificate"]["next_overwrites_after_current"] is True
    assert payload["batch_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["batch_certificate"]["trace_fresh_slots_distinct"] is True
    assert "AIM-T0079" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0091" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0092" in payload["batch_certificate"]["theorem_ids"]
    assert payload["adapter_request_trace_certificate"]["request_id"] == "prefill_read"
    assert payload["adapter_request_trace_certificate"]["requested_slots"] == [4, 8, 13, 15]
    assert payload["adapter_request_trace_certificate"]["pass_certificate"] is True
    assert payload["adapter_request_trace_certificate"]["first_stale_token"] is None
    assert payload["adapter_request_trace_certificate"]["first_stale_next_overwrite_token"] is None
    assert payload["adapter_request_trace_certificate"]["stale_member_blocks_pass"] is False
    assert payload["adapter_request_trace_certificate"]["next_overwrites_after_current"] is True
    assert payload["adapter_request_trace_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["adapter_request_trace_certificate"]["pass_iff_next_overwrite_boundary"] is True
    assert (
        payload["adapter_request_trace_certificate"][
            "pass_iff_no_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert (
        payload["adapter_request_trace_certificate"][
            "fail_iff_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert payload["adapter_request_trace_certificate"]["ordered_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["duplicate_free_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["live_window_subrequest_pass_contract"] is True
    assert "AIM-T0078" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0079" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0086" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0091" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0092" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0093" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0094" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0095" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0096" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0097" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0098" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0100" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert payload["live_window_certificate"]["full_coverage_contract"] is True
    assert payload["live_window_certificate"]["slot_count_matches_full_window"] is True
    assert payload["live_window_certificate"]["slot_range_covered"] is True
    assert payload["live_window_certificate"]["full_coverage_contract_matches_full_window"] is True
    assert "AIM-T0074" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0080" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0081" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0082" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0083" in payload["live_window_certificate"]["theorem_ids"]
    assert payload["live_window_request_certificate"]["request_id"] == (
        "prefill_read_generated_live_window"
    )
    assert payload["live_window_request_certificate"]["requested_tokens"] == list(range(16, 32))
    assert payload["live_window_request_certificate"]["requested_slots"] == list(range(16))
    assert payload["live_window_request_certificate"]["exact_live_window_request"] is True
    assert payload["live_window_request_certificate"]["pass_certificate"] is True
    assert payload["live_window_request_certificate"]["live_window_request_contract"] is True
    assert "AIM-T0087" in payload["live_window_request_certificate"]["theorem_ids"]
    assert "AIM-T0088" in payload["live_window_request_certificate"]["theorem_ids"]
    assert "AIM-T0089" in payload["live_window_request_certificate"]["fixture_theorem_ids"]


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
    assert payload["window_certificate"]["no_same_slot_overwrite_before_current"] is True
    assert payload["window_certificate"]["same_slot_overwrite_witness_when_stale"] is False
    assert payload["window_certificate"]["stale_iff_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["window_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["batch_certificate"]["tokens"] == [2]
    assert payload["batch_certificate"]["retained_iff_no_same_slot_overwrite_trace"] is True
    assert payload["batch_certificate"]["next_overwrites_after_current"] is True
    assert payload["batch_certificate"]["trace_fresh_iff_next_overwrite_boundary"] is True
    assert payload["batch_certificate"]["trace_fresh_slots_distinct"] is True
    assert "AIM-T0079" in payload["batch_certificate"]["theorem_ids"]
    assert "AIM-T0092" in payload["batch_certificate"]["theorem_ids"]
    assert payload["adapter_request_trace_certificate"]["requested_tokens"] == [2]
    assert payload["adapter_request_trace_certificate"]["pass_certificate"] is True
    assert payload["adapter_request_trace_certificate"]["pass_iff_next_overwrite_boundary"] is True
    assert (
        payload["adapter_request_trace_certificate"][
            "pass_iff_no_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert (
        payload["adapter_request_trace_certificate"][
            "fail_iff_stale_member_under_nonfuture_nodup"
        ]
        is True
    )
    assert payload["adapter_request_trace_certificate"]["first_stale_token"] is None
    assert payload["adapter_request_trace_certificate"]["first_stale_next_overwrite_token"] is None
    assert payload["adapter_request_trace_certificate"]["stale_member_blocks_pass"] is False
    assert payload["adapter_request_trace_certificate"]["ordered_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["duplicate_free_live_window_subrequest"] is True
    assert payload["adapter_request_trace_certificate"]["live_window_subrequest_pass_contract"] is True
    assert "AIM-T0086" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0093" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0094" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0095" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert "AIM-T0096" in payload["adapter_request_trace_certificate"]["theorem_ids"]
    assert payload["live_window_certificate"]["start"] == 0
    assert payload["live_window_certificate"]["length"] == 6
    assert payload["live_window_certificate"]["full_window"] is False
    assert payload["live_window_certificate"]["slot_count_matches_cache_size"] is False
    assert payload["live_window_certificate"]["slot_count_matches_full_window"] is True
    assert payload["live_window_certificate"]["slot_range_covered"] is False
    assert payload["live_window_certificate"]["full_coverage_contract"] is False
    assert payload["live_window_certificate"]["full_coverage_contract_matches_full_window"] is True
    assert "AIM-T0080" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0081" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0082" in payload["live_window_certificate"]["theorem_ids"]
    assert "AIM-T0083" in payload["live_window_certificate"]["theorem_ids"]
    assert payload["live_window_request_certificate"]["requested_tokens"] == list(range(6))
    assert payload["live_window_request_certificate"]["requested_slots"] == list(range(6))
    assert payload["live_window_request_certificate"]["exact_live_window_request"] is True
    assert payload["live_window_request_certificate"]["pass_certificate"] is True
    assert payload["live_window_request_certificate"]["live_window_request_contract"] is True
    assert payload["live_window_request_certificate"]["fixture_theorem_ids"] == []
    assert "AIM-T0087" in payload["live_window_request_certificate"]["theorem_ids"]
    assert "AIM-T0088" in payload["live_window_request_certificate"]["theorem_ids"]


def test_kv_cache_certifier_cli_reports_stale_request_witness() -> None:
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
            "12,20",
            "--request-id",
            "stale_read",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    adapter_request = payload["adapter_request_trace_certificate"]
    assert adapter_request["request_id"] == "stale_read"
    assert adapter_request["requested_tokens"] == [12, 20]
    assert adapter_request["requested_slots"] == [12, 4]
    assert adapter_request["all_non_future"] is True
    assert adapter_request["tokens_distinct"] is True
    assert adapter_request["all_retained"] is False
    assert adapter_request["slots_distinct"] is False
    assert adapter_request["first_stale_token"] == 12
    assert adapter_request["first_stale_next_overwrite_token"] == 28
    assert adapter_request["stale_member_blocks_pass"] is True
    assert adapter_request["next_overwrites_after_current"] is False
    assert adapter_request["pass_certificate"] is False
    assert adapter_request["pass_iff_next_overwrite_boundary"] is True
    assert adapter_request["pass_iff_no_stale_member_under_nonfuture_nodup"] is True
    assert adapter_request["fail_iff_stale_member_under_nonfuture_nodup"] is True
    assert "AIM-T0097" in adapter_request["theorem_ids"]
    assert "AIM-T0098" in adapter_request["theorem_ids"]
    assert "AIM-T0100" in adapter_request["theorem_ids"]
