from __future__ import annotations

from math import gcd

from circle_math.applications import (
    average_candidate_count,
    coil_attention_path,
    local_window_indices,
    loop_exit_certificate,
    loop_required_steps,
    memory_slot,
    memory_slot_collision_count,
    memory_slot_loads,
    mixed_retrieval_target_lags,
    retrieval_hit_rate,
    retrieval_hit_rate_by_lag,
    retrieval_target_index,
    run_content_gated_retrieval_benchmark,
    token_recurrence_budget,
    training_free_loop_budget,
)
from circle_math.finite import Circle
from circle_math.generative import (
    coil_orbit_generator,
    finite_circle_diagram_generator,
    orbit_decomposition_generator,
    physics_loop_diagram_generator,
    proof_glyph_generator,
    regenerate,
)
from circle_math.physics import (
    gauge_transform_path,
    path_holonomy,
    square_plaquette_path,
    transformed_holonomy_endpoint_prediction,
)
from circle_math.winding import lift


def js_mod(value: int, n: int) -> int:
    return ((value % n) + n) % n


def js_rot(n: int, k: int, x: int) -> int:
    return js_mod(x + k, n)


def js_orbit(n: int, stride: int, start: int) -> list[int]:
    seen: set[int] = set()
    out: list[int] = []
    x = js_mod(start, n)
    while x not in seen:
        seen.add(x)
        out.append(x)
        x = js_rot(n, stride, x)
    return out


def js_orbit_decomposition(n: int, stride: int) -> tuple[tuple[int, ...], ...]:
    remaining = set(range(n))
    cycles: list[tuple[int, ...]] = []
    while remaining:
        start = min(remaining)
        cycle = tuple(js_orbit(n, stride, start))
        cycles.append(cycle)
        remaining.difference_update(cycle)
    return tuple(cycles)


def js_finite_circle_diagram(n: int) -> dict:
    nodes = tuple({"id": node, "label": f"{node} mod {n}"} for node in range(n))
    edges = tuple(
        {"source": node, "target": (node + 1) % n, "rule": "successor_mod_n"}
        for node in range(n)
    )
    return {"nodes": nodes, "edges": edges}


def js_proof_glyph(glyph_id: str, theorem_id: str, lean_name: str) -> dict[str, str]:
    return {
        "glyph_id": glyph_id,
        "theorem_id": theorem_id,
        "lean_name": lean_name,
    }


def js_physics_loop_diagram(
    modulus: int,
    *,
    bottom: int,
    right: int,
    top: int,
    left: int,
) -> dict:
    phases = (
        ("v00", "v10", bottom),
        ("v10", "v11", right),
        ("v11", "v01", top),
        ("v01", "v00", left),
    )
    edges = tuple(
        {
            "source": source,
            "target": target,
            "phase": js_mod(phase, modulus),
            "label": f"{js_mod(phase, modulus)} mod {modulus}",
            "rule": "plaquette_edge_phase",
        }
        for source, target, phase in phases
    )
    return {
        "modulus": modulus,
        "vertices": tuple({"id": vertex} for vertex in ("v00", "v10", "v11", "v01")),
        "edges": edges,
        "closed": True,
        "holonomy": js_mod(sum(edge["phase"] for edge in edges), modulus),
    }


def js_square_plaquette_edges(
    modulus: int,
    *,
    bottom: int,
    right: int,
    top: int,
    left: int,
) -> tuple[dict, ...]:
    return (
        {"source": "v00", "target": "v10", "phase": js_mod(bottom, modulus)},
        {"source": "v10", "target": "v11", "phase": js_mod(right, modulus)},
        {"source": "v11", "target": "v01", "phase": js_mod(top, modulus)},
        {"source": "v01", "target": "v00", "phase": js_mod(left, modulus)},
    )


def js_gauge_value(gauge: dict[str, int], vertex: str, modulus: int) -> int:
    return js_mod(gauge.get(vertex, 0), modulus)


