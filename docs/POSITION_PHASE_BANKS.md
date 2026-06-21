# Position Phase Banks

Claim boundary: this page covers the exact finite integer-period phase-bank
contract. It does not prove real-valued trigonometric margins, model quality,
length extrapolation, speed, memory use, training stability, or deployment
behavior.

## Why This Belongs Here

Many positional encoding schemes are circle stories in disguise:

- sinusoidal Transformer positional encodings use sine/cosine frequency banks
  ([Attention Is All You Need](https://arxiv.org/abs/1706.03762));
- RoPE rotates query/key coordinates by position-dependent phases
  ([RoFormer](https://arxiv.org/abs/2104.09864));
- xPos, YaRN, and LongRoPE change scaling or interpolation rules around
  RoPE-style phase ladders
  ([xPos](https://arxiv.org/abs/2212.10554),
  [YaRN](https://arxiv.org/abs/2309.00071),
  [LongRoPE](https://arxiv.org/abs/2402.13753));
- 2D RoPE variants split or mix spatial axes into rotary phase banks
  ([RoPE for Vision Transformer](https://arxiv.org/abs/2403.13298)).

The common finite contract is smaller than any one paper:

```text
phase(period, position) = position mod period
```

Two ordered positions collide in one channel exactly when the period divides
the position gap. A finite phase bank collides exactly when every declared
period divides the gap.

## Lean Surface

The reusable proof source is:

```lean
import Circle.Applications.PositionPhase
```

Stable public import:

```lean
import Circle.Applications.Public
```

Primary declarations:

- `Circle.Applications.phaseChannelCollision_iff_gap_dvd`
- `Circle.Applications.phaseChannelDistinguishable_iff_not_gap_dvd`
- `Circle.Applications.phaseChannelCollision_iff_eq_on_context`
- `Circle.Applications.phaseBankCollision_iff_forall_gap_dvd`
- `Circle.Applications.phaseBankDistinguishable_iff_exists_not_gap_dvd`
- `Circle.Applications.phaseBankDistinguishable_of_period_ge_context`
- `Circle.Applications.phaseBankCollision_of_subset`
- `Circle.Applications.phaseBankDistinguishable_of_subset`
- `Circle.Applications.phaseGrid2DCollision_iff_axes`
- `Circle.Applications.scaledPhasePeriod_pos`
- `Circle.Applications.scaledPhasePeriodBank_all_pos`

The theorem ids are `CC-T0122` through `CC-T0132`.

## Python: Generic Phase Bank

```python
from circle_math.ai_contracts import (
    phase_bank_collision_report,
    phase_bank_from_periods,
)

bank = phase_bank_from_periods("diagnostic", [6, 9, 13])
report = phase_bank_collision_report(bank, 0, 36)

print(report.all_channels_collide)
print(report.witness_channels)
print([row.period_divides_gap for row in report.channel_results])
```

Expected output:

```text
False
('phase_2',)
[True, True, False]
```

The witness says the 13-period channel separates positions `0` and `36`, so
the bank does not have an all-channel collision for that pair.

## Python: RoPE-Family Descriptors

```python
from circle_math.ai_contracts import (
    longrope_nonuniform_scaled_phase_bank,
    phase_bank_collision_report,
    rope_integer_phase_bank,
    yarn_uniform_scaled_phase_bank,
)

base = rope_integer_phase_bank(head_dim=8, channel_count=3)
yarn = yarn_uniform_scaled_phase_bank(base, scale=4)
longrope = longrope_nonuniform_scaled_phase_bank(base, scale_factors=[1, 2, 3])

print(base.periods)
print(yarn.periods)
print(longrope.periods)
print(phase_bank_collision_report(base, 0, base.periods[0]).distinguishes)
```

These helpers produce integer-period artifacts for a declared phase-bank layer.
The exact theorem-backed statements concern residues and divisibility only.
YaRN/LongRoPE training recipes, search procedures, and real-valued phase
margins remain outside this proof.

## Python: 2D Phase Grid

```python
from circle_math.ai_contracts import (
    phase_bank_from_periods,
    phase_grid_2d_collision_report,
)

x_bank = phase_bank_from_periods("x", [4, 6], axis="x")
y_bank = phase_bank_from_periods("y", [5], axis="y")

report = phase_grid_2d_collision_report(x_bank, y_bank, (0, 1), (12, 6))
print(report.x_report.all_channels_collide)
print(report.y_report.all_channels_collide)
print(report.grid_collides)
```

The Lean predicate for 2D grids is the product of the two axis-bank predicates.
This models the exact finite layer of axial 2D RoPE. Mixed-direction or
spiral-style grids are good next targets, but they are not proved by the axial
theorem above.

## What To Reuse

Use this page when adding a new positional encoding to Circle Calculus:

1. Export a finite declared period bank.
2. State whether the periods are exact declarations or discretized real-period
   estimates.
3. Cite the finite phase-bank theorem ids for residue collision claims.
4. Keep real-valued margins, empirical quality, and extrapolation results as
   separate executable or benchmark evidence until they have their own Lean
   model.
