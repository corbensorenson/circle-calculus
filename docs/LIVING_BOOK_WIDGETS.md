# Circle Calculus Living Book Widgets

Widgets are deterministic browser-native explanation tools. They are not proofs. Their formulas should be small, auditable, and parity-checked against Python reference behavior where practical.

## Shared Constraints

- No backend server for first-milestone S1 widgets.
- No remote resource fetches at runtime.
- Plain HTML/SVG/JavaScript preferred.
- Inputs must have labels.
- Widget panels must be named regions.
- Dynamic widget output must be an `aria-live` region.
- Do not communicate status by color alone.
- SVG diagrams should expose a title, description, and visible node labels.
- Widget captions must not call output a proof.

## Shared Files

Implemented shared JavaScript:

- `site/widgets/shared/circle_math_core.js`
- `site/widgets/shared/svg_helpers.js`
- `site/widgets/shared/widget_base.js`

## Showcase Widgets

### capability_portfolio_matrix

- Inputs: none; the widget reads `site/data/generated/capability_showcase.json`.
- Outputs: capability lane, area, portfolio roles, proof provenance kind, paper count, theorem count, executable count, Living Book page count, Living Book widget count, and the explicit claim boundary.
- Data source: `manifests/capability_showcase.yaml`, exported by `scripts/site/export_site_data.py`.
- Guardrail: the matrix is a manifest-backed evidence summary only. It does not turn imported theorem bridges, executable examples, widgets, or benchmarks into new mathematical proofs.
- Validation: `scripts/check_capability_showcase.py` requires the matrix mount and script import on the public showcase page; `scripts/site/check_site_widget_contracts.py` verifies the widget index, page mount, and JavaScript mount call.

### capability_audit_checklist

- Inputs: none; the widget reads `site/data/generated/capability_showcase.json`.
- Outputs: capability lane, generated claim-contract readiness, claim-contract gate count, proof provenance text, advertised claim, paper/theorem/dictionary/executable/source/Living Book evidence counts, linked paper/theorem/dictionary id lists, proved paper-carried theorem-id counts with Lean names and cited-paper carriers, linked pytest executable refs, linked source refs, paper-backed source-ref counts with Source Trail vs Lean-sidecar-import backing labels, generated reproduction commands, linked Living Book page refs, Living Book widget ids, and explicit claim boundary.
- Data source: `manifests/capability_showcase.yaml`, exported by `scripts/site/export_site_data.py`.
- Guardrail: the checklist verifies traceability only. It does not turn standard theorem bridges, Python examples, widgets, or paper prose into new proofs.
- Validation: `scripts/check_capability_showcase.py` requires every advertised theorem id to be proved and carried by a cited paper, and every advertised source ref to be backed by a cited paper Source Trail or cited Lean sidecar import closure; `scripts/site/export_site_data.py` emits matching `theorem_ref_contract` and `source_ref_contract` records; `scripts/site/check_capability_contracts.py` requires every generated claim contract to be ready, every reproduction recipe to match its executable refs, every emitted theorem-ref contract to match the advertised theorem ids, and every emitted source-ref contract to match the advertised source refs; `scripts/site/check_site_widget_contracts.py` verifies the widget index, page mount, and JavaScript mount call; `scripts/site/check_site_navigation_contract.py` keeps the verification-page audit route present.

## S1 Widgets

### finite_circle_rotator

- Inputs: `n`, selected node `i`.
- Outputs: SVG finite circle `C_n`, highlighted node, residue label `i mod n`.
- Dictionary ids: Circle and Node entries where available.
- Validation: node reduction agrees with `circle_math` finite-circle reference behavior.

### rotation_composition

- Inputs: `n`, start `x`, stride `a`, stride `b`.
- Outputs: `rot(n,b)(x)`, `rot(n,a)(rot(n,b)(x))`, and `rot(n,a+b)(x)`.
- Theorem ids: rotation composition theorem when available in manifests.
- Validation: JavaScript formula agrees with Python rotation behavior.

### coil_orbit_explorer

- Inputs: `n`, stride `k`, start.
- Outputs: orbit sequence, visited nodes, closed-loop visualization, `gcd(n,k)`, predicted period `n/gcd(n,k)`, actual orbit length.
- Theorem ids: orbit/period theorem when available.
- Validation: orbit sequence and period agree with Python reference behavior.

### period_gcd_visualizer

- Inputs: `n`, `k`.
- Outputs: `gcd(n,k)`, number of cycles, cycle length, decomposition into `gcd(n,k)` orbits.
- Theorem ids: period/gcd theorem when available.
- Validation: gcd orbit count and cycle decomposition agree with Python reference behavior.

### prime_full_coil_explorer

- Inputs: `n`.
- Outputs: which strides `1 <= k < n` are full coils; prime/composite behavior; theorem status for prime full-coil behavior when available.
- Guardrail: do not imply primality behavior is Lean-proved unless the manifest says so.
- Validation: full-coil stride list agrees with Python reference behavior.

### winding_lift_explorer

- Inputs: base `n`, step count `t`.
- Outputs: quotient `q = t div n`, residue `r = t mod n`, lifted coordinate `(q,r)`, visual distinction between residue and winding.
- Theorem ids: winding/lift theorem ids when available.
- Guardrail: mark as planned/draft if the corresponding Lean theorem is not proved.
- Validation: quotient/residue decomposition agrees with Python reference behavior.

## Generative Widgets

### seed_rule_diagram_generator

