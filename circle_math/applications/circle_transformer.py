"""Runnable reference for a circle-structured ("CircleFormer") transformer block.

This module is the *executable* companion to the Lean structural guarantees in
``Circle/Applications/CircleTransformer.lean`` and ``Circle/Applications/Circulant.lean``.
It demonstrates, as measurable numeric facts, the exact properties those theorems prove:

* circulant token mixing is **cyclic-shift equivariant** (``AIT-T0006``);
* RoPE positional encoding gives a query/key score that depends only on the **relative**
  position ``m - n`` (``AIT-T0004``, ``AIT-T0005``);
* a strided ("coil") attention head reaches **all** positions iff its stride is coprime to
  the context length (``AIT-T0001``, ``AIT-T0002``), reaching ``n / gcd(n, k)`` positions.

These are *structural* demonstrations — exact properties checked in code, not accuracy
benchmarks. Whether such a block improves model quality is empirical and deliberately out
of scope here. The implementation is plain NumPy so it runs anywhere; it is written to be
MLX-portable (only elementwise ops, matmuls, and rolls are used).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Optional

import numpy as np

__all__ = [
    "cyclic_shift",
    "circulant_mix",
    "rope_rotate",
    "rope_score",
    "strided_reach",
    "strided_head_covers_all",
    "CircleFormerBlock",
    "shift_equivariance_error",
    "rope_relative_error",
    "strided_coverage_report",
]


# ---------------------------------------------------------------------------
# Circulant token mixing  (Circle.Applications.circConv / shiftBy)
# ---------------------------------------------------------------------------


def cyclic_shift(x: np.ndarray, s: int) -> np.ndarray:
    """Shift a sequence ``x`` (shape ``(n, d)``) cyclically by ``s`` positions."""
    return np.roll(x, s, axis=0)


def circulant_mix(kernel: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Circulant (cyclic-convolution) token mixing ``(c * x)_i = sum_j c_j x_{i-j}``.

    ``kernel`` has shape ``(n,)`` and ``x`` has shape ``(n, d)``; one shared kernel mixes
    across the ``n`` positions (the ``C n`` group algebra). ``O(n)`` parameters, not
    ``O(n^2)``.
    """
    n = kernel.shape[0]
    if x.shape[0] != n:
        raise ValueError("kernel length must match sequence length")
    out = np.zeros_like(x, dtype=float)
    for j in range(n):
        out = out + kernel[j] * np.roll(x, j, axis=0)
    return out


# ---------------------------------------------------------------------------
# RoPE positional encoding  (Circle.Applications.ropePhase / rope_*)
# ---------------------------------------------------------------------------


def _rope_angles(dim: int, base: float) -> np.ndarray:
    if dim % 2 != 0:
        raise ValueError("RoPE feature dimension must be even")
    half = dim // 2
    return base ** (-2.0 * np.arange(half) / dim)


def rope_rotate(vec: np.ndarray, position: int, base: float = 10000.0) -> np.ndarray:
    """Rotary position encoding: rotate the pairs of ``vec`` by ``position * theta_k``."""
    dim = vec.shape[-1]
    thetas = _rope_angles(dim, base)
    angle = position * thetas
    cos, sin = np.cos(angle), np.sin(angle)
    even = vec[..., 0::2]
    odd = vec[..., 1::2]
    rotated = np.empty_like(vec, dtype=float)
    rotated[..., 0::2] = even * cos - odd * sin
    rotated[..., 1::2] = even * sin + odd * cos
    return rotated


def rope_score(query: np.ndarray, key: np.ndarray, m: int, n: int, base: float = 10000.0) -> float:
    """Attention score ``<RoPE_m(query), RoPE_n(key)>`` between positions ``m`` and ``n``."""
    return float(np.dot(rope_rotate(query, m, base), rope_rotate(key, n, base)))


# ---------------------------------------------------------------------------
# Strided ("coil") sparse attention  (Circle.Applications.strided* / attentionReach)
# ---------------------------------------------------------------------------


