# Circle Calculus S2.3: Antipodes, Axes, Surface Closure, and Antinodes

Status: draft scaffold with the finite suspended-circle antipode theorem spine proved.

## Aim

This `S^2` paper adds the first conservative antipode and axis structure after the finite sphere-grid foundation.

## Target Spine

- `S2-T0008`: `Circle.S2.suspendedCircleAntipode_swapsPoles`
- `S2-T0009`: `Circle.S2.suspendedCircleAntipode_involutive`
- `S2-T0010`: `Circle.S2.suspendedCircleAntipode_preservesPoleSet`
- `S2-T0011`: `Circle.S2.suspendedCircleAntipode_preservesEquatorSet`

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

The finite pole and equator predicates are:

```text
is_suspended_pole(north)=true
is_suspended_pole(south)=true
is_suspended_pole(equator(x))=false

is_suspended_equator(north)=false
is_suspended_equator(south)=false
is_suspended_equator(equator(x))=true
```

## Proved Core

`S2-T0008` is proved by `Circle.S2.suspendedCircleAntipode_swapsPoles`: the antipode swaps the two poles.

`S2-T0009` is proved by `Circle.S2.suspendedCircleAntipode_involutive`: applying the antipode twice returns the original suspended-circle point.

`S2-T0010` is proved by `Circle.S2.suspendedCircleAntipode_preservesPoleSet`: the antipode preserves the finite pole subset, even though it swaps the individual north and south poles.

`S2-T0011` is proved by `Circle.S2.suspendedCircleAntipode_preservesEquatorSet`: the antipode sends equator points to equator points.

Surface closure remains tied to the already proved Euler facts `Circle.S2.suspendedCircle_chi` and `Circle.S2.sphereGrid_chi`.

## Dictionary Targets

- `S2-0005`: suspended-circle antipode
- `S2-0006`: pole axis / finite pole subset

## Notes

Do not force continuous geometry too early. Antinodes, meridian systems, and continuous surface geometry remain future refinements after the finite antipode, pole-subset, and equator-subset spine is stable.
