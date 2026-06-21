"""Circular statistics and finite residue histogram helpers.

The finite helpers in this module mirror Lean-proved modular contracts:
same-phase predicates, wrapped finite-circle distance, residue samples, and
histograms. The trigonometric helpers are executable reference models for
circular mean, resultant length, wrapped angular error, and unnormalized
von-Mises-style weights; their floating-point behavior is not a formal proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import atan2, cos, exp, hypot, isfinite, sin, tau
from typing import Any, Iterable, Mapping, Sequence


CIRCULAR_STATISTICS_SCHEMA_ID = "circle_calculus.circular_statistics_report.v0"

CIRCULAR_STATISTICS_THEOREM_IDS: tuple[str, ...] = (
    "CC-T0139",
    "CC-T0140",
    "CC-T0141",
    "CC-T0142",
    "CC-T0143",
    "CC-T0144",
    "CC-T0145",
    "CC-T0146",
    "CC-T0147",
    "CC-T0148",
)

CIRCULAR_STATISTICS_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.circularSamePhase_iff_gap_dvd",
    "Circle.Applications.circularSamePhase_refl",
    "Circle.Applications.circularSamePhase_symm",
    "Circle.Applications.circularSamePhase_trans",
    "Circle.Applications.wrappedCircularDistance_comm",
    "Circle.Applications.wrappedCircularDistance_le_forward",
    "Circle.Applications.wrappedCircularDistance_le_backward",
    "Circle.Applications.mem_circularSampleResidues_lt_period",
    "Circle.Applications.circularHistogram_le_length",
    "Circle.Applications.circularHistogram_zero_of_period_le_residue",
)

CIRCULAR_STATISTICS_CLAIM_BOUNDARY = (
    "The proved claim is the exact finite modular residue, same-phase, wrapped "
    "distance, and histogram layer. Floating-point circular means, resultant "
    "vectors, wrapped angular errors, von-Mises-style weights, uncertainty "
    "interpretation, model quality, sensor quality, and downstream decisions "
    "are executable references only and are not Lean-proved by this report."
)


@dataclass(frozen=True)
class CircularMeanReport:
    """Theorem-linked report for circular mean and resultant-length data."""

    schema_id: str
    period: float
    sample_count: int
    total_weight: float
    normalized_angles: tuple[float, ...]
    resultant_x: float
    resultant_y: float
    resultant_length: float
    mean_resultant_length: float
    circular_variance: float
    mean_angle: float | None
    undefined_mean: bool
    theorem_ids: tuple[str, ...] = CIRCULAR_STATISTICS_THEOREM_IDS
    lean_declarations: tuple[str, ...] = CIRCULAR_STATISTICS_LEAN_DECLARATIONS
    claim_boundary: str = CIRCULAR_STATISTICS_CLAIM_BOUNDARY
    references: tuple[str, ...] = (
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.circmean.html",
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.circvar.html",
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.directional_stats.html",
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_positive_finite_period(period: float) -> float:
    period = float(period)
    if not isfinite(period) or period <= 0.0:
        raise ValueError("period must be a positive finite number")
    return period


def _require_finite_angle(name: str, value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _require_positive_int(name: str, value: int) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _require_nonnegative_int(name: str, value: int) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _as_angle_tuple(angles: Iterable[float]) -> tuple[float, ...]:
    result = tuple(_require_finite_angle("angle", angle) for angle in angles)
    if not result:
        raise ValueError("at least one angle is required")
    return result


def _as_weight_tuple(
    weights: Iterable[float] | None,
    count: int,
) -> tuple[float, ...]:
    if weights is None:
        return (1.0,) * count
    result = tuple(float(weight) for weight in weights)
    if len(result) != count:
        raise ValueError("weights length must match angles length")
    if any((not isfinite(weight)) or weight < 0.0 for weight in result):
        raise ValueError("weights must be nonnegative finite numbers")
    if sum(result) <= 0.0:
        raise ValueError("at least one weight must be positive")
    return result


def normalize_angle(angle: float, *, period: float = tau) -> float:
    """Return ``angle`` normalized into ``[0, period)``."""

    period = _require_positive_finite_period(period)
    angle = _require_finite_angle("angle", angle)
    return angle % period


def angular_difference(left: float, right: float, *, period: float = tau) -> float:
    """Return the signed shortest difference from ``left`` to ``right``.

    The result lies in ``[-period/2, period/2)``. Antipodal samples choose the
    negative representative, matching the standard modulo-centered convention.
    """

    period = _require_positive_finite_period(period)
    left = _require_finite_angle("left", left)
    right = _require_finite_angle("right", right)
    return ((right - left + period / 2.0) % period) - period / 2.0


def wrapped_angular_error(left: float, right: float, *, period: float = tau) -> float:
    """Return the absolute shortest angular distance between two samples."""

    return abs(angular_difference(left, right, period=period))


def resultant_vector(
    angles: Iterable[float],
    *,
    weights: Iterable[float] | None = None,
    period: float = tau,
) -> tuple[float, float]:
    """Return the weighted resultant vector ``(sum cos, sum sin)``."""

    period = _require_positive_finite_period(period)
    angle_values = _as_angle_tuple(angles)
    weight_values = _as_weight_tuple(weights, len(angle_values))
    x = 0.0
    y = 0.0
    for angle, weight in zip(angle_values, weight_values):
        theta = normalize_angle(angle, period=period) / period * tau
        x += weight * cos(theta)
        y += weight * sin(theta)
    return (x, y)


def mean_resultant_length(
    angles: Iterable[float],
    *,
    weights: Iterable[float] | None = None,
    period: float = tau,
) -> float:
    """Return resultant length divided by total weight."""

    angle_values = _as_angle_tuple(angles)
    weight_values = _as_weight_tuple(weights, len(angle_values))
    x, y = resultant_vector(angle_values, weights=weight_values, period=period)
    return hypot(x, y) / sum(weight_values)


def circular_variance(
    angles: Iterable[float],
    *,
    weights: Iterable[float] | None = None,
    period: float = tau,
) -> float:
    """Return the common circular variance convention ``1 - R``."""

    return 1.0 - mean_resultant_length(angles, weights=weights, period=period)


def circular_mean(
    angles: Iterable[float],
    *,
    weights: Iterable[float] | None = None,
    period: float = tau,
    zero_tolerance: float = 1e-12,
) -> float | None:
    """Return the circular mean angle, or ``None`` for a zero resultant."""

    report = circular_mean_report(
        angles,
        weights=weights,
        period=period,
        zero_tolerance=zero_tolerance,
    )
    return report.mean_angle


def circular_mean_report(
    angles: Iterable[float],
    *,
    weights: Iterable[float] | None = None,
    period: float = tau,
    zero_tolerance: float = 1e-12,
    metadata: Mapping[str, Any] | None = None,
) -> CircularMeanReport:
    """Return a theorem-linked circular mean/resultant report.

    ``metadata`` is accepted for API symmetry with other report builders but is
    not stored yet; callers should keep large experiment payloads outside this
    compact public report.
    """

    del metadata
    period = _require_positive_finite_period(period)
    if zero_tolerance < 0.0 or not isfinite(zero_tolerance):
        raise ValueError("zero_tolerance must be a nonnegative finite number")
    angle_values = _as_angle_tuple(angles)
    weight_values = _as_weight_tuple(weights, len(angle_values))
    normalized = tuple(normalize_angle(angle, period=period) for angle in angle_values)
    x, y = resultant_vector(normalized, weights=weight_values, period=period)
    resultant = hypot(x, y)
    total_weight = sum(weight_values)
    mean_resultant = resultant / total_weight
    mean_angle = None
    undefined = resultant <= zero_tolerance
    if not undefined:
        mean_angle = normalize_angle(atan2(y, x) / tau * period, period=period)
    return CircularMeanReport(
        schema_id=CIRCULAR_STATISTICS_SCHEMA_ID,
        period=period,
        sample_count=len(angle_values),
        total_weight=total_weight,
        normalized_angles=normalized,
        resultant_x=x,
        resultant_y=y,
        resultant_length=resultant,
        mean_resultant_length=mean_resultant,
        circular_variance=1.0 - mean_resultant,
        mean_angle=mean_angle,
        undefined_mean=undefined,
    )


def von_mises_weight(
    angle: float,
    *,
    mean: float = 0.0,
    kappa: float = 1.0,
    period: float = tau,
) -> float:
    """Return the unnormalized von-Mises-style weight ``exp(kappa*cos(d))``."""

    period = _require_positive_finite_period(period)
    angle = _require_finite_angle("angle", angle)
    mean = _require_finite_angle("mean", mean)
    kappa = float(kappa)
    if not isfinite(kappa) or kappa < 0.0:
        raise ValueError("kappa must be a nonnegative finite number")
    diff = angular_difference(mean, angle, period=period) / period * tau
    return exp(kappa * cos(diff))


def finite_same_phase(period: int, left: int, right: int) -> bool:
    """Return the Lean-backed finite same-phase predicate."""

    period = _require_positive_int("period", period)
    left = _require_nonnegative_int("left", left)
    right = _require_nonnegative_int("right", right)
    return left % period == right % period


def finite_wrapped_distance(period: int, left: int, right: int) -> int:
    """Return the shorter wrapped distance on a finite natural circle."""

    period = _require_positive_int("period", period)
    left = _require_nonnegative_int("left", left)
    right = _require_nonnegative_int("right", right)
    forward = (right - left) % period
    backward = (left - right) % period
    return min(forward, backward)


def finite_residue_samples(period: int, samples: Iterable[int]) -> tuple[int, ...]:
    """Return natural samples mapped to residues modulo ``period``."""

    period = _require_positive_int("period", period)
    return tuple(
        _require_nonnegative_int("sample", sample) % period for sample in samples
    )


def finite_residue_histogram(
    period: int,
    samples: Iterable[int],
    *,
    include_zero_counts: bool = False,
) -> dict[int, int]:
    """Return a residue histogram for natural samples on ``C_period``."""

    period = _require_positive_int("period", period)
    residues = finite_residue_samples(period, samples)
    histogram: dict[int, int] = (
        {residue: 0 for residue in range(period)} if include_zero_counts else {}
    )
    for residue in residues:
        histogram[residue] = histogram.get(residue, 0) + 1
    return histogram


__all__ = [
    "CIRCULAR_STATISTICS_CLAIM_BOUNDARY",
    "CIRCULAR_STATISTICS_LEAN_DECLARATIONS",
    "CIRCULAR_STATISTICS_SCHEMA_ID",
    "CIRCULAR_STATISTICS_THEOREM_IDS",
    "CircularMeanReport",
    "angular_difference",
    "circular_mean",
    "circular_mean_report",
    "circular_variance",
    "finite_residue_histogram",
    "finite_residue_samples",
    "finite_same_phase",
    "finite_wrapped_distance",
    "mean_resultant_length",
    "normalize_angle",
    "resultant_vector",
    "von_mises_weight",
    "wrapped_angular_error",
]
