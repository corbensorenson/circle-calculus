"""Proof-carrying RoPE position distinguishability certifier.

The certifier has two layers:

* an exact discretized phase-bank contract backed by Lean theorem ids, where
  each rotary channel is represented by an integer period and collisions are
  characterized by divisibility of the position gap;
* a numerical real-phase margin scan for ordinary RoPE frequencies. This is an
  engineering diagnostic only, not a formal proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import combinations
from math import ceil, floor, gcd, pi, tau
from typing import Any, Iterable, Literal, Sequence


DiscretizationPolicy = Literal["round", "floor", "ceil"]
PiBoundPreset = Literal["d4", "d6", "d20"]


ROPE_CERTIFIER_THEOREMS: tuple[str, ...] = (
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
)

ROPE_CERTIFIER_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeDiscreteCollision_iff_gap_dvd",
    "Circle.Applications.ropeDiscreteDistinguishable_iff_not_gap_dvd",
    "Circle.Applications.ropeDiscreteCollision_iff_eq_on_context",
    "Circle.Applications.ropePhaseBankCollision_iff_forall_gap_dvd",
    "Circle.Applications.ropePhaseBankDistinguishable_iff_exists_not_gap_dvd",
    "Circle.Applications.ropePhaseBankDistinguishable_of_period_ge_context",
    "Circle.Applications.ropeCollisionPairCountAtGap_pos_iff",
    "Circle.Applications.ropePhaseBankCollision_at_gap_of_forall_dvd",
    "Circle.Applications.ropePhaseBankCollision_at_commonGap_mul_of_forall_dvd",
    "Circle.Applications.ropeDiscreteCollision_exists_positive_multiple_gap",
    "Circle.Applications.ropePhaseBankCollision_iff_lcm_dvd_gap",
    "Circle.Applications.not_ropePhaseBankCollision_of_lcm_ge_context",
    "Circle.Applications.ropePhaseBankCollision_at_lcm_gap",
    "Circle.Applications.ropePhaseBankCollision_exists_of_lcm_pos_lt_context",
    "Circle.Applications.not_ropePhaseBankCollision_of_prefix_lcm_ge_context",
    "Circle.Applications.not_ropePhaseBankCollision_of_subbank_lcm_ge_context",
)

ROPE_REAL_PHASE_PRECURSOR_THEOREMS: tuple[str, ...] = (
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
    "AIRA-T0126",
    "AIRA-T0139",
    "AIRA-T0140",
    "AIRA-T0141",
)

ROPE_REAL_PHASE_PRECURSOR_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeRealPhaseGapAbs_eq_natGap_mul_abs",
    "Circle.Applications.ropeRealPhaseGapAbs_ge_minGap_mul_lower",
    "Circle.Applications.ropeRealPhaseNatTurnEndpointErrors_ge_margin_of_one_turn_window",
    "Circle.Applications.ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window",
    "Circle.Applications.ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window",
    "Circle.Applications.ropeRealPhaseTurnSeparated_of_one_turn_window",
    "Circle.Applications.not_ropeRealPhaseNearTurn_of_turnSeparated_lt",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_bankTurnSeparated_lt",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_one_turn_window",
    "Circle.Applications.ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError",
    "Circle.Applications.not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin",
    "Circle.Applications.ropeTurnRatioFiniteMargin_mono_context",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context",
    "Circle.Applications.ropeTurnRatioFiniteMargin_mono_margin",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin",
    "Circle.Applications.ropeTurnRatioFiniteMargin_int_iff_nonpos_of_one_lt_context",
    "Circle.Applications.ropeTurnRatioFiniteMargin_iff_range_gap_bounds",
    "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_iff_nonpos_of_den_lt_context",
    "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den",
    "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_one_over_den_iff_context_le_den",
    "Circle.Applications.ropeNearestIntegerWitnesses_iff_forall_int",
    "Circle.Applications.ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses",
    "Circle.Applications.ropeTurnRatioIntervalWitness_of_band_bounds",
    "Circle.Applications.ropeTurnRatioIntervalWitness_of_rationalIntervalBand",
    "Circle.Applications.ropeTurnRatioIntervalCertificate_of_rationalIntervalBands",
    "Circle.Applications.ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid",
)

ROPE_RATIONAL_PRESET_4099_NAME = "rational_turn_ratio_1_4099_context_4096"

ROPE_RATIONAL_PRESET_4099_THEOREMS: tuple[str, ...] = (
    "AIRA-T0056",
    "AIRA-T0059",
    "AIRA-T0060",
    "AIRA-T0061",
    "AIRA-T0062",
)

ROPE_RATIONAL_PRESET_4099_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den",
    "Circle.Applications.ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses",
    "Circle.Applications.RopeTurnRatioFiniteMarginCertificate.certifies",
    "Circle.Applications.ropeRationalPreset4099_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeRationalPreset4099_nearTurn",
)

ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS: tuple[str, ...] = (
    "AIRA-T0139",
    "AIRA-T0140",
    "AIRA-T0141",
)

ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeTurnRatioIntervalWitness_of_rationalIntervalBand",
    "Circle.Applications.ropeTurnRatioIntervalCertificate_of_rationalIntervalBands",
    "Circle.Applications.ropeTurnRatioRationalIntervalBand_valid_of_ratEndpointValid",
)

ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME = "standard_rope_channel0_interval_context_131072"

ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS: tuple[str, ...] = (
    "AIRA-T0063",
    "AIRA-T0064",
    "AIRA-T0065",
    "AIRA-T0066",
    "AIRA-T0067",
    "AIRA-T0068",
    "AIRA-T0069",
    "AIRA-T0070",
    "AIRA-T0071",
    "AIRA-T0072",
    "AIRA-T0073",
    "AIRA-T0074",
    "AIRA-T0075",
    "AIRA-T0076",
    "AIRA-T0077",
    "AIRA-T0078",
    "AIRA-T0079",
    "AIRA-T0080",
    "AIRA-T0081",
    "AIRA-T0082",
    "AIRA-T0083",
    "AIRA-T0084",
    "AIRA-T0085",
    "AIRA-T0086",
    "AIRA-T0087",
    "AIRA-T0088",
    "AIRA-T0089",
    "AIRA-T0090",
    "AIRA-T0091",
    "AIRA-T0092",
    "AIRA-T0093",
    "AIRA-T0094",
    "AIRA-T0095",
    "AIRA-T0096",
    "AIRA-T0097",
    "AIRA-T0098",
    "AIRA-T0099",
    "AIRA-T0100",
    "AIRA-T0101",
    "AIRA-T0102",
    "AIRA-T0103",
    "AIRA-T0104",
    "AIRA-T0105",
    "AIRA-T0106",
    "AIRA-T0107",
    "AIRA-T0108",
    "AIRA-T0109",
    "AIRA-T0110",
    "AIRA-T0111",
    "AIRA-T0112",
    "AIRA-T0113",
    "AIRA-T0114",
    "AIRA-T0115",
    "AIRA-T0116",
    "AIRA-T0117",
    "AIRA-T0118",
    "AIRA-T0119",
    "AIRA-T0120",
    "AIRA-T0121",
    "AIRA-T0122",
    "AIRA-T0123",
    "AIRA-T0124",
    "AIRA-T0125",
    "AIRA-T0126",
    "AIRA-T0127",
    "AIRA-T0128",
    "AIRA-T0129",
    "AIRA-T0130",
    "AIRA-T0131",
    "AIRA-T0132",
    "AIRA-T0133",
    "AIRA-T0134",
    "AIRA-T0135",
    "AIRA-T0136",
    "AIRA-T0137",
    "AIRA-T0138",
    "AIRA-T0139",
    "AIRA-T0140",
    "AIRA-T0141",
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
)

ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.ropeTurnRatioIntervalWitness_forall_int",
    "Circle.Applications.ropeTurnRatioFiniteMargin_of_intervalCertificate",
    "Circle.Applications.ropeTurnRatioIntervalWitness_mono_margin",
    "Circle.Applications.ropeTurnRatioIntervalCertificate_mono_margin",
    "Circle.Applications.ropeStandardChannel0Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D2Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D2Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D2Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D3Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D3Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D3Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D4Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D4Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D4Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D5Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D5Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D5Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0_piD4_base_lower",
    "Circle.Applications.ropeStandardChannel0_piD4_base_upper",
    "Circle.Applications.ropeStandardChannel0D6Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D6Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D6Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D7Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D7Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D7Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0_piD6_base_lower",
    "Circle.Applications.ropeStandardChannel0_piD6_base_upper",
    "Circle.Applications.ropeStandardChannel0D8Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D8Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D8Seed_nearTurn",
    "Circle.Applications.ropeStandardChannel0D8_gap710_error_lt_margin",
    "Circle.Applications.not_ropeStandardChannel0D8SeedMargin_of_context_gt_seed",
    "Circle.Applications.ropeStandardChannel0_piD20_base_lower",
    "Circle.Applications.ropeStandardChannel0_piD20_base_upper",
    "Circle.Applications.ropeStandardChannel0D9Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D9Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D9Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D9Seed",
    "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_65536",
    "Circle.Applications.not_ropeStandardChannel0_margin_one_over_65536_of_context_gt_710",
    "Circle.Applications.ropeStandardChannel0D10Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D10Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D10Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D10Seed",
    "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104000",
    "Circle.Applications.not_ropeStandardChannel0_margin_one_over_104000_of_context_gt_710",
    "Circle.Applications.ropeStandardChannel0D11Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D11Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D11Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed",
    "Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104218",
    "Circle.Applications.not_ropeStandardChannel0_margin_one_over_104218_of_context_gt_710",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed_cons",
    "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
    "Circle.Applications.ropeStandardChannel0D11_context4096_margin_bracket",
    "Circle.Applications.ropeStandardChannel0D12Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D12Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D12Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons",
    "Circle.Applications.ropeStandardChannel0D12_context8192_margin_bracket",
    "Circle.Applications.ropeTurnRatioIntervalWitness_of_band_bounds",
    "Circle.Applications.ropeStandardChannel0D13Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D13Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D13Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons",
    "Circle.Applications.ropeStandardChannel0D13_context8192_margin_bracket",
    "Circle.Applications.ropeStandardChannel0D14Seed_intervalCertificate",
    "Circle.Applications.ropeStandardChannel0D14Seed_turnRatioFiniteMargin",
    "Circle.Applications.not_ropeStandardChannel0D14Seed_nearTurn",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons",
    "Circle.Applications.ropeStandardChannel0D14_context16384_margin_bracket",
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
)

ROPE_STANDARD_CHANNEL0_D12_BANK_BRIDGE_THEOREMS: tuple[str, ...] = (
    "AIRA-T0123",
    "AIRA-T0124",
)

ROPE_STANDARD_CHANNEL0_D12_BANK_BRIDGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons",
)

ROPE_STANDARD_CHANNEL0_D13_BANK_BRIDGE_THEOREMS: tuple[str, ...] = (
    "AIRA-T0130",
    "AIRA-T0131",
)

ROPE_STANDARD_CHANNEL0_D13_BANK_BRIDGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons",
)

ROPE_STANDARD_CHANNEL0_D14_BANK_BRIDGE_THEOREMS: tuple[str, ...] = (
    "AIRA-T0136",
    "AIRA-T0137",
)

ROPE_STANDARD_CHANNEL0_D14_BANK_BRIDGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons",
)

ROPE_STANDARD_CHANNEL0_D16_BANK_BRIDGE_THEOREMS: tuple[str, ...] = (
    "AIRA-T0151",
    "AIRA-T0152",
)

ROPE_STANDARD_CHANNEL0_D16_BANK_BRIDGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed_cons",
)

ROPE_STANDARD_CHANNEL0_D17_BANK_BRIDGE_THEOREMS: tuple[str, ...] = (
    "AIRA-T0159",
    "AIRA-T0160",
)

ROPE_STANDARD_CHANNEL0_D17_BANK_BRIDGE_LEAN_DECLARATIONS: tuple[str, ...] = (
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed",
    "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed_cons",
)

ROPE_CERTIFIER_CLAIM_BOUNDARY = (
    "Exact pass/fail is for the declared integer-period discretized RoPE model. "
    "The real-phase margin scan is numerical evidence only. This is not a model-quality, "
    "context-length, perplexity, training-stability, speed, memory, or deployment claim."
)

PHASE_BANK_CERTIFIER_CLAIM_BOUNDARY = (
    "Exact pass/fail is for a declared positive integer-period phase bank. "
    "No real-valued RoPE, model-quality, context-length, perplexity, speed, memory, "
    "training-stability, or deployment claim is made."
)


@dataclass(frozen=True)
class RoPEConfig:
    head_dim: int
    base: float
    context_length: int
    tolerance: float = 1e-6
    discretization: DiscretizationPolicy = "round"


@dataclass(frozen=True)
class PhaseBankConfig:
    periods: tuple[int, ...]
    context_length: int


@dataclass(frozen=True)
class PhaseBankPrefixCollisionReport:
    prefix_length: int
    periods: tuple[int, ...]
    lcm_collision_gap: int | None
    lcm_reaches_context: bool
    total_bank_collision_pair_count: int
    sample_collision_pairs: tuple[tuple[int, int], ...]
    theorem_ids: tuple[str, ...] = (
        "AIRA-T0036",
        "AIRA-T0046",
        "AIRA-T0048",
        "AIRA-T0049",
        "AIRA-T0051",
    )


@dataclass(frozen=True)
class PhaseBankSubfamilyPassReport:
    subfamily_indices: tuple[int, ...]
    periods: tuple[int, ...]
    lcm_value: int
    theorem_ids: tuple[str, ...] = (
        "AIRA-T0036",
        "AIRA-T0046",
        "AIRA-T0052",
    )


@dataclass(frozen=True)
class ExactDiscreteRoPECertificate:
    pass_exact: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    discretized_periods: tuple[int, ...]
    period_count: int
    single_period_collision_pair_counts: tuple[int, ...]
    prefix_collision_reports: tuple[PhaseBankPrefixCollisionReport, ...]
    first_exact_pass_prefix_length: int | None
    subfamily_pass_reports: tuple[PhaseBankSubfamilyPassReport, ...]
    smallest_pass_subfamily_size: int | None
    context_length: int
    common_collision_gap: int | None
    common_collision_gap_reaches_context: bool
    guaranteed_common_gap_collision_pair_count: int
    guaranteed_common_gap_multiple_pair_count: int
    total_bank_collision_pair_count: int
    sample_collision_pairs: tuple[tuple[int, int], ...]
    assumptions: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class RealPhaseMarginReport:
    pass_margin: bool
    tolerance: float
    worst_margin_radians: float
    worst_gap: int | None
    worst_channel_index: int | None
    worst_channel_period_estimate: float | None
    scanned_gap_count: int
    near_collision_gaps: tuple[tuple[int, float], ...]
    explanation: str
    formal_precursor_theorem_ids: tuple[str, ...] = ROPE_REAL_PHASE_PRECURSOR_THEOREMS
    formal_precursor_lean_declarations: tuple[str, ...] = ROPE_REAL_PHASE_PRECURSOR_LEAN_DECLARATIONS


@dataclass(frozen=True)
class RoPEProofLayerReport:
    layer: str
    status: str
    theorem_backed: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str


@dataclass(frozen=True)
class RoPEPositionCertificate:
    schema_id: str
    config: RoPEConfig
    exact_discrete: ExactDiscreteRoPECertificate
    real_phase_margin: RealPhaseMarginReport
    real_period_estimates: tuple[float, ...]
    proof_layers: tuple[RoPEProofLayerReport, ...]
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    claim_boundary: str = ROPE_CERTIFIER_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseBankPositionCertificate:
    schema_id: str
    config: PhaseBankConfig
    exact_discrete: ExactDiscreteRoPECertificate
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    claim_boundary: str = PHASE_BANK_CERTIFIER_CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TurnRatioFiniteMarginCertificate:
    schema_id: str
    name: str
    numerator: int
    denominator: int
    context_length: int
    turn_ratio: float
    certified_margin: float | None
    pass_certificate: bool
    zero_margin_witness: tuple[int, int] | None
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RationalIntervalWitnessReport:
    gap: int
    lower: str
    upper: str
    cell: int


@dataclass(frozen=True)
class StandardRoPEIntervalBandReport:
    start_gap: int
    end_gap: int
    cell: int
    start_lower_value: str
    end_upper_value: str
    endpoint_cell_margin_ok: bool
    bridge_theorem_id: str = "AIRA-T0126"


@dataclass(frozen=True)
class StandardRoPEIntervalPlan:
    schema_id: str
    name: str
    turn_ratio_expression: str
    context_length: int
    planned_margin: str
    pi_bound_preset: PiBoundPreset
    pi_bounds: str
    lower_turn_ratio_bound: str
    upper_turn_ratio_bound: str
    pass_plan: bool
    first_uncovered_gap: int | None
    band_count: int
    bands: tuple[StandardRoPEIntervalBandReport, ...]
    theorem_status: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardRoPERationalBandCertificateAudit:
    schema_id: str
    name: str
    source_plan_name: str
    requested_context_length: int
    certified_context_length: int
    planned_margin: str
    pi_bound_preset: PiBoundPreset
    lower_turn_ratio_bound: str
    upper_turn_ratio_bound: str
    band_count: int
    valid_band_count: int
    covered_gap_count: int
    first_covered_gap: int | None
    last_covered_gap: int | None
    first_uncovered_gap: int | None
    contiguous_from_one: bool
    endpoint_validity_pass: bool
    coverage_pass: bool
    pass_audit: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    theorem_status: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntervalBackedTurnRatioCertificate:
    schema_id: str
    name: str
    turn_ratio_expression: str
    context_length: int
    certified_margin: str
    pass_certificate: bool
    pi_bounds: str
    interval_witnesses: tuple[RationalIntervalWitnessReport, ...]
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D12BankBridgeCertificate:
    schema_id: str
    name: str
    requested_context: int
    requested_margin: str
    certified_context: int
    certified_margin: str
    pass_certificate: bool
    failure_reason: str | None
    bank_shape: str
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    assumptions: tuple[str, ...]
    tolerance_rule: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D12MarginBracketCertificate:
    schema_id: str
    name: str
    context_length: int
    proved_margin: str
    impossible_margin_floor: str
    pass_certificate: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D13BankBridgeCertificate:
    schema_id: str
    name: str
    requested_context: int
    requested_margin: str
    certified_context: int
    certified_margin: str
    pass_certificate: bool
    failure_reason: str | None
    bank_shape: str
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    assumptions: tuple[str, ...]
    tolerance_rule: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D13MarginBracketCertificate:
    schema_id: str
    name: str
    context_length: int
    proved_margin: str
    impossible_margin_floor: str
    pass_certificate: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D14BankBridgeCertificate:
    schema_id: str
    name: str
    requested_context: int
    requested_margin: str
    certified_context: int
    certified_margin: str
    pass_certificate: bool
    failure_reason: str | None
    bank_shape: str
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    assumptions: tuple[str, ...]
    tolerance_rule: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D14MarginBracketCertificate:
    schema_id: str
    name: str
    context_length: int
    proved_margin: str
    impossible_margin_floor: str
    pass_certificate: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D16BankBridgeCertificate:
    schema_id: str
    name: str
    requested_context: int
    requested_margin: str
    certified_context: int
    certified_margin: str
    pass_certificate: bool
    failure_reason: str | None
    bank_shape: str
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    assumptions: tuple[str, ...]
    tolerance_rule: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D16MarginBracketCertificate:
    schema_id: str
    name: str
    context_length: int
    proved_margin: str
    impossible_margin_floor: str
    pass_certificate: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D17BankBridgeCertificate:
    schema_id: str
    name: str
    requested_context: int
    requested_margin: str
    certified_context: int
    certified_margin: str
    pass_certificate: bool
    failure_reason: str | None
    bank_shape: str
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    assumptions: tuple[str, ...]
    tolerance_rule: str
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StandardChannel0D17MarginBracketCertificate:
    schema_id: str
    name: str
    context_length: int
    proved_margin: str
    impossible_margin_floor: str
    pass_certificate: bool
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    explanation: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def scale_phase_bank_periods(periods: Sequence[int], scale_factor: int) -> tuple[int, ...]:
    """Scale declared integer periods for an exact interpolation-style analogue.

    This is not a real-valued RoPE interpolation theorem. It is the exact
    integer-period phase-bank model where slowing phase advance by an integer
    factor is represented by multiplying every declared period by that factor.
    """
    if scale_factor <= 0:
        raise ValueError("scale_factor must be positive")
    result: list[int] = []
    for period in periods:
        if period <= 0:
            raise ValueError("periods must be positive")
        result.append(period * scale_factor)
    return tuple(result)


ROPE_CERTIFIER_PRESETS: dict[str, RoPEConfig] = {
    "llama_style_10000_4k": RoPEConfig(
        head_dim=128,
        base=10000.0,
        context_length=4096,
        tolerance=1e-6,
        discretization="round",
    ),
    "llama_style_10000_128k": RoPEConfig(
        head_dim=128,
        base=10000.0,
        context_length=131_072,
        tolerance=1e-6,
        discretization="round",
    ),
    "llama_style_500000_128k": RoPEConfig(
        head_dim=128,
        base=500000.0,
        context_length=131_072,
        tolerance=1e-6,
        discretization="round",
    ),
    "diagnostic_single_channel_10000_20": RoPEConfig(
        head_dim=2,
        base=10000.0,
        context_length=20,
        tolerance=1e-6,
        discretization="round",
    ),
    "diagnostic_two_channel_36_128": RoPEConfig(
        head_dim=4,
        base=36.0,
        context_length=128,
        tolerance=1e-6,
        discretization="round",
    ),
    "diagnostic_prefix_pass_4_128": RoPEConfig(
        head_dim=8,
        base=4.0,
        context_length=128,
        tolerance=1e-6,
        discretization="round",
    ),
    "diagnostic_shared_factor_25_64": RoPEConfig(
        head_dim=6,
        base=25.0,
        context_length=64,
        tolerance=1e-6,
        discretization="round",
    ),
}


PHASE_BANK_CERTIFIER_PRESETS: dict[str, PhaseBankConfig] = {
    "quantized_shared_factor_256": PhaseBankConfig(
        periods=(32, 48, 96),
        context_length=256,
    ),
    "quantized_lcm_boundary_fail_241": PhaseBankConfig(
        periods=(15, 16),
        context_length=241,
    ),
    "interpolated_x4_boundary_pass_960": PhaseBankConfig(
        periods=scale_phase_bank_periods((15, 16), 4),
        context_length=960,
    ),
    "interpolated_x4_boundary_fail_961": PhaseBankConfig(
        periods=scale_phase_bank_periods((15, 16), 4),
        context_length=961,
    ),
}


def validate_rope_config(config: RoPEConfig) -> None:
    if config.head_dim <= 0:
        raise ValueError("head_dim must be positive")
    if config.head_dim % 2 != 0:
        raise ValueError("head_dim must be even because RoPE uses dimension pairs")
    if config.base <= 1.0:
        raise ValueError("base must be greater than 1")
    if config.context_length <= 0:
        raise ValueError("context_length must be positive")
    if config.tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    if config.discretization not in ("round", "floor", "ceil"):
        raise ValueError("discretization must be one of: round, floor, ceil")


def validate_phase_bank_config(config: PhaseBankConfig) -> None:
    if config.context_length <= 0:
        raise ValueError("context_length must be positive")
    if not config.periods:
        raise ValueError("periods must be nonempty")
    for period in config.periods:
        if period <= 0:
            raise ValueError("periods must be positive")


def rope_angular_frequencies(head_dim: int, base: float) -> tuple[float, ...]:
    config = RoPEConfig(head_dim=head_dim, base=base, context_length=1)
    validate_rope_config(config)
    return tuple(base ** (-(2 * index) / head_dim) for index in range(head_dim // 2))


def rope_period_estimates(head_dim: int, base: float) -> tuple[float, ...]:
    """Return real-valued position periods for the standard RoPE channel schedule."""
    return tuple(tau / frequency for frequency in rope_angular_frequencies(head_dim, base))


def discretize_rope_periods(
    periods: Sequence[float],
    policy: DiscretizationPolicy = "round",
) -> tuple[int, ...]:
    """Map real period estimates to integer periods for the Lean-backed contract."""
    result: list[int] = []
    for period in periods:
        if policy == "round":
            value = int(floor(period + 0.5))
        elif policy == "floor":
            value = int(floor(period))
        elif policy == "ceil":
            value = int(ceil(period))
        else:
            raise ValueError("policy must be one of: round, floor, ceil")
        result.append(max(1, value))
    return tuple(result)


def capped_lcm(values: Iterable[int], cap: int) -> tuple[int, bool]:
    """Return the LCM until it reaches ``cap``.

    The boolean says whether the exact LCM is known to be at least ``cap``.
    """
    if cap <= 0:
        raise ValueError("cap must be positive")
    current = 1
    for value in values:
        if value <= 0:
            raise ValueError("periods must be positive")
        current = current * value // gcd(current, value)
        if current >= cap:
            return current, True
    return current, current >= cap


def sample_collision_pairs(context_length: int, gap: int, limit: int = 5) -> tuple[tuple[int, int], ...]:
    if gap <= 0 or gap >= context_length:
        return ()
    return tuple((start, start + gap) for start in range(min(limit, context_length - gap)))


def collision_pair_count_at_gap(context_length: int, gap: int) -> int:
    """Count ordered starts whose paired position is exactly ``gap`` ahead."""
    if gap <= 0 or gap >= context_length:
        return 0
    return context_length - gap


def collision_pair_count_at_gap_multiples(context_length: int, common_gap: int) -> int:
    """Count guaranteed starts over all positive in-context multiples of a common gap."""
    if common_gap <= 0 or common_gap >= context_length:
        return 0
    total = 0
    multiple = 1
    while multiple * common_gap < context_length:
        total += collision_pair_count_at_gap(context_length, multiple * common_gap)
        multiple += 1
    return total


def single_period_collision_pair_count(context_length: int, period: int) -> int:
    """Count ordered unequal position pairs that collide in one integer-period channel."""
    return collision_pair_count_at_gap_multiples(context_length, period)


def phase_bank_prefix_collision_reports(
    context_length: int,
    periods: Sequence[int],
    *,
    limit: int = 8,
    sample_limit: int = 3,
) -> tuple[PhaseBankPrefixCollisionReport, ...]:
    """Return exact collision summaries for bounded prefixes of a phase bank.

    Each prefix reuses the same theorem-backed LCM contract as the full bank:
    if the prefix LCM reaches the inspected context, that prefix has no unequal
    all-channel collision inside the context; otherwise its exact all-channel
    collision count is the sum over positive in-context multiples of the prefix
    LCM. Prefixes are reported to help identify how many declared channels are
    needed before the integer-period bank becomes position-distinguishing.
    """
    if context_length <= 0:
        raise ValueError("context_length must be positive")
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if sample_limit < 0:
        raise ValueError("sample_limit must be nonnegative")
    normalized_periods = tuple(periods)
    for period in normalized_periods:
        if period <= 0:
            raise ValueError("periods must be positive")
    reports: list[PhaseBankPrefixCollisionReport] = []
    for prefix_length in range(1, min(len(normalized_periods), limit) + 1):
        prefix = normalized_periods[:prefix_length]
        collision_gap, reaches_context = capped_lcm(prefix, context_length)
        pair_count = 0 if reaches_context else collision_pair_count_at_gap_multiples(
            context_length,
            collision_gap,
        )
        reports.append(PhaseBankPrefixCollisionReport(
            prefix_length=prefix_length,
            periods=prefix,
            lcm_collision_gap=None if reaches_context else collision_gap,
            lcm_reaches_context=reaches_context,
            total_bank_collision_pair_count=pair_count,
            sample_collision_pairs=sample_collision_pairs(
                context_length,
                collision_gap,
                limit=sample_limit,
            ),
        ))
    return tuple(reports)


def phase_bank_subfamily_pass_reports(
    context_length: int,
    periods: Sequence[int],
    *,
    max_size: int = 3,
    limit: int = 8,
) -> tuple[PhaseBankSubfamilyPassReport, ...]:
    """Return bounded subfamilies whose LCM already reaches the context.

    These reports are exact integer-period certificates for small selected
    subbanks. They are bounded intentionally: the goal is to expose small
    sufficient channel subsets for inspection, not to solve a minimum set-cover
    problem over large phase banks.
    """
    if context_length <= 0:
        raise ValueError("context_length must be positive")
    if max_size <= 0:
        raise ValueError("max_size must be positive")
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    normalized_periods = tuple(periods)
    for period in normalized_periods:
        if period <= 0:
            raise ValueError("periods must be positive")
    reports: list[PhaseBankSubfamilyPassReport] = []
    for size in range(1, min(max_size, len(normalized_periods)) + 1):
        for indices in combinations(range(len(normalized_periods)), size):
            subfamily = tuple(normalized_periods[index] for index in indices)
            lcm_value, reaches_context = capped_lcm(subfamily, context_length)
            if reaches_context:
                reports.append(PhaseBankSubfamilyPassReport(
                    subfamily_indices=indices,
                    periods=subfamily,
                    lcm_value=lcm_value,
                ))
                if len(reports) >= limit:
                    return tuple(reports)
    return tuple(reports)


def brute_force_single_period_collision_pair_count(context_length: int, period: int) -> int:
    """Brute-force parity oracle for ``single_period_collision_pair_count``."""
    if context_length <= 0 or period <= 0:
        return 0
    count = 0
    for left in range(context_length):
        for right in range(left + 1, context_length):
            if left % period == right % period:
                count += 1
    return count


def circular_phase_distance(angle: float) -> float:
    """Distance in radians from ``angle`` to the nearest whole turn."""
    return abs((angle + pi) % tau - pi)


def real_phase_nat_turn_error(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    turns: int,
) -> float:
    """Mirror Lean's ``ropeRealPhaseNatTurnError`` for examples and tests."""
    if left < 0 or right < 0:
        raise ValueError("left and right must be nonnegative")
    if turns < 0:
        raise ValueError("turns must be nonnegative")
    phase = abs((right - left) * frequency)
    return abs(phase - turns * full_turn)


