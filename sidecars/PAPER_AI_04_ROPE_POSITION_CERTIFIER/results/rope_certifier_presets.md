# RoPE Certifier Preset Results

These are proof-carrying position-contract reports for declared integer-period phase banks plus numerical real-phase margin scans. They are not model-quality, context-length, speed, memory, perplexity, or deployment claims.

| Preset | Head dim | Base | Context | Exact discrete | Common collision gap | Guaranteed common-gap pairs | Real margin | Worst gap | Theorem ids |
| --- | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- |
| llama_style_10000_4k | 128 | 10000 | 4096 | PASS | >= context | 0 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034 |
| llama_style_10000_128k | 128 | 10000 | 131072 | PASS | >= context | 0 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034 |
| llama_style_500000_128k | 128 | 500000 | 131072 | PASS | >= context | 0 | PASS (1 rad) | 1 | AIRA-T0021, AIRA-T0022, AIRA-T0023, AIRA-T0024, AIRA-T0025, AIRA-T0026, AIRA-T0027, AIRA-T0028, AIRA-T0034 |

Reproduce with:

```bash
python sidecars/PAPER_AI_04_ROPE_POSITION_CERTIFIER/python/benchmark_rope_certifier.py --format markdown
```
