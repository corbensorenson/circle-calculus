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

README state rule:
After meaningful proof batches, paper batches, roadmap changes, or application-context additions, update `README.md` so it reflects the actual current state, proof status, usage pointers, and where to find the relevant docs. Do not churn the README for tiny internal-only edits.

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

- [x] `papers/S1/PAPER_S1_01_FINITE_CIRCLES.md`
  - Current source: `papers/PAPER_01_FINITE_CIRCLES.md`
  - Proof targets: `CC-T0001` through `CC-T0007`
  - Status: proved theorem spine exists; paper should be polished and relocated or linked through the dimension layout.
- [x] `papers/S1/PAPER_S1_02_WINDING_NATURALS.md`
  - Current source: `papers/PAPER_02_WINDING_NATURALS.md`
  - Proof targets: `CC-T0009` through `CC-T0016`
  - Status: proved theorem spine exists; paper should be polished and relocated or linked through the dimension layout.
- [x] `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md`
  - Proof targets: oriented winding, signed residues, integer addition, additive inverse, reversible motion.
  - Status: signed zero, composition, and inverse motion are Lean-proved as `S1O-T0001` through `S1O-T0003`.
- [x] `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md`
  - Proof targets: `CC-T0008`, multiplication as repeated rotation/scaling, invertibility iff coprime, factor structure, prime/full-coil refinements.
  - Status: scaling invertible iff coprime, scale-by-zero collapse, scale-by-one identity, scaling composition, scale-factor congruence normalization, scaling transport of rotation stride, scaling transport of finite coil steps, scaling natural steps into coil traversal, prime-circle scaling bijectivity, divisor-cofactor collapse, cofactor-multiple collapse, cofactor-shift address collapse, scaling-zero divisibility, period-level kernel divisibility, period-multiple collapse, period-shift collapse, period-normal representatives, period-congruence scaled equality, scaled-address product congruence, and coprime scaling reflection are Lean-proved as `CC-T0008`, `CC-T0028`, `CC-T0017`, `CC-T0018`, `CC-T0029`, `CC-T0019`, `CC-T0020`, `CC-T0031`, `CC-T0021`, `CC-T0022`, `CC-T0023`, `CC-T0024`, `CC-T0025`, `CC-T0030`, `CC-T0032`, `CC-T0033`, `CC-T0034`, `CC-T0035`, `CC-T0026`, and `CC-T0027`; deeper factor/orbit refinements remain future extensions.

### S0: Opposition And Sign

- [x] `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md`
  - Proof targets: `S0-T0001`, `S0-T0002`
  - Status: both finite opposition facts are Lean-proved in `Circle/S0/Scaffold.lean`.
  - Warning target: `S0-W0001`, `C_1` is not `S^0`.

### S2: Sphere Calculus

- [x] `papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md`
  - Proof targets: `S2-T0001`, `S2-T0002`
  - Status: suspended-circle counts and Euler characteristic are Lean-proved in `Circle/S2/Scaffold.lean`.
  - Main model: `SuspC(n)`, with `V=n+2`, `E=3n`, `F=2n`, `chi=2`.
- [x] `papers/S2/PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md`
  - Proof targets: `S2-T0003` through `S2-T0007`
  - Status: sphere-grid counts, Euler characteristic, latitude-ring model, pole-fixing rotation, and inherited latitude coil period are Lean-proved.
  - Warning targets: `S2-W0001`, `S2-W0002`, `S2-W0003`
  - Main model: `SphereGrid(n,r)`, with pole collapse and latitude rings.
- [x] `papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md`
  - Proof targets to add as the model matures: antipodal map, axis, meridians, surface closure, antinodes.
  - Do not force continuous geometry too early.
  - Status: suspended-circle antipode pole swap and involution are Lean-proved; meridians and antinodes remain future refinements.

### S3: Hypersphere, Quaternions, Hopf

- [x] `papers/S3/PAPER_S3_01_FINITE_HYPERSPHERES.md`
  - Proof targets: `S3C-T0001` through `S3C-T0004`
  - Main model: suspension of finite 2D cell-count structures.
  - Status: suspended-surface counts, Euler-zero theorem, suspended-suspended-circle counts, and Euler characteristic are Lean-proved.
