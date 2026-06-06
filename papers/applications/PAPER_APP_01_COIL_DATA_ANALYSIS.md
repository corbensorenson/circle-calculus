# Circle Calculus Application 1: Coil Data Analysis

Status: polished draft with a proved finite phase-coordinate seed and exploratory deterministic benchmark fixtures.

## Aim

This paper starts the data-analysis application track: coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks. The target domain is not arbitrary data. Circle Calculus is relevant here when the data has real cyclic, periodic, recurrent, phase-like, or fibered structure.

The current formal seed is intentionally small: `COMMON-0016`, the finite phase coordinate

```text
phase(period, step) = step mod period
```

for positive periods. This is a synthetic-data primitive, not a detector for unknown real-world periods.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_APP_01_COIL_DATA_ANALYSIS/lean/PaperApp01.lean
```

The Python examples are:

```text
sidecars/PAPER_APP_01_COIL_DATA_ANALYSIS/python/test_phase_coordinate_examples.py
```

The theorem and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar and synthetic benchmark fixtures are executable support; Lean declarations determine proof status.

## Theorem Spine

- `APPD-T0001`: `Circle.Applications.phaseCoordinate_lt_period`
- `APPD-T0002`: `Circle.Applications.phaseCoordinate_add_period`
- `APPD-T0003`: `Circle.Applications.phaseCoordinate_zero`
- `APPD-T0004`: `Circle.Applications.phaseCoordinate_add_mul_period`
- `APPD-T0005`: `Circle.Applications.phaseCoordinate_idempotent`

## Proved Core

`APPD-T0001` proves that the phase coordinate is bounded by the positive period. This gives a checked finite phase channel for downstream examples.

`APPD-T0002` proves the closure law:

```text
phase(period, step + period) = phase(period, step)
```

`APPD-T0004` proves the multi-pass closure law:

```text
phase(period, step + passes * period) = phase(period, step)
```

`APPD-T0005` proves that normalizing an already normalized phase coordinate is a no-op:

```text
phase(period, phase(period, step)) = phase(period, step)
```

`APPD-T0003` proves the zero anchor:

```text
phase(period, 0) = 0
```

The Python sidecar checks the same synthetic examples for boundedness, closure, and the zero case. These checks are executable support; the Lean declarations are the formal proof layer.

## Benchmark Program

The first practical benchmark starts with synthetic signals where the ground-truth period is known. The current Python reference module `circle_math.applications.coil_data` adds:

- deterministic known-period signal generation;
- `coil_closure_error`, a mean-squared closure score for candidate periods;
- `autocorrelation_score`, an ordinary normalized autocorrelation baseline;
- `periodogram_score`, a simple single-frequency periodogram-style baseline;
- `benchmark_known_period`, a fixture reporting both best-period choices.
- `benchmark_period_fixture_suite`, a clean/noisy/aliased/multi-period fixture suite reporting all three methods.

The current fixture checks that both coil closure and autocorrelation recover the known period for a simple deterministic synthetic signal. That is a sanity check, not a usefulness claim.

`APPD-B0002` extends the fixture suite. Clean and deterministic-noisy cases recover the known period `12` across all three methods. The aliased case records both `6` and `12` as visible components. The multi-period case is intentionally ambiguous: coil closure and autocorrelation currently prefer `24`, while the periodogram-style score prefers `12`. This is a useful warning, not a win.

A minimal future pipeline is:

```text
signal
  -> candidate periods
  -> finite phase coordinates
  -> closure profile
  -> prime-lag or coprime-lag scans
  -> comparison against ordinary period/Fourier baselines
```

Only after synthetic behavior is understood should the project move to real datasets such as sleep cycles, heart rhythms, music/rhythm, machinery vibration, seasonal weather, or calendar/time patterns.

## Next Program

- Compare the deterministic suite against external periodogram/Fourier baselines.
- Add real-data guardrails before moving beyond synthetic fixtures.
- Track aliasing and false positives explicitly.
- Keep Python/MLX experiments separate from Lean proof status.

## Guardrail

No real-data application claim is accepted without a benchmark, a baseline, and a clearly labeled result. The current proved content is the finite phase-coordinate seed only.
