from circle_math.generative import (
    SeedRuleProvenance,
    bounded_generator_search,
    coil_orbit_generator,
    compare_generator_to_explicit,
    finite_circle_diagram_generator,
    finite_circle_generator,
    orbit_decomposition_generator,
    physics_loop_diagram_generator,
    proof_glyph_generator,
    regenerate,
)


def test_finite_circle_generator_regenerates_nodes() -> None:
    record = finite_circle_generator(8)

    assert regenerate(record) == tuple(range(8))
    assert record.generated_object == tuple(range(8))
    assert len(record.generated_object) == 8
    assert "GEN-T0001" in record.theorem_ids
    assert "GEN-T0020" in record.theorem_ids


def test_finite_circle_diagram_generator_regenerates_successor_edges() -> None:
    record = finite_circle_diagram_generator(5)
    diagram = regenerate(record)

    assert diagram == record.generated_object
    assert diagram["nodes"][0] == {"id": 0, "label": "0 mod 5"}
    assert diagram["nodes"][-1] == {"id": 4, "label": "4 mod 5"}
    assert diagram["edges"][0] == {"source": 0, "target": 1, "rule": "successor_mod_n"}
    assert diagram["edges"][-1] == {"source": 4, "target": 0, "rule": "successor_mod_n"}
    assert "COMMON-0064" in record.dictionary_ids


def test_physics_loop_diagram_generator_regenerates_closed_plaquette() -> None:
    record = physics_loop_diagram_generator(
        7,
        bottom=2,
        right=3,
        top=-1,
        left=5,
    )
    diagram = regenerate(record)

    assert diagram == record.generated_object
    assert diagram["vertices"] == (
        {"id": "v00"},
        {"id": "v10"},
        {"id": "v11"},
        {"id": "v01"},
    )
    assert diagram["edges"] == (
        {"source": "v00", "target": "v10", "phase": 2, "label": "2 mod 7", "rule": "plaquette_edge_phase"},
        {"source": "v10", "target": "v11", "phase": 3, "label": "3 mod 7", "rule": "plaquette_edge_phase"},
        {"source": "v11", "target": "v01", "phase": 6, "label": "6 mod 7", "rule": "plaquette_edge_phase"},
        {"source": "v01", "target": "v00", "phase": 5, "label": "5 mod 7", "rule": "plaquette_edge_phase"},
    )
    assert diagram["closed"]
    assert diagram["holonomy"] == 2
    assert "PHYS-T0005" in record.theorem_ids
    assert "PHYS-T0012" in record.theorem_ids
    assert "COMMON-0062" in record.dictionary_ids
    assert record.note.endswith("not a formal proof, physics claim, or minimality theorem.")


def test_coil_generator_regenerates_closed_stride_orbit() -> None:
    record = coil_orbit_generator(12, 8, start=0)

    assert regenerate(record) == (0, 8, 4)
    assert record.generated_object == (0, 8, 4)
    assert len(record.generated_object) == 3
    assert record.closure_condition == "stop when the next node has already appeared"
    assert "GEN-T0002" in record.theorem_ids
    assert "GEN-T0021" in record.theorem_ids


def test_orbit_decomposition_generator_partitions_circle() -> None:
    record = orbit_decomposition_generator(12, 8)
    flattened = tuple(node for orbit in record.generated_object for node in orbit)

    assert regenerate(record) == record.generated_object
    assert len(record.generated_object) == 4
    assert all(len(orbit) == 3 for orbit in record.generated_object)
    assert sorted(flattened) == list(range(12))
    assert "GEN-T0003" in record.theorem_ids
    assert "GEN-T0013" in record.theorem_ids


def test_proof_glyph_generator_regenerates_certificate_fields() -> None:
    record = proof_glyph_generator(
        "glyph:c13_stride5_period",
        "CC-T0005",
        "Circle.period_eq_n_div_gcd",
    )

    assert regenerate(record) == {
        "glyph_id": "glyph:c13_stride5_period",
        "theorem_id": "CC-T0005",
        "lean_name": "Circle.period_eq_n_div_gcd",
    }
    assert "COMMON-0033" in record.dictionary_ids


def test_generator_comparison_has_positive_and_negative_cases() -> None:
    compact = compare_generator_to_explicit(finite_circle_generator(128))
    diagram = compare_generator_to_explicit(finite_circle_diagram_generator(32))
    physics_loop = compare_generator_to_explicit(
        physics_loop_diagram_generator(7, bottom=2, right=3, top=-1, left=5)
    )
    noisy = compare_generator_to_explicit(finite_circle_generator(1))

    assert compact.exact_regeneration
    assert compact.generator_shorter
    assert diagram.exact_regeneration
    assert physics_loop.exact_regeneration
    assert noisy.exact_regeneration
    assert not noisy.generator_shorter


def test_bounded_generator_search_reports_scope_and_exact_candidates() -> None:
    broken = finite_circle_generator(12)
    broken = SeedRuleProvenance(
        artifact_id=broken.artifact_id,
        seed=broken.seed,
        rules=broken.rules,
        iteration_schedule=broken.iteration_schedule,
        closure_condition=broken.closure_condition,
        generated_object=(0, 1),
        theorem_ids=broken.theorem_ids,
        dictionary_ids=broken.dictionary_ids,
        note=broken.note,
    )
    search = bounded_generator_search(
        [finite_circle_generator(1), finite_circle_generator(128), broken],
        search_id="finite_circle_node_generators",
    )

    assert search.search_id == "finite_circle_node_generators"
    assert search.finite_search_space
    assert search.candidate_count == 3
    assert search.exact_candidate_count == 2
    assert search.best_exact is not None
    assert search.best_shorter is not None
    assert search.best_shorter.generator_shorter
    assert search.note.endswith("not an optimality theorem.")


def test_empty_bounded_generator_search_has_no_best_candidate() -> None:
    search = bounded_generator_search([], search_id="empty_declared_search")

    assert search.search_id == "empty_declared_search"
    assert search.finite_search_space
    assert search.candidate_count == 0
    assert search.exact_candidate_count == 0
    assert search.best_exact is None
    assert search.best_shorter is None
    assert search.theorem_ids == ("GEN-T0022", "GEN-T0023", "GEN-T0024")
