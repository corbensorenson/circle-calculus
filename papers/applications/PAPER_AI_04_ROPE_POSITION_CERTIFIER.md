# Circle Calculus AI 4: Proof-Carrying RoPE Position Distinguishability

Status: draft with proved exact discretized RoPE-bank collision criteria, rational/discretized finite-margin certificate, bounded standard-RoPE channel-0 interval seeds, a conditional bank bridge, and a public Python certifier.

## Purpose

This paper ships the first externally usable Circle Calculus AI contract: a RoPE position-distinguishability certifier that a non-Lean ML engineer can run against a rotary-position configuration.

The key separation is:

- **formal certificate:** exact integer-period/discretized phase-bank distinguishability;
- **finite-margin certificates:** a rational/discretized `1/4099` preset, bounded standard-RoPE channel-0 interval seeds, and a conditional bank bridge when channel 0 is present;
- **numerical diagnostic:** real-valued RoPE phase-margin scan;
- **out of scope:** claims about model quality, context-length improvement, perplexity, speed, memory, training stability, or deployment readiness.

Real RoPE channels rotate by real-valued angles. Exact collision in real arithmetic is usually not the right engineering object. The proof-backed contract here starts with the model that can be stated exactly: each channel has a positive integer period, and a position is visible as a residue modulo that period.

## Source Trail

Lean proof source:

```text
Circle/Applications/RoPECertifier.lean
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/lean/PaperAI04.lean
```

Python certifier source:

```text
circle_math/applications/rope_certifier.py
scripts/rope_certify.py
scripts/phase_bank_certify.py
tests/test_rope_certifier.py
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md
docs/ROPE_CERTIFIER_QUICKSTART.md
```

Lean declarations determine proof status. The theorem manifest is the proof-status source of truth. Python output is an executable certificate report for the declared model; it does not replace Lean proof status.

## Theorem Spine

