# Circle Calculus Living Book Policy

This document governs the Phase III Living Book: a Quarto-based interactive explanation layer for Circle Calculus.

## Purpose

The Living Book should help readers understand the project by combining prose, theorem-linked cards, dictionary entries, Python reference examples, Lean source links, and browser-native widgets. It is downstream of the formal repository. It must not become a separate hand-written website whose claims drift away from the manifests and Lean proofs.

## Sources Of Truth

- Theorem manifests are the source of truth for theorem ids and proof status.
- Lean declarations are the formal proof source.
- Python reference models are executable examples and modeling support only.
- Papers are human-readable exposition tied to theorem ids and sidecars.
- Widgets and diagrams are intuition and exploration layers only.

## Textbook Design Rule

The Living Book should be usable as a guided textbook, not merely as a directory of links. Reader-facing chapters should move from prerequisite concepts to harder concepts, and each core lesson should include:

- the learning goal,
- a plain-language explanation,
- a diagram or widget when the concept benefits from one,
- a worked example,
- a common mistake or boundary warning when the idea is easy to overread,
- a small thing for the reader to try,
- a checkpoint question or calculation, and
- a source trail back to theorem cards, dictionary entries, papers, Lean declarations, and Python examples.

Reference indexes remain important, but they should support the reading path instead of replacing it. Navigation should lead with the guided chapter sequence and place dictionary/theorem/paper/target indexes in a reference or appendix position.

The front of the book must include a foundations/toolkit layer before the first technical unit. This layer should teach the reader how the project uses objects, addresses, rules, composition, iteration, invariants, evidence layers, and proof status, so the rest of the book can be read as a cumulative curriculum.

## Proof-Status Rule

No page, theorem box, widget caption, status badge, or chapter text may call a theorem proved unless all of these are true:

1. The theorem id exists in a theorem manifest.
2. The theorem status is `proved` or `lean_proved`.
3. The theorem resolves to a compiled Lean declaration.
4. The proved core contains no `sorry`, `admit`, unapproved axiom, unsafe shortcut, or fake-proof marker.
5. Repository checks pass.

Python examples, widget output, SVG diagrams, and generated cards are not proofs.

## Status Language

Living Book theorem cards may use these labels:

- `Lean-proved`: only for `proved` or `lean_proved` manifest status.
- `Executable example`: for Python or widget demonstrations.
- `Planned theorem`: for `planned`, `stated`, or `lean_stated`.
- `Exploratory`: for `exploratory_python`.
- `Blocked`: only when blocker text exists.
- `Deferred`: for long-horizon topics.
- `Draft`: for paper/chapter drafts or other unproved exposition.

The site must not upgrade theorem status by prose.

## Quarto And Static Site Rule

The first implementation must work as a static Quarto site suitable for GitHub Pages. Core S1 widgets should be plain browser-native HTML/SVG/JavaScript and should not require a live Python server, Binder, Jupyter, Thebe, JupyterLite, Lean Web, or remote runtime.

If Quarto is not installed, do not fake a successful render. Keep non-render site checks functional and report the render blocker clearly.

Local render commands:

```bash
make site-data
make sitecheck
make site-render
make site-render-check
```

`make sitecheck` validates generated source-link paths so rendered GitHub links for theorem manifests, Lean files, dictionary sources, papers, sidecars, widgets, glyphs, and roadmap targets do not silently drift after files move. It also validates hard-coded GitHub source links in the Living Book, docs, and README; scaffold/future/non-proof guardrails; reciprocal generated backlinks across theorem, dictionary, paper, widget, and glyph data; widget mount contracts; and basic widget accessibility contracts such as labelled inputs, named regions, live output regions, and SVG title/description metadata.

`make site-render-check` validates the rendered `site/_site/` artifact after Quarto runs. It requires the Pages marker, fallback page, generated JSON indexes, widgets, CSS, and core HTML pages to exist, and it fails when built pages contain local links that escape or miss the published artifact.

It also validates rendered GitHub repository links, including Quarto-generated `View source` links. The Quarto project must keep `repo-subdir: site` configured so those links resolve to the checked-in Living Book sources instead of nonexistent repository-root `.qmd` files.

On this workstation, Quarto is available through a local extracted install under `.tools/` when no system `quarto` command exists. Fresh clones can install Quarto with the standard Quarto installer or a package manager, then run the same Make targets.

The Makefile sets Quarto's `HOME` and `DENO_DIR` to ignored repo-local paths under `.tools/` for render and preview targets. This keeps Quarto's Sass/Deno cache writes out of user-specific cache directories and makes sandboxed autonomous runs reproducible.

## Deferred Media And Runtime Layers

Do not implement Manim, TTS, narration, video rendering, or a long movie until the static Living Book skeleton and S1 interactives are stable. Jupyter/Thebe/JupyterLite and Lean Web links are optional later layers; they do not replace local `lake build`.

## Publishing

Document GitHub Pages publishing once the site exists, but do not add secrets, paid services, custom-domain assumptions, or automatic deployment unless the repository already has a clear deployment pattern.
