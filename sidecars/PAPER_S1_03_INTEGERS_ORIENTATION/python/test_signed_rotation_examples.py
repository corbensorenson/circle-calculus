def signed_rot(size: int, stride: int, node: int) -> int:
    assert size > 0
    return (node + stride) % size


def test_signed_rotation_zero_fixes_nodes() -> None:
    for size in range(1, 25):
        for node in range(size):
            assert signed_rot(size, 0, node) == node


def test_signed_rotation_composition_adds_strides() -> None:
    for size in range(1, 25):
        for node in range(size):
            for left in range(-12, 13):
                for right in range(-12, 13):
                    composed = signed_rot(size, left, signed_rot(size, right, node))
                    direct = signed_rot(size, left + right, node)
                    assert composed == direct


def test_signed_rotation_inverse_returns_to_start() -> None:
    for size in range(1, 25):
        for node in range(size):
            for stride in range(-64, 65):
                assert signed_rot(size, -stride, signed_rot(size, stride, node)) == node
