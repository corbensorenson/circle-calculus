from math import gcd

from circle_math import Circle


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
