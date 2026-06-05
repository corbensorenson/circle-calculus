# Circle Calculus S4.1: S4 as Base of Quaternionic Hopf Structure

Status: polished draft with the finite `S^4` suspension and Euler theorem spine Lean-proved.

## Aim

This paper establishes the finite `S^4` count model needed for the quaternionic Hopf roadmap.

The eventual classical shape is:

```text
S^3 -> S^7 -> S^4
```

This paper does not prove that fibration. It proves the finite `S^4` suspension-count anchor that lets the roadmap refer to `S^4` without skipping over it.

## Model

The finite `S^4` count model is one suspension above the proved finite `S^3` model:

```text
Circle.S4.counts(n) =
  suspensionCounts(Circle.S3.suspendedSuspendedCircleCounts(n))
```

The input `Circle.S3.suspendedSuspendedCircleCounts(n)` is the finite `S^3` model already proved in the `S3.1` paper. Applying the common suspension transform produces a finite count model for the next even-dimensional sphere.

## Target Spine

- `S4-T0001`: `Circle.S4.eulerCharacteristic`
- `S4-T0002`: `Circle.S4.counts_eq_suspension_s3`

## Proved Core

`S4-T0002` proves that the finite `S^4` counts are exactly the suspension of the finite `S^3` counts.

`S4-T0001` is then proved by `Circle.S4.eulerCharacteristic`:

```text
chi(Circle.S4.counts(n)) = 2
```

for every natural `n`.

The Python sidecar checks the same suspension-from-`S^3` count definition and Euler characteristic examples.

## Role In The Ladder

`S^4` is not algebraically special in the same way as `S^1`, `S^3`, or `S^7`, but it is geometrically central. It is the base dimension in the quaternionic Hopf story, and it is the next even sphere after the finite `S^3` suspension model.

Keeping `S^4` explicit helps the repository avoid a misleading algebra-only ladder:

```text
S^1 -> S^3 -> S^7
```

The geometric ladder instead keeps:

```text
S^1 -> S^2 -> S^3 -> S^4 -> S^5 -> S^6 -> S^7
```

## Roadmap Link

The intended later structure is:

```text
S^3 -> S^7 -> S^4
```

The current proved result is only the finite `S^4` count and Euler anchor. Quaternionic projective space, quotient topology, and the full Hopf fibration remain future formalization work.

## Dictionary Targets

- `S4-0001`: S4 quaternionic Hopf base
- `S456-0001`: iterated suspension Euler parity

## Guardrails

This paper proves finite suspension bookkeeping. It does not prove `HP^1`, smooth `S^4`, a quotient construction, or the quaternionic Hopf fibration.

The safe claim is: the project now has a checked finite `S^4` count model with Euler characteristic `2`, linked to the suspension ladder and ready for later bundle/fibration work.