- `AIRA-T0021`: `Circle.Applications.ropeDiscreteCollision_iff_gap_dvd`
- `AIRA-T0022`: `Circle.Applications.ropeDiscreteDistinguishable_iff_not_gap_dvd`
- `AIRA-T0023`: `Circle.Applications.ropeDiscreteCollision_iff_eq_on_context`
- `AIRA-T0024`: `Circle.Applications.ropePhaseBankCollision_iff_forall_gap_dvd`
- `AIRA-T0025`: `Circle.Applications.ropePhaseBankDistinguishable_iff_exists_not_gap_dvd`
- `AIRA-T0026`: `Circle.Applications.ropePhaseBankDistinguishable_of_period_ge_context`
- `AIRA-T0027`: `Circle.Applications.ropeCollisionPairCountAtGap_pos_iff`
- `AIRA-T0028`: `Circle.Applications.ropePhaseBankCollision_at_gap_of_forall_dvd`
- `AIRA-T0034`: `Circle.Applications.ropePhaseBankCollision_at_commonGap_mul_of_forall_dvd`
- `AIRA-T0035`: `Circle.Applications.ropeDiscreteCollision_exists_positive_multiple_gap`
- `AIRA-T0036`: `Circle.Applications.ropePhaseBankCollision_iff_lcm_dvd_gap`
- `AIRA-T0046`: `Circle.Applications.not_ropePhaseBankCollision_of_lcm_ge_context`
- `AIRA-T0048`: `Circle.Applications.ropePhaseBankCollision_at_lcm_gap`
- `AIRA-T0049`: `Circle.Applications.ropePhaseBankCollision_exists_of_lcm_pos_lt_context`
- `AIRA-T0051`: `Circle.Applications.not_ropePhaseBankCollision_of_prefix_lcm_ge_context`
- `AIRA-T0052`: `Circle.Applications.not_ropePhaseBankCollision_of_subbank_lcm_ge_context`
- `AIRA-T0029`: `Circle.Applications.ropeRealPhaseGapAbs_eq_natGap_mul_abs`
- `AIRA-T0030`: `Circle.Applications.ropeRealPhaseGapAbs_ge_minGap_mul_lower`
- `AIRA-T0031`: `Circle.Applications.ropeRealPhaseNatTurnEndpointErrors_ge_margin_of_one_turn_window`
- `AIRA-T0032`: `Circle.Applications.ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window`
- `AIRA-T0033`: `Circle.Applications.ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window`
- `AIRA-T0037`: `Circle.Applications.ropeRealPhaseTurnSeparated_of_one_turn_window`
- `AIRA-T0038`: `Circle.Applications.not_ropeRealPhaseNearTurn_of_turnSeparated_lt`
- `AIRA-T0039`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_bankTurnSeparated_lt`
- `AIRA-T0040`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_one_turn_window`
- `AIRA-T0041`: `Circle.Applications.ropeRealPhaseIntTurnError_eq_fullTurn_mul_turnRatioError`
- `AIRA-T0042`: `Circle.Applications.not_ropeRealPhaseNearTurn_of_turnRatioFiniteMargin`
- `AIRA-T0043`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin`
- `AIRA-T0044`: `Circle.Applications.ropeTurnRatioFiniteMargin_mono_context`
- `AIRA-T0045`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context`
- `AIRA-T0047`: `Circle.Applications.ropeTurnRatioFiniteMargin_mono_margin`
- `AIRA-T0050`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_one_channel_turnRatioFiniteMargin_le_context_margin`
- `AIRA-T0053`: `Circle.Applications.ropeTurnRatioFiniteMargin_int_iff_nonpos_of_one_lt_context`
- `AIRA-T0054`: `Circle.Applications.ropeTurnRatioFiniteMargin_iff_range_gap_bounds`
- `AIRA-T0055`: `Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_iff_nonpos_of_den_lt_context`
- `AIRA-T0056`: `Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_of_coprime_context_le_den`
- `AIRA-T0057`: `Circle.Applications.ropeTurnRatioFiniteMargin_natRatio_one_over_den_iff_context_le_den`
- `AIRA-T0058`: `Circle.Applications.ropeNearestIntegerWitnesses_iff_forall_int`
- `AIRA-T0059`: `Circle.Applications.ropeTurnRatioFiniteMargin_iff_nearestIntegerWitnesses`
- `AIRA-T0060`: `Circle.Applications.RopeTurnRatioFiniteMarginCertificate.certifies`
- `AIRA-T0061`: `Circle.Applications.ropeRationalPreset4099_turnRatioFiniteMargin`
- `AIRA-T0062`: `Circle.Applications.not_ropeRationalPreset4099_nearTurn`
- `AIRA-T0063`: `Circle.Applications.ropeTurnRatioIntervalWitness_forall_int`
- `AIRA-T0064`: `Circle.Applications.ropeTurnRatioFiniteMargin_of_intervalCertificate`
- `AIRA-T0065`: `Circle.Applications.ropeStandardChannel0Seed_intervalCertificate`
- `AIRA-T0066`: `Circle.Applications.ropeStandardChannel0Seed_turnRatioFiniteMargin`
- `AIRA-T0067`: `Circle.Applications.not_ropeStandardChannel0Seed_nearTurn`
- `AIRA-T0068`: `Circle.Applications.ropeStandardChannel0D2Seed_intervalCertificate`
- `AIRA-T0069`: `Circle.Applications.ropeStandardChannel0D2Seed_turnRatioFiniteMargin`
- `AIRA-T0070`: `Circle.Applications.not_ropeStandardChannel0D2Seed_nearTurn`
- `AIRA-T0071`: `Circle.Applications.ropeStandardChannel0D3Seed_intervalCertificate`
- `AIRA-T0072`: `Circle.Applications.ropeStandardChannel0D3Seed_turnRatioFiniteMargin`
- `AIRA-T0073`: `Circle.Applications.not_ropeStandardChannel0D3Seed_nearTurn`
- `AIRA-T0074`: `Circle.Applications.ropeStandardChannel0D4Seed_intervalCertificate`
- `AIRA-T0075`: `Circle.Applications.ropeStandardChannel0D4Seed_turnRatioFiniteMargin`
- `AIRA-T0076`: `Circle.Applications.not_ropeStandardChannel0D4Seed_nearTurn`
- `AIRA-T0077`: `Circle.Applications.ropeTurnRatioIntervalWitness_mono_margin`
- `AIRA-T0078`: `Circle.Applications.ropeTurnRatioIntervalCertificate_mono_margin`
- `AIRA-T0079`: `Circle.Applications.ropeStandardChannel0D5Seed_intervalCertificate`
- `AIRA-T0080`: `Circle.Applications.ropeStandardChannel0D5Seed_turnRatioFiniteMargin`
- `AIRA-T0081`: `Circle.Applications.not_ropeStandardChannel0D5Seed_nearTurn`
- `AIRA-T0082`: `Circle.Applications.ropeStandardChannel0_piD4_base_lower`
- `AIRA-T0083`: `Circle.Applications.ropeStandardChannel0_piD4_base_upper`
- `AIRA-T0084`: `Circle.Applications.ropeStandardChannel0D6Seed_intervalCertificate`
- `AIRA-T0085`: `Circle.Applications.ropeStandardChannel0D6Seed_turnRatioFiniteMargin`
- `AIRA-T0086`: `Circle.Applications.not_ropeStandardChannel0D6Seed_nearTurn`
- `AIRA-T0087`: `Circle.Applications.ropeStandardChannel0D7Seed_intervalCertificate`
- `AIRA-T0088`: `Circle.Applications.ropeStandardChannel0D7Seed_turnRatioFiniteMargin`
- `AIRA-T0089`: `Circle.Applications.not_ropeStandardChannel0D7Seed_nearTurn`
- `AIRA-T0090`: `Circle.Applications.ropeStandardChannel0_piD6_base_lower`
- `AIRA-T0091`: `Circle.Applications.ropeStandardChannel0_piD6_base_upper`
- `AIRA-T0092`: `Circle.Applications.ropeStandardChannel0D8Seed_intervalCertificate`
- `AIRA-T0093`: `Circle.Applications.ropeStandardChannel0D8Seed_turnRatioFiniteMargin`
- `AIRA-T0094`: `Circle.Applications.not_ropeStandardChannel0D8Seed_nearTurn`
- `AIRA-T0095`: `Circle.Applications.ropeStandardChannel0D8_gap710_error_lt_margin`
- `AIRA-T0096`: `Circle.Applications.not_ropeStandardChannel0D8SeedMargin_of_context_gt_seed`
- `AIRA-T0097`: `Circle.Applications.ropeStandardChannel0_piD20_base_lower`
- `AIRA-T0098`: `Circle.Applications.ropeStandardChannel0_piD20_base_upper`
- `AIRA-T0099`: `Circle.Applications.ropeStandardChannel0D9Seed_intervalCertificate`
- `AIRA-T0100`: `Circle.Applications.ropeStandardChannel0D9Seed_turnRatioFiniteMargin`
- `AIRA-T0101`: `Circle.Applications.not_ropeStandardChannel0D9Seed_nearTurn`
- `AIRA-T0102`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D9Seed`
- `AIRA-T0103`: `Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_65536`
- `AIRA-T0104`: `Circle.Applications.not_ropeStandardChannel0_margin_one_over_65536_of_context_gt_710`
- `AIRA-T0105`: `Circle.Applications.ropeStandardChannel0D10Seed_intervalCertificate`
- `AIRA-T0106`: `Circle.Applications.ropeStandardChannel0D10Seed_turnRatioFiniteMargin`
- `AIRA-T0107`: `Circle.Applications.not_ropeStandardChannel0D10Seed_nearTurn`
- `AIRA-T0108`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D10Seed`
- `AIRA-T0109`: `Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104000`
- `AIRA-T0110`: `Circle.Applications.not_ropeStandardChannel0_margin_one_over_104000_of_context_gt_710`
- `AIRA-T0111`: `Circle.Applications.ropeStandardChannel0D11Seed_intervalCertificate`
- `AIRA-T0112`: `Circle.Applications.ropeStandardChannel0D11Seed_turnRatioFiniteMargin`
- `AIRA-T0113`: `Circle.Applications.not_ropeStandardChannel0D11Seed_nearTurn`
- `AIRA-T0114`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed`
- `AIRA-T0115`: `Circle.Applications.ropeStandardChannel0_gap710_error_lt_one_over_104218`
- `AIRA-T0116`: `Circle.Applications.not_ropeStandardChannel0_margin_one_over_104218_of_context_gt_710`
- `AIRA-T0117`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D11Seed_cons`
- `AIRA-T0118`: `Circle.Applications.not_ropeStandardChannel0_margin_ge_one_over_104218_of_context_gt_710`
- `AIRA-T0119`: `Circle.Applications.ropeStandardChannel0D11_context4096_margin_bracket`
- `AIRA-T0120`: `Circle.Applications.ropeStandardChannel0D12Seed_intervalCertificate`
- `AIRA-T0121`: `Circle.Applications.ropeStandardChannel0D12Seed_turnRatioFiniteMargin`
- `AIRA-T0122`: `Circle.Applications.not_ropeStandardChannel0D12Seed_nearTurn`
- `AIRA-T0123`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed`
- `AIRA-T0124`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D12Seed_cons`
- `AIRA-T0125`: `Circle.Applications.ropeStandardChannel0D12_context8192_margin_bracket`
- `AIRA-T0126`: `Circle.Applications.ropeTurnRatioIntervalWitness_of_band_bounds`
- `AIRA-T0127`: `Circle.Applications.ropeStandardChannel0D13Seed_intervalCertificate`
- `AIRA-T0128`: `Circle.Applications.ropeStandardChannel0D13Seed_turnRatioFiniteMargin`
- `AIRA-T0129`: `Circle.Applications.not_ropeStandardChannel0D13Seed_nearTurn`
- `AIRA-T0130`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed`
- `AIRA-T0131`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D13Seed_cons`
- `AIRA-T0132`: `Circle.Applications.ropeStandardChannel0D13_context8192_margin_bracket`
- `AIRA-T0133`: `Circle.Applications.ropeStandardChannel0D14Seed_intervalCertificate`
- `AIRA-T0134`: `Circle.Applications.ropeStandardChannel0D14Seed_turnRatioFiniteMargin`
- `AIRA-T0135`: `Circle.Applications.not_ropeStandardChannel0D14Seed_nearTurn`
- `AIRA-T0136`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed`
- `AIRA-T0137`: `Circle.Applications.not_ropeRealPhaseBankNearTurn_of_standardChannel0D14Seed_cons`
- `AIRA-T0138`: `Circle.Applications.ropeStandardChannel0D14_context16384_margin_bracket`
- `AIRA-T0139`: `Circle.Applications.ropeTurnRatioIntervalWitness_of_rationalIntervalBand`
- `AIRA-T0140`: `Circle.Applications.ropeTurnRatioIntervalCertificate_of_rationalIntervalBands`

