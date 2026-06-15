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
archive/handoffs/circle_calculus_codex_handoff/source_logs/06_looped_recursive_transformer_research.md
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
scripts/kv_cache_certify.py
```

The KV-cache ring-buffer sidecar also stores reproducible result fixtures:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/kv_cache_ring_buffer.json
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/kv_cache_ring_buffer.md
```

The stride-family sparse-attention sidecar also stores reproducible result fixtures:

```text
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/stride_family_sparse_attention.json
sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/results/stride_family_sparse_attention.md
```

The command-line sparse-plan certifier is:

```text
scripts/stride_family_certify.py
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
- `AIM-T0064`: `Circle.Applications.kvCacheWindow_retainedSlot_ne_current_of_lt`
- `AIM-T0065`: `Circle.Applications.kvCacheWindow_retainedSlots_ne_of_lt`
- `AIM-T0066`: `Circle.Applications.kvCacheWindow_retainedSlots_ne_of_ne`
- `AIM-T0067`: `Circle.Applications.kvCacheWindow_retainedBatchSlots_pairwise_ne`
- `AIM-T0068`: `Circle.Applications.kvCacheWindow_retainedBatchSlotMap_nodup`
- `AIM-T0069`: `Circle.Applications.kvCacheWindowContains_iff_current_lt_nextOverwrite`
- `AIM-T0070`: `Circle.Applications.not_kvCacheWindowContains_iff_nextOverwrite_le_current_of_le`
- `AIM-T0071`: `Circle.Applications.kvCacheLiveWindowStart_add_length`
- `AIM-T0072`: `Circle.Applications.kvCacheWindowContains_iff_mem_liveWindowTokens`
- `AIM-T0073`: `Circle.Applications.kvCacheLiveWindowTokens_slotMap_nodup`
- `AIM-T0074`: `Circle.Applications.kvCacheLiveWindowTokens_slotMap_fullCoverageContract`
- `AIM-T0075`: `Circle.Applications.kvCacheWindow_noSameSlotOverwrite_between`
- `AIM-T0076`: `Circle.Applications.kvCacheWindow_sameSlotOverwrite_witness_of_not_contains`
- `AIM-T0077`: `Circle.Applications.kvCacheWindowContains_iff_noSameSlotOverwrite_between_of_le`
- `AIM-T0078`: `Circle.Applications.kvCacheWindow_retainedBatch_iff_noSameSlotOverwriteTrace_of_forall_le`
- `AIM-T0079`: `Circle.Applications.kvCacheWindow_traceFreshBatchSlotMap_nodup`
- `AIM-T0080`: `Circle.Applications.kvCacheLiveWindowTokens_slotMap_length_eq_cacheSize_iff_full`
- `AIM-T0081`: `Circle.Applications.kvCacheLiveWindowTokens_slotMap_fullCoverageContract_iff_full`
- `AIM-T0082`: `Circle.Applications.kvCacheLiveWindowTokens_slotMap_mem_iff_lt_cacheSize_of_full`
- `AIM-T0083`: `Circle.Applications.kvCacheLiveWindowTokens_slotRangeCovered_iff_full`
- `AIM-T0086`: `Circle.Applications.kvCacheAdapterRequestTracePass_iff_nonFuture_nodup_traceFresh`
- `AIM-T0087`: `Circle.Applications.kvCacheLiveWindowTokens_adapterRequestTracePass`
- `AIM-T0088`: `Circle.Applications.kvCacheLiveWindowRequestTraceContract_iff_tokens_eq_liveWindow`
- `AIM-T0089`: `Circle.Applications.kvCacheLiveWindowRequestTraceContract_default_16_31`
- `AIM-T0091`: `Circle.Applications.kvCacheNoSameSlotOverwriteTrace_iff_current_lt_nextOverwrite_of_le`
- `AIM-T0092`: `Circle.Applications.kvCacheBatchNoSameSlotOverwriteTrace_iff_all_nextOverwrite_after_current_of_forall_le`
- `AIM-T0093`: `Circle.Applications.kvCacheAdapterRequestTracePass_iff_nonFuture_nodup_nextOverwriteAfterCurrent`
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
- `AIM-T0084`: `Circle.Applications.loopScoreActive_firstActive_iff`
- `AIM-T0085`: `Circle.Applications.loopExitAvailable_iff_exists_firstActiveWithinBudget`
- `AIM-T0090`: `Circle.Applications.not_loopExitAvailable_iff_forall_not_loopScoreActive_withinBudget`
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
- `AIT-T0021`: `Circle.Applications.hybridFamilyLagGap_of_above_window_and_forall_stride_step_ne`
- `AIT-T0022`: `Circle.Applications.hybridFamilyLagReach_of_localWindow_ge_context_sub_one`
- `AIT-T0023`: `Circle.Applications.localWindowCoversContext_iff_context_sub_one_le`
- `AIT-T0024`: `Circle.Applications.coilStrideFamilyLagReach_cons_iff`
- `AIT-T0025`: `Circle.Applications.hybridFamilyLagReach_cons_iff`
- `AIT-T0026`: `Circle.Applications.not_coilStrideFamilyLagReach_nil`
- `AIT-T0027`: `Circle.Applications.hybridFamilyLagReach_nil_iff_local`
- `AIT-T0028`: `Circle.Applications.not_localLagReach_iff_window_lt_of_pos`
- `AIT-T0029`: `Circle.Applications.localLagReach_mono_window`
- `AIT-T0030`: `Circle.Applications.coilLagReach_mono_pathLength`
- `AIT-T0031`: `Circle.Applications.coilStrideFamilyLagReach_mono_pathLength`
- `AIT-T0032`: `Circle.Applications.hybridFamilyLagReach_mono_window_pathLength`
- `AIT-T0033`: `Circle.Applications.hybridFamilyCoversContext_iff_no_uncovered_lag`
- `AIT-T0034`: `Circle.Applications.hybridFamilyCoversContext_of_localWindow_ge_context_sub_one`
- `AIT-T0035`: `Circle.Applications.hybridFamilyCoversContext_mono_window_pathLength`
- `AIT-T0036`: `Circle.Applications.hybridFamilyRawCandidateBudget_ge_window`
- `AIT-T0037`: `Circle.Applications.hybridFamilyRawCandidateBudget_cons`
- `AIT-T0038`: `Circle.Applications.hybridFamilyRawCandidateBudget_mono_window_pathLength`
- `AIT-T0039`: `Circle.Applications.hybridFamilyDedupCandidateBudgetBound_le_raw`
- `AIT-T0040`: `Circle.Applications.hybridFamilyDedupCandidateBudgetBound_le_context`
- `AIT-T0041`: `Circle.Applications.hybridFamilyDedupCandidateBudgetBound_eq_raw_of_raw_le_context`
- `AIT-T0042`: `Circle.Applications.hybridFamilyDedupCandidateBudgetBound_eq_context_of_context_le_raw`
- `AIT-T0043`: `Circle.Applications.localLagCandidateList_length`
- `AIT-T0044`: `Circle.Applications.coilStrideFamilyLagResidueList_length`
- `AIT-T0045`: `Circle.Applications.hybridFamilyLagCandidateList_length`
- `AIT-T0046`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_le_raw`
- `AIT-T0047`: `Circle.Applications.mem_localLagCandidateList_iff`
- `AIT-T0048`: `Circle.Applications.mem_coilLagResidueList_iff`
- `AIT-T0049`: `Circle.Applications.mem_coilStrideFamilyLagResidueList_iff`
- `AIT-T0050`: `Circle.Applications.mem_hybridFamilyLagCandidateList_iff`
- `AIT-T0051`: `Circle.Applications.hybridFamilyQueryCandidateList_length`
- `AIT-T0052`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_le_raw`
- `AIT-T0053`: `Circle.Applications.mem_hybridFamilyQueryCandidateList_iff_exists_lag`
- `AIT-T0054`: `Circle.Applications.predecessorIndex_mem_hybridFamilyQueryCandidateList_of_reach`
- `AIT-T0055`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_eq_raw_of_noCollision`
- `AIT-T0056`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noCollision`
- `AIT-T0057`: `Circle.Applications.hybridFamilyLagCandidatesNoCollision_of_coil_noCollision_of_local_coil_disjoint`
- `AIT-T0058`: `Circle.Applications.hybridFamilyQueryCandidatesNoCollision_of_lag_noCollision_of_predecessor_injective`
- `AIT-T0059`: `Circle.Applications.coilLagResidueList_nodup_of_path_mul_stride_lt_context`
- `AIT-T0060`: `Circle.Applications.coilStrideFamilyLagResiduesNoCollision_singleton_of_path_mul_stride_lt_context`
- `AIT-T0061`: `Circle.Applications.localCoilLagCandidatesDisjoint_singleton_of_window_lt_stride_of_path_mul_stride_lt_context`
- `AIT-T0062`: `Circle.Applications.hybridFamilyLagCandidatesNoCollision_singleton_of_window_lt_stride_of_path_mul_stride_lt_context`
- `AIT-T0063`: `Circle.Applications.coilStrideFamilyLagResiduesNoCollision_cons_of_head_tail_disjoint`
- `AIT-T0064`: `Circle.Applications.coilLagResiduesDisjointFromFamily_of_path_mul_head_lt_tail_strides`
- `AIT-T0065`: `Circle.Applications.coilStrideFamilyLagResiduesNoCollision_of_noWrapSeparated`
- `AIT-T0066`: `Circle.Applications.localCoilLagCandidatesDisjoint_of_noWrapSeparated_of_window_lt_all_strides`
- `AIT-T0067`: `Circle.Applications.hybridFamilyLagCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides`
- `AIT-T0068`: `Circle.Applications.hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective`
- `AIT-T0069`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides`
- `AIT-T0070`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides_of_predecessor_injective`
- `AIT-T0071`: `Circle.Applications.predecessorIndex_injective_of_lag_lt_context`
- `AIT-T0072`: `Circle.Applications.mem_hybridFamilyLagCandidateList_lt_context_of_window_lt_context`
- `AIT-T0073`: `Circle.Applications.hybridFamilyPredecessorInjectiveOnLagCandidates_of_window_lt_context`
- `AIT-T0074`: `Circle.Applications.hybridFamilyQueryCandidatesNoCollision_of_noWrapSeparated_of_window_lt_all_strides_of_window_lt_context`
- `AIT-T0075`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_eq_raw_of_noWrapSeparated_of_window_lt_all_strides_of_window_lt_context`
- `AIT-T0076`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_eq_raw_iff_noCollision`
- `AIT-T0077`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_eq_raw_iff_noCollision`
- `AIT-T0078`: `Circle.Applications.hybridFamilyCoversContext_iff_range_lags_mem_candidate_list`
- `AIT-T0079`: `Circle.Applications.hybridFamilyLagGap_default_120_4_3_7_13_lag5`
- `AIT-T0080`: `Circle.Applications.not_hybridFamilyCoversContext_default_120_4_3_7_13`
- `AIT-T0081`: `Circle.Applications.mem_hybridFamilyUncoveredLagList_iff`
- `AIT-T0082`: `Circle.Applications.hybridFamilyCoversContext_iff_uncoveredLagList_eq_nil`
- `AIT-T0083`: `Circle.Applications.hybridFamilyCoversContext_iff_uncoveredLagList_length_eq_zero`
- `AIT-T0084`: `Circle.Applications.mem_hybridFamilyUncoveredLagList_default_120_4_3_7_13_lag5`
- `AIT-T0085`: `Circle.Applications.hybridFamilyUncoveredLagList_default_120_4_3_7_13_length`
- `AIT-T0086`: `Circle.Applications.hybridFamilyUncoveredLagList_complete_9_2_2_3_4_7_eq_nil`
- `AIT-T0087`: `Circle.Applications.hybridFamilyCoversContext_complete_9_2_2_3_4_7`
- `AIT-T0088`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_complete_9_2_2_3_4_7_eq_raw`
- `AIT-T0089`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_complete_9_2_2_3_4_7_eq_raw`
- `AIT-T0090`: `Circle.Applications.mem_hybridFamilyCoveredLagList_iff`
- `AIT-T0091`: `Circle.Applications.hybridFamilyCoveredLagList_default_120_4_3_7_13_length`
- `AIT-T0092`: `Circle.Applications.hybridFamilyCoveredLagList_disjoint_uncoveredLagList`
- `AIT-T0093`: `Circle.Applications.mem_hybridFamilyCoveredLagList_or_mem_hybridFamilyUncoveredLagList_of_pos_lt_context`
- `AIT-T0094`: `Circle.Applications.hybridFamilyCoveredUncoveredLagList_length_add`
- `AIT-T0095`: `Circle.Applications.hybridFamilyCoversContext_iff_coveredLagList_length_eq_context_sub_one`
- `AIT-T0096`: `Circle.Applications.hybridFamilyUncoveredLagList_length_pos_iff_exists_uncovered_lag`
- `AIT-T0097`: `Circle.Applications.hybridFamilyCoveredLagList_length_lt_context_sub_one_iff_exists_uncovered_lag`
- `AIT-T0098`: `Circle.Applications.hybridFamilyFirstUncoveredLag_eq_none_iff_uncoveredLagList_eq_nil`
- `AIT-T0099`: `Circle.Applications.hybridFamilyCoversContext_iff_firstUncoveredLag_eq_none`
- `AIT-T0100`: `Circle.Applications.hybridFamilyFirstUncoveredLag_eq_some_iff_uncoveredLagList_eq_cons`
- `AIT-T0101`: `Circle.Applications.hybridFamilyFirstUncoveredLag_eq_some_gap`
- `AIT-T0102`: `Circle.Applications.hybridFamilyFirstUncoveredLag_default_120_4_3_7_13_eq_some5`
- `AIT-T0103`: `Circle.Applications.hybridFamilyUncoveredLagList_length_pos_iff_firstUncoveredLag_ne_none`
- `AIT-T0104`: `Circle.Applications.hybridFamilyUncoveredLagIntervalList_default_120_4_3_7_13`
- `AIT-T0105`: `Circle.Applications.hybridFamilyUncoveredLagIntervalList_complete_9_2_2_3_4_7_eq_nil`
- `AIT-T0106`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_le_context_of_pos`
- `AIT-T0107`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_le_dedup_bound_of_context_pos`
- `AIT-T0108`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_le_uniqueLagCandidateCount`
- `AIT-T0109`: `Circle.Applications.hybridFamilyUniqueQueryCandidateCount_eq_uniqueLagCandidateCount_of_predecessor_injective`
- `AIT-T0110`: `Circle.Applications.hybridFamilyRawCandidateBudget_ge_context_sub_one_of_covers`
- `AIT-T0111`: `Circle.Applications.hybridFamilyUniqueLagCandidateCount_ge_context_sub_one_of_covers`
- `AIT-T0112`: `Circle.Applications.hybridFamilyCoversContext_iff_uniqueLagCandidateCount_eq_context_sub_one_of_candidate_range`

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
- `AIT-T0021` (`Circle.Applications.hybridFamilyLagGap_of_above_window_and_forall_stride_step_ne`): a concrete uncovered-lag certificate is valid when the lag is beyond the local window and no admitted stride/step pair has the same cyclic lag.
- `AIT-T0022` (`Circle.Applications.hybridFamilyLagReach_of_localWindow_ge_context_sub_one`): if the local window is at least `n - 1`, every positive lag inside a length-`n` context is covered by the local part of the plan.
- `AIT-T0023` (`Circle.Applications.localWindowCoversContext_iff_context_sub_one_le`): conversely, local-window coverage of every positive in-context lag is equivalent to the exact condition `n - 1 <= window`.
- `AIT-T0024` and `AIT-T0025` (`Circle.Applications.coilStrideFamilyLagReach_cons_iff`, `Circle.Applications.hybridFamilyLagReach_cons_iff`): adding one stride decomposes exactly into coverage by the added stride or by the previous family, matching the finite-family coverage certificate recursion.
- `AIT-T0026` and `AIT-T0027` (`Circle.Applications.not_coilStrideFamilyLagReach_nil`, `Circle.Applications.hybridFamilyLagReach_nil_iff_local`): the empty-family control has no coil reachability and reduces exactly to the local-window baseline.
- `AIT-T0028` (`Circle.Applications.not_localLagReach_iff_window_lt_of_pos`): for positive lags, the local-window miss condition is exactly `window < lag`.
- `AIT-T0029` through `AIT-T0032`: increasing the local-window width or admitted path length cannot remove lags already covered by the local, coil, stride-family, or combined sparse plan.
- `AIT-T0033` through `AIT-T0035`: the named complete-coverage predicate for a local+stride-family plan is equivalent to having no positive in-context uncovered-lag certificate, is implied by the dense-local `n - 1` threshold, and is preserved by conservative window/path-length budget increases.
- `AIT-T0036` through `AIT-T0038`: raw candidate-budget accounting for the same local+stride-family plan. The raw budget `window + pathLength * strides.length` contains the local-window budget, gains one path-length block per added stride, and is monotone under conservative budget increases. `AIT-T0039` through `AIT-T0042` add the context-clipped deduplicated-budget cap `min(context, raw_budget)`, prove that it is bounded by both raw budget and context size, and identify the two equality regimes. `AIT-T0043` through `AIT-T0050` add an exact theorem-side lag-candidate list: its raw length is the raw budget, its deduplicated length is bounded by the raw budget, and membership in the list is equivalent to local+stride-family reachability for in-context lags. `AIT-T0078` adds the finite coverage-enumeration endpoint: full context coverage is equivalent to every positive lag in `List.range' 1 (n - 1)` appearing in that theorem-side candidate list. `AIT-T0090` adds the positive covered-list bridge: membership in `hybridFamilyCoveredLagList` is exactly positive in-context semantic reachability. `AIT-T0081` through `AIT-T0083` make the complementary finite gap list proof-carrying too: membership in `hybridFamilyUncoveredLagList` is exactly a positive in-context semantic miss, and complete coverage is equivalent to that list being empty or having length zero. `AIT-T0092` through `AIT-T0097` add the finite partition, complete-count, and gap-count witness guardrails: the covered and uncovered lists are disjoint, every positive in-context lag appears in one of them, their lengths add to `n - 1`, complete coverage is equivalent to the covered-list length being `n - 1`, a positive uncovered-list length is equivalent to the existence of a concrete uncovered lag, and a covered-list count below `n - 1` is equivalent to such a gap witness. `AIT-T0098` through `AIT-T0101` make the first-gap report field theorem-backed: no first gap is equivalent to an empty uncovered list, complete coverage is equivalent to no first gap, a reported first gap is the uncovered-list head, and any reported first gap is a semantic miss. The Python certifier and Living Book compress that uncovered-lag list into consecutive intervals for readability; `AIT-T0104` and `AIT-T0105` certify the exact interval summaries for the two public sparse fixtures while leaving arbitrary interval compression as a report view over the proved gap list. `AIT-T0084` and `AIT-T0085` prove that the default plan's lag `5` appears in that finite uncovered-lag list and that the list has exactly `109` entries; `AIT-T0091` proves that the same default plan's covered-lag list has exactly `10` entries; `AIT-T0102` proves that the default first uncovered lag is exactly `5`. `AIT-T0086` through `AIT-T0089` add the positive fixture counterpart: for `C_9`, local window `2`, path length `2`, and strides `[3,4,7]`, the uncovered-lag list is empty, complete coverage holds, and both lag-side and query-side deduplicated counts equal the raw budget. `AIT-T0051` through `AIT-T0054` map that lag list to query-indexed predecessor candidates, bound the exact deduplicated query-candidate count by the raw budget, and prove that any reached in-context lag maps to a query candidate. `AIT-T0106` and `AIT-T0107` strengthen that budget story by proving that the exact deduplicated query-candidate count also fits inside the finite context and therefore inside the reported `min(context, raw_budget)` cap whenever the context is nonempty. `AIT-T0110` adds the raw-budget necessary-condition endpoint: if complete positive-lag coverage holds, then raw sparse generator budget must be at least `n - 1`, so a raw-budget shortfall is a proof-carrying incompleteness certificate. `AIT-T0111` adds the deduplicated counterpart: complete coverage also forces the theorem-side unique lag-candidate count to be at least `n - 1`, so duplicate collapse can certify incompleteness even when raw generator count alone is not decisive. `AIT-T0055` and `AIT-T0056` add the no-collision equality direction: if the lag or query candidate list has no duplicates, the exact deduplicated count equals the raw budget. `AIT-T0076` and `AIT-T0077` add the converse and close the budget-survival criterion: exact raw-budget equality holds if and only if the corresponding theorem-side candidate list has no duplicates. `AIT-T0057` and `AIT-T0058` make no-collision more checkable by deriving lag no-collision from coil-residue uniqueness plus local/coil disjointness, then lifting lag no-collision to query-candidate no-collision when predecessor indexing is injective on generated lag values. `AIT-T0059` through `AIT-T0062` add a numeric sufficient condition for singleton stride families: when the local window is below the stride and `pathLength * stride < n`, the lag candidates are duplicate-free. `AIT-T0063` makes residue no-collision compositional: adding one stride preserves the family certificate when the head block, tail family, and boundary are collision-free. `AIT-T0064` gives a numeric sufficient condition for the head/tail boundary: keep every involved stride block below `n` before modulo reduction and keep the head block's maximum below every tail stride. `AIT-T0065` lifts that rule to a whole ordered family: an ordered no-wrap separated stride family has duplicate-free residue blocks. `AIT-T0066` and `AIT-T0067` add the local-window side: if every stride starts beyond the local window, then local candidates are disjoint from the separated stride-family residues and the full theorem-side lag-candidate list is duplicate-free. `AIT-T0068` through `AIT-T0070` package the query side and exact raw-budget endpoints under the predecessor-injectivity predicate; `AIT-T0071` through `AIT-T0075` discharge that predicate from the numeric condition `window < n` and repackage the separated-family query/raw-budget endpoint without the abstract assumption. This is candidate-set accounting and reachability semantics, not a runtime theorem.

