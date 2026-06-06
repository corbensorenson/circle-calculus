# Circle Calculus

Circle Calculus is a staged paper-and-proof corpus for rebuilding familiar mathematical structures from finite circular address spaces, rotations, coils, winding, lifted arithmetic, and eventually a dimension-indexed sphere ladder.

The long-term aim is not just to write essays. The aim is to keep every serious concept tied to:

- a human-readable paper in `papers/`,
- Lean 4/mathlib declarations in `Circle/` and paper-specific Lean sidecars in `sidecars/`,
- executable Python reference models in `circle_math/`,
- a shared dictionary in `dictionary/circle_dictionary.yaml`, and
- theorem metadata in `manifests/theorem_manifest.yaml`.

The Phase IV wide/deep theorem-target audit is tracked in `manifests/phase4_theorem_targets.yaml` and validated by `scripts/check_phase4_targets.py`.

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

The current proved layer includes `S^1` finite circles, rotations, coils, period, orbit decomposition, same-orbit quotient membership, prime full coils, full-coil iff coprime, winding, lifted natural-number arithmetic, scaling invertibility, scale-factor normalization, scaling-to-coil image bridge, prime-circle scaling, divisor/cofactor scaling collapse, period-kernel collapse, period-normal scaling representatives, period-congruence scaled equality, bounded period-representative injectivity, period-representative image cardinality and membership, whole-circle scaling image equality and cardinality, canonical kernel/fiber representative equality and cardinality, zero-fiber/kernel and scaled-target/fiber bridges, fiber-set equality modulo scaled value and stride period, arbitrary target-fiber emptiness/cardinality, image-times-fiber and image-times-kernel scaling factorizations, kernel-subgroup membership, cofactor-shift collapse, exact scaling-zero and period-divisibility criteria, scaled-address equality congruence, coprime scaling reflection, and signed reversible rotation; `S^0` two-point opposition; common finite-cell suspension/Euler machinery; the first `S^2` suspended-circle, sphere-grid, antipode, pole/equator subset, latitude/longitude coordinate, and antipodal-pair theorem spine; the finite combinatorial `S^3` suspension theorem spine; the core `S^3` real-quaternion algebra spine; the first `S^3` Hopf coordinate and phase-action spine; the first `S^3` spin sign-cancellation theorem; the finite `S^4` through `S^6` suspension-count and Euler bridge; the finite topological `S^7` suspension-count and Euler model; the first Phase II finite stable-sphere, period-8 clock, trivial-bundle, directed-boundary, and proof-glyph certificate seeds; and the first application finite phase-coordinate, cyclic-address, direction-bin, stride-address, round-robin schedule, and Circle AI indexing seeds.

Future dimensional work is split into two related ladders:

- Geometric ladder: `S^0`, `S^1`, `S^2`, `S^3`, `S^4`, `S^5`, `S^6`, `S^7`.
- Algebraic ladder: `S^0` signs, `S^1` unit complex phase, `S^3` unit quaternions, `S^7` unit octonions.

The repository rule for that expansion is strict: higher dimensions may depend on lower dimensions, but lower dimensions must not import or rely on higher dimensions. The first dimensional implementation stage should be scaffolding only: dimension manifests, dictionary files, paper folders, Lean/Python roots, and import-check scripts, with all future theorem statuses kept planned, deferred, or exploratory until proofs exist.

See `docs/COMPLETION_ROADMAP.md`, `docs/DIMENSIONAL_LADDER.md`, `docs/PHASE2_AND_APPLICATIONS.md`, `docs/GITHUB_PAGES.md`, and `circle_calculus_dimensional_handoff/` for the detailed roadmap and guardrails.

## Current Status

This is an early public research scaffold with a working verification pipeline and a growing dimension-indexed theorem spine.

