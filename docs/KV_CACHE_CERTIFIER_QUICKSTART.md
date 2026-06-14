# KV-Cache Ring-Buffer Certifier Quickstart

This is the command-line surface for the finite KV-cache ring-buffer contract.

It answers one precise question:

```text
For a declared cache size, current token, inspected token, and optional modeled
adapter read request, what ring-buffer slots are used, which requested tokens
are still live, and does the generated full live window cover the finite slot
range without duplicates?
```

It does not claim paging-policy quality, throughput, memory savings, retrieval
quality, implementation correctness, deployment safety, or model quality.

## Example

```bash
python scripts/kv_cache_certify.py \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --request-id prefill_read
```

Expected shape:

```text
kv_cache_contract=LIVE cache_size=16 current=31 token=20 slot=4 current_slot=15 lag=11
overwrite_boundary=next_overwrite=36 after_current=True stale_by_boundary=False no_same_slot_overwrite_before_current=True same_slot_overwrite_witness_when_stale=False retained_iff_no_same_slot_overwrite_trace=True
batch_contract=tokens=(20, 24, 29, 31) slots=(4, 8, 13, 15) all_retained=True tokens_distinct=True slots_distinct=True
adapter_request_trace=PASS request_id=prefill_read tokens=(20, 24, 29, 31) slots=(4, 8, 13, 15) all_non_future=True all_retained=True tokens_distinct=True slots_distinct=True
live_window_contract=FULL start=16 length=16 slots_distinct=True slot_count_matches_cache_size=True slot_count_matches_full_window=True slot_range_covered=True full_coverage_contract=True full_coverage_contract_matches_full_window=True
```

Machine-readable output:

```bash
python scripts/kv_cache_certify.py \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31 \
  --format json \
  --json-out reports/kv_cache_certificate.json
```

## Reading The Certificate

- `window_certificate`: the inspected token's slot, current slot, lag, retained-window status, next same-slot overwrite boundary, whether any later token up to the current read point reused the same slot, whether a stale token has the explicit same-slot overwrite witness `token + cache_size`, and whether retained-window membership is equivalent to no later same-slot write in the trace up to `current`.
- `batch_certificate`: the optional retained batch, its slots, whether all batch tokens are retained, whether the batch slots are duplicate-free, whether all-retained is equivalent to every requested non-future token having no later same-slot write up to `current`, and whether a trace-fresh duplicate-free batch maps to duplicate-free slots.
- `adapter_request_trace_certificate`: the same retained-batch theorem spine packaged as a named modeled adapter read request. It passes only when the requested tokens are non-future, retained, duplicate-free, mapped to duplicate-free slots, and trace-fresh pointwise.
- `live_window_certificate`: the generated retained-token interval, its slot list, and whether the full-window coverage contract applies.
- `full_coverage_contract`: true when the live window is full, the generated slot list is duplicate-free, its length equals `cache_size`, and every emitted slot is inside the cache range.
- `slot_count_matches_full_window`: true when the generated slot-list count matches `cache_size` exactly when the live window is full.
- `slot_range_covered`: true when the generated live-window slot list contains every declared cache slot.
- `full_coverage_contract_matches_full_window`: true when the full generated live-window coverage contract is equivalent to the live window being full.

The main theorem spine is:

- `AIM-T0059` through `AIM-T0064`: bounded slots, same-slot periodicity, collision/gap facts, overwrite timing, and current-slot distinctness.
- `AIM-T0065` through `AIM-T0068`: ordered, unordered, and retained-batch slot distinctness.
- `AIM-T0069` and `AIM-T0070`: retained-window membership and stale-token status as next-overwrite boundary facts.
- `AIM-T0071` through `AIM-T0074`: generated live-window exactness, duplicate-free slots, and full-window finite slot coverage.
- `AIM-T0075`: retained-token no-same-slot-overwrite-before-current guard for read/write adapter checks.
- `AIM-T0076`: stale-token same-slot overwrite witness at `token + cache_size`.
- `AIM-T0077`: retained iff no later same-slot write appears in the finite trace up to `current`.
- `AIM-T0078`: batch all-retained iff every requested non-future token has no later same-slot write up to `current`.
- `AIM-T0079`: trace-fresh duplicate-free non-future read batches map to duplicate-free ring-buffer slots.
- `AIM-T0080`: the generated live-window slot-map count equals `cache_size` if and only if the window is full.
- `AIM-T0081`: the full generated live-window slot coverage contract holds if and only if the window is full.
- `AIM-T0082`: in a full generated live window, a slot appears in the generated slot map if and only if it is less than `cache_size`.
- `AIM-T0083`: the generated live-window slot map covers every declared cache slot exactly when the live window is full.
- `AIM-T0086`: the modeled adapter request pass predicate is equivalent to non-future, duplicate-free, trace-fresh requested tokens under positive cache size.
- `AIM-T0087`: the generated live-window token list passes the modeled adapter request-trace contract under positive cache size.
- `AIM-T0088`: the generated-live-window request contract is equivalent to the requested token list being exactly the generated live window.
- `AIM-T0089`: the public `cache_size = 16`, `current = 31` fixture realizes the exact generated-live-window request with tokens `16..31`.

## Boundary

This certifier checks finite arithmetic over a declared ring-buffer cache and
a modeled read request. The adapter request pass bit is a proof-carrying finite
checklist, not an implementation proof. It does not model a GPU kernel, memory allocator,
paging system, serving stack, retrieval policy, attention quality, or
language-model behavior. Use it as a proof-carrying indexing/freshness check
before implementation and experiments, not as experimental evidence.
