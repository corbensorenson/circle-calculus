from dataclasses import dataclass
from typing import TypeVar


Base = TypeVar("Base")
Fiber = TypeVar("Fiber")


@dataclass(frozen=True)
class TrivialBundlePoint:
    base: Base
    fiber: Fiber


def trivial_bundle_projection(point: TrivialBundlePoint) -> object:
    return point.base


def trivial_bundle_fiber(point: TrivialBundlePoint) -> object:
    return point.fiber


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