def real_phase_int_turn_error(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    turns: int,
) -> float:
    """Mirror Lean's signed ``ropeRealPhaseIntTurnError``."""
    if left < 0 or right < 0:
        raise ValueError("left and right must be nonnegative")
    phase = abs((right - left) * frequency)
    return abs(phase - turns * full_turn)


def real_phase_scaled_turn_ratio_error(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    turns: int,
) -> float:
    """Mirror the Diophantine-scaled full-turn error theorem.

    This helper assumes the theorem-side hypotheses: ordered positions,
    nonnegative frequency, and positive ``full_turn``.
    """
    if left < 0 or right < 0:
        raise ValueError("left and right must be nonnegative")
    if right < left:
        raise ValueError("right must be greater than or equal to left")
    if frequency < 0:
        raise ValueError("frequency must be nonnegative")
    if full_turn <= 0:
        raise ValueError("full_turn must be positive")
    gap = right - left
    return full_turn * abs(gap * (frequency / full_turn) - turns)


def turn_ratio_nearest_integer_error(*, turn_ratio: float, gap: int, turns: int) -> float:
    """Mirror Lean's ``ropeTurnRatioError`` for deterministic tests."""
    if gap < 0:
        raise ValueError("gap must be nonnegative")
    return abs(gap * turn_ratio - turns)


