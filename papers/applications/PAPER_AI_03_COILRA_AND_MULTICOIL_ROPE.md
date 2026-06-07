# Circle Calculus AI 3: CoilRA and MultiCoil RoPE

Status: polished draft with a proved adapter-block seed.

## Aim

This paper tracks CoilLinear, CoilRA, MultiCoil RoPE, periodic activations, and MLX-first benchmarks. The shared idea is to use cyclic or block-cyclic structure where a model already has phase, channel grouping, low-rank adaptation, or positional rotation structure.

The current formal seed is `COMMON-0030`, the adapter block index

```text
adapter_block(block_size,channel) = channel mod block_size
```

for positive block sizes. This is a block/cyclic channel-index primitive, not a LoRA replacement theorem or a MultiCoil RoPE theorem.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/lean/PaperAI03.lean
```

The Python examples are:

```text
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/test_adapter_block_examples.py
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_adapter_block.py
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_adapter_parameter_budget.py
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_multicoil_rope.py
sidecars/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE/python/benchmark_rope_relative_phase.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks adapter-block examples; Lean declarations determine proof status.

## Theorem Spine

- `AIRA-T0001`: `Circle.Applications.adapterBlock_lt_blockSize`
- `AIRA-T0002`: `Circle.Applications.adapterBlock_add_blockSize`
- `AIRA-T0003`: `Circle.Applications.adapterBlock_zero`
- `AIRA-T0004`: `Circle.Applications.adapterBlock_add_mul_blockSize`
- `AIRA-T0005`: `Circle.Applications.adapterBlock_idempotent`

## Proved Core

`AIRA-T0001` proves that the adapter block index is bounded by the positive block size. `AIRA-T0002` proves closure after one full block pass, `AIRA-T0004` proves closure after any whole number of full block passes, `AIRA-T0005` proves that normalizing an adapter block index twice is the same as normalizing it once, and `AIRA-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts certify only block indexing. They do not prove parameter efficiency, better fine-tuning, RoPE improvement, periodic-activation value, or runtime gains.

## Exploratory Benchmark Fixture

`AIRA-B0001` adds a deterministic adapter-block benchmark fixture. The positive synthetic task labels channels by adapter block, so an adapter-block lookup recovers the pattern while constant and scalar-threshold baselines do worse. The negative control labels channels by an ordinary scalar threshold; there the threshold baseline wins and the adapter-block lookup fails.

The fixture also reports block collision diagnostics: how many training channels collide into already-used adapter blocks and the maximum block load. Those diagnostics are useful for later CoilRA and block-cyclic adapter tests because aliasing is a real design constraint, not just a visualization detail.

This fixture is not evidence that CoilRA improves fine-tuning, that block-cyclic adapters beat LoRA, that MultiCoil RoPE improves positional encoding, or that a model runs faster. It is a small reproducible harness that separates a block-periodic task from a nonperiodic control before stronger experiments begin.

`AIRA-B0004` adds a deterministic adapter parameter-budget fixture. It compares a dense per-channel adapter count, a LoRA-style low-rank count, and a block-cyclic shared-table count, then reports alias/load diagnostics for `channel mod block_size`.

This fixture is only parameter accounting. It is not evidence that block-cyclic adapters improve fine-tuning, that fewer parameters improve quality, that LoRA is beaten, or that runtime/memory/training stability improves.

`AIRA-B0002` adds the first MultiCoil/RoPE-style positional fixture. The positive synthetic task labels positions by a combined phase tuple over periods `(5,7)`. A combined-period lookup recovers the pattern, while a single-period phase lookup, a constant baseline, and a scalar-threshold baseline do worse. The nonperiodic control labels positions by a scalar threshold; there the threshold baseline wins and the combined-period lookup fails.

This fixture is not evidence that MultiCoil RoPE improves a language model, that multiple periods beat standard RoPE, that learned positional encodings are unnecessary, or that attention should be replaced. It is a small reproducible check that multi-period phase structure can be represented and compared before real model experiments begin.

`AIRA-B0003` adds a RoPE-style relative phase fixture. The positive synthetic task labels query/key pairs by their relative lag modulo a true period. A correct-period relative phase lookup recovers the pattern; wrong-period relative lookup, query-position lookup, and scalar-threshold baselines remain weaker. The nonperiodic control labels pairs by the query index, where the scalar threshold baseline wins.

This fixture is not evidence that standard RoPE improves a model, that relative phase solves attention quality, or that a language model has better context behavior. It is a small test that the relative-position claim is being represented and compared before stronger RoPE experiments begin.

## Prototype Program

`CoilLinear` should test circulant and block-circulant layers against dense layers on tasks where convolutional or periodic structure is plausible.

`CoilRA` should test cyclic/block-cyclic adapters against dense adapters, LoRA, and block-circulant baselines. Metrics should include quality, parameter count, inference cost, training stability, and MLX runtime on this Mac.

`MultiCoil RoPE` should test multiple periods, coprime phases, winding-aware features, and torus-valued position views against standard RoPE and learned positional baselines.

Periodic activations should be evaluated on signal, coordinate, and neural-field tasks where periodicity is real.

## Next Program

- Treat `AIRA-B0001` as adapter-block benchmark scaffolding and `AIRA-B0004` as parameter-budget scaffolding only; CoilRA, model quality, parameter efficiency, memory, training stability, and runtime claims remain separate work.
- Treat `AIRA-B0002` as MultiCoil/RoPE-style positional scaffolding and `AIRA-B0003` as relative RoPE-style phase scaffolding only; standard RoPE, learned-position, attention, dense sequence, and MLX comparisons remain separate work.
- Start with small MLX prototypes and synthetic tasks.
- Compare against dense, LoRA, block-circulant, and standard RoPE baselines.
- Measure quality, memory, training stability, and runtime together; parameter reduction alone is not enough.
- Keep spherical/quaternion AI separate and keep octonion AI exploratory.

## Guardrail

Prime and coprime reasoning must be balanced with hardware-friendly smooth sizes. Do not optimize mathematical elegance at the expense of kernels that can actually run well.
