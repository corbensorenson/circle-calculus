"""Tiny circle-phase feature probe for synthetic periodic labels.

This module is intentionally small and non-claimy. It demonstrates one local
point: for a synthetic periodic target, a linear probe over ``cos/sin`` circle
coordinates can read the rule while a raw-position linear baseline cannot.
It is not a transformer benchmark.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Literal

import numpy as np


Backend = Literal["auto", "numpy", "mlx"]

NON_CLAIM = (
    "This synthetic probe does not prove real model quality, speed, memory, "
    "context-length, or reasoning gains."
)


@dataclass(frozen=True)
class CirclePhaseProbeResult:
    period: int
    train_cycles: int
    test_cycles: int
    train_length: int
    test_length: int
    backend_requested: str
    backend_used: str
    target_rule: str
    baseline_train_accuracy: float
    baseline_test_accuracy: float
    phase_train_accuracy: float
    phase_test_accuracy: float
    baseline_weights: tuple[float, ...]
    phase_weights: tuple[float, ...]
    non_claims: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _validate_positive(name: str, value: int) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _resolve_backend(backend: Backend) -> str:
    if backend not in {"auto", "numpy", "mlx"}:
        raise ValueError("backend must be one of: auto, numpy, mlx")
    if backend == "numpy":
        return "numpy"
    if backend == "mlx":
        try:
            import mlx.core  # noqa: F401
        except ModuleNotFoundError as exc:
            raise RuntimeError("backend='mlx' requested, but MLX is not installed") from exc
        return "mlx"
    try:
        import mlx.core  # noqa: F401
    except ModuleNotFoundError:
        return "numpy"
    return "mlx"


def _labels_numpy(positions: np.ndarray, period: int) -> np.ndarray:
    angle = 2.0 * math.pi * np.mod(positions, period) / period
    return (np.cos(angle) >= 0.0).astype(float)


def _raw_position_features_numpy(positions: np.ndarray, train_length: int) -> np.ndarray:
    scale = max(1, train_length - 1)
    return np.column_stack([np.ones_like(positions, dtype=float), positions / scale])


def _phase_features_numpy(positions: np.ndarray, period: int) -> np.ndarray:
    angle = 2.0 * math.pi * np.mod(positions, period) / period
    return np.column_stack(
        [
            np.ones_like(positions, dtype=float),
            np.cos(angle),
            np.sin(angle),
        ]
    )


def _phase_features_mlx(positions: np.ndarray, period: int) -> tuple[np.ndarray, np.ndarray]:
    import mlx.core as mx

    x = mx.array(positions)
    angle = (2.0 * math.pi) * (x % period) / period
    features = mx.stack([mx.ones_like(x), mx.cos(angle), mx.sin(angle)], axis=1)
    labels = (mx.cos(angle) >= 0.0).astype(mx.float32)
    mx.eval(features, labels)
    return np.array(features, dtype=float), np.array(labels, dtype=float)


def _fit_predict_accuracy(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    test_features: np.ndarray,
    test_labels: np.ndarray,
) -> tuple[float, float, tuple[float, ...]]:
    weights, *_ = np.linalg.lstsq(train_features, train_labels, rcond=None)
    train_pred = (train_features @ weights >= 0.5).astype(float)
    test_pred = (test_features @ weights >= 0.5).astype(float)
    return (
        float(np.mean(train_pred == train_labels)),
        float(np.mean(test_pred == test_labels)),
        tuple(float(value) for value in weights),
    )


def run_circle_phase_probe(
    *,
    period: int = 8,
    train_cycles: int = 4,
    test_cycles: int = 2,
    backend: Backend = "auto",
) -> CirclePhaseProbeResult:
    """Run the deterministic synthetic circle-phase probe.

    The baseline sees only a linear raw-position feature ``[1, x]``. The phase
    probe sees ``[1, cos(2 pi x / period), sin(2 pi x / period)]``.
    """

    period = _validate_positive("period", period)
    train_cycles = _validate_positive("train_cycles", train_cycles)
    test_cycles = _validate_positive("test_cycles", test_cycles)
    backend_used = _resolve_backend(backend)

    train_length = period * train_cycles
    test_length = period * test_cycles
    train_positions = np.arange(train_length, dtype=float)
    test_positions = np.arange(train_length, train_length + test_length, dtype=float)

    train_labels = _labels_numpy(train_positions, period)
    test_labels = _labels_numpy(test_positions, period)
    raw_train = _raw_position_features_numpy(train_positions, train_length)
    raw_test = _raw_position_features_numpy(test_positions, train_length)
    if backend_used == "mlx":
        phase_train, mlx_train_labels = _phase_features_mlx(train_positions, period)
        phase_test, mlx_test_labels = _phase_features_mlx(test_positions, period)
        train_labels = mlx_train_labels
        test_labels = mlx_test_labels
    else:
        phase_train = _phase_features_numpy(train_positions, period)
        phase_test = _phase_features_numpy(test_positions, period)

    baseline_train, baseline_test, baseline_weights = _fit_predict_accuracy(
        raw_train,
        train_labels,
        raw_test,
        test_labels,
    )
    phase_train_accuracy, phase_test_accuracy, phase_weights = _fit_predict_accuracy(
        phase_train,
        train_labels,
        phase_test,
        test_labels,
    )
    return CirclePhaseProbeResult(
        period=period,
        train_cycles=train_cycles,
        test_cycles=test_cycles,
        train_length=train_length,
        test_length=test_length,
        backend_requested=backend,
        backend_used=backend_used,
        target_rule="label(x)=1 iff cos(2*pi*(x mod period)/period) >= 0",
        baseline_train_accuracy=baseline_train,
        baseline_test_accuracy=baseline_test,
        phase_train_accuracy=phase_train_accuracy,
        phase_test_accuracy=phase_test_accuracy,
        baseline_weights=baseline_weights,
        phase_weights=phase_weights,
        non_claims=NON_CLAIM,
    )
