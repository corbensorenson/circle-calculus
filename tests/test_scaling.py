from math import gcd

from circle_math import Circle


def test_scale_permutation_iff_coprime() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for k in range(0, 257):
            assert c.scale_is_permutation(k) == (gcd(n, k) == 1)

