# Prime Engine External Mode Confirmation

Generated: `2026-06-21T09:53:41Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `40`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260621T095326Z_01.csv` | `2026-06-21T09:53:34Z` | 7 | 40 | `cf7aadfb9e3f` | `e042e6ebdc5b` |
| `prime_engine_external_mode_confirm_20260621T095326Z_02.csv` | `2026-06-21T09:53:41Z` | 7 | 40 | `cf7aadfb9e3f` | `e042e6ebdc5b` |

- observed groups: `1`
- confirmed: `0`
- unconfirmed: `1`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 2/2 | 2.361 | 1.190 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 4/2 | 4/4 | 1.094, 1.033, 1.358, 1.102 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 1/2 | 1/2 | 0.980, 1.184 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1572864 | 7/8 | 2/2 | 2/2 | 1.031, 1.044 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1638400 | 7/8 | 2/2 | 2/2 | 1.097, 1.138 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 1/2 | 1.190, 1.325 | `unconfirmed` |
