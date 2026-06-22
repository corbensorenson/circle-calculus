# Prime Engine External Mode Confirmation

Generated: `2026-06-21T23:44:27Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `40`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260621T234424Z_01.csv` | `2026-06-21T23:44:25Z` | 7 | 40 | `352342ffe9e6` | `8d8be40790f4` |
| `prime_engine_external_mode_confirm_20260621T234424Z_02.csv` | `2026-06-21T23:44:27Z` | 7 | 40 | `352342ffe9e6` | `8d8be40790f4` |

- observed groups: `1`
- confirmed: `0`
- unconfirmed: `1`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 2/2 | 0.054 | 37.017 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 1/2 | 36.801, 36.178 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 2/2 | 2/2 | 35.922, 34.778 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1572864 | 7/8 | 2/2 | 2/2 | 34.652, 36.758 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1638400 | 7/8 | 2/2 | 2/2 | 35.012, 39.145 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 2097152 | 5/8 | 2/2 | 2/2 | 32.301, 37.062 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 1/2 | 37.017, 32.070 | `unconfirmed` |
