"""Tiny learned token-level recurrence routing fixture.

This deterministic fixture fits a phase-to-budget lookup table from training
tokens and compares held-out token routing against fixed-budget, wrong-period,
shifted-budget, over-loop, and nonperiodic scalar controls. It is not a
model-quality, reasoning, runtime, memory, context-length, or
parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_token_level_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_token_level_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned token-level recurrence fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--wrong-period", type=int, default=3)
    parser.add_argument("--train-token-count", type=int, default=64)
    parser.add_argument("--test-token-count", type=int, default=32)
    parser.add_argument("--max-budget", type=int, default=4)
    parser.add_argument("--fixed-global-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--wrong-budget-shift", type=int, default=1)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_learned_token_level_recurrence_benchmark(
        loop_period=args.loop_period,
        wrong_period=args.wrong_period,
        train_token_count=args.train_token_count,
        test_token_count=args.test_token_count,
        max_budget=args.max_budget,
        fixed_global_budget=args.fixed_global_budget,
        over_loop_budget=args.over_loop_budget,
        wrong_budget_shift=args.wrong_budget_shift,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "learned_token_level_recurrence "
        f"loop_period={result.loop_period} wrong_period={result.wrong_period} "
        f"train_token_count={result.train_token_count} test_token_count={result.test_token_count}"
    )
    print(f"learned_budget_lookup={result.learned_budget_lookup}")
    print(f"wrong_period_budget_lookup={result.wrong_period_budget_lookup}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"learned_budget_sample={result.learned_budget_sample}")
    print(f"wrong_shift_budget_sample={result.wrong_shift_budget_sample}")
    print(f"active_token_counts={result.active_token_counts}")
    print(f"learned_token_router accuracy={result.learned_token_router_accuracy:.3f}")
    print(f"fixed_global_budget_baseline accuracy={result.fixed_global_budget_accuracy:.3f}")
    print(f"wrong_period_router_control accuracy={result.wrong_period_router_accuracy:.3f}")
    print(f"wrong_shift_control accuracy={result.wrong_shift_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"nonperiodic_phase_lookup_control accuracy={result.nonperiodic_phase_lookup_accuracy:.3f}")
    print(f"nonperiodic_scalar_threshold_baseline accuracy={result.nonperiodic_scalar_threshold_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
