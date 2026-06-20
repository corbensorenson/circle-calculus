# Circle Prime Engine

Status: first implementation slice.

The prime-search lane uses Circle Calculus language for diagnostics and exact
integer arithmetic for decisions. It does not claim a new asymptotic primality
algorithm.

## Shape

- Lean backbone: `Circle/Core/Horizon.lean` records the primitive-horizon
  containment bridge as exact divisibility.
- Rust engine: `rust/circle-prime` provides coil signatures, deterministic
  `u64` primality testing, and segmented range search.
- Python remains useful for repository integration tests and public examples,
  but not for the hot prime-search path.

## Commands

```bash
cargo test -p circle-prime
cargo run -p circle-prime -- inspect 16
cargo run -p circle-prime -- test 18446744073709551557 --json
cargo run -p circle-prime -- next 1000000000000 --json
cargo run -p circle-prime -- range 0 1000000 --count
cargo run -p circle-prime -- range 0 100000000 --count --threads 8
printf '1000000000000 1000010000000\n' | cargo run -p circle-prime -- count-server --threads 8
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 3
cargo run --release -p circle-prime --bin circle-prime-tune -- --rounds 3
make prime-engine-check
make prime-engine-benchmark
make prime-engine-benchmark-record
make prime-engine-benchmark-compare
make prime-engine-external-correctness
make prime-engine-external-controls
make prime-engine-external-controls-parallel
make prime-engine-external-controls-compare
make prime-engine-external-mode-sweep
make prime-engine-external-mode-confirm
make prime-engine-high-offset-hot-cold
make prime-engine-external-throughput
make prime-engine-external-throughput-compare
make prime-engine-external-segment-sweep
make prime-engine-calibrate-defaults
make prime-engine-calibrate-defaults-check
make prime-engine-apply-defaults
make prime-engine-apply-defaults-check
make prime-engine-tune
make prime-engine-tune-night
make prime-engine-report
make prime-engine-overnight
make prime-engine-overnight-improve
```

`make prime-engine-report` is a gated report command: it uses
`--require-inputs` and fails when the core benchmark, external-correctness,
external-control, or tuning artifacts are missing. The overnight targets
therefore stop on missing evidence instead of emitting a partial report that
looks complete.

`make prime-engine-check` compiles the Rust crate, exercises representative CLI
classification/count commands, and runs
`scripts/check_prime_proof_contract.py` so the JSON `proof_contract` emitted by
the Rust CLI, plus the `count_proof_contract` emitted by count JSON and
`count-server --json`, must match the proved theorem ids and Lean names in
`manifests/theorem_manifest.yaml`. The checker also resolves the claimed Lean
module to its `.lean` file and verifies that every contracted Lean declaration
is still present in source.

## Current Guarantees

- `CC-T0005`: `period(n,k) = n / gcd(n,k)` is already proved in Lean.
- `CC-T0054`: `fullCoil(n,k)` iff `Nat.Coprime n k` is already proved in Lean.
- `CC-T0073`: primitive horizon containment is exactly divisibility.
- `CC-T0074`: prime horizon iff no nontrivial smaller primitive horizon is contained.
- `CC-T0075`: prime horizon iff no primitive horizon up to `Nat.sqrt n` is contained.
- `CC-T0076`: no contained primitive horizon up to `Nat.sqrt n` proves the
  candidate horizon is prime.
- `CC-T0077`: every non-prime horizon has a contained primitive horizon up to
  `Nat.sqrt n`.
- `CC-T0078`: membership in `primeHorizonsInRange low high` is exactly
  `low <= n < high` plus `primeHorizon n`.
- `CC-T0079`: `primeHorizonRangeCount low high` is the cardinality of the
  half-open interval filtered by prime horizons.
- JSON output from `circle-prime inspect`, `circle-prime test`,
  `circle-prime recommend --json`, `circle-prime range --json`, and
  line-delimited `circle-prime next-server --json` includes a
  `proof_contract` object naming the Lean module and theorem ids behind the
  prime-horizon interpretation. This metadata is deliberately a contract link:
  Lean proves the horizon/divisibility equivalence, while Rust supplies exact
  `u64` arithmetic, sieving, and deterministic Miller-Rabin classification.
- Count JSON from `circle-prime recommend --count --json` and
  `circle-prime range ... --count --json`, plus line-delimited JSON from
  `circle-prime count-server --json`, also includes
  `count_proof_contract`, which points at the finite half-open range-count spec
  proved in Lean. This does not prove each Rust optimization internally; it
  fixes the mathematical target every count mode must match.
- Rust primality decisions for `u64` use exact arithmetic and the 7-base
  deterministic Miller-Rabin witness set for the full 64-bit domain:
  `{2, 325, 9375, 28178, 450775, 9780504, 1795265022}`.
- Range enumeration uses the same pre-sieved odd-candidate segment refill and
  cursor progression as count, then materializes surviving candidates in order.
- Range counting uses a count-only odd-byte segmented sieve with a reusable
  segment buffer, a build-time generated 3/5/7/11/13/17/19 pre-sieve table,
  and per-prime cursor state across segments. This avoids the enumeration
  callback path, skips the densest small-prime composite writes, removes
  repeated per-segment division setup, and avoids rebuilding the large pre-sieve
  table in fresh CLI processes. Prefix rows cap each segment to cursors whose
  prime square has reached that segment, avoiding inactive large-base-prime
  checks in early segments. Count-only rows sum `0/1` flag bytes through
  machine-word popcount.
- Base-prime generation uses a build-time generated table through `1100000`,
  an odd-only byte sieve for larger common `sqrt(high) <= 10000000` limits, and
  a compact bitset fallback through `sqrt(high) <= 100000000`. Larger
  base-prime horizons return `BaseLimitTooLarge` unless the requested interval
  is a small span; those tiny top-of-`u64` intervals use the exact scalar
  deterministic Miller-Rabin lane instead of trying to build a multi-gigabyte
  base-prime table. The generated table removes most base-sieve setup cost from
  the current `10^12` high-offset benchmark while keeping the general fallback
  path intact.
- The CLI chooses an adaptive default segment size. Single-thread count and
  enumeration use `262144` for ordinary prefix/range counts, `1048576` when
  the base-prime horizon reaches roughly `sqrt(high) >= 300000`, and
  `4194304` when it reaches `sqrt(high) >= 1000000`.
