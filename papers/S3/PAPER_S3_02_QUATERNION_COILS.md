# Circle Calculus S3.2: Quaternion Coils and Unit-Quaternion Hypersphere

Status: polished draft with the core quaternion theorem spine Lean-proved.

## Aim

This paper develops the algebraic `S^3` model using real quaternions and unit quaternions. It is the first dimension where the project has a native multiplication law that is richer than circle addition: quaternion multiplication is associative and norm-preserving on unit quaternions, but not commutative.

The topological `S^3` count model was introduced separately in `PAPER_S3_01_FINITE_HYPERSPHERES.md`. Here the focus is algebraic.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S3_02_QUATERNION_COILS/lean/PaperS302.lean
```

The Python examples are:

```text
sidecars/PAPER_S3_02_QUATERNION_COILS/python/test_quaternion_coil_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks executable examples; Lean and mathlib declarations determine proof status.

## Model

The Lean model uses mathlib's quaternion algebra:

```text
Circle.S3.RealQuaternion = Quaternion real
```

The project norm primitive is:

```text
Circle.S3.quaternionNorm q = Quaternion.normSq q
```

A unit quaternion is bundled as:

```text
UnitQuaternion =
  val  : RealQuaternion
  unit : quaternionNorm val = 1
```

The unit condition is the algebraic `S^3` layer in real quaternion coordinates.

## Theorem Spine

- `S3Q-T0001`: `Circle.S3.quaternionNorm`
- `S3Q-T0002`: `Circle.S3.unitQuaternion_mul_closed`
- `S3Q-T0003`: `Circle.S3.unitQuaternion_inverse`
- `S3Q-T0004`: `Circle.S3.quaternion_noncommutative_example`
- `S3Q-T0005`: `Circle.S3.quaternion_mul_assoc`
- `S3Q-T0006`: `Circle.S3.unitQuaternion_identity`
- `S3Q-T0007`: `Circle.S3.unitQuaternion_conj_inverse`
- `S3Q-T0008`: `Circle.S3.unitQuaternion_conj_involutive`

## Proved Core

`S3Q-T0001` registers the quaternion norm used by the project.

`S3Q-T0002` proves unit closure: if `p` and `q` are unit quaternions, then `p.val * q.val` also has norm `1`. This is the algebraic reason unit quaternions can act as a closed multiplication layer.

`S3Q-T0003` proves the conjugate-inverse equations:

```text
q.val * star q.val = 1
star q.val * q.val = 1
```

for a unit quaternion `q`.

`S3Q-T0006` packages the bundled identity unit quaternion:

```text
1 * q = q
q * 1 = q
```

inside the `UnitQuaternion` API. `S3Q-T0007` packages the conjugate as the bundled inverse:

```text
q * conjugate(q) = 1
conjugate(q) * q = 1
```

`S3Q-T0008` proves that bundled unit-quaternion conjugation is involutive:

```text
conjugate(conjugate(q)) = q
```

`S3Q-T0004` proves a concrete noncommutative example:

```text
i * j != j * i
```

This is the formal version of the slogan `S^3: order matters`.

`S3Q-T0005` proves associativity of quaternion multiplication. This separates quaternions from the later `S^7` octonion layer, where bracketing becomes a real warning.

The Python sidecar checks executable quaternion norm, unit multiplication, identity laws, conjugate-inverse, conjugate involution, noncommutativity, and associativity examples. These examples align with the Lean theorem spine but do not replace mathlib's formal proofs.

## Role In The Ladder

The quaternion spine supports the bounded Hopf coordinate paper, the spin sign-cancellation paper, the quaternionic Hopf roadmap in `S^7`, and robotics/orientation applications. It is one of the strongest algebraic parts of the dimensional ladder.

## Dictionary Targets

- `S3Q-0001`: quaternion model
- `S3Q-0002`: unit quaternion
- `S3Q-0003`: quaternion noncommutativity

## Guardrails

This paper proves the algebraic unit-quaternion spine. It does not claim that every topological, smooth, or rotational feature of continuous `S^3` has been formalized here.
