# Prime Engine Default Calibration

Generated: `2026-06-19T20:33:51Z`
Tolerance: `0.050` median slowdown over selected row.

- recommendations: `4`
- aligned: `1`
- within tolerance: `2`
- drift: `0`
- noisy drift: `0`
- unconfirmed mode drift: `1`
- missing evidence: `0`

| Range | Source | Baseline | Selected Mode | Current Mode | Selected Segment | Current Default | Threads | Selected Median ms | Samples | Default Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `dynamic` | `dynamic` | 131072 | 262144 | 2/2 -> 2/2 | 0.070 | unknown | 1.017x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `wheel30-mark` | `dynamic` | 65536 | 65536 | 8/8 -> 8/8 | 2.911 | noisy<br>C n=15, max/med=1.60<br>B n=15, max/med=7.34<br>mode unconfirmed 0/2 | 1.054x | `unconfirmed_mode_drift` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `dynamic` | `dynamic` | 196608 | 196608 | 8/8 -> 8/8 | 6.797 | noisy<br>C n=15, max/med=2.34<br>B n=15, max/med=1.52<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_mode_sweep` | `external_primesieve_count` | `segmented` | `balanced` | 3145728 | 4194304 | 4/8 -> 3/8 | 6.188 | stable<br>C n=10, max/med=1.16<br>B n=15, max/med=1.31<br>mode confirmed 2/2 | 0.977x | `within_tolerance` |
