from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALIBRATION = (
    ROOT / "sidecars" / "PRIME_ENGINE" / "results" / "prime_engine_default_calibration_latest.json"
)
DEFAULTS_PATH = ROOT / "rust" / "circle-prime" / "prime_engine_defaults.json"

VALID_COUNT_MODES = {
    "segmented",
    "balanced",
    "dynamic",
    "prefix-pi",
    "presieve13",
    "presieve17",
    "wheel30-mark",
    "hybrid-wheel30-mark",
}

DEFAULT_KEYS_BY_RANGE = {
    (0, 1_000_000): {
        "segment_size": "parallel_tiny_prefix_segment_size",
        "count_mode": "parallel_tiny_prefix_count_mode",
    },
    (0, 10_000_000): {
        "segment_size": "parallel_small_prefix_segment_size",
        "count_mode": "parallel_small_prefix_count_mode",
    },
    (0, 100_000_000): {
        "segment_size": "parallel_medium_prefix_segment_size",
        "count_mode": "parallel_medium_prefix_count_mode",
    },
    (1_000_000_000_000, 1_000_010_000_000): {
        "segment_size": "parallel_very_high_offset_segment_size",
        "count_mode": "parallel_very_high_offset_count_mode",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Apply calibrated Circle prime-engine segment/mode defaults to the "
            "structured Rust defaults file."
        )
    )
    parser.add_argument("--calibration", type=Path, default=DEFAULT_CALIBRATION)
    parser.add_argument("--defaults", type=Path, default=DEFAULTS_PATH)
    parser.add_argument(
        "--allow-noisy",
        action="store_true",
        help="Allow external recommendations whose sample stability is noisy.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if the defaults file does not match calibration.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing the defaults file.",
    )
    args = parser.parse_args()

    calibration = json.loads(args.calibration.read_text())
    defaults = json.loads(args.defaults.read_text())
    updated, changes, skipped = build_default_updates(
        calibration,
        defaults,
        allow_noisy=args.allow_noisy,
    )

    for message in skipped:
        print(f"skip: {message}")

    if not changes:
        print("prime-engine defaults already match calibrated recommendations")
        return 0

    for change in changes:
        print(
            "update: "
            f"{change['key']} {change['old']} -> {change['new']} "
            f"from [{change['low']}, {change['high']})"
        )

    if args.check:
        print("prime-engine defaults differ from calibrated recommendations", file=sys.stderr)
        return 1
    if args.dry_run:
        return 0

    args.defaults.write_text(json.dumps(updated, indent=2, sort_keys=True) + "\n")
    print(f"wrote prime-engine defaults: {args.defaults}")
    return 0


def build_default_updates(
    calibration: dict[str, Any],
    defaults: dict[str, Any],
    *,
    allow_noisy: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    updated = dict(defaults)
    changes: list[dict[str, Any]] = []
    skipped: list[str] = []
    for row in calibration.get("recommendations", []):
        keys = DEFAULT_KEYS_BY_RANGE.get((int(row["low"]), int(row["high"])))
        if keys is None:
            skipped.append(f"no defaults key for [{row['low']}, {row['high']})")
            continue
        missing = [key for key in keys.values() if key not in defaults]
        if missing:
            raise KeyError(f"defaults file is missing {', '.join(missing)}")

        segment_key = keys["segment_size"]
        selected_segment = int(row["selected_segment_size"])
        current_segment = int(updated[segment_key])
        selected_mode = (
            str(row["selected_count_mode"])
            if "selected_count_mode" in row
            else None
        )
        mode_key = keys["count_mode"]
        current_mode = str(updated[mode_key])
        would_change = selected_segment != current_segment or (
            selected_mode is not None and selected_mode != current_mode
        )

        status = row.get("status")
        if would_change and status == "within_tolerance":
            ratio = row.get("default_over_selected")
            ratio_text = "unknown" if ratio is None else f"{float(ratio):.3f}x"
            skipped.append(
                "keeping current default within calibration tolerance for "
                f"{keys['segment_size']}/{keys['count_mode']}: {ratio_text}"
            )
            continue
        if would_change and status in {"missing_default_evidence", "no_current_default"}:
            skipped.append(
                "refusing recommendation without measured current-default evidence for "
                f"{keys['segment_size']}/{keys['count_mode']}: {status}"
            )
            continue

        source = row.get("source")
        stability = row.get("selected_sample_stability")
        effective_stability = row.get("selected_effective_sample_stability", stability)
        confirmation_status = row.get("selected_mode_confirmation_status")
        if (
            would_change
            and str(source) in {"external_mode_sweep", "external_high_offset_quick"}
            and confirmation_status not in (None, "confirmed")
        ):
            skipped.append(
                "refusing unconfirmed external recommendation for "
                f"{keys['segment_size']}/{keys['count_mode']}: {confirmation_status}"
            )
            continue
        if (
            would_change
            and str(source).startswith("external_")
            and effective_stability != "stable"
            and not allow_noisy
        ):
            skipped.append(
                "refusing noisy/unknown external recommendation for "
                f"{keys['segment_size']}/{keys['count_mode']}: {stability}"
            )
            continue

        updated[segment_key] = selected_segment
        if selected_segment != current_segment:
            changes.append(
                {
                    "key": segment_key,
                    "old": current_segment,
                    "new": selected_segment,
                    "low": int(row["low"]),
                    "high": int(row["high"]),
                    "source": source,
                    "stability": stability,
                }
            )
        if selected_mode is not None:
            if selected_mode not in VALID_COUNT_MODES:
                raise ValueError(f"invalid selected_count_mode for defaults: {selected_mode}")
            updated[mode_key] = selected_mode
            if selected_mode != current_mode:
                changes.append(
                    {
                        "key": mode_key,
                        "old": current_mode,
                        "new": selected_mode,
                        "low": int(row["low"]),
                        "high": int(row["high"]),
                        "source": source,
                        "stability": stability,
                    }
                )
    return updated, changes, skipped


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"prime-engine default apply failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
