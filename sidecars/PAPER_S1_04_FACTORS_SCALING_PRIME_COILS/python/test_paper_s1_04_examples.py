from __future__ import annotations

from math import gcd

from circle_math import Circle


def coil_step(n: int, stride: int, start: int, steps: int) -> int:
    return (start + steps * stride) % n


def test_scaling_reversible_examples() -> None:
    assert Circle(12).scale_is_permutation(5)
    assert not Circle(12).scale_is_permutation(4)
    assert Circle(13).scale_is_permutation(5)


def test_scaling_reversible_iff_coprime_small_range() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 65):
            assert circle.scale_is_permutation(k) == (gcd(n, k) == 1)


def test_scaling_identity_and_composition_examples() -> None:
    circle = Circle(12)
    assert circle.scale(7, 1) == 7
    assert circle.scale(circle.scale(7, 5), 3) == circle.scale(7, 15)
    assert circle.scale(circle.rot(7, 4), 5) == circle.rot(circle.scale(7, 5), 20)
    assert circle.scale(coil_step(12, 4, 7, 3), 5) == coil_step(12, 20, 35, 3)

    for n in range(1, 33):
        circle = Circle(n)
        for i in range(0, 65):
            assert circle.scale(i, 1) == circle.node(i)
            for a in range(0, 17):
                for b in range(0, 17):
                    assert circle.scale(circle.scale(i, b), a) == circle.scale(i, a * b)
            for k in range(0, 17):
                for stride in range(0, 17):
                    assert circle.scale(circle.rot(i, stride), k) == circle.rot(
                        circle.scale(i, k), k * stride
                    )
                    assert circle.scale(coil_step(n, stride, i, 5), k) == coil_step(
                        n, k * stride, k * i, 5
                    )


def test_prime_scaling_examples() -> None:
    for p in [2, 3, 5, 7, 11, 13, 17, 19]:
        circle = Circle(p)
        for k in range(1, p):
            assert circle.scale_is_permutation(k)


def test_cofactor_zero_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                assert circle.scale(n // k, k) == 0


def test_cofactor_multiple_zero_examples() -> None:
    for n in range(1, 49):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                cofactor = n // k
                for m in range(0, 13):
                    assert circle.scale(m * cofactor, k) == 0