def strided_reach(n: int, k: int, start: int = 0) -> set[int]:
    """Positions reachable from ``start`` by repeatedly adding stride ``k`` modulo ``n``.

    This is the coil orbit of the stride; its size is ``n / gcd(n, k)``.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    seen: set[int] = set()
    i = start % n
    while i not in seen:
        seen.add(i)
        i = (i + k) % n
    return seen


def strided_head_covers_all(n: int, k: int) -> bool:
    """Whether a single stride-``k`` head reaches every position of a length-``n`` context."""
    return len(strided_reach(n, k)) == n


def _coil_attention_mask(n: int, strides: tuple[int, ...]) -> np.ndarray:
    """Boolean ``(n, n)`` mask: query ``i`` attends to its coil orbit(s) over the strides."""
    mask = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for k in strides:
            for j in strided_reach(n, k, start=i):
                mask[i, j] = True
    return mask


# ---------------------------------------------------------------------------
# A minimal CircleFormer block: RoPE + coil-attention + circulant mix
# ---------------------------------------------------------------------------


@dataclass
class CircleFormerBlock:
    """A tiny, runnable circle-structured attention+mixing block.

    Positional encoding is RoPE (the ``S^1`` rotation action), sparse attention runs along
    coil orbits with coprime strides (so coverage is provably full), and token mixing is a
    circulant convolution (translation-equivariant, ``n`` parameters).
    """

    seq_len: int
    dim: int
    strides: tuple[int, ...]
    rope_base: float = 10000.0
    seed: int = 0

    def __post_init__(self) -> None:
        if self.dim % 2 != 0:
            raise ValueError("dim must be even for RoPE")
        rng = np.random.default_rng(self.seed)
        # learned-ish parameters, fixed by seed for reproducibility
        self.Wq = rng.standard_normal((self.dim, self.dim)) / np.sqrt(self.dim)
        self.Wk = rng.standard_normal((self.dim, self.dim)) / np.sqrt(self.dim)
        self.Wv = rng.standard_normal((self.dim, self.dim)) / np.sqrt(self.dim)
        self.kernel = rng.standard_normal(self.seq_len)
        self._mask = _coil_attention_mask(self.seq_len, self.strides)

    def coverage_is_full(self) -> bool:
        """True iff the configured strides make every token reach every other (one hop set)."""
        return bool(self._mask.all())

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Run one block: RoPE coil-attention, then a circulant mix. ``x`` is ``(n, dim)``."""
        n, d = x.shape
        if n != self.seq_len or d != self.dim:
            raise ValueError("input shape must match (seq_len, dim)")
        q = x @ self.Wq
        k = x @ self.Wk
        v = x @ self.Wv
        # RoPE-rotate each position's query and key
        qr = np.stack([rope_rotate(q[i], i, self.rope_base) for i in range(n)])
        kr = np.stack([rope_rotate(k[i], i, self.rope_base) for i in range(n)])
        scores = (qr @ kr.T) / np.sqrt(d)
        scores = np.where(self._mask, scores, -np.inf)
        scores = scores - scores.max(axis=1, keepdims=True)
        weights = np.exp(scores)
        weights = weights / weights.sum(axis=1, keepdims=True)
        attended = weights @ v
        return circulant_mix(self.kernel, attended)


# ---------------------------------------------------------------------------
# Property demonstrations (return measurable quantities, ~0 / exact)
# ---------------------------------------------------------------------------


def shift_equivariance_error(n: int, dim: int, shift: int, seed: int = 0) -> float:
    """Max abs difference between ``mix(shift(x))`` and ``shift(mix(x))`` (should be ~0)."""
    rng = np.random.default_rng(seed)
    kernel = rng.standard_normal(n)
    x = rng.standard_normal((n, dim))
    lhs = circulant_mix(kernel, cyclic_shift(x, shift))
    rhs = cyclic_shift(circulant_mix(kernel, x), shift)
    return float(np.max(np.abs(lhs - rhs)))


def rope_relative_error(dim: int, m: int, n: int, delta: int, seed: int = 0) -> float:
    """Abs difference between ``rope_score(m, n)`` and ``rope_score(m+delta, n+delta)``.

    Demonstrates that the RoPE score depends only on the relative position ``m - n``
    (should be ~0).
    """
    rng = np.random.default_rng(seed)
    q = rng.standard_normal(dim)
    k = rng.standard_normal(dim)
    return abs(rope_score(q, k, m, n) - rope_score(q, k, m + delta, n + delta))


def strided_coverage_report(n: int) -> dict[int, dict[str, int | bool]]:
    """For each stride ``1..n-1``, report reachable count, full coverage, and gcd.

    The Lean theorem ``AIT-T0002`` predicts ``covers_all`` iff ``gcd(n, k) == 1`` and
    ``AIT-T0001`` predicts ``reach == n / gcd(n, k)``; this report exhibits both.
    """
    report: dict[int, dict[str, int | bool]] = {}
    for k in range(1, n):
        reach = len(strided_reach(n, k))
        g = gcd(n, k)
        report[k] = {
            "reach": reach,
            "predicted_reach": n // g,
            "covers_all": reach == n,
            "gcd": g,
            "coprime": g == 1,
        }
    return report
