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

## Expected Observations

The commands should show contract behavior, not benchmark claims:

| Case | Expected Contract Result | What It Demonstrates |
| --- | --- | --- |
| `llama_style_10000_4k` | exact discrete PASS | the rounded integer-period bank has no unequal all-channel collision inside context `4096`; the first bounded prefix pass appears at length `5` |
| `llama_style_10000_128k` | exact discrete PASS | the rounded integer-period bank still has its common gap outside context; the real-phase proof layer now separately has a one-channel D17 128k standard-channel certificate |
| `llama_style_500000_128k` | exact discrete PASS | a larger-base rounded bank also passes the declared exact model; the bounded subfamily report finds a sufficient subbank |
| `diagnostic_single_channel_10000_20` | exact discrete FAIL | common gap `6` and exact integer-bank collision-pair count `24` |
| `diagnostic_two_channel_36_128` | exact discrete FAIL | common gap `114` and exact integer-bank collision-pair count `14` |
| `interpolated_x4_boundary_fail_961` | exact discrete FAIL | the scaled-period integer analogue fails one token past its LCM boundary |

The real-phase rows are numerical diagnostics unless the output is specifically citing the theorem-backed rational or interval seed layers.

## Source Trail

- Quickstart: `docs/ROPE_CERTIFIER_QUICKSTART.md`
- Paper: `papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md`
- Lean: `Circle/Applications/RoPECertifier.lean`
- Generated Lean certificates: `Circle/Applications/RoPEGeneratedCertificates.lean`
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
AIRA-T0029 through AIRA-T0033, AIRA-T0037 through AIRA-T0045, AIRA-T0047, AIRA-T0050, AIRA-T0053 through AIRA-T0161
```

## Known Boundaries

- The exact proof object is the integer-period phase bank, not raw floating-point RoPE.
- The real-phase scan is numerical evidence only.
- The real-phase Lean work has conditional one-turn-window, turn-separation, finite bank no-near-turn, turn-ratio scaling, one-channel plus bank-level finite-context margin consequence, context-plus-margin transfer, integer/rational-turn-ratio guardrails, generated-gap finite-enumeration, floor/ceiling nearest-integer witness bridge precursors, one named theorem-backed rational/discretized `1/4099` context-4096 certificate, a generic rational interval-certificate bridge, interval-certificate margin monotonicity, a generated-band endpoint bridge, standard-RoPE channel-0 seeds for `1 / (2π)`, proved gap-`710` obstructions for margins `1/1024`, `1/65536`, `1/104000`, and every margin at or above `1/104218`, context-`4096`, context-`8192`, context-`16384`, context-`32768`, and context-`65536` channel-0 seeds at margin `1/104219`, plus a generated D17 context-`131072` seed at margin `1/328459`. The D17 bracket proves every margin at or above `1/328458` impossible once gap `103993` is in scope. The `AIRA-T0139`/`AIRA-T0140`/`AIRA-T0141` rational-band compression and endpoint-reflection bridge now powers generated 32k/64k/128k interval certificates; the generated source stores those large tables as compact uniform gap/cell rows with shared rational bounds attached inside Lean, proves coverage through a contiguous gap-chain bridge instead of a gap-by-band search, and checks endpoint validity on compact rows before reflecting it to expanded band validity.
- The standard-RoPE interval seed is a real theorem for that bounded one-channel context only. It still does not have the continued-fraction, generated-interval, or Diophantine theorem needed to certify arbitrary standard irrational RoPE ratios at large contexts or a full RoPE bank.
- Diagnostic presets are intentionally small failure cases; they are not vendor checkpoint claims.

## Review Questions

1. Are the integer-period assumptions stated clearly enough for an ML engineer?
2. Is the LCM-based total bank collision count the right user-facing report for the declared model?
3. Are the real-phase theorem ids clearly separated from the numerical scan?
4. What is the smallest useful Diophantine or continued-fraction lemma to prove next?
5. Would this packet be enough to reproduce and critique the contract without knowing Lean?
