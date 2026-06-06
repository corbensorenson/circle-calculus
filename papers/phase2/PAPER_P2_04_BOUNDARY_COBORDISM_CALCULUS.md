# Circle Calculus Phase II.4: Boundary and Cobordism Calculus

Status: polished draft with a proved directed-interval boundary seed.

## Aim

This paper starts the boundary side of Phase II. The long-term program includes boundary operators, the law `boundary(boundary)=0`, cobordisms, field-adjacent structures, and proofs as transformations between boundary states. The current paper proves only the smallest directed-interval seed.

That seed is useful because it gives the project a checked orientation-and-boundary vocabulary before it uses more ambitious cobordism or physics-adjacent language.

## Current Model

The formal seed is `COMMON-0010`, a directed interval with integer endpoints:

```text
interval = [source -> target]
intervalBoundary(interval) = target - source
pointBoundary(any zero-dimensional boundary chain) = 0
reverse(interval) = [target -> source]
```

`COMMON-0011` names the boundary operator, and `COMMON-0012` names interval orientation reversal.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS/lean/PaperP204.lean
```

The Python examples are:

```text
sidecars/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS/python/test_boundary_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks directed-boundary examples; Lean declarations determine proof status.

## Theorem Spine

- `P2BC-T0001`: `Circle.Phase2.boundaryBoundaryInterval_zero`
- `P2BC-T0002`: `Circle.Phase2.intervalBoundary_reverse`
- `P2BC-T0003`: `Circle.Phase2.reverseInterval_involutive`
- `P2BC-T0004`: `Circle.Phase2.intervalBoundary_constant_zero`
- `P2BC-T0005`: `Circle.Phase2.intervalBoundary_between_add`

## Proved Core

`P2BC-T0001` proves the first boundary-after-boundary seed: after taking the interval boundary, the point-boundary layer is zero. This is not yet a general chain-complex theorem, but it is the checked finite interval case.

`P2BC-T0002` proves that reversing a directed interval negates its boundary:

```text
intervalBoundary(reverse interval) = - intervalBoundary interval
```

`P2BC-T0003` proves that reversal is involutive, and `P2BC-T0004` proves that a constant interval has zero boundary.

`P2BC-T0005` proves the first adjacent-interval additivity law:

```text
boundary([source -> target])
  = boundary([source -> mid]) + boundary([mid -> target])
```

This is still a directed-interval theorem, not a general chain-complex theorem. Its role is to certify the arithmetic spine needed before finite chains or cobordism-style composition are introduced.

The Python sidecar checks the same directed-interval examples. It provides executable orientation, while Lean supplies the proof status.

## Next Program

- Generalize adjacent-interval additivity to finite chains only after selecting a representation.
- Keep TQFT, field, and physics-adjacent language as roadmap material until formalized.
- Use manifests to distinguish definitions, examples, planned claims, and proved laws.
- Link this boundary seed to proof-as-transformation papers only through explicit theorem ids.

## Guardrail

No general cobordism, chain-complex, TQFT, or physics theorem is promoted from analogy to proof without a checked formal statement.
