# Circle Calculus AI 2: Coil Attention and Memory

Status: polished draft with a proved cyclic memory-slot seed.

## Aim

This paper tracks Coil Attention, CoilKV, long-context retrieval, alias control, stride/orbit coverage, and cyclic memory. The goal is not to replace all attention with fixed circles. The serious target is a hybrid system where local attention, global/content-gated attention, and selected coil paths work together.

The current formal seed is `COMMON-0028`, the cyclic memory slot

```text
memory_slot(bank_size,token) = token mod bank_size
```

for positive memory-bank sizes. This is a memory indexing primitive, not a retrieval-quality or no-aliasing theorem.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/lean/PaperAI02.lean
```

The Python examples are:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/test_memory_slot_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks cyclic memory-slot examples; Lean declarations determine proof status.

## Theorem Spine

- `AIM-T0001`: `Circle.Applications.memorySlot_lt_bankSize`
- `AIM-T0002`: `Circle.Applications.memorySlot_add_bankSize`
- `AIM-T0003`: `Circle.Applications.memorySlot_zero`
- `AIM-T0004`: `Circle.Applications.memorySlot_add_mul_bankSize`
- `AIM-T0005`: `Circle.Applications.memorySlot_idempotent`

## Proved Core

`AIM-T0001` proves that the memory slot is bounded by the positive bank size. `AIM-T0002` proves closure after one full memory-bank pass:

```text
memorySlot bankSize (token + bankSize) =
  memorySlot bankSize token
```

`AIM-T0004` proves closure after any whole number of full memory-bank passes. `AIM-T0005` proves that normalizing a memory slot twice is the same as normalizing it once. `AIM-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

These theorems certify the cyclic slot address only. They do not prove retrieval quality, alias control, attention replacement, or long-context scaling.

## Prototype Program

The first benchmark should be synthetic long-context retrieval where the target dependency is known. A useful comparison set is:

```text
full attention
sliding-window attention
dilated/sparse attention
BigBird-like sparse attention
Hyena-like long convolution
S4/Mamba-like state-space baselines
Coil Attention plus CoilKV
```

Measurements should include accuracy, sequence length scaling, memory use, runtime, collision rate, alias behavior, and failure cases where coil slots overwrite useful information.

## Next Program

- Treat `AIA-B0001` as phase-channel benchmark scaffolding only; cyclic-memory retrieval still needs its own fixture.
- Test fixed, learned, and content-gated coil paths separately.
- Track gcd/orbit coverage and aliasing explicitly.
- Add local/global attention fallbacks before claiming a practical model.
- Keep MLX/Mac-compatible experiments first.

## Guardrail

Do not replace all attention with fixed circles. A cyclic memory slot is a proved address primitive, not a proof that cyclic memory is sufficient for language modeling or retrieval.