def turn_ratio_floor_ceil_witness_errors(
    *,
    turn_ratio: float,
    gap: int,
) -> tuple[float, float]:
    """Return the floor/ceiling witness errors for one turn-ratio gap.

    This mirrors ``ropeNearestIntegerWitnesses_iff_forall_int``: for a fixed
    real value ``gap * turn_ratio``, checking the floor and ceiling integer
    witnesses is equivalent to checking every integer turn. The returned
    values are executable diagnostics, not formal proof objects.
    """
    if gap < 0:
        raise ValueError("gap must be nonnegative")
    value = gap * turn_ratio
    floor_turn = int(floor(value))
    ceil_turn = int(ceil(value))
    return (
        turn_ratio_nearest_integer_error(
            turn_ratio=turn_ratio,
            gap=gap,
            turns=floor_turn,
        ),
        turn_ratio_nearest_integer_error(
            turn_ratio=turn_ratio,
            gap=gap,
            turns=ceil_turn,
        ),
    )


def turn_ratio_floor_ceil_witness_margin(*, turn_ratio: float, gap: int) -> float:
    """Return the smaller floor/ceiling witness error for one gap."""
    floor_error, ceil_error = turn_ratio_floor_ceil_witness_errors(
        turn_ratio=turn_ratio,
        gap=gap,
    )
    return min(floor_error, ceil_error)


def turn_ratio_floor_ceil_witnesses_certify_margin(
    *,
    turn_ratio: float,
    margin: float,
    context_length: int,
) -> bool:
    """Check the finite floor/ceiling witness shape for a margin.

    This helper mirrors the Lean equivalence between
    ``ropeTurnRatioFiniteMargin`` and the finite generated-gap floor/ceiling
    witness predicate. It is still a floating-point executable check, not a
    Lean proof for a concrete irrational RoPE ratio.
    """
    return all(
        margin <= turn_ratio_floor_ceil_witness_margin(
            turn_ratio=turn_ratio,
            gap=gap,
        )
        for gap in turn_ratio_finite_margin_gap_candidates(context_length=context_length)
    )


def turn_ratio_finite_margin_gap_candidates(*, context_length: int) -> tuple[int, ...]:
    """Positive gap candidates for a finite-context turn-ratio margin scan.

    This mirrors the positive members of Lean's ``List.range context`` bridge:
    a finite-context margin only needs gaps ``1 <= gap < context_length``. The
    Lean floor/ceiling witness bridge then reduces the integer-turn obligation
    for each generated gap to two nearest-integer witnesses.
    """
    if context_length < 0:
        raise ValueError("context_length must be nonnegative")
    return tuple(range(1, context_length))


def turn_ratio_nat_ratio_zero_margin_witness(
    *,
    numerator: int,
    denominator: int,
    context_length: int,
) -> tuple[int, int] | None:
    """Return the denominator-gap exact-turn witness for a rational turn ratio.

    This mirrors the Lean guardrail for ratios ``numerator / denominator``:
    when ``0 < denominator < context_length``, the gap ``denominator`` lands
    exactly on ``numerator`` full turns, so no positive finite-context margin
    can be certified from that channel alone.
    """
    if numerator < 0:
        raise ValueError("numerator must be nonnegative")
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if context_length <= 0:
        raise ValueError("context_length must be positive")
    if denominator < context_length:
        return denominator, numerator
    return None


def turn_ratio_nat_ratio_coprime_margin_certificate(
    *,
    numerator: int,
    denominator: int,
    context_length: int,
) -> float | None:
    """Return the proved rational finite-context margin when hypotheses hold.

    Lean proves that a reduced natural rational turn ratio ``numerator /
    denominator`` has finite-context nearest-integer margin at least
    ``1 / denominator`` as long as every inspected positive gap is strictly
    below the denominator, expressed by ``context_length <= denominator``.
    """
    if numerator < 0:
        raise ValueError("numerator must be nonnegative")
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if context_length <= 0:
        raise ValueError("context_length must be positive")
    if gcd(numerator, denominator) == 1 and context_length <= denominator:
        return 1.0 / denominator
    return None


