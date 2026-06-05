from __future__ import annotations

from circle_math.dimensions.common import euler_characteristic, suspension_counts
from circle_math.dimensions.hypersphere import suspended_suspended_circle_counts
from circle_math.dimensions.sphere_grid import sphere_grid_counts, suspended_circle_counts


def test_euler_characteristic_and_suspension_transform() -> None:
    assert euler_characteristic((5, 9, 6)) == 2
    assert suspension_counts((5, 9, 6)) == (7, 19, 24, 12)
    assert euler_characteristic(suspension_counts((5, 9, 6))) == 0


def test_suspended_circle_counts() -> None:
    assert suspended_circle_counts(5) == (7, 15, 10)
    assert euler_characteristic(suspended_circle_counts(5)) == 2


def test_sphere_grid_counts() -> None:
    assert sphere_grid_counts(5, 3) == (17, 35, 20)
    assert euler_characteristic(sphere_grid_counts(5, 3)) == 2


def test_suspended_suspended_circle_counts() -> None:
    assert suspended_suspended_circle_counts(5) == (9, 29, 40, 20)
    assert euler_characteristic(suspended_suspended_circle_counts(5)) == 0

