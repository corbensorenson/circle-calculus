# KV-Cache Ring-Buffer Certificate Results

These are proof-carrying finite ring-buffer indexing certificates for a declared KV-cache window, retained token batch, and modeled adapter request trace. They are not model-quality, throughput, memory-saving, retrieval-quality, paging-policy, implementation, or deployment-safety claims.

| Cache size | Current | Token | Slot | Current slot | Lag | Retained | Distinct from current | Next overwrite | Overwrite after current | Stale by overwrite boundary | No same-slot overwrite before current | Stale same-slot overwrite witness | Retained iff no later same-slot write | Trace iff boundary | Theorem ids |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| 16 | 31 | 20 | 4 | 15 | 11 | True | True | 36 | True | False | True | False | True | True | AIM-T0059, AIM-T0060, AIM-T0061, AIM-T0062, AIM-T0063, AIM-T0064, AIM-T0065, AIM-T0066, AIM-T0069, AIM-T0070, AIM-T0075, AIM-T0076, AIM-T0077, AIM-T0091 |

| Batch tokens | Batch slots | All retained | Tokens distinct | Slots distinct | Retained iff no later same-slot writes | Next overwrites after current | Trace iff boundary | Trace-fresh slots distinct | Theorem ids |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20, 24, 29, 31 | 4, 8, 13, 15 | True | True | True | True | True | True | True | AIM-T0059, AIM-T0065, AIM-T0066, AIM-T0067, AIM-T0068, AIM-T0078, AIM-T0079, AIM-T0091, AIM-T0092 |

| Request id | Requested tokens | Requested slots | All non-future | All retained | Tokens distinct | Slots distinct | First stale token | First stale next overwrite | Stale member blocks pass | Trace iff | Next overwrites after current | Trace iff boundary | Trace-fresh slots distinct | Ordered live-window subrequest | Duplicate-free live-window subrequest | Subrequest pass contract | Pass certificate | Pass iff boundary | Pass iff no stale member | Theorem ids |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default_read_request | 20, 24, 29, 31 | 4, 8, 13, 15 | True | True | True | True | None | None | False | True | True | True | True | True | True | True | True | True | True | AIM-T0059, AIM-T0067, AIM-T0068, AIM-T0078, AIM-T0079, AIM-T0086, AIM-T0091, AIM-T0092, AIM-T0093, AIM-T0094, AIM-T0095, AIM-T0096, AIM-T0097, AIM-T0098 |

| Live start | Live length | Live tokens | Live slots | All retained | Slots distinct | Full window | Slot count matches cache | Slot range covered | Slot count iff full window | Slots within cache | Full coverage contract | Full coverage iff full window | Theorem ids |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 16 | 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | True | True | True | True | True | True | True | True | True | AIM-T0071, AIM-T0072, AIM-T0073, AIM-T0074, AIM-T0080, AIM-T0081, AIM-T0082, AIM-T0083 |

| Request id | Requested tokens | Requested slots | Exact live-window request | Request count | All retained | Tokens distinct | Slots distinct | Pass certificate | Live-window request contract | Fixture theorem ids | Theorem ids |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| generated_live_window_read | 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | True | 16 | True | True | True | True | True | AIM-T0089 | AIM-T0087, AIM-T0088 |

Reproduce with:

```bash
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py --format markdown
```
