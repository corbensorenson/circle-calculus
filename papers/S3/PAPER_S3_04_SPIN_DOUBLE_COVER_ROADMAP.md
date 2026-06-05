# Circle Calculus S3.4: Spin, Double Covers, and Rotation Quotients

Status: draft scaffold with the first spin sign-cancellation theorem proved.

## Aim

This paper begins the connection from unit quaternions to 3D rotations and the double-cover relationship where `q` and `-q` represent the same rotation.

## Target Spine

- `S3S-T0001`: `Circle.S3.quaternionConjugation_neg`

## Model

The formal action used here is quaternion conjugation:

```text
Circle.S3.quaternionConjugationAction q v = q * v * star q
```

For unit quaternions, `star q` is the inverse of `q` by `Circle.S3.unitQuaternion_inverse`, so this is the algebraic shape behind quaternion rotation. This paper does not yet formalize all of `SO(3)`, pure imaginary vectors, or the quotient map from unit quaternions to rotations.

## Proved Core

`S3S-T0001` is proved by `Circle.S3.quaternionConjugation_neg`.

For every real quaternion `q` and every real quaternion input `v`,

```text
quaternionConjugationAction (-q) v =
quaternionConjugationAction q v
```

This is the first formal shadow of the spin double-cover story: changing a quaternion representative by sign does not change the conjugation action.

## Dictionary Targets

- `S3S-0001`: quaternion conjugation action
- `S3S-0002`: quaternion sign ambiguity

## Notes

The safe claim is sign cancellation for the conjugation action. The stronger geometric claim that unit quaternions double-cover `SO(3)` should remain a later target until the rotation quotient has been formally modeled.
