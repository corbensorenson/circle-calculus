from __future__ import annotations

import re
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from site_lib import GENERATED, ROOT, load_yaml, repo_relative, write_json

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DECL_RE = re.compile(r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive)\s+([A-Za-z0-9_'.]+)")

STATUS_MAP = {
    "proved": "proved",
    "lean_proved": "proved",
    "exploratory_python": "exploratory",
    "stated": "planned",
    "lean_stated": "planned",
    "planned": "planned",
    "paper_draft": "draft",
    "paper_complete": "draft",
    "blocked": "blocked",
    "deferred": "deferred",
}


def canonical_status(status: str) -> str:
    return STATUS_MAP.get(status, "planned")


def theorem_manifest_paths() -> list[Path]:
    candidates = sorted((ROOT / "manifests").glob("**/*.yaml"))
    return [path for path in candidates if path.name not in {"paper_manifest.yaml", "dimension_index.yaml"}]


def lean_declaration_sources() -> dict[str, dict[str, object]]:
    sources: dict[str, dict[str, object]] = {}
    for path in sorted((ROOT / "Circle").glob("**/*.lean")):
        namespace_stack: list[str] = []
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("namespace "):
                namespace_stack.append(stripped.split(None, 1)[1])
                continue
            if stripped == "end" or stripped.startswith("end "):
                if namespace_stack:
                    namespace_stack.pop()
                continue
            match = DECL_RE.match(line)
            if match:
                local = match.group(1)
                full = ".".join(namespace_stack + [local]) if namespace_stack else local
                sources[full] = {
                    "path": repo_relative(path),
                    "line": line_number,
                }
    return sources


def export_theorems() -> dict:
    theorems: list[dict] = []
    seen: set[str] = set()
    lean_sources = lean_declaration_sources()
    for path in theorem_manifest_paths():
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if not theorem_id or theorem_id in seen:
                continue
            seen.add(theorem_id)
            item = dict(theorem)
            item["source_manifest"] = repo_relative(path)
            item["original_status"] = item.get("status", "")
            item["canonical_status"] = canonical_status(item.get("status", "planned"))
            lean_source = lean_sources.get(item.get("lean_name", ""))
            if lean_source:
                item["lean_source"] = lean_source["path"]
                item["lean_source_line"] = lean_source["line"]
            theorems.append(item)
    return {"theorems": sorted(theorems, key=lambda item: item["id"])}


def dictionary_paths() -> list[Path]:
    paths = [ROOT / "dictionary" / "circle_dictionary.yaml"]
    paths.extend(sorted((ROOT / "dictionary" / "dimensions").glob("*.yaml")))
    return [path for path in paths if path.exists()]


def export_dictionary() -> dict:
    entries: list[dict] = []
    seen: set[str] = set()
    for path in dictionary_paths():
        data = load_yaml(path)
        for entry in data.get("entries", []):
            entry_id = entry.get("id")
            if not entry_id or entry_id in seen:
                continue
            seen.add(entry_id)
            item = dict(entry)
            item["source_dictionary"] = repo_relative(path)
            entries.append(item)
    return {"entries": sorted(entries, key=lambda item: item["id"])}


def export_dimensions() -> dict:
    path = ROOT / "manifests" / "dimensions" / "dimension_index.yaml"
    if not path.exists():
        return {"dimensions": []}
    data = load_yaml(path)
    return {"dimensions": data.get("dimensions", [])}


def paper_path_for_id(paper_id: str) -> str:
    for path in sorted((ROOT / "papers").glob("**/*.md")):
        if path.stem == paper_id:
            return repo_relative(path)
    return ""


def export_papers() -> dict:
    path = ROOT / "manifests" / "paper_manifest.yaml"
    if not path.exists():
        return {"papers": []}
    data = load_yaml(path)
    papers: list[dict] = []
    for paper in data.get("papers", []):
        item = dict(paper)
        item["path"] = paper_path_for_id(item.get("id", ""))
        papers.append(item)
    return {"papers": papers}


def export_widget_index() -> dict:
    widgets = [
        {
            "id": "finite_circle_rotator",
            "path": "site/widgets/S1/finite_circle_rotator.js",
            "theorem_ids": [],
            "dictionary_ids": ["CC-0001", "CC-0002"],
            "python_reference": "circle_math.finite.Circle.node",
        },
        {
            "id": "rotation_composition",
            "path": "site/widgets/S1/rotation_composition.js",
            "theorem_ids": ["CC-T0002"],
            "dictionary_ids": ["CC-0101"],
            "python_reference": "circle_math.finite.Circle.rot",
        },
        {
            "id": "coil_orbit_explorer",
            "path": "site/widgets/S1/coil_orbit_explorer.js",
            "theorem_ids": ["CC-T0005"],
            "dictionary_ids": ["CC-0201", "CC-0202", "CC-0205"],
            "python_reference": "circle_math.finite.Circle.orbit",
        },
        {
            "id": "period_gcd_visualizer",
            "path": "site/widgets/S1/period_gcd_visualizer.js",
            "theorem_ids": ["CC-T0006"],
            "dictionary_ids": ["CC-0205", "CC-0207", "CC-0208"],
            "python_reference": "circle_math.finite.Circle.orbit_decomposition",
        },
        {
            "id": "prime_full_coil_explorer",
            "path": "site/widgets/S1/prime_full_coil_explorer.js",
            "theorem_ids": ["CC-T0007"],
            "dictionary_ids": ["CC-0206"],
            "python_reference": "circle_math.finite.Circle.is_full_coil",
        },
        {
            "id": "winding_lift_explorer",
            "path": "site/widgets/S1/winding_lift_explorer.js",
            "theorem_ids": ["CC-T0009"],
            "dictionary_ids": ["CC-0301"],
            "python_reference": "circle_math.winding.lift",
        },
        {
            "id": "sphere_grid_placeholder",
            "path": "site/widgets/S2/sphere_grid_placeholder.js",
            "theorem_ids": [],
            "dictionary_ids": ["S2-0001", "S2-0002"],
            "python_reference": "",
        },
        {
            "id": "seed_rule_diagram_generator",
            "path": "site/widgets/generative/seed_rule_diagram_generator.js",
            "theorem_ids": [
                "CC-T0001",
                "CC-T0002",
                "CC-T0005",
                "CC-T0006",
                "PHYS-T0005",
                "PHYS-T0012",
                "P2G-T0001",
                "P2G-T0002",
                "P2G-T0003",
                "GEN-T0002",
                "GEN-T0003",
                "GEN-T0004",
                "GEN-T0006",
                "GEN-T0008",
                "GEN-T0009",
                "GEN-T0017",
                "GEN-T0019",
            ],
            "dictionary_ids": [
                "CC-0001",
                "CC-0002",
                "CC-0201",
                "CC-0205",
                "CC-0208",
                "COMMON-0033",
                "COMMON-0060",
                "COMMON-0061",
                "COMMON-0062",
                "COMMON-0063",
                "COMMON-0064",
                "COMMON-0066",
            ],
            "python_reference": "circle_math.generative.finite_circle_diagram_generator; circle_math.generative.physics_loop_diagram_generator; circle_math.generative.coil_orbit_generator; circle_math.generative.orbit_decomposition_generator; circle_math.generative.proof_glyph_generator",
        },
        {
            "id": "generator_comparison_search",
            "path": "site/widgets/generative/generator_comparison_search.js",
            "theorem_ids": [
                "GEN-T0001",
                "GEN-T0005",
                "GEN-T0017",
                "GEN-T0018",
                "GEN-T0019",
                "GEN-T0020",
                "GEN-T0022",
                "GEN-T0023",
                "GEN-T0024",
                "GEN-T0025",
                "GEN-T0026",
                "GEN-T0027",
            ],
            "dictionary_ids": ["COMMON-0064", "COMMON-0065", "COMMON-0066"],
            "python_reference": "circle_math.generative.compare_generator_to_explicit; circle_math.generative.bounded_generator_search; circle_math.generative.finite_circle_generator",
        },
        {
            "id": "orbit_family_generator",
            "path": "site/widgets/generative/orbit_family_generator.js",
            "theorem_ids": [
                "GEN-T0003",
                "GEN-T0006",
                "GEN-T0007",
                "GEN-T0008",
                "GEN-T0009",
                "GEN-T0010",
                "GEN-T0011",
                "GEN-T0012",
                "GEN-T0013",
            ],
            "dictionary_ids": ["CC-0205", "CC-0208", "COMMON-0064", "COMMON-0066"],
            "python_reference": "circle_math.generative.orbit_decomposition_generator; circle_math.generative.regenerate",
        },
        {
            "id": "proof_glyph_certificate",
            "path": "site/widgets/generative/proof_glyph_certificate.js",
            "theorem_ids": ["P2G-T0001", "P2G-T0002", "P2G-T0003", "P2G-T0004", "CC-T0005"],
            "dictionary_ids": ["COMMON-0033", "COMMON-0064", "COMMON-0066"],
            "python_reference": "circle_math.generative.proof_glyph_generator; circle_math.generative.regenerate",
        },
        {
            "id": "loop_recurrence_budget",
            "path": "site/widgets/ai/loop_recurrence_budget.js",
            "theorem_ids": [
                "AIM-T0018",
                "AIM-T0019",
                "AIM-T0020",
                "AIM-T0021",
                "AIM-T0022",
                "AIM-T0023",
                "AIM-T0025",
                "AIM-T0026",
                "AIM-T0027",
                "AIM-T0028",
                "AIM-T0029",
                "AIM-T0030",
            ],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0054",
                "COMMON-0059",
                "COMMON-0067",
            ],
            "python_reference": "circle_math.applications.circle_ai.loop_required_steps; circle_math.applications.circle_ai.token_recurrence_budget; circle_math.applications.circle_ai.training_free_loop_budget",
        },
        {
            "id": "loop_exit_certificate",
            "path": "site/widgets/ai/loop_exit_certificate.js",
            "theorem_ids": [
                "AIM-T0012",
                "AIM-T0013",
                "AIM-T0014",
                "AIM-T0015",
                "AIM-T0016",
                "AIM-T0017",
                "AIM-T0024",
                "AIM-T0029",
                "AIM-T0030",
            ],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0054",
                "COMMON-0059",
                "COMMON-0067",
            ],
            "python_reference": "circle_math.applications.circle_ai.loop_required_steps; circle_math.applications.circle_ai.loop_score_trace; circle_math.applications.circle_ai.loop_exit_step; circle_math.applications.circle_ai.loop_exit_certificate",
        },
        {
            "id": "training_free_loop_wrapper",
            "path": "site/widgets/ai/training_free_loop_wrapper.js",
            "theorem_ids": ["AIM-T0010", "AIM-T0011", "AIM-T0019", "AIM-T0020", "AIM-T0023", "AIM-T0025", "AIM-T0028"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0054",
                "COMMON-0067",
            ],
            "python_reference": "circle_math.applications.circle_ai.training_free_loop_budget; circle_math.applications.circle_ai.training_free_loop_budgets; circle_math.applications.circle_ai.run_training_free_loop_wrapper_benchmark",
        },
        {
            "id": "token_level_recurrence",
            "path": "site/widgets/ai/token_level_recurrence.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022", "AIM-T0026", "AIM-T0027"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0059",
                "COMMON-0068",
                "COMMON-0069",
            ],
            "python_reference": "circle_math.applications.circle_ai.token_recurrence_budgets; circle_math.applications.circle_ai.active_token_counts_by_budget; circle_math.applications.circle_ai.recurrence_resolution_levels; circle_math.applications.circle_ai.run_token_level_recurrence_benchmark",
        },
        {
            "id": "learned_token_recurrence",
            "path": "site/widgets/ai/learned_token_recurrence.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0059",
                "COMMON-0068",
                "COMMON-0069",
            ],
            "python_reference": "circle_math.applications.circle_ai.fit_loop_budget_lookup; circle_math.applications.circle_ai.predict_loop_budget_lookup; circle_math.applications.circle_ai.run_learned_token_level_recurrence_benchmark",
        },
        {
            "id": "learned_middle_block_recurrence",
            "path": "site/widgets/ai/learned_middle_block_recurrence.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0059",
                "COMMON-0068",
                "COMMON-0070",
            ],
            "python_reference": "circle_math.applications.circle_ai.fit_loop_block_lookup; circle_math.applications.circle_ai.predict_loop_block_lookup; circle_math.applications.circle_ai.fit_loop_budget_lookup; circle_math.applications.circle_ai.predict_loop_budget_lookup; circle_math.applications.circle_ai.run_learned_middle_block_recurrence_benchmark",
        },
        {
            "id": "learned_multi_resolution_recurrence",
            "path": "site/widgets/ai/learned_multi_resolution_recurrence.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0059",
                "COMMON-0069",
                "COMMON-0070",
            ],
            "python_reference": "circle_math.applications.circle_ai.fit_loop_budget_lookup; circle_math.applications.circle_ai.predict_loop_budget_lookup; circle_math.applications.circle_ai.fit_recurrence_resolution_lookup; circle_math.applications.circle_ai.predict_recurrence_resolution_lookup; circle_math.applications.circle_ai.run_learned_multi_resolution_recurrence_benchmark",
        },
        {
            "id": "learned_recurrence_schedule",
            "path": "site/widgets/ai/learned_recurrence_schedule.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0070",
            ],
            "python_reference": "circle_math.applications.circle_ai.fit_loop_budget_lookup; circle_math.applications.circle_ai.predict_loop_budget_lookup; circle_math.applications.circle_ai.run_learned_recurrence_schedule_benchmark",
        },
        {
            "id": "phase_channel_baseline",
            "path": "site/widgets/ai/phase_channel_baseline.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0003", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0026", "COMMON-0027"],
            "python_reference": "circle_math.applications.circle_ai.phase_channel; circle_math.applications.circle_ai.run_phase_channel_benchmark; circle_math.applications.circle_ai.run_learned_phase_baseline_benchmark",
        },
        {
            "id": "learned_feature_baseline",
            "path": "site/widgets/ai/learned_feature_baseline.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0003", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0026", "COMMON-0027"],
            "python_reference": "circle_math.applications.circle_ai.fit_phase_lookup; circle_math.applications.circle_ai.predict_phase_lookup; circle_math.applications.circle_ai.run_learned_feature_baseline_benchmark",
        },
        {
            "id": "harmonic_feature_baseline",
            "path": "site/widgets/ai/harmonic_feature_baseline.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0026", "COMMON-0027", "COMMON-0046"],
            "python_reference": "circle_math.applications.circle_ai.harmonic_feature; circle_math.applications.circle_ai.fit_harmonic_feature_lookup; circle_math.applications.circle_ai.predict_harmonic_feature_lookup; circle_math.applications.circle_ai.run_harmonic_feature_baseline_benchmark",
        },
        {
            "id": "backend_parity_fixture",
            "path": "site/widgets/ai/backend_parity_fixture.js",
            "theorem_ids": ["AIA-T0001", "AIM-T0001", "AIM-T0015", "AIRA-T0001"],
            "dictionary_ids": [
                "COMMON-0026",
                "COMMON-0028",
                "COMMON-0030",
                "COMMON-0046",
                "COMMON-0047",
                "COMMON-0051",
                "COMMON-0052",
            ],
            "python_reference": "circle_math.applications.circle_ai.ai_backend_parity_cases; circle_math.applications.circle_ai.run_ai_backend_parity_check",
        },
        {
            "id": "cyclic_memory_slots",
            "path": "site/widgets/ai/cyclic_memory_slots.js",
            "theorem_ids": ["AIM-T0001", "AIM-T0002", "AIM-T0003", "AIM-T0004", "AIM-T0005"],
            "dictionary_ids": ["COMMON-0028", "COMMON-0029"],
            "python_reference": "circle_math.applications.circle_ai.memory_slot; circle_math.applications.circle_ai.memory_slot_loads; circle_math.applications.circle_ai.memory_slot_collision_count",
        },
        {
            "id": "coil_retrieval_reachability",
            "path": "site/widgets/ai/coil_retrieval_reachability.js",
            "theorem_ids": ["CC-T0002", "CC-T0005"],
            "dictionary_ids": ["COMMON-0047", "COMMON-0028", "COMMON-0029"],
            "python_reference": "circle_math.applications.circle_ai.coil_attention_path; circle_math.applications.circle_ai.local_window_indices; circle_math.applications.circle_ai.retrieval_target_index; circle_math.applications.circle_ai.retrieval_hit_rate",
        },
        {
            "id": "content_gated_retrieval",
            "path": "site/widgets/ai/content_gated_retrieval.js",
            "theorem_ids": ["CC-T0002", "CC-T0005"],
            "dictionary_ids": ["COMMON-0057", "COMMON-0047", "COMMON-0028"],
            "python_reference": "circle_math.applications.circle_ai.mixed_retrieval_target_lags; circle_math.applications.circle_ai.retrieval_hit_rate_by_lag; circle_math.applications.circle_ai.average_candidate_count; circle_math.applications.circle_ai.run_content_gated_retrieval_benchmark",
        },
        {
            "id": "learned_content_gate_retrieval",
            "path": "site/widgets/ai/learned_content_gate_retrieval.js",
            "theorem_ids": ["CC-T0002", "CC-T0005"],
            "dictionary_ids": ["COMMON-0057", "COMMON-0047", "COMMON-0028"],
            "python_reference": "circle_math.applications.circle_ai.content_route_label; circle_math.applications.circle_ai.fit_content_route_lookup; circle_math.applications.circle_ai.predict_content_route_lookup; circle_math.applications.circle_ai.run_learned_content_gate_retrieval_benchmark",
        },
        {
            "id": "multicoil_phase_explorer",
            "path": "site/widgets/ai/multicoil_phase_explorer.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0046", "COMMON-0026", "COMMON-0027"],
            "python_reference": "circle_math.applications.circle_ai.multicoil_phase; circle_math.applications.circle_ai.multicoil_cycle_length; circle_math.applications.circle_ai.multicoil_phase_label",
        },
        {
            "id": "rope_relative_phase",
            "path": "site/widgets/ai/rope_relative_phase.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0051", "COMMON-0050", "COMMON-0026"],
            "python_reference": "circle_math.applications.circle_ai.rope_relative_feature; circle_math.applications.circle_ai.run_rope_relative_phase_benchmark",
        },
        {
            "id": "adapter_parameter_budget",
            "path": "site/widgets/ai/adapter_parameter_budget.js",
            "theorem_ids": ["AIRA-T0001", "AIRA-T0002", "AIRA-T0004", "AIRA-T0005"],
            "dictionary_ids": ["COMMON-0056", "COMMON-0030", "COMMON-0031"],
            "python_reference": "circle_math.applications.circle_ai.dense_adapter_parameter_count; circle_math.applications.circle_ai.lora_adapter_parameter_count; circle_math.applications.circle_ai.block_cyclic_adapter_parameter_count; circle_math.applications.circle_ai.run_adapter_parameter_budget_benchmark",
        },
        {
            "id": "circulant_mixer_validation",
            "path": "site/widgets/ai/circulant_mixer_validation.js",
            "theorem_ids": [],
            "dictionary_ids": ["COMMON-0058", "COMMON-0056", "COMMON-0046"],
            "python_reference": "circle_math.applications.circle_ai.circulant_mixer_output; circle_math.applications.circle_ai.dense_circulant_matrix; circle_math.applications.circle_ai.run_circulant_mixer_benchmark",
        },
        {
            "id": "finite_path_algebra",
            "path": "site/widgets/physics/finite_path_algebra.js",
            "theorem_ids": [
                "PHYS-T0001",
                "PHYS-T0002",
                "PHYS-T0003",
                "PHYS-T0006",
                "PHYS-T0007",
                "PHYS-T0039",
                "PHYS-T0050",
                "PHYS-T0051",
            ],
            "dictionary_ids": ["COMMON-0060", "COMMON-0061", "COMMON-0063"],
            "python_reference": "circle_math.physics.GaugePath; circle_math.physics.GaugeEdge; circle_math.physics.path_holonomy; circle_math.physics.concat_paths; circle_math.physics.reverse_path; circle_math.physics.gauge_transform_path; circle_math.physics.transformed_holonomy_endpoint_prediction",
        },
        {
            "id": "finite_gauge_loop_holonomy",
            "path": "site/widgets/physics/finite_gauge_loop_holonomy.js",
            "theorem_ids": ["PHYS-T0004", "PHYS-T0005", "PHYS-T0012", "PHYS-T0045", "PHYS-T0047"],
            "dictionary_ids": [
                "COMMON-0060",
                "COMMON-0061",
                "COMMON-0062",
                "COMMON-0063",
            ],
            "python_reference": "circle_math.physics.square_plaquette_path; circle_math.physics.gauge_transform_path; circle_math.physics.path_holonomy",
        },
        {
            "id": "wilson_loop_certificate",
            "path": "site/widgets/physics/wilson_loop_certificate.js",
            "theorem_ids": ["PHYS-T0004", "PHYS-T0005", "PHYS-T0046", "PHYS-T0047", "PHYS-T0049"],
            "dictionary_ids": [
                "COMMON-0060",
                "COMMON-0061",
                "COMMON-0062",
                "COMMON-0063",
            ],
            "python_reference": "circle_math.physics.GaugePath; circle_math.physics.GaugeEdge; circle_math.physics.gauge_transform_path; circle_math.physics.path_holonomy; circle_math.physics.wilson_loop_certificate",
        },
        {
            "id": "hopf_hidden_phase",
            "path": "site/widgets/physics/hopf_hidden_phase.js",
            "theorem_ids": ["S3H-T0001", "S3H-T0002", "S3H-T0003", "S3H-T0004", "S3H-T0005", "S3H-T0006"],
            "dictionary_ids": ["S3H-0001", "S3H-0002", "S3H-W0001"],
            "python_reference": "circle_math.dimensions.hopf.normalize_pair; circle_math.dimensions.hopf.phase_rotate; circle_math.dimensions.hopf.hopf_map; circle_math.dimensions.hopf.hopf_phase_record",
        },
        {
            "id": "spin_sign_ambiguity",
            "path": "site/widgets/physics/spin_sign_ambiguity.js",
            "theorem_ids": ["S3S-T0001", "S3S-T0002", "S3S-T0003", "S3S-T0004", "S3S-T0005"],
            "dictionary_ids": ["S3S-0001", "S3S-0002", "S3S-0003", "S3Q-0001", "S3Q-0002"],
            "python_reference": "circle_math.dimensions.quaternion.unit_i_phase; circle_math.dimensions.quaternion.conjugation_action; circle_math.dimensions.quaternion.orientation_debug_record",
        },
        {
            "id": "periodic_winding_dynamics",
            "path": "site/widgets/physics/periodic_winding_dynamics.js",
            "theorem_ids": ["CC-T0005", "CC-T0009", "CC-T0011"],
            "dictionary_ids": [
                "COMMON-0060",
                "COMMON-0063",
                "COMMON-0036",
                "COMMON-0038",
                "CC-0301",
            ],
            "python_reference": "circle_math.physics.finite_periodic_dynamics; circle_math.physics.finite_defect_winding",
        },
    ]
    return {"widgets": widgets}


def jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return value


def export_generator_index() -> dict:
    from circle_math.generative import (
        coil_orbit_generator,
        finite_circle_diagram_generator,
        orbit_decomposition_generator,
        physics_loop_diagram_generator,
        proof_glyph_generator,
    )

    records = [
        (
            "finite_circle_diagram",
            "Finite circle diagram",
            finite_circle_diagram_generator(8),
        ),
        (
            "physics_loop_diagram",
            "Finite physics-loop diagram",
            physics_loop_diagram_generator(7, bottom=2, right=3, top=-1, left=5),
        ),
        (
            "coil_orbit",
            "Coil orbit record",
            coil_orbit_generator(12, 8, start=0),
        ),
        (
            "orbit_decomposition",
            "Orbit decomposition record",
            orbit_decomposition_generator(12, 8),
        ),
        (
            "proof_glyph",
            "Proof-glyph record",
            proof_glyph_generator(
                "glyph:c13_stride5_period",
                "CC-T0005",
                "Circle.period_eq_n_div_gcd",
            ),
        ),
    ]
    generators = []
    for record_id, label, record in records:
        generators.append(
            {
                "id": record_id,
                "label": label,
                "artifact_id": record.artifact_id,
                "seed": dict(record.seed),
                "rules": [
                    {
                        "ruleId": rule.rule_id,
                        "parameters": dict(rule.parameters),
                    }
                    for rule in record.rules
                ],
                "iterationSchedule": record.iteration_schedule,
                "closureCondition": record.closure_condition,
                "generatedObject": jsonable(record.generated_object),
                "theoremIds": list(record.theorem_ids),
                "dictionaryIds": list(record.dictionary_ids),
                "note": record.note,
            }
        )
    return {"generators": generators}


