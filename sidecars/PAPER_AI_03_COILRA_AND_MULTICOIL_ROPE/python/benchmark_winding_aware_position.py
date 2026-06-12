"""Tiny winding-aware position benchmark sidecar.

This deterministic fixture compares residue-plus-winding position features
against residue-only, wrong-period, learned absolute-position, and scalar
threshold baselines. It also runs a nonperiodic control where the scalar
threshold baseline should win. It is not a RoPE, long-context, language-model,
quality, or speed claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_winding_aware_position.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_winding_aware_position_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic winding-aware position fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--winding-period", type=int, default=4)
    parser.add_argument("--wrong-period", type=int, default=7)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_winding_aware_position_benchmark(
        period=args.period,
        winding_period=args.winding_period,
        wrong_period=args.wrong_period,
        train_length=args.train_length,
        test_length=args.test_length,
    )
    print(
        "winding_aware_position "
        f"period={result.period} winding_period={result.winding_period} "
        f"wrong_period={result.wrong_period} cycle={result.cycle_length} "
        f"observed_features={result.observed_winding_feature_count} "
        f"alias_collisions={result.alias_collision_count}"
    )
    print(f"winding_position accuracy={result.winding_position_accuracy:.3f}")
    print(f"residue_only_baseline accuracy={result.residue_only_accuracy:.3f}")
    print(f"wrong_period_winding_baseline accuracy={result.wrong_period_winding_accuracy:.3f}")
    print(f"learned_absolute_position_baseline accuracy={result.learned_absolute_position_accuracy:.3f}")
    print(f"scalar_threshold_baseline accuracy={result.scalar_threshold_accuracy:.3f}")
    print(
        "nonperiodic_control "
        f"winding_position={result.nonperiodic_winding_accuracy:.3f} "
        f"scalar_threshold={result.nonperiodic_scalar_threshold_accuracy:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
