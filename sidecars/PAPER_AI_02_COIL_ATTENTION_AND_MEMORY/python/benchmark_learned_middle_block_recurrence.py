"""Tiny learned middle-block recurrence fixture.

This deterministic fixture fits separate phase lookups for the required middle
block and recurrence budget, then compares the learned route with selected-band,
full-block, fixed-budget, wrong-period, wrong-band, and over-loop controls. It
is not a model-quality, reasoning, runtime, memory, or parameter-efficiency
claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_middle_block_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_middle_block_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned middle-block fixture.")
    parser.add_argument("--block-count", type=int, default=8)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--wrong-block-period", type=int, default=2)
    parser.add_argument("--wrong-budget-period", type=int, default=3)
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
    result = run_learned_middle_block_recurrence_benchmark(
        block_count=args.block_count,
        train_length=args.train_length,
        test_length=args.test_length,
        loop_period=args.loop_period,
        wrong_block_period=args.wrong_block_period,
        wrong_budget_period=args.wrong_budget_period,
        selected_loop_block=(args.selected_start, args.selected_stop),
        wrong_loop_block=(args.wrong_start, args.wrong_stop),
        max_budget=args.max_budget,
        fixed_loop_budget=args.fixed_loop_budget,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "learned_middle_block_recurrence "
        f"block_count={result.block_count} train_length={result.train_length} "
        f"test_length={result.test_length} loop_period={result.loop_period}"
    )
    print(f"selected_loop_block={result.selected_loop_block}")
    print(f"selected_block_indices={result.selected_block_indices}")
    print(f"learned_block_lookup={result.learned_block_lookup}")
    print(f"learned_budget_lookup={result.learned_budget_lookup}")
    print(f"wrong_block_period_lookup={result.wrong_block_period_lookup}")
    print(f"wrong_budget_period_lookup={result.wrong_budget_period_lookup}")
    print(f"required_block_sample={result.required_block_sample}")
    print(f"learned_block_sample={result.learned_block_sample}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"learned_budget_sample={result.learned_budget_sample}")
    print(f"active_sample_counts={result.active_sample_counts}")
    print(f"learned_middle_block_router accuracy={result.learned_middle_block_router_accuracy:.3f}")
    print(f"selected_band_phase_budget accuracy={result.selected_band_phase_budget_accuracy:.3f}")
    print(f"full_block_phase_budget accuracy={result.full_block_phase_budget_accuracy:.3f}")
    print(f"fixed_loop_budget_control accuracy={result.fixed_loop_budget_accuracy:.3f}")
    print(f"wrong_block_period_control accuracy={result.wrong_block_period_accuracy:.3f}")
    print(f"wrong_budget_period_control accuracy={result.wrong_budget_period_accuracy:.3f}")
    print(f"wrong_loop_block_control accuracy={result.wrong_loop_block_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"average_learned_block_passes={result.average_learned_block_passes:.3f}")
    print(f"average_selected_band_passes={result.average_selected_band_passes:.3f}")
    print(f"average_full_block_passes={result.average_full_block_passes:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
