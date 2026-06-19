# Prime Engine Report

Generated: `2026-06-19T20:34:12Z`

## External Correctness

Status: `passed`; checks: `202`; failures: `0`.
Count checks: `174`; enumeration checks: `22`; next-prime checks: `6`.
Required external controls: `primecount`, `primesieve`.
Circle count modes checked: `segmented`, `balanced`, `dynamic`, `presieve13`, `wheel30-mark`, `hybrid-wheel30-mark`.
Requested Circle segment sizes: `0`, `65536`, `196608`, `4194304`.
Requested threads: Circle `8`, external `8`.
Count ranges checked: `8`.
Enumeration ranges checked: `6`.
Largest checked high: `18446744073709551615`.

## External Controls

- `primesieve`: Circle faster on 0/3 rows by best time; median faster on 0/3 rows.
- `primecount`: Circle faster on 2/3 rows by best time; median faster on 2/3 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- requested threads: Circle `8`, external `8` (`0` means tool default/all cores).
- Circle count modes: `default`.
- required external controls: `primecount`, `primesieve`.
- timing policy: interleaved round-robin samples.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv`.

| Range | Circle Row | Baseline | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | --- | --- |
| [0, 10000000) | `circle_prime_parallel_default_count_8t`<br>mode: `dynamic` (threads: 8) | `external_primesieve_count` (threads: 8) | 0.903 | 0.885 | noisy<br>C n=7, max/med=1.07<br>B n=7, max/med=2.00 | baseline_faster |
| [0, 10000000) | `circle_prime_parallel_default_count_8t`<br>mode: `dynamic` (threads: 8) | `external_primecount_pi_diff` (threads: 8) | 1.311 | 1.324 | noisy<br>C n=7, max/med=1.07<br>B n=7, max/med=1.97 | circle_faster |
| [0, 100000000) | `circle_prime_parallel_default_count_8t`<br>mode: `dynamic` (threads: 8) | `external_primesieve_count` (threads: 8) | 0.668 | 0.644 | stable<br>C n=7, max/med=1.05<br>B n=7, max/med=1.08 | baseline_faster |
| [0, 100000000) | `circle_prime_parallel_default_count_8t`<br>mode: `dynamic` (threads: 8) | `external_primecount_pi_diff` (threads: 8) | 0.669 | 0.640 | stable<br>C n=7, max/med=1.05<br>B n=7, max/med=1.19 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_3t`<br>mode: `balanced` (threads: 3/8) | `external_primesieve_count` (threads: 8) | 0.881 | 0.884 | stable<br>C n=7, max/med=1.10<br>B n=7, max/med=1.04 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_3t`<br>mode: `balanced` (threads: 3/8) | `external_primecount_pi_diff` (threads: 8) | 3.901 | 6.631 | stable<br>C n=7, max/med=1.10<br>B n=7, max/med=1.40 | circle_faster |

## External Next-Prime Search

- `primesieve --nth-prime`: Circle faster on 3/5 rows by best time; median faster on 5/5 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- requested threads: Circle `1`, external `8` (`0` means tool default/all cores).
- next-prime starts: `90`, `1000000`, `4294967000`, `1000000000000`, `18446744073709551500`.
- repeated searches per sample: `4`.
- required external controls: `primesieve`.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_next_samples_latest.csv`.

| Start | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 90 | 97 | 2 | 4 | 8.883 | 8.600 | 0.968 | 1.008 | noisy<br>C n=5, max/med=1.10<br>B n=5, max/med=1.86 | circle_faster |
| 1000000 | 1000003 | 2 | 4 | 8.744 | 8.692 | 0.994 | 1.001 | stable<br>C n=5, max/med=1.03<br>B n=5, max/med=1.17 | circle_faster |
| 4294967000 | 4294967029 | 8 | 4 | 8.431 | 9.017 | 1.069 | 1.064 | stable<br>C n=5, max/med=1.04<br>B n=5, max/med=1.05 | circle_faster |
| 1000000000000 | 1000000000039 | 12 | 4 | 8.371 | 9.934 | 1.187 | 1.189 | stable<br>C n=5, max/med=1.03<br>B n=5, max/med=1.16 | circle_faster |
| 18446744073709551500 | 18446744073709551521 | 5 | 4 | 8.657 | 3542.014 | 409.172 | 393.320 | stable<br>C n=5, max/med=1.15<br>B n=5, max/med=1.03 | circle_faster |

## External Count Mode Sweep