def certify_rational_turn_ratio_finite_margin(
    *,
    numerator: int,
    denominator: int,
    context_length: int,
    name: str | None = None,
) -> TurnRatioFiniteMarginCertificate:
    """Build a theorem-backed rational/discretized turn-ratio certificate.

    This is the first end-to-end finite-margin certificate lane: Lean proves
    the reduced rational boundary, while Python records the concrete values an
    engineer can inspect. It does not certify the ordinary irrational RoPE
    schedule unless that schedule has first been replaced by this declared
    rational turn ratio.
    """
    if numerator < 0:
        raise ValueError("numerator must be nonnegative")
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if context_length <= 0:
        raise ValueError("context_length must be positive")

    certified_margin = turn_ratio_nat_ratio_coprime_margin_certificate(
        numerator=numerator,
        denominator=denominator,
        context_length=context_length,
    )
    zero_margin_witness = turn_ratio_nat_ratio_zero_margin_witness(
        numerator=numerator,
        denominator=denominator,
        context_length=context_length,
    )
    pass_certificate = certified_margin is not None
    certificate_name = (
        name
        if name is not None
        else f"rational_turn_ratio_{numerator}_{denominator}_context_{context_length}"
    )
    theorem_ids: tuple[str, ...]
    lean_declarations: tuple[str, ...]
    if certificate_name == ROPE_RATIONAL_PRESET_4099_NAME and pass_certificate:
        theorem_ids = ROPE_RATIONAL_PRESET_4099_THEOREMS
        lean_declarations = ROPE_RATIONAL_PRESET_4099_LEAN_DECLARATIONS
    elif pass_certificate:
        theorem_ids = ("AIRA-T0056", "AIRA-T0057")
        lean_declarations = (
            "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den",
            "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_one_over_den_iff_context_le_den",
        )
    else:
        theorem_ids = ("AIRA-T0055", "AIRA-T0057")
        lean_declarations = (
            "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_iff_nonpos_of_den_lt_context",
            "Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_one_over_den_iff_context_le_den",
        )

    if pass_certificate:
        explanation = (
            "Lean proves this reduced rational turn ratio has finite-context "
            "nearest-integer margin 1/denominator because the inspected context "
            "does not reach the denominator return gap."
        )
    else:
        explanation = (
            "No positive rational finite-margin certificate is emitted: either "
            "the ratio is not reduced or the inspected context reaches the "
            "denominator return gap."
        )

    return TurnRatioFiniteMarginCertificate(
        schema_id="circle_calculus.rational_turn_ratio_finite_margin.v0",
        name=certificate_name,
        numerator=numerator,
        denominator=denominator,
        context_length=context_length,
        turn_ratio=numerator / denominator,
        certified_margin=certified_margin,
        pass_certificate=pass_certificate,
        zero_margin_witness=zero_margin_witness,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        explanation=explanation,
        claim_boundary=(
            "This is a theorem-backed rational/discretized turn-ratio certificate. "
            "It is not a proof of the standard irrational real RoPE schedule unless "
            "that schedule is explicitly replaced by the declared rational ratio."
        ),
    )


def certify_rational_preset_4099() -> TurnRatioFiniteMarginCertificate:
    """Return the named 4k rational/discretized finite-margin certificate."""
    return certify_rational_turn_ratio_finite_margin(
        numerator=1,
        denominator=4099,
        context_length=4096,
        name=ROPE_RATIONAL_PRESET_4099_NAME,
    )