- Inputs: selected generated artifact.
- Outputs: generated finite-circle successor diagram, finite physics-loop plaquette diagram, coil-orbit record, orbit-decomposition record, or proof-glyph metadata; seed; rules; schedule; closure condition; generated-object summary; theorem-status badges; dictionary links.
- Theorem ids: finite circle, finite coil/orbit, finite physics-loop, proof-glyph, generator-regeneration, generated-list length, and generator-comparison theorem ids exposed by the selected record.
- Dictionary ids: finite circle/node/coil/orbit ids plus proof-glyph, finite gauge, and generative provenance ids.
- Python references: `circle_math.generative.finite_circle_diagram_generator`, `circle_math.generative.physics_loop_diagram_generator`, `circle_math.generative.coil_orbit_generator`, `circle_math.generative.orbit_decomposition_generator`, and `circle_math.generative.proof_glyph_generator`.
- Data source: `site/data/generated/generator_index.json`, exported from the Python seed-rule fixtures by `scripts/site/export_site_data.py`.
- Guardrail: the widget is generated explanation only. It displays linked proof statuses from the theorem manifest, but the generated diagram or metadata is not a proof and does not prove compression minimality, search optimality, or physics claims.
- Validation: generated records are exported from the Python fixtures; deterministic JavaScript display paths are parity-checked against the same seed-rule behavior.

### orbit_family_generator

- Inputs: finite-circle size `n` and stride.
- Outputs: representative-indexed orbit family, period `n/gcd(n,k)`, orbit count, gcd count, count-vs-gcd flag, exact coverage flag, disjointness flag, theorem-status badges, and dictionary links.
- Theorem ids: `GEN-T0003`, `GEN-T0006`, `GEN-T0007`, `GEN-T0008`, `GEN-T0009`, `GEN-T0010`, `GEN-T0011`, `GEN-T0012`, and `GEN-T0013`.
- Dictionary ids: `CC-0205`, `CC-0208`, `COMMON-0064`, and `COMMON-0066`.
- Python references: `circle_math.generative.orbit_decomposition_generator` and `circle_math.generative.regenerate`.
- Guardrail: the widget is finite orbit-family regeneration and coverage bookkeeping only. It does not prove minimality, global compression optimality, or theorem-discovery power.
- Validation: deterministic JavaScript-equivalent orbit decomposition, period, orbit count, coverage, and disjointness formulas are parity-checked against the Python orbit-decomposition generator.

### generator_comparison_search

- Inputs: finite-circle size `n`.
- Outputs: explicit-vs-generator description lengths, exact regeneration flag, generator-shorter flag, a broken non-exact candidate, bounded finite search count, exact candidate count, best exact candidate, best shorter exact candidate, no-best/zero-count checks, theorem-status badges, and dictionary links.
- Theorem ids: `GEN-T0001`, `GEN-T0005`, `GEN-T0017`, `GEN-T0018`, `GEN-T0019`, `GEN-T0020`, `GEN-T0022`, `GEN-T0023`, `GEN-T0024`, `GEN-T0025`, `GEN-T0026`, `GEN-T0027`, `GEN-T0028`, `GEN-T0029`, `GEN-T0030`, `GEN-T0031`, `GEN-T0032`, `GEN-T0033`, `GEN-T0034`, `GEN-T0035`, `GEN-T0036`, `GEN-T0037`, `GEN-T0038`, and `GEN-T0039`.
- Dictionary ids: `COMMON-0064`, `COMMON-0065`, and `COMMON-0066`.
- Python references: `circle_math.generative.compare_generator_to_explicit`, `circle_math.generative.bounded_generator_search`, and `circle_math.generative.finite_circle_generator`.
- Guardrail: the widget is bounded finite description-length bookkeeping only. It does not prove global optimality, Kolmogorov complexity, universal compression, or that smaller descriptions are always better.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python generator-comparison and bounded-search helpers.

### proof_glyph_certificate

- Inputs: none; the widget reads the generated `proof_glyph` record from `site/data/generated/generator_index.json`.
- Outputs: generated glyph id, theorem id, Lean declaration name, theorem manifest status, Lean source path, field-resolution table, theorem-status badges, and dictionary links.
- Theorem ids: `P2G-T0001`, `P2G-T0002`, `P2G-T0003`, `P2G-T0004`, and the generated theorem id `CC-T0005`.
- Dictionary ids: `COMMON-0033`, `COMMON-0064`, and `COMMON-0066`.
- Python references: `circle_math.generative.proof_glyph_generator` and `circle_math.generative.regenerate`.
- Guardrail: the widget is proof navigation and certificate-field checking only. It does not prove the target theorem; theorem status still comes from the manifest and local Lean build.
- Validation: widget contract checks ensure the page mount, script import, theorem ids, and dictionary ids resolve; generator parity is covered by the existing proof-glyph regeneration case in `check_widget_python_parity.py`.

## AI Widgets

### phase_channel_baseline

