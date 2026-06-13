from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from circle_math.applications import (
    ROPE_CERTIFIER_THEOREMS,
    ROPE_RATIONAL_PRESET_4099_NAME,
    ROPE_RATIONAL_PRESET_4099_THEOREMS,
    ROPE_REAL_PHASE_PRECURSOR_THEOREMS,
    ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME,
    ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS,
    PHASE_BANK_CERTIFIER_PRESETS,
    PhaseBankConfig,
    RoPEConfig,
    brute_force_single_period_collision_pair_count,
    capped_lcm,
    certify_rational_preset_4099,
    certify_rational_turn_ratio_finite_margin,
    certify_rope_positions,
    certify_phase_bank_positions,
    certify_standard_channel0_interval_seed,
    collision_pair_count_at_gap,
    collision_pair_count_at_gap_multiples,
    discretize_rope_periods,
    phase_bank_prefix_collision_reports,
    phase_bank_certificate_summary_lines,
    phase_bank_subfamily_pass_reports,
    plan_standard_channel0_interval_bands,
    real_phase_bank_near_turn,
    real_phase_bank_turn_separated,
    real_phase_int_turn_error,
    real_phase_nat_turn_error,
    real_phase_near_turn,
    real_phase_scaled_turn_ratio_error,
    real_phase_turn_separated,
    sample_collision_pairs,
    scale_phase_bank_periods,
    scan_turn_ratio_finite_margin,
    single_period_collision_pair_count,
    standard_channel0_turn_ratio_bounds,
    turn_ratio_finite_margin_gap_candidates,
    turn_ratio_floor_ceil_witness_errors,
    turn_ratio_floor_ceil_witness_margin,
    turn_ratio_floor_ceil_witnesses_certify_margin,
    turn_ratio_margin_covers_context,
    turn_ratio_margin_covers_margin,
    turn_ratio_margin_covers_request,
    turn_ratio_nat_ratio_coprime_margin_certificate,
    turn_ratio_nat_ratio_zero_margin_witness,
    turn_ratio_nearest_integer_error,
)


def test_discretized_period_helpers_are_deterministic() -> None:
    assert discretize_rope_periods((4.2, 7.6), "round") == (4, 8)
    assert discretize_rope_periods((4.2, 7.6), "floor") == (4, 7)
    assert discretize_rope_periods((4.2, 7.6), "ceil") == (5, 8)
    assert capped_lcm((4, 6), 10) == (12, True)
    assert capped_lcm((4, 6), 30) == (12, False)
    assert collision_pair_count_at_gap(10, 4) == 6
    assert collision_pair_count_at_gap_multiples(20, 6) == 24
    assert single_period_collision_pair_count(20, 6) == 24
    assert collision_pair_count_at_gap(10, 10) == 0
    assert sample_collision_pairs(10, 4, limit=3) == ((0, 4), (1, 5), (2, 6))
    reports = phase_bank_prefix_collision_reports(20, (6, 35), limit=2)
    assert tuple(report.prefix_length for report in reports) == (1, 2)
    assert reports[0].lcm_collision_gap == 6
    assert reports[0].total_bank_collision_pair_count == 24
    assert reports[1].lcm_reaches_context
    assert reports[1].total_bank_collision_pair_count == 0
    subfamilies = phase_bank_subfamily_pass_reports(128, (6, 9, 13, 18), max_size=3)
    assert subfamilies[0].subfamily_indices == (2, 3)
    assert subfamilies[0].periods == (13, 18)
    assert subfamilies[0].lcm_value == 234


