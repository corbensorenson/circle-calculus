from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_widget_python_parity() -> None:
    subprocess.run([sys.executable, "scripts/site/check_widget_python_parity.py"], cwd=ROOT, check=True)
