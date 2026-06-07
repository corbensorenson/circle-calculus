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
- a downstream Living Book explanation layer where appropriate,
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

README state rule:
After meaningful proof batches, paper batches, roadmap changes, or application-context additions, update `README.md` so it reflects the actual current state, proof status, usage pointers, and where to find the relevant docs. Do not churn the README for tiny internal-only edits.

During autonomous sleep-mode work, apply the README state rule periodically: after each meaningful proof/paper batch and after each new browser handoff is absorbed into durable context, keep `README.md` aligned with the actual repo state before pushing.

Overnight expansion rule:
Do not treat Phase II, applications, `S15`, or other future-horizon sections as permanently parked. Work them now whenever they have tractable finite seeds, honest theorem targets, paper improvements, dictionary gaps, sidecar examples, Living Book links, or benchmark fixtures. Keep status labels strict: topology-heavy, benchmark, or domain claims remain planned, exploratory, deferred, or blocked until Lean proofs, executable models, and guardrail checks justify stronger claims.

Autonomous theorem discovery rule:
If the explicit roadmap is exhausted or every current item is blocked, search authoritative mathematical sources for additional theorems, constructions, and standard structures that can be translated into Circle Calculus. Prioritize hard-but-tractable targets that demonstrate real leverage: proof-carrying diagrams, finite cyclic structure, orbit/fiber/provenance facts, quaternion/Hopf/sign ambiguity facts, finite suspension/Euler facts, data-analysis descriptors, and application models with clear baselines. Record source context, add manifest entries before paper claims, and preserve proof-status honesty.

Dependency rule:
Higher dimensions may depend on lower dimensions. Lower dimensions must not import higher dimensions.

Verification rule:
After each meaningful stage, run the relevant checks. Before stopping, run make check and any dimension-specific checks that exist.

GitHub CI rule:
Treat local `make check` as the pre-commit/push gate. After a push, do not sit and wait on GitHub CI unless debugging a known failure. Push and continue working. Before the next push, inspect the previous GitHub CI result once; if it failed, fix that failure in the next commit before sending more work.
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
- Phase III Living Book source pages, widgets, generated data, and checks exist once that phase begins, and they do not upgrade proof status beyond the manifests.
- Phase IV wide/deep theorem discovery has audited every dimension and application area for missing theorem targets, weak papers, proof gaps, and better formal spines.
- Phase V edge problem-space exploration has identified hard, awkward, or ordinary-math-resistant problem spaces where Circle Calculus might give practical leverage, with experiments and claims kept honest.
- The dedicated Circle AI program has explored phase channels, cyclic memory, coil/sparse attention, adapter blocks, RoPE/MultiCoil positional structure, recurrent/state-space/convolutional sequence models, harmonic/circulant features, geometry-aware representations, proof-carrying model components, and MLX/Mac-compatible prototypes with proof status and benchmark claims kept separate.
- Phase VI global sweep has cleaned the whole corpus for correctness, soundness, prose quality, link integrity, proof status, and reader usability.
- `make check` passes.
- Living Book checks and `quarto render site` pass once the Quarto site exists, unless Quarto is explicitly unavailable and the blocker is documented.
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
- Do not let Living Book pages, widgets, theorem boxes, status badges, or captions present a theorem as proved unless the manifest and compiled Lean declaration say so.
- Do not introduce Manim, TTS, narration, video rendering, or a heavy frontend framework before the static Quarto Living Book and S1 widgets are stable.
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
- Phase IV theorem target registry: `manifests/phase4_theorem_targets.yaml`
- Phase IV target coverage/theorem-reference check: `scripts/check_phase4_targets.py`
- Dedicated Circle AI edge target: `P5-EDGE-009` in `manifests/phase5_edge_targets.yaml`
- Phase VI sweep registry: `manifests/phase6_sweep_targets.yaml`
- Application benchmark/edge-claim guardrails: `scripts/check_application_guardrails.py`
- Dimensional plan: `docs/DIMENSIONAL_LADDER.md`
- Phase II and applications context: `docs/PHASE2_AND_APPLICATIONS.md`
- Phase III Living Book plan: `docs/LIVING_BOOK_POLICY.md`, `docs/LIVING_BOOK_ROADMAP.md`, and `docs/LIVING_BOOK_WIDGETS.md`
- Living Book source once implemented: `site/`
- Completion control: this file

## Work Order

Prefer this order. Only skip ahead when blocked and record the blocker. During long autonomous runs, proceed from start to finish through this roadmap. When a target is blocked, record the blocker honestly, move to the next useful adjacent item, and return later instead of stopping the whole run.

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
13. Work the `S15` horizon as an active target layer once `S7` foundations are stable enough for honest finite seeds, warnings, and blocked targets.
14. After each `S15` pass, stop treating dimension climbing as the only objective. Pivot to Phase II: maps, bundles, spectra, Bott/Clifford periodicity, boundaries, proof-carrying glyphs, data applications, and compute applications.
15. Build Phase III: a Quarto-based Circle Calculus Living Book generated from manifests, dictionary entries, papers, Python reference models, and Lean proof metadata. Start with static S1 interactives and do not let the site drift from proof status.
16. Build Phase IV: go wide and deep across all dimensional levels, looking for additional theorem targets, stronger proof spines, missing dictionary terms, paper improvements, and proof-sidecar improvements.
17. Build Phase V: search edge problem spaces where Circle Calculus might do something hard, awkward, or unavailable in ordinary presentations, and turn promising leads into honest experiments, papers, models, or theorem targets.
18. Build the dedicated Circle AI deep program. Treat AI as an active first-class track that explores phase channels, cyclic memory, coil/sparse attention, adapter blocks, RoPE/MultiCoil positional structure, recurrent/state-space/convolutional sequence models, harmonic/circulant features, geometry-aware representations, proof-carrying model components, and MLX/Mac-compatible prototypes. For each avenue, add proof targets where tractable, executable fixtures, ordinary baselines, negative controls, benchmark scripts, paper improvements, and Living Book links.
19. Build Phase VI: sweep the entire project for correctness, clarity, style, consistency, proof status, broken links, missing citations, overclaims, and prose that should sound cleaner to a new reader.
20. If the roadmap is exhausted or blocked, search authoritative sources for additional theorem targets and convert the best candidates into manifests, dictionary entries, papers, Lean/Python sidecars, and Living Book links.

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

## Python Sidecar Backfill

Goal: make the executable examples line up with the Lean-backed papers without duplicating adapter-only material. The sidecars remain support artifacts; they never turn an unproved statement into a proved theorem.