- Inputs: period, training length, and test length.
- Outputs: positive phase set, learned phase lookup, periodic phase-lookup accuracy, periodic scalar-threshold accuracy, constant-majority accuracy, nonperiodic phase-lookup accuracy, nonperiodic scalar-threshold accuracy, theorem-status badges, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIA-T0002`, `AIA-T0003`, `AIA-T0004`, and `AIA-T0005`.
- Dictionary ids: `COMMON-0026` and `COMMON-0027`.
- Python references: `circle_math.applications.circle_ai.phase_channel`, `circle_math.applications.circle_ai.run_phase_channel_benchmark`, and `circle_math.applications.circle_ai.run_learned_phase_baseline_benchmark`.
- Guardrail: the widget is a deterministic synthetic phase-feature control fixture only. It does not prove neural-network quality, model speed, real-task usefulness, or that cyclic features help nonperiodic tasks.
- Validation: deterministic JavaScript-equivalent phase lookup, constant baseline, scalar-threshold baseline, and nonperiodic control formulas are parity-checked against the Python phase-channel benchmark helpers.

### learned_feature_baseline

- Inputs: period, wrong period, training length, and test length.
- Outputs: positive phase set, correct cyclic lookup, wrong-period lookup, periodic cyclic-feature accuracy, periodic dense-scalar accuracy, periodic learned-position accuracy, periodic wrong-period accuracy, nonperiodic cyclic accuracy, nonperiodic dense-scalar accuracy, nonperiodic learned-position accuracy, theorem-status badges, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIA-T0002`, `AIA-T0003`, `AIA-T0004`, and `AIA-T0005` as finite phase/indexing boundaries.
- Dictionary ids: `COMMON-0026` and `COMMON-0027`.
- Python references: `circle_math.applications.circle_ai.fit_phase_lookup`, `circle_math.applications.circle_ai.predict_phase_lookup`, and `circle_math.applications.circle_ai.run_learned_feature_baseline_benchmark`.
- Guardrail: the widget is a deterministic synthetic learned-feature control fixture only. It does not prove representation learning, neural-network quality, speed, parameter efficiency, or usefulness on real workloads.
- Validation: deterministic JavaScript-equivalent phase lookup, wrong-period phase lookup, scalar-threshold baseline, learned-position baseline, and nonperiodic control formulas are parity-checked against the Python learned-feature benchmark helpers.

### harmonic_feature_baseline

- Inputs: period, wrong period, training length, and test length.
- Outputs: positive phase set, learned phase lookup, observed harmonic feature count, sample sine/cosine feature, cyclic phase-lookup accuracy, correct harmonic feature accuracy, wrong-frequency harmonic accuracy, scalar-threshold accuracy, learned absolute-position accuracy, nonperiodic harmonic accuracy, nonperiodic scalar-threshold accuracy, theorem-status badges, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIA-T0002`, `AIA-T0004`, and `AIA-T0005` as finite phase/indexing boundaries.
- Dictionary ids: `COMMON-0026`, `COMMON-0027`, and `COMMON-0046`.
- Python references: `circle_math.applications.circle_ai.harmonic_feature`, `circle_math.applications.circle_ai.fit_harmonic_feature_lookup`, `circle_math.applications.circle_ai.predict_harmonic_feature_lookup`, and `circle_math.applications.circle_ai.run_harmonic_feature_baseline_benchmark`.
- Guardrail: the widget is a deterministic synthetic Fourier-style feature-control fixture only. It does not prove RoPE quality, language-model quality, speed, parameter efficiency, or usefulness on real workloads.
- Validation: deterministic JavaScript-equivalent phase lookup, harmonic feature lookup, wrong-period harmonic lookup, scalar-threshold baseline, learned-position baseline, and nonperiodic control formulas are parity-checked against the Python harmonic-feature benchmark helpers.

### backend_parity_fixture

- Inputs: none; this is the fixed deterministic `AIA-B0003` scoring harness.
- Outputs: fixture count, deterministic browser CPU scores for the backend parity cases, local Python/optional-MLX command boundary, theorem-status badges, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIM-T0001`, `AIM-T0015`, and `AIRA-T0001` as finite indexing/schedule boundaries.
- Dictionary ids: `COMMON-0026`, `COMMON-0028`, `COMMON-0030`, `COMMON-0046`, `COMMON-0047`, `COMMON-0051`, and `COMMON-0052`.
- Python references: `circle_math.applications.circle_ai.ai_backend_parity_cases` and `circle_math.applications.circle_ai.run_ai_backend_parity_check`.
- Guardrail: the widget is not an MLX runtime, acceleration result, speed benchmark, model-quality claim, or proof. The local Python fixture reports actual MLX availability and MLX-vs-CPU deltas when MLX is installed.
- Validation: deterministic JavaScript-equivalent fixture cases and CPU scores are parity-checked against the Python backend-parity case generator and benchmark result.

### loop_recurrence_budget

