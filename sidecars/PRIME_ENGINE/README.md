# Prime Engine Sidecar

This sidecar stores optional local benchmark artifacts for the Rust-backed
Circle prime engine.

The default repository checks do not depend on generated benchmark files.
Use:

```bash
make prime-engine-competitive-status
make prime-engine-competitive-short
make prime-engine-fuzzy-hybrid-smoke
make prime-engine-fuzzy-hybrid-next-smoke
make prime-engine-bigint-smoke
make prime-engine-proof-contract
make prime-engine-benchmark-record
make prime-engine-external-controls
make prime-engine-external-next
make prime-engine-external-next-server
make prime-engine-high-offset-shifted-hot-server
make prime-engine-high-offset-shifted-hot-server-confirm
make prime-engine-tune
```

to read the current competitive status from provenance-checked artifacts,
refresh the short competitive count scorecard when new data is needed, check
the proof-bounded fuzzy hybrid lane, check the standalone Lean/Rust
proof-contract boundary, then optionally run the release benchmark gate and
write the latest CSV sample to
`sidecars/PRIME_ENGINE/results/prime_engine_benchmark_latest.csv`, compare
against external `primesieve`/`primecount` tools, benchmark next-prime search
against CLI, direct `libprimesieve`, and direct `libprimecount` controls, or
sweep segment sizes and write tuning CSV/JSON summaries.

`make prime-engine-competitive-status` is the default readout after a benchmark
run already exists. It checks the proof-contract boundary, replays the
broader external-control, fixed high-offset, shifted high-offset, and
next-prime gates against current artifact fingerprints, runs
default-calibration drift checks, refreshes the combined report, and fails only
when a real fixed-default or shifted-lane trial decision is waiting.
The artifact checks rebuild the release `circle-prime` binary before comparing
hashes, so source edits cannot accidentally pass against an older binary.
These gates also assert artifact shape: broader external controls must be the
expected interleaved batched profile and range set, fixed high-offset must be
the expected identical-repeat server profile and range set, shifted high-offset
must be the expected `shifted` profile and shift, and next-prime must be the
expected server-only start set. That keeps a stale or wrong-profile artifact
from accidentally satisfying a short status check.

`make prime-engine-competitive-short` is the default refresh target for
daytime iteration. It runs the external correctness matrix, warmed persistent
count controls, the prime proof-contract gate, the high-offset hot-server
scorecard, a focused hot-server win/stability gate against persistent
`libprimesieve` and `libprimecount`, repeated high-offset default
confirmation, refreshed shifted high-offset confirmation, fresh high-offset
candidate confirmation, the focused next-prime server-only scorecard, the
broader next-prime comparison, default-calibration drift check, and the combined
report plus promotion/readout gates. The control rows use interleaved samples,
persistent Circle count-server rows, CLI `primesieve`/`primecount`, persistent
`libprimesieve` count helpers, and persistent `libprimecount` pi-diff helpers
when the local headers/libraries are available. Count timings batch repeated
requests inside each timed sample and
report per-request timings; persistent count-server rows send these as
`repeat COUNT ...` requests to Circle and enabled external helpers. This
keeps sub-10 ms rows meaningful without turning the target into an overnight
job. Circle's exact repeat path computes the identical range once and replays
the response lines, so exact-repeat rows are service replay throughput evidence
rather than fresh-interval evidence. The competitive smoke uses shifted batches
of `40` requests per timed sample; batch `20` is more exposed to helper timing
noise, while batch `80` can over-widen the adjacent-union count and lose median
stability on this machine. Overnight targets are optional
regression/tuning jobs, not the primary way to learn whether Circle is
competitive.
The latest refreshed smoke on 2026-06-22 passes current-binary provenance and
has `circle_prime_count_binary_server_default_count` at `1.364x` median over
persistent `libprimesieve` and `8.749x` median over persistent `libprimecount`
pi-diff on `[1e12, 1e12 + 1e7)` shifted batches. The matching external
correctness matrix checked `826` Circle variants against `primesieve` and
`primecount`.

