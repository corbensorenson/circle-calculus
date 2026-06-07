"""Tiny AI backend parity sidecar.

This deterministic fixture scores the current Circle AI synthetic cases on CPU
and, when available, with MLX array scoring. It is a backend parity check, not
a model-quality or speed claim.

Example:
    python sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_backend_parity.py
"""

from __future__ import annotations

from circle_math.applications.circle_ai import run_ai_backend_parity_check


def main() -> None:
    result = run_ai_backend_parity_check()
    print(f"ai_backend_parity fixture_count={result.fixture_count}")
    for name, score in result.cpu_scores:
        print(f"cpu {name} accuracy={score:.3f}")
    if not result.mlx_available:
        print("mlx unavailable")
    else:
        for name, score in result.mlx_scores:
            print(f"mlx {name} accuracy={score:.3f}")
        print(f"max_abs_delta={result.max_abs_delta:.6f}")
    print(result.note)


if __name__ == "__main__":
    main()
