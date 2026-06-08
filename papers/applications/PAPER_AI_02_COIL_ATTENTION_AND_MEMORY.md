# Circle Calculus AI 2: Coil Attention and Memory

Status: polished draft with proved cyclic memory-slot and finite loop-schedule seeds.

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
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_content_gated_retrieval.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_content_gate_retrieval.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_looped_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_token_level_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_token_level_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_training_free_loop_wrapper.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_middle_block_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_middle_block_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_multi_resolution_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_multi_resolution_recurrence.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_learned_recurrence_schedule.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks cyclic memory-slot examples; Lean declarations determine proof status. The looped/recursive transformer source review is archived in the handoff source log; it does not change theorem status.

## Theorem Spine

- `AIM-T0001`: `Circle.Applications.memorySlot_lt_bankSize`
- `AIM-T0002`: `Circle.Applications.memorySlot_add_bankSize`
- `AIM-T0003`: `Circle.Applications.memorySlot_zero`
- `AIM-T0004`: `Circle.Applications.memorySlot_add_mul_bankSize`
- `AIM-T0005`: `Circle.Applications.memorySlot_idempotent`
- `AIM-T0006`: `Circle.Applications.loopRequiredSteps_pos`
- `AIM-T0007`: `Circle.Applications.loopRequiredSteps_le_loopPeriod`
- `AIM-T0008`: `Circle.Applications.loopRequiredSteps_add_loopPeriod`
- `AIM-T0009`: `Circle.Applications.tokenRecurrenceBudget_add_loopPeriod`
- `AIM-T0010`: `Circle.Applications.trainingFreeLoopBudget_le_maxLoops`
- `AIM-T0011`: `Circle.Applications.trainingFreeLoopBudget_le_requiredSteps`
- `AIM-T0012`: `Circle.Applications.loopOverthinkingBoundary_ge_required`
- `AIM-T0013`: `Circle.Applications.loopExitAvailable_of_loopPeriod_le_budget`
- `AIM-T0014`: `Circle.Applications.loopExitAvailable_add_loopPeriod`
- `AIM-T0015`: `Circle.Applications.loopExitCertificate_exit_eq_required`
- `AIM-T0016`: `Circle.Applications.loopExitCertificate_within_budget`
- `AIM-T0017`: `Circle.Applications.loopExitCertificate_within_guardrail`
- `AIM-T0018`: `Circle.Applications.tokenRecurrenceBudget_le_loopPeriod`
- `AIM-T0019`: `Circle.Applications.trainingFreeLoopBudget_add_loopPeriod`
- `AIM-T0020`: `Circle.Applications.trainingFreeLoopBudget_eq_required_of_available`
- `AIM-T0021`: `Circle.Applications.loopOverthinkingBoundary_add_loopPeriod`
- `AIM-T0022`: `Circle.Applications.tokenRecurrenceBudget_pos`
- `AIM-T0023`: `Circle.Applications.trainingFreeLoopBudget_pos_of_available`
- `AIM-T0024`: `Circle.Applications.loopExitCertificate_exit_pos`
- `AIM-T0025`: `Circle.Applications.trainingFreeLoopBudget_eq_max_of_unavailable`
- `AIM-T0026`: `Circle.Applications.loopRequiredSteps_add_mul_loopPeriod`
- `AIM-T0027`: `Circle.Applications.tokenRecurrenceBudget_add_mul_loopPeriod`
- `AIM-T0028`: `Circle.Applications.trainingFreeLoopBudget_add_mul_loopPeriod`
- `AIM-T0029`: `Circle.Applications.loopOverthinkingBoundary_add_mul_loopPeriod`
- `AIM-T0030`: `Circle.Applications.loopExitAvailable_add_mul_loopPeriod`
- `AIM-T0031`: `Circle.Applications.loopExitCertificate_exit_available`
- `AIM-T0032`: `Circle.Applications.loopExitCertificate_budget_eq_exitStep`
- `AIM-T0033`: `Circle.Applications.loopExitCertificate_exitStep_add_mul_loopPeriod`
- `AIM-T0034`: `Circle.Applications.loopExitCertificate_boundary_add_mul_loopPeriod`
- `AIM-T0035`: `Circle.Applications.tokenActiveAtStep_one`
- `AIM-T0036`: `Circle.Applications.tokenActiveAtStep_add_mul_loopPeriod`
- `AIM-T0037`: `Circle.Applications.tokenActiveAtStep_step_le_loopPeriod`
- `AIM-T0038`: `Circle.Applications.tokenInactiveAtStep_of_loopPeriod_lt_step`

