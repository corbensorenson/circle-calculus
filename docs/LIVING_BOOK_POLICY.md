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
```

On this workstation, Quarto is available through a local extracted install under `.tools/` when no system `quarto` command exists. Fresh clones can install Quarto with the standard Quarto installer or a package manager, then run the same Make targets.

## Deferred Media And Runtime Layers

Do not implement Manim, TTS, narration, video rendering, or a long movie until the static Living Book skeleton and S1 interactives are stable. Jupyter/Thebe/JupyterLite and Lean Web links are optional later layers; they do not replace local `lake build`.

## Publishing

Document GitHub Pages publishing once the site exists, but do not add secrets, paid services, custom-domain assumptions, or automatic deployment unless the repository already has a clear deployment pattern.
