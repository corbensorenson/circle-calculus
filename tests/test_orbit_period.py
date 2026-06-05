from math import gcd

from circle_math import Circle


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

