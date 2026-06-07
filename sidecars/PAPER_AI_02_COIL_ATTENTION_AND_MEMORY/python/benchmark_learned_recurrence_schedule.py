"""Tiny learned recurrence-schedule fixture.

This deterministic fixture fits a phase-to-loop-budget lookup table from
training examples and compares it with fixed-budget, wrong-period, and over-loop
controls. It is not a model-quality, reasoning, runtime, memory, context-length,
or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_recurrence_schedule.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_recurrence_schedule_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned recurrence-schedule fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--wrong-period", type=int, default=3)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--fixed-loop-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_learned_recurrence_schedule_benchmark(
        loop_period=args.loop_period,
        wrong_period=args.wrong_period,
        train_length=args.train_length,
        test_length=args.test_length,
        fixed_loop_budget=args.fixed_loop_budget,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "learned_recurrence_schedule "
        f"loop_period={result.loop_period} wrong_period={result.wrong_period} "
        f"train_length={result.train_length} test_length={result.test_length}"
    )
    print(f"learned_budget_lookup={result.learned_budget_lookup}")
    print(f"wrong_period_budget_lookup={result.wrong_period_budget_lookup}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"learned_budget_sample={result.learned_budget_sample}")
    print(f"learned_phase_router accuracy={result.learned_phase_router_accuracy:.3f}")
    print(f"fixed_loop_budget_baseline accuracy={result.fixed_loop_budget_accuracy:.3f}")
    print(f"wrong_period_router_control accuracy={result.wrong_period_router_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
