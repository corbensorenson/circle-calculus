# RoPE Certifier Results Note

This is the short engineering-facing summary of the current Circle Calculus RoPE certifier findings. It is for deciding whether the contract is useful before reading the full paper, Lean source, or Living Book audit trail.

## Result In One Paragraph

The RoPE certifier currently gives theorem-linked exact collision reports for declared integer-period phase banks, plus a separate theorem-backed one-channel standard-RoPE frontier. The model-like rounded integer-period presets pass the exact discrete contract at 4k and 128k contexts; the diagnostic presets fail exactly where their shared periods force all-channel collisions. For genuine standard RoPE, the proved real-phase result is narrower but more mathematical: standard channel 0 has a Lean-proved margin of `1/328459` through context `196608`, margins at or above `1/328458` are impossible over the D19 range `103993 < context <= 196608`, and the open interval between those thresholds is deliberately not claimed.

## Current Exact Discrete Findings

These rows are about the declared integer-period phase-bank model. A `PASS` means no unequal pair of positions inside the context collides in every declared channel. A `FAIL` gives the exact shared collision gap and exact pair count for that declared model.

| Preset | Context | Exact discrete result | Main evidence |
| --- | ---: | --- | --- |
| `llama_style_10000_4k` | 4096 | PASS | common gap is outside context; first reported passing prefix has length `5` |
| `llama_style_10000_128k` | 131072 | PASS | common gap is outside context; first reported passing prefix has length `8` |
| `llama_style_500000_128k` | 131072 | PASS | common gap is outside context; a bounded subfamily already passes |
| `diagnostic_single_channel_10000_20` | 20 | FAIL | common gap `6`; total bank collision-pair count `24` |
| `diagnostic_two_channel_36_128` | 128 | FAIL | common gap `114`; total bank collision-pair count `14` |
| `diagnostic_shared_factor_25_64` | 64 | FAIL | common gap `54`; total bank collision-pair count `10` |

The exact phase-bank diagnostics also include quantized and interpolation-style boundary cases:

| Preset | Periods | Context | Result | Evidence |
| --- | --- | ---: | --- | --- |
| `quantized_shared_factor_256` | `32,48,96` | 256 | FAIL | common gap `96`; total bank collision-pair count `224` |
| `quantized_lcm_boundary_fail_241` | `15,16` | 241 | FAIL | common gap `240`; one exact all-channel collision pair |
| `interpolated_x4_boundary_pass_960` | `60,64` | 960 | PASS | LCM boundary is outside the inspected context |
| `interpolated_x4_boundary_fail_961` | `60,64` | 961 | FAIL | common gap `960`; one exact all-channel collision pair |

The main exact integer-period theorem spine is `AIRA-T0021` through `AIRA-T0028`, `AIRA-T0034` through `AIRA-T0036`, `AIRA-T0046`, `AIRA-T0048`, `AIRA-T0049`, `AIRA-T0051`, `AIRA-T0052`, `AIRA-T0174` through `AIRA-T0176`, `AIRA-T0203` through `AIRA-T0207`, and `AIRA-T0210` through `AIRA-T0213`.

## Current Real-Phase Frontier

The standard real-valued RoPE lane is intentionally separated from the exact integer-period lane.

What is theorem-backed now:

- `AIRA-T0168` through `AIRA-T0173` prove the generated D19 standard channel-0 seed at margin `1/328459` through context `196608`.
- `AIRA-T0208` and `AIRA-T0209` package the D19 context-range bracket for `103993 < context <= 196608`.
- `AIRA-T0216` through `AIRA-T0221` turn that bracket into the request classifier: margins at or below `1/328459` are proved, margins at or above `1/328458` are impossible, and the open interval between them is undecided.
- `AIRA-T0232` proves that the undecided open interval has exact width `1/107884986222`.
- `AIRA-T0233` proves the in-range semantic trichotomy: every request is exactly one of proved, impossible, or undecided.
- `AIRA-T0234` through `AIRA-T0237` transfer the proved branch to a conditional first-channel bank contract and ordinary radian-bank form.
- `AIRA-T0238` proves the public probe margin `2/656917` lies inside the undecided open gap.
- `AIRA-T0239` and `AIRA-T0240` give the Dirichlet guardrail: every nontrivial finite context has an in-context nearest-integer witness with error at most `1/context`, so no finite-context margin strictly above `1/context` can hold.

This is a real theorem program, but it is still a one-channel frontier. It is not yet a full all-channel standard-RoPE bank theorem.

## How To Reproduce

Run the exact preset table:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```

Run individual exact contracts:

```bash
python scripts/rope_certify.py --preset llama_style_10000_128k --format json
python scripts/rope_certify.py --preset diagnostic_two_channel_36_128 --format json
python scripts/phase_bank_certify.py --preset interpolated_x4_boundary_fail_961
```

Check the proof and Python implementation:

```bash
lake build Circle.Applications.RoPECertifier
python -m pytest tests/test_rope_certifier.py -q
```

Check the downstream contract-pack surface for the D19 frontier:

```bash
python scripts/circle_ai_contract_ready.py \
  --kind rope_position_distinguishability \
  --digest \
  --field d19_proved_request_status \
  --field d19_impossible_request_status \
  --field d19_undecided_request_status \
  --field d19_proved_first_channel_radian_bank_form \
  --field d19_undecided_probe_margin_in_open_gap \
  --field real_phase_dirichlet_witness_guardrail \
  --field real_phase_margin_ceiling_guardrail \
  --include-recommendations
```

## What This Means For AI Work

The useful deliverable is not "RoPE is better" or "Circle Calculus improves model quality." The useful deliverable is a proof-carrying contract shape:

```text
declared positional scheme
  -> finite phase-bank model or bounded real-phase request
  -> exact collision or margin question
  -> theorem ids
  -> machine-readable certificate
  -> explicit non-claims
```

That shape can catch all-channel exact collisions in declared phase banks, expose boundary failures in quantized or interpolation-style variants, and give downstream systems a theorem-backed receipt they can pin without importing Lean.

## Non-Claims

This note does not claim:

- that raw floating-point RoPE has exact integer periods;
- that the exact integer-period results prove the full real-valued RoPE schedule;
- that the one-channel D19 standard-RoPE frontier proves a full all-channel bank theorem;
- that a passing certificate improves context length, perplexity, reasoning quality, speed, memory, or training stability;
- that numerical scans are formal proofs;
- that this is enough by itself to deploy or recommend a positional scheme.

The current contribution is narrower and useful: it makes position-distinguishability assumptions explicit, executable, theorem-linked, and auditable.

## Source Trail

- Quickstart: `docs/ROPE_CERTIFIER_QUICKSTART.md`
- Review packet: `docs/ROPE_CERTIFIER_REVIEW_PACKET.md`
- Paper: `papers/applications/PAPER_AI_04_ROPE_POSITION_CERTIFIER.md`
- Living Book lesson: `site/chapters/applications/rope_certifier.qmd`
- Lean: `Circle/Applications/RoPECertifier.lean`
- Generated Lean certificates: `Circle/Applications/RoPEGeneratedCertificates.lean`
- Python: `circle_math/applications/rope_certifier.py`
- Exact phase-bank CLI: `scripts/phase_bank_certify.py`
- Generated fixtures: `sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/results/rope_certifier_presets.md`
