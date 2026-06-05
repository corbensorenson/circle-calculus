# Circle Calculus S4.1: S4 as Base of Quaternionic Hopf Structure

Status: draft scaffold with the finite S4 Euler theorem proved.

## Aim

This paper establishes the finite `S^4` count model needed for the quaternionic Hopf roadmap.

## Target Spine

- `S4-T0001`: `Circle.S4.eulerCharacteristic`

## Model

The finite `S^4` count model is one suspension above the proved finite `S^3` model:

```text
Circle.S4.counts(n) =
  suspensionCounts(Circle.S3.suspendedSuspendedCircleCounts(n))
```

## Proved Core

`S4-T0001` is proved by `Circle.S4.eulerCharacteristic`.

For every natural `n`,

```text
chi(Circle.S4.counts(n)) = 2
```

## Roadmap Link

The intended later structure is:

```text
S^3 -> S^7 -> S^4
```

## Dictionary Targets

- `S4-0001`: S4 quaternionic Hopf base
- `S456-0001`: iterated suspension Euler parity

## Notes

This paper proves the finite Euler characteristic needed to keep `S^4` in the ladder. It does not yet formalize the quaternionic Hopf fibration `S^3 -> S^7 -> S^4`.
