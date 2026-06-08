# Circle Calculus

**Start learning here:** [Circle Calculus Living Book](https://corbensorenson.github.io/circle-calculus/) is the public interactive textbook for the project.

Circle Calculus is a staged paper-and-proof corpus for rebuilding familiar mathematical structures from finite circular address spaces, rotations, coils, winding, lifted arithmetic, and eventually a dimension-indexed sphere ladder.

## Living Book

The Living Book is being organized as a guided textbook first and a reference index second: readers start with a front-of-book mathematical toolkit, then finite addresses, rotation, coils, closure, period, primes, winding, dimensions, and applications. It connects explanations, diagrams/widgets, checkpoint questions, dictionary entries, theorem status, papers, Python reference models, and Lean source links so readers can learn the project without losing the proof-status trail.

The long-term aim is not just to write essays. The aim is to keep every serious concept tied to:

- a human-readable paper in `papers/`,
- Lean 4/mathlib declarations in `Circle/` and paper-specific Lean sidecars in `sidecars/`,
- executable Python reference models in `circle_math/`,
- shared dictionary files under `dictionary/`, and
- theorem metadata in `manifests/theorem_manifest.yaml`.

The Phase IV wide/deep theorem-target audit is tracked in `manifests/phase4_theorem_targets.yaml` and validated by `scripts/check_phase4_targets.py`, including required layer coverage and promoted/supporting theorem references. Phase V edge problem-space targets are tracked in `manifests/phase5_edge_targets.yaml`, explained in `docs/PHASE5_EDGE_TARGETS.md`, and validated by `scripts/check_phase5_targets.py`. Phase VI global sweep targets are tracked in `manifests/phase6_sweep_targets.yaml` and validated by `scripts/check_phase6_sweep_targets.py`. Phase VII physics/generator targets are tracked in `manifests/phase7_physics_generators.yaml`, explained in `docs/PHASE7_PHYSICS_AND_GENERATORS.md`, and validated by `scripts/check_phase7_targets.py`; application benchmark and edge-claim guardrails are additionally checked by `scripts/check_application_guardrails.py`.

The rule is simple: papers are allowed to be ambitious, but claimed theorems must be traceable.

## What This Project Aims To Prove

The project starts from the finite cyclic address space `C_n`, modeled in Lean as `ZMod n`, and builds upward in stages.

Current focus:

- finite marked circles and nodes,
- rotations as addition in `C_n`,
- coils as repeated rotations,
- closure and period,
- orbit decomposition,
- full-coil iff coprime and prime full-coil behavior,
- lifted winding/residue coordinates, and
- natural-number addition and successor as lifted circular motion with carry.

Planned later stages include oriented winding for integers, multiplication and scaling, factor structure, geometry, analysis-flavored limits, higher spheres, and a careful foundations layer. Those later stages are not claimed as proved until their theorem manifest entries, Lean declarations, and checks exist.

## Dimensional Roadmap

The expanded long-horizon plan is dimension-organized:

```text
S^0 -> S^1 -> S^2 -> S^3 -> S^4/S^5/S^6 -> S^7 -> Future/S^15
```

The current proved layer includes `S^1` finite circles, rotations, coils, period, orbit decomposition, same-orbit quotient membership, prime full coils, full-coil iff coprime, winding, lifted natural-number arithmetic, scaling invertibility, scale-factor normalization, scaling-to-coil image bridge, prime-circle scaling, divisor/cofactor scaling collapse, period-kernel collapse, period-normal scaling representatives, period-congruence scaled equality, bounded period-representative injectivity, period-representative image cardinality and membership, whole-circle scaling image equality and cardinality, canonical kernel/fiber representative equality and cardinality, zero-fiber/kernel and scaled-target/fiber bridges, fiber-set equality modulo scaled value and stride period, arbitrary target-fiber emptiness/cardinality, image-times-fiber and image-times-kernel scaling factorizations, kernel-subgroup membership, cofactor-shift collapse, exact scaling-zero and period-divisibility criteria, scaled-address equality congruence, coprime scaling reflection, and signed reversible rotation; `S^0` two-point opposition; common finite-cell suspension/Euler machinery; the first `S^2` suspended-circle, sphere-grid, antipode, pole/equator subset, latitude/longitude coordinate, and antipodal-pair theorem spine; the finite combinatorial `S^3` suspension theorem spine; the core `S^3` real-quaternion algebra spine; the first `S^3` Hopf coordinate and phase-action spine; the first `S^3` spin sign-cancellation and pure-vector preservation theorems; the finite `S^4` through `S^6` suspension-count and Euler bridge; the finite topological `S^7` suspension-count and Euler model; the first Phase II finite stable-sphere, period-8 clock, trivial-bundle, directed-boundary, and proof-glyph certificate seeds; and the first application finite phase-coordinate, cyclic-address, direction-bin, stride-address, round-robin schedule, and Circle AI indexing seeds.

Future dimensional work is split into two related ladders:

- Geometric ladder: `S^0`, `S^1`, `S^2`, `S^3`, `S^4`, `S^5`, `S^6`, `S^7`.
- Algebraic ladder: `S^0` signs, `S^1` unit complex phase, `S^3` unit quaternions, `S^7` unit octonions.

The repository rule for that expansion is strict: higher dimensions may depend on lower dimensions, but lower dimensions must not import or rely on higher dimensions. The first dimensional implementation stage should be scaffolding only: dimension manifests, dictionary files, paper folders, Lean/Python roots, and import-check scripts, with all future theorem statuses kept planned, deferred, or exploratory until proofs exist.

See `docs/COMPLETION_ROADMAP.md`, `docs/DIMENSIONAL_LADDER.md`, `docs/PHASE2_AND_APPLICATIONS.md`, `docs/GITHUB_PAGES.md`, and `circle_calculus_dimensional_handoff/` for the detailed roadmap and guardrails.

## Current Status

This is an early public research scaffold with a working verification pipeline and a growing dimension-indexed theorem spine.

| Paper | Status | Formal spine |
| --- | --- | --- |
| `papers/PAPER_01_FINITE_CIRCLES.md` | polished draft | `CC-T0001` through `CC-T0007` plus `CC-T0054`, `CC-T0055`, and `CC-T0059` through `CC-T0061` proved; `P5-EDGE-002` adds an exploratory finite-coil theorem-signature index |
| `papers/PAPER_02_WINDING_NATURALS.md` | polished draft | `CC-T0009` through `CC-T0016` proved |
| `papers/S1/PAPER_S1_01_FINITE_CIRCLES.md` | polished dimension guide draft | `CC-T0001` through `CC-T0007` plus `CC-T0054`, `CC-T0055`, and `CC-T0059` through `CC-T0061` linked in dimension layout |
| `papers/S1/PAPER_S1_02_WINDING_NATURALS.md` | polished dimension guide draft | `CC-T0009` through `CC-T0016` linked in dimension layout |
| `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md` | polished draft | `S1O-T0001` through `S1O-T0004` proved with Python examples |
| `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md` | polished draft | `CC-T0008`, `CC-T0017` through `CC-T0054`, and `CC-T0056` through `CC-T0058` proved; linked to finite-coil signature and number-provenance fixtures |
| `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md` | polished draft | `S0-T0001` through `S0-T0005` proved with Python examples |
| `papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md` | polished draft | `S2-T0001` and `S2-T0002` proved with Python examples |
| `papers/S2/PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md` | polished draft | `S2-T0003` through `S2-T0007` and `S2-T0017` proved with Python examples |
| `papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md` | polished draft | `S2-T0008` through `S2-T0016` plus `S2-T0018` through `S2-T0020` proved with Python examples |
| `papers/S3/PAPER_S3_01_FINITE_HYPERSPHERES.md` | polished draft | `S3C-T0001` through `S3C-T0004` proved with Python examples |
| `papers/S3/PAPER_S3_02_QUATERNION_COILS.md` | polished draft | `S3Q-T0001` through `S3Q-T0008` proved with Python examples |
| `papers/S3/PAPER_S3_03_HOPF_COILS.md` | polished draft/proved spine | `S3H-T0001` through `S3H-T0008` are Lean-proved bounded Hopf coordinate, phase-multiplication, and phase-action facts; full fibration topology remains future work |
| `papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md` | polished draft | `S3S-T0001` through `S3S-T0005` proved with Python examples; `P5-EDGE-007` adds a bounded orientation-debugging note |
| `papers/S4_S6/PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md` | polished draft | `COMMON-T0001` through `COMMON-T0006` and `S456-T0001` proved with Python examples |
| `papers/S4_S6/PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md` | polished draft | `S4-T0001` and `S4-T0002` proved with Python examples |
| `papers/S4_S6/PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md` | polished draft | `S5-T0001` and `S5-T0002` proved with Python examples |
| `papers/S4_S6/PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md` | polished draft | `S6-T0001` through `S6-T0003` proved with Python examples; `S6-W0001` warning tracked |
| `papers/S7/PAPER_S7_01_TOPOLOGICAL_7SPHERE.md` | polished draft | `S7C-T0001` through `S7C-T0003` proved with Python examples |
| `papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md` | polished draft/partial proof | `S7QH-T0001` through `S7QH-T0005` are Lean-proved coordinate theorems; full fibration topology remains future work |
| `papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md` | polished draft/proved spine | `S7O-T0001` through `S7O-T0008` are Lean-proved in a bounded Cayley-Dickson coordinate model |
| `papers/future/S15/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md` | polished draft/partial proof | `S15-T0001` is a Lean roadmap marker; `S15-T0002` through `S15-T0009` have checked Lean declarations for topological, coordinate landing, safe right-phase, and warning-boundary facts with Python examples |
| `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md` | polished draft/proved finite seed | `P2S-T0001` through `P2S-T0005` are Lean-proved double/four/eight suspension facts with Python examples |
| `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md` | polished draft/proved finite seed | `P2B-T0001` through `P2B-T0004` are Lean-proved period-8 clock facts with Python examples; Bott/Clifford periodicity remains future work |
| `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md` | polished draft/proved transition seed | `P2BU-T0001` through `P2BU-T0009` are Lean-proved product-bundle projection/fiber and base-preserving transition facts with Python examples |
| `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md` | polished draft/proved finite seed | `P2BC-T0001` through `P2BC-T0005` are Lean-proved directed-interval boundary facts with Python examples |
| `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md` | polished draft/proved certificate seed | `P2G-T0001` through `P2G-T0006` are Lean-proved proof-glyph projection, metadata-validity, and manifest-growth facts with Python examples; `P5-EDGE-001` adds an exploratory generated glyph-status fixture |
| `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md` | polished draft/proved finite seed | `APPD-T0001` through `APPD-T0005` are Lean-proved phase-coordinate facts with Python examples; `APPD-B0001` and `APPD-B0002` are exploratory deterministic period benchmark fixtures |
| `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md` | polished draft/proved finite seed | `COMPC-T0001` through `COMPC-T0005` are Lean-proved cyclic-address facts with Python examples |
| `papers/applications/PAPER_COMP_02_COIL_RAY_AND_SAMPLING.md` | polished draft/proved finite seed | `COMPR-T0001` through `COMPR-T0005` are Lean-proved direction-bin schedule facts with Python examples |
| `papers/applications/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT.md` | polished draft/proved finite seed | `COMPL-T0001` through `COMPL-T0005` are Lean-proved stride-address facts with Python examples; `COMPL-B0001` and `COMPL-B0002` are exploratory CoilLayout/stencil validation fixtures |
| `papers/applications/PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS.md` | polished draft/proved finite seed | `COMPS-T0001` through `COMPS-T0004` are Lean-proved round-robin schedule facts with Python examples |
| `papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md` | polished draft/proved finite seed | `AIA-T0001` through `AIA-T0005` are Lean-proved phase-channel facts with Python examples; `AIA-B0001` through `AIA-B0005` are exploratory deterministic phase/backend/learned/harmonic-feature benchmark fixtures |
| `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md` | polished draft/proved finite seed | `AIM-T0001` through `AIM-T0056` are Lean-proved cyclic-memory-slot, finite loop-schedule, active-token-step, middle-block-route, combined route/budget one-cycle and multi-cycle closure, looped recurrent state, positive raw-budget closure, multi-pass recurrence closure, training-free loop-budget, unavailable-budget clamp, overthinking-boundary, loop-exit certificate, certificate-availability, certificate-budget-selection, certificate multi-pass invariance, and recurrence-budget positivity facts with Python examples; `AIM-B0001` adds an exploratory cyclic-memory fixture, `AIM-B0002` adds an exploratory coil-retrieval reachability fixture, `AIM-B0003` adds an exploratory looped-recurrence schedule fixture, `AIM-B0004` adds an exploratory content-gated retrieval fixture, `AIM-B0005` adds an exploratory token-level recurrence routing fixture, `AIM-B0006` adds an exploratory training-free loop-wrapper fixture, `AIM-B0007` adds an exploratory middle-block recurrence fixture, `AIM-B0008` adds an exploratory multi-resolution recurrence fixture, `AIM-B0009` adds an exploratory learned recurrence-schedule fixture, `AIM-B0010` adds an exploratory learned content-gate retrieval fixture, `AIM-B0011` adds an exploratory loop-exit certificate fixture, `AIM-B0012` adds an exploratory learned token-level recurrence fixture, `AIM-B0013` adds an exploratory learned middle-block recurrence fixture, `AIM-B0014` adds an exploratory learned multi-resolution recurrence fixture, and `AIM-B0015` adds an exploratory tiny looped recurrent prototype fixture |
| `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md` | polished draft/proved finite seed | `AIRA-T0001` through `AIRA-T0005` are Lean-proved adapter-block facts with Python examples; `AIRA-B0001` adds an exploratory adapter-block fixture, `AIRA-B0002` adds an exploratory MultiCoil/RoPE-style positional fixture, `AIRA-B0003` adds an exploratory RoPE-style relative phase fixture, `AIRA-B0004` adds an exploratory adapter parameter-budget fixture, and `AIRA-B0005` adds an exploratory circulant-mixer validation fixture |
| `papers/physics/PAPER_PHYS_01_PROOF_CARRYING_LATTICE_GAUGE.md` | draft/proved finite seed | `PHYS-T0001` through `PHYS-T0063` are Lean-proved finite `ZMod n` phase-list and link-path holonomy, source-target composability, singleton-concat/triple/four-link, empty-identity, concat-identity, concat-associativity, reversal-algebra, path-plus-reverse zero-holonomy, boundary-append composability, source/target projection, checked path identity/associativity/holonomy interface, checked-to-link-path projection bridges, checked closed-loop, two-path cycle, and three-path cycle gauge-invariance facts, closed-loop record identity/cycle holonomy, gauge-shifted holonomy, two-path basepoint-swap facts, complete cyclic three-path basepoint-rotation packages, gauge-transform, Wilson-loop, and plaquette invariance facts with Python examples |
| `papers/generative/PAPER_GEN_01_SEED_RULE_PROVENANCE.md` | draft/proved finite seed | `GEN-T0001` through `GEN-T0043` have checked Lean declarations for finite seed-rule, coil-orbit, representative-indexed orbit-decomposition, orbit-count/period/coverage/orbit-class agreement, canonical representative coverage/disjointness, proof-glyph, exact-comparison regeneration seeds, exact-regeneration self/symmetry/transitivity facts, comparison field-equality/negative-case gates, generated-list length certificates, finite-circle node membership/no-duplicate/nonempty gates, empty declared-search boundary facts, singleton exact-search facts, bounded best-candidate soundness facts, exact-candidate absence/count gates, exact-candidate list soundness, and singleton membership gates; Python fixtures now include bounded finite-list generator search |

The theorem manifest also includes `CC-T0008`, `CC-T0017` through `CC-T0054`, and `CC-T0056` through `CC-T0061`, proving the first scaling/full-coil/affine/orbit-membership spine: invertibility iff coprime, scale-by-zero collapse, scale-by-one identity, scaling composition, scale-factor congruence normalization, scaling transport of rotation stride, scaling transport of finite coil steps, the scaling-to-coil image bridge, bijectivity of nonzero scaling on prime circles, divisor-cofactor collapse to zero, cofactor-multiple collapse to zero, period-multiple collapse to zero, cofactor-shift and period-shift address collapse, period-normal representatives, period-congruence scaled equality, bounded period-representative injectivity, period-representative image cardinality and membership, whole-circle scaling image equality and cardinality, canonical kernel/fiber representative equality and gcd cardinality, zero-fiber/kernel and scaled-target/fiber bridges, fiber-set equality modulo scaled value and stride period, arbitrary target-fiber emptiness/cardinality, image-times-fiber and image-times-kernel scaling factorizations, kernel-subgroup membership, the exact divisibility and period-divisibility criteria for scaling to zero, the exact product-congruence criterion for scaled-address equality, coprime reflection of address congruence, full-coil iff coprime, rotation bijectivity, affine composition normal form, coprime affine bijectivity, and same-orbit natural-representative congruence modulo `gcd(n,k)`.

`CC-T0062` through `CC-T0072` are external theorem bridges: they restate mathlib-backed Erdős-Ginzburg-Ziv, Cauchy-Davenport, Katona/Erdős-Ko-Rado, Roth, Hales-Jewett/van der Waerden, cycle/circulant graph, and empty unit-distance boundary facts in Circle-facing language. These are Lean-checked wrappers around established mathlib results, not new Circle Calculus proofs or claims of progress on an open Erdős problem; see `docs/ERDOS_CIRCLE_MATH_REVIEW.md`.

The executable support layer `circle_math/additive.py` now gives finite-circle sumset examples, Cauchy-Davenport example certificates, zero-sum witness search, and the standard EGZ sharpness family. `circle_math/extremal.py` adds finite Katona/EKR, Roth/AP, Ramsey/Hales-Jewett, and cycle/circulant graph examples. These examples support the reader and tests; the formal theorem source remains Lean.

The D0 dimensional scaffold is also in place: dimension manifests, dimension dictionaries, planned paper stubs, Lean/Python scaffolds, and dimension validation scripts. Future-dimension claims remain planned, deferred, exploratory, or stated until actual Lean proofs exist.

Phase II and application scaffolds are also in place under `papers/phase2/`, `papers/applications/`, `manifests/theories/`, and `manifests/applications/`. `PAPER_P2_01_STABLE_SPHERE_CALCULUS` through `PAPER_P2_05_PROOF_CARRYING_GLYPHS`, `PAPER_APP_01_COIL_DATA_ANALYSIS`, `PAPER_COMP_01` through `PAPER_COMP_04`, and `PAPER_AI_01` through `PAPER_AI_03` now have proved seeds. The 2026-06-05 compute-applications handoff is preserved in `docs/PHASE2_AND_APPLICATIONS.md` and `circle_calculus_codex_handoff/source_logs/04_compute_applications_browser_note.md`. Benchmark claims remain benchmark work, not proof claims.

AI is now treated as a dedicated active program rather than a single application lane. The roadmap tracks phase channels, cyclic memory, coil/sparse attention, adapter blocks, RoPE/MultiCoil positional structure, looped/recursive transformer recurrence schedules, token-level and middle-block recurrence, multi-resolution recurrence, learned recurrence schedules, training-free loop wrappers, recurrent/state-space/convolutional models, harmonic/circulant features, geometry-aware representations, proof-carrying model components, and MLX/Mac-compatible prototypes. The proof rule remains strict: Lean can certify finite indexing, loop-budget, and rewrite facts, while model quality, speed, parameter efficiency, and usefulness require reproducible benchmarks with ordinary baselines and negative controls. The starter AI fixtures now cover phase channels, learned-feature and harmonic-feature baselines, backend parity, cyclic memory, coil-retrieval reachability, content-gated retrieval routing, learned content-gate retrieval routing, looped-recurrence schedule controls, loop-exit certificate controls, token-level recurrence routing, learned token-level recurrence routing, training-free loop-wrapper controls, middle-block recurrence controls, learned middle-block recurrence controls, multi-resolution recurrence controls, learned multi-resolution recurrence controls, learned recurrence-schedule controls, a tiny looped recurrent-state prototype, adapter blocks, adapter parameter budgets, circulant-mixer validation, MultiCoil/RoPE-style positional structure, and RoPE-style relative phase.

Phase III is now implemented as the first Circle Calculus Living Book milestone: a Quarto-based interactive explainer site generated from manifests, dictionary entries, papers, Python reference models, and Lean proof metadata. Its policy and roadmap live in `docs/LIVING_BOOK_POLICY.md`, `docs/LIVING_BOOK_ROADMAP.md`, and `docs/LIVING_BOOK_WIDGETS.md`; `site/reader_path.qmd` gives a proof-status-safe tour through dimensions, applications, source trails, and local verification; the source browser handoff is archived at `circle_calculus_codex_handoff/source_logs/05_living_book_browser_note.md`. The proof-backed showcase now includes generated reader routes for hard mathematics bridges, the cyclic proof spine, phase/finite-physics interfaces, and proof-carrying generated/AI structures; each route is ready only when every listed capability is known, claim-contracted, backed by theorem/source/Living Book evidence, backed for its declared role, connected by an ordered proof trail, packaged as a skeptical-reader review packet, tied to a generated standard-parity/Circle-native-value comparison, bundled into a route-level reviewer dossier, summarized by a generated impact summary, and clean under advertising-language guardrails. The Living Book now includes guided S1 widgets plus application widgets for phase-channel baselines, learned-feature baselines, harmonic/Fourier feature baselines, backend parity fixtures, cyclic memory, coil-retrieval reachability, content-gated retrieval, learned content-gate retrieval, loop-recurrence budgets, loop-exit certificates, training-free loop-wrapper controls, token-level recurrence routing, learned token-level recurrence routing, learned middle-block recurrence routing, learned multi-resolution recurrence routing, learned recurrence-schedule routing, MultiCoil positional structure, RoPE-style relative phase, finite path algebra, plaquette holonomy, Hopf hidden phase, quaternion spin sign ambiguity, periodic winding dynamics, seed-rule records, proof-glyph certificates, and bounded generator comparison. The Living Book is an explanation layer, not a proof layer. The intended public URL is `https://corbensorenson.github.io/circle-calculus/`, deployed from the static Quarto render only after proof/status/source-link checks pass in GitHub Actions.

The next project phases are intentionally wide, deep, application-aware, and correctness-driven: Phase IV audits every dimensional level and application area for missing theorem targets, paper improvements, reusable lemmas, dictionary gaps, and stronger proof spines; Phase V searches edge problem spaces where Circle Calculus may provide leverage that is hard, awkward, or unavailable in ordinary presentations; the dedicated Circle AI program explores all serious AI avenues with proof/benchmark separation; Phase VI sweeps the whole corpus so the writing is cleaner, the claims are more correct, and the proof-status links are easy for outsiders to consume; Phase VII turns physics-facing phase/gauge/holonomy/spin/winding ideas and seed-plus-rules generative compression into bounded proof targets, fixtures, papers, and Living Book lessons.

Phase VII is now an active research lane. The first finite physics slice has Lean-proved `ZMod n` phase-list holonomy, finite link-path record holonomy, singleton/two-link/singleton-concat/three-link/four-link, empty-identity, concat-identity, concat-associativity, reversal-algebra, boundary-append composability, source/target projection, a checked finite path interface with identity, associativity, holonomy, checked-to-link-path projection laws, and closed checked-loop gauge-invariance facts, endpoint-gauge, Wilson-loop, and plaquette facts, plus Python Wilson-loop certificates. The generative slice has Lean-proved finite seed-rule, finite-circle node membership/no-duplicate/nonempty facts, coil-orbit schedule, representative-indexed orbit-decomposition, orbit-count/period/coverage/orbit-class agreement, canonical representative coverage/disjointness, proof-glyph, exact-comparison seeds, exact-regeneration self/symmetry/transitivity facts, and comparison field-equality/negative-case gates plus Python fixtures for finite circles, finite-circle generated diagrams, finite physics-loop diagrams, coils, orbit decompositions, proof glyphs, generator-vs-explicit comparisons, and bounded finite-list generator search. The Living Book now includes finite path algebra, plaquette holonomy, Hopf hidden phase, quaternion spin sign ambiguity, and periodic winding-dynamics widgets for physics, plus generated-diagram, orbit-family, proof-glyph certificate, and bounded generator-comparison widgets for seed/rule structures. Berry/geometric-phase primers beyond the bounded Hopf coordinate widget, deeper quaternion quotient lessons, deeper Floquet/action-angle comparisons, stronger finite search-space baselines, and stronger minimality criteria remain next targets. The repo does not claim new physics or universal compression.

Current Phase VI maintenance state: all manifest papers now include source trails linking paper prose to Lean/Python sidecars and proof-status boundaries. `make check` also validates recursive paper theorem-id links across all theorem-id prefixes, paper source trails, root plus dimension dictionary entries, the application/theory/target manifests that connect papers, sidecars, benchmarks, theorem ids, and dictionary dependencies, and application guardrails for baseline language, benchmark/proof separation, and MLX/CUDA wording.

The README is updated after meaningful proof batches, paper batches, roadmap changes, or application-context additions. Tiny internal-only edits should update the relevant source files without creating README churn.

## Proof Standard

A theorem is treated as proved only when all of the following are true:

1. It has a theorem id in `manifests/theorem_manifest.yaml` or the appropriate dimension manifest under `manifests/dimensions/`.
2. It has an exact Lean declaration name.
3. Its manifest status is `proved` or `lean_proved`.
4. `lake build` succeeds.
5. `scripts/check_no_fake_proofs.py` finds no forbidden proof placeholders.

Python tests and generated diagrams are executable support. They help keep the papers honest, but they are not formal proofs.

For the fuller policy, see `docs/PROOF_POLICY.md`.

## Repository Layout

```text
Circle/                         Lean 4/mathlib formalization
Circle.lean                     Root Lean import file
circle_math/                    Python reference models
dictionary/                     Shared Circle Calculus vocabulary
docs/                           Proof policy and foundational notes
manifests/                      Paper and theorem metadata
papers/                         Human-readable papers
site/                           Phase III Quarto Living Book source
scripts/                        Repository validation scripts
sidecars/                       Per-paper Lean, Python, and diagram artifacts
tests/                          Python regression/property tests
circle_calculus_codex_handoff/  Original planning pack and source logs
circle_calculus_dimensional_handoff/  Dimensional-ladder planning pack
```

## Getting Started

Install Lean through `elan` if it is not already installed:

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y --default-toolchain none
```

Set up Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run the full verification suite:

```bash
make check
```

The first Lean build may take time because Lake has to fetch and build mathlib dependencies pinned by `lean-toolchain` and `lake-manifest.json`.

## Useful Commands

```bash
make lean        # build the root Lean library
make sidecarlean # check all per-paper Lean sidecars
make test        # run Python tests
make manifest    # validate theorem metadata
make dictionary  # validate root and dimension dictionary metadata
make papermanifest # validate paper-to-sidecar/theorem/dictionary links
make paperlinks  # recursively verify papers cite known theorem ids and matching Lean names
make papersources # verify manifest papers expose source trails and proof-status boundaries
make researchmanifests # validate application/theory manifest sidecars and benchmark refs
make claimlanguage # audit proved-language against theorem statuses
make phase4targets # validate the wide/deep theorem target registry
make phase5targets # validate the edge problem-space target registry
make phase6targets # validate the global sweep target registry
make phase7targets # validate the physics/generator target registry
make dimensioncheck # validate dimension manifests, imports, and paper links
make nofake      # reject forbidden proof placeholders
make examples    # regenerate current example diagrams
make sourcecheck # run repository checks after Lean has already been built
make site-data   # export Living Book JSON from manifests/dictionaries/papers
make sitecheck   # validate Living Book structure, ids, links, status, and widgets
python scripts/site/check_site_scaffold_contract.py # verify scaffold/future/non-proof guardrails
python scripts/site/check_capability_contracts.py # verify generated proof-backed showcase claim contracts
python scripts/site/check_site_source_links.py # verify generated GitHub/source-link paths
python scripts/site/check_site_static_source_links.py # verify hard-coded GitHub source links in site/docs/README
python scripts/site/check_site_data_backlinks.py # verify generated theorem/dictionary/paper/widget/glyph backlinks
python scripts/site/check_site_widget_contracts.py # verify widget mounts, scripts, and index entries
python scripts/site/check_site_accessibility_contract.py # verify widget accessibility guardrails
python scripts/site/check_widget_runtime_links.py # verify widget runtime keeps symbolic refs out of GitHub links
make site-render # render the Quarto Living Book into site/_site through the checked render helper
make site-render-check # validate the rendered GitHub Pages artifact
make living-book-check # run core checks plus Living Book checks, render, and artifact validation
make check       # run the full suite
```

## License And Citation

Circle Calculus is released under the MIT License. You can use, copy, modify, publish, and build on the repository freely as long as the copyright and license notice stay with substantial reused portions.

If you use this project in a paper, post, dataset, codebase, or derivative research artifact, please cite Corben Sorenson and the public repository. GitHub and citation tools can read the recommended citation from `CITATION.cff`.

## How To Read The Project

Start with:

1. [Circle Calculus Living Book](https://corbensorenson.github.io/circle-calculus/)
2. `site/reader_path.qmd`
3. `site/chapters/foundations/00_mathematical_building_blocks.qmd`
4. `site/chapters/S1/01_finite_circles.qmd`
5. `site/chapters/S1/02_rotation_as_addition.qmd`
6. `site/chapters/S1/03_coils_orbits_closure.qmd`
6. `site/chapters/S1/04_period_gcd_prime_full_coils.qmd`
7. `site/chapters/S1/05_winding_lift.qmd`
8. `site/chapters/S1/06_review.qmd`
9. `papers/PAPER_01_FINITE_CIRCLES.md`
10. `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`
11. `papers/PAPER_02_WINDING_NATURALS.md`
12. `sidecars/PAPER_02_WINDING_NATURALS/lean/Paper02.lean`
13. `dictionary/circle_dictionary.yaml`
14. `manifests/theorem_manifest.yaml`
15. `docs/COMPLETION_ROADMAP.md`
16. `docs/DIMENSIONAL_LADDER.md`
17. `docs/PHASE2_AND_APPLICATIONS.md`
18. `docs/LIVING_BOOK_ROADMAP.md`

The Living Book gives the guided learning path. The papers give long-form exposition. The sidecars show the proof links. The dictionary fixes vocabulary so later papers reuse the same meanings instead of drifting.

## How To Add A Paper

Use `papers/template.md` and keep the paper connected from the beginning.

1. Add or reuse dictionary entries in `dictionary/circle_dictionary.yaml`.
2. Add theorem ids to `manifests/theorem_manifest.yaml`.
3. Add the paper entry to `manifests/paper_manifest.yaml`.
4. Put Lean sidecars under `sidecars/<PAPER_ID>/lean/`.
5. Put executable examples or tests under `sidecars/<PAPER_ID>/python/`.
6. Add diagrams under `sidecars/<PAPER_ID>/diagrams/` when they clarify the argument.
7. Run `make check`.

If a statement is important but not proved yet, mark it as planned or blocked in the manifest instead of presenting it as proved.

## Current Theorem Spine

Proved finite-circle core:

- `CC-T0001`: rotation by zero
- `CC-T0002`: rotation composition
- `CC-T0003`: rotation inverse
- `CC-T0056`: rotations are bijections
- `CC-T0004`: closure condition
- `CC-T0005`: period equals `n / gcd(n,k)`
- `CC-T0006`: orbit decomposition count
- `CC-T0055`: same orbit iff the node difference lies in the stride subgroup
- `CC-T0059`: same-orbit natural representatives are gcd-congruent
- `CC-T0060`: gcd-congruent natural representatives are in the same orbit
- `CC-T0061`: same orbit iff natural representatives are gcd-congruent
- `CC-T0062`: Erdős-Ginzburg-Ziv zero-sum bridge on `C n`
- `CC-T0063`: Cauchy-Davenport sumset-growth bridge on prime-size `C p`
- `CC-T0064` through `CC-T0072`: external Katona/Erdős-Ko-Rado, Roth, Hales-Jewett/van der Waerden, cycle/circulant graph, and empty unit-distance boundary bridges
- `CC-T0007`: prime full coil
- `CC-T0054`: full coil iff coprime
- `CC-T0008`: scaling invertible iff coprime
- `CC-T0028`: scaling by zero collapses to zero
- `CC-T0017`: scaling by one is identity
- `CC-T0018`: scaling maps compose by multiplying scale factors
- `CC-T0029`: congruent scale factors act identically
- `CC-T0019`: scaling transports rotation stride
- `CC-T0020`: scaling transports finite coil steps
- `CC-T0031`: scaling a natural step index gives the matching coil step from zero
- `CC-T0021`: nonzero scaling below a prime circle size is bijective
- `CC-T0022`: scaling sends a divisor cofactor to zero
- `CC-T0023`: scaling sends divisor cofactor multiples to zero
- `CC-T0024`: scaling collapses addresses shifted by divisor cofactor multiples
- `CC-T0025`: scaling maps a natural address to zero iff the modulus divides the scaled product
- `CC-T0030`: scaling maps a natural address to zero iff the coil period divides that address
- `CC-T0032`: scaling maps natural multiples of the coil period to zero
- `CC-T0033`: scaling collapses addresses shifted by natural multiples of the coil period
- `CC-T0034`: scaling a natural address equals scaling its residue modulo the coil period
- `CC-T0035`: scaled natural addresses are equal iff they are congruent modulo the coil period
- `CC-T0036`: scaling is injective on representatives below the coil period
- `CC-T0037`: the scaled image of one period of representatives has cardinality equal to the coil period
- `CC-T0038`: every scaled natural address lands in the period-representative image
- `CC-T0039`: the full finite scaling image equals the period-representative image
- `CC-T0040`: the full finite scaling image has cardinality equal to the coil period
- `CC-T0041`: canonical scaling-kernel representatives are exactly the period multiples below `gcd(n,k)`
- `CC-T0042`: the canonical scaling-kernel representative set has cardinality `gcd(n,k)`
- `CC-T0043`: canonical scaling-fiber representatives are offset period multiples
- `CC-T0044`: canonical scaling-fiber representative sets have cardinality `gcd(n,k)`
- `CC-T0050`: the scaled zero fiber is the canonical kernel representative set
- `CC-T0052`: canonical representative fibers are equal iff the scaled representatives are equal
- `CC-T0053`: canonical representative fibers are equal iff representatives are congruent modulo the stride period
- `CC-T0045`: natural representatives lie in the scaling kernel subgroup exactly when the stride period divides them
- `CC-T0051`: the target fiber over a scaled representative is that representative's canonical fiber
- `CC-T0046`: target fibers are empty for target nodes outside the scaling image
- `CC-T0047`: target fibers over image nodes have cardinality `gcd(n,k)`
- `CC-T0048`: scaling image cardinality times reachable target-fiber cardinality equals the circle size
- `CC-T0049`: scaling image cardinality times kernel representative cardinality equals the circle size
- `CC-T0026`: scaled natural addresses are equal iff their scaled products are congruent modulo the circle size
- `CC-T0027`: coprime scaling reflects ordinary address congruence
- `CC-T0057`: affine circle maps compose by affine modular arithmetic
- `CC-T0058`: coprime affine circle maps are bijective

Proved winding/natural-number core:

- `CC-T0009`: unique winding/residue lift
- `CC-T0010`: lifted addition decomposition
- `CC-T0011`: lifted existence
- `CC-T0012`: successor with carry
- `CC-T0013`: lifted addition right zero identity
- `CC-T0014`: lifted addition associativity at reconstructed-value level
- `CC-T0015`: lifted addition left zero identity
- `CC-T0016`: iterated lifted successor

Proved common and dimensional spine:

- `COMMON-T0001`: finite cell-count Euler characteristic definition
- `COMMON-T0002`: finite suspension cell counts
- `COMMON-T0003`: finite suspension Euler theorem
- `COMMON-T0004`: general iterated finite suspension Euler theorem
- `COMMON-T0005`: two-step finite suspension Euler parity theorem
- `COMMON-T0006`: direct finite double-suspension Euler theorem
- `P2S-T0001`: finite double suspension preserves Euler characteristic
- `P2S-T0002`: finite four-suspension iteration preserves Euler characteristic
- `P2S-T0003`: finite four-suspension counts are two double-suspension steps
- `P2S-T0004`: finite eight-suspension counts are two four-suspension steps
- `P2S-T0005`: finite eight-suspension iteration preserves Euler characteristic
- `P2B-T0001`: finite period-8 dimension clock index is below 8
- `P2B-T0002`: finite period-8 dimension clock is invariant under adding 8
- `P2B-T0003`: finite period-8 dimension clock sends zero to zero
- `P2B-T0004`: finite period-8 dimension clock is invariant under any whole number of eight-step passes
- `P2BU-T0001`: trivial-bundle projection returns the base coordinate
- `P2BU-T0002`: trivial-bundle fiber coordinate returns the fiber value
- `P2BU-T0003`: trivial-bundle projection is invariant under changing only the fiber
- `P2BU-T0004`: trivial-bundle fiber coordinate is invariant under changing only the base
- `P2BU-T0005`: base-preserving bundle transitions do not change projection
- `P2BU-T0006`: bundle transitions apply their fiber map to the fiber coordinate
- `P2BU-T0007`: bundle transition composition agrees with sequential application
- `P2BU-T0008`: identity bundle transition leaves every trivial-bundle point unchanged
- `P2BU-T0009`: composing a bundle transition with identity on either side acts like the original transition on points
- `P2BC-T0001`: point-boundary after interval-boundary is zero in the directed-interval seed
- `P2BC-T0002`: reversing a directed interval negates its boundary
- `P2BC-T0003`: reversing a directed interval twice returns it
- `P2BC-T0004`: a constant directed interval has zero boundary
- `P2BC-T0005`: a directed interval boundary splits additively through an intermediate point
- `P2G-T0001`: proof glyph certificate exposes its theorem id
- `P2G-T0002`: proof glyph certificate exposes its Lean declaration name
- `P2G-T0003`: proof glyph certificate exposes its glyph id
- `P2G-T0004`: valid proof glyphs resolve to finite theorem metadata with matching theorem id and Lean name
- `P2G-T0005`: matching theorem metadata constructs a valid proof glyph relation
- `P2G-T0006`: proof glyph validity is preserved when finite theorem metadata grows by one entry
- `APPD-T0001`: finite phase coordinate is bounded by a positive period
- `APPD-T0002`: finite phase coordinate closes after adding one full period
- `APPD-T0003`: finite phase coordinate at zero is zero
- `APPD-T0004`: finite phase coordinate closes after any whole number of full periods
- `APPD-T0005`: finite phase-coordinate normalization is idempotent
- `APPD-B0001`: exploratory Python fixture comparing coil closure ranking with an autocorrelation baseline on a known-period synthetic signal
- `APPD-B0002`: exploratory Python fixture suite for clean, noisy, aliased, and multi-period synthetic signals with coil closure, autocorrelation, and periodogram-style baselines
- `COMPC-T0001`: cyclic address is bounded by a positive circular buffer size
- `COMPC-T0002`: cyclic address is unchanged after adding one full buffer size
- `COMPC-T0003`: cyclic address at zero is zero
- `COMPC-T0004`: cyclic address is unchanged after any whole number of full buffer-size passes
- `COMPC-T0005`: cyclic address normalization is idempotent
- `COMPR-T0001`: direction-bin schedule is bounded by a positive bin count
- `COMPR-T0002`: direction-bin schedule closes after one full pass through the bins
- `COMPR-T0003`: direction-bin schedule at zero is zero
- `COMPR-T0004`: direction-bin schedule closes after any whole number of full bin passes
- `COMPR-T0005`: direction-bin schedule normalization is idempotent
- `COMPL-T0001`: stride address is bounded by a positive circular size
- `COMPL-T0002`: stride address closes after one full pass through the circular step horizon
- `COMPL-T0003`: zero step has zero stride address
- `COMPL-T0004`: zero stride has zero stride address
- `COMPL-T0005`: stride address closes after any whole number of full circular-size passes
- `COMPL-B0001`: exploratory CoilLayout validation/benchmark-grid fixture
- `COMPL-B0002`: exploratory periodic-boundary stencil validation fixture
- `COMPS-T0001`: round-robin slot schedule is bounded by a positive slot count
- `COMPS-T0002`: round-robin slot schedule closes after one full pass through the slots
- `COMPS-T0003`: round-robin slot schedule at zero is zero
- `COMPS-T0004`: round-robin slot schedule closes after any whole number of full passes
- `AIA-T0001`: AI phase channel is bounded by a positive period
- `AIA-T0002`: AI phase channel closes after one full period
- `AIA-T0003`: AI phase channel at zero is zero
- `AIA-T0004`: AI phase channel closes after any whole number of full periods
- `AIA-T0005`: AI phase-channel normalization is idempotent
- `AIA-B0001`: exploratory deterministic phase-channel benchmark fixture
- `AIA-B0002`: exploratory learned-baseline fixture with periodic and nonperiodic controls
- `AIA-B0003`: exploratory CPU/optional-MLX backend parity fixture across current AI synthetic cases
- `AIA-B0004`: exploratory learned-feature fixture comparing cyclic phase features with dense-scalar, learned-position, and wrong-period baselines
- `AIA-B0005`: exploratory harmonic/Fourier-feature fixture comparing cyclic phase and correct sine/cosine lookup with wrong-frequency, scalar, and learned-position baselines
- `AIM-T0001`: cyclic memory slot is bounded by a positive bank size
- `AIM-T0002`: cyclic memory slot closes after one full bank pass
- `AIM-T0003`: cyclic memory slot at zero is zero
- `AIM-T0004`: cyclic memory slot closes after any whole number of full bank passes
- `AIM-T0005`: cyclic memory-slot normalization is idempotent
- `AIM-T0006`: looped-recurrence required depth is positive
- `AIM-T0007`: looped-recurrence required depth is bounded by a positive loop period
- `AIM-T0008`: looped-recurrence required depth closes after one full loop-period shift
- `AIM-T0009`: token recurrence budget closes after one full loop-period shift
- `AIM-T0010`: training-free loop budget is capped by the configured maximum
- `AIM-T0011`: training-free loop budget is capped by the required loop depth
- `AIM-T0012`: loop overthinking boundary is at least the required loop depth
- `AIM-T0013`: full-period loop budget makes exit available
- `AIM-T0014`: loop-exit availability closes after one full loop-period shift
- `AIM-T0015`: loop-exit certificate records the exact required step
- `AIM-T0016`: loop-exit certificate records the budget bound
- `AIM-T0017`: loop-exit certificate records the overthinking guardrail bound
- `AIM-T0018`: token recurrence budgets are bounded by the positive loop period
- `AIM-T0019`: training-free loop budgets are periodic under one full loop-period shift
- `AIM-T0020`: an available loop-exit budget makes the training-free wrapper choose the exact required depth
- `AIM-T0021`: loop overthinking boundaries are periodic under one full loop-period shift
- `AIM-T0022`: token recurrence budgets are positive
- `AIM-T0023`: available training-free loop budgets are positive
- `AIM-T0024`: loop-exit certificates carry positive exit steps
- `AIM-T0025`: unavailable training-free loop budgets clamp to `maxLoops`
- `AIM-T0026`: looped-recurrence required depth closes after any whole number of loop-period passes
- `AIM-T0027`: token recurrence budgets close after any whole number of loop-period passes
- `AIM-T0028`: training-free loop budgets close after any whole number of loop-period passes
- `AIM-T0029`: loop overthinking boundaries close after any whole number of loop-period passes
- `AIM-T0030`: loop-exit availability closes after any whole number of loop-period passes
- `AIM-T0031`: loop-exit certificates imply exit availability
- `AIM-T0032`: loop-exit certificates make the training-free wrapper choose the certified exit step
- `AIM-T0033`: loop-exit certificate exit steps close after any whole number of loop-period passes
- `AIM-T0034`: loop-exit certificate guardrail boundaries close after any whole number of loop-period passes
- `AIM-T0035`: every token is active at the first one-indexed loop step
- `AIM-T0036`: token active-step membership closes after any whole number of loop-period token shifts
- `AIM-T0037`: active token steps are bounded by the positive loop period
- `AIM-T0038`: token steps beyond the loop period are inactive
- `AIM-T0039` through `AIM-T0043`: Lean-proved selected middle-block route lower/upper bounds, one-width closure, multi-width closure, and zero-sample anchor facts
- `AIM-T0044` through `AIM-T0048` plus `AIM-T0056`: Lean-proved combined middle-block/budget route lower/upper block bounds, positive/bounded budget facts, and one-cycle/multi-cycle product common-cycle closure
- `AIM-T0049` through `AIM-T0055`: Lean-proved looped recurrent-state boundedness, one-step zero state, required-depth phase recovery, certified-budget phase recovery, whole-period token-shift invariance, and positive raw-budget one-period/multi-period closure facts
- `AIM-B0001`: exploratory cyclic-memory benchmark fixture with constant/scalar-threshold baselines and a nonperiodic control
- `AIM-B0002`: exploratory coil-retrieval reachability fixture with coil-path, local-window, wrong-stride, full-attention oracle, and near-lag controls
- `AIM-B0003`: exploratory looped-recurrence schedule fixture with single-pass, fixed-loop, adaptive-exit, recurrent-memory, sparse phase-router, over-looped, and dense-threshold controls
- `AIM-B0011`: exploratory loop-exit certificate fixture with score trace, exit availability, budget status, overthinking guardrail status, and a fixed-budget no-exit control
- `AIM-B0004`: exploratory content-gated retrieval fixture with static coil, static local, wrong-gate, union-candidate, full-attention, and candidate-budget controls
- `AIM-B0005`: exploratory token-level recurrence routing fixture with per-token budgets, active-token counts, selected middle block, resolution labels, fixed/wrong/over-loop controls, and a nonperiodic scalar-threshold control
- `AIM-B0012`: exploratory learned token-level recurrence fixture with phase-to-budget lookup, fixed-budget baseline, wrong-period control, shifted-budget control, over-loop control, and nonperiodic scalar-threshold control
- `AIM-B0006`: exploratory training-free loop-wrapper fixture with circular phase budgets, single-pass/fixed-loop/wrong-period/over-loop controls, a nonperiodic scalar-threshold baseline, and CPU/optional-MLX scoring
- `AIM-B0007`: exploratory middle-block recurrence fixture with selected-block, full-block, fixed-budget, wrong-block, over-loop controls, and block-pass accounting
- `AIM-B0013`: exploratory learned middle-block recurrence fixture with phase-to-block and phase-to-budget lookup tables, selected-band/full-block baselines, fixed-budget, wrong-period, wrong-block, over-loop controls, and block-pass accounting
- `AIM-B0008`: exploratory multi-resolution recurrence fixture with coarse/fine phase routing, single-resolution, fixed-budget, wrong-resolution, over-loop controls, and active-sample accounting
- `AIM-B0014`: exploratory learned multi-resolution recurrence fixture with phase-to-budget and phase-to-resolution lookup tables, single-resolution/fixed-budget baselines, wrong-period controls, over-loop controls, and active-sample accounting
- `AIM-B0009`: exploratory learned recurrence-schedule fixture with a phase-to-budget lookup, fixed-budget baseline, wrong-period control, and over-loop control
- `AIM-B0015`: exploratory tiny looped recurrent-state prototype with direct phase, one-step, scalar-threshold, wrong-period, and nonperiodic controls
- `AIM-B0010`: exploratory learned content-gate retrieval fixture with a phase-to-route lookup, static coil/local baselines, wrong-period and flipped-gate controls, union/full-attention baselines, route accuracy, and candidate-budget diagnostics
- `AIRA-T0001`: adapter block index is bounded by a positive block size
- `AIRA-T0002`: adapter block index closes after one full block pass
- `AIRA-T0003`: adapter block index at zero is zero
- `AIRA-T0004`: adapter block index closes after any whole number of full block passes
- `AIRA-T0005`: adapter-block normalization is idempotent
- `AIRA-B0001`: exploratory adapter-block benchmark fixture with constant/scalar-threshold baselines and a nonperiodic control
- `AIRA-B0002`: exploratory MultiCoil/RoPE-style positional fixture with single-period, constant, scalar-threshold, and nonperiodic controls
- `AIRA-B0003`: exploratory RoPE-style relative phase fixture with wrong-period, query-position, scalar-threshold, and nonperiodic controls
- `AIRA-B0004`: exploratory adapter parameter-budget fixture with dense adapter, LoRA-style low-rank, block-cyclic shared-table, and alias/load diagnostics
- `AIRA-B0005`: exploratory circulant-mixer validation fixture with dense circulant-matrix parity, wrong-shift control, and parameter-count diagnostics
- `PHYS-T0001`: Lean-proved finite path holonomy concatenation theorem
- `PHYS-T0002`: Lean-proved finite reversed-path holonomy theorem
- `PHYS-T0003`: Lean-proved finite gauge-transform endpoint theorem
- `PHYS-T0004`: Lean-proved finite closed Wilson-loop invariance theorem
- `PHYS-T0005`: Lean-proved finite square-plaquette invariance theorem
- `PHYS-T0006`: Lean-proved finite link-path holonomy concatenation theorem
- `PHYS-T0007`: Lean-proved finite reversed-link-path holonomy theorem
- `PHYS-T0008`: Lean-proved singleton finite link-path composability theorem
- `PHYS-T0009`: Lean-proved two-link finite link-path composability iff theorem
- `PHYS-T0010`: Lean-proved singleton-concat finite link-path composability iff theorem
- `PHYS-T0011`: Lean-proved three-link finite link-path composability iff theorem
- `PHYS-T0012`: Lean-proved four-link finite link-path composability iff theorem
- `PHYS-T0013`: Lean-proved empty finite link-path composability theorem
- `PHYS-T0014`: Lean-proved left empty-concat finite link-path composability theorem
- `PHYS-T0015`: Lean-proved right empty-concat finite link-path composability theorem
- `PHYS-T0016`: Lean-proved left empty-concat finite link-path identity theorem
- `PHYS-T0017`: Lean-proved right empty-concat finite link-path identity theorem
- `PHYS-T0018`: Lean-proved finite link-path concatenation associativity theorem
- `PHYS-T0019`: Lean-proved finite gauge-link double-reversal theorem
- `PHYS-T0020`: Lean-proved finite gauge-link path double-reversal theorem
- `PHYS-T0021`: Lean-proved finite gauge-link path reverse-concat theorem
- `PHYS-T0022`: Lean-proved finite gauge-link list boundary-append composability theorem
- `PHYS-T0023`: Lean-proved finite gauge-link path boundary-append composability theorem
- `PHYS-T0024`: Lean-proved finite gauge-link path source projection under nonempty-left concatenation theorem
- `PHYS-T0025`: Lean-proved finite gauge-link path target projection under nonempty-right concatenation theorem
- `PHYS-T0026`: Lean-proved endpoint-record boundary composability theorem
- `PHYS-T0027`: Lean-proved endpoint-record append theorem
- `PHYS-T0028`: Lean-proved checked identity-path source theorem
- `PHYS-T0029`: Lean-proved checked identity-path target theorem
- `PHYS-T0030`: Lean-proved checked singleton-path source theorem
- `PHYS-T0031`: Lean-proved checked singleton-path target theorem
- `PHYS-T0032`: Lean-proved checked path-concat source theorem
- `PHYS-T0033`: Lean-proved checked path-concat target theorem
- `PHYS-T0034`: Lean-proved checked path left-identity theorem
- `PHYS-T0035`: Lean-proved checked path right-identity theorem
- `PHYS-T0036`: Lean-proved checked path associativity theorem
- `PHYS-T0037`: Lean-proved checked identity-path holonomy theorem
- `PHYS-T0038`: Lean-proved checked singleton-path holonomy theorem
- `PHYS-T0039`: Lean-proved checked path-concat holonomy theorem
- `PHYS-T0040`: Lean-proved checked-to-link-path composability projection theorem
- `PHYS-T0041`: Lean-proved checked-to-link-path holonomy projection theorem
- `PHYS-T0042`: Lean-proved checked-to-link-path concat projection theorem
- `PHYS-T0043`: Lean-proved checked identity-path closure theorem
- `PHYS-T0044`: Lean-proved checked path cycle-concat closure theorem
- `PHYS-T0045`: Lean-proved closed checked-path gauge-invariance theorem
- `PHYS-T0046`: Lean-proved two-path cycle gauge-invariance theorem
- `PHYS-T0047`: Lean-proved closed gauge-loop record gauge-invariance theorem
- `PHYS-T0048`: Lean-proved closed identity-loop holonomy theorem
- `PHYS-T0049`: Lean-proved closed two-path cycle holonomy theorem
- `PHYS-T0050`: Lean-proved path-followed-by-reverse zero-holonomy theorem
- `PHYS-T0051`: Lean-proved reverse-followed-by-path zero-holonomy theorem
- `PHYS-T0052`: Lean-proved identity closed-loop gauge-shifted zero-holonomy theorem
- `PHYS-T0053`: Lean-proved two-path closed-cycle gauge-shifted holonomy sum theorem
- `PHYS-T0054` and `PHYS-T0055`: Lean-proved two-path closed-cycle basepoint-swap holonomy and gauge-shifted holonomy theorems
- `PHYS-T0056` through `PHYS-T0063`: Lean-proved three-path closed-cycle holonomy, gauge-shifted holonomy, one-step/two-step basepoint-rotation, and all-cyclic-basepoint package theorems
- `GEN-T0001`: Lean-proved finite-circle seed-rule regeneration theorem
- `GEN-T0002`: Lean-proved period-indexed coil-orbit schedule regeneration theorem
- `GEN-T0003`: orbit-decomposition seed-rule record regenerates its representative-indexed finite stride-orbit schedules
- `GEN-T0004`: Lean-proved proof-glyph seed-rule regeneration theorem
- `GEN-T0005`: Lean-proved exact-regeneration comparison theorem
- `GEN-T0006`: Lean-proved orbit-decomposition generator orbit-count theorem
- `GEN-T0007`: Lean-proved generated representative orbit-length theorem
- `GEN-T0008`: Lean-proved orbit-count times period coverage theorem
- `GEN-T0009`: Lean-proved generator orbit-count/formal orbit-class-count agreement theorem
- `GEN-T0010`: Lean-proved modulo representative range theorem
- `GEN-T0011`: Lean-proved modulo representative same-orbit coverage theorem
- `GEN-T0012`: Lean-proved canonical representatives same-orbit iff equality theorem
- `GEN-T0013`: Lean-proved distinct canonical representatives disjoint theorem
- `GEN-T0014`: Lean-proved exact-regeneration self theorem
- `GEN-T0015`: Lean-proved exact-regeneration symmetry theorem
- `GEN-T0016`: Lean-proved exact-regeneration transitivity theorem
- `GEN-T0017`: Lean-proved exact-regeneration iff regenerated/generated field equality theorem
- `GEN-T0018`: Lean-proved exact-regeneration witness implies regenerated/generated field equality theorem
- `GEN-T0019`: Lean-proved unequal regenerated/generated values block exact regeneration theorem
- `GEN-T0020`: Lean-proved finite-circle generator node-list length theorem
- `GEN-T0021`: Lean-proved coil-orbit generator period-length theorem
- `GEN-T0022`: Lean-proved empty bounded-generator search candidate-count theorem
- `GEN-T0023`: Lean-proved empty bounded-generator search exact-candidate-count theorem
- `GEN-T0024`: Lean-proved empty bounded-generator search no-best-exact-candidate theorem
- `GEN-T0025`: Lean-proved bounded-generator best exact candidate belongs to the exact-candidate list
- `GEN-T0026`: Lean-proved bounded-generator best exact candidate belongs to the declared candidate search space
- `GEN-T0027`: Lean-proved bounded-generator best exact candidate satisfies exact regeneration
- `GEN-T0028`: Lean-proved bounded-generator no-best-exact iff exact-candidate list empty theorem
- `GEN-T0029`: Lean-proved bounded-generator no-best-exact iff exact-candidate count zero theorem
- `GEN-T0030`: Lean-proved bounded-generator best-exact presence implies positive exact-candidate count theorem
- `GEN-T0031`: Lean-proved singleton exact-search candidate-count theorem
- `GEN-T0032`: Lean-proved singleton exact-search exact-candidate-count theorem
- `GEN-T0033`: Lean-proved singleton exact-search best-exact candidate theorem
- `GEN-T0034`: Lean-proved singleton exact-search best candidate exact-regeneration theorem
- `GEN-T0035`: Lean-proved bounded-generator exact-candidate membership in the declared finite candidate list
- `GEN-T0036`: Lean-proved bounded-generator exact-candidate exact-regeneration theorem
- `GEN-T0037`: Lean-proved bounded-generator positive exact-candidate count iff some best exact candidate exists theorem
- `GEN-T0038`: Lean-proved singleton exact-search self-comparison membership in the exact-candidate list
- `GEN-T0039`: Lean-proved singleton exact-search self-comparison membership in the declared finite candidate list
- `GEN-T0040` through `GEN-T0043`: Lean-proved finite-circle generator exact node membership, no-duplicate, zero-empty, and positive-nonempty facts
- `S0-T0001`: the finite `S^0` opposition type has two points
- `S0-T0002`: the opposition antipode is involutive
- `S0-T0003`: the opposition antipode has no fixed point
- `S0-T0004`: the opposition antipode swaps the two named signs
- `S0-T0005`: the opposition antipode is bijective
- `S2-T0001`: suspended-circle cell counts
- `S2-T0002`: suspended-circle Euler characteristic
- `S2-T0003`: sphere-grid cell counts
- `S2-T0004`: sphere-grid Euler characteristic
- `S2-T0005`: latitude rings are finite circles
- `S2-T0006`: longitude rotation fixes poles
- `S2-T0007`: latitude coil period inherits the finite-circle period theorem
- `S2-T0017`: latitude-ring orbit count inherits the finite-circle gcd orbit theorem
- `S2-T0008`: suspended-circle antipode swaps the poles
- `S2-T0009`: suspended-circle antipode is involutive
- `S2-T0010`: suspended-circle antipode preserves the finite pole subset
- `S2-T0011`: suspended-circle antipode preserves the finite equator subset
- `S2-T0012`: longitude rotation preserves finite latitude coordinates
- `S2-T0013`: longitude rotation advances finite longitude coordinates by circle rotation
- `S2-T0014`: every suspended-circle point forms an antipodal pair with its antipode
- `S2-T0015`: the suspended-circle antipodal-pair relation is symmetric
- `S2-T0016`: suspended-circle antipode converts signed longitude rotation into opposite signed rotation
- `S2-T0018`: suspended-circle antipode is bijective
- `S2-T0019`: suspended-circle signed longitude rotations are bijective
- `S2-T0020`: finite sphere-grid longitude rotations are bijective
- `S3C-T0001`: suspended-surface cell counts
- `S3C-T0002`: suspended-surface Euler characteristic is zero when the surface has Euler characteristic two
- `S3C-T0003`: suspended-suspended-circle cell counts
- `S3C-T0004`: suspended-suspended-circle Euler characteristic
- `S3Q-T0001`: real quaternion norm-square primitive
- `S3Q-T0002`: unit quaternions are closed under multiplication
- `S3Q-T0003`: conjugation gives inverse equations for unit quaternions
- `S3Q-T0004`: quaternion multiplication is noncommutative by exact example
- `S3Q-T0005`: quaternion multiplication is associative
- `S3Q-T0006`: bundled unit quaternion identity laws
- `S3Q-T0007`: bundled unit quaternion conjugate inverse laws
- `S3Q-T0008`: bundled unit quaternion conjugation is involutive
- `S3H-T0001`: normalized Hopf pairs map to the unit base equation
- `S3H-T0002`: unit common phase preserves the Hopf base point
- `S3H-T0003`: unit phase orbits stay normalized and preserve the Hopf base point
- `S3H-T0004`: identity phase leaves every Hopf pair unchanged
- `S3H-T0005`: composed Hopf phase rotations follow complex multiplication
- `S3H-T0006`: Hopf phase action wrapper satisfies identity and composition laws
- `S3H-T0007`: Hopf phase multiplication has left and right identity
- `S3H-T0008`: Hopf phase multiplication is associative
- `S3S-T0001`: quaternion conjugation action is invariant under replacing `q` by `-q`
- `S3S-T0002`: identity quaternion conjugation fixes every input
- `S3S-T0003`: quaternion conjugation sends zero to zero
- `S3S-T0004`: unit-quaternion sign relation is an equivalence relation
- `S3S-T0005`: quaternion conjugation preserves pure-imaginary quaternion inputs
- `S456-T0001`: iterated finite suspensions give S4/S5/S6 Euler characteristics 2, 0, and 2
- `S4-T0001`: finite S4 suspension model has Euler characteristic 2
- `S4-T0002`: finite S4 counts are the suspension of finite S3 counts
- `S5-T0001`: finite S5 suspension model has Euler characteristic 0
- `S5-T0002`: finite S5 counts are the suspension of finite S4 counts
- `S6-T0001`: finite S6 suspension model has Euler characteristic 2
- `S6-T0002`: finite S6 counts are the suspension of finite S5 counts
- `S6-T0003`: S6 warning boundary marker is tied to `S6-W0001`
- `S7C-T0001`: finite S7 iterated-suspension model
- `S7C-T0002`: finite S7 iterated-suspension model has Euler characteristic 0
- `S7C-T0003`: finite S7 model is the suspension of finite S6 counts
- `S1O-T0001`: signed rotation by zero fixes every finite-circle node
- `S1O-T0002`: composing signed rotations adds signed strides
- `S1O-T0003`: signed rotation by `k` followed by `-k` returns to the start

Executable exploratory spine:

- `S3H-T0001`: coordinate Hopf map lands on the unit base equation for normalized pairs
- `S3H-T0002`: common unit-phase rotation preserves the Hopf base point in Lean and Python checks
- `S3H-T0003`: unit phase orbit preserves normalized Hopf pairs and their base point; sampled `2*pi` closure remains an executable analytic example
- `S7QH-T0001`: coordinate quaternionic Hopf map sends normalized quaternion pairs to the unit five-coordinate base equation
- `S7QH-T0002`: shared right unit-quaternion phase rotation preserves the quaternionic Hopf map
- `S7QH-T0003`: quaternionic right phase action composes and preserves the Hopf base point
- `S7QH-T0004`: quaternionic right phase scales pair norm by the phase norm
- `S7QH-T0005`: unit quaternionic right phase preserves pair norm
- `S7O-T0001` through `S7O-T0008`: bounded Cayley-Dickson basis, two-sided conjugate norm, norm multiplicativity, unit closure by norm, bracket-explicit norm-one conjugate inverse, noncommutativity, and nonassociativity facts in Lean
- `S15-T0001`: Lean roadmap marker for the octonionic Hopf horizon
- `S15-T0002`: finite S15 Euler theorem
- `S15-T0003`: bounded octonionic Hopf landing theorem
- `S15-T0004`: finite S15 model is the eightfold suspension of finite S7
- `S15-T0009`: finite eightfold suspension preserves Euler characteristic
- `S15-T0005` through `S15-T0008`: safe octonionic right-phase landing facts plus a counterexample showing naive full-coordinate right-phase invariance is false in the bounded model

## What This Does Not Claim Yet

This repository does not currently claim to have rebuilt all of mathematics from circles. It contains a verified starting spine and an explicit roadmap for growing it.

It also does not claim that Python tests are proofs, that diagrams are proofs, that `S^2` has a natural group structure, that `S^3` is globally `S^2 x S^1`, that unit octonions form a group, or that formalization bypasses foundational limitations. See `docs/GODEL_AND_LIMITATIONS.md` for the current limitations note.

For the active application and compute tracks, see `docs/PHASE2_AND_APPLICATIONS.md`. Local compute experiments should be MLX/Mac-first; CUDA-specific references are portability notes or external benchmark baselines.

For the interactive explanation layer, see `docs/LIVING_BOOK_POLICY.md`, `docs/LIVING_BOOK_ROADMAP.md`, and `docs/LIVING_BOOK_WIDGETS.md`. The Living Book must derive theorem status from manifests and must not treat widgets, diagrams, or Python examples as proofs.
