# RoPE Certifier Preset Results

These are proof-carrying position-contract reports for declared integer-period phase banks plus numerical real-phase margin scans. They are not model-quality, context-length, speed, memory, perplexity, or deployment claims.

## Named Rational Margin Certificate

| Name | Ratio | Context | Certified margin | Status | Theorem ids |
| --- | --- | ---: | ---: | --- | --- |
| rational_turn_ratio_1_4099_context_4096 | 1/4099 | 4096 | 0.000243961941937 | PASS | AIRA-T0056, AIRA-T0059, AIRA-T0060, AIRA-T0061, AIRA-T0062 |

This is a theorem-backed rational/discretized turn-ratio certificate. It is not a proof of the standard irrational real RoPE schedule unless that schedule is explicitly replaced by the declared rational ratio.

## Named Standard RoPE Interval Seed

| Name | Turn ratio | Context | Certified margin | Pi bounds | Status | Theorem ids |
| --- | --- | ---: | --- | --- | --- | --- |
| standard_rope_channel0_interval_context_6 | 1/(2*pi) | 6 | 1/8 | 3 < pi <= 4 | PASS | AIRA-T0063, AIRA-T0064, AIRA-T0065, AIRA-T0066, AIRA-T0067 |

This is a theorem-backed interval certificate for the genuine standard RoPE channel-0 turn ratio over context 6 only. It is not a full standard RoPE bank certificate and does not certify 512, 4096, or larger contexts.

## RoPE Preset Diagnostics

| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Common-gap pairs | Total bank pairs | First pass prefix | Smallest pass subfamily | Real margin | Worst gap | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| llama_style_10000_4k | 128 | 10000 | 4096 | PASS | >= context | 0 | 0 | 5 | 1 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| llama_style_10000_128k | 128 | 10000 | 131072 | PASS | >= context | 0 | 0 | 8 | 2 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| llama_style_500000_128k | 128 | 500000 | 131072 | PASS | >= context | 0 | 0 | none | 1 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_single_channel_10000_20 | 2 | 10000 | 20 | FAIL | 6 | 14 | 24 | none | none | PASS (0.150444 rad) | 19 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_two_channel_36_128 | 4 | 36 | 128 | FAIL | 114 | 14 | 14 | none | none | PASS (0.0973355 rad) | 113 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_prefix_pass_4_128 | 8 | 4 | 128 | PASS | >= context | 0 | 0 | 3 | 2 | PASS (0.606456 rad) | 88 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| diagnostic_shared_factor_25_64 | 6 | 25 | 64 | FAIL | 54 | 10 | 10 | none | none | PASS (0.548668 rad) | 56 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |

## Exact Phase-Bank Diagnostics

These exact-only presets exercise quantized/shared-factor and interpolation-style scaled-period boundary cases. They are declared integer-period phase-bank contracts, not real-valued RoPE claims.

| Preset | Periods | Context | Exact discrete | Common collision gap | Total bank pairs | First pass prefix | Smallest pass subfamily | Theorem ids |
| --- | --- | ---: | --- | --- | ---: | --- | --- | --- |
| quantized_shared_factor_256 | 32,48,96 | 256 | FAIL | 96 | 224 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| quantized_lcm_boundary_fail_241 | 15,16 | 241 | FAIL | 240 | 1 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| interpolated_x4_boundary_pass_960 | 60,64 | 960 | PASS | >= context | 0 | 2 | 2 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |
| interpolated_x4_boundary_fail_961 | 60,64 | 961 | FAIL | 960 | 1 | none | none | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051, AIRA-T0052 |

Reproduce with:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```
