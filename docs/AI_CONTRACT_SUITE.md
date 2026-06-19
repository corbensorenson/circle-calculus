# Circle Calculus AI Contract Suite

This document is the compact working entry point for the proof-carrying AI contracts. It is for using the contracts, not for reading every theorem.

The guided suite starts with four v0.2 flagship contracts:

| Contract | Question | CLI | Living Book lesson |
| --- | --- | --- | --- |
| RoPE position distinguishability | Do declared rotary phase channels distinguish all positions in a finite context? | `scripts/rope_certify.py` and `scripts/phase_bank_certify.py` | `site/chapters/applications/rope_certifier.qmd` |
| KV-cache ring-buffer freshness plus sink-window policy | Are requested cache tokens live, duplicate-free where required, free of stale same-slot overwrites, and optionally generated from pinned seen sink tokens plus the rolling window? | `scripts/kv_cache_certify.py` | `site/chapters/applications/kv_cache_ring_buffer.qmd` |
| Sparse-attention coverage | Which positive lags are covered, which are gaps, and what budget/count facts explain the plan? | `scripts/stride_family_certify.py` | `site/chapters/applications/sparse_attention_contract.qmd` |
| Looped recurrence schedules | Which loop depth, exit step, active work count, inactive-token count, and whole-period shift invariants does a finite recurrence plan expose? | `scripts/recurrence_schedule_certify.py` | `site/chapters/applications/looped_recurrence_contracts.qmd` |

The common contract shape is:

```text
engineering object
  -> finite circular address space
  -> repeated action, stride, period, or window
  -> theorem ids
  -> Python certificate
  -> explicit non-claims
```

These contracts are useful because they expose finite failure modes before training or deployment: collisions, stale reads, uncovered lags, duplicate candidate collapse, and exact count boundaries. They do not prove model quality.

The KV-cache contract intentionally includes both a passing retained read and a failing stale-read probe, so downstream consumers can test the success and rejection boundaries from the same theorem-backed schema.
The RoPE contract likewise includes D19 standard-channel request-classifier probes that mark `1/328459` as proved and `1/328458` as impossible at context `131072`, with the exact non-claim that this is a one-channel frontier rather than a full all-channel real-RoPE theorem.

For external projects, the standalone public pack is generated with:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
```

It writes `site/data/generated/circle_ai_contract_pack.json` and the JSON Schema
sidecar `site/data/generated/circle_ai_contract_pack.schema.json`. The pack uses
schema id `circle_calculus.ai_contract_pack.v0` and contains the four flagship
records above plus five broader integration fixtures for strided fanout, cyclic
memory, multicoil phase features, circulant/block-cyclic mixers, and seed-rule
regeneration with finite storage accounting for the public
`C_128` fixture plus bounded finite-search evidence for declared generator
candidates. Each record carries theorem ids, dictionary
ids, source docs, Living Book pages, CLI entrypoints, focused validation
commands, deterministic fields, and non-claims. The consumer rules live in
`docs/CIRCLE_AI_CONTRACTS_INTEGRATION.md`. The older
`site/data/generated/theseus_hive_ai_contracts.json` file is a compatibility
view for the optional private Theseus-Hive transfer lane, not the public center
of the suite.

For one contract kind, downstream tools can use the readiness CLI:

```bash
make circle-ai-contracts-ready
python scripts/example_validate_circle_ai_contract_pack_schema.py --summary
python scripts/circle_ai_contract_ready.py --list-recommendations
python scripts/circle_ai_contract_ready.py --fingerprints
python scripts/circle_ai_contract_ready.py --action-plan
python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --action-plan --include-values --format json
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --format json
python scripts/circle_ai_contract_ready.py --kind kv_cache_ring_buffer --digest --field stale_probe_first_stale_token --include-recommendations
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --digest --field first_uncovered_lag --include-recommendations
python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability --digest --format json --field d19_proved_request_status --field d19_impossible_request_status --include-field-metadata --include-recommendations
python scripts/circle_ai_contract_ready.py --kind strided_candidate_fanout --digest --field gcd --field predicted_reach --field full_coverage --field effective_candidate_budget --field candidate_budget_shortfall --field duplicate_count --include-recommendations
python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest --field same_residue_events --field same_residue_windings --field max_alias_load
python scripts/circle_ai_contract_ready.py --kind cyclic_memory_residue_winding --digest --field max_alias_load --include-recommendations
python scripts/circle_ai_contract_ready.py --kind multicoil_phase_feature --digest --field phase_tuple --field joint_repeat_horizon --field shifted_phase_tuple --field relative_phase --field shifted_relative_phase --include-recommendations
python scripts/circle_ai_contract_ready.py --kind circulant_block_cyclic_mixer --digest --field max_abs_dense_delta --field circulant_parameters --field dense_parameters --field block_cyclic_parameters --field block_to_dense_ratio --include-recommendations
python scripts/circle_ai_contract_ready.py --kind rope_position_distinguishability --digest --field d19_proved_request_status --field d19_impossible_request_status --include-recommendations
python scripts/circle_ai_contract_ready.py --kind recurrence_schedule --digest --field scheduled_work_saving --field post_period_multi_extension_scheduled_work_saving --include-recommendations
python scripts/circle_ai_contract_ready.py --kind recurrence_schedule --digest --field periodic_shift_required_steps_invariant --field periodic_shift_active_at_step_invariant
python scripts/circle_ai_contract_ready.py --kind seed_rule_exact_regeneration --digest --field storage_saving --include-recommendations
```

Python consumers can use the package-level adapter without importing repository
validation scripts:

```python
from circle_math.applications.circle_ai_contract_consumer import (
    contract_digest,
    load_contract_pack,
    planner_action_plan,
)

