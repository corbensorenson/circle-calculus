# Circle AI Contracts Integration Guide

This guide explains how an external AI or math project can consume Circle
Calculus contracts without depending on Lean internals or on any private
Theseus-Hive workflow.

The public contract pack is:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
```

That writes:

```text
site/data/generated/circle_ai_contract_pack.json
site/data/generated/circle_ai_contract_pack.schema.json
```

The schema id is:

```text
circle_calculus.ai_contract_pack.v0
```

Validate the pack shape without importing Circle modules:

```bash
python scripts/example_validate_circle_ai_contract_pack_schema.py --summary
```

The older Theseus-Hive export remains available only as a compatibility view:

```bash
make theseus-ai-contracts
```

## What A Consumer Gets

The public pack currently exports nine contract families: `rope_position_distinguishability`, `kv_cache_ring_buffer`, `sparse_attention_coverage`, `recurrence_schedule`, `strided_candidate_fanout`, `cyclic_memory_residue_winding`, `multicoil_phase_feature`, `circulant_block_cyclic_mixer`, and `seed_rule_exact_regeneration`.

Each contract record contains:

- `id`: a generic Circle contract id such as `CC-AI-CONTRACT-FANOUT-001`;
- `kind`: the contract family;
- `status`: currently `fixture`;
- `content_fingerprint_algorithm` and `content_fingerprint`: deterministic
  `sha256-json-v1` artifact fingerprints for audit logs;
- `theorem_ids`: manifest theorem ids that support the structural facts;
- `proof_status`: resolved theorem status, Lean declaration names, and proved/not-proved
  flags generated from the manifests;
- `dictionary_ids`: vocabulary dependencies;
- `fields`: deterministic certificate data;
- `contract_passed`: whether the fixture satisfies its stated finite contract;
- `consumer_check`: the minimum-field gate a downstream consumer should verify;
- `integration_use`: the intended external use;
- `ordinary_baselines`: baseline categories a downstream experiment should compare against;
- `source_paper`, `quickstart_docs`, `living_book_pages`, and `entrypoints`:
  local source trails and command-line entrypoints for non-Lean consumers;
- `validation_commands`: focused commands for rechecking this contract without
  running the entire repository gate;
- `not_claimed`: the claim boundary;
- `compatibility_ids`: downstream aliases, currently including the older Theseus-Hive ids.

The top-level pack also carries `pack_content_fingerprint` and
`contract_fingerprint_index`, so a consumer can log the exact exported pack and
the exact contract records it used.

The pack is configuration and evidence metadata. It is not a model benchmark.

## Minimal Consumer Pattern

An external project should treat the pack as read-only input:

```python
import json
from pathlib import Path

pack = json.loads(Path("site/data/generated/circle_ai_contract_pack.json").read_text())
assert pack["schema_id"] == "circle_calculus.ai_contract_pack.v0"

for contract in pack["contracts"]:
    assert contract["contract_passed"] is True
    assert contract["consumer_check"]["ready_for_downstream_fixture_use"] is True
    theorem_ids = contract["theorem_ids"]
    assert contract["proof_status"]["all_theorem_ids_resolved"] is True
    assert contract["proof_status"]["all_theorem_ids_proved"] is True
    fields = contract["fields"]
    print(contract["id"], contract["kind"], theorem_ids, fields.keys())
