from __future__ import annotations

import re
import shlex
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from site_lib import GENERATED, ROOT, load_yaml, repo_relative, write_json

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DECL_RE = re.compile(r"^\s*(?:theorem|lemma|def|abbrev|structure|inductive)\s+([A-Za-z0-9_'.]+)")

CLAIM_LANGUAGE_PATTERNS = [
    ("open_problem_solution", re.compile(r"\bsolv(?:e|es|ed|ing)\b", re.IGNORECASE)),
    ("new_proof", re.compile(r"\bnew proof\b", re.IGNORECASE)),
    ("open_problem_progress", re.compile(r"\bprogress on (?:an? )?open\b", re.IGNORECASE)),
    ("improved_bounds", re.compile(r"\bimprov(?:e|es|ed|ing|ement)\s+bounds?\b", re.IGNORECASE)),
    ("universal_compression", re.compile(r"\buniversal compression\b", re.IGNORECASE)),
    ("model_quality_improvement", re.compile(r"\bmodel-quality improvement\b", re.IGNORECASE)),
    ("context_length_improvement", re.compile(r"\bcontext-length improvement\b", re.IGNORECASE)),
    ("speedup_claim", re.compile(r"\bspeedup\b|\bfaster\b", re.IGNORECASE)),
    ("physics_discovery", re.compile(r"\bphysics discovery\b", re.IGNORECASE)),
    ("continuum_physics", re.compile(r"\bcontinuum (?:gauge|physics)\b", re.IGNORECASE)),
    ("lattice_qcd_correctness", re.compile(r"\blattice-QCD correctness\b", re.IGNORECASE)),
    ("full_smooth_hopf", re.compile(r"\bfull smooth Hopf\b", re.IGNORECASE)),
    ("complete_so3", re.compile(r"\bcomplete SO\(3\)\b", re.IGNORECASE)),
]

CLAIM_BOUNDARY_MARKERS = [
    "no ",
    "not ",
    "does not",
    "without",
    "examples only",
    "future",
    "boundary",
]

CAPABILITY_CLAIM_LANGUAGE_FIELDS = [
    "audience_interest",
    "standard_math_anchor",
    "circle_math_expression",
    "circle_native_value",
    "advertised_claim",
    "proof_scope",
    "proof_provenance",
]