def test_single_period_collision_count_matches_bruteforce() -> None:
    for context_length in range(1, 25):
        for period in range(1, 12):
            assert single_period_collision_pair_count(
                context_length,
                period,
            ) == brute_force_single_period_collision_pair_count(context_length, period)


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
    assert real_phase_int_turn_error(
        frequency=0.25,
        full_turn=4.0,
        left=0,
        right=4,
        turns=-1,
    ) == 5.0
    assert "AIRA-T0031" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0032" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0033" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0037" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0038" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0039" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0040" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0041" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0042" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0043" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0044" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0045" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0047" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0050" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0053" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0054" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0055" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0056" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0057" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_real_phase_turn_separation_rules_out_smaller_near_turn() -> None:
    turns = range(-3, 4)
    kwargs = {
        "frequency": 0.25,
        "full_turn": 4.0,
        "left": 0,
        "right": 4,
    }
    assert real_phase_turn_separated(**kwargs, margin=1.0, turns=turns)
    assert not real_phase_near_turn(**kwargs, tolerance=0.5, turns=turns)
    assert real_phase_near_turn(**kwargs, tolerance=1.0, turns=turns)


def test_real_phase_bank_separation_rules_out_all_channel_near_turn() -> None:
    turns = range(-3, 4)
    kwargs = {
        "frequencies": (0.25, 0.5),
        "full_turn": 4.0,
        "left": 0,
        "right": 4,
    }
    assert real_phase_bank_turn_separated(**kwargs, margin=1.0, turns=turns)
    assert not real_phase_bank_near_turn(**kwargs, tolerance=0.5, turns=turns)
    assert real_phase_bank_near_turn(**kwargs, tolerance=2.0, turns=turns)


def test_real_phase_scaled_turn_ratio_error_matches_int_turn_error() -> None:
    kwargs = {
        "frequency": 0.25,
        "full_turn": 4.0,
        "left": 3,
        "right": 19,
        "turns": 1,
    }
    assert real_phase_scaled_turn_ratio_error(**kwargs) == real_phase_int_turn_error(**kwargs)


def test_turn_ratio_finite_margin_scan_matches_scaled_error() -> None:
    assert turn_ratio_finite_margin_gap_candidates(context_length=5) == (1, 2, 3, 4)
    margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=1.0 / 8.0,
        context_length=5,
    )
    assert gap == 1
    assert turns == 0
    assert margin == turn_ratio_nearest_integer_error(
        turn_ratio=1.0 / 8.0,
        gap=gap,
        turns=turns,
    )
    assert 8.0 * margin == real_phase_scaled_turn_ratio_error(
        frequency=1.0,
        full_turn=8.0,
        left=0,
        right=gap,
        turns=turns,
    )