pack = load_contract_pack("site/data/generated/circle_ai_contract_pack.json")
digest = contract_digest(
    pack,
    "sparse_attention_coverage",
    include_field_metadata=True,
)
assert digest["ready_for_downstream_fixture_use"] is True
assert "field_catalog" in digest

planner = planner_action_plan(
    pack,
    ["sparse_attention_coverage"],
    include_values=True,
)
assert planner["action_plan"][0]["action_parameters"]["proposed_local_window"] == 6
```

Use `planner_action_plan` when another project needs a theorem-linked action
list as data rather than a shell command. The same adapter has a copyable
example CLI:

```bash
python scripts/example_consume_circle_ai_contract_pack.py \
  --kind rope_position_distinguishability \
  --field d19_proved_request_status \
  --field d19_impossible_request_status

python scripts/example_consume_circle_ai_contract_pack.py \
  --kind sparse_attention_coverage \
  --field first_uncovered_lag \
  --include-recommendations

python scripts/example_consume_circle_ai_contract_pack.py \
  --planner \
  --planner-kind sparse_attention_coverage \
  --planner-kind rope_position_distinguishability

python scripts/example_consume_circle_ai_contract_pack.py \
  --planner \
  --planner-kind sparse_attention_coverage \
  --planner-include-values
```

The pack also carries a small consumer gate:

```text
contract_schema.required_contract_keys
contract_schema.minimum_fields_by_kind
contract_schema.minimum_field_catalog_by_kind
contract_readiness_index.<kind>.ready_for_downstream_fixture_use
contract_readiness_index.<kind>.planner_recommendation_count
contract_readiness_index.<kind>.planner_recommendation_ids
contract_fingerprint_index.<kind>.content_fingerprint
planner_recommendation_index.<recommendation_id>.kind
planner_recommendation_index.<recommendation_id>.contract_id
planner_recommendation_index.<recommendation_id>.theorem_ids
planner_recommendation_index.<recommendation_id>.validation_commands
contract.consumer_check.ready_for_downstream_fixture_use
```

Use `python scripts/circle_ai_contract_ready.py --fingerprints` when another
project needs a stable audit-log value for the exact exported pack. The
fingerprints are deterministic `sha256-json-v1` hashes of the exported JSON
content with fingerprint fields excluded; they identify an artifact version but
do not replace theorem ids, manifests, or Lean proof checks.
Use `--expect-pack-fingerprint <sha256>` and
`--expect-contract-fingerprint kind=<sha256>` when downstream CI should fail if
the public pack or a selected contract record drifted.

A downstream project should fail fast if the readiness index or contract-level
`ready_for_downstream_fixture_use` is false. That gate only means the public
Circle fixture contains the minimum theorem-linked fields for its contract kind
and every cited theorem id resolves as proved; it is not a benchmark result.
`make circle-ai-contracts-check` validates that gate against the generated JSON
artifact, manifests, dictionary ids, source docs, Living Book pages, and Python
entrypoint paths. It also validates each contract's `proof_status` block so
downstream readers can require every cited theorem id to resolve to a manifest
entry marked `proved` or `lean_proved` without parsing Lean or YAML directly.
For non-Python consumers, `contract_schema.minimum_field_catalog_by_kind`
adds a machine-readable description, JSON value kind, and proof role for every
minimum field.
Contracts may also expose optional `planner_recommendations`. These are
structured convenience records over existing certificate fields and theorem ids.
The example consumer's `--planner` mode flattens those records into a
theorem-linked action plan with source trails, validation commands, and
non-claims, which is the preferred starting point for external planners that
want copy-safe Circle actions without knowing the per-contract JSON layout. Add
`--planner-include-values` when the planner needs the resolved theorem-linked
field values and recommendation-specific parameters; for the sparse first
interval repair this includes local window `6`, next uncovered lag `8`, and the
`AIT-T0104`/`AIT-T0166`/`AIT-T0167` theorem boundary.
For the RoPE fixture, they name the exact integer-period phase-bank audit and
the D19 standard-channel-0 margin frontier while preserving the non-claim that
neither is a full all-channel real-RoPE or model-quality proof. For the
sparse-attention fixture, they name the first-interval local-window repair
target and the dense-local complete-coverage fallback while preserving the
non-claim that neither is an architecture-performance recommendation.
For the strided-fanout fixture, they name the full-coverage stride-cycle audit
and the duplicate-collapsed budget audit while preserving the non-claim that
neither is a search-quality, retrieval-quality, routing-quality, or
model-quality proof.
For the multicoil phase fixture, they name the joint-repeat phase-tag audit
and the relative-phase common-shift audit. For the circulant/block-cyclic mixer
fixture, they name the circulant dense-parity audit and the block-cyclic
parameter-budget audit. These are finite fixture/accounting records, not
embedding-quality, speed, memory, hardware-efficiency, or model-quality claims.
For the KV-cache fixture, they name a stale requested-token rejection target
and a generated sink-plus-rolling-window request policy. For the cyclic-memory
fixture, they name a winding/provenance alias record and a finite slot-load
audit record. For the recurrence fixture, they name the active-token work
schedule and the whole-period index reuse witness. For the seed-rule fixture,
they name the exact-regeneration recipe, stable bounded-search candidate ids,
and the shorter-candidate selection. These records are integration hints over
theorem-backed finite fields, not model-quality, runtime, memory, retrieval,
compression, global-minimality, or reasoning claims.

## Minimum Consumer Fields

This checklist is guarded by `scripts/check_circle_ai_contract_docs.py`. Every
field listed here comes from
`contract_schema.minimum_fields_by_kind` in the generated contract pack. Field
descriptions and JSON value kinds come from
`contract_schema.minimum_field_catalog_by_kind`.

| Contract kind | Minimum fields to read |
| --- | --- |
| `rope_position_distinguishability` | `certificate_schema_id`, `exact_discrete_pass`, `common_collision_gap`, `total_bank_collision_pair_count`, `real_phase_margin_pass`, `worst_margin_radians`, `d19_proved_request_status`, `d19_proved_request_theorem_backed_classification`, `d19_impossible_request_status`, `d19_impossible_request_theorem_backed_classification`, `d19_margin_thresholds_ordered`, `d19_proved_impossible_branches_disjoint`, `d19_margin_status_exhaustive`, `proof_layers` |
| `kv_cache_ring_buffer` | `certificate_schema_id`, `adapter_request_pass`, `stale_requested_count`, `pass_iff_stale_count_zero_under_nonfuture_nodup`, `stale_probe_requested_tokens`, `stale_probe_requested_slots`, `stale_probe_pass`, `stale_probe_first_stale_token`, `stale_probe_first_stale_next_overwrite_token`, `stale_probe_stale_requested_count`, `stale_probe_stale_member_blocks_pass`, `stale_probe_pass_iff_stale_count_zero_under_nonfuture_nodup`, `stale_probe_fail_iff_stale_count_positive_under_nonfuture_nodup`, `sink_window_exact_policy`, `sink_window_tokens_distinct`, `sink_window_token_count`, `sink_window_token_count_bound`, `sink_window_token_count_le_sink_plus_cache`, `sink_window_disjoint_exact_token_count`, `sink_window_token_count_eq_sink_plus_live_window_when_disjoint`, `sink_prefix_disjoint_from_live_window`, `sink_rolling_tokens_retained`, `sink_tokens_are_seen_prefix`, `sink_tokens_non_future`, `sink_tokens_retained_by_policy`, `sink_tokens_outside_ordinary_rolling_window` |
| `sparse_attention_coverage` | `certificate_schema_id`, `coverage_complete`, `covered_lag_count`, `uncovered_lag_count`, `uncovered_lag_intervals`, `first_uncovered_lag`, `first_uncovered_interval_start`, `first_uncovered_interval_stop`, `first_uncovered_interval_length`, `local_window_needed_to_cover_first_uncovered_interval`, `first_uncovered_interval_additional_local_slots`, `first_uncovered_interval_repair_reaches_interval`, `first_interval_repair_next_uncovered_lag`, `first_interval_repair_still_has_gap`, `first_interval_repair_covers_context`, `largest_uncovered_interval_start`, `largest_uncovered_interval_stop`, `largest_uncovered_interval_length`, `local_window_needed_to_cover_largest_uncovered_interval`, `largest_uncovered_interval_additional_local_slots`, `largest_uncovered_interval_repair_reaches_interval`, `largest_interval_repair_next_uncovered_lag`, `largest_interval_repair_still_has_gap`, `largest_interval_repair_covers_context`, `largest_uncovered_interval_is_tail`, `first_gap_local_window_shortfall`, `local_window_needed_to_cover_first_gap`, `current_window_below_first_gap`, `first_gap_repair_window_reaches`, `first_gap_repair_window_covers_context`, `first_gap_repair_window_is_final_positive_lag`, `first_gap_repair_threshold_matches_final_lag`, `local_window_complete_coverage_threshold`, `local_window_complete_coverage_shortfall`, `local_window_reaches_complete_coverage_threshold`, `local_window_threshold_certifies_complete`, `local_window_complete_threshold_is_exact_local_minimum`, `complete_repair_window`, `complete_repair_window_additional_local_slots`, `complete_repair_window_covers_context`, `complete_repair_window_uses_dense_threshold`, `complete_repair_window_minimal_for_declared_stride_family`, `complete_repair_window_minimal_witness_lag`, `interval_repair_plan`, `interval_repair_plan_step_count`, `interval_repair_plan_final_window`, `interval_repair_plan_covers_context`, `interval_repair_plan_strictly_progresses`, `first_gap_repair_window_reaches_complete_threshold`, `raw_budget_shortfall_certifies_incomplete`, `lag_unique_plus_loss_eq_raw`, `query_unique_plus_loss_eq_raw`, `lag_collision_pair_count`, `query_collision_pair_count`, `lag_collision_pair_count_zero_iff_no_collision`, `lag_collision_pair_count_positive_iff_collision`, `lag_collision_pair_count_bounds_dedup_loss`, `lag_collision_pair_count_excess_over_dedup_loss`, `query_collision_pair_count_zero_iff_no_collision`, `query_collision_pair_count_positive_iff_collision`, `query_collision_pair_count_bounds_dedup_loss`, `query_collision_pair_count_excess_over_dedup_loss` |
| `strided_candidate_fanout` | `context_length`, `stride`, `candidate_budget`, `unique_candidate_count`, `effective_candidate_budget`, `duplicate_count`, `candidate_budget_accounting`, `effective_budget_matches_unique_candidates`, `candidate_budget_shortfall`, `effective_budget_reaches_predicted_reach`, `full_coverage`, `predicted_reach` |
| `recurrence_schedule` | `required_steps`, `exit_step`, `loop_period`, `overthinking_boundary`, `active_step_one_is_full_range`, `first_step_active_token_count`, `first_step_inactive_token_count`, `first_step_inactive_count_zero`, `work_count_step`, `work_step_active_token_count`, `work_step_inactive_token_count`, `work_step_active_inactive_count_eq_token_count`, `post_period_active_empty`, `post_period_active_token_count`, `post_period_inactive_token_count`, `post_period_inactive_count_eq_token_count`, `active_token_sets_descend`, `active_token_lists_nodup`, `active_token_counts_bounded`, `active_token_counts_descend`, `inactive_token_counts_ascend`, `total_work_horizon_steps`, `active_token_count_trace`, `inactive_token_count_trace`, `active_token_count_trace_sum`, `inactive_token_count_trace_sum`, `active_token_count_trace_sum_matches_total`, `inactive_token_count_trace_sum_matches_total`, `first_inactive_steps`, `first_inactive_steps_match_budget_successor`, `total_active_token_work`, `total_inactive_token_work`, `full_loop_token_work`, `scheduled_work_saving`, `scheduled_work_saving_accounting`, `active_inactive_work_accounting`, `scheduled_work_saving_matches_inactive_work`, `scheduled_work_saving_positive`, `active_work_below_full_loop_work`, `scheduled_work_saving_positive_iff_active_work_shortfall`, `scheduled_work_saving_zero`, `active_work_equals_full_loop_work`, `scheduled_work_saving_zero_iff_no_active_work_shortfall`, `public_fixture_4_8_2_active_token_count`, `public_fixture_4_8_2_inactive_token_count`, `public_fixture_4_8_2_accounting_eq_token_count`, `public_fixture_4_8_4_total_active_token_work`, `public_fixture_4_8_4_total_inactive_token_work`, `public_fixture_8_4_full_loop_token_work`, `public_fixture_4_8_4_scheduled_work_saving`, `public_fixture_4_8_4_work_saving_accounting`, `public_fixture_4_8_4_active_inactive_work_accounting`, `public_fixture_4_8_4_work_saving_matches_inactive_work`, `public_fixture_4_8_4_scheduled_work_saving_positive`, `public_fixture_4_8_4_active_work_below_full_loop_work`, `public_fixture_4_8_4_positive_saving_iff_active_work_shortfall`, `public_fixture_4_8_4_scheduled_work_saving_zero`, `public_fixture_4_8_4_active_work_equals_full_loop_work`, `public_fixture_4_8_4_zero_saving_iff_no_active_work_shortfall`, `default_fixture_5_8_5_total_active_token_work`, `default_fixture_5_8_5_total_inactive_token_work`, `default_fixture_8_5_full_loop_token_work`, `default_fixture_5_8_5_scheduled_work_saving`, `default_fixture_5_8_5_work_saving_accounting`, `default_fixture_5_8_5_active_inactive_work_accounting`, `default_fixture_5_8_5_work_saving_matches_inactive_work`, `post_period_extension_horizon_steps`, `post_period_extension_total_active_token_work`, `post_period_extension_total_inactive_token_work`, `post_period_extension_full_loop_token_work`, `post_period_extension_scheduled_work_saving`, `post_period_extension_active_work_unchanged`, `post_period_extension_inactive_work_added_token_count`, `post_period_extension_saving_added_token_count`, `default_fixture_5_8_6_total_active_token_work`, `default_fixture_5_8_6_scheduled_work_saving`, `default_fixture_5_8_6_active_work_unchanged`, `default_fixture_5_8_6_saving_added_token_count`, `post_period_extra_steps`, `post_period_multi_extension_horizon_steps`, `post_period_multi_extension_total_active_token_work`, `post_period_multi_extension_total_inactive_token_work`, `post_period_multi_extension_full_loop_token_work`, `post_period_multi_extension_scheduled_work_saving`, `post_period_multi_extension_active_work_unchanged`, `post_period_multi_extension_inactive_work_added_extra_token_count`, `post_period_multi_extension_saving_added_extra_token_count`, `default_fixture_5_8_8_total_active_token_work`, `default_fixture_5_8_8_scheduled_work_saving`, `default_fixture_5_8_8_active_work_unchanged`, `default_fixture_5_8_8_saving_added_extra_token_count`, `periodic_shift_base_token`, `periodic_shift_passes`, `periodic_shift_amount`, `periodic_shifted_token`, `periodic_shift_required_steps_invariant`, `periodic_shift_recurrence_budget_invariant`, `periodic_shift_training_free_budget_invariant`, `periodic_shift_exit_step_invariant`, `periodic_shift_overthinking_boundary_invariant`, `periodic_shift_active_step`, `periodic_shift_active_at_step_invariant` |
| `cyclic_memory_residue_winding` | `bank_size`, `event_count`, `residue_slot`, `winding`, `same_residue_events`, `same_residue_windings`, `max_alias_load` |
| `multicoil_phase_feature` | `periods`, `position`, `phase_tuple`, `shifted_position`, `shifted_phase_tuple`, `joint_repeat_horizon`, `relative_period` |
| `circulant_block_cyclic_mixer` | `period`, `input_values`, `kernel_values`, `circulant_output`, `dense_output`, `max_abs_dense_delta`, `dense_parameters`, `circulant_parameters`, `circulant_parameter_ratio` |
| `seed_rule_exact_regeneration` | `artifact_id`, `fixture_n`, `seed`, `rules`, `generated_object`, `regenerated_object`, `exact_regeneration`, `explicit_length`, `generator_length`, `storage_saving`, `storage_saving_positive`, `generator_shorter`, `generator_shorter_iff_positive_saving`, `storage_saving_add_generator_length_eq_explicit_length`, `bounded_search_id`, `bounded_search_finite_search_space`, `bounded_search_candidate_count`, `bounded_search_exact_candidate_count`, `bounded_search_exact_candidate_count_le_candidate_count`, `bounded_search_has_best_exact`, `bounded_search_best_exact_exists_iff_exact_count_positive`, `bounded_search_best_exact_implies_candidate_count_positive`, `bounded_search_best_exact_artifact_id`, `bounded_search_best_exact_candidate_id`, `bounded_search_best_exact_regenerates`, `bounded_search_has_best_shorter`, `bounded_search_best_shorter_artifact_id`, `bounded_search_best_shorter_candidate_id`, `bounded_search_best_shorter_generator_shorter`, `bounded_search_candidates`, `bounded_search_candidate_ids_by_generator_length`, `bounded_search_exact_candidate_ids_by_generator_length`, `bounded_search_shorter_candidate_ids_by_generator_length`, `closure_condition` |

## Report Reading Pattern

Every report should be read in this order:

1. contract status;
2. `consumer_check.ready_for_downstream_fixture_use` in the generated pack;
3. main evidence fields;
4. optional `planner_recommendations`, when present;
5. theorem ids and Lean declaration names when emitted;
6. explicit boundary/non-claim text.

Representative field shapes:

```text
exact_discrete_contract=FAIL common_collision_gap=114 total_bank_collision_pair_count=14
adapter_request_trace=PASS stale_requested_count=0 sink_window_policy=PINNED_PREFIX_PLUS_ROLLING
stride_family_contract=GAPS uncovered_lags=109 first_gap=5 raw_budget_shortfall=True
local_window_complete_threshold=threshold=119 shortfall=115 exact_local_minimum=True first_gap_repair_reaches_threshold=False repair_threshold_matches_final_lag=True
complete_local_repair=window=119 additional_slots=115 covers_context=True uses_dense_threshold=True exact_local_minimum=True
strided_candidate_fanout_contract=READY context_length=12 stride=5 gcd=1 predicted_reach=12 full_coverage=True effective_candidate_budget=12 duplicate_count=0 candidate_budget_shortfall=0
recurrence_schedule=READY work_step=2 active=6 inactive=2 active_plus_inactive_eq_token_count=True
recurrence_work_budget=total_active_token_work=21 total_inactive_token_work=19 full_loop_token_work=40 scheduled_work_saving=19
recurrence_periodic_shift=base_token=7 passes=3 shifted_token=22 required_steps_invariant=True recurrence_budget_invariant=True active_at_step_invariant=True
cyclic_memory_contract=READY bank_size=8 event_index=23 event_count=32 residue_slot=7 winding=2
cyclic_memory_alias_class=same_residue_events=(7,15,23,31) same_residue_windings=(0,1,2,3) max_alias_load=4
multicoil_phase_feature_contract=READY periods=(5,7) phase_tuple=(2,2) joint_repeat_horizon=35 relative_phase=3
circulant_block_cyclic_mixer_contract=READY max_abs_dense_delta=0 circulant_parameters=8 dense_parameters=64 block_cyclic_parameters=128
seed_rule_contract=READY artifact_id=finite_circle fixture_n=128 exact_regeneration=True generator_shorter=True
seed_rule_bounded_search=candidate_count=3 exact_candidate_count=2 has_best_exact=True has_best_shorter=True
seed_rule_candidate_ranking=best_exact=finite_circle_unit_fixture best_shorter=finite_circle_public_fixture
```

The text report is for humans; the JSON report is for tools. Neither replaces the Lean proof source.

## 1. RoPE Position Distinguishability

Run:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --head-dim 128 --base 10000 --context 32768 --tolerance 1e-6
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
```

