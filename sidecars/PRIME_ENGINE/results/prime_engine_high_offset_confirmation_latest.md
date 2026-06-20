# Prime Engine External Mode Confirmation

Generated: `2026-06-20T08:55:11Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `20`

- observed groups: `4`
- confirmed: `4`
- unconfirmed: `0`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 2.325, 1.988, 1.768 | 0.908, 1.041, 1.104 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 1.936, 1.923, 1.830 | 1.094, 1.106, 1.137 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 2.015, 3.113, 2.136 | 1.962, 1.685, 1.883 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 3/2 | 3/3 | 2.658, 2.099, 2.214 | 3.995, 4.688, 4.481 | `confirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 0.908, 1.041, 1.104 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 1.094, 1.106, 1.137 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 1.962, 1.685, 1.883 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 3/2 | 3/3 | 3.995, 4.688, 4.481 | `confirmed` |
