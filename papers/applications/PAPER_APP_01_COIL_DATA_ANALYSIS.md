# Circle Calculus Application 1: Coil Data Analysis

Status: draft with a proved finite phase-coordinate seed.

## Aim

Explore coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks.

The current formal seed is `COMMON-0016`, the finite phase coordinate

```text
phase(period, step) = step mod period
```

for positive periods. This is a synthetic-data primitive, not a detector for unknown real-world periods.

## Theorem Spine

- `APPD-T0001`: for positive period, the phase coordinate is bounded by the period. Lean declaration: `Circle.Applications.phaseCoordinate_lt_period`.
- `APPD-T0002`: for positive period, adding one full period preserves phase. Lean declaration: `Circle.Applications.phaseCoordinate_add_period`.

The Python sidecar checks the same synthetic examples for boundedness and closure. These checks support examples and future benchmarks; the Lean declarations are the formal proof layer.

## Next Program

- Start with synthetic periodic data before real datasets.
- Compare against ordinary periodic and Fourier baselines.
- Keep Python/MLX experiments separate from Lean proof status.

## Guardrail

No application claim is accepted without a benchmark or a clearly labeled exploratory result.
