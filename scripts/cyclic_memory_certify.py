#!/usr/bin/env python
"""Run the finite cyclic memory residue/winding certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_cyclic_memory_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify finite cyclic memory slot aliases, residue/winding "
            "reconstruction, and residue-class load fields."
        ),
    )
    parser.add_argument(
        "--bank-size",
        type=int,
        default=8,
        help="Positive cyclic memory bank size.",
    )
    parser.add_argument(
        "--event-index",
        type=int,
        default=23,
        help="Event index to decompose into winding and residue.",
    )
    parser.add_argument(
        "--event-count",
        type=int,
        default=32,
        help="Positive number of events in the finite memory trace.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable cyclic memory contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.bank_size <= 0:
        raise SystemExit("--bank-size must be positive")
    if args.event_count <= 0:
        raise SystemExit("--event-count must be positive")
    if args.event_index < 0:
        raise SystemExit("--event-index must be nonnegative")
    if args.event_index >= args.event_count:
        raise SystemExit("--event-index must be less than --event-count")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_cyclic_memory_contract(
        bank_size=args.bank_size,
        event_index=args.event_index,
        event_count=args.event_count,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    reconstruction = fields["winding"] * fields["bank_size"] + fields["residue_slot"]
    return [
        (
            "cyclic_memory_contract="
            f"{status} bank_size={fields['bank_size']} "
            f"event_index={fields['event_index']} event_count={fields['event_count']} "
            f"residue_slot={fields['residue_slot']} winding={fields['winding']}"
        ),
        (
            "alias_class="
            f"same_residue_events={tuple(fields['same_residue_events'])} "
            f"same_residue_windings={tuple(fields['same_residue_windings'])} "
            f"max_alias_load={fields['max_alias_load']} "
            "theorems=AIM-T0001,AIM-T0002,AIM-T0004,AIM-T0005"
        ),
        (
            "reconstruction="
            f"event_index={fields['event_index']} "
            f"winding_times_bank_plus_residue={reconstruction} "
            f"exact={fields['event_index'] == reconstruction}"
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
