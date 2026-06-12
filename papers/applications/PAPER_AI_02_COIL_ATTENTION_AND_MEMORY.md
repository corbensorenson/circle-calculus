# Circle Calculus AI 2: Coil Attention and Memory

Status: polished draft with proved cyclic memory-slot, finite loop-schedule, and sparse-attention coverage seeds.

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
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_coil_retrieval.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_content_gated_retrieval.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_hybrid_sparse_attention.py
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py
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
- `AIM-T0059`: `Circle.Applications.kvCacheSlot_lt_cacheSize`
- `AIM-T0060`: `Circle.Applications.kvCacheSlot_add_cacheSize`
- `AIM-T0061`: `Circle.Applications.kvCacheSlotCollision_iff_gap_dvd`
- `AIM-T0062`: `Circle.Applications.kvCacheSlot_ne_of_positive_gap_lt_cache`
- `AIM-T0063`: `Circle.Applications.kvCacheWindow_nextOverwrite_after_current`
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
- `AIM-T0039`: `Circle.Applications.middleBlockRoute_ge_start`
- `AIM-T0040`: `Circle.Applications.middleBlockRoute_lt_stop`
- `AIM-T0041`: `Circle.Applications.middleBlockRoute_add_width`
- `AIM-T0042`: `Circle.Applications.middleBlockRoute_add_mul_width`
- `AIM-T0043`: `Circle.Applications.middleBlockRoute_zero`
- `AIM-T0044`: `Circle.Applications.middleBlockBudgetRoute_block_ge_start`
- `AIM-T0045`: `Circle.Applications.middleBlockBudgetRoute_block_lt_stop`
- `AIM-T0046`: `Circle.Applications.middleBlockBudgetRoute_budget_pos`
- `AIM-T0047`: `Circle.Applications.middleBlockBudgetRoute_budget_le_loopPeriod`
- `AIM-T0048`: `Circle.Applications.middleBlockBudgetRoute_add_commonCycle`
- `AIM-T0056`: `Circle.Applications.middleBlockBudgetRoute_add_mul_commonCycle`
- `AIM-T0057`: `Circle.Applications.tokenRecurrenceBudget_zero`
- `AIM-T0058`: `Circle.Applications.middleBlockBudgetRoute_zero`
- `AIM-T0049`: `Circle.Applications.loopedRecurrentState_lt_period`
- `AIM-T0050`: `Circle.Applications.loopedRecurrentState_one_zero`
- `AIM-T0051`: `Circle.Applications.loopedRecurrentState_of_requiredSteps`
- `AIM-T0052`: `Circle.Applications.loopedRecurrentState_of_tokenRecurrenceBudget`
- `AIM-T0053`: `Circle.Applications.loopedRecurrentState_tokenBudget_add_mul_loopPeriod`
- `AIM-T0054`: `Circle.Applications.loopedRecurrentState_budget_add_period`
- `AIM-T0055`: `Circle.Applications.loopedRecurrentState_budget_add_mul_period`
- `AIT-T0001`: `Circle.Applications.attentionReach_eq_div_gcd`
- `AIT-T0002`: `Circle.Applications.stridedHead_fullCoverage_iff_coprime`
- `AIT-T0003`: `Circle.Applications.stridedHead_fullCoverage_of_coprime`
- `AIT-T0010`: `Circle.Applications.localLagReach_of_le`
- `AIT-T0011`: `Circle.Applications.coilLagReach_of_step`
- `AIT-T0012`: `Circle.Applications.coilLagReach_add_context`
- `AIT-T0013`: `Circle.Applications.hybridLagReach_of_local`
- `AIT-T0014`: `Circle.Applications.hybridLagReach_of_coil`
- `AIT-T0015`: `Circle.Applications.coilStrideFamilyLagReach_of_member_step`
- `AIT-T0016`: `Circle.Applications.coilStrideFamilyLagReach_add_context`
- `AIT-T0017`: `Circle.Applications.hybridFamilyLagReach_of_local`
- `AIT-T0018`: `Circle.Applications.hybridFamilyLagReach_of_family`
- `AIT-T0019`: `Circle.Applications.hybridFamilyLagReach_of_member_step`
- `AIT-T0020`: `Circle.Applications.hybridFamilyLagGap_iff_not_local_and_not_family`

