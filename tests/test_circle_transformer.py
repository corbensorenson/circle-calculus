"""Property tests for the runnable CircleFormer reference.

Each test checks, in executable NumPy, a property that is *separately Lean-proved* in
``Circle/Applications/CircleTransformer.lean`` / ``Circle/Applications/Circulant.lean``.
These are structural-property checks (exact / numerically exact), not accuracy benchmarks.
"""

from __future__ import annotations

from math import gcd

import numpy as np

from circle_math.applications.circle_transformer import (
    CircleFormerBlock,
    rope_relative_error,
    shift_equivariance_error,
    strided_coverage_report,
    strided_head_covers_all,
)


def test_circulant_mixing_is_shift_equivariant() -> None:
    # AIT-T0006: circConv c (shiftBy s x) = shiftBy s (circConv c x)
    for n in (5, 8, 12, 16):
        for shift in (1, 3, n - 1):
            err = shift_equivariance_error(n, dim=4, shift=shift, seed=n + shift)
            assert err < 1e-10, (n, shift, err)


def test_rope_score_depends_only_on_relative_position() -> None:
    # AIT-T0004 / AIT-T0005: the RoPE score is invariant under shifting both positions.
    for (m, n) in ((0, 0), (3, 7), (10, 2), (5, 5)):
        for delta in (1, 4, 9):
            err = rope_relative_error(dim=8, m=m, n=n, delta=delta, seed=m * 13 + n)
            assert err < 1e-9, (m, n, delta, err)


def test_strided_head_coverage_matches_gcd() -> None:
    # AIT-T0001 / AIT-T0002: reach == n / gcd(n,k); full coverage iff gcd(n,k) == 1.
    for n in (6, 7, 12, 15, 20):
        report = strided_coverage_report(n)
        for k, row in report.items():
            assert row["reach"] == row["predicted_reach"] == n // gcd(n, k)
            assert row["covers_all"] == (gcd(n, k) == 1)
            assert strided_head_covers_all(n, k) == (gcd(n, k) == 1)


def test_coprime_strides_give_full_coverage_noncoprime_do_not() -> None:
    # A coil-attention block with coprime strides provably reaches everything.
    full = CircleFormerBlock(seq_len=12, dim=8, strides=(5,), seed=1)
    assert full.coverage_is_full()
    partial = CircleFormerBlock(seq_len=12, dim=8, strides=(4,), seed=1)
    assert not partial.coverage_is_full()


def test_circleformer_block_forward_runs() -> None:
    block = CircleFormerBlock(seq_len=7, dim=8, strides=(1,), seed=2)
    assert block.coverage_is_full()  # stride 1 is coprime to everything
    rng = np.random.default_rng(0)
    x = rng.standard_normal((7, 8))
    y = block.forward(x)
    assert y.shape == (7, 8)
    assert np.all(np.isfinite(y))
