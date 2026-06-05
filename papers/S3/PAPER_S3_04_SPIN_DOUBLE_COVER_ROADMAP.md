# Circle Calculus S3.4: Spin, Double Covers, and Rotation Quotients

Status: polished draft with the first spin action and sign-cancellation theorems Lean-proved.

## Aim

This paper records the first formal step from unit-quaternion algebra toward the spin and rotation story. The target geometric slogan is familiar: unit quaternions describe 3D rotations with the sign ambiguity `q` and `-q`. Circle Calculus does not use that slogan as a proof. It first proves the algebraic invariance that the slogan depends on.

The immediate object is the quaternion conjugation action:

```text
Circle.S3.quaternionConjugationAction q v = q * v * star q
```

For a unit quaternion, `star q` is the inverse supplied by the earlier quaternion paper. That makes this expression the algebraic shape behind quaternion rotation, while still avoiding an unproved global model of `SO(3)`.

## Theorem Spine

- `S3S-T0001`: `Circle.S3.quaternionConjugation_neg`
- `S3S-T0002`: `Circle.S3.quaternionConjugation_one`
- `S3S-T0003`: `Circle.S3.quaternionConjugation_zero_vector`

## Proved Core

`S3S-T0002` proves the identity case:

```text
quaternionConjugationAction 1 v = v
```

for every real quaternion input `v`. This anchors the action at the neutral representative.

`S3S-T0003` proves zero preservation:

```text
quaternionConjugationAction q 0 = 0
```

for every real quaternion `q`. This is a small but useful sanity condition for any future vector-action interpretation.

`S3S-T0001` proves the sign-cancellation law:

```text
quaternionConjugationAction (-q) v =
quaternionConjugationAction q v
```

for every real quaternion `q` and input `v`. The proof is purely algebraic. It uses the multiplication and conjugation laws already formalized in the `S^3` quaternion spine and shows that the two negative signs introduced by `-q` cancel inside the conjugation action.

Together, these facts provide the checked algebraic shadow of the spin double-cover story: identity acts as identity, zero remains zero, and changing a quaternion representative by sign does not change the action. The Python sidecar mirrors these examples for identity action, zero preservation, and sign cancellation.

## Role In The Ladder

This paper connects three layers of the project:

- `S1`: sign, orientation, and reversible motion;
- `S3`: associative quaternion multiplication and unit-quaternion closure;
- future rotation geometry: quotienting the unit-quaternion action by the sign ambiguity.

It is deliberately placed after `PAPER_S3_02_QUATERNION_COILS.md` and `PAPER_S3_03_HOPF_COILS.md`: the multiplication and phase-action facts must exist before the rotation quotient can be stated honestly.

## Dictionary Targets

- `S3S-0001`: quaternion conjugation action
- `S3S-0002`: quaternion sign ambiguity

## Guardrails

The proved claim is not yet a full formalization of `Spin(3)`, `SO(3)`, pure imaginary vectors, rotation matrices, or the quotient map from unit quaternions to rotations. Those belong in a later paper once the project has a precise formal model of 3D vector space and rotation equivalence. The safe current claim is exactly the algebraic conjugation-action spine and its sign invariance.