ROUTE_CLAIM_LANGUAGE_FIELDS = [
    "title",
    "audience",
    "route_claim",
]

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
                "GEN-T0028",
                "GEN-T0029",
                "GEN-T0030",
                "GEN-T0031",
                "GEN-T0032",
                "GEN-T0033",
                "GEN-T0034",
                "GEN-T0035",
                "GEN-T0036",
                "GEN-T0037",
                "GEN-T0038",
                "GEN-T0039",
                "GEN-T0044",
                "GEN-T0045",
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
                "AIM-T0031",
                "AIM-T0032",
                "AIM-T0033",
                "AIM-T0034",
                "AIM-T0084",
                "AIM-T0085",
                "AIM-T0090",
            ],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0054",
                "COMMON-0059",
                "COMMON-0067",
            ],
            "python_reference": "circle_math.applications.circle_ai.loop_required_steps; circle_math.applications.circle_ai.loop_score_active; circle_math.applications.circle_ai.loop_score_trace; circle_math.applications.circle_ai.loop_exit_step; circle_math.applications.circle_ai.loop_exit_certificate",
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
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022", "AIM-T0026", "AIM-T0027", "AIM-T0057", "AIM-T0106", "AIM-T0107"],
            "dictionary_ids": [
                "COMMON-0052",
                "COMMON-0053",
                "COMMON-0059",
                "COMMON-0068",
                "COMMON-0069",
            ],
            "python_reference": "circle_math.applications.circle_ai.token_recurrence_budgets; circle_math.applications.circle_ai.active_token_counts_by_budget; circle_math.applications.circle_ai.active_tokens_at_step; circle_math.applications.circle_ai.recurrence_resolution_levels; circle_math.applications.circle_ai.run_token_level_recurrence_benchmark",
        },
        {
            "id": "learned_token_recurrence",
            "path": "site/widgets/ai/learned_token_recurrence.js",
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0022", "AIM-T0057"],
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
            "theorem_ids": ["AIM-T0006", "AIM-T0007", "AIM-T0008", "AIM-T0009", "AIM-T0018", "AIM-T0039", "AIM-T0040", "AIM-T0041", "AIM-T0042", "AIM-T0043", "AIM-T0044", "AIM-T0045", "AIM-T0046", "AIM-T0047", "AIM-T0048", "AIM-T0056", "AIM-T0057", "AIM-T0058"],
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
            "id": "kv_cache_ring_buffer",
            "path": "site/widgets/ai/kv_cache_ring_buffer.js",
            "theorem_ids": [
                "AIM-T0059",
                "AIM-T0060",
                "AIM-T0061",
                "AIM-T0062",
                "AIM-T0063",
                "AIM-T0064",
                "AIM-T0065",
                "AIM-T0066",
                "AIM-T0067",
                "AIM-T0068",
                "AIM-T0069",
                "AIM-T0070",
                "AIM-T0071",
                "AIM-T0072",
                "AIM-T0073",
                "AIM-T0074",
                "AIM-T0075",
                "AIM-T0076",
                "AIM-T0077",
                "AIM-T0078",
                "AIM-T0079",
                "AIM-T0080",
                "AIM-T0081",
                "AIM-T0082",
                "AIM-T0083",
                "AIM-T0086",
                "AIM-T0087",
                "AIM-T0088",
                "AIM-T0089",
                "AIM-T0091",
                "AIM-T0092",
                "AIM-T0093",
                "AIM-T0094",
                "AIM-T0095",
                "AIM-T0096",
            ],
            "dictionary_ids": ["COMMON-0028", "COMMON-0081"],
            "python_reference": "circle_math.applications.circle_ai.kv_cache_slot; circle_math.applications.circle_ai.kv_cache_window_contains; circle_math.applications.circle_ai.kv_cache_next_overwrite_token; circle_math.applications.circle_ai.kv_cache_next_overwrite_after_current; circle_math.applications.circle_ai.kv_cache_stale_by_next_overwrite_boundary; circle_math.applications.circle_ai.kv_cache_same_slot_overwrite_witness_when_stale; circle_math.applications.circle_ai.kv_cache_stale_iff_same_slot_overwrite_trace; circle_math.applications.circle_ai.kv_cache_retained_iff_no_same_slot_overwrite_trace; circle_math.applications.circle_ai.kv_cache_trace_fresh_iff_next_overwrite_boundary; circle_math.applications.circle_ai.kv_cache_batch_retained_iff_no_same_slot_overwrite_trace; circle_math.applications.circle_ai.kv_cache_batch_trace_fresh_iff_next_overwrite_boundary; circle_math.applications.circle_ai.kv_cache_trace_fresh_batch_slots_distinct; circle_math.applications.circle_ai.kv_cache_retained_batch_slots_distinct; circle_math.applications.circle_ai.kv_cache_ordered_live_window_subrequest; circle_math.applications.circle_ai.kv_cache_live_window_slot_range_covered; circle_math.applications.circle_ai.certify_kv_cache_adapter_request_trace; circle_math.applications.circle_ai.certify_kv_cache_live_window",
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
            "id": "stride_family_attention",
            "path": "site/widgets/ai/stride_family_attention.js",
            "theorem_ids": [
                "AIT-T0015",
                "AIT-T0016",
                "AIT-T0017",
                "AIT-T0018",
                "AIT-T0019",
                "AIT-T0020",
                "AIT-T0021",
                "AIT-T0028",
                "AIT-T0033",
                "AIT-T0034",
                "AIT-T0035",
                "AIT-T0036",
                "AIT-T0037",
                "AIT-T0038",
                "AIT-T0039",
                "AIT-T0040",
                "AIT-T0041",
                "AIT-T0042",
                "AIT-T0043",
                "AIT-T0044",
                "AIT-T0045",
                "AIT-T0046",
                "AIT-T0047",
                "AIT-T0048",
                "AIT-T0049",
                "AIT-T0050",
                "AIT-T0051",
                "AIT-T0052",
                "AIT-T0053",
                "AIT-T0054",
                "AIT-T0055",
                "AIT-T0056",
                "AIT-T0057",
                "AIT-T0058",
                "AIT-T0059",
                "AIT-T0060",
                "AIT-T0061",
                "AIT-T0062",
                "AIT-T0063",
                "AIT-T0064",
                "AIT-T0065",
                "AIT-T0066",
                "AIT-T0067",
                "AIT-T0068",
                "AIT-T0069",
                "AIT-T0070",
                "AIT-T0071",
                "AIT-T0072",
                "AIT-T0073",
                "AIT-T0074",
                "AIT-T0075",
                "AIT-T0076",
                "AIT-T0077",
                "AIT-T0078",
                "AIT-T0079",
                "AIT-T0080",
                "AIT-T0081",
                "AIT-T0082",
                "AIT-T0083",
                "AIT-T0084",
                "AIT-T0085",
                "AIT-T0086",
                "AIT-T0087",
                "AIT-T0088",
                "AIT-T0089",
                "AIT-T0090",
                "AIT-T0091",
                "AIT-T0092",
                "AIT-T0093",
                "AIT-T0094",
                "AIT-T0095",
                "AIT-T0096",
                "AIT-T0097",
                "AIT-T0098",
                "AIT-T0099",
                "AIT-T0100",
                "AIT-T0101",
                "AIT-T0102",
                "AIT-T0103",
                "AIT-T0104",
                "AIT-T0105",
                "AIT-T0106",
                "AIT-T0107",
                "AIT-T0108",
                "AIT-T0109",
                "AIT-T0110",
                "AIT-T0111",
                "AIT-T0112",
                "AIT-T0113",
                "AIT-T0114",
                "AIT-T0115",
                "AIT-T0116",
            ],
            "dictionary_ids": ["COMMON-0075", "COMMON-0079", "COMMON-0047", "COMMON-0029"],
            "python_reference": "circle_math.applications.circle_ai.stride_family_attention_candidates; circle_math.applications.circle_ai.stride_family_lag_candidate_list; circle_math.applications.circle_ai.stride_family_query_candidate_list; circle_math.applications.circle_ai.consecutive_integer_intervals; circle_math.applications.circle_ai.stride_family_predecessor_injective_window_context_sufficient_condition; circle_math.applications.circle_ai.structured_stride_family_target_lags; circle_math.applications.circle_ai.nonstructured_stride_family_control_lags; circle_math.applications.circle_ai.run_stride_family_sparse_attention_benchmark",
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
            "theorem_ids": ["AIRA-T0016", "AIRA-T0017", "AIRA-T0018", "AIRA-T0019", "AIRA-T0020"],
            "dictionary_ids": ["COMMON-0074", "COMMON-0046", "COMMON-0026"],
            "python_reference": "circle_math.applications.circle_ai.multicoil_phase; circle_math.applications.circle_ai.multicoil_phase2; circle_math.applications.circle_ai.multicoil_product_cycle; circle_math.applications.circle_ai.run_multicoil_closure_benchmark",
        },
        {
            "id": "rope_relative_phase",
            "path": "site/widgets/ai/rope_relative_phase.js",
            "theorem_ids": ["AIA-T0001", "AIA-T0002", "AIA-T0004", "AIA-T0005"],
            "dictionary_ids": ["COMMON-0051", "COMMON-0050", "COMMON-0026"],
            "python_reference": "circle_math.applications.circle_ai.rope_relative_feature; circle_math.applications.circle_ai.run_rope_relative_phase_benchmark",
        },
        {
            "id": "rope_certifier",
            "path": "site/widgets/ai/rope_certifier.js",
            "theorem_ids": [
                "AIRA-T0021",
                "AIRA-T0022",
                "AIRA-T0023",
                "AIRA-T0024",
                "AIRA-T0025",
                "AIRA-T0026",
                "AIRA-T0027",
                "AIRA-T0028",
                "AIRA-T0034",
                "AIRA-T0035",
                "AIRA-T0036",
                "AIRA-T0046",
                "AIRA-T0048",
                "AIRA-T0049",
                "AIRA-T0051",
                "AIRA-T0052",
                "AIRA-T0190",
                "AIRA-T0191",
                "AIRA-T0188",
                "AIRA-T0192",
                "AIRA-T0193",
                "AIRA-T0194",
                "AIRA-T0189",
                "AIRA-T0195",
                "AIRA-T0203",
                "AIRA-T0204",
                "AIRA-T0205",
                "AIRA-T0206",
                "AIRA-T0207",
                "AIRA-T0210",
                "AIRA-T0211",
                "AIRA-T0212",
                "AIRA-T0213",
                "AIRA-T0029",
                "AIRA-T0030",
                "AIRA-T0031",
                "AIRA-T0032",
                "AIRA-T0033",
                "AIRA-T0037",
                "AIRA-T0038",
                "AIRA-T0039",
                "AIRA-T0040",
                "AIRA-T0041",
                "AIRA-T0042",
                "AIRA-T0043",
                "AIRA-T0044",
                "AIRA-T0045",
                "AIRA-T0047",
                "AIRA-T0050",
                "AIRA-T0053",
                "AIRA-T0054",
                "AIRA-T0055",
                "AIRA-T0056",
                "AIRA-T0057",
                "AIRA-T0058",
                "AIRA-T0059",
                "AIRA-T0182",
                "AIRA-T0183",
                "AIRA-T0214",
                "AIRA-T0060",
                "AIRA-T0177",
                "AIRA-T0186",
                "AIRA-T0178",
                "AIRA-T0181",
                "AIRA-T0196",
                "AIRA-T0197",
                "AIRA-T0209",
                "AIRA-T0061",
                "AIRA-T0185",
                "AIRA-T0215",
                "AIRA-T0187",
                "AIRA-T0062",
            ],
            "dictionary_ids": ["COMMON-0076", "COMMON-0077", "COMMON-0087", "COMMON-0088"],
            "python_reference": "circle_math.applications.rope_certifier.certify_rope_positions; scripts/rope_certify.py",
        },
        {
            "id": "winding_aware_position",
            "path": "site/widgets/ai/winding_aware_position.js",
            "theorem_ids": ["AIRA-T0006", "AIRA-T0007", "AIRA-T0008", "AIRA-T0009", "AIRA-T0010"],
            "dictionary_ids": ["COMMON-0072", "COMMON-0026", "COMMON-0046"],
            "python_reference": "circle_math.applications.circle_ai.winding_position; circle_math.applications.circle_ai.winding_position_feature; circle_math.applications.circle_ai.run_winding_aware_position_benchmark",
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
            "id": "block_cyclic_mixer_validation",
            "path": "site/widgets/ai/block_cyclic_mixer_validation.js",
            "theorem_ids": ["AIRA-T0011", "AIRA-T0012", "AIRA-T0013", "AIRA-T0014", "AIRA-T0015"],
            "dictionary_ids": ["COMMON-0073", "COMMON-0058", "COMMON-0056"],
            "python_reference": "circle_math.applications.circle_ai.block_cyclic_cell; circle_math.applications.circle_ai.block_cyclic_mixer_output; circle_math.applications.circle_ai.dense_block_cyclic_matrix; circle_math.applications.circle_ai.run_block_cyclic_mixer_benchmark",
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
            "theorem_ids": [
                "PHYS-T0004",
                "PHYS-T0005",
                "PHYS-T0046",
                "PHYS-T0047",
                "PHYS-T0049",
                "PHYS-T0052",
                "PHYS-T0053",
                "PHYS-T0054",
                "PHYS-T0055",
                "PHYS-T0056",
                "PHYS-T0057",
                "PHYS-T0058",
                "PHYS-T0059",
                "PHYS-T0060",
                "PHYS-T0061",
                "PHYS-T0062",
                "PHYS-T0063",
                "PHYS-T0064",
            ],
            "dictionary_ids": [
                "COMMON-0060",
                "COMMON-0061",
                "COMMON-0062",
                "COMMON-0063",
            ],
            "python_reference": "circle_math.physics.GaugePath; circle_math.physics.GaugeEdge; circle_math.physics.gauge_transform_path; circle_math.physics.path_holonomy; circle_math.physics.wilson_loop_certificate; circle_math.physics.three_path_cycle_closed_loop_record",
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
        {
            "id": "capability_portfolio_matrix",
            "path": "site/widgets/showcase/capability_portfolio_matrix.js",
            "theorem_ids": [],
            "dictionary_ids": [],
            "python_reference": "manifests/capability_showcase.yaml; scripts/check_capability_showcase.py; scripts/site/export_site_data.py",
        },
        {
            "id": "capability_audit_checklist",
            "path": "site/widgets/showcase/capability_audit_checklist.js",
            "theorem_ids": [],
            "dictionary_ids": [],
            "python_reference": "manifests/capability_showcase.yaml; site/data/generated/capability_showcase.json; scripts/check_capability_showcase.py; scripts/site/check_capability_contracts.py",
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


CLAIM_CONTRACT_ROLES = {"standard_math_parity", "circle_native_value"}
CLAIM_CONTRACT_PROVENANCE_KINDS = {"mathlib_bridge", "project_native", "mixed"}
SECTION_RE = re.compile(r"^##\s+", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+(.+)$")
SHOWCASE_REF_RE = re.compile(r'data-showcase-ref="([^"]+)"')
THEOREM_ATTR_RE = re.compile(r'data-theorem-id="([^"]+)"')
WIDGET_PANEL_RE = re.compile(r'data-widget="([^"]+)"')


def nonempty_text(item: dict, key: str) -> bool:
    return bool(str(item.get(key, "")).strip())


def contract_gate(gate_id: str, label: str, passed: bool, evidence: str) -> dict:
    return {
        "id": gate_id,
        "label": label,
        "passed": bool(passed),
        "evidence": evidence,
    }


def contract_count_or_failures(count: int, failures: list[str]) -> str:
    if not failures:
        return str(count)
    return f"{count}; failures: {', '.join(failures)}"


def unsafe_or_missing_path(ref: str) -> bool:
    path = Path(ref)
    return path.is_absolute() or ".." in path.parts or not (ROOT / path).exists()


def showcase_refs_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(SHOWCASE_REF_RE.findall(path.read_text()))


def theorem_ids_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(THEOREM_ATTR_RE.findall(path.read_text()))


def widgets_on_page(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(WIDGET_PANEL_RE.findall(path.read_text()))


def widget_ids_from_files() -> set[str]:
    return {
        path.stem
        for path in sorted((ROOT / "site" / "widgets").glob("**/*.js"))
    }


def path_for_paper_id(paper_id: str) -> Path | None:
    for path in sorted((ROOT / "papers").glob("**/*.md")):
        if path.stem == paper_id:
            return path
    return None


def source_trail_section(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text()
    marker = "## Source Trail"
    start = text.find(marker)
    if start == -1:
        return ""
    next_section = SECTION_RE.search(text, start + len(marker))
    if next_section is None:
        return text[start:]
    return text[start : next_section.start()]


def module_name_for_path(path: Path) -> str:
    return ".".join(path.with_suffix("").parts)


def module_name_for_ref(ref: str) -> str:
    return module_name_for_path(Path(ref))


def lean_modules_by_name() -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for path in sorted(ROOT.glob("**/*.lean")):
        if ".lake" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        modules[module_name_for_path(relative)] = path
    return modules


def imported_modules(path: Path) -> set[str]:
    imports: set[str] = set()
    if not path.exists():
        return imports
    for line in path.read_text().splitlines():
        match = IMPORT_RE.match(line)
        if not match:
            continue
        imports.update(part for part in match.group(1).split() if part)
    return imports


def paper_lean_sidecars(paper: dict) -> list[Path]:
    sidecar = paper.get("sidecar")
    if not sidecar:
        return []
    lean_dir = ROOT / sidecar / "lean"
    if not lean_dir.exists():
        return []
    return sorted(lean_dir.glob("*.lean"))


def transitive_local_imports(start_paths: list[Path], modules: dict[str, Path]) -> set[str]:
    seen: set[str] = set()
    stack: list[str] = []
    for path in start_paths:
        stack.extend(imported_modules(path))
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        local_path = modules.get(module)
        if local_path is not None:
            stack.extend(imported_modules(local_path) - seen)
    return seen


def paper_manifest_by_id() -> dict[str, dict]:
    path = ROOT / "manifests" / "paper_manifest.yaml"
    if not path.exists():
        return {}
    data = load_yaml(path)
    return {paper["id"]: paper for paper in data.get("papers", []) if paper.get("id")}


def theorem_manifest_by_id() -> dict[str, dict]:
    theorems: dict[str, dict] = {}
    for path in theorem_manifest_paths():
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id:
                theorems[theorem_id] = theorem
    return theorems


def theorem_ref_status(
    theorem_id: str,
    paper_ids: list[str],
    papers: dict[str, dict],
    theorems: dict[str, dict],
) -> dict:
    theorem = theorems.get(theorem_id, {})
    status = theorem.get("status", "missing")
    carried_by = sorted(
        paper_id
        for paper_id in paper_ids
        if theorem_id in (papers.get(paper_id, {}).get("theorem_ids", []) or [])
    )
    proved = canonical_status(status) == "proved"
    paper_backed = bool(carried_by)
    return {
        "id": theorem_id,
        "status": status,
        "canonical_status": canonical_status(status),
        "proved": proved,
        "lean_name": theorem.get("lean_name", ""),
        "paper_backed": paper_backed,
        "carried_by_papers": carried_by,
    }


def capability_theorem_ref_contract(
    item: dict,
    papers: dict[str, dict],
    theorems: dict[str, dict],
) -> dict:
    paper_ids = item.get("paper_ids", []) or []
    theorem_ids = item.get("theorem_ids", []) or []
    refs = [
        theorem_ref_status(theorem_id, paper_ids, papers, theorems)
        for theorem_id in theorem_ids
    ]
    proved_and_paper_backed_count = sum(
        1 for ref in refs if ref["proved"] and ref["paper_backed"]
    )
    return {
        "proved_and_paper_backed_count": proved_and_paper_backed_count,
        "total_count": len(refs),
        "unproved_or_unbacked_ids": [
            ref["id"] for ref in refs if not (ref["proved"] and ref["paper_backed"])
        ],
        "refs": refs,
    }


def source_ref_backing_status(
    ref: str,
    paper_ids: list[str],
    papers: dict[str, dict],
    local_lean_modules: dict[str, Path],
) -> dict:
    source_sections: list[str] = []
    sidecar_paths: list[Path] = []
    for paper_id in paper_ids:
        paper = papers.get(paper_id)
        if paper is None:
            continue
        paper_path = path_for_paper_id(paper_id)
        if paper_path is not None:
            source_sections.append(source_trail_section(paper_path))
        sidecar_paths.extend(paper_lean_sidecars(paper))

    if any(ref in section for section in source_sections):
        return {"ref": ref, "backed": True, "backing": "source_trail"}

    local_ref = Path(ref)
    if local_ref.parts[:1] == ("Circle",) and local_ref.suffix == ".lean":
        module_name = module_name_for_ref(ref)
        imported = transitive_local_imports(sidecar_paths, local_lean_modules)
        if module_name in imported:
            return {"ref": ref, "backed": True, "backing": "lean_sidecar_import"}

    return {"ref": ref, "backed": False, "backing": "missing"}


def capability_source_ref_contract(
    item: dict,
    papers: dict[str, dict],
    local_lean_modules: dict[str, Path],
) -> dict:
    paper_ids = item.get("paper_ids", []) or []
    source_refs = item.get("source_refs", []) or []
    refs = [
        source_ref_backing_status(ref, paper_ids, papers, local_lean_modules)
        for ref in source_refs
    ]
    backed_count = sum(1 for ref in refs if ref["backed"])
    return {
        "backed_count": backed_count,
        "total_count": len(refs),
        "unbacked_refs": [ref["ref"] for ref in refs if not ref["backed"]],
        "refs": refs,
    }


def capability_living_book_ref_contract(
    item: dict,
    known_widget_ids: set[str],
) -> dict:
    capability_id = item.get("id", "")
    theorem_ids = set(item.get("theorem_ids", []) or [])
    pages: list[dict] = []
    for ref in item.get("living_book_refs", []) or []:
        page_ref = ref.get("page", "")
        page_path = ROOT / page_ref
        page_exists = bool(page_ref) and not unsafe_or_missing_path(page_ref)
        showcase_backed = capability_id in showcase_refs_on_page(page_path)
        page_theorem_ids = theorem_ids_on_page(page_path)
        widget_ids = ref.get("widget_ids", []) or []
        widgets = []
        for widget_id in widget_ids:
            known = widget_id in known_widget_ids
            mounted = widget_id in widgets_on_page(page_path)
            widgets.append(
                {
                    "id": widget_id,
                    "known": known,
                    "mounted": mounted,
                    "backed": known and mounted,
                }
            )
        theorem_backed = bool(theorem_ids & page_theorem_ids)
        widget_backed = all(widget["backed"] for widget in widgets)
        presentation_backed = bool(widgets) and widget_backed or (
            not widgets and theorem_backed
        )
        page_backed = page_exists and showcase_backed and presentation_backed
        pages.append(
            {
                "page": page_ref,
                "exists": page_exists,
                "carries_showcase_ref": showcase_backed,
                "carries_advertised_theorem": theorem_backed,
                "backed": page_backed,
                "widgets": widgets,
            }
        )
    total_widget_ids = {
        widget["id"] for page in pages for widget in page["widgets"]
    }
    backed_widget_ids = {
        widget["id"]
        for page in pages
        for widget in page["widgets"]
        if widget["backed"]
    }
    return {
        "backed_page_count": sum(1 for page in pages if page["backed"]),
        "total_page_count": len(pages),
        "backed_widget_count": len(backed_widget_ids),
        "total_widget_count": len(total_widget_ids),
        "unbacked_pages": [page["page"] for page in pages if not page["backed"]],
        "unbacked_widgets": [
            f"{page['page']}#{widget['id']}"
            for page in pages
            for widget in page["widgets"]
            if not widget["backed"]
        ],
        "pages": pages,
    }


def proved_theorem_id_set() -> set[str]:
    proved: set[str] = set()
    for path in theorem_manifest_paths():
        data = load_yaml(path)
        for theorem in data.get("theorems", []):
            theorem_id = theorem.get("id")
            if theorem_id and canonical_status(theorem.get("status", "")) == "proved":
                proved.add(theorem_id)
    return proved


def paper_id_set() -> set[str]:
    path = ROOT / "manifests" / "paper_manifest.yaml"
    if not path.exists():
        return set()
    data = load_yaml(path)
    return {paper["id"] for paper in data.get("papers", []) if paper.get("id")}


def capability_verification_recipe(item: dict) -> dict:
    executable_refs = item.get("executable_refs", []) or []
    return {
        "lean_command": "lake build",
        "pytest_command": shlex.join(["python", "-m", "pytest", *executable_refs]),
        "capability_contract_command": shlex.join(
            ["python", "scripts/check_capability_showcase.py"]
        )
        + " && "
        + shlex.join(["python", "scripts/site/check_capability_contracts.py"]),
        "site_command": "make sitecheck",
    }


def claim_language_contract(item: dict, checked_fields: list[str]) -> dict:
    flagged_phrases = []
    for field in checked_fields:
        value = str(item.get(field, "") or "")
        for pattern_id, pattern in CLAIM_LANGUAGE_PATTERNS:
            for match in pattern.finditer(value):
                flagged_phrases.append(
                    {
                        "field": field,
                        "pattern": pattern_id,
                        "phrase": match.group(0),
                    }
                )
    boundary_text = str(item.get("not_claimed", "") or "")
    boundary_lower = boundary_text.lower()
    explicit_boundary = any(marker in boundary_lower for marker in CLAIM_BOUNDARY_MARKERS)
    return {
        "ready_to_advertise": not flagged_phrases and explicit_boundary,
        "checked_fields": checked_fields,
        "flagged_phrases": flagged_phrases,
        "boundary_field": "not_claimed",
        "explicit_boundary": explicit_boundary,
    }


def value_proposition_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
) -> dict:
    roles = set(item.get("portfolio_roles", []) or [])
    executable_ready = bool(item.get("executable_refs", []) or [])
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    checks = {
        "standard_math_parity": {
            "required": "standard_math_parity" in roles,
            "ready": (
                "standard_math_parity" not in roles
                or (
                    nonempty_text(item, "standard_math_anchor")
                    and nonempty_text(item, "circle_math_expression")
                    and theorem_ready
                )
            ),
            "evidence": (
                f"theorems "
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)}"
            ),
        },
        "circle_native_value": {
            "required": "circle_native_value" in roles,
            "ready": (
                "circle_native_value" not in roles
                or (
                    nonempty_text(item, "circle_native_value")
                    and nonempty_text(item, "circle_math_expression")
                    and source_ready
                    and living_ready
                    and executable_ready
                )
            ),
            "evidence": (
                f"sources {source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)}; "
                f"Living Book pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}"
            ),
        },
        "application_guardrail": {
            "required": "application_guardrail" in roles,
            "ready": (
                "application_guardrail" not in roles
                or (
                    nonempty_text(item, "not_claimed")
                    and claim_language_contract.get("ready_to_advertise", False)
                    and source_ready
                    and executable_ready
                )
            ),
            "evidence": (
                "language "
                + (
                    "clean"
                    if claim_language_contract.get("ready_to_advertise", False)
                    else "incomplete"
                )
            ),
        },
    }
    return {
        "ready_to_advertise": all(
            check["ready"] for check in checks.values() if check["required"]
        ),
        "role_checks": checks,
    }


def proof_trail_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
) -> dict:
    executable_refs = item.get("executable_refs", []) or []
    source_refs = set(item.get("source_refs", []) or [])
    executable_ready = (
        bool(executable_refs)
        and all(ref in source_refs for ref in executable_refs)
        and all(Path(ref).name.startswith("test_") and Path(ref).suffix == ".py" for ref in executable_refs)
    )
    steps = [
        {
            "id": "paper_backing",
            "label": "cited paper backing",
            "ready": bool(item.get("paper_ids", []) or []),
            "evidence": f"{len(item.get('paper_ids', []) or [])} paper ids",
        },
        {
            "id": "theorem_refs",
            "label": "proved paper-carried theorem refs",
            "ready": (
                theorem_ref_contract.get("total_count", 0) > 0
                and theorem_ref_contract.get("proved_and_paper_backed_count")
                == theorem_ref_contract.get("total_count")
                and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
            ),
            "evidence": (
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)} theorem refs"
            ),
        },
        {
            "id": "source_refs",
            "label": "paper-backed source refs",
            "ready": (
                source_ref_contract.get("total_count", 0) > 0
                and source_ref_contract.get("backed_count")
                == source_ref_contract.get("total_count")
                and not source_ref_contract.get("unbacked_refs", [])
            ),
            "evidence": (
                f"{source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)} source refs"
            ),
        },
        {
            "id": "executable_refs",
            "label": "pytest executable refs",
            "ready": executable_ready,
            "evidence": f"{len(executable_refs)} executable refs",
        },
        {
            "id": "living_book_refs",
            "label": "backed Living Book presentation",
            "ready": (
                living_book_ref_contract.get("total_page_count", 0) > 0
                and living_book_ref_contract.get("backed_page_count")
                == living_book_ref_contract.get("total_page_count")
                and living_book_ref_contract.get("backed_widget_count")
                == living_book_ref_contract.get("total_widget_count")
                and not living_book_ref_contract.get("unbacked_pages", [])
                and not living_book_ref_contract.get("unbacked_widgets", [])
            ),
            "evidence": (
                f"pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}; "
                f"widgets {living_book_ref_contract.get('backed_widget_count', 0)}/"
                f"{living_book_ref_contract.get('total_widget_count', 0)}"
            ),
        },
        {
            "id": "role_value",
            "label": "role-backed value proposition",
            "ready": value_proposition_contract.get("ready_to_advertise", False),
            "evidence": "role checks ready" if value_proposition_contract.get("ready_to_advertise", False) else "role checks incomplete",
        },
        {
            "id": "claim_language",
            "label": "advertising-language boundary",
            "ready": claim_language_contract.get("ready_to_advertise", False),
            "evidence": "clean" if claim_language_contract.get("ready_to_advertise", False) else "incomplete",
        },
    ]
    return {
        "ready_to_advertise": all(step["ready"] for step in steps),
        "passed_step_count": sum(1 for step in steps if step["ready"]),
        "total_step_count": len(steps),
        "steps": steps,
    }


