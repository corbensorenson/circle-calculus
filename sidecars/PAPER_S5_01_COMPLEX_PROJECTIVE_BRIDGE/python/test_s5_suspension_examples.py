from circle_math.dimensions.common import euler_characteristic, suspension_counts
from circle_math.dimensions.hypersphere import suspended_suspended_circle_counts


def s4_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(suspended_suspended_circle_counts(n))


def s5_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s4_counts(n))


def test_s5_counts_are_suspension_of_s4_counts() -> None:
    for n in range(3, 65):
        assert s5_counts(n) == suspension_counts(s4_counts(n))


def test_s5_euler_characteristic() -> None:
    for n in range(3, 65):
        assert euler_characteristic(s5_counts(n)) == 0