def add_dictionary_backlinks(
    dictionary: dict,
    theorem_manifest: dict,
    paper_index: dict,
    widget_index: dict,
    glyph_index: dict,
) -> dict:
    entries = [dict(entry) for entry in dictionary.get("entries", [])]
    by_id = {entry["id"]: entry for entry in entries}
    backlink_fields = [
        "used_by_theorems",
        "used_by_papers",
        "used_by_widgets",
        "used_by_glyphs",
    ]
    for entry in entries:
        for field in backlink_fields:
            entry[field] = []

    def add(entry_id: str, field: str, value: dict) -> None:
        entry = by_id.get(entry_id)
        if entry is not None:
            entry[field].append(value)

    for theorem in theorem_manifest.get("theorems", []):
        for entry_id in theorem.get("dictionary_dependencies", []):
            add(
                entry_id,
                "used_by_theorems",
                {
                    "id": theorem.get("id", ""),
                    "name": theorem.get("name", theorem.get("lean_name", "")),
                    "status": theorem.get("canonical_status", theorem.get("status", "")),
                    "lean_name": theorem.get("lean_name", ""),
                },
            )

    for paper in paper_index.get("papers", []):
        for entry_id in paper.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_papers",
                {
                    "id": paper.get("id", ""),
                    "title": paper.get("title", ""),
                    "status": paper.get("status", ""),
                    "path": paper.get("path", ""),
                },
            )

    for widget in widget_index.get("widgets", []):
        for entry_id in widget.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_widgets",
                {
                    "id": widget.get("id", ""),
                    "path": widget.get("path", ""),
                    "python_reference": widget.get("python_reference", ""),
                },
            )

    for glyph in glyph_index.get("glyphs", []):
        for entry_id in glyph.get("dictionary_ids", []):
            add(
                entry_id,
                "used_by_glyphs",
                {
                    "id": glyph.get("id", ""),
                    "theorem_id": glyph.get("theorem_id", ""),
                    "status": glyph.get("canonical_status", ""),
                    "status_label": glyph.get("status_label", ""),
                },
            )

    for entry in entries:
        for field in backlink_fields:
            entry[field] = sorted(entry[field], key=lambda item: item.get("id", ""))

    return {"entries": sorted(entries, key=lambda item: item["id"])}