`make prime-engine-fuzzy-hybrid-smoke` trains and evaluates the tiny bit-level
neural ordering model in `scripts/prime_fuzzy_hybrid.py`, writes
`sidecars/PRIME_ENGINE/results/prime_fuzzy_hybrid_smoke_latest.json`, and
checks whether neural ordering reduced deterministic candidate checks in a
batch of held-out search windows. This is not a proof or wall-clock speed claim: any
reported prime still comes from deterministic verification, and exact
count/enumeration workflows cannot discard candidates by neural score.
`make prime-engine-fuzzy-hybrid-any-smoke` is the wall-clock candidate lane for
that same relaxed operation: it benchmarks Python and Rust fuzzy any-prime
search against deterministic Python MR64, Circle `next-server`,
`libprimesieve`, and `libprimecount` on starts with longer deterministic gaps.
The fuzzy result may be a later prime than the next-prime controls; the checker
only accepts it if it is deterministically prime and inside the bounded window.
The Rust server scores only a bounded candidate prefix before deterministic
fallback so neural overhead remains visible and controlled in the artifact.
The refreshed gate now requires at least `0.55x` median versus Circle
`next-server` and at least `1.5x` median versus persistent `libprimesieve`
generate-next at every tracked start. The latest artifact has Rust fuzzy
any-prime at `2.435x`, `2.241x`, and `1.921x` median over `libprimesieve`
generate-next, and `0.674x`, `0.696x`, and `0.665x` median versus Circle
`next-server`, so this lane is useful against external controls but is still
not promoted as a deterministic next-prime replacement.
`make prime-engine-fuzzy-hybrid-next-smoke` is the comparable exact-next gate:
it writes `prime_fuzzy_hybrid_next` CSV/sample/metadata artifacts and compares
the current Python hybrid exact-next path and Rust `circle-prime fuzzy-server`
path against deterministic Python MR64, Circle `next-server`, `libprimesieve`,
and `libprimecount`. The benchmark exports the trained model to
`target/prime-controls/prime-fuzzy-hybrid-model.txt`; accepted exact-next
results still require Circle's deterministic next-prime proof path, either
through static exact tables or by verifying every earlier deterministic wheel
candidate in the bounded window. The exact-next `top_k` setting is an early
deterministic-wheel-candidate scoring budget; the best scored hint is compared
with the deterministic result for diagnostics, so it is not a whole-window skip
permission.
The checker requires wins over the Python lanes and conservative floors against
Circle `next-server`, `libprimesieve` generate, and `libprimecount`; those
floors are guardrails, not victory claims.

