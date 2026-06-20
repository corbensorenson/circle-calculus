from __future__ import annotations

import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from circle_math.applications import (
    ROPE_CERTIFIER_THEOREMS,
    ROPE_NAT_RATIO_COPRIME_FULL_DENOMINATOR_EXACT_MARGIN_THEOREMS,
    ROPE_NAT_RATIO_MODULAR_INVERSE_EXACT_MARGIN_THEOREMS,
    ROPE_ONE_OVER_NAT_EXACT_MARGIN_THEOREMS,
    ROPE_RATIONAL_PRESET_4099_NAME,
    ROPE_RATIONAL_PRESET_4099_THEOREMS,
    ROPE_REAL_PHASE_PRECURSOR_THEOREMS,
    ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS,
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
    certify_standard_channel0_d12_bank_request,
    certify_standard_channel0_d12_margin_bracket,
    certify_standard_channel0_d13_bank_request,
    certify_standard_channel0_d13_margin_bracket,
    certify_standard_channel0_d14_bank_request,
    certify_standard_channel0_d14_margin_bracket,
    certify_standard_channel0_d16_bank_request,
    certify_standard_channel0_d16_margin_bracket,
    certify_standard_channel0_d17_bank_request,
    certify_standard_channel0_d17_margin_bracket,
    certify_standard_channel0_d18_bank_request,
    certify_standard_channel0_d18_margin_bracket,
    certify_standard_channel0_d19_bank_request,
    certify_standard_channel0_d19_margin_bracket,
    certify_standard_channel0_d19_range_request_margin_bracket,
    audit_standard_channel0_rational_band_certificate,
    collision_pair_count_at_gap,
    collision_pair_count_fitting_multiple_count,
    collision_pair_count_at_gap_multiples_closed_form,
    collision_pair_count_at_gap_multiples_closed_form_numerator,
    collision_pair_count_at_gap_multiples_fitting_range,
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
    single_gap_boundary_collision_pair_count,
    single_period_collision_pair_count,
    standard_channel0_turn_ratio_bounds,
    turn_ratio_exact_context_nearest_margin,
    turn_ratio_exact_floor_ceil_witness_errors,
    turn_ratio_exact_floor_ceil_witness_margin,
    turn_ratio_finite_margin_gap_candidates,
    turn_ratio_floor_ceil_witness_errors,
    turn_ratio_floor_ceil_witness_margin,
    turn_ratio_floor_ceil_witnesses_certify_margin,
    turn_ratio_margin_covers_context,
    turn_ratio_margin_covers_margin,
    turn_ratio_margin_covers_request,
    turn_ratio_nat_ratio_coprime_margin_certificate,
    turn_ratio_nat_ratio_modular_inverse_margin_witness,
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
    assert collision_pair_count_at_gap_multiples_closed_form(20, 6) == 24
    assert collision_pair_count_at_gap_multiples_closed_form(6, 6) == 0
    assert collision_pair_count_at_gap_multiples_closed_form_numerator(20, 6) == 48
    assert collision_pair_count_at_gap_multiples_closed_form_numerator(6, 6) == 0
    assert collision_pair_count_at_gap_multiples_fitting_range(20, 6) == 24
    assert collision_pair_count_at_gap_multiples_fitting_range(6, 6) == 0
    assert collision_pair_count_fitting_multiple_count(20, 6) == 3
    assert collision_pair_count_fitting_multiple_count(6, 6) == 0
    assert collision_pair_count_fitting_multiple_count(6, 0) == 0
    assert single_gap_boundary_collision_pair_count(13, 7) == 6
    assert single_gap_boundary_collision_pair_count(15, 7) is None
    assert single_gap_boundary_collision_pair_count(7, 7) is None
    assert single_period_collision_pair_count(20, 6) == 24
    assert collision_pair_count_at_gap(10, 10) == 0
    assert sample_collision_pairs(10, 4, limit=3) == ((0, 4), (1, 5), (2, 6))
    reports = phase_bank_prefix_collision_reports(20, (6, 35), limit=2)
    assert tuple(report.prefix_length for report in reports) == (1, 2)
    assert reports[0].lcm_collision_gap == 6
    assert reports[0].fitting_collision_multiple_count == 3
    assert reports[0].collision_pair_count_closed_form_numerator == 48
    assert reports[0].total_bank_collision_pair_count == 24
    assert reports[1].lcm_reaches_context
    assert reports[1].fitting_collision_multiple_count == 0
    assert reports[1].collision_pair_count_closed_form_numerator == 0
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
    assert "AIRA-T0203" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0204" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0205" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0206" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0207" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0210" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0211" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0212" in ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0213" in ROPE_CERTIFIER_THEOREMS


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
    assert "AIRA-T0178" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0181" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0196" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0197" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0216" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0217" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0220" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0221" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0233" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0234" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0235" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0236" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0237" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0232" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


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
    exact_floor_error, exact_ceil_error = turn_ratio_exact_floor_ceil_witness_errors(
        turn_ratio=Fraction(3, 7),
        gap=2,
    )
    assert exact_floor_error == Fraction(6, 7)
    assert exact_ceil_error == Fraction(1, 7)
    assert turn_ratio_exact_floor_ceil_witness_margin(
        turn_ratio=Fraction(3, 7),
        gap=2,
    ) == Fraction(1, 7)
    assert turn_ratio_exact_context_nearest_margin(
        turn_ratio=Fraction(3, 7),
        context_length=7,
    ) == (Fraction(1, 7), 2)
    assert turn_ratio_exact_context_nearest_margin(
        turn_ratio=Fraction(3, 7),
        context_length=8,
    ) == (Fraction(0, 1), 7)

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
    assert "AIRA-T0182" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0183" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_real_phase_band_witness_bridge_is_listed() -> None:
    assert "AIRA-T0126" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


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
    assert "AIRA-T0222" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0223" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0224" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0225" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0226" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0227" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0228" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0229" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0230" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    assert "AIRA-T0231" in ROPE_REAL_PHASE_PRECURSOR_THEOREMS


def test_one_over_denominator_rational_certificate_uses_generic_exact_margin_theorem() -> None:
    certificate = certify_rational_turn_ratio_finite_margin(
        numerator=1,
        denominator=101,
        context_length=100,
    )
    assert certificate.pass_certificate
    assert certificate.certified_margin == 1.0 / 101.0
    assert certificate.exact_nearest_gap_margin == "1/101"
    assert certificate.exact_nearest_gap == 1
    assert ROPE_ONE_OVER_NAT_EXACT_MARGIN_THEOREMS == ("AIRA-T0222", "AIRA-T0223")
    assert "AIRA-T0222" in certificate.theorem_ids
    assert "AIRA-T0223" in certificate.theorem_ids
    assert "AIRA-T0230" in certificate.theorem_ids
    assert "AIRA-T0231" in certificate.theorem_ids
    assert (
        "Circle.Applications.ropeTurnRatioOneOverNat_gapOneNearestIntegerMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioOneOverNat_exactWeakestGapMargin_report"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioExactWeakestGapMargin_request_iff"
        in certificate.lean_declarations
    )
    scanned_margin, gap, turns = scan_turn_ratio_finite_margin(
        turn_ratio=certificate.turn_ratio,
        context_length=certificate.context_length,
    )
    assert abs(scanned_margin - certificate.certified_margin) < 1e-12
    assert gap == 1
    assert turns == 0


def test_coprime_rational_certificate_uses_modular_inverse_exact_margin_theorem() -> None:
    assert turn_ratio_nat_ratio_modular_inverse_margin_witness(
        numerator=3,
        denominator=7,
        gap=2,
    ) == (1, "minus_one")
    assert turn_ratio_nat_ratio_modular_inverse_margin_witness(
        numerator=3,
        denominator=7,
        gap=5,
    ) == (2, "plus_one")
    assert turn_ratio_nat_ratio_modular_inverse_margin_witness(
        numerator=3,
        denominator=7,
        gap=1,
    ) is None

    certificate = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=7,
    )
    assert certificate.pass_certificate
    assert certificate.certified_margin == 1.0 / 7.0
    assert certificate.exact_nearest_gap_margin == "1/7"
    assert certificate.exact_nearest_gap in {2, 5}
    assert ROPE_NAT_RATIO_MODULAR_INVERSE_EXACT_MARGIN_THEOREMS == (
        "AIRA-T0224",
        "AIRA-T0225",
        "AIRA-T0226",
    )
    assert "AIRA-T0224" in certificate.theorem_ids
    assert "AIRA-T0225" in certificate.theorem_ids
    assert "AIRA-T0226" in certificate.theorem_ids
    assert "AIRA-T0230" in certificate.theorem_ids
    assert "AIRA-T0231" in certificate.theorem_ids
    assert (
        "Circle.Applications.ropeTurnRatioGapNearestIntegerMargin_le_error"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioError_natRatio_eq_one_over_den_of_modular_inverse_witness"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioNatRatio_exactWeakestGapMargin_report_of_modular_inverse_witness"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeTurnRatioFiniteMargin_of_exactWeakestGapMargin_lt_request"
        in certificate.lean_declarations
    )


def test_coprime_rational_full_denominator_context_reports_existential_exact_margin_theorem() -> None:
    certificate = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=7,
    )
    assert certificate.pass_certificate
    assert certificate.exact_nearest_gap_margin == "1/7"
    assert certificate.exact_nearest_gap in {2, 5}
    assert ROPE_NAT_RATIO_COPRIME_FULL_DENOMINATOR_EXACT_MARGIN_THEOREMS == (
        "AIRA-T0227",
        "AIRA-T0228",
        "AIRA-T0229",
    )
    assert "AIRA-T0227" in certificate.theorem_ids
    assert "AIRA-T0228" in certificate.theorem_ids
    assert "AIRA-T0229" in certificate.theorem_ids
    assert "AIRA-T0230" in certificate.theorem_ids
    assert "AIRA-T0231" in certificate.theorem_ids
    assert (
        "Circle.Applications.ropeTurnRatioNatRatio_exists_exactWeakestGapMargin_report_of_coprime"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_full_denominator_iff_margin_le_one_over_den"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioNatRatio_full_denominator_obstruction_of_one_over_den_lt_margin"
        in certificate.lean_declarations
    )
    assert "exact threshold" in certificate.explanation
    assert certificate.exact_threshold_margin == "1/7"
    assert certificate.exact_threshold_witness_gap in {2, 5}
    assert certificate.exact_threshold_witness_turns in {1, 2}

    smaller_context_certificate = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=6,
    )
    assert smaller_context_certificate.pass_certificate
    assert "AIRA-T0226" in smaller_context_certificate.theorem_ids
    assert "AIRA-T0227" not in smaller_context_certificate.theorem_ids
    assert "AIRA-T0228" not in smaller_context_certificate.theorem_ids
    assert "AIRA-T0229" not in smaller_context_certificate.theorem_ids


def test_coprime_rational_full_denominator_requested_margin_uses_exact_threshold() -> None:
    passing = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=7,
        requested_margin=Fraction(1, 7),
    )
    assert passing.requested_margin == "1/7"
    assert passing.requested_margin_pass is True
    assert passing.requested_margin_status == "proved"
    assert passing.requested_margin_failure_reason is None
    assert passing.exact_threshold_margin == "1/7"
    assert passing.exact_threshold_witness_gap in {2, 5}
    assert passing.exact_threshold_witness_turns in {1, 2}
    assert "AIRA-T0229" in passing.theorem_ids

    failing = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=7,
        requested_margin=Fraction(1, 6),
    )
    assert failing.requested_margin == "1/6"
    assert failing.requested_margin_pass is False
    assert failing.requested_margin_status == "impossible"
    assert (
        failing.requested_margin_failure_reason
        == "requested_margin_exceeds_exact_full_denominator_threshold"
    )
    assert failing.exact_threshold_margin == "1/7"
    assert failing.exact_threshold_witness_gap in {2, 5}
    assert failing.exact_threshold_witness_turns in {1, 2}
    assert "AIRA-T0229" in failing.theorem_ids

    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_rational_turn_ratio_finite_margin(
            numerator=3,
            denominator=7,
            context_length=7,
            requested_margin=Fraction(-1, 7),
        )


