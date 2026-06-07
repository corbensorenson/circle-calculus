# Circle Calculus Living Book Roadmap

The Living Book is Phase III of the project: a public-facing Quarto website/e-textbook generated from papers, theorem manifests, dictionary entries, Lean proof metadata, and Python reference models.

Current milestone status as of 2026-06-06: Phase 0 and the first S1 interactive source milestone are implemented, including a theorem-status legend, generated dictionary/theorem/paper/target/glyph indexes, and searchable dictionary backlinks into theorem, paper, widget, and glyph usage. Higher dimensions, `S15`, Phase II, and applications are active roadmap tracks rather than parked ideas: pages exist, proved finite spines are linked where available, and topology/application claims remain marked as planned, exploratory, deferred, or blocked until formal evidence exists.

## Phase 0: Skeleton And Data

- Create `site/` with `_quarto.yml`, `index.qmd`, `about.qmd`, and `roadmap.qmd`.
- Add Quarto sidebar navigation.
- Add `site/assets/css/living-book.css`.
- Add generated data under `site/data/generated/`.
- Implement `scripts/site/export_site_data.py`.
- Add theorem, dictionary, paper, dimension, and widget indexes.
- Add status badge, theorem box, dictionary box, warning box, Lean link, Python example, and dimension banner components.

## Phase 1: S1 Interactive Core

Required chapters:

- `site/chapters/S1/index.qmd`
- `site/chapters/S1/01_finite_circles.qmd`
- `site/chapters/S1/02_rotation_as_addition.qmd`
- `site/chapters/S1/03_coils_orbits_closure.qmd`
- `site/chapters/S1/04_period_gcd_prime_full_coils.qmd`
- `site/chapters/S1/05_winding_lift.qmd`

Required widgets:

- `finite_circle_rotator`
- `rotation_composition`
- `coil_orbit_explorer`
- `period_gcd_visualizer`
- `prime_full_coil_explorer`
- `winding_lift_explorer`

Each chapter must distinguish intuition, example, Python model, and formal theorem. Theorem boxes and status badges must pull from generated manifest data.

## Phase 1.5: Public Access And Navigation Polish

- Publish the static Quarto render through GitHub Pages from the checked `main` branch.
- Keep `site/_site/` out of git and deploy it as a generated artifact.
- Gate deployment on Lean proof build, manifest checks, dictionary checks, paper checks, no-fake-proof checks, widget parity, and Quarto render.
- Make dictionary, theorem, paper, target, and glyph indexes filterable and source-linked.
- Show dictionary backlinks generated from manifests rather than hand-written duplicate lists.
- Visually check the S1 widgets on desktop and mobile before claiming the Living Book is reader-grade.

## Phase 1.6: Guided Textbook Pass

- Treat the Living Book as a book first and an index second.
- Add a front-of-book learning toolkit before S0/S1 so readers can review objects, addresses, rules, composition, iteration, invariants, evidence layers, and proof status before entering the technical chapters.
- Put the easiest building-block concepts first: finite addresses, nodes, rotation, repeated rotation, closure, gcd/period, primes, and winding.
- Make the sidebar and navbar lead readers through the learning sequence before exposing dictionary/theorem/paper/target indexes.
- Keep reference pages available as appendices, not as substitutes for chapters.
- Give each reader-facing lesson a goal, plain-language explanation, interactive diagram or widget when available, short learner task, checkpoint, and source trail.
- Keep theorem cards, dictionary boxes, paper links, Lean links, and Python examples close to the lesson they support, but do not let them replace the lesson.
- Prefer the lesson order `Lesson 0 toolkit -> S0 -> S1 finite addresses -> rotation -> coils -> period/gcd/primes -> winding -> S2/S3/higher dimensions -> Phase II -> applications`.
- Add worked examples and common-mistake notes to mature lessons so a reader can learn from the page without leaving it.
- Use indexes as reference shelves, not as the main reading experience.
- Add review/exercise pages at the end of mature units so readers can test the combined concept sequence before moving upward.
- Add guided paths for higher dimensions and applications as those pages mature, always preserving proof-status boundaries.

## Phase 2: S2 Interactives

- Add suspended-circle pages.
- Add sphere-grid pages.
- Keep continuous geometry claims future until formalized.
- Use placeholders until widgets and proof links exist.

## Phase 3: S3 Exploratory Pages

- Add finite hypersphere, quaternion, Hopf, and spin pages.
- Link proved quaternion and bounded Hopf coordinate facts.
- Keep quotient topology and full fibration claims future unless formalized.

## Phase 4: S4-S6, S7, And S15 Active Horizon Pages

- Add S4-S6 suspension/Euler parity pages.
- Add S7 topological, quaternionic Hopf, and octonion warning pages.
- Add and expand the S15 Hopf horizon page as active finite-seed and warning-boundary work.
- Keep exceptional and horizon topics visibly scoped: active does not mean proved.

## Phase 5: Applications

- Add AI, compute, rendering, systems, and data-analysis pages.
- Treat application pages as active proof/benchmark target tracks, not as indefinitely deferred notes.
- Keep benchmark claims separate from Lean proofs.
- Use MLX/Mac-first language for local compute work.
- Add Phase VII physics/generative-structure lessons from the first bounded fixtures: finite gauge loops, holonomy, Hopf hidden phase, spin sign ambiguity, periodic dynamics, winding defects, seed-rule provenance, generator comparison, and proof-carrying generated diagrams.

## Dedicated Circle AI Deep Program

