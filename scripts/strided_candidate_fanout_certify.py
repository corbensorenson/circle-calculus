#!/usr/bin/env python
"""Run the finite strided candidate-fanout certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_strided_candidate_fanout_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite strided candidate fanout: gcd reach, orbit, "
            "coverage, candidate path, and duplicate-collapse fields."
        ),
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=12,
        help="Positive finite context length.",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=5,
        help="Nonnegative stride for candidate fanout.",
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Start/query index for the orbit and candidate path.",
    )
    parser.add_argument(
        "--path-length",
        type=int,
        default=12,
        help="Positive number of predecessor candidates to emit.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable fanout contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.context_length <= 0:
        raise SystemExit("--context-length must be positive")
    if args.stride < 0:
        raise SystemExit("--stride must be nonnegative")
    if args.path_length <= 0:
        raise SystemExit("--path-length must be positive")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_strided_candidate_fanout_contract(
        context_length=args.context_length,
        stride=args.stride,
        start_index=args.start_index,
        path_length=args.path_length,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    orbit_unique = len(set(fields["orbit"])) == len(fields["orbit"])
    path_unique = len(set(fields["candidate_path"])) == len(fields["candidate_path"])
    return [
        (
            "strided_candidate_fanout_contract="
            f"{status} context_length={fields['context_length']} "
            f"start_index={fields['start_index']} stride={fields['stride']} "
            f"gcd={fields['gcd']} predicted_reach={fields['predicted_reach']} "
            f"full_coverage={fields['full_coverage']}"
        ),
        (
            "orbit="
            f"nodes={tuple(fields['orbit'])} "
            f"orbit_unique={orbit_unique} "
            "predicted_reach_matches_orbit_length="
            f"{fields['predicted_reach'] == len(fields['orbit'])} "
            "theorems=AIT-T0001,AIT-T0002,AIT-T0003"
        ),
        (
            "candidate_path="
            f"nodes={tuple(fields['candidate_path'])} "
            f"candidate_budget={fields['candidate_budget']} "
            f"unique_candidate_count={fields['unique_candidate_count']} "
            f"effective_candidate_budget={fields['effective_candidate_budget']} "
            f"duplicate_count={fields['duplicate_count']} "
            f"path_unique={path_unique} "
            f"candidate_budget_accounting={fields['candidate_budget_accounting']} "
            f"candidate_budget_shortfall={fields['candidate_budget_shortfall']} "
            "effective_budget_reaches_predicted_reach="
            f"{fields['effective_budget_reaches_predicted_reach']}"
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