- Count-only CLI runs can use `--threads N`. The value is a maximum worker
  count: the engine caps actual workers to the number of useful segments for
  the range. When no explicit `--segment-size` is provided, count-only threaded
  prefix-style ranges use command-level tuned defaults: `262144` up to
  about 2M, `65536` up to about 16M, and `196608` up to about 128M.
  True prefix buckets use the exact `prefix-pi` counter through `1e9`.
  Broad low-absolute count-only ranges also use `prefix-pi` when the upper
  bound is at most `3e9`; short external-control probes show that lane still
  beats `primesieve` there, while it loses by `[3e9, 4e9)` and must not become
  the high-offset default. Non-prefix `prefix-pi` ranges can use two workers
  for the exact `pi(high - 1) - pi(low - 1)` difference when the requested
  thread count allows it.
  Very-high-offset threaded counts with small spans use a tuned `1507328`
  default and the threaded `presieve17` count mode, which currently gives the best short-run
  command-level result against `primesieve` without claiming parity. Other
  ranges keep the conservative segmented default.
  The threaded-count values live in
  `rust/circle-prime/prime_engine_defaults.json`; Cargo's build script renders
  them into Rust constants, and the CLI tests read the same JSON.
  The parallel path splits the half-open range into chunks, shares the
  base-prime list across scoped worker threads, and verifies against the same
  count-only core used by the single-thread path.
- Benchmarks include control implementations: a straightforward full
  Sieve-of-Eratosthenes count, a guarded scalar trial-division count, and the
  optimized pure-Rust `primal` sieve.

## Control Baselines

The simple sieve and trial-division controls are not serious speed opponents.
They are retained because they are easy to audit and catch obvious correctness
or regression failures.

The first serious in-repo control is `primal`, which describes itself as a
cache-friendly optimized Sieve of Eratosthenes implementation. The current
Circle segmented count beats `primal` on the standard 1M and 10M benchmarks
with the tuned segment size. That is useful but not final: `primal` remains the
in-repo regression floor, and external `primesieve`/`primecount` comparisons
remain the higher bar.

For best-current external comparisons, use:

- `primesieve` for prime generation and range counting
  (`https://github.com/kimwalisch/primesieve`). It uses a segmented sieve with
  wheel factorization, cache-size tuning, bucket sieving for large values, and
  multi-threading where ordering permits.
- `primecount` for the prime-counting function `pi(x)`
  (`https://github.com/kimwalisch/primecount`). This is not the same task as
  enumerating/counting a materialized range; it uses combinatorial
  prime-counting algorithms such as Deleglise-Rivat and Xavier Gourdon.

The Makefile external-control targets require both tools. This prevents a
benchmark or overnight run from silently passing when the serious controls are
not installed. The benchmark metadata records tool paths, versions, requested
thread policy, command lines, sample CSV paths, and the required control list;
the generated prime-engine report surfaces that required-control list beside
the timing rows.

On macOS these can be installed outside the repo with:

```bash
brew install primesieve primecount
```

Then run:

```bash
make prime-engine-external-controls
make prime-engine-external-controls-parallel
make prime-engine-external-throughput
make prime-engine-external-segment-sweep
```

## Optimization Rule

Future speed work should be benchmark-driven:

1. keep a correct reference path;
2. record wall-clock timings and prime-count checks;
3. add one optimization at a time;
4. keep GPU or MLX work separate until CPU correctness and baselines are stable.

The first tuning knobs are count mode, segmented-sieve segment size, and
requested thread count. Use `circle-prime-tune` or `scripts/tune_prime_engine.py`
to sweep mode/segment/thread combinations in-process before changing code.

Current CPU findings:

- `Vec<bool>`/enumeration is correct but too slow for count-only work.
- Odd-byte flags with a reusable segment buffer are the current best in-tree
  count path.
- Experimental tracked-byte, bit-packed odd, compact wheel-30, and wheel-30
  multiplier-skipping count rows are kept in the release benchmark for A/B
  evidence, but they are not default paths. The tracked-byte path lost to
  branch/read overhead, the bit-packed path lost to individual bit marking
  overhead, the straightforward wheel-30 path lost to compact-index/gap
  scheduling overhead. The byte-buffer wheel-30 multiplier-skipping path now
  uses active cursor caps and an unrolled fixed 8-gap cycle, which made that
  experiment much faster than the earlier per-strike residue scheduler, but it
  still loses to the primary odd-byte path on the current sustained rows. An
  8-thread variant is also recorded; it narrows the gap on some prefix segment
  sizes, but remains slower than the primary 8-thread odd-byte counter and is
  not promoted to the CLI default. A hybrid dense/wheel threshold variant is
  also recorded. It can slightly improve isolated 100M prefix segment rows, but
  it loses the current 1B and high-offset rows, so it remains experimental.
- Reusable pre-sieving through 19 is a measured warm-run win. Rebuilding large
  pre-sieve patterns per segment was a loss; the table is now generated at
  build time and embedded with `include_bytes!`.
- A smaller cache-resident pre-sieve through 13 is available as `presieve13`.
  Its original single-thread row was slower on sustained rows because marking
  17/19 cost more than the cache benefit. The threaded variant is now promoted
  only for the narrow very-high-offset default, where command-level comparisons
  favor the smaller table over the larger 19-prime pre-sieve.
- A middle-sized pre-sieve through 17 is available as `presieve17`. It avoids
  marking multiples of 17 while staying much smaller than the 19-prime table.
  The latest high-offset tight scorecard found it slightly ahead of the
  promoted `presieve13` lane, but the confirmation gate has not yet proved the
  win stable enough to auto-promote the default.
- Carrying per-prime cursor state across segments is a measured win because it
  removes repeated per-prime ceil-division setup.
- Single-segment count chunks skip cursor-vector allocation and mark directly
  from the base-prime table. This is mainly for command-level parallel chunks
  and high-offset slices whose effective worker chunk fits inside one segment.
- Single-segment first-multiple setup returns the odd-byte index directly
  instead of materializing the starting multiple and subtracting the segment
  low back out. This preserves the same divisibility target while reducing
  arithmetic in the high-offset path that touches tens of thousands of base
  primes per worker.
- The high-offset odd-byte marker now switches to sparse writes at
  `flags.len() / 4` instead of the older `/8` cutoff. Focused external-control
  sweeps kept correctness fixed and closed part of the remaining median
  `primesieve` gap for the promoted `presieve13` high-offset lane.
- A monotonic active-cursor boundary that skipped cursors whose square had not
  reached the current segment was correct but slower on the benchmark rows, so
  it was reverted rather than promoted.
- Aligned machine-word popcount over byte flags is a measured count-only win
  over a byte-by-byte sum on the standard 10M and 100M benchmark ranges.
- The primary byte marking loop is manually unrolled in the count and
  enumeration paths. This is a measured win on prefix count rows because the
  hot loop has a variable stride and the compiler does not reliably remove
  enough branch overhead on its own.
