from circle_math.dimensions.common import euler_characteristic, suspension_counts
from circle_math.dimensions.hypersphere import suspended_suspended_circle_counts


def s4_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(suspended_suspended_circle_counts(n))


def s5_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s4_counts(n))


def s6_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s5_counts(n))


def test_common_suspension_euler_formula() -> None:
    examples = [
        (),
        (2,),
        (4, 6, 4),
        (8, 12, 6),
        (7, 21, 14),
    ]
    for counts in examples:
        assert euler_characteristic(suspension_counts(counts)) == 2 - euler_characteristic(counts)


def test_s4_s5_s6_euler_parity() -> None:
    for n in range(3, 65):
        assert euler_characteristic(suspended_suspended_circle_counts(n)) == 0
        assert euler_characteristic(s4_counts(n)) == 2
        assert euler_characteristic(s5_counts(n)) == 0
        assert euler_characteristic(s6_counts(n)) == 2