The main theorem is `AIRA-T0024`:

```text
Two ordered positions collide in every declared integer-period RoPE channel
iff every declared period divides their position gap.
```

That is the usable contract. It turns position indistinguishability into a finite arithmetic check over divisibility.

`AIRA-T0027`, `AIRA-T0028`, and `AIRA-T0034` add the first all-channel collision-counting seed. If the certifier finds a common exact collision gap inside the context, then `context - gap` ordered start positions have a paired position exactly `gap` steps ahead, and every one of those counted pairs is an all-channel collision when each declared period divides the gap. `AIRA-T0034` extends the same guarantee to every positive multiple of the common gap that still fits in the context. `AIRA-T0035` adds the single-channel converse: every unequal collision for one positive integer-period channel has a positive period-multiple gap. `AIRA-T0036` upgrades the all-channel count from guaranteed family to exact integer-bank count by proving that bank collision is equivalent to divisibility by the period-bank LCM. `AIRA-T0046` proves the complementary pass case: if that LCM reaches the inspected context, no unequal ordered in-context pair can collide in every declared integer-period channel. `AIRA-T0048` and `AIRA-T0049` prove the fail side: every counted start at the LCM gap is an all-channel collision, and a positive LCM below context produces an explicit unequal in-context collision witness. The Python certifier also applies this same LCM spine to bounded channel prefixes, reporting the first prefix whose LCM already reaches the inspected context when such a prefix appears in the bounded report. `AIRA-T0051` proves the prefix-to-full-bank bridge, and `AIRA-T0052` proves the unordered selected-subbank version: once a contained subbank's LCM reaches the context, the larger bank cannot have an unequal all-channel collision. Together with the Python parity tests, this justifies the exact per-channel single-period counts, exact total bank count, bounded prefix and subfamily reports, checked sample-collision witness, and no-collision pass result reported by the certifier for the declared integer-period model.

