# Sparse-Attention Certifier Quickstart

This is the command-line surface for the finite local-window plus stride-family
sparse-attention contract.

It answers one precise question:

```text
For a declared context length, local window, stride family, and path length,
which positive dependency lags are covered, which are gaps, when is the
deduplicated theorem-side candidate count an exact coverage test, and when do
checkable no-wrap or no-zero-residue stride conditions discharge that range
hypothesis?
```

It does not claim attention quality, model quality, long-context capability,
runtime, memory savings, throughput, or replacement of full attention.

## Example

```bash
python scripts/stride_family_certify.py \
  --context 120 \
  --strides 7,13 \
  --path-length 3 \
  --local-window 4
```

Expected shape:

```text
stride_family_contract=GAPS context=120 strides=(7, 13) path_length=3 local_window=4
covered_lags=10 uncovered_lags=109 uncovered_intervals=6 coverage_ratio=0.084034
lag_partition=covered_plus_uncovered=119 positive_lags=119 partition_complete=True theorem=AIT-T0094
covered_count_complete=False theorem=AIT-T0095
first_uncovered_lag_bridge=list_head=True none_iff_complete=True semantic_miss=True theorems=AIT-T0098,AIT-T0099,AIT-T0100,AIT-T0101
uncovered_count_witness=True positive=True first_gap=5 theorems=AIT-T0096,AIT-T0103
first_uncovered_interval=start=5 stop=6 length=2 repair_window=6 additional_local_slots=2 target_interval_reached=True theorems=AIT-T0104,AIT-T0171
first_interval_repair_next_gap=8 still_has_gap=True covers_context=False fixture_theorems=AIT-T0166,AIT-T0167
largest_uncovered_interval=start=40 stop=119 length=80 repair_window=119 additional_local_slots=115 target_interval_reached=True next_gap_after_repair=None covers_context=True is_tail=True source=largest_certificate_gap_interval
covered_count_shortfall=True gap_witness_equiv=True theorem=AIT-T0097
uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119))
candidate_budget_per_query=10 raw_upper_bound=10 deduplicated_bound=10 full_attention_budget=120
raw_budget_shortfall=True certifies_incomplete=True theorem=AIT-T0110
unique_lag_shortfall=True certifies_incomplete=True gap_witness_equiv_under_candidate_range=True period_threshold_equiv=True theorems=AIT-T0111,AIT-T0120,AIT-T0121,AIT-T0122,AIT-T0129
candidate_range=True no_wrap_separated_sufficient=False no_zero_residue_sufficient=True unique_count_complete_iff=True theorems=AIT-T0112,AIT-T0115,AIT-T0116,AIT-T0117,AIT-T0118,AIT-T0119
singleton_no_zero_period_threshold=None period=None matches_no_zero_residue_condition=True theorems=AIT-T0126,AIT-T0127
family_no_zero_period_thresholds=(True, True) periods=(120, 120) zero_residue_counts=(0, 0) counts_match_period_formula=True zero_residue_total_count=0 total_count_matches_sum_formula=True total_count_zero_matches_no_zero_condition=True period_threshold_sufficient=True matches_no_zero_residue_condition=True violation_witness=(None, None, None, None) witness_matches_period_threshold=True witness_matches_no_zero_failure=True period_violation_matches_no_zero_failure=True witness_is_first_zero=True witness_step_positive=True theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133,AIT-T0134,AIT-T0135,AIT-T0136,AIT-T0137,AIT-T0138
candidate_range_counts=covered_eq_unique=True uncovered_eq_context_minus_unique=True theorems=AIT-T0113,AIT-T0114
lag_budget_status=exact-raw-budget unique_lag_candidates=10 lag_dedup_loss=0 lag_no_collision=True
query_budget_status=exact-raw-budget unique_query_candidates=10 query_dedup_loss=0 query_no_collision=True
dedup_loss_collision=lag_positive=False lag_matches_collision=True query_positive=False query_matches_collision=True theorems=AIT-T0147,AIT-T0148
dedup_loss_accounting=lag_unique_plus_loss_eq_raw=True query_unique_plus_loss_eq_raw=True theorems=AIT-T0149,AIT-T0150
collision_pair_counts=lag=0 query=0 lag_zero_matches_no_collision=True lag_positive_matches_collision=True query_zero_matches_no_collision=True query_positive_matches_collision=True theorems=AIT-T0155,AIT-T0156,AIT-T0157,AIT-T0158 fixture_theorems=see_fixture_theorem_ids
collision_pair_severity=lag_bounds_dedup_loss=True lag_excess_over_dedup_loss=0 query_bounds_dedup_loss=True query_excess_over_dedup_loss=0 theorems=AIT-T0159,AIT-T0160
first_gap_local_repair=shortfall=1 needed_window=5 current_window_below_first_gap=True repair_window_reaches_first_gap=True repair_window_covers_context=False repair_window_is_final_positive_lag=False repair_threshold_matches_final_lag=True theorems=AIT-T0161,AIT-T0162,AIT-T0164,AIT-T0165 fixture_theorems=AIT-T0163
local_window_complete_threshold=threshold=119 shortfall=115 reaches_threshold=False threshold_certifies_complete=False exact_local_minimum=True first_gap_repair_reaches_threshold=False theorems=AIT-T0023,AIT-T0034
complete_local_repair=window=119 additional_slots=115 covers_context=True uses_dense_threshold=True exact_local_minimum=True minimal_for_declared_family=True minimal_witness_lag=119 theorems=AIT-T0023,AIT-T0034 fixture_theorems=AIT-T0168,AIT-T0169,AIT-T0170
interval_repair_plan=steps=6 final_window=119 covers_context=True strictly_progresses=True first_step=(5, 6, 6, 2, 107) last_step=(40, 119, 119, 81, 0) source=successive_first_uncovered_intervals
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

Python API users can call `build_sparse_attention_receipt(...)` from
`circle_math.ai_contracts`; see the shared examples in
`docs/CIRCLE_AI_CONTRACT_RUNNER.md#python-api`. A sparse receipt can be
theorem-backed and still fail the requested coverage property. Treat that as a
gap certificate, not as a passing architecture gate.