- [x] `papers/S3/PAPER_S3_02_QUATERNION_COILS.md`
  - Proof targets: `S3Q-T0001` through `S3Q-T0005`
  - Prefer mathlib quaternion support when available.
  - Status: real quaternion norm, unit closure, conjugate inverse equations, noncommutative example, and associativity are Lean-proved.
- [x] `papers/S3/PAPER_S3_03_HOPF_COILS.md`
  - Proof/model targets: `S3H-T0001` through `S3H-T0003`
  - Warning target: `S3H-W0001`, not globally `S^2 x S^1`
  - Start with Python numeric models if Lean analysis support is too heavy.
  - Status: `S3H-T0001` through `S3H-T0003` are Lean-proved bounded Hopf coordinate facts; analytic circle parameterization, quotient topology, and global fibration formalization remain future work.
- [x] `papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md`
  - Proof target: `S3S-T0001`
  - Status: quaternion conjugation action is Lean-proved invariant under replacing `q` by `-q`; full `SO(3)` quotient remains future work.

### S4-S6: Geometric Bridge

- [x] `papers/S4_S6/PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md`
  - Proof target: `S456-T0001`
  - Main result: `chi(S^d)=1+(-1)^d` for finite iterated suspension models.
- [x] `papers/S4_S6/PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md`
  - Proof target: `S4-T0001`
  - Roadmap target: role of `S^4` as base of `S^3 -> S^7 -> S^4`.
- [x] `papers/S4_S6/PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md`
  - Proof target: `S5-T0001`
  - Keep projective geometry exploratory unless formalized.
- [x] `papers/S4_S6/PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md`
  - Proof target: `S6-T0001`
  - Warning target: `S6-W0001`
  - Status: S4/S5/S6 finite suspension Euler characteristics are Lean-proved; projective, quaternionic Hopf, and S6 complex-structure topics remain roadmap/warning material.

### S7: Topological, Quaternionic Hopf, Octonionic

- [x] `papers/S7/PAPER_S7_01_TOPOLOGICAL_7SPHERE.md`
  - Proof targets: `S7C-T0001`, `S7C-T0002`
  - Prove topological/combinatorial `S7` before octonion algebra.
  - Status: finite iterated-suspension model and Euler characteristic are Lean-proved.
- [x] `papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md`
  - Targets: `S7QH-T0001`, `S7QH-T0002`
  - Keep roadmap/exploratory until `S3` quaternion calculus and `S4` base are stable.
  - Status: `S7QH-T0001` and `S7QH-T0002` are Lean-proved coordinate theorems; quaternionic projective space, quotient topology, and full fibration formalization remain future work.
- [x] `papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md`
  - Targets: `S7O-T0001` through `S7O-T0006`
  - Warning targets: `S7O-W0001`, `S7O-W0002`
  - Unit octonions are not a group.
  - Status: `S7O-T0001` through `S7O-T0006` are Lean-proved in a bounded Cayley-Dickson coordinate model; higher octonion library design and octonionic Hopf formalization remain future work.

### Future S15

- [x] `papers/future/S15/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md`
  - Future targets: `S15-T0001` through `S15-T0003`
  - Do not claim the full octonionic Hopf fibration before quotient topology and phase action are formalized.
  - Status: `S15-T0001` is a Lean roadmap marker; `S15-T0002` and `S15-T0003` are Lean-proved; full fibration topology remains future work.

### Phase II: Structured Transformations After S15

This section records deferred and active Phase II work from the browser handoffs. The detailed context lives in `docs/PHASE2_AND_APPLICATIONS.md`; proof status still comes only from Lean-linked theorem ids and manifests.

Guardrail: after `S^15`, do not invent a false classical Hopf/division-algebra continuation such as `S^15 -> S^31 -> S^16`. Higher spheres should move into general suspension, stable homotopy, or spectrum machinery instead.

