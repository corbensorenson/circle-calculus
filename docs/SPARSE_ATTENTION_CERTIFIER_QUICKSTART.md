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
covered_lags=10 uncovered_lags=109 coverage_ratio=0.084034
candidate_budget_per_query=10 raw_upper_bound=10 deduplicated_bound=10 full_attention_budget=120
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
- `raw_candidate_budget_upper_bound`: `local_window + path_length * number_of_strides`.
- `theorem_side_unique_lag_candidate_count`: deduplicated lag count from the theorem-side list.
- `theorem_side_unique_query_candidate_count`: deduplicated query-indexed predecessor count.
- `theorem_side_lag_candidates_no_collision`: no duplicate lag candidates.
- `theorem_side_query_candidates_no_collision`: no duplicate query-indexed candidates.

The raw-budget iff endpoints are:

- `AIT-T0076`: lag-candidate raw-budget equality holds if and only if the lag-candidate list has no duplicates.
- `AIT-T0077`: query-candidate raw-budget equality holds if and only if the query-indexed candidate list has no duplicates.

The finite-list endpoints are:

- `AIT-T0081`: membership in the uncovered-lag list is exactly a positive in-context semantic miss.
- `AIT-T0082`: complete coverage is equivalent to an empty uncovered-lag list.
- `AIT-T0083`: complete coverage is equivalent to uncovered-lag count zero.
- `AIT-T0090`: membership in the covered-lag list is exactly a positive in-context semantic hit.
- `AIT-T0091`: the default fixture's covered-lag list has exactly `10` entries.

The gap/coverage spine is `AIT-T0020` through `AIT-T0035`. The theorem-side candidate-list,
budget, no-collision, and predecessor-indexing spine is `AIT-T0036` through `AIT-T0077`.
The finite uncovered/covered list and count spine is `AIT-T0078` through `AIT-T0091`.

## Boundary

This certifier checks a finite index contract. It does not run a neural network, fit a
learned sparse-attention head, measure loss, measure speed, or prove usefulness on a real
task. Use it as a proof-carrying design check before experiments, not as experimental
evidence.
