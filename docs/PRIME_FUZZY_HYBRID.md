# Prime Fuzzy Hybrid

This lane trains a very small bit-level neural prime classifier beside the
deterministic Circle prime engine. The neural model is deliberately treated as
an ordering hint, not as a proof source.

The active contract is:

- Input is binary bits, least significant bit first.
- Labels come from a deterministic primality labeler, either the built-in
  u64 Miller-Rabin reference or the Rust `circle-prime test --json` CLI.
- The model may rank candidates for "find any prime in this window".
- A reported prime is accepted only after deterministic verification.
- Exact count, enumeration, and next-prime claims may not discard candidates
  based only on a neural score.
- Lean supports the deterministic proof boundary through
  `Circle.Core.Horizon`; it does not prove the learned weights.

Run the fast smoke experiment:

```bash
make prime-engine-fuzzy-hybrid-smoke
make prime-engine-fuzzy-hybrid-any-smoke
make prime-engine-fuzzy-hybrid-next-smoke
make prime-engine-bigint-smoke
```

Or run the script directly:

```bash
python scripts/prime_fuzzy_hybrid.py \
  --summary \
  --json-out sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_smoke_latest.json \
  --bit-width 21 \
  --train-low 900000 \
  --train-high 1000000 \
  --eval-low 1000000 \
  --eval-high 1100000 \
  --train-samples 1024 \
  --eval-samples 512 \
  --epochs 80 \
  --residue-moduli 3,5,7,11,13,17,19,23 \
  --search-start 1000000 \
  --search-window 512 \
  --top-k 32 \
  --search-runs 16 \
  --search-stride 4096
```

Run the exact-next control benchmark:

```bash
python scripts/benchmark_prime_fuzzy_hybrid_next.py \
  --summary \
  --starts 1000000,1004096,1008192 \
  --rounds 3 \
  --batch-size 8 \
  --warmup-rounds 1 \
  --top-k 8 \
  --output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_next_latest.csv \
  --sample-output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_next_samples_latest.csv \
  --metadata-output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_next_latest.json
```

Run the any-prime control benchmark:

```bash
python scripts/benchmark_prime_fuzzy_hybrid_any.py \
  --summary \
  --starts 4295061710,4295087310,4295135570 \
  --rounds 3 \
  --batch-size 8 \
  --warmup-rounds 1 \
  --bit-width 33 \
  --train-low 4294900000 \
  --train-high 4295300000 \
  --search-window 2048 \
  --top-k 16 \
  --score-limit 64 \
  --output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_any_latest.csv \
  --sample-output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_any_samples_latest.csv \
  --metadata-output sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_any_latest.json
```

That benchmark writes a Rust-readable model file to
`target/prime-controls/prime-fuzzy-hybrid-model.txt` and includes two hybrid
rows:

- `circle_fuzzy_hybrid_python_exact_next`
- `circle_fuzzy_hybrid_rust_server_exact_next`

The Rust row runs the same trained model through:

```bash
circle-prime fuzzy-server target/prime-controls/prime-fuzzy-hybrid-model.txt \
  --mode exact-next \
  --window 512 \
  --top-k 8
```

The Makefile target also runs `scripts/check_prime_fuzzy_hybrid_next.py` to
validate row coverage, result agreement, proof-contract metadata, tool versions,
current milestone wins over the Python hybrid and deterministic Python
reference, and conservative non-toy floors against Circle `next-server`,
`libprimesieve` generate, and `libprimecount`.

For labels from the Rust Circle solver:

```bash
cargo build --quiet -p circle-prime --bin circle-prime
python scripts/prime_fuzzy_hybrid.py \
  --labeler circle-prime \
  --circle-prime-bin target/debug/circle-prime \
  --summary \
  --json-out sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_circle_latest.json \
  --bit-width 16
```

There are two different scores to keep separate:

- `prime-engine-fuzzy-hybrid-smoke` measures loose "find any prime in this
  window" ordering. It can show whether the model is learning useful ranking
  signal, but it is not a next-prime speed claim.
- `prime-engine-fuzzy-hybrid-any-smoke` measures wall-clock any-prime search on
  starts with longer deterministic gaps. The fuzzy row may report a later prime
  than the next-prime controls, but every reported prime must be
  deterministically verified and inside the bounded window. The Rust server
  scores only the configured prefix budget before fallback; this keeps neural
  overhead bounded.
- `prime-engine-fuzzy-hybrid-next-smoke` measures exact next-prime semantics.
  The neural hint may be checked first, but the result is accepted only after a
  deterministic next-prime proof path certifies the result, either through
  Circle's static exact tables or by verifying every earlier deterministic
  wheel candidate in the bounded window. This target compares both the Python
  hybrid path and the Rust `fuzzy-server` path with deterministic Python MR64,
  Circle `next-server`, `libprimesieve`, and `libprimecount` controls.
  In exact-next mode, `top_k` is the early-candidate scoring budget; the best
  scored hint is compared with the deterministic result for diagnostics, while
  the deterministic next-prime proof path controls the accepted result.

