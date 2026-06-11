# Circle Calculus S3.4: Spin, Double Covers, and Rotation Quotients

Status: polished draft with the first spin action, pure-vector boundary, and sign-cancellation theorems Lean-proved.

## Aim

This paper records the first formal step from unit-quaternion algebra toward the spin and rotation story. The target geometric slogan is familiar: unit quaternions describe 3D rotations with the sign ambiguity `q` and `-q`. Circle Calculus does not use that slogan as a proof. It first proves the algebraic invariance that the slogan depends on.

The immediate object is the quaternion conjugation action:

```text
Circle.S3.quaternionConjugationAction q v = q * v * star q
```

For a unit quaternion, `star q` is the inverse supplied by the earlier quaternion paper. That makes this expression the algebraic shape behind quaternion rotation, while still avoiding an unproved global model of `SO(3)`.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP/lean/PaperS304.lean
```

The Python examples are:

```text
sidecars/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP/python/test_spin_conjugation_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks bounded orientation examples; Lean declarations determine proof status.

## Theorem Spine

- `S3S-T0001`: `Circle.S3.quaternionConjugation_neg`
- `S3S-T0002`: `Circle.S3.quaternionConjugation_one`
- `S3S-T0003`: `Circle.S3.quaternionConjugation_zero_vector`
- `S3S-T0004`: `Circle.S3.spinSignRelated_equivalence`
- `S3S-T0005`: `Circle.S3.quaternionConjugation_pure_of_pure`
- `S3S-T0006`: `Circle.S3.quaternionConjugation_normSq`
- `S3S-T0007`: `Circle.S3.quaternionConjugation_re`
- `S3S-T0008`: `Circle.S3.quaternionConjugation_mul`
- `S3S-T0009`: `Circle.S3.quaternionConjugation_real_trivial`
- `S3S-T0010`: `Circle.S3.realUnitQuaternion_eq_pm_one`
- `S3S-T0011`: `Circle.S3.quaternionConjugation_trivial_iff_pm_one`

## Double Cover Core

The five facts `S3S-T0006` through `S3S-T0010` upgrade the conjugation action from a
collection of sign and preservation lemmas into the recognizable algebraic core of the
double cover `Sp(1) = S^3 -> SO(3)`, all on the *actual* real quaternions `Quaternion R`:

- `S3S-T0006` (`Circle.S3.quaternionConjugation_normSq`) shows conjugation by a unit
  quaternion preserves the quaternion norm. This is the **isometry / orthogonality**
  property: the action lands in the rotation group.
- `S3S-T0007` (`Circle.S3.quaternionConjugation_re`) shows it preserves the real part,
  so it preserves the pure-imaginary copy of `R^3` and acts on vectors.
- `S3S-T0008` (`Circle.S3.quaternionConjugation_mul`) shows the action is a **monoid
  homomorphism**: conjugating by `a * b` equals conjugating by `a` then by `b`.
- `S3S-T0009` (`Circle.S3.quaternionConjugation_real_trivial`) and `S3S-T0010`
  (`Circle.S3.realUnitQuaternion_eq_pm_one`) compute the easy direction of the kernel:
  the real unit quaternions are exactly `+1` and `-1`, and they act trivially. With the
  two-to-one fact `S3S-T0001` (`q` and `-q` agree), this is the `±1` content.

Taken together: the conjugation action is a norm- and real-part-preserving monoid
homomorphism that identifies `q` with `-q`. That is the algebraic heart of the double
cover.

`S3S-T0011` (`Circle.S3.quaternionConjugation_trivial_iff_pm_one`) now **completes the
kernel computation**: a unit quaternion acts trivially (fixes every vector) *if and only if*
it is `±1`. The proof of the hard direction is the genuine content — a trivially-acting unit
quaternion commutes with every quaternion, and commuting with the imaginary units `i` and
`j` forces its imaginary parts to vanish, so it is real, hence `±1`. The kernel of the
conjugation action on the unit quaternions is therefore *exactly* the two-element group
`{±1}`.

