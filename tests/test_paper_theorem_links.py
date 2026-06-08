from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_paper_theorem_links_contract() -> None:
    subprocess.run([sys.executable, "scripts/check_paper_theorem_links.py"], cwd=ROOT, check=True)