- `AIT-T0108`: mapping theorem-side lag candidates to query-indexed predecessor
  candidates is a finite image operation, so deduplicating the query image cannot
  produce more distinct candidates than deduplicating the lag-candidate source.
- `AIT-T0109`: when the predecessor map is injective on the generated lag
  candidates, that finite image preserves the exact deduplicated count instead
  of only satisfying the one-sided bound.
- `AIT-T0110`: complete positive-lag coverage forces raw sparse generator
  budget at least `n - 1`; contrapositively, a raw-budget shortfall certifies
  that the sparse plan is incomplete before any learned-quality question is
  asked.
- `AIT-T0111`: complete positive-lag coverage forces deduplicated unique
  lag-candidate count at least `n - 1`; contrapositively, duplicate collapse or
  any other unique-lag shortfall certifies that the sparse plan is incomplete.
- `AIT-T0112`: under the explicit candidate-range hypothesis that every
  generated lag candidate is already a positive in-context lag, complete
  coverage is equivalent to the deduplicated unique lag-candidate count
  equaling `n - 1`.

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

`AIM-T0059` through `AIM-T0083`, plus `AIM-T0086` through `AIM-T0089` and `AIM-T0091` through `AIM-T0093`, add the second proof-carrying AI contract: KV-cache ring-buffer safety. The formal object is still finite arithmetic, not a deployment claim. The theorems prove that a token slot is bounded by the cache size, that writing exactly one cache-size later returns to the same slot, that ordered slot collision is equivalent to divisibility of the token-position gap, that positive gaps smaller than the cache size cannot collide, that a token still inside the retained window has its next same-slot overwrite after the current token, that retained-window membership is exactly the non-future plus next-overwrite-after-current boundary, that a non-future stale token is exactly one whose next same-slot overwrite is at or before the current token, that the stale boundary gives an explicit same-slot overwrite witness at `token + cacheSize`, that a retained older token cannot share the current token's ring-buffer slot, that any two ordered tokens retained in the same window have distinct ring-buffer slots, that a retained token has no strictly later same-slot writer up to the current read point, that retained-window membership is exactly the absence of any later same-slot writer in the finite trace up to current, that the no-later-same-slot-write trace predicate is itself equivalent to the constant-time inequality `current < token + cacheSize` for non-future tokens, that a batch of non-future requested tokens is retained exactly when every requested token has no later same-slot writer up to current, that batch trace freshness is equivalent to every requested token satisfying the same next-overwrite boundary, that trace-fresh duplicate-free requested batches map to duplicate-free ring-buffer slots, that the modeled adapter request pass predicate is equivalent both to non-future duplicate-free trace-fresh requested tokens and to non-future duplicate-free requested tokens whose next same-slot overwrites are after the current read point, that a generated live-window request passes the modeled adapter request-trace contract, that the exact generated-live-window request contract is equivalent to the requested token list being exactly the generated live window, that the public `cache_size = 16`, `current = 31` fixture realizes that request with tokens `16..31`, that the same pairwise distinctness holds for any two distinct retained tokens without requiring the caller to order them first, that a duplicate-free retained-token batch maps to duplicate-free ring-buffer slots, that the generated live-token list exactly matches the retained-window predicate, that the generated live window maps to duplicate-free ring-buffer slots, that a full generated live window has one duplicate-free in-range slot entry per declared cache slot, that the generated slot-list count equals `cacheSize` if and only if the live window is full, that the whole generated full-coverage contract holds if and only if the live window is full, and that a full generated live-window slot map contains exactly the valid cache-slot range.

