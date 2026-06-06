# Circle Calculus S15.1: Octonionic Hopf Roadmap

Status: polished draft with a Lean roadmap marker, finite topological `S^15`, bounded octonionic Hopf landing theorems, and a formal warning boundary for naive octonionic phase invariance Lean-proved.

## Aim

This future-facing paper records the last exceptional Hopf horizon that Circle Calculus should name before pivoting away from dimension climbing. The intended classical pattern is:

```text
S^7 -> S^15 -> S^8
```

That phrase is useful roadmap language, but it is not a proof. The paper therefore separates three levels:

- a durable Lean roadmap marker for the intended horizon;
- a finite topological `S^15` suspension anchor;
- a bounded coordinate landing theorem for the octonionic Hopf expression.

The full octonionic Hopf fibration, quotient topology, and global `S^7` phase action remain future work.

## Source Trail

The Lean sidecar is:

```text
sidecars/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP/lean/PaperS1501.lean
```

The Python examples are:

```text
sidecars/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP/python/test_s15_roadmap_examples.py
```

The theorem, warning, and dictionary links are registered in `manifests/paper_manifest.yaml`. The Python sidecar checks bounded examples and the roadmap marker; Lean declarations determine proof status, and the warning boundary prevents upgrading the marker into a full fibration proof.

## Theorem Spine

- `S15-T0001`: `Circle.Future.S15.octonionicHopfRoadmap`
- `S15-T0002`: `Circle.Future.S15.topologicalModel_eulerCharacteristic`
- `S15-T0003`: `Circle.Future.S15.octonionicHopf_lands_sphere`
- `S15-T0004`: `Circle.Future.S15.topologicalModel_eq_eightSuspensions_s7`
- `S15-T0005`: `Circle.Future.S15.octonionPairRightPhase_normSq`
- `S15-T0006`: `Circle.Future.S15.octonionicHopfMap_rightPhase_scalar_invariant`
- `S15-T0007`: `Circle.Future.S15.octonionicHopfMap_rightPhase_lands_sphere`
- `S15-T0008`: `Circle.Future.S15.octonionicHopfMap_rightPhase_not_invariant_example`
- `S15-T0009`: `Circle.Future.S15.eightSuspensions_eulerCharacteristic`
- `S15-W0001`: naive right unit-octonion phase is not full coordinate invariance

## Roadmap Marker

`S15-T0001` is intentionally registered as a Lean-stated roadmap marker:

```text
Circle.Future.S15.octonionicHopfRoadmap = "S7 -> S15 -> S8"
```

It exists so the dictionary, paper manifest, and future proof work have one stable reference for the post-`S^7` horizon. Its manifest blocker explicitly says that it is not a proof of the full fibration.

## Proved Topological Anchor

`S15-T0004` proves that the finite `S^15` model is exactly the eightfold suspension of the finite `S^7` model:

```text
topologicalModel n = eightSuspensions (Circle.S7.iteratedSuspensionModel n)
```

`S15-T0009` proves the general finite eight-suspension parity fact:

```text
chi(eightSuspensions(cells)) = chi(cells)
```

`S15-T0002` then proves:

```text
chi(topologicalModel n) = 0
```

for every natural `n`. This gives the future `S^15` paper the same kind of finite suspension anchor used throughout the dimensional ladder, without pretending that suspension counts alone formalize the Hopf fibration.

## Proved Coordinate Landing

`S15-T0003` proves a bounded coordinate landing fact: a normalized pair of coordinate octonions maps to a nine-coordinate base object with norm square `1`. The helper theorem `Circle.Future.S15.hopfBase9NormSq_octonionicHopfMap` proves the exact identity:

```text
||H(p)||^2 = ||p||^4
```

for the bounded octonionic Hopf expression. This is the right algebraic seed for the future fibration paper because it checks the base-sphere landing equation before any quotient or fiber story is claimed.

The Python sidecar mirrors the roadmap marker, the eightfold-suspension model, eight-suspension Euler preservation, Euler characteristic `0`, the coordinate identity, and normalized-pair landing examples.

## Right-Phase Boundary

After the `S^7` octonion layer proved two-sided conjugate inverse equations, this paper tests the tempting next claim:

```text
H(x * u, y * u) = H(x, y)
```

for every unit octonion `u`. In the current bounded coordinate model, that exact full-coordinate statement is false. The correct safe facts are narrower:

- `S15-T0005` proves shared right multiplication scales the octonion-pair squared norm by `normSq(u)`.
- `S15-T0006` proves that a unit right phase preserves the scalar coordinate of the bounded Hopf map.
- `S15-T0007` proves that if the original pair is normalized and `u` is unit, the phased pair still lands on the unit base equation.

The full coordinate is not invariant under naive shared right multiplication. `S15-T0008` proves a basis counterexample:

```text
H(e1 * e4, e2 * e4) != H(e1, e2)
```

This is not a failure of the classical Hopf horizon. It is a proof-status boundary for this repository: the future octonionic fibration work needs a more careful bracketed quotient/fiber model before any phase-invariance claim can be promoted.

## Role After S7

This paper is deliberately placed after `S^7` topological and octonion coordinate work. It also marks a strategic stopping point: after `S^15`, the project should pivot to stable spheres, maps, bundles, spectra, Bott/Clifford periodicity, boundaries, proof-carrying glyphs, and applications instead of implying a false continuation of exceptional Hopf/division-algebra dimensions.

## Dictionary Targets

- `S15-0001`: future octonionic Hopf horizon
- `S15-0002`: finite S15 suspension model
- `S15-0003`: bounded octonionic Hopf landing
- `S15-W0001`: naive octonionic phase invariance warning
- `S7O-0001`: octonion model

## Guardrails

The proved statements do not establish the full octonionic Hopf fibration, quotient topology, a globally well-behaved `S^7` phase action, or any new infinite family of Hopf fibrations. They prove the finite topological suspension anchor, bounded coordinate landing equations, safe right-phase landing facts, and a counterexample to naive full-coordinate right-phase invariance. Everything stronger stays roadmap/future until explicitly modeled and checked.
