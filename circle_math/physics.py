"""Finite physics-style fixtures for Circle Calculus.

The models here are bounded executable references. They are not continuum
physics, QFT, electromagnetism, or formal proofs.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Mapping, Sequence

from .winding import lift


def _require_positive(value: int, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


@dataclass(frozen=True)
class GaugeEdge:
    source: str
    target: str
    phase: int

    def normalized(self, modulus: int) -> "GaugeEdge":
        _require_positive(modulus, "modulus")
        return GaugeEdge(self.source, self.target, self.phase % modulus)

    def reversed(self, modulus: int) -> "GaugeEdge":
        _require_positive(modulus, "modulus")
        return GaugeEdge(self.target, self.source, (-self.phase) % modulus)


@dataclass(frozen=True)
class GaugePath:
    modulus: int
    edges: tuple[GaugeEdge, ...]

    def __post_init__(self) -> None:
        _require_positive(self.modulus, "modulus")
        if not self.edges:
            raise ValueError("path must contain at least one edge")
        normalized = tuple(edge.normalized(self.modulus) for edge in self.edges)
        object.__setattr__(self, "edges", normalized)
        for left, right in zip(normalized, normalized[1:]):
            if left.target != right.source:
                raise ValueError("path edges must compose target-to-source")

    @property
    def source(self) -> str:
        return self.edges[0].source

    @property
    def target(self) -> str:
        return self.edges[-1].target

    @property
    def closed(self) -> bool:
        return self.source == self.target


@dataclass(frozen=True)
class WilsonLoopCertificate:
    modulus: int
    holonomy: int
    closed: bool
    gauge_invariant_under: tuple[str, ...]
    theorem_ids: tuple[str, ...]
    target_ids: tuple[str, ...] = ()
    note: str = "Finite Wilson-loop fixture only; not a continuum physics claim."


@dataclass(frozen=True)
class ClosedGaugeLoopRecord:
    modulus: int
    source: str
    target: str
    phases: tuple[int, ...]
    holonomy: int
    closed: bool
    theorem_ids: tuple[str, ...]
    target_ids: tuple[str, ...] = ("P7-PHYS-001",)
    note: str = "Finite closed-gauge-loop record only; not a continuum physics claim."


@dataclass(frozen=True)
class PeriodicDynamicsRecord:
    modulus: int
    stride: int
    steps: int
    phase: int
    winding: int
    residue: int
    closure_period: int
    closed: bool
    phase_sequence: tuple[int, ...]
    target_ids: tuple[str, ...] = ("P7-PHYS-004",)
    note: str = "Finite periodic-dynamics fixture only; not a continuum physics claim."


@dataclass(frozen=True)
class DefectWindingRecord:
    sectors: int
    turns: int
    orientation: int
    phase_path: tuple[int, ...]
    net_steps: int
    winding: int
    closed: bool
    target_ids: tuple[str, ...] = ("P7-PHYS-004",)
    note: str = "Finite winding-defect toy fixture only; not a continuum defect claim."


def path_holonomy(path: GaugePath) -> int:
    """Return the additive finite phase accumulated along a path."""
    return sum(edge.phase for edge in path.edges) % path.modulus


def concat_paths(left: GaugePath, right: GaugePath) -> GaugePath:
    """Concatenate composable paths with the same finite phase modulus."""
    if left.modulus != right.modulus:
        raise ValueError("paths must use the same modulus")
    if left.target != right.source:
        raise ValueError("left target must equal right source")
    return GaugePath(left.modulus, (*left.edges, *right.edges))


def reverse_path(path: GaugePath) -> GaugePath:
    """Reverse a path and invert every finite link phase."""
    return GaugePath(path.modulus, tuple(edge.reversed(path.modulus) for edge in reversed(path.edges)))


def gauge_value(gauge: Mapping[str, int], vertex: str, modulus: int) -> int:
    _require_positive(modulus, "modulus")
    return gauge.get(vertex, 0) % modulus


def gauge_transform_edge(edge: GaugeEdge, gauge: Mapping[str, int], modulus: int) -> GaugeEdge:
    """Apply the finite additive gauge transform g(source)+U-g(target)."""
    _require_positive(modulus, "modulus")
    source_shift = gauge_value(gauge, edge.source, modulus)
    target_shift = gauge_value(gauge, edge.target, modulus)
    return GaugeEdge(edge.source, edge.target, (edge.phase + source_shift - target_shift) % modulus)


def gauge_transform_path(path: GaugePath, gauge: Mapping[str, int]) -> GaugePath:
    return GaugePath(
        path.modulus,
        tuple(gauge_transform_edge(edge, gauge, path.modulus) for edge in path.edges),
    )


def transformed_holonomy_endpoint_prediction(path: GaugePath, gauge: Mapping[str, int]) -> int:
    """Predict transformed path holonomy from only endpoint gauge values."""
    source_shift = gauge_value(gauge, path.source, path.modulus)
    target_shift = gauge_value(gauge, path.target, path.modulus)
    return (path_holonomy(path) + source_shift - target_shift) % path.modulus


def square_plaquette_path(
    modulus: int,
    *,
    bottom: int,
    right: int,
    top: int,
    left: int,
    origin: str = "v00",
) -> GaugePath:
    """Return a four-edge closed plaquette loop.

    The vertex names are fixed to keep fixture output deterministic. ``origin``
    can be changed for display, but the same origin is reused at closure.
    """
    return GaugePath(
        modulus,
        (
            GaugeEdge(origin, "v10", bottom),
            GaugeEdge("v10", "v11", right),
            GaugeEdge("v11", "v01", top),
            GaugeEdge("v01", origin, left),
        ),
    )


def wilson_loop_certificate(path: GaugePath, gauges: Sequence[Mapping[str, int]]) -> WilsonLoopCertificate:
    """Build a finite closed-loop certificate over sampled gauge choices."""
    holonomy = path_holonomy(path)
    invariant_under: list[str] = []
    if path.closed:
        for index, gauge in enumerate(gauges):
            transformed = gauge_transform_path(path, gauge)
            if path_holonomy(transformed) == holonomy:
                invariant_under.append(f"gauge:{index}")
    return WilsonLoopCertificate(
        modulus=path.modulus,
        holonomy=holonomy,
        closed=path.closed,
        gauge_invariant_under=tuple(invariant_under),
        theorem_ids=("PHYS-T0004", "PHYS-T0005", "PHYS-T0047", "PHYS-T0064"),
        target_ids=("P7-PHYS-001",),
    )


def closed_loop_record(path: GaugePath) -> ClosedGaugeLoopRecord:
    """Build a finite closed-loop record from an already composable path."""
    if not path.closed:
        raise ValueError("closed loop record requires a closed path")
    return ClosedGaugeLoopRecord(
        modulus=path.modulus,
        source=path.source,
        target=path.target,
        phases=tuple(edge.phase for edge in path.edges),
        holonomy=path_holonomy(path),
        closed=True,
        theorem_ids=("PHYS-T0047",),
    )


def identity_closed_loop_record(modulus: int, vertex: str) -> ClosedGaugeLoopRecord:
    """Return the empty checked-loop analogue used by the Lean identity theorem."""
    _require_positive(modulus, "modulus")
    return ClosedGaugeLoopRecord(
        modulus=modulus,
        source=vertex,
        target=vertex,
        phases=(),
        holonomy=0,
        closed=True,
        theorem_ids=("PHYS-T0048", "PHYS-T0052"),
    )


def cycle_closed_loop_record(left: GaugePath, right: GaugePath) -> ClosedGaugeLoopRecord:
    """Concatenate two finite paths that close into a cycle and record holonomy."""
    combined = concat_paths(left, right)
    if combined.target != combined.source:
        raise ValueError("cycle loop record requires endpoints to cycle back")
    record = closed_loop_record(combined)
    return ClosedGaugeLoopRecord(
        modulus=record.modulus,
        source=record.source,
        target=record.target,
        phases=record.phases,
        holonomy=record.holonomy,
        closed=record.closed,
        theorem_ids=("PHYS-T0047", "PHYS-T0049", "PHYS-T0053", "PHYS-T0054", "PHYS-T0055"),
        target_ids=record.target_ids,
        note=record.note,
    )


def three_path_cycle_closed_loop_record(
    first: GaugePath,
    second: GaugePath,
    third: GaugePath,
) -> ClosedGaugeLoopRecord:
    """Concatenate three finite paths that close into a cycle and record holonomy."""
    combined = concat_paths(concat_paths(first, second), third)
    if combined.target != combined.source:
        raise ValueError("three-path cycle record requires endpoints to cycle back")
    record = closed_loop_record(combined)
    return ClosedGaugeLoopRecord(
        modulus=record.modulus,
        source=record.source,
        target=record.target,
        phases=record.phases,
        holonomy=record.holonomy,
        closed=record.closed,
        theorem_ids=(
            "PHYS-T0047",
            "PHYS-T0056",
            "PHYS-T0057",
            "PHYS-T0058",
            "PHYS-T0059",
            "PHYS-T0060",
            "PHYS-T0061",
            "PHYS-T0062",
            "PHYS-T0063",
        ),
        target_ids=record.target_ids,
        note=record.note,
    )


def finite_periodic_dynamics(modulus: int, stride: int, steps: int) -> PeriodicDynamicsRecord:
    """Return a bounded stroboscopic phase/winding record.

    The record follows ``steps`` applications of a nonnegative finite stride on
    ``C_modulus``. The lift is ordinary quotient/remainder bookkeeping of the
    total natural stride count. This is a finite audit fixture, not Floquet
    theory or an action-angle theorem.
    """
    _require_positive(modulus, "modulus")
    if stride < 0:
        raise ValueError("stride must be nonnegative")
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    normalized_stride = stride % modulus
    closure_period = modulus // gcd(modulus, normalized_stride)
    total_motion = stride * steps
    lifted = lift(modulus, total_motion)
    phase_sequence = tuple((stride * step) % modulus for step in range(steps + 1))
    return PeriodicDynamicsRecord(
        modulus=modulus,
        stride=stride,
        steps=steps,
        phase=total_motion % modulus,
        winding=lifted.winding,
        residue=lifted.residue,
        closure_period=closure_period,
        closed=steps % closure_period == 0,
        phase_sequence=phase_sequence,
    )


def finite_defect_winding(sectors: int, turns: int, *, orientation: int = 1) -> DefectWindingRecord:
    """Return a finite winding toy around a marked defect.

    The loop samples a phase clock with ``sectors`` addresses for a chosen
    number of complete turns. The signed orientation is recorded as exact
    finite phase bookkeeping. This is not a continuum vortex or material model.
    """
    _require_positive(sectors, "sectors")
    if turns < 0:
        raise ValueError("turns must be nonnegative")
    if orientation not in (-1, 1):
        raise ValueError("orientation must be -1 or 1")
    total_steps = turns * sectors
    phase_path = tuple((orientation * step) % sectors for step in range(total_steps + 1))
    net_steps = orientation * total_steps
    return DefectWindingRecord(
        sectors=sectors,
        turns=turns,
        orientation=orientation,
        phase_path=phase_path,
        net_steps=net_steps,
        winding=net_steps // sectors,
        closed=phase_path[0] == phase_path[-1],
    )
