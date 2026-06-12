# RoPE Certifier Quickstart

This quickstart is for ML engineers who want to inspect a RoPE-like positional configuration without reading Lean code first.

The certifier answers a narrow contract question:

```text
Under a declared integer-period phase-bank model, do any two positions inside this context collide in every channel?
```

It also prints a numerical real-phase margin scan for ordinary RoPE frequencies. That scan is useful engineering evidence, but it is not a formal proof.

## Install

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Lean is not required to run the Python certifier. Lean is required only if you want to rebuild the formal proof source with `lake build`.

## Run A Preset

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
```

Available presets:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k
python scripts/rope_certify.py --preset llama_style_10000_128k
python scripts/rope_certify.py --preset llama_style_500000_128k
python scripts/rope_certify.py --preset diagnostic_single_channel_10000_20
python scripts/rope_certify.py --preset diagnostic_two_channel_36_128
python scripts/rope_certify.py --preset diagnostic_prefix_pass_4_128
python scripts/rope_certify.py --preset diagnostic_shared_factor_25_64
```

The `llama_style_*` preset names are public-safe configuration labels. They are not claims about a particular vendor checkpoint. The `diagnostic_*` presets are small exact-discrete cases for checking collision-count, prefix-pass, and shared-factor failure fields.

## Run A Custom Config

```bash
python scripts/rope_certify.py --head-dim 128 --base 10000 --context 32768 --tolerance 1e-6
```

Key flags:

- `--head-dim`: RoPE head dimension. It must be even because RoPE uses dimension pairs.
- `--base`: the RoPE base, such as `10000` or `500000`.
- `--context`: the inspected context length.
- `--tolerance`: numerical real-phase margin threshold in radians.
- `--discretization`: one of `round`, `floor`, or `ceil`, controlling how real period estimates become integer periods for the exact Lean-backed contract.

## Read The Output

The text output has two different evidence layers:

```text
exact_discrete_contract=PASS common_collision_gap=>= context
guaranteed_common_gap_collision_pair_count=0 guaranteed_common_gap_multiple_pair_count=0 total_bank_collision_pair_count=0
prefix_collision_reports=... first_exact_pass_prefix_length=...
real_phase_margin=PASS worst_margin_radians=...
real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050 (unwrapped, signed full-turn, turn-separation, bank-level no-near-turn, turn-ratio scaling, finite-context margin consequence, and context-plus-margin transfer precursors only; not a Diophantine proof)
theorem_ids=AIRA-T0021,AIRA-T0022,AIRA-T0023,AIRA-T0024,AIRA-T0025,AIRA-T0026,AIRA-T0027,AIRA-T0028,AIRA-T0034,AIRA-T0035,AIRA-T0036,AIRA-T0046,AIRA-T0048,AIRA-T0049
```

`exact_discrete_contract=PASS` means the integer-period phase bank has no all-channel collision among unequal positions inside the inspected context. The Lean-backed theorem spine proves that all-channel collision is equivalent to the period-bank LCM dividing the position gap, and `AIRA-T0046` proves the no-collision pass condition when that LCM reaches the context.

`real_phase_margin=PASS` means the numerical scan did not find a real-valued near-collision below the chosen tolerance. This is not a Lean proof over real trigonometric RoPE.

`real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050` means Lean has proved the unwrapped one-channel real phase-gap arithmetic, signed full-turn-multiple window precursors, the bank-level theorem shape that one proved separating channel rules out an all-channel near-turn collision at smaller tolerance, the turn-ratio scaling bridge into nearest-integer Diophantine error, the one-channel and bank-level consequences of a finite-context turn-ratio margin certificate, and conservative context/margin/context-plus-margin transfer laws. It is not a Diophantine proof that arbitrary RoPE gaps satisfy the margin predicate and does not certify the numerical scan.

If the exact discrete contract fails, the output includes a common collision gap and sample colliding pairs.
It also reports `guaranteed_common_gap_collision_pair_count`, the number of starts whose paired position is exactly the common collision gap ahead, and `guaranteed_common_gap_multiple_pair_count`, the corresponding guaranteed family summed over every positive in-context multiple of that gap. `total_bank_collision_pair_count` is the exact all-channel count for the declared integer-period bank, backed by the period-bank LCM theorem. `AIRA-T0048` proves the LCM-gap collision family, and `AIRA-T0049` proves that a positive LCM below the context gives an explicit unequal collision witness. It is not a real-valued RoPE collision count.

For each declared integer period, the JSON certificate includes `single_period_collision_pair_counts`. These are exact single-channel counts, not all-channel bank collision counts.

The JSON certificate also includes `prefix_collision_reports`, bounded summaries for the first few channel prefixes. Each prefix report reuses the same `AIRA-T0036`/`AIRA-T0046`/`AIRA-T0048`/`AIRA-T0049` LCM theorem spine as the full bank, so `first_exact_pass_prefix_length` tells you the first declared prefix whose integer-bank LCM already reaches the inspected context. This is still an integer-period sub-bank report, not a real-valued RoPE collision proof.

## Machine-Readable Output

Print JSON to stdout:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k --format json
```

Write JSON to a file:

```bash
python scripts/rope_certify.py --preset llama_style_10000_4k --json-out /tmp/rope_certificate.json
```

The JSON includes:

- config assumptions;
- theorem ids;
- Lean declaration names;
- discretized periods;
- exact single-period collision counts for each discretized period;
- exact all-channel bank collision count for the declared integer-period bank;
- bounded prefix collision reports and the first prefix that already passes, when one appears in the reported bound;
- exact discrete pass/fail;
- sample exact collisions when present;
- numerical real-phase margin data;
- a claim boundary.

## Reproduce The Preset Results Table

The paper sidecar can emit the preset results used by the paper and Living Book:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```

To regenerate the committed result fixtures:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py \
  --json-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.json \
  --markdown-out sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md
```

## What The Certifier Does Not Claim

The certifier does not claim:

- that standard real-valued RoPE has exact integer periods;
- that a model's context length improves;
- that perplexity, reasoning quality, speed, memory, or training stability improves;
- that numerical scans replace Lean proofs;
- that a pass is enough to deploy a positional scheme.

The useful claim is narrower: the exact discrete contract is theorem-linked, reproducible, and explicit about its assumptions.