def js_gauge_transformed_edges(edges: tuple[dict, ...], gauge: dict[str, int], modulus: int) -> tuple[dict, ...]:
    return tuple(
        {
            "source": edge["source"],
            "target": edge["target"],
            "phase": js_mod(
                edge["phase"]
                + js_gauge_value(gauge, edge["source"], modulus)
                - js_gauge_value(gauge, edge["target"], modulus),
                modulus,
            ),
        }
        for edge in edges
    )


def js_path_holonomy(edges: tuple[dict, ...], modulus: int) -> int:
    return js_mod(sum(edge["phase"] for edge in edges), modulus)


def js_loop_required_steps(loop_period: int, sample_index: int) -> int:
    return js_mod(sample_index, loop_period) + 1


def js_token_recurrence_budget(loop_period: int, token_index: int) -> int:
    return js_loop_required_steps(loop_period, token_index)


def js_training_free_loop_budget(loop_period: int, sample_index: int, max_loops: int) -> int:
    return min(js_loop_required_steps(loop_period, sample_index), max_loops)


def js_memory_slot(bank_size: int, token: int) -> int:
    return js_mod(token, bank_size)


def js_memory_slot_loads(bank_size: int, tokens: tuple[int, ...]) -> tuple[int, ...]:
    loads = [0 for _ in range(bank_size)]
    for token in tokens:
        loads[js_memory_slot(bank_size, token)] += 1
    return tuple(loads)


def js_memory_slot_collision_count(bank_size: int, tokens: tuple[int, ...]) -> int:
    return sum(max(0, load - 1) for load in js_memory_slot_loads(bank_size, tokens))


def js_coil_attention_path(
    sequence_length: int,
    query_index: int,
    stride: int,
    path_length: int,
) -> tuple[int, ...]:
    return tuple(
        js_mod(query_index - step * stride, sequence_length)
        for step in range(1, path_length + 1)
    )


def js_local_window_indices(sequence_length: int, query_index: int, window: int) -> tuple[int, ...]:
    return tuple(js_mod(query_index - step, sequence_length) for step in range(1, window + 1))


def js_retrieval_target_index(sequence_length: int, query_index: int, target_lag: int) -> int:
    return js_mod(query_index - target_lag, sequence_length)


def js_retrieval_hit_rate(
    sequence_length: int,
    query_indices: tuple[int, ...],
    target_lag: int,
    candidate_sets: tuple[tuple[int, ...], ...],
) -> float:
    hits = 0
    for query_index, candidates in zip(query_indices, candidate_sets):
        target = js_retrieval_target_index(sequence_length, query_index, target_lag)
        if target in set(candidates):
            hits += 1
    return hits / len(query_indices)


def js_mixed_retrieval_target_lags(
    query_indices: tuple[int, ...],
    *,
    long_target_lag: int,
    near_target_lag: int,
) -> tuple[int, ...]:
    return tuple(long_target_lag if query_index % 2 == 0 else near_target_lag for query_index in query_indices)


def js_retrieval_hit_rate_by_lag(
    sequence_length: int,
    query_indices: tuple[int, ...],
    target_lags: tuple[int, ...],
    candidate_sets: tuple[tuple[int, ...], ...],
) -> float:
    hits = 0
    for query_index, target_lag, candidates in zip(query_indices, target_lags, candidate_sets):
        target = js_retrieval_target_index(sequence_length, query_index, target_lag)
        if target in set(candidates):
            hits += 1
    return hits / len(query_indices)


def js_average_candidate_count(candidate_sets: tuple[tuple[int, ...], ...]) -> float:
    return sum(len(set(candidates)) for candidates in candidate_sets) / len(candidate_sets)


def js_loop_exit_available(loop_period: int, sample_index: int, max_loops: int) -> bool:
    return js_loop_required_steps(loop_period, sample_index) <= max_loops


def js_loop_overthinking_boundary(loop_period: int, sample_index: int, tolerance: int) -> int:
    return js_loop_required_steps(loop_period, sample_index) + tolerance


