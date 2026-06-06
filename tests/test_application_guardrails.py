from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_application_guardrails() -> None:
    subprocess.run([sys.executable, "scripts/check_application_guardrails.py"], cwd=ROOT, check=True)