def test_turn_ratio_floor_ceil_witness_bridge_matches_scan() -> None:
    floor_error, ceil_error = turn_ratio_floor_ceil_witness_errors(
        turn_ratio=3.0 / 7.0,
        gap=2,
    )
    assert abs(floor_error - 6.0 / 7.0) < 1e-12
    assert abs(ceil_error - 1.0 / 7.0) < 1e-12
    assert abs(
        turn_ratio_floor_ceil_witness_margin(
            turn_ratio=3.0 / 7.0,
            gap=2,
        )
        - 1.0 / 7.0
    ) < 1e-12

    for turn_ratio in (1.0 / 8.0, 3.0 / 7.0, 0.123456789):
        for context_length in (2, 5, 10):
            scanned_margin, _gap, _turns = scan_turn_ratio_finite_margin(
                turn_ratio=turn_ratio,
                context_length=context_length,
            )
            witness_margin = min(
                turn_ratio_floor_ceil_witness_margin(
                    turn_ratio=turn_ratio,
                    gap=gap,
                )
                for gap in turn_ratio_finite_margin_gap_candidates(
                    context_length=context_length,
                )
            )
            assert abs(scanned_margin - witness_margin) < 1e-12
            assert turn_ratio_floor_ceil_witnesses_certify_margin(
                turn_ratio=turn_ratio,
                margin=scanned_margin - 1e-12,
                context_length=context_length,
            )
            assert not turn_ratio_floor_ceil_witnesses_certify_margin(
                turn_ratio=turn_ratio,
                margin=scanned_margin + 1e-6,
                context_length=context_length,
            )

    assert "AIRA-T0058" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0059" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_integer_turn_ratio_has_zero_finite_margin_once_unit_gap_exists() -> None:
    margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=2.0,
        context_length=8,
    )
    assert margin == 0.0
    assert gap == 1
    assert turns == 2
    assert turn_ratio_nearest_integer_error(turn_ratio=2.0, gap=1, turns=2) == 0.0
    assert "AIRA-T0053" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_rational_turn_ratio_has_zero_margin_at_denominator_gap() -> None:
    assert turn_ratio_nat_ratio_zero_margin_witness(
        numerator=3,
        denominator=7,
        context_length=8,
    ) == (7, 3)
    assert turn_ratio_nat_ratio_zero_margin_witness(
        numerator=3,
        denominator=7,
        context_length=7,
    ) is None
    margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=3.0 / 7.0,
        context_length=8,
    )
    assert margin == 0.0
    assert gap == 7
    assert turns == 3
    assert turn_ratio_nearest_integer_error(turn_ratio=3.0 / 7.0, gap=7, turns=3) == 0.0
    assert "AIRA-T0055" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_coprime_rational_turn_ratio_certifies_margin_before_denominator_gap() -> None:
    certified_margin = turn_ratio_nat_ratio_coprime_margin_certificate(
        numerator=3,
        denominator=7,
        context_length=7,
    )
    assert certified_margin == 1.0 / 7.0
    scanned_margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=3.0 / 7.0,
        context_length=7,
    )
    assert abs(scanned_margin - certified_margin) < 1e-12
    assert gap in {2, 5}
    assert turns in {1, 2}
    assert turn_ratio_nat_ratio_coprime_margin_certificate(
        numerator=3,
        denominator=7,
        context_length=8,
    ) is None
    assert turn_ratio_nat_ratio_coprime_margin_certificate(
        numerator=2,
        denominator=6,
        context_length=6,
    ) is None
    assert "AIRA-T0056" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0057" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_named_rational_turn_ratio_certificate_is_theorem_backed() -> None:
    certificate = certify_rational_preset_4099()
    assert certificate.schema_id == "circle_calculus.rational_turn_ratio_finite_margin.v0"
    assert certificate.name == ROPE_RATIONAL_PRESET_4099_NAME
    assert certificate.numerator == 1
    assert certificate.denominator == 4099
    assert certificate.context_length == 4096
    assert certificate.pass_certificate
    assert certificate.zero_margin_witness is None
    assert certificate.certified_margin == 1.0 / 4099.0
    assert certificate.theorem_ids == ROPE_RATIONAL_PRESET_4099_THEOREMS
    assert "AIRA-T0060" in certificate.theorem_ids
    assert "AIRA-T0061" in certificate.theorem_ids
    assert "AIRA-T0062" in certificate.theorem_ids
    scanned_margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=certificate.turn_ratio,
        context_length=certificate.context_length,
    )
    assert abs(scanned_margin - certificate.certified_margin) < 1e-12
    assert gap == 1
    assert turns == 0
    assert "not a proof of the standard irrational real RoPE" in certificate.claim_boundary


