from circle_math.extremal import (
    all_binary_colorings_have_3ap,
    find_monochromatic_arithmetic_progression,
    find_monochromatic_combinatorial_line,
    find_monochromatic_homothetic_copy,
)


def test_binary_colorings_of_nine_points_have_3ap() -> None:
    assert all_binary_colorings_have_3ap(9)


def test_monochromatic_homothetic_copy_example() -> None:
    coloring = {point: point % 2 for point in range(9)}
    copy = find_monochromatic_homothetic_copy(
        (0, 1, 2), coloring, max_scale=4, max_translate=2
    )
    assert copy is not None
    assert copy.theorem_id == "CC-T0069"
    assert copy.scale == 2
    assert copy.image == (0, 2, 4)


def test_monochromatic_progression_and_hales_jewett_line_examples() -> None:
    coloring = {point: point % 2 for point in range(9)}
    progression = find_monochromatic_arithmetic_progression(coloring, length=3)
    assert progression is not None
    assert progression.progression == (0, 2, 4)

    line = find_monochromatic_combinatorial_line(
        (0, 1),
        2,
        lambda word: sum(int(value) for value in word) % 2,
    )
    assert line is not None
    assert line.theorem_id == "CC-T0068"
    assert line.variable_positions == (0, 1)
    assert line.words == ((0, 0), (1, 1))
