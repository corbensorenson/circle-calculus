"""Tiny token-level recurrence routing fixture.

This deterministic fixture records per-token loop budgets, active-token counts,
a selected middle-block range, coarse/fine resolution labels, and fixed/wrong
or over-loop controls. It is not a model-quality, reasoning-depth,
context-length, speed, memory, or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_token_level_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_token_level_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic token-level recurrence fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--token-count", type=int, default=32)
    parser.add_argument("--max-budget", type=int, default=4)
    parser.add_argument("--fixed-global-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--wrong-budget-shift", type=int, default=1)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    parser.add_argument("--selected-loop-block", type=int, nargs=2, metavar=("START", "STOP"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_token_level_recurrence_benchmark(
        loop_period=args.loop_period,
        token_count=args.token_count,
        max_budget=args.max_budget,
        fixed_global_budget=args.fixed_global_budget,
        over_loop_budget=args.over_loop_budget,
        wrong_budget_shift=args.wrong_budget_shift,
        overthink_tolerance=args.overthink_tolerance,
        selected_loop_block=args.selected_loop_block,
    )
    print(
        "token_level_recurrence "
        f"loop_period={result.loop_period} token_count={result.token_count} "
        f"selected_loop_block={result.selected_loop_block}"
    )
    print(f"token_budgets_sample={result.token_budgets[: min(12, len(result.token_budgets))]}")
    print(f"active_token_counts={result.active_token_counts}")
    print(f"resolution_levels={result.resolution_levels}")
    print(f"average_active_tokens={result.average_active_tokens:.3f}")
    print(f"token_level_routing accuracy={result.token_level_accuracy:.3f}")
    print(f"fixed_global_budget_baseline accuracy={result.fixed_global_budget_accuracy:.3f}")
    print(f"wrong_budget_control accuracy={result.wrong_budget_accuracy:.3f}")
    print(f"over_looped_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"nonperiodic_token_level accuracy={result.nonperiodic_token_level_accuracy:.3f}")
    print(f"nonperiodic_scalar_threshold_baseline accuracy={result.nonperiodic_scalar_threshold_accuracy:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
