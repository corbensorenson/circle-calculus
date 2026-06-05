from __future__ import annotations


def suspended_circle_counts(n: int) -> tuple[int, int, int]:
    """Return V,E,F for the planned finite suspended-circle model."""
    if n < 3:
        raise ValueError("suspended circle scaffold requires n >= 3")
    return (n + 2, 3 * n, 2 * n)


def sphere_grid_counts(n: int, r: int) -> tuple[int, int, int]:
    """Return V,E,F for the planned finite SphereGrid(n,r) model."""
    if n < 3:
        raise ValueError("sphere grid scaffold requires n >= 3")
    if r < 1:
        raise ValueError("sphere grid scaffold requires r >= 1")
    return (n * r + 2, n * (2 * r + 1), n * (r + 1))