def test_coprime_rational_requested_margin_status_distinguishes_unproved_and_zero_gap() -> None:
    conservative_lower_bound = certify_rational_turn_ratio_finite_margin(
        numerator=2,
        denominator=9,
        context_length=2,
        requested_margin=Fraction(1, 5),
    )
    assert conservative_lower_bound.pass_certificate
    assert conservative_lower_bound.requested_margin_pass is False
    assert (
        conservative_lower_bound.requested_margin_status
        == "unproved_above_certified_lower_bound"
    )
    assert (
        conservative_lower_bound.requested_margin_failure_reason
        == "requested_margin_exceeds_certified_rational_margin"
    )

    zero_gap = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=8,
        requested_margin=Fraction(1, 100),
    )
    assert zero_gap.pass_certificate is False
    assert zero_gap.zero_margin_witness == (7, 3)
    assert zero_gap.requested_margin_pass is False
    assert zero_gap.requested_margin_status == "impossible"
    assert (
        zero_gap.requested_margin_failure_reason
        == "positive_requested_margin_hits_exact_zero_gap"
    )


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
    assert certificate.exact_nearest_gap_margin == "1/4099"
    assert certificate.exact_nearest_gap == 1
    assert certificate.theorem_ids == ROPE_RATIONAL_PRESET_4099_THEOREMS
    assert "AIRA-T0182" in certificate.theorem_ids
    assert "AIRA-T0183" in certificate.theorem_ids
    assert "AIRA-T0214" in certificate.theorem_ids
    assert "AIRA-T0230" in certificate.theorem_ids
    assert "AIRA-T0231" in certificate.theorem_ids
    assert "AIRA-T0060" in certificate.theorem_ids
    assert "AIRA-T0177" in certificate.theorem_ids
    assert "AIRA-T0186" in certificate.theorem_ids
    assert "AIRA-T0061" in certificate.theorem_ids
    assert "AIRA-T0185" in certificate.theorem_ids
    assert "AIRA-T0215" in certificate.theorem_ids
    assert "AIRA-T0222" in certificate.theorem_ids
    assert "AIRA-T0223" in certificate.theorem_ids
    assert "AIRA-T0187" in certificate.theorem_ids
    assert "AIRA-T0196" in certificate.theorem_ids
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
    assert certificate.context_length == 196608
    assert certificate.certified_margin == "1/328459"
    assert certificate.pass_certificate
    assert "3.14159265358979323846 < pi" in certificate.pi_bounds
    assert "pi < 3.14159265358979323847" in certificate.pi_bounds
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
    assert "AIRA-T0090" in certificate.theorem_ids
    assert "AIRA-T0091" in certificate.theorem_ids
    assert "AIRA-T0092" in certificate.theorem_ids
    assert "AIRA-T0093" in certificate.theorem_ids
    assert "AIRA-T0094" in certificate.theorem_ids
    assert "AIRA-T0095" in certificate.theorem_ids
    assert "AIRA-T0096" in certificate.theorem_ids
    assert "AIRA-T0097" in certificate.theorem_ids
    assert "AIRA-T0098" in certificate.theorem_ids
    assert "AIRA-T0099" in certificate.theorem_ids
    assert "AIRA-T0100" in certificate.theorem_ids
    assert "AIRA-T0101" in certificate.theorem_ids
    assert "AIRA-T0102" in certificate.theorem_ids
    assert "AIRA-T0103" in certificate.theorem_ids
    assert "AIRA-T0104" in certificate.theorem_ids
    assert "AIRA-T0105" in certificate.theorem_ids
    assert "AIRA-T0106" in certificate.theorem_ids
    assert "AIRA-T0107" in certificate.theorem_ids
    assert "AIRA-T0108" in certificate.theorem_ids
    assert "AIRA-T0109" in certificate.theorem_ids
    assert "AIRA-T0110" in certificate.theorem_ids
    assert "AIRA-T0111" in certificate.theorem_ids
    assert "AIRA-T0112" in certificate.theorem_ids
    assert "AIRA-T0113" in certificate.theorem_ids
    assert "AIRA-T0114" in certificate.theorem_ids
    assert "AIRA-T0115" in certificate.theorem_ids
    assert "AIRA-T0116" in certificate.theorem_ids
    assert "AIRA-T0117" in certificate.theorem_ids
    assert "AIRA-T0118" in certificate.theorem_ids
    assert "AIRA-T0119" in certificate.theorem_ids
    assert "AIRA-T0120" in certificate.theorem_ids
    assert "AIRA-T0121" in certificate.theorem_ids
    assert "AIRA-T0122" in certificate.theorem_ids
    assert "AIRA-T0123" in certificate.theorem_ids
    assert "AIRA-T0124" in certificate.theorem_ids
    assert "AIRA-T0125" in certificate.theorem_ids
    assert "AIRA-T0126" in certificate.theorem_ids
    assert "AIRA-T0127" in certificate.theorem_ids
    assert "AIRA-T0128" in certificate.theorem_ids
    assert "AIRA-T0129" in certificate.theorem_ids
    assert "AIRA-T0130" in certificate.theorem_ids
    assert "AIRA-T0131" in certificate.theorem_ids
    assert "AIRA-T0132" in certificate.theorem_ids
    assert "AIRA-T0133" in certificate.theorem_ids
    assert "AIRA-T0134" in certificate.theorem_ids
    assert "AIRA-T0135" in certificate.theorem_ids
    assert "AIRA-T0136" in certificate.theorem_ids
    assert "AIRA-T0137" in certificate.theorem_ids
    assert "AIRA-T0138" in certificate.theorem_ids
    assert "AIRA-T0139" in certificate.theorem_ids
    assert "AIRA-T0140" in certificate.theorem_ids
    assert "AIRA-T0141" in certificate.theorem_ids
    for theorem_id in (
        "AIRA-T0142",
        "AIRA-T0143",
        "AIRA-T0144",
        "AIRA-T0145",
        "AIRA-T0146",
        "AIRA-T0147",
        "AIRA-T0148",
        "AIRA-T0149",
        "AIRA-T0150",
        "AIRA-T0151",
        "AIRA-T0152",
        "AIRA-T0153",
        "AIRA-T0154",
        "AIRA-T0155",
        "AIRA-T0156",
        "AIRA-T0157",
        "AIRA-T0158",
        "AIRA-T0159",
        "AIRA-T0160",
        "AIRA-T0161",
        "AIRA-T0162",
        "AIRA-T0163",
        "AIRA-T0164",
        "AIRA-T0165",
        "AIRA-T0166",
        "AIRA-T0167",
        "AIRA-T0168",
        "AIRA-T0169",
        "AIRA-T0170",
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0173",
    ):
        assert theorem_id in certificate.theorem_ids
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D9Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_65536"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0_margin_one_over_65536_of_context_gt_710"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D10Seed_intervalCertificate"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D10Seed_turnRatioFiniteMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0D10Seed_nearTurn"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D10Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104000"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0_margin_one_over_104000_of_context_gt_710"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D11Seed_intervalCertificate"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D11Seed_turnRatioFiniteMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0D11Seed_nearTurn"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104218"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0_margin_one_over_104218_of_context_gt_710"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed_cons"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D11_context4096_margin_bracket"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D12Seed_intervalCertificate"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D12Seed_turnRatioFiniteMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0D12Seed_nearTurn"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D12_context8192_margin_bracket"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeTurnRatioIntervalWitness_of_band_bounds"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D13Seed_intervalCertificate"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D13Seed_turnRatioFiniteMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0D13Seed_nearTurn"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D13_context8192_margin_bracket"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D14Seed_intervalCertificate"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D14Seed_turnRatioFiniteMargin"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeStandardChannel0D14Seed_nearTurn"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons"
        in certificate.lean_declarations
    )
    assert (
        "Circle.Applications.ropeStandardChannel0D14_context16384_margin_bracket"
        in certificate.lean_declarations
    )
    for declaration in (
        "Circle.Applications.ropeTurnRatioIntervalWitness_of_rationalIntervalBand",
        "Circle.Applications.ropeTurnRatioIntervalCertificate_of_rationalIntervalBands",
        "Circle.Applications.ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid",
        "Circle.Applications.ropeStandardChannel0D15Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D15Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0D15Seed_nearTurn",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D15Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D15Seed_cons",
        "Circle.Applications.ropeStandardChannel0D15_context32768_margin_bracket",
        "Circle.Applications.ropeStandardChannel0D16Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D16Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0D16Seed_nearTurn",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed_cons",
        "Circle.Applications.ropeStandardChannel0D16_context65536_margin_bracket",
        "Circle.Applications.ropeStandardChannel0_gap103993_error_lt_one_over_328458",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993",
        "Circle.Applications.ropeStandardChannel0D17Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D17Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0D17Seed_nearTurn",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed_cons",
        "Circle.Applications.ropeStandardChannel0D17_context131072_margin_bracket",
        "Circle.Applications.ropeStandardChannel0D18Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D18Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0D18Seed_nearTurn",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D18Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D18Seed_cons",
        "Circle.Applications.ropeStandardChannel0D18_context163840_margin_bracket",
        "Circle.Applications.ropeStandardChannel0D19Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D19Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0D19Seed_nearTurn",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed_cons",
        "Circle.Applications.ropeStandardChannel0D19_context196608_margin_bracket",
    ):
        assert declaration in certificate.lean_declarations
    assert "1/328459" in certificate.explanation
    assert "at or above 1/104218 is impossible" in certificate.explanation
    assert "1/328458 is impossible" in certificate.explanation
    assert "weaker D12 8k one-channel seed at margin 1/104220" in certificate.explanation
    assert "sharper D13 8k seed at margin 1/104219" in certificate.explanation
    assert "the D14 16k seed, and generated D15/D16" in certificate.explanation
    assert "D18 carries that same margin to the 160k context" in certificate.explanation
    assert "D19 carries it to the 192k context" in certificate.explanation
    assert "32k and 64k seeds at the same margin" in certificate.explanation
    assert "gaps 1 through 196607" in certificate.explanation
    assert tuple(witness.gap for witness in certificate.interval_witnesses) == tuple(
        range(1, 196608)
    )
    assert certificate.interval_witnesses[0].lower == (
        "50000000000000000000/314159265358979323847"
    )
    assert certificate.interval_witnesses[0].upper == (
        "25000000000000000000/157079632679489661923"
    )
    assert certificate.interval_witnesses[-1].gap == 196607
    assert certificate.interval_witnesses[-1].cell == 31290
    d6_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d6",
        margin=Fraction(1, 1024),
        max_context_length=4096,
    )
    assert d6_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094"
    d20_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 131072),
        max_context_length=4096,
    )
    assert d20_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0097_to_AIRA-T0101"
    d20_tight_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 105000),
        max_context_length=4096,
    )
    assert d20_tight_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0105_to_AIRA-T0108"
    assert d20_tight_plan.planned_margin == "1/105000"
    d20_sharp_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=4096,
    )
    assert d20_sharp_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114"
    assert d20_sharp_plan.planned_margin == "1/104219"
    d20_8k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104220),
        max_context_length=8192,
    )
    assert d20_8k_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122"
    assert d20_8k_plan.context_length == 8192
    assert d20_8k_plan.first_uncovered_gap is None
    assert d20_8k_plan.planned_margin == "1/104220"
    assert d20_8k_plan.band_count == 1304
    assert d20_8k_plan.bands[-1].start_gap == 8187
    assert d20_8k_plan.bands[-1].end_gap == 8191
    assert d20_8k_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_8k_plan.bands)
    d20_8k_sharp_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=8192,
    )
    assert d20_8k_sharp_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129"
    assert d20_8k_sharp_plan.context_length == 8192
    assert d20_8k_sharp_plan.first_uncovered_gap is None
    assert d20_8k_sharp_plan.planned_margin == "1/104219"
    assert d20_8k_sharp_plan.band_count == 1304
    assert d20_8k_sharp_plan.bands[-1].start_gap == 8187
    assert d20_8k_sharp_plan.bands[-1].end_gap == 8191
    assert d20_8k_sharp_plan.bands[-1].cell == 1303
    assert d20_8k_sharp_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_8k_sharp_plan.bands)
    d20_16k_sharp_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=16384,
    )
    assert d20_16k_sharp_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135"
    assert d20_16k_sharp_plan.context_length == 16384
    assert d20_16k_sharp_plan.first_uncovered_gap is None
    assert d20_16k_sharp_plan.planned_margin == "1/104219"
    assert d20_16k_sharp_plan.band_count == 2608
    assert d20_16k_sharp_plan.bands[-1].start_gap == 16381
    assert d20_16k_sharp_plan.bands[-1].end_gap == 16383
    assert d20_16k_sharp_plan.bands[-1].cell == 2607
    assert d20_16k_sharp_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_16k_sharp_plan.bands)
    d20_32k_sharp_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=32768,
    )
    assert d20_32k_sharp_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144"
    assert d20_32k_sharp_plan.context_length == 32768
    assert d20_32k_sharp_plan.first_uncovered_gap is None
    assert d20_32k_sharp_plan.planned_margin == "1/104219"
    assert d20_32k_sharp_plan.band_count == 5216
    assert d20_32k_sharp_plan.bands[-1].start_gap == 32767
    assert d20_32k_sharp_plan.bands[-1].end_gap == 32767
    assert d20_32k_sharp_plan.bands[-1].cell == 5215
    assert d20_32k_sharp_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_32k_sharp_plan.bands)
    d20_64k_sharp_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=65536,
    )
    assert d20_64k_sharp_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150"
    assert d20_64k_sharp_plan.context_length == 65536
    assert d20_64k_sharp_plan.first_uncovered_gap is None
    assert d20_64k_sharp_plan.planned_margin == "1/104219"
    assert d20_64k_sharp_plan.band_count == 10431
    assert d20_64k_sharp_plan.bands[-1].start_gap == 65534
    assert d20_64k_sharp_plan.bands[-1].end_gap == 65535
    assert d20_64k_sharp_plan.bands[-1].cell == 10430
    assert d20_64k_sharp_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_64k_sharp_plan.bands)
    d20_128k_d17_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=131072,
    )
    assert d20_128k_d17_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158"
    assert d20_128k_d17_plan.context_length == 131072
    assert d20_128k_d17_plan.first_uncovered_gap is None
    assert d20_128k_d17_plan.planned_margin == "1/328459"
    assert d20_128k_d17_plan.band_count == 20861
    assert d20_128k_d17_plan.bands[-1].start_gap == 131068
    assert d20_128k_d17_plan.bands[-1].end_gap == 131071
    assert d20_128k_d17_plan.bands[-1].cell == 20860
    assert d20_128k_d17_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_128k_d17_plan.bands)
    d20_160k_d18_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=163840,
    )
    assert d20_160k_d18_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0162_to_AIRA-T0164"
    assert d20_160k_d18_plan.context_length == 163840
    assert d20_160k_d18_plan.first_uncovered_gap is None
    assert d20_160k_d18_plan.planned_margin == "1/328459"
    assert d20_160k_d18_plan.band_count == 26076
    assert d20_160k_d18_plan.bands[-1].start_gap == 163835
    assert d20_160k_d18_plan.bands[-1].end_gap == 163839
    assert d20_160k_d18_plan.bands[-1].cell == 26075
    assert d20_160k_d18_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_160k_d18_plan.bands)
    d20_192k_d19_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=196608,
    )
    assert d20_192k_d19_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170"
    assert d20_192k_d19_plan.context_length == 196608
    assert d20_192k_d19_plan.first_uncovered_gap is None
    assert d20_192k_d19_plan.planned_margin == "1/328459"
    assert d20_192k_d19_plan.band_count == 31291
    assert d20_192k_d19_plan.bands[-1].start_gap == 196601
    assert d20_192k_d19_plan.bands[-1].end_gap == 196607
    assert d20_192k_d19_plan.bands[-1].cell == 31290
    assert d20_192k_d19_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_192k_d19_plan.bands)
    d20_8k_too_large_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104218),
        max_context_length=8192,
    )
    assert d20_8k_too_large_plan.context_length == 710
    assert d20_8k_too_large_plan.first_uncovered_gap == 710
    assert d20_8k_too_large_plan.theorem_status == "candidate_plan_not_lean_proved"
    assert d20_plan.context_length == 4096
    assert d20_plan.first_uncovered_gap is None
    assert d20_plan.band_count == 652
    assert d20_plan.bands[0].start_gap == d6_plan.bands[0].start_gap
    assert d20_plan.bands[0].end_gap == d6_plan.bands[0].end_gap
    assert d20_plan.bands[0].cell == d6_plan.bands[0].cell
    assert d20_plan.bands[-1].start_gap == 4091
    assert d20_plan.bands[-1].end_gap == 4095
    assert d20_plan.bands[-1].cell == 651
    assert d20_tight_plan.bands == d20_plan.bands
    assert d20_sharp_plan.bands == d20_plan.bands
    for band in d20_sharp_plan.bands:
        assert all(
            witness.cell == band.cell
            for witness in certificate.interval_witnesses[
                band.start_gap - 1 : band.end_gap
            ]
        )
    assert "gap 710" in certificate.explanation
    assert "1/1024 margin stops" in certificate.explanation
    assert "1/104000" in certificate.explanation
    assert "1/104218" in certificate.explanation
    scanned_margin, scanned_gap, scanned_turns = scan_turn_ratio_finite_margin(
        turn_ratio=1 / (2 * math.pi),
        context_length=711,
    )
    assert scanned_gap == 710
    assert scanned_turns == 113
    assert scanned_margin < 1 / 1024
    assert scanned_margin < 1 / 104000
    assert scanned_margin < 1 / 104218
    scanned_128k_margin, scanned_128k_gap, scanned_128k_turns = scan_turn_ratio_finite_margin(
        turn_ratio=1 / (2 * math.pi),
        context_length=103994,
    )
    assert scanned_128k_gap == 103993
    assert scanned_128k_turns == 16551
    assert scanned_128k_margin < 1 / 328458
    assert "over context 196608" in certificate.claim_boundary
    assert "one-separating-channel bank bridges" in certificate.claim_boundary
    assert "not a proof that every standard RoPE channel" in certificate.claim_boundary


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
    assert d4_plan.bands[0].start_lower_value == "625/3927"
    assert d4_plan.bands[0].end_upper_value == "6000/6283"
    assert d4_plan.bands[0].endpoint_cell_margin_ok
    assert d4_plan.bands[0].bridge_theorem_id == "AIRA-T0126"
    assert d4_plan.bands[-1].start_gap == 327
    assert d4_plan.bands[-1].end_gap == 332
    assert d4_plan.bands[-1].cell == 52
    assert all(band.endpoint_cell_margin_ok for band in d4_plan.bands)
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
    assert d6_plan.bands[0].start_gap == d4_plan.bands[0].start_gap
    assert d6_plan.bands[0].end_gap == d4_plan.bands[0].end_gap
    assert d6_plan.bands[0].cell == d4_plan.bands[0].cell
    assert d6_plan.bands[-1].start_gap == 704
    assert d6_plan.bands[-1].end_gap == 709
    assert d6_plan.bands[-1].cell == 112
    assert all(band.bridge_theorem_id == "AIRA-T0126" for band in d6_plan.bands)
    assert all(band.endpoint_cell_margin_ok for band in d6_plan.bands)
    assert d6_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094"

    d20_lower, d20_upper, d20_label = standard_channel0_turn_ratio_bounds(
        pi_bound_preset="d20"
    )
    assert d20_lower == Fraction(50_000_000_000_000_000_000, 314_159_265_358_979_323_847)
    assert d20_upper == Fraction(25_000_000_000_000_000_000, 157_079_632_679_489_661_923)
    assert "3.14159265358979323846 < pi" in d20_label

    d20_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=4096,
    )
    assert d20_plan.context_length == 4096
    assert d20_plan.first_uncovered_gap is None
    assert d20_plan.planned_margin == "1/104219"
    assert d20_plan.band_count == 652
    assert d20_plan.bands[0].start_gap == d4_plan.bands[0].start_gap
    assert d20_plan.bands[0].end_gap == d4_plan.bands[0].end_gap
    assert d20_plan.bands[0].cell == d4_plan.bands[0].cell
    assert d20_plan.bands[-1].start_gap == 4091
    assert d20_plan.bands[-1].end_gap == 4095
    assert d20_plan.bands[-1].cell == 651
    assert d20_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_plan.bands)
    assert d20_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114"

    d20_8k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=8192,
    )
    assert d20_8k_plan.context_length == 8192
    assert d20_8k_plan.first_uncovered_gap is None
    assert d20_8k_plan.planned_margin == "1/104219"
    assert d20_8k_plan.band_count == 1304
    assert d20_8k_plan.bands[-1].start_gap == 8187
    assert d20_8k_plan.bands[-1].end_gap == 8191
    assert d20_8k_plan.bands[-1].cell == 1303
    assert d20_8k_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_8k_plan.bands)
    assert d20_8k_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129"

    d20_16k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=16384,
    )
    assert d20_16k_plan.context_length == 16384
    assert d20_16k_plan.first_uncovered_gap is None
    assert d20_16k_plan.planned_margin == "1/104219"
    assert d20_16k_plan.band_count == 2608
    assert d20_16k_plan.bands[-1].start_gap == 16381
    assert d20_16k_plan.bands[-1].end_gap == 16383
    assert d20_16k_plan.bands[-1].cell == 2607
    assert d20_16k_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_16k_plan.bands)
    assert d20_16k_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135"

    d20_32k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=32768,
    )
    assert d20_32k_plan.context_length == 32768
    assert d20_32k_plan.first_uncovered_gap is None
    assert d20_32k_plan.planned_margin == "1/104219"
    assert d20_32k_plan.band_count == 5216
    assert d20_32k_plan.bands[-1].start_gap == 32767
    assert d20_32k_plan.bands[-1].end_gap == 32767
    assert d20_32k_plan.bands[-1].cell == 5215
    assert d20_32k_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_32k_plan.bands)
    assert d20_32k_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144"

    d20_64k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=65536,
    )
    assert d20_64k_plan.context_length == 65536
    assert d20_64k_plan.first_uncovered_gap is None
    assert d20_64k_plan.planned_margin == "1/104219"
    assert d20_64k_plan.band_count == 10431
    assert d20_64k_plan.bands[-1].start_gap == 65534
    assert d20_64k_plan.bands[-1].end_gap == 65535
    assert d20_64k_plan.bands[-1].cell == 10430
    assert d20_64k_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_64k_plan.bands)
    assert d20_64k_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150"

    d20_128k_d17_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=131072,
    )
    assert d20_128k_d17_plan.context_length == 131072
    assert d20_128k_d17_plan.first_uncovered_gap is None
    assert d20_128k_d17_plan.planned_margin == "1/328459"
    assert d20_128k_d17_plan.band_count == 20861
    assert d20_128k_d17_plan.bands[-1].start_gap == 131068
    assert d20_128k_d17_plan.bands[-1].end_gap == 131071
    assert d20_128k_d17_plan.bands[-1].cell == 20860
    assert d20_128k_d17_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_128k_d17_plan.bands)
    assert d20_128k_d17_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158"

    d20_160k_d18_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=163840,
    )
    assert d20_160k_d18_plan.context_length == 163840
    assert d20_160k_d18_plan.first_uncovered_gap is None
    assert d20_160k_d18_plan.planned_margin == "1/328459"
    assert d20_160k_d18_plan.band_count == 26076
    assert d20_160k_d18_plan.bands[-1].start_gap == 163835
    assert d20_160k_d18_plan.bands[-1].end_gap == 163839
    assert d20_160k_d18_plan.bands[-1].cell == 26075
    assert d20_160k_d18_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_160k_d18_plan.bands)
    assert d20_160k_d18_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0162_to_AIRA-T0164"

    d20_192k_d19_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=196608,
    )
    assert d20_192k_d19_plan.context_length == 196608
    assert d20_192k_d19_plan.first_uncovered_gap is None
    assert d20_192k_d19_plan.planned_margin == "1/328459"
    assert d20_192k_d19_plan.band_count == 31291
    assert d20_192k_d19_plan.bands[-1].start_gap == 196601
    assert d20_192k_d19_plan.bands[-1].end_gap == 196607
    assert d20_192k_d19_plan.bands[-1].cell == 31290
    assert d20_192k_d19_plan.bands[-1].bridge_theorem_id == "AIRA-T0126"
    assert all(band.endpoint_cell_margin_ok for band in d20_192k_d19_plan.bands)
    assert d20_192k_d19_plan.theorem_status == "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170"

    d20_too_large_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104218),
        max_context_length=4096,
    )
    assert d20_too_large_plan.context_length == 710
    assert d20_too_large_plan.first_uncovered_gap == 710
    assert d20_too_large_plan.theorem_status == "candidate_plan_not_lean_proved"


