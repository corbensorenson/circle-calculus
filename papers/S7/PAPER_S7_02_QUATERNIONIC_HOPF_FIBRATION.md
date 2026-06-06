# Circle Calculus S7.2: Quaternionic Hopf Fibration

Status: polished draft with bounded quaternionic Hopf coordinate landing and right-phase invariance facts Lean-proved.

## Aim

This paper records the quaternionic Hopf roadmap now that the `S^3` quaternion calculus and the finite `S^4` base are stable. The intended structure is:

```text
S^3 -> S^7 -> S^4
```

The current result is not the full fibration. It is the bounded coordinate spine needed before quaternionic projective space, quotient topology, and a complete fibration theorem can be stated honestly.

## Theorem Spine

- `S7QH-T0001`: `Circle.S7.quaternionicHopf_lands_sphere`
- `S7QH-T0002`: `Circle.S7.quaternionicPhaseInvariance`
- `S7QH-T0003`: `Circle.S7.quaternionicRightPhaseAction_laws`

## Model

The executable sidecar represents a point of `S^7` as a normalized pair of quaternions. The Lean sidecar uses equivalent real-coordinate quaternion pairs:

```text
(q0, q1) in H^2
|q0|^2 + |q1|^2 = 1
```

The coordinate Hopf map is:

```text
H(q0,q1) =
  (2 q0 conjugate(q1), |q0|^2 - |q1|^2)
```

The first component is a quaternion, so the output is represented by five real coordinates. The phase action is shared right multiplication by a unit quaternion:

```text
(q0,q1) -> (q0 u, q1 u)
```

## Proved Core

`S7QH-T0001` proves that if a quaternion pair has total norm square `1`, then the five Hopf base coordinates have norm square `1`. The helper theorem `Circle.S7.quaternionicHopfBaseNormSq_hopfMap` proves:

```text
||H(p)||^2 = ||p||^4
```

for the real-coordinate quaternionic Hopf model.

`S7QH-T0002` proves right-phase invariance: multiplying both quaternion coordinates on the right by the same unit quaternion coordinate preserves the Hopf base coordinates. The helper theorem `Circle.S7.quaternionicHopfMap_rightPhase_scaled` proves the stronger scaling identity: right multiplication by `u` scales the Hopf base by `|u|^2`, so unit `u` preserves the base point.

`S7QH-T0003` packages the right-phase action law:

```text
rightPhase(rightPhase(p,u),v) = rightPhase(p,u*v)
```

and combines it with the checked base-invariance laws for unit phases. This uses associativity of quaternion multiplication. It is an action law for the bounded coordinate model, not a proof of quotient topology or the full fibration.

The Python sidecar checks normalized landing, shared right-unit phase invariance, and right-phase composition on executable quaternion examples.

## Role In The Ladder

This paper links `S^3` quaternion algebra, finite `S^4` topology, and the `S^7` roadmap. It also sets the stage for robotics/orientation applications and for comparing the associative quaternionic story with the later nonassociative octonion layer.

## Dictionary Targets

- `S7QH-0001`: quaternionic Hopf roadmap
- `S3Q-0001`: quaternion model
- `S4-0001`: S4 quaternionic Hopf base

## Guardrails

This paper proves bounded coordinate landing, right-phase invariance, and the coordinate right-phase action law. It does not yet formalize quaternionic projective space, quotient topology, smooth bundle structure, or the full quaternionic Hopf fibration.