## Strided Attention Coverage (Proved Structural Guarantee)

A strided ("coil") attention head with stride `k` lets each token attend to positions
`i, i±k, i±2k, …` — exactly a coil orbit on `C n`. Its reachability is therefore governed
by the finite-circle orbit/period theory, which gives a **proved design rule** for sparse
attention:

- `AIT-T0001` (`Circle.Applications.attentionReach_eq_div_gcd`): one stride-`k` head reaches exactly `n / gcd(n,k)` distinct positions.
- `AIT-T0002` (`Circle.Applications.stridedHead_fullCoverage_iff_coprime`): it reaches **every** position of a length-`n` context **iff** `gcd(n,k) = 1`.
- `AIT-T0003` (`Circle.Applications.stridedHead_fullCoverage_of_coprime`): a coprime stride therefore guarantees full coverage.
- `AIT-T0010` (`Circle.Applications.localLagReach_of_le`): a local window reaches positive lags inside its width.
- `AIT-T0011` (`Circle.Applications.coilLagReach_of_step`): a coil path reaches lags generated by admitted stride steps.
- `AIT-T0012` (`Circle.Applications.coilLagReach_add_context`): coil lag reachability is unchanged by adding one full context length to the target lag.
- `AIT-T0013` and `AIT-T0014` (`Circle.Applications.hybridLagReach_of_local`, `Circle.Applications.hybridLagReach_of_coil`): a hybrid local+coil head reaches anything already reached by either component.
- `AIT-T0015` and `AIT-T0016` (`Circle.Applications.coilStrideFamilyLagReach_of_member_step`, `Circle.Applications.coilStrideFamilyLagReach_add_context`): a finite family of admitted strides reaches lags generated by any member stride, with the same full-context cyclic alias law.
- `AIT-T0017` through `AIT-T0019` (`Circle.Applications.hybridFamilyLagReach_of_local`, `Circle.Applications.hybridFamilyLagReach_of_family`, `Circle.Applications.hybridFamilyLagReach_of_member_step`): a local+stride-family plan reaches anything already reached by the local window or any admitted stride in the family.
- `AIT-T0020` (`Circle.Applications.hybridFamilyLagGap_iff_not_local_and_not_family`): a lag is missed by the local+stride-family plan exactly when it is missed by both the local window and the admitted stride-family paths.

This is the kind of structural guarantee practitioners reason about informally for
dilated/strided attention, here made exact and Lean-checked on top of the orbit spine
(`Circle.period_eq_n_div_gcd`). It is a guarantee about *which positions are reachable*,
not a claim about accuracy or speed — those remain empirical and are out of scope for the
theorem layer.

## Proved Core

`AIM-T0001` proves that the memory slot is bounded by the positive bank size. `AIM-T0002` proves closure after one full memory-bank pass:

```text
memorySlot bankSize (token + bankSize) =
  memorySlot bankSize token
```

`AIM-T0004` proves closure after any whole number of full memory-bank passes. `AIM-T0005` proves that normalizing a memory slot twice is the same as normalizing it once. `AIM-T0003` proves the zero anchor. The Python sidecar checks the same finite examples.

`AIM-T0059` through `AIM-T0063` add the second proof-carrying AI contract: KV-cache ring-buffer safety. The formal object is still finite arithmetic, not a deployment claim. The theorems prove that a token slot is bounded by the cache size, that writing exactly one cache-size later returns to the same slot, that ordered slot collision is equivalent to divisibility of the token-position gap, that positive gaps smaller than the cache size cannot collide, and that a token still inside the retained window has its next same-slot overwrite after the current token.