def review_packet_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
    proof_trail_contract: dict,
) -> dict:
    executable_refs = item.get("executable_refs", []) or []
    verification_recipe = capability_verification_recipe(item)
    expected_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    claim_ready = (
        nonempty_text(item, "advertised_claim")
        and nonempty_text(item, "proof_scope")
        and nonempty_text(item, "not_claimed")
        and claim_language_contract.get("ready_to_advertise", False)
    )
    command_ready = (
        bool(executable_refs)
        and verification_recipe.get("pytest_command") == expected_pytest_command
        and verification_recipe.get("lean_command") == "lake build"
        and verification_recipe.get("site_command") == "make sitecheck"
    )
    local_gate_ready = (
        proof_trail_contract.get("ready_to_advertise", False)
        and value_proposition_contract.get("ready_to_advertise", False)
        and claim_language_contract.get("ready_to_advertise", False)
    )
    sections = [
        {
            "id": "claim_scope_boundary",
            "label": "claim, proof scope, and boundary",
            "ready": claim_ready,
            "evidence": (
                "claim/scope/boundary present"
                if claim_ready
                else "missing claim, proof scope, clean language, or boundary"
            ),
            "refs": [],
        },
        {
            "id": "paper_trail",
            "label": "paper trail",
            "ready": bool(item.get("paper_ids", []) or []),
            "evidence": f"{len(item.get('paper_ids', []) or [])} paper ids",
            "refs": item.get("paper_ids", []) or [],
        },
        {
            "id": "theorem_trail",
            "label": "proved theorem trail",
            "ready": theorem_ready,
            "evidence": (
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)} theorem refs"
            ),
            "refs": item.get("theorem_ids", []) or [],
        },
        {
            "id": "source_trail",
            "label": "paper-backed source trail",
            "ready": source_ready,
            "evidence": (
                f"{source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)} source refs"
            ),
            "refs": item.get("source_refs", []) or [],
        },
        {
            "id": "example_command",
            "label": "executable example command",
            "ready": command_ready,
            "evidence": verification_recipe.get("pytest_command", ""),
            "refs": executable_refs,
            "command": verification_recipe.get("pytest_command", ""),
        },
        {
            "id": "living_book_route",
            "label": "Living Book route",
            "ready": living_ready,
            "evidence": (
                f"pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}; "
                f"widgets {living_book_ref_contract.get('backed_widget_count', 0)}/"
                f"{living_book_ref_contract.get('total_widget_count', 0)}"
            ),
            "refs": item.get("living_book_refs", []) or [],
        },
        {
            "id": "local_verification_gates",
            "label": "local verification gates",
            "ready": local_gate_ready,
            "evidence": (
                f"proof trail {proof_trail_contract.get('passed_step_count', 0)}/"
                f"{proof_trail_contract.get('total_step_count', 0)}; "
                "role/value/language gates ready"
            ),
            "refs": [],
            "commands": [
                verification_recipe.get("lean_command", ""),
                verification_recipe.get("capability_contract_command", ""),
                verification_recipe.get("site_command", ""),
            ],
        },
    ]
    ready = all(section["ready"] for section in sections)
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "sections": sections,
    }


