from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_site_dictionary_links_resolve() -> None:
    subprocess.run([sys.executable, "scripts/site/export_site_data.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/site/check_site_dictionary_links.py"], cwd=ROOT, check=True)