The main JSON certificate schema is:

```text
circle_calculus.rope_position_distinguishability.v0
```

The exact-only integer phase-bank schema is:

```text
circle_calculus.integer_phase_bank_distinguishability.v0
```

Related real-phase certificate-object schemas include:

```text
circle_calculus.rational_turn_ratio_finite_margin.v0
circle_calculus.standard_rope_interval_margin.v0
circle_calculus.standard_rope_channel0_d19_bank_bridge.v0
circle_calculus.standard_rope_channel0_d19_margin_bracket.v0
```

Core theorem cluster:

- `AIRA-T0021`: one-channel discrete collision iff period divides the gap.
- `AIRA-T0024`: phase-bank collision iff every declared period divides the gap.
- `AIRA-T0036`: the period-bank LCM gives the shared collision period.
- `AIRA-T0179` and `AIRA-T0180`: positive-period policy and exact pass/fail iff for the integer-period bank.
- `AIRA-T0203` through `AIRA-T0213`: zero/positive count semantics and closed-form collision-count fields.
- `AIRA-T0214` and `AIRA-T0215`: reusable exact-weakest-gap report contracts.
- `AIRA-T0216` and `AIRA-T0217`: request-level D19 standard-channel classifier bridge.
- `AIRA-T0222` through `AIRA-T0231`: exact rational, full-denominator margin/obstruction, and exact weakest-gap request-threshold contracts.

