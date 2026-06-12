#!/usr/bin/env python
"""Run the exact integer-period phase-bank distinguishability certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import (
    PhaseBankConfig,
    certify_phase_bank_positions,
    phase_bank_certificate_summary_lines,
)


def parse_periods(raw: str) -> tuple[int, ...]:
    parts = [part.strip() for part in raw.replace(";", ",").split(",")]
    periods = tuple(int(part) for part in parts if part)
    if not periods:
        raise argparse.ArgumentTypeError("periods must contain at least one integer")
    for period in periods:
        if period <= 0:
            raise argparse.ArgumentTypeError("periods must be positive")
    return periods


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Certify exact position distinguishability for a declared positive "
            "integer-period phase bank."
        ),
    )
    parser.add_argument(
        "--periods",
        required=True,
        type=parse_periods,
        help="Comma-separated positive integer periods, for example 6,9,13,18.",
    )
    parser.add_argument("--context", required=True, type=int, help="Inspected context length.")
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for a machine-readable certificate JSON report.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Print either human text or the full certificate JSON to stdout.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    certificate = certify_phase_bank_positions(
        PhaseBankConfig(periods=args.periods, context_length=args.context),
    )
    payload = certificate.to_dict()
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in phase_bank_certificate_summary_lines(certificate):
            print(line)
        if certificate.exact_discrete.sample_collision_pairs:
            print(f"sample_collision_pairs={certificate.exact_discrete.sample_collision_pairs}")


if __name__ == "__main__":
    main()