- Inputs: loop period, sample/token index, maximum loops, overthinking tolerance.
- Outputs: loop phase, required loop count, token recurrence budget, capped training-free loop budget, exit availability, overthinking boundary, one-period-shift periodicity checks, and whole-loop-pass closure checks.
- Theorem ids: `AIM-T0018`, `AIM-T0019`, `AIM-T0020`, `AIM-T0021`, `AIM-T0022`, `AIM-T0023`, `AIM-T0025`, `AIM-T0026`, `AIM-T0027`, `AIM-T0028`, `AIM-T0029`, and `AIM-T0030`.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0054`, `COMMON-0059`, and `COMMON-0067`.
- Python references: `circle_math.applications.circle_ai.loop_required_steps`, `circle_math.applications.circle_ai.token_recurrence_budget`, and `circle_math.applications.circle_ai.training_free_loop_budget`.
- Guardrail: the widget is finite schedule bookkeeping only. It does not prove model quality, speed, reasoning improvement, memory improvement, or context-length improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python AI recurrence helpers.

### loop_exit_certificate

- Inputs: loop period, primary sample index, primary maximum loops, fixed-budget control sample index, fixed-budget control maximum loops, and overthinking tolerance.
- Outputs: primary and control score traces, required loop depth, first exit step, exit availability, budget status, guardrail status, one-period and multi-pass exit-availability checks, theorem-status badges, and dictionary links.
- Theorem ids: `AIM-T0012`, `AIM-T0013`, `AIM-T0014`, `AIM-T0015`, `AIM-T0016`, `AIM-T0017`, `AIM-T0024`, `AIM-T0029`, `AIM-T0030`, `AIM-T0031`, `AIM-T0032`, `AIM-T0033`, and `AIM-T0034`.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0054`, `COMMON-0059`, and `COMMON-0067`.
- Python references: `circle_math.applications.circle_ai.loop_required_steps`, `circle_math.applications.circle_ai.loop_score_trace`, `circle_math.applications.circle_ai.loop_exit_step`, and `circle_math.applications.circle_ai.loop_exit_certificate`.
- Guardrail: the widget is deterministic finite loop-schedule certificate bookkeeping only. It does not prove trained early-exit quality, recursive reasoning, speed, memory improvement, context-length improvement, or overthinking behavior in real transformers.
- Validation: deterministic JavaScript-equivalent score traces, exit steps, availability flags, budget flags, guardrail flags, and one-period-shift checks are parity-checked against the Python loop-exit certificate helper.

### token_level_recurrence

- Inputs: loop period, token count, maximum budget, fixed global budget, wrong-budget shift, over-loop budget, and overthinking tolerance.
- Outputs: per-token recurrence-budget strip, selected middle-block record, coarse/fine resolution labels, active-token counts by loop step, first-step/beyond-period active-step boundary, fixed-budget control, wrong-budget control, over-loop control, nonperiodic phase-lookup control, and scalar-threshold control.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, `AIM-T0018`, `AIM-T0022`, `AIM-T0026`, `AIM-T0027`, `AIM-T0035`, `AIM-T0036`, `AIM-T0037`, and `AIM-T0038` as finite loop-budget and active-step primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0068`, and `COMMON-0069`.
- Python references: `circle_math.applications.circle_ai.token_recurrence_budgets`, `circle_math.applications.circle_ai.active_token_counts_by_budget`, `circle_math.applications.circle_ai.recurrence_resolution_levels`, and `circle_math.applications.circle_ai.run_token_level_recurrence_benchmark`.
- Guardrail: the widget is deterministic token-level schedule bookkeeping only. It does not prove learned-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python token-level recurrence benchmark fixture.

### training_free_loop_wrapper

- Inputs: loop period, sample count, maximum loops, fixed loop budget, wrong loop period, over-loop budget, and overthinking tolerance.
- Outputs: required-budget strip, phase-budget strip, phase-budget sample, wrong-period budget sample, active-sample counts, budget histogram, average phase budget, single-pass accuracy, fixed-budget accuracy, phase-budget accuracy, wrong-period accuracy, over-loop accuracy, nonperiodic phase-budget accuracy, and nonperiodic scalar-threshold accuracy.
- Theorem ids: `AIM-T0010`, `AIM-T0011`, `AIM-T0019`, `AIM-T0020`, `AIM-T0023`, `AIM-T0025`, and `AIM-T0028` as finite training-free loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0054`, and `COMMON-0067`.
- Python references: `circle_math.applications.circle_ai.training_free_loop_budget`, `circle_math.applications.circle_ai.training_free_loop_budgets`, and `circle_math.applications.circle_ai.run_training_free_loop_wrapper_benchmark`.
- Guardrail: the widget is deterministic training-free loop-wrapper bookkeeping only. It does not prove learned recurrence, recursive reasoning, language-model quality, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python training-free loop-wrapper benchmark fixture.

### learned_token_recurrence

- Inputs: loop period, wrong/control period, train-token count, held-out test-token count, maximum budget, fixed global budget, wrong-budget shift, over-loop budget, and overthinking tolerance.
- Outputs: fitted phase-to-budget lookup table, wrong-period lookup table, required held-out budget sample, learned held-out budget sample, shifted-budget control sample, active-token counts by loop step, learned-router accuracy, fixed-budget accuracy, wrong-period accuracy, wrong-shift accuracy, over-loop accuracy, nonperiodic phase-lookup accuracy, and nonperiodic scalar-threshold accuracy.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, `AIM-T0018`, and `AIM-T0022` as finite loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0068`, and `COMMON-0069`.
- Python references: `circle_math.applications.circle_ai.fit_loop_budget_lookup`, `circle_math.applications.circle_ai.predict_loop_budget_lookup`, and `circle_math.applications.circle_ai.run_learned_token_level_recurrence_benchmark`.
- Guardrail: the widget is learned lookup-table bookkeeping for a constructed finite fixture only. It does not prove neural-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python learned token-level recurrence benchmark fixture.

### learned_middle_block_recurrence

- Inputs: block count, selected block range, wrong block range, loop period, wrong block period, wrong budget period, train-sample count, held-out test-sample count, maximum budget, fixed budget, over-loop budget, and overthinking tolerance.
- Outputs: learned phase-to-block lookup, learned phase-to-budget lookup, wrong-period lookup tables, held-out required/learned/wrong block samples, held-out required/learned/wrong budget samples, active-sample counts, learned-router accuracy, selected-band accuracy, full-block accuracy, fixed-budget accuracy, wrong block-period accuracy, wrong budget-period accuracy, wrong-block accuracy, over-loop accuracy, and block-pass accounting.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, `AIM-T0018`, `AIM-T0039`, `AIM-T0040`, `AIM-T0041`, `AIM-T0042`, and `AIM-T0043` as finite loop-budget and selected middle-block route primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0068`, and `COMMON-0070`.
- Python references: `circle_math.applications.circle_ai.fit_loop_block_lookup`, `circle_math.applications.circle_ai.predict_loop_block_lookup`, `circle_math.applications.circle_ai.fit_loop_budget_lookup`, `circle_math.applications.circle_ai.predict_loop_budget_lookup`, and `circle_math.applications.circle_ai.run_learned_middle_block_recurrence_benchmark`.
- Guardrail: the widget is learned middle-block schedule bookkeeping for a constructed finite fixture only. It does not prove neural block-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python learned middle-block recurrence benchmark fixture.

