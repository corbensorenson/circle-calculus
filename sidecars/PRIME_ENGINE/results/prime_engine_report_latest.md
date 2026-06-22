# Prime Engine Report

Generated: `2026-06-22T03:05:29Z`

## External Control Provenance

| Artifact | Tool | Status | Version / Method | Path | Hashes |
| --- | --- | --- | --- | --- | --- |
| `external_controls` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `external_controls` | `primecount` | `available` | `primecount 8.5, <https://github.com/kimwalisch/primecount>` | `/opt/homebrew/bin/primecount` |  |
| `external_controls` | `primesieve_count_server` | `available` | `primesieve_count_primes(LOW, HIGH-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server` | `bin ced5d35595a7, src d27411820c2d` |
| `external_controls` | `primecount_pi_server` | `available` | `primecount_pi(HIGH-1)-primecount_pi(LOW-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server` | `bin aab86c4892fc, src 2a1079b82bac` |
| `competitive_smoke` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `competitive_smoke` | `primecount` | `available` | `primecount 8.5, <https://github.com/kimwalisch/primecount>` | `/opt/homebrew/bin/primecount` |  |
| `competitive_smoke` | `primesieve_count_server` | `available` | `primesieve_count_primes(LOW, HIGH-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server` | `bin ced5d35595a7, src d27411820c2d` |
| `competitive_smoke` | `primecount_pi_server` | `available` | `primecount_pi(HIGH-1)-primecount_pi(LOW-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server` | `bin aab86c4892fc, src 2a1079b82bac` |
| `high_offset_count_binary` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `high_offset_count_binary` | `primecount` | `available` | `primecount 8.5, <https://github.com/kimwalisch/primecount>` | `/opt/homebrew/bin/primecount` |  |
| `high_offset_count_binary` | `primesieve_count_server` | `available` | `primesieve_count_primes(LOW, HIGH-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server` | `bin ced5d35595a7, src d27411820c2d` |
| `high_offset_count_binary` | `primecount_pi_server` | `available` | `primecount_pi(HIGH-1)-primecount_pi(LOW-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server` | `bin aab86c4892fc, src 2a1079b82bac` |
| `high_offset_hot_server` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `high_offset_hot_server` | `primecount` | `available` | `primecount 8.5, <https://github.com/kimwalisch/primecount>` | `/opt/homebrew/bin/primecount` |  |
| `high_offset_hot_server` | `primesieve_count_server` | `available` | `primesieve_count_primes(LOW, HIGH-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server` | `bin ced5d35595a7, src d27411820c2d` |
| `high_offset_hot_server` | `primecount_pi_server` | `available` | `primecount_pi(HIGH-1)-primecount_pi(LOW-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server` | `bin aab86c4892fc, src 2a1079b82bac` |
| `high_offset_shifted_count_binary` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `high_offset_shifted_count_binary` | `primecount` | `available` | `primecount 8.5, <https://github.com/kimwalisch/primecount>` | `/opt/homebrew/bin/primecount` |  |
| `high_offset_shifted_count_binary` | `primesieve_count_server` | `available` | `primesieve_count_primes(LOW, HIGH-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server` | `bin ced5d35595a7, src d27411820c2d` |
| `high_offset_shifted_count_binary` | `primecount_pi_server` | `available` | `primecount_pi(HIGH-1)-primecount_pi(LOW-1)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server` | `bin aab86c4892fc, src 2a1079b82bac` |
| `external_next_server` | `primesieve` | `available` | `primesieve 12.14, <https://github.com/kimwalisch/primesieve>` | `/opt/homebrew/bin/primesieve` |  |
| `external_next_server` | `primesieve_library_server` | `available` | `primesieve_generate_n_primes(1, START, UINT64_PRIMES)` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-next-server` | `bin d3f6b22afcf9, src 78f814c881db` |
| `external_next_server` | `primesieve_iterator_server` | `available` | `primesieve::iterator.jump_to(START).next_prime()` | `/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-iterator-next-server` | `bin f955cf804c67, src a4e254ebc837` |

## External Correctness

Status: `passed`; checks: `826`; failures: `0`.
Count checks: `386`; count-server checks: `386`; enumeration checks: `46`; next-prime checks: `8`.
Next-prime external oracle comparisons: `14`.
Required external controls: `primecount`, `primesieve`.
Circle count modes checked: `segmented`, `balanced`, `dynamic`, `prefix-pi`, `presieve13`, `presieve17`, `wheel30-mark`, `hybrid-wheel30-mark`.
Requested Circle segment sizes: `0`, `65536`, `196608`, `1310720`, `1441792`, `1507328`, `2621440`, `4194304`.
Requested threads: Circle `8`, external `8`.
Count ranges checked: `8`.
Enumeration ranges checked: `6`.
Largest checked high: `18446744073709551615`.
Primecount next-prime checks capped at start `1000000000000`.

## External Controls

- `primesieve` cold CLI: Circle faster on 3/4 rows by best time; median faster on 2/4 rows.
- `primesieve` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimesieve count server` external server: Circle faster on 5/8 rows by best time; median faster on 5/8 rows.
- `primecount` cold CLI: Circle faster on 3/4 rows by best time; median faster on 4/4 rows.
- `primecount` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimecount pi server` external server: Circle faster on 5/8 rows by best time; median faster on 5/8 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- `circle_count_server`: available (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`); method `persistent count-server requests`.
- `circle_count_server` small-prefix `pi` cache: limit `2000000000`; default `2000000000`; max `3000000000`; env `CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT`; scope prefix-pi count-server ranges with HIGH-1 at or below the limit.
- `circle_count_server` small-prefix `pi` cache memory: estimated bytes `187500004`; default bytes `187500004`; max bytes `281250004`.
- `circle_count_server` small-prefix `pi` cache startup warmup: min `6904.493 ms`; median `7646.285 ms`; max `8944.585 ms`; samples `3`.
- `circle_count_server` small-prefix `pi` cache warmup: eligible prefix-pi count-server rows pass --warm-prefix-pi-cache before reading timed requests.
- `primesieve_count_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-count-server`); method `primesieve_count_primes(LOW, HIGH-1)`.
- `primecount_pi_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-pi-server`); method `primecount_pi(HIGH-1)-primecount_pi(LOW-1)`.
- requested threads: Circle `8`, external `8` (`0` means tool default/all cores).
- Circle count modes: `default`.
- required external controls: `primecount`, `primecount-library`, `primesieve`.
- timing policy: interleaved round-robin samples.
- warmup: `2` unrecorded interleaved pass(es).
- repeated count requests per timed sample: `20` (reported timings are per-request averages).
- Circle server rows: persistent `count-server` requests included.
- libprimesieve count-server rows included.
- libprimecount pi-server rows included.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv`.

| Range | Circle Row | Baseline | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | --- | --- |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 2.184 | 0.937 | noisy<br>C n=7, robust/med=1.46, max/med=5.15<br>B n=7, robust/med=1.57, max/med=1.67 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1367.329 | 1078.344 | noisy<br>C n=7, robust/med=10.27, max/med=12.45<br>B n=7, robust/med=1.57, max/med=1.67 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.612 | 1.081 | stable<br>C n=7, robust/med=1.46, max/med=5.15<br>B n=7, robust/med=1.50, max/med=1.70 | circle_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1009.081 | 1244.002 | noisy<br>C n=7, robust/med=10.27, max/med=12.45<br>B n=7, robust/med=1.50, max/med=1.70 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.138 | 0.077 | stable<br>C n=7, robust/med=1.46, max/med=5.15<br>B n=7, robust/med=1.28, max/med=2.40 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 86.378 | 88.109 | noisy<br>C n=7, robust/med=10.27, max/med=12.45<br>B n=7, robust/med=1.28, max/med=2.40 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.005 | 0.004 | noisy<br>C n=7, robust/med=1.46, max/med=5.15<br>B n=7, robust/med=2.06, max/med=7.20 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 3.289 | 4.378 | noisy<br>C n=7, robust/med=10.27, max/med=12.45<br>B n=7, robust/med=2.06, max/med=7.20 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1.857 | 2.305 | noisy<br>C n=7, robust/med=2.10, max/med=2.78<br>B n=7, robust/med=1.29, max/med=1.85 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1414.982 | 1886.199 | noisy<br>C n=7, robust/med=3.26, max/med=3.64<br>B n=7, robust/med=1.29, max/med=1.85 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.785 | 1.873 | noisy<br>C n=7, robust/med=2.10, max/med=2.78<br>B n=7, robust/med=1.48, max/med=5.73 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1359.923 | 1532.863 | noisy<br>C n=7, robust/med=3.26, max/med=3.64<br>B n=7, robust/med=1.48, max/med=5.73 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.660 | 0.776 | noisy<br>C n=7, robust/med=2.10, max/med=2.78<br>B n=7, robust/med=1.43, max/med=1.74 | baseline_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 503.119 | 634.762 | noisy<br>C n=7, robust/med=3.26, max/med=3.64<br>B n=7, robust/med=1.43, max/med=1.74 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.022 | 0.021 | noisy<br>C n=7, robust/med=2.10, max/med=2.78<br>B n=7, robust/med=1.25, max/med=2.63 | baseline_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 16.526 | 17.123 | noisy<br>C n=7, robust/med=3.26, max/med=3.64<br>B n=7, robust/med=1.25, max/med=2.63 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 4.318 | 4.557 | stable<br>C n=7, robust/med=1.33, max/med=2.21<br>B n=7, robust/med=1.11, max/med=1.43 | circle_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 5332.226 | 5888.753 | stable<br>C n=7, robust/med=1.17, max/med=3.01<br>B n=7, robust/med=1.11, max/med=1.43 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 0.959 | 1.037 | stable<br>C n=7, robust/med=1.33, max/med=2.21<br>B n=7, robust/med=1.07, max/med=1.40 | circle_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1184.022 | 1340.405 | stable<br>C n=7, robust/med=1.17, max/med=3.01<br>B n=7, robust/med=1.07, max/med=1.40 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 3.547 | 3.805 | stable<br>C n=7, robust/med=1.33, max/med=2.21<br>B n=7, robust/med=1.09, max/med=1.16 | circle_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 4379.745 | 4916.766 | stable<br>C n=7, robust/med=1.17, max/med=3.01<br>B n=7, robust/med=1.09, max/med=1.16 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.058 | 0.055 | stable<br>C n=7, robust/med=1.33, max/med=2.21<br>B n=7, robust/med=1.03, max/med=1.06 | baseline_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 71.542 | 71.718 | stable<br>C n=7, robust/med=1.17, max/med=3.01<br>B n=7, robust/med=1.03, max/med=1.06 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primesieve_count` (threads: 8) | 0.833 | 0.758 | stable<br>C n=7, robust/med=1.06, max/med=1.09<br>B n=7, robust/med=1.41, max/med=1.67 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primesieve_count` (threads: 8) | 47.422 | 43.404 | stable<br>C n=7, robust/med=1.14, max/med=2.13<br>B n=7, robust/med=1.41, max/med=1.67 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primecount_pi_diff` (threads: 8) | 5.584 | 7.226 | stable<br>C n=7, robust/med=1.06, max/med=1.09<br>B n=7, robust/med=1.29, max/med=1.29 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primecount_pi_diff` (threads: 8) | 317.931 | 414.001 | stable<br>C n=7, robust/med=1.14, max/med=2.13<br>B n=7, robust/med=1.29, max/med=1.29 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primesieve_count_server` (threads: 8) | 0.364 | 0.310 | noisy<br>C n=7, robust/med=1.06, max/med=1.09<br>B n=7, robust/med=1.80, max/med=2.57 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primesieve_count_server` (threads: 8) | 20.740 | 17.779 | noisy<br>C n=7, robust/med=1.14, max/med=2.13<br>B n=7, robust/med=1.80, max/med=2.57 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primecount_pi_diff_server` (threads: 8) | 1.802 | 1.663 | stable<br>C n=7, robust/med=1.06, max/med=1.09<br>B n=7, robust/med=1.25, max/med=1.26 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` (threads: 7/8) | `external_primecount_pi_diff_server` (threads: 8) | 102.601 | 95.267 | stable<br>C n=7, robust/med=1.14, max/med=2.13<br>B n=7, robust/med=1.25, max/med=1.26 | circle_faster |

## External Next-Prime Search

- `libprimesieve generate_n_primes server` cold CLI: Circle faster on 1/5 rows by best time; median faster on 1/5 rows.
- `libprimesieve iterator server` cold CLI: Circle faster on 1/5 rows by best time; median faster on 1/5 rows.
- `primesieve --nth-prime` cold CLI: Circle faster on 4/5 rows by best time; median faster on 3/5 rows.
- `primecount pi+nth-prime` cold CLI: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimecount pi+nth-prime server` cold CLI: Circle faster on 1/4 rows by best time; median faster on 1/4 rows.
- `libprimesieve generate_n_primes server` server: Circle faster on 5/5 rows by best time; median faster on 5/5 rows.
- `libprimesieve iterator server` server: Circle faster on 5/5 rows by best time; median faster on 5/5 rows.
- `primesieve --nth-prime` server: Circle faster on 5/5 rows by best time; median faster on 5/5 rows.
- `primecount pi+nth-prime` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimecount pi+nth-prime server` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- `primesieve_library_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-next-server`); method `primesieve_generate_n_primes(1, START, UINT64_PRIMES)`.
- `primesieve_iterator_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-iterator-next-server`); method `primesieve::iterator.jump_to(START).next_prime()`.
- `primecount_library_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primecount-next-server`); method `primecount_pi(START-1) then primecount_nth_prime(pi+1)`.
- requested threads: Circle `1`, external `8` (`0` means tool default/all cores).
- next-prime starts: `90`, `1000000`, `4294967000`, `1000000000000`, `18446744073709551500`.
- repeated searches per sample: `4`.
- Circle server rows: persistent `next-server` requests included.
- `primecount` next-prime rows included for starts at or below `1000000000000`.
- libprimesieve next-prime helper rows included for starts at or below `18446744073709551615`.
- libprimesieve iterator helper rows included for starts at or below `18446744073709551615`.
- libprimecount next-prime helper rows included for starts at or below `1000000000000`.
- required external controls: `primecount`, `primecount-library`, `primesieve`, `primesieve-iterator-library`, `primesieve-library`.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_next_samples_latest.csv`.