`AIM-T0006` through `AIM-T0058` prove finite loop-schedule, token-active-set, middle-block-route, combined route/budget, looped recurrent state, and loop-exit certificate facts: required loop depth is positive, bounded by a positive loop period, periodic under one full loop-period shift, and invariant under any whole number of loop-period passes; token recurrence budgets are positive, start at one loop step for token/sample zero, have the same one-period and multi-pass closure behavior, and are bounded by the loop period; a looped recurrent hidden-state index is bounded by the period, starts at zero for a one-step loop, recovers the sample phase when read at the required depth or certified token budget, is invariant under whole loop-period token shifts, and has one-period/multi-period closure for positive raw budgets; token active-step membership includes the first loop step, is invariant under whole loop-period token shifts, is bounded by the loop period, and excludes steps beyond that period; middle-block routes stay inside the selected block range, close after one selected-width shift, close after any whole number of selected-width shifts, and select the range start at sample zero; combined middle-block/budget routes carry both block-range and loop-budget bounds, initialize at `(start, 1)` for sample zero, and close after one product common cycle `width * loopPeriod` or any whole number of such product common cycles; the training-free wrapper budget is capped by `maxLoops` and by the required depth, is periodic, is invariant under whole loop-period passes, selects the exact positive required depth when an exit is available, and clamps to `maxLoops` when no exit is available; overthinking boundaries are at least the required depth and share the same one-period and multi-pass closure; exit availability is guaranteed when the loop budget covers the full period and is invariant under one or many loop-period passes; and a loop-exit certificate records a positive exact required step, budget bound, guardrail bound, implied exit availability, equality between the selected wrapper budget and the certified exit step, and multi-pass invariance of the certified exit step and guardrail boundary.

These theorems certify cyclic slot addresses and finite loop-budget arithmetic only. They do not prove retrieval quality, alias control, attention replacement, recursive reasoning, runtime, memory use, parameter efficiency, or long-context scaling.

## Exploratory Benchmark Fixture

`AIM-B0001` adds a deterministic cyclic-memory fixture. The positive synthetic task labels tokens by memory slot, so a slot lookup recovers the pattern while constant and scalar-threshold baselines do worse. The negative control labels tokens by an ordinary scalar threshold; there the threshold baseline wins and the memory-slot lookup fails.

The fixture also records collision diagnostics: how many training tokens alias into already-used slots and the maximum training load of a slot. These are executable checks for the benchmark harness only. They are not evidence that cyclic memory improves language modeling, retrieval, attention, or long-context scaling.

`AIM-B0018` adds the KV-cache ring-buffer certificate fixture. For a declared `cache_size`, `current`, and `token`, it reports the slot, lag, retained-window status, next same-slot overwrite token, and whether that overwrite occurs after the current token. The default sidecar reports `cache_size = 16`, `current = 31`, `token = 20`, slot `4`, lag `11`, retained `true`, and next overwrite `36 > 31`.

This fixture checks finite indexing and overwrite-window bookkeeping only. It is not evidence of better retrieval quality, lower memory, faster inference, safer deployment, or a complete KV-cache paging policy.

`AIM-B0002` adds a deterministic coil-retrieval reachability fixture. The positive synthetic task has a known dependency lag that is reachable by the selected coil path but not by the local-window or wrong-stride baselines. The full-attention candidate set is included as an oracle upper bound. The near-lag control reverses the story: local attention reaches the dependency while the selected coil path misses it.

This fixture checks candidate-set reachability only. It is not evidence that Coil Attention improves model quality, that fixed coils replace full attention, that alias behavior is solved, or that a model runs faster.

`AIM-B0004` adds a deterministic content-gated retrieval fixture. It mixes two dependency types: even-indexed queries need a long lag reached by the selected coil path, while odd-indexed queries need a near lag reached by the local window. The content-gated route chooses coil or local candidates according to that fixture signal. Static coil and static local baselines each solve only half of the mixed task; a wrong-gate control fails; union and full-attention baselines solve the task with larger candidate budgets.

This fixture checks routing reachability and candidate budget only. It is not evidence that a learned gate works, that attention quality improves, that context length improves, or that inference is faster.

`AIM-B0016` adds a deterministic hybrid sparse-attention fixture. It compares local-window, coil-only, hybrid local+coil, wrong-stride hybrid, and full-attention candidate sets on a mixed-lag task where one third of queries need a near dependency and two thirds need coil-reachable long dependencies. The hybrid reaches all structured dependencies with far fewer candidates than full attention, while local-only, coil-only, and wrong-stride controls fail part of the task. The nonstructured control reverses the lesson: full attention remains the oracle, and the sparse hybrid misses many arbitrary lags.

