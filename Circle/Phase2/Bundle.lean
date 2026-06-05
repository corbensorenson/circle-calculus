/-!
Phase II bundle-calculus seed.

This module formalizes only a trivial product bundle. It provides checked
base/fiber vocabulary without claiming that all bundles are globally products.
-/

namespace Circle.Phase2

structure TrivialBundle (Base Fiber : Type) where
  base : Base
  fiber : Fiber

def trivialBundleProjection {Base Fiber : Type}
    (point : TrivialBundle Base Fiber) : Base :=
  point.base

def trivialBundleFiber {Base Fiber : Type}
    (point : TrivialBundle Base Fiber) : Fiber :=
  point.fiber

def trivialBundlePoint {Base Fiber : Type}
    (base : Base) (fiber : Fiber) : TrivialBundle Base Fiber :=
  { base := base, fiber := fiber }

theorem trivialBundleProjection_point {Base Fiber : Type}
    (base : Base) (fiber : Fiber) :
    trivialBundleProjection (trivialBundlePoint base fiber) = base := by
  rfl

theorem trivialBundleFiber_point {Base Fiber : Type}
    (base : Base) (fiber : Fiber) :
    trivialBundleFiber (trivialBundlePoint base fiber) = fiber := by
  rfl

theorem trivialBundleProjection_forgetsFiber {Base Fiber : Type}
    (base : Base) (left right : Fiber) :
    trivialBundleProjection (trivialBundlePoint base left) =
      trivialBundleProjection (trivialBundlePoint base right) := by
  rfl

end Circle.Phase2
