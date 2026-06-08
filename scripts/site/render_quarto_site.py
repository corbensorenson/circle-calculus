from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from site_lib import ROOT, SITE


OUTPUT = SITE / "_site"
QUARTO_CACHE = SITE / ".quarto"


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def clean_quarto_intermediates(*, include_output: bool) -> None:
    if include_output:
        remove_path(OUTPUT)
    remove_path(QUARTO_CACHE)
    remove_path(SITE / "site_libs")

    for qmd in SITE.rglob("*.qmd"):
        if OUTPUT in qmd.parents:
            continue
        remove_path(qmd.with_suffix(".html"))
        remove_path(qmd.with_name(f"{qmd.stem}_files"))


def precreate_output_dirs() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path in SITE.rglob("*"):
        if not path.is_dir() or OUTPUT in path.parents or path == OUTPUT:
            continue
        (OUTPUT / path.relative_to(SITE)).mkdir(parents=True, exist_ok=True)


def run_quarto(quarto: str) -> int:
    return subprocess.run([quarto, "render", "site"], cwd=ROOT, env=os.environ.copy()).returncode


def rendered_site_is_valid() -> bool:
    result = subprocess.run(
        [sys.executable, "scripts/site/check_rendered_site.py"],
        cwd=ROOT,
        env=os.environ.copy(),
    )
    return result.returncode == 0


def main() -> int:
    quarto = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("QUARTO", "quarto")
    last_render_code = 1

    for attempt in range(1, 3):
        clean_quarto_intermediates(include_output=True)
        precreate_output_dirs()
        last_render_code = run_quarto(quarto)
        if last_render_code != 0:
            # Quarto can occasionally report a rename race after producing a
            # complete static site. Give delayed filesystem writes a moment to
            # settle, then require the independent rendered-site validator.
            time.sleep(1)
        if rendered_site_is_valid():
            if last_render_code != 0:
                print(
                    "quarto render reported a nonzero exit after producing a "
                    "validated _site; treating this as a known rename-race recovery",
                    file=sys.stderr,
                )
            clean_quarto_intermediates(include_output=False)
            return 0
        if attempt == 1:
            print("quarto render did not produce a valid _site; retrying once", file=sys.stderr)

    return last_render_code or 1


if __name__ == "__main__":
    raise SystemExit(main())
