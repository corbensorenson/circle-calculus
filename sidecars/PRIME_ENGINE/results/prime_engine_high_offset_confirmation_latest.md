# Prime Engine External Mode Confirmation

Generated: `2026-06-20T07:09:42Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `20`

- observed groups: `4`
- confirmed: `4`
- unconfirmed: `0`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 2/2 | 3/3 | 1.763, 2.066, 1.814 | 1.070, 0.964, 1.063 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 2/2 | 2/3 | 1.805, 2.082, 3.039 | 1.145, 1.016, 0.789 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 2/2 | 2/3 | 2.325, 1.900, 2.118 | 1.989, 2.021, 1.997 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 3/2 | 3/3 | 2.032, 2.907, 2.310 | 4.614, 3.624, 4.396 | `confirmed` |
