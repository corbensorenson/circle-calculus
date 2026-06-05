from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )


def test_export_site_data_writes_required_indexes() -> None:
    run_script("scripts/site/export_site_data.py")
    generated = ROOT / "site" / "data" / "generated"
    for name in [
        "theorem_manifest.json",
        "dictionary.json",
        "dimensions.json",
        "paper_index.json",
        "widget_index.json",
        "phase4_targets.json",
    ]:
        assert (generated / name).exists()

    theorems = json.loads((generated / "theorem_manifest.json").read_text())
    theorem_by_id = {item["id"]: item for item in theorems["theorems"]}
    assert theorem_by_id["CC-T0001"]["canonical_status"] == "proved"
    assert theorem_by_id["CC-T0002"]["lean_name"] == "Circle.rot_comp"
    assert theorem_by_id["CC-T0002"]["lean_source"] == "Circle/Core/Rotation.lean"
    assert theorem_by_id["CC-T0002"]["lean_source_line"] > 0

    dictionary = json.loads((generated / "dictionary.json").read_text())
    dictionary_by_id = {item["id"]: item for item in dictionary["entries"]}
    assert dictionary_by_id["CC-0001"]["name"] == "Circle"

    widgets = json.loads((generated / "widget_index.json").read_text())
    widget_ids = {item["id"] for item in widgets["widgets"]}
    assert "finite_circle_rotator" in widget_ids
    assert "prime_full_coil_explorer" in widget_ids

    targets = json.loads((generated / "phase4_targets.json").read_text())
    target_ids = {item["id"] for item in targets["targets"]}
    assert "P4-S1-001" in target_ids
    assert "P4-APP-002" in target_ids