Requested Circle segment sizes: `0`.
Circle count modes: `segmented`, `balanced`, `dynamic`, `presieve13`, `wheel30-mark`, `hybrid-wheel30-mark`.
Rounds per row: `5`.

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 65536 | 8 | 2.895 | 2.911 | 1.335 | 1.514 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.68 | circle_faster |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 65536 | 8 | 2.895 | 2.911 | 0.866 | 0.896 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.99 | baseline_faster |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 5.802 | 6.797 | 0.689 | 0.647 | noisy<br>C n=5, max/med=2.86<br>B n=5, max/med=1.23 | baseline_faster |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 5.802 | 6.797 | 0.742 | 0.648 | noisy<br>C n=5, max/med=2.86<br>B n=5, max/med=1.38 | baseline_faster |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_3t`<br>mode: `balanced` | 4194304 | 3/8 | 6.036 | 6.045 | 4.675 | 8.315 | stable<br>C n=5, max/med=1.07<br>B n=5, max/med=1.07 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_3t`<br>mode: `balanced` | 4194304 | 3/8 | 6.036 | 6.045 | 0.784 | 0.860 | stable<br>C n=5, max/med=1.07<br>B n=5, max/med=1.29 | baseline_faster |

Count mode candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 65536 | 8 | 2.895 | 2.911 | 1.335 | 1.514 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.68 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 65536 | 8 | 2.859 | 2.912 | 1.352 | 1.513 | noisy<br>C n=5, max/med=1.29<br>B n=5, max/med=1.68 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 65536 | 8 | 2.803 | 3.059 | 1.379 | 1.440 | noisy<br>C n=5, max/med=1.29<br>B n=5, max/med=1.68 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 65536 | 8 | 2.773 | 3.069 | 1.394 | 1.436 | noisy<br>C n=5, max/med=1.10<br>B n=5, max/med=1.68 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_presieve13_count`<br>mode: `presieve13` | 65536 | 1/8 | 3.121 | 3.159 | 1.238 | 1.395 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=1.68 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 65536 | 8 | 2.895 | 2.911 | 0.866 | 0.896 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.99 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 65536 | 8 | 2.859 | 2.912 | 0.877 | 0.896 | noisy<br>C n=5, max/med=1.29<br>B n=5, max/med=1.99 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 65536 | 8 | 2.803 | 3.059 | 0.895 | 0.853 | noisy<br>C n=5, max/med=1.29<br>B n=5, max/med=1.99 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 65536 | 8 | 2.773 | 3.069 | 0.904 | 0.850 | noisy<br>C n=5, max/med=1.10<br>B n=5, max/med=1.99 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_presieve13_count`<br>mode: `presieve13` | 65536 | 1/8 | 3.121 | 3.159 | 0.804 | 0.826 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=1.99 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 5.802 | 6.797 | 0.689 | 0.647 | noisy<br>C n=5, max/med=2.86<br>B n=5, max/med=1.23 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 196608 | 8 | 6.475 | 6.906 | 0.617 | 0.636 | stable<br>C n=5, max/med=1.19<br>B n=5, max/med=1.23 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 196608 | 8 | 6.262 | 7.236 | 0.638 | 0.607 | stable<br>C n=5, max/med=1.47<br>B n=5, max/med=1.23 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 6.764 | 7.283 | 0.591 | 0.603 | noisy<br>C n=5, max/med=2.32<br>B n=5, max/med=1.23 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 196608 | 8 | 7.744 | 8.437 | 0.516 | 0.521 | stable<br>C n=5, max/med=1.29<br>B n=5, max/med=1.23 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 5.802 | 6.797 | 0.742 | 0.648 | noisy<br>C n=5, max/med=2.86<br>B n=5, max/med=1.38 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 196608 | 8 | 6.475 | 6.906 | 0.665 | 0.638 | stable<br>C n=5, max/med=1.19<br>B n=5, max/med=1.38 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 196608 | 8 | 6.262 | 7.236 | 0.688 | 0.609 | stable<br>C n=5, max/med=1.47<br>B n=5, max/med=1.38 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 6.764 | 7.283 | 0.637 | 0.605 | noisy<br>C n=5, max/med=2.32<br>B n=5, max/med=1.38 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_wheel30_mark_count_8t`<br>mode: `wheel30-mark` | 196608 | 8 | 7.744 | 8.437 | 0.556 | 0.522 | stable<br>C n=5, max/med=1.29<br>B n=5, max/med=1.38 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_3t`<br>mode: `balanced` | 4194304 | 3/8 | 6.036 | 6.045 | 4.675 | 8.315 | stable<br>C n=5, max/med=1.07<br>B n=5, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_3t`<br>mode: `segmented` | 4194304 | 3/8 | 5.492 | 6.325 | 5.137 | 7.947 | stable<br>C n=5, max/med=1.13<br>B n=5, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_3t`<br>mode: `dynamic` | 4194304 | 3/8 | 5.810 | 6.410 | 4.856 | 7.842 | stable<br>C n=5, max/med=1.13<br>B n=5, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_wheel30_mark_count_3t`<br>mode: `wheel30-mark` | 4194304 | 3/8 | 6.540 | 7.300 | 4.314 | 6.887 | stable<br>C n=5, max/med=1.33<br>B n=5, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_hybrid_wheel30_mark_count_3t`<br>mode: `hybrid-wheel30-mark` | 4194304 | 3/8 | 7.230 | 8.243 | 3.903 | 6.099 | noisy<br>C n=5, max/med=1.68<br>B n=5, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_3t`<br>mode: `balanced` | 4194304 | 3/8 | 6.036 | 6.045 | 0.784 | 0.860 | stable<br>C n=5, max/med=1.07<br>B n=5, max/med=1.29 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_3t`<br>mode: `segmented` | 4194304 | 3/8 | 5.492 | 6.325 | 0.862 | 0.822 | stable<br>C n=5, max/med=1.13<br>B n=5, max/med=1.29 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_3t`<br>mode: `dynamic` | 4194304 | 3/8 | 5.810 | 6.410 | 0.814 | 0.811 | stable<br>C n=5, max/med=1.13<br>B n=5, max/med=1.29 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_wheel30_mark_count_3t`<br>mode: `wheel30-mark` | 4194304 | 3/8 | 6.540 | 7.300 | 0.724 | 0.713 | stable<br>C n=5, max/med=1.33<br>B n=5, max/med=1.29 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_3t`<br>mode: `hybrid-wheel30-mark` | 4194304 | 3/8 | 7.230 | 8.243 | 0.654 | 0.631 | noisy<br>C n=5, max/med=1.68<br>B n=5, max/med=1.29 |

## External Mode Confirmation

Observed groups: `3`; confirmed: `1`; unconfirmed: `2`.
Minimum confirmations: `2`; requires stable samples: `True`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primesieve_count` | `dynamic` | 196608 | 8 | 0/2 | 0/2 | 3.104 | `unconfirmed` |
| [0, 100000000) | `external_primesieve_count` | `dynamic` | 98304 | 8 | 0/2 | 0/2 | 6.974 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `segmented` | 3145728 | 4/8 | 2/2 | 2/2 | 6.188, 6.214 | `confirmed` |

