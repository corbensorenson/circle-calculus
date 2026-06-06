from circle_math.dimensions.common import euler_characteristic, suspension_counts
from circle_math.dimensions.hypersphere import suspended_suspended_circle_counts
from circle_math.dimensions.octonion import Octonion, octonion_basis


TOL = 1e-10


def assert_close(left: float, right: float, *, tol: float = TOL) -> None:
    assert abs(left - right) <= tol


def s4_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(suspended_suspended_circle_counts(n))


def s5_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s4_counts(n))


def s6_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s5_counts(n))


def s7_counts(n: int) -> tuple[int, ...]:
    return suspension_counts(s6_counts(n))


def eight_suspensions(cells: tuple[int, ...]) -> tuple[int, ...]:
    result = cells
    for _ in range(8):
        result = suspension_counts(result)
    return result


def s15_topological_model(n: int) -> tuple[int, ...]:
    return eight_suspensions(s7_counts(n))


def octonion_pair_norm_sq(left: Octonion, right: Octonion) -> float:
    return left.squared_norm() + right.squared_norm()


def normalize_pair(left: Octonion, right: Octonion) -> tuple[Octonion, Octonion]:
    norm_sq = octonion_pair_norm_sq(left, right)
    if norm_sq == 0.0:
        raise ValueError("cannot normalize a zero octonion pair")
    scale = norm_sq ** -0.5
    return (left.scale(scale), right.scale(scale))


def octonionic_hopf_map(left: Octonion, right: Octonion) -> tuple[Octonion, float]:
    octonion_part = (left * right.conjugate()).scale(2.0)
    scalar = left.squared_norm() - right.squared_norm()
    return (octonion_part, scalar)


def right_phase_pair(left: Octonion, right: Octonion, phase: Octonion) -> tuple[Octonion, Octonion]:
    return (left * phase, right * phase)


def hopf_base9_norm_sq(base: tuple[Octonion, float]) -> float:
    octonion_part, scalar = base
    return octonion_part.squared_norm() + scalar * scalar


def octonionic_hopf_roadmap() -> str:
    return "S7 -> S15 -> S8"


def test_octonionic_hopf_roadmap_marker() -> None:
    assert octonionic_hopf_roadmap() == "S7 -> S15 -> S8"


def test_s15_topological_model_is_eight_suspensions_of_s7() -> None:
    for n in range(3, 24):
        assert s15_topological_model(n) == eight_suspensions(s7_counts(n))


def test_eight_suspensions_preserve_euler_characteristic() -> None:
    examples = [
        (),
        (2,),
        (4, 6, 4),
        (8, 12, 6),
        (7, 21, 14),
    ]
    for cells in examples:
        assert euler_characteristic(eight_suspensions(cells)) == euler_characteristic(cells)


def test_s15_topological_model_euler_characteristic() -> None:
    for n in range(3, 24):
        assert euler_characteristic(s15_topological_model(n)) == 0


def test_octonionic_hopf_coordinate_identity_on_examples() -> None:
    examples = [
        (
            Octonion((1.0, -0.5, 0.25, 0.0, 0.75, -0.25, 0.5, 1.25)),
            Octonion((-0.25, 1.0, 0.5, -0.75, 0.0, 0.25, -0.5, 0.5)),
        ),
        (
            Octonion((0.5, 0.25, -1.0, 0.75, 0.0, 0.5, 1.0, -0.25)),
            Octonion((1.25, -0.5, 0.0, 0.25, -0.75, 0.5, 0.25, 0.0)),
        ),
    ]
    for left, right in examples:
        base = octonionic_hopf_map(left, right)
        pair_norm = octonion_pair_norm_sq(left, right)
        assert_close(hopf_base9_norm_sq(base), pair_norm * pair_norm)


def test_octonionic_hopf_lands_on_unit_base_for_normalized_pair() -> None:
    examples = [
        (
            Octonion((1.0, -0.5, 0.25, 0.0, 0.75, -0.25, 0.5, 1.25)),
            Octonion((-0.25, 1.0, 0.5, -0.75, 0.0, 0.25, -0.5, 0.5)),
        ),
        (
            Octonion((0.5, 0.25, -1.0, 0.75, 0.0, 0.5, 1.0, -0.25)),
            Octonion((1.25, -0.5, 0.0, 0.25, -0.75, 0.5, 0.25, 0.0)),
        ),
    ]
    for left, right in examples:
        normalized_left, normalized_right = normalize_pair(left, right)
        assert_close(octonion_pair_norm_sq(normalized_left, normalized_right), 1.0)
        assert_close(hopf_base9_norm_sq(octonionic_hopf_map(normalized_left, normalized_right)), 1.0)


def test_right_unit_octonion_phase_preserves_pair_norm_and_landing() -> None:
    basis = octonion_basis()
    examples = [
        (
            *normalize_pair(
                Octonion((1.0, -0.5, 0.25, 0.0, 0.75, -0.25, 0.5, 1.25)),
                Octonion((-0.25, 1.0, 0.5, -0.75, 0.0, 0.25, -0.5, 0.5)),
            ),
            basis[4],
        ),
        (
            *normalize_pair(
                Octonion((0.5, 0.25, -1.0, 0.75, 0.0, 0.5, 1.0, -0.25)),
                Octonion((1.25, -0.5, 0.0, 0.25, -0.75, 0.5, 0.25, 0.0)),
            ),
            basis[7],
        ),
    ]

    for left, right, phase in examples:
        assert_close(phase.squared_norm(), 1.0)
        phased_left, phased_right = right_phase_pair(left, right, phase)
        assert_close(octonion_pair_norm_sq(phased_left, phased_right), 1.0)
        assert_close(hopf_base9_norm_sq(octonionic_hopf_map(phased_left, phased_right)), 1.0)


def test_right_unit_octonion_phase_preserves_hopf_scalar_coordinate() -> None:
    left, right, phase = (
        Octonion((1.0, -0.5, 0.25, 0.0, 0.75, -0.25, 0.5, 1.25)),
        Octonion((-0.25, 1.0, 0.5, -0.75, 0.0, 0.25, -0.5, 0.5)),
        octonion_basis()[4],
    )
    phased_left, phased_right = right_phase_pair(left, right, phase)

    assert_close(phase.squared_norm(), 1.0)
    assert_close(octonionic_hopf_map(phased_left, phased_right)[1], octonionic_hopf_map(left, right)[1])


def test_naive_right_unit_octonion_phase_does_not_preserve_full_hopf_coordinates() -> None:
    basis = octonion_basis()
    left, right, phase = basis[1], basis[2], basis[4]
    phased_left, phased_right = right_phase_pair(left, right, phase)
    phased_hopf = octonionic_hopf_map(phased_left, phased_right)
    original_hopf = octonionic_hopf_map(left, right)

    assert_close(phase.squared_norm(), 1.0)
    assert_close(phased_hopf[1], original_hopf[1])
    assert phased_hopf[0] != original_hopf[0]