| Start | Baseline | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 90 | `primesieve --nth-prime` | 97 | 2 | 4 | 8.903 | 8.658 | 0.973 | 1.151 | stable<br>C n=5, robust/med=1.31, max/med=2.13<br>B n=5, robust/med=1.17, max/med=3.97 | circle_faster |
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 4 | 8.903 | 0.048 | 0.005 | 0.008 | stable<br>C n=5, robust/med=1.31, max/med=2.13<br>B n=5, robust/med=1.04, max/med=813.87 | baseline_faster |
| 90 | `libprimesieve iterator server` | 97 | 2 | 4 | 8.903 | 0.137 | 0.015 | 0.016 | stable<br>C n=5, robust/med=1.31, max/med=2.13<br>B n=5, robust/med=1.23, max/med=731.21 | baseline_faster |
| 90 | `primecount pi+nth-prime` | 97 | 2 | 4 | 8.903 | 30.967 | 3.478 | 3.662 | stable<br>C n=5, robust/med=1.31, max/med=2.13<br>B n=5, robust/med=1.02, max/med=1.19 | circle_faster |
| 90 | `libprimecount pi+nth-prime server` | 97 | 2 | 4 | 8.903 | 0.042 | 0.005 | 0.005 | stable<br>C n=5, robust/med=1.31, max/med=2.13<br>B n=5, robust/med=1.11, max/med=1831.69 | baseline_faster |
| 90 | `primesieve --nth-prime` | 97 | 2 | 4 | 0.035 | 8.658 | 249.459 | 271.882 | stable<br>C n=5, robust/med=1.16, max/med=3.81<br>B n=5, robust/med=1.17, max/med=3.97 | circle_faster |
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 4 | 0.035 | 0.048 | 1.372 | 1.815 | stable<br>C n=5, robust/med=1.16, max/med=3.81<br>B n=5, robust/med=1.04, max/med=813.87 | circle_faster |
| 90 | `libprimesieve iterator server` | 97 | 2 | 4 | 0.035 | 0.137 | 3.954 | 3.880 | stable<br>C n=5, robust/med=1.16, max/med=3.81<br>B n=5, robust/med=1.23, max/med=731.21 | circle_faster |
| 90 | `primecount pi+nth-prime` | 97 | 2 | 4 | 0.035 | 30.967 | 892.211 | 865.050 | stable<br>C n=5, robust/med=1.16, max/med=3.81<br>B n=5, robust/med=1.02, max/med=1.19 | circle_faster |
| 90 | `libprimecount pi+nth-prime server` | 97 | 2 | 4 | 0.035 | 0.042 | 1.221 | 1.192 | stable<br>C n=5, robust/med=1.16, max/med=3.81<br>B n=5, robust/med=1.11, max/med=1831.69 | circle_faster |
| 1000000 | `primesieve --nth-prime` | 1000003 | 2 | 4 | 8.811 | 8.966 | 1.018 | 0.993 | stable<br>C n=5, robust/med=1.09, max/med=1.11<br>B n=5, robust/med=1.02, max/med=1.11 | baseline_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 4 | 8.811 | 0.036 | 0.004 | 0.008 | stable<br>C n=5, robust/med=1.09, max/med=1.11<br>B n=5, robust/med=1.03, max/med=1.17 | baseline_faster |
| 1000000 | `libprimesieve iterator server` | 1000003 | 2 | 4 | 8.811 | 0.152 | 0.017 | 0.018 | stable<br>C n=5, robust/med=1.09, max/med=1.11<br>B n=5, robust/med=1.09, max/med=1.12 | baseline_faster |
| 1000000 | `primecount pi+nth-prime` | 1000003 | 2 | 4 | 8.811 | 31.050 | 3.524 | 3.365 | stable<br>C n=5, robust/med=1.09, max/med=1.11<br>B n=5, robust/med=1.03, max/med=1.16 | circle_faster |
| 1000000 | `libprimecount pi+nth-prime server` | 1000003 | 2 | 4 | 8.811 | 0.103 | 0.012 | 0.012 | stable<br>C n=5, robust/med=1.09, max/med=1.11<br>B n=5, robust/med=1.03, max/med=1.11 | baseline_faster |
| 1000000 | `primesieve --nth-prime` | 1000003 | 2 | 4 | 0.026 | 8.966 | 339.953 | 239.014 | stable<br>C n=5, robust/med=1.02, max/med=1.55<br>B n=5, robust/med=1.02, max/med=1.11 | circle_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 4 | 0.026 | 0.036 | 1.373 | 1.879 | stable<br>C n=5, robust/med=1.02, max/med=1.55<br>B n=5, robust/med=1.03, max/med=1.17 | circle_faster |
| 1000000 | `libprimesieve iterator server` | 1000003 | 2 | 4 | 0.026 | 0.152 | 5.761 | 4.221 | stable<br>C n=5, robust/med=1.02, max/med=1.55<br>B n=5, robust/med=1.09, max/med=1.12 | circle_faster |
| 1000000 | `primecount pi+nth-prime` | 1000003 | 2 | 4 | 0.026 | 31.050 | 1177.235 | 809.801 | stable<br>C n=5, robust/med=1.02, max/med=1.55<br>B n=5, robust/med=1.03, max/med=1.16 | circle_faster |
| 1000000 | `libprimecount pi+nth-prime server` | 1000003 | 2 | 4 | 0.026 | 0.103 | 3.910 | 2.965 | stable<br>C n=5, robust/med=1.02, max/med=1.55<br>B n=5, robust/med=1.03, max/med=1.11 | circle_faster |
| 4294967000 | `primesieve --nth-prime` | 4294967029 | 8 | 4 | 9.143 | 9.157 | 1.001 | 0.983 | stable<br>C n=5, robust/med=1.07, max/med=1.07<br>B n=5, robust/med=1.07, max/med=1.07 | baseline_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 4 | 9.143 | 0.148 | 0.016 | 0.022 | stable<br>C n=5, robust/med=1.07, max/med=1.07<br>B n=5, robust/med=1.05, max/med=1.10 | baseline_faster |
| 4294967000 | `libprimesieve iterator server` | 4294967029 | 8 | 4 | 9.143 | 0.665 | 0.073 | 0.073 | stable<br>C n=5, robust/med=1.07, max/med=1.07<br>B n=5, robust/med=1.07, max/med=1.09 | baseline_faster |
| 4294967000 | `primecount pi+nth-prime` | 4294967029 | 8 | 4 | 9.143 | 37.729 | 4.126 | 3.972 | stable<br>C n=5, robust/med=1.07, max/med=1.07<br>B n=5, robust/med=1.01, max/med=1.41 | circle_faster |
| 4294967000 | `libprimecount pi+nth-prime server` | 4294967029 | 8 | 4 | 9.143 | 5.492 | 0.601 | 0.581 | stable<br>C n=5, robust/med=1.07, max/med=1.07<br>B n=5, robust/med=1.01, max/med=1.08 | baseline_faster |
| 4294967000 | `primesieve --nth-prime` | 4294967029 | 8 | 4 | 0.044 | 9.157 | 206.928 | 176.730 | stable<br>C n=5, robust/med=1.02, max/med=1.04<br>B n=5, robust/med=1.07, max/med=1.07 | circle_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 4 | 0.044 | 0.148 | 3.345 | 3.976 | stable<br>C n=5, robust/med=1.02, max/med=1.04<br>B n=5, robust/med=1.05, max/med=1.10 | circle_faster |
| 4294967000 | `libprimesieve iterator server` | 4294967029 | 8 | 4 | 0.044 | 0.665 | 15.023 | 13.127 | stable<br>C n=5, robust/med=1.02, max/med=1.04<br>B n=5, robust/med=1.07, max/med=1.09 | circle_faster |
| 4294967000 | `primecount pi+nth-prime` | 4294967029 | 8 | 4 | 0.044 | 37.729 | 852.624 | 714.095 | stable<br>C n=5, robust/med=1.02, max/med=1.04<br>B n=5, robust/med=1.01, max/med=1.41 | circle_faster |
| 4294967000 | `libprimecount pi+nth-prime server` | 4294967029 | 8 | 4 | 0.044 | 5.492 | 124.124 | 104.406 | stable<br>C n=5, robust/med=1.02, max/med=1.04<br>B n=5, robust/med=1.01, max/med=1.08 | circle_faster |
| 1000000000000 | `primesieve --nth-prime` | 1000000000039 | 12 | 4 | 9.358 | 10.029 | 1.072 | 1.039 | stable<br>C n=5, robust/med=1.03, max/med=1.16<br>B n=5, robust/med=1.09, max/med=1.09 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 4 | 9.358 | 1.143 | 0.122 | 0.118 | stable<br>C n=5, robust/med=1.03, max/med=1.16<br>B n=5, robust/med=1.01, max/med=1.03 | baseline_faster |
| 1000000000000 | `libprimesieve iterator server` | 1000000000039 | 12 | 4 | 9.358 | 3.911 | 0.418 | 0.410 | stable<br>C n=5, robust/med=1.03, max/med=1.16<br>B n=5, robust/med=1.03, max/med=1.04 | baseline_faster |
| 1000000000000 | `primecount pi+nth-prime` | 1000000000039 | 12 | 4 | 9.358 | 98.673 | 10.544 | 10.440 | stable<br>C n=5, robust/med=1.03, max/med=1.16<br>B n=5, robust/med=1.43, max/med=1.58 | circle_faster |
| 1000000000000 | `libprimecount pi+nth-prime server` | 1000000000039 | 12 | 4 | 9.358 | 36.453 | 3.895 | 3.694 | stable<br>C n=5, robust/med=1.03, max/med=1.16<br>B n=5, robust/med=1.03, max/med=1.05 | circle_faster |
| 1000000000000 | `primesieve --nth-prime` | 1000000000039 | 12 | 4 | 0.062 | 10.029 | 163.073 | 152.053 | stable<br>C n=5, robust/med=1.17, max/med=1.19<br>B n=5, robust/med=1.09, max/med=1.09 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 4 | 0.062 | 1.143 | 18.583 | 17.194 | stable<br>C n=5, robust/med=1.17, max/med=1.19<br>B n=5, robust/med=1.01, max/med=1.03 | circle_faster |
| 1000000000000 | `libprimesieve iterator server` | 1000000000039 | 12 | 4 | 0.062 | 3.911 | 63.601 | 59.928 | stable<br>C n=5, robust/med=1.17, max/med=1.19<br>B n=5, robust/med=1.03, max/med=1.04 | circle_faster |
| 1000000000000 | `primecount pi+nth-prime` | 1000000000039 | 12 | 4 | 0.062 | 98.673 | 1604.446 | 1527.671 | stable<br>C n=5, robust/med=1.17, max/med=1.19<br>B n=5, robust/med=1.43, max/med=1.58 | circle_faster |
| 1000000000000 | `libprimecount pi+nth-prime server` | 1000000000039 | 12 | 4 | 0.062 | 36.453 | 592.732 | 540.582 | stable<br>C n=5, robust/med=1.17, max/med=1.19<br>B n=5, robust/med=1.03, max/med=1.05 | circle_faster |
| 18446744073709551500 | `primesieve --nth-prime` | 18446744073709551521 | 5 | 4 | 9.169 | 3669.693 | 400.217 | 334.530 | stable<br>C n=5, robust/med=1.30, max/med=1.64<br>B n=5, robust/med=1.01, max/med=1.14 | circle_faster |
| 18446744073709551500 | `libprimesieve generate_n_primes server` | 18446744073709551521 | 5 | 4 | 9.169 | 3628.245 | 395.697 | 297.469 | stable<br>C n=5, robust/med=1.30, max/med=1.64<br>B n=5, robust/med=1.12, max/med=1.22 | circle_faster |
| 18446744073709551500 | `libprimesieve iterator server` | 18446744073709551521 | 5 | 4 | 9.169 | 3600.384 | 392.658 | 341.792 | stable<br>C n=5, robust/med=1.30, max/med=1.64<br>B n=5, robust/med=1.08, max/med=2.88 | circle_faster |
| 18446744073709551500 | `primesieve --nth-prime` | 18446744073709551521 | 5 | 4 | 0.110 | 3669.693 | 33360.846 | 27145.241 | noisy<br>C n=5, robust/med=1.58, max/med=1.96<br>B n=5, robust/med=1.01, max/med=1.14 | circle_faster |
| 18446744073709551500 | `libprimesieve generate_n_primes server` | 18446744073709551521 | 5 | 4 | 0.110 | 3628.245 | 32984.045 | 24137.939 | noisy<br>C n=5, robust/med=1.58, max/med=1.96<br>B n=5, robust/med=1.12, max/med=1.22 | circle_faster |
| 18446744073709551500 | `libprimesieve iterator server` | 18446744073709551521 | 5 | 4 | 0.110 | 3600.384 | 32730.760 | 27734.514 | noisy<br>C n=5, robust/med=1.58, max/med=1.96<br>B n=5, robust/med=1.08, max/med=2.88 | circle_faster |

