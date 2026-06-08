from circle_math.dimensions.quaternion import (
    Quaternion,
    conjugation_action,
    is_pure_quaternion,
    orientation_debug_record,
    quaternion_close,
    unit_i_phase,
)


TOL = 1e-12

ONE = Quaternion(1.0, 0.0, 0.0, 0.0)
ZERO = Quaternion(0.0, 0.0, 0.0, 0.0)


def assert_quaternion_close(left: Quaternion, right: Quaternion, *, tol: float = TOL) -> None:
    for left_coord, right_coord in zip(left.coordinates(), right.coordinates()):
        assert abs(left_coord - right_coord) <= tol


def spin_sign_related(left: Quaternion, right: Quaternion) -> bool:
    return quaternion_close(right, left) or quaternion_close(right, -left)


def test_quaternion_conjugation_identity_action() -> None:
    examples = [
        ZERO,
        Quaternion(0.0, 1.0, 0.0, 0.0),
        Quaternion(0.0, 0.0, 1.0, 0.0),
        Quaternion(1.0, 2.0, -1.0, 0.5),
    ]
    for value in examples:
        assert_quaternion_close(conjugation_action(ONE, value), value)


def test_quaternion_conjugation_zero_vector() -> None:
    for q in [
        ONE,
        unit_i_phase(0.25),
        Quaternion(2.0, -1.0, 0.5, 3.0),
    ]:
        assert_quaternion_close(conjugation_action(q, ZERO), ZERO)


def test_quaternion_conjugation_preserves_pure_vector_inputs() -> None:
    quaternions = [
        ONE,
        unit_i_phase(0.5),
        Quaternion(2.0, -1.0, 0.5, 3.0),
    ]
    vectors = [
        ZERO,
        Quaternion(0.0, 1.0, 0.0, 0.0),
        Quaternion(0.0, 0.0, -2.0, 1.0),
        Quaternion(0.0, 3.0, -4.0, 5.0),
    ]
    for q in quaternions:
        for v in vectors:
            assert is_pure_quaternion(v)
            assert is_pure_quaternion(conjugation_action(q, v))


def test_quaternion_conjugation_sign_cancellation() -> None:
    quaternions = [
        ONE,
        unit_i_phase(0.5),
        Quaternion(2.0, -1.0, 0.5, 3.0),
    ]
    vectors = [
        ZERO,
        Quaternion(0.0, 1.0, 0.0, 0.0),
        Quaternion(0.0, 0.0, -2.0, 1.0),
    ]
    for q in quaternions:
        for v in vectors:
            assert_quaternion_close(conjugation_action(-q, v), conjugation_action(q, v))


def test_spin_sign_relation_is_equivalence_on_examples() -> None:
    representatives = [
        ONE,
        -ONE,
        unit_i_phase(0.5),
        -unit_i_phase(0.5),
        unit_i_phase(1.0),
        -unit_i_phase(1.0),
    ]

    for q in representatives:
        assert spin_sign_related(q, q)

    for q in representatives:
        for r in representatives:
            if spin_sign_related(q, r):
                assert spin_sign_related(r, q)

    for p in representatives:
        for q in representatives:
            for r in representatives:
                if spin_sign_related(p, q) and spin_sign_related(q, r):
                    assert spin_sign_related(p, r)


def test_orientation_debug_record_exposes_sign_ambiguity() -> None:
    q = unit_i_phase(0.75)
    v = Quaternion(0.0, 1.0, 2.0, -0.5)
    record = orientation_debug_record(q, v)
    assert record["representatives_are_distinct"]
    assert record["actions_match"]
    assert record["spin_sign_related"]
    assert record["input_is_pure"]
    assert record["q_action_is_pure"]
    assert record["neg_q_action_is_pure"]
