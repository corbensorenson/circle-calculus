# Cyclic Equivariance Contracts

Claim boundary: this page proves finite cyclic shift equivariance/invariance and
minimal finite reflection laws. It does not prove continuous rotation
equivariance, steerable-kernel completeness, robustness, data efficiency, model
quality, or deployment behavior.

## Motivation

Equivariance is the statement that transforming the input transforms the output
in the same way. In AI, this is the group-theoretic idea behind group
convolutions and many rotation/reflection-aware architectures; see
[Group Equivariant Convolutional Networks](https://arxiv.org/abs/1602.07576),
Distill's
[Naturally Occurring Equivariance in Neural Networks](https://distill.pub/2020/circuits/equivariance/),
and
[General E(2)-Equivariant Steerable CNNs](https://arxiv.org/abs/1911.08251).

Circle Calculus starts with the finite case:

```text
cyclic_shift(s, x)[i] = x[i - s]
cyclic equivariance: f(shift(s, x)) = shift(s, f(x))
cyclic invariance: readout(shift(s, x)) = readout(x)
reflection(x)[i] = x[-i]
```

That finite layer already covers circulant mixers, cyclic pooling, token-ring
features, orientation bins, and small dihedral fixtures.

## Lean Surface

The reusable proof source is:

```lean
import Circle.Applications.CyclicEquivariance
```

Stable public import:

```lean
import Circle.Applications.Public
```

Primary declarations:

- `Circle.Applications.cyclicShift_zero`
- `Circle.Applications.cyclicShift_add`
- `Circle.Applications.cyclicEquivariant_identity`
- `Circle.Applications.cyclicEquivariant_comp`
- `Circle.Applications.cyclicEquivariant_add`
- `Circle.Applications.circulantLayer_cyclicEquivariant`
- `Circle.Applications.cyclicSum_shift_invariant`
- `Circle.Applications.reflectSignal_involutive`
- `Circle.Applications.reflectSignal_shift`
- `Circle.Applications.dihedralEquivariant_identity`
- `Circle.Applications.dihedralEquivariant_implies_cyclic`
- `Circle.Applications.dihedralTransform_reflection_zero_involutive`

The theorem ids are `CC-T0149` through `CC-T0160`.

## Python: Transforms

```python
from circle_math.core import cyclic_shift, dihedral_transform, reflect_signal

print(cyclic_shift([1, 2, 3, 4], 1))
print(reflect_signal([10, 20, 30, 40]))
print(dihedral_transform([10, 20, 30, 40], shift=1, reflected=True))
```

Expected output:

```text
((4+0j), (1+0j), (2+0j), (3+0j))
((10+0j), (40+0j), (30+0j), (20+0j))
((20+0j), (10+0j), (40+0j), (30+0j))
```

## Python: Circulant Equivariance

```python
from circle_math.core import circulant_equivariance_report

report = circulant_equivariance_report(
    [2, 0, 1, 0],
    [[1, 2, 0, -1], [0, 3, 1, 2]],
)

print(report.passed)
print(report.max_abs_delta)
print(report.theorem_ids)
```

The Lean-backed fact is that a finite circulant convolution layer commutes with
every cyclic shift. This is a structural equivariance claim, not an accuracy or
efficiency claim.

## Python: Invariant Sum Pooling

```python
from circle_math.core import cyclic_sum_invariance_report

report = cyclic_sum_invariance_report([[1, 2, 3, 4], [2, -1, 0, 5]])
print(report.passed)
print(report.transform_family)
```

This cites the finite theorem that sum-pooling over all cyclic addresses is
shift-invariant.

## What To Reuse

Use this module when adding a model or feature map with a finite circular
symmetry:

1. State the exact finite transform convention.
2. Decide whether the output should be equivariant or invariant.
3. Use the Python report to generate executable evidence for fixtures.
4. Cite `CC-T0149` through `CC-T0160` only for the finite transform laws.
5. Keep continuous geometry, image robustness, and model-quality claims outside
   the proof boundary unless separate evidence exists.
