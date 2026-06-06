from dataclasses import dataclass
from typing import Callable, TypeVar


Base = TypeVar("Base")
Fiber = TypeVar("Fiber")


@dataclass(frozen=True)
class TrivialBundlePoint:
    base: Base
    fiber: Fiber


@dataclass(frozen=True)
class BundleTransition:
    map_fiber: Callable[[object], object]


def trivial_bundle_projection(point: TrivialBundlePoint) -> object:
    return point.base


def trivial_bundle_fiber(point: TrivialBundlePoint) -> object:
    return point.fiber


def bundle_transition_apply(
    transition: BundleTransition, point: TrivialBundlePoint
) -> TrivialBundlePoint:
    return TrivialBundlePoint(base=point.base, fiber=transition.map_fiber(point.fiber))


def bundle_transition_compose(
    outer: BundleTransition, inner: BundleTransition
) -> BundleTransition:
    return BundleTransition(map_fiber=lambda fiber: outer.map_fiber(inner.map_fiber(fiber)))


def test_projection_returns_base_coordinate() -> None:
    point = TrivialBundlePoint(base="visible", fiber={"phase": 3})
    assert trivial_bundle_projection(point) == "visible"


def test_fiber_returns_fiber_coordinate() -> None:
    point = TrivialBundlePoint(base="visible", fiber=("hidden", 5))
    assert trivial_bundle_fiber(point) == ("hidden", 5)


def test_projection_forgets_fiber() -> None:
    left = TrivialBundlePoint(base="same-base", fiber="left-fiber")
    right = TrivialBundlePoint(base="same-base", fiber="right-fiber")
    assert trivial_bundle_projection(left) == trivial_bundle_projection(right)


def test_fiber_forgets_base() -> None:
    left = TrivialBundlePoint(base="left-base", fiber="same-fiber")
    right = TrivialBundlePoint(base="right-base", fiber="same-fiber")
    assert trivial_bundle_fiber(left) == trivial_bundle_fiber(right)


def test_bundle_transition_preserves_projection() -> None:
    transition = BundleTransition(map_fiber=lambda fiber: f"{fiber}:moved")
    point = TrivialBundlePoint(base="same-base", fiber="phase")

    assert trivial_bundle_projection(bundle_transition_apply(transition, point)) == "same-base"


def test_bundle_transition_maps_fiber() -> None:
    transition = BundleTransition(map_fiber=lambda fiber: fiber + 3)
    point = TrivialBundlePoint(base="base", fiber=4)

    assert trivial_bundle_fiber(bundle_transition_apply(transition, point)) == 7


def test_bundle_transition_composes() -> None:
    outer = BundleTransition(map_fiber=lambda fiber: fiber * 2)
    inner = BundleTransition(map_fiber=lambda fiber: fiber + 3)
    point = TrivialBundlePoint(base="base", fiber=5)

    composed = bundle_transition_apply(bundle_transition_compose(outer, inner), point)
    sequential = bundle_transition_apply(outer, bundle_transition_apply(inner, point))
    assert composed == sequential