## Reading The Certificate

- `schema_id`: the report format identifier, currently `circle_calculus.stride_family_sparse_attention_certificate.v0`.
- `coverage_complete`: true only when every positive lag below the context is covered.
- `covered_lags`: positive lags reached by the local window or one admitted stride step.
- `uncovered_lags`: finite gap certificates for this declared sparse plan.
- `positive_lag_count`: the number of positive in-context lags, namely `context - 1`.
- `covered_uncovered_count_sum`: the covered count plus uncovered count.
- `covered_uncovered_count_partition`: true when the covered and uncovered lists partition the positive lags.
- `covered_count_certifies_complete`: true exactly when the covered-lag count reaches `context - 1`.
- `covered_count_shortfall`: true when the covered-lag count is below `context - 1`.
- `covered_count_shortfall_matches_gap_witness`: true when that count shortfall agrees with the existence of a gap witness.
- `first_uncovered_lag`: a concrete uncovered lag when the uncovered count is positive.
- `first_uncovered_lag_interval_start`: the start of the first consecutive uncovered-lag interval, or `null` when no gaps remain.
- `first_uncovered_lag_interval_stop`: the inclusive end of the first consecutive uncovered-lag interval, or `null` when no gaps remain.
- `first_uncovered_lag_interval_length`: the number of missed positive lags in that first interval, or `null` when no gaps remain.
- `first_uncovered_lag_interval_repair_window`: the local-window width that reaches the end of the first uncovered interval, or `null` when no gaps remain.
- `first_uncovered_lag_interval_additional_local_slots`: additional local slots needed to cover that first interval locally. This is an interval repair target, not a full-coverage claim.
- `first_uncovered_interval_repair_reaches_interval`: true when the first-interval repair window reaches every lag in the reported first uncovered interval. This is theorem-backed by `AIT-T0171`.
- `first_interval_repair_next_uncovered_lag`: the first remaining uncovered lag after applying the first-interval local repair. In the default row this is `8`.
- `first_interval_repair_still_has_gap`: true when the first-interval repair still leaves at least one uncovered positive lag.
- `first_interval_repair_covers_context`: true only when the first-interval repair already certifies complete positive-lag coverage. In the default row this is false, theorem-backed by `AIT-T0166` and `AIT-T0167`.
- `largest_uncovered_interval_start`, `largest_uncovered_interval_stop`, `largest_uncovered_interval_length`: the largest consecutive uncovered-lag run in the certificate. In the default row this is the tail interval `40..119`.
- `largest_uncovered_interval_repair_window`: the local-window width that reaches the end of that largest uncovered interval.
- `largest_uncovered_interval_additional_local_slots`: additional local slots required to reach the largest uncovered interval end from the current local window.
- `largest_uncovered_interval_repair_reaches_interval`: true when the reported repair window reaches every lag in the largest uncovered interval.
- `largest_interval_repair_next_uncovered_lag`: the first remaining uncovered lag after applying the largest-interval local repair, or `null` when none remain.
- `largest_interval_repair_still_has_gap`: true when that largest-interval repair still leaves a gap.
- `largest_interval_repair_covers_context`: true when that largest-interval repair covers every positive in-context lag.
- `largest_uncovered_interval_is_tail`: true when the largest uncovered interval reaches the final positive lag. This is a planner diagnostic; it does not say the sparse layout is optimal.
- `first_uncovered_lag_local_window_shortfall`: how far the current local window is below the first uncovered lag, or `null` when there is no first gap.
- `first_uncovered_lag_repair_window`: the local-window width that reaches the first uncovered lag locally, or `null` when there is no first gap.
- `first_uncovered_lag_exceeds_local_window`: true when a reported first gap is theorem-backed as strictly beyond the current local window.
- `first_uncovered_lag_repair_window_reaches`: true when raising the local window to the reported first gap reaches that lag. This does not prove the whole sparse plan becomes complete.
- `first_gap_repair_window_is_final_positive_lag`: true when the first-gap repair window is the final positive in-context lag, equivalently the dense-local complete threshold.
- `first_gap_repair_threshold_matches_final_lag`: true when the report's threshold check agrees with the final-positive-lag condition.
- `local_window_complete_coverage_threshold`: the dense-local threshold `context - 1` that guarantees every positive lag is locally reachable.
- `local_window_complete_coverage_shortfall`: how far the current local window is below that dense-local complete-coverage threshold.
- `local_window_reaches_complete_coverage_threshold`: true when the current local window reaches the dense-local threshold.
- `local_window_threshold_certifies_complete`: true when the dense-local threshold is actually reached and therefore certifies complete coverage.
- `local_window_complete_threshold_is_exact_local_minimum`: true when the threshold is the exact local-only minimum by `AIT-T0023`, not just a dense fallback convention.
- `first_gap_repair_window_reaches_complete_threshold`: whether the first-gap repair window also reaches the dense-local complete-coverage threshold. For the default row this is `false`, which is why first-gap repair is not presented as full sparse coverage.
- `complete_repair_window`: the dense-local fallback width `context - 1` that certifies complete positive-lag coverage.
- `complete_repair_window_additional_local_slots`: the additional local-window slots needed to reach that full fallback from the current plan.
- `complete_repair_window_covers_context`: true when the complete repair window is theorem-backed as covering every positive lag.
- `complete_repair_window_uses_dense_threshold`: true when the complete repair window is exactly the dense-local threshold. This is a correctness/boundary field, not a recommendation that dense local attention is a good architecture.
- `complete_repair_window_minimal_for_declared_stride_family`: true when the reported complete repair window is also minimal for the declared finite stride-family fixture, not only sufficient by dense-local coverage. `AIT-T0172` gives the reusable condition: if the declared stride family cannot reach the final positive lag, complete coverage is equivalent to reaching the dense-local threshold.
- `complete_repair_window_minimal_witness_lag`: a concrete lag witnessing failure at the previous local-window width. In the default row this is lag `119`.
- `interval_repair_plan`: deterministic repair rows of the form `[target_interval_start, target_interval_stop, proposed_local_window, additional_local_slots, remaining_gap_count_after_repair]`. The default row closes the six successive gap intervals and ends at window `119`.
- `interval_repair_plan_step_count`: number of successive first-interval repair rows.
- `interval_repair_plan_final_window`: final local-window width after the interval repair path.
- `interval_repair_plan_covers_context`: true when the final interval-repair window covers every positive lag.
- `interval_repair_plan_strictly_progresses`: true when every interval-repair row increases the local window. This is a remediation trace over reported gaps, not a proof of architectural optimality.
- `planner_recommendations`: optional contract-pack records that summarize repair actions over the same fields. The default sparse contract exposes `SPARSE-LOCAL-FIRST-INTERVAL-REPAIR` for the first gap run, `SPARSE-REPAIR-LARGEST-GAP-INTERVAL` for the largest reported gap run, `SPARSE-DENSE-LOCAL-COMPLETE-FALLBACK` for the dense-local full fallback, and `SPARSE-INTERVAL-REPAIR-PATH` for the successive first-gap-interval repair path. These are copy-safe audit actions, not performance recommendations.
- `uncovered_count_positive_matches_gap_witness`: true when the positive uncovered-count flag and the existence of a first gap agree.
- `uncovered_lag_intervals`: consecutive runs of those uncovered lags, for reading large gap lists compactly.
- `raw_candidate_budget_upper_bound`: `local_window + path_length * number_of_strides`.
- `raw_budget_shortfall_certifies_incomplete`: true when the certificate avoids the impossible state where raw budget is below `context - 1` but coverage is still reported complete.
- `theorem_side_unique_lag_candidate_count`: deduplicated lag count from the theorem-side list.
- `theorem_side_lag_candidate_dedup_loss`: raw lag-candidate budget minus deduplicated lag-candidate count.
- `theorem_side_lag_candidate_collision_pair_count`: unordered equal-lag pair count in the raw theorem-side lag-candidate list.
- `lag_collision_pair_count_zero_matches_no_collision`: true when zero lag pair-collision count agrees with the no-duplicate lag-candidate predicate.
- `lag_collision_pair_count_positive_matches_collision`: true when positive lag pair-collision count agrees with the existence of a duplicate lag-candidate collision.
- `lag_collision_pair_count_bounds_dedup_loss`: true when the lag pair-collision count is at least the lag deduplication loss.
- `lag_collision_pair_count_excess_over_dedup_loss`: lag pair-collision count minus lag deduplication loss; positive values indicate repeated multiplicity beyond one lost entry per duplicate value.
- `lag_dedup_loss_zero_matches_no_collision`: true when zero lag dedup loss agrees with the no-duplicate lag-candidate predicate.
- `theorem_side_lag_candidate_dedup_loss_positive`: true when at least one raw lag candidate disappeared under deduplication.
- `lag_dedup_loss_positive_matches_collision`: true when positive lag dedup loss agrees with the existence of a duplicate lag-candidate collision.
- `lag_dedup_loss_accounting_matches_raw`: true when unique lag candidates plus lag dedup loss equals the raw local-plus-stride-family candidate budget.
- `theorem_side_lag_candidates_positive_in_context`: true when every theorem-side lag candidate is between `1` and `context - 1`.
- `no_wrap_separated_candidate_range_sufficient_condition`: true when `local_window < context` and the ordered stride family satisfies the no-wrap separated numeric condition, which is a Lean-proved sufficient condition for positive in-context lag candidates.
- `no_zero_residue_candidate_range_sufficient_condition`: true when `local_window < context` and every admitted `step * stride mod context` is nonzero. This is a Lean-proved sufficient condition for positive in-context lag candidates that permits wrapping and overlap.
- `singleton_stride_period`: for one-stride plans, the finite coil period `context / gcd(context, stride)`; otherwise absent.
- `singleton_no_zero_period_threshold`: for one-stride plans, true exactly when `path_length < singleton_stride_period`.
- `singleton_no_zero_period_threshold_matches_condition`: true when the singleton period-threshold calculation agrees with the finite no-zero residue scan.
- `stride_family_periods`: the finite coil period of each admitted stride, in declared order.
- `no_zero_period_thresholds`: per-stride booleans checking `path_length < period`.
- `stride_family_zero_residue_step_counts`: per-stride counts of admitted positive steps whose generated residue is zero.
- `zero_residue_step_counts_match_period_formula`: true when those counts match `path_length // stride_period`.
- `stride_family_zero_residue_total_step_count`: total zero-residue stride-step pairs across the finite stride family.
- `zero_residue_total_count_matches_sum_formula`: true when the total count matches the sum of the per-stride period quotient formulas.
- `zero_residue_total_count_zero_matches_no_zero_condition`: true when total count zero is equivalent to the no-zero structural condition in the nonzero context.
- `no_zero_period_threshold_candidate_range_sufficient_condition`: true when `local_window < context` and every admitted stride passes the period-threshold no-zero check.
- `no_zero_period_threshold_matches_condition`: true when the period-threshold test agrees with the finite no-zero residue scan.
- `no_zero_period_violation_witness_stride`, `no_zero_period_violation_witness_period`, `no_zero_period_violation_witness_step`, `no_zero_period_violation_witness_residue`: the first constructed zero-residue witness when a period threshold fails; otherwise absent.
- `zero_residue_witness_matches_period_threshold`: true when the witness fields agree with the Lean-backed period-at-most-path-budget condition.
- `zero_residue_witness_matches_no_zero_failure`: true when existence of a generated zero-residue witness agrees with failure of the no-zero structural check.
- `period_threshold_violation_matches_no_zero_failure`: true when a period-at-most-path-budget violation agrees with failure of the no-zero structural check.
- `no_zero_period_violation_witness_step_positive`: true when no witness is present or the reported witness step is positive.
- `no_zero_period_violation_witness_is_first_zero`: true when no witness is present or the reported witness uses the first positive zero-residue step for that stride.
- `unique_lag_count_shortfall_certifies_incomplete`: true when the certificate avoids the impossible state where the deduplicated unique lag-candidate count is below `context - 1` but coverage is still reported complete.
- `unique_lag_count_shortfall_matches_gap_witness_under_period_threshold`: true when the period-threshold hypothesis is absent or, under `local_window < context` plus all `path_length < stride_period` checks, unique lag-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_lag_count_matches_complete_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, complete coverage matches `theorem_side_unique_lag_candidate_count == context - 1`.
- `covered_count_matches_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, covered count equals the unique lag-candidate count.
- `uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, uncovered count equals `context - 1 - theorem_side_unique_lag_candidate_count`.
- `theorem_side_unique_query_candidate_count`: deduplicated query-indexed predecessor count.
- `theorem_side_query_candidate_dedup_loss`: raw query-candidate budget minus deduplicated query-candidate count.
- `theorem_side_query_candidate_collision_pair_count`: unordered equal-address pair count in the raw query-indexed predecessor-candidate list.
- `query_collision_pair_count_zero_matches_no_collision`: true when zero query pair-collision count agrees with the no-duplicate query-candidate predicate.
- `query_collision_pair_count_positive_matches_collision`: true when positive query pair-collision count agrees with the existence of a duplicate query-candidate collision.
- `query_collision_pair_count_bounds_dedup_loss`: true when the query pair-collision count is at least the query deduplication loss.
- `query_collision_pair_count_excess_over_dedup_loss`: query pair-collision count minus query deduplication loss.
- `query_dedup_loss_zero_matches_no_collision`: true when zero query dedup loss agrees with the no-duplicate query-candidate predicate.
- `theorem_side_query_candidate_dedup_loss_positive`: true when at least one raw query predecessor candidate disappeared under deduplication.
- `query_dedup_loss_positive_matches_collision`: true when positive query dedup loss agrees with the existence of a duplicate query-candidate collision.
- `query_dedup_loss_accounting_matches_raw`: true when unique query candidates plus query dedup loss equals the raw local-plus-stride-family candidate budget.
- `unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective`: true when the candidate-range and predecessor-injectivity hypotheses are absent or, under those hypotheses, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated`: true when the no-wrap structural condition is absent or, under that checkable condition, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue`: true when the no-zero structural condition is absent or, under that checkable condition, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_period_threshold`: true when the period-threshold hypothesis is absent or, under `local_window < context` plus all `path_length < stride_period` checks, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `theorem_side_lag_candidates_no_collision`: no duplicate lag candidates.
- `theorem_side_query_candidates_no_collision`: no duplicate query-indexed candidates.

The local-window threshold endpoints are:

- `AIT-T0023`: the local window covers every positive in-context lag if and only if it reaches the largest possible lag, `context - 1`.
- `AIT-T0034`: when the local window reaches `context - 1`, any local-window plus stride-family plan satisfies complete coverage.

The raw-budget iff endpoints are:

- `AIT-T0076`: lag-candidate raw-budget equality holds if and only if the lag-candidate list has no duplicates.
- `AIT-T0077`: query-candidate raw-budget equality holds if and only if the query-indexed candidate list has no duplicates.
- `AIT-T0110`: complete coverage requires raw sparse generator budget at least `n - 1`, so a raw-budget shortfall certifies incompleteness.
- `AIT-T0111`: complete coverage requires deduplicated unique lag-candidate count at least `n - 1`, so duplicate collapse can certify incompleteness even when raw budget alone is not decisive.
- `AIT-T0112`: when every generated lag candidate is positive and in context, complete coverage is equivalent to unique lag-candidate count equaling `n - 1`.
- `AIT-T0113`: under the same candidate-range hypothesis, covered-lag count equals unique lag-candidate count.
- `AIT-T0114`: under the same candidate-range hypothesis, uncovered-lag count equals `n - 1 - unique_lag_candidate_count`.
- `AIT-T0115`: `window < context` plus the ordered no-wrap separated stride-family condition implies every theorem-side lag candidate is positive and in context.
- `AIT-T0116`: under that same checkable structural condition, complete coverage is equivalent to unique lag-candidate count equaling `n - 1`.
- `AIT-T0117`: if every admitted stride-step residue avoids zero, every generated stride-family residue candidate is positive.
- `AIT-T0118`: `window < context` plus the no-zero stride-residue condition implies every theorem-side lag candidate is positive and in context.
- `AIT-T0119`: under that no-zero residue condition, complete coverage is equivalent to unique lag-candidate count equaling `n - 1`.
- `AIT-T0120`: under the candidate-range hypothesis, unique lag-candidate shortfall is equivalent to an uncovered positive lag.
- `AIT-T0121`: the no-wrap separated structural version of that lag-side shortfall/gap equivalence.
- `AIT-T0122`: the no-zero-residue structural version of that lag-side shortfall/gap equivalence.
- `AIT-T0123`: under candidate range and predecessor injectivity, unique query-candidate shortfall is equivalent to an uncovered positive lag.
- `AIT-T0124`: the no-wrap separated structural version of that query-side shortfall/gap equivalence.
- `AIT-T0125`: the no-zero-residue structural version of that query-side shortfall/gap equivalence.
- `AIT-T0126`: for one stride, a generated residue is zero exactly when the stride period divides the step count.
- `AIT-T0127`: for a singleton stride family in a nonzero context, the no-zero-residue condition is exactly the threshold `path_length < period`.
- `AIT-T0128`: for any finite stride family in a nonzero context, the no-zero-residue condition is exactly the requirement that every admitted stride has period greater than `path_length`.
- `AIT-T0129`: under the period-threshold check and `window < context`, unique lag-candidate shortfall is equivalent to an uncovered positive lag.
- `AIT-T0130`: under the same period-threshold check and `window < context`, unique query-candidate shortfall is equivalent to an uncovered positive lag.
- `AIT-T0131`: a zero-residue witness exists exactly when some admitted stride period is at most `path_length`; the report constructs the witness with `step = period`.
- `AIT-T0132`: failure of the no-zero structural check is equivalent to existence of a generated zero-residue witness.
- `AIT-T0133`: in a nonzero context, failure of the no-zero structural check is equivalent to some admitted stride period being at most `path_length`.
- `AIT-T0134`: in a nonzero context, every stride has a positive finite coil period.
- `AIT-T0135`: in a nonzero context, the finite coil period is the first positive step that generates a zero residue for that stride.
- `AIT-T0136`: for one stride, the number of admitted positive zero-residue steps is exactly `path_length / period`.
- `AIT-T0137`: for a finite stride family, the total zero-residue count is the sum of the per-stride `path_length / period` counts.
- `AIT-T0138`: in a nonzero context, total zero-residue count is zero exactly when the no-zero structural condition holds.
- `AIT-T0139`: the public 4096-token no-wrap planner row has exactly 44 covered positive lags.
- `AIT-T0140`: the same 4096-token planner row has exactly 4051 uncovered positive lags.
- `AIT-T0141`: the public 8192-token coprime planner row has exactly 96 covered positive lags.
- `AIT-T0142`: the same 8192-token planner row has exactly 8095 uncovered positive lags.
- `AIT-T0143`: every query index in the public 4096-token no-wrap planner row has exactly 44 deduplicated predecessor candidates.
- `AIT-T0144`: every query index in the public 8192-token coprime planner row has exactly 96 deduplicated predecessor candidates.
- `AIT-T0145`: lag-side deduplication loss is zero if and only if the lag-candidate list has no duplicates.
- `AIT-T0146`: query-side deduplication loss is zero if and only if the query-candidate list has no duplicates.
- `AIT-T0147`: lag-side deduplication loss is positive if and only if the lag-candidate list has a duplicate collision.
- `AIT-T0148`: query-side deduplication loss is positive if and only if the query-candidate list has a duplicate predecessor collision.
- `AIT-T0149`: lag-side unique candidate count plus deduplication loss equals the raw candidate budget.
- `AIT-T0150`: query-side unique candidate count plus deduplication loss equals the raw candidate budget.
- `AIT-T0155`: lag-side pair-collision count is zero if and only if the lag-candidate list has no duplicates.
- `AIT-T0156`: query-side pair-collision count is zero if and only if the query-candidate list has no duplicates.
- `AIT-T0157`: lag-side pair-collision count is positive if and only if the lag-candidate list has a duplicate collision.
- `AIT-T0158`: query-side pair-collision count is positive if and only if the query-candidate list has a duplicate predecessor collision.
- `AIT-T0159`: lag-side pair-collision count is at least lag-side deduplication loss.
- `AIT-T0160`: query-side pair-collision count is at least query-side deduplication loss.
- `AIT-T0161`: any reported first uncovered lag is strictly beyond the current local window.
- `AIT-T0162`: raising the local window to the reported first uncovered lag makes that specific lag reachable locally; it is a first-gap repair fact, not a full-coverage theorem.
- `AIT-T0163`: for the default `C_120` row, the first-gap repair window still leaves a concrete gap, so it is not a complete-coverage repair.
- `AIT-T0164`: the first-gap repair window reaches the dense-local complete threshold exactly when the first reported gap is the final positive in-context lag.
- `AIT-T0165`: if the reported first gap is that final positive lag, then the repaired local window certifies complete context coverage.
- `AIT-T0171`: raising the local window to the end of a reported uncovered interval reaches every lag in that target interval locally; this is an interval repair fact, not a full-coverage theorem.
- `AIT-T0166`: for the default `C_120` row, repairing the first uncovered interval by raising the local window to `6` still leaves lag `8` uncovered.
- `AIT-T0167`: for the default `C_120` row, repairing only the first uncovered interval does not certify complete context coverage.
- `AIT-T0168`: for the default `C_120` row, lag `119` remains a concrete gap for every local window below `119`.
- `AIT-T0169`: therefore no local window below `119` certifies complete context coverage for the default row.
- `AIT-T0170`: for the default row, complete context coverage is equivalent to the local window being at least `119`.
- `AIT-T0172`: in any context with at least two positions, if the declared stride family cannot reach the final positive lag, complete coverage is equivalent to the local window being at least `context - 1`.

The finite-list endpoints are:

- `AIT-T0081`: membership in the uncovered-lag list is exactly a positive in-context semantic miss.
- `AIT-T0082`: complete coverage is equivalent to an empty uncovered-lag list.
- `AIT-T0083`: complete coverage is equivalent to uncovered-lag count zero.
- `AIT-T0090`: membership in the covered-lag list is exactly a positive in-context semantic hit.
- `AIT-T0091`: the default fixture's covered-lag list has exactly `10` entries.
- `AIT-T0092`: the finite covered-lag and uncovered-lag lists are disjoint.
- `AIT-T0093`: every positive in-context lag appears in one of the two lists.
- `AIT-T0094`: the covered-lag count plus uncovered-lag count equals `n - 1`.
- `AIT-T0095`: complete coverage is equivalent to the covered-lag count equaling `n - 1`.
- `AIT-T0096`: a positive uncovered-lag count is equivalent to the existence of a concrete uncovered positive lag.
- `AIT-T0097`: covered-lag count below `n - 1` is equivalent to the existence of a concrete uncovered positive lag.
- `AIT-T0098`: no first uncovered lag is equivalent to an empty uncovered-lag list.
- `AIT-T0099`: complete coverage is equivalent to no first uncovered lag.
- `AIT-T0100`: a reported first uncovered lag is exactly the head of the uncovered-lag list.
- `AIT-T0101`: a reported first uncovered lag is a genuine positive in-context miss.
- `AIT-T0102`: the default `C_120`, local window `4`, path length `3`, strides `[7,13]` fixture has first uncovered lag `5`.
- `AIT-T0104`: the default fixture's uncovered-lag interval summary is exactly `5..6`, `8..12`, `15..20`, `22..25`, `27..38`, `40..119`.
- `AIT-T0105`: the compact complete fixture's uncovered-lag interval summary is empty.
- `AIT-T0151` and `AIT-T0152`: the default `C_120` fixture has zero lag-side and query-side candidate pair collisions.
- `AIT-T0153` and `AIT-T0154`: the public `C_16`, local-window `2`, path-length `4`, strides `[4,8]` alias probe has six lag-side and six query-side candidate pair collisions.

The gap/coverage spine is `AIT-T0020` through `AIT-T0035`. The theorem-side candidate-list,
budget, no-collision, and predecessor-indexing spine is `AIT-T0036` through `AIT-T0077`.
The finite uncovered/covered list, count-partition, first-gap, public interval-summary, query-count, raw-budget necessary-condition, unique-lag necessary-condition, candidate-range unique-count iff, candidate-range gap-count, no-wrap separated candidate-range discharge, and no-zero residue candidate-range discharge spine is `AIT-T0078` through `AIT-T0119`.

## Boundary

This certifier checks a finite index contract. It does not run a neural network, fit a
learned sparse-attention head, measure loss, measure speed, or prove usefulness on a real
task. Use it as a proof-carrying design check before experiments, not as experimental
evidence.
