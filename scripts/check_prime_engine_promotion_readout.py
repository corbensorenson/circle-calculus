from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = (
    ROOT
    / "sidecars"
    / "PRIME_ENGINE"
    / "results"
    / "prime_engine_report_latest.json"
)
TRIAL_ACTION = "trial_candidate_default"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when the latest prime-engine report contains a fresh, "
            "confirmed high-offset candidate that is ready to trial as the "
            "adaptive default."
        )
    )
    parser.add_argument(
        "report",
        nargs="?",
        type=Path,
        default=DEFAULT_REPORT,
        help=(
            "Report JSON produced by scripts/report_prime_engine_results.py. "
            f"Defaults to {DEFAULT_REPORT}."
        ),
    )
    args = parser.parse_args()

    try:
        report = load_json_report(args.report)
    except OSError as exc:
        print(f"ERROR: could not read {args.report}: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: could not parse {args.report}: {exc}", file=sys.stderr)
        return 1

    result = check_promotion_readout(report)
    if result["ok"]:
        print(result["message"])
        return 0

    print(result["message"], file=sys.stderr)
    for row in result["trial_rows"]:
        print(f"  - {format_trial_row(row)}", file=sys.stderr)
    return 1


def load_json_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"expected report object in {path}")
    return data


def check_promotion_readout(report: dict[str, Any]) -> dict[str, Any]:
    summary = promotion_readout(report)
    if not summary.get("available"):
        return {
            "ok": False,
            "message": (
                "ERROR: high-offset promotion readout is unavailable; run "
                "`make prime-engine-competitive-short` or regenerate the report "
                "after hot-server and candidate-confirmation evidence exists."
            ),
            "trial_rows": [],
        }

    rows = promotion_rows(summary)
    trial_rows = trial_candidate_rows(summary)
    if trial_rows:
        return {
            "ok": False,
            "message": (
                "ERROR: high-offset promotion readout has "
                f"{len(trial_rows)} trial-ready candidate default(s). "
                "Promote them intentionally or record why they are being held."
            ),
            "trial_rows": trial_rows,
        }

    return {
        "ok": True,
        "message": (
            "OK: no trial-ready high-offset candidate defaults "
            f"({len(rows)} promotion row(s) checked)."
        ),
        "trial_rows": [],
    }


def promotion_readout(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("external_high_offset_promotion_readout")
    return summary if isinstance(summary, dict) else {}


def promotion_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = summary.get("rows", [])
    return [row for row in rows if isinstance(row, dict)]


def trial_candidate_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in promotion_rows(summary)
        if row.get("action") == TRIAL_ACTION
    ]


def format_trial_row(row: dict[str, Any]) -> str:
    default = identity_text(row.get("default"))
    best = identity_text(row.get("best"))
    return (
        f"{range_text(row)} baseline={row.get('baseline', '?')} "
        f"default={default} candidate={best} "
        f"gain={ratio_text(row.get('median_gain_over_default'))} "
        f"candidate_speedup={ratio_text(nested_get(row, 'best', 'median_circle_speedup'))}"
    )


def identity_text(value: Any) -> str:
    if not isinstance(value, dict):
        return "?"
    mode = value.get("count_mode", "?")
    segment_size = value.get("segment_size", "?")
    threads = value.get("circle_threads", value.get("circle_requested_threads", "?"))
    return f"{mode}:{segment_size}:{threads}"


def range_text(row: dict[str, Any]) -> str:
    return f"[{row.get('low', '?')}, {row.get('high', '?')})"


def ratio_text(value: Any) -> str:
    if value is None:
        return "?"
    try:
        return f"{float(value):.3f}x"
    except (TypeError, ValueError):
        return str(value)


def nested_get(row: dict[str, Any], *keys: str) -> Any:
    value: Any = row
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


if __name__ == "__main__":
    raise SystemExit(main())