def test_standard_channel0_interval_seed_is_theorem_backed() -> None:
    certificate = certify_standard_channel0_interval_seed()
    assert certificate.schema_id == "circle_calculus.standard_rope_interval_margin.v0"
    assert certificate.name == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME
    assert certificate.turn_ratio_expression == "1/(2*pi)"
    assert certificate.context_length == 333
    assert certificate.certified_margin == "1/512"
    assert certificate.pass_certificate
    assert (
        certificate.pi_bounds
        == "pi <= 4, 3.14 < pi, pi < 3.15, 3.1415 < pi, and pi < 3.1416"
    )
    assert certificate.theorem_ids == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS
    assert "AIRA-T0063" in certificate.theorem_ids
    assert "AIRA-T0064" in certificate.theorem_ids
    assert "AIRA-T0065" in certificate.theorem_ids
    assert "AIRA-T0066" in certificate.theorem_ids
    assert "AIRA-T0067" in certificate.theorem_ids
    assert "AIRA-T0077" in certificate.theorem_ids
    assert "AIRA-T0078" in certificate.theorem_ids
    assert "AIRA-T0068" in certificate.theorem_ids
    assert "AIRA-T0069" in certificate.theorem_ids
    assert "AIRA-T0070" in certificate.theorem_ids
    assert "AIRA-T0071" in certificate.theorem_ids
    assert "AIRA-T0072" in certificate.theorem_ids
    assert "AIRA-T0073" in certificate.theorem_ids
    assert "AIRA-T0074" in certificate.theorem_ids
    assert "AIRA-T0075" in certificate.theorem_ids
    assert "AIRA-T0076" in certificate.theorem_ids
    assert "AIRA-T0079" in certificate.theorem_ids
    assert "AIRA-T0080" in certificate.theorem_ids
    assert "AIRA-T0081" in certificate.theorem_ids
    assert "AIRA-T0082" in certificate.theorem_ids
    assert "AIRA-T0083" in certificate.theorem_ids
    assert "AIRA-T0084" in certificate.theorem_ids
    assert "AIRA-T0085" in certificate.theorem_ids
    assert "AIRA-T0086" in certificate.theorem_ids
    assert "AIRA-T0087" in certificate.theorem_ids
    assert "AIRA-T0088" in certificate.theorem_ids
    assert "AIRA-T0089" in certificate.theorem_ids
    assert tuple(witness.gap for witness in certificate.interval_witnesses) == tuple(
        range(1, 333)
    )
    assert certificate.interval_witnesses[0].lower == "625/3927"
    assert certificate.interval_witnesses[0].upper == "1000/6283"
    assert certificate.interval_witnesses[-1].gap == 332
    assert certificate.interval_witnesses[-1].cell == 52
    d4_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d4",
        margin=Fraction(1, 512),
        max_context_length=4096,
    )
    assert d4_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089"
    for band in d4_plan.bands:
        assert all(
            witness.cell == band.cell
            for witness in certificate.interval_witnesses[
                band.start_gap - 1 : band.end_gap
            ]
        )
    assert "context 333 only" in certificate.claim_boundary


def test_standard_channel0_interval_plan_finds_next_exact_rational_targets() -> None:
    d4_lower, d4_upper, d4_label = standard_channel0_turn_ratio_bounds(
        pi_bound_preset="d4"
    )
    assert d4_lower == Fraction(5_000, 31_416)
    assert d4_upper == Fraction(5_000, 31_415)
    assert "3.1415 < pi" in d4_label

    d4_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d4",
        margin=Fraction(1, 512),
        max_context_length=4096,
    )
    assert d4_plan.schema_id == "circle_calculus.standard_rope_interval_plan.v0"
    assert d4_plan.context_length == 333
    assert d4_plan.first_uncovered_gap == 333
    assert d4_plan.planned_margin == "1/512"
    assert d4_plan.lower_turn_ratio_bound == "625/3927"
    assert d4_plan.upper_turn_ratio_bound == "1000/6283"
    assert d4_plan.band_count == 53
    assert d4_plan.bands[0].start_gap == 1
    assert d4_plan.bands[0].end_gap == 6
    assert d4_plan.bands[0].cell == 0
    assert d4_plan.bands[-1].start_gap == 327
    assert d4_plan.bands[-1].end_gap == 332
    assert d4_plan.bands[-1].cell == 52
    assert d4_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089"
    assert "compiled Lean seed" in d4_plan.claim_boundary

    d6_lower, d6_upper, d6_label = standard_channel0_turn_ratio_bounds(
        pi_bound_preset="d6"
    )
    assert d6_lower == Fraction(500_000, 3_141_593)
    assert d6_upper == Fraction(62_500, 392_699)
    assert "3.141592 < pi" in d6_label

    d6_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d6",
        margin=Fraction(1, 1024),
        max_context_length=4096,
    )
    assert d6_plan.context_length == 710
    assert d6_plan.first_uncovered_gap == 710
    assert d6_plan.planned_margin == "1/1024"
    assert d6_plan.band_count == 113
    assert d6_plan.bands[0] == d4_plan.bands[0]
    assert d6_plan.bands[-1].start_gap == 704
    assert d6_plan.bands[-1].end_gap == 709
    assert d6_plan.bands[-1].cell == 112


