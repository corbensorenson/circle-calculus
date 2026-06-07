"""Tiny learned multi-resolution recurrence fixture.

This deterministic fixture fits phase lookups for loop budget and coarse/fine
resolution labels, then compares the learned route with single-resolution,
fixed-budget, wrong-period, and over-loop controls. It is not a model-quality,
reasoning, runtime, memory, or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_multi_resolution_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_multi_resolution_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned multi-resolution fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--wrong-budget-period", type=int, default=3)
    parser.add_argument("--wrong-resolution-period", type=int, default=3)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--max-budget", type=int, default=4)
    parser.add_argument("--fixed-loop-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_learned_multi_resolution_recurrence_benchmark(
        loop_period=args.loop_period,
        wrong_budget_period=args.wrong_budget_period,
        wrong_resolution_period=args.wrong_resolution_period,
        train_length=args.train_length,
        test_length=args.test_length,
        max_budget=args.max_budget,
        fixed_loop_budget=args.fixed_loop_budget,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "learned_multi_resolution_recurrence "
        f"loop_period={result.loop_period} train_length={result.train_length} "
        f"test_length={result.test_length}"
    )
    print(f"learned_budget_lookup={result.learned_budget_lookup}")
    print(f"learned_resolution_lookup={result.learned_resolution_lookup}")
    print(f"wrong_budget_period_lookup={result.wrong_budget_period_lookup}")
    print(f"wrong_resolution_period_lookup={result.wrong_resolution_period_lookup}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"learned_budget_sample={result.learned_budget_sample}")
    print(f"required_resolution_sample={result.required_resolution_sample}")
    print(f"learned_resolution_sample={result.learned_resolution_sample}")
    print(f"active_sample_counts={result.active_sample_counts}")
    print(f"learned_multi_resolution_router accuracy={result.learned_multi_resolution_router_accuracy:.3f}")
    print(f"single_resolution_coarse accuracy={result.single_resolution_coarse_accuracy:.3f}")
    print(f"single_resolution_fine accuracy={result.single_resolution_fine_accuracy:.3f}")
    print(f"fixed_budget_control accuracy={result.fixed_budget_accuracy:.3f}")
    print(f"wrong_budget_period_control accuracy={result.wrong_budget_period_accuracy:.3f}")
    print(f"wrong_resolution_period_control accuracy={result.wrong_resolution_period_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"average_active_samples={result.average_active_samples:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