## External Next-Prime Server-Only Search

- `libprimesieve generate_n_primes server` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimesieve iterator server` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve_library_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-next-server`); method `primesieve_generate_n_primes(1, START, UINT64_PRIMES)`.
- `primesieve_iterator_server`: available (`/Users/corbensorenson/Documents/circle math/target/prime-controls/primesieve-iterator-next-server`); method `primesieve::iterator.jump_to(START).next_prime()`.
- `primecount_library_server`: not built (`path unavailable`)
- requested threads: Circle `1`, external `0` (`0` means tool default/all cores).
- next-prime starts: `90`, `1000000`, `4294967000`, `1000000000000`.
- repeated searches per sample: `500`.
- server-only mode: cold CLI rows skipped; persistent Circle `next-server` is compared directly with persistent `libprimesieve`.
- Circle server rows: persistent `next-server` requests included.
- libprimesieve next-prime helper rows included for starts at or below `18446744073709551615`.
- libprimesieve iterator helper rows included for starts at or below `18446744073709551615`.
- required external controls: `primesieve-iterator-library`, `primesieve-library`.
- per-round samples: `sidecars/PRIME_ENGINE/results/prime_engine_external_next_server_samples_latest.csv`.

| Start | Baseline | Prime | Candidates | Batch | Circle ms | Baseline ms | Best Speedup | Median Speedup | Samples | Verdict |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 500 | 0.376 | 0.496 | 1.319 | 1.298 | noisy<br>C n=9, robust/med=1.89, max/med=2.63<br>B n=9, robust/med=1.07, max/med=2.87 | circle_faster |
| 90 | `libprimesieve iterator server` | 97 | 2 | 500 | 0.376 | 12.140 | 32.305 | 32.527 | noisy<br>C n=9, robust/med=1.89, max/med=2.63<br>B n=9, robust/med=1.39, max/med=1.49 | circle_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 500 | 0.394 | 0.956 | 2.424 | 2.384 | stable<br>C n=9, robust/med=1.02, max/med=1.02<br>B n=9, robust/med=1.04, max/med=1.04 | circle_faster |
| 1000000 | `libprimesieve iterator server` | 1000003 | 2 | 500 | 0.394 | 15.524 | 39.356 | 38.485 | stable<br>C n=9, robust/med=1.02, max/med=1.02<br>B n=9, robust/med=1.01, max/med=1.01 | circle_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 500 | 1.537 | 12.533 | 8.155 | 8.178 | stable<br>C n=9, robust/med=1.09, max/med=1.11<br>B n=9, robust/med=1.03, max/med=1.04 | circle_faster |
| 4294967000 | `libprimesieve iterator server` | 4294967029 | 8 | 500 | 1.537 | 57.561 | 37.452 | 37.667 | stable<br>C n=9, robust/med=1.09, max/med=1.11<br>B n=9, robust/med=1.02, max/med=1.97 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 500 | 3.361 | 139.372 | 41.462 | 45.320 | stable<br>C n=9, robust/med=1.08, max/med=1.83<br>B n=9, robust/med=1.25, max/med=1.67 | circle_faster |
| 1000000000000 | `libprimesieve iterator server` | 1000000000039 | 12 | 500 | 3.361 | 490.139 | 145.813 | 141.853 | stable<br>C n=9, robust/med=1.08, max/med=1.83<br>B n=9, robust/med=1.31, max/med=1.34 | circle_faster |

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
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.083 | 0.095 | 113.308 | 101.559 | stable<br>C n=7, robust/med=1.09, max/med=2.28<br>B n=7, robust/med=1.12, max/med=1.35 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.083 | 0.095 | 22.606 | 19.892 | stable<br>C n=7, robust/med=1.09, max/med=2.28<br>B n=7, robust/med=1.01, max/med=1.07 | circle_faster |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.093 | 0.106 | 120.591 | 117.544 | stable<br>C n=7, robust/med=1.18, max/med=1.19<br>B n=7, robust/med=1.09, max/med=1.21 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.093 | 0.106 | 21.902 | 19.457 | noisy<br>C n=7, robust/med=1.18, max/med=1.19<br>B n=7, robust/med=1.56, max/med=1.56 | circle_faster |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 379.964 | 383.861 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.12 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 47.239 | 41.745 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.30 | circle_faster |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.118 | 974.067 | 914.448 | noisy<br>C n=7, robust/med=1.68, max/med=1.85<br>B n=7, robust/med=1.17, max/med=1.18 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.118 | 89.987 | 87.611 | noisy<br>C n=7, robust/med=1.68, max/med=1.85<br>B n=7, robust/med=1.02, max/med=1.37 | circle_faster |