## Real-Phase Precursor

`AIRA-T0029` through `AIRA-T0033` start the real-valued RoPE theorem program without upgrading the numerical scan into a proof. They define the unwrapped real phase gap for one channel and prove:

```text
|((right : R) - left) * frequency| =
  (right - left) * |frequency|
```

for ordered natural positions, plus the lower-bound consequence:

```text
minGap * lower <= unwrapped_gap
```

whenever `minGap <= right-left`, `0 <= lower`, and `lower <= |frequency|`.

This is a quantitative precursor only. It is not a circular distance modulo a full turn, not a continued-fraction/Diophantine lower bound, and not a proof that the numerical real-phase margin report is formally certified.

`AIRA-T0031` adds the next bridge object:

```text
turn_error(turns) = |phase - turns * fullTurn|
```

If a phase lies inside one declared turn and is at least `margin` away from the left endpoint and the right endpoint, Lean proves the zero-turn and one-turn endpoint errors are both at least `margin`. `AIRA-T0032` strengthens that to every nonnegative full-turn multiple, and `AIRA-T0033` strengthens it again to every signed full-turn multiple. `AIRA-T0037` packages the result as a real phase-turn separation predicate, and `AIRA-T0038` proves that separation by `margin` rules out any near-turn collision at a smaller tolerance. `AIRA-T0039` and `AIRA-T0040` lift this to a finite real-phase bank: one separated channel is enough to rule out an all-channel near-turn collision at a smaller tolerance.

