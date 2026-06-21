"""Circle graph coverage helpers for sparse-attention layouts.

This module presents the existing sparse-attention lag certifier as a finite
directed graph on a circle. Vertices are residues ``0..context-1``. A generated
positive lag ``g`` gives each query vertex a directed edge to ``query - g``.

The Lean-backed claims are finite reachability and direct positive-lag coverage
claims. Graph diameter, quality, speed, memory, and attention replacement
claims are outside this module's proof boundary.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .applications.circle_ai import (
    certify_stride_family_coverage,
    normalize_stride_family,
    stride_family_covered_lags,
    stride_family_lag_candidate_list,
)


CIRCLE_GRAPH_COVERAGE_SCHEMA_ID = "circle_calculus.circle_graph_coverage.v0"

CIRCLE_GRAPH_COVERAGE_THEOREM_IDS: tuple[str, ...] = (
    "CC-T0133",
    "CC-T0134",
    "CC-T0135",
    "CC-T0136",
    "CC-T0137",
    "CC-T0138",
)

CIRCLE_GRAPH_COVERAGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.circleGraphStrideReach_eq_div_gcd",
    "Circle.Applications.circleGraphStrideFullCoverage_iff_coprime",
    "Circle.Applications.circleGraphLocalWindowCovers_iff_context_sub_one_le",
    "Circle.Applications.circleGraphFamilyCovers_iff_uncoveredLagList_eq_nil",
    "Circle.Applications.circleGraphFamilyCovers_iff_coveredLagList_length_eq_context_sub_one",
    "Circle.Applications.circleGraphCompleteFixture_9_2_2_3_4_7",
)

CIRCLE_GRAPH_COVERAGE_CLAIM_BOUNDARY = (
    "The proved claim is finite direct positive-lag coverage for a declared "
    "local-window plus stride-family circle graph. This does not prove graph "
    "optimality, sparse-attention quality, model quality, speed, memory savings, "
    "long-context capability, or deployment behavior."
)


@dataclass(frozen=True)
class CircleGraphCoverageReport:
    """Graph-shaped view of a finite sparse-attention coverage certificate."""

    schema_id: str
    context: int
    local_window: int
    path_length: int
    strides: tuple[int, ...]
    lag_generators: tuple[int, ...]
    raw_lag_candidates: tuple[int, ...]
    directed_edge_count: int
    covered_lags: tuple[int, ...]
    uncovered_lags: tuple[int, ...]
    uncovered_lag_intervals: tuple[tuple[int, int], ...]
    coverage_complete: bool
    coverage_ratio: float
    first_uncovered_lag: int | None
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    source_certificate_kind: str
    claim_boundary: str = CIRCLE_GRAPH_COVERAGE_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_positive(value: int, name: str) -> None:
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def circle_graph_lag_generators(
    context: int,
    strides: Sequence[int],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    """Return deduplicated positive lag generators for the circle graph."""

    return stride_family_covered_lags(
        context,
        normalize_stride_family(strides),
        path_length,
        local_window,
    )


def circle_graph_directed_edges(
    context: int,
    lag_generators: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    """Return all directed graph edges induced by positive lag generators."""

    _require_positive(context, "context")
    normalized_generators = tuple(lag_generators)
    for lag in normalized_generators:
        if not isinstance(lag, int) or not (1 <= lag < context):
            raise ValueError("lag_generators must be positive lags below context")
    return tuple(
        (query, (query - lag) % context)
        for query in range(context)
        for lag in normalized_generators
    )


def circle_graph_coverage_report(
    context: int,
    strides: Sequence[int],
    path_length: int,
    local_window: int,
) -> CircleGraphCoverageReport:
    """Return a graph-shaped report backed by the stride-family certifier."""

    _require_positive(context, "context")
    _require_positive(path_length, "path_length")
    _require_positive(local_window, "local_window")
    normalized_strides = normalize_stride_family(strides)
    certificate = certify_stride_family_coverage(
        context,
        normalized_strides,
        path_length,
        local_window,
    )
    generators = circle_graph_lag_generators(
        context,
        normalized_strides,
        path_length,
        local_window,
    )
    raw_candidates = stride_family_lag_candidate_list(
        context,
        normalized_strides,
        path_length,
        local_window,
    )
    theorem_ids = tuple(dict.fromkeys(
        CIRCLE_GRAPH_COVERAGE_THEOREM_IDS + certificate.theorem_ids
    ))
    return CircleGraphCoverageReport(
        schema_id=CIRCLE_GRAPH_COVERAGE_SCHEMA_ID,
        context=context,
        local_window=local_window,
        path_length=path_length,
        strides=normalized_strides,
        lag_generators=generators,
        raw_lag_candidates=raw_candidates,
        directed_edge_count=context * len(generators),
        covered_lags=certificate.covered_lags,
        uncovered_lags=certificate.uncovered_lags,
        uncovered_lag_intervals=certificate.uncovered_lag_intervals,
        coverage_complete=certificate.coverage_complete,
        coverage_ratio=certificate.coverage_ratio,
        first_uncovered_lag=certificate.first_uncovered_lag,
        theorem_ids=theorem_ids,
        lean_declarations=CIRCLE_GRAPH_COVERAGE_LEAN_DECLARATIONS,
        source_certificate_kind=certificate.__class__.__name__,
    )


__all__ = [
    "CIRCLE_GRAPH_COVERAGE_CLAIM_BOUNDARY",
    "CIRCLE_GRAPH_COVERAGE_LEAN_DECLARATIONS",
    "CIRCLE_GRAPH_COVERAGE_SCHEMA_ID",
    "CIRCLE_GRAPH_COVERAGE_THEOREM_IDS",
    "CircleGraphCoverageReport",
    "circle_graph_coverage_report",
    "circle_graph_directed_edges",
    "circle_graph_lag_generators",
]