- Treat Circle AI as a dedicated active program, not just one application page.
- Explore phase channels, cyclic memory, coil/sparse attention, looped/recursive transformer schedules, token-level and middle-block recurrence, multi-resolution recurrence, learned recurrence schedules, training-free loop wrappers, adapter blocks, circulant mixers, RoPE and MultiCoil positional structure, recurrent state, harmonic features, geometry-aware models, proof-carrying model components, and MLX/Mac-compatible prototypes.
- For each AI avenue, keep four lanes separate: Lean-proved finite safety/indexing facts, Python/MLX executable fixtures, benchmark comparisons against ordinary AI baselines, and speculative research hypotheses.
- Include looped/recursive transformer schedules as a specific AI lesson lane: loop phase, recurrence budget, token-level active set, selected loop block, resolution level, exit certificate, score trace, overthinking guardrail, and ordinary recursive-transformer baselines.
- Require negative controls for positive periodic fixtures, especially nonperiodic tasks where circular structure should not help.
- Report quality, runtime, memory, parameter count, and interpretability separately.
- Do not claim model improvement, attention replacement, parameter efficiency, or speed without a reproducible benchmark artifact and clear baseline.
- Link AI proof cards, dictionary terms, papers, benchmark fixtures, and future widgets into the Living Book so readers can distinguish proved address structure from empirical claims.
- Build the AI Living Book path as lessons, not a link farm: phase channels -> learned-feature baselines -> harmonic/Fourier features -> backend parity -> cyclic memory -> coil retrieval -> content-gated retrieval -> looped recurrence schedules -> loop-exit certificates -> token-level recurrence routing -> learned token-level recurrence routing -> training-free loop wrappers -> middle-block recurrence -> learned middle-block recurrence -> multi-resolution recurrence -> learned multi-resolution recurrence -> learned recurrence schedules -> adapters -> circulant mixers -> MultiCoil positions -> RoPE relative phase -> learned model baselines -> MLX prototypes -> geometry-aware AI.
- Each mature AI lesson should show the ordinary baseline, the circular hypothesis, the Lean-proved boundary, the Python/MLX fixture, the benchmark status, and the limitation before linking to the source files.
- Current benchmark anchors are `AIA-B0001`, `AIA-B0002`, `AIA-B0003`, `AIA-B0004`, `AIA-B0005`, `AIM-B0001`, `AIM-B0002`, `AIM-B0003`, `AIM-B0004`, `AIM-B0005`, `AIM-B0006`, `AIM-B0007`, `AIM-B0008`, `AIM-B0009`, `AIM-B0010`, `AIM-B0011`, `AIM-B0012`, `AIM-B0013`, `AIM-B0014`, `AIRA-B0001`, `AIRA-B0002`, `AIRA-B0003`, `AIRA-B0004`, and `AIRA-B0005`; they are scaffolds for phase, learned-feature baselines, harmonic/Fourier-feature baselines, backend parity, memory, coil-retrieval reachability, content-gated retrieval routing, learned content-gate retrieval routing, looped-recurrence schedules, loop-exit certificates, token-level recurrence routing, learned token-level recurrence routing, training-free loop-wrapper controls, middle-block recurrence controls, learned middle-block recurrence controls, multi-resolution recurrence controls, learned multi-resolution recurrence controls, learned recurrence-schedule controls, adapter-block, adapter parameter-budget accounting, circulant mixer validation, MultiCoil/RoPE-style positional structure, and RoPE-style relative phase, not model-quality results. The current interactive AI lessons cover cyclic memory, coil retrieval, content-gated retrieval, loop budgets, token-level recurrence routing, learned token-level recurrence routing, learned middle-block recurrence routing, MultiCoil phase, RoPE relative phase, adapter parameter accounting, and circulant mixer validation.

## Phase 6: Optional Manim Embedding

- Defer Manim-generated media until the static site and S1 widgets are stable.
- Embedded media must point back to theorem/status sources.

## Phase 7: Optional Live Python

- Evaluate JupyterLite, Thebe, or other live-code layers later.
- Live Python is optional and must not be required for core S1 widgets.

## Phase 8: Optional Lean Web Links

- Add Lean Web deep links or embedded snippets for selected small theorems.
- Lean Web is educational; local `lake build` remains the formal verification command.

## Main Project Phase VII: Physics And Generative Structure

The Living Book should teach the Phase VII roadmap as a guided path, not as a target table alone:

```text
finite gauge loops -> holonomy -> Hopf hidden phase -> spin sign ambiguity -> periodic dynamics -> winding defects -> minimal generators -> generator provenance -> proof-carrying generative diagrams
```

Each mature lesson must show the ordinary baseline, the Circle Calculus representation, the proof boundary, the executable fixture, the limitation, and then the source links. Physics pages must not imply a proved continuum model, and generator pages must not call a generator minimal without an explicit criterion and search space.

## First Milestone Acceptance Criteria

- [x] `site/` exists as a Quarto project.
- [x] `site/index.qmd` renders.
- [x] S1 chapters 01 through 04 exist.
- [x] S1 widgets `finite_circle_rotator`, `rotation_composition`, `coil_orbit_explorer`, `period_gcd_visualizer`, and `prime_full_coil_explorer` exist.
- [x] Site data exports from manifests and dictionary files.
- [x] Theorem boxes and dictionary boxes display generated data.
- [x] Status badges derive from manifest status.
- [x] `sitecheck` passes.
- [x] `quarto render site` succeeds.
- [x] Existing Lean, pytest, manifest, dictionary, paper, and dimension checks still pass after the Living Book commit.
