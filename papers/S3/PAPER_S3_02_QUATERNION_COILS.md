# Circle Calculus S3.2: Quaternion Coils and Unit-Quaternion Hypersphere

Status: draft scaffold with the core quaternion theorem spine proved.

## Aim

This paper develops the algebraic `S^3` model using real quaternions and unit quaternions.

## Target Spine

- `S3Q-T0001`: `Circle.S3.quaternionNorm`
- `S3Q-T0002`: `Circle.S3.unitQuaternion_mul_closed`
- `S3Q-T0003`: `Circle.S3.unitQuaternion_inverse`
- `S3Q-T0004`: `Circle.S3.quaternion_noncommutative_example`
- `S3Q-T0005`: `Circle.S3.quaternion_mul_assoc`

## Model

The Lean model uses mathlib's quaternion algebra:

```text
Circle.S3.RealQuaternion = Quaternion real
```

The project norm primitive is

```text
Circle.S3.quaternionNorm q = Quaternion.normSq q
```

where `Quaternion.normSq` is the norm-square multiplicative map supplied by mathlib.

A unit quaternion is bundled as:

```text
UnitQuaternion =
  val  : RealQuaternion
  unit : quaternionNorm val = 1
```

This is the algebraic `S^3` layer: the unit condition cuts out the unit 3-sphere in real quaternion coordinates, while multiplication gives a native group-like composition operation.

## Proved Core

`S3Q-T0001` is implemented by `Circle.S3.quaternionNorm`.

`S3Q-T0002` is proved by `Circle.S3.unitQuaternion_mul_closed`: if `p` and `q` are unit quaternions, then `p.val * q.val` also has norm `1`.

`S3Q-T0003` is proved by `Circle.S3.unitQuaternion_inverse`: for a unit quaternion `q`, conjugation gives both inverse equations

```text
q.val * star q.val = 1
star q.val * q.val = 1
```

`S3Q-T0004` is proved by `Circle.S3.quaternion_noncommutative_example`: the exact integer basis quaternions `i` and `j` satisfy

```text
i * j != j * i
```

This is the formal version of the slogan `S^3: order matters`.

`S3Q-T0005` is proved by `Circle.S3.quaternion_mul_assoc`: quaternion multiplication is associative.

## Dictionary Targets

- `S3Q-0001`: quaternion model
- `S3Q-0002`: unit quaternion
- `S3Q-0003`: quaternion noncommutativity

## Notes

This paper uses mathlib quaternion support directly. It does not claim that every topological feature of continuous `S^3` has been formalized here; it proves the algebraic unit-quaternion spine needed before Hopf and spin-double-cover work.
