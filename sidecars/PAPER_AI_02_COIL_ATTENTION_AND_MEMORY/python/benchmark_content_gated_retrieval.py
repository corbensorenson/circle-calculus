"""Tiny content-gated coil/local retrieval benchmark sidecar.

This deterministic fixture compares a content-gated route against static
coil, static local, wrong-gate, union, and full-attention candidate baselines.
It measures candidate-set reachability and candidate budget only. It is not an
attention-quality, model-quality, memory-scaling, context-length, or speed
claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_content_gated_retrieval.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_content_gated_retrieval_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic content-gated retrieval fixture.")
    parser.add_argument("--sequence-length", type=int, default=64)
    parser.add_argument("--query-count", type=int, default=64)
    parser.add_argument("--long-target-lag", type=int, default=21)
    parser.add_argument("--near-target-lag", type=int, default=3)
    parser.add_argument("--stride", type=int, default=7)
    parser.add_argument("--path-length", type=int, default=3)
    parser.add_argument("--local-window", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_content_gated_retrieval_benchmark(
        sequence_length=args.sequence_length,
        query_count=args.query_count,
        long_target_lag=args.long_target_lag,
        near_target_lag=args.near_target_lag,
        stride=args.stride,
        path_length=args.path_length,
        local_window=args.local_window,
    )
    print(
        "content_gated_retrieval "
        f"sequence_length={result.sequence_length} query_count={result.query_count} "
        f"long_lag={result.long_target_lag} near_lag={result.near_target_lag}"
    )
    print(f"content_gated accuracy={result.content_gated_accuracy:.3f}")
    print(f"static_coil_baseline accuracy={result.static_coil_accuracy:.3f}")
    print(f"static_local_baseline accuracy={result.static_local_accuracy:.3f}")
    print(f"wrong_gate_control accuracy={result.wrong_gate_accuracy:.3f}")
    print(f"union_candidate_baseline accuracy={result.union_candidate_accuracy:.3f}")
    print(f"full_attention_oracle accuracy={result.full_attention_accuracy:.3f}")
    print(
        "candidate_budget "
        f"gated={result.average_gated_candidate_count:.3f} "
        f"union={result.average_union_candidate_count:.3f} "
        f"full={result.average_full_candidate_count:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
