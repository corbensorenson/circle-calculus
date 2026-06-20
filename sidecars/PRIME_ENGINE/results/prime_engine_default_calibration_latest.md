# Prime Engine Default Calibration

Generated: `2026-06-20T08:59:46Z`
Tolerance: `0.050` median slowdown over selected row.
Minimum actionable median delta: `0.001000` ms.

- recommendations: `7`
- aligned: `6`
- within tolerance: `1`
- drift: `0`
- noisy drift: `0`
- unconfirmed mode drift: `0`
- missing evidence: `0`

| Range | Source | Baseline | Selected Mode | Current Mode | Selected Segment | Current Default | Threads | Selected Median ms | Samples | Default Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1/1 -> 1/1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=15, robust/med=2.28, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=15, robust/med=1.25, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1310720 | 1310720 | 8/8 -> 8/8 | 1.768 | noisy<br>effective stable<br>C n=27, robust/med=2.17, max/med=2.68<br>B n=27, robust/med=1.71, max/med=2.09<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [1500000000000, 1500010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1310720 | 1310720 | 8/8 -> 8/8 | 1.830 | noisy<br>effective stable<br>C n=27, robust/med=1.56, max/med=2.26<br>B n=27, robust/med=1.06, max/med=1.31<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [10000000000000, 10000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1310720 | 1310720 | 8/8 -> 8/8 | 2.015 | noisy<br>effective stable<br>C n=27, robust/med=2.56, max/med=2.83<br>B n=27, robust/med=1.67, max/med=1.70<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [100000000000000, 100000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8/8 -> 8/8 | 2.099 | noisy<br>effective stable<br>C n=27, robust/med=1.54, max/med=1.76<br>B n=27, robust/med=1.16, max/med=1.20<br>mode confirmed 3/2 | 1.000x | `aligned` |