`AIM-T0006` through `AIM-T0058` prove finite loop-schedule, token-active-set, middle-block-route, combined route/budget, looped recurrent state, and loop-exit certificate facts: required loop depth is positive, bounded by a positive loop period, periodic under one full loop-period shift, and invariant under any whole number of loop-period passes; token recurrence budgets are positive, start at one loop step for token/sample zero, have the same one-period and multi-pass closure behavior, and are bounded by the loop period; a looped recurrent hidden-state index is bounded by the period, starts at zero for a one-step loop, recovers the sample phase when read at the required depth or certified token budget, is invariant under whole loop-period token shifts, and has one-period/multi-period closure for positive raw budgets; token active-step membership includes the first loop step, is invariant under whole loop-period token shifts, is bounded by the loop period, and excludes steps beyond that period; middle-block routes stay inside the selected block range, close after one selected-width shift, close after any whole number of selected-width shifts, and select the range start at sample zero; combined middle-block/budget routes carry both block-range and loop-budget bounds, initialize at `(start, 1)` for sample zero, and close after one product common cycle `width * loopPeriod` or any whole number of such product common cycles; the training-free wrapper budget is capped by `maxLoops` and by the required depth, is periodic, is invariant under whole loop-period passes, selects the exact positive required depth when an exit is available, and clamps to `maxLoops` when no exit is available; overthinking boundaries are at least the required depth and share the same one-period and multi-pass closure; exit availability is guaranteed when the loop budget covers the full period and is invariant under one or many loop-period passes; and a loop-exit certificate records a positive exact required step, budget bound, guardrail bound, implied exit availability, equality between the selected wrapper budget and the certified exit step, and multi-pass invariance of the certified exit step and guardrail boundary.