| Paper | Status | Formal spine |
| --- | --- | --- |
| `papers/PAPER_01_FINITE_CIRCLES.md` | polished draft | `CC-T0001` through `CC-T0007` plus `CC-T0054`, `CC-T0055`, and `CC-T0059` through `CC-T0061` proved |
| `papers/PAPER_02_WINDING_NATURALS.md` | polished draft | `CC-T0009` through `CC-T0016` proved |
| `papers/S1/PAPER_S1_01_FINITE_CIRCLES.md` | polished dimension guide draft | `CC-T0001` through `CC-T0007` plus `CC-T0054`, `CC-T0055`, and `CC-T0059` through `CC-T0061` linked in dimension layout |
| `papers/S1/PAPER_S1_02_WINDING_NATURALS.md` | polished dimension guide draft | `CC-T0009` through `CC-T0016` linked in dimension layout |
| `papers/S1/PAPER_S1_03_INTEGERS_ORIENTATION.md` | polished draft | `S1O-T0001` through `S1O-T0003` proved with Python examples |
| `papers/S1/PAPER_S1_04_FACTORS_SCALING_PRIME_COILS.md` | polished draft | `CC-T0008`, `CC-T0017` through `CC-T0054`, and `CC-T0056` through `CC-T0058` proved |
| `papers/S0/PAPER_S0_01_TWO_POINT_OPPOSITION.md` | polished draft | `S0-T0001` through `S0-T0004` proved with Python examples |
| `papers/S2/PAPER_S2_01_SUSPENDED_CIRCLES.md` | polished draft | `S2-T0001` and `S2-T0002` proved with Python examples |
| `papers/S2/PAPER_S2_02_SPHERE_GRIDS_LATITUDE_COILS.md` | polished draft | `S2-T0003` through `S2-T0007` and `S2-T0017` proved with Python examples |
| `papers/S2/PAPER_S2_03_ANTIPODES_AXES_SURFACE_CLOSURE.md` | polished draft | `S2-T0008` through `S2-T0016` proved with Python examples |
| `papers/S3/PAPER_S3_01_FINITE_HYPERSPHERES.md` | polished draft | `S3C-T0001` through `S3C-T0004` proved with Python examples |
| `papers/S3/PAPER_S3_02_QUATERNION_COILS.md` | polished draft | `S3Q-T0001` through `S3Q-T0007` proved with Python examples |
| `papers/S3/PAPER_S3_03_HOPF_COILS.md` | polished draft/proved spine | `S3H-T0001` through `S3H-T0006` are Lean-proved bounded Hopf coordinate and phase-action facts; full fibration topology remains future work |
| `papers/S3/PAPER_S3_04_SPIN_DOUBLE_COVER_ROADMAP.md` | polished draft | `S3S-T0001` through `S3S-T0004` proved with Python examples |
| `papers/S4_S6/PAPER_S456_01_GENERAL_SUSPENSION_EULER_PARITY.md` | polished draft | `COMMON-T0001` through `COMMON-T0005` and `S456-T0001` proved with Python examples |
| `papers/S4_S6/PAPER_S4_01_BASE_OF_QUATERNIONIC_HOPF.md` | polished draft | `S4-T0001` and `S4-T0002` proved with Python examples |
| `papers/S4_S6/PAPER_S5_01_COMPLEX_PROJECTIVE_BRIDGE.md` | polished draft | `S5-T0001` and `S5-T0002` proved with Python examples |
| `papers/S4_S6/PAPER_S6_01_OCTONION_SHADOW_AND_WARNINGS.md` | polished draft | `S6-T0001` through `S6-T0003` proved with Python examples; `S6-W0001` warning tracked |
| `papers/S7/PAPER_S7_01_TOPOLOGICAL_7SPHERE.md` | polished draft | `S7C-T0001` through `S7C-T0003` proved with Python examples |
| `papers/S7/PAPER_S7_02_QUATERNIONIC_HOPF_FIBRATION.md` | polished draft/partial proof | `S7QH-T0001` through `S7QH-T0003` are Lean-proved coordinate theorems; full fibration topology remains future work |
| `papers/S7/PAPER_S7_03_OCTONIONIC_UNITS_AND_NONASSOCIATIVE_COILS.md` | polished draft/proved spine | `S7O-T0001` through `S7O-T0008` are Lean-proved in a bounded Cayley-Dickson coordinate model |
| `papers/future/S15/PAPER_S15_01_OCTONIONIC_HOPF_ROADMAP.md` | polished draft/partial proof | `S15-T0001` is a Lean roadmap marker; `S15-T0002` through `S15-T0008` are Lean-proved topological, coordinate landing, safe right-phase, and warning-boundary facts with Python examples |
| `papers/phase2/PAPER_P2_01_STABLE_SPHERE_CALCULUS.md` | polished draft/proved finite seed | `P2S-T0001` through `P2S-T0003` are Lean-proved double/four suspension facts with Python examples |
| `papers/phase2/PAPER_P2_02_BOTT_CLIFFORD_PERIODICITY.md` | polished draft/proved finite seed | `P2B-T0001` through `P2B-T0003` are Lean-proved period-8 clock facts with Python examples; Bott/Clifford periodicity remains future work |
| `papers/phase2/PAPER_P2_03_BUNDLE_CALCULUS.md` | polished draft/proved trivial seed | `P2BU-T0001` through `P2BU-T0004` are Lean-proved product-bundle projection/fiber facts with Python examples |
| `papers/phase2/PAPER_P2_04_BOUNDARY_COBORDISM_CALCULUS.md` | polished draft/proved finite seed | `P2BC-T0001` through `P2BC-T0004` are Lean-proved directed-interval boundary facts with Python examples |
| `papers/phase2/PAPER_P2_05_PROOF_CARRYING_GLYPHS.md` | polished draft/proved certificate seed | `P2G-T0001` through `P2G-T0003` are Lean-proved proof-glyph projection facts with Python examples |
| `papers/applications/PAPER_APP_01_COIL_DATA_ANALYSIS.md` | polished draft/proved finite seed | `APPD-T0001` through `APPD-T0003` are Lean-proved phase-coordinate facts with Python examples |
| `papers/applications/PAPER_COMP_01_PROOF_CARRYING_CIRCULAR_COMPUTATION.md` | polished draft/proved finite seed | `COMPC-T0001` through `COMPC-T0003` are Lean-proved cyclic-address facts with Python examples |
| `papers/applications/PAPER_COMP_02_COIL_RAY_AND_SAMPLING.md` | polished draft/proved finite seed | `COMPR-T0001` through `COMPR-T0003` are Lean-proved direction-bin schedule facts with Python examples |
| `papers/applications/PAPER_COMP_03_COIL_LAYOUT_STENCIL_NTT.md` | polished draft/proved finite seed | `COMPL-T0001` through `COMPL-T0004` are Lean-proved stride-address facts with Python examples and a starter CoilLayout benchmark harness |
| `papers/applications/PAPER_COMP_04_COIL_SYSTEMS_APPLICATIONS.md` | polished draft/proved finite seed | `COMPS-T0001` through `COMPS-T0003` are Lean-proved round-robin schedule facts with Python examples |
| `papers/applications/PAPER_AI_01_CIRCLE_AI_ARCHITECTURES.md` | polished draft/proved finite seed | `AIA-T0001` through `AIA-T0003` are Lean-proved phase-channel facts with Python examples |
| `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md` | polished draft/proved finite seed | `AIM-T0001` through `AIM-T0003` are Lean-proved cyclic-memory-slot facts with Python examples |
| `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md` | polished draft/proved finite seed | `AIRA-T0001` through `AIRA-T0003` are Lean-proved adapter-block facts with Python examples |

