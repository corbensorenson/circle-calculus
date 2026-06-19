#!/usr/bin/env python
"""Run the finite looped-recurrence schedule contract certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_recurrence_schedule_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite looped/recursive schedule bookkeeping: recurrence "
            "budget, exit step, active-token work, and whole-period index reuse."
        ),
    )
    parser.add_argument(
        "--loop-period",
        type=int,
        default=5,
        help="Positive loop period for the finite recurrence schedule.",
    )
    parser.add_argument(
        "--sample-index",
        type=int,
        default=8,
        help="Sample/token index used for the exit certificate.",
    )
    parser.add_argument(
        "--max-loops",
        type=int,
        default=7,
        help="Positive max-loop budget for the exit certificate.",
    )
    parser.add_argument(
        "--token-count",
        type=int,
        default=8,
        help="Number of generated token indices, starting at 0.",
    )
    parser.add_argument(
        "--selected-block-start",
        type=int,
        default=2,
        help="Start of the selected middle-block band used by the fixture.",
    )
    parser.add_argument(
        "--selected-block-width",
        type=int,
        default=3,
        help="Positive selected middle-block width used by the fixture.",
    )
    parser.add_argument(
        "--shift-passes",
        type=int,
        default=3,
        help="Whole loop-period passes used for the periodic-shift witness.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable recurrence contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.loop_period <= 0:
        raise SystemExit("--loop-period must be positive")
    if args.sample_index < 0:
        raise SystemExit("--sample-index must be nonnegative")
    if args.max_loops <= 0:
        raise SystemExit("--max-loops must be positive")
    if args.token_count <= 0:
        raise SystemExit("--token-count must be positive")
    if args.selected_block_start < 0:
        raise SystemExit("--selected-block-start must be nonnegative")
    if args.selected_block_width <= 0:
        raise SystemExit("--selected-block-width must be positive")
    if args.shift_passes < 0:
        raise SystemExit("--shift-passes must be nonnegative")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_recurrence_schedule_contract(
        loop_period=args.loop_period,
        sample_index=args.sample_index,
        max_loops=args.max_loops,
        token_indices=tuple(range(args.token_count)),
        selected_block_start=args.selected_block_start,
        selected_block_width=args.selected_block_width,
        periodic_shift_passes=args.shift_passes,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    theorem_ids = set(payload["theorem_ids"])
    shift_theorems = [
        theorem_id
        for theorem_id in (
            "AIM-T0026",
            "AIM-T0027",
            "AIM-T0028",
            "AIM-T0029",
            "AIM-T0030",
            "AIM-T0033",
            "AIM-T0034",
            "AIM-T0036",
        )
        if theorem_id in theorem_ids
    ]
    return [
        (
            "recurrence_schedule_contract="
            f"{status} loop_period={fields['loop_period']} "
            f"sample_index={fields['sample_index']} max_loops={fields['max_loops']} "
            f"token_count={len(fields['tokens'])}"
        ),
        (
            "exit_contract="
            f"required_steps={fields['required_steps']} exit_step={fields['exit_step']} "
            f"overthinking_boundary={fields['overthinking_boundary']} "
            "theorems=AIM-T0018,AIM-T0020,AIM-T0031,AIM-T0033"
        ),
        (
            "active_work="
            f"work_step={fields['work_count_step']} "
            f"active={fields['work_step_active_token_count']} "
            f"inactive={fields['work_step_inactive_token_count']} "
            "active_plus_inactive_eq_token_count="
            f"{fields['work_step_active_inactive_count_eq_token_count']} "
            "post_period_active_empty="
            f"{fields['post_period_active_empty']} "
            "theorems=AIM-T0111,AIM-T0112,AIM-T0120,AIM-T0123"
        ),
        (
            "work_budget="
            f"total_active_token_work={fields['total_active_token_work']} "
            f"total_inactive_token_work={fields['total_inactive_token_work']} "
            f"full_loop_token_work={fields['full_loop_token_work']} "
            f"scheduled_work_saving={fields['scheduled_work_saving']} "
            "scheduled_work_saving_accounting="
            f"{fields['scheduled_work_saving_accounting']} "
            "post_period_extension_active_work_unchanged="
            f"{fields['post_period_extension_active_work_unchanged']} "
            "post_period_extension_saving_added_token_count="
            f"{fields['post_period_extension_saving_added_token_count']} "
            "post_period_extra_steps="
            f"{fields['post_period_extra_steps']} "
            "post_period_multi_extension_saving="
            f"{fields['post_period_multi_extension_scheduled_work_saving']} "
            "post_period_multi_extension_active_work_unchanged="
            f"{fields['post_period_multi_extension_active_work_unchanged']} "
            "post_period_multi_extension_saving_added_extra_token_count="
            f"{fields['post_period_multi_extension_saving_added_extra_token_count']} "
            "theorems=AIM-T0130,AIM-T0131,AIM-T0144,AIM-T0145,"
            "AIM-T0150,AIM-T0151,AIM-T0152,AIM-T0155,AIM-T0156,AIM-T0157"
        ),
        (
            "schedule_trace="
            f"active_counts={tuple(fields['active_token_count_trace'])} "
            f"inactive_counts={tuple(fields['inactive_token_count_trace'])} "
            "active_sum_matches_total="
            f"{fields['active_token_count_trace_sum_matches_total']} "
            "inactive_sum_matches_total="
            f"{fields['inactive_token_count_trace_sum_matches_total']} "
            "first_inactive_steps_match_budget_successor="
            f"{fields['first_inactive_steps_match_budget_successor']} "
            "theorems=AIM-T0113,AIM-T0114,AIM-T0120,AIM-T0123,AIM-T0130,AIM-T0144"
        ),
        (
            "periodic_shift="
            f"base_token={fields['periodic_shift_base_token']} "
            f"passes={fields['periodic_shift_passes']} "
            f"amount={fields['periodic_shift_amount']} "
            f"shifted_token={fields['periodic_shifted_token']} "
            "required_steps_invariant="
            f"{fields['periodic_shift_required_steps_invariant']} "
            "recurrence_budget_invariant="
            f"{fields['periodic_shift_recurrence_budget_invariant']} "
            "training_free_budget_invariant="
            f"{fields['periodic_shift_training_free_budget_invariant']} "
            "exit_step_invariant="
            f"{fields['periodic_shift_exit_step_invariant']} "
            "overthinking_boundary_invariant="
            f"{fields['periodic_shift_overthinking_boundary_invariant']} "
            f"active_step={fields['periodic_shift_active_step']} "
            "active_at_step_invariant="
            f"{fields['periodic_shift_active_at_step_invariant']} "
            f"theorems={','.join(shift_theorems)}"
        ),
        (
            "consumer_check="
            f"ready={consumer['ready_for_downstream_fixture_use']} "
            f"required_fields_present={consumer['required_fields_present']} "
            f"all_theorem_ids_proved={consumer['all_theorem_ids_proved']} "
            f"missing_fields={len(consumer['missing_minimum_fields'])}"
        ),
        f"not_claimed={payload['not_claimed']}",
    ]


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload):
            print(line)


if __name__ == "__main__":
    main()
