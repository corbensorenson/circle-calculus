"""Tiny block-cyclic mixer validation sidecar.

This deterministic fixture compares a block-cyclic mixer against the dense
matrix it represents, then reports a wrong-row-shift control and alias/load
diagnostics. It is not a model-quality, speed, memory, training-stability, or
hardware-efficiency claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_block_cyclic_mixer.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_block_cyclic_mixer_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic block-cyclic mixer fixture.")
    parser.add_argument("--channel-count", type=int, default=16)
    parser.add_argument("--block-size", type=int, default=4)
    parser.add_argument("--wrong-row-shift", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_block_cyclic_mixer_benchmark(
        channel_count=args.channel_count,
        block_size=args.block_size,
        wrong_row_shift=args.wrong_row_shift,
    )
    print(
        "block_cyclic_mixer "
        f"channel_count={result.channel_count} block_size={result.block_size} "
        f"wrong_row_shift={args.wrong_row_shift}"
    )
    print(f"dense_matrix_baseline parameters={result.dense_parameters}")
    print(
        "block_cyclic_baseline "
        f"parameters={result.block_cyclic_parameters} ratio_to_dense={result.parameter_ratio:.6f}"
    )
    print(f"max_abs_dense_delta={result.max_abs_dense_delta}")
    print(f"wrong_shift_mismatch_count={result.wrong_shift_mismatch_count}")
    print(f"cell_collision_count={result.cell_collision_count}")
    print(f"max_cell_load={result.max_cell_load}")
    print(f"input_values={result.input_values}")
    print(f"block_kernel={result.block_kernel}")
    print(f"block_cyclic_output={result.block_cyclic_output}")
    print(f"dense_output={result.dense_output}")
    print(f"wrong_row_shift_output={result.wrong_row_shift_output}")
    print(result.note)


if __name__ == "__main__":
    main()