### learned_multi_resolution_recurrence

- Inputs: loop period, wrong budget period, wrong resolution period, train-sample count, held-out test-sample count, maximum budget, fixed budget, over-loop budget, and overthinking tolerance.
- Outputs: coarse/fine resolution levels, learned phase-to-budget lookup, learned phase-to-resolution lookup, wrong-period lookup tables, held-out required/learned/wrong budget samples, held-out required/learned/wrong resolution samples, active-sample counts, learned-router accuracy, single-resolution coarse/fine accuracies, fixed-budget accuracy, wrong budget-period accuracy, wrong resolution-period accuracy, over-loop accuracy, and average active samples.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, and `AIM-T0018` as finite loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0069`, and `COMMON-0070`.
- Python references: `circle_math.applications.circle_ai.fit_loop_budget_lookup`, `circle_math.applications.circle_ai.predict_loop_budget_lookup`, `circle_math.applications.circle_ai.fit_recurrence_resolution_lookup`, `circle_math.applications.circle_ai.predict_recurrence_resolution_lookup`, and `circle_math.applications.circle_ai.run_learned_multi_resolution_recurrence_benchmark`.
- Guardrail: the widget is learned multi-resolution schedule bookkeeping for a constructed finite fixture only. It does not prove neural compressed/full-resolution routing quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python learned multi-resolution recurrence benchmark fixture.

### learned_recurrence_schedule

- Inputs: loop period, wrong/control period, train-sample count, held-out test-sample count, fixed loop budget, over-loop budget, and overthinking tolerance.
- Outputs: learned phase-to-budget lookup, wrong-period lookup, required held-out budget sample, learned held-out budget sample, wrong-period budget sample, learned-router accuracy, fixed-budget accuracy, wrong-period accuracy, and over-loop accuracy.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, and `AIM-T0009` as finite loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, and `COMMON-0070`.
- Python references: `circle_math.applications.circle_ai.fit_loop_budget_lookup`, `circle_math.applications.circle_ai.predict_loop_budget_lookup`, and `circle_math.applications.circle_ai.run_learned_recurrence_schedule_benchmark`.
- Guardrail: the widget is learned recurrence-schedule bookkeeping for a constructed finite fixture only. It does not prove neural-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python learned recurrence-schedule benchmark fixture.

### cyclic_memory_slots

- Inputs: memory-bank size, token index, full-bank pass count, and token-window length.
- Outputs: selected slot, one-bank closure, multi-bank closure, idempotent slot normalization, slot zero, per-slot load counts, collision count, theorem-status badges, and dictionary links.
- Theorem ids: `AIM-T0001`, `AIM-T0002`, `AIM-T0003`, `AIM-T0004`, and `AIM-T0005`.
- Dictionary ids: `COMMON-0028` and `COMMON-0029`.
- Python references: `circle_math.applications.circle_ai.memory_slot`, `circle_math.applications.circle_ai.memory_slot_loads`, and `circle_math.applications.circle_ai.memory_slot_collision_count`.
- Guardrail: the widget is finite indexing and alias bookkeeping only. It does not prove retrieval quality, memory scaling, model-quality improvement, speedup, or training effectiveness.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python cyclic-memory helpers.

### coil_retrieval_reachability

- Inputs: sequence length, query index, target lag, selected stride, path length, local-window width, wrong stride, and near-control lag.
- Outputs: long-lag target index, selected coil-path candidates, local-window candidates, wrong-stride candidates, full-attention oracle row, near-lag local and coil controls, candidate counts, hit/miss status, finite primitive theorem links, and dictionary links.
- Theorem ids: `CC-T0002` and `CC-T0005` as finite rotation/orbit primitives only.
- Dictionary ids: `COMMON-0047`, `COMMON-0028`, and `COMMON-0029`.
- Python references: `circle_math.applications.circle_ai.coil_attention_path`, `circle_math.applications.circle_ai.local_window_indices`, `circle_math.applications.circle_ai.retrieval_target_index`, and `circle_math.applications.circle_ai.retrieval_hit_rate`.
- Guardrail: the widget is finite candidate-set reachability only. It does not prove retrieval quality, context length, runtime, memory scaling, attention replacement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python coil-retrieval helpers.

### content_gated_retrieval

- Inputs: sequence length, query count, inspected query, long lag, near lag, selected stride, path length, and local-window width.
- Outputs: content-gated, static-coil, static-local, wrong-gate, union-candidate, and full-attention oracle rows; hit rates; average candidate counts; inspected-query route; inspected target; selected candidates; finite primitive theorem links; and dictionary links.
- Theorem ids: `CC-T0002` and `CC-T0005` as finite rotation/orbit primitives only.
- Dictionary ids: `COMMON-0057`, `COMMON-0047`, and `COMMON-0028`.
- Python references: `circle_math.applications.circle_ai.mixed_retrieval_target_lags`, `circle_math.applications.circle_ai.retrieval_hit_rate_by_lag`, `circle_math.applications.circle_ai.average_candidate_count`, and `circle_math.applications.circle_ai.run_content_gated_retrieval_benchmark`.
- Guardrail: the widget is deterministic route and candidate-budget bookkeeping only. It does not prove learned-gate quality, retrieval quality, context length, runtime, memory scaling, attention replacement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python content-gated retrieval helpers.

### learned_content_gate_retrieval

- Inputs: sequence length, train length, test length, route period, wrong route period, long lag, near lag, selected stride, path length, and local-window width.
- Outputs: learned phase-to-route lookup, wrong-period lookup, required/learned route samples, route accuracy, learned/static/wrong/flipped/union/full hit rates, average candidate counts, finite primitive theorem links, and dictionary links.
- Theorem ids: `CC-T0002` and `CC-T0005` as finite rotation/orbit primitives only.
- Dictionary ids: `COMMON-0057`, `COMMON-0047`, and `COMMON-0028`.
- Python references: `circle_math.applications.circle_ai.content_route_label`, `circle_math.applications.circle_ai.fit_content_route_lookup`, `circle_math.applications.circle_ai.predict_content_route_lookup`, and `circle_math.applications.circle_ai.run_learned_content_gate_retrieval_benchmark`.
- Guardrail: the widget is a tiny deterministic route-table fixture with controls. It does not prove learned model quality, retrieval quality, context length, runtime, memory scaling, attention replacement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent phase-to-route lookup, route prediction, hit-rate, and candidate-budget formulas are parity-checked against the Python learned content-gate benchmark.

### multicoil_phase_explorer

- Inputs: two required phase periods, one optional third phase period, and a position.
- Outputs: combined phase tuple, joint repeat horizon, shifted phase tuple after one joint cycle, constructed synthetic fixture label, per-period closure rows, finite phase-channel theorem links, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIA-T0002`, `AIA-T0004`, and `AIA-T0005` as finite phase-channel primitives only.
- Dictionary ids: `COMMON-0046`, `COMMON-0026`, and `COMMON-0027`.
- Python references: `circle_math.applications.circle_ai.multicoil_phase`, `circle_math.applications.circle_ai.multicoil_cycle_length`, and `circle_math.applications.circle_ai.multicoil_phase_label`.
- Guardrail: the widget is positional phase bookkeeping for a synthetic fixture only. It does not prove RoPE improvement, language-model quality, attention replacement, context-length improvement, or runtime improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python MultiCoil phase helpers.