- A wider 8-write dense marking unroll was tested and rejected. It looked
  promising on some in-process primary rows, but repeated external-control
  runs worsened the key 100M command-level median, so the shared primary path
  stays on the narrower measured unroll.
- Reusable count buffers are refilled directly from the pre-sieve pattern
  without first zeroing newly grown memory. This is a small but measurable win
  on the current prefix and high-offset count rows because every byte is
  overwritten before marking begins.
- A build-time `u64` base-prime table covers horizons through `1100000` as a
  generated Rust static slice. The same table backs fast small `pi(n)` lookups
  and borrowed sieve setup, avoiding the previous duplicate generated `u32`
  and `u64` tables in the cold CLI binary. Odd-only byte generation remains the
  fallback for larger common command-level limits. The release benchmark emits
  `base_prime_generation` rows so this setup cost remains visible alongside
  range-count hot loops.
- Adaptive segment sizing is a measured win for high-offset interval searches:
  around `10^12`, large segments reduce repeated cursor scans over tens of
  thousands of base primes.
- `make prime-engine-high-offset-hot-cold` is the short feedback target for
  separating algorithmic speed from command startup. It runs only the Rust
  high-offset and cold-process benchmark sections, writes
  `prime_engine_high_offset_hot_cold_latest.csv`, and the report uses that
  artifact for the high-offset cold/hot overhead table when present. The same
  artifact now includes persistent `count-server` CLI rows, which keep the
  Circle binary loaded and time repeated stdin/stdout count requests. The report
  calls out the fastest server row so candidate modes such as `segmented`,
  `presieve13`, and `presieve17` are visible without a broad external sweep.
  Use it after small hot-path changes before spending time on broader external
  sweeps.
- The scalar `u64` primality lane uses the 7-base deterministic Miller-Rabin
  set instead of the first 12 prime bases. That is both the stronger documented
  `u64` coverage and a measured speedup for random candidate batches.
- The scalar lane also has a narrow angle-bundle GCD rejection layer after the
  exact small-horizon checks. The current bundle compresses prime horizons
  `41..79` into one product and rejects candidates sharing a nontrivial factor
  before Miller-Rabin. A broader five-bundle experiment through `257` was
  correct but slower on the scalar batch, so only the measured smaller bundle is
  retained.
- The `next` scalar search uses wheel-30 candidates after the small-prime
  boundary cases. That lets it skip divisibility checks by `2`, `3`, and `5`
  for every later candidate while keeping the same deterministic Miller-Rabin
  and proof-contract path.
- Parallel range counting is implemented as an opt-in count-only path. It is a
  measured win in-process on larger prefix ranges: on this workspace's latest
  benchmark, 100M dropped from about `19.2ms` single-thread to about `4.2ms`
  with 8 threads. Command-level gains are smaller because process startup and
  thread startup become visible.
- The release benchmark includes parallel rows at `131072`, `196608`, the
  single-thread recommendation, and the current count recommendation for 10M,
  100M, and 1B workloads. This keeps the tuned parallel lane visible without
  automatically promoting every noisy tuner winner into a CLI default. Prefix
  count-only threaded defaults split tiny spans from larger prefix ranges after
  command-level external probes showed one segment size does not fit both
  startup-dominated and throughput-dominated prefix counts. The structured
  defaults file now carries both segment-size and count-mode slots per tuned
  range; mode slots start conservatively and are promoted only when stable
  external-control calibration evidence favors another algorithm.
  Very-high-offset small-span threaded counts use the `1507328` default with
  `presieve17`; focused short probes keep nearby balanced and presieve segment
  choices as evidence lanes rather than default promotions because their wins
  have been noisy run-to-run.
- The release benchmark also includes `[10^12, 10^12 + 10M)` high-offset rows:
  one conservative single-thread row, one explicit segmented count-threaded
  row, hot-loop `parallel_high_offset_*_range_count_8t` rows covering the
  compiled adaptive count-mode default and explicit modes, and experimental
  lanes. This keeps cursor-initialization, mode-default, and high-offset
  segment-default regressions visible without relying only on the
  external-control script. The hot/cold report selects the fastest eligible
  hot row and fastest count-server row from the artifact so mode wins are not
  hidden behind a hardcoded default.
- A work-balanced prefix splitter using an `x^(3/2)` sieve-work estimate is
  kept as an experimental benchmark row. It was correct and helped some 100M
  rows, but it lost the current 1B rows, so the CLI default still uses equal
  range chunks. The release benchmark also records the same splitter on the
  high-offset interval because external mode-sweep evidence showed that
  high-offset chunk balance can differ from prefix chunk balance. A focused
  seven-round high-offset command-level probe showed balanced splitting beating
  equal chunks by median on `[10^12, 10^12 + 10M)`, but both Circle rows and
  the external controls were noisy, so this remains an evidence lane rather
  than a default promotion.
- A dynamic batched parallel splitter is available as the explicit `dynamic`
  count mode. It keeps the same segmented odd-byte sieve but lets workers pull
  batches of segments from a shared queue, targeting prefix-range load imbalance
  without changing the proof/correctness contract. Its batch size is adaptive:
  small segment-count ranges use one segment per batch so reported worker counts
  correspond to actual parallel work, while larger prefix ranges cap batch size
  to preserve cursor reuse. It is included in tuning and external mode sweeps;
  current calibration promotes it only for the small-prefix threaded bucket.
- High-offset bit-packed, tracked-byte, and wheel-30 experimental rows are
  also recorded. These are not default paths; they keep representation-specific
  offset costs visible because high-offset cursor setup has a different profile
  from prefix counting.
- Cold-process rows are part of the benchmark output. Child-worker rows keep
  explicit segmented labels, while `cold_cli_*_default_*` rows call
  `circle-prime range ... --count` without an explicit count mode so they track
  the current adaptive CLI default, intentionally including process and thread
  startup beside hot-loop timings.
- The next serious lanes are a lower-overhead wheel schedule, bucket sieving
  for large ranges, and reducing command-level overhead for parallel searches.

## Repository Validation

Use the Makefile targets for repeatable local checks:

```bash
make prime-engine-check
make prime-engine-benchmark
make prime-engine-benchmark-record
make prime-engine-external-correctness
make prime-engine-external-controls
make prime-engine-external-controls-parallel
make prime-engine-external-mode-sweep
make prime-engine-external-segment-sweep
make prime-engine-calibrate-defaults
make prime-engine-tune
make prime-engine-report
```

`prime-engine-check` runs `cargo fmt --all --check`, `cargo test -p
circle-prime`, and CLI smoke checks for scalar primality and the known
`pi(1,000,000)` count.

