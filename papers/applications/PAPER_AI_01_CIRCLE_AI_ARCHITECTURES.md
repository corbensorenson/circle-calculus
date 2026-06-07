# Circle Calculus AI 1: Circle AI Architectures

Status: polished draft with a proved finite phase-channel seed and an exploratory deterministic benchmark fixture.

## Aim

This paper states the disciplined Circle AI thesis: circle/coil structure may help when a model or dataset has real phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, or geometry-aware structure. It does not imply that circles improve all neural networks.

Many existing AI components already contain circle-shaped ingredients: RoPE and rotary embeddings, Fourier neural operators, FFT-style sequence mixers, SIREN-like periodic activations, circulant or block-circulant layers, long convolution systems, structured state-space models, looped/recursive transformers, spherical CNNs, and quaternion neural networks. The possible contribution here is not inventing those ingredients. It is making the phase/coil/proof interface systematic.

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

`COMMON-0048` adds a backend parity fixture. It scores the current deterministic AI cases on CPU and, when `mlx.core` is available, repeats the same scoring through MLX arrays. If MLX is not installed, the script reports that directly. This is a parity/readiness check, not an acceleration or model-quality benchmark.

`COMMON-0049` adds a learned-feature baseline fixture. It compares the correct cyclic phase feature against three small ordinary baselines: a dense scalar threshold, a learned absolute-position lookup, and a wrong-period phase lookup. The same fixture includes a nonperiodic scalar-control task where the dense scalar baseline wins. This is still a synthetic guardrail, not a neural-network result.

`COMMON-0050` adds a harmonic feature baseline fixture. It compares cyclic phase lookup with a correct sine/cosine feature lookup, a wrong-frequency sine/cosine lookup, a scalar threshold, and a learned-position lookup. This is a bridge to ordinary Fourier/RoPE-style phase encodings, not a standard RoPE benchmark or language-model result.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/lean/PaperAI01.lean
```

The Python examples and benchmark fixture are:

```text
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/test_phase_channel_examples.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_backend_parity.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_learned_feature_baselines.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_harmonic_feature_baselines.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. Benchmark fixtures are exploratory executable evidence; Lean declarations determine proof status.

## Theorem Spine

- `AIA-T0001`: `Circle.Applications.phaseChannel_lt_period`
- `AIA-T0002`: `Circle.Applications.phaseChannel_add_period`
- `AIA-T0003`: `Circle.Applications.phaseChannel_zero`
- `AIA-T0004`: `Circle.Applications.phaseChannel_add_mul_period`
- `AIA-T0005`: `Circle.Applications.phaseChannel_idempotent`

## Proved Core

`AIA-T0001` proves that the phase channel is bounded by the positive period. `AIA-T0002` proves that adding one full period preserves the channel, `AIA-T0004` proves the same closure law for any whole number of full periods, and `AIA-T0005` proves that normalizing an already normalized phase channel is a no-op. `AIA-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts certify only a finite phase-indexing primitive. They do not prove lower loss, better generalization, longer context, faster inference, or improved reasoning.

## Benchmark Fixture

`AIA-B0001` is the first exploratory Python benchmark fixture for this paper. `AIA-B0002` adds the periodic/nonperiodic learned-baseline control. `AIA-B0003` adds CPU/optional-MLX backend parity scoring across the current deterministic AI fixtures. `AIA-B0004` adds learned-feature baseline comparisons against dense scalar, learned-position, and wrong-period baselines, plus a nonperiodic scalar-control task. `AIA-B0005` adds harmonic/Fourier feature comparisons against wrong-frequency, scalar, and learned-position baselines. They live in:

```text
circle_math/applications/circle_ai.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_backend_parity.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_learned_feature_baselines.py
sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_harmonic_feature_baselines.py
```

The test sidecar checks that the fixture is deterministic, that phase lookup solves the constructed known-period task while the constant baseline does not, that an ordinary scalar threshold baseline wins on a nonperiodic control, that learned-position, wrong-period, and wrong-frequency baselines do not get mistaken for evidence, that correct harmonic features match the constructed phase task, and that CPU/MLX parity is reported honestly. The fixture intentionally does not compare against dense neural networks, standard RoPE, attention, state-space models, real sequence data, or runtime measurements yet.

## Architecture Program

The first architecture track should build MLX/Mac-compatible prototypes around structures that already have a reason to be cyclic:

- phase features for periodic or seasonal sequences;
- looped/recursive transformer schedules where recurrence depth, loop phase, exit status, and overthinking boundaries are explicitly tracked;
- sparse cyclic mixing for selected stride/orbit patterns;
- circular memory banks with explicit alias diagnostics;
- harmonic or circulant layers where convolutional structure is real;
- spherical or quaternion models where data lives on `S^2`, `SO(3)`, or orientation-like spaces.

Every experiment should compare against strong ordinary baselines and report negative results if the circle structure does not help.

## Next Program

- Use `AIA-B0004` as the current learned-feature baseline scaffold.
- Use `AIA-B0005` as the current harmonic/Fourier feature scaffold.
- Compare next against dense MLP/attention, standard RoPE, learned positional encodings, convolution, Hyena-like mixers, and S4/Mamba-like baselines as appropriate.
- Use `AIM-B0003` as the first looped/recursive transformer schedule scaffold, then compare learned recurrence ideas against dense transformer depth, Universal Transformer recurrence, fixed looped transformers, adaptive early-exit models, recurrent-memory transformers, sparse/MoE looped models, RWKV/Mamba-style recurrent/state-space models, and ordinary nonrecursive transformer baselines before reasoning or quality claims.
- Add separate memory-slot and adapter-block benchmarks before making CoilKV, Coil Attention, CoilRA, or MultiCoil RoPE claims.
- Use `AIA-B0003` as backend parity scaffolding only; real MLX model prototypes and timing remain separate work.
- Keep MLX/Mac-compatible prototypes first.
- Separate Lean-proved indexing facts from model-quality claims.

## Guardrail

Do not claim general AI improvement from circles. The target is cheaper, more interpretable, or more geometry-aware components only where cyclic or harmonic structure is real.
