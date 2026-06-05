from math import gcd

from circle_math import Circle


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n**0.5) + 1))


def test_prime_full_coils() -> None:
    for p in range(2, 258):
        if not is_prime(p):
            continue
        c = Circle(p)
        for k in range(1, p):
            assert c.is_full_coil(k)
            assert len(c.orbit(0, k)) == p


def test_composites_have_non_full_stride() -> None:
    for n in range(2, 257):
        if is_prime(n):
            continue
        c = Circle(n)
        assert any(gcd(n, k) != 1 and not c.is_full_coil(k) for k in range(1, n))

