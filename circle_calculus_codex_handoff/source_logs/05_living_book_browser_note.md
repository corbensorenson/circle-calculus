# 2026-06-05 Living Book Browser Handoff

This source log preserves the browser discussion that introduced Phase III: the Circle Calculus Living Book.

## Core Request

Build the Circle Calculus Living Book: a Quarto-based interactive explainer website/e-textbook generated from the existing repository, theorem manifests, dictionary entries, papers, Python reference models, and Lean proof metadata.

Purpose:

- create a public-facing interactive explanation layer;
- let readers change parameters and watch circles/coils update;
- connect explanations to theorem ids, Lean declarations, Python examples, paper sections, and dictionary entries;
- keep the site downstream of formal project artifacts rather than a separate hand-written website.

## Source-Of-Truth Rule

- Theorem manifests remain the source of truth for proof status.
- Lean remains the formal proof source.
- Python remains the executable reference/modeling layer.
- The site is an explanation and interaction layer, not a proof layer.

No page, theorem box, widget caption, status badge, or chapter text may present a theorem as proved unless the theorem id is marked `proved` or `lean_proved` in the relevant theorem manifest and resolves to a compiled Lean declaration with no forbidden proof shortcuts.

## Architecture Notes

Use Quarto as the main website/book framework.

Use:

- Quarto `.qmd` files for chapters;
- static HTML/SVG/JavaScript widgets for first S1 interactives;
- Python scripts to export site data from manifests, dictionary, and papers;
- Python reference models for examples and parity tests;
- Lean source/proof links as the first proof-integration layer.

Do not require a live Python server for core interactivity. The first version must work as a static site on GitHub Pages.

Do not add a heavy frontend framework. Do not implement Manim, TTS, narration, video rendering, or a long movie in the first Living Book goal.

## Planned Site Structure

```text
site/
  _quarto.yml
  index.qmd
  about.qmd
  roadmap.qmd
  chapters/
    S0/
    S1/
    S2/
    S3/
    S4_S6/
    S7/
    S15/
    phase2/
    applications/
  components/
  widgets/
  data/generated/
  assets/css/living-book.css

scripts/site/
tests/site/
docs/LIVING_BOOK_POLICY.md
docs/LIVING_BOOK_ROADMAP.md
docs/LIVING_BOOK_WIDGETS.md
```

## Required First Chapters

- `site/chapters/S1/01_finite_circles.qmd`
- `site/chapters/S1/02_rotation_as_addition.qmd`
- `site/chapters/S1/03_coils_orbits_closure.qmd`
- `site/chapters/S1/04_period_gcd_prime_full_coils.qmd`

The S1 chapters must include human explanation, dictionary boxes, theorem boxes, Python reference examples, Lean links, interactive widgets, and explicit distinctions between intuition, example, Python model, and formal theorem.

## Required First Widgets

- `finite_circle_rotator`
- `rotation_composition`
- `coil_orbit_explorer`
- `period_gcd_visualizer`
- `prime_full_coil_explorer`
- `winding_lift_explorer`

Widget constraints:

- deterministic;
- no backend server;
- no remote fetches at runtime;
- plain SVG/HTML/JS for S1;
- minimal and auditable math;
- parity tests against Python reference behavior where practical;
- widget output is never called a proof.

## Generated Data

Create `scripts/site/export_site_data.py` to export:

- `site/data/generated/theorem_manifest.json`;
- `site/data/generated/dictionary.json`;
- `site/data/generated/dimensions.json`;
- `site/data/generated/paper_index.json`;
- `site/data/generated/widget_index.json`.

Exporter status handling:

- `proved`, `lean_proved` -> `proved`;
- `exploratory_python` -> `exploratory`;
- `stated`, `lean_stated`, `planned`, `paper_draft` -> planned/draft as appropriate;
- `blocked` -> `blocked`;
- `deferred` -> `deferred`.

## Required Check Scripts

- `scripts/site/check_quarto_structure.py`
- `scripts/site/check_site_manifest_links.py`
- `scripts/site/check_site_dictionary_links.py`
- `scripts/site/check_site_theorem_status.py`
- `scripts/site/check_site_paper_links.py`
- `scripts/site/check_widget_python_parity.py`

The theorem-status checker must fail if a page labels a theorem as proved when the manifest status is not proved/lean_proved.

## Required Tests

- `tests/site/test_export_site_data.py`
- `tests/site/test_site_manifest_links.py`
- `tests/site/test_site_dictionary_links.py`
- `tests/site/test_site_theorem_status.py`
- `tests/site/test_widget_python_parity.py`

## Planned Make Targets

- `make site-data`
- `make sitecheck`
- `make site-render`
- `make site-preview`
- `make living-book-check`

`living-book-check` should include Lean build, pytest, existing manifest/dictionary checks, site data export, site checks, widget parity, and `quarto render site`.

If Quarto is unavailable, do not fake success. Report the render blocker and keep non-render checks functional.

## First Milestone Acceptance Criteria

- `site/` exists as a Quarto project.
- `site/index.qmd` renders.
- S1 chapters 01 through 04 exist.
- First S1 widgets exist.
- Site data exports from manifests and dictionary.
- Theorem and dictionary boxes display generated data.
- Status badges are generated from manifest status.
- `sitecheck` passes.
- `quarto render site` succeeds unless Quarto is unavailable and documented as a blocker.
- Existing Lean, pytest, manifest, dictionary, paper, and dimension checks still pass.

## Hard Constraints

- Do not modify theorem meanings to make the website easier.
- Do not change Lean proofs for site convenience unless required and green.
- Do not mark future work as proved.
- Do not duplicate dictionary definitions manually when generated data can provide them.
- Do not duplicate theorem statuses manually when generated data can provide them.
- Do not introduce Manim/TTS/video in this goal.
- Do not add a heavy frontend framework.
- Do not make S2/S3/S7 pages look complete when only scaffolded.
- Do not call Python examples or widgets proofs.
- Do not let higher-dimensional speculative concepts contaminate S1 core explanations.
- Do not break existing CI.
