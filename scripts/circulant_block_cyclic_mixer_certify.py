#!/usr/bin/env python
"""Run the finite circulant/block-cyclic mixer certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import build_circulant_block_cyclic_mixer_contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify deterministic circulant-vs-dense mixer parity plus "
            "block-cyclic adapter parameter/load accounting fields."
        ),
    )
    parser.add_argument(
        "--period",
        type=int,
        default=8,
        help="Positive period for the circulant mixer fixture.",
    )
    parser.add_argument(
        "--channel-count",
        type=int,
        default=128,
        help="Positive channel count for the adapter accounting fixture.",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=8,
        help="Positive block size for block-cyclic adapter accounting.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable mixer contract JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full generic contract JSON to stdout.",
    )
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    if args.period <= 0:
        raise SystemExit("--period must be positive")
    if args.channel_count <= 0:
        raise SystemExit("--channel-count must be positive")
    if args.block_size <= 0:
        raise SystemExit("--block-size must be positive")
    if args.block_size > args.channel_count:
        raise SystemExit("--block-size must be less than or equal to --channel-count")


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    _validate_args(args)
    return build_circulant_block_cyclic_mixer_contract(
        period=args.period,
        channel_count=args.channel_count,
        block_size=args.block_size,
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary_lines(payload: dict[str, Any]) -> list[str]:
    fields = payload["fields"]
    consumer = payload["consumer_check"]
    status = "READY" if consumer["ready_for_downstream_fixture_use"] else "NOT_READY"
    output_parity = fields["circulant_output"] == fields["dense_output"]
    return [
        (
            "circulant_block_cyclic_mixer_contract="
            f"{status} period={fields['period']} "
            f"channel_count={fields['channel_count']} block_size={fields['block_size']}"
        ),
        (
            "circulant_parity="
            f"output_parity={output_parity} "
            f"max_abs_dense_delta={fields['max_abs_dense_delta']} "
            f"circulant_output={tuple(fields['circulant_output'])} "
            f"dense_output={tuple(fields['dense_output'])} "
            f"theorems=AIT-T0006,AIT-T0007,AIT-T0008,AIT-T0009"
        ),
        (
            "circulant_parameters="
            f"circulant_parameters={fields['circulant_parameters']} "
            f"dense_parameters={fields['dense_parameters']} "
            f"circulant_parameter_ratio={fields['circulant_parameter_ratio']}"
        ),
        (
            "block_cyclic_accounting="
            f"dense_adapter_parameters={fields['dense_adapter_parameters']} "
            f"lora_parameters={fields['lora_parameters']} "
            f"block_cyclic_parameters={fields['block_cyclic_parameters']} "
            f"block_to_dense_ratio={fields['block_to_dense_ratio']} "
            f"block_loads={tuple(fields['block_loads'])} "
            f"theorems=AIRA-T0001,AIRA-T0002,AIRA-T0004"
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
