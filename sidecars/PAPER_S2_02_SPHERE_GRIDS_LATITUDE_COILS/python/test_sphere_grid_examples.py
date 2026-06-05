from math import gcd
from typing import Union

from circle_math.dimensions.common import euler_characteristic
from circle_math.dimensions.sphere_grid import sphere_grid_counts


Pole = str
RingPoint = tuple[str, int, int]
SphereGridPoint = Union[Pole, RingPoint]


def longitude_rotation(n: int, stride: int, point: SphereGridPoint) -> SphereGridPoint:
    if point in ("north", "south"):
        return point
    tag, latitude, node = point
    assert tag == "ring"
    return ("ring", latitude, (node + stride) % n)


def latitude_coil_period(n: int, stride: int) -> int:
    assert n > 0
    return n // gcd(n, stride)


def test_sphere_grid_counts() -> None:
    for n in range(3, 33):
        for r in range(1, 12):
            assert sphere_grid_counts(n, r) == (n * r + 2, n * (2 * r + 1), n * (r + 1))


def test_sphere_grid_euler_characteristic() -> None:
    for n in range(3, 33):
        for r in range(1, 12):
            assert euler_characteristic(sphere_grid_counts(n, r)) == 2


def test_longitude_rotation_fixes_poles() -> None:
    for n in range(3, 33):
        for stride in range(0, 64):
            assert longitude_rotation(n, stride, "north") == "north"
            assert longitude_rotation(n, stride, "south") == "south"


def test_longitude_rotation_preserves_latitude_ring() -> None:
    for n in range(3, 16):
        for r in range(1, 8):
            for latitude in range(r):
                for node in range(n):
                    rotated = longitude_rotation(n, 5, ("ring", latitude, node))
                    assert rotated[1] == latitude


def test_latitude_coil_period() -> None:
    for n in range(1, 65):
        for stride in range(0, 65):
            assert latitude_coil_period(n, stride) == n // gcd(n, stride)