`make prime-engine-bigint-smoke` is the arbitrary-precision smoke gate. It
builds the release `circle-prime` binary, checks `big-test` on known
127/255/256/521-bit prime/composite cases against OpenSSL `prime -checks N`
and SymPy `isprime`, checks `big-next` against SymPy `nextprime`, and runs a
BigUint fuzzy any-prime smoke. The artifact includes both cold CLI rows and hot
`big-test-server`/`big-next-server`/`big-fuzzy-server` rows so large-prime
tuning is not dominated by process startup. This lane reports probable-prime
status above `u64`; it is not a Lean-certified primality certificate yet.
When available, the same benchmark now adds optional GMP/gmpy2 rows
(`gmpy2_is_prime`, `gmpy2_next_prime`) and optional PARI/GP rows
(`pari_gp_ispseudoprime`, `pari_gp_isprime`, `pari_gp_nextprime`). These rows
are agreement-checked when present, and can be made mandatory with
`CIRCLE_PRIME_BIGINT_EXTRA_ARGS=--require-gmpy2` plus
`CIRCLE_PRIME_BIGINT_CHECK_EXTRA_ARGS=--require-gmpy2-controls`, or
`CIRCLE_PRIME_BIGINT_EXTRA_ARGS=--require-pari-gp` plus
`CIRCLE_PRIME_BIGINT_CHECK_EXTRA_ARGS=--require-pari-gp-controls`.
`big-test` and `big-next` now accept `--profile mr|bpsw`: `mr` uses the fixed
Miller-Rabin base bank, while `bpsw` uses base-2 Miller-Rabin plus strong
Lucas-Selfridge. The BigUint smoke records hot BPSW profile rows for test and
next-prime searches beside the default Miller-Rabin rows. In the latest local
smoke, hot BPSW beats SymPy on the selected raw-primality and large next-prime
searches, and the BPSW-backed fuzzy server beats SymPy `nextprime` under the
configured hot-server floor. The current hot path caches limb digits
for small-prime trial division, keeps incremental small-prime residues during
`big-next` wheel search, and uses a value-only fuzzy server path when JSON
diagnostics are not requested. The BPSW hot path also uses value-only
`big-test-server` status checks for non-JSON requests, skips BigUint square
roots when the candidate is not a square residue modulo 64, replaces several
Lucas `% n` operations with bounded modular add/double steps, specializes the
Selfridge `Q = -1` recurrence and strong-Lucas doubling tail, uses a short
pre-BPSW trial list through 47, and uses a fold-and-subtract reducer for
non-`Q = -1` Lucas work over pseudo-Mersenne moduli `2^k - c`. The BPSW-backed
fuzzy value path uses deterministic BPSW next directly for small starts where
model scoring is slower than direct verification.
Use `make prime-engine-bigint-raw-sympy-promotion-check` for that stricter
promotion gate. It reuses the latest BigUint artifact and requires hot BPSW
raw primality to beat SymPy `isprime` on the selected prime-like cases; it
remains separate from the default smoke so the raw-primality promotion claim is
explicit.
Use `make prime-engine-bigint-raw-sympy-confirm` for repeated confirmation: it
reruns a focused hot-batched raw-primality benchmark several times, applies
the same promotion floor on each run, and records the weakest observed speedup
by case. The latest 3-run confirmation passes: weakest BPSW-over-SymPy
speedups are `1.783x` on the 127-bit Mersenne prime, `1.161x` on Curve25519,
`1.140x` on secp256k1, and `2.941x` on the 521-bit Mersenne prime.
Use `make prime-engine-bigint-next-fuzzy-confirm` for the large next-prime and
fuzzy split. It repeats only hot BPSW `big-next-server`, hot BigUint
`big-fuzzy-server --profile bpsw`, and SymPy `nextprime` rows. The latest
3-run confirmation uses 15 measured samples per run and passes both the
deterministic `1.1x` BPSW-next-over-SymPy floor and the `1.0x`
BPSW-backed-fuzzy-over-SymPy floor. Weakest BPSW-next-over-SymPy speedups are
`2.327x` at `2^127` and `2.006x` near Curve25519; weakest
BPSW-backed-fuzzy-over-SymPy speedups are `2.324x` and `1.736x`. Fuzzy is now
near parity with deterministic BPSW next at `2^127` because the hybrid takes
the deterministic fast path there, but it still trails deterministic BPSW next
near Curve25519 with a weakest fuzzy-over-BPSW-next speedup of `0.828x`.