These theorems certify cyclic slot addresses and finite loop-budget arithmetic only. They do not prove retrieval quality, alias control, attention replacement, recursive reasoning, runtime, memory use, parameter efficiency, or long-context scaling.

## Exploratory Benchmark Fixture

`AIM-B0001` adds a deterministic cyclic-memory fixture. The positive synthetic task labels tokens by memory slot, so a slot lookup recovers the pattern while constant and scalar-threshold baselines do worse. The negative control labels tokens by an ordinary scalar threshold; there the threshold baseline wins and the memory-slot lookup fails.

The fixture also records collision diagnostics: how many training tokens alias into already-used slots and the maximum training load of a slot. These are executable checks for the benchmark harness only. They are not evidence that cyclic memory improves language modeling, retrieval, attention, or long-context scaling.

`AIM-B0018` adds the KV-cache ring-buffer certificate fixture. For a declared `cache_size`, `current`, and `token`, it reports the token slot, current slot, lag, retained-window status, whether a retained older token is distinct from the current slot, next same-slot overwrite token, whether that overwrite occurs after the current token, whether the token is stale by the next-overwrite boundary, whether any strictly later token up to the current read point has reused the same slot, whether the stale case has an explicit same-slot overwrite witness, and whether retention is equivalent to no later same-slot write in the finite trace. `AIM-T0069` proves that the next-overwrite-after-current flag is equivalent to retained-window membership once the token is not in the future. `AIM-T0070` proves the stale converse: a non-future token is not retained exactly when the next same-slot overwrite is at or before the current token. `AIM-T0076` packages the stale witness: for positive cache size, `token + cacheSize` is strictly later, at or before current, and in the same slot. `AIM-T0075` proves the read/write adapter guard: retained tokens have no later same-slot writer before the read point. `AIM-T0077` proves the trace contract: for positive cache size and a non-future token, retention is equivalent to no later same-slot writer up to current. `AIM-T0091` collapses that trace predicate to the same constant-time next-overwrite boundary, so an implementation-facing checker does not need to rescan every intervening write after the theorem has been proved. `AIM-T0078` lifts that trace contract to a declared read batch whose tokens are not in the future, and `AIM-T0092` gives the matching batch boundary iff. `AIM-T0079` packages the implementation-facing consequence: a duplicate-free non-future read batch whose requested tokens are all trace-fresh maps to duplicate-free ring-buffer slots. The sidecar also checks the ordered and unordered pairwise retained-token predicates behind `AIM-T0065` and `AIM-T0066`, plus the retained-batch slot-distinctness predicates behind `AIM-T0067` and `AIM-T0068`. The Python and CLI surfaces now package the retained-batch theorem spine as a named modeled adapter request trace: `AIM-T0086` proves that, for positive cache size, its pass predicate is equivalent to the compact checklist of non-future requested tokens, duplicate-free requested tokens, and per-token trace freshness; `AIM-T0093` proves the more implementation-facing form using the next-overwrite boundary instead of the trace scan; the retained and slot-distinct report fields are consequences rather than extra assumptions. `AIM-T0071` through `AIM-T0074` add the generated live-window certificate: its start plus length ends one past the current token, membership in the generated token list is equivalent to retained-window membership, the generated live window maps to duplicate-free slots, and a full live window has exactly `cache_size` in-range slot entries. `AIM-T0080` adds the count iff behind the live-window report: the generated slot-list length equals `cache_size` exactly when the live window is full. `AIM-T0081` upgrades the report's full-coverage flag to an iff: the duplicate-free, exact-count, in-range generated slot coverage contract holds exactly when the live window is full. `AIM-T0082` adds the membership form of that full-window slot-range claim: in the full generated live window, a slot appears exactly when it is less than `cache_size`. `AIM-T0083` proves that every declared cache slot appears in the generated slot map exactly when the live window is full. `AIM-T0087` and `AIM-T0088` add the generated-live-window request contract: the exact generated live-token list passes the modeled adapter request-trace predicate, and the named contract is equivalent to the requested token list being exactly that generated live window. `AIM-T0089` pins the public `16,31` fixture to the exact request `16..31`. The default CLI and sidecar report `cache_size = 16`, `current = 31`, `token = 20`, token slot `4`, current slot `15`, lag `11`, retained `true`, retained-current distinctness `true`, next overwrite `36 > 31`, stale-by-boundary `false`, no later same-slot overwrite before current `true`, stale same-slot overwrite witness `false`, retained/no-later-same-slot-write trace contract `true`, trace-fresh/next-overwrite-boundary iff `true`, retained batch `(20,24,29,31)` mapping to slots `(4,8,13,15)` with batch retained/no-later-same-slot-write trace contract `true`, batch next-overwrites-after-current `true`, adapter request trace `default_read_request` with `pass_certificate = true`, `pass_iff_next_overwrite_boundary = true`, trace-fresh slot distinctness `true`, generated live window tokens `16..31` mapping to slots `0..15`, and generated live-window request `generated_live_window_read` over tokens `16..31` with `exact_live_window_request = true`, `pass_certificate = true`, and `live_window_request_contract = true`. The CLI can emit text or JSON; the sidecar can emit text, JSON, or Markdown; the committed JSON/Markdown fixtures are regenerated by the sidecar and checked by the Python tests.

