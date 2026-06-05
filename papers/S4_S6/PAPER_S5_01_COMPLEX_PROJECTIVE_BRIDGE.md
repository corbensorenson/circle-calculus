# Circle Calculus S5.1: Complex Projective Bridge

Status: draft with the finite `S^5` suspension and Euler theorem spine Lean-proved.

## Aim

This paper keeps `S^5` visible in the geometric ladder and records its future role near projective and bundle structures.

The current contribution is deliberately modest: a finite `S^5` count model and its Euler characteristic. The paper does not formalize complex projective geometry yet.

## Model

The finite `S^5` count model is one suspension above the finite `S^4` model:

```text
Circle.S5.counts(n) =
  suspensionCounts(Circle.S4.counts(n))
```

Since `S^4` has finite Euler characteristic `2`, one more suspension gives:

```text
chi(S5) = 2 - chi(S4) = 0
```

This is the expected parity for an odd-dimensional sphere in the finite-count model.

## Target Spine

- `S5-T0001`: `Circle.S5.eulerCharacteristic`
- `S5-T0002`: `Circle.S5.counts_eq_suspension_s4`

## Proved Core

`S5-T0002` proves that the finite `S^5` counts are exactly the suspension of the finite `S^4` counts.

`S5-T0001` is then proved by `Circle.S5.eulerCharacteristic`:

```text
chi(Circle.S5.counts(n)) = 0
```

for every natural `n`.

The Python sidecar checks the same suspension-from-`S^4` count definition and Euler characteristic examples.

## Why S5 Is Kept Explicit

`S^5` can look like a pass-through dimension if the project focuses only on normed-division-algebra spheres. That would be a mistake for a dimension-organized corpus.

The `S^5` layer matters because:

- it preserves the continuous geometric ladder from `S^4` to `S^6`,
- it records the odd-sphere Euler parity between two even-sphere anchors,
- it leaves room for future projective and bundle papers,
- and it prevents the roadmap from treating only algebraically exceptional dimensions as important.

The paper title says "complex projective bridge" because later work may connect this region of the ladder to projective structures. The current formal claim is only the finite suspension/Euler seed.

## Dictionary Targets

- `S5-0001`: S5 complex projective bridge
- `S456-0001`: iterated suspension Euler parity

## Guardrails

Keep projective geometry exploratory until the formal infrastructure is selected.

This paper does not prove:

- complex projective space facts,
- bundle classifications,
- a Hopf fibration,
- characteristic classes,
- or any smooth geometric theorem.

The safe proved statement is finite and exact: `S^5` is modeled as the suspension of the finite `S^4` count model, and its Euler characteristic is `0`.
