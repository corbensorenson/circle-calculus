# Circle Calculus S3.3: Hopf Coils

Status: polished draft with bounded Hopf coordinate landing, phase-invariance, phase-multiplication, phase-action, and normalized fiber-orbit facts Lean-proved.

## Aim

This paper introduces the Hopf pattern `S^1 -> S^3 -> S^2` as visible base state with hidden circular phase. It is one of the central examples for Circle Calculus because it shows how a circle-like fiber can be real structure rather than decorative metaphor.

The current contribution is bounded and algebraic: coordinate landing, phase invariance, identity phase, phase composition, and normalized phase-orbit preservation. It is not yet a full formalization of the Hopf fibration as a topological quotient.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S3_03_HOPF_COILS/lean/PaperS303.lean
```

The Python examples are:

```text
sidecars/PAPER_S3_03_HOPF_COILS/python/test_paper_s3_03_examples.py
```

The theorem, warning, and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks coordinate examples; Lean declarations determine proof status.

## Theorem Spine

- `S3H-T0001`: `Circle.S3.hopfMap_lands_sphere`
- `S3H-T0002`: `Circle.S3.hopfMap_phase_invariant`
- `S3H-T0003`: `Circle.S3.hopfFiber_circle_like`
- `S3H-T0004`: `Circle.S3.phaseRotatePair_identity`
- `S3H-T0005`: `Circle.S3.phaseRotatePair_comp`
- `S3H-T0006`: `Circle.S3.hopfPhaseAction_laws`
- `S3H-T0007`: `Circle.S3.hopfPhaseMul_identity`
- `S3H-T0008`: `Circle.S3.hopfPhaseMul_assoc`
- `S3H-W0001`: not globally `S^2 x S^1`

## Model

The executable sidecar uses the standard complex-pair Hopf coordinates. The Lean sidecar uses equivalent real coordinates. A point of `S^3` is represented as a normalized pair:

```text
(z0, z1) in C^2
|z0|^2 + |z1|^2 = 1
```

The Hopf map is:

```text
H(z0,z1) =
  (2 Re(z0 conjugate(z1)),
   2 Im(z0 conjugate(z1)),
   |z0|^2 - |z1|^2)
```

The hidden phase action is simultaneous common rotation:

```text
(z0,z1) -> (exp(i theta) z0, exp(i theta) z1)
```

The Lean wrapper records this as a small action interface:

```text
HopfPhase(re,im)
hopfPhaseIdentity = (1,0)
hopfPhaseMul(left,right) = complex phase multiplication
hopfPhaseAct(phase,pair) = common phase rotation
```

## Proved Core

`S3H-T0001` proves that a normalized coordinate pair lands on the unit base equation. The helper theorem `Circle.S3.hopfBaseNormSq_hopfMap` proves the exact coordinate identity:

```text
||H(p)||^2 = ||p||^4
```

`S3H-T0002` proves that common multiplication by a unit real-coordinate phase preserves the Hopf base point. `S3H-T0003` proves that the same unit phase keeps a normalized pair normalized and preserves the base point.

`S3H-T0004` proves the identity phase law, and `S3H-T0005` proves that composing phase rotations follows complex multiplication:

```text
(u,v)*(a,b) = (u*a - v*b, v*a + u*b)
```

`S3H-T0006` packages those laws through the `HopfPhase` action wrapper: identity phase fixes every Hopf pair, and acting by one phase after another is the same as acting by their phase product.

`S3H-T0007` proves that the phase identity is a left and right identity for the `HopfPhase` multiplication wrapper. `S3H-T0008` proves that this phase multiplication is associative. Together, these make the checked phase-action API less ad hoc while remaining a coordinate algebra interface rather than a global product theorem.

The Python sidecar checks the same complex-coordinate examples, including sampled `2*pi` closure, phase multiplication identity/associativity, and the phase action laws as executable intuition. Those examples support the paper, but the proof status comes from the Lean declarations.

## Warning

`S3H-W0001` remains active: the Hopf fibration has circle-like fibers, but `S^3` should not be treated as the global product `S^2 x S^1`.

## Dictionary Targets

- `S3H-0001`: Hopf map
- `S3H-0002`: Hopf phase fiber
- `S3H-W0001`: Hopf not product warning

## Guardrails

The current Lean contribution is algebraic and coordinate-bounded. The phase action wrapper is an interface for the checked coordinate action, not a proof that `S^3` is a global product. The full Hopf fibration, topology of fibers, analytic circle parameterization beyond these algebraic phase laws, and global non-product structure remain future formalization work.