`AIRA-T0041` adds the turn-ratio bridge needed for the Diophantine route:

```text
|gap * frequency - turns * fullTurn|
=
fullTurn * |gap * (frequency / fullTurn) - turns|
```

for ordered positions, nonnegative frequency, and positive full-turn scale. This rewrites the RoPE near-turn error as the ordinary nearest-integer error for the turn ratio `frequency / fullTurn`. It is still not the full RoPE real-margin theorem, because the hard part is proving finite-context lower bounds for `|gap * alpha - turns|` through continued fractions or Diophantine approximation.

`AIRA-T0042` states that if such a finite-context turn-ratio margin has been certified for every positive gap below the inspected context, then one-channel real near-turn collision is impossible below the scaled tolerance `fullTurn * margin`. This theorem does not prove the margin for a concrete RoPE ratio; it proves that the margin certificate, once obtained by a later bounded-search or continued-fraction proof, has the intended no-near-turn consequence.

`AIRA-T0043` lifts the same finite-context margin certificate to a finite real-phase bank: one member channel with a proved finite-context margin is enough to rule out all-channel near-turn collision below the scaled tolerance. `AIRA-T0044` proves the monotonic transfer law for finite-context margins: a margin certified for a larger context automatically applies to any smaller requested context. `AIRA-T0047` proves the same downward closure for the margin value itself: a larger certified lower bound proves any smaller advertised margin over the same context. `AIRA-T0045` packages context transfer at the bank level, so one channel margin certified up to a larger horizon can rule out all-channel near-turn collision for smaller requested contexts. `AIRA-T0050` packages both transfers at once: a larger-context, larger-margin channel certificate can be reused for a smaller requested context and a smaller advertised margin in the final bank-level no-near-turn statement. `AIRA-T0054` connects the abstract finite-context predicate to the concrete generated gap range `List.range context`: checking every positive generated gap is equivalent to the predicate's gap side. `AIRA-T0058` proves the fixed-value nearest-integer bridge: checking a lower bound against the integer floor and integer ceiling is equivalent to checking the same bound against every integer turn. `AIRA-T0059` applies that bridge to every generated positive gap, making the finite-context predicate equivalent to two floor/ceiling witness checks per gap. This removes the infinite integer-turn search obligation, but it still does not prove that a concrete irrational or nonperiodic RoPE turn ratio has a positive lower bound. `AIRA-T0053` is the first negative guardrail for this path: an integer turn ratio has no positive finite-context margin once the context includes adjacent positions. `AIRA-T0055` extends the guardrail to natural rational ratios: if `turnRatio = numerator / denominator` and the context contains the denominator gap, that gap lands exactly on `numerator` full turns, so the channel again cannot certify any positive finite-context margin. `AIRA-T0056` gives the matching positive reduced-rational finite-context certificate: if `numerator` and `denominator` are coprime and the requested context stays at or below the denominator, then the nearest-integer margin is at least `1 / denominator`. `AIRA-T0057` packages the exact boundary: for a reduced natural rational turn ratio, that same `1 / denominator` certificate holds iff the inspected context does not exceed the denominator.