Non-claims:

- The exact pass/fail contract is for the declared integer-period phase-bank model.
- Numerical real-phase scans are diagnostics unless a named theorem-backed real-phase certificate is cited.
- The suite does not prove longer context, lower perplexity, speed, memory savings, or model quality.

Sample text fields:

```text
exact_discrete_contract=FAIL
common_collision_gap=114
total_bank_collision_pair_count=14
sample_collision_pairs=((0, 114), ...)
theorem_ids=AIRA-T0021,AIRA-T0024,AIRA-T0036,...
```

## 2. KV-Cache Ring-Buffer Freshness

Run:

```bash
python scripts/kv_cache_certify.py \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --sink-size 4 \
  --request-id prefill_read
```

Machine-readable output:

```bash
python scripts/kv_cache_certify.py \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --sink-size 4 \
  --request-id prefill_read \
  --format json \
  --json-out reports/kv_cache_certificate.json
```

The top-level JSON schema is:

```text
circle_calculus.kv_cache_ring_buffer_certificate.v0
```

Core theorem cluster:

- `AIM-T0069`: retained-window boundary for a token in a ring buffer.
- `AIM-T0074`: generated live-window membership exactness.
- `AIM-T0079`: trace-fresh duplicate-free read-batch slot distinctness.
- `AIM-T0080` through `AIM-T0083`: generated live-window slot distinctness and full-coverage contracts.
- `AIM-T0091` and `AIM-T0092`: next-overwrite trace freshness for single tokens and batches.
- `AIM-T0097` and `AIM-T0098`: stale requested member rejection and no-stale-member pass iff.
- `AIM-T0102` and `AIM-T0103`: pass iff stale-count zero and failure iff stale-count positive under the stated request assumptions.
- `AIM-T0104`, `AIM-T0105`, `AIM-T0108`, `AIM-T0109`, `AIM-T0110`, `AIM-T0117` through `AIM-T0119`, `AIM-T0136`, `AIM-T0137`, `AIM-T0148`, and `AIM-T0149`: exact generated sink-window policy membership, the public fixture with sink tokens `0..3` followed by rolling tokens `16..31`, retained rolling-suffix freshness, duplicate-free default and general sink-window request lists, the general `sink_size + cache_size` request-size bound, the public exact `20`-token request-size fixture, the exact `sink_size + live_window_length` count condition when the fully seen sink prefix lies before the rolling live window, explicit non-future/policy-retained facts for generated pinned sink-prefix tokens, and the distinction that those pinned prefix tokens are outside ordinary rolling-window retention in the default disjoint fixture.

