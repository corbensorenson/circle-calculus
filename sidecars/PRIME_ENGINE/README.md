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
make prime-engine-external-next-server
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
`libprimesieve`, repeated high-offset default confirmation, fresh high-offset
candidate confirmation, the focused next-prime server-only scorecard, the
broader next-prime comparison, default-calibration drift check, and the
combined report. The
control rows use interleaved samples,
persistent Circle count-server rows, CLI `primesieve`/`primecount`, and a
persistent `libprimesieve` count helper when the local headers/library are
available. Count timings batch repeated requests inside each timed sample and
report per-request timings; persistent count-server rows send these as
`repeat COUNT ...` requests to both Circle and the `libprimesieve` helper. This
keeps sub-10 ms rows meaningful without turning the target into an overnight
job. Overnight targets are optional regression/tuning jobs, not the primary way
to learn whether Circle is competitive.

`make prime-engine-high-offset-confirm` is the stricter short gate for the
remaining hard high-offset count lane. It runs warmed repeated confirmations
against the persistent `libprimesieve` count helper and the adaptive Circle
server default row. Fresh confirmation runs also batch repeated count requests
and report per-request timings, so default changes require a repeatable win
rather than a one-run median. This target focuses the timing loop on
`circle_prime_server_default_count` versus `external_primesieve_count_server`
across the hot-server range set by default and requires two stable median wins
across three runs for each observed range. The broader
`prime-engine-competitive-short` target includes this gate, refreshes
candidate-confirmation evidence after the hot-server scorecard, and also
refreshes CLI controls, candidate spreads, and next-prime evidence.

The current adaptive high-offset default uses `presieve13` through the tracked
lower and middle high-offset band, and `segmented` at the upper tracked edge.
The hot-server check passes across the full tracked range set, but the
promotion readout is intentionally treated as a candidate scout rather than an
automatic flip switch. Boundary candidates need repeated A/B confirmation plus
a passing post-promotion hot-server gate before another default change.

`make prime-engine-external-next-server` is the fast next-prime throughput gate.
It skips cold command invocations and compares persistent Circle `next-server`
requests directly against the persistent `libprimesieve` helper using
`primesieve_generate_n_primes(1, START, UINT64_PRIMES)`. The default starts are
`90`, `1000000`, `4294967000`, and `1000000000000`, with `50` repeated
searches sent as one `START COUNT` request per timed sample and `9` rounds, so
small-start results are measured as server throughput instead of process-launch
noise. The default gate requires every selected row to beat the helper by
median speed, and requires at least a `1.05x` median speedup on the material
non-tiny rows `1000000`, `4294967000`, and `1000000000000`. Strict
sample-stability failure can be enabled with
`CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_REQUIRE_STABLE_SAMPLES=1`.

`make prime-engine-high-offset-candidate-confirm` is the focused scout for
variants that look faster than the adaptive default in the hot-server spread.
It repeats exact persistent-server variants against persistent `libprimesieve`
and writes `prime_engine_high_offset_candidate_confirmation_latest.{json,md}`.
The confirmation JSON also records per-identity evidence for each exact
mode/segment/thread row in the scout grid. Use it before changing defaults; a
candidate winner still has to clear the combined report's promotion readout and
survive `make prime-engine-high-offset-hot-server-check` after promotion. The
promotion readout currently requires at least a `1.050x` median gain over the
adaptive default plus candidate-confirmation evidence that is at least as fresh
as the hot-server scorecard before marking a confirmed non-default candidate as
trial-ready, which keeps sub-3 ms timing noise and stale scout runs from
forcing churn.

`make prime-engine-high-offset-hot-server-check` reads the latest hot-server
scorecard and fails unless the selected adaptive Circle server default rows
beat the persistent `libprimesieve` count helper by median speed with stable
samples, unless a noisy row already clears the material-win bypass
`CIRCLE_PRIME_HIGH_OFFSET_HOT_SERVER_NOISY_MEDIAN_BYPASS` (default `1.5`).
By default it checks the full hot-server range set with a parity-plus `1.0`
median-speedup floor.

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
