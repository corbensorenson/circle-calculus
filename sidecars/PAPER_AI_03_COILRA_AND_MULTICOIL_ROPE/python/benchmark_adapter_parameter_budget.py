"""Tiny adapter parameter-budget benchmark sidecar.

This deterministic fixture compares dense per-channel, LoRA-style low-rank,
and block-cyclic shared-table parameter counts, then reports alias/load
diagnostics. It is not a model-quality, fine-tuning, speed, memory, or
hardware-efficiency claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_adapter_parameter_budget.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_adapter_parameter_budget_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic adapter parameter-budget fixture.")
    parser.add_argument("--channel-count", type=int, default=128)
    parser.add_argument("--block-size", type=int, default=8)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--parameters-per-channel", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_adapter_parameter_budget_benchmark(
        channel_count=args.channel_count,
        block_size=args.block_size,
        rank=args.rank,
        parameters_per_channel=args.parameters_per_channel,
    )
    print(
        "adapter_parameter_budget "
        f"channels={result.channel_count} block_size={result.block_size} "
        f"rank={result.rank} params_per_channel={result.parameters_per_channel}"
    )
    print(f"dense_adapter_baseline parameters={result.dense_adapter_parameters}")
    print(
        "lora_baseline "
        f"parameters={result.lora_parameters} ratio_to_dense={result.lora_to_dense_ratio:.6f}"
    )
    print(
        "block_cyclic_baseline "
        f"parameters={result.block_cyclic_parameters} ratio_to_dense={result.block_to_dense_ratio:.6f}"
    )
    print(
        "alias_diagnostics "
        f"channel_collision_count={result.channel_collision_count} "
        f"max_block_load={result.max_block_load}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
