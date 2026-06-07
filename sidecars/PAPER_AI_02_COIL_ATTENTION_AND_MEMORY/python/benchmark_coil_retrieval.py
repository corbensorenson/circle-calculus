"""Tiny coil-retrieval reachability benchmark sidecar.

This deterministic fixture compares a selected coil path against local-window,
wrong-stride, and full-attention oracle candidate sets for a known dependency
lag. It also runs a near-lag control where local attention should win. It is
not an attention-quality or model-quality claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_coil_retrieval.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_coil_retrieval_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic coil-retrieval reachability fixture.")
    parser.add_argument("--sequence-length", type=int, default=64)
    parser.add_argument("--query-count", type=int, default=64)
    parser.add_argument("--target-lag", type=int, default=21)
    parser.add_argument("--stride", type=int, default=7)
    parser.add_argument("--path-length", type=int, default=3)
    parser.add_argument("--local-window", type=int, default=8)
    parser.add_argument("--wrong-stride", type=int, default=5)
    parser.add_argument("--near-control-lag", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_coil_retrieval_benchmark(
        sequence_length=args.sequence_length,
        query_count=args.query_count,
        target_lag=args.target_lag,
        stride=args.stride,
        path_length=args.path_length,
        local_window=args.local_window,
        wrong_stride=args.wrong_stride,
        near_control_lag=args.near_control_lag,
    )
    print(
        "coil_retrieval "
        f"sequence_length={result.sequence_length} query_count={result.query_count} "
        f"target_lag={result.target_lag} stride={result.stride} "
        f"path_length={result.path_length} accuracy={result.coil_path_accuracy:.3f}"
    )
    print(f"local_window_baseline accuracy={result.local_window_accuracy:.3f}")
    print(f"wrong_stride_baseline accuracy={result.wrong_stride_accuracy:.3f}")
    print(f"full_attention_oracle accuracy={result.full_attention_accuracy:.3f}")
    print(
        "near_lag_control "
        f"lag={result.near_control_lag} "
        f"coil_path={result.near_control_coil_path_accuracy:.3f} "
        f"local_window={result.near_control_local_window_accuracy:.3f} "
        f"full_attention={result.near_control_full_attention_accuracy:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