## External Throughput

Requested Circle segment sizes: `131072`, `196608`, `262144`, `524288`.
Rounds per row: `5`.

| Range | Baseline | Best Circle Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | 262144 | 8 | 42.285 | 45.081 | 0.106 | 0.109 | noisy<br>C n=5, max/med=1.22<br>B n=5, max/med=2.14 | baseline_faster |
| [0, 1000000000) | `external_primesieve_count` | 262144 | 8 | 42.285 | 45.081 | 0.428 | 0.452 | stable<br>C n=5, max/med=1.22<br>B n=5, max/med=1.16 | baseline_faster |

Throughput segment candidate spread:

| Range | Baseline | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | 262144 | 8 | 42.285 | 45.081 | 0.106 | 0.109 | noisy<br>C n=5, max/med=1.22<br>B n=5, max/med=2.14 |
| [0, 1000000000) | `external_primecount_pi_diff` | 131072 | 8 | 44.907 | 46.883 | 0.100 | 0.105 | noisy<br>C n=5, max/med=1.21<br>B n=5, max/med=2.14 |
| [0, 1000000000) | `external_primecount_pi_diff` | 196608 | 8 | 43.284 | 48.988 | 0.104 | 0.100 | noisy<br>C n=5, max/med=1.39<br>B n=5, max/med=2.14 |
| [0, 1000000000) | `external_primecount_pi_diff` | 524288 | 8 | 74.944 | 76.938 | 0.060 | 0.064 | noisy<br>C n=5, max/med=1.06<br>B n=5, max/med=2.14 |
| [0, 1000000000) | `external_primesieve_count` | 262144 | 8 | 42.285 | 45.081 | 0.428 | 0.452 | stable<br>C n=5, max/med=1.22<br>B n=5, max/med=1.16 |
| [0, 1000000000) | `external_primesieve_count` | 131072 | 8 | 44.907 | 46.883 | 0.403 | 0.435 | stable<br>C n=5, max/med=1.21<br>B n=5, max/med=1.16 |
| [0, 1000000000) | `external_primesieve_count` | 196608 | 8 | 43.284 | 48.988 | 0.418 | 0.416 | stable<br>C n=5, max/med=1.39<br>B n=5, max/med=1.16 |
| [0, 1000000000) | `external_primesieve_count` | 524288 | 8 | 74.944 | 76.938 | 0.242 | 0.265 | stable<br>C n=5, max/med=1.06<br>B n=5, max/med=1.16 |

