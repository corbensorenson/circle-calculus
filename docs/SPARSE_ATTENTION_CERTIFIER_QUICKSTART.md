# Sparse-Attention Certifier Quickstart

This is the command-line surface for the finite local-window plus stride-family
sparse-attention contract.

It answers one precise question:

```text
For a declared context length, local window, stride family, and path length,
which positive dependency lags are covered, which are gaps, and when does the
deduplicated theorem-side candidate count preserve the raw candidate budget?
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
uncovered_count_witness=True positive=True first_gap=5 theorem=AIT-T0096
covered_count_shortfall=True gap_witness_equiv=True theorem=AIT-T0097
uncovered_lag_intervals=((5, 6), (8, 12), (15, 20), (22, 25), (27, 38), (40, 119))
candidate_budget_per_query=10 raw_upper_bound=10 deduplicated_bound=10 full_attention_budget=120
raw_budget_shortfall=True certifies_incomplete=True theorem=AIT-T0110
unique_lag_shortfall=True certifies_incomplete=True theorem=AIT-T0111
candidate_range=True unique_count_complete_iff=True theorem=AIT-T0112
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
- `unique_lag_count_shortfall_certifies_incomplete`: true when the certificate avoids the impossible state where the deduplicated unique lag-candidate count is below `context - 1` but coverage is still reported complete.
- `unique_lag_count_matches_complete_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, complete coverage matches `theorem_side_unique_lag_candidate_count == context - 1`.
- `covered_count_matches_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, covered count equals the unique lag-candidate count.
- `uncovered_count_matches_context_minus_unique_lag_count_under_candidate_range`: true when the candidate-range hypothesis is absent or, under that hypothesis, uncovered count equals `context - 1 - theorem_side_unique_lag_candidate_count`.
- `theorem_side_unique_query_candidate_count`: deduplicated query-indexed predecessor count.
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
The finite uncovered/covered list, count-partition, first-gap, public interval-summary, query-count, raw-budget necessary-condition, unique-lag necessary-condition, candidate-range unique-count iff, and candidate-range gap-count spine is `AIT-T0078` through `AIT-T0114`.

## Boundary

This certifier checks a finite index contract. It does not run a neural network, fit a
learned sparse-attention head, measure loss, measure speed, or prove usefulness on a real
task. Use it as a proof-carrying design check before experiments, not as experimental
evidence.