Best hot-server candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.083 | 0.090 | 113.097 | 107.354 | stable<br>C n=7, robust/med=1.04, max/med=1.22<br>B n=7, robust/med=1.12, max/med=1.35 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.083 | 0.090 | 22.564 | 21.027 | stable<br>C n=7, robust/med=1.04, max/med=1.22<br>B n=7, robust/med=1.01, max/med=1.07 | circle_faster |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.084 | 0.094 | 132.488 | 132.137 | stable<br>C n=7, robust/med=1.33, max/med=1.56<br>B n=7, robust/med=1.09, max/med=1.21 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.084 | 0.094 | 24.063 | 21.873 | noisy<br>C n=7, robust/med=1.33, max/med=1.56<br>B n=7, robust/med=1.56, max/med=1.56 | circle_faster |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 379.964 | 383.861 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.12 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 47.239 | 41.745 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.30 | circle_faster |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.100 | 0.109 | 1013.755 | 988.559 | noisy<br>C n=7, robust/med=1.71, max/med=8.98<br>B n=7, robust/med=1.17, max/med=1.18 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.100 | 0.109 | 93.653 | 94.711 | noisy<br>C n=7, robust/med=1.71, max/med=8.98<br>B n=7, robust/med=1.02, max/med=1.37 | circle_faster |