```

Then the project can attach its own private or public workload rows beside the
Circle contract id. Do not copy private payloads back into this repository.

## Consumer Readiness Gate

The pack now includes a machine-readable schema summary:

```python
schema = pack["contract_schema"]
required_keys = schema["required_contract_keys"]
minimum_fields_by_kind = schema["minimum_fields_by_kind"]
minimum_field_catalog_by_kind = schema["minimum_field_catalog_by_kind"]
```

Use `minimum_field_catalog_by_kind[kind][field]` when wiring a non-Python
consumer. Each catalog entry carries a short description, the JSON value kind
observed in the generated pack, and the field's proof role.

For fast downstream gating, read the top-level readiness index first:

```python
readiness = pack["contract_readiness_index"]["sparse_attention_coverage"]
assert readiness["ready_for_downstream_fixture_use"] is True
assert readiness["all_theorem_ids_resolved"] is True
assert readiness["all_theorem_ids_proved"] is True
assert readiness["missing_minimum_field_count"] == 0
assert readiness["unresolved_theorem_count"] == 0
assert readiness["unproved_theorem_count"] == 0
assert readiness["planner_recommendation_count"] == 4
assert "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR" in readiness["planner_recommendation_ids"]
assert "SPARSE-REPAIR-LARGEST-GAP-INTERVAL" in readiness["planner_recommendation_ids"]
assert "SPARSE-INTERVAL-REPAIR-PATH" in readiness["planner_recommendation_ids"]

rope = pack["contract_readiness_index"]["rope_position_distinguishability"]
assert rope["planner_recommendation_count"] == 2
assert "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK" in rope["planner_recommendation_ids"]
memory = pack["contract_readiness_index"]["cyclic_memory_residue_winding"]
assert memory["planner_recommendation_count"] == 2
assert "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE" in memory["planner_recommendation_ids"]
fanout = pack["contract_readiness_index"]["strided_candidate_fanout"]
assert fanout["planner_recommendation_count"] == 2
assert "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE" in fanout["planner_recommendation_ids"]
phase = pack["contract_readiness_index"]["multicoil_phase_feature"]
assert phase["planner_recommendation_count"] == 2
assert "PHASE-USE-JOINT-REPEAT-HORIZON" in phase["planner_recommendation_ids"]
mixer = pack["contract_readiness_index"]["circulant_block_cyclic_mixer"]
assert mixer["planner_recommendation_count"] == 2
assert "MIXER-AUDIT-CIRCULANT-DENSE-PARITY" in mixer["planner_recommendation_ids"]
recurrence = pack["contract_readiness_index"]["recurrence_schedule"]
assert recurrence["planner_recommendation_count"] == 2
assert "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE" in recurrence["planner_recommendation_ids"]
seed_rule = pack["contract_readiness_index"]["seed_rule_exact_regeneration"]
assert seed_rule["planner_recommendation_count"] == 2
assert "SEED-RULE-USE-EXACT-REGENERATION-RECIPE" in seed_rule["planner_recommendation_ids"]
assert "SEED-RULE-SELECT-BOUNDED-SHORTER-CANDIDATE" in seed_rule["planner_recommendation_ids"]
```

For action discovery across the whole pack, read the top-level recommendation
index before opening individual contract records:

```python
recommendations = pack["planner_recommendation_index"]
rope_frontier = recommendations["ROPE-USE-D19-MARGIN-FRONTIER"]
assert rope_frontier["kind"] == "rope_position_distinguishability"
assert rope_frontier["contract_id"] == "CC-AI-CONTRACT-ROPE-001"
assert rope_frontier["ready_for_downstream_fixture_use"] is True
assert "AIRA-T0216" in rope_frontier["theorem_ids"]
```

Then open the full contract record only when the gate is ready and you need
fields, theorem ids, source links, or non-claim text.

Each contract then carries:

```python
check = contract["consumer_check"]
assert check["missing_minimum_fields"] == []
assert check["required_fields_present"] is True
assert check["all_theorem_ids_resolved"] is True
assert check["all_theorem_ids_proved"] is True
assert check["ready_for_downstream_fixture_use"] is True
```

This is the intended first gate for a project such as Theseus-Hive or any other
AI/math consumer. It says the Circle fixture has the minimum public evidence
fields for that contract kind and that every cited theorem id resolves to a
manifest entry marked `proved` or `lean_proved`. It does not say that the
downstream experiment worked, that the model improved, or that the consumer's
private code is correct.

For a shell-level gate, validate the whole pack and require the contract kind
your downstream project consumes:

```bash
python scripts/check_circle_ai_contract_pack.py \
  --summary \
  --require-kind sparse_attention_coverage