- [x] Root `S1` finite-circle and winding papers already have Python examples through `sidecars/PAPER_01_FINITE_CIRCLES/python/test_paper_01_examples.py` and `sidecars/PAPER_02_WINDING_NATURALS/python/test_paper_02_examples.py`.
- [x] `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md` has Python examples for the two-point model, antipode involution, no-fixed-point flip, named sign swap, antipode bijection, and `C_1` warning.
- [x] `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md` has Python examples for zero signed rotation, signed composition, inverse motion, and signed-rotation bijectivity.
- [x] `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md` already has Python examples for the scaling/factor spine.
- [x] Backfill `S2` Python examples for suspended circles, sphere grids, antipodes, and finite coordinate rotations.
- [x] Backfill `S3` Python examples for finite hypersphere counts, quaternion coils, and spin sign cancellation. `PAPER_S3_03_HOPF_COILS` already has Python examples.
- [x] Backfill `S4` through `S6` Python examples for suspension/Euler bridge papers.
- [x] Backfill `S7` and future `S15` Python examples for finite suspension/topological landing facts where useful.
- [x] Phase II and application seed papers now have Python examples or benchmark sidecars where useful.

## Paper Checklist

### S1: Circle Core

- [x] `papers/S1/PAPER_S1_01_FINITE_CIRCLES.md`
  - Current source: `papers/PAPER_01_FINITE_CIRCLES.md`
  - Proof targets: `CC-T0001` through `CC-T0007`, plus `CC-T0054`, `CC-T0055`, and `CC-T0059` through `CC-T0061`
  - Status: polished dimension guide draft links the proved theorem spine into the dimension layout while keeping the root paper as the detailed source. The full same-orbit iff gcd-congruence representative theorem is Lean-proved as `CC-T0061`; `P5-EDGE-002` adds an exploratory finite-coil theorem-signature index for proof navigation.
- [x] `papers/S1/PAPER_S1_02_WINDING_NATURALS.md`
  - Current source: `papers/PAPER_02_WINDING_NATURALS.md`
  - Proof targets: `CC-T0009` through `CC-T0016`
  - Status: polished dimension guide draft links the proved theorem spine into the dimension layout while keeping the root paper as the detailed source.
- [x] `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md`
  - Proof targets: oriented winding, signed residues, integer addition, additive inverse, reversible motion.
  - Status: polished draft; signed zero, composition, inverse motion, and signed-rotation bijectivity are Lean-proved as `S1O-T0001` through `S1O-T0004`.
- [x] `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md`
  - Proof targets: `CC-T0008`, `CC-T0017` through `CC-T0054`, and `CC-T0056` through `CC-T0058`, multiplication as repeated rotation/scaling, invertibility iff coprime, factor structure, prime/full-coil refinements, and affine scale-then-rotation maps.
  - Status: polished draft; scaling invertible iff coprime, scale-by-zero collapse, scale-by-one identity, scaling composition, scale-factor congruence normalization, scaling transport of rotation stride, scaling transport of finite coil steps, scaling natural steps into coil traversal, prime-circle scaling bijectivity, divisor/cofactor collapse, cofactor-multiple collapse, cofactor-shift address collapse, scaling-zero divisibility, period-level kernel divisibility, period-multiple collapse, period-shift collapse, period-normal representatives, period-congruence scaled equality, bounded period-representative injectivity, period-representative image cardinality and membership, whole-circle scaling image equality and cardinality, canonical kernel/fiber representative equality and cardinality, zero-fiber/kernel and scaled-target/fiber bridges, fiber-set equality modulo scaled value and stride period, arbitrary target-fiber emptiness/cardinality, image-times-fiber and image-times-kernel scaling factorizations, kernel-subgroup membership, scaled-address product congruence, coprime scaling reflection, full-coil iff coprime, rotation bijectivity, affine composition normal form, and coprime affine bijectivity are Lean-proved; the `P5-EDGE-002` theorem-signature fixture and `P5-EDGE-003` number-provenance fixture index this spine for proof navigation; affine classification and composite orbit refinements remain future extensions.

### S0: Opposition And Sign

- [x] `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md`
  - Proof targets: `S0-T0001` through `S0-T0005`
  - Status: polished draft; the finite opposition cardinality, involution, no-fixed-point, named-swap, and antipode-bijection facts are Lean-proved in `Circle/S0/Scaffold.lean`.
  - Warning target: `S0-W0001`, `C_1` is not `S^0`.

### S2: Sphere Calculus

- [x] `papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md`
  - Proof targets: `S2-T0001`, `S2-T0002`
  - Status: polished draft; suspended-circle counts and Euler characteristic are Lean-proved in `Circle/S2/Scaffold.lean`.
  - Main model: `SuspC(n)`, with `V=n+2`, `E=3n`, `F=2n`, `chi=2`.
- [x] `papers/S2/PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md`
  - Proof targets: `S2-T0003` through `S2-T0007`, plus `S2-T0017`
  - Status: polished draft; sphere-grid counts, Euler characteristic, latitude-ring model, pole-fixing rotation, inherited latitude coil period, and inherited latitude orbit-count theorem are Lean-proved.
  - Warning targets: `S2-W0001`, `S2-W0002`, `S2-W0003`
  - Main model: `SphereGrid(n,r)`, with pole collapse and latitude rings.
- [x] `papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md`
  - Proof targets to add as the model matures: antipodal map, axis, meridians, surface closure, antinodes.
  - Do not force continuous geometry too early.
  - Status: polished draft; suspended-circle antipode pole swap, involution, finite bijection, finite signed longitude-rotation bijection, finite sphere-grid longitude-rotation bijection, finite pole/equator subset preservation, finite suspended longitude/opposite-stride law, finite sphere-grid latitude/longitude coordinate rotation laws, and finite antipodal-pair witness/symmetry facts are Lean-proved as `S2-T0008` through `S2-T0016` plus `S2-T0018` through `S2-T0020`; continuous surface geometry remains a future refinement.

### S3: Hypersphere, Quaternions, Hopf

- [x] `papers/S3/PAPER_S3_01_FINITE_HYPERSPHERES.md`
  - Proof targets: `S3C-T0001` through `S3C-T0004`
  - Main model: suspension of finite 2D cell-count structures.
  - Status: polished draft; suspended-surface counts, Euler-zero theorem, suspended-suspended-circle counts, and Euler characteristic are Lean-proved.
- [x] `papers/S3/PAPER_S3_02_QUATERNION_COILS.md`
  - Proof targets: `S3Q-T0001` through `S3Q-T0008`
  - Prefer mathlib quaternion support when available.
  - Status: polished draft; real quaternion norm, unit closure, conjugate inverse equations, bundled identity/inverse laws, bundled conjugation involution, noncommutative example, and associativity are Lean-proved.
- [x] `papers/S3/PAPER_S3_03_HOPF_COILS.md`
  - Proof/model targets: `S3H-T0001` through `S3H-T0008`
  - Warning target: `S3H-W0001`, not globally `S^2 x S^1`
  - Start with Python numeric models if Lean analysis support is too heavy.
  - Status: polished draft; `S3H-T0001` through `S3H-T0008` are Lean-proved bounded Hopf coordinate, phase-multiplication, and phase-action facts, including the Hopf phase action wrapper; analytic circle parameterization beyond these algebraic phase laws, quotient topology, and global fibration formalization remain future work.
