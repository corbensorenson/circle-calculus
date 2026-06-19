from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "recurrence_schedule_certify.py"


def test_recurrence_schedule_certifier_cli_text_and_json(tmp_path: Path) -> None:
    json_out = tmp_path / "recurrence_schedule_contract.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--json-out",
            str(json_out),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert (
        "recurrence_schedule_contract=READY loop_period=5 "
        "sample_index=8 max_loops=7 token_count=8"
    ) in result.stdout
    assert (
        "exit_contract=required_steps=4 exit_step=4 overthinking_boundary=5 "
        "theorems=AIM-T0018,AIM-T0020,AIM-T0031,AIM-T0033"
    ) in result.stdout
    assert (
        "active_work=work_step=2 active=6 inactive=2 "
        "active_plus_inactive_eq_token_count=True post_period_active_empty=True"
    ) in result.stdout
    assert (
        "work_budget=total_active_token_work=21 total_inactive_token_work=19 "
        "full_loop_token_work=40 scheduled_work_saving=19 "
        "scheduled_work_saving_accounting=True "
        "post_period_extension_active_work_unchanged=True "
        "post_period_extension_saving_added_token_count=True "
        "post_period_extra_steps=3 "
        "post_period_multi_extension_saving=43 "
        "post_period_multi_extension_active_work_unchanged=True "
        "post_period_multi_extension_saving_added_extra_token_count=True"
    ) in result.stdout
    assert (
        "schedule_trace=active_counts=(8, 6, 4, 2, 1) "
        "inactive_counts=(0, 2, 4, 6, 7) "
        "active_sum_matches_total=True inactive_sum_matches_total=True "
        "first_inactive_steps_match_budget_successor=True "
        "theorems=AIM-T0113,AIM-T0114,AIM-T0120,AIM-T0123,AIM-T0130,AIM-T0144"
    ) in result.stdout
    assert (
        "periodic_shift=base_token=7 passes=3 amount=15 shifted_token=22 "
        "required_steps_invariant=True recurrence_budget_invariant=True "
        "training_free_budget_invariant=True exit_step_invariant=True "
        "overthinking_boundary_invariant=True active_step=2 "
        "active_at_step_invariant=True "
        "theorems=AIM-T0026,AIM-T0027,AIM-T0028,AIM-T0029,"
        "AIM-T0030,AIM-T0033,AIM-T0034,AIM-T0036"
    ) in result.stdout
    assert (
        "consumer_check=ready=True required_fields_present=True "
        "all_theorem_ids_proved=True missing_fields=0"
    ) in result.stdout
    assert "do not prove model quality" in result.stdout

    payload = json.loads(json_out.read_text())
    assert payload["id"] == "CC-AI-CONTRACT-RECURRENCE-001"
    assert payload["kind"] == "recurrence_schedule"
    assert payload["consumer_check"]["ready_for_downstream_fixture_use"] is True
    assert payload["consumer_check"]["missing_minimum_fields"] == []
    assert payload["proof_status"]["all_theorem_ids_proved"] is True
    assert "docs/RECURRENCE_SCHEDULE_CERTIFIER_QUICKSTART.md" in payload["quickstart_docs"]
    assert "python scripts/recurrence_schedule_certify.py" in payload["entrypoints"]
    fields = payload["fields"]
    assert fields["active_token_count_trace"] == [8, 6, 4, 2, 1]
    assert fields["inactive_token_count_trace"] == [0, 2, 4, 6, 7]
    assert fields["active_token_count_trace_sum"] == 21
    assert fields["inactive_token_count_trace_sum"] == 19
    assert fields["active_token_count_trace_sum_matches_total"] is True
    assert fields["inactive_token_count_trace_sum_matches_total"] is True
    assert fields["first_inactive_steps"] == [
        {"token_index": 0, "active_budget": 1, "first_inactive_step": 2},
        {"token_index": 1, "active_budget": 2, "first_inactive_step": 3},
        {"token_index": 2, "active_budget": 3, "first_inactive_step": 4},
        {"token_index": 3, "active_budget": 4, "first_inactive_step": 5},
        {"token_index": 4, "active_budget": 5, "first_inactive_step": 6},
        {"token_index": 5, "active_budget": 1, "first_inactive_step": 2},
        {"token_index": 6, "active_budget": 2, "first_inactive_step": 3},
        {"token_index": 7, "active_budget": 3, "first_inactive_step": 4},
    ]
    assert fields["first_inactive_steps_match_budget_successor"] is True
    assert fields["periodic_shift_base_token"] == 7
    assert fields["periodic_shift_passes"] == 3
    assert fields["periodic_shift_amount"] == 15
    assert fields["periodic_shifted_token"] == 22
    assert fields["periodic_shift_required_steps_invariant"] is True
    assert fields["periodic_shift_recurrence_budget_invariant"] is True
    assert fields["periodic_shift_training_free_budget_invariant"] is True
    assert fields["periodic_shift_exit_step_invariant"] is True
    assert fields["periodic_shift_overthinking_boundary_invariant"] is True
    assert fields["periodic_shift_active_at_step_invariant"] is True
    assert fields["post_period_extension_horizon_steps"] == 6
    assert fields["post_period_extension_total_active_token_work"] == 21
    assert fields["post_period_extension_total_inactive_token_work"] == 27
    assert fields["post_period_extension_full_loop_token_work"] == 48
    assert fields["post_period_extension_scheduled_work_saving"] == 27
    assert fields["post_period_extension_active_work_unchanged"] is True
    assert fields["post_period_extension_inactive_work_added_token_count"] is True
    assert fields["post_period_extension_saving_added_token_count"] is True
    assert fields["default_fixture_5_8_6_total_active_token_work"] == 21
    assert fields["default_fixture_5_8_6_scheduled_work_saving"] == 27
    assert fields["default_fixture_5_8_6_active_work_unchanged"] is True
    assert fields["default_fixture_5_8_6_saving_added_token_count"] is True
    assert fields["post_period_extra_steps"] == 3
    assert fields["post_period_multi_extension_horizon_steps"] == 8
    assert fields["post_period_multi_extension_total_active_token_work"] == 21
    assert fields["post_period_multi_extension_total_inactive_token_work"] == 43
    assert fields["post_period_multi_extension_full_loop_token_work"] == 64
    assert fields["post_period_multi_extension_scheduled_work_saving"] == 43
    assert fields["post_period_multi_extension_active_work_unchanged"] is True
    assert fields["post_period_multi_extension_inactive_work_added_extra_token_count"] is True
    assert fields["post_period_multi_extension_saving_added_extra_token_count"] is True
    assert fields["default_fixture_5_8_8_total_active_token_work"] == 21
    assert fields["default_fixture_5_8_8_scheduled_work_saving"] == 43
    assert fields["default_fixture_5_8_8_active_work_unchanged"] is True
    assert fields["default_fixture_5_8_8_saving_added_extra_token_count"] is True
    assert "AIM-T0026" in payload["theorem_ids"]
    assert "AIM-T0036" in payload["theorem_ids"]
    assert "AIM-T0150" in payload["theorem_ids"]
    assert "AIM-T0154" in payload["theorem_ids"]
    assert "AIM-T0155" in payload["theorem_ids"]
    assert "AIM-T0159" in payload["theorem_ids"]


def test_recurrence_schedule_certifier_cli_json_custom_shift() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--shift-passes",
            "4",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    fields = payload["fields"]
    assert fields["periodic_shift_passes"] == 4
    assert fields["periodic_shift_amount"] == 20
    assert fields["periodic_shifted_token"] == 27
    assert fields["periodic_shift_required_steps_invariant"] is True
    assert fields["periodic_shift_recurrence_budget_invariant"] is True
    assert fields["periodic_shift_active_at_step_invariant"] is True