def format_fraction(value: Fraction) -> str:
    """Format an exact rational for certificate JSON and Markdown output."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def standard_channel0_turn_ratio_bounds(
    *,
    pi_bound_preset: PiBoundPreset,
) -> tuple[Fraction, Fraction, str]:
    """Return exact rational bounds for the standard channel-0 turn ratio.

    The returned pair is ``lower <= 1/(2*pi) <= upper`` as exact ``Fraction``
    objects derived from the named mathlib-style decimal bounds on ``pi``.
    This helper emits executable planning data only; a Lean theorem must still
    be added before a generated plan is formal proof.
    """
    if pi_bound_preset == "d4":
        return (
            Fraction(5_000, 31_416),
            Fraction(5_000, 31_415),
            "3.1415 < pi and pi < 3.1416",
        )
    if pi_bound_preset == "d6":
        return (
            Fraction(500_000, 3_141_593),
            Fraction(500_000, 3_141_592),
            "3.141592 < pi and pi < 3.141593",
        )
    if pi_bound_preset == "d20":
        return (
            Fraction(10**20, 2 * 314_159_265_358_979_323_847),
            Fraction(10**20, 2 * 314_159_265_358_979_323_846),
            "3.14159265358979323846 < pi and pi < 3.14159265358979323847",
        )
    raise ValueError("pi_bound_preset must be one of: d4, d6, d20")


def _standard_channel0_interval_cell(
    *,
    gap: int,
    margin: Fraction,
    lower_turn_ratio_bound: Fraction,
    upper_turn_ratio_bound: Fraction,
) -> int | None:
    lower_value = gap * lower_turn_ratio_bound
    upper_value = gap * upper_turn_ratio_bound
    start_cell = _floor_fraction(lower_value)
    end_cell = _floor_fraction(upper_value)
    for cell in range(max(0, start_cell - 1), end_cell + 2):
        if (
            Fraction(cell, 1) + margin <= lower_value
            and upper_value <= Fraction(cell + 1, 1) - margin
        ):
            return cell
    return None


def _standard_channel0_interval_band_report(
    *,
    start_gap: int,
    end_gap: int,
    cell: int,
    margin: Fraction,
    lower_turn_ratio_bound: Fraction,
    upper_turn_ratio_bound: Fraction,
) -> StandardRoPEIntervalBandReport:
    start_lower = start_gap * lower_turn_ratio_bound
    end_upper = end_gap * upper_turn_ratio_bound
    endpoint_cell_margin_ok = (
        Fraction(cell, 1) + margin <= start_lower
        and end_upper <= Fraction(cell + 1, 1) - margin
    )
    return StandardRoPEIntervalBandReport(
        start_gap=start_gap,
        end_gap=end_gap,
        cell=cell,
        start_lower_value=format_fraction(start_lower),
        end_upper_value=format_fraction(end_upper),
        endpoint_cell_margin_ok=endpoint_cell_margin_ok,
    )


def plan_standard_channel0_interval_bands(
    *,
    pi_bound_preset: PiBoundPreset = "d6",
    margin: Fraction = Fraction(1, 1024),
    max_context_length: int = 4096,
) -> StandardRoPEIntervalPlan:
    """Plan exact rational interval bands for standard RoPE channel 0.

    This is a deterministic source-data generator for future Lean interval
    certificates. It does not mark the generated plan as proved. A plan covers
    context ``N`` exactly when every positive gap below ``N`` has a rational
    interval contained in one integer cell with the requested margin.
    """
    if margin < 0:
        raise ValueError("margin must be nonnegative")
    if max_context_length <= 1:
        raise ValueError("max_context_length must be greater than 1")

    lower, upper, pi_bounds = standard_channel0_turn_ratio_bounds(
        pi_bound_preset=pi_bound_preset,
    )
    bands: list[StandardRoPEIntervalBandReport] = []
    active_start: int | None = None
    active_end: int | None = None
    active_cell: int | None = None
    first_uncovered_gap: int | None = None

    for gap in range(1, max_context_length):
        cell = _standard_channel0_interval_cell(
            gap=gap,
            margin=margin,
            lower_turn_ratio_bound=lower,
            upper_turn_ratio_bound=upper,
        )
        if cell is None:
            first_uncovered_gap = gap
            break
        if active_cell is None:
            active_start = gap
            active_end = gap
            active_cell = cell
        elif cell == active_cell and active_end == gap - 1:
            active_end = gap
        else:
            bands.append(_standard_channel0_interval_band_report(
                start_gap=active_start or gap,
                end_gap=active_end or gap,
                cell=active_cell,
                margin=margin,
                lower_turn_ratio_bound=lower,
                upper_turn_ratio_bound=upper,
            ))
            active_start = gap
            active_end = gap
            active_cell = cell

    if active_cell is not None:
        bands.append(_standard_channel0_interval_band_report(
            start_gap=active_start or 1,
            end_gap=active_end or 1,
            cell=active_cell,
            margin=margin,
            lower_turn_ratio_bound=lower,
            upper_turn_ratio_bound=upper,
        ))

    context_length = first_uncovered_gap or max_context_length
    margin_text = format_fraction(margin)
    proven_d4_seed = (
        pi_bound_preset == "d4"
        and margin == Fraction(1, 512)
        and context_length == 333
        and first_uncovered_gap == 333
    )
    proven_d6_seed = (
        pi_bound_preset == "d6"
        and margin == Fraction(1, 1024)
        and context_length == 710
        and first_uncovered_gap == 710
    )
    proven_d20_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 131072)
        and context_length == 4096
        and first_uncovered_gap is None
    )
    proven_d20_tight_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 105000)
        and context_length == 4096
        and first_uncovered_gap is None
    )
    proven_d20_sharp_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104219)
        and context_length == 4096
        and first_uncovered_gap is None
    )
    proven_d20_8k_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104220)
        and context_length == 8192
        and first_uncovered_gap is None
    )
    proven_d20_8k_sharp_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104219)
        and context_length == 8192
        and first_uncovered_gap is None
    )
    proven_d20_16k_sharp_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104219)
        and context_length == 16384
        and first_uncovered_gap is None
    )
    proven_d20_32k_sharp_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104219)
        and context_length == 32768
        and first_uncovered_gap is None
    )
    proven_d20_64k_sharp_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 104219)
        and context_length == 65536
        and first_uncovered_gap is None
    )
    proven_d20_128k_d17_seed = (
        pi_bound_preset == "d20"
        and margin == Fraction(1, 328459)
        and context_length == 131072
        and first_uncovered_gap is None
    )
    return StandardRoPEIntervalPlan(
        schema_id="circle_calculus.standard_rope_interval_plan.v0",
        name=(
            f"standard_rope_channel0_interval_plan_{pi_bound_preset}_"
            f"margin_{margin.numerator}_{margin.denominator}_context_{context_length}"
        ),
        turn_ratio_expression="1/(2*pi)",
        context_length=context_length,
        planned_margin=margin_text,
        pi_bound_preset=pi_bound_preset,
        pi_bounds=pi_bounds,
        lower_turn_ratio_bound=format_fraction(lower),
        upper_turn_ratio_bound=format_fraction(upper),
        pass_plan=bool(bands),
        first_uncovered_gap=first_uncovered_gap,
        band_count=len(bands),
        bands=tuple(bands),
        theorem_status=(
            "lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089"
            if proven_d4_seed
            else "lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094"
            if proven_d6_seed
            else "lean_proved_interval_seed_AIRA-T0097_to_AIRA-T0101"
            if proven_d20_seed
            else "lean_proved_interval_seed_AIRA-T0105_to_AIRA-T0108"
            if proven_d20_tight_seed
            else "lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114"
            if proven_d20_sharp_seed
            else "lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122"
            if proven_d20_8k_seed
            else "lean_proved_interval_seed_AIRA-T0127_to_AIRA-T0129"
            if proven_d20_8k_sharp_seed
            else "lean_proved_interval_seed_AIRA-T0133_to_AIRA-T0135"
            if proven_d20_16k_sharp_seed
            else "lean_proved_interval_seed_AIRA-T0142_to_AIRA-T0144"
            if proven_d20_32k_sharp_seed
            else "lean_proved_interval_seed_AIRA-T0148_to_AIRA-T0150"
            if proven_d20_64k_sharp_seed
            else "lean_proved_interval_seed_AIRA-T0156_to_AIRA-T0158"
            if proven_d20_128k_d17_seed
            else "candidate_plan_not_lean_proved"
        ),
        explanation=(
            "This exact-rational plan groups positive gaps into integer-cell "
            "bands for a Lean interval certificate. The d4 margin-1/512 "
            "context-333 plan, d6 margin-1/1024 context-710 plan, and d20 "
            "margin-1/131072, margin-1/105000, and margin-1/104219 context-4096 "
            "plans plus the d20 margin-1/104220 and margin-1/104219 context-8192 "
            "plans and the margin-1/104219 context-16384, context-32768, and "
            "context-65536 plans plus the margin-1/328459 context-131072 plan have now "
            "been converted into compiled Lean declarations; other generated "
            "plans remain source data until matching declarations compile and "
            "manifest ids are marked proved."
        ),
        claim_boundary=(
            "Interval-plan data only unless theorem_status names a compiled Lean "
            "seed. Even the proved seed is not a model-quality claim, large-context "
            "bank claim, speed claim, or deployment claim."
        ),
    )


def audit_standard_channel0_rational_band_certificate(
    plan: StandardRoPEIntervalPlan,
    *,
    requested_context_length: int | None = None,
) -> StandardRoPERationalBandCertificateAudit:
    """Audit whether a generated rational-band plan covers a request.

    This is an executable source-data check for the generic Lean compression
    bridge. It checks the finite band list shape and endpoint inequalities; it
    does not turn a generated list into a theorem-backed certificate by itself.
    """
    requested_context = (
        plan.context_length
        if requested_context_length is None
        else requested_context_length
    )
    if requested_context <= 1:
        raise ValueError("requested_context_length must be greater than 1")

    bands = plan.bands
    first_covered_gap = bands[0].start_gap if bands else None
    last_covered_gap = bands[-1].end_gap if bands else None
    valid_band_count = 0
    expected_start = 1
    contiguous_from_one = bool(bands) and first_covered_gap == 1
    bridge_ids = {band.bridge_theorem_id for band in bands}

    for band in bands:
        range_ok = 0 < band.start_gap <= band.end_gap
        contiguous_from_one = (
            contiguous_from_one and band.start_gap == expected_start
        )
        if range_ok and band.endpoint_cell_margin_ok:
            valid_band_count += 1
        expected_start = band.end_gap + 1

    endpoint_validity_pass = bool(bands) and valid_band_count == len(bands)
    certified_context_length = (
        (last_covered_gap or 0) + 1 if contiguous_from_one else 1
    )
    covered_gap_count = (
        last_covered_gap or 0
        if contiguous_from_one
        else sum(max(0, band.end_gap - band.start_gap + 1) for band in bands)
    )
    coverage_pass = requested_context <= certified_context_length
    first_uncovered_gap = None if coverage_pass else certified_context_length
    pass_audit = endpoint_validity_pass and coverage_pass
    bridge_text = ", ".join(
        tuple(sorted(bridge_ids)) + ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS
    )

    if coverage_pass:
        coverage_sentence = (
            f"covers every positive gap below requested context {requested_context}"
        )
    else:
        coverage_sentence = (
            f"stops before requested context {requested_context}; first uncovered "
            f"gap is {first_uncovered_gap}"
        )

    return StandardRoPERationalBandCertificateAudit(
        schema_id="circle_calculus.standard_rope_rational_band_certificate_audit.v0",
        name=f"{plan.name}_requested_context_{requested_context}_band_audit",
        source_plan_name=plan.name,
        requested_context_length=requested_context,
        certified_context_length=certified_context_length,
        planned_margin=plan.planned_margin,
        pi_bound_preset=plan.pi_bound_preset,
        lower_turn_ratio_bound=plan.lower_turn_ratio_bound,
        upper_turn_ratio_bound=plan.upper_turn_ratio_bound,
        band_count=len(bands),
        valid_band_count=valid_band_count,
        covered_gap_count=covered_gap_count,
        first_covered_gap=first_covered_gap,
        last_covered_gap=last_covered_gap,
        first_uncovered_gap=first_uncovered_gap,
        contiguous_from_one=contiguous_from_one,
        endpoint_validity_pass=endpoint_validity_pass,
        coverage_pass=coverage_pass,
        pass_audit=pass_audit,
        theorem_ids=ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_THEOREMS,
        lean_declarations=ROPE_STANDARD_CHANNEL0_INTERVAL_COMPRESSION_LEAN_DECLARATIONS,
        theorem_status="executable_band_audit_not_lean_proved",
        explanation=(
            f"The audit checks {len(bands)} generated rational interval bands "
            "for positive ordered gap ranges, contiguity from gap 1, endpoint-cell "
            f"margin inequalities, and requested-context coverage. It {coverage_sentence}. "
            f"The relevant generic bridge ids are {bridge_text}."
        ),
        claim_boundary=(
            "Executable source-data audit only. The listed Lean declarations are "
            "generic compression bridges; this row is not a generated Lean "
            "certificate for the band list unless a matching theorem id is added "
            "to the manifest and compiled by lake build."
        ),
    )


def certify_standard_channel0_interval_seed() -> IntervalBackedTurnRatioCertificate:
    """Return the strongest named theorem-backed interval seed for standard RoPE.

    The Lean theorem proves a finite witness table for the genuine channel-0
    turn ratio ``1 / (2π)`` over the context containing gaps 1 through 131071.
    The certificate uses 20-decimal bounds on ``π`` and a computed integer
    cell table. The earlier d6 seed proves why context 710 cannot keep margin
    1/1024. The D9/D10/D11 trail also proves that gap 710 obstructs the
    doubled D9 margin 1/65536, the nearby larger D10 margin 1/104000, and the
    adjacent larger D11 margin 1/104218. D13 extends the sharp margin
    1/104219 to context 8192, D14 extends it to context 16384, and the
    generated D15/D16 compressed certificates extend it to contexts 32768 and
    65536. D17 lowers the advertised margin to 1/328459 and extends the
    theorem-backed channel-0 seed through context 131072.
    """
    context_length = 131072
    margin = Fraction(1, 328459)
    lower_turn_ratio_bound, upper_turn_ratio_bound, _pi_bounds = (
        standard_channel0_turn_ratio_bounds(pi_bound_preset="d20")
    )
    witnesses: list[RationalIntervalWitnessReport] = []
    for gap in range(1, context_length):
        lower = gap * lower_turn_ratio_bound
        upper = gap * upper_turn_ratio_bound
        cell = _standard_channel0_interval_cell(
            gap=gap,
            margin=margin,
            lower_turn_ratio_bound=lower_turn_ratio_bound,
            upper_turn_ratio_bound=upper_turn_ratio_bound,
        )
        if cell is None:
            raise AssertionError("standard channel-0 seed witness table is incomplete")
        if not (
            Fraction(cell, 1) + margin <= lower
            and upper <= Fraction(cell + 1, 1) - margin
        ):
            raise AssertionError("standard channel-0 seed witness table is invalid")
        witnesses.append(
            RationalIntervalWitnessReport(
                gap=gap,
                lower=format_fraction(lower),
                upper=format_fraction(upper),
                cell=cell,
            )
        )

    return IntervalBackedTurnRatioCertificate(
        schema_id="circle_calculus.standard_rope_interval_margin.v0",
        name=ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_NAME,
        turn_ratio_expression="1/(2*pi)",
        context_length=context_length,
        certified_margin=format_fraction(margin),
        pass_certificate=True,
        pi_bounds=(
            "pi <= 4, 3.14 < pi, pi < 3.15, 3.1415 < pi, pi < 3.1416, "
            "3.141592 < pi, pi < 3.141593, "
            "3.14159265358979323846 < pi, and pi < 3.14159265358979323847"
        ),
        interval_witnesses=tuple(witnesses),
        theorem_ids=ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_THEOREMS,
        lean_declarations=ROPE_STANDARD_CHANNEL0_INTERVAL_SEED_LEAN_DECLARATIONS,
        explanation=(
            "Lean proves that standard RoPE channel 0, with turn ratio 1/(2*pi), "
            "has finite nearest-integer margin 1/328459 for gaps 1 through 131071. "
            "The generated D17 compressed certificate uses the 20-decimal enclosure "
            "10^20*gap/628318530717958647694 <= gap/(2*pi) <= "
            "10^20*gap/628318530717958647692, split across computed integer "
            "cells 0 through 20860. Lean also proves that the earlier 1/1024 "
            "margin stops at gap 710, and that margins 1/65536, 1/104000, and 1/104218 "
            "are already impossible for any context containing that gap. Lean further packages the D11 "
            "result as a 4k bracket: 1/104219 is proved, while every margin at or above "
            "1/104218 is impossible for context 4096. The theorem trail includes the "
            "weaker D12 8k one-channel seed at margin 1/104220, the sharper D13 "
            "8k seed at margin 1/104219, the D14 16k seed, and generated D15/D16 "
            "32k and 64k seeds at the same margin. D17 lowers the certified "
            "margin to 1/328459 for the 128k context; the adjacent larger "
            "margin 1/328458 is impossible once gap 103993 is in scope. "
            "D16 and D17 package their corresponding brackets and add "
            "bank-level bridges for banks containing the standard channel-0 angular "
            "frequency and for banks whose first channel is that standard frequency. "
            "The newest compressed certificates use the rational-band and "
            "endpoint-reflection bridges to avoid per-gap interval-case expansions."
        ),
        claim_boundary=(
            "This is a theorem-backed interval certificate for the genuine standard "
            "RoPE channel-0 turn ratio over context 131072, plus conditional "
            "one-separating-channel bank bridges. It is not a proof that every "
            "standard RoPE channel has a large-context margin, and it does not "
            "certify a full all-channel standard-RoPE bank."
        ),
    )


def scan_turn_ratio_finite_margin(
    *,
    turn_ratio: float,
    context_length: int,
) -> tuple[float, int | None, int | None]:
    """Numerically scan the finite-context nearest-integer margin.

    Returns ``(margin, gap, turns)`` for positive gaps below ``context_length``.
    This is an executable mirror of the finite-margin predicate shape; it is
    not a formal proof of that predicate for a real-valued turn ratio.
    """
    if context_length <= 1:
        return float("inf"), None, None
    best_margin = float("inf")
    best_gap: int | None = None
    best_turns: int | None = None
    for gap in turn_ratio_finite_margin_gap_candidates(context_length=context_length):
        nearest_turn = int(floor(gap * turn_ratio + 0.5))
        for turns in (nearest_turn - 1, nearest_turn, nearest_turn + 1):
            margin = turn_ratio_nearest_integer_error(
                turn_ratio=turn_ratio,
                gap=gap,
                turns=turns,
            )
            if margin < best_margin:
                best_margin = margin
                best_gap = gap
                best_turns = turns
    return best_margin, best_gap, best_turns


def turn_ratio_margin_covers_context(
    *,
    certified_context: int,
    requested_context: int,
) -> bool:
    """Return whether a finite-margin scan horizon covers a requested context.

    This mirrors the Lean monotonicity theorem: a margin certified over a
    larger context applies to any smaller requested context. It does not prove
    that the margin itself is formal for a real RoPE ratio.
    """
    if certified_context <= 0:
        raise ValueError("certified_context must be positive")
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    return requested_context <= certified_context


def turn_ratio_margin_covers_margin(
    *,
    certified_margin: float,
    requested_margin: float,
) -> bool:
    """Return whether a certified lower bound covers a requested lower bound."""
    if certified_margin < 0:
        raise ValueError("certified_margin must be nonnegative")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")
    return requested_margin <= certified_margin


def turn_ratio_margin_covers_request(
    *,
    certified_context: int,
    requested_context: int,
    certified_margin: float,
    requested_margin: float,
) -> bool:
    """Return whether one finite-margin certificate covers a request.

    This mirrors the bank-level Lean transfer theorem: a stronger certificate
    with a larger horizon and larger lower bound may be reused for a smaller
    context and a conservative reported margin. It still does not prove that
    the real RoPE turn ratio has the certified margin.
    """
    return turn_ratio_margin_covers_context(
        certified_context=certified_context,
        requested_context=requested_context,
    ) and turn_ratio_margin_covers_margin(
        certified_margin=certified_margin,
        requested_margin=requested_margin,
    )


def certify_standard_channel0_d12_bank_request(
    *,
    requested_context: int,
    requested_margin: Fraction = Fraction(1, 104220),
    first_channel_shape: bool = True,
) -> StandardChannel0D12BankBridgeCertificate:
    """Certify whether a request is inside the D12 standard-channel bank bridge.

    The result packages the Lean theorem trail for the conditional
    one-separating-channel bank certificate. It checks only the exact request
    inequalities exposed by the D12 transfer theorem: the requested context must
    be no larger than 8192, and the requested margin must be no larger than
    1/104220. It does not prove that every channel in a standard RoPE bank has a
    margin, and it does not say anything about model quality.
    """
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")

    certified_context = 8192
    certified_margin = Fraction(1, 104220)
    context_ok = requested_context <= certified_context
    margin_ok = requested_margin <= certified_margin
    pass_certificate = context_ok and margin_ok
    if not context_ok:
        failure_reason = "requested_context_exceeds_d12_seed"
    elif not margin_ok:
        failure_reason = "requested_margin_exceeds_d12_seed"
    else:
        failure_reason = None

    if first_channel_shape:
        theorem_ids = ROPE_STANDARD_CHANNEL0_D12_BANK_BRIDGE_THEOREMS
        lean_declarations = ROPE_STANDARD_CHANNEL0_D12_BANK_BRIDGE_LEAN_DECLARATIONS
        bank_shape = "standard_channel0_first"
        assumptions = (
            "The finite real-phase bank has standard channel 0 as its first channel.",
            "The requested context is at most 8192.",
            "The requested margin is at most 1/104220.",
        )
    else:
        theorem_ids = ("AIRA-T0123",)
        lean_declarations = (
            "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed",
        )
        bank_shape = "contains_standard_channel0"
        assumptions = (
            "The finite real-phase bank contains the standard channel-0 angular frequency.",
            "The requested context is at most 8192.",
            "The requested margin is at most 1/104220.",
        )

    return StandardChannel0D12BankBridgeCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d12_bank_bridge.v0",
        name="standard_rope_channel0_d12_bank_bridge_request",
        requested_context=requested_context,
        requested_margin=format_fraction(requested_margin),
        certified_context=certified_context,
        certified_margin=format_fraction(certified_margin),
        pass_certificate=pass_certificate,
        failure_reason=failure_reason,
        bank_shape=bank_shape,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        assumptions=assumptions,
        tolerance_rule="Lean conclusion applies when tolerance < fullTurn * requestedMargin.",
        explanation=(
            "This request is inside the D12 standard-channel bank bridge."
            if pass_certificate
            else "This request is outside the D12 standard-channel bank bridge."
        ),
        claim_boundary=(
            "This is a conditional one-separating-channel bank certificate based on "
            "standard channel 0. It is not a full all-channel standard-RoPE margin "
            "theorem, not a 128k certificate, and not a model-quality claim."
        ),
    )


def certify_standard_channel0_d12_margin_bracket() -> StandardChannel0D12MarginBracketCertificate:
    """Return the theorem-backed 8k standard-channel margin bracket.

    This packages the positive D12 seed together with the existing gap-710
    obstruction. It says exactly what Lean proves for the standard channel-0
    turn ratio: margin ``1/104220`` holds through context 8192, while every
    advertised margin at or above ``1/104218`` is impossible for that same
    context. The tiny gap between those rationals is intentionally left as a
    claim boundary unless a sharper proof is added.
    """

    return StandardChannel0D12MarginBracketCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d12_margin_bracket.v0",
        name="standard_rope_channel0_d12_context8192_margin_bracket",
        context_length=8192,
        proved_margin="1/104220",
        impossible_margin_floor="1/104218",
        pass_certificate=True,
        theorem_ids=("AIRA-T0120", "AIRA-T0121", "AIRA-T0118", "AIRA-T0125"),
        lean_declarations=(
            "Circle.Applications.ropeStandardChannel0D12Seed_intervalCertificate",
            "Circle.Applications.ropeStandardChannel0D12Seed_turnRatioFiniteMargin",
            "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
            "Circle.Applications.ropeStandardChannel0D12_context8192_margin_bracket",
        ),
        explanation=(
            "Lean proves that standard RoPE channel 0 has finite-context "
            "nearest-integer margin 1/104220 through context 8192. Lean also "
            "proves that any margin at or above 1/104218 is impossible for "
            "that context because gap 710 is already too close to integer turn 113."
        ),
        claim_boundary=(
            "This is an 8k one-channel standard-RoPE bracket. It is not a full "
            "all-channel bank margin theorem, not a 128k certificate, and it "
            "does not decide margins strictly between 1/104220 and 1/104218."
        ),
    )


def certify_standard_channel0_d13_bank_request(
    *,
    requested_context: int,
    requested_margin: Fraction = Fraction(1, 104219),
    first_channel_shape: bool = True,
) -> StandardChannel0D13BankBridgeCertificate:
    """Certify whether a request is inside the D13 standard-channel bank bridge.

    The result packages the sharper D13 theorem trail for the conditional
    one-separating-channel bank certificate. It checks only the exact request
    inequalities exposed by the D13 transfer theorem: the requested context must
    be no larger than 8192, and the requested margin must be no larger than
    1/104219.
    """
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")

    certified_context = 8192
    certified_margin = Fraction(1, 104219)
    context_ok = requested_context <= certified_context
    margin_ok = requested_margin <= certified_margin
    pass_certificate = context_ok and margin_ok
    if not context_ok:
        failure_reason = "requested_context_exceeds_d13_seed"
    elif not margin_ok:
        failure_reason = "requested_margin_exceeds_d13_seed"
    else:
        failure_reason = None

    if first_channel_shape:
        theorem_ids = ROPE_STANDARD_CHANNEL0_D13_BANK_BRIDGE_THEOREMS
        lean_declarations = ROPE_STANDARD_CHANNEL0_D13_BANK_BRIDGE_LEAN_DECLARATIONS
        bank_shape = "standard_channel0_first"
        assumptions = (
            "The finite real-phase bank has standard channel 0 as its first channel.",
            "The requested context is at most 8192.",
            "The requested margin is at most 1/104219.",
        )
    else:
        theorem_ids = ("AIRA-T0130",)
        lean_declarations = (
            "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed",
        )
        bank_shape = "contains_standard_channel0"
        assumptions = (
            "The finite real-phase bank contains the standard channel-0 angular frequency.",
            "The requested context is at most 8192.",
            "The requested margin is at most 1/104219.",
        )

    return StandardChannel0D13BankBridgeCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d13_bank_bridge.v0",
        name="standard_rope_channel0_d13_bank_bridge_request",
        requested_context=requested_context,
        requested_margin=format_fraction(requested_margin),
        certified_context=certified_context,
        certified_margin=format_fraction(certified_margin),
        pass_certificate=pass_certificate,
        failure_reason=failure_reason,
        bank_shape=bank_shape,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        assumptions=assumptions,
        tolerance_rule="Lean conclusion applies when tolerance < fullTurn * requestedMargin.",
        explanation=(
            "This request is inside the D13 standard-channel bank bridge."
            if pass_certificate
            else "This request is outside the D13 standard-channel bank bridge."
        ),
        claim_boundary=(
            "This is a conditional one-separating-channel bank certificate based on "
            "standard channel 0. It is not a full all-channel standard-RoPE margin "
            "theorem, not a 128k certificate, and not a model-quality claim."
        ),
    )


def certify_standard_channel0_d13_margin_bracket() -> StandardChannel0D13MarginBracketCertificate:
    """Return the theorem-backed sharp 8k standard-channel margin bracket."""

    return StandardChannel0D13MarginBracketCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d13_margin_bracket.v0",
        name="standard_rope_channel0_d13_context8192_margin_bracket",
        context_length=8192,
        proved_margin="1/104219",
        impossible_margin_floor="1/104218",
        pass_certificate=True,
        theorem_ids=("AIRA-T0127", "AIRA-T0128", "AIRA-T0118", "AIRA-T0132"),
        lean_declarations=(
            "Circle.Applications.ropeStandardChannel0D13Seed_intervalCertificate",
            "Circle.Applications.ropeStandardChannel0D13Seed_turnRatioFiniteMargin",
            "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
            "Circle.Applications.ropeStandardChannel0D13_context8192_margin_bracket",
        ),
        explanation=(
            "Lean proves that standard RoPE channel 0 has finite-context "
            "nearest-integer margin 1/104219 through context 8192. Lean also "
            "proves that any margin at or above 1/104218 is impossible for "
            "that context because gap 710 is already too close to integer turn 113."
        ),
        claim_boundary=(
            "This is an 8k one-channel standard-RoPE bracket. It is not a full "
            "all-channel bank margin theorem, not a 128k certificate, and it "
            "does not decide margins strictly between 1/104219 and 1/104218."
        ),
    )


def certify_standard_channel0_d14_bank_request(
    *,
    requested_context: int,
    requested_margin: Fraction = Fraction(1, 104219),
    first_channel_shape: bool = True,
) -> StandardChannel0D14BankBridgeCertificate:
    """Certify whether a request is inside the D14 standard-channel bank bridge."""
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")

    certified_context = 16384
    certified_margin = Fraction(1, 104219)
    context_ok = requested_context <= certified_context
    margin_ok = requested_margin <= certified_margin
    pass_certificate = context_ok and margin_ok
    if not context_ok:
        failure_reason = "requested_context_exceeds_d14_seed"
    elif not margin_ok:
        failure_reason = "requested_margin_exceeds_d14_seed"
    else:
        failure_reason = None

    if first_channel_shape:
        theorem_ids = ROPE_STANDARD_CHANNEL0_D14_BANK_BRIDGE_THEOREMS
        lean_declarations = ROPE_STANDARD_CHANNEL0_D14_BANK_BRIDGE_LEAN_DECLARATIONS
        bank_shape = "standard_channel0_first"
        assumptions = (
            "The finite real-phase bank has standard channel 0 as its first channel.",
            "The requested context is at most 16384.",
            "The requested margin is at most 1/104219.",
        )
    else:
        theorem_ids = ("AIRA-T0136",)
        lean_declarations = (
            "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed",
        )
        bank_shape = "contains_standard_channel0"
        assumptions = (
            "The finite real-phase bank contains the standard channel-0 angular frequency.",
            "The requested context is at most 16384.",
            "The requested margin is at most 1/104219.",
        )

    return StandardChannel0D14BankBridgeCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d14_bank_bridge.v0",
        name="standard_rope_channel0_d14_bank_bridge_request",
        requested_context=requested_context,
        requested_margin=format_fraction(requested_margin),
        certified_context=certified_context,
        certified_margin=format_fraction(certified_margin),
        pass_certificate=pass_certificate,
        failure_reason=failure_reason,
        bank_shape=bank_shape,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        assumptions=assumptions,
        tolerance_rule="Lean conclusion applies when tolerance < fullTurn * requestedMargin.",
        explanation=(
            "This request is inside the D14 standard-channel bank bridge."
            if pass_certificate
            else "This request is outside the D14 standard-channel bank bridge."
        ),
        claim_boundary=(
            "This is a conditional one-separating-channel bank certificate based on "
            "standard channel 0. It is not a full all-channel standard-RoPE margin "
            "theorem, not a 128k certificate, and not a model-quality claim."
        ),
    )


def certify_standard_channel0_d14_margin_bracket() -> StandardChannel0D14MarginBracketCertificate:
    """Return the theorem-backed sharp 16k standard-channel margin bracket."""

    return StandardChannel0D14MarginBracketCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d14_margin_bracket.v0",
        name="standard_rope_channel0_d14_context16384_margin_bracket",
        context_length=16384,
        proved_margin="1/104219",
        impossible_margin_floor="1/104218",
        pass_certificate=True,
        theorem_ids=("AIRA-T0133", "AIRA-T0134", "AIRA-T0118", "AIRA-T0138"),
        lean_declarations=(
            "Circle.Applications.ropeStandardChannel0D14Seed_intervalCertificate",
            "Circle.Applications.ropeStandardChannel0D14Seed_turnRatioFiniteMargin",
            "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
            "Circle.Applications.ropeStandardChannel0D14_context16384_margin_bracket",
        ),
        explanation=(
            "Lean proves that standard RoPE channel 0 has finite-context "
            "nearest-integer margin 1/104219 through context 16384. Lean also "
            "proves that any margin at or above 1/104218 is impossible for "
            "that context because gap 710 is already too close to integer turn 113."
        ),
        claim_boundary=(
            "This is a 16k one-channel standard-RoPE bracket. It is not a full "
            "all-channel bank margin theorem, not a 128k certificate, and it "
            "does not decide margins strictly between 1/104219 and 1/104218."
        ),
    )


def certify_standard_channel0_d16_bank_request(
    *,
    requested_context: int,
    requested_margin: Fraction = Fraction(1, 104219),
    first_channel_shape: bool = True,
) -> StandardChannel0D16BankBridgeCertificate:
    """Certify whether a request is inside the D16 standard-channel bank bridge."""
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")

    certified_context = 65536
    certified_margin = Fraction(1, 104219)
    context_ok = requested_context <= certified_context
    margin_ok = requested_margin <= certified_margin
    pass_certificate = context_ok and margin_ok
    if not context_ok:
        failure_reason = "requested_context_exceeds_d16_seed"
    elif not margin_ok:
        failure_reason = "requested_margin_exceeds_d16_seed"
    else:
        failure_reason = None

    if first_channel_shape:
        theorem_ids = ROPE_STANDARD_CHANNEL0_D16_BANK_BRIDGE_THEOREMS
        lean_declarations = ROPE_STANDARD_CHANNEL0_D16_BANK_BRIDGE_LEAN_DECLARATIONS
        bank_shape = "standard_channel0_first"
        assumptions = (
            "The finite real-phase bank has standard channel 0 as its first channel.",
            "The requested context is at most 65536.",
            "The requested margin is at most 1/104219.",
        )
    else:
        theorem_ids = ("AIRA-T0151",)
        lean_declarations = (
            "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D16Seed",
        )
        bank_shape = "contains_standard_channel0"
        assumptions = (
            "The finite real-phase bank contains the standard channel-0 angular frequency.",
            "The requested context is at most 65536.",
            "The requested margin is at most 1/104219.",
        )

    return StandardChannel0D16BankBridgeCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d16_bank_bridge.v0",
        name="standard_rope_channel0_d16_bank_bridge_request",
        requested_context=requested_context,
        requested_margin=format_fraction(requested_margin),
        certified_context=certified_context,
        certified_margin=format_fraction(certified_margin),
        pass_certificate=pass_certificate,
        failure_reason=failure_reason,
        bank_shape=bank_shape,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        assumptions=assumptions,
        tolerance_rule="Lean conclusion applies when tolerance < fullTurn * requestedMargin.",
        explanation=(
            "This request is inside the D16 standard-channel bank bridge."
            if pass_certificate
            else "This request is outside the D16 standard-channel bank bridge."
        ),
        claim_boundary=(
            "This is a conditional one-separating-channel bank certificate based on "
            "standard channel 0. It is not a full all-channel standard-RoPE margin "
            "theorem, not a 128k certificate, and not a model-quality claim."
        ),
    )


def certify_standard_channel0_d16_margin_bracket() -> StandardChannel0D16MarginBracketCertificate:
    """Return the theorem-backed sharp 64k standard-channel margin bracket."""

    return StandardChannel0D16MarginBracketCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d16_margin_bracket.v0",
        name="standard_rope_channel0_d16_context65536_margin_bracket",
        context_length=65536,
        proved_margin="1/104219",
        impossible_margin_floor="1/104218",
        pass_certificate=True,
        theorem_ids=("AIRA-T0148", "AIRA-T0149", "AIRA-T0118", "AIRA-T0153"),
        lean_declarations=(
            "Circle.Applications.ropeStandardChannel0D16Seed_intervalCertificate",
            "Circle.Applications.ropeStandardChannel0D16Seed_turnRatioFiniteMargin",
            "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710",
            "Circle.Applications.ropeStandardChannel0D16_context65536_margin_bracket",
        ),
        explanation=(
            "Lean proves that standard RoPE channel 0 has finite-context "
            "nearest-integer margin 1/104219 through context 65536. Lean also "
            "proves that any margin at or above 1/104218 is impossible for "
            "that context because gap 710 is already too close to integer turn 113."
        ),
        claim_boundary=(
            "This is a 64k one-channel standard-RoPE bracket. It is not a full "
            "all-channel bank margin theorem, not a 128k certificate, and it "
            "does not decide margins strictly between 1/104219 and 1/104218."
        ),
    )


def certify_standard_channel0_d17_bank_request(
    *,
    requested_context: int,
    requested_margin: Fraction = Fraction(1, 328459),
    first_channel_shape: bool = True,
) -> StandardChannel0D17BankBridgeCertificate:
    """Certify whether a request is inside the D17 standard-channel bank bridge."""
    if requested_context <= 0:
        raise ValueError("requested_context must be positive")
    if requested_margin < 0:
        raise ValueError("requested_margin must be nonnegative")

    certified_context = 131072
    certified_margin = Fraction(1, 328459)
    context_ok = requested_context <= certified_context
    margin_ok = requested_margin <= certified_margin
    pass_certificate = context_ok and margin_ok
    if not context_ok:
        failure_reason = "requested_context_exceeds_d17_seed"
    elif not margin_ok:
        failure_reason = "requested_margin_exceeds_d17_seed"
    else:
        failure_reason = None

    if first_channel_shape:
        theorem_ids = ROPE_STANDARD_CHANNEL0_D17_BANK_BRIDGE_THEOREMS
        lean_declarations = ROPE_STANDARD_CHANNEL0_D17_BANK_BRIDGE_LEAN_DECLARATIONS
        bank_shape = "standard_channel0_first"
        assumptions = (
            "The finite real-phase bank has standard channel 0 as its first channel.",
            "The requested context is at most 131072.",
            "The requested margin is at most 1/328459.",
        )
    else:
        theorem_ids = ("AIRA-T0159",)
        lean_declarations = (
            "Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D17Seed",
        )
        bank_shape = "contains_standard_channel0"
        assumptions = (
            "The finite real-phase bank contains the standard channel-0 angular frequency.",
            "The requested context is at most 131072.",
            "The requested margin is at most 1/328459.",
        )

    return StandardChannel0D17BankBridgeCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d17_bank_bridge.v0",
        name="standard_rope_channel0_d17_bank_bridge_request",
        requested_context=requested_context,
        requested_margin=format_fraction(requested_margin),
        certified_context=certified_context,
        certified_margin=format_fraction(certified_margin),
        pass_certificate=pass_certificate,
        failure_reason=failure_reason,
        bank_shape=bank_shape,
        theorem_ids=theorem_ids,
        lean_declarations=lean_declarations,
        assumptions=assumptions,
        tolerance_rule="Lean conclusion applies when tolerance < fullTurn * requestedMargin.",
        explanation=(
            "This request is inside the D17 standard-channel bank bridge."
            if pass_certificate
            else "This request is outside the D17 standard-channel bank bridge."
        ),
        claim_boundary=(
            "This is a conditional one-separating-channel bank certificate based on "
            "standard channel 0. It is not a full all-channel standard-RoPE margin "
            "theorem and not a model-quality claim."
        ),
    )


def certify_standard_channel0_d17_margin_bracket() -> StandardChannel0D17MarginBracketCertificate:
    """Return the theorem-backed 128k standard-channel margin bracket."""

    return StandardChannel0D17MarginBracketCertificate(
        schema_id="circle_calculus.standard_rope_channel0_d17_margin_bracket.v0",
        name="standard_rope_channel0_d17_context131072_margin_bracket",
        context_length=131072,
        proved_margin="1/328459",
        impossible_margin_floor="1/328458",
        pass_certificate=True,
        theorem_ids=("AIRA-T0156", "AIRA-T0157", "AIRA-T0155", "AIRA-T0161"),
        lean_declarations=(
            "Circle.Applications.ropeStandardChannel0D17Seed_intervalCertificate",
            "Circle.Applications.ropeStandardChannel0D17Seed_turnRatioFiniteMargin",
            "Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_328458_of_context_gt_103993",
            "Circle.Applications.ropeStandardChannel0D17_context131072_margin_bracket",
        ),
        explanation=(
            "Lean proves that standard RoPE channel 0 has finite-context "
            "nearest-integer margin 1/328459 through context 131072. Lean also "
            "proves that any margin at or above 1/328458 is impossible for "
            "that context because gap 103993 is already too close to integer turn 16551."
        ),
        claim_boundary=(
            "This is a 128k one-channel standard-RoPE bracket. It is not a full "
            "all-channel bank margin theorem, and it does not decide margins "
            "strictly between 1/328459 and 1/328458."
        ),
    )


def real_phase_turn_separated(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    margin: float,
    turns: Iterable[int],
) -> bool:
    """Executable mirror of ``ropeRealPhaseTurnSeparated`` over sampled turns."""
    return all(
        margin
        <= real_phase_int_turn_error(
            frequency=frequency,
            full_turn=full_turn,
            left=left,
            right=right,
            turns=turn,
        )
        for turn in turns
    )


def real_phase_near_turn(
    *,
    frequency: float,
    full_turn: float,
    left: int,
    right: int,
    tolerance: float,
    turns: Iterable[int],
) -> bool:
    """Executable mirror of ``ropeRealPhaseNearTurn`` over sampled turns."""
    return any(
        real_phase_int_turn_error(
            frequency=frequency,
            full_turn=full_turn,
            left=left,
            right=right,
            turns=turn,
        )
        <= tolerance
        for turn in turns
    )


def real_phase_bank_near_turn(
    *,
    frequencies: Sequence[float],
    full_turn: float,
    left: int,
    right: int,
    tolerance: float,
    turns: Iterable[int],
) -> bool:
    """Mirror the all-channel ``ropeRealPhaseBankNearTurn`` predicate.

    The turn iterable is materialized once so generator inputs can be reused
    for each channel deterministically.
    """
    turn_values = tuple(turns)
    return all(
        real_phase_near_turn(
            frequency=frequency,
            full_turn=full_turn,
            left=left,
            right=right,
            tolerance=tolerance,
            turns=turn_values,
        )
        for frequency in frequencies
    )


def real_phase_bank_turn_separated(
    *,
    frequencies: Sequence[float],
    full_turn: float,
    left: int,
    right: int,
    margin: float,
    turns: Iterable[int],
) -> bool:
    """Mirror the existence-of-one-channel bank separation predicate."""
    turn_values = tuple(turns)
    return any(
        real_phase_turn_separated(
            frequency=frequency,
            full_turn=full_turn,
            left=left,
            right=right,
            margin=margin,
            turns=turn_values,
        )
        for frequency in frequencies
    )


def real_phase_best_margin_for_gap(frequencies: Sequence[float], gap: int) -> tuple[float, int]:
    """Return the strongest channel margin for a gap and the channel that attains it."""
    best_margin = -1.0
    best_index = -1
    for index, frequency in enumerate(frequencies):
        margin = circular_phase_distance(gap * frequency)
        if margin > best_margin:
            best_margin = margin
            best_index = index
    return best_margin, best_index


def scan_real_phase_margin(
    *,
    head_dim: int,
    base: float,
    context_length: int,
    tolerance: float,
    near_collision_limit: int = 10,
) -> RealPhaseMarginReport:
    """Numerically scan real RoPE channels for the weakest phase-bank margin."""
    frequencies = rope_angular_frequencies(head_dim, base)
    periods = rope_period_estimates(head_dim, base)
    if context_length <= 1:
        return RealPhaseMarginReport(
            pass_margin=True,
            tolerance=tolerance,
            worst_margin_radians=float("inf"),
            worst_gap=None,
            worst_channel_index=None,
            worst_channel_period_estimate=None,
            scanned_gap_count=0,
            near_collision_gaps=(),
            explanation="A context of length 1 has no unequal position pairs to compare.",
        )

    worst_margin = float("inf")
    worst_gap: int | None = None
    worst_index: int | None = None
    near: list[tuple[int, float]] = []
    for gap in range(1, context_length):
        margin, index = real_phase_best_margin_for_gap(frequencies, gap)
        if margin < worst_margin:
            worst_margin = margin
            worst_gap = gap
            worst_index = index
        if margin <= tolerance and len(near) < near_collision_limit:
            near.append((gap, margin))

    return RealPhaseMarginReport(
        pass_margin=worst_margin > tolerance,
        tolerance=tolerance,
        worst_margin_radians=worst_margin,
        worst_gap=worst_gap,
        worst_channel_index=worst_index,
        worst_channel_period_estimate=None if worst_index is None else periods[worst_index],
        scanned_gap_count=context_length - 1,
        near_collision_gaps=tuple(near),
        explanation=(
            "The numerical real-phase margin is the smallest, over all nonzero position "
            "gaps in the context, of the best channel's circular distance from a full-turn "
            "collision. It is not a Lean proof."
        ),
    )


def certify_rope_positions(config: RoPEConfig) -> RoPEPositionCertificate:
    validate_rope_config(config)
    real_periods = rope_period_estimates(config.head_dim, config.base)
    discrete_periods = discretize_rope_periods(real_periods, config.discretization)
    exact = certify_exact_discrete_phase_bank(
        discrete_periods,
        config.context_length,
        period_source="produced by the declared discretization policy",
    )
    margin = scan_real_phase_margin(
        head_dim=config.head_dim,
        base=config.base,
        context_length=config.context_length,
        tolerance=config.tolerance,
    )
    rational_preset = certify_rational_preset_4099()
    standard_interval_seed = certify_standard_channel0_interval_seed()
    proof_layers = (
        RoPEProofLayerReport(
            layer="exact_integer_period_phase_bank",
            status="PASS" if exact.pass_exact else "FAIL",
            theorem_backed=True,
            theorem_ids=ROPE_CERTIFIER_THEOREMS,
            lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
            explanation=(
                "The declared integer-period phase bank is checked by Lean-backed "
                "LCM/divisibility theorems. It applies to the discretized phase-bank "
                "model, not directly to irrational standard RoPE."
            ),
        ),
        RoPEProofLayerReport(
            layer="rational_discretized_finite_margin",
            status=(
                "AVAILABLE_NAMED_PRESET"
                if rational_preset.pass_certificate
                else "UNAVAILABLE"
            ),
            theorem_backed=True,
            theorem_ids=rational_preset.theorem_ids,
            lean_declarations=rational_preset.lean_declarations,
            explanation=(
                "The named 1/4099 context-4096 preset is a theorem-backed "
                "rational/discretized turn-ratio finite-margin certificate."
            ),
        ),
        RoPEProofLayerReport(
            layer="interval_backed_standard_rope",
            status=(
                "AVAILABLE_SEED_CONTEXT_131072"
                if standard_interval_seed.pass_certificate
                else "UNAVAILABLE"
            ),
            theorem_backed=True,
            theorem_ids=standard_interval_seed.theorem_ids,
            lean_declarations=standard_interval_seed.lean_declarations,
            explanation=(
                "The bracketed 128k genuine standard-RoPE interval seed certifies channel 0 "
                "with turn ratio 1/(2*pi), margin 1/328459, and context 131072; "
                "the same theorem trail refutes every advertised margin at or above "
                "1/328458 for that channel and context, and D17 one-separating-channel bank bridges "
                "carry the one-channel separator into finite banks that contain standard channel 0."
            ),
        ),
        RoPEProofLayerReport(
            layer="numerical_real_phase_scan",
            status="PASS" if margin.pass_margin else "WARN",
            theorem_backed=False,
            theorem_ids=margin.formal_precursor_theorem_ids,
            lean_declarations=margin.formal_precursor_lean_declarations,
            explanation=(
                "The floating-point scan is a diagnostic over the requested config. "
                "The listed Lean declarations are structural precursors; they do not "
                "turn this scan into a formal proof."
            ),
        ),
    )
    return RoPEPositionCertificate(
        schema_id="circle_calculus.rope_position_distinguishability.v0",
        config=config,
        exact_discrete=exact,
        real_phase_margin=margin,
        real_period_estimates=real_periods,
        proof_layers=proof_layers,
        theorem_ids=ROPE_CERTIFIER_THEOREMS,
        lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
    )


def certify_exact_discrete_phase_bank(
    periods: Sequence[int],
    context_length: int,
    *,
    period_source: str = "declared explicitly by the phase-bank config",
) -> ExactDiscreteRoPECertificate:
    config = PhaseBankConfig(periods=tuple(periods), context_length=context_length)
    validate_phase_bank_config(config)
    discrete_periods = config.periods
    collision_gap, reaches_context = capped_lcm(discrete_periods, context_length)
    single_period_counts = tuple(
        single_period_collision_pair_count(context_length, period)
        for period in discrete_periods
    )
    prefix_reports = phase_bank_prefix_collision_reports(
        context_length,
        discrete_periods,
    )
    first_pass_prefix = next(
        (report.prefix_length for report in prefix_reports if report.lcm_reaches_context),
        None,
    )
    subfamily_reports = phase_bank_subfamily_pass_reports(
        context_length,
        discrete_periods,
    )
    smallest_subfamily = (
        None
        if not subfamily_reports
        else min(len(report.subfamily_indices) for report in subfamily_reports)
    )
    exact_pass = reaches_context
    guaranteed_pair_count = 0 if reaches_context else collision_pair_count_at_gap(
        context_length,
        collision_gap,
    )
    guaranteed_multiple_pair_count = 0 if reaches_context else collision_pair_count_at_gap_multiples(
        context_length,
        collision_gap,
    )
    return ExactDiscreteRoPECertificate(
        pass_exact=exact_pass,
        theorem_ids=ROPE_CERTIFIER_THEOREMS,
        lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
        discretized_periods=discrete_periods,
        period_count=len(discrete_periods),
        single_period_collision_pair_counts=single_period_counts,
        prefix_collision_reports=prefix_reports,
        first_exact_pass_prefix_length=first_pass_prefix,
        subfamily_pass_reports=subfamily_reports,
        smallest_pass_subfamily_size=smallest_subfamily,
        context_length=context_length,
        common_collision_gap=None if reaches_context else collision_gap,
        common_collision_gap_reaches_context=reaches_context,
        guaranteed_common_gap_collision_pair_count=guaranteed_pair_count,
        guaranteed_common_gap_multiple_pair_count=guaranteed_multiple_pair_count,
        total_bank_collision_pair_count=guaranteed_multiple_pair_count,
        sample_collision_pairs=sample_collision_pairs(context_length, collision_gap),
        assumptions=(
            "Positions are natural numbers in [0, context_length).",
            f"Each channel period is a positive integer {period_source}.",
            "Exact discrete collision means equal residues in every declared period channel.",
            "Lean theorem AIRA-T0024 characterizes all-channel collision by divisibility of the position gap.",
            "Lean theorem AIRA-T0025 characterizes bank distinguishability by at least one non-dividing period.",
            "Lean theorem AIRA-T0028 certifies every counted start at the common collision gap as an all-channel collision.",
            "Lean theorem AIRA-T0034 extends that guarantee to every positive in-context multiple of the common collision gap.",
            "Lean theorem AIRA-T0035 proves that every unequal single-channel collision has a positive period-multiple gap.",
            "Lean theorem AIRA-T0036 proves all-channel bank collision is equivalent to divisibility by the period-bank LCM, making the bank collision count total for the integer-period model. AIRA-T0046 proves that if the LCM reaches the inspected context, no unequal in-context all-channel collision exists. AIRA-T0048 and AIRA-T0049 prove the fail side: starts at the LCM gap collide, and a positive LCM below context yields an explicit unequal collision witness.",
            "Prefix collision reports apply the same AIRA-T0036/AIRA-T0046/AIRA-T0048/AIRA-T0049 LCM theorem spine to bounded channel prefixes so engineers can see when a smaller declared sub-bank already distinguishes the inspected context; AIRA-T0051 proves that adding suffix channels cannot create an unequal collision once the prefix LCM reaches the context. Subfamily reports use AIRA-T0052 for the unordered selected-subbank version.",
        ),
        explanation=(
            "PASS: the common exact collision gap is at least the context length, so no two unequal "
            "positions inside the inspected context collide in every discrete channel."
            if exact_pass
            else "FAIL: the common exact collision gap is inside the context, so the listed sample "
            "pairs collide in every discrete channel under the declared integer-period model."
        ),
    )


def certify_phase_bank_positions(config: PhaseBankConfig) -> PhaseBankPositionCertificate:
    validate_phase_bank_config(config)
    exact = certify_exact_discrete_phase_bank(
        config.periods,
        config.context_length,
    )
    return PhaseBankPositionCertificate(
        schema_id="circle_calculus.integer_phase_bank_distinguishability.v0",
        config=config,
        exact_discrete=exact,
        theorem_ids=ROPE_CERTIFIER_THEOREMS,
        lean_declarations=ROPE_CERTIFIER_LEAN_DECLARATIONS,
    )


def certificate_summary_lines(certificate: RoPEPositionCertificate) -> tuple[str, ...]:
    config = certificate.config
    exact = certificate.exact_discrete
    margin = certificate.real_phase_margin
    exact_status = "PASS" if exact.pass_exact else "FAIL"
    margin_status = "PASS" if margin.pass_margin else "WARN"
    gap = ">= context" if exact.common_collision_gap is None else str(exact.common_collision_gap)
    first_prefix = (
        "none"
        if exact.first_exact_pass_prefix_length is None
        else str(exact.first_exact_pass_prefix_length)
    )
    smallest_subfamily = (
        "none"
        if exact.smallest_pass_subfamily_size is None
        else str(exact.smallest_pass_subfamily_size)
    )
    worst_gap = "none" if margin.worst_gap is None else str(margin.worst_gap)
    worst_margin = (
        "inf"
        if margin.worst_margin_radians == float("inf")
        else f"{margin.worst_margin_radians:.12g}"
    )
    return (
        "RoPE position distinguishability certificate",
        f"config: head_dim={config.head_dim} base={config.base:g} context={config.context_length} "
        f"tolerance={config.tolerance:g} discretization={config.discretization}",
        "proof_layers="
        + ",".join(f"{layer.layer}:{layer.status}" for layer in certificate.proof_layers),
        f"exact_discrete_contract={exact_status} common_collision_gap={gap} "
        f"period_count={exact.period_count} "
        f"guaranteed_common_gap_collision_pair_count={exact.guaranteed_common_gap_collision_pair_count} "
        f"guaranteed_common_gap_multiple_pair_count={exact.guaranteed_common_gap_multiple_pair_count} "
        f"total_bank_collision_pair_count={exact.total_bank_collision_pair_count}",
        f"prefix_collision_reports={len(exact.prefix_collision_reports)} "
        f"first_exact_pass_prefix_length={first_prefix}",
        f"subfamily_pass_reports={len(exact.subfamily_pass_reports)} "
        f"smallest_pass_subfamily_size={smallest_subfamily}",
        f"real_phase_margin={margin_status} worst_margin_radians={worst_margin} "
        f"worst_gap={worst_gap} scanned_gaps={margin.scanned_gap_count}",
        f"real_phase_formal_precursors={','.join(margin.formal_precursor_theorem_ids)} "
        "(unwrapped, signed full-turn, turn-separation, bank-level no-near-turn, "
        "turn-ratio scaling, finite-context margin consequence, context-plus-margin transfer, "
        "integer/rational-turn-ratio guardrails, positive rational finite-context "
        "certificate and exact rational boundary, generated-gap enumeration, and "
        "floor/ceiling nearest-integer plus band-endpoint and band-list compression "
        "bridge precursors only; not a Diophantine proof)",
        f"theorem_ids={','.join(certificate.theorem_ids)}",
        certificate.claim_boundary,
    )


def phase_bank_certificate_summary_lines(
    certificate: PhaseBankPositionCertificate,
) -> tuple[str, ...]:
    config = certificate.config
    exact = certificate.exact_discrete
    exact_status = "PASS" if exact.pass_exact else "FAIL"
    gap = ">= context" if exact.common_collision_gap is None else str(exact.common_collision_gap)
    first_prefix = (
        "none"
        if exact.first_exact_pass_prefix_length is None
        else str(exact.first_exact_pass_prefix_length)
    )
    smallest_subfamily = (
        "none"
        if exact.smallest_pass_subfamily_size is None
        else str(exact.smallest_pass_subfamily_size)
    )
    return (
        "Integer phase-bank position distinguishability certificate",
        f"config: periods={','.join(str(period) for period in config.periods)} "
        f"context={config.context_length}",
        f"exact_discrete_contract={exact_status} common_collision_gap={gap} "
        f"period_count={exact.period_count} "
        f"guaranteed_common_gap_collision_pair_count={exact.guaranteed_common_gap_collision_pair_count} "
        f"guaranteed_common_gap_multiple_pair_count={exact.guaranteed_common_gap_multiple_pair_count} "
        f"total_bank_collision_pair_count={exact.total_bank_collision_pair_count}",
        f"prefix_collision_reports={len(exact.prefix_collision_reports)} "
        f"first_exact_pass_prefix_length={first_prefix}",
        f"subfamily_pass_reports={len(exact.subfamily_pass_reports)} "
        f"smallest_pass_subfamily_size={smallest_subfamily}",
        f"theorem_ids={','.join(certificate.theorem_ids)}",
        certificate.claim_boundary,
    )
