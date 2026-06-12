from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications.theseus_hive_feedback import import_feedback_summary


DEFAULT_INPUT = ROOT.parent / "Theseus-Hive" / "reports" / "circle_ai_feedback_summary.json"
DEFAULT_OUT = ROOT / "site" / "data" / "generated" / "theseus_hive_ai_feedback_summary.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import a public-safe Theseus-Hive Circle AI feedback summary.",
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Sanitized Theseus feedback summary JSON path.",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output JSON path for the Living Book.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail instead of writing a placeholder when the input summary is missing.",
    )
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_absolute():
        source = ROOT / source
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out

    if source.exists():
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit(f"expected object JSON at {source}")
        imported = import_feedback_summary(payload, source_path=display_path(source))
    else:
        if args.strict:
            raise SystemExit(f"missing Theseus feedback summary: {source}")
        imported = import_feedback_summary(None, source_path=display_path(source))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(imported, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {display_path(out)}")
    return 0


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        pass
    try:
        return str(path.resolve().relative_to(ROOT.parent.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


if __name__ == "__main__":
    raise SystemExit(main())