## External Segment Sweep

Requested Circle segment sizes: `0`, `32768`, `65536`, `98304`, `131072`, `196608`, `262144`, `524288`, `1048576`, `2097152`, `3145728`, `4194304`.
Circle count modes: `segmented`.
Rounds per row: `5`.

| Range | Baseline | Best Circle Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primecount_pi_diff` | 196608 | 8 | 2.849 | 2.888 | 1.361 | 1.482 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=1.88 | circle_faster |
| [0, 10000000) | `external_primesieve_count` | 196608 | 8 | 2.849 | 2.888 | 1.015 | 1.030 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=2.43 | circle_faster |
| [0, 100000000) | `external_primecount_pi_diff` | 131072 | 8 | 6.461 | 6.744 | 0.699 | 0.724 | stable<br>C n=5, max/med=1.37<br>B n=5, max/med=1.30 | baseline_faster |
| [0, 100000000) | `external_primesieve_count` | 131072 | 8 | 6.461 | 6.744 | 0.740 | 0.740 | stable<br>C n=5, max/med=1.37<br>B n=5, max/med=1.43 | baseline_faster |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 4194304 | 3/8 | 5.185 | 5.335 | 4.199 | 5.089 | noisy<br>C n=5, max/med=1.10<br>B n=5, max/med=1.98 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 4194304 | 3/8 | 5.185 | 5.335 | 0.890 | 0.900 | stable<br>C n=5, max/med=1.10<br>B n=5, max/med=1.06 | baseline_faster |

Segment candidate spread:

| Range | Baseline | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 10000000) | `external_primecount_pi_diff` | 196608 | 8 | 2.849 | 2.888 | 1.361 | 1.482 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 98304 | 8 | 2.856 | 2.923 | 1.357 | 1.465 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 65536 | 8 | 2.871 | 3.000 | 1.350 | 1.427 | noisy<br>C n=5, max/med=1.33<br>B n=5, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 32768 | 8 | 2.898 | 3.054 | 1.337 | 1.402 | noisy<br>C n=5, max/med=1.17<br>B n=5, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 131072 | 8 | 3.038 | 3.088 | 1.276 | 1.387 | noisy<br>C n=5, max/med=1.03<br>B n=5, max/med=1.88 |
| [0, 10000000) | `external_primesieve_count` | 196608 | 8 | 2.849 | 2.888 | 1.015 | 1.030 | noisy<br>C n=5, max/med=1.07<br>B n=5, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 98304 | 8 | 2.856 | 2.923 | 1.012 | 1.018 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 65536 | 8 | 2.871 | 3.000 | 1.006 | 0.992 | noisy<br>C n=5, max/med=1.33<br>B n=5, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 32768 | 8 | 2.898 | 3.054 | 0.997 | 0.974 | noisy<br>C n=5, max/med=1.17<br>B n=5, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 131072 | 8 | 3.038 | 3.088 | 0.951 | 0.964 | noisy<br>C n=5, max/med=1.03<br>B n=5, max/med=2.43 |
| [0, 100000000) | `external_primecount_pi_diff` | 131072 | 8 | 6.461 | 6.744 | 0.699 | 0.724 | stable<br>C n=5, max/med=1.37<br>B n=5, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 98304 | 8 | 6.743 | 7.237 | 0.670 | 0.675 | stable<br>C n=5, max/med=1.18<br>B n=5, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 262144 | 8 | 7.118 | 7.500 | 0.635 | 0.651 | stable<br>C n=5, max/med=1.02<br>B n=5, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 65536 | 8 | 7.063 | 7.761 | 0.640 | 0.629 | stable<br>C n=5, max/med=1.08<br>B n=5, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 196608 | 8 | 6.758 | 8.173 | 0.669 | 0.598 | stable<br>C n=5, max/med=1.41<br>B n=5, max/med=1.30 |
| [0, 100000000) | `external_primesieve_count` | 131072 | 8 | 6.461 | 6.744 | 0.740 | 0.740 | stable<br>C n=5, max/med=1.37<br>B n=5, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 98304 | 8 | 6.743 | 7.237 | 0.709 | 0.690 | stable<br>C n=5, max/med=1.18<br>B n=5, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 262144 | 8 | 7.118 | 7.500 | 0.672 | 0.666 | stable<br>C n=5, max/med=1.02<br>B n=5, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 65536 | 8 | 7.063 | 7.761 | 0.677 | 0.643 | stable<br>C n=5, max/med=1.08<br>B n=5, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 196608 | 8 | 6.758 | 8.173 | 0.708 | 0.611 | stable<br>C n=5, max/med=1.41<br>B n=5, max/med=1.43 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 4194304 | 3/8 | 5.185 | 5.335 | 4.199 | 5.089 | noisy<br>C n=5, max/med=1.10<br>B n=5, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 2097152 | 5/8 | 5.584 | 5.690 | 3.898 | 4.772 | noisy<br>C n=5, max/med=1.09<br>B n=5, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 3145728 | 4/8 | 5.089 | 5.945 | 4.278 | 4.567 | noisy<br>C n=5, max/med=1.11<br>B n=5, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 524288 | 8 | 6.223 | 6.614 | 3.498 | 4.105 | noisy<br>C n=5, max/med=1.12<br>B n=5, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 1048576 | 8 | 6.654 | 6.747 | 3.272 | 4.024 | noisy<br>C n=5, max/med=1.03<br>B n=5, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 4194304 | 3/8 | 5.185 | 5.335 | 0.890 | 0.900 | stable<br>C n=5, max/med=1.10<br>B n=5, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 2097152 | 5/8 | 5.584 | 5.690 | 0.826 | 0.844 | stable<br>C n=5, max/med=1.09<br>B n=5, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 3145728 | 4/8 | 5.089 | 5.945 | 0.907 | 0.808 | stable<br>C n=5, max/med=1.11<br>B n=5, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 524288 | 8 | 6.223 | 6.614 | 0.741 | 0.726 | stable<br>C n=5, max/med=1.12<br>B n=5, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 1048576 | 8 | 6.654 | 6.747 | 0.693 | 0.711 | stable<br>C n=5, max/med=1.03<br>B n=5, max/med=1.06 |

## Default Calibration

Recommendations: `4`; aligned: `1`; within tolerance: `2`; drift: `0`; noisy drift: `0`; unconfirmed mode drift: `1`; missing evidence: `0`.
Tolerance: `0.050` median slowdown.

| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `dynamic` | `dynamic` | 131072 | 262144 | 2 -> 2 | 0.070 | unknown | 1.017x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `wheel30-mark` | `dynamic` | 65536 | 65536 | 8 -> 8 | 2.911 | noisy<br>C n=15, max/med=1.60<br>B n=15, max/med=7.34<br>mode unconfirmed 0/2 | 1.054x | `unconfirmed_mode_drift` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `dynamic` | `dynamic` | 196608 | 196608 | 8 -> 8 | 6.797 | noisy<br>C n=15, max/med=2.34<br>B n=15, max/med=1.52<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_mode_sweep` | `external_primesieve_count` | `segmented` | `balanced` | 3145728 | 4194304 | 4/8 -> 3/8 | 6.188 | stable<br>C n=10, max/med=1.16<br>B n=15, max/med=1.31<br>mode confirmed 2/2 | 0.977x | `within_tolerance` |

