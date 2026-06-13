# KV-Cache Ring-Buffer Certifier Quickstart

This is the command-line surface for the finite KV-cache ring-buffer contract.

It answers one precise question:

```text
For a declared cache size, current token, inspected token, and optional retained
batch, what ring-buffer slots are used, which tokens are still live, and does
the generated full live window cover the finite slot range without duplicates?
```

It does not claim paging-policy quality, throughput, memory savings, retrieval
quality, implementation correctness, deployment safety, or model quality.

## Example

```bash
python scripts/kv_cache_certify.py \
  --cache-size 16 \
  --current 31 \
  --token 20 \
  --batch-tokens 20,24,29,31
```

Expected shape:

```text
kv_cache_contract=LIVE cache_size=16 current=31 token=20 slot=4 current_slot=15 lag=11
overwrite_boundary=next_overwrite=36 after_current=True stale_by_boundary=False no_same_slot_overwrite_before_current=True same_slot_overwrite_witness_when_stale=False retained_iff_no_same_slot_overwrite_trace=True
batch_contract=tokens=(20, 24, 29, 31) slots=(4, 8, 13, 15) all_retained=True tokens_distinct=True slots_distinct=True
live_window_contract=FULL start=16 length=16 slots_distinct=True slot_count_matches_cache_size=True full_coverage_contract=True
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
- `live_window_certificate`: the generated retained-token interval, its slot list, and whether the full-window coverage contract applies.
- `full_coverage_contract`: true when the live window is full, the generated slot list is duplicate-free, its length equals `cache_size`, and every emitted slot is inside the cache range.

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

## Boundary

This certifier checks finite arithmetic over a declared ring-buffer cache. It
does not model a GPU kernel, memory allocator, paging system, serving stack,
retrieval policy, attention quality, or language-model behavior. Use it as a
proof-carrying indexing/freshness check before implementation and experiments,
not as experimental evidence.
