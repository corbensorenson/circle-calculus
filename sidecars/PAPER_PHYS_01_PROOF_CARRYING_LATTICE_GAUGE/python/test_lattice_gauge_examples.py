from circle_math.physics import (
    GaugeEdge,
    GaugePath,
    closed_loop_record,
    concat_paths,
    cycle_closed_loop_record,
    finite_defect_winding,
    finite_periodic_dynamics,
    gauge_transform_path,
    path_holonomy,
    reverse_path,
    identity_closed_loop_record,
    square_plaquette_path,
    three_path_cycle_closed_loop_record,
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


def test_singleton_path_holonomy_is_edge_phase_mod_n() -> None:
    path = GaugePath(11, (GaugeEdge("a", "b", 14),))

    assert path_holonomy(path) == 3
    assert path.source == "a"
    assert path.target == "b"


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
    assert "PHYS-T0047" in certificate.theorem_ids


def test_closed_loop_records_identity_and_cycle_holonomy() -> None:
    identity = identity_closed_loop_record(11, "a")
    left = GaugePath(13, (GaugeEdge("a", "b", 5), GaugeEdge("b", "c", 4)))
    right = GaugePath(13, (GaugeEdge("c", "a", 2),))
    gauge = {"a": 7, "b": 3, "c": 11}
    combined = concat_paths(left, right)
    transformed_cycle = gauge_transform_path(combined, gauge)
    cycle = cycle_closed_loop_record(left, right)
    swapped_combined = concat_paths(right, left)
    transformed_swapped = gauge_transform_path(swapped_combined, gauge)
    swapped = cycle_closed_loop_record(right, left)

    assert identity.closed
    assert identity.source == identity.target == "a"
    assert identity.phases == ()
    assert identity.holonomy == 0
    assert identity.theorem_ids == ("PHYS-T0048", "PHYS-T0052")
    assert cycle.closed
    assert cycle.source == cycle.target == "a"
    assert cycle.holonomy == (path_holonomy(left) + path_holonomy(right)) % 13
    assert path_holonomy(transformed_cycle) == cycle.holonomy
    assert path_holonomy(transformed_cycle) == (path_holonomy(left) + path_holonomy(right)) % 13
    assert cycle.theorem_ids == ("PHYS-T0047", "PHYS-T0049", "PHYS-T0053", "PHYS-T0054", "PHYS-T0055")
    assert swapped.closed
    assert swapped.source == swapped.target == "c"
    assert swapped.holonomy == cycle.holonomy
    assert path_holonomy(transformed_swapped) == cycle.holonomy


def test_three_path_cycle_record_preserves_rotated_basepoint_holonomy() -> None:
    first = GaugePath(17, (GaugeEdge("a", "b", 5),))
    second = GaugePath(17, (GaugeEdge("b", "c", 8),))
    third = GaugePath(17, (GaugeEdge("c", "a", -3),))
    gauge = {"a": 4, "b": 9, "c": 13}
    combined = concat_paths(concat_paths(first, second), third)
    transformed = gauge_transform_path(combined, gauge)
    record = three_path_cycle_closed_loop_record(first, second, third)

    rotated = concat_paths(concat_paths(second, third), first)
    transformed_rotated = gauge_transform_path(rotated, gauge)
    rotated_record = three_path_cycle_closed_loop_record(second, third, first)
    rotated_twice = concat_paths(concat_paths(third, first), second)
    transformed_rotated_twice = gauge_transform_path(rotated_twice, gauge)
    rotated_twice_record = three_path_cycle_closed_loop_record(third, first, second)

    assert record.closed
    assert record.source == record.target == "a"
    assert record.holonomy == (path_holonomy(first) + path_holonomy(second) + path_holonomy(third)) % 17
    assert path_holonomy(transformed) == record.holonomy
    assert record.theorem_ids == (
        "PHYS-T0047",
        "PHYS-T0056",
        "PHYS-T0057",
        "PHYS-T0058",
        "PHYS-T0059",
        "PHYS-T0060",
        "PHYS-T0061",
    )
    assert rotated_record.closed
    assert rotated_record.source == rotated_record.target == "b"
    assert rotated_record.holonomy == record.holonomy
    assert path_holonomy(transformed_rotated) == record.holonomy
    assert rotated_twice_record.closed
    assert rotated_twice_record.source == rotated_twice_record.target == "c"
    assert rotated_twice_record.holonomy == record.holonomy
    assert path_holonomy(transformed_rotated_twice) == record.holonomy


def test_closed_loop_record_rejects_open_paths() -> None:
    open_path = GaugePath(17, (GaugeEdge("a", "b", 3),))
    closed_path = GaugePath(17, (GaugeEdge("a", "b", 3), GaugeEdge("b", "a", 5)))

    assert closed_loop_record(closed_path).closed
    try:
        closed_loop_record(open_path)
    except ValueError as error:
        assert "requires a closed path" in str(error)
    else:
        raise AssertionError("open paths must not produce closed-loop records")


def test_square_plaquette_fixture_is_closed_and_gauge_invariant() -> None:
    plaquette = square_plaquette_path(23, bottom=2, right=5, top=-7, left=4)
    gauge = {"v00": 3, "v10": 9, "v11": 1, "v01": 17}

    transformed = gauge_transform_path(plaquette, gauge)

    assert plaquette.closed
    assert path_holonomy(plaquette) == (2 + 5 - 7 + 4) % 23
    assert path_holonomy(transformed) == path_holonomy(plaquette)


def test_finite_periodic_dynamics_records_phase_winding_and_closure() -> None:
    record = finite_periodic_dynamics(12, stride=5, steps=7)
    closed = finite_periodic_dynamics(12, stride=5, steps=12)
    parked = finite_periodic_dynamics(12, stride=0, steps=9)

    assert record.phase == 35 % 12
    assert record.winding == 35 // 12
    assert record.residue == 35 % 12
    assert record.closure_period == 12
    assert not record.closed
    assert record.phase_sequence == (0, 5, 10, 3, 8, 1, 6, 11)
    assert closed.closed
    assert closed.phase == 0
    assert parked.closure_period == 1
    assert parked.closed
    assert record.note.endswith("not a continuum physics claim.")


def test_finite_defect_winding_records_signed_closed_loop() -> None:
    positive = finite_defect_winding(4, turns=2, orientation=1)
    negative = finite_defect_winding(4, turns=2, orientation=-1)

    assert positive.phase_path == (0, 1, 2, 3, 0, 1, 2, 3, 0)
    assert positive.net_steps == 8
    assert positive.winding == 2
    assert positive.closed
    assert negative.phase_path == (0, 3, 2, 1, 0, 3, 2, 1, 0)
    assert negative.net_steps == -8
    assert negative.winding == -2
    assert negative.closed
    assert negative.note.endswith("not a continuum defect claim.")