Non-claims:

- The certifier proves finite indexing and freshness facts for a modeled request.
- It is not a paging policy, GPU/kernel proof, serving-stack proof, retrieval-quality result, memory-saving result, throughput result, deployment-safety result, or model-quality result.
- The sink-window mode does not prove StreamingLLM quality or sink-token usefulness; it only proves the finite generated request-list policy.

Sample text fields:

```text
kv_cache_contract=LIVE cache_size=16 current=31 token=20 slot=4
adapter_request_trace=PASS tokens=(20, 24, 29, 31)
stale_requested_count=0
sink_window_policy=PINNED_PREFIX_PLUS_ROLLING sink_size=4
tokens_distinct=True
token_count=20 token_count_bound=20 token_count_le_sink_plus_cache=True
disjoint_exact_token_count=20 token_count_eq_sink_plus_live_window_when_disjoint=True
sink_tokens_non_future=True sink_tokens_retained_by_policy=True
theorem_ids=AIM-T0069,AIM-T0097,AIM-T0102,AIM-T0104,AIM-T0108,AIM-T0110,...
```

## 3. Sparse-Attention Coverage

Run:

```bash
python scripts/stride_family_certify.py \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 4
```

Machine-readable output:

```bash
python scripts/stride_family_certify.py \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 4 \
  --format json \
  --json-out reports/stride_family_certificate.json
```

