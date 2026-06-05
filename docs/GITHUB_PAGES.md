# GitHub Pages Publishing

The Living Book source lives under `site/` and renders with Quarto.

## Local Render

```bash
make site-data
make sitecheck
make site-render
```

The rendered output is `site/_site/`. That directory is generated output and should not be committed.

## Publishing Options

Preferred future route:

1. Add a GitHub Actions workflow that installs or exposes Quarto.
2. Run `make sitecheck`.
3. Run `make site-render`.
4. Upload `site/_site/` as the GitHub Pages artifact.
5. Deploy through GitHub Pages.

This repository does not currently enable automatic Pages deployment. That keeps the first Living Book milestone focused on correct source, generated data, and validation.

## Guardrails

- Do not publish a site render if `make sitecheck` fails.
- Do not publish a site render if theorem statuses fail validation.
- Do not treat GitHub Pages output as proof. The formal verification command remains `lake build`, supported by repository checks.
- Do not commit secrets, custom-domain assumptions, or paid-service configuration for Pages.