- [x] `papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md`
  - Proof target: `S3S-T0001` through `S3S-T0004`
  - Status: polished draft proves quaternion conjugation identity action, zero preservation, sign cancellation, and the unit-quaternion sign equivalence relation; `P5-EDGE-007` adds a bounded orientation-debugging note and sign-ambiguity Python record; full `SO(3)` quotient remains future work.

### S4-S6: Geometric Bridge

- [x] `papers/S4_S6/PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md`
  - Proof targets: `COMMON-T0001` through `COMMON-T0006`, plus `S456-T0001`
  - Status: polished draft proves the finite suspension/Euler parity bridge `chi(S^d)=1+(-1)^d` for the current `S^4` through `S^6` models, the direct finite double-suspension Euler theorem, and the general finite iterated-suspension Euler/two-step parity theorem.
- [x] `papers/S4_S6/PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md`
  - Proof targets: `S4-T0001`, `S4-T0002`
  - Status: polished draft proves the finite `S^4` suspension/Euler anchor and records the future role of `S^4` as base of `S^3 -> S^7 -> S^4`.
- [x] `papers/S4_S6/PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md`
  - Proof targets: `S5-T0001`, `S5-T0002`
  - Status: polished draft proves the finite `S^5` suspension/Euler anchor and keeps projective geometry exploratory unless formalized.
- [x] `papers/S4_S6/PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md`
  - Proof targets: `S6-T0001` through `S6-T0003`
  - Warning target: `S6-W0001`
  - Status: polished draft proves the finite `S^6` suspension/Euler anchor and warning-boundary marker, and keeps the `S^6` complex-structure warning explicit.

### S7: Topological, Quaternionic Hopf, Octonionic

- [x] `papers/S7/PAPER_S7_01_TOPOLOGICAL_7SPHERE.md`
  - Proof targets: `S7C-T0001`, `S7C-T0002`, `S7C-T0003`
  - Prove topological/combinatorial `S7` before octonion algebra.
  - Status: polished draft proves the finite iterated-suspension model, S6 suspension link, and Euler characteristic before octonion algebra enters.
- [x] `papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md`
  - Targets: `S7QH-T0001` through `S7QH-T0005`
  - Keep roadmap/exploratory until `S3` quaternion calculus and `S4` base are stable.
  - Status: polished draft; `S7QH-T0001` through `S7QH-T0005` are Lean-proved coordinate landing, right-phase norm scaling/preservation, right-phase invariance, and right-phase action theorems; quaternionic projective space, quotient topology, and full fibration formalization remain future work.
- [x] `papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md`
  - Targets: `S7O-T0001` through `S7O-T0008`
  - Warning targets: `S7O-W0001`, `S7O-W0002`
  - Unit octonions are not a group.
  - Status: polished draft; `S7O-T0001` through `S7O-T0008` are Lean-proved in a bounded Cayley-Dickson coordinate model, including two-sided conjugate norm and bracket-explicit norm-one conjugate inverse equations; higher octonion library design and octonionic Hopf formalization remain future work.

### Future S15

- [x] `papers/future/S15/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md`
  - Future targets: `S15-T0001` through `S15-T0009`
  - Do not claim the full octonionic Hopf fibration before quotient topology and a correct bracketed phase action are formalized.
  - Status: polished draft records `S15-T0001` as a Lean roadmap marker; `S15-T0002` through `S15-T0009` are Lean-proved finite topological, eight-suspension parity, coordinate landing, safe right-phase landing, and warning-boundary facts. The naive full-coordinate right unit-octonion phase-invariance target is blocked by a formal counterexample; full fibration topology remains future work.

### Phase II: Structured Transformations After S15

This section records deferred and active Phase II work from the browser handoffs. The detailed context lives in `docs/PHASE2_AND_APPLICATIONS.md`; proof status still comes only from Lean-linked theorem ids and manifests.

Guardrail: after `S^15`, do not invent a false classical Hopf/division-algebra continuation such as `S^15 -> S^31 -> S^16`. Higher spheres should move into general suspension, stable homotopy, or spectrum machinery instead.

- [x] `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md`
  - Program: suspension, stable maps, spectra, and stable invariants.
  - Status: polished draft; `P2S-T0001` through `P2S-T0005` are Lean-proved finite double/four/eight suspension facts with Python examples; stable maps, spectra, and stable homotopy claims remain future work.
- [x] `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md`
  - Program: Clifford algebras, spinors, Bott periodicity, and dimension clocks.
  - Status: polished draft; `P2B-T0001` through `P2B-T0004` are Lean-proved finite period-8 clock facts with Python examples; Clifford algebras, K-theory, KO-theory, and Bott periodicity remain future formalization work.
- [x] `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md`
  - Program: base, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance.
  - Status: polished draft; `P2BU-T0001` through `P2BU-T0009` are Lean-proved trivial product-bundle projection/fiber and base-preserving transition sanity facts with Python examples; nontrivial bundles, overlap/cocycle data, connections, curvature, and holonomy remain future work.
- [x] `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md`
  - Program: boundaries, `boundary(boundary)=0`, cobordisms, fields, and proofs as transformations.
  - Status: polished draft; `P2BC-T0001` through `P2BC-T0005` are Lean-proved directed-interval boundary facts with Python examples; general chain complexes, cobordisms, TQFT, and physics-adjacent claims remain future work.
- [x] `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md`
  - Program: glyphs with formal syntax, normal forms, theorem dependencies, proof certificates, semantic models, and projection views.
  - Status: polished draft; `P2G-T0001` through `P2G-T0006` are Lean-proved proof-glyph certificate projection, finite theorem-metadata validity, and manifest-growth facts with Python examples; `P5-EDGE-001` adds an exploratory generated glyph-status fixture; glyph syntax, normal forms, semantics, dependency correctness, and proof search remain future work.
- [x] `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md`
  - Program: coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks.
  - Status: polished draft; `APPD-T0001` through `APPD-T0005` are Lean-proved finite phase-coordinate facts with Python examples. `APPD-B0001` and `APPD-B0002` are exploratory Python fixtures comparing coil closure ranking with autocorrelation and periodogram-style baselines on deterministic clean, noisy, aliased, and multi-period synthetic signals; real-data and usefulness claims remain future work.
- [x] `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md`
  - Program: certified cyclic/circulant/orbit structure lowered to FFT/NTT/permutation backends and benchmarked.
  - Status: polished draft; `COMPC-T0001` through `COMPC-T0005` are Lean-proved cyclic-address facts with Python examples; backend lowering and performance claims remain benchmark work.
- [x] `papers/applications/PAPER_COMP_02_COIL_RAY_AND_SAMPLING.md`
  - Program: `CoilRay Sort`, `CoilSampler`, `CoilNoise`, `CoilSTIR`, BRDF/lighting angular compression, spherical-coil ray queues, procedural placement/dithering, and rendering benchmarks.
  - Status: polished draft; `COMPR-T0001` through `COMPR-T0005` are Lean-proved direction-bin schedule facts with Python examples; rendering performance, coherence, and sampling-quality claims remain benchmark work.