`prime-engine-benchmark` runs the same checks plus the release benchmark. The
benchmark gate parses emitted speedup rows and requires the fastest Circle
count row for each workload to beat the simple-sieve and trial-division
controls by configurable minimum ratios. It also requires a per-workload win
against `primal` via `--min-primal-speedup 1.0`, so a fast small workload
cannot hide a larger-range regression. It still emits single-thread rows, tuned
parallel rows, high-offset interval rows, base-prime generation rows, and
cold-process timing rows so the tradeoffs stay visible.

This target is intentionally separate from the default repository check because
timing gates are machine-sensitive.

`prime-engine-benchmark-record` uses five benchmark rounds and writes the CSV
artifact to:

```text
sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv
```

That file is intended as local optimization evidence. Re-run it after each
performance change and compare the `speedup` rows before claiming an
improvement.

For focused micro-iteration, the release benchmark binary also accepts
`--only` with comma-separated sections. This keeps speculative scalar, parallel,
or high-offset experiments from paying for the full suite while they are still
being evaluated:

```bash
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 9 --only scalar
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 9 --only scalar,next
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 7 --only parallel,high-offset
```

Compare focused candidate CSVs against the latest recorded release benchmark
before keeping a speculative optimization:

```bash
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 7 --only scalar,next > /tmp/circle-prime-scalar.csv
python scripts/compare_prime_engine_benchmarks.py \
  /tmp/circle-prime-scalar.csv \
  --names scalar_u64_batch,next_prime_search \
  --max-regression-ratio 1.02 \
  --require-improvement-ratio 0.99
```

The comparator requires every selected baseline timing row to appear in the
candidate CSV. This prevents a renamed or skipped row from silently passing an
overnight gate; use `--allow-candidate-subset` only for exploratory partial
comparisons.

The Make wrapper runs that loop with tunable variables:

```bash
make prime-engine-benchmark-compare
make prime-engine-benchmark-compare \
  CIRCLE_PRIME_BENCH_ONLY=parallel,high-offset \
  CIRCLE_PRIME_BENCH_NAMES=parallel_segmented_range_count_8t,parallel_high_offset_default_range_count_8t \
  CIRCLE_PRIME_BENCH_ROUNDS=7 \
  CIRCLE_PRIME_BENCH_MAX_REGRESSION_RATIO=1.03
```

By default, `prime-engine-benchmark-compare` now runs `scalar,next` and
compares both `scalar_u64_batch` and `next_prime_search`, so the proof-backed
next-prime search path has its own speed regression gate. For
`next_prime_search` timing rows, the CSV `workload` field is the search start
and `segment_size` is the repeated-search batch count used to get stable timing.

`prime-engine-external-correctness` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_correctness_latest.json
```

It builds the release `circle-prime` binary once, checks the requested Circle
count modes and segment-size candidates against both `primesieve` and
`primecount`, and checks exact materialized prime lists against `primesieve
--print` on small prefix, offset, square-boundary, `2^32`-boundary, and
high-offset windows, plus `circle-prime next` searches against `primesieve
--print` for representative starts. It also checks a tiny top-of-`u64` window
that exercises the scalar
fallback without making `primecount` compute `pi(x)` near `2^64`. It does this without
collecting timing samples. The default Makefile target requires both external
tools and checks all exposed count modes across prefix, offset, and high-offset
ranges, including windows that cross `2^32` and `10^12`, using the adaptive
default plus representative tuned segment sizes
`65536`, `196608`, `1310720`, `1441792`, `1507328`, `2621440`, and `4194304`. Use this as the fast external correctness
gate; use the external-control targets below for timing evidence.

`prime-engine-external-controls` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_samples_latest.csv
```

If `primesieve` or `primecount` are not installed, the script reports that and
still exits cleanly unless `--require-external` is passed directly.

`prime-engine-external-controls-parallel` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_parallel_samples_latest.csv
```

It uses `CIRCLE_PRIME_THREADS ?= 8` as the maximum requested worker count by
default and `EXTERNAL_PRIME_THREADS ?= $(CIRCLE_PRIME_THREADS)` for the
external tools. The harness passes `--threads=N` to `primesieve` and
`primecount` when `--external-threads N` is nonzero; use `0` to keep each
tool's default, which both tools document as all available CPU cores. The
Makefile targets use seven rounds to reduce single-sample timing noise. The
harness performs one untimed Circle JSON probe for adaptive segment/thread
metadata, then times plain count output so the Circle subprocess path is closer
to the `primesieve`/`primecount` command-level controls. The parallel Makefile
target also passes `--include-circle-server`, so each range includes persistent
`count-server` request rows beside the cold CLI rows. Treat the server rows as
steady-state application throughput evidence; the cold CLI rows remain the
command-vs-command comparison against `primesieve` and `primecount`.
The Makefile external control targets request `--circle-count-modes default`,
so the Circle rows omit `--count-mode` and track the current adaptive CLI
default. These targets use
interleaved timing: for each range, Circle variants and external baselines run
in a rotated round-robin order, and the harness writes the per-round sample CSV
alongside the summary CSV. This prevents a segment sweep from measuring all
Circle candidates in one machine state and the external baseline in another.
The CLI reports the actual worker count in JSON after capping by segment count.
The JSON sidecar records local tool paths, version strings, requested thread
policy, timing policy, whether server rows were included, ranges, and the exact
per-range commands used for Circle, `primesieve`, and `primecount`.
External-control CSV rows also include
the resolved Circle `count_mode`, so rows requested as `default` can still show
the actual CLI-selected mode such as `segmented` or `balanced`.
The CSV records both best-of-round and median-of-round timings/speedups; use
median speedup for default decisions and best speedup only as peak-throughput
evidence.
This matters because `primesieve` is the range-counting control and
`primecount` is the stronger `pi(x)`/prefix-counting control; comparing against
both avoids pretending that one baseline covers both tasks. Override the
requested maximum per run when the machine or workload favors a smaller worker
count:

```bash
make prime-engine-external-controls-parallel CIRCLE_PRIME_THREADS=4
make prime-engine-external-controls-parallel CIRCLE_PRIME_THREADS=8 EXTERNAL_PRIME_THREADS=0
```

`prime-engine-external-next` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_next_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_next_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_next_samples_latest.csv
```

It benchmarks `circle-prime next START` against three external next-prime
controls:

- `primesieve 1 START-1 --nth-prime --quiet`, which gives the first prime at or
  above `START` through the installed command-line tool.
- a tiny repo-owned line server linked against `libprimesieve` and using
  `primesieve_generate_n_primes(1, START, UINT64_PRIMES)`. This is the harder
  low-overhead control for independent next-prime queries, because it removes
  process startup and uses the library API directly.
