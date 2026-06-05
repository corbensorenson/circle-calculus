from __future__ import annotations

from .common import suspension_counts
from .sphere_grid import suspended_circle_counts


def suspended_surface_counts(vertices: int, edges: int, faces: int) -> tuple[int, int, int, int]:
    """Return V,E,F,T for the suspension of a finite surface count triple."""
    counts = suspension_counts((vertices, edges, faces))
    return (counts[0], counts[1], counts[2], counts[3])


def suspended_suspended_circle_counts(n: int) -> tuple[int, int, int, int]:
    """Return V,E,F,T for Susp(SuspC(n))."""
    return suspended_surface_counts(*suspended_circle_counts(n))