The top-level JSON schema is:

```text
circle_calculus.stride_family_sparse_attention_certificate.v0
```

The v0.1 contract fields are documented in `docs/SPARSE_ATTENTION_CERTIFIER_QUICKSTART.md`.

Core theorem cluster:

- `AIT-T0020`: abstract gap iff for sparse coverage.
- `AIT-T0078`: positive-lag range coverage iff via the theorem-side candidate list.
- `AIT-T0023` and `AIT-T0034`: the dense-local threshold is exactly `context - 1`, and reaching it certifies complete local+stride-family coverage.
- `AIT-T0090` through `AIT-T0097`: covered/uncovered list semantics, partition, complete-count iff, and gap-witness count iff.
- `AIT-T0110` and `AIT-T0111`: raw and deduplicated budget shortfall incompleteness criteria.
- `AIT-T0112` through `AIT-T0125`: candidate-range and shortfall iff endpoints.
- `AIT-T0126` through `AIT-T0138`: no-zero residue, period-threshold, witness, and zero-residue count formulas.
- `AIT-T0145` through `AIT-T0150`: lag/query dedup-loss zero/positive iff no-collision/collision endpoints, plus exact unique-plus-loss-equals-raw accounting.
- `AIT-T0151` through `AIT-T0154`: exact fixture collision-pair counts for the default no-collision sparse plan and the public `C_16` alias probe.
- `AIT-T0155` through `AIT-T0158`: general lag/query pair-collision zero/positive iff no-collision/collision endpoints.
- `AIT-T0159` and `AIT-T0160`: lag/query pair-collision counts bound ordinary deduplication loss, so the pair-count field is a severity metric at least as strong as the lost-candidate count.
- `AIT-T0161` and `AIT-T0162`: first-gap local-window repair fields. A reported first gap is beyond the current local window, and using that lag as the local-window width reaches that specific lag. This is planner advice for the first gap, not a full-coverage claim.

