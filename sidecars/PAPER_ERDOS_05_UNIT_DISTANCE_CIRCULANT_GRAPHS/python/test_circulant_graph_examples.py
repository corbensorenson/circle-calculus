from circle_math.extremal import (
    circulant_edges,
    cycle_circulant_example,
    cycle_graph_edges,
    regular_polygon_unit_embedding,
)


def test_cycle_graph_edges_match_circulant_jump_one() -> None:
    assert cycle_graph_edges(6) == circulant_edges(6, [1])


def test_cycle_circulant_unit_distance_example() -> None:
    example = cycle_circulant_example(7)
    assert example.theorem_id == "CC-T0070"
    assert example.connected_theorem_id == "CC-T0071"
    assert example.unit_distance_theorem_id == "CC-T0072"
    assert example.matches_circulant
    assert example.max_unit_distance_error < 1e-12


def test_regular_polygon_embedding_has_expected_size() -> None:
    assert len(regular_polygon_unit_embedding(5)) == 5
