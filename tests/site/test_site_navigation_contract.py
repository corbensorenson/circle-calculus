from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_site_navigation_contract() -> None:
    subprocess.run([sys.executable, "scripts/site/check_site_navigation_contract.py"], cwd=ROOT, check=True)
