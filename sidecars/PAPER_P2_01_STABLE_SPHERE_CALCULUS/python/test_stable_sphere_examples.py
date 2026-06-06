from circle_math.dimensions.common import euler_characteristic, suspension_counts


def double_suspension_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    return suspension_counts(suspension_counts(counts))


def four_suspension_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    return double_suspension_counts(double_suspension_counts(counts))


def eight_suspension_counts(counts: tuple[int, ...]) -> tuple[int, ...]:
    return four_suspension_counts(four_suspension_counts(counts))


def test_double_suspension_preserves_euler_characteristic() -> None:
    examples = [
        (),
        (3,),
        (5, 8),
        (4, 12, 10),
        (2, 7, 9, 4),
    ]
    for counts in examples:
        assert euler_characteristic(double_suspension_counts(counts)) == euler_characteristic(counts)


def test_four_suspension_is_two_double_suspensions() -> None:
    examples = [
        (),
        (1,),
        (6, 9),
        (3, 11, 12),
    ]
    for counts in examples:
        assert four_suspension_counts(counts) == double_suspension_counts(double_suspension_counts(counts))


def test_four_suspension_preserves_euler_characteristic() -> None:
    examples = [
        (),
        (2,),
        (3, 5),
        (7, 12, 10),
        (4, 9, 13, 6),
    ]
    for counts in examples:
        assert euler_characteristic(four_suspension_counts(counts)) == euler_characteristic(counts)


def test_eight_suspension_is_two_four_suspensions() -> None:
    examples = [
        (),
        (1,),
        (2, 3),
        (5, 8, 13),
    ]
    for counts in examples:
        assert eight_suspension_counts(counts) == four_suspension_counts(four_suspension_counts(counts))


def test_eight_suspension_preserves_euler_characteristic() -> None:
    examples = [
        (),
        (4,),
        (6, 10),
        (3, 7, 9),
        (2, 5, 11, 17),
    ]
    for counts in examples:
        assert euler_characteristic(eight_suspension_counts(counts)) == euler_characteristic(counts)
