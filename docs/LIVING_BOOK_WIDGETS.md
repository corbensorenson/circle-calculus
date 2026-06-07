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
- Theorem ids: finite circle, finite coil/orbit, finite physics-loop, proof-glyph, and generator-comparison theorem ids exposed by the selected record.
- Dictionary ids: finite circle/node/coil/orbit ids plus proof-glyph, finite gauge, and generative provenance ids.
- Python references: `circle_math.generative.finite_circle_diagram_generator`, `circle_math.generative.physics_loop_diagram_generator`, `circle_math.generative.coil_orbit_generator`, `circle_math.generative.orbit_decomposition_generator`, and `circle_math.generative.proof_glyph_generator`.
- Data source: `site/data/generated/generator_index.json`, exported from the Python seed-rule fixtures by `scripts/site/export_site_data.py`.
- Guardrail: the widget is generated explanation only. It displays linked proof statuses from the theorem manifest, but the generated diagram or metadata is not a proof and does not prove compression minimality, search optimality, or physics claims.
- Validation: generated records are exported from the Python fixtures; deterministic JavaScript display paths are parity-checked against the same seed-rule behavior.

### generator_comparison_search

- Inputs: finite-circle size `n`.
- Outputs: explicit-vs-generator description lengths, exact regeneration flag, generator-shorter flag, a broken non-exact candidate, bounded finite search count, exact candidate count, best exact candidate, best shorter exact candidate, theorem-status badges, and dictionary links.
- Theorem ids: `GEN-T0005`, `GEN-T0017`, `GEN-T0018`, and `GEN-T0019`.
- Dictionary ids: `COMMON-0064`, `COMMON-0065`, and `COMMON-0066`.
- Python references: `circle_math.generative.compare_generator_to_explicit`, `circle_math.generative.bounded_generator_search`, and `circle_math.generative.finite_circle_generator`.
- Guardrail: the widget is bounded finite description-length bookkeeping only. It does not prove global optimality, Kolmogorov complexity, universal compression, or that smaller descriptions are always better.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python generator-comparison and bounded-search helpers.

## AI Widgets

### loop_recurrence_budget

- Inputs: loop period, sample/token index, maximum loops, overthinking tolerance.
- Outputs: loop phase, required loop count, token recurrence budget, capped training-free loop budget, exit availability, overthinking boundary, and one-period-shift periodicity checks.
- Theorem ids: `AIM-T0018`, `AIM-T0019`, `AIM-T0020`, and `AIM-T0021`.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0054`, `COMMON-0059`, and `COMMON-0067`.
- Python references: `circle_math.applications.circle_ai.loop_required_steps`, `circle_math.applications.circle_ai.token_recurrence_budget`, and `circle_math.applications.circle_ai.training_free_loop_budget`.
- Guardrail: the widget is finite schedule bookkeeping only. It does not prove model quality, speed, reasoning improvement, memory improvement, or context-length improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python AI recurrence helpers.

### token_level_recurrence

- Inputs: loop period, token count, maximum budget, fixed global budget, wrong-budget shift, over-loop budget, and overthinking tolerance.
- Outputs: per-token recurrence-budget strip, selected middle-block record, coarse/fine resolution labels, active-token counts by loop step, fixed-budget control, wrong-budget control, over-loop control, nonperiodic phase-lookup control, and scalar-threshold control.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, and `AIM-T0018` as finite loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0068`, and `COMMON-0069`.
- Python references: `circle_math.applications.circle_ai.token_recurrence_budgets`, `circle_math.applications.circle_ai.active_token_counts_by_budget`, `circle_math.applications.circle_ai.recurrence_resolution_levels`, and `circle_math.applications.circle_ai.run_token_level_recurrence_benchmark`.
- Guardrail: the widget is deterministic token-level schedule bookkeeping only. It does not prove learned-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python token-level recurrence benchmark fixture.

### learned_token_recurrence