```

That command exits nonzero if the pack is malformed, if the requested contract
kind is missing, or if its `consumer_check.ready_for_downstream_fixture_use`
field is false.

For a smaller downstream-consumer command, ask only for the readiness entry your
project needs:

```bash
make circle-ai-contracts-ready
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --format json
python scripts/circle_ai_contract_ready.py --list-kinds
python scripts/circle_ai_contract_ready.py --list-recommendations
python scripts/circle_ai_contract_ready.py --fingerprints
python scripts/circle_ai_contract_ready.py --kind sparse_attention_coverage --action-plan --include-values --format json
```

The Makefile target checks the flagship RoPE, KV-cache, sparse-attention, and
recurrence contracts through the consumer path. The direct command validates
the pack first, then exits `0` only when the selected kind is ready under the
readiness index. The JSON form is the preferred input for external tooling.
The `--action-plan` form emits a theorem-linked planner record for the selected
contract kind, including recommendation ids, evidence fields, validation
commands, source links, and optional concrete evidence values. Use it when a
downstream planner needs to attach Circle-backed actions without parsing the
whole contract pack.
The `--fingerprints` form is the smallest reproducibility surface: it emits the
pack fingerprint and one fingerprint per contract kind. These hashes identify
the exported artifact content; they are not proof substitutes.
Downstream CI can pin those values:

```bash
python scripts/circle_ai_contract_ready.py \
  --fingerprints \
  --expect-pack-fingerprint <pack_sha256> \
  --expect-contract-fingerprint sparse_attention_coverage=<contract_sha256>
```

The command exits nonzero if the exported pack or selected contract record has
changed.

The summary line is intentionally proof-aware. A downstream consumer should see:

```text
ready=True proof_resolved=True proof_proved=True unresolved=0 unproved=0
```

If any of those proof fields is false or nonzero, treat the contract as a
non-ready fixture until Circle's manifests and generated pack agree again.

## Importable Consumer Adapter

Python consumers do not need to import Circle's repository validation scripts.
Use the package-level adapter when a downstream test, CI job, or experiment
runner needs a compact readiness gate:

```python
from circle_math.applications.circle_ai_contract_consumer import (
    contract_digest,
    contract_recommendations,
    find_planner_recommendation,
    load_contract_pack,
    planner_action_plan,
    planner_recommendation_index,
    require_ready_contract,
)

pack = load_contract_pack("site/data/generated/circle_ai_contract_pack.json")
contract = require_ready_contract(pack, "kv_cache_ring_buffer")
digest = contract_digest(
    pack,
    "kv_cache_ring_buffer",
    include_field_metadata=True,
)

assert digest["ready_for_downstream_fixture_use"] is True
assert digest["missing_requested_fields"] == []
assert digest["evidence_fields"]["stale_requested_count"] == 0
assert digest["field_catalog"]["stale_requested_count"]["value_kind"] == "integer"
print(contract["id"], digest["theorem_ids"])

recommendation_index = planner_recommendation_index(pack)
assert recommendation_index["ROPE-USE-D19-MARGIN-FRONTIER"]["kind"] == (
    "rope_position_distinguishability"
)
assert find_planner_recommendation(
    pack,
    "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE",
)["kind"] == "strided_candidate_fanout"

