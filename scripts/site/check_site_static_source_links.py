from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

from site_lib import ROOT, repo_relative


REPO_SOURCE_URL_RE = re.compile(
    r"https://github\.com/corbensorenson/circle-calculus/"
    r"(?P<kind>blob|tree)/main/"
    r"(?P<path>[^\s\"'<>)]*)"
)


def source_files() -> list[Path]:
    files: list[Path] = []
    direct_files = [
        ROOT / "README.md",
        ROOT / "site" / "_quarto.yml",
    ]
    for path in direct_files:
        if path.exists():
            files.append(path)

    patterns = [
        "docs/**/*.md",
        "site/**/*.qmd",
        "site/components/**/*.html",
        "site/widgets/**/*.js",
    ]
    for pattern in patterns:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_file() and "site/_site" not in repo_relative(path):
                files.append(path)

    return sorted(set(files))


def clean_url_path(raw_path: str) -> str:
    path = raw_path.split("#", 1)[0].split("?", 1)[0]
    return unquote(path).rstrip(".,;:")


def validate_link(
    failures: list[str],
    path: Path,
    line: int,
    kind: str,
    raw_repo_path: str,
) -> None:
    repo_path = clean_url_path(raw_repo_path)
    if not repo_path:
        failures.append(f"{repo_relative(path)}:{line}: empty GitHub {kind} path")
        return

    local_path = Path(repo_path)
    if local_path.is_absolute() or ".." in local_path.parts:
        failures.append(f"{repo_relative(path)}:{line}: unsafe GitHub {kind} path {repo_path}")
        return

    target = ROOT / local_path
    if kind == "blob":
        if not target.is_file():
            failures.append(f"{repo_relative(path)}:{line}: missing GitHub blob source {repo_path}")
    elif kind == "tree":
        if not target.is_dir():
            failures.append(f"{repo_relative(path)}:{line}: missing GitHub tree source {repo_path}")
    else:
        failures.append(f"{repo_relative(path)}:{line}: unsupported GitHub source kind {kind}")


def main() -> int:
    failures: list[str] = []
    checked = 0

    for path in source_files():
        text = path.read_text()
        for match in REPO_SOURCE_URL_RE.finditer(text):
            checked += 1
            line = text.count("\n", 0, match.start()) + 1
            validate_link(
                failures,
                path,
                line,
                match.group("kind"),
                match.group("path"),
            )

    if failures:
        print("site static source link failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"site static source links ok ({checked} checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
