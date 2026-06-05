from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from repo_paths import ROOT, SIDECARS


def lake_path() -> str:
    found = shutil.which("lake")
    if found:
        return found
    fallback = Path.home() / ".elan" / "bin" / "lake"
    if fallback.exists():
        return str(fallback)
    raise FileNotFoundError("lake not found on PATH or at ~/.elan/bin/lake")


def main() -> int:
    files = sorted(SIDECARS.glob("*/lean/*.lean"))
    if not files:
        print("no Lean sidecars found", file=sys.stderr)
        return 1

    env = os.environ.copy()
    elan_bin = str(Path.home() / ".elan" / "bin")
    env["PATH"] = f"{elan_bin}:{env.get('PATH', '')}"

    lake = lake_path()
    failures: list[tuple[Path, str]] = []
    for path in files:
        result = subprocess.run(
            [lake, "env", "lean", str(path)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            failures.append((path, result.stdout + result.stderr))

    if failures:
        print("Lean sidecar failures:", file=sys.stderr)
        for path, output in failures:
            print(f"--- {path} ---", file=sys.stderr)
            print(output, file=sys.stderr)
        return 1

    print(f"Lean sidecars ok: {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

