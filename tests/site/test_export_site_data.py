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
        "glyph_index.json",
        "generator_index.json",
        "phase4_targets.json",
        "phase5_targets.json",
        "phase6_targets.json",
        "phase7_targets.json",
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
    assert "CC-T0001" in {item["id"] for item in dictionary_by_id["CC-0001"]["used_by_theorems"]}
    assert "PAPER_01_FINITE_CIRCLES" in {item["id"] for item in dictionary_by_id["CC-0001"]["used_by_papers"]}
    assert "finite_circle_rotator" in {item["id"] for item in dictionary_by_id["CC-0001"]["used_by_widgets"]}

    widgets = json.loads((generated / "widget_index.json").read_text())
    widget_ids = {item["id"] for item in widgets["widgets"]}
    assert "finite_circle_rotator" in widget_ids
    assert "prime_full_coil_explorer" in widget_ids
    assert "sphere_grid_placeholder" in widget_ids
    assert "hopf_hidden_phase" in widget_ids
    assert "learned_content_gate_retrieval" in widget_ids
    assert "loop_exit_certificate" in widget_ids
    assert "periodic_winding_dynamics" in widget_ids
    assert "orbit_family_generator" in widget_ids

    glyphs = json.loads((generated / "glyph_index.json").read_text())
    glyph_by_id = {item["id"]: item for item in glyphs["glyphs"]}
    assert glyph_by_id["glyph:c13_stride5_period"]["status_label"] == "Lean-proved"
    assert glyph_by_id["glyph:s15_roadmap_marker"]["status_label"] != "Lean-proved"

    generators = json.loads((generated / "generator_index.json").read_text())
    generator_by_id = {item["id"]: item for item in generators["generators"]}
    assert generator_by_id["finite_circle_diagram"]["generatedObject"]["edges"][-1]["target"] == 0
    assert generator_by_id["physics_loop_diagram"]["generatedObject"]["closed"]
    assert generator_by_id["orbit_decomposition"]["generatedObject"][0] == [0, 8, 4]
    assert generator_by_id["proof_glyph"]["generatedObject"]["theorem_id"] == "CC-T0005"

    targets = json.loads((generated / "phase4_targets.json").read_text())
    target_ids = {item["id"] for item in targets["targets"]}
    assert "P4-S1-001" in target_ids
    assert "P4-APP-002" in target_ids

    phase5 = json.loads((generated / "phase5_targets.json").read_text())
    phase5_ids = {item["id"] for item in phase5["targets"]}
    assert "P5-EDGE-001" in phase5_ids
    assert "P5-EDGE-008" in phase5_ids

    phase6 = json.loads((generated / "phase6_targets.json").read_text())
    phase6_ids = {item["id"] for item in phase6["targets"]}
    assert "P6-SWEEP-001" in phase6_ids

    phase7 = json.loads((generated / "phase7_targets.json").read_text())
    phase7_ids = {item["id"] for item in phase7["targets"]}
    assert "P7-PHYS-001" in phase7_ids
    assert "P7-GEN-001" in phase7_ids
