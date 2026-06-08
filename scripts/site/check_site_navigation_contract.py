from __future__ import annotations

import re
import sys
from typing import Any

from site_lib import ROOT, SITE, load_yaml, repo_relative


REQUIRED_NAV_HREFS = {
    "index.qmd",
    "roadmap.qmd",
    "reader_path.qmd",
    "verify_claim.qmd",
    "status.qmd",
    "dictionary.qmd",
    "theorems.qmd",
    "papers.qmd",
    "targets.qmd",
    "about.qmd",
    "chapters/foundations/index.qmd",
    "chapters/foundations/00_mathematical_building_blocks.qmd",
    "chapters/S0/index.qmd",
    "chapters/S0/opposition.qmd",
    "chapters/S1/index.qmd",
    "chapters/S1/01_finite_circles.qmd",
    "chapters/S1/02_rotation_as_addition.qmd",
    "chapters/S1/03_coils_orbits_closure.qmd",
    "chapters/S1/04_period_gcd_prime_full_coils.qmd",
    "chapters/S1/05_winding_lift.qmd",
    "chapters/S2/index.qmd",
    "chapters/S2/suspended_circles.qmd",
    "chapters/S2/sphere_grids.qmd",
    "chapters/S3/index.qmd",
    "chapters/S3/hyperspheres.qmd",
    "chapters/S3/quaternions.qmd",
    "chapters/S3/hopf_coils.qmd",
    "chapters/S4_S6/index.qmd",
    "chapters/S4_S6/suspension_euler_parity.qmd",
    "chapters/S7/index.qmd",
    "chapters/S7/octonionic_layer.qmd",
    "chapters/S15/index.qmd",
    "chapters/S15/future_hopf_horizon.qmd",
    "chapters/phase2/index.qmd",
    "chapters/phase2/stable_sphere_calculus.qmd",
    "chapters/phase2/bundle_calculus.qmd",
    "chapters/phase2/bott_clifford_periodicity.qmd",
    "chapters/phase2/boundary_cobordism.qmd",
    "chapters/phase2/proof_carrying_glyphs.qmd",
    "chapters/applications/index.qmd",
    "chapters/applications/ai.qmd",
    "chapters/applications/physics.qmd",
    "chapters/applications/generative.qmd",
    "chapters/applications/compute.qmd",
    "chapters/applications/rendering.qmd",
    "chapters/applications/data_analysis.qmd",
}

REQUIRED_RESOURCES = {
    "data/generated/*.json",
    "widgets/**/*.js",
}

PAGE_CONTRACTS = {
    "index.qmd": [
        ("artifact pipeline", ["Lean proofs -> theorem manifests -> dictionary -> Python models -> papers -> interactive site"]),
        ("intuition mode", ["Intuition Mode"]),
        ("formal mode", ["Formal Mode"]),
        ("code mode", ["Code Mode"]),
        ("proof-backed portfolio", ["Proof-Backed Portfolio"]),
        ("portfolio advertisement boundary", ["serious public advertisement", "does not prove universal expressiveness"]),
        ("capability manifest", ["manifests/capability_showcase.yaml"]),
        ("capability validator", ["scripts/check_capability_showcase.py"]),
        ("proof guardrail", ["not proofs", "not formal proof"]),
    ],
    "roadmap.qmd": [
        ("wide/deep phase", ["Phase IV", "wide/deep"]),
        ("edge phase", ["Phase V", "edge problem"]),
        ("sweep phase", ["Phase VI", "correctness", "polish"]),
        ("placeholder guardrail", ["not a proof claim"]),
    ],
    "reader_path.qmd": [
        ("source trail", ["Source Trail"]),
        ("proof status", ["proof-status", "proof status"]),
        ("verify claim page", ["Verify A Claim"]),
        ("full verification", ["make living-book-check"]),
        ("regular verification", ["make check", "make site-render"]),
        ("lesson zero", ["Lesson 0", "Mathematical Building Blocks"]),
    ],
    "chapters/foundations/index.qmd": [
        ("textbook purpose", ["textbook instead of a pile of references"]),
        ("learning moves", ["Name", "Reduce", "Move", "Repeat", "Compare", "Prove"]),
        ("evidence checkpoint", ["picture, a rule, an example, and a proof"]),
    ],
    "chapters/foundations/00_mathematical_building_blocks.qmd": [
        ("objects and names", ["Objects And Names"]),
        ("rules and functions", ["Rules And Functions"]),
        ("composition", ["Composition"]),
        ("iteration", ["Iteration"]),
        ("evidence layers", ["Evidence Layers"]),
        ("non-proof guardrail", ["does not prove the theorem", "not a substitute"]),
    ],
    "verify_claim.qmd": [
        ("Lean-proved criteria", ["A mathematical claim is Lean-proved only when"]),
        ("theorem trace", ["Trace A Theorem Id"]),
        ("dictionary trace", ["Trace A Dictionary Term"]),
        ("paper trace", ["Trace A Paper Claim"]),
        ("widget trace", ["Trace A Widget Or Glyph"]),
        ("local verification", ["make living-book-check", "make sitecheck"]),
        ("public verification", ["GitHub Pages", "site/_site"]),
        ("non-proof guardrail", ["not proofs", "not prove"]),
    ],
    "status.qmd": [
        ("generated status source", ["generated theorem data"]),
        ("status guardrail", ["do not upgrade theorem status"]),
        ("Lean verification command", ["lake build"]),
    ],
    "dictionary.qmd": [
        ("dictionary guardrail", ["not theorem proofs"]),
        ("generated index", ["data-dictionary-index"]),
    ],
    "theorems.qmd": [
        ("manifest source", ["generated from theorem manifests"]),
        ("proof layer guardrail", ["not a proof layer"]),
    ],
    "papers.qmd": [
        ("paper manifest source", ["paper manifest"]),
        ("sidecar links", ["sidecar roots"]),
    ],
    "targets.qmd": [
        ("phase IV target index", ["Phase IV"]),
        ("phase V target index", ["Phase V"]),
        ("phase VI target index", ["Phase VI"]),
        ("phase VII target index", ["Phase VII"]),
        ("target status guardrail", ["not proved theorem claims"]),
    ],
}