def parity_value_comparison_contract(
    item: dict,
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
    proof_trail_contract: dict,
    review_packet_contract: dict,
) -> dict:
    roles = set(item.get("portfolio_roles", []) or [])
    evidence_counts = item.get("evidence_counts", {}) or {}
    executable_refs = item.get("executable_refs", []) or []
    standard_parity_claimed = "standard_math_parity" in roles
    circle_native_claimed = "circle_native_value" in roles
    theorem_ready = (
        theorem_ref_contract.get("total_count", 0) > 0
        and theorem_ref_contract.get("proved_and_paper_backed_count")
        == theorem_ref_contract.get("total_count")
        and not theorem_ref_contract.get("unproved_or_unbacked_ids", [])
    )
    source_ready = (
        source_ref_contract.get("total_count", 0) > 0
        and source_ref_contract.get("backed_count") == source_ref_contract.get("total_count")
        and not source_ref_contract.get("unbacked_refs", [])
    )
    living_ready = (
        living_book_ref_contract.get("total_page_count", 0) > 0
        and living_book_ref_contract.get("backed_page_count")
        == living_book_ref_contract.get("total_page_count")
        and living_book_ref_contract.get("backed_widget_count")
        == living_book_ref_contract.get("total_widget_count")
        and not living_book_ref_contract.get("unbacked_pages", [])
        and not living_book_ref_contract.get("unbacked_widgets", [])
    )
    executable_ready = bool(executable_refs)
    standard_ready = (
        nonempty_text(item, "audience_interest")
        and nonempty_text(item, "standard_math_anchor")
        and theorem_ready
    )
    circle_form_ready = (
        nonempty_text(item, "circle_math_expression")
        and nonempty_text(item, "advertised_claim")
    )
    circle_value_ready = (
        circle_native_claimed
        and nonempty_text(item, "circle_native_value")
        and value_proposition_contract.get("ready_to_advertise", False)
    )
    proof_backing_ready = (
        evidence_counts.get("paper_count", 0) > 0
        and theorem_ready
        and source_ready
        and living_ready
        and executable_ready
        and proof_trail_contract.get("ready_to_advertise", False)
    )
    review_ready = review_packet_contract.get("ready_to_review", False)
    boundary_ready = (
        nonempty_text(item, "not_claimed")
        and claim_language_contract.get("ready_to_advertise", False)
    )
    sections = [
        {
            "id": "standard_reference",
            "label": "standard-math reference point",
            "ready": standard_ready,
            "evidence": item.get("standard_math_anchor", ""),
            "refs": item.get("theorem_ids", []) or [],
            "standard_parity_claimed": standard_parity_claimed,
        },
        {
            "id": "circle_expression",
            "label": "Circle expression of the same surface",
            "ready": circle_form_ready,
            "evidence": item.get("circle_math_expression", ""),
            "refs": item.get("source_refs", []) or [],
        },
        {
            "id": "circle_native_value",
            "label": "Circle-native value claim",
            "ready": circle_value_ready,
            "evidence": item.get("circle_native_value", ""),
            "refs": item.get("living_book_refs", []) or [],
            "circle_native_claimed": circle_native_claimed,
        },
        {
            "id": "proof_backing",
            "label": "paper, theorem, source, executable, and Living Book backing",
            "ready": proof_backing_ready,
            "evidence": (
                f"papers {evidence_counts.get('paper_count', 0)}; "
                f"theorem refs "
                f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_ref_contract.get('total_count', 0)}; "
                f"sources {source_ref_contract.get('backed_count', 0)}/"
                f"{source_ref_contract.get('total_count', 0)}; "
                f"executables {evidence_counts.get('executable_count', 0)}; "
                f"Living Book pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}"
            ),
            "refs": [],
        },
        {
            "id": "review_entry",
            "label": "skeptical-reader review entry",
            "ready": review_ready,
            "evidence": (
                f"review packet {review_packet_contract.get('ready_section_count', 0)}/"
                f"{review_packet_contract.get('total_section_count', 0)} sections"
            ),
            "refs": [],
        },
        {
            "id": "advertising_boundary",
            "label": "advertising boundary",
            "ready": boundary_ready,
            "evidence": item.get("not_claimed", ""),
            "refs": [],
        },
    ]
    ready = all(section["ready"] for section in sections)
    summary_lines = [
        f"Standard reference: {item.get('standard_math_anchor', '')}",
        f"Circle expression: {item.get('circle_math_expression', '')}",
        f"Circle-native value: {item.get('circle_native_value', '')}",
        (
            f"Proof backing: {evidence_counts.get('paper_count', 0)} paper ids, "
            f"{theorem_ref_contract.get('proved_and_paper_backed_count', 0)}/"
            f"{theorem_ref_contract.get('total_count', 0)} theorem refs, "
            f"{source_ref_contract.get('backed_count', 0)}/"
            f"{source_ref_contract.get('total_count', 0)} source refs, "
            f"{evidence_counts.get('executable_count', 0)} executable refs, and "
            f"{living_book_ref_contract.get('backed_page_count', 0)}/"
            f"{living_book_ref_contract.get('total_page_count', 0)} Living Book page refs."
        ),
        f"Boundary: {item.get('not_claimed', '')}",
    ]
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "standard_parity_claimed": standard_parity_claimed,
        "circle_native_claimed": circle_native_claimed,
        "summary_lines": summary_lines,
        "sections": sections,
    }


