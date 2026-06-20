# Prime Engine Default Calibration

Generated: `2026-06-20T00:13:54Z`
Tolerance: `0.050` median slowdown over selected row.
Minimum actionable median delta: `0.001000` ms.

- recommendations: `4`
- aligned: `2`
- within tolerance: `1`
- drift: `0`
- noisy drift: `0`
- unconfirmed mode drift: `1`
- missing evidence: `0`

| Range | Source | Baseline | Selected Mode | Current Mode | Selected Segment | Current Default | Threads | Selected Median ms | Samples | Default Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1/1 -> 1/1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, max/med=1.29<br>B n=15, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | noisy<br>C n=5, max/med=1.33<br>B n=15, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count` | `presieve13` | `presieve17` | 4194304 | 1507328 | 3/8 -> 7/8 | 4.843 | noisy<br>C n=15, max/med=1.32<br>B n=15, max/med=1.97<br>mode unconfirmed 1/2 | 1.060x | `unconfirmed_mode_drift` |
