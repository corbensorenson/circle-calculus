# RoPE Certifier Review Packet

This packet is for an external reviewer who wants to try the Circle Calculus RoPE position-distinguishability certifier without reading the whole repository.

## What To Review

The certifier is a proof-carrying audit tool for a declared integer-period RoPE phase-bank model plus a numerical real-phase scan. It answers:

```text
Do two positions inside this context collide in every declared integer-period channel?
```

It does not claim model-quality, context-length, perplexity, runtime, memory, training, or deployment improvement.

## Quick Commands

```bash
python -m pip install -e .
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset diagnostic_single_channel_10000_20
python scripts/rope_certify.py --preset diagnostic_two_channel_36_128 --format json
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
lake build Circle.Applications.RoPECertifier
python -m pytest tests/test_rope_certifier.py -q
```

## Source Trail

- Quickstart: `docs/ROPE_CERTIFIER_QUICKSTART.md`
- Paper: `papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md`
- Lean: `Circle/Applications/RoPECertifier.lean`
- Python: `circle_math/applications/rope_certifier.py`
- Exact phase-bank CLI: `scripts/phase_bank_certify.py`
- Preset fixtures: `sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md`
- Living Book page: `site/chapters/applications/rope_certifier.qmd`

## Theorem Groups

Exact integer-period contract:

```text
AIRA-T0021 through AIRA-T0026
```

Collision counting:

```text
AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052
```

Real-phase theorem program and finite-margin certificates:

```text
AIRA-T0029 through AIRA-T0033, AIRA-T0037 through AIRA-T0045, AIRA-T0047, AIRA-T0050, AIRA-T0053 through AIRA-T0081
```

## Known Boundaries

- The exact proof object is the integer-period phase bank, not raw floating-point RoPE.
- The real-phase scan is numerical evidence only.
- The real-phase Lean work has conditional one-turn-window, turn-separation, finite bank no-near-turn, turn-ratio scaling, one-channel plus bank-level finite-context margin consequence, context-plus-margin transfer, integer/rational-turn-ratio guardrails, generated-gap finite-enumeration, floor/ceiling nearest-integer witness bridge precursors, one named theorem-backed rational/discretized `1/4099` context-4096 certificate, a generic rational interval-certificate bridge, interval-certificate margin monotonicity, and tiny standard-RoPE channel-0 seeds for `1 / (2π)`, currently strengthened to context `44`, margin `1/64`.
- The standard-RoPE interval seed is a real theorem for that tiny context only. It still does not have the continued-fraction, generated-interval, or Diophantine theorem needed to certify arbitrary standard irrational RoPE ratios at large contexts.
- Diagnostic presets are intentionally small failure cases; they are not vendor checkpoint claims.

## Review Questions

1. Are the integer-period assumptions stated clearly enough for an ML engineer?
2. Is the LCM-based total bank collision count the right user-facing report for the declared model?
3. Are the real-phase theorem ids clearly separated from the numerical scan?
4. What is the smallest useful Diophantine or continued-fraction lemma to prove next?
5. Would this packet be enough to reproduce and critique the contract without knowing Lean?
