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
- `AIRA-T0029`: `Circle.Applications.ropeRealPhaseGapAbs_eq_natGap_mul_abs`
- `AIRA-T0030`: `Circle.Applications.ropeRealPhaseGapAbs_ge_minGap_mul_lower`
- `AIRA-T0031`: `Circle.Applications.ropeRealPhaseNatTurnEndpointErrors_ge_margin_of_one_turn_window`
- `AIRA-T0032`: `Circle.Applications.ropeRealPhaseNatTurnError_ge_margin_of_one_turn_window`
- `AIRA-T0033`: `Circle.Applications.ropeRealPhaseIntTurnError_ge_margin_of_one_turn_window`

The main theorem is `AIRA-T0024`:

```text
Two ordered positions collide in every declared integer-period RoPE channel
iff every declared period divides their position gap.
```

That is the usable contract. It turns position indistinguishability into a finite arithmetic check over divisibility.

`AIRA-T0027`, `AIRA-T0028`, and `AIRA-T0034` add the first all-channel collision-counting seed. If the certifier finds a common exact collision gap inside the context, then `context - gap` ordered start positions have a paired position exactly `gap` steps ahead, and every one of those counted pairs is an all-channel collision when each declared period divides the gap. `AIRA-T0034` extends the same guarantee to every positive multiple of the common gap that still fits in the context. `AIRA-T0035` adds the single-channel converse: every unequal collision for one positive integer-period channel has a positive period-multiple gap. `AIRA-T0036` upgrades the all-channel count from guaranteed family to exact integer-bank count by proving that bank collision is equivalent to divisibility by the period-bank LCM. Together with the Python parity tests, this justifies the exact per-channel single-period counts and the exact total bank count reported by the certifier for the declared integer-period model.

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

If a phase lies inside one declared turn and is at least `margin` away from the left endpoint and the right endpoint, Lean proves the zero-turn and one-turn endpoint errors are both at least `margin`. `AIRA-T0032` strengthens that to every nonnegative full-turn multiple, and `AIRA-T0033` strengthens it again to every signed full-turn multiple. This is still not the full RoPE real-margin theorem, because the hard part is proving arbitrary RoPE gaps satisfy the one-turn window hypotheses via Diophantine or continued-fraction bounds.

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
- numerical real-phase margin and worst gap;
- theorem ids for the unwrapped real-phase precursor;
- a machine-readable JSON certificate when `--format json` or `--json-out` is used.

Named presets are available:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
```

The preset names are public-safe configuration labels, not claims about a particular vendor checkpoint.

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

The current preset table reports exact discrete `PASS` for the three public-safe presets under the rounded integer-period phase-bank model. It also reports numerical real-phase margin scans. These rows are reproducible configuration certificates, not evidence that any model has better perplexity, reasoning, context length, runtime, memory, training stability, or deployment readiness.

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
