# Circle Calculus AI 4: Proof-Carrying RoPE Position Distinguishability

Status: draft with proved exact discretized RoPE-bank collision criteria and a public Python certifier.

## Purpose

This paper ships the first externally usable Circle Calculus AI contract: a RoPE position-distinguishability certifier that a non-Lean ML engineer can run against a rotary-position configuration.

The key separation is:

- **formal certificate:** exact integer-period/discretized phase-bank distinguishability;
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

`AIRA-T0043` lifts the same finite-context margin certificate to a finite real-phase bank: one member channel with a proved finite-context margin is enough to rule out all-channel near-turn collision below the scaled tolerance. `AIRA-T0044` proves the monotonic transfer law for finite-context margins: a margin certified for a larger context automatically applies to any smaller requested context. `AIRA-T0047` proves the same downward closure for the margin value itself: a larger certified lower bound proves any smaller advertised margin over the same context. `AIRA-T0045` packages context transfer at the bank level, so one channel margin certified up to a larger horizon can rule out all-channel near-turn collision for smaller requested contexts. `AIRA-T0050` packages both transfers at once: a larger-context, larger-margin channel certificate can be reused for a smaller requested context and a smaller advertised margin in the final bank-level no-near-turn statement. `AIRA-T0054` connects the abstract finite-context predicate to the concrete generated gap range `List.range context`: checking every positive generated gap is equivalent to the predicate's gap side. `AIRA-T0058` proves the fixed-value nearest-integer bridge: checking a lower bound against the integer floor and integer ceiling is equivalent to checking the same bound against every integer turn. `AIRA-T0059` applies that bridge to every generated positive gap, making the finite-context predicate equivalent to two floor/ceiling witness checks per gap. This removes the infinite integer-turn search obligation, but it still does not prove that a concrete irrational or nonperiodic RoPE turn ratio has a positive lower bound. `AIRA-T0053` is the first negative guardrail for this path: an integer turn ratio has no positive finite-context margin once the context includes adjacent positions. `AIRA-T0055` extends the guardrail to natural rational ratios: if `turnRatio = numerator / denominator` and the context contains the denominator gap, that gap lands exactly on `numerator` full turns, so the channel again cannot certify any positive finite-context margin. `AIRA-T0056` gives the matching positive reduced-rational finite-context certificate: if `numerator` and `denominator` are coprime and the requested context stays at or below the denominator, then the nearest-integer margin is at least `1 / denominator`. `AIRA-T0057` packages the exact boundary: for a reduced natural rational turn ratio, that same `1 / denominator` certificate holds iff the inspected context does not exceed the denominator. These rational and floor/ceiling witness results are useful for discretized, rationalized, or exact finite-certificate phase policies; they still do not prove the irrational/nonperiodic real RoPE margin theorem.

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
- theorem ids for the unwrapped real-phase and turn-ratio precursors;
- a machine-readable JSON certificate when `--format json` or `--json-out` is used.

For explicit positive integer-period banks that are not derived from a RoPE base/head-dimension pair, the exact-only command is:

```bash
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
```

This path emits the same theorem-linked exact discrete certificate fields but deliberately omits numerical real-phase margin output.

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

The current preset table reports exact discrete `PASS` for the public-safe model-like presets under the rounded integer-period phase-bank model, exact discrete `FAIL` for diagnostic presets where the declared integer periods intentionally collide inside the context, and the first bounded prefix whose LCM already reaches the inspected context when the prefix report finds one. The diagnostic rows include both collision failures and prefix-pass cases. It also reports numerical real-phase margin scans. These rows are reproducible configuration certificates, not evidence that any model has better perplexity, reasoning, context length, runtime, memory, training stability, or deployment readiness.

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
