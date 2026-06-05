# Circle Calculus S0.1: Two-Point Opposition

Status: draft scaffold with the two finite opposition facts proved.

## Aim

This paper separates the two-point sphere `S^0` from the one-node circle `C_1`.

## Target Spine

- `S0-T0001`: `Circle.S0.card_sign`
- `S0-T0002`: `Circle.S0.antipode_involutive`
- `S0-W0001`: `C_1` is not `S^0`

## Proved Core

`S0-T0001` is proved by `Circle.S0.card_sign`: the finite `S^0` sign model has exactly two points.

`S0-T0002` is proved by `Circle.S0.antipode_involutive`: applying the antipode twice returns the original sign.

The Lean model is deliberately small:

```text
Sign = neg | pos
antipode(neg) = pos
antipode(pos) = neg
```

This is not the one-node circle `C_1`. The warning `S0-W0001` remains part of the paper because confusing those objects would break later dimensional notation.

## Dictionary Targets

- `S0-0001`: two-point opposition
- `S0-0002`: S0 antipode
- `S0-W0001`: C1 is not S0 warning

## Notes

This paper should be written before higher-dimensional notation starts using `S^0` heavily. It is a backfill paper and should not disturb the active `S^1` finite-circle core.
