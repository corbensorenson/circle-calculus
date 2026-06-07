"""Tiny MultiCoil/RoPE-style phase benchmark sidecar.

This deterministic fixture compares combined-period phase lookup against a
single-period phase lookup, a constant baseline, and a scalar-threshold
baseline. It also runs a nonperiodic control where the threshold baseline
should win. It is not a RoPE or model-quality claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_multicoil_rope.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_multicoil_rope_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic MultiCoil/RoPE-style benchmark fixture.")
    parser.add_argument("--periods", type=int, nargs="+", default=(5, 7))
    parser.add_argument("--train-length", type=int, default=140)
    parser.add_argument("--test-length", type=int, default=70)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_multicoil_rope_benchmark(
        periods=tuple(args.periods),
        train_length=args.train_length,
        test_length=args.test_length,
    )
    period_text = ",".join(str(period) for period in result.periods)
    print(
        "multicoil_rope "
        f"periods={period_text} cycle={result.cycle_length} "
        f"observed_phases={result.observed_phase_count} "
        f"train={result.train_length} test={result.test_length} "
        f"accuracy={result.multicoil_phase_accuracy:.3f}"
    )
    print(f"single_period_phase_baseline accuracy={result.single_period_phase_accuracy:.3f}")
    print(f"constant_baseline accuracy={result.constant_accuracy:.3f}")
    print(f"scalar_threshold_baseline accuracy={result.scalar_threshold_accuracy:.3f}")
    print(
        "nonperiodic_control "
        f"multicoil_phase={result.nonperiodic_multicoil_phase_accuracy:.3f} "
        f"scalar_threshold={result.nonperiodic_scalar_threshold_accuracy:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
