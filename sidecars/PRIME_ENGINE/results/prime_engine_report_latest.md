# Prime Engine Report

Generated: `2026-06-22T01:24:41Z`

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

- `primesieve` cold CLI: Circle faster on 3/4 rows by best time; median faster on 3/4 rows.
- `primesieve` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimesieve count server` external server: Circle faster on 5/8 rows by best time; median faster on 5/8 rows.
- `primecount` cold CLI: Circle faster on 3/4 rows by best time; median faster on 3/4 rows.
- `primecount` server: Circle faster on 4/4 rows by best time; median faster on 4/4 rows.
- `libprimecount pi server` external server: Circle faster on 5/8 rows by best time; median faster on 5/8 rows.

Tool metadata:
- `circle_prime`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`)
- `primesieve`: primesieve 12.14, <https://github.com/kimwalisch/primesieve> (`/opt/homebrew/bin/primesieve`)
- `primecount`: primecount 8.5, <https://github.com/kimwalisch/primecount> (`/opt/homebrew/bin/primecount`)
- `circle_count_server`: available (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime`); method `persistent count-server requests`.
- `circle_count_server` small-prefix `pi` cache: limit `2000000000`; default `2000000000`; max `3000000000`; env `CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT`; scope prefix-pi count-server ranges with HIGH-1 at or below the limit.
- `circle_count_server` small-prefix `pi` cache memory: estimated bytes `187500004`; default bytes `187500004`; max bytes `281250004`.
- `circle_count_server` small-prefix `pi` cache startup warmup: min `6479.784 ms`; median `6659.060 ms`; max `6779.564 ms`; samples `3`.
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
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1.163 | 1.213 | stable<br>C n=7, robust/med=1.11, max/med=1.13<br>B n=7, robust/med=1.03, max/med=1.23 | circle_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1006.035 | 689.463 | stable<br>C n=7, robust/med=1.14, max/med=1.16<br>B n=7, robust/med=1.03, max/med=1.23 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.651 | 1.643 | stable<br>C n=7, robust/med=1.11, max/med=1.13<br>B n=7, robust/med=1.12, max/med=1.13 | circle_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1427.967 | 934.095 | stable<br>C n=7, robust/med=1.14, max/med=1.16<br>B n=7, robust/med=1.12, max/med=1.13 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.153 | 0.150 | stable<br>C n=7, robust/med=1.11, max/med=1.13<br>B n=7, robust/med=1.01, max/med=1.04 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 132.595 | 85.406 | stable<br>C n=7, robust/med=1.14, max/med=1.16<br>B n=7, robust/med=1.01, max/med=1.04 | circle_faster |
| [0, 10000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.006 | 0.006 | stable<br>C n=7, robust/med=1.11, max/med=1.13<br>B n=7, robust/med=1.02, max/med=1.95 | baseline_faster |
| [0, 10000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 4.983 | 3.315 | stable<br>C n=7, robust/med=1.14, max/med=1.16<br>B n=7, robust/med=1.02, max/med=1.95 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1.775 | 1.729 | stable<br>C n=7, robust/med=1.14, max/med=1.22<br>B n=7, robust/med=1.12, max/med=1.22 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 1660.088 | 1050.129 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.12, max/med=1.22 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1.586 | 1.552 | stable<br>C n=7, robust/med=1.14, max/med=1.22<br>B n=7, robust/med=1.21, max/med=1.21 | circle_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1483.670 | 942.402 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.21, max/med=1.21 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 0.707 | 0.688 | stable<br>C n=7, robust/med=1.14, max/med=1.22<br>B n=7, robust/med=1.07, max/med=1.13 | baseline_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 661.058 | 417.894 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.07, max/med=1.13 | circle_faster |
| [0, 100000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.023 | 0.023 | stable<br>C n=7, robust/med=1.14, max/med=1.22<br>B n=7, robust/med=1.01, max/med=1.09 | baseline_faster |
| [0, 100000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 21.872 | 13.703 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.01, max/med=1.09 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 3.734 | 3.319 | stable<br>C n=7, robust/med=1.27, max/med=1.58<br>B n=7, robust/med=1.27, max/med=1.32 | circle_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count` (threads: 8) | 6532.417 | 5141.698 | noisy<br>C n=7, robust/med=1.79, max/med=3.65<br>B n=7, robust/med=1.27, max/med=1.32 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 0.824 | 0.989 | stable<br>C n=7, robust/med=1.27, max/med=1.58<br>B n=7, robust/med=1.37, max/med=1.42 | baseline_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff` (threads: 8) | 1442.138 | 1532.093 | noisy<br>C n=7, robust/med=1.79, max/med=3.65<br>B n=7, robust/med=1.37, max/med=1.42 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 3.141 | 2.459 | stable<br>C n=7, robust/med=1.27, max/med=1.58<br>B n=7, robust/med=1.10, max/med=1.30 | circle_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primesieve_count_server` (threads: 8) | 5494.592 | 3809.890 | noisy<br>C n=7, robust/med=1.79, max/med=3.65<br>B n=7, robust/med=1.10, max/med=1.30 | circle_faster |
| [0, 1000000000) | `circle_prime_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 0.050 | 0.038 | noisy<br>C n=7, robust/med=1.27, max/med=1.58<br>B n=7, robust/med=2.04, max/med=3.28 | baseline_faster |
| [0, 1000000000) | `circle_prime_server_default_count`<br>mode: `prefix-pi` (threads: 1/8) | `external_primecount_pi_diff_server` (threads: 8) | 87.708 | 59.153 | noisy<br>C n=7, robust/med=1.79, max/med=3.65<br>B n=7, robust/med=2.04, max/med=3.28 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primesieve_count` (threads: 8) | 0.916 | 0.925 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.05, max/med=1.22 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primesieve_count` (threads: 8) | 43.003 | 44.759 | stable<br>C n=7, robust/med=1.25, max/med=1.66<br>B n=7, robust/med=1.05, max/med=1.22 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primecount_pi_diff` (threads: 8) | 5.332 | 6.046 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.12, max/med=1.17 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primecount_pi_diff` (threads: 8) | 250.415 | 292.575 | stable<br>C n=7, robust/med=1.25, max/med=1.66<br>B n=7, robust/med=1.12, max/med=1.17 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primesieve_count_server` (threads: 8) | 0.339 | 0.319 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.19, max/med=1.20 | baseline_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primesieve_count_server` (threads: 8) | 15.906 | 15.420 | stable<br>C n=7, robust/med=1.25, max/med=1.66<br>B n=7, robust/med=1.19, max/med=1.20 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primecount_pi_diff_server` (threads: 8) | 1.768 | 1.859 | stable<br>C n=7, robust/med=1.02, max/med=1.08<br>B n=7, robust/med=1.01, max/med=1.03 | circle_faster |
| [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` (threads: 5/8) | `external_primecount_pi_diff_server` (threads: 8) | 83.035 | 89.960 | stable<br>C n=7, robust/med=1.25, max/med=1.66<br>B n=7, robust/med=1.01, max/med=1.03 | circle_faster |

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
| 90 | `libprimesieve generate_n_primes server` | 97 | 2 | 500 | 0.371 | 0.479 | 1.290 | 1.283 | stable<br>C n=9, robust/med=1.02, max/med=1.10<br>B n=9, robust/med=1.15, max/med=1.49 | circle_faster |
| 90 | `libprimesieve iterator server` | 97 | 2 | 500 | 0.371 | 11.640 | 31.385 | 30.294 | stable<br>C n=9, robust/med=1.02, max/med=1.10<br>B n=9, robust/med=1.01, max/med=1.02 | circle_faster |
| 1000000 | `libprimesieve generate_n_primes server` | 1000003 | 2 | 500 | 0.376 | 0.910 | 2.420 | 2.390 | stable<br>C n=9, robust/med=1.02, max/med=1.07<br>B n=9, robust/med=1.03, max/med=1.24 | circle_faster |
| 1000000 | `libprimesieve iterator server` | 1000003 | 2 | 500 | 0.376 | 14.745 | 39.208 | 38.192 | noisy<br>C n=9, robust/med=1.02, max/med=1.07<br>B n=9, robust/med=1.59, max/med=2.35 | circle_faster |
| 4294967000 | `libprimesieve generate_n_primes server` | 4294967029 | 8 | 500 | 1.490 | 12.147 | 8.150 | 8.176 | stable<br>C n=9, robust/med=1.08, max/med=1.28<br>B n=9, robust/med=1.11, max/med=1.40 | circle_faster |
| 4294967000 | `libprimesieve iterator server` | 4294967029 | 8 | 500 | 1.490 | 53.471 | 35.875 | 36.269 | stable<br>C n=9, robust/med=1.08, max/med=1.28<br>B n=9, robust/med=1.33, max/med=1.81 | circle_faster |
| 1000000000000 | `libprimesieve generate_n_primes server` | 1000000000039 | 12 | 500 | 3.243 | 132.176 | 40.761 | 45.154 | stable<br>C n=9, robust/med=1.06, max/med=1.06<br>B n=9, robust/med=1.18, max/med=1.27 | circle_faster |
| 1000000000000 | `libprimesieve iterator server` | 1000000000039 | 12 | 500 | 3.243 | 470.450 | 145.079 | 154.140 | stable<br>C n=9, robust/med=1.06, max/med=1.06<br>B n=9, robust/med=1.17, max/med=1.29 | circle_faster |

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
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` | 2097152 | 5/8 | 0.118 | 0.189 | 154.066 | 105.214 | stable<br>C n=7, robust/med=1.40, max/med=1.66<br>B n=7, robust/med=1.01, max/med=1.05 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` | 2097152 | 5/8 | 0.118 | 0.189 | 19.186 | 12.815 | stable<br>C n=7, robust/med=1.40, max/med=1.66<br>B n=7, robust/med=1.19, max/med=1.20 | circle_faster |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.104 | 0.180 | 217.367 | 137.761 | stable<br>C n=7, robust/med=1.49, max/med=1.60<br>B n=7, robust/med=1.11, max/med=1.35 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.104 | 0.180 | 23.516 | 17.821 | stable<br>C n=7, robust/med=1.49, max/med=1.60<br>B n=7, robust/med=1.04, max/med=1.28 | circle_faster |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.109 | 0.136 | 281.161 | 275.919 | noisy<br>C n=7, robust/med=1.67, max/med=2.06<br>B n=7, robust/med=1.21, max/med=3.65 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.109 | 0.136 | 35.809 | 37.712 | noisy<br>C n=7, robust/med=1.67, max/med=2.06<br>B n=7, robust/med=1.16, max/med=1.27 | circle_faster |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 1296.022 | 1513.839 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.29, max/med=1.31 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 100.418 | 115.146 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.32, max/med=1.37 | circle_faster |

Best hot-server candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.106 | 0.127 | 172.507 | 156.159 | stable<br>C n=7, robust/med=1.24, max/med=1.87<br>B n=7, robust/med=1.01, max/med=1.05 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.106 | 0.127 | 21.483 | 19.019 | stable<br>C n=7, robust/med=1.24, max/med=1.87<br>B n=7, robust/med=1.19, max/med=1.20 | circle_faster |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.119 | 0.138 | 190.871 | 178.948 | stable<br>C n=7, robust/med=1.15, max/med=1.32<br>B n=7, robust/med=1.11, max/med=1.35 | circle_faster |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.119 | 0.138 | 20.649 | 23.150 | stable<br>C n=7, robust/med=1.15, max/med=1.32<br>B n=7, robust/med=1.04, max/med=1.28 | circle_faster |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.098 | 0.112 | 311.844 | 334.031 | noisy<br>C n=7, robust/med=1.65, max/med=2.48<br>B n=7, robust/med=1.21, max/med=3.65 | circle_faster |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.098 | 0.112 | 39.717 | 45.654 | noisy<br>C n=7, robust/med=1.65, max/med=2.48<br>B n=7, robust/med=1.16, max/med=1.27 | circle_faster |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 1296.022 | 1513.839 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.29, max/med=1.31 | circle_faster |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 100.418 | 115.146 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.32, max/med=1.37 | circle_faster |

High-offset hot-server candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.106 | 0.127 | 172.507 | 156.159 | stable<br>C n=7, robust/med=1.24, max/med=1.87<br>B n=7, robust/med=1.01, max/med=1.05 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.092 | 0.139 | 197.800 | 142.917 | stable<br>C n=7, robust/med=1.21, max/med=1.33<br>B n=7, robust/med=1.01, max/med=1.05 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.098 | 0.154 | 185.284 | 129.086 | stable<br>C n=7, robust/med=1.48, max/med=1.65<br>B n=7, robust/med=1.01, max/med=1.05 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4 | 0.087 | 0.166 | 210.042 | 119.705 | stable<br>C n=7, robust/med=1.46, max/med=2.06<br>B n=7, robust/med=1.01, max/med=1.05 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.117 | 0.170 | 156.027 | 117.185 | stable<br>C n=7, robust/med=1.28, max/med=1.67<br>B n=7, robust/med=1.01, max/med=1.05 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.106 | 0.127 | 21.483 | 19.019 | stable<br>C n=7, robust/med=1.24, max/med=1.87<br>B n=7, robust/med=1.19, max/med=1.20 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.092 | 0.139 | 24.632 | 17.407 | stable<br>C n=7, robust/med=1.21, max/med=1.33<br>B n=7, robust/med=1.19, max/med=1.20 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.098 | 0.154 | 23.074 | 15.722 | stable<br>C n=7, robust/med=1.48, max/med=1.65<br>B n=7, robust/med=1.19, max/med=1.20 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_4t`<br>mode: `presieve13` | 3145728 | 4 | 0.087 | 0.166 | 26.157 | 14.580 | stable<br>C n=7, robust/med=1.46, max/med=2.06<br>B n=7, robust/med=1.19, max/med=1.20 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.117 | 0.170 | 19.430 | 14.273 | stable<br>C n=7, robust/med=1.28, max/med=1.67<br>B n=7, robust/med=1.19, max/med=1.20 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.119 | 0.138 | 190.871 | 178.948 | stable<br>C n=7, robust/med=1.15, max/med=1.32<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.122 | 0.143 | 186.597 | 172.573 | noisy<br>C n=7, robust/med=1.54, max/med=1.67<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.126 | 0.159 | 180.036 | 155.852 | stable<br>C n=7, robust/med=1.36, max/med=1.59<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.133 | 0.168 | 171.205 | 147.663 | stable<br>C n=7, robust/med=1.20, max/med=1.41<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.092 | 0.173 | 245.640 | 143.278 | stable<br>C n=7, robust/med=1.15, max/med=1.29<br>B n=7, robust/med=1.11, max/med=1.35 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.119 | 0.138 | 20.649 | 23.150 | stable<br>C n=7, robust/med=1.15, max/med=1.32<br>B n=7, robust/med=1.04, max/med=1.28 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.122 | 0.143 | 20.187 | 22.325 | noisy<br>C n=7, robust/med=1.54, max/med=1.67<br>B n=7, robust/med=1.04, max/med=1.28 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.126 | 0.159 | 19.477 | 20.162 | stable<br>C n=7, robust/med=1.36, max/med=1.59<br>B n=7, robust/med=1.04, max/med=1.28 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.133 | 0.168 | 18.522 | 19.102 | stable<br>C n=7, robust/med=1.20, max/med=1.41<br>B n=7, robust/med=1.04, max/med=1.28 |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.092 | 0.173 | 26.574 | 18.535 | stable<br>C n=7, robust/med=1.15, max/med=1.29<br>B n=7, robust/med=1.04, max/med=1.28 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.098 | 0.112 | 311.844 | 334.031 | noisy<br>C n=7, robust/med=1.65, max/med=2.48<br>B n=7, robust/med=1.21, max/med=3.65 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.125 | 294.352 | 299.979 | stable<br>C n=7, robust/med=1.24, max/med=1.95<br>B n=7, robust/med=1.21, max/med=3.65 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.109 | 0.136 | 281.161 | 275.919 | noisy<br>C n=7, robust/med=1.67, max/med=2.06<br>B n=7, robust/med=1.21, max/med=3.65 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.107 | 0.139 | 286.186 | 269.360 | stable<br>C n=7, robust/med=1.47, max/med=1.53<br>B n=7, robust/med=1.21, max/med=3.65 |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.107 | 0.142 | 287.336 | 263.402 | stable<br>C n=7, robust/med=1.15, max/med=1.20<br>B n=7, robust/med=1.21, max/med=3.65 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.098 | 0.112 | 39.717 | 45.654 | noisy<br>C n=7, robust/med=1.65, max/med=2.48<br>B n=7, robust/med=1.16, max/med=1.27 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.104 | 0.125 | 37.489 | 41.000 | stable<br>C n=7, robust/med=1.24, max/med=1.95<br>B n=7, robust/med=1.16, max/med=1.27 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.109 | 0.136 | 35.809 | 37.712 | noisy<br>C n=7, robust/med=1.67, max/med=2.06<br>B n=7, robust/med=1.16, max/med=1.27 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.107 | 0.139 | 36.449 | 36.815 | stable<br>C n=7, robust/med=1.47, max/med=1.53<br>B n=7, robust/med=1.16, max/med=1.27 |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.107 | 0.142 | 36.595 | 36.001 | stable<br>C n=7, robust/med=1.15, max/med=1.20<br>B n=7, robust/med=1.16, max/med=1.27 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 1296.022 | 1513.839 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.29, max/med=1.31 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.092 | 0.127 | 1369.739 | 1307.632 | stable<br>C n=7, robust/med=1.37, max/med=1.48<br>B n=7, robust/med=1.29, max/med=1.31 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.090 | 0.129 | 1406.263 | 1281.354 | stable<br>C n=7, robust/med=1.25, max/med=1.25<br>B n=7, robust/med=1.29, max/med=1.31 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.108 | 0.133 | 1163.707 | 1240.964 | stable<br>C n=7, robust/med=1.18, max/med=1.53<br>B n=7, robust/med=1.29, max/med=1.31 |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.111 | 0.138 | 1135.975 | 1200.716 | stable<br>C n=7, robust/med=1.31, max/med=1.72<br>B n=7, robust/med=1.29, max/med=1.31 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_8t`<br>mode: `presieve13` | 1310720 | 8 | 0.097 | 0.109 | 100.418 | 115.146 | stable<br>C n=7, robust/med=1.43, max/med=1.61<br>B n=7, robust/med=1.32, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_8t`<br>mode: `segmented` | 1310720 | 8 | 0.092 | 0.127 | 106.129 | 99.461 | stable<br>C n=7, robust/med=1.37, max/med=1.48<br>B n=7, robust/med=1.32, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve17_count_8t`<br>mode: `presieve17` | 1310720 | 8 | 0.090 | 0.129 | 108.959 | 97.462 | stable<br>C n=7, robust/med=1.25, max/med=1.25<br>B n=7, robust/med=1.32, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.108 | 0.133 | 90.166 | 94.390 | stable<br>C n=7, robust/med=1.18, max/med=1.53<br>B n=7, robust/med=1.32, max/med=1.37 |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7/8 | 0.111 | 0.138 | 88.017 | 91.329 | stable<br>C n=7, robust/med=1.31, max/med=1.72<br>B n=7, robust/med=1.32, max/med=1.37 |

## High-Offset Count Binary

Focused rows: `8`; median wins: `7/8`; best-time wins: `7/8`.
Probe shape: rounds `11`, batch `20`, warmup `2`.
- `circle-prime-count`: 0.1.0 (`/Users/corbensorenson/Documents/circle math/target/release/circle-prime-count`; sha `51c1702280ad`, size `1395152` bytes).
- standalone `circle-prime-count` rows included.
- slim `circle-prime-count count-server` rows included.
- libprimesieve count-server rows included.
- libprimecount pi-server rows included.

| Lane | Range | Circle Row | Baseline | Circle Median ms | Baseline Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| cold count binary vs primesieve CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_5t`<br>mode: `presieve13` | `primesieve CLI count` | 5.749 | 4.867 | 0.822 | 0.847 | stable<br>C n=11, robust/med=1.14, max/med=1.18<br>B n=11, robust/med=1.11, max/med=1.60 | baseline_faster |
| cold count binary vs primecount CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_5t`<br>mode: `presieve13` | `primecount CLI pi diff` | 5.749 | 35.789 | 5.570 | 6.226 | stable<br>C n=11, robust/med=1.14, max/med=1.18<br>B n=11, robust/med=1.26, max/med=1.37 | circle_faster |
| slim count binary server vs primesieve CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_5t`<br>mode: `presieve13` | `primesieve CLI count` | 0.129 | 4.867 | 41.605 | 37.765 | stable<br>C n=11, robust/med=1.11, max/med=1.26<br>B n=11, robust/med=1.11, max/med=1.60 | circle_faster |
| slim count binary server vs primecount CLI | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_5t`<br>mode: `presieve13` | `primecount CLI pi diff` | 0.129 | 35.789 | 282.050 | 277.701 | stable<br>C n=11, robust/med=1.11, max/med=1.26<br>B n=11, robust/med=1.26, max/med=1.37 | circle_faster |
| slim count binary server vs libprimesieve | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_5t`<br>mode: `presieve13` | `libprimesieve count server` | 0.129 | 1.997 | 17.938 | 15.494 | stable<br>C n=11, robust/med=1.11, max/med=1.26<br>B n=11, robust/med=1.04, max/med=1.35 | circle_faster |
| slim count binary server vs libprimecount | [1000000000000, 1000010000000) | `circle_prime_count_binary_server_parallel_default_count_5t`<br>mode: `presieve13` | `libprimecount pi server` | 0.129 | 11.208 | 89.177 | 86.968 | stable<br>C n=11, robust/med=1.11, max/med=1.26<br>B n=11, robust/med=1.16, max/med=1.32 | circle_faster |
| hot server vs libprimesieve | [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` | `libprimesieve count server` | 0.127 | 1.997 | 17.096 | 15.668 | stable<br>C n=11, robust/med=1.13, max/med=1.13<br>B n=11, robust/med=1.04, max/med=1.35 | circle_faster |
| hot server vs libprimecount | [1000000000000, 1000010000000) | `circle_prime_server_parallel_default_count_5t`<br>mode: `presieve13` | `libprimecount pi server` | 0.127 | 11.208 | 84.989 | 87.945 | stable<br>C n=11, robust/med=1.13, max/med=1.13<br>B n=11, robust/med=1.16, max/med=1.32 | circle_faster |

Cold-binary overhead diagnosis:

| Range | Cold Count Binary Median ms | Hot Count Binary Server Median ms | Circle Cold/Hot | Circle Extra ms | primesieve CLI/lib | Cold vs primesieve | Hot count binary vs libprimesieve |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [1000000000000, 1000010000000) | 5.749 | 0.129 | 44.61x | 5.620 | 2.44x | 0.847 | 15.494 |

## High-Offset Count-Binary Mode/Segment Sweep

Requested Circle segment sizes: `0`, `1507328`, `1835008`, `2097152`, `2621440`, `3145728`, `4194304`, `8388608`, `10000000`.
Circle count modes: `default`, `presieve13`.
Rounds per row: `11`.

Adaptive count-binary mode/segment scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.087 | 0.104 | 51.329 | 52.810 | stable<br>C n=11, robust/med=1.46, max/med=1.74<br>B n=11, robust/med=1.31, max/med=1.39 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.087 | 0.104 | 21.606 | 18.876 | stable<br>C n=11, robust/med=1.46, max/med=1.74<br>B n=11, robust/med=1.29, max/med=1.47 | circle_faster |

High-offset count-binary mode/segment candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.087 | 0.104 | 51.329 | 52.810 | stable<br>C n=11, robust/med=1.46, max/med=1.74<br>B n=11, robust/med=1.31, max/med=1.39 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 0.092 | 0.113 | 48.536 | 48.600 | noisy<br>C n=11, robust/med=1.52, max/med=1.56<br>B n=11, robust/med=1.31, max/med=1.39 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.101 | 0.118 | 43.997 | 46.706 | stable<br>C n=11, robust/med=1.41, max/med=1.56<br>B n=11, robust/med=1.31, max/med=1.39 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 0.098 | 0.120 | 45.445 | 46.024 | stable<br>C n=11, robust/med=1.45, max/med=1.66<br>B n=11, robust/med=1.31, max/med=1.39 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_server_parallel_presieve13_count_4t`<br>mode: `presieve13` | 2621440 | 4 | 0.116 | 0.125 | 38.521 | 44.110 | stable<br>C n=11, robust/med=1.27, max/med=1.62<br>B n=11, robust/med=1.31, max/med=1.39 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 0.087 | 0.104 | 21.606 | 18.876 | stable<br>C n=11, robust/med=1.46, max/med=1.74<br>B n=11, robust/med=1.29, max/med=1.47 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 0.092 | 0.113 | 20.430 | 17.372 | noisy<br>C n=11, robust/med=1.52, max/med=1.56<br>B n=11, robust/med=1.29, max/med=1.47 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_5t`<br>mode: `presieve13` | 2097152 | 5 | 0.101 | 0.118 | 18.520 | 16.694 | stable<br>C n=11, robust/med=1.41, max/med=1.56<br>B n=11, robust/med=1.29, max/med=1.47 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 0.098 | 0.120 | 19.129 | 16.451 | stable<br>C n=11, robust/med=1.45, max/med=1.66<br>B n=11, robust/med=1.29, max/med=1.47 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_presieve13_count_4t`<br>mode: `presieve13` | 2621440 | 4 | 0.116 | 0.125 | 16.215 | 15.767 | stable<br>C n=11, robust/med=1.27, max/med=1.62<br>B n=11, robust/med=1.29, max/med=1.47 |

## High-Offset Count-Binary Candidate Confirmation

Requested Circle segment sizes: `0`, `1572864`, `1835008`.
Circle count modes: `default`, `presieve13`.
Rounds per row: `17`.

Cold one-shot count-binary candidate readout:

Trial requires median gain over default at least `1.030x`, candidate median speedup at least `1.000x`, and candidate best-time speedup at least `1.000x` versus cold `primesieve`.

| Range | Default | Default Median/Best | Best Candidate | Candidate Median/Best | Median Gain | Action |
| --- | --- | ---: | --- | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13`<br>segment: `1507328`, threads: `7/8` | 0.901x / 0.876x | `circle_prime_count_binary_parallel_presieve13_count_6t`<br>mode: `presieve13`<br>segment: `1835008`, threads: `6` | 0.918x / 0.884x | 1.02x | `hold_small_gain_candidate` |

Focused cold default scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 5.037 | 5.476 | 0.876 | 0.901 | stable<br>C n=17, robust/med=1.41, max/med=1.47<br>B n=17, robust/med=1.43, max/med=1.48 | baseline_faster |

Focused cold candidate scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 4.990 | 5.370 | 0.884 | 0.918 | stable<br>C n=17, robust/med=1.40, max/med=1.91<br>B n=17, robust/med=1.43, max/med=1.48 | baseline_faster |

Focused cold candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_6t`<br>mode: `presieve13` | 1835008 | 6 | 4.990 | 5.370 | 0.884 | 0.918 | stable<br>C n=17, robust/med=1.40, max/med=1.91<br>B n=17, robust/med=1.43, max/med=1.48 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_default_count_7t`<br>mode: `presieve13` | 1507328 | 7/8 | 5.037 | 5.476 | 0.876 | 0.901 | stable<br>C n=17, robust/med=1.41, max/med=1.47<br>B n=17, robust/med=1.43, max/med=1.48 |
| [1000000000000, 1000010000000) | `external_primesieve_count` | `circle_prime_count_binary_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1572864 | 7/8 | 5.069 | 5.477 | 0.870 | 0.900 | stable<br>C n=17, robust/med=1.35, max/med=1.42<br>B n=17, robust/med=1.43, max/med=1.48 |

## High-Offset Shifted Hot-Server Scorecard

Requested Circle segment sizes: `0`, `1507328`, `1638400`, `1441792`.
Circle count modes: `default`, `presieve13`, `segmented`.
Rounds per row: `13`.

Adaptive default shifted scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.611 | 1.785 | 5.241 | 5.537 | stable<br>C n=13, robust/med=1.24, max/med=1.29<br>B n=13, robust/med=1.12, max/med=1.32 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.611 | 1.785 | 1.167 | 1.083 | stable<br>C n=13, robust/med=1.24, max/med=1.29<br>B n=13, robust/med=1.10, max/med=1.13 | circle_faster |

High-offset shifted candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.611 | 1.785 | 5.241 | 5.537 | stable<br>C n=13, robust/med=1.24, max/med=1.29<br>B n=13, robust/med=1.12, max/med=1.32 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.588 | 1.845 | 5.317 | 5.356 | stable<br>C n=13, robust/med=1.13, max/med=1.27<br>B n=13, robust/med=1.12, max/med=1.32 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7 | 1.558 | 1.849 | 5.419 | 5.345 | stable<br>C n=13, robust/med=1.34, max/med=1.48<br>B n=13, robust/med=1.12, max/med=1.32 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7 | 1.583 | 1.965 | 5.332 | 5.029 | stable<br>C n=13, robust/med=1.14, max/med=1.34<br>B n=13, robust/med=1.12, max/med=1.32 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7 | 1.797 | 2.016 | 4.697 | 4.902 | stable<br>C n=13, robust/med=1.17, max/med=1.42<br>B n=13, robust/med=1.12, max/med=1.32 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.611 | 1.785 | 1.167 | 1.083 | stable<br>C n=13, robust/med=1.24, max/med=1.29<br>B n=13, robust/med=1.10, max/med=1.13 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1507328 | 7 | 1.588 | 1.845 | 1.184 | 1.048 | stable<br>C n=13, robust/med=1.13, max/med=1.27<br>B n=13, robust/med=1.10, max/med=1.13 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1638400 | 7 | 1.558 | 1.849 | 1.207 | 1.046 | stable<br>C n=13, robust/med=1.34, max/med=1.48<br>B n=13, robust/med=1.10, max/med=1.13 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_presieve13_count_7t`<br>mode: `presieve13` | 1441792 | 7 | 1.583 | 1.965 | 1.187 | 0.984 | stable<br>C n=13, robust/med=1.14, max/med=1.34<br>B n=13, robust/med=1.10, max/med=1.13 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_segmented_count_7t`<br>mode: `segmented` | 1507328 | 7 | 1.797 | 2.016 | 1.046 | 0.959 | stable<br>C n=13, robust/med=1.17, max/med=1.42<br>B n=13, robust/med=1.10, max/med=1.13 |

## High-Offset Shifted Count-Binary Scorecard

Requested Circle segment sizes: `0`.
Circle count modes: `default`.
Rounds per row: `13`.

Adaptive shifted count-binary scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.470 | 1.820 | 6.613 | 6.486 | stable<br>C n=13, robust/med=1.39, max/med=2.36<br>B n=13, robust/med=1.43, max/med=1.63 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.470 | 1.820 | 1.320 | 1.220 | stable<br>C n=13, robust/med=1.39, max/med=2.36<br>B n=13, robust/med=1.38, max/med=1.80 | circle_faster |

High-offset shifted count-binary candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.470 | 1.820 | 6.613 | 6.486 | stable<br>C n=13, robust/med=1.39, max/med=2.36<br>B n=13, robust/med=1.43, max/med=1.63 |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.744 | 2.293 | 5.574 | 5.150 | noisy<br>C n=13, robust/med=1.59, max/med=3.81<br>B n=13, robust/med=1.43, max/med=1.63 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.470 | 1.820 | 1.320 | 1.220 | stable<br>C n=13, robust/med=1.39, max/med=2.36<br>B n=13, robust/med=1.38, max/med=1.80 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.744 | 2.293 | 1.113 | 0.969 | noisy<br>C n=13, robust/med=1.59, max/med=3.81<br>B n=13, robust/med=1.38, max/med=1.80 |

## Competitive Smoke Scorecard

Requested Circle segment sizes: `0`.
Circle count modes: `default`.
Rounds per row: `13`.

Fresh shifted count-binary smoke scorecard:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples | Verdict |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.344 | 1.450 | 7.058 | 7.332 | stable<br>C n=13, robust/med=1.37, max/med=1.60<br>B n=13, robust/med=1.33, max/med=1.38 | circle_faster |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.344 | 1.450 | 1.408 | 1.351 | stable<br>C n=13, robust/med=1.37, max/med=1.60<br>B n=13, robust/med=1.33, max/med=1.42 | circle_faster |

Competitive smoke candidate spread:

| Range | Baseline | Circle Row | Segment | Threads | Best ms | Median ms | Best Speedup | Median Speedup | Samples |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.344 | 1.450 | 7.058 | 7.332 | stable<br>C n=13, robust/med=1.37, max/med=1.60<br>B n=13, robust/med=1.33, max/med=1.38 |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `circle_prime_count_binary_server_parallel_default_count_7t`<br>mode: `presieve13` | 1638400 | 7/8 | 1.344 | 1.450 | 1.408 | 1.351 | stable<br>C n=13, robust/med=1.37, max/med=1.60<br>B n=13, robust/med=1.33, max/med=1.42 |

## High-Offset Shifted Candidate Readout

Shifted candidates require at least `1.050x` median gain over the adaptive default before this readout marks them as trial-ready for fresh-interval optimization.
Artifact profile: `shifted`, batch `80`, shift `10000000`, rounds `13`.

| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Action |
| --- | --- | --- | ---: | --- | ---: | ---: | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1638400 (7/8) | 5.537 | `presieve13` 1638400 (7/8) | 5.537 | 1.000x | `keep_default` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` 1638400 (7/8) | 1.083 | `presieve13` 1638400 (7/8) | 1.083 | 1.000x | `keep_default` |

## High-Offset Promotion Readout

Confirmed non-default candidates require at least `1.050x` median gain over the current adaptive default and fresh candidate-confirmation evidence before this readout marks them as trial-ready.

| Range | Baseline | Default | Default Median Speedup | Best Candidate | Candidate Median Speedup | vs Default | Default Confirm | Candidate Confirm | Candidate Freshness | Action |
| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- | --- | --- |
| [1000000000000, 1000010000000) | `external_primecount_pi_diff_server` | `presieve13` 2097152 (5/8) | 105.214 | `presieve13` 1507328 (7/8) | 156.159 | 1.484x | `missing` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` 2097152 (5/8) | 12.815 | `presieve13` 1507328 (7/8) | 19.019 | 1.484x | `confirmed` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1500000000000, 1500010000000) | `external_primecount_pi_diff_server` | `presieve17` 1310720 (8) | 137.761 | `segmented` 1310720 (8) | 178.948 | 1.299x | `missing` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` 1310720 (8) | 17.821 | `segmented` 1310720 (8) | 23.150 | 1.299x | `confirmed` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [10000000000000, 10000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1310720 (8) | 275.919 | `presieve17` 1310720 (8) | 334.031 | 1.211x | `missing` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` 1310720 (8) | 37.712 | `presieve17` 1310720 (8) | 45.654 | 1.211x | `confirmed` | `missing` | `missing` | `hold_unconfirmed_candidate` |
| [100000000000000, 100000010000000) | `external_primecount_pi_diff_server` | `presieve13` 1310720 (8) | 1513.839 | `presieve13` 1310720 (8) | 1513.839 | 1.000x | `missing` | `missing` | `missing` | `keep_default` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` 1310720 (8) | 115.146 | `presieve13` 1310720 (8) | 115.146 | 1.000x | `confirmed` | `confirmed` | `stale` | `keep_default` |

## High-Offset Promotion Focus Confirmation

Observed groups: `1`; confirmed: `0`; unconfirmed: `1`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `40`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `segmented` | 1310720 | 8 | 1/2 | 2/2 | 0.054 | 37.017 | `unconfirmed` |

## High-Offset Confirmation

Observed groups: `4`; confirmed: `4`; unconfirmed: `0`.
Minimum confirmations: `2`; requires stable samples: `True`.
Fresh-run count requests per timed sample: `80`.

| Range | Baseline | Mode | Segment | Threads | Confirmations | Stable Runs | Median ms Values | Median Speedups | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [1000000000000, 1000010000000) | `external_primesieve_count_server` | `presieve13` | 2097152 | 5/8 | 3/2 | 3/3 | 0.025, 0.039, 0.027 | 78.348, 59.327, 72.227 | `confirmed` |
| [1500000000000, 1500010000000) | `external_primesieve_count_server` | `presieve17` | 1310720 | 8 | 3/2 | 3/3 | 0.025, 0.034, 0.043 | 96.826, 71.300, 71.107 | `confirmed` |
| [10000000000000, 10000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 2/2 | 2/3 | 0.031, 0.030, 0.051 | 144.592, 154.534, 97.281 | `confirmed` |
| [100000000000000, 100000010000000) | `external_primesieve_count_server` | `presieve13` | 1310720 | 8 | 2/2 | 2/3 | 0.032, 0.040, 0.038 | 385.317, 329.671, 395.925 | `confirmed` |

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

Recommendations: `7`; aligned: `6`; within tolerance: `1`; drift: `0`; noisy drift: `0`; unconfirmed mode drift: `0`; missing evidence: `0`.
Tolerance: `0.050` median slowdown.

| Range | Source | Baseline | Selected Mode | Default Mode | Selected Segment | Default Segment | Threads | Median ms | Samples | Ratio | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| [0, 1000000) | `tuning` | `n/a` | `prefix-pi` | `prefix-pi` | 131072 | 262144 | 1 -> 1 | 0.000 | unknown | 1.506x | `within_tolerance` |
| [0, 10000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 65536 | 65536 | 1/8 -> 1/8 | 2.664 | noisy<br>C n=5, robust/med=1.10, max/med=1.29<br>B n=15, robust/med=2.28, max/med=7.25<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [0, 100000000) | `external_mode_sweep` | `external_primesieve_count` | `prefix-pi` | `prefix-pi` | 196608 | 196608 | 1/8 -> 1/8 | 3.195 | stable<br>C n=5, robust/med=1.05, max/med=1.33<br>B n=15, robust/med=1.25, max/med=1.54<br>mode unconfirmed 0/2 | 1.000x | `aligned` |
| [1000000000000, 1000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 2097152 | 2097152 | 5/8 -> 5/8 | 0.025 | noisy<br>effective stable<br>C n=27, robust/med=1.64, max/med=1.76<br>B n=27, robust/med=1.32, max/med=1.39<br>mode confirmed 3/2 | 1.000x | `aligned` |
| [1500000000000, 1500010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve17` | `presieve17` | 1310720 | 1310720 | 8 -> 8 | 0.025 | noisy<br>effective stable<br>C n=27, robust/med=1.73, max/med=5.30<br>B n=27, robust/med=1.40, max/med=1.66<br>mode confirmed 3/2 | 1.000x | `aligned` |
| [10000000000000, 10000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1310720 | 1310720 | 8 -> 8 | 0.030 | noisy<br>effective stable<br>C n=27, robust/med=2.21, max/med=3.02<br>B n=27, robust/med=1.35, max/med=1.48<br>mode confirmed 2/2 | 1.000x | `aligned` |
| [100000000000000, 100000010000000) | `external_high_offset_confirmation` | `external_primesieve_count_server` | `presieve13` | `presieve13` | 1310720 | 1310720 | 8 -> 8 | 0.032 | noisy<br>effective stable<br>C n=27, robust/med=1.90, max/med=2.67<br>B n=27, robust/med=1.47, max/med=1.48<br>mode confirmed 2/2 | 1.000x | `aligned` |

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
| 10000000 | `high_offset_segmented_range_count` | 4194304 | 5.734 | 361726 |
| 10000000 | `parallel_high_offset_segmented_range_count_8t` | 1507328 | 2.008 | 361726 |
| 10000000 | `parallel_high_offset_default_range_count_8t` | 1507328 | 2.046 | 361726 |
| 10000000 | `parallel_high_offset_balanced_segmented_range_count_8t` | 1507328 | 2.631 | 361726 |
| 10000000 | `high_offset_presieve13_range_count` | 1507328 | 6.685 | 361726 |
| 10000000 | `parallel_high_offset_presieve13_range_count_8t` | 1507328 | 2.114 | 361726 |
| 10000000 | `high_offset_presieve17_range_count` | 1507328 | 6.177 | 361726 |
| 10000000 | `parallel_high_offset_presieve17_range_count_8t` | 1507328 | 2.024 | 361726 |
| 10000000 | `high_offset_bitpacked_range_count` | 1507328 | 7.397 | 361726 |
| 10000000 | `high_offset_tracked_byte_range_count` | 1507328 | 17.918 | 361726 |
| 10000000 | `high_offset_wheel30_range_count` | 1507328 | 49.565 | 361726 |
| 10000000 | `high_offset_wheel30_mark_range_count` | 1507328 | 6.880 | 361726 |
| 10000000 | `parallel_high_offset_wheel30_mark_range_count_8t` | 1507328 | 3.326 | 361726 |
| 10000000 | `high_offset_hybrid_wheel30_mark_range_count` | 1507328 | 7.708 | 361726 |
| 10000000 | `parallel_high_offset_hybrid_wheel30_mark_range_count_8t` | 1507328 | 3.335 | 361726 |
| 100000 | `high_offset_u64_scalar_fallback_range_count` | 64 | 43.914 | 2139 |
| 100000 | `high_offset_u64_scalar_naive_control_count` | 0 | 46.301 | 2139 |
| 10000000 | `cold_external_primesieve_high_offset_count_8t` | 0 | 4.271 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1507328 | 1.895 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_segmented_count_8t` | 1507328 | 2.164 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve13_count_8t` | 1507328 | 2.022 | 361726 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_presieve17_count_8t` | 1507328 | 1.996 | 361726 |
| 1000000 | `cold_process_segmented_range_count` | 262144 | 3.096 | 78498 |
| 10000000 | `cold_process_segmented_range_count` | 262144 | 4.090 | 664579 |
| 10000000 | `cold_process_parallel_segmented_range_count_8t` | 65536 | 3.653 | 664579 |
| 10000000 | `cold_cli_parallel_default_range_count_8t` | 65536 | 1.403 | 664579 |
| 100000000 | `cold_process_parallel_segmented_range_count_8t` | 196608 | 7.768 | 5761455 |
| 100000000 | `cold_cli_parallel_default_range_count_8t` | 196608 | 1.707 | 5761455 |
| 0 | `cold_process_high_offset_noop_worker` | 0 | 1.475 | 0 |
| 10000000 | `cold_process_high_offset_default_plan_8t` | 1507328 | 1.780 | 7 |
| 0 | `cold_count_binary_high_offset_noop` | 0 | 1.343 | 0 |
| 10000000 | `cold_count_binary_high_offset_default_plan_8t` | 1507328 | 1.375 | 7 |
| 10000000 | `cold_process_parallel_high_offset_default_range_count_1t` | 1507328 | 9.534 | 361726 |
| 10000000 | `cold_process_parallel_high_offset_segmented_range_count_8t` | 1507328 | 5.786 | 361726 |
| 10000000 | `cold_process_parallel_high_offset_default_range_count_8t` | 1507328 | 4.329 | 361726 |
| 10000000 | `cold_cli_parallel_high_offset_default_range_count_8t` | 1507328 | 4.314 | 361726 |
| 10000000 | `cold_count_binary_parallel_high_offset_default_range_count_8t` | 1507328 | 4.458 | 361726 |

High-offset cold/hot overhead (source: `high_offset_hot_cold`):

| Workload | Hot Row | Hot ms | Server Row | Count Server ms | Server / Hot | Server / Cold Count Binary | Cold Count Binary ms | Count Binary / Hot | Full CLI ms | Minimal Default Process ms | Segmented Process ms |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10000000 | `parallel_high_offset_segmented_range_count_8t` | 2.008 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | 0.94x | 0.43x | 4.458 | 2.22x | 4.314 | 4.329 | 5.786 |

High-offset cold diagnostics:

| Workload | Bench Noop ms | Bench Plan ms | Count Binary Noop ms | Count Binary Plan ms | Serial Default ms | Count Binary ms | Count Binary - Binary Noop ms | primesieve Cold ms | Count Binary / primesieve |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10000000 | 1.475 | 1.780 | 1.343 | 1.375 | 9.534 | 4.458 | 3.115 | 4.271 | 1.04x |

High-offset server/external best-time comparison:

| Workload | Server Row | Server ms | Baseline | Baseline Best ms | Server Speedup | Cold CLI ms | Cold CLI Speedup |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primecount_pi_diff` | 32.389 | 17.092 | 6.075 | 5.332 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primecount_pi_diff` | 32.389 | 17.092 | 0.129 | 250.415 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primecount_pi_diff_server` | 10.740 | 5.667 | 6.075 | 1.768 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primecount_pi_diff_server` | 10.740 | 5.667 | 0.129 | 83.035 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primesieve_count` | 5.562 | 2.935 | 6.075 | 0.916 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primesieve_count` | 5.562 | 2.935 | 0.129 | 43.003 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primesieve_count_server` | 2.057 | 1.086 | 6.075 | 0.339 |
| 10000000 | `hot_cli_count_server_parallel_high_offset_default_range_count_8t` | 1.895 | `external_primesieve_count_server` | 2.057 | 1.086 | 0.129 | 15.906 |

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
