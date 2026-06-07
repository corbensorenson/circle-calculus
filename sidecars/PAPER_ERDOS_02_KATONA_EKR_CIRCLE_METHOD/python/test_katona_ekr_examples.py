from circle_math.extremal import (
    ekr_star_example,
    is_intersecting_family,
    is_uniform_family,
    katona_prefixed_density_example,
)


def test_katona_prefixed_density_count() -> None:
    example = katona_prefixed_density_example(5, [0, 2])
    assert example.theorem_id == "CC-T0064"
    assert example.prefixed_count == 12
    assert example.total_numberings == 120
    assert example.density == example.expected_density
    assert example.passes_bound


def test_ekr_star_family_is_sharp_intersecting_example() -> None:
    example = ekr_star_example(6, 3, center=0)
    assert example.theorem_id == "CC-T0065"
    assert len(example.family) == 10
    assert example.bound == 10
    assert is_uniform_family(example.family, 3)
    assert is_intersecting_family(example.family)
    assert example.is_sharp_example