rope_actions = contract_recommendations(pack, "rope_position_distinguishability")
assert rope_actions[0]["id"] == "ROPE-AUDIT-EXACT-INTEGER-PHASE-BANK"
sparse_actions = contract_recommendations(pack, "sparse_attention_coverage")
assert sparse_actions[0]["id"] == "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
assert sparse_actions[1]["id"] == "SPARSE-REPAIR-LARGEST-GAP-INTERVAL"
memory_actions = contract_recommendations(pack, "cyclic_memory_residue_winding")
assert memory_actions[0]["id"] == "MEMORY-ATTACH-WINDING-ALIAS-PROVENANCE"
fanout_actions = contract_recommendations(pack, "strided_candidate_fanout")
assert fanout_actions[0]["id"] == "FANOUT-USE-FULL-COVERAGE-STRIDE-CYCLE"
phase_actions = contract_recommendations(pack, "multicoil_phase_feature")
assert phase_actions[0]["id"] == "PHASE-USE-JOINT-REPEAT-HORIZON"
mixer_actions = contract_recommendations(pack, "circulant_block_cyclic_mixer")
assert mixer_actions[0]["id"] == "MIXER-AUDIT-CIRCULANT-DENSE-PARITY"
recurrence_actions = contract_recommendations(pack, "recurrence_schedule")
assert recurrence_actions[0]["id"] == "RECURRENCE-USE-ACTIVE-TOKEN-WORK-SCHEDULE"
seed_rule_actions = contract_recommendations(pack, "seed_rule_exact_regeneration")
assert seed_rule_actions[0]["id"] == "SEED-RULE-USE-EXACT-REGENERATION-RECIPE"
assert seed_rule_actions[1]["best_shorter_candidate_id"] == "finite_circle_public_fixture"

planner = planner_action_plan(
    pack,
    ["sparse_attention_coverage"],
    include_values=True,
)
assert planner["action_plan"][0]["recommendation_id"] == (
    "SPARSE-LOCAL-FIRST-INTERVAL-REPAIR"
)
assert planner["action_plan"][0]["action_parameters"]["proposed_local_window"] == 6
assert planner["action_plan"][1]["action_parameters"]["target_interval_start"] == 40
```

The adapter validates only the consumer-facing JSON invariants: schema id,
readiness-index consistency, minimum-field consistency, proof-status flags,
and the non-claim boundary. It intentionally does not require Lean, manifests,
dictionary YAML, Quarto, or private Theseus-Hive state. Circle's own release
checks still use the stricter repository validators.

Use `contract_digest` when a downstream project needs a copy-safe report row.
By default it includes the minimum evidence fields for the contract kind. Pass
an explicit `fields=(...)` list to attach only the fields needed by a specific
experiment. Pass `include_field_metadata=True` when the consumer also needs
field descriptions, JSON value kinds, and proof roles. Pass
`include_recommendations=True` or call `contract_recommendations` when a
contract exposes copy-safe repair/audit actions. Use `planner_action_plan` when
a downstream planner needs a complete theorem-linked action list with optional
resolved evidence values and recommendation-specific parameters.

The same digest is available from the readiness CLI:

```bash
python scripts/circle_ai_contract_ready.py \
  --kind rope_position_distinguishability \
  --digest \
  --format json \
  --field d19_proved_request_status \
  --field d19_impossible_request_status \
  --include-field-metadata \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind sparse_attention_coverage \
  --digest \
  --field first_uncovered_lag \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind strided_candidate_fanout \
  --digest \
  --field full_coverage \
  --field effective_candidate_budget \
  --field duplicate_count \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind recurrence_schedule \
  --digest \
  --field scheduled_work_saving \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind multicoil_phase_feature \
  --digest \
  --field joint_repeat_horizon \
  --field relative_phase \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind circulant_block_cyclic_mixer \
  --digest \
  --field max_abs_dense_delta \
  --field block_to_dense_ratio \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind cyclic_memory_residue_winding \
  --digest \
  --field max_alias_load \
  --include-recommendations

python scripts/circle_ai_contract_ready.py \
  --kind seed_rule_exact_regeneration \
  --digest \
  --field storage_saving \
  --include-recommendations
