# Stride-Family Sparse-Attention Certificate Results

This is a proof-carrying finite sparse-attention candidate-set certificate for a declared local-window plus stride-family plan. It reports covered lags, uncovered gap witnesses, no-collision budget predicates, and structured controls. It is not a neural attention-quality, long-context, throughput, runtime, memory-use, or model-quality claim.

| Context | Query count | Local window | Path length | Strides | Wrong strides | Coverage complete | Coverage ratio |
| ---: | ---: | ---: | ---: | --- | --- | --- | ---: |
| 120 | 120 | 4 | 3 | 7, 13 | 5, 9 | False | 0.084 |

| Structured family | Single stride | Local only | Wrong family | Full attention | Nonstructured family | Nonstructured full |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1.000 | 0.500 | 0.250 | 0.250 | 1.000 | 0.083 | 1.000 |

| Average family candidates | Average single-stride candidates | Average local candidates | Average full candidates |
| ---: | ---: | ---: | ---: |
| 10.000 | 7.000 | 4.000 | 120.000 |

| Covered lag count | Uncovered lag count | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Positive lags | Partition complete | Uncovered intervals | Candidate budget | Raw budget bound | Raw shortfall certifies incomplete | Unique lag candidates | Candidate range | No-wrap sufficient | No-zero sufficient | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Deduplicated bound | Full-attention budget |
| ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| 10 | 109 | 5 | True | True | True | True | True | True | 119 | True | 6 | 10 | 10 | True | 10 | True | False | True | True | True | True | True | 10 | 120 |

| Coil residues no collision | Local/coil disjoint | Lag candidates no collision | Predecessor injective | Query candidates no collision | Query count <= unique lag count | Query count = unique lag count |
| --- | --- | --- | --- | --- | --- | --- |
| True | True | True | True | True | True | True |

Covered lags:

```text
1, 2, 3, 4, 7, 14, 21, 13, 26, 39
```

Default fixture theorem ids:

```text
AIT-T0084, AIT-T0085, AIT-T0091, AIT-T0102, AIT-T0104
```

First uncovered lags:

```text
5, 6, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33
```

Uncovered lag intervals:

```text
5..6, 8..12, 15..20, 22..25, 27..38, 40..119
```

Complete sparse-family fixture:

| Context | Local window | Path length | Strides | Coverage complete | Uncovered lags | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Raw budget | Raw shortfall certifies incomplete | Unique lag candidates | Candidate range | No-wrap sufficient | No-zero sufficient | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Unique query candidates | Query <= unique lag | Query = unique lag | Fixture theorem ids |
| ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| 9 | 2 | 2 | 3, 4, 7 | True | 0 | None | True | True | True | True | False | True | 8 | True | 8 | True | False | True | True | True | True | True | 8 | True | True | AIT-T0086, AIT-T0087, AIT-T0088, AIT-T0089, AIT-T0105 |

Complete fixture covered lags:

```text
1, 2, 3, 6, 4, 8, 7, 5
```

Planner-style declared plans:

| Plan | Context | Local window | Path length | Strides | Complete | Coverage | Candidate budget | Budget ratio | Covered+uncovered | Positive lags | Uncovered lags | First gap | First gap is head | No first gap iff complete | First gap is semantic miss | Count witness | Covered shortfall | Shortfall witness | Gap intervals | Raw shortfall certifies incomplete | Candidate range | No-wrap sufficient | No-zero sufficient | Unique count iff complete | Covered count = unique | Uncovered count formula | Unique lag shortfall certifies incomplete | Raw budget survives dedup |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| default_gap_fixture_120 | 120 | 4 | 3 | 7, 13 | False | 0.084 | 10 | 0.083 | 119 | 119 | 109 | 5 | True | True | True | True | True | True | 6 | True | True | False | True | True | True | True | True | lag=True, query=True |
| complete_toy_fixture_9 | 9 | 2 | 2 | 3, 4, 7 | True | 1.000 | 8 | 0.889 | 8 | 8 | 0 | None | True | True | True | True | False | True | 0 | True | True | False | True | True | True | True | True | lag=True, query=True |
| long_context_no_wrap_probe_4096 | 4096 | 32 | 4 | 33, 160, 800 | False | 0.011 | 44 | 0.011 | 4095 | 4095 | 4051 | 34 | True | True | True | True | True | True | 12 | True | True | True | True | True | True | True | True | lag=True, query=True |
| long_context_coprime_probe_8192 | 8192 | 64 | 8 | 127, 509, 1021, 2039 | False | 0.012 | 96 | 0.012 | 8191 | 8191 | 8095 | 65 | True | True | True | True | True | True | 32 | True | True | False | True | True | True | True | True | lag=True, query=True |

Planner rows are compact reports over declared sparse layouts. Re-run the
`reproduce_command` in the JSON for the full covered/uncovered-lag certificate.

Theorem ids:

```text
AIT-T0016, AIT-T0017, AIT-T0020, AIT-T0021, AIT-T0022, AIT-T0023, AIT-T0024, AIT-T0025, AIT-T0028, AIT-T0029, AIT-T0030, AIT-T0031, AIT-T0032, AIT-T0033, AIT-T0034, AIT-T0035, AIT-T0036, AIT-T0037, AIT-T0038, AIT-T0039, AIT-T0040, AIT-T0041, AIT-T0042, AIT-T0043, AIT-T0044, AIT-T0045, AIT-T0046, AIT-T0047, AIT-T0048, AIT-T0049, AIT-T0050, AIT-T0051, AIT-T0052, AIT-T0053, AIT-T0054, AIT-T0055, AIT-T0056, AIT-T0057, AIT-T0058, AIT-T0059, AIT-T0060, AIT-T0061, AIT-T0062, AIT-T0063, AIT-T0064, AIT-T0065, AIT-T0066, AIT-T0067, AIT-T0068, AIT-T0069, AIT-T0070, AIT-T0071, AIT-T0072, AIT-T0073, AIT-T0074, AIT-T0075, AIT-T0076, AIT-T0077, AIT-T0078, AIT-T0079, AIT-T0080, AIT-T0081, AIT-T0082, AIT-T0083, AIT-T0084, AIT-T0085, AIT-T0090, AIT-T0092, AIT-T0093, AIT-T0094, AIT-T0095, AIT-T0096, AIT-T0097, AIT-T0098, AIT-T0099, AIT-T0100, AIT-T0101, AIT-T0102, AIT-T0103, AIT-T0104, AIT-T0105, AIT-T0106, AIT-T0107, AIT-T0108, AIT-T0109, AIT-T0110, AIT-T0111, AIT-T0112, AIT-T0113, AIT-T0114, AIT-T0115, AIT-T0116, AIT-T0117, AIT-T0118, AIT-T0119
```

Reproduce with:

```bash
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py --format markdown
```