### rope_relative_phase

- Inputs: correct period, wrong/control period, query position, and key position.
- Outputs: correct-period relative lag, sine/cosine relative feature, wrong-period feature, constructed synthetic label, query-shift closure check, key-shift closure check, finite phase-channel theorem links, and dictionary links.
- Theorem ids: `AIA-T0001`, `AIA-T0002`, `AIA-T0004`, and `AIA-T0005` as finite phase-channel primitives only.
- Dictionary ids: `COMMON-0051`, `COMMON-0050`, and `COMMON-0026`.
- Python references: `circle_math.applications.circle_ai.rope_relative_feature` and `circle_math.applications.circle_ai.run_rope_relative_phase_benchmark`.
- Guardrail: the widget is a relative phase fixture only. It does not prove standard RoPE quality, attention quality, context-length improvement, perplexity improvement, or runtime improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python RoPE relative phase helper.

### adapter_parameter_budget

- Inputs: channel count, block size, LoRA-style rank, and parameters per channel/block.
- Outputs: dense adapter parameters, LoRA-style parameters, block-cyclic shared-table parameters, ratios to dense, channel collision count, maximum block load, per-block load rows, adapter-block theorem links, and dictionary links.
- Theorem ids: `AIRA-T0001`, `AIRA-T0002`, `AIRA-T0004`, and `AIRA-T0005` as finite adapter-block indexing primitives only.
- Dictionary ids: `COMMON-0056`, `COMMON-0030`, and `COMMON-0031`.
- Python references: `circle_math.applications.circle_ai.dense_adapter_parameter_count`, `circle_math.applications.circle_ai.lora_adapter_parameter_count`, `circle_math.applications.circle_ai.block_cyclic_adapter_parameter_count`, and `circle_math.applications.circle_ai.run_adapter_parameter_budget_benchmark`.
- Guardrail: the widget counts parameters and alias/load pressure only. It does not prove fine-tuning quality, runtime, memory, training stability, hardware efficiency, or CoilRA usefulness.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python adapter parameter-budget helpers.

### circulant_mixer_validation