`AIRA-T0060` packages the finite witness payload as a proof-carrying certificate object. `AIRA-T0061` is the first named end-to-end finite-margin preset: the declared rational/discretized turn ratio `1/4099` has margin `1/4099` over context `4096`. `AIRA-T0062` applies that certificate to rule out one-channel near-turn collision below the certified margin. This is a complete theorem-backed certificate for a rational/discretized turn-ratio policy; it still does not prove the irrational/nonperiodic standard RoPE margin theorem.

`AIRA-T0063` and `AIRA-T0064` add the interval-certificate route. A rational enclosure of `gap * alpha` that lies inside one integer cell and stays at least `margin` from both cell endpoints proves the nearest-integer lower bound for that gap; a finite table of those witnesses proves the full finite-context turn-ratio margin. `AIRA-T0065` through `AIRA-T0067` instantiate that route for the genuine standard RoPE channel-0 turn ratio `alpha = 1 / (2π)` over context `6`, with margin `1/8`, using `3 < π <= 4`. `AIRA-T0068` through `AIRA-T0070` strengthen the same genuine standard-channel seed to context `7`, with margin `1/32`, using the sharper bound `3.14 < π` to certify the sixth gap by the enclosure `gap/8 <= gap/(2π) <= 25*gap/157`. `AIRA-T0071` through `AIRA-T0073` extend the seed to context `8` by certifying gap `7` in integer cell `1` with `10/9 <= 7/(2π) <= 175/157`, using `π < 3.15` and `3.14 < π`. `AIRA-T0074` through `AIRA-T0076` extend the same margin to context `19`: gaps `7` through `12` are certified in cell `1`, and gaps `13` through `18` are certified in cell `2`, with `10*gap/63 <= gap/(2π) <= 25*gap/157`. `AIRA-T0077` and `AIRA-T0078` prove that interval witnesses and certificates survive a nonnegative margin downgrade. `AIRA-T0079` through `AIRA-T0081` use that bridge plus new cell bands to certify context `44` with margin `1/64`. `AIRA-T0082` and `AIRA-T0083` prove the sharper four-decimal enclosure `5000/31416 <= 1/(2π) <= 5000/31415`; `AIRA-T0084` through `AIRA-T0086` use it to certify context `57` with margin `1/512`; `AIRA-T0087` through `AIRA-T0089` convert the generated d4 band table into a context-333, margin-`1/512` certificate plus no-near-turn consequence. `AIRA-T0090` and `AIRA-T0091` add six-decimal bounds `500000/3141593 <= 1/(2π) <= 500000/3141592`; `AIRA-T0092` through `AIRA-T0094` use those bounds and generated cells `0` through `112` to certify context `710` with margin `1/1024`. `AIRA-T0095` and `AIRA-T0096` prove the stop condition for that exact margin: gap `710` is already within margin `1/1024` of integer turn `113`, so a context larger than `710` cannot keep the same lower bound. `AIRA-T0097` through `AIRA-T0101` add 20-decimal bounds and certify context `4096` with conservative margin `1/131072`, using generated cells `0` through `651`. `AIRA-T0102` packages the D9 conditional bank-level consequence, and `AIRA-T0103` through `AIRA-T0104` prove that gap `710` blocks the doubled D9 margin `1/65536`. `AIRA-T0105` through `AIRA-T0108` reuse the same 20-decimal bounds and cell table to tighten the context-4096 standard channel-0 seed to margin `1/105000` and carry it through the one-channel and conditional bank-level no-near-turn consequences. `AIRA-T0109` and `AIRA-T0110` prove the nearby D10 boundary: gap `710` is already within `1/104000` of integer turn `113`, so no context containing that gap can certify that larger advertised margin. `AIRA-T0111` through `AIRA-T0114` tighten the context-4096 generated d20 certificate shape again to margin `1/104219`; `AIRA-T0115` and `AIRA-T0116` prove the adjacent stop condition that margin `1/104218` is already blocked at gap `710`. `AIRA-T0117` packages the D11 bridge for banks whose first frequency is standard channel 0. `AIRA-T0118` generalizes the stop condition to every advertised margin at or above `1/104218`, and `AIRA-T0119` packages the 4k bracket: margin `1/104219` is proved, while any margin at or above `1/104218` is impossible. `AIRA-T0120` through `AIRA-T0122` lower the margin one step to `1/104220` and extend the same d20 interval-certificate method to context `8192`, including the one-channel no-near-turn consequence. `AIRA-T0123` and `AIRA-T0124` carry that D12 seed through the conditional one-separating-channel bank transfer, including the common first-channel bank shape. `AIRA-T0125` packages the weaker 8k bracket at margin `1/104220`. `AIRA-T0126` adds a reusable generated-band endpoint bridge: if a whole band shares one integer cell and the band endpoints satisfy the required rational lower/upper inequalities, Lean derives the interval witness for every gap in that band by monotonicity. `AIRA-T0127` through `AIRA-T0132` use that bridge to certify the sharper context-8192 D13 seed at margin `1/104219`, its one-channel no-near-turn consequence, conditional bank transfers, and 8k bracket. `AIRA-T0133` through `AIRA-T0138` extend the same margin to context `16384`, add the D14 one-channel no-near-turn theorem, add D14 conditional bank transfers, and package the 16k bracket: margin `1/104219` is proved, while any margin at or above `1/104218` is impossible for context `16384`; margins strictly between those two rationals remain unresolved. `AIRA-T0139` and `AIRA-T0140` add the next compression bridge: a valid list of rational interval bands that covers every positive generated gap proves the same interval-certificate predicate without expanding every gap as a separate interval case. This is real standard-RoPE theorem infrastructure, but it is intentionally still channel-0 based: it does not certify 128k or prove margins for every channel in a multi-channel bank.