- Inputs: loop period, wrong/control period, train-token count, held-out test-token count, maximum budget, fixed global budget, wrong-budget shift, over-loop budget, and overthinking tolerance.
- Outputs: fitted phase-to-budget lookup table, wrong-period lookup table, required held-out budget sample, learned held-out budget sample, shifted-budget control sample, active-token counts by loop step, learned-router accuracy, fixed-budget accuracy, wrong-period accuracy, wrong-shift accuracy, over-loop accuracy, nonperiodic phase-lookup accuracy, and nonperiodic scalar-threshold accuracy.
- Theorem ids: `AIM-T0006`, `AIM-T0007`, `AIM-T0008`, `AIM-T0009`, and `AIM-T0018` as finite loop-budget primitives.
- Dictionary ids: `COMMON-0052`, `COMMON-0053`, `COMMON-0059`, `COMMON-0068`, and `COMMON-0069`.
- Python references: `circle_math.applications.circle_ai.fit_loop_budget_lookup`, `circle_math.applications.circle_ai.predict_loop_budget_lookup`, and `circle_math.applications.circle_ai.run_learned_token_level_recurrence_benchmark`.
- Guardrail: the widget is learned lookup-table bookkeeping for a constructed finite fixture only. It does not prove neural-router quality, recursive reasoning, perplexity improvement, throughput, memory improvement, context-length improvement, or model-quality improvement.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python learned token-level recurrence benchmark fixture.

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
- Theorem ids: `PHYS-T0001`, `PHYS-T0002`, `PHYS-T0003`, `PHYS-T0006`, `PHYS-T0007`, and `PHYS-T0039`.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, and `COMMON-0063`.
- Python references: `circle_math.physics.GaugePath`, `circle_math.physics.GaugeEdge`, `circle_math.physics.path_holonomy`, `circle_math.physics.concat_paths`, `circle_math.physics.reverse_path`, `circle_math.physics.gauge_transform_path`, and `circle_math.physics.transformed_holonomy_endpoint_prediction`.
- Guardrail: the widget is finite modular path algebra only. It does not prove continuum electromagnetism, QFT, Yang-Mills theory, Berry phase, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python finite path helpers.

### finite_gauge_loop_holonomy

- Inputs: finite phase modulus, four square-plaquette edge phases, and four vertex gauge values.
- Outputs: original normalized edge phases, transformed edge phases, original holonomy, transformed holonomy, closed-path endpoint-shift cancellation, theorem-status badges, and dictionary links.
- Theorem ids: `PHYS-T0004`, `PHYS-T0005`, `PHYS-T0012`, and `PHYS-T0045`.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, `COMMON-0062`, and `COMMON-0063`.
- Python references: `circle_math.physics.square_plaquette_path`, `circle_math.physics.gauge_transform_path`, and `circle_math.physics.path_holonomy`.
- Guardrail: the widget is finite `Z_n` bookkeeping only. It is not a proof artifact, continuum gauge theory, QFT, Yang-Mills theory, Berry phase, electromagnetism, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python finite lattice-gauge fixture.

### wilson_loop_certificate

- Inputs: finite phase modulus, three triangular-loop edge phases, and one editable sampled vertex gauge.
- Outputs: normalized triangular loop, original holonomy, transformed edge rows for three sampled gauges, transformed holonomies, sampled invariance flags, theorem-status badges, and dictionary links.
- Theorem ids: `PHYS-T0004` and `PHYS-T0005`, matching the current Python certificate payload.
- Dictionary ids: `COMMON-0060`, `COMMON-0061`, `COMMON-0062`, and `COMMON-0063`.
- Python references: `circle_math.physics.GaugePath`, `circle_math.physics.GaugeEdge`, `circle_math.physics.gauge_transform_path`, `circle_math.physics.path_holonomy`, and `circle_math.physics.wilson_loop_certificate`.
- Guardrail: the widget is a sampled finite Wilson-loop certificate only. It does not prove continuum gauge theory, electromagnetism, QFT, Berry phase, or a physics prediction.
- Validation: deterministic JavaScript-equivalent formulas are parity-checked against the Python Wilson-loop certificate helper.

## Future Placeholders

- `site/widgets/S2/sphere_grid_placeholder.js`
- `site/widgets/S3/hopf_placeholder.js`

These should be visibly marked placeholder/exploratory until implemented and linked to checked theorem status.

The placeholder widgets are included in `site/data/generated/widget_index.json` so every mounted widget is discoverable from generated site data, even when it is scaffold-only.

## Validation Strategy

Checkers:

- `scripts/site/check_site_widget_contracts.py` verifies that every `data-widget` page mount exists in `widget_index.json`, imports the matching widget script, and points to a JavaScript file that calls `mountWidgets("<widget_id>", ...)`.
- `scripts/site/check_site_accessibility_contract.py` verifies shared widget accessibility contracts: named widget regions, labelled number inputs, live output regions, SVG title/description metadata, visible focus styling, and scaffold-only placeholder guardrails.
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
