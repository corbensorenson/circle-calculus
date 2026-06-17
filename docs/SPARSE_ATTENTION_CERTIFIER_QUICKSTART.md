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
covered_count_shortfall=True gap_witness_equiv=True theorem=AIT-T0097
uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119))
candidate_budget_per_query=10 raw_upper_bound=10 deduplicated_bound=10 full_attention_budget=120
raw_budget_shortfall=True certifies_incomplete=True theorem=AIT-T0110
unique_lag_shortfall=True certifies_incomplete=True gap_witness_equiv_under_candidate_range=True period_threshold_equiv=True theorems=AIT-T0111,AIT-T0120,AIT-T0121,AIT-T0122,AIT-T0129
candidate_range=True no_wrap_separated_sufficient=False no_zero_residue_sufficient=True unique_count_complete_iff=True theorems=AIT-T0112,AIT-T0115,AIT-T0116,AIT-T0117,AIT-T0118,AIT-T0119
singleton_no_zero_period_threshold=None period=None matches_no_zero_residue_condition=True theorems=AIT-T0126,AIT-T0127
family_no_zero_period_thresholds=(True, True) periods=(120, 120) period_threshold_sufficient=True matches_no_zero_residue_condition=True violation_witness=(None, None, None, None) witness_matches_period_threshold=True witness_matches_no_zero_failure=True period_violation_matches_no_zero_failure=True theorems=AIT-T0128,AIT-T0131,AIT-T0132,AIT-T0133
candidate_range_counts=covered_eq_unique=True uncovered_eq_context_minus_unique=True theorems=AIT-T0113,AIT-T0114
lag_budget_status=exact-raw-budget unique_lag_candidates=10 lag_no_collision=True
query_budget_status=exact-raw-budget unique_query_candidates=10 query_no_collision=True
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

## Reading The Certificate

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
- `uncovered_count_positive_matches_gap_witness`: true when the positive uncovered-count flag and the existence of a first gap agree.
- `uncovered_lag_intervals`: consecutive runs of those uncovered lags, for reading large gap lists compactly.
- `raw_candidate_budget_upper_bound`: `local_window + path_length * number_of_strides`.
- `raw_budget_shortfall_certifies_incomplete`: true when the certificate avoids the impossible state where raw budget is below `context - 1` but coverage is still reported complete.
- `theorem_side_unique_lag_candidate_count`: deduplicated lag count from the theorem-side list.
- `theorem_side_lag_candidates_positive_in_context`: true when every theorem-side lag candidate is between `1` and `context - 1`.
- `no_wrap_separated_candidate_range_sufficient_condition`: true when `local_window < context` and the ordered stride family satisfies the no-wrap separated numeric condition, which is a Lean-proved sufficient condition for positive in-context lag candidates.
- `no_zero_residue_candidate_range_sufficient_condition`: true when `local_window < context` and every admitted `step * stride mod context` is nonzero. This is a Lean-proved sufficient condition for positive in-context lag candidates that permits wrapping and overlap.
- `singleton_stride_period`: for one-stride plans, the finite coil period `context / gcd(context, stride)`; otherwise absent.
- `singleton_no_zero_period_threshold`: for one-stride plans, true exactly when `path_length < singleton_stride_period`.
- `singleton_no_zero_period_threshold_matches_condition`: true when the singleton period-threshold calculation agrees with the finite no-zero residue scan.
- `stride_family_periods`: the finite coil period of each admitted stride, in declared order.
- `no_zero_period_thresholds`: per-stride booleans checking `path_length < period`.
- `no_zero_period_threshold_candidate_range_sufficient_condition`: true when `local_window < context` and every admitted stride passes the period-threshold no-zero check.
- `no_zero_period_threshold_matches_condition`: true when the period-threshold test agrees with the finite no-zero residue scan.
- `no_zero_period_violation_witness_stride`, `no_zero_period_violation_witness_period`, `no_zero_period_violation_witness_step`, `no_zero_period_violation_witness_residue`: the first constructed zero-residue witness when a period threshold fails; otherwise absent.
- `zero_residue_witness_matches_period_threshold`: true when the witness fields agree with the Lean-backed period-at-most-path-budget condition.
- `zero_residue_witness_matches_no_zero_failure`: true when existence of a generated zero-residue witness agrees with failure of the no-zero structural check.
- `period_threshold_violation_matches_no_zero_failure`: true when a period-at-most-path-budget violation agrees with failure of the no-zero structural check.
- `unique_lag_count_shortfall_certifies_incomplete`: true when the certificate avoids the impossible state where the deduplicated unique lag-candidate count is below `context - 1` but coverage is still reported complete.
- `unique_lag_count_shortfall_matches_gap_witness_under_period_threshold`: true when the period-threshold hypothesis is absent or, under `local_window < context` plus all `path_length < stride_period` checks, unique lag-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_lag_count_matches_complete_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, complete coverage matches `theorem_side_unique_lag_candidate_count == context - 1`.
- `covered_count_matches_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, covered count equals the unique lag-candidate count.
- `uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, uncovered count equals `context - 1 - theorem_side_unique_lag_candidate_count`.
- `theorem_side_unique_query_candidate_count`: deduplicated query-indexed predecessor count.
- `unique_query_count_shortfall_matches_gap_witness_under_candidate_range_and_injective`: true when the candidate-range and predecessor-injectivity hypotheses are absent or, under those hypotheses, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_no_wrap_separated`: true when the no-wrap structural condition is absent or, under that checkable condition, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_no_zero_residue`: true when the no-zero structural condition is absent or, under that checkable condition, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `unique_query_count_shortfall_matches_gap_witness_under_period_threshold`: true when the period-threshold hypothesis is absent or, under `local_window < context` plus all `path_length < stride_period` checks, query-candidate shortfall is equivalent to an uncovered-lag witness.
- `theorem_side_lag_candidates_no_collision`: no duplicate lag candidates.
- `theorem_side_query_candidates_no_collision`: no duplicate query-indexed candidates.

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

The gap/coverage spine is `AIT-T0020` through `AIT-T0035`. The theorem-side candidate-list,
budget, no-collision, and predecessor-indexing spine is `AIT-T0036` through `AIT-T0077`.
The finite uncovered/covered list, count-partition, first-gap, public interval-summary, query-count, raw-budget necessary-condition, unique-lag necessary-condition, candidate-range unique-count iff, candidate-range gap-count, no-wrap separated candidate-range discharge, and no-zero residue candidate-range discharge spine is `AIT-T0078` through `AIT-T0119`.

## Boundary

This certifier checks a finite index contract. It does not run a neural network, fit a
learned sparse-attention head, measure loss, measure speed, or prove usefulness on a real
task. Use it as a proof-carrying design check before experiments, not as experimental
evidence.
