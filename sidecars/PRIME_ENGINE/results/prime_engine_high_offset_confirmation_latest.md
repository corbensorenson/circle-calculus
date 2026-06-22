# Prime Engine External Mode Confirmation

Generated: `2026-06-22T02:36:05Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `80`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260622T023502Z_01.csv` | `2026-06-22T02:35:22Z` | 9 | 80 | `d7712080a7ca` | `31ac85d89c8b` |
| `prime_engine_external_mode_confirm_20260622T023502Z_02.csv` | `2026-06-22T02:35:46Z` | 9 | 80 | `d7712080a7ca` | `31ac85d89c8b` |
| `prime_engine_external_mode_confirm_20260622T023502Z_03.csv` | `2026-06-22T02:36:05Z` | 9 | 80 | `d7712080a7ca` | `31ac85d89c8b` |

- observed groups: `4`
- confirmed: `2`
- unconfirmed: `2`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 3/2 | 3/3 | 0.032, 0.024, 0.030 | 74.331, 78.958, 67.264 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 3/2 | 3/3 | 0.028, 0.025, 0.027 | 78.149, 84.217, 89.444 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/3 | 0.028, 0.035, 0.035 | 147.052, 150.918, 120.838 | `unconfirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/3 | 0.030, 0.047, 0.038 | 372.018, 326.063, 297.813 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 3/2 | 3/3 | 74.331, 78.958, 67.264 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 3/2 | 3/3 | 78.149, 84.217, 89.444 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/3 | 147.052, 150.918, 120.838 | `unconfirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/3 | 372.018, 326.063, 297.813 | `unconfirmed` |
