# Circle Calculus S2.1: Suspended Circles and the First Finite Sphere

Status: draft scaffold with the suspended-circle count and Euler facts proved.

## Aim

This paper will define the first finite combinatorial `S^2` model by suspending a finite circle.

## Target Spine

- `S2-T0001`: `Circle.S2.suspendedCircle_counts`
- `S2-T0002`: `Circle.S2.suspendedCircle_chi`

## Model

For `n >= 3`, the planned model is:

```text
SuspC(n)
V = n + 2
E = 3n
F = 2n
chi = 2
```

## Proved Core

`S2-T0001` is proved by `Circle.S2.suspendedCircle_counts`.

For every finite circle size `n`, the suspended-circle cell-count list is

```text
[n + 2, 3n, 2n]
```

The intended geometric use remains `n >= 3`, but the arithmetic cell-count identity is valid for all natural `n`.

`S2-T0002` is proved by `Circle.S2.suspendedCircle_chi`: applying `Circle.Common.eulerCharacteristic` to those counts gives `2`.

## Dictionary Targets

- `S2-0001`: suspended finite circle
- `COMMON-0001`: finite cell-count list
- `COMMON-0002`: Euler characteristic
- `COMMON-0003`: suspension cell-count transform

## Notes

This paper should be finite and combinatorial first. Continuous sphere geometry can be added only after the finite proof spine is stable.
