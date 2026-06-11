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
        "theseus_hive_ai_contracts.json",
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

    theseus_contracts = json.loads((generated / "theseus_hive_ai_contracts.json").read_text())
    assert theseus_contracts["schema_id"] == "circle_calculus.theseus_hive_ai_contracts.v0"
    contract_kinds = {item["kind"] for item in theseus_contracts["contracts"]}
    assert "recurrence_schedule" in contract_kinds
    assert "seed_rule_exact_regeneration" in contract_kinds

    capabilities = json.loads((generated / "capability_showcase.json").read_text())
    capability_by_id = {item["id"]: item for item in capabilities["capabilities"]}
    route_by_id = {item["id"]: item for item in capabilities["portfolio_routes"]}
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
    assert capability_by_id["SHOW-001"]["theorem_ref_contract"][
        "proved_and_paper_backed_count"
    ] == len(capability_by_id["SHOW-001"]["theorem_ids"])
    assert capability_by_id["SHOW-001"]["theorem_ref_contract"][
        "unproved_or_unbacked_ids"
    ] == []
    assert {
        ref["id"]: tuple(ref["carried_by_papers"])
        for ref in capability_by_id["SHOW-001"]["theorem_ref_contract"]["refs"]
    } == {
        "CC-T0062": ("PAPER_ERDOS_01_ZERO_SUM_CIRCLES",),
        "CC-T0063": ("PAPER_ERDOS_01_ZERO_SUM_CIRCLES",),
    }
    assert capability_by_id["SHOW-001"]["source_ref_contract"]["backed_count"] == len(
        capability_by_id["SHOW-001"]["source_refs"]
    )
    assert capability_by_id["SHOW-001"]["source_ref_contract"]["unbacked_refs"] == []
    assert {
        ref["backing"]
        for ref in capability_by_id["SHOW-001"]["source_ref_contract"]["refs"]
    } == {"lean_sidecar_import", "source_trail"}
    assert capability_by_id["SHOW-001"]["living_book_ref_contract"][
        "backed_page_count"
    ] == len(capability_by_id["SHOW-001"]["living_book_refs"])
    assert capability_by_id["SHOW-001"]["living_book_ref_contract"][
        "unbacked_pages"
    ] == []
    assert capability_by_id["SHOW-001"]["living_book_ref_contract"]["pages"][0][
        "carries_showcase_ref"
    ]
    assert capability_by_id["SHOW-001"]["living_book_ref_contract"]["pages"][0][
        "carries_advertised_theorem"
    ]
    assert capability_by_id["SHOW-010"]["living_book_ref_contract"][
        "backed_widget_count"
    ] == capability_by_id["SHOW-010"]["evidence_counts"]["living_book_widget_count"]
    assert capability_by_id["SHOW-009"]["evidence_counts"]["living_book_widget_count"] == 4
    assert capability_by_id["SHOW-011"]["evidence_counts"]["living_book_page_count"] == 1
    assert all(
        item["claim_contract"]["ready_to_advertise"]
        for item in capabilities["capabilities"]
    )
    assert all(
        item["claim_language_contract"]["ready_to_advertise"]
        for item in capabilities["capabilities"]
    )
    assert all(
        item["claim_language_contract"]["flagged_phrases"] == []
        for item in capabilities["capabilities"]
    )
    assert all(
        item["value_proposition_contract"]["ready_to_advertise"]
        for item in capabilities["capabilities"]
    )
    assert all(
        item["proof_trail_contract"]["ready_to_advertise"]
        for item in capabilities["capabilities"]
    )
    assert all(
        item["review_packet_contract"]["ready_to_review"]
        for item in capabilities["capabilities"]
    )
    assert all(
        item["parity_value_comparison_contract"]["ready_to_review"]
        for item in capabilities["capabilities"]
    )
    assert capability_by_id["SHOW-001"]["value_proposition_contract"]["role_checks"][
        "standard_math_parity"
    ]["ready"]
    assert capability_by_id["SHOW-001"]["value_proposition_contract"]["role_checks"][
        "standard_math_parity"
    ]["evidence"] == "theorems 2/2"
    assert not capability_by_id["SHOW-009"]["value_proposition_contract"]["role_checks"][
        "standard_math_parity"
    ]["required"]
    assert capability_by_id["SHOW-009"]["value_proposition_contract"]["role_checks"][
        "circle_native_value"
    ]["ready"]
    assert capability_by_id["SHOW-010"]["value_proposition_contract"]["role_checks"][
        "application_guardrail"
    ]["ready"]
    assert capability_by_id["SHOW-001"]["proof_trail_contract"]["passed_step_count"] == (
        capability_by_id["SHOW-001"]["proof_trail_contract"]["total_step_count"]
    )
    assert [
        step["id"]
        for step in capability_by_id["SHOW-001"]["proof_trail_contract"]["steps"]
    ] == [
        "paper_backing",
        "theorem_refs",
        "source_refs",
        "executable_refs",
        "living_book_refs",
        "role_value",
        "claim_language",
    ]
    assert capability_by_id["SHOW-001"]["review_packet_contract"]["ready_section_count"] == (
        capability_by_id["SHOW-001"]["review_packet_contract"]["total_section_count"]
    )
    assert [
        section["id"]
        for section in capability_by_id["SHOW-001"]["review_packet_contract"]["sections"]
    ] == [
        "claim_scope_boundary",
        "paper_trail",
        "theorem_trail",
        "source_trail",
        "example_command",
        "living_book_route",
        "local_verification_gates",
    ]
    assert capability_by_id["SHOW-001"]["review_packet_contract"]["sections"][4][
        "command"
    ] == (
        "python -m pytest "
        "sidecars/PAPER_ERDOS_01_ZERO_SUM_CIRCLES/python/test_zero_sum_circle_examples.py"
    )
    assert capability_by_id["SHOW-001"]["parity_value_comparison_contract"][
        "ready_section_count"
    ] == (
        capability_by_id["SHOW-001"]["parity_value_comparison_contract"][
            "total_section_count"
        ]
    )
    assert [
        section["id"]
        for section in capability_by_id["SHOW-001"][
            "parity_value_comparison_contract"
        ]["sections"]
    ] == [
        "standard_reference",
        "circle_expression",
        "circle_native_value",
        "proof_backing",
        "review_entry",
        "advertising_boundary",
    ]
    assert capability_by_id["SHOW-001"]["parity_value_comparison_contract"][
        "standard_parity_claimed"
    ]
    assert capability_by_id["SHOW-001"]["parity_value_comparison_contract"][
        "circle_native_claimed"
    ]
    show_001_theorem_contract = capability_by_id["SHOW-001"]["theorem_ref_contract"]
    show_001_source_contract = capability_by_id["SHOW-001"]["source_ref_contract"]
    show_001_living_contract = capability_by_id["SHOW-001"][
        "living_book_ref_contract"
    ]
    show_001_counts = capability_by_id["SHOW-001"]["evidence_counts"]
    assert capability_by_id["SHOW-001"]["parity_value_comparison_contract"][
        "sections"
    ][3]["evidence"] == (
        f"papers {show_001_counts['paper_count']}; "
        f"theorem refs "
        f"{show_001_theorem_contract['proved_and_paper_backed_count']}/"
        f"{show_001_theorem_contract['total_count']}; "
        f"sources {show_001_source_contract['backed_count']}/"
        f"{show_001_source_contract['total_count']}; "
        f"executables {show_001_counts['executable_count']}; "
        f"Living Book pages {show_001_living_contract['backed_page_count']}/"
        f"{show_001_living_contract['total_page_count']}"
    )
    assert capability_by_id["SHOW-001"]["claim_contract"]["status"] == "ready"
    assert capability_by_id["SHOW-001"]["claim_contract"]["passed_gate_count"] == (
        capability_by_id["SHOW-001"]["claim_contract"]["total_gate_count"]
    )
    assert "paper_backing" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "verification_recipe" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "claim_language_guardrail" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "value_proposition" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "proof_trail" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "review_packet" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert "parity_value_comparison" in {
        gate["id"] for gate in capability_by_id["SHOW-001"]["claim_contract"]["gates"]
    }
    assert capability_by_id["SHOW-001"]["verification_recipe"]["pytest_command"] == (
        "python -m pytest "
        "sidecars/PAPER_ERDOS_01_ZERO_SUM_CIRCLES/python/test_zero_sum_circle_examples.py"
    )
    assert capability_by_id["SHOW-001"]["verification_recipe"]["lean_command"] == "lake build"
    assert capability_by_id["SHOW-001"]["verification_recipe"]["site_command"] == "make sitecheck"
    assert summary["claim_contract_summary"]["ready_count"] == len(capabilities["capabilities"])
    assert summary["claim_contract_summary"]["incomplete_count"] == 0
    assert summary["claim_contract_summary"]["gate_failure_counts"] == {}
    assert summary["route_summary"]["route_count"] == 4
    assert summary["route_summary"]["ready_count"] == 4
    assert summary["route_summary"]["incomplete_count"] == 0
    assert summary["route_summary"]["ready_dossier_count"] == 4
    assert summary["route_summary"]["incomplete_dossier_ids"] == []
    assert summary["route_summary"]["ready_impact_summary_count"] == 4
    assert summary["route_summary"]["incomplete_impact_summary_ids"] == []
    assert summary["route_summary"]["unknown_capability_ids"] == []
    hard_math_route = route_by_id["ROUTE-001"]
    assert hard_math_route["capability_ids"] == [
        "SHOW-001",
        "SHOW-002",
        "SHOW-003",
        "SHOW-004",
        "SHOW-005",
    ]
    assert hard_math_route["route_contract"]["ready_to_advertise"]
    assert hard_math_route["route_contract"]["claim_language_contract"][
        "ready_to_advertise"
    ]
    assert hard_math_route["route_contract"]["claim_language_contract"][
        "flagged_phrases"
    ] == []
    assert hard_math_route["route_contract"]["capability_count"] == 5
    assert hard_math_route["route_contract"]["ready_capability_count"] == 5
    assert hard_math_route["route_contract"]["unknown_capability_ids"] == []
    assert hard_math_route["route_contract"]["incomplete_capability_ids"] == []
    assert hard_math_route["route_contract"]["theorem_refs"][
        "proved_and_paper_backed_count"
    ] == hard_math_route["route_contract"]["theorem_refs"]["total_count"]
    assert hard_math_route["route_contract"]["source_refs"]["backed_count"] == (
        hard_math_route["route_contract"]["source_refs"]["total_count"]
    )
    assert hard_math_route["route_contract"]["review_packets"] == {
        "ready_count": 5,
        "total_count": 5,
        "incomplete_capability_ids": [],
    }
    assert hard_math_route["route_review_dossier_contract"]["ready_section_count"] == (
        hard_math_route["route_review_dossier_contract"]["total_section_count"]
    )
    assert [
        section["id"]
        for section in hard_math_route["route_review_dossier_contract"]["sections"]
    ] == [
        "route_scope_boundary",
        "capability_review_packets",
        "standard_parity_surface",
        "circle_native_surface",
        "proof_provenance_surface",
        "route_reproduction_command",
        "advertising_guardrails",
    ]
    assert hard_math_route["route_review_dossier_contract"]["role_counts"][
        "standard_math_parity"
    ] == {"ready_count": 5, "total_count": 5}
    assert hard_math_route["route_review_dossier_contract"]["role_counts"][
        "circle_native_value"
    ] == {"ready_count": 5, "total_count": 5}
    assert hard_math_route["route_review_dossier_contract"]["sections"][5][
        "command"
    ] == (
        "python -m pytest "
        "sidecars/PAPER_ERDOS_01_ZERO_SUM_CIRCLES/python/test_zero_sum_circle_examples.py "
        "sidecars/PAPER_ERDOS_02_KATONA_EKR_CIRCLE_METHOD/python/test_katona_ekr_examples.py "
        "sidecars/PAPER_ERDOS_03_ROTH_THREE_AP_CIRCLES/python/test_roth_three_ap_examples.py "
        "sidecars/PAPER_ERDOS_04_HALES_JEWETT_RAMSEY_CIRCLES/python/test_ramsey_hj_examples.py "
        "sidecars/PAPER_ERDOS_05_UNIT_DISTANCE_CIRCULANT_GRAPHS/python/test_circulant_graph_examples.py"
    )
    assert hard_math_route["route_impact_summary_contract"]["ready_section_count"] == (
        hard_math_route["route_impact_summary_contract"]["total_section_count"]
    )
    assert [
        section["id"]
        for section in hard_math_route["route_impact_summary_contract"]["sections"]
    ] == [
        "audience_signal",
        "standard_interest_surface",
        "circle_native_value_surface",
        "proof_backing_counts",
        "review_path",
        "advertising_boundary",
    ]
    hard_route_counts = hard_math_route["route_contract"]["unique_evidence_counts"]
    assert hard_math_route["route_impact_summary_contract"]["sections"][3][
        "evidence"
    ] == (
        f"papers {hard_route_counts['paper_count']}; "
        f"theorem refs {hard_route_counts['theorem_count']}; "
        f"source refs {hard_route_counts['source_count']}; "
        f"executables {hard_route_counts['executable_count']}; "
        f"Living Book pages {hard_route_counts['living_book_page_count']}"
    )
    assert hard_math_route["route_impact_summary_contract"]["summary_lines"][1].startswith(
        "Capability surface: 5 route lanes across Additive combinatorics"
    )
    assert len(
        hard_math_route["route_impact_summary_contract"]["standard_interest_refs"]
    ) == 5
    assert len(
        hard_math_route["route_impact_summary_contract"]["circle_native_value_refs"]
    ) == 5
    systems_route = route_by_id["ROUTE-004"]
    assert systems_route["route_contract"]["ready_to_advertise"]
    assert systems_route["route_contract"]["claim_language_contract"][
        "ready_to_advertise"
    ]
    assert systems_route["route_contract"]["living_book_refs"][
        "backed_widget_count"
    ] == systems_route["route_contract"]["living_book_refs"]["total_widget_count"]
    backing_summary = summary["backing_contract_summary"]
    assert backing_summary["ready_to_advertise"]
    total_theorem_refs = sum(
        len(item["theorem_ids"]) for item in capabilities["capabilities"]
    )
    assert backing_summary["theorem_refs"]["total_count"] == total_theorem_refs
    assert (
        backing_summary["theorem_refs"]["proved_and_paper_backed_count"]
        == total_theorem_refs
    )
    assert backing_summary["theorem_refs"]["unproved_or_unbacked_refs"] == []
    total_source_refs = sum(
        len(item["source_refs"]) for item in capabilities["capabilities"]
    )
    assert backing_summary["source_refs"]["total_count"] == total_source_refs
    assert backing_summary["source_refs"]["backed_count"] == total_source_refs
    assert backing_summary["source_refs"]["unbacked_refs"] == []
    total_living_pages = sum(
        len({ref["page"] for ref in item["living_book_refs"]})
        for item in capabilities["capabilities"]
    )
    total_living_widgets = sum(
        len(
            {
                widget_id
                for ref in item["living_book_refs"]
                for widget_id in ref.get("widget_ids", [])
            }
        )
        for item in capabilities["capabilities"]
    )
    assert backing_summary["living_book_refs"]["total_page_count"] == total_living_pages
    assert (
        backing_summary["living_book_refs"]["backed_page_count"]
        == total_living_pages
    )
    assert (
        backing_summary["living_book_refs"]["total_widget_count"]
        == total_living_widgets
    )
    assert (
        backing_summary["living_book_refs"]["backed_widget_count"]
        == total_living_widgets
    )
    assert backing_summary["living_book_refs"]["unbacked_pages"] == []
    assert backing_summary["living_book_refs"]["unbacked_widgets"] == []
    assert backing_summary["review_packets"] == {
        "ready_count": len(capabilities["capabilities"]),
        "total_count": len(capabilities["capabilities"]),
        "incomplete_capability_ids": [],
    }
    assert backing_summary["parity_value_comparisons"] == {
        "ready_count": len(capabilities["capabilities"]),
        "total_count": len(capabilities["capabilities"]),
        "incomplete_capability_ids": [],
    }

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