This fixture checks candidate-set reachability and budget only. It is not evidence that hybrid sparse attention improves neural retrieval quality, long-context behavior, runtime, memory use, or model quality.

`AIM-B0017` adds a deterministic stride-family sparse-attention fixture. It compares a local-window plus finite stride family against local-only, single-stride, wrong-family, and full-attention candidate sets. On the default structured task, generated lags are either local or produced by one of the admitted strides `(7,13)`, so the family reaches all structured dependencies with average candidate count `10` versus `120` for full attention. The single-stride baseline reaches only the local plus first-stride portion, the wrong-family control misses the generated long lags, and the nonstructured control again shows that arbitrary lags are not covered by the sparse pattern.

The same fixture now emits an explicit coverage certificate. For the default `sequence_length = 120`, `local_window = 4`, `path_length = 3`, and strides `(7,13)`, the covered positive lags are:

```text
1, 2, 3, 4, 7, 14, 21, 13, 26, 39
```

The remaining `109` positive lags are exposed as uncovered-lag gap certificates. This is the practical point of the Phase VIII upgrade: the artifact reports holes, not only successful examples.

This fixture checks multi-stride candidate-set reachability and budget only. It is not evidence that stride-family sparse attention improves neural attention quality, long-context behavior, throughput, runtime, memory use, or model quality.

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

`AIM-B0007` adds a deterministic middle-block recurrence fixture. It records a selected loop-block range, the required block and recurrence budget for each sample, and compares selected-block scheduling against full-block, fixed-budget, wrong-block, and over-loop controls with block-pass accounting. `AIM-T0039` through `AIM-T0043` prove the finite route boundary used by the contiguous selected-block helper. `AIM-T0044` through `AIM-T0048` plus `AIM-T0056` through `AIM-T0058` add the combined route/budget certificate: the selected block remains in range, the budget remains positive and bounded by the loop period, token/sample zero starts at one loop step, the combined sample-zero route is `(start, 1)`, and the pair closes after one product common cycle or any whole number of product common cycles.

This fixture checks block and budget bookkeeping only. It is not evidence that looping a middle block improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0013` adds a deterministic learned middle-block recurrence fixture. It fits one phase-to-block lookup table and one phase-to-budget lookup table from training samples, applies both tables to held-out samples, and compares the learned route against selected-band, full-block, fixed-budget, wrong block-period, wrong budget-period, wrong-block, and over-loop controls with block-pass accounting.

This fixture checks whether the benchmark harness can learn a constructed finite block-and-budget routing table. It is not evidence that learned middle-block recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0008` adds a deterministic multi-resolution recurrence fixture. It records required loop budgets, required coarse/fine resolution labels, active sample counts by loop step, and compares phase-routed multi-resolution scheduling against single-resolution, fixed-budget, wrong-resolution, and over-loop controls.

This fixture checks budget and resolution bookkeeping only. It is not evidence that compressed/full-resolution recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0014` adds a deterministic learned multi-resolution recurrence fixture. It fits one phase-to-budget lookup table and one phase-to-resolution lookup table from training samples, applies both tables to held-out samples, and compares the learned route against single-resolution, fixed-budget, wrong budget-period, wrong resolution-period, and over-loop controls.

This fixture checks whether the benchmark harness can learn a constructed finite budget-and-resolution routing table. It is not evidence that learned multi-resolution recurrence improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0009` adds a deterministic learned recurrence-schedule fixture. It fits a phase-to-loop-budget lookup table from training examples, then compares that learned schedule against fixed-budget, wrong-period, and over-loop controls.

This fixture checks whether the benchmark harness can learn a constructed finite schedule table. It is not evidence that learned recursive transformers improve reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

`AIM-B0015` adds a tiny looped recurrent prototype fixture. It uses a finite hidden state that advances one phase per loop; reading that state at the certified token recurrence budget recovers the sample phase. The fixture fits a state-to-label lookup and compares it against direct phase lookup, one-step, scalar-threshold, wrong-period, and nonperiodic scalar controls.

