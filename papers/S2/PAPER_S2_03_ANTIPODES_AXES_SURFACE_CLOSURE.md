# Circle Calculus S2.3: Antipodes, Axes, Surface Closure, and Antinodes

Status: draft scaffold with the finite suspended-circle antipode theorem spine proved.

## Aim

This `S^2` paper adds the first conservative antipode and axis structure after the finite sphere-grid foundation.

## Target Spine

- `S2-T0008`: `Circle.S2.suspendedCircleAntipode_swapsPoles`
- `S2-T0009`: `Circle.S2.suspendedCircleAntipode_involutive`

## Model

The finite point model for the suspended circle has two poles and an equator:

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

This is a conservative finite model. It does not claim the full continuous antipodal map on every sphere construction.

## Proved Core

`S2-T0008` is proved by `Circle.S2.suspendedCircleAntipode_swapsPoles`: the antipode swaps the two poles.

`S2-T0009` is proved by `Circle.S2.suspendedCircleAntipode_involutive`: applying the antipode twice returns the original suspended-circle point.

Surface closure remains tied to the already proved Euler facts `Circle.S2.suspendedCircle_chi` and `Circle.S2.sphereGrid_chi`.

## Dictionary Targets

- `S2-0005`: suspended-circle antipode
- `S2-0006`: pole axis

## Notes

Do not force continuous geometry too early. Antinodes, meridian systems, and continuous surface geometry remain future refinements after the finite antipode spine is stable.