def main() -> int:
    cases = [
        (1, 0, 0),
        (5, 2, 17),
        (12, 4, 8),
        (13, 5, 21),
        (18, 6, 7),
    ]
    for n, k, start in cases:
        circle = Circle(n)
        assert circle.node(start) == js_mod(start, n)
        assert circle.rot(start, k) == js_rot(n, k, start)
        assert circle.rot(circle.rot(start, k), k + 1) == js_rot(n, k + 1, js_rot(n, k, start))
        assert circle.orbit(start, k) == js_orbit(n, k, start)
        assert circle.period(k) == n // gcd(n, k)
        assert len(circle.orbit_decomposition(k)) == gcd(n, k)
        lifted = lift(n, start)
        assert lifted.winding == start // n
        assert lifted.residue == start % n
        assert lifted.value == start

    finite_diagram = finite_circle_diagram_generator(8)
    assert regenerate(finite_diagram) == js_finite_circle_diagram(8)

    physics_diagram = physics_loop_diagram_generator(7, bottom=2, right=3, top=-1, left=5)
    assert regenerate(physics_diagram) == js_physics_loop_diagram(7, bottom=2, right=3, top=-1, left=5)

    coil_record = coil_orbit_generator(12, 8, start=0)
    assert regenerate(coil_record) == tuple(js_orbit(12, 8, 0))

    orbit_record = orbit_decomposition_generator(12, 8)
    assert regenerate(orbit_record) == js_orbit_decomposition(12, 8)

    glyph_record = proof_glyph_generator(
        "glyph:c13_stride5_period",
        "CC-T0005",
        "Circle.period_eq_n_div_gcd",
    )
    assert regenerate(glyph_record) == js_proof_glyph(
        "glyph:c13_stride5_period",
        "CC-T0005",
        "Circle.period_eq_n_div_gcd",
    )

    gauge_cases = [
        (23, 2, 5, -7, 4, {"v00": 3, "v10": 9, "v11": 1, "v01": 17}),
        (11, -3, 14, 5, 8, {"v00": -2, "v10": 6, "v11": 13, "v01": 1}),
        (5, 0, 0, 0, 0, {"v00": 4, "v10": 3, "v11": 2, "v01": 1}),
    ]
    for modulus, bottom, right, top, left, gauge in gauge_cases:
        plaquette = square_plaquette_path(
            modulus,
            bottom=bottom,
            right=right,
            top=top,
            left=left,
        )
        js_edges = js_square_plaquette_edges(
            modulus,
            bottom=bottom,
            right=right,
            top=top,
            left=left,
        )
        transformed = gauge_transform_path(plaquette, gauge)
        js_transformed = js_gauge_transformed_edges(js_edges, gauge, modulus)
        assert tuple(
            {"source": edge.source, "target": edge.target, "phase": edge.phase}
            for edge in plaquette.edges
        ) == js_edges
        assert tuple(
            {"source": edge.source, "target": edge.target, "phase": edge.phase}
            for edge in transformed.edges
        ) == js_transformed
        assert path_holonomy(plaquette) == js_path_holonomy(js_edges, modulus)
        assert path_holonomy(transformed) == js_path_holonomy(js_transformed, modulus)
        assert transformed_holonomy_endpoint_prediction(plaquette, gauge) == path_holonomy(plaquette)
        assert path_holonomy(transformed) == path_holonomy(plaquette)

    ai_cases = [
        (1, 0, 1, 0),
        (4, 11, 3, 1),
        (5, 22, 5, 2),
        (8, 19, 2, 3),
        (13, 42, 9, 0),
    ]
    for loop_period, sample_index, max_loops, tolerance in ai_cases:
        required = loop_required_steps(loop_period, sample_index)
        shifted_sample = sample_index + loop_period
        certificate = loop_exit_certificate(
            loop_period,
            sample_index,
            max_loops,
            overthink_tolerance=tolerance,
        )
        assert required == js_loop_required_steps(loop_period, sample_index)
        assert token_recurrence_budget(loop_period, sample_index) == js_token_recurrence_budget(
            loop_period,
            sample_index,
        )
        assert training_free_loop_budget(
            loop_period,
            sample_index,
            max_loops,
        ) == js_training_free_loop_budget(loop_period, sample_index, max_loops)
        assert certificate.exit_available == js_loop_exit_available(loop_period, sample_index, max_loops)
        assert certificate.overthinking_boundary == js_loop_overthinking_boundary(
            loop_period,
            sample_index,
            tolerance,
        )
        assert loop_required_steps(loop_period, shifted_sample) == required
        assert training_free_loop_budget(
            loop_period,
            shifted_sample,
            max_loops,
        ) == js_training_free_loop_budget(loop_period, sample_index, max_loops)
        assert loop_exit_certificate(
            loop_period,
            shifted_sample,
            max_loops,
            overthink_tolerance=tolerance,
        ).overthinking_boundary == certificate.overthinking_boundary

    memory_cases = [
        (1, 0, 0, 1),
        (8, 19, 3, 20),
        (13, 42, 5, 32),
    ]
    for bank_size, token, passes, window_length in memory_cases:
        tokens = tuple(range(window_length))
        slot = memory_slot(bank_size, token)
        assert slot == js_memory_slot(bank_size, token)
        assert memory_slot(bank_size, token + bank_size) == slot
        assert memory_slot(bank_size, token + passes * bank_size) == slot
        assert memory_slot(bank_size, slot) == slot
        assert memory_slot(bank_size, 0) == 0
        assert memory_slot_loads(bank_size, tokens) == js_memory_slot_loads(bank_size, tokens)
        assert memory_slot_collision_count(bank_size, tokens) == js_memory_slot_collision_count(
            bank_size,
            tokens,
        )

    retrieval_cases = [
        (64, tuple(range(64)), 21, 7, 3, 8, 5, 3),
        (31, tuple(range(16)), 12, 4, 3, 5, 6, 2),
    ]
    for sequence_length, query_indices, target_lag, stride, path_length, local_window, wrong_stride, near_lag in retrieval_cases:
        query_index = query_indices[-1]
        assert retrieval_target_index(
            sequence_length,
            query_index,
            target_lag,
        ) == js_retrieval_target_index(sequence_length, query_index, target_lag)
        assert coil_attention_path(
            sequence_length,
            query_index,
            stride,
            path_length,
        ) == js_coil_attention_path(sequence_length, query_index, stride, path_length)
        assert local_window_indices(
            sequence_length,
            query_index,
            local_window,
        ) == js_local_window_indices(sequence_length, query_index, local_window)

        coil_candidates = tuple(
            coil_attention_path(sequence_length, query, stride, path_length)
            for query in query_indices
        )
        local_candidates = tuple(
            local_window_indices(sequence_length, query, local_window)
            for query in query_indices
        )
        wrong_candidates = tuple(
            coil_attention_path(sequence_length, query, wrong_stride, path_length)
            for query in query_indices
        )
        full_candidates = tuple(tuple(range(sequence_length)) for _ in query_indices)
        js_coil_candidates = tuple(
            js_coil_attention_path(sequence_length, query, stride, path_length)
            for query in query_indices
        )
        js_local_candidates = tuple(
            js_local_window_indices(sequence_length, query, local_window)
            for query in query_indices
        )
        js_wrong_candidates = tuple(
            js_coil_attention_path(sequence_length, query, wrong_stride, path_length)
            for query in query_indices
        )
        assert coil_candidates == js_coil_candidates
        assert local_candidates == js_local_candidates
        assert wrong_candidates == js_wrong_candidates
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            coil_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, target_lag, js_coil_candidates)
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            local_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, target_lag, js_local_candidates)
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            wrong_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, target_lag, js_wrong_candidates)
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            target_lag,
            full_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, target_lag, full_candidates)
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            near_lag,
            local_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, near_lag, js_local_candidates)
        assert retrieval_hit_rate(
            sequence_length,
            query_indices,
            near_lag,
            coil_candidates,
        ) == js_retrieval_hit_rate(sequence_length, query_indices, near_lag, js_coil_candidates)

    content_cases = [
        (64, 64, 21, 3, 7, 3, 8),
        (31, 16, 12, 2, 4, 3, 5),
    ]
    for sequence_length, query_count, long_lag, near_lag, stride, path_length, local_window in content_cases:
        query_indices = tuple(range(query_count))
        target_lags = mixed_retrieval_target_lags(
            query_indices,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
        )
        js_target_lags = js_mixed_retrieval_target_lags(
            query_indices,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
        )
        assert target_lags == js_target_lags
        coil_candidates = tuple(
            coil_attention_path(sequence_length, query, stride, path_length)
            for query in query_indices
        )
        local_candidates = tuple(
            local_window_indices(sequence_length, query, local_window)
            for query in query_indices
        )
        gated_candidates = tuple(
            coil if query % 2 == 0 else local
            for query, coil, local in zip(query_indices, coil_candidates, local_candidates)
        )
        wrong_gate_candidates = tuple(
            local if query % 2 == 0 else coil
            for query, coil, local in zip(query_indices, coil_candidates, local_candidates)
        )
        union_candidates = tuple(
            tuple(sorted(set(coil) | set(local)))
            for coil, local in zip(coil_candidates, local_candidates)
        )
        full_candidates = tuple(tuple(range(sequence_length)) for _ in query_indices)
        js_coil_candidates = tuple(
            js_coil_attention_path(sequence_length, query, stride, path_length)
            for query in query_indices
        )
        js_local_candidates = tuple(
            js_local_window_indices(sequence_length, query, local_window)
            for query in query_indices
        )
        js_gated_candidates = tuple(
            coil if query % 2 == 0 else local
            for query, coil, local in zip(query_indices, js_coil_candidates, js_local_candidates)
        )
        js_wrong_gate_candidates = tuple(
            local if query % 2 == 0 else coil
            for query, coil, local in zip(query_indices, js_coil_candidates, js_local_candidates)
        )
        js_union_candidates = tuple(
            tuple(sorted(set(coil) | set(local)))
            for coil, local in zip(js_coil_candidates, js_local_candidates)
        )
        assert gated_candidates == js_gated_candidates
        assert wrong_gate_candidates == js_wrong_gate_candidates
        assert union_candidates == js_union_candidates
        for python_sets, js_sets in [
            (gated_candidates, js_gated_candidates),
            (coil_candidates, js_coil_candidates),
            (local_candidates, js_local_candidates),
            (wrong_gate_candidates, js_wrong_gate_candidates),
            (union_candidates, js_union_candidates),
            (full_candidates, full_candidates),
        ]:
            assert retrieval_hit_rate_by_lag(
                sequence_length,
                query_indices,
                target_lags,
                python_sets,
            ) == js_retrieval_hit_rate_by_lag(
                sequence_length,
                query_indices,
                js_target_lags,
                js_sets,
            )
            assert average_candidate_count(python_sets) == js_average_candidate_count(js_sets)

        benchmark = run_content_gated_retrieval_benchmark(
            sequence_length=sequence_length,
            query_count=query_count,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
            stride=stride,
            path_length=path_length,
            local_window=local_window,
        )
        assert benchmark.content_gated_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_gated_candidates,
        )
        assert benchmark.static_coil_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_coil_candidates,
        )
        assert benchmark.static_local_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_local_candidates,
        )
        assert benchmark.wrong_gate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_wrong_gate_candidates,
        )
        assert benchmark.union_candidate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_union_candidates,
        )
        assert benchmark.full_attention_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            full_candidates,
        )
        assert benchmark.average_gated_candidate_count == js_average_candidate_count(js_gated_candidates)
        assert benchmark.average_union_candidate_count == js_average_candidate_count(js_union_candidates)
        assert benchmark.average_full_candidate_count == js_average_candidate_count(full_candidates)

    print("widget Python parity ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
