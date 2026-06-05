from dataclasses import dataclass


@dataclass(frozen=True)
class DirectedInterval:
    source: int
    target: int


def interval_boundary(interval: DirectedInterval) -> int:
    return interval.target - interval.source


def point_boundary(_chain: int) -> int:
    return 0


def reverse_interval(interval: DirectedInterval) -> DirectedInterval:
    return DirectedInterval(source=interval.target, target=interval.source)


def constant_interval(point: int) -> DirectedInterval:
    return DirectedInterval(source=point, target=point)


def test_boundary_boundary_interval_zero() -> None:
    for source in range(-5, 6):
        for target in range(-5, 6):
            interval = DirectedInterval(source=source, target=target)
            assert point_boundary(interval_boundary(interval)) == 0


def test_interval_boundary_reverse_negates_boundary() -> None:
    for source in range(-5, 6):
        for target in range(-5, 6):
            interval = DirectedInterval(source=source, target=target)
            assert interval_boundary(reverse_interval(interval)) == -interval_boundary(interval)


def test_reverse_interval_is_involutive() -> None:
    for source in range(-5, 6):
        for target in range(-5, 6):
            interval = DirectedInterval(source=source, target=target)
            assert reverse_interval(reverse_interval(interval)) == interval


def test_constant_interval_has_zero_boundary() -> None:
    for point in range(-20, 21):
        assert interval_boundary(constant_interval(point)) == 0
