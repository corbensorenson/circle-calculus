# Prime Engine External Mode Confirmation

Generated: `2026-06-22T03:05:29Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `40`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260622T030526Z_01.csv` | `2026-06-22T03:05:27Z` | 7 | 40 | `d7712080a7ca` | `31ac85d89c8b` |
| `prime_engine_external_mode_confirm_20260622T030526Z_02.csv` | `2026-06-22T03:05:29Z` | 7 | 40 | `d7712080a7ca` | `31ac85d89c8b` |

- observed groups: `1`
- confirmed: `0`
- unconfirmed: `1`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 2/2 | 0.060 | 39.998 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/2 | 37.418, 37.563 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 4/2 | 4/4 | 32.310, 31.030, 38.293, 37.461 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1572864 | 7/8 | 2/2 | 2/2 | 31.629, 36.969 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1638400 | 7/8 | 2/2 | 2/2 | 30.966, 34.159 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 2/2 | 2/2 | 39.998, 37.269 | `confirmed` |
