# Circle Calculus S2.2: Sphere Grids, Latitude Rings, and Pole Collapse

Status: draft scaffold with the sphere-grid count and Euler facts proved.

## Aim

This paper will define finite sphere grids with collapsed poles and latitude rings that inherit `S^1` coil behavior.

## Target Spine

- `S2-T0003`: `Circle.S2.sphereGrid_counts`
- `S2-T0004`: `Circle.S2.sphereGrid_chi`
- `S2-T0005`: `Circle.S2.latitudeRing_isCircle`
- `S2-T0006`: `Circle.S2.longitudeRotation_fixesPoles`
- `S2-T0007`: `Circle.S2.latitudeCoil_period`
- `S2-W0001`: torus confusion warning
- `S2-W0002`: pole singularity warning
- `S2-W0003`: S2 group fallacy warning

## Model

For `n >= 3` and `r >= 1`, the planned model is:

```text
SphereGrid(n,r) = {N,S} union {(j,i) | 1 <= j <= r, i in C_n}
V = nr + 2
E = n(2r + 1)
F = n(r + 1)
chi = 2
```

The Lean count theorem uses the equivalent decomposed edge count `nr + n(r+1)` so the Euler proof stays linear:

```text
E = nr + n(r+1)
```

## Proved Core

`S2-T0003` is proved by `Circle.S2.sphereGrid_counts`.

For every natural `n` and `r`, the finite sphere-grid count list is

```text
[nr + 2, nr + n(r + 1), n(r + 1)]
```

The intended geometric use remains `n >= 3` and `r >= 1`, but the arithmetic cell-count identity is valid for all natural `n` and `r`.

`S2-T0004` is proved by `Circle.S2.sphereGrid_chi`: applying `Circle.Common.eulerCharacteristic` to those counts gives `2`.

The latitude-ring and pole-collapse behavior remains planned under `S2-T0005`, `S2-T0006`, and `S2-T0007`.

## Dictionary Targets

- `S2-0002`: sphere grid
- `S2-0003`: latitude ring
- `S2-0004`: pole collapse
- `S2-W0001`, `S2-W0002`, `S2-W0003`

## Notes

This paper must not model `S^2` as `C_n x C_m`.
