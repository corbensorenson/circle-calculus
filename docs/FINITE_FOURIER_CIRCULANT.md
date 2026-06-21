# Finite Fourier And Circulant Algebra

Claim boundary: the Lean modules prove finite algebra facts about cyclic
characters, roots-of-unity behavior, cyclic shifts, and circulant convolution.
The Python helpers execute the same finite-circle calculations over complex
floating point numbers; residual checks are diagnostics, not proofs.

## Stable Imports

Lean:

```lean
import Circle.Core
import Circle.Applications.Public
```

Specific modules:

- `Circle.Core.FiniteFourier`
- `Circle.Applications.Circulant`
- `Circle.Applications.CirculantSpectral`

Python:

```python
from circle_math.core import (
    circular_convolution,
    finite_fourier_coefficients,
    inverse_finite_fourier,
    spectral_aliasing_report,
    spectral_convolution_report,
)
```

## Lean Proof Spine

The finite Fourier layer defines `Circle.CyclicCharacter n R`, an algebraic
character from the additive finite circle `ZMod n` into a commutative monoid.
It proves:

- `Circle.CyclicCharacter.value_pow_card`: every character value is an `n`th
  root of unity;
- `Circle.finiteShift_zero` and `Circle.finiteShift_add`: cyclic shifts form the
  expected finite-circle action;
- `Circle.finiteFourierCoeff_add` and `Circle.finiteFourierCoeff_zero`:
  Fourier coefficients are additive in the signal;
- `Circle.finiteFourierCoeff_shift`: shifting a signal multiplies a Fourier
  coefficient by the matching character phase;
- `Circle.Applications.finiteFourierCoeff_circConv`: the Fourier coefficient of
  a circular convolution is the product of the matching kernel and signal
  coefficients.

The existing circulant mixer module also proves:

- `Circle.Applications.circConv_shift_equivariant`;
- `Circle.Applications.circConv_comm`;
- `Circle.Applications.circConv_add`.

## Python Example

```python
from circle_math.core import (
    circular_convolution,
    finite_fourier_coefficients,
    inverse_finite_fourier,
    spectral_aliasing_report,
    spectral_convolution_report,
)

signal = [1, 2, 0, -1]
kernel = [2, 0, 1, 0]

coefficients = finite_fourier_coefficients(signal)
reconstructed = inverse_finite_fourier(coefficients)
convolution = circular_convolution(kernel, signal)
report = spectral_convolution_report(kernel, signal)
aliases = spectral_aliasing_report(4, [-1, 0, 3, 4, 7])

print(convolution)
print(report.passed)
print(round(report.max_abs_error, 12))
print(aliases)
```

Expected shape:

```text
[(2+0j), (3+0j), (1+0j), 0j]
True
0.0
{0: [0, 4], 3: [-1, 3, 7]}
```

## Why This Matters For AI

Circulant layers, circular convolution, Fourier features, RoPE-style phases,
and cyclic attention patterns all depend on the same finite-circle algebra:
shift, phase, convolution, and aliasing. This page is the reusable contract
surface for those facts.

This does not claim a model will be accurate, efficient, stable, or better than
another model. It only records the finite algebra identities that a model or
contract can rely on.
