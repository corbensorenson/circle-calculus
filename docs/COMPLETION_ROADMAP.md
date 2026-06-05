# Completion Roadmap

This is the canonical operating checklist for finishing Circle Calculus as a dimension-organized paper-and-proof corpus.

Use this file as the control surface for long autonomous work. Do not create separate progress reports unless they replace or update this roadmap, the manifests, the dictionary, or a paper.

## Sleep-Mode Goal

```text
/goal Complete the Circle Calculus dimensional paper-and-proof corpus as far as rigorously possible while I am away.

Primary objective:
Build a dimension-organized corpus in which every planned concept has:
- a well-written paper,
- a theorem manifest entry,
- dictionary entries,
- Lean declarations and proofs where feasible,
- Python sidecars/examples where useful,
- paper-to-theorem links,
- passing repository checks,
- updated README and peripheral docs.

Hard proof rule:
Never mark a theorem proved unless it has a compiled Lean declaration, no sorry/admit/unapproved axiom/unsafe proof shortcuts, a theorem manifest entry, and passing checks.

If a theorem cannot be proved in the current run:
- keep it planned, deferred, exploratory_python, lean_stated, or blocked,
- write the paper honestly around that status,
- record the blocker in the manifest,
- keep moving to adjacent scaffold, exposition, tests, or lower-risk theorem targets.

Organization rule:
Maintain one clean roadmap/checklist, update manifests and dictionaries as source-of-truth registries, and avoid clutter reports or duplicate planning documents.

Dependency rule:
Higher dimensions may depend on lower dimensions. Lower dimensions must not import higher dimensions.

Verification rule:
After each meaningful stage, run the relevant checks. Before stopping, run make check and any dimension-specific checks that exist.
```

## Definition Of Done

The project is complete only when all of these are true:

- Every paper in the checklist exists and is written coherently.
- Every formal claim in every paper has a theorem id or is explicitly labeled background, conjecture, exploratory, or future.
- Every theorem id is registered in the appropriate manifest.
- Every proved theorem id points to a compiled Lean declaration.
- Every Lean proof builds without forbidden placeholders.
- Every dictionary term used as project vocabulary is registered.
- Every paper has sidecars for Lean and, where useful, Python executable examples.
- Paper manifests link papers to theorem ids, dictionary ids, and sidecar paths.
- `make check` passes.
- Dimension-specific checks pass once the dimension scaffolding exists.
- `README.md`, `docs/DIMENSIONAL_LADDER.md`, and this file describe the actual current state.

## Non-Negotiables

- Do not fake proofs.
- Do not use `sorry`, `admit`, unapproved axioms, or unsafe shortcuts in proved theorem paths.
- Do not let `S1` import `S2`, `S3`, `S4`, `S5`, `S6`, `S7`, or future modules.
- Do not treat `C_1` as `S^0`.
- Do not treat `C_n x C_m` as a sphere.
- Do not claim `S^2` has a natural group structure like `S^1` or `S^3`.
- Do not claim `S^3` is globally `S^2 x S^1`.
- Do not claim unit octonions form a group.
- Do not rely on unresolved `S^6` complex-structure claims.
- Do not let diagrams, projections, examples, or Python tests stand in for proofs.
- Do not clutter the repo with transient reports.

## Repository Sources Of Truth

- Papers: `papers/`
- Lean proof core: `Circle/`
- Paper proof sidecars: `sidecars/<PAPER_ID>/lean/`
- Python reference models: `circle_math/`
- Python paper examples: `sidecars/<PAPER_ID>/python/`
- Dictionary: `dictionary/circle_dictionary.yaml` and future `dictionary/dimensions/`
- Theorem registry: `manifests/theorem_manifest.yaml` and future `manifests/dimensions/`
- Paper registry: `manifests/paper_manifest.yaml`
- Dimensional plan: `docs/DIMENSIONAL_LADDER.md`
- Deferred Phase II and applications context: `docs/PHASE2_AND_APPLICATIONS.md`
- Completion control: this file

## Work Order

Prefer this order. Only skip ahead when blocked and record the blocker.

