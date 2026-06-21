#!/usr/bin/env python3
"""Generate public API reference docs for stable library surfaces."""

from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated" / "PUBLIC_API_REFERENCE.md"

PYTHON_MODULES = [
    "circle_math.core",
    "circle_math.contracts",
    "circle_math.ai_contracts",
]

LEAN_FACADES = [
    "Circle.Core",
    "Circle.Applications.Public",
    "Circle.Contracts",
]

DECL_RE = re.compile(
    r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive|class)\s+([A-Za-z0-9_'.]+)"
)
IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)")
PUB_MOD_RE = re.compile(r"^\s*pub\s+mod\s+([A-Za-z0-9_]+)\s*;")
PUB_USE_RE = re.compile(r"^\s*pub\s+use\s+(.+?);")


def module_to_path(module: str) -> Path:
    return ROOT / (module.replace(".", "/") + ".lean")


def lean_declarations(path: Path) -> list[str]:
    if not path.exists():
        return []
    names: list[str] = []
    for line in path.read_text().splitlines():
        match = DECL_RE.match(line)
        if match:
            names.append(match.group(1))
    return names


def lean_imports(module: str) -> list[str]:
    path = module_to_path(module)
    if not path.exists():
        return []
    imports: list[str] = []
    for line in path.read_text().splitlines():
        match = IMPORT_RE.match(line)
        if match:
            imports.append(match.group(1))
    return imports


def python_rows(module_name: str) -> list[str]:
    module = importlib.import_module(module_name)
    exported = list(getattr(module, "__all__", []))
    rows = [
        f"### `{module_name}`",
        "",
        inspect.getdoc(module) or "No module docstring.",
        "",
        "| Name | Kind | Signature / Summary |",
        "| --- | --- | --- |",
    ]
    for name in exported:
        value = getattr(module, name, None)
        if value is None:
            rows.append(f"| `{name}` | missing | not importable |")
            continue
        if inspect.isclass(value):
            kind = "class"
            summary = (inspect.getdoc(value) or "").splitlines()[0] if inspect.getdoc(value) else ""
        elif inspect.isfunction(value):
            kind = "function"
            try:
                summary = f"`{name}{inspect.signature(value)}`"
            except (TypeError, ValueError):
                summary = "`signature unavailable`"
        else:
            kind = "value"
            summary = type(value).__name__
        rows.append(f"| `{name}` | {kind} | {summary} |")
    rows.append("")
    return rows


def lean_rows() -> list[str]:
    rows = ["## Lean Stable Import Surfaces", ""]
    for facade in LEAN_FACADES:
        rows.extend([f"### `{facade}`", ""])
        imports = lean_imports(facade)
        if not imports:
            rows.extend(["No imports found.", ""])
            continue
        rows.extend(["| Imported Module | Declaration Count | Declarations |", "| --- | ---: | --- |"])
        for imported in imports:
            path = module_to_path(imported)
            declarations = lean_declarations(path)
            if len(declarations) > 60:
                shown = ", ".join(f"`{name}`" for name in declarations[:60])
                shown += f", ... ({len(declarations) - 60} more)"
            else:
                shown = ", ".join(f"`{name}`" for name in declarations) or "_none_"
            rows.append(f"| `{imported}` | {len(declarations)} | {shown} |")
        rows.append("")
    return rows


def rust_rows() -> list[str]:
    lib = ROOT / "rust" / "circle-prime" / "src" / "lib.rs"
    rows = ["## Rust `circle-prime` Crate Surface", ""]
    if not lib.exists():
        return rows + ["Rust crate root not found.", ""]
    modules: list[str] = []
    uses: list[str] = []
    pending_use: list[str] = []
    in_use_block = False
    for line in lib.read_text().splitlines():
        mod_match = PUB_MOD_RE.match(line)
        if mod_match:
            modules.append(mod_match.group(1))
        use_match = PUB_USE_RE.match(line)
        if use_match:
            uses.append(use_match.group(1))
            continue
        if line.strip().startswith("pub use "):
            in_use_block = True
            pending_use = [line.strip()]
            if line.strip().endswith(";"):
                uses.append(" ".join(pending_use).removeprefix("pub use ").removesuffix(";"))
                in_use_block = False
            continue
        if in_use_block:
            pending_use.append(line.strip())
            if line.strip().endswith(";"):
                text = " ".join(pending_use)
                uses.append(text.removeprefix("pub use ").removesuffix(";"))
                in_use_block = False
    rows.extend(["Public modules:", ""])
    for module in modules:
        rows.append(f"- `{module}`")
    rows.extend(["", "Public re-export groups:", ""])
    for use in uses:
        rows.append(f"- `{use}`")
    rows.append("")
    return rows


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Generated Public API Reference",
        "",
        "Generated by `scripts/generate_public_api_docs.py`.",
        "",
        "This reference documents stable public facades. It does not make",
        "research modules or generated artifacts stable by accident.",
        "",
        "## Python Stable Modules",
        "",
    ]
    for module_name in PYTHON_MODULES:
        lines.extend(python_rows(module_name))
    lines.extend(lean_rows())
    lines.extend(rust_rows())
    OUT.write_text("\n".join(lines).rstrip() + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