The sidecar also emits exact-rational interval plans for audit and standard-channel interval certificates. The four-decimal context-333 plan, six-decimal context-710 plan, 20-decimal context-4096 plans through the `1/104219` 4k seed, the 20-decimal context-8192 plans at margins `1/104220` and `1/104219`, and the 20-decimal context-16384 plan at margin `1/104219` are matched by Lean declarations. The same planner reports candidate 32k and 64k rows at margin `1/104219`, and a 128k-frontier row whose first uncovered gap is `103993`; those rows are not Lean-proved. The generated Markdown and JSON include `Band Endpoint Audit` summaries sampling the first and last band of each standard interval plan; rerun the Python planner for the complete deterministic band list. Larger generated plans remain reproducible source data until matching Lean declarations compile and manifest ids are marked proved.

## Certifier Interface

The public command is:

```bash
python scripts/rope_certify.py --head-dim 128 --base 10000 --context 32768 --tolerance 1e-6
```

It emits:

- config assumptions;
- theorem ids and Lean declaration names;
- integer periods produced by the discretization policy;
- exact discrete pass/fail;
- common exact collision gap when it is inside the context;
- sample colliding pairs when exact discrete distinguishability fails;
- guaranteed common-gap collision-pair count when exact discrete distinguishability fails;
- guaranteed common-gap-multiple collision-pair count when exact discrete distinguishability fails;
- exact single-period collision-pair counts for each declared integer channel;
- exact total bank collision-pair count for the declared integer-period phase bank;
- bounded prefix collision reports and the first prefix that already distinguishes the inspected context under the integer-period model;
- bounded selected-subfamily pass reports for small subbanks whose LCM already reaches the inspected context;
- numerical real-phase margin and worst gap;
- proof-layer status for exact integer-period, rational/discretized, interval-backed standard-RoPE, and numerical diagnostic layers;
- theorem ids for the unwrapped real-phase and turn-ratio precursors;
- a machine-readable JSON certificate when `--format json` or `--json-out` is used.

For explicit positive integer-period banks that are not derived from a RoPE base/head-dimension pair, the exact-only command is:

