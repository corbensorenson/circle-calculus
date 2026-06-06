# Circle Calculus S2.1: Suspended Circles and the First Finite Sphere

Status: polished draft with the suspended-circle count and Euler facts Lean-proved and Python examples linked.

## Aim

This paper defines the first finite combinatorial `S^2` model by suspending a finite circle.

The goal is not to formalize all continuous sphere geometry. The goal is to introduce a checked finite cell-count model whose Euler characteristic behaves like a sphere surface and whose construction can feed later sphere-grid, antipode, and suspension papers.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S2_01_SUSPENDED_CIRCLES/lean/PaperS201.lean
```

The Python examples are:

```text
sidecars/PAPER_S2_01_SUSPENDED_CIRCLES/python/test_suspended_circle_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. Python examples are executable support; Lean declarations determine proof status.

## Model

Start with a finite circle `C_n`. The suspended-circle model adds two poles and cones the circle from both sides.

For intended geometric use, take `n >= 3`:

```text
SuspC(n)
V = n + 2
E = 3n
F = 2n
chi = 2
```

The two new vertices are the north and south poles. The old circle contributes the equatorial cycle. Each old edge contributes two triangular faces, one to each pole.

The Lean count identity is arithmetic and is valid for all natural `n`; the geometric reading remains `n >= 3`.

## Theorem Spine

- `S2-T0001`: `Circle.S2.suspendedCircle_counts`
- `S2-T0002`: `Circle.S2.suspendedCircle_chi`

## Proved Core

`S2-T0001` is proved by `Circle.S2.suspendedCircle_counts`.

For every finite circle size `n`, the suspended-circle cell-count list is:

```text
[n + 2, 3n, 2n]
```

`S2-T0002` is proved by `Circle.S2.suspendedCircle_chi`: applying `Circle.Common.eulerCharacteristic` to those counts gives `2`.

The Python sidecar checks the same finite count formula and Euler characteristic on ordinary integer examples. It is executable support for the paper, not a replacement for the Lean theorem spine.

## Euler Calculation

The finite Euler characteristic is the alternating sum:

```text
chi = V - E + F
```

For `SuspC(n)`:

```text
chi = (n + 2) - 3n + 2n
    = 2
```

This calculation is the first checked surface-closure invariant in the project. It does not prove homeomorphism to a smooth sphere, but it gives the finite sphere ladder a disciplined count model.

## Relation To S1

The equator of `SuspC(n)` is still the finite circle core from `S1.1`. The two poles are not ordinary circle nodes and do not carry independent longitudes.

This distinction prepares the next paper:

```text
S2.2: SphereGrid(n,r)
```

Sphere grids add latitude rings while preserving pole collapse. Each non-pole latitude ring inherits `C_n` behavior, but the poles remain collapsed endpoints.

## Dictionary Targets

- `S2-0001`: suspended finite circle
- `COMMON-0001`: finite cell-count list
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform

## Guardrails

This paper is finite and combinatorial first.

It does not claim:

- a smooth round sphere,
- a metric geometry,
- a natural group structure on `S^2`,
- a product model `C_n x C_m`,
- or a proof by picture.

Continuous sphere geometry can be added only after the finite proof spine is stable and the needed formal model is explicit.

## Next Step

The next `S^2` paper refines this first suspended-circle model into sphere grids with latitude rings, pole collapse, inherited circle periods, and warnings against torus-like product confusion.