def test_rational_turn_ratio_certificate_reports_denominator_boundary() -> None:
    certificate = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=8,
    )
    assert not certificate.pass_certificate
    assert certificate.certified_margin is None
    assert certificate.zero_margin_witness == (7, 3)
    assert certificate.theorem_ids == ("AIRA-T0055", "AIRA-T0057")


def test_turn_ratio_finite_margin_gap_candidates_match_range_bridge() -> None:
    assert turn_ratio_finite_margin_gap_candidates(context_length=0) == ()
    assert turn_ratio_finite_margin_gap_candidates(context_length=1) == ()
    assert turn_ratio_finite_margin_gap_candidates(context_length=6) == (1, 2, 3, 4, 5)
    assert "AIRA-T0054" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_turn_ratio_margin_context_transfer_helper_is_monotone() -> None:
    assert turn_ratio_margin_covers_context(certified_context=128_000, requested_context=8_192)
    assert turn_ratio_margin_covers_context(certified_context=128_000, requested_context=128_000)
    assert not turn_ratio_margin_covers_context(certified_context=8_192, requested_context=128_000)
    assert turn_ratio_margin_covers_margin(certified_margin=0.125, requested_margin=0.1)
    assert turn_ratio_margin_covers_margin(certified_margin=0.125, requested_margin=0.125)
    assert not turn_ratio_margin_covers_margin(certified_margin=0.125, requested_margin=0.2)
    assert turn_ratio_margin_covers_request(
        certified_context=128_000,
        requested_context=8_192,
        certified_margin=0.125,
        requested_margin=0.1,
    )
    assert not turn_ratio_margin_covers_request(
        certified_context=8_192,
        requested_context=128_000,
        certified_margin=0.125,
        requested_margin=0.1,
    )
    assert not turn_ratio_margin_covers_request(
        certified_context=128_000,
        requested_context=8_192,
        certified_margin=0.125,
        requested_margin=0.2,
    )


def test_rope_certifier_exact_contract_finds_discrete_collision_gap() -> None:
    certificate = certify_rope_positions(
        RoPEConfig(head_dim=2, base=10000.0, context_length=20, tolerance=1e-6)
    )
    assert not certificate.exact_discrete.pass_exact
    assert certificate.exact_discrete.common_collision_gap == 6
    assert certificate.exact_discrete.single_period_collision_pair_counts == (24,)
    assert certificate.exact_discrete.first_exact_pass_prefix_length is None
    assert certificate.exact_discrete.prefix_collision_reports[0].prefix_length == 1
    assert certificate.exact_discrete.prefix_collision_reports[0].lcm_collision_gap == 6
    assert certificate.exact_discrete.prefix_collision_reports[0].total_bank_collision_pair_count == 24
    assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == 14
    assert certificate.exact_discrete.guaranteed_common_gap_multiple_pair_count == 24
    assert certificate.exact_discrete.total_bank_collision_pair_count == 24
    assert certificate.exact_discrete.sample_collision_pairs[0] == (0, 6)
    assert certificate.theorem_ids == ROPE_CERTIFIER_THEOREMS
    assert tuple(layer.layer for layer in certificate.proof_layers) == (
        "exact_integer_period_phase_bank",
        "rational_discretized_finite_margin",
        "interval_backed_standard_rope",
        "numerical_real_phase_scan",
    )
    assert certificate.proof_layers[0].status == "FAIL"
    assert certificate.proof_layers[1].status == "AVAILABLE_NAMED_PRESET"
    assert certificate.proof_layers[2].status == "AVAILABLE_SEED_CONTEXT_333"
    assert certificate.proof_layers[2].theorem_ids == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS
    assert not certificate.proof_layers[3].theorem_backed
    assert "AIRA-T0046" in certificate.theorem_ids
    assert "AIRA-T0048" in certificate.theorem_ids
    assert "AIRA-T0049" in certificate.theorem_ids
    assert "AIRA-T0051" in certificate.theorem_ids
    assert "AIRA-T0052" in certificate.theorem_ids
    assert "AIRA-T0024" in certificate.exact_discrete.assumptions[3]
    assert "AIRA-T0049" in certificate.exact_discrete.assumptions[-1]
    assert "not a model-quality" in certificate.claim_boundary


