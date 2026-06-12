# RoPE Certifier Preset Results

These are proof-carrying position-contract reports for declared integer-period phase banks plus numerical real-phase margin scans. They are not model-quality, context-length, speed, memory, perplexity, or deployment claims.

| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Common-gap pairs | Total bank pairs | First pass prefix | Real margin | Worst gap | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- |
| llama_style_10000_4k | 128 | 10000 | 4096 | PASS | >= context | 0 | 0 | 5 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| llama_style_10000_128k | 128 | 10000 | 131072 | PASS | >= context | 0 | 0 | 8 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| llama_style_500000_128k | 128 | 500000 | 131072 | PASS | >= context | 0 | 0 | none | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| diagnostic_single_channel_10000_20 | 2 | 10000 | 20 | FAIL | 6 | 14 | 24 | none | PASS (0.150444 rad) | 19 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| diagnostic_two_channel_36_128 | 4 | 36 | 128 | FAIL | 114 | 14 | 14 | none | PASS (0.0973355 rad) | 113 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| diagnostic_prefix_pass_4_128 | 8 | 4 | 128 | PASS | >= context | 0 | 0 | 3 | PASS (0.606456 rad) | 88 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |
| diagnostic_shared_factor_25_64 | 6 | 25 | 64 | FAIL | 54 | 10 | 10 | none | PASS (0.548668 rad) | 56 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034, AIRA-T0035, AIRA-T0036, AIRA-T0046, AIRA-T0048, AIRA-T0049, AIRA-T0051 |

Reproduce with:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```
