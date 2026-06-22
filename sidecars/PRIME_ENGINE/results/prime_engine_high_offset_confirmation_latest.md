# Prime Engine External Mode Confirmation

Generated: `2026-06-21T23:43:54Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `80`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260621T234251Z_01.csv` | `2026-06-21T23:43:10Z` | 9 | 80 | `352342ffe9e6` | `8d8be40790f4` |
| `prime_engine_external_mode_confirm_20260621T234251Z_02.csv` | `2026-06-21T23:43:31Z` | 9 | 80 | `352342ffe9e6` | `8d8be40790f4` |
| `prime_engine_external_mode_confirm_20260621T234251Z_03.csv` | `2026-06-21T23:43:54Z` | 9 | 80 | `352342ffe9e6` | `8d8be40790f4` |

- observed groups: `4`
- confirmed: `4`
- unconfirmed: `0`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 2097152 | 5/8 | 3/2 | 3/3 | 0.025, 0.039, 0.027 | 78.348, 59.327, 72.227 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 3/2 | 3/3 | 0.025, 0.034, 0.043 | 96.826, 71.300, 71.107 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 0.031, 0.030, 0.051 | 144.592, 154.534, 97.281 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 0.032, 0.040, 0.038 | 385.317, 329.671, 395.925 | `confirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 2097152 | 5/8 | 3/2 | 3/3 | 78.348, 59.327, 72.227 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8/8 | 3/2 | 3/3 | 96.826, 71.300, 71.107 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 144.592, 154.534, 97.281 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 385.317, 329.671, 395.925 | `confirmed` |