Non-claims:

- The certifier proves finite candidate-set coverage, gap witnesses, and budget/count facts for a declared plan.
- It does not prove attention quality, long-context capability, throughput, runtime, memory savings, or model quality.

Sample text fields:

```text
stride_family_contract=GAPS context=120 strides=(7, 13)
covered_lags=10 uncovered_lags=109 first_gap=5
raw_budget_shortfall=True certifies_incomplete=True
unique_lag_shortfall=True certifies_incomplete=True
collision_pair_counts=lag=0 query=0
collision_pair_severity=lag_bounds_dedup_loss=True lag_excess_over_dedup_loss=0 query_bounds_dedup_loss=True query_excess_over_dedup_loss=0
first_gap_local_repair=shortfall=1 needed_window=5 current_window_below_first_gap=True repair_window_reaches_first_gap=True repair_window_covers_context=False repair_window_is_final_positive_lag=False repair_threshold_matches_final_lag=True
local_window_complete_threshold=threshold=119 shortfall=115 reaches_threshold=False threshold_certifies_complete=False exact_local_minimum=True first_gap_repair_reaches_threshold=False repair_threshold_matches_final_lag=True
complete_local_repair=window=119 additional_slots=115 covers_context=True uses_dense_threshold=True exact_local_minimum=True
theorem_ids=AIT-T0020,AIT-T0078,AIT-T0110,AIT-T0111,...
```

## 4. Looped Recurrence Schedule

Run:

```bash
python scripts/recurrence_schedule_certify.py
python scripts/recurrence_schedule_certify.py --format json
python scripts/export_circle_ai_contracts.py
python scripts/check_circle_ai_contract_pack.py --summary --require-kind recurrence_schedule
```

The standalone recurrence certifier emits one generic contract object. The
same recurrence schedule also lives in the generic pack:

```text
circle_calculus.ai_contract_pack.v0
```

Core theorem cluster:

- `AIM-T0111` and `AIM-T0112`: first-step and post-period active-token list boundaries.
- `AIM-T0026` through `AIM-T0030`, plus `AIM-T0033`, `AIM-T0034`, and `AIM-T0036`: shifting a sample or token by whole loop periods preserves required steps, recurrence budget, wrapper budget, exit availability, exit certificate fields, guardrail boundary, and active-step membership.
- `AIM-T0113` and `AIM-T0114`: token activity and active-token lists are monotone in the loop step.
- `AIM-T0115` and `AIM-T0116`: generated active-token lists are duplicate-free and bounded by the token count.
- `AIM-T0120` through `AIM-T0125`, plus `AIM-T0128` and `AIM-T0129`: active/inactive work counts are bounded, exact at the first and overrun boundaries, monotone in the expected directions, and satisfy active plus inactive equals the declared token count.
- `AIM-T0126` and `AIM-T0127`: the public `loop_period=4`, `token_count=8`, `step=2` fixture has active count `6` and inactive count `2`.
- `AIM-T0130`, `AIM-T0131`, `AIM-T0144`, `AIM-T0145`, `AIM-T0138`, and `AIM-T0139`: finite work-budget accounting, saved-work accounting, active-plus-inactive work accounting, saved-work-is-inactive-work accounting, the positive-saving iff, and the zero-saving iff used by planner-facing reports.
- `AIM-T0132` through `AIM-T0135`, plus `AIM-T0146`: the public `loop_period=4`, `token_count=8`, `steps=4` fixture has `20` active token-steps, `32` fixed-depth token-steps, and `12` inactive/saved token-steps.
- `AIM-T0140` through `AIM-T0143`, plus `AIM-T0147`: the default exported `loop_period=5`, `token_count=8`, `steps=5` recurrence fixture has `21` active token-steps, `40` fixed-depth token-steps, and `19` inactive/saved token-steps with exact accounting.
- `AIM-T0150` through `AIM-T0154`: after the loop-period boundary, extending the horizon by one step adds no active-token work, adds one full token count of inactive work, and raises the default fixture's scheduled-work saving from `19` to `27`.
- `AIM-T0155` through `AIM-T0159`: after the loop-period boundary, extending by any declared number of extra steps adds no active-token work and increases inactive/saved work by `extra_steps * token_count`; the default `horizon=8` fixture raises scheduled-work saving from `19` to `43`.

