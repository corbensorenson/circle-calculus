#!/usr/bin/env python3
"""Copyable JSON Schema validation example for the Circle AI contract pack.

This script intentionally does not import Circle modules. It is a downstream
consumer pattern: read a generated pack, read its JSON Schema sidecar, and
validate the JSON shape before doing project-specific work.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        default="site/data/generated/circle_ai_contract_pack.json",
        help="Path to circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--schema",
        default="site/data/generated/circle_ai_contract_pack.schema.json",
        help="Path to circle_ai_contract_pack.schema.json.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print schema id, contract count, and contract kinds after validation.",
    )
    args = parser.parse_args()

    pack_path = Path(args.pack)
    schema_path = Path(args.schema)
    pack = json.loads(pack_path.read_text())
    schema = json.loads(schema_path.read_text())

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(pack, schema)

    if args.summary:
        contracts = pack.get("contracts", [])
        kinds = [
            contract.get("kind")
            for contract in contracts
            if isinstance(contract, dict) and isinstance(contract.get("kind"), str)
        ]
        print(
            " ".join(
                [
                    "circle AI contract schema ok:",
                    f"schema_id={pack.get('schema_id')}",
                    f"contracts={len(contracts) if isinstance(contracts, list) else 0}",
                    "kinds=" + ",".join(sorted(kinds)),
                ]
            )
        )
    else:
        print(f"circle AI contract schema ok: {pack_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