- `primecount` for starts at or below
  `CIRCLE_PRIME_EXTERNAL_NEXT_PRIMECOUNT_MAX_START` (default
  `1000000000000`): it computes `pi(START-1)` and then asks `primecount
  --nth-prime` for the next index. That keeps `primecount` as a serious second
  control where it is short-run friendly without letting near-`u64::MAX`
  `pi(x)` dominate the routine next-prime benchmark.

The Makefile target includes persistent `next-server` Circle request rows
beside the cold CLI rows, so the report separates command-level startup cost
from steady-state search throughput. The libprimesieve helper is also
persistent, which makes it the right comparison for judging Circle's persistent
server path. Persistent server rows send the repeated `batch_size` requests in
one stdin write per timing sample and then read one response line per request;
that keeps Circle and the libprimesieve helper on the same line-server footing
while reducing Python round-trip noise. The default starts cover small search,
the `2^32` boundary, `10^12`, and a near-`u64::MAX` scalar path.
The CSV keeps next-prime fields separate from range-count fields: `start`,
`batch_size`, resolved `result`, Circle `candidate_count`, and searches/sec. Use
`CIRCLE_PRIME_EXTERNAL_NEXT_BATCH_SIZE` for repeated searches per timing sample;
the Makefile default is `4` so command-level next-prime comparisons are less
sensitive to launch jitter while still keeping the near-`2^64` `primesieve`
row short enough for routine regression gates. Use `1` for quick local probes.
Raise `CIRCLE_PRIME_EXTERNAL_NEXT_PRIMECOUNT_MAX_START` only for explicit
primecount stress probes. Lower
`CIRCLE_PRIME_EXTERNAL_NEXT_PRIMESIEVE_LIBRARY_MAX_START` only if the
near-`u64::MAX` libprimesieve helper row is too slow for a local quick run.

`prime-engine-external-next-compare` writes candidate artifacts without
overwriting the accepted latest next-prime control run:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_next_candidate_samples_latest.csv
```

It then compares candidate next-prime speedup rows against
`prime_engine_external_next_latest.csv` with
`scripts/compare_prime_external_next.py`. The default comparison starts are
`4294967000`, `1000000000000`, and `18446744073709551500`: these keep the
`2^32`, `10^12`, and near-`u64::MAX` behavior under regression control while
leaving startup-dominated tiny starts as report evidence. Override
`CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_STARTS` when a focused experiment should
gate a different subset. The broad default drift gate checks
`CIRCLE_PRIME_EXTERNAL_NEXT_COMPARE_BASELINES` (default
`external_primesieve_next_prime,external_primesieve_generate_next_server`);
`primecount` rows remain measured and reported, but the default regression gate
does not fail on `primecount pi+nth-prime` timing jitter. The Makefile target
then runs a stricter selected-row check requiring
`circle_prime_server_next_prime` to keep median speedup at or above
`CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_LIB_MEDIAN_FLOOR` (default `1.0`) against
the direct `external_primesieve_generate_next_server` library control.
The next-prime comparator uses symmetric noise floors: a median-speedup
regression can be tolerated when best speedup stays close, and a best-speedup
regression can be tolerated when median speedup stays close. This matters for
command-level next-prime rows because sub-millisecond Circle startup jitter can
move the best-time ratio even when the median result is stable.
Rows that are already massively ahead also use an absolute-dominance floor:
when both the accepted and candidate speedups for a checked metric are at least
`CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_SPEEDUP_FLOOR` (default `1000.0`), the
ratio gate relaxes to `CIRCLE_PRIME_EXTERNAL_NEXT_DOMINANT_MIN_SPEEDUP_RATIO`
(default `0.75`). This keeps near-`u64::MAX` server rows from failing because
an 18,000x speedup measured lower than a 23,000x speedup in a short run, while
still rejecting a collapse from thousands-x to merely marginally faster.

`prime-engine-external-controls-compare` writes candidate artifacts without
overwriting the accepted latest external-control run:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_controls_candidate_samples_latest.csv
```

It then compares candidate speedup rows against
`prime_engine_external_controls_parallel_latest.csv` with
`scripts/compare_prime_external_controls.py`. Unlike the in-process benchmark
comparator, this gate compares Circle's speedup relative to the serious
external controls, so machine-wide timing drift is less likely to look like a
real improvement. The default candidate run uses seven interleaved rounds,
matching the accepted parallel external-control baseline. The comparator also
requires every selected baseline speedup row to appear in the candidate CSV;
use `--allow-candidate-subset` only for exploratory partial comparisons. The
comparison output reports baseline and candidate resolved `segment_size` and
`count_mode` values. For rows requested as adaptive `default`, segment or mode
changes are allowed by default because the gate is meant to evaluate new
default behavior against old default behavior; pass
`--fail-on-segment-size-change` or `--fail-on-count-mode-change` when you want
to freeze the selected implementation path during a check. The
default thresholds are deliberately conservative:
`CIRCLE_PRIME_EXTERNAL_MIN_MEDIAN_SPEEDUP_RATIO ?= 0.90` and
`CIRCLE_PRIME_EXTERNAL_MIN_BEST_SPEEDUP_RATIO ?= 0.85`. Median-only drift is
tolerated when the same row's best-speedup ratio still clears
`CIRCLE_PRIME_EXTERNAL_MEDIAN_REGRESSION_BEST_FLOOR ?= 0.90`; command-level
external rows can move enough that median-only failures are otherwise too
flaky for unattended overnight promotion. The default Make target compares
against `external_primesieve_count`, because `primesieve` is the
range-search/range-counting opponent. Add `external_primecount_pi_diff` when
the specific question is whether Circle is also gaining against the stronger
prefix `pi(x)` algorithm. Tighten thresholds for a quiet machine, or use
`CIRCLE_PRIME_EXTERNAL_REQUIRE_ANY_MEDIAN_SPEEDUP=1.0` when the goal is to
prove at least one median-time win over the selected external control.

```bash
make prime-engine-external-controls-compare
make prime-engine-external-controls-compare \
  CIRCLE_PRIME_EXTERNAL_COMPARE_BASELINES=external_primesieve_count,external_primecount_pi_diff \
  CIRCLE_PRIME_EXTERNAL_MIN_MEDIAN_SPEEDUP_RATIO=0.97
```

For direct exploratory runs, `scripts/benchmark_prime_external_controls.py`
also accepts `--circle-count-modes`. The script default remains `segmented` for
backward-compatible direct runs; pass `default` to omit `--count-mode` and
measure the current adaptive CLI default. Opt-in values `balanced`, `dynamic`,
`prefix-pi`, `presieve13`, `presieve17`, `wheel30-mark`, and `hybrid-wheel30-mark` expose the current
experimental counters as separate Circle rows against the same
`primesieve`/`primecount` command-level controls:

