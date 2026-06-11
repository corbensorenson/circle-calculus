# Theseus-Hive AI Transfer Lane

Status: planning and integration note. This is not proof status and not a model-quality claim.

## Purpose

Circle Calculus should become useful for the user's active AI work, not only an abstract math project. The near-term target is a disciplined transfer lane from Circle Calculus into the local Theseus-Hive system:

```text
Circle proofs and fixtures
  -> schedule / memory / routing contracts
  -> Theseus-Hive private experiments
  -> reports with ordinary baselines and negative controls
  -> only then paper or Living Book claims
```

The contribution to aim for is proof-carrying AI infrastructure: recurrence schedules, cyclic memory addresses, route budgets, strided coverage, phase features, and circulant mixers that are explicit enough to be checked, benchmarked, and audited.

## Local Theseus-Hive Context Reviewed

This note started from a read-only pass over the local Theseus-Hive project. The current local bridge is now additive only: a report-only consumer was added in the companion Theseus-Hive workspace without modifying existing dirty benchmark, data, or Rust files.

Reviewed surfaces:

- `README.md`
- `docs/PROJECT_STATE.md`
- `docs/TOP_TO_BOTTOM_ARCHITECTURE.md`
- `docs/THESEUS_HIVE.md`
- `docs/COGNITIVE_LOOP_CLOSURE.md`
- `docs/CAPABILITY_RATCHET.md`
- `docs/TRAINING_EVALS_BENCHMARKS.md`
- `docs/CONTEXT_PACKET_MEMORY.md`
- `crates/symliquid-cli/src/code_lm_closure/state_sequence_features.rs`
- `crates/symliquid-cli/src/code_lm_closure/work_budget.rs`
- `crates/symliquid-cli/src/code_lm_closure/candidate_fanout.rs`
- `crates/symliquid-cli/src/code_lm_closure/candidate_fanout/sts_bridge.rs`

The important architectural fit is this: Theseus-Hive already has a ratchet, private-transfer gates, context packet memory, route/fanout machinery, STS-conditioned candidate generation, work-budget admission, loop closure, and CPU/MLX local execution boundaries, with CUDA treated as external portability or baseline context. Circle Calculus should plug into those as verified structure and benchmark pressure, not as a vague claim that circles make AI better.

## Transfer Targets

### 1. Phase-indexed recurrence contracts

Circle side:

- theorem ids: `AIM-T0006` through `AIM-T0058`;
- fixtures: `AIM-B0003`, `AIM-B0011`, `AIM-B0005`, `AIM-B0012`, `AIM-B0006`, `AIM-B0007`, `AIM-B0013`, `AIM-B0008`, `AIM-B0014`, `AIM-B0009`, `AIM-B0015`;
- paper: `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`.

Theseus-Hive side:

- loop-closure tools;
- recursive/looped model experiments;
- per-token or per-task work budgets;
- overthinking and exit-boundary diagnostics.

First useful artifact:

```text
circle_recurrence_contract.json
```

Fields should include period, sample id, token id when relevant, required depth, selected budget, loop phase, active-step set, exit step, overthinking boundary, source fixture/report, and whether the finite contract passed.

Guardrail: Lean can certify finite schedule arithmetic. It cannot certify reasoning quality, perplexity, context length, or throughput.

### 2. Strided candidate fanout and sparse coverage

Circle side:

- theorem ids: `AIT-T0001`, `AIT-T0002`, `AIT-T0003`;
- fixture: `AIM-B0002`;
- paper: `papers/applications/PAPER_AI_02_COIL_ATTENTION_AND_MEMORY.md`.

Theseus-Hive side:

- candidate fanout;
- STS-conditioned branch generation;
- private transfer residual lanes;
- work-budget admission.

Experiment:

Compare ordinary sequential, random, round-robin, local-window, and stride-family fanout policies. A stride-family policy is only interesting if it reports coverage, gcd, candidate budget, duplicate rate, rejection reasons, and private-transfer effect. Coprime strides should be treated as a coverage guarantee, not as a quality guarantee.

Guardrail: full coverage of candidate positions is not full semantic coverage.

### 3. Cyclic memory with residue plus winding

Circle side:

- theorem ids: `AIM-T0001` through `AIM-T0005`;
- fixture: `AIM-B0001`;
- S1 winding paper and theorem spine for residue/winding separation.

Theseus-Hive side:

- context packet memory;
- routing memory;
- bounded worker state;
- long-horizon task traces.

