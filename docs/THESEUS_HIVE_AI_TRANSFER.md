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
../Theseus-Hive/scripts/circle_ai_real_workload_attachments.py
../Theseus-Hive/scripts/circle_ai_scored_private_benchmarks.py
../Theseus-Hive/docs/CIRCLE_CALCULUS_TRANSFER.md
../Theseus-Hive/reports/circle_ai_contract_consumer.json
../Theseus-Hive/reports/circle_ai_contract_consumer.md
../Theseus-Hive/reports/circle_ai_private_workload_smoke.json
../Theseus-Hive/reports/circle_ai_private_workload_smoke.md
../Theseus-Hive/reports/circle_ai_private_proxy_benchmark.json
../Theseus-Hive/reports/circle_ai_private_proxy_benchmark.md
../Theseus-Hive/reports/circle_ai_real_workload_attachments.json
../Theseus-Hive/reports/circle_ai_real_workload_attachments.md
../Theseus-Hive/reports/circle_ai_scored_private_benchmarks.json
../Theseus-Hive/reports/circle_ai_scored_private_benchmarks.md
../Theseus-Hive/reports/circle_trace_lane_integrity_audit.json
../Theseus-Hive/reports/circle_trace_lane_integrity_audit.md
```

When the generated contract pack exists beside the private Theseus-Hive
workspace, `scripts/run_capability_ratchet.py` now runs the consumer, structural
smoke, deterministic proxy, and aggregate real-workload attachment layers as
part of the compiled local ratchet. The scored private benchmark layer remains
explicitly data-gated and should be run only when the required private
candidate, router, context, and provenance artifacts are present.
The same compiled ratchet now runs `scripts/circle_ai_lane_integrity_audit.py`
to verify the contract-pack gate, safe compiled layers, output map, workflow
classifier entries, tool cards, and the non-compiled status of scored/private
maintenance layers.

Run it from Theseus-Hive with:

```bash
python scripts/circle_ai_contract_consumer.py \
  --contracts "../circle math/site/data/generated/theseus_hive_ai_contracts.json"
```

Its current state is intentionally `YELLOW`: all six contract families load, all required axes are reported, and every governance gate is report-clean, but there are not yet named private benchmark results. The generated report has `external_inference_calls = 0`, `training_mutation = false`, `promotion_evidence = false`, and `public_calibration_used = false`.

Run the aggregate local artifact attachment layer from Theseus-Hive with:

```bash
python scripts/circle_ai_real_workload_attachments.py \
  --contracts "../circle math/site/data/generated/theseus_hive_ai_contracts.json"
```

When the script is executed from a clean companion worktree but should read the active private workspace, pass `--data-root` to that local Theseus-Hive checkout.

Run the first scored private benchmark layer with:

```bash
python scripts/circle_ai_scored_private_benchmarks.py \
  --contracts "../circle math/site/data/generated/theseus_hive_ai_contracts.json"