The theorem manifest also includes `CC-T0008`, `CC-T0017` through `CC-T0054`, and `CC-T0056` through `CC-T0058`, proving the first scaling/full-coil/affine spine: invertibility iff coprime, scale-by-zero collapse, scale-by-one identity, scaling composition, scale-factor congruence normalization, scaling transport of rotation stride, scaling transport of finite coil steps, the scaling-to-coil image bridge, bijectivity of nonzero scaling on prime circles, divisor-cofactor collapse to zero, cofactor-multiple collapse to zero, period-multiple collapse to zero, cofactor-shift and period-shift address collapse, period-normal representatives, period-congruence scaled equality, bounded period-representative injectivity, period-representative image cardinality and membership, whole-circle scaling image equality and cardinality, canonical kernel/fiber representative equality and gcd cardinality, zero-fiber/kernel and scaled-target/fiber bridges, fiber-set equality modulo scaled value and stride period, arbitrary target-fiber emptiness/cardinality, image-times-fiber and image-times-kernel scaling factorizations, kernel-subgroup membership, the exact divisibility and period-divisibility criteria for scaling to zero, the exact product-congruence criterion for scaled-address equality, coprime reflection of address congruence, full-coil iff coprime, rotation bijectivity, affine composition normal form, and coprime affine bijectivity.

The D0 dimensional scaffold is also in place: dimension manifests, dimension dictionaries, planned paper stubs, Lean/Python scaffolds, and dimension validation scripts. Future-dimension claims remain planned, deferred, exploratory, or stated until actual Lean proofs exist.

Phase II and application scaffolds are also in place under `papers/phase2/`, `papers/applications/`, `manifests/theories/`, and `manifests/applications/`. `PAPER_P2_01_STABLE_SPHERE_CALCULUS` through `PAPER_P2_05_PROOF_CARRYING_GLYPHS`, `PAPER_APP_01_COIL_DATA_ANALYSIS`, `PAPER_COMP_01` through `PAPER_COMP_04`, and `PAPER_AI_01` through `PAPER_AI_03` now have proved seeds. The 2026-06-05 compute-applications handoff is preserved in `docs/PHASE2_AND_APPLICATIONS.md` and `circle_calculus_codex_handoff/source_logs/04_compute_applications_browser_note.md`. Benchmark claims remain benchmark work, not proof claims.

