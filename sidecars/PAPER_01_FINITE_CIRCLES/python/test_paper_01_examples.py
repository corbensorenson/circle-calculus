from math import gcd

from circle_math import Circle


def same_orbit_by_decomposition(circle: Circle, stride: int, x: int, y: int) -> bool:
    x_node = circle.node(x)
    y_node = circle.node(y)
    return any(x_node in orbit and y_node in orbit for orbit in circle.orbit_decomposition(stride))


def orbit_class_labels(circle: Circle, stride: int) -> dict[int, int]:
    labels: dict[int, int] = {}
    for index, orbit in enumerate(circle.orbit_decomposition(stride)):
        for node in orbit:
            labels[node] = index
    return labels


def test_prime_example_c13_stride5() -> None:
    assert Circle(13).orbit(0, 5) == [0, 5, 10, 2, 7, 12, 4, 9, 1, 6, 11, 3, 8]


def test_composite_example_c12_stride4() -> None:
    assert Circle(12).orbit(0, 4) == [0, 4, 8]
    assert Circle(12).period(4) == 3
    assert len(Circle(12).orbit_decomposition(4)) == 4


def test_full_coil_iff_coprime_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for stride in range(0, 65):
            assert circle.is_full_coil(stride) == (gcd(n, stride) == 1)


def test_same_orbit_gcd_congruence_examples() -> None:
    circle = Circle(12)
    assert same_orbit_by_decomposition(circle, 4, 1, 9)
    assert not same_orbit_by_decomposition(circle, 4, 1, 10)

    for n in range(1, 25):
        c = Circle(n)
        for stride in range(0, 49):
            g = gcd(n, stride)
            labels = orbit_class_labels(c, stride)
            for x in range(n):
                for y in range(n):
                    assert (labels[x] == labels[y]) == ((x - y) % g == 0)
