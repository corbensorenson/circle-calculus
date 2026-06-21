# Prime Engine External Mode Confirmation

Generated: `2026-06-21T06:35:40Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `40`

## Input Provenance

| Input | Finished | Rounds | Batch | Circle Binary | Defaults |
| --- | --- | ---: | ---: | --- | --- |
| `prime_engine_external_mode_confirm_20260621T063533Z_01.csv` | `2026-06-21T06:35:37Z` | 7 | 40 | `a1bb0ae27d96` | `e042e6ebdc5b` |
| `prime_engine_external_mode_confirm_20260621T063533Z_02.csv` | `2026-06-21T06:35:40Z` | 7 | 40 | `a1bb0ae27d96` | `e042e6ebdc5b` |

- observed groups: `1`
- confirmed: `0`
- unconfirmed: `1`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 1/2 | 2/2 | 1.785 | 1.087 | `unconfirmed` |

## Identity Evidence

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 4/4 | 1.087, 1.042, 0.995, 0.982 | `confirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 2/2 | 1.003, 0.999 | `unconfirmed` |