```bash
python scripts/benchmark_prime_external_controls.py \
  --ranges 0:1000000 \
  --rounds 3 \
  --interleaved \
  --require-tool primesieve \
  --require-tool primecount \
  --circle-threads 4 \
  --external-threads 4 \
  --circle-count-modes default,segmented,dynamic,prefix-pi,hybrid-wheel30-mark,wheel30-mark,balanced,presieve13,presieve17
```

`prime-engine-external-mode-sweep` records the durable version of that
algorithm-family comparison:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_mode_sweep_samples_latest.csv
```

It keeps the adaptive Circle segment default fixed and sweeps the available
count implementations: `segmented`, `balanced`, `dynamic`, `prefix-pi`,
`presieve13`, `presieve17`, `wheel30-mark`, and `hybrid-wheel30-mark`. Use it to decide which implementation family
deserves deeper work. Keep `prime-engine-external-segment-sweep` as the
default-change gate for current segmented CLI defaults.

`prefix-pi` is a Lehmer-style exact prefix counter exposed as a Circle count
mode. It is promoted for true prefix-count buckets such as `[0, 1M)`,
`[0, 10M)`, `[0, 100M)`, and `[0, 1B)`, plus broad low-absolute count ranges
ending at or below `3e9`. Short external-control runs show this lane is the
right Circle default for `pi(1e9)` and `[1e9, 2e9)`: it beats `primesieve`
there, and the two-worker non-prefix difference is now close to specialized
`primecount` on `[1e9, 2e9)`. It is deliberately not the larger-range or
high-offset default: probes above the cutoff, and high-offset intervals such as
`[1e12, 1e12 + 1e7)`, stay on the segmented-sieve family, currently the
threaded `presieve17` count mode with a tuned high-offset segment size.

`prime-engine-high-offset-quick` is the interactive scorecard for the remaining
`primesieve` gap. It isolates `[1e12, 1e12 + 1e7)`, runs 13 interleaved rounds
by default, and compares the current high-offset neighborhood
`1310720,1376256,1441792,1507328,2097152,3145728,4194304`
across `segmented`, `presieve13`, and `presieve17`.
It writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_quick_samples_latest.csv
```

Use this target first when editing high-offset marker internals or defaults; it
is short enough for interactive iteration and still compares against both
current controls.

`prime-engine-high-offset-hot-cold` is the shorter diagnostic target for code
changes that should affect the Rust engine before they affect command-vs-command
scorecards. It runs only the in-process high-offset rows plus persistent
`count-server` candidate rows for the default, segmented, presieve13, and
presieve17 lanes, cold process, and cold CLI rows, writing:

```text
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_hot_cold_latest.csv
```

The report prefers this artifact for the high-offset cold/hot overhead table
when it exists, so a quick run can show whether a change improved the engine or
only moved process-startup noise. Treat the persistent server row as a
hot-process application lane; the command-vs-command control remains the
external `primesieve`/`primecount` scorecard. When both artifacts are present,
the report also compares the fastest persistent server row directly against
the external high-offset command controls by best time.

`prime-engine-high-offset-tight` is the follow-up scorecard when the broad
quick run keeps pointing at the same neighborhood. It narrows the sweep to
`1310720,1376256,1441792,1507328,4194304`, keeps the same three count modes,
and runs 17 interleaved rounds. The grid includes the current default segment
size so calibration can compare the compiled default directly against the
tight winner. Use it to decide whether an apparent `primesieve` win is worth a
confirmation run without paying for the broader candidate grid. The
default-calibration script now treats this artifact as the preferred high-offset
evidence for the tracked `[1e12, 1e12 + 1e7)` lane when it exists, falling back
to the broader quick artifact only for uncovered ranges.

`prime-engine-high-offset-confirm` repeats the focused quick candidate set and
writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_confirmation_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_confirmation_latest.md
```

Calibration reads this confirmation file when present. A confirmed repeated
winner can override the latest quick median pick; an unconfirmed or noisy
winner stays visible as drift evidence but is not promoted by
`prime-engine-apply-defaults` unless the explicit noisy override is used.

`prime-engine-high-offset-compare` is the broader confirmation target for the
same gap. It isolates `[1e12, 1e12 + 1e7)`, sweeps the larger high-offset
segment-size neighborhood across `default`, `segmented`, `dynamic`, `balanced`,
`presieve13`, and `presieve17`, and writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_high_offset_compare_samples_latest.csv
```

Use the broader target before promoting a surprising winner into defaults; keep
`prime-engine-overnight` as a regression workflow rather than the default way
to learn whether a change helped.

`prime-engine-external-mode-confirm` runs repeated interleaved external
count-mode sweeps and writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_mode_confirmation_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_mode_confirmation_latest.md
```

The confirmation step answers a stricter question than a single mode sweep:
did the same mode/segment/thread tuple win repeatedly against the selected
external baseline with stable per-round samples? By default it runs three
sweeps against the adaptive segment default (`0`) and requires two stable
matching wins. Set `CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_SEGMENT_SIZES` to test
tuner-favored segment grids against `primesieve`/`primecount` before promoting
them into adaptive defaults, for example:

```bash
make prime-engine-external-mode-confirm \
  CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_SEGMENT_SIZES=0,65536,98304,131072,196608,262144,1376256,1441792,1507328,2359296,2621440,3145728,4194304
```

Use
`CIRCLE_PRIME_EXTERNAL_MODE_CONFIRM_FAIL=1` when you want the target to exit
nonzero on unconfirmed rows; leave it unset during exploratory overnight runs
so noisy-but-informative evidence is still recorded.

`prime-engine-external-throughput` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_throughput_samples_latest.csv
```

It runs `pi(1e9)` and `[1e9, 2e9)` across the adaptive default, explicit
segmented sieving, and explicit `prefix-pi`, with a small segment sweep for the
segmented rows. This is intentionally separate from the default external
controls because it exposes whether a count-only workload should use prefix
counting or sustained marking. On the current machine, these rows show
`prefix-pi` is the correct Circle lane for tracked low-absolute broad counts,
while specialized `primecount` remains the bar to beat for pure prime-counting.
The target uses exact `--circle-variant` entries instead of a full segment-size
by count-mode grid, so the adaptive default row is measured once with no
explicit segment-size override. The generated report renders an adaptive
default scorecard before the broader candidate spread so the headline reflects
the behavior users get without explicit tuning flags.

