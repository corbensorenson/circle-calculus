# Circle Calculus Phase II.4: Boundary and Cobordism Calculus

Status: draft with a proved directed-interval boundary seed.

## Aim

Develop boundary operators, `boundary(boundary)=0`, cobordisms, field-adjacent structures, and proofs as transformations between boundaries.

The current formal seed is deliberately small: `COMMON-0010`, a directed interval with integer endpoints.

## Current Model

```text
interval = [source -> target]
intervalBoundary(interval) = target - source
pointBoundary(any zero-dimensional boundary chain) = 0
reverse(interval) = [target -> source]
```

`COMMON-0011` names this boundary-operator seed, and `COMMON-0012` names interval orientation reversal.

## Theorem Spine

- `P2BC-T0001`: point-boundary after interval-boundary is zero. Lean declaration: `Circle.Phase2.boundaryBoundaryInterval_zero`.
- `P2BC-T0002`: reversing a directed interval negates its boundary. Lean declaration: `Circle.Phase2.intervalBoundary_reverse`.
- `P2BC-T0003`: reversing a directed interval twice returns the original interval. Lean declaration: `Circle.Phase2.reverseInterval_involutive`.
- `P2BC-T0004`: a constant directed interval has zero boundary. Lean declaration: `Circle.Phase2.intervalBoundary_constant_zero`.

These are Lean-proved finite interval facts. They support the boundary-calculus vocabulary, but they do not prove a general chain-complex theorem, a cobordism theorem, TQFT structure, or a physics boundary law.

## Next Program

- Start with finite combinatorial boundary models where Lean support is lightweight.
- Keep TQFT and physics-adjacent language as roadmap material until formalized.
- Use manifests to distinguish definitions, examples, and proved laws.

## Guardrail

No physics or cobordism theorem is promoted from analogy to proof without a checked formal statement.
