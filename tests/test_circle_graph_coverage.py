from __future__ import annotations

import pytest

from circle_math.ai_contracts import (
    CIRCLE_GRAPH_COVERAGE_SCHEMA_ID,
    circle_graph_coverage_report,
    circle_graph_directed_edges,
    circle_graph_lag_generators,
)


def test_circle_graph_complete_sparse_fixture_covers_all_positive_lags() -> None:
    report = circle_graph_coverage_report(
        context=9,
        strides=(3, 4, 7),
        path_length=2,
        local_window=2,
    )

    assert report.schema_id == CIRCLE_GRAPH_COVERAGE_SCHEMA_ID
    assert report.coverage_complete is True
    assert report.covered_lags == (1, 2, 3, 6, 4, 8, 7, 5)
    assert report.uncovered_lags == ()
    assert report.lag_generators == report.covered_lags
    assert report.directed_edge_count == 9 * 8
    assert "CC-T0138" in report.theorem_ids


def test_circle_graph_gap_fixture_exposes_uncovered_intervals() -> None:
    report = circle_graph_coverage_report(
        context=120,
        strides=(7, 13),
        path_length=3,
        local_window=4,
    )

    assert report.coverage_complete is False
    assert report.first_uncovered_lag == 5
    assert report.uncovered_lag_intervals[0] == (5, 6)
    assert report.uncovered_lag_intervals[-1] == (40, 119)
    assert report.directed_edge_count == 120 * len(report.lag_generators)
    assert report.raw_lag_candidates == (1, 2, 3, 4, 7, 14, 21, 13, 26, 39)


def test_circle_graph_directed_edges_follow_query_minus_lag() -> None:
    edges = circle_graph_directed_edges(5, (1, 2))

    assert edges[:4] == ((0, 4), (0, 3), (1, 0), (1, 4))
    assert len(edges) == 10
    assert (4, 2) in edges


def test_circle_graph_lag_generators_reject_invalid_inputs() -> None:
    assert circle_graph_lag_generators(9, (3, 4, 7), 2, 2) == (
        1,
        2,
        3,
        6,
        4,
        8,
        7,
        5,
    )

    with pytest.raises(ValueError):
        circle_graph_directed_edges(0, (1,))
    with pytest.raises(ValueError):
        circle_graph_directed_edges(5, (0,))
    with pytest.raises(ValueError):
        circle_graph_coverage_report(9, (), 2, 2)
