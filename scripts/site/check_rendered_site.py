from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from site_lib import ROOT, SITE


OUTPUT = SITE / "_site"
PAGES_BASE = "/circle-calculus/"
REPO_HOST = "github.com"
REPO_PATH = "/corbensorenson/circle-calculus/"

REQUIRED_RENDERED_FILES = [
    ".nojekyll",
    "404.html",
    "index.html",
    "about.html",
    "roadmap.html",
    "reader_path.html",
    "verify_claim.html",
    "status.html",
    "dictionary.html",
    "theorems.html",
    "papers.html",
    "targets.html",
    "assets/css/living-book.css",
    "data/generated/theorem_manifest.json",
    "data/generated/dictionary.json",
    "data/generated/dimensions.json",
    "data/generated/paper_index.json",
    "data/generated/widget_index.json",
    "data/generated/glyph_index.json",
    "data/generated/phase4_targets.json",
    "data/generated/phase5_targets.json",
    "data/generated/phase6_targets.json",
    "data/generated/phase7_targets.json",
    "widgets/shared/circle_math_core.js",
    "widgets/shared/svg_helpers.js",
    "widgets/shared/widget_base.js",
    "widgets/S1/finite_circle_rotator.js",
    "widgets/S1/rotation_composition.js",
    "widgets/S1/coil_orbit_explorer.js",
    "widgets/S1/period_gcd_visualizer.js",
    "widgets/S1/prime_full_coil_explorer.js",
    "widgets/S1/winding_lift_explorer.js",
    "widgets/S2/sphere_grid_placeholder.js",
    "widgets/S3/hopf_placeholder.js",
    "widgets/generative/seed_rule_diagram_generator.js",
]

REQUIRED_TEXT = {
    "index.html": "Circle Calculus Living Book",
    "404.html": "Page Not Found",
}

LINK_ATTRS = {"href", "src"}
IGNORED_SCHEMES = {
    "data",
    "http",
    "https",
    "javascript",
    "mailto",
    "tel",
}


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in LINK_ATTRS and value:
                self.links.append((name, value))


def rendered_relative(path: Path) -> str:
    return str(path.relative_to(OUTPUT))


def is_inside_output(path: Path) -> bool:
    try:
        path.resolve().relative_to(OUTPUT.resolve())
    except ValueError:
        return False
    return True


def local_target_for(source: Path, raw_value: str) -> Path | None:
    value = raw_value.strip()
    if not value or value.startswith("#"):
        return None

    parsed = urlsplit(value)
    if parsed.scheme in IGNORED_SCHEMES or parsed.netloc:
        return None

    path_text = unquote(parsed.path)
    if not path_text:
        return None

    if path_text.startswith("/"):
        if path_text == PAGES_BASE.rstrip("/"):
            return OUTPUT
        if path_text.startswith(PAGES_BASE):
            return (OUTPUT / path_text.removeprefix(PAGES_BASE)).resolve()
        raise ValueError(f"root-relative link outside Pages base: {raw_value}")

    return (source.parent / path_text).resolve()


def target_exists(target: Path) -> bool:
    if target.exists():
        return True
    if target.suffix:
        return False
    return target.with_suffix(".html").exists()


def clean_repo_path(path: str) -> str:
    return unquote(path).rstrip(".,;:")


def check_repo_source_link(failures: list[str], html_path: Path, attr: str, raw_value: str) -> None:
    parsed = urlsplit(raw_value)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != REPO_HOST:
        return
    if not parsed.path.startswith(REPO_PATH):
        return

    suffix = parsed.path.removeprefix(REPO_PATH)
    parts = suffix.split("/", 2)
    if len(parts) != 3:
        return

    kind, branch, repo_path = parts
    if branch != "main" or kind not in {"blob", "tree"}:
        return

    local_path = Path(clean_repo_path(repo_path))
    if local_path.is_absolute() or ".." in local_path.parts:
        failures.append(
            f"{rendered_relative(html_path)}: {attr} {raw_value!r} contains unsafe repo path {repo_path!r}"
        )
        return

    target = ROOT / local_path
    if kind == "blob" and not target.is_file():
        failures.append(
            f"{rendered_relative(html_path)}: {attr} {raw_value!r} points to missing repo file {repo_path}"
        )
    if kind == "tree" and not target.is_dir():
        failures.append(
            f"{rendered_relative(html_path)}: {attr} {raw_value!r} points to missing repo directory {repo_path}"
        )


def check_required_files(failures: list[str]) -> None:
    if not OUTPUT.exists():
        failures.append("site/_site does not exist; run `make site-render` first")
        return
    for rel_path in REQUIRED_RENDERED_FILES:
        path = OUTPUT / rel_path
        if not path.exists():
            failures.append(f"missing rendered file {rel_path}")
    for rel_path, needle in REQUIRED_TEXT.items():
        path = OUTPUT / rel_path
        if path.exists() and needle not in path.read_text(errors="ignore"):
            failures.append(f"{rel_path}: missing expected text {needle!r}")


def check_rendered_links(failures: list[str]) -> None:
    if not OUTPUT.exists():
        return
    for html_path in sorted(OUTPUT.glob("**/*.html")):
        parser = LinkCollector()
        parser.feed(html_path.read_text(errors="ignore"))
        for attr, raw_value in parser.links:
            check_repo_source_link(failures, html_path, attr, raw_value)
            try:
                target = local_target_for(html_path, raw_value)
            except ValueError as exc:
                failures.append(f"{rendered_relative(html_path)}: {exc}")
                continue
            if target is None:
                continue
            if not is_inside_output(target):
                failures.append(
                    f"{rendered_relative(html_path)}: {attr} {raw_value!r} resolves outside site/_site"
                )
                continue
            if not target_exists(target):
                failures.append(
                    f"{rendered_relative(html_path)}: {attr} {raw_value!r} resolves to missing {rendered_relative(target)}"
                )


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_rendered_links(failures)
    if failures:
        print("rendered site failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    html_count = len(list(OUTPUT.glob("**/*.html")))
    print(f"rendered site ok: {html_count} html files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