```

Use this when an external tool wants proof-status-aware evidence fields without
importing Python modules from the repository.

For a copyable downstream-consumer pattern, use the small example script:

```bash
python scripts/example_consume_circle_ai_contract_pack.py \
  --kind rope_position_distinguishability \
  --field d19_proved_request_status \
  --field d19_impossible_request_status \
  --include-field-metadata

python scripts/example_consume_circle_ai_contract_pack.py \
  --kind sparse_attention_coverage \
  --field first_uncovered_lag \
  --include-recommendations

python scripts/example_consume_circle_ai_contract_pack.py \
  --kind strided_candidate_fanout \
  --field full_coverage \
  --field effective_candidate_budget \
  --field duplicate_count \
  --include-recommendations

python scripts/example_consume_circle_ai_contract_pack.py \
  --kind multicoil_phase_feature \
  --field joint_repeat_horizon \
  --field relative_phase \
  --include-recommendations

python scripts/example_consume_circle_ai_contract_pack.py \
  --kind circulant_block_cyclic_mixer \
  --field max_abs_dense_delta \
  --field block_to_dense_ratio \
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

That script imports only the public consumer adapter, loads the generated JSON
pack, requires the selected contract to be ready, and emits a compact digest row
with theorem ids, selected evidence fields, optional field metadata, optional
planner recommendations, source trails, validation commands, and the claim boundary. It is meant as
a starting point for projects such as Theseus-Hive or other AI/math tools that
want Circle's proof-carrying finite contracts without depending on Circle's
internal validation scripts.

The `--planner` mode emits a compact action plan over the generated
`planner_recommendation_index`. Each action keeps the recommendation id, contract
kind, contract id, readiness flag, action kind, status, coverage scope, evidence
field names, theorem ids, quickstart docs, Living Book pages, validation
commands, source paper, and non-claim boundary. This is the safest first
interface for a downstream planner: it can decide which finite Circle-certified
audit or repair action to try, then run the listed validation commands before
copying the result into a private workload or benchmark lane.
Pass `--planner-include-values` when the downstream planner needs concrete
actionable values. In that mode, each action also carries `evidence_values`
resolved from the contract's theorem-linked `fields` block, a
`missing_evidence_fields` list that should be empty for ready contracts, and
`action_parameters` copied from the recommendation record. For example, the
sparse first-interval action includes proposed local window `6`, next uncovered
lag `8`, and the theorem ids `AIT-T0104`, `AIT-T0166`, and `AIT-T0167`.

## Flagship Field Checklist

For a first integration pass, consume these fields before adding project-specific
metrics:

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

For downstream AI work, attach benchmark or workload results beside these fields
instead of overwriting them. The Circle fields say whether the finite contract is
satisfied; downstream metrics say whether that structure helped a model or tool.
When a contract includes `planner_recommendations`, treat those records as
copy-safe repair or audit actions derived from the listed evidence fields and
theorem ids. For example, the sparse-attention contract exposes a first-gap
interval repair target and a dense-local complete-coverage fallback; neither is
a claim that the repaired architecture will be faster or better.
The RoPE contract exposes an exact integer-period phase-bank audit and a D19
standard-channel-0 margin frontier; neither is a full all-channel real-RoPE
proof, a context-extension claim, a Diophantine theorem for arbitrary channels,
or a model-quality claim.
The cyclic-memory contract exposes a winding/provenance alias record and a
finite slot-load audit record; neither is a retrieval-quality, memory-scaling,
allocation-policy, throughput, or model-quality claim.
The strided-fanout contract exposes a full-coverage stride-cycle record and a
duplicate-collapsed budget record; neither is a search-quality,
retrieval-quality, routing-quality, runtime, or model-quality claim.
The multicoil phase contract exposes joint-repeat phase-tag and relative-phase
shift-invariance records; neither is a learned-embedding, extrapolation,
attention-quality, or model-quality claim.
The circulant/block-cyclic mixer contract exposes dense-reference parity and
parameter-budget records; neither is a speed, memory, hardware-efficiency,
LoRA-replacement, or model-quality claim.
The recurrence contract similarly exposes an active-token work-schedule record
and a whole-period index-reuse record; neither is a claim about runtime,
adaptive halting, reasoning quality, or model quality.
The seed-rule contract exposes an exact-regeneration recipe and a bounded
finite-search candidate table with stable candidate ids; neither is a claim
about global minimality, Kolmogorov complexity, compression, semantic
equivalence, or model quality.

