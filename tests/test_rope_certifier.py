from __future__ import annotations

import json
import subprocess
import sys

from circle_math.applications import (
    ROPE_CERTIFIER_THEOREMS,
    ROPE_REAL_PHASE_PRECURSOR_THEOREMS,
    RoPEConfig,
    capped_lcm,
    certify_rope_positions,
    collision_pair_count_at_gap,
    discretize_rope_periods,
    real_phase_nat_turn_error,
    sample_collision_pairs,
)


def test_discretized_period_helpers_are_deterministic() -> None:
    assert discretize_rope_periods((4.2, 7.6), "round") == (4, 8)
    assert discretize_rope_periods((4.2, 7.6), "floor") == (4, 7)
    assert discretize_rope_periods((4.2, 7.6), "ceil") == (5, 8)
    assert capped_lcm((4, 6), 10) == (12, True)
    assert capped_lcm((4, 6), 30) == (12, False)
    assert collision_pair_count_at_gap(10, 4) == 6
    assert collision_pair_count_at_gap(10, 10) == 0
    assert sample_collision_pairs(10, 4, limit=3) == ((0, 4), (1, 5), (2, 6))


def test_real_phase_nat_turn_error_matches_endpoint_precursor_shape() -> None:
    assert real_phase_nat_turn_error(
        frequency=0.25,
        full_turn=4.0,
        left=0,
        right=4,
        turns=0,
    ) == 1.0
    assert real_phase_nat_turn_error(
        frequency=0.25,
        full_turn=4.0,
        left=0,
        right=4,
        turns=1,
    ) == 3.0
    assert "AIRA-T0031" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0032" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_rope_certifier_exact_contract_finds_discrete_collision_gap() -> None:
    certificate = certify_rope_positions(
        RoPEConfig(head_dim=2, base=10000.0, context_length=20, tolerance=1e-6)
    )
    assert not certificate.exact_discrete.pass_exact
    assert certificate.exact_discrete.common_collision_gap == 6
    assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == 14
    assert certificate.exact_discrete.sample_collision_pairs[0] == (0, 6)
    assert certificate.theorem_ids == ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0024" in certificate.exact_discrete.assumptions[3]
    assert "not a model-quality" in certificate.claim_boundary


def test_rope_certifier_exact_contract_passes_when_common_gap_exceeds_context() -> None:
    certificate = certify_rope_positions(
        RoPEConfig(head_dim=4, base=10000.0, context_length=8, tolerance=1e-6)
    )
    assert certificate.exact_discrete.pass_exact
    assert certificate.exact_discrete.common_collision_gap is None
    assert certificate.exact_discrete.common_collision_gap_reaches_context
    assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == 0
    assert certificate.exact_discrete.sample_collision_pairs == ()
    assert certificate.real_phase_margin.scanned_gap_count == 7
    assert certificate.real_phase_margin.formal_precursor_theorem_ids == ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_rope_certify_cli_emits_json_certificate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/rope_certify.py",
            "--head-dim",
            "2",
            "--base",
            "10000",
            "--context",
            "20",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.rope_position_distinguishability.v0"
    assert payload["exact_discrete"]["pass_exact"] is False
    assert payload["exact_discrete"]["common_collision_gap"] == 6
    assert payload["exact_discrete"]["guaranteed_common_gap_collision_pair_count"] == 14
    assert payload["real_phase_margin"]["formal_precursor_theorem_ids"] == list(ROPE_REAL_PHASE_PRECURSOR_THEOREMS)
    assert payload["theorem_ids"] == list(ROPE_CERTIFIER_THEOREMS)


def test_rope_preset_sidecar_emits_json_and_markdown() -> None:
    json_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py",
            "--preset",
            "llama_style_10000_4k",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(json_result.stdout)
    assert payload["schema_id"] == "circle_calculus.rope_certifier_preset_results.v0"
    assert payload["presets"][0]["preset"] == "llama_style_10000_4k"
    assert payload["presets"][0]["certificate"]["exact_discrete"]["pass_exact"] is True
    assert "not model-quality" in payload["claim_boundary"]

    markdown_result = subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py",
            "--preset",
            "llama_style_10000_4k",
            "--format",
            "markdown",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "| llama_style_10000_4k |" in markdown_result.stdout
    assert "Reproduce with:" in markdown_result.stdout