def test_rope_certifier_exact_contract_passes_when_common_gap_exceeds_context() -> None:
    certificate = certify_rope_positions(
        RoPEConfig(head_dim=4, base=10000.0, context_length=8, tolerance=1e-6)
    )
    assert certificate.exact_discrete.pass_exact
    assert certificate.exact_discrete.common_collision_gap is None
    assert certificate.exact_discrete.common_collision_gap_reaches_context
    assert certificate.exact_discrete.single_period_collision_pair_counts == (2, 0)
    assert certificate.exact_discrete.first_exact_pass_prefix_length == 2
    assert certificate.exact_discrete.prefix_collision_reports[0].total_bank_collision_pair_count == 2
    assert certificate.exact_discrete.prefix_collision_reports[1].lcm_reaches_context
    assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == 0
    assert certificate.exact_discrete.guaranteed_common_gap_multiple_pair_count == 0
    assert certificate.exact_discrete.total_bank_collision_pair_count == 0
    assert certificate.exact_discrete.sample_collision_pairs == ()
    assert "AIRA-T0046" in certificate.theorem_ids
    assert "AIRA-T0048" in certificate.theorem_ids
    assert "AIRA-T0049" in certificate.theorem_ids
    assert "AIRA-T0051" in certificate.theorem_ids
    assert "AIRA-T0052" in certificate.theorem_ids
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
    assert payload["exact_discrete"]["single_period_collision_pair_counts"] == [24]
    assert payload["exact_discrete"]["first_exact_pass_prefix_length"] is None
    assert payload["exact_discrete"]["prefix_collision_reports"][0]["lcm_collision_gap"] == 6
    assert payload["exact_discrete"]["smallest_pass_subfamily_size"] is None
    assert payload["exact_discrete"]["guaranteed_common_gap_collision_pair_count"] == 14
    assert payload["exact_discrete"]["guaranteed_common_gap_multiple_pair_count"] == 24
    assert payload["exact_discrete"]["total_bank_collision_pair_count"] == 24
    assert payload["real_phase_margin"]["formal_precursor_theorem_ids"] == list(ROPE_REAL_PHASE_PRECURSOR_THEOREMS)
    assert [layer["layer"] for layer in payload["proof_layers"]] == [
        "exact_integer_period_phase_bank",
        "rational_discretized_finite_margin",
        "interval_backed_standard_rope",
        "numerical_real_phase_scan",
    ]
    assert payload["proof_layers"][2]["theorem_ids"] == list(
        ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS
    )
    assert payload["proof_layers"][3]["theorem_backed"] is False
    assert payload["theorem_ids"] == list(ROPE_CERTIFIER_THEOREMS)


def test_rope_diagnostic_preset_reports_exact_failure() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/rope_certify.py",
            "--preset",
            "diagnostic_single_channel_10000_20",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert payload["exact_discrete"]["pass_exact"] is False
    assert payload["exact_discrete"]["common_collision_gap"] == 6
    assert payload["exact_discrete"]["guaranteed_common_gap_collision_pair_count"] == 14
    assert payload["exact_discrete"]["total_bank_collision_pair_count"] == 24


