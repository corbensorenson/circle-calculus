# Circle Calculus Application 1: Coil Data Analysis

Status: polished draft with a proved finite phase-coordinate seed.

## Aim

This paper starts the data-analysis application track: coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks. The target domain is not arbitrary data. Circle Calculus is relevant here when the data has real cyclic, periodic, recurrent, phase-like, or fibered structure.

The current formal seed is intentionally small: `COMMON-0016`, the finite phase coordinate

```text
phase(period, step) = step mod period
```

for positive periods. This is a synthetic-data primitive, not a detector for unknown real-world periods.

## Theorem Spine

- `APPD-T0001`: `Circle.Applications.phaseCoordinate_lt_period`
- `APPD-T0002`: `Circle.Applications.phaseCoordinate_add_period`
- `APPD-T0003`: `Circle.Applications.phaseCoordinate_zero`

## Proved Core

`APPD-T0001` proves that the phase coordinate is bounded by the positive period. This gives a checked finite phase channel for downstream examples.

`APPD-T0002` proves the closure law:

```text
phase(period, step + period) = phase(period, step)
```

`APPD-T0003` proves the zero anchor:

```text
phase(period, 0) = 0
```

The Python sidecar checks the same synthetic examples for boundedness, closure, and the zero case. These checks are executable support; the Lean declarations are the formal proof layer.

## Benchmark Program

The first practical benchmark should start with synthetic signals where the ground-truth period is known. A minimal pipeline is:

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

- Add synthetic periodic-data generators and known-period fixtures.
- Compare coil signatures against ordinary autocorrelation and Fourier baselines.
- Track aliasing and false positives explicitly.
- Keep Python/MLX experiments separate from Lean proof status.

## Guardrail

No real-data application claim is accepted without a benchmark, a baseline, and a clearly labeled result. The current proved content is the finite phase-coordinate seed only.
