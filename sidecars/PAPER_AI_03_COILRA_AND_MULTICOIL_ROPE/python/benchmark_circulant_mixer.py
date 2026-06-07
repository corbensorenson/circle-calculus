"""Tiny circulant-mixer validation sidecar.

This deterministic fixture compares circular-convolution output against the
equivalent dense circulant matrix baseline, then reports a wrong-shift control
and dense-vs-circulant parameter counts. It is not a model-quality, speed,
memory, training-stability, or hardware-efficiency claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_circulant_mixer.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_circulant_mixer_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic circulant-mixer fixture.")
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--wrong-shift", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_circulant_mixer_benchmark(period=args.period, wrong_shift=args.wrong_shift)
    print(f"circulant_mixer period={result.period}")
    print(f"dense_circulant_baseline parameters={result.dense_parameters}")
    print(
        "circulant_baseline "
        f"parameters={result.circulant_parameters} ratio_to_dense={result.parameter_ratio:.6f}"
    )
    print(f"max_abs_dense_delta={result.max_abs_dense_delta}")
    print(f"wrong_shift_mismatch_count={result.wrong_shift_mismatch_count}")
    print(f"input_values={result.input_values}")
    print(f"kernel_values={result.kernel_values}")
    print(f"circulant_output={result.circulant_output}")
    print(f"dense_output={result.dense_output}")
    print(f"wrong_shift_output={result.wrong_shift_output}")
    print(result.note)


if __name__ == "__main__":
    main()
