"""Proof-carrying RoPE position distinguishability certifier.

The certifier has two layers:

* an exact discretized phase-bank contract backed by Lean theorem ids, where
  each rotary channel is represented by an integer period and collisions are
  characterized by divisibility of the position gap;
* a numerical real-phase margin scan for ordinary RoPE frequencies. This is an
  engineering diagnostic only, not a formal proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, floor, gcd, pi, tau
from typing import Any, Iterable, Literal, Sequence


DiscretizationPolicy = Literal["round", "floor", "ceil"]


ROPE_CERTIFIER_THEOREMS: tuple[str, ...] = (
    "AIRA-T0021",
    "AIRA-T0022",
    "AIRA-T0023",
    "AIRA-T0024",
    "AIRA-T0025",
    "AIRA-T0026",
    "AIRA-T0027",
    "AIRA-T0028",
)

ROPE_CERTIFIER_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeDiscreteCollision_iff_gap_dvd",
    "Circle.Applications.ropeDiscreteDistinguishable_iff_not_gap_dvd",
    "Circle.Applications.ropeDiscreteCollision_iff_eq_on_context",
    "Circle.Applications.ropePhaseBankCollision_iff_forall_gap_dvd",
    "Circle.Applications.ropePhaseBankDistinguishable_iff_exists_not_gap_dvd",
    "Circle.Applications.ropePhaseBankDistinguishable_of_period_ge_context",
    "Circle.Applications.ropeCollisionPairCountAtGap_pos_iff",
    "Circle.Applications.ropePhaseBankCollision_at_gap_of_forall_dvd",
)

ROPE_REAL_PHASE_PRECURSOR_THEOREMS: tuple[str, ...] = (
    "AIRA-T0029",
    "AIRA-T0030",
    "AIRA-T0031",
    "AIRA-T0032",
)

ROPE_REAL_PHASE_PRECURSOR_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeRealPhaseGapAbs_eq_natGap_mul_abs",
    "Circle.Applications.ropeRealPhaseGapAbs_ge_minGap_mul_lower",
    "Circle.Applications.ropeRealPhaseNatTurnEndpointErrors_ge_margin_of_one_turn_window",
    "Circle.Applications.ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window",
)

ROPE_CERTIFIER_CLAIM_BOUNDARY = (
    "Exact pass/fail is for the declared integer-period discretized RoPE model. "
    "The real-phase margin scan is numerical evidence only. This is not a model-quality, "
    "context-length, perplexity, training-stability, speed, memory, or deployment claim."
)


@dataclass(frozen=True)
class RoPEConfig:
    head_dim: int
    base: float
    context_length: int
    tolerance: float = 1e-6
    discretization: DiscretizationPolicy = "round"


@dataclass(frozen=True)
class ExactDiscreteRoPECertificate:
    pass_exact: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    discretized_periods: tuple[int, ...]
    period_count: int
    context_length: int
    common_collision_gap: int | None
    common_collision_gap_reaches_context: bool
    guaranteed_common_gap_collision_pair_count: int
    sample_collision_pairs: tuple[tuple[int, int], ...]
    assumptions: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class RealPhaseMarginReport:
    pass_margin: bool
    tolerance: float
    worst_margin_radians: float
    worst_gap: int | None
    worst_channel_index: int | None
    worst_channel_period_estimate: float | None
    scanned_gap_count: int
    near_collision_gaps: tuple[tuple[int, float], ...]
    explanation: str
    formal_precursor_theorem_ids: tuple[str, ...] = ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    formal_precursor_lean_declarations: tuple[str, ...] = ROPE_REAL_PHASE_PRECURSOR_LEAN_DECLARATIONS


@dataclass(frozen=True)
class RoPEPositionCertificate:
    schema_id: str
    config: RoPEConfig
    exact_discrete: ExactDiscreteRoPECertificate
    real_phase_margin: RealPhaseMarginReport
    real_period_estimates: tuple[float, ...]
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    claim_boundary: str = ROPE_CERTIFIER_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ROPE_CERTIFIER_PRESETS: dict[str, RoPEConfig] = {
    "llama_style_10000_4k": RoPEConfig(
        head_dim=128,
        base=10000.0,
        context_length=4096,
        tolerance=1e-6,
        discretization="round",
    ),
    "llama_style_10000_128k": RoPEConfig(
        head_dim=128,
        base=10000.0,
        context_length=131_072,
        tolerance=1e-6,
        discretization="round",
    ),
    "llama_style_500000_128k": RoPEConfig(
        head_dim=128,
        base=500000.0,
        context_length=131_072,
        tolerance=1e-6,
        discretization="round",
    ),
}


def validate_rope_config(config: RoPEConfig) -> None:
    if config.head_dim <= 0:
        raise ValueError("head_dim must be positive")
    if config.head_dim % 2 != 0:
        raise ValueError("head_dim must be even because RoPE uses dimension pairs")
    if config.base <= 1.0:
        raise ValueError("base must be greater than 1")
    if config.context_length <= 0:
        raise ValueError("context_length must be positive")
    if config.tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    if config.discretization not in ("round", "floor", "ceil"):
        raise ValueError("discretization must be one of: round, floor, ceil")


def rope_angular_frequencies(head_dim: int, base: float) -> tuple[float, ...]:
    config = RoPEConfig(head_dim=head_dim, base=base, context_length=1)
    validate_rope_config(config)
    return tuple(base ** (-(2 * index) / head_dim) for index in range(head_dim // 2))


def rope_period_estimates(head_dim: int, base: float) -> tuple[float, ...]:
    """Return real-valued position periods for the standard RoPE channel schedule."""
    return tuple(tau / frequency for frequency in rope_angular_frequencies(head_dim, base))


def discretize_rope_periods(
    periods: Sequence[float],
    policy: DiscretizationPolicy = "round",
) -> tuple[int, ...]:
    """Map real period estimates to integer periods for the Lean-backed contract."""
    result: list[int] = []
    for period in periods:
        if policy == "round":
            value = int(floor(period + 0.5))
        elif policy == "floor":
            value = int(floor(period))
        elif policy == "ceil":
            value = int(ceil(period))
        else:
            raise ValueError("policy must be one of: round, floor, ceil")
        result.append(max(1, value))
    return tuple(result)


def capped_lcm(values: Iterable[int], cap: int) -> tuple[int, bool]:
    """Return the LCM until it reaches ``cap``.

    The boolean says whether the exact LCM is known to be at least ``cap``.
    """
    if cap <= 0:
        raise ValueError("cap must be positive")
    current = 1
    for value in values:
        if value <= 0:
            raise ValueError("periods must be positive")
        current = current * value // gcd(current, value)
        if current >= cap:
            return current, True
    return current, current >= cap


def sample_collision_pairs(context_length: int, gap: int, limit: int = 5) -> tuple[tuple[int, int], ...]:
    if gap <= 0 or gap >= context_length:
        return ()
    return tuple((start, start + gap) for start in range(min(limit, context_length - gap)))


def collision_pair_count_at_gap(context_length: int, gap: int) -> int:
    """Count ordered starts whose paired position is exactly ``gap`` ahead."""
    if gap <= 0 or gap >= context_length:
        return 0
    return context_length - gap


def circular_phase_distance(angle: float) -> float:
    """Distance in radians from ``angle`` to the nearest whole turn."""
    return abs((angle + pi) % tau - pi)


def real_phase_nat_turn_error(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    turns: int,
) -> float:
    """Mirror Lean's ``ropeRealPhaseNatTurnError`` for examples and tests."""
    if left < 0 or right < 0:
        raise ValueError("left and right must be nonnegative")
    if turns < 0:
        raise ValueError("turns must be nonnegative")
    phase = abs((right - left) * frequency)
    return abs(phase - turns * full_turn)


