from __future__ import annotations

import json
from math import cos, gcd, sin, tau

from circle_math.applications import (
    ai_backend_parity_cases,
    adapter_block_collision_count,
    adapter_block_loads,
    active_token_counts_by_budget,
    average_candidate_count,
    block_cyclic_adapter_parameter_count,
    block_cyclic_cell,
    block_cyclic_cell_collision_count,
    block_cyclic_cell_loads,
    block_cyclic_mixer_output,
    coil_attention_path,
    circulant_mixer_output,
    consecutive_integer_intervals,
    content_route_label,
    default_block_cyclic_input,
    default_block_cyclic_kernel,
    default_circulant_input,
    default_circulant_kernel,
    dense_block_cyclic_matrix,
    dense_circulant_matrix,
    dense_matrix_vector_product,
    dense_adapter_parameter_count,
    fit_content_route_lookup,
    fit_harmonic_feature_lookup,
    fit_loop_budget_lookup,
    fit_loop_block_lookup,
    fit_phase_lookup,
    fit_winding_position_lookup,
    fit_recurrence_resolution_lookup,
    harmonic_feature,
    certify_kv_cache_adapter_request_trace,
    certify_kv_cache_batch,
    certify_kv_cache_window,
    kv_cache_adapter_request_trace_pass_compact,
    kv_cache_batch_retained_iff_no_same_slot_overwrite_trace,
    kv_cache_batch_trace_fresh_iff_next_overwrite_boundary,
    kv_cache_next_overwrite_after_current,
    kv_cache_next_overwrite_token,
    kv_cache_no_same_slot_overwrite_before_current,
    kv_cache_retained_batch_slots_distinct,
    kv_cache_retained_iff_no_same_slot_overwrite_trace,
    kv_cache_same_slot_overwrite_witness_when_stale,
    kv_cache_slot,
    kv_cache_trace_fresh_batch_slots_distinct,
    kv_cache_trace_fresh_iff_next_overwrite_boundary,
    kv_cache_window_contains,
    local_window_indices,
    loop_block_indices,
    loop_exit_certificate,
    loop_exit_step,
    loop_score_active,
    loop_score_trace,
    loop_required_steps,
    looped_recurrent_state,
    looped_recurrent_states,
    lora_adapter_parameter_count,
    memory_slot,
    memory_slot_collision_count,
    memory_slot_loads,
    middle_block_budget_route,
    middle_block_required_blocks,
    mixed_retrieval_target_lags,
    multi_resolution_required_resolutions,
    multicoil_cycle_length,
    multicoil_phase,
    multicoil_phase2,
    multicoil_phase_label,
    multicoil_product_cycle,
    nonperiodic_threshold_label,
    nonstructured_stride_family_control_lags,
    periodic_phase_label,
    phase_channel,
    position_residue,
    position_winding,
    recurrence_resolution_levels,
    retrieval_hit_rate,
    retrieval_hit_rate_by_lag,
    retrieval_target_index,
    predict_content_route_lookup,
    predict_harmonic_feature_lookup,
    predict_phase_lookup,
    predict_winding_position_lookup,
    predict_loop_budget_lookup,
    predict_loop_block_lookup,
    predict_recurrence_resolution_lookup,
    rope_relative_feature,
    run_adapter_parameter_budget_benchmark,
    run_block_cyclic_mixer_benchmark,
    run_content_gated_retrieval_benchmark,
    run_circulant_mixer_benchmark,
    run_harmonic_feature_baseline_benchmark,
    run_learned_content_gate_retrieval_benchmark,
    run_learned_feature_baseline_benchmark,
    run_learned_phase_baseline_benchmark,
    run_learned_middle_block_recurrence_benchmark,
    run_learned_multi_resolution_recurrence_benchmark,
    run_learned_recurrence_schedule_benchmark,
    run_learned_token_level_recurrence_benchmark,
    run_ai_backend_parity_check,
    run_multicoil_closure_benchmark,
    run_phase_channel_benchmark,
    run_stride_family_sparse_attention_benchmark,
    run_tiny_looped_recurrent_prototype,
    run_training_free_loop_wrapper_benchmark,
    run_token_level_recurrence_benchmark,
    run_winding_aware_position_benchmark,
    synthetic_winding_position_dataset,
    certify_stride_family_coverage,
    stride_family_attention_candidates,
    stride_family_coil_residue_list,
    stride_family_coil_residues_no_collision,
    stride_family_covered_lags,
    stride_family_lag_candidate_list,
    stride_family_local_coil_candidates_disjoint,
    stride_family_predecessor_injective_window_context_sufficient_condition,
    stride_family_predecessor_injective_on_lag_candidates,
    stride_family_query_candidate_list,
    structured_stride_family_target_lags,
    token_active_at_step,
    token_recurrence_budget,
    token_recurrence_budgets,
    training_free_loop_budget,
    training_free_loop_budgets,
    rotate_block_cyclic_kernel_rows,
    rotate_kernel,
    capped_lcm,
    certify_rope_positions,
    collision_pair_count_at_gap,
    collision_pair_count_fitting_multiple_count,
    collision_pair_count_at_gap_multiples_closed_form_numerator,
    collision_pair_count_at_gap_multiples_fitting_range,
    collision_pair_count_at_gap_multiples,
    discretize_rope_periods,
    phase_bank_prefix_collision_reports,
    rope_period_estimates,
    RoPEConfig,
    winding_alias_collision_count,
    winding_position,
    winding_position_cycle_length,
    winding_position_feature,
    winding_position_label,
)
from circle_math.finite import Circle
from circle_math.dimensions.quaternion import (
    Quaternion,
    conjugation_action,
    is_pure_quaternion,
    orientation_debug_record,
    quaternion_close,
    spin_sign_related,
    unit_i_phase,
)
from circle_math.dimensions.hopf import (
    hopf_map,
    hopf_phase_record,
    normalize_pair,
    pair_norm_sq,
    phase_rotate,
    point_close,
    sphere_norm_sq,
)
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
from circle_math.physics import (
    GaugeEdge,
    GaugePath,
    concat_paths,
    finite_defect_winding,
    finite_periodic_dynamics,
    gauge_transform_path,
    path_holonomy,
    reverse_path,
    square_plaquette_path,
    three_path_cycle_closed_loop_record,
    transformed_holonomy_endpoint_prediction,
    wilson_loop_certificate,
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


def js_json_length(value: object) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")))


def js_finite_circle_record(n: int, *, broken: bool = False) -> dict:
    generated = (0, 1) if broken else tuple(range(n))
    return {
        "artifact_id": "finite_circle",
        "seed": (("n", n),),
        "rules": (("enumerate_nodes", (("start", 0), ("stop", n))),),
        "iteration_schedule": "i = 0..n-1",
        "closure_condition": "stop before node n, since nodes are residues modulo n",
        "generated_object": generated,
        "theorem_ids": (
            "GEN-T0001",
            "GEN-T0020",
            "GEN-T0040",
            "GEN-T0041",
            "GEN-T0042",
            "GEN-T0043",
            "CC-T0001",
        ),
        "dictionary_ids": ("CC-0001", "CC-0002", "COMMON-0064", "COMMON-0066"),
    }


def js_regenerate(record: dict) -> object:
    seed = dict(record["seed"])
    if record["artifact_id"] == "finite_circle":
        return tuple(range(int(seed["n"])))
    raise ValueError(f"unknown artifact id: {record['artifact_id']}")


def js_record_description(record: dict) -> dict:
    return {
        "artifact_id": record["artifact_id"],
        "seed": record["seed"],
        "rules": record["rules"],
        "iteration_schedule": record["iteration_schedule"],
        "closure_condition": record["closure_condition"],
        "theorem_ids": record["theorem_ids"],
        "dictionary_ids": record["dictionary_ids"],
    }


def js_compare_generator_to_explicit(record: dict) -> dict:
    explicit = {"artifact_id": record["artifact_id"], "generated_object": record["generated_object"]}
    generator = js_record_description(record)
    explicit_length = js_json_length(explicit)
    generator_length = js_json_length(generator)
    return {
        "artifact_id": record["artifact_id"],
        "exact_regeneration": js_regenerate(record) == record["generated_object"],
        "explicit_length": explicit_length,
        "generator_length": generator_length,
        "generator_shorter": generator_length < explicit_length,
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


def js_gauge_edge(source: str, target: str, phase: int, modulus: int) -> dict:
    return {"source": source, "target": target, "phase": js_mod(phase, modulus)}


def js_path_holonomy(edges: tuple[dict, ...], modulus: int) -> int:
    return js_mod(sum(edge["phase"] for edge in edges), modulus)


def js_reverse_edges(edges: tuple[dict, ...], modulus: int) -> tuple[dict, ...]:
    return tuple(
        js_gauge_edge(edge["target"], edge["source"], -edge["phase"], modulus)
        for edge in reversed(edges)
    )


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


def js_wilson_loop_certificate(
    edges: tuple[dict, ...], gauges: tuple[dict[str, int], ...], modulus: int
) -> dict:
    holonomy = js_path_holonomy(edges, modulus)
    invariant_under = []
    closed = bool(edges) and edges[0]["source"] == edges[-1]["target"]
    if closed:
        for index, gauge in enumerate(gauges):
            transformed = js_gauge_transformed_edges(edges, gauge, modulus)
            if js_path_holonomy(transformed, modulus) == holonomy:
                invariant_under.append(f"gauge:{index}")
    return {
        "modulus": modulus,
        "holonomy": holonomy,
        "closed": closed,
        "gauge_invariant_under": tuple(invariant_under),
        "theorem_ids": ("PHYS-T0004", "PHYS-T0005", "PHYS-T0047", "PHYS-T0064"),
    }


def js_three_path_cycle_closed_loop_record(edges: tuple[dict, ...], modulus: int) -> dict:
    closed = bool(edges) and edges[0]["source"] == edges[-1]["target"]
    if not closed:
        raise ValueError("three-path cycle record requires endpoints to cycle back")
    return {
        "modulus": modulus,
        "source": edges[0]["source"],
        "target": edges[-1]["target"],
        "phases": tuple(edge["phase"] for edge in edges),
        "holonomy": js_path_holonomy(edges, modulus),
        "closed": closed,
        "theorem_ids": (
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
    }


def js_finite_periodic_dynamics(modulus: int, stride: int, steps: int) -> dict[str, object]:
    normalized_stride = js_mod(stride, modulus)
    closure_period = modulus // gcd(modulus, normalized_stride)
    total_motion = stride * steps
    return {
        "phase": js_mod(total_motion, modulus),
        "winding": total_motion // modulus,
        "residue": js_mod(total_motion, modulus),
        "closure_period": closure_period,
        "closed": steps % closure_period == 0,
        "phase_sequence": tuple(js_mod(stride * step, modulus) for step in range(steps + 1)),
    }


def js_finite_defect_winding(sectors: int, turns: int, orientation: int) -> dict[str, object]:
    total_steps = turns * sectors
    phase_path = tuple(js_mod(orientation * step, sectors) for step in range(total_steps + 1))
    net_steps = orientation * total_steps
    return {
        "phase_path": phase_path,
        "net_steps": net_steps,
        "winding": net_steps // sectors,
        "closed": phase_path[0] == phase_path[-1],
    }


def gauge_path_edges(path: GaugePath) -> tuple[dict, ...]:
    return tuple(
        {"source": edge.source, "target": edge.target, "phase": edge.phase}
        for edge in path.edges
    )


def js_loop_required_steps(loop_period: int, sample_index: int) -> int:
    return js_mod(sample_index, loop_period) + 1


def js_loop_score_trace(required_steps: int, max_loops: int, overthink_tolerance: int) -> tuple[int, ...]:
    return tuple(
        1 if required_steps <= step <= required_steps + overthink_tolerance else 0
        for step in range(1, max_loops + 1)
    )


def js_loop_score_active(
    loop_period: int,
    sample_index: int,
    step: int,
    overthink_tolerance: int,
) -> bool:
    required = js_loop_required_steps(loop_period, sample_index)
    return required <= step <= required + overthink_tolerance


def js_loop_exit_step(required_steps: int, max_loops: int, overthink_tolerance: int) -> int | None:
    for index, score in enumerate(
        js_loop_score_trace(required_steps, max_loops, overthink_tolerance),
        start=1,
    ):
        if score == 1:
            return index
    return None


def js_loop_exit_certificate(
    loop_period: int,
    sample_index: int,
    max_loops: int,
    overthink_tolerance: int,
) -> dict[str, object]:
    required = js_loop_required_steps(loop_period, sample_index)
    boundary = required + overthink_tolerance
    trace = js_loop_score_trace(required, max_loops, overthink_tolerance)
    exit_step = js_loop_exit_step(required, max_loops, overthink_tolerance)
    first_active_step = required if required <= max_loops else None
    no_active_within_budget = all(
        not js_loop_score_active(loop_period, sample_index, step, overthink_tolerance)
        for step in range(1, max_loops + 1)
    )
    return {
        "required_steps": required,
        "overthinking_boundary": boundary,
        "score_trace": trace,
        "exit_step": exit_step,
        "exit_available": exit_step is not None,
        "within_budget": exit_step is not None and exit_step <= max_loops,
        "within_guardrail": exit_step is not None and exit_step <= boundary,
        "first_active_step": first_active_step,
        "first_active_step_matches_exit": first_active_step == exit_step,
        "exit_available_iff_first_active_within_budget": (exit_step is not None)
        == (first_active_step is not None),
        "no_exit_iff_no_active_within_budget": (exit_step is None) == no_active_within_budget,
    }


def js_token_recurrence_budget(loop_period: int, token_index: int) -> int:
    return js_loop_required_steps(loop_period, token_index)


def js_token_active_at_step(loop_period: int, token_index: int, step: int) -> bool:
    return step <= js_token_recurrence_budget(loop_period, token_index)


def js_token_recurrence_budgets(loop_period: int, token_count: int) -> tuple[int, ...]:
    return tuple(js_token_recurrence_budget(loop_period, token) for token in range(token_count))


def js_looped_recurrent_state(period: int, budget: int) -> int:
    return js_phase_channel(period, budget - 1)


def js_looped_recurrent_states(period: int, budgets: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(js_looped_recurrent_state(period, budget) for budget in budgets)


def js_active_token_counts_by_budget(budgets: tuple[int, ...], max_budget: int) -> tuple[int, ...]:
    return tuple(sum(1 for budget in budgets if budget >= step) for step in range(1, max_budget + 1))


def js_recurrence_resolution_levels(max_budget: int) -> tuple[str, ...]:
    return tuple("coarse" if step % 2 == 1 else "fine" for step in range(1, max_budget + 1))


def js_shifted_budgets(budgets: tuple[int, ...], max_budget: int, shift: int) -> tuple[int, ...]:
    return tuple(js_mod(budget - 1 + shift, max_budget) + 1 for budget in budgets)


def js_recurrence_budget_predictions(
    required_budgets: tuple[int, ...],
    planned_budgets: tuple[int, ...],
    tolerance: int,
) -> tuple[int, ...]:
    return tuple(
        1 if required <= planned <= required + tolerance else 0
        for required, planned in zip(required_budgets, planned_budgets)
    )


def js_accuracy(predictions: tuple[int, ...], labels: tuple[int, ...]) -> float:
    return sum(1 for prediction, label in zip(predictions, labels) if prediction == label) / len(labels)


def js_majority_label(labels: tuple[int, ...]) -> int:
    positives = sum(1 for label in labels if label == 1)
    negatives = len(labels) - positives
    return 1 if positives >= negatives else 0


def js_default_positive_phases(period: int) -> tuple[int, ...]:
    return tuple(phase for phase in range(period) if phase % 3 == 1)


def js_phase_channel(period: int, position: int) -> int:
    return js_mod(position, period)


def js_periodic_phase_label(period: int, position: int, positive_phases: tuple[int, ...]) -> int:
    return 1 if js_phase_channel(period, position) in positive_phases else 0


def js_fit_phase_lookup(
    period: int,
    positions: tuple[int, ...],
    labels: tuple[int, ...],
) -> tuple[int, ...]:
    fallback = js_majority_label(labels)
    counts: list[list[int]] = [[0, 0] for _ in range(period)]
    for position, label in zip(positions, labels):
        counts[js_phase_channel(period, position)][label] += 1
    return tuple(
        fallback if zero_count + one_count == 0 else (1 if one_count >= zero_count else 0)
        for zero_count, one_count in counts
    )


def js_predict_phase_lookup(
    period: int,
    lookup: tuple[int, ...],
    positions: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(lookup[js_phase_channel(period, position)] for position in positions)


def js_harmonic_feature(period: int, position: int, harmonic: int = 1) -> tuple[float, float]:
    angle = tau * harmonic * js_phase_channel(period, position) / period
    return (round(cos(angle), 12), round(sin(angle), 12))


def js_fit_harmonic_feature_lookup(
    period: int,
    positions: tuple[int, ...],
    labels: tuple[int, ...],
    harmonic: int = 1,
) -> tuple[tuple[tuple[float, float], int], ...]:
    counts: dict[tuple[float, float], list[int]] = {}
    for position, label in zip(positions, labels):
        feature = js_harmonic_feature(period, position, harmonic)
        if feature not in counts:
            counts[feature] = [0, 0]
        counts[feature][label] += 1
    entries = []
    for feature, (zero_count, one_count) in counts.items():
        entries.append((feature, 1 if one_count >= zero_count else 0))
    return tuple(sorted(entries))


def js_predict_harmonic_feature_lookup(
    period: int,
    lookup: tuple[tuple[tuple[float, float], int], ...],
    positions: tuple[int, ...],
    harmonic: int = 1,
) -> tuple[int, ...]:
    lookup_map = dict(lookup)
    fallback = js_majority_label(tuple(lookup_map.values()))
    return tuple(
        lookup_map.get(js_harmonic_feature(period, position, harmonic), fallback)
        for position in positions
    )


def js_nonperiodic_threshold_label(position: int, threshold: int) -> int:
    return 1 if position >= threshold else 0


def js_fit_threshold_classifier(
    positions: tuple[int, ...],
    labels: tuple[int, ...],
) -> tuple[int, int]:
    candidates = tuple(range(min(positions), max(positions) + 2))
    best = (-1.0, candidates[0], 1)
    for threshold in candidates:
        for polarity in (1, -1):
            predictions = tuple(
                1 if (position >= threshold) == (polarity == 1) else 0
                for position in positions
            )
            score = js_accuracy(predictions, labels)
            if score > best[0]:
                best = (score, threshold, polarity)
    return best[1], best[2]


def js_predict_threshold_classifier(
    positions: tuple[int, ...],
    threshold: int,
    polarity: int,
) -> tuple[int, ...]:
    return tuple(1 if (position >= threshold) == (polarity == 1) else 0 for position in positions)


def js_fit_position_lookup(
    positions: tuple[int, ...],
    labels: tuple[int, ...],
) -> tuple[int, tuple[tuple[int, int], ...]]:
    fallback = js_majority_label(labels)
    counts: dict[int, list[int]] = {}
    for position, label in zip(positions, labels):
        if position not in counts:
            counts[position] = [0, 0]
        counts[position][label] += 1
    entries = tuple(
        (position, 1 if one_count >= zero_count else 0)
        for position, (zero_count, one_count) in sorted(counts.items())
    )
    return fallback, entries


def js_predict_position_lookup(
    lookup: tuple[int, tuple[tuple[int, int], ...]],
    positions: tuple[int, ...],
) -> tuple[int, ...]:
    fallback, entries = lookup
    lookup_map = dict(entries)
    return tuple(lookup_map.get(position, fallback) for position in positions)


def js_majority_int(values: tuple[int, ...]) -> int:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return min(counts, key=lambda value: (-counts[value], value))


def js_fit_loop_budget_lookup(
    period: int,
    positions: tuple[int, ...],
    budgets: tuple[int, ...],
) -> tuple[int, ...]:
    fallback = js_majority_int(budgets)
    buckets: list[list[int]] = [[] for _ in range(period)]
    for position, budget in zip(positions, budgets):
        buckets[js_mod(position, period)].append(budget)
    return tuple(
        fallback if not bucket else js_majority_int(tuple(bucket))
        for bucket in buckets
    )


def js_predict_loop_budget_lookup(
    period: int,
    lookup: tuple[int, ...],
    positions: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(lookup[js_mod(position, period)] for position in positions)


def js_loop_block_indices(block_count: int, selected_loop_block: tuple[int, int]) -> tuple[int, ...]:
    start, stop = selected_loop_block
    return tuple(range(start, min(stop, block_count)))


def js_middle_block_required_blocks(
    block_count: int,
    selected_loop_block: tuple[int, int],
    sample_indices: tuple[int, ...],
) -> tuple[int, ...]:
    selected = js_loop_block_indices(block_count, selected_loop_block)
    return tuple(selected[js_mod(sample, len(selected))] for sample in sample_indices)


def js_fit_loop_block_lookup(
    period: int,
    positions: tuple[int, ...],
    blocks: tuple[int, ...],
) -> tuple[int, ...]:
    return js_fit_loop_budget_lookup(period, positions, blocks)


def js_predict_loop_block_lookup(
    period: int,
    lookup: tuple[int, ...],
    positions: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(lookup[js_mod(position, period)] for position in positions)


def js_middle_block_predictions(
    required_blocks: tuple[int, ...],
    required_budgets: tuple[int, ...],
    candidate_blocks: tuple[int, ...],
    planned_budgets: tuple[int, ...],
    tolerance: int,
) -> tuple[int, ...]:
    candidates = set(candidate_blocks)
    return tuple(
        1 if required_block in candidates and required <= planned <= required + tolerance else 0
        for required_block, required, planned in zip(required_blocks, required_budgets, planned_budgets)
    )


def js_sampled_middle_block_predictions(
    required_blocks: tuple[int, ...],
    required_budgets: tuple[int, ...],
    planned_blocks: tuple[int, ...],
    planned_budgets: tuple[int, ...],
    tolerance: int,
) -> tuple[int, ...]:
    return tuple(
        1 if required_block == planned_block and required <= planned <= required + tolerance else 0
        for required_block, required, planned_block, planned in zip(
            required_blocks,
            required_budgets,
            planned_blocks,
            planned_budgets,
        )
    )


def js_multi_resolution_required_resolutions(
    max_budget: int,
    required_budgets: tuple[int, ...],
) -> tuple[str, ...]:
    levels = js_recurrence_resolution_levels(max_budget)
    return tuple(levels[budget - 1] for budget in required_budgets)


def js_majority_str(values: tuple[str, ...]) -> str:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return min(counts, key=lambda value: (-counts[value], value))


def js_fit_recurrence_resolution_lookup(
    period: int,
    positions: tuple[int, ...],
    resolutions: tuple[str, ...],
) -> tuple[str, ...]:
    fallback = js_majority_str(resolutions)
    buckets: list[list[str]] = [[] for _ in range(period)]
    for position, resolution in zip(positions, resolutions):
        buckets[js_mod(position, period)].append(resolution)
    return tuple(
        fallback if not bucket else js_majority_str(tuple(bucket))
        for bucket in buckets
    )


def js_predict_recurrence_resolution_lookup(
    period: int,
    lookup: tuple[str, ...],
    positions: tuple[int, ...],
) -> tuple[str, ...]:
    return tuple(lookup[js_mod(position, period)] for position in positions)


def js_multi_resolution_predictions(
    required_budgets: tuple[int, ...],
    required_resolutions: tuple[str, ...],
    planned_budgets: tuple[int, ...],
    planned_resolutions: tuple[str, ...],
    tolerance: int,
) -> tuple[int, ...]:
    return tuple(
        1 if required_resolution == planned_resolution and required <= planned <= required + tolerance else 0
        for required, required_resolution, planned, planned_resolution in zip(
            required_budgets,
            required_resolutions,
            planned_budgets,
            planned_resolutions,
        )
    )


def js_fit_phase_lookup(period: int, positions: tuple[int, ...], labels: tuple[int, ...]) -> tuple[int, ...]:
    fallback = js_majority_label(labels)
    counts = [[0, 0] for _ in range(period)]
    for position, label in zip(positions, labels):
        counts[js_mod(position, period)][label] += 1
    return tuple(
        fallback if zero_count + one_count == 0 else (1 if one_count >= zero_count else 0)
        for zero_count, one_count in counts
    )


def js_predict_phase_lookup(period: int, lookup: tuple[int, ...], positions: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(lookup[js_mod(position, period)] for position in positions)


def js_nonperiodic_threshold_label(position: int, threshold: int) -> int:
    return 1 if position >= threshold else 0


def js_fit_threshold_classifier(positions: tuple[int, ...], labels: tuple[int, ...]) -> tuple[int, int]:
    candidates = tuple(range(min(positions), max(positions) + 2))
    best = (0.0, candidates[0], 1)
    for threshold in candidates:
        for polarity in (1, -1):
            predictions = tuple(
                1 if (position >= threshold) == (polarity == 1) else 0
                for position in positions
            )
            score = js_accuracy(predictions, labels)
            if score > best[0]:
                best = (score, threshold, polarity)
    return best[1], best[2]


def js_predict_threshold_classifier(
    positions: tuple[int, ...],
    threshold: int,
    polarity: int,
) -> tuple[int, ...]:
    return tuple(1 if (position >= threshold) == (polarity == 1) else 0 for position in positions)


def js_training_free_loop_budget(loop_period: int, sample_index: int, max_loops: int) -> int:
    return min(js_loop_required_steps(loop_period, sample_index), max_loops)


def js_training_free_loop_budgets(
    loop_period: int,
    sample_indices: tuple[int, ...],
    max_loops: int,
) -> tuple[int, ...]:
    return tuple(js_training_free_loop_budget(loop_period, sample, max_loops) for sample in sample_indices)


def js_budget_is_full_depth_predictions(planned_budgets: tuple[int, ...], max_loops: int) -> tuple[int, ...]:
    return tuple(1 if budget >= max_loops else 0 for budget in planned_budgets)


def js_budget_histogram(planned_budgets: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (budget, planned_budgets.count(budget))
        for budget in sorted(set(planned_budgets))
    )


def js_lcm(left: int, right: int) -> int:
    return abs(left * right) // gcd(left, right)


def js_multicoil_phase(periods: tuple[int, ...], position: int) -> tuple[int, ...]:
    return tuple(js_mod(position, period) for period in periods)


def js_multicoil_phase2(period_a: int, period_b: int, position: int) -> tuple[int, int]:
    return (js_mod(position, period_a), js_mod(position, period_b))


def js_multicoil_product_cycle(period_a: int, period_b: int) -> int:
    return period_a * period_b


def js_multicoil_cycle_length(periods: tuple[int, ...]) -> int:
    cycle = 1
    for period in periods:
        cycle = js_lcm(cycle, period)
    return cycle


def js_multicoil_phase_label(periods: tuple[int, ...], position: int) -> int:
    phase = js_multicoil_phase(periods, position)
    score = sum((index + 1) * residue for index, residue in enumerate(phase))
    return 1 if score % 4 == 1 else 0


def js_rope_relative_feature(period: int, query_position: int, key_position: int) -> tuple[float, float]:
    lag = js_mod(query_position - key_position, period)
    angle = tau * lag / period
    return (round(cos(angle), 12), round(sin(angle), 12))


def js_rope_period_estimates(head_dim: int, base: float) -> tuple[float, ...]:
    return tuple(tau / (base ** (-(2 * index) / head_dim)) for index in range(head_dim // 2))


def js_discretize_rope_periods(periods: tuple[float, ...], policy: str) -> tuple[int, ...]:
    if policy == "floor":
        return tuple(max(1, int(period // 1)) for period in periods)
    if policy == "ceil":
        return tuple(max(1, int(-(-period // 1))) for period in periods)
    return tuple(max(1, int((period + 0.5) // 1)) for period in periods)


def js_capped_lcm(values: tuple[int, ...], cap: int) -> tuple[int, bool]:
    current = 1
    for value in values:
        current = js_lcm(current, value)
        if current >= cap:
            return (current, True)
    return (current, current >= cap)


def js_collision_pair_count_at_gap_multiples(context: int, gap: int) -> int:
    if gap <= 0 or gap >= context:
        return 0
    fitting_count = js_collision_pair_count_fitting_multiple_count(context, gap)
    total = 0
    for multiple in range(1, fitting_count + 1):
        total += context - multiple * gap
    return total


def js_collision_pair_count_closed_form_numerator(context: int, gap: int) -> int:
    if gap <= 0 or gap >= context:
        return 0
    fitting_count = js_collision_pair_count_fitting_multiple_count(context, gap)
    return fitting_count * (2 * context - gap * (fitting_count + 1))


def js_collision_pair_count_fitting_multiple_count(context: int, gap: int) -> int:
    if gap <= 0 or gap >= context:
        return 0
    return (context - 1) // gap


def js_phase_bank_prefix_collision_reports(
    context: int,
    periods: tuple[int, ...],
    limit: int = 8,
):
    reports = []
    for prefix_length in range(1, min(len(periods), limit) + 1):
        lcm_value, reaches_context = js_capped_lcm(periods[:prefix_length], context)
        reports.append(
            (
                prefix_length,
                None if reaches_context else lcm_value,
                reaches_context,
                0 if reaches_context else js_collision_pair_count_fitting_multiple_count(context, lcm_value),
                0 if reaches_context else js_collision_pair_count_closed_form_numerator(context, lcm_value),
                0 if reaches_context else js_collision_pair_count_at_gap_multiples(context, lcm_value),
            )
        )
    return tuple(reports)


def js_position_residue(period: int, position: int) -> int:
    return js_mod(position, period)


def js_position_winding(period: int, position: int) -> int:
    return position // period


def js_winding_position(period: int, position: int) -> tuple[int, int]:
    return (js_position_winding(period, position), js_position_residue(period, position))


def js_winding_position_feature(period: int, winding_period: int, position: int) -> tuple[int, int]:
    winding, residue = js_winding_position(period, position)
    return (js_mod(winding, winding_period), residue)


def js_winding_position_cycle_length(period: int, winding_period: int) -> int:
    return period * winding_period


def js_winding_position_label(period: int, winding_period: int, position: int) -> int:
    winding_phase, residue = js_winding_position_feature(period, winding_period, position)
    score = residue + 2 * winding_phase
    return 1 if js_mod(score, 5) in (1, 3) else 0


def js_synthetic_winding_position_dataset(
    period: int,
    winding_period: int,
    length: int,
    start: int = 0,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    positions = tuple(range(start, start + length))
    labels = tuple(js_winding_position_label(period, winding_period, position) for position in positions)
    return positions, labels


def js_winding_alias_collision_count(
    period: int,
    positions: tuple[int, ...],
    labels: tuple[int, ...],
) -> int:
    residue_labels: dict[int, set[int]] = {}
    for position, label in zip(positions, labels):
        residue_labels.setdefault(js_position_residue(period, position), set()).add(label)
    ambiguous = {
        residue
        for residue, bucket_labels in residue_labels.items()
        if len(bucket_labels) > 1
    }
    return sum(1 for position in positions if js_position_residue(period, position) in ambiguous)


def js_default_circulant_input(period: int) -> tuple[int, ...]:
    return tuple(((index * index + 3 * index + 1) % 7) - 3 for index in range(period))


def js_default_circulant_kernel(period: int) -> tuple[int, ...]:
    kernel = [0 for _ in range(period)]
    kernel[0] = 2
    if period > 1:
        kernel[1] = -1
    if period > 2:
        kernel[2] = 1
    if period > 4:
        kernel[4] = -2
    return tuple(kernel)


def js_circulant_mixer_output(values: tuple[int, ...], kernel: tuple[int, ...]) -> tuple[int, ...]:
    period = len(values)
    return tuple(
        sum(kernel[offset] * values[js_mod(index - offset, period)] for offset in range(period))
        for index in range(period)
    )


def js_dense_circulant_matrix(kernel: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    period = len(kernel)
    return tuple(
        tuple(kernel[js_mod(row - column, period)] for column in range(period))
        for row in range(period)
    )


def js_dense_matrix_vector_product(
    matrix: tuple[tuple[int, ...], ...], values: tuple[int, ...]
) -> tuple[int, ...]:
    return tuple(sum(entry * value for entry, value in zip(row, values)) for row in matrix)


def js_rotate_kernel(kernel: tuple[int, ...], shift: int) -> tuple[int, ...]:
    period = len(kernel)
    return tuple(kernel[js_mod(index - shift, period)] for index in range(period))


def js_block_cyclic_cell(block_size: int, row: int, column: int) -> tuple[int, int]:
    return (js_mod(row, block_size), js_mod(column, block_size))


def js_block_cyclic_cell_loads(block_size: int, channel_count: int) -> tuple[tuple[int, ...], ...]:
    loads = [[0 for _ in range(block_size)] for _ in range(block_size)]
    for row in range(channel_count):
        for column in range(channel_count):
            block_row, block_column = js_block_cyclic_cell(block_size, row, column)
            loads[block_row][block_column] += 1
    return tuple(tuple(row) for row in loads)


def js_block_cyclic_cell_collision_count(block_size: int, channel_count: int) -> int:
    return sum(
        max(0, load - 1)
        for row in js_block_cyclic_cell_loads(block_size, channel_count)
        for load in row
    )


def js_default_block_cyclic_input(channel_count: int) -> tuple[int, ...]:
    return tuple(((index * index + 5 * index + 2) % 11) - 5 for index in range(channel_count))


def js_default_block_cyclic_kernel(block_size: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(((3 * row - 2 * column + row * column + 1) % 9) - 4 for column in range(block_size))
        for row in range(block_size)
    )


def js_block_cyclic_mixer_output(
    values: tuple[int, ...],
    kernel: tuple[tuple[int, ...], ...],
) -> tuple[int, ...]:
    block_size = len(kernel)
    return tuple(
        sum(kernel[js_mod(row, block_size)][js_mod(column, block_size)] * value for column, value in enumerate(values))
        for row in range(len(values))
    )


def js_dense_block_cyclic_matrix(
    channel_count: int,
    kernel: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    block_size = len(kernel)
    return tuple(
        tuple(kernel[js_mod(row, block_size)][js_mod(column, block_size)] for column in range(channel_count))
        for row in range(channel_count)
    )


def js_rotate_block_cyclic_kernel_rows(
    kernel: tuple[tuple[int, ...], ...],
    shift: int,
) -> tuple[tuple[int, ...], ...]:
    block_size = len(kernel)
    return tuple(kernel[js_mod(row - shift, block_size)] for row in range(block_size))


def js_quaternion_mul(left: Quaternion, right: Quaternion) -> Quaternion:
    return Quaternion(
        left.r * right.r - left.i * right.i - left.j * right.j - left.k * right.k,
        left.r * right.i + left.i * right.r + left.j * right.k - left.k * right.j,
        left.r * right.j - left.i * right.k + left.j * right.r + left.k * right.i,
        left.r * right.k + left.i * right.j - left.j * right.i + left.k * right.r,
    )


def js_quaternion_conjugate(value: Quaternion) -> Quaternion:
    return Quaternion(value.r, -value.i, -value.j, -value.k)


def js_conjugation_action(q: Quaternion, v: Quaternion) -> Quaternion:
    return js_quaternion_mul(js_quaternion_mul(q, v), js_quaternion_conjugate(q))


def js_is_pure_quaternion(value: Quaternion, *, tol: float = 1e-10) -> bool:
    return abs(value.r) <= tol


def js_quaternion_close(left: Quaternion, right: Quaternion, *, tol: float = 1e-10) -> bool:
    return all(
        abs(left_coord - right_coord) <= tol
        for left_coord, right_coord in zip(left.coordinates(), right.coordinates())
    )


def js_spin_sign_related(left: Quaternion, right: Quaternion) -> bool:
    return js_quaternion_close(right, left) or js_quaternion_close(right, -left)


def js_orientation_debug_record(period: int, step: int, vector: Quaternion) -> dict[str, bool | tuple[float, ...]]:
    q = unit_i_phase(tau * js_mod(step, period) / period)
    neg_q = -q
    q_action = js_conjugation_action(q, vector)
    neg_q_action = js_conjugation_action(neg_q, vector)
    return {
        "q_coordinates": q.coordinates(),
        "neg_q_coordinates": neg_q.coordinates(),
        "vector_coordinates": vector.coordinates(),
        "q_action_coordinates": q_action.coordinates(),
        "neg_q_action_coordinates": neg_q_action.coordinates(),
        "input_is_pure": js_is_pure_quaternion(vector),
        "q_action_is_pure": js_is_pure_quaternion(q_action),
        "neg_q_action_is_pure": js_is_pure_quaternion(neg_q_action),
        "representatives_are_distinct": not js_quaternion_close(q, neg_q),
        "actions_match": js_quaternion_close(q_action, neg_q_action),
        "spin_sign_related": js_spin_sign_related(q, neg_q),
    }


def js_complex_mul(left: complex, right: complex) -> complex:
    return complex(
        left.real * right.real - left.imag * right.imag,
        left.real * right.imag + left.imag * right.real,
    )


def js_pair_norm_sq(z0: complex, z1: complex) -> float:
    return z0.real * z0.real + z0.imag * z0.imag + z1.real * z1.real + z1.imag * z1.imag


def js_normalize_pair(z0: complex, z1: complex) -> tuple[complex, complex]:
    norm_sq = js_pair_norm_sq(z0, z1)
    if norm_sq == 0.0:
        raise ValueError("cannot normalize the zero complex pair")
    scale = norm_sq ** 0.5
    return (z0 / scale, z1 / scale)


def js_unit_phase(period: int, step: int) -> complex:
    angle = tau * js_mod(step, period) / period
    return complex(cos(angle), sin(angle))


def js_phase_rotate(z0: complex, z1: complex, phase: complex) -> tuple[complex, complex]:
    return (js_complex_mul(phase, z0), js_complex_mul(phase, z1))


def js_hopf_map(z0: complex, z1: complex) -> tuple[float, float, float]:
    product = js_complex_mul(z0, z1.conjugate())
    return (2.0 * product.real, 2.0 * product.imag, abs(z0) ** 2 - abs(z1) ** 2)


def js_sphere_norm_sq(point: tuple[float, float, float]) -> float:
    x, y, z = point
    return x * x + y * y + z * z


def js_point_close(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
    *,
    tol: float = 1e-10,
) -> bool:
    return all(abs(left_coord - right_coord) <= tol for left_coord, right_coord in zip(left, right))


def js_complex_pair_coordinates(pair: tuple[complex, complex]) -> tuple[tuple[float, float], tuple[float, float]]:
    return ((pair[0].real, pair[0].imag), (pair[1].real, pair[1].imag))


def js_hopf_phase_record(z0: complex, z1: complex, period: int, step: int) -> dict[str, object]:
    normalized = js_normalize_pair(z0, z1)
    phase = js_unit_phase(period, step)
    rotated = js_phase_rotate(*normalized, phase)
    base = js_hopf_map(*normalized)
    rotated_base = js_hopf_map(*rotated)
    return {
        "normalized_pair": js_complex_pair_coordinates(normalized),
        "rotated_pair": js_complex_pair_coordinates(rotated),
        "base_point": base,
        "rotated_base_point": rotated_base,
        "pair_norm_sq": js_pair_norm_sq(*normalized),
        "rotated_pair_norm_sq": js_pair_norm_sq(*rotated),
        "base_norm_sq": js_sphere_norm_sq(base),
        "rotated_base_norm_sq": js_sphere_norm_sq(rotated_base),
        "base_points_match": js_point_close(base, rotated_base),
    }


def js_memory_slot(bank_size: int, token: int) -> int:
    return js_mod(token, bank_size)


def js_kv_cache_slot(cache_size: int, token: int) -> int:
    return js_mod(token, cache_size)


def js_kv_cache_window_contains(cache_size: int, current: int, token: int) -> bool:
    return token <= current and current < token + cache_size


def js_kv_cache_next_overwrite_token(cache_size: int, token: int) -> int:
    return token + cache_size


def js_kv_cache_next_overwrite_after_current(
    cache_size: int,
    current: int,
    token: int,
) -> bool:
    return current < js_kv_cache_next_overwrite_token(cache_size, token)


def js_kv_cache_no_same_slot_overwrite_before_current(
    cache_size: int,
    current: int,
    token: int,
) -> bool:
    if token > current:
        return False
    slot = js_kv_cache_slot(cache_size, token)
    return all(
        js_kv_cache_slot(cache_size, overwrite) != slot
        for overwrite in range(token + 1, current + 1)
    )


def js_kv_cache_same_slot_overwrite_witness_when_stale(
    cache_size: int,
    current: int,
    token: int,
) -> bool:
    if token > current:
        return False
    overwrite = js_kv_cache_next_overwrite_token(cache_size, token)
    return (
        not js_kv_cache_window_contains(cache_size, current, token)
        and token < overwrite <= current
        and js_kv_cache_slot(cache_size, token) == js_kv_cache_slot(cache_size, overwrite)
    )


def js_kv_cache_retained_iff_no_same_slot_overwrite_trace(
    cache_size: int,
    current: int,
    token: int,
) -> bool:
    if token > current:
        return False
    return js_kv_cache_window_contains(cache_size, current, token) == (
        js_kv_cache_no_same_slot_overwrite_before_current(cache_size, current, token)
    )


def js_kv_cache_trace_fresh_iff_next_overwrite_boundary(
    cache_size: int,
    current: int,
    token: int,
) -> bool:
    if token > current:
        return False
    return js_kv_cache_no_same_slot_overwrite_before_current(
        cache_size,
        current,
        token,
    ) == js_kv_cache_next_overwrite_after_current(cache_size, current, token)


def js_kv_cache_retained_batch_slots_distinct(
    cache_size: int,
    current: int,
    tokens: tuple[int, ...],
) -> bool:
    if len(set(tokens)) != len(tokens):
        return False
    if not all(js_kv_cache_window_contains(cache_size, current, token) for token in tokens):
        return False
    slots = tuple(js_kv_cache_slot(cache_size, token) for token in tokens)
    return len(set(slots)) == len(slots)


def js_kv_cache_batch_retained_iff_no_same_slot_overwrite_trace(
    cache_size: int,
    current: int,
    tokens: tuple[int, ...],
) -> bool:
    if any(token > current for token in tokens):
        return False
    all_retained = all(
        js_kv_cache_window_contains(cache_size, current, token) for token in tokens
    )
    all_trace_fresh = all(
        js_kv_cache_no_same_slot_overwrite_before_current(cache_size, current, token)
        for token in tokens
    )
    return all_retained == all_trace_fresh


def js_kv_cache_trace_fresh_batch_slots_distinct(
    cache_size: int,
    current: int,
    tokens: tuple[int, ...],
) -> bool:
    if any(token > current for token in tokens):
        return False
    if len(set(tokens)) != len(tokens):
        return False
    if not all(
        js_kv_cache_no_same_slot_overwrite_before_current(cache_size, current, token)
        for token in tokens
    ):
        return False
    slots = tuple(js_kv_cache_slot(cache_size, token) for token in tokens)
    return len(set(slots)) == len(slots)


def js_kv_cache_batch_trace_fresh_iff_next_overwrite_boundary(
    cache_size: int,
    current: int,
    tokens: tuple[int, ...],
) -> bool:
    if any(token > current for token in tokens):
        return False
    all_trace_fresh = all(
        js_kv_cache_no_same_slot_overwrite_before_current(cache_size, current, token)
        for token in tokens
    )
    all_next_overwrite_after_current = all(
        js_kv_cache_next_overwrite_after_current(cache_size, current, token)
        for token in tokens
    )
    return all_trace_fresh == all_next_overwrite_after_current


def js_dense_adapter_parameter_count(channel_count: int, parameters_per_channel: int) -> int:
    return channel_count * parameters_per_channel


def js_lora_adapter_parameter_count(channel_count: int, parameters_per_channel: int, rank: int) -> int:
    return rank * (channel_count + parameters_per_channel)


def js_block_cyclic_adapter_parameter_count(block_size: int, parameters_per_block: int) -> int:
    return block_size * parameters_per_block


def js_adapter_block_loads(block_size: int, channel_count: int) -> tuple[int, ...]:
    loads = [0 for _ in range(block_size)]
    for channel in range(channel_count):
        loads[js_mod(channel, block_size)] += 1
    return tuple(loads)


def js_adapter_block_collision_count(loads: tuple[int, ...]) -> int:
    return sum(max(0, load - 1) for load in loads)


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


def js_unique_preserving_order(values: tuple[int, ...]) -> tuple[int, ...]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)


def js_stride_family_attention_candidates(
    sequence_length: int,
    query_index: int,
    strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    candidates = list(js_local_window_indices(sequence_length, query_index, local_window))
    for stride in strides:
        candidates.extend(js_coil_attention_path(sequence_length, query_index, stride, path_length))
    return js_unique_preserving_order(tuple(candidates))


def js_stride_family_covered_lags(
    sequence_length: int,
    strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    covered = list(range(1, min(local_window, sequence_length - 1) + 1))
    for stride in strides:
        for step in range(1, path_length + 1):
            lag = js_mod(step * stride, sequence_length)
            if lag != 0:
                covered.append(lag)
    return js_unique_preserving_order(tuple(covered))


def js_stride_family_lag_candidate_list(
    sequence_length: int,
    strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    candidates = list(range(1, local_window + 1))
    for stride in strides:
        for step in range(1, path_length + 1):
            candidates.append(js_mod(step * stride, sequence_length))
    return tuple(candidates)


def js_stride_family_coil_residue_list(
    sequence_length: int,
    strides: tuple[int, ...],
    path_length: int,
) -> tuple[int, ...]:
    residues: list[int] = []
    for stride in strides:
        for step in range(1, path_length + 1):
            residues.append(js_mod(step * stride, sequence_length))
    return tuple(residues)


def js_stride_family_query_candidate_list(
    sequence_length: int,
    query_index: int,
    strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    return tuple(
        js_mod(query_index - js_mod(lag, sequence_length), sequence_length)
        for lag in js_stride_family_lag_candidate_list(
            sequence_length,
            strides,
            path_length,
            local_window,
        )
    )


def js_predecessor_injective_on_lag_candidates(
    sequence_length: int,
    query_index: int,
    lag_candidates: tuple[int, ...],
) -> bool:
    predecessor = {
        lag: js_mod(query_index - js_mod(lag, sequence_length), sequence_length)
        for lag in lag_candidates
    }
    return all(
        predecessor[left] != predecessor[right] or left == right
        for left in lag_candidates
        for right in lag_candidates
    )


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


def js_structured_stride_family_target_lags(
    query_indices: tuple[int, ...],
    strides: tuple[int, ...],
    path_length: int,
    local_window: int,
) -> tuple[int, ...]:
    near_lag = min(3, local_window)
    lag_cycle = [near_lag, *(stride * min(2, path_length) for stride in strides)]
    lag_cycle.append(strides[-1] * path_length)
    return tuple(lag_cycle[index % len(lag_cycle)] for index, _query in enumerate(query_indices))


def js_nonstructured_stride_family_control_lags(
    query_indices: tuple[int, ...],
    sequence_length: int,
) -> tuple[int, ...]:
    return tuple(js_mod(11 * query_index + 17, sequence_length - 1) + 1 for query_index in query_indices)


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


def js_content_route_label(query_index: int) -> int:
    return 1 if query_index % 2 == 0 else 0


def js_fit_content_route_lookup(
    route_period: int,
    query_indices: tuple[int, ...],
    route_labels: tuple[int, ...],
) -> tuple[int, ...]:
    fallback = js_majority_int(route_labels)
    buckets: list[list[int]] = [[] for _ in range(route_period)]
    for query_index, route in zip(query_indices, route_labels):
        buckets[js_mod(query_index, route_period)].append(route)
    return tuple(fallback if not bucket else js_majority_int(tuple(bucket)) for bucket in buckets)


def js_predict_content_route_lookup(
    route_period: int,
    lookup: tuple[int, ...],
    query_indices: tuple[int, ...],
) -> tuple[int, ...]:
    return tuple(lookup[js_mod(query_index, route_period)] for query_index in query_indices)


def js_candidate_sets_for_routes(
    routes: tuple[int, ...],
    coil_candidates: tuple[tuple[int, ...], ...],
    local_candidates: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        coil if route == 1 else local
        for route, coil, local in zip(routes, coil_candidates, local_candidates)
    )


def js_loop_exit_available(loop_period: int, sample_index: int, max_loops: int) -> bool:
    return js_loop_required_steps(loop_period, sample_index) <= max_loops


def js_loop_overthinking_boundary(loop_period: int, sample_index: int, tolerance: int) -> int:
    return js_loop_required_steps(loop_period, sample_index) + tolerance


def js_synthetic_phase_dataset(
    period: int,
    length: int,
    start: int = 0,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    phases = js_default_positive_phases(period)
    positions = tuple(range(start, start + length))
    labels = tuple(js_periodic_phase_label(period, position, phases) for position in positions)
    return positions, labels


def js_synthetic_slot_dataset(
    size: int,
    length: int,
    start: int = 0,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    values = tuple(1 if index % 3 == 1 else 0 for index in range(size))
    positions = tuple(range(start, start + length))
    labels = tuple(values[js_mod(position, size)] for position in positions)
    return positions, labels


def js_fit_map_lookup(
    items: tuple,
    labels: tuple[int, ...],
    key_fn,
) -> tuple[tuple[object, int], ...]:
    counts: dict[object, list[int]] = {}
    for item, label in zip(items, labels):
        key = key_fn(item)
        if key not in counts:
            counts[key] = [0, 0]
        counts[key][label] += 1
    return tuple(
        (key, 1 if one_count >= zero_count else 0)
        for key, (zero_count, one_count) in sorted(counts.items())
    )


def js_predict_map_lookup(
    lookup: tuple[tuple[object, int], ...],
    items: tuple,
    key_fn,
) -> tuple[int, ...]:
    lookup_map = dict(lookup)
    fallback = js_majority_label(tuple(lookup_map.values()))
    return tuple(lookup_map.get(key_fn(item), fallback) for item in items)


def js_synthetic_rope_relative_dataset(
    period: int,
    length: int,
    start: int = 0,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    positive_lags = js_default_positive_phases(period)
    pairs: list[tuple[int, int]] = []
    labels: list[int] = []
    for sample_index in range(start, start + length):
        query_position = sample_index // period
        lag = sample_index % period
        key_position = query_position - lag
        pairs.append((query_position, key_position))
        labels.append(1 if lag in positive_lags else 0)
    return tuple(pairs), tuple(labels)


def js_loop_adaptive_exit_predictions(
    loop_period: int,
    sample_indices: tuple[int, ...],
    budget: int,
) -> tuple[int, ...]:
    return tuple(1 if js_loop_required_steps(loop_period, sample) <= budget else 0 for sample in sample_indices)


def js_ai_backend_parity_cases() -> tuple[tuple[str, tuple[int, ...], tuple[int, ...]], ...]:
    phase_train_positions, phase_train_labels = js_synthetic_phase_dataset(8, 64)
    phase_test_positions, phase_test_labels = js_synthetic_phase_dataset(8, 32, 64)
    phase_lookup = js_fit_phase_lookup(8, phase_train_positions, phase_train_labels)
    phase_predictions = js_predict_phase_lookup(8, phase_lookup, phase_test_positions)
    phase_constant = js_majority_label(phase_train_labels)

    memory_train_tokens, memory_train_labels = js_synthetic_slot_dataset(8, 64)
    memory_test_tokens, memory_test_labels = js_synthetic_slot_dataset(8, 32, 64)
    memory_lookup = js_fit_phase_lookup(8, memory_train_tokens, memory_train_labels)
    memory_predictions = js_predict_phase_lookup(8, memory_lookup, memory_test_tokens)

    adapter_train_channels, adapter_train_labels = js_synthetic_slot_dataset(8, 64)
    adapter_test_channels, adapter_test_labels = js_synthetic_slot_dataset(8, 32, 64)
    adapter_lookup = js_fit_phase_lookup(8, adapter_train_channels, adapter_train_labels)
    adapter_predictions = js_predict_phase_lookup(8, adapter_lookup, adapter_test_channels)

    multicoil_train_positions = tuple(range(140))
    multicoil_test_positions = tuple(range(140, 210))
    multicoil_periods = (5, 7)
    multicoil_train_labels = tuple(
        js_multicoil_phase_label(multicoil_periods, position)
        for position in multicoil_train_positions
    )
    multicoil_test_labels = tuple(
        js_multicoil_phase_label(multicoil_periods, position)
        for position in multicoil_test_positions
    )
    multicoil_lookup = js_fit_map_lookup(
        multicoil_train_positions,
        multicoil_train_labels,
        lambda position: js_multicoil_phase(multicoil_periods, position),
    )
    multicoil_predictions = js_predict_map_lookup(
        multicoil_lookup,
        multicoil_test_positions,
        lambda position: js_multicoil_phase(multicoil_periods, position),
    )

    retrieval_queries = tuple(range(64))
    retrieval_candidates = tuple(
        js_coil_attention_path(64, query_index, 7, 3)
        for query_index in retrieval_queries
    )
    retrieval_predictions = tuple(
        1 if js_retrieval_target_index(64, query_index, 21) in set(candidates) else 0
        for query_index, candidates in zip(retrieval_queries, retrieval_candidates)
    )
    retrieval_labels = tuple(1 for _ in retrieval_queries)

    learned_train_positions, learned_train_labels = js_synthetic_phase_dataset(8, 64)
    learned_test_positions, learned_test_labels = js_synthetic_phase_dataset(8, 32, 64)
    learned_lookup = js_fit_phase_lookup(8, learned_train_positions, learned_train_labels)
    learned_predictions = js_predict_phase_lookup(8, learned_lookup, learned_test_positions)
    learned_control_threshold = (3 * 64) // 4
    learned_control_train_labels = tuple(
        js_nonperiodic_threshold_label(position, learned_control_threshold)
        for position in learned_train_positions
    )
    learned_control_test_labels = tuple(
        js_nonperiodic_threshold_label(position, learned_control_threshold)
        for position in learned_test_positions
    )
    learned_control_threshold_fit, learned_control_polarity = js_fit_threshold_classifier(
        learned_train_positions,
        learned_control_train_labels,
    )
    learned_control_predictions = js_predict_threshold_classifier(
        learned_test_positions,
        learned_control_threshold_fit,
        learned_control_polarity,
    )

    harmonic_train_positions, harmonic_train_labels = js_synthetic_phase_dataset(8, 64)
    harmonic_test_positions, harmonic_test_labels = js_synthetic_phase_dataset(8, 32, 64)
    harmonic_lookup = js_fit_harmonic_feature_lookup(8, harmonic_train_positions, harmonic_train_labels)
    harmonic_predictions = js_predict_harmonic_feature_lookup(8, harmonic_lookup, harmonic_test_positions)

    rope_train_pairs, rope_train_labels = js_synthetic_rope_relative_dataset(8, 64)
    rope_test_pairs, rope_test_labels = js_synthetic_rope_relative_dataset(8, 32, 64)
    rope_lookup = js_fit_map_lookup(
        rope_train_pairs,
        rope_train_labels,
        lambda pair: js_rope_relative_feature(8, pair[0], pair[1]),
    )
    rope_predictions = js_predict_map_lookup(
        rope_lookup,
        rope_test_pairs,
        lambda pair: js_rope_relative_feature(8, pair[0], pair[1]),
    )

    winding_train_positions, winding_train_labels = js_synthetic_winding_position_dataset(8, 4, 64)
    winding_test_positions, winding_test_labels = js_synthetic_winding_position_dataset(8, 4, 32, 64)
    winding_lookup = js_fit_map_lookup(
        winding_train_positions,
        winding_train_labels,
        lambda position: js_winding_position_feature(8, 4, position),
    )
    winding_predictions = js_predict_map_lookup(
        winding_lookup,
        winding_test_positions,
        lambda position: js_winding_position_feature(8, 4, position),
    )

    near_local_candidates = tuple(
        js_local_window_indices(64, query_index, 8)
        for query_index in retrieval_queries
    )
    near_local_predictions = tuple(
        1 if js_retrieval_target_index(64, query_index, 3) in set(candidates) else 0
        for query_index, candidates in zip(retrieval_queries, near_local_candidates)
    )
    near_local_labels = tuple(1 for _ in retrieval_queries)

    gated_target_lags = tuple(21 if query_index % 2 == 0 else 3 for query_index in retrieval_queries)
    gated_coil_candidates = tuple(
        js_coil_attention_path(64, query_index, 7, 3)
        for query_index in retrieval_queries
    )
    gated_local_candidates = tuple(
        js_local_window_indices(64, query_index, 8)
        for query_index in retrieval_queries
    )
    gated_candidates = tuple(
        coil if query_index % 2 == 0 else local
        for query_index, coil, local in zip(retrieval_queries, gated_coil_candidates, gated_local_candidates)
    )
    gated_predictions = tuple(
        1 if js_retrieval_target_index(64, query_index, target_lag) in set(candidates) else 0
        for query_index, target_lag, candidates in zip(retrieval_queries, gated_target_lags, gated_candidates)
    )
    gated_labels = tuple(1 for _ in retrieval_queries)

    looped_test_indices = tuple(range(64, 96))
    looped_predictions = js_loop_adaptive_exit_predictions(4, looped_test_indices, 4)
    looped_labels = tuple(1 for _ in looped_test_indices)

    return (
        ("phase_lookup", phase_predictions, phase_test_labels),
        ("phase_constant_baseline", tuple(phase_constant for _ in phase_test_positions), phase_test_labels),
        ("memory_lookup", memory_predictions, memory_test_labels),
        ("adapter_lookup", adapter_predictions, adapter_test_labels),
        ("multicoil_lookup", multicoil_predictions, multicoil_test_labels),
        ("retrieval_coil_path", retrieval_predictions, retrieval_labels),
        ("retrieval_near_local_window", near_local_predictions, near_local_labels),
        ("retrieval_content_gated", gated_predictions, gated_labels),
        ("learned_feature_cyclic", learned_predictions, learned_test_labels),
        ("harmonic_feature_lookup", harmonic_predictions, harmonic_test_labels),
        ("rope_relative_phase", rope_predictions, rope_test_labels),
        ("winding_aware_position", winding_predictions, winding_test_labels),
        ("looped_recurrence_adaptive_exit", looped_predictions, looped_labels),
        ("learned_feature_nonperiodic_dense_scalar", learned_control_predictions, learned_control_test_labels),
    )


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

    phase_cases = [
        (8, 64, 32),
        (5, 40, 20),
    ]
    for period, train_length, test_length in phase_cases:
        positive_phases = js_default_positive_phases(period)
        train_positions = tuple(range(train_length))
        test_positions = tuple(range(train_length, train_length + test_length))
        train_labels = tuple(periodic_phase_label(period, position, positive_phases) for position in train_positions)
        test_labels = tuple(periodic_phase_label(period, position, positive_phases) for position in test_positions)
        js_train_labels = tuple(
            js_periodic_phase_label(period, position, positive_phases)
            for position in train_positions
        )
        js_test_labels = tuple(
            js_periodic_phase_label(period, position, positive_phases)
            for position in test_positions
        )
        assert train_labels == js_train_labels
        assert test_labels == js_test_labels
        for position in range(train_length + test_length):
            assert phase_channel(period, position) == js_phase_channel(period, position)

        lookup = fit_phase_lookup(period, train_positions, train_labels)
        js_lookup = js_fit_phase_lookup(period, train_positions, js_train_labels)
        assert lookup == js_lookup
        phase_predictions = predict_phase_lookup(period, lookup, test_positions)
        js_phase_predictions = js_predict_phase_lookup(period, js_lookup, test_positions)
        assert phase_predictions == js_phase_predictions
        constant = js_majority_label(js_train_labels)
        constant_predictions = tuple(constant for _ in test_positions)
        threshold, polarity = js_fit_threshold_classifier(train_positions, js_train_labels)
        threshold_predictions = js_predict_threshold_classifier(test_positions, threshold, polarity)

        control_threshold = (3 * train_length) // 4
        control_train_labels = tuple(
            nonperiodic_threshold_label(position, control_threshold)
            for position in train_positions
        )
        control_test_labels = tuple(
            nonperiodic_threshold_label(position, control_threshold)
            for position in test_positions
        )
        js_control_train_labels = tuple(
            js_nonperiodic_threshold_label(position, control_threshold)
            for position in train_positions
        )
        js_control_test_labels = tuple(
            js_nonperiodic_threshold_label(position, control_threshold)
            for position in test_positions
        )
        assert control_train_labels == js_control_train_labels
        assert control_test_labels == js_control_test_labels
        control_lookup = fit_phase_lookup(period, train_positions, control_train_labels)
        js_control_lookup = js_fit_phase_lookup(period, train_positions, js_control_train_labels)
        assert control_lookup == js_control_lookup
        control_phase_predictions = predict_phase_lookup(period, control_lookup, test_positions)
        js_control_phase_predictions = js_predict_phase_lookup(period, js_control_lookup, test_positions)
        assert control_phase_predictions == js_control_phase_predictions
        control_scalar_threshold, control_polarity = js_fit_threshold_classifier(
            train_positions,
            js_control_train_labels,
        )
        control_scalar_predictions = js_predict_threshold_classifier(
            test_positions,
            control_scalar_threshold,
            control_polarity,
        )

        phase_benchmark = run_phase_channel_benchmark(
            period=period,
            train_length=train_length,
            test_length=test_length,
        )
        assert phase_benchmark.phase_channel_accuracy == js_accuracy(js_phase_predictions, js_test_labels)
        assert phase_benchmark.constant_accuracy == js_accuracy(constant_predictions, js_test_labels)

        learned_benchmark = run_learned_phase_baseline_benchmark(
            period=period,
            train_length=train_length,
            test_length=test_length,
        )
        assert learned_benchmark.periodic_phase_accuracy == js_accuracy(js_phase_predictions, js_test_labels)
        assert learned_benchmark.periodic_dense_accuracy == js_accuracy(threshold_predictions, js_test_labels)
        assert learned_benchmark.nonperiodic_phase_accuracy == js_accuracy(
            js_control_phase_predictions,
            js_control_test_labels,
        )
        assert learned_benchmark.nonperiodic_dense_accuracy == js_accuracy(
            control_scalar_predictions,
            js_control_test_labels,
        )

        wrong_period = period - 1
        wrong_lookup = fit_phase_lookup(wrong_period, train_positions, train_labels)
        js_wrong_lookup = js_fit_phase_lookup(wrong_period, train_positions, js_train_labels)
        assert wrong_lookup == js_wrong_lookup
        wrong_predictions = predict_phase_lookup(wrong_period, wrong_lookup, test_positions)
        js_wrong_predictions = js_predict_phase_lookup(wrong_period, js_wrong_lookup, test_positions)
        assert wrong_predictions == js_wrong_predictions
        position_lookup = js_fit_position_lookup(train_positions, js_train_labels)
        position_predictions = js_predict_position_lookup(position_lookup, test_positions)
        control_position_lookup = js_fit_position_lookup(train_positions, js_control_train_labels)
        control_position_predictions = js_predict_position_lookup(control_position_lookup, test_positions)
        learned_feature_benchmark = run_learned_feature_baseline_benchmark(
            period=period,
            wrong_period=wrong_period,
            train_length=train_length,
            test_length=test_length,
        )
        assert learned_feature_benchmark.periodic_cyclic_feature_accuracy == js_accuracy(
            js_phase_predictions,
            js_test_labels,
        )
        assert learned_feature_benchmark.periodic_dense_scalar_accuracy == js_accuracy(
            threshold_predictions,
            js_test_labels,
        )
        assert learned_feature_benchmark.periodic_learned_position_accuracy == js_accuracy(
            position_predictions,
            js_test_labels,
        )
        assert learned_feature_benchmark.periodic_wrong_period_accuracy == js_accuracy(
            js_wrong_predictions,
            js_test_labels,
        )
        assert learned_feature_benchmark.nonperiodic_cyclic_feature_accuracy == js_accuracy(
            js_control_phase_predictions,
            js_control_test_labels,
        )
        assert learned_feature_benchmark.nonperiodic_dense_scalar_accuracy == js_accuracy(
            control_scalar_predictions,
            js_control_test_labels,
        )
        assert learned_feature_benchmark.nonperiodic_learned_position_accuracy == js_accuracy(
            control_position_predictions,
            js_control_test_labels,
        )

        for position in range(train_length + test_length):
            assert harmonic_feature(period, position) == js_harmonic_feature(period, position)
        harmonic_lookup = fit_harmonic_feature_lookup(period, train_positions, train_labels)
        js_harmonic_lookup = js_fit_harmonic_feature_lookup(period, train_positions, js_train_labels)
        assert harmonic_lookup == js_harmonic_lookup
        harmonic_predictions = predict_harmonic_feature_lookup(period, harmonic_lookup, test_positions)
        js_harmonic_predictions = js_predict_harmonic_feature_lookup(
            period,
            js_harmonic_lookup,
            test_positions,
        )
        assert harmonic_predictions == js_harmonic_predictions
        wrong_harmonic_lookup = fit_harmonic_feature_lookup(wrong_period, train_positions, train_labels)
        js_wrong_harmonic_lookup = js_fit_harmonic_feature_lookup(
            wrong_period,
            train_positions,
            js_train_labels,
        )
        assert wrong_harmonic_lookup == js_wrong_harmonic_lookup
        wrong_harmonic_predictions = predict_harmonic_feature_lookup(
            wrong_period,
            wrong_harmonic_lookup,
            test_positions,
        )
        js_wrong_harmonic_predictions = js_predict_harmonic_feature_lookup(
            wrong_period,
            js_wrong_harmonic_lookup,
            test_positions,
        )
        assert wrong_harmonic_predictions == js_wrong_harmonic_predictions
        control_harmonic_lookup = js_fit_harmonic_feature_lookup(
            period,
            train_positions,
            js_control_train_labels,
        )
        control_harmonic_predictions = js_predict_harmonic_feature_lookup(
            period,
            control_harmonic_lookup,
            test_positions,
        )

        harmonic_benchmark = run_harmonic_feature_baseline_benchmark(
            period=period,
            wrong_period=wrong_period,
            train_length=train_length,
            test_length=test_length,
        )
        assert harmonic_benchmark.observed_feature_count == len(js_harmonic_lookup)
        assert harmonic_benchmark.cyclic_phase_accuracy == js_accuracy(js_phase_predictions, js_test_labels)
        assert harmonic_benchmark.harmonic_feature_accuracy == js_accuracy(
            js_harmonic_predictions,
            js_test_labels,
        )
        assert harmonic_benchmark.wrong_harmonic_accuracy == js_accuracy(
            js_wrong_harmonic_predictions,
            js_test_labels,
        )
        assert harmonic_benchmark.scalar_threshold_accuracy == js_accuracy(
            threshold_predictions,
            js_test_labels,
        )
        assert harmonic_benchmark.learned_position_accuracy == js_accuracy(
            position_predictions,
            js_test_labels,
        )
        assert harmonic_benchmark.nonperiodic_harmonic_accuracy == js_accuracy(
            control_harmonic_predictions,
            js_control_test_labels,
        )
        assert harmonic_benchmark.nonperiodic_scalar_threshold_accuracy == js_accuracy(
            control_scalar_predictions,
            js_control_test_labels,
        )

    js_backend_cases = js_ai_backend_parity_cases()
    assert ai_backend_parity_cases() == js_backend_cases
    backend_parity = run_ai_backend_parity_check()
    js_cpu_scores = tuple(
        (name, js_accuracy(predictions, labels))
        for name, predictions, labels in js_backend_cases
    )
    assert backend_parity.fixture_count == len(js_backend_cases)
    assert backend_parity.cpu_scores == js_cpu_scores
    if backend_parity.mlx_available:
        assert backend_parity.mlx_scores
        assert backend_parity.max_abs_delta is not None
    else:
        assert backend_parity.mlx_scores == ()
        assert backend_parity.max_abs_delta is None

    finite_diagram = finite_circle_diagram_generator(8)
    assert regenerate(finite_diagram) == js_finite_circle_diagram(8)

    physics_diagram = physics_loop_diagram_generator(7, bottom=2, right=3, top=-1, left=5)
    assert regenerate(physics_diagram) == js_physics_loop_diagram(7, bottom=2, right=3, top=-1, left=5)

    coil_record = coil_orbit_generator(12, 8, start=0)
    assert regenerate(coil_record) == tuple(js_orbit(12, 8, 0))

    orbit_record = orbit_decomposition_generator(12, 8)
    assert regenerate(orbit_record) == js_orbit_decomposition(12, 8)

    orbit_family_cases = [
        (12, 8),
        (13, 5),
        (18, 6),
        (20, 0),
    ]
    for n, stride in orbit_family_cases:
        generated = regenerate(orbit_decomposition_generator(n, stride))
        js_generated = js_orbit_decomposition(n, stride)
        flattened = tuple(node for orbit in generated for node in orbit)
        assert generated == js_generated
        assert len(generated) == gcd(n, stride)
        assert len(set(flattened)) == n
        assert set(flattened) == set(range(n))
        assert len(flattened) == n

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

    for n in (1, 8, 128):
        comparison = compare_generator_to_explicit(finite_circle_generator(n))
        js_comparison = js_compare_generator_to_explicit(js_finite_circle_record(n))
        assert comparison.exact_regeneration == js_comparison["exact_regeneration"]
        assert comparison.explicit_length == js_comparison["explicit_length"]
        assert comparison.generator_length == js_comparison["generator_length"]
        assert comparison.generator_shorter == js_comparison["generator_shorter"]

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
    js_search_comparisons = tuple(
        js_compare_generator_to_explicit(record)
        for record in (
            js_finite_circle_record(1),
            js_finite_circle_record(128),
            js_finite_circle_record(12, broken=True),
        )
    )
    js_exact = tuple(comparison for comparison in js_search_comparisons if comparison["exact_regeneration"])
    js_shorter = tuple(comparison for comparison in js_exact if comparison["generator_shorter"])
    assert search.candidate_count == len(js_search_comparisons)
    assert search.exact_candidate_count == len(js_exact)
    assert search.exact_candidate_count <= search.candidate_count
    assert search.best_exact is not None
    assert search.best_shorter is not None
    assert (search.best_exact is not None) == (search.exact_candidate_count > 0)
    assert search.best_exact is None or search.candidate_count > 0
    assert search.best_exact.generator_length == min(
        comparison["generator_length"]
        for comparison in js_exact
    )
    assert search.best_shorter.generator_length == min(
        comparison["generator_length"]
        for comparison in js_shorter
    )
    generator_search_theorem_ids = (
        "GEN-T0022",
        "GEN-T0023",
        "GEN-T0024",
        "GEN-T0025",
        "GEN-T0026",
        "GEN-T0027",
        "GEN-T0028",
        "GEN-T0029",
        "GEN-T0030",
        "GEN-T0031",
        "GEN-T0032",
        "GEN-T0033",
        "GEN-T0034",
        "GEN-T0035",
        "GEN-T0036",
        "GEN-T0037",
        "GEN-T0038",
        "GEN-T0039",
        "GEN-T0044",
        "GEN-T0045",
    )
    assert search.theorem_ids == generator_search_theorem_ids
    empty_search = bounded_generator_search([], search_id="empty_declared_search")
    assert empty_search.candidate_count == 0
    assert empty_search.exact_candidate_count == 0
    assert empty_search.best_exact is None
    assert (empty_search.best_exact is None) == (empty_search.exact_candidate_count == 0)
    assert empty_search.best_shorter is None
    assert empty_search.theorem_ids == generator_search_theorem_ids

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

    path_cases = [
        (17, 6, 2, 9, {"a": 4, "b": 9, "c": 12, "d": 3}),
        (23, -5, 31, 8, {"a": 20, "b": -3, "c": 7, "d": 11}),
    ]
    for modulus, ab, bc, cd, gauge in path_cases:
        left = GaugePath(
            modulus,
            (
                GaugeEdge("a", "b", ab),
                GaugeEdge("b", "c", bc),
            ),
        )
        right = GaugePath(modulus, (GaugeEdge("c", "d", cd),))
        combined = concat_paths(left, right)
        reversed_path = reverse_path(combined)
        closed = concat_paths(combined, reversed_path)
        transformed = gauge_transform_path(combined, gauge)
        js_left = (
            js_gauge_edge("a", "b", ab, modulus),
            js_gauge_edge("b", "c", bc, modulus),
        )
        js_right = (js_gauge_edge("c", "d", cd, modulus),)
        js_combined = (*js_left, *js_right)
        js_reversed = js_reverse_edges(js_combined, modulus)
        js_closed = (*js_combined, *js_reversed)
        js_transformed = js_gauge_transformed_edges(js_combined, gauge, modulus)
        assert gauge_path_edges(left) == js_left
        assert gauge_path_edges(right) == js_right
        assert gauge_path_edges(combined) == js_combined
        assert gauge_path_edges(reversed_path) == js_reversed
        assert gauge_path_edges(closed) == js_closed
        assert gauge_path_edges(transformed) == js_transformed
        assert path_holonomy(combined) == js_path_holonomy(js_combined, modulus)
        assert path_holonomy(combined) == (
            path_holonomy(left) + path_holonomy(right)
        ) % modulus
        assert path_holonomy(reversed_path) == js_path_holonomy(js_reversed, modulus)
        assert path_holonomy(reversed_path) == (-path_holonomy(combined)) % modulus
        assert closed.closed
        assert path_holonomy(closed) == js_path_holonomy(js_closed, modulus)
        assert path_holonomy(closed) == 0
        assert path_holonomy(transformed) == js_path_holonomy(js_transformed, modulus)
        assert path_holonomy(transformed) == transformed_holonomy_endpoint_prediction(
            combined,
            gauge,
        )

    wilson_cases = [
        (
            19,
            (3, 7, 11),
            (
                {"a": 0, "b": 0, "c": 0},
                {"a": 5, "b": 13, "c": 2},
                {"a": 21, "b": -4, "c": 8},
            ),
        ),
        (
            11,
            (-3, 4, 19),
            (
                {"a": 0, "b": 0, "c": 0},
                {"a": 2, "b": 5, "c": 9},
                {"a": -7, "b": 12, "c": 3},
            ),
        ),
    ]
    for modulus, (ab, bc, ca), gauges in wilson_cases:
        first = GaugePath(modulus, (GaugeEdge("a", "b", ab),))
        second = GaugePath(modulus, (GaugeEdge("b", "c", bc),))
        third = GaugePath(modulus, (GaugeEdge("c", "a", ca),))
        loop = concat_paths(concat_paths(first, second), third)
        js_edges = (
            js_gauge_edge("a", "b", ab, modulus),
            js_gauge_edge("b", "c", bc, modulus),
            js_gauge_edge("c", "a", ca, modulus),
        )
        certificate = wilson_loop_certificate(loop, gauges)
        js_certificate = js_wilson_loop_certificate(js_edges, gauges, modulus)
        record = three_path_cycle_closed_loop_record(first, second, third)
        js_record = js_three_path_cycle_closed_loop_record(js_edges, modulus)
        rotated = concat_paths(concat_paths(second, third), first)
        rotated_record = three_path_cycle_closed_loop_record(second, third, first)
        js_rotated_edges = (js_edges[1], js_edges[2], js_edges[0])
        assert gauge_path_edges(loop) == js_edges
        assert certificate.holonomy == js_certificate["holonomy"]
        assert certificate.closed == js_certificate["closed"]
        assert certificate.gauge_invariant_under == js_certificate["gauge_invariant_under"]
        assert certificate.theorem_ids == js_certificate["theorem_ids"]
        assert record.source == js_record["source"]
        assert record.target == js_record["target"]
        assert record.phases == js_record["phases"]
        assert record.holonomy == js_record["holonomy"]
        assert record.closed == js_record["closed"]
        assert record.theorem_ids == js_record["theorem_ids"]
        assert gauge_path_edges(rotated) == js_rotated_edges
        assert rotated_record.holonomy == record.holonomy
        transformed_holonomies = []
        for gauge in gauges:
            transformed = gauge_transform_path(loop, gauge)
            js_transformed = js_gauge_transformed_edges(js_edges, gauge, modulus)
            transformed_rotated = gauge_transform_path(rotated, gauge)
            js_transformed_rotated = js_gauge_transformed_edges(js_rotated_edges, gauge, modulus)
            assert gauge_path_edges(transformed) == js_transformed
            assert gauge_path_edges(transformed_rotated) == js_transformed_rotated
            assert path_holonomy(transformed) == js_path_holonomy(js_transformed, modulus)
            assert path_holonomy(transformed) == certificate.holonomy
            transformed_holonomies.append(path_holonomy(transformed))
            assert path_holonomy(transformed_rotated) == record.holonomy
        assert len(set(transformed_holonomies)) == 1

    periodic_cases = [
        (12, 5, 7, 4, 2, 1),
        (12, 5, 12, 4, 2, -1),
        (9, 0, 6, 6, 1, 1),
        (14, 4, 21, 7, 3, -1),
    ]
    for modulus, stride, steps, sectors, turns, orientation in periodic_cases:
        record = finite_periodic_dynamics(modulus, stride, steps)
        js_record = js_finite_periodic_dynamics(modulus, stride, steps)
        assert record.phase == js_record["phase"]
        assert record.winding == js_record["winding"]
        assert record.residue == js_record["residue"]
        assert record.closure_period == js_record["closure_period"]
        assert record.closed == js_record["closed"]
        assert record.phase_sequence == js_record["phase_sequence"]

        defect = finite_defect_winding(sectors, turns, orientation=orientation)
        js_defect = js_finite_defect_winding(sectors, turns, orientation)
        assert defect.phase_path == js_defect["phase_path"]
        assert defect.net_steps == js_defect["net_steps"]
        assert defect.winding == js_defect["winding"]
        assert defect.closed == js_defect["closed"]

    ai_cases = [
        (1, 0, 1, 0),
        (4, 11, 3, 1),
        (5, 22, 5, 2),
        (8, 19, 2, 3),
        (13, 42, 9, 0),
    ]
    for loop_period, sample_index, max_loops, tolerance in ai_cases:
        required = loop_required_steps(loop_period, sample_index)
        certificate = loop_exit_certificate(
            loop_period,
            sample_index,
            max_loops,
            overthink_tolerance=tolerance,
        )
        js_certificate = js_loop_exit_certificate(loop_period, sample_index, max_loops, tolerance)
        assert required == js_loop_required_steps(loop_period, sample_index)
        assert loop_score_trace(required, max_loops, overthink_tolerance=tolerance) == js_loop_score_trace(
            required,
            max_loops,
            tolerance,
        )
        assert loop_exit_step(required, max_loops, overthink_tolerance=tolerance) == js_loop_exit_step(
            required,
            max_loops,
            tolerance,
        )
        for step in range(1, max_loops + 1):
            assert loop_score_active(
                loop_period,
                sample_index,
                step,
                overthink_tolerance=tolerance,
            ) == js_loop_score_active(loop_period, sample_index, step, tolerance)
        assert certificate.required_steps == js_certificate["required_steps"]
        assert certificate.score_trace == js_certificate["score_trace"]
        assert certificate.exit_step == js_certificate["exit_step"]
        assert certificate.first_active_step == js_certificate["first_active_step"]
        assert certificate.first_active_step_matches_exit == js_certificate["first_active_step_matches_exit"]
        assert certificate.exit_available_iff_first_active_within_budget == js_certificate[
            "exit_available_iff_first_active_within_budget"
        ]
        assert certificate.no_exit_iff_no_active_within_budget == js_certificate[
            "no_exit_iff_no_active_within_budget"
        ]
        assert certificate.within_budget == js_certificate["within_budget"]
        assert certificate.within_guardrail == js_certificate["within_guardrail"]
        assert "AIM-T0084" in certificate.theorem_ids
        assert "AIM-T0085" in certificate.theorem_ids
        assert "AIM-T0090" in certificate.theorem_ids
        assert token_recurrence_budget(loop_period, sample_index) == js_token_recurrence_budget(
            loop_period,
            sample_index,
        )
        assert token_recurrence_budget(loop_period, 0) == 1
        assert js_token_recurrence_budget(loop_period, 0) == 1
        assert looped_recurrent_state(
            loop_period,
            token_recurrence_budget(loop_period, sample_index),
        ) == js_looped_recurrent_state(
            loop_period,
            js_token_recurrence_budget(loop_period, sample_index),
        )
        assert looped_recurrent_state(
            loop_period,
            token_recurrence_budget(loop_period, sample_index),
        ) == phase_channel(loop_period, sample_index)
        assert training_free_loop_budget(
            loop_period,
            sample_index,
            max_loops,
        ) == js_training_free_loop_budget(loop_period, sample_index, max_loops)
        if certificate.exit_step is not None:
            assert training_free_loop_budget(
                loop_period,
                sample_index,
                max_loops,
            ) == certificate.exit_step
        if required > max_loops:
            assert training_free_loop_budget(loop_period, sample_index, max_loops) == max_loops
        assert certificate.exit_available == js_loop_exit_available(loop_period, sample_index, max_loops)
        assert certificate.overthinking_boundary == js_loop_overthinking_boundary(
            loop_period,
            sample_index,
            tolerance,
        )
        for passes in (1, 2, 3, 5):
            shifted_sample = sample_index + passes * loop_period
            shifted_certificate = loop_exit_certificate(
                loop_period,
                shifted_sample,
                max_loops,
                overthink_tolerance=tolerance,
            )
            assert loop_required_steps(loop_period, shifted_sample) == required
            assert token_recurrence_budget(loop_period, shifted_sample) == token_recurrence_budget(
                loop_period,
                sample_index,
            )
            assert training_free_loop_budget(
                loop_period,
                shifted_sample,
                max_loops,
            ) == js_training_free_loop_budget(loop_period, sample_index, max_loops)
            assert shifted_certificate.required_steps == certificate.required_steps
            assert shifted_certificate.exit_available == certificate.exit_available
            assert shifted_certificate.overthinking_boundary == certificate.overthinking_boundary

    training_free_cases = [
        (4, 32, 4, 2, 3, 8, 0),
        (5, 25, 5, 3, 4, 9, 1),
        (3, 18, 2, 2, 5, 6, 0),
    ]
    for loop_period, sample_count, max_loops, fixed_budget, wrong_period, over_budget, tolerance in training_free_cases:
        samples = tuple(range(sample_count))
        required_budgets = tuple(js_token_recurrence_budget(loop_period, sample) for sample in samples)
        positive_labels = tuple(1 for _ in samples)
        phase_budgets = js_training_free_loop_budgets(loop_period, samples, max_loops)
        single_pass_budgets = tuple(1 for _ in samples)
        fixed_budgets = tuple(fixed_budget for _ in samples)
        wrong_period_budgets = js_training_free_loop_budgets(wrong_period, samples, max_loops)
        over_budgets = tuple(over_budget for _ in samples)
        control_threshold = (3 * sample_count) // 4
        control_labels = tuple(js_nonperiodic_threshold_label(sample, control_threshold) for sample in samples)
        control_phase_predictions = js_budget_is_full_depth_predictions(phase_budgets, max_loops)
        threshold, polarity = js_fit_threshold_classifier(samples, control_labels)
        threshold_predictions = js_predict_threshold_classifier(samples, threshold, polarity)
        benchmark = run_training_free_loop_wrapper_benchmark(
            loop_period=loop_period,
            sample_count=sample_count,
            max_loops=max_loops,
            fixed_loop_budget=fixed_budget,
            wrong_loop_period=wrong_period,
            over_loop_budget=over_budget,
            overthink_tolerance=tolerance,
        )

        assert training_free_loop_budgets(loop_period, samples, max_loops) == phase_budgets
        assert benchmark.phase_budgets == phase_budgets
        assert benchmark.active_sample_counts == js_active_token_counts_by_budget(phase_budgets, max_loops)
        assert benchmark.budget_histogram == js_budget_histogram(phase_budgets)
        assert benchmark.single_pass_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, single_pass_budgets, tolerance),
            positive_labels,
        )
        assert benchmark.fixed_loop_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, fixed_budgets, tolerance),
            positive_labels,
        )
        assert benchmark.training_free_phase_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, phase_budgets, tolerance),
            positive_labels,
        )
        assert benchmark.wrong_period_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, wrong_period_budgets, tolerance),
            positive_labels,
        )
        assert benchmark.over_loop_no_exit_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, over_budgets, tolerance),
            positive_labels,
        )
        assert benchmark.nonperiodic_phase_budget_accuracy == js_accuracy(
            control_phase_predictions,
            control_labels,
        )
        assert benchmark.nonperiodic_scalar_threshold_accuracy == js_accuracy(
            threshold_predictions,
            control_labels,
        )

    token_recurrence_cases = [
        (4, 32, 4, 4, 8, 1, 0),
        (5, 25, 5, 3, 7, 2, 1),
        (3, 18, 4, 2, 6, 1, 0),
    ]
    for loop_period, token_count, max_budget, fixed_budget, over_budget, wrong_shift, tolerance in token_recurrence_cases:
        tokens = tuple(range(token_count))
        budgets = js_token_recurrence_budgets(loop_period, token_count)
        routed_budgets = tuple(min(budget, max_budget) for budget in budgets)
        fixed_budgets = tuple(fixed_budget for _ in tokens)
        wrong_budgets = js_shifted_budgets(budgets, max_budget, wrong_shift)
        over_budgets = tuple(over_budget for _ in tokens)
        labels = tuple(1 for _ in tokens)
        control_threshold = (3 * token_count) // 4
        control_labels = tuple(js_nonperiodic_threshold_label(token, control_threshold) for token in tokens)
        control_lookup = js_fit_phase_lookup(loop_period, tokens, control_labels)
        control_loop_predictions = js_predict_phase_lookup(loop_period, control_lookup, tokens)
        threshold, polarity = js_fit_threshold_classifier(tokens, control_labels)
        control_threshold_predictions = js_predict_threshold_classifier(tokens, threshold, polarity)
        benchmark = run_token_level_recurrence_benchmark(
            loop_period=loop_period,
            token_count=token_count,
            max_budget=max_budget,
            fixed_global_budget=fixed_budget,
            over_loop_budget=over_budget,
            wrong_budget_shift=wrong_shift,
            overthink_tolerance=tolerance,
        )

        assert token_recurrence_budgets(loop_period, tokens) == budgets
        assert token_recurrence_budget(loop_period, 0) == 1
        assert js_token_recurrence_budget(loop_period, 0) == 1
        assert looped_recurrent_states(loop_period, budgets) == js_looped_recurrent_states(
            loop_period,
            budgets,
        )
        for token in tokens:
            for step in range(1, max_budget + 2):
                assert token_active_at_step(loop_period, token, step) == js_token_active_at_step(
                    loop_period,
                    token,
                    step,
                )
        assert active_token_counts_by_budget(budgets, max_budget) == js_active_token_counts_by_budget(
            budgets,
            max_budget,
        )
        assert recurrence_resolution_levels(max_budget) == js_recurrence_resolution_levels(max_budget)
        assert benchmark.token_budgets == budgets
        assert benchmark.active_token_counts == js_active_token_counts_by_budget(budgets, max_budget)
        assert benchmark.resolution_levels == js_recurrence_resolution_levels(max_budget)
        assert benchmark.token_level_accuracy == js_accuracy(
            js_recurrence_budget_predictions(budgets, routed_budgets, tolerance),
            labels,
        )
        assert benchmark.fixed_global_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(budgets, fixed_budgets, tolerance),
            labels,
        )
        assert benchmark.wrong_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(budgets, wrong_budgets, tolerance),
            labels,
        )
        assert benchmark.over_looped_accuracy == js_accuracy(
            js_recurrence_budget_predictions(budgets, over_budgets, tolerance),
            labels,
        )
        assert benchmark.nonperiodic_token_level_accuracy == js_accuracy(
            control_loop_predictions,
            control_labels,
        )
        assert benchmark.nonperiodic_scalar_threshold_accuracy == js_accuracy(
            control_threshold_predictions,
            control_labels,
        )

    learned_token_cases = [
        (4, 3, 64, 32, 4, 4, 8, 1, 0),
        (5, 4, 50, 25, 5, 3, 9, 2, 1),
        (3, 5, 36, 18, 4, 2, 6, 1, 0),
    ]
    for (
        loop_period,
        wrong_period,
        train_token_count,
        test_token_count,
        max_budget,
        fixed_budget,
        over_budget,
        wrong_shift,
        tolerance,
    ) in learned_token_cases:
        train_tokens = tuple(range(train_token_count))
        train_budgets = js_token_recurrence_budgets(loop_period, train_token_count)
        test_tokens = tuple(range(train_token_count, train_token_count + test_token_count))
        required_budgets = tuple(
            js_token_recurrence_budget(loop_period, token)
            for token in test_tokens
        )
        labels = tuple(1 for _ in test_tokens)
        learned_lookup = js_fit_loop_budget_lookup(loop_period, train_tokens, train_budgets)
        learned_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(loop_period, learned_lookup, test_tokens)
        )
        wrong_lookup = js_fit_loop_budget_lookup(wrong_period, train_tokens, train_budgets)
        wrong_period_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(wrong_period, wrong_lookup, test_tokens)
        )
        fixed_budgets = tuple(fixed_budget for _ in test_tokens)
        wrong_shift_budgets = js_shifted_budgets(required_budgets, max_budget, wrong_shift)
        over_budgets = tuple(over_budget for _ in test_tokens)
        assert token_recurrence_budget(loop_period, 0) == 1
        assert js_token_recurrence_budget(loop_period, 0) == 1
        control_threshold = (3 * train_token_count) // 4
        control_train_labels = tuple(
            js_nonperiodic_threshold_label(token, control_threshold)
            for token in train_tokens
        )
        control_test_labels = tuple(
            js_nonperiodic_threshold_label(token, control_threshold)
            for token in test_tokens
        )
        control_phase_lookup = js_fit_phase_lookup(loop_period, train_tokens, control_train_labels)
        control_phase_predictions = js_predict_phase_lookup(loop_period, control_phase_lookup, test_tokens)
        threshold, polarity = js_fit_threshold_classifier(train_tokens, control_train_labels)
        threshold_predictions = js_predict_threshold_classifier(test_tokens, threshold, polarity)
        benchmark = run_learned_token_level_recurrence_benchmark(
            loop_period=loop_period,
            wrong_period=wrong_period,
            train_token_count=train_token_count,
            test_token_count=test_token_count,
            max_budget=max_budget,
            fixed_global_budget=fixed_budget,
            over_loop_budget=over_budget,
            wrong_budget_shift=wrong_shift,
            overthink_tolerance=tolerance,
        )

        assert fit_loop_budget_lookup(loop_period, train_tokens, train_budgets) == learned_lookup
        assert predict_loop_budget_lookup(loop_period, learned_lookup, test_tokens) == learned_budgets
        assert benchmark.learned_budget_lookup == learned_lookup
        assert benchmark.wrong_period_budget_lookup == wrong_lookup
        assert benchmark.required_budget_sample == required_budgets[: min(12, len(required_budgets))]
        assert benchmark.learned_budget_sample == learned_budgets[: min(12, len(learned_budgets))]
        assert benchmark.wrong_shift_budget_sample == wrong_shift_budgets[: min(12, len(wrong_shift_budgets))]
        assert benchmark.active_token_counts == js_active_token_counts_by_budget(learned_budgets, max_budget)
        assert benchmark.learned_token_router_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, learned_budgets, tolerance),
            labels,
        )
        assert benchmark.fixed_global_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, fixed_budgets, tolerance),
            labels,
        )
        assert benchmark.wrong_period_router_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, wrong_period_budgets, tolerance),
            labels,
        )
        assert benchmark.wrong_shift_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, wrong_shift_budgets, tolerance),
            labels,
        )
        assert benchmark.over_looped_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, over_budgets, tolerance),
            labels,
        )
        assert benchmark.nonperiodic_phase_lookup_accuracy == js_accuracy(
            control_phase_predictions,
            control_test_labels,
        )
        assert benchmark.nonperiodic_scalar_threshold_accuracy == js_accuracy(
            threshold_predictions,
            control_test_labels,
        )

    learned_middle_block_cases = [
        (8, 64, 32, 4, 2, 3, (2, 5), (0, 2), 4, 4, 8, 0),
        (10, 50, 25, 5, 2, 4, (3, 7), (0, 3), 5, 3, 9, 1),
        (12, 48, 24, 3, 5, 4, (4, 8), (1, 4), 4, 2, 6, 0),
    ]
    for (
        block_count,
        train_length,
        test_length,
        loop_period,
        wrong_block_period,
        wrong_budget_period,
        selected_block,
        wrong_block,
        max_budget,
        fixed_budget,
        over_budget,
        tolerance,
    ) in learned_middle_block_cases:
        train_samples = tuple(range(train_length))
        test_samples = tuple(range(train_length, train_length + test_length))
        selected_blocks = js_loop_block_indices(block_count, selected_block)
        wrong_blocks = js_loop_block_indices(block_count, wrong_block)
        full_blocks = tuple(range(block_count))
        block_period = len(selected_blocks)
        common_cycle = block_period * loop_period
        train_required_blocks = js_middle_block_required_blocks(block_count, selected_block, train_samples)
        train_budgets = tuple(js_token_recurrence_budget(loop_period, sample) for sample in train_samples)
        required_blocks = js_middle_block_required_blocks(block_count, selected_block, test_samples)
        required_budgets = tuple(js_token_recurrence_budget(loop_period, sample) for sample in test_samples)
        labels = tuple(1 for _ in test_samples)
        learned_block_lookup = js_fit_loop_block_lookup(block_period, train_samples, train_required_blocks)
        learned_blocks = js_predict_loop_block_lookup(block_period, learned_block_lookup, test_samples)
        learned_budget_lookup = js_fit_loop_budget_lookup(loop_period, train_samples, train_budgets)
        learned_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(loop_period, learned_budget_lookup, test_samples)
        )
        wrong_block_lookup = js_fit_loop_block_lookup(wrong_block_period, train_samples, train_required_blocks)
        wrong_period_blocks = js_predict_loop_block_lookup(wrong_block_period, wrong_block_lookup, test_samples)
        wrong_budget_lookup = js_fit_loop_budget_lookup(wrong_budget_period, train_samples, train_budgets)
        wrong_period_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(wrong_budget_period, wrong_budget_lookup, test_samples)
        )
        fixed_budgets = tuple(fixed_budget for _ in test_samples)
        over_budgets = tuple(over_budget for _ in test_samples)
        benchmark = run_learned_middle_block_recurrence_benchmark(
            block_count=block_count,
            train_length=train_length,
            test_length=test_length,
            loop_period=loop_period,
            wrong_block_period=wrong_block_period,
            wrong_budget_period=wrong_budget_period,
            selected_loop_block=selected_block,
            wrong_loop_block=wrong_block,
            max_budget=max_budget,
            fixed_loop_budget=fixed_budget,
            over_loop_budget=over_budget,
            overthink_tolerance=tolerance,
        )

        assert loop_block_indices(block_count, selected_block) == selected_blocks
        assert loop_block_indices(block_count, wrong_block) == wrong_blocks
        assert middle_block_required_blocks(block_count, selected_block, test_samples) == required_blocks
        assert middle_block_budget_route(selected_blocks[0], block_period, loop_period, 0) == (
            selected_blocks[0],
            1,
        )
        assert tuple(
            middle_block_budget_route(selected_blocks[0], block_period, loop_period, sample)
            for sample in test_samples
        ) == tuple(zip(required_blocks, required_budgets))
        assert all(
            middle_block_budget_route(selected_blocks[0], block_period, loop_period, sample + common_cycle)
            == middle_block_budget_route(selected_blocks[0], block_period, loop_period, sample)
            for sample in test_samples[: min(12, len(test_samples))]
        )
        assert fit_loop_block_lookup(block_period, train_samples, train_required_blocks) == learned_block_lookup
        assert predict_loop_block_lookup(block_period, learned_block_lookup, test_samples) == learned_blocks
        assert fit_loop_budget_lookup(loop_period, train_samples, train_budgets) == learned_budget_lookup
        assert benchmark.block_period == block_period
        assert benchmark.selected_block_indices == selected_blocks
        assert benchmark.learned_block_lookup == learned_block_lookup
        assert benchmark.learned_budget_lookup == learned_budget_lookup
        assert benchmark.wrong_block_period_lookup == wrong_block_lookup
        assert benchmark.wrong_budget_period_lookup == wrong_budget_lookup
        assert benchmark.required_block_sample == required_blocks[: min(12, len(required_blocks))]
        assert benchmark.learned_block_sample == learned_blocks[: min(12, len(learned_blocks))]
        assert benchmark.wrong_block_sample == wrong_period_blocks[: min(12, len(wrong_period_blocks))]
        assert benchmark.required_budget_sample == required_budgets[: min(12, len(required_budgets))]
        assert benchmark.learned_budget_sample == learned_budgets[: min(12, len(learned_budgets))]
        assert benchmark.wrong_budget_sample == wrong_period_budgets[: min(12, len(wrong_period_budgets))]
        assert benchmark.active_sample_counts == js_active_token_counts_by_budget(learned_budgets, max_budget)
        assert benchmark.learned_middle_block_router_accuracy == js_accuracy(
            js_sampled_middle_block_predictions(
                required_blocks,
                required_budgets,
                learned_blocks,
                learned_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.selected_band_phase_budget_accuracy == js_accuracy(
            js_middle_block_predictions(
                required_blocks,
                required_budgets,
                selected_blocks,
                learned_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.full_block_phase_budget_accuracy == js_accuracy(
            js_middle_block_predictions(
                required_blocks,
                required_budgets,
                full_blocks,
                learned_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.fixed_loop_budget_accuracy == js_accuracy(
            js_sampled_middle_block_predictions(
                required_blocks,
                required_budgets,
                learned_blocks,
                fixed_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.wrong_block_period_accuracy == js_accuracy(
            js_sampled_middle_block_predictions(
                required_blocks,
                required_budgets,
                wrong_period_blocks,
                learned_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.wrong_budget_period_accuracy == js_accuracy(
            js_sampled_middle_block_predictions(
                required_blocks,
                required_budgets,
                learned_blocks,
                wrong_period_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.wrong_loop_block_accuracy == js_accuracy(
            js_middle_block_predictions(
                required_blocks,
                required_budgets,
                wrong_blocks,
                learned_budgets,
                tolerance,
            ),
            labels,
        )
        assert benchmark.over_looped_accuracy == js_accuracy(
            js_sampled_middle_block_predictions(
                required_blocks,
                required_budgets,
                learned_blocks,
                over_budgets,
                tolerance,
            ),
            labels,
        )

    learned_multi_resolution_cases = [
        (4, 3, 3, 64, 32, 4, 4, 8, 0),
        (5, 3, 4, 50, 25, 5, 3, 9, 1),
        (3, 4, 5, 36, 18, 4, 2, 6, 0),
    ]
    for (
        loop_period,
        wrong_budget_period,
        wrong_resolution_period,
        train_length,
        test_length,
        max_budget,
        fixed_budget,
        over_budget,
        tolerance,
    ) in learned_multi_resolution_cases:
        train_samples = tuple(range(train_length))
        train_budgets = tuple(js_token_recurrence_budget(loop_period, sample) for sample in train_samples)
        train_resolutions = js_multi_resolution_required_resolutions(max_budget, train_budgets)
        test_samples = tuple(range(train_length, train_length + test_length))
        required_budgets = tuple(js_token_recurrence_budget(loop_period, sample) for sample in test_samples)
        required_resolutions = js_multi_resolution_required_resolutions(max_budget, required_budgets)
        labels = tuple(1 for _ in test_samples)
        learned_budget_lookup = js_fit_loop_budget_lookup(loop_period, train_samples, train_budgets)
        learned_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(loop_period, learned_budget_lookup, test_samples)
        )
        learned_resolution_lookup = js_fit_recurrence_resolution_lookup(
            loop_period,
            train_samples,
            train_resolutions,
        )
        learned_resolutions = js_predict_recurrence_resolution_lookup(
            loop_period,
            learned_resolution_lookup,
            test_samples,
        )
        wrong_budget_lookup = js_fit_loop_budget_lookup(wrong_budget_period, train_samples, train_budgets)
        wrong_budgets = tuple(
            min(budget, max_budget)
            for budget in js_predict_loop_budget_lookup(wrong_budget_period, wrong_budget_lookup, test_samples)
        )
        wrong_resolution_lookup = js_fit_recurrence_resolution_lookup(
            wrong_resolution_period,
            train_samples,
            train_resolutions,
        )
        wrong_resolutions = js_predict_recurrence_resolution_lookup(
            wrong_resolution_period,
            wrong_resolution_lookup,
            test_samples,
        )
        fixed_budgets = tuple(fixed_budget for _ in test_samples)
        over_budgets = tuple(over_budget for _ in test_samples)
        coarse_resolutions = tuple("coarse" for _ in test_samples)
        fine_resolutions = tuple("fine" for _ in test_samples)
        benchmark = run_learned_multi_resolution_recurrence_benchmark(
            loop_period=loop_period,
            wrong_budget_period=wrong_budget_period,
            wrong_resolution_period=wrong_resolution_period,
            train_length=train_length,
            test_length=test_length,
            max_budget=max_budget,
            fixed_loop_budget=fixed_budget,
            over_loop_budget=over_budget,
            overthink_tolerance=tolerance,
        )

        assert multi_resolution_required_resolutions(max_budget, train_budgets) == train_resolutions
        assert fit_recurrence_resolution_lookup(
            loop_period,
            train_samples,
            train_resolutions,
        ) == learned_resolution_lookup
        assert predict_recurrence_resolution_lookup(
            loop_period,
            learned_resolution_lookup,
            test_samples,
        ) == learned_resolutions
        assert benchmark.resolution_levels == js_recurrence_resolution_levels(max_budget)
        assert benchmark.learned_budget_lookup == learned_budget_lookup
        assert benchmark.learned_resolution_lookup == learned_resolution_lookup
        assert benchmark.wrong_budget_period_lookup == wrong_budget_lookup
        assert benchmark.wrong_resolution_period_lookup == wrong_resolution_lookup
        assert benchmark.required_budget_sample == required_budgets[: min(12, len(required_budgets))]
        assert benchmark.learned_budget_sample == learned_budgets[: min(12, len(learned_budgets))]
        assert benchmark.wrong_budget_sample == wrong_budgets[: min(12, len(wrong_budgets))]
        assert benchmark.required_resolution_sample == required_resolutions[: min(12, len(required_resolutions))]
        assert benchmark.learned_resolution_sample == learned_resolutions[: min(12, len(learned_resolutions))]
        assert benchmark.wrong_resolution_sample == wrong_resolutions[: min(12, len(wrong_resolutions))]
        assert benchmark.active_sample_counts == js_active_token_counts_by_budget(learned_budgets, max_budget)
        assert benchmark.learned_multi_resolution_router_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                learned_budgets,
                learned_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.single_resolution_coarse_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                learned_budgets,
                coarse_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.single_resolution_fine_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                learned_budgets,
                fine_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.fixed_budget_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                fixed_budgets,
                learned_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.wrong_budget_period_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                wrong_budgets,
                learned_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.wrong_resolution_period_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                learned_budgets,
                wrong_resolutions,
                tolerance,
            ),
            labels,
        )
        assert benchmark.over_looped_accuracy == js_accuracy(
            js_multi_resolution_predictions(
                required_budgets,
                required_resolutions,
                over_budgets,
                learned_resolutions,
                tolerance,
            ),
            labels,
        )

    learned_schedule_cases = [
        (4, 3, 64, 32, 4, 8, 0),
        (5, 4, 50, 25, 3, 9, 1),
        (3, 5, 36, 18, 2, 6, 0),
    ]
    for (
        loop_period,
        wrong_period,
        train_length,
        test_length,
        fixed_budget,
        over_budget,
        tolerance,
    ) in learned_schedule_cases:
        train_positions = tuple(range(train_length))
        train_budgets = tuple(js_token_recurrence_budget(loop_period, position) for position in train_positions)
        test_positions = tuple(range(train_length, train_length + test_length))
        required_budgets = tuple(js_token_recurrence_budget(loop_period, position) for position in test_positions)
        labels = tuple(1 for _ in test_positions)
        learned_lookup = js_fit_loop_budget_lookup(loop_period, train_positions, train_budgets)
        learned_budgets = js_predict_loop_budget_lookup(loop_period, learned_lookup, test_positions)
        wrong_lookup = js_fit_loop_budget_lookup(wrong_period, train_positions, train_budgets)
        wrong_budgets = js_predict_loop_budget_lookup(wrong_period, wrong_lookup, test_positions)
        fixed_budgets = tuple(fixed_budget for _ in test_positions)
        over_budgets = tuple(over_budget for _ in test_positions)
        benchmark = run_learned_recurrence_schedule_benchmark(
            loop_period=loop_period,
            wrong_period=wrong_period,
            train_length=train_length,
            test_length=test_length,
            fixed_loop_budget=fixed_budget,
            over_loop_budget=over_budget,
            overthink_tolerance=tolerance,
        )

        assert fit_loop_budget_lookup(loop_period, train_positions, train_budgets) == learned_lookup
        assert predict_loop_budget_lookup(loop_period, learned_lookup, test_positions) == learned_budgets
        assert benchmark.learned_budget_lookup == learned_lookup
        assert benchmark.wrong_period_budget_lookup == wrong_lookup
        assert benchmark.required_budget_sample == required_budgets[: min(12, len(required_budgets))]
        assert benchmark.learned_budget_sample == learned_budgets[: min(12, len(learned_budgets))]
        assert benchmark.learned_phase_router_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, learned_budgets, tolerance),
            labels,
        )
        assert benchmark.fixed_loop_budget_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, fixed_budgets, tolerance),
            labels,
        )
        assert benchmark.wrong_period_router_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, wrong_budgets, tolerance),
            labels,
        )
        assert benchmark.over_looped_accuracy == js_accuracy(
            js_recurrence_budget_predictions(required_budgets, over_budgets, tolerance),
            labels,
        )

    tiny_looped_cases = [
        (4, 3, 64, 32),
        (5, 4, 50, 25),
        (6, 5, 60, 30),
    ]
    for period, wrong_period, train_length, test_length in tiny_looped_cases:
        train_positions = tuple(range(train_length))
        train_labels = tuple(js_periodic_phase_label(period, position, js_default_positive_phases(period)) for position in train_positions)
        test_positions = tuple(range(train_length, train_length + test_length))
        test_labels = tuple(js_periodic_phase_label(period, position, js_default_positive_phases(period)) for position in test_positions)
        train_budgets = tuple(js_token_recurrence_budget(period, position) for position in train_positions)
        train_states = js_looped_recurrent_states(period, train_budgets)
        state_lookup = js_fit_phase_lookup(period, train_states, train_labels)
        test_budgets = tuple(js_token_recurrence_budget(period, position) for position in test_positions)
        required_states = js_looped_recurrent_states(period, test_budgets)
        looped_predictions = js_predict_phase_lookup(period, state_lookup, required_states)
        one_step_states = tuple(js_looped_recurrent_state(period, 1) for _ in test_positions)
        one_step_predictions = js_predict_phase_lookup(period, state_lookup, one_step_states)
        phase_lookup = js_fit_phase_lookup(period, train_positions, train_labels)
        phase_predictions = js_predict_phase_lookup(period, phase_lookup, test_positions)
        threshold, polarity = js_fit_threshold_classifier(train_positions, train_labels)
        scalar_predictions = js_predict_threshold_classifier(test_positions, threshold, polarity)
        wrong_train_budgets = tuple(js_token_recurrence_budget(wrong_period, position) for position in train_positions)
        wrong_train_states = js_looped_recurrent_states(wrong_period, wrong_train_budgets)
        wrong_lookup = js_fit_phase_lookup(wrong_period, wrong_train_states, train_labels)
        wrong_test_budgets = tuple(js_token_recurrence_budget(wrong_period, position) for position in test_positions)
        wrong_test_states = js_looped_recurrent_states(wrong_period, wrong_test_budgets)
        wrong_predictions = js_predict_phase_lookup(wrong_period, wrong_lookup, wrong_test_states)
        control_threshold = (3 * train_length) // 4
        control_train_labels = tuple(js_nonperiodic_threshold_label(position, control_threshold) for position in train_positions)
        control_test_labels = tuple(js_nonperiodic_threshold_label(position, control_threshold) for position in test_positions)
        control_state_lookup = js_fit_phase_lookup(period, train_states, control_train_labels)
        control_looped_predictions = js_predict_phase_lookup(period, control_state_lookup, required_states)
        control_threshold_fit, control_polarity = js_fit_threshold_classifier(train_positions, control_train_labels)
        control_threshold_predictions = js_predict_threshold_classifier(test_positions, control_threshold_fit, control_polarity)
        prototype = run_tiny_looped_recurrent_prototype(
            period=period,
            wrong_period=wrong_period,
            train_length=train_length,
            test_length=test_length,
        )

        assert looped_recurrent_states(period, train_budgets) == train_states
        assert prototype.learned_state_lookup == state_lookup
        assert prototype.wrong_period_state_lookup == wrong_lookup
        assert prototype.required_state_sample == required_states[: min(12, len(required_states))]
        assert prototype.learned_state_sample == required_states[: min(12, len(required_states))]
        assert prototype.one_step_state_sample == one_step_states[: min(12, len(one_step_states))]
        assert prototype.looped_recurrent_accuracy == js_accuracy(looped_predictions, test_labels)
        assert prototype.one_step_accuracy == js_accuracy(one_step_predictions, test_labels)
        assert prototype.phase_lookup_accuracy == js_accuracy(phase_predictions, test_labels)
        assert prototype.scalar_threshold_accuracy == js_accuracy(scalar_predictions, test_labels)
        assert prototype.wrong_period_state_accuracy == js_accuracy(wrong_predictions, test_labels)
        assert prototype.nonperiodic_looped_recurrent_accuracy == js_accuracy(
            control_looped_predictions,
            control_test_labels,
        )
        assert prototype.nonperiodic_scalar_threshold_accuracy == js_accuracy(
            control_threshold_predictions,
            control_test_labels,
        )
        assert prototype.average_unroll_steps == sum(test_budgets) / len(test_budgets)

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

    kv_cache_cases = [
        (16, 31, 20, (20, 24, 29, 31)),
        (16, 40, 20, (25, 31, 39, 40)),
        (8, 12, 12, (5, 7, 10, 12)),
    ]
    for cache_size, current, token, batch_tokens in kv_cache_cases:
        window = certify_kv_cache_window(cache_size=cache_size, current=current, token=token)
        batch = certify_kv_cache_batch(cache_size=cache_size, current=current, tokens=batch_tokens)
        adapter_request = certify_kv_cache_adapter_request_trace(
            cache_size=cache_size,
            current=current,
            requested_tokens=batch_tokens,
        )
        slot = js_kv_cache_slot(cache_size, token)
        current_slot = js_kv_cache_slot(cache_size, current)
        retained = js_kv_cache_window_contains(cache_size, current, token)
        next_overwrite = js_kv_cache_next_overwrite_token(cache_size, token)
        no_same_slot_overwrite = js_kv_cache_no_same_slot_overwrite_before_current(
            cache_size,
            current,
            token,
        )
        stale_witness = js_kv_cache_same_slot_overwrite_witness_when_stale(
            cache_size,
            current,
            token,
        )
        trace_iff = js_kv_cache_retained_iff_no_same_slot_overwrite_trace(
            cache_size,
            current,
            token,
        )
        boundary_iff = js_kv_cache_trace_fresh_iff_next_overwrite_boundary(
            cache_size,
            current,
            token,
        )

        assert kv_cache_slot(cache_size, token) == slot
        assert kv_cache_window_contains(cache_size, current, token) == retained
        assert kv_cache_next_overwrite_token(cache_size, token) == next_overwrite
        assert kv_cache_no_same_slot_overwrite_before_current(cache_size, current, token) == no_same_slot_overwrite
        assert kv_cache_same_slot_overwrite_witness_when_stale(cache_size, current, token) == stale_witness
        assert kv_cache_retained_iff_no_same_slot_overwrite_trace(cache_size, current, token) == trace_iff
        assert kv_cache_next_overwrite_after_current(cache_size, current, token) == (
            current < next_overwrite
        )
        assert kv_cache_trace_fresh_iff_next_overwrite_boundary(cache_size, current, token) == boundary_iff
        assert window.slot == slot
        assert window.current_slot == current_slot
        assert window.lag == current - token
        assert window.retained == retained
        assert window.next_overwrite_token == next_overwrite
        assert window.next_overwrite_after_current == (current < next_overwrite)
        assert window.no_same_slot_overwrite_before_current == no_same_slot_overwrite
        assert window.same_slot_overwrite_witness_when_stale == stale_witness
        assert window.retained_iff_no_same_slot_overwrite_trace == trace_iff
        assert window.trace_fresh_iff_next_overwrite_boundary == boundary_iff
        assert batch.slots == tuple(js_kv_cache_slot(cache_size, token) for token in batch_tokens)
        assert batch.all_retained == all(
            js_kv_cache_window_contains(cache_size, current, token)
            for token in batch_tokens
        )
        assert batch.tokens_distinct == (len(set(batch_tokens)) == len(batch_tokens))
        assert batch.slots_distinct == js_kv_cache_retained_batch_slots_distinct(
            cache_size,
            current,
            batch_tokens,
        )
        assert batch.retained_iff_no_same_slot_overwrite_trace == (
            js_kv_cache_batch_retained_iff_no_same_slot_overwrite_trace(
                cache_size,
                current,
                batch_tokens,
            )
        )
        assert batch.next_overwrites_after_current == all(
            js_kv_cache_next_overwrite_after_current(cache_size, current, token)
            for token in batch_tokens
        )
        assert batch.trace_fresh_iff_next_overwrite_boundary == (
            js_kv_cache_batch_trace_fresh_iff_next_overwrite_boundary(
                cache_size,
                current,
                batch_tokens,
            )
        )
        assert batch.trace_fresh_slots_distinct == (
            js_kv_cache_trace_fresh_batch_slots_distinct(cache_size, current, batch_tokens)
        )
        assert kv_cache_retained_batch_slots_distinct(cache_size, current, batch_tokens) == batch.slots_distinct
        assert kv_cache_batch_retained_iff_no_same_slot_overwrite_trace(
            cache_size,
            current,
            batch_tokens,
        ) == batch.retained_iff_no_same_slot_overwrite_trace
        assert kv_cache_batch_trace_fresh_iff_next_overwrite_boundary(
            cache_size,
            current,
            batch_tokens,
        ) == batch.trace_fresh_iff_next_overwrite_boundary
        assert kv_cache_trace_fresh_batch_slots_distinct(
            cache_size,
            current,
            batch_tokens,
        ) == batch.trace_fresh_slots_distinct
        assert adapter_request.requested_slots == batch.slots
        assert adapter_request.all_non_future == all(token <= current for token in batch_tokens)
        assert adapter_request.all_retained == batch.all_retained
        assert adapter_request.tokens_distinct == batch.tokens_distinct
        assert adapter_request.slots_distinct == batch.slots_distinct
        assert adapter_request.next_overwrites_after_current == batch.next_overwrites_after_current
        assert adapter_request.trace_fresh_iff_next_overwrite_boundary == (
            batch.trace_fresh_iff_next_overwrite_boundary
        )
        assert adapter_request.trace_fresh_slots_distinct == batch.trace_fresh_slots_distinct
        assert adapter_request.pass_certificate == (
            adapter_request.all_non_future
            and batch.all_retained
            and batch.tokens_distinct
            and batch.slots_distinct
            and batch.retained_iff_no_same_slot_overwrite_trace
            and batch.trace_fresh_slots_distinct
        )
        assert adapter_request.pass_certificate == kv_cache_adapter_request_trace_pass_compact(
            cache_size,
            current,
            batch_tokens,
        )
        assert adapter_request.pass_iff_next_overwrite_boundary == (
            adapter_request.pass_certificate
            == (
                adapter_request.all_non_future
                and batch.tokens_distinct
                and batch.next_overwrites_after_current
            )
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

    stride_family_cases = [
        (120, 120, (7, 13), (5, 9), 3, 4),
        (96, 96, (11, 17), (8, 15), 4, 5),
    ]
    for sequence_length, query_count, strides, wrong_strides, path_length, local_window in stride_family_cases:
        query_indices = tuple(range(query_count))
        target_lags = structured_stride_family_target_lags(
            query_indices,
            strides=strides,
            path_length=path_length,
            local_window=local_window,
        )
        control_lags = nonstructured_stride_family_control_lags(
            query_indices,
            sequence_length=sequence_length,
        )
        js_target_lags = js_structured_stride_family_target_lags(
            query_indices,
            strides,
            path_length,
            local_window,
        )
        js_control_lags = js_nonstructured_stride_family_control_lags(query_indices, sequence_length)
        assert target_lags == js_target_lags
        assert control_lags == js_control_lags

        family_sets = tuple(
            stride_family_attention_candidates(sequence_length, query, strides, path_length, local_window)
            for query in query_indices
        )
        single_sets = tuple(
            stride_family_attention_candidates(sequence_length, query, (strides[0],), path_length, local_window)
            for query in query_indices
        )
        local_sets = tuple(
            js_local_window_indices(sequence_length, query, local_window)
            for query in query_indices
        )
        wrong_family_sets = tuple(
            stride_family_attention_candidates(sequence_length, query, wrong_strides, path_length, local_window)
            for query in query_indices
        )
        full_sets = tuple(tuple(range(sequence_length)) for _ in query_indices)
        js_family_sets = tuple(
            js_stride_family_attention_candidates(sequence_length, query, strides, path_length, local_window)
            for query in query_indices
        )
        js_single_sets = tuple(
            js_stride_family_attention_candidates(sequence_length, query, (strides[0],), path_length, local_window)
            for query in query_indices
        )
        js_wrong_family_sets = tuple(
            js_stride_family_attention_candidates(sequence_length, query, wrong_strides, path_length, local_window)
            for query in query_indices
        )
        covered_lags = stride_family_covered_lags(sequence_length, strides, path_length, local_window)
        js_covered_lags = js_stride_family_covered_lags(sequence_length, strides, path_length, local_window)
        assert covered_lags == js_covered_lags
        lag_candidates = stride_family_lag_candidate_list(
            sequence_length,
            strides,
            path_length,
            local_window,
        )
        js_lag_candidates = js_stride_family_lag_candidate_list(
            sequence_length,
            strides,
            path_length,
            local_window,
        )
        assert lag_candidates == js_lag_candidates
        coil_residues = stride_family_coil_residue_list(sequence_length, strides, path_length)
        js_coil_residues = js_stride_family_coil_residue_list(sequence_length, strides, path_length)
        assert coil_residues == js_coil_residues
        query_candidates = stride_family_query_candidate_list(
            sequence_length,
            0,
            strides,
            path_length,
            local_window,
        )
        js_query_candidates = js_stride_family_query_candidate_list(
            sequence_length,
            0,
            strides,
            path_length,
            local_window,
        )
        assert query_candidates == js_query_candidates
        coverage_certificate = certify_stride_family_coverage(sequence_length, strides, path_length, local_window)
        assert coverage_certificate.covered_lags == js_covered_lags
        assert coverage_certificate.theorem_side_lag_candidates == js_lag_candidates
        assert coverage_certificate.theorem_side_unique_lag_candidate_count == len(set(js_lag_candidates))
        assert coverage_certificate.theorem_side_coil_residues_no_collision == (
            len(set(js_coil_residues)) == len(js_coil_residues)
        )
        assert coverage_certificate.theorem_side_coil_residues_no_collision == (
            stride_family_coil_residues_no_collision(sequence_length, strides, path_length)
        )
        assert coverage_certificate.theorem_side_local_coil_disjoint == (
            set(range(1, local_window + 1)).isdisjoint(set(js_coil_residues))
        )
        assert coverage_certificate.theorem_side_local_coil_disjoint == (
            stride_family_local_coil_candidates_disjoint(
                sequence_length,
                strides,
                path_length,
                local_window,
            )
        )
        assert coverage_certificate.theorem_side_lag_candidates_no_collision == (
            len(set(js_lag_candidates)) == len(js_lag_candidates)
        )
        assert coverage_certificate.theorem_side_unique_lag_candidate_count <= (
            local_window + path_length * len(strides)
        )
        assert coverage_certificate.theorem_side_query_candidates == js_query_candidates
        assert coverage_certificate.theorem_side_unique_query_candidate_count == len(set(js_query_candidates))
        assert coverage_certificate.theorem_side_predecessor_injective_on_lag_candidates == (
            js_predecessor_injective_on_lag_candidates(sequence_length, 0, js_lag_candidates)
        )
        assert coverage_certificate.theorem_side_predecessor_injective_on_lag_candidates == (
            stride_family_predecessor_injective_on_lag_candidates(
                sequence_length,
                0,
                strides,
                path_length,
                local_window,
            )
        )
        assert coverage_certificate.theorem_side_predecessor_injective_window_context_condition == (
            local_window < sequence_length
        )
        assert coverage_certificate.theorem_side_predecessor_injective_window_context_condition == (
            stride_family_predecessor_injective_window_context_sufficient_condition(
                sequence_length,
                local_window,
            )
        )
        assert coverage_certificate.theorem_side_query_candidates_no_collision == (
            len(set(js_query_candidates)) == len(js_query_candidates)
        )
        assert coverage_certificate.theorem_side_unique_query_candidate_count <= (
            local_window + path_length * len(strides)
        )
        assert coverage_certificate.theorem_side_query_count_le_unique_lag_count
        assert coverage_certificate.theorem_side_unique_query_candidate_count <= (
            coverage_certificate.theorem_side_unique_lag_candidate_count
        )
        assert coverage_certificate.theorem_side_query_count_matches_unique_lag_count == (
            coverage_certificate.theorem_side_unique_query_candidate_count
            == coverage_certificate.theorem_side_unique_lag_candidate_count
        )
        assert coverage_certificate.uncovered_lags == tuple(
            lag for lag in range(1, sequence_length) if lag not in set(js_covered_lags)
        )
        assert coverage_certificate.uncovered_lag_intervals == consecutive_integer_intervals(
            coverage_certificate.uncovered_lags,
        )
        assert coverage_certificate.uncovered_lag_interval_count == len(
            coverage_certificate.uncovered_lag_intervals,
        )
        assert coverage_certificate.covered_lag_count == len(js_covered_lags)
        assert coverage_certificate.uncovered_lag_count == sequence_length - 1 - len(js_covered_lags)
        assert coverage_certificate.candidate_budget_per_query == len(js_family_sets[0])
        assert coverage_certificate.raw_candidate_budget_upper_bound == (
            local_window + path_length * len(strides)
        )
        assert coverage_certificate.raw_budget_shortfall_certifies_incomplete == (
            not (
                coverage_certificate.raw_candidate_budget_upper_bound
                < coverage_certificate.positive_lag_count
                and coverage_certificate.coverage_complete
            )
        )
        assert coverage_certificate.unique_lag_count_shortfall_certifies_incomplete == (
            not (
                coverage_certificate.theorem_side_unique_lag_candidate_count
                < coverage_certificate.positive_lag_count
                and coverage_certificate.coverage_complete
            )
        )
        assert coverage_certificate.theorem_side_lag_candidates_positive_in_context == all(
            1 <= lag < sequence_length
            for lag in coverage_certificate.theorem_side_lag_candidates
        )
        assert coverage_certificate.unique_lag_count_matches_complete_under_candidate_range == (
            not coverage_certificate.theorem_side_lag_candidates_positive_in_context
            or (
                coverage_certificate.coverage_complete
                == (
                    coverage_certificate.theorem_side_unique_lag_candidate_count
                    == coverage_certificate.positive_lag_count
                )
            )
        )
        assert coverage_certificate.covered_count_matches_unique_lag_count_under_candidate_range == (
            not coverage_certificate.theorem_side_lag_candidates_positive_in_context
            or (
                coverage_certificate.covered_lag_count
                == coverage_certificate.theorem_side_unique_lag_candidate_count
            )
        )
        assert (
            coverage_certificate.uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range
            == (
                not coverage_certificate.theorem_side_lag_candidates_positive_in_context
                or (
                    coverage_certificate.uncovered_lag_count
                    == max(
                        0,
                        coverage_certificate.positive_lag_count
                        - coverage_certificate.theorem_side_unique_lag_candidate_count,
                    )
                )
            )
        )
        assert coverage_certificate.deduplicated_candidate_budget_upper_bound == min(
            sequence_length,
            local_window + path_length * len(strides),
        )
        assert (
            coverage_certificate.candidate_budget_per_query
            <= coverage_certificate.deduplicated_candidate_budget_upper_bound
        )
        assert (
            coverage_certificate.deduplicated_candidate_budget_upper_bound
            <= coverage_certificate.raw_candidate_budget_upper_bound
        )
        assert coverage_certificate.deduplicated_candidate_budget_upper_bound <= sequence_length
        assert coverage_certificate.full_attention_budget == sequence_length
        assert family_sets == js_family_sets
        assert single_sets == js_single_sets
        assert wrong_family_sets == js_wrong_family_sets

        benchmark = run_stride_family_sparse_attention_benchmark(
            sequence_length=sequence_length,
            query_count=query_count,
            strides=strides,
            wrong_strides=wrong_strides,
            path_length=path_length,
            local_window=local_window,
        )
        assert benchmark.family_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_family_sets,
        )
        assert benchmark.single_stride_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_single_sets,
        )
        assert benchmark.local_window_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            local_sets,
        )
        assert benchmark.wrong_family_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            js_wrong_family_sets,
        )
        assert benchmark.full_attention_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_target_lags,
            full_sets,
        )
        assert benchmark.nonstructured_family_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_control_lags,
            js_family_sets,
        )
        assert benchmark.nonstructured_full_attention_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            query_indices,
            js_control_lags,
            full_sets,
        )
        assert benchmark.average_family_candidate_count == js_average_candidate_count(js_family_sets)
        assert benchmark.average_single_stride_candidate_count == js_average_candidate_count(js_single_sets)
        assert benchmark.average_local_candidate_count == js_average_candidate_count(local_sets)
        assert benchmark.average_full_candidate_count == js_average_candidate_count(full_sets)
        assert benchmark.coverage_certificate == coverage_certificate

    learned_content_cases = [
        (64, 64, 32, 2, 3, 21, 3, 7, 3, 8),
        (48, 48, 24, 2, 5, 13, 2, 5, 4, 6),
    ]
    for (
        sequence_length,
        train_length,
        test_length,
        route_period,
        wrong_route_period,
        long_lag,
        near_lag,
        stride,
        path_length,
        local_window,
    ) in learned_content_cases:
        train_queries = tuple(range(train_length))
        train_routes = tuple(content_route_label(query) for query in train_queries)
        test_queries = tuple(range(train_length, train_length + test_length))
        required_routes = tuple(content_route_label(query) for query in test_queries)
        js_train_routes = tuple(js_content_route_label(query) for query in train_queries)
        js_required_routes = tuple(js_content_route_label(query) for query in test_queries)
        assert train_routes == js_train_routes
        assert required_routes == js_required_routes
        learned_lookup = fit_content_route_lookup(route_period, train_queries, train_routes)
        wrong_lookup = fit_content_route_lookup(wrong_route_period, train_queries, train_routes)
        js_learned_lookup = js_fit_content_route_lookup(route_period, train_queries, js_train_routes)
        js_wrong_lookup = js_fit_content_route_lookup(wrong_route_period, train_queries, js_train_routes)
        assert learned_lookup == js_learned_lookup
        assert wrong_lookup == js_wrong_lookup
        learned_routes = predict_content_route_lookup(route_period, learned_lookup, test_queries)
        wrong_routes = predict_content_route_lookup(wrong_route_period, wrong_lookup, test_queries)
        js_learned_routes = js_predict_content_route_lookup(route_period, js_learned_lookup, test_queries)
        js_wrong_routes = js_predict_content_route_lookup(wrong_route_period, js_wrong_lookup, test_queries)
        assert learned_routes == js_learned_routes
        assert wrong_routes == js_wrong_routes

        target_lags = mixed_retrieval_target_lags(
            test_queries,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
        )
        js_target_lags = js_mixed_retrieval_target_lags(
            test_queries,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
        )
        assert target_lags == js_target_lags
        coil_candidates = tuple(
            coil_attention_path(sequence_length, query, stride, path_length)
            for query in test_queries
        )
        local_candidates = tuple(
            local_window_indices(sequence_length, query, local_window)
            for query in test_queries
        )
        js_coil_candidates = tuple(
            js_coil_attention_path(sequence_length, query, stride, path_length)
            for query in test_queries
        )
        js_local_candidates = tuple(
            js_local_window_indices(sequence_length, query, local_window)
            for query in test_queries
        )
        learned_candidates = js_candidate_sets_for_routes(js_learned_routes, js_coil_candidates, js_local_candidates)
        wrong_candidates = js_candidate_sets_for_routes(js_wrong_routes, js_coil_candidates, js_local_candidates)
        flipped_routes = tuple(1 - route for route in js_required_routes)
        flipped_candidates = js_candidate_sets_for_routes(flipped_routes, js_coil_candidates, js_local_candidates)
        union_candidates = tuple(
            tuple(sorted(set(coil) | set(local)))
            for coil, local in zip(js_coil_candidates, js_local_candidates)
        )
        full_candidates = tuple(tuple(range(sequence_length)) for _ in test_queries)

        benchmark = run_learned_content_gate_retrieval_benchmark(
            sequence_length=sequence_length,
            train_length=train_length,
            test_length=test_length,
            route_period=route_period,
            wrong_route_period=wrong_route_period,
            long_target_lag=long_lag,
            near_target_lag=near_lag,
            stride=stride,
            path_length=path_length,
            local_window=local_window,
        )
        assert benchmark.learned_route_lookup == js_learned_lookup
        assert benchmark.wrong_period_route_lookup == js_wrong_lookup
        assert benchmark.learned_route_sample == js_learned_routes[:12]
        assert benchmark.required_route_sample == js_required_routes[:12]
        assert benchmark.learned_route_accuracy == js_accuracy(js_learned_routes, js_required_routes)
        assert benchmark.wrong_period_route_accuracy == js_accuracy(js_wrong_routes, js_required_routes)
        assert benchmark.learned_gate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            learned_candidates,
        )
        assert benchmark.static_coil_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            js_coil_candidates,
        )
        assert benchmark.static_local_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            js_local_candidates,
        )
        assert benchmark.wrong_period_gate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            wrong_candidates,
        )
        assert benchmark.flipped_gate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            flipped_candidates,
        )
        assert benchmark.union_candidate_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            union_candidates,
        )
        assert benchmark.full_attention_accuracy == js_retrieval_hit_rate_by_lag(
            sequence_length,
            test_queries,
            js_target_lags,
            full_candidates,
        )
        assert benchmark.average_learned_candidate_count == js_average_candidate_count(learned_candidates)
        assert benchmark.average_union_candidate_count == js_average_candidate_count(union_candidates)
        assert benchmark.average_full_candidate_count == js_average_candidate_count(full_candidates)

    multicoil_cases = [
        ((5, 7), 42),
        ((4, 6, 9), 35),
        ((8, 11), 140),
    ]
    for periods, position in multicoil_cases:
        cycle = multicoil_cycle_length(periods)
        assert multicoil_phase(periods, position) == js_multicoil_phase(periods, position)
        assert cycle == js_multicoil_cycle_length(periods)
        assert multicoil_phase(periods, position + cycle) == multicoil_phase(periods, position)
        assert multicoil_phase_label(periods, position) == js_multicoil_phase_label(periods, position)
        assert multicoil_phase_label(periods, position + cycle) == multicoil_phase_label(periods, position)

    multicoil_closure_cases = [
        (5, 7, 42, 5),
        (4, 6, 35, 4),
        (8, 11, 140, 8),
    ]
    for period_a, period_b, position, wrong_shift in multicoil_closure_cases:
        product_cycle = js_multicoil_product_cycle(period_a, period_b)
        lcm_cycle = js_multicoil_cycle_length((period_a, period_b))
        phase = js_multicoil_phase2(period_a, period_b, position)
        assert multicoil_phase2(period_a, period_b, position) == phase
        assert multicoil_product_cycle(period_a, period_b) == product_cycle
        assert multicoil_phase2(period_a, period_b, position + product_cycle) == phase
        assert multicoil_phase2(period_a, period_b, position + 3 * product_cycle) == phase
        benchmark = run_multicoil_closure_benchmark(
            period_a=period_a,
            period_b=period_b,
            position=position,
            wrong_shift=wrong_shift,
        )
        assert benchmark.product_cycle == product_cycle
        assert benchmark.lcm_cycle == lcm_cycle
        assert benchmark.phase == phase
        assert benchmark.product_shifted_phase == phase
        assert benchmark.lcm_shifted_phase == js_multicoil_phase2(period_a, period_b, position + lcm_cycle)
        assert benchmark.product_closes
        assert benchmark.lcm_closes
        assert benchmark.wrong_shifted_phase == js_multicoil_phase2(period_a, period_b, position + wrong_shift)
        assert benchmark.wrong_shift_mismatch == (phase != benchmark.wrong_shifted_phase)

    rope_cases = [
        (8, 19, 11, 7),
        (11, 42, -5, 9),
        (13, 140, 39, 12),
    ]
    for period, query_position, key_position, wrong_period in rope_cases:
        assert rope_relative_feature(period, query_position, key_position) == js_rope_relative_feature(
            period,
            query_position,
            key_position,
        )
        assert rope_relative_feature(period, query_position + period, key_position) == rope_relative_feature(
            period,
            query_position,
            key_position,
        )
        assert rope_relative_feature(period, query_position, key_position + period) == rope_relative_feature(
            period,
            query_position,
            key_position,
        )
        assert rope_relative_feature(wrong_period, query_position, key_position) == js_rope_relative_feature(
            wrong_period,
            query_position,
            key_position,
        )

    rope_certifier_cases = [
        RoPEConfig(head_dim=2, base=10000.0, context_length=20, tolerance=1e-6),
        RoPEConfig(head_dim=4, base=10000.0, context_length=8, tolerance=1e-6),
        RoPEConfig(head_dim=8, base=500000.0, context_length=64, tolerance=1e-6),
    ]
    for config in rope_certifier_cases:
        periods = rope_period_estimates(config.head_dim, config.base)
        js_periods = js_rope_period_estimates(config.head_dim, config.base)
        assert tuple(round(value, 12) for value in periods) == tuple(round(value, 12) for value in js_periods)
        discrete = discretize_rope_periods(periods, config.discretization)
        js_discrete = js_discretize_rope_periods(js_periods, config.discretization)
        assert discrete == js_discrete
        assert capped_lcm(discrete, config.context_length) == js_capped_lcm(js_discrete, config.context_length)
        certificate = certify_rope_positions(config)
        lcm_value, lcm_reaches = capped_lcm(discrete, config.context_length)
        assert certificate.exact_discrete.common_collision_gap_reaches_context == lcm_reaches
        assert certificate.exact_discrete.common_collision_gap == (None if lcm_reaches else lcm_value)
        js_pair_count = 0 if lcm_reaches else max(0, config.context_length - lcm_value)
        assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == js_pair_count
        assert collision_pair_count_at_gap(config.context_length, lcm_value) == js_pair_count
        js_multiple_count = 0 if lcm_reaches else js_collision_pair_count_at_gap_multiples(
            config.context_length,
            lcm_value,
        )
        assert (
            certificate.exact_discrete.guaranteed_common_gap_multiple_pair_count
            == js_multiple_count
        )
        js_fitting_count = 0 if lcm_reaches else js_collision_pair_count_fitting_multiple_count(
            config.context_length,
            lcm_value,
        )
        assert certificate.exact_discrete.common_gap_fitting_multiple_count == js_fitting_count
        assert collision_pair_count_fitting_multiple_count(config.context_length, lcm_value) == js_fitting_count
        js_closed_form_numerator = 0 if lcm_reaches else js_collision_pair_count_closed_form_numerator(
            config.context_length,
            lcm_value,
        )
        assert (
            certificate.exact_discrete.common_gap_collision_pair_count_closed_form_numerator
            == js_closed_form_numerator
        )
        assert (
            collision_pair_count_at_gap_multiples_closed_form_numerator(
                config.context_length,
                lcm_value,
            )
            == js_closed_form_numerator
        )
        assert 2 * js_multiple_count == js_closed_form_numerator
        assert collision_pair_count_at_gap_multiples(config.context_length, lcm_value) == js_multiple_count
        assert (
            collision_pair_count_at_gap_multiples_fitting_range(config.context_length, lcm_value)
            == js_multiple_count
        )
        python_prefix_reports = phase_bank_prefix_collision_reports(config.context_length, discrete)
        js_prefix_reports = js_phase_bank_prefix_collision_reports(config.context_length, js_discrete)
        assert tuple(
            (
                report.prefix_length,
                report.lcm_collision_gap,
                report.lcm_reaches_context,
                report.fitting_collision_multiple_count,
                report.collision_pair_count_closed_form_numerator,
                report.total_bank_collision_pair_count,
            )
            for report in python_prefix_reports
        ) == js_prefix_reports
        first_prefix = next(
            (report.prefix_length for report in python_prefix_reports if report.lcm_reaches_context),
            None,
        )
        assert certificate.exact_discrete.first_exact_pass_prefix_length == first_prefix

    winding_cases = [
        (8, 4, 37, 7),
        (9, 5, 81, 8),
        (13, 3, 140, 11),
    ]
    for period, winding_period, position, wrong_period in winding_cases:
        js_position = js_winding_position(period, position)
        assert position_winding(period, position) == js_position[0]
        assert position_residue(period, position) == js_position[1]
        assert winding_position(period, position) == js_position
        assert js_position[0] * period + js_position[1] == position
        assert winding_position_feature(period, winding_period, position) == js_winding_position_feature(
            period,
            winding_period,
            position,
        )
        assert winding_position_label(period, winding_period, position) == js_winding_position_label(
            period,
            winding_period,
            position,
        )
        cycle = winding_position_cycle_length(period, winding_period)
        assert cycle == js_winding_position_cycle_length(period, winding_period)
        assert winding_position_feature(period, winding_period, position + cycle) == winding_position_feature(
            period,
            winding_period,
            position,
        )
        assert winding_position_feature(wrong_period, winding_period, position) == js_winding_position_feature(
            wrong_period,
            winding_period,
            position,
        )

    period = 8
    winding_period = 4
    wrong_period = 7
    train_length = 64
    test_length = 32
    train_positions, train_labels = synthetic_winding_position_dataset(period, winding_period, train_length)
    test_positions, test_labels = synthetic_winding_position_dataset(
        period,
        winding_period,
        test_length,
        start=train_length,
    )
    js_train_positions, js_train_labels = js_synthetic_winding_position_dataset(
        period,
        winding_period,
        train_length,
    )
    js_test_positions, js_test_labels = js_synthetic_winding_position_dataset(
        period,
        winding_period,
        test_length,
        train_length,
    )
    assert train_positions == js_train_positions
    assert train_labels == js_train_labels
    assert test_positions == js_test_positions
    assert test_labels == js_test_labels
    winding_lookup = fit_winding_position_lookup(period, winding_period, train_positions, train_labels)
    js_winding_lookup = js_fit_map_lookup(
        js_train_positions,
        js_train_labels,
        lambda item: js_winding_position_feature(period, winding_period, item),
    )
    assert winding_lookup == js_winding_lookup
    winding_predictions = predict_winding_position_lookup(
        period,
        winding_period,
        winding_lookup,
        test_positions,
    )
    js_winding_predictions = js_predict_map_lookup(
        js_winding_lookup,
        js_test_positions,
        lambda item: js_winding_position_feature(period, winding_period, item),
    )
    assert winding_predictions == js_winding_predictions
    residue_lookup = fit_phase_lookup(period, train_positions, train_labels)
    js_residue_lookup = js_fit_phase_lookup(period, js_train_positions, js_train_labels)
    assert residue_lookup == js_residue_lookup
    residue_predictions = predict_phase_lookup(period, residue_lookup, test_positions)
    js_residue_predictions = js_predict_phase_lookup(period, js_residue_lookup, js_test_positions)
    assert residue_predictions == js_residue_predictions
    wrong_lookup = fit_winding_position_lookup(wrong_period, winding_period, train_positions, train_labels)
    js_wrong_lookup = js_fit_map_lookup(
        js_train_positions,
        js_train_labels,
        lambda item: js_winding_position_feature(wrong_period, winding_period, item),
    )
    assert wrong_lookup == js_wrong_lookup
    wrong_predictions = predict_winding_position_lookup(
        wrong_period,
        winding_period,
        wrong_lookup,
        test_positions,
    )
    js_wrong_predictions = js_predict_map_lookup(
        js_wrong_lookup,
        js_test_positions,
        lambda item: js_winding_position_feature(wrong_period, winding_period, item),
    )
    assert wrong_predictions == js_wrong_predictions
    assert winding_alias_collision_count(period, train_positions, train_labels) == js_winding_alias_collision_count(
        period,
        js_train_positions,
        js_train_labels,
    )
    winding_benchmark = run_winding_aware_position_benchmark(
        period=period,
        winding_period=winding_period,
        wrong_period=wrong_period,
        train_length=train_length,
        test_length=test_length,
    )
    assert winding_benchmark.cycle_length == js_winding_position_cycle_length(period, winding_period)
    assert winding_benchmark.observed_winding_feature_count == len(js_winding_lookup)
    assert winding_benchmark.alias_collision_count == js_winding_alias_collision_count(
        period,
        js_train_positions,
        js_train_labels,
    )
    assert winding_benchmark.winding_position_accuracy == js_accuracy(js_winding_predictions, js_test_labels)
    assert winding_benchmark.residue_only_accuracy == js_accuracy(js_residue_predictions, js_test_labels)
    assert winding_benchmark.wrong_period_winding_accuracy == js_accuracy(js_wrong_predictions, js_test_labels)

    adapter_budget_cases = [
        (64, 8, 4, 16),
        (96, 12, 6, 10),
        (128, 7, 3, 5),
    ]
    for channel_count, block_size, rank, parameters_per_channel in adapter_budget_cases:
        channels = tuple(range(channel_count))
        loads = js_adapter_block_loads(block_size, channel_count)
        dense_count = js_dense_adapter_parameter_count(channel_count, parameters_per_channel)
        lora_count = js_lora_adapter_parameter_count(channel_count, parameters_per_channel, rank)
        block_count = js_block_cyclic_adapter_parameter_count(block_size, parameters_per_channel)
        assert dense_adapter_parameter_count(channel_count, parameters_per_channel) == dense_count
        assert lora_adapter_parameter_count(channel_count, parameters_per_channel, rank) == lora_count
        assert block_cyclic_adapter_parameter_count(block_size, parameters_per_channel) == block_count
        assert adapter_block_loads(block_size, channels) == loads
        assert adapter_block_collision_count(block_size, channels) == js_adapter_block_collision_count(loads)
        benchmark = run_adapter_parameter_budget_benchmark(
            channel_count=channel_count,
            block_size=block_size,
            rank=rank,
            parameters_per_channel=parameters_per_channel,
        )
        assert benchmark.dense_adapter_parameters == dense_count
        assert benchmark.lora_parameters == lora_count
        assert benchmark.block_cyclic_parameters == block_count
        assert benchmark.channel_collision_count == js_adapter_block_collision_count(loads)
        assert benchmark.max_block_load == max(loads)

    circulant_cases = [
        (5, 1),
        (8, 1),
        (11, 3),
    ]
    for period, wrong_shift in circulant_cases:
        values = js_default_circulant_input(period)
        kernel = js_default_circulant_kernel(period)
        assert default_circulant_input(period) == values
        assert default_circulant_kernel(period) == kernel
        assert circulant_mixer_output(values, kernel) == js_circulant_mixer_output(values, kernel)
        assert dense_circulant_matrix(kernel) == js_dense_circulant_matrix(kernel)
        assert dense_matrix_vector_product(dense_circulant_matrix(kernel), values) == js_dense_matrix_vector_product(
            js_dense_circulant_matrix(kernel),
            values,
        )
        assert rotate_kernel(kernel, wrong_shift) == js_rotate_kernel(kernel, wrong_shift)
        benchmark = run_circulant_mixer_benchmark(period=period, wrong_shift=wrong_shift)
        assert benchmark.circulant_output == js_circulant_mixer_output(values, kernel)
        assert benchmark.dense_output == js_dense_matrix_vector_product(
            js_dense_circulant_matrix(kernel),
            values,
        )
        assert benchmark.wrong_shift_output == js_circulant_mixer_output(
            values,
            js_rotate_kernel(kernel, wrong_shift),
        )
        assert benchmark.max_abs_dense_delta == 0
        assert benchmark.dense_parameters == period * period
        assert benchmark.circulant_parameters == period

    block_cyclic_cases = [
        (8, 2, 1),
        (12, 3, 1),
        (16, 4, 2),
    ]
    for channel_count, block_size, wrong_shift in block_cyclic_cases:
        values = js_default_block_cyclic_input(channel_count)
        kernel = js_default_block_cyclic_kernel(block_size)
        loads = js_block_cyclic_cell_loads(block_size, channel_count)
        assert default_block_cyclic_input(channel_count) == values
        assert default_block_cyclic_kernel(block_size) == kernel
        for row in range(channel_count):
            for column in range(channel_count):
                assert block_cyclic_cell(block_size, row, column) == js_block_cyclic_cell(
                    block_size,
                    row,
                    column,
                )
        assert block_cyclic_mixer_output(values, kernel) == js_block_cyclic_mixer_output(values, kernel)
        assert dense_block_cyclic_matrix(channel_count, kernel) == js_dense_block_cyclic_matrix(
            channel_count,
            kernel,
        )
        assert dense_matrix_vector_product(dense_block_cyclic_matrix(channel_count, kernel), values) == (
            js_dense_matrix_vector_product(js_dense_block_cyclic_matrix(channel_count, kernel), values)
        )
        assert rotate_block_cyclic_kernel_rows(kernel, wrong_shift) == js_rotate_block_cyclic_kernel_rows(
            kernel,
            wrong_shift,
        )
        assert block_cyclic_cell_loads(block_size, channel_count) == loads
        assert block_cyclic_cell_collision_count(block_size, channel_count) == js_block_cyclic_cell_collision_count(
            block_size,
            channel_count,
        )
        benchmark = run_block_cyclic_mixer_benchmark(
            channel_count=channel_count,
            block_size=block_size,
            wrong_row_shift=wrong_shift,
        )
        assert benchmark.block_cyclic_output == js_block_cyclic_mixer_output(values, kernel)
        assert benchmark.dense_output == js_dense_matrix_vector_product(
            js_dense_block_cyclic_matrix(channel_count, kernel),
            values,
        )
        assert benchmark.wrong_row_shift_output == js_block_cyclic_mixer_output(
            values,
            js_rotate_block_cyclic_kernel_rows(kernel, wrong_shift),
        )
        assert benchmark.max_abs_dense_delta == 0
        assert benchmark.dense_parameters == channel_count * channel_count
        assert benchmark.block_cyclic_parameters == block_size * block_size
        assert benchmark.cell_collision_count == js_block_cyclic_cell_collision_count(block_size, channel_count)
        assert benchmark.max_cell_load == max(load for row in loads for load in row)

    hopf_cases = [
        (12, 2, 1.0 - 1.0j, 2.0 + 1.0j),
        (8, 3, 1.0 + 2.0j, -1.0 + 0.5j),
        (7, 13, -2.0 + 1.0j, 0.5 - 1.5j),
    ]
    for period, step, z0, z1 in hopf_cases:
        theta = tau * js_mod(step, period) / period
        normalized = normalize_pair(z0, z1)
        phase_rotated = phase_rotate(*normalized, theta)
        js_record = js_hopf_phase_record(z0, z1, period, step)
        py_record = hopf_phase_record(z0, z1, theta)
        assert abs(pair_norm_sq(*normalized) - js_record["pair_norm_sq"]) <= 1e-10
        assert abs(pair_norm_sq(*phase_rotated) - js_record["rotated_pair_norm_sq"]) <= 1e-10
        assert point_close(hopf_map(*normalized), js_record["base_point"], tol=1e-10)
        assert point_close(hopf_map(*phase_rotated), js_record["rotated_base_point"], tol=1e-10)
        assert abs(sphere_norm_sq(hopf_map(*normalized)) - js_record["base_norm_sq"]) <= 1e-10
        assert abs(sphere_norm_sq(hopf_map(*phase_rotated)) - js_record["rotated_base_norm_sq"]) <= 1e-10
        assert py_record["base_points_match"] == js_record["base_points_match"]
        assert py_record["base_points_match"]

    spin_cases = [
        (8, 1, Quaternion(0.0, 1.0, 2.0, -1.0)),
        (12, 5, Quaternion(0.0, -2.0, 1.0, 3.0)),
        (7, 13, Quaternion(0.0, 0.0, -3.0, 2.0)),
    ]
    for period, step, vector in spin_cases:
        q = unit_i_phase(tau * js_mod(step, period) / period)
        py_record = orientation_debug_record(q, vector)
        js_record = js_orientation_debug_record(period, step, vector)
        assert quaternion_close(conjugation_action(q, vector), js_conjugation_action(q, vector))
        assert quaternion_close(conjugation_action(-q, vector), js_conjugation_action(-q, vector))
        assert py_record["representatives_are_distinct"] == js_record["representatives_are_distinct"]
        assert py_record["actions_match"] == js_record["actions_match"]
        assert py_record["spin_sign_related"] == js_record["spin_sign_related"]
        assert py_record["input_is_pure"] == js_record["input_is_pure"]
        assert py_record["q_action_is_pure"] == js_record["q_action_is_pure"]
        assert py_record["neg_q_action_is_pure"] == js_record["neg_q_action_is_pure"]
        assert spin_sign_related(q, -q) == js_spin_sign_related(q, -q)
        assert is_pure_quaternion(vector)
        assert is_pure_quaternion(conjugation_action(q, vector))
        assert quaternion_close(conjugation_action(q, vector), conjugation_action(-q, vector))

    print("widget Python parity ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
