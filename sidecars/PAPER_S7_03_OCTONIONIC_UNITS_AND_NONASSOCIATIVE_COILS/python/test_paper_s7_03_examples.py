from circle_math.dimensions.octonion import Octonion, normalize, octonion_basis, real_part


TOL = 1e-12


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def test_octonion_basis_has_eight_unit_elements() -> None:
    basis = octonion_basis()

    assert len(basis) == 8
    for unit in basis:
        assert_close(unit.squared_norm(), 1.0)


def test_octonion_conjugate_norm_returns_real_norm_square() -> None:
    value = Octonion((1.0, -2.0, 0.5, 0.25, 1.5, -0.75, 0.0, 2.0))
    product = value * value.conjugate()

    assert_close(real_part(product), value.squared_norm())
    assert product.coordinates[1:] == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def test_octonion_norm_multiplicative_on_sample_values() -> None:
    left = Octonion((1.0, 0.5, -0.25, 0.0, 1.5, 0.25, -0.75, 0.5))
    right = Octonion((-0.5, 1.25, 0.75, -1.0, 0.0, 0.5, 0.25, -0.25))

    assert_close((left * right).squared_norm(), left.squared_norm() * right.squared_norm())


def test_unit_octonion_product_stays_unit_on_sample_values() -> None:
    left = normalize(Octonion((1.0, 1.0, 0.5, -0.25, 0.75, 0.0, -0.5, 0.25)))
    right = normalize(Octonion((0.25, -1.0, 0.5, 0.75, -0.25, 1.0, 0.0, -0.5)))

    assert_close(left.squared_norm(), 1.0)
    assert_close(right.squared_norm(), 1.0)
    assert_close((left * right).squared_norm(), 1.0)


def test_octonion_multiplication_is_noncommutative() -> None:
    _, e1, e2, *_ = octonion_basis()

    assert e1 * e2 != e2 * e1


def test_octonion_multiplication_is_nonassociative() -> None:
    basis = octonion_basis()
    e1, e2, e4 = basis[1], basis[2], basis[4]

    assert (e1 * e2) * e4 != e1 * (e2 * e4)