`prime-engine-external-throughput-compare` reruns the same short workload into
candidate artifacts and then gates `circle_prime_default_count` against
`external_primesieve_count` with
`CIRCLE_PRIME_EXTERNAL_THROUGHPUT_MEDIAN_FLOOR` (default `1.0`). This is a
focused regression check for the adaptive low-absolute count defaults; it
deliberately does not require a `primecount` win because `primecount` is the
specialized exact-`pi` implementation we still need to beat.

`prime-engine-external-segment-sweep` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_latest.csv
sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_external_segment_sweep_samples_latest.csv
```

It uses the same command-level `primesieve`/`primecount` controls as
`prime-engine-external-controls-parallel`, but sweeps Circle segment sizes from
`CIRCLE_PRIME_SEGMENT_SIZES`. Include `0` to benchmark the adaptive CLI
default. The harness deduplicates resolved Circle variants, so `0` plus the
current explicit default does not produce duplicate speedup rows. Use this
artifact as the default-change gate when the in-process tuner and subprocess
timings disagree. The report ranks sweep winners by median speedup when the
new median columns are present, while still displaying best-time speedups for
compatibility and peak evidence:

```bash
make prime-engine-external-segment-sweep CIRCLE_PRIME_SEGMENT_SIZES=0,98304,131072,196608,262144
```

`prime-engine-calibrate-defaults` writes:

```text
sidecars/PRIME_ENGINE/results/prime_engine_default_calibration_latest.json
sidecars/PRIME_ENGINE/results/prime_engine_default_calibration_latest.md
```

It reads the latest high-offset quick scorecard, repeated high-offset
confirmation artifact, external segment sweep, external count-mode sweep,
repeated mode-confirmation artifact, and in-process tuner summary as one
evidence pool, preferring `primesieve` rows over `primecount` rows because
`primesieve` is the stronger range-counting control. The high-offset tight
scorecard gets first priority for the tracked `[1e12, 1e12+1e7)` lane because it
is the short focused comparison used to judge the current `primesieve` gap; the
broader quick scorecard fills in ranges not covered by tight. Confirmed
repeated high-offset winners override a single latest high-offset pick when the
current evidence still contains matching candidate rows. Confirmed repeated
mode winners override a single latest mode sweep for the remaining ranges when
the current sweep still contains matching candidate evidence. Unconfirmed
winners are recorded as `unconfirmed_mode_drift` rather than promoted. If no
external sweep exists for a tuned range, calibration falls back to the
in-process tuner summary. The script
then probes the release `circle-prime recommend --count --json` CLI for the
current adaptive default and records whether that default mode/segment/thread
combination is exactly aligned, within the configured median-slowdown tolerance,
slower than tolerance, noisy enough to report without failing, unconfirmed by
repeat mode evidence, or missing default evidence in the sweep.

Use the non-failing target during exploratory and overnight runs:

```bash
make prime-engine-calibrate-defaults
```

Use the check target when you want stale defaults to fail locally or in CI:

```bash
make prime-engine-calibrate-defaults-check
```

`prime-engine-apply-defaults` applies stable calibrated segment-size and
count-mode recommendations to `rust/circle-prime/prime_engine_defaults.json` and
skips noisy external rows by default. External sweep rows must have stable
per-round samples unless `--allow-noisy` is passed directly to
`scripts/apply_prime_engine_defaults.py`; external mode-sweep rows must also be
confirmed by `prime-engine-external-mode-confirm`. Tuning fallback rows are
allowed when no external row covers that range.

```bash
make prime-engine-apply-defaults
make prime-engine-apply-defaults-check
```

Current external-control readout on this machine:

- `primesieve` remains the serious range-counting bar. Prefix defaults now beat
  it on the tracked small true-prefix count rows, `pi(1e9)`, and the tracked
  `[1e9, 2e9)` broad low-absolute count row. The high-offset cold CLI interval
  is near parity in the current
  short command-level run, while the persistent `count-server` row is clearly ahead. The
  comparison is intentionally command-level and therefore noisy, but it records
  actual worker counts. With `CIRCLE_PRIME_THREADS=8`, true-prefix `prefix-pi`
  rows report `1/8` effective Circle thread, broad non-prefix `prefix-pi` rows
  can report `2/8`, and the high-offset interval currently caps to `7/8` under
  the calibrated `1507328` threaded-count default.
- `primecount` remains the specialized prefix `pi(x)` bar, but Circle's
  `prefix-pi` default currently beats it on the tracked 10M and 100M command
  rows. Keep using external controls for confirmation because startup noise can
  move narrow margins.
- The Circle interval counter is faster than `primecount(high - 1) -
  primecount(low - 1)` on the high-offset interval test, because it directly
  sieves only the requested interval.
- If median tuner output and command-level external controls disagree, treat the
  repeated median external-control result as the default-change gate. Noisy
  external winners are reported as `noisy_drift` and skipped by default rather
  than promoted automatically.

`prime-engine-tune` builds the release Rust tuner and sweeps count-mode,
segment-size, and thread-count combinations across the 1M, 10M, 100M, and
`[10^12, 10^12 + 10M)` ranges, writing timestamped CSV/JSON summaries under
`sidecars/PRIME_ENGINE/results/`. The Rust tuner records both best-of-round and
median-of-round timings; the Python summary chooses tuned winners by median
time, using best time only as peak-throughput evidence. This keeps
recommendations from chasing one lucky timing sample. Each candidate receives
an unmeasured warm-up count before timed rounds so first-use initialization does
not bias the mode sweep. It is a tuning harness rather than a correctness gate.

`prime-engine-report` writes a combined Markdown and JSON summary:

```text
sidecars/PRIME_ENGINE/results/prime_engine_report_latest.md
sidecars/PRIME_ENGINE/results/prime_engine_report_latest.json
```

The report reads the latest release benchmark CSV, external-correctness JSON,
external-control CSV/JSON, external count-mode sweep CSV/JSON, repeated
mode-confirmation JSON, high-offset quick scorecard CSV/JSON, external
segment-sweep CSV/JSON, default-calibration JSON, and tuning JSON if they exist.
It summarizes external correctness
status, `primesieve`/`primecount`
best and median speedups, tool versions, fastest in-repo count rows,
high-offset rows, base-prime setup rows, materialized generation rows,
command-level high-offset quick winners, command-level count-mode winners,
command-level segment-sweep winners, and the
median-selected segment/thread result for each tuned range. It also reports the
calibration drift status for
the current adaptive defaults. It also shows compact spreads of primary count
candidates, high-offset quick candidates, and external segment-sweep
candidates, so tuner-favored segment sizes remain visible even when they do not
win a particular run. External segment-sweep winners are ranked by median
speedup when available, with best-speedup columns retained to show peak
throughput and support older artifacts. The high-offset hot/cold summary keeps
the persistent server lane separate from the cold CLI lane and derives a
best-time server/external table when matching `primesieve` or `primecount` rows
are available. It also compares median-selected tuned
winners with current calibrated CLI defaults when calibration evidence is
available, falling back to the default recommendations stored in the tuning
artifact otherwise. Rows backed by current calibration mark stale stored tuning
defaults, so overnight tuning makes stale count-mode, segment-size, or thread
defaults visible without overreacting to best-time noise.
It also lists experimental count lanes such as bit-packed, tracked-byte, and
wheel-30 rows with their slowdown versus the fastest primary row for the same
workload. Missing required input CSV/JSON timing artifacts are reported in the
Markdown instead of causing a partial overnight run to lose the evidence it did
collect; the external metadata sidecars and segment-sweep artifacts are optional
for compatibility with older runs.

`prime-engine-overnight` records the benchmark, external correctness checks,
external controls, count-mode sweep, repeated mode confirmation, throughput
probe, and segment sweep, runs the 8-hour tuner, writes default-calibration
artifacts, then emits the combined report:

```bash
make prime-engine-overnight
```

`prime-engine-overnight-improve` is the source-editing variant. It runs the same
measurement pipeline, applies stable calibrated defaults to the JSON defaults
file, formats Rust, runs `prime-engine-check`, verifies the applied defaults,
runs a focused in-process benchmark comparison and the `primesieve` external
control comparison against candidate artifacts, then refreshes the accepted
benchmark record and parallel default external-control rows only after those
candidate gates pass. It re-runs external correctness against the new adaptive
defaults, then re-runs calibration and the report. Use this when you want an
unattended run to promote measured count-mode and segment defaults while still
keeping compile/test/benchmark/control/correctness/calibration gates in the
loop.

Default calibration keeps raw per-sweep sample stability visible, but repeated
external mode confirmation can make a raw noisy row effectively stable. A mode
recommendation is actionable only when the confirmation record meets the
configured minimum confirmation count and stable-run requirement. Unconfirmed
mode drifts remain non-actionable and are skipped by `prime-engine-apply-defaults`
unless the policy is explicitly relaxed. Within-tolerance calibration rows are
also left alone by the applier, so local tuner noise does not churn the JSON
defaults when the current default is already close to the measured winner.

```bash
make prime-engine-overnight-improve
```

For an overnight benchmark-control record, keep each sample under a timestamped
name:

```bash
mkdir -p sidecars/PRIME_ENGINE/results
while true; do
  stamp=$(date -u +"%Y%m%dT%H%M%SZ")
  python scripts/check_prime_engine.py \
    --benchmark \
    --benchmark-rounds 5 \
    --benchmark-output "sidecars/PRIME_ENGINE/results/prime_engine_benchmark_${stamp}.csv"
  sleep 300
