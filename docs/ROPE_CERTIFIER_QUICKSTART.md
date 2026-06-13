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

## Run An Explicit Integer Phase Bank

When you already have declared integer periods from a quantized, rationalized, or diagnostic phase bank, use the exact-only CLI:

```bash
python scripts/phase_bank_certify.py --periods 6,9,13,18 --context 128
```

This command emits the theorem-linked exact discrete certificate only. It does not compute or claim any real-valued RoPE margin.

Named exact-only diagnostics are also available:

```bash
python scripts/phase_bank_certify.py --preset quantized_shared_factor_256
python scripts/phase_bank_certify.py --preset quantized_lcm_boundary_fail_241
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_pass_960
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
```

The `quantized_*` presets exercise shared-factor and one-token-past-boundary failures for declared integer periods. The `interpolated_x4_*` presets use the exact integer-period analogue of slowing phase advance by multiplying declared periods by `4`; they show the pass/fail boundary at LCM `960`. These are exact phase-bank contracts, not real-valued interpolation proofs.

## Read The Output

The text output has two different evidence layers:

```text
proof_layers=exact_integer_period_phase_bank:PASS,rational_discretized_finite_margin:AVAILABLE_NAMED_PRESET,interval_backed_standard_rope:AVAILABLE_SEED_CONTEXT_57,numerical_real_phase_scan:PASS
exact_discrete_contract=PASS common_collision_gap=>= context
guaranteed_common_gap_collision_pair_count=0 guaranteed_common_gap_multiple_pair_count=0 total_bank_collision_pair_count=0
prefix_collision_reports=... first_exact_pass_prefix_length=...
subfamily_pass_reports=... smallest_pass_subfamily_size=...
real_phase_margin=PASS worst_margin_radians=...
real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050,AIRA-T0053,AIRA-T0054,AIRA-T0055,AIRA-T0056,AIRA-T0057,AIRA-T0058,AIRA-T0059 (unwrapped, signed full-turn, turn-separation, bank-level no-near-turn, turn-ratio scaling, finite-context margin consequence, context-plus-margin transfer, integer/rational-turn-ratio guardrails, positive rational finite-context certificate and exact rational boundary, generated-gap enumeration, and floor/ceiling witness precursors only; not a Diophantine proof)
theorem_ids=AIRA-T0021,AIRA-T0022,AIRA-T0023,AIRA-T0024,AIRA-T0025,AIRA-T0026,AIRA-T0027,AIRA-T0028,AIRA-T0034,AIRA-T0035,AIRA-T0036,AIRA-T0046,AIRA-T0048,AIRA-T0049,AIRA-T0051,AIRA-T0052
```

`exact_discrete_contract=PASS` means the integer-period phase bank has no all-channel collision among unequal positions inside the inspected context. The Lean-backed theorem spine proves that all-channel collision is equivalent to the period-bank LCM dividing the position gap, and `AIRA-T0046` proves the no-collision pass condition when that LCM reaches the context.

`real_phase_margin=PASS` means the numerical scan did not find a real-valued near-collision below the chosen tolerance. This is not a Lean proof over real trigonometric RoPE.

`proof_layers=...` separates the evidence types. The exact integer-period layer is theorem-backed for the declared discretized phase-bank model. The rational/discretized finite-margin layer points to the named `1/4099` preset. The interval-backed standard-RoPE layer points to the tiny channel-0 context-7 seed. The numerical scan remains diagnostic even when it passes.

`real_phase_formal_precursors=AIRA-T0029,AIRA-T0030,AIRA-T0031,AIRA-T0032,AIRA-T0033,AIRA-T0037,AIRA-T0038,AIRA-T0039,AIRA-T0040,AIRA-T0041,AIRA-T0042,AIRA-T0043,AIRA-T0044,AIRA-T0045,AIRA-T0047,AIRA-T0050,AIRA-T0053,AIRA-T0054,AIRA-T0055,AIRA-T0056,AIRA-T0057,AIRA-T0058,AIRA-T0059` means Lean has proved the unwrapped one-channel real phase-gap arithmetic, signed full-turn-multiple window precursors, the bank-level theorem shape that one proved separating channel rules out an all-channel near-turn collision at smaller tolerance, the turn-ratio scaling bridge into nearest-integer Diophantine error, the one-channel and bank-level consequences of a finite-context turn-ratio margin certificate, conservative context/margin/context-plus-margin transfer laws, the guardrails that integer and natural-rational turn ratios cannot provide a positive finite-context margin once their exact-return gap is in scope, the positive `1 / denominator` finite-context certificate for reduced natural rational ratios before the denominator gap enters scope, the exact boundary saying that certificate holds iff the inspected context stays at or below the denominator, the bridge from the abstract finite-context predicate to generated positive gaps in `List.range context`, and the floor/ceiling witness bridge reducing each fixed-gap integer-turn check to two nearest-integer witnesses. It is not a Diophantine proof that arbitrary RoPE gaps satisfy the margin predicate and does not certify the numerical scan.

## Named Rational Margin Certificate

The first end-to-end real-phase-margin-shaped certificate is a rational/discretized turn-ratio preset, not the standard irrational RoPE schedule:

```python
from circle_math.applications import certify_rational_preset_4099

certificate = certify_rational_preset_4099()
print(certificate.name)
print(certificate.pass_certificate)
print(certificate.certified_margin)
print(certificate.theorem_ids)
```

Expected meaning:

```text
rational_turn_ratio_1_4099_context_4096
True
1 / 4099, represented as a Python float
AIRA-T0056,AIRA-T0059,AIRA-T0060,AIRA-T0061,AIRA-T0062
```

