#!/usr/bin/env python3
"""Run the synthetic circle-phase feature probe."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from circle_math.applications.phase_probe import CirclePhaseProbeResult, run_circle_phase_probe


def _text_report(result: CirclePhaseProbeResult) -> str:
    lines = [
        (
            "circle_phase_probe=READY "
            f"period={result.period} backend={result.backend_used} "
            f"train={result.train_length} test={result.test_length}"
        ),
        (
            "baseline=raw_position_linear "
            f"train_accuracy={result.baseline_train_accuracy:.6f} "
            f"test_accuracy={result.baseline_test_accuracy:.6f}"
        ),
        (
            "phase=circle_sin_cos_linear "
            f"train_accuracy={result.phase_train_accuracy:.6f} "
            f"test_accuracy={result.phase_test_accuracy:.6f}"
        ),
        f"target_rule={result.target_rule}",
        f"non_claimed={result.non_claims}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--train-cycles", type=int, default=4)
    parser.add_argument("--test-cycles", type=int, default=2)
    parser.add_argument("--backend", choices=("auto", "numpy", "mlx"), default="auto")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--json-out", help="Optional path to write the JSON report.")
    args = parser.parse_args()

    result = run_circle_phase_probe(
        period=args.period,
        train_cycles=args.train_cycles,
        test_cycles=args.test_cycles,
        backend=args.backend,
    )
    payload = result.to_dict()
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_text_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