`make prime-engine-high-offset-shifted-hot-server` is the harder diagnostic for
the same high-offset lane. It keeps the server processes hot, but advances each
request in a timed batch by `10000000` by default instead of repeating the
exact same interval. This measures fresh nearby intervals and blocks exact-range
reuse from flattering the result. The shifted benchmark protocol now sends one
native `shifted COUNT SHIFT ...` batch request to Circle and the external C
helpers, so all servers flush once per timed batch. Circle parses that shifted
batch once and dispatches the shifted intervals through the count-server worker
pool instead of synchronizing once per interval. `make
prime-engine-high-offset-shifted-hot-server-confirm` repeats the current top
shifted candidates over 13 rounds at batch size `80`, so sub-3 ms shifted rows
are less exposed to scheduler spikes. The latest focused shifted confirmation
has the adaptive default at `1.286x` median and `1.416x` best speedup versus
persistent `libprimesieve` on `[1e12, 1e12 + 1e7)` shifted batches, and
`7.674x` median and `7.054x` best speedup over persistent `libprimecount`
pi-diff, with mixed samples.
Native shifted default batches now use the measured edge high-offset
`presieve13:1310720` plan, which resolves to 8 effective workers for this
10M span while leaving fixed high-offset defaults unchanged. The full and slim
shifted servers also over-split adjacent shifted unions into multiple chunks
per worker and use scoped atomic work pulling so a single slow worker does not
dominate the batch. The apparent
best-vs-default gain in the latest shifted-candidate readout is `1.000x`, so
the shifted gate records `keep_default` rather than a new trial candidate.
The combined report has a shifted-candidate readout: it records
best-vs-default fresh-interval gains and only flags a shifted trial when a
non-default row clears a `1.050x` median gain over the adaptive default. The
current best executable plan remains the adaptive default, so the active
high-offset target is widening the adaptive default's fresh-interval margin
without regressing fixed hot-server and next-prime gates.
Circle's persistent `count-server` also maintains a reusable bitset-backed
small-prefix `pi` table through `2000000000` for `prefix-pi` ranges whose
`HIGH - 1` falls inside that limit. This is a hot-service precomputation, not
whole-result caching; `count-server --warm-prefix-pi-cache` pays the build at
startup, while cold CLI rows still measure the raw exact counter. The default
limit is `2000000000`; set `CIRCLE_PRIME_SMALL_PREFIX_PI_CACHE_LIMIT` lower for
leaner services or up to the `3000000000` cap for short larger-prefix probes
before changing defaults.
`make prime-engine-prefix-cache-probe` runs the 2B validation probe for
`[1e9, 2e9)` and writes the `prime_engine_external_controls_2b_prefix_probe`
artifacts; `make prime-engine-prefix-cache-probe-3b` writes the parallel 3B
`[2e9, 3e9)` probe. Current measured startup/memory: 2B uses about
`187500004` bytes and warms in `6648.603 ms`; 3B uses about `281250004` bytes
and warms in `10254.914 ms`.
The same 2B probe now requires the cold default row to stay ahead of cold
`primecount` pi-diff and cold `primesieve`; the latest readout is `2.124x`
median over `primecount` and `4.060x` median over `primesieve`.
The refreshed standard controls also have the cold `pi(1e9)` row stable at
`4.093 ms` median and `1.124x` median over cold `primecount`. `make
prime-engine-prefix-1b-confirm` is the focused short check for that lane; the
latest 17-round run has Circle at `4.857 ms` median and `1.111x` median over
cold `primecount`, with the row still marked noisy because of local outliers.

The non-JSON next-prime server path uses a value-only exact search and direct
ASCII `u64` writes while JSON still carries the full proof contract. The
standard server-only gate now has Circle ahead at every checked start against
the two persistent `libprimesieve` controls. In the latest accepted artifact,
Circle reads `1.283x`, `2.390x`, `8.176x`, and `45.154x` median over
persistent `libprimesieve` generate-next at starts `90`, `1000000`,
`4294967000`, and `1000000000000`. The same starts read `30.294x`, `38.192x`,
`36.269x`, and `154.140x` median over the persistent `libprimesieve` iterator
helper. The tracked material rows pass the server gate.

`make prime-engine-external-next-shifted` is the stricter fresh-start
next-prime gate. It sends native `shifted COUNT SHIFT START` requests to
Circle's `next-server` and the persistent `libprimesieve` helpers, so each
timed sample checks many distinct nearby starts with one server flush instead
of repeating an identical start. The row result is a checksum of the entire
prime vector, and every engine must match the vector per pass before speedups
are recorded. The latest shifted artifact uses batch size `64`, shift `4096`,
5 timed rounds, and 1 warmup round. Circle's median speedups over persistent
`libprimesieve` generate-next are `1.291x`, `1.396x`, `5.086x`, and `34.651x`
at starts `90`, `1000000`, `4294967000`, and `1000000000000`; against the
persistent iterator helper they are `12.528x`, `13.996x`, `38.864x`, and
`125.170x`. The shifted iterator row at `4294967000` is noisy but clears the
noisy-win bypass.

