# Circle Calculus AI 1: Circle AI Architectures

Status: polished draft with a proved finite phase-channel seed.

## Aim

This paper states the disciplined Circle AI thesis: circle/coil structure may help when a model or dataset has real phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, or geometry-aware structure. It does not imply that circles improve all neural networks.

Many existing AI components already contain circle-shaped ingredients: RoPE and rotary embeddings, Fourier neural operators, FFT-style sequence mixers, SIREN-like periodic activations, circulant or block-circulant layers, long convolution systems, structured state-space models, spherical CNNs, and quaternion neural networks. The possible contribution here is not inventing those ingredients. It is making the phase/coil/proof interface systematic.

## Current Model

The current formal seed is `COMMON-0026`, the AI phase channel

```text
phase_channel(period,position) = position mod period
```

for positive periods. This is a feature-index primitive, not evidence of model quality.

## Theorem Spine

- `AIA-T0001`: `Circle.Applications.phaseChannel_lt_period`
- `AIA-T0002`: `Circle.Applications.phaseChannel_add_period`
- `AIA-T0003`: `Circle.Applications.phaseChannel_zero`

## Proved Core

`AIA-T0001` proves that the phase channel is bounded by the positive period. `AIA-T0002` proves that adding one full period preserves the channel. `AIA-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts certify only a finite phase-indexing primitive. They do not prove lower loss, better generalization, longer context, faster inference, or improved reasoning.

## Architecture Program

The first architecture track should build MLX/Mac-compatible prototypes around structures that already have a reason to be cyclic:

- phase features for periodic or seasonal sequences;
- sparse cyclic mixing for selected stride/orbit patterns;
- circular memory banks with explicit alias diagnostics;
- harmonic or circulant layers where convolutional structure is real;
- spherical or quaternion models where data lives on `S^2`, `SO(3)`, or orientation-like spaces.

Every experiment should compare against strong ordinary baselines and report negative results if the circle structure does not help.

## Next Program

- Start with synthetic tasks where the true cyclic structure is known.
- Compare against dense MLP/attention, standard RoPE, convolution, Hyena-like mixers, and S4/Mamba-like baselines as appropriate.
- Keep MLX/Mac-compatible prototypes first.
- Separate Lean-proved indexing facts from model-quality claims.

## Guardrail

Do not claim general AI improvement from circles. The target is cheaper, more interpretable, or more geometry-aware components only where cyclic or harmonic structure is real.