This fixture checks finite indexing, overwrite-window bookkeeping, and a modeled read-request trace only. It is not evidence of better retrieval quality, lower memory, faster inference, safer deployment, a complete KV-cache paging policy, or correctness of any concrete implementation.

`AIM-B0002` adds a deterministic coil-retrieval reachability fixture. The positive synthetic task has a known dependency lag that is reachable by the selected coil path but not by the local-window or wrong-stride baselines. The full-attention candidate set is included as an oracle upper bound. The near-lag control reverses the story: local attention reaches the dependency while the selected coil path misses it.

This fixture checks candidate-set reachability only. It is not evidence that Coil Attention improves model quality, that fixed coils replace full attention, that alias behavior is solved, or that a model runs faster.

`AIM-B0004` adds a deterministic content-gated retrieval fixture. It mixes two dependency types: even-indexed queries need a long lag reached by the selected coil path, while odd-indexed queries need a near lag reached by the local window. The content-gated route chooses coil or local candidates according to that fixture signal. Static coil and static local baselines each solve only half of the mixed task; a wrong-gate control fails; union and full-attention baselines solve the task with larger candidate budgets.

This fixture checks routing reachability and candidate budget only. It is not evidence that a learned gate works, that attention quality improves, that context length improves, or that inference is faster.

