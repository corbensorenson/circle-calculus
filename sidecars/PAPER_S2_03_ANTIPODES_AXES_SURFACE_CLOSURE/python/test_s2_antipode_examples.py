from typing import Optional, Union


Pole = str
EquatorPoint = tuple[str, int]
SuspendedPoint = Union[Pole, EquatorPoint]

RingPoint = tuple[str, int, int]
SphereGridPoint = Union[Pole, RingPoint]


def suspended_antipode(n: int, point: SuspendedPoint) -> SuspendedPoint:
    if point == "north":
        return "south"
    if point == "south":
        return "north"
    tag, node = point
    assert tag == "equator"
    return ("equator", (-node) % n)


def is_pole(point: SuspendedPoint) -> bool:
    return point in ("north", "south")


def is_equator(point: SuspendedPoint) -> bool:
    return isinstance(point, tuple) and point[0] == "equator"


def antipodal_pair(n: int, left: SuspendedPoint, right: SuspendedPoint) -> bool:
    return suspended_antipode(n, left) == right


def suspended_longitude_rotation(n: int, stride: int, point: SuspendedPoint) -> SuspendedPoint:
    if point in ("north", "south"):
        return point
    tag, node = point
    assert tag == "equator"
    return ("equator", (node + stride) % n)


def longitude_rotation(n: int, stride: int, point: SphereGridPoint) -> SphereGridPoint:
    if point in ("north", "south"):
        return point
    tag, latitude, node = point
    assert tag == "ring"
    return ("ring", latitude, (node + stride) % n)


def latitude_coordinate(point: SphereGridPoint) -> Optional[int]:
    if point in ("north", "south"):
        return None
    return point[1]


def longitude_coordinate(point: SphereGridPoint) -> Optional[int]:
    if point in ("north", "south"):
        return None
    return point[2]


def suspended_points(n: int) -> tuple[SuspendedPoint, ...]:
    return ("north", "south", *(("equator", node) for node in range(n)))


def sphere_grid_points(n: int, r: int) -> tuple[SphereGridPoint, ...]:
    return ("north", "south", *(("ring", latitude, node) for latitude in range(r) for node in range(n)))


def test_suspended_antipode_swaps_poles() -> None:
    for n in range(1, 33):
        assert suspended_antipode(n, "north") == "south"
        assert suspended_antipode(n, "south") == "north"


def test_suspended_antipode_is_involutive() -> None:
    for n in range(1, 33):
        for point in suspended_points(n):
            assert suspended_antipode(n, suspended_antipode(n, point)) == point


def test_suspended_antipode_is_bijective() -> None:
    for n in range(1, 33):
        points = set(suspended_points(n))
        images = {suspended_antipode(n, point) for point in points}
        assert images == points


def test_suspended_longitude_rotation_is_bijective() -> None:
    for n in range(1, 33):
        points = set(suspended_points(n))
        for stride in range(-64, 65):
            images = {suspended_longitude_rotation(n, stride, point) for point in points}
            assert images == points


def test_suspended_antipode_preserves_pole_and_equator_sets() -> None:
    for n in range(1, 33):
        for point in suspended_points(n):
            antipode = suspended_antipode(n, point)
            assert is_pole(antipode) == is_pole(point)
            assert is_equator(antipode) == is_equator(point)


def test_suspended_antipode_longitude_rotation_opposite_stride() -> None:
    for n in range(1, 33):
        for stride in range(-64, 65):
            for point in suspended_points(n):
                rotate_then_antipode = suspended_antipode(
                    n, suspended_longitude_rotation(n, stride, point)
                )
                antipode_then_opposite = suspended_longitude_rotation(
                    n, -stride, suspended_antipode(n, point)
                )
                assert rotate_then_antipode == antipode_then_opposite


def test_longitude_rotation_preserves_latitude_coordinate() -> None:
    for n in range(1, 16):
        for r in range(1, 8):
            for point in sphere_grid_points(n, r):
                assert latitude_coordinate(longitude_rotation(n, 3, point)) == latitude_coordinate(point)


def test_longitude_rotation_advances_longitude_coordinate() -> None:
    for n in range(1, 16):
        for r in range(1, 8):
            for stride in range(0, 16):
                for point in sphere_grid_points(n, r):
                    rotated = longitude_rotation(n, stride, point)
                    longitude = longitude_coordinate(point)
                    expected = None if longitude is None else (longitude + stride) % n
                    assert longitude_coordinate(rotated) == expected


def test_antipodal_pair_self_and_symmetry() -> None:
    for n in range(1, 33):
        for point in suspended_points(n):
            antipode = suspended_antipode(n, point)
            assert antipodal_pair(n, point, antipode)
            assert antipodal_pair(n, point, antipode) == antipodal_pair(n, antipode, point)
