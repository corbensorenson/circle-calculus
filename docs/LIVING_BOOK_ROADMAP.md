# Circle Calculus Living Book Roadmap

The Living Book is Phase III of the project: a public-facing Quarto website/e-textbook generated from papers, theorem manifests, dictionary entries, Lean proof metadata, and Python reference models.

Current milestone status as of 2026-06-05: Phase 0 and the first S1 interactive source milestone are implemented. Higher dimensions and applications are scaffolded as placeholders only.

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

## Phase 2: S2 Interactives

- Add suspended-circle pages.
- Add sphere-grid pages.
- Keep continuous geometry claims future until formalized.
- Use placeholders until widgets and proof links exist.

## Phase 3: S3 Exploratory Pages

- Add finite hypersphere, quaternion, Hopf, and spin pages.
- Link proved quaternion and bounded Hopf coordinate facts.
- Keep quotient topology and full fibration claims future unless formalized.

## Phase 4: S4-S6, S7, And S15 Roadmap Pages

- Add S4-S6 suspension/Euler parity pages.
- Add S7 topological, quaternionic Hopf, and octonion warning pages.
- Add S15 future Hopf horizon page.
- Keep exceptional and future topics visibly scoped.

## Phase 5: Applications

- Add AI, compute, rendering, systems, and data-analysis pages.
- Keep benchmark claims separate from Lean proofs.
- Use MLX/Mac-first language for local compute work.

## Phase 6: Optional Manim Embedding

- Defer Manim-generated media until the static site and S1 widgets are stable.
- Embedded media must point back to theorem/status sources.

## Phase 7: Optional Live Python

- Evaluate JupyterLite, Thebe, or other live-code layers later.
- Live Python is optional and must not be required for core S1 widgets.

## Phase 8: Optional Lean Web Links

- Add Lean Web deep links or embedded snippets for selected small theorems.
- Lean Web is educational; local `lake build` remains the formal verification command.

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
