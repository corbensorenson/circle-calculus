# Prime Engine Sidecar

This sidecar stores optional local benchmark artifacts for the Rust-backed
Circle prime engine.

The default repository checks do not depend on generated benchmark files.
Use:

```bash
make prime-engine-competitive-short
make prime-engine-proof-contract
make prime-engine-benchmark-record
make prime-engine-external-controls
make prime-engine-external-next
make prime-engine-tune
```

to run the short competitive count scorecard first, check the standalone
Lean/Rust proof-contract boundary, then optionally run the release benchmark
gate and write the latest CSV sample to
`sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv`, compare
against external `primesieve`/`primecount` tools, benchmark next-prime search
against CLI and direct `libprimesieve` controls, or sweep segment sizes and
write tuning CSV/JSON summaries.

`make prime-engine-competitive-short` is the default orientation target for
daytime iteration. It runs the external correctness matrix, warmed persistent
count controls, the prime proof-contract gate, the high-offset hot-server
scorecard, a focused hot-server win/stability gate against persistent
`libprimesieve`, repeated high-offset confirmation, the focused next-prime
comparison, default-calibration drift check, and the combined report. The
control rows use interleaved samples,
persistent Circle count-server rows, CLI `primesieve`/`primecount`, and a
persistent `libprimesieve` count helper when the local headers/library are
available. Count timings batch repeated requests inside each timed sample and
report per-request timings, which keeps sub-10 ms rows meaningful without
turning the target into an overnight job. Overnight targets are optional
regression/tuning jobs, not the primary way to learn whether Circle is
competitive.

`make prime-engine-high-offset-confirm` is the stricter short gate for the
remaining hard count lane near `1e12`. It runs warmed repeated confirmations
against the persistent `libprimesieve` count helper and the adaptive Circle
server default row. Fresh confirmation runs also batch repeated count requests
and report per-request timings, so default changes require a repeatable win
rather than a one-run median. This target focuses the timing loop on
`circle_prime_server_default_count` versus `external_primesieve_count_server`
by default and requires two stable median wins across three runs. The broader
`prime-engine-competitive-short` target includes this gate and also refreshes
CLI controls, candidate spreads, and next-prime evidence.

`make prime-engine-high-offset-hot-server-check` reads the latest hot-server
scorecard and fails unless the selected adaptive Circle server default rows
beat the persistent `libprimesieve` count helper by median speed with stable
samples. By default it checks the tracked high-offset comparison range with a
parity-plus `1.0` median-speedup floor.

Short-run sample stability ignores a single high outlier when there are at
least five samples, but still marks repeated high samples as noisy. This keeps
sub-10 ms server comparisons from being decided by one scheduler spike while
preserving a conservative confirmation threshold.

`make prime-engine-high-offset-thread-sweep` is a narrower diagnostic for that
same lane. It fixes the high-offset range and sweeps exact Circle
mode/segment/thread variants against the persistent `libprimesieve` count
helper with the same batched timing policy. Use it when Circle is near parity
and you need a quick read on whether thread count or segment geometry, rather
than sieve semantics, is driving the gap.

`controls/primesieve_next_server.c` is a small benchmark helper for the
next-prime scorecard. The Python harness compiles it into `target/` and uses it
as a persistent line server around
`primesieve_generate_n_primes(1, START, UINT64_PRIMES)`.

`controls/primesieve_count_server.c` is the matching count-control helper. It
keeps a `libprimesieve` process alive and calls
`primesieve_count_primes(LOW, HIGH-1)` for half-open Circle benchmark ranges.

Benchmark and tuning files are local performance evidence, not proof artifacts.
Lean proof status is tracked through `Circle/Core/Horizon.lean` and
`manifests/theorem_manifest.yaml`.