def test_rope_diagnostic_prefix_and_shared_factor_presets_are_stable() -> None:
    prefix_result = subprocess.run(
        [
            sys.executable,
            "scripts/rope_certify.py",
            "--preset",
            "diagnostic_prefix_pass_4_128",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    prefix_payload = json.loads(prefix_result.stdout)
    assert prefix_payload["exact_discrete"]["pass_exact"] is True
    assert prefix_payload["exact_discrete"]["discretized_periods"] == [6, 9, 13, 18]
    assert prefix_payload["exact_discrete"]["first_exact_pass_prefix_length"] == 3
    assert prefix_payload["exact_discrete"]["smallest_pass_subfamily_size"] == 2
    assert prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["subfamily_indices"] == [2, 3]
    assert prefix_payload["exact_discrete"]["prefix_collision_reports"][1]["lcm_collision_gap"] == 18
    assert prefix_payload["exact_discrete"]["prefix_collision_reports"][2]["lcm_reaches_context"]

    shared_result = subprocess.run(
        [
            sys.executable,
            "scripts/rope_certify.py",
            "--preset",
            "diagnostic_shared_factor_25_64",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    shared_payload = json.loads(shared_result.stdout)
    assert shared_payload["exact_discrete"]["pass_exact"] is False
    assert shared_payload["exact_discrete"]["discretized_periods"] == [6, 18, 54]
    assert shared_payload["exact_discrete"]["common_collision_gap"] == 54
    assert shared_payload["exact_discrete"]["total_bank_collision_pair_count"] == 10
    assert shared_payload["exact_discrete"]["prefix_collision_reports"][2]["total_bank_collision_pair_count"] == 10


def test_explicit_phase_bank_certifier_reports_exact_only_contract() -> None:
    certificate = certify_phase_bank_positions(
        PhaseBankConfig(periods=(6, 9, 13, 18), context_length=128),
    )
    assert certificate.schema_id == "circle_calculus.integer_phase_bank_distinguishability.v0"
    assert certificate.exact_discrete.pass_exact
    assert certificate.exact_discrete.first_exact_pass_prefix_length == 3
    assert certificate.exact_discrete.smallest_pass_subfamily_size == 2
    assert certificate.exact_discrete.subfamily_pass_reports[0].periods == (13, 18)
    assert certificate.exact_discrete.prefix_collision_reports[1].lcm_collision_gap == 18
    assert "No real-valued RoPE" in certificate.claim_boundary
    summary = "\n".join(phase_bank_certificate_summary_lines(certificate))
    assert "Integer phase-bank position distinguishability certificate" in summary
    assert "first_exact_pass_prefix_length=3" in summary
    assert "smallest_pass_subfamily_size=2" in summary


def test_exact_phase_bank_diagnostic_presets_cover_quantized_and_scaled_boundaries() -> None:
    assert scale_phase_bank_periods((15, 16), 4) == (60, 64)

    shared = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["quantized_shared_factor_256"],
    )
    assert not shared.exact_discrete.pass_exact
    assert shared.exact_discrete.discretized_periods == (32, 48, 96)
    assert shared.exact_discrete.common_collision_gap == 96
    assert shared.exact_discrete.total_bank_collision_pair_count == 224

    boundary_fail = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["quantized_lcm_boundary_fail_241"],
    )
    assert not boundary_fail.exact_discrete.pass_exact
    assert boundary_fail.exact_discrete.common_collision_gap == 240
    assert boundary_fail.exact_discrete.guaranteed_common_gap_collision_pair_count == 1
    assert boundary_fail.exact_discrete.total_bank_collision_pair_count == 1
    assert boundary_fail.exact_discrete.sample_collision_pairs == ((0, 240),)

    scaled_pass = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["interpolated_x4_boundary_pass_960"],
    )
    assert scaled_pass.exact_discrete.pass_exact
    assert scaled_pass.exact_discrete.discretized_periods == (60, 64)
    assert scaled_pass.exact_discrete.common_collision_gap is None

    scaled_fail = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["interpolated_x4_boundary_fail_961"],
    )
    assert not scaled_fail.exact_discrete.pass_exact
    assert scaled_fail.exact_discrete.common_collision_gap == 960
    assert scaled_fail.exact_discrete.total_bank_collision_pair_count == 1
    assert scaled_fail.exact_discrete.sample_collision_pairs == ((0, 960),)