WIDGET_PAGE_CONTRACTS = {
    "chapters/S1/01_finite_circles.qmd": ["finite_circle_rotator"],
    "chapters/S1/02_rotation_as_addition.qmd": ["rotation_composition"],
    "chapters/S1/03_coils_orbits_closure.qmd": ["coil_orbit_explorer"],
    "chapters/S1/04_period_gcd_prime_full_coils.qmd": [
        "period_gcd_visualizer",
        "prime_full_coil_explorer",
    ],
    "chapters/S1/05_winding_lift.qmd": ["winding_lift_explorer"],
}

WIDGET_GUARDRAIL_PHRASES = [
    "not a proof",
    "not proofs",
    "not a formal proof",
    "executable reference",
    "explanation rather than a proof",
]

PORTFOLIO_ENTRYPOINT_CONTRACTS = [
    {
        "page": "index.qmd",
        "marker": 'class="portfolio-entrypoint"',
        "site_refs": ["showcase.qmd", "verify_claim.qmd"],
        "repo_refs": [
            "manifests/capability_showcase.yaml",
            "scripts/check_capability_showcase.py",
        ],
        "phrases": [
            "standard anchor",
            "Circle expression",
            "Circle-native value",
            "proof scope",
            "not-claimed boundary",
        ],
    }
]


def collect_hrefs(node: Any) -> set[str]:
    hrefs: set[str] = set()
    if isinstance(node, dict):
        href = node.get("href")
        if isinstance(href, str):
            hrefs.add(href)
        for value in node.values():
            hrefs.update(collect_hrefs(value))
    elif isinstance(node, list):
        for item in node:
            hrefs.update(collect_hrefs(item))
    return hrefs


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def has_phrase(text: str, phrase: str) -> bool:
    return normalized(phrase) in normalized(text)


def check_quarto_navigation(failures: list[str]) -> None:
    quarto = SITE / "_quarto.yml"
    data = load_yaml(quarto)
    hrefs = collect_hrefs(data.get("website", {}))
    missing = sorted(REQUIRED_NAV_HREFS - hrefs)
    if missing:
        failures.append(f"site/_quarto.yml: missing navigation hrefs {missing}")

    resources = set(data.get("project", {}).get("resources", []))
    missing_resources = sorted(REQUIRED_RESOURCES - resources)
    if missing_resources:
        failures.append(f"site/_quarto.yml: missing resources {missing_resources}")

    for href in sorted(hrefs):
        if href.endswith(".qmd") and not (SITE / href).exists():
            failures.append(f"site/_quarto.yml: navigation href does not exist: {href}")


def check_page_contracts(failures: list[str]) -> None:
    for rel_path, requirements in PAGE_CONTRACTS.items():
        path = SITE / rel_path
        text = path.read_text()
        for label, phrases in requirements:
            if not any(has_phrase(text, phrase) for phrase in phrases):
                failures.append(
                    f"{repo_relative(path)}: missing {label}; expected one of {phrases}"
                )


def check_widget_page_contracts(failures: list[str]) -> None:
    for rel_path, widgets in WIDGET_PAGE_CONTRACTS.items():
        path = SITE / rel_path
        text = path.read_text()
        lower_text = normalized(text)
        for widget in widgets:
            if f'data-widget="{widget}"' not in text:
                failures.append(f"{repo_relative(path)}: missing widget mount {widget}")
            if f"widgets/S1/{widget}.js" not in text:
                failures.append(f"{repo_relative(path)}: missing widget script {widget}.js")
        if "python reference model" not in lower_text:
            failures.append(f"{repo_relative(path)}: missing Python reference model section")
        if not any(phrase in lower_text for phrase in WIDGET_GUARDRAIL_PHRASES):
            failures.append(f"{repo_relative(path)}: widget page lacks an explicit non-proof guardrail")


def check_portfolio_entrypoints(failures: list[str]) -> None:
    for contract in PORTFOLIO_ENTRYPOINT_CONTRACTS:
        path = SITE / contract["page"]
        text = path.read_text()
        marker = contract["marker"]
        if marker not in text:
            failures.append(f"{repo_relative(path)}: missing portfolio entrypoint marker {marker}")
        for ref in contract["site_refs"]:
            if f'"{ref}"' not in text or f"]({ref})" not in text:
                failures.append(f"{repo_relative(path)}: missing portfolio site ref {ref}")
            if not (SITE / ref).exists():
                failures.append(f"{repo_relative(path)}: portfolio site ref does not exist: {ref}")
        for ref in contract["repo_refs"]:
            if f'"{ref}"' not in text:
                failures.append(f"{repo_relative(path)}: missing portfolio repo ref {ref}")
            if not (ROOT / ref).exists():
                failures.append(f"{repo_relative(path)}: portfolio repo ref does not exist: {ref}")
        for phrase in contract["phrases"]:
            if not has_phrase(text, phrase):
                failures.append(f"{repo_relative(path)}: missing portfolio phrase {phrase!r}")


def main() -> int:
    failures: list[str] = []
    check_quarto_navigation(failures)
    check_page_contracts(failures)
    check_widget_page_contracts(failures)
    check_portfolio_entrypoints(failures)

    if failures:
        print("site navigation contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site navigation contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
