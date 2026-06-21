# Prime Engine External Mode Confirmation

Generated: `2026-06-21T08:05:02Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `80`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260621T080338Z_01.csv` | `2026-06-21T08:04:06Z` | 9 | 80 | `cf7aadfb9e3f` | `e042e6ebdc5b` |
| `prime_engine_external_mode_confirm_20260621T080338Z_02.csv` | `2026-06-21T08:04:34Z` | 9 | 80 | `cf7aadfb9e3f` | `e042e6ebdc5b` |
| `prime_engine_external_mode_confirm_20260621T080338Z_03.csv` | `2026-06-21T08:05:02Z` | 9 | 80 | `cf7aadfb9e3f` | `e042e6ebdc5b` |

- observed groups: `4`
- confirmed: `4`
- unconfirmed: `0`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 2.037, 2.181, 1.847 | 1.162, 1.088, 1.224 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 2/2 | 2/3 | 1.677, 2.418, 1.729 | 1.480, 1.063, 1.429 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 1.996, 2.123, 2.880 | 2.347, 2.394, 2.026 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 2.529, 2.425, 2.482 | 4.713, 4.472, 4.073 | `confirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 1.162, 1.088, 1.224 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 2/2 | 2/3 | 1.480, 1.063, 1.429 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 2.347, 2.394, 2.026 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 4.713, 4.472, 4.073 | `confirmed` |
