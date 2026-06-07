# Circle Calculus AI 2: Coil Attention and Memory

Status: polished draft with a proved cyclic memory-slot seed.

## Aim

This paper tracks Coil Attention, CoilKV, long-context retrieval, alias control, stride/orbit coverage, cyclic memory, and looped/recursive transformer recurrence schedules. The goal is not to replace all attention with fixed circles. The serious target is a hybrid system where local attention, global/content-gated attention, selected coil paths, and auditable recurrence schedules work together.

The current formal seed is `COMMON-0028`, the cyclic memory slot

```text
memory_slot(bank_size,token) = token mod bank_size
```

for positive memory-bank sizes. This is a memory indexing primitive, not a retrieval-quality or no-aliasing theorem.

`COMMON-0052` through `COMMON-0054` add the planned looped/recursive transformer lane: recurrence schedules, loop-exit certificates, and overthinking guardrails. These are roadmap vocabulary terms, not proved architecture results. The research source note is:

```text
circle_calculus_codex_handoff/source_logs/06_looped_recursive_transformer_research.md
```

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/lean/PaperAI02.lean
```

The Python examples are:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/test_memory_slot_examples.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_memory_slot.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_coil_retrieval.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks cyclic memory-slot examples; Lean declarations determine proof status. The looped/recursive transformer source review is archived in the handoff source log; it does not change theorem status.

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

## Exploratory Benchmark Fixture

`AIM-B0001` adds a deterministic cyclic-memory fixture. The positive synthetic task labels tokens by memory slot, so a slot lookup recovers the pattern while constant and scalar-threshold baselines do worse. The negative control labels tokens by an ordinary scalar threshold; there the threshold baseline wins and the memory-slot lookup fails.

The fixture also records collision diagnostics: how many training tokens alias into already-used slots and the maximum training load of a slot. These are executable checks for the benchmark harness only. They are not evidence that cyclic memory improves language modeling, retrieval, attention, or long-context scaling.

`AIM-B0002` adds a deterministic coil-retrieval reachability fixture. The positive synthetic task has a known dependency lag that is reachable by the selected coil path but not by the local-window or wrong-stride baselines. The full-attention candidate set is included as an oracle upper bound. The near-lag control reverses the story: local attention reaches the dependency while the selected coil path misses it.

This fixture checks candidate-set reachability only. It is not evidence that Coil Attention improves model quality, that fixed coils replace full attention, that alias behavior is solved, or that a model runs faster.

## Looped And Recursive Transformer Program

Recent looped and recursive transformer work makes recurrence depth an active modeling axis: a model can reuse blocks through multiple loop steps, add memory tokens, exit at loop boundaries, use sparse/MoE routing across passes, or retrofit damped recurrence at inference time. Circle Calculus can contribute only if it makes the schedule explicit and testable.

The Circle version should treat a loop step as a finite phase and every recurrence pass as a recorded state transition:

```text
input state
  -> shared block at loop phase t
  -> recurrence state
  -> exit/continue decision
  -> score trace and overthinking boundary
```

The planned first fixture should compare fixed-depth, fixed-loop, adaptive-exit, over-looped, recurrent-memory, sparse/MoE, state-space, and dense baselines on a deterministic task. It should record when extra recurrence helps, does nothing, or degrades the metric. Lean theorem targets should stay at finite phase, budget, and closure facts unless a stronger formal model is introduced.

This is the potential semi-novel Circle contribution: proof/manifest-linked recurrence provenance and loop-exit certificates around a looped transformer, not a claim that Circle Math has already built a better recursive language model.

## Prototype Program

The next benchmark should be synthetic long-context retrieval where the target dependency is known. A useful comparison set is:

```text
full attention
sliding-window attention
dilated/sparse attention
BigBird-like sparse attention
Hyena-like long convolution
S4/Mamba-like state-space baselines
Universal Transformer and fixed looped-transformer baselines
adaptive early-exit and recurrent-memory baselines
RWKV/Mamba-style recurrent/state-space baselines
Coil Attention plus CoilKV
```

Measurements should include accuracy, sequence length scaling, memory use, runtime, collision rate, alias behavior, and failure cases where coil slots overwrite useful information.

## Next Program

- Treat `AIM-B0001` as cyclic-memory benchmark scaffolding only.
- Treat `AIM-B0002` as coil-retrieval reachability scaffolding only; learned/content-gated retrieval quality remains separate work.
- Treat `COMMON-0052` through `COMMON-0054` as looped/recursive transformer roadmap vocabulary only; recurrence-schedule benchmarks remain to be built.
- Test fixed, learned, and content-gated coil paths separately.
- Add recurrence schedule, loop-exit certificate, and overthinking-boundary fixtures with dense, Universal Transformer, fixed-loop, adaptive-exit, recurrent-memory, sparse/MoE, RWKV/Mamba-style, and state-space baselines.
- Track gcd/orbit coverage and aliasing explicitly.
- Add local/global attention fallbacks before claiming a practical model.
- Keep MLX/Mac-compatible experiments first.

## Guardrail

Do not replace all attention with fixed circles. A cyclic memory slot is a proved address primitive, not a proof that cyclic memory is sufficient for language modeling or retrieval. A looped recurrence schedule is not a proof of reasoning quality, context length, speed, or parameter efficiency.