def real_phase_best_margin_for_gap(frequencies: Sequence[float], gap: int) -> tuple[float, int]:
    """Return the strongest channel margin for a gap and the channel that attains it."""
    best_margin = -1.0
    best_index = -1
    for index, frequency in enumerate(frequencies):
        margin = circular_phase_distance(gap * frequency)
        if margin > best_margin:
            best_margin = margin
            best_index = index
    return best_margin, best_index


def scan_real_phase_margin(
    *,
    head_dim: int,
    base: float,
    context_length: int,
    tolerance: float,
    near_collision_limit: int = 10,
) -> RealPhaseMarginReport:
    """Numerically scan real RoPE channels for the weakest phase-bank margin."""
    frequencies = rope_angular_frequencies(head_dim, base)
    periods = rope_period_estimates(head_dim, base)
    if context_length <= 1:
        return RealPhaseMarginReport(
            pass_margin=True,
            tolerance=tolerance,
            worst_margin_radians=float("inf"),
            worst_gap=None,
            worst_channel_index=None,
            worst_channel_period_estimate=None,
            scanned_gap_count=0,
            near_collision_gaps=(),
            explanation="A context of length 1 has no unequal position pairs to compare.",
        )

    worst_margin = float("inf")
    worst_gap: int | None = None
    worst_index: int | None = None
    near: list[tuple[int, float]] = []
    for gap in range(1, context_length):
        margin, index = real_phase_best_margin_for_gap(frequencies, gap)
        if margin < worst_margin:
            worst_margin = margin
            worst_gap = gap
            worst_index = index
        if margin <= tolerance and len(near) < near_collision_limit:
            near.append((gap, margin))

    return RealPhaseMarginReport(
        pass_margin=worst_margin > tolerance,
        tolerance=tolerance,
        worst_margin_radians=worst_margin,
        worst_gap=worst_gap,
        worst_channel_index=worst_index,
        worst_channel_period_estimate=None if worst_index is None else periods[worst_index],
        scanned_gap_count=context_length - 1,
        near_collision_gaps=tuple(near),
        explanation=(
            "The numerical real-phase margin is the smallest, over all nonzero position "
            "gaps in the context, of the best channel's circular distance from a full-turn "
            "collision. It is not a Lean proof."
        ),
    )


