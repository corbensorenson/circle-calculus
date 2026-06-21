# Circular Statistics Contracts

Claim boundary: this page proves exact finite residue, same-phase, wrapped
distance, and histogram facts. It does not prove floating-point numerical
stability, circular-statistical estimator optimality, sensor uncertainty,
pose quality, model quality, or downstream decision quality.

## Motivation

Circular statistics is the standard way to analyze data whose values live on a
circle: angles, phases, headings, hue, pose orientation, oscillator phase, and
periodic feature channels. The public Python helpers follow the usual
resultant-vector picture used by tools such as
[SciPy `circmean`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.circmean.html),
[SciPy `circvar`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.circvar.html),
and
[SciPy `directional_stats`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.directional_stats.html).

The formal layer is deliberately smaller:

```text
same_phase(period, left, right) = left mod period = right mod period
wrapped_distance = min(forward_distance, backward_distance)
histogram(period, samples, residue) = count(sample mod period = residue)
```

That finite layer is reusable for angle bins, phase buckets, coil samples,
pose-sector counts, circular uncertainty reports, and AI feature diagnostics.

## Lean Surface

The reusable proof source is:

```lean
import Circle.Applications.CircularStatistics
```

Stable public import:

```lean
import Circle.Applications.Public
```

Primary declarations:

- `Circle.Applications.circularSamePhase_iff_gap_dvd`
- `Circle.Applications.circularSamePhase_refl`
- `Circle.Applications.circularSamePhase_symm`
- `Circle.Applications.circularSamePhase_trans`
- `Circle.Applications.wrappedCircularDistance_comm`
- `Circle.Applications.wrappedCircularDistance_le_forward`
- `Circle.Applications.wrappedCircularDistance_le_backward`
- `Circle.Applications.mem_circularSampleResidues_lt_period`
- `Circle.Applications.circularHistogram_le_length`
- `Circle.Applications.circularHistogram_zero_of_period_le_residue`

The theorem ids are `CC-T0139` through `CC-T0148`.

## Python: Finite Residue Histogram

```python
from circle_math.core import (
    finite_residue_histogram,
    finite_residue_samples,
    finite_same_phase,
    finite_wrapped_distance,
)

print(finite_same_phase(12, 1, 25))
print(finite_wrapped_distance(12, 1, 11))
print(finite_residue_samples(5, [0, 5, 7, 12]))
print(finite_residue_histogram(5, [0, 5, 7, 12], include_zero_counts=True))
```

Expected output:

```text
True
2
(0, 0, 2, 2)
{0: 2, 1: 0, 2: 2, 3: 0, 4: 0}
```

These helpers are theorem-facing: they are natural-number residue facts that
match the Lean declarations above.

## Python: Circular Mean And Resultant Length

```python
from math import tau

from circle_math.core import circular_mean_report

report = circular_mean_report([0.0, tau / 4.0])
print(report.mean_angle)
print(report.mean_resultant_length)
print(report.circular_variance)
print(report.undefined_mean)
```

The result reports:

- normalized angle samples;
- resultant vector `(sum cos, sum sin)`;
- resultant length and mean resultant length;
- circular variance using the common `1 - R` convention;
- `mean_angle=None` when the resultant vector is effectively zero.

This is executable numerical evidence, not a Lean proof about real arithmetic
or statistical inference.

## Python: Wrapped Error And Von-Mises-Style Weights

```python
from math import pi

from circle_math.core import (
    angular_difference,
    von_mises_weight,
    wrapped_angular_error,
)

print(angular_difference(0.0, 3.0 * pi / 2.0))
print(wrapped_angular_error(0.0, 3.0 * pi / 2.0))
print(von_mises_weight(0.0, mean=0.0, kappa=2.0))
```

`von_mises_weight` is intentionally unnormalized. It returns
`exp(kappa * cos(diff))` and avoids claiming a probability density until a
separate normalization and numerical-analysis contract exists.

## What To Reuse

Use this module when a circle-valued quantity needs a compact, public contract:

1. Normalize real-valued angles for executable diagnostics.
2. Export finite bins or declared residues when the claim needs Lean proof.
3. Cite `CC-T0139` through `CC-T0148` for same-phase, wrapped-distance, and
   histogram facts.
4. Keep estimator quality, pose uncertainty, sensor quality, and model-quality
   claims separate until they have explicit theorem or benchmark evidence.