`make prime-engine-high-offset-confirm` is the stricter short gate for the
remaining hard high-offset count lane. It runs warmed repeated confirmations
against the persistent `libprimesieve` count helper and the adaptive Circle
server default row. Fresh confirmation runs also batch repeated count requests
and report per-request timings; the default uses `80` repeated count requests
per timed sample. Circle exact-repeat batches replay the same computed response,
so default changes still require shifted or cold corroboration before being
treated as algorithmic wins. This target focuses the timing loop on
`circle_prime_server_default_count` versus `external_primesieve_count_server`
across the hot-server range set by default and requires two stable median wins
across three runs for each observed range. The broader
`prime-engine-competitive-short` target includes this gate, refreshes
candidate-confirmation evidence after the hot-server scorecard, and also
refreshes CLI controls, candidate spreads, next-prime evidence, the combined
report, and the promotion-readout gate.

The current adaptive high-offset default uses `presieve13:1507328` with the
promoted edge-band segment at the tracked edge, `presieve17` through the lower
tracked band, and `presieve13` through the middle and upper tracked high-offset
bands. The edge default resolves to 7 effective workers for the tracked 10M
span. The scoped parallel counters run one chunk on the caller thread, request a
128 KiB stack for worker threads, and spawn workers only for the remaining
chunks. That trims cold command thread startup while keeping the same half-open
range split; persistent `count-server` rows still matter because they avoid
repeated process setup, keep a reusable worker pool, cache adaptive default
plans, and count one chunk on the server thread while workers handle the rest.
Rejected cold-startup-only levers now include release symbol stripping,
undersizing/removing the embedded base-prime table, direct ASCII count output,
and serial shared-plan construction across adjacent cold chunks; none produced a
credible win on the tracked cold high-offset lane. The shared-plan probe fell to
about `0.595x` median versus cold `primesieve`, so the repeated per-worker setup
is still better than serializing mark-plan construction. A local release probe
also rejected reusing the shifted single-segment path across adjacent cold chunks
because its median was about `7.61 ms` versus `2.47 ms` for the current
parallel path.
The hot-server check passes across the full tracked range set, but the
promotion readout is intentionally treated as a candidate scout rather than an
automatic flip switch. Boundary candidates need repeated A/B confirmation plus
a passing post-promotion hot-server gate before another default change.