def capability_claim_contract(
    item: dict,
    evidence_counts: dict[str, int],
    proved_theorem_ids: set[str],
    known_paper_ids: set[str],
    theorem_ref_contract: dict,
    source_ref_contract: dict,
    living_book_ref_contract: dict,
    claim_language_contract: dict,
    value_proposition_contract: dict,
    proof_trail_contract: dict,
    review_packet_contract: dict,
    parity_value_comparison_contract: dict,
) -> dict:
    roles = set(item.get("portfolio_roles", []) or [])
    provenance_kind = item.get("proof_provenance_kind", "")
    paper_ids = item.get("paper_ids", []) or []
    theorem_ids = item.get("theorem_ids", []) or []
    source_refs = item.get("source_refs", []) or []
    executable_refs = item.get("executable_refs", []) or []
    living_book_refs = item.get("living_book_refs", []) or []
    unknown_papers = sorted(set(paper_ids) - known_paper_ids)
    unproved_theorems = sorted(set(theorem_ids) - proved_theorem_ids)
    unproved_or_unbacked_theorems = sorted(
        set(theorem_ref_contract.get("unproved_or_unbacked_ids", []) + unproved_theorems)
    )
    missing_sources = sorted(ref for ref in source_refs if unsafe_or_missing_path(ref))
    unbacked_sources = source_ref_contract.get("unbacked_refs", [])
    executable_failures = sorted(
        ref
        for ref in executable_refs
        if (
            ref not in source_refs
            or unsafe_or_missing_path(ref)
            or not Path(ref).name.startswith("test_")
            or Path(ref).suffix != ".py"
        )
    )
    unbacked_living_pages = living_book_ref_contract.get("unbacked_pages", [])
    unbacked_living_widgets = living_book_ref_contract.get("unbacked_widgets", [])
    verification_recipe = capability_verification_recipe(item)
    expected_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
    recipe_failures = []
    if verification_recipe["pytest_command"] != expected_pytest_command:
        recipe_failures.append("pytest command does not match executable refs")
    if verification_recipe["lean_command"] != "lake build":
        recipe_failures.append("Lean command is not lake build")
    if verification_recipe["site_command"] != "make sitecheck":
        recipe_failures.append("site command is not make sitecheck")
    gates = [
        contract_gate(
            "role_contract",
            "standard parity or Circle-native role",
            bool(roles & CLAIM_CONTRACT_ROLES),
            ", ".join(sorted(roles)) or "none",
        ),
        contract_gate(
            "standard_anchor",
            "standard math anchor",
            nonempty_text(item, "standard_math_anchor"),
            item.get("standard_math_anchor", ""),
        ),
        contract_gate(
            "circle_expression",
            "Circle Math expression",
            nonempty_text(item, "circle_math_expression"),
            item.get("circle_math_expression", ""),
        ),
        contract_gate(
            "circle_native_value",
            "Circle-native value",
            nonempty_text(item, "circle_native_value"),
            item.get("circle_native_value", ""),
        ),
        contract_gate(
            "advertised_claim",
            "advertised claim",
            nonempty_text(item, "advertised_claim"),
            item.get("advertised_claim", ""),
        ),
        contract_gate(
            "proof_scope",
            "proof scope",
            nonempty_text(item, "proof_scope"),
            item.get("proof_scope", ""),
        ),
        contract_gate(
            "proof_provenance_kind",
            "proof provenance kind",
            provenance_kind in CLAIM_CONTRACT_PROVENANCE_KINDS,
            provenance_kind or "none",
        ),
        contract_gate(
            "proof_provenance",
            "proof provenance text",
            nonempty_text(item, "proof_provenance"),
            item.get("proof_provenance", ""),
        ),
        contract_gate(
            "paper_backing",
            "paper backing",
            evidence_counts["paper_count"] > 0 and not unknown_papers,
            contract_count_or_failures(evidence_counts["paper_count"], unknown_papers),
        ),
        contract_gate(
            "proved_theorem_ids",
            "proved paper-carried theorem ids",
            (
                evidence_counts["theorem_count"] > 0
                and not unproved_or_unbacked_theorems
                and theorem_ref_contract.get("proved_and_paper_backed_count")
                == evidence_counts["theorem_count"]
            ),
            contract_count_or_failures(
                theorem_ref_contract.get("proved_and_paper_backed_count", 0),
                unproved_or_unbacked_theorems,
            ),
        ),
        contract_gate(
            "dictionary_backing",
            "dictionary backing",
            evidence_counts["dictionary_count"] > 0,
            str(evidence_counts["dictionary_count"]),
        ),
        contract_gate(
            "source_trail",
            "paper-backed source refs",
            (
                evidence_counts["source_count"] > 0
                and not missing_sources
                and not unbacked_sources
                and source_ref_contract.get("backed_count") == evidence_counts["source_count"]
            ),
            contract_count_or_failures(
                source_ref_contract.get("backed_count", 0),
                sorted(set(missing_sources + unbacked_sources)),
            ),
        ),
        contract_gate(
            "executable_reference",
            "executable pytest reference",
            evidence_counts["executable_count"] > 0 and not executable_failures,
            contract_count_or_failures(evidence_counts["executable_count"], executable_failures),
        ),
        contract_gate(
            "verification_recipe",
            "reproducible verification recipe",
            evidence_counts["executable_count"] > 0 and not recipe_failures,
            contract_count_or_failures(evidence_counts["executable_count"], recipe_failures),
        ),
        contract_gate(
            "living_book_presentation",
            "Living Book presentation",
            (
                evidence_counts["living_book_page_count"] > 0
                and living_book_ref_contract.get("backed_page_count")
                == evidence_counts["living_book_page_count"]
                and living_book_ref_contract.get("backed_widget_count")
                == evidence_counts["living_book_widget_count"]
                and not unbacked_living_pages
                and not unbacked_living_widgets
            ),
            (
                f"pages {living_book_ref_contract.get('backed_page_count', 0)}/"
                f"{living_book_ref_contract.get('total_page_count', 0)}; "
                f"widgets {living_book_ref_contract.get('backed_widget_count', 0)}/"
                f"{living_book_ref_contract.get('total_widget_count', 0)}"
                + (
                    "; failures: "
                    + ", ".join(sorted(unbacked_living_pages + unbacked_living_widgets))
                    if unbacked_living_pages or unbacked_living_widgets
                    else ""
                )
            ),
        ),
        contract_gate(
            "claim_language_guardrail",
            "advertising language guardrail",
            claim_language_contract.get("ready_to_advertise", False),
            (
                "clean"
                if claim_language_contract.get("ready_to_advertise", False)
                else ", ".join(
                    f"{item.get('field', '')}:{item.get('pattern', '')}"
                    for item in claim_language_contract.get("flagged_phrases", [])
                )
                or "missing explicit boundary"
            ),
        ),
        contract_gate(
            "value_proposition",
            "role-backed value proposition",
            value_proposition_contract.get("ready_to_advertise", False),
            "; ".join(
                f"{role} {check.get('evidence', '')}"
                for role, check in value_proposition_contract.get("role_checks", {}).items()
                if check.get("required")
            )
            or "no required roles",
        ),
        contract_gate(
            "proof_trail",
            "ordered proof trail",
            proof_trail_contract.get("ready_to_advertise", False),
            f"{proof_trail_contract.get('passed_step_count', 0)}/"
            f"{proof_trail_contract.get('total_step_count', 0)} steps",
        ),
        contract_gate(
            "review_packet",
            "skeptical-reader review packet",
            review_packet_contract.get("ready_to_review", False),
            f"{review_packet_contract.get('ready_section_count', 0)}/"
            f"{review_packet_contract.get('total_section_count', 0)} sections",
        ),
        contract_gate(
            "parity_value_comparison",
            "standard-parity versus Circle-native comparison",
            parity_value_comparison_contract.get("ready_to_review", False),
            f"{parity_value_comparison_contract.get('ready_section_count', 0)}/"
            f"{parity_value_comparison_contract.get('total_section_count', 0)} sections",
        ),
        contract_gate(
            "claim_boundary",
            "not-claimed boundary",
            nonempty_text(item, "not_claimed")
            and claim_language_contract.get("explicit_boundary", False),
            item.get("not_claimed", ""),
        ),
    ]
    ready = all(gate["passed"] for gate in gates)
    return {
        "status": "ready" if ready else "incomplete",
        "ready_to_advertise": ready,
        "passed_gate_count": sum(1 for gate in gates if gate["passed"]),
        "total_gate_count": len(gates),
        "gates": gates,
    }