def test_phase_bank_certify_cli_emits_json_certificate() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/phase_bank_certify.py",
            "--periods",
            "6,18,54",
            "--context",
            "64",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema_id"] == "circle_calculus.integer_phase_bank_distinguishability.v0"
    assert payload["config"]["periods"] == [6, 18, 54]
    assert payload["exact_discrete"]["pass_exact"] is False
    assert payload["exact_discrete"]["common_collision_gap"] == 54
    assert payload["exact_discrete"]["total_bank_collision_pair_count"] == 10
    assert payload["exact_discrete"]["smallest_pass_subfamily_size"] is None
    assert "real_phase_margin" not in payload

    preset_result = subprocess.run(
        [
            sys.executable,
            "scripts/phase_bank_certify.py",
            "--preset",
            "interpolated_x4_boundary_fail_961",
            "--format",
            "json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    preset_payload = json.loads(preset_result.stdout)
    assert preset_payload["config"]["periods"] == [60, 64]
    assert preset_payload["config"]["context_length"] == 961
    assert preset_payload["exact_discrete"]["common_collision_gap"] == 960
    assert preset_payload["exact_discrete"]["total_bank_collision_pair_count"] == 1


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
    assert payload["rational_margin_certificate"]["name"] == ROPE_RATIONAL_PRESET_4099_NAME
    assert payload["rational_margin_certificate"]["pass_certificate"] is True
    assert payload["standard_interval_certificate"]["name"] == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME
    assert payload["standard_interval_certificate"]["pass_certificate"] is True
    assert payload["standard_interval_candidate_plans"][0]["context_length"] == 333
    assert payload["standard_interval_candidate_plans"][0]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089"
    )
    assert payload["standard_interval_candidate_plans"][1]["context_length"] == 710
    assert payload["standard_interval_candidate_plans"][1]["band_count"] == 113
    assert payload["presets"][0]["preset"] == "llama_style_10000_4k"
    assert payload["presets"][0]["certificate"]["exact_discrete_summary"]["pass_exact"] is True
    assert "lean_declarations" not in payload["presets"][0]["certificate"]
    assert "assumptions" not in payload["presets"][0]["certificate"]["exact_discrete_summary"]
    assert payload["phase_bank_diagnostics"][0]["preset"] == "quantized_shared_factor_256"
    assert (
        payload["phase_bank_diagnostics"][0]["certificate"]["exact_discrete_summary"][
            "common_collision_gap"
        ]
        == 96
    )
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
    assert "Named Rational Margin Certificate" in markdown_result.stdout
    assert "Named Standard RoPE Interval Seed" in markdown_result.stdout
    assert "Standard RoPE Candidate Interval Plans" in markdown_result.stdout
    assert "candidate_plan_not_lean_proved" in markdown_result.stdout
    assert "Exact Phase-Bank Diagnostics" in markdown_result.stdout
    assert ROPE_RATIONAL_PRESET_4099_NAME in markdown_result.stdout
    assert ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME in markdown_result.stdout
    assert "quantized_shared_factor_256" in markdown_result.stdout
    assert "interpolated_x4_boundary_fail_961" in markdown_result.stdout
    assert "Total bank pairs" in markdown_result.stdout
    assert "First pass prefix" in markdown_result.stdout
    assert "Smallest pass subfamily" in markdown_result.stdout
    assert "Reproduce with:" in markdown_result.stdout


def test_committed_rope_preset_results_match_generator(tmp_path: Path) -> None:
    generated_json = tmp_path / "rope_certifier_presets.json"
    generated_markdown = tmp_path / "rope_certifier_presets.md"
    subprocess.run(
        [
            sys.executable,
            "sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py",
            "--json-out",
            str(generated_json),
            "--markdown-out",
            str(generated_markdown),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    committed_json = Path(
        "sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json"
    )
    committed_markdown = Path(
        "sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md"
    )
    assert json.loads(committed_json.read_text()) == json.loads(generated_json.read_text())
    assert committed_markdown.read_text() == generated_markdown.read_text()
