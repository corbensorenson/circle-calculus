"""Tiny learned-feature baseline sidecar for Circle AI.

This deterministic fixture compares cyclic phase features with ordinary small
baselines: scalar threshold, learned absolute-position lookup, and wrong-period
phase lookup. It is not a model-quality claim.

Example:
    python sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_learned_feature_baselines.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_feature_baseline_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned-feature baseline fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--wrong-period", type=int, default=7)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_learned_feature_baseline_benchmark(
        period=args.period,
        wrong_period=args.wrong_period,
        train_length=args.train_length,
        test_length=args.test_length,
    )
    print(
        "learned_feature_baselines "
        f"period={result.period} wrong_period={result.wrong_period} "
        f"train={result.train_length} test={result.test_length}"
    )
    print(f"periodic cyclic_feature accuracy={result.periodic_cyclic_feature_accuracy:.3f}")
    print(f"periodic dense_scalar_baseline accuracy={result.periodic_dense_scalar_accuracy:.3f}")
    print(f"periodic learned_position_baseline accuracy={result.periodic_learned_position_accuracy:.3f}")
    print(f"periodic wrong_period_baseline accuracy={result.periodic_wrong_period_accuracy:.3f}")
    print(f"nonperiodic cyclic_feature accuracy={result.nonperiodic_cyclic_feature_accuracy:.3f}")
    print(f"nonperiodic dense_scalar_baseline accuracy={result.nonperiodic_dense_scalar_accuracy:.3f}")
    print(f"nonperiodic learned_position_baseline accuracy={result.nonperiodic_learned_position_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
