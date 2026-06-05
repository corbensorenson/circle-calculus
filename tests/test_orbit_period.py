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


def test_period_eq_n_div_gcd() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for k in range(0, 257):
            expected = n // gcd(n, k)
            assert c.period(k) == expected
            assert len(c.orbit(0, k)) == expected


def test_orbit_decomposition() -> None:
    for n in range(1, 97):
        c = Circle(n)
        for k in range(0, 193):
            orbits = c.orbit_decomposition(k)
            flat = [node for orbit in orbits for node in orbit]
            assert len(orbits) == gcd(n, k)
            assert sorted(flat) == list(range(n))
            assert all(len(orbit) == n // gcd(n, k) for orbit in orbits)


def test_same_orbit_matches_gcd_congruence_examples() -> None:
    for n in range(1, 65):
        c = Circle(n)
        for k in range(0, 129):
            g = gcd(n, k)
            labels = orbit_class_labels(c, k)
            for x in range(0, n):
                for y in range(0, n):
                    assert (labels[x] == labels[y]) == ((x - y) % g == 0)
