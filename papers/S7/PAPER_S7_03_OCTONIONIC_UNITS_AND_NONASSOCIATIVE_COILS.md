# Circle Calculus S7.3: Octonionic Units and Nonassociative Coils

Status: draft scaffold with executable Python exploration before Lean formalization.

## Aim

This paper develops the octonionic `S^7` layer cautiously and explicitly tracks nonassociativity.

## Target Spine

- `S7O-T0001`: `Circle.S7.octonionBasis`
- `S7O-T0002`: `Circle.S7.octonionConjugateNorm`
- `S7O-T0003`: `Circle.S7.octonionNormMul`
- `S7O-T0004`: `Circle.S7.unitOctonion_mul_closed`
- `S7O-T0005`: `Circle.S7.octonion_noncommutative_example`
- `S7O-T0006`: `Circle.S7.octonion_nonassociative_example`
- `S7O-W0001`: unit octonions are not a group
- `S7O-W0002`: bracketing matters

## Dictionary Targets

- `S7O-0001`: octonion model
- `S7O-0002`: unit octonion
- `S7O-W0001`: unit octonions are not a group warning
- `S7O-W0002`: octonion bracketing warning

## Model

The executable sidecar uses a small Cayley-Dickson octonion model:

```text
Octonion = Quaternion pair
```

with multiplication, conjugation, squared norm, basis elements `e0` through `e7`, and normalization helpers in `circle_math.dimensions.octonion`.

This model is intentionally exploratory. It gives concrete examples and diagnostics before the project chooses a Lean octonion formalization path.

## Executable Core

The Python sidecar `sidecars/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS/python/test_paper_s7_03_examples.py` checks:

- `S7O-T0001`: the coordinate basis has eight unit elements.
- `S7O-T0002`: multiplying a sample octonion by its conjugate returns the squared norm in the real coordinate.
- `S7O-T0003`: squared norm is multiplicative on tested sample values.
- `S7O-T0004`: normalized sample octonions have product squared norm `1`.
- `S7O-T0005`: basis elements `e1` and `e2` do not commute.
- `S7O-T0006`: `(e1*e2)*e4` differs from `e1*(e2*e4)`.

These are executable checks, not formal Lean proofs. The dimension manifest keeps the octonion targets at `exploratory_python`.

## Warnings

`S7O-W0001` remains active: unit octonions should not be treated as a group under ordinary multiplication.

`S7O-W0002` remains active: bracketing is part of an octonion statement because multiplication is nonassociative.

## Notes

The core slogan for this stage is `S^7: order and grouping matter`.
