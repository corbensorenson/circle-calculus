# Circle Calculus S3.1: Finite 3-Spheres by Suspending Spheres

Status: draft scaffold with the finite suspended-surface theorem spine proved.

## Aim

This paper constructs finite combinatorial `S^3` models by suspending finite 2D sphere-count models.

## Target Spine

- `S3C-T0001`: `Circle.S3.suspensionSurface_counts`
- `S3C-T0002`: `Circle.S3.suspensionSurface_chi_zero`
- `S3C-T0003`: `Circle.S3.suspendedSuspendedCircle_counts`
- `S3C-T0004`: `Circle.S3.suspendedSuspendedCircle_chi`

## Model

Given a finite surface count list

```text
[V, E, F]
```

the suspension count transform gives a finite 3-dimensional cell-count list

```text
[V + 2, E + 2V, F + 2E, 2F]
```

The two new vertices are the suspension poles. Every old vertex contributes two new edges, every old edge contributes two new faces, and every old face contributes two new 3-cells.

If the original surface has Euler characteristic

```text
chi = V - E + F = 2
```

then the suspended count model has Euler characteristic

```text
(V + 2) - (E + 2V) + (F + 2E) - 2F = 0.
```

This is the expected Euler characteristic for a finite combinatorial `S^3` model.

## Suspended Suspended Circle

Applying the transform to the already-proved suspended finite circle model `SuspC(n)` gives

```text
Susp(SuspC(n))
V = n + 4
E = 5n + 4
F = 8n
T = 4n
chi = 0
```

Here `T` denotes 3-cells.

## Proved Core

`S3C-T0001` is proved by `Circle.S3.suspensionSurface_counts`.

For every natural `V`, `E`, and `F`, the finite suspended-surface count list is

```text
[V + 2, E + 2V, F + 2E, 2F]
```

`S3C-T0002` is proved by `Circle.S3.suspensionSurface_chi_zero`: if the input surface count list has Euler characteristic `2`, then its suspension has Euler characteristic `0`.

`S3C-T0003` is proved by `Circle.S3.suspendedSuspendedCircle_counts`: suspending the `S^2` model `SuspC(n)` gives

```text
[n + 4, 5n + 4, 8n, 4n]
```

`S3C-T0004` is proved by `Circle.S3.suspendedSuspendedCircle_chi`: applying `Circle.Common.eulerCharacteristic` to those counts gives `0`.

The Python sidecar checks the same suspension count transform, chi-zero implication on sphere-like surfaces, suspended-suspended-circle counts, and Euler characteristic examples.

## Dictionary Targets

- `S3C-0001`: finite 3-sphere suspension model
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform
- `S2-0001`: suspended finite circle

## Notes

This paper is topological/combinatorial. Quaternion algebra belongs in `PAPER_S3_02_QUATERNION_COILS.md`, and Hopf fiber structure belongs in `PAPER_S3_03_HOPF_COILS.md`.
