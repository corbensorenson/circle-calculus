# KV-Cache Ring-Buffer Certificate Results

These are proof-carrying finite ring-buffer indexing certificates for a declared KV-cache window, retained token batch, and modeled adapter request trace. They are not model-quality, throughput, memory-saving, retrieval-quality, paging-policy, implementation, or deployment-safety claims.

| Cache size | Current | Token | Slot | Current slot | Lag | Retained | Distinct from current | Next overwrite | Overwrite after current | Stale by overwrite boundary | No same-slot overwrite before current | Stale same-slot overwrite witness | Retained iff no later same-slot write | Theorem ids |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| 16 | 31 | 20 | 4 | 15 | 11 | True | True | 36 | True | False | True | False | True | AIM-T0059, AIM-T0060, AIM-T0061, AIM-T0062, AIM-T0063, AIM-T0064, AIM-T0065, AIM-T0066, AIM-T0069, AIM-T0070, AIM-T0075, AIM-T0076, AIM-T0077 |

| Batch tokens | Batch slots | All retained | Tokens distinct | Slots distinct | Retained iff no later same-slot writes | Trace-fresh slots distinct | Theorem ids |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20, 24, 29, 31 | 4, 8, 13, 15 | True | True | True | True | True | AIM-T0059, AIM-T0065, AIM-T0066, AIM-T0067, AIM-T0068, AIM-T0078, AIM-T0079 |

| Request id | Requested tokens | Requested slots | All non-future | All retained | Tokens distinct | Slots distinct | Trace iff | Trace-fresh slots distinct | Pass certificate | Theorem ids |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default_read_request | 20, 24, 29, 31 | 4, 8, 13, 15 | True | True | True | True | True | True | True | AIM-T0059, AIM-T0067, AIM-T0068, AIM-T0078, AIM-T0079 |

| Live start | Live length | Live tokens | Live slots | All retained | Slots distinct | Full window | Slot count matches cache | Slot range covered | Slot count iff full window | Slots within cache | Full coverage contract | Full coverage iff full window | Theorem ids |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 16 | 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | True | True | True | True | True | True | True | True | True | AIM-T0071, AIM-T0072, AIM-T0073, AIM-T0074, AIM-T0080, AIM-T0081, AIM-T0082, AIM-T0083 |

Reproduce with:

```bash
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_kv_cache_ring_buffer.py --format markdown
```
