"""Tiny harmonic/Fourier feature baseline sidecar for Circle AI.

This deterministic fixture compares a cyclic phase lookup with a correct
sine/cosine feature lookup, a wrong-frequency sine/cosine lookup, a scalar
threshold baseline, and an absolute-position lookup. It is not a
neural-network, RoPE-quality, or speed claim.

Example:
    python sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_harmonic_feature_baselines.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_harmonic_feature_baseline_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic harmonic-feature baseline fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--wrong-period", type=int, default=7)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_harmonic_feature_baseline_benchmark(
        period=args.period,
        wrong_period=args.wrong_period,
        train_length=args.train_length,
        test_length=args.test_length,
    )
    print(
        "harmonic_feature_baselines "
        f"period={result.period} wrong_period={result.wrong_period} "
        f"train={result.train_length} test={result.test_length} "
        f"observed_features={result.observed_feature_count}"
    )
    print(f"periodic cyclic_phase accuracy={result.cyclic_phase_accuracy:.3f}")
    print(f"periodic harmonic_feature accuracy={result.harmonic_feature_accuracy:.3f}")
    print(f"periodic wrong_harmonic_baseline accuracy={result.wrong_harmonic_accuracy:.3f}")
    print(f"periodic scalar_threshold_baseline accuracy={result.scalar_threshold_accuracy:.3f}")
    print(f"periodic learned_position_baseline accuracy={result.learned_position_accuracy:.3f}")
    print(f"nonperiodic harmonic_feature accuracy={result.nonperiodic_harmonic_accuracy:.3f}")
    print(f"nonperiodic scalar_threshold_baseline accuracy={result.nonperiodic_scalar_threshold_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
