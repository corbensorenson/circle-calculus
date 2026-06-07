from __future__ import annotations

import sys

from site_lib import ROOT


REQUIRED = [
    "site/_quarto.yml",
    "site/index.qmd",
    "site/404.qmd",
    "site/about.qmd",
    "site/roadmap.qmd",
    "site/showcase.qmd",
    "site/verify_claim.qmd",
    "site/status.qmd",
    "site/dictionary.qmd",
    "site/theorems.qmd",
    "site/papers.qmd",
    "site/targets.qmd",
    "site/chapters/S1/index.qmd",
    "site/chapters/S1/01_finite_circles.qmd",
    "site/chapters/S1/02_rotation_as_addition.qmd",
    "site/chapters/S1/03_coils_orbits_closure.qmd",
    "site/chapters/S1/04_period_gcd_prime_full_coils.qmd",
    "site/chapters/S1/05_winding_lift.qmd",
    "site/widgets/shared/circle_math_core.js",
    "site/widgets/shared/svg_helpers.js",
    "site/widgets/shared/widget_base.js",
    "site/widgets/S1/finite_circle_rotator.js",
    "site/widgets/S1/rotation_composition.js",
    "site/widgets/S1/coil_orbit_explorer.js",
    "site/widgets/S1/period_gcd_visualizer.js",
    "site/widgets/S1/prime_full_coil_explorer.js",
    "site/widgets/S1/winding_lift_explorer.js",
    "site/data/generated/theorem_manifest.json",
    "site/data/generated/dictionary.json",
    "site/data/generated/dimensions.json",
    "site/data/generated/paper_index.json",
    "site/data/generated/widget_index.json",
    "site/data/generated/glyph_index.json",
    "site/data/generated/generator_index.json",
    "site/data/generated/phase4_targets.json",
    "site/data/generated/phase5_targets.json",
    "site/data/generated/phase6_targets.json",
    "site/data/generated/phase7_targets.json",
    "site/data/generated/capability_showcase.json",
    "docs/LIVING_BOOK_POLICY.md",
    "docs/LIVING_BOOK_ROADMAP.md",
    "docs/LIVING_BOOK_WIDGETS.md",
]

REQUIRED_QUARTO_RESOURCES = [
    ".nojekyll",
    "data/generated/*.json",
    "widgets/**/*.js",
]

REQUIRED_QUARTO_CONFIG = [
    'repo-url: "https://github.com/corbensorenson/circle-calculus"',
    "repo-subdir: site",
    "repo-actions: [source]",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        print("missing required Living Book files:", file=sys.stderr)
        for path in missing:
            print(path, file=sys.stderr)
        return 1
    quarto_config = (ROOT / "site" / "_quarto.yml").read_text()
    missing_resources = [
        resource for resource in REQUIRED_QUARTO_RESOURCES if resource not in quarto_config
    ]
    if missing_resources:
        print("missing required Quarto resources:", file=sys.stderr)
        for resource in missing_resources:
            print(resource, file=sys.stderr)
        return 1
    missing_config = [setting for setting in REQUIRED_QUARTO_CONFIG if setting not in quarto_config]
    if missing_config:
        print("missing required Quarto source-link config:", file=sys.stderr)
        for setting in missing_config:
            print(setting, file=sys.stderr)
        return 1
    print("quarto structure ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