def add_theorem_backlinks(theorem_manifest: dict, paper_index: dict) -> dict:
    theorems = [dict(theorem) for theorem in theorem_manifest.get("theorems", [])]
    by_id = {theorem["id"]: theorem for theorem in theorems}
    for theorem in theorems:
        theorem["used_by_papers"] = []

    for paper in paper_index.get("papers", []):
        for theorem_id in paper.get("theorem_ids", []):
            theorem = by_id.get(theorem_id)
            if theorem is None:
                continue
            theorem["used_by_papers"].append(
                {
                    "id": paper.get("id", ""),
                    "title": paper.get("title", ""),
                    "status": paper.get("status", ""),
                    "path": paper.get("path", ""),
                },
            )

    for theorem in theorems:
        theorem["used_by_papers"] = sorted(
            theorem["used_by_papers"],
            key=lambda item: item.get("id", ""),
        )

    return {"theorems": sorted(theorems, key=lambda item: item["id"])}


def export_phase4_targets() -> dict:
    path = ROOT / "manifests" / "phase4_theorem_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_phase5_targets() -> dict:
    path = ROOT / "manifests" / "phase5_edge_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_phase6_targets() -> dict:
    path = ROOT / "manifests" / "phase6_sweep_targets.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_phase7_targets() -> dict:
    path = ROOT / "manifests" / "phase7_physics_generators.yaml"
    if not path.exists():
        return {"targets": []}
    data = load_yaml(path)
    return {"targets": data.get("targets", [])}


