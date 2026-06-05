# Circle Calculus S3.3: Hopf Coils

Status: draft scaffold with executable Python exploration before full Lean formalization.

## Aim

This paper models the Hopf structure `S^1 -> S^3 -> S^2` as hidden circular phase over a visible sphere base.

## Target Spine

- `S3H-T0001`: `Circle.S3.hopfMap_lands_sphere`
- `S3H-T0002`: `Circle.S3.hopfMap_phase_invariant`
- `S3H-T0003`: `Circle.S3.hopfFiber_circle_like`
- `S3H-W0001`: not globally `S^2 x S^1`

## Model

The executable sidecar uses the standard complex-pair Hopf coordinates. A point of `S^3` is represented as a normalized pair

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

## Executable Core

The Python sidecar `sidecars/PAPER_S3_03_HOPF_COILS/python/test_paper_s3_03_examples.py` checks three model properties:

- `S3H-T0001`: normalized complex pairs map to points whose squared `S^2` norm is numerically `1`.
- `S3H-T0002`: simultaneous common-phase rotation leaves the Hopf base point unchanged.
- `S3H-T0003`: the common-phase orbit stays normalized, preserves the Hopf base point, and closes after angle `2*pi`.

These are executable checks, not formal Lean proofs. The dimension manifest keeps the three Hopf targets at `exploratory_python` until the real/complex analysis path for Lean is selected.

## Warning

`S3H-W0001` remains active: the Hopf fibration has circle-like fibers, but `S^3` should not be treated as the global product `S^2 x S^1`.

## Dictionary Targets

- `S3H-0001`: Hopf map
- `S3H-0002`: Hopf phase fiber
- `S3H-W0001`: Hopf not product warning

## Notes

Move to Lean only where the supporting real/complex analysis infrastructure is ready. Until then, this paper should be read as an executable model and roadmap for the Hopf layer, not as a completed formalization.