Lean proves that the declared turn ratio `1/4099` has finite-context nearest-integer margin `1/4099` for every positive gap below context `4096`, then proves the corresponding no-near-turn consequence. This is useful as the first complete certificate shape. It is not a proof that the standard `1 / (2π)` RoPE channel has the same kind of finite-context margin.

## Named Standard RoPE Interval Seed

The first theorem-backed certificate for the genuine standard channel is intentionally tiny:

```python
from circle_math.applications import certify_standard_channel0_interval_seed

certificate = certify_standard_channel0_interval_seed()
print(certificate.name)
print(certificate.pass_certificate)
print(certificate.certified_margin)
print(certificate.theorem_ids)
```

Expected meaning:

```text
standard_rope_channel0_interval_context_4096
True
1/104219
AIRA-T0063,AIRA-T0064,AIRA-T0065,...,AIRA-T0122
```

Lean proves that channel 0 with standard turn ratio `1 / (2π)` has finite-context nearest-integer margin `1/104219` for gaps `1` through `4095`. The sharp 4k seed uses the 20-decimal enclosure `10^20*gap/628318530717958647694 <= gap/(2π) <= 10^20*gap/628318530717958647692`, split across computed integer cells `0` through `651`. Lean also proves that the earlier `1/1024` margin stops at gap `710`, that the doubled D9 margin `1/65536` is impossible for any context containing gap `710`, that the nearby larger D10 margin `1/104000` is impossible once that gap is in scope, and that the adjacent larger D11 margin `1/104218` is also impossible there. `AIRA-T0118` generalizes the last obstruction to every advertised margin at or above `1/104218`; `AIRA-T0119` packages the 4k bracket: `1/104219` is proved, while `1/104218` and larger margins are impossible. `AIRA-T0120` through `AIRA-T0122` then lower the margin to `1/104220` and extend the same one-channel interval-certificate method to context `8192`. `AIRA-T0102`, `AIRA-T0108`, and `AIRA-T0114` add conditional bank-level bridges when a finite real-phase bank contains the standard channel-0 angular frequency. `AIRA-T0117` packages the D11 bridge for banks whose first channel is standard channel 0. This is real standard-RoPE theorem content, but still channel-0 based; it is not a proof for 128k or every channel in the whole multi-channel bank.

For audit and future Lean work, the sidecar also exposes interval plans:

```python
from fractions import Fraction
from circle_math.applications import plan_standard_channel0_interval_bands

plan_standard_channel0_interval_bands(
    pi_bound_preset="d4",
    margin=Fraction(1, 512),
).theorem_status  # lean_proved_interval_seed_AIRA-T0087_to_AIRA-T0089

plan_standard_channel0_interval_bands(
    pi_bound_preset="d6",
    margin=Fraction(1, 1024),
).theorem_status  # lean_proved_interval_seed_AIRA-T0090_to_AIRA-T0094

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104219),
).theorem_status  # lean_proved_interval_seed_AIRA-T0111_to_AIRA-T0114

plan_standard_channel0_interval_bands(
    pi_bound_preset="d20",
    margin=Fraction(1, 104220),
    max_context_length=8192,
).theorem_status  # lean_proved_interval_seed_AIRA-T0120_to_AIRA-T0122
```

The d4, d6, conservative d20 `1/131072`, tighter d20 `1/105000`, sharp d20 `1/104219`, and 8k d20 `1/104220` plans have been converted into Lean proof. Future plans are exact-rational source data only until matching declarations compile and manifest ids are marked proved.

If the exact discrete contract fails, the output includes a common collision gap and sample colliding pairs.
It also reports `guaranteed_common_gap_collision_pair_count`, the number of starts whose paired position is exactly the common collision gap ahead, and `guaranteed_common_gap_multiple_pair_count`, the corresponding guaranteed family summed over every positive in-context multiple of that gap. `total_bank_collision_pair_count` is the exact all-channel count for the declared integer-period bank, backed by the period-bank LCM theorem. `AIRA-T0048` proves the LCM-gap collision family, and `AIRA-T0049` proves that a positive LCM below the context gives an explicit unequal collision witness. It is not a real-valued RoPE collision count.

For each declared integer period, the JSON certificate includes `single_period_collision_pair_counts`. These are exact single-channel counts, not all-channel bank collision counts.

The JSON certificate also includes `prefix_collision_reports`, bounded summaries for the first few channel prefixes. Each prefix report reuses the same `AIRA-T0036`/`AIRA-T0046`/`AIRA-T0048`/`AIRA-T0049` LCM theorem spine as the full bank, and `AIRA-T0051` proves that adding suffix channels cannot create an unequal collision once a prefix LCM reaches the inspected context. `first_exact_pass_prefix_length` tells you the first declared prefix whose integer-bank LCM already reaches the inspected context.

The certificate also includes bounded `subfamily_pass_reports` for small selected subbanks whose LCM reaches the context. `AIRA-T0052` proves the unordered selected-subbank bridge. These are still integer-period sub-bank reports, not real-valued RoPE collision proofs.

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
- bounded selected-subfamily pass reports for small declared subbanks;
- a proof-layer inventory distinguishing exact integer-period, rational/discretized, interval-backed standard-RoPE, and numerical diagnostic layers;
- exact discrete pass/fail;
- sample exact collisions when present;
- numerical real-phase margin data;
- a claim boundary.

The full CLI JSON is intentionally verbose. The paper sidecar fixture uses compact certificate summaries so the committed results stay readable while preserving pass/fail status, periods, collision gaps, counts, samples, proof layers, theorem ids, and claim boundaries.

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