`make prime-engine-high-offset-count-binary` is a short diagnostic for the slim
`circle-prime-count` executable. It measures the full CLI, the count-only CLI,
persistent Circle `count-server`, and the persistent external helpers in one
interleaved run. The current count-only binary is useful evidence because it
removes unrelated command surfaces while supporting `default`, `segmented`,
`balanced`, `dynamic`, `presieve13`, and `presieve17`; `prefix-pi` stays out of
the slim binary to avoid cold-start bloat. Shifted count-server batches detect
adjacent windows when the shift equals the range span and sieve the full union
once, binning flags back into the requested intervals for both `presieve13` and
`presieve17`; non-adjacent shifted requests fall back to the shifted
single-segment mark plan. The latest lower-thread cold sweep keeps the
count-only CLI below a clean promotion: the current adaptive default
(`presieve13:1507328`, 7 effective workers) reached `0.866x` median and
`0.884x` best versus cold `primesieve`, while the best expanded row
(`presieve17:1310720`, 8 effective workers) reached `0.873x` median and
`0.882x` best. `make
prime-engine-high-offset-count-binary-cold-candidate-check` rejected the lane
again with no trial-ready candidate and best default-relative gain only
`1.008x`. Treat the cold one-shot lane as below-parity until a candidate beats
cold `primesieve` by both median and best time. Earlier probes also rejected
`presieve13:1703936`, `presieve13:1835008`, `presieve13:4194304`,
`presieve17:3670016`, and one-shot worker-pool variants; noisy median parity
without best-time parity is not a promotion. The same exact-repeat probe has persistent Circle
`count-server` at `18.627x` median versus persistent `libprimesieve`, and the
slim count-binary server row at `18.722x` median versus persistent
`libprimesieve`; those are hot-service repeat throughput numbers, while the
shifted fresh-interval count-binary probe is the cleaner competitive count
claim at `1.227x` median versus persistent `libprimesieve`.
`make prime-engine-high-offset-count-binary-check` validates that artifact,
including the recorded `circle-prime-count` hash, the cold count-binary
adaptive-default row against cold `primesieve`, and the persistent Circle
server default row against persistent `libprimesieve`. The provenance gate also
requires the recorded external controls to be at least the current release
baselines (`primesieve 12.14`, `primecount 8.5`) wherever those controls are
part of the claim, so stale local tools cannot make a weak comparison look
strong. The generated report also starts with an external-control provenance
table for the key count, smoke, high-offset, shifted, and next-server artifacts,
including control versions, helper methods, paths, and helper binary/source
hashes.
`make prime-engine-high-offset-count-binary-overhead-check` classifies the same
artifact and now also reads `prime_engine_high_offset_hot_cold_latest.csv` so
the startup diagnosis has a local hot/cold decomposition gate; the competitive
status targets refresh that hot/cold artifact before enforcing the check. The
current diagnosis remains `cold_process_or_startup_bound`: the slim count-binary
server is already `18.722x` versus persistent `libprimesieve`, while cold
one-shot rows still trail cold `primesieve` on best time. The enforced best-time
split is cold `circle-prime-count` at `4.997 ms`, persistent default
`count-server` at `1.741 ms`, no-op
fresh-process floor at `1.720 ms`, scoped-spawn-only floor at `1.856 ms`,
cold/hot `2.87x`, no-op share `0.53x`, and scoped-spawn share `0.57x`
of the cold-over-hot gap; residual after no-op is `1.536 ms`, residual after
scoped spawn is `1.400 ms`, and the enforced next action is
`launch_amortization_required`.
`make prime-engine-high-offset-count-binary-cold-confirm` is the focused
one-shot confirmation for this weak lane: it runs 17 interleaved rounds of only
cold `circle-prime-count` default versus cold `primesieve`, writes
`prime_engine_high_offset_count_binary_cold_confirm_latest.{csv,json}`, and
checks provenance plus result agreement without promoting the row to a hard
speed gate. The current aggregate gate treats cold one-shot count as below
parity based on the current count-binary probe, not as durably promoted.
`make prime-engine-high-offset-count-binary-cold-candidate-check` reads the
short count-binary segment sweep, checks the focused confirmation artifact, and
fails only when a stable cold one-shot variant is at least `1.03x` faster than
the cold default while also beating cold `primesieve` by median and best time
without being held by focused confirmation. The sweep now keeps reduced-thread
high-offset candidates plus explicit `balanced` and `dynamic` rows visible; the
latest sweep/confirmation readout has no comparable stable candidate group that
both beats the cold default and beats cold `primesieve` by median and best
time. The focused confirmation briefly shows a `1.032x` default-relative gain,
but it still fails cold-`primesieve` parity; the combined sweep/confirmation
readout keeps the best actionable gain at `1.008x`, so no row is trial-ready.
`make prime-engine-high-offset-count-binary-candidate-confirm` is now the named
confirmation target for that lane: it reruns the default plus those current
reduced-thread candidates, writes
`prime_engine_high_offset_count_binary_candidate_confirm_latest.{csv,json}`, and
uses the same median-gain plus median/best-speed promotion rule. The latest
fallback action is no promotion; no comparable stable row group is trial-ready.
The one-shot worker-pool path is also closed as a cold-start lever: a local A/B
fell from `0.916x` median versus cold `primesieve` to `0.740x`, so the
server-style mpsc/thread teardown cost is not worth paying for one-shot CLI
work. A no-teardown variant that reused the one-shot worker pool, received all
worker results, and then let process exit reclaim idle workers still regressed
the cold row to `0.682x` median versus cold `primesieve`, so the
channel/scratch path itself remains too expensive for fresh CLI requests.
A static-base-prime reciprocal table prototype targeted per-chunk
modulo/division setup and produced one transient focused hot/cold win
(`3.931 ms` best for `circle-prime-count` versus `4.155 ms` for cold
`primesieve`), but it grew the slim binary and failed the isolated cold
confirmation twice; the stable rerun reported only `0.827x` median and
`0.749x` best speedup versus cold `primesieve`, so the prototype was removed.
A later current-binary cold sweep over wider `presieve13`, `presieve17`, and
`segmented` thread/segment combinations found no parity row: the best median
candidate in that probe was `presieve13:1310720` at 8 workers with `0.923x`
median and `0.870x` best versus cold `primesieve`. A spawn-all chunk scheduler
that moved the caller's chunk onto its own scoped worker regressed the cold
default to `0.576x` median versus cold `primesieve`, so the caller must keep
doing one chunk. A base-prime active-slice pre-touch prototype also failed to
produce a durable win: it reported `0.889x` median while worsening absolute
cold median to `5.995 ms` and weakening hot-server ratios.
A fixed-default probe that moved the edge high-offset segment from `1507328`
to the shifted-server `1310720` plan improved one short default median sample
to `0.903x` versus cold `primesieve`, and an A/B run saw the new default at
`1.040x` median but only `0.859x` best speedup. Because the stronger
calibration artifact still confirms `1507328`, and the new row fails best-time
parity, the fixed default stays at `1507328`. Replacing the small-stack
`thread::Builder::spawn_scoped` path with plain scoped spawns was also
rejected: it did not improve the slim cold count-binary best time and left the
row below best-time parity. Spawning the non-caller chunks in reverse
high-to-low order was also rejected: it produced a noisy median win but the
slim cold count-binary best-time speedup stayed at only `0.802x` versus cold
`primesieve`. Moving presieve13 segment-buffer capacity allocation onto the
caller before worker startup also regressed the slim cold median and the slim
server median, so worker-local allocation remains the current implementation.
Replacing checked `u64`-to-`usize` conversions for single-segment mark steps
with direct casts was also rejected: the focused run still had the slim cold
count-binary row below parity at `0.893x` best and `0.807x` median versus cold
`primesieve`.
A separate one-shot-only `circle-prime-count-cold` prototype removed stdin
server and shifted-batch code and cut the binary from `1395168` to `1310896`
bytes, but a 25-round interleaved A/B still left the existing
Builder/128 KiB-stack `circle-prime-count` row ahead at `0.989x` median versus
cold `primesieve`; the prototype remained below parity and was removed.
`make prime-engine-high-offset-hot-cold` now records the local bottleneck split
directly: a no-op fresh-process floor, adaptive-plan-only worker, serial
default worker, minimal fresh-process segmented/default rows, the full
`circle-prime` CLI row, the slim `circle-prime-count` CLI row, an optional
cold `primesieve` row, and persistent `count-server` candidate rows. The
latest full-status diagnostic has the slim cold count binary at `4.997 ms`
best, the persistent default count-server row at `1.741 ms`, the slim
binary no-op process floor at `1.720 ms`, and the scoped-spawn-only floor at
`1.856 ms` on the tracked high-offset span. The
strict interleaved count-binary probe still rejects promotion: the default slim
count-binary row is `0.862x` median and `0.902x` best versus cold
`primesieve`, with stable samples. Treat best-only hot/cold evidence as
bottleneck evidence, not an external cold one-shot promotion claim.
For build-profile probes, `scripts/benchmark_prime_external_controls.py` accepts
`--circle-prime-bin` and `--circle-prime-count-bin` to measure alternate
prebuilt binaries while keeping the normal `target/release` artifacts intact.
Recent fat-LTO and size-optimized `circle-prime-count` probes produced smaller
binaries but slower cold-count rows, so they are not promoted.

