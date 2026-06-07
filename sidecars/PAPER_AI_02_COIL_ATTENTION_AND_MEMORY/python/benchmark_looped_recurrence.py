"""Tiny looped/recursive transformer recurrence-schedule fixture.

This deterministic fixture compares single-pass, fixed-loop, adaptive-exit,
recurrent-memory, sparse phase-router, and over-looped schedule controls. It
also runs a nonperiodic scalar-threshold control. It is not a model-quality,
reasoning-depth, context-length, speed, or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_looped_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_looped_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic looped-recurrence schedule fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--fixed-loop-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=1)
    parser.add_argument("--sparse-phase-router-step", type=int, action="append", dest="router_steps")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_looped_recurrence_benchmark(
        loop_period=args.loop_period,
        train_length=args.train_length,
        test_length=args.test_length,
        fixed_loop_budget=args.fixed_loop_budget,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
        sparse_phase_router_steps=args.router_steps,
    )
    print(
        "looped_recurrence "
        f"loop_period={result.loop_period} train_length={result.train_length} "
        f"test_length={result.test_length} observed_exit_steps={result.observed_exit_steps}"
    )
    print(f"single_pass_baseline accuracy={result.single_pass_accuracy:.3f}")
    print(f"fixed_loop_baseline accuracy={result.fixed_loop_accuracy:.3f}")
    print(f"adaptive_exit accuracy={result.adaptive_exit_accuracy:.3f}")
    print(f"recurrent_memory_baseline accuracy={result.recurrent_memory_accuracy:.3f}")
    print(
        "sparse_phase_router_baseline "
        f"steps={result.sparse_phase_router_steps} accuracy={result.sparse_phase_router_accuracy:.3f}"
    )
    print(f"over_looped_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"nonperiodic_loop_phase accuracy={result.nonperiodic_loop_phase_accuracy:.3f}")
    print(f"nonperiodic_dense_threshold_baseline accuracy={result.nonperiodic_dense_threshold_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
