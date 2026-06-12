"""Hybrid local+coil sparse-attention reachability benchmark sidecar.

This deterministic fixture compares a local window, a fixed coil path, their
hybrid union, a wrong-stride hybrid, and a full-attention oracle. The positive
case is deliberately structured so near and coil-reachable long lags both
matter; the nonstructured control makes the sparse hybrid lose to full
attention. It is candidate-set reachability only, not an attention-quality or
model-quality claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_hybrid_sparse_attention.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_hybrid_sparse_attention_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic hybrid sparse-attention fixture.")
    parser.add_argument("--sequence-length", type=int, default=96)
    parser.add_argument("--query-count", type=int, default=96)
    parser.add_argument("--stride", type=int, default=11)
    parser.add_argument("--path-length", type=int, default=4)
    parser.add_argument("--local-window", type=int, default=5)
    parser.add_argument("--wrong-stride", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_hybrid_sparse_attention_benchmark(
        sequence_length=args.sequence_length,
        query_count=args.query_count,
        stride=args.stride,
        path_length=args.path_length,
        local_window=args.local_window,
        wrong_stride=args.wrong_stride,
    )
    print(
        "hybrid_sparse_attention "
        f"sequence_length={result.sequence_length} query_count={result.query_count} "
        f"stride={result.stride} path_length={result.path_length} "
        f"local_window={result.local_window}"
    )
    print(f"hybrid accuracy={result.hybrid_accuracy:.3f}")
    print(f"local_window_baseline accuracy={result.local_window_accuracy:.3f}")
    print(f"coil_path_baseline accuracy={result.coil_path_accuracy:.3f}")
    print(f"wrong_stride_hybrid_control accuracy={result.wrong_stride_hybrid_accuracy:.3f}")
    print(f"full_attention_oracle accuracy={result.full_attention_accuracy:.3f}")
    print(
        "candidate_budget "
        f"hybrid={result.average_hybrid_candidate_count:.3f} "
        f"local={result.average_local_candidate_count:.3f} "
        f"coil={result.average_coil_candidate_count:.3f} "
        f"full={result.average_full_candidate_count:.3f}"
    )
    print(
        "nonstructured_control "
        f"hybrid={result.nonstructured_hybrid_accuracy:.3f} "
        f"full={result.nonstructured_full_attention_accuracy:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