def portfolio_backing_contract_summary(capabilities: list[dict]) -> dict:
    theorem_refs = {
        "proved_and_paper_backed_count": 0,
        "total_count": 0,
        "unproved_or_unbacked_refs": [],
    }
    source_refs = {
        "backed_count": 0,
        "total_count": 0,
        "unbacked_refs": [],
    }
    living_book_refs = {
        "backed_page_count": 0,
        "total_page_count": 0,
        "backed_widget_count": 0,
        "total_widget_count": 0,
        "unbacked_pages": [],
        "unbacked_widgets": [],
    }
    review_packets = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    parity_value_comparisons = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    for capability in capabilities:
        capability_id = capability.get("id", "<missing id>")
        theorem_contract = capability.get("theorem_ref_contract", {}) or {}
        source_contract = capability.get("source_ref_contract", {}) or {}
        living_contract = capability.get("living_book_ref_contract", {}) or {}
        review_contract = capability.get("review_packet_contract", {}) or {}

        theorem_refs["proved_and_paper_backed_count"] += theorem_contract.get(
            "proved_and_paper_backed_count", 0
        )
        theorem_refs["total_count"] += theorem_contract.get("total_count", 0)
        theorem_refs["unproved_or_unbacked_refs"].extend(
            f"{capability_id}#{theorem_id}"
            for theorem_id in theorem_contract.get("unproved_or_unbacked_ids", []) or []
        )

        source_refs["backed_count"] += source_contract.get("backed_count", 0)
        source_refs["total_count"] += source_contract.get("total_count", 0)
        source_refs["unbacked_refs"].extend(
            f"{capability_id}#{ref}"
            for ref in source_contract.get("unbacked_refs", []) or []
        )

        living_book_refs["backed_page_count"] += living_contract.get(
            "backed_page_count", 0
        )
        living_book_refs["total_page_count"] += living_contract.get(
            "total_page_count", 0
        )
        living_book_refs["backed_widget_count"] += living_contract.get(
            "backed_widget_count", 0
        )
        living_book_refs["total_widget_count"] += living_contract.get(
            "total_widget_count", 0
        )
        living_book_refs["unbacked_pages"].extend(
            f"{capability_id}#{page}"
            for page in living_contract.get("unbacked_pages", []) or []
        )
        living_book_refs["unbacked_widgets"].extend(
            f"{capability_id}#{widget}"
            for widget in living_contract.get("unbacked_widgets", []) or []
        )
        review_packets["total_count"] += 1
        if review_contract.get("ready_to_review", False):
            review_packets["ready_count"] += 1
        else:
            review_packets["incomplete_capability_ids"].append(capability_id)
        comparison_contract = capability.get("parity_value_comparison_contract", {}) or {}
        parity_value_comparisons["total_count"] += 1
        if comparison_contract.get("ready_to_review", False):
            parity_value_comparisons["ready_count"] += 1
        else:
            parity_value_comparisons["incomplete_capability_ids"].append(capability_id)

    theorem_ready = (
        theorem_refs["proved_and_paper_backed_count"] == theorem_refs["total_count"]
        and not theorem_refs["unproved_or_unbacked_refs"]
    )
    source_ready = (
        source_refs["backed_count"] == source_refs["total_count"]
        and not source_refs["unbacked_refs"]
    )
    living_ready = (
        living_book_refs["backed_page_count"] == living_book_refs["total_page_count"]
        and living_book_refs["backed_widget_count"] == living_book_refs["total_widget_count"]
        and not living_book_refs["unbacked_pages"]
        and not living_book_refs["unbacked_widgets"]
    )
    review_ready = (
        review_packets["ready_count"] == review_packets["total_count"]
        and not review_packets["incomplete_capability_ids"]
    )
    comparison_ready = (
        parity_value_comparisons["ready_count"] == parity_value_comparisons["total_count"]
        and not parity_value_comparisons["incomplete_capability_ids"]
    )
    return {
        "ready_to_advertise": (
            theorem_ready and source_ready and living_ready and review_ready and comparison_ready
        ),
        "theorem_refs": theorem_refs,
        "source_refs": source_refs,
        "living_book_refs": living_book_refs,
        "review_packets": review_packets,
        "parity_value_comparisons": parity_value_comparisons,
    }


def route_backing_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    unknown_capability_ids = [
        capability_id
        for capability_id in capability_ids
        if capability_id not in capability_by_id
    ]
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    incomplete_capability_ids = [
        capability.get("id", "<missing id>")
        for capability in route_capabilities
        if not (capability.get("claim_contract", {}) or {}).get("ready_to_advertise")
    ]
    theorem_refs = {
        "proved_and_paper_backed_count": 0,
        "total_count": 0,
        "unproved_or_unbacked_refs": [],
    }
    source_refs = {
        "backed_count": 0,
        "total_count": 0,
        "unbacked_refs": [],
    }
    living_book_refs = {
        "backed_page_count": 0,
        "total_page_count": 0,
        "backed_widget_count": 0,
        "total_widget_count": 0,
        "unbacked_pages": [],
        "unbacked_widgets": [],
    }
    review_packets = {
        "ready_count": 0,
        "total_count": 0,
        "incomplete_capability_ids": [],
    }
    paper_ids: set[str] = set()
    theorem_ids: set[str] = set()
    dictionary_ids: set[str] = set()
    executable_refs: set[str] = set()
    source_ref_ids: set[str] = set()
    living_book_pages: set[str] = set()
    living_book_widgets: set[str] = set()
    roles: set[str] = set()
    provenance_kinds: set[str] = set()

    for capability in route_capabilities:
        capability_id = capability.get("id", "<missing id>")
        roles.update(capability.get("portfolio_roles", []) or [])
        provenance_kind = capability.get("proof_provenance_kind", "")
        if provenance_kind:
            provenance_kinds.add(provenance_kind)
        paper_ids.update(capability.get("paper_ids", []) or [])
        theorem_ids.update(capability.get("theorem_ids", []) or [])
        dictionary_ids.update(capability.get("dictionary_ids", []) or [])
        executable_refs.update(capability.get("executable_refs", []) or [])
        source_ref_ids.update(capability.get("source_refs", []) or [])
        for ref in capability.get("living_book_refs", []) or []:
            if not isinstance(ref, dict):
                continue
            page = ref.get("page", "")
            if page:
                living_book_pages.add(page)
            for widget_id in ref.get("widget_ids", []) or []:
                if widget_id:
                    living_book_widgets.add(widget_id)

        theorem_contract = capability.get("theorem_ref_contract", {}) or {}
        source_contract = capability.get("source_ref_contract", {}) or {}
        living_contract = capability.get("living_book_ref_contract", {}) or {}
        review_contract = capability.get("review_packet_contract", {}) or {}
        theorem_refs["proved_and_paper_backed_count"] += theorem_contract.get(
            "proved_and_paper_backed_count", 0
        )
        theorem_refs["total_count"] += theorem_contract.get("total_count", 0)
        theorem_refs["unproved_or_unbacked_refs"].extend(
            f"{capability_id}#{theorem_id}"
            for theorem_id in theorem_contract.get("unproved_or_unbacked_ids", []) or []
        )
        source_refs["backed_count"] += source_contract.get("backed_count", 0)
        source_refs["total_count"] += source_contract.get("total_count", 0)
        source_refs["unbacked_refs"].extend(
            f"{capability_id}#{ref}"
            for ref in source_contract.get("unbacked_refs", []) or []
        )
        living_book_refs["backed_page_count"] += living_contract.get(
            "backed_page_count", 0
        )
        living_book_refs["total_page_count"] += living_contract.get(
            "total_page_count", 0
        )
        living_book_refs["backed_widget_count"] += living_contract.get(
            "backed_widget_count", 0
        )
        living_book_refs["total_widget_count"] += living_contract.get(
            "total_widget_count", 0
        )
        living_book_refs["unbacked_pages"].extend(
            f"{capability_id}#{page}"
            for page in living_contract.get("unbacked_pages", []) or []
        )
        living_book_refs["unbacked_widgets"].extend(
            f"{capability_id}#{widget}"
            for widget in living_contract.get("unbacked_widgets", []) or []
        )
        review_packets["total_count"] += 1
        if review_contract.get("ready_to_review", False):
            review_packets["ready_count"] += 1
        else:
            review_packets["incomplete_capability_ids"].append(capability_id)

    theorem_ready = (
        theorem_refs["proved_and_paper_backed_count"] == theorem_refs["total_count"]
        and not theorem_refs["unproved_or_unbacked_refs"]
    )
    source_ready = (
        source_refs["backed_count"] == source_refs["total_count"]
        and not source_refs["unbacked_refs"]
    )
    living_ready = (
        living_book_refs["backed_page_count"] == living_book_refs["total_page_count"]
        and living_book_refs["backed_widget_count"] == living_book_refs["total_widget_count"]
        and not living_book_refs["unbacked_pages"]
        and not living_book_refs["unbacked_widgets"]
    )
    review_ready = (
        review_packets["ready_count"] == review_packets["total_count"]
        and not review_packets["incomplete_capability_ids"]
    )
    route_claim_language_contract = claim_language_contract(
        route,
        ROUTE_CLAIM_LANGUAGE_FIELDS,
    )
    return {
        "ready_to_advertise": (
            bool(capability_ids)
            and not unknown_capability_ids
            and not incomplete_capability_ids
            and theorem_ready
            and source_ready
            and living_ready
            and review_ready
            and route_claim_language_contract["ready_to_advertise"]
        ),
        "capability_count": len(capability_ids),
        "ready_capability_count": len(route_capabilities) - len(incomplete_capability_ids),
        "unknown_capability_ids": unknown_capability_ids,
        "incomplete_capability_ids": incomplete_capability_ids,
        "covered_roles": sorted(roles),
        "proof_provenance_kinds": sorted(provenance_kinds),
        "unique_evidence_counts": {
            "paper_count": len(paper_ids),
            "theorem_count": len(theorem_ids),
            "dictionary_count": len(dictionary_ids),
            "executable_count": len(executable_refs),
            "source_count": len(source_ref_ids),
            "living_book_page_count": len(living_book_pages),
            "living_book_widget_count": len(living_book_widgets),
        },
        "theorem_refs": theorem_refs,
        "source_refs": source_refs,
        "living_book_refs": living_book_refs,
        "review_packets": review_packets,
        "claim_language_contract": route_claim_language_contract,
    }


