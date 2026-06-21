"""Finite cyclic and dihedral equivariance helpers.

This module mirrors the Lean finite equivariance layer. It provides executable
checks for cyclic shifts, reflection-generated dihedral transforms, cyclic-sum
invariance, and circulant-layer cyclic equivariance. These checks are useful
contract artifacts, but model robustness and continuous rotation equivariance
remain outside the proof boundary.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Sequence, Union

from .harmonics import circular_convolution


CYCLIC_EQUIVARIANCE_SCHEMA_ID = "circle_calculus.cyclic_equivariance_report.v0"

CYCLIC_EQUIVARIANCE_THEOREM_IDS: tuple[str, ...] = (
    "CC-T0149",
    "CC-T0150",
    "CC-T0151",
    "CC-T0152",
    "CC-T0153",
    "CC-T0154",
    "CC-T0155",
    "CC-T0156",
    "CC-T0157",
    "CC-T0158",
    "CC-T0159",
    "CC-T0160",
)

CYCLIC_EQUIVARIANCE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.cyclicShift_zero",
    "Circle.Applications.cyclicShift_add",
    "Circle.Applications.cyclicEquivariant_identity",
    "Circle.Applications.cyclicEquivariant_comp",
    "Circle.Applications.cyclicEquivariant_add",
    "Circle.Applications.circulantLayer_cyclicEquivariant",
    "Circle.Applications.cyclicSum_shift_invariant",
    "Circle.Applications.reflectSignal_involutive",
    "Circle.Applications.reflectSignal_shift",
    "Circle.Applications.dihedralEquivariant_identity",
    "Circle.Applications.dihedralEquivariant_implies_cyclic",
    "Circle.Applications.dihedralTransform_reflection_zero_involutive",
)

CYCLIC_EQUIVARIANCE_CLAIM_BOUNDARY = (
    "The proved claim is finite cyclic shift equivariance/invariance and the "
    "minimal finite reflection laws listed in the Lean declarations. This does "
    "not prove steerable CNN completeness, continuous rotation equivariance, "
    "robustness, data efficiency, model quality, or deployment behavior."
)

Signal = Sequence[Union[complex, float, int]]
Layer = Callable[[tuple[complex, ...]], Sequence[Union[complex, float, int]]]


@dataclass(frozen=True)
class EquivarianceCheckReport:
    """Theorem-linked executable report for finite transform equivariance."""

    schema_id: str
    transform_family: str
    example_count: int
    transform_count: int
    passed: bool
    max_abs_delta: float
    failures: tuple[str, ...]
    theorem_ids: tuple[str, ...] = CYCLIC_EQUIVARIANCE_THEOREM_IDS
    lean_declarations: tuple[str, ...] = CYCLIC_EQUIVARIANCE_LEAN_DECLARATIONS
    claim_boundary: str = CYCLIC_EQUIVARIANCE_CLAIM_BOUNDARY
    references: tuple[str, ...] = (
        "https://arxiv.org/abs/1602.07576",
        "https://distill.pub/2020/circuits/equivariance/",
        "https://arxiv.org/abs/1911.08251",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _as_signal(values: Signal) -> tuple[complex, ...]:
    result = tuple(complex(value) for value in values)
    if not result:
        raise ValueError("signal must contain at least one value")
    return result


def _default_shifts(length: int) -> tuple[int, ...]:
    return tuple(range(length))


def _as_shifts(shifts: Iterable[int] | None, length: int) -> tuple[int, ...]:
    if shifts is None:
        return _default_shifts(length)
    result = tuple(int(shift) for shift in shifts)
    if not result:
        raise ValueError("at least one shift is required")
    return result


def _max_abs_delta(left: Sequence[complex], right: Sequence[complex]) -> float:
    if len(left) != len(right):
        return float("inf")
    return max((abs(a - b) for a, b in zip(left, right)), default=0.0)


def cyclic_shift(values: Signal, shift: int) -> tuple[complex, ...]:
    """Return the finite cyclic shift where output ``i`` reads input ``i-shift``."""

    signal = _as_signal(values)
    length = len(signal)
    normalized_shift = int(shift) % length
    return tuple(signal[(index - normalized_shift) % length] for index in range(length))


def reflect_signal(values: Signal) -> tuple[complex, ...]:
    """Return the finite reflection where output ``i`` reads input ``-i``."""

    signal = _as_signal(values)
    length = len(signal)
    return tuple(signal[(-index) % length] for index in range(length))


def dihedral_transform(
    values: Signal,
    *,
    shift: int = 0,
    reflected: bool = False,
) -> tuple[complex, ...]:
    """Apply a finite dihedral transform: optional reflection followed by shift."""

    signal = reflect_signal(values) if reflected else _as_signal(values)
    return cyclic_shift(signal, shift)


def cyclic_orbit(values: Signal) -> tuple[tuple[complex, ...], ...]:
    """Return all cyclic shifts of a signal."""

    signal = _as_signal(values)
    return tuple(cyclic_shift(signal, shift) for shift in range(len(signal)))


def dihedral_orbit(values: Signal) -> tuple[tuple[complex, ...], ...]:
    """Return all shift/reflection transforms of a signal."""

    signal = _as_signal(values)
    return tuple(
        dihedral_transform(signal, shift=shift, reflected=reflected)
        for reflected in (False, True)
        for shift in range(len(signal))
    )


def cyclic_sum(values: Signal) -> complex:
    """Return finite sum-pooling over the cyclic address space."""

    return sum(_as_signal(values), 0j)


def circulant_layer(kernel: Signal, values: Signal) -> tuple[complex, ...]:
    """Return circular convolution with ``kernel`` as a finite circulant layer."""

    kernel_values = _as_signal(kernel)
    signal = _as_signal(values)
    if len(kernel_values) != len(signal):
        raise ValueError("kernel and signal lengths must match")
    return tuple(circular_convolution(kernel_values, signal))


def check_cyclic_equivariance(
    layer: Layer,
    examples: Iterable[Signal],
    *,
    shifts: Iterable[int] | None = None,
    tolerance: float = 1e-9,
) -> EquivarianceCheckReport:
    """Check whether a Python layer commutes with declared finite shifts."""

    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    signals = tuple(_as_signal(example) for example in examples)
    if not signals:
        raise ValueError("at least one example signal is required")
    length = len(signals[0])
    if any(len(signal) != length for signal in signals):
        raise ValueError("all example signals must have the same length")
    shift_values = _as_shifts(shifts, length)
    max_delta = 0.0
    failures: list[str] = []
    for example_index, signal in enumerate(signals):
        base_output = tuple(complex(value) for value in layer(signal))
        for shift in shift_values:
            shifted_input_output = tuple(
                complex(value) for value in layer(cyclic_shift(signal, shift))
            )
            shifted_output = cyclic_shift(base_output, shift)
            delta = _max_abs_delta(shifted_input_output, shifted_output)
            max_delta = max(max_delta, delta)
            if delta > tolerance:
                failures.append(
                    f"example={example_index} shift={shift} delta={delta:.6g}"
                )
    return EquivarianceCheckReport(
        schema_id=CYCLIC_EQUIVARIANCE_SCHEMA_ID,
        transform_family="cyclic_shift",
        example_count=len(signals),
        transform_count=len(shift_values),
        passed=not failures,
        max_abs_delta=max_delta,
        failures=tuple(failures),
    )


def circulant_equivariance_report(
    kernel: Signal,
    examples: Iterable[Signal],
    *,
    shifts: Iterable[int] | None = None,
    tolerance: float = 1e-9,
) -> EquivarianceCheckReport:
    """Return a theorem-linked cyclic equivariance report for a circulant layer."""

    kernel_values = _as_signal(kernel)

    def layer(signal: tuple[complex, ...]) -> tuple[complex, ...]:
        return circulant_layer(kernel_values, signal)

    return check_cyclic_equivariance(
        layer,
        examples,
        shifts=shifts,
        tolerance=tolerance,
    )


def cyclic_sum_invariance_report(
    examples: Iterable[Signal],
    *,
    shifts: Iterable[int] | None = None,
    tolerance: float = 1e-9,
) -> EquivarianceCheckReport:
    """Check finite sum-pooling invariance under cyclic shifts."""

    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    signals = tuple(_as_signal(example) for example in examples)
    if not signals:
        raise ValueError("at least one example signal is required")
    length = len(signals[0])
    if any(len(signal) != length for signal in signals):
        raise ValueError("all example signals must have the same length")
    shift_values = _as_shifts(shifts, length)
    max_delta = 0.0
    failures: list[str] = []
    for example_index, signal in enumerate(signals):
        base_sum = cyclic_sum(signal)
        for shift in shift_values:
            shifted_sum = cyclic_sum(cyclic_shift(signal, shift))
            delta = abs(shifted_sum - base_sum)
            max_delta = max(max_delta, delta)
            if delta > tolerance:
                failures.append(
                    f"example={example_index} shift={shift} delta={delta:.6g}"
                )
    return EquivarianceCheckReport(
        schema_id=CYCLIC_EQUIVARIANCE_SCHEMA_ID,
        transform_family="cyclic_sum_invariance",
        example_count=len(signals),
        transform_count=len(shift_values),
        passed=not failures,
        max_abs_delta=max_delta,
        failures=tuple(failures),
    )


__all__ = [
    "CYCLIC_EQUIVARIANCE_CLAIM_BOUNDARY",
    "CYCLIC_EQUIVARIANCE_LEAN_DECLARATIONS",
    "CYCLIC_EQUIVARIANCE_SCHEMA_ID",
    "CYCLIC_EQUIVARIANCE_THEOREM_IDS",
    "EquivarianceCheckReport",
    "check_cyclic_equivariance",
    "circulant_equivariance_report",
    "circulant_layer",
    "cyclic_orbit",
    "cyclic_shift",
    "cyclic_sum",
    "cyclic_sum_invariance_report",
    "dihedral_orbit",
    "dihedral_transform",
    "reflect_signal",
]
