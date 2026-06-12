"""Tiny stride-family sparse-attention reachability sidecar.

This script reports candidate-set reachability only. It is not a neural
attention-quality, runtime, memory, or sparse-attention replacement benchmark.

Run:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_stride_family_sparse_attention_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence-length", type=int, default=120)
    parser.add_argument("--query-count", type=int, default=120)
    parser.add_argument("--strides", type=int, nargs="+", default=[7, 13])
    parser.add_argument("--wrong-strides", type=int, nargs="+", default=[5, 9])
    parser.add_argument("--path-length", type=int, default=3)
    parser.add_argument("--local-window", type=int, default=4)
    args = parser.parse_args()

    result = run_stride_family_sparse_attention_benchmark(
        sequence_length=args.sequence_length,
        query_count=args.query_count,
        strides=tuple(args.strides),
        wrong_strides=tuple(args.wrong_strides),
        path_length=args.path_length,
        local_window=args.local_window,
    )
    print(
        "stride_family_sparse_attention "
        f"sequence_length={result.sequence_length} "
        f"query_count={result.query_count} "
        f"strides={result.strides} "
        f"wrong_strides={result.wrong_strides} "
        f"path_length={result.path_length} "
        f"local_window={result.local_window} "
        f"family_accuracy={result.family_accuracy:.3f} "
        f"single_stride_accuracy={result.single_stride_accuracy:.3f} "
        f"local_window_accuracy={result.local_window_accuracy:.3f} "
        f"wrong_family_accuracy={result.wrong_family_accuracy:.3f} "
        f"full_attention_accuracy={result.full_attention_accuracy:.3f} "
        f"nonstructured_family_accuracy={result.nonstructured_family_accuracy:.3f} "
        f"nonstructured_full_attention_accuracy={result.nonstructured_full_attention_accuracy:.3f} "
        f"avg_family_candidates={result.average_family_candidate_count:.3f} "
        f"avg_single_stride_candidates={result.average_single_stride_candidate_count:.3f} "
        f"avg_local_candidates={result.average_local_candidate_count:.3f} "
        f"avg_full_candidates={result.average_full_candidate_count:.3f} "
        f"covered_lag_count={result.coverage_certificate.covered_lag_count} "
        f"uncovered_lag_count={result.coverage_certificate.uncovered_lag_count} "
        f"dedup_candidate_budget={result.coverage_certificate.candidate_budget_per_query} "
        f"theorem_side_unique_lag_candidate_count="
        f"{result.coverage_certificate.theorem_side_unique_lag_candidate_count} "
        f"dedup_candidate_budget_upper_bound="
        f"{result.coverage_certificate.deduplicated_candidate_budget_upper_bound} "
        f"raw_candidate_budget_upper_bound={result.coverage_certificate.raw_candidate_budget_upper_bound} "
        f"coverage_complete={result.coverage_certificate.coverage_complete} "
        f"coverage_ratio={result.coverage_certificate.coverage_ratio:.3f} "
        f"uncovered_lag_sample={result.coverage_certificate.uncovered_lags[:12]}"
    )


if __name__ == "__main__":
    main()