```

The scored benchmark layer currently implements twelve ids:

```text
circle_candidate_fanout_scored_manifest_v1
circle_candidate_fanout_semantic_frontier_v1
circle_candidate_fanout_equal_budget_semantic_v1
circle_recurrence_work_budget_semantic_v1
circle_memory_context_packet_retrieval_v1
circle_phase_feature_sequence_ablation_v1
circle_mixer_route_ranker_ablation_v1
circle_mixer_router_head_attachment_v1
circle_seed_rule_exact_regeneration_v1
circle_seed_rule_source_change_stress_v1
circle_seed_rule_workflow_tool_card_rebuild_v1
circle_seed_rule_update_cycle_effort_v1
```

The first compares Circle striding against sequential fanout, round-robin fanout, local-window selection, deterministic-random-like selection, and mode-stratified existing selection on private candidate-manifest score and gate fields. The second joins existing private frontier score reports to candidate manifests and reports semantic pass-rate context. The third freshly executes equal-budget candidate selections against local private heldout tests and exports aggregate-only pass-rate/runtime counters. The fourth treats the exported recurrence contract as a deterministic work-budget schedule and compares it with ordinary fixed-depth baselines under those same local private heldout tests. The fifth reads the local context-packet ledger and compares residue-plus-winding memory against ordinary context-packet retention baselines without exporting packet text. The sixth reads private sequence/category rows and compares exported Circle phase periods with no-phase, wrong-period, and ordinary position-bucket controls without exporting labels or row content. The seventh reads local Octopus router traces and compares Circle circulant/block-cyclic mixer transforms with dense, low-rank, and no-mixer controls without exporting task text, feature names, label names, or model weights. The eighth attaches those same mixer policies to current Octopus router-head holdout decisions and exports only aggregate decision agreement and accuracy. The ninth reads local provenance/tool-memory report summaries and compares Circle seed-rule-with-verifier regeneration with object-only storage, unverified-template, and freeform controls over safe artifact envelopes without exporting artifact bodies, packet text, command text, model weights, row content, code, tests, or private payloads. The tenth stress-tests the same seed-rule provenance layer under deterministic source-change and downstream-reuse scenarios over safe hashed envelopes. The eleventh rebuilds a safe hashed workflow/tool-card envelope from workflow compiler, tool registry, hook, routing, update, artifact, and benchmark-card sources. The twelfth instruments safe update-cycle ledgers for runtime, human-edit-minute, review-step, and maintenance-mode field availability. Its current state is still `YELLOW`: `scored_private_candidate_benchmark_results_present = true`, `semantic_pass_rate_present = true`, `fresh_equal_budget_semantic_results_present = true`, `scored_recurrence_budget_results_present = true`, `scored_memory_context_results_present = true`, `scored_phase_feature_results_present = true`, `scored_mixer_route_ranker_results_present = true`, `scored_mixer_router_head_attachment_present = true`, `scored_seed_rule_regeneration_results_present = true`, `scored_seed_rule_stress_results_present = true`, `scored_seed_rule_workflow_rebuild_results_present = true`, `update_cycle_effort_instrumented = true`, `learned_model_quality_metrics_present = false`, `external_inference_calls = 0`, `training_mutation = false`, `promotion_evidence = false`, and `private_data_exported = false`.

The semantic context is useful but not a win claim. The attached score report has full-inventory pass rate `1.0`, frontier-only pass rate `0.961538`, same-seed control pass rate `0.057692`, Circle stride budget-one pass rate `1.0`, sequential rank-one pass rate `1.0`, and direct global-contract-path projection budget-two pass rate `0.038462`. That last number is evidence that the exported global fanout path should not be naively projected onto per-task candidate ranks.

The fresh equal-budget run is also useful but not a win claim. On the full private frontier, it scores `1040` tasks across `26` categories with `unscored_task_count = 0` and `policy_count = 8`. Circle stride budget-one pass rate is `1.0`, sequential rank-one pass rate is `1.0`, Circle stride budget-two pass rate is `1.0`, sequential rank-two pass rate is `1.0`, Circle best minus ordinary best is `0.0`, and both Circle stride budget-one and sequential rank-one have zero failing categories. This validates the full private execution loop while showing no advantage over the rank baseline.

The recurrence work-budget run is the first scored recurrence attachment. On the full private frontier, it scores `1040` tasks across `26` categories with `unscored_task_count = 0`, `policy_count = 7`, recurrence budget pattern `[1, 2, 3, 4, 5, 1, 2, 3]`, Circle repeating-budget pass rate `1.0`, ordinary rank-one pass rate `1.0`, Circle repeating minus ordinary rank-one `0.0`, Circle best minus ordinary best `0.0`, Circle requested budget total `2730`, ordinary rank-one requested budget total `1040`, and zero failing categories for both Circle repeating-budget and ordinary rank-one. This promotes recurrence from metadata attachment to scored private workload, but the current workload is saturated by ordinary rank-one and therefore is not a Circle advantage claim.

The context-packet memory run is the first scored memory attachment. On the local context ledger, it scores `37` packet targets with `bank_size = 8` and `retention_budget = 8`. Full residue-plus-winding identity has hit rate `1.0` with retention cost units `74`. The equal-budget Circle slot-balanced policy has hit rate `0.216216`; ordinary score-top, FIFO-recent, and slot-only-latest baselines also have hit rate `0.216216`, so Circle slot-balanced minus best ordinary is `0.0`. This promotes memory from alias metadata to scored retrieval/retention accounting, but it is not downstream memory-usefulness evidence.

The phase-feature run is the first scored phase attachment. It scores `9750` private sequence/category rows with an ordered `7800`/`1950` train/eval split across `339` aggregate categories. Circle contract periods `[5, 7]`, Circle relative period `5`, wrong periods `[6, 8]`, and no-phase majority all report accuracy `0.528205`; Circle minus wrong-period, Circle minus no-phase, and Circle minus best ordinary are all `0.0`. This promotes phase from aggregate structure to scored feature ablation, but it is not model-quality, route/ranker usefulness, or downstream task evidence.

The mixer run is the first scored route/ranker mixer attachment. It scores `94` local Octopus router trace examples with `80` train examples, `14` eval examples, `19` labelsets, `19` arm labels, feature dimension `128`, block size `8`, and low-rank dimension `8`. Existing router-head exact-set accuracy is `1.0`; no-mixer exact-set accuracy is `0.0`, dense hashed exact-set accuracy is `1.0`, low-rank hashed exact-set accuracy is `0.714286`, Circle circulant exact-set accuracy is `1.0`, and Circle block-cyclic exact-set accuracy is `1.0`. The best ordinary policy is `ordinary_dense_hashed_centroid` with parameter count `2048`; the best Circle policy is `circle_circulant_contract_mixer` with parameter count `8`, Circle minus best ordinary `0.0`, and Circle parameter ratio versus best ordinary `0.003906`. This is useful route/ranker fixture evidence, but it is not a deployed-router, runtime, memory, promotion, or general model-quality result.

The router-head mixer attachment run is one step closer to the real route-head path while staying aggregate-only. It attaches the same mixer policies to the `14` current Octopus holdout decisions: current router-head exact-set accuracy is `1.0`, no-mixer agreement is `0.0`, dense hashed agreement is `1.0`, low-rank hashed agreement is `0.714286`, Circle circulant agreement is `1.0`, and Circle block-cyclic agreement is `1.0`. The best Circle policy remains `circle_circulant_contract_mixer` with `8` counted parameters versus `2048` for the best ordinary dense policy, Circle minus current router-head accuracy `0.0`, and Circle minus best ordinary accuracy `0.0`. This is router-head decision attachment evidence only, not actual route/ranker training, runtime, memory, promotion, or model-quality evidence.

The next trainer-shadow step is now implemented on the Theseus-Hive side. `scripts/train_octopus_router_head.py` accepts pure Circle mixer modes `--circle-mixer circulant` and `--circle-mixer block_cyclic` plus residual modes `--circle-mixer circulant_residual` and `--circle-mixer block_cyclic_residual`. The pure modes replace sparse router-head features with finite cyclic channels; the residual modes keep the raw features and add cyclic channels beside them. `scripts/circle_router_head_mixer_shadow_benchmark.py` emits the aggregate private-safe benchmark id `circle_router_head_mixer_shadow_training_v1` without exporting task text, feature names, arm labels, or model weights. A private-safe Mac shadow run over the current local ORA report, arm registry, and workflow routing traces scored `14` holdout cases: baseline, pure circulant, pure block-cyclic, residual circulant, and residual block-cyclic all reported exact-set accuracy `1.0`, risk-routing accuracy `1.0`, arm micro-F1 `1.0`, exact mismatch count `0`, and `external_inference_calls = 0`; each Circle mode used `4` shared kernel parameters in this trainer path. The repeated timing/memory run used `5` repetitions per mode and all aggregate metric hashes were stable. Validation-run median elapsed times were `10.704` ms for baseline, `112.769` ms for pure circulant, `96.332` ms for pure block-cyclic, `100.91` ms for residual circulant, and `97.362` ms for residual block-cyclic; median Python `tracemalloc` peak bytes were `117078`, `335297`, `339165`, `447689`, and `438394`, respectively. The new private-safe keyword-boundary diagnostic `circle_router_head_keyword_boundary_contrastive_v1` adds `45` train and `45` holdout examples from local routing keywords without exporting task text or arm labels. On that diagnostic, the no-mixer baseline still saturates exact accuracy at `1.0`; pure circulant and pure block-cyclic drop to `0.6667`, while full-gain residual circulant and residual block-cyclic improve to `0.8667` and `0.8222` but still trail baseline. The quality-only gain sweep `circle_router_head_keyword_boundary_gain_sweep_v1` then finds residual gains `0.05`, `0.1`, `0.25`, and `0.5` preserve baseline exact accuracy on this synthetic diagnostic for both residual modes, while full gain `1.0` regresses. The new real-trace boundary diagnostic `circle_router_head_real_trace_boundary_v1` deterministically re-splits `30` private workflow routing rows into `71` train and `9` holdout examples across `5` eligible private labelsets; full-gain pure and residual Circle modes score `0.8889` exact accuracy against the no-mixer `1.0`, while `circle_router_head_real_trace_boundary_gain_sweep_v1` preserves baseline exactness only at residual gains `0.05`, `0.1`, and `0.25`, with `0.5` and `1.0` regressing. The companion coverage report `circle_router_head_real_boundary_coverage_v1` reads the same private workflow rows plus the routing-memory trace file and finds `31` compatible real rows, `12` hashed labelset bins, `7` singleton bins, `11` bins under the target of `5` rows, and at least `40` additional private rows needed before the real-boundary mixer evidence should be treated as representative. The new private collection planner `circle_router_head_trace_collection_plan_v1` consumes that coverage report and emits hashed-bin row budgets, smoke/audit commands, and no task text, arm labels, feature names, model weights, private payloads, or promotion evidence. Future autonomous-goal traces now emit the router-head-compatible fields `workflow`, safe `command` summary, `routing_pattern`, sorted `selected_arms`, matching `expected_arms`, `split`, and `success`; the private producer validates this with `python scripts/autonomous_goal_runner.py --self-test`, exposes scratch `--ledger-out` and `--routing-trace-out` paths for non-live smoke rows, and falls back to `head_router` if the arm registry is unavailable so the strict schema audit still sees a compatible row. A scratch smoke audit produced one current-schema autonomous row, one compatible router-head row, `schema_ok = true`, and zero external inference, private export, or promotion evidence. The compiled private ratchet now runs the schema audit, boundary coverage report, collection plan, and static trace-lane integrity audit after the arm registry is generated and before router-head training consumes workflow or autonomous routing-memory traces. The integrity audit checks compiled command order, output-map discoverability, workflow classifiers, and two-source trainer/tool-card wiring without reading private trace payloads. This is actual router-head training/evaluation compatibility, regression, tuning, trace-quality, coverage, and wiring evidence with diagnostic runtime and memory measurements, but still not a claim of better quality, runtime, memory, transfer, or promotion readiness.

The seed-rule regeneration run is the first scored provenance attachment. It reads `3` local provenance/tool-memory source reports and regenerates `75` safe envelope records across `6` record kinds. Object-only storage and Circle seed-rule-with-verifier both report exact regeneration rate `1.0`; Circle verifier residual count is `0`; unverified-template and freeform controls both report exact regeneration rate `0.0`. The Circle recipe length is `527` bytes versus `13291` bytes for object-only storage, a ratio of `0.039651`. This promotes seed-rule provenance from aggregate attachment to scored exact-regeneration accounting, but it is source-dependent provenance evidence only, not universal compression, model-quality, runtime, memory, transfer, or promotion evidence.

The seed-rule source-change stress run is the first scored edit-cost and downstream-reuse attachment. It applies `4` deterministic source-change scenarios to the safe provenance envelopes and scores `20` downstream reuse queries. Object-only storage and Circle seed-rule-with-verifier both report exact regeneration `1.0` and downstream reuse hit rate `1.0`; Circle verifier residual count is `0`; template and freeform controls both report exact regeneration `0.0`. Circle average description length is `590.0` versus object-only `10344.75`, and Circle average edit cost is `463.75` versus object-only `6327.5`, an edit-cost ratio of `0.073291`. This is source-change provenance tooling evidence only, not universal compression, model-quality, runtime, memory, transfer, or promotion evidence.

The workflow/tool-card rebuild run is the first scored rebuild attachment. It reads `72` safe sources, including `64` benchmark-card sources, and rebuilds `188` safe envelope records across `13` record kinds. Object-only storage and Circle seed-rule-with-verifier both report exact rebuild `1.0` and downstream reuse hit rate `1.0`; Circle verifier residual count is `0`; inventory and registry-only baselines both report exact rebuild `0.0`. Circle automated rebuild work units are `9334` versus object-only `59730`, a ratio of `0.15627`. Human edit time is not measured in this fixture. This is workflow provenance tooling evidence only, not universal compression, model-quality, runtime, human-time, transfer, or promotion evidence.

The update-cycle effort run is instrumentation, not a scored improvement claim. It reads `13` safe sources and `289` aggregate event records. It finds `212` runtime fields with total runtime `92252.0` ms, average runtime `435.151` ms, and p95 runtime `864.0` ms. It now finds `3` `review_step_count` fields with total review steps `15.0`, plus `2` explicit `maintenance_mode` fields: one `object_only` row and one `circle_seed_rule_rebuild` row. It still finds `0` `human_edit_minutes` fields. `human_edit_time_measured = false`, `review_steps_measured = true`, `paired_maintenance_modes_present = true`, and `maintenance_savings_claim_ready = false`. This proves paired maintenance labels and review-step fields can flow through real update-cycle ledgers, but it is not yet a human-time or maintenance-savings comparison. The private Theseus-Hive side now has `scripts/hive_record_maintenance_effort.py` to write measured rows into `reports/hive_maintenance_effort_ledger.jsonl`; the current aggregate run has no measured rows from that recorder yet.

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

The companion real workload attachment layer now reads local Theseus-Hive artifacts and exports only aggregate counts, rates, ids, and path names under:

```text
circle_recurrence_budget_real_rows_v1
circle_candidate_fanout_real_manifest_v1
circle_memory_alias_real_trace_v1
circle_phase_feature_real_sequence_v1
circle_mixer_real_report_summary_v1
circle_seed_rule_real_provenance_summary_v1
```

That report is still intentionally `YELLOW`: all six families attach to real local private/synthetic/report-summary artifacts, `real_local_workload_aggregates_present = true`, `learned_model_quality_metrics_present = false`, `real_private_model_benchmark_results_present = false`, `external_inference_calls = 0`, `training_mutation = false`, `promotion_evidence = false`, and `private_data_exported = false`. It does not copy private row bodies, prompts, tests, solution code, candidate code, or learned-model scores into this public repository.

The scored layer is stronger but still limited benchmark evidence: it has named private workloads, baselines, metrics, scripts, reports, imported semantic score context, fresh equal-budget private semantic execution, fresh recurrence work-budget execution, context-packet memory retrieval scoring, phase-feature ablation scoring, route/ranker mixer ablation scoring, router-head mixer decision attachment, seed-rule exact-regeneration scoring, seed-rule source-change stress scoring, seed-rule workflow/tool-card rebuild scoring, and update-cycle effort instrumentation. It still does not show a Circle advantage over the relevant ordinary quality baselines, although the mixer fixtures record a parameter-count reduction at tied heldout trace accuracy and tied current router-head agreement, and the seed-rule fixtures record shorter verified regeneration/edit/rebuild recipes than object-only storage.

The next concrete private Theseus-Hive milestone is to use the full-frontier failure/runtime tables to design workloads and Circle policies that differ from ordinary rank-one or fixed-depth baselines when evidence supports them:

1. Consume `site/data/generated/theseus_hive_ai_contracts.json` only as private experiment configuration, not as public-calibration data.
2. Use `circle_candidate_fanout_equal_budget_semantic_v1` to design a Circle selection rule that differs from ordinary rank-one when evidence supports it.
3. Use `circle_recurrence_work_budget_semantic_v1` to design a recurrence workload where loop depth matters and ordinary rank-one no longer saturates the task.
4. Attach task-level retrieval targets, answer quality, and latency measurements to `circle_memory_context_packet_retrieval_v1`.
5. Attach `circle_phase_feature_sequence_ablation_v1` features to actual route/ranker/model decisions and compare heldout task quality, runtime, and failure cases against ordinary position features.
6. Extend the actual Octopus router-head `--circle-mixer` trainer path with real confusion-boundary traces, implementation profiling, and failure-case tables against the current no-mixer head; keep pure replacement and bounded-gain residual Circle modes diagnostic until they match or beat the no-mixer baseline on those harder cases.
7. Keep the autonomous-goal routing-memory producer schema, scratch-output smoke path, `head_router` fallback, compiled pre-training schema audit, boundary coverage report, hashed trace collection planner, and trace-lane integrity audit under test so future private traces improve the boundary coverage bins instead of being silently ignored by the router-head trainer.
8. Use `scripts/hive_record_maintenance_effort.py` to add `human_edit_minutes` only when actually measured on paired `maintenance_mode = object_only` and `maintenance_mode = circle_seed_rule_rebuild` update-cycle rows, then rerun `circle_seed_rule_update_cycle_effort_v1` to compare object-only maintenance with Circle seed-rule rebuilds.
9. Record every result as private experimental evidence until a named workload, baseline, metric, and reproducible script exist.

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
