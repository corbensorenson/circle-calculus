from math import gcd

from circle_math import Circle


def coil_step(n: int, stride: int, start: int, steps: int) -> int:
    return (start + steps * stride) % n


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


def test_scale_transports_rotation_stride() -> None:
    for n in range(1, 65):
        c = Circle(n)
        for i in range(0, 129):
            for k in range(0, 33):
                for stride in range(0, 33):
                    assert c.scale(c.rot(i, stride), k) == c.rot(c.scale(i, k), k * stride)


def test_scale_transports_coil_step() -> None:
    for n in range(1, 33):
        c = Circle(n)
        for start in range(0, 33):
            for steps in range(0, 17):
                for k in range(0, 9):
                    for stride in range(0, 9):
                        assert c.scale(coil_step(n, stride, start, steps), k) == coil_step(
                            n, k * stride, k * start, steps
                        )


def test_prime_scale_bijective() -> None:
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        circle = Circle(p)
        for k in range(1, p):
            assert circle.scale_is_permutation(k)


def test_scale_cofactor_zero_for_divisors() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                assert circle.scale(n // k, k) == 0
