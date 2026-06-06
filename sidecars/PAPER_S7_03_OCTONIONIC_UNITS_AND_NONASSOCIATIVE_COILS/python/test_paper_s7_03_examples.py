from circle_math.dimensions.octonion import Octonion, normalize, octonion_basis, real_part


TOL = 1e-12


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def assert_octonion_close(left: Octonion, right: Octonion, *, tol: float = TOL) -> None:
    for left_value, right_value in zip(left.coordinates, right.coordinates):
        assert_close(left_value, right_value, tol=tol)


def test_octonion_basis_has_eight_unit_elements() -> None:
    basis = octonion_basis()

    assert len(basis) == 8
    for unit in basis:
        assert_close(unit.squared_norm(), 1.0)


def test_octonion_conjugate_norm_returns_real_norm_square() -> None:
    value = Octonion((1.0, -2.0, 0.5, 0.25, 1.5, -0.75, 0.0, 2.0))
    right_product = value * value.conjugate()
    left_product = value.conjugate() * value

    assert_close(real_part(right_product), value.squared_norm())
    assert right_product.coordinates[1:] == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert_close(real_part(left_product), value.squared_norm())
    assert left_product.coordinates[1:] == (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


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


def test_unit_octonion_conjugate_inverse_with_explicit_bracketing() -> None:
    one = Octonion((1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    units = (
        normalize(Octonion((1.0, 1.0, 0.5, -0.25, 0.75, 0.0, -0.5, 0.25))),
        normalize(Octonion((0.25, -1.0, 0.5, 0.75, -0.25, 1.0, 0.0, -0.5))),
        *octonion_basis(),
    )

    for unit in units:
        assert_close(unit.squared_norm(), 1.0)
        assert_octonion_close(unit * unit.conjugate(), one)
        assert_octonion_close(unit.conjugate() * unit, one)


def test_octonion_multiplication_is_noncommutative() -> None:
    _, e1, e2, *_ = octonion_basis()

    assert e1 * e2 != e2 * e1


def test_octonion_multiplication_is_nonassociative() -> None:
    basis = octonion_basis()
    e1, e2, e4 = basis[1], basis[2], basis[4]

    assert (e1 * e2) * e4 != e1 * (e2 * e4)