## Proved Core

`AIM-T0001` proves that the memory slot is bounded by the positive bank size. `AIM-T0002` proves closure after one full memory-bank pass:

```text
memorySlot bankSize (token + bankSize) =
  memorySlot bankSize token
```

`AIM-T0004` proves closure after any whole number of full memory-bank passes. `AIM-T0005` proves that normalizing a memory slot twice is the same as normalizing it once. `AIM-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

`AIM-T0006` through `AIM-T0038` prove finite loop-schedule, token-active-set, and loop-exit certificate facts: required loop depth is positive, bounded by a positive loop period, periodic under one full loop-period shift, and invariant under any whole number of loop-period passes; token recurrence budgets are positive, have the same one-period and multi-pass closure behavior, and are bounded by the loop period; token active-step membership includes the first loop step, is invariant under whole loop-period token shifts, is bounded by the loop period, and excludes steps beyond that period; the training-free wrapper budget is capped by `maxLoops` and by the required depth, is periodic, is invariant under whole loop-period passes, selects the exact positive required depth when an exit is available, and clamps to `maxLoops` when no exit is available; overthinking boundaries are at least the required depth and share the same one-period and multi-pass closure; exit availability is guaranteed when the loop budget covers the full period and is invariant under one or many loop-period passes; and a loop-exit certificate records a positive exact required step, budget bound, guardrail bound, implied exit availability, equality between the selected wrapper budget and the certified exit step, and multi-pass invariance of the certified exit step and guardrail boundary.

These theorems certify cyclic slot addresses and finite loop-budget arithmetic only. They do not prove retrieval quality, alias control, attention replacement, recursive reasoning, runtime, memory use, parameter efficiency, or long-context scaling.

## Exploratory Benchmark Fixture

`AIM-B0001` adds a deterministic cyclic-memory fixture. The positive synthetic task labels tokens by memory slot, so a slot lookup recovers the pattern while constant and scalar-threshold baselines do worse. The negative control labels tokens by an ordinary scalar threshold; there the threshold baseline wins and the memory-slot lookup fails.

The fixture also records collision diagnostics: how many training tokens alias into already-used slots and the maximum training load of a slot. These are executable checks for the benchmark harness only. They are not evidence that cyclic memory improves language modeling, retrieval, attention, or long-context scaling.

`AIM-B0002` adds a deterministic coil-retrieval reachability fixture. The positive synthetic task has a known dependency lag that is reachable by the selected coil path but not by the local-window or wrong-stride baselines. The full-attention candidate set is included as an oracle upper bound. The near-lag control reverses the story: local attention reaches the dependency while the selected coil path misses it.

This fixture checks candidate-set reachability only. It is not evidence that Coil Attention improves model quality, that fixed coils replace full attention, that alias behavior is solved, or that a model runs faster.

`AIM-B0004` adds a deterministic content-gated retrieval fixture. It mixes two dependency types: even-indexed queries need a long lag reached by the selected coil path, while odd-indexed queries need a near lag reached by the local window. The content-gated route chooses coil or local candidates according to that fixture signal. Static coil and static local baselines each solve only half of the mixed task; a wrong-gate control fails; union and full-attention baselines solve the task with larger candidate budgets.

This fixture checks routing reachability and candidate budget only. It is not evidence that a learned gate works, that attention quality improves, that context length improves, or that inference is faster.

`AIM-B0010` adds a deterministic learned content-gate retrieval fixture. It fits a phase-to-route lookup table from training queries, then uses that learned table to choose coil or local candidates on held-out queries. The fixture reports route accuracy, retrieval reachability, static coil/local baselines, wrong-period and flipped-gate controls, union and full-attention baselines, and candidate-budget diagnostics.

This fixture checks whether the benchmark harness can learn a constructed finite route table. It is not evidence that a neural learned gate improves retrieval quality, attention quality, context length, memory use, runtime, or parameter efficiency.

`AIM-B0003` adds a deterministic looped-recurrence schedule fixture. The positive synthetic task assigns each sample a required recurrence depth. The fixture compares single-pass, fixed-loop, adaptive-exit, recurrent-memory, sparse phase-router, and over-looped controls. The adaptive-exit and recurrent-memory controls can retain the successful intermediate step; the over-looped control deliberately demonstrates degradation after the overthinking boundary. A nonperiodic scalar-threshold control checks that loop phase is not treated as useful when the target is ordinary scalar structure.

This fixture checks schedule bookkeeping only. It is not evidence that looped transformers improve reasoning, language-model quality, context length, runtime, memory use, or parameter efficiency.

`AIM-B0011` adds a deterministic loop-exit certificate fixture for one synthetic sample plus a fixed-budget no-exit control. It records required depth, score trace, exit availability, whether the exit is within budget, and whether the exit stays within the overthinking guardrail.

This fixture checks certificate bookkeeping only. It is not evidence that adaptive exit improves reasoning, language-model quality, context length, runtime, memory use, or parameter efficiency.

`AIM-B0005` adds a deterministic token-level recurrence routing fixture. It records per-token recurrence budgets, active-token counts by loop step, a selected middle-block range, alternating coarse/fine resolution labels, a fixed global-budget baseline, a wrong-budget control, an over-loop control, and a nonperiodic scalar-threshold control.

This fixture checks routing bookkeeping only. It is not evidence that token-level recursive transformers improve reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0012` adds a deterministic learned token-level recurrence fixture. It fits a phase-to-budget lookup table from training tokens, applies that learned table to held-out tokens, and compares it against fixed-budget, wrong-period, shifted-budget, over-loop, and nonperiodic scalar-threshold controls.