High-offset hot-server candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.083 | 0.090 | 113.097 | 107.354 | stable<br>C n=7, robust/med=1.04, max/med=1.22<br>B n=7, robust/med=1.12, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.083 | 0.095 | 113.308 | 101.559 | stable<br>C n=7, robust/med=1.09, max/med=2.28<br>B n=7, robust/med=1.12, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.086 | 0.097 | 109.196 | 100.074 | stable<br>C n=7, robust/med=1.08, max/med=3.14<br>B n=7, robust/med=1.12, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3 | 0.100 | 0.104 | 93.973 | 93.112 | stable<br>C n=7, robust/med=1.24, max/med=2.55<br>B n=7, robust/med=1.12, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.084 | 0.105 | 110.928 | 92.613 | stable<br>C n=7, robust/med=1.33, max/med=2.35<br>B n=7, robust/med=1.12, max/med=1.35 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.083 | 0.090 | 22.564 | 21.027 | stable<br>C n=7, robust/med=1.04, max/med=1.22<br>B n=7, robust/med=1.01, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.083 | 0.095 | 22.606 | 19.892 | stable<br>C n=7, robust/med=1.09, max/med=2.28<br>B n=7, robust/med=1.01, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.086 | 0.097 | 21.786 | 19.601 | stable<br>C n=7, robust/med=1.08, max/med=3.14<br>B n=7, robust/med=1.01, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_3t`<br>mode: `presieve17` | 4194304 | 3 | 0.100 | 0.104 | 18.749 | 18.238 | stable<br>C n=7, robust/med=1.24, max/med=2.55<br>B n=7, robust/med=1.01, max/med=1.07 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.084 | 0.105 | 22.131 | 18.140 | stable<br>C n=7, robust/med=1.33, max/med=2.35<br>B n=7, robust/med=1.01, max/med=1.07 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.084 | 0.094 | 132.488 | 132.137 | stable<br>C n=7, robust/med=1.33, max/med=1.56<br>B n=7, robust/med=1.09, max/med=1.21 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.093 | 0.106 | 120.591 | 117.544 | stable<br>C n=7, robust/med=1.18, max/med=1.19<br>B n=7, robust/med=1.09, max/med=1.21 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3 | 0.104 | 0.106 | 107.661 | 117.091 | noisy<br>C n=7, robust/med=1.58, max/med=2.84<br>B n=7, robust/med=1.09, max/med=1.21 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.097 | 0.107 | 115.471 | 115.992 | stable<br>C n=7, robust/med=1.07, max/med=4.02<br>B n=7, robust/med=1.09, max/med=1.21 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 115.715 | 114.654 | stable<br>C n=7, robust/med=1.05, max/med=1.17<br>B n=7, robust/med=1.09, max/med=1.21 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.084 | 0.094 | 24.063 | 21.873 | noisy<br>C n=7, robust/med=1.33, max/med=1.56<br>B n=7, robust/med=1.56, max/med=1.56 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.093 | 0.106 | 21.902 | 19.457 | noisy<br>C n=7, robust/med=1.18, max/med=1.19<br>B n=7, robust/med=1.56, max/med=1.56 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_3t`<br>mode: `presieve13` | 4194304 | 3 | 0.104 | 0.106 | 19.554 | 19.382 | noisy<br>C n=7, robust/med=1.58, max/med=2.84<br>B n=7, robust/med=1.56, max/med=1.56 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.097 | 0.107 | 20.972 | 19.200 | noisy<br>C n=7, robust/med=1.07, max/med=4.02<br>B n=7, robust/med=1.56, max/med=1.56 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 21.017 | 18.979 | noisy<br>C n=7, robust/med=1.05, max/med=1.17<br>B n=7, robust/med=1.56, max/med=1.56 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 379.964 | 383.861 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.12 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.085 | 0.096 | 356.323 | 383.603 | stable<br>C n=7, robust/med=1.16, max/med=1.32<br>B n=7, robust/med=1.04, max/med=1.12 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.094 | 0.097 | 323.269 | 378.727 | stable<br>C n=7, robust/med=1.04, max/med=1.13<br>B n=7, robust/med=1.04, max/med=1.12 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.089 | 0.099 | 341.630 | 373.176 | stable<br>C n=7, robust/med=1.05, max/med=1.13<br>B n=7, robust/med=1.04, max/med=1.12 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.089 | 0.099 | 340.641 | 372.391 | stable<br>C n=7, robust/med=1.07, max/med=1.09<br>B n=7, robust/med=1.04, max/med=1.12 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.080 | 0.096 | 47.239 | 41.745 | stable<br>C n=7, robust/med=1.13, max/med=1.21<br>B n=7, robust/med=1.04, max/med=1.30 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.085 | 0.096 | 44.300 | 41.717 | stable<br>C n=7, robust/med=1.16, max/med=1.32<br>B n=7, robust/med=1.04, max/med=1.30 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.094 | 0.097 | 40.190 | 41.187 | stable<br>C n=7, robust/med=1.04, max/med=1.13<br>B n=7, robust/med=1.04, max/med=1.30 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.089 | 0.099 | 42.473 | 40.583 | stable<br>C n=7, robust/med=1.05, max/med=1.13<br>B n=7, robust/med=1.04, max/med=1.30 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.089 | 0.099 | 42.350 | 40.498 | stable<br>C n=7, robust/med=1.07, max/med=1.09<br>B n=7, robust/med=1.04, max/med=1.30 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.100 | 0.109 | 1013.755 | 988.559 | noisy<br>C n=7, robust/med=1.71, max/med=8.98<br>B n=7, robust/med=1.17, max/med=1.18 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.118 | 974.067 | 914.448 | noisy<br>C n=7, robust/med=1.68, max/med=1.85<br>B n=7, robust/med=1.17, max/med=1.18 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.114 | 0.118 | 891.563 | 913.948 | stable<br>C n=7, robust/med=1.29, max/med=1.35<br>B n=7, robust/med=1.17, max/med=1.18 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.099 | 0.119 | 1024.129 | 905.695 | noisy<br>C n=7, robust/med=1.55, max/med=1.90<br>B n=7, robust/med=1.17, max/med=1.18 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.093 | 0.119 | 1098.012 | 904.350 | stable<br>C n=7, robust/med=1.27, max/med=1.61<br>B n=7, robust/med=1.17, max/med=1.18 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.100 | 0.109 | 93.653 | 94.711 | noisy<br>C n=7, robust/med=1.71, max/med=8.98<br>B n=7, robust/med=1.02, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.118 | 89.987 | 87.611 | noisy<br>C n=7, robust/med=1.68, max/med=1.85<br>B n=7, robust/med=1.02, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.114 | 0.118 | 82.365 | 87.563 | stable<br>C n=7, robust/med=1.29, max/med=1.35<br>B n=7, robust/med=1.02, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.099 | 0.119 | 94.611 | 86.772 | noisy<br>C n=7, robust/med=1.55, max/med=1.90<br>B n=7, robust/med=1.02, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.093 | 0.119 | 101.437 | 86.644 | stable<br>C n=7, robust/med=1.27, max/med=1.61<br>B n=7, robust/med=1.02, max/med=1.37 |

## High-Offset Count Binary