This fixture checks whether a tiny recurrent-state harness obeys its finite schedule contract. It is not evidence that a learned recursive transformer improves reasoning, perplexity, throughput, memory use, context length, or parameter efficiency.

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

The current long-context retrieval fixtures now separate fixed coil reachability (`AIM-B0002`), hand-coded route selection (`AIM-B0004`), learned finite route tables (`AIM-B0010`), and hybrid local+coil coverage (`AIM-B0016`). The next benchmark should move from candidate-set reachability toward learned sparse attention while preserving the same ordinary baselines and controls:

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

## Theseus-Hive Recurrence, Fanout, And Memory Transfer

The local Theseus-Hive project is the practical testbed for this paper's ideas. A read-only architecture pass identified three immediate integration surfaces:

1. state-sequence and candidate-generation features, where position buckets and dynamic token features can be compared with phase and MultiCoil features;
2. candidate fanout and STS-conditioned branch ranking, where stride-family coverage can be compared with sequential, random, round-robin, and ordinary stratified policies;
3. context packet and routing memory, where cyclic slots must be paired with winding/provenance to avoid hiding alias collisions.

The Circle-side transfer artifact should be a small contract schema rather than a model fork:

```text
circle_recurrence_contract:
  period
  sample_id
  token_id
  required_depth
  selected_budget
  loop_phase
  active_steps
  exit_step
  overthinking_boundary

circle_fanout_contract:
  context_length
  stride
  gcd
  predicted_reach
  candidate_budget
  duplicate_count
  rejection_reason_counts

circle_memory_contract:
  bank_size
  event_index
  residue_slot
  winding
  alias_load
  retained
```

The Lean side can prove only finite facts about these fields: bounds, closure after full periods, gcd coverage, and schedule invariance. Theseus-Hive experiments must decide whether those contracts improve private transfer, runtime, memory use, or interpretability. The ordinary baselines should be Theseus-Hive's current feature buckets, existing work-budget admission, score-based packet retention, fixed-loop or dense-depth recurrence, and existing candidate fanout policies.

The recurrence, fanout, and memory contracts are now exported by:

```text
circle_math/applications/theseus_hive_contracts.py
scripts/export_theseus_hive_ai_contracts.py
site/data/generated/theseus_hive_ai_contracts.json
```

## Next Program

- Treat `AIM-B0001` as cyclic-memory benchmark scaffolding only.
- Treat `AIM-B0002` as coil-retrieval reachability scaffolding only; learned/content-gated retrieval quality remains separate work.
- Treat `AIM-B0004` as content-gated route scaffolding only; learned gates, attention quality, context length, runtime, and memory-scaling claims remain separate work.
- Treat `AIM-B0010` as learned route-table scaffolding only; neural learned gates, retrieval quality, context length, runtime, and memory-scaling claims remain separate work.
- Treat `AIM-B0016` as hybrid local+coil reachability scaffolding only; sparse-attention quality, speed, memory scaling, and long-context usefulness remain separate work.
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
- Use `docs/THESEUS_HIVE_AI_TRANSFER.md` and `site/data/generated/theseus_hive_ai_contracts.json` as the Theseus-Hive integration boundary: run private Theseus-Hive comparisons against existing fanout, memory, work-budget, and recurrence baselines before making any usefulness claim.
- Test fixed, learned, and content-gated coil paths separately.
- Expand recurrence schedule, loop-exit certificate, and overthinking-boundary fixtures toward dense, Universal Transformer, fixed-loop, adaptive-exit, recurrent-memory, token-level Mixture-of-Recursions, sparse/MoE, RWKV/Mamba-style, and state-space baseline implementations.
- Track gcd/orbit coverage and aliasing explicitly.
- Add local/global attention fallbacks before claiming a practical model.
- Keep MLX/Mac-compatible experiments first.

## Guardrail

Do not replace all attention with fixed circles. A cyclic memory slot is a proved address primitive, not a proof that cyclic memory is sufficient for language modeling or retrieval. A looped recurrence schedule is not a proof of reasoning quality, context length, speed, or parameter efficiency.