1. Keep current `S1` green.
2. Add dimensional scaffolding and checks.
3. Finish missing `S1` papers and proofs.
4. Backfill `S0` if useful for notation and sign/opposition.
5. Build `S2` finite sphere calculus.
6. Build `S3` finite hypersphere calculus.
7. Build `S3` quaternion calculus.
8. Add `S3` Hopf executable models and formal proofs where feasible.
9. Build `S4` through `S6` suspension/Euler bridge.
10. Build topological `S7` by iterated suspension.
11. Add `S7` quaternionic Hopf roadmap/models.
12. Add `S7` octonion exploratory algebra and formalize only robust targets.
13. Add future `S15` roadmap only after `S7` foundations are stable.
14. After the `S15` horizon, stop treating dimension climbing as the main objective. Pivot to Phase II: maps, bundles, spectra, Bott/Clifford periodicity, boundaries, proof-carrying glyphs, data applications, and compute applications.

## Stage D0: Dimensional Scaffolding

Goal: organize the future without changing proved `S1` mathematics.

Status: implemented as scaffolding. The dimension checks are now part of `make check`.

Required artifacts:

- [x] `manifests/dimensions/dimension_index.yaml`
- [x] `manifests/dimensions/Common.yaml`
- [x] `manifests/dimensions/S0_opposition.yaml`
- [x] `manifests/dimensions/S1_circle.yaml` or an adapter to the existing manifest
- [x] `manifests/dimensions/S2_sphere.yaml`
- [x] `manifests/dimensions/S3_hypersphere.yaml`
- [x] `manifests/dimensions/S4_4sphere.yaml`
- [x] `manifests/dimensions/S5_5sphere.yaml`
- [x] `manifests/dimensions/S6_6sphere.yaml`
- [x] `manifests/dimensions/S7_octonionic.yaml`
- [x] `manifests/dimensions/S15_future.yaml`
- [x] `dictionary/dimensions/Common.yaml`
- [x] `dictionary/dimensions/S0.yaml`
- [x] `dictionary/dimensions/S1.yaml`
- [x] `dictionary/dimensions/S2.yaml`
- [x] `dictionary/dimensions/S3.yaml`
- [x] `dictionary/dimensions/S4_S6.yaml`
- [x] `dictionary/dimensions/S7.yaml`
- [x] `dictionary/dimensions/S15.yaml`
- [x] `dictionary/dimensions/warnings.yaml`
- [x] planned paper stubs under `papers/S0/`, `papers/S1/`, `papers/S2/`, `papers/S3/`, `papers/S4_S6/`, `papers/S7/`, `papers/future/S15/`
- [x] `Circle/Common/`, `Circle/S0/`, `Circle/S1/`, `Circle/S2/`, `Circle/S3/`, `Circle/S4/`, `Circle/S5/`, `Circle/S6/`, `Circle/S7/`, `Circle/Future/S15/`
- [x] `circle_math/dimensions/`
- [x] `tests/dimensions/`
- [x] dimension check scripts:
  - [x] `scripts/check_dimension_index.py`
  - [x] `scripts/check_dimension_imports.py`
  - [x] `scripts/check_dimension_manifests.py`
  - [x] `scripts/check_dimension_paper_links.py`

All future theorem statuses must remain planned, deferred, exploratory_python, or lean_stated until actual proofs exist.

## Paper Checklist

### S1: Circle Core

- [ ] `papers/S1/PAPER_S1_01_FINITE_CIRCLES.md`
  - Current source: `papers/PAPER_01_FINITE_CIRCLES.md`
  - Proof targets: `CC-T0001` through `CC-T0007`
  - Status: proved theorem spine exists; paper should be polished and relocated or linked through the dimension layout.
- [ ] `papers/S1/PAPER_S1_02_WINDING_NATURALS.md`
  - Current source: `papers/PAPER_02_WINDING_NATURALS.md`
  - Proof targets: `CC-T0009` through `CC-T0016`
  - Status: proved theorem spine exists; paper should be polished and relocated or linked through the dimension layout.
- [ ] `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md`
  - Proof targets: oriented winding, signed residues, integer addition, additive inverse, reversible motion.
- [ ] `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md`
  - Proof targets: `CC-T0008`, multiplication as repeated rotation/scaling, invertibility iff coprime, factor structure, prime/full-coil refinements.