- Inputs: period and wrong-shift control.
- Outputs: deterministic input vector, deterministic sparse kernel, circular-convolution output, dense circulant-matrix output, wrong-shift output, max absolute dense delta, wrong-shift mismatch count, dense parameter count, circulant parameter count, parameter ratio, and dictionary links.
- Theorem ids: none dedicated yet. This is an executable validation fixture for `AIRA-B0005`; finite proof work remains in adjacent indexing theorem cards.
- Dictionary ids: `COMMON-0058`, `COMMON-0056`, and `COMMON-0046`.
- Python references: `circle_math.applications.circle_ai.circulant_mixer_output`, `circle_math.applications.circle_ai.dense_circulant_matrix`, and `circle_math.applications.circle_ai.run_circulant_mixer_benchmark`.
- Guardrail: the widget validates circular-convolution bookkeeping only. It does not prove neural-layer quality, runtime, memory, training stability, hardware efficiency, or CoilLinear usefulness.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python circulant mixer helpers.

## Physics Widgets

### finite_path_algebra

- Inputs: finite phase modulus; phases on `a->b`, `b->c`, and `c->d`; and vertex gauge values at `a`, `b`, `c`, and `d`.
- Outputs: left/right/concatenated path records, concatenated holonomy, additive concatenation check, reversed path, reverse holonomy, closed path formed by appending the reverse, closed holonomy, gauge-transformed open path, endpoint-shift prediction, theorem-status badges, and dictionary links.
- Theorem ids: `PHYS-T0001`, `PHYS-T0002`, `PHYS-T0003`, `PHYS-T0006`, `PHYS-T0007`, `PHYS-T0039`, `PHYS-T0050`, and `PHYS-T0051`.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, and `COMMON-0063`.
- Python references: `circle_math.physics.GaugePath`, `circle_math.physics.GaugeEdge`, `circle_math.physics.path_holonomy`, `circle_math.physics.concat_paths`, `circle_math.physics.reverse_path`, `circle_math.physics.gauge_transform_path`, and `circle_math.physics.transformed_holonomy_endpoint_prediction`.
- Guardrail: the widget is finite modular path algebra only. It does not prove continuum electromagnetism, QFT, Yang-Mills theory, Berry phase, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python finite path helpers.

### finite_gauge_loop_holonomy

- Inputs: finite phase modulus, four square-plaquette edge phases, and four vertex gauge values.
- Outputs: original normalized edge phases, transformed edge phases, original holonomy, transformed holonomy, closed-path endpoint-shift cancellation, theorem-status badges, and dictionary links.
- Theorem ids: `PHYS-T0004`, `PHYS-T0005`, `PHYS-T0012`, `PHYS-T0045`, and `PHYS-T0047`.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, `COMMON-0062`, and `COMMON-0063`.
- Python references: `circle_math.physics.square_plaquette_path`, `circle_math.physics.gauge_transform_path`, and `circle_math.physics.path_holonomy`.
- Guardrail: the widget is finite `Z_n` bookkeeping only. It is not a proof artifact, continuum gauge theory, QFT, Yang-Mills theory, Berry phase, electromagnetism, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python finite lattice-gauge fixture.

### wilson_loop_certificate

- Inputs: finite phase modulus, three triangular-loop edge phases, and one editable sampled vertex gauge.
- Outputs: identity-loop gauge samples, normalized triangular loop, original holonomy, transformed edge rows for three sampled gauges, transformed holonomies, sampled invariance flags, theorem-status badges, and dictionary links.
- Theorem ids: `PHYS-T0004`, `PHYS-T0005`, `PHYS-T0046`, `PHYS-T0047`, `PHYS-T0049`, `PHYS-T0052`, `PHYS-T0053`, `PHYS-T0054`, and `PHYS-T0055`, linking the sampled Python certificate to the Lean-proved closed-loop identity, two-path cycle invariance, and two-path basepoint-swap boundaries.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, `COMMON-0062`, and `COMMON-0063`.
- Python references: `circle_math.physics.GaugePath`, `circle_math.physics.GaugeEdge`, `circle_math.physics.gauge_transform_path`, `circle_math.physics.path_holonomy`, and `circle_math.physics.wilson_loop_certificate`.
- Guardrail: the widget is a sampled finite Wilson-loop certificate only. It does not prove continuum gauge theory, electromagnetism, QFT, Berry phase, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python Wilson-loop certificate helper.

### hopf_hidden_phase

- Inputs: finite phase period, phase step, and integer real/imaginary coordinates for a nonzero complex pair.
- Outputs: normalized complex-pair coordinates, shared unit phase, phase-rotated pair, visible Hopf base point before/after phase rotation, pair/base norm checks, base-point equality flag, theorem-status badges, and dictionary links.
- Theorem ids: `S3H-T0001`, `S3H-T0002`, `S3H-T0003`, `S3H-T0004`, `S3H-T0005`, and `S3H-T0006`.
- Dictionary ids: `S3H-0001`, `S3H-0002`, and `S3H-W0001`.
- Python references: `circle_math.dimensions.hopf.normalize_pair`, `circle_math.dimensions.hopf.phase_rotate`, `circle_math.dimensions.hopf.hopf_map`, and `circle_math.dimensions.hopf.hopf_phase_record`.
- Guardrail: the widget is a bounded coordinate Hopf phase fixture. It does not prove Berry phase, a complete fiber-bundle formalization, quantum mechanics, or a physics prediction.
- Validation: deterministic JavaScript-equivalent complex-pair normalization, phase rotation, and Hopf-map formulas are parity-checked against the Python S3 Hopf helpers.

### spin_sign_ambiguity

