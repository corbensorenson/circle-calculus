from circle_math.dimensions.common import euler_characteristic
from circle_math.dimensions.sphere_grid import suspended_circle_counts


def test_suspended_circle_counts() -> None:
    for n in range(3, 65):
        assert suspended_circle_counts(n) == (n + 2, 3 * n, 2 * n)


def test_suspended_circle_euler_characteristic() -> None:
    for n in range(3, 65):
        assert euler_characteristic(suspended_circle_counts(n)) == 2
