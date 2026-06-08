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
        "capability_showcase.json",
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
    assert "phase_channel_baseline" in widget_ids
    assert "learned_feature_baseline" in widget_ids
    assert "harmonic_feature_baseline" in widget_ids
    assert "backend_parity_fixture" in widget_ids

    glyphs = json.loads((generated / "glyph_index.json").read_text())
    glyph_by_id = {item["id"]: item for item in glyphs["glyphs"]}
    assert glyph_by_id["glyph:c13_stride5_period"]["status_label"] == "Lean-proved"
    assert glyph_by_id["glyph:s15_roadmap_marker"]["status_label"] != "Lean-proved"

    generators = json.loads((generated / "generator_index.json").read_text())
    generator_by_id = {item["id"]: item for item in generators["generators"]}
    assert generator_by_id["finite_circle_diagram"]["generatedObject"]["edges"][-1]["target"] == 0
    assert generator_by_id["physics_loop_diagram"]["generatedObject"]["closed"]
    assert generator_by_id["orbit_decomposition"]["generatedObject"][0] == [0, 8, 4]
    assert "GEN-T0003" in generator_by_id["orbit_decomposition"]["theoremIds"]
    assert "GEN-T0013" in generator_by_id["orbit_decomposition"]["theoremIds"]
    assert "GEN-T0021" in generator_by_id["coil_orbit"]["theoremIds"]
    assert generator_by_id["proof_glyph"]["generatedObject"]["theorem_id"] == "CC-T0005"
    assert "GEN-T0004" in generator_by_id["proof_glyph"]["theoremIds"]

    capabilities = json.loads((generated / "capability_showcase.json").read_text())
    capability_by_id = {item["id"]: item for item in capabilities["capabilities"]}
    summary = capabilities["portfolio_summary"]
    assert summary["capability_count"] == len(capabilities["capabilities"])
    assert summary["role_counts"]["standard_math_parity"] == sum(
        "standard_math_parity" in item["portfolio_roles"]
        for item in capabilities["capabilities"]
    )
    assert summary["role_counts"]["circle_native_value"] == sum(
        "circle_native_value" in item["portfolio_roles"]
        for item in capabilities["capabilities"]
    )
    assert summary["role_counts"]["application_guardrail"] == sum(
        "application_guardrail" in item["portfolio_roles"]
        for item in capabilities["capabilities"]
    )
    assert summary["proof_provenance_counts"]["mathlib_bridge"] == sum(
        item["proof_provenance_kind"] == "mathlib_bridge"
        for item in capabilities["capabilities"]
    )
    assert summary["proof_provenance_counts"]["project_native"] == sum(
        item["proof_provenance_kind"] == "project_native"
        for item in capabilities["capabilities"]
    )
    unique_theorems = {
        theorem_id
        for item in capabilities["capabilities"]
        for theorem_id in item["theorem_ids"]
    }
    assert summary["unique_evidence_counts"]["theorem_count"] == len(unique_theorems)
    assert "site/chapters/applications/erdos_bridges.qmd" in summary["unique_living_book_pages"]
    assert capability_by_id["SHOW-001"]["evidence_counts"]["theorem_count"] == len(
        capability_by_id["SHOW-001"]["theorem_ids"]
    )
    assert capability_by_id["SHOW-009"]["evidence_counts"]["living_book_widget_count"] == 4
    assert capability_by_id["SHOW-011"]["evidence_counts"]["living_book_page_count"] == 1
    assert all(
        item["claim_contract"]["ready_to_advertise"]
        for item in capabilities["capabilities"]
    )
    assert capability_by_id["SHOW-001"]["claim_contract"]["status"] == "ready"
    assert capability_by_id["SHOW-001"]["claim_contract"]["passed_gate_count"] == (
        capability_by_id["SHOW-001"]["claim_contract"]["total_gate_count"]
    )
    assert "paper_backing" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert summary["claim_contract_summary"]["ready_count"] == len(capabilities["capabilities"])
    assert summary["claim_contract_summary"]["incomplete_count"] == 0
    assert summary["claim_contract_summary"]["gate_failure_counts"] == {}

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
