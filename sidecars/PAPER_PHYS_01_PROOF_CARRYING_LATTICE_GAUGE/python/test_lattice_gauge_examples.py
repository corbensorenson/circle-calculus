from circle_math.physics import (
    GaugeEdge,
    GaugePath,
    concat_paths,
    gauge_transform_path,
    path_holonomy,
    reverse_path,
    square_plaquette_path,
    transformed_holonomy_endpoint_prediction,
    wilson_loop_certificate,
)


def test_path_holonomy_concatenates_by_addition_mod_n() -> None:
    left = GaugePath(11, (GaugeEdge("a", "b", 3), GaugeEdge("b", "c", 4)))
    right = GaugePath(11, (GaugeEdge("c", "d", 9),))

    combined = concat_paths(left, right)

    assert path_holonomy(combined) == (path_holonomy(left) + path_holonomy(right)) % 11
    assert combined.source == "a"
    assert combined.target == "d"


def test_reverse_path_inverts_holonomy() -> None:
    path = GaugePath(13, (GaugeEdge("a", "b", 5), GaugeEdge("b", "c", 4)))
    reversed_path = reverse_path(path)
    closed = concat_paths(path, reversed_path)

    assert path_holonomy(reversed_path) == (-path_holonomy(path)) % 13
    assert closed.closed
    assert path_holonomy(closed) == 0


def test_gauge_transform_changes_open_path_by_endpoint_values() -> None:
    path = GaugePath(17, (GaugeEdge("a", "b", 6), GaugeEdge("b", "c", 2)))
    gauge = {"a": 4, "b": 9, "c": 12}

    transformed = gauge_transform_path(path, gauge)

    assert path_holonomy(transformed) == transformed_holonomy_endpoint_prediction(path, gauge)
    assert path_holonomy(transformed) == (path_holonomy(path) + gauge["a"] - gauge["c"]) % 17


def test_closed_wilson_loop_is_invariant_under_sampled_gauges() -> None:
    loop = GaugePath(
        19,
        (
            GaugeEdge("a", "b", 3),
            GaugeEdge("b", "c", 7),
            GaugeEdge("c", "a", 11),
        ),
    )
    gauges = (
        {"a": 0, "b": 0, "c": 0},
        {"a": 5, "b": 13, "c": 2},
        {"a": 21, "b": -4, "c": 8},
    )

    certificate = wilson_loop_certificate(loop, gauges)

    assert loop.closed
    assert certificate.holonomy == path_holonomy(loop)
    assert certificate.gauge_invariant_under == ("gauge:0", "gauge:1", "gauge:2")


def test_square_plaquette_fixture_is_closed_and_gauge_invariant() -> None:
    plaquette = square_plaquette_path(23, bottom=2, right=5, top=-7, left=4)
    gauge = {"v00": 3, "v10": 9, "v11": 1, "v01": 17}

    transformed = gauge_transform_path(plaquette, gauge)

    assert plaquette.closed
    assert path_holonomy(plaquette) == (2 + 5 - 7 + 4) % 23
    assert path_holonomy(transformed) == path_holonomy(plaquette)