`make prime-engine-external-next-server` is the fast next-prime throughput gate.
It skips cold command invocations and compares persistent Circle `next-server`
requests directly against the persistent `libprimesieve` helper using
`primesieve_generate_n_primes(1, START, UINT64_PRIMES)` and the persistent
`libprimesieve` iterator helper using
`primesieve::iterator.jump_to(START).next_prime()`. The broad
`make prime-engine-external-next` target still records `libprimecount`
pi/nth-prime evidence, but the fast throughput gate stays focused on serious
next-prime controls. The default starts are `90`, `1000000`, `4294967000`, and
`1000000000000`, with `500` repeated searches sent as one `START COUNT`
request per timed sample, `3` unrecorded warmup rounds, and `9` recorded
rounds. Every side still recomputes every requested search; the larger batch
makes small-start results measure server throughput instead of
process-launch, first-request, or stdio noise. The target verifies the
benchmark metadata fingerprints for the current `circle-prime` binary and
`prime_engine_defaults.json` before comparing speedups. The default gate gives
every selected row a correctness/result match and requires every tracked start,
including `90`, to beat each persistent library control. The material non-tiny
rows `1000000`, `4294967000`, and `1000000000000` must also clear a stricter
`1.05x` median speedup floor with stable samples unless the row clears the
material noisy-win bypass, currently `1.5x`. Set
`CIRCLE_PRIME_EXTERNAL_NEXT_SERVER_REQUIRE_STABLE_SAMPLES=1` for a stricter
diagnostic that requires stable samples on every tracked row.

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
trial-ready. `make prime-engine-high-offset-promotion-check` fails only in that
trial-ready case, which keeps sub-3 ms timing noise and stale scout runs from
forcing churn while making real default opportunities hard to miss.

