# Prime Engine External Mode Confirmation

Generated: `2026-06-19T20:32:12Z`
Minimum confirmations: `2`
Require stable samples: `True`

- observed groups: `3`
- confirmed: `1`
- unconfirmed: `2`

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primesieve_count` | `dynamic` | 196608 | 8/8 | 0/2 | 0/2 | 3.104 | `unconfirmed` |
| [0, 100000000) | `external_primesieve_count` | `dynamic` | 98304 | 8/8 | 0/2 | 0/2 | 6.974 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `segmented` | 3145728 | 4/8 | 2/2 | 2/2 | 6.188, 6.214 | `confirmed` |
