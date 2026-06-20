# Prime Engine Report

Generated: `2026-06-20T07:13:01Z`

## External Correctness

Status: `passed`; checks: `824`; failures: `0`.
Count checks: `386`; count-server checks: `386`; enumeration checks: `46`; next-prime checks: `6`.
Required external controls: `primecount`, `primesieve`.
Circle count modes checked: `segmented`, `balanced`, `dynamic`, `prefix-pi`, `presieve13`, `presieve17`, `wheel30-mark`, `hybrid-wheel30-mark`.
Requested Circle segment sizes: `0`, `65536`, `196608`, `1310720`, `1441792`, `1507328`, `2621440`, `4194304`.
Requested threads: Circle `8`, external `8`.
Count ranges checked: `8`.
Enumeration ranges checked: `6`.
Largest checked high: `18446744073709551615`.

## External Controls

- `primesieve` cold CLI: Circle faster on 2/3 rows by best time; median faster on 1/3 rows.
- `primesieve` server: Circle faster on 3/3 rows by best time; median faster on 3/3 rows.
- `libprimesieve count server` external server: Circle faster on 3/6 rows by best time; median faster on 2/6 rows.
- `primecount` cold CLI: Circle faster on 3/3 rows by best time; median faster on 3/3 rows.
- `primecount` server: Circle faster on 3/3 rows by best time; median faster on 3/3 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- `primesieve_count_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server`); method `primesieve_count_primes(LOW, HIGH-1)`.
- requested threads: Circle `8`, external `8` (`0` means tool default/all cores).
- Circle count modes: `default`.
- required external controls: `primecount`, `primesieve`.
- timing policy: interleaved round-robin samples.
- warmup: `2` unrecorded interleaved pass(es).
- repeated count requests per timed sample: `20` (reported timings are per-request averages).
- Circle server rows: persistent `count-server` requests included.
- libprimesieve count-server rows included.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv`.

| Range | Circle Row | Baseline | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | --- | --- |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1.153 | 0.969 | stable<br>C n=7, robust/med=1.41, max/med=1.77<br>B n=7, robust/med=1.19, max/med=1.32 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 55.605 | 54.993 | stable<br>C n=7, robust/med=1.02, max/med=1.36<br>B n=7, robust/med=1.19, max/med=1.32 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.649 | 1.385 | stable<br>C n=7, robust/med=1.41, max/med=1.77<br>B n=7, robust/med=1.17, max/med=1.32 | circle_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 79.486 | 78.565 | stable<br>C n=7, robust/med=1.02, max/med=1.36<br>B n=7, robust/med=1.17, max/med=1.32 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.165 | 0.138 | stable<br>C n=7, robust/med=1.41, max/med=1.77<br>B n=7, robust/med=1.01, max/med=1.05 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 7.965 | 7.832 | stable<br>C n=7, robust/med=1.02, max/med=1.36<br>B n=7, robust/med=1.01, max/med=1.05 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1.518 | 1.636 | noisy<br>C n=7, robust/med=1.60, max/med=1.66<br>B n=7, robust/med=1.04, max/med=1.34 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 14.363 | 16.391 | stable<br>C n=7, robust/med=1.07, max/med=1.14<br>B n=7, robust/med=1.04, max/med=1.34 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.399 | 1.354 | noisy<br>C n=7, robust/med=1.60, max/med=1.66<br>B n=7, robust/med=1.34, max/med=2.56 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 13.238 | 13.570 | stable<br>C n=7, robust/med=1.07, max/med=1.14<br>B n=7, robust/med=1.34, max/med=2.56 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.531 | 0.597 | noisy<br>C n=7, robust/med=1.60, max/med=1.66<br>B n=7, robust/med=1.31, max/med=1.47 | baseline_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 5.028 | 5.987 | stable<br>C n=7, robust/med=1.07, max/med=1.14<br>B n=7, robust/med=1.31, max/med=1.47 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primesieve_count` (threads: 8) | 0.858 | 0.783 | stable<br>C n=7, robust/med=1.43, max/med=1.51<br>B n=7, robust/med=1.14, max/med=1.51 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primesieve_count` (threads: 8) | 2.578 | 2.097 | stable<br>C n=7, robust/med=1.26, max/med=1.61<br>B n=7, robust/med=1.14, max/med=1.51 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primecount_pi_diff` (threads: 8) | 4.453 | 5.406 | stable<br>C n=7, robust/med=1.43, max/med=1.51<br>B n=7, robust/med=1.21, max/med=1.69 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primecount_pi_diff` (threads: 8) | 13.372 | 14.486 | stable<br>C n=7, robust/med=1.26, max/med=1.61<br>B n=7, robust/med=1.21, max/med=1.69 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primesieve_count_server` (threads: 8) | 0.371 | 0.341 | stable<br>C n=7, robust/med=1.43, max/med=1.51<br>B n=7, robust/med=1.13, max/med=1.35 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` (threads: 8) | `external_primesieve_count_server` (threads: 8) | 1.114 | 0.914 | stable<br>C n=7, robust/med=1.26, max/med=1.61<br>B n=7, robust/med=1.13, max/med=1.35 | baseline_faster |

## External Next-Prime Search

- `libprimesieve generate_n_primes server` cold CLI: Circle faster on 1/5 rows by best time; median faster on 1/5 rows.
- `primesieve --nth-prime` cold CLI: Circle faster on 4/5 rows by best time; median faster on 3/5 rows.
- `primecount pi+nth-prime` cold CLI: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimesieve generate_n_primes server` server: Circle faster on 4/5 rows by best time; median faster on 4/5 rows.
- `primesieve --nth-prime` server: Circle faster on 5/5 rows by best time; median faster on 5/5 rows.
- `primecount pi+nth-prime` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- `primesieve_library_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-next-server`); method `primesieve_generate_n_primes(1, START, UINT64_PRIMES)`.
- requested threads: Circle `1`, external `8` (`0` means tool default/all cores).
- next-prime starts: `90`, `1000000`, `4294967000`, `1000000000000`, `18446744073709551500`.
- repeated searches per sample: `4`.
- Circle server rows: persistent `next-server` requests included.
- `primecount` next-prime rows included for starts at or below `1000000000000`.
- libprimesieve next-prime helper rows included for starts at or below `18446744073709551615`.
- required external controls: `primecount`, `primesieve`, `primesieve-library`.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_next_samples_latest.csv`.

| Start | Baseline | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 90 | `primesieve --nth-prime` | 97 | 2 | 4 | 7.594 | 8.221 | 1.083 | 1.037 | stable<br>C n=5, robust/med=1.01, max/med=1.38<br>B n=5, robust/med=1.08, max/med=1.73 | circle_faster |
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 4 | 7.594 | 0.025 | 0.003 | 0.008 | noisy<br>C n=5, robust/med=1.01, max/med=1.38<br>B n=5, robust/med=5.51, max/med=1195.15 | baseline_faster |
| 90 | `primecount pi+nth-prime` | 97 | 2 | 4 | 7.594 | 26.553 | 3.496 | 3.320 | stable<br>C n=5, robust/med=1.01, max/med=1.38<br>B n=5, robust/med=1.37, max/med=1.64 | circle_faster |
| 90 | `primesieve --nth-prime` | 97 | 2 | 4 | 0.042 | 8.221 | 195.342 | 153.901 | stable<br>C n=5, robust/med=1.13, max/med=1.24<br>B n=5, robust/med=1.08, max/med=1.73 | circle_faster |
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 4 | 0.042 | 0.025 | 0.582 | 1.126 | noisy<br>C n=5, robust/med=1.13, max/med=1.24<br>B n=5, robust/med=5.51, max/med=1195.15 | circle_faster |
| 90 | `primecount pi+nth-prime` | 97 | 2 | 4 | 0.042 | 26.553 | 630.956 | 492.876 | stable<br>C n=5, robust/med=1.13, max/med=1.24<br>B n=5, robust/med=1.37, max/med=1.64 | circle_faster |
| 1000000 | `primesieve --nth-prime` | 1000003 | 2 | 4 | 9.492 | 10.104 | 1.064 | 0.807 | stable<br>C n=5, robust/med=1.03, max/med=2.55<br>B n=5, robust/med=1.20, max/med=3.75 | baseline_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 4 | 9.492 | 0.060 | 0.006 | 0.005 | stable<br>C n=5, robust/med=1.03, max/med=2.55<br>B n=5, robust/med=1.01, max/med=6.73 | baseline_faster |
| 1000000 | `primecount pi+nth-prime` | 1000003 | 2 | 4 | 9.492 | 37.257 | 3.925 | 3.094 | stable<br>C n=5, robust/med=1.03, max/med=2.55<br>B n=5, robust/med=1.17, max/med=1.22 | circle_faster |
| 1000000 | `primesieve --nth-prime` | 1000003 | 2 | 4 | 0.042 | 10.104 | 242.005 | 163.812 | stable<br>C n=5, robust/med=1.00, max/med=13.26<br>B n=5, robust/med=1.20, max/med=3.75 | circle_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 4 | 0.042 | 0.060 | 1.437 | 0.962 | stable<br>C n=5, robust/med=1.00, max/med=13.26<br>B n=5, robust/med=1.01, max/med=6.73 | baseline_faster |
| 1000000 | `primecount pi+nth-prime` | 1000003 | 2 | 4 | 0.042 | 37.257 | 892.384 | 628.007 | stable<br>C n=5, robust/med=1.00, max/med=13.26<br>B n=5, robust/med=1.17, max/med=1.22 | circle_faster |
| 4294967000 | `primesieve --nth-prime` | 4294967029 | 8 | 4 | 9.118 | 8.730 | 0.957 | 0.944 | stable<br>C n=5, robust/med=1.13, max/med=1.78<br>B n=5, robust/med=1.04, max/med=1.18 | baseline_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 4 | 9.118 | 0.154 | 0.017 | 0.017 | stable<br>C n=5, robust/med=1.13, max/med=1.78<br>B n=5, robust/med=1.42, max/med=1.58 | baseline_faster |
| 4294967000 | `primecount pi+nth-prime` | 4294967029 | 8 | 4 | 9.118 | 39.560 | 4.339 | 4.014 | stable<br>C n=5, robust/med=1.13, max/med=1.78<br>B n=5, robust/med=1.02, max/med=1.44 | circle_faster |
| 4294967000 | `primesieve --nth-prime` | 4294967029 | 8 | 4 | 0.042 | 8.730 | 206.222 | 164.033 | stable<br>C n=5, robust/med=1.35, max/med=1.58<br>B n=5, robust/med=1.04, max/med=1.18 | circle_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 4 | 0.042 | 0.154 | 3.648 | 2.893 | stable<br>C n=5, robust/med=1.35, max/med=1.58<br>B n=5, robust/med=1.42, max/med=1.58 | circle_faster |
| 4294967000 | `primecount pi+nth-prime` | 4294967029 | 8 | 4 | 0.042 | 39.560 | 934.472 | 697.211 | stable<br>C n=5, robust/med=1.35, max/med=1.58<br>B n=5, robust/med=1.02, max/med=1.44 | circle_faster |
| 1000000000000 | `primesieve --nth-prime` | 1000000000039 | 12 | 4 | 8.222 | 9.487 | 1.154 | 1.296 | stable<br>C n=5, robust/med=1.01, max/med=1.14<br>B n=5, robust/med=1.03, max/med=1.19 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 4 | 8.222 | 1.158 | 0.141 | 0.139 | stable<br>C n=5, robust/med=1.01, max/med=1.14<br>B n=5, robust/med=1.03, max/med=3.77 | baseline_faster |
| 1000000000000 | `primecount pi+nth-prime` | 1000000000039 | 12 | 4 | 8.222 | 76.723 | 9.331 | 10.315 | stable<br>C n=5, robust/med=1.01, max/med=1.14<br>B n=5, robust/med=1.07, max/med=1.83 | circle_faster |
| 1000000000000 | `primesieve --nth-prime` | 1000000000039 | 12 | 4 | 0.054 | 9.487 | 177.336 | 169.890 | stable<br>C n=5, robust/med=1.12, max/med=1.14<br>B n=5, robust/med=1.03, max/med=1.19 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 4 | 0.054 | 1.158 | 21.649 | 18.227 | stable<br>C n=5, robust/med=1.12, max/med=1.14<br>B n=5, robust/med=1.03, max/med=3.77 | circle_faster |
| 1000000000000 | `primecount pi+nth-prime` | 1000000000039 | 12 | 4 | 0.054 | 76.723 | 1434.070 | 1351.662 | stable<br>C n=5, robust/med=1.12, max/med=1.14<br>B n=5, robust/med=1.07, max/med=1.83 | circle_faster |
| 18446744073709551500 | `primesieve --nth-prime` | 18446744073709551521 | 5 | 4 | 8.399 | 3629.408 | 432.128 | 343.629 | stable<br>C n=5, robust/med=1.03, max/med=1.19<br>B n=5, robust/med=1.00, max/med=1.16 | circle_faster |
| 18446744073709551500 | `libprimesieve generate_n_primes server` | 18446744073709551521 | 5 | 4 | 8.399 | 3616.402 | 430.580 | 351.440 | stable<br>C n=5, robust/med=1.03, max/med=1.19<br>B n=5, robust/med=1.02, max/med=1.08 | circle_faster |
| 18446744073709551500 | `primesieve --nth-prime` | 18446744073709551521 | 5 | 4 | 0.106 | 3629.408 | 34253.268 | 34049.484 | stable<br>C n=5, robust/med=1.12, max/med=1.22<br>B n=5, robust/med=1.00, max/med=1.16 | circle_faster |
| 18446744073709551500 | `libprimesieve generate_n_primes server` | 18446744073709551521 | 5 | 4 | 0.106 | 3616.402 | 34130.520 | 34823.468 | stable<br>C n=5, robust/med=1.12, max/med=1.22<br>B n=5, robust/med=1.02, max/med=1.08 | circle_faster |

## High-Offset Quick Scorecard

Requested Circle segment sizes: `1310720`, `1376256`, `1441792`, `1507328`, `2097152`, `3145728`, `4194304`.
Circle count modes: `segmented`, `presieve13`, `presieve17`.
Rounds per row: `13`.

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4/8 | 4.434 | 4.786 | 3.923 | 5.202 | noisy<br>C n=13, robust/med=1.13, max/med=1.69<br>B n=13, robust/med=1.73, max/med=2.66 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4/8 | 4.434 | 4.786 | 1.054 | 1.034 | noisy<br>C n=13, robust/med=1.13, max/med=1.69<br>B n=13, robust/med=1.96, max/med=2.98 | circle_faster |

High-offset quick candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4/8 | 4.434 | 4.786 | 3.923 | 5.202 | noisy<br>C n=13, robust/med=1.13, max/med=1.69<br>B n=13, robust/med=1.73, max/med=2.66 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve17_count_4t`<br>mode: `presieve17` | 3145728 | 4/8 | 4.533 | 4.842 | 3.837 | 5.142 | noisy<br>C n=13, robust/med=1.07, max/med=1.48<br>B n=13, robust/med=1.73, max/med=2.66 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 4.570 | 4.929 | 3.806 | 5.051 | noisy<br>C n=13, robust/med=1.12, max/med=1.12<br>B n=13, robust/med=1.73, max/med=2.66 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.619 | 4.970 | 3.766 | 5.009 | noisy<br>C n=13, robust/med=1.11, max/med=3.52<br>B n=13, robust/med=1.73, max/med=2.66 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3/8 | 4.785 | 4.971 | 3.635 | 5.009 | noisy<br>C n=13, robust/med=1.13, max/med=1.15<br>B n=13, robust/med=1.73, max/med=2.66 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4/8 | 4.434 | 4.786 | 1.054 | 1.034 | noisy<br>C n=13, robust/med=1.13, max/med=1.69<br>B n=13, robust/med=1.96, max/med=2.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve17_count_4t`<br>mode: `presieve17` | 3145728 | 4/8 | 4.533 | 4.842 | 1.031 | 1.022 | noisy<br>C n=13, robust/med=1.07, max/med=1.48<br>B n=13, robust/med=1.96, max/med=2.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 4.570 | 4.929 | 1.023 | 1.004 | noisy<br>C n=13, robust/med=1.12, max/med=1.12<br>B n=13, robust/med=1.96, max/med=2.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.619 | 4.970 | 1.012 | 0.996 | noisy<br>C n=13, robust/med=1.11, max/med=3.52<br>B n=13, robust/med=1.96, max/med=2.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3/8 | 4.785 | 4.971 | 0.977 | 0.996 | noisy<br>C n=13, robust/med=1.13, max/med=1.15<br>B n=13, robust/med=1.96, max/med=2.98 |

## High-Offset Tight Scorecard

Requested Circle segment sizes: `1310720`, `1376256`, `1441792`, `1507328`, `4194304`.
Circle count modes: `segmented`, `presieve13`, `presieve17`.
Rounds per row: `7`.

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3/8 | 4.773 | 4.957 | 5.443 | 8.526 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.11, max/med=1.35 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3/8 | 4.773 | 4.957 | 0.959 | 0.951 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.02, max/med=1.89 | baseline_faster |

High-offset tight candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3/8 | 4.773 | 4.957 | 5.443 | 8.526 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 4.868 | 5.068 | 5.338 | 8.339 | stable<br>C n=7, robust/med=1.05, max/med=1.06<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_3t`<br>mode: `segmented` | 4194304 | 3/8 | 4.889 | 5.087 | 5.314 | 8.309 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.774 | 5.087 | 5.442 | 8.309 | stable<br>C n=7, robust/med=1.04, max/med=1.08<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3/8 | 4.746 | 5.095 | 5.475 | 8.295 | stable<br>C n=7, robust/med=1.06, max/med=1.14<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3/8 | 4.773 | 4.957 | 0.959 | 0.951 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.02, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 4.868 | 5.068 | 0.941 | 0.930 | stable<br>C n=7, robust/med=1.05, max/med=1.06<br>B n=7, robust/med=1.02, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_3t`<br>mode: `segmented` | 4194304 | 3/8 | 4.889 | 5.087 | 0.936 | 0.927 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.02, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.774 | 5.087 | 0.959 | 0.927 | stable<br>C n=7, robust/med=1.04, max/med=1.08<br>B n=7, robust/med=1.02, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3/8 | 4.746 | 5.095 | 0.965 | 0.926 | stable<br>C n=7, robust/med=1.06, max/med=1.14<br>B n=7, robust/med=1.02, max/med=1.89 |

## High-Offset Hot-Server Scorecard

Requested Circle segment sizes: `0`, `1507328`, `1310720`, `2097152`, `3145728`, `4194304`.
Circle count modes: `default`, `segmented`, `presieve13`, `presieve17`.
Rounds per row: `7`.

Adaptive default hot-server scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.746 | 1.882 | 1.105 | 1.040 | stable<br>C n=7, robust/med=1.06, max/med=2.31<br>B n=7, robust/med=1.22, max/med=1.66 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.711 | 1.786 | 1.245 | 1.214 | stable<br>C n=7, robust/med=1.02, max/med=1.07<br>B n=7, robust/med=1.01, max/med=1.04 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.840 | 1.993 | 2.068 | 1.996 | stable<br>C n=7, robust/med=1.39, max/med=1.78<br>B n=7, robust/med=1.15, max/med=1.22 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 2.094 | 2.448 | 4.538 | 4.856 | stable<br>C n=7, robust/med=1.44, max/med=2.11<br>B n=7, robust/med=1.28, max/med=1.39 | circle_faster |

Best hot-server candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.697 | 1.746 | 1.137 | 1.121 | stable<br>C n=7, robust/med=1.08, max/med=1.09<br>B n=7, robust/med=1.22, max/med=1.66 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.693 | 1.760 | 1.259 | 1.231 | stable<br>C n=7, robust/med=1.03, max/med=1.10<br>B n=7, robust/med=1.01, max/med=1.04 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.690 | 1.886 | 2.251 | 2.109 | stable<br>C n=7, robust/med=1.08, max/med=2.29<br>B n=7, robust/med=1.15, max/med=1.22 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 2.094 | 2.448 | 4.538 | 4.856 | stable<br>C n=7, robust/med=1.44, max/med=2.11<br>B n=7, robust/med=1.28, max/med=1.39 | circle_faster |

High-offset hot-server candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.697 | 1.746 | 1.137 | 1.121 | stable<br>C n=7, robust/med=1.08, max/med=1.09<br>B n=7, robust/med=1.22, max/med=1.66 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 1.750 | 1.800 | 1.102 | 1.087 | stable<br>C n=7, robust/med=1.01, max/med=1.03<br>B n=7, robust/med=1.22, max/med=1.66 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.667 | 1.803 | 1.157 | 1.085 | stable<br>C n=7, robust/med=1.07, max/med=1.33<br>B n=7, robust/med=1.22, max/med=1.66 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 1.830 | 1.873 | 1.054 | 1.045 | stable<br>C n=7, robust/med=1.16, max/med=1.33<br>B n=7, robust/med=1.22, max/med=1.66 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.746 | 1.882 | 1.105 | 1.040 | stable<br>C n=7, robust/med=1.06, max/med=2.31<br>B n=7, robust/med=1.22, max/med=1.66 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.693 | 1.760 | 1.259 | 1.231 | stable<br>C n=7, robust/med=1.03, max/med=1.10<br>B n=7, robust/med=1.01, max/med=1.04 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.711 | 1.786 | 1.245 | 1.214 | stable<br>C n=7, robust/med=1.02, max/med=1.07<br>B n=7, robust/med=1.01, max/med=1.04 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 1.718 | 1.842 | 1.241 | 1.177 | stable<br>C n=7, robust/med=1.08, max/med=1.30<br>B n=7, robust/med=1.01, max/med=1.04 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 1.719 | 1.863 | 1.240 | 1.163 | stable<br>C n=7, robust/med=1.20, max/med=1.30<br>B n=7, robust/med=1.01, max/med=1.04 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.823 | 1.917 | 1.169 | 1.130 | stable<br>C n=7, robust/med=1.01, max/med=1.01<br>B n=7, robust/med=1.01, max/med=1.04 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.690 | 1.886 | 2.251 | 2.109 | stable<br>C n=7, robust/med=1.08, max/med=2.29<br>B n=7, robust/med=1.15, max/med=1.22 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 1.880 | 1.936 | 2.023 | 2.055 | stable<br>C n=7, robust/med=1.02, max/med=1.03<br>B n=7, robust/med=1.15, max/med=1.22 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.766 | 1.966 | 2.155 | 2.023 | stable<br>C n=7, robust/med=1.47, max/med=2.51<br>B n=7, robust/med=1.15, max/med=1.22 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 1.840 | 1.993 | 2.068 | 1.996 | stable<br>C n=7, robust/med=1.39, max/med=1.78<br>B n=7, robust/med=1.15, max/med=1.22 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 1.747 | 2.003 | 2.178 | 1.986 | stable<br>C n=7, robust/med=1.04, max/med=1.27<br>B n=7, robust/med=1.15, max/med=1.22 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `segmented` | 1310720 | 8 | 2.094 | 2.448 | 4.538 | 4.856 | stable<br>C n=7, robust/med=1.44, max/med=2.11<br>B n=7, robust/med=1.28, max/med=1.39 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 2.042 | 2.470 | 4.654 | 4.812 | stable<br>C n=7, robust/med=1.09, max/med=2.30<br>B n=7, robust/med=1.28, max/med=1.39 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 2.228 | 2.552 | 4.266 | 4.658 | stable<br>C n=7, robust/med=1.23, max/med=1.70<br>B n=7, robust/med=1.28, max/med=1.39 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 2.062 | 2.558 | 4.608 | 4.648 | stable<br>C n=7, robust/med=1.25, max/med=1.26<br>B n=7, robust/med=1.28, max/med=1.39 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 2.404 | 2.584 | 3.953 | 4.601 | stable<br>C n=7, robust/med=1.11, max/med=1.19<br>B n=7, robust/med=1.28, max/med=1.39 |

## High-Offset Confirmation

Observed groups: `4`; confirmed: `4`; unconfirmed: `0`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `20`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 2/2 | 3/3 | 1.763, 2.066, 1.814 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 2/2 | 2/3 | 1.805, 2.082, 3.039 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 2/2 | 2/3 | 2.325, 1.900, 2.118 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 3/2 | 3/3 | 2.032, 2.907, 2.310 | `confirmed` |

## External Count Mode Sweep

Requested Circle segment sizes: `0`.
Circle count modes: `segmented`, `balanced`, `dynamic`, `prefix-pi`, `presieve13`, `presieve17`, `wheel30-mark`, `hybrid-wheel30-mark`.
Rounds per row: `5`.

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 65536 | 1/8 | 2.250 | 2.664 | 1.729 | 1.660 | stable<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=5, robust/med=1.08, max/med=1.89 | circle_faster |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 65536 | 1/8 | 2.250 | 2.664 | 1.190 | 1.221 | stable<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=5, robust/med=1.05, max/med=2.17 | circle_faster |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 196608 | 1/8 | 2.735 | 3.195 | 1.448 | 1.568 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=5, robust/med=1.01, max/med=1.11 | circle_faster |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 196608 | 1/8 | 2.735 | 3.195 | 1.483 | 1.459 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=5, robust/med=1.05, max/med=1.13 | circle_faster |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_7t`<br>mode: `balanced` | 1441792 | 7/8 | 5.994 | 6.118 | 5.041 | 8.685 | stable<br>C n=5, robust/med=1.21, max/med=1.39<br>B n=5, robust/med=1.09, max/med=2.18 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_7t`<br>mode: `balanced` | 1441792 | 7/8 | 5.994 | 6.118 | 0.830 | 0.914 | stable<br>C n=5, robust/med=1.21, max/med=1.39<br>B n=5, robust/med=1.06, max/med=1.26 | baseline_faster |

Count mode candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 65536 | 1/8 | 2.250 | 2.664 | 1.729 | 1.660 | stable<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=5, robust/med=1.08, max/med=1.89 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_8t`<br>mode: `presieve13` | 65536 | 8 | 2.730 | 2.952 | 1.425 | 1.498 | stable<br>C n=5, robust/med=1.25, max/med=1.31<br>B n=5, robust/med=1.08, max/med=1.89 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 65536 | 8 | 2.818 | 2.995 | 1.381 | 1.476 | stable<br>C n=5, robust/med=1.03, max/med=1.62<br>B n=5, robust/med=1.08, max/med=1.89 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 65536 | 8 | 2.661 | 3.009 | 1.462 | 1.469 | stable<br>C n=5, robust/med=1.14, max/med=1.30<br>B n=5, robust/med=1.08, max/med=1.89 |
| [0, 10000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve17_count_8t`<br>mode: `presieve17` | 65536 | 8 | 2.657 | 3.011 | 1.465 | 1.468 | stable<br>C n=5, robust/med=1.06, max/med=1.21<br>B n=5, robust/med=1.08, max/med=1.89 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 65536 | 1/8 | 2.250 | 2.664 | 1.190 | 1.221 | stable<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=5, robust/med=1.05, max/med=2.17 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_8t`<br>mode: `presieve13` | 65536 | 8 | 2.730 | 2.952 | 0.981 | 1.102 | stable<br>C n=5, robust/med=1.25, max/med=1.31<br>B n=5, robust/med=1.05, max/med=2.17 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 65536 | 8 | 2.818 | 2.995 | 0.950 | 1.086 | stable<br>C n=5, robust/med=1.03, max/med=1.62<br>B n=5, robust/med=1.05, max/med=2.17 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_hybrid_wheel30_mark_count_8t`<br>mode: `hybrid-wheel30-mark` | 65536 | 8 | 2.661 | 3.009 | 1.006 | 1.081 | stable<br>C n=5, robust/med=1.14, max/med=1.30<br>B n=5, robust/med=1.05, max/med=2.17 |
| [0, 10000000) | `external_primesieve_count` | `circle_prime_parallel_presieve17_count_8t`<br>mode: `presieve17` | 65536 | 8 | 2.657 | 3.011 | 1.008 | 1.080 | stable<br>C n=5, robust/med=1.06, max/med=1.21<br>B n=5, robust/med=1.05, max/med=2.17 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 196608 | 1/8 | 2.735 | 3.195 | 1.448 | 1.568 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=5, robust/med=1.01, max/med=1.11 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_8t`<br>mode: `presieve13` | 196608 | 8 | 6.173 | 6.348 | 0.641 | 0.789 | stable<br>C n=5, robust/med=1.20, max/med=1.42<br>B n=5, robust/med=1.01, max/med=1.11 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 6.368 | 6.777 | 0.622 | 0.739 | stable<br>C n=5, robust/med=1.05, max/med=1.14<br>B n=5, robust/med=1.01, max/med=1.11 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 6.419 | 7.035 | 0.617 | 0.712 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.01, max/med=1.11 |
| [0, 100000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 196608 | 8 | 6.437 | 7.359 | 0.615 | 0.681 | stable<br>C n=5, robust/med=1.27, max/med=1.98<br>B n=5, robust/med=1.01, max/med=1.11 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 196608 | 1/8 | 2.735 | 3.195 | 1.483 | 1.459 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=5, robust/med=1.05, max/med=1.13 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_8t`<br>mode: `presieve13` | 196608 | 8 | 6.173 | 6.348 | 0.657 | 0.735 | stable<br>C n=5, robust/med=1.20, max/med=1.42<br>B n=5, robust/med=1.05, max/med=1.13 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_8t`<br>mode: `dynamic` | 196608 | 8 | 6.368 | 6.777 | 0.637 | 0.688 | stable<br>C n=5, robust/med=1.05, max/med=1.14<br>B n=5, robust/med=1.05, max/med=1.13 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 6.419 | 7.035 | 0.632 | 0.663 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.05, max/med=1.13 |
| [0, 100000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_8t`<br>mode: `balanced` | 196608 | 8 | 6.437 | 7.359 | 0.630 | 0.634 | stable<br>C n=5, robust/med=1.27, max/med=1.98<br>B n=5, robust/med=1.05, max/med=1.13 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_balanced_count_7t`<br>mode: `balanced` | 1441792 | 7/8 | 5.994 | 6.118 | 5.041 | 8.685 | stable<br>C n=5, robust/med=1.21, max/med=1.39<br>B n=5, robust/med=1.09, max/med=2.18 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve17_count_7t`<br>mode: `presieve17` | 1441792 | 7/8 | 5.439 | 6.135 | 5.556 | 8.661 | stable<br>C n=5, robust/med=1.05, max/med=1.26<br>B n=5, robust/med=1.09, max/med=2.18 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_7t`<br>mode: `segmented` | 1441792 | 7/8 | 5.315 | 6.553 | 5.686 | 8.109 | stable<br>C n=5, robust/med=1.00, max/med=1.08<br>B n=5, robust/med=1.09, max/med=2.18 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_dynamic_count_7t`<br>mode: `dynamic` | 1441792 | 7/8 | 5.330 | 6.652 | 5.669 | 7.988 | stable<br>C n=5, robust/med=1.15, max/med=1.16<br>B n=5, robust/med=1.09, max/med=2.18 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 5.980 | 7.083 | 5.054 | 7.502 | stable<br>C n=5, robust/med=1.04, max/med=1.28<br>B n=5, robust/med=1.09, max/med=2.18 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_balanced_count_7t`<br>mode: `balanced` | 1441792 | 7/8 | 5.994 | 6.118 | 0.830 | 0.914 | stable<br>C n=5, robust/med=1.21, max/med=1.39<br>B n=5, robust/med=1.06, max/med=1.26 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve17_count_7t`<br>mode: `presieve17` | 1441792 | 7/8 | 5.439 | 6.135 | 0.915 | 0.911 | stable<br>C n=5, robust/med=1.05, max/med=1.26<br>B n=5, robust/med=1.06, max/med=1.26 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_7t`<br>mode: `segmented` | 1441792 | 7/8 | 5.315 | 6.553 | 0.936 | 0.853 | stable<br>C n=5, robust/med=1.00, max/med=1.08<br>B n=5, robust/med=1.06, max/med=1.26 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_dynamic_count_7t`<br>mode: `dynamic` | 1441792 | 7/8 | 5.330 | 6.652 | 0.933 | 0.840 | stable<br>C n=5, robust/med=1.15, max/med=1.16<br>B n=5, robust/med=1.06, max/med=1.26 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 5.980 | 7.083 | 0.832 | 0.789 | stable<br>C n=5, robust/med=1.04, max/med=1.28<br>B n=5, robust/med=1.06, max/med=1.26 |

## External Mode Confirmation

Observed groups: `3`; confirmed: `1`; unconfirmed: `2`.
Minimum confirmations: `2`; requires stable samples: `True`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primesieve_count` | `dynamic` | 196608 | 8 | 0/2 | 0/2 | 3.104 | `unconfirmed` |
| [0, 100000000) | `external_primesieve_count` | `dynamic` | 98304 | 8 | 0/2 | 0/2 | 6.974 | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `segmented` | 3145728 | 4/8 | 2/2 | 2/2 | 6.188, 6.214 | `confirmed` |

## External Throughput

Requested Circle segment sizes: `0`, `131072`, `196608`, `262144`, `524288`.
Circle count modes: `default`, `segmented`, `prefix-pi`.
Rounds per row: `5`.

Adaptive default scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 6.209 | 10.092 | 0.799 | 0.650 | stable<br>C n=5, robust/med=1.00, max/med=1.96<br>B n=5, robust/med=1.12, max/med=1.64 | baseline_faster |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 6.209 | 10.092 | 3.112 | 3.056 | stable<br>C n=5, robust/med=1.00, max/med=1.96<br>B n=5, robust/med=1.22, max/med=1.28 | circle_faster |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 9.828 | 10.475 | 0.910 | 1.054 | stable<br>C n=5, robust/med=1.06, max/med=1.52<br>B n=5, robust/med=1.01, max/med=1.15 | circle_faster |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 9.828 | 10.475 | 2.153 | 2.172 | stable<br>C n=5, robust/med=1.06, max/med=1.52<br>B n=5, robust/med=1.00, max/med=1.19 | circle_faster |

Prefix-pi thread comparison:

| Range | Baseline | Serial Row | Default Row | Serial ms | Default ms | Median Ratio | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` (2/8) | 12.964 | 10.475 | 1.238 | `default_faster` |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` (2/8) | 12.964 | 10.475 | 1.238 | `default_faster` |

Throughput segment candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 6.209 | 10.092 | 0.799 | 0.650 | stable<br>C n=5, robust/med=1.00, max/med=1.96<br>B n=5, robust/med=1.12, max/med=1.64 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 6.761 | 10.472 | 0.734 | 0.626 | stable<br>C n=5, robust/med=1.06, max/med=1.19<br>B n=5, robust/med=1.12, max/med=1.64 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 51.940 | 61.176 | 0.096 | 0.107 | stable<br>C n=5, robust/med=1.30, max/med=1.55<br>B n=5, robust/med=1.12, max/med=1.64 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 131072 | 8 | 47.852 | 62.311 | 0.104 | 0.105 | stable<br>C n=5, robust/med=1.07, max/med=1.47<br>B n=5, robust/med=1.12, max/med=1.64 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 56.565 | 67.328 | 0.088 | 0.097 | stable<br>C n=5, robust/med=1.14, max/med=1.32<br>B n=5, robust/med=1.12, max/med=1.64 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 6.209 | 10.092 | 3.112 | 3.056 | stable<br>C n=5, robust/med=1.00, max/med=1.96<br>B n=5, robust/med=1.22, max/med=1.28 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 6.761 | 10.472 | 2.857 | 2.945 | stable<br>C n=5, robust/med=1.06, max/med=1.19<br>B n=5, robust/med=1.22, max/med=1.28 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 51.940 | 61.176 | 0.372 | 0.504 | stable<br>C n=5, robust/med=1.30, max/med=1.55<br>B n=5, robust/med=1.22, max/med=1.28 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 131072 | 8 | 47.852 | 62.311 | 0.404 | 0.495 | stable<br>C n=5, robust/med=1.07, max/med=1.47<br>B n=5, robust/med=1.22, max/med=1.28 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 56.565 | 67.328 | 0.342 | 0.458 | stable<br>C n=5, robust/med=1.14, max/med=1.32<br>B n=5, robust/med=1.22, max/med=1.28 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 9.828 | 10.475 | 0.910 | 1.054 | stable<br>C n=5, robust/med=1.06, max/med=1.52<br>B n=5, robust/med=1.01, max/med=1.15 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 10.176 | 11.096 | 0.879 | 0.995 | stable<br>C n=5, robust/med=1.03, max/med=1.23<br>B n=5, robust/med=1.01, max/med=1.15 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 12.687 | 12.964 | 0.705 | 0.852 | stable<br>C n=5, robust/med=1.01, max/med=2.67<br>B n=5, robust/med=1.01, max/med=1.15 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 50.974 | 61.165 | 0.175 | 0.181 | stable<br>C n=5, robust/med=1.25, max/med=1.27<br>B n=5, robust/med=1.01, max/med=1.15 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 47.025 | 61.734 | 0.190 | 0.179 | noisy<br>C n=5, robust/med=2.04, max/med=2.32<br>B n=5, robust/med=1.01, max/med=1.15 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 9.828 | 10.475 | 2.153 | 2.172 | stable<br>C n=5, robust/med=1.06, max/med=1.52<br>B n=5, robust/med=1.00, max/med=1.19 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 10.176 | 11.096 | 2.079 | 2.051 | stable<br>C n=5, robust/med=1.03, max/med=1.23<br>B n=5, robust/med=1.00, max/med=1.19 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 12.687 | 12.964 | 1.668 | 1.755 | stable<br>C n=5, robust/med=1.01, max/med=2.67<br>B n=5, robust/med=1.00, max/med=1.19 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 50.974 | 61.165 | 0.415 | 0.372 | stable<br>C n=5, robust/med=1.25, max/med=1.27<br>B n=5, robust/med=1.00, max/med=1.19 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 47.025 | 61.734 | 0.450 | 0.369 | noisy<br>C n=5, robust/med=2.04, max/med=2.32<br>B n=5, robust/med=1.00, max/med=1.19 |

## External Segment Sweep

Requested Circle segment sizes: `0`, `32768`, `65536`, `98304`, `131072`, `196608`, `262144`, `524288`, `1048576`, `2097152`, `3145728`, `4194304`.
Circle count modes: `segmented`.
Rounds per row: `5`.

| Range | Baseline | Best Circle Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 10000000) | `external_primecount_pi_diff` | 196608 | 8 | 2.849 | 2.888 | 1.361 | 1.482 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.11, max/med=1.88 | circle_faster |
| [0, 10000000) | `external_primesieve_count` | 196608 | 8 | 2.849 | 2.888 | 1.015 | 1.030 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.06, max/med=2.43 | circle_faster |
| [0, 100000000) | `external_primecount_pi_diff` | 131072 | 8 | 6.461 | 6.744 | 0.699 | 0.724 | stable<br>C n=5, robust/med=1.09, max/med=1.37<br>B n=5, robust/med=1.23, max/med=1.30 | baseline_faster |
| [0, 100000000) | `external_primesieve_count` | 131072 | 8 | 6.461 | 6.744 | 0.740 | 0.740 | stable<br>C n=5, robust/med=1.09, max/med=1.37<br>B n=5, robust/med=1.18, max/med=1.43 | baseline_faster |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 4194304 | 3/8 | 5.185 | 5.335 | 4.199 | 5.089 | noisy<br>C n=5, robust/med=1.03, max/med=1.10<br>B n=5, robust/med=1.78, max/med=1.98 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 4194304 | 3/8 | 5.185 | 5.335 | 0.890 | 0.900 | stable<br>C n=5, robust/med=1.03, max/med=1.10<br>B n=5, robust/med=1.00, max/med=1.06 | baseline_faster |

Segment candidate spread:

| Range | Baseline | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 10000000) | `external_primecount_pi_diff` | 196608 | 8 | 2.849 | 2.888 | 1.361 | 1.482 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.11, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 98304 | 8 | 2.856 | 2.923 | 1.357 | 1.465 | stable<br>C n=5, robust/med=1.01, max/med=1.12<br>B n=5, robust/med=1.11, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 65536 | 8 | 2.871 | 3.000 | 1.350 | 1.427 | stable<br>C n=5, robust/med=1.07, max/med=1.33<br>B n=5, robust/med=1.11, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 32768 | 8 | 2.898 | 3.054 | 1.337 | 1.402 | stable<br>C n=5, robust/med=1.00, max/med=1.17<br>B n=5, robust/med=1.11, max/med=1.88 |
| [0, 10000000) | `external_primecount_pi_diff` | 131072 | 8 | 3.038 | 3.088 | 1.276 | 1.387 | stable<br>C n=5, robust/med=1.01, max/med=1.03<br>B n=5, robust/med=1.11, max/med=1.88 |
| [0, 10000000) | `external_primesieve_count` | 196608 | 8 | 2.849 | 2.888 | 1.015 | 1.030 | stable<br>C n=5, robust/med=1.02, max/med=1.07<br>B n=5, robust/med=1.06, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 98304 | 8 | 2.856 | 2.923 | 1.012 | 1.018 | stable<br>C n=5, robust/med=1.01, max/med=1.12<br>B n=5, robust/med=1.06, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 65536 | 8 | 2.871 | 3.000 | 1.006 | 0.992 | stable<br>C n=5, robust/med=1.07, max/med=1.33<br>B n=5, robust/med=1.06, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 32768 | 8 | 2.898 | 3.054 | 0.997 | 0.974 | stable<br>C n=5, robust/med=1.00, max/med=1.17<br>B n=5, robust/med=1.06, max/med=2.43 |
| [0, 10000000) | `external_primesieve_count` | 131072 | 8 | 3.038 | 3.088 | 0.951 | 0.964 | stable<br>C n=5, robust/med=1.01, max/med=1.03<br>B n=5, robust/med=1.06, max/med=2.43 |
| [0, 100000000) | `external_primecount_pi_diff` | 131072 | 8 | 6.461 | 6.744 | 0.699 | 0.724 | stable<br>C n=5, robust/med=1.09, max/med=1.37<br>B n=5, robust/med=1.23, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 98304 | 8 | 6.743 | 7.237 | 0.670 | 0.675 | stable<br>C n=5, robust/med=1.01, max/med=1.18<br>B n=5, robust/med=1.23, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 262144 | 8 | 7.118 | 7.500 | 0.635 | 0.651 | stable<br>C n=5, robust/med=1.00, max/med=1.02<br>B n=5, robust/med=1.23, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 65536 | 8 | 7.063 | 7.761 | 0.640 | 0.629 | stable<br>C n=5, robust/med=1.04, max/med=1.08<br>B n=5, robust/med=1.23, max/med=1.30 |
| [0, 100000000) | `external_primecount_pi_diff` | 196608 | 8 | 6.758 | 8.173 | 0.669 | 0.598 | stable<br>C n=5, robust/med=1.28, max/med=1.41<br>B n=5, robust/med=1.23, max/med=1.30 |
| [0, 100000000) | `external_primesieve_count` | 131072 | 8 | 6.461 | 6.744 | 0.740 | 0.740 | stable<br>C n=5, robust/med=1.09, max/med=1.37<br>B n=5, robust/med=1.18, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 98304 | 8 | 6.743 | 7.237 | 0.709 | 0.690 | stable<br>C n=5, robust/med=1.01, max/med=1.18<br>B n=5, robust/med=1.18, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 262144 | 8 | 7.118 | 7.500 | 0.672 | 0.666 | stable<br>C n=5, robust/med=1.00, max/med=1.02<br>B n=5, robust/med=1.18, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 65536 | 8 | 7.063 | 7.761 | 0.677 | 0.643 | stable<br>C n=5, robust/med=1.04, max/med=1.08<br>B n=5, robust/med=1.18, max/med=1.43 |
| [0, 100000000) | `external_primesieve_count` | 196608 | 8 | 6.758 | 8.173 | 0.708 | 0.611 | stable<br>C n=5, robust/med=1.28, max/med=1.41<br>B n=5, robust/med=1.18, max/med=1.43 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 4194304 | 3/8 | 5.185 | 5.335 | 4.199 | 5.089 | noisy<br>C n=5, robust/med=1.03, max/med=1.10<br>B n=5, robust/med=1.78, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 2097152 | 5/8 | 5.584 | 5.690 | 3.898 | 4.772 | noisy<br>C n=5, robust/med=1.03, max/med=1.09<br>B n=5, robust/med=1.78, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 3145728 | 4/8 | 5.089 | 5.945 | 4.278 | 4.567 | noisy<br>C n=5, robust/med=1.10, max/med=1.11<br>B n=5, robust/med=1.78, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 524288 | 8 | 6.223 | 6.614 | 3.498 | 4.105 | noisy<br>C n=5, robust/med=1.05, max/med=1.12<br>B n=5, robust/med=1.78, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff` | 1048576 | 8 | 6.654 | 6.747 | 3.272 | 4.024 | noisy<br>C n=5, robust/med=1.01, max/med=1.03<br>B n=5, robust/med=1.78, max/med=1.98 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 4194304 | 3/8 | 5.185 | 5.335 | 0.890 | 0.900 | stable<br>C n=5, robust/med=1.03, max/med=1.10<br>B n=5, robust/med=1.00, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 2097152 | 5/8 | 5.584 | 5.690 | 0.826 | 0.844 | stable<br>C n=5, robust/med=1.03, max/med=1.09<br>B n=5, robust/med=1.00, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 3145728 | 4/8 | 5.089 | 5.945 | 0.907 | 0.808 | stable<br>C n=5, robust/med=1.10, max/med=1.11<br>B n=5, robust/med=1.00, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 524288 | 8 | 6.223 | 6.614 | 0.741 | 0.726 | stable<br>C n=5, robust/med=1.05, max/med=1.12<br>B n=5, robust/med=1.00, max/med=1.06 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | 1048576 | 8 | 6.654 | 6.747 | 0.693 | 0.711 | stable<br>C n=5, robust/med=1.01, max/med=1.03<br>B n=5, robust/med=1.00, max/med=1.06 |

## Default Calibration

Recommendations: `8`; aligned: `6`; within tolerance: `1`; drift: `0`; noisy drift: `0`; unconfirmed mode drift: `1`; missing evidence: `0`.
Tolerance: `0.050` median slowdown.

| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1 -> 1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=15, robust/med=2.28, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=15, robust/med=1.25, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8 -> 8 | 1.763 | stable<br>C n=27, robust/med=1.38, max/med=1.56<br>B n=27, robust/med=1.49, max/med=1.51<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_tight` | `external_primesieve_count` | `presieve13` | `segmented` | 4194304 | 1310720 | 3/8 -> 8 | 4.957 | stable<br>C n=7, robust/med=1.03, max/med=1.21<br>B n=7, robust/med=1.02, max/med=1.89<br>mode missing 0/2 | 1.098x | `unconfirmed_mode_drift` |
| [1500000000000, 1500010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8 -> 8 | 1.805 | noisy<br>effective stable<br>C n=27, robust/med=2.36, max/med=2.49<br>B n=27, robust/med=1.47, max/med=1.50<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [10000000000000, 10000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8 -> 8 | 1.900 | noisy<br>effective stable<br>C n=27, robust/med=1.65, max/med=2.02<br>B n=27, robust/med=1.57, max/med=1.79<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [100000000000000, 100000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `segmented` | `segmented` | 1310720 | 1310720 | 8 -> 8 | 2.032 | noisy<br>effective stable<br>C n=27, robust/med=1.85, max/med=1.85<br>B n=27, robust/med=1.20, max/med=1.24<br>mode confirmed 3/2 | 1.000x | `aligned` |

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

High-offset hot/cold rows:

| Workload | Row | Segment | Best ms | Count |
| ---: | --- | ---: | ---: | ---: |
| 10000000 | `high_offset_segmented_range_count` | 4194304 | 6.214 | 361726 |
| 10000000 | `parallel_high_offset_segmented_range_count_8t` | 4194304 | 3.499 | 361726 |
| 10000000 | `parallel_high_offset_default_range_count_8t` | 4194304 | 3.309 | 361726 |
| 10000000 | `parallel_high_offset_balanced_segmented_range_count_8t` | 4194304 | 2.902 | 361726 |
| 10000000 | `high_offset_presieve13_range_count` | 4194304 | 6.154 | 361726 |
| 10000000 | `parallel_high_offset_presieve13_range_count_8t` | 4194304 | 2.556 | 361726 |
| 10000000 | `high_offset_presieve17_range_count` | 4194304 | 6.039 | 361726 |
| 10000000 | `parallel_high_offset_presieve17_range_count_8t` | 4194304 | 3.090 | 361726 |
| 10000000 | `high_offset_bitpacked_range_count` | 4194304 | 7.572 | 361726 |
| 10000000 | `high_offset_tracked_byte_range_count` | 4194304 | 16.731 | 361726 |
| 10000000 | `high_offset_wheel30_range_count` | 4194304 | 49.964 | 361726 |
| 10000000 | `high_offset_wheel30_mark_range_count` | 4194304 | 5.872 | 361726 |
| 10000000 | `parallel_high_offset_wheel30_mark_range_count_8t` | 4194304 | 4.854 | 361726 |
| 10000000 | `high_offset_hybrid_wheel30_mark_range_count` | 4194304 | 6.721 | 361726 |
| 10000000 | `parallel_high_offset_hybrid_wheel30_mark_range_count_8t` | 4194304 | 4.636 | 361726 |
| 100000 | `high_offset_u64_scalar_fallback_range_count` | 64 | 44.960 | 2139 |
| 100000 | `high_offset_u64_scalar_naive_control_count` | 0 | 45.100 | 2139 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 4194304 | 3.050 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_segmented_count_8t` | 4194304 | 2.842 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 4194304 | 2.731 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve17_count_8t` | 4194304 | 3.284 | 361726 |
| 1000000 | `cold_process_segmented_range_count` | 262144 | 1.840 | 78498 |
| 10000000 | `cold_process_segmented_range_count` | 262144 | 3.069 | 664579 |
| 10000000 | `cold_process_parallel_segmented_range_count_8t` | 65536 | 2.329 | 664579 |
| 10000000 | `cold_cli_parallel_default_range_count_8t` | 65536 | 1.476 | 664579 |
| 100000000 | `cold_process_parallel_segmented_range_count_8t` | 196608 | 6.259 | 5761455 |
| 100000000 | `cold_cli_parallel_default_range_count_8t` | 196608 | 2.603 | 5761455 |
| 10000000 | `cold_process_parallel_high_offset_segmented_range_count_8t` | 4194304 | 4.870 | 361726 |
| 10000000 | `cold_cli_parallel_high_offset_default_range_count_8t` | 4194304 | 4.834 | 361726 |

High-offset cold/hot overhead (source: `high_offset_hot_cold`):

| Workload | Hot Row | Hot ms | Server Row | Count Server ms | Server / Hot | Server / Cold CLI | Cold CLI ms | CLI / Hot | CLI Extra ms | Cold Process ms | Process / Hot |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10000000 | `parallel_high_offset_presieve13_range_count_8t` | 2.556 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | 1.07x | 0.56x | 4.834 | 1.89x | 2.278 | 4.870 | 1.91x |

High-offset server/external best-time comparison:

| Workload | Server Row | Server ms | Baseline | Baseline Best ms | Server Speedup | Cold CLI ms | Cold CLI Speedup |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primecount_pi_diff` | 23.041 | 8.437 | 5.175 | 4.453 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primecount_pi_diff` | 23.041 | 8.437 | 1.723 | 13.372 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primesieve_count` | 4.442 | 1.627 | 5.175 | 0.858 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primesieve_count` | 4.442 | 1.627 | 1.723 | 2.578 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primesieve_count_server` | 1.920 | 0.703 | 5.175 | 0.371 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 2.731 | `external_primesieve_count_server` | 1.920 | 0.703 | 1.723 | 1.114 |

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

Samples: `12`; rounds: `9`; elapsed seconds: `0.21430345799999984`.

| Range | Mode | Segment | Threads | Best ms | Median ms | Count |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [0, 1000000) | `prefix-pi` | 131072 | 1/1 | 0.000 | 0.000 | 78498 |

Default alignment uses current calibration defaults when available; `stale artifact` means the tuning JSON stored an older default.

Default alignment:

| Range | Tuned mode | Default mode | Tuned segment | Default segment | Tuned threads | Default threads | Default source | Median ms | Aligned |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1/1 | 1/1 | `current_calibration` | 0.000 | no |
