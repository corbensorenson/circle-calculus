from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    node = shutil.which("node")
    if node is None:
        print("widget runtime link check requires Node.js", file=sys.stderr)
        return 1
    subprocess.run(
        [node, "scripts/site/check_widget_runtime_links.mjs"],
        cwd=ROOT,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