def test_standard_channel0_rational_band_audit_marks_frontier_candidates() -> None:
    d20_32k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=32768,
    )
    d20_32k_audit = audit_standard_channel0_rational_band_certificate(
        d20_32k_plan,
        requested_context_length=32768,
    )
    assert d20_32k_audit.schema_id == (
        "circle_calculus.standard_rope_rational_band_certificate_audit.v0"
    )
    assert d20_32k_audit.requested_context_length == 32768
    assert d20_32k_audit.certified_context_length == 32768
    assert d20_32k_audit.band_count == 5216
    assert d20_32k_audit.valid_band_count == 5216
    assert d20_32k_audit.covered_gap_count == 32767
    assert d20_32k_audit.first_covered_gap == 1
    assert d20_32k_audit.last_covered_gap == 32767
    assert d20_32k_audit.first_uncovered_gap is None
    assert d20_32k_audit.contiguous_from_one
    assert d20_32k_audit.endpoint_validity_pass
    assert d20_32k_audit.coverage_pass
    assert d20_32k_audit.pass_audit
    assert d20_32k_audit.theorem_ids == ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS
    assert d20_32k_audit.theorem_status == "executable_band_audit_not_lean_proved"
    assert "not a generated Lean certificate" in d20_32k_audit.claim_boundary

    d20_64k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=65536,
    )
    d20_64k_audit = audit_standard_channel0_rational_band_certificate(
        d20_64k_plan,
        requested_context_length=65536,
    )
    assert d20_64k_audit.requested_context_length == 65536
    assert d20_64k_audit.certified_context_length == 65536
    assert d20_64k_audit.band_count == 10431
    assert d20_64k_audit.valid_band_count == 10431
    assert d20_64k_audit.first_uncovered_gap is None
    assert d20_64k_audit.pass_audit

    d20_128k_d17_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 328459),
        max_context_length=131072,
    )
    d20_128k_d17_audit = audit_standard_channel0_rational_band_certificate(
        d20_128k_d17_plan,
        requested_context_length=131072,
    )
    assert d20_128k_d17_audit.requested_context_length == 131072
    assert d20_128k_d17_audit.certified_context_length == 131072
    assert d20_128k_d17_audit.band_count == 20861
    assert d20_128k_d17_audit.valid_band_count == 20861
    assert d20_128k_d17_audit.covered_gap_count == 131071
    assert d20_128k_d17_audit.first_uncovered_gap is None
    assert d20_128k_d17_audit.contiguous_from_one
    assert d20_128k_d17_audit.endpoint_validity_pass
    assert d20_128k_d17_audit.coverage_pass
    assert d20_128k_d17_audit.pass_audit

    d20_128k_plan = plan_standard_channel0_interval_bands(
        pi_bound_preset="d20",
        margin=Fraction(1, 104219),
        max_context_length=131072,
    )
    d20_128k_audit = audit_standard_channel0_rational_band_certificate(
        d20_128k_plan,
        requested_context_length=131072,
    )
    assert d20_128k_plan.context_length == 103993
    assert d20_128k_audit.requested_context_length == 131072
    assert d20_128k_audit.certified_context_length == 103993
    assert d20_128k_audit.band_count == 16551
    assert d20_128k_audit.valid_band_count == 16551
    assert d20_128k_audit.covered_gap_count == 103992
    assert d20_128k_audit.first_uncovered_gap == 103993
    assert d20_128k_audit.contiguous_from_one
    assert d20_128k_audit.endpoint_validity_pass
    assert not d20_128k_audit.coverage_pass
    assert not d20_128k_audit.pass_audit
    assert "first uncovered gap is 103993" in d20_128k_audit.explanation


