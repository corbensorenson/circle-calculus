# Circle Calculus AI 1: Circle AI Architectures

Status: draft with a proved finite phase-channel seed.

## Aim

State the disciplined Circle AI thesis for phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, geometry-aware models, and proof-carrying model components.

The current formal seed is `COMMON-0026`, the AI phase channel

```text
phase_channel(period,position) = position mod period
```

for positive periods. This is a feature-index primitive, not evidence of model quality.

## Theorem Spine

- `AIA-T0001`: for positive period, the phase channel is bounded by the period. Lean declaration: `Circle.Applications.phaseChannel_lt_period`.
- `AIA-T0002`: for positive period, adding one full period preserves the phase channel. Lean declaration: `Circle.Applications.phaseChannel_add_period`.

The Python sidecar checks the same finite examples. Architecture claims still need MLX/Mac-compatible benchmarks against strong baselines.

## Next Program

- Target data and architectures with real cyclic, periodic, convolutional, rotational, harmonic, or memory-like structure.
- Compare against strong ordinary baselines.
- Use MLX/Mac-compatible prototypes first.

## Guardrail

Do not claim general AI improvement from circles.