- [x] `papers/applications/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT.md`
  - Program: `CoilLayout`, `CoilStencil`, `CoilNTT`, gcd-cycle memory layouts, verified periodic boundaries, exact finite transforms, and MLX/Mac-compatible prototypes where relevant.
  - Status: polished draft; `COMPL-T0001` through `COMPL-T0005` are Lean-proved stride-address facts with Python examples; `COMPL-B0001` and `COMPL-B0002` are exploratory CoilLayout/stencil validation fixtures; layout, FFT, NTT, MLX/backend, and performance claims remain future work.
- [x] `papers/applications/PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS.md`
  - Program: `CoilHash`, `CoilMotion`, `CoilPRM`, `CoilCodec`, `CoilANN`, `CoilAcquire`, `CoilCAM`, `CoilTorsion`, `CoilDetect`, `CoilSched`, and `CoilQ` as benchmarked or domain-tested application roadmaps.
  - Status: polished draft; `COMPS-T0001` through `COMPS-T0004` are Lean-proved round-robin schedule facts with Python examples; fairness, load balancing, robotics, codec, ANN, acquisition, CAM, torsion, detection, and quantum claims remain future domain work.
- [x] `papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md`
  - Program: disciplined Circle AI thesis covering phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, geometry-aware models, and proof-carrying model components.
  - Status: polished draft; `AIA-T0001` through `AIA-T0005` are Lean-proved phase-channel facts with Python examples; `AIA-B0001` and `AIA-B0002` are exploratory deterministic phase-channel benchmark fixtures; model-quality and speed claims remain benchmark work.
- [x] `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`
  - Program: Coil Attention, CoilKV, long-context retrieval, alias control, stride/orbit coverage, and comparisons against full attention, sparse attention, Hyena-like mixers, and S4/Mamba-like baselines.
  - Status: polished draft; `AIM-T0001` through `AIM-T0005` are Lean-proved cyclic-memory-slot facts with Python examples; `AIM-B0001` is an exploratory cyclic-memory fixture with constant/scalar-threshold baselines and a nonperiodic control; `AIM-B0002` is an exploratory coil-retrieval reachability fixture with coil-path, local-window, wrong-stride, full-attention oracle, and near-lag controls; retrieval quality, alias control, and attention replacement claims remain benchmark work.
- [x] `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md`
  - Program: CoilLinear, CoilRA, MultiCoil RoPE, periodic activations, and MLX-first benchmarks against dense, LoRA, block-circulant, and standard RoPE baselines.
  - Status: polished draft; `AIRA-T0001` through `AIRA-T0005` are Lean-proved adapter-block facts with Python examples; `AIRA-B0001` is an exploratory adapter-block fixture with constant/scalar-threshold baselines and a nonperiodic control; `AIRA-B0002` is an exploratory MultiCoil/RoPE-style positional fixture with single-period, constant, scalar-threshold, and nonperiodic controls; CoilRA, MultiCoil RoPE, model quality, parameter efficiency, and runtime claims remain benchmark work.

Created planned manifest families:

- [x] `manifests/theories/stable_sphere_calculus.yaml`
- [x] `manifests/theories/bott_clifford_calculus.yaml`
- [x] `manifests/theories/bundle_calculus.yaml`
- [x] `manifests/theories/boundary_cobordism_calculus.yaml`
- [x] `manifests/theories/glyph_proof_interface.yaml`
- [x] `manifests/applications/coil_data_analysis.yaml`
- [x] `manifests/applications/coil_compute.yaml`
- [x] `manifests/applications/coil_rendering.yaml`
- [x] `manifests/applications/coil_systems.yaml`
- [x] `manifests/applications/circle_ai.yaml`

Application guardrails:

- [x] Keep novelty claims disciplined: known mathematics is background; the possible contribution is the proof-carrying interface, dictionary, manifests, glyph/provenance layer, and tested applications.
- [x] Treat proof-carrying diagrams as a first demonstrator: glyph/diagram to theorem id, Lean declaration, proof certificate, Python example, and paper section.
- [x] Treat number provenance as first-class only after the finite-circle factor/orbit spine is stable.
- [x] For local compute work, use MLX/Mac-compatible acceleration first. CUDA/cuFFT references are future portability notes or external baselines, not the active backend on this machine.
- [x] Benchmark compute claims against ordinary dense/direct baselines before presenting any speedup as real.
- [x] Prioritize `CoilRay Sort`, `CoilLayout`, and `CoilNTT` as the first non-AI compute prototypes after the dimensional proof spine is stable enough.
- [x] Treat ray tracing, periodic simulations, crypto/ZK transforms, systems scheduling, and vector indexing as applications to benchmark, not as automatic proof-theorem consequences.
- [x] Keep Circle AI claims benchmark-driven: no claim that circles improve all AI; only target cyclic, periodic, convolutional, rotational, harmonic, memory-like, or proof-search-like structure.
- [x] Stage AI work in this order when the proof/math spine is ready: CoilLinear/CoilRA prototypes, MultiCoil RoPE, Coil Attention plus CoilKV, activation-coil interpretability, then spherical/quaternion models. Keep octonion AI exploratory.

## Common Proof Targets

