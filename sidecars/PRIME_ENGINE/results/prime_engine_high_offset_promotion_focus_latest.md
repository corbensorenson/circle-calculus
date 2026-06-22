# Prime Engine External Mode Confirmation

Generated: `2026-06-22T02:36:40Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `40`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260622T023636Z_01.csv` | `2026-06-22T02:36:38Z` | 7 | 40 | `d7712080a7ca` | `31ac85d89c8b` |
| `prime_engine_external_mode_confirm_20260622T023636Z_02.csv` | `2026-06-22T02:36:39Z` | 7 | 40 | `d7712080a7ca` | `31ac85d89c8b` |

- observed groups: `1`
- confirmed: `0`
- unconfirmed: `1`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1572864 | 7/8 | 1/2 | 2/2 | 0.054 | 37.837 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/2 | 36.175, 30.965 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 3/2 | 3/4 | 37.704, 36.750, 37.858, 35.486 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1572864 | 7/8 | 2/2 | 2/2 | 37.837, 32.432 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1638400 | 7/8 | 1/2 | 1/2 | 39.441, 23.137 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 2/2 | 2/2 | 36.588, 38.278 | `confirmed` |
