"""Finite Fourier and circulant helpers for finite circles.

The functions in this module are executable companions to the Lean
``Circle.Core.FiniteFourier`` and ``Circle.Applications.CirculantSpectral``
theorems. They use the standard complex DFT convention

``X[k] = sum_j x[j] * exp(-2*pi*i*k*j/n)``.

Claim boundary: these helpers compute finite cyclic algebra facts. Floating
point residuals are diagnostics, not Lean proofs.
"""

from __future__ import annotations

from cmath import exp, pi
from dataclasses import dataclass
from typing import Iterable, Sequence, Union


Number = Union[complex, float, int]


@dataclass(frozen=True)
class SpectralConvolutionReport:
    """Residual report for the finite Fourier circular-convolution identity."""

    size: int
    max_abs_error: float
    passed: bool
    tolerance: float


def _as_complex_vector(values: Sequence[Number] | Iterable[Number]) -> list[complex]:
    return [complex(value) for value in values]


def _require_positive_size(size: int) -> None:
    if size <= 0:
        raise ValueError("finite circle size must be positive")


def _require_same_length(left: Sequence[Number], right: Sequence[Number]) -> None:
    if len(left) != len(right):
        raise ValueError("finite-circle vectors must have the same length")
    _require_positive_size(len(left))


def root_of_unity(size: int, frequency: int = 1) -> complex:
    """Return ``exp(-2*pi*i*frequency/size)`` for the finite circle."""

    _require_positive_size(size)
    return exp((-2j * pi * frequency) / size)


def character_value(size: int, frequency: int, index: int) -> complex:
    """Evaluate the DFT character ``k`` at finite-circle node ``index``."""

    _require_positive_size(size)
    return root_of_unity(size, frequency) ** (index % size)


def dft_matrix(size: int) -> list[list[complex]]:
    """Return the unnormalized DFT matrix for a finite circle of ``size`` nodes."""

    _require_positive_size(size)
    return [
        [character_value(size, frequency, index) for index in range(size)]
        for frequency in range(size)
    ]


def finite_fourier_coefficients(signal: Sequence[Number]) -> list[complex]:
    """Return unnormalized finite Fourier coefficients of ``signal``."""

    values = _as_complex_vector(signal)
    _require_positive_size(len(values))
    return [
        sum(value * character_value(len(values), frequency, index)
            for index, value in enumerate(values))
        for frequency in range(len(values))
    ]


def inverse_finite_fourier(coefficients: Sequence[Number]) -> list[complex]:
    """Invert ``finite_fourier_coefficients`` with the matching normalization."""

    values = _as_complex_vector(coefficients)
    size = len(values)
    _require_positive_size(size)
    return [
        sum(
            values[frequency] * exp((2j * pi * frequency * index) / size)
            for frequency in range(size)
        )
        / size
        for index in range(size)
    ]


def circular_convolution(kernel: Sequence[Number], signal: Sequence[Number]) -> list[complex]:
    """Return ``(kernel * signal)[i] = sum_j kernel[j] * signal[i-j]`` on ``Z/nZ``."""

    _require_same_length(kernel, signal)
    c = _as_complex_vector(kernel)
    x = _as_complex_vector(signal)
    size = len(c)
    return [
        sum(c[j] * x[(i - j) % size] for j in range(size))
        for i in range(size)
    ]


def circulant_matrix(kernel: Sequence[Number]) -> list[list[complex]]:
    """Return the matrix for circular convolution by ``kernel``."""

    c = _as_complex_vector(kernel)
    _require_positive_size(len(c))
    size = len(c)
    return [[c[(row - col) % size] for col in range(size)] for row in range(size)]


def spectral_convolution_report(
    kernel: Sequence[Number],
    signal: Sequence[Number],
    *,
    tolerance: float = 1e-9,
) -> SpectralConvolutionReport:
    """Check ``DFT(kernel * signal) = DFT(kernel) * DFT(signal)`` numerically."""

    _require_same_length(kernel, signal)
    conv_hat = finite_fourier_coefficients(circular_convolution(kernel, signal))
    kernel_hat = finite_fourier_coefficients(kernel)
    signal_hat = finite_fourier_coefficients(signal)
    errors = [
        abs(left - (right_kernel * right_signal))
        for left, right_kernel, right_signal in zip(conv_hat, kernel_hat, signal_hat)
    ]
    max_abs_error = max(errors, default=0.0)
    return SpectralConvolutionReport(
        size=len(kernel),
        max_abs_error=max_abs_error,
        passed=max_abs_error <= tolerance,
        tolerance=tolerance,
    )


def spectral_aliasing_report(size: int, frequencies: Iterable[int]) -> dict[int, list[int]]:
    """Group integer frequencies by their finite-circle residue class."""

    _require_positive_size(size)
    classes: dict[int, list[int]] = {}
    for frequency in frequencies:
        classes.setdefault(frequency % size, []).append(frequency)
    return {residue: sorted(values) for residue, values in sorted(classes.items())}


__all__ = [
    "SpectralConvolutionReport",
    "character_value",
    "circular_convolution",
    "circulant_matrix",
    "dft_matrix",
    "finite_fourier_coefficients",
    "inverse_finite_fourier",
    "root_of_unity",
    "spectral_aliasing_report",
    "spectral_convolution_report",
]
