"""Tiny learned content-gate coil/local retrieval benchmark sidecar.

This deterministic fixture fits a phase-to-route lookup table for coil/local
candidate routing and compares it with static, wrong-period, flipped-gate,
union, and full-attention baselines. It measures candidate-set reachability and
candidate budget only. It is not an attention-quality, model-quality,
memory-scaling, context-length, or speed claim.

Example:
    python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_content_gate_retrieval.py
"""

from __future__ import annotations

import argparse

from circle_math.applications.circle_ai import run_learned_content_gate_retrieval_benchmark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic learned content-gate retrieval fixture.")
    parser.add_argument("--sequence-length", type=int, default=64)
    parser.add_argument("--train-length", type=int, default=64)
    parser.add_argument("--test-length", type=int, default=32)
    parser.add_argument("--route-period", type=int, default=2)
    parser.add_argument("--wrong-route-period", type=int, default=3)
    parser.add_argument("--long-target-lag", type=int, default=21)
    parser.add_argument("--near-target-lag", type=int, default=3)
    parser.add_argument("--stride", type=int, default=7)
    parser.add_argument("--path-length", type=int, default=3)
    parser.add_argument("--local-window", type=int, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_learned_content_gate_retrieval_benchmark(
        sequence_length=args.sequence_length,
        train_length=args.train_length,
        test_length=args.test_length,
        route_period=args.route_period,
        wrong_route_period=args.wrong_route_period,
        long_target_lag=args.long_target_lag,
        near_target_lag=args.near_target_lag,
        stride=args.stride,
        path_length=args.path_length,
        local_window=args.local_window,
    )
    print(
        "learned_content_gate_retrieval "
        f"sequence_length={result.sequence_length} train_length={result.train_length} "
        f"test_length={result.test_length} route_period={result.route_period} "
        f"wrong_route_period={result.wrong_route_period}"
    )
    print(f"learned_route_lookup={result.learned_route_lookup}")
    print(f"wrong_period_route_lookup={result.wrong_period_route_lookup}")
    print(f"required_route_sample={result.required_route_sample}")
    print(f"learned_route_sample={result.learned_route_sample}")
    print(f"learned_route accuracy={result.learned_route_accuracy:.3f}")
    print(f"wrong_period_route_control accuracy={result.wrong_period_route_accuracy:.3f}")
    print(f"learned_gate accuracy={result.learned_gate_accuracy:.3f}")
    print(f"static_coil_baseline accuracy={result.static_coil_accuracy:.3f}")
    print(f"static_local_baseline accuracy={result.static_local_accuracy:.3f}")
    print(f"wrong_period_gate_control accuracy={result.wrong_period_gate_accuracy:.3f}")
    print(f"flipped_gate_control accuracy={result.flipped_gate_accuracy:.3f}")
    print(f"union_candidate_baseline accuracy={result.union_candidate_accuracy:.3f}")
    print(f"full_attention_oracle accuracy={result.full_attention_accuracy:.3f}")
    print(
        "candidate_budget "
        f"learned={result.average_learned_candidate_count:.3f} "
        f"union={result.average_union_candidate_count:.3f} "
        f"full={result.average_full_candidate_count:.3f}"
    )
    print(result.note)


if __name__ == "__main__":
    main()
