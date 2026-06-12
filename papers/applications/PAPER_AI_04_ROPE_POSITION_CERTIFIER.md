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
```

Lean declarations determine proof status. The theorem manifest is the proof-status source of truth. Python output is an executable certificate report for the declared model; it does not replace Lean proof status.

## Theorem Spine

- `AIRA-T0021`: `Circle.Applications.ropeDiscreteCollision_iff_gap_dvd`
- `AIRA-T0022`: `Circle.Applications.ropeDiscreteDistinguishable_iff_not_gap_dvd`
- `AIRA-T0023`: `Circle.Applications.ropeDiscreteCollision_iff_eq_on_context`
- `AIRA-T0024`: `Circle.Applications.ropePhaseBankCollision_iff_forall_gap_dvd`
- `AIRA-T0025`: `Circle.Applications.ropePhaseBankDistinguishable_iff_exists_not_gap_dvd`
- `AIRA-T0026`: `Circle.Applications.ropePhaseBankDistinguishable_of_period_ge_context`

The main theorem is `AIRA-T0024`:

```text
Two ordered positions collide in every declared integer-period RoPE channel
iff every declared period divides their position gap.
```

That is the usable contract. It turns position indistinguishability into a finite arithmetic check over divisibility.

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
- numerical real-phase margin and worst gap;
- a machine-readable JSON certificate when `--format json` or `--json-out` is used.

Named presets are available:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
```

The preset names are public-safe configuration labels, not claims about a particular vendor checkpoint.

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

The ordinary baseline for this interface is an unchecked numerical scan or hand-written RoPE configuration note. The Circle Calculus certifier improves the audit path by attaching theorem ids and assumptions to the exact discrete claim. That benchmark-facing comparison is not evidence of model quality, and the Python report is not a proof.

## Guardrail

This paper does not claim:

- that standard real-valued RoPE has exact integer periods;
- that a model improves when a certifier passes;
- that context length is extended;
- that perplexity, reasoning, speed, memory, or training stability improves;
- that this replaces RoPE scaling, interpolation, YaRN-style methods, ALiBi, learned positions, state-space models, or attention experiments.

The contribution is narrower and more useful: a proof-carrying architecture contract for a real class of position-bookkeeping questions.