Phase III is now implemented as the first Circle Calculus Living Book milestone: a Quarto-based interactive explainer site generated from manifests, dictionary entries, papers, Python reference models, and Lean proof metadata. Its policy and roadmap live in `docs/LIVING_BOOK_POLICY.md`, `docs/LIVING_BOOK_ROADMAP.md`, and `docs/LIVING_BOOK_WIDGETS.md`; the source browser handoff is archived at `circle_calculus_codex_handoff/source_logs/05_living_book_browser_note.md`. The Living Book is an explanation layer, not a proof layer.

The next project phases are intentionally wide and deep: Phase IV audits every dimensional level and application area for missing theorem targets, paper improvements, and stronger proof spines; Phase V searches edge problem spaces where Circle Calculus may provide leverage that is hard, awkward, or unavailable in ordinary presentations; Phase VI sweeps the whole corpus so the writing is cleaner, the claims are more correct, and the proof-status links are easy for outsiders to consume.

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
make dictionary  # validate dictionary metadata
make papermanifest # validate paper-to-sidecar/theorem/dictionary links
make paperlinks  # verify papers cite known theorem ids
make phase4targets # validate the wide/deep theorem target registry
make dimensioncheck # validate dimension manifests, imports, and paper links
make nofake      # reject forbidden proof placeholders
make examples    # regenerate current example diagrams
make site-data   # export Living Book JSON from manifests/dictionaries/papers
make sitecheck   # validate Living Book structure, ids, links, status, and widgets
make site-render # render the Quarto Living Book into site/_site
make living-book-check # run core checks plus Living Book checks and render
make check       # run the full suite
```

## License And Citation

Circle Calculus is released under the MIT License. You can use, copy, modify, publish, and build on the repository freely as long as the copyright and license notice stay with substantial reused portions.

If you use this project in a paper, post, dataset, codebase, or derivative research artifact, please cite Corben Sorenson and the public repository. GitHub and citation tools can read the recommended citation from `CITATION.cff`.

## How To Read The Project

Start with:

1. `papers/PAPER_01_FINITE_CIRCLES.md`
2. `sidecars/PAPER_01_FINITE_CIRCLES/lean/Paper01.lean`
3. `papers/PAPER_02_WINDING_NATURALS.md`
4. `sidecars/PAPER_02_WINDING_NATURALS/lean/Paper02.lean`
5. `dictionary/circle_dictionary.yaml`
6. `manifests/theorem_manifest.yaml`
7. `docs/COMPLETION_ROADMAP.md`
8. `docs/DIMENSIONAL_LADDER.md`
9. `docs/PHASE2_AND_APPLICATIONS.md`
10. `docs/LIVING_BOOK_ROADMAP.md`
11. `site/index.qmd`
12. `site/status.qmd`
13. `site/dictionary.qmd`
14. `site/theorems.qmd`
15. `site/papers.qmd`
16. `site/targets.qmd`

The papers give the conceptual path. The sidecars show the proof links. The dictionary fixes vocabulary so later papers reuse the same meanings instead of drifting.

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
- `P2S-T0001`: finite double suspension preserves Euler characteristic
- `P2S-T0002`: finite four-suspension iteration preserves Euler characteristic
- `P2S-T0003`: finite four-suspension counts are two double-suspension steps
- `P2B-T0001`: finite period-8 dimension clock index is below 8
- `P2B-T0002`: finite period-8 dimension clock is invariant under adding 8
- `P2B-T0003`: finite period-8 dimension clock sends zero to zero
- `P2BU-T0001`: trivial-bundle projection returns the base coordinate
- `P2BU-T0002`: trivial-bundle fiber coordinate returns the fiber value
- `P2BU-T0003`: trivial-bundle projection is invariant under changing only the fiber
- `P2BU-T0004`: trivial-bundle fiber coordinate is invariant under changing only the base
- `P2BC-T0001`: point-boundary after interval-boundary is zero in the directed-interval seed
- `P2BC-T0002`: reversing a directed interval negates its boundary
- `P2BC-T0003`: reversing a directed interval twice returns it
- `P2BC-T0004`: a constant directed interval has zero boundary
- `P2G-T0001`: proof glyph certificate exposes its theorem id
- `P2G-T0002`: proof glyph certificate exposes its Lean declaration name
- `P2G-T0003`: proof glyph certificate exposes its glyph id
- `APPD-T0001`: finite phase coordinate is bounded by a positive period
- `APPD-T0002`: finite phase coordinate closes after adding one full period
- `APPD-T0003`: finite phase coordinate at zero is zero
- `COMPC-T0001`: cyclic address is bounded by a positive circular buffer size
- `COMPC-T0002`: cyclic address is unchanged after adding one full buffer size
- `COMPC-T0003`: cyclic address at zero is zero
- `COMPR-T0001`: direction-bin schedule is bounded by a positive bin count
- `COMPR-T0002`: direction-bin schedule closes after one full pass through the bins
- `COMPR-T0003`: direction-bin schedule at zero is zero
- `COMPL-T0001`: stride address is bounded by a positive circular size
- `COMPL-T0002`: stride address closes after one full pass through the circular step horizon
- `COMPL-T0003`: zero step has zero stride address
- `COMPL-T0004`: zero stride has zero stride address
- `COMPS-T0001`: round-robin slot schedule is bounded by a positive slot count
- `COMPS-T0002`: round-robin slot schedule closes after one full pass through the slots
- `COMPS-T0003`: round-robin slot schedule at zero is zero
- `AIA-T0001`: AI phase channel is bounded by a positive period
- `AIA-T0002`: AI phase channel closes after one full period
- `AIA-T0003`: AI phase channel at zero is zero
- `AIM-T0001`: cyclic memory slot is bounded by a positive bank size
- `AIM-T0002`: cyclic memory slot closes after one full bank pass
- `AIM-T0003`: cyclic memory slot at zero is zero
- `AIRA-T0001`: adapter block index is bounded by a positive block size
- `AIRA-T0002`: adapter block index closes after one full block pass
- `AIRA-T0003`: adapter block index at zero is zero
- `S0-T0001`: the finite `S^0` opposition type has two points
- `S0-T0002`: the opposition antipode is involutive
- `S0-T0003`: the opposition antipode has no fixed point
- `S0-T0004`: the opposition antipode swaps the two named signs
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
- `S3H-T0001`: normalized Hopf pairs map to the unit base equation
- `S3H-T0002`: unit common phase preserves the Hopf base point
- `S3H-T0003`: unit phase orbits stay normalized and preserve the Hopf base point
- `S3H-T0004`: identity phase leaves every Hopf pair unchanged
- `S3H-T0005`: composed Hopf phase rotations follow complex multiplication
- `S3H-T0006`: Hopf phase action wrapper satisfies identity and composition laws
- `S3S-T0001`: quaternion conjugation action is invariant under replacing `q` by `-q`
- `S3S-T0002`: identity quaternion conjugation fixes every input
- `S3S-T0003`: quaternion conjugation sends zero to zero
- `S3S-T0004`: unit-quaternion sign relation is an equivalence relation
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
- `S7O-T0001` through `S7O-T0008`: bounded Cayley-Dickson basis, two-sided conjugate norm, norm multiplicativity, unit closure by norm, bracket-explicit norm-one conjugate inverse, noncommutativity, and nonassociativity facts in Lean
- `S15-T0001`: Lean roadmap marker for the octonionic Hopf horizon
- `S15-T0002`: finite S15 Euler theorem
- `S15-T0003`: bounded octonionic Hopf landing theorem
- `S15-T0004`: finite S15 model is the eightfold suspension of finite S7
- `S15-T0005` through `S15-T0008`: safe octonionic right-phase landing facts plus a counterexample showing naive full-coordinate right-phase invariance is false in the bounded model

## What This Does Not Claim Yet

This repository does not currently claim to have rebuilt all of mathematics from circles. It contains a verified starting spine and an explicit roadmap for growing it.

It also does not claim that Python tests are proofs, that diagrams are proofs, that `S^2` has a natural group structure, that `S^3` is globally `S^2 x S^1`, that unit octonions form a group, or that formalization bypasses foundational limitations. See `docs/GODEL_AND_LIMITATIONS.md` for the current limitations note.

For the deferred application and compute tracks, see `docs/PHASE2_AND_APPLICATIONS.md`. Local compute experiments should be MLX/Mac-first; CUDA-specific references are future portability notes or external benchmark baselines.

For the planned interactive explanation layer, see `docs/LIVING_BOOK_POLICY.md`, `docs/LIVING_BOOK_ROADMAP.md`, and `docs/LIVING_BOOK_WIDGETS.md`. The Living Book must derive theorem status from manifests and must not treat widgets, diagrams, or Python examples as proofs.