def test_standard_channel0_d12_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d12_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d12_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d12_context8192_margin_bracket"
    assert bracket.context_length == 8192
    assert bracket.proved_margin == "1/104220"
    assert bracket.impossible_margin_floor == "1/104218"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0120", "AIRA-T0121", "AIRA-T0118", "AIRA-T0125")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D12Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D12Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
        "Circle.Applications.ropeStandardChannel0D12_context8192_margin_bracket",
    )
    assert "margin 1/104220 through context 8192" in bracket.explanation
    assert "gap 710" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d13_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d13_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d13_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d13_context8192_margin_bracket"
    assert bracket.context_length == 8192
    assert bracket.proved_margin == "1/104219"
    assert bracket.impossible_margin_floor == "1/104218"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0127", "AIRA-T0128", "AIRA-T0118", "AIRA-T0132")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D13Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D13Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
        "Circle.Applications.ropeStandardChannel0D13_context8192_margin_bracket",
    )
    assert "margin 1/104219 through context 8192" in bracket.explanation
    assert "gap 710" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d14_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d14_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d14_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d14_context16384_margin_bracket"
    assert bracket.context_length == 16384
    assert bracket.proved_margin == "1/104219"
    assert bracket.impossible_margin_floor == "1/104218"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0133", "AIRA-T0134", "AIRA-T0118", "AIRA-T0138")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D14Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D14Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
        "Circle.Applications.ropeStandardChannel0D14_context16384_margin_bracket",
    )
    assert "margin 1/104219 through context 16384" in bracket.explanation
    assert "gap 710" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d16_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d16_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d16_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d16_context65536_margin_bracket"
    assert bracket.context_length == 65536
    assert bracket.proved_margin == "1/104219"
    assert bracket.impossible_margin_floor == "1/104218"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0148", "AIRA-T0149", "AIRA-T0118", "AIRA-T0153")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D16Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D16Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
        "Circle.Applications.ropeStandardChannel0D16_context65536_margin_bracket",
    )
    assert "margin 1/104219 through context 65536" in bracket.explanation
    assert "gap 710" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d17_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d17_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d17_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d17_context131072_margin_bracket"
    assert bracket.context_length == 131072
    assert bracket.proved_margin == "1/328459"
    assert bracket.impossible_margin_floor == "1/328458"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0156", "AIRA-T0157", "AIRA-T0155", "AIRA-T0161")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D17Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D17Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993",
        "Circle.Applications.ropeStandardChannel0D17_context131072_margin_bracket",
    )
    assert "margin 1/328459 through context 131072" in bracket.explanation
    assert "gap 103993" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d18_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d18_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d18_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d18_context163840_margin_bracket"
    assert bracket.context_length == 163840
    assert bracket.proved_margin == "1/328459"
    assert bracket.impossible_margin_floor == "1/328458"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == ("AIRA-T0162", "AIRA-T0163", "AIRA-T0155", "AIRA-T0167")
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D18Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D18Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993",
        "Circle.Applications.ropeStandardChannel0D18_context163840_margin_bracket",
    )
    assert "margin 1/328459 through context 163840" in bracket.explanation
    assert "gap 103993" in bracket.explanation
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d19_margin_bracket_is_theorem_backed() -> None:
    bracket = certify_standard_channel0_d19_margin_bracket()
    assert bracket.schema_id == (
        "circle_calculus.standard_rope_channel0_d19_margin_bracket.v0"
    )
    assert bracket.name == "standard_rope_channel0_d19_context196608_margin_bracket"
    assert bracket.context_length == 196608
    assert bracket.context_range_min_exclusive == 103993
    assert bracket.context_range_max_inclusive == 196608
    assert bracket.proved_margin == "1/328459"
    assert bracket.impossible_margin_floor == "1/328458"
    assert bracket.pass_certificate
    assert bracket.theorem_ids == (
        "AIRA-T0168",
        "AIRA-T0169",
        "AIRA-T0155",
        "AIRA-T0173",
        "AIRA-T0209",
        "AIRA-T0208",
    )
    assert bracket.lean_declarations == (
        "Circle.Applications.ropeStandardChannel0D19Seed_intervalCertificate",
        "Circle.Applications.ropeStandardChannel0D19Seed_turnRatioFiniteMargin",
        "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993",
        "Circle.Applications.ropeStandardChannel0D19_context196608_margin_bracket",
        "Circle.Applications.ropeTurnRatioFiniteMargin_contextRange_bracket_of_obstruction",
        "Circle.Applications.ropeStandardChannel0D19_contextRange_margin_bracket",
    )
    assert "margin 1/328459 through context 196608" in bracket.explanation
    assert "gap 103993" in bracket.explanation
    assert "103993 < context <= 196608" in bracket.claim_boundary
    assert "not a full all-channel" in bracket.claim_boundary
    assert "does not decide margins strictly between" in bracket.claim_boundary


def test_standard_channel0_d19_range_request_bracket_classifies_proved_request() -> None:
    request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(1, 328459),
    )
    assert request.schema_id == (
        "circle_calculus.standard_rope_channel0_d19_range_request_bracket.v0"
    )
    assert request.name == "standard_rope_channel0_d19_range_request_margin_bracket"
    assert request.requested_context == 131072
    assert request.requested_margin == "1/328459"
    assert request.request_status == "proved"
    assert request.requested_margin_relation == "at_or_below_proved_threshold"
    assert request.undecided_margin_interval_lower_exclusive == "1/328459"
    assert request.undecided_margin_interval_upper_exclusive == "1/328458"
    assert request.undecided_margin_interval_width == "1/107884986222"
    assert request.theorem_backed_classification
    assert request.proved_margin_applies
    assert not request.impossible_margin_applies
    assert request.margin_thresholds_ordered
    assert request.proved_impossible_branches_disjoint
    assert not request.undecided_margin_open_gap
    assert request.margin_status_exhaustive
    assert request.in_range_semantic_trichotomy
    assert request.failure_reason is None
    assert request.theorem_ids == (
        "AIRA-T0216",
        "AIRA-T0217",
        "AIRA-T0218",
        "AIRA-T0219",
        "AIRA-T0220",
        "AIRA-T0221",
        "AIRA-T0233",
        "AIRA-T0232",
    )
    assert request.lean_declarations == (
        "Circle.Applications.ropeTurnRatioFiniteMargin_contextRange_request_bracket_of_obstruction",
        "Circle.Applications.ropeStandardChannel0D19_contextRange_request_margin_bracket",
        "Circle.Applications.ropeStandardChannel0D19_request_margin_thresholds_ordered",
        "Circle.Applications.ropeStandardChannel0D19_request_margin_branches_disjoint",
        "Circle.Applications.ropeStandardChannel0D19_request_margin_open_gap_iff_unclassified",
        "Circle.Applications.ropeStandardChannel0D19_request_margin_trichotomy",
        "Circle.Applications.ropeStandardChannel0D19_contextRange_request_margin_semantic_trichotomy",
        "Circle.Applications.ropeStandardChannel0D19_request_margin_open_gap_width",
    )
    assert "D19 obstruction range" in request.explanation
    assert "not a full all-channel" in request.claim_boundary
    assert "threshold branches are disjoint" in request.claim_boundary