### S0: Opposition And Sign

- [x] `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md`
  - Proof targets: `S0-T0001`, `S0-T0002`
  - Status: both finite opposition facts are Lean-proved in `Circle/S0/Scaffold.lean`.
  - Warning target: `S0-W0001`, `C_1` is not `S^0`.

### S2: Sphere Calculus

- [ ] `papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md`
  - Proof targets: `S2-T0001`, `S2-T0002`
  - Main model: `SuspC(n)`, with `V=n+2`, `E=3n`, `F=2n`, `chi=2`.
- [ ] `papers/S2/PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md`
  - Proof targets: `S2-T0003` through `S2-T0007`
  - Warning targets: `S2-W0001`, `S2-W0002`, `S2-W0003`
  - Main model: `SphereGrid(n,r)`, with pole collapse and latitude rings.
- [ ] `papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md`
  - Proof targets to add as the model matures: antipodal map, axis, meridians, surface closure, antinodes.
  - Do not force continuous geometry too early.

### S3: Hypersphere, Quaternions, Hopf

- [ ] `papers/S3/PAPER_S3_01_FINITE_HYPERSPHERES.md`
  - Proof targets: `S3C-T0001` through `S3C-T0004`
  - Main model: suspension of finite 2D cell-count structures.
- [ ] `papers/S3/PAPER_S3_02_QUATERNION_COILS.md`
  - Proof targets: `S3Q-T0001` through `S3Q-T0005`
  - Prefer mathlib quaternion support when available.
- [ ] `papers/S3/PAPER_S3_03_HOPF_COILS.md`
  - Proof/model targets: `S3H-T0001` through `S3H-T0003`
  - Warning target: `S3H-W0001`, not globally `S^2 x S^1`
  - Start with Python numeric models if Lean analysis support is too heavy.
- [ ] `papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md`
  - Proof targets to add after quaternion basics: `q` and `-q` represent the same 3D rotation.

### S4-S6: Geometric Bridge

- [ ] `papers/S4_S6/PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md`
  - Proof target: `S456-T0001`
  - Main result: `chi(S^d)=1+(-1)^d` for finite iterated suspension models.
- [ ] `papers/S4_S6/PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md`
  - Proof target: `S4-T0001`
  - Roadmap target: role of `S^4` as base of `S^3 -> S^7 -> S^4`.
- [ ] `papers/S4_S6/PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md`
  - Proof target: `S5-T0001`
  - Keep projective geometry exploratory unless formalized.
- [ ] `papers/S4_S6/PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md`
  - Proof target: `S6-T0001`
  - Warning target: `S6-W0001`

### S7: Topological, Quaternionic Hopf, Octonionic

- [ ] `papers/S7/PAPER_S7_01_TOPOLOGICAL_7SPHERE.md`
  - Proof targets: `S7C-T0001`, `S7C-T0002`
  - Prove topological/combinatorial `S7` before octonion algebra.
- [ ] `papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md`
  - Targets: `S7QH-T0001`, `S7QH-T0002`
  - Keep roadmap/exploratory until `S3` quaternion calculus and `S4` base are stable.
- [ ] `papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md`
  - Targets: `S7O-T0001` through `S7O-T0006`
  - Warning targets: `S7O-W0001`, `S7O-W0002`
  - Unit octonions are not a group.

### Future S15

- [ ] `papers/future/S15/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md`
  - Future target: `S15-T0001`
  - Do not implement before `S7` is stable.

### Phase II: Structured Transformations After S15

This section records deferred work from the browser handoffs. It is not active proof status. The detailed context lives in `docs/PHASE2_AND_APPLICATIONS.md`.

Guardrail: after `S^15`, do not invent a false classical Hopf/division-algebra continuation such as `S^15 -> S^31 -> S^16`. Higher spheres should move into general suspension, stable homotopy, or spectrum machinery instead.

- [ ] `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md`
  - Program: suspension, stable maps, spectra, and stable invariants.
- [ ] `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md`
  - Program: Clifford algebras, spinors, Bott periodicity, and dimension clocks.
- [ ] `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md`
  - Program: base, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance.
