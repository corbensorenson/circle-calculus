from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications.circle_ai_contracts import (
    build_contract_pack,
    build_contract_pack_json_schema,
)


DEFAULT_OUT = ROOT / "site" / "data" / "generated" / "circle_ai_contract_pack.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export the public standalone Circle AI contract pack.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output JSON path. Defaults to site/data/generated/circle_ai_contract_pack.json.",
    )
    parser.add_argument(
        "--schema-out",
        help=(
            "Output JSON Schema path. Defaults to the pack output path with "
            ".schema.json suffix."
        ),
    )
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    schema_out = Path(args.schema_out) if args.schema_out else out.with_suffix(".schema.json")
    if not schema_out.is_absolute():
        schema_out = ROOT / schema_out
    out.parent.mkdir(parents=True, exist_ok=True)
    schema_out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_contract_pack(), indent=2, sort_keys=True) + "\n")
    schema_out.write_text(
        json.dumps(build_contract_pack_json_schema(), indent=2, sort_keys=True) + "\n"
    )
    try:
        display_path = out.relative_to(ROOT)
    except ValueError:
        display_path = out
    try:
        display_schema_path = schema_out.relative_to(ROOT)
    except ValueError:
        display_schema_path = schema_out
    print(f"wrote {display_path}")
    print(f"wrote {display_schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
