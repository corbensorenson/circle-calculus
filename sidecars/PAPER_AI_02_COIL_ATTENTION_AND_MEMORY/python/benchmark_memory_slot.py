"""Tiny cyclic-memory benchmark sidecar.

This deterministic fixture compares memory-slot lookup against ordinary
constant and scalar-threshold baselines, then runs a nonperiodic control where
the threshold baseline should win. It is not a model-quality claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_memory_slot.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_memory_slot_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic cyclic-memory benchmark fixture.")
    parser.add_argument("--bank-size", type=int, default=8)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_memory_slot_benchmark(
        bank_size=args.bank_size,
        train_length=args.train_length,
        test_length=args.test_length,
    )
    print(
        "memory_slot "
        f"bank_size={result.bank_size} train={result.train_length} test={result.test_length} "
        f"accuracy={result.cyclic_memory_accuracy:.3f}"
    )
    print(f"constant_baseline accuracy={result.constant_accuracy:.3f}")
    print(f"scalar_threshold_baseline accuracy={result.scalar_threshold_accuracy:.3f}")
    print(
        "nonperiodic_control "
        f"memory_slot={result.nonperiodic_cyclic_memory_accuracy:.3f} "
        f"scalar_threshold={result.nonperiodic_scalar_threshold_accuracy:.3f}"
    )
    print(
        "collision_diagnostics "
        f"train_collision_count={result.train_collision_count} "
        f"max_train_slot_load={result.max_train_slot_load}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
