# Circle Calculus S7.3: Octonionic Units and Nonassociative Coils

Status: polished draft with the bounded Cayley-Dickson octonion theorem spine Lean-proved.

## Aim

This paper develops the octonionic `S^7` layer cautiously. Octonions are the first place in the dimensional ladder where multiplication remains norm-compatible but becomes nonassociative. That means the project must track order and grouping explicitly.

The core slogan for this stage is:

```text
S^7: order and grouping matter
```

## Theorem Spine

- `S7O-T0001`: `Circle.S7.octonionBasis`
- `S7O-T0002`: `Circle.S7.octonionConjugateNorm`
- `S7O-T0003`: `Circle.S7.octonionNormMul`
- `S7O-T0004`: `Circle.S7.unitOctonion_mul_closed`
- `S7O-T0005`: `Circle.S7.octonion_noncommutative_example`
- `S7O-T0006`: `Circle.S7.octonion_nonassociative_example`
- `S7O-W0001`: unit octonions are not a group
- `S7O-W0002`: bracketing matters

## Model

The executable sidecar uses a small Cayley-Dickson octonion model, and the Lean sidecar mirrors a bounded real-coordinate Cayley-Dickson skeleton:

```text
Octonion = Quaternion pair
```

The model includes multiplication, conjugation, squared norm, basis elements `e0` through `e7`, and normalization helpers. It is intentionally bounded: it proves the current coordinate algebra spine before the project attempts a fuller octonion algebra library.

## Proved Core

`S7O-T0001` proves each coordinate basis element has squared norm `1`. `S7O-T0002` proves that `x * conjugate(x)` is the real coordinate containing `squared_norm(x)`.

`S7O-T0003` proves squared norm is multiplicative for the Cayley-Dickson coordinate product. `S7O-T0004` uses that fact to prove products of norm-one octonions remain norm-one.

The next two theorems are warnings made formal. `S7O-T0005` proves:

```text
e1 * e2 != e2 * e1
```

`S7O-T0006` proves:

```text
(e1 * e2) * e4 != e1 * (e2 * e4)
```

The Python sidecar checks the same basis, conjugate-norm, norm-multiplication, unit-product, noncommutativity, and nonassociativity examples.

## Warnings

`S7O-W0001` remains active: unit octonions should not be treated as a group under ordinary multiplication.

`S7O-W0002` remains active: bracketing is part of an octonion statement because multiplication is nonassociative.

## Dictionary Targets

- `S7O-0001`: octonion model
- `S7O-0002`: unit octonion
- `S7O-W0001`: unit octonions are not a group warning
- `S7O-W0002`: octonion bracketing warning

## Guardrails

This paper proves bounded coordinate octonion facts and formal example warnings. It does not claim unit octonions form a group, does not erase bracketing, and does not yet prove the full octonionic Hopf fibration.
