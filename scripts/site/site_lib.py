from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
SITE = ROOT / "site"
GENERATED = SITE / "data" / "generated"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


THEOREM_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-T\d{4}\b")
DICTIONARY_ATTR_RE = re.compile(r'data-dictionary-ids?="([^"]+)"')
PAPER_ATTR_RE = re.compile(r'data-paper-ref="([^"]+)"')
MARKDOWN_PAPER_LINK_RE = re.compile(r"\]\(([^)#]*papers/[^)#]+\.md)(?:#[^)]+)?\)")


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text())
    return data or {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def site_source_files() -> list[Path]:
    patterns = [
        "site/**/*.qmd",
        "site/components/**/*.html",
        "site/widgets/**/*.js",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(ROOT.glob(pattern)))
    return files


def split_ids(raw: str) -> list[str]:
    return [item for item in re.split(r"[\s,]+", raw.strip()) if item]


def collect_theorem_ids(files: Iterable[Path] | None = None) -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for path in files or site_source_files():
        ids = set(THEOREM_ID_RE.findall(path.read_text()))
        if ids:
            out[path] = ids
    return out


def collect_dictionary_ids(files: Iterable[Path] | None = None) -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for path in files or site_source_files():
        text = path.read_text()
        ids: set[str] = set()
        for match in DICTIONARY_ATTR_RE.finditer(text):
            ids.update(split_ids(match.group(1)))
        if ids:
            out[path] = ids
    return out


def collect_paper_refs(files: Iterable[Path] | None = None) -> dict[Path, set[str]]:
    out: dict[Path, set[str]] = {}
    for path in files or sorted(SITE.glob("**/*.qmd")):
        text = path.read_text()
        refs = {match.group(1) for match in PAPER_ATTR_RE.finditer(text)}
        refs.update(match.group(1) for match in MARKDOWN_PAPER_LINK_RE.finditer(text))
        if refs:
            out[path] = refs
    return out


def repo_relative(path: Path) -> str:
    return str(path.relative_to(ROOT))
