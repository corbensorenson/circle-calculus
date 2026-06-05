from circle_math.dimensions.common import euler_characteristic
from circle_math.dimensions.hypersphere import (
    suspended_surface_counts,
    suspended_suspended_circle_counts,
)
from circle_math.dimensions.sphere_grid import sphere_grid_counts, suspended_circle_counts


def test_suspended_surface_counts() -> None:
    examples = [
        (4, 6, 4),
        (8, 12, 6),
        (6, 12, 8),
        (10, 20, 12),
    ]
    for vertices, edges, faces in examples:
        assert suspended_surface_counts(vertices, edges, faces) == (
            vertices + 2,
            edges + 2 * vertices,
            faces + 2 * edges,
            2 * faces,
        )


def test_suspending_sphere_like_surface_has_chi_zero() -> None:
    examples = [
        (4, 6, 4),
        (8, 12, 6),
        suspended_circle_counts(7),
        sphere_grid_counts(5, 3),
    ]
    for counts in examples:
        assert euler_characteristic(counts) == 2
        assert euler_characteristic(suspended_surface_counts(*counts)) == 0


def test_suspended_suspended_circle_counts() -> None:
    for n in range(3, 65):
        assert suspended_suspended_circle_counts(n) == (n + 4, 5 * n + 4, 8 * n, 4 * n)


def test_suspended_suspended_circle_euler_characteristic() -> None:
    for n in range(3, 65):
        assert euler_characteristic(suspended_suspended_circle_counts(n)) == 0