`AIM-B0016` adds a deterministic hybrid sparse-attention fixture. It compares local-window, coil-only, hybrid local+coil, wrong-stride hybrid, and full-attention candidate sets on a mixed-lag task where one third of queries need a near dependency and two thirds need coil-reachable long dependencies. The hybrid reaches all structured dependencies with far fewer candidates than full attention, while local-only, coil-only, and wrong-stride controls fail part of the task. The nonstructured control reverses the lesson: full attention remains the oracle, and the sparse hybrid misses many arbitrary lags.

This fixture checks candidate-set reachability and budget only. It is not evidence that hybrid sparse attention improves neural retrieval quality, long-context behavior, runtime, memory use, or model quality.

`AIM-B0017` adds a deterministic stride-family sparse-attention fixture. It compares a local-window plus finite stride family against local-only, single-stride, wrong-family, and full-attention candidate sets. On the default structured task, generated lags are either local or produced by one of the admitted strides `(7,13)`, so the family reaches all structured dependencies with average candidate count `10` versus `120` for full attention. The sidecar emits text, JSON, and Markdown result fixtures whose payloads record covered lags, uncovered gap witnesses, no-collision flags, query/lag candidate counts, the finite-range coverage iff (`AIT-T0078`), the proof-carrying covered-list bridge (`AIT-T0090`), the proof-carrying uncovered-list bridge (`AIT-T0081` through `AIT-T0083`), the covered/uncovered partition and count guardrail, covered-count completion criterion, uncovered-count witness criterion, covered-count shortfall witness criterion (`AIT-T0092` through `AIT-T0097`), first-gap/count-presence field semantics (`AIT-T0098` through `AIT-T0103`), and public fixture interval-summary certificates (`AIT-T0104`, `AIT-T0105`), the concrete default lag-`5` gap witness, incomplete-coverage consequence, uncovered-list membership witness, exact `109`-gap count, exact `10`-covered-lag count, exact first-uncovered-lag value, and exact six-interval gap summary (`AIT-T0079`, `AIT-T0080`, `AIT-T0084`, `AIT-T0085`, `AIT-T0091`, `AIT-T0102`, `AIT-T0104`), plus a compact complete-coverage fixture on `C_9` whose empty uncovered list, complete coverage, raw-budget-preserving lag/query counts, and empty interval summary are checked by `AIT-T0086` through `AIT-T0089` and `AIT-T0105`. The sidecar also emits compact planner-style rows for declared 4096- and 8192-token sparse layouts; these rows report exact candidate budgets, gap counts, first-gap witnesses, raw-budget and unique-lag shortfall incompleteness flags, candidate-range unique-count iff flags, covered-count shortfall flags, and no-collision budget predicates while pointing back to `scripts/stride_family_certify.py` for the full covered/uncovered-lag certificate. The iff theorem ids (`AIT-T0076`, `AIT-T0077`) characterize exactly when deduplicated theorem-side counts preserve the raw candidate budget; `AIT-T0106` and `AIT-T0107` separately certify that the exact deduplicated query-candidate count is bounded by the finite context and by the reported context-clipped budget, while `AIT-T0110` certifies that raw budget below `n - 1` is enough to rule out complete coverage, `AIT-T0111` certifies the sharper deduplicated unique-lag-count necessary condition, and `AIT-T0112` upgrades that count to a complete-coverage iff under the explicit positive in-context candidate-range hypothesis. The single-stride baseline reaches only the local plus first-stride portion, the wrong-family control misses the generated long lags, and the nonstructured control again shows that arbitrary lags are not covered by the sparse pattern.