- Inputs: finite phase period, phase step, and three integer coordinates for a pure-vector quaternion input.
- Outputs: sampled unit `i`-phase representative `q`, the opposite representative `-q`, the input vector, both conjugation-action outputs, distinct-representative flag, sign-related flag, action-equivalence flag, pure-vector preservation flag, theorem-status badges, and dictionary links.
- Theorem ids: `S3S-T0001`, `S3S-T0002`, `S3S-T0003`, `S3S-T0004`, and `S3S-T0005`.
- Dictionary ids: `S3S-0001`, `S3S-0002`, `S3S-0003`, `S3Q-0001`, and `S3Q-0002`.
- Python references: `circle_math.dimensions.quaternion.unit_i_phase`, `circle_math.dimensions.quaternion.conjugation_action`, and `circle_math.dimensions.quaternion.orientation_debug_record`.
- Guardrail: the widget is a bounded quaternion conjugation-action fixture. It does not prove a complete `SO(3)` quotient, robotics verification, spinor theory, or a physical rotation model.
- Validation: deterministic JavaScript-equivalent quaternion multiplication, conjugation, and sign-comparison formulas are parity-checked against the Python S3 spin helpers.

### periodic_winding_dynamics

- Inputs: phase modulus, stride, step count, defect sectors, defect turns, and signed orientation.
- Outputs: stroboscopic phase, total motion, lifted winding/residue, closure period, closure flag, phase sequence, finite marked-defect phase path, net signed steps, defect winding, closed-loop flag, theorem-status badges, and dictionary links.
- Theorem ids: `CC-T0005`, `CC-T0009`, and `CC-T0011` as finite period and winding primitives only.
- Dictionary ids: `COMMON-0060`, `COMMON-0063`, `COMMON-0036`, `COMMON-0038`, and `CC-0301`.
- Python references: `circle_math.physics.finite_periodic_dynamics` and `circle_math.physics.finite_defect_winding`.
- Guardrail: the widget is finite phase, winding, residue, and closure bookkeeping only. It does not prove Floquet theory, action-angle mechanics, continuum vortices, Kosterlitz-Thouless physics, or physical material behavior.
- Validation: deterministic JavaScript-equivalent closure-period, lifted winding/residue, phase-sequence, signed defect-path, net-step, winding, and closure formulas are parity-checked against the Python physics helpers.

## Future Placeholders

- `site/widgets/S2/sphere_grid_placeholder.js`

These should be visibly marked placeholder/exploratory until implemented and linked to checked theorem status.

Mounted placeholder widgets are included in `site/data/generated/widget_index.json` so every active widget slot is discoverable from generated site data, even when it is scaffold-only.

## Validation Strategy

Checkers:

- `scripts/site/check_site_widget_contracts.py` verifies that every `data-widget` page mount exists in `widget_index.json`, imports the matching widget script, and points to a JavaScript file that calls `mountWidgets("<widget_id>", ...)`.
- `scripts/site/check_site_accessibility_contract.py` verifies shared widget accessibility contracts: named widget regions, labelled number inputs, live output regions, SVG title/description metadata, visible focus styling, and scaffold-only placeholder guardrails.
- `scripts/site/check_capability_contracts.py` verifies generated proof-backed showcase claim contracts and fails if any advertised capability is missing its standard anchor, Circle expression, Circle-native value, proof provenance, proved paper-carried theorem-ref contract, paper-backed source-ref contract, executable support, generated reproduction recipe, Living Book presentation, or not-claimed boundary.
- `scripts/site/check_widget_python_parity.py` validates deterministic S1 formulas against Python reference behavior.
- `scripts/site/check_widget_runtime_links.py` imports the shared widget runtime under Node and verifies that real repository paths become GitHub source links while symbolic paper-section references remain plain text.

Minimum parity cases:

- node reduction;
- rotation;
- rotation composition;
- orbit sequence;
- period `n/gcd(n,k)`;
- gcd orbit count;
- winding/residue decomposition.
- finite-circle generated diagram nodes and successor edges;
- finite physics-loop generated diagram normalized phases, closed-loop flag, and holonomy.
- generated coil orbit sequences, orbit decompositions, and proof-glyph metadata fields.
- generator comparison exactness, description lengths, shorter-than-explicit flag, and bounded-search candidate counts.
- AI recurrence phase, required loop count, token recurrence budget, capped training-free budget, exit availability, overthinking boundary, and one-period-shift periodicity.
- cyclic memory slot reduction, one-bank closure, multi-bank closure, idempotent normalization, slot loads, and collision count.
- coil-retrieval target index, selected coil path, local window, wrong-stride path, full-attention oracle hit, and near-lag local/coil controls.
- content-gated retrieval mixed lags, gated/static/wrong/union/full hit rates, and average candidate counts.
- MultiCoil phase tuple, joint cycle length, phase closure after one joint cycle, and constructed synthetic label.
- RoPE-style relative phase lag, sine/cosine feature, query-period closure, and key-period closure.
- adapter parameter-budget dense, LoRA-style, and block-cyclic counts; ratios; block loads; and collision count.
- circulant mixer circular-convolution output, dense circulant-matrix output, wrong-shift output, max dense delta, and parameter counts.
- token-level recurrence budgets, active-token counts, resolution labels, fixed/wrong/over-loop controls, and nonperiodic scalar-control comparison.
- finite path concatenation holonomy, reverse-path holonomy, path-plus-reverse closure, and open-path gauge endpoint prediction.
- finite gauge-loop normalized phases, gauge-transformed phases, original/transformed holonomy, and closed endpoint cancellation.
- Wilson-loop certificate original holonomy, transformed sampled-gauge holonomies, sampled invariance ids, and theorem id payload.