Experiment:

Add an offline analyzer that maps packet or route events into:

```text
slot = event_index mod bank_size
winding = event_index div bank_size
```

Then compare slot-only retention, slot-plus-winding retention, score-based retention, and ordinary FIFO/LRU baselines on private synthetic traces. The useful Circle contribution is not a new memory system by itself; it is alias visibility and provenance.

Guardrail: residue-only memory aliases by construction. Winding/provenance must stay visible.

### 4. MultiCoil feature tags for Code LM state sequences

Circle side:

- theorem ids: `AIA-T0001` through `AIA-T0005`, `AIT-T0004`, `AIT-T0005`;
- fixtures: `AIA-B0004`, `AIA-B0005`, `AIRA-B0002`, `AIRA-B0003`;
- papers: `PAPER_AI_01` and `PAPER_AI_03`.

Theseus-Hive side:

- dynamic state-sequence decoder features such as `pos`, `pos_bucket`, previous-token features, and category-position features.

Experiment:

Add optional private-only feature tags:

```text
phase:p:position_mod_p
phase_tuple:p_q:position_mod_p|position_mod_q
relative_phase:p:query_minus_key_mod_p
```

Evaluate them against existing position buckets, learned-position controls, wrong-period controls, and nonperiodic controls. These features should be off by default until an experiment shows value.

Guardrail: phase tags are feature engineering, not model understanding.

### 5. Circulant and block-cyclic lightweight mixers

Circle side:

- theorem ids: `AIT-T0006`, `AIT-T0007`, `AIT-T0008`, `AIT-T0009`, `AIRA-T0001` through `AIRA-T0005`;
- fixtures: `AIRA-B0004`, `AIRA-B0005`;
- paper: `papers/applications/PAPER_AI_03_COILRA_AND_MULTICOIL_ROPE.md`.

Theseus-Hive side:

- small rankers;
- route heads;
- feature mixers;
- candidate scoring layers.

Experiment:

Test dense, low-rank, block-cyclic, and circulant mixers on private route/ranker tasks where shift or periodic structure is plausible. Report quality, parameter count, runtime, memory, and failure cases separately.

Guardrail: parameter reduction is not a win unless quality and runtime stay competitive on a named workload.

### 6. CGS and smallest-generator pressure

Circle side:

- generator/provenance work in Phase VII;
- proof-carrying glyph and exact-regeneration gates;
- finite search and exact-candidate count guardrails.

Theseus-Hive side:

- CGS accounting;
- loop closure;
- procedural tool cards;
- residual escrow.

Experiment:

Represent a repeated Theseus workflow as a seed-rule object:

```text
seed + rules + parameters + verifier + residuals -> regenerated artifact
```

Compare object-only storage with seed-rule storage on exact regeneration, edit distance, verification cost, and residual rate.

Guardrail: a smaller generator is not automatically better or more meaningful.

## First Milestone

The first concrete milestone is implemented as a public Circle contract pack plus a local private Theseus-Hive consumer:

```text
circle_math/applications/theseus_hive_contracts.py
scripts/export_theseus_hive_ai_contracts.py
site/data/generated/theseus_hive_ai_contracts.json
tests/test_theseus_hive_ai_contracts.py
```

Generate the public-safe contract pack with:

```bash
make theseus-ai-contracts
```

The exported pack currently contains six deterministic contract families:

- recurrence schedule and loop-exit contract;
- strided candidate-fanout coverage contract;
- cyclic memory residue-plus-winding contract;
- MultiCoil and relative-phase feature contract;
- circulant/block-cyclic mixer contract;
- seed-rule exact-regeneration contract.

The companion Theseus-Hive workspace now has a report-only consumer:

```text
../Theseus-Hive/scripts/circle_ai_contract_consumer.py
../Theseus-Hive/scripts/circle_ai_private_workload_smoke.py
../Theseus-Hive/scripts/circle_ai_private_proxy_benchmark.py
../Theseus-Hive/docs/CIRCLE_CALCULUS_TRANSFER.md
../Theseus-Hive/reports/circle_ai_contract_consumer.json
../Theseus-Hive/reports/circle_ai_contract_consumer.md
../Theseus-Hive/reports/circle_ai_private_workload_smoke.json
../Theseus-Hive/reports/circle_ai_private_workload_smoke.md
../Theseus-Hive/reports/circle_ai_private_proxy_benchmark.json
../Theseus-Hive/reports/circle_ai_private_proxy_benchmark.md
```

