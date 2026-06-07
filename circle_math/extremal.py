from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb, cos, factorial, pi, sin, sqrt
from typing import Callable, Hashable, Iterable, Mapping, Optional, Sequence


def _unique_sorted(values: Iterable[int]) -> tuple[int, ...]:
    return tuple(sorted(set(values)))


def _validate_ground_size(size: int) -> None:
    if size <= 0:
        raise ValueError("ground size must be positive")


def _validate_subset(ground_size: int, subset: Iterable[int]) -> tuple[int, ...]:
    _validate_ground_size(ground_size)
    normalized = _unique_sorted(subset)
    if any(value < 0 or ground_size <= value for value in normalized):
        raise ValueError("subset entries must lie in range(ground_size)")
    return normalized


@dataclass(frozen=True)
class PrefixDensityExample:
    ground_size: int
    subset: tuple[int, ...]
    prefixed_count: int
    total_numberings: int
    density: Fraction
    expected_density: Fraction

    @property
    def theorem_id(self) -> str:
        return "CC-T0064"

    @property
    def passes_bound(self) -> bool:
        return self.density == self.expected_density


def katona_prefixed_density_example(
    ground_size: int, subset: Iterable[int]
) -> PrefixDensityExample:
    """Count numberings where `subset` is the prefix block."""

    normalized = _validate_subset(ground_size, subset)
    subset_size = len(normalized)
    prefixed_count = factorial(subset_size) * factorial(ground_size - subset_size)
    total_numberings = factorial(ground_size)
    return PrefixDensityExample(
        ground_size=ground_size,
        subset=normalized,
        prefixed_count=prefixed_count,
        total_numberings=total_numberings,
        density=Fraction(prefixed_count, total_numberings),
        expected_density=Fraction(1, comb(ground_size, subset_size)),
    )


def ekr_star_family(n: int, r: int, *, center: int = 0) -> tuple[tuple[int, ...], ...]:
    """Return the standard sharp EKR star: all `r`-sets containing `center`."""

    _validate_ground_size(n)
    if r <= 0 or n < r:
        raise ValueError("require 0 < r <= n")
    if center < 0 or n <= center:
        raise ValueError("center must lie in range(n)")

    others = [value for value in range(n) if value != center]
    family = []
    for tail in combinations(others, r - 1):
        family.append(tuple(sorted((center, *tail))))
    return tuple(family)


def is_uniform_family(family: Iterable[Iterable[int]], size: int) -> bool:
    return all(len(set(member)) == size for member in family)


def is_intersecting_family(family: Iterable[Iterable[int]]) -> bool:
    members = [set(member) for member in family]
    return all(members[i] & members[j] for i in range(len(members)) for j in range(i + 1, len(members)))


@dataclass(frozen=True)
class EKRStarExample:
    n: int
    r: int
    center: int
    family: tuple[tuple[int, ...], ...]
    bound: int

    @property
    def theorem_id(self) -> str:
        return "CC-T0065"

    @property
    def is_sharp_example(self) -> bool:
        return (
            len(self.family) == self.bound
            and is_uniform_family(self.family, self.r)
            and is_intersecting_family(self.family)
        )


def ekr_star_example(n: int, r: int, *, center: int = 0) -> EKRStarExample:
    family = ekr_star_family(n, r, center=center)
    return EKRStarExample(
        n=n,
        r=r,
        center=center,
        family=family,
        bound=comb(n - 1, r - 1),
    )


def three_ap_witnesses(
    values: Iterable[int], *, limit: Optional[int] = None
) -> tuple[tuple[int, int, int], ...]:
    """Return nontrivial three-term arithmetic progressions in a finite set."""

    normalized = _unique_sorted(values)
    value_set = set(normalized)
    witnesses: list[tuple[int, int, int]] = []
    for left, right in combinations(normalized, 2):
        total = left + right
        if total % 2 != 0:
            continue
        middle = total // 2
        if left < middle < right and middle in value_set:
            witnesses.append((left, middle, right))
            if limit is not None and len(witnesses) >= limit:
                break
    return tuple(witnesses)


def is_three_ap_free(values: Iterable[int]) -> bool:
    return not three_ap_witnesses(values, limit=1)


@dataclass(frozen=True)
class RothIntervalExample:
    n: int
    values: tuple[int, ...]
    density: Fraction
    witnesses: tuple[tuple[int, int, int], ...]

    @property
    def theorem_id(self) -> str:
        return "CC-T0066"

    @property
    def has_progression(self) -> bool:
        return bool(self.witnesses)


def roth_interval_example(n: int, values: Iterable[int]) -> RothIntervalExample:
    _validate_ground_size(n)
    normalized = _validate_subset(n, values)
    return RothIntervalExample(
        n=n,
        values=normalized,
        density=Fraction(len(normalized), n),
        witnesses=three_ap_witnesses(normalized),
    )


@dataclass(frozen=True)
class MonochromaticProgression:
    progression: tuple[int, ...]
    color: Hashable

    @property
    def theorem_id(self) -> str:
        return "CC-T0069"


def find_monochromatic_arithmetic_progression(
    coloring: Mapping[int, Hashable], *, length: int = 3
) -> Optional[MonochromaticProgression]:
    if length <= 0:
        raise ValueError("progression length must be positive")
    if not coloring:
        return None

    points = tuple(sorted(coloring))
    point_set = set(points)
    largest = points[-1]
    for start in points:
        max_step = largest - start
        for step in range(1, max_step + 1):
            progression = tuple(start + step * index for index in range(length))
            if all(point in point_set for point in progression):
                colors = {coloring[point] for point in progression}
                if len(colors) == 1:
                    return MonochromaticProgression(progression, next(iter(colors)))
    return None


