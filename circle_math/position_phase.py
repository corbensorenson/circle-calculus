"""Reusable finite phase-bank positional encoding helpers.

The functions here model the theorem-backed integer layer of positional phase
systems: each channel exports a declared integer period, and a position is read
through its residue modulo that period. This is useful for RoPE-family schemes,
sinusoidal position features, and 2D phase grids, but it is not a claim about
real-valued margins, length extrapolation, model quality, or runtime behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, floor, tau
from typing import Any, Iterable, Literal, Mapping, Sequence


DiscretizationPolicy = Literal["round", "floor", "ceil"]

POSITION_PHASE_SCHEMA_ID = "circle_calculus.position_phase_bank.v0"
POSITION_PHASE_COLLISION_REPORT_SCHEMA_ID = (
    "circle_calculus.position_phase_collision_report.v0"
)
POSITION_PHASE_GRID_REPORT_SCHEMA_ID = "circle_calculus.position_phase_grid_report.v0"

POSITION_PHASE_THEOREM_IDS: tuple[str, ...] = (
    "CC-T0122",
    "CC-T0123",
    "CC-T0124",
    "CC-T0125",
    "CC-T0126",
    "CC-T0127",
    "CC-T0128",
    "CC-T0129",
    "CC-T0130",
    "CC-T0131",
    "CC-T0132",
)

POSITION_PHASE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.phaseChannelCollision_iff_gap_dvd",
    "Circle.Applications.phaseChannelDistinguishable_iff_not_gap_dvd",
    "Circle.Applications.phaseChannelCollision_iff_eq_on_context",
    "Circle.Applications.phaseBankCollision_iff_forall_gap_dvd",
    "Circle.Applications.phaseBankDistinguishable_iff_exists_not_gap_dvd",
    "Circle.Applications.phaseBankDistinguishable_of_period_ge_context",
    "Circle.Applications.phaseBankCollision_of_subset",
    "Circle.Applications.phaseBankDistinguishable_of_subset",
    "Circle.Applications.phaseGrid2DCollision_iff_axes",
    "Circle.Applications.scaledPhasePeriod_pos",
    "Circle.Applications.scaledPhasePeriodBank_all_pos",
)

POSITION_PHASE_CLAIM_BOUNDARY = (
    "The proved claim is the exact finite integer-period phase-bank residue "
    "contract. Real-valued trigonometric margins, learned scaling rules, "
    "length extrapolation, accuracy, perplexity, speed, memory, training "
    "stability, and deployment behavior are not proved by this report."
)


@dataclass(frozen=True)
class PhaseChannel:
    """One declared integer-period positional phase channel."""

    name: str
    period: int
    source: str = "declared_integer_period"
    axis: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class PhaseBank:
    """A finite collection of declared integer-period phase channels."""

    name: str
    channels: tuple[PhaseChannel, ...]
    scheme: str = "generic_integer_phase_bank"
    schema_id: str = POSITION_PHASE_SCHEMA_ID
    theorem_ids: tuple[str, ...] = POSITION_PHASE_THEOREM_IDS
    lean_declarations: tuple[str, ...] = POSITION_PHASE_LEAN_DECLARATIONS
    claim_boundary: str = POSITION_PHASE_CLAIM_BOUNDARY

    @property
    def periods(self) -> tuple[int, ...]:
        return tuple(channel.period for channel in self.channels)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseChannelCollisionResult:
    """Residue/divisibility report for one channel and one position pair."""

    channel_name: str
    period: int
    left_residue: int
    right_residue: int
    collides: bool
    distinguishes: bool
    period_divides_gap: bool


@dataclass(frozen=True)
class PhaseBankCollisionReport:
    """Theorem-linked collision report for one phase bank and position pair."""

    schema_id: str
    bank: PhaseBank
    left: int
    right: int
    ordered_left: int
    ordered_right: int
    gap: int
    channel_results: tuple[PhaseChannelCollisionResult, ...]
    all_channels_collide: bool
    distinguishes: bool
    witness_channels: tuple[str, ...]
    theorem_ids: tuple[str, ...] = POSITION_PHASE_THEOREM_IDS
    lean_declarations: tuple[str, ...] = POSITION_PHASE_LEAN_DECLARATIONS
    claim_boundary: str = POSITION_PHASE_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseGrid2DCollisionReport:
    """Two-axis phase-grid report for 2D RoPE-style row/column banks."""

    schema_id: str
    x_report: PhaseBankCollisionReport
    y_report: PhaseBankCollisionReport
    grid_collides: bool
    grid_distinguishes: bool
    theorem_ids: tuple[str, ...] = POSITION_PHASE_THEOREM_IDS
    lean_declarations: tuple[str, ...] = POSITION_PHASE_LEAN_DECLARATIONS
    claim_boundary: str = POSITION_PHASE_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_nonnegative_int(name: str, value: int) -> int:
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _require_positive_int(name: str, value: int) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _discretize_period(value: float, policy: DiscretizationPolicy) -> int:
    if value <= 0:
        raise ValueError("period estimate must be positive")
    if policy == "round":
        period = round(value)
    elif policy == "floor":
        period = floor(value)
    elif policy == "ceil":
        period = ceil(value)
    else:
        raise ValueError("discretization must be one of: round, floor, ceil")
    return max(1, int(period))


def phase_residue(period: int, position: int) -> int:
    """Return ``position mod period`` for a positive integer phase period."""

    _require_positive_int("period", period)
    _require_nonnegative_int("position", position)
    return position % period


def phase_channel_collides(period: int, left: int, right: int) -> bool:
    """Return whether two positions collide in one declared phase channel."""

    return phase_residue(period, left) == phase_residue(period, right)


def phase_channel_distinguishes(period: int, left: int, right: int) -> bool:
    """Return whether one declared phase channel separates two positions."""

    return not phase_channel_collides(period, left, right)


def period_divides_gap(period: int, left: int, right: int) -> bool:
    """Return the divisibility criterion proved equivalent to collision."""

    _require_positive_int("period", period)
    _require_nonnegative_int("left", left)
    _require_nonnegative_int("right", right)
    return abs(right - left) % period == 0


def phase_bank_from_periods(
    name: str,
    periods: Iterable[int],
    *,
    scheme: str = "generic_integer_phase_bank",
    source: str = "declared_integer_period",
    axis: str | None = None,
) -> PhaseBank:
    """Build a phase bank from positive integer periods."""

    channels = tuple(
        PhaseChannel(
            name=f"{axis + '_' if axis else ''}phase_{index}",
            period=_require_positive_int("period", int(period)),
            source=source,
            axis=axis,
            metadata={"index": index},
        )
        for index, period in enumerate(periods)
    )
    if not channels:
        raise ValueError("a phase bank must contain at least one channel")
    return PhaseBank(name=name, channels=channels, scheme=scheme)


def phase_bank_collision_report(
    bank: PhaseBank,
    left: int,
    right: int,
) -> PhaseBankCollisionReport:
    """Report exact finite phase-bank collision data for a position pair."""

    _require_nonnegative_int("left", left)
    _require_nonnegative_int("right", right)
    ordered_left, ordered_right = sorted((left, right))
    gap = ordered_right - ordered_left
    channel_results = tuple(
        PhaseChannelCollisionResult(
            channel_name=channel.name,
            period=channel.period,
            left_residue=phase_residue(channel.period, left),
            right_residue=phase_residue(channel.period, right),
            collides=phase_channel_collides(channel.period, left, right),
            distinguishes=phase_channel_distinguishes(channel.period, left, right),
            period_divides_gap=period_divides_gap(channel.period, left, right),
        )
        for channel in bank.channels
    )
    all_collide = all(result.collides for result in channel_results)
    witnesses = tuple(
        result.channel_name for result in channel_results if result.distinguishes
    )
    return PhaseBankCollisionReport(
        schema_id=POSITION_PHASE_COLLISION_REPORT_SCHEMA_ID,
        bank=bank,
        left=left,
        right=right,
        ordered_left=ordered_left,
        ordered_right=ordered_right,
        gap=gap,
        channel_results=channel_results,
        all_channels_collide=all_collide,
        distinguishes=not all_collide,
        witness_channels=witnesses,
    )


def scaled_periods(periods: Iterable[int], scale: int) -> tuple[int, ...]:
    """Return the positive integer periods obtained by multiplying by ``scale``."""

    _require_positive_int("scale", scale)
    return tuple(_require_positive_int("period", int(period)) * scale for period in periods)


def scaled_phase_bank(
    bank: PhaseBank,
    scale: int,
    *,
    name: str | None = None,
    scheme: str = "uniform_scaled_integer_phase_bank",
) -> PhaseBank:
    """Scale every declared channel period in a phase bank."""

    _require_positive_int("scale", scale)
    channels = tuple(
        PhaseChannel(
            name=channel.name,
            period=channel.period * scale,
            source=f"{channel.source}; uniform_integer_scale={scale}",
            axis=channel.axis,
            metadata={**(dict(channel.metadata or {})), "scale": scale},
        )
        for channel in bank.channels
    )
    return PhaseBank(name=name or f"{bank.name}_x{scale}", channels=channels, scheme=scheme)


def sinusoidal_integer_phase_bank(
    *,
    model_dim: int,
    base: float = 10000.0,
    channel_count: int | None = None,
    discretization: DiscretizationPolicy = "round",
    name: str = "sinusoidal_integer_phase_bank",
) -> PhaseBank:
    """Approximate sinusoidal positional wavelengths as declared integer periods.

    The returned bank is an integer contract artifact. It preserves the frequency
    ladder shape of sinusoidal positional encoding, but it does not prove a
    real-valued sinusoid margin.
    """

    _require_positive_int("model_dim", model_dim)
    if base <= 1:
        raise ValueError("base must be greater than 1")
    pairs = model_dim // 2
    count = pairs if channel_count is None else channel_count
    _require_positive_int("channel_count", count)
    if count > pairs:
        raise ValueError("channel_count cannot exceed model_dim // 2")
    channels: list[PhaseChannel] = []
    for index in range(count):
        exponent = (2 * index) / model_dim
        real_period = tau * (base**exponent)
        period = _discretize_period(real_period, discretization)
        channels.append(
            PhaseChannel(
                name=f"sinusoidal_pair_{index}",
                period=period,
                source="sinusoidal_real_period_discretized",
                metadata={
                    "index": index,
                    "model_dim": model_dim,
                    "base": base,
                    "real_period_estimate": real_period,
                    "discretization": discretization,
                },
            )
        )
    return PhaseBank(
        name=name,
        channels=tuple(channels),
        scheme="sinusoidal_integer_phase_bank",
    )


def rope_integer_phase_bank(
    *,
    head_dim: int,
    base: float = 10000.0,
    channel_count: int | None = None,
    discretization: DiscretizationPolicy = "round",
    name: str = "rope_integer_phase_bank",
) -> PhaseBank:
    """Return the integer phase-bank layer for a RoPE-style frequency ladder."""

    bank = sinusoidal_integer_phase_bank(
        model_dim=head_dim,
        base=base,
        channel_count=channel_count,
        discretization=discretization,
        name=name,
    )
    return PhaseBank(
        name=bank.name,
        channels=tuple(
            PhaseChannel(
                name=channel.name.replace("sinusoidal", "rope"),
                period=channel.period,
                source="rope_real_period_discretized",
                metadata=channel.metadata,
            )
            for channel in bank.channels
        ),
        scheme="rope_integer_phase_bank",
    )


def xpos_integer_phase_bank(
    *,
    head_dim: int,
    base: float = 10000.0,
    channel_count: int | None = None,
    discretization: DiscretizationPolicy = "round",
    name: str = "xpos_integer_phase_bank",
) -> PhaseBank:
    """Return the angular integer phase-bank layer for an xPos-style scheme."""

    bank = rope_integer_phase_bank(
        head_dim=head_dim,
        base=base,
        channel_count=channel_count,
        discretization=discretization,
        name=name,
    )
    return PhaseBank(
        name=bank.name,
        channels=tuple(
            PhaseChannel(
                name=channel.name.replace("rope", "xpos"),
                period=channel.period,
                source="xpos_angular_period_discretized; amplitude_decay_not_proved",
                metadata={**(dict(channel.metadata or {})), "xpos_boundary": "phase_only"},
            )
            for channel in bank.channels
        ),
        scheme="xpos_integer_phase_bank",
    )


def yarn_uniform_scaled_phase_bank(
    bank: PhaseBank,
    *,
    scale: int,
    name: str = "yarn_uniform_scaled_phase_bank",
) -> PhaseBank:
    """Model the integer-period layer of a uniform RoPE extension scale."""

    return scaled_phase_bank(bank, scale, name=name, scheme="yarn_uniform_scaled_phase_bank")


def longrope_nonuniform_scaled_phase_bank(
    bank: PhaseBank,
    *,
    scale_factors: Sequence[int],
    name: str = "longrope_nonuniform_scaled_phase_bank",
) -> PhaseBank:
    """Model a non-uniform integer scaling vector over declared phase channels."""

    if len(scale_factors) != len(bank.channels):
        raise ValueError("scale_factors must have one entry per phase channel")
    channels = tuple(
        PhaseChannel(
            name=channel.name,
            period=channel.period * _require_positive_int("scale_factor", int(scale)),
            source=f"{channel.source}; nonuniform_integer_scale={int(scale)}",
            axis=channel.axis,
            metadata={**(dict(channel.metadata or {})), "scale_factor": int(scale)},
        )
        for channel, scale in zip(bank.channels, scale_factors)
    )
    return PhaseBank(
        name=name,
        channels=channels,
        scheme="longrope_nonuniform_scaled_phase_bank",
    )


def phase_grid_2d_collision_report(
    x_bank: PhaseBank,
    y_bank: PhaseBank,
    left: tuple[int, int],
    right: tuple[int, int],
) -> PhaseGrid2DCollisionReport:
    """Return the product-grid collision report for two 2D positions."""

    if len(left) != 2 or len(right) != 2:
        raise ValueError("left and right must be (x, y) coordinate pairs")
    x_report = phase_bank_collision_report(x_bank, left[0], right[0])
    y_report = phase_bank_collision_report(y_bank, left[1], right[1])
    grid_collides = x_report.all_channels_collide and y_report.all_channels_collide
    return PhaseGrid2DCollisionReport(
        schema_id=POSITION_PHASE_GRID_REPORT_SCHEMA_ID,
        x_report=x_report,
        y_report=y_report,
        grid_collides=grid_collides,
        grid_distinguishes=not grid_collides,
    )


__all__ = [
    "DiscretizationPolicy",
    "POSITION_PHASE_CLAIM_BOUNDARY",
    "POSITION_PHASE_COLLISION_REPORT_SCHEMA_ID",
    "POSITION_PHASE_GRID_REPORT_SCHEMA_ID",
    "POSITION_PHASE_LEAN_DECLARATIONS",
    "POSITION_PHASE_SCHEMA_ID",
    "POSITION_PHASE_THEOREM_IDS",
    "PhaseBank",
    "PhaseBankCollisionReport",
    "PhaseChannel",
    "PhaseChannelCollisionResult",
    "PhaseGrid2DCollisionReport",
    "longrope_nonuniform_scaled_phase_bank",
    "period_divides_gap",
    "phase_bank_collision_report",
    "phase_bank_from_periods",
    "phase_channel_collides",
    "phase_channel_distinguishes",
    "phase_grid_2d_collision_report",
    "phase_residue",
    "rope_integer_phase_bank",
    "scaled_periods",
    "scaled_phase_bank",
    "sinusoidal_integer_phase_bank",
    "xpos_integer_phase_bank",
    "yarn_uniform_scaled_phase_bank",
]
