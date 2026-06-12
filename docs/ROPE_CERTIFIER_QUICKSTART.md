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
```

The preset names are public-safe configuration labels. They are not claims about a particular vendor checkpoint.

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
guaranteed_common_gap_collision_pair_count=0
real_phase_margin=PASS worst_margin_radians=...
real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031 (unwrapped and one-turn endpoint precursors only; not a circular-margin proof)
theorem_ids=AIRA-T0021,AIRA-T0022,AIRA-T0023,AIRA-T0024,AIRA-T0025,AIRA-T0026,AIRA-T0027,AIRA-T0028
```

`exact_discrete_contract=PASS` means the integer-period phase bank has no all-channel collision among unequal positions inside the inspected context. The Lean-backed theorem spine proves that all-channel collision is equivalent to every declared period dividing the position gap.

`real_phase_margin=PASS` means the numerical scan did not find a real-valued near-collision below the chosen tolerance. This is not a Lean proof over real trigonometric RoPE.

`real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031` means Lean has proved the unwrapped one-channel real phase-gap arithmetic and a one-turn endpoint-error precursor used by later real-margin work. It is not a full circular modulo-full-turn proof and does not certify the numerical scan.

If the exact discrete contract fails, the output includes a common collision gap and sample colliding pairs.
It also reports `guaranteed_common_gap_collision_pair_count`, the number of starts whose paired position is exactly the common collision gap ahead. That count is theorem-backed for the declared integer-period phase bank, but it is not a total count of all collision pairs at every multiple of the gap.

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
