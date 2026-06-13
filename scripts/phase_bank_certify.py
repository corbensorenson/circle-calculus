#!/usr/bin/env python
"""Run the exact integer-period phase-bank distinguishability certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import (
    PHASE_BANK_CERTIFIER_PRESETS,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Certify exact position distinguishability for a declared positive "
            "integer-period phase bank."
        ),
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PHASE_BANK_CERTIFIER_PRESETS),
        help="Named exact phase-bank diagnostic preset. Explicit flags override preset values.",
    )
    parser.add_argument(
        "--periods",
        type=parse_periods,
        help="Comma-separated positive integer periods, for example 6,9,13,18.",
    )
    parser.add_argument("--context", type=int, help="Inspected context length.")
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
    return parser


def parse_args() -> argparse.Namespace:
    return build_parser().parse_args()


def config_from_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> PhaseBankConfig:
    base_config = PHASE_BANK_CERTIFIER_PRESETS.get(args.preset) if args.preset else None
    periods = (
        args.periods
        if args.periods is not None
        else (base_config.periods if base_config else None)
    )
    context = (
        args.context
        if args.context is not None
        else (base_config.context_length if base_config else None)
    )
    if periods is None or context is None:
        parser.error("either --preset or both --periods and --context are required")
    return PhaseBankConfig(periods=periods, context_length=context)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    certificate = certify_phase_bank_positions(config_from_args(args, parser))
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
