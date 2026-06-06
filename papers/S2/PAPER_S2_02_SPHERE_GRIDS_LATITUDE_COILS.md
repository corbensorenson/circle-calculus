# Circle Calculus S2.2: Sphere Grids, Latitude Rings, and Pole Collapse

Status: polished draft with the sphere-grid theorem spine Lean-proved.

## Aim

This paper gives `S^2` a finite grid model without confusing it with a torus. The construction uses collapsed poles and latitude rings. Each non-pole latitude ring inherits the already-proved `S^1` circle behavior, while the north and south poles remain special points.

The result is a controlled combinatorial sphere model:

```text
SphereGrid(n,r) = {N,S} union {(j,i) | 1 <= j <= r, i in C_n}
```

The warnings matter as much as the formulas: `C_n x C_m` is torus-like, pole collapse creates singular chart behavior, and `S^2` is not treated as a group.

## Theorem Spine

- `S2-T0003`: `Circle.S2.sphereGrid_counts`
- `S2-T0004`: `Circle.S2.sphereGrid_chi`
- `S2-T0005`: `Circle.S2.latitudeRing_isCircle`
- `S2-T0006`: `Circle.S2.longitudeRotation_fixesPoles`
- `S2-T0007`: `Circle.S2.latitudeCoil_period`
- `S2-T0017`: `Circle.S2.latitudeRingOrbitClassCount_eq_gcd`
- `S2-W0001`: torus confusion warning
- `S2-W0002`: pole singularity warning
- `S2-W0003`: S2 group fallacy warning

## Model

For the intended geometric range `n >= 3` and `r >= 1`, the cell counts are:

```text
V = nr + 2
E = nr + n(r + 1)
F = n(r + 1)
chi = 2
```

The edge formula is equivalent to `n(2r + 1)`, but the decomposed form keeps the Euler proof linear and transparent.

## Proved Core

`S2-T0003` proves the count list:

```text
[nr + 2, nr + n(r + 1), n(r + 1)]
```

for all natural `n` and `r`. `S2-T0004` proves that the Euler characteristic of this count model is `2`.

`S2-T0005` proves that every non-pole latitude ring is modeled as `Circle.C n`. `S2-T0006` proves that longitude rotation fixes the collapsed north and south poles. `S2-T0007` proves that a latitude ring inherits the existing `S^1` period theorem:

```text
period(n,k) = n / gcd(n,k)
```

`S2-T0017` proves the matching orbit-class count inherited by each finite latitude ring:

```text
orbit_class_count(n,k) = gcd(n,k)
```

The theorem is deliberately ring-local. It does not count orbits of the whole sphere grid and it does not give `S^2` a global circle-group structure.

The Python sidecar checks the same counts, Euler characteristic, pole-fixing longitude rotations, latitude preservation on ring points, inherited period formula, and inherited orbit-class count on finite examples.

## Role In The Ladder

This paper is the bridge from one-dimensional circle behavior to a surface model. It lets later `S^3` suspension papers refer to finite surface counts, and it gives the Living Book a natural S2 placeholder: latitude circles are familiar, but poles and surface structure require extra guardrails.

## Dictionary Targets

- `S2-0002`: sphere grid
- `S2-0003`: latitude ring
- `S2-0004`: pole collapse
- `S2-W0001`, `S2-W0002`, `S2-W0003`

## Guardrails

This paper does not model `S^2` as `C_n x C_m`, does not claim a global group law on `S^2`, and does not turn finite grid examples into continuous differential geometry. It proves the finite grid count, Euler, latitude-ring, pole-fixing, inherited-period, and inherited orbit-count spine.
