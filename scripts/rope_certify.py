#!/usr/bin/env python
"""Run the proof-carrying RoPE position distinguishability certifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from circle_math.applications import (
    ROPE_CERTIFIER_PRESETS,
    RoPEConfig,
    certificate_summary_lines,
    certify_rope_positions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Certify exact discrete RoPE position distinguishability and report real-phase margins.",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(ROPE_CERTIFIER_PRESETS),
        help="Named public-safe config preset. Explicit numeric flags override preset values.",
    )
    parser.add_argument("--head-dim", type=int, help="RoPE head dimension; must be even.")
    parser.add_argument("--base", type=float, help="RoPE base, for example 10000 or 500000.")
    parser.add_argument("--context", type=int, help="Inspected context length.")
    parser.add_argument("--tolerance", type=float, help="Numerical real-phase tolerance in radians.")
    parser.add_argument(
        "--discretization",
        choices=("round", "floor", "ceil"),
        help="How real period estimates are mapped to integer periods for the Lean-backed contract.",
    )
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


def config_from_args(args: argparse.Namespace) -> RoPEConfig:
    base_config = ROPE_CERTIFIER_PRESETS.get(args.preset) if args.preset else None
    return RoPEConfig(
        head_dim=args.head_dim if args.head_dim is not None else (base_config.head_dim if base_config else 128),
        base=args.base if args.base is not None else (base_config.base if base_config else 10000.0),
        context_length=(
            args.context
            if args.context is not None
            else (base_config.context_length if base_config else 32768)
        ),
        tolerance=(
            args.tolerance
            if args.tolerance is not None
            else (base_config.tolerance if base_config else 1e-6)
        ),
        discretization=(
            args.discretization
            if args.discretization is not None
            else (base_config.discretization if base_config else "round")
        ),
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    certificate = certify_rope_positions(config_from_args(args))
    payload = certificate.to_dict()
    if args.json_out is not None:
        write_json(args.json_out, payload)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in certificate_summary_lines(certificate):
            print(line)
        if certificate.exact_discrete.sample_collision_pairs:
            print(f"sample_collision_pairs={certificate.exact_discrete.sample_collision_pairs}")
        if certificate.real_phase_margin.near_collision_gaps:
            print(f"near_collision_gaps={certificate.real_phase_margin.near_collision_gaps}")


if __name__ == "__main__":
    main()