This fixture checks whether the benchmark harness can learn a constructed token-level budget table. It is not evidence that learned token routers improve reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0006` adds a deterministic training-free loop-wrapper fixture. It uses circular phase as a fixed loop-budget prior and compares that wrapper against single-pass, fixed-loop, wrong-period, over-loop, and nonperiodic scalar-threshold baselines. The benchmark supports CPU scoring and optional MLX scoring through the same accuracy interface.

This fixture checks loop-budget bookkeeping only. It is not evidence that training-free recurrence improves reasoning, language-model quality, context length, runtime, memory use, or parameter efficiency.

`AIM-B0007` adds a deterministic middle-block recurrence fixture. It records a selected loop-block range, the required block and recurrence budget for each sample, and compares selected-block scheduling against full-block, fixed-budget, wrong-block, and over-loop controls with block-pass accounting.

This fixture checks block and budget bookkeeping only. It is not evidence that looping a middle block improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0013` adds a deterministic learned middle-block recurrence fixture. It fits one phase-to-block lookup table and one phase-to-budget lookup table from training samples, applies both tables to held-out samples, and compares the learned route against selected-band, full-block, fixed-budget, wrong block-period, wrong budget-period, wrong-block, and over-loop controls with block-pass accounting.

This fixture checks whether the benchmark harness can learn a constructed finite block-and-budget routing table. It is not evidence that learned middle-block recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0008` adds a deterministic multi-resolution recurrence fixture. It records required loop budgets, required coarse/fine resolution labels, active sample counts by loop step, and compares phase-routed multi-resolution scheduling against single-resolution, fixed-budget, wrong-resolution, and over-loop controls.

This fixture checks budget and resolution bookkeeping only. It is not evidence that compressed/full-resolution recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0014` adds a deterministic learned multi-resolution recurrence fixture. It fits one phase-to-budget lookup table and one phase-to-resolution lookup table from training samples, applies both tables to held-out samples, and compares the learned route against single-resolution, fixed-budget, wrong budget-period, wrong resolution-period, and over-loop controls.

This fixture checks whether the benchmark harness can learn a constructed finite budget-and-resolution routing table. It is not evidence that learned multi-resolution recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0009` adds a deterministic learned recurrence-schedule fixture. It fits a phase-to-loop-budget lookup table from training examples, then compares that learned schedule against fixed-budget, wrong-period, and over-loop controls.

This fixture checks whether the benchmark harness can learn a constructed finite schedule table. It is not evidence that learned recursive transformers improve reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

## Looped And Recursive Transformer Program

Recent looped and recursive transformer work makes recurrence depth an active modeling axis: a model can reuse blocks through multiple loop steps, add memory tokens, exit at loop boundaries, route different tokens to different recursion depths, loop only a middle block, recurse over compressed and full-resolution views, use sparse/MoE routing across passes, or retrofit damped recurrence at inference time. Circle Calculus can contribute only if it makes the schedule explicit and testable.

The Circle version should treat a loop step as a finite phase and every recurrence pass as a recorded state transition:

```text
input state
  -> shared block at loop phase t
  -> active token set / resolution level
  -> recurrence state
  -> exit/continue decision
  -> score trace and overthinking boundary
