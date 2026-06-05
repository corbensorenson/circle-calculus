# Circle Calculus AI 3: CoilRA and MultiCoil RoPE

Status: draft with a proved adapter-block seed.

## Aim

Explore CoilLinear, CoilRA, MultiCoil RoPE, periodic activations, and MLX-first benchmarks.

The current formal seed is `COMMON-0030`, the adapter block index

```text
adapter_block(block_size,channel) = channel mod block_size
```

for positive block sizes. This is a block/cyclic channel-index primitive, not a LoRA replacement theorem or a MultiCoil RoPE theorem.

## Theorem Spine

- `AIRA-T0001`: for positive block size, the adapter block index is bounded by the block size. Lean declaration: `Circle.Applications.adapterBlock_lt_blockSize`.
- `AIRA-T0002`: for positive block size, adding one full block size preserves the adapter block index. Lean declaration: `Circle.Applications.adapterBlock_add_blockSize`.

The Python sidecar checks the same finite examples. CoilRA, CoilLinear, MultiCoil RoPE, and periodic-activation claims still require MLX-first benchmarks against dense adapters, LoRA, block-circulant layers, and standard RoPE.

## Next Program

- Compare against dense adapters, LoRA, block-circulant layers, and standard RoPE.
- Measure quality, parameter count, inference cost, and runtime.
- Keep octonion AI exploratory until the S7 algebra and benchmarks justify it.

## Guardrail

Prime/coprime reasoning must be balanced with hardware-friendly sizes.