Focused rows: `8`; median wins: `7/8`; best-time wins: `7/8`.
Probe shape: rounds `11`, batch `20`, warmup `2`.
- `circle-prime-count`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime-count`; sha `0a312e87d84d`, size `1395216` bytes).
- standalone `circle-prime-count` rows included.
- slim `circle-prime-count count-server` rows included.
- libprimesieve count-server rows included.
- libprimecount pi-server rows included.

| Lane | Range | Circle Row | Baseline | Circle Median ms | Baseline Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| cold count binary vs primesieve CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | `primesieve CLI count` | 7.248 | 5.987 | 0.884 | 0.826 | noisy<br>C n=11, robust/med=1.62, max/med=1.96<br>B n=11, robust/med=2.09, max/med=5.13 | baseline_faster |
| cold count binary vs primecount CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | `primecount CLI pi diff` | 7.248 | 57.421 | 5.931 | 7.923 | noisy<br>C n=11, robust/med=1.62, max/med=1.96<br>B n=11, robust/med=1.42, max/med=1.50 | circle_faster |
| slim count binary server vs primesieve CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | `primesieve CLI count` | 0.145 | 5.987 | 45.521 | 41.344 | noisy<br>C n=11, robust/med=5.22, max/med=9.45<br>B n=11, robust/med=2.09, max/med=5.13 | circle_faster |
| slim count binary server vs primecount CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | `primecount CLI pi diff` | 0.145 | 57.421 | 305.568 | 396.560 | noisy<br>C n=11, robust/med=5.22, max/med=9.45<br>B n=11, robust/med=1.42, max/med=1.50 | circle_faster |
| slim count binary server vs libprimesieve | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | `libprimesieve count server` | 0.145 | 2.091 | 18.360 | 14.442 | noisy<br>C n=11, robust/med=5.22, max/med=9.45<br>B n=11, robust/med=1.24, max/med=2.87 | circle_faster |
| slim count binary server vs libprimecount | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | `libprimecount pi server` | 0.145 | 13.129 | 100.525 | 90.672 | noisy<br>C n=11, robust/med=5.22, max/med=9.45<br>B n=11, robust/med=1.54, max/med=2.16 | circle_faster |
| hot server vs libprimesieve | [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | `libprimesieve count server` | 0.130 | 2.091 | 18.238 | 16.144 | noisy<br>C n=11, robust/med=2.89, max/med=8.86<br>B n=11, robust/med=1.24, max/med=2.87 | circle_faster |
| hot server vs libprimecount | [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | `libprimecount pi server` | 0.130 | 13.129 | 99.861 | 101.360 | noisy<br>C n=11, robust/med=2.89, max/med=8.86<br>B n=11, robust/med=1.54, max/med=2.16 | circle_faster |

Cold-binary overhead diagnosis:

| Range | Cold Count Binary Median ms | Hot Count Binary Server Median ms | Circle Cold/Hot | Circle Extra ms | primesieve CLI/lib | Cold vs primesieve | Hot count binary vs libprimesieve |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [1000000000000, 1000010000000) | 7.248 | 0.145 | 50.05x | 7.103 | 2.86x | 0.826 | 14.442 |

## High-Offset Count-Binary Mode/Segment Sweep

Requested Circle segment sizes: `0`, `1310720`, `1441792`, `1507328`, `1572864`, `1638400`, `1835008`, `4194304`, `3670016`.
Circle count modes: `default`, `segmented`, `balanced`, `dynamic`, `presieve13`, `presieve17`.
Rounds per row: `9`.

Cold one-shot count-binary candidate readout:

Trial requires median gain over default at least `1.030x`, candidate median speedup at least `1.000x`, and candidate best-time speedup at least `1.000x` versus cold `primesieve`.

| Range | Default | Default Median/Best | Best Candidate | Candidate Median/Best | Median Gain | Sweep Action | Confirmation | Final Action |
| --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |
| [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13`<br>segment: `1507328`, threads: `7/8` | 0.893x / 0.854x | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13`<br>segment: `1572864`, threads: `7/8` | 0.872x / 0.888x | 0.98x | `keep_default` | `all` `hold_small_gain_candidate`<br>0.962x / 0.911x, gain 1.03x | `keep_default` |

Adaptive count-binary mode/segment scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.109 | 0.179 | 43.161 | 33.196 | stable<br>C n=9, robust/med=1.39, max/med=1.79<br>B n=9, robust/med=1.29, max/med=2.69 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.109 | 0.179 | 18.515 | 13.448 | noisy<br>C n=9, robust/med=1.39, max/med=1.79<br>B n=9, robust/med=1.68, max/med=1.84 | circle_faster |

Best count-binary mode/segment candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 0.099 | 0.129 | 47.584 | 46.177 | stable<br>C n=9, robust/med=1.25, max/med=1.45<br>B n=9, robust/med=1.29, max/med=2.69 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 0.099 | 0.129 | 20.412 | 18.706 | noisy<br>C n=9, robust/med=1.25, max/med=1.45<br>B n=9, robust/med=1.68, max/med=1.84 | circle_faster |

High-offset count-binary mode/segment candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 0.099 | 0.129 | 47.584 | 46.177 | stable<br>C n=9, robust/med=1.25, max/med=1.45<br>B n=9, robust/med=1.29, max/med=2.69 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 0.094 | 0.129 | 49.791 | 46.072 | stable<br>C n=9, robust/med=1.42, max/med=2.65<br>B n=9, robust/med=1.29, max/med=2.69 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 0.108 | 0.130 | 43.481 | 45.816 | noisy<br>C n=9, robust/med=1.65, max/med=1.80<br>B n=9, robust/med=1.29, max/med=2.69 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.111 | 0.131 | 42.247 | 45.510 | stable<br>C n=9, robust/med=1.45, max/med=1.87<br>B n=9, robust/med=1.29, max/med=2.69 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 0.089 | 0.135 | 52.529 | 44.118 | stable<br>C n=9, robust/med=1.19, max/med=1.39<br>B n=9, robust/med=1.29, max/med=2.69 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 0.099 | 0.129 | 20.412 | 18.706 | noisy<br>C n=9, robust/med=1.25, max/med=1.45<br>B n=9, robust/med=1.68, max/med=1.84 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 0.094 | 0.129 | 21.359 | 18.664 | noisy<br>C n=9, robust/med=1.42, max/med=2.65<br>B n=9, robust/med=1.68, max/med=1.84 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7/8 | 0.108 | 0.130 | 18.652 | 18.560 | noisy<br>C n=9, robust/med=1.65, max/med=1.80<br>B n=9, robust/med=1.68, max/med=1.84 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.111 | 0.131 | 18.123 | 18.436 | noisy<br>C n=9, robust/med=1.45, max/med=1.87<br>B n=9, robust/med=1.68, max/med=1.84 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 0.089 | 0.135 | 22.533 | 17.872 | noisy<br>C n=9, robust/med=1.19, max/med=1.39<br>B n=9, robust/med=1.68, max/med=1.84 |

## High-Offset Count-Binary Candidate Confirmation

Requested Circle segment sizes: `0`, `1507328`, `1572864`.
Circle count modes: `default`, `presieve13`.
Rounds per row: `17`.

Cold one-shot count-binary candidate readout:

Trial requires median gain over default at least `1.030x`, candidate median speedup at least `1.000x`, and candidate best-time speedup at least `1.000x` versus cold `primesieve`.

| Range | Default | Default Median/Best | Best Candidate | Candidate Median/Best | Median Gain | Action |
| --- | --- | ---: | --- | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13`<br>segment: `1507328`, threads: `7/8` | 0.933x / 0.912x | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13`<br>segment: `1572864`, threads: `7/8` | 0.962x / 0.911x | 1.03x | `hold_small_gain_candidate` |

Focused cold default scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.935 | 5.808 | 0.912 | 0.933 | stable<br>C n=17, robust/med=1.32, max/med=1.77<br>B n=17, robust/med=1.47, max/med=1.89 | baseline_faster |

Focused cold candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 4.937 | 5.637 | 0.911 | 0.962 | noisy<br>C n=17, robust/med=1.83, max/med=2.04<br>B n=17, robust/med=1.47, max/med=1.89 | baseline_faster |

Focused cold candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 4.937 | 5.637 | 0.911 | 0.962 | noisy<br>C n=17, robust/med=1.83, max/med=2.04<br>B n=17, robust/med=1.47, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.935 | 5.808 | 0.912 | 0.933 | stable<br>C n=17, robust/med=1.32, max/med=1.77<br>B n=17, robust/med=1.47, max/med=1.89 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 4.909 | 5.980 | 0.916 | 0.907 | stable<br>C n=17, robust/med=1.13, max/med=2.54<br>B n=17, robust/med=1.47, max/med=1.89 |

## High-Offset Shifted Hot-Server Scorecard

Requested Circle segment sizes: `0`, `1507328`, `1638400`, `1441792`.
Circle count modes: `default`, `presieve13`, `segmented`.
Rounds per row: `13`.

Adaptive default shifted scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.325 | 1.577 | 7.054 | 7.674 | stable<br>C n=13, robust/med=1.31, max/med=1.41<br>B n=13, robust/med=1.17, max/med=1.56 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.325 | 1.577 | 1.416 | 1.286 | noisy<br>C n=13, robust/med=1.31, max/med=1.41<br>B n=13, robust/med=1.62, max/med=1.75 | circle_faster |

Best shifted candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.409 | 1.565 | 6.630 | 7.734 | noisy<br>C n=13, robust/med=1.68, max/med=1.82<br>B n=13, robust/med=1.17, max/med=1.56 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.409 | 1.565 | 1.331 | 1.296 | noisy<br>C n=13, robust/med=1.68, max/med=1.82<br>B n=13, robust/med=1.62, max/med=1.75 | circle_faster |

High-offset shifted candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.409 | 1.565 | 6.630 | 7.734 | noisy<br>C n=13, robust/med=1.68, max/med=1.82<br>B n=13, robust/med=1.17, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7 | 1.415 | 1.567 | 6.605 | 7.720 | stable<br>C n=13, robust/med=1.50, max/med=1.63<br>B n=13, robust/med=1.17, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.325 | 1.577 | 7.054 | 7.674 | stable<br>C n=13, robust/med=1.31, max/med=1.41<br>B n=13, robust/med=1.17, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7 | 1.381 | 1.805 | 6.764 | 6.703 | stable<br>C n=13, robust/med=1.49, max/med=1.77<br>B n=13, robust/med=1.17, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7 | 1.906 | 2.648 | 4.904 | 4.570 | noisy<br>C n=13, robust/med=1.88, max/med=1.95<br>B n=13, robust/med=1.17, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.409 | 1.565 | 1.331 | 1.296 | noisy<br>C n=13, robust/med=1.68, max/med=1.82<br>B n=13, robust/med=1.62, max/med=1.75 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7 | 1.415 | 1.567 | 1.326 | 1.294 | noisy<br>C n=13, robust/med=1.50, max/med=1.63<br>B n=13, robust/med=1.62, max/med=1.75 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.325 | 1.577 | 1.416 | 1.286 | noisy<br>C n=13, robust/med=1.31, max/med=1.41<br>B n=13, robust/med=1.62, max/med=1.75 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7 | 1.381 | 1.805 | 1.358 | 1.123 | noisy<br>C n=13, robust/med=1.49, max/med=1.77<br>B n=13, robust/med=1.62, max/med=1.75 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7 | 1.906 | 2.648 | 0.984 | 0.766 | noisy<br>C n=13, robust/med=1.88, max/med=1.95<br>B n=13, robust/med=1.62, max/med=1.75 |

## High-Offset Shifted Count-Binary Scorecard

Requested Circle segment sizes: `0`.
Circle count modes: `default`.
Rounds per row: `13`.

Adaptive shifted count-binary scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.794 | 2.158 | 8.593 | 10.616 | stable<br>C n=13, robust/med=1.33, max/med=1.33<br>B n=13, robust/med=1.18, max/med=1.56 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.794 | 2.158 | 1.146 | 1.227 | noisy<br>C n=13, robust/med=1.33, max/med=1.33<br>B n=13, robust/med=1.68, max/med=1.72 | circle_faster |

High-offset shifted count-binary candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.794 | 2.158 | 8.593 | 10.616 | stable<br>C n=13, robust/med=1.33, max/med=1.33<br>B n=13, robust/med=1.18, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.707 | 2.313 | 9.033 | 9.902 | stable<br>C n=13, robust/med=1.39, max/med=1.53<br>B n=13, robust/med=1.18, max/med=1.56 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.794 | 2.158 | 1.146 | 1.227 | noisy<br>C n=13, robust/med=1.33, max/med=1.33<br>B n=13, robust/med=1.68, max/med=1.72 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.707 | 2.313 | 1.205 | 1.145 | noisy<br>C n=13, robust/med=1.39, max/med=1.53<br>B n=13, robust/med=1.68, max/med=1.72 |

## Competitive Smoke Scorecard

Requested Circle segment sizes: `0`.
Circle count modes: `default`.
Rounds per row: `13`.

Fresh shifted count-binary smoke scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.425 | 1.635 | 7.558 | 8.749 | stable<br>C n=13, robust/med=1.29, max/med=1.32<br>B n=13, robust/med=1.24, max/med=1.29 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.425 | 1.635 | 1.417 | 1.364 | stable<br>C n=13, robust/med=1.29, max/med=1.32<br>B n=13, robust/med=1.29, max/med=2.28 | circle_faster |

Competitive smoke candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.425 | 1.635 | 7.558 | 8.749 | stable<br>C n=13, robust/med=1.29, max/med=1.32<br>B n=13, robust/med=1.24, max/med=1.29 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 1.425 | 1.635 | 1.417 | 1.364 | stable<br>C n=13, robust/med=1.29, max/med=1.32<br>B n=13, robust/med=1.29, max/med=2.28 |

## High-Offset Shifted Candidate Readout

Shifted candidates require at least `1.050x` median gain over the adaptive default before this readout marks them as trial-ready for fresh-interval optimization.
Artifact profile: `shifted`, batch `80`, shift `10000000`, rounds `13`.

| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Action |
| --- | --- | --- | ---: | --- | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1310720 (8) | 7.674 | `presieve13` 1507328 (7) | 7.734 | 1.008x | `hold_small_gain_candidate` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` 1310720 (8) | 1.286 | `presieve13` 1507328 (7) | 1.296 | 1.008x | `hold_small_gain_candidate` |

