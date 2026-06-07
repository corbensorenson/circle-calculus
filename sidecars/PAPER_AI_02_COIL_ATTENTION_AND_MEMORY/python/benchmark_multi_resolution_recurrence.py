"""Tiny multi-resolution recurrence fixture.

This deterministic fixture compares a phase-routed multi-resolution recurrence
schedule with single-resolution, fixed-budget, wrong-resolution, and over-loop
controls. It is not a model-quality, reasoning, runtime, memory, context-length,
or parameter-efficiency claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_multi_resolution_recurrence.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_multi_resolution_recurrence_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic multi-resolution recurrence fixture.")
    parser.add_argument("--loop-period", type=int, default=4)
    parser.add_argument("--sample-count", type=int, default=32)
    parser.add_argument("--max-budget", type=int, default=4)
    parser.add_argument("--fixed-loop-budget", type=int, default=4)
    parser.add_argument("--wrong-resolution-shift", type=int, default=1)
    parser.add_argument("--over-loop-budget", type=int, default=8)
    parser.add_argument("--overthink-tolerance", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_multi_resolution_recurrence_benchmark(
        loop_period=args.loop_period,
        sample_count=args.sample_count,
        max_budget=args.max_budget,
        fixed_loop_budget=args.fixed_loop_budget,
        wrong_resolution_shift=args.wrong_resolution_shift,
        over_loop_budget=args.over_loop_budget,
        overthink_tolerance=args.overthink_tolerance,
    )
    print(
        "multi_resolution_recurrence "
        f"loop_period={result.loop_period} sample_count={result.sample_count} "
        f"max_budget={result.max_budget}"
    )
    print(f"resolution_levels={result.resolution_levels}")
    print(f"required_budget_sample={result.required_budget_sample}")
    print(f"required_resolution_sample={result.required_resolution_sample}")
    print(f"active_sample_counts={result.active_sample_counts}")
    print(f"multi_resolution accuracy={result.multi_resolution_accuracy:.3f}")
    print(f"single_resolution_coarse_baseline accuracy={result.single_resolution_coarse_accuracy:.3f}")
    print(f"single_resolution_fine_baseline accuracy={result.single_resolution_fine_accuracy:.3f}")
    print(f"fixed_budget_baseline accuracy={result.fixed_budget_accuracy:.3f}")
    print(f"wrong_resolution_control accuracy={result.wrong_resolution_accuracy:.3f}")
    print(f"over_loop_control accuracy={result.over_looped_accuracy:.3f}")
    print(f"average_active_samples={result.average_active_samples:.3f}")
    print(result.note)


if __name__ == "__main__":
    main()