Run it from Theseus-Hive with:

```bash
python scripts/circle_ai_contract_consumer.py \
  --contracts "../circle math/site/data/generated/theseus_hive_ai_contracts.json"
```

Its current state is intentionally `YELLOW`: all six contract families load, all required axes are reported, and every governance gate is report-clean, but there are not yet named private benchmark results. The generated report has `external_inference_calls = 0`, `training_mutation = false`, `promotion_evidence = false`, and `public_calibration_used = false`.

The companion smoke workload layer gives each family a stable named workload slot:

```text
circle_recurrence_budget_trace_smoke
circle_strided_candidate_coverage_smoke
circle_memory_alias_visibility_smoke
circle_phase_feature_invariance_smoke
circle_mixer_parameter_accounting_smoke
circle_seed_rule_regeneration_smoke
```

These are deterministic structural smoke checks, not model benchmarks. Their current report is also `YELLOW`: six workloads pass, `model_quality_metrics_present = false`, `external_inference_calls = 0`, `training_mutation = false`, and `promotion_evidence = false`.

The companion proxy benchmark layer then measures deterministic baseline metrics for:

```text
circle_recurrence_budget_proxy_v1
circle_candidate_fanout_proxy_v1
circle_memory_alias_proxy_v1
circle_phase_feature_proxy_v1
circle_mixer_parameter_proxy_v1
circle_seed_rule_regeneration_proxy_v1
```

That proxy report is also intentionally `YELLOW`: all six proxy benchmarks pass and deterministic proxy metrics exist, but `learned_model_quality_metrics_present = false` and `real_private_workload_results_present = false`.

The next concrete private Theseus-Hive milestone is to replace the proxy benchmarks with real private workloads:

1. Consume `site/data/generated/theseus_hive_ai_contracts.json` only as private experiment configuration, not as public-calibration data.
2. Compare recurrence contracts against fixed-depth, dense-depth, no-recurrence, and existing work-budget baselines.
3. Compare fanout contracts against sequential, random, round-robin, local-window, and existing stratified admission baselines.
4. Compare memory contracts against FIFO, LRU, score-based retention, and slot-only retention baselines.
5. Compare phase-feature contracts against existing position buckets, learned-position controls, wrong-period controls, and no-phase controls.
6. Compare mixer contracts against dense, low-rank, LoRA-style, and no-mixer baselines.
7. Compare seed-rule contracts against object-only storage and unverified tool-memory baselines.
8. Record every result as private experimental evidence until a named workload, baseline, metric, and reproducible script exist.

## ASI-Relevant Tooling Boundary

The user-facing ambition is to give Theseus-Hive better tools for the climb toward very high capability. The honest engineering interpretation is:

- make recurring cognition compilable into verified tools;
- make memory, recurrence, and routing schedules explicit instead of hidden in logs;
- attach finite contracts to loops, fanout, and generated artifacts;
- force every capability claim through ordinary baselines, private held-out pressure, negative controls, and governance gates;
- preserve provenance so future self-improvement can be audited rather than guessed.

This is ASI-relevant infrastructure, not an ASI claim. The contract pack should help Theseus-Hive become more disciplined, self-measuring, and less drift-prone; it does not itself prove intelligence growth.

## External Research Anchors

These sources motivate the baseline set; they do not prove Circle Calculus helps AI.

- Adaptive Computation Time: <https://arxiv.org/abs/1603.08983>
- Universal Transformer: <https://arxiv.org/abs/1807.03819>
- Recurrent Memory Transformer: <https://arxiv.org/abs/2207.06881>
- RoFormer / RoPE: <https://arxiv.org/abs/2104.09864>
- FNet Fourier token mixing: <https://arxiv.org/abs/2105.03824>
- Hyena Hierarchy: <https://arxiv.org/abs/2302.10866>
- Mamba selective state spaces: <https://arxiv.org/abs/2312.00752>
- Mixture-of-Recursions: <https://arxiv.org/abs/2507.10524>

## Claim Boundary

The public claim should be:

Circle Calculus can provide proof-linked finite contracts for cyclic AI schedules, memory addresses, sparse coverage, phase features, and circulant structure, and Theseus-Hive is a natural testbed for whether those contracts improve real private-transfer workflows.

The public claim should not be:

Circle Calculus has already improved Theseus-Hive, solved recursive transformers, improved LLM reasoning, extended context length, reduced inference cost, or beaten ordinary AI baselines.
