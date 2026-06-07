# Looped And Recursive Transformer Research Note

Date researched: 2026-06-06

Purpose: preserve the online research context behind the Circle AI looped/recursive transformer roadmap lane without turning the repository into a loose transcript archive.

## Sources Checked

- Universal Transformers, arXiv:1807.03819, https://arxiv.org/abs/1807.03819
- Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention, arXiv:2006.16236, https://arxiv.org/abs/2006.16236
- Recurrent Memory Transformer, arXiv:2207.06881, https://arxiv.org/abs/2207.06881
- Looped Transformers are Better at Learning Learning Algorithms, arXiv:2311.12424, https://arxiv.org/abs/2311.12424
- RWKV: Reinventing RNNs for the Transformer Era, arXiv:2305.13048, https://arxiv.org/abs/2305.13048
- Mamba: Linear-Time Sequence Modeling with Selective State Spaces, arXiv:2312.00752, https://arxiv.org/abs/2312.00752
- Looped Transformers for Length Generalization, arXiv:2409.15647, https://arxiv.org/abs/2409.15647
- LoopFormer: Elastic-Depth Looped Transformers for Latent Reasoning via Shortcut Modulation, arXiv:2602.11451, https://arxiv.org/abs/2602.11451
- SpiralFormer: Looped Transformers Can Learn Hierarchical Dependencies via Multi-Resolution Recursion, arXiv:2602.11698, https://arxiv.org/abs/2602.11698
- Loop, Think, & Generalize: Implicit Reasoning in Recurrent-Depth Transformers, arXiv:2604.07822, https://arxiv.org/abs/2604.07822
- Parcae: Scaling Laws For Stable Looped Language Models, arXiv:2604.12946, https://arxiv.org/abs/2604.12946
- How Much Is One Recurrence Worth? Iso-Depth Scaling Laws for Looped Language Models, arXiv:2604.21106, https://arxiv.org/abs/2604.21106
- Sparse Layers are Critical to Scaling Looped Language Models, arXiv:2605.09165, https://arxiv.org/abs/2605.09165
- Training-Free Looped Transformers, arXiv:2605.23872, https://arxiv.org/abs/2605.23872

## Synthesis

Looped and recursive transformer work is now a serious active AI direction. The shared theme is decoupling parameter depth from compute depth: a model can reuse one or more blocks across recurrence steps, sometimes with adaptive exits, memory tokens, sparse expert routing, shortcut consistency, damped update rules, or multi-resolution schedules.

The immediate Circle Calculus opportunity is not to claim a better language model. The tractable opportunity is to make recurrence explicit:

- loop step as a finite phase channel,
- recurrence schedule as a coil-like traversal through a shared block,
- early-exit points as closure/halting certificates,
- overthinking as a measured failure boundary,
- loop-state provenance as a manifest-linked trace,
- sparse/MoE loop routing as a phase-conditioned or divergence-tracked path,
- multi-resolution recursion as nested coils over compressed and full token views.

## Proposed Circle AI Work

Add a looped/recursive transformer lane under the dedicated Circle AI program:

1. Define a finite recurrence schedule object and dictionary terms. Initial terms: `COMMON-0052` through `COMMON-0055`.
2. Add a Python fixture that compares fixed-depth, looped-depth, adaptive-exit, and over-looped controls on a small deterministic task. Initial fixture: `AIM-B0003`, implemented by `circle_math.applications.circle_ai.run_looped_recurrence_benchmark` and `sidecars/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY/python/benchmark_looped_recurrence.py`.
3. Add a Lean seed for bounded loop phase and recurrence-budget indexing if it is not already covered by phase-channel facts.
4. Add a Living Book lesson that teaches recurrence depth, exit certificates, and overthinking guardrails without claiming model quality.
5. Later, add MLX prototypes against ordinary dense, Universal Transformer, looped-transformer, recurrent-memory, sparse/MoE, RWKV/Mamba-style, and standard transformer baselines.

## Guardrail

All looped/recursive transformer claims remain planned or exploratory until the exact workload, ordinary baseline, metric, reproducible script, and proof-status boundary exist. Lean can certify schedule/index facts; it does not certify model accuracy, reasoning depth, benchmark quality, or inference speed.