`make prime-engine-high-offset-hot-server-check` reads the latest hot-server
scorecard and fails unless the selected adaptive Circle server default rows
beat both the persistent `libprimesieve` count helper and the persistent
`libprimecount` pi-diff helper by median speed with stable samples, unless a
noisy row already clears the material-win bypass
`CIRCLE_PRIME_HIGH_OFFSET_HOT_SERVER_NOISY_MEDIAN_BYPASS` (default `1.05`).
By default it checks the full hot-server range set with a parity-plus `1.0`
median-speedup floor.
Default promotion remains gated by the separate confirmation/promotion readout
and post-promotion checks.

The shifted hot-server check uses the same stable-sample preference, but its
fresh-interval win is naturally smaller; noisy shifted rows pass only after
clearing `CIRCLE_PRIME_HIGH_OFFSET_SHIFTED_CHECK_NOISY_MEDIAN_BYPASS`
(default `1.15`).

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

`controls/primesieve_next_server.c`,
`controls/primesieve_iterator_next_server.cpp`, and
`controls/primecount_next_server.c` are small benchmark helpers for the
next-prime scorecard. The Python harness compiles them into `target/` and uses
them as persistent line servers around the `libprimesieve` generate API, the
`libprimesieve` iterator API, and the `libprimecount` pi+nth-prime API.

`controls/primesieve_count_server.c` and `controls/primecount_pi_server.c` are
the matching count-control helpers. They keep `libprimesieve`/`libprimecount`
processes alive and call `primesieve_count_primes(LOW, HIGH-1)` or
`primecount_pi(HIGH-1)-primecount_pi(LOW-1)` for half-open Circle benchmark
ranges.

`controls/primecount_pi_server.c` is the persistent `libprimecount` pi-diff
helper. It keeps `primecount`'s Gourdon-backed `primecount_pi` path hot and
returns `primecount_pi(HIGH-1) - primecount_pi(LOW-1)` for the same half-open
ranges.

Benchmark and tuning files are local performance evidence, not proof artifacts.
Lean proof status is tracked through `Circle/Core/Horizon.lean` and
`manifests/theorem_manifest.yaml`.
