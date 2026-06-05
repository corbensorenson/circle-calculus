# Circle Calculus Phase II.3: Bundle Calculus

Status: polished draft with a proved trivial product-bundle seed.

## Aim

This paper begins a proof-carrying language for base space, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance. The long-term target is a dictionary where visible base state and hidden fiber state can be tracked explicitly across Hopf-like, gauge-like, and proof-interface examples.

The current formal seed is deliberately small: `COMMON-0007`, a trivial product bundle with a visible base coordinate and a hidden fiber coordinate. This is a vocabulary seed, not a claim that all bundles are products.

## Current Model

```text
TrivialBundle(Base,Fiber)
  point(base,fiber)
  projection(point) = base
  fiber(point) = fiber
```

`COMMON-0008` names the projection operation. `COMMON-0009` names the fiber-coordinate operation.

## Theorem Spine

- `P2BU-T0001`: `Circle.Phase2.trivialBundleProjection_point`
- `P2BU-T0002`: `Circle.Phase2.trivialBundleFiber_point`
- `P2BU-T0003`: `Circle.Phase2.trivialBundleProjection_forgetsFiber`
- `P2BU-T0004`: `Circle.Phase2.trivialBundleFiber_forgetsBase`

## Proved Core

`P2BU-T0001` proves that projecting a constructed product-bundle point returns its base coordinate. `P2BU-T0002` proves the dual fiber-coordinate statement.

The two forgetfulness theorems are the important conceptual seed. `P2BU-T0003` proves that changing only the fiber value does not change the visible base projection. `P2BU-T0004` proves that changing only the base value does not change the hidden fiber coordinate.

This pair of laws gives Circle Calculus a precise way to say "visible base" and "hidden fiber" without using those words as metaphor only. The Python sidecar checks the same base/fiber projection examples.

## Relation To Hopf And Glyphs

The `S^3`, `S^7`, and future `S^15` Hopf papers motivate this vocabulary: a visible base point can have phase or fiber data that is not visible in the projection. Proof-carrying glyphs will need the same separation between a rendered view and hidden theorem/proof metadata.

## Next Program

- Add transition functions only after choosing a nontrivial bundle representation.
- Use Hopf-coordinate papers as motivating examples, not as completed bundle formalizations.
- Track visible base state and hidden phase/fiber state separately.
- Add theorem ids only for precise bundle definitions and checked maps.

## Guardrail

Do not collapse twisted or nontrivial fiber structures into global products. This paper proves trivial product-bundle projection facts only.
