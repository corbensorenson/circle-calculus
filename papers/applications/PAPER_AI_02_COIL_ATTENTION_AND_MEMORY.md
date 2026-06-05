# Circle Calculus AI 2: Coil Attention and Memory

Status: draft with a proved cyclic memory-slot seed.

## Aim

Explore Coil Attention, CoilKV, long-context retrieval, alias control, stride/orbit coverage, and cyclic memory.

The current formal seed is `COMMON-0028`, the cyclic memory slot

```text
memory_slot(bank_size,token) = token mod bank_size
```

for positive memory-bank sizes. This is a memory indexing primitive, not a retrieval-quality or no-aliasing theorem.

## Theorem Spine

- `AIM-T0001`: for positive bank size, the memory slot is bounded by the bank size. Lean declaration: `Circle.Applications.memorySlot_lt_bankSize`.
- `AIM-T0002`: for positive bank size, adding one full bank size preserves the memory slot. Lean declaration: `Circle.Applications.memorySlot_add_bankSize`.
- `AIM-T0003`: the memory slot at zero is zero. Lean declaration: `Circle.Applications.memorySlot_zero`.

The Python sidecar checks the same finite examples. Coil Attention and CoilKV claims still require synthetic long-context retrieval benchmarks and comparisons against full attention, sparse attention, long convolution, and state-space baselines.

## Next Program

- Start with synthetic long-context retrieval.
- Compare against full attention, sliding-window, sparse attention, Hyena-like mixers, and state-space baselines.
- Track aliasing and closure failures explicitly.

## Guardrail

Do not replace all attention with fixed circles; start with hybrid local, global, coil, and content-gated components.