def export_capability_showcase() -> dict:
    path = ROOT / "manifests" / "capability_showcase.yaml"
    if not path.exists():
        return {"capabilities": []}
    data = load_yaml(path)
    return {"capabilities": data.get("capabilities", [])}


def glyph_status_label(canonical_status: str) -> str:
    if canonical_status == "proved":
        return "Lean-proved"
    if canonical_status == "exploratory":
        return "Exploratory"
    if canonical_status == "blocked":
        return "Blocked"
    if canonical_status == "deferred":
        return "Deferred"
    if canonical_status == "draft":
        return "Draft"
    return "Planned theorem"


def glyph_manifest_paths() -> list[Path]:
    return sorted((ROOT / "manifests" / "glyphs").glob("*.yaml"))


def export_glyph_index(theorem_manifest: dict, dictionary: dict) -> dict:
    theorem_by_id = {item["id"]: item for item in theorem_manifest.get("theorems", [])}
    dictionary_ids = {item["id"] for item in dictionary.get("entries", [])}
    glyphs: list[dict] = []
    for path in glyph_manifest_paths():
        data = load_yaml(path)
        for glyph in data.get("glyphs", []):
            theorem = theorem_by_id.get(glyph.get("theorem_id", ""))
            if theorem is None:
                raise ValueError(f"{repo_relative(path)}: unknown theorem id {glyph.get('theorem_id')}")
            if glyph.get("lean_name") != theorem.get("lean_name"):
                raise ValueError(f"{repo_relative(path)}: Lean name mismatch for {glyph.get('id')}")
            unknown_dictionary_ids = [
                dictionary_id
                for dictionary_id in glyph.get("dictionary_ids", [])
                if dictionary_id not in dictionary_ids
            ]
            if unknown_dictionary_ids:
                raise ValueError(f"{repo_relative(path)}: unknown dictionary ids {unknown_dictionary_ids}")
            item = dict(glyph)
            item["source_manifest"] = repo_relative(path)
            item["original_status"] = theorem.get("original_status", theorem.get("status", "planned"))
            item["canonical_status"] = theorem.get("canonical_status", "planned")
            item["status_label"] = glyph_status_label(item["canonical_status"])
            item["lean_source"] = theorem.get("lean_source", "")
            item["lean_source_line"] = theorem.get("lean_source_line", "")
            glyphs.append(item)
    return {"glyphs": sorted(glyphs, key=lambda item: item["id"])}


