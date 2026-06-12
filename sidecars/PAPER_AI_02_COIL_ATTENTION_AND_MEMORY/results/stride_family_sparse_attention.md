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

| Covered lag count | Uncovered lag count | Candidate budget | Raw budget bound | Deduplicated bound | Full-attention budget |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 109 | 10 | 10 | 10 | 120 |

| Coil residues no collision | Local/coil disjoint | Lag candidates no collision | Predecessor injective | Query candidates no collision |
| --- | --- | --- | --- | --- |
| True | True | True | True | True |

Covered lags:

```text
1, 2, 3, 4, 7, 14, 21, 13, 26, 39
```

First uncovered lags:

```text
5, 6, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33
```

Theorem ids:

```text
AIT-T0016, AIT-T0017, AIT-T0020, AIT-T0021, AIT-T0022, AIT-T0023, AIT-T0024, AIT-T0025, AIT-T0028, AIT-T0029, AIT-T0030, AIT-T0031, AIT-T0032, AIT-T0033, AIT-T0034, AIT-T0035, AIT-T0036, AIT-T0037, AIT-T0038, AIT-T0039, AIT-T0040, AIT-T0041, AIT-T0042, AIT-T0043, AIT-T0044, AIT-T0045, AIT-T0046, AIT-T0047, AIT-T0048, AIT-T0049, AIT-T0050, AIT-T0051, AIT-T0052, AIT-T0053, AIT-T0054, AIT-T0055, AIT-T0056, AIT-T0057, AIT-T0058, AIT-T0059, AIT-T0060, AIT-T0061, AIT-T0062, AIT-T0063, AIT-T0064, AIT-T0065, AIT-T0066, AIT-T0067, AIT-T0068, AIT-T0069, AIT-T0070, AIT-T0071, AIT-T0072, AIT-T0073, AIT-T0074, AIT-T0075, AIT-T0076, AIT-T0077
```

Reproduce with:

```bash
python sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_stride_family_sparse_attention.py --format markdown
```
