from __future__ import annotations

from math import gcd

from circle_math.applications import (
    loop_exit_certificate,
    loop_required_steps,
    token_recurrence_budget,
    training_free_loop_budget,
)
from circle_math.finite import Circle
from circle_math.generative import (
    finite_circle_diagram_generator,
    physics_loop_diagram_generator,
    regenerate,
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


def js_finite_circle_diagram(n: int) -> dict:
    nodes = tuple({"id": node, "label": f"{node} mod {n}"} for node in range(n))
    edges = tuple(
        {"source": node, "target": (node + 1) % n, "rule": "successor_mod_n"}
        for node in range(n)
    )
    return {"nodes": nodes, "edges": edges}


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


def js_loop_required_steps(loop_period: int, sample_index: int) -> int:
    return js_mod(sample_index, loop_period) + 1


def js_token_recurrence_budget(loop_period: int, token_index: int) -> int:
    return js_loop_required_steps(loop_period, token_index)


def js_training_free_loop_budget(loop_period: int, sample_index: int, max_loops: int) -> int:
    return min(js_loop_required_steps(loop_period, sample_index), max_loops)


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

    print("widget Python parity ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
