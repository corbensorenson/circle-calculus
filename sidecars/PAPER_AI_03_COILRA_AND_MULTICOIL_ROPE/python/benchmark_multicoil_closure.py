"""Tiny MultiCoil common-cycle closure sidecar.

This deterministic fixture compares a two-period phase pair against the
proof-backed product cycle, the ordinary lcm cycle, and a wrong-shift control.
It is positional bookkeeping only, not a RoPE, language-model, quality, or
speed claim.

Example:
    python sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_multicoil_closure.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_multicoil_closure_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic MultiCoil closure fixture.")
    parser.add_argument("--period-a", type=int, default=5)
    parser.add_argument("--period-b", type=int, default=7)
    parser.add_argument("--position", type=int, default=42)
    parser.add_argument("--wrong-shift", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_multicoil_closure_benchmark(
        period_a=args.period_a,
        period_b=args.period_b,
        position=args.position,
        wrong_shift=args.wrong_shift,
    )
    print(
        "multicoil_closure "
        f"period_a={result.period_a} period_b={result.period_b} position={result.position}"
    )
    print(f"phase={result.phase}")
    print(f"product_cycle={result.product_cycle}")
    print(f"lcm_cycle={result.lcm_cycle}")
    print(f"product_equals_lcm={result.product_equals_lcm}")
    print(f"product_shifted_phase={result.product_shifted_phase}")
    print(f"lcm_shifted_phase={result.lcm_shifted_phase}")
    print(f"product_closes={result.product_closes}")
    print(f"lcm_closes={result.lcm_closes}")
    print(f"wrong_shift={result.wrong_shift}")
    print(f"wrong_shifted_phase={result.wrong_shifted_phase}")
    print(f"wrong_shift_mismatch={result.wrong_shift_mismatch}")
    print(result.note)


if __name__ == "__main__":
    main()
