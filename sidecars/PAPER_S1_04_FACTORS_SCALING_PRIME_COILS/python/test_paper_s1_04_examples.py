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


def test_full_coil_iff_coprime_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 65):
            assert circle.is_full_coil(k) == (gcd(n, k) == 1)
            assert (circle.period(k) == n) == (gcd(n, k) == 1)


def test_scale_zero_factor_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for i in range(0, 129):
            assert circle.scale(i, 0) == 0


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


def test_scale_natural_step_to_coil_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            for steps in range(0, 65):
                assert circle.scale(steps, k) == coil_step(n, k, 0, steps)


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


def test_add_cofactor_multiple_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(1, n + 1):
            if n % k == 0:
                cofactor = n // k
                for x in range(0, 17):
                    for m in range(0, 7):
                        assert circle.scale(x + m * cofactor, k) == circle.scale(x, k)


def test_scale_zero_divisibility_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            for x in range(0, 65):
                assert (circle.scale(x, k) == 0) == ((k * x) % n == 0)


def test_scale_zero_period_divisibility_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(0, 65):
                assert (circle.scale(x, k) == 0) == (x % period == 0)


def test_scale_kernel_subgroup_membership_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(0, 65):
                assert (circle.scale(x, k) == 0) == (x % period == 0)


def test_scale_period_multiple_zero_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for m in range(0, 17):
                assert circle.scale(m * period, k) == 0


def test_scale_add_period_multiple_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(0, 33):
                for m in range(0, 9):
                    assert circle.scale(x + m * period, k) == circle.scale(x, k)


def test_scale_period_normal_form_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(0, 129):
                assert circle.scale(x, k) == circle.scale(x % period, k)


def test_scale_equality_congruence_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            for x in range(0, 33):
                for y in range(0, 33):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (
                        (k * x) % n == (k * y) % n
                    )


def test_scale_equality_period_congruence_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            period = circle.period(k)
            for x in range(0, 33):
                for y in range(0, 33):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (
                        x % period == y % period
                    )


def test_scale_period_representatives_injective_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            for x in range(period):
                for y in range(period):
                    assert (circle.scale(x, k) == circle.scale(y, k)) == (x == y)


def test_scale_period_representative_image_card_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            image = {circle.scale(r, k) for r in range(period)}
            assert len(image) == period


def test_scaled_addresses_lie_in_period_representative_image_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            image = {circle.scale(r, k) for r in range(period)}
            for x in range(0, 129):
                assert circle.scale(x, k) in image


def test_scale_circle_image_equals_period_representative_image_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            circle_image = {circle.scale(x, k) for x in range(n)}
            representative_image = {circle.scale(r, k) for r in range(period)}
            assert circle_image == representative_image


def test_scale_circle_image_card_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            circle_image = {circle.scale(x, k) for x in range(n)}
            assert len(circle_image) == period


def test_scale_kernel_representatives_equal_period_multiples_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            period = circle.period(k)
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            period_multiples = {m * period for m in range(gcd(n, k))}
            assert kernel == period_multiples


def test_scale_kernel_representative_card_examples() -> None:
    for n in range(1, 65):
        circle = Circle(n)
        for k in range(0, 33):
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            assert len(kernel) == gcd(n, k)


def test_scale_fiber_representatives_equal_period_fibers_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            period = circle.period(k)
            for r in range(0, 17):
                fiber = {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(r, k)
                }
                period_fibers = {r % period + m * period for m in range(gcd(n, k))}
                assert fiber == period_fibers


def test_scale_fiber_representative_card_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            for r in range(0, 17):
                fiber = {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(r, k)
                }
                assert len(fiber) == gcd(n, k)


def test_scale_zero_fiber_equals_kernel_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            zero_fiber = {
                x
                for x in range(n)
                if circle.scale(x, k) == circle.scale(0, k)
            }
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            assert zero_fiber == kernel


def test_scale_target_fiber_empty_outside_image_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            image = {circle.scale(x, k) for x in range(n)}
            for target in range(n):
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                if target not in image:
                    assert fiber == set()


def test_scale_target_fiber_card_inside_image_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            image = {circle.scale(x, k) for x in range(n)}
            for target in image:
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                assert len(fiber) == gcd(n, k)


def test_scale_target_fiber_over_scaled_representative_equals_representative_fiber_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            for r in range(0, 17):
                target = circle.scale(r, k)
                target_fiber = {
                    x for x in range(n) if circle.scale(x, k) == target
                }
                representative_fiber = {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(r, k)
                }
                assert target_fiber == representative_fiber


def test_scale_fiber_sets_equal_iff_scaled_representatives_equal_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            fibers = {
                s: {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(s, k)
                }
                for s in range(0, 33)
            }
            for r in range(n):
                fiber_r = fibers[r]
                for s in range(0, 33):
                    fiber_s = fibers[s]
                    assert (fiber_r == fiber_s) == (
                        circle.scale(r, k) == circle.scale(s, k)
                    )


def test_scale_fiber_sets_equal_iff_period_congruent_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            period = circle.period(k)
            fibers = {
                s: {
                    x
                    for x in range(n)
                    if circle.scale(x, k) == circle.scale(s, k)
                }
                for s in range(0, 33)
            }
            for r in range(n):
                fiber_r = fibers[r]
                for s in range(0, 33):
                    fiber_s = fibers[s]
                    assert (fiber_r == fiber_s) == (r % period == s % period)


def test_scale_image_card_times_target_fiber_card_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            image = {circle.scale(x, k) for x in range(n)}
            for target in image:
                fiber = {x for x in range(n) if circle.scale(x, k) == target}
                assert len(image) * len(fiber) == n


def test_scale_image_card_times_kernel_card_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 17):
            image = {circle.scale(x, k) for x in range(n)}
            kernel = {x for x in range(n) if circle.scale(x, k) == 0}
            assert len(image) * len(kernel) == n


def test_coprime_scale_equality_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 33):
            if gcd(n, k) == 1:
                for x in range(0, 33):
                    for y in range(0, 33):
                        assert (circle.scale(x, k) == circle.scale(y, k)) == (
                            x % n == y % n
                        )


def test_scale_factor_mod_equivalent_examples() -> None:
    for n in range(1, 33):
        circle = Circle(n)
        for k in range(0, 33):
            for m in range(0, 9):
                equivalent = k + m * n
                for x in range(0, 33):
                    assert circle.scale(x, k) == circle.scale(x, equivalent)
