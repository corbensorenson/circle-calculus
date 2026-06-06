# Circle Calculus Phase II.3: Bundle Calculus

Status: polished draft with a proved trivial product-bundle and base-preserving transition seed.

## Aim

This paper begins a proof-carrying language for base space, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance. The long-term target is a dictionary where visible base state and hidden fiber state can be tracked explicitly across Hopf-like, gauge-like, and proof-interface examples.

The current formal seed is deliberately small: `COMMON-0007`, a trivial product bundle with a visible base coordinate and a hidden fiber coordinate. This is a vocabulary seed, not a claim that all bundles are products.

The Phase IV audit adds a bounded transition layer. A `BundleTransition` is a fiber map applied over the same visible base coordinate. It is a transition sanity seed, not a nontrivial atlas or cocycle model.

## Current Model

```text
TrivialBundle(Base,Fiber)
  point(base,fiber)
  projection(point) = base
  fiber(point) = fiber
```

`COMMON-0008` names the projection operation. `COMMON-0009` names the fiber-coordinate operation.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_P2_03_BUNDLE_CALCULUS/lean/PaperP203.lean
```

The Python examples are:

```text
sidecars/PAPER_P2_03_BUNDLE_CALCULUS/python/test_trivial_bundle_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks finite bundle examples; Lean declarations determine proof status.

## Theorem Spine

- `P2BU-T0001`: `Circle.Phase2.trivialBundleProjection_point`
- `P2BU-T0002`: `Circle.Phase2.trivialBundleFiber_point`
- `P2BU-T0003`: `Circle.Phase2.trivialBundleProjection_forgetsFiber`
- `P2BU-T0004`: `Circle.Phase2.trivialBundleFiber_forgetsBase`
- `P2BU-T0005`: `Circle.Phase2.bundleTransitionProjection_apply`
- `P2BU-T0006`: `Circle.Phase2.bundleTransitionFiber_apply`
- `P2BU-T0007`: `Circle.Phase2.bundleTransitionApply_compose`
- `P2BU-T0008`: `Circle.Phase2.bundleTransitionApply_identity`
- `P2BU-T0009`: `Circle.Phase2.bundleTransitionApply_compose_identity`

## Proved Core

`P2BU-T0001` proves that projecting a constructed product-bundle point returns its base coordinate. `P2BU-T0002` proves the dual fiber-coordinate statement.

The two forgetfulness theorems are the important conceptual seed. `P2BU-T0003` proves that changing only the fiber value does not change the visible base projection. `P2BU-T0004` proves that changing only the base value does not change the hidden fiber coordinate.

This pair of laws gives Circle Calculus a precise way to say "visible base" and "hidden fiber" without using those words as metaphor only. The Python sidecar checks the same base/fiber projection examples.

`P2BU-T0005` proves that applying a base-preserving transition does not change the projected base coordinate. `P2BU-T0006` proves that the transition acts on the fiber coordinate by its fiber map. `P2BU-T0007` proves that transition composition agrees with applying the inner transition and then the outer transition. `P2BU-T0008` proves that the identity transition leaves every trivial-bundle point unchanged.

`P2BU-T0009` proves the identity-composition sanity law for transition action on points: composing any transition with the identity transition on either side acts the same as the original transition. This is still a trivial-bundle transition law, not a cocycle or atlas theorem.

These transition facts are deliberately local to the trivial product-bundle seed. They are the sanity laws future nontrivial transition functions must satisfy before the project talks about overlaps, cocycles, connections, curvature, or holonomy.

## Relation To Hopf And Glyphs

The `S^3`, `S^7`, and future `S^15` Hopf papers motivate this vocabulary: a visible base point can have phase or fiber data that is not visible in the projection. Proof-carrying glyphs will need the same separation between a rendered view and hidden theorem/proof metadata.

## Next Program

- Extend transition functions beyond composition/identity sanity laws only after choosing a nontrivial bundle representation and explicit overlap data.
- Use Hopf-coordinate papers as motivating examples, not as completed bundle formalizations.
- Track visible base state and hidden phase/fiber state separately.
- Add theorem ids only for precise bundle definitions and checked maps.

## Guardrail

Do not collapse twisted or nontrivial fiber structures into global products. This paper proves trivial product-bundle projection facts and base-preserving transition sanity laws only.
