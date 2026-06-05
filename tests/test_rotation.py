from circle_math import Circle


def test_rot_zero() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for i in range(-256, 257):
            assert c.rot(i, 0) == c.node(i)


def test_rot_comp() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for a in range(-16, 17):
            for b in range(-16, 17):
                for i in range(-16, 17):
                    assert c.rot(c.rot(i, b), a) == c.rot(i, a + b)


def test_rot_inverse() -> None:
    for n in range(1, 129):
        c = Circle(n)
        for a in range(-256, 257):
            for i in range(-16, 17):
                assert c.rot(c.rot(i, a), -a) == c.node(i)

