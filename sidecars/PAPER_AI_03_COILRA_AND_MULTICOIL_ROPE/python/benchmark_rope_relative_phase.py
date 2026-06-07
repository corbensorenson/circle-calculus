"""Tiny RoPE-style relative phase benchmark sidecar.

This deterministic fixture compares a correct-period relative phase lookup
against wrong-period, query-only, and scalar-threshold baselines. It also runs
a nonperiodic query-threshold control where scalar structure should win. It is
not a standard RoPE, language-model, quality, or speed claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_rope_relative_phase.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_rope_relative_phase_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic RoPE-style relative phase fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--wrong-period", type=int, default=7)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_rope_relative_phase_benchmark(
        period=args.period,
        wrong_period=args.wrong_period,
        train_length=args.train_length,
        test_length=args.test_length,
    )
    print(
        "rope_relative_phase "
        f"period={result.period} wrong_period={result.wrong_period} "
        f"train={result.train_length} test={result.test_length} "
        f"observed_features={result.observed_relative_feature_count}"
    )
    print(f"positive_lags={','.join(str(lag) for lag in result.positive_lags)}")
    print(f"relative_phase accuracy={result.rope_relative_accuracy:.3f}")
    print(f"wrong_period_rope_baseline accuracy={result.wrong_period_rope_accuracy:.3f}")
    print(f"query_position_baseline accuracy={result.query_position_accuracy:.3f}")
    print(f"scalar_query_threshold_baseline accuracy={result.scalar_query_threshold_accuracy:.3f}")
    print(
        "nonperiodic_control "
        f"relative_phase={result.nonperiodic_rope_relative_accuracy:.3f} "
        f"scalar_query_threshold={result.nonperiodic_scalar_query_threshold_accuracy:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
