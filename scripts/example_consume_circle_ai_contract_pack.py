#!/usr/bin/env python3
"""Example downstream consumer for the Circle AI contract pack.

This script is intentionally small and copyable. It uses only the public
consumer adapter, not Lean, manifests, dictionary YAML, Quarto, or private
Theseus-Hive state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from circle_math.applications.circle_ai_contract_consumer import (  # noqa: E402
    ContractConsumerError,
    contract_digest,
    contract_kinds,
    load_contract_pack,
    planner_action_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        default="site/data/generated/circle_ai_contract_pack.json",
        help="Path to a generated circle_calculus.ai_contract_pack.v0 JSON file.",
    )
    parser.add_argument(
        "--kind",
        default="rope_position_distinguishability",
        help="Contract kind to require and summarize.",
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="Evidence field to include. Repeat to request multiple fields.",
    )
    parser.add_argument(
        "--list-kinds",
        action="store_true",
        help="Print available contract kinds from the pack and exit.",
    )
    parser.add_argument(
        "--planner",
        action="store_true",
        help=(
            "Emit a copy-safe theorem-linked action plan from planner "
            "recommendations instead of a single contract digest."
        ),
    )
    parser.add_argument(
        "--planner-kind",
        action="append",
        default=[],
        help=(
            "Contract kind to include in --planner output. Repeat to include "
            "multiple kinds. Defaults to every ready contract kind."
        ),
    )
    parser.add_argument(
        "--planner-include-values",
        action="store_true",
        help=(
            "In --planner output, resolve evidence field names to contract "
            "field values and include recommendation-specific parameters."
        ),
    )
    parser.add_argument(
        "--include-field-metadata",
        action="store_true",
        help="Include field descriptions, JSON value kinds, and proof roles.",
    )
    parser.add_argument(
        "--include-recommendations",
        action="store_true",
        help="Include optional planner recommendation records.",
    )
    args = parser.parse_args()

    try:
        pack = load_contract_pack(args.pack)
        if args.list_kinds:
            print(json.dumps({"kinds": list(contract_kinds(pack))}, indent=2))
            return 0
        if args.planner:
            print(json.dumps(
                planner_action_plan(
                    pack,
                    args.planner_kind or None,
                    include_values=args.planner_include_values,
                ),
                indent=2,
            ))
            return 0
        digest = contract_digest(
            pack,
            args.kind,
            fields=args.field or None,
            include_field_metadata=args.include_field_metadata,
            include_recommendations=args.include_recommendations,
        )
    except (ContractConsumerError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Circle AI contract pack consumer failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(digest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
