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
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks adapter-block examples; Lean declarations determine proof status.

## Theorem Spine

- `AIRA-T0001`: `Circle.Applications.adapterBlock_lt_blockSize`
- `AIRA-T0002`: `Circle.Applications.adapterBlock_add_blockSize`
- `AIRA-T0003`: `Circle.Applications.adapterBlock_zero`
- `AIRA-T0004`: `Circle.Applications.adapterBlock_add_mul_blockSize`

## Proved Core

`AIRA-T0001` proves that the adapter block index is bounded by the positive block size. `AIRA-T0002` proves closure after one full block pass, `AIRA-T0004` proves closure after any whole number of full block passes, and `AIRA-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These facts certify only block indexing. They do not prove parameter efficiency, better fine-tuning, RoPE improvement, periodic-activation value, or runtime gains.

## Prototype Program

`CoilLinear` should test circulant and block-circulant layers against dense layers on tasks where convolutional or periodic structure is plausible.

`CoilRA` should test cyclic/block-cyclic adapters against dense adapters, LoRA, and block-circulant baselines. Metrics should include quality, parameter count, inference cost, training stability, and MLX runtime on this Mac.

`MultiCoil RoPE` should test multiple periods, coprime phases, winding-aware features, and torus-valued position views against standard RoPE and learned positional baselines.

Periodic activations should be evaluated on signal, coordinate, and neural-field tasks where periodicity is real.

## Next Program

- Treat `AIA-B0001` as phase-channel benchmark scaffolding only; adapter, CoilRA, and MultiCoil RoPE benchmarks remain separate work.
- Start with small MLX prototypes and synthetic tasks.
- Compare against dense, LoRA, block-circulant, and standard RoPE baselines.
- Measure quality and runtime together; parameter reduction alone is not enough.
- Keep spherical/quaternion AI separate and keep octonion AI exploratory.

## Guardrail

Prime and coprime reasoning must be balanced with hardware-friendly smooth sizes. Do not optimize mathematical elegance at the expense of kernels that can actually run well.