Non-claims:

- The recurrence contract proves finite schedule accounting, not recursive reasoning or adaptive-exit quality.
- It does not prove perplexity, context length, speed, memory savings, throughput, model quality, or a trained router.

Sample JSON fields:

```text
kind=recurrence_schedule
required_steps=4 exit_step=4 overthinking_boundary=5
work_count_step=2 work_step_active_token_count=6 work_step_inactive_token_count=2
work_step_active_inactive_count_eq_token_count=True
total_active_token_work=21 total_inactive_token_work=19 full_loop_token_work=40 scheduled_work_saving=19
scheduled_work_saving_accounting=True active_inactive_work_accounting=True scheduled_work_saving_matches_inactive_work=True
scheduled_work_saving_positive=True active_work_below_full_loop_work=True scheduled_work_saving_positive_iff_active_work_shortfall=True
scheduled_work_saving_zero=False active_work_equals_full_loop_work=False scheduled_work_saving_zero_iff_no_active_work_shortfall=True
active_token_counts_descend=True inactive_token_counts_ascend=True
post_period_active_token_count=0 post_period_inactive_token_count=8
public_fixture_4_8_2_active_token_count=6 public_fixture_4_8_2_inactive_token_count=2
public_fixture_4_8_4_total_active_token_work=20 public_fixture_4_8_4_total_inactive_token_work=12 public_fixture_8_4_full_loop_token_work=32 public_fixture_4_8_4_scheduled_work_saving=12
default_fixture_5_8_5_total_active_token_work=21 default_fixture_5_8_5_total_inactive_token_work=19 default_fixture_8_5_full_loop_token_work=40 default_fixture_5_8_5_scheduled_work_saving=19
post_period_extension_horizon_steps=6 post_period_extension_total_active_token_work=21 post_period_extension_total_inactive_token_work=27 post_period_extension_full_loop_token_work=48 post_period_extension_scheduled_work_saving=27
post_period_extension_active_work_unchanged=True post_period_extension_inactive_work_added_token_count=True post_period_extension_saving_added_token_count=True
post_period_extra_steps=3 post_period_multi_extension_horizon_steps=8 post_period_multi_extension_scheduled_work_saving=43
post_period_multi_extension_active_work_unchanged=True post_period_multi_extension_saving_added_extra_token_count=True
periodic_shift_base_token=7 periodic_shift_passes=3 periodic_shift_amount=15 periodic_shifted_token=22
periodic_shift_required_steps_invariant=True periodic_shift_recurrence_budget_invariant=True periodic_shift_training_free_budget_invariant=True periodic_shift_exit_step_invariant=True periodic_shift_overthinking_boundary_invariant=True periodic_shift_active_at_step_invariant=True
planner_recommendations=RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE,RECURRENCE-REUSE-WHOLE-PERIOD-SHIFT
theorem_ids=AIM-T0026,AIM-T0027,AIM-T0028,AIM-T0029,AIM-T0030,AIM-T0033,AIM-T0034,AIM-T0036,AIM-T0111,AIM-T0112,AIM-T0120,AIM-T0123,AIM-T0128,AIM-T0129,AIM-T0126,AIM-T0127,AIM-T0130,AIM-T0131,AIM-T0144,AIM-T0145,AIM-T0138,AIM-T0139,AIM-T0132,AIM-T0133,AIM-T0134,AIM-T0146,AIM-T0135,AIM-T0140,AIM-T0141,AIM-T0142,AIM-T0147,AIM-T0143,...
```

## Working Rule

Use the suite in this order:

1. Run the relevant CLI and save text or JSON output.
2. Check that the report names theorem ids.
3. Run `make circle-ai-contracts-check` for the generated suite-level JSON pack.
4. Check that each theorem id exists in the generated theorem index or manifest.
5. Read the corresponding Living Book lesson for the concept and claim boundary.
6. Use `make targeted-check` during iteration and `make check` before release-grade commits.

If a report field is not backed by a theorem id, treat it as executable support or diagnostic evidence, not as a formal result.
