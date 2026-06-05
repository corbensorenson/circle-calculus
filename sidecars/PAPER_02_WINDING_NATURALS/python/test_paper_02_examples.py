from circle_math.winding import lift, lift_add, lift_iter_successor, lift_successor


def test_seventeen_steps_around_c5() -> None:
    lifted = lift(5, 17)
    assert lifted.winding == 3
    assert lifted.residue == 2
    assert lifted.value == 17


def test_lift_round_trip_examples() -> None:
    examples = [(3, 0), (3, 8), (5, 17), (12, 49)]
    for modulus, value in examples:
        lifted = lift(modulus, value)
        assert lifted.value == value
        assert 0 <= lifted.residue < modulus


def test_successor_no_carry_and_with_carry() -> None:
    no_carry = lift_successor(5, 17)
    assert no_carry.winding == 3
    assert no_carry.residue == 3
    assert no_carry.value == 18

    with_carry = lift_successor(5, 19)
    assert with_carry.winding == 4
    assert with_carry.residue == 0
    assert with_carry.value == 20


def test_path_concatenation_addition() -> None:
    added = lift_add(5, 17, 8)
    assert added.winding == 5
    assert added.residue == 0
    assert added.value == 25


def test_addition_zero_identity_example() -> None:
    assert lift_add(5, 17, 0) == lift(5, 17)
    assert lift_add(5, 0, 17) == lift(5, 17)


def test_addition_associativity_value_example() -> None:
    left_assoc = lift_add(5, 17 + 8, 4)
    right_assoc = lift_add(5, 17, 8 + 4)
    assert left_assoc.value == right_assoc.value == 29


def test_iterated_successor_example() -> None:
    iterated = lift_iter_successor(5, 17, 8)
    assert iterated.winding == 5
    assert iterated.residue == 0
    assert iterated.value == 25