## Integration Rules

1. Keep Circle contract ids in downstream reports so results can be traced back
   to manifests and Lean declarations.
2. Preserve the `not_claimed` text or a stricter downstream boundary in every
   report.
3. Compare against ordinary baselines listed in `ordinary_baselines` before
   claiming usefulness.
4. Treat `fields` as deterministic certificate data, not proof terms.
5. Treat theorem ids as formal claims only when the generated theorem index and
   Lean build agree that the id is proved.
6. Keep project-specific reports downstream unless they are aggregate-only and
   intentionally public.

## Current Contract Families

| Kind | Intended use | Typical downstream question |
| --- | --- | --- |
| `rope_position_distinguishability` | RoPE position-contract auditing | Do declared rotary phase channels distinguish all positions in a finite context, and where are the discrete/real-phase boundaries? |
| `kv_cache_ring_buffer` | KV-cache request auditing | Are requested tokens retained, duplicate-free where needed, and compatible with pinned sink plus rolling-window policy? |
| `sparse_attention_coverage` | Sparse-attention layout auditing | Which lags are covered or missed, and where do budget/collision fields explain the plan? |
| `recurrence_schedule` | Looped/recursive schedule auditing | Do phase cycles, active-token budgets, exit steps, and whole-period index-reuse fields satisfy a finite schedule contract? |
| `strided_candidate_fanout` | Sparse fanout auditing | Which candidates are reached, duplicated, or missed by a finite stride plan? |
| `cyclic_memory_residue_winding` | Cyclic memory auditing | Which memory slots alias, and what winding/provenance separates repeated residues? |
| `multicoil_phase_feature` | Phase-feature auditing | Which periodic tags repeat, and at what joint horizon? |
| `circulant_block_cyclic_mixer` | Structured mixer/accounting checks | Do fixture outputs match the dense reference, and what parameter counts are exposed? |
| `seed_rule_exact_regeneration` | Generative provenance checks | Can an object be regenerated exactly from a seed/rule record, and what finite declared-search/accounting fields are exposed? |

## Validation

During local iteration:

```bash
make targeted-check TARGETED_FILES="circle_math/applications/circle_ai_contracts.py scripts/recurrence_schedule_certify.py scripts/strided_candidate_fanout_certify.py scripts/cyclic_memory_certify.py scripts/multicoil_phase_feature_certify.py scripts/circulant_block_cyclic_mixer_certify.py scripts/seed_rule_certify.py scripts/export_circle_ai_contracts.py"
```

Before a release-quality checkpoint:

```bash
make circle-ai-contracts
make circle-ai-contracts-check
make circle-ai-contracts-ready
python -m pytest tests/test_circle_ai_contract_consumer.py -q
make site-data
make check
make site-render
make site-render-check
```

`make circle-ai-contracts-check` validates the generated JSON artifact directly:
schema id, the adjacent JSON Schema sidecar when present, required keys, minimum
fields, consumer gate, theorem ids, dictionary ids, source paths, docs, Living
Book pages, and Python entrypoint paths. These commands validate the Circle
repository. A downstream consumer still needs its own workload-specific tests.

## Claim Boundary

The contract pack does not prove model quality, reasoning ability, context
length, speed, memory scaling, deployment safety, transfer, or ASI. Its value is
that external projects can attach experiments to proof-linked finite structure:
indexing, phase, period, recurrence, sparse coverage, and regeneration.