`AIT-T0108` additionally certifies the report's `query_count_le_unique_lag_count` field: query-indexed predecessor candidates are a finite image of the lag-candidate source, so the unique query count is bounded by the unique lag count. `AIT-T0109` certifies the companion `query_count_matches_unique_lag_count` field whenever predecessor indexing is injective on the generated lag candidates. `AIT-T0110` certifies the raw-budget shortfall field: if the raw candidate generator count is below the number of positive in-context lags, the plan cannot be complete. `AIT-T0111` certifies the deduplicated unique-lag shortfall field: if duplicate removal leaves fewer unique lag candidates than positive in-context lags, the plan cannot be complete. `AIT-T0112` certifies the companion iff field: when every generated lag candidate is positive and in context, unique lag-candidate count equals `n - 1` exactly when coverage is complete.

The same fixture now emits an explicit coverage certificate. For the default `sequence_length = 120`, `local_window = 4`, `path_length = 3`, and strides `(7,13)`, the covered positive lags are:

```text
1, 2, 3, 4, 7, 14, 21, 13, 26, 39
```

The remaining `109` positive lags are exposed as uncovered-lag gap certificates. `AIT-T0021` states the concrete condition behind those holes: an uncovered lag is beyond the local window and every admitted stride/step pair misses its cyclic residue. `AIT-T0079` applies that condition to the default fixture by proving that lag `5` is genuinely uncovered for `C_120`, local window `4`, path length `3`, and strides `[7,13]`; `AIT-T0080` turns that witness into a theorem that the default plan is not complete coverage. `AIT-T0090` adds the positive finite-list bridge: the theorem-side `hybridFamilyCoveredLagList` contains exactly the positive in-context semantic hits. `AIT-T0081` through `AIT-T0083` are the complementary gap-list bridge the executable certifier needs: the theorem-side `hybridFamilyUncoveredLagList` contains exactly the positive in-context semantic misses, and complete coverage is equivalent to that list being empty or having length zero. `AIT-T0092` proves that no lag appears in both finite lists, `AIT-T0093` proves every positive in-context lag appears in one of them, `AIT-T0094` proves their lengths add to `n - 1`, `AIT-T0095` proves complete coverage is equivalent to the covered-list length being `n - 1`, `AIT-T0096` proves a positive uncovered-list length is equivalent to an actual uncovered positive-lag witness, and `AIT-T0097` proves that the covered-list count falling short of `n - 1` is equivalent to such a witness. `AIT-T0098` through `AIT-T0101` make the `first_uncovered_lag` report field proof-carrying: no first gap is equivalent to an empty uncovered list, complete coverage is equivalent to no first gap, a reported first gap is exactly the head of the theorem-side uncovered list, and any reported first gap is a semantic miss. `AIT-T0103` closes the adjacent count/presence bridge by proving that a positive uncovered-list count is equivalent to the first-gap option being populated. Together these justify reading the sidecar report as a finite hit/gap partition with a checked total count, checked completion criteria, checked count-to-witness presence, and a checked first-gap witness. `AIT-T0084` proves that the default fixture's lag `5` is a member of that finite uncovered list; `AIT-T0085` proves the list has exactly `109` entries; `AIT-T0091` proves the default covered-list has exactly `10` entries; `AIT-T0102` proves the default first uncovered lag is exactly `5`; and `AIT-T0104` proves the default interval compression is exactly `5..6`, `8..12`, `15..20`, `22..25`, `27..38`, `40..119`. `AIT-T0105` proves the compact complete fixture's uncovered interval summary is empty. `AIT-T0028` tightens the local part by proving that, for positive lags, missing the local window is exactly `window < lag`. `AIT-T0022` records the dense-local limit: if the local window is at least `n - 1`, there are no positive-lag holes. `AIT-T0023` adds the converse for local-only coverage: that threshold is exact for covering every positive in-context lag by the local window alone. `AIT-T0024` and `AIT-T0025` state the exact recursion for adding one stride to a family. `AIT-T0026` and `AIT-T0027` prove the no-stride control reduces exactly to local-window reachability. `AIT-T0029` through `AIT-T0032` add the tuning guarantee: increasing the local-window width or admitted path length cannot remove lags already covered by the plan. `AIT-T0033` through `AIT-T0035` package the full-plan coverage status itself: complete coverage is exactly the absence of positive uncovered-lag witnesses, dense local coverage implies that complete-coverage predicate, and conservative budget increases preserve complete coverage. `AIT-T0036` through `AIT-T0038` add raw candidate-budget accounting, `AIT-T0039` through `AIT-T0042` add the context-clipped bound on any deduplicated candidate count, `AIT-T0043` through `AIT-T0050` add the theorem-side exact lag-candidate list whose membership matches reachability for in-context lags, `AIT-T0078` proves that checking every generated positive lag in `List.range' 1 (n - 1)` against that list is equivalent to complete context coverage, `AIT-T0051` through `AIT-T0054` map reached lags into query-indexed predecessor candidates, `AIT-T0106`/`AIT-T0107` prove that the exact deduplicated query-candidate count fits the finite context and the reported clipped budget, `AIT-T0110` proves that any complete plan has raw candidate budget at least `n - 1`, `AIT-T0055`/`AIT-T0056` prove that no-collision candidate lists deduplicate without budget loss, `AIT-T0076`/`AIT-T0077` prove the iff endpoint that raw-budget survival is equivalent to no duplicates, `AIT-T0057`/`AIT-T0058` expose structural conditions that imply those no-collision predicates, `AIT-T0059` through `AIT-T0062` prove the first numeric singleton no-wrap condition, `AIT-T0063` adds a compositional residue no-collision rule for finite stride families, `AIT-T0064` adds a numeric head/tail separation rule for proving the compositional disjointness premise, `AIT-T0065` proves the ordered separated-family sufficient condition, `AIT-T0066`/`AIT-T0067` lift it through local-window disjointness to full theorem-side lag-candidate no-collision, `AIT-T0068` through `AIT-T0070` package the query no-collision and exact raw-budget endpoint under predecessor injectivity, and `AIT-T0071` through `AIT-T0075` prove the numeric `window < n` condition that supplies that injectivity for the generated lag candidates. The report now separates query-indexed candidate count, exact theorem-side unique lag-candidate count, exact theorem-side unique query-candidate count, coil-residue no-collision, local/coil disjointness, predecessor-map injectivity, no-collision flags, the theorem-backed raw upper bound `local_window + path_length * number_of_strides`, the raw-budget shortfall incompleteness guard, and the tighter theorem-backed `min(context, raw_budget)` cap. This is the practical point of the Phase VIII upgrade: the artifact reports hits and holes, preserves known coverage under conservative budget increases, and exposes candidate-budget assumptions instead of only showing successful examples.