done
```

For an overnight mode/segment/thread search, run the dedicated tuner:

```bash
make prime-engine-tune-night
```

or choose a custom duration and workload:

```bash
python scripts/tune_prime_engine.py \
  --seconds 28800 \
  --rounds 5 \
  --ranges 0:1000000,0:10000000,1000000000:1010000000,100000000000:100010000000,1000000000000:1000010000000 \
  --segment-sizes 4096,8192,16384,32768,65536,131072,196608,262144,524288,1048576,1310720,1376256,1441792,1507328,1572864,2097152,2359296,2621440,3145728,4194304 \
  --thread-counts 1,2,3,4,8 \
  --count-modes segmented,balanced,dynamic,prefix-pi,presieve13,presieve17,wheel30-mark,hybrid-wheel30-mark
```

The tuner validates that every mode/segment/thread candidate returns the same
prime count for a range, warms that exact candidate once, then records best and
median timings for each candidate. The summary selects the tuned `count_mode`,
`segment_size`, `requested_threads`, and effective `threads` per range by median time in
`prime_engine_tuning_latest.json`. It also records whether the CLI's current
default mode/segment/thread recommendation matches that median-selected
candidate. Treat that file as local guidance for the next optimization, not as
proof.

Latest `make prime-engine-tune` sample on this workspace:

```text
median-selected count configurations:
  [0,1000000) -> seg=... threads=... best=...ms median=...ms rate=.../s
  [0,10000000) -> seg=... threads=... best=...ms median=...ms rate=.../s
  [0,100000000) -> seg=... threads=... best=...ms median=...ms rate=.../s
  [1000000000000,1000010000000) -> seg=... threads=... best=...ms median=...ms rate=.../s
```

## Initial Local Benchmark Sample

Command:

```bash
cargo run --release -p circle-prime --bin circle-prime-bench -- --rounds 3
```

Sample output on this workspace:

```text
kind,name,workload,segment_size,result,rounds,best_ms,rate_per_second,baseline,best_speedup
timing,scalar_u64_batch,200000,0,9135,3,182.002,1098889.530,,
timing,segmented_range_count,1000000,262144,78498,3,0.148,6756756756.757,,
timing,segmented_range_count,10000000,262144,664579,3,1.823,5485213783.465,,
timing,segmented_range_count,100000000,262144,5761455,3,22.708,4403694029.930,,
timing,parallel_segmented_range_count_8t,10000000,131072,664579,3,0.708,14124293785.311,,
timing,parallel_segmented_range_count_4t,100000000,131072,5761455,3,8.746,11433908123.517,,
timing,parallel_segmented_range_count_8t,100000000,262144,5761455,3,7.323,13655527306.821,,
timing,cold_process_segmented_range_count,10000000,262144,664579,3,4.140,2415289166.873,,
timing,control_primal_sieve_count,10000000,0,664579,3,3.182,3142801021.410,,
timing,control_simple_sieve_count,10000000,0,664579,3,13.181,758643778.586,,
speedup,segmented_range_count,1000000,262144,78498,3,0.148,6756756756.757,control_primal_sieve_count,2.726
speedup,segmented_range_count,10000000,262144,664579,3,1.823,5485213783.465,control_primal_sieve_count,1.745
speedup,parallel_segmented_range_count_8t,10000000,131072,664579,3,0.708,14124293785.311,control_primal_sieve_count,4.494
speedup,parallel_segmented_range_count_8t,10000000,131072,664579,3,0.708,14124293785.311,control_simple_sieve_count,18.618
```

These are best-of-three baseline timings for comparison only. They include
current release build behavior and should be rerun before claiming any speedup.

The immediate performance target is explicit: keep beating the simple controls,
then beat `control_primal_sieve_count`, then compare against external
`primesieve` for generation/range counting and `primecount` for `pi(x)`-style
counting. If a future optimization cannot improve the strong-control rows end
to end, keep it experimental.
