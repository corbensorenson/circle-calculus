"""Tiny adapter-block benchmark sidecar.

This deterministic fixture compares adapter-block lookup against ordinary
constant and scalar-threshold baselines, then runs a nonperiodic control where
the threshold baseline should win. It is not a model-quality claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_adapter_block.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_adapter_block_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic adapter-block benchmark fixture.")
    parser.add_argument("--block-size", type=int, default=8)
    parser.add_argument("--train-channels", type=int, default=64)
    parser.add_argument("--test-channels", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_adapter_block_benchmark(
        block_size=args.block_size,
        train_channels=args.train_channels,
        test_channels=args.test_channels,
    )
    print(
        "adapter_block "
        f"block_size={result.block_size} train={result.train_channels} test={result.test_channels} "
        f"accuracy={result.adapter_block_accuracy:.3f}"
    )
    print(f"constant_baseline accuracy={result.constant_accuracy:.3f}")
    print(f"scalar_channel_threshold_baseline accuracy={result.scalar_channel_threshold_accuracy:.3f}")
    print(
        "nonperiodic_control "
        f"adapter_block={result.nonperiodic_adapter_block_accuracy:.3f} "
        f"scalar_threshold={result.nonperiodic_scalar_threshold_accuracy:.3f}"
    )
    print(
        "collision_diagnostics "
        f"train_collision_count={result.train_collision_count} "
        f"max_train_block_load={result.max_train_block_load}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