## High-Offset Promotion Readout

Confirmed non-default candidates require at least `1.050x` median gain over the current adaptive default and fresh candidate-confirmation evidence before this readout marks them as trial-ready.

| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Default Confirm | Candidate Confirm | Candidate Freshness | Action |
| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1507328 (7/8) | 101.559 | `presieve13` 1310720 (8) | 107.354 | 1.057x | `missing` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` 1507328 (7/8) | 19.892 | `presieve13` 1310720 (8) | 21.027 | 1.057x | `confirmed` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `presieve17` 1310720 (8) | 117.544 | `segmented` 1310720 (8) | 132.137 | 1.124x | `missing` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` 1310720 (8) | 19.457 | `segmented` 1310720 (8) | 21.873 | 1.124x | `confirmed` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1310720 (8) | 383.861 | `presieve13` 1310720 (8) | 383.861 | 1.000x | `missing` | `missing` | `missing` | `keep_default` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` 1310720 (8) | 41.745 | `presieve13` 1310720 (8) | 41.745 | 1.000x | `unconfirmed` | `missing` | `missing` | `keep_default` |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1310720 (8) | 914.448 | `presieve13` 1310720 (8) | 988.559 | 1.081x | `missing` | `missing` | `missing` | `keep_default` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` 1310720 (8) | 87.611 | `presieve13` 1310720 (8) | 94.711 | 1.081x | `unconfirmed` | `confirmed` | `stale` | `keep_default` |

## High-Offset Promotion Focus Confirmation

Observed groups: `1`; confirmed: `0`; unconfirmed: `1`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `40`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 1/2 | 2/2 | 0.060 | 39.998 | `unconfirmed` |

## High-Offset Confirmation

Observed groups: `4`; confirmed: `2`; unconfirmed: `2`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `80`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 1507328 | 7/8 | 3/2 | 3/3 | 0.032, 0.024, 0.030 | 74.331, 78.958, 67.264 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8 | 3/2 | 3/3 | 0.028, 0.025, 0.027 | 78.149, 84.217, 89.444 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 1/2 | 1/3 | 0.028, 0.035, 0.035 | 147.052, 150.918, 120.838 | `unconfirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 1/2 | 1/3 | 0.030, 0.047, 0.038 | 372.018, 326.063, 297.813 | `unconfirmed` |

## High-Offset Candidate Confirmation

Observed groups: `4`; confirmed: `1`; unconfirmed: `3`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `80`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8 | 1/2 | 2/3 | 2.048 | 1.276 | `unconfirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 1/2 | 2/3 | 1.760, 2.150 | 1.444, 1.241 | `unconfirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 1/2 | 3/3 | 1.926 | 2.232 | `unconfirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 2/2 | 3/3 | 2.437, 2.348 | 5.156, 4.792 | `confirmed` |

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

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 10000000) | `external_primesieve_count` | `dynamic` | 196608 | 8 | 0/2 | 0/2 | 3.104 | - | `unconfirmed` |
| [0, 100000000) | `external_primesieve_count` | `dynamic` | 98304 | 8 | 0/2 | 0/2 | 6.974 | - | `unconfirmed` |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `segmented` | 3145728 | 4/8 | 2/2 | 2/2 | 6.188, 6.214 | - | `confirmed` |

## External Throughput

Requested Circle segment sizes: `0`, `131072`, `196608`, `262144`, `524288`.
Circle count modes: `default`, `segmented`, `prefix-pi`.
Rounds per row: `5`.

Adaptive default scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 0.814 | 0.846 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.05, max/med=3.22 | baseline_faster |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 3.477 | 3.895 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.03, max/med=1.07 | circle_faster |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 2.830 | 2.989 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.02, max/med=1.33 | circle_faster |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 1.164 | 1.110 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.11, max/med=2.01 | circle_faster |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 3.247 | 2.945 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.09, max/med=1.12 | circle_faster |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 2.399 | 2.772 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.03, max/med=1.14 | circle_faster |

Prefix-pi thread comparison:

| Range | Baseline | Serial Row | Default Row | Serial ms | Default ms | Median Ratio | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` (2/8) | 10.116 | 8.899 | 1.137 | `default_faster` |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` (2/8) | 10.116 | 8.899 | 1.137 | `default_faster` |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` (1) | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` (2/8) | 10.116 | 8.899 | 1.137 | `default_faster` |

Best candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 0.814 | 0.846 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.05, max/med=3.22 | baseline_faster |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 3.477 | 3.895 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.03, max/med=1.07 | circle_faster |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 2.830 | 2.989 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.02, max/med=1.33 | circle_faster |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 1.107 | 1.129 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.11, max/med=2.01 | circle_faster |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 3.088 | 2.995 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.09, max/med=1.12 | circle_faster |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 2.282 | 2.819 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.03, max/med=1.14 | circle_faster |

