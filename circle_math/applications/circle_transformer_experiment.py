"""An honest bias-variance experiment: circulant mixer vs dense mixer.

This is a real, non-tautological comparison (not an accuracy fixture rigged for circle
math to win). The question:

    A circulant token mixer has ``n`` parameters and a built-in *shift-structured*
    inductive bias; a dense mixer has ``n^2`` parameters and no such bias. When does the
    circulant model generalize *better*, and when *worse*?

Both models are linear maps fit by exact least squares (no iterative training, fully
deterministic), so the comparison is clean. We run two regimes:

* **shift-structured target** — the true map is itself circulant (a periodic dependency);
* **unstructured target** — the true map is a dense random matrix.

and sweep the training-set size. The honest expectation, which the numbers either confirm
or refute: the circulant model should win on the shift-structured target in the
small-sample regime (right inductive bias, fewer parameters) and lose on the unstructured
target (its bias is wrong there). We report the measured test error straight, whatever it
is. This says nothing about deep transformers; it is a controlled study of the circulant
inductive bias.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _circulant_matrix(kernel: np.ndarray) -> np.ndarray:
    """Build the ``n x n`` circulant matrix ``C`` with ``C[i, j] = kernel[(i - j) mod n]``."""
    n = kernel.shape[0]
    idx = (np.arange(n)[:, None] - np.arange(n)[None, :]) % n
    return kernel[idx]


def _fit_dense(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Least-squares fit of a dense map ``M`` (n x n) with ``Y ≈ X @ M.T``."""
    M_T, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return M_T.T


def _fit_circulant(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Least-squares fit of a circulant map (kernel of length n) with ``Y ≈ X @ C.T``.

    ``(X @ C.T)[s, i] = sum_j kernel[j] * X[s, (i - j) mod n]``, which is linear in the
    kernel; we stack that design matrix and solve for the kernel.
    """
    n = X.shape[1]
    n_samples = X.shape[0]
    # design[s*n + i, j] = X[s, (i - j) mod n]
    design = np.empty((n_samples * n, n))
    for j in range(n):
        design[:, j] = np.roll(X, j, axis=1).reshape(-1)
    target = Y.reshape(-1)
    kernel, *_ = np.linalg.lstsq(design, target, rcond=None)
    return _circulant_matrix(kernel)


def _test_mse(M: np.ndarray, X: np.ndarray, Y: np.ndarray) -> float:
    pred = X @ M.T
    return float(np.mean((pred - Y) ** 2))


@dataclass
class ExperimentResult:
    n: int
    n_train: int
    structured: bool
    noise: float
    circulant_test_mse: float
    dense_test_mse: float

    @property
    def circulant_wins(self) -> bool:
        return self.circulant_test_mse < self.dense_test_mse


def run_experiment(
    n: int = 16,
    n_train: int = 24,
    n_test: int = 400,
    structured: bool = True,
    noise: float = 0.05,
    seed: int = 0,
) -> ExperimentResult:
    """Fit circulant and dense linear mixers and return held-out test MSE for each."""
    rng = np.random.default_rng(seed)
    if structured:
        true_map = _circulant_matrix(rng.standard_normal(n))
    else:
        true_map = rng.standard_normal((n, n)) / np.sqrt(n)

    X_train = rng.standard_normal((n_train, n))
    X_test = rng.standard_normal((n_test, n))
    Y_train = X_train @ true_map.T + noise * rng.standard_normal((n_train, n))
    Y_test = X_test @ true_map.T

    circ = _fit_circulant(X_train, Y_train)
    dense = _fit_dense(X_train, Y_train)
    return ExperimentResult(
        n=n,
        n_train=n_train,
        structured=structured,
        noise=noise,
        circulant_test_mse=_test_mse(circ, X_test, Y_test),
        dense_test_mse=_test_mse(dense, X_test, Y_test),
    )


def sweep(n: int = 16, train_sizes: tuple[int, ...] = (12, 16, 24, 48, 200), seed: int = 0):
    """Run the experiment across training sizes for both target regimes."""
    rows = []
    for structured in (True, False):
        for n_train in train_sizes:
            rows.append(run_experiment(n=n, n_train=n_train, structured=structured, seed=seed))
    return rows


def format_report(rows: list[ExperimentResult]) -> str:
    lines = [
        "circulant vs dense linear mixer — held-out test MSE (lower is better)",
        f"{'target':<14}{'n_train':>8}{'circulant':>12}{'dense':>12}{'winner':>12}",
    ]
    for r in rows:
        target = "shift-struct" if r.structured else "unstructured"
        winner = "circulant" if r.circulant_wins else "dense"
        lines.append(
            f"{target:<14}{r.n_train:>8}{r.circulant_test_mse:>12.4f}"
            f"{r.dense_test_mse:>12.4f}{winner:>12}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_report(sweep()))
