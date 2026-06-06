"""Tiny phase-channel benchmark sidecar.

This is a deterministic harness for the Circle AI phase-channel seed. It is
not a model-quality claim.

Examples:
    python sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py
    python sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py --backend mlx
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_phase_channel_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic phase-channel benchmark fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--backend", choices=("cpu", "mlx"), default="cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_phase_channel_benchmark(
        period=args.period,
        train_length=args.train_length,
        test_length=args.test_length,
        backend=args.backend,
    )
    print(
        "phase_channel "
        f"period={result.period} train={result.train_length} test={result.test_length} "
        f"backend={result.backend} accuracy={result.phase_channel_accuracy:.3f}"
    )
    print(f"constant_baseline accuracy={result.constant_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
