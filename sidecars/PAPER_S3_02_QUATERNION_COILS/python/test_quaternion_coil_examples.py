import math

from circle_math.dimensions.quaternion import Quaternion, unit_i_phase


TOL = 1e-12

ONE = Quaternion(1.0, 0.0, 0.0, 0.0)
I = Quaternion(0.0, 1.0, 0.0, 0.0)
J = Quaternion(0.0, 0.0, 1.0, 0.0)
K = Quaternion(0.0, 0.0, 0.0, 1.0)


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def assert_quaternion_close(left: Quaternion, right: Quaternion, *, tol: float = TOL) -> None:
    for left_coord, right_coord in zip(left.coordinates(), right.coordinates()):
        assert_close(left_coord, right_coord, tol=tol)


def test_quaternion_norm_square() -> None:
    assert ONE.squared_norm() == 1.0
    assert I.squared_norm() == 1.0
    assert J.squared_norm() == 1.0
    assert K.squared_norm() == 1.0
    assert Quaternion(1.0, 2.0, 3.0, 4.0).squared_norm() == 30.0


def test_unit_quaternion_multiplication_preserves_norm() -> None:
    units = [ONE, I, J, K, unit_i_phase(math.pi / 7.0)]
    for left in units:
        for right in units:
            assert_close((left * right).squared_norm(), 1.0)


def test_unit_quaternion_identity_laws() -> None:
    for q in [ONE, I, J, K, unit_i_phase(math.pi / 7.0), unit_i_phase(math.pi / 11.0)]:
        assert_quaternion_close(ONE * q, q)
        assert_quaternion_close(q * ONE, q)


def test_unit_quaternion_conjugate_is_inverse() -> None:
    for q in [ONE, I, J, K, unit_i_phase(math.pi / 5.0), unit_i_phase(math.pi / 3.0)]:
        assert_quaternion_close(q * q.conjugate(), ONE)
        assert_quaternion_close(q.conjugate() * q, ONE)


def test_unit_quaternion_conjugate_is_involutive() -> None:
    for q in [ONE, I, J, K, unit_i_phase(math.pi / 5.0), unit_i_phase(math.pi / 3.0)]:
        assert_quaternion_close(q.conjugate().conjugate(), q)


def test_quaternion_multiplication_is_noncommutative() -> None:
    assert I * J == K
    assert J * I == -K
    assert I * J != J * I


def test_quaternion_multiplication_is_associative_on_examples() -> None:
    examples = [ONE, I, J, K, Quaternion(1.0, 2.0, -1.0, 0.5)]
    for a in examples:
        for b in examples:
            for c in examples:
                assert_quaternion_close((a * b) * c, a * (b * c))