def all_binary_colorings_have_3ap(width: int) -> bool:
    _validate_ground_size(width)
    for colors in product((0, 1), repeat=width):
        coloring = {index: colors[index] for index in range(width)}
        if find_monochromatic_arithmetic_progression(coloring, length=3) is None:
            return False
    return True


@dataclass(frozen=True)
class HomotheticCopy:
    scale: int
    translate: int
    image: tuple[int, ...]
    color: Hashable

    @property
    def theorem_id(self) -> str:
        return "CC-T0069"


def find_monochromatic_homothetic_copy(
    shape: Sequence[int],
    coloring: Mapping[int, Hashable],
    *,
    max_scale: int,
    max_translate: Optional[int] = None,
) -> Optional[HomotheticCopy]:
    if max_scale <= 0:
        raise ValueError("max_scale must be positive")
    if not shape or not coloring:
        return None
    translate_bound = max(coloring) if max_translate is None else max_translate
    for scale in range(1, max_scale + 1):
        for translate in range(0, translate_bound + 1):
            image = tuple(scale * value + translate for value in shape)
            if all(point in coloring for point in image):
                colors = {coloring[point] for point in image}
                if len(colors) == 1:
                    return HomotheticCopy(scale, translate, image, next(iter(colors)))
    return None


@dataclass(frozen=True)
class CombinatorialLine:
    variable_positions: tuple[int, ...]
    words: tuple[tuple[Hashable, ...], ...]
    color: Hashable

    @property
    def theorem_id(self) -> str:
        return "CC-T0068"


def find_monochromatic_combinatorial_line(
    alphabet: Sequence[Hashable],
    dimension: int,
    coloring: Callable[[tuple[Hashable, ...]], Hashable],
) -> Optional[CombinatorialLine]:
    if not alphabet:
        raise ValueError("alphabet must be nonempty")
    if dimension <= 0:
        raise ValueError("dimension must be positive")

    positions = range(dimension)
    for mask_size in range(1, dimension + 1):
        for variable_positions in combinations(positions, mask_size):
            fixed_positions = tuple(pos for pos in positions if pos not in variable_positions)
            for fixed_values in product(alphabet, repeat=len(fixed_positions)):
                fixed = dict(zip(fixed_positions, fixed_values))
                words = []
                for symbol in alphabet:
                    word = tuple(
                        symbol if pos in variable_positions else fixed[pos]
                        for pos in positions
                    )
                    words.append(word)
                colors = {coloring(word) for word in words}
                if len(colors) == 1:
                    return CombinatorialLine(
                        variable_positions=variable_positions,
                        words=tuple(words),
                        color=next(iter(colors)),
                    )
    return None


Edge = tuple[int, int]


def _edge(left: int, right: int) -> Edge:
    return (left, right) if left < right else (right, left)


def cycle_graph_edges(vertices: int) -> tuple[Edge, ...]:
    _validate_ground_size(vertices)
    edges: set[Edge] = set()
    for vertex in range(vertices):
        neighbor = (vertex + 1) % vertices
        if vertex != neighbor:
            edges.add(_edge(vertex, neighbor))
    return tuple(sorted(edges))


def circulant_edges(vertices: int, jumps: Iterable[int]) -> tuple[Edge, ...]:
    _validate_ground_size(vertices)
    normalized_jumps = {jump % vertices for jump in jumps}
    edges: set[Edge] = set()
    for left, right in combinations(range(vertices), 2):
        if (left - right) % vertices in normalized_jumps or (
            right - left
        ) % vertices in normalized_jumps:
            edges.add((left, right))
    return tuple(sorted(edges))


def regular_polygon_unit_embedding(vertices: int) -> tuple[tuple[float, float], ...]:
    if vertices == 2:
        return ((0.0, 0.0), (1.0, 0.0))
    if vertices < 3:
        raise ValueError("unit cycle embedding requires at least two vertices")
    radius = 1.0 / (2.0 * sin(pi / vertices))
    return tuple(
        (
            radius * cos(2.0 * pi * vertex / vertices),
            radius * sin(2.0 * pi * vertex / vertices),
        )
        for vertex in range(vertices)
    )


def edge_length(points: Sequence[tuple[float, float]], edge: Edge) -> float:
    left, right = edge
    dx = points[left][0] - points[right][0]
    dy = points[left][1] - points[right][1]
    return sqrt(dx * dx + dy * dy)


@dataclass(frozen=True)
class CycleCirculantExample:
    vertices: int
    cycle_edges: tuple[Edge, ...]
    circulant_edges: tuple[Edge, ...]
    max_unit_distance_error: float

    @property
    def theorem_id(self) -> str:
        return "CC-T0070"

    @property
    def connected_theorem_id(self) -> str:
        return "CC-T0071"

    @property
    def unit_distance_theorem_id(self) -> str:
        return "CC-T0072"

    @property
    def matches_circulant(self) -> bool:
        return self.cycle_edges == self.circulant_edges


def cycle_circulant_example(vertices: int) -> CycleCirculantExample:
    cycle_edges_value = cycle_graph_edges(vertices)
    points = regular_polygon_unit_embedding(vertices)
    errors = [abs(edge_length(points, edge) - 1.0) for edge in cycle_edges_value]
    return CycleCirculantExample(
        vertices=vertices,
        cycle_edges=cycle_edges_value,
        circulant_edges=circulant_edges(vertices, [1]),
        max_unit_distance_error=max(errors, default=0.0),
    )