def test_standard_channel0_d19_range_request_bracket_classifies_impossible_request() -> None:
    request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(1, 328458),
    )
    assert request.request_status == "impossible"
    assert request.requested_margin_relation == "at_or_above_impossible_floor"
    assert request.theorem_backed_classification
    assert not request.proved_margin_applies
    assert request.impossible_margin_applies
    assert request.margin_thresholds_ordered
    assert request.proved_impossible_branches_disjoint
    assert not request.undecided_margin_open_gap
    assert request.margin_status_exhaustive
    assert request.in_range_semantic_trichotomy
    assert request.failure_reason is None
    assert "obstruction gap 103993" in request.explanation


def test_standard_channel0_d19_range_request_bracket_reports_undecided_gap() -> None:
    middle_margin = (Fraction(1, 328459) + Fraction(1, 328458)) / 2
    request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=middle_margin,
    )
    assert Fraction(1, 328459) < middle_margin
    assert middle_margin < Fraction(1, 328458)
    assert request.request_status == "undecided_margin_gap"
    assert request.requested_margin_relation == "strictly_between_thresholds"
    assert request.undecided_margin_interval_lower_exclusive == "1/328459"
    assert request.undecided_margin_interval_upper_exclusive == "1/328458"
    assert request.undecided_margin_interval_width == "1/107884986222"
    assert not request.theorem_backed_classification
    assert not request.proved_margin_applies
    assert not request.impossible_margin_applies
    assert request.margin_thresholds_ordered
    assert request.proved_impossible_branches_disjoint
    assert request.undecided_margin_open_gap
    assert request.margin_status_exhaustive
    assert request.in_range_semantic_trichotomy
    assert (
        request.failure_reason
        == "requested_margin_between_proved_and_impossible_thresholds"
    )


def test_standard_channel0_d19_range_request_bracket_reports_outside_range() -> None:
    request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=103993,
        requested_margin=Fraction(1, 328459),
    )
    assert request.request_status == "outside_range"
    assert request.requested_margin_relation == "context_outside_range"
    assert not request.theorem_backed_classification
    assert request.margin_thresholds_ordered
    assert request.proved_impossible_branches_disjoint
    assert not request.undecided_margin_open_gap
    assert request.margin_status_exhaustive
    assert not request.in_range_semantic_trichotomy
    assert request.failure_reason == "requested_context_outside_d19_obstruction_range"


def test_rope_quickstart_d19_classifier_example_lists_current_theorem_spine() -> None:
    request = certify_standard_channel0_d19_range_request_margin_bracket(
        requested_context=131072,
        requested_margin=Fraction(1, 328458),
    )
    docs = Path("docs/ROPE_CERTIFIER_QUICKSTART.md").read_text(encoding="utf-8")
    expected_theorem_comment = (
        "request.theorem_ids     # " + ",".join(request.theorem_ids)
    )

    assert expected_theorem_comment in docs
    assert "request.margin_thresholds_ordered  # True" in docs
    assert "request.proved_impossible_branches_disjoint  # True" in docs
    assert "request.margin_status_exhaustive  # True" in docs
    assert "undecided_margin_open_gap" in docs


def test_rational_turn_ratio_certificate_reports_denominator_boundary() -> None:
    certificate = certify_rational_turn_ratio_finite_margin(
        numerator=3,
        denominator=7,
        context_length=8,
    )
    assert not certificate.pass_certificate
    assert certificate.certified_margin is None
    assert certificate.exact_nearest_gap_margin == "0"
    assert certificate.exact_nearest_gap == 7
    assert certificate.zero_margin_witness == (7, 3)
    assert certificate.theorem_ids == (
        "AIRA-T0055",
        "AIRA-T0057",
        "AIRA-T0182",
        "AIRA-T0183",
    )


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


def test_standard_channel0_d12_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d12_bank_request(
        requested_context=8192,
        requested_margin=Fraction(1, 104220),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 8192
    assert certificate.requested_margin == "1/104220"
    assert certificate.certified_context == 8192
    assert certificate.certified_margin == "1/104220"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0123", "AIRA-T0124")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d12_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d12_bank_request(
        requested_context=4096,
        requested_margin=Fraction(1, 200000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0123",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d12_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d12_bank_request(
        requested_context=8193,
        requested_margin=Fraction(1, 104220),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d12_seed"

    margin_failure = certify_standard_channel0_d12_bank_request(
        requested_context=8192,
        requested_margin=Fraction(1, 104219),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d12_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d12_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 104220),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d12_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 104220),
        )


def test_standard_channel0_d13_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d13_bank_request(
        requested_context=8192,
        requested_margin=Fraction(1, 104219),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 8192
    assert certificate.requested_margin == "1/104219"
    assert certificate.certified_context == 8192
    assert certificate.certified_margin == "1/104219"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0130", "AIRA-T0131")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d13_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d13_bank_request(
        requested_context=4096,
        requested_margin=Fraction(1, 200000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0130",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d13_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d13_bank_request(
        requested_context=8193,
        requested_margin=Fraction(1, 104219),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d13_seed"

    margin_failure = certify_standard_channel0_d13_bank_request(
        requested_context=8192,
        requested_margin=Fraction(1, 104218),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d13_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d13_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 104219),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d13_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 104219),
        )


def test_standard_channel0_d14_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d14_bank_request(
        requested_context=16384,
        requested_margin=Fraction(1, 104219),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 16384
    assert certificate.requested_margin == "1/104219"
    assert certificate.certified_context == 16384
    assert certificate.certified_margin == "1/104219"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0136", "AIRA-T0137")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d14_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d14_bank_request(
        requested_context=8192,
        requested_margin=Fraction(1, 200000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0136",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d14_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d14_bank_request(
        requested_context=16385,
        requested_margin=Fraction(1, 104219),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d14_seed"

    margin_failure = certify_standard_channel0_d14_bank_request(
        requested_context=16384,
        requested_margin=Fraction(1, 104218),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d14_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d14_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 104219),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d14_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 104219),
        )


def test_standard_channel0_d16_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d16_bank_request(
        requested_context=65536,
        requested_margin=Fraction(1, 104219),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 65536
    assert certificate.requested_margin == "1/104219"
    assert certificate.certified_context == 65536
    assert certificate.certified_margin == "1/104219"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0151", "AIRA-T0152")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d16_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d16_bank_request(
        requested_context=32768,
        requested_margin=Fraction(1, 200000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0151",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d16_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d16_bank_request(
        requested_context=65537,
        requested_margin=Fraction(1, 104219),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d16_seed"

    margin_failure = certify_standard_channel0_d16_bank_request(
        requested_context=65536,
        requested_margin=Fraction(1, 104218),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d16_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d16_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 104219),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d16_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 104219),
        )


def test_standard_channel0_d17_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d17_bank_request(
        requested_context=131072,
        requested_margin=Fraction(1, 328459),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 131072
    assert certificate.requested_margin == "1/328459"
    assert certificate.certified_context == 131072
    assert certificate.certified_margin == "1/328459"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0159", "AIRA-T0160")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d17_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d17_bank_request(
        requested_context=65536,
        requested_margin=Fraction(1, 400000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0159",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d17_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d17_bank_request(
        requested_context=131073,
        requested_margin=Fraction(1, 328459),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d17_seed"

    margin_failure = certify_standard_channel0_d17_bank_request(
        requested_context=131072,
        requested_margin=Fraction(1, 328458),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d17_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d17_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 328459),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d17_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 328459),
        )


