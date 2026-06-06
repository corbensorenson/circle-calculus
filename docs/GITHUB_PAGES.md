# GitHub Pages Publishing

The Living Book source lives under `site/` and renders with Quarto. The rendered output is `site/_site/`; that directory is generated output and should not be committed.

GitHub Pages is the public hosting target for the Living Book:

```text
https://corbensorenson.github.io/circle-calculus/
```

GitHub Pages is a static-site host for HTML, CSS, and JavaScript from a GitHub repository. For this public repository, the static Quarto output is a direct fit.

## Local Render

```bash
make site-data
make sitecheck
make site-render
make site-render-check
```

For the full local gate, including Lean and all repository checks:

```bash
make living-book-check
```

## Automatic Deployment

`.github/workflows/pages.yml` builds and deploys the Living Book.

The build job:

1. checks out the repository,
2. builds the Lean proof spine with `leanprover/lean-action`,
3. installs Python dependencies,
4. installs Quarto,
5. runs `make sourcecheck`,
6. renders with `make site-render`, and
7. validates the rendered artifact with `make site-render-check`, and
8. uploads `site/_site/` as a GitHub Pages artifact.

The deploy job publishes the artifact to GitHub Pages only from `main`.

This keeps publication downstream of the proof/status/data checks. A rendered page can be public only after theorem manifests, dictionary links, paper links, generated theorem/dictionary/paper/widget/glyph backlinks, widget mount contracts, widget parity, fake-proof guardrails, Quarto render, and rendered-artifact link validation have all passed in CI.

`make sourcecheck` includes `make sitecheck`, and `sitecheck` validates the generated source-link paths and reciprocal generated backlinks used by Living Book GitHub links and indexes. This protects the public site against stale links when Lean files, papers, dictionary files, sidecars, widgets, glyph fixtures, or target manifests move.

## Repository Settings

This repository is configured for GitHub Pages workflow builds at:

```text
https://corbensorenson.github.io/circle-calculus/
```

No secrets, custom domain, paid service, or checked-in rendered output are required.

The Quarto site includes `site/.nojekyll` and `site/404.qmd`. The marker prevents accidental Jekyll processing if publishing mode changes, and the 404 page routes stale public links back to the Start, Reader Path, Dictionary, Theorem, Paper, and Roadmap entry points.

If the first deployment does not appear, check:

- the `Deploy Living Book` workflow run,
- repository Settings -> Pages -> Build and deployment source,
- repository Actions permissions, and
- whether the build failed before artifact upload.

## Guardrails

- Do not publish a site render if `make sourcecheck` or `make sitecheck` fails.
- Do not publish a site render if `make site-render-check` finds a missing artifact or broken local link.
- Do not publish a site render if theorem statuses fail validation.
- Do not treat GitHub Pages output as proof. The formal verification command remains `lake build`, supported by repository checks.
- Do not commit secrets, custom-domain assumptions, or paid-service configuration for Pages.
