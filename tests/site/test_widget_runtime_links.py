from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_widget_runtime_links() -> None:
    subprocess.run([sys.executable, "scripts/site/check_widget_runtime_links.py"], cwd=ROOT, check=True)