def route_review_dossier_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    route_contract = route_backing_contract(route, capability_by_id)
    executable_refs = sorted(
        {
            ref
            for capability in route_capabilities
            for ref in (capability.get("executable_refs", []) or [])
        }
    )
    route_pytest_command = shlex.join(["python", "-m", "pytest", *executable_refs])
    role_counts: dict[str, dict[str, int]] = {}
    for role in ("standard_math_parity", "circle_native_value", "application_guardrail"):
        required_capabilities = [
            capability
            for capability in route_capabilities
            if role in (capability.get("portfolio_roles", []) or [])
        ]
        ready_capabilities = [
            capability
            for capability in required_capabilities
            if (
                (
                    capability.get("value_proposition_contract", {})
                    or {}
                ).get("role_checks", {})
                or {}
            ).get(role, {}).get("ready", False)
        ]
        role_counts[role] = {
            "ready_count": len(ready_capabilities),
            "total_count": len(required_capabilities),
        }

    theorem_refs = route_contract.get("theorem_refs", {}) or {}
    source_refs = route_contract.get("source_refs", {}) or {}
    living_refs = route_contract.get("living_book_refs", {}) or {}
    review_packets = route_contract.get("review_packets", {}) or {}
    route_language = route_contract.get("claim_language_contract", {}) or {}
    capability_language_ready_count = sum(
        1
        for capability in route_capabilities
        if (capability.get("claim_language_contract", {}) or {}).get(
            "ready_to_advertise",
            False,
        )
    )
    proof_provenance_kinds = route_contract.get("proof_provenance_kinds", []) or []
    theorem_ready = (
        theorem_refs.get("total_count", 0) > 0
        and theorem_refs.get("proved_and_paper_backed_count")
        == theorem_refs.get("total_count")
        and not theorem_refs.get("unproved_or_unbacked_refs", [])
    )
    source_ready = (
        source_refs.get("total_count", 0) > 0
        and source_refs.get("backed_count") == source_refs.get("total_count")
        and not source_refs.get("unbacked_refs", [])
    )
    living_ready = (
        living_refs.get("total_page_count", 0) > 0
        and living_refs.get("backed_page_count") == living_refs.get("total_page_count")
        and living_refs.get("backed_widget_count") == living_refs.get("total_widget_count")
        and not living_refs.get("unbacked_pages", [])
        and not living_refs.get("unbacked_widgets", [])
    )
    standard_ready = (
        role_counts["standard_math_parity"]["total_count"] > 0
        and role_counts["standard_math_parity"]["ready_count"]
        == role_counts["standard_math_parity"]["total_count"]
    )
    circle_native_ready = (
        role_counts["circle_native_value"]["total_count"] > 0
        and role_counts["circle_native_value"]["ready_count"]
        == role_counts["circle_native_value"]["total_count"]
    )
    guardrail_ready = (
        route_language.get("ready_to_advertise", False)
        and capability_language_ready_count == len(route_capabilities)
        and all(nonempty_text(capability, "not_claimed") for capability in route_capabilities)
    )
    sections = [
        {
            "id": "route_scope_boundary",
            "label": "route claim, audience, and boundary",
            "ready": (
                nonempty_text(route, "audience")
                and nonempty_text(route, "route_claim")
                and nonempty_text(route, "not_claimed")
                and route_language.get("ready_to_advertise", False)
            ),
            "evidence": (
                "route claim language clean"
                if route_language.get("ready_to_advertise", False)
                else "route claim language incomplete"
            ),
            "refs": [],
        },
        {
            "id": "capability_review_packets",
            "label": "capability review packets",
            "ready": (
                review_packets.get("total_count", 0) > 0
                and review_packets.get("ready_count") == review_packets.get("total_count")
                and not review_packets.get("incomplete_capability_ids", [])
                and not route_contract.get("unknown_capability_ids", [])
                and not route_contract.get("incomplete_capability_ids", [])
            ),
            "evidence": (
                f"{review_packets.get('ready_count', 0)}/"
                f"{review_packets.get('total_count', 0)} packets"
            ),
            "refs": capability_ids,
        },
        {
            "id": "standard_parity_surface",
            "label": "standard-math parity surface",
            "ready": standard_ready,
            "evidence": (
                f"{role_counts['standard_math_parity']['ready_count']}/"
                f"{role_counts['standard_math_parity']['total_count']} standard-parity lanes"
            ),
            "refs": [
                capability.get("id", "")
                for capability in route_capabilities
                if "standard_math_parity" in (capability.get("portfolio_roles", []) or [])
            ],
        },
        {
            "id": "circle_native_surface",
            "label": "Circle-native value surface",
            "ready": circle_native_ready,
            "evidence": (
                f"{role_counts['circle_native_value']['ready_count']}/"
                f"{role_counts['circle_native_value']['total_count']} Circle-native lanes"
            ),
            "refs": [
                capability.get("id", "")
                for capability in route_capabilities
                if "circle_native_value" in (capability.get("portfolio_roles", []) or [])
            ],
        },
        {
            "id": "proof_provenance_surface",
            "label": "proof provenance and backing surface",
            "ready": bool(proof_provenance_kinds) and theorem_ready and source_ready and living_ready,
            "evidence": (
                f"provenance {', '.join(proof_provenance_kinds) or 'none'}; "
                f"theorems {theorem_refs.get('proved_and_paper_backed_count', 0)}/"
                f"{theorem_refs.get('total_count', 0)}; "
                f"sources {source_refs.get('backed_count', 0)}/"
                f"{source_refs.get('total_count', 0)}"
            ),
            "refs": proof_provenance_kinds,
        },
        {
            "id": "route_reproduction_command",
            "label": "route-wide executable reproduction command",
            "ready": bool(executable_refs),
            "evidence": route_pytest_command,
            "refs": executable_refs,
            "command": route_pytest_command,
        },
        {
            "id": "advertising_guardrails",
            "label": "route and capability advertising guardrails",
            "ready": guardrail_ready,
            "evidence": (
                f"route language {'pass' if route_language.get('ready_to_advertise', False) else 'fail'}; "
                f"capability language {capability_language_ready_count}/{len(route_capabilities)}"
            ),
            "refs": capability_ids,
        },
    ]
    ready = all(section["ready"] for section in sections)
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "role_counts": role_counts,
        "sections": sections,
    }


def route_impact_summary_contract(route: dict, capability_by_id: dict[str, dict]) -> dict:
    capability_ids = route.get("capability_ids", []) or []
    route_capabilities = [
        capability_by_id[capability_id]
        for capability_id in capability_ids
        if capability_id in capability_by_id
    ]
    route_contract = route_backing_contract(route, capability_by_id)
    route_dossier = route_review_dossier_contract(route, capability_by_id)
    unique_counts = route_contract.get("unique_evidence_counts", {}) or {}
    route_language = route_contract.get("claim_language_contract", {}) or {}
    areas = sorted(
        {
            str(capability.get("area", "")).strip()
            for capability in route_capabilities
            if str(capability.get("area", "")).strip()
        }
    )
    standard_interest_refs = [
        {
            "capability_id": capability.get("id", ""),
            "area": capability.get("area", ""),
            "audience_interest": capability.get("audience_interest", ""),
            "standard_math_anchor": capability.get("standard_math_anchor", ""),
        }
        for capability in route_capabilities
    ]
    circle_native_value_refs = [
        {
            "capability_id": capability.get("id", ""),
            "circle_math_expression": capability.get("circle_math_expression", ""),
            "circle_native_value": capability.get("circle_native_value", ""),
        }
        for capability in route_capabilities
    ]
    capability_language_ready_count = sum(
        1
        for capability in route_capabilities
        if (capability.get("claim_language_contract", {}) or {}).get(
            "ready_to_advertise",
            False,
        )
    )
    audience_ready = (
        nonempty_text(route, "title")
        and nonempty_text(route, "audience")
        and nonempty_text(route, "route_claim")
    )
    interest_ready = bool(standard_interest_refs) and all(
        str(ref.get("area", "")).strip()
        and str(ref.get("audience_interest", "")).strip()
        and str(ref.get("standard_math_anchor", "")).strip()
        for ref in standard_interest_refs
    )
    circle_value_ready = bool(circle_native_value_refs) and all(
        str(ref.get("circle_math_expression", "")).strip()
        and str(ref.get("circle_native_value", "")).strip()
        for ref in circle_native_value_refs
    )
    proof_backing_ready = (
        route_contract.get("ready_to_advertise", False)
        and unique_counts.get("paper_count", 0) > 0
        and unique_counts.get("theorem_count", 0) > 0
        and unique_counts.get("source_count", 0) > 0
        and unique_counts.get("executable_count", 0) > 0
        and unique_counts.get("living_book_page_count", 0) > 0
    )
    boundary_ready = (
        route_language.get("ready_to_advertise", False)
        and nonempty_text(route, "not_claimed")
        and capability_language_ready_count == len(route_capabilities)
    )
    sections = [
        {
            "id": "audience_signal",
            "label": "audience and route signal",
            "ready": audience_ready,
            "evidence": route.get("audience", ""),
            "refs": [],
        },
        {
            "id": "standard_interest_surface",
            "label": "respected standard-math interest surface",
            "ready": interest_ready,
            "evidence": f"{len(standard_interest_refs)} capability interest anchors",
            "refs": [ref["capability_id"] for ref in standard_interest_refs],
        },
        {
            "id": "circle_native_value_surface",
            "label": "Circle-native value surface",
            "ready": circle_value_ready,
            "evidence": f"{len(circle_native_value_refs)} Circle-native value statements",
            "refs": [ref["capability_id"] for ref in circle_native_value_refs],
        },
        {
            "id": "proof_backing_counts",
            "label": "proof-backed evidence counts",
            "ready": proof_backing_ready,
            "evidence": (
                f"papers {unique_counts.get('paper_count', 0)}; "
                f"theorem refs {unique_counts.get('theorem_count', 0)}; "
                f"source refs {unique_counts.get('source_count', 0)}; "
                f"executables {unique_counts.get('executable_count', 0)}; "
                f"Living Book pages {unique_counts.get('living_book_page_count', 0)}"
            ),
            "refs": [],
        },
        {
            "id": "review_path",
            "label": "review path",
            "ready": route_dossier.get("ready_to_review", False),
            "evidence": (
                f"route dossier {route_dossier.get('ready_section_count', 0)}/"
                f"{route_dossier.get('total_section_count', 0)} sections"
            ),
            "refs": [],
        },
        {
            "id": "advertising_boundary",
            "label": "advertising boundary",
            "ready": boundary_ready,
            "evidence": route.get("not_claimed", ""),
            "refs": capability_ids,
        },
    ]
    ready = all(section["ready"] for section in sections)
    summary_lines = [
        f"Audience: {route.get('audience', '')}",
        (
            f"Capability surface: {len(route_capabilities)} route lanes"
            + (f" across {', '.join(areas)}." if areas else ".")
        ),
        (
            f"Proof backing: {unique_counts.get('theorem_count', 0)} proved theorem refs, "
            f"{unique_counts.get('paper_count', 0)} paper ids, "
            f"{unique_counts.get('source_count', 0)} source refs, "
            f"{unique_counts.get('executable_count', 0)} executable refs, "
            f"and {unique_counts.get('living_book_page_count', 0)} Living Book page refs."
        ),
        (
            f"Circle-native value: {len(circle_native_value_refs)} lanes state explicit "
            "Circle expression/value statements with role-backed checks."
        ),
        f"Boundary: {route.get('not_claimed', '')}",
    ]
    return {
        "ready_to_review": ready,
        "ready_to_advertise": ready,
        "ready_section_count": sum(1 for section in sections if section["ready"]),
        "total_section_count": len(sections),
        "areas": areas,
        "summary_lines": summary_lines,
        "standard_interest_refs": standard_interest_refs,
        "circle_native_value_refs": circle_native_value_refs,
        "sections": sections,
    }