`AIT-T0108` backs the sidecar field `query_count_le_unique_lag_count`. It says the query-indexed predecessor list is a finite image of the lag-candidate list, so deduplication after mapping cannot create a larger unique candidate set than the lag-side source.

`AIT-T0111` backs the sidecar field `unique_lag_count_shortfall_certifies_incomplete`. It is the collision-aware companion to `AIT-T0110`: raw generator budget is only an upper accounting layer, while the deduplicated unique lag-candidate count is the actual finite source that would have to cover every positive lag.

`AIT-T0112` backs the sidecar fields `theorem_side_lag_candidates_positive_in_context` and `unique_lag_count_matches_complete_under_candidate_range`. The first field is the theorem hypothesis; the second checks the theorem conclusion in executable form.

The same sidecar now includes a positive PASS certificate: `C_9`, local window `2`, path length `2`, and strides `(3,4,7)`. Its theorem-side candidate sequence is `1,2,3,6,4,8,7,5`, so every positive lag below `9` appears exactly once. `AIT-T0086` proves the uncovered-list is empty, `AIT-T0087` turns that into complete context coverage, and `AIT-T0088`/`AIT-T0089` prove the lag-side and query-side deduplicated counts equal the raw budget `8`. This is still only a finite candidate-set certificate, but it gives the sparse contract both a checked GAPS example and a checked PASS example.

The planner-style rows extend that same certificate shape to larger declared layouts without adding a new theorem claim. For `context = 4096`, `local_window = 32`, `path_length = 4`, and strides `(64,320,1500)`, the report records `44` candidates per query, `44` covered lags, `4051` uncovered lags, `13` uncovered intervals, and raw-budget survival on both the lag and query sides. For `context = 8192`, `local_window = 64`, `path_length = 8`, and strides `(127,509,1021,2039)`, it records `96` candidates per query, `96` covered lags, `8095` uncovered lags, `32` uncovered intervals, and the same raw-budget survival flags. In both rows, the raw budget and unique lag-candidate count are far below `context - 1`, and the generated candidates satisfy the positive in-context range hypothesis, so `AIT-T0110` through `AIT-T0112` certify incompleteness before inspecting individual lag witnesses. These are examples of how an engineer should read the contract: the budget may be exactly certified while coverage remains deliberately partial.

This fixture checks multi-stride candidate-set reachability and budget only. It is not evidence that stride-family sparse attention improves neural attention quality, long-context behavior, throughput, runtime, memory use, or model quality.

`AIM-B0010` adds a deterministic learned content-gate retrieval fixture. It fits a phase-to-route lookup table from training queries, then uses that learned table to choose coil or local candidates on held-out queries. The fixture reports route accuracy, retrieval reachability, static coil/local baselines, wrong-period and flipped-gate controls, union and full-attention baselines, and candidate-budget diagnostics.

This fixture checks whether the benchmark harness can learn a constructed finite route table. It is not evidence that a neural learned gate improves retrieval quality, attention quality, context length, memory use, runtime, or parameter efficiency.

`AIM-B0003` adds a deterministic looped-recurrence schedule fixture. The positive synthetic task assigns each sample a required recurrence depth. The fixture compares single-pass, fixed-loop, adaptive-exit, recurrent-memory, sparse phase-router, and over-looped controls. The adaptive-exit and recurrent-memory controls can retain the successful intermediate step; the over-looped control deliberately demonstrates degradation after the overthinking boundary. A nonperiodic scalar-threshold control checks that loop phase is not treated as useful when the target is ordinary scalar structure.

This fixture checks schedule bookkeeping only. It is not evidence that looped transformers improve reasoning, language-model quality, context length, runtime, memory use, or parameter efficiency.

`AIM-B0011` adds a deterministic loop-exit certificate fixture for one synthetic sample plus a fixed-budget no-exit control. It records required depth, score trace, exit availability, whether the exit is within budget, whether the exit stays within the overthinking guardrail, the first active trace step, whether exit availability matches existence of that first active step inside the budget, and whether no exit is equivalent to no active in-budget step. `AIM-T0084` proves the trace-side first-active iff: the first active score step is exactly the required loop depth. `AIM-T0085` proves the budgeted bridge: loop-exit availability is equivalent to existence of that first active step within `maxLoops`. `AIM-T0090` proves the failure-side bridge: no loop exit is available exactly when every step inside the max-loop budget is outside the active score band.

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
