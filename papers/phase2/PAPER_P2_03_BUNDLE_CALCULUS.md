# Circle Calculus Phase II.3: Bundle Calculus

Status: draft with a proved trivial product-bundle seed.

## Aim

Develop a proof-carrying language for base, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance.

The current formal seed is deliberately small: `COMMON-0007`, a trivial product bundle with a visible base coordinate and a hidden fiber coordinate.

This is a vocabulary seed, not a theorem that all bundles are products.

## Current Model

```text
TrivialBundle(Base,Fiber)
  point(base,fiber)
  projection(point) = base
  fiber(point) = fiber
```

`COMMON-0008` names the projection operation, and `COMMON-0009` names the fiber-coordinate operation.

## Theorem Spine

- `P2BU-T0001`: projection of a built trivial-bundle point returns the base. Lean declaration: `Circle.Phase2.trivialBundleProjection_point`.
- `P2BU-T0002`: the fiber coordinate of a built trivial-bundle point returns the fiber value. Lean declaration: `Circle.Phase2.trivialBundleFiber_point`.
- `P2BU-T0003`: changing only the fiber value does not change the projected base. Lean declaration: `Circle.Phase2.trivialBundleProjection_forgetsFiber`.

These are Lean-proved product-bundle facts. They support base/fiber terminology for later proof-carrying glyph and Hopf-style examples, but they do not formalize nontrivial bundles, transition functions, connections, curvature, or holonomy.

## Next Program

- Use the Hopf papers as motivating examples, not as completed bundle formalizations.
- Track visible base state and hidden phase/fiber state separately.
- Add theorem ids only for precise bundle definitions and checked maps.

## Guardrail

Do not collapse twisted fiber structures into global products.
