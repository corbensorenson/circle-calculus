from __future__ import annotations

import sys

from site_lib import ROOT, SITE, repo_relative


SHARED_HELPER_REQUIREMENTS = {
    "site/widgets/shared/svg_helpers.js": [
        ("SVG image role", 'role: "img"'),
        ("SVG labelled-by metadata", '"aria-labelledby"'),
        ("SVG title element", 'svgElement("title"'),
        ("SVG description element", 'svgElement("desc"'),
        ("numeric input label", 'input.setAttribute("aria-label", label)'),
        ("numeric input mode", 'input.inputMode = "numeric"'),
        ("DOM-built widget header", "export function addWidgetHeader"),
        ("live output region", 'output.setAttribute("aria-live", "polite")'),
        ("atomic output updates", 'output.setAttribute("aria-atomic", "true")'),
        ("output region role", 'output.setAttribute("role", "region")'),
    ],
    "site/widgets/shared/widget_base.js": [
        ("widget region role", 'target.setAttribute("role", "region")'),
        ("widget region label", 'target.setAttribute("aria-label"'),
    ],
    "site/assets/css/living-book.css": [
        ("keyboard focus styling", ".widget-panel input:focus-visible"),
    ],
}

S1_WIDGETS = [
    "finite_circle_rotator",
    "rotation_composition",
    "coil_orbit_explorer",
    "period_gcd_visualizer",
    "prime_full_coil_explorer",
    "winding_lift_explorer",
]

PLACEHOLDER_WIDGETS = [
    "sphere_grid_placeholder",
    "hopf_placeholder",
]

GENERATIVE_WIDGETS = [
    "seed_rule_diagram_generator",
]


def check_shared_helpers(failures: list[str]) -> None:
    for rel_path, requirements in SHARED_HELPER_REQUIREMENTS.items():
        path = ROOT / rel_path
        text = path.read_text()
        for label, needle in requirements:
            if needle not in text:
                failures.append(f"{rel_path}: missing {label}")


def check_s1_widget_accessibility(failures: list[str]) -> None:
    for widget_id in S1_WIDGETS:
        path = SITE / "widgets" / "S1" / f"{widget_id}.js"
        text = path.read_text()
        if "addLabeledNumber" not in text:
            failures.append(f"{repo_relative(path)}: inputs must use addLabeledNumber")
        if "addOutput" not in text:
            failures.append(f"{repo_relative(path)}: dynamic output must use addOutput")
        if "renderCircleSvg({" in text and "title:" not in text:
            failures.append(f"{repo_relative(path)}: renderCircleSvg calls must pass a title")
        if "addWidgetHeader" not in text:
            failures.append(f"{repo_relative(path)}: header must use addWidgetHeader")
        if ".innerHTML" in text:
            failures.append(f"{repo_relative(path)}: avoid innerHTML in interactive S1 widgets")


def check_placeholder_guardrails(failures: list[str]) -> None:
    for widget_id in PLACEHOLDER_WIDGETS:
        dimension = "S2" if widget_id.startswith("sphere") else "S3"
        path = SITE / "widgets" / dimension / f"{widget_id}.js"
        text = path.read_text()
        if "Scaffold only" not in text:
            failures.append(f"{repo_relative(path)}: placeholder must be marked scaffold-only")
        if "addWidgetHeader" not in text:
            failures.append(f"{repo_relative(path)}: placeholder header must use addWidgetHeader")
        if ".innerHTML" in text:
            failures.append(f"{repo_relative(path)}: avoid innerHTML in placeholder widgets")
        if "does not" not in text and "future work" not in text:
            failures.append(f"{repo_relative(path)}: placeholder must include a non-proof/future-work guardrail")


def check_generative_widget_guardrails(failures: list[str]) -> None:
    for widget_id in GENERATIVE_WIDGETS:
        path = SITE / "widgets" / "generative" / f"{widget_id}.js"
        text = path.read_text()
        if "addWidgetHeader" not in text:
            failures.append(f"{repo_relative(path)}: header must use addWidgetHeader")
        if "addOutput" not in text:
            failures.append(f"{repo_relative(path)}: dynamic output must use addOutput")
        if ".innerHTML" in text:
            failures.append(f"{repo_relative(path)}: avoid innerHTML in generative widgets")
        if "generated explanation only" not in text:
            failures.append(f"{repo_relative(path)}: generated widgets must state the non-proof boundary")
        if "not a formal proof" not in text:
            failures.append(f"{repo_relative(path)}: generated widgets must not present diagrams as proofs")


def main() -> int:
    failures: list[str] = []
    check_shared_helpers(failures)
    check_s1_widget_accessibility(failures)
    check_placeholder_guardrails(failures)
    check_generative_widget_guardrails(failures)

    if failures:
        print("site accessibility contract failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("site accessibility contract ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
