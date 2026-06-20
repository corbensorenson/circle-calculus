# Prime Engine Default Calibration

Generated: `2026-06-20T07:09:54Z`
Tolerance: `0.050` median slowdown over selected row.
Minimum actionable median delta: `0.001000` ms.

- recommendations: `8`
- aligned: `6`
- within tolerance: `1`
- drift: `0`
- noisy drift: `0`
- unconfirmed mode drift: `1`
- missing evidence: `0`

| Range | Source | Baseline | Selected Mode | Current Mode | Selected Segment | Current Default | Threads | Selected Median ms | Samples | Default Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1/1 -> 1/1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=15, robust/med=2.28, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=15, robust/med=1.25, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8/8 -> 8/8 | 1.763 | stable<br>C n=27, robust/med=1.38, max/med=1.56<br>B n=27, robust/med=1.49, max/med=1.51<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_tight` | `external_primesieve_count` | `presieve13` | `segmented` | 4194304 | 1310720 | 3/8 -> 8/8 | 4.957 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.02, max/med=1.89<br>mode missing 0/2 | 1.098x | `unconfirmed_mode_drift` |
| [1500000000000, 1500010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8/8 -> 8/8 | 1.805 | noisy<br>effective stable<br>C n=27, robust/med=2.36, max/med=2.49<br>B n=27, robust/med=1.47, max/med=1.50<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [10000000000000, 10000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8/8 -> 8/8 | 1.900 | noisy<br>effective stable<br>C n=27, robust/med=1.65, max/med=2.02<br>B n=27, robust/med=1.57, max/med=1.79<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [100000000000000, 100000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8/8 -> 8/8 | 2.032 | noisy<br>effective stable<br>C n=27, robust/med=1.85, max/med=1.85<br>B n=27, robust/med=1.20, max/med=1.24<br>mode confirmed 3/2 | 1.000x | `aligned` |
