# Prime Engine Sidecar

This sidecar stores optional local benchmark artifacts for the Rust-backed
Circle prime engine.

The default repository checks do not depend on generated benchmark files.
Use:

```bash
make prime-engine-benchmark-record
make prime-engine-external-controls
make prime-engine-external-next
make prime-engine-tune
```

to run the release benchmark gate and write the latest CSV sample to
`sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv`, compare
against optional external `primesieve`/`primecount` tools, benchmark
next-prime search against CLI and direct `libprimesieve` controls, or sweep
segment sizes and write tuning CSV/JSON summaries.

`controls/primesieve_next_server.c` is a small benchmark helper for the
next-prime scorecard. The Python harness compiles it into `target/` and uses it
as a persistent line server around
`primesieve_generate_n_primes(1, START, UINT64_PRIMES)`.

Benchmark and tuning files are local performance evidence, not proof artifacts.
Lean proof status is tracked through `Circle/Core/Horizon.lean` and
`manifests/theorem_manifest.yaml`.
