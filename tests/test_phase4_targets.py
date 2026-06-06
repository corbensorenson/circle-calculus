from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_phase4_targets() -> None:
    subprocess.run([sys.executable, "scripts/check_phase4_targets.py"], cwd=ROOT, check=True)
