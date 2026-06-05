from math import gcd

from circle_math import Circle


def coil_step(n: int, stride: int, start: int, steps: int) -> int:
    return (start + steps * stride) % n


def test_scale_permutation_iff_coprime() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for k in range(0, 257):
            assert c.scale_is_permutation(k) == (gcd(n, k) == 1)


def test_scale_zero_factor() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for i in range(0, 257):
            assert c.scale(i, 0) == 0


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


def test_scale_natural_step_to_coil_step() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for k in range(0, 65):
            for steps in range(0, 129):
                assert c.scale(steps, k) == coil_step(n, k, 0, steps)


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


def test_scale_cofactor_multiples_zero_for_divisors() -> None:
    for n in range(1, 97):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                cofactor = n // k
                for m in range(0, 17):
                    assert circle.scale(m * cofactor, k) == 0


def test_scale_add_cofactor_multiple_for_divisors() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                cofactor = n // k
                for x in range(0, 33):
                    for m in range(0, 9):
                        assert circle.scale(x + m * cofactor, k) == circle.scale(x, k)


def test_scale_zero_iff_modulus_divides_product() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            for x in range(0, 129):
                assert (circle.scale(x, k) == 0) == ((k * x) % n == 0)


def test_scale_zero_iff_period_divides_address() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for x in range(0, 129):
                assert (circle.scale(x, k) == 0) == (x % period == 0)


def test_scale_kernel_subgroup_membership_matches_period_divisibility() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for x in range(0, 129):
                assert (circle.scale(x, k) == 0) == (x % period == 0)


def test_scale_period_multiples_zero() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for m in range(0, 33):
                assert circle.scale(m * period, k) == 0


def test_scale_add_period_multiple() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for x in range(0, 65):
                for m in range(0, 17):
                    assert circle.scale(x + m * period, k) == circle.scale(x, k)


def test_scale_period_normal_form() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for x in range(0, 257):
                assert circle.scale(x, k) == circle.scale(x % period, k)


def test_scale_equality_iff_scaled_products_congruent() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            for x in range(0, 65):
                for y in range(0, 65):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (
                        (k * x) % n == (k * y) % n
                    )


def test_scale_equality_iff_period_congruent() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(0, 65):
                for y in range(0, 65):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (
                        x % period == y % period
                    )


def test_scale_period_representatives_injective() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            for x in range(period):
                for y in range(period):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (x == y)


def test_scale_period_representative_image_card() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            image = {circle.scale(r, k) for r in range(period)}
            assert len(image) == period


def test_scaled_addresses_lie_in_period_representative_image() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            image = {circle.scale(r, k) for r in range(period)}
            for x in range(0, 257):
                assert circle.scale(x, k) in image


def test_scale_circle_image_equals_period_representative_image() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            circle_image = {circle.scale(x, k) for x in range(n)}
            representative_image = {circle.scale(r, k) for r in range(period)}
            assert circle_image == representative_image


def test_scale_circle_image_card() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            circle_image = {circle.scale(x, k) for x in range(n)}
            assert len(circle_image) == period


def test_scale_kernel_representatives_equal_period_multiples() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            period = circle.period(k)
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            period_multiples = {m * period for m in range(gcd(n, k))}
            assert kernel == period_multiples


def test_scale_kernel_representative_card() -> None:
    for n in range(1, 129):
        circle = Circle(n)
        for k in range(0, 65):
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            assert len(kernel) == gcd(n, k)


def test_scale_fiber_representatives_equal_period_fibers() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for r in range(0, 33):
                fiber = {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(r, k)
                }
                period_fibers = {r % period + m * period for m in range(gcd(n, k))}
                assert fiber == period_fibers


def test_scale_fiber_representative_card() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            for r in range(0, 33):
                fiber = {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(r, k)
                }
                assert len(fiber) == gcd(n, k)


def test_scale_target_fiber_empty_outside_image() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            image = {circle.scale(x, k) for x in range(n)}
            for target in range(n):
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                if target not in image:
                    assert fiber == set()


def test_scale_target_fiber_card_inside_image() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            image = {circle.scale(x, k) for x in range(n)}
            for target in image:
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                assert len(fiber) == gcd(n, k)


def test_scale_image_card_times_target_fiber_card() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            image = {circle.scale(x, k) for x in range(n)}
            for target in image:
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                assert len(image) * len(fiber) == n


def test_scale_image_card_times_kernel_card() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            image = {circle.scale(x, k) for x in range(n)}
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            assert len(image) * len(kernel) == n


def test_coprime_scale_equality_iff_addresses_congruent() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 65):
            if gcd(n, k) == 1:
                for x in range(0, 65):
                    for y in range(0, 65):
                        assert (circle.scale(x, k) == circle.scale(y, k)) == (
                            x % n == y % n
                        )


def test_scale_factor_mod_equivalent() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 65):
            for m in range(0, 17):
                equivalent = k + m * n
                for x in range(0, 65):
                    assert circle.scale(x, k) == circle.scale(x, equivalent)
