# Prime Engine External Mode Confirmation

Generated: `2026-06-20T07:24:33Z`
Minimum confirmations: `2`
Require stable samples: `True`
Fresh-run count requests per timed sample: `20`

- observed groups: `4`
- confirmed: `2`
- unconfirmed: `2`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 0/2 | 0/3 | 2.138, 1.594, 1.864 | 1.405, 1.210, 1.058 | `unconfirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 2/2 | 2/3 | 1.811, 1.925, 1.983 | 1.152, 1.123, 1.050 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8/8 | 3/2 | 3/3 | 1.960, 1.602, 4.131 | 2.283, 2.404, 1.549 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8/8 | 1/2 | 1/3 | 2.226, 1.852, 2.085 | 4.672, 5.667, 4.948 | `unconfirmed` |
