from circle_math.dimensions.common import euler_characteristic, suspension_counts
from circle_math.dimensions.hypersphere import suspended_suspended_circle_counts


def s4_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(suspended_suspended_circle_counts(n))


def test_s4_counts_are_suspension_of_s3_counts() -> None:
    for n in range(3, 65):
        assert s4_counts(n) == suspension_counts(suspended_suspended_circle_counts(n))


def test_s4_euler_characteristic() -> None:
    for n in range(3, 65):
        assert euler_characteristic(s4_counts(n)) == 2