def test_standard_channel0_d18_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d18_bank_request(
        requested_context=163840,
        requested_margin=Fraction(1, 328459),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 163840
    assert certificate.requested_margin == "1/328459"
    assert certificate.certified_context == 163840
    assert certificate.certified_margin == "1/328459"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.theorem_ids == ("AIRA-T0165", "AIRA-T0166")
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D18Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D18Seed_cons",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d18_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d18_bank_request(
        requested_context=131072,
        requested_margin=Fraction(1, 400000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert certificate.theorem_ids == ("AIRA-T0165",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D18Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d18_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d18_bank_request(
        requested_context=163841,
        requested_margin=Fraction(1, 328459),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d18_seed"

    margin_failure = certify_standard_channel0_d18_bank_request(
        requested_context=163840,
        requested_margin=Fraction(1, 328458),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d18_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d18_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 328459),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d18_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 328459),
        )


def test_standard_channel0_d19_bank_request_certificate_marks_covered_request() -> None:
    certificate = certify_standard_channel0_d19_bank_request(
        requested_context=196608,
        requested_margin=Fraction(1, 328459),
    )
    assert certificate.pass_certificate
    assert certificate.failure_reason is None
    assert certificate.requested_context == 196608
    assert certificate.requested_margin == "1/328459"
    assert certificate.certified_context == 196608
    assert certificate.certified_margin == "1/328459"
    assert certificate.bank_shape == "standard_channel0_first"
    assert certificate.context_wide_pair_scope == (
        "all ordered unequal pairs left < right < requested_context"
    )
    assert certificate.context_wide_first_channel_contract
    assert certificate.theorem_ids == (
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
    )
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed",
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed_cons",
        "Circle.Applications.ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn",
        "Circle.Applications.ropeStandardChannel0D19_proved_request_firstChannel_bank_noNearTurn_onContext",
        "Circle.Applications.ropeStandardChannel0D19_proved_request_radianFirstChannel_bank_noNearTurn_onContext",
        "Circle.Applications.ropeStandardChannel0D19_contextRange_radianFirstChannel_request_semantic_trichotomy",
    )
    assert "standard channel 0 as its first channel" in certificate.assumptions[0]
    assert "tolerance < fullTurn * requestedMargin" in certificate.tolerance_rule
    assert "not a full all-channel" in certificate.claim_boundary


def test_standard_channel0_d19_bank_request_certificate_supports_membership_shape() -> None:
    certificate = certify_standard_channel0_d19_bank_request(
        requested_context=163840,
        requested_margin=Fraction(1, 400000),
        first_channel_shape=False,
    )
    assert certificate.pass_certificate
    assert certificate.bank_shape == "contains_standard_channel0"
    assert not certificate.context_wide_first_channel_contract
    assert certificate.theorem_ids == ("AIRA-T0171",)
    assert certificate.lean_declarations == (
        "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D19Seed",
    )
    assert "contains the standard channel-0" in certificate.assumptions[0]


def test_standard_channel0_d19_bank_request_certificate_reports_failures() -> None:
    context_failure = certify_standard_channel0_d19_bank_request(
        requested_context=196609,
        requested_margin=Fraction(1, 328459),
    )
    assert not context_failure.pass_certificate
    assert context_failure.failure_reason == "requested_context_exceeds_d19_seed"

    margin_failure = certify_standard_channel0_d19_bank_request(
        requested_context=196608,
        requested_margin=Fraction(1, 328458),
    )
    assert not margin_failure.pass_certificate
    assert margin_failure.failure_reason == "requested_margin_exceeds_d19_seed"

    with pytest.raises(ValueError, match="requested_context must be positive"):
        certify_standard_channel0_d19_bank_request(
            requested_context=0,
            requested_margin=Fraction(1, 328459),
        )
    with pytest.raises(ValueError, match="requested_margin must be nonnegative"):
        certify_standard_channel0_d19_bank_request(
            requested_context=1,
            requested_margin=Fraction(-1, 328459),
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
    assert certificate.exact_discrete.prefix_collision_reports[0].fitting_collision_multiple_count == 3
    assert (
        certificate.exact_discrete.prefix_collision_reports[0]
        .collision_pair_count_closed_form_numerator
        == 48
    )
    assert certificate.exact_discrete.prefix_collision_reports[0].total_bank_collision_pair_count == 24
    assert certificate.exact_discrete.guaranteed_common_gap_collision_pair_count == 14
    assert certificate.exact_discrete.common_gap_fitting_multiple_count == 3
    assert certificate.exact_discrete.common_gap_collision_pair_count_closed_form_numerator == 48
    assert certificate.exact_discrete.guaranteed_common_gap_multiple_pair_count == 24
    assert certificate.exact_discrete.total_bank_collision_pair_count == 24
    assert certificate.exact_discrete.sample_collision_pairs[0] == (0, 6)
    assert certificate.theorem_ids == ROPE_CERTIFIER_THEOREMS
    assert "AIRA-T0203" in certificate.theorem_ids
    assert "AIRA-T0204" in certificate.theorem_ids
    assert "AIRA-T0205" in certificate.theorem_ids
    assert tuple(layer.layer for layer in certificate.proof_layers) == (
        "exact_integer_period_phase_bank",
        "rational_discretized_finite_margin",
        "interval_backed_standard_rope",
        "numerical_real_phase_scan",
    )
    assert certificate.proof_layers[0].status == "FAIL"
    assert certificate.proof_layers[1].status == "AVAILABLE_NAMED_PRESET"
    assert certificate.proof_layers[2].status == "AVAILABLE_SEED_CONTEXT_196608"
    assert certificate.proof_layers[2].theorem_ids == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS
    assert "margin 1/328459" in certificate.proof_layers[2].explanation
    assert "at or above 1/328458" in certificate.proof_layers[2].explanation
    assert "D19 one-separating-channel bank bridges" in certificate.proof_layers[2].explanation
    assert not certificate.proof_layers[3].theorem_backed
    assert "AIRA-T0046" in certificate.theorem_ids
    assert "AIRA-T0048" in certificate.theorem_ids
    assert "AIRA-T0049" in certificate.theorem_ids
    assert "AIRA-T0051" in certificate.theorem_ids
    assert "AIRA-T0052" in certificate.theorem_ids
    assert "AIRA-T0179" in certificate.theorem_ids
    assert "AIRA-T0180" in certificate.theorem_ids
    assert "AIRA-T0184" in certificate.theorem_ids
    assert "AIRA-T0188" not in certificate.theorem_ids
    assert "AIRA-T0189" not in certificate.theorem_ids
    assert "AIRA-T0174" in certificate.theorem_ids
    assert "AIRA-T0175" in certificate.theorem_ids
    assert "AIRA-T0176" in certificate.theorem_ids
    assert "AIRA-T0210" in certificate.theorem_ids
    assert "AIRA-T0211" in certificate.theorem_ids
    assert "AIRA-T0212" in certificate.theorem_ids
    assert "AIRA-T0213" in certificate.theorem_ids
    assert "AIRA-T0024" in certificate.exact_discrete.assumptions[3]
    exact_assumptions = "\n".join(certificate.exact_discrete.assumptions)
    assert "AIRA-T0184" in exact_assumptions
    assert "AIRA-T0175" in exact_assumptions
    assert "AIRA-T0176" in exact_assumptions
    assert "AIRA-T0212" in exact_assumptions
    assert "AIRA-T0213" in exact_assumptions
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
    assert certificate.exact_discrete.common_gap_fitting_multiple_count == 0
    assert certificate.exact_discrete.guaranteed_common_gap_multiple_pair_count == 0
    assert certificate.exact_discrete.total_bank_collision_pair_count == 0
    assert certificate.exact_discrete.sample_collision_pairs == ()
    assert "AIRA-T0046" in certificate.theorem_ids
    assert "AIRA-T0048" in certificate.theorem_ids
    assert "AIRA-T0049" in certificate.theorem_ids
    assert "AIRA-T0051" in certificate.theorem_ids
    assert "AIRA-T0052" in certificate.theorem_ids
    assert "AIRA-T0179" in certificate.theorem_ids
    assert "AIRA-T0180" in certificate.theorem_ids
    assert "AIRA-T0184" in certificate.theorem_ids
    assert "AIRA-T0174" in certificate.theorem_ids
    assert "AIRA-T0175" in certificate.theorem_ids
    assert "AIRA-T0176" in certificate.theorem_ids
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
    assert payload["exact_discrete"]["prefix_collision_reports"][0]["fitting_collision_multiple_count"] == 3
    assert (
        payload["exact_discrete"]["prefix_collision_reports"][0]
        ["collision_pair_count_closed_form_numerator"]
        == 48
    )
    assert payload["exact_discrete"]["smallest_pass_subfamily_size"] is None
    assert payload["exact_discrete"]["guaranteed_common_gap_collision_pair_count"] == 14
    assert payload["exact_discrete"]["common_gap_fitting_multiple_count"] == 3
    assert payload["exact_discrete"]["common_gap_collision_pair_count_closed_form_numerator"] == 48
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
    assert payload["exact_discrete"]["common_gap_fitting_multiple_count"] == 3
    assert payload["exact_discrete"]["common_gap_collision_pair_count_closed_form_numerator"] == 48
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
    assert "AIRA-T0190" not in prefix_payload["exact_discrete"]["prefix_collision_reports"][1]["theorem_ids"]
    assert "AIRA-T0191" not in prefix_payload["exact_discrete"]["prefix_collision_reports"][1]["theorem_ids"]
    assert "AIRA-T0190" in prefix_payload["exact_discrete"]["prefix_collision_reports"][2]["theorem_ids"]
    assert "AIRA-T0191" in prefix_payload["exact_discrete"]["prefix_collision_reports"][2]["theorem_ids"]
    assert "AIRA-T0188" in prefix_payload["exact_discrete"]["prefix_collision_reports"][2]["theorem_ids"]
    assert "AIRA-T0192" in prefix_payload["exact_discrete"]["prefix_collision_reports"][2]["theorem_ids"]
    assert "AIRA-T0193" in prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["theorem_ids"]
    assert "AIRA-T0194" in prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["theorem_ids"]
    assert "AIRA-T0189" in prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["theorem_ids"]
    assert "AIRA-T0195" in prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["theorem_ids"]
    assert prefix_payload["exact_discrete"]["subfamily_pass_reports"][0]["subfamily_indices"] == [2, 3]
    assert prefix_payload["exact_discrete"]["prefix_collision_reports"][1]["lcm_collision_gap"] == 18
    assert prefix_payload["exact_discrete"]["prefix_collision_reports"][1]["fitting_collision_multiple_count"] == 7
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
    assert shared_payload["exact_discrete"]["common_gap_fitting_multiple_count"] == 1
    assert shared_payload["exact_discrete"]["total_bank_collision_pair_count"] == 10
    assert "AIRA-T0198" in shared_payload["exact_discrete"]["theorem_ids"]
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
    assert "AIRA-T0190" not in certificate.exact_discrete.prefix_collision_reports[1].theorem_ids
    assert "AIRA-T0191" not in certificate.exact_discrete.prefix_collision_reports[1].theorem_ids
    assert "AIRA-T0190" in certificate.exact_discrete.prefix_collision_reports[2].theorem_ids
    assert "AIRA-T0191" in certificate.exact_discrete.prefix_collision_reports[2].theorem_ids
    assert "AIRA-T0188" in certificate.exact_discrete.prefix_collision_reports[2].theorem_ids
    assert "AIRA-T0192" in certificate.exact_discrete.prefix_collision_reports[2].theorem_ids
    assert "AIRA-T0193" in certificate.exact_discrete.subfamily_pass_reports[0].theorem_ids
    assert "AIRA-T0194" in certificate.exact_discrete.subfamily_pass_reports[0].theorem_ids
    assert "AIRA-T0189" in certificate.exact_discrete.subfamily_pass_reports[0].theorem_ids
    assert "AIRA-T0195" in certificate.exact_discrete.subfamily_pass_reports[0].theorem_ids
    assert certificate.exact_discrete.prefix_collision_reports[1].lcm_collision_gap == 18
    assert certificate.exact_discrete.prefix_collision_reports[1].fitting_collision_multiple_count == 7
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
    assert shared.exact_discrete.common_gap_collision_pair_count_closed_form_numerator == 448
    assert shared.exact_discrete.total_bank_collision_pair_count == 224
    assert "AIRA-T0199" in shared.exact_discrete.theorem_ids

    boundary_fail = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["quantized_lcm_boundary_fail_241"],
    )
    assert not boundary_fail.exact_discrete.pass_exact
    assert boundary_fail.exact_discrete.common_collision_gap == 240
    assert boundary_fail.exact_discrete.guaranteed_common_gap_collision_pair_count == 1
    assert boundary_fail.exact_discrete.common_gap_collision_pair_count_closed_form_numerator == 2
    assert boundary_fail.exact_discrete.total_bank_collision_pair_count == 1
    assert boundary_fail.exact_discrete.sample_collision_pairs == ((0, 240),)
    assert "AIRA-T0200" in boundary_fail.exact_discrete.theorem_ids

    scaled_pass = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["interpolated_x4_boundary_pass_960"],
    )
    assert scaled_pass.exact_discrete.pass_exact
    assert scaled_pass.exact_discrete.discretized_periods == (60, 64)
    assert scaled_pass.exact_discrete.common_collision_gap is None
    assert scaled_pass.exact_discrete.common_gap_collision_pair_count_closed_form_numerator == 0
    assert scaled_pass.exact_discrete.total_bank_collision_pair_count == 0
    assert "AIRA-T0201" in scaled_pass.exact_discrete.theorem_ids

    scaled_fail = certify_phase_bank_positions(
        PHASE_BANK_CERTIFIER_PRESETS["interpolated_x4_boundary_fail_961"],
    )
    assert not scaled_fail.exact_discrete.pass_exact
    assert scaled_fail.exact_discrete.common_collision_gap == 960
    assert scaled_fail.exact_discrete.total_bank_collision_pair_count == 1
    assert scaled_fail.exact_discrete.common_gap_fitting_multiple_count == 1
    assert scaled_fail.exact_discrete.common_gap_collision_pair_count_closed_form_numerator == 2
    assert scaled_fail.exact_discrete.sample_collision_pairs == ((0, 960),)
    assert "AIRA-T0202" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0206" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0207" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0210" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0211" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0212" in scaled_fail.exact_discrete.theorem_ids
    assert "AIRA-T0213" in scaled_fail.exact_discrete.theorem_ids


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
    assert payload["rational_margin_certificate"]["exact_nearest_gap_margin"] == "1/4099"
    assert payload["rational_margin_certificate"]["exact_nearest_gap"] == 1
    assert payload["rational_margin_certificate"]["theorem_ids"] == list(
        ROPE_RATIONAL_PRESET_4099_THEOREMS
    )
    assert payload["standard_interval_certificate"]["name"] == ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME
    assert payload["standard_interval_certificate"]["pass_certificate"] is True
    assert payload["standard_interval_certificate"]["witness_count"] == 196607
    assert payload["standard_interval_certificate"]["first_interval_witness"]["gap"] == 1
    assert payload["standard_interval_certificate"]["last_interval_witness"]["gap"] == 196607
    assert "interval_witnesses" not in payload["standard_interval_certificate"]
    assert payload["standard_d12_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d12_bank_bridge_request"]["requested_context"] == 8192
    assert payload["standard_d12_bank_bridge_request"]["requested_margin"] == "1/104220"
    assert payload["standard_d12_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0123",
        "AIRA-T0124",
    ]
    assert payload["standard_d12_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d12_margin_bracket"]["context_length"] == 8192
    assert payload["standard_d12_margin_bracket"]["proved_margin"] == "1/104220"
    assert payload["standard_d12_margin_bracket"]["impossible_margin_floor"] == "1/104218"
    assert payload["standard_d12_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0120",
        "AIRA-T0121",
        "AIRA-T0118",
        "AIRA-T0125",
    ]
    assert payload["standard_d13_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d13_bank_bridge_request"]["requested_context"] == 8192
    assert payload["standard_d13_bank_bridge_request"]["requested_margin"] == "1/104219"
    assert payload["standard_d13_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0130",
        "AIRA-T0131",
    ]
    assert payload["standard_d13_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d13_margin_bracket"]["context_length"] == 8192
    assert payload["standard_d13_margin_bracket"]["proved_margin"] == "1/104219"
    assert payload["standard_d13_margin_bracket"]["impossible_margin_floor"] == "1/104218"
    assert payload["standard_d13_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0127",
        "AIRA-T0128",
        "AIRA-T0118",
        "AIRA-T0132",
    ]
    assert payload["standard_d14_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d14_bank_bridge_request"]["requested_context"] == 16384
    assert payload["standard_d14_bank_bridge_request"]["requested_margin"] == "1/104219"
    assert payload["standard_d14_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0136",
        "AIRA-T0137",
    ]
    assert payload["standard_d14_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d14_margin_bracket"]["context_length"] == 16384
    assert payload["standard_d14_margin_bracket"]["proved_margin"] == "1/104219"
    assert payload["standard_d14_margin_bracket"]["impossible_margin_floor"] == "1/104218"
    assert payload["standard_d14_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0133",
        "AIRA-T0134",
        "AIRA-T0118",
        "AIRA-T0138",
    ]
    assert payload["standard_d16_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d16_bank_bridge_request"]["requested_context"] == 65536
    assert payload["standard_d16_bank_bridge_request"]["requested_margin"] == "1/104219"
    assert payload["standard_d16_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0151",
        "AIRA-T0152",
    ]
    assert payload["standard_d16_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d16_margin_bracket"]["context_length"] == 65536
    assert payload["standard_d16_margin_bracket"]["proved_margin"] == "1/104219"
    assert payload["standard_d16_margin_bracket"]["impossible_margin_floor"] == "1/104218"
    assert payload["standard_d16_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0148",
        "AIRA-T0149",
        "AIRA-T0118",
        "AIRA-T0153",
    ]
    assert payload["standard_d17_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d17_bank_bridge_request"]["requested_context"] == 131072
    assert payload["standard_d17_bank_bridge_request"]["requested_margin"] == "1/328459"
    assert payload["standard_d17_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0159",
        "AIRA-T0160",
    ]
    assert payload["standard_d17_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d17_margin_bracket"]["context_length"] == 131072
    assert payload["standard_d17_margin_bracket"]["proved_margin"] == "1/328459"
    assert payload["standard_d17_margin_bracket"]["impossible_margin_floor"] == "1/328458"
    assert payload["standard_d17_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0156",
        "AIRA-T0157",
        "AIRA-T0155",
        "AIRA-T0161",
    ]
    assert payload["standard_d18_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d18_bank_bridge_request"]["requested_context"] == 163840
    assert payload["standard_d18_bank_bridge_request"]["requested_margin"] == "1/328459"
    assert payload["standard_d18_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0165",
        "AIRA-T0166",
    ]
    assert payload["standard_d18_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d18_margin_bracket"]["context_length"] == 163840
    assert payload["standard_d18_margin_bracket"]["proved_margin"] == "1/328459"
    assert payload["standard_d18_margin_bracket"]["impossible_margin_floor"] == "1/328458"
    assert payload["standard_d18_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0162",
        "AIRA-T0163",
        "AIRA-T0155",
        "AIRA-T0167",
    ]
    assert payload["standard_d19_bank_bridge_request"]["pass_certificate"] is True
    assert payload["standard_d19_bank_bridge_request"]["requested_context"] == 196608
    assert payload["standard_d19_bank_bridge_request"]["requested_margin"] == "1/328459"
    assert payload["standard_d19_bank_bridge_request"]["theorem_ids"] == [
        "AIRA-T0171",
        "AIRA-T0172",
        "AIRA-T0234",
        "AIRA-T0235",
        "AIRA-T0236",
        "AIRA-T0237",
    ]
    assert payload["standard_d19_bank_bridge_request"][
        "context_wide_first_channel_contract"
    ] is True
    assert payload["standard_d19_margin_bracket"]["pass_certificate"] is True
    assert payload["standard_d19_margin_bracket"]["context_length"] == 196608
    assert payload["standard_d19_margin_bracket"]["proved_margin"] == "1/328459"
    assert payload["standard_d19_margin_bracket"]["impossible_margin_floor"] == "1/328458"
    assert payload["standard_d19_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0168",
        "AIRA-T0169",
        "AIRA-T0155",
        "AIRA-T0173",
        "AIRA-T0209",
        "AIRA-T0208",
    ]
    assert payload["standard_d19_range_request_margin_bracket"]["request_status"] == (
        "impossible"
    )
    assert payload["standard_d19_range_request_margin_bracket"][
        "requested_margin_relation"
    ] == "at_or_above_impossible_floor"
    assert payload["standard_d19_range_request_margin_bracket"][
        "undecided_margin_interval_lower_exclusive"
    ] == "1/328459"
    assert payload["standard_d19_range_request_margin_bracket"][
        "undecided_margin_interval_upper_exclusive"
    ] == "1/328458"
    assert payload["standard_d19_range_request_margin_bracket"][
        "undecided_margin_interval_width"
    ] == "1/107884986222"
    assert payload["standard_d19_range_request_margin_bracket"][
        "theorem_backed_classification"
    ] is True
    assert payload["standard_d19_range_request_margin_bracket"]["requested_context"] == 131072
    assert payload["standard_d19_range_request_margin_bracket"]["requested_margin"] == (
        "1/328458"
    )
    assert payload["standard_d19_range_request_margin_bracket"]["theorem_ids"] == [
        "AIRA-T0216",
        "AIRA-T0217",
        "AIRA-T0218",
        "AIRA-T0219",
        "AIRA-T0220",
        "AIRA-T0221",
        "AIRA-T0233",
        "AIRA-T0232",
    ]
    assert (
        payload["standard_d19_range_request_margin_bracket"][
            "undecided_margin_open_gap"
        ]
        is False
    )
    assert (
        payload["standard_d19_range_request_margin_bracket"][
            "margin_status_exhaustive"
        ]
        is True
    )
    assert (
        payload["standard_d19_range_request_margin_bracket"][
            "in_range_semantic_trichotomy"
        ]
        is True
    )
    assert (
        payload["standard_d19_range_request_margin_bracket"][
            "margin_thresholds_ordered"
        ]
        is True
    )
    assert (
        payload["standard_d19_range_request_margin_bracket"][
            "proved_impossible_branches_disjoint"
        ]
        is True
    )
    assert payload["standard_channel0_frontier_summary"]["proved_margin"] == "1/328459"
    assert payload["standard_channel0_frontier_summary"]["proved_context"] == 196608
    assert payload["standard_channel0_frontier_summary"]["proved_theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170"
    )
    assert payload["standard_channel0_frontier_summary"]["sharp_64k_margin"] == "1/104219"
    assert payload["standard_channel0_frontier_summary"]["sharp_64k_context"] == 65536
    assert payload["standard_channel0_frontier_summary"]["sharp_64k_theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150"
    )
    assert payload["standard_channel0_frontier_summary"]["too_strong_128k_margin"] == "1/104219"
    assert payload["standard_channel0_frontier_summary"]["candidate_full_contexts"] == []
    assert payload["standard_channel0_frontier_summary"]["candidate_first_uncovered_gaps"] == [
        103993,
    ]
    assert payload["standard_channel0_frontier_summary"]["compression_bridge_theorem_ids"] == [
        "AIRA-T0139",
        "AIRA-T0140",
        "AIRA-T0141",
    ]
    assert payload["standard_channel0_frontier_summary"][
        "compression_bridge_lean_declarations"
    ] == [
        "Circle.Applications.ropeTurnRatioIntervalWitness_of_rationalIntervalBand",
        "Circle.Applications.ropeTurnRatioIntervalCertificate_of_rationalIntervalBands",
        "Circle.Applications.ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid",
    ]
    assert payload["standard_channel0_frontier_summary"]["frontier_status"] == (
        "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170"
    )
    assert "does not upgrade candidate rows" in (
        payload["standard_channel0_frontier_summary"]["claim_boundary"]
    )
    assert payload["standard_band_certificate_audits"][6]["requested_context_length"] == 32768
    assert payload["standard_band_certificate_audits"][6]["certified_context_length"] == 32768
    assert payload["standard_band_certificate_audits"][6]["band_count"] == 5216
    assert payload["standard_band_certificate_audits"][6]["valid_band_count"] == 5216
    assert payload["standard_band_certificate_audits"][6]["coverage_pass"] is True
    assert payload["standard_band_certificate_audits"][6]["pass_audit"] is True
    assert payload["standard_band_certificate_audits"][6]["theorem_status"] == (
        "executable_band_audit_not_lean_proved"
    )
    assert payload["standard_band_certificate_audits"][7]["requested_context_length"] == 65536
    assert payload["standard_band_certificate_audits"][7]["certified_context_length"] == 65536
    assert payload["standard_band_certificate_audits"][7]["band_count"] == 10431
    assert payload["standard_band_certificate_audits"][7]["coverage_pass"] is True
    assert payload["standard_band_certificate_audits"][8]["requested_context_length"] == 131072
    assert payload["standard_band_certificate_audits"][8]["certified_context_length"] == 103993
    assert payload["standard_band_certificate_audits"][8]["band_count"] == 16551
    assert payload["standard_band_certificate_audits"][8]["first_uncovered_gap"] == 103993
    assert payload["standard_band_certificate_audits"][8]["endpoint_validity_pass"] is True
    assert payload["standard_band_certificate_audits"][8]["coverage_pass"] is False
    assert payload["standard_band_certificate_audits"][8]["pass_audit"] is False
    assert payload["standard_band_certificate_audits"][8]["theorem_ids"] == [
        "AIRA-T0139",
        "AIRA-T0140",
        "AIRA-T0141",
    ]
    assert "Executable source-data audit only" in (
        payload["standard_band_certificate_audits"][8]["claim_boundary"]
    )
    assert payload["standard_band_certificate_audits"][9]["requested_context_length"] == 131072
    assert payload["standard_band_certificate_audits"][9]["certified_context_length"] == 131072
    assert payload["standard_band_certificate_audits"][9]["band_count"] == 20861
    assert payload["standard_band_certificate_audits"][9]["valid_band_count"] == 20861
    assert payload["standard_band_certificate_audits"][9]["first_uncovered_gap"] is None
    assert payload["standard_band_certificate_audits"][9]["coverage_pass"] is True
    assert payload["standard_band_certificate_audits"][9]["pass_audit"] is True
    assert payload["standard_band_certificate_audits"][10]["requested_context_length"] == 163840
    assert payload["standard_band_certificate_audits"][10]["certified_context_length"] == 163840
    assert payload["standard_band_certificate_audits"][10]["band_count"] == 26076
    assert payload["standard_band_certificate_audits"][10]["valid_band_count"] == 26076
    assert payload["standard_band_certificate_audits"][10]["first_uncovered_gap"] is None
    assert payload["standard_band_certificate_audits"][10]["coverage_pass"] is True
    assert payload["standard_band_certificate_audits"][10]["pass_audit"] is True
    assert payload["standard_band_certificate_audits"][11]["requested_context_length"] == 196608
    assert payload["standard_band_certificate_audits"][11]["certified_context_length"] == 196608
    assert payload["standard_band_certificate_audits"][11]["band_count"] == 31291
    assert payload["standard_band_certificate_audits"][11]["valid_band_count"] == 31291
    assert payload["standard_band_certificate_audits"][11]["first_uncovered_gap"] is None
    assert payload["standard_band_certificate_audits"][11]["coverage_pass"] is True
    assert payload["standard_band_certificate_audits"][11]["pass_audit"] is True
    assert payload["standard_interval_candidate_plans"][0]["context_length"] == 333
    assert "bands" not in payload["standard_interval_candidate_plans"][0]
    assert payload["standard_interval_candidate_plans"][0]["first_band"]["start_gap"] == 1
    assert payload["standard_interval_candidate_plans"][0]["last_band"]["end_gap"] == 332
    assert payload["standard_interval_candidate_plans"][0]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089"
    )
    assert payload["standard_interval_candidate_plans"][1]["context_length"] == 710
    assert payload["standard_interval_candidate_plans"][1]["band_count"] == 113
    assert payload["standard_interval_candidate_plans"][1]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094"
    )
    assert payload["standard_interval_candidate_plans"][2]["context_length"] == 4096
    assert payload["standard_interval_candidate_plans"][2]["band_count"] == 652
    assert payload["standard_interval_candidate_plans"][2]["planned_margin"] == "1/104219"
    assert payload["standard_interval_candidate_plans"][2]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114"
    )
    assert payload["standard_interval_candidate_plans"][3]["context_length"] == 8192
    assert payload["standard_interval_candidate_plans"][3]["band_count"] == 1304
    assert payload["standard_interval_candidate_plans"][3]["planned_margin"] == "1/104220"
    assert payload["standard_interval_candidate_plans"][3]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122"
    )
    assert payload["standard_interval_candidate_plans"][4]["context_length"] == 8192
    assert payload["standard_interval_candidate_plans"][4]["band_count"] == 1304
    assert payload["standard_interval_candidate_plans"][4]["planned_margin"] == "1/104219"
    assert payload["standard_interval_candidate_plans"][4]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129"
    )
    assert payload["standard_interval_candidate_plans"][5]["context_length"] == 16384
    assert payload["standard_interval_candidate_plans"][5]["band_count"] == 2608
    assert payload["standard_interval_candidate_plans"][5]["planned_margin"] == "1/104219"
    assert "bands" not in payload["standard_interval_candidate_plans"][5]
    assert payload["standard_interval_candidate_plans"][5]["first_band"]["start_gap"] == 1
    assert payload["standard_interval_candidate_plans"][5]["last_band"]["start_gap"] == 16381
    assert payload["standard_interval_candidate_plans"][5]["last_band"]["end_gap"] == 16383
    assert payload["standard_interval_candidate_plans"][5]["last_band"]["cell"] == 2607
    assert payload["standard_interval_candidate_plans"][5]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135"
    )
    assert payload["standard_interval_candidate_plans"][6]["context_length"] == 32768
    assert payload["standard_interval_candidate_plans"][6]["band_count"] == 5216
    assert payload["standard_interval_candidate_plans"][6]["first_uncovered_gap"] is None
    assert payload["standard_interval_candidate_plans"][6]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144"
    )
    assert payload["standard_interval_candidate_plans"][7]["context_length"] == 65536
    assert payload["standard_interval_candidate_plans"][7]["band_count"] == 10431
    assert payload["standard_interval_candidate_plans"][7]["first_uncovered_gap"] is None
    assert payload["standard_interval_candidate_plans"][7]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150"
    )
    assert payload["standard_interval_candidate_plans"][8]["context_length"] == 103993
    assert payload["standard_interval_candidate_plans"][8]["band_count"] == 16551
    assert payload["standard_interval_candidate_plans"][8]["first_uncovered_gap"] == 103993
    assert payload["standard_interval_candidate_plans"][8]["theorem_status"] == (
        "candidate_plan_not_lean_proved"
    )
    assert payload["standard_interval_candidate_plans"][9]["context_length"] == 131072
    assert payload["standard_interval_candidate_plans"][9]["band_count"] == 20861
    assert payload["standard_interval_candidate_plans"][9]["planned_margin"] == "1/328459"
    assert payload["standard_interval_candidate_plans"][9]["first_uncovered_gap"] is None
    assert payload["standard_interval_candidate_plans"][9]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158"
    )
    assert payload["standard_interval_candidate_plans"][10]["context_length"] == 163840
    assert payload["standard_interval_candidate_plans"][10]["band_count"] == 26076
    assert payload["standard_interval_candidate_plans"][10]["planned_margin"] == "1/328459"
    assert payload["standard_interval_candidate_plans"][10]["first_uncovered_gap"] is None
    assert payload["standard_interval_candidate_plans"][10]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0162_to_AIRA-T0164"
    )
    assert payload["standard_interval_candidate_plans"][11]["context_length"] == 196608
    assert payload["standard_interval_candidate_plans"][11]["band_count"] == 31291
    assert payload["standard_interval_candidate_plans"][11]["planned_margin"] == "1/328459"
    assert payload["standard_interval_candidate_plans"][11]["first_uncovered_gap"] is None
    assert payload["standard_interval_candidate_plans"][11]["theorem_status"] == (
        "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170"
    )
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
    assert "Exact weakest gap margin" in markdown_result.stdout
    assert "1/4099" in markdown_result.stdout
    assert "AIRA-T0182, AIRA-T0183" in markdown_result.stdout
    assert "AIRA-T0196" in markdown_result.stdout
    assert "Named Standard RoPE Interval Seed" in markdown_result.stdout
    assert "Standard RoPE D12 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0123, AIRA-T0124" in markdown_result.stdout
    assert "Standard RoPE D12 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0120, AIRA-T0121, AIRA-T0118, AIRA-T0125" in markdown_result.stdout
    assert "Standard RoPE D13 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0130, AIRA-T0131" in markdown_result.stdout
    assert "Standard RoPE D13 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0127, AIRA-T0128, AIRA-T0118, AIRA-T0132" in markdown_result.stdout
    assert "Standard RoPE D14 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0136, AIRA-T0137" in markdown_result.stdout
    assert "Standard RoPE D14 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0133, AIRA-T0134, AIRA-T0118, AIRA-T0138" in markdown_result.stdout
    assert "Standard RoPE D16 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0151, AIRA-T0152" in markdown_result.stdout
    assert "Standard RoPE D16 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0148, AIRA-T0149, AIRA-T0118, AIRA-T0153" in markdown_result.stdout
    assert "Standard RoPE D17 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0159, AIRA-T0160" in markdown_result.stdout
    assert "Standard RoPE D17 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0156, AIRA-T0157, AIRA-T0155, AIRA-T0161" in markdown_result.stdout
    assert "Standard RoPE D18 Bank Bridge Request" in markdown_result.stdout
    assert "AIRA-T0165, AIRA-T0166" in markdown_result.stdout
    assert "Standard RoPE D18 Margin Bracket" in markdown_result.stdout
    assert "AIRA-T0162, AIRA-T0163, AIRA-T0155, AIRA-T0167" in markdown_result.stdout
    assert "Standard RoPE D19 Bank Bridge Request" in markdown_result.stdout
    assert (
        "AIRA-T0171, AIRA-T0172, AIRA-T0234, AIRA-T0235, AIRA-T0236, AIRA-T0237"
        in markdown_result.stdout
    )
    assert "Standard RoPE D19 Margin Bracket" in markdown_result.stdout
    assert (
        "AIRA-T0168, AIRA-T0169, AIRA-T0155, AIRA-T0173, AIRA-T0209, AIRA-T0208"
        in markdown_result.stdout
    )
    assert "Standard RoPE D19 Range Request Classifier" in markdown_result.stdout
    assert "AIRA-T0216, AIRA-T0217" in markdown_result.stdout
    assert "| standard_rope_channel0_d19_range_request_margin_bracket | 131072 | 1/328458 | impossible | True | False | True | False | True | True | True | True | AIRA-T0216, AIRA-T0217, AIRA-T0218, AIRA-T0219, AIRA-T0220, AIRA-T0221, AIRA-T0233, AIRA-T0232 |" in markdown_result.stdout
    assert "Standard Channel-0 Frontier Summary" in markdown_result.stdout
    assert "| 1/328459 | 196608 | lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170 |  | 103993 | AIRA-T0139, AIRA-T0140, AIRA-T0141 | lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170 |" in markdown_result.stdout
    assert "Standard RoPE Candidate Interval Plans" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0162_to_AIRA-T0164" in markdown_result.stdout
    assert "lean_proved_interval_seed_AIRA-T0168_to_AIRA-T0170" in markdown_result.stdout
    assert "candidate_plan_not_lean_proved" in markdown_result.stdout
    assert "context_32768" in markdown_result.stdout
    assert "context_65536" in markdown_result.stdout
    assert "context_131072" in markdown_result.stdout
    assert "context_163840" in markdown_result.stdout
    assert "context_196608" in markdown_result.stdout
    assert "| 103993 | 16551 | candidate_plan_not_lean_proved |" in markdown_result.stdout
    assert "Rational-Band Certificate Audits" in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_32768 "
        "| 32768 | 32768 | 5216 | 5216 | 32767 | none | PASS | PASS |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_65536 "
        "| 65536 | 65536 | 10431 | 10431 | 65535 | none | PASS | PASS |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_103993 "
        "| 131072 | 103993 | 16551 | 16551 | 103992 | 103993 | FAIL | PASS |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_328459_context_131072 "
        "| 131072 | 131072 | 20861 | 20861 | 131071 | none | PASS | PASS |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_328459_context_163840 "
        "| 163840 | 163840 | 26076 | 26076 | 163839 | none | PASS | PASS |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_328459_context_196608 "
        "| 196608 | 196608 | 31291 | 31291 | 196607 | none | PASS | PASS |"
    ) in markdown_result.stdout
    assert "Band Endpoint Audit" in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104220_context_8192 "
        "| last | 8187-8191 | 1303 |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_8192 "
        "| last | 8187-8191 | 1303 |"
    ) in markdown_result.stdout
    assert (
        "| standard_rope_channel0_interval_plan_d20_margin_1_104219_context_16384 "
        "| last | 16381-16383 | 2607 |"
    ) in markdown_result.stdout
    assert "AIRA-T0126" in markdown_result.stdout
    assert "Exact Phase-Bank Diagnostics" in markdown_result.stdout
    assert ROPE_RATIONAL_PRESET_4099_NAME in markdown_result.stdout
    assert ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME in markdown_result.stdout
    assert "quantized_shared_factor_256" in markdown_result.stdout
    assert "interpolated_x4_boundary_fail_961" in markdown_result.stdout
    assert "AIRA-T0199" in markdown_result.stdout
    assert "AIRA-T0202" in markdown_result.stdout
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
