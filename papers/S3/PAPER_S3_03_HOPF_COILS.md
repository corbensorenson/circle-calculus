# Circle Calculus S3.3: Hopf Coils

Status: draft with two bounded Hopf algebra facts Lean-proved; the full fiber-closure model remains executable Python exploration.

## Aim

This paper models the Hopf structure `S^1 -> S^3 -> S^2` as hidden circular phase over a visible sphere base.

## Target Spine

- `S3H-T0001`: `Circle.S3.hopfMap_lands_sphere`
- `S3H-T0002`: `Circle.S3.hopfMap_phase_invariant`
- `S3H-T0003`: `Circle.S3.hopfFiber_circle_like`
- `S3H-W0001`: not globally `S^2 x S^1`

## Model

The executable sidecar uses the standard complex-pair Hopf coordinates. The Lean sidecar uses equivalent real coordinates for the pair. A point of `S^3` is represented as a normalized pair

```text
(z0, z1) in C^2
|z0|^2 + |z1|^2 = 1
```

The Hopf map used by the Python model is

```text
H(z0,z1) =
  (2 Re(z0 conjugate(z1)),
   2 Im(z0 conjugate(z1)),
   |z0|^2 - |z1|^2)
```

The common hidden phase action is

```text
(z0,z1) -> (exp(i theta) z0, exp(i theta) z1)
```

This phase action is the exploratory fiber coil: changing `theta` moves in the hidden `S^1` direction while keeping the visible Hopf base point fixed.

## Proved Core

The Lean sidecar `sidecars/PAPER_S3_03_HOPF_COILS/lean/PaperS303.lean` checks the bounded algebraic Hopf coordinate facts:

- `S3H-T0001` is proved by `Circle.S3.hopfMap_lands_sphere`: if the coordinate pair has norm square `1`, the Hopf base coordinates have norm square `1`.
- `S3H-T0002` is proved by `Circle.S3.hopfMap_phase_invariant`: common multiplication by a unit real-coordinate phase `(u,v)` preserves the Hopf base point.

The helper theorem `Circle.S3.hopfBaseNormSq_hopfMap` proves the exact identity

```text
||H(p)||^2 = ||p||^4
```

for the coordinate model.

## Executable Core

The Python sidecar `sidecars/PAPER_S3_03_HOPF_COILS/python/test_paper_s3_03_examples.py` remains useful as executable complex-number exploration:

- `S3H-T0001`: normalized complex pairs map to points whose squared `S^2` norm is numerically `1`, matching the Lean coordinate theorem.
- `S3H-T0002`: simultaneous common-phase rotation leaves the Hopf base point unchanged, matching the Lean coordinate theorem.
- `S3H-T0003`: the common-phase orbit stays normalized, preserves the Hopf base point, and closes after angle `2*pi`.

`S3H-T0003` is still an executable check, not a full Lean fibration or topological closure proof.

## Warning

`S3H-W0001` remains active: the Hopf fibration has circle-like fibers, but `S^3` should not be treated as the global product `S^2 x S^1`.

## Dictionary Targets

- `S3H-0001`: Hopf map
- `S3H-0002`: Hopf phase fiber
- `S3H-W0001`: Hopf not product warning

## Notes

The current Lean contribution is algebraic: landing on the unit base equation and invariance under common unit phase. The full Hopf fibration, topology of fibers, and global non-product structure remain future formalization work.