**Roadmap (not yet claimed).** With the exact kernel in hand, one step remains to the full
double-cover isomorphism `Sp(1) / {±1} ≅ SO(3)`: surjectivity of the action onto `SO(3)`,
the representation-theoretic / analytic step beyond this algebraic spine.

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

`S3S-T0005` defines the conservative pure-vector predicate:

```text
Circle.S3.isPureQuaternion v iff v.re = 0
```

and proves that quaternion conjugation preserves that predicate:

```text
isPureQuaternion v ->
isPureQuaternion (quaternionConjugationAction q v)
```

This is the algebraic boundary needed by the widget's vector inputs. It says that inputs represented as pure-imaginary quaternions stay pure-imaginary after conjugation. It does not prove norm preservation, rotation-matrix semantics, or a full 3D vector-space action.

`S3S-T0001` proves the sign-cancellation law:

```text
quaternionConjugationAction (-q) v =
quaternionConjugationAction q v
```

for every real quaternion `q` and input `v`. The proof is purely algebraic. It uses the multiplication and conjugation laws already formalized in the `S^3` quaternion spine and shows that the two negative signs introduced by `-q` cancel inside the conjugation action.

Together, these facts provide the checked algebraic shadow of the spin double-cover story: identity acts as identity, zero remains zero, pure-vector inputs stay pure-vector outputs, and changing a quaternion representative by sign does not change the action.

`S3S-T0004` defines the conservative sign relation on bundled unit quaternions:

```text
p ~ q iff q = p or q = -p
```

and proves that this relation is reflexive, symmetric, and transitive. This is the quotient-ready algebraic relation needed before any future `SO(3)` coverage is claimed.

The Python sidecar mirrors these examples for identity action, zero preservation, pure-vector preservation, sign cancellation, and bounded sign-relation equivalence checks.

## Orientation-Debugging Note

This paper can already support a small debugging workflow for quaternion orientation code:

1. Treat the two inputs `q` and `-q` as distinct representatives.
2. Compare the downstream conjugation action, not the raw representative sign.
3. Record whether the representatives are sign-related by `S3S-T0004`.
4. Use `S3S-T0005` to check that the pure-vector input boundary remains intact.
5. Use `S3S-T0001` as the checked reason that the conjugation action is unchanged.

The Python sidecar function `orientation_debug_record` follows exactly that bounded workflow. It reports that a sample unit phase `q` and its negative are distinct quaternion records, sign-related representatives, pure-vector preserving on the tested input, and action-equivalent under conjugation on the tested vector. This is an executable orientation-debugging example only. It is not a robotics verification result, not a complete `SO(3)` quotient formalization, and not a replacement for a full rotation-matrix or vector-space model.

## Role In The Ladder

This paper connects three layers of the project:

- `S1`: sign, orientation, and reversible motion;
- `S3`: associative quaternion multiplication and unit-quaternion closure;
- future rotation geometry: quotienting the unit-quaternion action by the sign ambiguity.

It is deliberately placed after `PAPER_S3_02_QUATERNION_COILS.md` and `PAPER_S3_03_HOPF_COILS.md`: the multiplication and phase-action facts must exist before the rotation quotient can be stated honestly.

## Dictionary Targets

- `S3S-0001`: quaternion conjugation action
- `S3S-0002`: quaternion sign ambiguity
- `S3S-0003`: pure quaternion vector boundary

## Guardrails

The proved claim is not yet a full formalization of `Spin(3)`, `SO(3)`, rotation matrices, norm-preserving physical vector rotations, or the quotient map from unit quaternions to rotations. Those belong in a later paper once the project has a precise formal model of 3D vector space and rotation equivalence. The safe current claim is exactly the algebraic conjugation-action spine, pure-imaginary preservation, sign invariance, and the equivalence relation that identifies `q` with `-q`.
