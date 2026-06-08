"""Seed-and-rule provenance fixtures for Circle Calculus.

These helpers test a constructive-compression framing: a generated artifact is
stored with the seed and rules needed to rebuild it. This is not a minimality
theorem or a substitute for formal proof.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from circle_math.finite import Circle
from circle_math.physics import path_holonomy, square_plaquette_path


@dataclass(frozen=True)
class GenerationRule:
    rule_id: str
    parameters: tuple[tuple[str, int | str], ...] = ()


@dataclass(frozen=True)
class SeedRuleProvenance:
    artifact_id: str
    seed: tuple[tuple[str, int | str], ...]
    rules: tuple[GenerationRule, ...]
    iteration_schedule: str
    closure_condition: str
    generated_object: Any
    theorem_ids: tuple[str, ...]
    dictionary_ids: tuple[str, ...]
    note: str = "Generator fixture only; not a minimality theorem."


@dataclass(frozen=True)
class GeneratorComparison:
    artifact_id: str
    exact_regeneration: bool
    explicit_length: int
    generator_length: int
    generator_shorter: bool
    note: str = "Description-length fixture only; not universal compression."


@dataclass(frozen=True)
class BoundedGeneratorSearch:
    search_id: str
    candidate_count: int
    exact_candidate_count: int
    best_exact: Optional[GeneratorComparison]
    best_shorter: Optional[GeneratorComparison]
    finite_search_space: bool = True
    theorem_ids: tuple[str, ...] = (
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
    )
    note: str = "Bounded finite search only; not an optimality theorem."


def _sorted_pairs(mapping: Mapping[str, int | str]) -> tuple[tuple[str, int | str], ...]:
    return tuple(sorted(mapping.items()))


def _json_length(value: Any) -> int:
    return len(json.dumps(value, sort_keys=True, separators=(",", ":")))


def _record_description(record: SeedRuleProvenance) -> dict[str, Any]:
    return {
        "artifact_id": record.artifact_id,
        "seed": record.seed,
        "rules": tuple((rule.rule_id, rule.parameters) for rule in record.rules),
        "iteration_schedule": record.iteration_schedule,
        "closure_condition": record.closure_condition,
        "theorem_ids": record.theorem_ids,
        "dictionary_ids": record.dictionary_ids,
    }


def _finite_circle_diagram(n: int) -> dict[str, Any]:
    nodes = tuple({"id": node, "label": f"{node} mod {n}"} for node in range(n))
    edges = tuple(
        {"source": node, "target": (node + 1) % n, "rule": "successor_mod_n"}
        for node in range(n)
    )
    return {"nodes": nodes, "edges": edges}


def _physics_loop_diagram(
    modulus: int,
    *,
    bottom: int,
    right: int,
    top: int,
    left: int,
) -> dict[str, Any]:
    path = square_plaquette_path(
        modulus,
        bottom=bottom,
        right=right,
        top=top,
        left=left,
    )
    vertices = tuple({"id": vertex} for vertex in ("v00", "v10", "v11", "v01"))
    edges = tuple(
        {
            "source": edge.source,
            "target": edge.target,
            "phase": edge.phase,
            "label": f"{edge.phase} mod {modulus}",
            "rule": "plaquette_edge_phase",
        }
        for edge in path.edges
    )
    return {
        "modulus": modulus,
        "vertices": vertices,
        "edges": edges,
        "closed": path.closed,
        "holonomy": path_holonomy(path),
    }


def regenerate(record: SeedRuleProvenance) -> Any:
    seed = dict(record.seed)
    if record.artifact_id == "finite_circle":
        return tuple(range(int(seed["n"])))
    if record.artifact_id == "finite_circle_diagram":
        return _finite_circle_diagram(int(seed["n"]))
    if record.artifact_id == "physics_loop_diagram":
        return _physics_loop_diagram(
            int(seed["modulus"]),
            bottom=int(seed["bottom"]),
            right=int(seed["right"]),
            top=int(seed["top"]),
            left=int(seed["left"]),
        )
    if record.artifact_id == "coil_orbit":
        circle = Circle(int(seed["n"]))
        return tuple(circle.orbit(int(seed.get("start", 0)), int(seed["stride"])))
    if record.artifact_id == "orbit_decomposition":
        circle = Circle(int(seed["n"]))
        return tuple(tuple(orbit) for orbit in circle.orbit_decomposition(int(seed["stride"])))
    if record.artifact_id == "proof_glyph":
        return {
            "glyph_id": seed["glyph_id"],
            "theorem_id": seed["theorem_id"],
            "lean_name": seed["lean_name"],
        }
    raise ValueError(f"unknown artifact id: {record.artifact_id}")


def finite_circle_generator(n: int) -> SeedRuleProvenance:
    if n <= 0:
        raise ValueError("n must be positive")
    generated = tuple(range(n))
    return SeedRuleProvenance(
        artifact_id="finite_circle",
        seed=_sorted_pairs({"n": n}),
        rules=(GenerationRule("enumerate_nodes", _sorted_pairs({"start": 0, "stop": n})),),
        iteration_schedule="i = 0..n-1",
        closure_condition="stop before node n, since nodes are residues modulo n",
        generated_object=generated,
        theorem_ids=(
            "GEN-T0001",
            "GEN-T0020",
            "GEN-T0040",
            "GEN-T0041",
            "GEN-T0042",
            "GEN-T0043",
            "CC-T0001",
        ),
        dictionary_ids=("CC-0001", "CC-0002", "COMMON-0064", "COMMON-0066"),
    )


def finite_circle_diagram_generator(n: int) -> SeedRuleProvenance:
    if n <= 0:
        raise ValueError("n must be positive")
    generated = _finite_circle_diagram(n)
    return SeedRuleProvenance(
        artifact_id="finite_circle_diagram",
        seed=_sorted_pairs({"n": n}),
        rules=(
            GenerationRule("enumerate_nodes", _sorted_pairs({"start": 0, "stop": n})),
            GenerationRule("connect_successor_mod_n"),
        ),
        iteration_schedule="nodes i=0..n-1; edges i -> (i+1) mod n",
        closure_condition="successor edge from n-1 returns to node 0",
        generated_object=generated,
        theorem_ids=("CC-T0001", "CC-T0002"),
        dictionary_ids=("CC-0001", "CC-0002", "COMMON-0064", "COMMON-0066"),
        note="Generated diagram fixture only; not a formal proof or minimality theorem.",
    )


def physics_loop_diagram_generator(
    modulus: int,
    *,
    bottom: int,
    right: int,
    top: int,
    left: int,
) -> SeedRuleProvenance:
    generated = _physics_loop_diagram(
        modulus,
        bottom=bottom,
        right=right,
        top=top,
        left=left,
    )
    return SeedRuleProvenance(
        artifact_id="physics_loop_diagram",
        seed=_sorted_pairs(
            {
                "modulus": modulus,
                "bottom": bottom,
                "right": right,
                "top": top,
                "left": left,
            }
        ),
        rules=(
            GenerationRule("normalize_link_phases_mod_n"),
            GenerationRule("connect_square_plaquette"),
            GenerationRule("sum_closed_loop_holonomy"),
        ),
        iteration_schedule="v00 -> v10 -> v11 -> v01 -> v00",
        closure_condition="fourth edge returns to v00, so the finite loop is closed",
        generated_object=generated,
        theorem_ids=("PHYS-T0005", "PHYS-T0012"),
        dictionary_ids=(
            "COMMON-0060",
            "COMMON-0061",
            "COMMON-0062",
            "COMMON-0063",
            "COMMON-0064",
            "COMMON-0066",
        ),
        note="Generated finite physics-loop diagram fixture only; not a formal proof, physics claim, or minimality theorem.",
    )


def coil_orbit_generator(n: int, stride: int, start: int = 0) -> SeedRuleProvenance:
    circle = Circle(n)
    generated = tuple(circle.orbit(start, stride))
    return SeedRuleProvenance(
        artifact_id="coil_orbit",
        seed=_sorted_pairs({"n": n, "stride": stride, "start": start}),
        rules=(GenerationRule("repeat_rotation", _sorted_pairs({"stride": stride})),),
        iteration_schedule="x_0=start; x_{t+1}=x_t+stride mod n",
        closure_condition="stop when the next node has already appeared",
        generated_object=generated,
        theorem_ids=("GEN-T0002", "GEN-T0021", "CC-T0005", "CC-T0006"),
        dictionary_ids=("CC-0201", "CC-0205", "COMMON-0064", "COMMON-0066"),
    )


def orbit_decomposition_generator(n: int, stride: int) -> SeedRuleProvenance:
    circle = Circle(n)
    generated = tuple(tuple(orbit) for orbit in circle.orbit_decomposition(stride))
    return SeedRuleProvenance(
        artifact_id="orbit_decomposition",
        seed=_sorted_pairs({"n": n, "stride": stride}),
        rules=(
            GenerationRule("repeat_rotation", _sorted_pairs({"stride": stride})),
            GenerationRule("restart_at_smallest_unvisited"),
        ),
        iteration_schedule="generate one closed orbit, then restart at the smallest unvisited node",
        closure_condition="stop when every node in C_n has appeared exactly once",
        generated_object=generated,
        theorem_ids=(
            "GEN-T0003",
            "GEN-T0006",
            "GEN-T0007",
            "GEN-T0008",
            "GEN-T0009",
            "GEN-T0010",
            "GEN-T0011",
            "GEN-T0012",
            "GEN-T0013",
            "CC-T0006",
        ),
        dictionary_ids=("CC-0205", "CC-0208", "COMMON-0064", "COMMON-0066"),
    )


def proof_glyph_generator(glyph_id: str, theorem_id: str, lean_name: str) -> SeedRuleProvenance:
    generated = {
        "glyph_id": glyph_id,
        "theorem_id": theorem_id,
        "lean_name": lean_name,
    }
    return SeedRuleProvenance(
        artifact_id="proof_glyph",
        seed=_sorted_pairs({"glyph_id": glyph_id, "theorem_id": theorem_id, "lean_name": lean_name}),
        rules=(GenerationRule("project_certificate_fields"),),
        iteration_schedule="single certificate construction",
        closure_condition="generated fields match seed fields",
        generated_object=generated,
        theorem_ids=("GEN-T0004", "P2G-T0001", "P2G-T0002", "P2G-T0003"),
        dictionary_ids=("COMMON-0033", "COMMON-0064", "COMMON-0066"),
    )


def compare_generator_to_explicit(record: SeedRuleProvenance) -> GeneratorComparison:
    regenerated = regenerate(record)
    explicit = {"artifact_id": record.artifact_id, "generated_object": record.generated_object}
    generator = _record_description(record)
    return GeneratorComparison(
        artifact_id=record.artifact_id,
        exact_regeneration=regenerated == record.generated_object,
        explicit_length=_json_length(explicit),
        generator_length=_json_length(generator),
        generator_shorter=_json_length(generator) < _json_length(explicit),
    )


def bounded_generator_search(
    records: Sequence[SeedRuleProvenance],
    *,
    search_id: str = "bounded_generator_search",
) -> BoundedGeneratorSearch:
    """Rank a declared finite set of generator records by description length.

    The result is scoped only to the supplied finite candidate list. It does not
    claim global minimality, Kolmogorov complexity, or universal compression.
    """

    comparisons = tuple(compare_generator_to_explicit(record) for record in records)
    exact = tuple(comparison for comparison in comparisons if comparison.exact_regeneration)
    shorter = tuple(comparison for comparison in exact if comparison.generator_shorter)

    def key(comparison: GeneratorComparison) -> tuple[int, int, str]:
        return (comparison.generator_length, comparison.explicit_length, comparison.artifact_id)

    return BoundedGeneratorSearch(
        search_id=search_id,
        candidate_count=len(comparisons),
        exact_candidate_count=len(exact),
        best_exact=min(exact, key=key) if exact else None,
        best_shorter=min(shorter, key=key) if shorter else None,
    )