- [x] `COMMON-T0001`: Euler characteristic of a finite cell-count list.
- [x] `COMMON-T0002`: suspension cell-count transform.
- [x] `COMMON-T0003`: suspension Euler transform, `chi(Susp(K)) = 2 - chi(K)`.
- [x] `COMMON-T0004`: general iterated finite suspension Euler theorem.
- [x] `COMMON-T0005`: two-step finite suspension Euler parity theorem.
- [x] `COMMON-T0006`: direct finite double-suspension Euler theorem.
- [x] `P2S-T0001`: finite double suspension preserves Euler characteristic.
- [x] `P2S-T0002`: finite four-suspension iteration preserves Euler characteristic.
- [x] `P2S-T0003`: finite four-suspension counts are two double-suspension steps.
- [x] `P2S-T0004`: finite eight-suspension counts are two four-suspension steps.
- [x] `P2S-T0005`: finite eight-suspension iteration preserves Euler characteristic.
- [x] `P2B-T0001`: finite period-8 dimension clock index is below 8.
- [x] `P2B-T0002`: finite period-8 dimension clock is invariant under adding 8.
- [x] `P2B-T0003`: finite period-8 dimension clock sends zero to zero.
- [x] `P2B-T0004`: finite period-8 dimension clock is invariant under any whole number of eight-step passes.
- [x] `P2BU-T0001`: trivial-bundle projection returns the base coordinate.
- [x] `P2BU-T0002`: trivial-bundle fiber coordinate returns the fiber value.
- [x] `P2BU-T0003`: trivial-bundle projection is invariant under changing only the fiber.
- [x] `P2BU-T0004`: trivial-bundle fiber coordinate is invariant under changing only the base.
- [x] `P2BU-T0005`: base-preserving bundle transitions do not change projection.
- [x] `P2BU-T0006`: bundle transitions apply their fiber map to the fiber coordinate.
- [x] `P2BU-T0007`: bundle transition composition agrees with sequential application.
- [x] `P2BU-T0008`: identity bundle transition leaves every trivial-bundle point unchanged.
- [x] `P2BU-T0009`: composing a bundle transition with identity on either side acts like the original transition on points.
- [x] `P2BC-T0001`: point-boundary after interval-boundary is zero in the directed-interval seed.
- [x] `P2BC-T0002`: reversing a directed interval negates its boundary.
- [x] `P2BC-T0003`: reversing a directed interval twice returns it.
- [x] `P2BC-T0004`: a constant directed interval has zero boundary.
- [x] `P2BC-T0005`: a directed interval boundary splits additively through an intermediate point.
- [x] `P2G-T0001`: proof glyph certificate exposes its theorem id.
- [x] `P2G-T0002`: proof glyph certificate exposes its Lean declaration name.
- [x] `P2G-T0003`: proof glyph certificate exposes its glyph id.
- [x] `P2G-T0004`: valid proof glyphs resolve to finite theorem metadata with matching theorem id and Lean name.
- [x] `P2G-T0005`: matching theorem metadata constructs a valid proof glyph relation.
- [x] `P2G-T0006`: proof glyph validity is preserved when finite theorem metadata grows by one entry.
- [x] `APPD-T0001`: finite phase coordinate is bounded by a positive period.
- [x] `APPD-T0002`: finite phase coordinate closes after adding one full period.
- [x] `APPD-T0003`: finite phase coordinate at zero is zero.
- [x] `APPD-T0004`: finite phase coordinate closes after any whole number of full periods.
- [x] `APPD-T0005`: finite phase-coordinate normalization is idempotent.
- [x] `APPD-B0001`: exploratory known-period Python fixture compares coil closure ranking with an autocorrelation baseline.
- [x] `APPD-B0002`: exploratory clean/noisy/aliased/multi-period Python fixture reports coil closure, autocorrelation, and periodogram-style baselines.
- [x] `COMPC-T0001`: cyclic address is bounded by a positive circular buffer size.
- [x] `COMPC-T0002`: cyclic address is unchanged after adding one full buffer size.
- [x] `COMPC-T0003`: cyclic address at zero is zero.
- [x] `COMPC-T0004`: cyclic address is unchanged after any whole number of full buffer-size passes.
- [x] `COMPC-T0005`: cyclic address normalization is idempotent.
- [x] `COMPR-T0001`: direction-bin schedule is bounded by a positive bin count.
- [x] `COMPR-T0002`: direction-bin schedule closes after one full pass through the bins.
- [x] `COMPR-T0003`: direction-bin schedule at zero is zero.
- [x] `COMPR-T0004`: direction-bin schedule closes after any whole number of full bin passes.
- [x] `COMPR-T0005`: direction-bin schedule normalization is idempotent.
- [x] `COMPL-T0001`: stride address is bounded by a positive circular size.
- [x] `COMPL-T0002`: stride address closes after one full pass through the circular step horizon.
- [x] `COMPL-T0003`: zero step has zero stride address.
- [x] `COMPL-T0004`: zero stride has zero stride address.
- [x] `COMPL-T0005`: stride address closes after any whole number of full circular-size passes.
- [x] `COMPL-B0001`: exploratory CoilLayout validation/benchmark-grid fixture.
- [x] `COMPL-B0002`: exploratory periodic-boundary stencil validation fixture.
- [x] `COMPS-T0001`: round-robin slot schedule is bounded by a positive slot count.
- [x] `COMPS-T0002`: round-robin slot schedule closes after one full pass through the slots.
- [x] `COMPS-T0003`: round-robin slot schedule at zero is zero.
- [x] `COMPS-T0004`: round-robin slot schedule closes after any whole number of full passes.
- [x] `AIA-T0001`: AI phase channel is bounded by a positive period.
- [x] `AIA-T0002`: AI phase channel closes after one full period.
- [x] `AIA-T0003`: AI phase channel at zero is zero.
- [x] `AIA-T0004`: AI phase channel closes after any whole number of full periods.
- [x] `AIA-T0005`: AI phase-channel normalization is idempotent.
- [x] `AIA-B0001`: exploratory deterministic phase-channel benchmark fixture.
- [x] `AIA-B0002`: exploratory learned-baseline phase fixture with periodic and nonperiodic controls.
- [x] `AIM-T0001`: cyclic memory slot is bounded by a positive bank size.
- [x] `AIM-T0002`: cyclic memory slot closes after one full bank pass.
- [x] `AIM-T0003`: cyclic memory slot at zero is zero.
- [x] `AIM-T0004`: cyclic memory slot closes after any whole number of full bank passes.
- [x] `AIM-T0005`: cyclic memory-slot normalization is idempotent.
- [x] `AIM-B0001`: exploratory cyclic-memory benchmark fixture with baselines and a nonperiodic control.
- [x] `AIM-B0002`: exploratory coil-retrieval reachability fixture with baselines and a near-lag control.
- [x] `AIRA-T0001`: adapter block index is bounded by a positive block size.
- [x] `AIRA-T0002`: adapter block index closes after one full block pass.
- [x] `AIRA-T0003`: adapter block index at zero is zero.
- [x] `AIRA-T0004`: adapter block index closes after any whole number of full block passes.
- [x] `AIRA-T0005`: adapter-block normalization is idempotent.
- [x] `AIRA-B0001`: exploratory adapter-block benchmark fixture with baselines and a nonperiodic control.
- [x] `AIRA-B0002`: exploratory MultiCoil/RoPE-style positional fixture with baselines and a nonperiodic control.

## Current S1 Proof Status

Already proved and linked:

- [x] `CC-T0001`: rotation by zero
- [x] `CC-T0002`: rotation composition
- [x] `CC-T0003`: rotation inverse
- [x] `CC-T0056`: rotations are bijections
- [x] `CC-T0004`: closure condition
- [x] `CC-T0005`: period equals `n / gcd(n,k)`
- [x] `CC-T0006`: orbit decomposition count
- [x] `CC-T0055`: same orbit iff the node difference lies in the stride subgroup
- [x] `CC-T0059`: same-orbit natural representatives are congruent modulo `gcd(n,k)`
- [x] `CC-T0060`: gcd-congruent natural representatives lie in the same stride-orbit quotient
- [x] `CC-T0061`: same orbit iff natural representatives are congruent modulo `gcd(n,k)`
- [x] `CC-T0007`: prime full coil
- [x] `CC-T0054`: full coil iff coprime
- [x] `CC-T0008`: scaling invertible iff coprime
- [x] `CC-T0028`: scaling by zero collapses to zero
- [x] `CC-T0017`: scaling by one is identity
- [x] `CC-T0018`: scaling maps compose by multiplying scale factors
- [x] `CC-T0029`: congruent scale factors act identically
- [x] `CC-T0019`: scaling transports rotation stride
- [x] `CC-T0020`: scaling transports finite coil steps
- [x] `CC-T0031`: scaling a natural step index gives the matching coil step from zero
- [x] `CC-T0021`: nonzero scaling below a prime circle size is bijective
- [x] `CC-T0022`: scaling sends a divisor cofactor to zero
- [x] `CC-T0023`: scaling sends divisor cofactor multiples to zero
- [x] `CC-T0024`: scaling collapses addresses shifted by divisor cofactor multiples
- [x] `CC-T0025`: scaling maps a natural address to zero iff the modulus divides the scaled product
- [x] `CC-T0030`: scaling maps a natural address to zero iff the coil period divides that address
- [x] `CC-T0032`: scaling maps natural multiples of the coil period to zero
- [x] `CC-T0033`: scaling collapses addresses shifted by natural multiples of the coil period
- [x] `CC-T0034`: scaling a natural address equals scaling its residue modulo the coil period
- [x] `CC-T0035`: scaled natural addresses are equal iff they are congruent modulo the coil period
- [x] `CC-T0036`: scaling is injective on representatives below the coil period
- [x] `CC-T0037`: the scaled image of one period of representatives has cardinality equal to the coil period
- [x] `CC-T0038`: every scaled natural address lands in the period-representative image
- [x] `CC-T0039`: the full finite scaling image equals the period-representative image
- [x] `CC-T0040`: the full finite scaling image has cardinality equal to the coil period
- [x] `CC-T0041`: canonical scaling-kernel representatives are exactly the period multiples below `gcd(n,k)`
- [x] `CC-T0042`: the canonical scaling-kernel representative set has cardinality `gcd(n,k)`
- [x] `CC-T0043`: canonical scaling-fiber representatives are offset period multiples
- [x] `CC-T0044`: canonical scaling-fiber representative sets have cardinality `gcd(n,k)`
- [x] `CC-T0050`: the scaled zero fiber is the canonical kernel representative set
- [x] `CC-T0052`: canonical representative fibers are equal iff the scaled representatives are equal
- [x] `CC-T0053`: canonical representative fibers are equal iff representatives are congruent modulo the stride period
- [x] `CC-T0045`: natural representatives lie in the scaling kernel subgroup exactly when the stride period divides them
- [x] `CC-T0051`: the target fiber over a scaled representative is that representative's canonical fiber
- [x] `CC-T0046`: target fibers are empty for target nodes outside the scaling image
- [x] `CC-T0047`: target fibers over image nodes have cardinality `gcd(n,k)`
- [x] `CC-T0048`: scaling image cardinality times reachable target-fiber cardinality equals the circle size
- [x] `CC-T0049`: scaling image cardinality times kernel representative cardinality equals the circle size
- [x] `CC-T0026`: scaled natural addresses are equal iff their scaled products are congruent modulo the circle size
- [x] `CC-T0027`: coprime scaling reflects ordinary address congruence
- [x] `CC-T0057`: affine circle maps compose by affine modular arithmetic
- [x] `CC-T0058`: coprime affine circle maps are bijective
- [x] `CC-T0009`: unique winding/residue lift
- [x] `CC-T0010`: lifted addition decomposition
- [x] `CC-T0011`: lifted existence
- [x] `CC-T0012`: successor with carry
- [x] `CC-T0013`: lifted addition right zero identity
- [x] `CC-T0014`: lifted addition associativity at reconstructed-value level
- [x] `CC-T0015`: lifted addition left zero identity
- [x] `CC-T0016`: iterated lifted successor

Still planned:

- Scaling/factor refinements beyond the current `CC-T0058` affine spine: affine classification and additional factor-lattice/provenance links. Orbit packaging beyond the current `CC-T0061` gcd-congruence theorem remains a separate future refinement.

## Latest Application Handoff Queue

The 2026-06-05 compute handoff is preserved in `docs/PHASE2_AND_APPLICATIONS.md` and `circle_calculus_codex_handoff/source_logs/04_compute_applications_browser_note.md`. Keep these additions at the end of the roadmap so the proof-first dimensional work can continue without losing application context:

- [x] Preserve the disciplined rule: Circle Math helps compute only when the workload has real cyclic, periodic, angular, spherical, toroidal, rotational, circulant, ring-buffer, or fibered structure.
- [x] Record the strongest current prototype priorities: `CoilRay Sort`, `CoilLayout`, and `CoilNTT`.
- [x] Preserve the broader top-ten prototype queue: `CoilRay Sort`, `CoilSampler`, `CoilLayout`, `CoilStencil`, `CoilNTT`, `CoilHash`, `CoilMotion`, `CoilPRM`, `CoilCodec`, and `CoilANN`.
- [x] Preserve the `CoilIR` meta-application: dictionary-detected circular structure, Lean-proved rewrites, backend selection, and benchmark validation.
- [x] When application work resumes, start with small MLX/Mac-compatible benchmarks where possible; keep CUDA/NVIDIA references as external baselines or future portability notes. Current starters: `sidecars/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT/python/benchmark_coil_layout.py` validates a layout grid and times natural versus gcd-cycle circular-stride traversal on CPU and optionally MLX; `sidecars/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES/python/benchmark_phase_channel.py` scores a deterministic phase-channel fixture on CPU and optionally MLX.
- [x] Do not present ray tracing, GPU layout, stencil, NTT, hashing, robotics, codec, ANN, acquisition, CAM, torsion, detection, scheduler, or quantum ideas as proved until they have explicit models, manifests, sidecars, and checks. Current papers and manifests label these as benchmark/domain tracks unless a Lean theorem id and checked sidecar exist.

## Phase III: Circle Calculus Living Book

The 2026-06-05 Living Book handoff is preserved in `circle_calculus_codex_handoff/source_logs/05_living_book_browser_note.md`. The curated operating docs are:

- [x] `docs/LIVING_BOOK_POLICY.md`
- [x] `docs/LIVING_BOOK_ROADMAP.md`
- [x] `docs/LIVING_BOOK_WIDGETS.md`

Goal:
Build a Quarto-based interactive explainer website/e-textbook generated from the existing repository artifacts. The Living Book is the public-facing explanation layer: readers should be able to change parameters, watch circles/coils update, read theorem-linked explanations, and open the corresponding Lean, Python, manifest, dictionary, and paper sources.

Source-of-truth rule:
The Living Book is downstream of the formal project. The theorem manifests remain the source of truth for proof status, Lean remains the formal proof source, Python remains the executable reference/modeling layer, and widgets/diagrams remain intuition/exploration only.

Core proof-status rule:
No page, theorem box, widget caption, status badge, or chapter text may present a theorem as proved unless the theorem id is marked `proved` or `lean_proved` in the relevant manifest and resolves to a compiled Lean declaration with no forbidden proof shortcuts.

Architecture:

- [x] Create `site/` as a Quarto project with `_quarto.yml`, landing page, roadmap page, S1 chapters, higher-dimensional placeholders, application placeholders, CSS, components, widgets, and generated data.
- [x] Keep the first version static-site compatible for GitHub Pages. Do not require a live Python server for core interactivity.
- [x] Use Quarto `.qmd` files, static HTML/SVG/JavaScript widgets, Python data exporters, and generated JSON from manifests/dictionaries/papers.
- [x] Avoid React/Next/Svelte/Vue and other heavy frontend frameworks unless a future need is explicit and justified.
- [x] Do not implement Manim, TTS, narration, video rendering, or a long movie in this phase. Those are later optional media layers.