- [x] `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md`
  - Program: suspension, stable maps, spectra, and stable invariants.
  - Status: `P2S-T0001` and `P2S-T0002` are Lean-proved finite double/four suspension Euler facts; stable maps, spectra, and stable homotopy claims remain future work.
- [x] `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md`
  - Program: Clifford algebras, spinors, Bott periodicity, and dimension clocks.
  - Status: `P2B-T0001` and `P2B-T0002` are Lean-proved finite period-8 clock facts; Clifford algebras, K-theory, KO-theory, and Bott periodicity remain future formalization work.
- [x] `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md`
  - Program: base, fiber, total space, projection, transition functions, connection, curvature, holonomy, and hidden proof provenance.
  - Status: `P2BU-T0001` through `P2BU-T0003` are Lean-proved trivial product-bundle projection/fiber facts; nontrivial bundles, transition functions, connections, curvature, and holonomy remain future work.
- [x] `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md`
  - Program: boundaries, `boundary(boundary)=0`, cobordisms, fields, and proofs as transformations.
  - Status: `P2BC-T0001` and `P2BC-T0002` are Lean-proved directed-interval boundary facts; general chain complexes, cobordisms, TQFT, and physics-adjacent claims remain future work.
- [x] `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md`
  - Program: glyphs with formal syntax, normal forms, theorem dependencies, proof certificates, semantic models, and projection views.
  - Status: `P2G-T0001` and `P2G-T0002` are Lean-proved proof-glyph certificate projection facts; glyph syntax, normal forms, semantics, dependency correctness, and proof search remain future work.
- [x] `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md`
  - Program: coil signatures, closure profiles, prime-lag recurrence, antinode maps, and periodic-data benchmarks.
  - Status: `APPD-T0001` and `APPD-T0002` are Lean-proved finite phase-coordinate facts with Python examples; real-data and benchmark claims remain future work.
- [x] `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md`
  - Program: certified cyclic/circulant/orbit structure lowered to FFT/NTT/permutation backends and benchmarked.
  - Status: `COMPC-T0001` and `COMPC-T0002` are Lean-proved cyclic-address facts with Python examples; backend lowering and performance claims remain benchmark work.
- [x] `papers/applications/PAPER_COMP_02_COIL_RAY_AND_SAMPLING.md`
  - Program: `CoilRay Sort`, `CoilSampler`, `CoilNoise`, `CoilSTIR`, BRDF/lighting angular compression, spherical-coil ray queues, procedural placement/dithering, and rendering benchmarks.
  - Status: `COMPR-T0001` and `COMPR-T0002` are Lean-proved direction-bin schedule facts with Python examples; rendering performance, coherence, and sampling-quality claims remain benchmark work.
- [x] `papers/applications/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT.md`
  - Program: `CoilLayout`, `CoilStencil`, `CoilNTT`, gcd-cycle memory layouts, verified periodic boundaries, exact finite transforms, and MLX/Mac-compatible prototypes where relevant.
  - Status: `COMPL-T0001` and `COMPL-T0002` are Lean-proved stride-address facts with Python examples; layout, stencil, FFT, NTT, MLX/backend, and performance claims remain future work.
- [x] `papers/applications/PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS.md`
  - Program: `CoilHash`, `CoilMotion`, `CoilPRM`, `CoilCodec`, `CoilANN`, `CoilAcquire`, `CoilCAM`, `CoilTorsion`, `CoilDetect`, `CoilSched`, and `CoilQ` as benchmarked or domain-tested application roadmaps.
  - Status: `COMPS-T0001` and `COMPS-T0002` are Lean-proved round-robin schedule facts with Python examples; fairness, load balancing, robotics, codec, ANN, acquisition, CAM, torsion, detection, and quantum claims remain future domain work.
- [x] `papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md`
  - Program: disciplined Circle AI thesis covering phase, recurrence, rotation, sparse cyclic mixing, circular memory, harmonic transforms, geometry-aware models, and proof-carrying model components.
  - Status: `AIA-T0001` and `AIA-T0002` are Lean-proved phase-channel facts with Python examples; model-quality and speed claims remain benchmark work.