```bash
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
python scripts/phase_bank_certify.py --preset quantized_shared_factor_256
python scripts/phase_bank_certify.py --preset quantized_lcm_boundary_fail_241
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_pass_960
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
```

This path emits the same theorem-linked exact discrete certificate fields but deliberately omits numerical real-phase margin output. The quantized presets are declared shared-factor and near-boundary integer-period banks. The interpolation-style presets use the exact integer-period analogue of multiplying declared periods by an integer scale factor; they are not real-valued interpolation theorems.

Named presets are available:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
python scripts/rope_certify.py --preset diagnostic_single_channel_10000_20
python scripts/rope_certify.py --preset diagnostic_two_channel_36_128
python scripts/rope_certify.py --preset diagnostic_prefix_pass_4_128
python scripts/rope_certify.py --preset diagnostic_shared_factor_25_64
```

The `llama_style_*` preset names are public-safe configuration labels, not claims about a particular vendor checkpoint. The `diagnostic_*` presets are intentionally small exact-discrete cases used to exercise sample collisions, common-gap counts, prefix-pass reporting, shared-factor failures, and total bank counts.

## Reproducible Preset Results

The paper sidecar records the current named preset outputs under:

```text
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json
sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md
```

Regenerate them with:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py \
  --json-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json \
  --markdown-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md
```

The current preset table reports exact discrete `PASS` for the public-safe model-like presets under the rounded integer-period phase-bank model, exact discrete `FAIL` for diagnostic presets where the declared integer periods intentionally collide inside the context, and the first bounded prefix whose LCM already reaches the inspected context when the prefix report finds one. The exact phase-bank table adds quantized shared-factor cases and interpolation-style scaled-period boundary cases. The sidecar JSON stores compact certificate summaries rather than full nested CLI certificates, preserving theorem ids and count evidence while avoiding repeated Lean declaration and assumption payloads. These rows are reproducible configuration certificates, not evidence that any model has better perplexity, reasoning, context length, runtime, memory, training stability, or deployment readiness.

## Exact Discrete Model

For one declared period:

```text
phase(period, position) = position mod period
```

For a phase bank:

```text
phase_bank(periods, position) =
  [position mod period for period in periods]
```

Two positions collide in the bank exactly when every channel collides:

```text
forall period in periods:
  left mod period = right mod period
```

For ordered positions `left <= right`, the Lean theorem states:

```text
phase_bank(left) = phase_bank(right)
iff
forall period in periods:
  period divides (right - left)
```

The Python certifier uses this by computing the common collision gap. If that gap is at least the inspected context length, then no unequal pair inside the context can collide in every discrete channel.

## Real-Phase Margin Diagnostic

The certifier also computes the usual real-valued RoPE channel periods:

```text
period_i = 2*pi / base^(-2*i/head_dim)
```

For each nonzero position gap in the context, it computes the best channel separation from a full-turn collision and reports the worst such margin.

This is deliberately labeled as numerical evidence only. It is useful for engineering inspection, but it is not a Lean proof over real-valued trigonometric RoPE.

## Proved Core

The proved result is a finite exact contract:

- exact collision in a single integer-period channel is characterized by divisibility of the position gap;
- exact collision in a finite bank is characterized by all declared periods dividing the same gap;
- exact distinguishability is equivalent to at least one declared period not dividing the gap;
- if the bank contains a period at least as large as the inspected context, unequal positions inside that context are distinguished by that channel.
- if a common exact collision gap lies inside the context, `context - gap` start positions produce theorem-certified all-channel collisions at that gap.

The ordinary baseline for this interface is an unchecked numerical scan or hand-written RoPE configuration note. The Circle Calculus certifier improves the audit path by attaching theorem ids and assumptions to the exact discrete claim. That benchmark-facing comparison is not evidence of model quality, and the Python report is not a proof.

## Guardrail

This paper does not claim:

- that standard real-valued RoPE has exact integer periods;
- that a model improves when a certifier passes;
- that context length is extended;
- that perplexity, reasoning, speed, memory, or training stability improves;
- that this replaces RoPE scaling, interpolation, YaRN-style methods, ALiBi, learned positions, state-space models, or attention experiments.

The contribution is narrower and more useful: a proof-carrying architecture contract for a real class of position-bookkeeping questions.
