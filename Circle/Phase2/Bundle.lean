/-!
Phase II bundle-calculus seed.

This module formalizes only a trivial product bundle. It provides checked
base/fiber vocabulary without claiming that all bundles are globally products.
-/

namespace Circle.Phase2

structure TrivialBundle (Base Fiber : Type) where
  base : Base
  fiber : Fiber

structure BundleTransition (Fiber : Type) where
  mapFiber : Fiber -> Fiber

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

theorem trivialBundleFiber_forgetsBase {Base Fiber : Type}
    (left right : Base) (fiber : Fiber) :
    trivialBundleFiber (trivialBundlePoint left fiber) =
      trivialBundleFiber (trivialBundlePoint right fiber) := by
  rfl

def bundleTransitionApply {Base Fiber : Type}
    (transition : BundleTransition Fiber)
    (point : TrivialBundle Base Fiber) : TrivialBundle Base Fiber :=
  trivialBundlePoint point.base (transition.mapFiber point.fiber)

def bundleTransitionIdentity {Fiber : Type} : BundleTransition Fiber :=
  { mapFiber := fun fiber => fiber }

def bundleTransitionCompose {Fiber : Type}
    (outer inner : BundleTransition Fiber) : BundleTransition Fiber :=
  { mapFiber := fun fiber => outer.mapFiber (inner.mapFiber fiber) }

theorem bundleTransitionProjection_apply {Base Fiber : Type}
    (transition : BundleTransition Fiber)
    (point : TrivialBundle Base Fiber) :
    trivialBundleProjection (bundleTransitionApply transition point) =
      trivialBundleProjection point := by
  rfl

theorem bundleTransitionFiber_apply {Base Fiber : Type}
    (transition : BundleTransition Fiber) (base : Base) (fiber : Fiber) :
    trivialBundleFiber (bundleTransitionApply transition (trivialBundlePoint base fiber)) =
      transition.mapFiber fiber := by
  rfl

theorem bundleTransitionApply_compose {Base Fiber : Type}
    (outer inner : BundleTransition Fiber)
    (point : TrivialBundle Base Fiber) :
    bundleTransitionApply (bundleTransitionCompose outer inner) point =
      bundleTransitionApply outer (bundleTransitionApply inner point) := by
  rfl

theorem bundleTransitionApply_identity {Base Fiber : Type}
    (point : TrivialBundle Base Fiber) :
    bundleTransitionApply bundleTransitionIdentity point = point := by
  rcases point with ⟨base, fiber⟩
  rfl

theorem bundleTransitionApply_compose_identity {Base Fiber : Type}
    (transition : BundleTransition Fiber)
    (point : TrivialBundle Base Fiber) :
    bundleTransitionApply (bundleTransitionCompose bundleTransitionIdentity transition) point =
        bundleTransitionApply transition point ∧
      bundleTransitionApply (bundleTransitionCompose transition bundleTransitionIdentity) point =
        bundleTransitionApply transition point := by
  constructor <;> rcases point with ⟨base, fiber⟩ <;> rfl

end Circle.Phase2