```

The first fixture is now `AIM-B0003`. It compares fixed-depth, fixed-loop, adaptive-exit, over-looped, recurrent-memory, sparse phase-router, and dense-threshold controls on a deterministic task. `AIM-B0005` adds the token-level view: different tokens can carry different loop budgets, a selected middle block is recorded, active-token counts shrink by loop step, and wrong/over-loop controls stay explicit. `AIM-B0012` adds the learned token-level view: a tiny phase-to-budget lookup is fit from training tokens, applied to held-out tokens, and checked against fixed, wrong-period, shifted-budget, over-loop, and nonperiodic controls. `AIM-B0006` adds the training-free wrapper view: reuse a block according to a fixed circular phase budget, then compare against ordinary fixed, wrong-period, over-loop, and scalar-threshold controls. `AIM-B0007` adds the middle-block view: selected loop-block scheduling is compared against full-block, fixed-budget, wrong-block, and over-loop controls. `AIM-B0013` adds the learned middle-block view: phase-to-block and phase-to-budget lookups are fit from training samples, applied to held-out samples, and compared against selected-band, full-block, fixed-budget, wrong-period, wrong-block, and over-loop controls. `AIM-B0008` adds the multi-resolution view: phase-routed coarse/fine scheduling is compared against single-resolution, fixed-budget, wrong-resolution, and over-loop controls. `AIM-B0014` adds the learned multi-resolution view: phase-to-budget and phase-to-resolution lookups are fit from training samples, applied to held-out samples, and compared against single-resolution, fixed-budget, wrong-period, and over-loop controls. `AIM-B0009` adds the learned-schedule view: a tiny phase-to-budget lookup is fit from examples and compared against fixed-budget, wrong-period, and over-loop controls. `AIM-B0010` adds the learned coil/local route view: a tiny phase-to-route lookup is fit from examples and compared against static, wrong-period, flipped-gate, union, and full-attention controls. Lean theorem targets should stay at finite phase, budget, route, and closure facts unless a stronger formal model is introduced.

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
- Treat `AIM-B0004` as content-gated route scaffolding only; learned gates, attention quality, context length, runtime, and memory-scaling claims remain separate work.
- Treat `AIM-B0010` as learned route-table scaffolding only; neural learned gates, retrieval quality, context length, runtime, and memory-scaling claims remain separate work.
- Treat `AIM-B0003` as looped/recursive transformer schedule scaffolding only; learned recursive model quality remains separate work.
- Treat `AIM-B0011` as loop-exit certificate scaffolding only; adaptive-exit quality, reasoning, runtime, and throughput claims remain separate work.
- Treat `AIM-B0005` as token-level recurrence routing scaffolding only; learned token routers, middle-block recurrence, multi-resolution recurrence, training-free loop wrappers, model quality, runtime, memory, and throughput claims remain separate work.
- Treat `AIM-B0012` as learned token-level recurrence scaffolding only; neural token routers, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Treat `AIM-B0006` as training-free loop-wrapper scaffolding only; learned recurrence, real model quality, runtime, memory, throughput, and reasoning claims remain separate work.
- Treat `AIM-B0007` as middle-block recurrence scaffolding only; neural learned block routers, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Treat `AIM-B0013` as learned middle-block recurrence scaffolding only; neural block routers, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Treat `AIM-B0008` as multi-resolution recurrence scaffolding only; learned multi-resolution recurrence, compressed/full-resolution routing, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Treat `AIM-B0014` as learned multi-resolution recurrence scaffolding only; neural compressed/full-resolution routing, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Treat `AIM-B0009` as learned recurrence-schedule scaffolding only; learned recursive transformer quality, throughput, memory, context length, perplexity, and reasoning claims remain separate work.
- Test fixed, learned, and content-gated coil paths separately.
- Expand recurrence schedule, loop-exit certificate, and overthinking-boundary fixtures toward dense, Universal Transformer, fixed-loop, adaptive-exit, recurrent-memory, token-level Mixture-of-Recursions, sparse/MoE, RWKV/Mamba-style, and state-space baseline implementations.
- Track gcd/orbit coverage and aliasing explicitly.
- Add local/global attention fallbacks before claiming a practical model.
- Keep MLX/Mac-compatible experiments first.

## Guardrail

Do not replace all attention with fixed circles. A cyclic memory slot is a proved address primitive, not a proof that cyclic memory is sufficient for language modeling or retrieval. A looped recurrence schedule is not a proof of reasoning quality, context length, speed, or parameter efficiency.
