#!/usr/bin/env python
"""Run the finite MultiCoil phase-feature certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_multicoil_phase_feature_contract


def parse_periods(raw: str) -> tuple[int, ...]:
    parts = tuple(int(part.strip()) for part in raw.replace(";", ",").split(",") if part.strip())
    if not parts:
        raise argparse.ArgumentTypeError("period list must not be empty")
    if any(period <= 0 for period in parts):
        raise argparse.ArgumentTypeError("all periods must be positive")
    return parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite MultiCoil phase tags, joint-repeat horizon, and "
            "relative-phase invariance under a full joint-cycle shift."
        ),
    )
    parser.add_argument(
        "--periods",
        type=parse_periods,
        default=(5, 7),
        help="Comma-separated positive periods, for example 5,7.",
    )
    parser.add_argument(
        "--position",
        type=int,
        default=37,
        help="Position whose multicoil phase tuple is inspected.",
    )
    parser.add_argument(
        "--query-position",
        type=int,
        default=41,
        help="Query position for the relative-phase fixture.",
    )
    parser.add_argument(
        "--key-position",
        type=int,
        default=18,
        help="Key position for the relative-phase fixture.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable phase-feature contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.position < 0:
        raise SystemExit("--position must be nonnegative")
    if args.query_position < 0:
        raise SystemExit("--query-position must be nonnegative")
    if args.key_position < 0:
        raise SystemExit("--key-position must be nonnegative")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_multicoil_phase_feature_contract(
        periods=args.periods,
        position=args.position,
        query_position=args.query_position,
        key_position=args.key_position,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    return [
        (
            "multicoil_phase_feature_contract="
            f"{status} periods={tuple(fields['periods'])} position={fields['position']} "
            f"phase_tuple={tuple(fields['phase_tuple'])} "
            f"joint_repeat_horizon={fields['joint_repeat_horizon']}"
        ),
        (
            "joint_shift="
            f"shifted_position={fields['shifted_position']} "
            f"shifted_phase_tuple={tuple(fields['shifted_phase_tuple'])} "
            "phase_invariant="
            f"{fields['phase_tuple'] == fields['shifted_phase_tuple']} "
            "theorems=AIA-T0001,AIA-T0002,AIA-T0004"
        ),
        (
            "relative_phase="
            f"query_position={fields['query_position']} "
            f"key_position={fields['key_position']} "
            f"relative_period={fields['relative_period']} "
            f"relative_phase={fields['relative_phase']} "
            f"shifted_relative_phase={fields['shifted_relative_phase']} "
            "relative_phase_invariant="
            f"{fields['relative_phase'] == fields['shifted_relative_phase']} "
            "theorems=AIT-T0004,AIT-T0005"
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