## Release Benchmark

| Scope | Workload | Row | Segment | Best ms | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| high_offset | 10000000 | `parallel_high_offset_segmented_range_count_8t` | 4194304 | 2.183 | 361726 |
| prefix | 1000000000 | `parallel_segmented_range_count_8t` | 131072 | 35.001 | 50847534 |
| prefix | 100000000 | `parallel_segmented_range_count_8t` | 131072 | 3.592 | 5761455 |
| prefix | 10000000 | `parallel_segmented_range_count_8t` | 131072 | 0.381 | 664579 |
| prefix | 1000000 | `segmented_range_count` | 32768 | 0.078 | 78498 |

Base-prime generation rows:
- limit `10000`: 0.000ms
- limit `1000000`: 0.010ms

Cold process count rows:

| Scope | Workload | Row | Segment | Best ms | Count |
| --- | ---: | --- | ---: | ---: | ---: |
| prefix | 1000000 | `cold_process_segmented_range_count` | 262144 | 1.632 | 78498 |
| prefix | 10000000 | `cold_process_segmented_range_count` | 262144 | 2.872 | 664579 |
| prefix | 10000000 | `cold_process_parallel_segmented_range_count_8t` | 65536 | 2.209 | 664579 |
| prefix | 10000000 | `cold_cli_parallel_default_range_count_8t` | 65536 | 1.957 | 664579 |
| prefix | 100000000 | `cold_process_parallel_segmented_range_count_8t` | 196608 | 5.009 | 5761455 |
| prefix | 100000000 | `cold_cli_parallel_default_range_count_8t` | 196608 | 5.120 | 5761455 |
| high_offset | 10000000 | `cold_process_parallel_high_offset_segmented_range_count_8t` | 4194304 | 4.225 | 361726 |
| high_offset | 10000000 | `cold_cli_parallel_high_offset_default_range_count_8t` | 4194304 | 4.351 | 361726 |