- [x] `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`
  - Program: Coil Attention, CoilKV, long-context retrieval, alias control, stride/orbit coverage, and comparisons against full attention, sparse attention, Hyena-like mixers, and S4/Mamba-like baselines.
  - Status: `AIM-T0001` and `AIM-T0002` are Lean-proved cyclic-memory-slot facts with Python examples; retrieval quality, alias control, and attention replacement claims remain benchmark work.
- [x] `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md`
  - Program: CoilLinear, CoilRA, MultiCoil RoPE, periodic activations, and MLX-first benchmarks against dense, LoRA, block-circulant, and standard RoPE baselines.
  - Status: `AIRA-T0001` and `AIRA-T0002` are Lean-proved adapter-block facts with Python examples; CoilRA, MultiCoil RoPE, model quality, parameter efficiency, and runtime claims remain benchmark work.

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
- [x] `P2S-T0001`: finite double suspension preserves Euler characteristic.
- [x] `P2S-T0002`: finite four-suspension iteration preserves Euler characteristic.
- [x] `P2B-T0001`: finite period-8 dimension clock index is below 8.
- [x] `P2B-T0002`: finite period-8 dimension clock is invariant under adding 8.
- [x] `P2BU-T0001`: trivial-bundle projection returns the base coordinate.
- [x] `P2BU-T0002`: trivial-bundle fiber coordinate returns the fiber value.
- [x] `P2BU-T0003`: trivial-bundle projection is invariant under changing only the fiber.
- [x] `P2BC-T0001`: point-boundary after interval-boundary is zero in the directed-interval seed.
- [x] `P2BC-T0002`: reversing a directed interval negates its boundary.
- [x] `P2G-T0001`: proof glyph certificate exposes its theorem id.
- [x] `P2G-T0002`: proof glyph certificate exposes its Lean declaration name.
- [x] `APPD-T0001`: finite phase coordinate is bounded by a positive period.
- [x] `APPD-T0002`: finite phase coordinate closes after adding one full period.
- [x] `COMPC-T0001`: cyclic address is bounded by a positive circular buffer size.
- [x] `COMPC-T0002`: cyclic address is unchanged after adding one full buffer size.
- [x] `COMPR-T0001`: direction-bin schedule is bounded by a positive bin count.
- [x] `COMPR-T0002`: direction-bin schedule closes after one full pass through the bins.
- [x] `COMPL-T0001`: stride address is bounded by a positive circular size.
- [x] `COMPL-T0002`: stride address closes after one full pass through the circular step horizon.
- [x] `COMPS-T0001`: round-robin slot schedule is bounded by a positive slot count.
- [x] `COMPS-T0002`: round-robin slot schedule closes after one full pass through the slots.
- [x] `AIA-T0001`: AI phase channel is bounded by a positive period.
- [x] `AIA-T0002`: AI phase channel closes after one full period.
- [x] `AIM-T0001`: cyclic memory slot is bounded by a positive bank size.
- [x] `AIM-T0002`: cyclic memory slot closes after one full bank pass.
- [x] `AIRA-T0001`: adapter block index is bounded by a positive block size.
- [x] `AIRA-T0002`: adapter block index closes after one full block pass.

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
- [x] `CC-T0026`: scaled natural addresses are equal iff their scaled products are congruent modulo the circle size
- [x] `CC-T0027`: coprime scaling reflects ordinary address congruence
- [x] `CC-T0009`: unique winding/residue lift
- [x] `CC-T0010`: lifted addition decomposition
- [x] `CC-T0011`: lifted existence
- [x] `CC-T0012`: successor with carry
- [x] `CC-T0013`: lifted addition right zero identity
- [x] `CC-T0014`: lifted addition associativity at reconstructed-value level
- [x] `CC-T0015`: lifted addition left zero identity
- [x] `CC-T0016`: iterated lifted successor

Still planned:

- Scaling/factor refinements beyond `CC-T0035`: kernel cardinality, image size, composite orbit refinements, and factor-lattice/provenance links.

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
