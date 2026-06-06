# Circle Calculus AI 1: Circle AI Architectures

Status: polished draft with a proved finite phase-channel seed and an exploratory deterministic benchmark fixture.

## Aim

This paper states the disciplined Circle AI thesis: circle/coil structure may help when a model or dataset has real phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, or geometry-aware structure. It does not imply that circles improve all neural networks.

Many existing AI components already contain circle-shaped ingredients: RoPE and rotary embeddings, Fourier neural operators, FFT-style sequence mixers, SIREN-like periodic activations, circulant or block-circulant layers, long convolution systems, structured state-space models, spherical CNNs, and quaternion neural networks. The possible contribution here is not inventing those ingredients. It is making the phase/coil/proof interface systematic.

## Current Model

The current formal seed is `COMMON-0026`, the AI phase channel

```text
phase_channel(period,position) = position mod period
```

for positive periods. This is a feature-index primitive, not evidence of model quality.

The current executable benchmark seed is `COMMON-0039`, a deterministic known-period binary-label fixture:

```text
positions -> phase_channel(period,position) -> phase lookup
```

It compares that phase lookup against a constant baseline on a task whose labels are constructed from the true phase. The fixture can score on CPU and can use MLX scoring when `mlx.core` is available. This is a smoke test for the benchmark harness, not evidence about learned models or real data.

`COMMON-0044` adds a second tiny fixture comparing phase lookup with a learned scalar threshold baseline on two controls. On the periodic synthetic task, phase lookup reaches `1.0` accuracy while the scalar threshold baseline does not. On the nonperiodic threshold-control task, the scalar threshold reaches `1.0` while phase lookup fails. This is the intended guardrail: phase features should help only when phase structure is real.

## Theorem Spine

- `AIA-T0001`: `Circle.Applications.phaseChannel_lt_period`
- `AIA-T0002`: `Circle.Applications.phaseChannel_add_period`
- `AIA-T0003`: `Circle.Applications.phaseChannel_zero`

## Proved Core

`AIA-T0001` proves that the phase channel is bounded by the positive period. `AIA-T0002` proves that adding one full period preserves the channel. `AIA-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts certify only a finite phase-indexing primitive. They do not prove lower loss, better generalization, longer context, faster inference, or improved reasoning.

## Benchmark Fixture

`AIA-B0001` is the first exploratory Python benchmark fixture for this paper. `AIA-B0002` adds the periodic/nonperiodic learned-baseline control. They live in:

```text
circle_math/applications/circle_ai.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py
```

The test sidecar checks that the fixture is deterministic, that phase lookup solves the constructed known-period task while the constant baseline does not, and that an ordinary scalar threshold baseline wins on a nonperiodic control. The fixture intentionally does not compare against dense neural networks, RoPE, attention, state-space models, or real sequence data yet.

## Architecture Program

The first architecture track should build MLX/Mac-compatible prototypes around structures that already have a reason to be cyclic:

- phase features for periodic or seasonal sequences;
- sparse cyclic mixing for selected stride/orbit patterns;
- circular memory banks with explicit alias diagnostics;
- harmonic or circulant layers where convolutional structure is real;
- spherical or quaternion models where data lives on `S^2`, `SO(3)`, or orientation-like spaces.

Every experiment should compare against strong ordinary baselines and report negative results if the circle structure does not help.

## Next Program

- Expand the learned phase fixture beyond scalar thresholds to dense, RoPE, and cyclic-feature baselines.
- Compare against dense MLP/attention, standard RoPE, convolution, Hyena-like mixers, and S4/Mamba-like baselines as appropriate.
- Add separate memory-slot and adapter-block benchmarks before making CoilKV, Coil Attention, CoilRA, or MultiCoil RoPE claims.
- Keep MLX/Mac-compatible prototypes first.
- Separate Lean-proved indexing facts from model-quality claims.

## Guardrail

Do not claim general AI improvement from circles. The target is cheaper, more interpretable, or more geometry-aware components only where cyclic or harmonic structure is real.
