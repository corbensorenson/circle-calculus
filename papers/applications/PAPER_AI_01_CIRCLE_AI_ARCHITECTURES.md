# Circle Calculus AI 1: Circle AI Architectures

Status: polished draft with a proved finite phase-channel seed and an exploratory deterministic benchmark fixture.

## Aim

This paper states the disciplined Circle AI thesis: circle/coil structure may help when a model or dataset has real phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, or geometry-aware structure. It does not imply that circles improve all neural networks.

Many existing AI components already contain circle-shaped ingredients: RoPE and rotary embeddings, Fourier neural operators, FFT-style sequence mixers, SIREN-like periodic activations, circulant or block-circulant layers, long convolution systems, structured state-space models, looped/recursive transformers, spherical CNNs, and quaternion neural networks. The possible contribution here is not inventing those ingredients. It is making the phase/coil/proof interface systematic.

## Two Tiers Of Result (Read This First)

To keep the program honest, separate two very different kinds of "AI theorem" in this track:

1. **Finite-indexing bookkeeping** — the `AIA`, `AIM`, and `AIRA` families. These are
   elementary facts that an index stays in range and is unchanged by a full period (for
   example `phase_channel(period, position) = position mod period < period`). They are
   honest but **trivial** — instances of the `S^1` closure spine wearing AI vocabulary. They
   are useful infrastructure for keeping the prose tied to Lean, and nothing more; they are
   not evidence that circular structure helps a model.
2. **Proved structural guarantees** — the `AIT` family (in `PAPER_AI_02` and `PAPER_AI_03`).
   These are the genuinely non-trivial, ML-relevant facts: strided-attention coverage from
   the orbit/gcd theory, RoPE relative position from rotation composition, and circulant
   shift-equivariance. This is where circle math earns its place.

Everything else on this track is exploratory benchmark scaffolding, not a model-quality
claim. Whether circular structure improves accuracy, efficiency, or extrapolation is an
empirical question that Lean cannot settle and that requires experiments with ordinary
baselines and negative controls.

## Current Model

The first finite-indexing seed is `COMMON-0026`, the AI phase channel

```text
phase_channel(period,position) = position mod period
```

for positive periods. This is a feature-index primitive (tier 1 above), not evidence of model quality.

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

## Theseus-Hive Transfer Program

Circle Calculus also has a direct application target in the local Theseus-Hive AI project. The transfer plan is recorded in:

```text
docs/THESEUS_HIVE_AI_TRANSFER.md
```

The purpose is not to claim that Circle Calculus has already improved Theseus-Hive. The purpose is to turn the AI theorem spine and sidecar fixtures into contracts Theseus-Hive can test under its existing private-transfer and governance machinery:

- recurrence contracts for looped/recursive schedules, exit certificates, active-token sets, and overthinking boundaries;
- strided/fanout contracts that report gcd, coverage, duplicate pressure, candidate budget, and rejection reasons;
- cyclic memory analyzers that separate residue from winding so alias pressure is visible;
- phase-feature tags for state-sequence decoders, compared against ordinary position buckets and learned-position controls;
- circulant and block-cyclic mixer baselines for small route heads, rankers, or adapter-like layers;
- seed-rule provenance objects for workflows where exact regeneration is the real compression target.

This is the most important near-term AI path because Theseus-Hive already has ratchets, private held-out pressure, STS-conditioned candidate generation, context packet memory, work-budget admission, and CPU/MLX local execution boundaries, with CUDA treated as external portability or baseline context. Circle Calculus should plug into that system as proof-linked structure and benchmark scaffolding, not as a replacement for its training and evaluation gates.

The first public-side tool is now:

```bash
make theseus-ai-contracts
```

It writes `site/data/generated/theseus_hive_ai_contracts.json`, a deterministic fixture pack with recurrence, fanout, memory, phase-feature, mixer, and seed-rule contracts. These contracts are experiment inputs, not results.

