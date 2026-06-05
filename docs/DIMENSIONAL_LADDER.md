# Dimensional Ladder

This note summarizes the expanded post-`S^1` roadmap. The active completion checklist lives in `docs/COMPLETION_ROADMAP.md`, the deferred Phase II/application context lives in `docs/PHASE2_AND_APPLICATIONS.md`, and the detailed planning pack lives in `circle_calculus_dimensional_handoff/`.

The current proved core now spans the finite `S^0` through `S^7` ladder, with future `S^15` topological and bounded-coordinate landing seeds. Higher-dimensional work should keep extending lower layers without contaminating them.

## Core Rule

Higher dimensions may import lower dimensions. Lower dimensions must not import higher dimensions.

In dependency order:

```text
Common -> S0 -> S1 -> S2 -> S3 -> S4 -> S5 -> S6 -> S7 -> Future/S15
```

This rule is structural. It does not claim that all mathematical meaning is linear.

## Two Ladders

The geometric ladder keeps every sphere dimension visible:

```text
S^0 = two-point opposition
S^1 = circle
S^2 = ordinary sphere surface
S^3 = 3-sphere / 4D hypersphere
S^4 = 4-sphere
S^5 = 5-sphere
S^6 = 6-sphere
S^7 = 7-sphere
```

The algebraic ladder marks the special normed-division-algebra dimensions:

```text
S^0 = unit real signs
S^1 = unit complex numbers
S^3 = unit quaternions
S^7 = unit octonions
```

The project should not jump from `S^3` to `S^7` and ignore `S^4`, `S^5`, and `S^6`. Those dimensions remain part of the geometric and suspension roadmap even when `S^1`, `S^3`, and `S^7` carry the strongest algebraic structure.

## Stage Order

1. `D0`: create dimension-indexed scaffolding only.
2. `S2.1`: finite suspended-circle sphere calculus.
3. `S2.2`: sphere grids, latitude rings, pole collapse, and inherited `S^1` coil periods.
4. `S3.1`: finite 3-spheres by suspension.
5. `S3.2`: quaternion calculus for the unit-quaternion `S^3` model.
6. `S3.3`: Hopf-coil executable models and later formal proofs where support is ready.
7. `S456.1`: general suspension and Euler parity for `S^4` through `S^6`.
8. `S7.1`: topological `S^7` by iterated suspension.
9. `S7.2`: quaternionic Hopf roadmap `S^3 -> S^7 -> S^4`.
10. `S7.3`: octonion exploratory algebra, with nonassociativity made explicit.
11. `S15`: future octonionic Hopf horizon.
12. `Phase II`: after the `S^15` horizon, pivot from special sphere objects to maps, bundles, spectra, Bott/Clifford periodicity, boundaries, proof-carrying glyphs, data applications, and compute applications.

## Guardrails

- `C_1` is not `S^0`.
- `C_n x C_m` is torus-like, not a sphere.
- `S^2` does not have a natural group structure like `S^1` or `S^3`.
- `S^3` is not globally `S^2 x S^1`; Hopf structure is globally twisted.
- Continuous geometry, real analysis, smooth manifolds, Hopf fibrations, quaternions, and octonions should be staged after finite combinatorial models.
- Slices, projections, and pictures are explanations, not proofs.
- Unit octonions are not a group; bracketing matters.
- Do not claim a classical Hopf/division-algebra continuation `S^15 -> S^31 -> S^16`.
- Claims about `S^6` complex structures must stay warning/speculative unless formalized from accepted foundations.
- No future theorem may be marked proved without a compiled Lean declaration and the repository proof checks.

## Post-S15 Rule

`S^15` is the exceptional Hopf/division-algebra horizon. Higher spheres may still appear through suspension, stable homotopy, or spectrum machinery, but the roadmap should not keep climbing dimensions as if the same division-algebra pattern continues.

After `S^15`, the project should move from dimension-specific objects to structured transformations:

```text
maps
fibers
bundles
boundaries
fields
spectra
proof-carrying glyphs
applications
```

See `docs/PHASE2_AND_APPLICATIONS.md` for the deferred Phase II and MLX-first compute tracks.

## Current Expansion State

The D0 scaffold exists: dimension manifests, dictionary files, paper folders, Lean/Python scaffolding, and dimension check scripts.

The current proved dimensional spine includes:

- `S^0`: two-point opposition and antipode involution.
- `S^1`: finite circles, rotations, coils, winding, signed orientation, scaling, factors, kernels, images, and fibers.
- `S^2`: suspended-circle counts, sphere grids, latitude rings, pole-fixing rotations, finite antipodes, coordinate projections, and antipodal-pair laws.
- `S^3`: finite suspension counts, quaternion algebra, bounded Hopf coordinate laws, and spin sign-cancellation seeds.
- `S^4` through `S^6`: finite iterated-suspension counts and Euler parity bridge.
- `S^7`: finite topological suspension model, bounded quaternionic Hopf coordinate seeds, and bounded octonion coordinate algebra.
- `Future/S15`: roadmap marker plus finite eightfold-suspension and bounded octonionic Hopf landing seeds.

Full smooth topology, quotient fibration theorems, stable homotopy, Bott/Clifford periodicity, and benchmarked application claims remain future work unless a paper, manifest entry, Lean declaration, and repository checks say otherwise. Track the next implementation stages in `docs/COMPLETION_ROADMAP.md`.
