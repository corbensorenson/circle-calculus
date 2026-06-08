from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_capability_showcase_contract() -> None:
    subprocess.run([sys.executable, "scripts/check_capability_showcase.py"], cwd=ROOT, check=True)