Required first milestone:

- [x] `site/` exists as a Quarto project.
- [x] `site/index.qmd` renders.
- [x] S1 chapters 01 through 04 exist:
  - `site/chapters/S1/01_finite_circles.qmd`
  - `site/chapters/S1/02_rotation_as_addition.qmd`
  - `site/chapters/S1/03_coils_orbits_closure.qmd`
  - `site/chapters/S1/04_period_gcd_prime_full_coils.qmd`
- [x] S1 widgets exist:
  - `finite_circle_rotator`
  - `rotation_composition`
  - `coil_orbit_explorer`
  - `period_gcd_visualizer`
  - `prime_full_coil_explorer`
- [x] `winding_lift_explorer` exists or is scaffolded with honest theorem status.
- [x] Generated data exists under `site/data/generated/`:
  - `theorem_manifest.json`
  - `dictionary.json`
  - `dimensions.json`
  - `paper_index.json`
  - `widget_index.json`
- [x] Theorem boxes and dictionary boxes display generated data rather than hand-copied proof status.
- [x] Status badges are generated from manifest status.
- [x] Higher dimensions and applications are scaffolded as placeholders without looking complete.
- [x] `sitecheck` passes.
- [x] `quarto render site` succeeds.
- [x] `lake build`, `python -m pytest`, manifest checks, and dictionary checks still pass.

Required first scripts:

- [x] `scripts/site/export_site_data.py`
- [x] `scripts/site/check_quarto_structure.py`
- [x] `scripts/site/check_site_manifest_links.py`
- [x] `scripts/site/check_site_dictionary_links.py`
- [x] `scripts/site/check_site_theorem_status.py`
- [x] `scripts/site/check_site_paper_links.py`
- [x] `scripts/site/check_widget_python_parity.py`

Required first tests:

- [x] `tests/site/test_export_site_data.py`
- [x] `tests/site/test_site_manifest_links.py`
- [x] `tests/site/test_site_dictionary_links.py`
- [x] `tests/site/test_site_theorem_status.py`
- [x] `tests/site/test_widget_python_parity.py`

Required Make targets once implementation begins:

- [x] `make site-data`
- [x] `make sitecheck`
- [x] `make site-render`
- [x] `make site-preview`
- [x] `make living-book-check`

Phase III guardrails:

- [x] v0 circles are finite cyclic address spaces, not Euclidean metric circles.
- [x] Diagrams are explanations, not proofs.
- [x] Python examples are executable references, not formal proofs.
- [x] Widgets are deterministic and browser-native for the S1 milestone.
- [x] Widgets do not fetch remote resources at runtime.
- [x] Widget math is minimal, auditable, and checked against Python reference behavior where practical.
- [x] The site must not duplicate theorem status or dictionary definitions manually when generated data can provide them.
- [x] Quarto/Lean Web/Jupyter integrations never replace local `lake build` as the formal verification command.

## Phase IV: Wide And Deep Theorem Discovery

Goal:
Expand coverage at every dimensional level by deliberately looking for missing theorems, stronger formal statements, cleaner proof spines, better sidecars, and paper improvements. This phase is not a license to invent unsupported claims; it is a structured audit for what the project should prove next and for where existing papers or proofs should be strengthened.

Coverage standard:
Go wide across every dimensional layer and application family, then go deep wherever the audit finds a real proof spine, reusable lemma, dictionary concept, or paper improvement. A successful Phase IV pass should leave the project with broader theorem coverage, stronger local proofs, and clearer paper/proof links, not just a longer wishlist.

Required sweep:

- [ ] Audit `S0` for sign, opposition, involution, parity, and antipodal vocabulary that should be made explicit.
- [ ] Audit `S1` for additional finite cyclic-group, rotation, coil, winding, scaling, factor, fiber, quotient, and normal-form theorems.
- [ ] Audit `S2` for suspended-circle, sphere-grid, pole/equator, latitude/longitude, antipode, axis, cell-count, and inherited-coil theorem gaps.
- [ ] Audit `S3` for finite hypersphere, quaternion algebra, unit-quaternion, Hopf-coordinate, phase-action, spin, and quotient-warning theorem gaps.
- [ ] Audit `S4-S6` for suspension/Euler parity, quaternionic Hopf base, complex projective bridge, octonion-shadow, and warning theorem gaps.
- [ ] Audit `S7` and `S15` for topological suspension, quaternionic Hopf, octonionic algebra, nonassociativity, future horizon, and non-overclaim theorem gaps.
- [ ] Audit Phase II and applications for stable-sphere, Bott/Clifford seed, bundle, boundary/cobordism, proof-glyph, data-analysis, compute, rendering, systems, and AI theorem gaps.
- [ ] For each promising theorem target, add or update a manifest entry before claiming it in prose.
- [ ] Prove low-risk targets in Lean first, then update paper text, Python sidecars, theorem cards, and Living Book links.
- [ ] Revisit existing proved claims for stronger variants, cleaner names, better lemmas, or more useful corollaries before moving to speculative terrain.
- [ ] Improve papers or proof sidecars when the audit shows a claim is correct but underexplained, weakly linked, or hard for a reader to consume.
- [ ] Record blocked or long-horizon targets as `blocked`, `deferred`, `planned`, `lean_stated`, or `exploratory_python` with a useful blocker or next-step note.
- [ ] Keep lower dimensions independent of higher dimensions.

Outputs:

- [x] A broader theorem target list represented in manifests, not a loose report.
- [ ] Improved paper sections where proofs already exist or where planned status needs clearer wording.
- [ ] Additional Lean sidecars and Python parity examples where they strengthen the formal spine.
- [ ] Updated dictionary terms for recurring vocabulary discovered during the sweep.
- [x] Updated Living Book pages or index data when new proved or planned theorem ids land.

Completion criteria:

- [ ] Each dimension and application folder has been inspected for missing theorem/paper/proof opportunities.
- [ ] Every accepted new target has a manifest entry and an honest status.
- [ ] No speculative target is presented as proved.
- [ ] `make check` and relevant Living Book checks pass.

## Phase V: Edge Problem-Space Search

Goal:
Search for problem spaces near the edge of the project where Circle Calculus may offer leverage that is difficult, awkward, or unavailable in ordinary presentations. The standard is not hype; the standard is whether the circle/provenance/glyph/proof-carrying organization produces a concrete artifact, explanation, compression, benchmark, search improvement, or formal interface that would be hard to get otherwise.

Search standard:
Look for tasks where ordinary mathematical presentation is correct but awkward, fragmented, hard to navigate, hard to certify visually, or hard to operationalize. Circle Calculus earns a Phase V claim only when it produces a concrete advantage: a better proof interface, a cleaner executable model, a more navigable provenance object, a stronger benchmark fixture, or a clearer reader workflow.