def certify_rope_positions(config: RoPEConfig) -> RoPEPositionCertificate:
    validate_rope_config(config)
    real_periods = rope_period_estimates(config.head_dim, config.base)
    discrete_periods = discretize_rope_periods(real_periods, config.discretization)
    collision_gap, reaches_context = capped_lcm(discrete_periods, config.context_length)
    exact_pass = reaches_context
    guaranteed_pair_count = 0 if reaches_context else collision_pair_count_at_gap(
        config.context_length,
        collision_gap,
    )
    exact = ExactDiscreteRoPECertificate(
        pass_exact=exact_pass,
        theorem_ids=ROPE_CERTIFIER_THEOREMS,
        lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
        discretized_periods=discrete_periods,
        period_count=len(discrete_periods),
        context_length=config.context_length,
        common_collision_gap=None if reaches_context else collision_gap,
        common_collision_gap_reaches_context=reaches_context,
        guaranteed_common_gap_collision_pair_count=guaranteed_pair_count,
        sample_collision_pairs=sample_collision_pairs(config.context_length, collision_gap),
        assumptions=(
            "Positions are natural numbers in [0, context_length).",
            "Each channel period is a positive integer produced by the declared discretization policy.",
            "Exact discrete collision means equal residues in every declared period channel.",
            "Lean theorem AIRA-T0024 characterizes all-channel collision by divisibility of the position gap.",
            "Lean theorem AIRA-T0025 characterizes bank distinguishability by at least one non-dividing period.",
            "Lean theorem AIRA-T0028 certifies every counted start at the common collision gap as an all-channel collision.",
        ),
        explanation=(
            "PASS: the common exact collision gap is at least the context length, so no two unequal "
            "positions inside the inspected context collide in every discrete channel."
            if exact_pass
            else "FAIL: the common exact collision gap is inside the context, so the listed sample "
            "pairs collide in every discrete channel under the declared integer-period model."
        ),
    )
    margin = scan_real_phase_margin(
        head_dim=config.head_dim,
        base=config.base,
        context_length=config.context_length,
        tolerance=config.tolerance,
    )
    return RoPEPositionCertificate(
        schema_id="circle_calculus.rope_position_distinguishability.v0",
        config=config,
        exact_discrete=exact,
        real_phase_margin=margin,
        real_period_estimates=real_periods,
        theorem_ids=ROPE_CERTIFIER_THEOREMS,
        lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
    )


def certificate_summary_lines(certificate: RoPEPositionCertificate) -> tuple[str, ...]:
    config = certificate.config
    exact = certificate.exact_discrete
    margin = certificate.real_phase_margin
    exact_status = "PASS" if exact.pass_exact else "FAIL"
    margin_status = "PASS" if margin.pass_margin else "WARN"
    gap = ">= context" if exact.common_collision_gap is None else str(exact.common_collision_gap)
    worst_gap = "none" if margin.worst_gap is None else str(margin.worst_gap)
    worst_margin = (
        "inf"
        if margin.worst_margin_radians == float("inf")
        else f"{margin.worst_margin_radians:.12g}"
    )
    return (
        "RoPE position distinguishability certificate",
        f"config: head_dim={config.head_dim} base={config.base:g} context={config.context_length} "
        f"tolerance={config.tolerance:g} discretization={config.discretization}",
        f"exact_discrete_contract={exact_status} common_collision_gap={gap} "
        f"period_count={exact.period_count} "
        f"guaranteed_common_gap_collision_pair_count={exact.guaranteed_common_gap_collision_pair_count}",
        f"real_phase_margin={margin_status} worst_margin_radians={worst_margin} "
        f"worst_gap={worst_gap} scanned_gaps={margin.scanned_gap_count}",
        f"real_phase_formal_precursors={','.join(margin.formal_precursor_theorem_ids)} "
        "(unwrapped and nonnegative full-turn precursors only; not a signed nearest-turn proof)",
        f"theorem_ids={','.join(certificate.theorem_ids)}",
        certificate.claim_boundary,
    )