- [ ] `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md`
  - Program: boundaries, `boundary(boundary)=0`, cobordisms, fields, and proofs as transformations.
- [ ] `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md`
  - Program: glyphs with formal syntax, normal forms, theorem dependencies, proof certificates, semantic models, and projection views.
- [ ] `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md`
  - Program: coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks.
- [ ] `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md`
  - Program: certified cyclic/circulant/orbit structure lowered to FFT/NTT/permutation backends and benchmarked.

Deferred manifest families:

- [ ] `manifests/theories/stable_sphere_calculus.yaml`
- [ ] `manifests/theories/bott_clifford_calculus.yaml`
- [ ] `manifests/theories/bundle_calculus.yaml`
- [ ] `manifests/theories/boundary_cobordism_calculus.yaml`
- [ ] `manifests/theories/glyph_proof_interface.yaml`
- [ ] `manifests/applications/coil_data_analysis.yaml`
- [ ] `manifests/applications/coil_compute.yaml`

Application guardrails:

- [ ] Keep novelty claims disciplined: known mathematics is background; the possible contribution is the proof-carrying interface, dictionary, manifests, glyph/provenance layer, and tested applications.
- [ ] Treat proof-carrying diagrams as a first demonstrator: glyph/diagram to theorem id, Lean declaration, proof certificate, Python example, and paper section.
- [ ] Treat number provenance as first-class only after the finite-circle factor/orbit spine is stable.
- [ ] For local compute work, use MLX/Mac-compatible acceleration first. CUDA/cuFFT references are future portability notes or external baselines, not the active backend on this machine.
- [ ] Benchmark compute claims against ordinary dense/direct baselines before presenting any speedup as real.

## Common Proof Targets

- [ ] `COMMON-T0001`: Euler characteristic of a finite cell-count list.
- [ ] `COMMON-T0002`: suspension cell-count transform.
- [ ] `COMMON-T0003`: suspension Euler transform, `chi(Susp(K)) = 2 - chi(K)`.

## Current S1 Proof Status

Already proved and linked:

- [x] `CC-T0001`: rotation by zero
- [x] `CC-T0002`: rotation composition
- [x] `CC-T0003`: rotation inverse
- [x] `CC-T0004`: closure condition
- [x] `CC-T0005`: period equals `n / gcd(n,k)`
- [x] `CC-T0006`: orbit decomposition count
- [x] `CC-T0007`: prime full coil
- [x] `CC-T0008`: scaling invertible iff coprime
- [x] `CC-T0009`: unique winding/residue lift
- [x] `CC-T0010`: lifted addition decomposition
- [x] `CC-T0011`: lifted existence
- [x] `CC-T0012`: successor with carry
- [x] `CC-T0013`: lifted addition right zero identity
- [x] `CC-T0014`: lifted addition associativity at reconstructed-value level
- [x] `CC-T0015`: lifted addition left zero identity
- [x] `CC-T0016`: iterated lifted successor

Still planned:

- Scaling/factor refinements beyond `CC-T0008`: multiplication as repeated scaling, factor structure, and prime/full-coil refinements.

## Verification Checklist

Run these whenever relevant:

```bash
make check
```

Dimension checks are included in `make check` and can also be run directly:

```bash
python scripts/check_dimension_index.py
python scripts/check_dimension_imports.py
python scripts/check_dimension_manifests.py
python scripts/check_dimension_paper_links.py
```

Before any push:

- [ ] `lake build`
- [ ] Lean sidecars compile
- [ ] Python tests pass
- [ ] theorem manifest validates
- [ ] dictionary validates
- [ ] paper theorem links validate
- [ ] no fake proof markers
- [ ] dimension checks pass if present
- [ ] `README.md` describes current state
- [ ] no transient reports, caches, build artifacts, or local secrets are staged

## Wake-Up State

If the whole corpus is not finished by the time work pauses, the repo should still be in a useful wake-up state:

- `make check` passes, or the exact failing command is known.
- This roadmap reflects completed, pending, and blocked work.
- Manifest statuses are honest.
- Papers do not claim planned/blocked theorems are proved.
- The README points to the current stage.
- The public GitHub repo has the latest clean commit pushed when appropriate.