def export_all() -> None:
    theorem_manifest = export_theorems()
    base_dictionary = export_dictionary()
    paper_index = export_papers()
    theorem_manifest = add_theorem_backlinks(theorem_manifest, paper_index)
    widget_index = export_widget_index()
    glyph_index = export_glyph_index(theorem_manifest, base_dictionary)
    dictionary = add_dictionary_backlinks(
        base_dictionary,
        theorem_manifest,
        paper_index,
        widget_index,
        glyph_index,
    )
    write_json(GENERATED / "theorem_manifest.json", theorem_manifest)
    write_json(GENERATED / "dictionary.json", dictionary)
    write_json(GENERATED / "dimensions.json", export_dimensions())
    write_json(GENERATED / "paper_index.json", paper_index)
    write_json(GENERATED / "widget_index.json", widget_index)
    write_json(GENERATED / "phase4_targets.json", export_phase4_targets())
    write_json(GENERATED / "phase5_targets.json", export_phase5_targets())
    write_json(GENERATED / "phase6_targets.json", export_phase6_targets())
    write_json(GENERATED / "phase7_targets.json", export_phase7_targets())
    write_json(GENERATED / "capability_showcase.json", export_capability_showcase())
    write_json(GENERATED / "glyph_index.json", glyph_index)
    write_json(GENERATED / "generator_index.json", export_generator_index())


def main() -> int:
    export_all()
    print("site data exported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
