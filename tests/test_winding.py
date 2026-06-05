from circle_math.winding import lift, lift_add, lift_iter_successor, lift_successor


def test_lift_unique_decomposition_round_trip() -> None:
    for modulus in range(1, 65):
        for value in range(0, 2048):
            lifted = lift(modulus, value)
            assert 0 <= lifted.residue < modulus
            assert lifted.value == value


def test_lift_successor_with_carry() -> None:
    for modulus in range(1, 65):
        for value in range(0, 2048):
            successor = lift_successor(modulus, value)
            assert successor.value == value + 1
            assert 0 <= successor.residue < modulus


def test_lift_add_path_concatenation() -> None:
    for modulus in range(1, 33):
        for left in range(0, 96):
            for right in range(0, 96):
                added = lift_add(modulus, left, right)
                assert added.value == left + right
                assert 0 <= added.residue < modulus


def test_lift_add_zero_identity() -> None:
    for modulus in range(1, 65):
        for value in range(0, 2048):
            lifted = lift(modulus, value)
            assert lift_add(modulus, value, 0) == lifted
            assert lift_add(modulus, 0, value) == lifted


def test_lift_add_associative_value() -> None:
    for modulus in range(1, 17):
        for left in range(0, 32):
            for middle in range(0, 32):
                for right in range(0, 32):
                    left_assoc = lift_add(modulus, left + middle, right)
                    right_assoc = lift_add(modulus, left, middle + right)
                    assert left_assoc.value == right_assoc.value


def test_lift_iter_successor_induction() -> None:
    for modulus in range(1, 33):
        for value in range(0, 256):
            for steps in range(0, 64):
                iterated = lift_iter_successor(modulus, value, steps)
                assert iterated.value == value + steps
                assert 0 <= iterated.residue < modulus
