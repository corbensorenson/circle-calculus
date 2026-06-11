from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications.theseus_hive_contracts import build_contract_pack


DEFAULT_OUT = ROOT / "site" / "data" / "generated" / "theseus_hive_ai_contracts.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export public-safe Circle AI contracts for Theseus-Hive experiments.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output JSON path. Defaults to site/data/generated/theseus_hive_ai_contracts.json.",
    )
    args = parser.parse_args()

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_contract_pack(), indent=2, sort_keys=True) + "\n")
    try:
        display_path = out.relative_to(ROOT)
    except ValueError:
        display_path = out
    print(f"wrote {display_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
