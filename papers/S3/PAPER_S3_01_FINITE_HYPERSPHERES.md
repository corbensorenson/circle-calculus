# Circle Calculus S3.1: Finite 3-Spheres by Suspending Spheres

Status: polished draft with the finite suspended-surface theorem spine Lean-proved.

## Aim

This paper constructs finite combinatorial `S^3` models by suspending finite `S^2`-like surface count models. It is the topological/combinatorial `S^3` layer, separate from the quaternion algebra introduced in the next paper.

The key idea is that suspension adds two poles and raises dimension by one. For a finite surface count list

```text
[V, E, F]
```

the suspension count transform produces:

```text
[V + 2, E + 2V, F + 2E, 2F]
```

The two new vertices are suspension poles. Every old vertex contributes two new edges, every old edge contributes two new faces, and every old face contributes two new 3-cells.

## Theorem Spine

- `S3C-T0001`: `Circle.S3.suspensionSurface_counts`
- `S3C-T0002`: `Circle.S3.suspensionSurface_chi_zero`
- `S3C-T0003`: `Circle.S3.suspendedSuspendedCircle_counts`
- `S3C-T0004`: `Circle.S3.suspendedSuspendedCircle_chi`

## Euler Behavior

If the original surface has Euler characteristic

```text
chi = V - E + F = 2
```

then its suspended finite 3-dimensional count model has Euler characteristic:

```text
(V + 2) - (E + 2V) + (F + 2E) - 2F = 0
```

This is the expected Euler characteristic for an odd-dimensional sphere model.

## Proved Core

`S3C-T0001` proves the suspension count transform for all natural `V`, `E`, and `F`. `S3C-T0002` proves that if the input surface count list has Euler characteristic `2`, then its suspension has Euler characteristic `0`.

Applying the transform to the already-proved suspended finite circle model `SuspC(n)` gives the suspended-suspended-circle model:

```text
V = n + 4
E = 5n + 4
F = 8n
T = 4n
chi = 0
```

`S3C-T0003` proves the count list `[n + 4, 5n + 4, 8n, 4n]`, and `S3C-T0004` proves its Euler characteristic is `0`.

The Python sidecar checks the same suspension count transform, chi-zero implication on sphere-like surfaces, suspended-suspended-circle counts, and Euler characteristic examples.

## Role In The Ladder

This paper lets the project talk about `S^3` before using quaternions. That separation is important: the topological suspension model and the algebraic unit-quaternion model are compatible roadmap layers, but neither should silently stand in for the other.

## Dictionary Targets

- `S3C-0001`: finite 3-sphere suspension model
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform
- `S2-0001`: suspended finite circle

## Guardrails

This paper is topological/combinatorial. Quaternion multiplication belongs in `PAPER_S3_02_QUATERNION_COILS.md`, Hopf fiber structure belongs in `PAPER_S3_03_HOPF_COILS.md`, and spin/rotation quotient claims belong in `PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md`.
