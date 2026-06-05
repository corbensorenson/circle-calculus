# Circle Calculus S3.4: Spin, Double Covers, and Rotation Quotients

Status: draft scaffold with the first spin action and sign-cancellation theorems proved.

## Aim

This paper begins the connection from unit quaternions to 3D rotations and the double-cover relationship where `q` and `-q` represent the same rotation.

## Target Spine

- `S3S-T0001`: `Circle.S3.quaternionConjugation_neg`
- `S3S-T0002`: `Circle.S3.quaternionConjugation_one`
- `S3S-T0003`: `Circle.S3.quaternionConjugation_zero_vector`

## Model

The formal action used here is quaternion conjugation:

```text
Circle.S3.quaternionConjugationAction q v = q * v * star q
```

For unit quaternions, `star q` is the inverse of `q` by `Circle.S3.unitQuaternion_inverse`, so this is the algebraic shape behind quaternion rotation. This paper does not yet formalize all of `SO(3)`, pure imaginary vectors, or the quotient map from unit quaternions to rotations.

## Proved Core

`S3S-T0002` is proved by `Circle.S3.quaternionConjugation_one`: conjugation by the identity quaternion fixes every input.

`S3S-T0003` is proved by `Circle.S3.quaternionConjugation_zero_vector`: conjugation sends the zero input quaternion to zero.

`S3S-T0001` is proved by `Circle.S3.quaternionConjugation_neg`.

For every real quaternion `q` and every real quaternion input `v`,

```text
quaternionConjugationAction (-q) v =
quaternionConjugationAction q v
```

Together these are the first formal shadow of the spin double-cover story: the action has an identity case, fixes zero, and changing a quaternion representative by sign does not change the conjugation action.

The Python sidecar checks the same algebraic conjugation-action examples for identity action, zero preservation, and sign cancellation. It does not assert the full `SO(3)` quotient.

## Dictionary Targets

- `S3S-0001`: quaternion conjugation action
- `S3S-0002`: quaternion sign ambiguity

## Notes

The safe claim is the algebraic conjugation-action spine: identity action, zero preservation, and sign cancellation. The stronger geometric claim that unit quaternions double-cover `SO(3)` should remain a later target until the rotation quotient has been formally modeled.
