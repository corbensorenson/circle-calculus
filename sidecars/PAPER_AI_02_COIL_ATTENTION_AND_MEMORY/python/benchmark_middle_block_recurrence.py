"""Tiny middle-block recurrence fixture.

This deterministic fixture compares a selected middle-block recurrence schedule
with full-block, fixed-budget, wrong-block, and over-loop controls. It is not a
model-quality, reasoning, runtime, memory, or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_middle_block_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_middle_block_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic middle-block recurrence fixture.")
    parser.add_argument("--block-count", type=int, default=8)
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--selected-start", type=int, default=2)
    parser.add_argument("--selected-stop", type=int, default=5)
    parser.add_argument("--wrong-start", type=int, default=0)
    parser.add_argument("--wrong-stop", type=int, default=2)
    parser.add_argument("--max-budget", type=int, default=4)
    parser.add_argument("--fixed-loop-budget", type=int, default=4)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_middle_block_recurrence_benchmark(
        block_count=args.block_count,
        sample_count=args.sample_count,
        loop_period=args.loop_period,
        selected_loop_block=(args.selected_start, args.selected_stop),
        wrong_loop_block=(args.wrong_start, args.wrong_stop),
        max_budget=args.max_budget,
        fixed_loop_budget=args.fixed_loop_budget,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "middle_block_recurrence "
        f"block_count={result.block_count} sample_count={result.sample_count} "
        f"loop_period={result.loop_period}"
    )
    print(f"selected_loop_block={result.selected_loop_block}")
    print(f"wrong_loop_block={result.wrong_loop_block}")
    print(f"selected_block_indices={result.selected_block_indices}")
    print(f"required_block_sample={result.required_block_sample}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"selected_middle_block accuracy={result.selected_middle_block_accuracy:.3f}")
    print(f"full_block_phase_budget accuracy={result.full_block_phase_budget_accuracy:.3f}")
    print(f"fixed_loop_budget_control accuracy={result.fixed_loop_budget_accuracy:.3f}")
    print(f"wrong_block_control accuracy={result.wrong_block_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"average_selected_block_passes={result.average_selected_block_passes:.3f}")
    print(f"average_full_block_passes={result.average_full_block_passes:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