Throughput segment candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 0.814 | 0.846 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.05, max/med=3.22 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 6.001 | 6.286 | 0.790 | 0.796 | stable<br>C n=5, robust/med=1.07, max/med=1.11<br>B n=5, robust/med=1.05, max/med=3.22 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 39.265 | 43.926 | 0.121 | 0.114 | stable<br>C n=5, robust/med=1.07, max/med=1.12<br>B n=5, robust/med=1.05, max/med=3.22 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 131072 | 8 | 44.133 | 45.955 | 0.107 | 0.109 | stable<br>C n=5, robust/med=1.07, max/med=1.13<br>B n=5, robust/med=1.05, max/med=3.22 |
| [0, 1000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 43.279 | 50.134 | 0.110 | 0.100 | stable<br>C n=5, robust/med=1.06, max/med=1.21<br>B n=5, robust/med=1.05, max/med=3.22 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 3.477 | 3.895 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.03, max/med=1.07 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 6.001 | 6.286 | 3.376 | 3.664 | stable<br>C n=5, robust/med=1.07, max/med=1.11<br>B n=5, robust/med=1.03, max/med=1.07 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 39.265 | 43.926 | 0.516 | 0.524 | stable<br>C n=5, robust/med=1.07, max/med=1.12<br>B n=5, robust/med=1.03, max/med=1.07 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 131072 | 8 | 44.133 | 45.955 | 0.459 | 0.501 | stable<br>C n=5, robust/med=1.07, max/med=1.13<br>B n=5, robust/med=1.03, max/med=1.07 |
| [0, 1000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 43.279 | 50.134 | 0.468 | 0.459 | stable<br>C n=5, robust/med=1.06, max/med=1.21<br>B n=5, robust/med=1.03, max/med=1.07 |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_default_count`<br>mode: `prefix-pi` | 262144 | 1/8 | 5.826 | 5.913 | 2.830 | 2.989 | stable<br>C n=5, robust/med=1.13, max/med=1.17<br>B n=5, robust/med=1.02, max/med=1.33 |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 6.001 | 6.286 | 2.747 | 2.811 | stable<br>C n=5, robust/med=1.07, max/med=1.11<br>B n=5, robust/med=1.02, max/med=1.33 |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 39.265 | 43.926 | 0.420 | 0.402 | stable<br>C n=5, robust/med=1.07, max/med=1.12<br>B n=5, robust/med=1.02, max/med=1.33 |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 131072 | 8 | 44.133 | 45.955 | 0.374 | 0.385 | stable<br>C n=5, robust/med=1.07, max/med=1.13<br>B n=5, robust/med=1.02, max/med=1.33 |
| [0, 1000000000) | `external_primesieve_count_server` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 43.279 | 50.134 | 0.381 | 0.353 | stable<br>C n=5, robust/med=1.06, max/med=1.21<br>B n=5, robust/med=1.02, max/med=1.33 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 1.107 | 1.129 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.11, max/med=2.01 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 1.164 | 1.110 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.11, max/med=2.01 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 9.729 | 10.116 | 0.937 | 0.976 | stable<br>C n=5, robust/med=1.04, max/med=1.06<br>B n=5, robust/med=1.11, max/med=2.01 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 48.315 | 55.457 | 0.189 | 0.178 | stable<br>C n=5, robust/med=1.01, max/med=1.08<br>B n=5, robust/med=1.11, max/med=2.01 |
| [1000000000, 2000000000) | `external_primecount_pi_diff` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 50.630 | 56.554 | 0.180 | 0.175 | stable<br>C n=5, robust/med=1.04, max/med=1.11<br>B n=5, robust/med=1.11, max/med=2.01 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 3.088 | 2.995 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.09, max/med=1.12 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 3.247 | 2.945 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.09, max/med=1.12 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 9.729 | 10.116 | 2.614 | 2.591 | stable<br>C n=5, robust/med=1.04, max/med=1.06<br>B n=5, robust/med=1.09, max/med=1.12 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 48.315 | 55.457 | 0.526 | 0.473 | stable<br>C n=5, robust/med=1.01, max/med=1.08<br>B n=5, robust/med=1.09, max/med=1.12 |
| [1000000000, 2000000000) | `external_primesieve_count` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 50.630 | 56.554 | 0.502 | 0.463 | stable<br>C n=5, robust/med=1.04, max/med=1.11<br>B n=5, robust/med=1.09, max/med=1.12 |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_prefix_pi_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 8.236 | 8.751 | 2.282 | 2.819 | stable<br>C n=5, robust/med=1.01, max/med=1.04<br>B n=5, robust/med=1.03, max/med=1.14 |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_default_count_2t`<br>mode: `prefix-pi` | 262144 | 2/8 | 7.834 | 8.899 | 2.399 | 2.772 | stable<br>C n=5, robust/med=1.02, max/med=1.14<br>B n=5, robust/med=1.03, max/med=1.14 |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_prefix_pi_count`<br>mode: `prefix-pi` | 262144 | 1 | 9.729 | 10.116 | 1.932 | 2.438 | stable<br>C n=5, robust/med=1.04, max/med=1.06<br>B n=5, robust/med=1.03, max/med=1.14 |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 262144 | 8 | 48.315 | 55.457 | 0.389 | 0.445 | stable<br>C n=5, robust/med=1.01, max/med=1.08<br>B n=5, robust/med=1.03, max/med=1.14 |
| [1000000000, 2000000000) | `external_primesieve_count_server` | `circle_prime_parallel_segmented_count_8t`<br>mode: `segmented` | 196608 | 8 | 50.630 | 56.554 | 0.371 | 0.436 | stable<br>C n=5, robust/med=1.04, max/med=1.11<br>B n=5, robust/med=1.03, max/med=1.14 |

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

Recommendations: `5`; aligned: `4`; within tolerance: `1`; drift: `0`; noisy drift: `0`; unconfirmed mode drift: `0`; missing evidence: `0`.
Tolerance: `0.050` median slowdown.

| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1 -> 1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=15, robust/med=2.28, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=15, robust/med=1.25, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1507328 | 1507328 | 7/8 -> 7/8 | 0.024 | noisy<br>effective stable<br>C n=27, robust/med=1.66, max/med=3.60<br>B n=27, robust/med=1.85, max/med=1.89<br>mode confirmed 3/2 | 1.000x | `aligned` |
| [1500000000000, 1500010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve17` | `presieve17` | 1310720 | 1310720 | 8 -> 8 | 0.025 | stable<br>C n=27, robust/med=1.30, max/med=1.35<br>B n=27, robust/med=1.25, max/med=1.51<br>mode confirmed 3/2 | 1.000x | `aligned` |

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
| 10000000 | `high_offset_segmented_range_count` | 4194304 | 5.749 | 361726 |
| 10000000 | `parallel_high_offset_segmented_range_count_8t` | 1507328 | 2.663 | 361726 |
| 10000000 | `parallel_high_offset_default_range_count_8t` | 1507328 | 2.526 | 361726 |
| 10000000 | `parallel_high_offset_balanced_segmented_range_count_8t` | 1507328 | 2.573 | 361726 |
| 10000000 | `high_offset_presieve13_range_count` | 1507328 | 6.481 | 361726 |
| 10000000 | `parallel_high_offset_presieve13_range_count_8t` | 1507328 | 2.163 | 361726 |
| 10000000 | `high_offset_presieve17_range_count` | 1507328 | 6.205 | 361726 |
| 10000000 | `parallel_high_offset_presieve17_range_count_8t` | 1507328 | 2.169 | 361726 |
| 10000000 | `high_offset_bitpacked_range_count` | 1507328 | 7.226 | 361726 |
| 10000000 | `high_offset_tracked_byte_range_count` | 1507328 | 17.592 | 361726 |
| 10000000 | `high_offset_wheel30_range_count` | 1507328 | 50.382 | 361726 |
| 10000000 | `high_offset_wheel30_mark_range_count` | 1507328 | 7.058 | 361726 |
| 10000000 | `parallel_high_offset_wheel30_mark_range_count_8t` | 1507328 | 4.492 | 361726 |
| 10000000 | `high_offset_hybrid_wheel30_mark_range_count` | 1507328 | 8.450 | 361726 |
| 10000000 | `parallel_high_offset_hybrid_wheel30_mark_range_count_8t` | 1507328 | 5.541 | 361726 |
| 100000 | `high_offset_u64_scalar_fallback_range_count` | 64 | 46.728 | 2139 |
| 100000 | `high_offset_u64_scalar_naive_control_count` | 0 | 47.236 | 2139 |
| 10000000 | `cold_external_primesieve_high_offset_count_8t` | 0 | 4.643 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1507328 | 2.473 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_segmented_count_8t` | 1507328 | 2.741 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1507328 | 1.891 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve17_count_8t` | 1507328 | 2.080 | 361726 |
| 1000000 | `cold_process_segmented_range_count` | 262144 | 3.263 | 78498 |
| 10000000 | `cold_process_segmented_range_count` | 262144 | 4.470 | 664579 |
| 10000000 | `cold_process_parallel_segmented_range_count_8t` | 65536 | 4.121 | 664579 |
| 10000000 | `cold_cli_parallel_default_range_count_8t` | 65536 | 2.191 | 664579 |
| 100000000 | `cold_process_parallel_segmented_range_count_8t` | 196608 | 9.627 | 5761455 |
| 100000000 | `cold_cli_parallel_default_range_count_8t` | 196608 | 1.843 | 5761455 |
| 0 | `cold_process_high_offset_noop_worker` | 0 | 1.891 | 0 |
| 10000000 | `cold_process_high_offset_default_plan_8t` | 1507328 | 1.551 | 7 |
| 0 | `cold_count_binary_high_offset_noop` | 0 | 1.329 | 0 |
| 10000000 | `cold_count_binary_high_offset_default_plan_8t` | 1507328 | 1.302 | 7 |
| 10000000 | `cold_process_parallel_high_offset_default_range_count_1t` | 1507328 | 9.599 | 361726 |
| 10000000 | `cold_process_parallel_high_offset_segmented_range_count_8t` | 1507328 | 6.868 | 361726 |
| 10000000 | `cold_process_parallel_high_offset_default_range_count_8t` | 1507328 | 4.249 | 361726 |
| 10000000 | `cold_cli_parallel_high_offset_default_range_count_8t` | 1507328 | 4.413 | 361726 |
| 10000000 | `cold_count_binary_parallel_high_offset_default_range_count_8t` | 1507328 | 5.540 | 361726 |

High-offset cold/hot overhead (source: `high_offset_hot_cold`):

| Workload | Hot Row | Hot ms | Server Row | Count Server ms | Server / Hot | Server / Cold Count Binary | Cold Count Binary ms | Count Binary / Hot | Full CLI ms | Minimal Default Process ms | Segmented Process ms |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10000000 | `parallel_high_offset_presieve13_range_count_8t` | 2.163 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | 0.87x | 0.34x | 5.540 | 2.56x | 4.413 | 4.249 | 6.868 |

High-offset cold diagnostics:

| Workload | Bench Noop ms | Bench Plan ms | Count Binary Noop ms | Count Binary Plan ms | Serial Default ms | Count Binary ms | Count Binary - Server ms | Noop Share | Residual After Noop ms | Next Action | primesieve Cold ms | Count Binary / primesieve |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 10000000 | 1.891 | 1.551 | 1.329 | 1.302 | 9.599 | 5.540 | 3.649 | 0.36x | 2.320 | `thread_first_touch_reduction_required` | 4.643 | 1.19x |

High-offset server/external best-time comparison:

| Workload | Server Row | Server ms | Baseline | Baseline Best ms | Server Speedup | Cold CLI ms | Cold CLI Speedup |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primecount_pi_diff` | 28.860 | 15.262 | 5.169 | 5.584 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primecount_pi_diff` | 28.860 | 15.262 | 0.091 | 317.931 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primecount_pi_diff_server` | 9.314 | 4.925 | 5.169 | 1.802 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primecount_pi_diff_server` | 9.314 | 4.925 | 0.091 | 102.601 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primesieve_count` | 4.305 | 2.276 | 5.169 | 0.833 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primesieve_count` | 4.305 | 2.276 | 0.091 | 47.422 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primesieve_count_server` | 1.883 | 0.996 | 5.169 | 0.364 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1.891 | `external_primesieve_count_server` | 1.883 | 0.996 | 0.091 | 20.740 |

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
