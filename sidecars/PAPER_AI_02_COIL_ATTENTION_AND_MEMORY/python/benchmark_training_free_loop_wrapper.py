"""Tiny training-free loop-wrapper fixture.

This deterministic fixture uses circular phase as a fixed loop-budget prior
and compares it with single-pass, fixed-budget, wrong-period, over-loop, and
nonperiodic scalar-threshold controls. It is not a model-quality, reasoning,
context-length, speed, memory, or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_training_free_loop_wrapper.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_training_free_loop_wrapper_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic training-free loop-wrapper fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--max-loops", type=int, default=4)
    parser.add_argument("--fixed-loop-budget", type=int, default=2)
    parser.add_argument("--wrong-loop-period", type=int, default=3)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    parser.add_argument("--backend", choices=("cpu", "mlx"), default="cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_training_free_loop_wrapper_benchmark(
        loop_period=args.loop_period,
        sample_count=args.sample_count,
        max_loops=args.max_loops,
        fixed_loop_budget=args.fixed_loop_budget,
        wrong_loop_period=args.wrong_loop_period,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
        backend=args.backend,
    )
    print(
        "training_free_loop_wrapper "
        f"loop_period={result.loop_period} sample_count={result.sample_count} "
        f"max_loops={result.max_loops} backend={result.backend}"
    )
    print(f"phase_budgets_sample={result.phase_budgets[: min(12, len(result.phase_budgets))]}")
    print(f"active_sample_counts={result.active_sample_counts}")
    print(f"budget_histogram={result.budget_histogram}")
    print(f"average_phase_budget={result.average_phase_budget:.3f}")
    print(f"single_pass_baseline accuracy={result.single_pass_accuracy:.3f}")
    print(f"fixed_loop_baseline accuracy={result.fixed_loop_accuracy:.3f}")
    print(f"training_free_phase_budget accuracy={result.training_free_phase_budget_accuracy:.3f}")
    print(f"wrong_period_budget_control accuracy={result.wrong_period_budget_accuracy:.3f}")
    print(f"over_loop_no_exit_control accuracy={result.over_loop_no_exit_accuracy:.3f}")
    print(f"nonperiodic_phase_budget accuracy={result.nonperiodic_phase_budget_accuracy:.3f}")
    print(f"nonperiodic_scalar_threshold_baseline accuracy={result.nonperiodic_scalar_threshold_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
