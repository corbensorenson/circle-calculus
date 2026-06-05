# Circle Calculus S7.2: Quaternionic Hopf Fibration

Status: draft with the bounded quaternionic Hopf coordinate landing and right-phase invariance facts Lean-proved.

## Aim

This paper tracks the quaternionic Hopf roadmap now that the `S^3` quaternion calculus and the finite `S^4` base are stable.

## Target Spine

- `S7QH-T0001`: `Circle.S7.quaternionicHopf_lands_sphere`
- `S7QH-T0002`: `Circle.S7.quaternionicPhaseInvariance`

## Intended Structure

```text
S^3 -> S^7 -> S^4
```

## Model

The executable sidecar represents a point of `S^7` as a normalized pair of quaternions. The Lean sidecar uses equivalent real-coordinate quaternion pairs:

```text
(q0, q1) in H^2
|q0|^2 + |q1|^2 = 1
```

The exploratory quaternionic Hopf map is:

```text
H(q0,q1) =
  (2 q0 conjugate(q1), |q0|^2 - |q1|^2)
```

The first component is a quaternion, so the output is represented by five real coordinates: four from `2 q0 conjugate(q1)` and one scalar coordinate.

The quaternionic phase action used by the executable model is right multiplication by a shared unit quaternion:

```text
(q0,q1) -> (q0 u, q1 u)
```

When `|u|=1`, the Hopf coordinates are invariant in the Python model.

## Proved Core

The Lean sidecar `sidecars/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION/lean/PaperS702.lean` checks the coordinate model:

- `S7QH-T0001` is proved by `Circle.S7.quaternionicHopf_lands_sphere`: if a quaternion pair has total norm square `1`, the five Hopf base coordinates have norm square `1`.
- `S7QH-T0002` is proved by `Circle.S7.quaternionicPhaseInvariance`: right multiplication of both quaternion coordinates by the same unit quaternion coordinate preserves the Hopf base coordinates.

The helper theorem `Circle.S7.quaternionicHopfBaseNormSq_hopfMap` proves the exact identity

```text
||H(p)||^2 = ||p||^4
```

for the real-coordinate quaternionic Hopf model.

The helper theorem `Circle.S7.quaternionicHopfMap_rightPhase_scaled` proves the stronger scaling identity: right multiplication by `u` scales the Hopf base by `|u|^2`, so unit `u` preserves the base point.

## Executable Core

The Python sidecar `sidecars/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION/python/test_paper_s7_02_examples.py` checks:

- `S7QH-T0001`: normalized quaternion pairs map to five-coordinate points with squared norm numerically `1`, matching the Lean coordinate theorem.
- `S7QH-T0002`: shared right unit-quaternion phase rotation preserves the quaternionic Hopf map, matching the Lean coordinate theorem.

These checks remain useful examples, but the two bounded coordinate statements now have Lean proofs.

## Dictionary Targets

- `S7QH-0001`: quaternionic Hopf roadmap
- `S3Q-0001`: quaternion model
- `S4-0001`: S4 quaternionic Hopf base

## Notes

This paper records the coordinate model and bounded invariances. It does not yet formalize quaternionic projective space, a full fibration theorem, or the quotient topology.
