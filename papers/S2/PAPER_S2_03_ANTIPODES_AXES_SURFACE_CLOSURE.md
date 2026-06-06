# Circle Calculus S2.3: Antipodes, Axes, Surface Closure, and Antinodes

Status: polished draft with the finite suspended-circle antipode and sphere-grid coordinate theorem spine Lean-proved.

## Aim

This paper adds conservative antipode, pole-axis, equator, and coordinate-rotation structure to the finite `S^2` layer. It extends the suspended-circle and sphere-grid models without pretending that the full continuous antipodal map, smooth axes, or surface geometry have been formalized.

The guiding rule is the same as the rest of the `S^2` track: prove finite structure first, keep continuous geometry future.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE/lean/PaperS203.lean
```

The Python examples are:

```text
sidecars/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE/python/test_s2_antipode_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks finite examples; Lean declarations determine proof status.

## Theorem Spine

- `S2-T0008`: `Circle.S2.suspendedCircleAntipode_swapsPoles`
- `S2-T0009`: `Circle.S2.suspendedCircleAntipode_involutive`
- `S2-T0010`: `Circle.S2.suspendedCircleAntipode_preservesPoleSet`
- `S2-T0011`: `Circle.S2.suspendedCircleAntipode_preservesEquatorSet`
- `S2-T0012`: `Circle.S2.longitudeRotation_preservesLatitudeCoordinate`
- `S2-T0013`: `Circle.S2.longitudeRotation_advancesLongitudeCoordinate`
- `S2-T0014`: `Circle.S2.suspendedCircleAntipodalPair_self_antipode`
- `S2-T0015`: `Circle.S2.suspendedCircleAntipodalPair_symmetric`
- `S2-T0016`: `Circle.S2.suspendedCircleAntipode_longitudeRotation_opposite`
- `S2-T0018`: `Circle.S2.suspendedCircleAntipode_bijective`
- `S2-T0019`: `Circle.S2.suspendedCircleLongitudeRotation_bijective`

## Model

The finite suspended-circle point model has two poles and an equator:

```text
SuspendedCirclePoint(n) =
  north
  south
  equator(node in C_n)
```

The finite antipode operation is:

```text
north      -> south
south      -> north
equator(x) -> equator(-x)
```

The finite suspended-circle longitude rotation leaves the poles fixed and rotates only equator nodes:

```text
rot_k(north)      = north
rot_k(south)      = south
rot_k(equator(x)) = equator(x+k)
```

Pole and equator predicates distinguish the collapsed poles from the circular equator. In the sphere-grid model, non-pole points also have partial coordinate projections:

```text
latitude_coordinate(pole)=none
longitude_coordinate(pole)=none
latitude_coordinate(ring(latitude,node))=some(latitude)
longitude_coordinate(ring(latitude,node))=some(node)
```

## Proved Core

`S2-T0008` proves that the suspended-circle antipode swaps north and south. `S2-T0009` proves the antipode is involutive. `S2-T0018` proves the same finite antipode is a bijection of suspended-circle points. `S2-T0019` proves every signed suspended longitude rotation is also a bijection: it fixes the two poles and uses the already-proved signed `S^1` rotation bijection on equator coordinates. `S2-T0010` proves the antipode preserves the finite pole subset, and `S2-T0011` proves it preserves the equator subset.

`S2-T0012` proves that longitude rotation preserves latitude coordinates. `S2-T0013` proves that longitude rotation advances a ring point's longitude coordinate by `Circle.rot(n,stride)` while keeping pole longitudes empty.

`S2-T0014` proves every point forms an antipodal pair with its antipode, and `S2-T0015` proves the finite antipodal-pair relation is symmetric.

`S2-T0016` proves the equator-compatible antipode/longitude law: antipoding after a signed longitude rotation by `k` equals rotating by `-k` after antipoding. On poles this is the fixed-pole rule; on equator coordinates it is the finite-circle identity `-(x+k)=(-x)+(-k)`.

Surface closure remains tied to the already-proved Euler facts for suspended circles and sphere grids. The Python sidecar checks the same finite antipode, antipode bijection, suspended longitude-rotation bijection, pole/equator predicate, suspended longitude/opposite-stride law, longitude-coordinate, latitude-coordinate, and antipodal-pair examples.

## Role In The Ladder

This paper makes `S^2` more than a cell-count example. It gives later Hopf and sphere-grid explanations finite language for poles, equators, latitude/longitude coordinates, and antipodal pairing.

## Dictionary Targets

- `S2-0005`: suspended-circle antipode
- `S2-0006`: pole axis / finite pole subset

## Guardrails

Continuous surface geometry, smooth antinodes, metric axes, and full analytic antipodal maps remain future work. The current proved content is the finite antipode, its finite bijection property, finite signed suspended longitude-rotation bijection, pole/equator preservation, suspended longitude/opposite-stride law, coordinate-rotation, and antipodal-pair spine.