The local companion Theseus-Hive workspace now has a report-only consumer, `scripts/circle_ai_contract_consumer.py`, a structural smoke workload layer, `scripts/circle_ai_private_workload_smoke.py`, a deterministic proxy benchmark layer, `scripts/circle_ai_private_proxy_benchmark.py`, a real local aggregate attachment layer, `scripts/circle_ai_real_workload_attachments.py`, and a first scored private benchmark layer, `scripts/circle_ai_scored_private_benchmarks.py`, with a matching note at `docs/CIRCLE_CALCULUS_TRANSFER.md`. The consumer loads the Circle pack, writes `reports/circle_ai_contract_consumer.json` and `.md`, separates quality/runtime/memory/parameter/interpretability/transfer/failure-case axes, and keeps its state `YELLOW` until named private benchmark results exist. The smoke layer adds six stable workload slots: `circle_recurrence_budget_trace_smoke`, `circle_strided_candidate_coverage_smoke`, `circle_memory_alias_visibility_smoke`, `circle_phase_feature_invariance_smoke`, `circle_mixer_parameter_accounting_smoke`, and `circle_seed_rule_regeneration_smoke`. The proxy layer adds measured deterministic baseline metrics under `circle_recurrence_budget_proxy_v1`, `circle_candidate_fanout_proxy_v1`, `circle_memory_alias_proxy_v1`, `circle_phase_feature_proxy_v1`, `circle_mixer_parameter_proxy_v1`, and `circle_seed_rule_regeneration_proxy_v1`. The aggregate attachment layer adds `circle_recurrence_budget_real_rows_v1`, `circle_candidate_fanout_real_manifest_v1`, `circle_memory_alias_real_trace_v1`, `circle_phase_feature_real_sequence_v1`, `circle_mixer_real_report_summary_v1`, and `circle_seed_rule_real_provenance_summary_v1`. The scored layer adds `circle_candidate_fanout_scored_manifest_v1`, `circle_candidate_fanout_semantic_frontier_v1`, `circle_candidate_fanout_equal_budget_semantic_v1`, `circle_recurrence_work_budget_semantic_v1`, and `circle_memory_context_packet_retrieval_v1`, comparing Circle and ordinary candidate selections on private manifest score/gate fields, existing private semantic score-report context, a full-frontier private semantic execution run, a recurrence work-budget execution run over 1040 tasks across 26 categories, and context-packet identity/retention policies over 37 ledger targets. It still marks learned-model quality metrics, promotion evidence, and private data export absent; the full-frontier scored runs tie the relevant ordinary rank-one or fixed-depth baselines, and equal-budget memory retention ties ordinary retention baselines rather than showing a Circle advantage.

The acceptance rule is strict: a Circle-side contract can be Lean-proved for finite schedule/index/coverage/equivariance facts, but any claim that it improves Theseus-Hive must name the workload, baseline, metric, reproducible script, and report.

## Next Program

- Use `AIA-B0004` as the current learned-feature baseline scaffold.
- Use `AIA-B0005` as the current harmonic/Fourier feature scaffold.
- Compare next against dense MLP/attention, standard RoPE, learned positional encodings, convolution, Hyena-like mixers, and S4/Mamba-like baselines as appropriate.
- Use `AIM-B0003` as the first looped/recursive transformer schedule scaffold and `AIM-B0005` as the first token-level routing scaffold, then compare learned recurrence ideas against dense transformer depth, Universal Transformer recurrence, fixed looped transformers, adaptive early-exit models, recurrent-memory transformers, token-level Mixture-of-Recursions, middle-block recurrence, multi-resolution recurrence, training-free loop wrappers, sparse/MoE looped models, RWKV/Mamba-style recurrent/state-space models, and ordinary nonrecursive transformer baselines before reasoning or quality claims.
- Add separate memory-slot and adapter-block benchmarks before making CoilKV, Coil Attention, CoilRA, or MultiCoil RoPE claims.
- Use the private Theseus-Hive consumers for `site/data/generated/theseus_hive_ai_contracts.json` as the report boundary, keeping private reports out of the public Circle repository unless they are intentionally scrubbed and public-safe; next use the full-frontier fanout, recurrence, and memory tables to design Circle selection, loop-depth, or downstream retrieval workloads that differ from ordinary baselines when evidence supports it, and promote the remaining phase-feature, mixer, and seed-rule aggregate attachments into scored private benchmarks.
- Use `AIA-B0003` as backend parity scaffolding only; real MLX model prototypes and timing remain separate work.
- Keep MLX/Mac-compatible prototypes first.
- Separate Lean-proved indexing facts from model-quality claims.

## Guardrail

Do not claim general AI improvement from circles. The target is cheaper, more interpretable, or more geometry-aware components only where cyclic or harmonic structure is real.