The first promotion score is deterministic checks for the loose ordering lane.
The exact-next benchmark is expected to expose overhead until the Rust
implementation can use the learned signal without weakening the proof boundary
or adding more deterministic checks than the baseline path.
The default smoke gate is intentionally below a victory claim for Circle and
`primesieve`; it exists to keep the lane attached to real competitors while
iteration continues.

## Arbitrary-Precision Lane

The Rust CLI now has a separate arbitrary-precision path:

```bash
circle-prime big-test N --rounds 64 --json
circle-prime big-test N --profile bpsw --json
circle-prime big-next START --rounds 64 --max-candidates 1000000 --json
circle-prime big-next START --profile bpsw --max-candidates 1000000 --json
circle-prime big-fuzzy-search MODEL START \
  --candidate-window 512 \
  --top-k 16 \
  --score-limit 128 \
  --rounds 64 \
  --json
circle-prime big-test-server --rounds 64
circle-prime big-next-server --rounds 64 --max-candidates 1000000
circle-prime big-fuzzy-server MODEL \
  --candidate-window 512 \
  --top-k 16 \
  --score-limit 128 \
  --rounds 64
```

This path is deliberately not merged into the u64 proof contract. For inputs
that fit in `u64`, `big-test` delegates to the exact deterministic classifier.
For larger `BigUint` inputs, accepted candidates are probable primes from
trial division plus a selected probable-prime profile. The default `mr`
profile uses configured fixed Miller-Rabin bases. The optional `bpsw` profile
uses base-2 Miller-Rabin plus a strong Lucas-Selfridge check. Composite results
are exact when a small factor or witness is found; prime results above `u64`
are still probable-prime reports, not formal primality certificates.

`big-fuzzy-search` keeps the same safety rule as the smaller fuzzy lane: the
model only ranks candidates, and every reported candidate must pass the
BigUint probable-prime verifier. Its JSON reports
`deterministically_verified=false` for large probable-prime results so the
boundary is visible in benchmark artifacts.

Run the large-prime control smoke:

```bash
make prime-engine-bigint-smoke
```

That target compares Circle `big-test` against OpenSSL `prime -checks N` and
SymPy `isprime` on known 127/255/256/521-bit prime/composite cases, then
compares `big-next` against SymPy `nextprime`. It also runs a fuzzy any-prime
search smoke and verifies the reported candidate with SymPy. The benchmark
records both cold one-shot CLI rows and hot `big-*-server` rows; use the hot
server rows for engine tuning because they remove process startup from the
measurement. It also records hot `bpsw` profile rows for `big-test-server` and
`big-next-server`, so the fixed-base Miller-Rabin and Baillie-PSW-style
profiles can be compared without changing the proof boundary. The output lives at
`sidecars/PRIME_ENGINE/results/prime_bigint_controls_latest.csv` with metadata
in `prime_bigint_controls_latest.json`.

Current local smoke status from 2026-06-21:

- 16-round `prime-engine-bigint-smoke` agrees with OpenSSL and SymPy on every
  selected large-prime case.
- Hot Circle `big-test-server` is faster than OpenSSL `prime -checks 16` on
  every selected 127/255/256/521-bit primality case. Latest medians include
  `0.595 ms` for the Curve25519 prime, `0.657 ms` for the secp256k1 field
  prime, and `2.465 ms` for the 521-bit Mersenne prime. SymPy `isprime`
  remains faster on most raw primality checks, though Circle is now close on
  the Curve25519 case in this local smoke.
- Hot Circle `big-next-server` agrees with SymPy on the selected 127-bit and
  near-255-bit starts. It is still slower than SymPy on the 127-bit start
  (`0.237 ms` versus `0.175 ms`), but is faster than SymPy on the near-255-bit
  start (`0.991 ms` versus `1.715 ms`) in the latest 16-round smoke.
- A single-sample 64-check probe still agrees on every case. Hot Circle
  `big-test-server` beats OpenSSL on every selected primality check at that
  setting, including the 521-bit Mersenne prime, but remains slower than SymPy.
- BigUint fuzzy any-prime search is correct in the smoke and its value-only
  server path now skips diagnostic baseline scans. It beats SymPy on the
  near-255-bit any-prime case (`1.104 ms` versus SymPy next-prime at
  `1.715 ms`), but remains slower than deterministic `big-next-server`; it is
  not promoted as a deterministic-speed win yet.

Near-term promotion requirements:

- Keep the model tiny enough that inference is cheaper than one meaningful
  deterministic primality check.
- Verify every accepted prime through the deterministic Rust path.
- Record false positives, false negatives, precision, recall, and F1 on
  held-out ranges.
- Compare against existing prime-engine controls before claiming speed.
- Add a Lean-facing wrapper theorem only for the deterministic acceptance rule,
  not for model quality.
- For arbitrary-precision claims, add a certificate path such as Pratt,
  Pocklington, ECPP, or an externally checkable certificate before saying
  "proved prime" above `u64`.
