from __future__ import annotations

from math import gcd

from circle_math import Circle


def test_scaling_reversible_examples() -> None:
    assert Circle(12).scale_is_permutation(5)
    assert not Circle(12).scale_is_permutation(4)
    assert Circle(13).scale_is_permutation(5)


def test_scaling_reversible_iff_coprime_small_range() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 65):
            assert circle.scale_is_permutation(k) == (gcd(n, k) == 1)