Source of truth:

- `manifests/phase5_edge_targets.yaml`
- `docs/PHASE5_EDGE_TARGETS.md`
- `scripts/check_phase5_targets.py`

Search areas:

- [ ] Proof-carrying diagrams and glyphs: can diagrams compile to theorem ids, Lean declarations, and checked status without drifting?
- [ ] Proof search and theorem discovery: can coil/glyph normal forms expose useful theorem candidates or reduce search friction in bounded domains?
- [ ] Number provenance and symbolic compression: can first-class construction histories improve explanation, simplification, proof compression, or theorem navigation?
- [ ] Cyclic and periodic data analysis: can coil signatures, closure profiles, prime-lag scans, and period lattices add value beyond standard baselines?
- [ ] AI/ML inductive bias: can phase channels, cyclic memory, coil/sparse attention, MultiCoil RoPE, adapter scheduling, recurrent/state-space/convolutional sequence models, harmonic/circulant features, geometry-aware representations, or proof-carrying model components create measurable gains on tasks with real periodic, rotational, memory-like, or fibered structure?
- [ ] Compute and rendering: can circular layouts, stride scheduling, sampling, stencils, or NTT-like structures improve locality, explainability, or verification?
- [ ] Robotics/orientation and physics-adjacent models: can quaternion/Hopf/fiber language make orientation, phase ambiguity, gauge-like redundancy, or spin easier to verify or debug?
- [ ] Education and public understanding: can the Living Book make formal cyclic and dimensional ideas easier to learn without weakening rigor?

Required discipline:

- [ ] Define a baseline before claiming an improvement.
- [ ] Separate mathematical proof, executable example, benchmark, and speculative interpretation.
- [ ] Use MLX/Mac-first language for local AI/compute work; CUDA references remain portability or external-baseline notes.
- [ ] Add papers, sidecars, or application manifests only when the experiment or theorem target is concrete enough to track.
- [ ] Keep a clear comparison to ordinary mathematical notation, software, or proof workflow so any claimed advantage is visible rather than assumed.
- [ ] Reject or defer directions that become metaphor-only.

Outputs:

- [x] A short list of concrete edge experiments with acceptance criteria.
- [x] `P5-EDGE-001`: generated glyph-status fixture resolves theorem and dictionary data without upgrading unproved theorem status.
- [x] `P5-EDGE-002`: finite-coil theorem-signature index normalizes gcd, period, orbit count, full-coil, and same-orbit tags for bounded S1 proof navigation.
- [x] `P5-EDGE-003`: number provenance fixture records divisor, cofactor, orbit-count, period, and theorem-link views for selected finite circles.
- [x] `P5-EDGE-004`: expanded deterministic periodic-data fixture suite records clean, noisy, aliased, and multi-period baseline behavior without upgrading usefulness claims.
- [x] `P5-EDGE-005`: learned phase-channel baseline fixture records both a positive periodic case and a negative nonperiodic control.
- [x] `P5-EDGE-006`: periodic-boundary stencil validation fixture checks direct, dense, and gcd-cycle traversal outputs before backend or speed claims.
- [x] `P5-EDGE-007`: orientation-debugging note records q/-q sign ambiguity against existing S3 spin theorem ids without claiming full SO(3) or robotics verification.
- [x] `P5-EDGE-008`: Living Book reader path links dimensions, applications, theorem status, dictionary entries, source trails, and local verification commands.
- [x] `P5-EDGE-009`: full-spectrum Circle AI program target separates proof targets, benchmarks, baselines, controls, model prototypes, and speculative hypotheses; `AIM-B0002` extends the starter fixtures to coil-retrieval reachability, `AIRA-B0001` extends them to adapter-block structure, and `AIRA-B0002` extends them to MultiCoil/RoPE-style positional structure.
- [ ] At least one experiment-ready paper or application note for each accepted edge direction.
- [ ] Python/MLX or other executable sidecars where the claim is computational.
- [ ] Lean theorem targets where the claim is formal.
- [x] Living Book target index generated downstream of manifests and source artifacts.

## Phase VI: Global Correctness, Clarity, And Polish Sweep

Goal:
Make the entire project cleaner, more correct, easier to consume, and harder to misread. This is the final wide sweep over writing, proofs, manifests, dictionary entries, site pages, examples, links, and repository ergonomics.

Source of truth:

- `manifests/phase6_sweep_targets.yaml`
- `scripts/check_phase6_sweep_targets.py`

Polish standard:
The final pass should optimize for correct wide and deep coverage. Every reader-facing claim should be either proved, explicitly planned, exploratory, blocked, deferred, or background. Every public entry point should sound cleaner, point to the right source of truth, and make it easy for a new reader to understand what has been proved and what remains future work.

Sweep checklist:

- [ ] Re-read every paper for overclaims, missing theorem ids, unclear status language, duplicated definitions, and weak exposition.
- [ ] Improve prose that sounds rough, vague, or too speculative, while preserving exact theorem status.
- [ ] Re-run every theorem manifest against Lean declarations and paper references.
- [ ] Re-run every dictionary entry against actual usage in papers, Lean, Python, and the Living Book.
- [ ] Check every sidecar for stale examples, missing tests, weak names, and mismatch with paper claims.
- [ ] Check every Living Book page for status drift, broken generated data, stale source links, mobile readability, and widget correctness.
- [ ] Check README, roadmap, GitHub Pages docs, and policy docs for actual current state.
- [ ] Remove transient caches, reports, and generated clutter from git while keeping durable source and generated data that the repo intentionally tracks.
- [ ] Run `make check`, `make living-book-check`, and `quarto render site`.
- [ ] Inspect GitHub CI once before each push and fix known failures before sending the next batch.

Completion criteria:

- [ ] No known paper theorem claim lacks a theorem id or explicit non-proof label.
- [ ] No manifest-proved theorem lacks a compiled Lean declaration.
- [ ] No Living Book theorem card or widget caption upgrades status beyond the manifest.
- [ ] No major broken links remain in README, papers, docs, or site pages.
- [ ] The public repo can be consumed by a new reader through README, papers, theorem index, dictionary index, and Living Book without needing hidden context.

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

- [x] previous GitHub CI result inspected once, with any known failure fixed in this commit
- [x] `lake build`
- [x] Lean sidecars compile
- [x] Python tests pass
- [x] theorem manifest validates
- [x] dictionary validates
- [x] paper manifest validates
- [x] paper theorem links validate
- [x] no fake proof markers
- [x] dimension checks pass if present
- [x] `README.md` describes current state
- [x] no transient reports, caches, build artifacts, or local secrets are staged

## Wake-Up State

If the whole corpus is not finished by the time work pauses, the repo should still be in a useful wake-up state:

- `make check` passes, or the exact failing command is known.
- This roadmap reflects completed, pending, and blocked work.
- Manifest statuses are honest.
- Papers do not claim planned/blocked theorems are proved.
- The README points to the current stage.
- The public GitHub repo has the latest clean commit pushed when appropriate.