def export_portfolio_routes(
    route_entries: list[dict],
    capability_by_id: dict[str, dict],
) -> list[dict]:
    routes: list[dict] = []
    for route in route_entries:
        item = dict(route)
        item["route_contract"] = route_backing_contract(item, capability_by_id)
        item["route_review_dossier_contract"] = route_review_dossier_contract(
            item,
            capability_by_id,
        )
        item["route_impact_summary_contract"] = route_impact_summary_contract(
            item,
            capability_by_id,
        )
        routes.append(item)
    return routes


def portfolio_route_summary(routes: list[dict]) -> dict:
    ready_count = sum(
        1
        for route in routes
        if (route.get("route_contract", {}) or {}).get("ready_to_advertise")
    )
    return {
        "route_count": len(routes),
        "ready_count": ready_count,
        "incomplete_count": len(routes) - ready_count,
        "ready_dossier_count": sum(
            1
            for route in routes
            if (route.get("route_review_dossier_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "incomplete_dossier_ids": sorted(
            route.get("id", "")
            for route in routes
            if not (route.get("route_review_dossier_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "ready_impact_summary_count": sum(
            1
            for route in routes
            if (route.get("route_impact_summary_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "incomplete_impact_summary_ids": sorted(
            route.get("id", "")
            for route in routes
            if not (route.get("route_impact_summary_contract", {}) or {}).get(
                "ready_to_review",
                False,
            )
        ),
        "unknown_capability_ids": sorted(
            {
                capability_id
                for route in routes
                for capability_id in (
                    (route.get("route_contract", {}) or {}).get("unknown_capability_ids", [])
                    or []
                )
            }
        ),
    }


def export_capability_showcase() -> dict:
    path = ROOT / "manifests" / "capability_showcase.yaml"
    if not path.exists():
        return {"capabilities": [], "portfolio_summary": {}}
    data = load_yaml(path)
    capabilities: list[dict] = []
    role_counts: dict[str, int] = {}
    proof_provenance_counts: dict[str, int] = {}
    evidence_totals = {
        "paper_count": 0,
        "theorem_count": 0,
        "dictionary_count": 0,
        "executable_count": 0,
        "source_count": 0,
        "living_book_page_count": 0,
        "living_book_widget_count": 0,
    }
    unique_papers: set[str] = set()
    unique_theorems: set[str] = set()
    unique_dictionary_ids: set[str] = set()
    unique_executables: set[str] = set()
    unique_sources: set[str] = set()
    unique_living_pages: set[str] = set()
    unique_living_widgets: set[str] = set()
    contract_ready_count = 0
    contract_gate_failures: dict[str, int] = {}
    proved_theorem_ids = proved_theorem_id_set()
    known_paper_ids = paper_id_set()
    papers = paper_manifest_by_id()
    theorems = theorem_manifest_by_id()
    local_lean_modules = lean_modules_by_name()
    known_widget_ids = widget_ids_from_files()
    for capability in data.get("capabilities", []):
        item = dict(capability)
        living_pages: set[str] = set()
        living_widgets: set[str] = set()
        for ref in item.get("living_book_refs", []) or []:
            page = ref.get("page", "")
            if page:
                living_pages.add(page)
            for widget_id in ref.get("widget_ids", []) or []:
                if widget_id:
                    living_widgets.add(widget_id)
        item["evidence_counts"] = {
            "paper_count": len(item.get("paper_ids", []) or []),
            "theorem_count": len(item.get("theorem_ids", []) or []),
            "dictionary_count": len(item.get("dictionary_ids", []) or []),
            "executable_count": len(item.get("executable_refs", []) or []),
            "source_count": len(item.get("source_refs", []) or []),
            "living_book_page_count": len(living_pages),
            "living_book_widget_count": len(living_widgets),
        }
        item["verification_recipe"] = capability_verification_recipe(item)
        item["theorem_ref_contract"] = capability_theorem_ref_contract(
            item,
            papers,
            theorems,
        )
        item["source_ref_contract"] = capability_source_ref_contract(
            item,
            papers,
            local_lean_modules,
        )
        item["living_book_ref_contract"] = capability_living_book_ref_contract(
            item,
            known_widget_ids,
        )
        item["claim_language_contract"] = claim_language_contract(
            item,
            CAPABILITY_CLAIM_LANGUAGE_FIELDS,
        )
        item["value_proposition_contract"] = value_proposition_contract(
            item,
            item["theorem_ref_contract"],
            item["source_ref_contract"],
            item["living_book_ref_contract"],
            item["claim_language_contract"],
        )
        item["proof_trail_contract"] = proof_trail_contract(
            item,
            item["theorem_ref_contract"],
            item["source_ref_contract"],
            item["living_book_ref_contract"],
            item["claim_language_contract"],
            item["value_proposition_contract"],
        )
        item["review_packet_contract"] = review_packet_contract(
            item,
            item["theorem_ref_contract"],
            item["source_ref_contract"],
            item["living_book_ref_contract"],
            item["claim_language_contract"],
            item["value_proposition_contract"],
            item["proof_trail_contract"],
        )
        item["parity_value_comparison_contract"] = parity_value_comparison_contract(
            item,
            item["theorem_ref_contract"],
            item["source_ref_contract"],
            item["living_book_ref_contract"],
            item["claim_language_contract"],
            item["value_proposition_contract"],
            item["proof_trail_contract"],
            item["review_packet_contract"],
        )
        item["claim_contract"] = capability_claim_contract(
            item,
            item["evidence_counts"],
            proved_theorem_ids,
            known_paper_ids,
            item["theorem_ref_contract"],
            item["source_ref_contract"],
            item["living_book_ref_contract"],
            item["claim_language_contract"],
            item["value_proposition_contract"],
            item["proof_trail_contract"],
            item["review_packet_contract"],
            item["parity_value_comparison_contract"],
        )
        if item["claim_contract"]["ready_to_advertise"]:
            contract_ready_count += 1
        for gate in item["claim_contract"]["gates"]:
            if not gate["passed"]:
                gate_id = gate["id"]
                contract_gate_failures[gate_id] = contract_gate_failures.get(gate_id, 0) + 1
        for role in item.get("portfolio_roles", []) or []:
            role_counts[role] = role_counts.get(role, 0) + 1
        proof_provenance_kind = item.get("proof_provenance_kind", "")
        if proof_provenance_kind:
            proof_provenance_counts[proof_provenance_kind] = (
                proof_provenance_counts.get(proof_provenance_kind, 0) + 1
            )
        for key, value in item["evidence_counts"].items():
            evidence_totals[key] += value
        unique_papers.update(item.get("paper_ids", []) or [])
        unique_theorems.update(item.get("theorem_ids", []) or [])
        unique_dictionary_ids.update(item.get("dictionary_ids", []) or [])
        unique_executables.update(item.get("executable_refs", []) or [])
        unique_sources.update(item.get("source_refs", []) or [])
        unique_living_pages.update(living_pages)
        unique_living_widgets.update(living_widgets)
        capabilities.append(item)
    capability_by_id = {
        item["id"]: item
        for item in capabilities
        if item.get("id")
    }
    portfolio_routes = export_portfolio_routes(
        data.get("portfolio_routes", []) or [],
        capability_by_id,
    )
    portfolio_summary = {
        "capability_count": len(capabilities),
        "role_counts": dict(sorted(role_counts.items())),
        "proof_provenance_counts": dict(sorted(proof_provenance_counts.items())),
        "evidence_totals": evidence_totals,
        "unique_evidence_counts": {
            "paper_count": len(unique_papers),
            "theorem_count": len(unique_theorems),
            "dictionary_count": len(unique_dictionary_ids),
            "executable_count": len(unique_executables),
            "source_count": len(unique_sources),
            "living_book_page_count": len(unique_living_pages),
            "living_book_widget_count": len(unique_living_widgets),
        },
        "unique_living_book_pages": sorted(unique_living_pages),
        "claim_contract_summary": {
            "ready_count": contract_ready_count,
            "incomplete_count": len(capabilities) - contract_ready_count,
            "gate_failure_counts": dict(sorted(contract_gate_failures.items())),
        },
        "backing_contract_summary": portfolio_backing_contract_summary(capabilities),
        "route_summary": portfolio_route_summary(portfolio_routes),
    }
    return {
        "capabilities": capabilities,
        "portfolio_routes": portfolio_routes,
        "portfolio_summary": portfolio_summary,
    }


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
    from circle_math.applications.circle_ai_contracts import build_contract_pack as build_circle_ai_contract_pack
    from circle_math.applications.theseus_hive_contracts import build_contract_pack

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
    write_json(GENERATED / "circle_ai_contract_pack.json", build_circle_ai_contract_pack())
    write_json(GENERATED / "theseus_hive_ai_contracts.json", build_contract_pack())


def main() -> int:
    export_all()
    print("site data exported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
