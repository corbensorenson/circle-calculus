from math import gcd

from circle_math import Circle


def test_scale_permutation_iff_coprime() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for k in range(0, 257):
            assert c.scale_is_permutation(k) == (gcd(n, k) == 1)


def test_scale_one_identity() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for i in range(0, 257):
            assert c.scale(i, 1) == c.node(i)


def test_scale_composition() -> None:
    for n in range(1, 65):
        c = Circle(n)
        for i in range(0, 129):
            for a in range(0, 33):
                for b in range(0, 33):
                    assert c.scale(c.scale(i, b), a) == c.scale(i, a * b)