High-offset benchmark rows:

| Workload | Row | Segment | Best ms | Count |
| ---: | --- | ---: | ---: | ---: |
| 10000000 | `high_offset_segmented_range_count` | 4194304 | 5.588 | 361726 |
| 10000000 | `parallel_high_offset_segmented_range_count_8t` | 4194304 | 2.183 | 361726 |
| 10000000 | `parallel_high_offset_default_range_count_8t` | 4194304 | 2.204 | 361726 |
| 10000000 | `parallel_high_offset_balanced_segmented_range_count_8t` | 4194304 | 2.193 | 361726 |
| 10000000 | `high_offset_bitpacked_range_count` | 4194304 | 7.476 | 361726 |
| 10000000 | `high_offset_tracked_byte_range_count` | 4194304 | 15.910 | 361726 |
| 10000000 | `high_offset_wheel30_range_count` | 4194304 | 47.906 | 361726 |
| 10000000 | `high_offset_wheel30_mark_range_count` | 4194304 | 5.587 | 361726 |
| 10000000 | `parallel_high_offset_wheel30_mark_range_count_8t` | 4194304 | 3.250 | 361726 |
| 10000000 | `high_offset_hybrid_wheel30_mark_range_count` | 4194304 | 6.961 | 361726 |
| 10000000 | `parallel_high_offset_hybrid_wheel30_mark_range_count_8t` | 4194304 | 4.537 | 361726 |
| 100000 | `high_offset_u64_scalar_fallback_range_count` | 64 | 43.567 | 2139 |
| 100000 | `high_offset_u64_scalar_naive_control_count` | 0 | 43.310 | 2139 |
| 10000000 | `cold_process_parallel_high_offset_segmented_range_count_8t` | 4194304 | 4.225 | 361726 |
| 10000000 | `cold_cli_parallel_high_offset_default_range_count_8t` | 4194304 | 4.351 | 361726 |

Materialized generation rows:

| Workload | Row | Segment | Best ms | Count |
| ---: | --- | ---: | ---: | ---: |
| 1000000 | `enumerate_range_primes` | 262144 | 0.789 | 78498 |
| 10000000 | `enumerate_range_primes` | 262144 | 7.326 | 664579 |

Next-prime search rows:

| Start | Row | Searches | Best ms | Prime |
| ---: | --- | ---: | ---: | ---: |
| 90 | `next_prime_search` | 4096 | 0.645 | 97 |
| 1000000 | `next_prime_search` | 4096 | 4.165 | 1000003 |
| 4294967000 | `next_prime_search` | 4096 | 8.992 | 4294967029 |
| 1000000000000 | `next_prime_search` | 4096 | 23.502 | 1000000000039 |
| 18446744073709551500 | `next_prime_search` | 4096 | 64.862 | 18446744073709551521 |

Primary count candidate spread:

| Scope | Workload | Row | Segment | Best ms | Slowdown vs fastest |
| --- | ---: | --- | ---: | ---: | ---: |
| high_offset | 10000000 | `parallel_high_offset_segmented_range_count_8t` | 4194304 | 2.183 | 1.00x |
| high_offset | 10000000 | `parallel_high_offset_default_range_count_8t` | 4194304 | 2.204 | 1.01x |
| high_offset | 10000000 | `high_offset_segmented_range_count` | 4194304 | 5.588 | 2.56x |
| prefix | 1000000000 | `parallel_segmented_range_count_8t` | 131072 | 35.001 | 1.00x |
| prefix | 1000000000 | `parallel_segmented_range_count_8t` | 262144 | 37.075 | 1.06x |
| prefix | 1000000000 | `parallel_segmented_range_count_8t` | 196608 | 40.164 | 1.15x |
| prefix | 1000000000 | `parallel_segmented_range_count_4t` | 262144 | 48.789 | 1.39x |
| prefix | 1000000000 | `parallel_segmented_range_count_4t` | 196608 | 51.123 | 1.46x |
| prefix | 100000000 | `parallel_segmented_range_count_8t` | 131072 | 3.592 | 1.00x |
| prefix | 100000000 | `parallel_segmented_range_count_4t` | 131072 | 3.930 | 1.09x |
| prefix | 100000000 | `parallel_segmented_range_count_4t` | 196608 | 3.986 | 1.11x |
| prefix | 100000000 | `parallel_segmented_range_count_8t` | 196608 | 4.003 | 1.11x |
| prefix | 100000000 | `parallel_segmented_range_count_8t` | 262144 | 4.022 | 1.12x |
| prefix | 10000000 | `parallel_segmented_range_count_8t` | 131072 | 0.381 | 1.00x |
| prefix | 10000000 | `parallel_segmented_range_count_8t` | 65536 | 0.390 | 1.02x |
| prefix | 10000000 | `parallel_segmented_range_count_8t` | 196608 | 0.416 | 1.09x |
| prefix | 10000000 | `parallel_segmented_range_count_8t` | 262144 | 0.435 | 1.14x |
| prefix | 10000000 | `parallel_segmented_range_count_4t` | 131072 | 0.472 | 1.24x |
| prefix | 1000000 | `segmented_range_count` | 32768 | 0.078 | 1.00x |
| prefix | 1000000 | `segmented_range_count` | 196608 | 0.079 | 1.01x |
| prefix | 1000000 | `segmented_range_count` | 262144 | 0.079 | 1.01x |
| prefix | 1000000 | `segmented_range_count` | 1048576 | 0.202 | 2.59x |

Experimental count lanes:

| Workload | Row | Segment | Best ms | Slowdown vs primary |
| ---: | --- | ---: | ---: | ---: |
| 1000000 | `bitpacked_range_count` | 32768 | 0.332 | 4.26x |
| 1000000 | `bitpacked_range_count` | 262144 | 0.333 | 4.27x |
| 1000000 | `tracked_byte_range_count` | 32768 | 0.595 | 7.63x |
| 1000000 | `tracked_byte_range_count` | 262144 | 0.428 | 5.49x |
| 1000000 | `wheel30_mark_range_count` | 32768 | 0.102 | 1.31x |
| 1000000 | `wheel30_mark_range_count` | 262144 | 0.089 | 1.14x |
| 1000000 | `wheel30_range_count` | 32768 | 2.734 | 35.05x |
| 1000000 | `wheel30_range_count` | 262144 | 2.728 | 34.97x |
| 10000000 | `bitpacked_range_count` | 131072 | 3.837 | 10.07x |
| 10000000 | `bitpacked_range_count` | 262144 | 3.856 | 10.12x |
| 10000000 | `high_offset_bitpacked_range_count` | 4194304 | 7.476 | 3.42x |
| 10000000 | `high_offset_hybrid_wheel30_mark_range_count` | 4194304 | 6.961 | 3.19x |
| 10000000 | `high_offset_tracked_byte_range_count` | 4194304 | 15.910 | 7.29x |
| 10000000 | `high_offset_wheel30_mark_range_count` | 4194304 | 5.587 | 2.56x |
| 10000000 | `high_offset_wheel30_range_count` | 4194304 | 47.906 | 21.95x |
| 10000000 | `hybrid_wheel30_mark_range_count` | 131072 | 0.943 | 2.48x |
| 10000000 | `hybrid_wheel30_mark_range_count` | 262144 | 1.020 | 2.68x |
| 10000000 | `parallel_high_offset_balanced_segmented_range_count_8t` | 4194304 | 2.193 | 1.00x |
| 10000000 | `parallel_high_offset_hybrid_wheel30_mark_range_count_8t` | 4194304 | 4.537 | 2.08x |
| 10000000 | `parallel_high_offset_wheel30_mark_range_count_8t` | 4194304 | 3.250 | 1.49x |
| 10000000 | `presieve13_range_count` | 131072 | 0.976 | 2.56x |
| 10000000 | `presieve13_range_count` | 262144 | 1.020 | 2.68x |
| 10000000 | `tracked_byte_range_count` | 131072 | 8.559 | 22.46x |
| 10000000 | `tracked_byte_range_count` | 262144 | 7.719 | 20.26x |
| 10000000 | `wheel30_mark_range_count` | 131072 | 1.299 | 3.41x |
| 10000000 | `wheel30_mark_range_count` | 262144 | 1.186 | 3.11x |
| 10000000 | `wheel30_range_count` | 131072 | 31.624 | 83.00x |
| 10000000 | `wheel30_range_count` | 262144 | 31.805 | 83.48x |
| 100000000 | `bitpacked_range_count` | 262144 | 43.386 | 12.08x |
| 100000000 | `hybrid_wheel30_mark_range_count` | 262144 | 11.642 | 3.24x |
| 100000000 | `parallel_balanced_segmented_range_count_8t` | 131072 | 2.832 | 0.79x |
| 100000000 | `parallel_balanced_segmented_range_count_8t` | 196608 | 3.567 | 0.99x |
| 100000000 | `parallel_balanced_segmented_range_count_8t` | 262144 | 3.374 | 0.94x |
| 100000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 131072 | 3.397 | 0.95x |
| 100000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 196608 | 3.781 | 1.05x |
| 100000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 262144 | 3.583 | 1.00x |
| 100000000 | `parallel_wheel30_mark_range_count_8t` | 131072 | 4.741 | 1.32x |
| 100000000 | `parallel_wheel30_mark_range_count_8t` | 196608 | 4.910 | 1.37x |
| 100000000 | `parallel_wheel30_mark_range_count_8t` | 262144 | 4.471 | 1.24x |
| 100000000 | `presieve13_range_count` | 131072 | 11.971 | 3.33x |
| 100000000 | `presieve13_range_count` | 262144 | 11.860 | 3.30x |
| 100000000 | `tracked_byte_range_count` | 262144 | 104.890 | 29.20x |
| 100000000 | `wheel30_mark_range_count` | 262144 | 15.540 | 4.33x |
| 100000000 | `wheel30_range_count` | 262144 | 354.303 | 98.64x |
| 1000000000 | `hybrid_wheel30_mark_range_count` | 262144 | 155.027 | 4.43x |
| 1000000000 | `parallel_balanced_segmented_range_count_8t` | 131072 | 42.285 | 1.21x |
| 1000000000 | `parallel_balanced_segmented_range_count_8t` | 196608 | 41.231 | 1.18x |
| 1000000000 | `parallel_balanced_segmented_range_count_8t` | 262144 | 35.810 | 1.02x |
| 1000000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 131072 | 47.031 | 1.34x |
| 1000000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 196608 | 41.040 | 1.17x |
| 1000000000 | `parallel_hybrid_wheel30_mark_range_count_8t` | 262144 | 40.195 | 1.15x |
| 1000000000 | `parallel_wheel30_mark_range_count_8t` | 131072 | 60.028 | 1.72x |
| 1000000000 | `parallel_wheel30_mark_range_count_8t` | 196608 | 58.662 | 1.68x |
| 1000000000 | `parallel_wheel30_mark_range_count_8t` | 262144 | 49.558 | 1.42x |
| 1000000000 | `presieve13_range_count` | 196608 | 151.832 | 4.34x |

## Tuning

Samples: `880`; rounds: `9`; elapsed seconds: `44.109362875`.

| Range | Mode | Segment | Threads | Best ms | Median ms | Count |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [0, 1000000) | `dynamic` | 131072 | 2/2 | 0.067 | 0.070 | 78498 |
| [0, 10000000) | `dynamic` | 98304 | 8/8 | 0.307 | 0.314 | 664579 |
| [0, 100000000) | `dynamic` | 98304 | 8/8 | 2.621 | 2.852 | 5761455 |
| [1000000000000, 1000010000000) | `balanced` | 3145728 | 4/4 | 1.764 | 1.925 | 361726 |

Default alignment uses current calibration defaults when available; `stale artifact` means the tuning JSON stored an older default.

Default alignment:

| Range | Tuned mode | Default mode | Tuned segment | Default segment | Tuned threads | Default threads | Default source | Median ms | Aligned |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `dynamic` | `dynamic` | 131072 | 262144 | 2/2 | 2/2 | `current_calibration` | 0.070 | no |
| [0, 10000000) | `dynamic` | `dynamic` | 98304 | 65536 | 8/8 | 8/8 | `current_calibration` | 0.314 | no |
| [0, 100000000) | `dynamic` | `dynamic` | 98304 | 196608 | 8/8 | 8/8 | `current_calibration` | 2.852 | no |
| [1000000000000, 1000010000000) | `balanced` | `balanced` | 3145728 | 4194304 | 4/4 | 3/4 | `tuning_artifact` | 1.925 | no |
